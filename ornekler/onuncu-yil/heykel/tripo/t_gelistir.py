# Blender: nakil2.blend (Tripo yüzü + Hunyuan kafatası) -> kaş şeridi düzleştirme, gerçek göz (v13 modülü), renk + malzeme -> renkli.blend
# Noktalar: nakil2-noktalar3.json (hizalı dünya uzayı). Koordinat: Z yukarı, ön -Y. Kullanım: blender -b -P t_gelistir.py
import bpy, bmesh, os, json, math, numpy as np
from mathutils import Vector
W = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(W, 'nakil2.blend'))
o = bpy.data.objects['bas']; me = o.data
bpy.context.view_layer.objects.active = o; o.select_set(True); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6); bm.to_mesh(me); bm.free()   # UV dikişlerinde çift köşe: komşu ortalaması dikişi çatlatır
n = len(me.vertices); A = np.zeros(n * 3); me.vertices.foreach_get('co', A); A = A.reshape(-1, 3)
def oz(ad): v = np.zeros(n); me.attributes[ad].data.foreach_get('value', v); return v
NAK, YUZ, KUL = oz('nakil'), oz('yuz'), oz('kulak')
E = np.zeros(len(me.edges) * 2, dtype=np.int64); me.edges.foreach_get('vertices', E); E = E.reshape(-1, 2)
kom_i = np.r_[E[:, 0], E[:, 1]]; kom_j = np.r_[E[:, 1], E[:, 0]]; der = np.bincount(kom_i, minlength=n).astype(float)
def ort(X): return np.stack([np.bincount(kom_i, weights=X[kom_j, k], minlength=n) for k in range(X.shape[1])], 1) / np.maximum(der, 1)[:, None]
def normaller():
    me.vertices.foreach_set('co', A.ravel()); me.update(); N_ = np.zeros(n * 3); me.vertices.foreach_get('normal', N_); return N_.reshape(-1, 3)
