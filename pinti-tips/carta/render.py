"""Tip-historia «Mi hija de 5 años me dejó esta nota» · @escribirconpinti. Tiempos por palabra (Whisper), escenas de ~2-3 s con movimiento,
todo visible desde el frame 0, subtítulos palabra a palabra, zona segura TikTok.  Uso: python3 render.py info | still 1,2 | scenes [i..] | mix [out.mp4]"""
import os, sys, json, math, random, subprocess
from functools import lru_cache
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageOps
import art as A

HERE = os.path.dirname(os.path.abspath(__file__))
DESC = os.path.join(HERE, "..", "..", "descargas", "carta_tip")
SFXD = os.path.join(HERE, "..", "..", "descargas", "mateo_sfx")
TMP = os.path.join(HERE, "tmp"); os.makedirs(TMP, exist_ok=True)
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

def put_tip(base, im, tx, ty, s=1.0):      # pone la punta del lápiz (600, 900 de la capa) en (tx, ty)
    if s != 1: im = im.resize((int(im.width * s), int(im.height * s)), Image.BILINEAR)
    base.paste(im, (int(tx - 600 * s), int(ty - 900 * s)), im)

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
    put(b, im, x, y + bob(t, 7), s, rot + bob(t, 1.5, .8))

def nota(b, t, x, y, s, rot, lines=("Mamá, no", "estés triste.", "Te quiero."), modo="fea", seed=7, k=1.0, cinta=True):
    h = A.hoja().copy(); h.alpha_composite(A.letra(tuple(lines), modo, seed, 112)); put(b, h, x, y + bob(t, 6, .9), s * k, rot + bob(t, 1.2, .7))
    if cinta:
        tp = Image.new("RGBA", (230, 70), (255, 226, 120, 215)); put(b, tp, x, y - 450 * s + bob(t, 6, .9), k, rot * .5)

def luz_dia(b, t): bg(b, "amarillo", t)

def S00(b, t, T):  # gancho: todo visible en el frame 0
    bg(b, "durazno", t); titulo(b, "MI HIJA DE 5 AÑOS\n*ME DEJÓ ESTA NOTA", t, -1, 300, 88)
    nota(b, t, 540, 940, .92, -5); put(b, A.corazon(170), 880, 560, pop(t, 1.2), 10 + bob(t, 5, 2))
def S01(b, t, T):
    bg(b, "lila", t); titulo(b, "¿CÓMO APRENDIÓ\n*A ESCRIBIRLO?", t, 0, 330, 90); per(b, "m", "asombro", t, 540, 1010, 1.0, 0)
    for i, (xx, yy) in enumerate(((220, 680), (860, 640), (800, 900))): put(b, A.texto("?", 190, A.AMA, 12), xx, yy + bob(t, 10, 1.6, i), pop(t, .4 + i * .3), -10 + i * 10)
def S02(b, t, T):
    bg(b, "amarillo", t); put(b, A.sol(520), 800, 520 + bob(t, 8, .8), 1.0, t * 8); titulo(b, "ESTA MAÑANA", t, 0, 300, 110)
    put(b, A.cama(), 540, 1010, 1.0, 0); per(b, "m", "cansado", t, 330, 880, .62, -8)
def S03(b, t, T):
    bg(b, "crema", t); put(b, A.puerta(560, 900), 540, 790, 1.0, 0); titulo(b, "UN PAPEL\n*EN LA PUERTA", t, .05, 300, 100)
    nota(b, t, 540, 780, .5, -6, ("Mamá, no", "estés triste.", "Te quiero."), "fea", 7, pop(t, .4, .35)); put(b, A.flecha_curva(260, A.ROJO), 860, 1000, pop(t, 1.2), 100)
def S04(b, t, T):
    bg(b, "cielo", t); nota(b, t, 540, 830, 1.0, -9 + 4 * math.sin(t * 2)); titulo(b, "LETRAS GRANDES\n*Y TORCIDAS", t, 0, 290, 86)
