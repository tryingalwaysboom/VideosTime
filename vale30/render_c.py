"""Serie «30 días sin celular: solo puedo escribir a mano» · DÍA 1 — La caja.
Estilo: cortes secos cada 1,5-2 s con golpe de zoom, neón morado/turquesa, etiquetas de papel, subtítulos palabra a palabra.
Uso: python3 render_v1.py info | mid | still t.. | scenes [i..]"""
import os, sys, math, json, subprocess, random
from functools import lru_cache
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["GUION"] = "guion_v1c"; os.environ["VOZDIR"] = os.path.join(HERE, "voz_v1c")
sys.path.insert(0, HERE)
import importlib.util
_spec = importlib.util.spec_from_file_location("R", os.path.join(HERE, "..", "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
R.LAY = os.path.join(HERE, "layers"); R.layer.cache_clear(); R.scaled.cache_clear()
TMP = os.path.join(HERE, "tmp_v1c"); os.makedirs(TMP, exist_ok=True)
W, H, FPS = R.W, R.H, R.FPS
put, ease, clamp, back, font, bg = R.put, R.ease, R.clamp, R.back, R.font, R.bg
F_ANTON = R.F_ANTON; MF = os.path.join(HERE, "..", "mateo-pov", "fonts")
F_HAND = os.path.join(MF, "Caveat.ttf"); F_BAL = os.path.join(MF, "Baloo2-ExtraBold.ttf")
PI_ = math.pi
OL = (22, 15, 44); MOR = (35, 21, 72); MOR2 = (12, 10, 32); TUR = (43, 212, 196); AMA = (255, 201, 60); ROSA = (255, 93, 115)
PAPEL = (255, 246, 220); TINTA = (42, 59, 143); BLANCO = (255, 255, 255); ROJO = (255, 59, 78)

# ---------------------------------------------------------------- tiempos
R.GAP.clear()
BASE = {"Y02": .06, "Y03": .1, "Y04": .1, "Y05": .12, "Y06": .1, "Y07": .06, "Y08": .12, "Y09": .12, "Y10": .14, "Y11": .16}
FLEX = ("Y03", "Y05", "Y08", "Y10")
COLA = .35
R.GAP.update(BASE); _tl, _ = R.timeline(); _fin = _tl["Y11"][1] - .1 + COLA
OBJ = float(math.ceil(_fin)); _extra = (OBJ - COLA) - (_tl["Y11"][1] - .1)
for _k in FLEX: R.GAP[_k] = BASE[_k] + _extra / len(FLEX)
R.TL, R.TOTAL = R.timeline(); R.TL = {k: (a - .1, b - .1) for k, (a, b) in R.TL.items()}; R.TOTAL = OBJ
TL, TOTAL = R.TL, R.TOTAL; LINEAS = R.LINEAS
def S(l): return TL[l][0]
def E(l): return TL[l][1]
_WT = {lid: R.word_times(lid, cap.split()) for lid, who, tts, cap in LINEAS}
def WI(lid, i): return _WT[lid][i][0]
def talk(lid, T): return S(lid) <= T < E(lid)
def u_(T, t0, d): return clamp((T - t0) / d)
def pop(T, t0, d=.28): return back((T - t0) / d) if T >= t0 else 0

def chunks():
    out = []
    for lid, who, tts, cap in LINEAS:
        words = cap.split(); times = _WT[lid]; groups, cur = [], []
        for i, w in enumerate(words):
            cur.append(i)
            if sum(len(words[x].strip("*")) + 1 for x in cur) >= 11 or w.rstrip("*").endswith((".", ",", ":", "?", "!", "…")):
                groups.append(cur); cur = []
        if cur: groups.append(cur)
        for g in groups:
            out.append((times[g[0]][0], times[g[-1]][1], [(words[i].replace("*", "").rstrip(":").upper(), times[i], "*" in words[i]) for i in g], who, lid))
    return out
CH = chunks()

# ---------------------------------------------------------------- utilidades
@lru_cache(8)
def _plano(c1, c2, glow=None):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); t = (yy / H)[..., None]
    a = np.array(c1, np.float32) * (1 - t) + np.array(c2, np.float32) * t
    if glow:
        g = np.exp(-(((xx - W / 2) / 620) ** 2 + ((yy - 860) / 760) ** 2))[..., None]; a = a + (np.array(glow, np.float32) - a) * g * .38
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
def plano(c1=MOR, c2=MOR2, glow=None): return _plano(c1, c2, glow).copy()

def rayos(c, T, col=TUR, cx=540, cy=860, a=26, n=14):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for i in range(n):
        an = T * .5 + i * 2 * PI_ / n; d.polygon([(cx, cy), (cx + 2400 * math.cos(an - .09), cy + 2400 * math.sin(an - .09)), (cx + 2400 * math.cos(an + .09), cy + 2400 * math.sin(an + .09))], fill=col + (a,))
    c.alpha_composite(lay)

def titulo(c, s, cx, cy, size, col=BLANCO, rot=0, k=1.0, sw=12, f=None, sfill=OL):
    if k <= 0: return
    f_ = font(f or F_ANTON, size * k); tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(tmp).text((cx, cy), s, font=f_, fill=col + (255,), anchor="mm", stroke_width=int(sw * k), stroke_fill=sfill + (255,))
    if rot: tmp = tmp.rotate(rot, center=(cx, cy), resample=Image.BICUBIC)
    c.alpha_composite(tmp)

def papel(c, s, cx, cy, size, rot=-3, k=1.0, fill=PAPEL, fg=OL, f=None, cinta=True, pad=26):
    """Etiqueta de papel de cuaderno pegada con cinta."""
    if k <= 0.02: return
    f_ = font(f or F_BAL, size); d0 = ImageDraw.Draw(c); lines = s.split("\n")
    tw = max(d0.textlength(l, font=f_) for l in lines); lh = size * 1.08; w = int(tw + pad * 2.2); h = int(lh * len(lines) + pad * 1.5)
    im = Image.new("RGBA", (w + 60, h + 70), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((36, 46, 36 + w, 46 + h), 10, fill=(0, 0, 0, 90)); d.rounded_rectangle((30, 36, 30 + w, 36 + h), 10, fill=fill + (255,), outline=OL + (255,), width=6)
    for i, l in enumerate(lines): d.text((30 + w / 2, 36 + pad * .75 + lh * (i + .5) - size * .06), l, font=f_, fill=fg + (255,), anchor="mm")
    if cinta: d.rectangle((30 + w / 2 - 60, 18, 30 + w / 2 + 60, 52), fill=(255, 226, 122, 225), outline=OL + (255,), width=3)
    if k != 1: im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.BICUBIC)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    c.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def osc(c, a, box=None, col=(8, 5, 20)):
    if a <= 0: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).rectangle(box or (0, 0, W, H), fill=col + (int(a),)); c.alpha_composite(lay)

def flash(c, T, t0, d=.22, col=(255, 255, 255)):
    if t0 <= T < t0 + d: osc(c, 235 * (1 - (T - t0) / d) ** 1.5, col=col)

def corazon(d, cx, cy, r, col):
    d.ellipse((cx - r, cy - r, cx, cy), fill=col); d.ellipse((cx, cy - r, cx + r, cy), fill=col); d.polygon([(cx - r * .96, cy - r * .3), (cx + r * .96, cy - r * .3), (cx, cy + r * .95)], fill=col)

def chispas(c, cx, cy, T, t0, n=10, col=AMA, r=260):
    u = (T - t0) / .5
    if not 0 <= u < 1: return
    d = ImageDraw.Draw(c); rr = random.Random(int(cx + cy))
    for i in range(n):
        an = rr.uniform(0, 2 * PI_); q = r * (.35 + .65 * ease(u)) * rr.uniform(.6, 1); x, y = cx + q * math.cos(an), cy + q * math.sin(an); s = 16 * (1 - u) + 3
        d.polygon([(x, y - s * 1.6), (x + s * .5, y), (x, y + s * 1.6), (x - s * .5, y)], fill=col); d.polygon([(x - s * 1.6, y), (x, y - s * .5), (x + s * 1.6, y), (x, y + s * .5)], fill=col)