N = normaller()
L = {int(k): np.array(v) for k, v in json.load(open(os.path.join(W, 'nakil2-noktalar3.json'))).items()}
nk = lambda *ix: np.mean([L[i] for i in ix if i in L], axis=0)
def gauss(c, r): d2 = ((A - c) ** 2).sum(1); return np.exp(-d2 / (2 * r * r))
def segment_uzak(p0, p1): v = p1 - p0; t = np.clip(((A - p0) @ v) / (v @ v), 0, 1); return np.linalg.norm(A - (p0 + t[:, None] * v), axis=1)
def cizgi_uzak(P): return np.min([segment_uzak(P[k], P[k + 1]) for k in range(len(P) - 1)], axis=0)
ss_ = lambda x: np.clip(x, 0, 1) ** 2 * (3 - 2 * np.clip(x, 0, 1))
yuzon = np.clip(-N[:, 1] * 1.5, 0, 1)
olc = np.linalg.norm(nk(33) - nk(263)); xm = nk(6, 168, 1)[0]; print('ÖLÇEK göz-göz', round(olc, 4))
KAS = ((70, 63, 105, 66, 107), (300, 293, 334, 296, 336))
# ---------- 1) kaş şeridi: Tripo'nun yırtık kaş geometrisi (yüksek frekans) düzleşir, kaş kemeri hacmi (düşük frekans) kalır ----------
kw = np.zeros(n)
for kas in KAS: kw = np.maximum(kw, np.exp(-(cizgi_uzak([nk(i) for i in kas]) / (.07 * olc)) ** 2))
kw *= yuzon
for _ in range(30): A += (ort(A) - A) * (.6 * kw)[:, None]
N = normaller()
# ---------- 1b) burun kemeri: yönetmen profilde kemerli buldu -> sırt, kök (168) ile uç (4) doğrusunun önüne taşan kısmın %80'i geri ----------
p_k, p_u = nk(168), nk(4)
tz = np.clip((A[:, 2] - p_k[2]) / (p_u[2] - p_k[2]), 0, 1); yl = p_k[1] + (p_u[1] - p_k[1]) * tz
wN = np.exp(-((A[:, 0] - xm) / (.10 * olc)) ** 2) * ss_(tz / .1) * ss_((1 - tz) / .15) * yuzon
tas = np.maximum(yl - A[:, 1], 0)   # önü -Y: doğrunun önündeki fazlalık
A[:, 1] += .8 * wN * tas
for _ in range(10): A += (ort(A) - A) * (.4 * wN)[:, None]
print('BURUN kemer en çok', round(float((tas * wN).max() / olc * 100), 2), '% göz-göz')
N = normaller()
# ---------- 2) gözler (v13 modülü): badem yarık, deri göz küresinin arkasına; Tripo'nun kısık sağ gözü de aynı badem ölçüsüyle açılır ----------
cuk = sum(gauss(nk(a_) + (nk(a_) - nk(b_)) * .12, .09 * olc) for a_, b_ in ((133, 33), (362, 263)))
for _ in range(80): A += (ort(A) - A) * (np.clip(cuk * 1.4, 0, 1) * .7)[:, None]
gozb = np.zeros(n)
for dis, ic in ((33, 133), (263, 362)): gozb = np.maximum(gozb, gauss((nk(dis) + nk(ic)) / 2, .35 * olc))
for _ in range(25): A += (ort(A) - A) * (.5 * np.clip(gozb * 1.3, 0, 1))[:, None]   # boyalı göz kabartısı (Tripo) yarık oyulmadan yumuşar
N = normaller()
GOZ = []; YARIK = []
for s, (dis, ic) in {'R': (33, 133), 'L': (263, 362)}.items():
    pd, pi = nk(dis), nk(ic); gw0 = np.linalg.norm(pd - pi)
    pi = pi + (pi - pd) / gw0 * .10 * gw0; pd = pd + (pd - pi) / np.linalg.norm(pd - pi) * .015 * gw0   # Tripo köşeleri gerçek yarığa yakın: iç uzatma .28 -> .10
    c = (pd + pi) / 2; gw = np.linalg.norm(pd - pi)
    R = .50 * gw
    eks = (pd - pi) / gw; yuk = np.array([0, 0, 1.]); ileri = np.cross(eks, yuk); ileri = ileri if ileri[1] < 0 else -ileri
    zc = c + ileri * (-R * .9)
    q = A - c; u = (q @ eks) / (gw / 2); v = q @ yuk; derin = q @ ileri
    uu = np.clip(np.abs(u), 0, 1)
    ust_k = .16 * gw - .14 * gw * uu ** 2 + (.02 * gw * u if s == 'R' else -.02 * gw * u)   # ağır üst kapak, dış köşe hafif aşağı
    alt_k = -.10 * gw + .09 * gw * uu ** 2
    d = np.maximum.reduce([v - ust_k, alt_k - v, (np.abs(u) - 1) * gw / 2])
    yakin = (np.abs(u) < 1.6) & (np.abs(v) < .5 * gw) & (derin > -.6 * gw)
    kure_on = np.sqrt(np.maximum(0, R * R - ((A - zc) ** 2).sum(1) + ((A - zc) @ ileri) ** 2))
    hedef = ((zc - c) @ ileri) + kure_on
    t = np.clip((d + .02 * gw) / (.08 * gw), 0, 1); t = t * t * (3 - 2 * t)
    hz = hedef - .02 * gw + .06 * gw * t
    hz = np.maximum(hz, (zc - c) @ ileri + .45 * R)
    yeni = np.where(d < 0, np.minimum(derin, hz), np.where((d < .25 * gw) & (np.abs(u) < 1), np.maximum(derin, hz), derin))
    A[yakin] += ileri * (yeni - derin)[yakin, None]
    ku = yakin * (np.abs(u) < 1) * (v > 0) * np.exp(-((d - .05 * gw) / (.06 * gw)) ** 2) * (1 - uu ** 2)
    A += ileri * (.035 * gw * ku)[:, None]
    kv = v - (ust_k + .17 * gw); kiv = yakin * (np.abs(u) < 1.1) * np.exp(-(kv / (.035 * gw)) ** 2) * (1 - uu ** 2)
    A -= N * (.018 * gw * kiv)[:, None]
    GOZ.append((s, zc, R, ileri)); YARIK.append((d, v, yakin, gw, kiv, pi))
