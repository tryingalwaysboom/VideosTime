"""Monta el Ep.1 "You Wake Up in 2009 Knowing Everything About Bitcoin" (1920x1080, 30 fps).
python3 render.py info | still 3.2 40 ... | scenes [ids] | join"""
import json, math, os, subprocess, sys, difflib, re
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from guion import LINEAS, CLIPS, HUECO_SIN_AUDIO

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1080, 30
BW, BH = 1920, 1080   # tamaño de los fondos dibujados (a 1x)
COLD = 3.4            # arranque en frío (gancho mudo que explica la serie)
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
    t, tl = COLD - 0.12, {}
    for lid, who, txt in LINEAS:
        t += GAP.get(lid, .25)
        if lid in CLIPS:
            p = os.path.join(AUD, CLIPS[lid])
            if os.path.exists(p):
                d = dur_audio(p); ww = whisper(CLIPS[lid])
                if ww: words = [(w["p"], t + w["inicio"], t + w["fin"]) for w in ww]
                else:
                    tw = txt.split(); words = [(w, t + d * i / len(tw), t + d * (i + 1) / len(tw)) for i, w in enumerate(tw)]
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

def view(z, fx, fy):
    """Origen (en coords del fondo 1x) de la ventana W x H vista con zoom z."""
    return (BW - W / z) * fx, (BH - H / z) * fy

def bg(name, T, t0, zoom0=1.0, zoom1=1.06, dur=8, fx=0.5, fy=0.5):
    im = layer(name)
    z = zoom0 + (zoom1 - zoom0) * ease_io((T - t0) / dur)
    x0, y0 = view(z, fx, fy)
    return im.resize((W, H), Image.BILINEAR, box=(2 * x0, 2 * y0, 2 * (x0 + W / z), 2 * (y0 + H / z)), reducing_gap=2.0).convert("RGBA")

def zoom_at(T, t0, zoom0, zoom1, dur): return zoom0 + (zoom1 - zoom0) * ease_io((T - t0) / dur)

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
        size = 72 * k; f = font(F_ANTON, size)
        widths = [d.textlength(p + " ", font=f) for p, _ in g]
        total = sum(widths) - d.textlength(" ", font=f)
        if total > 980:
            f = font(F_ANTON, size * 980 / total); widths = [d.textlength(p + " ", font=f) for p, _ in g]; total = sum(widths) - d.textlength(" ", font=f)
        x = W / 2 - total / 2; y = 960
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
            d.rounded_rectangle((W / 2 - tw / 2 - 18, 862, W / 2 + tw / 2 + 18, 904), 12, fill=CYAN if who == "Y" else YEL)
            d.text((W / 2, 883), tag, font=ft, fill=OL, anchor="mm")
        return

# ---------------------------------------------------------------- barra superior de la serie (cuadrado: 2 filas)
EPISODIO = 1

def btc_icon(d, cx, cy, r, on=True):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=ORG if on else (70, 78, 100), outline=(110, 60, 0) if on else (40, 44, 60), width=3)
    for dx in (-.18, .12): d.line((cx + dx * r, cy - r * .72, cx + dx * r, cy + r * .72), fill=WHITE, width=max(2, int(r * .12)))
    d.text((cx + 1, cy + 1), "B", font=font(F_UI, int(r * 1.2)), fill=WHITE, anchor="mm")

def coin_usd(d, cx, cy, r, on=True):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(90, 190, 110) if on else (70, 78, 100), outline=(30, 90, 40) if on else (40, 44, 60), width=3)
    d.text((cx, cy + 1), "$", font=font(F_UI, int(r * 1.2)), fill=WHITE, anchor="mm")

HX0, HY0, HX1, HY1 = 24, 18, W - 24, 156

@lru_cache(1)
def barra_base():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((HX0, HY0 + 8, HX1, HY1 + 10), 24, fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).rounded_rectangle((HX0, HY0, HX1, HY1), 24, outline=ORG + (140,), width=6)
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((HX0, HY0, HX1, HY1), 24, fill=(12, 10, 26, 215), outline=ORG + (120,), width=2)
    d.rounded_rectangle((HX0 + 14, HY0 + 14, HX0 + 104, HY0 + 58), 12, fill=ORG)
    d.text((HX0 + 59, HY0 + 37), f"EP.{EPISODIO}", font=font(F_ANTON, 30), fill=OL, anchor="mm")
    d.line((HX0 + 16, HY0 + 70, HX1 - 16, HY0 + 70), fill=(255, 255, 255, 35), width=2)
    for xs in (378, 712): d.line((xs, HY0 + 80, xs, HY1 - 10), fill=(255, 255, 255, 40), width=2)
    d.line((560, HY0 + 12, 560, HY0 + 60), fill=(255, 255, 255, 40), width=2)
    d.text((580, HY0 + 22), "GOAL", font=font(F_UI, 15), fill=ORG, anchor="lm")
    return im

