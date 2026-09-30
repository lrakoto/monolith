"""Test irregular submerged shelf depth while preserving the retained materials."""
from pathlib import Path
from math import exp

import bpy


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-pond-depth-pockets-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-pond-bed-breakup-cloud-v1.blend'))
scene = bpy.context.scene
shelf = bpy.data.objects['submerged mottled shallows test']
assert len(shelf.data.vertices) == 4 and len(shelf.data.polygons) == 1
assert shelf.material_slots[0].material.name == 'submerged growth with irregular bed detail'
assert 'sparse submerged curved leaves' not in bpy.data.objects


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


before = {obj.name: descriptor(obj) for obj in scene.objects}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
old = shelf.data
assert all(abs(v.co.z) < .00001 for v in old.vertices)
assert tuple(shelf.location) == (0, -390, shelf.location.z)
assert abs(shelf.location.z + .7) < .00001


# the flat emissive shelf remains a useful value baseline, but its depth never
# varies. lower a few broad irregular pockets under the nearer water without
# moving the shore or adding more surface litter. material graphs stay intact.
pockets = ((-235,-375,90,48,2.4), (-125,-520,76,70,3.1),
           (190,-405,120,53,2.6), (310,-595,98,82,3.8),
           (-40,-715,135,60,2.2))
steps = 126
verts, faces = [], []
for j in range(steps+1):
    y = -1050 + 2100*j/steps
    wy = y + shelf.location.y
    fade = max(0, min(1, (-wy-250)/110))
    fade = fade*fade*(3-2*fade)
    for i in range(steps+1):
        x = -1050 + 2100*i/steps
        depth = sum(a*exp(-((x-cx)/rx)**2-((wy-cy)/ry)**2)
                    for cx,cy,rx,ry,a in pockets)
        verts.append((x,y,-min(4.5,depth)*fade))
for j in range(steps):
    for i in range(steps):
        k=j*(steps+1)+i
        faces.append((k,k+1,k+steps+2,k+steps+1))
mesh = bpy.data.meshes.new('submerged shelf with uneven depth pockets')
mesh.from_pydata(verts, [], faces)
mesh.update()
for material in old.materials:
    mesh.materials.append(material)
shelf.data = mesh
for face in mesh.polygons:
    face.use_smooth = True
points = [shelf.matrix_world @ v.co for v in mesh.vertices]
assert len(points) == 16129 and len(mesh.polygons) == 15876
assert all(-5.21 < p.z <= -.6999 for p in points)
assert all(abs(p.z + .7) < .00001 for p in points if p.y >= -250)
assert min(p.z for p in points) < -4
for name,old_desc in before.items():
    expected = (old_desc[0],old_desc[1],mesh.name,old_desc[3]) if name == shelf.name else old_desc
    assert descriptor(bpy.data.objects[name]) == expected,name
assert camera == (scene.camera.data.lens, descriptor(scene.camera))
assert lights == {obj.name:(obj.data.energy,tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
assert scene.render.resolution_x == scene.render.resolution_y == 1200
assert scene.cycles.samples == 64
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True,packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True)
print('SAVED',output,'POCKET DEPTH BOUNDS',min(p.z for p in points),max(p.z for p in points),flush=True)
