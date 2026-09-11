"""Soft key: contrast overshoots entirely through the shadows, which a hard sun keeps too dark."""
import bpy, math, random, sys
from pathlib import Path
from mathutils import Vector
from mathutils.noise import noise_vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'renders';OUT.mkdir(exist_ok=True)
# measuring value structure does not need full resolution, so a quick mode renders small.
import os
QUICK=os.environ.get('CATHEDRAL_QUICK')
STILL=Path(QUICK) if QUICK else OUT/'cathedral-softkey-study.png'
random.seed(1707)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=16 if QUICK else 64;scene.cycles.use_denoising=True
scene.cycles.max_bounces=7;scene.cycles.transparent_max_bounces=6
QUICK_RES=int(os.environ.get('CATHEDRAL_QUICK_RES','600'))
scene.render.resolution_x=scene.render.resolution_y=QUICK_RES if QUICK else 1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(STILL)
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.25,.36,.32,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.76
# a dark forest beyond the clearing prevents bright gaps from outlining every crown.
wn=scene.world.node_tree.nodes;wl=scene.world.node_tree.links
rays=wn.new('ShaderNodeLightPath');mix=wn.new('ShaderNodeMixShader');back=wn.new('ShaderNodeBackground')
back.inputs['Color'].default_value=(.033,.05,.065,1);back.inputs['Strength'].default_value=.34
wl.new(rays.outputs['Is Camera Ray'],mix.inputs[0]);wl.new(wn['Background'].outputs[0],mix.inputs[1]);wl.new(back.outputs[0],mix.inputs[2]);wl.new(mix.outputs[0],wn['World Output'].inputs['Surface'])
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-1.0
# CPU avoids a Metal kernel readiness stall on the current render host.
scene.cycles.device="CPU"

def mat(name,low,high,scale=5,bump=.1,rough=.85,stretch=None,gen=False):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=rough
 tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=scale;tex.inputs['Detail'].default_value=5;tex.inputs['Roughness'].default_value=.75
 coord=n.new('ShaderNodeTexCoord')
 src=coord.outputs['Generated'] if gen else coord.outputs['Object']
 if stretch:
  v=n.new('ShaderNodeVectorMath');v.operation='MULTIPLY';v.inputs[1].default_value=stretch;l.new(src,v.inputs[0]);l.new(v.outputs[0],tex.inputs['Vector'])
 else:l.new(src,tex.inputs['Vector'])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=(*low,1);ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(*high,1)
 l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
 bn=n.new('ShaderNodeBump');bn.inputs['Strength'].default_value=.6;bn.inputs['Distance'].default_value=bump;l.new(tex.outputs['Fac'],bn.inputs['Height']);l.new(bn.outputs['Normal'],p.inputs['Normal'])
 return m
