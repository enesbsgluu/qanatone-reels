# Blender: üretilmiş GLB'yi aç, birleştir, ölçekle (yükseklik 1 -> baş ~ .5), merkezle -> <onek>.blend; bilgi yazdır
import bpy, sys
from mathutils import Vector
argv = sys.argv[sys.argv.index('--') + 1:]; G, ON = argv[0], argv[1]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=G)
ms = [o for o in bpy.context.scene.objects if o.type == 'MESH']
for o in bpy.context.scene.objects: o.select_set(o.type == 'MESH')
bpy.context.view_layer.objects.active = ms[0]
if len(ms) > 1: bpy.ops.object.join()
o = bpy.context.view_layer.objects.active; bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bb = [Vector(c) for c in o.bound_box]; mn = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb))); mx = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
s = .45 / (mx.z - mn.z); o.location = -(mn + mx) / 2 * s + Vector((0, 0, -.12)); o.scale = (s, s, s); bpy.ops.object.transform_apply(location=True, scale=True)
for p in o.data.polygons: p.use_smooth = True
print('AÇ', len(o.data.vertices), 'köşe', len(o.data.polygons), 'yüz; boyut', [round(v, 3) for v in (mx - mn)])
import os; bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(ON + '.blend'))
