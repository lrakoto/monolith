"""Soften luminous pond bands and test sparse dark floating growth near camera."""
import math
import random
from pathlib import Path

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-water-calm-foreground-cloud-v1.blend'
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

# The previous remap turned pond bands into rays. Keep those coordinates and
# reduce contrast in the visibility and color ramps instead.
water = pond.material_slots[0].material.copy()
water.name = 'pond calmer clarity contrast'
ramps = [node for node in water.node_tree.nodes if node.type == 'VALTORGB'
         and abs(node.color_ramp.elements[0].position - .42) < .00001
         and abs(node.color_ramp.elements[1].position - .63) < .00001]
assert len(ramps) == 1, ramps
ramps[0].color_ramp.elements[0].color = (.25, .25, .25, 1)
ramps[0].color_ramp.elements[1].color = (.75, .75, .75, 1)
pond.material_slots[0].link = 'OBJECT'
pond.material_slots[0].material = water
growth = shelf.material_slots[0].material.copy()
growth.name = 'submerged growth calmer contrast'
ramps = [node for node in growth.node_tree.nodes if node.type == 'VALTORGB']
assert len(ramps) == 2, ramps
color = next(node for node in ramps if abs(node.color_ramp.elements[0].position - .25) < .00001)
mask = next(node for node in ramps if abs(node.color_ramp.elements[0].position - .32) < .00001)
color.color_ramp.elements[0].color = (.044, .108, .043, 1)
color.color_ramp.elements[1].color = (.076, .180, .073, 1)
mask.color_ramp.elements[0].color = (.22, .22, .22, 1)
mask.color_ramp.elements[1].color = (.80, .80, .80, 1)
shelf.material_slots[0].link = 'OBJECT'
shelf.material_slots[0].material = growth

material = bpy.data.materials.new('dark floating growth with broken edges')
material.use_nodes = True
nodes = material.node_tree.nodes
nodes.clear()
links = material.node_tree.links
out = nodes.new('ShaderNodeOutputMaterial')
coord = nodes.new('ShaderNodeTexCoord')
xyz = nodes.new('ShaderNodeSeparateXYZ')
links.new(coord.outputs['Generated'], xyz.inputs[0])
xy = nodes.new('ShaderNodeCombineXYZ')
links.new(xyz.outputs['X'], xy.inputs['X'])
links.new(xyz.outputs['Y'], xy.inputs['Y'])
radius = nodes.new('ShaderNodeVectorMath')
radius.operation = 'DISTANCE'
radius.inputs[1].default_value = (.5, .5, 0)
links.new(xy.outputs[0], radius.inputs[0])
edge = nodes.new('ShaderNodeMapRange')
edge.clamp = True
edge.interpolation_type = 'SMOOTHSTEP'
edge.inputs['From Min'].default_value = .18
edge.inputs['From Max'].default_value = .52
edge.inputs['To Min'].default_value = 1
edge.inputs['To Max'].default_value = 0
links.new(radius.outputs['Value'], edge.inputs['Value'])
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 9
noise.inputs['Detail'].default_value = 3
links.new(coord.outputs['Generated'], noise.inputs['Vector'])
mask = nodes.new('ShaderNodeValToRGB')
mask.color_ramp.elements[0].position = .27
mask.color_ramp.elements[1].position = .57
links.new(noise.outputs['Fac'], mask.inputs['Fac'])
coverage = nodes.new('ShaderNodeMath')
coverage.operation = 'MULTIPLY'
links.new(edge.outputs['Result'], coverage.inputs[0])
links.new(mask.outputs['Color'], coverage.inputs[1])
clear = nodes.new('ShaderNodeBsdfTransparent')
dark = nodes.new('ShaderNodeBsdfPrincipled')
dark.inputs['Base Color'].default_value = (.007, .018, .012, 1)
dark.inputs['Roughness'].default_value = .52
dark.inputs['Specular IOR Level'].default_value = .22
mix = nodes.new('ShaderNodeMixShader')
links.new(coverage.outputs[0], mix.inputs[0])
links.new(clear.outputs[0], mix.inputs[1])
links.new(dark.outputs[0], mix.inputs[2])
links.new(mix.outputs[0], out.inputs['Surface'])

# Buried silhouettes disappeared at the grazing angle. These sparse algae
# mats sit at the waterline and occupy only the nearest few image rows.
depsgraph = bpy.context.evaluated_depsgraph_get()
projection = scene.camera.calc_matrix_camera(depsgraph,
    x=scene.render.resolution_x, y=scene.render.resolution_y,
    scale_x=scene.render.pixel_aspect_x, scale_y=scene.render.pixel_aspect_y)
inverse = projection.inverted()
origin = scene.camera.matrix_world.translation


def water_point(x, y):
    near = inverse @ Vector((x * 2 - 1, y * 2 - 1, -1, 1))
    near = Vector(near[:3]) / near.w
    ray = scene.camera.matrix_world.to_3x3() @ near
    assert abs(ray.z) > .00001
    point = origin + ray * ((.12 - origin.z) / ray.z)
    projected = world_to_camera_view(scene, scene.camera, point)
    assert abs(projected.x - x) < .00001 and abs(projected.y - y) < .00001
    return point


rng = random.Random(3050930)
patches = ((.28, .013, .075, .010), (.43, .025, .040, .012),
           (.62, .019, .060, .008), (.76, .009, .082, .014),
           (.88, .028, .035, .010))
for index, (x, y, rx, ry) in enumerate(patches):
    count = 48
    phase = rng.uniform(0, math.tau)
    vertices = [tuple(water_point(x, y))]
    for k in range(count):
        angle = math.tau * k / count
        r = 1 + .20 * math.sin(3 * angle + phase) + .12 * math.cos(7 * angle - phase)
        vertices.append(tuple(water_point(x + rx * r * math.cos(angle), y + ry * r * math.sin(angle))))
    mesh = bpy.data.meshes.new(f'near pond floating growth {index:02d} mesh')
    mesh.from_pydata(vertices, [], [(0, k + 1, (k + 1) % count + 1) for k in range(count)])
    mesh.update()
    obj = bpy.data.objects.new(f'near pond floating growth {index:02d}', mesh)
    scene.collection.objects.link(obj)
    mesh.materials.append(material)

assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, 'FOREGROUND PATCHES', len(patches), flush=True)
