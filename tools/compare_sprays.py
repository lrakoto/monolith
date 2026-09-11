import bpy
import numpy as np
from pathlib import Path
import argparse, sys
parser=argparse.ArgumentParser()
parser.add_argument('--variant', default='sprays', choices=('sprays','hero-crown','hero-canopy'))
parser.add_argument('--baseline', choices=('lace','hero-crown'), default='lace')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=Path(__file__).resolve().parents[1]
files=[root/'reference/midjourney-index2.png', root/('renders/cathedral-'+args.baseline+'-study.png'), root/('renders/cathedral-'+args.variant+'-study.png')]
patches=[]
for path in files:
    image=bpy.data.images.load(str(path));image.colorspace_settings.name='Non-Color'
    w,h=image.size
    a=np.empty(w*h*4,dtype=np.float32);image.pixels.foreach_get(a)
    a=a.reshape(h,w,4)[::-1]
    crop=a[int(h*.68):int(h*.94),int(w*.63):w]
    ys=np.linspace(0,crop.shape[0]-1,400).astype(int)
    xs=np.linspace(0,crop.shape[1]-1,570).astype(int)
    patches.append(crop[ys[:,None],xs])
    lum=(a[:,:,:3]@np.array([.2126,.7152,.0722]))*255
    bounds=np.linspace(0,h,13).astype(int);xb=np.linspace(0,w,13).astype(int)
    cells=np.array([[lum[bounds[r]:bounds[r+1],xb[c]:xb[c+1]].mean() for c in range(12)] for r in range(12)])
    if len(patches)==1:reference=cells
    print(path.name, 'cell RMS',round(float(np.sqrt(((cells-reference)**2).mean())),3),'mean',round(float(lum.mean()),3),flush=True)
out=np.concatenate(patches,axis=1)
im=bpy.data.images.new('reference | lace | branch sprays',out.shape[1],out.shape[0],alpha=False)
im.pixels.foreach_set(out[::-1].ravel());im.filepath_raw=str(root/('renders/cathedral-'+args.variant+'-comparison.png'));im.file_format='PNG';im.save()
print('Saved comparison',flush=True)
