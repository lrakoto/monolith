"""Test a larger irregular right-bank canopy contour at the final camera."""
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-overgrown-right-canopy-contour-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-overgrown-trunk-natural-cloud-v1.blend'))
scene = bpy.context.scene
names = (
    'fine foliage 7299', 'fine foliage 6880', 'fine foliage 6834',
    'fine foliage 7307', 'fine foliage 6843', 'fine foliage 7313',
    'fine foliage 7302', 'fine foliage 7461', 'fine foliage 6841',
    'fine foliage 6564', 'fine foliage 1699', 'fine foliage 6573',
    'fine foliage 6691', 'fine foliage 6694', 'fine foliage 6581',
    'fine foliage 7279', 'fine foliage 6540', 'fine foliage 6601',
    'fine foliage 6567', 'fine foliage 7133',
)
assert len(names) == len(set(names))


def descriptor(obj):
    return (
        tuple(value for row in obj.matrix_world for value in row),
        obj.hide_render,
        obj.data.name if obj.data else None,
        tuple(slot.material.name if slot.material else None for slot in obj.material_slots),
    )


def bottom(obj):
    return min((obj.matrix_world @ Vector(corner)).z for corner in obj.bound_box)


before = {obj.name: descriptor(obj) for obj in scene.objects if obj.name not in names}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
factors = (1.28, 1.49, 1.20, 1.36, 1.57, 1.24, 1.43)
for index, name in enumerate(names):
    obj = bpy.data.objects[name]
    assert obj.type == 'MESH' and not obj.hide_render and len(obj.data.vertices) > 60000
    projected = world_to_camera_view(scene, scene.camera, obj.location)
    assert .61 < projected.x < .94 and .32 < projected.y < .70, (name, projected)
    old_bottom = bottom(obj)
    obj.scale.z *= factors[index % len(factors)]
    obj.scale.x *= (1.06, .98, 1.12)[index % 3]
    bpy.context.view_layer.update()
    obj.location.z += old_bottom - bottom(obj)
    bpy.context.view_layer.update()
    assert abs(bottom(obj) - old_bottom) < .001

# The selected leaves already have rich geometry. Unequal height and width,
# anchored at the same ground level, should form a bank rather than a row of
# similarly sized crowns. Everything outside the probed visible strip stays.
assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, 'CONTOUR_CROWNS', len(names), flush=True)