N = normaller()
# ---------- 3) saç maskesi: Hunyuan'dan gelen bölge, saç çizgisinin üstü; önde şakaklar geri çekik (M), arkada ense ----------
kz = nk(234, 454)[2]; yk = nk(234, 454)[1]
arka = ss_((A[:, 1] - yk + .1 * olc) / (.5 * olc))
yan = ss_((np.abs(A[:, 0] - xm) - .25 * olc) / (.5 * olc))
on_hat = nk(10)[2] + .30 * olc + .22 * olc * yan   # alın ortası saç çizgisi, şakakta yukarı
hat = on_hat * (1 - arka) + (kz - .55 * olc) * arka
sacw = ss_((A[:, 2] - hat + .05 * olc) / (.10 * olc)) * np.clip(NAK * 1.5, 0, 1) * (1 - KUL)
for s_ in (234, 454):   # kulak kepçesi ve arkası ten
    kc_ = L[s_] + np.array([np.sign(L[s_][0] - xm) * .25 * olc, .25 * olc, -.05 * olc]); sacw *= 1 - gauss(kc_, .28 * olc)
for _ in range(10): sacw = ort(sacw[:, None])[:, 0]
for _ in range(6): A += (ort(A) - A) * (.35 * sacw)[:, None]   # Hunyuan kil topakları yumuşar, tel dokusu gölgelendiriciden
N = normaller()
# ---------- 4) renk (köşe rengi, sRGB -> doğrusal); portre: sıcak pembe-bej ten, kumral-kül saç, açık buz mavisi göz ----------
ten = np.array([.79, .58, .46]); ten2 = np.array([.71, .46, .38]); sacR = np.array([.40, .33, .25]); sacA = np.array([.60, .51, .39])   # portre: ten daha sıcak, soluk pembe değil
C = np.tile(ten, (n, 1))
for k in (205, 425, 4):   # yanak + burun ucu sıcaklığı
    g = (.14 if k != 4 else .2) * gauss(nk(k), (.30 if k != 4 else .10) * olc)[:, None]; C = C * (1 - g) + ten2 * g   # yanakta iki kırmızı leke vardı
dud = [nk(i) for i in (61, 40, 37, 0, 267, 270, 291)]; dud2 = [nk(i) for i in (61, 91, 84, 17, 314, 321, 291)]
dw = np.maximum(np.exp(-(cizgi_uzak(dud) / (.022 * olc)) ** 2), np.exp(-(cizgi_uzak(dud2) / (.035 * olc)) ** 2)) * yuzon
C = C * (1 - .45 * dw[:, None]) + np.array([.66, .42, .38]) * .45 * dw[:, None]
kil = np.sin(A @ np.array([1913., 377., 2711.])) + np.sin(A @ np.array([-517., 2203., 1409.]))   # kaş kenarı tüylü: köşe başına sözde gürültü
for _ in range(2): kil = ort(kil[:, None])[:, 0]
kil = kil / (np.abs(kil).max() + 1e-9)
kasT = np.zeros(n)
for kas in KAS:
    P_ = [nk(i) + np.array([0, 0, -.006 * olc]) for i in kas]   # kas: dış uç -> iç uç; portre: kaş göze yakın, alçak
    dk = np.array([segment_uzak(P_[k], P_[k + 1]) for k in range(len(P_) - 1)]); ki = dk.argmin(0); du = dk.min(0)
    p0 = np.array(P_)[ki]; p1 = np.array(P_)[ki + 1]; vv = p1 - p0; tt_ = np.clip(((A - p0) * vv).sum(1) / (vv * vv).sum(1), 0, 1)
    sk = (ki + tt_) / (len(P_) - 1)   # 0 kuyruk, 1 iç uç
    gen = .030 * olc + .030 * olc * ss_(sk / .6)   # portre: içte gür, kuyrukta incelir (düz şerit kalem gibiydi)
    kw = ss_((gen + .012 * olc * kil - du) / (.018 * olc)) * yuzon * ss_((sk + .04) / .08)
    C = C * (1 - .85 * kw[:, None]) + np.array([.33, .26, .19]) * .85 * kw[:, None]
    kasT = np.maximum(kasT, kw)
