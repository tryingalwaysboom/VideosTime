"""Monta el Ep.1 "Heredas el taller de tuning abandonado de tu tío".
Sin voces: los tiempos se estiman por longitud de texto. Cuando existan voz/T01.wav… (+ .json de whisper) se usan los reales."""
import json, math, os, subprocess, sys, difflib, unicodedata
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from guion import LINEAS

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
LAY = os.path.join(HERE, "layers"); VOZ = os.path.join(HERE, "voz"); TMP = os.path.join(HERE, "tmp")
os.makedirs(TMP, exist_ok=True)
F_ANTON = os.path.join(HERE, "fonts/Anton-Regular.ttf"); F_HAND = os.path.join(HERE, "fonts/Caveat.ttf")
F_UI = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
YEL = (255, 201, 60); RED = (255, 77, 77); WHITE = (255, 255, 255); OL = (27, 21, 48); PANEL = (22, 20, 40)
CYAN = (62, 240, 255); MAG = (255, 79, 216); GRIS = (150, 160, 185); GREEN = (40, 150, 90)

# ---------------------------------------------------------------- tiempos
def dur_audio(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                         capture_output=True, text=True).stdout.strip()
    return float(out)

GAP = {"T02": .35, "T05": .45, "T06": .45, "T07": .3, "T08": .45, "T11": .5, "T13": .45, "T14": .5, "T15": .5,
       "T16": .35, "T17": .3, "T18": .55, "T19": .4}

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
PI_ = math.pi

@lru_cache(None)
def layer(name): return Image.open(os.path.join(LAY, name + ".png")).convert("RGBA")

@lru_cache(None)
def font(path, size): return ImageFont.truetype(path, max(1, int(size)))

@lru_cache(256)
def scaled(name, s):
    im = layer(name)
    return im.resize((max(1, int(im.width * s / 2)), max(1, int(im.height * s / 2))), Image.LANCZOS)

def put(canvas, name, cx, cy, s=1.0, alpha=1.0, rot=0):
    s = round(s, 3); im = scaled(name, s)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def bg(name, T, t0, zoom0=1.0, zoom1=1.08, dur=8, fx=0.5, fy=0.5):
    im = layer(name)
    z = zoom0 + (zoom1 - zoom0) * clamp((T - t0) / dur)
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
def dark(c, a): c.alpha_composite(Image.new("RGBA", (W, H), (8, 6, 18, int(a))))

def vignette():
    y, x = np.mgrid[0:H, 0:W]
    r = np.sqrt(((x - W / 2) / (W * .75)) ** 2 + ((y - H / 2) / (H * .75)) ** 2)
    a = np.clip((r - .55) * 1.6, 0, .75) * 255
    v = np.zeros((H, W, 4), np.uint8); v[..., 3] = a.astype(np.uint8)
    return Image.fromarray(v, "RGBA")
VIG = vignette()

def euros(v): return f"{v:,}".replace(",", ".") + " €"

# ---------------------------------------------------------------- subtítulos (palabra a palabra)
def _norm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return "".join(c for c in w if c.isalnum())

def _whisper(lid):
    p = os.path.join(VOZ, lid + ".json")
    if not os.path.exists(p): return []
    raw = json.load(open(p, encoding="utf-8")); out = []
    for w in raw:
        if out and w["p"][:1] in ".,-" and any(ch.isdigit() for ch in w["p"]):
            out[-1] = {"p": out[-1]["p"] + w["p"], "inicio": out[-1]["inicio"], "fin": w["fin"]}
        else: out.append(dict(w))
    return out

def word_times(lid, words):
    t0, t1 = TL[lid]; ww = _whisper(lid); n = len(words); res = [None] * n
    if ww:
        A = [_norm(w.strip("*")) for w in words]; B = [_norm(w["p"]) for w in ww]
        for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
            if op == "equal" or (op == "replace" and i2 - i1 == j2 - j1):
                for k in range(i2 - i1): res[i1 + k] = (t0 + ww[j1 + k]["inicio"], t0 + ww[j1 + k]["fin"])
            elif op == "replace" and j2 > j1:
                s_, e_ = ww[j1]["inicio"], ww[j2 - 1]["fin"]; L = sum(len(x) for x in A[i1:i2]) or 1; acc = 0
                for k in range(i1, i2):
                    a0 = s_ + (e_ - s_) * acc / L; acc += len(A[k]); res[k] = (t0 + a0, t0 + s_ + (e_ - s_) * acc / L)
    if all(r is None for r in res):   # sin voz: reparto por longitud de palabra (+ pausa en signos)
        wts = [len(w.strip("*")) + 1 + (3 if w.rstrip("*")[-1:] in ".,:?!" else 0) for w in words]
        tot = sum(wts); acc = 0
        for k in range(n):
            a = t0 + (t1 - t0) * acc / tot; acc += wts[k]; res[k] = (a, t0 + (t1 - t0) * (acc - (3 if wts[k] > len(words[k]) + 1 else 0)) / tot)
        return res
    for k in range(n):
        if res[k] is None:
            prev = next((res[j][1] for j in range(k - 1, -1, -1) if res[j]), t0)
            nxt = next((res[j][0] for j in range(k + 1, n) if res[j]), t1)
            run = []
            for j in range(k, n):
                if res[j] is None: run.append(j)
                else: break
            step = (nxt - prev) / len(run)
            for i, j in enumerate(run): res[j] = (prev + i * step, prev + (i + 1) * step)
    return res

