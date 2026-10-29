// 2B usta-çırak sahnesi: gece çatı, şehir silueti, yağmur; takım elbiseli tilki usta + kapüşonlu genç köpek çırak.
// Her şey kodla çizilir (canvas 2D, kesik-parça / cutout animasyon). Görsel üretici yok, telif yok.
// Her şey zamanın saf fonksiyonu: kare(t) aynı t için hep aynı görüntüyü verir (rastgelelik sabit tohumdan).
const G = 1080, Y = 1920;
const S = await (await fetch('./senaryo.json')).json();
const cekim = new URLSearchParams(location.search).has('cekim');

const kap = document.getElementById('kap');
const yazi = document.querySelector('#altyazi span');
const tuval = document.createElement('canvas'); tuval.width = G; tuval.height = Y; kap.prepend(tuval);
const c = tuval.getContext('2d');

// ---- yardımcılar ----
const tohum = (n) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };   // sabit sözde rastgele
const yumusak = (x) => { x = Math.min(1, Math.max(0, x)); return x * x * (3 - 2 * x); };
const RENK = { gok1: '#0d1117', gok2: '#2a1c2c', ay: '#f3e6c4', bina: '#141820', pencere: '#f3cf72', cati: '#1d2129',
  tilki: '#d9682b', tilkiKoyu: '#a8461b', beyaz: '#f4ede1', takim: '#23262e', takimKoyu: '#171a20', kravat: '#ef233c',
  kopek: '#c9a27a', kopekKoyu: '#8f6b4b', kapusonlu: '#4a5a6e', kapusonluKoyu: '#36424f', goz: '#14110f' };
const yol = (noktalar, kapat = true) => { c.beginPath(); c.moveTo(...noktalar[0]); for (const p of noktalar.slice(1)) p.length === 2 ? c.lineTo(...p) : c.quadraticCurveTo(...p); if (kapat) c.closePath(); };
const doldur = (renk) => { c.fillStyle = renk; c.fill(); };
const elips = (x, y, rx, ry, renk, a = 0) => { c.beginPath(); c.ellipse(x, y, rx, ry, a, 0, Math.PI * 2); doldur(renk); };

// ---- senaryodan zaman bilgisi ----
const satir = (t) => S.satirlar.find((s) => t >= s.bas - 0.05 && t < s.bit + 0.18) || null;
const plan = (t) => { let p = S.planlar[0]; for (const q of S.planlar) if (t >= q.bas) p = q; return p; };
// ağız: ses.wav varsa gerçek sesin genlik zarfından (60 dilim/sn), yoksa metin uzunluğundan hece ritmi
let ZARF = null;
try {
  const r = await fetch('./ses.wav');
  if (r.ok) {
    const b = await new OfflineAudioContext(1, 1, 48000).decodeAudioData(await r.arrayBuffer()), x = b.getChannelData(0), n = Math.round(b.sampleRate / 60);
    ZARF = new Float32Array(Math.ceil(x.length / n));
    for (let i = 0; i < ZARF.length; i++) { let e = 0; for (let j = i * n; j < Math.min(x.length, (i + 1) * n); j++) e += x[j] * x[j]; ZARF[i] = Math.sqrt(e / n); }
    const tepe = ZARF.reduce((a, v) => Math.max(a, v), 0); for (let i = 0; i < ZARF.length; i++) ZARF[i] = Math.min(1, ZARF[i] / (tepe * 0.6));
  }
} catch (e) { ZARF = null; }
const agizAc = (t, s) => {
  if (!s || t < s.bas || t > s.bit) return 0;
  if (ZARF) return ZARF[Math.min(ZARF.length - 1, Math.round(t * 60))] || 0;
  const h = (s.metin.length / 2.6) / (s.bit - s.bas);   // saniyede hece
  const u = (t - s.bas) * h; return 0.5 + 0.5 * Math.sin(u * Math.PI * 2) * (0.7 + 0.3 * tohum(Math.floor(u)));
};
const kirp = (t, faz) => { const p = (t + faz) % 3.7; return p < 0.12 ? Math.sin(p / 0.12 * Math.PI) : 0; };   // göz kırpma
const nefes = (t, faz) => Math.sin((t + faz) * 1.6) * 4;

