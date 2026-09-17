"""Small visible hillside patches built from the proven branching crown."""
import bpy
from mathutils import Vector
from cathedral_crown import build_crown


def replace_visible_patch(scene, spread=False, upper=False, banks=None, detail='full', extended=False, tiered=False):
    camera=scene.camera
    bpy.context.view_layer.update()
    depsgraph=bpy.context.evaluated_depsgraph_get()
    selected={}
    reshaped=set()
    anchors=[(.33,.48)] if not spread else [(.33,.48),(.67,.53)]
    if upper:anchors += [(.30,.40),(.72,.43)]
    if banks:anchors += [(.24,.63)]
    if banks=='both':anchors += [(.76,.64)]
    if extended:anchors += [(.35,.55),(.64,.46)]
    per_patch=12 if not spread else 24
    # choose actual frontmost crowns through the final camera, not hidden trees whose
    # centres happen to project into the same area. keep all surrounding planting.
    for patch_index,(ax,ay) in enumerate(anchors):
        upper_patch=upper and patch_index>=2
        wanted=16 if banks and patch_index>=4 else 12 if upper_patch else per_patch
        found=0
        offsets=sorted(((i*.012,j*.014) for i in range(-5,6) for j in range(-5,6)),key=lambda p:p[0]*p[0]+p[1]*p[1])
        for dx,dy in offsets:
            direction=Vector(((ax+dx-.5)*camera.data.sensor_width/camera.data.lens,(.5-ay-dy)*camera.data.sensor_width/camera.data.lens,-1))
            direction=camera.matrix_world.to_3x3()@direction.normalized()
            hit,loc,normal,index,obj,matrix=scene.ray_cast(depsgraph,camera.location,direction,distance=10000)
            if upper_patch:
                # viewport raycasts include shadow-only flags and hidden support meshes.
                # step past those surfaces when selecting the new upper-edge patches.
                for unused in range(64):
                    if not hit or (obj.visible_camera and not obj.hide_render):break
                    hit,loc,normal,index,obj,matrix=scene.ray_cast(depsgraph,loc+direction*.01,direction,distance=10000)
            prefixes=('canopy lobe ','fine foliage ','plinth planting ') if upper_patch else ('canopy lobe ','fine foliage ')
            if not hit or not obj.name.startswith(prefixes):continue
            suffix=obj.name.rsplit(' ',1)[1]
            if obj.name.startswith('plinth planting '):crown=bpy.data.objects[obj.name];leaves=None
            else:
                crown=bpy.data.objects.get('canopy lobe '+suffix);leaves=bpy.data.objects.get('fine foliage '+suffix)
                if leaves and crown and (crown.location-leaves.location).length>.001:leaves=None
            if crown is None or crown.name in selected:continue
            if leaves is None and not upper_patch:continue
            selected[crown.name]=(crown,leaves);found+=1
            if tiered and patch_index>=6:reshaped.add(crown.name)
            if found==wanted:break
        assert found==wanted,(found,wanted)
    first=next(iter(selected.values()))[1]
    mesh=build_crown([slot.material for slot in first.material_slots],layered=True,natural=True,distant=detail=='lean')
    tiered_mesh=build_crown([slot.material for slot in first.material_slots],layered=True,natural=True,distant=detail=='lean',tiered=True) if reshaped else None
    paired=[(c,l) for c,l in selected.values() if l is not None]
    added=[]
    for crown,leaves in selected.values():
        if leaves is None:
            # the raised-wall planting has no leaf layer. borrow tones from its nearest
            # paired crown, while keeping the original planting transform and archive mesh.
            nearby=min(paired,key=lambda pair:(pair[0].location-crown.location).length)[1]
            materials=[slot.material for slot in nearby.material_slots]
            leaves=bpy.data.objects.new('branch replacement '+crown.name,mesh);scene.collection.objects.link(leaves)
            leaves.matrix_world=crown.matrix_world.copy();added.append(leaves.name)
        else:materials=[slot.material for slot in leaves.material_slots]
        leaves.data=tiered_mesh if crown.name in reshaped else mesh
        for slot,material in zip(leaves.material_slots,materials):slot.link='OBJECT';slot.material=material
        crown.hide_render=True
    scene['branch_patch_reshaped']=','.join(sorted(reshaped))
    scene['branch_patch_added']=','.join(added)
    scene['branch_patch_targets']=','.join(sorted(selected))
    print('Branch patch:',len(selected),'visible crowns replaced; existing transforms retained',flush=True)
