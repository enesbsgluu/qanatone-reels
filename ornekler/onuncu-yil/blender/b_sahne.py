# Blender: kursu.blend (set) + ata-govde.blend (Hunyuan kürsü gövdesi, bölge sınıflı) + renkli.blend (Tripo yüzlü baş + gözler) -> sahne.blend
# Gövde malzemeleri 'bolge' özniteliğinden (yüz başına çoğunluk): 0 siyah yün, 1 beyaz (gömlek/papyon/yaka/manşet), 2 ten, 3 kâğıt.
# Baş: ölçek .5418 (renkli birimi -> metre; çene-tepe 22,5 cm), çene z 1,515; çenenin 4,5 cm altı kesilir (boyun ucu yakanın içinde).
# Baş + gözler 'bas_pivot' boşluğuna bağlı (boyun dibi): baş eğme/çevirme animasyonu. Kullanım: blender -b -P b_sahne.py
import bpy, bmesh, os, json, math, numpy as np
from mathutils import Vector, Matrix
W = os.path.dirname(os.path.abspath(__file__)); T = os.path.join(W, '..', 'heykel', 'tripo')
bpy.ops.wm.open_mainfile(filepath=os.path.join(W, 'kursu.blend')); sc = bpy.context.scene
# ---------- gövde ----------
with bpy.data.libraries.load(os.path.join(W, 'ata-govde.blend')) as (src, dst): dst.objects = ['govde']
gv = dst.objects[0]; sc.collection.objects.link(gv)
def malz(ad, renk, pur, **k):
    m = bpy.data.materials.new(ad); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*renk, 1); b.inputs['Roughness'].default_value = pur
    for a, v in k.items():
        if a in b.inputs: b.inputs[a].default_value = v
    return m
YUN = malz('yun', (.008, .008, .010), .6, **{'Sheen Weight': .22, 'Sheen Roughness': .45})   # parlaklık .6 frakı gri gösteriyordu
nt = YUN.node_tree; b = nt.nodes['Principled BSDF']; tc = nt.nodes.new('ShaderNodeTexCoord'); nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 2500; nz.inputs['Detail'].default_value = 2
nt.links.new(tc.outputs['Object'], nz.inputs['Vector']); bu = nt.nodes.new('ShaderNodeBump'); bu.inputs['Strength'].default_value = .12; nt.links.new(nz.outputs['Fac'], bu.inputs['Height']); nt.links.new(bu.outputs['Normal'], b.inputs['Normal'])   # yün dokusu
BEYAZ = malz('gomlek', (.80, .79, .76), .42, **{'Sheen Weight': .25})
TEN = malz('el_ten', (.62, .40, .31), .5, **{'Subsurface Weight': .2, 'Subsurface Radius': (.004, .002, .0015)})
KAGIT = malz('kagit', (.86, .82, .73), .85)
me = gv.data; me.materials.clear()
# tek malzeme: yün tabanı, BolgeW (beyaz, ten, kâğıt) ağırlıklarıyla yumuşak geçiş (yüz başına malzeme basamaklı kenar yapıyordu)
GM = YUN.copy(); GM.name = 'govde_malz'; nt = GM.node_tree; b = nt.nodes['Principled BSDF']; Ln = nt.links.new
va = nt.nodes.new('ShaderNodeVertexColor'); va.layer_name = 'BolgeW'; sp = nt.nodes.new('ShaderNodeSeparateColor'); Ln(va.outputs['Color'], sp.inputs[0])
def karis(onceki, renk, agirlik_cikisi, tip='RGBA'):
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = tip; Ln(agirlik_cikisi, mx.inputs['Factor'])
    if tip == 'RGBA':
        if isinstance(onceki, tuple): mx.inputs[6].default_value = onceki
        else: Ln(onceki, mx.inputs[6])
        mx.inputs[7].default_value = renk; return mx.outputs[2]
    if isinstance(onceki, float): mx.inputs[2].default_value = onceki
    else: Ln(onceki, mx.inputs[2])
    mx.inputs[3].default_value = renk; return mx.outputs[0]
