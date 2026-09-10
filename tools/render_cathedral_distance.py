"""A complete offline scene: reference composition, physical lighting and foliage."""
import bpy, math, random, sys
from pathlib import Path
from mathutils import Vector
from mathutils.noise import noise_vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'renders';OUT.mkdir(exist_ok=True)
random.seed(1707)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.cycles.max_bounces=7;scene.cycles.transparent_max_bounces=6
scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'cathedral-distance-study.png')
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.25,.36,.32,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-1.0
# CPU avoids a Metal kernel readiness stall on the current render host.
scene.cycles.device="CPU"

def mat(name,low,high,scale=5,bump=.1,rough=.85,stretch=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=rough
 tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=scale;tex.inputs['Detail'].default_value=5;tex.inputs['Roughness'].default_value=.75
 coord=n.new('ShaderNodeTexCoord')
 if stretch:
  v=n.new('ShaderNodeVectorMath');v.operation='MULTIPLY';v.inputs[1].default_value=stretch;l.new(coord.outputs['Object'],v.inputs[0]);l.new(v.outputs[0],tex.inputs['Vector'])
 else:l.new(coord.outputs['Object'],tex.inputs['Vector'])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=(*low,1);ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(*high,1)
 l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
 bn=n.new('ShaderNodeBump');bn.inputs['Strength'].default_value=.6;bn.inputs['Distance'].default_value=bump;l.new(tex.outputs['Fac'],bn.inputs['Height']);l.new(bn.outputs['Normal'],p.inputs['Normal'])
 return m
bark=mat('damp deeply furrowed bark',(.009,.017,.011),(.075,.092,.05),3,.23,.94,(2,2,.13))
moss=mat('moss and forest earth',(.008,.018,.006),(.045,.087,.025),3,.14)
stone=mat('weathered pale limestone',(.23,.27,.24),(.56,.59,.51),2.5,.045)
stairmat=mat('damp basalt treads',(.017,.026,.022),(.10,.13,.11),6,.025,.82)
metal=mat('aged bronze lamps',(.04,.026,.012),(.12,.085,.035),8,.012,.38)
with bpy.data.libraries.load(str(ROOT/'assets/cathedral/cathedral-trunks.blend'),link=False) as (src,dst):dst.objects=[n for n in src.objects if n=='monument' or n.startswith('rooted_trunk')]
assets={o.name:o for o in dst.objects}
def instance(name,source,loc,scale=(1,1,1),material=None):
 o=bpy.data.objects.new(name,source.data.copy() if material else source.data);scene.collection.objects.link(o);o.location=loc;o.scale=scale
 if material:o.data.materials.clear();o.data.materials.append(material)
 return o
def box(name,loc,scale,material,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 if bevel:m=o.modifiers.new('worn corners','BEVEL');m.width=bevel;m.segments=2
 return o
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,target,energy,size,color):
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;aim(o,target);return o
# rebuild the silhouette without the old large inscription baked into the mesh.
outline=[(-7,0),(7,0),(7,78),(2.6,78),(2.6,25)]
for j in range(1,17):
 a=-math.pi*j/16;outline.append((2.6*math.cos(a),25+2.6*math.sin(a)))
outline += [(-2.6,73),(-7,73)]
vs=[(x,y,z) for y in [0,-5.2] for x,z in outline];n=len(outline)
fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
me=bpy.data.meshes.new('uninscribed silhouette');me.from_pydata(vs,[],fs);me.update()
import bmesh
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
mon=bpy.data.objects.new('limestone monument',me);scene.collection.objects.link(mon);mon.location=(0,346,150);mon.scale=(3.9,3.08,300/78);me.materials.append(stone)
b=mon.modifiers.new('soft limestone edges','BEVEL');b.width=.09;b.segments=3
box('landing',(0,340,147.5),(66,20,5),stairmat,.08)
box('dark entrance',(0,329.98,156),(25,.15,12),bark)
# a small dark inset makes the actual engraved letters legible at this distance.
font=bpy.data.curves.new('305 engraved shadow','FONT');font.body='305';font.size=28;font.align_x='CENTER';font.extrude=.002
letter=bpy.data.objects.new('305',font);scene.collection.objects.link(letter);letter.location=(0,329.95,184);letter.rotation_euler=(math.pi/2,0,0);font.materials.append(stairmat)
for i in range(150):
 h=(i+1);y=(i+.5)*330/150;w=58-i/150*11
 box('tread %03d'%i,(0,y,h/2),(w,330/150+.01,h),stairmat,.018)
# ground rolls into banks, leaving a submerged bed across the foreground.
def height(x,y):
 rise=max(0,min(1,y/330))*150
 bank=max(0,min(1,(abs(x)-23)/20));bank=bank*bank*(3-2*bank)
 return rise*bank-3+noise_vector(Vector((x*.014,y*.014,2))).z*5*bank
verts=[];faces=[];N=90
for j in range(N+1):
 y=-360+j*1160/N
 for i in range(N+1):
  x=-600+i*1200/N;verts.append((x,y,height(x,y)))
for j in range(N):
 for i in range(N):
  a=j*(N+1)+i;faces.append((a,a+1,a+N+2,a+N+1))
mesh=bpy.data.meshes.new('simple forest banks');mesh.from_pydata(verts,[],faces);mesh.update()
o=bpy.data.objects.new('simple forest banks',mesh);scene.collection.objects.link(o);mesh.materials.append(moss)
for p in mesh.polygons:p.use_smooth=True
# only two trunks establish the giant scale; the smaller forest remains a blockout.
for i,(x,y,r) in enumerate([(-175,155,90),(200,280,115)]):
 source=assets['rooted_trunk_'+str(i)]
 xs=[v.co.x for v in source.data.vertices];zs=[v.co.z for v in source.data.vertices]
 tr=instance('colossal trunk '+str(i),source,(x,y,height(x,y)),(r*2/(max(xs)-min(xs)),r*2/(max(xs)-min(xs)),900/(max(zs)-min(zs))),bark)
 tr.rotation_euler.z=i*.8
# a few joined crown lobes suggest ordinary trees without individual leaves.
mesh=bpy.data.meshes.new('simple clustered crown');bm=bmesh.new()
for k in range(11):
 a=k*2.39996;r=.62*math.sqrt(k/10)
 c=Vector((math.cos(a)*r,math.sin(a)*r,.32*(1-r)))
 result=bmesh.ops.create_icosphere(bm,subdivisions=2,radius=.43)
 for v in result['verts']:
  v.co*=1+noise_vector(v.co*8+Vector((k,0,0))).x*.16
  v.co+=c
bm.to_mesh(mesh);bm.free()
core=bpy.data.objects.new('simplified canopy template',mesh);scene.collection.objects.link(core)
for p in core.data.polygons:p.use_smooth=True
core.data.materials.append(mat('blockout canopy',(.012,.029,.016),(.08,.13,.055),1,.2))
core.hide_render=True
crown_specs=[]
for i in range(6500):
 y=random.uniform(-35,650);x=random.choice([-1,1])*random.uniform(38,490)
 if abs(x)<(31-y/330*5)+8:continue
 r=random.uniform(5,12)
 z=height(x,y)+r*.7+max(0,abs(x)-70)*.08
 crown_specs.append((i,(x,y,z),(r,r,r*1.1),(0,0,random.random()*math.tau)))
water=bpy.data.materials.new('deep green clear water');water.use_nodes=True;p=water.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.055,.13,.085,1);p.inputs['Roughness'].default_value=.075;p.inputs['IOR'].default_value=1.333;p.inputs['Transmission Weight'].default_value=.8
n=water.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=3;n.inputs['Detail'].default_value=2
b=water.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.14;b.inputs['Distance'].default_value=.07;water.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);water.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,-130,.03));o=bpy.context.object;o.name='pond';o.scale=(350,350,1);o.data.materials.append(water)
padmat=mat('lily pad waxy surface',(.025,.09,.012),(.16,.28,.045),14,.006,.4)
for i in range(65):
 x=random.choice([-1,1])*random.uniform(15,140);y=random.uniform(-160,-5)
 if i>57:x=random.uniform(-8,8)
 r=random.uniform(.22,.7);rot=random.random()*math.tau;vs=[(x,y,.075)]
 for j in range(31):
  a=rot+.15+j/30*(math.tau-.38);vs.append((x+math.cos(a)*r,y+math.sin(a)*r,.075+.025*math.sin(j/30*math.pi)))
 fs=[(0,j,j+1) for j in range(1,31)]
 me=bpy.data.meshes.new('notched pad');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('lily pad',me);scene.collection.objects.link(o);me.materials.append(padmat)
