"""Isolate whether the pond's final dark emission mix hides bed detail."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-water-surface-diagnostic-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-pond-bed-breakup-cloud-v1.blend'))
scene = bpy.context.scene
pond = bpy.data.objects['pond']
original = pond.material_slots[0].material
assert original.name == 'pond balanced roughness by distance'


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


before = {obj.name: descriptor(obj) for obj in scene.objects}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name:(obj.data.energy,tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
water = original.copy()
water.name = 'pond without final dark emission diagnostic'
nodes,links = water.node_tree.nodes,water.node_tree.links
surface = nodes['Material Output'].inputs['Surface']
final = nodes['Mix Shader.001']
existing = nodes['Mix Shader']
assert len(surface.links) == 1 and surface.links[0].from_node == final
assert final.inputs[1].links[0].from_node == existing
assert final.inputs[2].links[0].from_node.type == 'EMISSION'
before_links = {(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in links}

# geometry changes barely survived the retained surface treatment. isolate its
# last emission veil before planning a water rebuild; a brighter image alone
# is not a successful result, and the approved value baseline stays preserved.
links.new(existing.outputs[0],surface)
expected = before_links - {(final.name,final.outputs[0].name,'Material Output','Surface')}
expected.add((existing.name,existing.outputs[0].name,'Material Output','Surface'))
assert expected == {(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in links}
pond.material_slots[0].link = 'OBJECT'
pond.material_slots[0].material = water
for name,old in before.items():
    slots=list(old[3])
    if name == pond.name:
        slots[0]=water.name
    assert descriptor(bpy.data.objects[name]) == (old[0],old[1],old[2],tuple(slots)),name
assert camera == (scene.camera.data.lens,descriptor(scene.camera))
assert lights == {obj.name:(obj.data.energy,tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
assert scene.render.resolution_x == scene.render.resolution_y == 1200
assert scene.cycles.samples == 64
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True,packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True)
print('SAVED',output,'ONLY FINAL SURFACE EMISSION MIX BYPASSED',flush=True)
