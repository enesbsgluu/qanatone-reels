# Konuşma temizliği: python araclar/ses_temizle.py girdi.wav cikti.wav [--bas 6.6 --bit 48.9]
import sys; sys.stdout.reconfigure(encoding="utf-8")
# Girdi tercihen Demucs ile ayrılmış konuşma (vocals.wav). Sıra: kesit -> gürültü azaltma (en sessiz 0,5 sn gürültü örneği)
# -> 80 Hz altı kesim + 3 kHz anlaşılırlık + hafif parlaklık (aexciter) -> −14 LUFS, tepe −1,5 dBTP, 48 kHz mono.
import sys, os, subprocess, tempfile, numpy as np, soundfile as sf, noisereduce as nr
a = sys.argv[1:]; g, c = a[0], a[1]; op = lambda k, v=None: float(a[a.index(k) + 1]) if k in a else v
x, sr = sf.read(g); x = x.mean(1) if x.ndim > 1 else x
b0, b1 = op('--bas', 0), op('--bit', len(x) / sr); x = x[int(b0 * sr):int(b1 * sr)]
p = int(.5 * sr); e = np.array([np.sqrt(np.mean(x[i:i + p] ** 2)) for i in range(0, max(1, len(x) - p), p // 4)])
i0 = int(np.argmin(e)) * (p // 4); gurultu = x[i0:i0 + p]
y = nr.reduce_noise(y=x, sr=sr, y_noise=gurultu, stationary=True, prop_decrease=.9)
t = os.path.join(tempfile.gettempdir(), 'ses_temizle_ara.wav'); sf.write(t, y, sr)
af = 'highpass=f=80,equalizer=f=3000:t=q:w=1.2:g=3,equalizer=f=250:t=q:w=1:g=-2,aexciter=amount=1.5:freq=6000,loudnorm=I=-14:TP=-1.5:LRA=11'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', t, '-af', af, '-ar', '48000', '-ac', '1', c], check=True); os.remove(t)
def taban(z): z = z.mean(1) if z.ndim > 1 else z; w = int(.05 * 48000); return 20 * np.log10(np.percentile([np.sqrt(np.mean(z[i:i + w] ** 2)) + 1e-9 for i in range(0, len(z) - w, w)], 5))
print('gürültü tabanı (dB):', round(taban(sf.read(c)[0]), 1), '->', c)
