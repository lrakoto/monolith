"""Focused variants of the saved Lace scene, without copying its scene builder.

blender --background --threads 8 --python tools/render_cathedral_study.py -- --variant hero-canopy
Use --variant baseline for the identical saved scene. --quick skips the blend save.
"""
import argparse
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
args = argparse.ArgumentParser()
args.add_argument('--variant', choices=('baseline', 'sprays-flat', 'sprays', 'hero-crown', 'hero-canopy', 'hero-leafcraft', 'hero-sprig', 'stair-edges', 'stair-weathered', 'monument-stone', 'inscription-stone', 'entrance-depth', 'left-bank-masses', 'left-bank-contour', 'right-bank-contour', 'canopy-groups'), default='hero-canopy')
args.add_argument('--quick', action='store_true')
args.add_argument('--samples', type=int, choices=(16,32,64,128), default=64, help='sample budget for a saved composition study')
args.add_argument('--retain-understory', action='store_true', help='keep the original clumps in front of the hero crown')
args.add_argument('--resolution', type=int, default=1200)
args.add_argument('--output-name', help='unique filename stem when rebuilding an archived variant')
args.add_argument('--camera-height', type=float, help='absolute world height for a camera-only composition study')
args.add_argument('--camera-compression', type=float, default=1, help='multiply monument distance and focal length together')
args.add_argument('--camera-waterline', type=float, help='top-down frame fraction for the stair foot; adjusts camera pitch')
args.add_argument('--camera-lens', type=float, help='explicit focal length after distance compensation')
args.add_argument('--ascent-lift', type=float, default=0, help='raise the landing and stair rise, preserving the monument top')
args.add_argument('--canopy-shadows', action='store_true', help='test broad shadow-only overhead canopy flags')
args.add_argument('--entrance-wash', action='store_true', help='soft warm facade lighting at the top of the ascent')
args.add_argument('--entrance-wash-power', type=float, default=9000)
args.add_argument('--entrance-wash-size', type=float, default=30)
args.add_argument('--pond-roughness', type=float, help='isolated water reflection study; preserves pond color and geometry')
args.add_argument('--shore-colonies', action='store_true', help='cluster foreground floating leaves for the distant camera')
args.add_argument('--shore-gathered', action='store_true', help='denser asymmetric colonies with selective foreground light')
args.add_argument('--shore-no-light', action='store_true', help='retain gathered planting without the experimental foreground light')
args.add_argument('--canopy-detail', choices=('support','fine','broken','dense'), help='recess crown shells, optionally split broad surface leaves')
args.add_argument('--branch-patch', choices=('left','both','upper','bank-left','banks','banks-extended'), help='replace a small visible hillside patch with actual branching crowns')
args.add_argument('--render-crop', nargs=4, type=float, metavar=('X0','Y0','X1','Y1'), help='normalized top-down detail render without changing the camera')
args.add_argument('--branch-detail', choices=('full','lean'), default='full', help='lower-cost folded leaves for distant replacement crowns only')
args.add_argument('--branch-tiered', action='store_true', help='stagger branch fans on the32 extended-patch crowns only')
args.add_argument('--canopy-landform', action='store_true', help='connected left forest ridges and saddle with planted ground preserved')
args.add_argument('--canopy-landform-strength', type=float, default=1.0, help='ridge and valley depth multiplier')
args.add_argument('--canopy-landform-both', action='store_true', help='add a separately shaped distant right bank')
args.add_argument('--canopy-root-extension', action='store_true', help='bury the finite right trunk base beneath the forest bank')
args.add_argument('--canopy-thicket', action='store_true', help='replace12 rounded crowns with interlocking smaller branching trees')
args.add_argument('--thicket-plinth', action='store_true', help='also replace8 prominent unpaired planting crowns')
args.add_argument('--thicket-fitted', action='store_true', help='retain the original outer dimensions of unpaired planting replacements')
args.add_argument('--thicket-right', action='store_true', help='extend the approved thicket structure to15 right-bank crowns')
args.add_argument('--thicket-lower', action='store_true', help='continue the finer thickets through12 lower-left crowns')
args.add_argument('--thicket-fill', choices=('right','both','left-edge','edges'), help='continue thickets through transition patches and optional forest edges')
args.add_argument('--canopy-leaf-thinning', action='store_true', help='remove one in three distant leaves without moving retained geometry')
args = args.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
source = ROOT / 'renders/cathedral-lace-study.blend'
assert source.exists(), source
bpy.ops.wm.open_mainfile(filepath=str(source))
scene = bpy.context.scene
camera_matrix = scene.camera.matrix_world.copy()
camera_lens = scene.camera.data.lens


