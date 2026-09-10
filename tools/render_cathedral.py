"""A complete offline scene: reference composition, physical lighting and foliage."""
import bpy, math, random, sys
from pathlib import Path
from mathutils import Vector
from mathutils.noise import noise_vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'renders';OUT.mkdir(exist_ok=True)
random.seed(1707)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=True
scene.cycles.max_bounces=7;scene.cycles.transparent_max_bounces=6
scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'cathedral-still.png')
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.25,.36,.32,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.18
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.3
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
stairmat=mat('damp basalt treads',(.017,.026,.022),(.065,.084,.067),6,.025,.75)
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
mon=instance('limestone monument',assets['monument'],(0,120,34),material=stone)
box('landing',(0,119,32.5),(19,14,3),stairmat,.08)
box('dark entrance',(0,114.68,36.2),(3.5,.15,4.4),bark)
# a small dark inset makes the actual engraved letters legible at this distance.
font=bpy.data.curves.new('305 engraved shadow','FONT');font.body='305';font.size=4.7;font.align_x='CENTER';font.extrude=.002
letter=bpy.data.objects.new('305',font);scene.collection.objects.link(letter);letter.location=(0,114.75,44);letter.rotation_euler=(math.pi/2,0,0);font.materials.append(stairmat)
for i in range(144):
 h=(i+1)*34/144;y=18+(i+.5)*96/144;w=10.8-i/144*2.6
 box('tread %03d'%i,(0,y,h/2),(w,96/144+.01,h),stairmat,.018)
# ground rolls into banks, leaving a submerged bed across the foreground.
def height(x,y):
 rise=max(0,min(1,(y-18)/96))*34
 bank=max(0,min(1,(abs(x)-5)/8));bank=bank*bank*(3-2*bank)
 basin=max(0,1-((x/34)**2+((y+2)/37)**2))
 return rise*bank+bank*(1.1+noise_vector(Vector((x*.07,y*.07,1))).z*1.8)-2.4*basin
verts=[];faces=[];N=150
for j in range(N+1):
 y=-80+j*310/N
 for i in range(N+1):
  x=-135+i*270/N;verts.append((x,y,height(x,y)))
for j in range(N):
 for i in range(N):
  a=j*(N+1)+i;faces.append((a,a+1,a+N+2,a+N+1))
mesh=bpy.data.meshes.new('forest floor');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('moss banks',mesh);scene.collection.objects.link(o);o.data.materials.append(moss)
for p in mesh.polygons:p.use_smooth=True
# the principal trunks frame a deep opening, rather than filling it with poles.
trees=[(-22,20,1.05),(23,25,1.1),(-33,48,.85),(34,65,.95),(-23,89,.67),(25,98,.72)]
for i in range(42):trees.append(((1 if i%2 else -1)*(25+random.random()*66),35+random.random()*200,.4+random.random()*.7))
for i,(x,y,scale) in enumerate(trees):
 tr=instance('ancient cedar %02d'%i,assets['rooted_trunk_'+str(i%3)],(x,y,height(x,y)-.5),(scale,scale,.9+random.random()*.45),bark);tr.rotation_euler.z=random.random()*math.tau