def draw_hud(canvas, T):
    if T >= S("N19") - .1 or T < COLD: return
    canvas.alpha_composite(barra_base()); d = ImageDraw.Draw(canvas)
    def pop(t): return 1 + .28 * math.sin(clamp((T - t) / .3) * PI_) if 0 <= T - t < .3 else 1
    t_fecha = WT("N04", "january")
    if T < S("N12"): fecha, hora, tf = ("JAN ?, ????" if T < t_fecha else "JAN 9, 2009"), "7:58 AM", t_fecha
    elif T < S("N16"): fecha, hora, tf = "JAN 9, 2009", "11:47 PM", S("N12")
    else: fecha, hora, tf = "JAN 10, 2009", "3:12 AM", S("N16")
    if T < S("N02") - .4:
        if T < WT("N01", "2009"): fecha, hora, tf = "??? ?, 2026", "11:59 PM", 0
        else: fecha, hora, tf = "??? ?, 2009", "?:?? AM", WT("N01", "2009")
    yr = HY0 + 37
    d.text((134, yr), fecha, font=font(F_ANTON, 36 * pop(tf)), fill=WHITE, anchor="lm")
    d.text((420, yr + 2), hora, font=font(F_UI, 22), fill=GRIS, anchor="lm")
    # objetivo (fila 1, derecha)
    if T < WT("N09", "future"): goal, tg = "Figure out what's happening", S("N02")
    elif T < WT("N14", "50"): goal, tg = "Get Bitcoin before anyone else", WT("N09", "future")
    else: goal, tg = "Keep mining. Tell no one.", WT("N14", "50")
    if T < S("N02") - .4: goal = "Sleep" if T < WT("N01", "2009") else "???"
    d.text((580, HY0 + 46), goal, font=font(F_UI, 23 * pop(tg)), fill=WHITE, anchor="lm")
    # fila 2: precio, tus BTC, cash
    y2 = HY0 + 106
    t_p = WT("N09", "zero"); on = T >= t_p
    btc_icon(d, 64, y2, 22, on)
    d.text((98, y2 - 15), "BTC PRICE", font=font(F_UI, 16), fill=GRIS, anchor="lm")
    d.text((98, y2 + 13), "$0.00" if on else "?", font=font(F_ANTON, 32 * pop(t_p)), fill=WHITE if on else GRIS, anchor="lm")
    t_b = WT("N14", "50"); hb = T >= t_b
    btc_icon(d, 418, y2, 22, hb)
    d.text((452, y2 - 15), "YOUR BTC", font=font(F_UI, 16), fill=GRIS, anchor="lm")
    v = int(50 * ease((T - t_b) / .9)) if hb else 0
    d.text((452, y2 + 13), str(v), font=font(F_ANTON, 32 * pop(t_b)), fill=ORG if hb else WHITE, anchor="lm")
    t_c = WT("N10", "three"); hc = T >= t_c
    coin_usd(d, 752, y2, 22, hc)
    d.text((786, y2 - 15), "CASH", font=font(F_UI, 16), fill=GRIS, anchor="lm")
    d.text((786, y2 + 13), money(int(340 * ease((T - t_c) / .8))) if hc else "?", font=font(F_ANTON, 32 * pop(t_c)), fill=WHITE if hc else GRIS, anchor="lm")

# ---------------------------------------------------------------- escenas (1080x1080)
def cold_base(T):
    """Monitor a las 3:12 con el mensaje, en una habitación a oscuras (sin texto encima)."""
    c = Image.new("RGBA", (W, H), (5, 6, 14, 255))
    mon = scaled("monitor_grande", .66); mx, my = (W - mon.width) // 2, 290
    c.alpha_composite(mon, (mx, my)); k = mon.width / 1580
    sx, sy, sw, sh = int(mx + 100 * k + 4), int(my + 80 * k + 4), int(1380 * k - 8), int(820 * k - 8)
    sc = pantalla_pc(E("N17") + 1.5)
    beat = [0.0, .55, 1.25, 1.75, 2.45]
    g = int(T * 30)
    if any(0 < T - b < .12 for b in beat) or 1.3 < T < 1.5:
        arr = np.array(sc); sh_ = (g * 37) % 40 - 20
        for band in range(6):
            y1 = (g * 53 + band * 97) % REF_SH; y2 = min(REF_SH, y1 + 18)
            arr[y1:y2] = np.roll(arr[y1:y2], sh_ * (band + 1), axis=1)
        sc = Image.fromarray(arr)
    sc = sc.resize((sw, sh), Image.LANCZOS)
    # reflejo de alguien detrás de ti en la pantalla (aparece tras el zoom out)
    if T >= 1.55:
        a = .5 * ease((T - 1.55) / .5) * (.85 + .15 * math.sin(T * 23))
        fig = scaled("nakamoto", .55).copy(); fig.putalpha(fig.getchannel("A").point(lambda v: int(v * a)))
        sc.alpha_composite(fig, (int(sw * .62), int(sh - fig.height * .8)))
    c.alpha_composite(sc, (sx, sy))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.ellipse((W / 2 - 620, sy - 220, W / 2 + 620, sy + sh + 220), fill=CYAN + (55,))
    c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(90)))
    return c, (sx, sy, sw, sh), beat

def sc_cold(T):
    """Gancho: suspense. Primerísimo plano del mensaje que se acerca lento con el latido, tirón atrás,
    alguien se refleja en la pantalla, '19 HOURS EARLIER'. La premisa está escrita desde el fotograma 0."""
    c, (sx, sy, sw, sh), beat = cold_base(T)
    # cámara: muy cerca del texto rojo, se acerca despacio; a 1.25s tirón hacia atrás
    fx_, fy_ = sx + sw * .5, sy + sh * .48
    if T < 1.25: zc = 1.38 + .22 * ease_io(T / 1.25)
    elif T < 1.55: zc = 1.6 - .57 * ease((T - 1.25) / .3)
    else: zc = 1.03 + .05 * (T - 1.55)
    cw, chh = W / zc, H / zc
    x0 = min(max(0, fx_ - cw / 2), W - cw); y0 = min(max(0, fy_ - chh / 2), H - chh)
    c = c.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + chh))
    # latido: la viñeta se cierra en cada golpe (sin destellos de color)
    pulse = sum(math.exp(-(T - b) * 7) for b in beat if T >= b)
    c.alpha_composite(VIG)
    if pulse > .05:
        v = VIG_HARD.copy(); v.putalpha(v.getchannel("A").point(lambda x: int(x * min(1, .55 * pulse))))
        c.alpha_composite(v)
    c.alpha_composite(_cold_top())
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((W / 2 - 70, 26, W / 2 + 70, 70), 14, fill=ORG)
    d.text((W / 2, 48), "PART 1", font=font(F_ANTON, 32), fill=OL, anchor="mm")
    hit = 1 + .14 * math.sin(clamp((T - 1.25) / .25) * PI_) if T >= 1.25 else 1
    text(d, (W / 2, 128), "POV: YOU WAKE UP IN 2009", 76 * hit, WHITE, stroke=6)
    text(d, (W / 2, 212), "KNOWING BITCOIN'S FUTURE", 76 * hit, ORG, stroke=6)
    pul = 1 + .05 * pulse
    bw, bh = 470 * pul, 52 * pul
    d.rounded_rectangle((W / 2 - bw, 935 - bh, W / 2 + bw, 935 + bh), 30, fill=YEL, outline=OL, width=6)
    text(d, (W / 2, 937), "YOU DECIDE WHAT HAPPENS NEXT", 60 * pul, OL)
    if 1.75 <= T < 2.6: etiqueta(c, T, 1.75, "SOMEONE IS WATCHING", W / 2, 820, (20, 18, 34), WHITE, 34)
    if T >= 2.6:
        dark(c, 185 * ease((T - 2.6) / .2))
        stamp(c, T, 2.6, "19 HOURS EARLIER...", W / 2, 560, YEL, -4, 84)
    amp = sum(14 * math.exp(-(T - ti) * 9) for ti in (1.25, 2.6) if T >= ti) + 3 * pulse
    if amp > .8:
        z = 1.03; cc = c.resize((int(W * z), int(H * z)), Image.BILINEAR)
        ox = (cc.width - W) / 2 + amp * math.sin(T * 95); oy = (cc.height - H) / 2 + amp * math.cos(T * 71)
        c = cc.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    return c

