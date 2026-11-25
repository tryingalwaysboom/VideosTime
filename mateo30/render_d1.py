"""Temporada "Mateo: 30 días para no repetir" · DÍA 1 — La nota.
Mundo visual nuevo (pizarra verde, tiza amarilla, rojo de corrección), barra FALTAN X DÍAS + imanes M-A-T-E-O,
subtítulos palabra a palabra y cierre con dos tarjetas de una palabra.
Uso: python3 render_d1.py still 1 5 | scenes [i...] | info"""
import os, sys, math, json, subprocess, random
from functools import lru_cache
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["GUION"] = "guion_d1"; os.environ["VOZDIR"] = os.path.join(HERE, "voz_d1")
sys.path.insert(0, HERE)
import importlib.util
_spec = importlib.util.spec_from_file_location("R", os.path.join(HERE, "..", "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

R.LAY = os.path.join(HERE, "layers"); R.layer.cache_clear(); R.scaled.cache_clear()
TMP = os.path.join(HERE, "tmp_d1"); os.makedirs(TMP, exist_ok=True)
W, H, FPS = R.W, R.H, R.FPS
put, ease, clamp, back, font, mouth, bg = R.put, R.ease, R.clamp, R.back, R.font, R.mouth, R.bg
F_ANTON = R.F_ANTON
MF = os.path.join(HERE, "..", "mateo-pov", "fonts")
F_HAND = os.path.join(MF, "Caveat.ttf"); F_BAL = os.path.join(MF, "Baloo2-ExtraBold.ttf"); F_AND = os.path.join(MF, "Andika-Bold.ttf")
PI_ = math.pi
OL = (29, 22, 48); PIZ = (36, 82, 66); PIZ2 = (25, 60, 48); TIZA = (246, 244, 232); AMA = (255, 212, 84)
ROJO = (226, 72, 59); CREMA = (255, 253, 244); AZUL = (63, 127, 208); MADERA = (176, 122, 72)
DIAS_FALTAN = 30; LETRAS_ON = ""          # Día 1: ninguna letra dominada

# ---------------------------------------------------------------- tiempos
R.GAP.clear()
R.GAP.update({"G02": .2, "G03": .3, "G04": .3, "G05": .25, "G06": .3, "G07": .3, "G08": .2, "G09": .45, "G10": .25, "G11": .45,
              "G12": .45, "G13": .7, "G14": .4, "G15": .7, "G16": .6, "G17": .5, "G18": .8, "G19": .5, "G20": .45, "G21": .3})
R.TL, R.TOTAL = R.timeline()
R.TL = {k: (a - .1, b - .1) for k, (a, b) in R.TL.items()}      # la voz arranca en el fotograma 0
R.TOTAL = R.TL["G21"][1] + .1                                    # corte en seco ~0,1 s tras la última palabra
TL, TOTAL = R.TL, R.TOTAL
S, E, WT = R.S, R.E, R.WT
LINEAS = R.LINEAS
def talk(lid, T): return S(lid) <= T < E(lid)
def u_(T, t0, d): return clamp((T - t0) / d)
def pop(T, t0, d=.3): return back((T - t0) / d) if T >= t0 else 0

def chunks():
    out = []
    for lid, who, tts, cap in LINEAS:
        words = cap.split(); times = R.word_times(lid, words); groups, cur = [], []
        for i, w in enumerate(words):
            cur.append(i)
            if sum(len(words[x].strip("*")) + 1 for x in cur) >= 11 or w.rstrip("*").endswith((".", ",", ":", "?", "!", "…")):
                groups.append(cur); cur = []
        if cur: groups.append(cur)
        for g in groups:
            out.append((times[g[0]][0], times[g[-1]][1], [(words[i].replace("*", "").rstrip(":").upper(), times[i], "*" in words[i]) for i in g], who, lid))
    return out
CH = chunks()

# ---------------------------------------------------------------- texturas y utilidades
_RNG = np.random.default_rng(7)
_NOISE = Image.fromarray((_RNG.random((H, W)) * 90 + 165).astype(np.uint8))

@lru_cache(1)
def pizarra_img():
    a = np.zeros((H, W, 3), np.float32); a[:] = PIZ
    yy, xx = np.mgrid[0:H, 0:W]
    a *= (1 - .22 * (((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2))[..., None] * 1.06
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    sm = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(sm); r = random.Random(4)
    for _ in range(26):   # manchas de borrador
        x, y = r.uniform(0, W), r.uniform(0, H); w, h = r.uniform(200, 520), r.uniform(40, 110)
        d.ellipse((x - w, y - h, x + w, y + h), fill=(255, 255, 255, r.randint(5, 13)))
    im.alpha_composite(sm.filter(ImageFilter.GaussianBlur(40)))
    return im
def pizarra(): return pizarra_img().copy()

def tiza(c, s, cx, cy, size, col=TIZA, rot=0, f=None, alpha=255, anchor="mm", stroke=0, borde=False):
    """Texto de tiza: letra a mano con grano."""
    f = font(f or F_HAND, size)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((cx, cy), s, font=f, fill=col + (255,), anchor=anchor, stroke_width=stroke, stroke_fill=col + (255,))
    m = lay.getchannel("A"); m = Image.composite(_NOISE, Image.new("L", (W, H), 0), m).point(lambda v: min(255, int(v * 1.25 * alpha / 255)))
    lay.putalpha(m)
    if borde:
        b = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(b).text((cx, cy), s, font=f, fill=OL + (255,), anchor=anchor, stroke_width=stroke + 9, stroke_fill=OL + (255,))
        b.alpha_composite(lay); lay = b
    if rot: lay = lay.rotate(rot, center=(cx, cy), resample=Image.BICUBIC)
    c.alpha_composite(lay)

def rotulo(c, s, cx, cy, size, fill=CREMA, fg=OL, rot=0, f=None, pad=22, k=1.0):
    """Etiqueta de cartulina pegada con cinta."""
    if k <= 0: return
    f_ = font(f or F_BAL, size * k); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    tw = d.textlength(s, font=f_); h = size * k * 1.25
    d.rounded_rectangle((cx - tw / 2 - pad, cy - h / 2, cx + tw / 2 + pad, cy + h / 2), 14, fill=fill + (255,), outline=OL + (255,), width=5)
    d.text((cx, cy), s, font=f_, fill=fg + (255,), anchor="mm")
    if rot: lay = lay.rotate(rot, center=(cx, cy), resample=Image.BICUBIC)
    c.alpha_composite(lay)

def lapiz_rojo(c, box, u, w=11, seed=1):
    """Círculo de lápiz rojo de maestra, dibujado a mano."""
    if u <= 0: return
    x0, y0, x1, y1 = box; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
    r = random.Random(seed); ph = r.uniform(0, 6); pts = []
    n = int(70 * clamp(u)) + 2
    for k in range(n):
        a = math.radians(-110 + 410 * k / 70); j = 1 + .035 * math.sin(k * .5 + ph) + .0009 * k
        pts.append((cx + rx * j * math.cos(a), cy + ry * j * math.sin(a)))
    d = ImageDraw.Draw(c); d.line(pts, fill=ROJO, width=w, joint="curve")
    for p in (pts[0], pts[-1]): d.ellipse((p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2), fill=ROJO)

def paste_rot(c, im, cx, cy, s=1.0, rot=0, alpha=1.0):
    if s != 1.0: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    c.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def sombra(c, box, rad=24, a=90, dy=14):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = box; d.rounded_rectangle((x0, y0 + dy, x1, y1 + dy), rad, fill=(0, 0, 0, a))
    c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(14)))

def view(im, cx, cy, z):
    w, h = W / z, H / z
    x0 = clamp((cx - w / 2) / max(1, W - w)) * (W - w); y0 = clamp((cy - h / 2) / max(1, H - h)) * (H - h)
    return im.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + w, y0 + h)).convert("RGBA")

