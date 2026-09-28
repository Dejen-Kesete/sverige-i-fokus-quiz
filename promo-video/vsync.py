# Verifies lip sync of the vertical cut against the source.
# Usage: vsync.py <vertical.mp4>
# Audio: finds where the source voice sits in the output (should be +0 ms).
# Video: for each on-camera segment, matches the output's motion pattern to the source
#        (around the face) and reports the frame offset (should be 0).
import sys, json, subprocess, numpy as np

out = sys.argv[1]
SR, FPS = 44100, 25
def A(v): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", v, "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                             capture_output=True).stdout, np.float32)
voice, o = A("voice.wav"), A(out)
for t in (2, 17, 31, 47, 76, 82):
    s = voice[int(t * SR):int((t + 1.5) * SR)]
    c = [np.dot(s, o[int(t * SR) + L:int(t * SR) + L + len(s)]) for L in range(-2205, 2206, 1)]
    print(f"audio  src {t:5.1f}s: offset {(int(np.argmax(c)) - 2205) / SR * 1000:+.2f} ms")

def motion(v, vf):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", v, "-vf", f"fps={FPS},{vf},format=gray", "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    return raw
# output: centre band of the vertical frame (face area) at low res
ro = motion(out, "crop=1080:1100:0:100,scale=54:55")
fo = np.frombuffer(ro, np.uint8).reshape(-1, 55, 54).astype(np.float32)
# source: vertical-ish window around the face
rs = motion("src.mov", "crop=608:1080:656:0,scale=54:96")
fs = np.frombuffer(rs, np.uint8).reshape(-1, 96, 54).astype(np.float32)
mo = np.abs(np.diff(fo, axis=0)).mean((1, 2)); ms = np.abs(np.diff(fs, axis=0)).mean((1, 2))
host = [(0.5, 4.7), (10.8, 12.8), (15.2, 18.5), (30.6, 32.5), (45.8, 48.9), (81.2, 82.7)]
for a, b in host:
    i0, i1 = int(a * FPS), int(b * FPS)
    x = mo[i0:i1]; x = (x - x.mean()) / (x.std() + 1e-6)
    best = max(range(-8, 9), key=lambda L: np.dot(x, (ms[i0 + L:i1 + L] - ms[i0 + L:i1 + L].mean()) / (ms[i0 + L:i1 + L].std() + 1e-6)))
    y = ms[i0 + best:i1 + best]; r = np.corrcoef(x, y)[0, 1]
    print(f"video  src {a:5.1f}-{b:5.1f}s: frame offset {best:+d} ({best*40:+d} ms), motion match r={r:.2f}")
