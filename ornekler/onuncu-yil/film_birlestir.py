# Onuncu Yıl Nutku filmi son birleştirme: blender/kare/<plan>/####.png (kürsü planları film karesiyle, ürün planları 1..N) -> zaman.json SAHNE sırası, kesme geçişler;
# altyazı (Inter 600, alt), ürün planlarında üstte marka etiketi, hafif sıcak renk + kenar kararması + gren; son: yandan 3/4 yakın (şarkı başlar) -> kart (yazı + imza çizimi).
# Ses: 0–42,3 sn yalnız nutuk (ses-temiz.wav, zaman.json OF 6,6), 42,3 sn'den şarkı 3:03–3:26 (23 sn). Çıktı: QANATONE-onuncu-yil-nutku-29-ekim-TR-1080x1920.mp4
# Kullanım: python film_birlestir.py [--onizle]   (--onizle: yalnız kontrol kareleri)
import os, re, sys, json, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)); K = os.path.join(D, 'blender', 'kare'); FPS = 30; Wd, Hd = 1080, 1920
FD = os.environ.get('QANAT_YAZITIPI', os.path.join(D, 'yazitipi')); Fn = lambda w, s: ImageFont.truetype(os.path.join(FD, 'Inter_' + w + '.ttf'), s)
SARKI = os.environ.get('QANAT_SARKI', '')   # kapanış şarkısı (telifli, repoda yok); yoksa miks.wav'ın sentez kapanışı kullanılır
SARKI_BAS = float(os.environ.get('QANAT_SARKI_BAS', '183'))   # şarkının hangi saniyesinden başlanır (bizim filmde 3:03)
if not os.path.exists(SARKI): SARKI, SARKI_BAS = os.path.join(D, 'miks.wav'), 42.3
J = json.load(open(os.path.join(D, 'zaman.json'), encoding='utf-8')); SAT = J['satir']
F = lambda t: int(round(t * 30)) + 1
SON0, SON1, KART = 42.3, 60.3, 5.0; NF = F(SON1) - 1 + int(KART * FPS)
PL = json.load(open(os.path.join(D, 'blender', 'kursu_planlar.json')))
URUN = [('TOGG', 8.56, 12.27, 'togg', 'TOGG  ·  T10X'), ('BAYKAR', 12.27, 15.96, 'baykar', 'BAYKAR  ·  KIZILELMA'), ('TUSAS', 20.95, 24.57, 'tusas', 'TUSAŞ  ·  KAAN'),
        ('TB3', 24.57, 28.11, 'tb3', 'BAYKAR  ·  TB3  ·  TCG ANADOLU'), ('MARTI', 33.07, 35.38, 'marti', 'MARTI'), ('UZAY', 35.38, 39.42, 'uzay', 'TÜRKSAT 6A')]
def kaynak(f):   # film karesi -> (png yolu, etiket)
    for ad, (a, b) in PL.items():
        if a <= f <= b: return os.path.join(K, ad, f'{f:04d}.png'), None
    for ad, t0, t1, kl, et in URUN:
        if F(t0) <= f < F(t1):
            n = len([x for x in os.listdir(os.path.join(K, kl))]) if os.path.isdir(os.path.join(K, kl)) else 1
            return os.path.join(K, kl, f'{min(f - F(t0) + 1, n):04d}.png'), (et, (f - F(t0)) / FPS, (F(t1) - F(t0)) / FPS)
    return None, None
ss = lambda x: np.clip(x, 0, 1) ** 2 * (3 - 2 * np.clip(x, 0, 1))
yy, xx = np.mgrid[0:Hd, 0:Wd].astype(np.float32); yy /= Hd; xx = xx / Wd * 2 - 1
VIN = (1 - .35 * ss((np.sqrt(xx ** 2 * .7 + ((yy - .48) * 1.5) ** 2) - .55) / .7))[..., None]
rng = np.random.default_rng(1923)
def renk(a):   # hafif sıcak renk + kenar kararması + ince gren
    a = a * np.array([1.03, 1.0, .965]) * VIN; a = a + rng.normal(0, 3.2, a.shape[:2])[..., None]; return a
