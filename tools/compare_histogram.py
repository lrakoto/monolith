"""How the luminance is distributed, band by band, against the reference.

blender --background --factory-startup --python tools/compare_histogram.py -- \
  ref=reference/midjourney-index2.png ours=renders/latest.png

The difference map and the percentile summary both miss shape. This is what showed that half the
reference sits in a narrow 30 to 40 band while ours spread across 30 to 50, and that our tower
occupies three times the reference's share above 100.
"""
import bpy, numpy as np, sys
args=sys.argv[sys.argv.index('--')+1:]
def lum(path):
    img=bpy.data.images.load(path); img.colorspace_settings.name='Non-Color'
    w,h=img.size; a=np.empty(w*h*4,dtype=np.float32); img.pixels.foreach_get(a)
    a=a.reshape(h,w,4)
    return ((0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2])*255).flatten()
names=[a.split('=')[0] for a in args]; data=[lum(a.split('=')[1]) for a in args]
edges=list(range(0,101,10))+[130,180,256]
print('%-9s'%'band'+''.join('%10s'%n for n in names))
for i in range(len(edges)-1):
    lo,hi=edges[i],edges[i+1]
    print('%-9s'%('%d-%d'%(lo,hi))+''.join('%9.1f%%'%(100*((d>=lo)&(d<hi)).mean()) for d in data))
