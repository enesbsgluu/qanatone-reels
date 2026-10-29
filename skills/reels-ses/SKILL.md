---
name: reels-ses
description: Reels sesi — Türkçe TTS seslendirme, kelime zamanı ve satır zamanlaması, ses ayırma/temizleme, konuşmacı doğrulama, miks ve ses düzeyi. Seslendirme, replik sesi, dublaj, altyazı zamanlaması, müzik/efekt miksi, gürültü temizliği veya "bu replik kimin" sorusu için kullan. Also use for voiceover, TTS, word timings, audio cleanup, speaker identification or mixing.
---

# Reels sesi

Zamanlamayı gerçek ses belirler: önce ses üretilir, sonra satır başlangıçları sesten ölçülüp `senaryo.json`'a yazılır. Sahne yalnız bu dosyadan okur.

## Adımlar

1. **Senaryoya ses bilgisini ekle.** `senaryo.json`'a `karakterler` (her biri için Gemini ses adı + kısa tarif: yaş, tını, tavır) ve satırlara `ton` yaz. Ton yönergesi isteğe ayrı eklenir, satır metninin içine yazılmaz.
2. **Üret ve hizala:** `python araclar/seslendir.py <klasör>`. Satırlar en fazla 2 konuşmacılı gruplar hâlinde tek istekte üretilir (karakterler birbirine cevap verir, tonlama doğal akar), Whisper kelime zamanlarıyla satırlara bölünür, her satır iki satır arasındaki en sessiz noktadan kesilir, düzey eşitlenir. Çıktı `ses.wav`; `senaryo.json`'daki `bas/bit/sure` gerçek sesten yeniden yazılır (`planlar`da `"satir": n` olan kesme o satıra taşınır). Konsoldaki "duyulan" sütununu metinle karşılaştır. Anahtar `GEMINI_API_KEY`; ücretsiz kota günde ~10 istek.
3. **Bozuk satırı tek başına yenile:** `python araclar/seslendir.py <klasör> 4` (yalnız 4. satırın grubu yeniden üretilir). Satır sonunu dalga biçiminde kontrol et: Whisper kelime sonunu erken düşürür, araç +0,25 sn pay bırakır.
4. **Dinlet.** Ses önizlemesini (m4a) kullanıcıya sun. *Bitti:* kullanıcı onayladı. Bundan sonra çekime geçilir.
5. **Miks.** Ortam sesi, efektler (tık, bildirim, yudum), konuşmada otomatik kısılan (sidechain) arka ses. Müzik genelde yalnız kapanış kartında. Zamanlar değiştiyse miksi yeniden üret; eski miks eski zamanlamayı basar.

## Telaffuz

- İngilizce anadilli hazır sesler Türkçeyi yabancı aksanla okur; Türkçe destekleyen modeli seç (Gemini TTS iyi sonuç verir).
- Rakamları yazıyla ver ("1912" → "bin dokuz yüz on iki"); marka adlarının okunuşunu yönergede belirt.
- Kısa replik şüpheli çıkarsa (yarım, yanlış kişi, uydurma ek cümle) yalnız o satırı yeniden üret.

## Uyarlama (meme) sesi

- **Ayır:** `demucs -n htdemucs_ft --two-stems vocals girdi.wav` → konuşma ile müzik ayrılır.
- **Temizle:** `python araclar/ses_temizle.py vocals.wav temiz.wav` (gürültü azaltma + EQ + −14 LUFS).
- **Kelime zamanı:** `python araclar/kelime_zamani.py temiz.wav kelime.json` (faster-whisper large-v3; `[[kelime, bas, bit], ...]`).
- **Konuşmacıyı ölç, tahmin etme:** `python araclar/konusmaci.py vocals.wav referans.json [satirlar.json]`. Konuşan çoğu zaman ekranda değildir (tepki planı üstüne ses). Fark zayıfsa (<~1) o aralığın ağız bölgesini kare kare kontrol et: ağzı oynayan konuşandır. Ölçüm tahmini yener, ağız ölçümü yener.

## Ses düzeyi

Teslimde −14 LUFS (−15,5…−12,5 aralığı), gerçek tepe ≤ −1,5 dBTP. Denetimi reels-teslim yapar.
