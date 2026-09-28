# Admas Studio promo video — edit pipeline

Scripts used to turn the raw promo recording into the finished, graded promo with motion graphics.
The rendered videos themselves are not committed (they are large binaries).

| File | What it does |
|---|---|
| `endbg.py` | Renders the animated navy + gold bokeh backgrounds: the 3.5 s branded intro, and the end card with the circular studio-mic logo. |
| `gen_ass.py` | Generates the motion-graphics layer as an ASS script rendered by libass. It covers letterbox bars, titles, service cards, checklists, the price card and the CTA end card. Copy is in English (`en`) and Swedish (`sv`). |
| `music.py` | Synthesizes the ambient score (pad, bass, bell arpeggio, pulse, reverb) and the whoosh/hit/shimmer SFX, all timed to the graphics. |
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