def make_sprays(family, materials):
    # connected woody scaffolds carry flattened leaf sprays; no opaque crown shell.
    rng = random.Random(911305 + family)
    vertices, faces, tones = [], [], []

    def frame(axis):
        side = axis.cross(Vector((0, 0, 1)))
        if side.length < .01:
            side = axis.cross(Vector((0, 1, 0)))
        side.normalize()
        return side, axis.cross(side).normalized()

    def wood(a, b, radius):
        axis = (b - a).normalized()
        side, up = frame(axis)
        offset = len(vertices)
        for point, width in ((a, radius), (b, radius * .35)):
            for k in range(4):
                angle = k * math.tau / 4
                vertices.append(tuple(point + (side * math.cos(angle) + up * math.sin(angle)) * width))
        for k in range(4):
            faces.append((offset+k, offset+(k+1)%4, offset+4+(k+1)%4, offset+4+k))
            tones.append(4)

    def leaf(base, direction, normal, length, tone):
        direction.normalize()
        side = normal.cross(direction).normalized()
        normal = direction.cross(side).normalized()
        offset = len(vertices)
        vertices.extend(tuple(v) for v in (
            base, base + direction * length * .47 + side * length * .22,
            base + direction * length, base + direction * length * .47 - side * length * .22,
            base + direction * length * .46 + normal * length * .09))
        for k in range(4):
            faces.append((offset+k, offset+(k+1)%4, offset+4))
            tones.append(tone)

    root = Vector((0, 0, -.9))
    leader = Vector((.04, -.03, .25))
    wood(root, leader, .026)
    for b in range(17 if args.variant == 'sprays-flat' else 25):
        angle = b * 2.39996 + family * .61 + rng.uniform(-.2, .2)
        radial = Vector((math.cos(angle), math.sin(angle)*.85, 0))
        radius = rng.uniform(.55, .96)
        start = root.lerp(leader, rng.uniform(.25, .85))
        if args.variant == 'sprays-flat':
            elbow = radial * radius * .55 + Vector((0, 0, rng.uniform(-.08, .25)))
            tip = radial * radius + Vector((0, 0, rng.uniform(-.08, .38)))
        else:
            # a stepped distribution retains crown depth without rebuilding an opaque shell.
            tip_height = -.36 + (b % 5) * .26 + rng.uniform(-.13, .13)
            radius *= 1 - .28 * max(0, tip_height)
            elbow = radial * radius * .55 + Vector((0, 0, tip_height - rng.uniform(.1, .25)))
            tip = radial * radius + Vector((0, 0, tip_height))
        wood(start, elbow, .011)
        wood(elbow, tip, .006)
        direction = (tip - elbow).normalized()
        lateral = Vector((-radial.y, radial.x, 0)).normalized()
        for twig in range(8):
            t = .2 + twig * .1
            anchor = elbow.lerp(tip, t)
            sign = -1 if twig % 2 else 1
            end = anchor + lateral * sign * rng.uniform(.12, .27) + direction * rng.uniform(.04, .12)
            end.z += rng.uniform(-.09, .10)
            wood(anchor, end, .0028)
            axis = (end - anchor).normalized()
            side, up = frame(axis)
            for shoot in range(5):
                u = .24 + shoot * .16
                origin = anchor.lerp(end, u)
                sign2 = -1 if shoot % 2 else 1
                spray_tip = origin + axis * .08 + side * sign2 * rng.uniform(.075, .17)
                spray_tip.z += rng.uniform(-.06, .03)
                wood(origin, spray_tip, .0009)
                shoot_axis = (spray_tip-origin).normalized()
                shoot_side, unused = frame(shoot_axis)
                for n in range(10):
                    v = .12 + n * .087
                    point = origin.lerp(spray_tip, v)
                    handed = -1 if n % 2 else 1
                    forward = shoot_axis * .5 + shoot_side * handed * .85 + Vector((0, 0, rng.uniform(-.35, .25)))
                    normal = Vector((rng.uniform(-.35, .35), rng.uniform(-.35, .35), 1))
                    leaf(point, forward, normal, rng.uniform(.055, .105) * (1 - .2*v), rng.randrange(4))

    mesh = bpy.data.meshes.new('branch spray family %02d' % family)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    for material in materials:
        mesh.materials.append(material)
    for polygon, tone in zip(mesh.polygons, tones):
        polygon.material_index = tone
    return mesh