def chunks():
    out = []
    for lid, who, tts, cap in LINEAS:
        words = cap.split(); times = word_times(lid, words); groups, cur = [], []
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
    cap = [x for x in LINEAS if x[0] == lid][0][3].split(); tt = word_times(lid, cap); c = 0
    for w, (a, b) in zip(cap, tt):
        if _norm(w.strip("*")) == _norm(palabra):
            c += 1
            if c == n: return a
    raise KeyError(lid + " " + palabra)

NOMBRE = {"M": "MANOLO", "T": "TÍO RUBÉN · NOTA DE VOZ", "X": "NITRO"}

def draw_caption(canvas, T):
    for idx, (t0, t1, g, who, lid) in enumerate(CH):
        nxt0 = CH[idx + 1][0] if idx + 1 < len(CH) else 1e9
        if not (t0 - .04 <= T < t1 + .35) or T >= nxt0 - .04: continue
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
            activa = ws - .03 <= T < fin_ - .03; dicha = T >= ws - .03
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

# ---------------------------------------------------------------- barra superior de la serie
EPISODIO, DIA = 1, 1

def coin(d, cx, cy, r):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(242, 190, 60), outline=(120, 80, 10), width=4)
    d.text((cx, cy + 1), "€", font=font(F_UI, int(r * 1.1)), fill=(120, 80, 10), anchor="mm")

def flecha(d, cx, cy, s):
    d.polygon([(cx - 14*s, cy - 12*s), (cx + 2*s, cy + 4*s), (cx - 4*s, cy + 10*s), (cx + 14*s, cy + 14*s), (cx + 10*s, cy - 4*s), (cx + 4*s, cy + 2*s), (cx - 10*s, cy - 16*s)], fill=(255, 90, 80))

def carito(d, cx, cy, col):
    d.rounded_rectangle((cx - 20, cy - 4, cx + 20, cy + 9), 5, fill=col)
    d.polygon([(cx - 12, cy - 4), (cx - 6, cy - 13), (cx + 8, cy - 13), (cx + 14, cy - 4)], fill=col)
    for x in (cx - 11, cx + 11): d.ellipse((x - 6, cy + 4, x + 6, cy + 16), fill=(20, 20, 28), outline=(200, 200, 210), width=2)

def estrella(d, cx, cy, r, col):
    pts = []
    for i in range(10):
        a = -PI_ / 2 + i * PI_ / 5; rr = r if i % 2 == 0 else r * .45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=col, outline=(120, 80, 10))

@lru_cache(1)
def barra_base():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x0, y0, x1, y1 = 36, 168, 1044, 278
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 8, x1, y1 + 10), 26, fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).rounded_rectangle((x0, y0, x1, y1), 26, outline=CYAN + (150,), width=6)
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0, y0, x1, y1), 26, fill=(12, 10, 26, 205), outline=CYAN + (110,), width=2)
    d.rounded_rectangle((x0 + 14, y0 + 12, x0 + 118, y0 + 56), 12, fill=CYAN)
    d.text((x0 + 66, y0 + 34), f"EP.{EPISODIO}", font=font(F_ANTON, 32), fill=OL, anchor="mm")
    d.text((x0 + 132, y0 + 35), f"DÍA {DIA}", font=font(F_ANTON, 40), fill=WHITE, anchor="lm")
    d.line((x0 + 16, y0 + 64, x1 - 16, y0 + 64), fill=(255, 255, 255, 30), width=2)
    d.text((x0 + 18, y0 + 87), "OBJETIVO", font=font(F_UI, 20), fill=CYAN, anchor="lm")
    return im

