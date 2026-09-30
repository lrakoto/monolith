"""Test the reference's bright far shallows and dark near pond in one scene."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-water-value-split-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-water-graded-clarity-cloud-v1.blend'))
scene = bpy.context.scene
pond = bpy.data.objects['pond']
shelf = bpy.data.objects['submerged mottled shallows test']


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


before = {obj.name: descriptor(obj) for obj in scene.objects if obj.name not in (pond.name, shelf.name)}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}

# The far water is about eighteen green levels below the matched reference crop.
# Raise the shallow growth beneath it, while the already dark gaps stay transparent.
growth = shelf.material_slots[0].material.copy()
growth.name = 'submerged growth brighter far bank study'
emission = [node for node in growth.node_tree.nodes if node.type == 'EMISSION']
assert len(emission) == 1 and abs(emission[0].inputs['Strength'].default_value - .75) < .00001
emission[0].inputs['Strength'].default_value = 1.2
shelf.material_slots[0].link = 'OBJECT'
shelf.material_slots[0].material = growth

water = pond.material_slots[0].material.copy()
water.name = 'pond brighter shore darker foreground study'
nodes = water.node_tree.nodes
links = water.node_tree.links
output_node = next(node for node in nodes if node.type == 'OUTPUT_MATERIAL')
surface_link = output_node.inputs['Surface'].links[0]
surface = surface_link.from_socket
clear_mix = [node for node in nodes if node.type == 'MATH' and node.operation == 'MULTIPLY'
             and any(link.to_node == node and link.to_socket == node.inputs[1] for link in links)]
assert len(clear_mix) == 1, clear_mix
floor = clear_mix[0].inputs[1].links[0].from_node
assert floor.operation == 'ADD' and abs(floor.inputs[1].default_value - .30) < .00001
amplitude = floor.inputs[0].links[0].from_node
assert amplitude.operation == 'MULTIPLY' and abs(amplitude.inputs[1].default_value - .42) < .00001
floor.inputs[1].default_value = .22
amplitude.inputs[1].default_value = .66

# Fresnel reflection makes the closest water too pale even with the buried layer
# masked away. Let a broken, low-strength dark surface appear only below y=-390.
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
strength.inputs[1].default_value = .24
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

assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, flush=True)