from nota_spec import NOTA, glifos
def escribe(c, ox, oy, k, gl, u, col=TINTA):
    """Dibuja los primeros glifos de la letra de Vale (los mismos que lleva la nota), a escala k. Devuelve la punta."""
    n = u * len(gl); tip = (ox + gl[0][1] * k, oy + gl[0][2] * k)
    for i, (g, x, y, sz, rot) in enumerate(gl):
        if i >= n: break
        f_ = font(F_HAND, sz * k); R_ = int(sz * k * 1.5); im = Image.new("RGBA", (2 * R_, 2 * R_), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((R_, R_), g, font=f_, fill=col + (255,), anchor="ls", stroke_width=max(1, int(k * 1.2)), stroke_fill=col + (255,))
        im = im.rotate(-rot, resample=Image.BICUBIC, center=(R_, R_)); c.alpha_composite(im, (int(ox + x * k - R_), int(oy + y * k - R_))); tip = (ox + (x + sz * .4) * k, oy + (y - sz * .1) * k)
    return tip
LETRA1 = glifos(("hoy no ise", "la tarea por", "ke mi perro", "se la comio"), 11, 0, 0, 52, (46, 68))

def hoja(c, cx, cy, w, h, rot=0, rayas=True):
    """Hoja de cuaderno grande (para escribir encima). Devuelve nada; se dibuja recta."""
    d = ImageDraw.Draw(c); d.rounded_rectangle((cx - w / 2 + 14, cy - h / 2 + 18, cx + w / 2 + 14, cy + h / 2 + 18), 8, fill=(0, 0, 0, 110))
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 8, fill=PAPEL, outline=OL, width=8)
    if rayas:
        for y in range(int(cy - h / 2 + 110), int(cy + h / 2 - 30), 74): d.line((cx - w / 2 + 12, y, cx + w / 2 - 12, y), fill=(156, 199, 238), width=4)
        d.line((cx - w / 2 + 90, cy - h / 2 + 8, cx - w / 2 + 90, cy + h / 2 - 8), fill=(240, 138, 138), width=4)
    d.rectangle((cx - 90, cy - h / 2 - 22, cx + 90, cy - h / 2 + 26), fill=(255, 226, 122), outline=OL, width=4)
    for y in range(int(cy - h / 2 + 90), int(cy + h / 2 - 40), 150): d.ellipse((cx - w / 2 + 26, y - 17, cx - w / 2 + 60, y + 17), fill=(29, 22, 64), outline=OL, width=4)
    d.polygon([(cx + w / 2 - 8, cy + h / 2 - 90), (cx + w / 2 - 8, cy + h / 2 - 8), (cx + w / 2 - 90, cy + h / 2 - 8)], fill=(232, 217, 176))

def vale(c, kind, cx, cy, s, T, lid=None, pose=None, rot=0):
    hab = lid is not None and talk(lid, T) and math.sin(T * 26) > -.2
    name = f"vale_{kind}" + (f"_{pose}" if pose else "")
    if hab and os.path.exists(os.path.join(R.LAY, name + "_hab.png")): name += "_hab"
    if cy + 640 * s < H:      # el cuerpo sigue hasta el borde: nunca se ve cortado
        d = ImageDraw.Draw(c); d.rectangle((cx - 300 * s, cy + 600 * s, cx + 300 * s, H + 10), fill=(240, 184, 40)); d.rectangle((cx + 170 * s, cy + 600 * s, cx + 300 * s, H + 10), fill=(214, 156, 22))
        d.line((cx - 302 * s, cy + 640 * s, cx - 302 * s, H), fill=OL, width=max(3, int(7 * s))); d.line((cx + 302 * s, cy + 640 * s, cx + 302 * s, H), fill=OL, width=max(3, int(7 * s)))
    put(c, name, cx, cy + 5 * math.sin(T * 3.1), s, rot=rot)

def zoom(im, z, fx=.5, fy=.5):
    if abs(z - 1) < .003: return im
    w, h = W / z, H / z; x0 = (W - w) * fx; y0 = (H - h) * fy
    return im.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + w, y0 + h))

def caja_big(c, cx, cy, s, T, texto=None, tcol=ROJO, shake=0):
    cx += shake * math.sin(T * 70); put(c, "caja", cx, cy, s)
    if texto:
        d = ImageDraw.Draw(c); x0, y0, x1, y1 = cx - 104 * s, cy - 215 * s, cx + 104 * s, cy - 123 * s
        d.rounded_rectangle((x0, y0, x1, y1), int(14 * s), fill=(22, 18, 42), outline=OL, width=int(8 * s))
        f_ = font(F_ANTON, 56 * s * (1 if len(texto) < 9 else .62)); d.text(((x0 + x1) / 2, (y0 + y1) / 2 - 2 * s), texto, font=f_, fill=tcol, anchor="mm")

# ---------------------------------------------------------------- escenas
def sc_gancho(T, t0):           # la caja se cierra
    c = bg("bg_cocina", T, t0, 1.0, 1.1, 3, .5, .62); rayos(c, T, ROSA, 540, 900, 20)
    tk = WI("X02", 4); u = u_(T, tk - .16, .16)
    caja_big(c, 540, 960, 1.95, T, shake=10 * math.exp(-(T - tk) * 9) if T >= tk else 0)
    put(c, "mano_mama", 1250 - 470 * ease(u_(T, t0, .25)) + 300 * ease(u_(T, tk + .45, .3)), 1040, .85)
    if T >= tk: chispas(c, 540, 1040, T, tk, 12, AMA, 330); titulo(c, "¡CLIC!", 300, 400, 130, AMA, 8, pop(T, tk, .2)); papel(c, "23:59", 800, 420, 96, 6, pop(T, t0 + .05, .2), f=F_ANTON)
    flash(c, T, tk, .12)
    return c
def sc_30(T, t0):               # el contador
    c = plano((60, 12, 40), (20, 8, 28), ROJO); rayos(c, T, ROJO, 540, 760, 30)
    k = pop(T, t0, .22); put(c, "candado", 540, 1090 + 40 * (1 - k), 1.5, rot=6 * math.sin(T * 9))
    titulo(c, "30", 540, 500, 420, ROJO, 0, k, 16, sfill=(20, 8, 28)); titulo(c, "DÍAS", 540, 770, 170, BLANCO, 0, pop(T, t0 + .12, .22))
    return c
def sc_treinta(T, t0):          # FOTOGRAMA 0: Vale grita y la premisa ya está escrita
    c = bg("bg_cuarto", T, t0, 1.25, 1.4, 1, .5, .3); rayos(c, T * 3, ROJO, 540, 900, 40)
    vale(c, "shock", 540 + 10 * math.sin(T * 60), 1250, .95, T, "V02", "manos")
    k = .9 + .1 * back(u_(T, t0, .18)); titulo(c, "30 DÍAS", 540, 440, 200, ROJO, -3, k, 18, sfill=BLANCO); titulo(c, "SIN CELULAR", 540, 600, 115, BLANCO, -3, k, 15)
    return zoom(c, 1 + .06 * u_(T, t0, .8), .5, .25)
def sc_vale(T, t0):             # presentación
    c = bg("bg_cuarto", T, t0, 1.0, 1.12, 3, .5, .5); put(c, "cocodrilo", 120, 1225, .3, rot=-8); vale(c, "aburrida", 560, 1130, 1.18, T)
    papel(c, "VALE", 250, 470, 130, -8, pop(T, WI("X03", 2) - .05), AMA, f=F_ANTON)
    papel(c, "15 AÑOS", 760, 560, 84, 6, pop(T, WI("X03", 3) - .05), f=F_ANTON)
    return c
def sc_9horas(T, t0):           # tiempo de pantalla
    c = plano((18, 30, 74), (12, 10, 34), TUR); d = ImageDraw.Draw(c)
    x0, y0, x1, y1 = 190, 330, 890, 1290; d.rounded_rectangle((x0, y0, x1, y1), 70, fill=(34, 32, 58), outline=OL, width=14); d.rounded_rectangle((x0 + 34, y0 + 70, x1 - 34, y1 - 70), 24, fill=(16, 14, 34))
    d.text((540, 480), "TIEMPO DE PANTALLA", font=font(F_BAL, 46), fill=(170, 176, 214), anchor="mm")
    u = ease(u_(T, t0 + .05, .7)); n = int(round(9 * u)); d.text((540, 640), f"{n} h {int(4 * u):02d} min", font=font(F_ANTON, 150), fill=TUR if n < 9 else ROJO, anchor="mm")
    hs = [5, 7, 6, 8, 9, 9, 9]
    for i, hh in enumerate(hs):
        bx = 280 + i * 78; bh = 360 * hh / 9 * ease(u_(T, t0 + .1 + i * .06, .35)); d.rounded_rectangle((bx, 1150 - bh, bx + 52, 1150), 10, fill=ROJO if hh == 9 else TUR)
        d.text((bx + 26, 1185), "LMXJVSD"[i], font=font(F_BAL, 34), fill=(170, 176, 214), anchor="mm")
    papel(c, "AL DÍA", 760, 800, 70, 7, pop(T, WI("V03", 7)), ROSA, BLANCO, F_ANTON)
    return zoom(c, 1.04 + .05 * u_(T, t0, 2))
def sc_letra(T, t0):            # una letra que no entiende ni ella
    c = plano((70, 44, 20), (30, 16, 40), AMA); hoja(c, 540, 660, 800, 600)
    tip = escribe(c, 270, 500, 1.9, LETRA1, u_(T, t0, E("X03") - t0 + .3))
    put(c, "mano_pluma", tip[0] + 320, tip[1] - 250, 1.0)
    vale(c, "asco", 270, 1250, .62, T)
    for i, (x, y) in enumerate(((640, 1130), (790, 1090), (880, 1190))): titulo(c, "?", x, y, 170 - 24 * i, ROSA, 12 - 12 * i, pop(T, WI("X03", 9) + i * .12))
    return c
