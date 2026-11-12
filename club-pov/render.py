"""Monta el Ep.1 "Heredas un club de fútbol abandonado en la última división"."""
import json, math, os, re, subprocess, sys, wave
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from guion import LINEAS

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
LAY = os.path.join(HERE, "layers2"); VOZ = os.path.join(HERE, "voz"); TMP = os.path.join(HERE, "tmp")
os.makedirs(TMP, exist_ok=True)
F_ANTON = os.path.join(HERE, "fonts/Anton-Regular.ttf"); F_HAND = os.path.join(HERE, "fonts/Caveat.ttf")
F_UI = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
YEL = (255, 201, 60); RED = (255, 77, 77); WHITE = (255, 255, 255); OL = (27, 21, 48); PANEL = (22, 28, 50)

# ---------------------------------------------------------------- tiempos
def dur_audio(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                         capture_output=True, text=True).stdout.strip()
    return float(out)

GAP = {"L02": .35, "L05": .45, "L06": .45, "L07": .3, "L08": .45, "L11": .5, "L12": .5, "L13": .5, "L14": .35,
       "L15": .3, "L16": .55, "L17": .4}

def timeline():
    t, tl = 0.25, {}
    for lid, who, tts, cap in LINEAS:
        t += GAP.get(lid, .3) if tl else 0
        p = os.path.join(VOZ, lid + ".wav")
        d = dur_audio(p) if os.path.exists(p) else len(tts) / 14.5
        tl[lid] = (t, t + d)
        t += d
    return tl, t + 2.2

TL, TOTAL = timeline()
def S(l): return TL[l][0]
def E(l): return TL[l][1]

# ---------------------------------------------------------------- utilidades
def ease(u): u = max(0., min(1., u)); return 1 - (1 - u) ** 3
def back(u):
    u = max(0., min(1., u)); c = 1.7
    return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2
def clamp(u): return max(0., min(1., u))

@lru_cache(None)
def layer(name):
    return Image.open(os.path.join(LAY, name + ".png")).convert("RGBA")

@lru_cache(None)
def font(path, size): return ImageFont.truetype(path, max(1, int(size)))

@lru_cache(256)
def scaled(name, s):
    im = layer(name)
    return im.resize((max(1, int(im.width * s / 2)), max(1, int(im.height * s / 2))), Image.LANCZOS)

def put(canvas, name, cx, cy, s=1.0, alpha=1.0, rot=0):
    s = round(s, 3)
    im = scaled(name, s)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def bg(name, T, t0, zoom0=1.0, zoom1=1.08, dur=8, fx=0.5, fy=0.5):
    im = layer(name)
    z = zoom0 + (zoom1 - zoom0) * clamp((T - t0) / dur)
    w, h = 2 * W / z, 2 * H / z
    x0 = (2 * W - w) * fx; y0 = (2 * H - h) * fy
    return im.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + w, y0 + h), reducing_gap=2.0)

def text(d, xy, s, size, fill=WHITE, anchor="mm", f=F_ANTON, stroke=0, sfill=OL):
    d.text(xy, s, font=font(f, size), fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sfill)