bark=mat('vine draped colossal bark',(.0004,.0006,.0004),(.0109,.0130,.0079),1,.16,.985,(55,55,2.0),True)
# the noise fac clusters around the middle, so the default ramp span returned almost one colour
# and the streaks washed out entirely. narrowing the span spreads them back across the range.
bark_ramp=[n for n in bark.node_tree.nodes if n.type=='VALTORGB'][0]
bark_ramp.color_ramp.elements[0].position=.405;bark_ramp.color_ramp.elements[1].position=.598
moss=mat('moss and forest earth',(.005,.011,.004),(.027,.052,.015),3,.14)
stone=mat('weathered pale limestone',(.198,.232,.206),(.474,.500,.432),2.5,.045)
plinth_stone=mat('weathered plinth limestone',(.158,.188,.168),(.378,.408,.348),1.6,.075,.85,(.045,.045,7.5))
stairmat=mat('damp basalt treads',(.0134,.0206,.0174),(.0792,.103,.0871),6,.025,.82)
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
for side in (-1,1):
 box('flanking wall %d'%side,(side*69,338,186),(86,9,72),plinth_stone,.12)
 box('wall cornice %d'%side,(side*69,336.4,223.6),(89,12.4,3.2),plinth_stone,.1)
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
riser_geo=stairmat.node_tree.nodes.new('ShaderNodeNewGeometry')
riser_split=stairmat.node_tree.nodes.new('ShaderNodeSeparateXYZ')
riser_fade=stairmat.node_tree.nodes.new('ShaderNodeMapRange');riser_fade.clamp=True
riser_fade.inputs['From Min'].default_value=-.85;riser_fade.inputs['From Max'].default_value=-.3
riser_fade.inputs['To Min'].default_value=.44;riser_fade.inputs['To Max'].default_value=1.0
riser_mix=stairmat.node_tree.nodes.new('ShaderNodeMix');riser_mix.data_type='RGBA';riser_mix.blend_type='MULTIPLY'
riser_mix.inputs['Factor'].default_value=1.0
_ramp=next(n for n in stairmat.node_tree.nodes if n.type=='VALTORGB')
_bsdf=stairmat.node_tree.nodes.get('Principled BSDF')
stairmat.node_tree.links.new(riser_geo.outputs['Normal'],riser_split.inputs[0])
stairmat.node_tree.links.new(riser_split.outputs['Y'],riser_fade.inputs['Value'])
stairmat.node_tree.links.new(_ramp.outputs['Color'],riser_mix.inputs[6])
stairmat.node_tree.links.new(riser_fade.outputs['Result'],riser_mix.inputs[7])
stairmat.node_tree.links.new(riser_mix.outputs[2],_bsdf.inputs['Base Color'])
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
trunk_info=[]
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
  spread=radial*(1+.62*t)
  vert.co.x=vert.co.x*spread+math.sin(t*8+i)*1.3
  vert.co.y=vert.co.y*spread+math.sin(t*5+i)*.9
 trunk_zs=[v.co.z for v in tr.data.vertices]
 bins=26;profile=[0.0]*bins;span=max(trunk_zs)-min(trunk_zs)
 for v in tr.data.vertices:
  b=min(bins-1,int((v.co.z-min(trunk_zs))/span*bins))
  profile[b]=max(profile[b],math.hypot(v.co.x,v.co.y)*tr.scale.x)
 for b in range(1,bins):
  if profile[b]<=0:profile[b]=profile[b-1]
 trunk_info.append((x,y,r,tr.location.z+min(trunk_zs)*tr.scale.z,tr.location.z+max(trunk_zs)*tr.scale.z,profile))
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
 tr.hide_render=True
 # each distant stem wanders independently so the gaps stop reading as parallel bars.
 phase=i*1.731;lean=math.sin(phase)*5
 for vert in tr.data.vertices:
  t=(vert.co.z-min(zs))/(max(zs)-min(zs))
  angle=math.atan2(vert.co.y,vert.co.x)
  swell=1+.13*math.sin(t*14+phase)+.06*math.sin(angle*5+t*27)
  vert.co.x=vert.co.x*swell+lean*t+math.sin(t*9+phase)*2.1
  vert.co.y=vert.co.y*swell+math.cos(t*7+phase)*1.5

# the remote forest is a restrained procedural backdrop for this composition study.
# retain the former distant stems hidden so their effect can still be compared in blender.
backdrop=bpy.data.materials.new('remote forest atmosphere backdrop');backdrop.use_nodes=True
nodes=backdrop.node_tree.nodes;links=backdrop.node_tree.links;nodes.clear()
coord=nodes.new('ShaderNodeTexCoord');stretch=nodes.new('ShaderNodeVectorMath');stretch.operation='MULTIPLY';stretch.inputs[1].default_value=(22,1,.35)
noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3;noise.inputs['Detail'].default_value=3
ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.0112,.0189,.0222,1);ramp.color_ramp.elements[1].color=(.0245,.0357,.0378,1)
emit=nodes.new('ShaderNodeEmission');emit.inputs['Strength'].default_value=1
height_split=nodes.new('ShaderNodeSeparateXYZ');falloff=nodes.new('ShaderNodeMapRange');falloff.clamp=True
falloff.inputs['From Min'].default_value=.25;falloff.inputs['From Max'].default_value=.52
falloff.inputs['To Min'].default_value=1.5;falloff.inputs['To Max'].default_value=.58
links.new(coord.outputs['Generated'],height_split.inputs[0])
links.new(height_split.outputs['Z'],falloff.inputs['Value'])
links.new(falloff.outputs['Result'],emit.inputs['Strength'])
out=nodes.new('ShaderNodeOutputMaterial')
links.new(coord.outputs['Generated'],stretch.inputs[0]);links.new(stretch.outputs[0],noise.inputs['Vector']);links.new(noise.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs['Color'],emit.inputs['Color']);links.new(emit.outputs[0],out.inputs['Surface'])
box('remote forest backdrop',(0,1450,1500),(5000,2,4000),backdrop)
# asymmetric connected crowns avoid the repeated radial shapes of the first blockout.
# use a separate generator so template changes do not move the established forest.
shape_rng=random.Random(3051707)
canopy_material=mat('blockout canopy',(.0064,.0154,.0081),(.0382,.0635,.0273),1,.2)
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
   vert.co*=1+noise_vector(vert.co*9+Vector((k,family,0))).x*.15+noise_vector(vert.co*23+Vector((k,family,4))).y*.085
   vert.co=Vector((vert.co.x*stretch[0],vert.co.y*stretch[1],vert.co.z*stretch[2]))+center
 bm.to_mesh(mesh);bm.free()
 for poly in mesh.polygons:poly.use_smooth=True
 mesh.materials.append(canopy_material);crown_meshes.append(mesh)