def oscurecer(c, col=(10, 14, 40), a=90): c.alpha_composite(Image.new("RGBA", (W, H), col + (int(a),)))

# ---------------------------------------------------------------- personajes
def mateo(c, kind, hx, hy, s, T, lid=None, blink=True):
    """Mateo con la cabeza centrada en (hx, hy). Plano cerrado: cara y pecho."""
    hab = lid is not None and talk(lid, T)
    put(c, f"mateo_{kind}_hab" if hab else f"mateo_{kind}", hx, hy + 498 * s, s)
    if hab: mouth(c, hx, hy + 150 * s, T, True, int(26 * s))
    if blink and kind in ("neutral", "timido", "triste", "susto") and (T % 3.7) < .11: parpadeo(c, hx, hy, s)

def cabeza(c, kind, hx, hy, s, T, lid=None):
    hab = lid is not None and talk(lid, T)
    put(c, f"cab_{kind}_hab" if hab else f"cab_{kind}", hx, hy + 138 * s, s)
    if hab: mouth(c, hx, hy + 150 * s, T, True, int(22 * s))
    if (T % 4.3) < .11: parpadeo(c, hx, hy, s)

def parpadeo(c, hx, hy, s):
    d = ImageDraw.Draw(c)
    for ex in (-75.5, 75.5):
        x, y = hx + ex * s, hy - 22 * s
        d.ellipse((x - 46 * s, y - 44 * s, x + 46 * s, y + 44 * s), fill=(243, 194, 155))
        d.line((x - 34 * s, y + 6 * s, x + 34 * s, y + 6 * s), fill=OL, width=max(3, int(7 * s)))

def maestra(c, hx, hy, s, T, lid=None):
    hab = lid is not None and talk(lid, T)
    put(c, "maestra_hab" if hab else "maestra", hx, hy + 400 * s, s)
    if hab: mouth(c, hx, hy + 112 * s, T, True, int(20 * s))

# ---------------------------------------------------------------- objetos
@lru_cache(1)
def nota_img():
    w, h = 880, 1120; im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 18, fill=CREMA + (255,), outline=OL + (255,), width=7)
    d.rectangle((4, 4, w - 5, 150), fill=AZUL + (255,)); d.line((0, 150, w, 150), fill=OL, width=6)
    d.text((w / 2, 78), "PREESCOLAR · AVISO", font=font(F_BAL, 62), fill=CREMA, anchor="mm")
    f = font(F_AND, 54)
    d.text((70, 250), "Para la familia de Mateo:", font=f, fill=OL, anchor="lm")
    d.text((70, 370), "Mateo aún no escribe", font=f, fill=OL, anchor="lm")
    d.text((70, 450), "su nombre.", font=f, fill=OL, anchor="lm")
    d.text((70, 570), "Tiene 30 días. Si no…", font=f, fill=OL, anchor="lm")
    d.text((w / 2, 770), "REPITE", font=font(F_ANTON, 250), fill=ROJO, anchor="mm")
    d.text((70, 980), "Maestra Marta", font=font(F_HAND, 78), fill=AZUL, anchor="lm")
    d.line((60, 1030, 470, 1030), fill=(150, 150, 165), width=4)
    return im
NOTA_REPITE = (-330, 80, 330, 340)     # caja de "REPITE" respecto al centro de la nota (escala 1)

@lru_cache(4)
def sobre_img(texto="MATEO"):
    w, h = 820, 540; im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 20, fill=(250, 238, 208, 255), outline=OL + (255,), width=8)
    d.line((6, 8, w / 2, h * .52, w - 6, 8), fill=(206, 186, 140), width=7)
    d.line((6, h - 8, w * .36, h * .42), fill=(222, 204, 160), width=5); d.line((w - 6, h - 8, w * .64, h * .42), fill=(222, 204, 160), width=5)
    d.ellipse((w / 2 - 56, h * .52 - 56, w / 2 + 56, h * .52 + 56), fill=ROJO + (255,), outline=OL + (255,), width=7)   # sello de lacre
    d.text((w / 2, h * .52), "★", font=font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60), fill=CREMA, anchor="mm")
    d.rounded_rectangle((w / 2 - 250, h - 190, w / 2 + 250, h - 56), 14, fill=CREMA + (255,), outline=OL + (255,), width=5)
    d.text((w / 2, h - 126), texto, font=font(F_AND, 104), fill=AZUL, anchor="mm")
    return im

@lru_cache(1)
def hoja_img():
    return R.layer("hoja").resize((940, 680), Image.LANCZOS)

def raya_pts(x0, x1, y, amp=16, seed=3, n=60):
    r = random.Random(seed); ph = r.uniform(0, 6)
    return [(x0 + (x1 - x0) * k / n, y + amp * math.sin(k * .42 + ph) + amp * .5 * math.sin(k * 1.13) + (k / n) * 26) for k in range(n + 1)]

