"""Cooler layered distance haze around the established architecture and forest."""
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
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'cathedral-atmosphere-study.png')
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.25,.36,.32,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
# a dark forest beyond the clearing prevents bright gaps from outlining every crown.
wn=scene.world.node_tree.nodes;wl=scene.world.node_tree.links
rays=wn.new('ShaderNodeLightPath');mix=wn.new('ShaderNodeMixShader');back=wn.new('ShaderNodeBackground')
back.inputs['Color'].default_value=(.033,.05,.065,1);back.inputs['Strength'].default_value=.35
wl.new(rays.outputs['Is Camera Ray'],mix.inputs[0]);wl.new(wn['Background'].outputs[0],mix.inputs[1]);wl.new(back.outputs[0],mix.inputs[2]);wl.new(mix.outputs[0],wn['World Output'].inputs['Surface'])
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
box('entrance back wall',(0,341.08,156),(25,.12,12),bark)
# a small dark inset makes the actual engraved letters legible at this distance.
font=bpy.data.curves.new('305 engraved shadow','FONT');font.body='305';font.size=28;font.align_x='CENTER';font.extrude=.002
letter=bpy.data.objects.new('305',font);scene.collection.objects.link(letter);letter.location=(0,329.95,184);letter.rotation_euler=(math.pi/2,0,0);font.materials.append(stairmat)
# cut before beveling so both the silhouette and new recesses receive the same edge treatment.
mon.modifiers.clear()
bpy.ops.object.select_all(action='DESELECT');mon.select_set(True);bpy.context.view_layer.objects.active=mon
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
def subtract(cutter,name):
 bpy.ops.object.select_all(action='DESELECT');mon.select_set(True);bpy.context.view_layer.objects.active=mon
 modifier=mon.modifiers.new(name,'BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
 bpy.ops.object.modifier_apply(modifier=modifier.name);bpy.data.objects.remove(cutter,do_unlink=True)
cutfont=font.copy();cutfont.extrude=2
cutter=bpy.data.objects.new('inscription cutter',cutfont);scene.collection.objects.link(cutter)
cutter.location=(0,331.2,184);cutter.rotation_euler=letter.rotation_euler.copy()
bpy.ops.object.select_all(action='DESELECT');cutter.select_set(True);bpy.context.view_layer.objects.active=cutter
bpy.ops.object.convert(target='MESH');cutter=bpy.context.object
subtract(cutter,'recessed 305')
letter.location.y=333.17
cutter=box('entrance cutter',(0,335,155.9),(25,12,12.2),stone)
subtract(cutter,'deep entrance')
bevel=mon.modifiers.new('weathered architectural edges','BEVEL');bevel.width=.18;bevel.segments=3
# check the carved mesh itself, not just the text overlay or dark doorway material.
bpy.context.view_layer.update()
def facade_hit(x,z):
 origin=mon.matrix_world.inverted()@Vector((x,320,z))
 hit,point,normal,face=mon.ray_cast(origin,Vector((0,1,0)))
 assert hit,(x,z)
 return (mon.matrix_world@point).y
assert facade_hit(0,156)>340
assert max(facade_hit(x,z) for x in range(-20,21,2) for z in range(186,204,2))>332
print('Architecture checks: doorway and inscription have actual recessed geometry',flush=True)
stair_variants=[]
for k in range(7):
 material=stairmat.copy();material.name='basalt variation %02d'%k
 ramp=next(n for n in material.node_tree.nodes if n.type=='VALTORGB')
 for element in ramp.color_ramp.elements:
  color=element.color[:];factor=.93+k*.023
  element.color=(color[0]*factor,color[1]*factor,color[2]*factor,1)
 material.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.78+k*.012
 stair_variants.append(material)
for i in range(150):
 h=(i+1);y=(i+.5)*330/150;w=58-i/150*11
 box('tread %03d'%i,(0,y,h/2),(w,330/150+.01,h),stair_variants[(i*37+i*i*3)%7],.035)
# ground rolls into banks, leaving a submerged bed across the foreground.
def height(x,y):
 rise=max(0,min(1,y/330))*150
 bank=max(0,min(1,(abs(x)-23)/20));bank=bank*bank*(3-2*bank)
 # separate shoulders bury the roots without turning the whole valley into a ramp.
 hills=[(-120,130,65,65,95),(155,255,100,85,105),(-75,300,45,38,60),(85,75,32,48,45)]
 relief=sum(h*math.exp(-((x-cx)/wx)**2-((y-cy)/wy)**2) for cx,cy,h,wx,wy in hills)
 # smaller shoulders interrupt the broad hills, while shallow gullies separate stands.
 shoulders=[(-68,65,18,23,26),(-95,185,25,26,32),(-54,282,18,18,24),(65,135,25,25,30),(105,280,26,30,28)]
 relief+=sum(h*math.exp(-((x-cx)/wx)**2-((y-cy)/wy)**2) for cx,cy,h,wx,wy in shoulders)
 relief-=13*math.exp(-((x+80)/32)**2-((y-125)/17)**2)
 relief-=17*math.exp(-((x-83)/38)**2-((y-210)/19)**2)
 relief+=noise_vector(Vector((x*.045,y*.032,14))).z*10
 shore=max(0,min(1,(y+25)/55))
 return rise*bank-3+bank*shore*relief+noise_vector(Vector((x*.014,y*.014,2))).z*7*bank*shore
verts=[];faces=[];N=150
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
 tr.location.z-=45
 # slow bends and unequal ribs break the clean column silhouette at this distance.
 for vert in tr.data.vertices:
  t=(vert.co.z-min(zs))/(max(zs)-min(zs))
  angle=math.atan2(vert.co.y,vert.co.x)
  radial=1+.085*math.sin(angle*7+t*14+i)+.045*math.sin(angle*13-t*5)+.035*math.sin(t*65+angle*3)
  vert.co.x=vert.co.x*radial+math.sin(t*8+i)*1.3
  vert.co.y=vert.co.y*radial+math.sin(t*5+i)*.9
# faint upright stands behind the clearing establish depth beyond the monument.
distant_bark=mat('hazy distant bark',(.012,.02,.017),(.022,.035,.03),.4,.05)
dp=distant_bark.node_tree.nodes.get('Principled BSDF')
dp.inputs['Emission Color'].default_value=(.012,.02,.019,1);dp.inputs['Emission Strength'].default_value=.35
back_stands=[]
for i in range(28):
 y=random.uniform(680,1350);x=random.uniform(-690,690)
 source=assets['rooted_trunk_'+str(i%3)]
 xs=[v.co.x for v in source.data.vertices];zs=[v.co.z for v in source.data.vertices]
 radius=random.uniform(30,60);h=random.uniform(1100,1500)
 back_stands.append((x,y,radius))
 tr=instance('distant forest trunk %02d'%i,source,(x,y,130),(radius*2/(max(xs)-min(xs)),radius*2/(max(xs)-min(xs)),h/(max(zs)-min(zs))),distant_bark)
 tr.rotation_euler.z=random.random()*math.tau
 # each distant stem wanders independently so the gaps stop reading as parallel bars.
 phase=i*1.731;lean=math.sin(phase)*5
 for vert in tr.data.vertices:
  t=(vert.co.z-min(zs))/(max(zs)-min(zs))
  angle=math.atan2(vert.co.y,vert.co.x)
  swell=1+.13*math.sin(t*14+phase)+.06*math.sin(angle*5+t*27)
  vert.co.x=vert.co.x*swell+lean*t+math.sin(t*9+phase)*2.1
  vert.co.y=vert.co.y*swell+math.cos(t*7+phase)*1.5

# asymmetric connected crowns avoid the repeated radial shapes of the first blockout.
# use a separate generator so template changes do not move the established forest.
shape_rng=random.Random(3051707)
canopy_material=mat('blockout canopy',(.012,.029,.016),(.08,.13,.055),1,.2)
crown_meshes=[]
for family in range(7):
 mesh=bpy.data.meshes.new('asymmetric crown family %02d'%family);bm=bmesh.new()
 lobes=[(Vector((0,0,-.23)),.66,(1,.85,.85))]
 for k in range(9+family):
  angle=k*2.39996+family*.7
  radius=shape_rng.uniform(.22,.68)
  c=Vector((math.cos(angle)*radius,math.sin(angle)*radius*.8,shape_rng.uniform(-.05,.36)))
  size=shape_rng.uniform(.24,.43)
  lobes.append((c,size,(shape_rng.uniform(.8,1.3),shape_rng.uniform(.8,1.2),shape_rng.uniform(.7,1.2))))
 for k,(center,radius,stretch) in enumerate(lobes):
  result=bmesh.ops.create_icosphere(bm,subdivisions=2,radius=radius)
  for vert in result['verts']:
   vert.co*=1+noise_vector(vert.co*9+Vector((k,family,0))).x*.19
   vert.co=Vector((vert.co.x*stretch[0],vert.co.y*stretch[1],vert.co.z*stretch[2]))+center
 bm.to_mesh(mesh);bm.free()
 for poly in mesh.polygons:poly.use_smooth=True
 mesh.materials.append(canopy_material);crown_meshes.append(mesh)
core=bpy.data.objects.new('simplified canopy template',crown_meshes[0]);scene.collection.objects.link(core);core.hide_render=True
crown_specs=[]
for i in range(6500):
 y=random.uniform(-35,650);side=random.choice([-1,1]);x=side*random.uniform(34,490)
 edge=31-y/330*5+5+5*math.sin(y*.045+side)
 if abs(x)<edge:continue
 stand=noise_vector(Vector((x*.023,y*.023,8))).z
 r=random.uniform(4,10)*(1.05+stand*.4)
 z=height(x,y)+r*.8+max(0,abs(x)-70)*.045
 crown_specs.append((i,(x,y,z),(r,r*random.uniform(.8,1.2),r*random.uniform(.9,1.5)),(0,0,random.random()*math.tau)))
# grouped smaller crowns stitch exposed gaps into connected stands at different heights.
# this generator preserves the existing stair edge and distant planting samples.
stand_rng=random.Random(30542)
for group in range(54):
 side=-1 if group%2 else 1
 cx=side*stand_rng.uniform(45,155);cy=stand_rng.uniform(12,325)
 spread_x=stand_rng.uniform(7,17);spread_y=stand_rng.uniform(10,25)
 for j in range(30):
  x=stand_rng.gauss(cx,spread_x);y=stand_rng.gauss(cy,spread_y)
  if y<0 or y>345 or abs(x)<34-y/330*4:continue
  r=stand_rng.uniform(2.5,6.5)
  z=height(x,y)+r*.72
  crown_specs.append((len(crown_specs),(x,y,z),(r,r*stand_rng.uniform(.8,1.3),r*stand_rng.uniform(.9,1.6)),(0,0,stand_rng.random()*math.tau)))
# small uneven fingers overlap the stair edges while keeping the ascent legible.
for side,cy,amount in [(-1,95,70),(1,195,85),(-1,280,60),(1,35,55)]:
 for j in range(amount):
  y=random.gauss(cy,16);r=random.uniform(3,7)
  edge=29-y/330*5.5
  x=side*(edge+random.uniform(0,13))
  z=max(0,y*150/330)+r*.45
  crown_specs.append((len(crown_specs),(x,y,z),(r,r,r*1.2),(0,0,random.random()*math.tau)))
# offset forest silhouettes recede behind the trunks and the central clearing.
for i in range(2200):
 y=random.uniform(480,1250);x=random.uniform(-650,650)
 r=random.uniform(7,15)
 shoulder=170+90*math.exp(-((x+165)/115)**2)+150*math.exp(-((x-235)/140)**2)
 z=shoulder+noise_vector(Vector((x*.018,y*.012,9))).z*35
 crown_specs.append((len(crown_specs),(x,y,z),(r,r,r*1.25),(0,0,random.random()*math.tau)))
# low shoreline clumps join the large forest masses to the water without a straight edge.
for side,cx,cy in [(-1,55,-8),(1,72,-5),(-1,110,-15)]:
 for j in range(90):
  x=side*(cx+random.gauss(0,13));y=cy+random.gauss(0,7)
  r=random.uniform(1.3,3.8);z=height(x,y)+r*.55
  if z<-.4:continue
  crown_specs.append((len(crown_specs),(x,y,z),(r,r*.8,r*.75),(0,0,random.random()*math.tau)))
water=bpy.data.materials.new('deep green clear water');water.use_nodes=True;p=water.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.055,.13,.085,1);p.inputs['Roughness'].default_value=.16;p.inputs['IOR'].default_value=1.333;p.inputs['Transmission Weight'].default_value=.6
n=water.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=3;n.inputs['Detail'].default_value=2
b=water.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.14;b.inputs['Distance'].default_value=.07;water.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);water.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,-130,.03));o=bpy.context.object;o.name='pond';o.scale=(350,350,1);o.data.materials.append(water)
padmat=mat('lily pad waxy surface',(.025,.09,.012),(.16,.28,.045),14,.006,.4)
for i in range(65):
 x=random.choice([-1,1])*random.uniform(15,140);y=random.uniform(-160,-5)
 if i>57:x=random.uniform(-8,8)
 r=random.uniform(.4,1.2);rot=random.random()*math.tau;vs=[(x,y,.075)]
 for j in range(31):
  a=rot+.15+j/30*(math.tau-.38);vs.append((x+math.cos(a)*r,y+math.sin(a)*r,.075+.025*math.sin(j/30*math.pi)))
 fs=[(0,j,j+1) for j in range(1,31)]
 me=bpy.data.meshes.new('notched pad');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('lily pad',me);scene.collection.objects.link(o);me.materials.append(padmat)