def sc_trato(T, t0):
    c = plano(MOR, MOR2, TUR); rayos(c, T, TUR); hoja(c, 540, 800, 800, 520, rayas=False)
    titulo(c, "EL TRATO", 540, 720, 190, OL, -3, pop(T, t0, .2), 0); d = ImageDraw.Draw(c); u = ease(u_(T, t0 + .2, .35)); d.line((240, 850, 240 + 600 * u, 842), fill=ROSA, width=14)
    titulo(c, "mamá  vs  Vale", 540, 940, 84, TINTA, 0, pop(T, t0 + .3), 0, F_HAND)
    return c
def sc_recupera(T, t0):         # si aguanta: lo recupera
    c = bg("bg_cocina", T, t0, 1.1, 1.2, 2, .5, .6); rayos(c, T, AMA, 600, 740, 34)
    u = ease(u_(T, t0 + .1, .5)); put(c, "candado_abierto", 250, 1050, .95, rot=-14 + 5 * math.sin(T * 6))
    put(c, "celular", 620, 800 - 60 * u + 12 * math.sin(T * 4), 1.05, rot=8 - 8 * u); chispas(c, 620, 760, T, t0 + .25, 14, AMA, 380)
    papel(c, "SI AGUANTA", 300, 400, 84, -6, pop(T, t0 + .05), TUR, OL, F_ANTON)
    return c
def sc_concierto(T, t0):
    c = plano((70, 14, 60), (24, 10, 44), ROSA); rayos(c, T * 2, ROSA, 540, 800, 40); k = pop(T, t0, .25)
    put(c, "boleto", 520, 780, 1.4 * k, rot=-8 + 30 * (1 - k)); chispas(c, 540, 780, T, t0 + .1, 16, AMA, 460)
    d = ImageDraw.Draw(c); sil = (16, 8, 30)
    for i in range(8):
        x = 60 + i * 140; y = 1660 + 26 * math.sin(T * 9 + i * 1.3); d.ellipse((x - 74, y - 74, x + 74, y + 74), fill=sil); d.rounded_rectangle((x - 100, y + 50, x + 100, H), 40, fill=sil)
        if i % 2 == 0: d.line((x + 70, y + 60, x + 110, y - 150), fill=sil, width=44); d.ellipse((x + 82, y - 196, x + 138, y - 140), fill=sil)
    return c
def sc_trampa(T, t0):
    c = plano((90, 10, 26), (24, 6, 20), ROJO); vale(c, "shock", 540, 1230, .95, T)
    k = pop(T, WI("V04", 14) - .04, .2); titulo(c, "TRAMPA", 540, 390, 200, ROJO, -6, k, 16, sfill=BLANCO); titulo(c, "UNA SOLA VEZ", 540, 545, 74, BLANCO, -6, pop(T, WI("V04", 15)))
    return c
def sc_16(T, t0):
    c = plano((36, 12, 40), (10, 6, 20), ROJO); caja_big(c, 540, 930, 1.8, T, "HASTA LOS 16", ROJO, 8 * math.exp(-(T - t0) * 6))
    d = ImageDraw.Draw(c)
    for sx in (-1, 1):
        for i in range(10): x = 540 + sx * (i - 4.5) * 112; y = 1010 + (i - 4.5) * 40 * sx; d.ellipse((x - 62, y - 30, x + 62, y + 30), outline=OL, width=22); d.ellipse((x - 60, y - 28, x + 60, y + 28), outline=(201, 211, 230), width=13)
    titulo(c, "SIN CELULAR", 540, 400, 150, BLANCO, 0, pop(T, WI("V04", 20) - .05))
    return zoom(c, 1 + .08 * u_(T, t0, 2))
def sc_regla(T, t0):            # la regla
    c = bg("bg_cocina", T, t0, 1.15, 1.25, 3, .5, .4); osc(c, 110); hoja(c, 520, 800, 800, 640)
    titulo(c, "REGLA Nº 1", 520, 640, 150, ROJO, -2, pop(T, t0 + .05, .2), 0)
    frase = "Si quiere contestar…"; n = int(len(frase) * u_(T, WI("X04", 3) - .1, .7)); d = ImageDraw.Draw(c); d.text((220, 800), frase[:n], font=font(F_HAND, 84), fill=TINTA)
    return zoom(c, 1 + .06 * u_(T, t0, 2))
def sc_en_nota(T, t0):          # …va en una nota
    c = plano((14, 60, 70), (10, 14, 40), TUR); rayos(c, T * 2, TUR, 540, 820, 34); k = pop(T, t0, .22)
    put(c, "nota_blanca", 540, 860, 2.0 * k, rot=-6 + 30 * (1 - k)); titulo(c, "EN UNA", 540, 760, 150, TINTA, -6, pop(T, t0 + .08, .2), 0, F_HAND); titulo(c, "NOTA", 540, 930, 230, ROJO, -6, pop(T, WI("X04", 9) - .05, .2), 0)
    chispas(c, 540, 860, T, WI("X04", 9), 14, AMA, 430)
    return c
def sc_amano(T, t0):
    c = plano((14, 60, 70), (10, 14, 40), TUR); rayos(c, T * 2, TUR, 540, 800, 36); k = pop(T, t0, .2)
    put(c, "mano_pluma", 620, 980, 1.5 * k, rot=-6 + 4 * math.sin(T * 8)); titulo(c, "A MANO", 540, 470, 250, AMA, -5, k, 18)
    return c
def sc_amano_q(T, t0):          # Vale: ¿a mano?
    c = bg("bg_cuarto", T, t0, 1.3, 1.42, 1.5, .4, .3); vale(c, "asco", 540, 1180, 1.5, T, "V06")
    return c
def sc_prehistoria(T, t0):
    c = plano((84, 62, 40), (36, 24, 30), (220, 170, 110)); k = pop(T, t0, .22); put(c, "piedra", 540, 660, 1.3 * k, rot=-5)
    d = ImageDraw.Draw(c); u = abs(math.sin(T * 11)); d.line((820, 330 + 50 * u, 690, 500 + 50 * u), fill=OL, width=44); d.line((820, 330 + 50 * u, 690, 500 + 50 * u), fill=(140, 96, 60), width=28)
    d.rounded_rectangle((760, 260 + 50 * u, 910, 360 + 50 * u), 20, fill=(154, 143, 132), outline=OL, width=9)
    vale(c, "asco", 260, 1270, .62, T, "V06"); papel(c, "AÑO 10.000 a. C.", 690, 1080, 60, 5, pop(T, t0 + .2), f=F_ANTON)
    return c
def _hora(c, n, T, t0): papel(c, f"HORA {n}", 215, 370, 96, -7, pop(T, t0, .2), ROSA, BLANCO, F_ANTON)
def sc_hora1(T, t0):            # revisa su bolsillo 14 veces: cuerpo entero, mete la mano y saca el forro vacío
    c = bg("bg_cuarto", T, t0, 1.0, 1.08, 3, .5, .62); tk = WI("V07", 2); q = clamp((T - tk) / 1.3) * 13; n = int(q); ph = q % 1 if 0 < q < 13 else (1 if q >= 13 else 0)
    fuera = ph >= .5 and T >= tk; lay = "vale_cuerpo_c" if n >= 13 else ("vale_cuerpo_b" if fuera else "vale_cuerpo_a")
    put(c, lay, 600 + (9 if fuera else -6), 985 + (-12 if fuera else 0), .72, rot=-2.5 if fuera else 2)
    _hora(c, 1, T, t0); titulo(c, f"x{max(n, 1)}", 215, 720, 175 * (1 + .2 * (1 - abs(ph - .5) * 2 if fuera else 0)), AMA if n < 13 else ROJO, -8, 1 if T >= tk else 0)      # FALLO 1 a propósito: dicen 14 y se queda en 13
    papel(c, "¡vacío!", 215, 900, 70, 4, pop(T, tk + .25), f=F_HAND)
    if fuera and n < 13: chispas(c, 860, 1160, T, tk + (n + .5) * 1.3 / 13, 6, BLANCO, 130)
    return c
def sc_hora2(T, t0):            # le habla al microondas
    c = bg("bg_cocina", T, t0, 1.2, 1.3, 3, .3, .55); put(c, "microondas", 590, 770 + 6 * math.sin(T * 5), 1.0)
    vale(c, "orgullosa", 230, 1270, .68, T, "V07"); _hora(c, 2, T, t0)
    k = pop(T, t0 + .35); d = ImageDraw.Draw(c)
    if k > 0:
        d.rounded_rectangle((440, 1050, 930, 1170), 50, fill=BLANCO, outline=OL, width=8); d.polygon([(470, 1120), (470, 1160), (410, 1190)], fill=BLANCO, outline=OL); d.line((446, 1122, 446, 1156), fill=BLANCO, width=10)
        d.text((685, 1106), "¿y tú qué cuentas?", font=font(F_BAL, 46), fill=OL, anchor="mm")
    titulo(c, "…", 850, 450, 150, TUR, 0, pop(T, t0 + .9))
    return c
