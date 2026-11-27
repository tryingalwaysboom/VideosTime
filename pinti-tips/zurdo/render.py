"""Tip «Si tu hijo es zurdo, NO hagas esto» · @escribirconpinti. Tiempos por palabra de la voz (Whisper), escenas de ~2-3 s con
movimiento constante, subtítulos palabra a palabra, zona segura de TikTok (nada importante en el borde derecho ni abajo).
Uso: python3 render.py still 12.5 [salida.png] | scenes | mix [salida.mp4] | info"""
import os, sys, json, math, random, subprocess
from functools import lru_cache
from multiprocessing import Pool
from PIL import Image, ImageDraw
import art as A

HERE = os.path.dirname(os.path.abspath(__file__))
DESC = os.path.join(HERE, "..", "..", "descargas", "zurdo_tip")
SFXD = os.path.join(HERE, "..", "..", "descargas", "mateo_sfx")
TMP = os.path.join(HERE, "tmp"); os.makedirs(TMP, exist_ok=True)
W, H, FPS = 1080, 1920, 30
JA = json.load(open(os.path.join(DESC, "voz_a.json"), encoding="utf-8")); JC = json.load(open(os.path.join(DESC, "voz_c.json"), encoding="utf-8"))

GUION_A = ('Si tu hijo es zurdo... NO hagas esto. Seguro alguien ya te dijo que lo corrijas. Que escriba con la derecha, porque "es lo normal". '
           'Pues eso es un mito. Y puede hacerle mucho daño. Cuando obligas a un niño zurdo a cambiar de mano, la letra le sale peor, se cansa muy rápido... y empieza a odiar escribir. '
           'Y no es que sea torpe. Es que su cerebro ya eligió su mano. Entonces, ¿qué sí puedes hacer? Tres cosas que de verdad ayudan. '
           'Uno. Deja que use la mano que quiera. Sin comentarios y sin correcciones. Dos. Inclina el papel un poquito. Así su mano no tapa lo que va escribiendo. '
           'Tres. Que sujete el lápiz un poco más arriba, lejos de la punta. Así ve lo que escribe y no se mancha. '
           'Y no te asustes si al principio la letra sale fea, o si se le corre la tinta. Les pasa a casi todos los zurdos, y mejora con la práctica. '
           'Un niño zurdo no necesita que lo cambien. Necesita que lo ayudes a escribir a su manera. Sígueme, y cada día te traigo un tip para que tu hijo escriba mejor.')
GUION_C = ('Y un último consejo: celebra cuando escriba, sin importar cómo le quede. Un niño que se siente orgulloso de su letra, escribe más. '
           'Y el que escribe más, mejora más rápido. Así que cuando te enseñe lo que hizo, mira su esfuerzo, no si la letra le quedó perfecta.')
TA_, TC_ = GUION_A.split(), GUION_C.split()
assert len(TA_) == len(JA) and len(TC_) == len(JC), (len(TA_), len(JA), len(TC_), len(JC))

# ---------------------------------------------------------------- línea de tiempo (voz A + párrafo C insertado antes del cierre)
IDX = 164                                    # "Un niño zurdo no necesita…": aquí se inserta el párrafo extra
CUT = JA[IDX]["inicio"] - 0.06
DC = JC[-1]["fin"] + 0.15
OFFC = CUT + 0.45
OFF2 = OFFC + DC + 0.45
def ta(i): return JA[i]["inicio"] if i < IDX else JA[i]["inicio"] - CUT + OFF2
def tae(i): return JA[i]["fin"] if i < IDX else JA[i]["fin"] - CUT + OFF2
def tc(j): return JC[j]["inicio"] + OFFC
def tce(j): return JC[j]["fin"] + OFFC
TOTAL = max(tae(len(JA) - 1) + 0.6, 81.0)
WORDS = [(TA_[i].strip('"“”'), ta(i), tae(i)) for i in range(len(JA))]
WORDS = WORDS[:IDX] + [(TC_[j], tc(j), tce(j)) for j in range(len(JC))] + WORDS[IDX:]

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
def s_hook(b, t, T):
    bg(b, "cielo", t); titulo(b, "SI TU HIJO\n*ES ZURDO", t, .0, 400, 150); escritorio(b)
    kidpos(b, "feliz", t, 540, 920, 1.0, .1)
    put(b, A.lapiz(520), 700, 1235, pop(t, .5, .3), -6 + bob(t, 2, 2)); estrellas(b, t, .55, (540, 700), 4, 420, 80)