def panel(canvas, box, fill=PANEL, alpha=235, rad=28, outline=None, ow=0):
    ov = Image.new("RGBA", canvas.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    d.rounded_rectangle(box, rad, fill=fill + (alpha,), outline=outline, width=ow)
    canvas.alpha_composite(ov)

def popscale(T, t0, d=.35): return back((T - t0) / d) if T >= t0 else 0

def vignette():
    y, x = np.mgrid[0:H, 0:W]
    r = np.sqrt(((x - W / 2) / (W * .75)) ** 2 + ((y - H / 2) / (H * .75)) ** 2)
    a = np.clip((r - .55) * 1.6, 0, .75) * 255
    v = np.zeros((H, W, 4), np.uint8); v[..., 3] = a.astype(np.uint8)
    return Image.fromarray(v, "RGBA")
VIG = vignette()

# ---------------------------------------------------------------- subtítulos
import difflib, unicodedata
def _norm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return "".join(c for c in w if c.isalnum())

def _whisper(lid):
    p = os.path.join(VOZ, lid + ".json")
    if not os.path.exists(p): return []
    raw = json.load(open(p, encoding="utf-8"))
    out = []
    for w in raw:   # une "182" + ".400" y similares
        if out and w["p"][:1] in ".,-" and any(ch.isdigit() for ch in w["p"]):
            out[-1] = {"p": out[-1]["p"] + w["p"], "inicio": out[-1]["inicio"], "fin": w["fin"]}
        else:
            out.append(dict(w))
    return out

def word_times(lid, words):
    """Tiempos (inicio, fin) absolutos para cada palabra del subtítulo, alineados con lo que dice la voz."""
    t0, t1 = TL[lid]
    ww = _whisper(lid)
    n = len(words)
    res = [None] * n
    if ww:
        A = [_norm(w.strip("*")) for w in words]; B = [_norm(w["p"]) for w in ww]
        sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "equal" or (op == "replace" and i2 - i1 == j2 - j1):
                for k in range(i2 - i1):
                    res[i1 + k] = (t0 + ww[j1 + k]["inicio"], t0 + ww[j1 + k]["fin"])
            elif op == "replace" and j2 > j1:
                s_, e_ = ww[j1]["inicio"], ww[j2 - 1]["fin"]
                L = sum(len(x) for x in A[i1:i2]) or 1; acc = 0
                for k in range(i1, i2):
                    a0 = s_ + (e_ - s_) * acc / L; acc += len(A[k]); res[k] = (t0 + a0, t0 + s_ + (e_ - s_) * acc / L)
    # rellena huecos interpolando
    for k in range(n):
        if res[k] is None:
            prev = next((res[j][1] for j in range(k - 1, -1, -1) if res[j]), t0)
            nxt = next((res[j][0] for j in range(k + 1, n) if res[j]), t1)
            gap = [j for j in range(k, n) if res[j] is None]
            run = [j for j in gap if all(res[m] is None for m in range(k, j + 1))]
            m = len(run); step = (nxt - prev) / (m or 1)
            for i, j in enumerate(run): res[j] = (prev + i * step, prev + (i + 1) * step)
    return res

def chunks():
    out = []
    for lid, who, tts, cap in LINEAS:
        words = cap.split()
        times = word_times(lid, words)
        groups, cur = [], []
        for i, w in enumerate(words):
            cur.append(i)
            if sum(len(words[x].strip("*")) + 1 for x in cur) >= 14 or w.rstrip("*").endswith((".", ",", ":", "?", "!")):
                groups.append(cur); cur = []
        if cur: groups.append(cur)
        for g in groups:
            out.append((times[g[0]][0], times[g[-1]][1], [(words[i].strip("*").upper(), times[i]) for i in g], who, lid))
    return out
CH = chunks()

def WT(lid, palabra, n=1):
    """Instante en que la voz dice `palabra` (n-ésima aparición) dentro de la línea lid."""
    cap = [x for x in LINEAS if x[0] == lid][0][3].split()
    tt = word_times(lid, cap); c = 0
    for w, (a, b) in zip(cap, tt):
        if _norm(w.strip("*")) == _norm(palabra):
            c += 1
            if c == n: return a
    raise KeyError(lid + palabra)
NOMBRE = {"P": "PACO", "A": "EL ABUELO (CARTA)", "R": "ARTURO"}

def draw_caption(canvas, T):
    for idx, (t0, t1, g, who, lid) in enumerate(CH):
        nxt0 = CH[idx + 1][0] if idx + 1 < len(CH) else 1e9
        hold = min(t1 + .35, nxt0) if CH[idx + 1 if idx + 1 < len(CH) else idx][4] == lid else t1 + .35
        if not (t0 - .04 <= T < max(hold, t1)):
            continue
        if T >= nxt0 - .04: continue
        d = ImageDraw.Draw(canvas)
        k = 0.85 + 0.15 * back((T - t0 + .04) / .14)
        f = font(F_ANTON, 96 * k)
        widths = [d.textlength(p + " ", font=f) for p, _ in g]
        total = sum(widths) - d.textlength(" ", font=f)
        sc = min(1.0, 820 / total)
        if sc < 1:
            f = font(F_ANTON, 96 * k * sc); widths = [d.textlength(p + " ", font=f) for p, _ in g]; total = sum(widths) - d.textlength(" ", font=f)
        x = W / 2 - total / 2; y = 1480
        starts = [ws for _, (ws, we) in g] + [1e9]
        for i_, ((p, (ws, we)), wd) in enumerate(zip(g, widths)):
            fin_ = min(starts[i_ + 1], we + .35) if i_ + 1 < len(g) else we + .35
            activa = ws - .03 <= T < fin_ - .03
            dicha = T >= ws - .03
            col = YEL if activa else (WHITE if dicha else (225, 225, 230))
            if activa:
                u = clamp((T - ws + .03) / .12); fa = font(F_ANTON, f.size * (1 + .06 * math.sin(u * PI_)))
                d.text((x + (wd - d.textlength(" ", font=f)) / 2, y), p, font=fa, fill=col, anchor="mm", stroke_width=10, stroke_fill=(10, 10, 20))
            else:
                d.text((x, y), p, font=f, fill=col, anchor="lm", stroke_width=9, stroke_fill=(10, 10, 20))
            x += wd
        if who in NOMBRE:
            tag = NOMBRE[who]; ft = font(F_UI, 30); tw = d.textlength(tag, font=ft)
            d.rounded_rectangle((W / 2 - tw / 2 - 18, 1385, W / 2 + tw / 2 + 18, 1431), 12, fill=YEL)
            d.text((W / 2, 1408), tag, font=ft, fill=OL, anchor="mm")
        return
PI_ = math.pi

# ---------------------------------------------------------------- HUD
F_LED = os.path.join(HERE, "fonts/Orbitron.ttf")
AMBER = (255, 176, 40)

@lru_cache(64)
def led_img(txt, size, col=AMBER, boost=0):
    f = ImageFont.truetype(F_LED, int(size))
    try: f.set_variation_by_axes([900])
    except Exception: pass
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    w = int(tmp.textlength(txt, font=f)) + 40; h = int(size * 1.5) + 20
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((w / 2, h / 2), txt, font=f, fill=col + (255,), anchor="mm")
    glow = im.filter(ImageFilter.GaussianBlur(7 + boost * 6))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for _ in range(2 + boost): out.alpha_composite(glow)
    out.alpha_composite(im)
    sl = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ds = ImageDraw.Draw(sl)
    for y in range(0, h, 4): ds.line((0, y, w, y), fill=(0, 0, 0, 70), width=1)
    out.alpha_composite(sl)
    return out

def hud_vals(T):
    caja = None if T < WT("L11", "312") else int(312 * ease((T - WT("L11", "312")) / .8))
    jug = None if T < WT("L08", "tres.") else 3
    dias = None if T < S("L04") + .25 else max(21, 30 - int((T - S("L04") - .25) / .1))
    return caja, jug, dias

EPISODIO, DIA, DIAS_TOTAL = 1, 1, 21

def coin(d, cx, cy, r):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(242, 190, 60), outline=(120, 80, 10), width=4)
    d.ellipse((cx - r * .62, cy - r * .62, cx + r * .62, cy + r * .62), outline=(196, 140, 30), width=3)
    d.text((cx, cy + 1), "€", font=font(F_UI, int(r * 1.1)), fill=(120, 80, 10), anchor="mm")

