"""A complete offline scene: reference composition, physical lighting and foliage."""
import bpy, math, random, sys
from pathlib import Path
from mathutils import Vector
from mathutils.noise import noise_vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'renders';OUT.mkdir(exist_ok=True)
random.seed(1707)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=96;scene.cycles.use_denoising=True
scene.cycles.max_bounces=7;scene.cycles.transparent_max_bounces=6
scene.render.resolution_x=1600;scene.render.resolution_y=1600;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'cathedral-landscape-scale.png')
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
stone=mat('weathered pale limestone',(.23,.27,.24),(.56,.59,.51),8,.018)
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
 # unequal ridges give the valley a geological silhouette instead of a tree colonnade.
 peaks=[(-100,150,260,62,155),(118,245,290,70,145),(-155,370,195,72,110),(95,55,105,65,80)]
 ridge=max(amp*math.exp(-((x-cx)/wx)**2-((y-cy)/wy)**2) for cx,cy,amp,wx,wy in peaks)
 # open pockets between offset shoulders keep the gorge from becoming two hedges.
 if x<0:
  edge=27+20*math.exp(-((y-110)/55)**2)+11*math.sin(y*.034)
 else:
  edge=30+25*math.exp(-((y-225)/65)**2)+9*math.sin(y*.046+1.3)
 shoulder=max(0,min(1,(abs(x)-edge)/42));shoulder=shoulder*shoulder*(3-2*shoulder)
 erosion=noise_vector(Vector((x*.035,y*.027,2))).z*35+noise_vector(Vector((x*.11,y*.075,6))).x*5
 return rise*bank+bank*(1.1+noise_vector(Vector((x*.07,y*.07,1))).z*1.8)-2.4*basin+shoulder*max(0,ridge+erosion)
verts=[];faces=[];N=190
for j in range(N+1):
 y=-190+j*650/N
 for i in range(N+1):
  x=-220+i*440/N;verts.append((x,y,height(x,y)))
for j in range(N):
 for i in range(N):
  a=j*(N+1)+i;faces.append((a,a+1,a+N+2,a+N+1))
# steep faces show occasional stone through the vegetation; gentler slopes stay mossy.
cliff=mat('mossy cliff faces',(.025,.033,.026),(.085,.11,.071),.7,.8,.97)
n=cliff.node_tree.nodes;l=cliff.node_tree.links;p=n.get('Principled BSDF')
geo=n.new('ShaderNodeNewGeometry');split=n.new('ShaderNodeSeparateXYZ');ramp=n.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.25;ramp.color_ramp.elements[0].color=(.018,.032,.021,1)
ramp.color_ramp.elements[1].position=.7;ramp.color_ramp.elements[1].color=(.012,.033,.011,1)
l.new(geo.outputs['Normal'],split.inputs[0]);l.new(split.outputs['Z'],ramp.inputs[0]);l.new(ramp.outputs['Color'],p.inputs['Base Color'])
# a fine continuous canopy layer prevents individual plants from defining the hillside scale.
tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=4.5;tex.inputs['Detail'].default_value=6
small=n.new('ShaderNodeBump');small.inputs['Strength'].default_value=.8;small.inputs['Distance'].default_value=.35
l.new(tex.outputs['Fac'],small.inputs['Height']);l.new(small.outputs['Normal'],p.inputs['Normal'])

mesh=bpy.data.meshes.new('forest floor');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('moss banks',mesh);scene.collection.objects.link(o);o.data.materials.append(cliff)
for p in mesh.polygons:p.use_smooth=True
# the lower canopy is a continuous uneven surface, so distant forest has no bare gaps
# between crown instances. its relief stays small against the landform's overall height.
cv=[];cf=[];nx=500;ny=540
for row in range(ny+1):
 yy=-12+row*480/ny
 for col in range(nx+1):
  xx=-220+col*440/nx
  relief=1.15+abs(noise_vector(Vector((xx*.7,yy*.7,7))).z)*1.8
  cv.append((xx,yy,height(xx,yy)+relief))
for row in range(ny):
 yy=-12+(row+.5)*480/ny
 for col in range(nx):
  xx=-220+(col+.5)*440/nx
  if abs(xx)<16 or height(xx,yy)<.2:continue
  k=row*(nx+1)+col;cf.append((k,k+1,k+nx+2,k+nx+1))
me=bpy.data.meshes.new('continuous fine forest canopy');me.from_pydata(cv,[],cf);me.update()
o=bpy.data.objects.new('continuous fine forest canopy',me);scene.collection.objects.link(o);o.hide_render=True
canopymat=mat('distant connected forest',(.016,.039,.012),(.055,.105,.031),3.8,.18,.9);me.materials.append(canopymat)
for face in me.polygons:face.use_smooth=True
# build a connected understory, with fine branchlets instanced across irregular crowns.
# sharing the branchlet meshes keeps the editable scene small without spherical stand-ins.
random.seed(260910)
leafm=[]
for i in range(5):
 m=bpy.data.materials.new('forest leaf '+str(i));m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.026+i*.009,.065+i*.022,.011+i*.005,1)
 p.inputs['Roughness'].default_value=.6;p.inputs['Subsurface Weight'].default_value=.08
 leafm.append(m)
