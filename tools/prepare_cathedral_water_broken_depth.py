"""Rejected pond mapping diagnostic; retain the broken shoreline baseline."""
import math
import random
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-water-broken-depth-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-shore-grove-broken-cloud-v1.blend'))
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


def remap(material, old_scale, new_scale):
    matches = [node for node in material.node_tree.nodes
               if node.type == 'VECT_MATH' and node.operation == 'MULTIPLY'
               and all(abs(a - b) < .00001 for a, b in zip(node.inputs[1].default_value, old_scale))]
    assert len(matches) == 1, (material.name, matches)
    matches[0].inputs[1].default_value = new_scale


# This tested longer world y footprints to offset the grazing view. The
# cloud result instead formed conspicuous rays; keep this recipe as a diagnostic.
water = pond.material_slots[0].material.copy()
water.name = 'pond broken depth windows'
remap(water, (.018, .011, 1), (.045, .0038, 1))
pond.material_slots[0].link = 'OBJECT'
pond.material_slots[0].material = water
growth = shelf.material_slots[0].material.copy()
growth.name = 'submerged growth broken depth'
remap(growth, (.012, .008, 1), (.040, .0035, 1))
shelf.material_slots[0].link = 'OBJECT'
shelf.material_slots[0].material = growth

material = bpy.data.materials.new('irregular submerged dark growth')
material.use_nodes = True
nodes = material.node_tree.nodes
nodes.clear()
links = material.node_tree.links
out = nodes.new('ShaderNodeOutputMaterial')
coord = nodes.new('ShaderNodeTexCoord')
radial = nodes.new('ShaderNodeVectorMath')
radial.operation = 'DISTANCE'
radial.inputs[1].default_value = (.5, .5, 0)
links.new(coord.outputs['Generated'], radial.inputs[0])
edge = nodes.new('ShaderNodeMapRange')
edge.clamp = True
edge.interpolation_type = 'SMOOTHSTEP'
edge.inputs['From Min'].default_value = .22
edge.inputs['From Max'].default_value = .58
edge.inputs['To Min'].default_value = .80
edge.inputs['To Max'].default_value = 0
links.new(radial.outputs['Value'], edge.inputs['Value'])
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 5
noise.inputs['Detail'].default_value = 2
links.new(coord.outputs['Generated'], noise.inputs['Vector'])
mask = nodes.new('ShaderNodeValToRGB')
mask.color_ramp.elements[0].position = .24
mask.color_ramp.elements[1].position = .64
links.new(noise.outputs['Fac'], mask.inputs['Fac'])
coverage = nodes.new('ShaderNodeMath')
coverage.operation = 'MULTIPLY'
links.new(edge.outputs['Result'], coverage.inputs[0])
links.new(mask.outputs['Color'], coverage.inputs[1])
clear = nodes.new('ShaderNodeBsdfTransparent')
dark = nodes.new('ShaderNodeEmission')
dark.inputs['Color'].default_value = (.012, .026, .016, 1)
dark.inputs['Strength'].default_value = 1
mix = nodes.new('ShaderNodeMixShader')
links.new(coverage.outputs[0], mix.inputs[0])
links.new(clear.outputs[0], mix.inputs[1])
links.new(dark.outputs[0], mix.inputs[2])
links.new(mix.outputs[0], out.inputs['Surface'])

# These islands interrupt the bright underlayer through the same clear
# windows. Their edges feather underwater; the surface stays reflective.
rng = random.Random(3050929)
placements = ((-220, -325, 55, 110), (125, -300, 38, 88),
              (-20, -450, 44, 130), (260, -505, 60, 90),
              (-270, -565, 75, 110), (85, -605, 68, 140))
for index, (x, y, rx, ry) in enumerate(placements):
    phase = rng.uniform(0, math.tau)
    vertices = [(0, 0, 0)]
    count = 32
    for k in range(count):
        angle = math.tau * k / count
        radius = 1 + .22 * math.sin(3 * angle + phase) + .13 * math.cos(7 * angle - phase)
        vertices.append((rx * radius * math.cos(angle), ry * radius * math.sin(angle), 0))
    mesh = bpy.data.meshes.new(f'submerged dark island {index:02d} mesh')
    mesh.from_pydata(vertices, [], [(0, k + 1, (k + 1) % count + 1) for k in range(count)])
    mesh.update()
    obj = bpy.data.objects.new(f'submerged dark island {index:02d}', mesh)
    scene.collection.objects.link(obj)
    obj.location = (x, y, -.28 - .01 * index)
    obj.rotation_euler.z = rng.uniform(-.22, .22)
    mesh.materials.append(material)

assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, 'DARK ISLANDS', len(placements), flush=True)
