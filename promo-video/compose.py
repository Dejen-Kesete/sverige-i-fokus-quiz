# Builds the vertical 1080x1920 base video, one output frame per source frame (lip sync by construction).
# Usage: compose.py <lang> [first_frame last_frame]   -> vbase_<lang>.mp4 (video only)
import sys, json, subprocess, numpy as np, cv2
import broll

LANG = sys.argv[1]
FPS, W, H, SW, SH = 25, 1080, 1920, 1920, 1080
END0 = 82.76
fr = lambda t: int(round(t * FPS))

# ---- edit decision list: (start_s, end_s, kind, params). Times are source == output times.
EDL = [
    (0.00, 4.80, "host", dict(zoom=(1.0, 1.07))),
    (4.80, 10.68, "fit", dict(cx=930, w=900)),          # laptop typing admasstudio.se
    (10.68, 12.88, "host", dict(tight=True)),
    (12.88, 15.08, "crop", dict(cx=1090)),              # studio mic
    (15.08, 16.88, "host", dict()),
    (16.88, 18.64, "host", dict(tight=True)),
    (18.64, 25.00, "host", dict(zoom=(1.0, 1.05))),     # headphones, face-tracked
    (25.00, 27.80, "broll", dict(scene="wave")),
    (27.80, 30.44, "host", dict(tight=True)),
    (30.44, 32.60, "host", dict(tight=True)),
    (32.60, 36.44, "broll", dict(scene="translate")),
    (36.44, 43.08, "crop", dict(cx=1150, zoom=(1.0, 1.06))),  # book pages
    (43.08, 45.68, "crop", dict(cx=1090)),              # mic
    (45.68, 47.40, "host", dict()),
    (47.40, 49.00, "host", dict(tight=True)),
    (49.00, 52.64, "broll", dict(scene="counter")),
    (52.64, 62.64, "fit", dict(cx=960, w=720, zoom=(1.0, 1.08))),  # book on pedestal
    (62.64, 67.40, "broll", dict(scene="phone")),
    (67.40, 70.80, "fit", dict(cx=980, w=760)),         # sign-up button
    (70.80, 75.24, "fit", dict(cx=1150, w=1080)),       # Tigrinya key-word slides
    (75.24, 76.20, "host", dict(tight=True)),
    (76.20, 78.80, "crop", dict(cx=1250, zoom=(1.0, 1.05))),  # paperwork
    (78.80, 81.16, "broll", dict(scene="form")),
    (81.16, END0, "host", dict()),
    (END0, 103.00, "end", dict()),
]

# ---- smoothed face track (from faces_src.json, detected on 960x540)
F = json.load(open("faces_src.json")); sc = SW / F["w"]
N = fr(103.0)
fx = np.full(N, np.nan); fy = np.full(N, np.nan); fh = np.full(N, np.nan)
for i, b in enumerate(F["boxes"][:N]):
    if b: fx[i], fy[i], fh[i] = (b[0] + b[2] / 2) * sc, (b[1] + b[3] / 2) * sc, b[3] * sc

def track(a, b):
    """Face centre per frame for a segment: gaussian-smoothed detections, gaps filled."""
    i0, i1 = fr(a), fr(b); idx = np.arange(i0, i1)
    x, y, h = fx[i0:i1], fy[i0:i1], fh[i0:i1]
    ok = ~np.isnan(x)
    if ok.sum() < 3:
        return np.full(len(idx), 960.0), np.full(len(idx), 300.0), np.full(len(idx), 230.0)
    xs = np.interp(idx, idx[ok], x[ok]); ys = np.interp(idx, idx[ok], y[ok]); hs = np.interp(idx, idx[ok], h[ok])
    k = np.exp(-0.5 * (np.arange(-30, 31) / 12.0) ** 2); k /= k.sum()
    sm = lambda v: np.convolve(np.pad(v, 30, mode="edge"), k, "valid")
    return sm(xs), sm(ys), sm(hs)

tracks = {}
for a, b, kind, p in EDL:
    if kind == "host": tracks[(a, b)] = track(a, b)

