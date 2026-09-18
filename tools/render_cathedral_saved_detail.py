"""Render a repeatable detail crop from an existing local study without changing it."""
import argparse
from pathlib import Path
import sys
import bpy

parser=argparse.ArgumentParser()
parser.add_argument('--source',required=True,help='existing blend filename stem in renders')
parser.add_argument('--output',required=True,help='new PNG filename stem in renders')
parser.add_argument('--crop',required=True,nargs=4,type=float,metavar=('X0','Y0','X1','Y1'))
parser.add_argument('--resolution',type=int,default=2400)
parser.add_argument('--samples',type=int,default=64)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
root=Path(__file__).resolve().parents[1]/'renders'
assert all(Path(n).name==n and n not in ('.','..') for n in (args.source,args.output))
source=root/(args.source+'.blend');output=root/(args.output+'.png')
assert source.is_file(),source
assert not output.exists(),output
x0,y0,x1,y1=args.crop
assert 0<=x0<x1<=1 and 0<=y0<y1<=1
assert args.resolution>0 and args.samples>0
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene
# border coordinates in blender start at the bottom; our review crops start at the top.
s.render.resolution_x=s.render.resolution_y=args.resolution
s.render.resolution_percentage=100
s.cycles.samples=args.samples;s.cycles.device='CPU'
s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=x0;s.render.border_max_x=x1
s.render.border_min_y=1-y1;s.render.border_max_y=1-y0
s.render.filepath=str(output)
bpy.ops.render.render(write_still=True)
assert output.is_file(),output