c_ = karis((.008, .008, .010, 1), (.80, .79, .76, 1), sp.outputs[0]); c_ = karis(c_, (.62, .40, .31, 1), sp.outputs[1]); c_ = karis(c_, (.86, .82, .73, 1), sp.outputs[2]); Ln(c_, b.inputs['Base Color'])
r_ = karis(.6, .42, sp.outputs[0], 'FLOAT'); r_ = karis(r_, .5, sp.outputs[1], 'FLOAT'); r_ = karis(r_, .85, sp.outputs[2], 'FLOAT'); Ln(r_, b.inputs['Roughness'])
sh = karis(.22, .0, sp.outputs[1], 'FLOAT'); sh = karis(sh, .0, sp.outputs[2], 'FLOAT'); Ln(sh, b.inputs['Sheen Weight'])
ss_ = karis(.0, .2, sp.outputs[1], 'FLOAT'); Ln(ss_, b.inputs['Subsurface Weight'])
me.materials.append(GM)
n = len(me.vertices)
for p in me.polygons: p.use_smooth = True
# ---------- baş ----------
names = ['bas'] + [n_ for n_ in ('gozR', 'gozL', 'irisR', 'irisL', 'bebekR', 'bebekL', 'korneaR', 'korneaL')]
with bpy.data.libraries.load(os.path.join(T, 'renkli.blend')) as (src, dst): dst.objects = [n_ for n_ in names if n_ in src.objects]
basP = [o for o in dst.objects if o]; [sc.collection.objects.link(o) for o in basP]; bas = [o for o in basP if o.name.startswith('bas')][0]
bpy.context.view_layer.update()   # yeni eklenen nesnenin matrix_world'ü güncellenmeden birim döner (gözler aynı noktaya düşüyordu)
Lm = {int(k): np.array(v) for k, v in json.load(open(os.path.join(T, 'nakil2-noktalar3.json'))).items()}
S = .5418; cene = Lm[152]
# boyun hizası: gövdenin yaka ağzı merkezi
A = np.zeros(n * 3); me.vertices.foreach_get('co', A); A = A.reshape(-1, 3); yk = A[(A[:, 2] > 1.44) & (np.abs(A[:, 0]) < .1)]; bx, by = float(yk[:, 0].mean()), float(yk[:, 1].mean())
Ab = np.array([v.co[:] for v in bas.data.vertices]); bo = Ab[(Ab[:, 2] < cene[2] - .08) & (Ab[:, 2] > cene[2] - .12) & (np.abs(Ab[:, 0] - cene[0]) < .12)]
nx, ny = float(np.mean([Lm[i][0] for i in (168, 6, 1, 152)])), bo[:, 1].mean()   # x yüz orta hattından (yaka bölgesi asimetrik: baş 4 cm kayıyordu)
M = Matrix.Translation(Vector((bx, by + .006, 1.472))) @ Matrix.Scale(S, 4) @ Matrix.Translation(Vector((-nx, -ny, -cene[2])))   # çene yakanın hemen üstünde (1,515: uzun boyun + dikiş görünüyordu)
for o in basP: o.matrix_world = M @ o.matrix_world
bpy.context.view_layer.update()
bm = bmesh.new(); bm.from_mesh(bas.data); Mw = bas.matrix_world
Rk = np.zeros(len(bas.data.vertices) * 4); bas.data.color_attributes['Renk'].data.foreach_get('color', Rk); Rk = Rk.reshape(-1, 4)[:, :3]
beyaz_ = Rk.min(1) > .55   # Tripo kanat yakası (köşe rengi beyaz): gövdenin kendi yakası var -> silinir
bm.verts.ensure_lookup_table()
cy_w = (M @ Vector(cene)).y   # çene ucunun dünya y'si
def alt_(p): return p.z < 1.457 + max(0., p.y - cy_w) * (.023 / .11)   # eğim az: .055 çene köşesini kesiyordu (yandan keskin çizgi)   # çene altı (önde 1,475) -> ense (11 cm geride 1,53) eğik düzlem: yakadan çıkan temiz boyun hattı
sil = [v for v in bm.verts if alt_(Mw @ v.co) or (beyaz_[v.index] and (Mw @ v.co).z < 1.53)]
ten_ = Rk[~beyaz_ & (np.array([(Mw @ v.co).z for v in bm.verts]) < 1.472) & (np.array([(Mw @ v.co).z for v in bm.verts]) > 1.447)].mean(0)
bmesh.ops.delete(bm, geom=sil, context='VERTS')
sinir = [e for e in bm.edges if e.is_boundary]; hf = bmesh.ops.holes_fill(bm, edges=sinir, sides=4000); bmesh.ops.triangulate(bm, faces=hf['faces'])   # baş altı kapağı: yakın planda açık kabuk kenarı/iç yüzey görünüyordu
bm.to_mesh(bas.data); bm.free(); print('BAŞ altı silinen', len(sil), 'boyun teni', ten_.round(3), 'kapak yüz', len(hf['faces']))
# boyun silindiri: gövdenin yaka ağzını doldurur (kara boşluk görünüyordu), başın içine 3 cm girer
bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=1, vertices=48, location=(bx, by + .006, 1.44)); bo_ = bpy.context.object; bo_.name = 'boyun'
bo_.scale = (.059, .063, .17); bpy.ops.object.transform_apply(scale=True)   # 1,37 -> 1,54: yakanın içinden başın içine
for p in bo_.data.polygons: p.use_smooth = True
bm_ = malz('boyun_ten', tuple(ten_), .5, **{'Subsurface Weight': .15}); bo_.data.materials.append(bm_)
pv = bpy.data.objects.new('bas_pivot', None); pv.location = (bx, by, 1.47); sc.collection.objects.link(pv); bpy.context.view_layer.update()   # pivot matrisi güncel olmalı (yoksa baş 1,47 m yukarı kayıyordu)
# yaka: gövdenin boyun çevresindeki yırtık iç yaka parçaları silinir, yerine boyna oturan düz beyaz gömlek yakası bandı (1,405 -> 1,474)
bmg = bmesh.new(); bmg.from_mesh(gv.data)
yk_sil = [v for v in bmg.verts if v.co.z > 1.43 and math.hypot(v.co.x - bx, (v.co.y - by) * .93) < .097]
bmesh.ops.delete(bmg, geom=yk_sil, context='VERTS'); bmg.to_mesh(gv.data); bmg.free(); print('İÇ YAKA silinen', len(yk_sil))
bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=1, vertices=64, end_fill_type='NOTHING', location=(bx, by + .006, 1.4395)); yb = bpy.context.object; yb.name = 'gomlek_yaka'
yb.scale = (.066, .070, .069); bpy.ops.object.transform_apply(scale=True)
sl_ = yb.modifiers.new('k', 'SOLIDIFY'); sl_.thickness = .003; sl_.offset = 1; ss_ = yb.modifiers.new('ss', 'SUBSURF'); ss_.levels = 1; ss_.render_levels = 2
for p in yb.data.polygons: p.use_smooth = True
yb.data.materials.append(BEYAZ)
basP.append(bpy.data.objects['boyun'])
for o in basP: mw = o.matrix_world.copy(); o.parent = pv; o.matrix_parent_inverse = pv.matrix_world.inverted(); o.matrix_world = mw
for m_ in bas.data.materials:   # Tripo normal haritası dikişleri yanakta yatay çizgi yapıyordu -> etkisi .3
    for nd in (m_.node_tree.nodes if m_ and m_.use_nodes else []):
        if nd.type == 'NORMAL_MAP':
            for l in list(nd.inputs['Strength'].links): m_.node_tree.links.remove(l)
            nd.inputs['Strength'].default_value = 0.   # yan ışıkta yanakta leke/çizgi yapıyordu
print('BAŞ yerleşti: yaka merkezi', round(bx, 3), round(by, 3), 'boyun merkezi (baş birimi)', round(nx, 3), round(ny, 3))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(W, 'sahne.blend')); print('SAHNE kaydedildi')
