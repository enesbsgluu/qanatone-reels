# Blender: sahne_anim.blend -> film_kursu.blend: kürsü planları K1–K5 + son (yandan 3/4 yakın, şarkı) için animasyon + kameralar. Kare = round(t*30)+1 (film zamanı).
# Baş: satır başında kâğıda eğik (okuma), satır sonunda/vurgularda dinleyiciye kalkar, sağa-sola hafif döner; son satır + final: ufka bakış.
# Ağız: zaman.json satır z (30 fps ses zarfı) -> 'agiz' şekil anahtarı + ağız boşluğu dikey ölçeği. Kırpma: doğal aralıklar. Gözler bakışı izler.
# Kullanım: blender -b -P b_film.py
import bpy, os, json, math, numpy as np
from mathutils import Vector
W = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(W, '..')
bpy.ops.wm.open_mainfile(filepath=os.path.join(W, 'sahne_anim.blend')); sc = bpy.context.scene
J = json.load(open(os.path.join(D, 'zaman.json'), encoding='utf-8')); SAT = J['satir']; VUR = J['vurgu']
F = lambda t: int(round(t * 30)) + 1; SON0, SON1 = 42.3, 60.3
pv = bpy.data.objects['bas_pivot']; bas = bpy.data.objects['bas']; ai = bpy.data.objects['agiz_ici']; BK = [bpy.data.objects['bakis_R'], bpy.data.objects['bakis_L']]
KB = bas.data.shape_keys.key_blocks; r = math.radians
# ---------- baş + göz pozu zaman çizgisi ----------
P = [(0.0, 10, 0, 12)]   # (t, eğim°, dönüş°, göz eğimi°): + aşağı (okuma)
for i, s_ in enumerate(SAT):
    t0, t1 = s_['t'], s_['t'] + s_['d']; yon = 7 if i % 2 == 0 else -6
    son = i == len(SAT) - 1
    P += [(t0 - .25, 11, 0, 13), (t0 + .55 * s_['d'], 9, 1 * (1 if i % 2 else -1), 12)]
    if son: P += [(t0 + .45 * s_['d'], 4, 4, 4), (t1, -6, 12, -4)]   # ufka bakış: sol kameradan uzağa (+X yönü)
    else: P += [(t0 + .72 * s_['d'], -2, yon, 0), (t1 + .25, -1, yon * .8, 0)]
P += [(SON1, -6.5, 13, -4)]
P.sort()
def poz(o, t, rx, rz):
    o.rotation_euler = (r(rx), 0, r(rz)); o.keyframe_insert('rotation_euler', frame=F(t))
pv.rotation_mode = 'XYZ'
for t, e, d, g in P:
    poz(pv, t, e, d)
    for b in BK: b.rotation_euler = (r(g), 0, r(d * .5)); b.keyframe_insert('rotation_euler', frame=F(t))
for o in [pv] + BK:
    for fc in getattr(o.animation_data.action, 'fcurves', []):
        for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'; kp.easing = 'AUTO'
# ---------- ağız (konuşma zarfı) ----------
ag = np.zeros(F(SON1) + 2)
for s_ in SAT:
    z = np.array(s_['z'], float); f0 = F(s_['t'])
    for k, v in enumerate(z): ag[f0 + k] = max(ag[f0 + k], v)
ag = np.convolve(ag, np.ones(3) / 3, mode='same'); ag = np.clip(ag * 1.15, 0, 1) * .7
for f in range(1, F(SON0) + 6):
    KB['agiz'].value = float(ag[f]); KB['agiz'].keyframe_insert('value', frame=f)
    ai.scale[2] = .001 + .0055 * float(ag[f]); ai.keyframe_insert('scale', index=2, frame=f)
# ---------- kırpma ----------
for t in (2.3, 5.2, 7.6, 16.6, 19.6, 29.6, 32.3, 40.5, 44.2, 47.9, 51.8, 55.6, 59.0):
    f = F(t)
    for df, v in ((-1, 0), (1, 1), (2, 1), (5, 0)): KB['kirp'].value = v; KB['kirp'].keyframe_insert('value', frame=f + df)
