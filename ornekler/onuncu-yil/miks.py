# Atatürk · Onuncu Yıl edit miksi (28 Eki): ses-temiz.wav (Atatürk'ün kendi sesi, temizlenmiş, −14 LUFS) + sentez yaylı zemini.
# Zemin: ağır, saygılı; Re minör (Dm–B♭–F–C) konuşma boyunca −26 dB civarı, konuşmada ayrıca kısılır (sidechain); kapanış kartında Re majöre açılır (umut).
# Telif yok (sentez). Çıktı miks.wav (48 kHz mono) — kurgu-gece "son" bunu kullanır.
import numpy as np, soundfile as sf, json, os
from scipy.signal import butter, sosfiltfilt
D = os.path.dirname(os.path.abspath(__file__)); SR = 48000
J = json.load(open(os.path.join(D, 'zaman.json'), encoding='utf-8')); SURE = J['sure']
v, sr = sf.read(os.path.join(D, 'ses-temiz.wav')); v = v.mean(1) if v.ndim > 1 else v
assert sr == SR, sr
N = int(SURE * SR); t = np.arange(N) / SR
ses = np.zeros(N); ses[:min(N, len(v))] = v[:N]
nota = lambda n: 440 * 2 ** ((n - 69) / 12)
def yay(f, a, b):   # dedektörlü testere dalgası topluluğu (yaylı), yumuşak giriş/çıkış
    i0, i1 = int(a * SR), int(b * SR); tt = np.arange(i1 - i0) / SR; s = np.zeros(i1 - i0)
    for d in (-.09, -.03, .03, .09): ph = 2 * np.pi * f * (1 + d / 100) * tt + np.random.default_rng(int(f)).random() * 6; s += 2 * ((ph / (2 * np.pi)) % 1) - 1
    s *= .25 * (1 + .06 * np.sin(2 * np.pi * 5.2 * tt))   # hafif vibrato genliği
    L = len(s); zar = np.minimum(1, tt / 1.6) * np.minimum(1, (L / SR - tt) / 1.4); return i0, s * zar
ZEMIN = np.zeros(N)
AK = [(0, ['D3', 'A3', 'D4', 'F4']), (10.5, ['Bb2', 'F3', 'D4', 'F4']), (21, ['F2', 'C3', 'A3', 'F4']), (30.5, ['C3', 'G3', 'E4', 'G4']), (37.5, ['Bb2', 'F3', 'D4', 'F4']), (42.0, ['D3', 'A3', 'D4', 'F#4', 'A4'])]
AD = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'Bb': 10, 'B': 11}
def mid(s): ad, ok = s[:-1], int(s[-1]); return 12 * (ok + 1) + AD[ad]
for k, (a, notalar) in enumerate(AK):
    b = AK[k + 1][0] + 1.4 if k + 1 < len(AK) else SURE
    for n in notalar: i0, s = yay(nota(mid(n)), a, min(b, SURE)); ZEMIN[i0:i0 + len(s)] += s
ZEMIN = sosfiltfilt(butter(2, [70, 2600], 'bandpass', fs=SR, output='sos'), ZEMIN)
ZEMIN /= np.max(np.abs(ZEMIN)) + 1e-9
# seviye eğrisi: konuşma boyunca −26 dB; konuşma anında ek −6 dB (zarf); kapanış kartında −12 dB'ye çıkar, son 0,6 sn söner
e = np.sqrt(np.convolve(ses ** 2, np.ones(SR // 20) / (SR // 20), 'same')); kon = np.clip(e / (np.percentile(e, 95) + 1e-9), 0, 1)
kon = np.convolve(kon, np.ones(SR // 5) / (SR // 5), 'same')
seviye = 10 ** (-26 / 20) * (1 - .5 * kon)
kart = np.clip((t - J['kart']) / 1.2, 0, 1); seviye = seviye * (1 - kart) + 10 ** (-13 / 20) * kart
seviye *= np.clip((SURE - t) / .8, 0, 1) * np.clip(t / 1.0, 0, 1)
out = ses + ZEMIN * seviye
out /= max(1, np.max(np.abs(out)) / .97)
sf.write(os.path.join(D, 'miks.wav'), out.astype('float32'), SR, subtype='PCM_16')
print('miks.wav', round(SURE, 2), 'sn; zemin tepe', round(float(np.max(np.abs(ZEMIN * seviye))), 3))
