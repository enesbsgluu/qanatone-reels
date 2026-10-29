# QANATONE Reels · yapay zekâ ile kodla video stüdyosu

Instagram'da izlediğin QANATONE reels'leri (low-poly skeçler, dizi bölümleri, meme uyarlamaları, 29 Ekim Onuncu Yıl filmi) kamerayla değil **kodla** çekildi. Bu repo o hattın tamamıdır: senaryo yöntemi, seslendirme, 3B ve 2B sahne kurulumu, kare kare çekim, teslim denetimi, büyüme stratejisi.

Repo bir **yetenek paketi** olarak yazıldı. Claude Code'a (ya da başka bir kod ajanına) verdiğinde "usta-çırak tarzında, kahvenin gizli tarihini anlatan 70 saniyelik bir video yap" gibi bir isteği hangi sırayla, hangi kurallarla, hangi araçla yapacağını bilir.

| | |
|---|---|
| `ornekler/2b-usta-cirak` | 2B çizim: gece çatı, tilki usta + köpek çırak, Gemini sesiyle (tamamen kodla çizilir) |
| `ornekler/3b-baslangic` | 3B low-poly: iki karakter, oda, plan kesmeleri |
| `ornekler/onuncu-yil` | Blender: fotoğraftan 3B Atatürk, kürsü sahnesi, 6 ürün sahnesi, 29 Ekim filmi |

## Kurulum

Gerekenler: [Node.js 20+](https://nodejs.org), [ffmpeg](https://ffmpeg.org/download.html), [Python 3.10+](https://python.org). Ses için ücretsiz bir [Gemini API anahtarı](https://aistudio.google.com/apikey).

```bash
git clone https://github.com/enesbsgluu/qanatone-reels.git
cd qanatone-reels
npm install
pip install -r requirements.txt
npm run cek:2b      # ornekler/2b-usta-cirak/cikti/sahne.mp4
```

### Claude Code ile

**Yol 1 (önerilen):** repoyu klonla, klasörde `claude` çalıştır. `CLAUDE.md` yetenekleri otomatik tanıtır. Sonra isteğini yaz:

> usta-çırak tarzında, Coca-Cola'nın ilk reklamlarının gizli hikâyesini anlatan 70 saniyelik bir 2B video yap

**Yol 2:** yetenekleri her projede kullanmak için eklenti olarak kur:

```
/plugin marketplace add enesbsgluu/qanatone-reels
/plugin install qanatone-reels@qanatone-reels
```

Araçlar (`araclar/`) ve örnekler bu repoda durduğu için video çekerken repoyu yine de klonlamış olman gerekir.

### Başka bir yapay zekâ ile

Repoyu (ya da zip'ini) yükle ve şunu yaz: *"AGENTS.md dosyasını oku, oradaki skill'leri izleyerek benim için şu videoyu yap: …"*. Cursor, Codex, Gemini CLI gibi kod ajanları dosyaları okuyup komutları çalıştırabildiği için hattı uçtan uca yürütür. Yalnız sohbet eden araçlar senaryo ve sahne kodunu yazar, komutları sen çalıştırırsın.

## Hat

```
senaryo  →  ses (Gemini TTS)  →  zamanlama (Whisper)  →  sahne (three.js / canvas / Blender)  →  kare kare çekim  →  teslim denetimi
  onay        dinleme onayı         otomatik                 önizleme panosu onayı                  cek.mjs           teslim_denetim.py
```

Sahne zamanın saf fonksiyonudur: `kare(t)` aynı saniye için hep aynı kareyi verir. Bir hatayı düzeltince yalnız o saniyeler yeniden çekilir, hiçbir şey kaymaz.

## Yetenekler (`skills/`)

| Skill | İçerik |
|---|---|
| reels-uretim | giriş kapısı: tür seçimi, hat sırası, onay kapıları |
| reels-senaryo | kanca, sahne kartı, diyalog kuralları, mantık zinciri, klişe süzgeci, usta-çırak formatı |
| reels-ses | Gemini TTS, kelime zamanı, Demucs ayrımı, temizlik, konuşmacı ölçümü, miks |
| reels-3b-sahne | three.js set/karakter/ışık/kamera, fizik kuralları, titreme ve kara blok tuzakları |
| reels-2b-cizim | canvas kesik-parça karakter, paralaks, noir palet |
| reels-meme-uyarlama | bilinen sahneyi AI/marka karakterleriyle birebir yeniden çekmek |
| reels-blender-film | fotoğraftan 3B (ücretsiz Hugging Face), yüz nakli, Blender betikli film |
| reels-teslim | Instagram dosya standardı, otomatik denetim, altyazı yerleşimi |
| reels-buyume | kapak, açıklama kalıbı, yorum→DM hunisi, ritim, ölçüm |

## Araçlar (`araclar/`)

| Araç | Ne yapar |
|---|---|
| `cek.mjs <klasör> [--onizle] [--sure s] [--bas s] [--ses ses.wav]` | sahneyi kare kare çeker, 1080×1920 30 fps MP4 |
| `seslendir.py <klasör> [satır]` | senaryo.json'u seslendirir, zamanları gerçek sesten yazar |
| `kelime_zamani.py ses.wav kelime.json` | kelime düzeyinde zaman (Whisper large-v3) |
| `ses_temizle.py girdi.wav cikti.wav` | gürültü azaltma + EQ + −14 LUFS |
| `konusmaci.py vocals.wav referans.json` | repliğin kime ait olduğunu sesten ölçer |
| `teslim_denetim.py video.mp4 [senaryo.json] [pano.jpg]` | boyut/fps/SAR/ses düzeyi/kara blok/titreme denetimi |

## Telif

Kod MIT lisanslıdır. Referans ses/görüntü, şarkılar, marka logoları ve yapay zekâ ile üretilmiş 3B modeller repoda yok. Betikler bunları yerelde üretir ya da senden ister. Kendi videolarında kullandığın kaynakların haklarına dikkat et.

---

Yapılan işler ve sorular için: [@qanatone](https://www.instagram.com/qanatone/) · [qanatone.com](https://www.qanatone.com/?utm_source=github&utm_medium=readme)
