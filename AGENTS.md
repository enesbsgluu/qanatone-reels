# Bu repo ne

Kodla kısa video (Instagram Reels, TikTok, Shorts) üretim stüdyosu. Sahne bir web sayfasıdır (three.js 3B ya da canvas 2B), `araclar/cek.mjs` onu kare kare çekip 1080×1920 MP4 yapar. Ses Gemini TTS ile üretilir, zamanlama gerçek sesten ölçülür. Gerçekçi işler için Blender hattı vardır.

# Bir video isteği geldiğinde

1. `skills/reels-uretim/SKILL.md` dosyasını oku: tür seçimi, hat sırası ve onay kapıları orada.
2. Türe göre ilgili skill'i oku ve adımlarını sırayla uygula:

| Skill | Ne zaman |
|---|---|
| `skills/reels-senaryo/SKILL.md` | senaryo, diyalog, bölüm taslağı |
| `skills/reels-ses/SKILL.md` | seslendirme, kelime zamanı, ses temizliği, konuşmacı ölçümü, miks |
| `skills/reels-3b-sahne/SKILL.md` | three.js low-poly sahne, karakter, kamera |
| `skills/reels-2b-cizim/SKILL.md` | canvas/SVG 2B çizim, usta-çırak (tilki/kurt) tarzı |
| `skills/reels-meme-uyarlama/SKILL.md` | bilinen bir sahneyi kendi karakterleriyle yeniden çekmek |
| `skills/reels-blender-film/SKILL.md` | fotoğraftan 3B, gerçekçi karakter, Blender betikli film |
| `skills/reels-teslim/SKILL.md` | yayın öncesi denetim, dosya standardı |
| `skills/reels-buyume/SKILL.md` | kapak, açıklama, yorum→DM hunisi, yayın ritmi |

3. Yeni video için bir örneği kopyalayarak başla: `ornekler/3b-baslangic`, `ornekler/2b-usta-cirak` ya da `ornekler/onuncu-yil`.

# Doğrulama

- Sahne değişikliğinden sonra: `node araclar/cek.mjs <klasör> --sure 3` ve birkaç kareye bak (`ffmpeg -ss 1 -i <klasör>/cikti/sahne.mp4 -frames:v 1 kare.png`). Sayfa hatası terminale "sayfa hatası" diye düşer.
- Teslimden önce: `python araclar/teslim_denetim.py <video> <senaryo.json> pano.jpg` "SORUN: yok" demeli.
