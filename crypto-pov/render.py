"""Monta el Ep.1 "You Wake Up in 2009 Knowing Everything About Bitcoin" (1920x1080, 30 fps).
python3 render.py info | still 3.2 40 ... | scenes [ids] | join"""
import json, math, os, subprocess, sys, difflib, re
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from guion import LINEAS, CLIPS, HUECO_SIN_AUDIO

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1920, 1080, 30
LAY = os.path.join(HERE, "layers"); AUD = os.path.join(HERE, "..", "descargas", "crypto_ep1"); TMP = os.path.join(HERE, "tmp")
os.makedirs(TMP, exist_ok=True)
FONTS = os.path.join(HERE, "..", "taller-pov", "fonts")
F_ANTON = os.path.join(FONTS, "Anton-Regular.ttf")
F_UI = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
F_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
YEL = (255, 201, 60); RED = (255, 77, 77); WHITE = (255, 255, 255); OL = (27, 21, 48); PANEL = (16, 14, 30)
ORG = (247, 147, 26); CYAN = (110, 214, 255); GRIS = (150, 160, 185); GREEN = (80, 220, 120)
PI_ = math.pi

# ---------------------------------------------------------------- audio y tiempos
def dur_audio(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout.strip())

def toks(s): return [re.sub(r"[^a-z0-9]", "", w.lower()) for w in s.split()]

def whisper(name):
    p = os.path.join(AUD, name[:-4] + ".json")
    return json.load(open(p)) if os.path.exists(p) else None

NARR = whisper("narr.mp3")

def narr_segments():
    """Para cada línea N/Y: (inicio, fin) en narr.mp3 y sus palabras de whisper."""
    ids = [l for l in LINEAS if l[0] not in CLIPS]
    if not NARR:  # estimación por longitud
        tot = dur_audio(os.path.join(AUD, "narr.mp3")); L = sum(len(t) for _, _, t in ids); t = 0; out = {}
        for lid, _, txt in ids:
            d = tot * len(txt) / L; out[lid] = (t, t + d, []); t += d
        return out
    A, owner = [], []
    for lid, _, txt in ids:
        for w in toks(txt): A.append(w); owner.append(lid)
    B = [re.sub(r"[^a-z0-9]", "", w["p"].lower()) for w in NARR]
    mapA = [None] * len(A)
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
        if op == "equal":
            for k in range(i2 - i1): mapA[i1 + k] = j1 + k
        elif op == "replace":
            for k in range(i2 - i1): mapA[i1 + k] = j1 + min(k * (j2 - j1) // max(1, i2 - i1), j2 - j1 - 1)
    # índice de whisper donde empieza cada línea = primera palabra mapeada
    first = {}
    for i, lid in enumerate(owner):
        if lid not in first and mapA[i] is not None: first[lid] = mapA[i]
    order = [l[0] for l in ids]; out = {}
    for k, lid in enumerate(order):
        j0 = first[lid]; j1 = first[order[k + 1]] if k + 1 < len(order) else len(NARR)
        ws = NARR[j0:j1]
        out[lid] = (ws[0]["inicio"], ws[-1]["fin"], ws)
    return out

SEG = narr_segments()

GAP = {"N02": .5, "N03": .2, "N04": .3, "N05": .35, "N06": .4, "V01": .25, "D01": .3, "N07": .55, "N09": .3, "N10": .45,
       "Y01": .45, "D02": .25, "N12": .9, "N13": .4, "N14": .3, "N15": .45, "N16": .8, "N17": .5, "N18": .6, "N19": .7, "N20": .4}

def fix_words(ws):
    out = []
    for w, a, b in ws:
        if out and out[-1][0] == "0" and w.startswith(".1"): out[-1] = ("0.1" + w[2:], out[-1][1], b); continue
        out.append(({"312": "3:12"}.get(w, w), a, b))
    return out

def timeline():
    """TL[lid] = (t0, t1, src0, archivo, palabras con tiempos absolutos)"""
    t, tl = 0.6, {}
    for lid, who, txt in LINEAS:
        t += GAP.get(lid, .25)
        if lid in CLIPS:
            p = os.path.join(AUD, CLIPS[lid])
            if os.path.exists(p):
                d = dur_audio(p); ww = whisper(CLIPS[lid]) or []
                words = [(w["p"], t + w["inicio"], t + w["fin"]) for w in ww]
                tl[lid] = (t, t + d, 0.0, CLIPS[lid], words)
            else:
                d = HUECO_SIN_AUDIO[lid]; tw = txt.split(); words = []
                for i, w in enumerate(tw): words.append((w, t + d * i / len(tw), t + d * (i + 1) / len(tw)))
                tl[lid] = (t, t + d, 0.0, None, words)
        else:
            s0, s1, ws = SEG[lid]; s0 = max(0, s0 - .06); s1 = s1 + .12
            d = s1 - s0
            words = fix_words([(w["p"], t + w["inicio"] - s0, t + w["fin"] - s0) for w in ws])
            tl[lid] = (t, t + d, s0, "narr.mp3", words)
        t += d
    return tl, t + 1.6

TL, TOTAL = timeline()
def S(l): return TL[l][0]
def E(l): return TL[l][1]

def WT(lid, palabra, n=1, fin=False):
    c = 0
    for w, a, b in TL[lid][4]:
        if re.sub(r"[^a-z0-9]", "", w.lower()) == palabra.lower():
            c += 1
            if c == n: return b if fin else a
    return S(lid)

# ---------------------------------------------------------------- utilidades
def ease(u): u = max(0., min(1., u)); return 1 - (1 - u) ** 3
def ease_io(u): u = max(0., min(1., u)); return u * u * (3 - 2 * u)
def back(u):
    u = max(0., min(1., u)); c = 1.7
    return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2
def clamp(u): return max(0., min(1., u))

@lru_cache(None)
def layer(name): return Image.open(os.path.join(LAY, name + ".png")).convert("RGBA")

@lru_cache(None)
def font(path, size): return ImageFont.truetype(path, max(1, int(size)))

@lru_cache(512)
def scaled(name, s):
    im = layer(name)
    return im.resize((max(1, int(im.width * s / 2)), max(1, int(im.height * s / 2))), Image.LANCZOS)

def put(canvas, name, cx, cy, s=1.0, alpha=1.0, rot=0):
    s = round(s, 3); im = scaled(name, s)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def bg(name, T, t0, zoom0=1.0, zoom1=1.06, dur=8, fx=0.5, fy=0.5):
    im = layer(name)
    z = zoom0 + (zoom1 - zoom0) * ease_io((T - t0) / dur)
    w, h = 2 * W / z, 2 * H / z
    x0 = (2 * W - w) * fx; y0 = (2 * H - h) * fy
    return im.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + w, y0 + h), reducing_gap=2.0).convert("RGBA")