core=bpy.data.objects.new('simplified canopy template',crown_meshes[0]);scene.collection.objects.link(core);core.hide_render=True
# surface leaves are shared by crown family; planting and camera remain unchanged.
import bisect
leaf_rng=random.Random(3052026)
leaf_materials=[]
for j,color in enumerate([(.0129,.031,.012),(.0229,.047,.0139),(.037,.0619,.0199),(.0509,.0759,.0261)]):
 material=bpy.data.materials.new('leaf tone %d'%j);material.use_nodes=True
 shader=material.node_tree.nodes.get('Principled BSDF')
 shader.inputs['Base Color'].default_value=(*color,1);shader.inputs['Roughness'].default_value=.42
 shader.inputs['Subsurface Weight'].default_value=.035
 leaf_materials.append(material)
near_leaf_materials=[]
for j,color in enumerate([(.0406,.0826,.0364),(.0665,.1155,.0441),(.1015,.1505,.0595),(.1386,.1876,.0756)]):
 material=bpy.data.materials.new('near leaf tone %d'%j);material.use_nodes=True
 shader=material.node_tree.nodes.get('Principled BSDF')
 shader.inputs['Base Color'].default_value=(*color,1);shader.inputs['Roughness'].default_value=.38
 shader.inputs['Subsurface Weight'].default_value=.035
 near_leaf_materials.append(material)
sunlit_leaf_materials=[]
for j,color in enumerate([(.121,.246,.108),(.198,.344,.131),(.303,.448,.177),(.413,.559,.225)]):
 material=bpy.data.materials.new('sunlit leaf tone %d'%j);material.use_nodes=True
 shader=material.node_tree.nodes.get('Principled BSDF')
 shader.inputs['Base Color'].default_value=(*color,1);shader.inputs['Roughness'].default_value=.38
 shader.inputs['Subsurface Weight'].default_value=.035
 sunlit_leaf_materials.append(material)
leaf_meshes=[];near_leaf_meshes=[];sunlit_leaf_meshes=[]
for family,source in enumerate(crown_meshes):
 source.calc_loop_triangles();triangles=[];weights=[];total=0
 for tri in source.loop_triangles:
  a,b,c=[source.vertices[index].co.copy() for index in tri.vertices]
  cross=(b-a).cross(c-a);triangle_area=cross.length*.5
  if triangle_area<1e-9:continue
  triangles.append((a,b,c,cross.normalized()));total+=triangle_area;weights.append(total)
 vertices=[];faces=[];tones=[]
 def add_leaf(center,normal,forward,length,tone):
  side=normal.cross(forward).normalized();base=len(vertices)
  vertices.extend([tuple(center+normal*length*.13),tuple(center-forward*length*.5),tuple(center+side*length*.23),tuple(center+forward*length*.5),tuple(center-side*length*.23)])
  for k in range(4):faces.append((base,base+1+(k+1)%4,base+1+k));tones.append(tone)
 for j in range(7500):
  a,b,c,normal=triangles[bisect.bisect_left(weights,leaf_rng.random()*total)]
  u=math.sqrt(leaf_rng.random());w=leaf_rng.random()
  center=a*(1-u)+b*(u*(1-w))+c*(u*w)+normal*.014
  tangent=normal.cross(Vector((0,0,1)))
  if tangent.length<.05:tangent=normal.cross(Vector((0,1,0)))
  tangent.normalize();bitangent=normal.cross(tangent).normalized()
  angle=leaf_rng.random()*math.tau
  forward=(tangent*math.cos(angle)+bitangent*math.sin(angle)+normal*leaf_rng.uniform(-.3,.3)).normalized()
  add_leaf(center,normal,forward,leaf_rng.uniform(.085,.155),leaf_rng.randrange(4))
 # sparse branching shoots interrupt the surface shell with small irregular extensions.
 shoot_rng=random.Random(305900+family)
 for j in range(550):
  a,b,c,normal=triangles[bisect.bisect_left(weights,shoot_rng.random()*total)]
  if normal.z<-.45:continue
  u=math.sqrt(shoot_rng.random());w=shoot_rng.random()
  start=a*(1-u)+b*(u*(1-w))+c*(u*w)
  tangent=normal.cross(Vector((0,0,1)))
  if tangent.length<.05:tangent=normal.cross(Vector((0,1,0)))
  tangent.normalize()
  axis=(normal*.65+tangent*shoot_rng.uniform(-.65,.65)+Vector((0,0,.35))).normalized()
  length=shoot_rng.uniform(.13,.28);tip=start+axis*length
  side=axis.cross(Vector((0,0,1)))
  if side.length<.05:side=axis.cross(Vector((0,1,0)))
  side.normalize();up=axis.cross(side).normalized()
  radius=shoot_rng.uniform(.0025,.0045);base=len(vertices)
  for center,width in [(start-normal*.025,radius),(tip,radius*.2)]:
   for k in range(3):
    angle=k*math.tau/3;vertices.append(tuple(center+(side*math.cos(angle)+up*math.sin(angle))*width))
  for k in range(3):faces.append((base+k,base+(k+1)%3,base+3+(k+1)%3,base+3+k));tones.append(4)
  faces.extend([(base+2,base+1,base),(base+3,base+4,base+5)]);tones.extend([4,4])
  for k in range(12):
   t=shoot_rng.uniform(.22,1);angle=shoot_rng.random()*math.tau
   radial=side*math.cos(angle)+up*math.sin(angle)
   center=start+axis*length*t+radial*shoot_rng.uniform(.008,.035)
   leaf_normal=(Vector((0,0,.65))+normal*.25+radial*.45).normalized()
   forward=(axis*.45+radial*.8).normalized()
   add_leaf(center,leaf_normal,forward,shoot_rng.uniform(.035,.07)*(1-.2*t),shoot_rng.randrange(4))
 mesh=bpy.data.meshes.new('fine surface leaves %02d'%family);mesh.from_pydata(vertices,[],faces);mesh.update()
 for material in leaf_materials:mesh.materials.append(material)
 mesh.materials.append(bark)
 for j,poly in enumerate(mesh.polygons):poly.material_index=tones[j]
 leaf_meshes.append(mesh)
 near=mesh.copy();near.materials.clear()
 for material in near_leaf_materials:near.materials.append(material)
 near.materials.append(bark);near_leaf_meshes.append(near)
 bright=mesh.copy();bright.materials.clear()
 for material in sunlit_leaf_materials:bright.materials.append(material)
 bright.materials.append(bark);sunlit_leaf_meshes.append(bright)
