// Başlangıç sahnesi: iki low-poly karakter, bir oda, plan kesmeleri ve altyazı.
// Her şey zamanın saf fonksiyonu: kare(t) aynı t için hep aynı görüntüyü verir.
// Bu sayede çekim (cek.mjs) gerçek zamandan bağımsız, kare kare ve titremesiz olur.
import * as THREE from 'three';

const G = 1080, Y = 1920;
const S = await (await fetch('./senaryo.json')).json();
const cekim = new URLSearchParams(location.search).has('cekim');

const kap = document.getElementById('kap');
const yazi = document.querySelector('#altyazi span');
const r = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
r.setPixelRatio(1);
r.setSize(G, Y);
r.outputColorSpace = THREE.SRGBColorSpace;
r.toneMapping = THREE.ACESFilmicToneMapping;
r.shadowMap.enabled = true;
r.shadowMap.type = THREE.PCFSoftShadowMap;
kap.prepend(r.domElement);

const sc = new THREE.Scene();
sc.background = new THREE.Color('#1b1a18');
sc.fog = new THREE.Fog('#1b1a18', 9, 22);
const kam = new THREE.PerspectiveCamera(40, G / Y, 0.1, 60);

// ---- malzeme yardımcısı: düz gölgeli (low-poly görünüm) ----
const mal = (renk, o = {}) => new THREE.MeshStandardMaterial({ color: renk, flatShading: true, roughness: 0.75, ...o });
const kutu = (g, y, d, m) => { const k = new THREE.Mesh(new THREE.BoxGeometry(g, y, d), m); k.castShadow = k.receiveShadow = true; return k; };

// ---- oda ----
const zemin = new THREE.Mesh(new THREE.PlaneGeometry(30, 30), mal('#2a2724'));
zemin.rotation.x = -Math.PI / 2; zemin.receiveShadow = true; sc.add(zemin);
const duvar = kutu(14, 6, 0.2, mal('#3a3531')); duvar.position.set(0, 3, -3.2); sc.add(duvar);
const pano = kutu(3.2, 1.8, 0.06, mal('#ef233c', { emissive: '#ef233c', emissiveIntensity: 0.08 })); pano.position.set(0, 3.1, -3.08); sc.add(pano);
const masa = kutu(2.4, 0.12, 1.1, mal('#5b4434')); masa.position.set(0, 1.0, -0.6); sc.add(masa);
for (const [x, z] of [[-1.1, -1.05], [1.1, -1.05], [-1.1, -0.15], [1.1, -0.15]]) { const a = kutu(0.08, 1.0, 0.08, mal('#3b2c22')); a.position.set(x, 0.5, z); sc.add(a); }
// imza: masada küçük kızıl damla
const damla = new THREE.Mesh(new THREE.SphereGeometry(0.09, 10, 8), mal('#ef233c', { roughness: 0.35 }));
damla.scale.set(1, 1.25, 1); damla.position.set(0.85, 1.15, -0.55); damla.castShadow = true; sc.add(damla);

// ---- ışık ----
sc.add(new THREE.HemisphereLight('#ffe9d6', '#1b1a18', 0.55));
const ana = new THREE.DirectionalLight('#fff1e0', 2.2); ana.position.set(3, 6, 4); ana.castShadow = true;
ana.shadow.mapSize.set(2048, 2048); Object.assign(ana.shadow.camera, { left: -5, right: 5, top: 5, bottom: -5 }); sc.add(ana);
const kenar = new THREE.PointLight('#ef233c', 2.2, 6); kenar.position.set(0, 3, -2.6); sc.add(kenar);

