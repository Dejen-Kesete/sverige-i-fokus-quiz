# Generates the motion-graphics layer (ASS / libass) for the Admas Studio promo.
# Times below are in SOURCE seconds; OFF shifts everything after the branded intro.
import sys

LANG = sys.argv[1] if len(sys.argv) > 1 else "en"
OFF = 3.5            # length of the branded intro prepended before the source video
TOTAL = 103.0 + OFF
END0 = 82.76         # source time where the custom end card takes over

GOLD, GOLD_L, WHITE, NAVY, MUTED = "&H6CB4D9&", "&HA7DCF1&", "&HFFFFFF&", "&H26140B&", "&HD6CCC2&"
PLAY, PLAYB, ML, MM, MB, MX, ETH = "AS Playfair", "AS Playfair Bold", "AS Mont Light", "AS Mont Medium", "AS Mont Bold", "AS Mont XBold", "AS Ethiopic"

T = {
 "en": dict(
  intro_kicker="LANGUAGE SERVICES  ·  MEDIA PRODUCTION",
  intro_tag="Clear communication with Tigrinya-speaking audiences",
  lt_sub="Language services & media production",
  web="Visit us online",
  vo_k="01  ·  SERVICE", vo_t1="Voice-over", vo_t2="in Tigrinya",
  vo_list=["Documentaries", "Commercials", "E-services", "Educational materials", "Informational videos"],
  tr_k="02  ·  SERVICE", tr_t1="Translation", tr_t2="into Tigrinya",
  tr_from1="Swedish", tr_from2="English", tr_note="Written translation of information\\Nand materials — accurate and clear.",
  ct_k="03  ·  CITIZENSHIP TEST", ct_t1="Prepare with", ct_t2="confidence", ct_book="Based on the official book",
  ct_list=[("200+ practice questions", "based on Sverige i fokus"),
           ("Answers & clear explanations", "understand it — don't just memorize"),
           ("The whole book in easy Swedish", "easier to read and understand"),
           ("The whole book in Tigrinya", "read in your native language"),
           ("Key words in Tigrinya", "from every chapter, simply explained"),
           ("Unlimited access", "practice whenever you want")],
  pr_k="ONE-TIME PAYMENT", pr_price="299 SEK", pr_sub="Instant access to the full practice package",
  kw_k="KEY WORDS", kw_t="Every chapter's key words — in Tigrinya",
  dc_k="04  ·  DOCUMENTS & APPLICATIONS", dc_t1="Official paperwork,", dc_t2="made clear",
  dc_list=["Citizenship application", "Family reunification", "Residence permit extension", "CV & cover letter", "Other official documents"],
  dc_note="Clear, complete and ready before you submit.",
  end_tag="Clear communication with Tigrinya-speaking audiences",
  end_services="VOICE-OVER   ·   TRANSLATION   ·   CITIZENSHIP TEST   ·   DOCUMENTS",
  cta_k="START TODAY", cta_pill="Create your account  ·  299 SEK",
 ),
 "sv": dict(
  intro_kicker="SPRÅKTJÄNSTER  ·  MEDIAPRODUKTION",
  intro_tag="Tydlig kommunikation med tigrinjatalande målgrupper",
  lt_sub="Språktjänster & mediaproduktion",
  web="Besök oss online",
  vo_k="01  ·  TJÄNST", vo_t1="Voice-over", vo_t2="på tigrinja",
  vo_list=["Dokumentärer", "Reklamfilmer", "E-tjänster", "Utbildningsmaterial", "Informationsfilmer"],
  tr_k="02  ·  TJÄNST", tr_t1="Översättning", tr_t2="till tigrinja",
  tr_from1="Svenska", tr_from2="Engelska", tr_note="Skriftlig översättning av information\\Noch material — korrekt och tydligt.",
  ct_k="03  ·  MEDBORGARSKAPSPROVET", ct_t1="Förbered dig", ct_t2="med trygghet", ct_book="Baserat på den officiella boken",
  ct_list=[("200+ övningsfrågor", "baserade på Sverige i fokus"),
           ("Rätt svar & tydliga förklaringar", "förstå — inte bara memorera"),
           ("Hela boken på lätt svenska", "enklare att läsa och förstå"),
           ("Hela boken på tigrinja", "läs på ditt modersmål"),
           ("Nyckelord på tigrinja", "från varje kapitel, enkelt förklarade"),
           ("Obegränsad tillgång", "öva när du vill, i din egen takt")],
  pr_k="ENGÅNGSBETALNING", pr_price="299 kr", pr_sub="Direkt tillgång till hela övningspaketet",
  kw_k="NYCKELORD", kw_t="Varje kapitels nyckelord — på tigrinja",
  dc_k="04  ·  MYNDIGHETSÄRENDEN", dc_t1="Dokument & ansökningar,", dc_t2="gjort tydligt",
  dc_list=["Ansökan om medborgarskap", "Familjeåterförening", "Förlängning av uppehållstillstånd", "CV & personligt brev", "Andra viktiga myndighetsdokument"],
  dc_note="Tydligt och komplett — innan du skickar in.",
  end_tag="Tydlig kommunikation med tigrinjatalande målgrupper",
  end_services="VOICE-OVER   ·   ÖVERSÄTTNING   ·   MEDBORGARSKAPSPROV   ·   DOKUMENT",
  cta_k="BÖRJA I DAG", cta_pill="Skapa ditt konto  ·  299 kr",
 ),
}[LANG]