def s_no(b, t, T):
    bg(b, "alerta", t); shake(t, .12, 26)
    put(b, A.xmark(260), 540, 850, pop(t, .1, .35) * 2.2, 0); titulo(b, "NO HAGAS\n*ESTO", t, .35, 300, 140)

def s_dijeron(b, t, T):
    bg(b, "crema", t); escritorio(b); kidpos(b, "preocupado", t, 540, 960, .95, 0)
    put(b, A.globo("¡Cámbialo a\nla derecha!", 62, tail="right"), 420, 420, pop(t, .35) * 1.0, -3 + bob(t, 2))
    put(b, A.globo("¡Así no se\nescribe!", 62, (255, 232, 160), tail="left"), 650, 700, pop(t, 1.35) * 1.0, 3 + bob(t, 2, 1.1))

def s_derecha(b, t, T):
    bg(b, "lila", t); titulo(b, "¿ES LO NORMAL?", t, 0, 300, 100)
    carta(b, "MANO\nIZQUIERDA", (63, 127, 208), 330, 800, t, .1, rot=-4); carta(b, "MANO\nDERECHA", (150, 150, 170), 750, 800, t, .9, rot=3)
    put(b, A.check(170), 840, 1040, pop(t, 2.0), 0); put(b, A.globo("«lo normal»", 50, tail="right"), 640, 560, pop(t, 2.0), 3)

def s_mito(b, t, T):
    bg(b, "amarillo", t); k = ease(u_(t, .5, .16)); shake(t, .62, 34)
    titulo(b, "PUES ESO ES UN…", t, 0, 400, 104)
    if t >= .5: put(b, A.sello("MITO", 820, 330, A.ROJO, 230), 540, 800, 1 + (1 - k) * 1.6, -7)

def s_dano(b, t, T):
    bg(b, "noche", t); escritorio(b, 0, (120, 84, 70)); kidpos(b, "triste", t, 540, 950, .95, 0)
    put(b, A.corazon(280), 850, 520 + bob(t, 10, 3), pop(t, .3), 8); put(b, A.xmark(160), 850, 520, pop(t, 1.0) * 1.0, 0)
    titulo(b, "PUEDE HACERLE\n*DAÑO", t, .2, 320, 100)

def s_cambiar(b, t, T):
    bg(b, "cielo", t); titulo(b, "CAMBIAR\n*DE MANO", t, 0, 330, 120)
    k = ease(u_(t, .6, 1.4)); x = 270 + 560 * k; y = 900 - math.sin(k * math.pi) * 240
    carta(b, "IZQ.", (63, 127, 208), 250, 1000, t, 0, 300, 360); carta(b, "DER.", (150, 150, 170), 830, 1000, t, .2, 300, 360)
    put(b, A.lapiz(480), x, y, 1, -20 + 40 * k); put(b, A.flecha_curva(360), 540, 760, pop(t, .3), 0)

def s_peor(b, t, T):
    bg(b, "crema", t); modo = "limpia" if t < .55 else "fea"; shake(t, .55, 14, .3)
    hoja_escribiendo(b, 540, 760, .85, -4 if modo == "limpia" else bob(t, 3, 6), t, 0, .5 if modo == "limpia" else 0.01, ["mamá", "sol"], modo, mano=False)
    if t >= .6: put(b, A.xmark(220), 800, 430, pop(t, .65), 0)
    titulo(b, "LA LETRA SALE\n*PEOR", t, .0, 260, 96)

