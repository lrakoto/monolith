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
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'cathedral-forest.png')
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.25,.36,.32,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.18
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-.65
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
# recess the same inscription into the facade; the face remains the approved size.
bpy.ops.object.select_all(action='DESELECT');mon.select_set(True);bpy.context.view_layer.objects.active=mon
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
cutfont=font.copy();cutfont.extrude=1.0
cutter=bpy.data.objects.new('305 carving tool',cutfont);scene.collection.objects.link(cutter);cutter.location=(0,229.1,118);cutter.rotation_euler=letter.rotation_euler.copy()
bpy.ops.object.select_all(action='DESELECT');cutter.select_set(True);bpy.context.view_layer.objects.active=cutter;bpy.ops.object.convert(target='MESH');cutter=bpy.context.object
bpy.context.view_layer.objects.active=mon
carve=mon.modifiers.new('recessed inscription','BOOLEAN');carve.operation='DIFFERENCE';carve.solver='EXACT';carve.object=cutter
bpy.ops.object.modifier_apply(modifier=carve.name);bpy.data.objects.remove(cutter,do_unlink=True)
letter.location.y=229.9
# long, faint mineral variation belongs to the surface rather than a flat uniform color.
n=stone.node_tree.nodes;l=stone.node_tree.links;bs=n.get('Principled BSDF')
tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=.11;tex.inputs['Detail'].default_value=5
coord=n.new('ShaderNodeTexCoord');stretch=n.new('ShaderNodeVectorMath');stretch.operation='MULTIPLY';stretch.inputs[1].default_value=(3,3,.15);l.new(coord.outputs['Object'],stretch.inputs[0]);l.new(stretch.outputs[0],tex.inputs['Vector'])
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.25,.29,.27,1);ramp.color_ramp.elements[1].color=(.49,.52,.47,1);l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],bs.inputs['Base Color'])
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
# build a connected understory, with fine branchlets instanced across irregular crowns.
# sharing the branchlet meshes keeps the editable scene small without spherical stand-ins.
random.seed(260910)
leafm=[]
for i in range(5):
 m=bpy.data.materials.new('forest leaf '+str(i));m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.026+i*.009,.065+i*.022,.011+i*.005,1)
 p.inputs['Roughness'].default_value=.6;p.inputs['Subsurface Weight'].default_value=.08
 leafm.append(m)
templates=[]
for variant in range(8):
 vs=[];fs=[];mi=[]
 def twig(start,end,r1,r2):
  d=(end-start).normalized();u=d.cross(Vector((0,0,1)))
  if u.length<.01:u=Vector((1,0,0))
  u.normalize();v=d.cross(u);base=len(vs)
  for c,r in [(start,r1),(end,r2)]:
   for j in range(5):vs.append(tuple(c+(u*math.cos(j*math.tau/5)+v*math.sin(j*math.tau/5))*r))
  for j in range(5):fs.append((base+j,base+(j+1)%5,base+5+(j+1)%5,base+5+j));mi.append(5)
 def leaflet(c,d,length):
  d.normalize();u=d.cross(Vector((0,0,1)))
  if u.length<.01:u=Vector((1,0,0))
  u.normalize();n=u.cross(d);base=len(vs)
  points=[c,c+d*length*.42+u*length*.24,c+d*length,c+d*length*.42-u*length*.24,c+d*length*.46+n*length*.065]
  vs.extend(tuple(v) for v in points)
  for j in range(4):fs.append((base+j,base+(j+1)%4,base+4));mi.append(random.randrange(5))
 for branch in range(14):
  a=branch*2.39996+random.uniform(-.3,.3);tip=Vector((math.cos(a)*random.uniform(.65,1.4),math.sin(a)*random.uniform(.65,1.4),random.uniform(.0,.6)))
  start=Vector((0,0,-.35));twig(start,tip,.023,.004)
  for j in range(10):
   t=.22+j*.075;c=start.lerp(tip,t);side=Vector((-math.sin(a),math.cos(a),.35))
   for sign in [-1,1]:
    direction=(side*sign+Vector((math.cos(a)*.4,math.sin(a)*.4,.2)))
    leaflet(c,direction,random.uniform(.18,.31))
 mesh=bpy.data.meshes.new('branchlet '+str(variant));mesh.from_pydata(vs,[],fs);mesh.update()
 for m in leafm+[bark]:mesh.materials.append(m)
 for i,f in enumerate(mesh.polygons):f.material_index=mi[i]
 templates.append(mesh)
