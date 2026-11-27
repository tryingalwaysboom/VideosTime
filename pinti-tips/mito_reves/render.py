"""Tip «3 frases que apagan a tu hijo» · @escribirconpinti. Tiempos por palabra (Whisper), escenas de ~2-3 s con movimiento,
todo visible desde el frame 0, subtítulos palabra a palabra, zona segura TikTok.  Uso: python3 render.py info | still 1,2 | scenes [i..] | mix [out.mp4]"""
import os, sys, json, math, random, subprocess
from functools import lru_cache
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageOps
import art as A

HERE = os.path.dirname(os.path.abspath(__file__))
DESC = os.path.join(HERE, "..", "..", "descargas", "mito3")
SFXD = os.path.join(HERE, "..", "..", "descargas", "mateo_sfx")
TMP = os.path.join(HERE, "tmp2"); os.makedirs(TMP, exist_ok=True)
W, H, FPS = 1080, 1920, 30
J = json.load(open(os.path.join(DESC, "voz.json"), encoding="utf-8"))
def ta(i): return J[i]["inicio"]
TOTAL = float(math.ceil(J[-1]["fin"] + 0.6))
WORDS = [(x["p"].strip('"“”'), x["inicio"], x["fin"]) for x in J]

# ---------------------------------------------------------------- utilidades
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(u): u = clamp(u); return u * u * (3 - 2 * u)
def back(u): u = clamp(u); c1 = 1.70158; c3 = c1 + 1; return 1 + c3 * (u - 1) ** 3 + c1 * (u - 1) ** 2
def u_(t, t0, d): return clamp((t - t0) / d)
def pop(t, t0, d=.28): return back(u_(t, t0, d))
def bob(t, a=8, f=1.4, ph=0.0): return math.sin(t * f * 2 * math.pi + ph) * a
SHK = [0.0, 0.0]
def shake(t, t0, amp=22, dur=.45):
    if 0 <= t - t0 < dur:
        k = (1 - (t - t0) / dur) ** 2; SHK[0] += math.sin((t - t0) * 70) * amp * k; SHK[1] += math.cos((t - t0) * 83) * amp * .7 * k

def put(base, im, cx, cy, s=1.0, rot=0.0, a=1.0):
    if s <= 0.02 or a <= 0.02: return
    if abs(s - 1) > 1e-3: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if a < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    base.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)

_HC = {}
def put_tip(base, im, tx, ty, s=1.0, espejo=False):      # pone la punta del lápiz de la mano en (tx, ty)
    s = round(s, 2); key = (id(im), s)
    if len(_HC) > 24: _HC.clear()
    if key not in _HC: _HC[key] = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR) if s != 1 else im
    im2 = _HC[key]; tipx = (A.HAND_W - A.TIP[0] if espejo else A.TIP[0]) * s
    base.paste(im2, (int(tx - tipx), int(ty - A.TIP[1] * s)), im2)

PAL = {"crema": ((255, 244, 222), (255, 230, 192)), "cielo": ((196, 226, 250), (172, 210, 244)), "menta": ((200, 236, 222), (174, 226, 206)),
       "durazno": ((255, 214, 186), (255, 198, 164)), "lila": ((226, 214, 248), (208, 192, 240)), "amarillo": ((255, 226, 120), (255, 212, 84)),
       "alerta": ((255, 204, 198), (250, 176, 170)), "noche": ((52, 46, 84), (66, 58, 104))}
