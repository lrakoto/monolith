"""Independent finishing studies against the same cloud cohesion baseline."""
from pathlib import Path
import bpy
root=Path(__file__).resolve().parents[1]/'renders'
source=root/'cathedral-forest-cohesion-cloud-v1.blend'

def color_multiply(mat,scale,low,high):
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    base=shader.inputs['Base Color'];incoming=base.links[0].from_socket if base.is_linked else None
    color=tuple(base.default_value)
    geo=nodes.new('ShaderNodeNewGeometry')
    stretch=nodes.new('ShaderNodeVectorMath');stretch.operation='MULTIPLY';stretch.inputs[1].default_value=scale
    links.new(geo.outputs['Position'],stretch.inputs[0])
    noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1;noise.inputs['Detail'].default_value=3
    links.new(stretch.outputs['Vector'],noise.inputs['Vector'])
    ramp=nodes.new('ShaderNodeMapRange');ramp.inputs['From Min'].default_value=.25;ramp.inputs['From Max'].default_value=.75
    ramp.inputs['To Min'].default_value=low;ramp.inputs['To Max'].default_value=high
    links.new(noise.outputs['Fac'],ramp.inputs['Value'])
    mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1
    if incoming:links.new(incoming,mix.inputs[1])
    else:mix.inputs[1].default_value=color
    links.new(ramp.outputs['Result'],mix.inputs[2]);links.new(mix.outputs[0],base)

for variant in ('edge-light','stone-grain','pond-ripple'):
    out=root/f'cathedral-{variant}-cloud-v1.blend';assert not out.exists(),out
    bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
    snapshot={o.name:(tuple(v for row in o.matrix_world for v in row),o.hide_render,o.data.name if o.data else None) for o in s.objects}
    if variant=='edge-light':
        # foreground highlights should anchor the forest while the high fill recedes.
        for name,factor in {'open sky':.85,'near bank opening':1.65,'left canopy opening':1.25,'stone light':1.12}.items():
            bpy.data.objects[name].data.energy*=factor
    elif variant=='stone-grain':
        # broad mineral mottling breaks the pristine vertical surface without new geometry.
        color_multiply(bpy.data.materials['weathered monumental limestone'],(.028,.028,.018),.72,1.15)
    else:
        mat=bpy.data.materials['deep green clear water'];nodes=mat.node_tree.nodes;links=mat.node_tree.links
        shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
        prior=shader.inputs['Normal'].links[0].from_socket if shader.inputs['Normal'].is_linked else None
        geo=nodes.new('ShaderNodeNewGeometry');stretch=nodes.new('ShaderNodeVectorMath');stretch.operation='MULTIPLY'
        stretch.inputs[1].default_value=(.055,.30,.055);links.new(geo.outputs['Position'],stretch.inputs[0])
        noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1;noise.inputs['Detail'].default_value=2
        links.new(stretch.outputs['Vector'],noise.inputs['Vector'])
        bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.18
        links.new(noise.outputs['Fac'],bump.inputs['Height'])
        if prior:links.new(prior,bump.inputs['Normal'])
        links.new(bump.outputs['Normal'],shader.inputs['Normal'])
        # keep the accepted roughness; the earlier mirror-like pond was rejected.
        assert abs(shader.inputs['Roughness'].default_value-.30)<1e-5
    assert snapshot=={o.name:(tuple(v for row in o.matrix_world for v in row),o.hide_render,o.data.name if o.data else None) for o in s.objects}
    s.render.filepath='//'+out.stem+'.png';s['finishing_variant']=variant
    bpy.ops.file.pack_all();assert not bpy.utils.blend_paths(absolute=True,packed=False)
    bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
    print('SAVED',out,flush=True)