ev = []
def ts(s):
    s = max(s, 0); h = int(s // 3600); m = int(s % 3600 // 60); sec = s % 60
    return f"{h}:{m:02d}:{sec:05.2f}"

def add(start, end, text, layer=5, src=True):
    o = OFF if src else 0
    ev.append(f"Dialogue: {layer},{ts(start + o)},{ts(end + o)},Base,,0,0,0,,{text}")

def txt(start, end, x, y, s, font, size, color=WHITE, an=7, sp=0, fin=550, fout=350, dx=0, dy=22, blur=5,
        alpha="&H00&", layer=6, extra="", src=True):
    # blur-in "focus pull" + gentle rise/slide + fade
    mv = f"\\move({x+dx},{y+dy},{x},{y},0,{int(fin*1.3)})" if (dx or dy) else f"\\pos({x},{y})"
    tag = (f"{{\\an{an}{mv}\\fn{font}\\fs{size}\\fsp{sp}\\c{color}\\1a{alpha}\\bord0\\shad0"
           f"\\blur{blur}\\t(0,{fin},0.6,\\blur0.6)\\fad({fin},{fout}){extra}}}")
    add(start, end, tag + s, layer, src)

def rect(start, end, x, y, w, h, color=NAVY, alpha="&H40&", blur=0, an=7, fin=400, fout=300, layer=2, extra="", src=True):
    add(start, end, f"{{\\an{an}\\pos({x},{y})\\p1\\bord0\\shad0\\c{color}\\1a{alpha}\\blur{blur}\\fad({fin},{fout}){extra}}}"
        f"m 0 0 l {w} 0 l {w} {h} l 0 {h}{{\\p0}}", layer, src)

def line(start, end, x, y, w, h=2, color=GOLD, delay=0, dur=700, an=7, fout=300, layer=4, src=True):
    # grows from its anchor
    add(start, end, f"{{\\an{an}\\pos({x},{y})\\p1\\bord0\\shad0\\c{color}\\fscx0\\t({delay},{delay+dur},0.35,\\fscx100)"
        f"\\fad(0,{fout})}}m 0 0 l {w} 0 l {w} {h} l 0 {h}{{\\p0}}", layer, src)

def check(start, end, x, y, delay=0, src=True):
    add(start, end, f"{{\\an7\\pos({x},{y})\\p1\\bord0\\shad0\\c{GOLD}\\fscx40\\fscy40\\alpha&HFF&"
        f"\\t({delay},{delay+120},\\alpha&H00&)\\t({delay},{delay+380},0.5,\\fscx100\\fscy100)\\fad(0,300)}}"
        f"m 0 12 l 5 7 l 10 13 l 23 0 l 28 5 l 10 23{{\\p0}}", 7, src)

def scrim(start, end, x, y, w, h, alpha="&H38&", blur=60):
    rect(start, end, x, y, w, h, NAVY, alpha, blur, fin=500, fout=400, layer=1)

# ---------------------------------------------------------------- letterbox 2:1 (opens like a curtain)
BAR = 60
add(-OFF, TOTAL, f"{{\\an7\\pos(0,0)\\p1\\bord0\\shad0\\c&H000000&\\fscy900\\t(300,1500,0.4,\\fscy100)}}m 0 0 l 1920 0 l 1920 {BAR} l 0 {BAR}{{\\p0}}", 20)
add(-OFF, TOTAL, f"{{\\an1\\pos(0,1080)\\p1\\bord0\\shad0\\c&H000000&\\fscy900\\t(300,1500,0.4,\\fscy100)}}m 0 0 l 1920 0 l 1920 {BAR} l 0 {BAR}{{\\p0}}", 20)

# ---------------------------------------------------------------- branded intro (before source)
I0 = -OFF
txt(I0 + 0.9, -0.15, 960, 420, T["intro_kicker"], MM, 22, GOLD, an=5, sp=7, fin=700, fout=450, dy=12)
txt(I0 + 1.2, -0.15, 960, 520, "ADMAS STUDIO", PLAY, 118, GOLD_L, an=5, sp=18, fin=1000, fout=450, dy=0, blur=14,
    extra="\\fscx108\\t(0,3200,0.5,\\fscx100)")
line(I0 + 1.6, -0.15, 960, 600, 420, 2, GOLD, 0, 900, an=8, fout=450)
txt(I0 + 1.9, -0.15, 960, 650, T["intro_tag"], ML, 32, WHITE, an=5, sp=1, fin=700, fout=450, dy=14)
txt(I0 + 2.2, -0.15, 960, 715, "ትግርኛ", ETH, 30, GOLD, an=5, fin=700, fout=450, dy=10)

# ---------------------------------------------------------------- host lower-third (0.6–4.5)
scrim(0.5, 4.55, 30, 790, 640, 220, "&H50&", 40)
line(0.6, 4.5, 90, 842, 5, 96, GOLD, 0, 1, fout=300)
txt(0.75, 4.5, 118, 836, "ADMAS STUDIO", MX, 40, WHITE, sp=6, dx=-26, dy=0)
txt(0.95, 4.5, 120, 890, T["lt_sub"], ML, 25, GOLD_L, sp=1, dx=-26, dy=0)

# ---------------------------------------------------------------- laptop / website (4.8–10.68)
rect(7.3, 10.55, 960, 948, 500, 112, NAVY, "&H18&", 1.5, an=5, fin=450, layer=3,
     extra="\\fscx60\\t(0,500,0.5,\\fscx100)")
line(7.45, 10.55, 960, 892, 500, 2, GOLD, 0, 600, an=8)
txt(7.55, 10.55, 960, 922, T["web"].upper(), MM, 19, GOLD, an=5, sp=6, dy=8)
txt(7.7, 10.55, 960, 966, "www.admasstudio.se", MB, 34, WHITE, an=5, sp=2, dy=0)

# ---------------------------------------------------------------- 01 voice-over (headphones 20.3–30.2)
a, b = 20.35, 30.15
scrim(a, b, 1270, 40, 760, 1000, "&H48&", 70)
x = 1360
txt(a + 0.1, b, x, 250, T["vo_k"], MM, 21, GOLD, sp=6, dx=30, dy=0)
line(a + 0.2, b, x, 292, 64, 2)
txt(a + 0.35, b, x, 318, T["vo_t1"], PLAYB, 84, WHITE, dx=40, dy=0)
txt(a + 0.55, b, x, 418, T["vo_t2"], PLAY, 58, GOLD_L, dx=40, dy=0, extra="\\i1")
txt(a + 0.8, b, x + 2, 508, "ትግርኛ", ETH, 28, GOLD, dx=30, dy=0)
for i, it in enumerate(T["vo_list"]):
    t0 = a + 1.4 + i * 0.45; y = 590 + i * 62
    line(t0, b, x, y + 17, 22, 2, GOLD, 0, 350)
    txt(t0 + 0.05, b, x + 40, y, it, MM, 31, WHITE, dx=24, dy=0, fin=450)

# ---------------------------------------------------------------- 02 translation (books 36.44–43.0)
a, b = 36.55, 42.95
scrim(a, b, -140, 40, 1020, 1000, "&H22&", 80)
x = 110
txt(a + 0.05, b, x, 230, T["tr_k"], MM, 21, GOLD, sp=6, dx=-30, dy=0)
line(a + 0.15, b, x, 272, 64, 2)
txt(a + 0.3, b, x, 298, T["tr_t1"], PLAYB, 84, WHITE, dx=-40, dy=0)
txt(a + 0.5, b, x, 398, T["tr_t2"], PLAY, 58, GOLD_L, dx=-40, dy=0, extra="\\i1")
for i, src_lang in enumerate([T["tr_from1"], T["tr_from2"]]):
    t0 = a + 1.1 + i * 0.5; y = 528 + i * 78
    rect(t0, b, x, y, 560, 60, "&H3A2A1A&", "&H10&", 0.8, fin=400, layer=3, extra="\\fscx0\\t(0,450,0.5,\\fscx100)")
    txt(t0 + 0.15, b, x + 26, y + 13, src_lang, MB, 28, WHITE, fin=400, dy=0, dx=-12)
    line(t0 + 0.35, b, x + 250, y + 30, 150, 2, GOLD, 0, 450)
    add(t0 + 0.75, b, f"{{\\an4\\pos({x+400},{y+31})\\p1\\bord0\\shad0\\c{GOLD}\\fad(200,300)}}m 0 -9 l 14 0 l 0 9{{\\p0}}", 6)
    txt(t0 + 0.8, b, x + 432, y + 10, "ትግርኛ", ETH, 30, GOLD_L, fin=400, dx=-10, dy=0)
txt(a + 2.3, b, x, 710, T["tr_note"], ML, 28, "&HE8E2DC&", fin=600, dy=12)

# ---------------------------------------------------------------- 03 citizenship test (book 52.64–62.64)
a, b = 52.8, 62.55
scrim(a, b, -160, 40, 900, 1000, "&H60&", 70)
scrim(a + 0.3, b, 1160, 40, 900, 1000, "&H58&", 70)
x = 110
txt(a + 0.1, b, x, 300, T["ct_k"], MM, 21, GOLD, sp=6, dx=-30, dy=0)
line(a + 0.2, b, x, 342, 64, 2)
txt(a + 0.35, b, x, 368, T["ct_t1"], PLAYB, 76, WHITE, dx=-40, dy=0)
txt(a + 0.55, b, x, 460, T["ct_t2"], PLAY, 64, GOLD_L, dx=-40, dy=0, extra="\\i1")
txt(a + 1.1, b, x, 590, T["ct_book"].upper(), MM, 18, MUTED, sp=4, dy=10)
txt(a + 1.3, b, x, 622, "Sverige i fokus", PLAY, 44, WHITE, dy=10, extra="\\i1")
x = 1230
for i, (m, s) in enumerate(T["ct_list"]):
    t0 = a + 1.0 + i * 0.95; y = 215 + i * 112
    check(t0, b, x, y + 8)
    txt(t0 + 0.08, b, x + 50, y, m, MB, 31, WHITE, dx=22, dy=0, fin=450)
    txt(t0 + 0.2, b, x + 51, y + 44, s, ML, 23, GOLD_L, dx=22, dy=0, fin=450)

# ---------------------------------------------------------------- price (website 62.96–70.8)
a, b = 64.0, 70.7
scrim(a, b, 1180, 540, 900, 520, "&H30&", 60)
x = 1830
txt(a + 0.1, b, x, 700, T["pr_k"], MM, 21, GOLD, an=9, sp=6, dx=30, dy=0)
txt(a + 0.3, b, x, 735, T["pr_price"], PLAYB, 128, GOLD_L, an=9, dx=0, dy=24, blur=12,
    extra="\\fscx112\\fscy112\\t(0,700,0.5,\\fscx100\\fscy100)")
line(a + 0.6, b, x, 895, 360, 2, GOLD, 0, 700, an=9)
txt(a + 0.8, b, x, 915, T["pr_sub"], ML, 26, WHITE, an=9, dy=10)

# ---------------------------------------------------------------- key words (tablet 70.88–75.24)
a, b = 71.3, 75.15
scrim(a, b, -100, 780, 1100, 300, "&H30&", 50)
line(a, b, 90, 850, 5, 104, GOLD, 0, 1)
txt(a + 0.1, b, 118, 846, T["kw_k"] + "  ·  ትግርኛ", MM, 22, GOLD, sp=6, dx=-24, dy=0)
txt(a + 0.3, b, 118, 884, T["kw_t"], PLAY, 44, WHITE, dx=-24, dy=0)

# ---------------------------------------------------------------- 04 documents (paper 76.2–82.76)
a, b = 76.35, 82.66
scrim(a, b, -150, 40, 1060, 1000, "&H1C&", 80)
x = 110
txt(a + 0.05, b, x, 205, T["dc_k"], MM, 21, GOLD, sp=6, dx=-30, dy=0)
line(a + 0.15, b, x, 247, 64, 2)
txt(a + 0.3, b, x, 273, T["dc_t1"], PLAYB, 68, WHITE, dx=-40, dy=0)
txt(a + 0.5, b, x, 358, T["dc_t2"], PLAY, 58, GOLD_L, dx=-40, dy=0, extra="\\i1")
for i, it in enumerate(T["dc_list"]):
    t0 = a + 1.0 + i * 0.4; y = 480 + i * 66
    check(t0, b, x, y + 4)
    txt(t0 + 0.06, b, x + 50, y, it, MM, 31, WHITE, dx=22, dy=0, fin=420)
line(a + 3.2, b, x, 830, 380, 1, GOLD, 0, 600)
txt(a + 3.4, b, x, 850, T["dc_note"], ML, 27, GOLD_L, dy=10, extra="\\i1")

# ---------------------------------------------------------------- end card (82.76–103)
e = END0
A1 = e + 10.2  # phase A → phase B
txt(e + 1.0, A1, 960, 505, "Admas Studio", PLAY, 112, GOLD_L, an=5, sp=4, fin=1000, fout=500, dy=0, blur=14,
    extra="\\fscx106\\t(0,4000,0.5,\\fscx100)")
line(e + 1.5, A1, 960, 580, 360, 2, GOLD, 0, 900, an=8, fout=500)
txt(e + 1.8, A1, 960, 630, T["end_tag"], ML, 34, WHITE, an=5, sp=1, fin=700, fout=500, dy=14)
for i, s in enumerate(T["end_services"].split("   ·   ")):
    pass
txt(e + 2.6, A1, 960, 760, T["end_services"], MM, 22, GOLD, an=5, sp=4, fin=900, fout=500, dy=12)
# phase B: call to action
B = A1 + 0.35
txt(B, 103.0, 960, 480, T["cta_k"], MM, 22, GOLD, an=5, sp=8, fin=600, fout=0, dy=12)
txt(B + 0.2, 103.0, 960, 565, "admasstudio.se", PLAYB, 104, WHITE, an=5, sp=2, fin=900, fout=0, dy=0, blur=14,
    extra="\\fscx106\\t(0,3000,0.5,\\fscx100)")
line(B + 0.6, 103.0, 960, 640, 520, 2, GOLD, 0, 900, an=8, fout=0)
txt(B + 0.9, 103.0, 960, 694, "info@admasstudio.se       +46 70 644 47 62", MM, 32, GOLD_L, an=5, sp=1, fin=700, fout=0, dy=12)
rect(B + 1.5, 103.0, 960, 800, 620, 76, GOLD, "&H00&", 1.2, an=5, fin=500, fout=0, layer=4,
     extra="\\fscx30\\t(0,600,0.5,\\fscx100)")
txt(B + 1.75, 103.0, 960, 801, T["cta_pill"], MB, 30, NAVY, an=5, sp=2, fin=500, fout=0, dy=0, blur=3)

hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Base,{MM},40,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
open(f"gfx_{LANG}.ass", "w").write(hdr + "\n".join(ev) + "\n")
print("events", len(ev))