# the shaded supporting masses get a fine grain instead of a smooth plastic surface.
for node in canopy_material.node_tree.nodes:
 if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=100
 if node.type=='BUMP':node.inputs['Distance'].default_value=.012
print('Fine foliage templates ready',flush=True)
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
  r=stand_rng.uniform(2.2,8.6)
  z=height(x,y)+r*.72+r*stand_rng.uniform(0,3.3)
  crown_specs.append((len(crown_specs),(x,y,z),(r,r*stand_rng.uniform(.8,1.3),r*stand_rng.uniform(.9,1.6)),(0,0,stand_rng.random()*math.tau)))
# lifting the crowns onto trunks opened the bank up, but what showed through was smooth pale
# terrain rather than the dark gaps the reference has. an understory fills in underneath so the
# openings read as shadow between trees instead of exposed ground.
under_rng=random.Random(30671)
for group in range(48):
 side=-1 if group%2 else 1
 cx=side*under_rng.uniform(42,160);cy=under_rng.uniform(10,330)
 for j in range(19):
  x=under_rng.gauss(cx,19);y=under_rng.gauss(cy,25)
  if y<0 or y>345 or abs(x)<34-y/330*4:continue
  r=under_rng.uniform(1.6,4.2)
  z=height(x,y)+r*.55
  crown_specs.append((len(crown_specs),(x,y,z),(r,r*under_rng.uniform(.85,1.25),r*under_rng.uniform(.8,1.2)),(0,0,under_rng.random()*math.tau)))
# small uneven fingers overlap the stair edges while keeping the ascent legible.
for side,cy,amount in [(-1,95,70),(1,195,85),(-1,280,60),(1,35,55)]:
 for j in range(amount):
  y=random.gauss(cy,16);r=random.uniform(3,7)
  edge=29-y/330*5.5
  x=side*(edge+random.uniform(0,13))
  z=max(0,y*150/330)+r*.45
  crown_specs.append((len(crown_specs),(x,y,z),(r,r,r*1.2),(0,0,random.random()*math.tau)))
