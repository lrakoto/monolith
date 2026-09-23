"""Test whether stronger selective canopy openings reveal distant leaves."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-overgrown-bank-light-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-overgrown-overhead-connected-cloud-v1.blend'))
scene = bpy.context.scene


def descriptor(obj):
    return (
        tuple(value for row in obj.matrix_world for value in row),
        obj.hide_render,
        obj.data.name if obj.data else None,
        tuple(slot.material.name if slot.material else None for slot in obj.material_slots),
    )


before = {obj.name: descriptor(obj) for obj in scene.objects}
camera = (scene.camera.data.lens, descriptor(scene.camera))
original_lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
factors = {'left canopy opening': 2.4, 'right canopy opening': 2.2}
for name, factor in factors.items():
    light = bpy.data.objects[name]
    assert light.type == 'LIGHT' and light.data.type == 'POINT'
    light.data.energy *= factor

assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
for name, values in original_lights.items():
    light = bpy.data.objects[name]
    expected = values[0] * factors.get(name, 1)
    assert abs(light.data.energy - expected) < .01 and tuple(light.data.color) == values[1], name
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, 'LIGHTS', factors, flush=True)
