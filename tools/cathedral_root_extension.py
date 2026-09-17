"""Bury the finite source trunk below the reshaped forest bank."""
import bpy


def extend_right_root(scene):
    trunk=bpy.data.objects['colossal trunk 1']
    mesh=trunk.data.copy();trunk.data=mesh
    # generated bark coordinates must retain the old bounds when the root grows.
    location=mesh.texspace_location.copy();size=mesh.texspace_size.copy()
    mesh.use_auto_texspace=False;mesh.texspace_location=location;mesh.texspace_size=size
    inverse=trunk.matrix_world.inverted()
    floor=min((trunk.matrix_world@v.co).z for v in mesh.vertices)
    moved=0
    for vertex in mesh.vertices:
        world=trunk.matrix_world@vertex.co
        weight=max(0.0,1-(world.z-floor)/120)
        if weight>0:
            world.z-=180*weight*weight
            vertex.co=inverse@world;moved+=1
    assert moved>0
    mesh.update();scene['extended_right_root_floor']=floor
    print('Right root extension:',moved,'vertices; upper trunk and bark coordinates retained',flush=True)
