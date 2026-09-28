# Sample-exact audio mix: processed voice placed at a fixed offset, ducked score, SFX.
# Usage: mix.py <voice.wav> <music.wav> <sfx.wav> <offset_seconds> <total_seconds> <out.wav>
# (Alignment is done on raw samples, never on ffmpeg timestamps, so lip sync cannot drift.)
import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import lfilter

vf, mf, sf, off, tot, out = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
SR = 44100

def load(p):
    sr, x = wavfile.read(p); assert sr == SR, (p, sr)
    x = x.astype(np.float32)
    if x.ndim == 1: x = np.stack([x, x], 1)
    return x

N = int(round(tot * SR))
def fit(x):
    y = np.zeros((N, 2), np.float32); n = min(N, len(x)); y[:n] = x[:n]; return y

voice = np.zeros((N, 2), np.float32)
v = load(vf); o = int(round(off * SR))
n = min(len(v), N - o); voice[o:o + n] = v[:n]
music, sfx = fit(load(mf)), fit(load(sf))

# ducking: envelope follower on the voice (30 ms attack, 500 ms release) -> up to -7 dB on the score
lvl = np.abs(voice).max(1)
a_att, a_rel = np.exp(-1 / (0.03 * SR)), np.exp(-1 / (0.5 * SR))
env = np.zeros(N, np.float32); e = 0.0
step = 64  # block-wise follower is plenty for ducking
for i in range(0, N, step):
    x = lvl[i:i + step].max()
    e = x + (e - x) * (a_att ** step if x > e else a_rel ** step)
    env[i:i + step] = e
duck = 1.0 - 0.55 * np.clip(env / 0.08, 0, 1)
mix = voice + music * (10 ** (-3 / 20)) * duck[:, None] + sfx
wavfile.write(out, SR, mix.astype(np.float32))
print("wrote", out, f"{N/SR:.3f}s, voice at {o/SR:.3f}s")