// ---- arka plan katmanları (paralaks için ayrı çizilir) ----
function gok() {
  const g = c.createLinearGradient(0, 0, 0, Y); g.addColorStop(0, RENK.gok1); g.addColorStop(0.75, RENK.gok2); c.fillStyle = g; c.fillRect(-400, -400, G + 800, Y + 800);
  const h = c.createRadialGradient(780, 420, 10, 780, 420, 260); h.addColorStop(0, 'rgba(243,230,196,.35)'); h.addColorStop(1, 'rgba(243,230,196,0)');
  c.fillStyle = h; c.fillRect(400, 100, 760, 640); elips(780, 420, 70, 70, RENK.ay);
}
function sehir(t) {
  for (let i = 0; i < 26; i++) {
    const x = -300 + i * 70 + tohum(i) * 30, w = 60 + tohum(i + 9) * 70, h = 380 + tohum(i + 3) * 620, y = 1330 - h;
    c.fillStyle = RENK.bina; c.fillRect(x, y, w, h + 400);
    for (let py = y + 24; py < 1300; py += 42) for (let px = x + 10; px < x + w - 14; px += 22) {
      const n = i * 977 + px * 13 + py * 7; if (tohum(n) > 0.32) continue;
      const yanip = tohum(n + Math.floor(t / 4 + tohum(n) * 9)) > 0.15;   // bazı pencereler ara sıra söner
      c.fillStyle = yanip ? RENK.pencere : '#2a2f3a'; c.globalAlpha = 0.55 + 0.4 * tohum(n + 1); c.fillRect(px, py, 10, 16); c.globalAlpha = 1;
    }
  }
}
function cati() {
  c.fillStyle = RENK.cati; c.fillRect(-400, 1330, G + 800, 900);
  c.fillStyle = '#272c36'; c.fillRect(-400, 1330, G + 800, 14);
  // sokak lambası: sıcak pratik ışık
  c.fillStyle = '#0b0d11'; c.fillRect(905, 900, 12, 440); c.fillRect(860, 900, 60, 10);
  const l = c.createRadialGradient(866, 925, 4, 866, 925, 360); l.addColorStop(0, 'rgba(243,207,114,.55)'); l.addColorStop(1, 'rgba(243,207,114,0)');
  c.fillStyle = l; c.fillRect(500, 560, 740, 900); elips(866, 918, 16, 8, '#ffe7a8');
  // bank: iki karakter üstünde oturur (ayaklar zemine basar)
  c.fillStyle = '#3b2c22'; c.fillRect(150, 1395, 780, 26); c.fillRect(150, 1300, 780, 18);
  c.fillStyle = '#251b15'; for (const x of [180, 520, 880]) c.fillRect(x, 1420, 16, 120);
}
function yagmur(t) {
  c.strokeStyle = 'rgba(200,215,235,.22)'; c.lineWidth = 2; c.beginPath();
  for (let i = 0; i < 140; i++) {
    const x = (tohum(i) * (G + 600) - 300 + t * 120) % (G + 600) - 300, y = ((tohum(i + 50) * Y + t * 1500 * (0.8 + 0.4 * tohum(i + 7))) % (Y + 200)) - 100;
    c.moveTo(x, y); c.lineTo(x - 10, y + 46);
  }
  c.stroke();
}

