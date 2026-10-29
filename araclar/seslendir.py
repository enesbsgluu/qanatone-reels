# Senaryoyu Gemini TTS ile seslendirir ve zamanlamayı gerçek sesten yazar.
import sys; sys.stdout.reconfigure(encoding="utf-8")
#   python araclar/seslendir.py <klasör>            -> <klasör>/ses.wav + senaryo.json'da satirlar[].bas/bit ve sure güncellenir
#   python araclar/seslendir.py <klasör> 3,4        -> yalnız 3. ve 4. satır yeniden üretilir (1'den sayılır), diğerleri önbellekten
# senaryo.json'a eklenecekler:
#   "karakterler": {"usta": {"ses": "Charon", "tarif": "ellili yaşlarda, sakin, bilge, alçak sesli"}, ...}
#   satırlarda isteğe bağlı "ton" ("meraklı", "kuru, iğneleyici") ve "bosluk" (satırdan önce sessizlik, sn; varsayılan .35)
#   isteğe bağlı "baglam": "Bu bir Türk kısa dizisi..." (tüm isteklere eklenir)
# Anahtar: GEMINI_API_KEY ortam değişkeni (aistudio.google.com, ücretsiz). Model: QANAT_TTS_MODEL (varsayılan aşağıda).
# Ücretsiz kota model başına günde ~10 istek: satırlar en fazla 2 konuşmacılı, 6 satırlık gruplar hâlinde tek istekte üretilir
# (karakterler birbirine cevap verdiği için tonlama da doğal akar). Çıktı Whisper kelime zamanlarıyla satırlara bölünür.
import json, os, sys, re, base64, time, wave, difflib, urllib.request, urllib.error, shutil
import numpy as np
from scipy.signal import resample_poly

D = os.path.abspath(sys.argv[1]); SJ = os.path.join(D, 'senaryo.json')
S = json.load(open(SJ, encoding='utf-8')); L = S['satirlar']; K = S['karakterler']
SEC = {int(x) - 1 for x in sys.argv[2].split(',')} if len(sys.argv) > 2 else None
MODEL = os.environ.get('QANAT_TTS_MODEL', 'gemini-2.5-flash-preview-tts')
KEY = os.environ.get('GEMINI_API_KEY') or (open(os.path.expanduser('~/.gemini-api-key')).read().strip() if os.path.exists(os.path.expanduser('~/.gemini-api-key')) else None)
if not KEY: sys.exit('GEMINI_API_KEY yok: aistudio.google.com -> Get API key, sonra ortam değişkeni olarak ver.')
ON = os.path.join(D, 'ses-parca'); os.makedirs(ON, exist_ok=True); SR = 24000

# ---- satırları en fazla 2 konuşmacılı, 6 satırlık gruplara böl ----
gruplar, g = [], []
for i, s in enumerate(L):
    kisiler = {L[j]['kim'] for j in g} | {s['kim']}
    if g and (len(kisiler) > 2 or len(g) >= 6): gruplar.append(g); g = []
    g.append(i)
if g: gruplar.append(g)

