"""Build an editable Blender Temple and bake its browser textures.
Run with Blender --background --factory-startup --threads 4 --python this_file.
Geometry starts from the approved Three.js scene; outputs are isolated study assets.
"""
import bpy, bmesh, json, math, random, sys, time, hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/temple-study'; WORK=ROOT/'artifacts/temple-study'
OUT.mkdir(parents=True,exist_ok=True); WORK.mkdir(parents=True,exist_ok=True)
SIZE=1024 if '--draft' in sys.argv else 2048
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=24
scene.cycles.use_denoising=True; scene.render.threads_mode='FIXED'; scene.render.threads=4
scene.cycles.max_bounces=4; scene.cycles.diffuse_bounces=3
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.40,.49,.60,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.18
scene.view_settings.view_transform='AgX'

def material(name,colors,scale,rough=.83,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links
 p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 geom=n.new('ShaderNodeNewGeometry');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=scale;l.new(geom.outputs['Position'],mapping.inputs[0])
 noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1;noise.inputs['Detail'].default_value=4;noise.inputs['Roughness'].default_value=.72;l.new(mapping.outputs['Vector'],noise.inputs['Vector'])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.22;ramp.color_ramp.elements[0].color=(*colors[0],1);ramp.color_ramp.elements[1].position=.80;ramp.color_ramp.elements[1].color=(*colors[1],1);l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],p.inputs['Base Color'])
 fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=7;fine.inputs['Detail'].default_value=2;l.new(mapping.outputs['Vector'],fine.inputs['Vector'])
 bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.20;bump.inputs['Distance'].default_value=.014;l.new(fine.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
 return m
wood=material('aged cedar',[(.065,.026,.012),(.24,.125,.055)],(11,13,.85))
beam=material('cedar beams',[(.075,.032,.015),(.28,.155,.071)],(.8,12,15))
roof=material('smoked clay tile',[(.028,.036,.041),(.095,.115,.12)],(4,5,7),.77,.03)
brass=material('aged bronze',[(.12,.070,.020),(.31,.22,.082)],(8,8,8),.57,.62)
plaque=material('carved cedar plaque',[(.040,.016,.008),(.14,.063,.023)],(12,12,1))
objects=[]

def bevel(o,width=.035):
 mod=o.modifiers.new('soft worn arrises','BEVEL');mod.width=width;mod.segments=2;mod.limit_method='ANGLE'
 mod.angle_limit=.5
 bpy.context.view_layer.objects.active=o
 bpy.ops.object.modifier_apply(modifier=mod.name)
 for p in o.data.polygons:p.use_smooth=True
 mod=o.modifiers.new('weighted corner normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=40
 bpy.ops.object.modifier_apply(modifier=mod.name)

def mesh(name,verts,faces,mat,edge=0):
 data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update();o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.data.materials.append(mat);objects.append(o)
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.00001);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(data);bm.free()
 if edge:bevel(o,edge)
 return o

def box(name,location,dimensions,mat,edge=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=location);o=bpy.context.object;o.name=name;o.dimensions=dimensions;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);objects.append(o)
 if edge:bevel(o,edge)
 return o

def beam_between(name,a,b,width,depth,mat):
 a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(width,depth,(b-a).length),mat,.016);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o

# convert once: Blender Z up, with glTF's exporter returning the Three Y-up frame.
data=json.loads((WORK/'source-geometry.json').read_text())
for i,entry in enumerate(data['meshes']):
 p=entry['positions'];verts=[(p[j],-p[j+2],p[j+1]) for j in range(0,len(p),3)];idx=entry['indices'];faces=[idx[j:j+3] for j in range(0,len(idx),3)]
 tag=entry['name'];mat={'timber':wood,'post':beam,'roof':roof,'brass':brass,'plaque':plaque}[tag]
 obj=mesh(f'{tag}_{i:02}',verts,faces,mat,.025 if tag not in ('roof','plaque') else 0)
 # the old label was a flat texture; the new face gets physical cut lettering below.
 if tag=='roof':
  for poly in obj.data.polygons:poly.use_smooth=True

# roof caps follow the original corner-weighted curve, staying inside its outline.
def smooth(a,b,v):
 t=max(0,min(1,(v-a)/(b-a)));return t*t*(3-2*t)
def height(x,z,A,B,R,H,flare):
 cx=min(1,abs(x)/A);cz=min(1,abs(z)/B);t=min(1,max(max(0,(abs(x)-R)/max(A-R,.0001)),cz))
 return H*(1-t)**1.45+flare*H*smooth(.72,1,t)*(.52+.68*min(cx,cz))
