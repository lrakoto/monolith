"""Test a taller, broader shoreline crown against the distant camera."""
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-overgrown-shore-hero-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-overgrown-trunk-natural-cloud-v1.blend'))
scene = bpy.context.scene
name = 'fuller right shoreline crown'
hero = bpy.data.objects[name]
assert hero.type == 'MESH' and not hero.hide_render and len(hero.data.vertices) > 300000


def descriptor(obj):
    return (
        tuple(value for row in obj.matrix_world for value in row),
        obj.hide_render,
        obj.data.name if obj.data else None,
        tuple(slot.material.name if slot.material else None for slot in obj.material_slots),
    )


before = {obj.name: descriptor(obj) for obj in scene.objects if obj.name != name}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
assert tuple(round(value) for value in hero.location) == (240, 54, 66)

# The reference has one broad, high bank of leaves near the right waterline.
# Widen and raise this existing detailed crown without lifting its root.
hero.location.x += 100
hero.scale.x *= 1.25
hero.scale.z *= 1.45
bpy.context.view_layer.update()
projected = [world_to_camera_view(scene, scene.camera, hero.matrix_world @ Vector(corner)) for corner in hero.bound_box]
print('PROJECTED', tuple(round(value, 3) for value in (
    min(p.x for p in projected), max(p.x for p in projected),
    min(p.y for p in projected), max(p.y for p in projected),
)), flush=True)
assert .63 < min(p.x for p in projected) < .73
assert max(p.y for p in projected) > .29

assert all(descriptor(bpy.data.objects[obj_name]) == old for obj_name, old in before.items())
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True, packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
print('SAVED', output, 'HERO_BOUNDS', tuple(round(value, 3) for value in (
    min(p.x for p in projected), max(p.x for p in projected),
    min(p.y for p in projected), max(p.y for p in projected),
)), flush=True)
