"""Test warmer stair markers as scale cues without moving the ascent."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-overgrown-lamp-readability-cloud-v1.blend'
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


hoods = [obj for obj in scene.objects if obj.type == 'MESH' and obj.name.startswith('lamp hood')]
glass = [obj for obj in scene.objects if obj.type == 'MESH' and obj.name.startswith('amber lamp')]
pools = [obj for obj in scene.objects if obj.type == 'LIGHT' and obj.name.startswith('lamp pool')]
assert len(hoods) == len(glass) == len(pools) == 18
changing = {obj.name for obj in hoods + glass}
before = {obj.name: descriptor(obj) for obj in scene.objects if obj.name not in changing}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}

bronze = bpy.data.materials['aged bronze lamps'].copy()
bronze.name = 'readable aged bronze lamps'
ramps = [node for node in bronze.node_tree.nodes if node.type == 'VALTORGB']
assert len(ramps) == 1 and len(ramps[0].color_ramp.elements) == 2
for element in ramps[0].color_ramp.elements:
    element.color = tuple(min(1, channel * 1.9) for channel in element.color[:3]) + (element.color[3],)

amber = bpy.data.materials['warm lamp glass'].copy()
amber.name = 'readable warm lamp glass'
shader = amber.node_tree.nodes['Principled BSDF']
assert shader.inputs['Emission Strength'].default_value == 4
shader.inputs['Emission Strength'].default_value = 6

# The existing housings are already wide enough; their dark bronze only
# leaves the tiny emissive core visible from the distant reference camera.
for obj, source, material in [(obj, 'aged bronze lamps', bronze) for obj in hoods] + [
    (obj, 'warm lamp glass', amber) for obj in glass
]:
    assert len(obj.material_slots) == 1 and obj.material_slots[0].material.name == source
    obj.material_slots[0].link = 'OBJECT'
    obj.material_slots[0].material = material
for obj in pools:
    obj.data.energy *= 2.5

assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
for name, (energy, color) in lights.items():
    obj = bpy.data.objects[name]
    assert abs(obj.data.energy - energy * (2.5 if obj in pools else 1)) < .01
    assert tuple(obj.data.color) == color
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, 'LAMPS', len(pools), flush=True)
