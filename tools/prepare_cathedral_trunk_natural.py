"""Break the regular bright trunk ribs with broad natural shadow variation."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-overgrown-trunk-natural-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-overgrown-trunk-value-cloud-v1.blend'))
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
source = bpy.data.materials['colossal trunk readable bark']
copy = source.copy()
copy.name = 'colossal trunk irregular bark'
nodes = copy.node_tree.nodes
links = copy.node_tree.links
shader = nodes['Principled BSDF']
base = shader.inputs['Base Color']
assert len(base.links) == 1
old = base.links[0].from_socket
coordinates = [node for node in nodes if node.type == 'TEX_COORD']
assert len(coordinates) == 1

# The raised bark reveals useful scale but also emphasizes long parallel
# ribs. A lower-frequency shadow mask interrupts them without changing mesh.
noise = nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 3.2
noise.inputs['Detail'].default_value = 2
links.new(coordinates[0].outputs['Generated'], noise.inputs['Vector'])
ramp = nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = .25
ramp.color_ramp.elements[0].color = (.48, .48, .48, 1)
ramp.color_ramp.elements[1].position = .73
ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
mix = nodes.new('ShaderNodeMixRGB')
mix.blend_type = 'MULTIPLY'
mix.inputs[0].default_value = 1
links.new(old, mix.inputs[1])
links.new(ramp.outputs['Color'], mix.inputs[2])
links.new(mix.outputs['Color'], base)

for name in names:
    obj = bpy.data.objects[name]
    assert len(obj.material_slots) == 1 and obj.material_slots[0].material == source
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
