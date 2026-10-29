# Render kuyruğu (TEK SIRA; paralel çekim BSOD yapar): kürsü planları + ürün sahneleri -> kare/<plan>/####.png ; var olan kareler atlanır (kaldığı yerden devam)
B="${BLENDER:-blender}"; cd "$(dirname "$0")"
coz() { "$B" -b "$1" -P render_aralik.py -- "$2" "$3" "$4" 2>&1 | grep -E "KARE|Error|Traceback" | tail -2; }
for p in $(python -c "import json;print(' '.join(f'{k}:{a}:{b}' for k,(a,b) in json.load(open('kursu_planlar.json')).items()))"); do
  IFS=: read ad a b <<< "$p"; echo "PLAN $ad $a-$b basladi $(date +%T)"; coz film_kursu.blend "$ad" $a $b; echo "PLAN $ad bitti $(date +%T)"; done
for s in togg baykar tusas tb3 marti uzay; do echo "URUN $s basladi $(date +%T)"; coz sahne_$s.blend $s 1 0; echo "URUN $s bitti $(date +%T)"; done
echo "KUYRUK BITTI $(date +%T)"