def s_cansa(b, t, T):
    bg(b, "lila", t); escritorio(b); kidpos(b, "cansado", t, 540, 960, .95, 0)
    put(b, A.bateria(380, max(.08, .8 - t * .6)), 800, 380, pop(t, .2), -6)
    for i in range(3): put(b, A.gota(70), 340 + i * 30, 640 + ((t * 300 + i * 120) % 260), pop(t, .3 + i * .15), 0)

def s_odia(b, t, T):
    bg(b, "noche", t); escritorio(b, 0, (110, 80, 66)); kidpos(b, "triste", t, 540, 960, .95, 0)
    put(b, A.nube(560), 540, 400 + bob(t, 8), pop(t, 1.3), 0); shake(t, 1.45, 14, .3)
    put(b, A.hoja(), 840, 760, pop(t, 1.9) * .45, 12); put(b, A.xmark(170), 840, 760, pop(t, 2.1), 0)

def s_torpe(b, t, T):
    bg(b, "menta", t); put(b, A.texto("TORPE", 250, A.AMA, 16), 540, 640, pop(t, .15), -3)
    k = u_(t, .7, .25); d = ImageDraw.Draw(b); x1 = 140 + 800 * k
    if k > 0: d.line((140, 650, x1, 610), fill=A.ROJO, width=26)
    titulo(b, "NO ES", t, 0, 380, 100); put(b, A.check(220), 540, 1010, pop(t, 1.1), 0)

def s_cerebro(b, t, T):
    bg(b, "cielo", t); put(b, A.cerebro(620), 540, 640 + bob(t, 10, 1.1), pop(t, .35, .4), bob(t, 3, .7)); estrellas(b, t, 1.35, (540, 640), 6, 360)
    put(b, A.texto("¡ES ZURDO!", 130, A.AMA, 12), 540, 1080, pop(t, 1.5), -3); titulo(b, "SU CEREBRO", t, 0, 270, 100)

def s_entonces(b, t, T):
    bg(b, "crema", t); titulo(b, "¿QUÉ SÍ\n*PUEDES HACER?", t, .6, 330, 118); escritorio(b); kidpos(b, "feliz" if t > 1.0 else "preocupado", t, 540, 980, .9, 0)

def s_tres(b, t, T):
    bg(b, "amarillo", t); put(b, A.texto("3", 520, (255, 255, 255), 18), 540, 560, pop(t, .1, .4), -4)
    put(b, A.texto("COSAS", 150, A.OL, 0, "anton", (255, 255, 255)), 540, 960, pop(t, .5))
    for i in range(3): insignia(b, i + 1, t, 1.0 + i * .5, 300 + i * 240, 1120, .8)

def s_uno(b, t, T):
    bg(b, "menta", t); insignia(b, 1, t, 0, 130, 250, .8); titulo(b, "LA MANO QUE QUIERA", t, .1, 250, 84)
    hoja_escribiendo(b, 600, 900, .78, -3, t, .3, 2.0, ["mamá", "sol"], "limpia"); put(b, A.check(200), 840, 1130, pop(t, 2.2), 0)

def s_sin(b, t, T):
    bg(b, "lila", t); titulo(b, "SIN COMENTARIOS\n*NI CORRECCIONES", t, 0, 320, 96)
    put(b, A.globo("¡Así no\nse hace!", 70, tail="left"), 540, 800, pop(t, .5), bob(t, 2)); put(b, A.xmark(300), 540, 800, pop(t, 1.0) * 1.0, 0)

def s_dos_a(b, t, T):
    bg(b, "cielo", t); insignia(b, 2, t, 0, 130, 250, .8); titulo(b, "INCLINA EL PAPEL", t, .1, 250, 96)
    r = -28 * ease(u_(t, .9, 1.1)); put(b, A.hoja(), 540, 840, .8, r); put(b, A.flecha_curva(420, A.ROJO), 800, 560, pop(t, 1.0), 0)

