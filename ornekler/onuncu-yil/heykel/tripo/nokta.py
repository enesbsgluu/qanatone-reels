# python nokta.py resim.png kadraj.json cikti.json : MediaPipe 478 nokta -> dünya x,z (ortografik önden)
import sys, json, numpy as np, mediapipe as mp
from PIL import Image, ImageDraw
from mediapipe.tasks import python as mpt; from mediapipe.tasks.python import vision
im = Image.open(sys.argv[1]).convert('RGB'); a = np.array(im); K = json.load(open(sys.argv[2]))
det = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=mpt.BaseOptions(model_asset_path=sys.argv[4] if len(sys.argv) > 4 else '../face_landmarker.task'), num_faces=1, min_face_detection_confidence=.2))
r = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=a))
if not r.face_landmarks: raise SystemExit('YÜZ BULUNAMADI')
L = r.face_landmarks[0]; s = K['olcek']; px = K['px']
json.dump([[K['cx'] + (p.x - .5) * s, K['cz'] - (p.y - .5) * s] for p in L], open(sys.argv[3], 'w'))
dr = ImageDraw.Draw(im)
for p in L: dr.ellipse((p.x * px - 2, p.y * px - 2, p.x * px + 2, p.y * px + 2), fill=(255, 40, 40))
im.resize((700, 700)).save(sys.argv[3].replace('.json', '.jpg')); print('NOKTA', len(L))
