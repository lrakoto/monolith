"""Compare cropped overhead foliage with the open cathedral ascent."""
from pathlib import Path
import math

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-overgrown-overhead-canopy-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-overgrown-ridge-visible-cloud-v1.blend'))
scene = bpy.context.scene


def descriptor(obj):
    return (
        tuple(value for row in obj.matrix_world for value in row),
        obj.hide_render,
        obj.data.name if obj.data else None,
    )


before = {obj.name: descriptor(obj) for obj in scene.objects}
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
camera = (scene.camera.data.lens, descriptor(scene.camera))
template = bpy.data.objects['wall foliage backing 00']
assert len(template.data.vertices) > 300000

# These are in front of the two giant trunks and cropped by the frame. The
# unplanted center keeps the distant monument clear, as in the reference.
positions = [
    (-360, -100, 785, 210, 150, 210),
    (-300, 130, 740, 220, 140, 200),
    (-450, 0, 650, 200, 150, 180),
    (360, 100, 760, 200, 140, 220),
    (480, -80, 700, 220, 140, 180),
    (290, 240, 810, 170, 130, 190),
]
for index, (x, y, z, width, depth, height) in enumerate(positions):
    obj = template.copy()
    obj.name = f'overhead frame crown {index:02d}'
    scene.collection.objects.link(obj)
    obj.location = (x, y, z)
    obj.scale = (width, depth, height)
    obj.rotation_euler = (0, 0, (index * 2.39996) % (2 * math.pi))
    obj.hide_render = False
    projected = world_to_camera_view(scene, scene.camera, Vector((x, y, z)))
    assert projected.x < 0.4 or projected.x > 0.6, (obj.name, projected)

assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert sum(obj.name.startswith('overhead frame crown ') for obj in scene.objects) == 6
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, 'CROWNS', len(positions), flush=True)
