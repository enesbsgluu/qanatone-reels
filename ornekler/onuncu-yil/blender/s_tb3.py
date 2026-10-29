# TB3 ara planı (3,5 sn; zaman.json TB3 24.57 -> K4 28.11): gün batımında açık denizde TCG Anadolu (L400), Bayraktar TB3 uçuş güvertesinde hızlanır,
# baş taraftaki kayak rampasından (12°) havalanır. Deniz: Okyanus değiştiricisi. Kamera alçaktan, TB3'ü izleyerek yana açılır.
# Kullanım: blender -b -P s_tb3.py -- [kare] -> sahne_tb3.blend
import os, sys, math
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'urun_ortak.py'), encoding='utf-8').read())
exec(open(os.path.join(UW, 'm_tb2.py'), encoding='utf-8').read())
a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []; NK = int(a[0]) if a else 120
sc = sifirla(); eevee(sc, NK, 64, True)
hdri_dunya('qwantani_sunset_puresky_4k.hdr', 1.2, 2.513)   # güneş (u=.60) 144° dönüşle +X'te: TB3 rampadan güneşe doğru kalkar
isik('gunes', 'SUN', (0, 0, 0), (-1, 0, -.1), 4.0, (1, .68, .42), 1.0)
# ---------- deniz ----------
bpy.ops.mesh.primitive_plane_add(size=1); de = bpy.context.object; de.name = 'deniz'
oc = de.modifiers.new('okyanus', 'OCEAN'); oc.geometry_mode = 'GENERATE'; oc.spatial_size = 400; oc.repeat_x = oc.repeat_y = 6; oc.resolution = 14; oc.wave_scale = 1.2; oc.choppiness = 1.1; oc.wind_velocity = 14
oc.time = 1; oc.keyframe_insert('time', frame=1); oc.time = 1 + NK / 30; oc.keyframe_insert('time', frame=NK)
for fc in getattr(de.animation_data.action, 'fcurves', []):
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
de.location = (-1200, -1200, 0)
bagla(de, malz('su', (.006, .022, .035), .06, **{'Specular IOR Level': .6}))
for p in de.data.polygons: p.use_smooth = True
# ---------- TCG Anadolu (L400): gövde 231 m, en 32 m, uçuş güvertesi + kayak rampası + ada ----------
GG = boya('gemi_gri', (.05, .055, .06), .6, .1); GD = malz('guverte', (.02, .02, .022), .8)   # ters ışıkta koyu siluet (açık gri bej görünüyordu)
gemi = bpy.data.objects.new('anadolu', None); sc.collection.objects.link(gemi)
st = [(-115, 26, 14, 2, dict(us=4, alt=2.4, ust_oran=.6)), (-60, 32, 20, 1, dict(us=5, alt=2.2, ust_oran=.6)), (40, 32, 20, 1, dict(us=5, alt=2.2, ust_oran=.6)),
      (95, 22, 18, 2, dict(us=3, alt=1.8, ust_oran=.6)), (116, 3, 14, 4, dict(us=2, alt=1.6, ust_oran=.6))]
gv = nesne('gemi_govde', loft('gemi_govde', st, n=32), gemi); bagla(yumusat(gv, 1), GG)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-5, 0, 13.4)); gu = bpy.context.object; gu.scale = (215, 31, .8); bpy.ops.object.transform_apply(scale=True); gu.parent = gemi; bagla(gu, GD)
bpy.ops.mesh.primitive_cube_add(size=1); rp = bpy.context.object; rp.name = 'rampa'; rp.scale = (24, 13, .8); bpy.ops.object.transform_apply(scale=True)
rp.rotation_euler = (0, math.radians(-12), 0); rp.location = (112, 8, 16.0); rp.parent = gemi; bagla(rp, GD)   # iskele tarafı kayak rampası
for i, x in enumerate(range(-90, 100, 18)):   # güverte çizgileri (beyaz kesikli orta hat)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 8, 13.82)); c = bpy.context.object; c.scale = (8, .4, .02); bpy.ops.object.transform_apply(scale=True); c.parent = gemi; bagla(c, malz('cizgi', (.8, .8, .78), .6))
ada = [((-20, -12, 22), (38, 7, 16)), ((-26, -12, 34), (18, 6, 10)), ((-24, -12, 44), (6, 3, 12))]   # sancak ada + direk
for (p, s) in ada:
    bpy.ops.mesh.primitive_cube_add(size=1, location=p); b = bpy.context.object; b.scale = s; bpy.ops.object.transform_apply(scale=True); b.parent = gemi; bagla(yumusat(b, 1, .3), GG)
no = yazi('l400', 'L400', 9, (.9, .9, .88), .05, gemi); no.rotation_euler = (math.pi / 2, 0, 0); no.location = (-60, -16.2, 9.5)
no2 = yazi('l400b', '400', 14, (.85, .85, .83), .02, gemi); no2.location = (70, 6, 13.85)
gemi.location = (0, 0, 0)
# ---------- TB3: TB2'den büyük (boy 8,35 m, açıklık 14 m) -> ölçek 1,2; güvertede hızlanır, rampadan kalkar ----------
t = tb2('tb3', renk=(.6, .62, .63)); t.scale = (1.2, 1.2, 1.2)
P = [(1, (40, 8, 14.6), 0, 0), (int(NK * .55), (88, 8, 14.6), 0, 0), (int(NK * .72), (118, 8, 22.8), -.21, 0), (NK, (138, 7, 27.5), -.16, .05)]
for f, loc, pitch, roll in P:
    t.location = loc; t.rotation_euler = (roll, pitch, 0); t.keyframe_insert('location', frame=f); t.keyframe_insert('rotation_euler', frame=f)
for fc in getattr(t.animation_data.action, 'fcurves', []):
    for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'; kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
pv = bpy.data.objects[t['pervane']]; pv.keyframe_insert('rotation_euler', frame=1); pv.rotation_euler = (NK * 2.3, 0, 0); pv.keyframe_insert('rotation_euler', frame=NK)
for fc in getattr(pv.animation_data.action, 'fcurves', []):
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
hedef = bpy.data.objects.new('tb3_hedef', None); sc.collection.objects.link(hedef); hedef.parent = t; hedef.location = (3, 0, .2)
kam = kamera(40, 0); kam.location = (22, 17, 16.4)   # güvertede, TB3'ün arka-iskele tarafı (gövde kadraja girmez)
tt = kam.constraints.new('TRACK_TO'); tt.target = hedef; tt.track_axis = 'TRACK_NEGATIVE_Z'; tt.up_axis = 'UP_Y'
kam.keyframe_insert('location', frame=1); kam.location = (100, 15, 18.5); kam.keyframe_insert('location', frame=NK)   # güverte boyunca ileri kayar, rampaya yaklaşır (TB3 sonda kadrajın ~%80'i)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(UW, 'sahne_tb3.blend')); print('TB3 kaydedildi', NK)
