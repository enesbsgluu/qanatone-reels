# python heykel/noktalar.py : hy-on.png (ortografik önden kil) -> MediaPipe FaceMesh 478 nokta -> dünya x,z (Blender) -> heykel/hy-noktalar.json + kontrol görseli
import json, mediapipe as mp, numpy as np
from PIL import Image, ImageDraw
im = Image.open('heykel/hy-on.png').convert('RGB'); a = np.array(im); K = json.load(open('heykel/hy-on.json'))
try:
    fm = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, refine_landmarks=True, max_num_faces=1, min_detection_confidence=.2)
    r = fm.process(a); L = r.multi_face_landmarks[0].landmark if r.multi_face_landmarks else None
except AttributeError:
    from mediapipe.tasks import python as mpt; from mediapipe.tasks.python import vision
    import urllib.request, os
    md = 'heykel/face_landmarker.task'
    if not os.path.exists(md): urllib.request.urlretrieve('https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task', md)
    det = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=mpt.BaseOptions(model_asset_path=md), num_faces=1, min_face_detection_confidence=.2))
    res = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=a)); L = res.face_landmarks[0] if res.face_landmarks else None
if L is None: raise SystemExit('YÜZ BULUNAMADI')
px = K['px']; s = K['olcek']
D = [[K['cx'] + (p.x - .5) * s, K['cz'] - (p.y - .5) * s] for p in L]   # dünya x, z
json.dump(D, open('heykel/hy-noktalar.json', 'w'))
dr = ImageDraw.Draw(im)
for p in L: dr.ellipse((p.x * px - 2, p.y * px - 2, p.x * px + 2, p.y * px + 2), fill=(255, 40, 40))
im.resize((700, 700)).save('heykel/hy-noktalar.jpg'); print('NOKTA', len(D))
