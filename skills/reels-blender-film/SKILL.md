---
name: reels-blender-film
description: Blender ile gerçekçi 3B kısa film hattı — tek fotoğraftan 3B model (Hunyuan3D/TRELLIS, ücretsiz HF), yüz nakli, sahne betikleri, ürün/araç sahneleri, render kuyruğu, kare birleştirme. Tarihî kişi canlandırma, gerçekçi karakter, ürün tanıtım sahnesi, Blender betikli film için kullan. Also use for photo-to-3D characters and scripted Blender video pipelines.
---

# Blender film hattı

Çalışan örnek: `ornekler/onuncu-yil` (Atatürk · Onuncu Yıl Nutku, 29 Ekim filmi). Adım adım kurulum ve komutlar o klasörün `README.md` dosyasında. Her betik Blender'da arka planda koşar: `blender -b -P betik.py`. Ara çıktı `.blend` dosyalarıdır; her aşama bir öncekini açar, işini yapar ve yenisini kaydeder.

## Hat

1. **Kaynak** (`kaynak/indir.sh`): ses/görüntü yt-dlp ile indirilir, kesit alınır.
2. **Ses**: Demucs ayrımı + temizlik → `ses-temiz.wav`; kelime zamanları → `iyi-kelime.json`; `zaman.py` → `zaman.json` (satırlar, sahne sırası).
3. **3B üretim** (`heykel/uretim/uret.py`): fotoğraftan GLB, ücretsiz Hugging Face Space'leriyle (Hunyuan3D-2.1, TRELLIS.2). Baş/büst ve kürsü gövdesi ayrı üretilir.
4. **Yüz** (`heykel/`, `heykel/tripo/`): MediaPipe 478 nokta ile iki model hizalanır; ayrıntılı yüz (Tripo) korunur, kafatası/saç başka modelden nakledilir; gerçek göz (kornea + iris), kaş, ten → `renkli.blend`.
5. **Sahne** (`blender/b_*.py`): gövde → set (kürsü, bayrak, perde, ışık) → baş takılır → yüz canlılığı (göz kırpma, ağız) → kamera planları (`b_film.py`).
6. **Ürün sahneleri** (`blender/s_*.py` + `m_*.py` + `urun_ortak.py`): her ürün kendi `.blend` sahnesi.
7. **Render** (`blender/render_kuyruk.sh`): TEK SIRA, var olan kare atlanır (kaldığı yerden devam).
8. **Birleştirme** (`film_birlestir.py`): kareler + altyazı + marka etiketi + renk/gren + kapanış kartı + ses → MP4. `--onizle` ile yalnız kontrol kareleri.

## Dersler

- **Gerçek kişi benzerliği ölçülür:** referans fotoğraflarla model render'ı MediaPipe oranlarıyla (yüz en/boy, çene, ağız, göz yarığı, kaş-göz) karşılaştır; görünüm arası ~%5 gürültüdür.
- **Saydam kornea** EEVEE'de opak çizilebilir (gri iris); göz yakın planlarında Cycles kullan ya da korneayı BLENDED + düşük alfa yap.
- **glTF içe aktarımı** kuaterniyon döndürme modunda gelir; `rotation_euler` etkisizdir, matrisle döndür.
- **Yeni eklenen nesne:** `view_layer.update()` çağrılmadan `matrix_world` birim matris döner.
- **Hazır frak/giysi modelleri** çoğu zaman iskeletlenemez (kollar gövdeye kaynaşık). Kürsü/oturan gibi poz gerektiren gövdeyi doğrudan o pozdaki fotoğraftan üret.
- **Ses hizası:** temiz ses film zamanına hizalı tutulur; kelime zamanı dosyasının ofseti yalnız o dosya içindir. Vurgu anlarında enerji ölçerek doğrula.
- **Satır sonu yorumu:** Python'da `;` ile birleştirilmiş satırlarda `#` sonrası her şey yorumdur. Birleşik satırlara yorum ekledikten sonra yorumun kodu yutmadığını tara.
- **Telif:** referans ses/görüntü, şarkı ve üretilmiş modeller repoya konmaz; betikler bunları yerelde üretir ya da kullanıcıdan alır.
