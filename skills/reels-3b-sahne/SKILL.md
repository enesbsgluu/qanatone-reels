---
name: reels-3b-sahne
description: three.js ile low-poly 3B reels sahnesi kurma — set, karakter, ışık, kamera planları, ağız/göz animasyonu, kare kare çekim. 3B sahne, low-poly karakter, oda/set, kamera hareketi kurarken ya da 3B çekimde titreme, kara blok, fizik hatası düzeltirken kullan. Also use for building or fixing a three.js scene for a short video.
---

# 3B sahne (three.js)

Başlangıç: `ornekler/3b-baslangic` klasörünü kopyala. Sözleşme: `index.html` + `senaryo.json`; sayfa hazır olunca `window.hazir = true`, `window.kare(t)` t saniyesini çizer. Çekim: `node araclar/cek.mjs <klasör>`.

## Adımlar

1. **Seti kur.** Bir genel plan ortamın tamamını gösterir. Premium çıta: dokulu malzeme (ahşap damarı, kumaş, taş), en az 3 ışık (anahtar + sıcak/soğuk dolgu + pratik ışık: lamba, ekran), atmosfer (sis, toz, yağmur), ön–orta–arka katman.
2. **Karakterleri kur.** Yüz okunur olmalı: göz akı + bebek, duygu taşıyan kaş, sese göre açılıp kapanan ağız. Marka/AI karakteri baştan ayağa marka diliyle tasarlanır (renk, malzeme, siluet, rozet); yalnız logoya göz çizmek yetmez. Seride yerleşik karakter önceki videodaki modelin birebir kopyasıdır, yeni takı eklenmez.
3. **Planları yaz.** Kesme `senaryo.json`'daki `planlar`dan gelir; plan içinde yalnız yavaş itme/kaydırma. Konuşan belli olur, dinleyen konuşana döner; tepki planında kamera bakış çizgisi üzerindedir (yüz görünür, profil değil).
4. **Önizleme panosu.** 5–6 kritik anı kareye çıkar (`--bas t --sure 0.04`), gerekiyorsa referans karelerle yan yana koy, kullanıcıya göster. *Bitti:* kullanıcı onayladı.
5. **Çek.** Önce `--sure 3`, sonra tamamı. Uzun filmde 6 sn'lik parçalar `--bas` ile sırayla çekilir.

## Fizik ve süreklilik (her önizlemede kontrol)

- Ölçek yüzeye sığar; her ayak/taban bir yüzeye basar; uzuv mobilyanın içinden geçmez.
- Karakter geldiği yönden çıkar ve kadraj dışında kaybolur. Yürüyüşte adım ile mesafe kilitlidir; yerinde dönme yürürken yay üstünde olur.
- Planlar arası mekân sürekliliği kurgu sırasına göre kurulur.

## Zamanın saf fonksiyonu

Görüntüyü değiştiren her şey `kare(t)` içinde `t`'den hesaplanır. Rastgelelik sabit tohumdan: `tohum(n)`. Birikimli durum (`x += hız`) çekim parçaları arasında sıçrama yaratır.

## Bilinen tuzaklar

- **Parça ilk kare sekmesi:** kamera, karakter pozu güncellenmeden hesaplanırsa yeni parçanın ilk karesi önceki pozu kullanır. `cek.mjs` bir önceki kareyi ısıtma olarak çizer; kendi çekicini yazarsan aynısını yap. Kamera hesabını poz güncellemesinden sonra yap.
- **Aralıklı kara blok:** tek NaN piksel DOF/bloom geçişlerinde dikdörtgene yayılır. Son işleme zincirine NaN temizleyici geçiş koy. ANGLE/D3D `isnan()`'ı derleyicide eler; NaN'ı `floatBitsToUint` ile üs bitlerinden ve `abs(c) > 6e4` ile yakala.
- **Saydam katman + DOF:** cam/yağmur gibi saydam nesneler derinlik geçişinden çıkarılmazsa arkası bulanıklaşır.
- **Paralel çekim:** tek GPU'da birden çok WebGL çekimi sürücü çökmesine (TDR) yol açar. Çekimleri tek sıra koş, çekim sürerken önizleme açma. Yarım kalan MP4'leri (moov yok, birkaç bayt) silip yeniden çek.
- **Satır sonu yorumu:** `// yorum` aynı satırdaki sonraki komutu yutar. Bir satıra birden çok komut yazıyorsan yorumu en sona koy ya da `/* */` kullan.
