# Synthesizes a subtle cinematic score + motion-graphics SFX for the promo.
# Output: music.wav (score) and sfx.wav (whooshes/hits), 44.1 kHz stereo float32 WAV.
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
from scipy.io import wavfile

SR = 44100
OFF = 3.5
TOTAL = 103.0 + OFF
N = int(TOTAL * SR)
rng = np.random.default_rng(3)
t_all = np.arange(N) / SR

def hz(m): return 440.0 * 2 ** ((m - 69) / 12)

def env_adsr(n, a, r):
    e = np.ones(n); na, nr = int(a * SR), int(r * SR)
    e[:na] = np.sin(np.linspace(0, np.pi / 2, na)) ** 2
    e[-nr:] *= np.cos(np.linspace(0, np.pi / 2, nr)) ** 2
    return e

def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, "low", fs=SR, output="sos"), x, axis=0)

def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x, axis=0)

def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x, axis=0)

def place(buf, sig, t0, gain=1.0):
    i = int(t0 * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(sig)); buf[i:j] += sig[:j - i] * gain

music = np.zeros((N, 2))

# ---- chord progression (D major, cinematic/hopeful), 6 s per chord
BEAT = 60 / 80
chords = [  # (bass midi, pad notes)
    (38, [62, 66, 69, 73, 76]),   # Dmaj9
    (35, [59, 62, 66, 69, 74]),   # Bm7(add11)
    (31, [59, 62, 66, 67, 71]),   # Gmaj7
    (33, [57, 61, 64, 69, 71]),   # A(add9)
]
CH = 6.0
start = 0.0
k = 0
while start < TOTAL:
    bass, notes = chords[k % 4]
    dur = CH + 2.5
    n = int(dur * SR); tt = np.arange(n) / SR
    e = env_adsr(n, 1.8, 2.4)
    for m in notes:
        f = hz(m)
        for det, pan in ((-7, 0.2), (0, 0.5), (7, 0.8)):
            ff = f * 2 ** (det / 1200)
            ph = rng.uniform(0, 6.28)
            s = np.sin(2 * np.pi * ff * tt + ph) + 0.28 * np.sin(4 * np.pi * ff * tt + ph) + 0.08 * np.sin(6 * np.pi * ff * tt)
            s *= (1 + 0.15 * np.sin(2 * np.pi * rng.uniform(0.1, 0.3) * tt)) * e * 0.035
            place(music[:, 0], s * (1 - pan), start); place(music[:, 1], s * pan, start)
    b = (np.sin(2 * np.pi * hz(bass) * tt) + 0.2 * np.sin(4 * np.pi * hz(bass) * tt)) * e * 0.11
    place(music[:, 0], b, start); place(music[:, 1], b, start)
    start += CH; k += 1

# ---- bell arpeggio (enters after the intro, gentle), ping-pong panned
def bell(f, dur=2.2):
    n = int(dur * SR); tt = np.arange(n) / SR
    s = (np.sin(2 * np.pi * f * tt) * np.exp(-tt * 2.2) + 0.35 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 5)
         + 0.15 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt * 9))
    s[:80] *= np.linspace(0, 1, 80)
    return s

step = BEAT / 2
i = 0
tt0 = OFF + 2.0
while tt0 < TOTAL - 1.5:
    ci = int(tt0 // CH) % 4
    notes = chords[ci][1]
    pattern = [0, 2, 4, 1, 3, 2, 4, 3]
    m = notes[pattern[i % 8]] + 12
    # louder on the end card, quieter under dialogue
    g = 0.030 if tt0 < 82.76 + OFF else 0.055
    s = bell(hz(m)) * g
    pan = 0.25 if i % 2 == 0 else 0.75
    place(music[:, 0], s * (1 - pan) * 2, tt0); place(music[:, 1], s * pan * 2, tt0)
    tt0 += step; i += 1

# ---- soft pulse (felt more than heard) from the services section on
def thump():
    n = int(0.5 * SR); tt = np.arange(n) / SR
    f = 55 * np.exp(-tt * 6) + 40
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)
tp = OFF + 19.5
while tp < TOTAL - 2:
    g = 0.10 if tp < 82.76 + OFF else 0.14
    place(music[:, 0], thump() * g, tp); place(music[:, 1], thump() * g, tp)
    tp += BEAT * 2

