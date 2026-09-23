"""Replace three visible round left-bank cores with detailed leaf silhouettes."""
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-overgrown-left-plinth-foliage-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-overgrown-trunk-natural-cloud-v1.blend'))
scene = bpy.context.scene
names = ('plinth planting 015', 'plinth planting 030', 'plinth planting 045')
template = bpy.data.objects['wall foliage backing 00']
assert len(template.data.vertices) > 300000


def descriptor(obj):
    return (
        tuple(value for row in obj.matrix_world for value in row),
        obj.hide_render,
        obj.data.name if obj.data else None,
        tuple(slot.material.name if slot.material else None for slot in obj.material_slots),
    )


def box(obj):
    projected = [world_to_camera_view(scene, scene.camera, obj.matrix_world @ Vector(corner)) for corner in obj.bound_box]
    return (min(v.x for v in projected), max(v.x for v in projected),
            min(v.y for v in projected), max(v.y for v in projected))


before = {obj.name: descriptor(obj) for obj in scene.objects if obj.name not in names}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
for index, name in enumerate(names):
    old = bpy.data.objects[name]
    assert old.type == 'MESH' and not old.hide_render
    assert old.material_slots[0].material.name == 'blockout canopy'
    old_box = box(old)
    corners = [old.matrix_world @ Vector(corner) for corner in old.bound_box]
    lo = Vector(tuple(min(c[i] for c in corners) for i in range(3)))
    hi = Vector(tuple(max(c[i] for c in corners) for i in range(3)))
    replacement = template.copy()
    replacement.name = f'left plinth fine foliage {index:02d}'
    scene.collection.objects.link(replacement)
    replacement.location = (lo + hi) / 2
    replacement.rotation_euler = (0, 0, (.31, 1.24, 2.05)[index])
    replacement.scale = hi - lo
    replacement.hide_render = False
    old.hide_render = True
    bpy.context.view_layer.update()
    new_box = box(replacement)
    assert max(abs(a - b) for a, b in zip(old_box, new_box)) < .018, (name, old_box, new_box)
    print('REPLACED', name, 'screen', tuple(round(v, 3) for v in old_box), flush=True)

assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, flush=True)