def crayon(c, pts, w=20, col=(63, 174, 74)):
    if len(pts) < 2: return
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m); d.line(pts, fill=255, width=int(w), joint="curve")
    for p in (pts[0], pts[-1]): d.ellipse((p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2), fill=255)
    m = Image.composite(_NOISE, Image.new("L", (W, H), 0), m)
    lay = Image.new("RGBA", (W, H), col + (0,)); lay.putalpha(m); c.alpha_composite(lay)

def mano(c, tip, T, s=.62):
    x, y = tip; jx = 1.6 * math.sin(T * 31); jy = 1.6 * math.cos(T * 27)
    put(c, "mano_crayola", x + 270 * s + jx, y + 78 * s + jy, s)

NOMBRES = ["ANA", "LUIS", "SOFÍA", "DIEGO", "EMMA", "JUAN", "LUCÍA", "BRUNO", "MÍA", "PABLO", "VALE", "IKER", "NORA", None,
           "HUGO", "ELSA", "DANI", "ABRIL", "GAEL", "ZOE", "RENATA", "SAMU"]
PASTEL = [(255, 226, 190), (206, 232, 255), (216, 245, 214), (255, 214, 224), (240, 226, 255), (255, 244, 190)]
TINTAS = [(214, 70, 60), (52, 110, 200), (50, 150, 80), (150, 80, 180), (224, 130, 30)]
def slot(i):
    r_, c_ = divmod(i, 4); n_row = 4 if r_ < 5 else 2
    x = 190 + c_ * 234 if n_row == 4 else 424 + c_ * 234
    return x, 560 + r_ * 178
HUECO = slot(13)

@lru_cache(1)
def pared_img():
    im = Image.new("RGBA", (W, H), (250, 236, 204, 255)); d = ImageDraw.Draw(im)
    for x in range(0, W, 120): d.line((x, 0, x, H), fill=(244, 228, 192), width=3)
    d.rectangle((0, 1700, W, H), fill=(214, 178, 132)); d.line((0, 1700, W, 1700), fill=OL, width=6)
    d.rounded_rectangle((150, 250, 930, 400), 26, fill=AZUL, outline=OL, width=7)
    d.text((W / 2, 322), "NUESTROS NOMBRES", font=font(F_BAL, 76), fill=CREMA, anchor="mm")
    d.rounded_rectangle((60, 440, 1020, 1620), 30, fill=(201, 152, 98), outline=(120, 80, 44), width=14)
    r = random.Random(11)
    for _ in range(900):
        x, y = r.uniform(76, 1004), r.uniform(456, 1604); d.ellipse((x, y, x + 4, y + 4), fill=(186, 138, 86))
    for i, nm in enumerate(NOMBRES):
        x, y = slot(i)
        if nm is None:
            for k in range(0, 204, 34):   # hueco: contorno punteado
                d.line((x - 102 + k, y - 70, x - 102 + k + 20, y - 70), fill=(110, 72, 40), width=6)
                d.line((x - 102 + k, y + 70, x - 102 + k + 20, y + 70), fill=(110, 72, 40), width=6)
            for k in range(0, 140, 34):
                d.line((x - 102, y - 70 + k, x - 102, y - 70 + k + 20), fill=(110, 72, 40), width=6)
                d.line((x + 102, y - 70 + k, x + 102, y - 70 + k + 20), fill=(110, 72, 40), width=6)
            continue
        card = Image.new("RGBA", (204, 140), (0, 0, 0, 0)); dc = ImageDraw.Draw(card)
        dc.rounded_rectangle((0, 0, 203, 139), 12, fill=PASTEL[i % 6] + (255,), outline=OL + (255,), width=5)
        sz = 62 if len(nm) <= 4 else (50 if len(nm) <= 5 else 40)
        dc.text((102, 78), nm, font=font(F_BAL, sz), fill=TINTAS[i % 5], anchor="mm")
        card = card.rotate(r.uniform(-4, 4), resample=Image.BICUBIC, expand=True)
        im.alpha_composite(card, (int(x - card.width / 2), int(y - card.height / 2)))
        d.ellipse((x - 12, y - 78, x + 12, y - 54), fill=ROJO, outline=OL, width=4)
    return im

@lru_cache(1)
def refri_img():
    im = Image.new("RGBA", (W, H), (236, 214, 178, 255)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((70, 120, 1010, 2100), 60, fill=(238, 242, 246), outline=OL, width=9)
    d.rounded_rectangle((110, 160, 970, 2100), 40, fill=(248, 250, 252))
    d.rounded_rectangle((120, 700, 160, 1180), 20, fill=(176, 184, 196), outline=OL, width=6)
    # hoja de Tomás: cinco letras perfectas
    a = Image.new("RGBA", (520, 400), (0, 0, 0, 0)); da = ImageDraw.Draw(a)
    da.rounded_rectangle((0, 0, 519, 399), 10, fill=CREMA + (255,), outline=OL + (255,), width=6)
    for k in range(3): da.line((30, 150 + k * 90, 490, 150 + k * 90), fill=(170, 200, 232), width=4)
    for k, ch in enumerate("TOMÁS"):
        da.text((72 + k * 94, 212), ch, font=font(F_BAL, 150), fill=TINTAS[k % 5], anchor="mm")
    da.text((440, 60), "★", font=font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 76), fill=(240, 180, 30), anchor="mm")
    da.text((40, 352), "¡Muy bien!", font=font(F_HAND, 54), fill=ROJO, anchor="lm")
    a = a.rotate(-4, resample=Image.BICUBIC, expand=True); im.alpha_composite(a, (250, 430))
    d.ellipse((480, 420, 540, 480), fill=AMA, outline=OL, width=5)
    # hoja de Mateo: una raya
    b = Image.new("RGBA", (W, H), (0, 0, 0, 0)); db = ImageDraw.Draw(b)
    db.rounded_rectangle((330, 1010, 850, 1410), 10, fill=CREMA + (255,), outline=OL + (255,), width=6)
    for k in range(3): db.line((360, 1160 + k * 90, 820, 1160 + k * 90), fill=(170, 200, 232), width=4)
    crayon(b, raya_pts(380, 800, 1230, 14, 3), 18)
    b = b.rotate(5, center=(590, 1210), resample=Image.BICUBIC); im.alpha_composite(b)
    d.ellipse((560, 990, 620, 1050), fill=(80, 170, 110), outline=OL, width=5)
    return im

