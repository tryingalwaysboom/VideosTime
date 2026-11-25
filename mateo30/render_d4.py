"""Temporada "Mateo: 30 días para no repetir" · DÍA 4 — La M en el sofá (ganó PREMIO).
Mundo visual nuevo (pizarra verde, tiza amarilla, rojo de corrección), barra FALTAN X DÍAS + imanes M-A-T-E-O,
subtítulos palabra a palabra y cierre con dos tarjetas de una palabra.
Uso: python3 render_d1.py still 1 5 | scenes [i...] | info"""
import os, sys, math, json, subprocess, random
from functools import lru_cache
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["GUION"] = "guion_d4"; os.environ["VOZDIR"] = os.path.join(HERE, "voz_d4")
sys.path.insert(0, HERE)
import importlib.util
_spec = importlib.util.spec_from_file_location("R", os.path.join(HERE, "..", "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

R.LAY = os.path.join(HERE, "layers"); R.layer.cache_clear(); R.scaled.cache_clear()
TMP = os.path.join(HERE, "tmp_d4"); os.makedirs(TMP, exist_ok=True)
W, H, FPS = R.W, R.H, R.FPS
put, ease, clamp, back, font, mouth, bg = R.put, R.ease, R.clamp, R.back, R.font, R.mouth, R.bg
F_ANTON = R.F_ANTON
MF = os.path.join(HERE, "..", "mateo-pov", "fonts")
F_HAND = os.path.join(MF, "Caveat.ttf"); F_BAL = os.path.join(MF, "Baloo2-ExtraBold.ttf"); F_AND = os.path.join(MF, "Andika-Bold.ttf")
PI_ = math.pi
OL = (29, 22, 48); PIZ = (36, 82, 66); PIZ2 = (25, 60, 48); TIZA = (246, 244, 232); AMA = (255, 212, 84)
ROJO = (226, 72, 59); CREMA = (255, 253, 244); AZUL = (63, 127, 208); MADERA = (176, 122, 72)
DIAS_FALTAN = 27; LETRAS_ON = ""          # Día 1: ninguna letra dominada

# ---------------------------------------------------------------- tiempos
R.GAP.clear()
BASE = {"L02": .25, "L03": .25, "L04": .55, "L05": .3, "L06": .3, "L07": .7, "L08": .5, "L09": .4, "L10": .35, "L11": .4, "L12": .5,
        "L13": .4, "L14": .5, "L15": .6, "L16": .5, "L17": .3}
FLEX = ("L04", "L07", "L08", "L09", "L11", "L12", "L13", "L15", "L16")      # pausas que absorben el ajuste para clavar la duración
COLA = .35
R.GAP.update(BASE); _tl, _ = R.timeline(); _fin = _tl["L17"][1] - .1 + COLA
OBJ = float(max(80, math.ceil(_fin)))                                        # segundos enteros, mínimo 80
_extra = (OBJ - COLA) - (_tl["L17"][1] - .1)
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
T_FINAL = S("L16") - .25
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

# ---------------------------------------------------------------- 1 · gancho: una sola idea y pregunta abierta
@esc(0)
def gancho(T, t0):
    """Fotograma 0: el sofá nuevo rayado con marcador y Mateo al lado, con el marcador en la mano."""
    z = 1.5 + .12 * ease(T / .5) + .05 * u_(T, 0, 2); c, tr = sofa(480, 930, z)
    hx = 236 + 5 * math.sin(T * 17) * (1 - u_(T, 0, .6)); mateo(c, "feliz_tira", hx, 1130, .92, T, blink=False)
    brazo_tira(c, hx + 224 * .92, 1130 + 372 * .92, -38 + 3 * math.sin(T * 6), -80 + 4 * math.sin(T * 6), .92, "marcador")
    p = 1 + .04 * math.exp(-T * 6) * math.cos(T * 22)
    rotulo(c, "RAYÓ", 380, 290, 132, CREMA, OL, -4, k=p); rotulo(c, "EL SOFÁ NUEVO", 530, 450, 100, ROJO, CREMA, -4, k=p)
    return c

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

@esc(WI("L01", 4) - .1)
def llego(T, t0):
    u = ease((T - t0) / .4); c = puerta(T, 540, 880, 1.18 + .1 * u_(T, t0, 2), abierta=.35 + .65 * u, papa=clamp((T - t0 - .12) / .3))
    k = pop(T, WI("L01", 5) - .05, .2)
    if k > 0: rotulo(c, "…Y PAPÁ YA LLEGÓ", 500, 300, 84, ROJO, CREMA, -4, k=k)
    return c

# ---------------------------------------------------------------- 2 · el objetivo, en una frase
@esc(S("L02") - .15)
def faltan(T, t0):
    c = pizarra(); mateo(c, "timido", 270 - 420 * (1 - ease((T - t0) / .3)), 720, 1.05 + .03 * u_(T, t0, 2.5), T)
    k = pop(T, WI("L02", 1) - .08, .25)
    if k > 0: tiza(c, "27", 770, 480, 330 * k * (1 + .03 * math.sin((T - t0) * 9)), AMA, 0, f=F_ANTON)
    k = pop(T, WI("L02", 2) - .05, .22)
    if k > 0: tiza(c, "DÍAS", 770, 700, 130 * k, TIZA, -2, f=F_BAL)
    k = pop(T, WI("L02", 3) - .05, .22)
    if k > 0: tiza(c, "para escribir", 770, 830, 72 * k, TIZA, -2, f=F_BAL)
    k = pop(T, WI("L02", 5) - .05, .22)
    if k > 0: tiza(c, "SU NOMBRE", 750, 925, 84 * k, AMA, -2, f=F_BAL)
    return c

@esc(WI("L02", 7) - .1)
def o_repite(T, t0):
    c = pizarra(); tr_ = WI("L02", 8) - .05
    mateo(c, "neutral" if T < tr_ else "susto", 270 + (9 * math.sin(T * 40) * math.exp(-(T - tr_) * 5) if T >= tr_ else 0), 720, 1.1 + (.08 * ease((T - tr_) / .2) if T >= tr_ else 0), T, blink=False)
    tiza(c, "…o", 760, 470, 150 * pop(T, t0 + .03, .22), TIZA, -3, f=F_BAL)
    k2 = pop(T, tr_, .2)
    if k2 > 0: rotulo(c, "REPITE", 750, 670, 128, ROJO, CREMA, -5, k=k2)
    k3 = pop(T, WI("L02", 9) - .05, .2)
    if k3 > 0: tiza(c, "EL CURSO", 750, 850, 96 * k3, TIZA, -3, f=F_BAL)
    return c

# ---------------------------------------------------------------- 3 · cómo llegó ahí: ustedes eligieron PREMIO
@esc(S("L03") - .1)
def eligieron(T, t0):
    c = pizarra(); mateo(c, "feliz", 270 - 420 * (1 - ease((T - t0) / .3)), 720, 1.08 + .03 * u_(T, t0, 2.5), T, blink=False)
    k = pop(T, t0 + .05, .22); tiza(c, "USTEDES", 750, 470, 100 * k, TIZA, -2, f=F_BAL)
    k = pop(T, WI("L03", 2) - .05, .22)
    if k > 0: tiza(c, "ELIGIERON:", 750, 590, 100 * k, AMA, -2, f=F_BAL)
    k = pop(T, WI("L03", 3) - .05, .2)
    if k > 0: rotulo(c, "PREMIO", 750, 800, 128, NAR, CREMA, -5, k=k); dulce_ico(c, 760, 1010, .62 * k)
    return c

NCOM = len([f for f in os.listdir(os.path.join(HERE, "coment_d4")) if f.endswith(".jpg")])
def _com_y():
    ys, y = [], 400
    for i in range(NCOM):
        h = _coment(i + 1).height; ys.append(y + h / 2); y += h * (.62 if NCOM > 4 else 1.06)
    k = min(1.0, (1180 - 400) / (y + _coment(NCOM).height * .38 - 400)); return [400 + (v - 400) * k for v in ys]
COM_Y = _com_y()
@esc(WI("L03", 4) - .1)
def comentarios(T, t0):
    """Comentarios reales de quienes votaron PREMIO y el sello."""
    c = pizarra(); tiza(c, "USTEDES ELIGIERON", 470, 338, 74, AMA, -2, f=F_BAL)
    for i in range(NCOM):
        ti = t0 + .04 + .9 * i / NCOM; k = pop(T, ti, .18)
        if k <= 0: continue
        im = _coment(i + 1); cx = 470 + (22 if i % 2 else -22); r = (-2.5, 2, -1.5, 2.5, -2, 1.5)[i]; cy = COM_Y[i] + 40 * (1 - ease((T - ti) / .18))
        sombra(c, (cx - im.width / 2, cy - im.height / 2, cx + im.width / 2, cy + im.height / 2), 26, 120, 14); paste_rot(c, im, cx, cy, k, r)
    ks = pop(T, t0 + 1.0, .2)
    if ks > 0: rotulo(c, "✔ GANÓ: PREMIO", 470, 1246, 58, NAR, CREMA, -3, f=DJ, k=ks)
    return c

# tres M rápidas sobre la fila punteada de la hoja real (la tercera, al revés: el error escondido)
FS = [_poli([(208, 628), (213, 556), (240, 612), (262, 560), (271, 633)], 8, 51, 2.4), _poli([(298, 621), (307, 551), (326, 597), (353, 566), (350, 634)], 8, 52, 2.6),
      _poli([(388, 560), (402, 629), (420, 581), (437, 631), (451, 556)], 8, 53, 2.4)]
T_F0 = WI("L04", 3) - .1
def _hoja_rapida(c, T, s=4.4, cx=470, cy=900, hasta=None):
    tr, sc = pagM(c, s, 330, 592, cx, cy); tip = None
    for i, F in enumerate(FS):
        u = 1 if hasta is None else u_(T, T_F0 + i * .4, .34); pts = parcial(F, u); cray(c, tr, sc, pts)
        if pts and u < 1: tip = tr(pts[-1])
    return tr, sc, tip

@esc(S("L04") - .25)
def rapido(T, t0):
    c = _mesa(T, t0, 1.05); tr, sc, tip = _hoja_rapida(c, T, hasta=True)
    put(c, "tarro", 800, 500, .62 + .02 * math.sin(T * 7), rot=4)
    if tip is None: tip = tr(FS[0][0]) if T < T_F0 else tr(FS[2][-1])
    if T_F0 <= T < T_F0 + 1.2:
        d = ImageDraw.Draw(c)
        for i in range(3): d.line((tip[0] + 120 + i * 46, tip[1] - 150 + i * 30, tip[0] + 260 + i * 46, tip[1] - 200 + i * 30), fill=TIZA, width=9)
    mano(c, tip, T, .8); return c

@esc(WI("L04", 5) - .1)
def mal(T, t0):
    c = _mesa(T, t0, 1.1); tr, sc, _ = _hoja_rapida(c, T, 4.8, 500, 900)
    for i, F in enumerate(FS):
        k = pop(T, WI("L04", 7) - .05 + i * .16, .2)
        if k > 0: a = tr(F[len(F) // 2]); tiza(c, "✗", a[0], a[1] - 150, 120 * k, ROJO, 6, f=DJ, stroke=3, borde=True)
    return view(c, 520, 880, 1 + .08 * u_(T, t0, 2))

@esc(S("L05") - .2)
def mi_dulce(T, t0):
    c = bg("bg_cocina", T, t0, 1.3, 1.36, 3, .5, .45); hx, hy, sc = 330, 660, 1.2
    mateo(c, "feliz_tira", hx, hy, sc, T, "L05", blink=False)
    u = ease((T - t0) / .25); x, y = brazo_tira(c, hx + 224 * sc, hy + 372 * sc, 75 - 35 * u, 10 - 80 * u + 3 * math.sin(T * 9), sc, False)
    k = pop(T, WI("L05", 3) - .05, .2)
    if k > 0: dulce_ico(c, x + 10, y - 170 - 10 * math.sin(T * 8), .6 * k); tiza(c, "?", x + 150, y - 250, 150 * k, AMA, 8, f=F_BAL, stroke=3, borde=True)
    return c

@esc(S("L06") - .2)
def asi_no(T, t0):
    c = bg("bg_cocina", T, t0, 1.36, 1.4, 3, .5, .45); tn = WI("L06", 1) - .05
    mateo(c, "feliz" if T < tn else "triste", 330, 660, 1.2 + (.05 * ease((T - tn) / .2) if T >= tn else 0), T, blink=False)
    dulce_ico(c, 760, 560, .7, tachado=u_(T, tn, .25))
    k = pop(T, tn, .2)
    if k > 0: rotulo(c, "ASÍ NO", 730, 800, 110, ROJO, CREMA, -5, k=k)
    return c

@esc(WI("L06", 2) - .1)
def en_lo_alto(T, t0):
    """Los dulces suben a lo más alto del refrigerador; Mateo los mira desde abajo."""
    u = ease((T - t0 - .1) / .7); c, tr = vista("bg_cocina", 760, 950 - 430 * u, 1.3)
    x, y = tr((330 + 510 * u, 930 - 590 * u - 140 * math.sin(PI_ * u))); put(c, "tarro", x, y, .66, rot=-10 * math.sin(PI_ * u))
    mateo(c, "triste", 330, 1380 + 430 * u * 1.3 * .35, 1.0, T, blink=False)
    k = pop(T, WI("L06", 8) - .05, .2)
    if k > 0: tiza(c, "↑", 330, 560, 190 * k, TIZA, 0, f=DJ, stroke=3, borde=True)
    return c

@esc(WI("L06", 9) - .1)
def se_fue(T, t0):
    c = bg("bg_cocina", T, t0, 1.3, 1.34, 3, .5, .45); u = ease((T - t0 - .15) / 1.1)
    mateo(c, "triste", 540 - 980 * u, 700 + 10 * abs(math.sin((T - t0) * 9)), 1.25, T, blink=False)
    return c

@esc(S("L07") - .25)
def silencio(T, t0):
    """La hoja y la crayola, abandonadas."""
    c = _mesa(T, t0, 1.0); _hoja_rapida(c, T, 3.6, 500, 900); put(c, "crayola", 760, 1250, .6, rot=24); oscurecer(c, (10, 14, 40), 70)
    return view(c, 540, 900, 1.12 - .08 * u_(T, t0, 1.6))

@esc(WI("L07", 1) - .1)
def silencio2(T, t0):
    c = bg("bg_cuarto", T, t0, 1.2, 1.3, 2.5, .5, .5); oscurecer(c, (10, 14, 40), 60)
    k = pop(T, t0 + .08, .25)
    if k > 0: tiza(c, "¿MATEO…?", 500, 620, 130 * k, TIZA, -4, f=F_BAL, stroke=3, borde=True)
    return c

# ---------------------------------------------------------------- 4 · la sala
T_REV = WI("L08", 6) - .05
@esc(S("L08") - .25)
def sala(T, t0):
    """La sala: Mateo, de pie delante del sofá, tapa algo."""
    z = 1.12 + .14 * u_(T, t0, 2.2); c, tr = sofa(540, 960, z); x, y = tr((540, 905))
    mateo(c, "timido", x, y + 60, 1.02 * z, T, blink=False)
    return c

@esc(WI("L08", 4) - .1)
def ahi_estaba(T, t0):
    z = 1.26 + .1 * u_(T, t0, 1.6); c, tr = sofa(470, 960, z); u = ease((T - T_REV + .12) / .3); x, y = tr((540 - 430 * u, 905))
    mateo(c, "susto" if u > .2 else "timido", x, y + 60 + 150 * u, 1.02 * z, T, blink=False)
    return c

@esc(WI("L08", 7) - .1)
def nuevo(T, t0):
    """La etiqueta de NUEVO, todavía colgando."""
    c, tr = sofa(900, 1090, 2.0 + .25 * u_(T, t0, 1.5)); x, y = tr((1000, 1150))
    k = pop(T, WI("L08", 10) - .08, .2)
    if k > 0: lapiz_rojo(c, (x - 190, y - 130, x + 190, y + 130), u_(T, WI("L08", 10) - .08, .3), 13, 9)
    return c

@esc(WI("L08", 11) - .1)
def permanente(T, t0):
    c, tr = sofa(540, 930, 1.9); c = borroso(c, 12, 110); k = pop(T, t0 + .04, .25)
    put(c, "marcador", 520, 860 + 10 * math.sin((T - t0) * 5), 1.45 * k, rot=18 - 6 * u_(T, t0, 1.6))
    return c

@esc(S("L09") - .2)
def mirala(T, t0):
    c, tr = sofa(540, 930, 1.55 + .3 * u_(T, t0, 1.8)); return c

T_SB = [WI("L09", i) - .04 for i in (3, 4, 5, 6)] + [WI("L09", 7) - .15]
@esc(T_SB[0] - .12)
def sube_baja(T, t0):
    """Así la hizo: cada trazo cae con su palabra (sube, baja, sube, baja)."""
    z = 2.0; c, tr = vista("bg_sala", 600, 915, z); pts = []
    for i in range(4):
        u = u_(T, T_SB[i], max(.2, (T_SB[i + 1] - T_SB[i]) * .8)); pts += parcial(MS[i], u)
    tip = tr(pts[-1]) if pts else tr(MS[0][0])
    if pts: trazo(c, [tr(p) for p in pts], 26 * z)
    mano(c, tip, T, .95, "mano_marcador"); return c

@esc(WI("L09", 7) - .1)
def lenta(T, t0):
    c, tr = vista("bg_sala", 300, 900, 2.2); c = borroso(c, 10, 60); mateo(c, "concentra", 400, 760, 1.35 + .04 * u_(T, t0, 2), T, blink=False)
    k = pop(T, t0 + .06, .22)
    if k > 0: tiza(c, "LENTA", 770, 420, 110 * k, TIZA, -4, f=F_BAL, stroke=3, borde=True)
    k = pop(T, WI("L09", 8) - .05, .22)
    if k > 0: tiza(c, "DERECHITA", 720, 560, 104 * k, AMA, -4, f=F_BAL, stroke=3, borde=True)
    return c

T_PERF = WI("L09", 12) - .05
@esc(WI("L09", 9) - .1)
def perfecta(T, t0):
    """La recompensa: su primera M perfecta."""
    z = 1.5 + .12 * u_(T, t0, 2); c, tr = sofa(540, 930, z); x, y = tr((540, 915))
    if T >= T_PERF: chispas(c, x, y, T, T_PERF, 9, 420, 5)
    k = pop(T, T_PERF, .22)
    if k > 0: rotulo(c, "✔ PERFECTA", 520, y - 350, 96, VERDE_C, CREMA, -4, f=DJ, k=k)
    return c

@esc(S("L10") - .2)
def mira_mama(T, t0):
    z = 1.6 + .05 * u_(T, t0, 2); c, tr = sofa(480, 930, z); hx = 215
    mateo(c, "feliz_tira", hx, 1130 - 14 * abs(math.sin((T - t0) * 8)), .92, T, "L10", blink=False)
    brazo_tira(c, hx + 224 * .92, 1130 + 372 * .92, -30 + 4 * math.sin(T * 9), -42 + 5 * math.sin(T * 9), .92, False)
    return c

@esc(WI("L10", 2) - .08, True)
def sin_dulce(T, t0):
    c, tr = vista("bg_sala", 300, 900, 2.2); c = borroso(c, 10, 40); mateo(c, "feliz", 430, 700, 1.45 + .05 * u_(T, t0, 1.5), T, "L10", blink=False)
    k = pop(T, WI("L10", 5) - .05, .2)
    if k > 0: dulce_ico(c, 820, 470, .62 * k, tachado=u_(T, WI("L10", 5) + .05, .25))
    return c

@esc(S("L11") - .2)
def reir_llorar(T, t0):
    c, tr = sofa(540, 960, 1.4 + .06 * u_(T, t0, 2))
    k = pop(T, WI("L11", 3) - .05, .22)
    if k > 0: tiza(c, "¿REÍR?", 300, 420, 120 * k, AMA, -6, f=F_BAL, stroke=3, borde=True)
    k = pop(T, WI("L11", 5) - .05, .22)
    if k > 0: tiza(c, "¿LLORAR?", 690, 560, 120 * k, TIZA, 5, f=F_BAL, stroke=3, borde=True)
    return c

HJ = (322, 720, 762, 1090)      # la hoja sobre la M (coordenadas del fondo)
def _hoja_sofa(c, tr, dy=0, a=205):
    p0, p1 = tr((HJ[0], HJ[1] + dy)), tr((HJ[2], HJ[3] + dy)); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rectangle((p0[0], p0[1], p1[0], p1[1]), fill=CREMA + (a,), outline=(200, 190, 170, 255), width=6); sombra(c, (p0[0], p0[1], p1[0], p1[1]), 4, 60, 10); c.alpha_composite(lay)

T_CAL = WI("L11", 10) - .05
@esc(WI("L11", 6) - .1)
def hoja_encima(T, t0):
    z = 1.9; c, tr = sofa(540, 915, z); u = ease((T - t0 - .1) / .45); _hoja_sofa(c, tr, -560 * (1 - u))
    return c

@esc(T_CAL - .05, True)
def calcan(T, t0):
    """La calcan juntos: la crayola verde sigue la M que se ve debajo de la hoja."""
    z = 1.9 + .12 * u_(T, t0, 2); c, tr = sofa(560, 915, z); _hoja_sofa(c, tr)
    pts = parcial(MS_ALL, u_(T, T_CAL + .1, 1.5))
    if pts: crayon(c, [tr(p) for p in pts], 17 * z, VERDE)
    mano(c, tr(pts[-1]) if pts else tr(MS_ALL[0]), T, .9); return c

@lru_cache(1)
def hoja_calco():
    w, h = (HJ[2] - HJ[0]) * 2, (HJ[3] - HJ[1]) * 2; im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ox, oy = (W - w) / 2, (H - h) / 2; d.rectangle((ox, oy, ox + w, oy + h), fill=CREMA + (255,), outline=(200, 190, 170, 255), width=8)
    crayon(im, [(ox + (x - HJ[0]) * 2, oy + (y - HJ[1]) * 2) for x, y in MS_ALL], 34, VERDE); return im.crop((int(ox) - 6, int(oy) - 6, int(ox + w) + 6, int(oy + h) + 6))

@esc(WI("L11", 14) - .1)
def guardarla(T, t0):
    c, tr = sofa(540, 930, 1.5); c = borroso(c, 10, 70); k = pop(T, t0 + .03, .28); im = hoja_calco()
    sombra(c, (500 - im.width * .45, 860 - im.height * .45, 500 + im.width * .45, 860 + im.height * .45), 8, 120, 22)
    paste_rot(c, im, 500, 860 - 20 * u_(T, t0, 1.5), .9 * k, -5 + 2 * math.sin((T - t0) * 3)); chispas(c, 500, 860, T, t0 + .2, 6, 430, 8)
    return c

# ---------------------------------------------------------------- 5 · el giro: papá
@esc(S("L12") - .2)
def justo_ahi(T, t0):
    """La puerta, todavía cerrada."""
    c = puerta(T, 540, 880, 1.2 + .12 * u_(T, t0, 1.5), abierta=0.0); return c

@esc(WI("L12", 3) - .1)
def se_abre(T, t0):
    u = ease((T - t0 - .05) / .5); c = puerta(T, 540, 880, 1.32 + .06 * u_(T, t0, 1.5), abierta=u, papa=clamp((T - t0 - .3) / .3)); return c

@esc(S("L13") - .2)
def papa_sofa(T, t0):
    """Papá mira el sofá: su sombra cruza la M."""
    z = 1.5 + .08 * u_(T, t0, 2); c, tr = sofa(540, 930, z); u = ease((T - t0) / .7)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); x = W + 200 - 900 * u
    ImageDraw.Draw(lay).polygon([(x, 0), (W + 400, 0), (W + 400, H), (x - 380, H)], fill=(20, 16, 40, 125)); c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(16)))
    return c

@esc(WI("L13", 4) - .1)
def papa_mateo(T, t0):
    c, tr = vista("bg_sala", 300, 900, 2.0); c = borroso(c, 8, 50); mateo(c, "susto", 520, 720, 1.4 + .05 * u_(T, t0, 1.5), T, blink=False)
    u = ease((T - t0 - .1) / .5); put(c, "marcador", 800, 1050 + 500 * u * u, .7, rot=-40 - 200 * u)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).polygon([(W - 520, 0), (W + 200, 0), (W + 200, H), (W - 880, H)], fill=(20, 16, 40, 110)); c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(16)))
    return c

