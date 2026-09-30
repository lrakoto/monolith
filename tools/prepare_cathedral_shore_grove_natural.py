"""Break the shoreline grove's flat hedge profile into layered tree crowns."""
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-shore-grove-natural-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-shore-grove-cloud-v1.blend'))
scene = bpy.context.scene
names = ('fuller right shoreline crown', 'shore grove left shoulder', 'shore grove right shoulder')
crowns = [bpy.data.objects[name] for name in names]


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


before = {obj.name: descriptor(obj) for obj in scene.objects if obj.name not in names}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}

# A wide, short center crown drew a straight lit bar. Let the three original
# masses rise and overlap unevenly, with smaller shadowed leaves below them.
for crown, location, scale, turn in zip(crowns,
                                        ((260, 20, 154), (174, 0, 140), (350, 65, 180)),
                                        ((105, 85, 90), (77, 60, 78), (92, 70, 80)),
                                        (.12, -.33, .43)):
    crown.location = location
    crown.scale = scale
    crown.rotation_euler.z = turn

lower = []
for name, location, scale, turn in (
    ('shore grove lower foliage left', (215, -5, 110), (65, 57, 52), -.08),
    ('shore grove lower foliage right', (319, 33, 122), (74, 59, 57), .28),
):
    obj = crowns[0].copy()
    obj.name = name
    scene.collection.objects.link(obj)
    obj.location = location
    obj.scale = scale
    obj.rotation_euler.z = turn
    for slot in obj.material_slots:
        if slot.material.name.startswith('soft leaf surface '):
            material = slot.material.copy()
            material.name = name + ' ' + slot.material.name
            shader = next(node for node in material.node_tree.nodes if node.type == 'BSDF_PRINCIPLED')
            color = shader.inputs['Base Color'].default_value
            shader.inputs['Base Color'].default_value = (color[0] * .62, color[1] * .63, color[2] * .62, 1)
            slot.link = 'OBJECT'
            slot.material = material
    lower.append(obj)

bpy.context.view_layer.update()
projected = [world_to_camera_view(scene, scene.camera, crown.matrix_world @ Vector(corner))
             for crown in crowns + lower for corner in crown.bound_box]
bounds = (min(v.x for v in projected), max(v.x for v in projected),
          min(v.y for v in projected), max(v.y for v in projected))
assert .55 < bounds[0] < .72 and .88 < bounds[1] < 1.1, bounds
assert .12 < bounds[2] < .28 and .30 < bounds[3] < .43, bounds
assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, 'GROVE_BOUNDS', tuple(round(v, 3) for v in bounds), flush=True)