em=bpy.data.materials.new('warm lamp glass');em.use_nodes=True;p=em.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.7,.28,.07,1);p.inputs['Emission Color'].default_value=(1,.42,.12,1);p.inputs['Emission Strength'].default_value=4
box('recessed entrance light',(0,336.8,161.6),(8,.45,.22),em)
for i in range(24):
 t=i/23;y=3+t*324;z=y*150/330
 for side in [-1,1]:
  x=side*(30-t*5.5)
  box('lamp post',(x,y,z+.65),(.095,.095,1.3),metal)
  box('lamp hood',(x,y,z+1.35),(.7,.58,.075),metal,.025)
  box('amber lamp',(x,y,z+1.27),(.32,.25,.09),em)
  d=bpy.data.lights.new('lamp pool','POINT');d.energy=24;d.color=(1,.48,.19);d.shadow_soft_size=.25;o=bpy.data.objects.new('lamp pool',d);scene.collection.objects.link(o);o.location=(x,y,z+1.2)
area('entrance warmth',(0,336,159),(0,341,156),1100,6,(1,.52,.27))
def soft(name,loc,energy,size,color):
 d=bpy.data.lights.new(name,'POINT');d.energy=energy;d.shadow_soft_size=size;d.color=color
 o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc
soft('open sky',(-100,80,650),2200000,250,(.76,.85,.88))
soft('stone light',(-90,250,440),620000,110,(.84,.89,.86))
soft('pond opening',(-80,-160,170),400000,120,(.73,.86,.77))
# broad local openings reveal a few crown tops while the giant trunks stay shaded.
soft('left canopy opening',(-65,95,160),180000,55,(.83,.88,.72))
soft('right canopy opening',(85,235,265),210000,65,(.66,.79,.83))
soft('stair skylight',(0,130,190),110000,90,(.78,.85,.86))

