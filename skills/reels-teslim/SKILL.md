---
name: reels-teslim
description: Reels teslim ve yayın öncesi denetim — Instagram/TikTok dosya standardı, SAR/fps/ses düzeyi, titreme ve kara blok taraması, kontak tabakası, altyazı yerleşimi, kurgu katmanları. Video bitince, "teslim et", "yayına hazırla", "kalite kontrol", "Instagram bozuk yüklüyor" dendiğinde kullan. Also use before delivering or publishing any short video.
---

# Teslim

## Adımlar

1. **Denetimi koş:** `python araclar/teslim_denetim.py video.mp4 [senaryo.json] [pano.jpg]`. Ölçer: 1080×1920, 30 fps sabit, SAR 1:1 (eksikse kayıpsız yazar, görüntü md5'i eşit kalır), süre, ses var mı, −14 LUFS ve tepe, kara blok, tek karelik titreme, 12 karelik kontak tabakası.
2. **Gözle bak:** kontak tabakası + açılış ve kapanış kareleri. Altyazı Reels arayüzünün altında kalmıyor mu, yüzleri örtüyor mu?
3. **Ses ile görüntü senkronu:** satır başlarında ağız hareketi ile ses başlangıcı arasındaki fark ortalama ≤ 0,1 sn.
4. *Bitti:* denetim "SORUN: yok" der, kontak tabakası temiz, dosya adı içeriği anlatıyor (`marka-konu-TR-1080x1920.mp4`).

## Dosya standardı (Instagram Reels)

1080×1920 · 30 fps sabit · H.264 High · yuv420p · BT.709 · SAR 1:1 · GOP 2 sn · faststart · AAC 48 kHz · −14 LUFS (−15,5…−12,5) · gerçek tepe ≤ −1,5 dBTP · ~8–11 Mbps.

Kayıpsız etiket düzeltmesi:
```bash
ffmpeg -i in.mp4 -map 0 -c copy -bsf:v h264_metadata=sample_aspect_ratio=1/1:video_full_range_flag=0:colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1 -movflags +faststart out.mp4
```

Yükleme: telefona dosyayı indir (Drive'dan doğrudan paylaşım yeniden sıkıştırır), Instagram → Ayarlar → Medya kalitesi → "En yüksek kalitede yükle" açık; uygulama içinde kırpma/filtre yok.

## Kurgu katmanları

Uzun işte görüntü, altyazı ve ses ayrı katmandır: altyazısız "plaka" bir kez çekilir, düzeltme gereken saniyeler `--bas/--sure` ile parça olarak yeniden çekilir, altyazı ve ses son birleştirmede bindirilir. Altyazı düzeltmesi yeniden çekim gerektirmez. `zaman.json` değiştiyse miks de yeniden üretilir.

## Altyazı

Tek yazı tipi (Inter 600), beyaz, koyu yarı saydam yuvarlak kutu, ortalı. Alt kenar ekranın ~%77'sinde (y≈1480), genişlik ≤ 860 px: Reels'in alt arayüzü ~420 px, sağ sütun düğmeleri yer kaplar. Vurgu renkle verilir, italikle verilmez.
