"""Test whether the modeled bed reads through a clearer pond surface."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-water-transmission-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-overgrown-right-canopy-contour-cloud-v1.blend'))
scene = bpy.context.scene
pond = bpy.data.objects['pond']
assert len(pond.material_slots) == 1
old_material = pond.material_slots[0].material
assert old_material.name == 'deep green clear water'


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


before = {obj.name: descriptor(obj) for obj in scene.objects if obj.name != pond.name}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
material = old_material.copy()
material.name = 'pond clearer water test'
shader = next(node for node in material.node_tree.nodes if node.type == 'BSDF_PRINCIPLED')
assert abs(shader.inputs['Transmission Weight'].default_value - .22) < .00001
assert abs(shader.inputs['Roughness'].default_value - .30) < .00001
assert abs(shader.inputs['IOR'].default_value - 1.333) < .00001
shader.inputs['Transmission Weight'].default_value = .58
pond.material_slots[0].link = 'OBJECT'
pond.material_slots[0].material = material

assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, flush=True)