# a middle layer bridges the gap between the banks and the distant silhouettes, so the forest
# recedes continuously rather than jumping from planting to backdrop.
layer_rng=random.Random(30713)
for group in range(34):
 side=-1 if group%2 else 1
 cx=side*layer_rng.uniform(70,300);cy=layer_rng.uniform(350,505)
 for j in range(22):
  x=layer_rng.gauss(cx,38);y=layer_rng.gauss(cy,30)
  if y<340 or y>520:continue
  r=layer_rng.uniform(5,13)
  z=max(0,(y-330)*.16)+r*layer_rng.uniform(.8,2.4)
  crown_specs.append((len(crown_specs),(x,y,z),(r,r*layer_rng.uniform(.85,1.25),r*layer_rng.uniform(.9,1.5)),(0,0,layer_rng.random()*math.tau)))
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
shore_rng=random.Random(30631)
shore_material=mat('lit shoreline canopy',(.0246,.0508,.0229),(.127,.1925,.086),1,.2)
sunlit_material=mat('sunlit shoreline canopy',(.0511,.0964,.0452),(.2409,.3293,.1622),1,.2)
sunstruck_material=mat('sunstruck edge canopy',(.060,.098,.050),(.262,.312,.172),1,.2)
shore_meshes=[];sunlit_meshes=[];sunstruck_meshes=[]
for mesh in crown_meshes:
 copy=mesh.copy();copy.materials.clear();copy.materials.append(shore_material);shore_meshes.append(copy)
 lit=mesh.copy();lit.materials.clear();lit.materials.append(sunlit_material);sunlit_meshes.append(lit)
 struck=mesh.copy();struck.materials.clear();struck.materials.append(sunstruck_material);sunstruck_meshes.append(struck)
# a tree crown standing in front of the left trunk, its top in the light and its base lost in the
# dark bank below. the frame edge and the trunk behind it keep this from reading as a floating mass.
edge_rng=random.Random(30683)
edge_specs=[]
for j in range(44):
 t=edge_rng.random()
 x=-163+edge_rng.gauss(0,10);y=82+edge_rng.gauss(0,13)
 z=104+t*34+edge_rng.gauss(0,5)
 r=edge_rng.uniform(4,10)*(1-.3*t)
 edge_specs.append((len(edge_specs),(x,y,z),(r,r*edge_rng.uniform(.8,1.2),r*edge_rng.uniform(.75,1.15)),(0,0,edge_rng.random()*math.tau)))
shore_specs=[]
for side,cx,cy,count in [(1,76,24,34),(-1,86,14,28)]:
 for j in range(count):
  x=side*(cx+shore_rng.gauss(0,17));y=cy+shore_rng.gauss(0,15)
  r=shore_rng.uniform(3.5,9.5)
  z=height(x,y)+r*.6
  shore_specs.append((len(shore_specs),(x,y,z),(r,r*shore_rng.uniform(.85,1.2),r*shore_rng.uniform(.9,1.4)),(0,0,shore_rng.random()*math.tau)))
cling_rng=random.Random(30647)
cling_specs=[]
for tx,ty,tr_r,zlo,zhi,profile in trunk_info:
 for j in range(620):
  t=cling_rng.random()**.8
  z=zlo+60+t*(zhi-zlo-120)
  ang=cling_rng.random()*math.tau
  here=profile[min(len(profile)-1,int((z-zlo)/(zhi-zlo)*len(profile)))]
  rad=here*cling_rng.uniform(.86,.99)
  x=tx+math.cos(ang)*rad;y=ty+math.sin(ang)*rad
  r=cling_rng.uniform(1.8,5.5)*(1-.3*t)
  lit=math.cos(ang-math.radians(116))>-.05
  cling_specs.append((len(cling_specs),(x,y,z),(r,r*cling_rng.uniform(.8,1.2),r*cling_rng.uniform(.9,1.5)),(0,0,cling_rng.random()*math.tau),lit))
# planting laps over both ends of the wall, as in the reference, instead of leaving it cut off
# in clear air. kept out of crown_specs so it does not pick up fine leaves at this distance.
plinth_rng=random.Random(30659)
plinth_specs=[]
for side in (-1,1):
 for j in range(46):
  x=side*plinth_rng.uniform(74,142);y=plinth_rng.uniform(316,332)
  z=150+plinth_rng.random()**.7*74
  r=plinth_rng.uniform(6,17)
  plinth_specs.append((len(plinth_specs),(x,y,z),(r,r*plinth_rng.uniform(.8,1.2),r*plinth_rng.uniform(.85,1.3)),(0,0,plinth_rng.random()*math.tau)))
reed_rng=random.Random(30707)
reed_material=mat('shaded shoreline growth',(.0042,.0101,.0053),(.0231,.0384,.0165),1,.2)
reed_meshes=[]
for mesh in crown_meshes:
 copy=mesh.copy();copy.materials.clear();copy.materials.append(reed_material);reed_meshes.append(copy)
