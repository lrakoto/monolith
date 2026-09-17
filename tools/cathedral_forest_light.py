"""Shadow-only canopy flags for a controlled cinematic lighting study."""
import math
import bpy
from mathutils import Vector


def add_canopy_shadows(scene):
    # large unseen canopy casts broad broken shadows; these lighting flags affect shadow
    # rays only, so they do not replace or obscure the visible forest meshes.
    scene.view_layers.update()
    direction = bpy.data.objects['canopy key'].matrix_world.to_quaternion() @ Vector((0,0,-1))
    assert direction.z < -.1
    material = bpy.data.materials.new('opaque canopy shade flag')
    material.use_nodes = True
    shader = material.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (.008,.012,.009,1)
    shader.inputs['Roughness'].default_value = 1
    for label, target, clearance, rx, ry, phase in (
        ('left',(-270,420,350),200,135,235,.3),
        ('right',(350,690,520),250,155,240,2.1),
    ):
        center = Vector(target)-direction*(clearance/-direction.z)
        vertices=[tuple(center)]
        for i in range(48):
            a=i*math.tau/48
            r=1+.13*math.sin(a*3+phase)+.09*math.sin(a*7-phase)
            vertices.append(tuple(center+Vector((math.cos(a)*rx*r,math.sin(a)*ry*r,0))))
        mesh=bpy.data.meshes.new('irregular canopy shade '+label)
        mesh.from_pydata(vertices,[],[(0,i+1,(i+1)%48+1) for i in range(48)])
        mesh.materials.append(material);mesh.update()
        obj=bpy.data.objects.new('forest shadow flag '+label,mesh);scene.collection.objects.link(obj)
        obj.visible_camera=False;obj.visible_diffuse=False;obj.visible_glossy=False
        obj.visible_transmission=False;obj.visible_volume_scatter=False;obj.visible_shadow=True
    print('Added two shadow-only canopy flags; camera-visible geometry, exposure and light energies unchanged',flush=True)


def add_entrance_wash(scene, lift, power=9000, size=30):
    # a soft fixture wash makes the entrance the destination without flattening its
    # dark recess or changing the forest exposure. aim away from the stair flight.
    light=bpy.data.lights.new('warm entrance facade wash','AREA')
    assert math.isfinite(power) and power>0 and math.isfinite(size) and size>0
    light.energy=power;light.color=(1,.48,.23);light.shape='DISK';light.size=size
    obj=bpy.data.objects.new('warm entrance facade wash',light);scene.collection.objects.link(obj)
    obj.location=(0,960,500+lift)
    target=Vector((0,992,490+lift))
    obj.rotation_euler=(target-obj.location).to_track_quat('-Z','Y').to_euler()
    print('Added warm entrance facade wash; existing lighting and geometry retained',flush=True)
