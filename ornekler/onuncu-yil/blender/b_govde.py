# Blender: Hunyuan3D-2.1 kürsü gövdesi (heykel/uretim/hunyuan21-kursu.glb; girdi: nutuk 191,5 sn karesi, mikrofon silinmiş) -> ata-govde.blend
# 1) yüz +X'e bakıyor -> matrisle Z -90° (ön -Y); 2) en büyük bağlı parça kalır (mikrofon plakası, zil kırıntıları gider);
# 3) ölçek: omuz genişliği 0,46 m, ayak z=0 varsayımıyla omuz z 1,42 (kişi 1,75); 4) bölge rengi: girdi karesi önden izdüşümle örneklenir
# (koyu = frak yünü, açık = gömlek/yelek/kâğıt, orta = el) -> köşe rengi 'Bolge'. Kullanım: blender -b -P b_govde.py
import bpy, bmesh, os, math, numpy as np
from mathutils import Vector, Matrix
W = os.path.dirname(os.path.abspath(__file__)); U = os.path.join(W, '..', 'heykel', 'uretim')
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=os.path.join(U, 'hunyuan21-kursu.glb'))
o = [x for x in bpy.data.objects if x.type == 'MESH'][0]; o.name = 'govde'
bpy.context.view_layer.objects.active = o; o.select_set(True); bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
o.matrix_world = Matrix.Rotation(-math.pi / 2, 4, 'Z') @ o.matrix_world; bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)   # glTF nesnesi kuaterniyon modunda: rotation_euler etkisiz
for x in list(bpy.data.objects):
    if x is not o: bpy.data.objects.remove(x)
# en büyük bağlı parça
bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
gor = set(); parcalar = []
for v in bm.verts:
    if v.index in gor: continue
    yig = [v]; gor.add(v.index); par = []
    while yig:
        q = yig.pop(); par.append(q)
        for e in q.link_edges:
            w_ = e.other_vert(q)
            if w_.index not in gor: gor.add(w_.index); yig.append(w_)
    parcalar.append(par)
parcalar.sort(key=len, reverse=True); sil = [v for p in parcalar[1:] for v in p]
print('PARÇA', len(parcalar), 'en büyük', len(parcalar[0]), 'silinen köşe', len(sil))
bmesh.ops.delete(bm, geom=sil, context='VERTS'); bm.to_mesh(o.data); bm.free()
# 2b) yapışık fazlalıklar (kesitlerden): sırtta ince levha (y > .66), sağ önde mikrofon plakası (çizgi (.42,-.2)-(.8,.1), z < -.25), bel altı (z < -.8)
from mathutils import Vector as V_
bm = bmesh.new(); bm.from_mesh(o.data)
p0, p1 = np.array([.42, -.2]), np.array([.80, .10]); dv = p1 - p0
def plaka(c):
    q = np.array([c.x, c.y]); t = np.clip((q - p0) @ dv / (dv @ dv), -.1, 1.15); return np.linalg.norm(q - (p0 + t * dv)) < .03 and -1.0 < c.z < -.30 and c.x > .43   # el/önkol x < .40 (ilk denemede .035 + z sınırsız sol önkolu deldi)
sil = [v for v in bm.verts if v.co.y > .66 or v.co.z < -.95 or plaka(v.co)]   # alt uç sonra 0,85 m'ye uzatılır (kürsü üstünden gövde ~0,93 m'ye dek görünür)   # z < -.66 (dünya < 1,155 m) kürsü arkasında
bmesh.ops.delete(bm, geom=sil, context='VERTS'); print('FAZLALIK silinen', len(sil))
# 3) baş kaldırılır (yaka üstü z > .43; bizim başımız takılacak)
sil = [v for v in bm.verts if v.co.z > .44]   # yaka üstü tümü (ilk deneme yalnız önü silmiş, ense kabuğu + kulaklar kalmıştı)
bmesh.ops.delete(bm, geom=sil, context='VERTS'); print('BAŞ silinen', len(sil))
bm.verts.ensure_lookup_table(); gor = set(); kucuk = []   # silmelerden sonra kopan küçük parçalar (mikrofon çubuğu iğnesi)
for v in bm.verts:
    if v.index in gor: continue
    yig = [v]; gor.add(v.index); par = []
    while yig:
        q = yig.pop(); par.append(q)
        for e in q.link_edges:
            w_ = e.other_vert(q)
            if w_.index not in gor: gor.add(w_.index); yig.append(w_)
    if len(par) < 3000: kucuk += par
