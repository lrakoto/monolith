"""Reduce distant canopy memory without moving branches or retained leaves."""
import bpy


def thin_distant_leaves(scene):
    prefixes=('distant folded-leaf crown','interlocking small forest crowns','fitted small forest crowns')
    meshes={o.data.name:o.data for o in scene.objects if o.type=='MESH' and not o.hide_render and o.data.name.startswith(prefixes)}
    changed=[];removed=0;old_faces=0;new_faces=0
    for name,source in meshes.items():
        faces=[];tones=[];smooth=[];leaf_count=0;index=0;kept_leaves=0
        while index<len(source.polygons):
            polygon=source.polygons[index]
            if polygon.material_index<4:
                group=[source.polygons[i] for i in range(index,index+4)]
                assert all(len(p.vertices)==3 and p.material_index==polygon.material_index for p in group),name
                assert len(set.intersection(*(set(p.vertices) for p in group)))==1,name
                leaf_count+=1;index+=4
                if leaf_count%3==0:removed+=1;continue
                kept_leaves+=1
            else:group=[polygon];index+=1
            for p in group:faces.append(tuple(p.vertices));tones.append(p.material_index);smooth.append(p.use_smooth)
        used=sorted({v for face in faces for v in face});remap={old:new for new,old in enumerate(used)}
        mesh=bpy.data.meshes.new('lighter '+name)
        mesh.from_pydata([tuple(source.vertices[i].co) for i in used],[],[tuple(remap[v] for v in face) for face in faces]);mesh.update()
        mesh.use_auto_texspace=False;mesh.texspace_location=source.texspace_location;mesh.texspace_size=source.texspace_size
        for mat in source.materials:mesh.materials.append(mat)
        for p,tone,soft in zip(mesh.polygons,tones,smooth):p.material_index=tone;p.use_smooth=soft
        mesh['retained_leaf_count']=kept_leaves;mesh['source_mesh']=name
        for obj in list(scene.objects):
            if obj.type!='MESH' or obj.data!=source:continue
            slots=[(slot.link,slot.material) for slot in obj.material_slots];obj.data=mesh
            for slot,(link,mat) in zip(obj.material_slots,slots):
                slot.link=link
                if link=='OBJECT':slot.material=mat
            changed.append(obj.name)
        old_faces+=len(source.polygons);new_faces+=len(mesh.polygons)
        # only generated replacement meshes are discarded from this new scene. old
        # blend files remain intact; freeing them here is the point of this memory test.
        assert source.users==0,name
        bpy.data.meshes.remove(source)
    assert changed
    scene['canopy_thinned_objects']=','.join(sorted(changed))
    print('Distant leaf thinning:',len(changed),'objects;',removed,'leaves removed per unique-template total;',old_faces,'->',new_faces,'faces',flush=True)