reed_specs=[]
for j in range(64):
 x=reed_rng.uniform(48,104);y=reed_rng.uniform(-112,-40)
 r=reed_rng.uniform(1.4,4.6)
 z=r*.42-.6
 reed_specs.append((len(reed_specs),(x,y,z),(r,r*reed_rng.uniform(.8,1.3),r*reed_rng.uniform(.7,1.1)),(0,0,reed_rng.random()*math.tau)))
water=bpy.data.materials.new('deep green clear water');water.use_nodes=True;p=water.node_tree.nodes.get('Principled BSDF');# the reference is dark at the top because the flanking forest runs unbroken off the top corners,
# not because crowns hang in the middle of the sky. free floating blobs were tried and rejected
# in an earlier pass; these are continuous columns rooted in the banks and stacked past the frame.
def frame_top_z(y,f):
 # screen height is linear in tangent rather than angle, so a fraction down from the top edge
 # has to map through tan; .50679 is the half sensor over the lens, .226 the camera tilt.
 return 36+(y+240)*math.tan(.226+math.atan(.50679*(1-2*f)))
overhead_specs=[]
over_rng=random.Random(30592)
for side in (-1,1):
 for column in range(13):
  y=over_rng.uniform(260,760);d=y+240
  # sit the column just inside the frame edge so it reads as the forest continuing past the crop.
  cx=side*d*.50679*over_rng.uniform(.66,1.06)
  top=frame_top_z(y,over_rng.uniform(-.08,.05))
  steps=9
  for j in range(steps):
   t=j/(steps-1)
   z=90+(top-90)*t
   r=d*over_rng.uniform(.030,.052)*(1-.25*t)
   x=cx+over_rng.gauss(0,d*.045)
   yy=y+over_rng.gauss(0,32)
   overhead_specs.append((len(overhead_specs),(x,yy,z),(r,r*over_rng.uniform(.85,1.2),r*over_rng.uniform(.7,1.05)),(0,0,over_rng.random()*math.tau)))
# a deep transmissive pond read as the darkest thing in frame; in the reference it is among
# the palest, a milky green carrying light back into the bottom of the composition.
p.inputs['Base Color'].default_value=(.068,.116,.089,1);p.inputs['Roughness'].default_value=.30;p.inputs['IOR'].default_value=1.333;p.inputs['Transmission Weight'].default_value=.22
n=water.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=3;n.inputs['Detail'].default_value=2
b=water.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.14;b.inputs['Distance'].default_value=.07;water.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);water.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,-130,.03));o=bpy.context.object;o.name='pond';o.scale=(350,350,1);o.data.materials.append(water)
padmat=mat('lily pad waxy surface',(.098,.152,.071),(.386,.452,.282),14,.006,.4)
# the difference map put the reference bottom corners near 78 where ours sat at 44. that light
# is crowded pale pads close to camera, not brighter water; a sparse dark scatter reads as a slab.
# a dedicated generator keeps the planting and shoreline above from moving with these.
pad_rng=random.Random(30617)
for i in range(250):
 side=-1 if i%2 else 1
 near=pad_rng.random()<.58
 if 34<i<196:
  # the reference packs large pads into its bottom left corner, the brightest cell in the frame.
  x=-pad_rng.uniform(60,120);y=pad_rng.uniform(-106,-44);r=pad_rng.uniform(1.5,3.1)
 elif i>240:x=pad_rng.uniform(-9,9);y=pad_rng.uniform(-130,-20);r=pad_rng.uniform(.6,1.7)
 elif near:x=side*pad_rng.uniform(40,235);y=pad_rng.uniform(-250,-50);r=pad_rng.uniform(1.6,4.4)
 else:x=side*pad_rng.uniform(15,150);y=pad_rng.uniform(-150,-5);r=pad_rng.uniform(.6,1.7)
 rot=pad_rng.random()*math.tau;vs=[(x,y,.075)]
 for j in range(31):
  a=rot+.15+j/30*(math.tau-.38);vs.append((x+math.cos(a)*r,y+math.sin(a)*r,.075+.025*math.sin(j/30*math.pi)))
 fs=[(0,j,j+1) for j in range(1,31)]
 me=bpy.data.meshes.new('notched pad');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('lily pad',me);scene.collection.objects.link(o);me.materials.append(padmat)
