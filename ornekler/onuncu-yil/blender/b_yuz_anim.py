# Blender: sahne.blend -> yüz canlılığı (sahne_anim.blend): dudak hattı kesilir (ağız gerçekten açılır) + koyu ağız içi; şekil anahtarları 'kirp' (göz kırpma:
# üst kapak derisi göz küresinin üstünden iner) ve 'agiz' (alt dudak + çene aşağı); her göz için bakış boşluğu (göz küresi parçaları onun çocuğu).
# Baş birimi (renkli.blend yerel; metre = x .5418): göz merkezleri renkli.json, noktalar nakil2-noktalar3.json. Kullanım: blender -b -P b_yuz_anim.py [-- test]
import bpy, bmesh, os, sys, json, math, numpy as np
from mathutils import Vector
W = os.path.dirname(os.path.abspath(__file__)); T = os.path.join(W, '..', 'heykel', 'tripo')
bpy.ops.wm.open_mainfile(filepath=os.path.join(W, 'sahne.blend')); sc = bpy.context.scene
bas = bpy.data.objects['bas']; pv = bpy.data.objects['bas_pivot']
L = {int(k): np.array(v) for k, v in json.load(open(os.path.join(T, 'nakil2-noktalar3.json'))).items()}
G = {s: (np.array(zc), R, np.array(il)) for s, zc, R, il in json.load(open(os.path.join(T, 'renkli.json')))['goz']}
ss = lambda x: np.clip(x, 0, 1) ** 2 * (3 - 2 * np.clip(x, 0, 1))
xm = float(np.mean([L[i][0] for i in (168, 6, 1, 152)]))
# ---------- 1) dudak hattı: üst/alt dudak arasındaki kenarlar ayrılır ----------
z0 = (L[13][2] + L[14][2]) / 2; yarim = abs(L[291][0] - L[61][0]) / 2
ALT_DIKIS = set()   # dudak kesme yöntemi bırakıldı (açılınca barkod gibi şerit kalıyordu): ağız boşluğu nesnesi + alt dudak/çene inişi
me = bas.data; n = len(me.vertices); A = np.zeros(n * 3); me.vertices.foreach_get('co', A); A = A.reshape(-1, 3)
# ---------- 2) şekil anahtarları ----------
if not me.shape_keys: bas.shape_key_add(name='Basis')
K = bas.shape_key_add(name='agiz'); B = A.copy()
dx = np.abs(A[:, 0] - xm) / (yarim * 2.3); wx = np.clip(1 - dx ** 2, 0, 1) ** 1.5   # yanaklara geniş geçiş
wz = ss((z0 + .002 - A[:, 2]) / .006) * ss((A[:, 2] - (L[152][2] - .07)) / .06)   # dudak altından çene altına (eski formül işaret hatasıyla 0 veriyordu)
on = ss((L[14][1] + .06 - A[:, 1]) / .04)
acik = .0095   # 5 mm (baş birimi): alt dudak + çene iner
w = wx * wz * on
B[:, 2] -= acik * w; B[:, 1] += acik * .2 * w   # tek parça yumuşak iniş (çenede kırık çizgi kalkar)
K.data.foreach_set('co', B.ravel())
K2 = bas.shape_key_add(name='kirp'); C = A.copy()
for s, (zc, R, il) in G.items():
    eks = np.cross(np.array([0, 0, 1.]), il); eks /= np.linalg.norm(eks)
    rel = A - zc; f = rel @ il; u = (rel @ eks) / (R * 1.35); v = rel[:, 2]
    bolge = (f > -.1 * R) & (np.abs(u) < 1) & (v > -.15 * R) & (v < 1.15 * R) & (np.linalg.norm(rel, axis=1) < 1.7 * R)   # kaş altı oynamaz (gerilme çizgisi)
    wk = np.where(bolge, (1 - u ** 2) * ss((1.15 * R - v) / (.85 * R)), 0)
    hedef = -.32 * R
    Cz = v + (hedef - v) * wk * ss((v - hedef) / (.2 * R))   # kapak kenarı merkezin altına iner, yukarısı orantılı
    yeni = np.c_[rel[:, 0], rel[:, 1], Cz]
    r_ = np.linalg.norm(yeni, axis=1); it_ = np.where(bolge & (r_ < 1.05 * R) & (yeni @ il > 0), 1.05 * R / np.maximum(r_, 1e-6), 1)   # göz küresinin dışında kalır
    yeni = yeni * it_[:, None]
    C[bolge] = (zc + yeni)[bolge]
    alt = (f > -.1 * R) & (np.abs(u) < 1) & (v < -.1 * R) & (v > -.9 * R) & (np.linalg.norm(rel, axis=1) < 1.6 * R)   # alt kapak hafif yukarı
    C[alt, 2] += (.18 * R * (1 - u[alt] ** 2) * ss((v[alt] + .9 * R) / (.6 * R)))
