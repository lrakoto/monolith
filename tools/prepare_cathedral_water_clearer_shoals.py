"""Reveal more of the modeled shallows without changing their placement or light."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-water-clearer-shoals-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-water-layered-shoals-cloud-v1.blend'))
scene = bpy.context.scene
pond = bpy.data.objects['pond']


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


before = {obj.name: descriptor(obj) for obj in scene.objects if obj.name != pond.name}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
water = pond.material_slots[0].material.copy()
water.name = 'pond clearer broken shallows test'
shader = next(node for node in water.node_tree.nodes if node.type == 'BSDF_PRINCIPLED')
assert abs(shader.inputs['Roughness'].default_value - .30) < .00001
assert abs(shader.inputs['IOR'].default_value - 1.333) < .00001
assert abs(shader.inputs['Transmission Weight'].default_value - .58) < .00001
clear_mix = [node for node in water.node_tree.nodes
             if node.type == 'MATH' and node.operation == 'MULTIPLY'
             and abs(node.inputs[1].default_value - .42) < .00001]
assert len(clear_mix) == 1, clear_mix
clear_mix[0].inputs[1].default_value = .72
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
