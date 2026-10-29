# Blender: TERS NAKİL — Tripo yüzüne dokunulmaz; Tripo'nun düz tepe/arka/yan kısmı Hunyuan kafatası+saçına (hy-is.blend) çekilir. -> nakil2.blend
# (ilk sürüm t_nakil.py Tripo yüzünü Hunyuan ağına basıyordu: seyrek ağ kaş/göz ayrıntısını bozdu)
# Nokta eşlemeyle (MediaPipe 478) benzerlik hizası, yüz ovali içinde Hunyuan köşeleri
# Tripo yüzeyine (en yakın nokta) çekilir, ovalin kenarında yumuşak geçiş; kafatası, saç, kulak Hunyuan'da kalır. -> nakil.blend
# Kullanım: blender -b -P t_nakil.py
import bpy, os, json, numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
W = os.path.dirname(os.path.abspath(__file__)); H_ = os.path.dirname(W)
bpy.ops.wm.open_mainfile(filepath=os.path.join(H_, 'hy-is.blend'))
h = [x for x in bpy.data.objects if x.type == 'MESH'][0]; h.name = 'bas'
with bpy.data.libraries.load(os.path.join(W, 'tp.blend')) as (src, dst): dst.objects = ['tripo']
t = dst.objects[0]; bpy.context.scene.collection.objects.link(t)
dg = bpy.context.evaluated_depsgraph_get()
def noktalar3(o, js):
    b = BVHTree.FromObject(o, dg); M = o.matrix_world; Mi = M.inverted(); R = {}
    for i, (x, z) in enumerate(json.load(open(js))):
        p = b.ray_cast(Mi @ Vector((x, -9, z)), (Mi.to_3x3() @ Vector((0, 1, 0))).normalized(), 50)[0]
        if p: R[i] = np.array(M @ p)
    return R
LH = noktalar3(h, os.path.join(H_, 'hy-noktalar.json')); LT = noktalar3(t, os.path.join(W, 'tp-noktalar.json'))
DUDAK_GOZ = set([0, 13, 14, 17, 37, 39, 40, 61, 78, 80, 81, 82, 84, 87, 88, 91, 95, 146, 178, 181, 185, 191, 267, 269, 270, 291, 308, 310, 311, 312, 314, 317, 318, 321, 324, 375, 402, 405, 409, 415] + list(range(468, 478)) + [7, 33, 133, 144, 145, 153, 154, 155, 157, 158, 159, 160, 161, 163, 173, 246, 249, 263, 362, 373, 374, 380, 381, 382, 384, 385, 386, 387, 388, 390, 398, 466])
ix = [i for i in LH if i in LT and i not in DUDAK_GOZ]
def umeyama(X, Y):   # Y ~ s R X + t
    mx, my = X.mean(0), Y.mean(0); Xc, Yc = X - mx, Y - my; U, S, Vt = np.linalg.svd(Yc.T @ Xc / len(X)); D = np.eye(3)
    if np.linalg.det(U @ Vt) < 0: D[2, 2] = -1
    R = U @ D @ Vt; s = np.trace(np.diag(S) @ D) / (Xc ** 2).sum(1).mean(); return s, R, my - s * R @ mx
for tur in range(3):   # en kötü %20'yi at, yeniden hizala
    X = np.array([LT[i] for i in ix]); Y = np.array([LH[i] for i in ix]); s, R, tt = umeyama(X, Y)
    e = np.linalg.norm((s * (R @ X.T)).T + tt - Y, axis=1)
    if tur < 2: ix = [ix[k] for k in np.argsort(e)[:int(len(ix) * .8)]]
fw = np.linalg.norm(LH[234] - LH[454]); print('HİZA ölçek', round(s, 4), 'artık ort', round(e.mean() / fw * 100, 2), '% yüz genişliği, nokta', len(ix))
T = Matrix.Identity(4)
for a in range(3):
    for b_ in range(3): T[a][b_] = s * R[a, b_]
    T[a][3] = tt[a]
t.matrix_world = T @ t.matrix_world; bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get(); bh = BVHTree.FromObject(h, dg); Mh_ = h.matrix_world; Mhi_ = Mh_.inverted()
me = t.data; n = len(me.vertices); A = np.zeros(n * 3); me.vertices.foreach_get('co', A); A = A.reshape(-1, 3)
Mt = np.array(t.matrix_world); Aw = A @ Mt[:3, :3].T + Mt[:3, 3]
L3 = {i: s * R @ LT[i] + tt for i in LT}; L3 = {**{i: LH[i] for i in LH if i not in L3}, **L3}   # ışını kaçan Tripo noktası -> hizalı Hunyuan noktası
OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
P2 = np.array([[L3[i][0], L3[i][2]] for i in OVAL]); Q = Aw[:, [0, 2]]
ic = np.zeros(len(Q), bool)
for k in range(len(P2)):
    a, b_ = P2[k], P2[(k + 1) % len(P2)]; c1 = (a[1] > Q[:, 1]) != (b_[1] > Q[:, 1])
    xk = a[0] + (Q[:, 1] - a[1]) * (b_[0] - a[0]) / (b_[1] - a[1] + 1e-12); ic ^= c1 & (Q[:, 0] < xk)
