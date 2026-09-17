"""One deliberately shaped shoreline crown, in normalized local coordinates."""
import math
import random
import hashlib
import struct
import bpy
from mathutils import Vector


def build_crown(materials, layered=False, natural=False, clustered=False, distant=False, tiered=False, shoot_density=1.0):
    rng = random.Random(305911)
    detail_rng = random.Random(305914)
    verts, faces, tones = [], [], []
    layout=hashlib.sha256()
    leaf_count=0

    def basis(axis):
        side = axis.cross(Vector((0, 0, 1)))
        if side.length < .01:
            side = axis.cross(Vector((0, 1, 0)))
        side.normalize()
        return side, axis.cross(side).normalized()

    def branch(a, b, width):
        layout.update(struct.pack('!7d',*a,*b,width))
        sides=3 if distant else 5
        axis = (b-a).normalized()
        side, up = basis(axis)
        offset = len(verts)
        for point, radius in ((a, width), (b, width*.45)):
            for k in range(sides):
                angle = k*math.tau/sides
                verts.append(tuple(point + radius*(side*math.cos(angle)+up*math.sin(angle))))
        for k in range(sides):
            faces.append((offset+k, offset+(k+1)%sides, offset+sides+(k+1)%sides, offset+sides+k))
            tones.append(4)

    def leaf(point, forward, length, tone):
        nonlocal leaf_count
        leaf_count+=1
        forward.normalize()
        normal = Vector((rng.uniform(-.9,.9), rng.uniform(-.9,.9), rng.uniform(.3,1)))
        if layered:
            # neighbouring sprays share their value so highlights describe branches, not confetti.
            patch = math.sin(point.x*9 + point.z*3) * math.cos(point.y*7 - point.z*4)
            value = .38 + point.z*.4 + patch*.30
            tone = max(0, min(3, int(value*4)))
            normal.x *= .5; normal.y *= .5
        side = normal.cross(forward).normalized()
        normal = forward.cross(side).normalized()
        offset = len(verts)
        if natural:
            # a separate stream keeps every branch and leaf attachment fixed across the comparison.
            length *= max(.42, min(1.65, detail_rng.lognormvariate(-.12, .38)))
            width = length * detail_rng.uniform(.16, .31)
            fold = length * detail_rng.uniform(.025, .10)
            skew = detail_rng.uniform(-.16, .16)
            layout.update(struct.pack('!13d',*point,*forward,*normal,length,width,fold,skew))
            # distant leaves retain every attachment and their folded surface. widening
            # the four-point rim preserves the old eight-point leaf's projected area.
            rim=[(0,0),(.48,-1.2096),(1,0),(.48,1.2096)] if distant else [(0,0),(.20,-.64),(.48,-1),(.78,-.62),(1,0),(.78,.62),(.48,1),(.20,.64)]
            for t,w in rim:
                verts.append(tuple(point + forward*length*t + side*(width*w+skew*length*t*(1-t))))
            verts.append(tuple(point+forward*length*.48+normal*fold))
            for k in range(len(rim)):
                faces.append((offset+k,offset+(k+1)%len(rim),offset+len(rim)));tones.append(tone)
            return
        verts.extend(tuple(v) for v in (point, point+forward*length*.45-side*length*.25,
                     point+forward*length, point+forward*length*.45+side*length*.25,
                     point+forward*length*.45+normal*length*.09))
        for k in range(4):
            faces.append((offset+k, offset+(k+1)%4, offset+4));tones.append(tone)

    # overlapping but unequal branch systems form a broad shoulder and a sloping right edge.
    groups = [((-.62,-.03,.10),(.37,.35,.28)), ((-.29,-.10,.39),(.44,.38,.35)),
              ((.10,.07,.48),(.43,.39,.36)), ((.48,.03,.24),(.39,.38,.31)),
              ((.76,.02,-.04),(.27,.29,.23)), ((-.38,.43,.14),(.37,.34,.32)),
              ((.27,.45,.27),(.48,.30,.36)), ((-.36,-.40,-.07),(.39,.29,.27)),
              ((.08,-.43,.03),(.40,.32,.30)), ((.49,-.30,-.13),(.35,.32,.28)),
              ((.06,-.03,-.14),(.42,.38,.32))]
    if layered:
        groups = [((-.70,-.01,.07),(.43,.34,.20)), ((-.32,-.06,.30),(.43,.38,.26)),
                  ((.06,.12,.44),(.49,.38,.23)), ((.50,.08,.19),(.42,.36,.24)),
                  ((.88,.08,-.09),(.23,.29,.17)), ((-.44,.43,.11),(.35,.34,.27)),
                  ((.26,.46,.25),(.44,.30,.26)), ((-.44,-.40,-.14),(.38,.29,.19)),
                  ((.01,-.40,-.02),(.37,.31,.24)), ((.57,-.29,-.20),(.31,.29,.19)),
                  ((.08,-.02,-.20),(.35,.34,.22))]
    if tiered:
        # flatten individual branch fans and stagger their heights rather than adding
        # leaves. the older crown piles overlapping round groups into one dark mass.
        lifts=(.02,-.08,.06,-.06,.03,.10,-.04,-.06,.08,-.02,-.08)
        groups=[((x,y,z+lifts[i]),(rx*1.06,ry*.94,rz*.62))
                for i,((x,y,z),(rx,ry,rz)) in enumerate(groups)]
    root = Vector((.08,.05,-.82));fork = Vector((-.08,.08,-.30))
    branch(root, fork, .028)
    for index,(location,radii) in enumerate(groups):
        center=Vector(location)
        elbow=fork.lerp(center,.55)+Vector((0,.06,-.05))
        branch(fork,elbow,.014);branch(elbow,center,.008)
        for j in range(max(1,round(([100,150,130,90,65,120,110,95,80,55,70][index] if layered else 120)*shoot_density))):
            direction=Vector((rng.gauss(0,1),rng.gauss(0,1),rng.gauss(0,1))).normalized()
            radius=rng.uniform(.35,1)**.5
            end=center+Vector(tuple(direction[k]*radii[k]*radius for k in range(3)))
            start=center.lerp(elbow,rng.uniform(0,.45))
            branch(start,end,.0018)
            axis=(end-start).normalized();side,up=basis(axis)
            for k in range(28):
                t=rng.uniform(.38,1.08)
                if clustered:
                    # move the same leaves into growth sprays, leaving the inner woody stems legible.
                    jitter = (t-.73)*.18
                    t = (.60,.86,1.07)[k % 3] + jitter
                angle=k*2.39996+rng.uniform(-.4,.4)
                radial=side*math.cos(angle)+up*math.sin(angle)
                point=start.lerp(end,t)+radial*rng.uniform(.009,.033)
                forward=axis*.3+radial*.8+Vector((0,0,rng.uniform(-.35,.2)))
                leaf(point,forward,rng.uniform(.024,.048),rng.randrange(4))
        # uneven curtains connect the lit crown to the shaded bank without a continuous skirt.
        if center.y < .15:
            for trail in range(max(1,round(([6,11,5,8,4,7,7,12,7,10,5][index] if layered else 9)*min(1.0,shoot_density*2.5)))):
                start=center+Vector((rng.uniform(-radii[0],radii[0]),-radii[1]*rng.uniform(.5,.9),-radii[2]*.2))
                length=rng.uniform(.18,.58)
                prior=start
                for segment in range(12):
                    t=(segment+1)/12
                    point=start+Vector((math.sin(t*4+trail)*.024, -.07*t, -length*t))
                    branch(prior,point,.0012*(1-t*.7))
                    for k in range(3):
                        forward=Vector((rng.uniform(-1,1),rng.uniform(-.6,.6),rng.uniform(-.8,.1)))
                        leaf(point,forward,rng.uniform(.016,.036)*(1-t*.4),rng.randrange(4))
                    prior=point
    mesh=bpy.data.meshes.new('distant folded-leaf crown' if distant else 'full shoreline crown with hanging sprays')
    mesh.from_pydata(verts,[],faces);mesh.update()
    mesh['layout_hash']=layout.hexdigest();mesh['leaf_count']=leaf_count
    mesh['detail_mode']='lean' if distant else 'full'
    mesh['tiered']=tiered
    for index, material in enumerate(materials):
        if natural and index < 4:
            material = material.copy()
            material.name = 'soft leaf surface %d' % index
            material.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = .62
        mesh.materials.append(material)
    for polygon,tone in zip(mesh.polygons,tones):
        polygon.material_index=tone
        if natural and tone < 4:polygon.use_smooth=True
    print('Hero crown:',len(verts),'vertices;',len(faces),'faces',flush=True)
    return mesh
