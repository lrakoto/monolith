"""Build an uneven shore canopy from overlapping differently toned masses."""
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-overgrown-shore-layered-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-overgrown-trunk-natural-cloud-v1.blend'))
scene = bpy.context.scene


def descriptor(obj):
    return (
        tuple(value for row in obj.matrix_world for value in row),
        obj.hide_render,
        obj.data.name if obj.data else None,
        tuple(slot.material.name if slot.material else None for slot in obj.material_slots),
    )


before = {obj.name: descriptor(obj) for obj in scene.objects}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
template = bpy.data.objects['wall foliage backing 00']
assert len(template.data.vertices) > 300000

# The single shoreline crown reads like a round shrub when it is simply
# enlarged. A darker canopy behind it should make a connected, stepped edge.
layer = template.copy()
layer.name = 'right shoreline upper leaf mass'
scene.collection.objects.link(layer)
layer.location = (380, 190, 170)
layer.scale = (180, 125, 190)
layer.rotation_euler = (0, 0, 1.37)
layer.hide_render = False
bpy.context.view_layer.update()
projected = [world_to_camera_view(scene, scene.camera, layer.matrix_world @ Vector(corner)) for corner in layer.bound_box]
bounds = (min(v.x for v in projected), max(v.x for v in projected),
          min(v.y for v in projected), max(v.y for v in projected))
print('SHORE_LAYER_BOUNDS', tuple(round(v, 3) for v in bounds), flush=True)
assert .65 < bounds[0] < .90
assert bounds[3] > .29

assert all(descriptor(bpy.data.objects[name]) == old for name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, flush=True)
