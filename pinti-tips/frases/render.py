"""Tip «3 frases que apagan a tu hijo» · @escribirconpinti. Tiempos por palabra (Whisper), escenas de ~2-3 s con movimiento,
todo visible desde el frame 0, subtítulos palabra a palabra, zona segura TikTok.  Uso: python3 render.py info | still 1,2 | scenes [i..] | mix [out.mp4]"""
import os, sys, json, math, random, subprocess
from functools import lru_cache
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageOps
import art as A

HERE = os.path.dirname(os.path.abspath(__file__))
DESC = os.path.join(HERE, "..", "..", "descargas", "frases3")
SFXD = os.path.join(HERE, "..", "..", "descargas", "mateo_sfx")
TMP = os.path.join(HERE, "tmp2"); os.makedirs(TMP, exist_ok=True)
W, H, FPS = 1080, 1920, 30
J = json.load(open(os.path.join(DESC, "voz.json"), encoding="utf-8"))
def ta(i): return J[i]["inicio"]
TOTAL = J[-1]["fin"] + 0.6
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

def titulo(base, txt, t, t0=0.0, y=330, size=128, fill=(255, 255, 255), amarillo=None, d=.3):
    """Titular de dos líneas máx.: la línea marcada con * va en amarillo."""
    lines = txt.split("\n"); n = len(lines)
    for i, l in enumerate(lines):
        col = A.AMA if l.startswith("*") else fill
        im = A.texto(l.lstrip("*"), size, col, 12)
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

def reloj(size=420):
    im = A.canvas(size, size); d = ImageDraw.Draw(im); A.ell(d, (10, 10, size - 10, size - 10), (255, 255, 255), A.OL, 12)
    c = size / 2
    for k in range(12):
        a = k * math.pi / 6; A.line(d, [(c + math.sin(a) * c * .78, c - math.cos(a) * c * .78), (c + math.sin(a) * c * .9, c - math.cos(a) * c * .9)], A.OL, 8)
    A.ell(d, (c - 14, c - 14, c + 14, c + 14), A.OL, None); return A.fin(im).copy()
_RL = {}
def reloj_vivo(b, x, y, s, t, v=1.0):
    if "r" not in _RL: _RL["r"] = reloj(420)
    im = _RL["r"].copy(); d = ImageDraw.Draw(im); c = 210; a1 = t * 6 * v; a2 = t * .5 * v
    d.line((c, c, c + math.sin(a1) * 150, c - math.cos(a1) * 150), fill=A.ROJO, width=11)
    d.line((c, c, c + math.sin(a2) * 100, c - math.cos(a2) * 100), fill=A.OL, width=14); put(b, im, x, y, s, 0)

def frase(b, t, txt, x, y, size, t0=.0, col=(255, 255, 255), tail="left", rot=-2):
    put(b, A.globo(txt, size, col, tail), x, y, pop(t, t0, .32), rot + bob(t, 2))

def numero(b, n, t, x=540, y=900, s=1.0, color=None):
    im = A.canvas(560, 560); d = ImageDraw.Draw(im); A.ell(d, (20, 20, 540, 540), color or A.AMA, A.OL, 14); im = A.fin(im).copy()
    ImageDraw.Draw(im).text((280, 300), str(n), font=A.font("anton", 380), fill=A.OL, anchor="mm")
    put(b, im, x, y + bob(t, 8, 1.2), pop(t, 0, .35) * s, -5 + bob(t, 2, 1))

def S00(b, t, T):  # gancho: todo visible desde el frame 0
    bg(b, "alerta", t); titulo(b, "3 FRASES QUE\n*APAGAN A TU HIJO", t, -1, 290, 96)
    put(b, A.bombilla(420), 540, 640 + bob(t, 6, 1.2), 1.0, 0); per(b, "n", "triste", t, 540, 1040, .72)
    put(b, A.xmark(200), 820, 660, pop(t, .5), 8)