def text(d, xy, s, size, fill=WHITE, anchor="mm", f=F_ANTON, stroke=0, sfill=OL):
    d.text(xy, s, font=font(f, size), fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sfill)

def panel(canvas, box, fill=PANEL, alpha=235, rad=28, outline=None, ow=0):
    ov = Image.new("RGBA", canvas.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    d.rounded_rectangle(box, rad, fill=fill + (alpha,), outline=outline, width=ow)
    canvas.alpha_composite(ov)

def popscale(T, t0, d=.35): return back((T - t0) / d) if T >= t0 else 0
def dark(c, a): c.alpha_composite(Image.new("RGBA", (W, H), (8, 6, 18, int(max(0, min(255, a))))))

def vignette(k=.75, s=1.6, top=.75):
    y, x = np.mgrid[0:H, 0:W]
    r = np.sqrt(((x - W / 2) / (W * k)) ** 2 + ((y - H / 2) / (H * k)) ** 2)
    a = np.clip((r - .55) * s, 0, top) * 255
    v = np.zeros((H, W, 4), np.uint8); v[..., 3] = a.astype(np.uint8)
    return Image.fromarray(v, "RGBA")
VIG = vignette()
VIG_HARD = vignette(.6, 2.4, .92)

@lru_cache(1)
def grains():
    r = np.random.default_rng(1); out = []
    for i in range(4):
        n = r.integers(0, 255, (H // 2, W // 2), dtype=np.uint8)
        a = np.zeros((H // 2, W // 2, 4), np.uint8); a[..., 0:3] = n[..., None]; a[..., 3] = 9
        out.append(Image.fromarray(a, "RGBA").resize((W, H), Image.NEAREST))
    return out

def stamp(canvas, T, t0, label, cx, cy, col=RED, rot=-10, size=120):
    if T < t0: return
    u = clamp((T - t0) / .18); k = 1.8 - .8 * ease(u)
    im = Image.new("RGBA", (1200, 320), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = font(F_ANTON, size); tw = d.textlength(label, font=f)
    d.rounded_rectangle((600 - tw / 2 - 34, 50, 600 + tw / 2 + 34, 270), 20, outline=col, width=14)
    d.text((600, 162), label, font=f, fill=col, anchor="mm")
    im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    im = im.resize((int(im.width * k), int(im.height * k)), Image.BILINEAR)
    if u < 1: im.putalpha(im.getchannel("A").point(lambda v: int(v * u)))
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def etiqueta(c, T, t0, s, cx, cy, fill=YEL, fg=OL, size=36):
    if T < t0: return
    u = popscale(T, t0); d = ImageDraw.Draw(c); f = font(F_UI, size); tw = d.textlength(s, font=f)
    d.rounded_rectangle((cx - (tw / 2 + 22) * u, cy - 34, cx + (tw / 2 + 22) * u, cy + 34), 14, fill=fill, outline=OL, width=4)
    if T - t0 > .2: d.text((cx, cy), s, font=f, fill=fg, anchor="mm")

def flecha_a(d, x0, y0, x1, y1, col=YEL, w=10):
    d.line((x0, y0, x1, y1), fill=col, width=w)
    a = math.atan2(y1 - y0, x1 - x0)
    d.polygon([(x1, y1), (x1 - 30 * math.cos(a - .45), y1 - 30 * math.sin(a - .45)), (x1 - 30 * math.cos(a + .45), y1 - 30 * math.sin(a + .45))], fill=col)

@lru_cache(8)
def _scan(w, h, a):
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for yy in range(0, h, 4): d.line((0, yy, w, yy), fill=(0, 0, 0, a))
    return ov
def scan(im, a=22): im.alpha_composite(_scan(im.width, im.height, a))

def money(v, dec=False): return f"${v:,.2f}" if dec else f"${v:,}"

# ---------------------------------------------------------------- subtítulos (palabra a palabra)
TAGS = {"D": "DAD", "Y": "YOU", "V": "TV NEWS"}

def chunks():
    out = []
    for lid, who, txt in LINEAS:
        words = TL[lid][4]; cur = []; groups = []
        for i, (w, a, b) in enumerate(words):
            cur.append(i)
            if sum(len(words[x][0]) + 1 for x in cur) >= 30 or w.endswith((".", ",", "?", "!", ":")) and len(cur) >= 2 or w.endswith("..."):
                groups.append(cur); cur = []
        if cur: groups.append(cur)
        for g in groups:
            out.append((words[g[0]][1], words[g[-1]][2], [(words[i][0].upper(), (words[i][1], words[i][2])) for i in g], who, lid))
    return out
CH = chunks()

def draw_caption(canvas, T):
    if T >= S("N19") - .05: return     # la tarjeta de voto lleva su propio texto
    for idx, (t0, t1, g, who, lid) in enumerate(CH):
        nxt0 = CH[idx + 1][0] if idx + 1 < len(CH) else 1e9
        if not (t0 - .04 <= T < t1 + .35) or T >= nxt0 - .04: continue
        d = ImageDraw.Draw(canvas)
        k = 0.88 + 0.12 * back((T - t0 + .04) / .14)
        size = 78 * k; f = font(F_ANTON, size)
        widths = [d.textlength(p + " ", font=f) for p, _ in g]
        total = sum(widths) - d.textlength(" ", font=f)
        if total > 1500:
            f = font(F_ANTON, size * 1500 / total); widths = [d.textlength(p + " ", font=f) for p, _ in g]; total = sum(widths) - d.textlength(" ", font=f)
        x = W / 2 - total / 2; y = 950
        starts = [ws for _, (ws, we) in g] + [1e9]
        for i_, ((p, (ws, we)), wd) in enumerate(zip(g, widths)):
            fin_ = min(starts[i_ + 1], we + .35) if i_ + 1 < len(g) else we + .35
            activa = ws - .03 <= T < fin_ - .03; dicha = T >= ws - .03
            col = YEL if activa else (WHITE if dicha else (225, 225, 230))
            if activa:
                u = clamp((T - ws + .03) / .12); fa = font(F_ANTON, f.size * (1 + .06 * math.sin(u * PI_)))
                d.text((x + (wd - d.textlength(" ", font=f)) / 2, y), p, font=fa, fill=col, anchor="mm", stroke_width=9, stroke_fill=(10, 10, 20))
            else:
                d.text((x, y), p, font=f, fill=col, anchor="lm", stroke_width=8, stroke_fill=(10, 10, 20))
            x += wd
        if who in TAGS:
            tag = TAGS[who]; ft = font(F_UI, 28); tw = d.textlength(tag, font=ft)
            d.rounded_rectangle((W / 2 - tw / 2 - 18, 846, W / 2 + tw / 2 + 18, 888), 12, fill=CYAN if who == "Y" else YEL)
            d.text((W / 2, 867), tag, font=ft, fill=OL, anchor="mm")
        return

# ---------------------------------------------------------------- barra superior de la serie
EPISODIO = 1

def btc_icon(d, cx, cy, r, on=True):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=ORG if on else (70, 78, 100), outline=(110, 60, 0) if on else (40, 44, 60), width=3)
    for dx in (-.18, .12): d.line((cx + dx * r, cy - r * .72, cx + dx * r, cy + r * .72), fill=WHITE, width=max(2, int(r * .12)))
    d.text((cx + 1, cy + 1), "B", font=font(F_UI, int(r * 1.2)), fill=WHITE, anchor="mm")

def coin_usd(d, cx, cy, r, on=True):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(90, 190, 110) if on else (70, 78, 100), outline=(30, 90, 40) if on else (40, 44, 60), width=3)
    d.text((cx, cy + 1), "$", font=font(F_UI, int(r * 1.2)), fill=WHITE, anchor="mm")

@lru_cache(1)
def barra_base():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x0, y0, x1, y1 = 40, 26, W - 40, 112
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 8, x1, y1 + 10), 24, fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).rounded_rectangle((x0, y0, x1, y1), 24, outline=ORG + (140,), width=6)
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0, y0, x1, y1), 24, fill=(12, 10, 26, 210), outline=ORG + (120,), width=2)
    d.rounded_rectangle((x0 + 14, y0 + 18, x0 + 112, y1 - 18), 12, fill=ORG)
    d.text((x0 + 63, (y0 + y1) / 2 + 1), f"EP.{EPISODIO}", font=font(F_ANTON, 32), fill=OL, anchor="mm")
    for xs in (560, 860, 1120, 1380): d.line((xs, y0 + 18, xs, y1 - 18), fill=(255, 255, 255, 40), width=2)
    d.text((1404, y0 + 26), "GOAL", font=font(F_UI, 18), fill=ORG, anchor="lm")
    return im