for s, zc, R, ileri in GOZ:   # göz altı / kapak gölgesi
    g = gauss(zc + ileri * R + np.array([0, 0, -.25 * R]), 1.1 * R) * yuzon
    C = C * (1 - .22 * g[:, None]) + np.array([.58, .40, .35]) * .22 * g[:, None]
for s, zc, R, ileri in GOZ:   # göz çukuru: kaş kemeri altı ile üst kapak arası gölge (portre: derine gömülü bakış)
    g = gauss(zc + ileri * .7 * R + np.array([0, 0, .75 * R]), .95 * R) * yuzon
    C = C * (1 - .30 * g[:, None]) + np.array([.48, .31, .26]) * .30 * g[:, None]
for d, v, yakin, gw, kiv, pi_ in YARIK:
    kw = yakin * (np.exp(-((d - .004 * gw) / (.024 * gw)) ** 2) * (v > 0) * 1. + .35 * np.exp(-((d - .004 * gw) / (.03 * gw)) ** 2) * (v <= 0))
    C = C * (1 - .6 * kw[:, None]) + np.array([.24, .17, .13]) * .6 * kw[:, None]
    C = C * (1 - .3 * kiv[:, None]) + np.array([.50, .34, .29]) * .3 * kiv[:, None]
    kr = gauss(pi_, .07 * gw)[:, None]; C = C * (1 - .7 * kr) + np.array([.80, .50, .47]) * .7 * kr
pur = np.linalg.norm(A - ort(A), axis=1)
for _ in range(4): pur = ort(pur[:, None])[:, 0]
tel = np.clip((pur - np.percentile(pur, 40)) / (np.percentile(pur, 97) - np.percentile(pur, 40) + 1e-12), 0, 1)
sacC = sacR * .5 + sacA * .5 + (sacA - sacR) * (tel[:, None] - .5) * .3
C = C * (1 - sacw[:, None]) + sacC * sacw[:, None]
# yaka: Tripo'nun kanat yakası + papyon (nutuk kıyafeti) -> Tripo dokusundan oku: çene altında açık ve renksiz = beyaz yaka, çok koyu = papyon
bimg = next((im for im in bpy.data.images if 'basecolor' in im.name.lower()), None)
if bimg:
    bw_, bh_ = bimg.size; px = np.zeros(bw_ * bh_ * 4, dtype=np.float32); bimg.pixels.foreach_get(px); px = px.reshape(bh_, bw_, 4)
    uvl = me.uv_layers.active.data; uv = np.zeros(len(uvl) * 2); uvl.foreach_get('uv', uv); uv = uv.reshape(-1, 2)
    lv = np.zeros(len(me.loops), dtype=np.int64); me.loops.foreach_get('vertex_index', lv)
    U = np.zeros((n, 2)); cnt = np.bincount(lv, minlength=n); U[:, 0] = np.bincount(lv, uv[:, 0], n) / np.maximum(cnt, 1); U[:, 1] = np.bincount(lv, uv[:, 1], n) / np.maximum(cnt, 1)
    T_ = px[np.clip((U[:, 1] * bh_).astype(int), 0, bh_ - 1), np.clip((U[:, 0] * bw_).astype(int), 0, bw_ - 1), :3]
    lum = T_.mean(1); doy = T_.max(1) - T_.min(1)
    alt = ss_((nk(152)[2] + .05 * olc - A[:, 2]) / (.08 * olc)) * (1 - NAK)
    beyaz = alt * ss_((lum - .45) / .15) * ss_((.12 - doy) / .06); siyah = alt * ss_((.10 - lum) / .05)
    for _ in range(3): beyaz = ort(beyaz[:, None])[:, 0]; siyah = ort(siyah[:, None])[:, 0]
    C = C * (1 - beyaz[:, None]) + np.array([.90, .89, .86]) * beyaz[:, None]
    C = C * (1 - siyah[:, None]) + np.array([.03, .03, .035]) * siyah[:, None]
    print('YAKA beyaz', int((beyaz > .5).sum()), 'papyon', int((siyah > .5).sum()))
