"""Set the small shoreline grove deeper into the right bank composition."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-shore-grove-placed-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-holistic-shore-water-cloud-v1.blend'))
scene = bpy.context.scene
crowns = [bpy.data.objects[name] for name in (
    'fuller right shoreline crown', 'shore grove left shoulder',
    'shore grove right shoulder', 'shore grove lower foliage left',
    'shore grove lower foliage right')]
stems = [obj for obj in scene.objects if obj.name.startswith(('shore grove trunk', 'shore grove branch'))]
understory = [obj for obj in scene.objects if obj.name.startswith('shore grove understory')]
assert len(stems) == 12 and len(understory) == 12


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


changed = {obj.name for obj in crowns + stems + understory}
before = {obj.name: descriptor(obj) for obj in scene.objects if obj.name not in changed}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}

# The first integrated grove rises into the mid-bank and reads as a bright
# hedge. The reference's small trees sit at the water edge on the right.
for crown in crowns:
    crown.location.x += 35
    crown.location.z -= 45
for obj in understory:
    obj.location.x += 35
for obj in stems:
    assert obj.type == 'CURVE' and len(obj.data.splines) == 1
    for point in obj.data.splines[0].points:
        point.co.x += 35
        point.co.z *= .70

warm = [mat for mat in bpy.data.materials if mat.name.startswith('shore grove warm ')]
assert len(warm) == 4
for mat in warm:
    shader = next(node for node in mat.node_tree.nodes if node.type == 'BSDF_PRINCIPLED')
    color = shader.inputs['Base Color'].default_value
    shader.inputs['Base Color'].default_value = tuple(color[i] * .78 for i in range(3)) + (1,)

assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, 'STEMS', len(stems), 'UNDERSTORY', len(understory), flush=True)