# ---------- kameralar (plan başı/sonu; planlar arası kesme) ----------
kam = sc.camera; cd = kam.data; cd.dof.use_dof = True; cd.dof.aperture_fstop = 2.2; hedefB = Vector((0, .0, 1.56))
PLAN = [('K1', 0.0, 8.56, ((.6, -4.6, 1.85), (0, -.1, 1.45), 35), ((.35, -2.6, 1.66), (0, 0, 1.5), 45)),
        ('K2', 15.96, 17.45, ((.06, -1.05, 1.6), (0, 0, 1.585), 85), ((.04, -.96, 1.6), (0, 0, 1.585), 85)),
        ('K3', 17.45, 20.95, ((1.05, -1.6, 1.55), (0, 0, 1.47), 50), ((.85, -1.75, 1.58), (0, 0, 1.48), 50)),
        ('K4', 28.11, 33.07, ((.45, -1.7, 1.25), (0, 0, 1.53), 40), ((.15, -1.55, 1.3), (0, 0, 1.55), 40)),
        ('K5', 39.42, 42.3, ((.5, -.98, 1.61), (0, 0, 1.585), 85), ((.44, -.9, 1.61), (0, 0, 1.59), 85)),
        ('SON', SON0, SON1, ((-.78, -.98, 1.63), (0, 0, 1.6), 70), ((-.6, -.8, 1.615), (0, 0, 1.6), 92))]   # aydınlık sol taraf (sağ yanak gölgede lekeli); mikrofon bu planda gizli
for ad, t0, t1, (l0, h0, f0), (l1, h1, f1) in PLAN:
    for t, l, h, fl in ((t0, l0, h0, f0), (t1 - 1 / 30, l1, h1, f1)):
        kam.location = l; kam.rotation_euler = (Vector(h) - Vector(l)).to_track_quat('-Z', 'Y').to_euler(); cd.lens = fl; cd.dof.focus_distance = (Vector(l) - hedefB).length
        f = F(t); kam.keyframe_insert('location', frame=f); kam.keyframe_insert('rotation_euler', frame=f); cd.keyframe_insert('lens', frame=f); cd.dof.keyframe_insert('focus_distance', frame=f)
for o in (kam, cd):
    for fc in getattr(o.animation_data.action, 'fcurves', []):
        for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'; kp.easing = 'EASE_IN_OUT'
mik = [o for o in bpy.data.objects if o.type == 'MESH' and o.matrix_world.translation.x < -.25 and o.matrix_world.translation.y < -.5 and o.name not in ('zemin',)]
for o in mik:   # son planda mikrofon gizli (sol açıdan kadraja giriyordu)
    o.hide_render = False; o.keyframe_insert('hide_render', frame=F(SON0) - 1); o.hide_render = True; o.keyframe_insert('hide_render', frame=F(SON0))
print('SON planda gizlenen', [o.name for o in mik][:12])
# ---------- render: EEVEE, kornea saydam karışım ----------
sc.render.engine = 'BLENDER_EEVEE' if 'BLENDER_EEVEE' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE_NEXT'
for a, v in (('taa_render_samples', 64), ('use_raytracing', True), ('use_shadows', True)):
    try: setattr(sc.eevee, a, v)
    except Exception: pass
for m in bpy.data.materials:
    if m.name.startswith('kornea'):
        try: m.surface_render_method = 'BLENDED'
        except Exception: pass
        b = m.node_tree.nodes['Principled BSDF']; b.inputs['Alpha'].default_value = .08; b.inputs['Transmission Weight'].default_value = 0; b.inputs['Roughness'].default_value = .02
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920; sc.render.resolution_percentage = 100; sc.render.fps = 30; sc.frame_start = 1; sc.frame_end = F(SON1)
sc.render.use_motion_blur = False
json.dump({ad: [F(t0), F(t1) - 1] for ad, t0, t1, *_ in PLAN}, open(os.path.join(W, 'kursu_planlar.json'), 'w'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(W, 'film_kursu.blend')); print('FİLM KÜRSÜ kaydedildi', {ad: (F(t0), F(t1) - 1) for ad, t0, t1, *_ in PLAN})