plant_specs=[]
# dense banks cover the exposed slope, with a clear architectural edge at the stairs.
for side in [-1,1]:
 for row in range(43):
  y=-2+row*7.2
  for col in range(14):
   x=side*(20+col*8+random.uniform(-3.8,3.8));yy=y+random.uniform(-3.4,3.4)
   r=3+random.random()**2*15;x=side*max(abs(x),14+r*.8)
   c=Vector((x,yy,height(x,yy)+r*.35));count=13 if r<8 else 30
   for k in range(count):
    a=k*2.39996;rr=r*math.sqrt((k+.5)/count)*.75
    z=math.sqrt(max(0,1-(rr/r)**2))*r*.5+random.uniform(-.12,.12)*r
    loc=c+Vector((math.cos(a)*rr,math.sin(a)*rr,z))
    size=random.uniform(1.3,2.3)
    plant_specs.append((loc,(size,size,size*random.uniform(.7,1.1)),random.uniform(0,math.tau),random.randrange(8)))
# background trunks are partially concealed by layered crowns instead of isolated poles.
trees=[]
for i in range(80):
 side=random.choice([-1,1]);x=side*random.uniform(62,170);y=random.uniform(110,440);scale=random.uniform(.6,1.2)
 trees.append((x,y,scale))
 tr=instance('forest trunk %02d'%i,assets['rooted_trunk_'+str(i%3)],(x,y,height(x,y)-.5),(scale,scale,1.9+random.random()*.6),bark);tr.rotation_euler.z=random.random()*math.tau
 for layer in range(5):
  z=height(x,y)+35+layer*36+random.uniform(-8,8)
  for k in range(40):
   a=random.random()*math.tau;r=random.uniform(3,16)*scale
   loc=Vector((x+math.cos(a)*r,y+math.sin(a)*r,z+random.uniform(-5,7)))
   size=random.uniform(2.4,4.4)
   plant_specs.append((loc,(size,size,size*.8),random.uniform(0,math.tau),random.randrange(8)))
# link all foliage after the operator-based primitives have been built.
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
area('soft pond daylight',(-65,-20,95),(0,50,12),70000,85,(.79,.88,.73))
area('limestone soft light',(-35,170,240),(0,240,190),110000,110,(.83,.88,.81))
# a real participating medium joins the layers of trees and softens the distance.
vol=bpy.data.materials.new('forest atmosphere');vol.use_nodes=True;ns=vol.node_tree.nodes;ns.clear();v=ns.new('ShaderNodeVolumePrincipled');v.inputs['Density'].default_value=.0016;v.inputs['Color'].default_value=(.54,.65,.60,1);v.inputs['Anisotropy'].default_value=.35;out=ns.new('ShaderNodeOutputMaterial');vol.node_tree.links.new(v.outputs['Volume'],out.inputs['Volume'])
# keep the pond clear and concentrate the atmospheric separation in the distance.
coord=ns.new('ShaderNodeTexCoord');split=ns.new('ShaderNodeSeparateXYZ');depth=ns.new('ShaderNodeMapRange')
depth.inputs['From Min'].default_value=.25;depth.inputs['From Max'].default_value=.85;depth.inputs['To Min'].default_value=.00025;depth.inputs['To Max'].default_value=.0025;depth.clamp=True
vol.node_tree.links.new(coord.outputs['Generated'],split.inputs[0]);vol.node_tree.links.new(split.outputs['Y'],depth.inputs['Value']);vol.node_tree.links.new(depth.outputs['Result'],v.inputs['Density'])
box('atmosphere',(0,140,160),(430,600,340),vol)
bpy.ops.object.camera_add(location=(0,-92,10));camera=bpy.context.object;camera.name='reference camera';camera.data.lens=34;camera.data.clip_end=800;aim(camera,(0,228,111));scene.camera=camera
for idx,(loc,scale,rot,variant) in enumerate(plant_specs):
 o=bpy.data.objects.new('leafy branchlet %05d'%idx,templates[variant]);scene.collection.objects.link(o);o.location=loc;o.scale=scale;o.rotation_euler.z=rot
scene.render.film_transparent=False
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cathedral-forest.blend'))
print('Scene ready; rendering',flush=True)
bpy.ops.render.render(write_still=True)
