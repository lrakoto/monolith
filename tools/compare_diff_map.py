"""Per cell difference between a render and the reference: where we are off, and by how much.

blender --background --factory-startup --python tools/compare_diff_map.py -- ref.png mine.png [out.png]

This is the measurement that decides what the next pass is. rms is a guide to where to look and
never the verdict: two passes here scored better while visibly getting worse, so read the image too.
"""
import bpy, numpy as np, sys
args=sys.argv[sys.argv.index('--')+1:]
ref_path, ren_path, out_png = args[0], args[1], (args[2] if len(args)>2 else '')
G=12   # grid cells per side; small enough to read as text, fine enough to localise

def load(path):
    img=bpy.data.images.load(path); img.colorspace_settings.name='Non-Color'
    w,h=img.size
    a=np.empty(w*h*4,dtype=np.float32); img.pixels.foreach_get(a)
    return a.reshape(h,w,4)[::-1,:,:3]                      # blender rows are bottom-up
def lum(a): return (0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2])*255.0
def cells(L):
    h,w=L.shape
    ys=np.linspace(0,h,G+1).astype(int); xs=np.linspace(0,w,G+1).astype(int)
    return np.array([[L[ys[r]:ys[r+1], xs[c]:xs[c+1]].mean() for c in range(G)] for r in range(G)])

R=cells(lum(load(ref_path))); M=cells(lum(load(ren_path))); D=M-R

print('delta per cell (render minus reference; + = we are too bright)')
print('    '+''.join('%5d'%c for c in range(G)))
for r in range(G):
    print('%3d '%r+''.join('%5.0f'%D[r,c] for c in range(G)))
print('\nrms %.1f   mean |delta| %.1f   worst %+.0f'%(np.sqrt((D**2).mean()),np.abs(D).mean(),D.flat[np.abs(D).argmax()]))
order=np.argsort(-np.abs(D).flatten())[:10]
print('\nworst cells (row,col are 0-%d from top-left; x,y are frame fractions)'%(G-1))
for i in order:
    r,c=divmod(int(i),G)
    print('  r%-2d c%-2d  x %.2f-%.2f  y %.2f-%.2f   ref %5.1f  ours %5.1f  delta %+6.1f'
          %(r,c,c/G,(c+1)/G,r/G,(r+1)/G,R[r,c],M[r,c],D[r,c]))

if out_png:
    # red where we are too bright, blue where too dark, mid grey where we match.
    S=48; img=bpy.data.images.new('diff',G*S,G*S,alpha=False)
    buf=np.zeros((G*S,G*S,4),dtype=np.float32); buf[...,3]=1
    scale=25.0
    for r in range(G):
        for c in range(G):
            t=float(np.clip(D[r,c]/scale,-1,1))
            col=(.14+.86*t,.14+.30*(1-abs(t)),.14-.86*t) if t>=0 else (.14+.86*t*0,.14+.30*(1-abs(t)),.14-.86*t)
            col=(max(0,min(1,col[0])),max(0,min(1,col[1])),max(0,min(1,col[2])))
            buf[r*S:(r+1)*S, c*S:(c+1)*S, :3]=col
    img.pixels.foreach_set(buf[::-1].ravel())
    img.filepath_raw=out_png; img.file_format='PNG'; img.save()
    print('\nwrote',out_png)
