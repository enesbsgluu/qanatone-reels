// Bir tarayıcı sahnesini kare kare çeker ve ffmpeg ile 1080x1920, 30 fps MP4 yapar.
// Sahne sözleşmesi: <klasör>/index.html + senaryo.json ("sure"); sayfa hazır olunca window.hazir = true,
// window.kare(t) t saniyesini çizer (async olabilir). 3B (three.js) ve 2B (canvas/SVG) sahneler aynı sözleşmeyi kullanır.
//   node araclar/cek.mjs <klasör>                 -> <klasör>/cikti/sahne.mp4
//   node araclar/cek.mjs <klasör> --onizle        -> tarayıcıda canlı önizleme adresi verir
//   node araclar/cek.mjs <klasör> --sure 3        -> yalnız ilk 3 saniye (hızlı deneme)
//   node araclar/cek.mjs <klasör> --bas 12        -> 12. saniyeden başlar (parça çekimi)
//   node araclar/cek.mjs <klasör> --ses ses.wav   -> sesi videoya ekler
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const KOK = path.resolve(process.argv[2] && !process.argv[2].startsWith('--') ? process.argv[2] : '.');
if (!fs.existsSync(path.join(KOK, 'index.html'))) { console.error('Sahne klasörü bulunamadı (index.html yok):', KOK); process.exit(1); }
const arg = (ad, vars) => { const i = process.argv.indexOf(ad); return i < 0 ? vars : process.argv[i + 1]; };
const FPS = 30;

// Modüller file:// üzerinden yüklenmediği için küçük bir yerel sunucu
const TUR = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml', '.jpg': 'image/jpeg', '.wav': 'audio/wav', '.css': 'text/css', '.glb': 'model/gltf-binary' };
const sunucu = http.createServer((q, y) => {
  const yol = path.join(KOK, decodeURIComponent(new URL(q.url, 'http://x').pathname).replace(/\/$/, '/index.html'));
  if (!yol.startsWith(KOK) || !fs.existsSync(yol)) { y.writeHead(404); return y.end(); }
  y.writeHead(200, { 'Content-Type': TUR[path.extname(yol)] || 'application/octet-stream' });
  fs.createReadStream(yol).pipe(y);
});
await new Promise((ok) => sunucu.listen(0, '127.0.0.1', ok));
const ADRES = `http://127.0.0.1:${sunucu.address().port}/`;

if (process.argv.includes('--onizle')) {
  console.log('Önizleme:', ADRES, '(kapatmak için Ctrl+C)');
} else {
  const { default: puppeteer } = await import('puppeteer');
  const senaryo = JSON.parse(fs.readFileSync(path.join(KOK, 'senaryo.json'), 'utf8'));
  const bas = Number(arg('--bas', 0));
  const sure = Number(arg('--sure', senaryo.sure - bas));
  const ses = arg('--ses', null);
  fs.mkdirSync(path.join(KOK, 'cikti'), { recursive: true });
  const cikti = path.join(KOK, 'cikti', 'sahne.mp4');

  const tarayici = await puppeteer.launch({ headless: true, args: ['--use-angle=default', '--enable-unsafe-swiftshader'] });
  const s = await tarayici.newPage();
  await s.setViewport({ width: 1080, height: 1920, deviceScaleFactor: 1 });
  s.on('pageerror', (e) => console.error('sayfa hatası:', e.message));
  await s.goto(ADRES + '?cekim', { waitUntil: 'networkidle0' });
  await s.waitForFunction('window.hazir === true', { timeout: 30000 });

  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    ...(ses ? ['-ss', String(bas), '-i', ses, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-ac', '2', '-c:a', 'aac', '-b:a', '256k', '-shortest'] : []),   // ses Instagram düzeyine (−14 LUFS)
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', String(FPS), '-g', String(FPS * 2),
    '-bsf:v', 'h264_metadata=sample_aspect_ratio=1/1', '-movflags', '+faststart', cikti],
    { stdio: ['pipe', 'inherit', 'inherit'] });

  const toplam = Math.round(sure * FPS);
  // ısıtma karesi: ilk karede gölge haritası ve kamera henüz oturmamış olabilir (titreme önlemi)
  // parça ortadan başlıyorsa bir önceki kare de çizilir: kamera/poz durumu oturur, ilk karede sekme olmaz
  await s.evaluate((t) => window.kare(t), Math.max(0, bas - 1 / FPS));
  for (let i = 0; i < toplam; i++) {
    await s.evaluate((t) => window.kare(t), bas + i / FPS);
    const kare = await s.screenshot({ type: 'png', clip: { x: 0, y: 0, width: 1080, height: 1920 } });
    if (!ff.stdin.write(kare)) await new Promise((ok) => ff.stdin.once('drain', ok));
    if (i % FPS === 0) process.stdout.write(`\r${(i / FPS).toFixed(0)} / ${sure} sn`);
  }
  ff.stdin.end();
  await new Promise((ok, red) => ff.on('close', (c) => (c === 0 ? ok() : red(new Error('ffmpeg çıkış ' + c)))));
  await tarayici.close();
  sunucu.close();
  console.log('\nHazır:', path.relative(process.cwd(), cikti));
}
