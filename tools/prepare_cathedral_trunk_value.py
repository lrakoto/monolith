"""Compare gentle bark separation on only the two colossal framing trunks."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-overgrown-trunk-value-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-overgrown-overhead-connected-cloud-v1.blend'))
scene = bpy.context.scene
names = ('colossal trunk 0', 'colossal trunk 1')


def descriptor(obj):
    return (
        tuple(value for row in obj.matrix_world for value in row),
        obj.hide_render,
        obj.data.name if obj.data else None,
        tuple(slot.material.name if slot.material else None for slot in obj.material_slots),
    )


before = {obj.name: descriptor(obj) for obj in scene.objects if obj.name not in names}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
source = bpy.data.materials['vine draped colossal bark']
copy = source.copy()
copy.name = 'colossal trunk readable bark'
ramps = [node for node in copy.node_tree.nodes if node.type == 'VALTORGB']
assert len(ramps) == 1
elements = list(ramps[0].color_ramp.elements)
assert len(elements) == 2

# The old bark values vanish into the volume at this camera distance. Lift
# the brighter ridges more than the recesses to reveal texture, not a flat fill.
for element, factor in zip(elements, (2.0, 3.0)):
    element.color = tuple(min(1, channel * factor) for channel in element.color[:3]) + (element.color[3],)

for name in names:
    obj = bpy.data.objects[name]
    assert len(obj.material_slots) == 1
    assert obj.material_slots[0].material == source
    obj.material_slots[0].link = 'OBJECT'
    obj.material_slots[0].material = copy

assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, flush=True)