roofs=[(0,-44,18.7,10.8,7.2,3.6,5.2,.48,.26),(0,-44,12.6,9.6,6.4,3.2,2.9,.40,.26),(-10.6,-42.6,10.4,5,4,1.4,1.9,.32,.26),(10.6,-42.6,10.4,5,4,1.4,1.9,.32,.26)]
for ri,(cx,cz,base,A,B,R,H,thick,flare) in enumerate(roofs):
 verts=[];faces=[];columns=round(2*(A-.18)/.46)
 for col in range(columns+1):
  x=-A+.18+(2*A-.36)*col/columns
  for side in (-1,1):
   start=len(verts);steps=24 if ri<2 else 14;slices=5
   for j in range(steps+1):
    z=side*(.06+(B-.18)*j/steps)
    for k in range(slices+1):
     angle=math.pi*k/slices;xx=x+math.cos(angle)*.065
     y=base+height(xx,z,A,B,R,H,flare)+.015+math.sin(angle)*.062
     verts.append((cx+xx,-(cz+z),y))
   for j in range(steps):
    for k in range(slices):
     a=start+j*(slices+1)+k;b=a+slices+1;faces.append((a,a+1,b+1,b))
 caps=mesh(f'half round roof caps {ri}',verts,faces,roof)
 for p in caps.data.polygons:p.use_smooth=True
 # exposed rafter tails give the roof a layered edge without enlarging its silhouette.
 for x in [(-A+.5)+j*.65 for j in range(int((2*A-1)/.65)+1)]:
  for side in (-1,1):
   z1=side*(B-1.5);z2=side*(B-.16)
   a=(cx+x,-(cz+z1),base+height(x,z1,A,B,R,H,flare)-thick-.12)
   b=(cx+x,-(cz+z2),base+height(x,z2,A,B,R,H,flare)-thick-.12)
   beam_between('exposed cedar rafter',a,b,.14,.18,beam)

# shallow plank relief and fitted peg ends catch light at the scale of the whole facade.
for w,cy,h,z in [(13.6,9.5,5,-39.895),(10,16.4,3.4,-40.995), (7.6,8.7,3.4,-39.995)]:
 centers=[0] if w!=7.6 else [-10.6,10.6]
 for center in centers:
  for j in range(int(w/.40)):
   x=center-w/2+(j+.5)*.4
   box('individual cedar boards',(x,-z,cy),(.387,.042,h-.08),wood,.006)
# windows stay in the browser, just forward of these planks; no duplicate paper or light sources.

# real inset numerals cut into a dedicated plaque insert.
insert=box('305 carved sign',(0,40.802,16.7),(1.67,.08,1.07),plaque,.018)
bpy.ops.object.text_add(location=(0,40.753,16.43),rotation=(math.pi/2,0,0));text=bpy.context.object;text.name='305 cut';text.data.body='305';text.data.align_x='CENTER';text.data.size=.68;text.data.extrude=.055;text.data.bevel_depth=.003
bpy.ops.object.convert(target='MESH');cutter=bpy.context.object
bpy.context.view_layer.objects.active=insert;mod=insert.modifiers.new('recessed studio number','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter
bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
# a muted bronze fill sits inside the cut, so the number reads in moonlight.
bpy.ops.object.text_add(location=(0,40.778,16.43),rotation=(math.pi/2,0,0))
letter=bpy.context.object;letter.name='305 recessed bronze fill';letter.data.body='305';letter.data.align_x='CENTER';letter.data.size=.68;letter.data.extrude=.004;letter.data.bevel_depth=.002
bpy.ops.object.convert(target='MESH');letter=bpy.context.object;letter.data.materials.append(brass);objects.append(letter)

# join before baking so the lightmap is shared, with one draw group per surface family.
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();model=bpy.context.object;model.name='Temple_quality'
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.006,margin_method='FRACTION');bpy.ops.object.mode_set(mode='OBJECT')
model.data.uv_layers.active.name='Atlas'

# bake only the building. a ground receiver and the original moon direction give restrained bounce.
ground=box('bake ground',(0,44,6.8),(42,27,.35),wood,0);objects.remove(ground)
world=scene.world
bpy.ops.object.light_add(type='SUN',location=(17,54,39));sun=bpy.context.object;sun.name='moon for bake';sun.data.energy=.45;sun.data.angle=.08;sun.data.color=(.58,.70,1)
sun.rotation_euler=(Vector((0,44,14))-sun.location).to_track_quat('-Z','Y').to_euler()
for x in [-5.6,-2.8,0,2.8,5.6]:
 bpy.ops.object.light_add(type='AREA',location=(x,39.73,9.6));light=bpy.context.object;light.data.energy=12;light.data.color=(1,.64,.32);light.data.shape='RECTANGLE';light.data.size=1.3;light.data.size_y=2.2
 light.rotation_euler=(math.pi/2,0,0)

for i, mat in enumerate(model.data.materials):
 if mat is None:model.data.materials[i]=plaque
