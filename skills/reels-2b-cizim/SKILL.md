---
name: reels-2b-cizim
description: Kodla 2B çizim/illüstrasyon reels — canvas veya SVG ile kesik-parça (cutout) karakter animasyonu, paralaks arka plan, usta-çırak (tilki/kurt noir tarzı) ders videoları. 2B karakter, çizgi film, illüstrasyon video, hayvan karakterli ders videosu yaparken kullan. Also use for 2D animated explainers, cutout character animation, or fox/wolf mentor-style videos.
---

# 2B çizim sahnesi

Başlangıç: `ornekler/2b-usta-cirak` (gece çatı, tilki usta + köpek çırak). Aynı sözleşme: `window.kare(t)` + `window.hazir`, çekim `node araclar/cek.mjs <klasör>`. Görsel üretici gerekmez; her şey yol (path) ve şekillerle çizilir, böylece karakter her karede aynıdır ve telif sorunu yoktur.

## Adımlar

1. **Kendi karakterini tasarla.** Bir tarzı kopyalama, kalıbı al: başarılı usta-çırak videolarının gücü karakterin değil formatın (bilge usta, izleyicinin vekili çırak, gerçek vaka, kameraya imza cümlesi). Silueti tek bakışta okunan, 2–3 ana renkli, biri sıcak biri soğuk iki karakter seç. Renkleri `RENK` sözlüğünde topla.
2. **Parçalara böl.** Her karakter pivotlu parçalardan oluşur: gövde → baş (boyunda döner) → kulak, göz, kaş, ağız; kol omuzdan, kuyruk kökünden döner. Her parça `c.save(); c.translate(pivot); c.rotate(açı); ... c.restore()` ile çizilir.
3. **Canlılık ekle.** Nefes (gövdede yavaş sinüs), göz kırpma (3–4 sn'de bir, 0,12 sn), kuyruk/kulak salınımı, konuşurken ağız (ses varsa genlik zarfından, yoksa hece ritminden), duyguyu kaş taşır. Tüm salınımlar `t`'den hesaplanır, fazları karakter başına farklıdır.
4. **Arka planı katmanla.** Gök → uzak şehir → orta (çatı, lamba) → karakterler → ön (yağmur) → kenar kararması. Paralaks: uzak katman kamera hareketinden az etkilenir (`para` 0,15–0,45).
5. **Planları yaz.** Kamera = canvas dönüşümü (ölçek + öteleme). Plan içinde yavaş itme (%3–4/sn), kesme senaryodan. Son plan: usta kameraya döner ve imza cümlesini söyler.
6. **Pano + onay**, sonra çekim (reels-3b-sahne ile aynı süreç).

## Fizik

Oturan karakterin kalçası oturağa, ayakları zemine basar; el bedene bağlıdır (kol pivotundan), havada kopuk parça olmaz. Gölge elipsi her karakterin altında durur. Bakış konuşana döner.

## Tarz notları

- Noir gece paleti: koyu lacivert gök, sıcak sarı pencere ve lamba ışığı, tek vurgu rengi (ör. kızıl kravat).
- Altyazı stil sistemi: tek yazı tipi (Inter 600), koyu yarı saydam kutu, beyaz, ortalı; italik ve ikinci yazı tipi yok.
- Daha "el çizimi" his için: kenara 1–2 px koyu kontur, kâğıt grenli doku katmanı, hafif titreyen çizgi (tohumla, kare başına değil 4 karede bir değişen).
