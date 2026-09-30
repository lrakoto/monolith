"""Replace strong vertical monument streaks with restrained mineral mottling."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-stone-irregular-weathering-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-water-balanced-response-cloud-v1.blend'))
scene = bpy.context.scene
original = bpy.data.materials['weathered monumental limestone']
targets = [(obj, index) for obj in scene.objects for index, slot in enumerate(obj.material_slots)
           if slot.material == original]
assert {obj.name for obj, index in targets} == {'limestone monument', '305'}, [(obj.name, index) for obj, index in targets]


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


before = {obj.name: descriptor(obj) for obj in scene.objects}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
stone = original.copy()
stone.name = 'monument irregular mineral weathering'
nodes = stone.node_tree.nodes


def mapped_noise(scale):
    matches = [node for node in nodes if node.type == 'VECT_MATH' and node.operation == 'MULTIPLY'
               and all(abs(a-b) < .00001 for a,b in zip(node.inputs[1].default_value, scale))]
    assert len(matches) == 1, (scale, matches)
    vector = matches[0]
    noise = [link.to_node for link in vector.outputs[0].links if link.to_node.type == 'TEX_NOISE']
    assert len(noise) == 1
    ranges = [link.to_node for link in noise[0].outputs['Fac'].links if link.to_node.type == 'MAP_RANGE']
    assert len(ranges) == 1
    return vector, ranges[0]


# the tall surface's .005 z frequency stretched weathering into woodlike grain.
# keep its mean value but replace those long streaks with smaller mineral patches.
vector, variation = mapped_noise((.14, .04, .005))
assert abs(variation.inputs['To Min'].default_value - .82) < .00001
assert abs(variation.inputs['To Max'].default_value - 1.18) < .00001
vector.inputs[1].default_value = (.065, .065, .040)
variation.inputs['To Min'].default_value = .94
variation.inputs['To Max'].default_value = 1.06

# the later grain layer carries most of the visible irregular contrast.
# give it comparable dimensions in all directions rather than another vertical bias.
vector, variation = mapped_noise((.028, .028, .018))
assert abs(variation.inputs['To Min'].default_value - .72) < .00001
assert abs(variation.inputs['To Max'].default_value - 1.15) < .00001
vector.inputs[1].default_value = (.035, .035, .035)
variation.inputs['To Min'].default_value = .76
variation.inputs['To Max'].default_value = 1.11

for obj, index in targets:
    obj.material_slots[index].link = 'OBJECT'
    obj.material_slots[index].material = stone
for name, old in before.items():
    new = descriptor(bpy.data.objects[name])
    slots = list(old[3])
    for obj, index in targets:
        if obj.name == name:
            slots[index] = stone.name
    assert new == (old[0], old[1], old[2], tuple(slots)), name
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, 'STONE TARGETS', [(obj.name,index) for obj,index in targets], flush=True)
