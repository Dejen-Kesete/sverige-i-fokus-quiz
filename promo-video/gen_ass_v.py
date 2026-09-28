# Motion-graphics layer (ASS / libass) for the vertical 1080x1920 TikTok cut.
# Times are source seconds (the vertical cut has no intro, so source == output time).
# Text stays inside TikTok's safe zone: y 250..1450, clear of the right-hand button column.
import sys
from PIL import ImageFont

LANG = sys.argv[1] if len(sys.argv) > 1 else "en"
END0, TOTAL = 82.76, 103.0
GOLD, GOLD_L, WHITE, NAVY, MUTED = "&H6CB4D9&", "&HA7DCF1&", "&HFFFFFF&", "&H26140B&", "&HD6CCC2&"
PLAY, PLAYB, ML, MM, MB, MX, ETH = "AS Playfair", "AS Playfair Bold", "AS Mont Light", "AS Mont Medium", "AS Mont Bold", "AS Mont XBold", "AS Ethiopic"
FONTFILE = {MM: "sf/ASMontMedium.ttf"}

T = {
 "en": dict(
  hook_k="ADMAS STUDIO", hook_1="Clear communication", hook_2="in Tigrinya",
  web="VISIT US ONLINE",
  vo_k="01  ·  SERVICE", vo_t1="Voice-over", vo_t2="in Tigrinya",
  vo_list=[["Documentaries", "Commercials", "E-services"], ["Educational materials", "Informational videos"]],
  tr_k="02  ·  SERVICE", tr_t1="Translation", tr_t2="into Tigrinya", tr_from=["Swedish", "English"],
  ct_k="03  ·  CITIZENSHIP TEST", ct_t1="Prepare with", ct_t2="confidence",
  ct_list=[("200+ practice questions", "based on Sverige i fokus"),
           ("Answers & clear explanations", "understand it — don't just memorize"),
           ("The whole book in easy Swedish", "easier to read and understand"),
           ("The whole book in Tigrinya", "read in your native language"),
           ("Key words in Tigrinya", "from every chapter, simply explained"),
           ("Unlimited access", "practice whenever you want")],
  pr_k="ONE-TIME PAYMENT", pr_price="299 SEK", pr_sub="Instant access to the full package",
  kw_k="KEY WORDS  ·  ", kw_1="Every chapter's key words", kw_2="— in Tigrinya",
  dc_k="04  ·  DOCUMENTS & APPLICATIONS", dc_t1="Official paperwork,", dc_t2="made clear",
  dc_note="Clear, complete and ready before you submit.",
  end_tag=["Clear communication with", "Tigrinya-speaking audiences"],
  end_services=["VOICE-OVER", "TRANSLATION", "CITIZENSHIP TEST", "DOCUMENTS"],
  cta_k="START TODAY", cta_pill="Create your account · 299 SEK",
 ),
 "sv": dict(
  hook_k="ADMAS STUDIO", hook_1="Tydlig kommunikation", hook_2="på tigrinja",
  web="BESÖK OSS ONLINE",
  vo_k="01  ·  TJÄNST", vo_t1="Voice-over", vo_t2="på tigrinja",
  vo_list=[["Dokumentärer", "Reklamfilmer", "E-tjänster"], ["Utbildningsmaterial", "Informationsfilmer"]],
  tr_k="02  ·  TJÄNST", tr_t1="Översättning", tr_t2="till tigrinja", tr_from=["Svenska", "Engelska"],
  ct_k="03  ·  MEDBORGARSKAPSPROVET", ct_t1="Förbered dig", ct_t2="med trygghet",
  ct_list=[("200+ övningsfrågor", "baserade på Sverige i fokus"),
           ("Rätt svar & tydliga förklaringar", "förstå — inte bara memorera"),
           ("Hela boken på lätt svenska", "enklare att läsa och förstå"),
           ("Hela boken på tigrinja", "läs på ditt modersmål"),
           ("Nyckelord på tigrinja", "från varje kapitel, enkelt förklarade"),
           ("Obegränsad tillgång", "öva när du vill, i din egen takt")],
  pr_k="ENGÅNGSBETALNING", pr_price="299 kr", pr_sub="Direkt tillgång till hela paketet",
  kw_k="NYCKELORD  ·  ", kw_1="Varje kapitels nyckelord", kw_2="— på tigrinja",
  dc_k="04  ·  MYNDIGHETSÄRENDEN", dc_t1="Dokument & ansökningar,", dc_t2="gjort tydligt",
  dc_note="Tydligt och komplett — innan du skickar in.",
  end_tag=["Tydlig kommunikation med", "tigrinjatalande målgrupper"],
  end_services=["VOICE-OVER", "ÖVERSÄTTNING", "MEDBORGARSKAPSPROV", "DOKUMENT"],
  cta_k="BÖRJA I DAG", cta_pill="Skapa ditt konto · 299 kr",
 ),
}[LANG]

