"""What geometry sits behind a given difference map cell, in world coordinates.

blender --background --factory-startup study.blend --python tools/probe_frame_cells.py -- 10,0 10,8 11,0

Pass cells as row,col after a bare --. Use this instead of deriving positions by hand: builders lay out
in working units and multiply by three at the end, so hand computed placements land three times out.
"""
import bpy, sys
from mathutils import Vector
args=[a for a in sys.argv[sys.argv.index('--')+1:]] if '--' in sys.argv else []
cells=[tuple(int(v) for v in a.split(',')) for a in args] or [(9,9),(10,8),(10,0),(11,0)]
G=12
scene=bpy.context.scene; cam=scene.camera
dg=bpy.context.evaluated_depsgraph_get()
frame=[cam.matrix_world @ c for c in cam.data.view_frame(scene=scene)]
tr,br,bl,tl=frame            # blender returns top-right, bottom-right, bottom-left, top-left
origin=cam.matrix_world.translation
print('camera at',tuple(round(v,1) for v in origin))
for r,c in cells:
    u=(c+.5)/G; v=(r+.5)/G                       # v measured downward from the top
    top=tl.lerp(tr,u); bot=bl.lerp(br,u)
    target=top.lerp(bot,v)
    d=(target-origin).normalized()
    hit,loc,nor,idx,obj,mat=scene.ray_cast(dg,origin,d)
    if hit:
        print('r%-2d c%-2d  hit %-28s at (%7.1f,%7.1f,%7.1f)  dist %6.0f'
              %(r,c,obj.name[:28],loc.x,loc.y,loc.z,(loc-origin).length))
    else:
        print('r%-2d c%-2d  no hit'%(r,c))
