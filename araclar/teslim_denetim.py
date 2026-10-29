# Teslim denetimi: python araclar/teslim_denetim.py video.mp4 [senaryo.json] [pano.jpg]
# Ölçer: 1080x1920, 30 fps, SAR 1:1 (eksikse kayıpsız yazar, görüntü md5 eşitliğiyle doğrular), süre (senaryo verilirse), ses,
# −14 LUFS + gerçek tepe, kara blok (komşu karelerde olmayan dolu siyah dikdörtgen), tek karelik titreme (kesme kareleri hariç), kontak tabakası.
# Çıkış 1 = sorun var.
import subprocess, sys, json, os
import numpy as np
from scipy import ndimage
sys.stdout.reconfigure(encoding='utf-8')
a = sys.argv[1:]; v = a[0]
J = next((json.load(open(x, encoding='utf-8')) for x in a[1:] if x.endswith('.json')), {})
pano = next((x for x in a[1:] if x.endswith(('.jpg', '.png'))), None)
sorun = []
def pr(*x): print(*x, flush=True)

# 1) akış + SAR
o = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', v], capture_output=True, text=True).stdout)
vs = [s for s in o['streams'] if s['codec_type'] == 'video'][0]; au = [s for s in o['streams'] if s['codec_type'] == 'audio']; SURE = float(o['format']['duration'])
pr('boyut', vs['width'], 'x', vs['height'], '| fps', vs['r_frame_rate'], '| SAR', vs.get('sample_aspect_ratio'), '| süre', round(SURE, 2), '| ses akışı', len(au))
if (vs['width'], vs['height']) != (1080, 1920): sorun.append('boyut 1080x1920 değil')
if vs['r_frame_rate'] != '30/1': sorun.append('fps 30 değil')
if J.get('sure') and abs(SURE - J['sure']) > .25: sorun.append(f"süre {SURE:.2f} ≠ senaryo {J['sure']}")
if vs.get('sample_aspect_ratio') != '1:1':
    md = lambda f: subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-map', '0:v', '-f', 'md5', '-'], capture_output=True, text=True).stdout.strip()
    t = v + '.sar.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', v, '-map', '0', '-c', 'copy', '-bsf:v', 'h264_metadata=sample_aspect_ratio=1/1', '-movflags', '+faststart', t], check=True)
    if md(t) == md(v): os.replace(t, v); pr('SAR 1:1 yazıldı (görüntü md5 eşit)')
    else: sorun.append('SAR yazılamadı'); os.remove(t)

# 2) ses düzeyi
if au:
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', v, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = float(r[r.rindex('I:'):].split()[1]); P = float(r[r.rindex('Peak:'):].split()[1]); pr('LUFS', I, '| gerçek tepe', P)
    if not -15.5 < I < -12.5: sorun.append(f'LUFS {I} (hedef −14)')
    if P > -1.0: sorun.append(f'tepe {P} dBTP (hedef ≤ −1,5)')
else: sorun.append('ses yok')

# 3) kara blok: tek NaN piksel DOF/bloom'da dikdörtgene yayılır; komşu karelerde olmayan, içi dolu tam siyah alan aranır
W, H = 270, 480
F = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', v, '-vf', f'scale={W}:{H}:flags=neighbor,format=gray', '-f', 'rawvideo', '-'],
                                 capture_output=True).stdout, np.uint8).reshape(-1, H, W)
Sb = F < 6; kara = []
for i in range(4, len(F) - 4):   # açılış/kapanış karartması hariç
    yeni = Sb[i] & ~Sb[i - 1] & ~Sb[i + 1]
    if yeni.sum() < 300: continue
    et, _ = ndimage.label(yeni); boy = np.bincount(et.ravel())[1:]
    if boy.max() < 300: continue
    ys, xs = np.nonzero(et == boy.argmax() + 1)
    if Sb[i][ys.min():ys.max() + 1, xs.min():xs.max() + 1].mean() > .9: kara.append(round(i / 30, 2))
pr('kara blok', len(kara), kara[:10])
if kara: sorun.append(f'kara blok {kara[:10]}')

# 4) titreme: tek karelik sekme (kare komşularından farklı, komşular birbirine benzer); kesme kareleri hariç
G = F[:, ::3, ::3].astype(np.float32)
kes = {int(round(p['bas'] * 30)) for p in J.get('planlar', [])}; kes |= {x + d for x in list(kes) for d in (-1, 1, 2)}
tit = []
for i in range(4, len(G) - 1):
    if i in kes: continue
    x1 = np.abs(G[i] - G[i - 1]).mean(); x2 = np.abs(G[i + 1] - G[i]).mean(); x3 = np.abs(G[i + 1] - G[i - 1]).mean()
    if x1 > 4 and x2 > 4 and x3 < .5 * min(x1, x2): tit.append(round(i / 30, 2))
pr('titreme', len(tit), tit[:12], '(6 sn katlarındaysa çekim parçasının ilk karesi: ısıtma karesi eksik)' if tit else '')
if tit: sorun.append(f'titreme {len(tit)}')

# 5) kontak tabakası
if pano:
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', v, '-vf', f'fps={12 / SURE},scale=270:480,tile=6x2', '-frames:v', '1', pano]); pr('pano ->', pano)
pr('SORUN:', sorun if sorun else 'yok')
sys.exit(1 if sorun else 0)
