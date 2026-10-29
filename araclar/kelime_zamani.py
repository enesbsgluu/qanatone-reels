# Kelime düzeyinde zaman: python araclar/kelime_zamani.py ses.wav kelime.json [model]
import sys; sys.stdout.reconfigure(encoding="utf-8")
# Çıktı [[kelime, bas, bit], ...] (sn). Model varsayılan large-v3 (yavaş ama en doğru); hızlı deneme için "medium".
import sys, json
from faster_whisper import WhisperModel
g, c = sys.argv[1], sys.argv[2]; m = WhisperModel(sys.argv[3] if len(sys.argv) > 3 else 'large-v3', device='auto', compute_type='int8')
seg, _ = m.transcribe(g, language='tr', word_timestamps=True)
W = [[w.word.strip(), round(w.start, 3), round(w.end, 3)] for s in seg for w in s.words]
json.dump(W, open(c, 'w', encoding='utf-8'), ensure_ascii=False); print(len(W), 'kelime ->', c); print(' '.join(w[0] for w in W))