@lru_cache(1)
def _cold_top():
    top = Image.new("RGBA", (W, H), (0, 0, 0, 0)); td = ImageDraw.Draw(top)
    for y in range(0, 300): td.line((0, y, W, y), fill=(6, 5, 14, int(250 * (1 - max(0, y - 230) / 70))))
    return top

def sc_hook(T):
    """'You go to sleep in 2026' (te ves dormido con el móvil) -> túnel del tiempo con años volando -> 2009."""
    t09 = WT("N01", "2009"); tb = WT("N01", "bitcoin"); s0 = COLD
    if T < t09 - .25:
        c = bg("bg_noche", T, s0, 1.25, 1.45, 3, .5, .6).filter(ImageFilter.GaussianBlur(3))
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.ellipse((W / 2 - 420, 380, W / 2 + 420, 1200), fill=(150, 170, 255, 70))
        c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(70)))
        z = 1.0 + .12 * ease_io((T - s0) / 2.2)
        put(c, "heroe_dormido", W / 2, 840 + 20 * math.sin(T * 1.6), 1.15 * z)
        d = ImageDraw.Draw(c)
        for i in range(3):   # zzz que suben
            ph = (T * .6 + i / 3) % 1
            text(d, (W / 2 + 220 + ph * 90, 430 - ph * 200), "Z", 40 + 30 * ph, (230, 235, 255), stroke=4)
        # móvil de 2026 brillando en la mano
        py = 640 + 6 * math.sin(T * 2)
        gl2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl2).ellipse((W / 2 - 460, py - 60, W / 2 - 200, py + 240), fill=(120, 170, 255, 90))
        c.alpha_composite(gl2.filter(ImageFilter.GaussianBlur(40))); d = ImageDraw.Draw(c)
        d.rounded_rectangle((W / 2 - 380, py, W / 2 - 280, py + 170), 18, fill=(20, 22, 30), outline=OL, width=5)
        d.rounded_rectangle((W / 2 - 372, py + 12, W / 2 - 288, py + 158), 12, fill=(120, 170, 255))
        d.text((W / 2 - 330, py + 60), "11:59", font=font(F_ANTON, 26), fill=WHITE, anchor="mm")
        d.text((W / 2 - 330, py + 95), "2026", font=font(F_UI, 16), fill=WHITE, anchor="mm")
        etiqueta(c, T, s0 + .1, "YOU GO TO SLEEP", W / 2, 230, CYAN, OL, 40)
        u = popscale(T, WT("N01", "2026"))
        text(d, (W / 2, 340), "2026", 120 * max(u, .01), WHITE, stroke=8) if T >= WT("N01", "2026") else None
        return c
    # túnel del tiempo
    c = Image.new("RGBA", (W, H), (10, 9, 22, 255))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    sp = 2.2 if T < t09 + .8 else .8
    for i in range(18):
        ph = ((T * sp + i / 18) % 1); r = 30 + ph ** 2 * 1100
        a = int(190 * math.sin(ph * PI_))
        od.ellipse((W / 2 - r * 1.2, H / 2 - r, W / 2 + r * 1.2, H / 2 + r), outline=ORG + (a,) if i % 2 else CYAN + (a,), width=6)
    c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(2)))
    u2 = clamp((T - (t09 - .25)) / .9)
    yr_now = int(round(2026 - 17 * ease(u2)))
    # tarjetas de calendario con años que vuelan hacia la cámara
    if u2 < 1:
        for k in range(6):
            ph = ((T * 2.6 + k / 6) % 1); sc_ = .3 + ph * 2.6
            ang = k * 1.05 + T * .8; rx = math.cos(ang) * 380 * ph; ry = math.sin(ang) * 330 * ph
            card = Image.new("RGBA", (220, 160), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
            cd.rounded_rectangle((4, 4, 216, 156), 14, fill=(246, 243, 234), outline=OL, width=5)
            cd.rectangle((4, 4, 216, 46), fill=(198, 47, 47))
            cd.text((110, 102), str(max(2009, yr_now + k)), font=font(F_ANTON, 64), fill=OL, anchor="mm")
            card = card.resize((int(220 * sc_), int(160 * sc_)), Image.BILINEAR).rotate(ang * 20 % 40 - 20, expand=True)
            card.putalpha(card.getchannel("A").point(lambda v: int(v * min(1, (1 - ph) * 2.5))))
            c.alpha_composite(card, (int(W / 2 + rx - card.width / 2), int(H / 2 + ry - card.height / 2)))
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(gl)
    big = 300 * (1 + .25 * math.sin(clamp((T - t09) / .3) * PI_)) if T >= t09 else 300
    gd.text((W / 2, 470), str(yr_now), font=font(F_ANTON, big), fill=ORG + (255,), anchor="mm")
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(18))); c.alpha_composite(gl)
    d = ImageDraw.Draw(c)
    d.text((W / 2, 470), str(yr_now), font=font(F_ANTON, big), fill=WHITE, anchor="mm")
    etiqueta(c, T, t09, "YOU WAKE UP", W / 2, 200, YEL, OL, 40)
    if T >= tb:
        u = popscale(T, tb, .5)
        for k in range(5):   # monedas que caen girando
            x = 120 + k * 210; y = 640 + ((T - tb) * 260 + k * 90) % 300
            put(c, "btc_coin", x, y, .4 * u, rot=(T * 180 + k * 70) % 360)
    if u2 < 1:   # remolino: rota todo un poco mientras viajas
        c = c.rotate(8 * math.sin(T * 9) * (1 - u2), resample=Image.BILINEAR, center=(W / 2, H / 2), fillcolor=(10, 9, 22))
    return c

