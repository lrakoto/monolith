"""Restore a few slender existing stems in front of the distant procedural backdrop."""
from pathlib import Path
import bpy
root=Path(__file__).resolve().parents[1]/'renders';out=root/'cathedral-overgrown-remote-stems-cloud-v1.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(root/'cathedral-overgrown-wall-tones-cloud-v1.blend'))
s=bpy.context.scene
names=[f'distant forest trunk {i:02}' for i in (1,5,11,23,24,27)]
for name in names:
 o=bpy.data.objects[name];assert o.hide_render
 # thin stems sit behind the monument; the two framing trunks keep their scale hierarchy.
 o.hide_render=False;o.scale.x*=.28;o.scale.y*=.28
s.render.filepath='//'+out.stem+'.png';s['restored_remote_stems']=','.join(names)
bpy.ops.file.pack_all();assert not bpy.utils.blend_paths(absolute=True,packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);print('SAVED',out,flush=True)
