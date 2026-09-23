"""Test broken clear windows above the existing brighter submerged terrain."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-water-clear-patches-cloud-v1.blend'
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
water.name = 'pond broken clarity over lit shallows test'
nodes = water.node_tree.nodes
links = water.node_tree.links
shader = next(node for node in nodes if node.type == 'BSDF_PRINCIPLED')
output_node = next(node for node in nodes if node.type == 'OUTPUT_MATERIAL')
assert abs(shader.inputs['Transmission Weight'].default_value - .22) < .00001
assert abs(shader.inputs['Roughness'].default_value - .30) < .00001
shader.inputs['Transmission Weight'].default_value = .58
geometry = nodes.new('ShaderNodeNewGeometry')
stretch = nodes.new('ShaderNodeVectorMath')
stretch.operation = 'MULTIPLY'
stretch.inputs[1].default_value = (.018, .011, 1)
links.new(geometry.outputs['Position'], stretch.inputs[0])
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 1
noise.inputs['Detail'].default_value = 2
links.new(stretch.outputs[0], noise.inputs['Vector'])
ramp = nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = .42
ramp.color_ramp.elements[1].position = .63
links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
strength = nodes.new('ShaderNodeMath')
strength.operation = 'MULTIPLY'
strength.inputs[1].default_value = .28
links.new(ramp.outputs['Color'], strength.inputs[0])
clear = nodes.new('ShaderNodeBsdfTransparent')
mix_surface = nodes.new('ShaderNodeMixShader')
links.new(strength.outputs[0], mix_surface.inputs[0])
links.new(shader.outputs['BSDF'], mix_surface.inputs[1])
links.new(clear.outputs['BSDF'], mix_surface.inputs[2])
links.new(mix_surface.outputs[0], output_node.inputs['Surface'])
pond.material_slots[0].link = 'OBJECT'
pond.material_slots[0].material = water

earth = bank.material_slots[0].material.copy()
earth.name = 'forest earth with brighter submerged bed test'
nodes = earth.node_tree.nodes
links = earth.node_tree.links
earth_shader = next(node for node in nodes if node.type == 'BSDF_PRINCIPLED')
old_link = earth_shader.inputs['Base Color'].links[0]
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
earth_geometry = nodes.new('ShaderNodeNewGeometry')
z = nodes.new('ShaderNodeSeparateXYZ')
links.new(earth_geometry.outputs['Position'], z.inputs[0])
submerged = nodes.new('ShaderNodeMath')
submerged.operation = 'LESS_THAN'
submerged.inputs[1].default_value = -.25
links.new(z.outputs['Z'], submerged.inputs[0])
mix_bed = nodes.new('ShaderNodeMixRGB')
mix_bed.blend_type = 'MIX'
links.new(submerged.outputs[0], mix_bed.inputs[0])
links.new(original_color, mix_bed.inputs[1])
links.new(underwater_ramp.outputs['Color'], mix_bed.inputs[2])
links.new(mix_bed.outputs['Color'], earth_shader.inputs['Base Color'])
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
