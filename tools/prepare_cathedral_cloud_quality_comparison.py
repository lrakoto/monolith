"""Render the retained Cathedral at higher quality without changing the scene."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-fine-mineral-quality-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-stone-fine-breakup-cloud-v1.blend'))
scene = bpy.context.scene
assert scene.render.engine == 'CYCLES'
assert (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage) == (1200, 1200, 100)
assert scene.cycles.samples == 64 and scene.cycles.use_adaptive_sampling
assert abs(scene.cycles.adaptive_threshold - .01) < .000001
assert scene.cycles.use_denoising and not scene.camera.data.dof.use_dof


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


before = {obj.name: descriptor(obj) for obj in scene.objects}
camera = (scene.camera.data.lens, scene.camera.data.shift_x, scene.camera.data.shift_y)
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
view = (scene.view_settings.view_transform, scene.view_settings.look, scene.view_settings.exposure)

# do not compensate for softness by changing the approved composition or shader.
# this comparison separates sampling loss from detail the scene does not contain.
scene.render.resolution_x = 2400
scene.render.resolution_y = 2400
scene.cycles.samples = 128
scene.cycles.adaptive_threshold = .005
assert before == {obj.name: descriptor(obj) for obj in scene.objects}
assert camera == (scene.camera.data.lens, scene.camera.data.shift_x, scene.camera.data.shift_y)
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
assert view == (scene.view_settings.view_transform, scene.view_settings.look, scene.view_settings.exposure)
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, '2400PX 128SAMPLES ADAPTIVE .005', flush=True)