def sc_alarma(T):
    s0 = S("N02"); z = zoom_at(T, s0, 1.9, 1.75, 3)
    c = bg("bg_bedroom", T, s0, 1.9, 1.75, 3, .5, .78)
    x0, y0 = view(z, .5, .78)
    ring = s0 - .3 <= T < WT("N02", "phone", fin=True) + .6
    sh = 8 * math.sin(T * 60) if ring else 0
    ax, ay = (800 - x0) * z, (632 - y0) * z
    put(c, "alarma", ax + sh, ay, 150 * z / 300, rot=sh * .8)
    if ring:
        d = ImageDraw.Draw(c)
        for k in range(3):
            a = (T * 3 + k / 3) % 1; r = 90 * z + a * 140
            d.arc((ax - r, ay - r, ax + r, ay + r), 200, 250, fill=(255, 255, 255, int(255 * (1 - a))), width=8)
            d.arc((ax - r, ay - r, ax + r, ay + r), 290, 340, fill=(255, 255, 255, int(255 * (1 - a))), width=8)
        stamp(c, T, s0 - .2, "RIIIING!", 800, 290, YEL, 8, 90)
    etiqueta(c, T, WT("N02", "real"), "A REAL ALARM CLOCK", ax, ay - 200, YEL)
    return c

def sc_cuarto(T):
    s0, e0 = S("N03"), E("N03")
    u = ease_io((T - s0) / (e0 - s0 + .4)); z = 1.25 - .15 * u; fx = .2 + .8 * u
    c = bg("bg_bedroom", T, s0, z, z, 1, fx, .45)
    x0, y0 = view(z, fx, .45)
    sc_ = lambda X, Y: ((X - x0) * z, (Y - y0) * z)
    px, py = sc_(985, 470); etiqueta(c, T, WT("N03", "posters"), "POSTERS", px, py, YEL)
    mx, my = sc_(1500, 225); etiqueta(c, T, WT("N03", "monitor"), "CRT MONITOR · 17\"", mx, my, CYAN)
    fx_, fy_ = sc_(1262, 560); etiqueta(c, T, WT("N03", "flip"), "FLIP PHONE", fx_, fy_, YEL)
    if T >= WT("N03", "apartment"):
        stamp(c, T, WT("N03", "apartment", fin=True), "NOT YOUR ROOM", W / 2, 770, RED, -6, 80)
    return c

def sc_movil(T):
    s0 = S("N04")
    c = bg("bg_bedroom", T, s0, 1.3, 1.36, 4, .9, .6).filter(ImageFilter.GaussianBlur(10)); dark(c, 110)
    u = ease((T - s0 + .3) / .5)
    cy = 580 + 600 * (1 - u)
    put(c, "movil", W / 2, cy, .9, rot=-4)
    d = ImageDraw.Draw(c)
    k = .9; sx, sy = W / 2 - 210 * k + 96 * k, cy - 460 * k + 80 * k; sw_ = 228 * k
    d.text((sx + sw_ / 2, sy + 36), "08:00", font=font(F_MONO, 30), fill=OL, anchor="mm")
    tj = WT("N04", "january")
    if T >= tj:
        d.text((sx + sw_ / 2, sy + 125), "FRI", font=font(F_ANTON, 40 * popscale(T, tj)), fill=OL, anchor="mm")
        d.text((sx + sw_ / 2, sy + 180), "09 JAN", font=font(F_ANTON, 46 * popscale(T, tj)), fill=OL, anchor="mm")
    t9 = WT("N04", "2009")
    if T >= t9:
        d.text((sx + sw_ / 2, sy + 235), "2009", font=font(F_ANTON, 46 * popscale(T, t9)), fill=(200, 40, 40), anchor="mm")
        stamp(c, T, t9 + .1, "2009", 850, 300, RED, -12, 110)
    return c

def sc_espejo(T):
    s0 = S("N05"); z = zoom_at(T, s0, 1.0, 1.06, 4)
    c = bg("bg_espejo", T, s0, 1.0, 1.06, 4, .5, .5)
    x0, y0 = view(z, .5, .5)
    mx0, my0, mx1, my1 = (620 - x0) * z, (180 - y0) * z, (1300 - x0) * z, (820 - y0) * z
    ref = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tr = WT("N05", "19")
    nm = "heroe_shock" if T >= WT("N05", "mirror") else "heroe_miedo"
    jump = 18 * math.sin(clamp((T - tr) / .3) * PI_) if T >= tr else 0
    put(ref, nm, (mx0 + mx1) / 2, my0 + 430 * z - jump, 1.15 * z)
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rounded_rectangle((mx0 + 4, my0 + 4, mx1 - 4, my1 - 4), int(24 * z), fill=255)
    ref.alpha_composite(Image.new("RGBA", (W, H), (167, 196, 207, 60)))
    c.paste(ref, (0, 0), Image.composite(ref.getchannel("A"), Image.new("L", (W, H), 0), m))
    gl_ = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl_).polygon([(mx0 + 30, my0 + 30), (mx0 + 150, my0 + 30), (mx0 + 30, my0 + 170)], fill=(255, 255, 255, 80))
    c.alpha_composite(gl_)
    if T >= tr:
        stamp(c, T, tr, "AGE: 19", mx1 - 60, my0 + 120, YEL, -8, 90)
        etiqueta(c, T, tr + .25, "AGAIN.", mx1 - 60, my0 + 250, RED, WHITE, 36)
    return c