def S05(b, t, T):
    bg(b, "alerta", t); titulo(b, "UNA E\n*AL REVÉS", t, 0, 300, 120)
    put(b, ImageOps.mirror(A.texto("E", 700, A.TINTA, 0, "hand")), 540, 860, pop(t, .15, .35), -6)
    k = ease(u_(t, .6, .35)); d = ImageDraw.Draw(b); r = 300 * k; d.ellipse((540 - r, 860 - r, 540 + r, 860 + r), outline=A.ROJO, width=18)
def S06(b, t, T):
    bg(b, "menta", t); nota(b, t, 400, 880, .75, -5); put(b, A.check(420), 780, 820, pop(t, .35, .4), 6); titulo(b, "SE ENTENDÍA\n*PERFECTO", t, 0, 290, 100)
def S07(b, t, T):
    bg(b, "crema", t); titulo(b, "DECÍA:", t, 0, 290, 130); hoja_escribiendo(b, 580, 870, .95, -4, t, .15, 1.8, ["Mamá,", "no estés", "triste."], "fea", True, .6, 7)
def S08(b, t, T):
    bg(b, "durazno", t); nota(b, t, 540, 800, .9, 4, ("Te quiero.",), "fea", 9, 1.0, False); put(b, A.corazon(400), 540, 1090, pop(t, .2, .45), 0 + bob(t, 5, 2)); estrellas(b, t, .5, (540, 820), 6, 420)
def S09(b, t, T):
    bg(b, "menta", t); per(b, "m", "preocupado", t, 380, 980, .95); nota(b, t, 790, 820, .55, 7, cinta=False)
    put(b, A.sello("5 VECES", 620, 240, A.ROJO, 150), 540, 420, pop(t, .2, .35), -4)
def S10(b, t, T):
    bg(b, "cielo", t); per(b, "m", "asombro", t, 540, 980, 1.0); titulo(b, "SIN\n*RESPIRAR", t, 0, 310, 130)
def S11(b, t, T):
    bg(b, "noche", t); put(b, A.luna(300), 800, 420 + bob(t, 8, .6), 1.0, 0); titulo(b, "ANOCHE", t, 0, 300, 130, (255, 236, 160))
    put(b, A.cama(), 540, 1050, 1.1, 0); per(b, "n", "cansado", t, 330, 930, .5, -80)
    for i in range(3): put(b, A.texto("Z", 110 + i * 30, (255, 255, 255), 8), 600 + i * 90, 880 - i * 120 - (t * 40 % 40), pop(t, .5 + i * .35), 8)
def S12(b, t, T):
    bg(b, "noche", t); d = ImageDraw.Draw(b); d.rectangle((0, 1000, W, 1250), fill=(120, 96, 140)); d.line((0, 1000, W, 1000), fill=A.OL, width=8)
    per(b, "m", "triste", t, 540, 960, .95)
    for i in range(4):
        tt = (t * 1.4 + i * .25) % 1; put(b, A.gota(70), 350 + (i % 2) * 380, 760 + tt * 300, 1.0 - tt * .3, 0)
    titulo(b, "LLORANDO EN\n*LA COCINA", t, 0, 300, 100, (255, 236, 160))
def S13(b, t, T):
    bg(b, "lila", t); per(b, "m", "preocupado", t, 540, 1000, .9); put(b, A.calendario(640, 560, 9), 540, 520, pop(t, .15, .4) * .85, -3); titulo(b, "SEMANAS", t, .1, 250, 120)
def S14(b, t, T):
    bg(b, "crema", t); escritorio(b); per(b, "m", "neutral", t, 540, 980, .95, shirt=(62, 180, 110))
    put(b, A.globo("Tu hija\nescribe raro", 76, tail="left"), 540, 430, pop(t, .3, .35), -2 + bob(t, 2))
def S15(b, t, T):
    bg(b, "lila", t); titulo(b, "CON LA\n*DERECHA", t, 0, 300, 130)
    put(b, A.mano_der(200), 540 + math.sin(t * 3) * 14, 880, .95 * pop(t, .1, .4), 0); put(b, A.sello("OBLIGADA", 620, 220, A.ROJO, 130), 540, 1180, pop(t, .8, .3), -3)