if args.variant in ('hero-crown', 'hero-canopy', 'hero-leafcraft', 'hero-sprig', 'stair-edges', 'stair-weathered', 'monument-stone', 'inscription-stone', 'entrance-depth', 'left-bank-masses', 'left-bank-contour', 'right-bank-contour', 'canopy-groups'):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from cathedral_crown import build_crown
    targets = [o for o in scene.objects if o.name.startswith('shoreline stand ') and o.location.x > 0]
    assert len(targets) == 34
    materials = bpy.data.objects['shoreline foliage 009'].data.materials
    for old in targets:
        old.hide_render = True
        bpy.data.objects['shoreline foliage ' + old.name.rsplit(' ', 1)[1]].hide_render = True
    crown = bpy.data.objects.new('fuller right shoreline crown', build_crown(materials, layered=args.variant in ('hero-canopy', 'hero-leafcraft', 'hero-sprig', 'stair-edges', 'stair-weathered', 'monument-stone', 'inscription-stone', 'entrance-depth', 'left-bank-masses', 'left-bank-contour', 'right-bank-contour', 'canopy-groups'), natural=args.variant in ('hero-leafcraft', 'hero-sprig', 'stair-edges', 'stair-weathered', 'monument-stone', 'inscription-stone', 'entrance-depth', 'left-bank-masses', 'left-bank-contour', 'right-bank-contour', 'canopy-groups'), clustered=args.variant == 'hero-sprig'))
    scene.collection.objects.link(crown)
    if not args.retain_understory:
        cleared = []
        for original in list(scene.objects):
            x, y, z = (v / 3 for v in original.location)
            if original.name.startswith('canopy lobe ') and 55 < x < 115 and -18 < y < 18 and z < 24:
                # low ground cover hides the bare bank without masking the hanging crown edge.
                original.location.z -= original.scale.z * .36
                original.scale *= .32
                leaves = bpy.data.objects.get('fine foliage ' + original.name.rsplit(' ', 1)[1])
                if leaves:
                    leaves.location = original.location.copy()
                    leaves.scale = original.scale.copy()
                cleared.append(original.name)
        print('Lowered overlapping foreground clumps:', len(cleared), flush=True)
    crown.location = (240, 54, 66)
    crown.scale = (99, 75, 87)
    print('One fuller crown replaces the same 34 shoreline stands; scene camera unchanged', flush=True)

if args.variant in ('sprays', 'sprays-flat'):
    targets = sorted((o for o in scene.objects if o.name.startswith('shoreline stand ') and o.location.x > 0), key=lambda o: o.name)
    assert len(targets) == 34, len(targets)
    templates = {}
    for index, old in enumerate(targets):
        original_leaves = bpy.data.objects['shoreline foliage ' + old.name.rsplit(' ', 1)[1]]
        family = index % 7
        key = (family, tuple(m.name for m in original_leaves.data.materials))
        if key not in templates:
            templates[key] = make_sprays(family, original_leaves.data.materials)
        replacement = bpy.data.objects.new('botanical test ' + old.name, templates[key])
        scene.collection.objects.link(replacement)
        replacement.matrix_world = old.matrix_world.copy()
        old.hide_render = True
        original_leaves.hide_render = True
    print('Replaced 34 right shoreline crowns; camera, lighting and other planting preserved', flush=True)