def draw_hud(canvas, T):
    if T >= S("T18") - .1: return
    canvas.alpha_composite(barra_base())
    d = ImageDraw.Draw(canvas)
    x0, y0, x1 = 36, 168, 1044
    t_deuda, t_caja, t_c1, t_c2, t_rep = WT("T03", "64.300"), S("T08") + .2, WT("T09", "Seat"), WT("T13", "deportivo"), WT("T10", "Cero.")
    def pop(t): return 1 + .28 * math.sin(clamp((T - t) / .3) * PI_) if 0 <= T - t < .3 else 1
    coches = "?" if T < t_c1 else ("1" if T < t_c2 else "2")
    tcoch = t_c1 if T < t_c2 else t_c2
    caja = "?" if T < t_caja else euros(int(410 * ease((T - t_caja) / .8)))
    deuda = "?" if T < t_deuda else "-" + euros(int(64300 * ease((T - t_deuda) / .9)))
    rep = "?" if T < t_rep else "0"
    items = [("coch", coches, tcoch, x0 + 300), ("caja", caja, t_caja, x0 + 420), ("deuda", deuda, t_deuda, x0 + 600), ("rep", rep, t_rep, x0 + 880)]
    for k, v, t, x in items:
        cy = y0 + 34
        if k == "coch": carito(d, x, cy, CYAN if v != "?" else (70, 78, 100))
        if k == "caja": coin(d, x, cy, 15)
        if k == "deuda": flecha(d, x, cy, 1.0)
        if k == "rep": estrella(d, x, cy, 17, (242, 190, 60) if v != "?" else (70, 78, 100))
        col = GRIS if v == "?" else ((255, 120, 110) if k == "deuda" else WHITE)
        d.text((x + 24, y0 + 35), v, font=font(F_ANTON, 34 * pop(t)), fill=col, anchor="lm")
    d.text((x0 + 132, y0 + 87), "Abrir el taller", font=font(F_UI, 24), fill=WHITE, anchor="lm")
    d.text((x1 - 20, y0 + 87), "REPUTACIÓN", font=font(F_UI, 18), fill=GRIS, anchor="rm")

# ---------------------------------------------------------------- piezas
def stamp(canvas, T, t0, label, cx, cy, col=RED, rot=-12, size=120):
    if T < t0: return
    u = clamp((T - t0) / .18); k = 1.8 - .8 * ease(u)
    im = Image.new("RGBA", (1000, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = font(F_ANTON, size); tw = d.textlength(label, font=f)
    d.rounded_rectangle((500 - tw / 2 - 30, 60, 500 + tw / 2 + 30, 240), 18, outline=col, width=14)
    d.text((500, 152), label, font=f, fill=col, anchor="mm")
    im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    im = im.resize((int(im.width * k), int(im.height * k)), Image.BILINEAR)
    if u < 1: im.putalpha(im.getchannel("A").point(lambda v: int(v * u)))
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def ficha(c, T, t0, x, y, nombre, l1, l2, w=500):
    if T < t0: return
    u = ease((T - t0) / .35); xx = x - 80 * (1 - u)
    panel(c, (xx, y, xx + w, y + 170), fill=(250, 246, 235), alpha=int(250 * u), rad=18, outline=OL, ow=6)
    d = ImageDraw.Draw(c)
    if u > .3:
        text(d, (xx + 28, y + 48), nombre, 50, OL, "lm")
        text(d, (xx + 28, y + 102), l1, 25, (90, 80, 100), "lm", F_UI)
        text(d, (xx + 28, y + 138), l2, 25, (200, 50, 50), "lm", F_UI)

def etiqueta(c, T, t0, s, cx, cy, fill=YEL, fg=OL, size=34):
    if T < t0: return
    u = popscale(T, t0); d = ImageDraw.Draw(c); f = font(F_UI, size); tw = d.textlength(s, font=f)
    d.rounded_rectangle((cx - (tw / 2 + 24) * u, cy - 40, cx + (tw / 2 + 24) * u, cy + 40), 14, fill=fill)
    if u > .5: d.text((cx, cy), s, font=f, fill=fg, anchor="mm")

def dust(c, T, n=45, col=(255, 236, 190)):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); r = np.random.default_rng(5)
    for i in range(n):
        x0, y0, sp, ph = r.uniform(150, 930), r.uniform(150, 1300), r.uniform(8, 25), r.uniform(0, 6.28)
        x = x0 + 30 * math.sin(T * .6 + ph); y = (y0 - T * sp) % 1250 + 150
        a = int(90 + 80 * math.sin(T * 2 + ph)); rr = 2 + (i % 3)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col + (max(0, a),))
    c.alpha_composite(ov)