materials=list(dict.fromkeys(model.data.materials))
def bake(name,kind,passes=None):
 image=bpy.data.images.new(name,width=SIZE,height=SIZE,alpha=False,float_buffer=kind=='DIFFUSE')
 if kind in ('AO','NORMAL','DIFFUSE'):image.colorspace_settings.name='Non-Color'
 nodes=[]
 for m in materials:
  node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;m.node_tree.nodes.active=node;nodes.append(node)
 bpy.ops.object.select_all(action='DESELECT');model.select_set(True);bpy.context.view_layer.objects.active=model
 scene.render.bake.margin=max(2,SIZE//512);scene.render.bake.use_clear=True
 kwargs={'type':kind}
 if passes:kwargs['pass_filter']=passes
 print('BAKING',name,flush=True);bpy.ops.object.bake(**kwargs)
 if kind=='DIFFUSE':
  # indirect light has no sharp detail. downsampling also averages bake noise.
  import numpy as np
  pixels=np.array(image.pixels[:],dtype=np.float32).reshape(SIZE,SIZE,4)
  pixels=pixels.reshape(SIZE//2,2,SIZE//2,2,4).mean(axis=(1,3))
  for axis in (0,1):
   pixels=(np.roll(pixels,1,axis)+pixels*2+np.roll(pixels,-1,axis))/4
  byte=bpy.data.images.new(name+' web',width=SIZE//2,height=SIZE//2,alpha=False,float_buffer=False)
  byte.colorspace_settings.name='Non-Color';byte.pixels.foreach_set(pixels.ravel());image=byte
 extension='.jpg' if kind in ('EMIT','AO') else '.png'
 image.filepath_raw=str(OUT/(name+extension));image.file_format='JPEG' if extension=='.jpg' else 'PNG';image.save()
 image.use_fake_user=True;image.pack()
 for m,node in zip(materials,nodes):m.node_tree.nodes.remove(node)
 return image

# emission bake records the authored albedo without baking the studio's illumination into it.
links=[]
for m in materials:
 n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');out=n.get('Material Output');em=n.new('ShaderNodeEmission');l.new(p.inputs['Base Color'].links[0].from_socket,em.inputs['Color']);l.new(em.outputs[0],out.inputs['Surface']);links.append(em)
color=bake('cedar-albedo','EMIT')
for m,em in zip(materials,links):
 n=m.node_tree.nodes;m.node_tree.links.new(n.get('Principled BSDF').outputs[0],n.get('Material Output').inputs['Surface']);n.remove(em)
normal=bake('cedar-normal','NORMAL')
ao=bake('temple-occlusion','AO')
# indirect only: browser lights retain control of the direct illumination and moving highlights.
lightmap=bake('temple-bounce','DIFFUSE',{'INDIRECT'})

# retain the complete procedural source and bake rig in an editable local file.
bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'temple-quality.blend'))
# glTF carries ordinary PBR maps; the separate lightmap is attached to uv2 by the study page.
for m in materials:
 n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
 for socket in ('Base Color','Normal'):
  for link in list(p.inputs[socket].links):l.remove(link)
 for image,socket in [(color,'Base Color')]:
  t=n.new('ShaderNodeTexImage');t.image=image;l.new(t.outputs['Color'],p.inputs[socket])
 t=n.new('ShaderNodeTexImage');t.image=normal;nm=n.new('ShaderNodeNormalMap');l.new(t.outputs['Color'],nm.inputs['Color']);l.new(nm.outputs['Normal'],p.inputs['Normal'])
 # exporter recognizes this named input as the standard glTF occlusion texture.
 group=bpy.data.node_groups.get('glTF Material Output')
 if not group:
  group=bpy.data.node_groups.new('glTF Material Output','ShaderNodeTree');group.interface.new_socket(name='Occlusion',in_out='INPUT',socket_type='NodeSocketFloat')
 g=n.new('ShaderNodeGroup');g.node_tree=group;t=n.new('ShaderNodeTexImage');t.image=ao;l.new(t.outputs['Color'],g.inputs['Occlusion'])
bpy.ops.object.select_all(action='DESELECT');model.select_set(True);bpy.context.view_layer.objects.active=model
bpy.ops.export_scene.gltf(filepath=str(OUT/'temple-quality.glb'),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_image_format='AUTO')
triangles=sum(len(p.vertices)-2 for p in model.data.polygons)
manifest={'source':'Blender 5.2 / approved Temple geometry','sourceCommit':'a505366','sourceGeometrySha256':hashlib.sha256((WORK/'source-geometry.json').read_bytes()).hexdigest(),'triangles':triangles,'materials':len(materials),'textureSize':SIZE,'lightmap':'temple-bounce.png','coordinateSystem':'three-y-up-world','bake':'Cycles 24 samples; tangent normal, ambient occlusion, indirect diffuse','glbBytes':(OUT/'temple-quality.glb').stat().st_size}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest),flush=True)
