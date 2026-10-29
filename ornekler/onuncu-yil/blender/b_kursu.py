# Blender: kürsü seti (29 Ekim 1933 Onuncu Yıl havası, premium) -> kursu.blend
# Ceviz kürsü (pahlı kenar, panelli ön, pirinç şerit), Türk bayrağı (bayrak.png, Tüzük oranları; kumaş dalgası), bordo kadife perde (kıvrımlı, sheen),
# 1930'lar mikrofonları (halka + yaylı karbon blok, kutu şerit mikrofon, krom ayak), karanfil yığını (kırmızı/beyaz), parke zemin, hafif hacimsel pus.
# Karakter: ata-karakter.blend (yoksa frakli.blend) bağlanır. Kişi önü -Y; ayak z=0. Kullanım: blender -b -P b_kursu.py
import bpy, bmesh, os, math, random
from mathutils import Vector, Matrix
W = os.path.dirname(os.path.abspath(__file__)); random.seed(1933)
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
def malz(ad, renk, pur=.5, met=0., **k):
    m = bpy.data.materials.new(ad); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*renk, 1); b.inputs['Roughness'].default_value = pur; b.inputs['Metallic'].default_value = met
    for a, v in k.items():
        if a in b.inputs: b.inputs[a].default_value = v
    return m
def bagla(o, m): o.data.materials.clear(); o.data.materials.append(m); return o
def kutu(ad, boy, konum, m, pah=.004, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=konum, rotation=rot); o = bpy.context.object; o.name = ad; o.scale = boy
    bpy.ops.object.transform_apply(scale=True); bv = o.modifiers.new('pah', 'BEVEL'); bv.width = pah; bv.segments = 3; bv.limit_method = 'ANGLE'
    for p in o.data.polygons: p.use_smooth = True
    o.data.shade_smooth() if hasattr(o.data, 'shade_smooth') else None
    return bagla(o, m)
def silindir(ad, r, h, konum, m, rot=(0, 0, 0), seg=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=konum, rotation=rot, vertices=seg); o = bpy.context.object; o.name = ad
    for p in o.data.polygons: p.use_smooth = True
    return bagla(o, m)
# ---------- malzemeler ----------
def ceviz():
    m = bpy.data.materials.new('ceviz'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; L = nt.links.new
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (2.5, 30, 2.5); L(tc.outputs['Object'], mp.inputs['Vector'])   # ince damar (ilk deneme iri şeritliydi)
    wv = nt.nodes.new('ShaderNodeTexWave'); wv.wave_type = 'BANDS'; wv.inputs['Scale'].default_value = 3; wv.inputs['Distortion'].default_value = 1.2; wv.inputs['Detail'].default_value = 6; L(mp.outputs['Vector'], wv.inputs['Vector'])
    rp = nt.nodes.new('ShaderNodeValToRGB'); e = rp.color_ramp.elements; e[0].color = (.07, .031, .014, 1); e[1].color = (.10, .047, .022, 1); L(wv.outputs['Fac'], rp.inputs[0]); L(rp.outputs['Color'], b.inputs['Base Color'])   # ince, düşük kontrastlı damar (dalgalı şerit yapay duruyordu)
    b.inputs['Roughness'].default_value = .32
    if 'Coat Weight' in b.inputs: b.inputs['Coat Weight'].default_value = .6; b.inputs['Coat Roughness'].default_value = .12   # cilalı ceviz
    bu = nt.nodes.new('ShaderNodeBump'); bu.inputs['Strength'].default_value = .08; L(wv.outputs['Fac'], bu.inputs['Height']); L(bu.outputs['Normal'], b.inputs['Normal'])
    return m
CEVIZ = ceviz(); PIRINC = malz('pirinc', (.78, .56, .26), .22, 1.); KROM = malz('krom', (.9, .9, .92), .12, 1.)
SIYAH = malz('siyah_bakalit', (.015, .015, .017), .28); KADIFE = malz('kadife', (.22, .012, .02), .85, **{'Sheen Weight': 1., 'Sheen Roughness': .35, 'Sheen Tint': (1, .55, .55, 1)})
KIRMIZI = malz('karanfil_k', (.55, .02, .04), .6, **{'Subsurface Weight': .25}); BEYAZ = malz('karanfil_b', (.85, .83, .78), .6, **{'Subsurface Weight': .25}); YAPRAK = malz('yaprak', (.04, .14, .04), .55)
# ---------- zemin: koyu parke ----------
bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 1, 0)); z = bpy.context.object; z.name = 'zemin'
zm = bpy.data.materials.new('parke'); zm.use_nodes = True; nt = zm.node_tree; b = nt.nodes['Principled BSDF']; L = nt.links.new
br = nt.nodes.new('ShaderNodeTexBrick'); br.inputs['Scale'].default_value = 3; br.inputs['Color1'].default_value = (.10, .045, .02, 1); br.inputs['Color2'].default_value = (.16, .075, .035, 1); br.inputs['Mortar'].default_value = (.03, .015, .008, 1); br.inputs['Mortar Size'].default_value = .004
br.inputs['Brick Width'].default_value = .9; br.inputs['Row Height'].default_value = .12; L(br.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = .38; bagla(z, zm)
# ---------- arka perde: bordo kadife, derin kıvrımlar ----------
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 2.6, 2.4), rotation=(math.pi / 2, 0, 0)); pr = bpy.context.object; pr.name = 'perde'; pr.scale = (10, 4.8, 1); bpy.ops.object.transform_apply(scale=True)
bm = bmesh.new(); bm.from_mesh(pr.data); bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=160, use_grid_fill=True); bm.to_mesh(pr.data); bm.free()
for v in pr.data.vertices:
    x, zz = v.co.x, v.co.z; v.co.y += .09 * math.sin(x * 6.3) + .035 * math.sin(x * 15.1 + 1.3) + .02 * math.sin(x * 2.1) * (zz + 2.4) / 4.8