dmin = np.full(n, 1e9)
for k in range(len(P2)):
    a, b_ = P2[k], P2[(k + 1) % len(P2)]; v = b_ - a; u = np.clip(((Q - a) @ v) / (v @ v), 0, 1); dmin = np.minimum(dmin, np.linalg.norm(Q - (a + u[:, None] * v), axis=1))
fw = np.linalg.norm(L3[234] - L3[454]); sd = np.where(ic, dmin, -dmin)
ss = lambda x: np.clip(x, 0, 1) ** 2 * (3 - 2 * np.clip(x, 0, 1))
yk = (L3[234][1] + L3[454][1]) / 2
fth = .08 * fw + .20 * fw * ss((Aw[:, 2] - L3[105][2]) / (.25 * fw))   # alında geniş geçiş: Tripo alnı ile Hunyuan tepesi birleşmiyordu (profilde çıkıntı)
yuz = ss((sd + .02 * fw) / fth) * ss((yk - Aw[:, 1]) / (.05 * fw))   # yüz = 1 (dokunulmaz)
xm0 = np.mean([L3[i][0] for i in (6, 168, 1)]); gz_ = (L3[33][2] + L3[263][2]) / 2
yuz *= 1 - ss((np.abs(Aw[:, 0] - xm0) - .36 * fw) / (.08 * fw)) * ss((Aw[:, 2] - gz_ + .05 * fw) / (.12 * fw))   # şakak (göz hizası üstü, yan) Hunyuan'a: Tripo'nun tıraş çizgileri profilde görünüyordu
z0 = L3[2][2]   # burun altı hizası: altı (ense kutusu, yaka) Tripo'da kalır — çene hizası ensede saçak yapıyordu
w = (1 - yuz) * ss((Aw[:, 2] - z0) / (.15 * fw))
# kulak koruması: ince kabuk (normalin tersine kısa ışın karşı yüze çarpar) + yan + kulak yüksekliği; komşulukla genişlet/yumuşat
bl = BVHTree.FromObject(t, dg); Nl = np.zeros(n * 3); me.vertices.foreach_get('normal', Nl); Nl = Nl.reshape(-1, 3)
Mt3i = np.linalg.inv(Mt[:3, :3]); kal = .06 * fw / s   # yerel birimde kalınlık eşiği
mx = (L3[234][0] + L3[454][0]) / 2; aday = (np.abs(Aw[:, 0] - mx) > .30 * fw) & (Aw[:, 2] > z0 - .1 * fw) & (Aw[:, 2] < L3[105][2]) & (Aw[:, 1] > yk - .15 * fw)
ince = np.zeros(n)
for i in np.nonzero(aday)[0]:
    h_ = bl.ray_cast(Vector(A[i] - Nl[i] * 1e-4), Vector(-Nl[i]), kal)
    if h_[0] is not None: ince[i] = 1
Ek = np.zeros(len(me.edges) * 2, dtype=np.int64); me.edges.foreach_get('vertices', Ek); Ek = Ek.reshape(-1, 2)
for _ in range(12):   # genişlet
    m_ = ince.copy(); np.maximum.at(m_, Ek[:, 0], ince[Ek[:, 1]]); np.maximum.at(m_, Ek[:, 1], ince[Ek[:, 0]]); ince = m_
for _ in range(10):   # yumuşat
    sm = np.zeros(n); c_ = np.zeros(n); np.add.at(sm, Ek[:, 0], ince[Ek[:, 1]]); np.add.at(sm, Ek[:, 1], ince[Ek[:, 0]]); np.add.at(c_, Ek.ravel(), 1); ince = .5 * ince + .5 * sm / np.maximum(c_, 1)
print('KULAK köşe', int((ince > .5).sum()))
w *= 1 - ince
mk = (L3[234] + L3[454]) / 2; mk[1] += .10 * fw; mk[2] += .05 * fw
xm = np.mean([L3[i][0] for i in (6, 168, 1)]); mk[0] = xm
def isin(q):   # kafa ortasından q yönünde DIŞTAN içeri ilk Hunyuan çarpması
    dv = q - mk; dv /= np.linalg.norm(dv); p = bh.ray_cast(Mhi_ @ Vector(mk + dv * 3 * fw), (Mhi_.to_3x3() @ Vector(-dv)).normalized(), 50)[0]
    return None if p is None else np.array(Mh_ @ p)