def tv_noticias(c, T, x, y, w, h, t0):
    tv = Image.new("RGBA", (w, h), (24, 40, 90, 255)); d = ImageDraw.Draw(tv)
    d.rectangle((0, 0, w, h * .62), fill=(40, 60, 120))
    pts = [(int(w * .08 + i * w * .84 / 9), int(h * .16 + (i ** 1.4) * h * .045 + 10 * math.sin(i * 1.7))) for i in range(10)]
    k = int(clamp((T - t0) / 1.4) * 9) + 1
    if k > 1: d.line(pts[:k], fill=(255, 80, 80), width=6)
    d.rectangle((0, h * .62, w, h * .80), fill=(200, 30, 40))
    d.text((18, h * .71), "BREAKING NEWS", font=font(F_ANTON, int(h * .1)), fill=WHITE, anchor="lm")
    d.rectangle((0, h * .80, w, h), fill=(245, 245, 245))
    tick = "  BANKS COLLAPSING · MILLIONS LOSE THEIR HOMES · DOW DOWN 34% IN 2008 · BAILOUTS ·  "
    f = font(F_UI, int(h * .085)); tw = d.textlength(tick, font=f); off = (T * 160) % tw
    for k2 in range(3): d.text((-off + k2 * tw, h * .9), tick, font=f, fill=(20, 20, 30), anchor="lm")
    scan(tv, 40)
    c.alpha_composite(tv, (int(x), int(y)))

def sc_salon_tv(T):
    s0 = S("N06"); z = zoom_at(T, s0, 1.0, 1.06, 8); fx = .78
    c = bg("bg_salon", T, s0, 1.0, 1.06, 8, fx, .4)
    x0, y0 = view(z, fx, .4)
    tv_noticias(c, T, (1170 - x0) * z + 6, (236 - y0) * z + 6, int(508 * z), int(356 * z), S("V01"))
    td = S("D01") - .7
    if T >= td:
        u = ease((T - td) / .6)
        put(c, "papa_serio", 230 - 450 * (1 - u), 760, 1.0)
        put(c, "taza", 470 - 450 * (1 - u), 840, .55)
    return c

def sc_satoshi(T):
    c = Image.new("RGBA", (W, H), (12, 10, 24, 255))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.ellipse((W / 2 - 500, H / 2 - 420, W / 2 + 500, H / 2 + 420), fill=ORG + (55,))
    c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(c)
    for i in range(15):
        x = 36 + i * 72; sp = 60 + (i * 37) % 90
        for j in range(12):
            y = (j * 92 + T * sp + i * 51) % (H + 100) - 50
            d.text((x, y), "01"[(i + j) % 2], font=font(F_MONO, 30), fill=(247, 147, 26, 50), anchor="mm")
    tn = WT("N07", "satoshi"); tdays = WT("N07", "six")
    if tdays <= T < tn:
        u = popscale(T, tdays); text(d, (W / 2, 470), "6 DAYS AGO", 170 * u, ORG, stroke=10)
        text(d, (W / 2, 630), "JANUARY 3, 2009", 56 * u, WHITE)
    if T >= tn:
        u = ease((T - tn) / .5); put(c, "nakamoto", 270, 620 + 80 * (1 - u), .72, alpha=u)
        etiqueta(c, T, tn + .2, "SATOSHI NAKAMOTO", 270, 270, ORG, WHITE, 30)
    if T >= WT("N07", "first"):
        u = popscale(T, WT("N07", "first"))
        panel(c, (545, 330, 545 + 500 * u, 650), (250, 246, 235), 250, 22, OL, 6)
        if u > .6:
            text(d, (795, 395), "BLOCK #0", 56, OL)
            text(d, (795, 458), "\"THE GENESIS BLOCK\"", 34, ORG)
            text(d, (795, 528), "MINED: JAN 3, 2009", 28, (90, 80, 100), f=F_UI)
            text(d, (795, 585), "REWARD: 50 BTC", 28, (90, 80, 100), f=F_UI)
    tk = WT("N08", "nobody")
    if T >= tk: stamp(c, T, tk, "ALMOST NOBODY KNOWS", W / 2, 790, RED, -4, 64)
    return c

def sc_precio(T):
    s0 = S("N09")
    c = Image.new("RGBA", (W, H), (12, 10, 24, 255)); d = ImageDraw.Draw(c); scan(c, 40)
    text(d, (W / 2, 215), "TODAY · 2009", 40, GRIS, f=F_UI)
    put(c, "btc_coin", 330, 370, .75 * popscale(T, s0 + .1, .5), rot=6 * math.sin(T * 2))
    tz = WT("N09", "zero")
    if T >= tz:
        text(d, (680, 360), "$0.00", 130 * popscale(T, tz), WHITE, stroke=8)
        text(d, (680, 450), "PER BITCOIN", 28, GRIS, f=F_UI)
    tf = WT("N09", "future")
    if T >= tf:
        u = ease((T - tf) / .5)
        flecha_a(d, W / 2, 500, W / 2, 500 + 90 * u, ORG, 12)
        text(d, (W / 2, 640), "YOUR FUTURE", 40, ORG, f=F_UI)
        th = WT("N09", "hundred")
        if T >= th:
            v = int(100000 * ease((T - th) / 1.0))
            text(d, (W / 2, 770), f"${v:,}+", 150 * popscale(T, th), ORG, stroke=8)
    return c

REF_SW, REF_SH = 1230, 726   # pantalla del monitor a tamaño de referencia (se dibuja así y se escala)

def monitor(c, T, t0):
    z = 1.0 + .04 * ease_io((T - t0) / 20)
    mon = scaled("monitor_grande", round(.66 * z, 3)); mx, my = (W - mon.width) // 2, 180 + (H - 180 - 120 - mon.height) // 2
    c.alpha_composite(mon, (mx, my))
    k = mon.width / 1580
    return int(mx + 100 * k + 4), int(my + 80 * k + 4), int(1380 * k - 8), int(820 * k - 8)