def orta(dr, y, s, f, renk_=(255, 255, 255, 255), iz=0):
    w_ = sum(dr.textlength(ch, font=f) for ch in s) + iz * (len(s) - 1); x = (Wd - w_) / 2
    for ch in s: dr.text((x, y), ch, font=f, fill=renk_); x += dr.textlength(ch, font=f) + iz
FS = Fn('600SemiBold', 54); FE = Fn('600SemiBold', 30)
def katmanlar(im, f, etk):
    t = (f - 1) / FPS; ov = Image.new('RGBA', (Wd, Hd), (0, 0, 0, 0)); dr = ImageDraw.Draw(ov)
    for s_ in SAT:   # altyazı
        a_ = ss((t - s_['t'] + .1) / .25) * (1 - ss((t - (s_['t'] + s_['d']) - .15) / .25))
        if a_ <= 0: continue
        m = s_['m']; sat = [m]
        if dr.textlength(m, font=FS) > Wd - 120:
            k = m.split(); h = (len(k) + 1) // 2; sat = [' '.join(k[:h]), ' '.join(k[h:])]
        for j, l in enumerate(sat):
            orta(dr, 1600 + j * 70 + 3, l, FS, (0, 0, 0, int(160 * a_))); orta(dr, 1600 + j * 70, l, FS, (255, 255, 255, int(255 * a_)))
    if etk:   # marka etiketi: üstte, ince çizgi + harf aralıklı
        et, tt, du = etk; a_ = ss(tt / .35) * (1 - ss((tt - (du - .35)) / .3))
        if a_ > 0:
            orta(dr, 300, et, FE, (255, 255, 255, int(235 * a_)), iz=5); w_ = 46; dr.line(((Wd - w_) / 2, 352, (Wd + w_) / 2, 352), fill=(227, 10, 23, int(255 * a_)), width=3)
    return Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB')
# ---------- kart (yazı + imza çizimi), on_parca.py ile aynı tasarım, 5 sn ----------
svg = open(os.path.join(D, 'imza', 'imza.svg'), encoding='utf-8').read(); dp = re.search(r'<path[^>]*?\sd="([^"]+)"', svg, re.S).group(1)
tok = re.findall(r'[MLCz]|-?\d*\.?\d+(?:e-?\d+)?', dp); i = 0; alt = []; cur = None; Pp = []
while i < len(tok):
    c = tok[i]; i += 1
    if c == 'M':
        if Pp: alt.append(Pp)
        Pp = [(float(tok[i]), float(tok[i + 1]))]; i += 2; cur = 'L'; continue
    if c == 'z': alt.append(Pp); Pp = []; continue
    if c in 'LC': cur = c
    else: i -= 1; c = cur
    if c == 'L': Pp.append((float(tok[i]), float(tok[i + 1]))); i += 2
    else:
        p0 = np.array(Pp[-1]); p1, p2, p3 = [np.array((float(tok[i + 2 * k_]), float(tok[i + 2 * k_ + 1]))) for k_ in range(3)]; i += 6
        for tt in np.linspace(0, 1, 12)[1:]: Pp.append(tuple((1 - tt) ** 3 * p0 + 3 * (1 - tt) ** 2 * tt * p1 + 3 * (1 - tt) * tt * tt * p2 + tt ** 3 * p3))
if Pp: alt.append(Pp)
tum = np.concatenate([np.array(p) for p in alt]); mn, mx = tum.min(0), tum.max(0); IW = 720; sc_ = IW / (mx[0] - mn[0]); IH = int((mx[1] - mn[1]) * sc_) + 1; ix0, iy0 = (Wd - IW) // 2, 1080
mask = np.zeros((IH + 20, IW + 20), bool)
for p in alt:
    m_ = Image.new('L', (IW + 20, IH + 20), 0); ImageDraw.Draw(m_).polygon([((x - mn[0]) * sc_ + 10, (y - mn[1]) * sc_ + 10) for x, y in p], fill=255); mask ^= np.asarray(m_) > 127
