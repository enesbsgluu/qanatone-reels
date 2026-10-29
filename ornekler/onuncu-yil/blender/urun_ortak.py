# Ürün sahneleri ortak araçları (exec ile yüklenir): kesitten gövde (loft), kanat/kuyruk, malzemeler, yazı/bayrak etiketi, HDRI dünya, EEVEE ayarı.
# Eksen: uçaklarda yerel +X burun yönü, +Z yukarı, +Y sol kanat. Ölçü metre.
import bpy, bmesh, os, math
from mathutils import Vector, Matrix, Euler
UW = os.path.dirname(os.path.abspath(__file__)); FONT = os.path.join(os.environ.get('QANAT_YAZITIPI', os.path.join(UW, '..', 'yazitipi')), 'Inter_700Bold.ttf')
def sifirla():
    bpy.ops.wm.read_factory_settings(use_empty=True); return bpy.context.scene
def malz(ad, renk, pur=.5, met=0., **k):
    m = bpy.data.materials.new(ad); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*renk, 1) if len(renk) == 3 else renk; b.inputs['Roughness'].default_value = pur; b.inputs['Metallic'].default_value = met
    for a, v in k.items():
        if a in b.inputs: b.inputs[a].default_value = v
    return m
def boya(ad, renk, pur=.38, kaplama=.5, panel=.06):   # askeri/otomotiv boya: hafif pürüz gürültüsü + vernik
    m = malz(ad, renk, pur, **{'Coat Weight': kaplama, 'Coat Roughness': .08}); nt = m.node_tree; b = nt.nodes['Principled BSDF']; L = nt.links.new
    tc = nt.nodes.new('ShaderNodeTexCoord'); nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3; nz.inputs['Detail'].default_value = 8; L(tc.outputs['Object'], nz.inputs['Vector'])
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = pur - panel; mr.inputs['To Max'].default_value = pur + panel; L(nz.outputs['Fac'], mr.inputs['Value']); L(mr.outputs[0], b.inputs['Roughness'])
    return m
def bagla(o, m):
    if m is not None: o.data.materials.clear(); o.data.materials.append(m)
    return o
def nesne(ad, me, ebeveyn=None):
    o = bpy.data.objects.new(ad, me); bpy.context.scene.collection.objects.link(o)
    if ebeveyn: o.parent = ebeveyn
    return o
def yumusat(o, sev=2, pah=0.):
    if pah: bv = o.modifiers.new('pah', 'BEVEL'); bv.width = pah; bv.segments = 2; bv.limit_method = 'ANGLE'
    s = o.modifiers.new('ss', 'SUBSURF'); s.levels = min(sev, 2); s.render_levels = sev
    for p in o.data.polygons: p.use_smooth = True
    return o
def kesit(w, h, n=32, us=2.5, alt=2.5, ust_oran=.55, kose=0.):
    # üstü/altı ayrı üslü süperelips; kose>0 yanlarda keskin sırt (chine) için noktaları yana çeker
    P = []
    for i in range(n):
        t = 2 * math.pi * i / n; c, s = math.cos(t), math.sin(t); e = us if s >= 0 else alt
        y = (w / 2) * math.copysign(abs(c) ** (2 / e), c); hz = h * (ust_oran if s >= 0 else 1 - ust_oran)
        z = hz * math.copysign(abs(s) ** (2 / e), s)
        if kose: y *= 1 + kose * (1 - abs(s)) ** 6
        P.append((y, z))
    return P
