# Animated B-roll scenes for the vertical (1080x1920) promo, drawn frame by frame.
# Each scene is a function (t_local, lang) -> RGB uint8 array (1920, 1080, 3).
import numpy as np, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.io import wavfile

W, H = 1080, 1920
FD = "sf/"
_fc = {}
def F(name, size):
    k = (name, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(FD + name + ".ttf", size)
    return _fc[k]

GOLD, GOLD_L, WHITE, NAVY = (217, 180, 108), (241, 220, 167), (255, 255, 255), (11, 20, 38)
MUTED = (194, 204, 214)

S = {
 "en": dict(tr_k="02  ·  TRANSLATION", tr_h="Swedish & English", tr_h2="into Tigrinya",
            ct_k="03  ·  CITIZENSHIP TEST", ct_l="PRACTICE QUESTIONS",
            q_k="SVERIGE I FOKUS  ·  QUIZ", q_h="Practice with clear explanations",
            dc_k="04  ·  DOCUMENTS", dc_h="Your application",
            dc_list=["Citizenship application", "Family reunification", "Residence permit extension", "CV & cover letter", "Other official documents"],
            stamp="READY TO SUBMIT", vo_l="VOICE-OVER"),
 "sv": dict(tr_k="02  ·  ÖVERSÄTTNING", tr_h="Svenska & engelska", tr_h2="till tigrinja",
            ct_k="03  ·  MEDBORGARSKAPSPROVET", ct_l="ÖVNINGSFRÅGOR",
            q_k="SVERIGE I FOKUS  ·  QUIZ", q_h="Öva med tydliga förklaringar",
            dc_k="04  ·  MYNDIGHETSÄRENDEN", dc_h="Din ansökan",
            dc_list=["Ansökan om medborgarskap", "Familjeåterförening", "Förlängning av uppehållstillstånd", "CV & personligt brev", "Andra myndighetsdokument"],
            stamp="KLAR ATT SKICKA IN", vo_l="VOICE-OVER"),
}

def clamp01(x): return max(0.0, min(1.0, x))
def eout(x): x = clamp01(x); return 1 - (1 - x) ** 3
def eback(x):
    x = clamp01(x); c1 = 1.5; c3 = c1 + 1; return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def fade(t, t0, d=0.35): return eout((t - t0) / d)

# ---------------- background: navy gradient + drifting gold particles (shared by all scenes)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.clip(np.sqrt(((xx - W / 2) / (W * 0.95)) ** 2 + ((yy - H * 0.42) / (H * 0.62)) ** 2), 0, 1) ** 1.3
BG = (np.array([27, 40, 70], np.float32)[None, None] / 255 * (1 - _r[..., None]) +
      np.array([4, 7, 14], np.float32)[None, None] / 255 * _r[..., None]).astype(np.float32)
_rng = np.random.default_rng(11)
def _sprite(size, sharp):
    s = int(size * 2 + 2); y, x = np.mgrid[0:s, 0:s].astype(np.float32) - (s - 1) / 2
    d = np.sqrt(x * x + y * y) / size
    a = (np.exp(-(d * 2.2) ** 2) + 0.35 * np.exp(-(d * 0.9) ** 2)) if sharp else np.clip((1 - d) * 3, 0, 1) * 0.8
    return (a / a.max()).astype(np.float32)
_golds = np.array([[1.0, 0.74, 0.36], [0.98, 0.64, 0.24], [1.0, 0.84, 0.52]], np.float32)
PARTS = []
for n, smin, smax, amin, amax, sp, sharp in ((150, 1.2, 3.0, 0.3, 0.9, 16, True), (30, 8, 20, 0.08, 0.22, 24, False)):
    for _ in range(n):
        size = _rng.uniform(smin, smax)
        PARTS.append((_sprite(size, sharp), _rng.uniform(0, W), _rng.uniform(0, H), _rng.uniform(-0.2, 0.5) * sp,
                      -_rng.uniform(0.4, 1.0) * sp, _rng.uniform(amin, amax), _golds[_rng.integers(0, 3)], _rng.uniform(0, 6.28)))

def background(tg):
    img = BG.copy()
    for spr, x, y, vx, vy, a, col, ph in PARTS:
        hs = spr.shape[0]
        px = (x + vx * tg) % (W + 100) - 50; py = (y + vy * tg) % (H + 100) - 50
        aa = a * (0.6 + 0.4 * math.sin(tg * 2 + ph))
        x0, y0 = int(px - hs / 2), int(py - hs / 2)
        xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + hs, W), min(y0 + hs, H)
        if xa < xb and ya < yb:
            img[ya:yb, xa:xb] += spr[ya - y0:yb - y0, xa - x0:xb - x0, None] * (col * aa)
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).convert("RGBA")

