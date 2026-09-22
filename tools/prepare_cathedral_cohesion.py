"""Make a material-only forest cohesion candidate from the accepted saved scene."""
from pathlib import Path
import bpy
root=Path(__file__).resolve().parents[1]/'renders'
source=root/'cathedral-canopy-upper-planting-study.blend'
out=root/'cathedral-forest-cohesion-cloud-v1.blend'
assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene
before={o.name:(tuple(v for row in o.matrix_world for v in row),o.hide_render,o.data.name if o.data else None) for o in s.objects}
changed=[]
for mat in bpy.data.materials:
    name=mat.name.lower()
    if not any(t in name for t in ('blockout canopy','shoreline canopy','edge canopy','leaf tone','soft leaf surface')):continue
    if not mat.node_tree:continue
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    shaders=[n for n in nodes if n.type=='BSDF_PRINCIPLED']
    if len(shaders)!=1:continue
    shader=shaders[0];base=shader.inputs['Base Color']
    incoming=base.links[0].from_socket if base.is_linked else None
    color=tuple(base.default_value)
    # world position makes neighboring crowns share a broad tonal pattern;
    # generated coordinates would repeat the same patch on every separate tree.
    geom=nodes.new('ShaderNodeNewGeometry');geom.label='continuous forest position'
    noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=.006
    noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.6
    links.new(geom.outputs['Position'],noise.inputs['Vector'])
    ramp=nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.25;ramp.color_ramp.elements[0].color=(.68,.68,.68,1)
    ramp.color_ramp.elements[1].position=.75;ramp.color_ramp.elements[1].color=(1.06,1.06,1.06,1)
    links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
    mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1
    if incoming:links.new(incoming,mix.inputs[1])
    else:mix.inputs[1].default_value=color
    links.new(ramp.outputs['Color'],mix.inputs[2]);links.new(mix.outputs[0],base)
    changed.append(mat.name)
assert changed
assert before=={o.name:(tuple(v for row in o.matrix_world for v in row),o.hide_render,o.data.name if o.data else None) for o in s.objects}
s.render.resolution_x=s.render.resolution_y=1200;s.render.resolution_percentage=100
s.cycles.samples=64;s.cycles.device='GPU'
s.render.use_border=False;s.render.use_crop_to_border=False
s.frame_start=s.frame_end=s.frame_current
s.render.filepath='//cathedral-forest-cohesion-cloud-v1.png'
s['cohesion_materials']=','.join(changed)
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True,packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
print('COHESION',len(changed),'materials; object transforms, visibility and meshes unchanged;',out)