def sc_hora3(T, t0):            # escribe su primera nota: LA MISMA nota que luego se enseña
    c = plano((70, 44, 20), (30, 16, 40), AMA); s = 1.95; cx, cy = 520, 860; put(c, "nota_blanca", cx, cy, s)
    u = u_(T, t0 + .1, E("V07") - t0 + .3) * .62
    tip = escribe(c, cx - 220 * s + 10 * s, cy - 180 * s + 22 * s, s, NOTA, u); put(c, "mano_pluma", tip[0] + 290, tip[1] - 250, 1.0, rot=3 * math.sin(T * 30)); _hora(c, 3, T, t0)
    return zoom(c, 1 + .06 * u_(T, t0, 2), .5, .45)
def sc_11min(T, t0):
    c = plano(MOR, MOR2, ROSA); d = ImageDraw.Draw(c); cx, cy, r = 540, 760, 300; d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=PAPEL, outline=OL, width=16)
    for i in range(12): a = i * PI_ / 6; d.line((cx + (r - 50) * math.sin(a), cy - (r - 50) * math.cos(a), cx + (r - 22) * math.sin(a), cy - (r - 22) * math.cos(a)), fill=OL, width=10)
    u = ease(u_(T, t0, .9)); a = 2 * PI_ * 11 / 60 * u * 1; am = a + 2 * PI_ * 4 * (1 - u)
    d.pieslice((cx - r + 40, cy - r + 40, cx + r - 40, cy + r - 40), -90, -90 + math.degrees(a), fill=(255, 93, 115))
    d.line((cx, cy, cx + 230 * math.sin(am), cy - 230 * math.cos(am)), fill=OL, width=16); d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=OL)
    titulo(c, "11 MIN", 540, 1190, 200, AMA, -4, pop(T, WI("V08", 1) - .05, .2)); papel(c, "para 5 palabras", 540, 370, 70, 4, pop(T, t0 + .5), f=F_HAND)
    return c
def sc_salio(T, t0):            # la nota, en grande
    c = plano((14, 60, 70), (10, 14, 40), TUR); rayos(c, T, TUR, 540, 820, 30); k = pop(T, t0 + .05, .3)
    put(c, "nota", 540, 820, 2.25 * k, rot=-6 + 40 * (1 - k)); titulo(c, "¿¿??", 800, 400, 170, ROSA, 10, pop(T, t0 + .5)); papel(c, "mándaselo a quien escribe así", 540, 1225, 52, -2, pop(T, t0 + .8), AMA, f=F_HAND)
    return zoom(c, 1 + .1 * u_(T, t0, 2.2), .5, .44)
def sc_clarisimo(T, t0):        # Vale orgullosa
    c = bg("bg_cuarto", T, t0, 1.1, 1.2, 3, .5, .5); vale(c, "orgullosa", 520, 780, 1.0, T, "V09", "nota")
    d = ImageDraw.Draw(c); d.rounded_rectangle((-30, 1345, W + 30, H + 40), 60, fill=(59, 42, 122), outline=OL, width=10); d.rounded_rectangle((60, 1280, 330, 1410), 60, fill=(185, 138, 214), outline=OL, width=9)
    papel(c, "«clarísimo»", 770, 420, 80, 6, pop(T, WI("V09", 1) - .05), AMA, f=F_HAND)
    return c
def sc_traduce(T, t0):          # lo que ella dice que dice
    c = plano((70, 44, 20), (30, 16, 40), AMA); put(c, "nota", 540, 620, 1.7, rot=-4); d = ImageDraw.Draw(c)
    papel(c, "ESTOY CASTIGDA,", 540, 990, 74, -2, pop(T, WI("V09", 2) - .05), f=F_ANTON); papel(c, "NO TENGO CELULAR", 540, 1115, 74, 2, pop(T, WI("V09", 4) - .05), f=F_ANTON, cinta=False); papel(c, "mándaselo a quien escribe así", 540, 1238, 48, -2, pop(T, WI("V09", 5)), TUR, f=F_HAND, cinta=False)
    papel(c, "según Vale", 240, 330, 60, -8, pop(T, t0 + .1), TUR, f=F_HAND)
    return c
def sc_no(T, t0):
    c = plano((90, 10, 26), (24, 6, 20), ROJO); put(c, "nota", 540, 820, 1.9, rot=-4); k = pop(T, t0, .16); titulo(c, "NO", 540, 800, 520, ROJO, -10, k, 22, sfill=BLANCO)
    return c
def sc_nico_lee(T, t0):
    c = bg("bg_cocina", T, t0, 1.1, 1.2, 2, .6, .5); k = pop(T, t0, .22); put(c, "nico", 420, 1400 - 440 * k, 1.1)
    put(c, "nota", 790, 1040, .9, rot=8 + 3 * math.sin(T * 7)); papel(c, "SU HERMANO", 330, 440, 80, -6, pop(T, t0 + .1), TUR, f=F_ANTON)
    return c
def sc_cocodrilo(T, t0):
    c = plano((20, 70, 50), (12, 20, 40), (95, 196, 106)); rayos(c, T, (95, 196, 106), 540, 760, 34); k = pop(T, WI("V10", 7) - .1, .25)
    papel(c, "ESTOY CASADA", 540, 400, 92, -3, pop(T, t0, .2), f=F_ANTON); papel(c, "CON UN COCODRILO", 540, 1210, 80, 3, k, AMA, f=F_ANTON, cinta=False)
    put(c, "cocodrilo", 540, 800 + 10 * math.sin(T * 6), 1.45 * max(k, .001), rot=4 * math.sin(T * 5)); d = ImageDraw.Draw(c)
    for i in range(5):
        if T >= WI("V10", 7) + i * .08: y = 700 - ((T - WI("V10", 7)) * 160 + i * 90) % 520; corazon(d, 140 + i * 200, y + 300, 34, ROSA)
    return c
def sc_dame(T, t0):             # ¡Nico, dame eso!
    c = bg("bg_cuarto", T, t0, 1.2, 1.3, 1, .5, .4); u = u_(T, t0, 1.4)
    put(c, "nico", 880 + 500 * ease(u_(T, t0 + .5, .7)), 1250, .8); put(c, "nota", 760 + 500 * ease(u_(T, t0 + .5, .7)), 900, .7, rot=20)
    vale(c, "enojada", 380 + 80 * ease(u) + 8 * math.sin(T * 50), 1150, 1.35, T, "V11")
    return c
def sc_nico(T, t0):
    c = bg("bg_cuarto", T, t0, 1.0, 1.1, 3, .7, .5); put(c, "nico", 520, 1020 + 6 * math.sin(T * 4), 1.25)
    papel(c, "NICO", 260, 420, 120, -8, pop(T, t0, .2), ROSA, BLANCO, F_ANTON); papel(c, "9 AÑOS", 780, 520, 80, 6, pop(T, WI("V12", 2) - .05), f=F_ANTON)
    papel(c, "nivel de peligro: ALTO", 540, 1260, 56, -2, pop(T, WI("V12", 3)), AMA, f=F_HAND)
    return c
def sc_tablet(T, t0):
    c = plano((18, 30, 74), (12, 10, 34), TUR); rayos(c, T, TUR, 540, 780, 26); k = pop(T, t0, .22); put(c, "tablet", 520, 780, 1.4 * k, rot=-6 + 3 * math.sin(T * 3))
    return c
def sc_foto(T, t0):
    c = plano((18, 30, 74), (12, 10, 34), TUR); put(c, "tablet", 520, 800, 1.4, rot=-3); tk = WI("V12", 9)
    d = ImageDraw.Draw(c)
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)): x, y = 520 + sx * 290, 800 + sy * 230; d.line((x, y, x - sx * 80, y), fill=BLANCO, width=12); d.line((x, y, x, y - sy * 80), fill=BLANCO, width=12)
    titulo(c, "FOTO GUARDADA", 520, 370, 100, ROJO, -4, pop(T, tk + .12, .2), 12, sfill=BLANCO); flash(c, T, tk, .28)
    return c
def sc_resumen(T, t0):          # 30 días · 0 notas
    c = plano(MOR, MOR2, ROSA); caja_big(c, 290, 740, 1.15, T, shake=6 * math.exp(-(T - t0) * 6))
    k = pop(T, WI("V13", 2) - .05, .22); put(c, "nota", 780, 840, 1.0 * max(k, .001), rot=7); titulo(c, "0", 780, 480, 300, AMA, 6, k, 16)
    papel(c, "NOTAS QUE SE ENTIENDEN", 540, 1080, 62, -2, pop(T, WI("V13", 3)), f=F_ANTON); papel(c, "guárdalo: el día 30 comparamos su letra", 540, 1225, 46, 2, pop(T, WI("V13", 5)), TUR, f=F_HAND, cinta=False)
    return c