def crop_resize(img, cx, cy_top, cw, ch, ow, oh):
    x0 = int(round(min(max(cx - cw / 2, 0), SW - cw))); y0 = int(round(min(max(cy_top, 0), SH - ch)))
    return cv2.resize(img[y0:y0 + int(ch), x0:x0 + int(cw)], (ow, oh), interpolation=cv2.INTER_LANCZOS4)

def blurred_bg(img, cx):
    # fill for letterboxed shots: same shot, cropped vertical, heavily blurred and darkened
    b = crop_resize(img, cx, 0, 608, 1080, 108, 192)
    b = cv2.GaussianBlur(b, (0, 0), 6)
    b = cv2.resize(b, (W, H), interpolation=cv2.INTER_CUBIC)
    return (b.astype(np.float32) * 0.42).astype(np.uint8)

def render(n, src, endf):
    t = n / FPS
    for a, b, kind, p in EDL:
        if fr(a) <= n < fr(b): break
    u = (n - fr(a)) / max(1, fr(b) - fr(a))  # 0..1 progress within the segment
    z0, z1 = p.get("zoom", (1.0, 1.0)); z = z0 + (z1 - z0) * u
    if kind == "host":
        xs, ys, hs = tracks[(a, b)]; k = n - fr(a)
        cx, fcy, fh_ = xs[k], ys[k], hs[k]
        if p.get("tight"):
            ch = 960 / z; cw = ch * W / H
            top = fcy - 0.30 * ch  # face in the upper third
        else:
            ch = 1080 / z; cw = ch * W / H
            top = (1080 - ch) * 0.3
        return crop_resize(src, cx, top, cw, ch, W, H)
    if kind == "crop":
        ch = 1080 / z; cw = ch * W / H
        return crop_resize(src, p["cx"], (1080 - ch) / 2, cw, ch, W, H)
    if kind == "fit":
        out = blurred_bg(src, p["cx"])
        cw = p["w"] / z; ch = 1080 / z
        oh = int(round(W * ch / cw)); oh -= oh % 2
        fg = crop_resize(src, p["cx"], (1080 - ch) / 2, cw, ch, W, oh)
        y0 = (H - oh) // 2
        # feather the top/bottom 28 px of the sharp picture into the blurred fill
        e = 28; ramp = (np.arange(oh, dtype=np.float32)[:, None, None])
        alpha = np.clip(np.minimum(ramp + 1, oh - ramp) / e, 0, 1)
        region = out[y0:y0 + oh].astype(np.float32)
        out[y0:y0 + oh] = (fg.astype(np.float32) * alpha + region * (1 - alpha)).astype(np.uint8)
        return out
    if kind == "broll":
        return broll.SCENES[p["scene"]](t - a, LANG, t)
    if kind == "end":
        return endf

def reader(path, w, h, start=0):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(start), "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                            stdout=subprocess.PIPE, bufsize=w * h * 3 * 4)

def main():
    first, last = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, N)
    out = f"vbase_{LANG}.mp4" if len(sys.argv) <= 3 else f"vtest_{LANG}.mp4"
    src = reader("graded.mp4", SW, SH, first / FPS)
    endr = None
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "libx264", "-preset", "fast", "-crf", "12", "-pix_fmt", "yuv420p", out],
                           stdin=subprocess.PIPE)
    for n in range(first, last):
        buf = src.stdout.read(SW * SH * 3)
        if len(buf) < SW * SH * 3: raise SystemExit(f"source ended early at frame {n}")
        img = np.frombuffer(buf, np.uint8).reshape(SH, SW, 3)
        endf = None
        if n >= fr(END0):
            if endr is None: endr = reader("endbg_v.mp4", W, H, max(0, (n - fr(END0)) / FPS))
            endf = np.frombuffer(endr.stdout.read(W * H * 3), np.uint8).reshape(H, W, 3)
        frame = render(n, img, endf)
        assert frame.shape == (H, W, 3), (n, frame.shape)
        enc.stdin.write(np.ascontiguousarray(frame).tobytes())
        if n % 250 == 0: print("frame", n, flush=True)
    enc.stdin.close(); enc.wait(); print("wrote", out, last - first, "frames")

if __name__ == "__main__":
    main()
