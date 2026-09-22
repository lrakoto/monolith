"""Compare integrated wall foliage with restrained weathering on stair margins."""
from pathlib import Path
import bpy
root=Path(__file__).resolve().parents[1]/'renders'

def tint_copy(mat,tag,tint,edge=False):
 copy=mat.copy();copy.name=tag+' '+mat.name
 nodes=copy.node_tree.nodes;links=copy.node_tree.links
 shaders=[n for n in nodes if n.type=='BSDF_PRINCIPLED']
 assert len(shaders)==1,mat.name
 base=shaders[0].inputs['Base Color'];old=base.links[0].from_socket if base.is_linked else None;color=tuple(base.default_value)
 mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(*tint,1)
 if old:links.new(old,mix.inputs[1])
 else:mix.inputs[1].default_value=color
 if edge:
  # weather only the outer treads; world noise prevents the same stain repeating on every step.
  geom=nodes.new('ShaderNodeNewGeometry');sep=nodes.new('ShaderNodeSeparateXYZ');links.new(geom.outputs['Position'],sep.inputs[0])
  absolute=nodes.new('ShaderNodeMath');absolute.operation='ABSOLUTE';links.new(sep.outputs['X'],absolute.inputs[0])
  mask=nodes.new('ShaderNodeMapRange');mask.clamp=True;mask.inputs['From Min'].default_value=57;mask.inputs['From Max'].default_value=82;mask.inputs['To Min'].default_value=0;mask.inputs['To Max'].default_value=.85;links.new(absolute.outputs[0],mask.inputs['Value'])
  noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=.065;noise.inputs['Detail'].default_value=3;links.new(geom.outputs['Position'],noise.inputs['Vector'])
  ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.35;ramp.color_ramp.elements[1].position=.62;links.new(noise.outputs['Fac'],ramp.inputs[0])
  product=nodes.new('ShaderNodeMath');product.operation='MULTIPLY';links.new(mask.outputs['Result'],product.inputs[0]);links.new(ramp.outputs[0],product.inputs[1]);links.new(product.outputs[0],mix.inputs[0])
 links.new(mix.outputs[0],base)
 return copy

for variant in ('wall-tones','stair-patina'):
 out=root/f'cathedral-overgrown-{variant}-cloud-v1.blend';assert not out.exists(),out
 bpy.ops.wm.open_mainfile(filepath=str(root/'cathedral-overgrown-leafy-cloud-v1.blend'));s=bpy.context.scene
 before={o.name:(tuple(v for row in o.matrix_world for v in row),o.hide_render,o.data.name if o.data else None) for o in s.objects}
 copies={};wall_count=0
 for o in s.objects:
  if not o.name.startswith('wall foliage backing '):continue
  wall_count+=1
  for slot in o.material_slots:
   mat=slot.material
   if mat is None:continue
   if mat.name not in copies:copies[mat.name]=tint_copy(mat,'distant wall tone',(.58,.69,.63))
   slot.link='OBJECT';slot.material=copies[mat.name]
 assert wall_count==7
 if variant=='stair-patina':
  copies={};steps=[o for o in s.objects if o.name.startswith('tread ')];assert len(steps)==150
  for o in steps:
   for slot in o.material_slots:
    mat=slot.material
    if mat is None:continue
    if mat.name not in copies:copies[mat.name]=tint_copy(mat,'damp stair edge',(.40,.62,.33),True)
    slot.link='OBJECT';slot.material=copies[mat.name]
 assert before=={o.name:(tuple(v for row in o.matrix_world for v in row),o.hide_render,o.data.name if o.data else None) for o in s.objects}
 s.render.filepath='//'+out.stem+'.png';bpy.ops.file.pack_all();assert not bpy.utils.blend_paths(absolute=True,packed=False)
 bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);print('SAVED',out,flush=True)
