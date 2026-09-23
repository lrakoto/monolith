"""Lighten only the submerged terrain so clear water has something to reveal."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-water-shallows-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-overgrown-right-canopy-contour-cloud-v1.blend'))
scene = bpy.context.scene
pond = bpy.data.objects['pond']
bank = bpy.data.objects['simple forest banks']


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


before = {obj.name: descriptor(obj) for obj in scene.objects if obj.name not in (pond.name, bank.name)}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}

water = pond.material_slots[0].material.copy()
water.name = 'pond clear water over lit shallows test'
water_shader = next(node for node in water.node_tree.nodes if node.type == 'BSDF_PRINCIPLED')
assert abs(water_shader.inputs['Transmission Weight'].default_value - .22) < .00001
assert abs(water_shader.inputs['Roughness'].default_value - .30) < .00001
water_shader.inputs['Transmission Weight'].default_value = .58
pond.material_slots[0].link = 'OBJECT'
pond.material_slots[0].material = water

earth = bank.material_slots[0].material.copy()
earth.name = 'forest earth with brighter submerged bed test'
nodes = earth.node_tree.nodes
links = earth.node_tree.links
shader = next(node for node in nodes if node.type == 'BSDF_PRINCIPLED')
old_link = shader.inputs['Base Color'].links[0]
original_color = old_link.from_socket
original_ramp = old_link.from_node
assert original_ramp.type == 'VALTORGB'
underwater_ramp = nodes.new('ShaderNodeValToRGB')
underwater_ramp.label = 'mottled shallow bed'
underwater_ramp.color_ramp.elements[0].position = .18
underwater_ramp.color_ramp.elements[0].color = (.03, .072, .025, 1)
underwater_ramp.color_ramp.elements[1].position = .8
underwater_ramp.color_ramp.elements[1].color = (.105, .18, .067, 1)
links.new(original_ramp.inputs['Fac'].links[0].from_socket, underwater_ramp.inputs['Fac'])
geometry = nodes.new('ShaderNodeNewGeometry')
z = nodes.new('ShaderNodeSeparateXYZ')
links.new(geometry.outputs['Position'], z.inputs[0])
submerged = nodes.new('ShaderNodeMath')
submerged.operation = 'LESS_THAN'
submerged.inputs[1].default_value = -.25
links.new(z.outputs['Z'], submerged.inputs[0])
mix = nodes.new('ShaderNodeMixRGB')
mix.blend_type = 'MIX'
links.new(submerged.outputs[0], mix.inputs[0])
links.new(original_color, mix.inputs[1])
links.new(underwater_ramp.outputs['Color'], mix.inputs[2])
links.new(mix.outputs['Color'], shader.inputs['Base Color'])
bank.material_slots[0].link = 'OBJECT'
bank.material_slots[0].material = earth

assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, flush=True)
