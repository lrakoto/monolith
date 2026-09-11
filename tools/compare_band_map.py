"""Where one luminance band is over or under represented, cell by cell.

blender --background --factory-startup --python tools/compare_band_map.py -- \
  reference/midjourney-index2.png renders/latest.png 40 50

The histogram says which band is wrong and this says where it is. Together they found the largest
remaining structural difference: our upper middle frame is 100 percent in the 40 to 50 band where
the reference is at zero, because the reference has distant forest there and we have luminous haze.
"""
"""Where a luminance band is over or under represented, cell by cell."""
import bpy, numpy as np, sys
args=sys.argv[sys.argv.index('--')+1:]
ref_path, ren_path, lo, hi = args[0], args[1], float(args[2]), float(args[3])
G=12
def lum(path):
    img=bpy.data.images.load(path); img.colorspace_settings.name='Non-Color'
    w,h=img.size; a=np.empty(w*h*4,dtype=np.float32); img.pixels.foreach_get(a)
    a=a.reshape(h,w,4)[::-1]
    return (0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2])*255
def frac(L):
    h,w=L.shape; ys=np.linspace(0,h,G+1).astype(int); xs=np.linspace(0,w,G+1).astype(int)
    m=(L>=lo)&(L<hi)
    return np.array([[100*m[ys[r]:ys[r+1], xs[c]:xs[c+1]].mean() for c in range(G)] for r in range(G)])
R=frac(lum(ref_path)); M=frac(lum(ren_path)); D=M-R
print('share of each cell in the %g-%g band, render minus reference (percentage points)'%(lo,hi))
print('    '+''.join('%5d'%c for c in range(G)))
for r in range(G):
    print('%3d '%r+''.join('%5.0f'%D[r,c] for c in range(G)))
order=np.argsort(-np.abs(D).flatten())[:8]
print('\nlargest gaps')
for i in order:
    r,c=divmod(int(i),G)
    print('  r%-2d c%-2d  x %.2f-%.2f  y %.2f-%.2f   ref %5.1f%%  ours %5.1f%%  delta %+6.1f'
          %(r,c,c/G,(c+1)/G,r/G,(r+1)/G,R[r,c],M[r,c],D[r,c]))