# foliage has actual cupped leaves and branch structure, not transparent sheets.
leafm=[]
for i in range(5):
 m=bpy.data.materials.new('leaf green '+str(i));m.diffuse_color=(.03+i*.009,.085+i*.017,.015+i*.005,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=m.diffuse_color;p.inputs['Roughness'].default_value=.56;p.inputs['Subsurface Weight'].default_value=.055
 leafm.append(m)
lv=[];lf=[];lm=[]
def leaf(pos,direction,size):
 forward=direction.normalized();side=forward.cross(Vector((0,0,1)))
 if side.length<.1:side=Vector((1,0,0))
 side.normalize();up=side.cross(forward).normalized();base=len(lv)
 lv.append(tuple(pos+forward*size*.46+up*size*.10))
 for k in range(10):
  a=k/10*math.tau;lv.append(tuple(pos+forward*(.5+.5*math.cos(a))*size+side*math.sin(a)*size*.29))
 for k in range(10):lf.append((base,base+1+k,base+1+(k+1)%10));lm.append(random.randrange(5))
centers=[]
for i in range(280):
 y=10+random.random()*140;x=(1 if i%2 else -1)*(7+random.random()*35);r=2+random.random()*4
 centers.append((Vector((x,y,height(x,y)+r*.7)),r))
for c,r in centers:
 for j in range(500):
  v=Vector((random.uniform(-1,1),random.uniform(-1,1),random.uniform(-.7,.7))).normalized()
  p=c+Vector((v.x*r,v.y*r,v.z*r*.75))*random.uniform(.5,1.05)
  leaf(p,Vector((v.x,v.y,random.uniform(-.2,.9))),random.uniform(.35,.9))
# leaf clusters follow substantial boughs so the canopy reads as a living structure.
def branch(start,end,radius):
 delta=end-start
 bpy.ops.mesh.primitive_cone_add(vertices=9,radius1=radius,radius2=radius*.18,depth=delta.length,location=(start+end)/2)
 o=bpy.context.object;o.name='canopy bough';o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();o.data.materials.append(bark)
for i,(x,y,scale) in enumerate(trees):
 for k in range(6):
  a=random.random()*math.tau;z=82+random.random()*34
  start=Vector((x,y,z));end=start+Vector((math.cos(a)*16*scale,math.sin(a)*16*scale,random.uniform(1,8)))
  if abs(end.x)<16:end.x=16 if x>0 else -16
  branch(start,end,.65*scale)
  for j in range(240):
   v=Vector((random.uniform(-1,1),random.uniform(-1,1),random.uniform(-.5,.5)))
   leaf(end+v*random.uniform(2,7)*scale,Vector((v.x,v.y,random.uniform(.1,.8))),random.uniform(.7,1.5))
mesh=bpy.data.meshes.new('individual leaves');mesh.from_pydata(lv,[],lf);mesh.update();o=bpy.data.objects.new('layered foliage',mesh);scene.collection.objects.link(o)
for m in leafm:mesh.materials.append(m)
for i,p in enumerate(mesh.polygons):p.material_index=lm[i];p.use_smooth=True
# dark branches make the crowns feel rooted rather than suspended.
for c,r in centers:
 bpy.ops.mesh.primitive_cone_add(vertices=7,radius1=.16,radius2=.045,depth=r*1.2,location=(c.x,c.y,c.z-r*.5));bpy.context.object.data.materials.append(bark)
water=bpy.data.materials.new('deep green clear water');water.use_nodes=True;p=water.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.055,.13,.085,1);p.inputs['Roughness'].default_value=.075;p.inputs['IOR'].default_value=1.333;p.inputs['Transmission Weight'].default_value=.8
n=water.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=3;n.inputs['Detail'].default_value=2
b=water.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.14;b.inputs['Distance'].default_value=.07;water.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);water.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,-4,.03));o=bpy.context.object;o.name='pond';o.scale=(34,34,1);o.data.materials.append(water)
padmat=mat('lily pad waxy surface',(.025,.09,.012),(.16,.28,.045),14,.006,.4)
for i in range(65):
 x=random.choice([-1,1])*random.uniform(8,26);y=random.uniform(-26,12)
 if i>57:x=random.uniform(-8,8)
 r=random.uniform(.22,.7);rot=random.random()*math.tau;vs=[(x,y,.075)]
 for j in range(31):
  a=rot+.15+j/30*(math.tau-.38);vs.append((x+math.cos(a)*r,y+math.sin(a)*r,.075+.025*math.sin(j/30*math.pi)))
 fs=[(0,j,j+1) for j in range(1,31)]
 me=bpy.data.meshes.new('notched pad');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('lily pad',me);scene.collection.objects.link(o);me.materials.append(padmat)
em=bpy.data.materials.new('warm lamp glass');em.use_nodes=True;p=em.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.7,.28,.07,1);p.inputs['Emission Color'].default_value=(1,.42,.12,1);p.inputs['Emission Strength'].default_value=4
for i in range(14):
 t=i/13;y=20+t*92;z=(y-18)*34/96
 for side in [-1,1]:
  x=side*(5.9-t*1.3)
  box('lamp post',(x,y,z+.65),(.095,.095,1.3),metal)
  box('lamp hood',(x,y,z+1.35),(.7,.58,.075),metal,.025)
  box('amber lamp',(x,y,z+1.27),(.32,.25,.09),em)
  d=bpy.data.lights.new('lamp pool','POINT');d.energy=24;d.color=(1,.48,.19);d.shadow_soft_size=.25;o=bpy.data.objects.new('lamp pool',d);scene.collection.objects.link(o);o.location=(x,y,z+1.2)
area('entrance warmth',(0,111,38),(0,119,39),600,3,(1,.52,.27))
area('overcast opening',(-25,60,155),(0,80,15),180000,95,(.76,.86,.79))
area('limestone soft light',(-16,77,103),(0,120,75),45000,45,(.83,.88,.81))
# a real participating medium joins the layers of trees and softens the distance.
vol=bpy.data.materials.new('forest atmosphere');vol.use_nodes=True;ns=vol.node_tree.nodes;ns.clear();v=ns.new('ShaderNodeVolumePrincipled');v.inputs['Density'].default_value=.0016;v.inputs['Color'].default_value=(.54,.65,.60,1);v.inputs['Anisotropy'].default_value=.35;out=ns.new('ShaderNodeOutputMaterial');vol.node_tree.links.new(v.outputs['Volume'],out.inputs['Volume'])
box('atmosphere',(0,80,100),(360,400,220),vol)
bpy.ops.object.camera_add(location=(0,-35,3.0));camera=bpy.context.object;camera.name='reference camera';camera.data.lens=40;camera.data.clip_end=800;aim(camera,(0,110,37));scene.camera=camera
scene.render.film_transparent=False
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cathedral-cinematic.blend'))
print('Scene ready; rendering',flush=True)
bpy.ops.render.render(write_still=True)