def S01(b, t, T):
    bg(b, "noche", t); titulo(b, "SIN QUERER\n*LE APAGAN LAS GANAS", t, 0, 290, 80, (255, 236, 160))
    put(b, A.bateria(340, .08), 540, 720, pop(t, .2, .4), bob(t, 3, 1.5)); per(b, "n", "cansado", t, 540, 1080, .62)
def S02(b, t, T):
    bg(b, "lila", t); per(b, "m", "asombro", t, 540, 1010, 1.0); titulo(b, "SEGURO QUE\n*YA DIJISTE ALGUNA", t, 0, 290, 78)
    put(b, A.texto("¿YO?", 170, A.AMA, 12), 830, 700 + bob(t, 8, 1.6), pop(t, .8, .3), 8)
def S03(b, t, T):
    bg(b, "amarillo", t); numero(b, 1, t, 540, 820); titulo(b, "FRASE", t, 0, 330, 140); per(b, "m", "preocupado", t, 540, 1190, .45)
def S04(b, t, T):
    bg(b, "alerta", t); per(b, "m", "neutral", t, 400, 1120, .8); frase(b, t, "Eso está mal,\nbórralo y hazlo\notra vez.", 540, 640, 76, .05)
    put(b, A.xmark(230), 830, 1000, pop(t, 2.0, .3), 0)
def S05(b, t, T):
    bg(b, "crema", t); h = A.hoja().copy(); h.alpha_composite(A.letra(("mi perro", "salta"), "fea", 4, 150)); put(b, h, 540, 880 + bob(t, 6), .9, -4)
    k = ease(u_(t, .5, .5)); ImageDraw.Draw(b).line((250, 700, 250 + 560 * k, 1000), fill=A.ROJO, width=30)
    put(b, A.sello("PARECE AYUDAR", 760, 210, A.AMA, 100), 540, 380, pop(t, .15, .3), -3)
def S06(b, t, T):
    bg(b, "cielo", t); per(b, "n", "triste", t, 540, 1030, .85)
    for i, (xx, yy) in enumerate(((220, 640), (860, 620), (800, 940), (250, 930))): put(b, A.xmark(150), xx, yy + bob(t, 7, 1.4, i), pop(t, .3 + i * .45, .3), -10 + i * 8)
    titulo(b, "TODO LO QUE HACE\n*ES UN ERROR", t, 0, 290, 76)
def S07(b, t, T):
    bg(b, "menta", t); titulo(b, "MEJOR DILE:", t, 0, 280, 120); per(b, "m", "feliz", t, 400, 1130, .8)
    frase(b, t, "Mira, esta letra\nte quedó muy bien.", 560, 600, 70, 1.1, (255, 255, 255)); put(b, A.check(210), 830, 1000, pop(t, 1.9), 6)
def S08(b, t, T):
    bg(b, "durazno", t); per(b, "n", "feliz", t, 400, 1130, .75); frase(b, t, "¿Probamos otra\nigual?", 580, 620, 80, .1, tail="left", rot=2)
    put(b, A.lapiz(440), 820, 1180, pop(t, .5, .3), -8 + bob(t, 2, 2))
def S09(b, t, T):
    bg(b, "amarillo", t); numero(b, 2, t, 540, 820); titulo(b, "FRASE", t, 0, 330, 140); per(b, "m", "preocupado", t, 540, 1190, .45)
def S10(b, t, T):
    bg(b, "alerta", t); per(b, "m", "neutral", t, 340, 1130, .75); put(b, A.kid("orgulloso"), 840, 1130 + bob(t, 6), .5, 0)
    frase(b, t, "Mira cómo\nescribe tu primo.", 560, 620, 76, .05)
def S11(b, t, T):
    bg(b, "cielo", t); per(b, "n", "triste", t, 540, 1040, .8); put(b, A.sello("COMPARAR", 700, 230, A.ROJO, 120), 540, 360, pop(t, .15, .3), -3)
    put(b, A.kid("orgulloso"), 860, 800, pop(t, .6, .3) * .45, 0)
