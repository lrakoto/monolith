"""Luminance statistics for a render against the reference. Run under blender for numpy.

blender --background --factory-startup --python tools/compare_value_stats.py -- ref=a.png mine=b.png

Summary numbers only. They hide where the error is, so prefer compare_diff_map.py to decide
what to work on; this is for checking the shape of the histogram once you know.
"""
import bpy, numpy as np, sys
def load(path):
    img=bpy.data.images.load(path)
    img.colorspace_settings.name='Non-Color'   # raw stored values, not linearised
    w,h=img.size
    a=np.empty(w*h*4,dtype=np.float32); img.pixels.foreach_get(a)
    a=a.reshape(h,w,4)[::-1,:,:3]              # blender rows are bottom-up
    return a
def lum(a): return (0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2])*255.0
def frac(L,x0,x1,y0,y1):
    h,w=L.shape
    return float(L[int(y0*h):int(y1*h), int(x0*w):int(x1*w)].mean())
rows=[]
for name,path in [(a.split('=')[0],a.split('=')[1]) for a in sys.argv[sys.argv.index('--')+1:]]:
    L=lum(load(path)); f=L.flatten()
    rows.append((name, dict(
        mean=L.mean(), p5=np.percentile(f,5), p50=np.percentile(f,50), p95=np.percentile(f,95),
        top=frac(L,0,1,0,.14), pond=frac(L,0,1,.88,1.0),
        edges=(frac(L,0,.13,0,1)+frac(L,.87,1,0,1))/2, centre=frac(L,.40,.60,0,1),
        contrast=np.percentile(f,95)-np.percentile(f,5))))
keys=['mean','p5','p50','p95','contrast','top','pond','edges','centre']
print('%-10s'%'metric'+''.join('%12s'%n for n,_ in rows))
for k in keys:
    print('%-10s'%k+''.join('%12.1f'%d[k] for _,d in rows))
print()
print('%-10s'%'edge/centre'+''.join('%12.2f'%(d['edges']/d['centre']) for _,d in rows))
print('%-10s'%'pond/mean'+''.join('%12.2f'%(d['pond']/d['mean']) for _,d in rows))