Ao = A.copy()
for _ in range(12): Ao = ort(Ao)
kav = np.clip(((Ao - A) * N).sum(1) / (.012 * olc), -1, 1)   # + çukur (kırışık dibi, burun-dudak, göz çukuru), - tümsek
kv_ = np.clip(kav, 0, 1) * (1 - sacw)
C = C * (1 - .07 * kv_[:, None]) + C * np.array([.78, .62, .58]) * .07 * kv_[:, None]   # çukurlar koyu-sıcak: düz manken teni gider
C = C * (1 + .06 * np.clip(-kav, 0, 1) * (1 - sacw))[:, None]
C = np.where(C <= .04045, C / 12.92, ((C + .055) / 1.055) ** 2.4)
me.vertices.foreach_set('co', A.ravel()); me.update()
for ad in ('Renk', 'Sac', 'Yuz', 'Kas'):
    if ad in me.color_attributes: me.color_attributes.remove(me.color_attributes[ad])
me.color_attributes.new('Renk', 'FLOAT_COLOR', 'POINT').data.foreach_set('color', np.c_[C, np.ones(n)].ravel())
me.color_attributes.new('Sac', 'FLOAT_COLOR', 'POINT').data.foreach_set('color', np.c_[np.repeat(sacw[:, None], 3, 1), np.ones(n)].ravel())
me.color_attributes.new('Kas', 'FLOAT_COLOR', 'POINT').data.foreach_set('color', np.c_[np.repeat(kasT[:, None], 3, 1), np.ones(n)].ravel())
nmw = YUZ * (1 - np.clip(gozb * 1.5, 0, 1))   # Tripo normal haritası yalnız yüzde (göz oyuğu hariç)
me.color_attributes.new('Yuz', 'FLOAT_COLOR', 'POINT').data.foreach_set('color', np.c_[np.repeat(nmw[:, None], 3, 1), np.ones(n)].ravel())
# ---------- 5) malzeme: ten + saç (v13 düğümleri) + Tripo normal haritası yüzde ----------
nimg = next((im for im in bpy.data.images if 'normal' in im.name.lower()), None)
mt = bpy.data.materials.new('ten'); mt.use_nodes = True; nt = mt.node_tree; b = nt.nodes['Principled BSDF']; Ln = nt.links.new
at = nt.nodes.new('ShaderNodeVertexColor'); at.layer_name = 'Renk'
tn = nt.nodes.new('ShaderNodeTexNoise'); tn.inputs['Scale'].default_value = 140; tn.inputs['Detail'].default_value = 3; tr_ = nt.nodes.new('ShaderNodeMapRange'); tr_.inputs['To Min'].default_value = .92; tr_.inputs['To Max'].default_value = 1.06; Ln(tn.outputs['Fac'], tr_.inputs['Value'])
tm = nt.nodes.new('ShaderNodeMix'); tm.data_type = 'RGBA'; tm.blend_type = 'MULTIPLY'; tm.inputs['Factor'].default_value = 1; Ln(at.outputs['Color'], tm.inputs[6]); Ln(tr_.outputs[0], tm.inputs[7])
ka = nt.nodes.new('ShaderNodeVertexColor'); ka.layer_name = 'Kas'; ks = nt.nodes.new('ShaderNodeSeparateColor'); Ln(ka.outputs['Color'], ks.inputs[0])
tck = nt.nodes.new('ShaderNodeTexCoord'); km = nt.nodes.new('ShaderNodeMapping'); km.inputs['Scale'].default_value = (25, 420, 420); km.inputs['Rotation'].default_value = (0, .35, 0); Ln(tck.outputs['Object'], km.inputs['Vector'])   # kaş kılı: x boyunca uzun, hafif yukarı eğik
kn = nt.nodes.new('ShaderNodeTexNoise'); kn.inputs['Scale'].default_value = 1; kn.inputs['Detail'].default_value = 6; Ln(km.outputs['Vector'], kn.inputs['Vector'])
kr_ = nt.nodes.new('ShaderNodeMapRange'); kr_.inputs['From Min'].default_value = .35; kr_.inputs['From Max'].default_value = .65; kr_.inputs['To Min'].default_value = .45; kr_.inputs['To Max'].default_value = 1.5; Ln(kn.outputs['Fac'], kr_.inputs['Value'])
kx = nt.nodes.new('ShaderNodeMix'); kx.data_type = 'RGBA'; kx.blend_type = 'MULTIPLY'; Ln(ks.outputs[0], kx.inputs['Factor']); Ln(tm.outputs[2], kx.inputs[6]); Ln(kr_.outputs[0], kx.inputs[7]); Ln(kx.outputs[2], b.inputs['Base Color'])   # ten lekelenmesi: düz plastik görünüm gider
sa = nt.nodes.new('ShaderNodeVertexColor'); sa.layer_name = 'Sac'; sp = nt.nodes.new('ShaderNodeSeparateColor'); Ln(sa.outputs['Color'], sp.inputs[0])
mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = .60; mr.inputs['To Max'].default_value = .45; Ln(sp.outputs[0], mr.inputs['Value']); Ln(mr.outputs[0], b.inputs['Roughness'])
tc = nt.nodes.new('ShaderNodeTexCoord')
gz = nt.nodes.new('ShaderNodeTexNoise'); gz.inputs['Scale'].default_value = 900; gz.inputs['Detail'].default_value = 2; Ln(tc.outputs['Object'], gz.inputs['Vector'])
dm = nt.nodes.new('ShaderNodeMapping'); dm.inputs['Scale'].default_value = (260, 5, 5); Ln(tc.outputs['Object'], dm.inputs['Vector'])   # x boyunca sık, y/z boyunca seyrek gürültü: önden arkaya tarak izi
dv = nt.nodes.new('ShaderNodeTexNoise'); dv.inputs['Scale'].default_value = 1; dv.inputs['Detail'].default_value = 4; Ln(dm.outputs['Vector'], dv.inputs['Vector'])
mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'FLOAT'; Ln(sp.outputs[0], mx.inputs['Factor']); Ln(gz.outputs['Fac'], mx.inputs['A']); Ln(dv.outputs['Fac'], mx.inputs['B'])
mk2 = nt.nodes.new('ShaderNodeMix'); mk2.data_type = 'FLOAT'; Ln(ks.outputs[0], mk2.inputs['Factor']); Ln(mx.outputs[0], mk2.inputs['A']); Ln(kn.outputs['Fac'], mk2.inputs['B'])   # kaşta kıl kabartısı
bk = nt.nodes.new('ShaderNodeMath'); bk.operation = 'MAXIMUM'
bs = nt.nodes.new('ShaderNodeMapRange'); bs.inputs['To Min'].default_value = .04; bs.inputs['To Max'].default_value = .3; Ln(sp.outputs[0], bs.inputs['Value'])
bk.inputs[1].default_value = 0; Ln(bs.outputs[0], bk.inputs[0]); kb3 = nt.nodes.new('ShaderNodeMath'); kb3.operation = 'MULTIPLY'; kb3.inputs[1].default_value = .35; Ln(ks.outputs[0], kb3.inputs[0]); Ln(kb3.outputs[0], bk.inputs[1])
bu = nt.nodes.new('ShaderNodeBump'); bu.inputs['Distance'].default_value = .0008; Ln(mk2.outputs[0], bu.inputs['Height']); Ln(bk.outputs[0], bu.inputs['Strength'])
if nimg:
    nimg.colorspace_settings.name = 'Non-Color'
    ti = nt.nodes.new('ShaderNodeTexImage'); ti.image = nimg; nm = nt.nodes.new('ShaderNodeNormalMap'); Ln(ti.outputs['Color'], nm.inputs['Color'])
    yw = nt.nodes.new('ShaderNodeVertexColor'); yw.layer_name = 'Yuz'; ys = nt.nodes.new('ShaderNodeSeparateColor'); Ln(yw.outputs['Color'], ys.inputs[0])
    Ln(ys.outputs[0], nm.inputs['Strength']); Ln(nm.outputs['Normal'], bu.inputs['Normal'])