em=bpy.data.materials.new('warm lamp glass');em.use_nodes=True;p=em.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.7,.28,.07,1);p.inputs['Emission Color'].default_value=(1,.42,.12,1);p.inputs['Emission Strength'].default_value=4
box('recessed entrance light',(0,336.8,161.6),(8,.45,.22),em)
for i in range(9):
 t=i/8;y=5+t*318;z=y*150/330
 for side in [-1,1]:
  x=side*(30-t*5.5)
  box('lamp post',(x,y,z+2.3),(.34,.34,4.6),metal)
  box('lamp hood',(x,y,z+4.8),(2.6,2.1,.28),metal,.08)
  box('amber lamp',(x,y,z+4.5),(1.2,.95,.34),em)
  d=bpy.data.lights.new('lamp pool','POINT');d.energy=260;d.color=(1,.48,.19);d.shadow_soft_size=.9;o=bpy.data.objects.new('lamp pool',d);scene.collection.objects.link(o);o.location=(x,y,z+4.3)
area('entrance warmth',(0,336,159),(0,341,156),1100,6,(1,.52,.27))
FILL=.52
def soft(name,loc,energy,size,color):
 d=bpy.data.lights.new(name,'POINT');d.energy=energy*FILL;d.shadow_soft_size=size;d.color=color
 o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc
soft('open sky',(-100,80,650),1500000,250,(.76,.85,.88))
soft('stone light',(-90,250,440),620000,110,(.84,.89,.86))
soft('pond opening',(-80,-160,170),820000,120,(.73,.86,.77))
# broad local openings reveal a few crown tops while the giant trunks stay shaded.
soft('left canopy opening',(-65,95,160),110000,55,(.83,.88,.72))
soft('right canopy opening',(85,235,265),120000,65,(.66,.79,.83))
soft('stair skylight',(0,130,190),110000,90,(.78,.85,.86))
soft('near bank opening',(100,5,110),160000,35,(.83,.89,.73))

key=bpy.data.lights.new('canopy key','SUN');key.energy=1.82;key.angle=math.radians(30);key.color=(.93,.95,.86)
keyobj=bpy.data.objects.new('canopy key',key);scene.collection.objects.link(keyobj)
keyobj.rotation_euler=(math.radians(39),0,math.radians(26))
vol=bpy.data.materials.new('distance haze');vol.use_nodes=True;ns=vol.node_tree.nodes;ns.clear()
v=ns.new('ShaderNodeVolumePrincipled');v.inputs['Density'].default_value=.00065;v.inputs['Color'].default_value=(.24,.31,.37,1);v.inputs['Anisotropy'].default_value=.2
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
sky_split=ns.new('ShaderNodeSeparateXYZ');sky_fade=ns.new('ShaderNodeMapRange');sky_fade.clamp=True
sky_fade.inputs['From Min'].default_value=.27;sky_fade.inputs['From Max'].default_value=.5
sky_fade.inputs['To Min'].default_value=1.0;sky_fade.inputs['To Max'].default_value=.52
vol.node_tree.links.new(coord.outputs['Generated'],sky_split.inputs[0])
vol.node_tree.links.new(sky_split.outputs['Z'],sky_fade.inputs['Value'])
height_scale=ns.new('ShaderNodeMath');height_scale.operation='MULTIPLY'
vol.node_tree.links.new(multiply.outputs[0],height_scale.inputs[0])
vol.node_tree.links.new(sky_fade.outputs['Result'],height_scale.inputs[1])
vol.node_tree.links.new(height_scale.outputs[0],v.inputs['Density'])
# a faint distant ambient contribution closes the black gaps without lighting the near trunks.
ambient=ns.new('ShaderNodeMapRange');ambient.clamp=True
ambient.inputs['From Min'].default_value=.0006;ambient.inputs['From Max'].default_value=.0027
ambient.inputs['To Min'].default_value=0;ambient.inputs['To Max'].default_value=.00021
vol.node_tree.links.new(fade.outputs['Result'],ambient.inputs['Value'])
v.inputs['Emission Color'].default_value=(.10,.16,.22,1)
vol.node_tree.links.new(ambient.outputs['Result'],v.inputs['Emission Strength'])
box('atmosphere',(0,1250,2000),(6000,3300,5000),vol)
bpy.ops.object.camera_add(location=(0,-240,36));camera=bpy.context.object;camera.name='distant reference camera';camera.data.lens=35.518;camera.data.clip_end=20000
camera.rotation_euler=(math.pi/2+.226,0,0);scene.camera=camera
# link distant crowns after primitive construction to avoid repeated scene updates.
back_meshes=[]
for mesh in crown_meshes:
 back=mesh.copy();back.materials.clear();back.materials.append(distant_bark);back_meshes.append(back)
