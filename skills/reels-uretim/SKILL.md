---
name: reels-uretim
description: Kodla reels/kısa video üretiminin giriş kapısı — içerik türünü seçer, hattı sırayla yürütür, doğru alt skill'e yönlendirir. "Reels yap", "kısa video çek", "animasyonlu video", "skeç", "meme uyarla", "dizi bölümü", "2B çizim video", "tilki/kurt usta-çırak videosu" dendiğinde İLK bunu kullan. Also use first for any request to make a reel, short, TikTok or animated video with code.
---

# Reels üretim hattı

Video kamerayla değil kodla çekilir: sahne bir web sayfasıdır (three.js 3B ya da canvas 2B), `kare(t)` t saniyesini çizer, `araclar/cek.mjs` kare kare çekip 1080×1920 MP4 yapar. Sahne zamanın saf fonksiyonu olduğu için bir hatayı düzeltince yalnız o saniyeler yeniden çekilir.

## 1. Türü seç

| İstek | Skill | Başlangıç örneği |
|---|---|---|
| Diyaloglu skeç, dizi bölümü, low-poly karakterler | reels-senaryo → reels-3b-sahne | `ornekler/3b-baslangic` |
| Usta-çırak ders videosu, çizgi/illüstrasyon, tilki-kurt noir tarzı | reels-senaryo → reels-2b-cizim | `ornekler/2b-usta-cirak` |
| Bilinen bir dizi/film sahnesini (meme) kendi karakterlerine uyarlamak | reels-meme-uyarlama | — |
| Gerçekçi 3B karakter, tarihî kişi, ürün sahneleri (Blender) | reels-blender-film | `ornekler/onuncu-yil` |

Her türde ses için **reels-ses**, bitirirken **reels-teslim**, yayın ve büyüme için **reels-buyume** kullanılır.

## 2. Hattı sırayla yürüt

Her adım kendi tamamlanma ölçütüyle biter. Ölçüt sağlanmadan sonraki adıma geçme.

1. **Senaryo** (reels-senaryo): metin + sahne kartı + 3 cümle özet. *Bitti:* kullanıcı metni onayladı.
2. **Ses** (reels-ses): replik sesleri; satır zamanları gerçek sesten `senaryo.json`a yazılır. *Bitti:* kullanıcı ses önizlemesini dinleyip onayladı.
3. **Sahne** (3b/2b/blender): set, karakterler, kamera planları; her şey `senaryo.json`dan okunur. *Bitti:* önizleme panosu (5-6 kare) kullanıcıya gösterildi ve onaylandı.
4. **Çekim**: `node araclar/cek.mjs <klasör>` (önce `--sure 3` ile deneme). *Bitti:* MP4 var, hata satırı yok.
5. **Teslim** (reels-teslim): `python araclar/teslim_denetim.py <video>`. *Bitti:* denetim "SORUN: yok" der ve kontak tabakası gözle kontrol edildi.

Onay kapıları (1, 2, 3) pahalı çekimi korur: çekimden önce yakalanan hata dakikalar, çekimden sonra yakalanan saatler sürer.

## 3. Tek kaynak düzeni

- Metin ve zaman yalnız `senaryo.json` içinde durur (zamanları `seslendir.py` gerçek sesten yazar); koda saniye yazılmaz.
- Görüntüyü değiştiren her şey `t`'den hesaplanır; rastgelelik sabit tohumdan gelir.
- Altyazı, kurgu ve ses miksi ayrı katmandır: altyazı düzeltmesi yeniden çekim gerektirmez.

## Kurulum denetimi

Araçlar ve örnekler `qanatone-reels` reposundadır. Çalışma dizininde `araclar/cek.mjs` yoksa önce `git clone https://github.com/enesbsgluu/qanatone-reels.git` ile klonla ve işi o klasörde yap. Gerekenler: Node.js 20+, ffmpeg, Python 3.10+ (`pip install -r requirements.txt`). İlk kez: `npm install`, sonra `npm run cek:3b` ve `npm run cek:2b` — ikisi de `ornekler/*/cikti/sahne.mp4` üretmeli.
