"""Add broken stair-edge growth and taller wall planting to the saved study."""
from pathlib import Path
import random
import bpy
from mathutils import Vector
root=Path(__file__).resolve().parents[1]/'renders'
out=root/'cathedral-overgrown-cloud-v1.blend'
assert not out.exists(),out
bpy.ops.wm.open_mainfile(filepath=str(root/'cathedral-stone-grain-cloud-v1.blend'))
s=bpy.context.scene
before={o.name:(tuple(v for row in o.matrix_world for v in row),o.hide_render,o.data.name if o.data else None) for o in s.objects}
rng=random.Random(30591)
templates=[bpy.data.objects['thicket replacement plinth planting '+n] for n in ('020','038','063','054')]
meshes={}
for obj in templates:
 mesh=obj.data.copy();mesh.name='normalized overgrowth '+obj.name
 lo=Vector([min(v.co[i] for v in mesh.vertices) for i in range(3)])
 hi=Vector([max(v.co[i] for v in mesh.vertices) for i in range(3)])
 center=(lo+hi)*.5
 for v in mesh.vertices:
  v.co=Vector([(v.co[i]-center[i])/(hi[i]-lo[i]) for i in range(3)])
 mesh.update();meshes[obj.name]=mesh
collection=bpy.data.collections.new('irregular stair and wall growth');s.collection.children.link(collection)
added=[]
def crown(name,location,dimensions,angle):
 template=templates[len(added)%len(templates)]
 o=template.copy();o.data=meshes[template.name];o.name=name;collection.objects.link(o)
 o.location=location;o.rotation_euler=(0,0,angle);o.scale=dimensions;o.hide_render=False
 added.append(o)
# unequal gaps keep the ascent legible instead of forming two clipped hedges.
steps=sorted([o for o in s.objects if o.name.startswith('tread ')],key=lambda o:o.location.y)
assert len(steps)==150
for side,indices in [(-1,[7,12,29,43,47,69,83,101,117,129,135]),(1,[16,24,39,58,63,79,95,110,123,140])]:
 for j,index in enumerate(indices):
  step=steps[index];half=step.dimensions.x/2;top=step.location.z+step.dimensions.z/2
  width=rng.uniform(29,48);height=rng.uniform(19,35);depth=rng.uniform(32,58)
  crown(f'overgrown stair {side} {j:02}',(side*(half+width*.22),step.location.y,top+height*.22),(width,depth,height),rng.uniform(-.5,.5))
# taller pockets cross the cornice at different heights, leaving a small wall opening.
for j,(x,y,z,w,d,h) in enumerate([(-145,979,728,62,65,75),(-206,972,744,78,72,84),(-273,989,745,82,68,94),(-320,982,751,62,61,86),(141,978,733,58,58,66),(205,982,750,77,67,88),(266,974,762,86,78,96)]):
 crown(f'overgrown wall {j:02}',(x,y,z),(w,d,h),rng.uniform(-.6,.6))
bpy.context.view_layer.update()
for name,desc in before.items():
 o=bpy.data.objects[name];assert desc==(tuple(v for row in o.matrix_world for v in row),o.hide_render,o.data.name if o.data else None),name
s['overgrowth_added']=','.join(o.name for o in added)
s.render.filepath='//'+out.stem+'.png'
bpy.ops.file.pack_all();assert not bpy.utils.blend_paths(absolute=True,packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
print('SAVED',out,'ADDED',len(added),'existing objects unchanged',flush=True)