ev = []
def ts(s):
    s = max(s, 0); h = int(s // 3600); m = int(s % 3600 // 60); sec = s % 60
    return f"{h}:{m:02d}:{sec:05.2f}"
def add(start, end, text, layer=5):
    ev.append(f"Dialogue: {layer},{ts(start)},{ts(end)},Base,,0,0,0,,{text}")
def txt(start, end, x, y, s, font, size, color=WHITE, an=5, sp=0, fin=500, fout=300, dx=0, dy=24, blur=5, layer=6, extra=""):
    mv = f"\\move({x+dx},{y+dy},{x},{y},0,{int(fin*1.3)})" if (dx or dy) else f"\\pos({x},{y})"
    add(start, end, f"{{\\an{an}{mv}\\fn{font}\\fs{size}\\fsp{sp}\\c{color}\\bord0\\shad0\\blur{blur}"
                    f"\\t(0,{fin},0.6,\\blur0.6)\\fad({fin},{fout}){extra}}}" + s, layer)
def rect(start, end, x, y, w, h, color=NAVY, alpha="&H40&", blur=0, an=7, fin=400, fout=300, layer=2, extra="", r=0):
    if r:  # rounded rectangle via bezier corners
        k = r * 0.45
        path = (f"m {r} 0 l {w-r} 0 b {w-k} 0 {w} {k} {w} {r} l {w} {h-r} b {w} {h-k} {w-k} {h} {w-r} {h} "
                f"l {r} {h} b {k} {h} 0 {h-k} 0 {h-r} l 0 {r} b 0 {k} {k} 0 {r} 0")
    else:
        path = f"m 0 0 l {w} 0 l {w} {h} l 0 {h}"
    add(start, end, f"{{\\an{an}\\pos({x},{y})\\p1\\bord0\\shad0\\c{color}\\1a{alpha}\\blur{blur}\\fad({fin},{fout}){extra}}}{path}{{\\p0}}", layer)
def line(start, end, x, y, w, h=3, color=GOLD, delay=0, dur=600, an=8, fout=300, layer=4):
    add(start, end, f"{{\\an{an}\\pos({x},{y})\\p1\\bord0\\shad0\\c{color}\\fscx0\\t({delay},{delay+dur},0.35,\\fscx100)"
                    f"\\fad(0,{fout})}}m 0 0 l {w} 0 l {w} {h} l 0 {h}{{\\p0}}", layer)
def check(start, end, x, y, delay=0):
    add(start, end, f"{{\\an7\\pos({x},{y})\\p1\\bord0\\shad0\\c{GOLD}\\fscx45\\fscy45\\alpha&HFF&"
                    f"\\t({delay},{delay+120},\\alpha&H00&)\\t({delay},{delay+380},0.5,\\fscx130\\fscy130)\\fad(0,300)}}"
                    f"m 0 12 l 5 7 l 10 13 l 23 0 l 28 5 l 10 23{{\\p0}}", 7)
def scrim_bottom(start, end, top=1000, alpha="&H30&"):
    # dark gradient rising from the bottom so text reads over any footage
    rect(start, end, -100, top, 1280, 1100, NAVY, alpha, 90, fin=450, fout=350, layer=1)

_fnt = {}
def width(s, font, size):
    k = (font, size)
    if k not in _fnt: _fnt[k] = ImageFont.truetype(FONTFILE[font], size)
    return _fnt[k].getlength(s)

C = 540  # horizontal centre

# ---- hook over the opening talking head
scrim_bottom(0.15, 4.75, 1020, "&H28&")
txt(0.3, 4.7, C, 1135, T["hook_k"], MM, 30, GOLD, sp=10, dy=14)
line(0.45, 4.7, C, 1165, 120)
txt(0.55, 4.7, C, 1240, T["hook_1"], PLAYB, 84, WHITE, dy=30, blur=10)
txt(0.8, 4.7, C, 1335, T["hook_2"], PLAY, 76, GOLD_L, dy=30, blur=10, extra="\\i1")
txt(1.1, 4.7, C, 1420, "ትግርኛ", ETH, 42, GOLD, dy=14)

# ---- website pill over the laptop
rect(7.3, 10.6, C, 1330, 720, 140, NAVY, "&H14&", 1.5, an=5, fin=400, layer=3, r=34, extra="\\fscx70\\t(0,450,0.5,\\fscx100)")
txt(7.45, 10.6, C, 1297, T["web"], MM, 24, GOLD, sp=7, dy=8)
txt(7.6, 10.6, C, 1352, "www.admasstudio.se", MB, 46, WHITE, sp=1, dy=0)

# ---- 01 voice-over (headphones)
a, b = 18.9, 24.96
scrim_bottom(a - 0.1, b, 960, "&H24&")
txt(a, b, C, 1060, T["vo_k"], MM, 28, GOLD, sp=8, dy=12)
line(a + 0.1, b, C, 1090, 90)
txt(a + 0.2, b, C, 1165, T["vo_t1"], PLAYB, 92, WHITE, dy=30, blur=10)
txt(a + 0.4, b, C, 1260, T["vo_t2"], PLAY, 70, GOLD_L, dy=30, blur=10, extra="\\i1")
k = 0
for ri, row in enumerate(T["vo_list"]):
    ws = [width(it, MM, 32) * 0.93 + 60 for it in row]; gap = 16
    x = C - (sum(ws) + gap * (len(ws) - 1)) / 2; y = 1345 + ri * 76
    for it, w in zip(row, ws):
        t0 = a + 1.0 + k * 0.3
        rect(t0, b, int(x), y, int(w), 64, NAVY, "&H20&", 0.8, fin=300, layer=3, r=32)
        rect(t0, b, int(x), y, int(w), 64, GOLD, "&HC0&", 0.8, fin=300, layer=3, r=32)
        txt(t0 + 0.05, b, int(x + w / 2), y + 32, it, MM, 32, WHITE, dy=0, fin=300, blur=2)
        x += w + gap; k += 1

# ---- 02 translation card over the book pages
a, b = 36.55, 42.98
rect(a, b, 60, 990, 960, 470, NAVY, "&H1C&", 2, fin=400, layer=2, r=36)
txt(a + 0.05, b, C, 1050, T["tr_k"], MM, 28, GOLD, sp=8, dy=12)
line(a + 0.15, b, C, 1080, 90)
txt(a + 0.25, b, C, 1150, T["tr_t1"], PLAYB, 88, WHITE, dy=26, blur=10)
txt(a + 0.45, b, C, 1240, T["tr_t2"], PLAY, 66, GOLD_L, dy=26, blur=10, extra="\\i1")
for i, lang_ in enumerate(T["tr_from"]):
    t0 = a + 1.0 + 0.45 * i; y = 1330 + i * 72
    txt(t0, b, 470, y, lang_, MB, 38, WHITE, an=6, dx=-20, dy=0, fin=350)
    line(t0 + 0.2, b, 500, y, 90, 3, GOLD, 0, 350, an=4)
    add(t0 + 0.5, b, f"{{\\an4\\pos(592,{y})\\p1\\bord0\\shad0\\c{GOLD}\\fad(150,300)}}m 0 -11 l 18 0 l 0 11{{\\p0}}", 6)
    txt(t0 + 0.55, b, 632, y, "ትግርኛ", ETH, 40, GOLD_L, an=4, dx=-12, dy=0, fin=350)

# ---- 03 citizenship test over the pedestal book
a = 52.8
scrim_bottom(a - 0.1, 56.25, 1040, "&H28&")
txt(a, 56.2, C, 1135, T["ct_k"], MM, 28, GOLD, sp=8, dy=12)
line(a + 0.1, 56.2, C, 1165, 90)
txt(a + 0.25, 56.2, C, 1245, T["ct_t1"], PLAYB, 88, WHITE, dy=28, blur=10)
txt(a + 0.45, 56.2, C, 1340, T["ct_t2"], PLAY, 78, GOLD_L, dy=28, blur=10, extra="\\i1")
a, b = 56.3, 62.58
rect(a, b, 40, 470, 1000, 990, NAVY, "&H22&", 3, fin=450, layer=2, r=40)
for i, (m, s) in enumerate(T["ct_list"]):
    t0 = a + 0.25 + i * 0.7; y = 530 + i * 150
    check(t0, b, 92, y + 8)
    txt(t0 + 0.06, b, 150, y, m, MB, 46, WHITE, an=7, dx=22, dy=0, fin=400)
    txt(t0 + 0.18, b, 151, y + 62, s, MM, 34, GOLD_L, an=7, dx=22, dy=0, fin=400)

# ---- price over the sign-up shot (top band, clear of the site's gold button lower down)
a, b = 67.6, 70.72
rect(a - 0.1, b, -100, -200, 1280, 1000, NAVY, "&H20&", 90, fin=450, fout=350, layer=1)
txt(a, b, C, 330, T["pr_k"], MM, 30, GOLD, sp=8, dy=12)
txt(a + 0.2, b, C, 470, T["pr_price"], PLAYB, 170, GOLD_L, dy=26, blur=14, extra="\\fscx112\\fscy112\\t(0,600,0.5,\\fscx100\\fscy100)")
line(a + 0.5, b, C, 575, 400)
txt(a + 0.7, b, C, 635, T["pr_sub"], MM, 36, WHITE, dy=10)

# ---- key words over the tablet (top band, above the picture)
a, b = 71.0, 75.18
txt(a, b, C, 270, T["kw_k"] + "ትግርኛ", MM, 26, GOLD, sp=6, dy=10)
line(a + 0.1, b, C, 298, 90)
txt(a + 0.2, b, C, 345, T["kw_1"], PLAYB, 54, WHITE, dy=16)

# ---- 04 documents over the paperwork, then the footer note over the host
a, b = 76.3, 78.76
scrim_bottom(a - 0.1, b, 1000, "&H1C&")
txt(a, b, C, 1110, T["dc_k"], MM, 26, GOLD, sp=6, dy=12)
line(a + 0.1, b, C, 1140, 90)
txt(a + 0.25, b, C, 1220, T["dc_t1"], PLAYB, 76, WHITE, dy=26, blur=10)
txt(a + 0.45, b, C, 1310, T["dc_t2"], PLAY, 72, GOLD_L, dy=26, blur=10, extra="\\i1")
scrim_bottom(81.1, END0 - 0.02, 1150, "&H30&")
line(81.2, END0 - 0.02, C, 1290, 300)
txt(81.3, END0 - 0.02, C, 1345, T["dc_note"], ML, 34, GOLD_L, dy=10, fout=150, extra="\\i1")

# ---- end card (logo is in the background at y 410..710)
e = END0; A1 = e + 10.2
txt(e + 1.0, A1, C, 860, "Admas Studio", PLAY, 118, GOLD_L, sp=3, fin=1000, fout=500, dy=0, blur=14, extra="\\fscx106\\t(0,4000,0.5,\\fscx100)")
line(e + 1.5, A1, C, 935, 360, 3, GOLD, 0, 900, fout=500)
for i, l in enumerate(T["end_tag"]):
    txt(e + 1.8 + 0.15 * i, A1, C, 1000 + i * 56, l, ML, 40, WHITE, fin=700, fout=500, dy=14)
for i, s in enumerate(T["end_services"]):
    txt(e + 2.6 + 0.25 * i, A1, C, 1180 + i * 62, s, MM, 30, GOLD, sp=8, fin=700, fout=500, dy=12)
B = A1 + 0.35
txt(B, TOTAL, C, 820, T["cta_k"], MM, 30, GOLD, sp=10, fin=600, fout=0, dy=12)
txt(B + 0.2, TOTAL, C, 915, "admasstudio.se", PLAYB, 100, WHITE, sp=1, fin=900, fout=0, dy=0, blur=14, extra="\\fscx106\\t(0,3000,0.5,\\fscx100)")
line(B + 0.6, TOTAL, C, 990, 560, 3, GOLD, 0, 900, fout=0)
txt(B + 0.9, TOTAL, C, 1060, "info@admasstudio.se", MM, 40, GOLD_L, fin=700, fout=0, dy=12)
txt(B + 1.05, TOTAL, C, 1120, "+46 70 644 47 62", MM, 40, GOLD_L, fin=700, fout=0, dy=12)
rect(B + 1.5, TOTAL, C, 1260, 800, 110, GOLD, "&H00&", 1.2, an=5, fin=500, fout=0, layer=4, r=55, extra="\\fscx30\\t(0,600,0.5,\\fscx100)")
txt(B + 1.75, TOTAL, C, 1261, T["cta_pill"], MB, 38, NAVY, sp=1, fin=500, fout=0, dy=0, blur=3)

hdr = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Base,AS Mont Medium,40,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
open(f"gfx_v_{LANG}.ass", "w").write(hdr + "\n".join(ev) + "\n")
print("events", len(ev))
