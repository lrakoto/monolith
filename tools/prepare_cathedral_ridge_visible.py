"""Move the test crowns into a brighter, visible layer above the far wall."""
from pathlib import Path
import bpy

root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-overgrown-ridge-visible-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-overgrown-ridge-cloud-v1.blend'))
scene = bpy.context.scene
names = [f'distant ridge foliage {index:02d}' for index in range(12)]
for index, name in enumerate(names):
    obj = bpy.data.objects[name]
    obj.location.y = 1170 + (index * 53) % 151
    obj.location.z += 35
    obj.scale.x *= 1.15
    obj.scale.y *= 1.10
    obj.scale.z *= 1.12
    # The wall foliage was shaded down for the nearer stone. The distant
    # crowns need their own untinted leaf color to survive the existing haze.
    for slot in obj.material_slots:
        slot.link = 'DATA'
assert sum(obj.name.startswith('distant ridge foliage ') for obj in scene.objects) == 12
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, flush=True)