def neon_flicker(c, T, box, col, seed=0):
    """Parpadeo de neón: brillo que tiembla sobre una zona."""
    v = .55 + .45 * math.sin(T * 23 + seed) * math.sin(T * 7.3 + seed * 2)
    if (int(T * 10) + seed) % 37 == 0: v = .1
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).ellipse(box, fill=col + (int(70 * max(0, v)),))
    c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(40)))

# ---------------------------------------------------------------- escenas
def sc_llaves(T):
    c = bg("bg_mesa", T, 0, 1.12, 1.0, 5)
    u = ease((T - .15) / .55)
    bounce = 30 * abs(math.sin((T - .7) * 9)) * math.exp(-(T - .7) * 4) if T > .7 else 0
    put(c, "llaves", 560, 980 - 900 * (1 - u) - bounce, 1.15, rot=-8 + 14 * (1 - u))
    ficha(c, T, WT("T01", "Rubén"), 60, 330, "TÍO RUBÉN", "DESAPARECIDO HACE 2 AÑOS", "NADIE SABE DÓNDE ESTÁ", 560)
    if T >= WT("T01", "Rubén") + .2: put(c, "tio_foto", 860, 470, .55, rot=7)
    stamp(c, T, WT("T01", "llaves."), "HEREDADO", 540, 1200, RED, -12, 110)
    return c

def sc_fachada(T):
    s0, e0 = TL["T02"]
    c = bg("bg_fachada", T, s0, 1.0, 1.07, e0 - s0 + 1, .5, .55)
    put(c, "persiana", 540, 1115, 1.0)
    neon_flicker(c, T, (60, 560, 400, 820), MAG, 1)
    stamp(c, T, WT("T02", "cerrado."), "CERRADO", 540, 1100, RED, -8, 120)
    if T >= WT("T02", "solo."):
        dark(c, 110 * clamp((T - WT("T02", "solo.")) / .3))
    return c

def sc_stats(T):
    s0, e0 = TL["T03"]
    c = bg("bg_noche", T, s0, 1.04, 1.0, 10); d = ImageDraw.Draw(c)
    items = [(s0 + .1, "DEUDA HEREDADA", -64300, RED), (WT("T03", "Dos"), "AÑOS CON LA PERSIANA BAJADA", 2, WHITE),
             (WT("T03", "aviso"), "AVISO DE DESAHUCIO", None, YEL)]
    for i, (t, lab, val, col) in enumerate(items):
        if T < t: continue
        y = 430 + i * 270; a = ease((T - t) / .3)
        panel(c, (90 + 60 * (1 - a), y - 110, 990 - 60 * (1 - a), y + 120), alpha=int(230 * a), outline=CYAN + (90,), ow=3)
        d = ImageDraw.Draw(c)
        text(d, (540, y - 62), lab, 32, (180, 186, 210), "mm", F_UI)
        if val is None:
            stamp(c, T, t + .15, "1 AVISO", 540, y + 32, YEL, -4, 90); d = ImageDraw.Draw(c)
        else:
            cnt = val * ease((T - t) / .9)
            num = ("-" + euros(abs(int(cnt)))) if val < 0 else str(int(round(cnt)))
            text(d, (540, y + 32), num, 118, col)
    return c

def sc_aviso(T):
    s0, e0 = TL["T04"]
    c = bg("bg_fachada", T, s0, 1.5, 1.55, e0 - s0, .5, .62)
    dark(c, 120)
    u = ease((T - s0) / .45)
    put(c, "aviso", 540, 800 + 600 * (1 - u), 1.2, rot=-3)
    stamp(c, T, WT("T04", "banco"), "EMBARGO", 560, 860, RED, -14, 120)
    if T >= WT("T04", "todo"):
        etiqueta(c, T, WT("T04", "todo"), "EL LOCAL Y TODO LO DE DENTRO", 540, 1290, RED, WHITE, 36)
    return c

def sc_persiana(T):
    s0 = S("T05")
    c = bg("bg_fachada", T, s0, 1.0, 1.12, 3.5, .5, .62)
    # interior que se ve al subir
    inner = bg("bg_taller", T, s0, 1.4, 1.4, 1, .5, .6).crop((150, 830, 930, 1400))
    c.alpha_composite(inner, (150, 830))
    up = ease((T - s0 - .1) / 2.2)
    shake = 3 * math.sin(T * 60) if 0 < up < 1 else 0
    pers = scaled("persiana", 1.0)
    h = int(570 * (1 - up))
    if h > 2:
        c.alpha_composite(pers.crop((0, 570 - h, 780, 570)), (150 + int(shake), 830))
    return c

