"""Test a distant, uneven forest crown line behind the monument."""
from pathlib import Path
import math
import bpy

root = Path(__file__).resolve().parents[1] / 'renders'
source = root / 'cathedral-overgrown-remote-depth-cloud-v1.blend'
output = root / 'cathedral-overgrown-ridge-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.context.scene
before = {
    obj.name: (
        tuple(value for row in obj.matrix_world for value in row),
        obj.hide_render,
        obj.data.name if obj.data else None,
    )
    for obj in scene.objects
}
camera = (scene.camera.data.lens, tuple(value for row in scene.camera.matrix_world for value in row))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}

# Old foliage already covers the wall. These crowns sit behind it and form
# the taller uneven horizon visible around the monument in the reference.
positions = [
    (-710, 1600, 805, 170, 130, 135),
    (-620, 1450, 830, 155, 118, 145),
    (-545, 1570, 800, 145, 120, 124),
    (-475, 1380, 840, 158, 125, 148),
    (-392, 1340, 828, 137, 113, 128),
    (-320, 1430, 804, 122, 102, 112),
    (315, 1410, 816, 126, 108, 113),
    (392, 1330, 845, 150, 120, 140),
    (478, 1410, 826, 146, 112, 130),
    (565, 1570, 850, 165, 128, 144),
    (650, 1490, 821, 153, 116, 126),
    (738, 1640, 800, 160, 121, 130),
]
template = bpy.data.objects['wall foliage backing 00']
for index, (x, y, z, width, depth, height) in enumerate(positions):
    obj = template.copy()
    obj.name = f'distant ridge foliage {index:02d}'
    scene.collection.objects.link(obj)
    obj.location = (x, y, z)
    obj.scale = (width, depth, height)
    obj.rotation_euler = (0, 0, (index * 2.39996) % (2 * math.pi))
    obj.hide_render = False

for name, descriptor in before.items():
    obj = bpy.data.objects[name]
    current = (
        tuple(value for row in obj.matrix_world for value in row),
        obj.hide_render,
        obj.data.name if obj.data else None,
    )
    assert current == descriptor, name
assert camera == (scene.camera.data.lens, tuple(value for row in scene.camera.matrix_world for value in row))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene['distant_ridge_count'] = len(positions)
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, 'CROWNS', len(positions), flush=True)
