# UZAY ara planı (4,0 sn; zaman.json UZAY 35.38 -> K5 39.42): yerdurağan yörüngede Türksat 6A (ilk yerli haberleşme uydusu), altında Dünya (Türkiye görünür),
# sert güneş ışığı, atmosfer parıltısı, yıldızlar. Uydu: altın yalıtım kaplı gövde, iki güneş paneli kanadı, beyaz anten çanakları, bayrak + TÜRKSAT 6A.
# Kamera uyduya yavaş yaklaşıp hafif döner; Dünya yavaşça döner. Kullanım: blender -b -P s_uzay.py -- [kare] -> sahne_uzay.blend
import os, sys, math
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'urun_ortak.py'), encoding='utf-8').read())
a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []; NK = int(a[0]) if a else 120
sc = sifirla(); eevee(sc, NK, 64, True)
LOGO = os.path.join(UW, '..', 'logo')
# yıldızlı uzay: koyu arka plan + seyrek parlak noktalar (Voronoi)
w = bpy.data.worlds.new('uzay'); sc.world = w; w.use_nodes = True; nt = w.node_tree; bg = nt.nodes['Background']; L = nt.links.new
tc = nt.nodes.new('ShaderNodeTexCoord'); vr = nt.nodes.new('ShaderNodeTexVoronoi'); vr.inputs['Scale'].default_value = 420; L(tc.outputs['Generated'], vr.inputs['Vector'])
rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].position = .0; rp.color_ramp.elements[0].color = (1, 1, 1, 1); rp.color_ramp.elements[1].position = .035; rp.color_ramp.elements[1].color = (0, 0, 0, 1)
L(vr.outputs['Distance'], rp.inputs[0]); L(rp.outputs['Color'], bg.inputs['Color']); bg.inputs['Strength'].default_value = .6
isik('gunes', 'SUN', (0, 0, 0), (-.6, .55, -.35), 6.0, (1, .97, .92), .5)
# Dünya (yarıçap ölçeği: 1 birim = 100 km; uydu birkaç metre -> Dünya çok uzakta ve büyük: yarıçap 63,7 birim, merkez uydunun 40 birim altında + geride)
bpy.ops.mesh.primitive_uv_sphere_add(radius=63.7, segments=128, ring_count=64, location=(0, 60, -78)); du = bpy.context.object; du.name = 'dunya'
for p in du.data.polygons: p.use_smooth = True
dm = bpy.data.materials.new('dunya'); dm.use_nodes = True; t_ = dm.node_tree; b = t_.nodes['Principled BSDF']
ti = t_.nodes.new('ShaderNodeTexImage'); ti.image = bpy.data.images.load(os.path.join(LOGO, 'dunya-8k.jpg')); t_.links.new(ti.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = .7
fr = t_.nodes.new('ShaderNodeLayerWeight'); fr.inputs['Blend'].default_value = .25; em = t_.nodes.new('ShaderNodeMix'); em.data_type = 'RGBA'
t_.links.new(fr.outputs['Facing'], em.inputs['Factor']); em.inputs[6].default_value = (0, 0, 0, 1); em.inputs[7].default_value = (.25, .5, 1, 1)
t_.links.new(em.outputs[2], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 1.6   # atmosfer kenar parıltısı
du.data.materials.append(dm)
# Türkiye (39°K 35°D) yüzey normali kameraya baksın: UV küresinde +X boylam 0, +Z kuzey varsayımı; dönüş = normal -> (kamera - merkez) farkı
km = Vector((4.3, -13.7, 2.8)); n_tr = Vector((math.cos(math.radians(31)) * math.cos(math.radians(50)), math.cos(math.radians(31)) * math.sin(math.radians(50)), math.sin(math.radians(31))))
d_ = (km - du.location).normalized(); q0 = n_tr.rotation_difference(d_); du.rotation_mode = 'QUATERNION'
kz = q0 @ Vector((0, 0, 1)); up_ = Vector((0, 0, 1))   # kuzey yukarı: dünya ekseninin bakış düzlemine izdüşümü dünya yukarısına hizalanır
pk = (kz - d_ * kz.dot(d_)).normalized(); pu = (up_ - d_ * up_.dot(d_)).normalized(); ac = math.atan2(pk.cross(pu).dot(d_), pk.dot(pu))
q0 = __import__('mathutils').Quaternion(d_, ac) @ q0
du.rotation_quaternion = q0; du.keyframe_insert('rotation_quaternion', frame=1)
ek = __import__('mathutils').Quaternion(q0 @ Vector((0, 0, 1)), math.radians(2.5)); du.rotation_quaternion = ek @ q0; du.keyframe_insert('rotation_quaternion', frame=NK)   # kendi ekseninde yavaş dönüş
# Türksat 6A
uy = bpy.data.objects.new('turksat6a', None); sc.collection.objects.link(uy)
ALTIN = malz('mli_altin', (1.0, .66, .22), .32, .55, **{'Coat Weight': .3})   # parlak altın folyo (kahverengi görünüyordu)
nz = ALTIN.node_tree.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 9; nz.inputs['Detail'].default_value = 10; bu = ALTIN.node_tree.nodes.new('ShaderNodeBump'); bu.inputs['Strength'].default_value = .35
ALTIN.node_tree.links.new(nz.outputs['Fac'], bu.inputs['Height']); ALTIN.node_tree.links.new(bu.outputs['Normal'], ALTIN.node_tree.nodes['Principled BSDF'].inputs['Normal'])   # buruşuk altın folyo
bpy.ops.mesh.primitive_cube_add(size=1); gv = bpy.context.object; gv.scale = (1.8, 1.8, 2.4); bpy.ops.object.transform_apply(scale=True); gv.parent = uy; bagla(yumusat(gv, 1, .02), ALTIN)
PANEL = malz('gunes_hucre', (.01, .02, .08), .2, .3, **{'Coat Weight': .8})
br = PANEL.node_tree.nodes.new('ShaderNodeTexBrick'); br.inputs['Scale'].default_value = 3; br.inputs['Mortar Size'].default_value = .03
tco = PANEL.node_tree.nodes.new('ShaderNodeTexCoord'); PANEL.node_tree.links.new(tco.outputs['Object'], br.inputs['Vector'])
bp = PANEL.node_tree.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = .4; PANEL.node_tree.links.new(br.outputs['Fac'], bp.inputs['Height']); PANEL.node_tree.links.new(bp.outputs['Normal'], PANEL.node_tree.nodes['Principled BSDF'].inputs['Normal'])   # hücre ızgarası kabartma (renk gri kalıyordu)
for s in (1, -1):
    bpy.ops.mesh.primitive_cylinder_add(radius=.05, depth=1.4, location=(1.6 * s, 0, 0), rotation=(0, math.pi / 2, 0)); k = bpy.context.object; k.parent = uy; bagla(k, malz('kol', (.7, .7, .72), .3, 1.))
    for j in range(3):
        bpy.ops.mesh.primitive_cube_add(size=1, location=((2.6 + j * 2.05) * s, 0, 0)); p = bpy.context.object; p.scale = (2.0, .05, 1.6); bpy.ops.object.transform_apply(scale=True); p.parent = uy; bagla(p, PANEL)
BEYAZ = malz('anten', (.85, .85, .83), .45)
for (px, pz, r, rx) in ((.0, 1.35, .9, -.5), (.7, -1.0, .7, .6)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=48, ring_count=24, location=(px, -1.15, pz)); d = bpy.context.object; d.scale = (1, .32, 1); d.rotation_euler = (rx, 0, 0); d.parent = uy
    bm = bmesh.new(); bm.from_mesh(d.data); bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y > .25], context='VERTS'); bm.to_mesh(d.data); bm.free()
    sl = d.modifiers.new('k', 'SOLIDIFY'); sl.thickness = .03; bagla(yumusat(d, 1), BEYAZ)
bk = resim_etiket('t6a_bayrak', bayrak_resmi(), .9, uy, alfa=False, pur=.5); bk.rotation_euler = (math.pi / 2, 0, 0); bk.location = (.0, -.91, .2)
yz = yazi('t6a_yazi', 'TÜRKSAT 6A', .26, (.95, .95, .95), .01, uy); yz.rotation_euler = (math.pi / 2, 0, 0); yz.location = (0, -.92, -.55)
uy.rotation_euler = (.06, 0, .25); uy.keyframe_insert('rotation_euler', frame=1); uy.rotation_euler = (.02, 0, .10); uy.keyframe_insert('rotation_euler', frame=NK)
kam = kamera(35, 0)
bak(kam, (5.5, -16, 3.4), (0, 0, -1.5), 1); bak(kam, (3.2, -11.5, 2.2), (0, 0, -1.2), NK); yumusak_egriler(kam)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(UW, 'sahne_uzay.blend')); print('UZAY kaydedildi', NK)
