# TOGG ara planı (3,7 sn; zaman.json TOGG 8.56 -> BAYKAR 12.27): karanlık stüdyoda Togg T10X (boy 4,6 / en 1,9 / yük. 1,68 / dingil 2,89 m),
# metalik gece mavisi, ön/arka LED şerit, ön panelde Togg logosu; yansıtıcı zemin, arkada parlayan TOGG logosu; kamera ön-3/4'ten yana yavaş yay, ışık süpürmesi.
# Kullanım: blender -b -P s_togg.py -- [kare] -> sahne_togg.blend
import os, sys, math
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'urun_ortak.py'), encoding='utf-8').read())
a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []; NK = int(a[0]) if a else 120
sc = sifirla(); eevee(sc, NK, 64, True)
hdri_dunya('studio_small_09_2k.hdr', .9, 0, gorunur=False)
LOGO = os.path.join(UW, '..', 'logo')
# T10X: Hunyuan3D-2.1 (heykel/uretim/hunyuan21-togg.glb, girdi ref/ara/togg-t10x-on.jpg dekupe) -> boy 4,6 m (1 birim = 2,315 m), ön -Y.
# Bölge (birim uzayında, _tg_olc ölçümü): teker merkezi y ±.595 z -.218 r .16; bel z .135; ön y < -.86 -> boya/cam/krom ızgara/alt kaplama/lastik/jant/LED.
import numpy as np
bpy.ops.import_scene.gltf(filepath=os.path.join(UW, '..', 'heykel', 'uretim', 'hunyuan21-togg.glb'))
araba = [x for x in bpy.data.objects if x.type == 'MESH'][0]; araba.name = 't10x'
for x in list(bpy.data.objects):
    if x.type == 'EMPTY': mw = araba.matrix_world.copy(); araba.parent = None; araba.matrix_world = mw; bpy.data.objects.remove(x)
bpy.context.view_layer.objects.active = araba; araba.select_set(True); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
me = araba.data; n = len(me.vertices); A = np.zeros(n * 3); me.vertices.foreach_get('co', A); A = A.reshape(-1, 3); Nn = np.zeros(n * 3); me.vertices.foreach_get('normal', Nn); Nn = Nn.reshape(-1, 3)
x, y, z = A.T; ax = np.abs(x)
BOYA = malz('t10x_boya', (.008, .022, .06), .2, .75, **{'Coat Weight': 1., 'Coat Roughness': .03})
CAM = malz('t10x_cam', (.003, .004, .005), .04, .0, **{'Coat Weight': 1.}); SIYAH = malz('t10x_kaplama', (.012, .012, .013), .55)
KROM = malz('t10x_krom', (.8, .8, .82), .12, 1.); LAST = malz('lastik', (.015, .015, .017), .85); JANT = malz('jant', (.35, .36, .38), .3, 1.)
LEDB = malz('led_b', (1, 1, 1), .3, **{'Emission Color': (.85, .92, 1, 1), 'Emission Strength': 30}); LEDK = malz('led_k', (1, 0, 0), .3, **{'Emission Color': (1, .03, .02, 1), 'Emission Strength': 15})
S_ = np.zeros(n, np.int32)   # 0 boya
td = np.minimum(np.hypot(y - .595, z + .218), np.hypot(y + .595, z + .218))
S_[(z > .135) & ~((ax > .40) & (z < .16))] = 1                                   # cam + siyah tavan (aynalar hariç)
S_[(z < -.20) & ((ax > .30) | (y < -.80) | (y > .85))] = 2                       # alt kaplama
S_[(td < .21) & (ax > .33)] = 2                                                  # çamurluk kaplaması
S_[(td < .165) & (ax > .30)] = 4; S_[(td < .112) & (ax > .30)] = 5               # lastik, jant
S_[(y < -.90) & (z > -.14) & (z < -.012) & (ax < .21)] = 3                          # krom ızgara
S_[(y < -.885) & (z > .026) & (z < .039)] = 6                                       # ön LED imza şeridi
S_[(y > .90) & (z > .068) & (z < .092) & (ax < .36)] = 7                                        # arka LED
for m_ in (BOYA, CAM, SIYAH, KROM, LAST, JANT, LEDB, LEDK): me.materials.append(m_)
me.polygons.foreach_set('material_index', [int(np.bincount(S_[list(p.vertices)], minlength=8).argmax()) for p in me.polygons])
for p in me.polygons: p.use_smooth = True
araba.matrix_world = Matrix.Translation((0, 0, .379 * 2.315)) @ Matrix.Rotation(math.pi / 2, 4, 'Z') @ Matrix.Scale(2.315, 4)   # ön +X (-Y -> +X: +90°; -90 arkayı gösteriyordu) (kamera düzeni korunur), tekerler zeminde
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
print('T10X bölge', np.bincount(S_, minlength=8))
es = LEDB.node_tree.nodes['Principled BSDF'].inputs['Emission Strength']   # uyanış: LED şerit 0,4 sn'de yanar
for f_, v_ in ((1, 0.), (8, 0.), (14, 60.), (20, 34.)): es.default_value = v_; es.keyframe_insert('default_value', frame=f_)
# stüdyo: yansıtıcı koyu zemin + arka duvarda parlayan TOGG logosu + ışıklar
bpy.ops.mesh.primitive_plane_add(size=60); z = bpy.context.object; bagla(z, malz('zemin', (.006, .006, .007), .36, **{'Coat Weight': .5, 'Coat Roughness': .05}))   # .12 parlak zeminde ışın izleme gürültüsü
yl = resim_etiket('togg_duvar', os.path.join(LOGO, 'togg-yazi.png'), 3.2, None, alfa=True, emisyon=3.0); yl.rotation_euler = (math.pi / 2, 0, math.pi / 2); yl.location = (-6.5, 0, 2.4)   # -pi/2 ayna görüntü veriyordu
isik('tepe', 'AREA', (-1.0, 0, 4.4), (0, 0, 0), 160, (1, 1, 1), 3.5)   # gerçek model: tepe yumuşak ışık hatları gösterir
sup = isik('supurme', 'AREA', (4, -5, 1.8), (0, 0, .8), 500, (.85, .9, 1), .8)
sup.keyframe_insert('location', frame=1); sup.location = (4, 5, 1.8); sup.keyframe_insert('location', frame=NK)   # ışık süpürmesi: boya yansıması akar
isik('kenar', 'AREA', (-4.5, 2.6, 2.2), (0, 0, 1.0), 1100, (1, .95, .9), .8); isik('kenar2', 'AREA', (-4.5, -2.6, 2.2), (0, 0, 1.0), 1100, (.85, .9, 1), .8)   # arkadan iki kenar ışığı: tavan + omuz hattı
kam = kamera(50, 2.0); kam.data.dof.focus_object = araba
bak(kam, (6.6, -3.4, .95), (0, 0, .75), 1); bak(kam, (6.4, -1.5, .88), (.1, 0, .76), NK); yumusak_egriler(kam)   # önden alçak, yavaş yaklaşma: LED imza şeridi kadrajın ortasında
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(UW, 'sahne_togg.blend')); print('TOGG kaydedildi', NK)