def S16(b, t, T):
    bg(b, "menta", t); per(b, "n", "feliz", t, 540, 1010, 1.0); put(b, A.sello("ES ZURDA", 640, 240, A.VERDE, 140), 540, 420, pop(t, .15, .3), -3)
def S17(b, t, T):
    bg(b, "alerta", t); titulo(b, "A PUNTO DE\n*OBLIGARLA", t, 0, 290, 100); per(b, "m", "preocupado", t, 400, 1000, 1.0); per(b, "n", "triste", t, 830, 1100, .55)
def S18(b, t, T):
    bg(b, "crema", t); escritorio(b); per(b, "n", "triste", t, 540, 980, .95); put(b, A.pencil_hand(200), 560 + t * 380, 960, .5 * (1 - clamp((t - 1.5) / .7)) + .001, 0)
    put(b, A.xmark(220), 860, 520, pop(t, .5), 0)
def S19(b, t, T):
    bg(b, "alerta", t); shake(t, .05, 18); put(b, A.texto("x2", 560, A.ROJO, 18), 540, 760, pop(t, .05, .35), -5); titulo(b, "DOS VECES", t, .2, 1120, 100)
def S20(b, t, T):
    bg(b, "cielo", t); escritorio(b); per(b, "n", "feliz", t, 540, 980, .95); titulo(b, "SIN QUE\n*NADIE SE LO PIDIERA", t, 0, 290, 84)
    put(b, A.lapiz(520), 760, 1235, pop(t, .5, .3), -6 + bob(t, 2, 2))
def S21(b, t, T):
    bg(b, "menta", t); titulo(b, "CON LA\n*IZQUIERDA", t, 0, 270, 112); hoja_escribiendo(b, 560, 880, .95, -5, t, .15, 1.5, ["Mamá,", "te quiero"], "fea", True, .6, 5)
def S22(b, t, T):
    bg(b, "durazno", t); put(b, A.corazon(520), 540, 700 + bob(t, 8, 2), pop(t, .05, .45), 0); titulo(b, "LO MÁS\n*BONITO", t, .15, 1040, 120); estrellas(b, t, .5, (540, 700), 7, 430)
def S23(b, t, T):
    bg(b, "noche", t); put(b, A.puerta(560, 900, True), 540, 800, 1.0, 0); titulo(b, "FUI A\n*SU CUARTO", t, 0, 290, 100, (255, 236, 160)); put(b, A.mama("preocupado"), 400 + t * 30, 1120, .45, 0)
def S24(b, t, T):
    bg(b, "noche", t); put(b, A.cama(), 540, 1000, 1.15, 0); per(b, "n", "neutral", t, 330, 880, .55, -80); titulo(b, "DESPIERTA", t, 0, 330, 130, (255, 236, 160))
def S25(b, t, T):
    bg(b, "durazno", t); per(b, "n", "feliz", t, 540, 1000, 1.0); titulo(b, "UNA SONRISA\n*MUY CHIQUITA", t, 0, 290, 92); put(b, A.corazon(170), 850, 560, pop(t, .8), 8)
def S26(b, t, T):
    bg(b, "cielo", t); per(b, "n", "orgulloso", t, 540, 1020, 1.0); put(b, A.globo("¡Mami!", 100, tail="left"), 540, 420, pop(t, .25, .35), -2)
def S27(b, t, T):
    bg(b, "amarillo", t); per(b, "n", "orgulloso", t, 540, 1020, 1.0); put(b, A.globo("¡Lo escribí\nyo solita!", 80, tail="left"), 540, 430, pop(t, .1, .35), 2)
def S28(b, t, T):
    bg(b, "menta", t); titulo(b, "LA MANO\n*QUE ME GUSTA", t, 0, 270, 100); put(b, A.pencil_hand(200), 540, 880, .95 * pop(t, .1, .4), bob(t, 3, 2)); put(b, A.corazon(220), 820, 1130, pop(t, .8), 8)
