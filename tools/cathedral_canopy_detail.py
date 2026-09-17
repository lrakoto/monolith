"""Isolated hillside crown shading and finer surface leaf experiments."""
import bpy
import math


def refine_canopy(scene, fine=False, broken=False, dense=False):
    # keep the planted volume intact; smaller whole crowns previously exposed bare banks.
    # darkening only the supporting shell lets actual leaf geometry carry the highlights.
    shaded={}; meshes={};warped={};count=0
    for crown in list(scene.objects):
        if not crown.name.startswith('canopy lobe '):continue
        x,y,z=(v/3 for v in crown.location)
        if not (43<abs(x)<265 and 12<y<365):continue
        leaves=bpy.data.objects.get('fine foliage '+crown.name.rsplit(' ',1)[1])
        if leaves is None or (leaves.location-crown.location).length>.001:continue
        for slot in crown.material_slots:
            original=slot.material
            if original is None:continue
            if original.name not in shaded:
                mat=original.copy();mat.name='recessed crown support '+original.name
                ns,links=mat.node_tree.nodes,mat.node_tree.links
                shader=next(n for n in ns if n.type=='BSDF_PRINCIPLED')
                color=shader.inputs['Base Color']
                multiply=ns.new('ShaderNodeMixRGB');multiply.blend_type='MULTIPLY'
                multiply.inputs[0].default_value=1;multiply.inputs[2].default_value=(.38,.38,.38,1)
                if color.is_linked:links.new(color.links[0].from_socket,multiply.inputs[1])
                else:multiply.inputs[1].default_value=color.default_value
                links.new(multiply.outputs[0],color);shader.inputs['Roughness'].default_value=1
                if broken:shader.inputs['Specular IOR Level'].default_value=0
                shaded[original.name]=mat
            slot.link='OBJECT';slot.material=shaded[original.name]
        if fine:
            source=leaves.data
            if source.name not in meshes:
                # the first7500 five-vertex fans are the broad surface leaves. split each
                # into three smaller offset leaves; retain the branching shoots verbatim.
                assert len(source.vertices)>37500
                vertices=[];faces=[];tones=[]
                for i in range(7500):
                    points=[source.vertices[i*5+j].co.copy() for j in range(5)]
                    centre=sum(points[1:],points[0]*0)/4
                    forward=points[3]-points[1];side=points[2]-points[4]
                    tone=source.polygons[i*4].material_index
                    for along,across in ((-.24,-.16),(.22,-.10),(.02,.25)):
                        shift=forward*along+side*across
                        offset=len(vertices)
                        if dense:
                            vertices.extend(tuple(centre+(p-centre)*.58+shift) for p in points)
                            for k in range(4):faces.append((offset,offset+1+(k+1)%4,offset+1+k));tones.append(tone)
                        else:
                            # at this distance a small triangular blade is sufficient. three
                            # blades use fewer faces than the old four-face folded leaf.
                            width=.24 if broken else .14
                            for along_leaf,across_leaf in ((-.29,-width),(-.29,width),(.38,0)):
                                vertices.append(tuple(centre+shift+forward*along_leaf+side*across_leaf))
                            faces.append((offset,offset+1,offset+2));tones.append(tone)
                offset=len(vertices)-37500
                vertices.extend(tuple(v.co) for v in list(source.vertices)[37500:])
                for poly in list(source.polygons)[30000:]:
                    assert min(poly.vertices)>=37500
                    faces.append(tuple(v+offset for v in poly.vertices));tones.append(poly.material_index)
                mesh=bpy.data.meshes.new('finer canopy leaves '+source.name)
                mesh.from_pydata(vertices,[],faces);mesh.update()
                for mat in source.materials:mesh.materials.append(mat)
                for poly,tone in zip(mesh.polygons,tones):poly.material_index=tone
                meshes[source.name]=mesh
            leaves.data=meshes[source.name]
        if broken:
            # warp shells and leaves together. retain the lower cover, but shear and
            # flatten the upper lobes so every crown does not end in a round cap.
            for obj in (crown,leaves):
                source=obj.data
                if source.name not in warped:
                    mesh=source.copy();mesh.name='broken canopy silhouette '+source.name
                    for v in mesh.vertices:
                        x,y,z=v.co
                        top=max(0,min(1,(z+.25)/.65))
                        v.co.x=x+.15*math.sin(y*7+z*4)*top
                        v.co.y=y+.08*math.cos(x*8-z*3)*top
                        v.co.z=z-.22*max(z,0)+.08*math.sin(x*11+y*7)*top
                    mesh.update();warped[source.name]=mesh
                obj.data=warped[source.name]
        count+=1
    assert count>100,count
    print('Canopy detail:',count,'paired crowns; finer leaves',fine,'; transforms preserved',flush=True)