if args.variant in ('stair-edges', 'stair-weathered', 'monument-stone', 'inscription-stone', 'entrance-depth', 'left-bank-masses', 'left-bank-contour', 'right-bank-contour', 'canopy-groups'):
    steps = sorted((o for o in scene.objects if o.name.startswith('tread ')), key=lambda o:o.name)
    assert len(steps) == 150
    edges = {}
    for index, step in enumerate(steps):
        strength = max(0, min(1, (index-32)/55))
        if not strength: continue
        material = step.data.materials[0]
        if material.name not in edges:
            edge = material.copy(); edge.name = 'worn nosing ' + material.name
            ramp = next(n for n in edge.node_tree.nodes if n.type == 'VALTORGB')
            for element in ramp.color_ramp.elements:
                color = element.color[:]
                element.color = (*[v*1.8 for v in color[:3]], 1)
            fade = next(n for n in edge.node_tree.nodes if n.type == 'MAP_RANGE')
            fade.inputs['To Min'].default_value = .80
            edges[material.name] = edge
        step.data.materials.append(edges[material.name])
        bevel = next(m for m in step.modifiers if m.type == 'BEVEL')
        bevel.width = .035 + strength*.165
        bevel.segments = 3
        bevel.material = len(step.data.materials)-1
    print('Upper stair bevels broadened; 150 original steps and their transforms preserved', flush=True)

if args.variant in ('stair-weathered', 'monument-stone', 'inscription-stone', 'entrance-depth', 'left-bank-masses', 'left-bank-contour', 'right-bank-contour', 'canopy-groups'):
    def weather_surface(original, edge):
        material = original.copy(); material.name = 'weathered ' + original.name
        nodes, links = material.node_tree.nodes, material.node_tree.links
        shader = nodes.get('Principled BSDF')
        incoming = shader.inputs['Base Color'].links[0].from_socket
        geometry = nodes.new('ShaderNodeNewGeometry')
        stretch = nodes.new('ShaderNodeVectorMath'); stretch.operation = 'MULTIPLY'
        stretch.inputs[1].default_value = (.065, .024, .035)
        links.new(geometry.outputs['Position'], stretch.inputs[0])
        noise = nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 1
        noise.inputs['Detail'].default_value = 2; noise.inputs['Roughness'].default_value = .6
        links.new(stretch.outputs['Vector'], noise.inputs['Vector'])
        fade = nodes.new('ShaderNodeMapRange'); fade.clamp = True
        fade.inputs['From Min'].default_value = .27; fade.inputs['From Max'].default_value = .73
        fade.inputs['To Min'].default_value = .65 if edge else .85
        fade.inputs['To Max'].default_value = 1.40 if edge else 1.12
        links.new(noise.outputs['Fac'], fade.inputs['Value'])
        mix = nodes.new('ShaderNodeMixRGB'); mix.blend_type = 'MULTIPLY'; mix.inputs[0].default_value = 1
        links.new(incoming, mix.inputs[1]); links.new(fade.outputs['Result'], mix.inputs[2])
        links.new(mix.outputs['Color'], shader.inputs['Base Color'])
        return material
    weathered = {}
    wear_rng = random.Random(305915)
    for step in steps:
        for index, original in enumerate(list(step.data.materials)):
            key = (original.name, index > 0)
            if key not in weathered: weathered[key] = weather_surface(original, index > 0)
            step.data.materials[index] = weathered[key]
        bevel = next(m for m in step.modifiers if m.type == 'BEVEL')
        bevel.width *= wear_rng.uniform(.88, 1.12)
    print('Added continuous damp-stone variation and restrained edge wear; lighting unchanged', flush=True)

