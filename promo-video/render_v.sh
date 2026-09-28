#!/bin/bash
# Final pass for the vertical cut: graphics + audio -> master and a <30 MB share copy.
# Usage: render_v.sh <lang>   (needs vbase_<lang>.mp4, gfx_v_<lang>.ass, mix_v.wav)
set -e
cd "$(dirname "$0")"
L=${1:-en}; U=${L^^}
mkdir -p vert
VF="ass=gfx_v_${L}.ass:fontsdir=sf,fade=t=in:st=0:d=0.3,fade=t=out:st=102.2:d=0.8,format=yuv420p"
COL="-color_primaries bt709 -color_trc bt709 -colorspace bt709"
# master (high quality, for uploading to TikTok directly)
ffmpeg -hide_banner -loglevel error -y -i vbase_${L}.mp4 -i mix_v.wav -map 0:v -map 1:a -vf "$VF" \
  -c:v libx264 -preset slow -crf 17 -profile:v high -pix_fmt yuv420p $COL -c:a aac -b:a 256k -movflags +faststart \
  -t 103 vert/AdmasStudio_TikTok_${U}_master.mp4
# share copy (<30 MB): two-pass from the master
ffmpeg -hide_banner -loglevel error -y -i vert/AdmasStudio_TikTok_${U}_master.mp4 -c:v libx264 -preset slow -b:v 2000k \
  -pass 1 -passlogfile pv_$U -an -f mp4 /dev/null
ffmpeg -hide_banner -loglevel error -y -i vert/AdmasStudio_TikTok_${U}_master.mp4 -c:v libx264 -preset slow -b:v 2000k \
  -maxrate 4000k -bufsize 8000k -pass 2 -passlogfile pv_$U -pix_fmt yuv420p $COL -c:a copy -movflags +faststart \
  vert/AdmasStudio_TikTok_${U}.mp4
ls -la vert/AdmasStudio_TikTok_${U}*.mp4
echo "DONE $L"