def text(d, xy, s, font, fill, a=1.0, anchor="la", spacing=0):
    if a <= 0: return
    col = tuple(fill[:3]) + (int(255 * clamp01(a)),)
    if spacing == 0:
        d.text(xy, s, font=font, fill=col, anchor=anchor); return
    # letter-spaced text: measure, then draw per character
    widths = [font.getlength(c) for c in s]; total = sum(widths) + spacing * (len(s) - 1)
    x, y = xy
    if anchor[0] == "m": x -= total / 2
    elif anchor[0] == "r": x -= total
    for c, w in zip(s, widths):
        d.text((x, y), c, font=font, fill=col, anchor="l" + anchor[1]); x += w + spacing

def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)

def over(base, layer): return Image.alpha_composite(base, layer)

def kicker(d, s, t, y=300):
    a = fade(t, 0.05)
    text(d, (W / 2, y), s, F("ASMontMedium", 30), GOLD, a, "mm", spacing=8)
    w = 90 * eout((t - 0.15) / 0.5)
    d.rectangle((W / 2 - w / 2, y + 36, W / 2 + w / 2, y + 38), fill=GOLD + (int(255 * a),))

# ---------------- B1: live voice spectrum (uses the real voice at that moment)
_voice = None
def _voice_arr():
    global _voice
    if _voice is None:
        sr, x = wavfile.read("voice.wav"); x = x.astype(np.float32)
        _voice = (sr, x.mean(1) if x.ndim > 1 else x)
    return _voice