Ln(bu.outputs['Normal'], b.inputs['Normal'])
if 'Coat Weight' in b.inputs:
    cw = nt.nodes.new('ShaderNodeMath'); cw.operation = 'MULTIPLY'; cw.inputs[1].default_value = .06; Ln(sp.outputs[0], cw.inputs[0]); Ln(cw.outputs[0], b.inputs['Coat Weight'])
    if 'Coat Roughness' in b.inputs: b.inputs['Coat Roughness'].default_value = .25
for k in ('Subsurface Weight', 'Subsurface'):
    if k in b.inputs: b.inputs[k].default_value = .15
if 'Subsurface Radius' in b.inputs: b.inputs['Subsurface Radius'].default_value = (.004, .002, .0015)
me.materials.clear(); me.materials.append(mt)
# ---------- 6) göz küreleri (v13): göz akı kenara koyu-pembe, iris radyal + lif, bebek, kornea ----------
def malz(ad, renk, pur_=.3):
    m = bpy.data.materials.new(ad); m.use_nodes = True; bb = m.node_tree.nodes['Principled BSDF']; bb.inputs['Base Color'].default_value = (*[(c_ / 12.92 if c_ <= .04045 else ((c_ + .055) / 1.055) ** 2.4) for c_ in renk], 1); bb.inputs['Roughness'].default_value = pur_; return m
