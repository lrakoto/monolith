"""Replace the continuous bright underlayer with separate submerged shoals."""
import math
import random
import sys
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
assert args in ([], ['--layered']), args
layered = args == ['--layered']
output = root / ('cathedral-water-layered-shoals-cloud-v1.blend' if layered
                 else 'cathedral-water-shoals-cloud-v1.blend')
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-water-shore-clarity-cloud-v1.blend'))
scene = bpy.context.scene
old_shelf = bpy.data.objects['submerged mottled shallows test']


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


before = {obj.name: descriptor(obj) for obj in scene.objects if layered or obj.name != old_shelf.name}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
if not layered:
    bpy.data.objects.remove(old_shelf, do_unlink=True)


def shoal_material(name, dark, light):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    links = material.node_tree.links
    out = nodes.new('ShaderNodeOutputMaterial')
    coords = nodes.new('ShaderNodeTexCoord')
    radial = nodes.new('ShaderNodeVectorMath')
    radial.operation = 'DISTANCE'
    radial.inputs[1].default_value = (.5, .5, 0)
    links.new(coords.outputs['Generated'], radial.inputs[0])
    edge = nodes.new('ShaderNodeMapRange')
    edge.clamp = True
    edge.interpolation_type = 'SMOOTHSTEP'
    edge.inputs['From Min'].default_value = .30
    edge.inputs['From Max'].default_value = .55
    edge.inputs['To Min'].default_value = 1
    edge.inputs['To Max'].default_value = 0
    links.new(radial.outputs['Value'], edge.inputs['Value'])
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 5
    noise.inputs['Detail'].default_value = 3
    links.new(coords.outputs['Generated'], noise.inputs['Vector'])
    breakup = nodes.new('ShaderNodeValToRGB')
    breakup.color_ramp.elements[0].position = .36
    breakup.color_ramp.elements[1].position = .72
    links.new(noise.outputs['Fac'], breakup.inputs['Fac'])
    coverage = nodes.new('ShaderNodeMath')
    coverage.operation = 'MULTIPLY'
    links.new(edge.outputs['Result'], coverage.inputs[0])
    links.new(breakup.outputs['Color'], coverage.inputs[1])
    color = nodes.new('ShaderNodeValToRGB')
    color.color_ramp.elements[0].position = .26
    color.color_ramp.elements[0].color = (*dark, 1)
    color.color_ramp.elements[1].position = .75
    color.color_ramp.elements[1].color = (*light, 1)
    links.new(noise.outputs['Fac'], color.inputs['Fac'])
    transparent = nodes.new('ShaderNodeBsdfTransparent')
    growth = nodes.new('ShaderNodeEmission')
    growth.inputs['Strength'].default_value = 1.55 if layered else .85
    links.new(color.outputs['Color'], growth.inputs['Color'])
    mix = nodes.new('ShaderNodeMixShader')
    links.new(coverage.outputs[0], mix.inputs[0])
    links.new(transparent.outputs['BSDF'], mix.inputs[1])
    links.new(growth.outputs['Emission'], mix.inputs[2])
    links.new(mix.outputs[0], out.inputs['Surface'])
    return material


materials = [
    shoal_material('submerged olive growth', (.020, .058, .020), (.074, .18, .058)),
    shoal_material('submerged moss growth', (.018, .051, .025), (.065, .16, .067)),
    shoal_material('submerged sage growth', (.026, .061, .027), (.086, .18, .073)),
]

rng = random.Random(3050917)
placements = []
count = 46 if layered else 31
for i in range(count):
    # The shoreward half has growth; the nearest water keeps dark reflective gaps.
    y = rng.uniform(-470, -150)
    x_span = 290 if y < -350 else 360
    x = rng.uniform(-x_span, x_span)
    rx = rng.uniform(28, 75) if layered else rng.uniform(18, 60)
    ry = rng.uniform(18, 46) if layered else rng.uniform(12, 39)
    depth = rng.uniform(.38, 1.2) if layered else rng.uniform(.42, 1.45)
    placements.append((x, y, rx, ry, depth))

for i, (x, y, rx, ry, depth) in enumerate(placements):
    phase = rng.uniform(0, math.tau)
    ring_count = 22
    vertices = [(0, 0, 0)]
    for j in range(ring_count):
        theta = math.tau * j / ring_count
        radius = 1 + .17 * math.sin(3 * theta + phase) + .09 * math.cos(7 * theta - phase)
        radius += rng.uniform(-.06, .06)
        vertices.append((rx * radius * math.cos(theta),
                         ry * radius * math.sin(theta),
                         -.13 - .07 * math.sin(theta + phase)))
    faces = [(0, j + 1, (j + 1) % ring_count + 1) for j in range(ring_count)]
    mesh = bpy.data.meshes.new(f'water shoal {i:02d} mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(f'water shoal {i:02d}', mesh)
    scene.collection.objects.link(obj)
    obj.location = (x, y, -depth)
    mesh.materials.append(materials[i % len(materials)])

assert len(placements) == count
assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, flush=True)