if args.variant in ('monument-stone', 'inscription-stone', 'entrance-depth', 'left-bank-masses', 'left-bank-contour', 'right-bank-contour', 'canopy-groups'):
    monument = bpy.data.objects['limestone monument']
    material = monument.data.materials[0].copy(); material.name = 'weathered monumental limestone'
    monument.data.materials[0] = material
    nodes, links = material.node_tree.nodes, material.node_tree.links
    shader = nodes.get('Principled BSDF')
    incoming = shader.inputs['Base Color'].links[0].from_socket
    geometry = nodes.new('ShaderNodeNewGeometry')
    def stone_pattern(stretch, low, high):
        vector = nodes.new('ShaderNodeVectorMath'); vector.operation = 'MULTIPLY'
        vector.inputs[1].default_value = stretch
        links.new(geometry.outputs['Position'], vector.inputs[0])
        noise = nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 1
        noise.inputs['Detail'].default_value = 3; noise.inputs['Roughness'].default_value = .65
        links.new(vector.outputs['Vector'], noise.inputs['Vector'])
        fade = nodes.new('ShaderNodeMapRange'); fade.clamp = True
        fade.inputs['From Min'].default_value = .28; fade.inputs['From Max'].default_value = .72
        fade.inputs['To Min'].default_value = low; fade.inputs['To Max'].default_value = high
        links.new(noise.outputs['Fac'], fade.inputs['Value'])
        return fade.outputs['Result']
    # metre-scale weathering must survive the distant camera; fine bump alone cannot do that.
    mottling = stone_pattern((.045,.025,.018), .88, 1.12)
    streaks = stone_pattern((.14,.04,.005), .82, 1.18)
    for variation in (mottling, streaks):
        mix = nodes.new('ShaderNodeMixRGB'); mix.blend_type = 'MULTIPLY'; mix.inputs[0].default_value = 1
        links.new(incoming, mix.inputs[1]); links.new(variation, mix.inputs[2]); incoming = mix.outputs['Color']
    links.new(incoming, shader.inputs['Base Color'])
    print('Monument material only: broad limestone mottling and vertical weathering; silhouette preserved', flush=True)

if args.variant in ('inscription-stone', 'entrance-depth', 'left-bank-masses', 'left-bank-contour', 'right-bank-contour', 'canopy-groups'):
    inscription = bpy.data.objects['305']
    inscription.data = inscription.data.copy()
    inscription.data.materials.clear()
    inscription.data.materials.append(bpy.data.objects['limestone monument'].data.materials[0])
    print('305 inset uses matching limestone; existing carved geometry and text placement unchanged', flush=True)

if args.variant in ('entrance-depth', 'left-bank-masses', 'left-bank-contour', 'right-bank-contour', 'canopy-groups'):
    back = bpy.data.objects['entrance back wall']
    # the original panel sat behind the boolean back face and could not shade the opening.
    back.location.y = 340.99*3
    dark = bpy.data.materials.new('deep entrance stone'); dark.use_nodes = True
    shader = dark.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (.006,.007,.006,1)
    shader.inputs['Roughness'].default_value = .92
    back.data.materials.clear(); back.data.materials.append(dark)
    warmth = bpy.data.objects['entrance warmth']
    warmth.location = Vector((0,340,158.5))*3
    warmth.rotation_euler = (Vector((0,332,150))*3-warmth.location).to_track_quat('-Z','Y').to_euler()
    warmth.data.energy *= .55
    fixture = bpy.data.objects['recessed entrance light']
    fixture.location = Vector((0,340.4,159.9))*3
    fixture.scale.x *= .6
    glow = fixture.data.materials[0].copy(); glow.name = 'subdued interior glow'
    for node in glow.node_tree.nodes:
        if node.type == 'EMISSION':node.inputs['Strength'].default_value *= .35
        elif node.type == 'BSDF_PRINCIPLED':node.inputs['Emission Strength'].default_value *= .35
    fixture.data.materials.clear(); fixture.data.materials.append(glow)
    # small rear lights provide depth cues while the floor receives the main warm light.
    for side in (-1,1):
        bpy.ops.mesh.primitive_cube_add(size=1, location=Vector((side*1.7,340.85,155))*3)
        panel = bpy.context.object; panel.name = 'deep entrance warm detail %d' % side
        panel.dimensions = Vector((.65,.06,1.2))*3; panel.data.materials.append(glow)
    print('Entrance light moved deeper and aimed toward threshold; opening geometry unchanged', flush=True)