def s_dos_b(b, t, T):
    bg(b, "cielo", t); hoja_escribiendo(b, 600, 840, .85, -28, t, .2, 1.9, ["sol", "mamá"], "limpia")
    put(b, A.ojo(260), 850, 290, pop(t, .4), 0); put(b, A.check(170), 220, 330, pop(t, 1.6), 0)
    put(b, A.texto("¡SE VE LO QUE ESCRIBE!", 66, (255, 255, 255), 9), 540, 1190, pop(t, 1.3), 0)

def s_tres_a(b, t, T):
    bg(b, "durazno", t); insignia(b, 3, t, 0, 160, 290); titulo(b, "AGARRA EL LÁPIZ\n*MÁS ARRIBA", t, .1, 360, 90)
    g = 120 + 210 * ease(u_(t, .9, 1.9)); put_tip(b, A.pencil_hand(g), 640, 1190, .72)
    put(b, A.flecha_curva(260, A.VERDE, True), 880, 900, pop(t, 1.2), 90)

def s_tres_b(b, t, T):
    bg(b, "durazno", t); titulo(b, "LEJOS DE LA PUNTA", t, 0, 290, 96); put_tip(b, A.pencil_hand(330), 640, 1190, .72)
    put(b, A.flecha_doble(300), 667, 1030, pop(t, .3), -63)

def s_tres_c(b, t, T):
    bg(b, "menta", t); put(b, A.ojo(260), 230, 330, pop(t, .2), 0)
    hoja_escribiendo(b, 580, 840, .85, -10, t, .2, 1.6, ["sol", "mamá"], "limpia")
    put(b, A.check(220), 850, 1090, pop(t, 1.6), 0); estrellas(b, t, 1.7, (540, 700), 5, 380)

def s_fea(b, t, T):
    bg(b, "crema", t); kidpos(b, "preocupado", t, 330, 940, .72, 0)
    hoja_escribiendo(b, 760, 760, .62, 6, t, .2, 1.8, ["mamá", "sol"], "fea", mano=False); titulo(b, "LETRA FEA", t, .1, 300, 110)

