#!/usr/bin/env bash
# Kaynak ses: Onuncu Yıl Nutku, iyileştirilmiş kayıt (YouTube 9qORieOMQRQ). Telif nedeniyle repoda yok; buradan indirilir.
# Gerekenler: yt-dlp (güncel sürüm; eskileri 403 alır: pip install -U yt-dlp), ffmpeg. Çalıştır: bash kaynak/indir.sh (ornekler/onuncu-yil içinden)
set -e; cd "$(dirname "$0")"
yt-dlp -f bestaudio -o "9qORieOMQRQ.%(ext)s" "https://www.youtube.com/watch?v=9qORieOMQRQ"
# kesit: 181-233 sn (son bölüm "Çünkü Türk Milletinin karakteri yüksektir ..."), 44,1 kHz mono
ffmpeg -v error -y -ss 181 -to 233 -i 9qORieOMQRQ.* -ac 1 -ar 44100 iyi-kesit44.wav
echo "Hazır: kaynak/iyi-kesit44.wav"
