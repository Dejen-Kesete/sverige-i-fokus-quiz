# Admas Studio promo video — edit pipeline

Scripts used to turn the raw promo recording into the finished, graded promo with motion graphics.
The rendered videos themselves are not committed (they are large binaries).

| File | What it does |
|---|---|
| `endbg.py` | Renders the animated navy + gold bokeh backgrounds: the 3.5 s branded intro, and the end card with the circular studio-mic logo. |
| `gen_ass.py` | Generates the motion-graphics layer as an ASS script rendered by libass. It covers letterbox bars, titles, service cards, checklists, the price card and the CTA end card. Copy is in English (`en`) and Swedish (`sv`). |
| `music.py` | Synthesizes the ambient score (pad, bass, bell arpeggio, pulse, reverb) and the whoosh/hit/shimmer SFX, all timed to the graphics. |
| `mix.py` | Places the processed voice at an exact sample offset and mixes it with the ducked score and SFX. Alignment is done on raw samples, never on ffmpeg timestamps, so lip sync cannot drift. |
| `render.sh` | Mixes and loudness-normalizes the audio (voice EQ/compression, score ducked under the voice, −14 LUFS). It then applies the cinematic grade (bloom, teal/gold balance, filmic curve, vignette, grain), composites everything and encodes H.264. |

Usage (in a working folder containing `src.mov`, the source recording, plus a `sf/` folder of static font instances
named `AS Mont *`, `AS Playfair*` and `AS Ethiopic`, made from Montserrat, Playfair Display and Noto Sans Ethiopic):

```bash
ffmpeg -ss 14 -i src.mov -frames:v 1 st/logo_mic.png
python3 endbg.py 20.24 st/logo_mic.png endbg.mp4
python3 endbg.py 3.5  st/logo_mic.png introbg.mp4
python3 music.py
python3 gen_ass.py en && ./render.sh en    # -> admas_promo_en.mp4
python3 gen_ass.py sv && ./render.sh sv    # -> admas_promo_sv.mp4
```

Timings in `gen_ass.py` are in source seconds and match the cuts of the original recording.

## Vertical 1080×1920 (TikTok) cut

| File | What it does |
|---|---|
| `faces.py` | Detects the face in every source frame; drives the vertical reframing. |
| `broll.py` | Five animated B-roll scenes: live voice spectrum, Swedish→Tigrinya translation, 200+ counter, phone quiz demo, application checklist. |
| `compose.py` | Builds the vertical base video one output frame per source frame (lip sync by construction): face-tracked wide/tight crops, reframed footage, B-roll and end card. |
| `gen_ass_v.py` | Vertical graphics (EN/SV), kept inside TikTok's safe zone. |
| `render_v.sh` | Adds graphics and audio, writes a master and a <30 MB share copy. |
| `vsync.py` | Verifies the output: voice offset (ms) and per-segment picture offset (frames) against the source. |

```bash
python3 faces.py src.mov faces_src.json
EW=1080 EH=1920 LD=300 LCY=560 python3 endbg.py 20.24 st/logo_mic.png endbg_v.mp4
VERT=1 python3 music.py && python3 mix.py voice.wav music_v.wav sfx_v.wav 0 103 mix_v_raw.wav  # then loudness-normalize to mix_v.wav
python3 compose.py en && python3 gen_ass_v.py en && ./render_v.sh en
python3 vsync.py vert/AdmasStudio_TikTok_EN.mp4
```

`compose.py` expects `graded.mp4`, which is the source run through the grade in `render.sh`.
