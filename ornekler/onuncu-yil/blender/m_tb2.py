# Bayraktar TB2 SİHA modeli (exec ile): tb2(ad, ebeveyn, pervane_hiz) -> kök boşluk. Boy 6,5 m, kanat açıklığı 12 m; ince gövde, düz yüksek kanat,
# ters V kuyruk (iki kuyruk bomu), arkada itici pervane, burun altında optik kamera kubbesi. Renk açık gri; kanat altında bayrak.
def tb2(ad='tb2', ebeveyn=None, renk=(.55, .57, .58), pervane=True):
    kok = bpy.data.objects.new(ad, None); bpy.context.scene.collection.objects.link(kok)
    if ebeveyn: kok.parent = ebeveyn
    G = boya(ad + '_boya', renk, .4, .4); K = malz(ad + '_koyu', (.03, .03, .035), .4); C = malz(ad + '_cam', (.02, .02, .03), .05, 0, **{'Coat Weight': 1.})
    od = dict(us=2.2, alt=2.2, ust_oran=.5)
    st = [(0, .02, .02, 0, od), (.25, .32, .34, 0, od), (.9, .58, .6, .02, od), (2.4, .62, .62, .04, od), (4.2, .5, .5, .04, od), (5.6, .28, .3, .04, od), (6.1, .12, .14, .04, od)]
    gv = nesne(ad + '_govde', loft(ad + '_govde', [(6.1 - x, w, h, z, k) for x, w, h, z, k in st][::-1], n=32), kok); bagla(yumusat(gv, 2), G)
    plan = [(2.0, 0), (2.0, 6.0), (2.75, 6.0), (2.95, 0)]   # düz kanat, kök kirişi .95, uç .75
    kn = nesne(ad + '_kanat', kanat(ad + '_kanat', [(6.1 - x, y) for x, y in plan][::-1], .12, .07, z=.3), kok); bagla(yumusat(kn, 1, .006), G)
    for s in (1, -1):   # kuyruk bomları + ters V kuyruk
        bpy.ops.mesh.primitive_cylinder_add(radius=.045, depth=3.3, vertices=16, location=(6.1 - 4.4, 1.15 * s, .3), rotation=(0, math.pi / 2, 0)); b = bpy.context.object; b.parent = kok; bagla(yumusat(b, 1), G)
        me = kanat(ad + '_vk', [(6.1 - x, y) for x, y in [(5.5, 0), (5.9, 1.05), (6.25, 1.05), (6.35, 0)]][::-1], .07, .04, cift=False)
        v = nesne(ad + f'_vkuyruk{s}', me, kok); v.rotation_euler = (math.radians(-40 if s > 0 else -140), 0, 0); v.location = (0, 1.15 * s, .3); bagla(yumusat(v, 1, .004), G)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.17, location=(6.1 - .55, 0, -.28)); kb = bpy.context.object; kb.parent = kok; bagla(yumusat(kb, 1), C)   # optik kubbe
    # itici pervane (arkada, x=0 yakını); hareket bulanıklığında disk gibi görünür
    pv = bpy.data.objects.new(ad + '_pervane', None); pv.location = (-.08, 0, .04); bpy.context.scene.collection.objects.link(pv); pv.parent = kok
    for a in (0, math.pi):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0)); p = bpy.context.object; p.scale = (.03, .07, .68); bpy.ops.object.transform_apply(scale=True)
        p.rotation_euler = (a, 0, 0); p.parent = pv; p.location = (0, 0, 0); bagla(yumusat(p, 1), K)
    for s in (1, -1):
        bk = resim_etiket(ad + f'_bayrak{s}', bayrak_resmi(), .5, kok, alfa=False, pur=.45); bk.location = (6.1 - 2.45, 4.6 * s, .3 - .045); bk.rotation_euler = (math.pi, 0, 0)
    kok['pervane'] = pv.name
    return kok
