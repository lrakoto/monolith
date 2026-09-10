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
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'cathedral-proportions.png')
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.25,.36,.32,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.18
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
mon=bpy.data.objects.new('limestone monument',me);scene.collection.objects.link(mon);mon.location=(0,240,100);mon.scale=(2.2,2.2,2.45);me.materials.append(stone)
b=mon.modifiers.new('soft limestone edges','BEVEL');b.width=.09;b.segments=3
box('landing',(0,234,97.5),(42,18,5),stairmat,.08)
box('dark entrance',(0,228.48,104),(15,.15,8),bark)
# a small dark inset makes the actual engraved letters legible at this distance.
font=bpy.data.curves.new('305 engraved shadow','FONT');font.body='305';font.size=16;font.align_x='CENTER';font.extrude=.002
letter=bpy.data.objects.new('305',font);scene.collection.objects.link(letter);letter.location=(0,228.48,118);letter.rotation_euler=(math.pi/2,0,0);font.materials.append(stairmat)
for i in range(150):
 h=(i+1)*100/150;y=18+(i+.5)*210/150;w=28-i/150*4
 box('tread %03d'%i,(0,y,h/2),(w,210/150+.01,h),stairmat,.018)
# ground rolls into banks, leaving a submerged bed across the foreground.
def height(x,y):
 rise=max(0,min(1,(y-18)/210))*100
 bank=max(0,min(1,(abs(x)-12)/12));bank=bank*bank*(3-2*bank)
 basin=max(0,1-((x/90)**2+((y+28)/90)**2))
 return rise*bank+bank*(1.1+noise_vector(Vector((x*.07,y*.07,1))).z*1.8)-2.4*basin
verts=[];faces=[];N=190
for j in range(N+1):
 y=-190+j*650/N
 for i in range(N+1):
  x=-220+i*440/N;verts.append((x,y,height(x,y)))
for j in range(N):
 for i in range(N):
  a=j*(N+1)+i;faces.append((a,a+1,a+N+2,a+N+1))
mesh=bpy.data.meshes.new('forest floor');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('moss banks',mesh);scene.collection.objects.link(o);o.data.materials.append(moss)
for p in mesh.polygons:p.use_smooth=True
# the principal trunks frame a deep opening, rather than filling it with poles.
# distant stands merge into walls; no single near trunk dominates the composition.
trees=[]
for i in range(100):
 y=60+random.random()*340;x=random.choice([-1,1])*(45+random.random()*95)
 trees.append((x,y,random.uniform(.38,.85)))
for i,(x,y,scale) in enumerate(trees):
 tr=instance('ancient cedar %02d'%i,assets['rooted_trunk_'+str(i%3)],(x,y,height(x,y)-.5),(scale,scale,1.6+random.random()*.65),bark);tr.rotation_euler.z=random.random()*math.tau
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
for i in range(470):
 y=12+random.random()*340;x=random.choice([-1,1])*(17+random.random()*120);r=random.uniform(4,10)
 centers.append((Vector((x,y,height(x,y)+r*.65)),r))
# overlapping crowns build a forest silhouette at landscape scale.
for i in range(220):
 y=random.uniform(85,410);x=random.choice([-1,1])*random.uniform(58,145);r=random.uniform(9,19)
 centers.append((Vector((x,y,height(x,y)+random.uniform(30,185))),r))
for c,r in centers:
 for j in range(470):
  v=Vector((random.uniform(-1,1),random.uniform(-1,1),random.uniform(-.7,.7))).normalized()
  p=c+Vector((v.x*r,v.y*r,v.z*r*.75))*random.uniform(.5,1.05)
  leaf(p,Vector((v.x,v.y,random.uniform(-.2,.9))),random.uniform(.4,1.0))
# shaded inner crowns join the fine leaves into connected masses at this distance.
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1)
core=bpy.context.object;core.name='crown template'
for v in core.data.vertices:
 v.co *= 1+noise_vector(v.co*7).x*.4
for p in core.data.polygons:p.use_smooth=True
crownmat=mat('dense fine canopy',(.008,.022,.007),(.055,.10,.035),9,.65,.95)
core.data.materials.append(crownmat);core.hide_render=True
crown_specs=[]
for idx,(c,r) in enumerate(centers):
 for k in range(18):
  angle=k*2.39996;rr=r*math.sqrt((k+.5)/18)*.83
  offset=Vector((math.cos(angle)*rr,math.sin(angle)*rr,random.uniform(-.24,.24)*r))
  size=r*random.uniform(.21,.36)
  crown_specs.append((idx,c+offset,(size,size,size*.7),(random.random(),random.random(),random.random())))
