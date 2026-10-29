# Atatürk · Onuncu Yıl Nutku (29 Ekim 1933) son bölümü — QANATONE edit (28 Eki 2026). Ses: ses-temiz.wav
# (kaynak 9qORieOMQRQ kesiti 181 sn + 6,6 sn; Demucs htdemucs_ft + noisereduce + EQ/exciter, −14 LUFS). Kelime zamanı: iyi-kelime.json (large-v3), −6,6 sn kaydırılır.
# Metin Atatürk'ün özgün metnidir (Whisper'ın yanlış duyduğu "hürmetli/teretti/neşale" düzeltildi). Satır bitişi enerjiyle uzatılır (kelime yutulmasın).
# SAHNE: kürsü (K*) ile ara planlar sırayla; ara planlar cümle sınırlarına oturur. Kapanış kartı konuşmadan sonra.
import json, os, numpy as np, soundfile as sf
D = os.path.dirname(os.path.abspath(__file__)); OF = 6.6
x, SR = sf.read(os.path.join(D, 'ses-temiz.wav')); x = x.mean(1) if x.ndim > 1 else x
W = [(w, a - OF, b - OF) for w, a, b in json.load(open(os.path.join(D, 'iyi-kelime.json'), encoding='utf-8')) if a - OF > -.2 and b - OF < 42.3]
SAT = [('Çünkü Türk Milletinin karakteri yüksektir.', 'Çünkü', 'yüksektir.'),
       ('Türk Milleti çalışkandır,', 'Türk', 'çalışkandır,'),
       ('Türk Milleti zekidir.', 'Türk', 'zekidir.'),
       ('Çünkü Türk Milleti, milli birlik ve beraberlikle', 'Çünkü', 'beraberlikle'),
       ('güçlükleri yenmesini bilmiştir.', 'güçlükleri', 'bilmiştir.'),
       ('Ve çünkü Türk Milletinin yürümekte olduğu', 'Ve', 'olduğu'),
       ('terakki ve medeniyet yolunda,', 'teretti', 'yolunda'),
       ('elinde ve kafasında tuttuğu meşale,', 'elinde', 'neşale'),
       ('müspet ilimdir.', 'müspetilimdir.', 'müspetilimdir.')]
i = 0; out = []
for m, ilk, son in SAT:
    while W[i][0] != ilk: i += 1
    a = W[i][1]
    while W[i][0] != son: i += 1
    b = W[i][2]; i += 1
    out.append([m, round(a, 2), round(b, 2)])
hh = SR // 30
e = np.array([np.sqrt(np.mean(x[j:j + hh] ** 2)) for j in range(0, len(x) - hh, hh)]); tepe = np.percentile(e, 98)
def uzat(b, sonraki):
    t = b
    while t < min(b + .35, sonraki - .15) and e[min(len(e) - 1, int(t * 30))] > tepe * 10 ** (-34 / 20): t += 1 / 30
    return round(min(t + .06, sonraki - .06), 2)
satir = []
for k, (m, a, b) in enumerate(out):
    nx = out[k + 1][1] if k + 1 < len(out) else 42.3
    b = uzat(b, nx); a = round(a - .05, 2)
    z = e[int(a * 30):int(b * 30) + 1]; taban = np.percentile(z, 12); z = np.clip(z - taban * .8, 0, None); mz = np.percentile(z, 95) or 1
    satir.append(dict(k=f'{k + 1:02d}', v='A', m=m, t=a, d=round(b - a, 3), z=[round(float(min(1, q / mz)), 2) for q in z]))
S = {s['k']: s for s in satir}
bas = lambda k: S[k]['t']; bit = lambda k: S[k]['t'] + S[k]['d']
# sahne sınırları (ara planlar cümleye oturur; geçişler cümle başından ~0,25 sn önce)
SAHNE = [[0, 'K1'], [bas('02') - .45, 'TOGG'], [bas('03') - .2, 'BAYKAR'], [bit('03') + .35, 'K2'], [bas('04') - .2, 'K3'],
         [bas('04') + 3.3, 'TUSAS'], [bas('05') - .1, 'TB3'], [bas('06') - .2, 'K4'], [bas('07') - .2, 'MARTI'], [bas('08') - .15, 'UZAY'],
         [bas('09') - .15, 'K5'], [42.3, 'KART']]
SAHNE = [[round(a, 2), n] for a, n in SAHNE]
vurgu = []
for s in satir:
    z = np.array(s['z'])
    for j in range(1, len(z) - 1):
        if z[j] >= np.percentile(z, 80) and z[j] >= z[j - 1] and z[j] > z[j + 1]: vurgu.append(round(s['t'] + j / 30 - .04, 2))
SURE = 46.0
J = dict(satir=satir, vurgu=vurgu, sahne=SAHNE, ses=42.3, sure=SURE, kart=42.3, kara=[SURE - .5, SURE])
json.dump(J, open(os.path.join(D, 'zaman.json'), 'w', encoding='utf-8'), ensure_ascii=False)
for s in satir: print(s['k'], f"{s['t']:6.2f} {s['t'] + s['d']:6.2f}", s['m'])
print(SAHNE)
