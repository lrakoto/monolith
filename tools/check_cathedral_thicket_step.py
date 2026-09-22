"""Verify a saved thicket continuation changes only its newly selected crowns."""
import argparse
from pathlib import Path
import sys
import bpy

parser=argparse.ArgumentParser()
parser.add_argument('--baseline',required=True)
parser.add_argument('--candidate',required=True)
parser.add_argument('--counts',required=True,nargs=2,type=int)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
root=Path(__file__).resolve().parents[1]/'renders'
def snapshot(stem):
    assert Path(stem).name==stem and stem not in ('.','..')
    bpy.ops.wm.open_mainfile(filepath=str(root/(stem+'.blend')))
    scene=bpy.context.scene
    objects={o.name:(tuple(v for row in o.matrix_world for v in row),o.hide_render,
             o.data.name if o.data else '',tuple(s.material.name if s.material else '' for s in o.material_slots)) for o in scene.objects}
    camera=scene.camera.data
    optics=tuple(getattr(camera,k) for k in ('type','lens','sensor_width','sensor_height','sensor_fit','shift_x','shift_y','clip_start','clip_end'))
    lights={o.name:(o.data.type,o.data.energy,tuple(o.data.color)) for o in scene.objects if o.type=='LIGHT'}
    bounds={o.name:tuple((min(v[i] for v in o.bound_box),max(v[i] for v in o.bound_box)) for i in range(3))
            for o in scene.objects if o.type=='MESH' and o.name.startswith(('plinth planting ','thicket replacement '))}
    return objects,optics,lights,scene['branch_patch_targets'],set(scene['thicket_targets'].split(',')),set(filter(None,scene['thicket_added'].split(','))),bounds
a=snapshot(args.baseline);b=snapshot(args.candidate)
assert a[1:4]==b[1:4]
assert (len(a[4]),len(b[4]))==tuple(args.counts) and a[4]<b[4]
extra=b[4]-a[4]
assert all(n.startswith(('canopy lobe ','plinth planting ')) for n in extra)
leaves={'fine foliage '+n.rsplit(' ',1)[1] for n in extra if n.startswith('canopy lobe ')}
new_objects={'thicket replacement '+n:n for n in extra if n.startswith('plinth planting ')}
assert set(b[0])==set(a[0])|set(new_objects)
assert b[5]==a[5]|set(new_objects)
for name,old in a[0].items():
    current=b[0][name]
    assert old[0]==current[0],name
    if name in extra:
        assert not old[1] and current[1] and old[2:]==current[2:],name
    elif name in leaves:
        assert old[1]==current[1] and old[3:]==current[3:],name
        assert old[2]!=current[2] and 'interlocking small forest crowns' in current[2],name
    else:assert old==current,name
for name,source in new_objects.items():
    current=b[0][name]
    # copying a matrix through blender's transform decomposition introduces float rounding.
    assert max(abs(x-y) for x,y in zip(current[0],a[0][source][0]))<.00001 and not current[1],name
    assert 'fitted small forest crowns' in current[2] and all(current[3]),name
    for (lo,hi),(source_lo,source_hi) in zip(b[6][name],a[6][source]):
        assert lo>=source_lo-.0001 and hi<=source_hi+.0001,(name,lo,hi,source_lo,source_hi)
print('PASS:',len(extra),'selected crowns;',len(new_objects),'fitted unpaired replacements; prior objects, camera optics, lights and material assignments preserved',flush=True)