for idx,loc,scale,rot in crown_specs:
 family=int(abs(loc[0]*13.17+loc[1]*7.31))%len(crown_meshes)
 emergent=loc[1]<640 and loc[2]-height(loc[0],loc[1])>19 and (loc[0]<26 or loc[2]<86)
 if loc[1]>650:mesh=back_meshes[family]
 elif loc[1]<12:mesh=shore_meshes[family]
 elif emergent:mesh=sunlit_meshes[family]
 else:mesh=crown_meshes[family]
 o=bpy.data.objects.new('canopy lobe %03d'%idx,mesh);scene.collection.objects.link(o);o.location=loc;o.scale=scale;o.rotation_euler=rot
 if loc[1]<365 and abs(loc[0])<265:
  foliage=(sunlit_leaf_meshes if loc[0]>0 else near_leaf_meshes) if loc[1]<12 else near_leaf_meshes if emergent else leaf_meshes
  leaves=bpy.data.objects.new('fine foliage %03d'%idx,foliage[family]);scene.collection.objects.link(leaves)
  leaves.location=loc;leaves.scale=scale;leaves.rotation_euler=rot
for idx,loc,scale,rot in shore_specs:
 family=int(abs(loc[0]*7.9+loc[1]*3.3))%len(shore_meshes)
 if loc[0]>0:bank=sunstruck_meshes if loc[2]>height(loc[0],loc[1])+2 else sunlit_meshes
 else:bank=shore_meshes
 o=bpy.data.objects.new('shoreline stand %03d'%idx,bank[family]);scene.collection.objects.link(o)
 o.location=loc;o.scale=scale;o.rotation_euler=rot
 foliage=sunlit_leaf_meshes if loc[0]>0 else near_leaf_meshes
 leaves=bpy.data.objects.new('shoreline foliage %03d'%idx,foliage[family]);scene.collection.objects.link(leaves)
 leaves.location=loc;leaves.scale=scale;leaves.rotation_euler=rot
for idx,loc,scale,rot,lit in cling_specs:
 family=int(abs(loc[0]*5.1+loc[2]*2.7))%len(crown_meshes)
 o=bpy.data.objects.new('trunk cling %03d'%idx,crown_meshes[family]);scene.collection.objects.link(o)
 o.location=loc;o.scale=scale;o.rotation_euler=rot
for idx,loc,scale,rot in plinth_specs:
 family=int(abs(loc[0]*6.3+loc[2]*4.1))%len(crown_meshes)
 o=bpy.data.objects.new('plinth planting %03d'%idx,crown_meshes[family]);scene.collection.objects.link(o)
 o.location=loc;o.scale=scale;o.rotation_euler=rot
for idx,loc,scale,rot in edge_specs:
 family=int(abs(loc[0]*4.7+loc[2]*3.1))%len(sunstruck_meshes)
 o=bpy.data.objects.new('sunstruck edge tree %03d'%idx,sunstruck_meshes[family]);scene.collection.objects.link(o)
 o.location=loc;o.scale=scale;o.rotation_euler=rot
 leaves=bpy.data.objects.new('sunstruck edge foliage %03d'%idx,sunlit_leaf_meshes[family]);scene.collection.objects.link(leaves)
 leaves.location=loc;leaves.scale=scale;leaves.rotation_euler=rot
for idx,loc,scale,rot in reed_specs:
 family=int(abs(loc[0]*8.3+loc[1]*5.9))%len(reed_meshes)
 o=bpy.data.objects.new('shoreline growth %03d'%idx,reed_meshes[family]);scene.collection.objects.link(o)
 o.location=loc;o.scale=scale;o.rotation_euler=rot
 leaves=bpy.data.objects.new('shoreline growth foliage %03d'%idx,leaf_meshes[family]);scene.collection.objects.link(leaves)
 leaves.location=loc;leaves.scale=scale;leaves.rotation_euler=rot
# overhead masses stay bare blockout; leaves scaled for a six metre crown would be absurd here.
for idx,loc,scale,rot in overhead_specs:
 family=int(abs(loc[0]*11.3+loc[1]*5.7))%len(crown_meshes)
 o=bpy.data.objects.new('overhead canopy %03d'%idx,crown_meshes[family]);scene.collection.objects.link(o)
 o.location=loc;o.scale=scale;o.rotation_euler=rot
# metres: architecture is monumental, while ordinary crowns stay small beside it.
# the camera relationship was solved above; this unit conversion preserves it.
for o in scene.objects:
 o.location*=3;o.scale*=3
 if o.type=='LIGHT':
  if o.data.type!='SUN':o.data.energy*=9
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
if not QUICK:bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cathedral-softkey-study.blend'))
print('Scene ready; rendering',flush=True)
bpy.ops.render.render(write_still=True)
