"""Test sharper pond reflections and world-sized fine ripples in isolation."""
from pathlib import Path

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-water-fine-reflection-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-pond-growth-fragments-cloud-v1.blend'))
scene = bpy.context.scene
pond = bpy.data.objects['pond']


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


before = {obj.name: descriptor(obj) for obj in scene.objects if obj != pond}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
water = pond.material_slots[0].material.copy()
water.name = 'pond fine ripples sharper reflection'
nodes, links = water.node_tree.nodes, water.node_tree.links
shaders = [node for node in nodes if node.type == 'BSDF_PRINCIPLED']
bumps = [node for node in nodes if node.type == 'BUMP']
assert len(shaders) == len(bumps) == 1
shader, bump = shaders[0], bumps[0]
assert abs(shader.inputs['Roughness'].default_value - .30) < .00001
assert abs(shader.inputs['IOR'].default_value - 1.333) < .00001
assert abs(shader.inputs['Transmission Weight'].default_value - .58) < .00001
assert abs(bump.inputs['Strength'].default_value - .14) < .00001
assert abs(bump.inputs['Distance'].default_value - .07) < .00001
noise = bump.inputs['Height'].links[0].from_node
assert noise.type == 'TEX_NOISE' and not noise.inputs['Vector'].is_linked
assert abs(noise.inputs['Scale'].default_value - 3) < .00001

# generated coordinates spread three waves across the whole giant pond.
# shallow ripples sized in world units should break reflections into finer glints;
# the clarity windows and submerged color remain exactly as before.
shader.inputs['Roughness'].default_value = .16
bump.inputs['Strength'].default_value = .12
bump.inputs['Distance'].default_value = .20
noise.inputs['Scale'].default_value = 1
geometry = nodes.new('ShaderNodeNewGeometry')
mapping = nodes.new('ShaderNodeVectorMath')
mapping.operation = 'MULTIPLY'
mapping.inputs[1].default_value = (.045, .22, 1)
links.new(geometry.outputs['Position'], mapping.inputs[0])
links.new(mapping.outputs[0], noise.inputs['Vector'])
pond.material_slots[0].link = 'OBJECT'
pond.material_slots[0].material = water

assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, 'ROUGHNESS .16 RIPPLE MAPPING .045 .22', flush=True)