def sc_interior(T):
    t0 = WT("T05", "Huele"); e0 = E("T05")
    c = bg("bg_taller", T, t0, 1.12, 1.0, e0 - t0 + 1, .5, .6)
    neon_flicker(c, T, (300, 220, 800, 520), CYAN, 3)
    dust(c, T, 50)
    tm = WT("T05", "mueve")
    put(c, "motor", 540, 1220, 1.15)
    # ojos en la oscuridad del motor
    if T >= tm:
        d = ImageDraw.Draw(c); bl = 1 if (T - tm) % 2.4 > .12 else .1
        for ex in (500, 580):
            d.ellipse((ex - 14, 1100 - 9 * bl, ex + 14, 1100 + 9 * bl), fill=(216, 255, 90))
    tg = WT("T05", "motor.") + .25
    if T >= tg:
        k = popscale(T, tg, .45); hop = 30 * abs(math.sin((T - tg) * 5)) * math.exp(-(T - tg) * 2)
        put(c, "gato", 540, 1040 - 70 * ease((T - tg) / .4) - hop, .95 * max(k, .02))
        put(c, "motor", 540, 1220, 1.15)  # el gato sale por detrás del bloque
        etiqueta(c, T, tg + .4, "JEFE DE TALLER (DE MOMENTO)", 540, 880)
    return c

def mouth(c, ox, oy, T, talking, w=22):
    d = ImageDraw.Draw(c)
    if talking:
        m = 10 + 18 * abs(math.sin(T * 13)) * (.6 + .4 * abs(math.sin(T * 3.1)))
        d.ellipse((ox - w, oy - 4, ox + w, oy + m), fill=(110, 25, 40), outline=OL, width=5)
        d.ellipse((ox - w * .5, oy + m * .45, ox + w * .5, oy + m - 2), fill=(225, 100, 110))

def sc_manolo(T):
    s0 = S("T06"); e7 = E("T07")
    c = bg("bg_taller", T, s0, 1.0, 1.08, e7 - s0, .5, .55)
    neon_flicker(c, T, (300, 220, 800, 520), CYAN, 3)
    tp = s0 + (E("T06") - s0) * .15
    if T >= tp:
        u = ease((T - tp) / .5)
        dorm = T < WT("T06", "Manolo.")
        bob = 6 * math.sin((T - tp) * (1.2 if dorm else 2.2))
        talk = S("T07") <= T < E("T07")
        px, py = 540 + 600 * (1 - u), 1320 + bob
        put(c, "manolo", px, py, 1.0)
        d = ImageDraw.Draw(c); ox, oy = px - 400, py - 700
        if dorm or (T % 3.3) < .13:   # ojos cerrados (dormido / parpadeo)
            for ex in (350, 450):
                d.ellipse((ox + ex - 20, oy + 438 - 18, ox + ex + 20, oy + 438 + 18), fill=(243, 194, 155))
                d.line((ox + ex - 17, oy + 440, ox + ex + 17, oy + 440), fill=OL, width=4)
        if dorm:
            for k in range(3):
                ph = ((T * .8) + k / 3) % 1
                text(d, (ox + 560 + 60 * ph + k * 10, oy + 300 - 160 * ph), "z", 50 + 20 * k, (220, 230, 255), stroke=4)
        mouth(c, ox + 400, oy + 574, T, talk, 28)
    dust(c, T)
    ficha(c, T, WT("T06", "Manolo.") + .1, 60, 520, "MANOLO", "MECÁNICO · 30 AÑOS CON RUBÉN", "2 AÑOS SIN COBRAR")
    return c

def card(c, T, t, lay, nm, a1, a2):
    k = popscale(T, t, .4)
    panel(c, (110, 820, 970, 1250), fill=(250, 246, 235), alpha=250, rad=26, outline=OL, ow=6)
    put(c, lay, 330, 1035, .9 * max(k, .02))
    d = ImageDraw.Draw(c)
    text(d, (540, 940), nm, 64, OL, "lm")
    text(d, (540, 1030), a1, 30, (90, 80, 100), "lm", F_UI)
    text(d, (540, 1080), a2, 30, (200, 50, 50), "lm", F_UI)

