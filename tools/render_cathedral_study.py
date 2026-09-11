"""Focused variants of the saved Lace scene, without copying its scene builder.

blender --background --threads 8 --python tools/render_cathedral_study.py -- --variant sprays
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
args.add_argument('--variant', choices=('baseline', 'sprays-flat', 'sprays', 'hero-crown'), default='sprays')
args.add_argument('--quick', action='store_true')
args.add_argument('--retain-understory', action='store_true', help='keep the original clumps in front of the hero crown')
args.add_argument('--resolution', type=int, default=1200)
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


if args.variant == 'hero-crown':
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from cathedral_crown import build_crown
    targets = [o for o in scene.objects if o.name.startswith('shoreline stand ') and o.location.x > 0]
    assert len(targets) == 34
    materials = bpy.data.objects['shoreline foliage 009'].data.materials
    for old in targets:
        old.hide_render = True
        bpy.data.objects['shoreline foliage ' + old.name.rsplit(' ', 1)[1]].hide_render = True
    crown = bpy.data.objects.new('fuller right shoreline crown', build_crown(materials))
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

assert scene.camera.matrix_world == camera_matrix
assert scene.camera.data.lens == camera_lens
scene.render.resolution_x = scene.render.resolution_y = args.resolution
scene.render.resolution_percentage = 100
scene.cycles.samples = 16 if args.quick else 64
scene.cycles.device = 'CPU'
name = 'cathedral-' + args.variant + ('-quick' if args.quick else '-study')
scene.render.filepath = str(ROOT / 'renders' / (name + '.png'))
bpy.context.preferences.filepaths.save_version = 0
if not args.quick:
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'renders' / (name + '.blend')))
print('Rendering ' + name, flush=True)
bpy.ops.render.render(write_still=True)
assert Path(scene.render.filepath).exists()