vol=bpy.data.materials.new('distance haze');vol.use_nodes=True;ns=vol.node_tree.nodes;ns.clear()
v=ns.new('ShaderNodeVolumePrincipled');v.inputs['Density'].default_value=.00065;v.inputs['Color'].default_value=(.46,.58,.69,1);v.inputs['Anisotropy'].default_value=.2
out=ns.new('ShaderNodeOutputMaterial');vol.node_tree.links.new(v.outputs['Volume'],out.inputs['Volume'])
# stronger extinction beyond the monument merges distant shapes into forest layers.
coord=ns.new('ShaderNodeTexCoord');separate=ns.new('ShaderNodeSeparateXYZ')
fade=ns.new('ShaderNodeMapRange');fade.clamp=True
fade.inputs['From Min'].default_value=.22;fade.inputs['From Max'].default_value=.48
fade.inputs['To Min'].default_value=.00054/3;fade.inputs['To Max'].default_value=.0027
vol.node_tree.links.new(coord.outputs['Generated'],separate.inputs[0])
vol.node_tree.links.new(separate.outputs['Y'],fade.inputs['Value'])
# subtle variation keeps the distant medium from becoming a flat curtain.
texture=ns.new('ShaderNodeTexNoise');texture.inputs['Scale'].default_value=7;texture.inputs['Detail'].default_value=1.5
variation=ns.new('ShaderNodeMapRange');variation.inputs['To Min'].default_value=.85;variation.inputs['To Max'].default_value=1.15
multiply=ns.new('ShaderNodeMath');multiply.operation='MULTIPLY'
vol.node_tree.links.new(coord.outputs['Generated'],texture.inputs['Vector'])
vol.node_tree.links.new(texture.outputs['Fac'],variation.inputs['Value'])
vol.node_tree.links.new(variation.outputs['Result'],multiply.inputs[0]);vol.node_tree.links.new(fade.outputs['Result'],multiply.inputs[1])
vol.node_tree.links.new(multiply.outputs[0],v.inputs['Density'])
# a faint distant ambient contribution closes the black gaps without lighting the near trunks.
ambient=ns.new('ShaderNodeMapRange');ambient.clamp=True
ambient.inputs['From Min'].default_value=.0006;ambient.inputs['From Max'].default_value=.0027
ambient.inputs['To Min'].default_value=0;ambient.inputs['To Max'].default_value=.00016
vol.node_tree.links.new(fade.outputs['Result'],ambient.inputs['Value'])
v.inputs['Emission Color'].default_value=(.18,.28,.38,1)
vol.node_tree.links.new(ambient.outputs['Result'],v.inputs['Emission Strength'])
box('atmosphere',(0,1250,2000),(6000,3300,5000),vol)
bpy.ops.object.camera_add(location=(0,-240,36));camera=bpy.context.object;camera.name='distant reference camera';camera.data.lens=35.518;camera.data.clip_end=6000
camera.rotation_euler=(math.pi/2+.226,0,0);scene.camera=camera
# link distant crowns after primitive construction to avoid repeated scene updates.
back_meshes=[]
for mesh in crown_meshes:
 back=mesh.copy();back.materials.clear();back.materials.append(distant_bark);back_meshes.append(back)
for idx,loc,scale,rot in crown_specs:
 family=int(abs(loc[0]*13.17+loc[1]*7.31))%len(crown_meshes)
 mesh=back_meshes[family] if loc[1]>650 else crown_meshes[family]
 o=bpy.data.objects.new('canopy lobe %03d'%idx,mesh);scene.collection.objects.link(o);o.location=loc;o.scale=scale;o.rotation_euler=rot
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
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cathedral-atmosphere-study.blend'))
print('Scene ready; rendering',flush=True)
bpy.ops.render.render(write_still=True)
