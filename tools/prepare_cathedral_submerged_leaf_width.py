"""Correct subpixel submerged leaf widths without changing centers or water."""
from pathlib import Path

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-submerged-leaf-width-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-submerged-leaf-depth-cloud-v1.blend'))
scene = bpy.context.scene
leaf = bpy.data.objects['sparse submerged curved leaves']
assert len(leaf.data.polygons) == 288 and len(leaf.data.vertices) == 648


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


before = {obj.name: descriptor(obj) for obj in scene.objects}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy,tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
depsgraph = bpy.context.evaluated_depsgraph_get()
inverse = scene.camera.calc_matrix_camera(depsgraph,
    x=scene.render.resolution_x,y=scene.render.resolution_y,
    scale_x=scene.render.pixel_aspect_x,scale_y=scene.render.pixel_aspect_y).inverted()
origin = scene.camera.matrix_world.translation


def at_depth(x,y,z):
    near = inverse @ Vector((x*2-1,y*2-1,-1,1))
    near = Vector(near[:3])/near.w
    ray = scene.camera.matrix_world.to_3x3() @ near
    return origin+ray*((z-origin.z)/ray.z)


# the first leaves taper below a pixel in the dominant horizontal directions.
# double their width and undo only the side-width y compression; their curved
# centerlines, depth, count and materials remain the exact diagnostic baseline.
mesh = leaf.data.copy()
mesh.name = 'submerged curved leaves with visible projected widths'
leaf.data = mesh
world_to_local = leaf.matrix_world.inverted()
print('DEPTH CHECK',min(v.co.z for v in mesh.vertices),max(v.co.z for v in mesh.vertices),
      max(abs(mesh.vertices[i].co.z-mesh.vertices[i+1].co.z) for i in range(0,len(mesh.vertices),2)),flush=True)
for i in range(0,len(mesh.vertices),2):
    a,b = mesh.vertices[i],mesh.vertices[i+1]
    wa,wb = leaf.matrix_world@a.co,leaf.matrix_world@b.co
    # saved float coordinates differ by up to 7.6e-6 across a pair at this scale.
    assert -.7 < wa.z < .09 and abs(wa.z-wb.z) < .00001
    pa,pb = world_to_camera_view(scene,scene.camera,wa),world_to_camera_view(scene,scene.camera,wb)
    cx,cy = (pa.x+pb.x)/2,(pa.y+pb.y)/2
    hx,hy = (pb.x-pa.x),(pb.y-pa.y)/.22
    a.co = world_to_local@at_depth(cx-hx,cy-hy,wa.z)
    b.co = world_to_local@at_depth(cx+hx,cy+hy,wb.z)
    na,nb = world_to_camera_view(scene,scene.camera,leaf.matrix_world@a.co),world_to_camera_view(scene,scene.camera,leaf.matrix_world@b.co)
    assert abs((na.x+nb.x)/2-cx) < .00001 and abs((na.y+nb.y)/2-cy) < .00001
    assert abs((nb.x-na.x)-2*(pb.x-pa.x)) < .00001
    assert abs((nb.y-na.y)-2*(pb.y-pa.y)/.22) < .00001
mesh.update()
for name,old in before.items():
    expected = (old[0],old[1],mesh.name,old[3]) if name == leaf.name else old
    assert descriptor(bpy.data.objects[name]) == expected,name
assert camera == (scene.camera.data.lens,descriptor(scene.camera))
assert lights == {obj.name:(obj.data.energy,tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True,packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True)
print('SAVED',output,'36 LEAVES; X WIDTH 2X, Y WIDTH 2/.22; CENTERS/DEPTH PRESERVED',flush=True)