def sc_inventario(T):
    s8 = S("T08"); e10 = E("T10")
    c = bg("bg_noche", T, s8, 1.0, 1.04, e10 - s8); d = ImageDraw.Draw(c)
    if T < S("T09"):
        k = popscale(T, s8 + .1, .4)
        text(d, (540, 760), "¿QUÉ QUEDA", 130 * max(k, .01), WHITE, stroke=8)
        text(d, (540, 900), "DE VALOR?", 130 * max(k, .01), YEL, stroke=8)
        if T >= WT("T08", "ríe."):
            text(d, (540, 1090), "JA, JA, JA", 80 * popscale(T, WT("T08", "ríe.")), CYAN, stroke=6)
        return c
    text(d, (540, 420), "INVENTARIO", 90, WHITE, stroke=6)
    cards = [("icon_elevador", "ELEVADOR", "FUNCIONA… CON PATADA", "ESTADO: DUDOSO", S("T09")),
             ("icon_caja", "HERRAMIENTAS", "CAJA COMPLETA", "FALTA LA MITAD", WT("T09", "caja")),
             ("icon_utilitario", "SEAT IBIZA 98", "DE UN CLIENTE", "NO HA VUELTO EN 2 AÑOS", WT("T09", "Seat"))]
    # miniaturas de lo ya visto
    for i, (lay, nm, a1, a2, t) in enumerate(cards):
        if T >= t: put(c, lay, 260 + i * 280, 600, .55)
    if T < S("T10"):
        cur = max(i for i, x in enumerate(cards) if T >= x[4])
        card(c, T, *[cards[cur][4], *cards[cur][:4]])
        return c
    d = ImageDraw.Draw(c)
    k = popscale(T, S("T10"), .4)
    text(d, (540, 900), "CLIENTES", 110 * max(k, .01), WHITE, stroke=8)
    if T >= WT("T10", "Cero."):
        text(d, (540, 1080), "0", 260 * popscale(T, WT("T10", "Cero.")), RED, stroke=10)
    stamp(c, T, WT("T10", "gafado."), "GAFADO", 760, 1180, YEL, 12, 100)
    return c

def sc_lona(T):
    s0 = S("T11"); e0 = E("T12")
    c = bg("bg_taller", T, s0, 1.25, 1.35, e0 - s0, .5, .7)
    dark(c, 120)
    # foco sobre la lona
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(ov).polygon([(440, 0), (640, 0), (1000, 1250), (80, 1250)], fill=(255, 230, 170, 45))
    c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(30)))
    put(c, "lona", 540, 1060, 1.0)
    dust(c, T, 70)
    if S("T12") <= T:
        put(c, "manolo", 900, 1500, .55)
        mouth(c, 900 - 220 + 220, 1500 - 385 + 315, T, T < E("T12"), 12)
        etiqueta(c, T, WT("T12", "nadie."), "NADIE LO HA TOCADO", 540, 640, RED, WHITE, 38)
    return c

def sc_reveal(T):
    s0 = S("T13"); tg = WT("T13", "guantera...")
    c = bg("bg_taller", T, s0, 1.25, 1.18, 4, .5, .7)
    neon_flicker(c, T, (200, 700, 880, 1300), MAG, 5)
    put(c, "deportivo", 540, 1060, 1.0)
    # la lona sale volando hacia arriba a la derecha
    u = ease((T - s0) / .9)
    if u < 1: put(c, "lona", 540 + 700 * u, 1060 - 900 * u, 1.0, alpha=1 - u * .6, rot=-25 * u)
    if T >= s0 + .9: dust(c, T, 40, (255, 150, 240))
    if T < tg:
        ficha(c, T, WT("T13", "deportivo"), 60, 440, "¿¿ ??", "POTENCIA: DESCONOCIDA", "ESTADO: 40 %", 480)
        if T >= WT("T13", "motor,"): etiqueta(c, T, WT("T13", "motor,"), "MOTOR SIN TERMINAR", 540, 1300, CYAN, OL)
        return c
    # zoom a la guantera → móvil
    z = ease((T - tg) / .8)
    dark(c, 170 * z)
    put(c, "movil", 540, 900 + 400 * (1 - z), .5 + .7 * z, rot=-6 * (1 - z))
    return c

