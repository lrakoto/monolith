"""Test whether the full stair faces can read without changing their geometry."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-overgrown-stair-readability-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-overgrown-ridge-visible-cloud-v1.blend'))
scene = bpy.context.scene


def descriptor(obj):
    return (
        tuple(value for row in obj.matrix_world for value in row),
        obj.hide_render,
        obj.data.name if obj.data else None,
    )


before = {obj.name: descriptor(obj) for obj in scene.objects}
steps = [obj for obj in scene.objects if obj.name.startswith('tread ')]
assert len(steps) == 150
copies = {}


def brighter_copy(source, face, tint):
    key = (source.name, face)
    if key in copies:
        return copies[key]
    copy = source.copy()
    copy.name = f'stair {face} readable {source.name}'
    nodes = copy.node_tree.nodes
    links = copy.node_tree.links
    shaders = [node for node in nodes if node.type == 'BSDF_PRINCIPLED']
    assert len(shaders) == 1
    base = shaders[0].inputs['Base Color']
    assert len(base.links) == 1
    old = base.links[0].from_socket
    mix = nodes.new('ShaderNodeMixRGB')
    mix.blend_type = 'MULTIPLY'
    mix.inputs[0].default_value = 1
    mix.inputs[2].default_value = (*tint, 1)
    links.new(old, mix.inputs[1])
    links.new(mix.outputs[0], base)
    copies[key] = copy
    return copy


changed_faces = {'riser': 0, 'top': 0}
for obj in steps:
    assert len(obj.data.polygons) == 6, obj.name
    source = obj.material_slots[0].material
    assert source and source.name.startswith('weathered basalt variation ')
    riser = brighter_copy(source, 'riser', (1.38, 1.32, 1.28))
    top = brighter_copy(source, 'top', (1.60, 1.50, 1.42))
    for face, material in (('riser', riser), ('top', top)):
        assert material.name not in [slot.material.name for slot in obj.material_slots if slot.material]
        obj.data.materials.append(material)
        index = len(obj.material_slots) - 1
        polygons = [polygon for polygon in obj.data.polygons if
                    (polygon.normal.y < -0.9 if face == 'riser' else polygon.normal.z > 0.9)]
        assert len(polygons) == 1, (obj.name, face)
        polygons[0].material_index = index
        changed_faces[face] += 1

assert changed_faces == {'riser': 150, 'top': 150}
assert before == {obj.name: descriptor(obj) for obj in scene.objects}
assert scene.camera.data.lens == 47
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, 'FACES', changed_faces, flush=True)