# ham Hunyuan'ın +x şakağında saç topağı var (v3 dersi) -> +x yarı, -x yarının aynasından alınır; orta hatta .1fw geçiş
ay = ss((Aw[:, 0] - xm) / (.1 * fw))
# dolgunluk: yönetmen ilk nakli (Hunyuan hacmi) daha mantıklı buldu -> yanak/çene yanlarında Hunyuan'a doğru düşük frekanslı kayma; burun/göz/kaş/ağız (orta) Tripo keskinliğinde
wF = yuz * ss((np.abs(Aw[:, 0] - xm) - .14 * fw) / (.22 * fw)) * ss((L3[105][2] - Aw[:, 2]) / (.10 * fw))
hedef = Aw.copy(); kac = 0
for i in np.nonzero((w > 1e-4) | (wF > 1e-4))[0]:
    p = isin(Aw[i])
    if ay[i] > 0:
        q = Aw[i].copy(); q[0] = 2 * xm - q[0]; pm = isin(q)
        if pm is not None:
            pm[0] = 2 * xm - pm[0]; p = pm if p is None else p * (1 - ay[i]) + pm * ay[i]
    if p is None: w[i] = 0; kac += 1; continue
    hedef[i] = p
uz = np.linalg.norm(hedef - Aw, axis=1)
print('TERS NAKİL köşe', int((w > .5).sum()), 'ort uzaklık', round(float(uz[w > .5].mean() / fw * 100), 2), '% fw, ışınsız', kac)
Yw = Aw + w[:, None] * (hedef - Aw)
_, kim = np.unique(np.round(Aw * 1e6).astype(np.int64), axis=0, return_inverse=True); kim = kim.ravel(); m_ = kim.max() + 1   # UV dikişi çift köşelerini kaynak: komşuluk kesintisiz
Ku = np.unique(np.sort(kim[Ek], 1), axis=0); Ku = Ku[Ku[:, 0] != Ku[:, 1]]; ki_ = np.r_[Ku[:, 0], Ku[:, 1]]; kj_ = np.r_[Ku[:, 1], Ku[:, 0]]; dg_ = np.bincount(ki_, minlength=m_).astype(float)
def ort_(X): return np.stack([np.bincount(ki_, weights=X[kj_, k], minlength=m_) for k in range(X.shape[1])], 1) / np.maximum(dg_, 1)[:, None]
def tek(x): r_ = np.zeros((m_,) + x.shape[1:]); np.add.at(r_, kim, x); c_ = np.bincount(kim, minlength=m_).astype(float); return r_ / c_.reshape((-1,) + (1,) * (x.ndim - 1))
D = np.where((wF > 1e-4)[:, None], hedef - Aw, 0.); Du = tek(D)
for _ in range(80): Du = ort_(Du)   # düşük geçiren: Hunyuan'ın ayrıntısı değil yalnız hacmi
Yw += (1.0 * wF)[:, None] * Du[kim]
print('DOLGUNLUK köşe', int((wF > .5).sum()), 'ort kayma', round(float(np.linalg.norm(Du[kim][wF > .5], axis=1).mean() / fw * 100), 2), '% fw')
bant = tek(4 * w * (1 - w) * ss((Aw[:, 2] - L3[105][2]) / (.15 * fw)))   # alın-saç birleşim bandı yumuşar
Yu = tek(Yw)
for _ in range(25): Yu += (ort_(Yu) - Yu) * (.5 * np.clip(bant * 1.5, 0, 1))[:, None]
Yw = Yu[kim]
# yanal dolgunluk (ölçüm: ilk nakil elmacık +%10, ağız +%7, çene +%19 -> yönetmen "bir tık dolgun": ~2/3'ü); orta hat (burun/göz/ağız ortası) sabit
zk = [L3[152][2] - .30 * fw, L3[152][2], (L3[61][2] + L3[152][2]) / 2, L3[61][2], L3[205][2], L3[105][2]]; kk = [.04, .10, .12, .05, .065, 0]
def genis(P, ag=None):
    dx = P[:, 0] - xm; f = ss((np.abs(dx) - .08 * fw) / (.25 * fw)); k = np.interp(P[:, 2], zk, kk) * (1 if ag is None else ag)
    P = P.copy(); P[:, 0] = xm + dx * (1 + k * f); return P
Yw = genis(Yw, 1 - .7 * w)   # Hunyuan'a çekilen kafatası daha az
L3 = {i: genis(np.array([L3[i]]))[0] for i in L3}
Mti = np.linalg.inv(Mt); me.vertices.foreach_set('co', (Yw @ Mti[:3, :3].T + Mti[:3, 3]).ravel()); me.update()
for ad, val in (('nakil', w), ('yuz', yuz), ('kulak', ince)):
    ag = me.attributes.get(ad) or me.attributes.new(ad, 'FLOAT', 'POINT'); ag.data.foreach_set('value', val.astype(np.float32))
json.dump({str(i): list(map(float, L3[i])) for i in L3}, open(os.path.join(W, 'nakil2-noktalar3.json'), 'w'))
bpy.data.objects.remove(h); t.name = 'bas'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(W, 'nakil2.blend'))