mesh=bpy.data.meshes.new('individual leaves');mesh.from_pydata(lv,[],lf);mesh.update();o=bpy.data.objects.new('layered foliage',mesh);scene.collection.objects.link(o)
for m in leafm:mesh.materials.append(m)
for i,p in enumerate(mesh.polygons):p.material_index=lm[i];p.use_smooth=True
# dark branches make the crowns feel rooted rather than suspended.
for c,r in centers:
 bpy.ops.mesh.primitive_cone_add(vertices=7,radius1=.16,radius2=.045,depth=r*1.2,location=(c.x,c.y,c.z-r*.5));bpy.context.object.data.materials.append(bark)
water=bpy.data.materials.new('deep green clear water');water.use_nodes=True;p=water.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.055,.13,.085,1);p.inputs['Roughness'].default_value=.075;p.inputs['IOR'].default_value=1.333;p.inputs['Transmission Weight'].default_value=.8
n=water.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=3;n.inputs['Detail'].default_value=2
b=water.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.14;b.inputs['Distance'].default_value=.07;water.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);water.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,-4,.03));o=bpy.context.object;o.name='pond';o.scale=(110,110,1);o.data.materials.append(water)
padmat=mat('lily pad waxy surface',(.025,.09,.012),(.16,.28,.045),14,.006,.4)
for i in range(65):
 x=random.choice([-1,1])*random.uniform(8,65);y=random.uniform(-70,12)
 if i>57:x=random.uniform(-8,8)
 r=random.uniform(.22,.7);rot=random.random()*math.tau;vs=[(x,y,.075)]
 for j in range(31):
  a=rot+.15+j/30*(math.tau-.38);vs.append((x+math.cos(a)*r,y+math.sin(a)*r,.075+.025*math.sin(j/30*math.pi)))
 fs=[(0,j,j+1) for j in range(1,31)]
 me=bpy.data.meshes.new('notched pad');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('lily pad',me);scene.collection.objects.link(o);me.materials.append(padmat)
em=bpy.data.materials.new('warm lamp glass');em.use_nodes=True;p=em.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.7,.28,.07,1);p.inputs['Emission Color'].default_value=(1,.42,.12,1);p.inputs['Emission Strength'].default_value=4
for i in range(24):
 t=i/23;y=20+t*206;z=(y-18)*100/210
 for side in [-1,1]:
  x=side*(14.7-t*2)
  box('lamp post',(x,y,z+.65),(.095,.095,1.3),metal)
  box('lamp hood',(x,y,z+1.35),(.7,.58,.075),metal,.025)
  box('amber lamp',(x,y,z+1.27),(.32,.25,.09),em)
  d=bpy.data.lights.new('lamp pool','POINT');d.energy=24;d.color=(1,.48,.19);d.shadow_soft_size=.25;o=bpy.data.objects.new('lamp pool',d);scene.collection.objects.link(o);o.location=(x,y,z+1.2)
area('entrance warmth',(0,222,108),(0,231,108),1800,8,(1,.52,.27))
area('overcast opening',(-25,100,260),(0,130,25),450000,150,(.76,.86,.79))
area('limestone soft light',(-35,170,240),(0,240,190),110000,110,(.83,.88,.81))
# a real participating medium joins the layers of trees and softens the distance.
vol=bpy.data.materials.new('forest atmosphere');vol.use_nodes=True;ns=vol.node_tree.nodes;ns.clear();v=ns.new('ShaderNodeVolumePrincipled');v.inputs['Density'].default_value=.0016;v.inputs['Color'].default_value=(.54,.65,.60,1);v.inputs['Anisotropy'].default_value=.35;out=ns.new('ShaderNodeOutputMaterial');vol.node_tree.links.new(v.outputs['Volume'],out.inputs['Volume'])
box('atmosphere',(0,140,160),(430,600,340),vol)
bpy.ops.object.camera_add(location=(0,-92,10));camera=bpy.context.object;camera.name='reference camera';camera.data.lens=34;camera.data.clip_end=800;aim(camera,(0,228,111));scene.camera=camera
# link distant crowns after primitive construction to avoid repeated scene updates.
for idx,loc,scale,rot in crown_specs:
 o=bpy.data.objects.new('canopy lobe %03d'%idx,core.data);scene.collection.objects.link(o);o.location=loc;o.scale=scale;o.rotation_euler=rot
scene.render.film_transparent=False
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cathedral-proportions.blend'))
print('Scene ready; rendering',flush=True)
bpy.ops.render.render(write_still=True)