def s_tinta(b, t, T):
    bg(b, "lila", t); put(b, A.hoja(), 540, 830, .85, -3)
    k = pop(t, .5, .5); im = Image.new("RGBA", (400, 400), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for (x, y, r) in ((200, 200, 120), (130, 250, 60), (270, 140, 55), (250, 290, 50)): d.ellipse((x - r, y - r, x + r, y + r), fill=(36, 52, 150, 235))
    put(b, im, 560, 770, k * 1.2, 0); put(b, A.gota(110), 560, 350 + ease(u_(t, .1, .4)) * 250, 1 - u_(t, .45, .1), 0)
    titulo(b, "SE CORRE LA TINTA", t, .1, 260, 90)

def s_todos(b, t, T):
    bg(b, "cielo", t); titulo(b, "A CASI TODOS\n*LES PASA", t, 0, 330, 104)
    for i in range(5):
        k = pop(t, .3 + i * .22, .3); put(b, A.kid(["feliz", "neutral", "feliz", "preocupado", "feliz"][i]), 200 + i * 170, 860 + bob(t, 6, 1.2, i), .30 * k, bob(t, 3, 1, i))
    put(b, A.texto("¡ES NORMAL!", 120, A.AMA, 12), 540, 1110, pop(t, 1.5), -3)

def s_mejora(b, t, T):
    bg(b, "menta", t); titulo(b, "CADA DÍA\n*MEJOR", t, 0, 300, 120)
    for i, (modo, sd) in enumerate((("fea", 5), ("fea", 8), ("limpia", 3))):
        cx = 250 + i * 280; k = pop(t, .2 + i * .5, .35)
        h = A.hoja().copy(); h.alpha_composite(A.letra(("mamá",), modo, sd, 120)); put(b, h, cx, 860 - i * 40, .42 * k, -4 + i * 4)
    put(b, A.flecha_curva(300, A.VERDE), 540, 1090, pop(t, 1.4), 90); estrellas(b, t, 1.6, (800, 760), 4, 150, 70)

def c_a(b, t, T):
    bg(b, "amarillo", t); titulo(b, "UN ÚLTIMO\n*CONSEJO", t, .05, 520, 150); estrellas(b, t, .5, (540, 760), 6, 360)

def c_b(b, t, T):
    bg(b, "cielo", t); escritorio(b); kidpos(b, "orgulloso", t, 540, 960, .95, 0); confeti(b, t, .15); titulo(b, "¡CELEBRA!", t, .1, 360, 150)

def c_c(b, t, T):
    bg(b, "crema", t); hoja_escribiendo(b, 540, 860, .8, 3, t, .01, .01, ["mamá", "sol"], "fea", mano=False)
    put(b, A.check(300), 800, 620, pop(t, 1.3), 0); put(b, A.corazon(220), 300, 1090, pop(t, 1.5), -8); titulo(b, "SIN IMPORTAR\n*CÓMO QUEDE", t, 0, 270, 92)

def c_d(b, t, T):
    bg(b, "durazno", t); escritorio(b); kidpos(b, "orgulloso", t, 540, 960, .95, 0); put(b, A.corazon(280), 840, 520, pop(t, 1.0) * 1.0, 8 + bob(t, 6, 2))
    titulo(b, "SE SIENTE\n*ORGULLOSO", t, .2, 300, 104)

def c_e(b, t, T):
    bg(b, "menta", t); hoja_escribiendo(b, 580, 860, .85, -6, t, .1, 1.6, ["mamá", "sol", "mi casa"], "limpia"); titulo(b, "*ESCRIBE MÁS", t, 0, 260, 110)

def c_f(b, t, T):
    bg(b, "cielo", t)
    for i in range(4):
        h = A.hoja(); put(b, h, 350 + i * 120, 880 - i * 55 + (1 - pop(t, .1 + i * .3, .3)) * 400, .55, -8 + i * 5)
    titulo(b, "Y ESCRIBE\n*MÁS", t, 0, 280, 104)

def c_g(b, t, T):
    bg(b, "amarillo", t); titulo(b, "MEJORA MÁS\n*RÁPIDO", t, 0, 290, 104)
    d = ImageDraw.Draw(b)
    for i in range(4):
        k = ease(u_(t, .15 + i * .22, .35)); hgt = (130 + i * 150) * k; x = 230 + i * 190
        d.rounded_rectangle((x - 70, 1100 - hgt, x + 70, 1100), 20, fill=A.VERDE, outline=A.OL, width=8)
    put(b, A.flecha_curva(300, A.ROJO), 800, 700, pop(t, .9), 0); estrellas(b, t, 1.1, (780, 700), 4, 170, 70)

def c_h(b, t, T):
    bg(b, "crema", t); escritorio(b); kidpos(b, "orgulloso", t, 380, 970, .82, 0)
    h = A.hoja().copy(); h.alpha_composite(A.letra(("mamá", "sol"), "fea", 5, 150)); put(b, h, 760 + bob(t, 4, 1), 850 + bob(t, 8, 1.3), .62 * pop(t, .3), 8)
    titulo(b, "LO QUE\n*HIZO", t, .1, 300, 110)

def c_i(b, t, T):
    bg(b, "durazno", t); put(b, A.texto("ESFUERZO", 200, A.AMA, 14), 540, 620, pop(t, .25), -3); put(b, A.corazon(280), 540, 960 + bob(t, 8, 2), pop(t, .8), 0)
    estrellas(b, t, .9, (540, 700), 6, 400)

def c_j(b, t, T):
    bg(b, "lila", t); put(b, A.texto("PERFECTA", 190, (150, 150, 170), 14), 540, 620, pop(t, .2), 3)
    k = u_(t, .9, .25); ImageDraw.Draw(b).line((110, 630, 110 + 860 * k, 610), fill=A.ROJO, width=24)
    put(b, A.xmark(220), 540, 960, pop(t, 1.2), 0)

def e_a(b, t, T):
    bg(b, "cielo", t); escritorio(b); kidpos(b, "feliz", t, 540, 970, .95, 0); titulo(b, "NO NECESITA\n*CAMBIAR", t, .1, 320, 110)

def e_b(b, t, T):
    bg(b, "menta", t); hoja_escribiendo(b, 580, 870, .85, -6, t, .2, 2.0, ["a mi", "manera"], "limpia")
    put(b, A.corazon(200), 880, 330, pop(t, 1.2), 8 + bob(t, 5, 2)); titulo(b, "A SU MANERA", t, .1, 270, 108)

def e_c(b, t, T):
    bg(b, "amarillo", t); titulo(b, "1 TIP\n*CADA DÍA", t, .05, 280, 140)
    put(b, A.boton_seguir(700), 540, 640, pop(t, .5, .4) * (1 + .03 * math.sin(t * 6)), bob(t, 1.5, 1.2))
    put(b, A.texto("@escribirconpinti", 72, (255, 255, 255), 9, "baloo"), 540, 800, pop(t, .9)); put(b, A.kid("feliz"), 540, 1030, .55 * pop(t, .2, .4), bob(t, 2, 1))

# (inicio, función, sonidos [(nombre, dt, dB)], sin_whoosh)
def _b(i): return ta(i) - 0.04
def _c(j): return tc(j) - 0.04
SHOTS = [
    (0.0, s_hook, [("brillo", .6, -9)], True), (_b(5), s_no, [("golpe", .12, -3)], False), (_b(8), s_dijeron, [("brillo", .4, -12), ("brillo", 1.4, -12)], False),
    (_b(16), s_derecha, [("brillo", 2.0, -10)], False), (_b(25), s_mito, [("golpe", .5, -2)], False), (_b(30), s_dano, [], False),
    (_b(35), s_cambiar, [("lapiz", .6, -8)], False), (_b(45), s_peor, [("borrar", .5, -7)], False), (_b(50), s_cansa, [], False),
    (_b(54), s_odia, [("golpe", 1.5, -8)], False), (_b(59), s_torpe, [("rasgar", .7, -10)], False), (_b(65), s_cerebro, [("brillo", 1.4, -8)], False),
    (_b(73), s_entonces, [], False), (_b(78), s_tres, [("golpe", .1, -9)], False), (_b(84), s_uno, [("lapiz", .3, -8), ("brillo", 2.2, -9)], False),
    (_b(92), s_sin, [("golpe", 1.0, -9)], False), (_b(97), s_dos_a, [("rasgar", .9, -14)], False), (_b(103), s_dos_b, [("lapiz", .2, -8), ("brillo", 1.6, -9)], False),
    (_b(112), s_tres_a, [], False), (_b(121), s_tres_b, [], False), (_b(126), s_tres_c, [("lapiz", .2, -8), ("brillo", 1.7, -8)], False),
    (_b(134), s_fea, [("lapiz", .2, -8)], False), (_b(145), s_tinta, [("golpe", .5, -9)], False), (_b(152), s_todos, [("brillo", 1.5, -10)], False),
    (_b(159), s_mejora, [("resultado", 1.4, -12), ("brillo", 1.6, -10)], False),
    (_c(0) , c_a, [("brillo", .5, -9)], False), (_c(4), c_b, [("brillo", .2, -8)], False), (_c(7), c_c, [("brillo", 1.3, -9)], False),
    (_c(12), c_d, [("brillo", 1.0, -9)], False), (_c(18), c_e, [("lapiz", .1, -8)], False), (_c(23), c_f, [], False),
    (_c(28), c_g, [("resultado", .9, -12)], False), (_c(31), c_h, [], False), (_c(39), c_i, [("brillo", .9, -9)], False),
    (_c(45), c_j, [("golpe", 1.2, -10)], False), (_b(164), e_a, [], False), (_b(172), e_b, [("lapiz", .2, -8), ("brillo", 1.2, -10)], False),
    (_b(181), e_c, [("brillo", .5, -9)], False),
]
SHOTS = [(max(0.0, a), f, s, n) for a, f, s, n in SHOTS]
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
    A_, C_ = os.path.join(DESC, "voz_a.mp3"), os.path.join(DESC, "voz_c.mp3"); o2, oc = int(OFF2 * 1000), int(OFFC * 1000)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", A_, "-i", C_, "-filter_complex",
                    f"[0:a]asplit=2[x][y];[x]atrim=0:{CUT:.3f},asetpts=PTS-STARTPTS,afade=t=out:st={CUT - .03:.3f}:d=0.03[a1];"
                    f"[1:a]atrim=0:{DC:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,adelay={oc}|{oc}[a2];"
                    f"[y]atrim=start={CUT:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,adelay={o2}|{o2}[a3];"
                    f"[a1][a2][a3]amix=inputs=3:normalize=0:duration=longest,aresample=48000,apad,atrim=0:{TOTAL:.2f},"
                    "acompressor=threshold=-18dB:ratio=3:attack=5:release=120,loudnorm=I=-15:TP=-1.5:LRA=9,aresample=48000[v]",
                    "-map", "[v]", "-ac", "1", "-ar", "48000", vw], check=True)
    mw = os.path.join(TMP, "musica.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", os.path.join(SFXD, "musica.mp3"), "-i", vw, "-filter_complex",
                    f"[0:a]aresample=48000,atrim=0:{TOTAL:.2f},loudnorm=I=-28:TP=-8,aresample=48000,aformat=channel_layouts=mono[m0];[1:a]apad,atrim=0:{TOTAL:.2f}[key];"
                    "[m0][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[mus]", "-map", "[mus]", "-ar", "48000", "-ac", "1", mw], check=True)
    efx = []
    for (a, fn, sfx, nw), (s0, s1) in zip(SHOTS, BOUNDS):
        if a > 0 and not nw: efx.append(("whoosh", a - .05, -10, None))
        for n, dt, db in sfx:
            efx.append((n, a + dt, db, (a + dt, a + dt + (2.0 if n == "lapiz" else 0)) if n == "lapiz" else None))
    ins, flt, parts = ["-i", vw, "-i", mw], [f"[0:a]apad,atrim=0:{TOTAL:.2f}[v]", f"[1:a]apad,atrim=0:{TOTAL:.2f}[m]"], ["[v]", "[m]"]
    for j, (n, t, db, gate) in enumerate(efx):
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
        print("TOTAL %.2f s, escenas %d, CUT %.2f OFFC %.2f OFF2 %.2f" % (TOTAL, len(SHOTS), CUT, OFFC, OFF2))
        for i, (a, e) in enumerate(BOUNDS): print(i, SHOTS[i][1].__name__, "%.2f-%.2f (%.1fs)" % (a, e, e - a))
    elif cmd == "still":
        for tt in sys.argv[2].split(","): frame(float(tt)).save(f"/tmp/still_{float(tt):.1f}.png")
    elif cmd == "scenes":
        todo = [int(x) for x in sys.argv[2:]] or [i for i in range(len(SHOTS)) if not os.path.exists(os.path.join(TMP, f"s{i:02d}.mp4"))]
        with Pool(2) as p:
            for i in p.imap_unordered(render_scene, todo): print("escena", i, flush=True)
    elif cmd == "mix":
        mix(sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "tip_zurdo_mito.mp4"))