def draw_hud(canvas, T):
    if T < E("N01") + .3 or T >= S("N19") - .1: return
    canvas.alpha_composite(barra_base()); d = ImageDraw.Draw(canvas)
    def pop(t): return 1 + .28 * math.sin(clamp((T - t) / .3) * PI_) if 0 <= T - t < .3 else 1
    # fecha y hora
    t_fecha = WT("N04", "january")
    if T < S("N12"): fecha, hora, tf = ("JAN ?, ????" if T < t_fecha else "JAN 9, 2009"), "7:58 AM", t_fecha
    elif T < S("N16"): fecha, hora, tf = "JAN 9, 2009", "11:47 PM", S("N12")
    else: fecha, hora, tf = "JAN 10, 2009", "3:12 AM", S("N16")
    d.text((176, 69), fecha, font=font(F_ANTON, 40 * pop(tf)), fill=WHITE, anchor="lm")
    d.text((400, 70), hora, font=font(F_UI, 26), fill=GRIS, anchor="lm")
    # precio BTC
    t_p = WT("N09", "zero"); on = T >= t_p
    btc_icon(d, 600, 69, 20, on)
    d.text((632, 56), "BTC PRICE", font=font(F_UI, 16), fill=GRIS, anchor="lm")
    d.text((632, 84), "$0.00" if on else "?", font=font(F_ANTON, 30 * pop(t_p)), fill=WHITE if on else GRIS, anchor="lm")
    # tus BTC
    t_b = WT("N14", "50"); hb = T >= t_b
    btc_icon(d, 900, 69, 20, hb)
    d.text((932, 56), "YOUR BTC", font=font(F_UI, 16), fill=GRIS, anchor="lm")
    v = int(50 * ease((T - t_b) / .9)) if hb else 0
    d.text((932, 84), str(v), font=font(F_ANTON, 30 * pop(t_b)), fill=ORG if hb else WHITE, anchor="lm")
    # dinero
    t_c = WT("N10", "three"); hc = T >= t_c
    coin_usd(d, 1160, 69, 20, hc)
    d.text((1192, 56), "CASH", font=font(F_UI, 16), fill=GRIS, anchor="lm")
    d.text((1192, 84), money(int(340 * ease((T - t_c) / .8))) if hc else "?", font=font(F_ANTON, 30 * pop(t_c)), fill=WHITE if hc else GRIS, anchor="lm")
    # objetivo
    if T < WT("N09", "future"): goal, tg = "Figure out what's happening", S("N02")
    elif T < WT("N14", "50"): goal, tg = "Get Bitcoin before anyone else", WT("N09", "future")
    else: goal, tg = "Keep mining. Tell no one.", WT("N14", "50")
    d.text((1404, 84), goal, font=font(F_UI, 26 * pop(tg)), fill=WHITE, anchor="lm")

# ---------------------------------------------------------------- escenas
def sc_hook(T):
    c = Image.new("RGBA", (W, H), (10, 9, 22, 255)); d = ImageDraw.Draw(c)
    # túnel de anillos
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for i in range(14):
        ph = ((T * .55 + i / 14) % 1); r = 40 + ph ** 2 * 1400
        a = int(150 * math.sin(ph * PI_))
        od.ellipse((W / 2 - r * 1.6, H / 2 - r, W / 2 + r * 1.6, H / 2 + r), outline=ORG + (a,) if i % 2 else CYAN + (a // 2,), width=4)
    c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(2)))
    t26, t09 = WT("N01", "2026"), WT("N01", "2009")
    if T < t09:
        yr = "2026"; u = popscale(T, .05, .45)
    else:
        u2 = clamp((T - t09) / .7)
        yr = str(int(round(2026 - 17 * ease(u2)))); u = 1
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(gl)
    gd.text((W / 2, H / 2 - 40), yr, font=font(F_ANTON, 330 * max(u, .01)), fill=ORG + (255,), anchor="mm")
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(18))); c.alpha_composite(gl)
    d = ImageDraw.Draw(c)
    if T >= .05: d.text((W / 2, H / 2 - 40), yr, font=font(F_ANTON, 330 * max(u, .01)), fill=WHITE, anchor="mm")
    if .1 <= T < t09: etiqueta(c, T, .1, "YOU GO TO SLEEP", W / 2, 180, CYAN)
    if T >= t09: etiqueta(c, T, t09, "YOU WAKE UP", W / 2, 180, YEL)
    tb = WT("N01", "bitcoin")
    if T >= tb:
        u = popscale(T, tb, .5); put(c, "btc_coin", W / 2 + 470, H / 2 - 60, .9 * u, rot=8 * math.sin(T * 2))
        put(c, "btc_coin", W / 2 - 470, H / 2 - 60, .9 * u, rot=-8 * math.sin(T * 2))
    return c

