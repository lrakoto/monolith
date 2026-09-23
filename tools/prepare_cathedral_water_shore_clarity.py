"""Keep clear shallows shoreward while the near pond stays reflective and dark."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-water-shore-clarity-cloud-v1.blend'
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
strength.inputs[1].default_value = .42
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

# At this grazing view a bed nine units below the pond stays almost black even
# when it is lit and the water transmits more light. This thin layer represents
# intermittent near-surface growth; dark gaps still show the deeper bed.
mesh = bpy.data.meshes.new('submerged mottled shelf mesh')
mesh.from_pydata([(-1050, -1050, 0), (1050, -1050, 0), (1050, 1050, 0), (-1050, 1050, 0)],
                 [], [(0, 1, 2, 3)])
mesh.update()
shelf = bpy.data.objects.new('submerged mottled shallows test', mesh)
scene.collection.objects.link(shelf)
shelf.location = (0, -390, -.7)
shelf_material = bpy.data.materials.new('submerged mottled growth test')
shelf_material.use_nodes = True
mesh.materials.append(shelf_material)
nodes = shelf_material.node_tree.nodes
nodes.clear()
links = shelf_material.node_tree.links
out = nodes.new('ShaderNodeOutputMaterial')
geo = nodes.new('ShaderNodeNewGeometry')
stretch = nodes.new('ShaderNodeVectorMath')
stretch.operation = 'MULTIPLY'
stretch.inputs[1].default_value = (.012, .008, 1)
links.new(geo.outputs['Position'], stretch.inputs[0])
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 1
noise.inputs['Detail'].default_value = 3
links.new(stretch.outputs[0], noise.inputs['Vector'])
color = nodes.new('ShaderNodeValToRGB')
color.color_ramp.elements[0].position = .25
color.color_ramp.elements[0].color = (.025, .064, .027, 1)
color.color_ramp.elements[1].position = .78
color.color_ramp.elements[1].color = (.095, .24, .10, 1)
links.new(noise.outputs['Fac'], color.inputs['Fac'])
mask = nodes.new('ShaderNodeValToRGB')
mask.color_ramp.elements[0].position = .43
mask.color_ramp.elements[1].position = .67
links.new(noise.outputs['Fac'], mask.inputs['Fac'])
clear_bed = nodes.new('ShaderNodeBsdfTransparent')
growth = nodes.new('ShaderNodeEmission')
growth.inputs['Strength'].default_value = .75
links.new(color.outputs['Color'], growth.inputs['Color'])
mix_shelf = nodes.new('ShaderNodeMixShader')
coord = nodes.new('ShaderNodeSeparateXYZ')
links.new(geo.outputs['Position'], coord.inputs[0])
distance = nodes.new('ShaderNodeMapRange')
distance.clamp = True
distance.interpolation_type = 'SMOOTHSTEP'
distance.inputs['From Min'].default_value = -625
distance.inputs['From Max'].default_value = -180
links.new(coord.outputs['Y'], distance.inputs['Value'])
visible_mottle = nodes.new('ShaderNodeMath')
visible_mottle.operation = 'MULTIPLY'
links.new(mask.outputs['Color'], visible_mottle.inputs[0])
links.new(distance.outputs['Result'], visible_mottle.inputs[1])
links.new(visible_mottle.outputs[0], mix_shelf.inputs[0])
links.new(clear_bed.outputs['BSDF'], mix_shelf.inputs[1])
links.new(growth.outputs['Emission'], mix_shelf.inputs[2])
links.new(mix_shelf.outputs[0], out.inputs['Surface'])

assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, flush=True)
