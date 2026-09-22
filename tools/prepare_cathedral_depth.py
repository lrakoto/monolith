"""Compare directional forest lighting with a restrained atmospheric-depth variant."""
from pathlib import Path
import bpy
root=Path(__file__).resolve().parents[1]/'renders'
for variant in ('directional-depth','atmospheric-depth'):
 out=root/f'cathedral-{variant}-cloud-v1.blend';assert not out.exists()
 bpy.ops.wm.open_mainfile(filepath=str(root/'cathedral-stone-grain-cloud-v1.blend'))
 s=bpy.context.scene
 before={o.name:(tuple(v for row in o.matrix_world for v in row),o.hide_render,o.data.name if o.data else None) for o in s.objects}
 print('WORLD LINKS',[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in s.world.node_tree.links])
 # sun gives the crowns directional modeling; broad fills keep the staircase readable.
 bpy.data.objects['canopy key'].data.energy*=1.8
 bpy.data.objects['open sky'].data.energy*=.55
 bpy.data.objects['pond opening'].data.energy*=.65
 bpy.data.objects['near bank opening'].data.energy*=2.4
 bpy.data.objects['stone light'].data.energy*=1.2
 for n in s.world.node_tree.nodes:
  if n.type=='BACKGROUND' and n.name=='Background':n.inputs['Strength'].default_value*=.55
 if variant=='atmospheric-depth':
  # a finite distant veil leaves the foreground water clear and strengthens the scale cue.
  bpy.ops.mesh.primitive_cube_add(size=2,location=(0,1250,900))
  veil=bpy.context.object;veil.name='distant atmospheric veil';veil.scale=(1700,850,1200)
  mat=bpy.data.materials.new('distant forest haze');mat.use_nodes=True
  nodes=mat.node_tree.nodes;nodes.clear();output=nodes.new('ShaderNodeOutputMaterial');volume=nodes.new('ShaderNodeVolumePrincipled')
  volume.inputs['Density'].default_value=.00012
  volume.inputs['Color'].default_value=(.53,.66,.67,1)
  volume.inputs['Anisotropy'].default_value=.2
  mat.node_tree.links.new(volume.outputs['Volume'],output.inputs['Volume']);veil.data.materials.append(mat)
 for name,desc in before.items():
  o=bpy.data.objects[name];assert desc==(tuple(v for row in o.matrix_world for v in row),o.hide_render,o.data.name if o.data else None)
 s['depth_variant']=variant;s.render.filepath='//'+out.stem+'.png'
 bpy.ops.file.pack_all();assert not bpy.utils.blend_paths(absolute=True,packed=False)
 bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
 print('SAVED',out,flush=True)