K2.data.foreach_set('co', C.ravel())
print('ŞEKİL agiz köşe', int((w > .05).sum()), 'kirp köşe', int((np.linalg.norm(C - A, axis=1) > 1e-5).sum()))
# ---------- 3) ağız içi (koyu) + göz bakış boşlukları ----------
Mw = bas.matrix_world
mi = np.array([xm, L[13][1] + .0105, z0 - .001])   # ağız boşluğu: yassı koyu elipsoid, önü dudak yüzeyinin ~1,5 mm önünde; dikey ölçeği konuşmayla büyür
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=32, ring_count=16, location=Mw @ Vector(mi)); ai = bpy.context.object; ai.name = 'agiz_ici'
ai.scale = (yarim * .5418 * .58, .0055, .001); ai.data.materials.append(bpy.data.materials.get('agiz_ici_m') or bpy.data.materials.new('agiz_ici_m'))   # dar: profilde dudak köşesinden iğne gibi taşıyordu
m_ = ai.data.materials[0]; m_.use_nodes = True; m_.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.03, .008, .008, 1); m_.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .5
bpy.context.view_layer.update()   # ölçek matrix_world'e geçsin (animasyonlu ölçek: uygulanamaz)
mw_ = ai.matrix_world.copy(); ai.parent = pv; ai.matrix_parent_inverse = pv.matrix_world.inverted(); ai.matrix_world = mw_
bpy.context.view_layer.update()
for s, (zc, R, il) in G.items():
    gb = bpy.data.objects.new('bakis_' + s, None); gb.location = Mw @ Vector(zc); sc.collection.objects.link(gb); bpy.context.view_layer.update()
    gb.parent = pv; gb.matrix_parent_inverse = pv.matrix_world.inverted(); gb.location = Mw @ Vector(zc); bpy.context.view_layer.update()
    for ad in ('goz', 'iris', 'bebek', 'kornea'):
        o = bpy.data.objects.get(ad + s)
        if o: mw = o.matrix_world.copy(); o.parent = gb; o.matrix_parent_inverse = gb.matrix_world.inverted(); o.matrix_world = mw
bpy.context.view_layer.update()
if 'test' in sys.argv:
    from mathutils import Vector as V
    kam = sc.camera; kam.location = (.12, -.75, 1.56); kam.rotation_euler = (V((0, 0, 1.55)) - kam.location).to_track_quat('-Z', 'Y').to_euler(); kam.data.lens = 85; kam.data.dof.use_dof = False
    sc.cycles.samples = 32; sc.render.resolution_percentage = 40
    for ad, (a_, k_) in (('ac', (1, 0)), ('kirp', (0, 1)), ('normal', (0, 0))):
        me.shape_keys.key_blocks['agiz'].value = a_; me.shape_keys.key_blocks['kirp'].value = k_; ai.scale[2] = .001 + .0055 * a_
        sc.render.filepath = os.path.join(W, f'_yz_{ad}.png'); bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(W, 'sahne_anim.blend')); print('YÜZ ANİM kaydedildi')