# ---------------------------------------------------------------- barra fija: FALTAN X DÍAS + imanes M-A-T-E-O
T_HUD = WT("G03", "Hoy,") - .15
HS = 1.06
IMAN = [(226, 72, 59), (255, 180, 40), (72, 170, 96), (63, 127, 208), (160, 96, 200)]
def calendario(d, cx, cy, s, n=DIAS_FALTAN):
    w, h = 150 * s, 168 * s
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 20 * s, fill=CREMA, outline=OL, width=max(4, int(6 * s)))
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy - h / 2 + 50 * s), 20 * s, fill=ROJO, outline=OL, width=max(4, int(6 * s)))
    d.rectangle((cx - w / 2 + 4 * s, cy - h / 2 + 30 * s, cx + w / 2 - 4 * s, cy - h / 2 + 50 * s), fill=ROJO)
    d.text((cx, cy - h / 2 + 26 * s), "FALTAN", font=font(F_BAL, 32 * s), fill=CREMA, anchor="mm")
    d.text((cx, cy + 10 * s), str(n), font=font(F_ANTON, 86 * s), fill=OL, anchor="mm")
    d.text((cx, cy + 64 * s), "DÍAS", font=font(F_BAL, 30 * s), fill=OL, anchor="mm")

def imanes(d, x0, cy, s, T, on=LETRAS_ON, t0=None):
    for i, ch in enumerate("MATEO"):
        k = 1 if t0 is None else pop(T, t0 + i * .07, .28)
        if k <= 0: continue
        cx = x0 + i * 126 * s; r = 54 * s * k
        lit = ch in on
        d.rounded_rectangle((cx - r, cy - r, cx + r, cy + r), 18 * s, fill=IMAN[i] if lit else (58, 92, 80), outline=OL, width=max(4, int(6 * s)))
        d.text((cx, cy + 2 * s), ch, font=font(F_BAL, 78 * s * k), fill=CREMA if lit else (196, 208, 202), anchor="mm")

def draw_hud(c, T):
    if T < T_HUD: return
    d = ImageDraw.Draw(c); k = 1
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    dl.rounded_rectangle((34, 146, 886, 334), 34, fill=PIZ2 + (232,), outline=(214, 190, 150, 255), width=6)
    c.alpha_composite(lay)
    calendario(d, 134, 240, HS); imanes(d, 290, 240, HS, T)

# ---------------------------------------------------------------- subtítulos palabra a palabra (clave en amarillo tiza)
CAP_Y = 1372
def draw_caption(c, T):
    for idx, (t0, t1, g, who, lid) in enumerate(CH):
        nxt0 = CH[idx + 1][0] if idx + 1 < len(CH) else 1e9
        if not (t0 - .04 <= T < t1 + .3) or T >= nxt0 - .04: continue
        d = ImageDraw.Draw(c); size = 104
        f = font(F_ANTON, size); sp = d.textlength(" ", font=f)
        widths = [d.textlength(p, font=f) for p, _, _ in g]; total = sum(widths) + sp * (len(g) - 1)
        if total > 900:
            size = int(size * 900 / total); f = font(F_ANTON, size); sp = d.textlength(" ", font=f)
            widths = [d.textlength(p, font=f) for p, _, _ in g]; total = sum(widths) + sp * (len(g) - 1)
        x = W / 2 - total / 2
        for (p, (ws, we), star), wd in zip(g, widths):
            if T >= ws - .04:
                k = .8 + .2 * back((T - ws + .04) / .13)
                col = AMA if star else TIZA
                d.text((x + wd / 2, CAP_Y), p, font=font(F_ANTON, size * k), fill=col, anchor="mm", stroke_width=11, stroke_fill=(12, 16, 22))
            x += wd + sp
        return

# ================================================================ ESCENAS
def sc_nota(T):
    """0-3 s: UN objeto enorme (la nota) con el error en círculo rojo. Movimiento desde el fotograma 0."""
    c = pizarra(); u = ease(T / .45); z = 1.22 - .17 * u + .03 * (T / 4)
    cx, cy = W / 2, 860 + 40 * (1 - u); rot = -7 + 4 * u
    nb = nota_img(); sombra(c, (cx - 440 * z, cy - 560 * z, cx + 440 * z, cy + 560 * z), 24, 110, 22)
    paste_rot(c, nb, cx, cy, z, rot)
    t1 = WT("G01", "repite") - .25
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x0, y0, x1, y1 = NOTA_REPITE
    caja = (cx + x0 * z, cy + y0 * z, cx + x1 * z, cy + y1 * z)
    lapiz_rojo(lay, caja, .3 + .7 * u_(T, 0, .38), 15)                      # ya asoma en el fotograma 0
    lapiz_rojo(lay, (caja[0] - 14, caja[1] - 10, caja[2] + 14, caja[3] + 10), u_(T, t1, .3), 13, 6)   # segunda vuelta al decir "repite"
    c.alpha_composite(lay.rotate(rot, center=(cx, cy), resample=Image.BICUBIC))
    return c

def sc_pregunta(T):
    t0 = S("G02") - .1; c = pizarra(); z = 1.5 + .16 * u_(T, t0, 3.2)
    mateo(c, "susto", W / 2, 820, z, T)
    k = pop(T, WT("G02", "pregunta.") - .1, .3)
    if k > 0:
        tiza(c, "?", 860, 430, 330 * k, AMA, -12, stroke=3)
    return c

def sc_barra(T):
    """Se enciende la barra de la temporada: calendario FALTAN 30 DÍAS + imanes apagados."""
    t0 = S("G03") - .1; c = pizarra(); d = ImageDraw.Draw(c)
    k = pop(T, t0 + .05, .3); m = ease((T - (T_HUD - .42)) / .4)      # m: viaja a su sitio en la barra
    cs = (2.3 * (1 - m) + HS * m) * k
    calendario(d, 540 * (1 - m) + 134 * m, 700 * (1 - m) + 240 * m, cs)
    ims = 1.5 * (1 - m) + HS * m
    imanes(d, (162 * (1 - m)) + 290 * m, 1120 * (1 - m) + 240 * m, ims, T, t0=t0 + .3)
    return c

def sc_salida(T):
    t0 = WT("G03", "Hoy,") - .1; c = bg("bg_escuela", T, t0, 1.0, 1.1, 3, .5, .55)
    maestra(c, 760 - 40 * u_(T, t0, 2.5), 720, 1.1, T)
    tn = WT("G03", "nota.") - .5; u = ease((T - tn) / .5)
    if u > 0:
        nb = nota_img(); paste_rot(c, nb, 520 - 200 * u, 1100 - 60 * u, .2 + .26 * u, 12 - 18 * u)
    return c