def pantalla_banco(T):
    w, h = REF_SW, REF_SH
    sc = Image.new("RGBA", (w, h), (236, 240, 246, 255)); d = ImageDraw.Draw(sc)
    d.rectangle((0, 0, w, 70), fill=(20, 60, 140)); d.text((24, 35), "FIRST HOMETOWN BANK · Online Banking", font=font(F_SANSB, 30), fill=WHITE, anchor="lm")
    d.rectangle((0, 70, w, 112), fill=(200, 210, 225)); d.text((24, 91), "Accounts   Transfers   Bill Pay   Log out", font=font(F_SANS, 24), fill=(30, 40, 70), anchor="lm")
    d.text((60, 190), "Student Checking  ****4417", font=font(F_SANSB, 36), fill=(30, 40, 70), anchor="lm")
    d.text((60, 260), "Available balance", font=font(F_SANS, 32), fill=(90, 100, 120), anchor="lm")
    tv = WT("N10", "three")
    if T >= tv:
        v = 340 * ease((T - tv) / .9)
        d.text((60, 370), f"${v:,.2f}", font=font(F_SANSB, int(130 * popscale(T, tv))), fill=(20, 120, 50), anchor="lm")
    rows = [("01/07/09", "GameStop", "-$59.99"), ("01/05/09", "Paycheck · Pizza Hut", "+$212.40"), ("01/02/09", "iTunes", "-$0.99")]
    for i, (a, b, cc) in enumerate(rows):
        yy = 490 + i * 60; d.line((60, yy - 28, w - 60, yy - 28), fill=(200, 205, 215), width=2)
        d.text((60, yy), a, font=font(F_SANS, 28), fill=(90, 100, 120), anchor="lm"); d.text((280, yy), b, font=font(F_SANS, 28), fill=(30, 40, 70), anchor="lm")
        d.text((w - 60, yy), cc, font=font(F_SANSB, 28), fill=(30, 40, 70), anchor="rm")
    scan(sc, 14)
    return sc

def sc_banco(T):
    s0 = S("N10")
    c = Image.new("RGBA", (W, H), (30, 26, 40, 255))
    sx, sy, sw, sh = monitor(c, T, s0)
    c.alpha_composite(pantalla_banco(T).resize((sw, sh), Image.LANCZOS), (sx, sy))
    te = WT("N10", "entire")
    if T >= te: stamp(c, T, te, "ENTIRE FORTUNE", 760, 650, RED, -8, 70)
    return c

def sc_papa(T):
    s0 = S("Y01"); z = zoom_at(T, s0, 1.12, 1.18, 9); fx = .228
    c = bg("bg_salon", T, s0, 1.12, 1.18, 9, fx, .5)
    x0, y0 = view(z, fx, .5)
    risa = T >= S("D02") - .05
    bounce = 10 * abs(math.sin(T * 14)) if risa else 0
    put(c, "heroe_decidido", 230, 760, 1.0)
    put(c, "papa_risa" if risa else "papa_serio", 870, 740 - bounce, .98)
    mx, my = (740 - x0) * z, (640 - y0) * z
    tr = S("D02") + .35
    if T >= tr + .25:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        sp = ease((T - tr - .25) / .5); ty = my + 78
        od.ellipse((mx - 20 - 110 * sp, ty - 7 - 7 * sp, mx + 20 + 120 * sp, ty + 7 + 7 * sp), fill=(90, 51, 32, 235), outline=OL, width=4)
        c.alpha_composite(ov)
    if T < tr: put(c, "taza", mx, my, .62)
    else:
        u = clamp((T - tr) / .35)
        put(c, "taza", mx + 36 * ease(u), my + 36 * ease(u), .62, rot=-85 * ease(u))
    if risa: etiqueta(c, T, S("D02") + .1, "HA HA HA", 880, 330, YEL, OL, 38)
    return c

def crt_noche(c, cx, cy, s):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.ellipse((cx - 560 * s, cy - 380 * s, cx + 560 * s, cy + 380 * s), fill=CYAN + (70,))
    c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(90)))

def sc_noche(T):
    s0 = S("N12")
    c = bg("bg_noche", T, s0, 1.0, 1.08, 9, .4, .55)
    on = T >= WT("N12", "turn"); s = .58
    shake = 4 * math.sin(T * 70) if T >= WT("N12", "fan") else 0
    cx, cy = W / 2 + shake, 520
    if on: crt_noche(c, cx, cy, 1.0)
    put(c, "monitor_grande", cx, cy, s)
    mw, mh = 1580 * s, 1060 * s
    x0, y0 = cx - mw / 2 + 100 * s + 4, cy - mh / 2 + 80 * s + 4
    scr = Image.new("RGBA", (int(1380 * s) - 8, int(820 * s) - 8), (0, 0, 0, 255)); sd = ImageDraw.Draw(scr)
    if on:
        boot = clamp((T - WT("N12", "turn")) / 1.4)
        if boot < 1: sd.text((26, 26), "Starting Windows XP" + "." * int(T * 4 % 4), font=font(F_MONO, 26), fill=(200, 200, 200))
        else:
            sd.rectangle((0, 0, scr.width, scr.height), fill=(58, 110, 165)); sd.rectangle((0, scr.height - 26, scr.width, scr.height), fill=(36, 94, 220))
            sd.rounded_rectangle((0, scr.height - 26, 80, scr.height), 10, fill=(60, 160, 60)); sd.text((40, scr.height - 13), "start", font=font(F_SANSB, 16), fill=WHITE, anchor="mm")
        scan(scr, 30)
        c.alpha_composite(scr, (int(x0), int(y0)))
    else:
        c.alpha_composite(scr, (int(x0), int(y0))); dark(c, 60)
    if T >= WT("N12", "fan"):
        d = ImageDraw.Draw(c)
        for k2 in range(4):
            a = (T * 2.5 + k2 / 4) % 1
            d.arc((960 - 60 - a * 80, 700 - 60 - a * 80, 960 + 60 + a * 80, 700 + 60 + a * 80), 220, 320, fill=(255, 255, 255, int(200 * (1 - a))), width=5)
        stamp(c, T, WT("N12", "jet"), "VRRRRRRR", 800, 250, CYAN, 8, 70)
    ta = WT("N12", "asleep")
    if ta <= T < WT("N12", "turn"): etiqueta(c, T, ta, "EVERYONE'S ASLEEP", W / 2, 260, (40, 44, 70), WHITE, 32)
    return c

