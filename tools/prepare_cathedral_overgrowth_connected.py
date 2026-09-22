"""Connect the new wall growth to the existing bank instead of perching on the ledge."""
from pathlib import Path
import bpy
root=Path(__file__).resolve().parents[1]/'renders'
out=root/'cathedral-overgrown-connected-cloud-v1.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(root/'cathedral-overgrown-cloud-v1.blend'))
s=bpy.context.scene
objects=[o for o in s.objects if o.name.startswith('overgrown wall ')]
assert len(objects)==7
for o in objects:
 # grow downward into the old canopy while retaining an uneven upper silhouette.
 o.location.z-=25
 o.location.y-=15
 o.scale.z*=1.65
 o.scale.x*=1.22
 o.scale.y*=1.15
s.render.filepath='//'+out.stem+'.png'
bpy.ops.file.pack_all();assert not bpy.utils.blend_paths(absolute=True,packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
print('SAVED',out,flush=True)