def sc_maestra(T):
    t0 = S("G04") - .15; c = bg("bg_escuela", T, t0, 1.5, 1.62, 4, .5, .4)
    maestra(c, W / 2, 700, 1.75 + .08 * u_(T, t0, 3), T, "G04")
    return c

def sc_menos(T):
    """"…menos Mateo": plano cerrado de Mateo y círculo rojo sobre su etiqueta vacía."""
    t0 = WT("G04", "Todos…", 2) - .15; c = pizarra(); z = 1.55 + .1 * u_(T, t0, 2)
    mateo(c, "timido", W / 2, 640, z, T)
    ty = 640 + (955 - 452) * z
    lapiz_rojo(c, (W / 2 - 250 * z * .78, ty - 120 * z * .78, W / 2 + 250 * z * .78, ty + 120 * z * .78), u_(T, WT("G04", "Mateo.") - .1, .4), 13, 5)
    return c

def sc_pared(T):
    t0 = S("G05") - .15; th = WT("G05", "hueco.") - .2
    m = ease((T - th) / .45)
    z = 1.05 + .25 * u_(T, t0, 2) * (1 - m) + m * 1.5
    cx = 400 + 300 * u_(T, t0, 1.8); cy = 760 + 200 * u_(T, t0, 1.8)
    cx = cx * (1 - m) + HUECO[0] * m; cy = cy * (1 - m) + HUECO[1] * m
    im = pared_img().copy()
    if m > 0:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        a = int((120 + 80 * math.sin(T * 9)) * m)
        d.rounded_rectangle((HUECO[0] - 110, HUECO[1] - 78, HUECO[0] + 110, HUECO[1] + 78), 14, fill=AMA + (a,))
        im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10)))
        ImageDraw.Draw(im).text((HUECO[0], HUECO[1]), "?", font=font(F_BAL, 110), fill=(110, 72, 40), anchor="mm")
    c = view(im, cx, cy, z)
    k = pop(T, WT("G05", "21") - .05, .25)
    if k > 0 and m < .3: rotulo(c, "21", 870, 520, 130, AMA, OL, 8, k=k)
    return c

def sc_plazo(T):
    t0 = S("G06") - .15; c = bg("bg_escuela", T, t0, 1.45, 1.55, 4, .5, .4)
    maestra(c, 380, 760, 1.5, T, "G06")
    d = ImageDraw.Draw(c); k = pop(T, WT("G06", "30") - .08, .28)
    if k > 0: calendario(d, 820, 560, 1.9 * k)
    tr = WT("G06", "repite.") - .08; kr = pop(T, tr, .2)
    if kr > 0:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay); f = font(F_ANTON, 210 * (1.5 - .5 * min(1, kr)))
        tw = dl.textlength("REPITE", font=f)
        dl.rounded_rectangle((540 - tw / 2 - 40, 1060 - 140, 540 + tw / 2 + 40, 1060 + 140), 26, outline=ROJO + (255,), width=16)
        dl.text((540, 1060), "REPITE", font=f, fill=ROJO + (255,), anchor="mm")
        c.alpha_composite(lay.rotate(-9, center=(540, 1060), resample=Image.BICUBIC))
    return c

def sc_sobre(T):
    t0 = S("G07") - .15; c = bg("bg_escuela", T, t0, 1.8, 1.9, 5, .5, .7); oscurecer(c, (20, 40, 34), 150)
    u = ease((T - t0) / .4); wob = 3 * math.sin((T - t0) * 2.2)
    if T >= S("G08") - .1: maestra(c, 250, 560, .95, T, "G08")
    cy = 1020 + 300 * (1 - u); z = 1.0 + .08 * u_(T, t0, 5)
    sombra(c, (540 - 410 * z, cy - 270 * z, 540 + 410 * z, cy + 270 * z), 24, 120, 20)
    paste_rot(c, sobre_img(), 540, cy, z, -5 + wob)
    for sx in (-1, 1):   # manos de la maestra que lo sostienen
        ImageDraw.Draw(c).ellipse((540 + sx * 420 * z - 62, cy + 150 - 56, 540 + sx * 420 * z + 62, cy + 150 + 56), fill=(243, 194, 155), outline=OL, width=6)
    k = pop(T, WT("G07", "cerrado.") - .1, .25)
    if k > 0 and T < S("G08"): rotulo(c, "CERRADO", 760, 700, 78, ROJO, CREMA, 9, k=k)
    ua = u_(T, WT("G08", "afuera.") - .25, .4)
    if ua > 0:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        lapiz_rojo(lay, (540 - 290 * z, cy + 70 * z, 540 + 290 * z, cy + 228 * z), ua, 12, 9)
        c.alpha_composite(lay.rotate(-5 + wob, center=(540, cy), resample=Image.BICUBIC))
    return c

def sc_cocina(T):
    """Mateo sostiene el sobre AL REVÉS: no sabe leer lo que pone."""
    t0 = S("G09") - .2; c = bg("bg_cocina", T, t0, 1.25, 1.35, 3, .5, .45)
    z = 1.35 + .06 * u_(T, t0, 2.5)
    mateo(c, "neutral", W / 2, 600, z, T, "G09")
    cy = 1190; wob = 4 * math.sin((T - t0) * 3)
    paste_rot(c, sobre_img(), 540, cy, .8, 180 + 6 + wob)
    d = ImageDraw.Draw(c)
    for sx in (-1, 1): d.ellipse((540 + sx * 330 - 60, cy + 30 - 56, 540 + sx * 330 + 60, cy + 30 + 56), fill=(243, 194, 155), outline=OL, width=6)
    return c

def sc_letras(T):
    """Cada letra del sobre con un ? encima: dice su nombre y no lo sabe leer."""
    t0 = S("G10") - .15; c = pizarra()
    r = ease((T - t0) / .5); rot = 180 * (1 - r)
    z = 1.2 + .06 * u_(T, t0, 3); cy = 900
    sombra(c, (540 - 492, cy - 324, 540 + 492, cy + 324), 24, 120, 20)
    paste_rot(c, sobre_img(), 540, cy, z, rot)
    tq = WT("G10", "Y") - .1
    for i in range(5):
        k = pop(T, tq + i * .09, .22)
        if k > 0: tiza(c, "?", 540 + (i - 2) * 170, cy - 430 + 16 * math.sin(T * 6 + i), 200 * k, AMA, (i - 2) * 7, stroke=3)
    return c

