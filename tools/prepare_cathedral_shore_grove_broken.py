"""Break the shoreline hedge into smaller overlapping tree crowns."""
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-shore-grove-broken-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-shore-grove-placed-cloud-v1.blend'))
scene = bpy.context.scene
old_crowns = [bpy.data.objects[name] for name in (
    'fuller right shoreline crown', 'shore grove left shoulder',
    'shore grove right shoulder', 'shore grove lower foliage left',
    'shore grove lower foliage right')]
assert all(not obj.hide_render for obj in old_crowns)


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


before = {obj.name: descriptor(obj) for obj in scene.objects}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}

# Three large copies merge into a hedge with one continuous hanging skirt.
# Smaller crowns keep their fine leaves while staggered heights expose forks
# and let the bank show through without clearing the shoreline understory.
layout = (
    ((223, 15, 80), (48, 46, 64), -.60, .86),
    ((267, 16, 102), (56, 42, 75), .35, .96),
    ((315, 30, 112), (63, 51, 78), 1.30, .86),
    ((375, 55, 145), (72, 56, 87), -.40, 1.00),
    ((434, 82, 123), (58, 46, 74), .50, .82),
    ((340, -10, 74), (47, 40, 51), -.90, .68),
    ((402, 25, 86), (58, 43, 59), 1.80, .74),
)
new_crowns = []
for index, (location, scale, turn, value) in enumerate(layout):
    obj = old_crowns[0].copy()
    obj.name = f'shore grove broken crown {index:02d}'
    scene.collection.objects.link(obj)
    obj.location = location
    obj.scale = scale
    obj.rotation_euler.z = turn
    for slot in obj.material_slots:
        if slot.material and slot.material.name.startswith('shore grove warm '):
            material = slot.material.copy()
            material.name = f'broken grove {index:02d} ' + slot.material.name
            shader = next(node for node in material.node_tree.nodes if node.type == 'BSDF_PRINCIPLED')
            color = shader.inputs['Base Color'].default_value
            shader.inputs['Base Color'].default_value = tuple(color[i] * value for i in range(3)) + (1,)
            slot.link = 'OBJECT'
            slot.material = material
    new_crowns.append(obj)
for obj in old_crowns:
    obj.hide_render = True

bpy.context.view_layer.update()
projected = [world_to_camera_view(scene, scene.camera, obj.matrix_world @ Vector(corner))
             for obj in new_crowns for corner in obj.bound_box]
bounds = (min(p.x for p in projected), max(p.x for p in projected),
          min(p.y for p in projected), max(p.y for p in projected))
assert .62 < bounds[0] < .78 and .91 < bounds[1] < 1.20, bounds
assert .04 < bounds[2] < .18 and .22 < bounds[3] < .40, bounds
hidden = {obj.name for obj in old_crowns}
for name, old in before.items():
    expected = (old[0], True, old[2], old[3]) if name in hidden else old
    assert descriptor(bpy.data.objects[name]) == expected, name
assert len(scene.objects) == len(before) + len(new_crowns)
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, 'CROWNS', len(new_crowns), 'BOUNDS', bounds, flush=True)
