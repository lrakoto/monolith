"""Broaden far-bank green shallows and deepen the near water without scene edits."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-water-deep-contrast-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-water-value-split-cloud-v1.blend'))
scene = bpy.context.scene
pond = bpy.data.objects['pond']
shelf = bpy.data.objects['submerged mottled shallows test']


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


before = {obj.name: descriptor(obj) for obj in scene.objects if obj.name not in (pond.name, shelf.name)}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}

growth = shelf.material_slots[0].material.copy()
growth.name = 'submerged growth broader far bank study'
mask = [node for node in growth.node_tree.nodes if node.type == 'VALTORGB'
        and abs(node.color_ramp.elements[0].position - .43) < .00001
        and abs(node.color_ramp.elements[1].position - .67) < .00001]
assert len(mask) == 1, mask
mask[0].color_ramp.elements[0].position = .32
mask[0].color_ramp.elements[1].position = .58
shelf.material_slots[0].link = 'OBJECT'
shelf.material_slots[0].material = growth

water = pond.material_slots[0].material.copy()
water.name = 'pond deep foreground study'
near_strength = [node for node in water.node_tree.nodes if node.type == 'MATH'
                 and node.operation == 'MULTIPLY'
                 and abs(node.inputs[1].default_value - .24) < .00001]
assert len(near_strength) == 1, near_strength
near_strength[0].inputs[1].default_value = .42
pond.material_slots[0].link = 'OBJECT'
pond.material_slots[0].material = water

assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, flush=True)
