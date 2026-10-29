# Blender: Hunyuan3D-2.1 büstü -> çalışma ağı (heykel/hy-is.blend): alt plaka kesilir, ~400k yüze azaltılır, önden ORTOGRAFİK kil render (yüz noktaları için)
# Koordinat: Blender Z yukarı, ön -Y. Çıktı: heykel/hy-on.png + heykel/hy-on.json (ortografik kamera: merkez, ölçek)
import bpy, bmesh, sys, os, json, math
from mathutils import Vector
W = os.path.abspath('heykel')
bpy.ops.wm.open_mainfile(filepath=os.path.join(W, 'uretim', 'hunyuan21.blend'))
o = [x for x in bpy.data.objects if x.type == 'MESH'][0]; bpy.context.view_layer.objects.active = o; o.select_set(True)
zs = sorted(v.co.z for v in o.data.vertices); zmin, zmax = zs[0], zs[-1]
bm = bmesh.new(); bm.from_mesh(o.data); kes = zmin + .012   # alt plaka (~1 cm)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < kes], context='VERTS'); bm.to_mesh(o.data); bm.free()
m = o.modifiers.new('d', 'DECIMATE'); m.ratio = 400000 / len(o.data.polygons); bpy.ops.object.modifier_apply(modifier='d')
for p in o.data.polygons: p.use_smooth = True
print('HAZIR', len(o.data.polygons), 'yüz; z', round(zmin, 3), round(zmax, 3))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(W, 'hy-is.blend'))
# önden ortografik render
KIL_ON = os.path.join(W, '_yok'); exec(open(os.path.join(W, 'kil.py'), encoding='utf-8').read().split('# otomatik kadraj')[0])
sc = bpy.context.scene; kam = sc.camera; kam.data.type = 'ORTHO'
P = [o.matrix_world @ v.co for v in o.data.vertices]; zt = max(p.z for p in P)
bas = [p for p in P if p.z > zt - .25]; cx = sum(p.x for p in bas) / len(bas); cz = zt - .21
kam.data.ortho_scale = .50; kam.location = (cx, -2, cz); kam.rotation_euler = (math.pi / 2, 0, 0)
sc.render.resolution_x = sc.render.resolution_y = 1400; sc.render.filepath = os.path.join(W, 'hy-on.png'); bpy.ops.render.render(write_still=True)
json.dump({'cx': cx, 'cz': cz, 'olcek': .50, 'px': 1400}, open(os.path.join(W, 'hy-on.json'), 'w'))