for p in pr.data.polygons: p.use_smooth = True
bagla(pr, KADIFE)
# ---------- bayrak: Tüzük oranlı doku, kumaş dalgası ----------
G = 2.1; Lb = G * (1.5 + 1 / 30)
bpy.ops.mesh.primitive_plane_add(size=1, location=(-.15, 2.25, 2.3), rotation=(math.pi / 2, 0, 0)); by = bpy.context.object; by.name = 'bayrak'; by.scale = (Lb, G, 1); bpy.ops.object.transform_apply(scale=True)
bm = bmesh.new(); bm.from_mesh(by.data); bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=120, use_grid_fill=True); bm.to_mesh(by.data); bm.free()
for v in by.data.vertices:
    u = (v.co.x + Lb / 2) / Lb; v.co.y += (.03 + .07 * u) * math.sin(u * 8.5 + v.co.z * .7) + .018 * math.sin(u * 19 + v.co.z * 2.2)
for p in by.data.polygons: p.use_smooth = True
bym = bpy.data.materials.new('bayrak'); bym.use_nodes = True; nt = bym.node_tree; b = nt.nodes['Principled BSDF']
ti = nt.nodes.new('ShaderNodeTexImage'); ti.image = bpy.data.images.load(os.path.join(W, 'bayrak.png')); nt.links.new(ti.outputs['Color'], b.inputs['Base Color'])
b.inputs['Roughness'].default_value = .78; b.inputs['Sheen Weight'].default_value = .4 if 'Sheen Weight' in b.inputs else 0
bagla(by, bym)
silindir('gonder', .028, 4.6, (-.15 - Lb / 2 - .04, 2.25, 2.0), malz('gonder', (.85, .83, .78), .35))
bpy.ops.mesh.primitive_uv_sphere_add(radius=.07, location=(-.15 - Lb / 2 - .04, 2.25, 4.33)); bagla(bpy.context.object, PIRINC)
# ---------- ceviz kürsü (kişinin önünde) ----------
K = (0, -.46, 0)   # kürsü tabanı merkezi (arka kenar y -.22: eller kâğıtla kürsünün hemen üstünde)
kutu('kursu_govde', (.86, .48, 1.04), (K[0], K[1], .52), CEVIZ, .012)
kutu('kursu_taban', (.96, .58, .07), (K[0], K[1], .035), CEVIZ, .01)
ust = kutu('kursu_ust', (.96, .62, .045), (K[0], K[1] + .02, 1.075), CEVIZ, .008, rot=(math.radians(-9), 0, 0))
for i, x in enumerate((-.27, 0, .27)):   # ön paneller (çıkıntılı çerçeve)
    kutu(f'panel{i}', (.22, .02, .72), (K[0] + x, K[1] - .245, .56), CEVIZ, .006)
    kutu(f'panel_ic{i}', (.17, .012, .64), (K[0] + x, K[1] - .257, .56), CEVIZ, .004)
