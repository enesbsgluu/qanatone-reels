# Blender: Tripo GLB -> tp.blend + önden ortografik dokulu render (MediaPipe için). Kullanım: blender -b -P t_hazir.py -- girdi.glb
import bpy, sys, os, json, math
from mathutils import Vector
W = os.path.dirname(os.path.abspath(__file__)); GIR = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=GIR)
o = [x for x in bpy.data.objects if x.type == 'MESH'][0]; o.name = 'tripo'
bpy.context.view_layer.objects.active = o; o.select_set(True); bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM'); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for x in list(bpy.data.objects):
    if x is not o: bpy.data.objects.remove(x)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(W, 'tp.blend'))
sc = bpy.context.scene; sc.render.engine = 'BLENDER_WORKBENCH'; sc.display.shading.light = 'FLAT'; sc.display.shading.color_type = 'TEXTURE'
sc.view_settings.view_transform = 'Standard'
P = [v.co for v in o.data.vertices]; zt = max(p.z for p in P); zb = min(p.z for p in P)
bas = [p for p in P if p.z > zt - (zt - zb) * .5]; cx = sum(p.x for p in bas) / len(bas); cz = zt - (zt - zb) * .42; S = (zt - zb) * .95
cd = bpy.data.cameras.new('k'); cd.type = 'ORTHO'; cd.ortho_scale = S; kam = bpy.data.objects.new('k', cd); sc.collection.objects.link(kam); sc.camera = kam
kam.location = (cx, -5, cz); kam.rotation_euler = (math.pi / 2, 0, 0)
sc.render.resolution_x = sc.render.resolution_y = 1400; sc.render.filepath = os.path.join(W, 'tp-on.png'); bpy.ops.render.render(write_still=True)
json.dump({'cx': cx, 'cz': cz, 'olcek': S, 'px': 1400}, open(os.path.join(W, 'tp-on.json'), 'w'))