def b_wave(t, lang, tsrc):
    sr, v = _voice_arr()
    img = background(tsrc); L = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(L)
    # REC indicator + timecode
    if int(t * 2) % 2 == 0: d.ellipse((96, 286, 124, 314), fill=(226, 60, 60, 255))
    text(d, (140, 300), "REC", F("ASMontBold", 30), WHITE, 1, "lm", spacing=4)
    fr = int(round(tsrc * 25))
    tc = f"00:{fr // 1500:02d}:{fr // 25 % 60:02d}:{fr % 25:02d}"
    text(d, (W - 96, 300), tc, F("ASMontMedium", 30), MUTED, 1, "rm", spacing=2)
    # spectrum bars from a 2048-sample window centred on this frame
    n = 2048; c = int(tsrc * sr); seg = v[max(0, c - n // 2):c + n // 2]
    seg = np.pad(seg, (0, n - len(seg))) * np.hanning(n)
    sp = np.abs(np.fft.rfft(seg)); fr_hz = np.fft.rfftfreq(n, 1 / sr)
    NB = 48; edges = np.geomspace(90, 7000, NB + 1)
    bands = np.array([sp[(fr_hz >= edges[i]) & (fr_hz < edges[i + 1])].mean()
                      if ((fr_hz >= edges[i]) & (fr_hz < edges[i + 1])).any()
                      else sp[int(np.argmin(np.abs(fr_hz - edges[i])))] for i in range(NB)])
    bands = bands * (0.5 * (edges[:-1] + edges[1:]) / 250) ** 0.9  # tilt: lift the quieter highs
    lvl = np.clip((20 * np.log10(bands + 1e-6) + 8) / 52, 0.03, 1.0)
    cy = 860; bw = 12; gap = (W - 160 - NB * bw) / (NB - 1)
    k = eout(t / 0.4)
    for i, l in enumerate(lvl):
        x = 80 + i * (bw + gap); h = 18 + l * 330 * k
        g = i / (NB - 1); col = tuple(int(GOLD[j] * (1 - g * 0.25) + GOLD_L[j] * g * 0.25) for j in range(3))
        rrect(d, (x, cy - h, x + bw, cy + h), bw // 2, fill=col + (235,))
    text(d, (W / 2, 1290), S[lang]["vo_l"], F("ASMontMedium", 34), GOLD, fade(t, 0.2), "mm", spacing=10)
    text(d, (W / 2, 1380), "ትግርኛ", F("ASEthiopic", 72), WHITE, fade(t, 0.35), "mm")
    return np.array(over(img, L).convert("RGB"))

# ---------------- B2: Swedish -> Tigrinya translation
SV_LINE = "Demokrati betyder folkstyre."
TI_LINES = ["ዲሞክራሲ ማለት", "ህዝባዊ ምሕደራ ማለት'ዩ"]
def b_translate(t, lang, tsrc):
    s = S[lang]; img = background(tsrc); L = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(L)
    kicker(d, s["tr_k"], t)
    text(d, (W / 2, 410), s["tr_h"], F("ASPlayfairBold", 64), WHITE, fade(t, 0.15), "mm")
    text(d, (W / 2, 490), s["tr_h2"], F("ASPlayfair", 52), GOLD_L, fade(t, 0.3), "mm")
    # card 1: Swedish, typed
    a1 = fade(t, 0.3, 0.4); dy = 40 * (1 - a1)
    rrect(d, (90, 590 + dy, 990, 800 + dy), 28, fill=(27, 42, 72, int(235 * a1)), outline=GOLD + (int(120 * a1),), width=2)
    text(d, (130, 640 + dy), "SVENSKA", F("ASMontMedium", 26), GOLD, a1, "lm", spacing=6)
    nch = int(len(SV_LINE) * clamp01((t - 0.55) / 1.0))
    typed = SV_LINE[:nch]
    fnt = F("ASPlayfair", 52)
    text(d, (130, 725 + dy), typed, fnt, WHITE, a1, "lm")
    if t < 2.0 and int(t * 4) % 2 == 0 and a1 > 0.5:
        cx = 130 + fnt.getlength(typed) + 6
        d.rectangle((cx, 695 + dy, cx + 4, 755 + dy), fill=GOLD + (255,))
    # arrow
    a2 = fade(t, 1.6, 0.3)
    if a2 > 0:
        cy = 880; r = 48 * eback((t - 1.6) / 0.35)
        d.ellipse((W / 2 - r, cy - r, W / 2 + r, cy + r), fill=GOLD + (int(255 * a2),))
        d.polygon([(W / 2 - 18, cy - 8), (W / 2 + 18, cy - 8), (W / 2, cy + 16)], fill=NAVY + (int(255 * a2),))
        d.rectangle((W / 2 - 5, cy - 26, W / 2 + 5, cy - 6), fill=NAVY + (int(255 * a2),))
    # card 2: Tigrinya, word by word
    a3 = fade(t, 1.8, 0.4); dy = 40 * (1 - a3)
    rrect(d, (90, 960 + dy, 990, 1290 + dy), 28, fill=(27, 42, 72, int(235 * a3)), outline=GOLD + (int(120 * a3),), width=2)
    text(d, (130, 1010 + dy), "ትግርኛ", F("ASEthiopic", 30), GOLD, a3, "lm")
    words = [w for line in TI_LINES for w in line.split(" ")]
    shown = clamp01((t - 2.1) / 1.1) * len(words)
    fe = F("ASEthiopic", 56); i = 0
    for li, line in enumerate(TI_LINES):
        x = 130
        for w in line.split(" "):
            aw = clamp01(shown - i) * a3
            text(d, (x, 1105 + li * 90 + dy + 10 * (1 - aw)), w, fe, WHITE, aw, "lm")
            x += fe.getlength(w + " "); i += 1
    return np.array(over(img, L).convert("RGB"))

# ---------------- B3: 200+ counter ring
def b_counter(t, lang, tsrc):
    s = S[lang]; img = background(tsrc); L = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(L)
    kicker(d, s["ct_k"], t)
    cx, cy, R = W // 2, 800, 300
    p = eout((t - 0.25) / 2.0)
    # ring drawn at 2x for smooth edges
    ring = Image.new("RGBA", ((2 * R + 60) * 2,) * 2); rd = ImageDraw.Draw(ring); o = 60
    rd.ellipse((o, o, ring.size[0] - o, ring.size[1] - o), outline=(255, 255, 255, 40), width=28)
    if p > 0: rd.arc((o, o, ring.size[0] - o, ring.size[1] - o), -90, -90 + 360 * p, fill=GOLD + (255,), width=28)
    ring = ring.resize(((2 * R + 60),) * 2, Image.LANCZOS)
    L.alpha_composite(ring, (cx - R - 30, cy - R - 30))
    n = int(round(200 * p))
    fnum = F("ASPlayfairBold", 200)
    a = fade(t, 0.1)
    num = f"{n}"
    wnum = fnum.getlength(num)
    plus_a = fade(t, 2.2, 0.25)
    text(d, (cx - (fnum.getlength("+") * 0.55 * plus_a) / 2, cy - 10), num, fnum, WHITE, a, "mm")
    if plus_a > 0:
        sc = eback((t - 2.2) / 0.3)
        fp = F("ASPlayfairBold", max(10, int(150 * sc)))
        text(d, (cx + wnum / 2 - fnum.getlength("+") * 0.25 * plus_a + 50, cy - 20), "+", fp, GOLD, plus_a, "mm")
    text(d, (W / 2, 1200), s["ct_l"], F("ASMontBold", 40), GOLD, fade(t, 0.5), "mm", spacing=8)
    text(d, (W / 2, 1285), "Sverige i fokus", F("ASPlayfair", 60), WHITE, fade(t, 0.8), "mm")
    return np.array(over(img, L).convert("RGB"))

# ---------------- B4: phone quiz demo (UI copy is Swedish, like the product)
def wrap(s, font, width):
    out, line = [], ""
    for w in s.split(" "):
        tst = (line + " " + w).strip()
        if font.getlength(tst) <= width: line = tst
        else: out.append(line); line = w
    out.append(line); return out

def b_phone(t, lang, tsrc):
    s = S[lang]; img = background(tsrc); L = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(L)
    kicker(d, s["q_k"], t, y=270)
    text(d, (W / 2, 350), s["q_h"], F("ASPlayfair", 50), WHITE, fade(t, 0.15), "mm")
    a = fade(t, 0.1, 0.55); dy = int(160 * (1 - a))
    X0, Y0, X1, Y1 = 225, 430 + dy, 855, 1560 + dy
    ph = Image.new("RGBA", (W, H)); pd = ImageDraw.Draw(ph)
    rrect(pd, (X0 - 6, Y0 - 6, X1 + 6, Y1 + 6), 86, fill=(60, 66, 82, 255))
    rrect(pd, (X0, Y0, X1, Y1), 80, fill=(8, 11, 18, 255))
    sx0, sy0, sx1, sy1 = X0 + 18, Y0 + 18, X1 - 18, Y1 - 18
    rrect(pd, (sx0, sy0, sx1, sy1), 64, fill=(14, 26, 51, 255))
    rrect(pd, (W / 2 - 70, sy0 + 16, W / 2 + 70, sy0 + 50), 17, fill=(0, 0, 0, 255))
    text(pd, (sx0 + 44, sy0 + 34), "9:41", F("ASMontBold", 24), WHITE, 1, "lm")
    x = sx0 + 40; y = sy0 + 110
    text(pd, (x, y), "Sverige i fokus", F("ASPlayfairBold", 44), WHITE, 1, "lm")
    text(pd, (x, y + 52), "ÖVNINGSQUIZ", F("ASMontMedium", 20), GOLD, 1, "lm", spacing=5)
    text(pd, (x, y + 120), "Fråga 12 av 200", F("ASMontMedium", 22), MUTED, 1, "lm")
    rrect(pd, (x, y + 145, sx1 - 40, y + 155), 5, fill=(255, 255, 255, 40))
    rrect(pd, (x, y + 145, x + (sx1 - 40 - x) * 0.06, y + 155), 5, fill=GOLD + (255,))
    fq = F("ASMontBold", 36); qy = y + 215
    for i, ln in enumerate(wrap("Hur ofta hålls val till riksdagen i Sverige?", fq, sx1 - 40 - x)):
        text(pd, (x, qy + i * 48), ln, fq, WHITE, 1, "lm")
    opts = ["Vart tredje år", "Vart fjärde år", "Vart femte år"]
    oy = qy + 170; tap = 2.0
    for i, o in enumerate(opts):
        ai = fade(t, 0.6 + 0.15 * i, 0.3)
        by = oy + i * 112
        correct = (i == 1 and t >= tap)
        fill = (38, 125, 80, 255) if correct else (22, 37, 74, int(255 * ai))
        outl = (90, 200, 140, 255) if correct else (46, 65, 112, int(255 * ai))
        rrect(pd, (x, by, sx1 - 40, by + 92), 22, fill=fill, outline=outl, width=2)
        text(pd, (x + 30, by + 46), o, F("ASMontMedium", 32), WHITE, ai, "lm")
        if correct:
            k = eback((t - tap) / 0.3); cxk, cyk = sx1 - 90, by + 46
            pts = [(cxk - 16 * k, cyk), (cxk - 5 * k, cyk + 12 * k), (cxk + 18 * k, cyk - 13 * k)]
            pd.line(pts, fill=WHITE + (255,), width=6, joint="curve")
    # tap ripple
    if tap - 0.25 <= t <= tap + 0.45:
        k = clamp01((t - tap + 0.25) / 0.7); r = 20 + 90 * k
        cxr, cyr = x + 330, oy + 112 + 46
        pd.ellipse((cxr - r, cyr - r, cxr + r, cyr + r), outline=(255, 255, 255, int(200 * (1 - k))), width=5)
        pd.ellipse((cxr - 22, cyr - 22, cxr + 22, cyr + 22), fill=(255, 255, 255, int(160 * (1 - k))))
    # explanation
    ae = fade(t, 2.45, 0.35)
    if ae > 0:
        ey = oy + 3 * 112 + 20 + int(20 * (1 - ae))
        rrect(pd, (x, ey, sx1 - 40, ey + 150), 18, fill=(255, 255, 255, int(18 * ae)))
        pd.rectangle((x, ey, x + 6, ey + 150), fill=GOLD + (int(255 * ae),))
        text(pd, (x + 28, ey + 40), "Rätt!", F("ASMontBold", 30), (110, 220, 150), ae, "lm")
        fe = F("ASMontMedium", 26)
        for i, ln in enumerate(wrap("Riksdagsval hålls vart fjärde år, i september.", fe, sx1 - 40 - x - 50)):
            text(pd, (x + 28, ey + 86 + i * 34), ln, fe, (230, 232, 238), ae, "lm")
    ph.putalpha(Image.fromarray((np.array(ph.split()[3], np.float32) * a).astype(np.uint8)))
    L.alpha_composite(ph)
    return np.array(over(img, L).convert("RGB"))

# ---------------- B5: application checklist + stamp
def b_form(t, lang, tsrc):
    s = S[lang]; img = background(tsrc); L = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(L)
    kicker(d, s["dc_k"], t)
    a = fade(t, 0.0, 0.35); dy = int(80 * (1 - a))
    card = Image.new("RGBA", (W, H)); cd = ImageDraw.Draw(card)
    X0, Y0, X1, Y1 = 110, 420 + dy, 970, 1440 + dy
    rrect(cd, (X0 + 10, Y0 + 16, X1 + 10, Y1 + 16), 26, fill=(0, 0, 0, 90))
    card = card.filter(ImageFilter.GaussianBlur(14)); cd = ImageDraw.Draw(card)
    rrect(cd, (X0, Y0, X1, Y1), 26, fill=(246, 243, 236, 255))
    text(cd, (X0 + 60, Y0 + 90), s["dc_h"], F("ASPlayfairBold", 56), NAVY, 1, "lm")
    cd.rectangle((X0 + 60, Y0 + 145, X0 + 160, Y0 + 149), fill=GOLD + (255,))
    for i, it in enumerate(s["dc_list"]):
        ry = Y0 + 230 + i * 125
        cd.rounded_rectangle((X0 + 60, ry - 26, X0 + 112, ry + 26), 10, outline=(150, 160, 175, 255), width=3)
        text(cd, (X0 + 140, ry), it, F("ASMontMedium", 33), (30, 40, 60), 1, "lm")
        cd.line((X0 + 140, ry + 44, X1 - 60, ry + 44), fill=(220, 214, 200, 255), width=2)
        tk = 0.3 + 0.2 * i
        if t >= tk:
            k = eback((t - tk) / 0.25); cx, cy = X0 + 86, ry
            cd.rounded_rectangle((X0 + 60, ry - 26, X0 + 112, ry + 26), 10, fill=(38, 125, 80, 255))
            cd.line([(cx - 13 * k, cy), (cx - 4 * k, cy + 10 * k), (cx + 14 * k, cy - 11 * k)], fill=WHITE + (255,), width=6)
    card.putalpha(Image.fromarray((np.array(card.split()[3], np.float32) * a).astype(np.uint8)))
    L.alpha_composite(card)
    # stamp
    ts = 1.45
    if t >= ts:
        k = clamp01((t - ts) / 0.22); sc = 1.7 - 0.7 * eout(k)
        fs = F("ASMontXBold", 44); tw = fs.getlength(s["stamp"]) + 70
        st = Image.new("RGBA", (int(tw) + 40, 150)); sd = ImageDraw.Draw(st)
        col = (38, 125, 80)
        sd.rounded_rectangle((20, 20, st.size[0] - 20, 130), 16, outline=col + (255,), width=7)
        text(sd, (st.size[0] / 2, 76), s["stamp"], fs, col, 1, "mm", spacing=3)
        st = st.rotate(-10, expand=True, resample=Image.BICUBIC)
        st = st.resize((int(st.size[0] * sc), int(st.size[1] * sc)), Image.LANCZOS)
        st.putalpha(Image.fromarray((np.array(st.split()[3], np.float32) * k * 0.95).astype(np.uint8)))
        L.alpha_composite(st, (int(W / 2 - st.size[0] / 2 + 40), int(1330 + dy - st.size[1] / 2)))
    return np.array(over(img, L).convert("RGB"))

SCENES = {"wave": b_wave, "translate": b_translate, "counter": b_counter, "phone": b_phone, "form": b_form}