def S29(b, t, T):
    bg(b, "lila", t); per(b, "m", "asombro", t, 540, 1020, 1.0); put(b, A.bombilla(440), 540, 480, pop(t, .3, .4), bob(t, 4, 3)); titulo(b, "ENTENDÍ\n*ALGO", t, 0, 270, 110)
def S30(b, t, T):
    bg(b, "alerta", t); put(b, A.sello("DERECHA", 800, 300, A.ROJO, 190), 540, 760, pop(t, .05, .35), -4); k = u_(t, .6, .25)
    ImageDraw.Draw(b).line((160, 800, 160 + 760 * k, 720), fill=A.ROJO, width=26); put(b, A.xmark(250), 540, 1060, pop(t, 1.0), 0); titulo(b, "NO LE FALTABA", t, 0, 380, 80)
def S31(b, t, T):
    bg(b, "durazno", t); per(b, "m", "feliz", t, 400, 1000, .9); per(b, "n", "orgulloso", t, 760, 1060, .72); put(b, A.corazon(260), 560, 520 + bob(t, 6, 2), pop(t, .3, .4), 8)
    titulo(b, "CONFIAR\n*EN ELLA", t, 0, 270, 110)
def S32(b, t, T):
    bg(b, "crema", t); d = ImageDraw.Draw(b); d.rounded_rectangle((200, 420, 880, 1100), 30, fill=(214, 150, 92), outline=A.OL, width=9)
    nota(b, t, 540, 760, .55, -4, cinta=False, k=1.0); put(b, A.corazon(180), 780, 440, pop(t, .5), 8); titulo(b, "GUARDÉ LA NOTA", t, 0, 300, 90)
def S33(b, t, T):
    bg(b, "cielo", t); escritorio(b); per(b, "n", "feliz", t, 380, 990, .85); put(b, A.lapiz(520), 160 + ease(u_(t, .1, .9)) * 600, 1090, 1.0, -6)
def S34(b, t, T):
    bg(b, "menta", t); put(b, A.pencil_hand(200), 540, 880, .95 * pop(t, 0, .4), bob(t, 3, 2)); put(b, A.sello("IZQUIERDA", 700, 240, A.VERDE, 150), 540, 380, pop(t, .2, .35), -3)
def S35(b, t, T):
    bg(b, "amarillo", t); titulo(b, "ESCRIBE MÁS\n*QUE NUNCA", t, 0, 270, 96)
    for i in range(5):
        h = A.hoja().copy(); h.alpha_composite(A.letra(("mamá",), "fea", i + 1, 120)); put(b, h, 200 + i * 170, 760 + (i % 2) * 90 + (1 - pop(t, .1 + i * .22, .3)) * 400, .42, -8 + i * 4)
    per(b, "n", "orgulloso", t, 540, 1100, .6)
def S36(b, t, T):
    bg(b, "cielo", t); put(b, A.sol(420), 840, 470, 1.0, t * 8); escritorio(b); per(b, "n", "feliz", t, 430, 980, .85); titulo(b, "YA NO SE\n*ESCONDE", t, 0, 270, 100)
    h = A.hoja().copy(); h.alpha_composite(A.letra(("mamá", "sol"), "limpia", 3, 150)); put(b, h, 800, 1000 + bob(t, 6), .5, 6)
def S37(b, t, T):
    bg(b, "amarillo", t); titulo(b, "SI ES ZURDO\n*NO SE LO CAMBIES", t, 0, 300, 90); put(b, A.pencil_hand(200), 540, 880, .9 * pop(t, .15, .4), bob(t, 3, 2)); put(b, A.check(240), 830, 1100, pop(t, .8), 0)
def S38(b, t, T):
    bg(b, "menta", t); hoja_escribiendo(b, 560, 900, .95, -4, t, .05, 1.1, ["a su", "manera"], "limpia", True, .6); titulo(b, "DÉJALO", t, 0, 270, 130)
def S39(b, t, T):
    bg(b, "cielo", t); titulo(b, "CUÉNTAME EN\n*COMENTARIOS", t, 0, 300, 90); put(b, A.globo("¿Zurdo o\ndiestro?", 88, tail="left"), 540, 720, pop(t, .3, .35), -2 + bob(t, 2)); put(b, A.flecha_curva(300, A.ROJO), 800, 1110, pop(t, .9), 90)
