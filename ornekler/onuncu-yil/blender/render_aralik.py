# blender -b x.blend -P render_aralik.py -- ad bas bit  (bit=0 -> sahnenin frame_end'i); kare/<ad>/####.png, var olanlar atlanır
import bpy, sys, os
a = sys.argv[sys.argv.index('--') + 1:]; ad, b0, b1 = a[0], int(a[1]), int(a[2]); sc = bpy.context.scene
if b1 <= 0: b0, b1 = sc.frame_start, sc.frame_end
O = os.path.join(os.path.dirname(bpy.data.filepath), 'kare', ad); os.makedirs(O, exist_ok=True); sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGB'
for f in range(b0, b1 + 1):
    p = os.path.join(O, f'{f:04d}.png')
    if os.path.exists(p) and os.path.getsize(p) > 50000: continue
    sc.frame_set(f); sc.render.filepath = p; bpy.ops.render.render(write_still=True)
print('KARE', ad, b0, b1, 'tamam')
