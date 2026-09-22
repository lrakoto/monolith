"""A few low emergent plants break the flat foreground water planting."""
import math
import random
import bpy


def add_shore_shoots(scene, gathered=False):
    assert 'foreground emergent shoots' not in scene.objects
    rng=random.Random(305918)
    materials=[]
    for index,color in enumerate(((.025,.052,.018,1),(.045,.079,.025,1),(.062,.105,.029,1))):
        material=bpy.data.materials.new('emergent shore green %d'%index);material.use_nodes=True
        shader=material.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Base Color'].default_value=tuple(c*(1.6 if gathered else 1) for c in color[:3])+(1,)
        shader.inputs['Roughness'].default_value=.58
        materials.append(material)
    vertices=[];faces=[];tones=[];count=0
    # the central water remains empty. these small edge plants give the floating
    # colonies a few vertical interruptions without adding a reflecting light.
    patches=((-162,-625),(-200,-565),(-185,-520),(-245,-460),(175,-650),(220,-580))
    if gathered:patches=((-176,-619),(-206,-558),(-247,-462),(175,-647))
    for cx,cy in patches:
        for unused in range(28 if gathered else 9):
            x=cx+rng.uniform(-5,5) if gathered else cx+rng.uniform(-1.8,1.8)
            y=cy+rng.uniform(-8,8) if gathered else cy+rng.uniform(-1.8,1.8)
            angle=rng.random()*math.tau;height=rng.uniform(5,10);lean=rng.uniform(1.2,4)
            width=rng.uniform(.45,.85);tone=rng.randrange(3);offset=len(vertices)
            if gathered:height=rng.uniform(2,6.5);lean=rng.uniform(3,7);width=rng.uniform(.25,.7)
            for step in range(9):
                t=step/8;w=width*math.sin(math.pi*t)**.7
                center=(x+math.cos(angle)*lean*t*t,y+math.sin(angle)*lean*t*t,.3+height*(t-.12*t*t))
                for side in (-1,1):
                    vertices.append((center[0]-side*math.sin(angle)*w,center[1]+side*math.cos(angle)*w,center[2]))
            for step in range(8):
                k=offset+step*2;faces.append((k,k+1,k+3,k+2));tones.append(tone)
            count+=1
    mesh=bpy.data.meshes.new('low emergent shore blades');mesh.from_pydata(vertices,[],faces);mesh.update()
    for material in materials:mesh.materials.append(material)
    for face,tone in zip(mesh.polygons,tones):face.material_index=tone;face.use_smooth=True
    obj=bpy.data.objects.new('foreground emergent shoots',mesh);scene.collection.objects.link(obj)
    scene['shore_shoot_count']=count
    print('Emergent shore:',count,'blades in',len(patches),'edge patches; water, lights and existing plants unchanged',flush=True)
