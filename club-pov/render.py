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
def chunks():
    out = []
    for lid, who, tts, cap in LINEAS:
        words = cap.split()
        t0, t1 = TL[lid]
        tot = sum(len(w.strip("*")) + 2 for w in words)
        groups, cur = [], []
        for w in words:
            cur.append(w)
            if sum(len(x.strip("*")) + 1 for x in cur) >= 14 or w.rstrip("*").endswith((".", ",", ":", "?", "!")):
                groups.append(cur); cur = []
        if cur: groups.append(cur)
        t = t0
        for g in groups:
            d = (t1 - t0) * sum(len(w.strip("*")) + 2 for w in g) / tot
            out.append((t, t + d, g, who, lid)); t += d
    return out
CH = chunks()
NOMBRE = {"P": "PACO", "A": "EL ABUELO (CARTA)", "R": "ARTURO"}

def draw_caption(canvas, T):
    for t0, t1, g, who, lid in CH:
        if t0 <= T < t1 + (0.25 if lid != "L17" else 0) and T < t1 + .25:
            nxt = [c for c in CH if c[0] > t0]
            if nxt and T >= nxt[0][0]: continue
            d = ImageDraw.Draw(canvas)
            k = 0.82 + 0.18 * back((T - t0) / .14)
            size = 96 * k
            f = font(F_ANTON, size)
            parts = [(w.strip("*").upper(), w.startswith("*")) for w in g]
            widths = [d.textlength(p + " ", font=f) for p, _ in parts]
            total = sum(widths) - d.textlength(" ", font=f)
            if total > 820:
                size *= 820 / total; f = font(F_ANTON, size)
                widths = [d.textlength(p + " ", font=f) for p, _ in parts]; total = sum(widths) - d.textlength(" ", font=f)
            x = W / 2 - total / 2; y = 1480
            for (p, hi), wd in zip(parts, widths):
                d.text((x, y), p, font=f, fill=YEL if hi else WHITE, anchor="lm", stroke_width=9, stroke_fill=(10, 10, 20))
                x += wd
            if who in NOMBRE:
                tag = NOMBRE[who]; ft = font(F_UI, 30); tw = d.textlength(tag, font=ft)
                d.rounded_rectangle((W / 2 - tw / 2 - 18, 1385, W / 2 + tw / 2 + 18, 1431), 12, fill=YEL)
                d.text((W / 2, 1408), tag, font=ft, fill=OL, anchor="mm")
            return

# ---------------------------------------------------------------- HUD
HORAS = [(0, "10:02"), (S("L05"), "12:40"), (S("L06"), "13:05"), (S("L11"), "13:31"), (S("L13"), "19:48")]
def draw_hud(canvas, T):
    if T >= S("L16") - .1: return
    d = ImageDraw.Draw(canvas)
    hora = [h for t, h in HORAS if T >= t][-1]
    d.rounded_rectangle((40, 120, 330, 188), 14, fill=(12, 14, 26, 220))
    d.rounded_rectangle((40, 120, 150, 188), 14, fill=YEL)
    text(d, (95, 154), "DÍA 1", 40, OL)
    text(d, (240, 154), hora, 44, WHITE)
    text(d, (44, 210), "SAN LORENZO DEL VALLE", 22, (200, 205, 220), "lm", F_UI)
    # caja
    d.rounded_rectangle((720, 120, 1040, 188), 14, fill=(12, 14, 26, 220))
    text(d, (760, 154), "CAJA", 26, (170, 175, 195), "lm", F_UI)
    caja = "312 €" if T >= S("L11") + 1.2 else "¿?"
    text(d, (1020, 154), caja, 46, (120, 230, 140) if caja != "¿?" else WHITE, "rm")
    if T >= E("L04") - .2:
        u = popscale(T, E("L04") - .2)
        d.rounded_rectangle((720, 196, 1040, 240), 10, fill=RED)
        text(d, (880, 218), "1er PARTIDO EN 21 DÍAS", 24 * max(.01, u), WHITE, "mm", F_UI)

CHECK = ["JUGADORES", "ENTRENADOR", "CAMPO", "FICHA FEDERATIVA", "DINERO"]
def draw_checklist(canvas, x, y, s, T, t0, marks=()):
    d = ImageDraw.Draw(canvas)
    w, h = 560 * s, (90 + 74 * 5) * s
    panel(canvas, (x, y, x + w, y + h), rad=int(26 * s))
    text(d, (x + 36 * s, y + 52 * s), "PARA EMPEZAR LA LIGA", 34 * s, YEL, "lm")
    for i, it in enumerate(CHECK):
        a = clamp((T - t0 - i * .18) / .25)
        if a <= 0: continue
        yy = y + (120 + 74 * i) * s
        d.rounded_rectangle((x + 36 * s, yy - 22 * s, x + 80 * s, yy + 22 * s), int(8 * s), outline=WHITE, width=max(2, int(5 * s)))
        text(d, (x + 104 * s, yy), it, 40 * s, WHITE, "lm", F_UI)
        if it in marks:
            d.line((x + 40 * s, yy, x + 56 * s, yy + 18 * s, x + 86 * s, yy - 26 * s), fill=RED, width=int(8 * s))