def iste(metin, kisiler):
    if len(kisiler) > 1: sc = {'multiSpeakerVoiceConfig': {'speakerVoiceConfigs': [{'speaker': k, 'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': K[k]['ses']}}} for k in kisiler]}}
    else: sc = {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': K[kisiler[0]]['ses']}}}
    b = json.dumps({'contents': [{'parts': [{'text': metin}]}], 'generationConfig': {'responseModalities': ['AUDIO'], 'speechConfig': sc}}).encode()
    for _ in range(6):
        try:
            r = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent', b, {'x-goog-api-key': KEY, 'Content-Type': 'application/json'})
            j = json.load(urllib.request.urlopen(r, timeout=300)); return np.frombuffer(base64.b64decode(j['candidates'][0]['content']['parts'][0]['inlineData']['data']), '<i2').astype(np.float32) / 32768
        except urllib.error.HTTPError as e:
            m = e.read().decode(); print('bekle', e.code, m[:200].replace('\n', ' '), flush=True)
            if 'PerDay' in m: sys.exit('GÜNLÜK KOTA DOLDU: ' + MODEL + ' (yarın ya da QANAT_TTS_MODEL ile başka model)')
            time.sleep(30)
    sys.exit('TTS isteği başarısız')

# ---- kelime eşleme yardımcıları ----
BIR = ['', 'bir', 'iki', 'üç', 'dört', 'beş', 'altı', 'yedi', 'sekiz', 'dokuz']; ONL = ['', 'on', 'yirmi', 'otuz', 'kırk', 'elli', 'altmış', 'yetmiş', 'seksen', 'doksan']
def say(n):   # 1912 -> bin dokuz yüz on iki (Whisper rakam yazar, metin yazıyla olabilir)
    if n == 0: return ['sıfır']
    o = []
    if n >= 1000: b = n // 1000; o += ([] if b == 1 else say(b)) + ['bin']; n %= 1000
    if n >= 100: y = n // 100; o += ([] if y == 1 else [BIR[y]]) + ['yüz']; n %= 100
    if n >= 10: o.append(ONL[n // 10]); n %= 10
    if n: o.append(BIR[n])
    return o
nrm = lambda s: re.sub(r'[^a-zçğıöşü0-9]', '', s.replace('İ', 'i').replace('I', 'ı').lower())
_m = None
def kelimeler(x):
    global _m
    if _m is None:
        from faster_whisper import WhisperModel
        _m = WhisperModel(os.environ.get('QANAT_WHISPER', 'medium'), device='cpu', compute_type='int8')
    seg, _ = _m.transcribe(resample_poly(x, 2, 3).astype(np.float32), language='tr', word_timestamps=True)
    W = []
    for s in seg:
        for w in s.words:
            d = re.sub(r'[.,]', '', w.word.strip())
            W += [(x_, w.start, w.end) for x_ in say(int(d))] if d.isdigit() else [(w.word, w.start, w.end)]
    return W

# ---- grup grup üret ve satırlara böl ----
for gi, g in enumerate(gruplar):
    if SEC is not None and not (SEC & set(g)) and all(os.path.exists(os.path.join(ON, f'{i + 1:02d}.wav')) for i in g): continue
    if SEC is None and all(os.path.exists(os.path.join(ON, f'{i + 1:02d}.wav')) for i in g): continue
    kisiler = list(dict.fromkeys(L[i]['kim'] for i in g))
    yon = ((S.get('baglam', 'Bu bir Türkçe kısa video.') + ' ') +
           'Herkesin ana dili Türkçe; telaffuz kusursuz İstanbul Türkçesi, hiçbir yabancı aksan yok. Gerçek oyuncular gibi doğal ve zamanlamalı konuşun; '
           'her cümleyi sonuna kadar tamamlayın. Her replikten sonra yaklaşık bir saniye sessizlik bırakın.\nKarakterler:\n' +
           ''.join(f"- {k}: {K[k]['tarif']}\n" for k in kisiler) +
           'Replik replik tonlar (bunları okuma, yalnız uygula):\n' + ''.join(f"{n + 1}. {L[i]['kim']}: {L[i].get('ton', 'doğal')}\n" for n, i in enumerate(g)) +
           '\nSeslendirilecek konuşma:\n' + ''.join(f"{L[i]['kim']}: {L[i]['metin']}\n" for i in g))
    print(f'grup {gi + 1}/{len(gruplar)}: satır {g[0] + 1}-{g[-1] + 1} ({", ".join(kisiler)})', flush=True)
    x = iste(yon, kisiler); WW = kelimeler(x)
    hedef = [(i, nrm(w)) for i in g for w in L[i]['metin'].split() if nrm(w)]
    sm = difflib.SequenceMatcher(None, [h[1] for h in hedef], [nrm(w[0]) for w in WW], autojunk=False)
    bas, son = {}, {}
    for blk in sm.get_matching_blocks():
        for q in range(blk.size):
            i = hedef[blk.a + q][0]; _, s0, e0 = WW[blk.b + q]; bas[i] = min(bas.get(i, s0), s0); son[i] = max(son.get(i, e0), e0)
    e = np.sqrt(np.convolve(x ** 2, np.ones(480) / 480, 'same'))
    def sessiz(t0, t1):   # kesim: iki satır arasındaki en sessiz an (kelime ortası kesilmez)
        i0, i1 = int(t0 * SR), int(t1 * SR)
        return (t0 + t1) / 2 if i1 <= i0 + 10 else (i0 + int(np.argmin(e[i0:i1]))) / SR
    for n, i in enumerate(g):
        if i not in bas:
            print(f'!! satır {i + 1} sesle eşleşmedi, boşluktan alındı'); onceki = son.get(g[n - 1], 0) if n else 0
            bas[i] = onceki + .05; son[i] = (bas[g[n + 1]] if n + 1 < len(g) and g[n + 1] in bas else len(x) / SR) - .05
    kes = [0] + [sessiz(son[g[n]] + .25, max(son[g[n]] + .26, bas[g[n + 1]])) for n in range(len(g) - 1)] + [len(x) / SR]
    for n, i in enumerate(g):
        y = x[int(kes[n] * SR):int(kes[n + 1] * SR)]
        ee = np.sqrt(np.convolve(y ** 2, np.ones(240) / 240, 'same')); ii = np.where(ee > ee.max() * 10 ** (-40 / 20))[0]
        y = y[max(0, ii[0] - 720):min(len(y), ii[-1] + 1920)].copy()
        y[:480] *= np.linspace(0, 1, min(480, len(y))); f2 = min(1440, len(y)); y[-f2:] *= np.linspace(1, 0, f2) ** 2
        y = y / (np.sqrt(np.mean(y ** 2)) + 1e-9) * 10 ** (-20 / 20)   # satırlar arası eşit düzey (−20 dB RMS)
        o = wave.open(os.path.join(ON, f'{i + 1:02d}.wav'), 'wb'); o.setnchannels(1); o.setsampwidth(2); o.setframerate(48000)
        o.writeframes((np.clip(resample_poly(y, 2, 1), -1, 1) * 32767).astype('<i2').tobytes()); o.close()
        duyulan = ' '.join(w[0].strip() for w in WW if bas[i] - .01 <= w[1] <= son[i] + .01)
        print(f"  {i + 1:02d} {L[i]['kim']:>8} {len(y) / SR:5.2f}s | {L[i]['metin']} | duyulan: {duyulan}", flush=True)

# ---- birleştir: satır sesleri + boşluklar -> ses.wav, zamanlar senaryo.json'a ----
t, parca = .5, [np.zeros(int(.5 * 48000), np.float32)]
for i, s in enumerate(L):
    w = wave.open(os.path.join(ON, f'{i + 1:02d}.wav')); y = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float32) / 32768
    if i: b = s.get('bosluk', .35); parca.append(np.zeros(int(b * 48000), np.float32)); t += b
    s['bas'] = round(t, 3); t += len(y) / 48000; s['bit'] = round(t, 3); parca.append(y)
S['sure'] = round(t + float(S.get('kapanis', 1.0)), 2); parca.append(np.zeros(int(float(S.get('kapanis', 1.0)) * 48000), np.float32))
o = wave.open(os.path.join(D, 'ses.wav'), 'wb'); o.setnchannels(1); o.setsampwidth(2); o.setframerate(48000)
o.writeframes((np.clip(np.concatenate(parca), -1, 1) * 32767).astype('<i2').tobytes()); o.close()
# plan kesmeleri satırlara bağlıysa ("satir": n) yeni zamana taşınır
for p in S.get('planlar', []):
    if 'satir' in p: p['bas'] = round(max(0, L[p['satir'] - 1]['bas'] - .15), 3)
shutil.copy(SJ, SJ + '.yedek'); json.dump(S, open(SJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('HAZIR:', os.path.join(D, 'ses.wav'), 'süre', S['sure'], '| senaryo.json güncellendi (eski: senaryo.json.yedek)')