def sc_tu(T, t0):
    c = bg("bg_cuarto", T, t0, 1.1, 1.25, 2, .5, .4); rayos(c, T * 2, AMA, 540, 900, 30); vale(c, "aburrida", 500, 1340, 1.05, T, None, "senala")
    titulo(c, "TÚ DECIDES", 540, 480, 150, AMA, -4, pop(T, WI("X05", 3) - .05, .2), 16); papel(c, "guárdalo: el día 30 comparamos su letra", 540, 625, 44, 2, pop(T, WI("X05", 3) + .3), TUR, f=F_HAND, cinta=False)
    return zoom(c, 1 + .06 * u_(T, t0, 2), .5, .7)
def _duo(c, T, da=0, ra=0, t0=0, cambiado=False):
    d = ImageDraw.Draw(c); d.rectangle((0, 0, 540, H), fill=(92, 22, 60)); d.rectangle((540, 0, W, H), fill=(18, 78, 92))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    for i in range(6): corazon(dl, 60 + (i * 97) % 440, 1500 - ((T * 90 + i * 260) % 1300), 26 + 6 * (i % 3), (255, 93, 115, 120))
    for i in range(6): x = 600 + (i * 83) % 420; y = 1500 - ((T * 90 + i * 240) % 1300); dl.polygon([(x, y - 30), (x + 9, y - 9), (x + 30, y), (x + 9, y + 9), (x, y + 30), (x - 9, y + 9), (x - 30, y), (x - 9, y - 9)], fill=(43, 212, 196, 130))
    c.alpha_composite(lay)
    put(c, "dani", 270, 850 + 6 * math.sin(T * 3), .62); put(c, "renata", 810, 850 + 6 * math.sin(T * 3 + 1), .62)
    papel(c, "DANI", 270, 520, 100, -5, 1, ROSA, BLANCO, F_ANTON); papel(c, "RENATA", 810, 520, 88, 5, 1, TUR, OL, F_ANTON)
    e1, e2 = ("su mejor amiga", "el que le gusta") if cambiado else ("el que le gusta", "su mejor amiga")      # FALLO 3: en el cierre van cambiadas
    papel(c, e1, 270, 1180, 46, 3, 1, f=F_HAND, cinta=False); papel(c, e2, 810, 1180, 46, -3, 1, f=F_HAND, cinta=False)
    osc(c, da, (0, 0, 540, H)); osc(c, ra, (540, 0, W, H)); d = ImageDraw.Draw(c); d.line((540, 0, 540, H), fill=OL, width=14)
def sc_duo(T, t0):
    c = plano(); tr = WI("X05", 11) - .05; _duo(c, T, 165 if T >= tr else 0, 165 if T < tr else 0); return c
def sc_ojo(T, t0):              # alguien más va a leer esa nota
    c = plano((10, 8, 26), (4, 3, 12)); d = ImageDraw.Draw(c); u = ease(u_(T, t0, .5))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).ellipse((240, 520, 840, 1120), fill=(255, 246, 220, 60)); c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(70)))
    put(c, "nota", 540, 830, 1.25, rot=-5 + 2 * math.sin(T * 2))
    bl = 1 if (T - t0) % 1.6 > .12 else .1
    for ex in (410, 670): d.ellipse((ex - 62, 380 - 40 * bl * u, ex + 62, 380 + 40 * bl * u), fill=BLANCO); d.ellipse((ex - 22 + 14 * math.sin(T * 2), 380 - 22 * bl * u, ex + 22 + 14 * math.sin(T * 2), 380 + 22 * bl * u), fill=OL)
    titulo(c, "?", 540, 1150, 170, ROJO, 0, pop(T, WI("V15", 1), .25), 14, sfill=BLANCO)
    return zoom(c, 1 + .08 * u_(T, t0, 2.5))
def sc_final(T, t0):
    c = plano(); _duo(c, T, cambiado=True); k = pop(T, t0, .22); papel(c, "COMENTA", 540, 340, 80, 0, k, AMA, OL, F_ANTON, cinta=False)
    put(c, "nota", 540, 1010, .55 * max(k, .001), rot=-8 + 4 * math.sin(T * 3)); return c
def telefono(c, cx, cy, s, hora, notifs, T, vib=0):
    """Celular con pantalla de bloqueo: hora y notificaciones (nombre, texto, t_aparece, borrado)."""
    cx += vib * math.sin(T * 90); put(c, "celular_limpio", cx, cy, s, rot=vib * .25 * math.sin(T * 70)); d = ImageDraw.Draw(c)
    d.text((cx, cy - 150 * s), hora, font=font(F_ANTON, 64 * s), fill=(214, 222, 240), anchor="mm"); d.text((cx, cy - 104 * s), "jueves 26 de noviembre", font=font(F_BAL, 15 * s), fill=(150, 158, 190), anchor="mm")
    y = cy - 70 * s
    for nombre, txt, ta, borrado in notifs:
        k = pop(T, ta, .2)
        if k <= 0: continue
        w, h = 206 * s * min(1, k), 58 * s; x0 = cx - w / 2
        d.rounded_rectangle((x0, y, x0 + w, y + h), int(14 * s), fill=(58, 55, 100) if not borrado else (40, 36, 66), outline=(120, 116, 180), width=max(2, int(1.5 * s)))
        if k > .9:
            d.ellipse((x0 + 8 * s, y + 10 * s, x0 + 46 * s, y + 48 * s), fill=(255, 93, 115)); d.text((x0 + 27 * s, y + 28 * s), "D", font=font(F_ANTON, 24 * s), fill=BLANCO, anchor="mm")
            d.text((x0 + 54 * s, y + 18 * s), nombre, font=font(F_BAL, 15 * s), fill=BLANCO, anchor="lm")
            if borrado:
                d.ellipse((x0 + 54 * s, y + 31 * s, x0 + 68 * s, y + 45 * s), outline=(160, 160, 190), width=max(2, int(1.6 * s))); d.line((x0 + 57 * s, y + 42 * s, x0 + 65 * s, y + 34 * s), fill=(160, 160, 190), width=max(2, int(1.6 * s)))
                d.text((x0 + 73 * s, y + 38 * s), txt, font=font(F_BAL, 12.5 * s), fill=(160, 160, 190), anchor="lm")
            else: d.text((x0 + 54 * s, y + 38 * s), txt, font=font(F_BAL, 14 * s), fill=(214, 222, 240), anchor="lm")
        y += h + 9 * s
def sc_msg(T, t0):              # FOTOGRAMA 0: el celular vibra, mensaje de Dani
    c = plano((26, 18, 64), (8, 6, 22), (120, 90, 255)); rayos(c, T * 2, (120, 90, 255), 540, 820, 30)
    telefono(c, 540, 1000, 2.9, "23:58", [], T, 9 * math.exp(-(T - t0) * 2.2))
    d = ImageDraw.Draw(c); d.rounded_rectangle((96, 1010, 984, 1216), 56, fill=(0, 0, 0, 255)); d.rounded_rectangle((90, 1000, 978, 1206), 56, fill=BLANCO, outline=OL, width=9)
    d.ellipse((120, 1034, 258, 1172), fill=ROSA, outline=OL, width=7); d.text((189, 1101), "D", font=font(F_ANTON, 92), fill=BLANCO, anchor="mm")
    d.text((290, 1062), "Dani · ahora", font=font(F_BAL, 44), fill=(120, 116, 150), anchor="lm"); d.text((290, 1136), "tengo que decirte algo…", font=font(F_BAL, 56), fill=OL, anchor="lm")
    for sx_ in (-1, 1):
        for i in range(3): x = 540 + sx_ * (455 + i * 30 + 12 * math.sin(T * 30)); d.arc((x - 30, 640, x + 30, 900), -60 if sx_ > 0 else 120, 60 if sx_ > 0 else 240, fill=BLANCO, width=9)
    return zoom(c, 1.1 - .1 * ease(u_(T, t0, .4)) + .04 * u_(T, t0, 2), .5, .4)
def sc_msg2(T, t0):             # Vale lo ve… "tengo que decirte algo"
    c = bg("bg_cuarto", T, t0, 1.2, 1.32, 2, .5, .35); osc(c, 80); vale(c, "orgullosa", 500, 1240, 1.15, T)
    d = ImageDraw.Draw(c); k = pop(T, t0, .2)
    if k > 0:
        d.rounded_rectangle((150, 330, 930, 560), 60, fill=BLANCO, outline=OL, width=9); d.polygon([(600, 552), (700, 552), (640, 640)], fill=BLANCO, outline=OL); d.line((606, 552, 694, 552), fill=BLANCO, width=12)
        d.ellipse((180, 370, 320, 510), fill=ROSA, outline=OL, width=7); d.text((250, 440), "D", font=font(F_ANTON, 90), fill=BLANCO, anchor="mm")
        d.text((350, 400), "Dani", font=font(F_BAL, 50), fill=(120, 116, 150), anchor="lm"); frase = "tengo que decirte algo…"; n = int(len(frase) * u_(T, t0 + .1, .7)); d.text((350, 472), frase[:n], font=font(F_BAL, 50), fill=OL, anchor="lm")
    d = ImageDraw.Draw(c)
    for i in range(4):
        if T >= t0 + .5 + i * .1: corazon(d, 760 + i * 44 - 20 * (i % 2), 700 - ((T - t0) * 120 + i * 40) % 220 + 110, 22, ROSA)
    return c
