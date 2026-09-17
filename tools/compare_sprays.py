import bpy
import numpy as np
from pathlib import Path
import argparse, sys
parser=argparse.ArgumentParser()
parser.add_argument('--variant', default='sprays', choices=('sprays','hero-crown','hero-canopy','hero-leafcraft','hero-sprig','stair-edges','stair-weathered','monument-stone','inscription-stone','entrance-depth','left-bank-masses','left-bank-contour','right-bank-contour','canopy-groups'))
parser.add_argument('--baseline', choices=('lace','hero-crown','hero-canopy','hero-leafcraft','stair-edges','stair-weathered','monument-stone','inscription-stone','entrance-depth','left-bank-masses'), default='lace')
parser.add_argument('--render-name', help='filename stem of a separately named render; also names its comparison')
parser.add_argument('--baseline-name', help='filename stem of a separately named baseline render')
parser.add_argument('--crop', nargs=4, type=float, metavar=('X0','Y0','X1','Y1'), help='normalized top-down comparison crop')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
if args.crop:
    x0,y0,x1,y1=args.crop
    assert 0<=x0<x1<=1 and 0<=y0<y1<=1

root=Path(__file__).resolve().parents[1]
render_name=args.render_name or 'cathedral-'+args.variant+'-study'
assert Path(render_name).name == render_name, 'render name must be a filename stem'
comparison_name=(args.render_name or 'cathedral-'+args.variant)+'-comparison'
if args.crop:comparison_name+='-crop'
baseline_name=args.baseline_name or 'cathedral-'+args.baseline+'-study'
assert Path(baseline_name).name == baseline_name, 'baseline name must be a filename stem'
files=[root/'reference/midjourney-index2.png', root/('renders/'+baseline_name+'.png'), root/('renders/'+render_name+'.png')]
patches=[]
for path in files:
    image=bpy.data.images.load(str(path));image.colorspace_settings.name='Non-Color'
    w,h=image.size
    a=np.empty(w*h*4,dtype=np.float32);image.pixels.foreach_get(a)
    a=a.reshape(h,w,4)[::-1]
    if args.variant in ('inscription-stone','entrance-depth'):
        crop=a[int(h*.40):int(h*.55),int(w*.39):int(w*.61)]
    elif args.variant == 'monument-stone':
        crop=a[int(h*.06):int(h*.55),int(w*.39):int(w*.61)]
    else:
        crop=a[int(h*.52):int(h*.89),int(w*.37):int(w*.63)] if args.variant.startswith('stair-') else a[int(h*.68):int(h*.94),int(w*.63):w]
    ch,cw=(400,587) if args.variant in ('inscription-stone','entrance-depth') else (700,314) if args.variant == 'monument-stone' else (650,457) if args.variant.startswith('stair-') else (400,570)
    if args.variant in ('left-bank-masses','left-bank-contour','right-bank-contour','canopy-groups'): crop=a; ch=cw=600
    if args.crop:
        crop=a[int(h*y0):int(h*y1),int(w*x0):int(w*x1)]
        cw=450;ch=round(cw*(y1-y0)/(x1-x0))
    ys=np.linspace(0,crop.shape[0]-1,ch).astype(int)
    xs=np.linspace(0,crop.shape[1]-1,cw).astype(int)
    patches.append(crop[ys[:,None],xs])
    lum=(a[:,:,:3]@np.array([.2126,.7152,.0722]))*255
    bounds=np.linspace(0,h,13).astype(int);xb=np.linspace(0,w,13).astype(int)
    cells=np.array([[lum[bounds[r]:bounds[r+1],xb[c]:xb[c+1]].mean() for c in range(12)] for r in range(12)])
    if len(patches)==1:reference=cells
    print(path.name, 'cell RMS',round(float(np.sqrt(((cells-reference)**2).mean())),3),'mean',round(float(lum.mean()),3),flush=True)
out=np.concatenate(patches,axis=1)
im=bpy.data.images.new('reference | baseline | study',out.shape[1],out.shape[0],alpha=False)
im.pixels.foreach_set(out[::-1].ravel());im.filepath_raw=str(root/('renders/'+comparison_name+'.png'));im.file_format='PNG';im.save()
print('Saved comparison',flush=True)
