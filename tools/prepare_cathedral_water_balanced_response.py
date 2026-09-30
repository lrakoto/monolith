"""Balance pond reflections with graded roughness and shore-only growth light."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-water-balanced-response-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-water-fine-reflection-cloud-v1.blend'))
scene = bpy.context.scene
pond = bpy.data.objects['pond']
shelf = bpy.data.objects['submerged mottled shallows test']


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


before = {obj.name: descriptor(obj) for obj in scene.objects if obj not in (pond, shelf)}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}


def y_gradient(material, start, end, near_value, far_value):
    nodes, links = material.node_tree.nodes, material.node_tree.links
    geometry = nodes.new('ShaderNodeNewGeometry')
    xyz = nodes.new('ShaderNodeSeparateXYZ')
    links.new(geometry.outputs['Position'], xyz.inputs['Vector'])
    gradient = nodes.new('ShaderNodeMapRange')
    gradient.clamp = True
    gradient.interpolation_type = 'SMOOTHSTEP'
    gradient.inputs['From Min'].default_value = start
    gradient.inputs['From Max'].default_value = end
    gradient.inputs['To Min'].default_value = near_value
    gradient.inputs['To Max'].default_value = far_value
    links.new(xyz.outputs['Y'], gradient.inputs['Value'])
    return gradient.outputs['Result']


# constant low roughness produced two conspicuous warm reflection columns.
# let the near surface soften them while the far water keeps a clearer response.
water = pond.material_slots[0].material.copy()
water.name = 'pond balanced roughness by distance'
shaders = [node for node in water.node_tree.nodes if node.type == 'BSDF_PRINCIPLED']
assert len(shaders) == 1
shader = shaders[0]
assert not shader.inputs['Roughness'].is_linked
assert abs(shader.inputs['Roughness'].default_value - .16) < .00001
roughness = y_gradient(water, -620, -160, .26, .17)
water.node_tree.links.new(roughness, shader.inputs['Roughness'])
pond.material_slots[0].link = 'OBJECT'
pond.material_slots[0].material = water

# clearer reflection made the far green shallows too dim. Restore a small
# amount there without changing the shelf light in the nearest water.
growth = shelf.material_slots[0].material.copy()
growth.name = 'submerged growth gently lifted at shore'
emissions = [node for node in growth.node_tree.nodes if node.type == 'EMISSION']
assert len(emissions) == 1
emission = emissions[0]
assert not emission.inputs['Strength'].is_linked
assert abs(emission.inputs['Strength'].default_value - 1.2) < .00001
brightness = y_gradient(growth, -430, -180, 1.2, 1.5)
growth.node_tree.links.new(brightness, emission.inputs['Strength'])
shelf.material_slots[0].link = 'OBJECT'
shelf.material_slots[0].material = growth

assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, 'ROUGHNESS .26 NEAR .17 FAR; GROWTH 1.2 NEAR 1.5 FAR', flush=True)