def sc_msg3(T, t0): return zoom(sc_msg2(T, sp("X01", 3)), 1.3 + .06 * u_(T, t0, 2), .5, .2)      # mismo momento, más cerca
def sc_buzz(T, t0):             # la caja vibra: mensajes que nadie va a leer
    c = bg("bg_cocina", T, t0, 1.1, 1.2, 3, .5, .62); osc(c, 150); n = sum(1 for i in range(4) if T >= WI("X06", 1) + i * .42)
    caja_big(c, 540, 940, 1.9, T, shake=10 * max(0, math.sin((T - WI("X06", 1)) * 2 * PI_ / .42)) if T >= WI("X06", 1) else 0)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).ellipse((300, 760, 780, 1240), fill=(140, 120, 255, 90)); c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(80)))
    if n: d = ImageDraw.Draw(c); k = pop(T, WI("X06", 1) + (n - 1) * .42, .18); r_ = 86 * k; d.ellipse((820 - r_, 560 - r_, 820 + r_, 560 + r_), fill=ROJO, outline=OL, width=9); titulo(c, f"+{n}", 820, 556, 104, BLANCO, 0, k, 0)      # FALLO 3 a propósito: dicen 3 y llegan 4
    titulo(c, "BZZZ", 240, 520, 120, AMA, -10, pop(T, WI("X06", 1), .2))
    return c
def sc_borrado(T, t0):          # …y el último lo borró
    c = plano((14, 10, 34), (4, 3, 12), (90, 70, 200)); tb = WI("X06", 10) - .1
    telefono(c, 520, 740, 2.05, "00:07", [("Dani", "¿hola?", t0 - 1, False), ("Dani", "¿estás?", t0 - 1, False), ("Dani", "ok…", t0 - 1, False), ("Dani", "Se eliminó este mensaje" if T >= tb else "Vale, la verdad es que…", t0 + .1, T >= tb)], T)
    flash(c, T, tb, .15); titulo(c, "BORRADO", 540, 1205, 112, ROJO, -5, pop(T, tb, .2), 14, sfill=BLANCO)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    for x in (120, 330, 760, 940): dl.line((x, 0, x - 260, H), fill=(190, 230, 245, 26), width=46)
    c.alpha_composite(lay); put(c, "candado", 880, 420, .5, rot=10)
    return zoom(c, 1 + .07 * u_(T, t0, 2.5), .5, .45)

def sp(lid, i, d=-.06): return WI(lid, i) + d
# ================================================================ DÍA 1 de 30 s: "¿Puedes leer esta nota?"
def nota_rota(c, cx, cy, s, sep, T):
    """La nota de Dani partida en dos mitades con borde en zigzag."""
    im = R.layer("nota_dani"); w, h = im.size; k = s / 2; im = im.resize((int(w * k), int(h * k)), Image.BICUBIC); w, h = im.size
    zig = [(w / 2 + (14 if i % 2 else -14) * s, i * h / 9) for i in range(10)]
    for lado in (-1, 1):
        m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).polygon(([(0, 0)] + zig + [(0, h)]) if lado < 0 else ([(w, 0)] + zig + [(w, h)]), fill=255)
        p = Image.new("RGBA", (w, h), (0, 0, 0, 0)); p.paste(im, (0, 0), m); p = p.rotate(-lado * (7 + 2 * math.sin(T * 5)), resample=Image.BICUBIC, expand=True)
        c.alpha_composite(p, (int(cx - p.width / 2 + lado * sep), int(cy - p.height / 2 + 10 * lado)))
def c_reto(T, t0):              # FOTOGRAMA 0: la nota ilegible y el reto
    c = plano((70, 44, 20), (24, 12, 40), AMA); rayos(c, T * 1.5, AMA, 540, 860, 30)
    put(c, "nota", 540, 880, 2.25, rot=-3 + 1.5 * math.sin(T * 3)); titulo(c, "¿PUEDES LEERLA?", 540, 380, 132, AMA, -3, .92 + .08 * back(u_(T, t0, .2)), 16)
    for i, (x, y) in enumerate(((150, 640), (930, 600), (900, 1180))): titulo(c, "?", x, y, 150 - 20 * i, ROSA, 14 - 14 * i, pop(T, t0 + .25 + i * .15))
    return zoom(c, 1 + .1 * u_(T, t0, 1.6), .5, .46)
def c_tampoco(T, t0):           # Vale tampoco
    c = bg("bg_cuarto", T, t0, 1.1, 1.2, 2, .5, .5); vale(c, "aburrida", 520, 800, 1.0, T, None, "nota")
    d = ImageDraw.Draw(c); d.rounded_rectangle((-30, 1345, W + 30, H + 40), 60, fill=(59, 42, 122), outline=OL, width=10)
    papel(c, "VALE", 240, 430, 120, -8, pop(T, t0, .2), AMA, f=F_ANTON); titulo(c, "¿¿??", 820, 470, 150, ROSA, 10, pop(T, t0 + .3))
    return c
def c_ella(T, t0):              # …y la escribió ella
    c = bg("bg_cuarto", T, t0, 1.25, 1.38, 2, .5, .4); vale(c, "orgullosa", 520, 940, 1.3, T, None, "nota")
    papel(c, "LA ESCRIBIÓ ELLA", 540, 420, 84, -3, pop(T, t0, .2), ROSA, BLANCO, F_ANTON)
    return c
def c_15(T, t0):
    c = bg("bg_cuarto", T, t0, 1.0, 1.1, 3, .5, .5); vale(c, "aburrida", 560, 1150, 1.15, T)
    papel(c, "15 AÑOS", 250, 480, 100, -7, pop(T, t0, .2), TUR, OL, F_ANTON); papel(c, "letra: 1/10", 800, 560, 64, 6, pop(T, t0 + .25), f=F_HAND)
    return c
def c_9h(T, t0):                # tiempo de pantalla
    c = plano((18, 30, 74), (12, 10, 34), TUR); d = ImageDraw.Draw(c)
    x0, y0, x1, y1 = 190, 330, 890, 1290; d.rounded_rectangle((x0, y0, x1, y1), 70, fill=(42, 39, 72), outline=OL, width=14); d.rounded_rectangle((x0 + 34, y0 + 70, x1 - 34, y1 - 70), 24, fill=(16, 14, 34))
    d.text((540, 480), "TIEMPO DE PANTALLA", font=font(F_BAL, 46), fill=(170, 176, 214), anchor="mm")
    u = ease(u_(T, t0 + .03, .5)); n = int(round(9 * u)); d.text((540, 640), f"{n} h {int(4 * u):02d} min", font=font(F_ANTON, 150), fill=TUR if n < 9 else ROJO, anchor="mm")
    for i, hh in enumerate([5, 7, 6, 8, 9, 9, 9]):
        bx = 280 + i * 78; bh = 360 * hh / 9 * ease(u_(T, t0 + .05 + i * .04, .3)); d.rounded_rectangle((bx, 1150 - bh, bx + 52, 1150), 10, fill=ROJO if hh == 9 else TUR); d.text((bx + 26, 1185), "LMXJVSD"[i], font=font(F_BAL, 34), fill=(170, 176, 214), anchor="mm")
    papel(c, "AL DÍA", 770, 810, 70, 7, pop(T, WI("Y03", 4)), ROSA, BLANCO, F_ANTON)
    return zoom(c, 1.03 + .05 * u_(T, t0, 1.5))
def c_anoche(T, t0):            # …hasta anoche (FALLO a propósito: el reloj marca 25:59)
    c = plano((20, 12, 44), (4, 3, 12)); telefono(c, 540, 830, 2.2, "25:59", [], T, 8 * math.exp(-(T - t0) * 3)); osc(c, 150 * u_(T, t0 + .25, .5), (300, 380, 780, 1300))
    titulo(c, "HASTA ANOCHE", 540, 1215, 118, ROJO, -4, pop(T, t0 + .05, .2), 14, sfill=BLANCO)
    return c
def c_caja(T, t0):              # su mamá lo encerró
    c = bg("bg_cocina", T, t0, 1.0, 1.1, 3, .5, .62); rayos(c, T, ROSA, 540, 900, 20); tk = WI("Y04", 3); u = u_(T, tk - .16, .16)
    caja_big(c, 540, 960, 1.95, T, shake=10 * math.exp(-(T - tk) * 9) if T >= tk else 0)
    put(c, "mano_mama", 1250 - 470 * ease(u_(T, t0, .22)) + 300 * ease(u_(T, tk + .4, .3)), 1040, .85)
    if T >= tk: chispas(c, 540, 1040, T, tk, 12, AMA, 330); titulo(c, "¡CLIC!", 300, 400, 130, AMA, 8, pop(T, tk, .2))
    flash(c, T, tk, .12)
    return c