@esc(WI("L13", 7) - .1)
def no_dice_nada(T, t0):
    c = puerta(T, 540, 760, 1.75 + .15 * u_(T, t0, 2), abierta=1.0, papa=1.0, px=540)
    k = pop(T, WI("L13", 10) - .05, .25)
    if k > 0: tiza(c, "…", 250, 430, 200 * k, CREMA, 0, f=F_BAL, stroke=3, borde=True)
    return c

@esc(S("L14") - .2)
def enojado(T, t0):
    c, tr = vista("bg_sala", 300, 900, 2.2); c = borroso(c, 10, 60); mateo(c, "timido", 500, 700, 1.4 + .06 * u_(T, t0, 2), T, "L14", blink=False)
    return c

# ---------------------------------------------------------------- 6 · la escuela y el sobre
@esc(S("L15") - .4)
def mientras(T, t0):
    c = pizarra(); tiza(c, "MIENTRAS", 500, 780, 190 * pop(T, t0 + .05, .25), AMA, -4, f=F_BAL)
    if T >= t0 + .22: tiza(c, "TANTO…", 500, 990, 190 * pop(T, t0 + .22, .25), TIZA, -4, f=F_BAL)
    return c

@esc(WI("L15", 2) - .05)
def escuela(T, t0): return bg("bg_escuela", T, t0, 1.05, 1.3, 2.2, .5, .45)

