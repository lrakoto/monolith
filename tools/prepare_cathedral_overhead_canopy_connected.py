"""Turn the overhead test trees into darker overlapping leaf cover."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-overgrown-overhead-connected-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-overgrown-overhead-canopy-cloud-v1.blend'))
scene = bpy.context.scene
names = [f'overhead frame crown {index:02d}' for index in range(6)]
assert all(name in bpy.data.objects for name in names)


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

transparent = bpy.data.materials.new('overhead branches invisible')
transparent.use_nodes = True
nodes = transparent.node_tree.nodes
nodes.clear()
output_node = nodes.new('ShaderNodeOutputMaterial')
glassless = nodes.new('ShaderNodeBsdfTransparent')
transparent.node_tree.links.new(glassless.outputs['BSDF'], output_node.inputs['Surface'])
darkened = {}


def leaf_material(source):
    if source.name in darkened:
        return darkened[source.name]
    copy = source.copy()
    copy.name = 'overhead dark ' + source.name
    nodes = copy.node_tree.nodes
    links = copy.node_tree.links
    shader = [node for node in nodes if node.type == 'BSDF_PRINCIPLED']
    assert len(shader) == 1
    base = shader[0].inputs['Base Color']
    assert len(base.links) == 1
    old = base.links[0].from_socket
    mix = nodes.new('ShaderNodeMixRGB')
    mix.blend_type = 'MULTIPLY'
    mix.inputs[0].default_value = 1
    mix.inputs[2].default_value = (.60, .66, .60, 1)
    links.new(old, mix.inputs[1])
    links.new(mix.outputs[0], base)
    darkened[source.name] = copy
    return copy


# Pull each small group together so it reads as canopy attached to the
# colossal framing trees rather than six isolated crowns with dangling stems.
new_x = [-360, -340, -390, 340, 430, 350]
for index, name in enumerate(names):
    obj = bpy.data.objects[name]
    obj.location.x = new_x[index]
    obj.scale.x *= 1.30
    obj.scale.z *= 1.08
    assert len(obj.material_slots) == 5
    for slot_index, slot in enumerate(obj.material_slots):
        slot.link = 'OBJECT'
        slot.material = transparent if slot_index == 4 else leaf_material(slot.material)

assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, 'CROWNS', len(names), flush=True)