def c_regla(T, t0):
    c = bg("bg_cocina", T, t0, 1.15, 1.25, 3, .5, .4); osc(c, 110); hoja(c, 520, 800, 800, 640)
    titulo(c, "REGLA Nº 1", 520, 640, 150, ROJO, -2, pop(T, t0 + .03, .2), 0)
    frase = "Todo lo que quiera decir…"; n = int(len(frase) * u_(T, WI("Y04", 9) - .1, .8)); ImageDraw.Draw(c).text((220, 800), frase[:n], font=font(F_HAND, 84), fill=TINTA)
    return zoom(c, 1 + .06 * u_(T, t0, 2))
def c_en_nota(T, t0):
    c = plano((14, 60, 70), (10, 14, 40), TUR); rayos(c, T * 2, TUR, 540, 820, 34); k = pop(T, t0, .2)
    put(c, "nota_blanca", 540, 860, 2.0 * k, rot=-6 + 30 * (1 - k)); titulo(c, "EN UNA", 540, 760, 150, TINTA, -6, pop(T, t0 + .06, .2), 0, F_HAND); titulo(c, "NOTA", 540, 930, 230, ROJO, -6, pop(T, WI("Y04", 17) - .05, .2), 0)
    chispas(c, 540, 860, T, WI("Y04", 17), 14, AMA, 430)
    return c
def c_vuela(T, t0):             # la primera fue para…
    c = plano((70, 14, 60), (24, 10, 44), ROSA); u = ease(u_(T, t0, .9)); x = 160 + 760 * u; y = 900 - 320 * math.sin(u * PI_)
    d = ImageDraw.Draw(c)
    for i in range(10):
        uu = max(0, u - i * .03); d.ellipse((160 + 760 * uu - 10, 900 - 320 * math.sin(uu * PI_) - 10 + 130, 160 + 760 * uu + 10, 900 - 320 * math.sin(uu * PI_) + 10 + 130), fill=BLANCO)
    put(c, "nota", x, y, .9, rot=-20 + 400 * u); papel(c, "NOTA Nº 1", 300, 430, 96, -6, pop(T, t0, .2), AMA, f=F_ANTON)
    return c
def c_dani(T, t0):
    c = plano((92, 22, 60), (30, 10, 40), ROSA); rayos(c, T * 2, ROSA, 540, 860, 36); k = pop(T, t0, .22); put(c, "dani", 540, 1560 - 600 * k, 1.15)
    papel(c, "DANI", 250, 440, 130, -7, pop(T, t0 + .05, .2), ROSA, BLANCO, F_ANTON); papel(c, "el que le gusta", 790, 540, 60, 6, pop(T, WI("Y05", 7)), f=F_HAND)
    d = ImageDraw.Draw(c)
    for i in range(6): corazon(d, 120 + i * 170, 1180 - ((T - t0) * 260 + i * 130) % 760, 30 + 6 * (i % 3), (255, 143, 163))
    return c
def c_clarisimo(T, t0):
    c = bg("bg_cuarto", T, t0, 1.1, 1.2, 3, .5, .5); vale(c, "orgullosa", 520, 780, 1.0, T, "Y06", "nota")
    d = ImageDraw.Draw(c); d.rounded_rectangle((-30, 1345, W + 30, H + 40), 60, fill=(59, 42, 122), outline=OL, width=10); d.rounded_rectangle((60, 1280, 330, 1410), 60, fill=(185, 138, 214), outline=OL, width=9)
    papel(c, "«clarísimo»", 770, 420, 80, 6, pop(T, WI("Y06", 1) - .05), AMA, f=F_HAND)
    return c
def c_traduce(T, t0):           # lo que ELLA dice que pone (FALLO a propósito: SÁBDO)
    c = plano((70, 44, 20), (30, 16, 40), AMA); put(c, "nota", 540, 610, 1.7, rot=-4)
    papel(c, "¿VAMOS AL CINE", 540, 990, 78, -2, pop(T, t0, .2), f=F_ANTON); papel(c, "EL SÁBDO?", 540, 1115, 78, 2, pop(T, WI("Y06", 5) - .05), f=F_ANTON, cinta=False)
    papel(c, "según Vale", 240, 320, 60, -8, pop(T, t0 + .1), TUR, f=F_HAND); papel(c, "mándaselo a quien escribe así", 540, 1238, 48, -2, pop(T, WI("Y06", 6)), TUR, f=F_HAND, cinta=False)
    return c
def c_dani_lee(T, t0):
    c = plano((92, 22, 60), (30, 10, 40), ROSA); put(c, "dani", 400, 1030 + 5 * math.sin(T * 4), 1.1); put(c, "nota", 800, 1050, .85, rot=8 + 3 * math.sin(T * 7))
    papel(c, "DANI LEYÓ…", 540, 420, 100, -4, pop(T, t0, .2), f=F_ANTON); titulo(c, "?", 830, 720, 190, AMA, 10, pop(T, t0 + .2))
    return c
def c_vomite(T, t0):
    c = plano((30, 84, 40), (12, 26, 30), (120, 220, 90)); rayos(c, T * 2, (120, 220, 90), 540, 800, 36); d = ImageDraw.Draw(c); rr = random.Random(4)
    k = pop(T, t0, .22)
    for i in range(14):                                                  # salpicón verde
        a = rr.uniform(0, 2 * PI_); q = rr.uniform(120, 400) * min(1, k); r_ = rr.uniform(26, 70); x, y = 540 + q * math.cos(a), 800 + q * math.sin(a) * .8; d.ellipse((x - r_, y - r_, x + r_, y + r_), fill=(126, 211, 79), outline=OL, width=7)
    d.ellipse((540 - 240 * k, 800 - 200 * k, 540 + 240 * k, 800 + 200 * k), fill=(126, 211, 79), outline=OL, width=8)
    if k > .5:                                                           # cubo de palomitas
        d.polygon([(410, 700), (670, 700), (630, 980), (450, 980)], fill=(255, 93, 115), outline=OL); d.line([(410, 700), (670, 700), (630, 980), (450, 980), (410, 700)], fill=OL, width=9)
        for i in range(3): d.polygon([(462 + i * 72, 704), (498 + i * 72, 704), (492 + i * 60, 976), (468 + i * 60, 976)], fill=PAPEL)
        for i in range(9): x = 420 + rr.uniform(0, 240); y = 640 + rr.uniform(-30, 50); d.ellipse((x - 30, y - 26, x + 30, y + 26), fill=(255, 236, 170), outline=OL, width=6)
        d.text((540, 850), "CINE", font=font(F_ANTON, 70), fill=OL, anchor="mm")
    papel(c, "VOMITÉ EN EL CINE", 540, 410, 88, -3, pop(T, t0 + .02, .2), f=F_ANTON); papel(c, "EL SÁBADO", 540, 1180, 96, 3, pop(T, WI("Y07", 6) - .05), AMA, f=F_ANTON, cinta=False)
    return c
def c_respuesta(T, t0):         # Dani ya contestó (FALLO a propósito: "para: BALE")
    c = plano((18, 30, 74), (8, 8, 26), (120, 170, 255)); rayos(c, T * 2, (120, 170, 255), 540, 840, 34); k = pop(T, t0, .24)
    put(c, "nota_dani", 540, 860 + 300 * (1 - min(1, k)), 2.1 * max(k, .001), rot=-5 + 24 * (1 - min(1, k)) + 2 * math.sin(T * 5)); chispas(c, 540, 860, T, t0 + .15, 16, AMA, 470)
    papel(c, "RESPUESTA DE DANI", 540, 400, 84, -3, pop(T, t0 + .1, .2), ROSA, BLANCO, F_ANTON)
    return zoom(c, 1 + .08 * u_(T, t0, 1.6))
def c_tu(T, t0):
    c = bg("bg_cuarto", T, t0, 1.1, 1.25, 2, .5, .4); rayos(c, T * 2, AMA, 540, 900, 30); vale(c, "aburrida", 500, 1340, 1.05, T, None, "senala")
    titulo(c, "TÚ DECIDES", 540, 480, 150, AMA, -4, pop(T, t0, .2), 16); papel(c, "guárdalo: el día 30 comparamos su letra", 540, 625, 44, 2, pop(T, t0 + .3), TUR, f=F_HAND, cinta=False)
    return zoom(c, 1 + .06 * u_(T, t0, 2), .5, .7)