# ---------------------------------------------------------------- escenas
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
    stamp(c, T, E("L01") - .9, "HEREDADO", 540, 820)
    return c

def crest(d, cx, cy, s):
    pts = [(cx - 170 * s, cy - 200 * s), (cx + 170 * s, cy - 200 * s), (cx + 170 * s, cy + 40 * s), (cx, cy + 230 * s), (cx - 170 * s, cy + 40 * s)]
    d.polygon(pts, fill=(30, 90, 168), outline=OL, width=int(12 * s))
    d.polygon([(cx - 170 * s, cy - 60 * s), (cx + 170 * s, cy - 60 * s), (cx + 170 * s, cy + 10 * s), (cx - 170 * s, cy + 10 * s)], fill=WHITE)
    text(d, (cx, cy - 130 * s), "C.D.", 70 * s, WHITE)
    text(d, (cx, cy - 25 * s), "SAN LORENZO", 52 * s, (30, 90, 168))
    text(d, (cx, cy + 90 * s), "1931", 60 * s, YEL)

def sc_club(T):
    c = bg("bg_dark", T, S("L02"), 1.0, 1.06, 6).convert("RGBA"); d = ImageDraw.Draw(c)
    s = popscale(T, S("L02") + .05, .45)
    if s > 0:
        # grietas: escudo agrietado
        crest(d, 540, 700, 1.25 * s)
    t1 = S("L02") + (E("L02") - S("L02")) * .45
    if T >= t1:
        u = popscale(T, t1)
        d.rounded_rectangle((540 - 260 * u, 1010, 540 + 260 * u, 1100), 16, fill=RED)
        if u > .5: text(d, (540, 1055), "ÚLTIMA DIVISIÓN", 58, WHITE)
    return c

def sc_stats(T):
    c = bg("bg_dark", T, S("L03"), 1.04, 1.0, 10).convert("RGBA"); d = ImageDraw.Draw(c)
    s0, e0 = TL["L03"]; L = e0 - s0
    items = [(s0 + .1, "DEUDA HEREDADA", -182400, "€", RED), (s0 + L * .33, "PARTIDOS SEGUIDOS SIN GANAR", 43, "", WHITE),
             (s0 + L * .68, "AFICIONADOS EN EL ÚLTIMO PARTIDO", 0, "", YEL)]
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

def sc_ultimatum(T):
    c = bg("bg_dark", T, S("L04"), 1.0, 1.05, 6).convert("RGBA"); d = ImageDraw.Draw(c)
    s0, e0 = TL["L04"]
    k = popscale(T, s0 + .05, .4)
    text(d, (540, 470), "21", 330 * max(k, .01), RED, stroke=10)
    if k > .5: text(d, (540, 670), "DÍAS", 90, WHITE)
    draw_checklist(c, 260, 790, 1.0, T, s0 + .6)
    return c

def sc_campo(T):
    s0, e0 = TL["L05"]; L = e0 - s0
    z = 1.10 - 0.10 * clamp((T - s0) / (L + .5))
    c = bg("bg_campo", T, s0, 1.10, 1.0, L + .5, .5, .45).convert("RGBA")
    def scr(px, py): return z * px - (z * W - W) * .5, z * py - (z * H - H) * .45
    tg = s0 + L * .72
    if T >= tg:
        k = popscale(T, tg, .45)
        put(c, "cabra", 560, 1290, 1.0 * max(k, .02))
    c.alpha_composite(scaled("hierba", 1.0), (0, int(60 * (1 - ease((T - s0) / 2.5)))))
    d = ImageDraw.Draw(c)
    if s0 + L * .48 <= T < tg:  # porterías
        u = popscale(T, s0 + L * .48)
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
        n = 3 if T >= s8 + (E("L08") - s8) * .8 else 18
        slot_grid(c, T, s8 + .1, n if T >= s8 + (E("L08") - s8) * .8 else 0)
        return c
    if T < E("L09") + .15:
        slot_grid(c, T, -99, 3)
        cards = [("ramon", "RAMÓN", "44 AÑOS · PORTERO", "RODILLA DE TITANIO", s9),
                 ("josito", "JOSITO", "17 AÑOS", "NUNCA HA JUGADO", s9 + L9 * .33),
                 ("primo", "EL PRIMO", "¿PRIMO DE QUIÉN?", "NADIE LO SABE", s9 + L9 * .7)]
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
    if T > S("L10") + (E("L10") - S("L10")) * .6:
        x = 540
        for i in range(3):
            put(c, ["ramon", "josito", "primo"][i], 300 + i * 240, 1050, .45)
    return c

