"""Break broad pond-bed color fields with a finer nondirectional layer."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-pond-bed-breakup-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-stone-fine-breakup-cloud-v1.blend'))
scene = bpy.context.scene
shelf = bpy.data.objects['submerged mottled shallows test']
original = shelf.material_slots[0].material
assert original.name == 'submerged growth gently lifted at shore'


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


before = {obj.name: descriptor(obj) for obj in scene.objects}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
growth = original.copy()
growth.name = 'submerged growth with irregular bed detail'
nodes, links = growth.node_tree.nodes, growth.node_tree.links
base = nodes['Noise Texture']
mapping = nodes['Vector Math']
assert mapping.operation == 'MULTIPLY'
assert all(abs(a-b) < .000001 for a,b in zip(mapping.inputs[1].default_value, (.012,.008,1)))
assert base.inputs['Vector'].links[0].from_node == mapping
ramps = [node for node in nodes if node.type == 'VALTORGB']
assert len(ramps) == 2
assert all(node.inputs['Fac'].links[0].from_node == base for node in ramps)
position = nodes['Geometry'].outputs['Position']

# native-resolution review confirmed the broad smooth fields are in the bed.
# add a smaller isotropic layer without stretching the existing map into rays,
# and keep signed variation around zero rather than brighten all the shallows.
fine_mapping = nodes.new('ShaderNodeVectorMath')
fine_mapping.operation = 'MULTIPLY'
fine_mapping.inputs[1].default_value = (.08,.08,.08)
links.new(position, fine_mapping.inputs[0])
fine = nodes.new('ShaderNodeTexNoise')
fine.inputs['Scale'].default_value = 1
fine.inputs['Detail'].default_value = 4
fine.inputs['Roughness'].default_value = .7
fine.inputs['Distortion'].default_value = .2
links.new(fine_mapping.outputs['Vector'], fine.inputs['Vector'])
variation = nodes.new('ShaderNodeMapRange')
variation.clamp = True
variation.inputs['From Min'].default_value = .35
variation.inputs['From Max'].default_value = .65
variation.inputs['To Min'].default_value = -.17
variation.inputs['To Max'].default_value = .17
links.new(fine.outputs['Fac'], variation.inputs['Value'])
combined = nodes.new('ShaderNodeMath')
combined.operation = 'ADD'
combined.use_clamp = True
links.new(base.outputs['Fac'], combined.inputs[0])
links.new(variation.outputs['Result'], combined.inputs[1])
for ramp in ramps:
    links.new(combined.outputs[0], ramp.inputs['Fac'])
shelf.material_slots[0].link = 'OBJECT'
shelf.material_slots[0].material = growth
for name, old in before.items():
    slots = list(old[3])
    if name == shelf.name:
        slots[0] = growth.name
    assert descriptor(bpy.data.objects[name]) == (old[0], old[1], old[2], tuple(slots)), name
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, 'BED DETAIL .08 XYZ SIGNED .17; ORIGINAL MAP PRESERVED', flush=True)