def loft(ad, istasyonlar, n=32, kapak=True):
    # istasyonlar: [(x, w, h, zc, dict(kesit parametreleri))] -> halkalar birleşir (yerel +X boyunca)
    bm = bmesh.new(); halkalar = []
    for x, w, h, zc, kp in istasyonlar:
        if w < 1e-3: halkalar.append([bm.verts.new((x, 0, zc))]); continue
        halkalar.append([bm.verts.new((x, y, zc + z)) for y, z in kesit(w, h, n, **kp)])
    for a, b in zip(halkalar, halkalar[1:]):
        if len(a) == 1: [bm.faces.new((a[0], b[(i + 1) % n], b[i])) for i in range(n)]
        elif len(b) == 1: [bm.faces.new((a[i], a[(i + 1) % n], b[0])) for i in range(n)]
        else: [bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i])) for i in range(n)]
    if kapak and len(halkalar[-1]) > 1: bm.faces.new(halkalar[-1][::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); me = bpy.data.meshes.new(ad); bm.to_mesh(me); bm.free(); return me
def kanat(ad, plan, kok_kalin, uc_kalin, z=0., cift=True, profil=10):
    # plan: yarım kanat dış hatları [(x, y)] (y>=0), saat yönü tersine; kalınlık y ile doğrusal; üst yüzey profil kubbesi
    bm = bmesh.new(); ymax = max(p[1] for p in plan)
    def kal(y): return kok_kalin + (uc_kalin - kok_kalin) * (y / ymax if ymax else 0)
    ust = [bm.verts.new((x, y, z + kal(y) * .62)) for x, y in plan]; alt = [bm.verts.new((x, y, z - kal(y) * .38)) for x, y in plan]
    bm.faces.new(ust); bm.faces.new(alt[::-1]); k = len(plan)
    for i in range(k): bm.faces.new((ust[i], alt[i], alt[(i + 1) % k], ust[(i + 1) % k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if cift:
        bmesh.ops.mirror(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], axis='Y', merge_dist=.002)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(ad); bm.to_mesh(me); bm.free(); return me
def yazi(ad, metin, boy, renk=(1, 1, 1), kalin=.002, ebeveyn=None, emisyon=0.):
    cu = bpy.data.curves.new(ad, 'FONT'); cu.body = metin; cu.size = boy; cu.extrude = kalin; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    try: cu.font = bpy.data.fonts.load(FONT, check_existing=True)
    except Exception: pass
    o = bpy.data.objects.new(ad, cu); bpy.context.scene.collection.objects.link(o)
    m = malz(ad + '_m', renk, .4, **({'Emission Color': (*renk, 1), 'Emission Strength': emisyon} if emisyon else {})); cu.materials.append(m)
    if ebeveyn: o.parent = ebeveyn
    return o
def resim_etiket(ad, dosya, gen, ebeveyn=None, alfa=True, pur=.5, emisyon=0.):
    if not os.path.exists(dosya):   # logo yoksa (repoda marka logoları yok) boş nesne: sahne yine kurulur
        print('UYARI: logo yok, atlandı:', dosya); o = bpy.data.objects.new(ad, None); bpy.context.scene.collection.objects.link(o)
        if ebeveyn: o.parent = ebeveyn
        return o
    im = bpy.data.images.load(dosya, check_existing=True); w, h = im.size
    bpy.ops.mesh.primitive_plane_add(size=1); o = bpy.context.object; o.name = ad; o.scale = (gen, gen * h / w, 1); bpy.ops.object.transform_apply(scale=True)
    m = bpy.data.materials.new(ad + '_m'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; ti = nt.nodes.new('ShaderNodeTexImage'); ti.image = im
    nt.links.new(ti.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = pur
    if alfa: nt.links.new(ti.outputs['Alpha'], b.inputs['Alpha']); m.surface_render_method = 'DITHERED' if hasattr(m, 'surface_render_method') else None
    if emisyon: nt.links.new(ti.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = emisyon
    o.data.materials.append(m)
    if ebeveyn: o.parent = ebeveyn
    return o
def hdri_dunya(dosya, guc=1., donus=0., gorunur=True):
    sc = bpy.context.scene; w = bpy.data.worlds.new('dunya'); sc.world = w; w.use_nodes = True; nt = w.node_tree; bg = nt.nodes['Background']
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value = (0, 0, donus)
    te = nt.nodes.new('ShaderNodeTexEnvironment'); te.image = bpy.data.images.load(os.path.join(UW, 'hdri', dosya))
    nt.links.new(tc.outputs['Generated'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], te.inputs['Vector']); nt.links.new(te.outputs['Color'], bg.inputs['Color']); bg.inputs['Strength'].default_value = guc
    if not gorunur:   # ışık HDRI'dan, kamera görmez (koyu stüdyo)
        lp = nt.nodes.new('ShaderNodeLightPath'); mx = nt.nodes.new('ShaderNodeMixShader'); bk = nt.nodes.new('ShaderNodeBackground'); bk.inputs['Color'].default_value = (.004, .004, .005, 1)
        nt.links.new(lp.outputs['Is Camera Ray'], mx.inputs[0]); nt.links.new(bg.outputs[0], mx.inputs[1]); nt.links.new(bk.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], nt.nodes['World Output'].inputs['Surface'])
    return w
def isik(ad, tip, konum, hedef, enerji, renk=(1, 1, 1), boy=1.):
    L = bpy.data.lights.new(ad, tip); L.energy = enerji; L.color = renk
    if tip == 'AREA': L.size = boy
    if tip == 'SUN': L.angle = math.radians(boy)
    o = bpy.data.objects.new(ad, L); o.location = konum; o.rotation_euler = (Vector(hedef) - Vector(konum)).to_track_quat('-Z', 'Y').to_euler(); bpy.context.scene.collection.objects.link(o); return o
def eevee(sc, kare_say, ornek=64, bulanik=True):
    sc.render.engine = 'BLENDER_EEVEE' if 'BLENDER_EEVEE' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE_NEXT'
    for a, v in (('taa_render_samples', ornek), ('use_raytracing', True), ('use_shadows', True)):
        try: setattr(sc.eevee, a, v)
        except Exception: pass
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1920; sc.render.fps = 30; sc.frame_start = 1; sc.frame_end = kare_say
    sc.view_settings.view_transform = 'AgX'
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    sc.render.use_motion_blur = bulanik
    try: sc.render.motion_blur_shutter = .35
    except Exception: pass
def kamera(lens=50, fstop=0.):
    sc = bpy.context.scene; cd = bpy.data.cameras.new('kam'); cd.lens = lens; cd.clip_start = .05; cd.clip_end = 20000
    if fstop: cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop
    k = bpy.data.objects.new('kam', cd); sc.collection.objects.link(k); sc.camera = k; return k
def bak(o, konum, hedef, kare=None):
    o.location = konum; o.rotation_euler = (Vector(hedef) - Vector(konum)).to_track_quat('-Z', 'Y').to_euler()
    if kare is not None: o.keyframe_insert('location', frame=kare); o.keyframe_insert('rotation_euler', frame=kare)
def yumusak_egriler(o):   # anahtar karelerde kolay giriş/çıkış (bezier) -> akışkan
    ad = o.animation_data
    if ad and ad.action:
        for fc in getattr(ad.action, 'fcurves', []):
            for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'; kp.easing = 'AUTO'
def bayrak_resmi(): return os.path.join(UW, 'bayrak.png')
