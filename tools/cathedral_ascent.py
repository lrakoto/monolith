"""A connected ascent adjustment with fixed summit and camera."""
import bpy
from mathutils import Vector


def raise_ascent(scene, lift):
    def warp_stone(z):
        # keep the entrance and lettering rigid; absorb the height change in the upper
        # spires so the approved top framing survives the longer-looking stair flight.
        return z + lift * max(0, min(1, (1350-z)/650))

    monument = bpy.data.objects['limestone monument']
    monument.data = monument.data.copy()
    inverse = monument.matrix_world.inverted()
    for vertex in monument.data.vertices:
        world = monument.matrix_world @ vertex.co
        world.z = warp_stone(world.z)
        vertex.co = inverse @ world
    monument.data.update()
    for obj in scene.objects:
        if obj.name.startswith('tread '):
            obj.location.z *= (450+lift)/450
            obj.scale.z *= (450+lift)/450
        elif obj.name in ('landing','entrance back wall','entrance warmth','recessed entrance light','305') or obj.name.startswith(('flanking wall ','wall cornice ','deep entrance warm detail','plinth planting ')):
            obj.location.z += lift
        elif obj.name.startswith(('lamp post','lamp hood','amber lamp','lamp pool')):
            obj.location.z += lift*max(0,min(1,obj.location.y/990))

    def bank_lift(x,y):
        if y <= 0 or y >= 1260: return 0
        side = max(0,min(1,(360-abs(x))/255))
        side = side*side*(3-2*side)
        back = max(0,min(1,(1260-y)/240))
        back = back*back*(3-2*back)
        return lift*min(1,y/990)*side*back

    bank = bpy.data.objects['simple forest banks']
    bank.data = bank.data.copy()
    inverse = bank.matrix_world.inverted()
    for vertex in bank.data.vertices:
        world = bank.matrix_world @ vertex.co
        world.z += bank_lift(world.x,world.y)
        vertex.co = inverse @ world
    bank.data.update()
    count = 0
    for obj in scene.objects:
        if obj.name.startswith(('canopy lobe ','fine foliage ','shoreline stand ','shoreline foliage ','sunstruck edge tree ','sunstruck edge foliage ')):
            amount = bank_lift(obj.location.x,obj.location.y)
            if amount:
                obj.location.z += amount; count += 1
    bpy.context.view_layer.update()
    steps = [o for o in scene.objects if o.name.startswith('tread ')]
    top = max((o.matrix_world @ Vector(v)).z for o in steps for v in o.bound_box)
    assert len(steps)==150 and abs(top-(450+lift))<.01
    summit = max((monument.matrix_world @ v.co).z for v in monument.data.vertices)
    assert abs(summit-1350)<.01
    print('Ascent raised:', lift, 'landing:', top, 'fixed summit:',summit,'adjacent planting:',count,flush=True)