def _mesa(T, t0, zoom=1.0):
    return bg("bg_mesa", T, t0, 1.15 * zoom, 1.2 * zoom, 4, .45, .5)

HOJA_C = (540, 900)
def sc_hoja(T):
    t0 = S("G11") - .2; c = _mesa(T, t0)
    u = ease((T - t0) / .4)
    paste_rot(c, hoja_img(), HOJA_C[0], HOJA_C[1] - 900 * (1 - u), 1.0, 5 * (1 - u))
    uc = ease((T - (WT("G11", "escribe") - .2)) / .45)
    if uc > 0: put(c, "crayola", 540 + 600 * (1 - uc), 1420, .5, rot=70 + 220 * (1 - uc))
    return c

def sc_concentra(T):
    t0 = S("G12") - .2; c = bg("bg_cocina", T, t0, 1.5, 1.6, 3, .5, .4)
    tl = WT("G12", "Saca") - .1
    z = 1.5 + .05 * u_(T, t0, 2) + .22 * ease((T - tl) / .25)
    mateo(c, "neutral" if T < tl else "concentra", W / 2, 760, z, T)
    if T < tl:
        put(c, "crayola", 720, 1250, .42, rot=30 + 3 * math.sin(T * 40))
        ImageDraw.Draw(c).ellipse((640, 1250, 780, 1380), fill=(243, 194, 155), outline=OL, width=6)
        k = pop(T, WT("G12", "crayola.") - .15, .2)
        if k > 0: tiza(c, "¡ÑIC!", 850, 1050, 104 * k, AMA, 14, stroke=2, borde=True)
    return c

T_RAYA0 = WT("G12", "escribe…") - .1; T_RAYA1 = WT("G12", "raya.") + .35
RAYA = raya_pts(210, 850, 892, 16, 3)
def sc_raya(T):
    """La mano agarra la crayola y traza de verdad: sale una raya."""
    t0 = WT("G12", "Y") - .15; c = _mesa(T, t0, 1.05)
    paste_rot(c, hoja_img(), HOJA_C[0], HOJA_C[1], 1.0, 0)
    u = u_(T, T_RAYA0, T_RAYA1 - T_RAYA0); ue = u * u * (3 - 2 * u)
    n = max(1, int(len(RAYA) * ue)); pts = RAYA[:n + 1]
    crayon(c, pts, 20)
    tip = pts[-1] if T >= T_RAYA0 else (RAYA[0][0] - 30, RAYA[0][1] - 60 * (1 - u_(T, t0, T_RAYA0 - t0)))
    if T > T_RAYA1: tip = (RAYA[-1][0] + 60 * u_(T, T_RAYA1, .3), RAYA[-1][1] - 120 * u_(T, T_RAYA1, .3))
    mano(c, tip, T if T_RAYA0 <= T <= T_RAYA1 else 0)
    return c

def sc_listo(T):
    t0 = S("G13") - .2; c = bg("bg_cocina", T, t0, 1.3, 1.36, 3, .5, .45)
    jump = 26 * abs(math.sin((T - t0) * 7)) * (1 - u_(T, t0, 1.2))
    mateo(c, "feliz", W / 2, 600 - jump, 1.35, T, "G13")
    cy = 1200 - jump; lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    paste_rot(lay, hoja_img(), 540, cy, .7, 0)
    crayon(lay, raya_pts(310, 770, cy - 6, 11, 3), 15)
    c.alpha_composite(lay.rotate(-5, center=(540, cy), resample=Image.BICUBIC))
    d = ImageDraw.Draw(c)
    for sx in (-1, 1): d.ellipse((540 + sx * 370 - 58, cy - 54, 540 + sx * 370 + 58, cy + 54), fill=(243, 194, 155), outline=OL, width=6)
    k = pop(T, t0 + .2, .22)
    if k > 0: tiza(c, "¡LISTO!", 810, 420, 112 * k, AMA, 10, stroke=2, borde=True)
    return c

def sc_refri(T):
    t0 = S("G14") - .2; tp = WT("G14", "primo.") - .35; tm = E("G14") - .15
    m = ease((T - t0) / .7)
    cx, cy, z = 520, 760 * m + 1100 * (1 - m), 1.25 + .5 * m          # baja de la raya de Mateo… a la hoja de Tomás
    c = view(refri_img(), cx, cy, z + .05 * u_(T, tp, 3))
    k = pop(T, tp + .25, .25)
    if k > 0: rotulo(c, "SU PRIMO", 760, 500, 64, AZUL, CREMA, 6, k=k)
    for i in range(5):
        kk = pop(T, WT("G14", "5") - .05 + i * .1, .2)
        if kk > 0: tiza(c, "✓", 215 + i * 150, 1120, 110 * kk, (72, 190, 110), 0, f="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", stroke=2)
    return c

def sc_mientras(T):
    t0 = S("G15") - .45; c = pizarra()
    k = pop(T, t0 + .05, .25)
    tiza(c, "MIENTRAS", 540, 780, 190 * k, AMA, -4, f=F_BAL)
    tiza(c, "TANTO…", 540, 990, 190 * pop(T, t0 + .22, .25), TIZA, -4, f=F_BAL) if T >= t0 + .22 else None
    return c

def sc_aula(T):
    """La maestra guarda un lugar: clava una chincheta en el hueco."""
    t0 = WT("G15", "en") - .05; tg = WT("G15", "guarda") - .05
    im = pared_img().copy(); d = ImageDraw.Draw(im)
    u = ease((T - tg) / .3)
    if u > 0:
        y = HUECO[1] - 66 - 260 * (1 - u)
        d.ellipse((HUECO[0] - 15, y - 15, HUECO[0] + 15, y + 15), fill=AMA, outline=OL, width=4)
    c = view(im, HUECO[0], HUECO[1] + 40, 1.9 + .25 * u_(T, t0, 4))
    oscurecer(c, (30, 40, 90), 60)
    k = pop(T, tg + .28, .2)
    if k > 0: tiza(c, "¡CLAC!", 800, 560, 110 * k, AMA, 12, stroke=2, borde=True)
    kl = pop(T, WT("G15", "lugar") - .05, .25)
    if kl > 0: rotulo(c, "RESERVADO", 540, 1150, 70, AMA, OL, -4, k=kl)
    return c

