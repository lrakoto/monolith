"""Integrate the stronger pond with a layered, planted right shoreline grove."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-holistic-shore-water-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-shore-grove-natural-cloud-v1.blend'))
scene = bpy.context.scene
pond = bpy.data.objects['pond']
shelf = bpy.data.objects['submerged mottled shallows test']
crowns = [bpy.data.objects[name] for name in (
    'fuller right shoreline crown', 'shore grove left shoulder', 'shore grove right shoulder')]


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


changed = {pond.name, shelf.name, *(obj.name for obj in crowns)}
before = {obj.name: descriptor(obj) for obj in scene.objects if obj.name not in changed}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}

# Repeat the reviewed material settings locally. Importing the materials from
# the other blend leaves library paths in blend_paths despite link=False.
growth = shelf.material_slots[0].material.copy()
growth.name = 'submerged growth broader far bank integrated'
emission = [node for node in growth.node_tree.nodes if node.type == 'EMISSION']
assert len(emission) == 1 and abs(emission[0].inputs['Strength'].default_value - .75) < .00001
emission[0].inputs['Strength'].default_value = 1.2
mask = [node for node in growth.node_tree.nodes if node.type == 'VALTORGB'
        and abs(node.color_ramp.elements[0].position - .43) < .00001
        and abs(node.color_ramp.elements[1].position - .67) < .00001]
assert len(mask) == 1, mask
mask[0].color_ramp.elements[0].position = .32
mask[0].color_ramp.elements[1].position = .58
shelf.material_slots[0].link = 'OBJECT'
shelf.material_slots[0].material = growth

water = pond.material_slots[0].material.copy()
water.name = 'pond deep foreground integrated'
nodes = water.node_tree.nodes
links = water.node_tree.links
output_node = next(node for node in nodes if node.type == 'OUTPUT_MATERIAL')
surface = output_node.inputs['Surface'].links[0].from_socket
clear_mix = [node for node in nodes if node.type == 'MATH' and node.operation == 'MULTIPLY'
             and any(link.to_node == node and link.to_socket == node.inputs[1] for link in links)]
assert len(clear_mix) == 1, clear_mix
floor = clear_mix[0].inputs[1].links[0].from_node
amplitude = floor.inputs[0].links[0].from_node
assert floor.operation == 'ADD' and abs(floor.inputs[1].default_value - .30) < .00001
assert amplitude.operation == 'MULTIPLY' and abs(amplitude.inputs[1].default_value - .42) < .00001
floor.inputs[1].default_value = .22
amplitude.inputs[1].default_value = .66
geo = nodes.new('ShaderNodeNewGeometry')
xyz = nodes.new('ShaderNodeSeparateXYZ')
links.new(geo.outputs['Position'], xyz.inputs['Vector'])
near = nodes.new('ShaderNodeMapRange')
near.clamp = True
near.interpolation_type = 'SMOOTHSTEP'
near.inputs['From Min'].default_value = -610
near.inputs['From Max'].default_value = -380
links.new(xyz.outputs['Y'], near.inputs['Value'])
invert = nodes.new('ShaderNodeMath')
invert.operation = 'SUBTRACT'
invert.inputs[0].default_value = 1
links.new(near.outputs['Result'], invert.inputs[1])
strength = nodes.new('ShaderNodeMath')
strength.operation = 'MULTIPLY'
strength.inputs[1].default_value = .42
links.new(invert.outputs[0], strength.inputs[0])
dark = nodes.new('ShaderNodeEmission')
dark.inputs['Color'].default_value = (.008, .020, .013, 1)
dark.inputs['Strength'].default_value = 1
mix = nodes.new('ShaderNodeMixShader')
links.new(strength.outputs[0], mix.inputs[0])
links.new(surface, mix.inputs[1])
links.new(dark.outputs[0], mix.inputs[2])
links.new(mix.outputs[0], output_node.inputs['Surface'])
pond.material_slots[0].link = 'OBJECT'
pond.material_slots[0].material = water

# The reference's exposed leaves are a little warmer without being brighter
# overall; keep the darker lower foliage and touch only the three upper crowns.
warm = {}
for crown in crowns:
    for slot in crown.material_slots:
        source_material = slot.material
        if not source_material or not source_material.name.startswith('soft leaf surface '):
            continue
        if source_material.name not in warm:
            material = source_material.copy()
            material.name = 'shore grove warm ' + source_material.name
            shader = next(node for node in material.node_tree.nodes if node.type == 'BSDF_PRINCIPLED')
            color = shader.inputs['Base Color'].default_value
            shader.inputs['Base Color'].default_value = (color[0] * 1.22, color[1], color[2] * 1.18, 1)
            warm[source_material.name] = material
        slot.link = 'OBJECT'
        slot.material = warm[source_material.name]
assert len(warm) == 4

template = bpy.data.objects['shoreline foliage 020']
assert len(template.data.vertices) > 60000
plantings = (
    (169, 36, 18, 1.45, 1.48, 1.28),
    (198, 13, 17, 1.65, 1.35, 1.48),
    (224, 45, 22, 1.20, 1.45, 1.36),
    (246, -12, 13, 1.55, 1.58, 1.20),
    (269, 58, 20, 1.65, 1.32, 1.62),
    (293, 3, 16, 1.35, 1.55, 1.38),
    (318, 87, 26, 1.55, 1.38, 1.36),
    (343, 8, 15, 1.62, 1.54, 1.53),
    (369, 50, 19, 1.28, 1.43, 1.35),
    (391, 98, 22, 1.52, 1.28, 1.42),
    (288, 104, 18, 1.32, 1.32, 1.48),
    (228, 91, 23, 1.42, 1.46, 1.36),
)
for index, (x, y, z, sx, sy, sz) in enumerate(plantings):
    obj = template.copy()
    obj.name = f'shore grove understory {index:02d}'
    scene.collection.objects.link(obj)
    obj.location = (x, y, z)
    obj.scale = (template.scale.x * sx, template.scale.y * sy, template.scale.z * sz)
    obj.rotation_euler.z = .31 * index
    if index in (1, 4, 7, 10):
        for slot in obj.material_slots:
            material = slot.material
            if material and material.name.startswith('leaf tone '):
                slot.link = 'OBJECT'
                slot.material = bpy.data.materials['sunlit ' + material.name]

assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, 'UNDERSTORY', len(plantings), flush=True)
