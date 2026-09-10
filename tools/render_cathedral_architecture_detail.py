"""Render a close detail from the saved architecture study without moving its camera."""
import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'renders/cathedral-architecture-study.blend'))
scene=bpy.context.scene
scene.render.resolution_x=3600;scene.render.resolution_y=3600
scene.render.resolution_percentage=100
scene.render.use_border=True;scene.render.use_crop_to_border=True
scene.render.border_min_x=.425;scene.render.border_max_x=.575
scene.render.border_min_y=.435;scene.render.border_max_y=.615
scene.cycles.samples=64
scene.render.filepath=str(root/'renders/cathedral-architecture-detail.png')
# the saved full composition remains unchanged; this is only a separate inspection render.
bpy.ops.render.render(write_still=True)
