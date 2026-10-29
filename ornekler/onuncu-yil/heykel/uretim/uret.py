# python heykel/uretim/uret.py <arac> <girdi.png> : ücretsiz HF Space'lerle tek fotoğraftan 3B (TRELLIS.2 / Hunyuan3D-2.1 / Hi3DGen) -> heykel/uretim/<arac>.glb
import sys, shutil, os
from gradio_client import Client, handle_file
A, G = sys.argv[1], sys.argv[2]; O = f'heykel/uretim/{A}' + (sys.argv[3] if len(sys.argv) > 3 else ''); OCT = int(sys.argv[4]) if len(sys.argv) > 4 else 384
if A == 'trellis2':
    c = Client('microsoft/TRELLIS.2', verbose=False, token=__import__('huggingface_hub').get_token()); c.predict(api_name='/start_session')
    p = c.predict(input=handle_file(G), api_name='/preprocess_image')
    c.predict(image=handle_file(p if isinstance(p, str) else p['path']), seed=1, resolution='1536', api_name='/image_to_3d')
    r = c.predict(decimation_target=600000, texture_size=2048, api_name='/extract_glb'); f = r[1] if isinstance(r, (list, tuple)) else r
elif A == 'hunyuan21':
    c = Client('tencent/Hunyuan3D-2.1', verbose=False, token=__import__('huggingface_hub').get_token())
    r = c.predict(image=handle_file(G), mv_image_front=None, mv_image_back=None, mv_image_left=None, mv_image_right=None, steps=50, guidance_scale=5.0, seed=1234,
                  octree_resolution=OCT, check_box_rembg=False, num_chunks=8000, randomize_seed=False, api_name='/shape_generation'); f = r[0]
elif A == 'hi3dgen':
    c = Client('Stable-X/Hi3DGen', verbose=False, token=__import__('huggingface_hub').get_token())
    p = c.predict(image=handle_file(G), api_name='/preprocess_image')
    r = c.predict(image=handle_file(p if isinstance(p, str) else p['path']), seed=1, ss_guidance_strength=3, ss_sampling_steps=50, slat_guidance_strength=3.0, slat_sampling_steps=6, api_name='/generate_3d')
    f = r[-1]
f = f['value'] if isinstance(f, dict) and 'value' in f else (f['path'] if isinstance(f, dict) else f)
uz = os.path.splitext(f)[1] or '.glb'; shutil.copy(f, O + uz); print('TAMAM', A, O + uz, os.path.getsize(O + uz))
