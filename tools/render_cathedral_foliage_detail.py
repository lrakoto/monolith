"""Inspect the near canopy from the saved camera without changing the full scene."""
import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'renders/cathedral-foliage-study.blend'))
scene=bpy.context.scene
scene.render.resolution_x=3600;scene.render.resolution_y=3600
scene.render.resolution_percentage=100
scene.render.use_border=True;scene.render.use_crop_to_border=True
scene.render.border_min_x=.10;scene.render.border_max_x=.32
scene.render.border_min_y=.14;scene.render.border_max_y=.37
scene.cycles.samples=64
scene.render.filepath=str(root/'renders/cathedral-foliage-detail.png')
bpy.ops.render.render(write_still=True)