bmesh.ops.delete(bm, geom=kucuk, context='VERTS'); print('KOPUK silinen', len(kucuk))
bm.to_mesh(o.data); bm.free()
# 4b) sol bilekte dikey iğne (girdideki mikrofon ayağının kâğıt altı kısmı): dünya x .121, y -.06, z > 1.205 -> birim uzayında (S öncesi) karşılığı aşağıda ölçekten sonra silinir
# 4) ölçek + yer: omuz dış genişliği ~1,6 birim = 0,46 m; omuz üstü z .25 birim -> 1,42 m
S = .46 / 1.6; o.matrix_world = Matrix.Translation((0, 0, 1.42)) @ Matrix.Scale(S, 4) @ Matrix.Translation((0, 0, -.25)); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bm = bmesh.new(); bm.from_mesh(o.data)
ig = [v for v in bm.verts if abs(v.co.x - .121) < .0075 and -.085 < v.co.y < -.035 and (v.co.z > 1.19 or v.co.z < 1.168)]   # mikrofon ayağı: elin üstü + altı (uzatmayla aşağı iniyordu)
bmesh.ops.delete(bm, geom=ig, context='VERTS'); print('İĞNE silinen', len(ig)); bm.to_mesh(o.data); bm.free()
# 5) çene kalıntısı (Hunyuan başının yaka önünde kalan kısmı): bizim boynumuz buraya girer
bm = bmesh.new(); bm.from_mesh(o.data)
ck = [v for v in bm.verts if v.co.z > 1.425 and abs(v.co.x - .008) < .055 and v.co.y < .02]
bmesh.ops.delete(bm, geom=ck, context='VERTS'); print('ÇENE silinen', len(ck)); bm.to_mesh(o.data); bm.free()
# 5b) alt kenar: sınır kenarları 0,85 m'ye uzatılır (düz ceket), hafif içe daralma
bm = bmesh.new(); bm.from_mesh(o.data); bm.edges.ensure_lookup_table()
cb = [v for v in bm.verts if v.co.z < 1.15 and v.co.y < -.045 and .06 < v.co.x < .14]   # mikrofon ayağının bel hizası kalıntısı (uzatmada önde çubuk oluyordu)
bmesh.ops.delete(bm, geom=cb, context='VERTS'); bm.edges.ensure_lookup_table(); print('ÇUBUK silinen', len(cb))
alt = [e for e in bm.edges if e.is_boundary and all(v.co.z < 1.10 and v.co.y > -.045 for v in e.verts)]
r_ = bmesh.ops.extrude_edge_only(bm, edges=alt); yeni = [g for g in r_['geom'] if isinstance(g, bmesh.types.BMVert)]
for v in yeni: v.co.z = .85; v.co.x *= .97; v.co.y = v.co.y * .97 + .002
print('UZATMA kenar', len(alt), 'yeni köşe', len(yeni))
dl = [e for e in bm.edges if e.is_boundary and all(.9 < v.co.z < 1.40 for v in e.verts)]   # yaka ağzı (z > 1,40) ve alt uç (z .85) açık kalır
hf = bmesh.ops.holes_fill(bm, edges=dl, sides=600); print('DELİK kapatılan yüz', len(hf['faces']))
bm.to_mesh(o.data); bm.free()
# 6) BÖLGE (geometriyle; _g2 ızgara ölçümü, dünya metre): 0 frak yünü, 1 beyaz (gömlek/yelek/papyon/yaka/manşet), 2 ten (eller), 3 kâğıt
me_ = o.data; me_.update(); n_ = len(me_.vertices); A = np.zeros(n_ * 3); me_.vertices.foreach_get('co', A); A = A.reshape(-1, 3)
N_ = np.zeros(n_ * 3); me_.vertices.foreach_get('normal', N_); N_ = N_.reshape(-1, 3); x, y, z = A.T
sinif = np.zeros(n_, np.int32)
kutu_ = (x > -.05) & (x < .105) & (y < -.07) & (z > 1.15) & (z < 1.245)   # kâğıt + üstündeki parmaklar
aday = kutu_ & (y < -.135)   # parmakların ötesi: yalnız kâğıt -> düzlem uydur
P_ = A[aday]; c_ = P_.mean(0); _, _, vt = np.linalg.svd(P_ - c_); nrm = vt[2]
ud = (A - c_) @ nrm; ud = ud * np.sign(np.median(N_[aday] @ nrm) or 1)
kagit = kutu_ & (np.abs(ud) < .0075)
sag_el = (x < .0) & (y < -.05) & (z < 1.245) & (z > 1.15) & (x > -.13)
sol_el = (x >= .0) & (y < -.04) & (z < 1.25) & (z > 1.15) & (x < .16)
el = (sag_el | sol_el) & ~kagit
mans = ((x < .0) & (y >= -.05) & (y < -.038) | (x >= .0) & (y >= -.04) & (y < -.028)) & (z < 1.25) & (z > 1.16) & (np.abs(x) > .07)
gomlek = (np.abs(x + .01) < .034) & (N_[:, 1] < -.35) & (z > 1.17) & (z < 1.47) & (y < .01)
yaka = z > 1.442
papyon = (z > 1.35) & (z < 1.44) & (np.abs(x - .009) < .06) & (y < .04) & (N_[:, 1] < .2)   # beyaz papyon (frak + white tie)
sinif[gomlek | yaka | mans | papyon] = 1; sinif[el] = 2; sinif[kagit] = 3
ag_ = me_.attributes.get('bolge') or me_.attributes.new('bolge', 'INT', 'POINT'); ag_.data.foreach_set('value', sinif)
# yumuşak bölge ağırlıkları (malzeme sınırı basamaklı görünmesin): tek-sıcak -> komşu ortalaması 4 tur -> köşe rengi BolgeW = (beyaz, ten, kâğıt)
E_ = np.zeros(len(me_.edges) * 2, dtype=np.int64); me_.edges.foreach_get('vertices', E_); E_ = E_.reshape(-1, 2)
ki_ = np.r_[E_[:, 0], E_[:, 1]]; kj_ = np.r_[E_[:, 1], E_[:, 0]]; dg_ = np.maximum(np.bincount(ki_, minlength=n_), 1).astype(float)
Wt_ = np.eye(4)[sinif]
for _ in range(4): Wt_ = .5 * Wt_ + .5 * np.stack([np.bincount(ki_, weights=Wt_[kj_, c], minlength=n_) for c in range(4)], 1) / dg_[:, None]
cw_ = me_.color_attributes.get('BolgeW') or me_.color_attributes.new('BolgeW', 'FLOAT_COLOR', 'POINT'); cw_.data.foreach_set('color', np.c_[Wt_[:, 1], Wt_[:, 2], Wt_[:, 3], np.ones(n_)].ravel())
print('BÖLGE', np.bincount(sinif, minlength=4), 'kâğıt normali', nrm.round(3))
A = np.array([v.co[:] for v in o.data.vertices])
print('KUTU m', A.min(0).round(3), A.max(0).round(3))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(W, 'ata-govde.blend'))