def ventana(sd, x, y, w, h, title):
    sd.rounded_rectangle((x, y, x + w, y + h), 10, fill=(236, 233, 216), outline=(0, 60, 180), width=3)
    sd.rounded_rectangle((x, y, x + w, y + 40), 10, fill=(0, 84, 227)); sd.rectangle((x, y + 24, x + w, y + 40), fill=(0, 84, 227))
    sd.text((x + 14, y + 20), title, font=font(F_SANSB, 20), fill=WHITE, anchor="lm")
    sd.rounded_rectangle((x + w - 36, y + 7, x + w - 8, y + 33), 5, fill=(224, 80, 50), outline=WHITE, width=2)
    sd.text((x + w - 22, y + 20), "x", font=font(F_SANSB, 18), fill=WHITE, anchor="mm")

def pantalla_pc(T):
    sw, sh = REF_SW, REF_SH
    sc = Image.new("RGBA", (sw, sh), (58, 110, 165, 255)); d = ImageDraw.Draw(sc)
    d.rectangle((0, sh - 44, sw, sh), fill=(36, 94, 220)); d.rounded_rectangle((0, sh - 44, 130, sh), 14, fill=(60, 160, 60))
    d.text((65, sh - 22), "start", font=font(F_SANSB, 26), fill=WHITE, anchor="mm")
    reloj = "11:52 PM" if T < S("N16") else "3:12 AM"
    d.text((sw - 20, sh - 22), reloj, font=font(F_SANS, 24), fill=WHITE, anchor="rm")
    if T < S("N14"):
        ventana(d, 30, 24, sw - 60, sh - 90, "Inbox - cryptography@metzdowd.com")
        rows = [("Satoshi Nakamoto", "Bitcoin v0.1 released", "1/8/2009"), ("J. Smith", "Re: digital cash ideas", "1/7/2009"), ("Mailing list", "Weekly digest", "1/5/2009")]
        for i, (a, b, cc) in enumerate(rows):
            yy = 104 + i * 58; sel = i == 0 and T >= WT("N13", "bitcoin")
            if sel: d.rectangle((40, yy - 26, sw - 40, yy + 26), fill=(49, 106, 197))
            col = WHITE if sel else (20, 20, 30)
            d.text((60, yy), a, font=font(F_SANSB if i == 0 else F_SANS, 28), fill=col, anchor="lm")
            d.text((400, yy), b, font=font(F_SANSB if i == 0 else F_SANS, 28), fill=col, anchor="lm")
            d.text((sw - 60, yy), cc, font=font(F_SANS, 26), fill=col, anchor="rm")
        if T >= WT("N13", "bitcoin"):
            yb = 300; d.line((40, yb - 22, sw - 40, yb - 22), fill=(160, 160, 160), width=2)
            d.text((60, yb + 14), "From: Satoshi Nakamoto", font=font(F_SANSB, 30), fill=(20, 20, 30), anchor="lm")
            d.text((60, yb + 60), "Subject: Bitcoin v0.1 released", font=font(F_SANSB, 30), fill=(20, 20, 30), anchor="lm")
            d.text((60, yb + 130), "A new electronic cash system. No central server.", font=font(F_SANS, 30), fill=(40, 40, 50), anchor="lm")
            d.text((60, yb + 180), "Download: bitcoin-0.1.0.rar", font=font(F_SANS, 30), fill=(0, 70, 200), anchor="lm")
    else:
        ventana(d, 80, 30, sw - 160, sh - 100, "Bitcoin")
        d.text((100, 94), "File   Settings   Help", font=font(F_SANS, 26), fill=(20, 20, 30), anchor="lm")
        tg = WT("N14", "generate"); gen = T >= tg + .25
        d.rectangle((110, 124, 138, 152), fill=WHITE, outline=(20, 20, 30), width=2)
        if gen: d.line((114, 138, 123, 148, 136, 128), fill=(0, 140, 0), width=5)
        d.text((152, 138), "Generate Coins", font=font(F_SANSB, 30), fill=(20, 20, 30), anchor="lm")
        tf = WT("N14", "50"); bal = 50 if T >= tf else 0
        d.text((110, 204), "Balance:", font=font(F_SANS, 32), fill=(20, 20, 30), anchor="lm")
        d.text((265, 204), f"{bal:.2f}", font=font(F_SANSB, int(42 * popscale(T, tf) if T >= tf else 42)), fill=(0, 120, 0) if bal else (20, 20, 30), anchor="lm")
        d.text((110, 258), "Status: " + ("Generating..." if gen else "Idle"), font=font(F_SANS, 26), fill=(80, 80, 90), anchor="lm")
        d.rectangle((110, 296, sw - 110, sh - 90), fill=WHITE, outline=(150, 150, 160))
        if T >= tf:
            d.text((130, 330), "Date             Description        Credit", font=font(F_MONO, 24), fill=(80, 80, 90), anchor="lm")
            d.text((130, 372), "1/9/2009 23:58   Generated          +50.00", font=font(F_MONO, 24), fill=(20, 20, 30), anchor="lm")
        if tg - .4 <= T < tg + .6:
            u = ease((T - tg + .4) / .5); cx, cy = 400 - 270 * u, 330 - 190 * u
            d.polygon([(cx, cy), (cx, cy + 40), (cx + 10, cy + 31), (cx + 19, cy + 48), (cx + 26, cy + 44), (cx + 18, cy + 28), (cx + 31, cy + 28)], fill=WHITE, outline=(0, 0, 0))
        if T >= S("N16"):
            tm = WT("N16", "appears")
            if T >= tm:
                u = popscale(T, tm, .3); bw, bh = int(900 * u), int(330 * u)
                bx, by = sw // 2 - bw // 2, sh // 2 - bh // 2 - 20
                if bw > 40:
                    ventana(d, bx, by, bw, bh, "New message" if u > .7 else "")
                    if u > .9:
                        d.text((bx + 30, by + 84), "From: (unknown)", font=font(F_SANS, 28), fill=(110, 110, 120), anchor="lm")
                        msg = "I know where you came from."
                        t17 = S("N17"); n = int(len(msg) * clamp((T - t17 + .1) / max(.3, E("N17") - t17)))
                        d.text((bx + 30, by + 190), msg[:n] + ("|" if int(T * 3) % 2 and n < len(msg) else ""), font=font(F_SANSB, 52), fill=(150, 10, 10), anchor="lm")
    scan(sc, 20)
    if WT("N16", "flickers") <= T < WT("N16", "appears") + .2:
        g = int(T * 30)
        if g % 5 in (0, 1):
            arr = np.array(sc); sh_ = (g * 37) % 40 - 20
            for band in range(6):
                y1 = (g * 53 + band * 97) % sh; y2 = min(sh, y1 + 18)
                arr[y1:y2] = np.roll(arr[y1:y2], sh_ * (band + 1), axis=1)
            sc = Image.fromarray(arr)
    return sc