@esc(WI("L15", 4) - .1)
def tacha(T, t0):
    c = pizarra(); d = ImageDraw.Draw(c); x0, y0, cw, ch_ = 70, 440, 136, 136
    sombra(c, (x0 - 26, y0 - 110, x0 + 6 * cw + 26, y0 + 5 * ch_ + 26), 18, 110, 14)
    d.rounded_rectangle((x0 - 26, y0 - 110, x0 + 6 * cw + 26, y0 + 5 * ch_ + 26), 18, fill=CREMA, outline=OL, width=8)
    d.rounded_rectangle((x0 - 26, y0 - 110, x0 + 6 * cw + 26, y0 - 14), 18, fill=ROJO, outline=OL, width=8); d.text((x0 + 3 * cw, y0 - 62), "30 DÍAS · MATEO", font=font(F_BAL, 58), fill=CREMA, anchor="mm")
    for i in range(30):
        x, y = x0 + (i % 6) * cw, y0 + (i // 6) * ch_; d.rectangle((x + 6, y + 6, x + cw - 6, y + ch_ - 6), outline=(190, 186, 170), width=4)
        d.text((x + cw / 2, y + ch_ / 2), str(i + 1), font=font(F_ANTON, 58), fill=OL if i > 2 else (150, 150, 160), anchor="mm")
    tx = WI("L15", 4) - .02
    for n in range(3):
        a = (x0 + n * cw + 18, y0 + 18); b = (x0 + (n + 1) * cw - 18, y0 + ch_ - 18)
        for j, (p, q) in enumerate(((a, b), ((b[0], a[1]), (a[0], b[1])))):
            u = 1 if n < 2 else u_(T, tx + j * .16, .14)
            if u > 0: d.line((p[0], p[1], p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u), fill=ROJO, width=18)
    return view(c, 480, 800, 1 + .05 * u_(T, t0, 2.5))

@esc(WI("L15", 8) - .1)
def sobre(T, t0):
    c = bg("bg_cocina", T, t0, 1.4, 1.5, 3, .7, .3); oscurecer(c, (10, 14, 40), 120); z = .95 + .1 * u_(T, t0, 2.5)
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((0, 420, 960, 1300), fill=(255, 226, 150, 110)); c.alpha_composite(g.filter(ImageFilter.GaussianBlur(70)))
    sombra(c, (480 - 410 * z, 860 - 270 * z, 480 + 410 * z, 860 + 270 * z), 20, 130, 20); paste_rot(c, sobre_img(), 480, 860, z, -3 + 1.5 * math.sin((T - t0) * 3))
    k = pop(T, WI("L15", 12) - .05, .22)
    if k > 0: rotulo(c, "CERRADO", 640, 1140, 78, ROJO, CREMA, -8, k=k)
    return c

# ---------------------------------------------------------------- 7 · el dilema
@lru_cache(1)
def _mitades():
    A2 = bg("bg_cuarto", 0, 0, 1.3, 1.3, 1, .5, .5); A2.alpha_composite(Image.new("RGBA", (W, H), ROJO + (70,)))
    B2, _ = sofa(540, 1000, 1.25); B2.alpha_composite(Image.new("RGBA", (W, H), VERDE_C + (60,)))
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon([(0, 0), (512, 0), (428, H), (0, H)], fill=255); return A2, B2, m
T_A, T_B, T_C = WI("L16", 0) - .05, WI("L16", 6) - .05, S("L17") - .05
T_TU = WI("L17", 4) - .08
@esc(S("L16") - .25)
def final(T, t0):
    """Pantalla partida: cada opción con su consecuencia. Sin "mañana": las tarjetas dicen "¿EN EL DÍA 5?"."""
    A2, B2, m = _mitades(); a = A2.copy(); b = B2.copy()
    mateo(a, "triste", 245, 1490, .92, T, blink=False); mateo(b, "feliz", 720 + 4 * math.sin(T * 3), 1490, .92, T, blink=False)
    if T < T_B: b.alpha_composite(Image.new("RGBA", (W, H), (10, 14, 40, int(150 * (1 - u_(T, T_B - .2, .2))))))
    ka = u_(T, T_B, .2) * (1 - u_(T, T_C - .2, .2))      # mientras se habla de la B, la A queda en oscuro
    c = b; c.paste(a, (0, 0), m); d = ImageDraw.Draw(c); d.line((512, 0, 428, H), fill=CREMA, width=16)
    pa = 1 + .07 * math.sin((T - T_C) * 10) if WI("L17", 1) - .08 <= T < WI("L17", 2) else 1; pb = 1 + .07 * math.sin((T - T_C) * 10) if WI("L17", 3) - .08 <= T < T_TU else 1
    tarjeta(c, 247, 660, .74 * pop(T, T_A, .3) * pa, "CASTIGO", ROJO, "castigo", 3, sub="¿EN EL DÍA 5?")
    tarjeta(c, 719, 660, .74 * pop(T, T_B, .3) * pb, "CELEBRAR", VERDE_C, "celebrar", -3, sub="¿EN EL DÍA 5?")
    dos_lineas(c, 243, 950, "por rayar", "el sofá", 2, pop(T, WI("L16", 2) - .05, .25)); dos_lineas(c, 715, 950, "su primera", "M perfecta", -2, pop(T, WI("L16", 8) - .05, .25))
    if ka > 0: c.paste(Image.alpha_composite(c, Image.new("RGBA", (W, H), (10, 14, 40, int(150 * ka)))), (0, 0), m); d = ImageDraw.Draw(c); d.line((512, 0, 428, H), fill=CREMA, width=16)
    kv = pop(T, T_B + .1, .25)
    if kv > 0:
        r = 65 * kv; d = ImageDraw.Draw(c); d.ellipse((483 - r, 659 - r, 483 + r, 659 + r), fill=AMA, outline=OL, width=8); d.text((483, 657), "vs", font=font(F_BAL, 78 * kv), fill=OL, anchor="mm")
    kt = pop(T, T_TU, .25)
    if kt > 0: paste_rot(c, _coment(min(3, NCOM), 540), 478, 356 - 30 * (1 - ease((T - T_TU) / .25)), kt, -3)     # "Tu comentario puede salir…": asoma un comentario real
    return c

SC.sort(key=lambda x: x[0])
SCENES = [(t, f) for t, f, s_ in SC]; SUAVES = {t for t, f, s_ in SC if s_}
IMPACTS = [.05, WI("L02", 8), T_REV, WI("L09", 12), WI("L12", 6), WI("L13", 10)]

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
