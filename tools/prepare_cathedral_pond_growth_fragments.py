"""Break foreground pond mats into scattered fragments and low fine tufts."""
import math
import random
from pathlib import Path

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-pond-growth-fragments-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-water-calm-foreground-cloud-v1.blend'))
scene = bpy.context.scene


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


before = {obj.name: descriptor(obj) for obj in scene.objects}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
hidden = {'near pond floating growth 00', 'near pond floating growth 02', 'near pond floating growth 03'}
for name in hidden:
    assert name in before and not bpy.data.objects[name].hide_render
    bpy.data.objects[name].hide_render = True

depsgraph = bpy.context.evaluated_depsgraph_get()
projection = scene.camera.calc_matrix_camera(depsgraph,
    x=scene.render.resolution_x, y=scene.render.resolution_y,
    scale_x=scene.render.pixel_aspect_x, scale_y=scene.render.pixel_aspect_y)
inverse = projection.inverted()
origin = scene.camera.matrix_world.translation
right = scene.camera.matrix_world.to_3x3() @ Vector((1, 0, 0))


def water_point(x, y):
    near = inverse @ Vector((x * 2 - 1, y * 2 - 1, -1, 1))
    near = Vector(near[:3]) / near.w
    ray = scene.camera.matrix_world.to_3x3() @ near
    point = origin + ray * ((.13 - origin.z) / ray.z)
    projected = world_to_camera_view(scene, scene.camera, point)
    assert abs(projected.x - x) < .00001 and abs(projected.y - y) < .00001
    return point


# The five separated mats read like flat islands. Gather smaller fragments
# unevenly toward the nearest frame edges, leaving the central water open.
rng = random.Random(3050931)
growth = bpy.data.materials['dark floating growth with broken edges']
clusters = ((.285, .009, .10, 7), (.72, .004, .14, 9))
for group, (cx, cy, spread, count) in enumerate(clusters):
    for index in range(count):
        x = cx + rng.uniform(-spread, spread)
        y = max(-.002, cy + rng.uniform(-.008, .009))
        rx = rng.uniform(.012, .037)
        ry = rng.uniform(.004, .009)
        phase = rng.uniform(0, math.tau)
        vertices = [tuple(water_point(x, y))]
        ring = 32
        for k in range(ring):
            angle = math.tau * k / ring
            radius = 1 + .23 * math.sin(3 * angle + phase) + .16 * math.cos(7 * angle - phase)
            vertices.append(tuple(water_point(x + rx * radius * math.cos(angle), y + ry * radius * math.sin(angle))))
        mesh = bpy.data.meshes.new(f'pond growth fragment {group}-{index:02d} mesh')
        mesh.from_pydata(vertices, [], [(0, k + 1, (k + 1) % ring + 1) for k in range(ring)])
        mesh.update()
        obj = bpy.data.objects.new(f'pond growth fragment {group}-{index:02d}', mesh)
        scene.collection.objects.link(obj)
        mesh.materials.append(growth)

palette = []
for index, color in enumerate(((.006, .017, .010, 1), (.013, .029, .018, 1), (.019, .039, .020, 1))):
    material = bpy.data.materials.new(f'pond tuft wet leaf {index}')
    material.use_nodes = True
    shader = next(node for node in material.node_tree.nodes if node.type == 'BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value = color
    shader.inputs['Roughness'].default_value = .47
    shader.inputs['Specular IOR Level'].default_value = .24
    palette.append(material)

# A few low curled leaves create a depth cue like the reference's tiny
# foreground tuft. Keep them well below the far shoreline in projection.
vertices, faces, slots = [], [], []
tufts = ((.423, .022, 42, .008, .014), (.752, .009, 24, .012, .012),
         (.865, .025, 18, .006, .010))
for cx, cy, count, spread, projected_height in tufts:
    for index in range(count):
        x = cx + rng.gauss(0, spread * .40)
        y = cy + rng.gauss(0, .0017)
        base = water_point(x, y)
        pixel_height = world_to_camera_view(scene, scene.camera, base + Vector((0, 0, 1))).y - y
        assert pixel_height > 0
        height = projected_height * rng.uniform(.35, 1.0) / pixel_height
        width = (water_point(x + .00045, y) - base).length * rng.uniform(.6, 1.4)
        lean = right * height * rng.uniform(-.48, .48)
        lean.y += height * rng.uniform(-.20, .20)
        start = len(vertices)
        steps = 5
        for k in range(steps + 1):
            t = k / steps
            center = base + Vector((0, 0, height * (t - .16 * t * t))) + lean * t * t
            half_width = width * .5 * (1 - t) ** .75
            vertices.extend((tuple(center - right * half_width), tuple(center + right * half_width)))
        for k in range(steps):
            a = start + 2 * k
            faces.append((a, a + 1, a + 3, a + 2))
            slots.append(rng.choices((0, 1, 2), weights=(5, 3, 1))[0])
mesh = bpy.data.meshes.new('pond low curled tuft leaves mesh')
mesh.from_pydata(vertices, [], faces)
mesh.update()
obj = bpy.data.objects.new('pond low curled tuft leaves', mesh)
scene.collection.objects.link(obj)
for material in palette:
    mesh.materials.append(material)
for polygon, slot in zip(mesh.polygons, slots):
    polygon.material_index = slot

for name, old in before.items():
    expected = (old[0], True, old[2], old[3]) if name in hidden else old
    assert descriptor(bpy.data.objects[name]) == expected, name
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
assert len([obj for obj in scene.objects if obj.name.startswith('pond growth fragment ')]) == 16
assert len(mesh.polygons) == 420
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, 'FRAGMENTS 16', 'LEAVES 84', flush=True)