def S12(b, t, T):
    bg(b, "noche", t); per(b, "n", "triste", t, 540, 1100, .62, 0); titulo(b, "NUNCA\n*LLEGA", t, 0, 330, 140, (255, 236, 160))
    put(b, A.flecha_curva(260, A.ROJO), 820, 760, pop(t, .8), 100)
def S13(b, t, T):
    bg(b, "lila", t); put(b, A.calendario(600, 520, 4), 540, 700, pop(t, .15, .4), -3); titulo(b, "CADA NIÑO\n*SU RITMO", t, 0, 290, 96)
    per(b, "n", "neutral", t, 540, 1220, .42)
def S14(b, t, T):
    bg(b, "menta", t); per(b, "n", "feliz", t, 540, 1040, .85); put(b, A.check(260), 830, 640, pop(t, .5), 6); titulo(b, "EL TUYO\n*ESTÁ AVANZANDO", t, 0, 290, 84)
def S15(b, t, T):
    bg(b, "menta", t); titulo(b, "MEJOR DILE:", t, 0, 280, 120); per(b, "m", "feliz", t, 400, 1130, .8)
    frase(b, t, "Hoy escribes\nmejor que ayer.", 560, 600, 76, 1.0); put(b, A.estrella(190), 830, 980, pop(t, 1.6), 10)
def S16(b, t, T):
    bg(b, "durazno", t); per(b, "n", "orgulloso", t, 540, 1030, .85); frase(b, t, "Lo veo.", 540, 500, 120, .1, tail="left"); estrellas(b, t, .4, (540, 560), 6, 380)
def S17(b, t, T):
    bg(b, "amarillo", t); numero(b, 3, t, 540, 820); titulo(b, "FRASE", t, 0, 330, 140); per(b, "m", "preocupado", t, 540, 1190, .45)
def S18(b, t, T):
    bg(b, "alerta", t); shake(t, .05, 10); per(b, "m", "cansado", t, 360, 1130, .8); frase(b, t, "¡Date prisa!\nQue no\nterminamos.", 580, 640, 80, .05)
def S19(b, t, T):
    bg(b, "cielo", t); per(b, "n", "neutral", t, 540, 1060, .78); put(b, A.bombilla(300), 820, 640 + bob(t, 6, 1.4), pop(t, .5, .4), 0)
    titulo(b, "MUCHA\n*CONCENTRACIÓN", t, 0, 290, 92)
def S20(b, t, T):
    bg(b, "alerta", t); reloj_vivo(b, 540, 640, 1.0, t, 3.0)
    h = A.hoja().copy(); h.alpha_composite(A.letra(("la luna",), "fea", 8, 140)); put(b, h, 540, 1150 + bob(t, 6), .72, -6); titulo(b, "LETRAS PEOR", t, 0, 300, 100)
def S21(b, t, T):
    bg(b, "noche", t); per(b, "n", "asombro", t, 540, 1030, .85); put(b, A.texto("?!", 200, A.AMA, 12), 820, 640 + bob(t, 8, 1.8), pop(t, .5, .3), 8)
    titulo(b, "MIEDO A\n*EQUIVOCARSE", t, 0, 290, 96, (255, 236, 160))
def S22(b, t, T):
    bg(b, "menta", t); titulo(b, "MEJOR DILE:", t, 0, 280, 120); per(b, "m", "feliz", t, 400, 1130, .8)
    frase(b, t, "Tómate tu tiempo,\nyo espero.", 560, 600, 70, 1.1); put(b, A.check(210), 830, 1000, pop(t, 2.2), 6)
def S23(b, t, T):
    bg(b, "durazno", t); per(b, "m", "feliz", t, 360, 1080, .75); per(b, "n", "feliz", t, 760, 1140, .6); put(b, A.corazon(240), 560, 560 + bob(t, 6, 2), pop(t, .2, .4), 8)
def S24(b, t, T):
    bg(b, "crema", t); titulo(b, "NINGUNA ES\n*MALA INTENCIÓN", t, 0, 290, 90); per(b, "m", "preocupado", t, 540, 1040, .9); put(b, A.corazon(200), 820, 700, pop(t, .6), 8)