# ---- master envelope: swell in intro, settle under voice, lift at end card, fade out
env = np.interp(t_all, [0, 1.0, OFF, OFF + 3, 82.76 + OFF - 1, 82.76 + OFF + 0.5, TOTAL - 3.5, TOTAL],
                [0.0, 0.9, 1.0, 0.75, 0.75, 1.15, 1.15, 0.0])
music *= env[:, None]

# ---- reverb (synthetic stereo IR)
irn = int(2.8 * SR); ti = np.arange(irn) / SR
ir = rng.standard_normal((irn, 2)) * np.exp(-ti * 2.4)[:, None]
ir = lp(ir, 6000); ir /= np.abs(ir).sum(axis=0) ** 0.5 * 25
wet = np.stack([fftconvolve(music[:, c], ir[:, c])[:N] for c in range(2)], 1)
music = lp(music * 0.7 + wet * 0.9, 9000)
music = hp(music, 35)

# ================= SFX =================
sfx = np.zeros((N, 2))
def whoosh(dur=0.9, lo=300, hi=5000, rev=False):
    n = int(dur * SR); tt = np.linspace(0, 1, n)
    x = rng.standard_normal(n)
    env = np.sin(np.pi * tt ** (0.6 if not rev else 1.6)) ** 2
    # sweeping band: mix fixed bands weighted around a moving centre frequency
    centres = np.geomspace(lo, hi, 8)
    sweep = np.log(lo) + (np.log(hi) - np.log(lo)) * (tt if not rev else 1 - tt)
    out = np.zeros(n)
    for fc in centres:
        w = np.exp(-((np.log(fc) - sweep) / 0.45) ** 2)
        out += bp(x, fc * 0.7, min(fc * 1.4, SR / 2 - 100)) * w
    out *= env
    pan = np.linspace(0.2, 0.8, n)
    return np.stack([out * (1 - pan), out * pan], 1) / (np.abs(out).max() + 1e-9)

def boom(dur=2.4):
    n = int(dur * SR); tt = np.arange(n) / SR
    f = 70 * np.exp(-tt * 3) + 32
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 2.0)
    s += lp(rng.standard_normal(n), 900) * np.exp(-tt * 18) * 0.5
    return np.stack([s, s], 1) / np.abs(s).max()

def shimmer(dur=2.5):
    n = int(dur * SR); out = np.zeros((n, 2))
    for j, m in enumerate([86, 90, 93, 97, 98, 102]):
        b = bell(hz(m), dur)[:n] * 0.5
        d = int(j * 0.06 * SR); p = j / 5
        out[d:, 0] += b[:n - d] * (1 - p); out[d:, 1] += b[:n - d] * p
    return out / np.abs(out).max()

S = lambda s: s + OFF  # source time -> timeline
place(sfx, boom(), 1.15, 0.55)                 # intro title
place(sfx, whoosh(1.2, 200, 3000), 0.55, 0.10)  # curtain / bars opening
place(sfx, whoosh(0.8, 400, 6000, True), OFF - 0.55, 0.12)  # into the host
for t0 in (0.6, 7.2, 20.35, 36.55, 52.8, 64.0, 71.3, 76.35):
    place(sfx, whoosh(0.75), S(t0) - 0.25, 0.10)
place(sfx, boom(), S(82.76) + 0.2, 0.45)
place(sfx, shimmer(), S(82.76) + 1.0, 0.10)
place(sfx, whoosh(1.0, 300, 7000), S(82.76 + 10.2) - 0.2, 0.11)
place(sfx, shimmer(), S(82.76 + 10.55), 0.09)

def write(name, x):
    wavfile.write(name, SR, (x / max(1.0, np.abs(x).max() / 0.95)).astype(np.float32))
write("music.wav", music)
write("sfx.wav", sfx)
print("peak music", np.abs(music).max(), "rms", np.sqrt((music ** 2).mean()))