def sc_alarma(T):
    s0 = S("N02")
    c = bg("bg_bedroom", T, s0, 1.9, 1.75, 3, .38, .78)
    ring = s0 - .3 <= T < WT("N02", "phone", fin=True) + .6
    sh = 8 * math.sin(T * 60) if ring else 0
    z = 1.9 - .15 * ease_io((T - s0) / 3); x0 = (W - W / z) * .38; y0 = (H - H / z) * .78
    ax, ay = (800 - x0) * z, (632 - y0) * z
    put(c, "alarma", ax + sh, ay, 150 * z / 300, rot=sh * .8)
    if ring:
        d = ImageDraw.Draw(c)
        for k in range(3):
            a = (T * 3 + k / 3) % 1
            r = 90 * z + a * 140
            d.arc((ax - r, ay - r, ax + r, ay + r), 200, 250, fill=(255, 255, 255, int(255 * (1 - a))), width=8)
            d.arc((ax - r, ay - r, ax + r, ay + r), 290, 340, fill=(255, 255, 255, int(255 * (1 - a))), width=8)
        stamp(c, T, s0 - .2, "RIIIING!", 1450, 300, YEL, 8, 110)
    etiqueta(c, T, WT("N02", "real"), "A REAL ALARM CLOCK", ax, ay - 190, YEL)
    return c

def sc_cuarto(T):
    s0, e0 = S("N03"), E("N03")
    u = ease_io((T - s0) / (e0 - s0 + .4))
    c = bg("bg_bedroom", T, s0, 1.22 - .17 * u, 1.22 - .17 * u, 1, .15 + .7 * u, .45)
    etiqueta(c, T, WT("N03", "posters"), "POSTERS", 760 - 520 * u + 330, 520, YEL)
    etiqueta(c, T, WT("N03", "monitor"), "CRT MONITOR · 17\"", 1180 - 300 * u + 200, 230, CYAN)
    etiqueta(c, T, WT("N03", "flip"), "FLIP PHONE", 1250, 720, YEL)
    if T >= WT("N03", "apartment"):
        stamp(c, T, WT("N03", "apartment", fin=True), "NOT YOUR ROOM", 520, 300, RED, -8, 90)
    return c

def sc_movil(T):
    s0 = S("N04")
    c = bg("bg_bedroom", T, s0, 1.3, 1.36, 4, .9, .6).filter(ImageFilter.GaussianBlur(10)); dark(c, 110)
    u = ease((T - s0 + .3) / .5)
    cy = 560 + 600 * (1 - u)
    put(c, "movil", W / 2, cy, 1.0, rot=-4)
    d = ImageDraw.Draw(c)
    # pantalla del móvil (en coords del lienzo: el móvil mide 420x920, pantalla en 96,80 228x300)
    sx, sy = W / 2 - 210 + 96, cy - 460 + 80
    d.text((sx + 114, sy + 40), "08:00", font=font(F_MONO, 34), fill=OL, anchor="mm")
    tj = WT("N04", "january")
    if T >= tj:
        d.text((sx + 114, sy + 140), "FRI", font=font(F_ANTON, 44 * popscale(T, tj)), fill=OL, anchor="mm")
        d.text((sx + 114, sy + 200), "09 JAN", font=font(F_ANTON, 50 * popscale(T, tj)), fill=OL, anchor="mm")
    t9 = WT("N04", "2009")
    if T >= t9:
        d.text((sx + 114, sy + 260), "2009", font=font(F_ANTON, 50 * popscale(T, t9)), fill=(200, 40, 40), anchor="mm")
        stamp(c, T, t9 + .1, "2009", 1450, 520, RED, -10, 170)
    return c

def sc_espejo(T):
    s0 = S("N05")
    c = bg("bg_espejo", T, s0, 1.0, 1.06, 4, .5, .5)
    z = 1.0 + .06 * ease_io((T - s0) / 4)
    x0 = (W - W / z) * .5; y0 = (H - H / z) * .5
    mx0, my0, mx1, my1 = [(v - o) * z for v, o in ((620, x0), (180, y0), (1300, x0), (820, y0))]
    ref = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tr = WT("N05", "19")
    nm = "heroe_shock" if T >= WT("N05", "mirror") else "heroe_miedo"
    jump = 18 * math.sin(clamp((T - tr) / .3) * PI_) if T >= tr else 0
    put(ref, nm, (mx0 + mx1) / 2, my0 + 430 * z - jump, 1.15 * z)
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rounded_rectangle((mx0 + 4, my0 + 4, mx1 - 4, my1 - 4), int(24 * z), fill=255)
    tint = Image.new("RGBA", (W, H), (167, 196, 207, 60)); ref.alpha_composite(tint)
    c.paste(ref, (0, 0), Image.composite(ref.getchannel("A"), Image.new("L", (W, H), 0), m))
    d = ImageDraw.Draw(c)
    gl_ = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl_).polygon([(mx0 + 30, my0 + 30), (mx0 + 150, my0 + 30), (mx0 + 30, my0 + 170)], fill=(255, 255, 255, 80))
    c.alpha_composite(gl_)
    if T >= tr:
        stamp(c, T, tr, "AGE: 19", 1650, 480, YEL, -8, 120)
        etiqueta(c, T, tr + .25, "AGAIN.", 1650, 660, RED, WHITE, 40)
    return c

def tv_noticias(c, T, x, y, w, h, t0):
    """Pinta las noticias de 2009 en la pantalla de la tele (x,y,w,h en coords de pantalla)."""
    tv = Image.new("RGBA", (w, h), (24, 40, 90, 255)); d = ImageDraw.Draw(tv)
    d.rectangle((0, 0, w, h * .62), fill=(40, 60, 120))
    # gráfico cayendo
    pts = [(int(w * .08 + i * w * .84 / 9), int(h * .16 + (i ** 1.4) * h * .045 + 10 * math.sin(i * 1.7))) for i in range(10)]
    k = int(clamp((T - t0) / 1.4) * 9) + 1
    if k > 1: d.line(pts[:k], fill=(255, 80, 80), width=6)
    d.rectangle((0, h * .62, w, h * .80), fill=(200, 30, 40))
    d.text((18, h * .71), "BREAKING NEWS", font=font(F_ANTON, int(h * .1)), fill=WHITE, anchor="lm")
    d.rectangle((0, h * .80, w, h), fill=(245, 245, 245))
    tick = "  BANKS COLLAPSING · MILLIONS LOSE THEIR HOMES · DOW DOWN 34% IN 2008 · BAILOUTS ·  "
    f = font(F_UI, int(h * .085)); tw = d.textlength(tick, font=f); off = (T * 160) % tw
    for k2 in range(3): d.text((-off + k2 * tw, h * .9), tick, font=f, fill=(20, 20, 30), anchor="lm")
    # líneas de CRT
    scan(tv, 40)
    c.alpha_composite(tv, (int(x), int(y)))