def S40(b, t, T):
    bg(b, "lila", t); put(b, A.pencil_hand(200), 300, 760, .62 * pop(t, 0, .35), 0); put(b, A.mano_der(200), 780, 760, .62 * pop(t, .15, .35), 0)
    put(b, A.sello("ZURDO", 440, 200, A.VERDE, 120), 300, 1120, pop(t, .5, .3), -3); put(b, A.sello("DIESTRO", 440, 200, A.ROJO, 120), 780, 1120, pop(t, .7, .3), 3); put(b, A.texto("VS", 190, A.AMA, 14), 540, 760, pop(t, .35, .35), 0)
    titulo(b, "¿Y TÚ?", t, 0, 290, 130)
def S41(b, t, T):
    bg(b, "amarillo", t); titulo(b, "SÍGUEME", t, 0, 300, 150); put(b, A.boton_seguir(700), 540, 720, pop(t, .2, .4) * (1 + .03 * math.sin(t * 6)), bob(t, 1.5, 1.2))
    put(b, A.texto("@escribirconpinti", 72, (255, 255, 255), 9, "baloo"), 540, 900, pop(t, .5))
def S42(b, t, T):
    bg(b, "cielo", t); titulo(b, "1 TIP\n*CADA DÍA", t, 0, 290, 140); per(b, "n", "feliz", t, 540, 1020, .85); put(b, A.lapiz(480), 800, 1230, pop(t, .3, .3), -8 + bob(t, 2, 2)); estrellas(b, t, .4, (540, 760), 5, 400)

def _b(i): return ta(i) - 0.04
# (palabra de inicio, función, sonidos [(nombre, dt, dB)], sin_whoosh)
SHOTS = [
    (0, S00, [("brillo", .5, -9)], True), (10, S01, [("golpe", .1, -9)], False), (16, S02, [("brillo", .3, -11)], False), (21, S03, [("brillo", .5, -10)], False),
    (31, S04, [], False), (37, S05, [("golpe", .1, -9), ("lapiz", .6, -9)], False), (41, S06, [("resultado", .4, -12)], False), (45, S07, [("lapiz", .2, -8)], False),
    (50, S08, [("brillo", .3, -10)], False), (52, S09, [("golpe", .25, -10)], False), (56, S10, [], False), (58, S11, [], False), (63, S12, [], False),
    (69, S13, [("lapiz", .4, -9)], False), (72, S14, [("brillo", .35, -11)], False), (82, S15, [("golpe", .8, -10)], False), (91, S16, [("brillo", .2, -10)], False),
    (94, S17, [], False), (100, S18, [("rasgar", .5, -12)], False), (110, S19, [("golpe", .05, -6)], False), (112, S20, [("lapiz", .5, -9)], False),
    (120, S21, [("lapiz", .15, -8)], False), (126, S22, [("brillo", .3, -9)], False), (133, S23, [], False), (137, S24, [], False), (139, S25, [("brillo", .7, -11)], False),
    (145, S26, [("brillo", .25, -11)], False), (148, S27, [("brillo", .1, -11)], False), (152, S28, [("brillo", .8, -11)], False), (158, S29, [("brillo", .3, -9)], False),
    (162, S30, [("golpe", .05, -8), ("rasgar", .6, -12)], False), (172, S31, [("brillo", .3, -10)], False), (179, S32, [("brillo", .5, -11)], False),
    (183, S33, [("lapiz", .5, -10)], False), (187, S34, [("brillo", .2, -10)], False), (191, S35, [("brillo", .3, -10)], False), (198, S36, [], False),
    (205, S37, [("brillo", .15, -10)], False), (214, S38, [("lapiz", .1, -8)], False), (219, S39, [("brillo", .3, -11)], False), (224, S40, [("golpe", .35, -10)], False),
    (229, S41, [("brillo", .25, -9)], False), (233, S42, [("resultado", .1, -12)], False),
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

