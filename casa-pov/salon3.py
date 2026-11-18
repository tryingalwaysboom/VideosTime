"""La casa de 1 dólar (reforma) — Parte 3: abrir la caja fuerte con el taladro (gancho = caja ya abierta en el segundo 0).
python3 salon3.py frames -> fotogramas de control · python3 salon3.py -> vídeo final"""
import json, math, os, random, subprocess, sys
from functools import lru_cache
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw
import art as A, salon as SL, manos as M, bodycam as BC
import salon2 as S2
from art import W, H, font, F_ANTON, F_UI, lerp
from ep1 import cam, text, flash, ease, back, clamp, inout, banda, grain, mirada, YEL, WHITE, OL, RED, GRIS, ic_coin, ic_casa, ic_cal, soft
from salon1 import precio, destellos

HERE = os.path.dirname(os.path.abspath(__file__)); FPS = 30
SRC = os.path.join(HERE, "..", "descargas", "casa_salon3"); SFXD = os.path.join(HERE, "..", "descargas", "casa_sfx")
TMP = os.path.join(HERE, "tmp_salon3"); OUT = os.path.join(HERE, "out"); os.makedirs(TMP, exist_ok=True)
VOZ = os.path.join(SRC, "V01.mp3")
RAW = json.load(open(os.path.join(SRC, "V01.json")))
TXT = ("¡Abrí la caja fuerte con un taladro! ¡Y dentro había esto! Primero, la broca. $15 dólares. Taladro, chispas, ¡clac! $200 dólares. "
       "Justo lo que cobraba el cerrajero. Y una llave. Me quedan $1,910 dólares. ¿Qué puerta abre? ¿La habitación o el baño? Tú decides.").split()
assert len(TXT) == len(RAW), (len(TXT), len(RAW))
WD = [(t, w["inicio"], w["fin"]) for t, w in zip(TXT, RAW)]
t0_ = lambda i: WD[i][1]
VDUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", VOZ], capture_output=True, text=True).stdout)
TOTAL = VDUR + .3

T_DENTRO, T_PRIM, T_15, T_TAL, T_CLAC, T_200, T_CERR, T_Y, T_LLAVE, T_ME, T_1910, T_QUE, T_HAB, T_BANO, T_TU = (t0_(i) for i in (8, 11, 14, 16, 18, 19, 26, 27, 29, 30, 32, 34, 38, 41, 42))
CUTS = [0.0, T_PRIM - .12, T_TAL - .15, T_CLAC - .1, T_Y - .08, T_ME - .1, T_QUE - .15, TOTAL]

# ------------------------------------------------------------------ subtítulos y barra (PARTE 3)
def chunks():
    out, g = [], []
    for w in WD:
        g.append(w)
        if len(g) == 3 or w[0][-1] in ".,!?:" or (len(g) == 2 and len(g[0][0] + g[1][0]) > 13): out.append(g); g = []
    if g: out.append(g)
    return out
CH = chunks()
def caption(c, T):
    if T >= CUTS[6] - .05: return
    for i, g in enumerate(CH):
        t0, t1 = g[0][1], g[-1][2]; nxt = CH[i + 1][0][1] if i + 1 < len(CH) else 1e9
        if not (t0 - .05 <= T < min(t1 + .4, nxt - .05)): continue
        d = ImageDraw.Draw(c); k = .86 + .14 * back((T - t0 + .05) / .14)
        f = font(F_ANTON, 94 * k); ws = [d.textlength(w + " ", font=f) for w, _, _ in g]; tot = sum(ws) - d.textlength(" ", font=f)
        if tot > 860: f = font(F_ANTON, 94 * k * 860 / tot); ws = [d.textlength(w + " ", font=f) for w, _, _ in g]; tot = sum(ws) - d.textlength(" ", font=f)
        x = W / 2 - tot / 2; y = 1170
        for j, ((w, a, b), wd) in enumerate(zip(g, ws)):
            fin = g[j + 1][1] if j + 1 < len(g) else b + .4
            col = YEL if a - .03 <= T < fin - .03 else (WHITE if T >= a - .03 else (215, 215, 222))
            d.text((x, y), w, font=f, fill=col, anchor="lm", stroke_width=10, stroke_fill=OL); x += wd
        return

