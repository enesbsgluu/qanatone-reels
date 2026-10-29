# MARTI ara planı (2,3 sn; zaman.json MARTI 33.07 -> UZAY 35.38): akşam şehir sokağında ıslak asfalt üstünde dizili Martı elektrikli mopetleri
# (yeşil gövde, beyaz ön kalkan, siyah sele; ref TRIPO-GIRDI/08), gövdede Martı logosu; kamera yandan kayarak geçer, sokak lambası yansımaları.
# Kullanım: blender -b -P s_marti.py -- [kare] -> sahne_marti.blend
import os, sys, math
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'urun_ortak.py'), encoding='utf-8').read())
a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []; NK = int(a[0]) if a else 75
sc = sifirla(); eevee(sc, NK, 64, True)
hdri_dunya('modern_evening_street_4k.hdr', 1.0, .6)
LOGO = os.path.join(UW, '..', 'logo')
YESIL = malz('marti_yesil', (.0, .55, .22), .3, **{'Coat Weight': .8, 'Coat Roughness': .05}); BEYAZ = malz('marti_beyaz', (.85, .87, .86), .3, **{'Coat Weight': .6})
SIYAH = malz('sele', (.02, .02, .022), .6); LAST = malz('lastik', (.015, .015, .017), .85); JANT = malz('jant_m', (.2, .2, .22), .35, 1.); KROM = malz('krom_m', (.8, .8, .82), .15, 1.)
FAR = malz('far', (1, 1, 1), .2, **{'Emission Color': (1, .97, .9, 1), 'Emission Strength': 12})
def moped(ad, konum, yon=0.):
    k = bpy.data.objects.new(ad, None); sc.collection.objects.link(k); k.location = konum; k.rotation_euler = (0, 0, yon)
    # gövde (arka kaporta, sele altı) - yerel +X ön
    st = [(-.75, .05, .05, .55, {}), (-.62, .30, .30, .56, dict(us=2.6, alt=2.4)), (-.15, .34, .36, .55, dict(us=2.6, alt=2.4)), (.1, .26, .26, .48, dict(us=2.4, alt=2.4)), (.18, .16, .14, .40, dict(us=2.2, alt=2.2))]
    g = nesne(ad + '_govde', loft(ad + '_govde', st, n=28), k); bagla(yumusat(g, 2), YESIL)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(.05, 0, .30)); ta = bpy.context.object; ta.scale = (.55, .30, .05); ta.parent = k; ta.location = (.05, 0, .30); bagla(yumusat(ta, 1, .02), SIYAH)   # ayak tabanı
    bpy.ops.mesh.primitive_cube_add(size=1); se = bpy.context.object; se.scale = (.62, .28, .09); se.parent = k; se.location = (-.32, 0, .76); bagla(yumusat(se, 2, .03), SIYAH)   # sele
    kf = nesne(ad + '_kalkan', loft(ad + '_kalkan', [(.30, .30, .55, .55, dict(us=3, alt=3)), (.42, .34, .62, .62, dict(us=3, alt=3)), (.50, .22, .50, .72, dict(us=3, alt=3))], n=24), k); bagla(yumusat(kf, 2), BEYAZ)   # ön kalkan
    bpy.ops.mesh.primitive_cylinder_add(radius=.03, depth=.6, location=(.52, 0, .95)); di = bpy.context.object; di.rotation_euler = (0, -.35, 0); di.parent = k; di.location = (.52, 0, .95); bagla(di, KROM)
    bpy.ops.mesh.primitive_cylinder_add(radius=.018, depth=.62, location=(.62, 0, 1.2), rotation=(math.pi / 2, 0, 0)); gd = bpy.context.object; gd.parent = k; gd.location = (.62, 0, 1.2); bagla(gd, SIYAH)   # gidon
    bpy.ops.mesh.primitive_cylinder_add(radius=.06, depth=.03, location=(.52, 0, .9), rotation=(0, math.pi / 2, 0)); fr = bpy.context.object; fr.parent = k; fr.location = (.515, 0, .9); bagla(fr, FAR)   # far ön kalkanın üstünde (havada duruyordu)
    for x in (-.52, .58):
        bpy.ops.mesh.primitive_cylinder_add(radius=.2, depth=.09, vertices=48, location=(x, 0, .2), rotation=(math.pi / 2, 0, 0)); l = bpy.context.object; l.parent = k; l.location = (x, 0, .2); bagla(yumusat(l, 1, .02), LAST)
        bpy.ops.mesh.primitive_cylinder_add(radius=.12, depth=.1, vertices=32, location=(x, 0, .2), rotation=(math.pi / 2, 0, 0)); j = bpy.context.object; j.parent = k; j.location = (x, 0, .2); bagla(j, JANT)
    for s in (1, -1):
        lg = resim_etiket(ad + f'_logo{s}', os.path.join(LOGO, 'marti-logo.png'), .34, k, alfa=True, pur=.3); lg.rotation_euler = (math.pi / 2, 0, 0 if s < 0 else math.pi); lg.location = (-.38, .175 * s, .56)
    return k
for i in range(5): moped(f'marti{i}', (i * .95 - 1.9, 0, 0), math.radians(-12))
bpy.ops.mesh.primitive_plane_add(size=80); z = bpy.context.object
zm = malz('asfalt', (.02, .02, .022), .18, **{'Coat Weight': .5, 'Coat Roughness': .03}); nt = zm.node_tree; nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 40
mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = .05; mr.inputs['To Max'].default_value = .5; nt.links.new(nz.outputs['Fac'], mr.inputs['Value']); nt.links.new(mr.outputs[0], nt.nodes['Principled BSDF'].inputs['Roughness'])   # ıslak asfalt: yer yer su birikintisi
bagla(z, zm)
isik('sokak', 'AREA', (1.5, -2.5, 3.5), (0, 0, .5), 260, (1, .85, .65), 1.5); isik('kenar', 'AREA', (-2.5, 3, 2), (0, 0, .7), 300, (.7, .8, 1), 1.0)
kam = kamera(40, 2.2); kam.data.dof.focus_distance = 3.4
bak(kam, (-2.6, -3.2, .85), (-1.2, 0, .6), 1); bak(kam, (1.6, -3.0, .8), (1.2, 0, .6), NK); yumusak_egriler(kam)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(UW, 'sahne_marti.blend')); print('MARTI kaydedildi', NK)