if args.variant in ('left-bank-masses', 'left-bank-contour', 'right-bank-contour', 'canopy-groups'):
    # compressed crowns exposed smooth terrain even with their bases anchored. retain the
    # planted volume here; broader trunk exposure needs a coordinated terrain and forest pass.
    shaded_materials = {}
    changed = []
    def shade_object(obj, factor):
        bucket = round(factor * 12) / 12
        for slot in obj.material_slots:
            original = slot.material
            if original is None: continue
            key = (original.name, bucket)
            if key not in shaded_materials:
                material = original.copy()
                material.name = 'left bank shade %.2f ' % bucket + original.name
                nodes, links = material.node_tree.nodes, material.node_tree.links
                shader = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
                if shader:
                    color = shader.inputs['Base Color']
                    multiply = nodes.new('ShaderNodeMixRGB'); multiply.blend_type = 'MULTIPLY'
                    multiply.inputs[0].default_value = 1
                    multiply.inputs[2].default_value = (bucket, bucket, bucket, 1)
                    if color.is_linked: links.new(color.links[0].from_socket, multiply.inputs[1])
                    else: multiply.inputs[1].default_value = color.default_value
                    links.new(multiply.outputs[0], color)
                shaded_materials[key] = material
            slot.link = 'OBJECT'; slot.material = shaded_materials[key]

    for obj in list(scene.objects):
        if not obj.name.startswith('canopy lobe '): continue
        x, y, z = (v / 3 for v in obj.location)
        if not (-300 < x < -43 and -5 < y < 320): continue
        falloff = math.exp(-((x+130)/105)**4 - ((y-140)/180)**4)
        # a low shoulder and a distant crown remain the light anchors between shaded stands.
        island = max(math.exp(-((x+105)/24)**2-((y-65)/30)**2),
                     math.exp(-((x+70)/24)**2-((y-275)/35)**2))
        shade_object(obj, 1 - .65 * falloff * (1-.85*island))
        leaves = bpy.data.objects.get('fine foliage ' + obj.name.rsplit(' ',1)[1])
        if leaves: shade_object(leaves, 1 - .65 * falloff * (1-.85*island))
        changed.append(obj.name)
    assert len(changed) > 100, len(changed)
    print('Left bank crowns regrouped:', len(changed), 'private shade materials:', len(shaded_materials), flush=True)

if args.variant in ('left-bank-contour', 'right-bank-contour', 'canopy-groups'):
    # lower the ground and the entire planted volume together. compressing individual
    # crowns exposed bare terrain; this broad saddle keeps their overlap and root contact.
    def bank_drop(x, y):
        if x < -45 and 10 < y < 320:
            edge = max(0, min(1, (-x-45)/55))
            edge = edge*edge*(3-2*edge)
            return 55 * edge * math.exp(-((x+150)/100)**4) * math.sin(math.pi*(y-10)/310)**2
        # the second trunk sits farther back. keep its bank higher than the left and leave
        # the near shore intact so the bright crown retains its planted foreground setting.
        if args.variant in ('right-bank-contour', 'canopy-groups') and x > 65 and 85 < y < 395:
            edge = max(0, min(1, (x-65)/55))
            edge = edge*edge*(3-2*edge)
            # the outer bank must keep covering the trunk mesh's cut lower edge.
            outer = max(0, min(1, (245-x)/65))
            outer = outer*outer*(3-2*outer)
            return 32 * edge * outer * math.exp(-((x-195)/110)**4) * math.sin(math.pi*(y-85)/310)**2
        return 0

    terrain = bpy.data.objects['simple forest banks']
    terrain.data = terrain.data.copy()
    inverse = terrain.matrix_world.inverted()
    moved_vertices = 0
    for vertex in terrain.data.vertices:
        world = terrain.matrix_world @ vertex.co
        drop = bank_drop(world.x/3, world.y/3)
        if drop > .001:
            world.z -= drop*3
            vertex.co = inverse @ world
            moved_vertices += 1
    terrain.data.update()
    prefixes = ('canopy lobe ', 'fine foliage ', 'shoreline stand ', 'shoreline foliage ',
                'sunstruck edge tree ', 'sunstruck edge foliage ', 'plinth planting ')
    moved_plants = 0
    for obj in scene.objects:
        if obj.name.startswith(prefixes):
            drop = bank_drop(obj.location.x/3, obj.location.y/3)
            if drop > .001:
                obj.location.z -= drop*3
                moved_plants += 1
    assert moved_vertices > 100 and moved_plants > 100
    print('Bank contour:', args.variant, moved_vertices, 'terrain vertices;', moved_plants,
          'plant objects translated with terrain; left max 165, right max 96 world units', flush=True)

