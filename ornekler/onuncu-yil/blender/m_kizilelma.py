# Bayraktar KIZILELMA modeli (exec ile, urun_ortak sonrası): kizilelma(ad, ebeveyn) -> kök boşluk. Ölçü: boy 14,7 m, kanat açıklığı 10 m, yükseklik ~3,4 m.
# Hatlar (ref/ara/kizilelma-*.jpg): keskin sırtlı (chine) burun, gövde altı tek hava girişi, kanardlar, kırık delta kanat, dışa yatık çift dikey kuyruk, tek motor lülesi.
# Renk: koyu gri; kuyrukta Türk bayrağı + "BAYRAKTAR KIZILELMA", gövdede "TC-ÖZB".
def kizilelma(ad='kizilelma', ebeveyn=None, renk=(.022, .024, .028)):
    kok = bpy.data.objects.new(ad, None); bpy.context.scene.collection.objects.link(kok)
    if ebeveyn: kok.parent = ebeveyn
    G = boya(ad + '_boya', renk, .42, .45); Gk = boya(ad + '_koyu', (.025, .027, .03), .5, .2); Lu = malz(ad + '_lule', (.08, .07, .065), .32, 1.)
    ch = dict(us=1.6, alt=1.9, ust_oran=.5, kose=.35); ort = dict(us=2.4, alt=2.0, ust_oran=.55, kose=.18)
    st = [(0, 0, 0, 0, {}), (.35, .30, .14, .02, ch), (1.2, .85, .40, .06, ch), (2.4, 1.35, .70, .10, ch), (3.8, 1.75, .88, .12, ort), (5.5, 2.0, .98, .12, ort),
          (7.5, 2.1, 1.0, .12, ort), (9.5, 1.95, .92, .12, ort), (11.5, 1.6, .80, .12, ort), (13.4, 1.15, .70, .12, ort), (14.3, .98, .66, .12, ort)]
    gv = nesne(ad + '_govde', loft(ad + '_govde', [(14.3 - x, w, h, z, k) for x, w, h, z, k in st][::-1], n=40), kok); bagla(yumusat(gv, 2), G)
    # gövde altı hava girişi (x 3.6..7, burnun 4,5 m gerisinde açılır)
    gi = nesne(ad + '_giris', loft(ad + '_giris', [(14.3 - 8.6, .5, .12, -.30, dict(us=3, alt=3, ust_oran=.5)), (14.3 - 6.5, 1.15, .30, -.38, dict(us=3, alt=4, ust_oran=.5)), (14.3 - 3.9, 1.25, .32, -.38, dict(us=3, alt=4, ust_oran=.5))], n=24, kapak=True), kok)   # gövdeye kaynaşık (ilk hali kapsül gibiydi)
    bagla(yumusat(gi, 1), G)
    ag = nesne(ad + '_agiz', loft(ad + '_agiz', [(14.3 - 3.86, 1.08, .24, -.38, dict(us=3, alt=4)), (14.3 - 3.84, 1.08, .24, -.38, dict(us=3, alt=4))], n=24), kok); bagla(ag, malz(ad + '_ic', (.01, .01, .012), .9))
    # kırık delta kanat (yarım plan: x burundan, y sol)
    plan = [(5.0, .95), (8.6, 2.6), (10.6, 5.0), (12.0, 5.0), (12.6, 2.2), (12.9, .95)]
    kn = nesne(ad + '_kanat', kanat(ad + '_kanat', [(14.3 - x, y) for x, y in plan][::-1], .20, .05, z=.02), kok); bagla(yumusat(kn, 1, .01), G)
    kd = nesne(ad + '_kanard', kanat(ad + '_kanard', [(14.3 - x, y) for x, y in [(3.0, .8), (4.3, 2.0), (4.8, 2.0), (4.7, .8)]][::-1], .07, .03, z=.18), kok); bagla(yumusat(kd, 1, .005), G)
    # dışa yatık çift dikey kuyruk
    for s in (1, -1):   # s=+1 sol (+Y), -1 sağ; kanat düzlemi XY, açıklık +Y -> X ekseninde dönüş: sol 62°, sağ 118° (ikisi de yukarı-dışa 28° yatık)
        me = kanat(ad + '_kuyruk', [(14.3 - x, y) for x, y in [(11.0, 0), (12.6, 1.75), (13.5, 1.75), (14.2, 0)]][::-1], .12, .04, cift=False)
        k = nesne(ad + f'_kuyruk{s}', me, kok); k.rotation_euler = (math.radians(62 if s > 0 else 118), 0, 0); k.location = (0, .72 * s, .42); bagla(yumusat(k, 1, .005), G)
        # dış yüz: sol kuyrukta yerel -Z (etiket Y etrafında 180° -> okunuş ileri-geri doğru), sağda yerel +Z
        zd = (-.12 * .38 - .003) if s > 0 else (.12 * .62 + .003); dz = (0, math.pi, 0) if s > 0 else (0, 0, 0)
        bk = resim_etiket(ad + f'_bayrak{s}', bayrak_resmi(), .55, k, alfa=False, pur=.45); bk.rotation_euler = dz; bk.location = (14.3 - 13.0, 1.22, zd)
        yz = yazi(ad + f'_yazi{s}', 'BAYRAKTAR\nKIZILELMA', .15, (.85, .86, .88), .001, k); yz.rotation_euler = dz; yz.location = (14.3 - 12.75, .62, zd)
    # lüle
    lu = nesne(ad + '_lule', loft(ad + '_lule', [(0, .82, .58, .12, dict(us=2.2, alt=2.2)), (-.45, .72, .52, .12, dict(us=2.2, alt=2.2))], n=40, kapak=False), kok); bagla(yumusat(lu, 1), Lu)
    ic = nesne(ad + '_lule_ic', loft(ad + '_lule_ic', [(-.3, .62, .44, .12, dict(us=2.2, alt=2.2)), (-.31, .62, .44, .12, dict(us=2.2, alt=2.2))], n=40), kok); bagla(ic, malz(ad + '_lule_karanlik', (.005, .004, .004), .6, emission=0))
    # gövde yazısı TC-ÖZB (sol yan, burun gerisi)
    for s in (1, -1):
        t = yazi(ad + f'_tc{s}', 'TC-ÖZB', .2, (.82, .83, .85), .001, kok); t.rotation_euler = (math.pi / 2, 0, math.pi if s > 0 else 0); t.location = (14.3 - 3.0, .76 * s, .12)   # sol yan normal +Y, okunuş -X
    return kok