def sc_nosabe(T):
    t0 = WT("G15", "Pero") - .15; c = bg("bg_cuarto", T, t0, 1.3, 1.4, 3, .5, .5)
    mateo(c, "travieso", W / 2 + 14 * math.sin((T - t0) * 5), 700, 1.4, T)
    put(c, "crayola", 800, 1260 + 12 * math.sin((T - t0) * 8), .4, rot=20)
    ImageDraw.Draw(c).ellipse((730, 1260, 860, 1380), fill=(243, 194, 155), outline=OL, width=6)
    return c

def _cama(c, T, hx, hy, s, kind, lid=None):
    d = ImageDraw.Draw(c)
    d.ellipse((hx - 330 * s, hy - 210 * s, hx + 330 * s, hy + 250 * s), fill=(214, 220, 240), outline=OL, width=6)   # almohada
    cabeza(c, kind, hx, hy, s, T, lid)
    y0 = hy + 230 * s
    d.polygon([(0, y0 + 40), (W * .3, y0 - 6), (W * .7, y0 - 10), (W, y0 + 30), (W, H), (0, H)], fill=(52, 70, 150), outline=OL)
    d.line([(0, y0 + 40), (W * .3, y0 - 6), (W * .7, y0 - 10), (W, y0 + 30)], fill=(214, 220, 240), width=26)
    for sx in (-1, 1):   # manos agarradas a la manta
        d.ellipse((hx + sx * 150 * s - 44 * s, y0 - 30 * s, hx + sx * 150 * s + 44 * s, y0 + 40 * s), fill=(243, 194, 155), outline=OL, width=5)

def sc_noche(T):
    t0 = S("G16") - .4; c = bg("bg_noche", T, t0, 1.6, 1.6, 1, .9, .1)
    td = WT("G16", "Escuchó") - .15; ud = ease((T - td) / .5)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if ud > 0:   # rendija de luz de la puerta
        d.polygon([(0, 330), (70 + 80 * ud, 360), (70 + 80 * ud, 1500), (0, 1700)], fill=(255, 220, 140, int(200 * ud)))
        d.polygon([(70 + 80 * ud, 1500), (760, 1920), (0, 1920), (0, 1700)], fill=(255, 220, 140, int(70 * ud)))
        c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(8)))
    z = 1.05 + .12 * u_(T, t0, 4)
    _cama(c, T, 560, 900, z, "susto")
    oscurecer(c, (20, 30, 90), 46)
    for i in range(2):
        k = pop(T, t0 + .4 + i * .25, .3)
        if k > 0 and T < td: tiza(c, "z", 860 + i * 60, 520 - i * 90, (80 + i * 30) * k, (150, 170, 220), 10)
    if T >= WT("G16", "duerme.") - .2 and T < td:
        d2 = ImageDraw.Draw(c); d2.line((820, 430, 990, 560), fill=ROJO, width=14); d2.line((990, 430, 820, 560), fill=ROJO, width=14)
    return c

def sc_susurro(T):
    t0 = S("G17") - .2; c = bg("bg_noche", T, t0, 1.9, 1.9, 1, .9, .1)
    z = 1.5 + .12 * u_(T, t0, 3)
    _cama(c, T, 540, 800, z, "susto", "G17")
    oscurecer(c, (20, 30, 90), 40)
    return c

def sc_silencio(T):
    t0 = S("G18") - .2; c = bg("bg_noche", T, t0, 2.0, 2.0, 1, .9, .1)
    z = 1.7 + .2 * u_(T, t0, 3.5)
    _cama(c, T, 540, 820, z, "timido")
    oscurecer(c, (20, 30, 90), 42)
    for i in range(3):
        k = pop(T, WT("G18", "sin") - .1 + i * .18, .2)
        if k > 0: ImageDraw.Draw(c).ellipse((440 + i * 100 - 22 * k, 330 - 22 * k, 440 + i * 100 + 22 * k, 330 + 22 * k), fill=TIZA)
    return c

def sc_sobre2(T):
    t0 = S("G19") - .3; c = _mesa(T, t0); oscurecer(c, (10, 16, 60), 150)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).ellipse((140, 520, 940, 1400), fill=(190, 210, 255, 70))
    c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(70)))
    z = .95 + .1 * u_(T, t0, 4)
    sombra(c, (540 - 410 * z, 960 - 270 * z, 540 + 410 * z, 960 + 270 * z), 24, 140, 18)
    paste_rot(c, sobre_img(), 540, 960, z, -6)
    k = pop(T, WT("G19", "cerrado.") - .1, .22)
    if k > 0: rotulo(c, "SIGUE CERRADO", 540, 520, 80, ROJO, CREMA, -5, k=k)
    return c