if args.variant == 'canopy-groups':
    # expanding uneven crown groups keeps the existing cover; shrinking the old rounded
    # masses exposed smooth ground. retain heights so the new trunk exposure survives.
    grouped = 0
    for crown in list(scene.objects):
        if not crown.name.startswith('canopy lobe '): continue
        x,y,z = (v/3 for v in crown.location)
        if not (65 < abs(x) < 235 and 35 < y < 300): continue
        leaves = bpy.data.objects.get('fine foliage '+crown.name.rsplit(' ',1)[1])
        # a few old numeric names collide; only transform an actual colocated leaf layer.
        if leaves is None or (leaves.location-crown.location).length > .001: continue
        radius = max(crown.scale.x,crown.scale.y)/3
        if radius < 4 or abs(x)-radius*1.7 < 42: continue
        patch = .5+.5*math.sin(x*.046+y*.027)*math.cos(y*.037-x*.014)
        width = 1.15+.50*patch
        depth = 1.04+.12*(1-patch)
        for obj in (crown,leaves):
            obj.scale.x *= width
            obj.scale.y *= depth
        grouped += 1
    assert grouped > 100, grouped
    print('Widened connected canopy groups:', grouped, 'paired crowns; original heights and ground retained',flush=True)

if args.canopy_detail:
    assert args.output_name
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from cathedral_canopy_detail import refine_canopy
    refine_canopy(scene, fine=args.canopy_detail != 'support', broken=args.canopy_detail == 'broken', dense=args.canopy_detail == 'dense')

if args.ascent_lift:
    assert args.output_name and 0 < args.ascent_lift <= 150
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from cathedral_ascent import raise_ascent
    raise_ascent(scene, args.ascent_lift)

if args.canopy_shadows:
    assert args.output_name
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from cathedral_forest_light import add_canopy_shadows
    add_canopy_shadows(scene)

if args.entrance_wash:
    assert args.output_name
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from cathedral_forest_light import add_entrance_wash
    add_entrance_wash(scene, args.ascent_lift, args.entrance_wash_power, args.entrance_wash_size)

if args.pond_roughness is not None:
    assert args.output_name and 0 <= args.pond_roughness <= 1
    pond = bpy.data.objects['pond']
    material = pond.data.materials[0].copy(); material.name = 'pond reflection study'
    pond.data.materials[0] = material
    shader = material.node_tree.nodes.get('Principled BSDF')
    previous = shader.inputs['Roughness'].default_value
    shader.inputs['Roughness'].default_value = args.pond_roughness
    print('Pond roughness:',previous,'->',args.pond_roughness,'; color, transmission and ripple bump preserved',flush=True)

if args.shore_colonies or args.shore_gathered:
    assert args.output_name
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from cathedral_shore import add_leaf_colonies
    add_leaf_colonies(scene, gathered=args.shore_gathered)
    if args.shore_gathered and not args.shore_no_light:
        from cathedral_shore import add_shore_light
        add_shore_light(scene)

assert scene.camera.matrix_world == camera_matrix
assert scene.camera.data.lens == camera_lens
if args.camera_height is not None:
    assert math.isfinite(args.camera_height) and args.camera_height > 0, 'camera height must be positive and finite'
    # isolate water-level perspective from focal length and pitch; named outputs preserve
    # the accepted composition when testing a lower viewpoint.
    assert args.output_name, 'camera experiments require a separate output name'
    original_height = scene.camera.location.z
    scene.camera.location.z = args.camera_height
    bpy.context.view_layer.update()
    expected = camera_matrix.copy(); expected.translation.z = args.camera_height
    assert scene.camera.matrix_world == expected
    print('Camera height:', original_height, '->', args.camera_height, '; lens, pitch and horizontal position unchanged', flush=True)