// ---- karakterler: parçalar kendi pivotunda çizilir (baş boyna, kol omuza bağlı) ----
function usta(t, s, bakis) {   // bakis: -1 çırağa, 0 kameraya
  const ac = agizAc(t, s), n = nefes(t, 0);
  c.save(); c.translate(690, 1395);
  elips(0, 10, 150, 18, 'rgba(0,0,0,.35)');                         // gölge
  yol([[-120, 0], [-130, -200], [-80, -330 + n], [80, -330 + n], [130, -200], [120, 0]]); doldur(RENK.takim);   // gövde
  yol([[-40, -330 + n], [0, -230], [40, -330 + n]]); doldur(RENK.beyaz);                                            // gömlek
  yol([[-8, -320 + n], [8, -320 + n], [14, -240], [0, -222], [-14, -240]]); doldur(RENK.kravat);                 // kravat
  yol([[-80, -330 + n], [-30, -300], [0, -230], [-45, -250]]); doldur(RENK.takimKoyu);                            // yaka
  yol([[80, -330 + n], [30, -300], [0, -230], [45, -250]]); doldur(RENK.takimKoyu);
  c.fillStyle = RENK.takimKoyu; c.fillRect(-90, 0, 56, 140); c.fillRect(34, 0, 56, 140); elips(-66, 145, 40, 14, '#0e1014'); elips(66, 145, 40, 14, '#0e1014');   // bacak + ayakkabı (zeminde)
  c.save(); c.translate(-92, -300 + n); c.rotate(-0.18 + 0.03 * Math.sin(t * 0.9)); c.fillStyle = RENK.takimKoyu; c.fillRect(-24, 0, 48, 270); elips(4, 274, 24, 20, RENK.tilki); c.restore();  // kol: el dizin üstünde
  c.save(); c.translate(150, -10); c.rotate(-0.5 + 0.06 * Math.sin(t * 1.3)); yol([[0, 0], [60, -40, 140, -20], [120, 20, 30, 30]]); doldur(RENK.tilki); yol([[100, -22], [140, -20], [128, 10]]); doldur(RENK.beyaz); c.restore();  // kuyruk
  // baş
  c.save(); c.translate(0, -340 + n); c.rotate(bakis * 0.12 + 0.02 * Math.sin(t * 0.7)); const yon = bakis * 22;
  yol([[-70, -20], [-60, -150], [-20, -70]]); doldur(RENK.tilkiKoyu); yol([[70, -20], [60, -150], [20, -70]]); doldur(RENK.tilkiKoyu);   // kulak
  yol([[-50, -40], [-46, -112], [-26, -66]]); doldur(RENK.goz); yol([[50, -40], [46, -112], [26, -66]]); doldur(RENK.goz);
  yol([[-90, -40], [0, -95, 90, -40], [100, 20], [yon, 120], [-100, 20]]); doldur(RENK.tilki);                   // yüz
  yol([[-62, 30], [yon * 0.6, 60], [yon, 122], [-40 + yon * 0.4, 80]]); doldur(RENK.beyaz); yol([[62, 30], [yon * 0.6, 60], [yon, 122], [40 + yon * 0.4, 80]]); doldur(RENK.beyaz);
  elips(yon, 118, 14, 10, RENK.goz);                                                                                  // burun
  const k = 1 - kirp(t, 0.4);
  for (const sx of [-1, 1]) { elips(sx * 38 + yon * 0.7, -2, 15, 11 * k + 0.5, RENK.beyaz); elips(sx * 38 + yon, -2, 7, 8 * k + 0.5, RENK.goz); c.fillStyle = RENK.tilkiKoyu; c.fillRect(sx * 38 + yon * 0.7 - 20, -26 - 3 * ac, 40, 7); }   // göz + kaş
  elips(yon * 0.9, 140, 16, 3 + 13 * ac, '#3a1410');                                                                 // ağız
  c.restore(); c.restore();
}
function cirak(t, s, bakis) {
  const ac = agizAc(t, s), n = nefes(t, 1.3);
  c.save(); c.translate(340, 1395);
  elips(0, 10, 120, 16, 'rgba(0,0,0,.35)');
  yol([[-95, 0], [-100, -160], [-60, -260 + n], [60, -260 + n], [100, -160], [95, 0]]); doldur(RENK.kapusonlu);
  yol([[-60, -260 + n], [0, -215], [60, -260 + n], [40, -290 + n], [-40, -290 + n]]); doldur(RENK.kapusonluKoyu);   // kapüşon kenarı
  c.fillStyle = RENK.kapusonluKoyu; c.fillRect(-40, -120, 80, 40);                                                   // cep
  c.fillStyle = '#20262e'; c.fillRect(-80, 0, 50, 140); c.fillRect(30, 0, 50, 140); elips(-55, 145, 34, 14, '#0e1014'); elips(55, 145, 34, 14, '#0e1014');   // bacak + ayak (zeminde)
  // baş: biraz büyük (genç), ustaya bakar
  c.save(); c.translate(0, -280 + n); c.rotate(bakis * 0.1 + 0.03 * Math.sin(t * 1.1)); const yon = bakis * 18;
  elips(0, -20, 92, 86, RENK.kopek);
  c.save(); c.translate(-80, -60); c.rotate(0.35 + 0.05 * Math.sin(t * 2)); elips(0, 50, 28, 66, RENK.kopekKoyu); c.restore();   // sarkık kulak
  c.save(); c.translate(80, -60); c.rotate(-0.35 - 0.05 * Math.sin(t * 2 + 1)); elips(0, 50, 28, 66, RENK.kopekKoyu); c.restore();
  elips(yon * 0.8, 30, 46, 34, RENK.beyaz); elips(yon, 12, 15, 11, RENK.goz);
  const k = 1 - kirp(t, 2.1);
  for (const sx of [-1, 1]) { elips(sx * 34 + yon * 0.7, -38, 17, 15 * k + 0.5, RENK.beyaz); elips(sx * 34 + yon, -36, 9, 10 * k + 0.5, RENK.goz); c.fillStyle = RENK.kopekKoyu; c.fillRect(sx * 34 + yon * 0.7 - 16, -66 + (sx < 0 ? 4 : -2), 32, 6); }   // kaşlar asimetrik: kafa karışıklığı
  elips(yon * 0.9, 46, 12, 2 + 11 * ac, '#3a1410');
  c.restore(); c.restore();
}

