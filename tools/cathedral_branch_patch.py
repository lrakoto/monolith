"""Small visible hillside patches built from the proven branching crown."""
import bpy
from mathutils import Vector
from cathedral_crown import build_crown


def replace_visible_patch(scene, spread=False):
    camera=scene.camera
    bpy.context.view_layer.update()
    depsgraph=bpy.context.evaluated_depsgraph_get()
    selected={}
    anchors=[(.33,.48)] if not spread else [(.33,.48),(.67,.53)]
    per_patch=12 if not spread else 24
    # choose actual frontmost crowns through the final camera, not hidden trees whose
    # centres happen to project into the same area. keep all surrounding planting.
    for ax,ay in anchors:
        found=0
        offsets=sorted(((i*.012,j*.014) for i in range(-5,6) for j in range(-5,6)),key=lambda p:p[0]*p[0]+p[1]*p[1])
        for dx,dy in offsets:
            direction=Vector(((ax+dx-.5)*camera.data.sensor_width/camera.data.lens,(.5-ay-dy)*camera.data.sensor_width/camera.data.lens,-1))
            direction=camera.matrix_world.to_3x3()@direction.normalized()
            hit,loc,normal,index,obj,matrix=scene.ray_cast(depsgraph,camera.location,direction,distance=10000)
            if not hit or not obj.name.startswith(('canopy lobe ','fine foliage ')):continue
            suffix=obj.name.rsplit(' ',1)[1]
            crown=bpy.data.objects.get('canopy lobe '+suffix);leaves=bpy.data.objects.get('fine foliage '+suffix)
            if crown is None or leaves is None or crown.name in selected:continue
            if (crown.location-leaves.location).length>.001:continue
            selected[crown.name]=(crown,leaves);found+=1
            if found==per_patch:break
        assert found==per_patch,(found,per_patch)
    first=next(iter(selected.values()))[1]
    mesh=build_crown([slot.material for slot in first.material_slots],layered=True,natural=True)
    for crown,leaves in selected.values():
        materials=[slot.material for slot in leaves.material_slots]
        leaves.data=mesh
        for slot,material in zip(leaves.material_slots,materials):slot.link='OBJECT';slot.material=material
        crown.hide_render=True
    scene['branch_patch_targets']=','.join(sorted(selected))
    print('Branch patch:',len(selected),'visible crowns replaced; existing transforms retained',flush=True)
