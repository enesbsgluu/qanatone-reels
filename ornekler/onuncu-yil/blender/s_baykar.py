# BAYKAR ara planı (3,7 sn; zaman.json BAYKAR 12.27 -> K2 15.96): gün batımında bulutların üstünde Kızılelma, arkada kol uçuşunda iki TB2.
# Hareket: kamera önden-alttan yana yay (akışkan bezier), gök (HDRI) döner = hız hissi, uçak hafif yatış + iniş-çıkış, pervaneler döner (hareket bulanıklığı).
# Kullanım: blender -b -P s_baykar.py -- [kare_sayisi] -> sahne_baykar.blend
import os, sys, math
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'urun_ortak.py'), encoding='utf-8').read())
for m_ in ('m_kizilelma.py', 'm_tb2.py'): exec(open(os.path.join(UW, m_), encoding='utf-8').read())
a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []; NK = int(a[0]) if a else 120
sc = sifirla(); eevee(sc, NK, 64, True)
w = hdri_dunya('industrial_sunset_02_puresky_4k.hdr', 1.25, .794)   # güneş u=.60 (_gunes_bul.py) -> 45,5° dönüş: güneş tam uçağın arkasında (70,7° kadrajın 30° sağında kalıyordu)
mp = [n for n in w.node_tree.nodes if n.type == 'MAPPING'][0]
mp.inputs['Rotation'].default_value[2] = .794; mp.inputs['Rotation'].keyframe_insert('default_value', index=2, frame=1)
mp.inputs['Rotation'].default_value[2] = .794 + .10; mp.inputs['Rotation'].keyframe_insert('default_value', index=2, frame=NK)
for fc in getattr(w.node_tree.animation_data.action, 'fcurves', []):
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
isik('gunes', 'SUN', (0, 0, 0), (.15, -1, -.04), 5.0, (1, .72, .45), 1.0)   # HDRI güneşiyle aynı yön: arkadan altın kenar ışığı
isik('dolgu', 'SUN', (0, 0, 0), (.4, .6, .5), .6, (.55, .65, 1), 8)   # gök dolgusu (alttan soğuk)
ke = kizilelma('kizilelma'); ke.location = (-7.2, 0, 0)   # gövde ortası orijinde
for f, roll, dz in ((1, .10, 0), (NK // 2, -.04, .25), (NK, .06, -.1)):
    ke.rotation_euler = (roll, .02, 0); ke.location.z = dz; ke.keyframe_insert('rotation_euler', frame=f); ke.keyframe_insert('location', frame=f)
for i, (p, ph) in enumerate((((-30, 42, 3.5), 0), ((-44, 60, -2.5), 1.3))):   # uçağın gerisinde, derinde (kameradan uzak)
    t = tb2(f'tb2_{i}'); t.location = p; t.rotation_euler = (.05 * (1 if i else -1), 0, 0)
    for f, dz in ((1, 0), (NK, .8 * (1 if i else -1))):
        t.location.z = p[2] + dz; t.keyframe_insert('location', frame=f)
    pv = bpy.data.objects[t['pervane']]
    pv.rotation_euler = (ph, 0, 0); pv.keyframe_insert('rotation_euler', frame=1); pv.rotation_euler = (ph + NK * 2.1, 0, 0); pv.keyframe_insert('rotation_euler', frame=NK)
    for fc in getattr(pv.animation_data.action, 'fcurves', []):
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
kam = kamera(35, 5.6); kam.data.dof.focus_object = ke
bak(kam, (14, -26, -1.2), (0, 4, .2), 1); bak(kam, (2, -31, -.6), (-1, 4, .3), NK)   # ufuk seviyesi: gün batımı kızıllığı uçağın arkasında (yukarı bakınca öğle mavisi kalıyordu)
yumusak_egriler(kam)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(UW, 'sahne_baykar.blend')); print('BAYKAR kaydedildi', NK)
