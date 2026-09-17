"""Foreground water planting arranged for the current distant camera."""
import math
import random
import bpy


def add_leaf_colonies(scene, gathered=False):
    # the old pads were scattered for a closer camera. cluster smaller overlapping leaves
    # along the new foreground edges and retain an open water channel toward the stairs.
    originals=[o for o in scene.objects if o.name=='lily pad' or o.name.startswith('lily pad.')]
    assert len(originals)==250,len(originals)
    source=originals[0].data.materials[0]
    for obj in originals: obj.hide_render=True
    materials=[]
    for i,factor in enumerate((.72,.88,1,1.12,1.26)):
        mat=source.copy();mat.name='foreground floating leaf tone %d'%i
        for node in mat.node_tree.nodes:
            if node.type=='VALTORGB':
                for stop in node.color_ramp.elements:
                    c=stop.color[:];stop.color=(*[v*factor for v in c[:3]],1)
            elif node.type=='BSDF_PRINCIPLED':node.inputs['Roughness'].default_value=.55
        materials.append(mat)
    rng=random.Random(917305)
    vertices=[];faces=[];tones=[];count=0
    colonies=[(-205,-560,42,62,240),(-270,-405,48,75,160),(-285,-210,44,38,110),
              (205,-560,42,58,210),(280,-375,45,65,150),(310,-185,45,38,90)]
    if gathered:
        colonies=[(-205,-560,24,43,360),(-270,-405,31,55,180),(-285,-210,32,30,100),
                  (230,-595,22,38,130),(300,-375,24,45,90),(310,-185,28,30,70)]
    for cx,cy,sx,sy,amount in colonies:
        for unused in range(amount):
            x=rng.gauss(cx,sx);y=rng.gauss(cy,sy)
            if abs(x)<85 or y<-690 or y>0:continue
            radius=rng.uniform(1.5,5.7);stretch=rng.uniform(.65,1.1);angle=rng.random()*math.tau
            z=.25+rng.uniform(.03,.13)
            offset=len(vertices);vertices.append((x,y,z))
            for k in range(24):
                a=.14+k/23*(math.tau-.28)
                r=radius*(1+.075*math.sin(a*3+angle))
                u=math.cos(a)*r;v=math.sin(a)*r*stretch
                vertices.append((x+u*math.cos(angle)-v*math.sin(angle),y+u*math.sin(angle)+v*math.cos(angle),z+.08*math.sin(a*2+angle)+radius*.025))
            tone=rng.choices(range(5),weights=(1,2,4,3,1))[0]
            for k in range(23):faces.append((offset,offset+k+1,offset+k+2));tones.append(tone)
            count+=1
    mesh=bpy.data.meshes.new('clustered floating leaf surfaces');mesh.from_pydata(vertices,[],faces);mesh.update()
    for mat in materials:mesh.materials.append(mat)
    for poly,tone in zip(mesh.polygons,tones):poly.material_index=tone;poly.use_smooth=True
    obj=bpy.data.objects.new('foreground floating leaf colonies',mesh);scene.collection.objects.link(obj)
    print('Foreground leaf colonies:',count,'leaves replace250 scattered pads; central channel left open',flush=True)


def add_shore_light(scene):
    # a downward pool reveals the near left leaves without flattening the distant forest.
    from mathutils import Vector
    light=bpy.data.lights.new('left foreground opening','AREA')
    light.energy=180000;light.shape='DISK';light.size=150
    light.color=(.91,1,.74)
    obj=bpy.data.objects.new('left foreground opening',light);scene.collection.objects.link(obj)
    obj.location=(-230,-500,150)
    obj.rotation_euler=(Vector((-205,-560,0))-obj.location).to_track_quat('-Z','Y').to_euler()
