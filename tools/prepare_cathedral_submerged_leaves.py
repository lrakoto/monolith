"""Add sparse submerged leaves above the bed, preserving the open pond center."""
import math
import random
from pathlib import Path

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view


root = Path(__file__).resolve().parents[1] / 'renders'
output = root / 'cathedral-submerged-leaf-depth-cloud-v1.blend'
assert not output.exists(), output
bpy.ops.wm.open_mainfile(filepath=str(root / 'cathedral-pond-bed-breakup-cloud-v1.blend'))
scene = bpy.context.scene


def descriptor(obj):
    return (tuple(value for row in obj.matrix_world for value in row),
            obj.hide_render, obj.data.name if obj.data else None,
            tuple(slot.material.name if slot.material else None for slot in obj.material_slots))


before = {obj.name: descriptor(obj) for obj in scene.objects}
camera = (scene.camera.data.lens, descriptor(scene.camera))
lights = {obj.name: (obj.data.energy, tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
depsgraph = bpy.context.evaluated_depsgraph_get()
projection = scene.camera.calc_matrix_camera(depsgraph,
    x=scene.render.resolution_x, y=scene.render.resolution_y,
    scale_x=scene.render.pixel_aspect_x, scale_y=scene.render.pixel_aspect_y)
inverse = projection.inverted()
origin = scene.camera.matrix_world.translation


def pond_point(x, y, z):
    near = inverse @ Vector((x*2-1, y*2-1, -1, 1))
    near = Vector(near[:3]) / near.w
    ray = scene.camera.matrix_world.to_3x3() @ near
    point = origin + ray * ((z-origin.z) / ray.z)
    projected = world_to_camera_view(scene, scene.camera, point)
    assert abs(projected.x-x) < .00001 and abs(projected.y-y) < .00001
    return tuple(point)


palette = []
for index, color in enumerate(((.004,.012,.007,1), (.008,.022,.011,1), (.013,.029,.017,1))):
    material = bpy.data.materials.new(f'submerged leaf dark olive {index}')
    material.use_nodes = True
    shader = next(node for node in material.node_tree.nodes if node.type == 'BSDF_PRINCIPLED')
    shader.inputs['Base Color'].default_value = color
    shader.inputs['Roughness'].default_value = .63
    shader.inputs['Specular IOR Level'].default_value = .22
    palette.append(material)

# the bed now has smaller variation but no recognizable submerged structure.
# keep these few dark ribbons between the shelf at -.7 and water at .09;
# cluster them unevenly at the frame edges, with no new central obstruction.
rng = random.Random(3050929)
groups = ((.20,.025,7), (.30,.047,5), (.73,.017,9),
          (.80,.048,6), (.16,.077,4), (.86,.073,5))
vertices, faces, slots = [], [], []
for cx, cy, count in groups:
    for index in range(count):
        x = cx + rng.gauss(0,.008)
        y = cy + rng.gauss(0,.0015)
        angle = rng.uniform(0,math.tau)
        dx = math.cos(angle)*rng.uniform(.016,.038)
        dy = math.sin(angle)*rng.uniform(.005,.012)
        width = rng.uniform(.0007,.0016)
        bend = rng.uniform(-.008,.008)
        depth = rng.uniform(-.58,-.32)
        normal = Vector((-dy,dx)).normalized()
        start = len(vertices)
        segments = 8
        for k in range(segments+1):
            t = k/segments
            xx = x+dx*t+normal.x*bend*math.sin(math.pi*t)
            yy = y+dy*t+normal.y*bend*.22*math.sin(math.pi*t)
            half_width = width*math.sin(math.pi*t)**.7
            z = depth+.12*math.sin(math.pi*t)
            assert -.7 < z < .09
            vertices.extend((pond_point(xx-normal.x*half_width,yy-normal.y*half_width*.22,z),
                             pond_point(xx+normal.x*half_width,yy+normal.y*half_width*.22,z)))
        for k in range(segments):
            a = start+2*k
            faces.append((a,a+1,a+3,a+2))
            slots.append(rng.choices((0,1,2),weights=(5,3,1))[0])
mesh = bpy.data.meshes.new('sparse submerged curved leaves mesh')
mesh.from_pydata(vertices,[],faces)
mesh.update()
obj = bpy.data.objects.new('sparse submerged curved leaves',mesh)
scene.collection.objects.link(obj)
for material in palette:
    mesh.materials.append(material)
for polygon, slot in zip(mesh.polygons,slots):
    polygon.material_index = slot
assert len(mesh.polygons) == 288
assert all(descriptor(bpy.data.objects[name]) == old for name,old in before.items())
assert camera == (scene.camera.data.lens,descriptor(scene.camera))
assert lights == {obj.name: (obj.data.energy,tuple(obj.data.color)) for obj in scene.objects if obj.type == 'LIGHT'}
scene.render.filepath = '//' + output.stem + '.png'
bpy.ops.file.pack_all()
assert not bpy.utils.blend_paths(absolute=True,packed=False)
bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True)
print('SAVED',output,'SUBMERGED LEAVES 36 FACES 288',flush=True)
