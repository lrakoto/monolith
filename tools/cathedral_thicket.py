"""Replace a few large round crowns with interlocking smaller branching trees."""
import math
import bpy
from mathutils import Vector, Matrix
from cathedral_crown import build_crown


def replace_thicket(scene, plinth=False, fitted=False, right=False, lower=False, fill=None, upper_plinth=None):
    camera=scene.camera; bpy.context.view_layer.update()
    depsgraph=bpy.context.evaluated_depsgraph_get();selected={};extra={}
    offsets=sorted(((i*.011,j*.013) for i in range(-6,7) for j in range(-6,7)),key=lambda p:p[0]**2+p[1]**2)
    for dx,dy in offsets:
        direction=Vector(((.35+dx-.5)*camera.data.sensor_width/camera.data.lens,(.5-.44-dy)*camera.data.sensor_width/camera.data.lens,-1))
        direction=camera.matrix_world.to_3x3()@direction.normalized();origin=camera.location
        for unused in range(64):
            hit,loc,normal,index,obj,matrix=scene.ray_cast(depsgraph,origin,direction,distance=10000)
            if not hit or (obj.visible_camera and not obj.hide_render):break
            origin=loc+direction*.01
        if not hit:continue
        if plinth and obj.name.startswith('plinth planting ') and len(extra)<8:
            extra[obj.name]=(obj,None)
        if not obj.name.startswith(('canopy lobe ','fine foliage ')):continue
        suffix=obj.name.rsplit(' ',1)[1]
        crown=bpy.data.objects.get('canopy lobe '+suffix);leaves=bpy.data.objects.get('fine foliage '+suffix)
        if crown is None or leaves is None or crown.hide_render or (crown.location-leaves.location).length>.001:continue
        if len(selected)<12:selected[crown.name]=(crown,leaves)
        if len(selected)==12 and (not plinth or len(extra)==8):break
    assert len(selected)==12,len(selected)
    if plinth:assert len(extra)==8,len(extra)
    paired=list(selected.values());selected.update(extra)
    base_targets=set(selected);right_paired=[]
    if right:
        new_pairs={};new_extra={}
        right_offsets=sorted(((i*.011,j*.013) for i in range(-9,10) for j in range(-9,10)),key=lambda p:p[0]**2+p[1]**2)
        for dx,dy in right_offsets:
            direction=Vector(((.65+dx-.5)*camera.data.sensor_width/camera.data.lens,(.5-.44-dy)*camera.data.sensor_width/camera.data.lens,-1))
            direction=camera.matrix_world.to_3x3()@direction.normalized();origin=camera.location
            for unused in range(64):
                hit,loc,normal,index,obj,matrix=scene.ray_cast(depsgraph,origin,direction,distance=10000)
                if not hit or (obj.visible_camera and not obj.hide_render):break
                origin=loc+direction*.01
            if not hit or obj.name in base_targets:continue
            if plinth and obj.name.startswith('plinth planting ') and len(new_extra)<3:
                new_extra[obj.name]=(bpy.data.objects[obj.name],None)
            if obj.name.startswith(('canopy lobe ','fine foliage ')):
                suffix=obj.name.rsplit(' ',1)[1]
                crown=bpy.data.objects.get('canopy lobe '+suffix);leaves=bpy.data.objects.get('fine foliage '+suffix)
                if crown is None or leaves is None or crown.hide_render or crown.name in base_targets or (crown.location-leaves.location).length>.001:continue
                if len(new_pairs)<12:new_pairs[crown.name]=(crown,leaves)
            if len(new_pairs)==12 and (not plinth or len(new_extra)==3):break
        assert len(new_pairs)==12,len(new_pairs)
        if plinth:assert len(new_extra)==3,len(new_extra)
        right_paired=list(new_pairs.values());selected.update(new_pairs);selected.update(new_extra)
    if lower:
        lower_pairs={}
        for dx,dy in offsets:
            direction=Vector(((.30+dx-.5)*camera.data.sensor_width/camera.data.lens,(.5-.64-dy)*camera.data.sensor_width/camera.data.lens,-1))
            direction=camera.matrix_world.to_3x3()@direction.normalized();origin=camera.location
            for unused in range(64):
                hit,loc,normal,index,obj,matrix=scene.ray_cast(depsgraph,origin,direction,distance=10000)
                if not hit or (obj.visible_camera and not obj.hide_render):break
                origin=loc+direction*.01
            if not hit or not obj.name.startswith(('canopy lobe ','fine foliage ')):continue
            suffix=obj.name.rsplit(' ',1)[1]
            crown=bpy.data.objects.get('canopy lobe '+suffix);leaves=bpy.data.objects.get('fine foliage '+suffix)
            if crown is None or leaves is None or crown.hide_render or crown.name in selected or (crown.location-leaves.location).length>.001:continue
            lower_pairs[crown.name]=(crown,leaves)
            if len(lower_pairs)==12:break
        assert len(lower_pairs)==12,len(lower_pairs)
        selected.update(lower_pairs)
    if fill:
        anchors=[(.69,.64)]
        if fill in ('both','left-edge','edges','inner','inner-left','inner-banks','inner-rise'):anchors.append((.31,.54))
        if fill in ('left-edge','edges','inner','inner-left','inner-banks','inner-rise'):anchors.append((.20,.54))
        if fill in ('edges','inner','inner-left','inner-banks','inner-rise'):anchors.append((.79,.57))
        if fill=='inner':anchors.extend(((.37,.64),(.63,.55)))
        if fill in ('inner-left','inner-banks','inner-rise'):anchors.append((.37,.64))
        if fill in ('inner-banks','inner-rise'):anchors.append((.63,.55))
        if fill=='inner-rise':anchors.append((.36,.51))
        for ax,ay in anchors:
            wanted=8 if (ax,ay) in ((.20,.54),(.79,.57),(.36,.51)) or (fill in ('inner-left','inner-banks','inner-rise') and (ax,ay) in ((.37,.64),(.63,.55))) else 16
            patch={}
            for dx,dy in offsets:
                direction=Vector(((ax+dx-.5)*camera.data.sensor_width/camera.data.lens,(.5-ay-dy)*camera.data.sensor_width/camera.data.lens,-1))
                direction=camera.matrix_world.to_3x3()@direction.normalized();origin=camera.location
                for unused in range(64):
                    hit,loc,normal,index,obj,matrix=scene.ray_cast(depsgraph,origin,direction,distance=10000)
                    if not hit or (obj.visible_camera and not obj.hide_render):break
                    origin=loc+direction*.01
                if not hit or not obj.name.startswith(('canopy lobe ','fine foliage ')):continue
                suffix=obj.name.rsplit(' ',1)[1]
                crown=bpy.data.objects.get('canopy lobe '+suffix);leaves=bpy.data.objects.get('fine foliage '+suffix)
                if crown is None or leaves is None or crown.hide_render or crown.name in selected or (crown.location-leaves.location).length>.001:continue
                patch[crown.name]=(crown,leaves)
                if len(patch)==wanted:break
            assert len(patch)==wanted,(ax,ay,len(patch))
            selected.update(patch)
    if upper_plinth:
        # these still-visible planting crowns were identified through the final camera.
        # fitting their replacements keeps the upper bank envelope while opening the texture.
        names=['plinth planting 020','plinth planting 038']
        if upper_plinth=='both':names+=['plinth planting 063','plinth planting 054']
        for name in names:
            crown=bpy.data.objects[name]
            assert not crown.hide_render and name not in selected,name
            selected[name]=(crown,None)
            if name in names[:2]:base_targets.add(name)
    first=next(iter(selected.values()))[1]
    small=build_crown([slot.material for slot in first.material_slots],layered=True,natural=True,distant=True,shoot_density=.12)
    verts=[];faces=[];tones=[]
    # several small unequal crowns fill the old envelope, rather than one enlarged
    # shoreline tree. their fine branches should read as a distant forest at this scale.
    groups=[((-.46,-.16,.05),(.48,.52,.52),0),((.05,-.25,.12),(.50,.48,.55),.7),
            ((.52,-.10,.02),(.43,.49,.48),1.6),((-.28,.30,.35),(.46,.45,.55),2.1),
            ((.28,.32,.30),(.49,.47,.52),-.5),((-.15,-.02,-.32),(.49,.51,.48),1.0),
            ((.40,.10,-.26),(.44,.47,.49),2.7)]
    for pos,scale,angle in groups:
        rotation=Matrix.Rotation(angle,3,'Z');offset=len(verts)
        for v in small.vertices:
            p=rotation@Vector(tuple(v.co[i]*scale[i] for i in range(3)))+Vector(pos)
            verts.append(tuple(p))
        for p in small.polygons:faces.append(tuple(offset+i for i in p.vertices));tones.append(p.material_index)
    mesh=bpy.data.meshes.new('interlocking small forest crowns');mesh.from_pydata(verts,[],faces);mesh.update()
    for mat in small.materials:mesh.materials.append(mat)
    for p,tone in zip(mesh.polygons,tones):p.material_index=tone;p.use_smooth=tone<4
    added=[];fitted_meshes={}
    def fit_mesh(source):
        if source.name not in fitted_meshes:
            fitted_mesh=mesh.copy();fitted_mesh.name='fitted small forest crowns '+source.name
            old_bounds=[(min(v.co[i] for v in source.vertices),max(v.co[i] for v in source.vertices)) for i in range(3)]
            new_bounds=[(min(v.co[i] for v in mesh.vertices),max(v.co[i] for v in mesh.vertices)) for i in range(3)]
            for vertex in fitted_mesh.vertices:
                for i,((lo,hi),(nlo,nhi)) in enumerate(zip(old_bounds,new_bounds)):
                    vertex.co[i]=lo+(vertex.co[i]-nlo)*(hi-lo)/(nhi-nlo)
            fitted_mesh.update();fitted_meshes[source.name]=fitted_mesh
        return fitted_meshes[source.name]
    for crown,leaves in selected.values():
        if leaves is None:
            nearby=min(paired if crown.name in base_targets else right_paired,key=lambda pair:(pair[0].location-crown.location).length)[1]
            mats=[slot.material for slot in nearby.material_slots]
            leaves=bpy.data.objects.new('thicket replacement '+crown.name,fit_mesh(crown.data) if fitted else mesh);scene.collection.objects.link(leaves)
            leaves.matrix_world=crown.matrix_world.copy();added.append(leaves.name)
        else:mats=[s.material for s in leaves.material_slots];leaves.data=mesh
        for slot,mat in zip(leaves.material_slots,mats):slot.link='OBJECT';slot.material=mat
        crown.hide_render=True
    scene['thicket_added']=','.join(added)
    scene['thicket_targets']=','.join(sorted(selected))
    print('Thicket:',len(selected),'crowns;',len(mesh.vertices),'vertices;',len(mesh.polygons),'faces',flush=True)
