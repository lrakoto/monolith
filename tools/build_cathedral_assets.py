"""Build reusable rooted trunks in Blender, exporting compact Three.js geometry."""
import bpy, math, json, random, struct
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parents[1]/'assets'/'cathedral'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
objects=[]
for variant in range(3):
 random.seed(305+variant);verts=[];faces=[]
 rings=42;sides=48
 for j in range(rings+1):
  u=j/rings;y=u*135
  for k in range(sides):
   a=k/sides*math.tau
   roots=(max(0,math.cos(a*7+variant))**10)*3.6*math.exp(-u*32)
   r=4.8*(1-.63*u)+1.8*math.exp(-u*16)+roots
   r*=1+.07*math.sin(a*13+.3*math.sin(u*9))+.035*math.cos(a*23+u*5)
   verts.append((r*math.cos(a)+math.sin(u*3+variant)*u*2,r*math.sin(a)+math.cos(u*4+variant)*u*1.2,y))
 for j in range(rings):
  for k in range(sides):
   a=j*sides+k;b=j*sides+(k+1)%sides
   faces.append((a,b,b+sides,a+sides))
 mesh=bpy.data.meshes.new('fluted_bark');mesh.from_pydata(verts,[],faces);mesh.update()
 obj=bpy.data.objects.new('rooted_trunk_'+str(variant),mesh);bpy.context.collection.objects.link(obj)
 bpy.context.view_layer.objects.active=obj;obj.select_set(True)
 for poly in mesh.polygons:poly.use_smooth=True
 bevel=obj.modifiers.new('soft bark shoulders','BEVEL');bevel.width=.04;bevel.segments=2
 # keep the mesh light; the radial flutes carry silhouette while textures carry grain.
 uv=mesh.uv_layers.new(name='Bark')
 for poly in mesh.polygons:
  ks=[mesh.loops[i].vertex_index%sides for i in poly.loop_indices]
  seam=0 in ks and sides-1 in ks
  for li in poly.loop_indices:
   vi=mesh.loops[li].vertex_index;k=vi%sides
   uv.data[li].uv=((1 if seam and k==0 else k/sides)*3,vi//sides/rings)
 objects.append(obj);obj.select_set(False)
# the monument shares the reference's unequal prongs and round-bottom slot.
outline=[(-7,0),(7,0),(7,78),(2.6,78),(2.6,25)]
for j in range(1,17):
 a=-math.pi*j/16
 outline.append((2.6*math.cos(a),25+2.6*math.sin(a)))
outline += [(-2.6,73),(-7,73)]
verts=[(x,y,z) for y in [0,-5.2] for x,z in outline];n=len(outline)
faces=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]
faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
mesh=bpy.data.meshes.new('monument');mesh.from_pydata(verts,[],faces);mesh.update()
obj=bpy.data.objects.new('monument',mesh);bpy.context.collection.objects.link(obj)
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
# recalculate winding before beveling the silhouette.
import bmesh
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free()
bevel=obj.modifiers.new('worn arris','BEVEL');bevel.width=.11;bevel.segments=3
bpy.ops.object.modifier_apply(modifier=bevel.name)
font=bpy.data.curves.new('inscription','FONT');font.body='305';font.size=4.7;font.align_x='CENTER';font.extrude=.35;font.resolution_u=4
text=bpy.data.objects.new('engraving cutter',font);bpy.context.collection.objects.link(text)
text.location=(0,-5.0,10);text.rotation_euler=(math.pi/2,0,0)
bpy.ops.object.select_all(action='DESELECT');text.select_set(True);bpy.context.view_layer.objects.active=text;bpy.ops.object.convert(target='MESH')
bpy.context.view_layer.objects.active=obj
cut=obj.modifiers.new('carved 305','BOOLEAN');cut.operation='DIFFERENCE';cut.object=text;bpy.ops.object.modifier_apply(modifier=cut.name)
bpy.data.objects.remove(text,do_unlink=True);objects.append(obj)

# editable source travels with the scene, so asset refinements are repeatable.
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cathedral-trunks.blend'))
result=[]
for obj in objects:
 evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh();mesh.calc_loop_triangles()
 pos=[];normal=[];uvs=[]
 for tri in mesh.loop_triangles:
  for li in tri.loops:
   v=mesh.vertices[mesh.loops[li].vertex_index];p=v.co;n=mesh.corner_normals[li].vector;uv=mesh.uv_layers.active.data[li].uv if mesh.uv_layers.active else Vector((p.x/14,p.z/78))
   pos.extend([round(p.x,4),round(p.z,4),round(-p.y,4)])
   normal.extend([round(n.x,5),round(n.z,5),round(-n.y,5)])
   uvs.extend([round(uv.x,5),round(uv.y,5)])
 result.append({'name':obj.name,'position':pos,'normal':normal,'uv':uvs})
 evaluated.to_mesh_clear()
packed=bytearray();catalog=[]
for item in result:
 unique={};vertices=[];indices=[]
 for i in range(len(item['position'])//3):
  row=tuple(item['position'][i*3:i*3+3]+item['normal'][i*3:i*3+3]+item['uv'][i*2:i*2+2])
  if row not in unique:unique[row]=len(vertices);vertices.append(row)
  indices.append(unique[row])
 record={'name':item['name'],'offset':len(packed),'vertices':len(vertices),'indices':len(indices)}
 for row in vertices:packed.extend(struct.pack('<8f',*row))
 packed.extend(struct.pack('<'+'I'*len(indices),*indices));catalog.append(record)
(OUT/'geometry.bin').write_bytes(packed)
(OUT/'geometry.json').write_text(json.dumps(catalog,separators=(',',':')))
print('exported',sum(len(o['position'])//9 for o in result),'triangles')