def yaricap(t_, Rk):   # nesne uzayında bakış eksenine (yerel z) uzaklık / Rk
    Ln_ = t_.links.new; tc_ = t_.nodes.new('ShaderNodeTexCoord'); sx = t_.nodes.new('ShaderNodeSeparateXYZ'); Ln_(tc_.outputs['Object'], sx.inputs[0])
    cxy = t_.nodes.new('ShaderNodeCombineXYZ'); Ln_(sx.outputs['X'], cxy.inputs['X']); Ln_(sx.outputs['Y'], cxy.inputs['Y'])
    ln = t_.nodes.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'; Ln_(cxy.outputs[0], ln.inputs[0])
    dv_ = t_.nodes.new('ShaderNodeMath'); dv_.operation = 'DIVIDE'; dv_.inputs[1].default_value = Rk; Ln_(ln.outputs['Value'], dv_.inputs[0]); return dv_, tc_
def ak_malz(Rk, ad):
    m = malz(ad, (.78, .74, .69), .3); t_ = m.node_tree; dv_, _ = yaricap(t_, Rk)
    rp = t_.nodes.new('ShaderNodeValToRGB'); E_ = rp.color_ramp.elements; E_[0].position = .5; E_[0].color = (.55, .50, .45, 1); E_[1].position = .95; E_[1].color = (.33, .21, .19, 1)
    t_.links.new(dv_.outputs[0], rp.inputs[0]); t_.links.new(rp.outputs['Color'], t_.nodes['Principled BSDF'].inputs['Base Color']); return m