em=bpy.data.materials.new('warm lamp glass');em.use_nodes=True;p=em.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.7,.28,.07,1);p.inputs['Emission Color'].default_value=(1,.42,.12,1);p.inputs['Emission Strength'].default_value=4
for i in range(24):
 t=i/23;y=3+t*324;z=y*150/330
 for side in [-1,1]:
  x=side*(30-t*5.5)
  box('lamp post',(x,y,z+.65),(.095,.095,1.3),metal)
  box('lamp hood',(x,y,z+1.35),(.7,.58,.075),metal,.025)
  box('amber lamp',(x,y,z+1.27),(.32,.25,.09),em)
  d=bpy.data.lights.new('lamp pool','POINT');d.energy=24;d.color=(1,.48,.19);d.shadow_soft_size=.25;o=bpy.data.objects.new('lamp pool',d);scene.collection.objects.link(o);o.location=(x,y,z+1.2)
area('entrance warmth',(0,320,160),(0,335,160),3500,12,(1,.52,.27))
def soft(name,loc,energy,size,color):
 d=bpy.data.lights.new(name,'POINT');d.energy=energy;d.shadow_soft_size=size;d.color=color
 o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc
soft('open sky',(-100,80,650),2200000,250,(.76,.85,.88))
soft('stone light',(-90,250,440),320000,110,(.84,.89,.86))
soft('pond opening',(-80,-160,170),250000,120,(.73,.86,.77))
vol=bpy.data.materials.new('distance haze');vol.use_nodes=True;ns=vol.node_tree.nodes;ns.clear()
v=ns.new('ShaderNodeVolumePrincipled');v.inputs['Density'].default_value=.00065;v.inputs['Color'].default_value=(.48,.59,.63,1);v.inputs['Anisotropy'].default_value=.2
out=ns.new('ShaderNodeOutputMaterial');vol.node_tree.links.new(v.outputs['Volume'],out.inputs['Volume'])
box('atmosphere',(0,500,500),(1800,1800,1300),vol)
bpy.ops.object.camera_add(location=(0,-240,36));camera=bpy.context.object;camera.name='distant reference camera';camera.data.lens=35.518;camera.data.clip_end=6000
camera.rotation_euler=(math.pi/2+.226,0,0);scene.camera=camera
# link distant crowns after primitive construction to avoid repeated scene updates.
for idx,loc,scale,rot in crown_specs:
 o=bpy.data.objects.new('canopy lobe %03d'%idx,core.data);scene.collection.objects.link(o);o.location=loc;o.scale=scale;o.rotation_euler=rot
# metres: architecture is monumental, while ordinary crowns stay small beside it.
# the camera relationship was solved above; this unit conversion preserves it.
for o in scene.objects:
 o.location*=3;o.scale*=3
 if o.type=='LIGHT':
  o.data.energy*=9
  if o.data.type=='POINT':o.data.shadow_soft_size*=3
  elif o.data.type=='AREA':o.data.size*=3
v.inputs['Density'].default_value/=3
scene.view_settings.exposure=.1
from bpy_extras.object_utils import world_to_camera_view
bpy.context.view_layer.update()
for name,point,target in [('tower top',(0,990,1350),.92),('tower base',(0,990,450),.47),('stair foot',(0,0,0),.11)]:
 projected=world_to_camera_view(scene,camera,Vector(point))
 print(name,tuple(projected),flush=True)
 assert abs(projected.y-target)<.015,(name,projected.y,target)
scene.render.film_transparent=False
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cathedral-distance-study.blend'))
print('Scene ready; rendering',flush=True)
bpy.ops.render.render(write_still=True)
