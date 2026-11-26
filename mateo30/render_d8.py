"""Temporada "Mateo: 30 días para no repetir" · DÍA 8 — Pone mamá (ganó SEGUIMOS; estructura del vídeo de 1M: el buzón de Rex).
Mundo visual nuevo (pizarra verde, tiza amarilla, rojo de corrección), barra FALTAN X DÍAS + imanes M-A-T-E-O,
subtítulos palabra a palabra y cierre con dos tarjetas de una palabra.
Uso: python3 render_d1.py still 1 5 | scenes [i...] | info"""
import os, sys, math, json, subprocess, random
from functools import lru_cache
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["GUION"] = "guion_d8"; os.environ["VOZDIR"] = os.path.join(HERE, "voz_d8")
sys.path.insert(0, HERE)
import importlib.util
_spec = importlib.util.spec_from_file_location("R", os.path.join(HERE, "..", "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

R.LAY = os.path.join(HERE, "layers"); R.layer.cache_clear(); R.scaled.cache_clear()
TMP = os.path.join(HERE, "tmp_d8"); os.makedirs(TMP, exist_ok=True)
W, H, FPS = R.W, R.H, R.FPS
put, ease, clamp, back, font, mouth, bg = R.put, R.ease, R.clamp, R.back, R.font, R.mouth, R.bg
F_ANTON = R.F_ANTON
MF = os.path.join(HERE, "..", "mateo-pov", "fonts")
F_HAND = os.path.join(MF, "Caveat.ttf"); F_BAL = os.path.join(MF, "Baloo2-ExtraBold.ttf"); F_AND = os.path.join(MF, "Andika-Bold.ttf")
PI_ = math.pi
OL = (29, 22, 48); PIZ = (36, 82, 66); PIZ2 = (25, 60, 48); TIZA = (246, 244, 232); AMA = (255, 212, 84)
ROJO = (226, 72, 59); CREMA = (255, 253, 244); AZUL = (63, 127, 208); MADERA = (176, 122, 72)
DIAS_FALTAN = 23; LETRAS_ON = "M"          # Día 1: ninguna letra dominada

# ---------------------------------------------------------------- tiempos
R.GAP.clear()
BASE = {"L02": .15, "L03": .5, "L04": .25, "L05": .35, "L06": .4, "L07": .45, "L08": .5, "L09": .45, "L10": .45, "L11": .5, "L12": .55,
        "L13": .3, "L14": .6, "L15": .5, "L16": .7, "L17": .35, "L18": .3}
FLEX = ("L03", "L06", "L08", "L10", "L12", "L14", "L16")
COLA = .35
R.GAP.update(BASE); _tl, _ = R.timeline(); _fin = _tl["L18"][1] - .1 + COLA
OBJ = float(math.ceil(_fin))                                                 # segundos enteros, sin relleno
_extra = (OBJ - COLA) - (_tl["L18"][1] - .1)
for _k in FLEX: R.GAP[_k] = BASE[_k] + _extra / len(FLEX)
R.TL, R.TOTAL = R.timeline()
R.TL = {k: (a - .1, b - .1) for k, (a, b) in R.TL.items()}      # la voz arranca en el fotograma 0
R.TOTAL = OBJ
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
# ================================================================ DÍA 2
R.scaled = lru_cache(12)(R.scaled.__wrapped__)   # los zooms animados no deben llenar la memoria de capas escaladas
def WI(lid, i):
    cap = [x for x in LINEAS if x[0] == lid][0][3].split(); return R.word_times(lid, cap)[i][0]
DJ = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; PB = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
VERDE = (63, 174, 74); AZULC = (52, 110, 200); PIEL = (243, 194, 155)

# ---------------------------------------------------------------- barra fija (píldora): días + letras M-A-T-E-O + "o repite el curso"
def _barra_img(n, on):
    K = 3; w, h = 650, 108; im = Image.new("RGBA", (w * K, h * K), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    k = lambda v: tuple(int(x * K) for x in v); F = lambda p, s: font(p, s * K)
    d.rounded_rectangle(k((0, 0, 650, 108)), 54 * K, fill=(22, 28, 46, 238), outline=(255, 255, 255, 70), width=2 * K)
    d.ellipse(k((8, 8, 100, 100)), fill=ROJO + (255,)); d.text(k((54, 46)), str(n), font=F(F_ANTON, 50), fill=CREMA, anchor="mm"); d.text(k((54, 80)), "DÍAS", font=F(PB, 13), fill=CREMA, anchor="mm")
    d.text(k((118, 25)), "PARA ESCRIBIR SU NOMBRE", font=F(PB, 17), fill=(255, 255, 255, 200), anchor="lm")
    for i, ch in enumerate("MATEO"):
        x = 118 + i * 56; ok = ch in on
        d.rounded_rectangle(k((x, 42, x + 48, 92)), 12 * K, fill=IMAN[i] + (255,) if ok else (44, 51, 72, 255), outline=None if ok else (120, 128, 152, 255), width=2 * K)
        d.text(k((x + 24, 68)), ch, font=F(F_BAL, 38), fill=(255, 255, 255, 255) if ok else (128, 136, 160, 255), anchor="mm")
    d.line(k((416, 26, 416, 82)), fill=(255, 255, 255, 60), width=2 * K)
    d.text(k((526, 42)), "o repite", font=F(F_HAND, 40), fill=(255, 209, 71), anchor="mm"); d.text(k((526, 74)), "el curso", font=F(F_HAND, 40), fill=(255, 209, 71), anchor="mm")
    w, h = int(w * 1.2), int(h * 1.2); im = im.resize((w, h), Image.LANCZOS); pad = 24; o = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    a = Image.new("L", o.size, 0); a.paste(im.split()[3].point(lambda v: v * 70 // 255), (pad, pad + 7)); a = a.filter(ImageFilter.GaussianBlur(9))
    o.paste((0, 0, 0, 255), (0, 0), a); o.alpha_composite(im, (pad, pad)); return o
IMAN = [(226, 72, 59), (245, 166, 35), (60, 160, 90), (63, 127, 208), (150, 90, 200)]
BARRA = _barra_img(DIAS_FALTAN, LETRAS_ON)
T_HUD = S("L02") - .1
def draw_hud(c, T):
    if T < T_HUD: return
    y = int(122 - 320 * (1 - ease((T - T_HUD) / .35)))
    if y >= 0: c.alpha_composite(BARRA, (10, y))
    elif -y < BARRA.height: c.alpha_composite(BARRA, (10, 0), (0, -y, BARRA.width, BARRA.height))

# ---------------------------------------------------------------- subtítulos palabra a palabra
T_FINAL = WI("L16", 3) - .2
def draw_caption(c, T):
    fin = T >= T_FINAL; cy, cx, maxw = (1110, 478, 800) if fin else (1372, 540, 900)
    for idx, (t0, t1, g, who, lid) in enumerate(CH):
        nxt0 = CH[idx + 1][0] if idx + 1 < len(CH) else 1e9
        if not (t0 - .04 <= T < t1 + .3) or T >= nxt0 - .04: continue
        d = ImageDraw.Draw(c); size = 104
        f = font(F_ANTON, size); sp = d.textlength(" ", font=f)
        widths = [d.textlength(p, font=f) for p, _, _ in g]; total = sum(widths) + sp * (len(g) - 1)
        if total > maxw:
            size = int(size * maxw / total); f = font(F_ANTON, size); sp = d.textlength(" ", font=f)
            widths = [d.textlength(p, font=f) for p, _, _ in g]; total = sum(widths) + sp * (len(g) - 1)
        x = cx - total / 2
        for (p, (ws, we), star), wd in zip(g, widths):
            if T >= ws - .04:
                k = .8 + .2 * back((T - ws + .04) / .13)
                d.text((x + wd / 2, cy), p, font=font(F_ANTON, size * k), fill=AMA if star else TIZA, anchor="mm", stroke_width=11, stroke_fill=(12, 16, 22))
            x += wd + sp
        return

# ---------------------------------------------------------------- utilidades del Día 2
def tomas(c, kind, hx, hy, s, T, lid=None):
    hab = lid is not None and talk(lid, T)
    put(c, "tomas_feliz_hab" if hab else f"tomas_{kind}", hx, hy + 498 * s, s)
    if hab: mouth(c, hx, hy + 150 * s, T, True, int(26 * s))

def manos(c, cx, cy, sep, r=56):
    d = ImageDraw.Draw(c)
    for sx in (-1, 1): d.ellipse((cx + sx * sep - r, cy - r, cx + sx * sep + r, cy + r), fill=PIEL, outline=OL, width=6)

LIB = os.path.join(HERE, "libro"); PM = (30, 30, 1212, 1010)
@lru_cache(4)
def _pag(name, box, w):
    im = Image.open(os.path.join(LIB, name)).convert("RGB").crop(box); return im.resize((w, int(w * im.height / im.width)), Image.LANCZOS)
def pagM(c, s, fx, fy, cx=540, cy=900):
    """Hoja real de la letra M (mitad de arriba) con el punto (fx, fy) de la página en (cx, cy). Devuelve la transformación página→pantalla."""
    w = int(round((PM[2] - PM[0]) * s / 2)) * 2; im = _pag("p022.png", PM, w); s = w / (PM[2] - PM[0])
    x0, y0 = cx - (fx - PM[0]) * s, cy - (fy - PM[1]) * s
    sombra(c, (x0, y0, x0 + im.width, y0 + im.height), 12, 110, 16); c.paste(im, (int(x0), int(y0)))
    return lambda p: (x0 + (p[0] - PM[0]) * s, y0 + (p[1] - PM[1]) * s), s

def _poli(pts, n=9, seed=1, j=2.2):
    r = random.Random(seed); out = []
    for (a, b) in zip(pts, pts[1:]):
        for k in range(n): out.append((a[0] + (b[0] - a[0]) * k / n + r.uniform(-j, j), a[1] + (b[1] - a[1]) * k / n + r.uniform(-j, j)))
    out.append(pts[-1]); return out
W_PTS = _poli([(204, 662), (220, 727), (237, 678), (254, 729), (272, 660)], 9, 4, 1.4)                      # sobre la 1.ª M punteada… al revés
M_STK = [_poli([(301, 722), (301, 666)], 9, 5, .8), _poli([(301, 666), (328, 704)], 9, 6, .8), _poli([(328, 704), (355, 666)], 9, 7, .8), _poli([(355, 666), (355, 722)], 9, 8, .8)]
M_PTS = [p for s_ in M_STK for p in s_]                                                                       # 2.ª M punteada, siguiendo los puntos
MP3_PTS = _poli([(392, 722), (392, 666), (418, 704), (445, 666), (445, 722)], 9, 11, 1.0)                     # 3.ª M punteada
ML_PTS = _poli([(494, 727), (497, 661), (528, 708), (559, 659), (563, 729)], 9, 12, 1.6)                      # ya sin puntos
M3_PTS = _poli([(606, 727), (609, 663), (632, 706), (655, 664), (678, 706), (701, 661), (705, 728)], 9, 9, 1.6)   # sin puntos… con tres montañas
def parcial(pts, u): return pts[:max(2, int(1 + (len(pts) - 1) * clamp(u)))] if u > 0 else []
def cray(c, tr, s, pts, col=VERDE, w=6.5):
    if len(pts) >= 2: crayon(c, [tr(p) for p in pts], max(6, w * s), col)

@lru_cache(None)
def hoja_mateo(n=2):
    """Recorte de su hoja (renglones de la M) con lo que lleva escrito."""
    box = (70, 540, 760, 770); im = Image.open(os.path.join(LIB, "p022.png")).convert("RGBA").crop(box); d = ImageDraw.Draw(im)
    for pts in ([W_PTS, M_PTS, MP3_PTS, ML_PTS, M3_PTS][:2 if n == 2 else 5]): d.line([(x - box[0], y - box[1]) for x, y in pts], fill=VERDE + (255,), width=7, joint="curve")
    d.rectangle((0, 0, im.width - 1, im.height - 1), outline=(214, 190, 150, 255), width=5); return im

@lru_cache(1)
def hoja_tomas():
    im = hoja_img().copy(); d = ImageDraw.Draw(im); d.text((470, 330), "TOMÁS", font=font(F_AND, 190), fill=AZULC + (255,), anchor="mm"); return im

def icono_tarjeta(d, ix, iy, k, icono):
    if icono == "secreto":
        d.arc((ix - 62 * k, iy - 122 * k, ix + 62 * k, iy + 10 * k), 180, 360, fill=OL, width=max(4, int(22 * k)))
        d.rounded_rectangle((ix - 96 * k, iy - 50 * k, ix + 96 * k, iy + 96 * k), 22 * k, fill=AMA, outline=OL, width=max(3, int(7 * k)))
        d.ellipse((ix - 20 * k, iy - 4 * k, ix + 20 * k, iy + 36 * k), fill=OL); d.rectangle((ix - 8 * k, iy + 20 * k, ix + 8 * k, iy + 62 * k), fill=OL)
    elif icono == "comparar":   # dos hojas, una junto a la otra, y un ojo que va de una a otra
        for sx, col, t in ((-1, VERDE, "M"), (1, AZULC, "T")):
            x = ix + sx * 74 * k; d.rounded_rectangle((x - 58 * k, iy - 84 * k, x + 58 * k, iy + 70 * k), 10 * k, fill=CREMA, outline=OL, width=max(3, int(6 * k)))
            d.text((x, iy - 12 * k), t, font=font(F_AND, 96 * k), fill=col, anchor="mm")
        d.polygon([(ix - 26 * k, iy + 100 * k), (ix, iy + 84 * k), (ix, iy + 116 * k)], fill=OL); d.polygon([(ix + 26 * k, iy + 100 * k), (ix, iy + 84 * k), (ix, iy + 116 * k)], fill=OL)
    elif icono == "premio":     # paleta de dulce
        d.line((ix, iy + 10 * k, ix, iy + 124 * k), fill=OL, width=max(4, int(22 * k))); d.line((ix, iy + 10 * k, ix, iy + 120 * k), fill=CREMA, width=max(2, int(10 * k)))
        d.ellipse((ix - 88 * k, iy - 110 * k, ix + 88 * k, iy + 66 * k), fill=ROJO, outline=OL, width=max(3, int(8 * k)))
        d.arc((ix - 56 * k, iy - 78 * k, ix + 56 * k, iy + 34 * k), 200, 80, fill=CREMA, width=max(3, int(16 * k))); d.arc((ix - 24 * k, iy - 46 * k, ix + 24 * k, iy + 2 * k), 20, 260, fill=CREMA, width=max(3, int(12 * k)))
    elif icono == "sinpremio":  # el mismo dulce, tachado
        icono_tarjeta(d, ix, iy, k * .86, "premio"); d.ellipse((ix - 118 * k, iy - 124 * k, ix + 118 * k, iy + 112 * k), outline=OL, width=max(4, int(18 * k)))
        d.line((ix - 80 * k, iy - 88 * k, ix + 80 * k, iy + 76 * k), fill=OL, width=max(4, int(18 * k)))
    else:                       # corazón: a su ritmo
        r = 58 * k
        d.ellipse((ix - 2 * r, iy - 1.5 * r, ix, iy + .5 * r), fill=ROJO, outline=OL, width=max(3, int(7 * k))); d.ellipse((ix, iy - 1.5 * r, ix + 2 * r, iy + .5 * r), fill=ROJO, outline=OL, width=max(3, int(7 * k)))
        d.polygon([(ix - 1.86 * r, iy - .1 * r), (ix + 1.86 * r, iy - .1 * r), (ix, iy + 1.9 * r)], fill=ROJO)
        d.line([(ix - 1.86 * r, iy - .05 * r), (ix, iy + 1.9 * r), (ix + 1.86 * r, iy - .05 * r)], fill=OL, width=max(3, int(7 * k)), joint="curve")
        d.ellipse((ix - 1.5 * r, iy - 1.1 * r, ix - .9 * r, iy - .5 * r), fill=(255, 170, 160))
def tarjeta(lay, cx, cy, k, palabra, col, icono, rot, sub="¿MAÑANA?"):
    if k <= 0: return
    w, h = 400 * k, 560 * k; t = Image.new("RGBA", (int(w) + 8, int(h) + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
    d.rounded_rectangle((0, 0, w, h), 34 * k, fill=CREMA + (255,), outline=OL + (255,), width=max(4, int(9 * k)))
    d.rounded_rectangle((22 * k, 22 * k, w - 22 * k, h * .6), 22 * k, fill=col + (255,))
    icono_tarjeta(d, w / 2, h * .32, k, icono)
    size = 92
    while d.textlength(palabra, font=font(F_ANTON, size * k)) > w - 44 * k: size -= 4
    d.text((w / 2, h * .74), palabra, font=font(F_ANTON, size * k), fill=OL, anchor="mm")
    d.text((w / 2, h * .9), sub, font=font(F_BAL, 40 * k), fill=(120, 120, 135), anchor="mm")
    t = t.rotate(rot, resample=Image.BICUBIC, expand=True); lay.alpha_composite(t, (int(cx - t.width / 2), int(cy - t.height / 2)))

def dos_lineas(c, cx, y, l1, l2, rot, k=1.0):
    if k <= 0: return
    lay = Image.new("RGBA", c.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); f = font(F_BAL, 40 * k)
    w = max(d.textlength(l1, font=f), d.textlength(l2, font=f)) + 44 * k
    d.rounded_rectangle((cx - w / 2, y - 58 * k, cx + w / 2, y + 58 * k), 18, fill=CREMA + (255,), outline=OL + (255,), width=5)
    d.text((cx, y - 24 * k), l1, font=f, fill=OL, anchor="mm"); d.text((cx, y + 24 * k), l2, font=f, fill=OL, anchor="mm")
    c.alpha_composite(lay.rotate(rot, center=(cx, y), resample=Image.BICUBIC))

def chispas(c, cx, cy, T, t0, n=7, R_=300, seed=2):
    r = random.Random(seed)
    for i in range(n):
        a = r.uniform(0, 6.28); rr = R_ * r.uniform(.55, 1); k = pop(T, t0 + i * .06, .25)
        if k > 0: tiza(c, "✦", cx + rr * math.cos(a), cy + rr * math.sin(a) * .7, (60 + 50 * r.random()) * k * (1 + .15 * math.sin(T * 9 + i)), AMA, 0, f=DJ, stroke=2)

def mano(c, tip, T, s=.62, capa="mano_crayola"):
    x, y = tip; put(c, capa, x + 745.5 * s + 1.4 * math.sin(T * 31), y + 75 * s + 1.4 * math.cos(T * 27), s)

SC = []
def esc(t0, suave=False):
    def deco(fn): SC.append((t0, fn, suave)); return fn
    return deco
def _mesa(T, t0, zoom=1.0): return bg("bg_mesa", T, t0, 1.15 * zoom, 1.2 * zoom, 4, .45, .5)

# ================================================================ ESCENAS DEL DÍA 3 (un plano cada ~2 s)
HAR = (252, 250, 244); MAD2 = (150, 100, 56); NAR = (238, 124, 40); MORA = (150, 110, 200)

@lru_cache(None)
def _coment(i, w=730):
    """Comentario real del vídeo anterior (captura), recortado a su contenido, con esquinas redondas."""
    im = Image.open(os.path.join(HERE, "coment_d4", f"c{i}.jpg")).convert("RGB"); g = im.convert("L").point(lambda v: 255 if v < 244 else 0); bb = g.getbbox()
    im = im.crop((max(0, bb[0] - 26), max(0, bb[1] - 22), min(im.width, bb[2] + 26), min(im.height, bb[3] + 22))); full = Image.new("RGB", (1080, im.height), (255, 255, 255)); full.paste(im, (0, 0))
    full = full.resize((w, int(w * full.height / 1080)), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", full.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, full.width - 1, full.height - 1), 26, fill=255); full.putalpha(m); return full

def harina(c, T, t0, cx=500, cy=900, rx=430, ry=330, k=1.0):
    """Mancha de harina sobre la mesa (borde suave)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); r = random.Random(7)
    for i in range(26):
        a = i / 26 * 2 * PI_; rr = r.uniform(.82, 1.06) * k
        d.ellipse((cx + rx * rr * math.cos(a) - 120, cy + ry * rr * math.sin(a) - 120, cx + rx * rr * math.cos(a) + 120, cy + ry * rr * math.sin(a) + 120), fill=HAR + (255,))
    d.ellipse((cx - rx * k, cy - ry * k, cx + rx * k, cy + ry * k), fill=HAR + (255,))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh.paste((90, 60, 30, 90), (0, 0), lay.split()[3]); c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), (0, 10))
    c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(5)))

def surco(c, pts, w=46):
    """Lo que el dedo deja al pasar por la harina: se ve la madera."""
    if len(pts) < 2: return
    d = ImageDraw.Draw(c); d.line(pts, fill=MAD2, width=int(w), joint="curve")
    for p in (pts[0], pts[-1]): d.ellipse((p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2), fill=MAD2)
    d.line([(x - 5, y - 6) for x, y in pts], fill=(232, 226, 212), width=5, joint="curve")

def dedo(c, tip, T, s=1.0):
    x, y = tip[0] + 2 * math.sin(T * 30), tip[1] + 2 * math.cos(T * 26); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.polygon([(x + 150 * s, y + 250 * s), (x + 520 * s, y + 900 * s), (x + 900 * s, y + 700 * s), (x + 330 * s, y + 130 * s)], fill=(63, 127, 208, 255)); d.line([(x + 150 * s, y + 250 * s), (x + 520 * s, y + 900 * s)], fill=OL, width=7); d.line([(x + 330 * s, y + 130 * s), (x + 900 * s, y + 700 * s)], fill=OL, width=7)
    d.ellipse((x + 110 * s, y + 90 * s, x + 370 * s, y + 330 * s), fill=PIEL, outline=OL, width=7)
    d.line([(x + 14 * s, y + 14 * s), (x + 190 * s, y + 170 * s)], fill=OL, width=int(74 * s)); d.line([(x + 14 * s, y + 14 * s), (x + 190 * s, y + 170 * s)], fill=PIEL, width=int(60 * s))
    d.ellipse((x - 16 * s, y - 16 * s, x + 44 * s, y + 44 * s), fill=PIEL, outline=OL, width=6)
    c.alpha_composite(lay)

def letraM(x, y, w, h, seed, humps=2, j=5):
    P = [(x, y + h), (x + 4, y), (x + w / 2, y + h * .62), (x + w - 4, y - 4), (x + w, y + h)]
    return _poli(P, 8, seed, j)
HM = [letraM(120, 640, 250, 300, 21), letraM(470, 610, 240, 290, 22), letraM(150, 1010, 230, 250, 23), letraM(520, 1000, 200, 220, 24)]   # la mamá cuenta tres… y hay cuatro

def bolsa(c, cx, cy, s, rot):
    t = Image.new("RGBA", (420, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
    d.polygon([(40, 120), (380, 120), (400, 540), (20, 540)], fill=(240, 226, 196)); d.line([(40, 120), (380, 120), (400, 540), (20, 540), (40, 120)], fill=OL, width=8)
    d.polygon([(40, 120), (90, 30), (330, 30), (380, 120)], fill=(226, 208, 172)); d.line([(40, 120), (90, 30), (330, 30), (380, 120)], fill=OL, width=8)
    d.rounded_rectangle((80, 230, 340, 400), 18, fill=ROJO, outline=OL, width=6); d.text((210, 314), "HARINA", font=font(F_ANTON, 62), fill=CREMA, anchor="mm")
    paste_rot(c, t, cx, cy, s, rot)

def brazos(c, hx, hy, s):
    """Brazos cruzados sobre el pecho."""
    d = ImageDraw.Draw(c); y = hy + 470 * s
    for sx in (-1, 1):
        ex, ey = hx - sx * 150 * s, y + 70 * s * (1 if sx < 0 else .2)
        d.line([(hx + sx * 250 * s, y - 40 * s), (ex, ey)], fill=OL, width=int(128 * s)); d.line([(hx + sx * 250 * s, y - 40 * s), (ex, ey)], fill=(63, 127, 208), width=int(112 * s))
        d.ellipse((ex - 58 * s, ey - 58 * s, ex + 58 * s, ey + 58 * s), fill=PIEL, outline=OL, width=6)

def manchas(c, hx, hy, s):
    d = ImageDraw.Draw(c)
    for dx, dy, r in ((-150, 120, 34), (120, 60, 26), (10, 20, 22), (170, 150, 20)): d.ellipse((hx + dx * s - r * s, hy + dy * s - r * s, hx + dx * s + r * s, hy + dy * s + r * s), fill=HAR)

def volando(c, x, y, rot, s=.6):
    d = ImageDraw.Draw(c)
    for i in range(3): d.line((x + 90 + i * 50, y - 60 + i * 44, x + 250 + i * 50, y - 130 + i * 44), fill=TIZA, width=9)
    put(c, "crayola", x, y, s, rot=rot)

BATA_ = (63, 127, 208); CREMA_ = (255, 253, 244)
def _ang(T):
    """Ángulos (brazo, antebrazo) del lanzamiento: se echa atrás y latiga hacia delante."""
    if T < .16: u = ease(T / .16); return -40 - 12 * u, -80 - 18 * u
    u = clamp((T - .16) / .13); u = 1 - (1 - u) ** 3; r = 5 * math.exp(-(T - .29) * 9) * math.cos((T - .29) * 26) if T > .29 else 0
    return -52 + 66 * u + r, -98 + 96 * u + r * 1.6
def brazo_tira(c, ox, oy, a1, a2, s, con_crayola):
    """Brazo que lanza, dibujado a 2x para que el borde salga limpio. Devuelve la posición de la mano."""
    K = 2; lay = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    P = lambda x, y: (x * K, y * K); w = 100 * s
    ex, ey = ox + 150 * s * math.cos(math.radians(a1)), oy + 150 * s * math.sin(math.radians(a1))
    ux, uy = math.cos(math.radians(a2)), math.sin(math.radians(a2)); L = 150 * s
    hx, hy = ex + L * ux, ey + L * uy; mx, my = hx + 36 * s * ux, hy + 36 * s * uy
    def seg(a, b, col, ww, cap=True):
        d.line(P(*a) + P(*b), fill=col, width=int(ww * K))
        if cap:
            for q in (a, b): d.ellipse((q[0] * K - ww * K / 2, q[1] * K - ww * K / 2, q[0] * K + ww * K / 2, q[1] * K + ww * K / 2), fill=col)
    for a, b in (((ox, oy), (ex, ey)), ((ex, ey), (hx, hy))): seg(a, b, OL, w + 14 * s)
    d.ellipse((mx * K - 53 * s * K, my * K - 51 * s * K, mx * K + 53 * s * K, my * K + 51 * s * K), fill=OL)
    for a, b in (((ox, oy), (ex, ey)), ((ex, ey), (hx, hy))): seg(a, b, BATA_, w)
    q0 = (hx - 62 * s * ux, hy - 62 * s * uy); seg(q0, (hx, hy), OL, w + 14 * s, False); seg((q0[0] + 6 * s * ux, q0[1] + 6 * s * uy), (hx - 6 * s * ux, hy - 6 * s * uy), CREMA_, w, False)
    d.ellipse((mx * K - 46 * s * K, my * K - 44 * s * K, mx * K + 46 * s * K, my * K + 44 * s * K), fill=PIEL)
    c.alpha_composite(lay.resize((W, H), Image.LANCZOS))
    if con_crayola: put(c, con_crayola if isinstance(con_crayola, str) else "crayola", mx + 30 * s * ux, my + 30 * s * uy, .62, rot=-a2)
    return mx, my

# ================================================================ ESCENAS DEL DÍA 4 — La M en el sofá (un plano cada ~2 s)
NEGRO = (24, 22, 30); VERDE_C = (86, 176, 110)

@lru_cache(8)
def fondo2(name): return R.layer(name)
def vista(name, cx, cy, z):
    """Encuadre de un fondo (capa 2x) centrado en (cx, cy) con zoom z. Devuelve la imagen y la transformación fondo→pantalla."""
    im = fondo2(name); w, h = 2 * W / z, 2 * H / z
    x0 = min(max(cx * 2 - w / 2, 0), 2 * W - w); y0 = min(max(cy * 2 - h / 2, 0), 2 * H - h)
    c = im.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + w, y0 + h)).convert("RGBA")
    return c, (lambda p: ((p[0] - x0 / 2) * z, (p[1] - y0 / 2) * z))
def trazo(c, pts, w, col=NEGRO):
    """Trazo de marcador (borde limpio: se dibuja a 2x)."""
    if len(pts) < 2: return
    K = 2; m = Image.new("L", (W * K, H * K), 0); d = ImageDraw.Draw(m); q = [(x * K, y * K) for x, y in pts]
    d.line(q, fill=255, width=int(w * K), joint="curve")
    for p in q[::3] + [q[-1]]: d.ellipse((p[0] - w * K / 2, p[1] - w * K / 2, p[0] + w * K / 2, p[1] + w * K / 2), fill=255)
    lay = Image.new("RGBA", (W, H), col + (255,)); lay.putalpha(m.resize((W, H), Image.LANCZOS)); c.alpha_composite(lay)

# la M del sofá (coordenadas del fondo bg_sala): sube, baja, sube, baja
MS = [_poli([(400, 1030), (398, 800)], 10, 41, 1.6), _poli([(398, 800), (540, 962)], 10, 42, 1.6), _poli([(540, 962), (682, 800)], 10, 43, 1.6), _poli([(682, 800), (684, 1030)], 10, 44, 1.6)]
MS_ALL = [p for s_ in MS for p in s_]
def sofa(cx, cy, z, u=1.0):
    c, tr = vista("bg_sala", cx, cy, z); pts = parcial(MS_ALL, u)
    if pts: trazo(c, [tr(p) for p in pts], 26 * z)
    return c, tr
def borroso(c, r=14, a=70):
    c = c.filter(ImageFilter.GaussianBlur(r)); oscurecer(c, (20, 18, 40), a); return c
def dulce_ico(c, x, y, s, tachado=0.0, rot=-12):
    put(c, "dulce", x, y, s, rot=rot)
    if tachado > 0:
        d = ImageDraw.Draw(c); r = 150 * s; u = clamp(tachado)
        d.line((x - r, y - r, x - r + 2 * r * u, y - r + 2 * r * u), fill=ROJO, width=int(26 * s) + 6)
        if u > .5: d.line((x + r, y - r, x + r - 2 * r * (u - .5) * 2, y - r + 2 * r * (u - .5) * 2), fill=ROJO, width=int(26 * s) + 6)

_ico3 = icono_tarjeta
def icono_tarjeta(d, ix, iy, k, icono):
    if icono == "castigo":      # el marcador, prohibido
        d.rounded_rectangle((ix - 96 * k, iy - 24 * k, ix + 40 * k, iy + 24 * k), 10 * k, fill=NEGRO, outline=OL, width=max(3, int(6 * k)))
        d.polygon([(ix + 40 * k, iy - 18 * k), (ix + 98 * k, iy), (ix + 40 * k, iy + 18 * k)], fill=(70, 66, 86), outline=OL)
        d.ellipse((ix - 118 * k, iy - 118 * k, ix + 118 * k, iy + 118 * k), outline=CREMA, width=max(4, int(20 * k)))
        d.line((ix - 82 * k, iy - 82 * k, ix + 82 * k, iy + 82 * k), fill=CREMA, width=max(4, int(20 * k)))
    elif icono == "celebrar":   # estrella con su M
        P = [(ix + (118 if i % 2 == 0 else 52) * k * math.sin(i * PI_ / 5), iy - (118 if i % 2 == 0 else 52) * k * math.cos(i * PI_ / 5)) for i in range(10)]
        d.polygon(P, fill=AMA, outline=OL); d.line(P + [P[0]], fill=OL, width=max(3, int(8 * k)), joint="curve")
        d.text((ix, iy + 4 * k), "M", font=font(F_AND, 96 * k), fill=OL, anchor="mm")
    else: _ico3(d, ix, iy, k, icono)

AB = (270, 270, 816, 1356)      # hueco de la puerta en bg_puerta
def puerta(T, cx, cy, z, abierta=1.0, papa=0.0, px=560):
    """La puerta de entrada: se abre (abierta 0→1) y papá aparece a contraluz con su sombra larga."""
    c, tr = vista("bg_puerta", cx, cy, z); d = ImageDraw.Draw(c)
    if abierta < .5:       # puerta cerrada: la hoja abierta del fondo no se ve
        a, b = tr((822, 180)), tr((1080, 1352)); d.rectangle((a[0], a[1], b[0], b[1]), fill=c.getpixel((int(tr((60, 300))[0]) if tr((60, 300))[0] > 0 else 4, int(tr((60, 300))[1]))))
    if papa > 0:
        s = .64 * z; fx, fy = tr((px, AB[3] - 6)); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(lay).polygon([(fx - 150 * z, fy), (fx + 150 * z, fy), (fx - 80 * z, fy + 900 * z), (fx - 620 * z, fy + 900 * z)], fill=(20, 16, 40, int(120 * papa)))
        c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10))); put(c, "papa_silueta", fx, fy - 810 * s + 14 * (1 - papa), s, alpha=clamp(papa))
    if abierta < 1:
        a, b = tr((AB[0], AB[1])), tr((AB[0] + (AB[2] - AB[0]) * (1 - abierta), AB[3]))
        if b[0] - a[0] > 4:
            d = ImageDraw.Draw(c); d.rectangle((a[0], a[1], b[0], b[1]), fill=(176, 106, 52), outline=OL, width=7)
            d.rectangle((a[0] + 40 * z, a[1] + 60 * z, b[0] - 40 * z, a[1] + 480 * z), outline=(140, 82, 40), width=7) if b[0] - a[0] > 120 * z else None
            kx, ky = b[0] - 46 * z, (a[1] + b[1]) / 2 + 30 * z; d.ellipse((kx - 22 * z, ky - 22 * z, kx + 22 * z, ky + 22 * z), fill=AMA, outline=OL, width=5)
    return c

# ================================================================ ESCENAS DEL DÍA 5 — «Solo sabe una letra» (ganó CASTIGO). Fórmula de los virales:
# tú eres la mamá, vuelve Rex, un momento de ternura, el truco de la M paso a paso y un «¿Qué harías tú?» con pro y contra.
NEGRO = (24, 22, 30); VERDE_C = (86, 176, 110); REXV = (108, 196, 106); REXO = (46, 120, 62); NOCHE = (14, 18, 52)
SUB = "↑"; BAJ = "↓"

@lru_cache(None)
def hojaM(blancos=True, nombre=True, seed=61):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); lay.alpha_composite(hoja_img(), (70, 600)); d = ImageDraw.Draw(lay)
    if nombre: d.text((130, 668), "Mi nombre:", font=font(F_AND, 46), fill=(120, 120, 140), anchor="lm")
    crayon(lay, letraM(170, 800, 240, 290, seed, j=4), 26, VERDE)
    if blancos:
        for k in range(4): d.line((480 + k * 118, 1092, 480 + k * 118 + 84, 1092), fill=(150, 150, 168), width=9)
    return lay.crop((60, 590, 1020, 1290))

def hoja_en(c, cx, cy, s=1.0, rot=0, blancos=True, sombra_=True):
    im = hojaM(blancos)
    if sombra_: sombra(c, (cx - 470 * s, cy - 340 * s, cx + 470 * s, cy + 340 * s), 8, 100, 16)
    paste_rot(c, im, cx, cy, s, rot)

def lagrimas(c, x, y, T, n=3, s=1.0):
    d = ImageDraw.Draw(c)
    for i in range(n):
        u = ((T * 1.3 + i / n) % 1); yy = y + 260 * s * u; xx = x + (i - 1) * 150 * s + 10 * math.sin(T * 5 + i); r = 15 * s * (1 - .4 * u)
        d.polygon([(xx, yy - 2.2 * r), (xx - r, yy), (xx + r, yy)], fill=(120, 190, 240)); d.ellipse((xx - r, yy - r, xx + r, yy + r), fill=(120, 190, 240), outline=(60, 120, 190), width=3)

def nino_sil(c, x, y, s, T, ph=0.0, col=(40, 46, 86), risa=True):
    """Compañero de clase a contraluz, riéndose (sin cara reconocible: el que importa es Mateo)."""
    y = y - 22 * s * abs(math.sin(T * 9 + ph)); d = ImageDraw.Draw(c); r = 118 * s
    d.rounded_rectangle((x - 170 * s, y + 90 * s, x + 170 * s, y + 700 * s), int(90 * s), fill=col)
    d.ellipse((x - r, y - r, x + r, y + r), fill=col)
    d.pieslice((x - 40 * s, y - 168 * s, x + 80 * s, y - 60 * s), 180, 330, fill=col)
    if risa:
        for sx in (-1, 1): d.arc((x + sx * 48 * s - 26 * s, y - 34 * s, x + sx * 48 * s + 26 * s, y + 14 * s), 200, 340, fill=CREMA, width=max(3, int(8 * s)))
        d.chord((x - 52 * s, y + 4 * s, x + 52 * s, y + 84 * s), 0, 180, fill=CREMA)

def jaja(c, T, t0, pts, col=AMA):
    for i, (x, y, sz, rot) in enumerate(pts):
        k = pop(T, t0 + i * .12, .2)
        if k > 0: tiza(c, "JA", x + 6 * math.sin(T * 14 + i), y + 6 * math.cos(T * 11 + i), sz * k, col, rot, f=F_BAL, stroke=3, borde=True)

def brazo_mama(c, hx, hy, s, u=1.0):
    """Tu brazo (el de mamá) entra por la derecha y se apoya en su hombro."""
    K = 2; lay = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    ex, ey = hx + 190 * s + 700 * (1 - u), hy + 330 * s; ox, oy = W + 160, ey + 260
    d.line((ox * K, oy * K, ex * K, ey * K), fill=OL, width=int(150 * s * K)); d.line((ox * K, oy * K, ex * K, ey * K), fill=(226, 120, 140), width=int(134 * s * K))
    d.ellipse(((ex - 80 * s) * K, (ey - 70 * s) * K, (ex + 70 * s) * K, (ey + 70 * s) * K), fill=PIEL, outline=OL, width=7 * K)
    c.alpha_composite(lay.resize((W, H), Image.LANCZOS))

def corazon(c, x, y, r, col=ROJO):
    if r <= 1: return
    K = 2; lay = Image.new("RGBA", (int(r * 5) * K, int(r * 5) * K), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); ix, iy = lay.width / 2, lay.height / 2; r2 = r * K
    d.ellipse((ix - 2 * r2, iy - 1.5 * r2, ix, iy + .5 * r2), fill=col, outline=OL, width=max(3, int(r2 * .12))); d.ellipse((ix, iy - 1.5 * r2, ix + 2 * r2, iy + .5 * r2), fill=col, outline=OL, width=max(3, int(r2 * .12)))
    d.polygon([(ix - 1.86 * r2, iy - .1 * r2), (ix + 1.86 * r2, iy - .1 * r2), (ix, iy + 1.9 * r2)], fill=col)
    d.line([(ix - 1.86 * r2, iy - .05 * r2), (ix, iy + 1.9 * r2), (ix + 1.86 * r2, iy - .05 * r2)], fill=OL, width=max(3, int(r2 * .12)), joint="curve")
    lay = lay.resize((lay.width // K, lay.height // K), Image.LANCZOS); c.alpha_composite(lay, (int(x - lay.width / 2), int(y - lay.height / 2)))

def corazones(c, cx, cy, T, t0, n=5, seed=3):
    r = random.Random(seed)
    for i in range(n):
        ph = r.uniform(0, 1); dx = r.uniform(-260, 260); u = ((T - t0) * .45 + ph) % 1
        if T - t0 < ph * .6: continue
        corazon(c, cx + dx + 20 * math.sin(T * 3 + i), cy - 420 * u, 26 * math.sin(PI_ * u) + 2)

@lru_cache(4)
def luz_img(cx, cy, rad, a):
    yy, xx = np.mgrid[0:H, 0:W]; dd = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / rad; al = np.clip(dd, 0, 1) ** 1.6 * a
    im = np.zeros((H, W, 4), np.uint8); im[..., 0], im[..., 1], im[..., 2] = NOCHE; im[..., 3] = al.astype(np.uint8); return Image.fromarray(im, "RGBA")
def noche(c, cx=540, cy=900, rad=900, a=200):
    c.alpha_composite(Image.new("RGBA", (W, H), (255, 190, 90, 18))); c.alpha_composite(luz_img(cx, cy, rad, a))

def huella(c, x, y, s, col=REXO, rot=0):
    lay = Image.new("RGBA", (int(220 * s), int(220 * s)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); m = lay.width / 2
    d.ellipse((m - 52 * s, m - 14 * s, m + 52 * s, m + 78 * s), fill=col)
    for dx, dy in ((-62, -40), (0, -72), (62, -40)): d.ellipse((m + dx * s - 24 * s, m + dy * s - 28 * s, m + dx * s + 24 * s, m + dy * s + 28 * s), fill=col)
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC)
    c.alpha_composite(lay, (int(x - m), int(y - m)))

def pata(c, x, y, s, rot=0):
    """La patita de Rex."""
    lay = Image.new("RGBA", (int(420 * s), int(420 * s)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); m = lay.width / 2
    d.line((m + 40 * s, m, m + 205 * s, m - 40 * s), fill=OL, width=int(128 * s)); d.line((m + 40 * s, m, m + 205 * s, m - 40 * s), fill=REXV, width=int(112 * s))
    d.ellipse((m - 100 * s, m - 82 * s, m + 84 * s, m + 82 * s), fill=REXV, outline=OL, width=max(4, int(8 * s)))
    for dy in (-46, 0, 46): d.ellipse((m - 128 * s, m + dy * s - 20 * s, m - 80 * s, m + dy * s + 20 * s), fill=CREMA, outline=OL, width=max(3, int(5 * s)))
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC)
    c.alpha_composite(lay, (int(x - m), int(y - m)))

BK = 1.55      # Bruno es más grande que Mateo
def bruno_(c, kind, hx, hy, s, T, lid=None):
    """Bruno: personaje propio (bruno_art.py) — grandote, rubio de punta, curita, le falta un diente, suéter morado de rayas. Cara y voz fijas."""
    hab = lid is not None and talk(lid, T)
    if hab: kind = "rie" if int(T * 9) % 2 == 0 else "rie2"
    put(c, f"bruno_{kind}", hx, hy + 498 * s * BK, s * BK)

def hoja_blanca(c, T, t0, dy=0):
    sombra(c, (110, 600 + dy, 970, 1250 + dy), 8, 110, 18); d = ImageDraw.Draw(c); d.rectangle((110, 600 + dy, 970, 1250 + dy), fill=CREMA, outline=(214, 190, 150), width=7)

def rex(c, x, y, s, T, rot=0): put(c, "dino", x, y + 4 * math.sin(T * 2.4), s, rot=rot)
def suelo(T, t0, cx=540, cy=1500, z=1.5):
    c, tr = vista("bg_cuarto", cx, cy, z); return c, tr

def hoja_blanca_mini(c, cx, cy, s, rot):
    n = Image.new("RGBA", (880, 660), (0, 0, 0, 0)); d = ImageDraw.Draw(n); d.rectangle((4, 4, 875, 655), fill=CREMA + (255,), outline=(214, 190, 150, 255), width=8); paste_rot(c, n, cx, cy, s, rot)

_ico4 = icono_tarjeta
def icono_tarjeta(d, ix, iy, k, icono):
    if icono == "hablar":       # dos globos de diálogo
        d.rounded_rectangle((ix - 120 * k, iy - 110 * k, ix + 50 * k, iy + 10 * k), 30 * k, fill=CREMA, outline=OL, width=max(3, int(7 * k)))
        d.polygon([(ix - 80 * k, iy + 6 * k), (ix - 96 * k, iy + 56 * k), (ix - 30 * k, iy + 6 * k)], fill=CREMA, outline=OL)
        for q in (-78, -36, 6): d.ellipse((ix + q * k - 11 * k, iy - 61 * k, ix + q * k + 11 * k, iy - 39 * k), fill=OL)
        d.rounded_rectangle((ix - 30 * k, iy - 10 * k, ix + 124 * k, iy + 96 * k), 28 * k, fill=AMA, outline=OL, width=max(3, int(7 * k)))
        d.polygon([(ix + 80 * k, iy + 92 * k), (ix + 104 * k, iy + 134 * k), (ix + 40 * k, iy + 92 * k)], fill=AMA, outline=OL)
    elif icono == "solo":       # escudo con estrella: se defiende él
        P = [(ix - 100 * k, iy - 110 * k), (ix + 100 * k, iy - 110 * k), (ix + 100 * k, iy + 10 * k), (ix, iy + 124 * k), (ix - 100 * k, iy + 10 * k)]
        d.polygon(P, fill=AMA, outline=OL); d.line(P + [P[0]], fill=OL, width=max(3, int(8 * k)), joint="curve")
        S_ = [(ix + (70 if i % 2 == 0 else 30) * k * math.sin(i * PI_ / 5), iy - 14 * k - (70 if i % 2 == 0 else 30) * k * math.cos(i * PI_ / 5)) for i in range(10)]
        d.polygon(S_, fill=CREMA, outline=OL)
    else: _ico4(d, ix, iy, k, icono)

def pro_contra(c, cx, y, pro, contra, k1, k2, rot=0):
    for txt, yy, col, sg, k in ((pro, y, VERDE_C, "+", k1), (contra, y + 80, ROJO, "–", k2)):
        if k <= 0: continue
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); f = font(F_BAL, 38 * k); w = d.textlength(txt, font=f) + 86 * k; x0 = cx - w / 2
        d.rounded_rectangle((x0, yy - 35 * k, x0 + w, yy + 35 * k), 16, fill=CREMA + (255,), outline=OL + (255,), width=5)
        d.ellipse((x0 + 8 * k, yy - 26 * k, x0 + 60 * k, yy + 26 * k), fill=col + (255,)); d.text((x0 + 34 * k, yy - 3 * k), sg, font=font(F_BAL, 50 * k), fill=CREMA, anchor="mm")
        d.text((x0 + 70 * k, yy), txt, font=f, fill=OL, anchor="lm"); c.alpha_composite(lay.rotate(rot, center=(cx, yy), resample=Image.BICUBIC))

# ================================================================ ESCENAS DEL DÍA 6 — «La abuela tampoco sabía» (ganó MAESTRA)
# Aprendido del Día 5: gancho de 3 s sin resumen, Rex antes del segundo 35, «mándaselo» dicho en voz en el momento tierno.
AK = 1.6      # la abuela es adulta: más grande que Mateo
def abuela(c, kind, hx, hy, s, T, lid=None):
    """La abuela Pilar: personaje propio (abuela_art.py). Cara y voz fijas para toda la temporada."""
    if lid is not None and talk(lid, T): kind = "habla" if int(T * 9) % 2 == 0 else "habla2"
    put(c, f"abuela_{kind}", hx, hy + 498 * s * AK + 3 * math.sin(T * 2.2), s * AK)

def globo(c, cx, cy, w, h, lineas, k=1.0, cola=(0, 1), rot=-3, sz=92):
    if k <= 0: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    d.rounded_rectangle((x0, y0, x1, y1), 56, fill=CREMA + (255,), outline=OL + (255,), width=8); tx = cx + cola[0] * w * .3
    d.polygon([(tx - 50, y1 - 8), (tx + cola[0] * 60, y1 + 110), (tx + 50, y1 - 8)], fill=CREMA + (255,)); d.line([(tx - 50, y1 - 2), (tx + cola[0] * 60, y1 + 110), (tx + 50, y1 - 2)], fill=OL + (255,), width=8)
    n = len(lineas)
    for i, (txt, col) in enumerate(lineas): d.text((cx, cy + (i - (n - 1) / 2) * sz * 1.15), txt, font=font(F_BAL, sz), fill=col, anchor="mm")
    lay = lay.rotate(rot, center=(cx, cy), resample=Image.BICUBIC)
    if k != 1:
        k = max(.05, k); sm = lay.resize((int(W * k), int(H * k)), Image.LANCZOS); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); lay.alpha_composite(sm, (max(0, int(cx - cx * k)), max(0, int(cy - cy * k)))) if k <= 1 else lay.alpha_composite(sm.crop((int(cx * k - cx), int(cy * k - cy), int(cx * k - cx) + W, int(cy * k - cy) + H)))
    c.alpha_composite(lay)

@lru_cache(1)
def nota_rex():
    """La nota de Rex del Día 5, ya escrita (la que Mateo guarda como su secreto)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); put(lay, "nota", 540, 800, .9); r = random.Random(9)
    for txt, y in (("Hola, Mateo.", 470), ("Soy Rex.", 630), ("Yo no sé hacer la M.", 790), ("¿Me enseñas?", 950)):
        x = 230; t = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(t)
        for ch in txt:
            sz = 92 + r.uniform(-9, 9); f = font(F_HAND, sz); d.text((x, y + r.uniform(-9, 9)), ch, font=f, fill=REXO + (255,), anchor="lm", stroke_width=2, stroke_fill=REXO + (255,)); x += d.textlength(ch, font=f) + r.uniform(0, 5) + (26 if ch == " " else 0)
        lay.alpha_composite(t)
    huella(lay, 760, 1130, 1.0, REXO, -14)
    return lay.crop((int(540 - 432), int(800 - 522), int(540 + 432), int(800 + 522)))

@lru_cache(4)
def hoja_M_mateo(k=1.0):
    """La hoja de M que Mateo le deja a Rex."""
    n = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(n); d.rectangle((110, 600, 970, 1250), fill=CREMA + (255,), outline=(214, 190, 150, 255), width=7)
    for i in range(3): crayon(n, letraM(190 + i * 250, 740, 190, 300, 30 + i, j=6), 24, VERDE)
    return n.crop((100, 590, 980, 1260))

def avion(c, x, y, s, rot=0):
    lay = Image.new("RGBA", (int(300 * s), int(300 * s)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); m = lay.width / 2
    P = [(m - 120 * s, m - 20 * s), (m + 130 * s, m - 100 * s), (m + 20 * s, m + 120 * s), (m - 10 * s, m + 30 * s)]
    d.polygon(P, fill=CREMA, outline=OL); d.line(P + [P[0]], fill=OL, width=max(4, int(9 * s)), joint="curve"); d.line((m - 10 * s, m + 30 * s, m + 130 * s, m - 100 * s), fill=OL, width=max(4, int(8 * s)))
    c.alpha_composite(lay.rotate(rot, resample=Image.BICUBIC), (int(x - m), int(y - m)))

# ================================================================ ESCENAS DEL DÍA 7 — «Primera victoria» (ganó ABUELA)
# Para ti frío: gancho con pregunta abierta (M perfecta + llanto), sin resumen ni nombres; Rex y «mándale esto» hacia el segundo 35.
def Mperf(x, y, w, h, seed, j=1.2):
    return _poli([(x, y + h), (x, y), (x + w / 2, y + h * .62), (x + w, y), (x + w, y + h)], 12, seed, j)
def estrella(c, x, y, r, col=AMA, rot=0):
    if r <= 2: return
    K = 2; lay = Image.new("RGBA", (int(r * 2.6) * K, int(r * 2.6) * K), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); m = lay.width / 2
    P = [(m + (r if i % 2 == 0 else r * .45) * K * math.sin(i * PI_ / 5 + rot), m - (r if i % 2 == 0 else r * .45) * K * math.cos(i * PI_ / 5 + rot)) for i in range(10)]
    d.polygon(P, fill=col); d.line(P + [P[0]], fill=OL, width=max(4, int(r * .14)), joint="curve")
    lay = lay.resize((lay.width // K, lay.height // K), Image.LANCZOS); c.alpha_composite(lay, (int(x - lay.width / 2), int(y - lay.height / 2)))
def hojita(c, x0, y0, x1, y1):
    sombra(c, (x0, y0, x1, y1), 8, 110, 18); ImageDraw.Draw(c).rectangle((x0, y0, x1, y1), fill=CREMA, outline=(214, 190, 150), width=7)
def noche7(c, cx=540, cy=900, rad=1000, a=190): noche(c, cx, cy, rad, a)

# ================================================================ ESCENAS DEL DÍA 8 — «Pone mamá» (ganó SEGUIMOS)
# Estructura del vídeo de 1M: pelea de casa en 3 s · mamá inventa el buzón de Rex · el juego se repite · pasan los días (8 → 11)
# · «él solo agarra el crayón» · la maestra lo confirma · golpe final de Mateo y corte directo a un dilema moral. Sin pedir compartir.
CAJA = (184, 132, 84); CAJA_C = (214, 166, 112); CAJA_S = (150, 104, 62)
def caja(c, cx, cy, s=1.0, ranura=1.0, rex=1.0, dino=1.0, brillo=0.0):
    """El buzón de Rex: una caja de zapatos con una ranura y «REX» escrito con crayón."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); w, h, p = 290 * s, 170 * s, 110 * s
    sombra(c, (cx - w, cy + h - 30 * s, cx + w + p * .6, cy + h + 30 * s), 10, 110, 22)
    d.polygon([(cx + w, cy - h), (cx + w + p, cy - h - p * .55), (cx + w + p, cy + h - p * .55), (cx + w, cy + h)], fill=CAJA_S, outline=OL)
    d.polygon([(cx - w, cy - h), (cx - w + p, cy - h - p * .55), (cx + w + p, cy - h - p * .55), (cx + w, cy - h)], fill=CAJA_C, outline=OL)
    d.rectangle((cx - w, cy - h, cx + w, cy + h), fill=CAJA, outline=OL, width=max(4, int(8 * s)))
    for P in ([(cx + w, cy - h), (cx + w + p, cy - h - p * .55), (cx + w + p, cy + h - p * .55), (cx + w, cy + h)], [(cx - w, cy - h), (cx - w + p, cy - h - p * .55), (cx + w + p, cy - h - p * .55), (cx + w, cy - h)]):
        d.line(P + [P[0]], fill=OL, width=max(4, int(8 * s)), joint="curve")
    if ranura > 0:
        rw = 150 * s * clamp(ranura); rx, ry = cx + p * .5, cy - h - p * .275
        d.polygon([(rx - rw, ry + 12 * s), (rx - rw + 22 * s, ry - 12 * s), (rx + rw + 22 * s, ry - 12 * s), (rx + rw, ry + 12 * s)], fill=(50, 34, 26))
    n = int(clamp(rex) * 3 + .001)
    if n > 0: d.text((cx - 60 * s, cy - 6 * s), "REX"[:n], font=font(F_HAND, 230 * s), fill=VERDE, anchor="mm", stroke_width=max(2, int(4 * s)), stroke_fill=VERDE)
    c.alpha_composite(lay)
    if dino > 0: put(c, "dino", cx + 195 * s, cy + 70 * s, .2 * s * clamp(dino))
    if brillo > 0: chispas(c, cx, cy, brillo, 0, 6, int(330 * s), 61)
def ranura_xy(cx, cy, s=1.0): return cx + 110 * s * .5 + 10 * s, cy - 170 * s - 110 * s * .275

def sobre(c, x, y, s, rot=0, corazon_=True):
    lay = Image.new("RGBA", (int(360 * s), int(260 * s)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); w, h = lay.width, lay.height
    d.rounded_rectangle((6, 6, w - 6, h - 6), int(14 * s), fill=(255, 253, 244), outline=OL, width=max(4, int(7 * s)))
    d.line([(8, 10), (w / 2, h * .58), (w - 8, 10)], fill=OL, width=max(3, int(6 * s)), joint="curve")
    if corazon_: r = 20 * s; d.ellipse((w / 2 - 2 * r, h * .58 - r, w / 2, h * .58 + r), fill=ROJO); d.ellipse((w / 2, h * .58 - r, w / 2 + 2 * r, h * .58 + r), fill=ROJO); d.polygon([(w / 2 - 1.86 * r, h * .58 + .3 * r), (w / 2 + 1.86 * r, h * .58 + .3 * r), (w / 2, h * .58 + 2.2 * r)], fill=ROJO)
    paste_rot(c, lay, x, y, 1.0, rot)

NX, NY, NS = 540, 800, .9
def nota_base(c, dy=0):
    sombra(c, (NX - 470 * NS, NY - 570 * NS + dy, NX + 470 * NS, NY + 570 * NS + dy), 10, 120, 20); put(c, "nota", NX, NY + dy, NS)
def mk_carta(lid, filas, seed, rojas=("M.", "A?")):
    r = random.Random(seed); out = []; cap = [x for x in LINEAS if x[0] == lid][0][3].split(); wt = R.word_times(lid, cap); d = ImageDraw.Draw(Image.new("L", (8, 8)))
    for txt, idx, y in filas:
        x = 230
        for w, wi in zip(txt.split(" "), idx):
            a, b = wt[wi]; a -= .12; b = max(b - .1, a + .12)
            for j, ch in enumerate(w):
                sz = 100 + r.uniform(-9, 9); wd = d.textlength(ch, font=font(F_HAND, sz))
                out.append((ch, x + wd / 2, y + r.uniform(-9, 9), r.uniform(-11, 11), sz, a + (b - a) * j / max(1, len(w)), w in rojas and ch in "MA")); x += wd + r.uniform(0, 5)
            x += 28
    return out
@lru_cache(None)
def _letra8(ch, sz, rot, col):
    t = Image.new("RGBA", (int(sz * 1.6), int(sz * 1.8)), (0, 0, 0, 0)); ImageDraw.Draw(t).text((t.width / 2, t.height / 2), ch, font=font(F_HAND, sz), fill=col + (255,), anchor="mm", stroke_width=2, stroke_fill=col + (255,))
    return t.rotate(rot, resample=Image.BICUBIC)
def carta(c, CT, T, t_hue, todo=False):
    tip = None
    for ch, x, y, rot, sz, t, roja in CT:
        if todo or T >= t:
            im = _letra8(ch, int(sz), round(rot), ROJO if roja else REXO); c.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))
            if not todo and T < t + .14: tip = (x + 14, y + 26)
    if todo or T >= t_hue: huella(c, 760, 1110, 1.0 * (1 if todo else pop(T, t_hue, .25)), REXO, -14)
    return tip

# barra con los días que pasan dentro del vídeo (Día 8 → 11) y la A que se enciende al final
DIA_T = []          # (instante, días que faltan, letras encendidas) — se rellena más abajo
_BARRAS = {}
def draw_hud(c, T):
    if T < T_HUD: return
    n, on = DIAS_FALTAN, LETRAS_ON
    for t, nn, oo in DIA_T:
        if T >= t: n, on = nn, oo
    if (n, on) not in _BARRAS: _BARRAS[(n, on)] = _barra_img(n, on)
    B = _BARRAS[(n, on)]; y = int(122 - 320 * (1 - ease((T - T_HUD) / .35)))
    if y >= 0: c.alpha_composite(B, (10, y))
    elif -y < B.height: c.alpha_composite(B, (10, 0), (0, -y, B.width, B.height))
def dia(c, T, t, n):
    k = pop(T, t, .22)
    if k > 0 and T < t + 1.6: rotulo(c, f"DÍA {n}", 860, 330, 64, AMA, OL, 4, k=k)

# ---------------------------------------------------------------- 1 · gancho: una pelea de casa, en 3 segundos
T_TIRA = WI("L01", 8) - .06
@esc(0)
def gancho(T, t0):
    c = _mesa(T, t0, 1.12); c = borroso(c, 4, 20); u = u_(T, T_TIRA, .7)
    mateo(c, "enojado" if T > WI("L01", 4) - .1 else "timido", 400, 760, 1.25 + .05 * u_(T, 0, 3), T, blink=False)
    p = 1 + .04 * math.exp(-T * 6) * math.cos(T * 22); rotulo(c, "8 DÍAS SIN PARAR", 540, 300, 88, ROJO, CREMA, -3, k=p)
    if T < T_TIRA: put(c, "crayola", 800, 1050 + 4 * math.sin(T * 9), .8, rot=-28)
    else:
        x = 800 + 150 * u; y = 1050 - 320 * math.sin(PI_ * min(1, u * 1.15)) + 520 * u * u; reb = 40 * abs(math.sin((u - 1) * 14)) * math.exp(-(T - T_TIRA - .7) * 5) if u >= 1 else 0
        put(c, "crayola", x, min(y, 1250) - reb, .8, rot=-28 - 420 * u)
        if u >= 1: jaja_ = pop(T, T_TIRA + .7, .15); tiza(c, "¡PAF!", 900, 1120, 90 * jaja_, AMA, 10, f=F_BAL, stroke=3, borde=True) if T < T_TIRA + 1.5 else None
    return c

@esc(S("L02") - .15)
def no_quiero(T, t0):
    c = _mesa(T, t0, 1.3); c = borroso(c, 10, 60); mateo(c, "enojado", 540 + 5 * math.sin(T * 20) * (1 - u_(T, t0, .5)), 800, 1.55 + .06 * u_(T, t0, 3), T, "L02", blink=False)
    k = pop(T, WI("L02", 4) - .1, .2)
    if k > 0: rotulo(c, "¡ES ABURRIDO!", 540, 400, 104, ROJO, CREMA, -5, k=k)
    return c

# ---------------------------------------------------------------- 2 · respiras… y sacas una caja de zapatos: el buzón de Rex (un solo plano largo)
T_RAN = WI("L04", 3) - .1; T_REX = WI("L04", 8) - .1; T_DIN = WI("L04", 11) - .1
@esc(S("L03") - .2, True)
def el_buzon(T, t0):
    c = _mesa(T, t0, 1.05); u = ease((T - WI("L03", 2) + .1) / .5) if T > WI("L03", 2) - .1 else 0
    k = pop(T, t0 + .1, .3)
    if k > 0 and T < WI("L03", 2): tiza(c, "RESPIRAS…", 540, 820, 150 * k, OL, -2, f=F_BAL)
    if u > 0:
        caja(c, 500, 940 + 900 * (1 - u), 1.25, ranura=u_(T, T_RAN, .5), rex=u_(T, T_REX, .9) if T >= T_REX else 0, dino=pop(T, T_DIN, .3), brillo=(T - T_DIN) if T >= T_DIN else 0)
        if T_RAN <= T < T_RAN + .7: rx, ry = ranura_xy(500, 940, 1.25); put(c, "crayola", rx - 150 + 300 * u_(T, T_RAN, .5), ry - 120, .3, rot=-60)
        if T_REX <= T < T_DIN: mano(c, (300 + 330 * u_(T, T_REX, .9), 1000), T, .8)
    k = pop(T, WI("L03", 4) - .1, .2)
    if k > 0 and T < T_RAN: rotulo(c, "UNA CAJA DE ZAPATOS", 540, 440, 76, CREMA, OL, -3, k=k)
    k = pop(T, T_REX + .5, .22)
    if k > 0: rotulo(c, "EL BUZÓN DE REX", 540, 440, 96, VERDE_C, CREMA, -3, k=k)
    k = pop(T, T_DIN, .22)
    if k > 0: rotulo(c, "SU DINOSAURIO", 560, 590, 62, AMA, OL, 3, k=k)
    return view(c, 540, 900, 1.0 + .1 * u_(T, t0, 9))

@esc(S("L05") - .15)
def tiene_buzon(T, t0):
    c = _mesa(T, t0, 1.25); c = borroso(c, 8, 40); mateo(c, "susto", 420, 800, 1.35, T, "L05", blink=False); caja(c, 850, 1130, .5)
    for i in range(3):
        k = pop(T, t0 + .15 + i * .12, .2)
        if k > 0: tiza(c, "?", 760 + i * 80, 560 - i * 60, (90 + i * 30) * k, AMA, -10 + i * 10, f=F_BAL, stroke=3, borde=True)
    return c

# ---------------------------------------------------------------- 3 · el juego: carta de noche, respuesta de mañana (un plano: de noche a día)
T_MAN = WI("L06", 6) - .1
@esc(S("L06") - .2, True)
def el_juego(T, t0):
    c = _mesa(T, t0, 1.05); caja(c, 520, 980, 1.2); rx, ry = ranura_xy(520, 980, 1.2); dn = 1 - u_(T, T_MAN - .2, .6)
    u = u_(T, WI("L06", 3) - .1, .7)
    if T < T_MAN and u < 1: sobre(c, rx + 10, ry - 420 + 400 * u, .8 * (1 - .5 * u), -8)
    if T >= T_MAN:
        v = u_(T, WI("L06", 9) - .1, .7); 
        if v > 0: sobre(c, rx + 10, ry - 20 - 400 * v, .4 + .5 * v, 6); chispas(c, rx, ry - 300, T, WI("L06", 9), 5, 220, 71)
    if dn > 0: c.alpha_composite(Image.new("RGBA", (W, H), NOCHE + (int(150 * dn),)))
    k = pop(T, t0 + .2, .22)
    if k > 0 and T < T_MAN: rotulo(c, "CADA NOCHE: UNA CARTA", 540, 440, 72, CREMA, OL, -3, k=k)
    k = pop(T, T_MAN, .22)
    if k > 0: rotulo(c, "CADA MAÑANA: SE CONTESTA", 540, 440, 66, AMA, OL, -3, k=k)
    return view(c, 540, 900, 1.0 + .08 * u_(T, t0, 5.5))

C1 = mk_carta("L07", [("Hola.", (0,), 470), ("Ya sé la M.", (1, 2, 3, 4), 630), ("¿Me enseñas", (5, 6), 790), ("la A?", (7, 9), 950)], 23); T_H1 = E("L07") + .05
@esc(S("L07") - .2, True)
def carta_uno(T, t0):
    c = _mesa(T, t0, 1.05); nota_base(c); tip = carta(c, C1, T, T_H1); dia(c, T, t0 + .1, 8)
    return view(c, 540, 800, 1.0 + .08 * u_(T, t0, 5))

# ---------------------------------------------------------------- 4 · por primera vez, él solo agarra el crayón
T_SOLO = WI("L08", 8) - .1
@esc(S("L08") - .2, True)
def el_solo(T, t0):
    c = _mesa(T, t0, 1.15); c = borroso(c, 4, 20); u = ease((T - T_SOLO) / .6) if T > T_SOLO else 0
    mateo(c, "concentra" if T > T_SOLO else "neutral", 360, 760, 1.25 + .05 * u_(T, t0, 4), T, blink=False)
    put(c, "crayola", 800, 1120 - 160 * u, .7, rot=-28 + 20 * u)
    if u > 0:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); hx, hy = 860 - 60 * u, 1180 - 160 * u + 400 * (1 - u)
        d.line((hx - 330, hy + 330, hx, hy), fill=OL, width=120); d.line((hx - 330, hy + 330, hx, hy), fill=BATA_, width=104); d.ellipse((hx - 84, hy - 78, hx + 84, hy + 78), fill=PIEL, outline=OL, width=8); c.alpha_composite(lay)
    k = pop(T, T_SOLO + .2, .22)
    if k > 0: rotulo(c, "ÉL SOLO", 760, 440, 120, VERDE_C, CREMA, -4, k=k); chispas(c, 800, 960, T, T_SOLO + .3, 6, 260, 73)
    return c

# ---------------------------------------------------------------- 5 · el truco: la A es una carpa con su puente
A_UP = _poli([(300, 1130), (540, 770)], 12, 301, 1.5); A_DN = _poli([(540, 770), (780, 1130)], 12, 302, 1.5); A_BR = _poli([(400, 985), (680, 985)], 10, 303, 1.5)
TA = [WI("L09", 6) - .06, WI("L09", 7) - .06, WI("L09", 11) - .1, E("L09") + .15]
def carpa(c, a):
    if a <= 0: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); al = int(255 * clamp(a))
    d.polygon([(300, 1130), (540, 770), (780, 1130)], fill=(255, 214, 150, al)); d.polygon([(470, 1130), (540, 990), (610, 1130)], fill=(232, 150, 90, al))
    d.line((540, 770, 540, 690), fill=OL + (al,), width=7); d.polygon([(540, 690), (620, 715), (540, 742)], fill=ROJO + (al,))
    c.alpha_composite(lay)
@esc(S("L09") - .2, True)
def la_carpa(T, t0):
    c = _mesa(T, t0, 1.05); hoja_blanca(c, T, t0); carpa(c, .55 * u_(T, WI("L09", 4) - .1, .4)); pts = []
    for i, P in enumerate((A_UP, A_DN)): pts += parcial(P, u_(T, TA[i], max(.3, (TA[i + 1] - TA[i]) * .7)))
    if len(pts) >= 2: crayon(c, pts, 34, VERDE)
    br = parcial(A_BR, u_(T, TA[2], .45))
    if len(br) >= 2: crayon(c, br, 34, ROJO)
    k = pop(T, WI("L09", 4) - .1, .22)
    if k > 0 and T < TA[0]: rotulo(c, "LA A ES UNA CARPA", 540, 440, 88, AZUL, CREMA, -3, k=k)
    for i, (txt, col) in enumerate((("SUBE " + SUB, VERDE_C), ("BAJA " + BAJ, AZULC), ("…Y SU PUENTE", ROJO))):
        if TA[i] <= T < TA[i + 1] or (i == 2 and T >= TA[2]): rotulo(c, txt, 320 if i < 2 else 540, 440, 100 if i < 2 else 92, col, CREMA, -3, f=DJ, k=pop(T, TA[i], .18))
    tip = (br[-1] if len(br) >= 1 and T >= TA[2] else (pts[-1] if pts else A_UP[0]))
    if T < TA[3] + .1: mano(c, tip, T, .9)
    return c

# ---------------------------------------------------------------- 6 · tres intentos… y la tercera va al buzón
def A_pts(x, y, w, h, seed, j=2, puente=True, tor=0):
    up = _poli([(x, y + h), (x + w / 2 + tor, y)], 8, seed, j); dn = _poli([(x + w / 2 + tor, y), (x + w + tor * .4, y + h)], 8, seed + 1, j)
    br = _poli([(x + w * .22, y + h * .62), (x + w * .8 + tor * .3, y + h * .62 + tor * .25)], 6, seed + 2, j) if puente else []
    return up + dn, br
A3 = [A_pts(175, 800, 190, 280, 311, 3, False), A_pts(445, 800, 190, 280, 321, 9, True, 46), A_pts(715, 800, 190, 280, 331, 2, True)]
T3 = [WI("L10", 0) - .05, WI("L10", 6) - .05, WI("L10", 9) - .05]; T_METE = WI("L10", 11) - .1
@esc(S("L10") - .2, True)
def tres_intentos(T, t0):
    c = _mesa(T, t0, 1.05); v = ease((T - T_METE) / .9) if T > T_METE else 0
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); hojita(lay, 110, 600, 970, 1250)
    for i, (ab, br) in enumerate(A3):
        p = parcial(ab, u_(T, T3[i], .7))
        if len(p) >= 2: crayon(lay, p, 26, VERDE)
        b = parcial(br, u_(T, T3[i] + .7, .3)) if br else []
        if len(b) >= 2: crayon(lay, b, 26, VERDE)
    if T >= T3[2] + 1.0: estrella(lay, 905, 760, 44 * pop(T, T3[2] + 1.0, .2))
    if v <= 0: c.alpha_composite(lay)
    else:
        caja(c, 760, 1150, .62 * ease((T - T_METE) / .3)); rx, ry = ranura_xy(760, 1150, .62)
        if v < 1: paste_rot(c, lay.crop((100, 590, 980, 1260)), 540 + (rx - 540) * v, 925 + (ry - 925) * v, 1 - .86 * v, -24 * v, 1.0)
        else: chispas(c, rx, ry - 40, T, T_METE + .9, 6, 240, 81)
    if v <= 0:
        for i, (txt, col, x) in enumerate((("SIN PUENTE", ROJO, 270), ("TORCIDA", MORA, 540), ("¡ESTA SÍ!", VERDE_C, 810))):
            k = pop(T, T3[i] + .75, .2)
            if k > 0: rotulo(c, txt, x, 1170, 50, col, CREMA, (-3, 2, -2)[i], k=k)
    k = pop(T, T_METE + .2, .22)
    if k > 0: rotulo(c, "AL BUZÓN", 400, 440, 110, VERDE_C, CREMA, -4, k=k)
    return c

# ---------------------------------------------------------------- 7 · así pasan tres días: tres cartas y ni una queja
T_D = [S("L11") - .05 + i * .55 for i in range(3)]; T_QJ = WI("L11", 6) - .1
@esc(S("L11") - .2, True)
def tres_dias(T, t0):
    c = _mesa(T, t0, 1.1); c = borroso(c, 5, 30)
    for i in range(3):
        k = pop(T, T_D[i], .25)
        if k > 0:
            sobre(c, (270, 810, 540)[i], (760, 760, 1050)[i], 1.0 * k, (-7, 6, -3)[i]); rotulo(c, f"DÍA {9 + i}", (270, 810, 540)[i], (640, 640, 930)[i], 60, AMA, OL, (-4, 4, -2)[i], k=k)
    k = pop(T, WI("L11", 4) - .1, .2)
    if k > 0 and T < T_QJ: rotulo(c, "3 DÍAS · 3 CARTAS", 540, 440, 88, AZUL, CREMA, -3, k=k)
    k = pop(T, T_QJ, .22)
    if k > 0:
        rotulo(c, "¡NO QUIERO!", 540, 440, 96, (228, 222, 206), (150, 144, 130), -3, k=k); u = u_(T, T_QJ + .25, .25)
        if u > 0: ImageDraw.Draw(c).line((250, 470, 250 + 580 * u, 410), fill=ROJO, width=22)
    return c

# ---------------------------------------------------------------- 8 · el jueves, la maestra te detiene a la salida
@esc(S("L12") - .2)
def la_maestra(T, t0):
    c = bg("bg_escuela", T, t0, 1.2, 1.3, 4, .5, .4); u = ease((T - t0) / .4); maestra(c, 540, 800 + 300 * (1 - u), 1.5, T, None)
    k = pop(T, WI("L12", 1) - .1, .2)
    if k > 0: rotulo(c, "JUEVES · A LA SALIDA", 540, 400, 72, CREMA, OL, -3, k=k)
    return c

T_DINO = WI("L13", 21) - .1
@esc(S("L13") - .2, True)
def dice_que(T, t0):
    c = bg("bg_escuela", T, t0, 1.45, 1.55, 6, .5, .38); c = borroso(c, 6, 30); maestra(c, 300, 900, 1.25, T, "L13")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); k = pop(T, t0 + .3, .25)
    if k > 0:
        d.rounded_rectangle((470, 330, 1040, 800), 70, fill=CREMA + (255,), outline=OL + (255,), width=8); d.polygon([(520, 780), (430, 900), (620, 790)], fill=CREMA + (255,)); d.line([(520, 786), (430, 900), (620, 794)], fill=OL + (255,), width=8)
        c.alpha_composite(lay)
        if T < T_DINO:
            t = Image.new("RGBA", (W, H), (0, 0, 0, 0)); mateo(t, "feliz", 600, 590, .4, T, blink=False); nino_sil(t, 930, 640, .5, 0, 0, (90, 96, 140), risa=False)
            box = (482, 342, 1028, 788); c.alpha_composite(t.crop(box), box[:2])
            ab, br = A_pts(720, 370, 110, 140, 341, 2, True); crayon(c, ab, 16, VERDE); crayon(c, br, 16, ROJO)
        else:
            kk = pop(T, T_DINO, .25); put(c, "dino", 760, 580, .42 * kk); 
            if kk > 0: tiza(c, "?", 950, 430, 110 * kk, AMA, 10, f=F_BAL, stroke=3, borde=True)
    return c

# ---------------------------------------------------------------- 9 · esa noche, una hoja en el buzón: M, A
MA_M = letraM(250, 800, 260, 300, 351, j=6); MA_A, MA_B = A_pts(590, 800, 240, 300, 352, 5, True, 14)
def hoja_MA(lay, u=1.0, cor=1.0):
    hojita(lay, 110, 600, 970, 1250); p = parcial(MA_M + [], u)
    crayon(lay, MA_M, 30, VERDE); crayon(lay, MA_A, 30, VERDE); crayon(lay, MA_B, 30, VERDE)
    if cor > 0: corazon(lay, 880, 700, 30 * cor)
@lru_cache(2)
def hoja_MA_img(cor=1):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); hoja_MA(lay, 1, cor); return lay.crop((100, 590, 980, 1260))
T_DOS = WI("L14", 8) - .1
@esc(S("L14") - .2, True)
def hoja_noche(T, t0):
    c = _mesa(T, t0, 1.05); caja(c, 520, 1030, 1.0); rx, ry = ranura_xy(520, 1030, 1.0); u = ease((T - WI("L14", 3) + .1) / .9) if T > WI("L14", 3) - .1 else 0
    c.alpha_composite(Image.new("RGBA", (W, H), NOCHE + (120,))); c.alpha_composite(luz_img(540, 900, 1000, 120))
    if u > 0: paste_rot(c, hoja_MA_img(1), rx + (540 - rx) * u, ry - 20 + (880 - ry) * u, .1 + .9 * u, 18 * (1 - u))
    k = pop(T, t0 + .1, .22)
    if k > 0 and T < T_DOS: tiza(c, "ESA NOCHE…", 540, 430, 100 * k, CREMA, -3, f=F_BAL, stroke=3, borde=True)
    k = pop(T, T_DOS, .22)
    if k > 0: rotulo(c, "DOS LETRAS JUNTAS", 540, 430, 80, AMA, OL, -3, k=k)
    return view(c, 540, 900, 1.0 + .1 * u_(T, t0, 6))

# ---------------------------------------------------------------- 10 · el golpe: «Mira, mami… pone mamá»
T_PONE = WI("L15", 6) - .1
@esc(S("L15") - .25, True)
def pone_mama(T, t0):
    c, tr = vista("bg_sala", 400, 900, 1.9); c = borroso(c, 9, 40); c.alpha_composite(Image.new("RGBA", (W, H), (255, 190, 90, 22))); z = 1.0 + .1 * u_(T, t0, 5)
    mateo(c, "feliz" if T >= T_PONE else "timido", 360, 780, 1.3 * z, T, "L15", blink=False)
    paste_rot(c, hoja_MA_img(1), 790, 960, .52 * z, 7 + 2 * math.sin(T * 3))
    k = pop(T, T_PONE + .15, .28)
    if k > 0: tiza(c, "«mamá»", 760, 610, 110 * k, CREMA, -4, stroke=2, borde=True); corazones(c, 760, 760, T, T_PONE + .2, 6, 91)
    return c

T_Q = WI("L16", 3) - .12
@esc(S("L16") - .15, True)
def solo_ma(T, t0):
    """Solo pone MA: las dos letras que faltan, en fantasma."""
    c = _mesa(T, t0, 1.05); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); hojita(lay, 60, 640, 1020, 1210); c.alpha_composite(lay); d = ImageDraw.Draw(c)
    for i, ch in enumerate("MAMÁ"):
        on = i < 2; d.text((190 + i * 235, 920), ch, font=font(F_HAND, 330), fill=VERDE if on else (206, 204, 196), anchor="mm", stroke_width=5 if on else 0, stroke_fill=VERDE)
    k = pop(T, WI("L16", 2) - .12, .22)
    if k > 0: rotulo(c, "SOLO PONE «MA»", 540, 440, 96, ROJO, CREMA, -3, k=k); lapiz_rojo(c, (70, 720, 520, 1130), u_(T, WI("L16", 2), .35), 14, 9)
    return c

# ---------------------------------------------------------------- 11 · ¿qué harías tú? (dilema moral: la verdad o la ilusión)
_ico8 = icono_tarjeta
def icono_tarjeta(d, ix, iy, k, icono):
    if icono == "aun_no":       # MA + dos huecos
        d.text((ix - 40 * k, iy - 10 * k), "MA", font=font(F_BAL, 130 * k), fill=CREMA, anchor="mm", stroke_width=max(2, int(5 * k)), stroke_fill=OL)
        for q in (60, 116): d.line((ix + q * k, iy + 40 * k, ix + (q + 40) * k, iy + 40 * k), fill=CREMA, width=max(4, int(12 * k)))
    elif icono == "cora":
        r = 62 * k; d.ellipse((ix - 2 * r, iy - 1.4 * r, ix, iy + .6 * r), fill=CREMA, outline=OL, width=max(3, int(8 * k))); d.ellipse((ix, iy - 1.4 * r, ix + 2 * r, iy + .6 * r), fill=CREMA, outline=OL, width=max(3, int(8 * k)))
        d.polygon([(ix - 1.86 * r, iy), (ix + 1.86 * r, iy), (ix, iy + 2 * r)], fill=CREMA); d.line([(ix - 1.86 * r, iy + .05 * r), (ix, iy + 2 * r), (ix + 1.86 * r, iy + .05 * r)], fill=OL, width=max(3, int(8 * k)), joint="curve")
    else: _ico8(d, ix, iy, k, icono)

@lru_cache(1)
def _mitades():
    A2, tr = vista("bg_sala", 300, 900, 1.6); A2 = borroso(A2, 6, 20); A2.alpha_composite(Image.new("RGBA", (W, H), AZUL + (70,)))
    B2, tr = vista("bg_sala", 700, 900, 1.6); B2 = borroso(B2, 6, 20); B2.alpha_composite(Image.new("RGBA", (W, H), ROJO + (50,)))
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon([(0, 0), (512, 0), (428, H), (0, H)], fill=255); return A2, B2, m
T_A, T_B, T_C = WI("L17", 0) - .05, WI("L17", 5) - .05, S("L18") - .05
@esc(T_Q)
def final(T, t0):
    """Pantalla partida: ¿le dices que aún no, o le dices que sí? Cada opción con su pro y su contra."""
    A2, B2, m = _mitades(); a = A2.copy(); b = B2.copy()
    mateo(a, "timido", 235, 1500, .9, T, blink=False); mateo(b, "feliz", 730 + 4 * math.sin(T * 3), 1500, .9, T, blink=False)
    if T < T_B: b.alpha_composite(Image.new("RGBA", (W, H), (10, 14, 40, int(150 * (1 - u_(T, T_B - .2, .2))))))
    ka = u_(T, T_B, .2) * (1 - u_(T, T_C - .2, .2))
    c = b; c.paste(a, (0, 0), m); d = ImageDraw.Draw(c); d.line((512, 0, 428, H), fill=CREMA, width=16)
    tarjeta(c, 247, 640, .7 * pop(T, T_A, .3), "AÚN NO", AZUL, "aun_no", 3, sub="le dices la verdad")
    tarjeta(c, 719, 640, .7 * pop(T, T_B, .3), "SÍ", ROJO, "cora", -3, sub="pone mamá")
    pro_contra(c, 243, 892, "aprende lo que falta", "le rompes la ilusión", pop(T, T_A + .35, .22), pop(T, T_A + .6, .22), 2)
    pro_contra(c, 718, 892, "se siente capaz", "se lo dirá otro niño", pop(T, T_B + .35, .22), pop(T, T_B + .6, .22), -2)
    if ka > 0: c.paste(Image.alpha_composite(c, Image.new("RGBA", (W, H), (10, 14, 40, int(150 * ka)))), (0, 0), m); d = ImageDraw.Draw(c); d.line((512, 0, 428, H), fill=CREMA, width=16)
    k = pop(T, T_Q + .05, .25)
    if k > 0: rotulo(c, "¿QUÉ HARÍAS TÚ?", 478, 345, 80, AMA, OL, -2, k=k)
    kv = pop(T, T_B + .1, .25)
    if kv > 0:
        r = 58 * kv; d = ImageDraw.Draw(c); d.ellipse((480 - r, 640 - r, 480 + r, 640 + r), fill=AMA, outline=OL, width=8); d.text((480, 638), "o", font=font(F_BAL, 84 * kv), fill=OL, anchor="mm")
    return c

DIA_T[:] = [(T_D[0], 22, "M"), (T_D[1], 21, "M"), (T_D[2], 20, "M"), (T_DOS, 20, "MA")]

SC.sort(key=lambda x: x[0])
SCENES = [(t, f) for t, f, s_ in SC]; SUAVES = {t for t, f, s_ in SC if s_}
IMPACTS = [.05, T_TIRA + .7, WI("L02", 4) - .1, T_SOLO + .2, T_METE + .9, T_PONE + .15]

def hblur(im, k):
    if k < 2: return im
    return im.resize((max(1, W // k), H), Image.BILINEAR).resize((W, H), Image.BILINEAR)

TW = .16
def frame(T):
    idx = max(i for i, (t, f) in enumerate(SCENES) if T >= t)
    t0, fn = SCENES[idx]; c = fn(T, t0)
    u = (T - t0) / TW
    if idx > 0 and u < 1 and t0 not in SUAVES:      # barrido rápido entre escenas (nunca fundido a negro)
        e = ease(u); pt, pf = SCENES[idx - 1]; prev = pf(T, pt); k = int(2 + 20 * math.sin(PI_ * u))
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
        print(len(SCENES), [(round(t, 2), f.__name__) for t, f in SCENES])
    elif cmd == "mid":
        for i, (t, f) in enumerate(SCENES):
            t1 = SCENES[i + 1][0] if i + 1 < len(SCENES) else TOTAL; frame(t + (t1 - t) * .72).save(os.path.join(TMP, f"m{i:02d}_{f.__name__}.jpg"), quality=80)
    elif cmd == "scenes":
        from multiprocessing import Pool
        ids = [int(x) for x in sys.argv[2:]] or list(range(len(SCENES)))
        with Pool(2) as pool: pool.starmap(render_scene, [(i, os.path.join(TMP, f"s{i:02d}.mp4")) for i in ids])