def _dos(c, T, da=0, ra=0):
    d = ImageDraw.Draw(c); d.rectangle((0, 0, 540, H), fill=(16, 70, 96)); d.rectangle((540, 0, W, H), fill=(96, 20, 44))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).ellipse((40, 620, 500, 1080), fill=(255, 240, 170, 110)); c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(70)))
    put(c, "nota_dani", 270, 850 + 8 * math.sin(T * 3), 1.0, rot=-6 + 3 * math.sin(T * 4)); chispas(c, 270, 850, T, int(T * 2) / 2, 8, AMA, 260)
    nota_rota(c, 810, 850, 1.0, 46 + 10 * math.sin(T * 6), T)
    papel(c, "ABRIR", 270, 520, 104, -5, 1, TUR, OL, F_ANTON); papel(c, "ROMPER", 810, 520, 96, 5, 1, ROJO, BLANCO, F_ANTON)
    papel(c, "y saber qué dice", 270, 1150, 46, 3, 1, f=F_HAND, cinta=False); papel(c, "sin leerla nunca", 810, 1150, 46, -3, 1, f=F_HAND, cinta=False)
    osc(c, da, (0, 0, 540, H)); osc(c, ra, (540, 0, W, H)); ImageDraw.Draw(c).line((540, 0, 540, H), fill=OL, width=14)
def c_dos(T, t0):
    c = plano(); tr = WI("Y09", 6) - .05; _dos(c, T, 165 if T >= tr else 0, 165 if T < tr else 0); return c
def c_palabra(T, t0):           # una sola palabra
    c = plano((10, 8, 26), (4, 3, 12)); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).ellipse((200, 480, 880, 1160), fill=(207, 230, 255, 70)); c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(80)))
    d = ImageDraw.Draw(c); d.rounded_rectangle((176, 596, 916, 1076), 12, fill=(0, 0, 0)); d.rounded_rectangle((160, 580, 900, 1060), 12, fill=(207, 230, 255), outline=OL, width=9); d.line((160, 820, 900, 820), fill=(160, 190, 225), width=5)
    w = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(w).text((530, 815), "xxxxxx", font=font(F_HAND, 230), fill=TINTA + (255,), anchor="mm"); c.alpha_composite(w.filter(ImageFilter.GaussianBlur(22)))
    titulo(c, "1 PALABRA", 540, 400, 150, AMA, -4, pop(T, WI("Y10", 6) - .05, .2), 16)
    return zoom(c, 1 + .1 * u_(T, t0, 2.6), .5, .43)
def c_final(T, t0):
    c = plano(); _dos(c, T); papel(c, "COMENTA", 540, 340, 84, 0, pop(T, t0, .2), AMA, OL, F_ANTON, cinta=False); return c

SC = [(0, c_reto), (S("Y02") - .04, c_tampoco), (sp("Y02", 2), c_ella), (S("Y03") - .05, c_15), (sp("Y03", 2), c_9h), (sp("Y03", 9), c_anoche),
      (S("Y04") - .05, c_caja), (sp("Y04", 4), sc_30), (sp("Y04", 6), c_regla), (sp("Y04", 14), c_en_nota), (sp("Y04", 18), sc_amano),
      (S("Y05") - .05, c_vuela), (sp("Y05", 4), c_dani), (S("Y06") - .05, c_clarisimo), (sp("Y06", 2), c_traduce),
      (S("Y07") - .05, c_dani_lee), (sp("Y07", 2), c_vomite), (S("Y08") - .06, c_respuesta), (S("Y09") - .06, c_tu), (sp("Y09", 2), c_dos),
      (S("Y10") - .08, c_palabra), (S("Y11") - .08, c_final)]
SC.sort(key=lambda x: x[0])
SCENES = SC

def draw_hud(c, T):
    d = ImageDraw.Draw(c); x0, y0, x1, y1 = 200, 176, 880, 250
    d.rounded_rectangle((x0 + 5, y0 + 7, x1 + 5, y1 + 7), 37, fill=(0, 0, 0, 120)); d.rounded_rectangle((x0, y0, x1, y1), 37, fill=(22, 18, 42), outline=TUR, width=5)
    d.ellipse((x0 + 22, y0 + 24, x0 + 48, y0 + 50), fill=ROJO if int(T * 2) % 2 == 0 else (120, 30, 40))
    d.text((x0 + 66, (y0 + y1) / 2 - 1), "DÍA 1 DE 30", font=font(F_ANTON, 42), fill=BLANCO, anchor="lm")
    d.text((x1 - 28, (y0 + y1) / 2 - 1), "NOTAS: 0  ·  LETRA: 1/10", font=font(F_ANTON, 36), fill=AMA, anchor="rm")

def draw_caption(c, T):
    cy = 1372
    for idx, (t0, t1, g, who, lid) in enumerate(CH):
        nxt0 = CH[idx + 1][0] if idx + 1 < len(CH) else 1e9
        if not (t0 - .04 <= T < t1 + .3) or T >= nxt0 - .04: continue
        d = ImageDraw.Draw(c); size = 108; maxw = 880; f = font(F_ANTON, size); sp_ = d.textlength(" ", font=f)
        widths = [d.textlength(p, font=f) for p, _, _ in g]; total = sum(widths) + sp_ * (len(g) - 1)
        if total > maxw:
            size = int(size * maxw / total); f = font(F_ANTON, size); sp_ = d.textlength(" ", font=f); widths = [d.textlength(p, font=f) for p, _, _ in g]; total = sum(widths) + sp_ * (len(g) - 1)
        x = 540 - total / 2
        for (p, (ws, we), star), wd in zip(g, widths):
            if T >= ws - .04:
                k = .8 + .2 * back((T - ws + .04) / .13); col = (AMA if who == "N" else TUR) if star else BLANCO
                d.text((x + wd / 2, cy), p, font=font(F_ANTON, size * k), fill=col, anchor="mm", stroke_width=12, stroke_fill=(14, 10, 26))
            x += wd + sp_
        return

IMPACTS = [.02, WI("Y04", 3), sp("Y07", 2)]
@lru_cache(1)
def acabado():
    """Acabado de cómic: trama de puntos muy suave + viñeta. Se aplica a todos los fotogramas."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); a = np.zeros((H, W, 4), np.uint8)
    u = (xx * .866 + yy * .5) % 14 - 7; v = (-xx * .5 + yy * .866) % 14 - 7; dots = (u * u + v * v) < 7.5
    vg = np.clip((((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .6)) ** 2 - .55) * 1.5, 0, 1)
    a[..., 3] = (vg * 150).astype(np.uint8); suave = dots & (vg < .04); a[suave, 0:3] = 255; a[suave, 3] = 11
    return Image.fromarray(a, "RGBA")

def frame(T):
    idx = max(i for i, (t, f) in enumerate(SCENES) if T >= t); t0, fn = SCENES[idx]; c = fn(T, t0)
    z = 1 + (.085 * (1 - ease((T - t0) / .2)) if idx > 0 else 0)          # golpe de zoom en cada corte
    z += sum(.022 * math.exp(-(T - ch[0]) * 9) for ch in CH if 0 <= T - ch[0] < .5)
    amp = sum(16 * math.exp(-(T - ti) * 7) for ti in IMPACTS if 0 <= T - ti < .6)
    if z > 1.002 or amp > .6:
        cc = c.resize((int(W * z), int(H * z)), Image.BILINEAR); ox = (cc.width - W) // 2 + int(amp * math.sin(T * 80)); oy = (cc.height - H) // 2 + int(amp * math.cos(T * 67))
        ox = max(0, min(cc.width - W, ox)); oy = max(0, min(cc.height - H, oy)); c = cc.crop((ox, oy, ox + W, oy + H))
    c.alpha_composite(acabado()); draw_hud(c, T); draw_caption(c, T)
    return c.convert("RGB")

def render_scene(i, out):
    t0 = SCENES[i][0]; t1 = SCENES[i + 1][0] if i + 1 < len(SCENES) else TOTAL
    f0, f1 = round(t0 * FPS), round(t1 * FPS); tmp = out + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in range(f0, f1): p.stdin.write(frame(f / FPS).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0: os.replace(tmp, out)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "still":
        for t in sys.argv[2:]: frame(float(t)).save(os.path.join(TMP, f"f_{float(t):06.2f}.jpg"), quality=86)
    elif cmd == "info":
        print(json.dumps({k: [round(a, 2), round(b, 2)] for k, (a, b) in TL.items()}), round(TOTAL, 2)); print(len(SCENES), [(round(t, 2), f.__name__) for t, f in SCENES])
    elif cmd == "mid":
        for i, (t, f) in enumerate(SCENES):
            t1 = SCENES[i + 1][0] if i + 1 < len(SCENES) else TOTAL; frame(t + (t1 - t) * .8).save(os.path.join(TMP, f"m{i:02d}_{f.__name__}.jpg"), quality=80)
    elif cmd == "scenes":
        from multiprocessing import Pool
        ids = [int(x) for x in sys.argv[2:]] or list(range(len(SCENES)))
        with Pool(2) as pool: pool.starmap(render_scene, [(i, os.path.join(TMP, f"s{i:02d}.mp4")) for i in ids])