def ball(d, cx, cy, r):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(245, 245, 245), outline=OL, width=4)
    for (dx, dy) in ((0, -.45), (-.45, .2), (.45, .2), (0, .62)):
        x, y = cx + dx * r, cy + dy * r; q = r * .26
        d.polygon([(x - q, y - q * .3), (x, y - q), (x + q, y - q * .3), (x + q * .6, y + q * .8), (x - q * .6, y + q * .8)], fill=OL)

@lru_cache(1)
def hud_base():
    """Barra de la serie: EPISODIO · DÍA X DE 21 con barra de progreso hacia el primer partido."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x0, y0, x1, y1 = 40, 92, 1040, 262
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 10, x1, y1 + 12), 30, fill=(0, 0, 0, 140))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0, y0, x1, y1), 30, fill=(14, 18, 32, 228), outline=(255, 255, 255, 40), width=2)
    # chapa de episodio
    d.rounded_rectangle((x0 + 18, y0 + 18, x0 + 178, y0 + 74), 16, fill=YEL)
    d.text((x0 + 98, y0 + 46), f"EPISODIO {EPISODIO}", font=font(F_UI, 24), fill=OL, anchor="mm")
    # día
    d.text((x0 + 200, y0 + 47), f"DÍA {DIA}", font=font(F_ANTON, 56), fill=WHITE, anchor="lm")
    d.text((x0 + 340, y0 + 50), f"DE {DIAS_TOTAL}", font=font(F_ANTON, 34), fill=(150, 160, 185), anchor="lm")
    # barra de progreso: un tramo por día hasta el primer partido
    tx0, tx1, ty = x0 + 30, x1 - 110, y0 + 122
    n = DIAS_TOTAL; gap = 6; sw = (tx1 - tx0 - gap * (n - 1)) / n
    for i in range(n):
        xa = tx0 + i * (sw + gap)
        col = YEL if i < DIA else (52, 60, 84)
        d.rounded_rectangle((xa, ty - 9, xa + sw, ty + 9), 5, fill=col)
    ball(d, x1 - 70, ty, 26)
    return im

GRIS = (150, 160, 185)
def trofeo(d, cx, cy, s):
    d.polygon([(cx - 16*s, cy - 16*s), (cx + 16*s, cy - 16*s), (cx + 10*s, cy + 4*s), (cx - 10*s, cy + 4*s)], fill=(242, 190, 60), outline=(120, 80, 10))
    d.rectangle((cx - 3*s, cy + 4*s, cx + 3*s, cy + 12*s), fill=(242, 190, 60))
    d.rectangle((cx - 10*s, cy + 12*s, cx + 10*s, cy + 17*s), fill=(160, 110, 20))

def flecha(d, cx, cy, s):
    d.polygon([(cx - 14*s, cy - 12*s), (cx + 2*s, cy + 4*s), (cx - 4*s, cy + 10*s), (cx + 14*s, cy + 14*s), (cx + 10*s, cy - 4*s), (cx + 4*s, cy + 2*s), (cx - 10*s, cy - 16*s)], fill=(255, 90, 80))

def euros(v): return f"{v:,}".replace(",", ".") + " €"

@lru_cache(1)
def barra_base():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x0, y0, x1, y1 = 36, 168, 1044, 278
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 8, x1, y1 + 10), 26, fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0, y0, x1, y1), 26, fill=(12, 16, 30, 200), outline=(255, 255, 255, 35), width=2)
    d.rounded_rectangle((x0 + 14, y0 + 12, x0 + 118, y0 + 56), 12, fill=YEL)
    d.text((x0 + 66, y0 + 34), f"EP.{EPISODIO}", font=font(F_ANTON, 32), fill=OL, anchor="mm")
    d.text((x0 + 132, y0 + 35), f"DÍA {DIA}", font=font(F_ANTON, 40), fill=WHITE, anchor="lm")
    d.line((x0 + 16, y0 + 64, x1 - 16, y0 + 64), fill=(255, 255, 255, 30), width=2)
    d.text((x0 + 18, y0 + 87), "OBJETIVO", font=font(F_UI, 20), fill=YEL, anchor="lm")
    return im

def draw_hud(canvas, T):
    if T >= S("L16") - .1: return
    canvas.alpha_composite(barra_base())
    d = ImageDraw.Draw(canvas)
    x0, y0, x1 = 36, 168, 1044
    t_deuda, t_caja, t_jug, t_obj = WT("L03", "182.400"), WT("L11", "312"), WT("L08", "tres."), WT("L04", "11")
    def pop(t): return 1 + .28 * math.sin(clamp((T - t) / .3) * math.pi) if 0 <= T - t < .3 else 1
    jug = "?" if T < t_jug else "3/11"
    caja = "?" if T < t_caja else euros(int(312 * ease((T - t_caja) / .8)))
    deuda = "?" if T < t_deuda else "-" + euros(int(182400 * ease((T - t_deuda) / .9)))
    items = [("jug", jug, t_jug, x0 + 312), ("caja", caja, t_caja, x0 + 440), ("deuda", deuda, t_deuda, x0 + 615), ("liga", "-", 1e9, x0 + 900)]
    for k, v, t, x in items:
        cy = y0 + 34
        if k == "jug": shirt(d, x, cy, .32, (220, 60, 50) if v != "?" else (70, 78, 100), WHITE)
        if k == "caja": coin(d, x, cy, 15)
        if k == "deuda": flecha(d, x, cy, 1.0)
        if k == "liga": trofeo(d, x, cy, 1.0)
        col = GRIS if v in ("?", "-") else ((255, 120, 110) if k == "deuda" else WHITE)
        d.text((x + 24, y0 + 35), v, font=font(F_ANTON, 34 * pop(t)), fill=col, anchor="lm")
    if T < t_obj:
        obj, prog, ptxt = "Salvar el club", 0, ""
    else:
        n = 3 if T >= t_jug else 0
        obj, prog, ptxt = "Fichar 11 jugadores", n / 11, f"{n}/11"
    d.text((x0 + 132, y0 + 87), obj, font=font(F_UI, 24), fill=WHITE, anchor="lm")
    bx0, bx1 = x0 + 640, x1 - 110
    d.rounded_rectangle((bx0, y0 + 80, bx1, y0 + 94), 7, fill=(52, 60, 84))
    if prog > 0:
        pv = prog * ease((T - t_jug) / .6)
        d.rounded_rectangle((bx0, y0 + 80, bx0 + (bx1 - bx0) * pv, y0 + 94), 7, fill=YEL)
    if ptxt: d.text((x1 - 20, y0 + 87), ptxt, font=font(F_ANTON, 28 * pop(t_jug)), fill=WHITE, anchor="rm")

def stamp(canvas, T, t0, label, cx, cy, col=RED, rot=-12, size=120):
    if T < t0: return
    u = clamp((T - t0) / .18); k = 1.8 - .8 * ease(u)
    im = Image.new("RGBA", (900, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = font(F_ANTON, size); tw = d.textlength(label, font=f)
    d.rounded_rectangle((450 - tw / 2 - 30, 60, 450 + tw / 2 + 30, 240), 18, outline=col, width=14)
    d.text((450, 152), label, font=f, fill=col, anchor="mm")
    im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    im = im.resize((int(im.width * k), int(im.height * k)), Image.BILINEAR)
    if u < 1: im.putalpha(im.getchannel("A").point(lambda v: int(v * u)))
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def sc_notaria(T):
    c = bg("bg_notaria", T, 0, 1.12, 1.0, 5).convert("RGBA")
    u = ease((T - .1) / .9)
    put(c, "manos", 540, 960 + 400 * (1 - u))
    th = WT("L01", "testamento,")
    if T >= th - .1:
        hl = highlight_img(clamp((T - th + .1) / .9))
        c.alpha_composite(hl, (540 - hl.width // 2, 905 - hl.height // 2))
    return c

def highlight_img(u):
    im = Image.new("RGBA", (560, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 34, 10 + 540 * ease(u), 90), 10, fill=(255, 214, 60, 150))
    d.text((24, 62), "Lego a mi nieto el C.D. San Lorenzo", font=font(F_HAND, 44), fill=(25, 35, 90, 255), anchor="lm")
    return im.rotate(6, resample=Image.BICUBIC, expand=True)

def crest(d, cx, cy, s):
    pts = [(cx - 170 * s, cy - 200 * s), (cx + 170 * s, cy - 200 * s), (cx + 170 * s, cy + 40 * s), (cx, cy + 230 * s), (cx - 170 * s, cy + 40 * s)]
    d.polygon(pts, fill=(30, 90, 168), outline=OL, width=int(12 * s))
    d.polygon([(cx - 170 * s, cy - 60 * s), (cx + 170 * s, cy - 60 * s), (cx + 170 * s, cy + 10 * s), (cx - 170 * s, cy + 10 * s)], fill=WHITE)
    text(d, (cx, cy - 130 * s), "C.D.", 70 * s, WHITE)
    text(d, (cx, cy - 25 * s), "SAN LORENZO", 52 * s, (30, 90, 168))
    text(d, (cx, cy + 90 * s), "1931", 60 * s, YEL)

def sc_club(T):
    c = bg("bg_dark", T, S("L02"), 1.0, 1.06, 6).convert("RGBA"); d = ImageDraw.Draw(c)
    t0c = WT("L01", "Un")
    s = popscale(T, t0c, .35)
    if s > 0:
        put(c, "escudo", 540, 690, 1.05 * max(s, .02), rot=3 * math.sin(T * 1.3))
        stamp(c, T, t0c + .55, "HEREDADO", 540, 640, RED, -14, 110)
    d = ImageDraw.Draw(c)
    t1 = WT("L02", "Última")
    if T >= t1:
        u = popscale(T, t1)
        d.rounded_rectangle((540 - 260 * u, 1080, 540 + 260 * u, 1170), 16, fill=RED)
        if u > .5: text(d, (540, 1125), "ÚLTIMA DIVISIÓN", 58, WHITE)
    return c

def sc_stats(T):
    c = bg("bg_dark", T, S("L03"), 1.04, 1.0, 10).convert("RGBA"); d = ImageDraw.Draw(c)
    s0, e0 = TL["L03"]; L = e0 - s0
    items = [(s0 + .1, "DEUDA HEREDADA", -182400, "€", RED), (WT("L03", "43"), "PARTIDOS SEGUIDOS SIN GANAR", 43, "", WHITE),
             (WT("L03", "cero"), "AFICIONADOS EN EL ÚLTIMO PARTIDO", 0, "", YEL)]
    for i, (t, lab, val, suf, col) in enumerate(items):
        if T < t: continue
        y = 430 + i * 270
        a = ease((T - t) / .3)
        panel(c, (90 + 60 * (1 - a), y - 110, 990 - 60 * (1 - a), y + 120), alpha=int(230 * a))
        d = ImageDraw.Draw(c)
        text(d, (540, y - 62), lab, 32, (180, 186, 210), "mm", F_UI)
        cnt = val * ease((T - t) / .9)
        num = (f"-{abs(int(cnt)):,}".replace(",", ".") + " €") if val < 0 else str(int(round(cnt)))
        text(d, (540, y + 32), num, 118, col)
    return c

def shirt(d, cx, cy, s, fill, outline):
    p = [(-38, -40), (-14, -46), (0, -36), (14, -46), (38, -40), (54, -14), (36, -4), (34, 46), (-34, 46), (-36, -4), (-54, -14)]
    d.polygon([(cx + x * s, cy + y * s) for x, y in p], fill=fill, outline=outline, width=max(2, int(4 * s)))

def sc_ultimatum(T):
    s0, e0 = TL["L04"]
    c = bg("bg_dark", T, s0, 1.0, 1.05, 6).convert("RGBA"); d = ImageDraw.Draw(c)
    n = max(21, 30 - int(max(0, T - s0 - .25) / .1))
    flip = ((T - s0 - .25) % .1) / .1 if n > 21 else 1
    cx, cy, w, h = 540, 620, 420, 470
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((cx - w/2 + 10, cy - h/2 + 24, cx + w/2 + 10, cy + h/2 + 24), 26, fill=(0, 0, 0, 160))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16))); d = ImageDraw.Draw(c)
    d.rounded_rectangle((cx - w/2, cy - h/2, cx + w/2, cy + h/2), 26, fill=(246, 242, 232), outline=OL, width=8)
    d.rounded_rectangle((cx - w/2, cy - h/2, cx + w/2, cy - h/2 + 110), 26, fill=(200, 45, 45), outline=OL, width=8)
    d.rectangle((cx - w/2 + 8, cy - h/2 + 80, cx + w/2 - 8, cy - h/2 + 104), fill=(200, 45, 45))
    for k in (-110, 0, 110):
        d.ellipse((cx + k - 16, cy - h/2 - 26, cx + k + 16, cy - h/2 + 6), fill=(60, 64, 74), outline=OL, width=5)
    text(d, (cx, cy - h/2 + 56), "QUEDAN", 56, WHITE)
    text(d, (cx, cy + 40), str(n), 240, OL)
    text(d, (cx, cy + 190), "DÍAS", 54, (120, 110, 100))
    if n > 21:   # hoja que cae
        hh = int((h - 120) * (1 - flip))
        if hh > 4:
            d.rectangle((cx - w/2 + 8, cy - h/2 + 112, cx + w/2 - 8, cy - h/2 + 112 + hh), fill=(236, 230, 216), outline=(180, 170, 150))
    tj = WT("L04", "11") if True else None
    if T >= tj:
        u = ease((T - tj) / .5)
        text(d, (540, 1000), "JUGADORES CON FICHA", 40, (190, 196, 215), "mm", F_UI)
        for i in range(11):
            a_ = clamp((T - tj - i * .04) / .2)
            if a_ <= 0: continue
            row, col_ = (0, i) if i < 6 else (1, i - 6)
            x = 540 + (col_ - (2.5 if row == 0 else 2)) * 128; y = 1090 + row * 110
            red = T >= WT("L04", "desaparece.")
            shirt(d, x, y, .9 * (0.6 + .4 * back(a_)), None, (255, 80, 60) if red else (120, 128, 150))
        text(d, (540, 1300), "0 / 11", 64, (255, 80, 60) if T >= WT("L04", "desaparece.") else WHITE)
    return c

def sc_campo(T):
    s0, e0 = TL["L05"]; L = e0 - s0
    z = 1.10 - 0.10 * clamp((T - s0) / (L + .5))
    c = bg("bg_campo", T, s0, 1.10, 1.0, L + .5, .5, .45).convert("RGBA")
    def scr(px, py): return z * px - (z * W - W) * .5, z * py - (z * H - H) * .45
    tg = WT("L05", "cabra")
    if T >= tg:
        k = popscale(T, tg, .45)
        hop = 40 * abs(math.sin((T - tg) * 4)) * math.exp(-(T - tg) * 1.5)
        put(c, "cabra", 560, 1290 - hop, 1.0 * max(k, .02))
    c.alpha_composite(scaled("hierba", 1.0), (0, int(60 * (1 - ease((T - s0) / 2.5)))))
    d = ImageDraw.Draw(c)
    if WT("L05", "porterías") <= T < tg:  # porterías
        u = popscale(T, WT("L05", "porterías"))
        for gx in (180, 900):
            cx, cy = scr(gx, 1300)
            rx, ry = 165 * z * u, 120 * z * u
            d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=(10, 10, 20), width=16)
            d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=RED, width=10)
    if T >= tg + .5:
        u = popscale(T, tg + .5)
        d.rounded_rectangle((190, 880, 890, 960), 14, fill=YEL)
        if u > .5: text(d, (540, 920), "CAPITANA DEL EQUIPO (DE MOMENTO)", 34, OL, "mm", F_UI)
    return c

def ficha(c, T, t0, x, y, nombre, l1, l2, col=YEL):
    if T < t0: return
    u = ease((T - t0) / .35); d = ImageDraw.Draw(c)
    xx = x - 80 * (1 - u)
    panel(c, (xx, y, xx + 470, y + 170), fill=(250, 246, 235), alpha=int(250 * u), rad=18, outline=OL, ow=6)
    d = ImageDraw.Draw(c)
    if u > .3:
        text(d, (xx + 28, y + 48), nombre, 54, OL, "lm")
        text(d, (xx + 28, y + 102), l1, 26, (90, 80, 100), "lm", F_UI)
        text(d, (xx + 28, y + 138), l2, 26, (200, 50, 50), "lm", F_UI)

def dust(c, T, n=45):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    r = np.random.default_rng(5)
    for i in range(n):
        x0, y0, sp, ph = r.uniform(200, 880), r.uniform(150, 1300), r.uniform(8, 25), r.uniform(0, 6.28)
        x = x0 + 30 * math.sin(T * .6 + ph); y = (y0 - T * sp) % 1250 + 150
        a = int(90 + 80 * math.sin(T * 2 + ph)); rr = 2 + (i % 3)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 236, 190, max(0, a)))
    c.alpha_composite(ov)

def sc_paco(T):
    s0 = S("L06"); e7 = E("L07")
    c = bg("bg_vestuario", T, s0, 1.0, 1.08, e7 - s0).convert("RGBA")
    tp = s0 + (E("L06") - s0) * .18
    if T >= tp:
        u = ease((T - tp) / .5)
        bob = 6 * math.sin((T - tp) * 2.2)
        talk = 8 * abs(math.sin(T * 11)) if S("L07") <= T < E("L07") else 0
        px, py = 540 + 600 * (1 - u), 1320 + bob - talk
        put(c, "paco", px, py, 1.0)
        d = ImageDraw.Draw(c); ox, oy = px - 400, py - 700
        if (T % 3.3) < .13:
            for ex in (350, 450):
                d.ellipse((ox + ex - 19, oy + 436 - 17, ox + ex + 19, oy + 436 + 17), fill=(243, 194, 155))
                d.line((ox + ex - 17, oy + 438, ox + ex + 17, oy + 438), fill=OL, width=4)
        if S("L07") <= T < E("L07"):
            m = 6 + 14 * abs(math.sin(T * 13))
            d.ellipse((ox + 378, oy + 566 - 2, ox + 422, oy + 566 + m), fill=(120, 30, 40), outline=OL, width=4)
    dust(c, T)
    ficha(c, T, s0 + (E("L06") - s0) * .3, 60, 520, "PACO", "UTILLERO DESDE 1985", "9 MESES SIN COBRAR")
    return c

def slot_grid(c, T, t0, filled):
    d = ImageDraw.Draw(c)
    x0, y0, cs, gp = 140, 360, 120, 14
    text(d, (540, 300), "PLANTILLA", 60, WHITE)
    for i in range(18):
        r, k = divmod(i, 6)
        x, y = x0 + k * (cs + gp), y0 + r * (cs + gp)
        a = clamp((T - t0 - i * .04) / .2)
        if a <= 0: continue
        if i < filled:
            d.rounded_rectangle((x, y, x + cs, y + cs), 16, fill=WHITE)
            text(d, (x + cs / 2, y + cs / 2), str(i + 1), 70, OL)
        else:
            d.rounded_rectangle((x, y, x + cs, y + cs), 16, outline=(90, 100, 140), width=5)
    if T >= t0 + .9: text(d, (540, y0 + 3 * (cs + gp) + 40), f"{filled} DE 18", 54, RED)

def sc_plantilla(T):
    s8, e10 = S("L08"), E("L10")
    c = bg("bg_dark", T, s8, 1.0, 1.04, e10 - s8).convert("RGBA")
    s9, e9 = TL["L09"]; L9 = e9 - s9
    if T < s9:
        slot_grid(c, T, s8 + .1, 3 if T >= WT("L08", "tres.") else 0)
        return c
    if T < E("L09") + .15:
        slot_grid(c, T, -99, 3)
        cards = [("ramon", "RAMÓN", "44 AÑOS · PORTERO", "RODILLA DE TITANIO", s9),
                 ("josito", "JOSITO", "17 AÑOS", "NUNCA HA JUGADO", WT("L09", "Josito:")),
                 ("primo", "EL PRIMO", "¿PRIMO DE QUIÉN?", "NADIE LO SABE", WT("L09", "el"))]
        for i, (lay, nm, a1, a2, t) in enumerate(cards):
            if T < t: continue
            nxt = cards[i + 1][4] if i < 2 else 1e9
            focus = T < nxt
            x = 200 + i * 340 if not focus else 540
            yy = 1000
            if focus:
                k = popscale(T, t, .4)
                panel(c, (140, 870, 940, 1250), fill=(250, 246, 235), alpha=250, rad=26, outline=OL, ow=6)
                put(c, lay, 360, 1060, .78 * max(k, .02))
                d = ImageDraw.Draw(c)
                text(d, (560, 960), nm, 76, OL, "lm")
                text(d, (560, 1040), a1, 30, (90, 80, 100), "lm", F_UI)
                text(d, (560, 1090), a2, 30, (200, 50, 50), "lm", F_UI)
        return c
    # L10: menos de 7
    d = ImageDraw.Draw(c)
    k = popscale(T, E("L09") + .15, .4)
    text(d, (540, 650), "MENOS DE 7", 150 * max(k, .01), WHITE, stroke=8)
    if k > .6: text(d, (540, 820), "= NO HAY PARTIDO", 80, RED, stroke=6)
    if T > WT("L10", "Ni"):
        x = 540
        for i in range(3):
            put(c, ["ramon", "josito", "primo"][i], 300 + i * 240, 1050, .45)
    return c

def sc_caja(T):
    s0, e0 = TL["L11"]; L = e0 - s0
    zt = WT("L11", "sobre")
    z = 1.0 + 0.9 * ease((T - zt) / 1.2) if T > zt else 1.0
    c = bg("bg_dark", T, s0, 1.0, 1.0, 1).convert("RGBA")
    u = ease((T - s0) / .5)
    k = (z - 1) / .9
    put(c, "caja", 540 - k * (380 - 540) * z, 900 + 100 * (1 - u) - k * (850 - 550) * z, 1.0 * z)
    d = ImageDraw.Draw(c)
    if T >= WT("L11", "312") and T < zt:
        k = popscale(T, WT("L11", "312"))
        d.rounded_rectangle((330, 400, 750, 500), 16, fill=(40, 120, 70))
        if k > .5: text(d, (540, 450), "312 €", 80, WHITE)
    if T >= WT("L11", "bocadillo") and T < zt:
        k = popscale(T, WT("L11", "bocadillo"))
        d.rounded_rectangle((560, 1240, 920, 1310), 12, fill=YEL)
        if k > .5: text(d, (740, 1275), "CADUCADO EN 2019", 30, OL, "mm", F_UI)
    if T >= zt + .9:
        text(d, (540, 1250), "PARA CUANDO ESTÉS AQUÍ", 76, YEL, stroke=8)
    return c

HAND = ["Si lees esto, te van a ofrecer", "dinero por el campo.", "No lo vendas.", "Debajo del vestuario", "está la razón por la que", "este club nunca", "debe morir.", "", "         — Tu abuelo"]
def sc_carta(T):
    s0, e0 = TL["L12"]; L = e0 - s0
    tb = WT("L12", "Debajo") - .2
    if T >= tb + .2 and T < e0 + .3:
        z = 1.0 + .25 * clamp((T - tb) / (e0 - tb))
        c = bg("baldosas", T, tb, 1.0 + .0, 1.25, e0 - tb).convert("RGBA")
        glow = .5 + .5 * math.sin(T * 5)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        d.ellipse((380, 900, 700, 1260), fill=(255, 201, 60, int(60 + 50 * glow)))
        ov = ov.filter(ImageFilter.GaussianBlur(40)); c.alpha_composite(ov)
        d = ImageDraw.Draw(c)
        text(d, (540, 560), "¿QUÉ HAY AQUÍ DEBAJO?", 72, WHITE, stroke=8)
        return c
    c = bg("bg_dark", T, s0, 1.0, 1.0, 1).convert("RGBA")
    put(c, "carta", 540, 880, 1.0)
    d = ImageDraw.Draw(c)
    nchar = int(clamp((T - s0) / (tb - s0 + 1.2)) * sum(len(l) for l in HAND))
    for i, l in enumerate(HAND):
        if nchar <= 0: break
        part = l[:nchar]; nchar -= len(l)
        text(d, (230, 540 + i * 70), part, 66, (30, 40, 90), "ls", F_HAND)
    put(c, "abuelo_foto", 880, 1260, .42, rot=8)
    return c

def sc_coche(T):
    s0, e0 = TL["L13"]
    c = bg("bg_puerta", T, s0, 1.0, 1.05, 4).convert("RGBA")
    u = ease((T - s0 - .2) / 1.4)
    put(c, "coche", 540 + 900 * (1 - u), 1170, 1.0)
    return c

def sc_arturo(T):
    s0 = S("L14"); e15 = E("L15")
    c = bg("bg_puerta", T, s0, 1.5, 1.56, e15 - s0, .5, 1.0).convert("RGBA")
    c.alpha_composite(Image.new("RGBA", (W, H), (10, 10, 20, 110)))
    u = ease((T - s0) / .5)
    talk = 6 * abs(math.sin(T * 10)) if S("L14") <= T < E("L14") else 0
    put(c, "arturo", 540, 720 + 300 * (1 - u) - talk + 3 * math.sin(T * 1.8), 1.0)
    put(c, "coche", 540, 1050, 1.0)
    d = ImageDraw.Draw(c)
    if T < E("L14") + .2:
        k = popscale(T, s0 + .1, .4)
        d.rounded_rectangle((200, 280, 880, 430), 20, fill=(40, 120, 70), outline=OL, width=6)
        if k > .5:
            text(d, (540, 355), "250.000 €", 120 * min(1.1, k), WHITE, stroke=6)
        if T >= WT("L14", "pisos."):
            stamp(c, T, WT("L14", "pisos."), "PISOS DE LUJO", 540, 520, YEL, 6, 80)
    else:
        ficha(c, T, S("L15"), 50, 280, "ARTURO FERRÁN", "PRESIDENTE · ATLÉTICO VALLE", "EL QUE ARRUINÓ A TU ABUELO")
        tr = WT("L15", "presidente")
        if T >= tr:
            k = popscale(T, tr)
            d = ImageDraw.Draw(c)
            d.rounded_rectangle((620, 470, 1000, 540), 12, fill=RED)
            if k > .5: text(d, (810, 505), "RIVAL", 50, WHITE)
    return c

def option(c, T, t0, x, letter, lines, col, hi):
    k = popscale(T, t0, .4)
    if k <= 0: return
    w, h = 440, 640
    y = 760
    sc_ = 1.0 + (.06 if hi else 0)
    box = (x - w / 2 * sc_, y - h / 2 * sc_ + 60 * (1 - k), x + w / 2 * sc_, y + h / 2 * sc_ + 60 * (1 - k))
    panel(c, box, fill=col, alpha=255, rad=30, outline=YEL if hi else None, ow=10)
    d = ImageDraw.Draw(c)
    d.ellipse((x - 60, box[1] + 40, x + 60, box[1] + 160), fill=OL)
    text(d, (x, box[1] + 100), letter, 90, WHITE)
    for i, (l, cc) in enumerate(lines):
        text(d, (x, box[1] + 230 + i * 58), l, 36, cc, "mm", F_UI)

def sc_decision(T):
    s0, e0 = TL["L16"]; L = e0 - s0
    c = bg("bg_dark", T, s0, 1.0, 1.04, 10).convert("RGBA"); d = ImageDraw.Draw(c)
    k = popscale(T, s0, .4)
    beat = 1 + .05 * max(0, math.sin(T * 7.5)) ** 8
    text(d, (540, 250), "¿QUÉ HARÍAS TÚ?", 110 * max(k, .01) * beat, YEL, stroke=8)
    ta, tb = WT("L16", "A:"), WT("L16", "B:")
    hiA = ta <= T < tb; hiB = tb <= T < e0
    option(c, T, ta, 290, "A", [("VENDES EL", (40, 40, 60)), ("TERRENO", (40, 40, 60)), ("", OL), ("+68.000 €", (30, 130, 70)),
                                 ("pero derriban", (200, 50, 50)), ("el campo", (200, 50, 50))], (248, 246, 240), hiA)
    option(c, T, tb, 790, "B", [("ROMPES EL", OL), ("CONTRATO", OL), ("", OL), ("312 €", OL), ("3 jugadores", OL), ("21 días", OL)],
           YEL, hiB)
    if T >= S("L17"):
        u = popscale(T, WT("L17", "Comenta"))
        if u > 0:
            d = ImageDraw.Draw(c)
            d.rounded_rectangle((540 - 300 * u, 1120, 540 + 300 * u, 1210), 45, fill=WHITE)
            if u > .5: text(d, (540, 1165), "COMENTA  A  o  B", 56, OL)
    return c

SCENES = [  # (inicio, función)
    (0, sc_notaria), (WT("L01", "Un") - .12, sc_club), (S("L03") - .15, sc_stats), (S("L04") - .15, sc_ultimatum),
    (S("L05") - .2, sc_campo), (S("L06") - .2, sc_paco), (S("L08") - .2, sc_plantilla), (S("L11") - .2, sc_caja),
    (S("L12") - .2, sc_carta), (S("L13") - .2, sc_coche), (S("L14") - .15, sc_arturo), (S("L16") - .25, sc_decision),
]

def hblur(im, k):
    if k < 2: return im
    return im.resize((max(1, W // k), H), Image.BILINEAR).resize((W, H), Image.BILINEAR)

IMPACTS = []
def _impacts():
    global IMPACTS
    IMPACTS = [WT("L01", "Un"), WT("L01", "Un") + .55, S("L04") + .05, E("L09") + .15, WT("L14", "pisos."), S("L16")]
_impacts()

@lru_cache(1)
def grains():
    rng = np.random.default_rng(3); out = []
    for _ in range(4):
        n = rng.integers(0, 255, (H // 2, W // 2), dtype=np.uint8)
        a = np.zeros((H // 2, W // 2, 4), np.uint8); a[..., 0] = a[..., 1] = a[..., 2] = n; a[..., 3] = 9
        out.append(Image.fromarray(a, "RGBA").resize((W, H), Image.NEAREST))
    return out

TW = .32
def frame(T):
    idx = max(i for i, (t, f) in enumerate(SCENES) if T >= t)
    t0, fn = SCENES[idx]
    c = fn(T)
    u = (T - t0) / TW
    if idx > 0 and u < 1:   # whip-pan: la escena anterior sale por la izquierda y entra la nueva
        e = ease(u); prev = SCENES[idx - 1][1](T)
        k = int(2 + 22 * math.sin(math.pi * u))
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        canvas.alpha_composite(hblur(prev, k), (int(-W * e), 0))
        canvas.alpha_composite(hblur(c, k), (int(W * (1 - e)), 0))
        c = canvas
    amp = sum(16 * math.exp(-(T - ti) * 7) for ti in IMPACTS if 0 <= T - ti < .7)
    if amp > .6:
        z = 1.04; cc = c.resize((int(W * z), int(H * z)), Image.BILINEAR)
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
                          "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp],
                         stdin=subprocess.PIPE)
    for f in range(f0, f1):
        p.stdin.write(frame(f / FPS).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0: os.replace(tmp, out)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "still":
        for t in sys.argv[2:]:
            frame(float(t)).save(os.path.join(TMP, f"f_{float(t):06.2f}.jpg"), quality=90)
    elif cmd == "info":
        print(json.dumps({k: [round(a, 2), round(b, 2)] for k, (a, b) in TL.items()}), TOTAL)
    elif cmd == "scenes":
        from multiprocessing import Pool
        ids = [int(x) for x in sys.argv[2:]] or list(range(len(SCENES)))
        with Pool(2) as pool:
            pool.starmap(render_scene, [(i, os.path.join(TMP, f"s{i:02d}.mp4")) for i in ids])