def S25(b, t, T):
    bg(b, "noche", t); per(b, "m", "cansado", t, 540, 1050, .9); titulo(b, "LAS DECIMOS\n*CANSADOS", t, 0, 290, 96, (255, 236, 160))
    for i in range(3): put(b, A.texto("Z", 110 + i * 30, (255, 255, 255), 8), 770 + i * 70, 800 - i * 100 - (t * 40 % 40), pop(t, .5 + i * .35), 8)
def S26(b, t, T):
    bg(b, "alerta", t); reloj_vivo(b, 540, 760, 1.2, t, 3.0); titulo(b, "CON PRISA", t, 0, 380, 120)
def S27(b, t, T):
    bg(b, "cielo", t); per(b, "n", "triste", t, 540, 1030, .85); put(b, A.sello("JUZGADO", 720, 230, A.ROJO, 130), 540, 400, pop(t, .5, .3), -4); put(b, A.ojo(260), 820, 700, pop(t, .2, .3), 0)
def S28(b, t, T):
    bg(b, "crema", t); escritorio(b); per(b, "n", "triste", t, 400, 990, .8)
    put(b, A.lapiz(480), 800 + t * 200, 1235 + t * 30, 1.0, -6); titulo(b, "EMPIEZA A\n*EVITARLO", t, 0, 290, 96)
def S29(b, t, T):
    bg(b, "menta", t); per(b, "m", "feliz", t, 360, 1050, .78); per(b, "n", "feliz", t, 760, 1110, .62); put(b, A.corazon(220), 560, 560 + bob(t, 6, 2), pop(t, .3, .4), 8)
    titulo(b, "ACOMPAÑADO", t, 0, 290, 100)
def S30(b, t, T):
    bg(b, "amarillo", t); hoja_escribiendo(b, 560, 900, .95, -4, t, .1, 1.3, ["Quiero", "escribir"], "limpia", True, .6); titulo(b, "QUIERE\n*ESCRIBIR MÁS", t, 0, 290, 92)
def S31(b, t, T):
    bg(b, "cielo", t); titulo(b, "CAMBIA SOLO\n*UNA FRASE", t, 0, 300, 100); numero(b, 1, t, 540, 860, .85); per(b, "m", "feliz", t, 540, 1290, .35)
def S32(b, t, T):
    bg(b, "amarillo", t); put(b, A.sello("SOLO UNA", 760, 260, A.VERDE, 150), 540, 760, pop(t, .05, .3), -4); estrellas(b, t, .3, (540, 760), 6, 420)
def S33(b, t, T):
    bg(b, "lila", t); titulo(b, "EN UNA\n*SEMANA", t, 0, 290, 120); put(b, A.calendario(640, 560, 1 + int(t * 3.5) % 8), 540, 820, pop(t, .1, .4), -3); put(b, A.check(190), 800, 1170, pop(t, 1.2, .35), 6)
def S35(b, t, T):
    bg(b, "amarillo", t)
    for i in range(3): numero(b, i + 1, t - i * .22, 230 + i * 310, 820, .42)
    put(b, A.texto("¿CUÁL?", 190, A.ROJO, 14), 540, 1080 + bob(t, 6, 1.5), pop(t, .5, .3), -4)
def S36(b, t, T):
    bg(b, "amarillo", t); titulo(b, "SÍGUEME", t, 0, 300, 150); put(b, A.boton_seguir(700), 540, 720, pop(t, .2, .4) * (1 + .03 * math.sin(t * 6)), bob(t, 1.5, 1.2))
    put(b, A.texto("@escribirconpinti", 72, (255, 255, 255), 9, "baloo"), 540, 900, pop(t, .5))
def S37(b, t, T):
    bg(b, "cielo", t); titulo(b, "1 TIP\n*CADA DÍA", t, 0, 290, 140); per(b, "m", "feliz", t, 540, 1020, .85); estrellas(b, t, .4, (540, 520), 5, 380)