if args.camera_compression != 1 or args.camera_waterline is not None or args.camera_lens is not None:
    assert args.output_name, 'camera experiments require a separate output name'
    assert math.isfinite(args.camera_compression) and args.camera_compression > 0
    camera = scene.camera
    assert abs(camera.location.x) < .001 and abs(camera.rotation_euler.y) < .001 and abs(camera.rotation_euler.z) < .001
    # the facade is at world y990. measure the dolly relative to it, rather than
    # multiplying distance to the pond, so the lens compensation has a defined subject.
    camera.location.y = 990-(990-camera.location.y)*args.camera_compression
    camera.data.lens *= args.camera_compression
    if args.camera_lens is not None:
        assert math.isfinite(args.camera_lens) and args.camera_lens > 0
        camera.data.lens = args.camera_lens
    if args.camera_waterline is not None:
        assert 0 < args.camera_waterline < 1
        assert camera.location.y < 0
        # square composition, horizontal sensor fit: solve pitch at the stair foot.
        pitch = math.atan((args.camera_waterline-.5)*camera.data.sensor_width/camera.data.lens)-math.atan2(camera.location.z,-camera.location.y)
        camera.rotation_euler.x = math.pi/2+pitch
    bpy.context.view_layer.update()
    from bpy_extras.object_utils import world_to_camera_view
    for label, point in [('tower top',(0,990,1350)),('tower base',(0,990,450+args.ascent_lift)),('stair foot',(0,0,0))]:
        fraction = 1-world_to_camera_view(scene,camera,Vector(point)).y
        print(label, 'top-down frame fraction', round(fraction,5), flush=True)
        if label == 'stair foot' and args.camera_waterline is not None:
            assert abs(fraction-args.camera_waterline)<.001
    print('Compressed camera:', tuple(camera.location), 'lens', camera.data.lens,
          'pitch degrees', math.degrees(camera.rotation_euler.x-math.pi/2), flush=True)

if args.branch_patch:
    assert args.output_name
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from cathedral_branch_patch import replace_visible_patch
    replace_visible_patch(scene, spread=args.branch_patch != 'left', upper=args.branch_patch in ('upper','bank-left','banks','banks-extended'), banks='both' if args.branch_patch in ('banks','banks-extended') else 'left' if args.branch_patch=='bank-left' else None, detail=args.branch_detail, extended=args.branch_patch=='banks-extended', tiered=args.branch_tiered)

if args.canopy_landform:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from cathedral_canopy_landform import reshape_left_bank
    reshape_left_bank(scene, strength=args.canopy_landform_strength, both=args.canopy_landform_both)

if args.canopy_root_extension:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from cathedral_root_extension import extend_right_root
    extend_right_root(scene)

if args.canopy_thicket:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from cathedral_thicket import replace_thicket
    replace_thicket(scene, plinth=args.thicket_plinth, fitted=args.thicket_fitted, right=args.thicket_right, lower=args.thicket_lower, fill=args.thicket_fill)

if args.canopy_leaf_thinning:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from cathedral_leaf_thinning import thin_distant_leaves
    thin_distant_leaves(scene)

scene.render.resolution_x = scene.render.resolution_y = args.resolution
scene.render.resolution_percentage = 100
if args.render_crop:
    assert args.output_name
    x0,y0,x1,y1=args.render_crop
    assert 0<=x0<x1<=1 and 0<=y0<y1<=1
    scene.render.use_border=True;scene.render.use_crop_to_border=True
    scene.render.border_min_x=x0;scene.render.border_max_x=x1
    scene.render.border_min_y=1-y1;scene.render.border_max_y=1-y0
scene.cycles.samples = 16 if args.quick else args.samples
scene.cycles.device = 'CPU'
name = 'cathedral-' + args.variant + ('-quick' if args.quick else '-study')
if args.output_name:
    assert Path(args.output_name).name == args.output_name, 'output name must be a filename stem'
    name = args.output_name
# archived outputs are inputs for other agents, so refuse to overwrite tracked study files.
import subprocess
for extension in ('.png', '.blend'):
    relative = 'renders/' + name + extension
    tracked = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '--', relative], text=True).strip()
    if tracked:
        raise RuntimeError('Output is an archived Git file; choose a new variant name: ' + relative)
scene.render.filepath = str(ROOT / 'renders' / (name + '.png'))
bpy.context.preferences.filepaths.save_version = 0
if not args.quick:
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'renders' / (name + '.blend')))
print('Rendering ' + name, flush=True)
bpy.ops.render.render(write_still=True)
assert Path(scene.render.filepath).exists()