@lru_cache(1)
def hud_base():
    im = Image.new("RGBA", (W, 400), (0, 0, 0, 0)); x0, y0, x1, y1 = 36, 238, 1044, 348
    im.alpha_composite(soft((W, 400), lambda dd: dd.rounded_rectangle((x0, y0 + 8, x1, y1 + 10), 26, fill=(0, 0, 0, 130)), 10))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0, y0, x1, y1), 26, fill=(12, 10, 26, 215), outline=(255, 170, 70, 140), width=2)
    d.rounded_rectangle((x0 + 14, y0 + 12, x0 + 160, y0 + 56), 12, fill=(255, 170, 70)); d.text((x0 + 87, y0 + 34), "PARTE 3", font=font(F_ANTON, 32), fill=OL, anchor="mm")
    d.line((x0 + 16, y0 + 64, x1 - 16, y0 + 64), fill=(255, 255, 255, 30), width=2)
    d.text((x0 + 18, y0 + 87), "OBJETIVO", font=font(F_UI, 20), fill=(255, 170, 70), anchor="lm"); d.text((x0 + 132, y0 + 87), "Abrir la caja fuerte", font=font(F_UI, 24), fill=WHITE, anchor="lm")
    d.text((x1 - 20, y0 + 87), "12 MESES PARA TERMINAR", font=font(F_UI, 18), fill=GRIS, anchor="rm")
    return im
def hud(c, T):
    if T >= CUTS[6] - .1: return
    c.alpha_composite(hud_base()); d = ImageDraw.Draw(c); x0, y0 = 36, 238
    def pop(t): return 1 + .3 * math.sin(clamp((T - t) / .3) * math.pi) if 0 <= T - t < .3 else 1
    # dinero: 1725 al empezar -> -15 (broca) -> +200 (billetes de la caja)
    v = int(1725 - 15 * ease((T - T_15) / .5) * (T >= T_15) + 200 * ease((T - T_200) / .6) * (T >= T_200))
    hot_neg = T_15 <= T < T_15 + 1; hot_pos = T_200 <= T < T_200 + 1.2
    ic_coin(d, x0 + 230, y0 + 34)
    d.text((x0 + 256, y0 + 35), f"${v:,}", font=font(F_ANTON, 36 * max(pop(T_15), pop(T_200))), fill=(255, 120, 110) if hot_neg else ((120, 230, 120) if hot_pos else WHITE), anchor="lm")
    ic_casa(d, x0 + 470, y0 + 34, (255, 170, 70)); d.text((x0 + 498, y0 + 35), "CASA 15%", font=font(F_ANTON, 34), fill=WHITE, anchor="lm")
    ic_cal(d, x0 + 770, y0 + 34, WHITE); d.text((x0 + 798, y0 + 35), "12 MESES", font=font(F_ANTON, 34), fill=WHITE, anchor="lm")

# ------------------------------------------------------------------ caja fuerte abierta y objetos
SAFE = S2.SAFE; X0, Y0, X1, Y1 = SAFE; CX, CY = (X0 + X1) / 2, (Y0 + Y1) / 2

@lru_cache(None)
def pared():
    return S2.pared_cerca(0, rasgado=1, safe=False)