@lru_cache(None)
def _tile(name):
    c1, c2 = PAL[name]; im = Image.new("RGB", (W + 240, H + 240), c1); d = ImageDraw.Draw(im)
    for gy in range(0, H + 240, 120):
        for gx in range(0, W + 240, 120):
            ox = 60 if (gy // 120) % 2 else 0; d.ellipse((gx + ox - 14, gy - 14, gx + ox + 14, gy + 14), fill=c2)
    return im
def bg(base, name, t, sp=16):
    ox = int(t * sp) % 120; oy = int(t * sp * .6) % 120
    base.paste(_tile(name).crop((ox, oy, ox + W, oy + H)), (0, 0))

def escritorio(base, t=0, color=(214, 150, 92)):
    d = ImageDraw.Draw(base); d.rectangle((0, 1150, W, H), fill=color); d.rectangle((0, 1150, W, 1170), fill=(238, 184, 130)); d.line((0, 1150, W, 1150), fill=A.OL, width=7)

import numpy as np
from scipy.ndimage import binary_fill_holes
@lru_cache(None)
def _tit(l, size, col):
    im = A.texto(l, size, col, 12 if size > 100 else 17)
    a = np.array(im.getchannel("A")) > 8; fill = binary_fill_holes(a) & ~a
    if fill.any():
        arr = np.array(im); arr[fill] = (*A.OL, 255); im = Image.fromarray(arr, "RGBA")
    return im

def titulo(base, txt, t, t0=0.0, y=330, size=128, fill=(255, 255, 255), amarillo=None, d=.3):
    """Titular de dos líneas máx.: la línea marcada con * va en amarillo."""
    lines = txt.split("\n"); n = len(lines)
    for i, l in enumerate(lines):
        col = A.AMA if l.startswith("*") else fill
        im = _tit(l.lstrip("*"), size, col)
        put(base, im, 540, y + i * size * 1.12, pop(t, t0 + i * .12, d), 0)

def insignia(base, num, t, t0=0.0, x=170, y=300, s=1.0):
    k = pop(t, t0, .3)
    im = A.canvas(200, 200); d = ImageDraw.Draw(im); A.ell(d, (10, 10, 190, 190), A.AMA, A.OL, 10); im = A.fin(im).copy()
    ImageDraw.Draw(im).text((100, 108), str(num), font=A.font("anton", 130), fill=A.OL, anchor="mm")
    put(base, im, x, y, k * s, -6)

def kidpos(base, expr, t, x=540, y=900, s=1.0, t0=0.0, rot=0.0, rebote=True):
    k = pop(t, t0, .45) if rebote else 1
    put(base, A.kid(expr), x, y + (1 - k) * 700 + bob(t, 7), s, rot + bob(t, 1.5, .8))

def confeti(base, t, t0, n=26, seed=1):
    rnd = random.Random(seed)
    for i in range(n):
        x0 = rnd.uniform(80, 1000); vy = rnd.uniform(380, 780); ph = rnd.uniform(0, 6.28); c = rnd.choice([A.AMA, A.ROJO, A.VERDE, (63, 127, 208), A.ROSA])
        tt = t - t0 - rnd.uniform(0, .5)
        if tt < 0 or tt > 3.2: continue
        y = 240 + tt * vy * .55; x = x0 + math.sin(tt * 4 + ph) * 40
        if y > 1180: continue
        im = Image.new("RGBA", (26, 14), c + (255,)); put(base, im, x, y, 1, tt * 240 + ph * 50)

def estrellas(base, t, t0, centro, n=5, r=190, size=90, seed=2):
    rnd = random.Random(seed)
    for i in range(n):
        a = i / n * 6.28 + rnd.uniform(-.4, .4); k = pop(t, t0 + i * .07, .3) * (1 - clamp((t - t0 - 1.2) / .6))
        put(base, A.estrella(int(size * rnd.uniform(.8, 1.2))), centro[0] + math.cos(a) * r * rnd.uniform(.8, 1.2), centro[1] + math.sin(a) * r * rnd.uniform(.8, 1.2), k, i * 25)

def hoja_escribiendo(base, cx, cy, s, rot, t, t0, dur, lineas, modo="limpia", mano=True, ms=.55, seed=3):
    """La letra aparece de izquierda a derecha y el lápiz con la mano izquierda va siguiendo la punta."""
    lineas = list(lineas); full = A.letra(tuple(lineas), modo, seed); prog = u_(t, t0, dur); n = len(lineas)
    k = prog * n; li = min(int(k), n - 1); frac = 1.0 if prog >= 1 else k - li
    out = Image.new("RGBA", (720, 900), (0, 0, 0, 0)); fx = A.font("hand", 150); xr = 120
    for i, txt in enumerate(lineas):
        y0 = 210 + i * 150 - 150; wl = fx.getlength(txt) * (1.04 if modo != "limpia" else 1.0)
        if i < li or prog >= 1: x1 = 720
        elif i == li: x1 = int(120 + frac * (wl + 20)); xr = 120 + frac * wl
        else: continue
        out.alpha_composite(full.crop((0, y0, x1, y0 + 190)), (0, y0))
    h = A.hoja().copy(); h.alpha_composite(out); put(base, h, cx, cy, s, rot)
    if mano:
        px, py = (xr if prog < 1 else 120 + fx.getlength(lineas[-1])), 210 + li * 150 - 18 + bob(t, 4, 5)
        if prog >= 1: py = 210 + (n - 1) * 150 - 18
        dx, dy = (px - 360) * s, (py - 450) * s; th = math.radians(rot)
        tx = cx + dx * math.cos(th) + dy * math.sin(th); ty = cy - dx * math.sin(th) + dy * math.cos(th)
        put_tip(base, A.pencil_hand(200), tx + 10, ty, ms)

def carta(base, txt, color, x, y, t, t0, w=420, h=520, rot=0):
    k = pop(t, t0, .35); im = A.canvas(w, h); d = ImageDraw.Draw(im); A.rrect(d, (8, 8, w - 8, h - 8), 44, color, A.OL, 10); im = A.fin(im).copy()
    put(base, im, x, y, k, rot)
    put(base, A.texto(txt, 76, (255, 255, 255), 9), x, y - 80, k, rot)



# ---------------------------------------------------------------- escenas
def per(b, quien, expr, t, x=540, y=960, s=1.0, rot=0.0, **kw):
    im = A.nina(expr) if quien == "n" else A.mama(expr, **kw)
    put(b, im, x, y + 60 + bob(t, 7), s * 1.2, rot + bob(t, 1.5, .8))

def frase(b, t, txt, x, y, size, t0=.0, col=(255, 255, 255), tail="left", rot=-2):
    put(b, A.globo(txt, size, col, tail), x, y, pop(t, t0, .32), rot + bob(t, 2))

def numero(b, n, t, x=540, y=900, s=1.0, color=None):
    im = A.canvas(560, 560); d = ImageDraw.Draw(im); A.ell(d, (20, 20, 540, 540), color or A.AMA, A.OL, 14); im = A.fin(im).copy()
    ImageDraw.Draw(im).text((280, 300), str(n), font=A.font("anton", 380), fill=A.OL, anchor="mm")
    put(b, im, x, y + bob(t, 8, 1.2), pop(t, 0, .35) * s, -5 + bob(t, 2, 1))

def tarjeta(txt, w=420, h=520, size=380, color=A.CREMA, espejo=False, fcol=None):
    im = A.canvas(w, h); d = ImageDraw.Draw(im); A.rrect(d, (8, 8, w - 8, h - 8), 44, color, A.OL, 10); im = A.fin(im).copy()
    g = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ImageDraw.Draw(g).text((w // 2, h // 2 + 10), txt, font=A.font("hand", size), fill=fcol or A.OL, anchor="mm")
    if espejo: g = ImageOps.mirror(g)
    im.alpha_composite(g); return im

@lru_cache(None)
def perro(der=True):
    im = A.canvas(520, 380); d = ImageDraw.Draw(im); C = (222, 170, 108)
    A.rrect(d, (90, 130, 380, 270), 70, C, A.OL, 10)
    for x in (120, 320): A.rrect(d, (x, 240, x + 50, 350), 20, C, A.OL, 10)
    A.line(d, [(95, 160), (45, 100)], A.OL, 26); A.line(d, [(95, 160), (45, 100)], C, 14)
    A.ell(d, (320, 60, 470, 200), C, A.OL, 10); A.ell(d, (410, 110, 505, 175), (240, 205, 160), A.OL, 10); A.ell(d, (480, 112, 505, 134), A.OL, None)
    A.ell(d, (385, 95, 410, 120), (255, 255, 255), A.OL, 6); A.ell(d, (392, 102, 404, 114), A.OL, None)
    A.poly(d, [(330, 70), (350, 10), (385, 75)], (150, 100, 60), A.OL, 8)
    im = A.fin(im).copy(); return im if der else ImageOps.mirror(im)

def trazo(letra, p, size=520):
    """Dibuja la b o la d en dos trazos: el 1.º en rojo, el 2.º en azul."""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im); W = 44
    def seg(pts, col):
        for i in range(len(pts) - 1): d.line([pts[i], pts[i + 1]], fill=col, width=W)
        for q in pts: d.ellipse((q[0] - W // 2, q[1] - W // 2, q[0] + W // 2, q[1] + W // 2), fill=col)
    def arco(cx, cy, r, a0, sg, k, col): seg([(cx + r * math.cos(math.radians(a0 + sg * 360 * j / 40)), cy - r * math.sin(math.radians(a0 + sg * 360 * j / 40))) for j in range(int(40 * k) + 1)], col)
    ROJ, AZU = (230, 70, 60), (60, 130, 220)
    if letra == "b":
        k1 = min(1, p / .5); k2 = max(0, (p - .5) / .5)
        seg([(170, 60), (170, 60 + 440 * k1)], ROJ)
        if k2 > 0: arco(300, 380, 120, 180, -1, k2, AZU)
    else:
        k1 = min(1, p / .5); k2 = max(0, (p - .5) / .5)
        arco(230, 380, 120, 0, 1, k1, ROJ)
        if k2 > 0: seg([(350, 60), (350, 60 + 440 * k2)], AZU)
    return im

def tabla_trazo(b, letra, t, x, y, s=1.0):
    k = pop(t, 0, .35); card = tarjeta("", 560, 640); put(b, card, x, y, k * s, 0)
    ImageDraw.Draw(b)  # no-op para mantener el orden
    put(b, trazo(letra, ease(u_(t, .3, 2.2)), 520), x, y, k * s, 0)
    numero(b, 1, t, x - 240 * s, y - 300 * s, .22 * s); numero(b, 2, t - 1.3, x + 240 * s, y - 300 * s, .22 * s)

def S00(b, t, T):  # gancho visible desde el frame 0
    bg(b, "cielo", t); titulo(b, "SI TU HIJO ESCRIBE\n*LAS LETRAS AL REVÉS", t, -1, 290, 78)
    put(b, tarjeta("b"), 290, 860 + bob(t, 6, 1.2), .85, -5); put(b, A.flecha_doble(250), 540, 860, 1.0, 0); put(b, tarjeta("d"), 790, 860 + bob(t, 6, 1.2, 1), .85, 5)
def S01(b, t, T):
    bg(b, "alerta", t); put(b, A.sello("NO HAGAS ESTO", 940, 280, A.ROJO, 120), 540, 640 + bob(t, 4, 1.5), pop(t, 0, .3), -4); per(b, "m", "preocupado", t, 540, 1120, .85)
def S02(b, t, T):
    bg(b, "lila", t); per(b, "m", "preocupado", t, 400, 1130, .8); frase(b, t, "¡Es dislexia!", 590, 620, 90, .2, tail="left"); titulo(b, "ALGUIEN\n*TE LO DIJO", t, 0, 290, 96)
def S03(b, t, T):
    bg(b, "amarillo", t); put(b, A.sello("MITO", 760, 300, A.ROJO, 200), 540, 760, pop(t, .05, .3), -5); put(b, A.xmark(260), 840, 1130, pop(t, .5), 8)
def S04(b, t, T):
    bg(b, "noche", t); per(b, "n", "triste", t, 540, 1130, .85); titulo(b, "TU MIEDO\n*LE HACE DAÑO", t, 0, 290, 96, (255, 236, 160))
def S05(b, t, T):
    bg(b, "menta", t); numero(b, 7, t, 540, 760, .95); titulo(b, "HASTA LOS\n*7 AÑOS", t, 0, 290, 96); put(b, A.sello("ES NORMAL", 700, 230, A.VERDE, 120), 540, 1130, pop(t, 1.0, .3), -3)
def S06(b, t, T):
    bg(b, "cielo", t); put(b, tarjeta("b"), 300, 850, pop(t, 0, .3) * .8, -4); put(b, A.flecha_doble(260), 540, 850, pop(t, .5), 0); put(b, tarjeta("d"), 780, 850, pop(t, .8, .3) * .8, 4)
    titulo(b, "B  COMO  D", t, 0, 400, 120)
def S07(b, t, T):
    bg(b, "durazno", t); put(b, tarjeta("p"), 300, 850, pop(t, 0, .3) * .8, -4); put(b, A.flecha_doble(260), 540, 850, pop(t, .4), 0); put(b, tarjeta("q"), 780, 850, pop(t, .6, .3) * .8, 4)
    titulo(b, "P  COMO  Q", t, 0, 400, 120)
def S08(b, t, T):
    bg(b, "crema", t); h = A.hoja().copy(); h.alpha_composite(ImageOps.mirror(A.letra(("LUCÍA",), "limpia", 4, 150))); put(b, h, 540, 880 + bob(t, 6), .95, -3)
    titulo(b, "SU NOMBRE\n*EN ESPEJO", t, 0, 290, 96)
def S09(b, t, T):
    bg(b, "lila", t); put(b, A.bombilla(480), 540, 840 + bob(t, 8, 1.2), pop(t, .1, .4), 0); titulo(b, "SU CEREBRO\n*ESTÁ APRENDIENDO", t, 0, 290, 80)
def S10(b, t, T):
    bg(b, "amarillo", t); titulo(b, "LA DIRECCIÓN\n*IMPORTA", t, 0, 330, 100); put(b, A.flecha_doble(560), 540, 760, pop(t, .3), 0); put(b, tarjeta("b", 300, 380, 280), 540, 1090, pop(t, .6, .3), 0)
def S11(b, t, T):
    bg(b, "menta", t); put(b, perro(False), 290, 800 + bob(t, 6, 1.6), .75 * pop(t, 0, .3), 0); put(b, perro(True), 790, 800 + bob(t, 6, 1.6, 1), .75 * pop(t, .5, .3), 0)
    put(b, A.check(170), 540, 1020, pop(t, 1.3), 6); titulo(b, "SIGUE SIENDO\n*UN PERRO", t, 0, 290, 96)
def S12(b, t, T):
    bg(b, "alerta", t); put(b, tarjeta("b"), 300, 850, pop(t, 0, .3) * .8, -4); put(b, tarjeta("b", espejo=True), 750, 850, pop(t, .35, .3), 4); put(b, A.texto("¿?", 170, A.AMA, 12), 540, 1250, pop(t, 1.0, .3), 5)
def S13(b, t, T):
    bg(b, "amarillo", t); put(b, A.sello("OTRA LETRA", 860, 260, A.ROJO, 130), 540, 760, pop(t, .05, .3), -4); estrellas(b, t, .3, (540, 760), 6, 420)
def S14(b, t, T):
    bg(b, "cielo", t); per(b, "n", "feliz", t, 540, 1120, .85); put(b, A.bombilla(260), 830, 640 + bob(t, 6, 1.4), pop(t, .5, .4), 0); titulo(b, "ES NUEVO\n*PARA ÉL", t, 0, 290, 100)
def S15(b, t, T):
    bg(b, "alerta", t); titulo(b, "LO QUE NO\n*HAY QUE HACER", t, 0, 290, 96); per(b, "m", "neutral", t, 540, 1130, .85); put(b, A.xmark(220), 830, 780, pop(t, .6), 8)
def S16(b, t, T):
    bg(b, "crema", t); h = A.hoja().copy(); h.alpha_composite(A.letra(("b  d  p",), "limpia", 4, 150)); put(b, h, 540, 880 + bob(t, 6), .95, -3)
    k = ease(u_(t, .4, .6)); ImageDraw.Draw(b).line((220, 760, 220 + 640 * k, 960), fill=A.ROJO, width=30); titulo(b, "TACHARLE", t, 0, 300, 120)
def S17(b, t, T):
    bg(b, "alerta", t); per(b, "m", "neutral", t, 380, 1130, .8); frase(b, t, "Está mal,\notra vez.", 600, 620, 84, .05); put(b, A.xmark(210), 850, 1010, pop(t, 1.0, .3), 0)
def S18(b, t, T):
    bg(b, "lila", t); per(b, "m", "preocupado", t, 540, 1100, .9); titulo(b, "CARA DE\n*PREOCUPACIÓN", t, 0, 290, 96); put(b, A.xmark(190), 840, 760, pop(t, .8), 8)
def S19(b, t, T):
    bg(b, "noche", t); per(b, "n", "triste", t, 540, 1110, .85); titulo(b, "SE FRUSTRA Y\n*EVITA ESCRIBIR", t, 0, 290, 84, (255, 236, 160)); put(b, A.lapiz(480), 820 + t * 120, 1260 + t * 20, 1.0, -8)
def S20(b, t, T):
    bg(b, "menta", t); titulo(b, "LO QUE SÍ", t, 0, 420, 170); put(b, A.check(300), 540, 820, pop(t, .3, .4), 6)
def S21(b, t, T):
    bg(b, "menta", t); per(b, "m", "feliz", t, 540, 1120, .85); titulo(b, "ENSÉÑALE POR DÓNDE\n*EMPIEZA CADA LETRA", t, 0, 290, 76); put(b, A.flecha_curva(260, A.ROJO), 850, 760, pop(t, .8), 100)
def S22(b, t, T):
    bg(b, "amarillo", t); tabla_trazo(b, "b", t, 540, 800, 1.0); titulo(b, "LA B", t, 0, 300, 120); put(b, A.texto("palito, luego barriga", 62, (255, 255, 255), 8, "baloo"), 540, 1180, pop(t, 1.0))
def S23(b, t, T):
    bg(b, "cielo", t); tabla_trazo(b, "d", t, 540, 800, 1.0); titulo(b, "LA D", t, 0, 300, 120); put(b, A.texto("barriga, luego palito", 62, (255, 255, 255), 8, "baloo"), 540, 1180, pop(t, 1.0))
def S24(b, t, T):
    bg(b, "durazno", t); put(b, A.ojo(300), 540, 700 + bob(t, 6, 1.3), pop(t, .1, .35), 0); put(b, tarjeta("b", 260, 330, 230), 250, 1060, pop(t, .6, .3), -6); put(b, tarjeta("d", 260, 330, 230), 830, 1060, pop(t, .9, .3), 6); titulo(b, "BÚSCALAS EN\n*CARTELES Y CUENTOS", t, 0, 290, 80)
def S25(b, t, T):
    bg(b, "amarillo", t); put(b, A.sello("OTRO TRUCO", 860, 260, A.VERDE, 130), 540, 760, pop(t, .05, .3), -4); estrellas(b, t, .3, (540, 760), 6, 420)
def S26(b, t, T):
    bg(b, "lila", t); per(b, "n", "feliz", t, 540, 1250, .75); u = ease(u_(t, .4, 2.0)); put(b, trazo("b", u, 460), 540, 740, .9, 0); titulo(b, "DIBÚJALA CON\n*EL DEDO EN EL AIRE", t, 0, 290, 76)
def S27(b, t, T):
    bg(b, "durazno", t); d = ImageDraw.Draw(b); d.rounded_rectangle((120, 560, 960, 1180), 50, fill=(236, 205, 150), outline=A.OL, width=10)
    put(b, trazo("d", ease(u_(t, .2, 1.3)), 560), 540, 870, 1.0, 0); titulo(b, "EN LA ARENA\n*O EN HARINA", t, 0, 290, 90)
def S28(b, t, T):
    bg(b, "menta", t); per(b, "n", "feliz", t, 540, 1110, .85); titulo(b, "SIENTE EL\n*MOVIMIENTO", t, 0, 290, 100); estrellas(b, t, 1.2, (540, 640), 5, 380)
def S29(b, t, T):
    bg(b, "cielo", t); put(b, A.bombilla(380), 540, 760 + bob(t, 8, 1.2), pop(t, .1, .4), 0); put(b, A.corazon(180), 790, 640, pop(t, .8), 8); titulo(b, "SU CUERPO\n*RECUERDA", t, 0, 290, 100)
def S30(b, t, T):
    bg(b, "crema", t); put(b, A.calendario(600, 520, 5), 540, 760, pop(t, .1, .4), -3); titulo(b, "PASADOS LOS\n*7 U 8 AÑOS", t, 0, 290, 96)
def S31(b, t, T):
    bg(b, "alerta", t); put(b, tarjeta("b"), 300, 830, pop(t, 0, .3) * .8, -4); put(b, tarjeta("d", espejo=True), 780, 830, pop(t, .3, .3) * .8, 4); titulo(b, "SIGUE HACIÉNDOLO\n*MUCHO", t, 0, 290, 80)
def S32(b, t, T):
    bg(b, "lila", t); per(b, "n", "triste", t, 540, 1120, .8); titulo(b, "ADEMÁS LE\n*CUESTA LEER", t, 0, 290, 100)
def S33(b, t, T):
    bg(b, "menta", t); per(b, "m", "feliz", t, 540, 1120, .85, shirt=(60, 160, 110)); titulo(b, "CONSÚLTALO CON\n*SU MAESTRA", t, 0, 290, 90); put(b, A.check(190), 840, 780, pop(t, .7), 6)
def S34(b, t, T):
    bg(b, "cielo", t); numero(b, 5, t, 540, 640, .8); titulo(b, "NIÑO DE 5 AÑOS", t, 0, 930, 90); per(b, "n", "feliz", t, 540, 1330, .55)
def S35(b, t, T):
    bg(b, "menta", t); put(b, A.sello("NADA RARO", 800, 270, A.VERDE, 140), 540, 760, pop(t, .05, .3), -4); put(b, A.check(260), 540, 1110, pop(t, .5, .4), 6)
def S36(b, t, T):
    bg(b, "amarillo", t); per(b, "n", "orgulloso", t, 540, 1130, .85); titulo(b, "ESTÁ\n*APRENDIENDO", t, 0, 290, 110); estrellas(b, t, .3, (540, 560), 6, 380)
def S37(b, t, T):
    bg(b, "cielo", t); titulo(b, "DÉJALO EN\n*COMENTARIOS", t, 0, 300, 100); per(b, "m", "feliz", t, 540, 1380, .8)
def S38(b, t, T):
    bg(b, "amarillo", t); frase(b, t, "¿Qué letra escribe\nal revés tu hijo?", 540, 640, 76, .1, tail="left"); put(b, tarjeta("b"), 300, 1000, pop(t, .5, .3) * .8, -4); put(b, tarjeta("d", espejo=True), 780, 1000, pop(t, .8, .3) * .8, 4)


def _b(i): return ta(i) - 0.04
SHOTS = [
    (0, S00, [('brillo', 0.5, -10)], True),
    (8, S01, [('golpe', 0.1, -10)], False),
    (11, S02, [('brillo', 0.3, -10)], False),
    (20, S03, [('golpe', 0.05, -10)], False),
    (26, S04, [('golpe', 0.3, -10)], False),
    (31, S05, [('brillo', 0.3, -10)], False),
    (40, S06, [('golpe', 0.1, -10)], False),
    (44, S07, [('golpe', 0.1, -10)], False),
    (49, S08, [('lapiz', 0.3, -10)], False),
    (53, S09, [('brillo', 0.3, -10)], False),
    (62, S10, [('golpe', 0.1, -10)], False),
    (65, S11, [('brillo', 0.3, -10)], False),
    (75, S12, [('golpe', 0.1, -10)], False),
    (82, S13, [('golpe', 0.05, -10)], False),
    (86, S14, [('brillo', 0.4, -10)], False),
    (92, S15, [('golpe', 0.1, -10)], False),
    (98, S16, [('rasgar', 0.5, -10)], False),
    (100, S17, [('golpe', 0.1, -10)], False),
    (104, S18, [('golpe', 0.2, -10)], False),
    (109, S19, [('golpe', 0.4, -10)], False),
    (116, S20, [('resultado', 0.3, -10)], False),
    (119, S21, [('brillo', 0.3, -10)], False),
    (125, S22, [('lapiz', 0.4, -10)], False),
    (135, S23, [('lapiz', 0.4, -10)], False),
    (145, S24, [('brillo', 0.4, -10)], False),
    (153, S25, [('brillo', 0.1, -10)], False),
    (158, S26, [('brillo', 0.5, -10)], False),
    (169, S27, [('lapiz', 0.3, -10)], False),
    (175, S28, [('brillo', 0.3, -10)], False),
    (182, S29, [('brillo', 0.3, -10)], False),
    (187, S30, [('golpe', 0.1, -10)], False),
    (194, S31, [('golpe', 0.2, -10)], False),
    (200, S32, [('golpe', 0.2, -10)], False),
    (203, S33, [('resultado', 0.5, -10)], False),
    (207, S34, [('golpe', 0.1, -10)], False),
    (216, S35, [('resultado', 0.3, -10)], False),
    (220, S36, [('brillo', 0.2, -10)], False),
    (222, S37, [('golpe', 0.1, -10)], False),
    (226, S38, [('brillo', 0.3, -10)], False),
]
SHOTS = [(0.0 if i == 0 else _b(w), f, s, n) for i, (w, f, s, n) in enumerate(SHOTS)]
for i in range(1, len(SHOTS)): assert SHOTS[i][0] > SHOTS[i - 1][0], (i, SHOTS[i][0], SHOTS[i - 1][0])
BOUNDS = [(SHOTS[i][0], SHOTS[i + 1][0] if i + 1 < len(SHOTS) else TOTAL) for i in range(len(SHOTS))]


# ---------------------------------------------------------------- subtítulos palabra a palabra (zona segura: y ~1340)
def chunks():
    out, cur = [], []
    for i, (w, a, e) in enumerate(WORDS):
        cur.append(i)
        if sum(len(WORDS[x][0]) + 1 for x in cur) >= 16 or len(cur) >= 3 or w.endswith((".", ",", "?", "!", ":", "…")):
            out.append(cur); cur = []
    if cur: out.append(cur)
    return out
CH = chunks()
def subtitulo(b, T):
    for ci, g in enumerate(CH):
        a = WORDS[g[0]][1]; e = WORDS[CH[ci + 1][0]][1] if ci + 1 < len(CH) else TOTAL
        e = min(e, WORDS[g[-1]][2] + .5)
        if a - .03 <= T < e: break
    else: return
    size = 84; f = A.font("baloo", size); ws = [WORDS[i][0].upper().rstrip(",.:…") if False else WORDS[i][0].upper() for i in g]
    sp = 22; total = sum(f.getlength(w) for w in ws) + sp * (len(ws) - 1)
    if total > 900: size = int(84 * 900 / total); f = A.font("baloo", size); total = sum(f.getlength(w) for w in ws) + sp * (len(ws) - 1)
    d = ImageDraw.Draw(b); x = 540 - total / 2; y = 1330; k = pop(T, a, .12); dy = (1 - k) * 18
    for i, w in zip(g, ws):
        cur = WORDS[i][1] - .02 <= T < WORDS[i][2] + .02 or (i == g[-1] and T >= WORDS[i][1])
        d.text((x, y + dy), w, font=f, fill=A.AMA if cur else (255, 255, 255), stroke_width=12, stroke_fill=A.OL, anchor="lm"); x += f.getlength(w) + sp

# ---------------------------------------------------------------- fotograma
def shot_at(T):
    for i, (a, e) in enumerate(BOUNDS):
        if a <= T < e: return i
    return len(SHOTS) - 1

def frame(T):
    i = shot_at(T); a, fn, sfx, nw = SHOTS[i]; e = BOUNDS[i][1]; t = T - a; SHK[0] = SHK[1] = 0.0
    b = Image.new("RGB", (W, H), (255, 244, 222)); fn(b, t, e - a)
    z = 1.03 + .045 * clamp(t / max(e - a, .1)); cw, ch = W / z, H / z
    x0 = max(0.0, min(W - cw, (W - cw) / 2 + SHK[0])); y0 = max(0.0, min(H - ch, (H - ch) / 2 + SHK[1]))
    b = b.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch)); subtitulo(b, T)
    return b

def render_scene(i):
    a, fn, sfx, nw = SHOTS[i]; e = BOUNDS[i][1]; f0, f1 = round(a * FPS), round(e * FPS)
    out = os.path.join(TMP, f"s{i:02d}.mp4"); tmp = os.path.join(TMP, f"s{i:02d}.part.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                          "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
    for f in range(f0, f1): p.stdin.write(frame(f / FPS).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out)
    return i


# ---------------------------------------------------------------- audio
def golpe(path):
    if not os.path.exists(path):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "aevalsrc=sin(2*PI*(60+90*exp(-t*22))*t)*exp(-t*8)+0.25*random(0)*exp(-t*60):d=0.6:s=48000", "-ac", "1", path], check=True)
    return path

def mix(out):
    vw = os.path.join(TMP, "voz.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(DESC, "voz.mp3"), "-af",
                    f"aresample=48000,apad,atrim=0:{TOTAL:.2f},acompressor=threshold=-18dB:ratio=3:attack=5:release=120,loudnorm=I=-15:TP=-1.5:LRA=9,aresample=48000",
                    "-ac", "1", "-ar", "48000", vw], check=True)
    mw = os.path.join(TMP, "musica.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", os.path.join(SFXD, "musica.mp3"), "-i", vw, "-filter_complex",
                    f"[0:a]aresample=48000,atrim=0:{TOTAL:.2f},loudnorm=I=-28:TP=-8,aresample=48000,aformat=channel_layouts=mono[m0];[1:a]apad,atrim=0:{TOTAL:.2f}[key];"
                    "[m0][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[mus]", "-map", "[mus]", "-ar", "48000", "-ac", "1", mw], check=True)
    efx = []
    for (a, fn, sfx, nw), (s0, s1) in zip(SHOTS, BOUNDS):
        if a > 0 and not nw: efx.append(("whoosh", a - .05, -10))
        for n, dt, db in sfx: efx.append((n, a + dt, db))
    ins, flt, parts = ["-i", vw, "-i", mw], [f"[0:a]apad,atrim=0:{TOTAL:.2f}[v]", f"[1:a]apad,atrim=0:{TOTAL:.2f}[m]"], ["[v]", "[m]"]
    for j, (n, t, db) in enumerate(efx):
        p = golpe(os.path.join(TMP, "golpe.wav")) if n == "golpe" else os.path.join(SFXD, n + ".mp3"); ins += ["-i", p]; ms = max(0, int(t * 1000))
        trim = ",atrim=0:2.2" if n == "lapiz" else (",atrim=0:2.5" if n in ("rasgar", "borrar", "resultado", "brillo") else "")
        flt.append(f"[{j + 2}:a]aresample=48000{trim},loudnorm=I=-25:TP=-6,aresample=48000,volume={db}dB,adelay={ms}|{ms},apad[s{j}]"); parts.append(f"[s{j}]")
    flt.append("".join(parts) + f"amix=inputs={len(parts)}:normalize=0:duration=longest,alimiter=limit=0.95,apad,atrim=0:{TOTAL:.2f}[mx]")
    wav = os.path.join(TMP, "mezcla.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(flt), "-map", "[mx]", "-ac", "2", wav], check=True)
    lst = os.path.join(TMP, "list.txt")
    with open(lst, "w") as f:
        for i in range(len(SHOTS)): f.write(f"file 's{i:02d}.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium",
                    "-crf", "23", "-maxrate", "2200k", "-bufsize", "4400k", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-t", f"{TOTAL:.2f}", "-movflags", "+faststart", out], check=True)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "info"
    if cmd == "info":
        print("TOTAL %.2f s, escenas %d" % (TOTAL, len(SHOTS)))
        for i, (a, e) in enumerate(BOUNDS): print(i, SHOTS[i][1].__name__, "%.2f-%.2f (%.1fs)" % (a, e, e - a))
    elif cmd == "still":
        for tt in sys.argv[2].split(","): frame(float(tt)).save(f"/tmp/still_{float(tt):.1f}.png")
    elif cmd == "scenes":
        todo = [int(x) for x in sys.argv[2:]] or [i for i in range(len(SHOTS)) if not os.path.exists(os.path.join(TMP, f"s{i:02d}.mp4"))]
        with Pool(2) as p:
            for i in p.imap_unordered(render_scene, todo): print("escena", i, flush=True)
    elif cmd == "mix":
        mix(sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "tip_carta.mp4"))