kutu('pirinc_serit', (.94, .012, .014), (K[0], K[1] - .30, 1.03), PIRINC, .003)
kutu('pirinc_etek', (.98, .012, .014), (K[0], K[1] - .295, .075), PIRINC, .003)
# ---------- mikrofon ayağı (Atatürk'ün sağ önü, ekran solu) ----------
M0 = Vector((-.50, -.70, 0))
silindir('mik_taban', .17, .035, M0 + Vector((0, 0, .018)), KROM); silindir('mik_direk', .014, 1.40, M0 + Vector((0, 0, .72)), KROM)
kutu('mik_kol', (.46, .02, .02), M0 + Vector((.05, 0, 1.42)), KROM, .004)
# halka içinde yaylı karbon blok mikrofon
hm = M0 + Vector((.05, -.02, 1.56))
bpy.ops.mesh.primitive_torus_add(major_radius=.115, minor_radius=.011, location=hm, rotation=(math.pi / 2, 0, 0)); bagla(bpy.context.object, KROM)
kutu('karbon_blok', (.11, .06, .11), hm, malz('bakalit_koyu', (.03, .028, .03), .3), .012)
silindir('karbon_izgara', .042, .062, hm + Vector((0, -.001, 0)), malz('izgara', (.6, .6, .62), .35, .9), rot=(math.pi / 2, 0, 0))
for k in range(8):   # yaylar
    a = k * math.pi / 4; p0 = hm + Vector((math.cos(a) * .06, 0, math.sin(a) * .06)); p1 = hm + Vector((math.cos(a) * .108, 0, math.sin(a) * .108))
    c = (p0 + p1) / 2; d = p1 - p0
    bpy.ops.mesh.primitive_cylinder_add(radius=.004, depth=d.length, location=c, vertices=8); s = bpy.context.object; s.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); bagla(s, KROM)
silindir('halka_sap', .009, .07, hm + Vector((0, 0, -.15)), KROM)
# kutu şerit mikrofon (sağda)
sm = M0 + Vector((.26, -.01, 1.50)); kutu('serit_mik', (.07, .05, .16), sm, SIYAH, .015); kutu('serit_izgara', (.074, .052, .12), sm + Vector((0, -.001, 0)), malz('izgara2', (.5, .5, .52), .4, .9), .01)
silindir('serit_sap', .008, .06, sm + Vector((0, 0, -.1)), KROM)
# karanfil yığını kaldırıldı (ön planda ucuz top yığını gibi görünüyordu)
# ---------- karakter: b_sahne.py ekler (ata-govde.blend + renkli baş) ----------
# ---------- ışık + dünya (hafif hacimsel pus) ----------
w = bpy.data.worlds.new('dunya'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (.012, .008, .008, 1); w.node_tree.nodes['Background'].inputs[1].default_value = .4
vol = w.node_tree.nodes.new('ShaderNodeVolumePrincipled'); vol.inputs['Density'].default_value = .0025; vol.inputs['Color'].default_value = (1, .92, .85, 1)   # .012 sütlü pus yapıyordu
w.node_tree.links.new(vol.outputs['Volume'], w.node_tree.nodes['World Output'].inputs['Volume'])
def isik(ad, tip, konum, hedef, enerji, renk, boy=1.):
    L_ = bpy.data.lights.new(ad, tip); L_.energy = enerji; L_.color = renk
    if tip == 'AREA': L_.size = boy
    if tip == 'SPOT': L_.spot_size = math.radians(38); L_.spot_blend = .6; L_.shadow_soft_size = .15
    o = bpy.data.objects.new(ad, L_); o.location = konum; o.rotation_euler = (Vector(hedef) - Vector(konum)).to_track_quat('-Z', 'Y').to_euler(); sc.collection.objects.link(o); return o
isik('ana', 'AREA', (-1.6, -2.4, 3.0), (0, 0, 1.55), 170, (1, .86, .72), 1.6)        # sıcak ana ışık (sol üst önden, Rembrandt)
isik('dolgu', 'AREA', (2.2, -2.0, 1.7), (0, 0, 1.5), 14, (.75, .82, 1), 2.0)          # soğuk zayıf dolgu
isik('kenar', 'AREA', (1.3, 1.6, 2.6), (0, 0, 1.6), 160, (.85, .9, 1), .8)            # kenar ışığı (omuz/saç)
isik('pencere', 'SPOT', (-3.5, 1.0, 5.0), (0, .3, 1.2), 900, (1, .9, .78))            # pencereden huzme (pus içinde ışın)
isik('bayrak_isik', 'AREA', (0, .6, 3.6), (0, 2.25, 2.3), 55, (1, .9, .85), 2.5)
# ---------- kamera + render ----------
cd = bpy.data.cameras.new('kam'); cd.lens = 50; cd.dof.use_dof = True; cd.dof.aperture_fstop = 2.8
kam = bpy.data.objects.new('kam', cd); sc.collection.objects.link(kam); sc.camera = kam
kam.location = (.55, -3.1, 1.55); kam.rotation_euler = (Vector((0, -.2, 1.42)) - kam.location).to_track_quat('-Z', 'Y').to_euler()
cd.dof.focus_distance = (kam.location - Vector((0, 0, 1.55))).length
sc.render.engine = 'CYCLES'; sc.cycles.samples = 128; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920; sc.view_settings.view_transform = 'AgX'
try: sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
pr_ = bpy.context.preferences.addons['cycles'].preferences
for t in ('OPTIX', 'CUDA'):
    try: pr_.compute_device_type = t; pr_.get_devices(); [setattr(d, 'use', True) for d in pr_.devices]; sc.cycles.device = 'GPU'; break
    except Exception: pass
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(W, 'kursu.blend')); print('KÜRSÜ kaydedildi')