// ---- kamera planları: plan içinde yalnız yavaş itme; kesme senaryodan gelir ----
const KAMERA = { genis: [540, 1060, 1.0], usta: [690, 1080, 1.85], cirak: [340, 1140, 1.95], kamera: [690, 1010, 2.4] };

window.kare = function kare(t) {
  const s = satir(t), p = plan(t), [kx, ky, z0] = KAMERA[p.plan], z = z0 * (1 + 0.035 * (t - p.bas));
  const kamerayaBakar = p.plan === 'kamera';
  c.setTransform(1, 0, 0, 1, 0, 0);
  for (const [katman, para] of [[gok, 0.15], [sehir, 0.45], [null, 1]]) {   // paralaks: uzak katman kameradan az etkilenir
    c.setTransform(1, 0, 0, 1, 0, 0); c.translate(G / 2, Y / 2); const zz = 1 + (z - 1) * para; c.scale(zz, zz); c.translate(-(G / 2 + (kx - G / 2) * para), -(Y / 2 + (ky - Y / 2) * para));
    if (katman) { katman(t); continue; }
    cati(); cirak(t, s && s.kim === 'cirak' ? s : null, 1); usta(t, s && s.kim === 'usta' ? s : null, kamerayaBakar ? 0 : -1);
  }
  c.setTransform(1, 0, 0, 1, 0, 0); yagmur(t);
  const v = c.createRadialGradient(G / 2, Y / 2, Y * 0.3, G / 2, Y / 2, Y * 0.75); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,.55)');   // kenar kararması
  c.fillStyle = v; c.fillRect(0, 0, G, Y);
  c.fillStyle = `rgba(0,0,0,${1 - yumusak(t / 0.5)})`; c.fillRect(0, 0, G, Y);   // açılış
  yazi.textContent = s ? s.metin : '';
};

// Önizleme: gerçek zamanlı döngü. Çekimde (?cekim) cek.mjs kare(t)'yi kendisi çağırır.
if (cekim) {
  document.body.classList.add('cekim');
  window.hazir = true;
} else {
  const sigdir = () => { const o = Math.min(innerWidth / G, innerHeight / Y); kap.style.transform = `scale(${o})`; };
  sigdir(); addEventListener('resize', sigdir);
  const t0 = performance.now();
  const dongu = () => { window.kare(((performance.now() - t0) / 1000) % S.sure); requestAnimationFrame(dongu); };
  dongu();
}
