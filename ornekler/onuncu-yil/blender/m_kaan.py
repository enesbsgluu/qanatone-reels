# TUSAŞ KAAN modeli (exec ile): kaan(ad, ebeveyn, art_yakici) -> kök boşluk. Boy ~21 m, kanat açıklığı ~14 m. 5. nesil: keskin sırtlı burun, kokpit kanopisi,
# yan (kanal) hava girişleri, yamuk kanat, dışa yatık çift dikey kuyruk + yatay stabilizeler, çift motor lülesi (art yakıcı parıltısı). Renk açık-orta gri; kuyrukta bayrak, "KAAN".
def kaan(ad='kaan', ebeveyn=None, renk=(.20, .215, .23), art_yakici=1.):
    kok = bpy.data.objects.new(ad, None); bpy.context.scene.collection.objects.link(kok)
    if ebeveyn: kok.parent = ebeveyn
    G = boya(ad + '_boya', renk, .45, .35); Lu = malz(ad + '_lule', (.10, .09, .085), .35, 1.)
    KN = malz(ad + '_kanopi', (.08, .07, .03), .03, .3, **{'Coat Weight': 1., 'Coat Roughness': .02})   # altın kaplamalı kanopi
    L0 = 20.6; ch = dict(us=1.6, alt=1.8, ust_oran=.5, kose=.4); ort = dict(us=2.6, alt=2.2, ust_oran=.5, kose=.25)
    st = [(0, 0, 0, 0, {}), (.6, .4, .25, .02, ch), (2.0, 1.1, .7, .08, ch), (4.0, 1.6, 1.0, .12, ch), (6.0, 2.6, 1.15, .1, ort), (9.0, 3.6, 1.2, .05, ort),
          (13.0, 3.7, 1.15, .05, ort), (16.5, 3.2, 1.0, .05, ort), (19.0, 2.4, .85, .05, ort), (20.2, 2.1, .78, .05, ort)]
    gv = nesne(ad + '_govde', loft(ad + '_govde', [(L0 - x, w, h, z, k) for x, w, h, z, k in st][::-1], n=44), kok); bagla(yumusat(gv, 2), G)
    kp = nesne(ad + '_kanopi', loft(ad + '_kanopi', [(L0 - 3.4, .05, .05, .45, {}), (L0 - 4.3, .75, .55, .55, dict(us=2.2, alt=4, ust_oran=.9)), (L0 - 6.2, .85, .6, .6, dict(us=2.2, alt=4, ust_oran=.9)), (L0 - 7.6, .3, .2, .62, dict(us=2, alt=4, ust_oran=.9))], n=28), kok)
    bagla(yumusat(kp, 2), KN)
    for s in (1, -1):   # yan hava girişleri (açılı, kokpit gerisi)
        gi = nesne(ad + f'_giris{s}', loft(ad + '_giris', [(L0 - 11.5, .6, .9, -.1, dict(us=3, alt=3)), (L0 - 7.0, .85, .95, -.12, dict(us=3, alt=3))], n=20), kok); gi.location.y = 1.55 * s; bagla(yumusat(gi, 1), G)
        ag = nesne(ad + f'_agiz{s}', loft(ad + '_agiz', [(L0 - 6.98, .7, .8, -.12, dict(us=3, alt=3)), (L0 - 6.96, .7, .8, -.12, dict(us=3, alt=3))], n=20), kok); ag.location.y = 1.58 * s; bagla(ag, malz(ad + '_ic', (.01, .01, .012), .9))
    plan = [(8.5, 1.7), (13.6, 7.0), (15.4, 7.0), (16.2, 1.7)]
    kn = nesne(ad + '_kanat', kanat(ad + '_kanat', [(L0 - x, y) for x, y in plan][::-1], .30, .07), kok); bagla(yumusat(kn, 1, .01), G)
    ys = nesne(ad + '_ystab', kanat(ad + '_ystab', [(L0 - x, y) for x, y in [(17.0, 1.3), (19.4, 3.6), (20.5, 3.6), (20.6, 1.3)]][::-1], .14, .05, z=.0), kok); bagla(yumusat(ys, 1, .006), G)
    for s in (1, -1):
        me = kanat(ad + '_kuyruk', [(L0 - x, y) for x, y in [(15.2, 0), (17.6, 2.6), (19.0, 2.6), (19.9, 0)]][::-1], .16, .05, cift=False)
        k = nesne(ad + f'_kuyruk{s}', me, kok); k.rotation_euler = (math.radians(60 if s > 0 else 120), 0, 0); k.location = (0, 1.3 * s, .45); bagla(yumusat(k, 1, .006), G)
        zd = (-.16 * .38 - .003) if s > 0 else (.16 * .62 + .003); dz = (0, math.pi, 0) if s > 0 else (0, 0, 0)
        bk = resim_etiket(ad + f'_bayrak{s}', bayrak_resmi(), .75, k, alfa=False, pur=.45); bk.rotation_euler = dz; bk.location = (L0 - 18.3, 1.75, zd)
        yz = yazi(ad + f'_yazi{s}', 'KAAN', .32, (.12, .13, .14), .001, k); yz.rotation_euler = dz; yz.location = (L0 - 18.0, .85, zd)
        # lüle + art yakıcı
        lu = nesne(ad + f'_lule{s}', loft(ad + '_lule', [(.25, .95, .95, .05, dict(us=2, alt=2)), (-.55, .82, .82, .05, dict(us=2, alt=2))], n=36, kapak=False), kok); lu.location.y = .62 * s; bagla(yumusat(lu, 1), Lu)
        ay = malz(ad + '_alev', (1, .45, .15), .5, **{'Emission Color': (1, .45, .12, 1), 'Emission Strength': 25 * art_yakici})
        al = nesne(ad + f'_alev{s}', loft(ad + '_alev', [(-.35, .7, .7, .05, dict(us=2, alt=2)), (-2.2, .25, .25, .05, dict(us=2, alt=2)), (-3.4, .02, .02, .05, {})], n=24), kok); al.location.y = .62 * s
        bagla(al, ay)
        if art_yakici <= 0: al.hide_render = True
    return kok