def _tarjeta(lay, cx, cy, k, palabra, col, icono, rot):
    if k <= 0: return
    w, h = 400 * k, 560 * k; t = Image.new("RGBA", (int(w) + 8, int(h) + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
    d.rounded_rectangle((0, 0, w, h), 34 * k, fill=CREMA + (255,), outline=OL + (255,), width=max(4, int(9 * k)))
    d.rounded_rectangle((22 * k, 22 * k, w - 22 * k, h * .6), 22 * k, fill=col + (255,))
    ix, iy = w / 2, h * .32
    if icono == "verdad":   # bocadillo con exclamación: decirlo
        d.rounded_rectangle((ix - 120 * k, iy - 92 * k, ix + 120 * k, iy + 60 * k), 36 * k, fill=CREMA, outline=OL, width=max(3, int(7 * k)))
        d.polygon([(ix - 50 * k, iy + 56 * k), (ix - 84 * k, iy + 118 * k), (ix + 4 * k, iy + 58 * k)], fill=CREMA, outline=OL)
        d.line((ix - 46 * k, iy + 56 * k, ix, iy + 56 * k), fill=CREMA, width=max(3, int(9 * k)))
        d.text((ix, iy - 18 * k), "!", font=font(F_ANTON, 130 * k), fill=ROJO, anchor="mm")
    else:                   # candado: guardar el secreto
        d.arc((ix - 62 * k, iy - 122 * k, ix + 62 * k, iy + 10 * k), 180, 360, fill=OL, width=max(4, int(22 * k)))
        d.rounded_rectangle((ix - 96 * k, iy - 50 * k, ix + 96 * k, iy + 96 * k), 22 * k, fill=AMA, outline=OL, width=max(3, int(7 * k)))
        d.ellipse((ix - 20 * k, iy - 4 * k, ix + 20 * k, iy + 36 * k), fill=OL); d.rectangle((ix - 8 * k, iy + 20 * k, ix + 8 * k, iy + 62 * k), fill=OL)
    d.text((w / 2, h * .74), palabra, font=font(F_ANTON, 92 * k), fill=OL, anchor="mm")
    d.text((w / 2, h * .9), "¿MAÑANA?", font=font(F_BAL, 40 * k), fill=(120, 120, 135), anchor="mm")
    t = t.rotate(rot, resample=Image.BICUBIC, expand=True)
    lay.alpha_composite(t, (int(cx - t.width / 2), int(cy - t.height / 2)))

def sc_cartas(T):
    """Cierre: dos tarjetas de UNA palabra. La voz dice: Comenta VERDAD o SECRETO. Sígueme: día 2."""
    t0 = S("G20") - .25; c = pizarra()
    tv = WT("G20", "verdad,") - .15; ts = WT("G20", "secreto,") - .15
    kv, ks = pop(T, tv, .3), pop(T, ts, .3)
    tc = S("G21"); hv = 1 + .07 * math.sin((T - tc) * 9) * (1 if WT("G21", "VERDAD,") - .1 <= T < WT("G21", "o") else 0)
    hs = 1 + .07 * math.sin((T - tc) * 9) * (1 if WT("G21", "SECRETO.") - .1 <= T < WT("G21", "Sígueme:") else 0)
    _tarjeta(c, 280, 700, .94 * kv * hv, "VERDAD", (86, 176, 110), "verdad", 3)
    _tarjeta(c, 800, 700, .94 * ks * hs, "SECRETO", (150, 110, 200), "secreto", -3)
    if kv > 0 and ks > 0: tiza(c, "vs", 540, 690, 120 * min(1, ks), AMA, 0, f=F_BAL, borde=True)
    kc = pop(T, tc - .05, .25)
    if kc > 0: rotulo(c, "¡COMENTA!", 540, 1080, 96, AMA, OL, -3, k=kc)
    kg = pop(T, WT("G21", "Sígueme:") - .1, .25)
    if kg > 0: rotulo(c, "SÍGUEME · DÍA 2  ▶", 540, 1222, 72, ROJO, CREMA, 2, f="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", k=kg)
    return c

SCENES = [
    (0, sc_nota), (S("G02") - .1, sc_pregunta), (S("G03") - .1, sc_barra), (WT("G03", "Hoy,") - .1, sc_salida),
    (S("G04") - .15, sc_maestra), (WT("G04", "Todos…", 2) - .15, sc_menos), (S("G05") - .15, sc_pared), (S("G06") - .15, sc_plazo),
    (S("G07") - .15, sc_sobre), (S("G09") - .2, sc_cocina), (S("G10") - .15, sc_letras), (S("G11") - .2, sc_hoja),
    (S("G12") - .2, sc_concentra), (WT("G12", "Y") - .15, sc_raya), (S("G13") - .2, sc_listo), (S("G14") - .2, sc_refri),
    (S("G15") - .45, sc_mientras), (WT("G15", "en") - .05, sc_aula), (WT("G15", "Pero") - .15, sc_nosabe),
    (S("G16") - .4, sc_noche), (S("G17") - .2, sc_susurro), (S("G18") - .2, sc_silencio), (S("G19") - .3, sc_sobre2),
    (S("G20") - .25, sc_cartas),
]
SUAVES = {SCENES[20][0], SCENES[21][0]}          # cortes sin barrido (misma cama, plano más cerrado)
IMPACTS = [WT("G01", "repite") + .05, WT("G06", "repite.") - .05, WT("G15", "guarda") + .25]

def hblur(im, k):
    if k < 2: return im
    return im.resize((max(1, W // k), H), Image.BILINEAR).resize((W, H), Image.BILINEAR)

TW = .18
def frame(T):
    idx = max(i for i, (t, f) in enumerate(SCENES) if T >= t)
    t0, fn = SCENES[idx]; c = fn(T)
    u = (T - t0) / TW
    if idx > 0 and u < 1 and t0 not in SUAVES:      # barrido rápido entre escenas (nunca fundido a negro)
        e = ease(u); prev = SCENES[idx - 1][1](T); k = int(2 + 20 * math.sin(PI_ * u))
        canvas = Image.new("RGBA", (W, H), PIZ2 + (255,))
        canvas.alpha_composite(hblur(prev, k), (int(-W * e), 0)); canvas.alpha_composite(hblur(c, k), (int(W * (1 - e)), 0))
        c = canvas
    punch = sum(.028 * math.exp(-(T - ch[0]) * 9) for ch in CH if 0 <= T - ch[0] < .5)
    zz = 1 + punch
    amp = sum(15 * math.exp(-(T - ti) * 7) for ti in IMPACTS if 0 <= T - ti < .6)
    if zz > 1.002 or amp > .6:
        zz += .035 if amp > .6 else 0
        cc = c.resize((int(W * zz), int(H * zz)), Image.BILINEAR)
        ox = (cc.width - W) / 2 + amp * math.sin(T * 95); oy = (cc.height - H) / 2 + amp * math.cos(T * 71)
        c = cc.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    draw_hud(c, T); draw_caption(c, T)
    return c.convert("RGB")

def render_scene(i, out):
    t0 = SCENES[i][0]; t1 = SCENES[i + 1][0] if i + 1 < len(SCENES) else TOTAL
    f0, f1 = round(t0 * FPS), round(t1 * FPS); tmp = out + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in range(f0, f1): p.stdin.write(frame(f / FPS).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0: os.replace(tmp, out)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "still":
        for t in sys.argv[2:]: frame(float(t)).save(os.path.join(TMP, f"f_{float(t):06.2f}.jpg"), quality=86)
    elif cmd == "info":
        print(json.dumps({k: [round(a, 2), round(b, 2)] for k, (a, b) in TL.items()}), round(TOTAL, 2))
        print([round(t, 2) for t, f in SCENES])
    elif cmd == "scenes":
        from multiprocessing import Pool
        ids = [int(x) for x in sys.argv[2:]] or list(range(len(SCENES)))
        with Pool(2) as pool: pool.starmap(render_scene, [(i, os.path.join(TMP, f"s{i:02d}.mp4")) for i in ids])
