# Onuncu Yıl Nutku · 29 Ekim filmi (Blender hattı)

QANATONE'un 29 Ekim 2026 filmi: Atatürk'ün Onuncu Yıl Nutku'nun son bölümü, Atatürk'ün kendi sesiyle. Kürsüde fotoğraftan üretilmiş 3B Atatürk, ara planlarda Türkiye'nin bugünkü başarıları (TOGG T10X, Baykar Kızılelma, TUSAŞ KAAN, TB3 + TCG Anadolu, Martı, Türksat 6A). 65 sn, 1080×1920.

Bu klasör filmin **gerçekten kullanılan** betiklerini içerir. Deneme sürümleri ve hata ayıklama betikleri çıkarıldı. Ağır dosyalar (ses, `.blend`, `.glb`, render kareleri) repoda yok, her biri aşağıdaki adımlarla yerelde üretilir.

## Gerekenler

- [Blender 4.2+](https://www.blender.org/download/) (film 5.2 ile yapıldı) — `blender` komutu PATH'te olmalı ya da `BLENDER` ortam değişkeni ile yolu ver
- Python: `pip install numpy scipy soundfile pillow faster-whisper demucs noisereduce gradio_client huggingface_hub mediapipe`
- Ücretsiz [Hugging Face](https://huggingface.co) hesabı (`huggingface-cli login`): 3B üretim ücretsiz Space'lerde koşar, kotası hesaba bağlıdır
- [Inter](https://fonts.google.com/specimen/Inter) yazı tipi: `Inter_600SemiBold.ttf` ve `Inter_700Bold.ttf` dosyalarını `yazitipi/` klasörüne koy (ya da `QANAT_YAZITIPI` ile klasörü göster)
- GPU önerilir (render saatler sürer; filmde 4 GB'lık kartla ~3,5 saat)

Komutlar `ornekler/onuncu-yil` klasöründen çalıştırılır.

## 1. Ses

```bash
bash kaynak/indir.sh                                                        # kaynak/iyi-kesit44.wav (181–233 sn)
demucs -n htdemucs_ft --two-stems vocals -o ayir kaynak/iyi-kesit44.wav     # konuşmayı arka plandan ayır
python ../../araclar/ses_temizle.py ayir/htdemucs_ft/iyi-kesit44/vocals.wav ses-temiz.wav --bas 6.6 --bit 48.9
python miks.py                                                              # sentez yaylı zemin (telifsiz) -> miks.wav
```

`ses-temiz.wav` film zamanına hizalıdır (0 = ilk kelime). `iyi-kelime.json` (Whisper large-v3 kelime zamanları, kesit zamanında) ve `zaman.json` (satırlar + sahne sırası) repoda hazır gelir. Yeniden üretmek için `python ../../araclar/kelime_zamani.py kaynak/iyi-kesit44.wav iyi-kelime.json`, ardından `python zaman.py`. Whisper'ın yanlış duyduğu kelimeler `zaman.py` içinde özgün metinle düzeltilir.

## 2. Fotoğraftan 3B

Girdi görselleri (`heykel/uretim/girdi-*.png`) senin seçeceğin fotoğraflardır. Arka planı silinmiş (RGBA), kare, yüz/nesne ortada olmalı.

```bash
python heykel/uretim/uret.py hunyuan21 heykel/uretim/girdi-bas-rgba.png              # baş/büst -> heykel/uretim/hunyuan21.glb
python heykel/uretim/uret.py hunyuan21 heykel/uretim/girdi-kursu-rgba.png -kursu     # kürsüde iki elle kâğıt tutan gövde
python heykel/uretim/uret.py hunyuan21 heykel/uretim/girdi-togg-rgba.png -togg       # TOGG T10X
```

Kürsü gövdesi için nutuk görüntüsünden bir kare kullanıldı (mikrofon boyanıp silindi). Hazır frak/giysi modelleri iskeletlenemediği için gövde doğrudan kürsü pozundaki fotoğraftan üretildi.

## 3. Yüz

Ayrıntılı yüz [Tripo](https://www.tripo3d.ai) ile (ücretsiz kredi) aynı fotoğraftan üretildi ve GLB olarak indirildi. Hunyuan modeli kafatası, saç ve kulakları verir; iki model MediaPipe 478 yüz noktasıyla hizalanır.

```bash
blender -b -P heykel/b_ac.py -- heykel/uretim/hunyuan21.glb heykel/uretim/hunyuan21   # GLB -> .blend, ölçek/merkez
blender -b -P heykel/b_hazir.py                                                        # çalışma ağı + önden kil render
python heykel/noktalar.py                                                              # hy-noktalar.json (yüz modeli otomatik iner)
blender -b -P heykel/tripo/t_hazir.py -- tripo-yuz.glb                                 # Tripo -> tp.blend + önden render
cd heykel/tripo && python nokta.py tp-on.png tp-on.json tp-noktalar.json && cd ../..
blender -b -P heykel/tripo/t_nakil2.py                                                 # Tripo yüzü + Hunyuan kafatası -> nakil2.blend
blender -b -P heykel/tripo/t_gelistir.py                                               # gerçek göz, kaş, ten, malzeme -> renkli.blend
```

## 4. Sahne ve ürünler

```bash
cd blender
blender -b -P b_govde.py      # kürsü gövdesi temizlik + ölçek -> ata-govde.blend
blender -b -P b_kursu.py      # ceviz kürsü, bayrak, perde, ışık -> kursu.blend
blender -b -P b_sahne.py      # set + gövde + baş -> sahne.blend
blender -b -P b_yuz_anim.py   # göz kırpma, ağız -> sahne_anim.blend
blender -b -P b_film.py       # kamera planları K1–K5 + son -> film_kursu.blend
for s in togg baykar tusas tb3 marti uzay; do blender -b -P s_$s.py; done   # ürün sahneleri -> sahne_<ad>.blend
```

Marka logoları (`logo/*.png`) ve Dünya dokusu (`logo/dunya-8k.jpg`, ör. [Solar System Scope](https://www.solarsystemscope.com/textures/), CC BY 4.0) repoda yok. Logo dosyası yoksa sahne logosuz kurulur.

## 5. Render ve birleştirme

```bash
bash blender/render_kuyruk.sh      # TEK SIRA; kare/<plan>/####.png; yarıda kalırsa kaldığı yerden devam eder
python film_birlestir.py --onizle  # yalnız kontrol kareleri
python film_birlestir.py           # film-tam.mp4
python ../../araclar/teslim_denetim.py film-tam.mp4 zaman.json pano.jpg
```

Kapanış şarkısı telifli olduğu için repoda yok. Kendi şarkını `QANAT_SARKI=şarkı.mp3` ve başlangıç saniyesini `QANAT_SARKI_BAS=183` ile ver. Verilmezse `miks.wav`'ın sentez kapanışı kullanılır.

## Bu filmden dersler

`skills/reels-blender-film/SKILL.md` → "Dersler" bölümü.