def sc_salon_tv(T):
    s0 = S("N06")
    c = bg("bg_salon", T, s0, 1.0, 1.08, 8, .62, .4)
    z = 1.0 + .08 * ease_io((T - s0) / 8); x0 = (W - W / z) * .62; y0 = (H - H / z) * .4
    tx, ty = (1170 - x0) * z + 6, (236 - y0) * z + 6
    tv_noticias(c, T, tx, ty, int(508 * z), int(356 * z), S("V01"))
    td = S("D01") - .7
    if T >= td:
        u = ease((T - td) / .6)
        put(c, "papa_serio", 420 - 500 * (1 - u), 700, 1.12)
        put(c, "taza", 640 - 500 * (1 - u), 860, .72)
    if T >= S("V01") and TL["V01"][3] is None:
        etiqueta(c, T, S("V01") + .1, "TV: \"BANKS ARE COLLAPSING...\"", 1410, 760, YEL, OL, 30)
    return c

def sc_satoshi(T):
    s0 = S("N07")
    c = Image.new("RGBA", (W, H), (12, 10, 24, 255))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.ellipse((W / 2 - 700, H / 2 - 420, W / 2 + 700, H / 2 + 420), fill=ORG + (55,))
    c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(c)
    # código binario cayendo
    for i in range(26):
        x = 40 + i * 74; sp = 60 + (i * 37) % 90
        for j in range(12):
            y = (j * 92 + T * sp + i * 51) % (H + 100) - 50
            d.text((x, y), "01"[(i + j) % 2], font=font(F_MONO, 30), fill=(247, 147, 26, 50), anchor="mm")
    tn = WT("N07", "satoshi")
    if T >= tn:
        u = ease((T - tn) / .5); put(c, "nakamoto", 520, 640 + 80 * (1 - u), .9, alpha=u)
        etiqueta(c, T, tn + .2, "SATOSHI NAKAMOTO", 520, 230, ORG, WHITE, 40)
        etiqueta(c, T, tn + .5, "IDENTITY: UNKNOWN", 520, 990 - 120, (40, 40, 60), WHITE, 26) if False else None
    tdays = WT("N07", "six")
    if tdays <= T < tn: 
        u = popscale(T, tdays); text(d, (W / 2, 470), "6 DAYS AGO", 200 * u, ORG, stroke=10)
        text(d, (W / 2, 640), "JANUARY 3, 2009", 60 * u, WHITE, f=F_ANTON)
    if T >= WT("N07", "first"):
        u = popscale(T, WT("N07", "first"))
        panel(c, (980, 260, 980 + 780 * u, 610), (250, 246, 235), 250, 22, OL, 6)
        if u > .6:
            text(d, (1370, 325), "BLOCK #0", 64, OL)
            text(d, (1370, 395), "\"THE GENESIS BLOCK\"", 40, ORG)
            text(d, (1370, 470), "MINED: JAN 3, 2009", 34, (90, 80, 100), f=F_UI)
            text(d, (1370, 535), "REWARD: 50 BTC", 34, (90, 80, 100), f=F_UI)
    tk = WT("N08", "nobody")
    if T >= tk:
        stamp(c, T, tk, "ALMOST NOBODY KNOWS", 1370, 745, RED, -4, 76)
    return c

def sc_precio(T):
    s0 = S("N09")
    c = Image.new("RGBA", (W, H), (12, 10, 24, 255)); d = ImageDraw.Draw(c)
    scan(c, 40)
    tz = WT("N09", "zero")
    put(c, "btc_coin", 480, 470, 1.0 * popscale(T, s0 + .1, .5), rot=6 * math.sin(T * 2))
    text(d, (480, 160), "TODAY · 2009", 44, GRIS, f=F_UI)
    if T >= tz:
        u = popscale(T, tz); text(d, (480, 760), "$0.00", 150 * u, WHITE, stroke=8)
        text(d, (480, 860), "PER BITCOIN", 34, GRIS, f=F_UI)
    tf = WT("N09", "future")
    if T >= tf:
        u = ease((T - tf) / .6)
        flecha_a(d, 760, 470, 760 + 380 * u, 470, ORG, 14)
        text(d, (1440, 160), "YOUR FUTURE", 44, ORG, f=F_UI)
        th = WT("N09", "hundred")
        if T >= th:
            v = int(100000 * ease((T - th) / 1.0))
            text(d, (1440, 470), f"${v:,}+", 150 * popscale(T, th), ORG, stroke=8)
            text(d, (1440, 590), "PER BITCOIN", 34, GRIS, f=F_UI)
    return c

def pantalla_banco(c, T, x0, y0, w, h, t0):
    sc = Image.new("RGBA", (w, h), (236, 240, 246, 255)); d = ImageDraw.Draw(sc)
    d.rectangle((0, 0, w, 70), fill=(20, 60, 140)); d.text((24, 35), "FIRST HOMETOWN BANK · Online Banking", font=font(F_SANSB, 30), fill=WHITE, anchor="lm")
    d.rectangle((0, 70, w, 112), fill=(200, 210, 225)); d.text((24, 91), "Accounts   Transfers   Bill Pay   Log out", font=font(F_SANS, 24), fill=(30, 40, 70), anchor="lm")
    d.text((60, 190), "Student Checking  ****4417", font=font(F_SANSB, 34), fill=(30, 40, 70), anchor="lm")
    d.text((60, 260), "Available balance", font=font(F_SANS, 30), fill=(90, 100, 120), anchor="lm")
    tv = WT("N10", "three")
    if T >= tv:
        v = 340 * ease((T - tv) / .9)
        d.text((60, 360), f"${v:,.2f}", font=font(F_SANSB, int(110 * popscale(T, tv))), fill=(20, 120, 50), anchor="lm")
    rows = [("01/07/09", "GameStop", "-$59.99"), ("01/05/09", "Paycheck · Pizza Hut", "+$212.40"), ("01/02/09", "iTunes", "-$0.99")]
    for i, (a, b, cc) in enumerate(rows):
        yy = 470 + i * 56; d.line((60, yy - 26, w - 60, yy - 26), fill=(200, 205, 215), width=2)
        d.text((60, yy), a, font=font(F_SANS, 26), fill=(90, 100, 120), anchor="lm"); d.text((260, yy), b, font=font(F_SANS, 26), fill=(30, 40, 70), anchor="lm")
        d.text((w - 60, yy), cc, font=font(F_SANSB, 26), fill=(30, 40, 70), anchor="rm")
    scan(sc, 14)
    c.alpha_composite(sc, (int(x0), int(y0)))

