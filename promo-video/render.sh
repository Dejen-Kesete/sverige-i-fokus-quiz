#!/bin/bash
# Usage: render.sh <lang> [preview_start preview_dur]
set -e
cd "$(dirname "$0")"
L=${1:-en}
OFF=3.5; END0=82.76; TOT=106.5

# ---------- audio: polished voice + ducked score + sfx, then linear gain to -14 LUFS
if [ ! -f mix_raw.wav ]; then
ffmpeg -hide_banner -loglevel error -y -i src.mov -i music.wav -i sfx.wav -filter_complex "
[0:a]aformat=sample_rates=44100:channel_layouts=stereo,highpass=f=80,
 equalizer=f=250:t=q:w=1.2:g=-2.5,equalizer=f=4200:t=q:w=1.4:g=2.5,equalizer=f=11000:t=h:w=2000:g=1.5,
 acompressor=threshold=-24dB:ratio=3:attack=8:release=180:makeup=3,
 loudnorm=I=-16:LRA=8:TP=-2,aresample=44100,
 adelay=${OFF}s:all=1,apad=whole_dur=${TOT},asplit[v1][v2];
[1:a]volume=-3dB[mu];
[mu][v2]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=500:makeup=1[md];
[v1][md][2:a]amix=inputs=3:weights='1 1 1':normalize=0,atrim=0:${TOT}[a]" -map "[a]" -c:a pcm_f32le mix_raw.wav
fi
if [ ! -f mix.wav ]; then
I=$(ffmpeg -hide_banner -i mix_raw.wav -af ebur128=peak=true -f null - 2>&1 | awk '/Integrated/{f=1} f&&/I:/{print $2; exit}')
G=$(python3 -c "print(round(-14.0-($I),2))")
echo "mix loudness $I LUFS -> gain $G dB"
ffmpeg -hide_banner -loglevel error -y -i mix_raw.wav -af "volume=${G}dB,alimiter=limit=0.89:attack=3:release=60:level=disabled,afade=t=in:d=0.3,afade=t=out:st=$(python3 -c "print($TOT-1.2)"):d=1.2" -c:a pcm_f32le mix.wav
fi

# ---------- video
GRADE="format=gbrp,split[ga][gb];[gb]curves=master='0/0 0.62/0 1/1',gblur=sigma=30[gbl];[ga][gbl]blend=all_mode=screen:all_opacity=0.2,format=yuv420p,eq=contrast=1.04:saturation=1.07:gamma=1.02,colorbalance=rs=-0.035:gs=-0.005:bs=0.045:rm=0.012:bm=-0.012:rh=0.04:gh=0.015:bh=-0.04:pl=1,curves=master='0/0.03 0.25/0.235 0.5/0.52 0.8/0.83 1/0.975',vignette=angle=PI/5.2"

SS=""; DUR=""; OUT="admas_promo_${L}.mp4"; CRF=17; PRE=slow
if [ -n "$2" ]; then SS="-ss $2"; DUR="-t $3"; OUT="prev_${L}.mp4"; CRF=22; PRE=veryfast; fi

ffmpeg -hide_banner -loglevel error -stats -y -i src.mov -i introbg.mp4 -i endbg.mp4 -i mix.wav -filter_complex "
[0:v]setpts=PTS-STARTPTS,fps=25,${GRADE}[g];
[2:v]setpts=PTS-STARTPTS+${END0}/TB,format=yuva420p,fade=t=in:st=${END0}:d=0.45:alpha=1[eb];
[g][eb]overlay=eof_action=pass:format=auto[body];
[1:v]fps=25,format=yuv420p,fade=t=out:st=$(python3 -c "print($OFF-0.45)"):d=0.45[intro];
[intro][body]concat=n=2:v=1:a=0,settb=1/25,
 ass=gfx_${L}.ass:fontsdir=sf,
 noise=alls=4:allf=t,
 fade=t=in:st=0:d=0.5,fade=t=out:st=$(python3 -c "print($TOT-0.8)"):d=0.8,format=yuv420p[v]" \
 -map "[v]" -map 3:a $SS $DUR -c:v libx264 -preset $PRE -crf $CRF -profile:v high -pix_fmt yuv420p \
 -color_primaries bt709 -color_trc bt709 -colorspace bt709 -movflags +faststart \
 -c:a aac -b:a 256k -t $TOT "$OUT"
echo "wrote $OUT"
