"""Back the fine wall branches with smaller existing foliage masses."""
from pathlib import Path
import bpy
from mathutils import Vector
root=Path(__file__).resolve().parents[1]/'renders';out=root/'cathedral-overgrown-backed-cloud-v1.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(root/'cathedral-overgrown-connected-cloud-v1.blend'))
s=bpy.context.scene
originals=[bpy.data.objects['plinth planting '+n] for n in ('020','038','063','054')]
meshes={}
for t in originals:
 mesh=t.data.copy();lo=Vector([min(v.co[i] for v in mesh.vertices) for i in range(3)]);hi=Vector([max(v.co[i] for v in mesh.vertices) for i in range(3)]);center=(lo+hi)/2
 for v in mesh.vertices:v.co=Vector([(v.co[i]-center[i])/(hi[i]-lo[i]) for i in range(3)])
 mesh.update();meshes[t.name]=mesh
walls=sorted([o for o in s.objects if o.name.startswith('overgrown wall ')],key=lambda o:o.name);assert len(walls)==7
for i,wall in enumerate(walls):
 t=originals[i%4];o=t.copy();o.data=meshes[t.name];o.name=f'wall foliage backing {i:02}';s.collection.objects.link(o);o.hide_render=False
 o.location=wall.location+Vector((0,-10,-22));o.rotation_euler=wall.rotation_euler.copy();o.scale=(wall.scale.x*.93,wall.scale.y,wall.scale.z*.85)
s.render.filepath='//'+out.stem+'.png';bpy.ops.file.pack_all();assert not bpy.utils.blend_paths(absolute=True,packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);print('SAVED',out,flush=True)