def sc_banco(T):
    s0 = S("N10")
    c = Image.new("RGBA", (W, H), (30, 26, 40, 255))
    z = 1.0 + .06 * ease_io((T - s0) / 6)
    mon = scaled("monitor_grande", round(.9 * z, 3)); mx, my = (W - mon.width) // 2, 150 - int(40 * z)
    c.alpha_composite(mon, (mx, my))
    k = mon.width / 1580
    pantalla_banco(c, T, mx + 100 * k + 6, my + 80 * k + 6, int(1380 * k - 12), int(820 * k - 12), s0)
    te = WT("N10", "entire")
    if T >= te: stamp(c, T, te, "ENTIRE FORTUNE", 1450, 780, RED, -8, 90)
    return c

def sc_papa(T):
    s0 = S("Y01")
    c = bg("bg_salon", T, s0, 1.12, 1.18, 9, .35, .5)
    risa = T >= S("D02") - .05
    bounce = 10 * abs(math.sin(T * 14)) if risa else 0
    put(c, "papa_risa" if risa else "papa_serio", 1340, 690 - bounce, 1.2)
    put(c, "heroe_decidido", 330, 720, 1.25)
    # taza: se cae al reírse
    tr = S("D02") + .35
    if T >= tr + .25:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        sp = ease((T - tr - .25) / .5)
        od.ellipse((860 - 120 * sp, 728 - 8 * sp, 900 + 130 * sp, 742 + 8 * sp), fill=(90, 51, 32, 235), outline=OL, width=4)
        c.alpha_composite(ov)
    if T < tr: put(c, "taza", 880, 652, .7)
    else:
        u = clamp((T - tr) / .35)
        put(c, "taza", 880 + 40 * ease(u), 652 + 40 * ease(u), .7, rot=-85 * ease(u))
    if TL["D02"][3] is None and T >= S("D02"):
        u = popscale(T, S("D02")); d = ImageDraw.Draw(c)
        bx, by = 1340, 250
        d.rounded_rectangle((bx - 330 * u, by - 80 * u, bx + 330 * u, by + 80 * u), 40, fill=WHITE, outline=OL, width=6)
        if u > .6:
            d.polygon([(bx - 40, by + 76), (bx + 10, by + 76), (bx - 60, by + 150)], fill=WHITE, outline=OL)
            text(d, (bx, by), "SON... GO GET A JOB.", 58, OL)
    if risa: etiqueta(c, T, S("D02") + .1, "HA HA HA", 1700, 430, YEL, OL, 40)
    return c

