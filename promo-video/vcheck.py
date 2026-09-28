# Strict picture-sync test for the vertical cut.
# For sampled output frames n inside on-camera segments, rebuild the frame from source frames n+L
# (L = -4..+4) with the same reframing code and compare with the actual output frame (top 55%,
# away from graphics). If the cut is in sync, L = 0 must match best.
# Usage: vcheck.py <vertical.mp4> <lang>
import sys, subprocess, numpy as np
sys.argv = [sys.argv[0], sys.argv[2], "_", sys.argv[1]]  # compose.py reads LANG from argv[1]
import compose
out = sys.argv[3]
W, H, SW, SH, FPS = 1080, 1920, 1920, 1080, 25

def grab(path, n, w, h, count=1):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{n / FPS:.3f}", "-i", path, "-frames:v", str(count),
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)

segs = [(0.5, 4.6), (10.8, 12.8), (15.2, 18.5), (19.5, 24.8), (28.0, 32.5), (45.8, 48.9), (75.3, 76.1), (81.3, 82.6)]
worst = 0
for a, b in segs:
    for n in np.linspace(int(a * FPS) + 5, int(b * FPS) - 5, 3).astype(int):
        o = grab(out, n, W, H)[0][150:1050].astype(np.float32)
        srcs = grab("graded.mp4", n - 4, SW, SH, 9)
        errs = []
        for L in range(-4, 5):
            r = compose.render(n, srcs[L + 4], None)[150:1050].astype(np.float32)
            errs.append(np.abs(r - o).mean())
        best = int(np.argmin(errs)) - 4; worst = max(worst, abs(best))
        e = sorted(errs)
        print(f"t={n / FPS:6.2f}s  best source frame offset {best:+d}   error at 0: {errs[4]:.2f}  next best: {e[1]:.2f}")
print("MAX OFFSET (frames):", worst)
