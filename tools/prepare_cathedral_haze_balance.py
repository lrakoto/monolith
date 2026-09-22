"""Reduce the existing atmosphere's self illumination without changing its density."""
from pathlib import Path
import bpy
root = Path(__file__).resolve().parents[1] / 'renders'
source = root / 'cathedral-directional-depth-cloud-v1.blend'
output = root / 'cathedral-haze-balance-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.context.scene
before = {o.name: (tuple(v for row in o.matrix_world for v in row), o.hide_render, o.data.name if o.data else None) for o in scene.objects}
material = bpy.data.materials['distance haze']
nodes, links = material.node_tree.nodes, material.node_tree.links
volume = nodes.get('Principled Volume')
socket = volume.inputs['Emission Strength']
assert len(socket.links) == 1
old = socket.links[0].from_socket
links.remove(socket.links[0])
# retain the distant density gradient while testing whether emissive fog washes out the forest.
multiply = nodes.new('ShaderNodeMath')
multiply.name = 'haze emission quarter'
multiply.operation = 'MULTIPLY'
multiply.inputs[1].default_value = .25
links.new(old, multiply.inputs[0])
links.new(multiply.outputs[0], socket)
assert before == {o.name: (tuple(v for row in o.matrix_world for v in row), o.hide_render, o.data.name if o.data else None) for o in scene.objects}
scene.render.filepath = '//' + output.stem + '.png'
scene['depth_variant'] = 'existing haze emission x0.25, density unchanged'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, flush=True)
