# TUSAŞ ara planı (3,6 sn; zaman.json TUSAS 20.95 -> TB3 24.57): parçalı bulutlu gökte KAAN, art yakıcı açık, kameraya doğru gelip yanından süzülerek geçer;
# kamera izleme kısıtıyla döner (akışkan), hafif yatış. Kullanım: blender -b -P s_tusas.py -- [kare] -> sahne_tusas.blend
import os, sys, math
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'urun_ortak.py'), encoding='utf-8').read())
exec(open(os.path.join(UW, 'm_kaan.py'), encoding='utf-8').read())
a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []; NK = int(a[0]) if a else 120
sc = sifirla(); eevee(sc, NK, 64, True)
hdri_dunya('kloofendal_48d_partly_cloudy_puresky_4k.hdr', 1.0, 2.4)
isik('gunes', 'SUN', (0, 0, 0), (-.4, .6, -.7), 4.0, (1, .95, .88), 1.0)
k = kaan('kaan'); k.location = (150, 9, 6)
k.rotation_euler = (0, 0, math.pi); k.keyframe_insert('rotation_euler', frame=1); k.keyframe_insert('location', frame=1)   # burun -X (kameraya doğru)
k.location = (55, 7, 3.5); k.rotation_euler = (-.25, .03, math.pi); k.keyframe_insert('location', frame=int(NK * .55)); k.keyframe_insert('rotation_euler', frame=int(NK * .55))
k.location = (-12, 4, 2.5); k.rotation_euler = (-.45, .06, math.pi); k.keyframe_insert('location', frame=NK); k.keyframe_insert('rotation_euler', frame=NK)
for fc in getattr(k.animation_data.action, 'fcurves', []):
    for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'; kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
hedef = bpy.data.objects.new('kaan_hedef', None); sc.collection.objects.link(hedef); hedef.parent = k; hedef.location = (10.3, 0, .3)   # gövde ortası (yerel: kuyruk x=0, burun +20,6; -8 kuyruğun arkasında boşluğa bakıyordu)
kam = kamera(40, 0); kam.location = (-6, -9, .8)
tt = kam.constraints.new('TRACK_TO'); tt.target = hedef; tt.track_axis = 'TRACK_NEGATIVE_Z'; tt.up_axis = 'UP_Y'
kam.keyframe_insert('location', frame=1); kam.location = (-3, -11, 1.4); kam.keyframe_insert('location', frame=NK)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(UW, 'sahne_tusas.blend')); print('TUSAŞ kaydedildi', NK)