def sc_caja(T):
    s0, e0 = TL["L11"]; L = e0 - s0
    zt = s0 + L * .78
    z = 1.0 + 0.9 * ease((T - zt) / 1.2) if T > zt else 1.0
    c = bg("bg_dark", T, s0, 1.0, 1.0, 1).convert("RGBA")
    u = ease((T - s0) / .5)
    k = (z - 1) / .9
    put(c, "caja", 540 - k * (380 - 540) * z, 900 + 100 * (1 - u) - k * (850 - 550) * z, 1.0 * z)
    d = ImageDraw.Draw(c)
    if T >= s0 + L * .35 and T < zt:
        k = popscale(T, s0 + L * .35)
        d.rounded_rectangle((330, 400, 750, 500), 16, fill=(40, 120, 70))
        if k > .5: text(d, (540, 450), "312 €", 80, WHITE)
    if T >= s0 + L * .55 and T < zt:
        k = popscale(T, s0 + L * .55)
        d.rounded_rectangle((560, 1240, 920, 1310), 12, fill=YEL)
        if k > .5: text(d, (740, 1275), "CADUCADO EN 2019", 30, OL, "mm", F_UI)
    if T >= zt + .9:
        text(d, (540, 1250), "PARA CUANDO ESTÉS AQUÍ", 76, YEL, stroke=8)
    return c

HAND = ["Si lees esto, te van a ofrecer", "dinero por el campo.", "No lo vendas.", "Debajo del vestuario", "está la razón por la que", "este club nunca", "debe morir.", "", "         — Tu abuelo"]
def sc_carta(T):
    s0, e0 = TL["L12"]; L = e0 - s0
    tb = s0 + L * .45
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
    put(c, "arturo", 540, 720 + 300 * (1 - u), 1.0)
    put(c, "coche", 540, 1050, 1.0)
    d = ImageDraw.Draw(c)
    if T < E("L14") + .2:
        k = popscale(T, s0 + .1, .4)
        d.rounded_rectangle((200, 280, 880, 430), 20, fill=(40, 120, 70), outline=OL, width=6)
        if k > .5:
            text(d, (540, 355), "250.000 €", 120 * min(1.1, k), WHITE, stroke=6)
        if T >= s0 + (E("L14") - s0) * .7:
            stamp(c, T, s0 + (E("L14") - s0) * .7, "PISOS DE LUJO", 540, 520, YEL, 6, 80)
    else:
        ficha(c, T, S("L15"), 50, 280, "ARTURO FERRÁN", "PRESIDENTE · ATLÉTICO VALLE", "EL QUE ARRUINÓ A TU ABUELO")
        tr = S("L15") + (E("L15") - S("L15")) * .25
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
    text(d, (540, 250), "¿QUÉ HARÍAS TÚ?", 110 * max(k, .01), YEL, stroke=8)
    ta, tb = s0 + L * .12, s0 + L * .55
    hiA = ta <= T < tb; hiB = tb <= T < e0
    option(c, T, ta, 290, "A", [("VENDES EL", (40, 40, 60)), ("TERRENO", (40, 40, 60)), ("", OL), ("+68.000 €", (30, 130, 70)),
                                 ("pero derriban", (200, 50, 50)), ("el campo", (200, 50, 50))], (248, 246, 240), hiA)
    option(c, T, tb, 790, "B", [("ROMPES EL", OL), ("CONTRATO", OL), ("", OL), ("312 €", OL), ("3 jugadores", OL), ("21 días", OL)],
           YEL, hiB)
    if T >= S("L17"):
        u = popscale(T, S("L17") + (E("L17") - S("L17")) * .5)
        if u > 0:
            d = ImageDraw.Draw(c)
            d.rounded_rectangle((540 - 300 * u, 1120, 540 + 300 * u, 1210), 45, fill=WHITE)
            if u > .5: text(d, (540, 1165), "COMENTA  A  o  B", 56, OL)
    return c

SCENES = [  # (inicio, función)
    (0, sc_notaria), (S("L02") - .15, sc_club), (S("L03") - .15, sc_stats), (S("L04") - .15, sc_ultimatum),
    (S("L05") - .2, sc_campo), (S("L06") - .2, sc_paco), (S("L08") - .2, sc_plantilla), (S("L11") - .2, sc_caja),
    (S("L12") - .2, sc_carta), (S("L13") - .2, sc_coche), (S("L14") - .15, sc_arturo), (S("L16") - .25, sc_decision),
]

def frame(T):
    idx = max(i for i, (t, f) in enumerate(SCENES) if T >= t)
    t0, fn = SCENES[idx]
    c = fn(T)
    # transición: flash-zoom de entrada
    u = (T - t0) / .22
    if idx > 0 and u < 1:
        z = 1 + .12 * (1 - ease(u))
        cc = c.resize((int(W * z), int(H * z)), Image.BILINEAR)
        c = cc.crop(((cc.width - W) // 2, (cc.height - H) // 2, (cc.width - W) // 2 + W, (cc.height - H) // 2 + H))
        c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(55 * (1 - u)))))
    c.alpha_composite(VIG)
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