def iris_malz(Rk, ad):   # portre: açık buz mavisi, koyu limbus halkası, bebek yakası gri-yeşil
    m = bpy.data.materials.new(ad); m.use_nodes = True; t_ = m.node_tree; ib = t_.nodes['Principled BSDF']; ib.inputs['Roughness'].default_value = .35; Ln_ = t_.links.new
    dv_, tc_ = yaricap(t_, Rk); rp = t_.nodes.new('ShaderNodeValToRGB'); E_ = rp.color_ramp.elements
    for k_, (po, co) in enumerate(((.12, (.16, .20, .19)), (.18, (.30, .40, .44)), (.30, (.52, .68, .80)), (.42, (.30, .42, .54)), (.48, (.03, .045, .06)))):
        e_ = E_[k_] if k_ < 2 else E_.new(po); e_.position = po; e_.color = (*co, 1)
    Ln_(dv_.outputs[0], rp.inputs[0])
    ga = t_.nodes.new('ShaderNodeTexGradient'); ga.gradient_type = 'RADIAL'; Ln_(tc_.outputs['Object'], ga.inputs['Vector'])
    ml = t_.nodes.new('ShaderNodeMath'); ml.operation = 'MULTIPLY'; ml.inputs[1].default_value = 70; Ln_(ga.outputs['Fac'], ml.inputs[0])
    cm = t_.nodes.new('ShaderNodeCombineXYZ'); Ln_(ml.outputs[0], cm.inputs['X']); m3 = t_.nodes.new('ShaderNodeMath'); m3.operation = 'MULTIPLY'; m3.inputs[1].default_value = 6; Ln_(dv_.outputs[0], m3.inputs[0]); Ln_(m3.outputs[0], cm.inputs['Y'])
    iz = t_.nodes.new('ShaderNodeTexNoise'); iz.inputs['Scale'].default_value = 1; iz.inputs['Detail'].default_value = 6; Ln_(cm.outputs[0], iz.inputs['Vector'])
    lf = t_.nodes.new('ShaderNodeMapRange'); lf.inputs['From Min'].default_value = .3; lf.inputs['From Max'].default_value = .7; lf.inputs['To Min'].default_value = .78; lf.inputs['To Max'].default_value = 1.15; Ln_(iz.outputs['Fac'], lf.inputs['Value'])
    mx_ = t_.nodes.new('ShaderNodeMix'); mx_.data_type = 'RGBA'; mx_.blend_type = 'MULTIPLY'; mx_.inputs['Factor'].default_value = 1
    Ln_(rp.outputs['Color'], mx_.inputs[6]); Ln_(lf.outputs[0], mx_.inputs[7]); Ln_(mx_.outputs[2], ib.inputs['Base Color']); return m
BB = malz('bebek', (.015, .015, .015), .2)
KO = bpy.data.materials.new('kornea'); KO.use_nodes = True; kb = KO.node_tree.nodes['Principled BSDF']; kb.inputs['Base Color'].default_value = (1, 1, 1, 1); kb.inputs['Roughness'].default_value = .0; kb.inputs['IOR'].default_value = 1.376
kb.inputs['Transmission Weight' if 'Transmission Weight' in kb.inputs else 'Transmission'].default_value = 1
for s, zc, R, ileri in GOZ:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=R, location=tuple(zc), segments=48, ring_count=32); k = bpy.context.object; k.name = 'goz' + s; k.data.materials.append(ak_malz(R, 'ak' + s))
    k.rotation_euler = Vector(ileri).to_track_quat('Z', 'Y').to_euler()
    for p in k.data.polygons: p.use_smooth = True
    for ad, rr, m, ek in (('iris', .48, iris_malz(R * 1.004, 'iris' + s), 1.004), ('bebek', .12, BB, 1.008)):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=R * ek, location=(0, 0, 0), segments=96, ring_count=96)
        x = bpy.context.object; x.name = ad + s; x.data.materials.append(m)
        bm = bmesh.new(); bm.from_mesh(x.data); cz_ = R * ek * math.cos(math.asin(rr))
        bmesh.ops.delete(bm, geom=[vv for vv in bm.verts if vv.co.z < cz_ - 1e-7], context='VERTS'); bm.to_mesh(x.data); bm.free()
        for p in x.data.polygons: p.use_smooth = True
        x.location = tuple(zc); x.rotation_euler = Vector(ileri).to_track_quat('Z', 'Y').to_euler()
    bpy.ops.mesh.primitive_uv_sphere_add(radius=R * .66, location=(0, 0, 0), segments=96, ring_count=64); x = bpy.context.object; x.name = 'kornea' + s; x.data.materials.append(KO)
    bm = bmesh.new(); bm.from_mesh(x.data); bmesh.ops.delete(bm, geom=[vv for vv in bm.verts if vv.co.z < R * .66 * .55], context='VERTS'); bm.to_mesh(x.data); bm.free()
    for p in x.data.polygons: p.use_smooth = True
    x.location = tuple(zc + ileri * (R * .42)); x.rotation_euler = Vector(ileri).to_track_quat('Z', 'Y').to_euler()
json.dump({'olc': float(olc), 'goz': [[s, list(map(float, zc)), float(R), list(map(float, ileri))] for s, zc, R, ileri in GOZ]}, open(os.path.join(W, 'renkli.json'), 'w'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(W, 'renkli.blend'))
print('GELİŞTİRİLDİ saç oranı', round(float(sacw.mean()), 3))