def billete(d, cx, cy, ang, w=210, h=100, tono=0):
    a = math.radians(ang); ca, sa = math.cos(a), math.sin(a)
    pts = [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
    base = [(112, 168, 108), (126, 178, 118), (100, 156, 104)][tono % 3]
    d.polygon(pts, fill=base, outline=(46, 88, 54))
    inner = [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in ((-w / 2 + 12, -h / 2 + 10), (w / 2 - 12, -h / 2 + 10), (w / 2 - 12, h / 2 - 10), (-w / 2 + 12, h / 2 - 10))]
    d.line(inner + [inner[0]], fill=(60, 110, 70), width=3)
    d.ellipse((cx - 24, cy - 24, cx + 24, cy + 24), outline=(50, 96, 58), width=4); d.text((cx, cy), "$", font=font(F_ANTON, 34), fill=(50, 96, 58), anchor="mm")

def interior(T, glow=1.0):
    """hueco de la caja con dinero (sin llave) listo para pegar encima de la pared."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rectangle((X0 - 30, Y0 - 30, X1 + 30, Y1 + 30), fill=(60, 54, 50)); d.rectangle((X0 - 18, Y0 - 18, X1 + 18, Y1 + 18), fill=(30, 28, 30))
    for k in range(18):   # fondo del hueco con degradado cálido
        t = k / 17; d.rectangle((X0, Y0 + t * (Y1 - Y0) / 1, X1, Y1), fill=(int(40 + 70 * glow * (1 - t)), int(34 + 50 * glow * (1 - t)), 30)) if False else None
    d.rectangle((X0, Y0, X1, Y1), fill=(34, 30, 30))
    for k in range(8): d.rectangle((X0, Y0 + k * 60, X1, Y0 + k * 60 + 30), fill=(int(42 + 26 * glow), int(36 + 20 * glow), 30))
    d.line((X0, CY + 40, X1, CY + 40), fill=(100, 94, 86), width=8)   # balda
    rng = random.Random(3)
    for k, (dx, dy, ang) in enumerate(((-110, 170, -8), (80, 176, 6), (-10, 150, -2), (-170, 120, -14), (150, 125, 12), (20, 190, 4))):
        billete(d, CX + dx, Y1 - 120 + dy - 140 + k * 3, ang, 200, 92, k)
    d.rectangle((CX - 60, Y1 - 190, CX + 60, Y1 - 140), fill=(210, 190, 120)); d.text((CX, Y1 - 165), "$200", font=font(F_ANTON, 36), fill=(90, 70, 30), anchor="mm")
    return lay

def puerta_caja(c, ang):
    """puerta de la caja: ang 0 = cerrada · 0..110 grados abriendo hacia nosotros (bisagra a la izquierda)."""
    a = math.radians(ang); cs = math.cos(a); xf = X0 + (X1 - X0) * cs; hf = (Y1 - Y0) / 2 * (1 + .22 * math.sin(a))
    d = ImageDraw.Draw(c)
    col = (84, 92, 96) if cs >= 0 else (60, 66, 70)
    d.polygon([(X0, Y0), (xf, CY - hf), (xf, CY + hf), (X0, Y1)], fill=col, outline=(48, 54, 58))
    for k in range(1, 6):   # remaches / nervios
        t = k / 6; d.line((lerp(X0, xf, 0), lerp(Y0, CY - hf, 0) + (Y1 - Y0) * t, xf, CY - hf + 2 * hf * t), fill=(70, 76, 80), width=3)
    if cs > .12:   # dial y manija, aplastados por la perspectiva
        dx = X0 + (X1 - X0) * cs * .46; rw = 90 * cs
        d.ellipse((dx - rw, CY - 90 * (1 + .1 * math.sin(a)), dx + rw, CY + 90 * (1 + .1 * math.sin(a))), fill=(40, 42, 46), outline=(160, 166, 170), width=6)
        hx = X0 + (X1 - X0) * cs * .86; d.rounded_rectangle((hx - 18 * cs, CY - 110, hx + 18 * cs, CY + 110), 10, fill=(170, 176, 180))

def llave_suelta(c, x, y, s=1.0, ang=-20):
    lay = Image.new("RGBA", (600, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); gold = (236, 196, 70)
    d.ellipse((40, 100, 140, 200), outline=gold, width=20); d.rectangle((130, 140, 470, 160), fill=gold)
    for tx in (390, 430, 460): d.rectangle((tx, 160, tx + 18, 205), fill=gold)
    d.rounded_rectangle((70, 190, 150, 260), 10, fill=(236, 230, 210), outline=(150, 140, 110), width=3); d.text((110, 225), "?", font=font(F_ANTON, 50), fill=(120, 40, 30), anchor="mm")
    lay = lay.rotate(ang, expand=True, resample=Image.BICUBIC); lay = lay.resize((int(lay.width * s), int(lay.height * s)))
    c.alpha_composite(lay, (int(x - lay.width / 2), int(y - lay.height / 2)))

def taladro(c, x, y, ang=0, s=1.0):
    """taladro amarillo apuntando hacia la izquierda; (x,y) = punta de la broca."""
    lay = Image.new("RGBA", (900, 520), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rectangle((60, 235, 300, 265), fill=(190, 192, 198))
    for k in range(7): d.line((70 + k * 34, 235, 100 + k * 34, 265), fill=(130, 132, 140), width=5)   # espiral de la broca
    d.rounded_rectangle((290, 190, 380, 310), 20, fill=(60, 62, 68))
    d.rounded_rectangle((370, 160, 800, 340), 70, fill=(244, 188, 46)); d.rounded_rectangle((370, 160, 800, 215), 50, fill=(255, 214, 90))
    d.rounded_rectangle((520, 300, 680, 520), 40, fill=(40, 40, 46)); d.rounded_rectangle((540, 320, 580, 440), 12, fill=(70, 72, 80))
    d.rectangle((700, 235, 770, 245), fill=(40, 40, 46))
    lay = lay.rotate(ang, expand=True, resample=Image.BICUBIC, center=(60, 250)); lay = lay.resize((int(lay.width * s), int(lay.height * s)), Image.BILINEAR)
    c.alpha_composite(lay, (int(x - 60 * s), int(y - 250 * s)))

def broca(c, x, y, ang=-35, s=1.0):
    lay = Image.new("RGBA", (500, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rectangle((20, 40, 380, 80), fill=(196, 200, 206)); d.polygon([(380, 40), (480, 60), (380, 80)], fill=(160, 164, 170))
    for k in range(10): d.line((30 + k * 36, 40, 56 + k * 36, 80), fill=(120, 124, 132), width=6)
    lay = lay.rotate(ang, expand=True, resample=Image.BICUBIC); lay = lay.resize((int(lay.width * s), int(lay.height * s)))
    c.alpha_composite(lay, (int(x - lay.width / 2), int(y - lay.height / 2)))

def chispas(c, T, x, y, n=26, long=1.0):
    d = ImageDraw.Draw(c); fr = int(T * 30)
    for k in range(n):
        r = random.Random(fr * 97 + k); a = r.uniform(-math.pi * .95, math.pi * .2) + math.pi * .0; v = r.uniform(30, 170) * long
        d.line((x + math.cos(a) * v * .3, y + math.sin(a) * v * .3, x + math.cos(a) * v, y + math.sin(a) * v), fill=(255, r.randint(190, 245), r.randint(60, 140)), width=r.randint(3, 7))
        d.ellipse((x + math.cos(a) * v - 5, y + math.sin(a) * v - 5, x + math.cos(a) * v + 5, y + math.sin(a) * v + 5), fill=(255, 235, 150))
    c.alpha_composite(soft((W, H), lambda dd: dd.ellipse((x - 70, y - 70, x + 70, y + 70), fill=(255, 190, 80, 200)), 24))

def zoom(c, z, cx=W / 2, cy=H / 2):
    if z <= 1.001: return c
    w, h = int(W / z), int(H / z); x = int(clamp(cx - w / 2, 0, W - w) if False else max(0, min(W - w, cx - w / 2))); y = int(max(0, min(H - h, cy - h / 2)))
    return c.crop((x, y, x + w, y + h)).resize((W, H), Image.BILINEAR)

def caja_plate(T, ang, glow=1.0):
    c = pared().copy()
    c.alpha_composite(interior(T, glow)); puerta_caja(c, ang)
    return c

# ------------------------------------------------------------------ escenas
def sc_gancho(T):
    """0 -> segundo 0: caja ya abierta con dinero y llave brillando."""
    c = caja_plate(T, 112, glow=1.0); d = ImageDraw.Draw(c)
    llave_suelta(c, CX + 20, Y0 + 120 + 6 * math.sin(T * 5), 1.05, -24)
    c.alpha_composite(soft((W, H), lambda dd: dd.ellipse((X0 + 30, Y0 + 40, X1 - 30, Y1 - 20), fill=(255, 214, 110, int(90 + 40 * math.sin(T * 6)))), 60))
    z = 1.2 + .15 * ease(T / 3.9); c = zoom(c, z, CX, CY + 150 / z)
    destellos(c, T, 0.05, [(330, 760), (760, 800), (540, 1000), (440, 900), (680, 940)], 1.8, 1.2)
    d = ImageDraw.Draw(c); k = .92 + .08 * back(T / .25)
    text(d, (W / 2, 425), "¡ABIERTA!", 120 * k, (255, 206, 60), stroke=12)
    flash(c, T, T_DENTRO, .14, (255, 250, 220), 150)
    return c

def sc_broca(T):
    t0 = CUTS[1]; u = (T - t0) / (CUTS[2] - t0)
    c = pared().copy(); c.alpha_composite(S2.caja_fuerte()); d = ImageDraw.Draw(c)
    bx, by = BC.respiracion(T * 1.15 + 3, .9)
    broca(c, 520 + 30 * u, 1330 - 40 * u, 145 - 10 * u, 1.3); M.poner(c, "puno", 735 + 30 * u + bx, 1760 + by, "d", 1.0, 0, 1.0)
    # etiqueta "antes"
    k = min(1, back((T - t0) / .25)); d.rounded_rectangle((W / 2 - 230, 470, W / 2 + 230, 570), 24, fill=(230, 80, 70))
    for dx in (-190, -160): d.polygon([(W / 2 + dx + 24, 490), (W / 2 + dx + 24, 550), (W / 2 + dx - 14, 520)], fill=WHITE)
    d.text((W / 2 + 30, 520), "ANTES", font=font(F_ANTON, 64), fill=WHITE, anchor="mm")
    precio(c, T, T_15 - .05, CUTS[2], "BROCA DE ACERO", "- $15", (255, 120, 100), 760)
    flash(c, T, t0, .1)
    return c

def sc_taladro(T):
    t0 = CUTS[2]; u = (T - t0) / (CUTS[3] - t0); z = 1.0 + .12 * ease(u)
    c = pared().copy(); c.alpha_composite(S2.caja_fuerte()); sx, sy = random.Random(int(T * 30)).uniform(-7, 7), random.Random(int(T * 30) + 7).uniform(-7, 7)
    dx, dy = CX - 40, CY
    tx = dx + 150 - 60 * min(1, u * 4) + sx
    taladro(c, tx, dy + sy, 0, .62)
    M.poner(c, "puno", tx + 335, dy + 330 + sy, "d", 1.0, 0, 1.0)
    chispas(c, T, dx + 10, dy + 4, 30, 1.0 + .6 * u)
    c = zoom(c, z, CX + 60, CY + 40); d = ImageDraw.Draw(c)
    text(d, (W / 2 + random.Random(int(T * 30)).uniform(-6, 6), 470), "¡BRRRR!", 120, (255, 206, 60), stroke=12)
    flash(c, T, t0, .1)
    return c

def sc_abre(T):
    t0 = CUTS[3]; u = T - t0
    ang = 112 * ease(u / .4)
    c = caja_plate(T, ang, glow=min(1.0, u / .3)); d = ImageDraw.Draw(c)
    if u > .25: llave_suelta(c, CX + 20, Y0 + 120, 1.05, -24)
    z = 1.0 + .15 * ease(u / 3.5); c = zoom(c, z, CX, CY - 170)
    d = ImageDraw.Draw(c)
    if u < 1.0:
        k = min(1, back(u / .25)); text(d, (W / 2, 470), "¡CLAC!", 150 * k, WHITE, stroke=14)
    flash(c, T, t0, .16, (255, 255, 255), 200)
    if T >= T_200 - .05: destellos(c, T, T_200 - .05, [(300, 900), (780, 880), (540, 1020), (420, 800), (660, 760)], 1.8, 1.4)
    precio(c, T, T_200 - .05, CUTS[4], "DENTRO HABÍA", "+ $200", (110, 230, 120), 520)
    if T >= T_CERR - .15:   # cerrajero tachado
        k = min(1, back((T - T_CERR + .15) / .25)); d = ImageDraw.Draw(c)
        d.rounded_rectangle((W / 2 - 300, 1330 - 52 * k, W / 2 + 300, 1330 + 52 * k), 22, fill=(24, 24, 32, 235), outline=(255, 206, 60), width=4)
        if k > .7:
            d.text((W / 2, 1332), "CERRAJERO  $200", font=font(F_ANTON, 56), fill=(255, 206, 60), anchor="mm")
            p = clamp((T - T_CERR - .1) / .25); d.line((W / 2 - 280, 1332, W / 2 - 280 + 560 * p, 1332), fill=RED, width=12)
    return c

def sc_llave(T):
    t0, t1 = CUTS[4], CUTS[5]; u = (T - t0) / (t1 - t0)
    c = caja_plate(T, 112, glow=1.0); c = zoom(c, 1.5, CX, CY - 10); d = ImageDraw.Draw(c)
    bx, by = BC.respiracion(T * 1.15 + 3, .9)
    # la mano sube con la llave
    p = ease(u * 1.3)
    M.poner(c, "llave", 560 + bx, lerp(1900, 1300, p) + by, "d", 1.1, -8, 1.0)
    destellos(c, T, t0 + .05, [(380, 760), (700, 820), (560, 700)], 1.6, 1.2)
    flash(c, T, t0, .1)
    return c

def sc_dinero(T):
    t0, t1 = CUTS[5], CUTS[6]; u = (T - t0) / (t1 - t0)
    c = cam(SL.salon("noche", "parquet_brillo", False), lerp(1.6, 1.5, inout(u)), 1296, 2080); d = ImageDraw.Draw(c)
    bx, by = BC.respiracion(T * 1.15 + 3, .9)
    M.poner(c, "llave", 560 + bx, 1480 + by, "d", 1.05, -6, 1.0)
    k = min(1, back((T - T_ME + .05) / .3)); d.rounded_rectangle((W / 2 - 400, 420, W / 2 + 400, 720), 42, fill=(16, 18, 40, 235), outline=(255, 206, 60), width=6)
    d.text((W / 2, 480), "TE QUEDAN", font=font(F_ANTON, 56), fill=(255, 206, 60), anchor="mm")
    val = 1910; sz = 170 * (1 + .12 * math.sin(clamp((T - T_1910) / .3) * math.pi) if T >= T_1910 else 1)
    text(d, (W / 2, 600), f"${val:,}", sz * min(1, k + .001), (120, 230, 120), stroke=10)
    flash(c, T, t0, .1)
    return c

RAYO = [(560, 0), (520, 520), (580, 560), (490, 1100), (560, 1140), (470, H)]
def puerta(d, cx, base, w, h, col, panel, placa):
    x0, y0 = cx - w / 2, base - h
    d.rectangle((x0 - 20, y0 - 20, x0 + w + 20, base), fill=(70, 56, 46)); d.rectangle((x0, y0, x0 + w, base), fill=col)
    for dx, dy, ww, hh in ((24, 30, w - 48, h * .38), (24, h * .46, w - 48, h * .46)): d.rounded_rectangle((x0 + dx, y0 + dy, x0 + dx + ww, y0 + dy + hh), 10, fill=panel, outline=(0, 0, 0, 60), width=3)
    d.ellipse((x0 + w - 56, y0 + h * .5 - 16, x0 + w - 24, y0 + h * .5 + 16), fill=(236, 196, 70))
    d.rounded_rectangle((cx - 110, y0 - 90, cx + 110, y0 - 30), 14, fill=(30, 30, 38)); d.text((cx, y0 - 60), placa, font=font(F_ANTON, 36), fill=WHITE, anchor="mm")

def sc_elige(T):
    t0 = CUTS[6]
    hiA = 1.0 if T_HAB - .3 <= T < T_BANO - .3 else (.35 if T_BANO - .3 <= T < T_TU else 1.0)
    hiB = 1.0 if T_BANO - .3 <= T < T_TU else (.35 if T_HAB - .3 <= T < T_BANO - .3 else 1.0)
    base = pared().copy(); L = base.copy(); R = base.copy()
    puerta(ImageDraw.Draw(L), 250, 1520, 300, 860, (150, 100, 62), (126, 82, 50), "HABITACIÓN")
    puerta(ImageDraw.Draw(R), 790, 1520, 280, 860, (96, 170, 196), (74, 140, 166), "BAÑO")
    c = R.copy(); mL = Image.new("L", (W, H), 0); ImageDraw.Draw(mL).polygon([(0, 0)] + RAYO + [(0, H)], fill=255); c.paste(L, (0, 0), mL)
    for poly, h in (([(0, 0)] + RAYO + [(0, H)], hiA), ([(W, 0)] + RAYO + [(W, H)], hiB)):
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).polygon(poly, fill=(0, 0, 0, int(170 * (1 - h)))); c.alpha_composite(lay)
    c.alpha_composite(soft((W, H), lambda dd: dd.line(RAYO, fill=(255, 190, 90, 255), width=30), 16)); d = ImageDraw.Draw(c); d.line(RAYO, fill=(255, 245, 220), width=9)
    k0 = min(1, back((T - t0) / .3)); text(d, (W / 2, 340), "¿QUÉ ABRE LA LLAVE?", 66 * k0, WHITE, stroke=8)
    for cx, t1, t2, col, h, tin in ((270, "HABITACIÓN", "A", (255, 190, 100), hiA, T_HAB - .3), (810, "BAÑO", "B", (120, 220, 255), hiB, T_BANO - .3)):
        if T < t0 + .3: continue
        k = min(1, back((T - max(tin, t0 + .3)) / .3)) * (1 + .08 * h) if T >= tin else min(1, back((T - t0 - .3) / .3)) * .9
        text(d, (cx, 460), t1, (66 if len(t1) > 5 else 84) * k, col if h > .5 else (190, 190, 200), stroke=10)
    flash(c, T, t0, .14)
    return c

ESC = [sc_gancho, sc_broca, sc_taladro, sc_abre, sc_llave, sc_dinero, sc_elige]
def escena(T):
    for i in range(len(ESC)):
        if CUTS[i] <= T < CUTS[i + 1]: return i
    return len(ESC) - 1

def frame(T):
    i = escena(T); c = mirada(ESC[i](T), T, .5 if i == 6 else 1.0)
    hud(c, T)
    if T < CUTS[6] - .05: c.alpha_composite(banda())
    caption(c, T)
    a = np.asarray(c.convert("RGB"), np.int16) + grain(int(T * FPS) % 6)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")

def render(i):
    fa, fb = round(CUTS[i] * FPS), round(CUTS[i + 1] * FPS)
    part = os.path.join(TMP, f"e{i}.part.mp4"); out = os.path.join(TMP, f"e{i}.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", part], stdin=subprocess.PIPE)
    for f in range(fa, fb): p.stdin.write(frame(f / FPS).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(part, out)
    return i

def mezcla(wav):
    s = lambda n: os.path.join(SFXD, n + ".mp3")
    # (archivo, inicio, dB, duración máx opcional)
    SFX = [(s("caja_fuerte"), 0.0, 0, None), (s("billetes"), T_DENTRO, 0, None), (s("whoosh"), CUTS[1] - .2, -3, None),
           (s("caja"), T_15 - .05, -1, None), (s("taladro"), T_TAL - .05, -3, CLAC := T_CLAC - .05 - (T_TAL - .05)),
           (s("boom"), T_CLAC - .04, 0, None), (s("caja_fuerte"), T_CLAC, -1, None),
           (s("billetes"), T_200, 0, None), (s("caja"), T_200, -1, None), (s("brillo"), T_Y, -2, None), (s("llave"), T_LLAVE - .35, 1, None),
           (s("caja"), T_1910 - .05, -1, None), (s("whoosh"), CUTS[6] - .25, -2, None)]
    ins = ["-i", VOZ]; flt = [f"[0:a]aresample=48000,apad=pad_dur=4,acompressor=threshold=-18dB:ratio=3:attack=5:release=120,loudnorm=I=-15:TP=-1.5:LRA=9,atrim=0:{TOTAL:.2f}[v]"]
    for k, (p, t, db, mx) in enumerate(SFX):
        ins += ["-i", p]; ms = int(max(0, t) * 1000)
        cut = f",atrim=0:{mx:.2f},afade=t=out:st={max(0, mx - .12):.2f}:d=0.12" if mx else ""
        flt.append(f"[{k + 1}:a]aresample=48000,loudnorm=I=-26:TP=-6{cut},volume={db}dB,adelay={ms}|{ms},apad[s{k}]")
    flt.append("[v]" + "".join(f"[s{k}]" for k in range(len(SFX))) + f"amix=inputs={len(SFX) + 1}:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.95[m]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(flt), "-map", "[m]", "-ac", "2", wav], check=True)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        os.makedirs("/tmp/s3_chk", exist_ok=True)
        for i in range(len(ESC)):
            for q in (.04, .5, .9):
                t = lerp(CUTS[i], CUTS[i + 1], q); frame(t).resize((405, 720)).save(f"/tmp/s3_chk/{i}_{q}.jpg")
        print("TOTAL", round(TOTAL, 2), [round(x, 2) for x in CUTS]); sys.exit()
    with Pool(3) as p: list(p.imap_unordered(render, range(len(ESC))))
    lst = os.path.join(TMP, "list.txt"); open(lst, "w").write("".join(f"file 'e{i}.mp4'\n" for i in range(len(ESC))))
    hq = os.path.join(TMP, "hq.mp4"); subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", hq], check=True)
    wav = os.path.join(TMP, "mezcla.wav"); mezcla(wav)
    out = os.path.join(OUT, "la_casa_de_1_dolar_parte3_salon.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", hq, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-maxrate", "5000k", "-bufsize", "10000k",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], check=True)
    print("ok", out, round(TOTAL, 2))
