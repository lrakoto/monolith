"""Replace the low isolated shoreline crown with an overhanging small-tree grove."""
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-shore-grove-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-water-graded-clarity-cloud-v1.blend'))
scene = bpy.context.scene
hero = bpy.data.objects['fuller right shoreline crown']
assert len(hero.data.vertices) > 300000


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


before = {obj.name: descriptor(obj) for obj in scene.objects if obj.name != hero.name}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}

# The reference has a raised, horizontal canopy supported by several visible
# stems. The existing crown sits too low and reads as a single round shrub.
hero.location = (255, 25, 150)
hero.scale = (132, 78, 57)
hero.rotation_euler.z = .13
crowns = [hero]
for name, location, scale, turn in (
    ('shore grove left shoulder', (178, 5, 132), (74, 62, 59), -.31),
    ('shore grove right shoulder', (344, 70, 157), (81, 67, 63), .44),
):
    crown = hero.copy()
    crown.name = name
    scene.collection.objects.link(crown)
    crown.location = location
    crown.scale = scale
    crown.rotation_euler.z = turn
    crowns.append(crown)

bark = bpy.data.materials.new('shore grove dark wet bark')
bark.diffuse_color = (.016, .028, .019, 1)
bark.use_nodes = True
shader = bark.node_tree.nodes.get('Principled BSDF')
shader.inputs['Base Color'].default_value = (.016, .028, .019, 1)
shader.inputs['Roughness'].default_value = .84


def stem(name, points, radii, width):
    curve = bpy.data.curves.new(name + ' curve', 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 2
    curve.bevel_depth = width
    curve.bevel_resolution = 2
    spline = curve.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for point, pos, radius in zip(spline.points, points, radii):
        point.co = (*pos, 1)
        point.radius = radius
    tree = bpy.data.objects.new(name, curve)
    scene.collection.objects.link(tree)
    curve.materials.append(bark)
    return tree


for index, (x, y, rise, lean, width) in enumerate((
    (192, 4, 132, -18, 4.8),
    (257, 40, 149, 11, 6.0),
    (324, 69, 151, 17, 5.2),
    (371, 82, 148, -10, 4.3),
)):
    stem(f'shore grove trunk {index:02d}',
         ((x, y, 1), (x - 3, y + 2, rise * .34),
          (x + lean * .45, y + 4, rise * .70),
          (x + lean, y + 6, rise)),
         (1.12, .88, .62, .27), width)
    for side, delta in enumerate((-1, 1)):
        stem(f'shore grove branch {index:02d} {side}',
             ((x + lean * .38, y + 4, rise * .68),
              (x + lean + delta * 17, y + 9, rise * .83),
              (x + lean + delta * 39, y + 12, rise * 1.01)),
             (.61, .35, .12), width * .52)

bpy.context.view_layer.update()
projected = [world_to_camera_view(scene, scene.camera, crown.matrix_world @ Vector(corner))
             for crown in crowns for corner in crown.bound_box]
bounds = (min(v.x for v in projected), max(v.x for v in projected),
          min(v.y for v in projected), max(v.y for v in projected))
assert .55 < bounds[0] < .72 and .88 < bounds[1] < 1.1, bounds
assert .15 < bounds[2] < .26 and .26 < bounds[3] < .40, bounds
assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, 'GROVE_BOUNDS', tuple(round(v, 3) for v in bounds), flush=True)
