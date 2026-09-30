"""Refine mineral patch edges without changing Cathedral composition or lighting."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-stone-fine-breakup-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-stone-irregular-weathering-cloud-v1.blend'))
scene = bpy.context.scene
original = bpy.data.materials['monument irregular mineral weathering']
targets = [(obj, index) for obj in scene.objects for index, slot in enumerate(obj.material_slots)
           if slot.material == original]
assert {obj.name for obj, index in targets} == {'limestone monument', '305'}


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


before = {obj.name: descriptor(obj) for obj in scene.objects}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
stone = original.copy()
stone.name = 'monument finer mineral breakup'
nodes = stone.node_tree.nodes
vectors = [node for node in nodes if node.type == 'VECT_MATH' and node.operation == 'MULTIPLY'
           and all(abs(a-b) < .00001 for a,b in zip(node.inputs[1].default_value, (.035,.035,.035)))]
assert len(vectors) == 1
noises = [link.to_node for link in vectors[0].outputs[0].links if link.to_node.type == 'TEX_NOISE']
assert len(noises) == 1
noise = noises[0]
ranges = [link.to_node for link in noise.outputs['Fac'].links if link.to_node.type == 'MAP_RANGE']
assert len(ranges) == 1
variation = ranges[0]
observed = (noise.inputs['Scale'].default_value, noise.inputs['Detail'].default_value,
            noise.inputs['Roughness'].default_value,
            variation.inputs['From Min'].default_value, variation.inputs['From Max'].default_value,
            variation.inputs['To Min'].default_value, variation.inputs['To Max'].default_value)
expected = (1, 3, .5, .25, .75, .76, 1.11)
print('INSPECTED MINERAL LAYER', observed, flush=True)
assert all(abs(a-b) < .00001 for a,b in zip(observed, expected)), observed

# the new mineral patches lost the woodlike grain but still looked soft.
# more fractal detail and a narrower input span should break their rounded edges;
# keep the output range and mean tone rather than brighten the whole monument.
noise.inputs['Detail'].default_value = 5
noise.inputs['Roughness'].default_value = .72
variation.inputs['From Min'].default_value = .35
variation.inputs['From Max'].default_value = .65
for obj, index in targets:
    obj.material_slots[index].link = 'OBJECT'
    obj.material_slots[index].material = stone
for name, old in before.items():
    slots = list(old[3])
    for obj, index in targets:
        if obj.name == name:
            slots[index] = stone.name
    assert descriptor(bpy.data.objects[name]) == (old[0], old[1], old[2], tuple(slots)), name
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, 'DETAIL 5 ROUGHNESS .72 RANGE .35 .65', flush=True)