def sc_nota(T):
    s0, e0 = TL["T14"]
    c = bg("bg_noche", T, s0, 1.0, 1.05, e0 - s0)
    put(c, "movil", 540, 900, 1.2)
    d = ImageDraw.Draw(c)
    # barra de reproducción de la nota de voz
    p = clamp((T - s0) / (e0 - s0))
    x0, x1, y = 540 - 85, 540 + 140, 900 - 430 * .6 + 220 * .6
    bx0, bx1 = 540 - 230 * 1.2 / 2 + 160 * .6 * 1.0, 540 + 230 * .6
    d.rounded_rectangle((bx0, 960, bx0 + (bx1 - bx0) * p, 972), 6, fill=CYAN)
    for i in range(14):   # ondas de sonido saliendo del móvil
        ph = (T * 1.4 + i / 14) % 1
        if T < e0 and i % 5 == 0:
            r = 280 + 260 * ph
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(ov).ellipse((540 - r, 900 - r, 540 + r, 900 + r), outline=CYAN + (int(140 * (1 - ph)),), width=5)
            c.alpha_composite(ov)
    put(c, "tio_foto", 860, 470, .55, rot=8)
    if T >= WT("T14", "buscándolo."):
        stamp(c, T, WT("T14", "buscándolo."), "HAY GENTE BUSCÁNDOLO", 540, 1280, RED, -6, 76)
    return c

def sc_faros(T):
    s0, e0 = TL["T15"]
    c = bg("bg_fachada", T, s0, 1.0, 1.06, e0 - s0 + 1, .5, .62)
    inner = bg("bg_taller", T, s0, 1.4, 1.4, 1, .5, .6).crop((150, 830, 930, 1400)); dark(inner, 60)
    c.alpha_composite(inner, (150, 830))
    dark(c, 90)
    u = ease((T - WT("T15", "coche")) / 1.4) if T >= WT("T15", "coche") else 0
    if T >= WT("T15", "coche"):
        put(c, "coche_negro", 540 + 900 * (1 - u), 1260, 1.0)
    tf = WT("T15", "ciegan")
    if T >= tf:
        k = clamp((T - tf) / .25) * (1 - .55 * clamp((T - tf - .6) / .8))
        put(c, "faros", 540, 1000, 1.6, alpha=k)
        c.alpha_composite(Image.new("RGBA", (W, H), (255, 250, 230, int(170 * k * clamp(1 - (T - tf) / .5)))))
    if T >= WT("T15", "petardeando."):   # chispazos del escape
        tp = WT("T15", "petardeando.")
        d = ImageDraw.Draw(c)
        for i in range(3):
            tt = tp + i * .28
            if 0 <= T - tt < .12:
                ex = 540 + 900 * (1 - u) + 495; d.ellipse((ex - 10, 1260 + 160 - 50, ex + 90, 1260 + 160 + 10), fill=(255, 160, 40))
                d.ellipse((ex + 10, 1260 + 160 - 36, ex + 60, 1260 + 160 - 4), fill=(255, 240, 160))
    return c

def sc_nitro(T):
    s0 = S("T16"); e17 = E("T17")
    c = bg("bg_fachada", T, s0, 1.5, 1.56, e17 - s0, .5, 1.0)
    dark(c, 120)
    neon_flicker(c, T, (100, 300, 980, 900), MAG, 7)
    u = ease((T - s0) / .5)
    talk = S("T16") <= T < E("T16")
    nx, ny = 540, 760 + 300 * (1 - u) + 3 * math.sin(T * 1.8)
    put(c, "nitro", nx, ny, 1.0)
    mouth(c, nx + 12, ny + 24, T, talk, 24)
    put(c, "coche_negro", 540, 1090, 1.0)
    d = ImageDraw.Draw(c)
    if T < E("T16") + .2:
        k = popscale(T, WT("T16", "90.000"), .4)
        if k > 0:
            d.rounded_rectangle((220, 280, 860, 430), 20, fill=GREEN, outline=OL, width=6)
            if k > .5: text(d, (540, 355), "90.000 €", 120 * min(1.1, k), WHITE, stroke=6)
        if T >= WT("T16", "lona."): etiqueta(c, T, WT("T16", "lona."), "+ EL COCHE DE TU TÍO", 540, 500, RED, WHITE, 38)
        if T >= WT("T16", "noche."): stamp(c, T, WT("T16", "noche."), "ESTA NOCHE", 540, 640, YEL, 6, 80)
    else:
        ficha(c, T, S("T17"), 50, 280, "IVÁN «NITRO» SALCEDO", "DUEÑO DE NITRO MOTORS", "EL TALLER MÁS GRANDE", 640)
        if T >= WT("T17", "último"):
            etiqueta(c, T, WT("T17", "último"), "EL ÚLTIMO QUE VIO A TU TÍO", 540, 540, RED, WHITE, 38)
    return c