def S38(b, t, T):
    bg(b, "menta", t); hoja_escribiendo(b, 560, 880, .95, -4, t, .2, 2.6, ["Me gusta", "escribir"], "limpia", True, .6); titulo(b, "TU HIJO\n*ESCRIBE MEJOR", t, 0, 290, 92); estrellas(b, t, 3.0, (540, 880), 6, 430)


def H00(b, t, T):  # gancho nuevo: condición + prohibición, visible desde el frame 0
    bg(b, "alerta", t); titulo(b, "SI TU HIJO ESTÁ\nAPRENDIENDO A ESCRIBIR", t, -1, 250, 74)
    per(b, "n", "triste", t, 540, 1090, .85); put(b, A.sello("NO LE DIGAS ESTO", 960, 240, A.ROJO, 110), 540, 640 + bob(t, 4, 1.5), 1.0, -4)
def H01(b, t, T):
    bg(b, "amarillo", t); titulo(b, "NO LE DIGAS\n*ESTAS 3 FRASES", t, 0, 290, 100)
    for i in range(3): numero(b, i + 1, t - i * .25, 230 + i * 310, 820, .42)
    per(b, "m", "preocupado", t, 540, 1190, .5)

def S34(b, t, T):
    bg(b, "cielo", t); titulo(b, "DIME EN\n*COMENTARIOS", t, 0, 300, 100); frase(b, t, "¿Cuál te decían\na ti de niña?", 540, 760, 76, .35)
    put(b, A.flecha_curva(300, A.ROJO), 800, 1110, pop(t, 1.0), 90)

def _b(i): return ta(i) - 0.04
SHOTS = [
    (0, H00, [("brillo",.5,-9)], True),
    (7, H01, [("golpe",.1,-9)], False),
    (13, S02, [("brillo",.3,-11)], False),
    (19, S01, [("golpe",.1,-9)], False),
    (28, S03, [('golpe', 0.1, -9)], False),
    (30, S04, [('brillo', 0.3, -10)], False),
    (38, S05, [('lapiz', 0.5, -9)], False),
    (44, S06, [('golpe', 0.4, -10)], False),
    (53, S07, [('resultado', 1.2, -12)], False),
    (62, S08, [('brillo', 0.5, -10)], False),
    (65, S09, [('golpe', 0.1, -9)], False),
    (67, S10, [('brillo', 0.3, -10)], False),
    (72, S11, [('golpe', 0.3, -10)], False),
    (78, S12, [], False),
    (82, S13, [('brillo', 0.4, -11)], False),
    (88, S14, [('resultado', 0.5, -12)], False),
    (93, S15, [('resultado', 1.2, -12)], False),
    (100, S16, [('brillo', 0.2, -10)], False),
    (102, S17, [('golpe', 0.1, -9)], False),
    (104, S18, [('golpe', 0.1, -9)], False),
    (109, S19, [('brillo', 0.4, -11)], False),
    (115, S20, [('rasgar', 0.6, -12)], False),
    (122, S21, [('golpe', 0.4, -10)], False),
    (129, S22, [('resultado', 1.4, -12)], False),
    (134, S23, [('brillo', 0.2, -10)], False),
    (136, S24, [], False),
    (142, S25, [], False),
    (145, S26, [], False),
    (149, S27, [('golpe', 0.5, -10)], False),
    (158, S28, [('lapiz', 0.3, -10)], False),
    (161, S29, [('brillo', 0.4, -10)], False),
    (167, S30, [('lapiz', 0.2, -8)], False),
    (170, S31, [('brillo', 0.3, -10)], False),
    (179, S32, [('brillo', 0.1, -9)], False),
    (181, S33, [('lapiz', 0.4, -10)], False),
    (189, S34, [('brillo', 0.3, -11)], False),
    (194, S35, [('golpe', 0.2, -10)], False),
    (205, S36, [('brillo', 0.25, -9)], False),
    (207, S37, [('resultado', 0.1, -12)], False),
    (215, S38, [('lapiz', 0.3, -8)], False),
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

