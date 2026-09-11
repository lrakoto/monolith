"""Magnified crop of one region, for comparing texture against the reference side by side.

blender --background --factory-startup --python tools/compare_crop.py -- src.png out.png x0 y0 x1 y1 scale

Coordinates are frame fractions. Texture frequency has to be judged at final resolution; the
600px preview reads fine detail as either coarse or absent.
"""
import bpy, numpy as np, sys
src,out,x0,y0,x1,y1,scale=sys.argv[sys.argv.index('--')+1:]
x0,y0,x1,y1,scale=float(x0),float(y0),float(x1),float(y1),int(scale)
img=bpy.data.images.load(src); img.colorspace_settings.name='Non-Color'
w,h=img.size; a=np.empty(w*h*4,dtype=np.float32); img.pixels.foreach_get(a)
a=a.reshape(h,w,4)[::-1]                                  # top-down
c=a[int(y0*h):int(y1*h), int(x0*w):int(x1*w)]
c=np.repeat(np.repeat(c,scale,axis=0),scale,axis=1)
o=bpy.data.images.new('crop',c.shape[1],c.shape[0],alpha=False)
o.pixels.foreach_set(c[::-1].ravel()); o.filepath_raw=out; o.file_format='PNG'; o.save()
print('wrote',out,c.shape)