def option(c, T, t0, x, letter, lines, col, hi):
    k = popscale(T, t0, .4)
    if k <= 0: return
    w, h, y = 440, 660, 760
    sc_ = 1.0 + (.06 if hi else 0)
    box = (x - w / 2 * sc_, y - h / 2 * sc_ + 60 * (1 - k), x + w / 2 * sc_, y + h / 2 * sc_ + 60 * (1 - k))
    if hi:
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).rounded_rectangle(box, 30, outline=CYAN + (200,), width=18)
        c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14)))
    panel(c, box, fill=col, alpha=255, rad=30, outline=CYAN if hi else None, ow=10)
    d = ImageDraw.Draw(c)
    d.ellipse((x - 60, box[1] + 40, x + 60, box[1] + 160), fill=OL)
    text(d, (x, box[1] + 100), letter, 90, WHITE)
    for i, (l, cc) in enumerate(lines):
        text(d, (x, box[1] + 230 + i * 58), l, 36, cc, "mm", F_UI)

def sc_decision(T):
    s0, e0 = TL["T18"]
    c = bg("bg_noche", T, s0, 1.0, 1.04, 10); d = ImageDraw.Draw(c)
    k = popscale(T, s0, .4)
    beat = 1 + .05 * max(0, math.sin(T * 7.5)) ** 8
    text(d, (540, 250), "¿QUÉ HARÍAS TÚ?", 110 * max(k, .01) * beat, YEL, stroke=8)
    ta, tb = WT("T18", "A:"), WT("T18", "B:")
    hiA = ta <= T < tb; hiB = tb <= T < e0
    option(c, T, ta, 290, "A", [("VENDES A", (40, 40, 60)), ("NITRO", (40, 40, 60)), ("", OL), ("+25.700 €", (30, 130, 70)),
                                 ("pero el coche", (200, 50, 50)), ("será suyo", (200, 50, 50))], (248, 246, 240), hiA)
    option(c, T, tb, 790, "B", [("LE CIERRAS", OL), ("LA PERSIANA", OL), ("", OL), ("410 €", OL), ("1 mecánico, 1 gato", OL), ("y un coche roto", OL)],
           YEL, hiB)
    if T >= S("T19"):
        u = popscale(T, WT("T19", "Comenta"))
        if u > 0:
            d = ImageDraw.Draw(c)
            d.rounded_rectangle((540 - 300 * u, 1120, 540 + 300 * u, 1210), 45, fill=WHITE)
            if u > .5: text(d, (540, 1165), "COMENTA  A  o  B", 56, OL)
    return c

SCENES = [
    (0, sc_llaves), (S("T02") - .15, sc_fachada), (S("T03") - .15, sc_stats), (S("T04") - .15, sc_aviso),
    (S("T05") - .2, sc_persiana), (WT("T05", "Huele") - .1, sc_interior), (S("T06") - .2, sc_manolo),
    (S("T08") - .2, sc_inventario), (S("T11") - .2, sc_lona), (S("T13") - .1, sc_reveal), (S("T14") - .2, sc_nota),
    (S("T15") - .2, sc_faros), (S("T16") - .15, sc_nitro), (S("T18") - .25, sc_decision),
]

def hblur(im, k):
    if k < 2: return im
    return im.resize((max(1, W // k), H), Image.BILINEAR).resize((W, H), Image.BILINEAR)

IMPACTS = [WT("T01", "llaves."), WT("T02", "cerrado."), WT("T04", "banco"), WT("T10", "gafado."), S("T13") + .1,
           WT("T15", "ciegan"), WT("T16", "noche."), S("T18")]

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
    if idx > 0 and u < 1:   # whip-pan entre escenas
        e = ease(u); prev = SCENES[idx - 1][1](T)
        k = int(2 + 22 * math.sin(PI_ * u))
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
                          "-i", "-", "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp],
                         stdin=subprocess.PIPE)
    for f in range(f0, f1): p.stdin.write(frame(f / FPS).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0: os.replace(tmp, out)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "still":
        for t in sys.argv[2:]: frame(float(t)).save(os.path.join(TMP, f"f_{float(t):06.2f}.jpg"), quality=88)
    elif cmd == "info":
        print(json.dumps({k: [round(a, 2), round(b, 2)] for k, (a, b) in TL.items()}), TOTAL)
        print([round(t, 2) for t, f in SCENES])
    elif cmd == "scenes":
        from multiprocessing import Pool
        ids = [int(x) for x in sys.argv[2:]] or list(range(len(SCENES)))
        with Pool(2) as pool:
            pool.starmap(render_scene, [(i, os.path.join(TMP, f"s{i:02d}.mp4")) for i in ids])
