"""Compare a more legible distant forest layer without moving the main composition."""
from pathlib import Path
import bpy
root=Path(__file__).resolve().parents[1]/'renders';out=root/'cathedral-overgrown-remote-depth-cloud-v1.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(root/'cathedral-overgrown-remote-stems-cloud-v1.blend'));s=bpy.context.scene
for name in s['restored_remote_stems'].split(','):
 o=bpy.data.objects[name];o.location.y-=650;o.scale.x*=1.5;o.scale.y*=1.5
s.render.filepath='//'+out.stem+'.png';bpy.ops.file.pack_all();assert not bpy.utils.blend_paths(absolute=True,packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);print('SAVED',out,flush=True)