def sc_pc(T):
    c = Image.new("RGBA", (W, H), (8, 10, 20, 255))
    sx, sy, sw, sh = monitor(c, T, S("N13"))
    c.alpha_composite(pantalla_pc(T).resize((sw, sh), Image.LANCZOS), (sx, sy))
    return c

def sc_cara(T, nombre, t0, luz=True, latido=False):
    c = bg("bg_noche", T, t0, 1.35, 1.45, 5, .5, .5).filter(ImageFilter.GaussianBlur(6))
    pul = 1 + (.025 * max(0, math.sin(T * 2 * PI_ * 1.1)) ** 8 if latido else 0)
    put(c, nombre, W / 2, 760, 1.25 * pul)
    if luz:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.ellipse((W / 2 - 520, 250, W / 2 + 520, 1300), fill=CYAN + (60,))
        c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(80)))
    if latido: c.alpha_composite(VIG_HARD)
    return c

def sc_decidido(T):
    c = sc_cara(T, "heroe_decidido", S("N15"))
    stamp(c, T, WT("N15", "missing"), "NOT THIS TIME", 800, 300, ORG, -8, 64)
    return c

def sc_miedo(T):
    c = sc_cara(T, "heroe_miedo", S("N18"), True, True)
    if T >= WT("N18", "nobody"): etiqueta(c, T, WT("N18", "nobody"), "NOBODY KNOWS.", 220, 300, WHITE, OL, 32)
    if T >= WT("N18", "nobody", 2): etiqueta(c, T, WT("N18", "nobody", 2), "NOBODY CAN KNOW.", 850, 300, RED, WHITE, 32)
    return c

def sc_voto(T):
    s0 = S("N19")
    c = Image.new("RGBA", (W, H), (12, 10, 24, 255)); d = ImageDraw.Draw(c)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.ellipse((-300, 150, 600, 950), fill=(60, 140, 255, 60)); od.ellipse((480, 150, 1380, 950), fill=(255, 80, 80, 50))
    c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(110)))
    text(d, (W / 2, 150), "WHAT DO YOU DO?", 92 * popscale(T, s0), WHITE, stroke=8)
    ta, tb = WT("N19", "a"), WT("N19", "b")
    for (t, lab, sub, l2, cx, col) in ((ta, "A", "REPLY", "find out who knows\nyour secret", 280, (60, 140, 255)),
                                       (tb, "B", "DELETE IT", "keep mining like\nnothing happened", 800, (255, 90, 90))):
        if T < t: continue
        u = popscale(T, t); w, h = 470 * u, 540 * u
        panel(c, (cx - w / 2, 540 - h / 2, cx + w / 2, 540 + h / 2), (24, 22, 44), 245, 36, col, 8)
        if u > .6:
            d.ellipse((cx - 85, 330, cx + 85, 500), fill=col, outline=WHITE, width=6)
            text(d, (cx, 415), lab, 120, WHITE)
            text(d, (cx, 585), sub, 72, WHITE)
            d.multiline_text((cx, 690), l2, font=font(F_UI, 28), fill=GRIS, anchor="mm", align="center", spacing=8)
    tc = WT("N20", "comment")
    if T >= tc:
        u = popscale(T, tc)
        d.rounded_rectangle((W / 2 - 400 * u, 920 - 64 * u, W / 2 + 400 * u, 920 + 64 * u), 30, fill=YEL, outline=OL, width=6)
        if u > .6:
            text(d, (W / 2 - 30, 922), "COMMENT  A  OR  B", 66, OL)
            bob = 8 * math.sin(T * 6)
            d.polygon([(W / 2 + 300, 900 + bob), (W / 2 + 350, 900 + bob), (W / 2 + 325, 945 + bob)], fill=OL)
    return c

SCENES = [(0.0, sc_cold), (COLD, sc_hook), (S("N02") - .35, sc_alarma), (S("N03") - .1, sc_cuarto), (S("N04") - .15, sc_movil),
          (S("N05") - .2, sc_espejo), (S("N06") - .2, sc_salon_tv), (S("N07") - .25, sc_satoshi), (S("N09") - .2, sc_precio),
          (S("N10") - .2, sc_banco), (S("Y01") - .25, sc_papa), (S("N12") - .5, sc_noche), (S("N13") - .25, sc_pc),
          (S("N15") - .2, sc_decidido), (S("N16") - .3, sc_pc), (S("N18") - .2, sc_miedo), (S("N19") - .3, sc_voto)]

TW = .32

def hblur(im, k):
    if k <= 1: return im
    return im.resize((max(1, W // k), H), Image.BILINEAR).resize((W, H), Image.BILINEAR)

IMPACTS = [WT("N01", "2009") + .02, WT("N01", "2026"), WT("N04", "2009"), WT("N05", "19"), WT("N09", "hundred"), S("D02") + .35, S("N17")]

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