im_a = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(.6)), np.float32) / 255
kol = np.nonzero(mask.any(0))[0]; xa, xb = kol.min(), kol.max()
def kart(t):
    r_ = np.sqrt(xx ** 2 * .6 + (yy - .45) ** 2 * 2.2)
    g = np.array([70, 8, 14], np.float32) * (1 - np.clip(r_, 0, 1))[..., None] + np.array([14, 3, 5], np.float32) * np.clip(r_, 0, 1)[..., None]
    im = Image.fromarray(g.clip(0, 255).astype(np.uint8)).convert('RGBA'); ov = Image.new('RGBA', (Wd, Hd), (0, 0, 0, 0)); dr = ImageDraw.Draw(ov)
    for s, f_, y, ta in (('29 Ekim', Fn('700Bold', 150), 610, .2), ('Cumhuriyet Bayramımız', Fn('600SemiBold', 74), 800, .65), ('Kutlu Olsun', Fn('600SemiBold', 74), 900, 1.05)):
        a_ = ss((t - ta) / .5); orta(dr, y + 18 * (1 - a_), s, f_, (255, 255, 255, int(255 * a_)))
    arr = np.asarray(Image.alpha_composite(im, ov).convert('RGB'), dtype=np.float32)
    u = np.clip((t - 1.6) / 2.2, 0, 1); xc = xa + (xb - xa + 30) * u
    on = np.clip((xc - np.arange(IW + 20)) / 14, 0, 1)[None, :] * im_a
    bl = arr[iy0:iy0 + IH + 20, ix0:ix0 + IW + 20]; bl[:] = bl * (1 - on[..., None]) + np.array([255, 255, 255], np.float32) * on[..., None]
    if 0 < u < 1:
        col = int(min(xc, xb)); ys = np.nonzero(mask[:, max(col - 3, 0):col + 1].any(1))[0]
        if len(ys):
            py, px = iy0 + ys.mean(), ix0 + col; Y_, X_ = np.ogrid[:Hd, :Wd]; pr = np.exp(-((Y_ - py) ** 2 + (X_ - px) ** 2) / (2 * 9 ** 2))[..., None]; arr = arr * (1 - .6 * pr) + 255 * .6 * pr
    return arr
# ---------- kareler ----------
ON = '--onizle' in sys.argv; KD = os.path.join(D, '_film_kare'); os.makedirs(KD, exist_ok=True)
KONTROL = [F(t) for t in (1, 5, 10, 14, 16.5, 19, 22, 26, 30, 34, 37, 41, 45, 55)] + [F(SON1) + 30, F(SON1) + 100, NF]
eksik = []
for f in (KONTROL if ON else range(1, NF + 1)):
    if f > F(SON1) - 1:
        t = (f - F(SON1)) / FPS; a = kart(t); a = a * ss((f - (F(SON1) - 1)) / 12) if f - F(SON1) < 12 else a   # karta geçiş: kısa açılış
        fr = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    else:
        p, etk = kaynak(f)
        if p is None or not os.path.exists(p): eksik.append(f); fr = Image.new('RGB', (Wd, Hd), (0, 0, 0))
        else:
            a = renk(np.asarray(Image.open(p).convert('RGB').resize((Wd, Hd)), dtype=np.float32))
            if F(SON1) - 1 - f < 12: a = a * ss((F(SON1) - 1 - f) / 12)   # son plan sonu kararır
            fr = katmanlar(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), f, etk)
    fr.save(os.path.join(KD, f'{f:05d}.jpg'), quality=95)
print('EKSİK kare', len(eksik), eksik[:10])
if ON: print('ÖNİZLEME', KONTROL); sys.exit()
OUT = os.path.join(D, 'film-tam.mp4'); T1 = SON0
FC = (f'[1:a]atrim=0:{T1},asetpts=PTS-STARTPTS,apad=whole_dur={T1},afade=t=out:st={T1 - .4}:d=0.4,loudnorm=I=-15:TP=-1.5[a1];'
      f'[2:a]atrim={SARKI_BAS}:{SARKI_BAS + (NF / FPS - T1)},asetpts=PTS-STARTPTS,apad=whole_dur={NF / FPS - T1},afade=t=in:d=0.8,afade=t=out:st={NF / FPS - T1 - 2.2}:d=2.2,loudnorm=I=-15:TP=-1.5[a2];'
      f'[a1][a2]concat=n=2:v=0:a=1,aresample=48000[a]')
r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(KD, '%05d.jpg'), '-i', os.path.join(D, 'ses-temiz.wav'), '-i', SARKI,
                    '-filter_complex', FC, '-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', '30',
                    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', OUT], capture_output=True, text=True)
print(r.returncode, r.stderr[-400:]); print('BİTTİ', OUT, 'kare', NF)