def crt_noche(c, T, cx, cy, s, screen_fn=None):
    """CRT en la mesa de noche con resplandor."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.ellipse((cx - 600 * s, cy - 380 * s, cx + 600 * s, cy + 380 * s), fill=CYAN + (70,))
    c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(90)))
    put(c, "monitor_grande", cx, cy, s * .62)

def sc_noche(T):
    s0 = S("N12")
    c = bg("bg_noche", T, s0, 1.0, 1.1, 9, .5, .55)
    on = T >= WT("N12", "turn")
    shake = 4 * math.sin(T * 70) if T >= WT("N12", "fan") else 0
    if on:
        crt_noche(c, T, 960 + shake, 470, 1.0)
        mw, mh = 1580 * .62, 1060 * .62
        x0, y0 = 960 + shake - mw / 2 + 100 * .62 + 4, 470 - mh / 2 + 80 * .62 + 4
        boot = clamp((T - WT("N12", "turn")) / 1.4)
        scr = Image.new("RGBA", (int(1380 * .62) - 8, int(820 * .62) - 8), (0, 0, 0, 255)); sd = ImageDraw.Draw(scr)
        if boot < 1: sd.text((30, 30), "Starting Windows XP" + "." * int(T * 4 % 4), font=font(F_MONO, 30), fill=(200, 200, 200))
        else:
            sd.rectangle((0, 0, scr.width, scr.height), fill=(58, 110, 165)); sd.rectangle((0, scr.height - 26, scr.width, scr.height), fill=(36, 94, 220))
            sd.rounded_rectangle((0, scr.height - 26, 80, scr.height), 10, fill=(60, 160, 60)); sd.text((40, scr.height - 13), "start", font=font(F_SANSB, 16), fill=WHITE, anchor="mm")
            scan(scr, 30)
        c.alpha_composite(scr, (int(x0), int(y0)))
    else:
        put(c, "monitor_grande", 960, 470, .62); dark(c, 60)
    if T >= WT("N12", "fan"):
        d = ImageDraw.Draw(c)
        for k2 in range(4):
            a = (T * 2.5 + k2 / 4) % 1
            d.arc((1400 - 60 - a * 80, 640 - 60 - a * 80, 1400 + 60 + a * 80, 640 + 60 + a * 80), 220, 320, fill=(255, 255, 255, int(200 * (1 - a))), width=5)
        stamp(c, T, WT("N12", "jet"), "VRRRRRRR", 1560, 380, CYAN, 8, 80)
    ta = WT("N12", "asleep")
    if T >= ta and T < WT("N12", "turn"): etiqueta(c, T, ta, "EVERYONE'S ASLEEP", 960, 300, (40, 44, 70), WHITE, 34)
    return c

def ventana(sd, x, y, w, h, title):
    sd.rounded_rectangle((x, y, x + w, y + h), 10, fill=(236, 233, 216), outline=(0, 60, 180), width=3)
    sd.rounded_rectangle((x, y, x + w, y + 40), 10, fill=(0, 84, 227)); sd.rectangle((x, y + 24, x + w, y + 40), fill=(0, 84, 227))
    sd.text((x + 14, y + 20), title, font=font(F_SANSB, 20), fill=WHITE, anchor="lm")
    sd.rounded_rectangle((x + w - 36, y + 7, x + w - 8, y + 33), 5, fill=(224, 80, 50), outline=WHITE, width=2)
    sd.text((x + w - 22, y + 20), "x", font=font(F_SANSB, 18), fill=WHITE, anchor="mm")

def sc_pc(T):
    """Primer plano del monitor: correo de la lista, descarga, Bitcoin v0.1 y el mensaje."""
    s0 = S("N13")
    gl = T >= WT("N16", "flickers") and T < S("N16") + 99
    c = Image.new("RGBA", (W, H), (8, 10, 20, 255))
    z = 1.0 + .04 * ease_io((T - s0) / 20)
    mon = scaled("monitor_grande", round(.9 * z, 3)); mx, my = (W - mon.width) // 2, 150 - int(40 * z)
    c.alpha_composite(mon, (mx, my))
    k = mon.width / 1580; sw, sh = int(1380 * k - 12), int(820 * k - 12); sx, sy = int(mx + 100 * k + 6), int(my + 80 * k + 6)
    sc = Image.new("RGBA", (sw, sh), (58, 110, 165, 255)); d = ImageDraw.Draw(sc)
    d.rectangle((0, sh - 40, sw, sh), fill=(36, 94, 220)); d.rounded_rectangle((0, sh - 40, 120, sh), 14, fill=(60, 160, 60))
    d.text((60, sh - 20), "start", font=font(F_SANSB, 24), fill=WHITE, anchor="mm")
    reloj = "11:52 PM" if T < S("N16") else "3:12 AM"
    d.text((sw - 20, sh - 20), reloj, font=font(F_SANS, 22), fill=WHITE, anchor="rm")
    if T < S("N14"):
        ventana(d, 40, 30, sw - 80, sh - 110, "Inbox - cryptography@metzdowd.com - Mozilla Thunderbird")
        rows = [("Satoshi Nakamoto", "Bitcoin v0.1 released", "1/8/2009"), ("J. Smith", "Re: digital cash ideas", "1/7/2009"),
                ("Mailing list", "Weekly digest", "1/5/2009")]
        for i, (a, b, cc) in enumerate(rows):
            yy = 110 + i * 54; sel = i == 0 and T >= WT("N13", "bitcoin")
            if sel: d.rectangle((50, yy - 24, sw - 50, yy + 24), fill=(49, 106, 197))
            col = WHITE if sel else (20, 20, 30)
            d.text((70, yy), a, font=font(F_SANSB if i == 0 else F_SANS, 24), fill=col, anchor="lm")
            d.text((380, yy), b, font=font(F_SANSB if i == 0 else F_SANS, 24), fill=col, anchor="lm")
            d.text((sw - 70, yy), cc, font=font(F_SANS, 22), fill=col, anchor="rm")
        if T >= WT("N13", "bitcoin"):
            yb = 300; d.line((50, yb - 20, sw - 50, yb - 20), fill=(160, 160, 160), width=2)
            d.text((70, yb + 10), "From: Satoshi Nakamoto", font=font(F_SANSB, 24), fill=(20, 20, 30), anchor="lm")
            d.text((70, yb + 50), "Subject: Bitcoin v0.1 released", font=font(F_SANSB, 24), fill=(20, 20, 30), anchor="lm")
            d.text((70, yb + 110), "A new electronic cash system. No central server.", font=font(F_SANS, 24), fill=(40, 40, 50), anchor="lm")
            d.text((70, yb + 150), "Download: bitcoin-0.1.0.rar", font=font(F_SANS, 24), fill=(0, 70, 200), anchor="lm")
    else:
        ventana(d, 120, 40, sw - 240, sh - 130, "Bitcoin")
        d.text((140, 102), "File   Settings   Help", font=font(F_SANS, 22), fill=(20, 20, 30), anchor="lm")
        tg = WT("N14", "generate"); gen = T >= tg + .25
        d.rectangle((150, 130, 172, 152), fill=WHITE, outline=(20, 20, 30), width=2)
        if gen: d.line((153, 141, 160, 149, 170, 133), fill=(0, 140, 0), width=4)
        d.text((186, 141), "Generate Coins", font=font(F_SANSB, 24), fill=(20, 20, 30), anchor="lm")
        tf = WT("N14", "50"); bal = 50 if T >= tf else 0
        d.text((150, 200), "Balance:", font=font(F_SANS, 26), fill=(20, 20, 30), anchor="lm")
        d.text((280, 200), f"{bal:.2f}", font=font(F_SANSB, int(34 * popscale(T, tf) if T >= tf else 34)), fill=(0, 120, 0) if bal else (20, 20, 30), anchor="lm")
        d.text((150, 250), "Status: " + ("Generating..." if gen else "Idle"), font=font(F_SANS, 22), fill=(80, 80, 90), anchor="lm")
        d.rectangle((150, 290, sw - 150, sh - 120), fill=WHITE, outline=(150, 150, 160))
        if T >= tf:
            d.text((170, 320), "Date            Description              Credit", font=font(F_MONO, 20), fill=(80, 80, 90), anchor="lm")
            d.text((170, 360), "1/9/2009 23:58  Generated (50 matures) +50.00", font=font(F_MONO, 20), fill=(20, 20, 30), anchor="lm")
        if T < tg + .6 and T >= tg - .4:   # cursor que hace clic
            u = ease((T - tg + .4) / .5); cx, cy = 400 - 240 * u, 300 - 160 * u
            d.polygon([(cx, cy), (cx, cy + 34), (cx + 9, cy + 26), (cx + 16, cy + 40), (cx + 22, cy + 37), (cx + 15, cy + 24), (cx + 26, cy + 24)], fill=WHITE, outline=(0, 0, 0))
        if T >= S("N16"):
            tm = WT("N16", "appears")
            if T >= tm:
                u = popscale(T, tm, .3)
                bw, bh = int(720 * u), int(300 * u)
                bx, by = sw // 2 - bw // 2, sh // 2 - bh // 2 - 20
                if bw > 40:
                    ventana(d, bx, by, bw, bh, "New message" if u > .7 else "")
                    if u > .9:
                        d.text((bx + 30, by + 80), "From: (unknown)", font=font(F_SANS, 22), fill=(110, 110, 120), anchor="lm")
                        msg = "I know where you came from."
                        t17 = S("N17"); n = int(len(msg) * clamp((T - t17 + .1) / max(.3, E("N17") - t17)))
                        d.text((bx + 30, by + 170), msg[:n] + ("|" if int(T * 3) % 2 and n < len(msg) else ""), font=font(F_SANSB, 40), fill=(150, 10, 10), anchor="lm")
    scan(sc, 20)
    if gl:   # glitch del 3:12 (sin destellos rojos)
        g = int(T * 30)
        if g % 5 in (0, 1) and T < WT("N16", "appears") + .2:
            arr = np.array(sc); sh_ = (g * 37) % 40 - 20
            for band in range(6):
                y1 = (g * 53 + band * 97) % sh; y2 = min(sh, y1 + 18)
                arr[y1:y2] = np.roll(arr[y1:y2], sh_ * (band + 1), axis=1)
            sc = Image.fromarray(arr)
    c.alpha_composite(sc, (sx, sy))
    return c

def sc_cara(T, nombre, t0, luz=True, latido=False):
    c = bg("bg_noche", T, t0, 1.35, 1.45, 5, .5, .5).filter(ImageFilter.GaussianBlur(6))
    pul = 1 + (.025 * max(0, math.sin(T * 2 * PI_ * 1.1)) ** 8 if latido else 0)
    put(c, nombre, W / 2, 720, 1.3 * pul)
    if luz:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.ellipse((W / 2 - 700, 200, W / 2 + 700, 1300), fill=CYAN + (60,))
        c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(80)))
    if latido: c.alpha_composite(VIG_HARD)
    return c

def sc_decidido(T):
    c = sc_cara(T, "heroe_decidido", S("N15"))
    stamp(c, T, WT("N15", "missing"), "NOT THIS TIME", 1500, 300, ORG, -8, 90)
    return c

def sc_miedo(T):
    c = sc_cara(T, "heroe_miedo", S("N18"), True, True)
    d = ImageDraw.Draw(c)
    if T >= WT("N18", "nobody"):
        etiqueta(c, T, WT("N18", "nobody"), "NOBODY KNOWS.", 380, 420, WHITE, OL, 40)
    if T >= WT("N18", "nobody", 2):
        etiqueta(c, T, WT("N18", "nobody", 2), "NOBODY CAN KNOW.", 1540, 420, RED, WHITE, 40)
    return c

def sc_voto(T):
    s0 = S("N19")
    c = Image.new("RGBA", (W, H), (12, 10, 24, 255)); d = ImageDraw.Draw(c)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.ellipse((-200, 100, 900, 1000), fill=(60, 140, 255, 60)); od.ellipse((1020, 100, 2120, 1000), fill=(255, 80, 80, 50))
    c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(120)))
    text(d, (W / 2, 120), "WHAT DO YOU DO?", 96 * popscale(T, s0), WHITE, stroke=8)
    ta, tb = WT("N19", "a"), WT("N19", "b")
    for (t, lab, sub, cx, col) in ((ta, "A", "REPLY", 500, (60, 140, 255)), (tb, "B", "DELETE IT", 1420, (255, 90, 90))):
        if T < t: continue
        u = popscale(T, t); w, h = 700 * u, 520 * u
        panel(c, (cx - w / 2, 560 - h / 2, cx + w / 2, 560 + h / 2), (24, 22, 44), 245, 36, col, 8)
        if u > .6:
            d.ellipse((cx - 90, 360, cx + 90, 540), fill=col, outline=WHITE, width=6)
            text(d, (cx, 450), lab, 130, WHITE)
            text(d, (cx, 640), sub, 84, WHITE)
            text(d, (cx, 730), "find out who knows your secret" if lab == "A" else "keep mining like nothing happened", 30, GRIS, f=F_UI)
    tc = WT("N20", "comment")
    if T >= tc:
        u = popscale(T, tc)
        d.rounded_rectangle((W / 2 - 430 * u, 900 - 64 * u, W / 2 + 430 * u, 900 + 64 * u), 30, fill=YEL, outline=OL, width=6)
        if u > .6:
            text(d, (W / 2 - 30, 902), "COMMENT  A  OR  B", 70, OL)
            bob = 8 * math.sin(T * 6)
            d.polygon([(W / 2 + 330, 880 + bob), (W / 2 + 380, 880 + bob), (W / 2 + 355, 925 + bob)], fill=OL)
    return c

SCENES = [(0.0, sc_hook), (S("N02") - .35, sc_alarma), (S("N03") - .1, sc_cuarto), (S("N04") - .15, sc_movil),
          (S("N05") - .2, sc_espejo), (S("N06") - .2, sc_salon_tv), (S("N07") - .25, sc_satoshi), (S("N09") - .2, sc_precio),
          (S("N10") - .2, sc_banco), (S("Y01") - .25, sc_papa), (S("N12") - .5, sc_noche), (S("N13") - .25, sc_pc),
          (S("N15") - .2, sc_decidido), (S("N16") - .3, sc_pc), (S("N18") - .2, sc_miedo), (S("N19") - .3, sc_voto)]
TW = .32

def hblur(im, k):
    if k <= 1: return im
    return im.resize((max(1, W // k), H), Image.BILINEAR).resize((W, H), Image.BILINEAR)

IMPACTS = [WT("N01", "2009"), WT("N04", "2009"), WT("N05", "19"), WT("N09", "hundred"), S("D02") + .35, S("N17")]

def frame(T):
    idx = max(i for i, (t, f) in enumerate(SCENES) if T >= t)
    t0, fn = SCENES[idx]
    c = fn(T)
    u = (T - t0) / TW
    if idx > 0 and u < 1:   # whip-pan entre escenas (sin fundidos a negro)
        e = ease(u); prev = SCENES[idx - 1][1](T)
        k = int(2 + 22 * math.sin(PI_ * u))
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        canvas.alpha_composite(hblur(prev, k), (int(-W * e), 0))
        canvas.alpha_composite(hblur(c, k), (int(W * (1 - e)), 0))
        c = canvas
    amp = sum(14 * math.exp(-(T - ti) * 7) for ti in IMPACTS if 0 <= T - ti < .7)
    if amp > .6:
        z = 1.03; cc = c.resize((int(W * z), int(H * z)), Image.BILINEAR)
        dx = amp * math.sin(T * 95); dy = amp * math.cos(T * 71)
        ox = (cc.width - W) / 2 + dx; oy = (cc.height - H) / 2 + dy
        c = cc.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    c.alpha_composite(VIG)
    c.alpha_composite(grains()[int(T * 24) % 4])
    draw_hud(c, T)
    draw_caption(c, T)
    return c.convert("RGB")

def render_scene(i, out):
    t0 = SCENES[i][0]; t1 = SCENES[i + 1][0] if i + 1 < len(SCENES) else TOTAL
    f0, f1 = round(t0 * FPS), round(t1 * FPS)
    tmp = out + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp],
                         stdin=subprocess.PIPE)
    for f in range(f0, f1): p.stdin.write(frame(f / FPS).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0: os.replace(tmp, out)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "still":
        for t in sys.argv[2:]: frame(float(t)).save(os.path.join(TMP, f"f_{float(t):06.2f}.jpg"), quality=88)
    elif cmd == "info":
        for lid, (a, b, s0, src, ws) in TL.items(): print(lid, round(a, 2), round(b, 2), src, " ".join(w for w, _, _ in ws)[:70])
        print("TOTAL", round(TOTAL, 2)); print([round(t, 2) for t, f in SCENES])
    elif cmd == "scenes":
        from multiprocessing import Pool
        ids = [int(x) for x in sys.argv[2:]] or list(range(len(SCENES)))
        with Pool(2) as pool:
            pool.starmap(render_scene, [(i, os.path.join(TMP, f"s{i:02d}.mp4")) for i in ids])
    elif cmd == "join":
        with open(os.path.join(TMP, "list.txt"), "w") as f:
            for i in range(len(SCENES)): f.write(f"file 's{i:02d}.mp4'\n")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(TMP, "list.txt"), "-c", "copy",
                        os.path.join(TMP, "video.mp4")], check=True)
