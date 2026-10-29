# Konuşmacı ölçümü: "bu replik kimin?" sorusunu tahminle değil sesle cevaplar.
#   python araclar/konusmaci.py vocals.wav referans.json [satirlar.json]
#   referans.json: {"Polat": [[0.05, 2.1], [2.9, 4.7]], "Memati": [[7.1, 9.2]]}  (konuşanın ekranda ağzının açıkça oynadığı kesin aralıklar)
#   satirlar.json: [[bas, bit, "metin"], ...]  (yoksa tüm ses 1 sn dilimlerle taranır)
# Yöntem: log-mel MFCC ortalaması + perde (F0); her satır ve 1 sn dilim için en yakın ses merkezi ve fark.
# Fark < ~1 ise ZAYIF: o aralıkta ağız bölgesini kare kare kontrol et (ağzı oynayan konuşandır).
import sys, json, numpy as np, soundfile as sf
from scipy.signal import resample_poly
from scipy.fft import dct
sys.stdout.reconfigure(encoding='utf-8')
v, SR = sf.read(sys.argv[1]); v = v.mean(1) if v.ndim > 1 else v; v = resample_poly(v, 16000, SR); SR = 16000
REF = json.load(open(sys.argv[2], encoding='utf-8'))

def melfb(n=40, nfft=512):
    hz = lambda m: 700 * (10 ** (m / 2595) - 1); mel = lambda f: 2595 * np.log10(1 + f / 700)
    p = hz(np.linspace(mel(80), mel(7600), n + 2)); b = np.floor((nfft + 1) * p / SR).astype(int); F = np.zeros((n, nfft // 2 + 1))
    for i in range(n):
        for k in range(b[i], b[i + 1]): F[i, k] = (k - b[i]) / max(1, b[i + 1] - b[i])
        for k in range(b[i + 1], b[i + 2]): F[i, k] = (b[i + 2] - k) / max(1, b[i + 2] - b[i + 1])
    return F
FB = melfb()

def oz(a, b):
    x = v[int(a * SR):int(b * SR)]
    fr = [(np.sqrt(np.mean(w ** 2)), w) for w in (x[i:i + 400] * np.hamming(400) for i in range(0, len(x) - 400, 160))]
    if not fr: return None
    em = max(e for e, _ in fr); C, F0 = [], []
    for e, w in fr:
        if e < em * .25: continue   # yalnız sesli çerçeveler
        P = np.abs(np.fft.rfft(w, 512)) ** 2; C.append(dct(np.log(FB @ P + 1e-10), norm='ortho')[1:14])
        ww = w - w.mean(); ac = np.correlate(ww, ww, 'full')[399:]
        if ac[0] > 0:
            ac = ac / ac[0]; k = 53 + np.argmax(ac[53:267])
            if ac[k] > .5: F0.append(SR / k)
    C = np.array(C); return C.mean(0), C.std(0), (np.median(F0) if F0 else 0)

mer = {k: np.vstack([oz(a, b)[0] for a, b in L]).mean(0) for k, L in REF.items()}
sd = np.mean([oz(a, b)[1] for L in REF.values() for a, b in L], 0)
for k, L in REF.items(): print(f'referans {k}: perde {np.median([oz(a, b)[2] for a, b in L]):.0f} Hz')

def kim(a, b):
    r = oz(a, b)
    if r is None: return '-', 0, 0
    m, _, f0 = r; d = {k: np.linalg.norm((m - c) / sd) for k, c in mer.items()}; s = sorted(d, key=d.get)
    return s[0], (d[s[1]] - d[s[0]]) if len(s) > 1 else 0, f0

S = json.load(open(sys.argv[3], encoding='utf-8')) if len(sys.argv) > 3 else [[t, t + 1, ''] for t in np.arange(0, len(v) / SR - .5, 1.0)]
for a, b, m in S:
    k, g, f0 = kim(a, b); dil = []; t = a
    while t < b - .4: kk, gg, _ = kim(t, min(b, t + 1.0)); dil.append(f'{kk}{gg:.1f}'); t += 1.0
    print(f"{a:7.2f}-{b:7.2f} -> {k:10s} fark {g:4.2f}{' ZAYIF' if g < 1 else ''} F0 {f0:4.0f} | {' '.join(dil):36s} | {m}")
