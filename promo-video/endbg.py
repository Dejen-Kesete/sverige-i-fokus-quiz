# Renders the animated end-card background: navy gradient, drifting gold bokeh,
# light sweep, and a circular studio-mic logo with a gold ring.
import numpy as np, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter

W, H, FPS = 1920, 1080, 25
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 20.24
N = int(round(DUR * FPS))
OUT = sys.argv[3] if len(sys.argv) > 3 else "endbg.mp4"
USE_LOGO = OUT == "endbg.mp4"
rng = np.random.default_rng(7 if USE_LOGO else 21)

# --- background gradient
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.42) / (H * 0.75)) ** 2)
r = np.clip(r, 0, 1)
c_in = np.array([27, 40, 70], np.float32) / 255
c_out = np.array([4, 7, 14], np.float32) / 255
bg = (c_in[None, None] * (1 - r[..., None] ** 1.3) + c_out[None, None] * (r[..., None] ** 1.3)).astype(np.float32)

# --- sprites
def sprite(size, sharp):
    s = int(size * 2 + 2)
    y, x = np.mgrid[0:s, 0:s].astype(np.float32) - (s - 1) / 2
    d = np.sqrt(x * x + y * y) / size
    if sharp:
        a = np.exp(-(d * 2.2) ** 2) + 0.35 * np.exp(-(d * 0.9) ** 2)
    else:  # bokeh disc with soft edge + slightly brighter rim
        a = np.clip((1 - d) * 3, 0, 1) * (0.75 + 0.25 * np.clip((d - 0.6) * 3, 0, 1))
        a = np.array(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(size * 0.12)), np.float32) / 255
    return a / max(a.max(), 1e-6)

golds = np.array([[1.0, 0.74, 0.36], [0.98, 0.64, 0.24], [1.0, 0.84, 0.52], [0.90, 0.56, 0.20]], np.float32)
parts = []
def add(n, smin, smax, amin, amax, speed, sharp):
    for _ in range(n):
        size = rng.uniform(smin, smax)
        parts.append(dict(
            spr=sprite(size, sharp), x=rng.uniform(-100, W + 100), y=rng.uniform(-100, H + 100),
            vx=rng.uniform(-0.2, 0.6) * speed, vy=-rng.uniform(0.4, 1.0) * speed,
            a=rng.uniform(amin, amax), col=golds[rng.integers(0, 4)],
            tw=rng.uniform(0.3, 1.4), ph=rng.uniform(0, 6.28), sway=rng.uniform(0, 12)))
add(260, 1.2, 3.0, 0.35, 1.0, 14, True)      # fine sparkles
add(55, 8, 22, 0.14, 0.34, 22, False)       # mid bokeh
add(14, 45, 90, 0.04, 0.10, 32, False)      # large foreground bokeh

# --- logo (studio mic still, circular)
LOGO_D = 232
src = Image.open(sys.argv[2] if len(sys.argv) > 2 else "st/logo_mic.png").convert("RGB")
sw, sh = src.size
side = min(sw, sh)
# crop square around the microphone (it sits roughly centre-left of the frame)
cx = int(sw * 0.57)
logo_base = src.crop((cx - side // 2, 0, cx + side // 2, side))
mask_big = Image.new("L", (LOGO_D * 4, LOGO_D * 4), 0)
ImageDraw.Draw(mask_big).ellipse((0, 0, LOGO_D * 4 - 1, LOGO_D * 4 - 1), fill=255)
mask = np.array(mask_big.resize((LOGO_D, LOGO_D), Image.LANCZOS), np.float32) / 255
# gold ring + outer glow
R = LOGO_D + 60
ry, rx = np.mgrid[0:R, 0:R].astype(np.float32) - (R - 1) / 2
rd = np.sqrt(rx * rx + ry * ry)
ring = np.clip(1 - np.abs(rd - LOGO_D / 2 - 3) / 2.2, 0, 1)
glow = np.exp(-((rd - LOGO_D / 2) / 16) ** 2) * 0.35 * (rd > LOGO_D / 2)
LOGO_CX, LOGO_CY = W // 2, 318

def ease_out_back(t):
    c1 = 1.4; c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

def smooth(t):
    t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)

ff = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                       "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "12",
                       "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
for f in range(N):
    t = f / FPS
    img = bg.copy()
    for p in parts:
        s = p["spr"]; hs = s.shape[0]
        x = (p["x"] + p["vx"] * t + p["sway"] * np.sin(t * 0.7 + p["ph"])) % (W + 200) - 100
        y = (p["y"] + p["vy"] * t) % (H + 200) - 100
        a = p["a"] * (0.55 + 0.45 * np.sin(t * p["tw"] * 2.5 + p["ph"]))
        x0, y0 = int(x - hs / 2), int(y - hs / 2)
        xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + hs, W), min(y0 + hs, H)
        if xa >= xb or ya >= yb: continue
        img[ya:yb, xa:xb] += s[ya - y0:yb - y0, xa - x0:xb - x0, None] * (p["col"] * a)
    # diagonal light sweep at the start and at the CTA change
    for t0 in ((0.2, 10.3) if USE_LOGO else (1.1,)):
        k = (t - t0) / 1.6
        if 0 <= k <= 1:
            pos = -600 + k * (W + 1200)
            band = np.exp(-(((xx + (yy - H / 2) * 0.45) - pos) / 170) ** 2) * np.sin(np.pi * k) * 0.22
            img += band[..., None] * np.array([1.0, 0.8, 0.5], np.float32)
    # logo
    k = smooth((t - 0.35) / 0.9) if USE_LOGO else 0
    if k > 0:
        sc = ease_out_back(min(max((t - 0.35) / 0.9, 0), 1))
        zoom = 1.0 + 0.10 * (t / DUR)
        crop = logo_base.size[0] / zoom
        o = (logo_base.size[0] - crop) / 2
        d = max(int(LOGO_D * sc), 2)
        li = np.array(logo_base.resize((LOGO_D, LOGO_D), Image.LANCZOS, box=(o, o, o + crop, o + crop)), np.float32) / 255
        li = li * np.array([1.02, 0.98, 0.9], np.float32)  # warm it toward the brand gold
        layer = np.zeros((R, R, 4), np.float32)
        off = (R - LOGO_D) // 2
        layer[off:off + LOGO_D, off:off + LOGO_D, :3] = li
        layer[off:off + LOGO_D, off:off + LOGO_D, 3] = mask
        gcol = np.array([0.93, 0.76, 0.45], np.float32)
        ra = np.clip(ring + glow, 0, 1)
        layer[..., :3] = layer[..., :3] * (1 - ra[..., None]) + gcol * ra[..., None]
        layer[..., 3] = np.maximum(layer[..., 3], ra)
        if d != LOGO_D:
            rs = max(int(R * sc), 2)
            layer = np.array(Image.fromarray((np.clip(layer, 0, 1) * 255).astype(np.uint8), "RGBA").resize((rs, rs), Image.LANCZOS), np.float32) / 255
        rs = layer.shape[0]
        x0, y0 = LOGO_CX - rs // 2, LOGO_CY - rs // 2
        al = layer[..., 3:4] * k
        img[y0:y0 + rs, x0:x0 + rs] = img[y0:y0 + rs, x0:x0 + rs] * (1 - al) + layer[..., :3] * al
    ff.stdin.write((np.clip(img, 0, 1) * 255).astype(np.uint8).tobytes())
ff.stdin.close(); ff.wait()
print("done", N)