// ---- karakter: gövde + kafa + göz + ağız. ağız açıklığı konuşmaya göre ----
function karakter({ govde, kafa, kafaBoy, sapka }) {
  const k = new THREE.Group();
  const g = kutu(0.62, 0.9, 0.38, mal(govde)); g.position.y = 1.15; k.add(g);
  for (const s of [-1, 1]) { const b = kutu(0.2, 0.75, 0.22, mal('#26231f')); b.position.set(0.17 * s, 0.38, 0); k.add(b); }
  const kol = []; for (const s of [-1, 1]) { const q = kutu(0.16, 0.7, 0.18, mal(govde)); q.geometry.translate(0, -0.33, 0); q.position.set(0.41 * s, 1.55, 0); k.add(q); kol.push(q); }
  const bas = new THREE.Group(); bas.position.y = 1.62 + kafaBoy / 2; k.add(bas);
  bas.add(kutu(0.5, kafaBoy, 0.46, mal(kafa)));
  const goz = mal('#0e0e0d', { roughness: 0.3 });
  for (const s of [-1, 1]) { const o = new THREE.Mesh(new THREE.SphereGeometry(0.045, 8, 6), goz); o.position.set(0.11 * s, 0.06, 0.235); bas.add(o); }
  const agiz = kutu(0.14, 0.03, 0.02, mal('#0e0e0d')); agiz.position.set(0, -0.1, 0.235); bas.add(agiz);
  if (sapka) { const s1 = kutu(0.7, 0.04, 0.62, mal('#111')); s1.position.y = kafaBoy / 2 + 0.02; const s2 = kutu(0.44, 0.22, 0.4, mal('#111')); s2.position.y = kafaBoy / 2 + 0.15; bas.add(s1, s2); }
  sc.add(k);
  return { k, bas, kol, agiz };
}
const adam = karakter({ govde: '#3d5a46', kafa: '#d9a47e', kafaBoy: 0.5, sapka: true });
const robot = karakter({ govde: '#6f6a64', kafa: '#c9774f', kafaBoy: 0.56, sapka: false });
adam.k.position.set(-0.75, 0, 0.35); adam.k.rotation.y = 0.45;
robot.k.position.set(0.75, 0, 0.35); robot.k.rotation.y = -0.45;
const KIM = { adam, robot };

// ---- zaman yardımcıları ----
const yum = (x) => { x = Math.min(1, Math.max(0, x)); return x * x * (3 - 2 * x); };
const konusan = (t) => S.satirlar.find((s) => t >= s.bas && t <= s.bit);
const planAt = (t) => [...S.planlar].reverse().find((p) => t >= p.bas)?.plan || 'genis';

// Ağız: gerçek ses yoksa hece ritmi taklidi (yaklaşık 7 hece/sn). Ses eklersen burayı ses zarfına bağla.
function agizAc(t, s) {
  if (!s) return 0;
  const icinde = yum((t - s.bas) / 0.08) * yum((s.bit - t) / 0.08);
  return icinde * (0.35 + 0.65 * Math.abs(Math.sin(t * Math.PI * 7)));
}

const PLAN = {
  genis: { kon: [0, 2.3, 8.2], bak: [0, 1.35, 0] },
  adam: { kon: [0.2, 1.95, 3.4], bak: [-0.75, 1.8, 0.35] },
  robot: { kon: [-0.2, 1.95, 3.4], bak: [0.75, 1.8, 0.35] },
};

window.kare = function kare(t) {
  const s = konusan(t);
  for (const [ad, c] of Object.entries(KIM)) {
    const benim = s && s.kim === ad;
    c.agiz.scale.y = 1 + 3.2 * agizAc(t, benim ? s : null);
    // nefes + konuşurken hafif baş hareketi + dinleyen konuşana döner
    c.k.position.y = Math.sin(t * 2.1 + (ad === 'adam' ? 0 : 1.3)) * 0.008;
    c.bas.rotation.x = benim ? Math.sin(t * 3.1) * 0.05 : 0;
    c.bas.rotation.y = !benim && s ? (ad === 'adam' ? 0.25 : -0.25) : 0;
    c.kol[ad === 'adam' ? 1 : 0].rotation.x = benim ? -0.25 - Math.sin(t * 2.4) * 0.15 : 0;
  }
  damla.rotation.y = t * 0.6;
  // plan: kesme anında kamera atlar (kurguda kesme), plan içinde çok yavaş itme
  const p = PLAN[planAt(t)], basT = [...S.planlar].reverse().find((q) => t >= q.bas)?.bas || 0;
  const it = Math.min(1, (t - basT) / 4) * 0.25;
  kam.position.set(p.kon[0], p.kon[1], p.kon[2] - it);
  kam.lookAt(...p.bak);
  yazi.textContent = s ? s.metin : '';
  r.render(sc, kam);
};

// Önizleme: gerçek zamanlı döngü. Çekimde (?cekim) cek.mjs kare(t)'yi kendisi çağırır.
if (cekim) {
  document.body.classList.add('cekim');
  window.hazir = true;
} else {
  const sigdir = () => { const o = Math.min(innerWidth / G, innerHeight / Y); kap.style.transform = `scale(${o})`; };
  addEventListener('resize', sigdir); sigdir();
  const t0 = performance.now();
  const dongu = () => { window.kare(((performance.now() - t0) / 1000) % S.sure); requestAnimationFrame(dongu); };
  dongu();
}