# each instance is a whole irregular crown with much smaller surface leaves.
templates=[]
for variant in range(8):
 vs=[];fs=[];mi=[]
 random.seed(4000+variant)
 for j in range(900):
  a=random.random()*math.tau;z=random.uniform(-.7,.9);rr=math.sqrt(max(0,1-z*z))
  radial=Vector((math.cos(a)*rr,math.sin(a)*rr,z))
  radius=.83+noise_vector(radial*4+Vector((variant,0,0))).x*.26
  c=Vector((radial.x*radius,radial.y*radius,radial.z*radius*.8))
  normal=(radial+Vector((0,0,.45))).normalized();u=normal.cross(Vector((0,0,1)))
  if u.length<.01:u=Vector((1,0,0))
  u.normalize();v=normal.cross(u);length=random.uniform(.11,.19);base=len(vs)
  vs.extend(tuple(q) for q in [c-u*length,c+v*length*.46,c+u*length,c-v*length*.46,c+normal*length*.12])
  for k in range(4):fs.append((base+k,base+(k+1)%4,base+4));mi.append(random.randrange(5))
 mesh=bpy.data.meshes.new('fine forest crown '+str(variant));mesh.from_pydata(vs,[],fs);mesh.update()
 for m in leafm:mesh.materials.append(m)
 for j,f in enumerate(mesh.polygons):f.material_index=mi[j]
 templates.append(mesh)
random.seed(260910)
plant_specs=[]
# sample the actual slope more densely, so steep cliffs do not expose a planting grid.
for side in [-1,1]:
 for row in range(105):
  y=-2+row*4.2
  for col in range(42):
   x=side*(18+col*4.4+random.uniform(-2,2));yy=y+random.uniform(-2,2)
   dx=(height(x+.5,yy)-height(x-.5,yy));dy=(height(x,yy+.5)-height(x,yy-.5))
   density=min(14,max(7,int(math.sqrt(1+dx*dx+dy*dy)*4)))
   for k in range(density):
    xx=x+random.uniform(-2,2);yyy=yy+random.uniform(-2,2)
    if abs(xx)<16:continue
    size=random.uniform(1.7825,3.1775)
    loc=Vector((xx,yyy,height(xx,yyy)+size*.65+2))
    plant_specs.append((loc,(size,size,size*random.uniform(.8,1.2)),random.uniform(0,math.tau),random.randrange(8)))
# distant vegetation follows the ridges too; the silhouette no longer relies on trunks.
# far ridges are separate layers behind the monument, with different contours.
for layer,(distance,base) in enumerate([(460,75),(610,88),(780,105)]):
 rv=[];rf=[];count=150
 for row in range(3):
  yy=distance+row*28
  for i in range(count+1):
   x=-430+i*860/count
   z=base+abs(x)*.58+25*math.sin(x*.024+layer*1.9)+noise_vector(Vector((x*.012,layer*2,2))).z*30
   rv.append((x,yy,z-row*12))
 for row in range(2):
  for i in range(count):
   k=row*(count+1)+i;rf.append((k,k+1,k+count+2,k+count+1))
 me=bpy.data.meshes.new('far ridge '+str(layer));me.from_pydata(rv,[],rf);me.update();o=bpy.data.objects.new('far ridge '+str(layer),me);scene.collection.objects.link(o);me.materials.append(cliff)
 for face in me.polygons:face.use_smooth=True
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
depth.inputs['From Min'].default_value=.13;depth.inputs['From Max'].default_value=.44;depth.inputs['To Min'].default_value=.00025;depth.inputs['To Max'].default_value=.0025;depth.clamp=True
vol.node_tree.links.new(coord.outputs['Generated'],split.inputs[0]);vol.node_tree.links.new(split.outputs['Y'],depth.inputs['Value']);vol.node_tree.links.new(depth.outputs['Result'],v.inputs['Density'])
box('atmosphere',(0,420,300),(1000,1160,700),vol)
bpy.ops.object.camera_add(location=(0,-92,10));camera=bpy.context.object;camera.name='reference camera';camera.data.lens=34;camera.data.clip_end=1800;aim(camera,(0,228,111));scene.camera=camera
for idx,(loc,scale,rot,variant) in enumerate(plant_specs):
 o=bpy.data.objects.new('leafy branchlet %05d'%idx,templates[variant]);scene.collection.objects.link(o);o.location=loc;o.scale=scale;o.rotation_euler.z=rot
scene.render.film_transparent=False
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cathedral-landscape-scale.blend'))
print('Scene ready; rendering',flush=True)
bpy.ops.render.render(write_still=True)
