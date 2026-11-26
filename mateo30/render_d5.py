"""Temporada "Mateo: 30 días para no repetir" · DÍA 5 — Solo sabe una letra (ganó CASTIGO; fórmula de los virales: vuelve Rex).
Mundo visual nuevo (pizarra verde, tiza amarilla, rojo de corrección), barra FALTAN X DÍAS + imanes M-A-T-E-O,
subtítulos palabra a palabra y cierre con dos tarjetas de una palabra.
Uso: python3 render_d1.py still 1 5 | scenes [i...] | info"""
import os, sys, math, json, subprocess, random
from functools import lru_cache
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["GUION"] = "guion_d5"; os.environ["VOZDIR"] = os.path.join(HERE, "voz_d5")
sys.path.insert(0, HERE)
import importlib.util
_spec = importlib.util.spec_from_file_location("R", os.path.join(HERE, "..", "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

R.LAY = os.path.join(HERE, "layers"); R.layer.cache_clear(); R.scaled.cache_clear()
TMP = os.path.join(HERE, "tmp_d5"); os.makedirs(TMP, exist_ok=True)
W, H, FPS = R.W, R.H, R.FPS
put, ease, clamp, back, font, mouth, bg = R.put, R.ease, R.clamp, R.back, R.font, R.mouth, R.bg
F_ANTON = R.F_ANTON
MF = os.path.join(HERE, "..", "mateo-pov", "fonts")
F_HAND = os.path.join(MF, "Caveat.ttf"); F_BAL = os.path.join(MF, "Baloo2-ExtraBold.ttf"); F_AND = os.path.join(MF, "Andika-Bold.ttf")
PI_ = math.pi
OL = (29, 22, 48); PIZ = (36, 82, 66); PIZ2 = (25, 60, 48); TIZA = (246, 244, 232); AMA = (255, 212, 84)
ROJO = (226, 72, 59); CREMA = (255, 253, 244); AZUL = (63, 127, 208); MADERA = (176, 122, 72)
DIAS_FALTAN = 26; LETRAS_ON = "M"          # Día 1: ninguna letra dominada

# ---------------------------------------------------------------- tiempos
R.GAP.clear()
BASE = {"L02": .3, "L03": .3, "L04": .45, "L05": .5, "L06": .25, "L06B": .12, "L07": .35, "L08": .55, "L09": .4, "L10": .5, "L11": .3, "L12": .6,
        "L13": .45, "L14": .45, "L15": .6, "L16": .45, "L17": .6, "L18": .4, "L19": .3}
FLEX = ("L05", "L08", "L10", "L12", "L14", "L15", "L17")      # pausas que absorben el ajuste para clavar la duración
COLA = .35
R.GAP.update(BASE); _tl, _ = R.timeline(); _fin = _tl["L19"][1] - .1 + COLA
OBJ = float(math.ceil(_fin))                                                 # segundos enteros, sin relleno
_extra = (OBJ - COLA) - (_tl["L19"][1] - .1)
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
T_FINAL = S("L18") - .25
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

# ---------------------------------------------------------------- 1 · gancho (una idea): llegó llorando… con una hoja que solo tiene una letra
@esc(0)
def gancho(T, t0):
    z = 1.3 + .1 * ease(T / .5) + .05 * u_(T, 0, 2.6); c = puerta(T, 620, 900, z, abierta=1.0)
    hx = 330 + 5 * math.sin(T * 17) * (1 - u_(T, 0, .6)); mateo(c, "llora", hx, 760 + 5 * math.sin(T * 13), 1.18, T, blink=False); lagrimas(c, hx, 840, T, 3, 1.1)
    hoja_en(c, 770, 1080 + 8 * math.sin(T * 6), .56, -9 + 2 * math.sin(T * 5))
    p = 1 + .04 * math.exp(-T * 6) * math.cos(T * 22)
    rotulo(c, "LLEGÓ LLORANDO", 540, 300, 104, ROJO, CREMA, -3, k=p); rotulo(c, "DE LA ESCUELA", 560, 432, 84, CREMA, OL, -3, k=p)
    return c

T_UNA = WI("L01", 13) - .05
@esc(WI("L01", 7) - .1)
def una_letra(T, t0):
    c = _mesa(T, t0, 1.05); u = ease((T - t0) / .3); hoja_en(c, 540, 860 + 300 * (1 - u), 1.02, -3)
    k = pop(T, T_UNA, .22)
    if k > 0: lapiz_rojo(c, (130, 640, 480, 1050), u_(T, T_UNA, .35), 14, 5); rotulo(c, "SOLO UNA LETRA", 540, 440, 92, ROJO, CREMA, -4, k=k)
    return view(c, 540, 860, 1.0 + .1 * u_(T, t0, 2.5))

# ---------------------------------------------------------------- 2 · ustedes eligieron CASTIGO
@esc(S("L02") - .1)
def eligieron(T, t0):
    c, tr = sofa(560, 930, 1.5 + .06 * u_(T, t0, 2)); c = borroso(c, 8, 70); mateo(c, "triste", 250 - 420 * (1 - ease((T - t0) / .25)), 800, 1.1, T, blink=False)
    k = pop(T, t0 + .05, .2); tiza(c, "USTEDES", 740, 430, 96 * k, CREMA, -2, f=F_BAL, stroke=3, borde=True); tiza(c, "ELIGIERON:", 740, 545, 96 * k, AMA, -2, f=F_BAL, stroke=3, borde=True)
    k = pop(T, WI("L02", 1) - .08, .2)
    if k > 0: rotulo(c, "CASTIGO", 740, 730, 128, ROJO, CREMA, -5, k=k)
    return c

def tele(c, cx, cy, s, tach):
    d = ImageDraw.Draw(c)
    d.line((cx - 70 * s, cy - 250 * s, cx, cy - 170 * s), fill=OL, width=int(14 * s)); d.line((cx + 70 * s, cy - 250 * s, cx, cy - 170 * s), fill=OL, width=int(14 * s))
    d.rounded_rectangle((cx - 270 * s, cy - 180 * s, cx + 270 * s, cy + 180 * s), int(40 * s), fill=(70, 66, 96), outline=OL, width=int(9 * s))
    d.rounded_rectangle((cx - 230 * s, cy - 140 * s, cx + 150 * s, cy + 140 * s), int(24 * s), fill=(150, 214, 240), outline=OL, width=int(6 * s))
    d.ellipse((cx - 110 * s, cy - 70 * s, cx + 30 * s, cy + 70 * s), fill=AMA, outline=OL, width=int(6 * s))
    for ex in (-66, -14): d.ellipse((cx + ex * s - 9 * s, cy - 24 * s, cx + ex * s + 9 * s, cy - 6 * s), fill=OL)
    d.arc((cx - 80 * s, cy - 20 * s, cx, cy + 40 * s), 20, 160, fill=OL, width=int(7 * s))
    for dy in (-70, 10): d.ellipse((cx + 180 * s, cy + dy * s, cx + 230 * s, cy + dy * s + 50 * s), fill=CREMA, outline=OL, width=int(5 * s))
    if tach > 0:
        r = 300 * s; d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=ROJO, width=int(34 * s)); a = clamp(tach)
        d.line((cx - r * .7, cy - r * .7, cx - r * .7 + 1.4 * r * a, cy - r * .7 + 1.4 * r * a), fill=ROJO, width=int(34 * s))

@esc(WI("L02", 2) - .1)
def sin_dibujos(T, t0):
    c, tr = vista("bg_sala", 540, 900, 1.5); c = borroso(c, 12, 110); k = pop(T, t0 + .03, .22)
    tele(c, 540, 800, 1.1 * k, u_(T, WI("L02", 4) - .05, .25))
    rotulo(c, "3 DÍAS", 300, 420, 120, AMA, OL, -5, k=k)
    k = pop(T, WI("L02", 4) - .05, .2)
    if k > 0: rotulo(c, "SIN DIBUJOS", 600, 1180, 100, ROJO, CREMA, -3, k=k)
    return c

def esponja(c, x, y, s, T):
    d = ImageDraw.Draw(c)
    for i in range(7):
        a = i * .9 + T * 2; r = (22 + 12 * math.sin(i * 2.1)) * s; bx, by = x + 150 * s * math.cos(a) * .9, y + 90 * s * math.sin(a) + 60 * s
        d.ellipse((bx - r, by - r, bx + r, by + r), fill=(255, 255, 255, 235), outline=(170, 210, 235), width=3)
    d.rounded_rectangle((x - 120 * s, y - 70 * s, x + 120 * s, y + 70 * s), int(26 * s), fill=AMA, outline=OL, width=int(7 * s))
    d.rounded_rectangle((x - 120 * s, y - 70 * s, x + 120 * s, y - 28 * s), int(18 * s), fill=VERDE_C, outline=OL, width=int(7 * s))

@esc(WI("L02", 6) - .1)
def limpiar(T, t0):
    z = 1.75 + .1 * u_(T, t0, 2); c, tr = sofa(520, 930, z); a = (T - t0) * 5.2
    x, y = tr((540 + 150 * math.sin(a), 920 + 70 * math.sin(a * 2)))
    esponja(c, x, y, 1.0, T)
    mateo(c, "triste", 150, 1120, .8, T, blink=False)
    k = pop(T, WI("L02", 8) - .05, .2)
    if k > 0: rotulo(c, "A LIMPIAR EL SOFÁ", 560, 420, 84, CREMA, OL, -3, k=k)
    return c

# ---------------------------------------------------------------- 3 · «era para papá»
@esc(S("L03") - .15)
def bonita(T, t0):
    c, tr = vista("bg_sala", 300, 900, 2.2); c = borroso(c, 10, 50); mateo(c, "triste", 500, 700, 1.4 + .06 * u_(T, t0, 2), T, "L03", blink=False)
    return c

@esc(WI("L03", 6) - .1, True)
def para_papa(T, t0):
    z = 1.9 + .2 * u_(T, t0, 2.2); c, tr = sofa(540, 915, z); x, y = tr((540, 730))
    k = pop(T, WI("L03", 7) - .08, .28)
    if k > 0: tiza(c, "para papá", x - 40, y - 60, 130 * k, CREMA, -5, stroke=2, borde=True); corazon(c, x + 300, y - 70, 34 * k * (1 + .08 * math.sin(T * 8)))
    return c

# ---------------------------------------------------------------- 4 · papá no dice nada… pero esa noche (ternura)
@esc(S("L04") - .2)
def papa_calla(T, t0):
    c = puerta(T, 540, 760, 1.7 + .12 * u_(T, t0, 2), abierta=1.0, papa=1.0, px=540)
    k = pop(T, WI("L04", 3) - .1, .25)
    if k > 0: tiza(c, "…", 250, 430, 200 * k, CREMA, 0, f=F_BAL, stroke=3, borde=True)
    return c

@esc(WI("L04", 4) - .1)
def esa_noche(T, t0):
    """La sala a oscuras; papá, a contraluz, se acerca al sofá."""
    z = 1.3 + .1 * u_(T, t0, 2.5); c, tr = sofa(540, 960, z); u = ease((T - t0 - .1) / 1.0)
    x, y = tr((1060 - 250 * u, 1330)); s = .7 * z; put(c, "papa_silueta", x, y - 810 * s, s)
    noche(c, int(tr((540, 915))[0]), int(tr((540, 915))[1]), 1000, 215)
    k = pop(T, WI("L04", 5) - .05, .25)
    if k > 0: tiza(c, "ESA NOCHE…", 420, 420, 110 * k, CREMA, -3, f=F_BAL, stroke=3, borde=True)
    return c

@lru_cache(1)
def _pantalla():
    c, tr = sofa(540, 905, 2.6); return c.resize((372, 662), Image.LANCZOS)
T_FOTO = WI("L04", 12) - .02
@esc(WI("L04", 9) - .1, True)
def foto(T, t0):
    """Le toma una foto a la M: el móvil, la M en la pantalla y el destello."""
    z = 1.7 + .12 * u_(T, t0, 3.5); c, tr = sofa(560, 930, z); noche(c, 540, 900, 1100, 205)
    u = ease((T - t0) / .4); cx, cy = 600, 1010 + 700 * (1 - u) + 6 * math.sin(T * 3); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse((cx + 120, cy + 300, cx + 420, cy + 620), fill=(34, 30, 60)); d.polygon([(cx + 200, cy + 420), (cx + 430, cy + 380), (cx + 700, cy + 1100), (cx + 380, cy + 1100)], fill=(34, 30, 60))
    d.rounded_rectangle((cx - 214, cy - 380, cx + 214, cy + 380), 46, fill=(20, 20, 30), outline=(90, 94, 120), width=6)
    lay.alpha_composite(_pantalla(), (int(cx - 186), int(cy - 331)))
    d.ellipse((cx - 30, cy + 250, cx + 30, cy + 310), fill=CREMA, outline=(150, 150, 160), width=5)
    for a, b in (((-150, -290), (40, 0)), ((-150, -290), (0, 40)), ((150, 200), (-40, 0)), ((150, 200), (0, -40))): d.line((cx + a[0], cy + a[1], cx + a[0] + b[0], cy + a[1] + b[1]), fill=CREMA, width=6)
    c.alpha_composite(lay.rotate(-6, center=(cx, cy), resample=Image.BICUBIC))
    if T >= T_FOTO:
        f = math.exp(-(T - T_FOTO) * 7)
        if f > .02: c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(235 * f))))
        k = pop(T, T_FOTO + .15, .3); corazon(c, 300, 560 - 30 * u_(T, T_FOTO, 2), 46 * k * (1 + .07 * math.sin(T * 7)))
        k = pop(T, WI("L04", 16) - .05, .25)
        if k > 0: rotulo(c, "ANTES DE BORRARLA", 540, 420, 76, CREMA, OL, -3, k=k)
    return c

# ---------------------------------------------------------------- 5 · hoy, en clase
@esc(S("L05") - .2)
def clase(T, t0):
    c = pared_img().copy(); u = u_(T, t0, 3); return view(c, 540, 700 + 300 * u, 1.05 + .2 * u)

T_SOLO = WI("L05", 8) - .1
@esc(T_SOLO)
def lo_unico(T, t0):
    c = pared_img().copy(); x, y = HUECO; k = pop(T, t0 + .12, .25)
    if k > 0:
        card = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(card); d.rounded_rectangle((x - 102, y - 70, x + 102, y + 70), 12, fill=CREMA + (255,), outline=OL + (255,), width=5)
        crayon(card, letraM(x - 86, y - 44, 60, 86, 71, j=1.5), 9, VERDE)
        for i in range(4): d.line((x - 10 + i * 27, y + 44, x + 8 + i * 27, y + 44), fill=(150, 150, 168), width=4)
        d.ellipse((x - 12, y - 78, x + 12, y - 54), fill=ROJO, outline=OL, width=4); c.alpha_composite(card)
    c = view(c, x, y + 40, 2.3 + .35 * u_(T, t0, 2.5))
    k = pop(T, WI("L05", 10) - .05, .22)
    if k > 0: rotulo(c, "LO ÚNICO QUE SABE", 540, 420, 84, ROJO, CREMA, -3, k=k)
    return c

BK = 1.55      # Bruno es más grande que Mateo
def bruno_(c, kind, hx, hy, s, T, lid=None):
    """Bruno: personaje propio (bruno_art.py) — grandote, rubio de punta, curita, le falta un diente, suéter morado de rayas. Cara y voz fijas."""
    hab = lid is not None and talk(lid, T)
    if hab: kind = "rie" if int(T * 9) % 2 == 0 else "rie2"
    put(c, f"bruno_{kind}", hx, hy + 498 * s * BK, s * BK)

@esc(S("L06") - .2)
def bruno(T, t0):
    c = borroso(pared_img().copy(), 9, 60); tr_ = WI("L06", 6) - .05; rie = T >= tr_
    bruno_(c, "rie" if rie else "burlon", 800, 800 - (20 * abs(math.sin((T - tr_) * 10)) if rie else 0), .8, T)
    mateo(c, "timido" if not rie else "triste", 250, 900, .95, T, blink=False)
    k = pop(T, WI("L06", 1) - .08, .2)
    if k > 0: rotulo(c, "BRUNO", 800, 400, 84, MORA, CREMA, 4, k=k)
    jaja(c, T, tr_, [(470, 560, 110, -8), (1000, 1150, 90, 8)])
    return c

@esc(S("L06B") - .12)
def una_sola(T, t0):
    """Bruno, de cerca, lo dice con su propia voz; Mateo, pequeño, lo oye."""
    c = borroso(pared_img().copy(), 12, 90); hab = talk("L06B", T)
    bruno_(c, "rie", 620, 960 - 14 * abs(math.sin((T - t0) * 10)), .92 + .04 * u_(T, t0, 2), T, "L06B")
    mateo(c, "triste", 160, 1330, .62, T, blink=False)
    k = pop(T, t0 + .05, .22)
    if k > 0:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); d.rounded_rectangle((150, 320, 910, 610), 60, fill=CREMA + (255,), outline=OL + (255,), width=8)
        d.polygon([(560, 600), (640, 720), (680, 600)], fill=CREMA + (255,)); d.line([(560, 606), (640, 720), (680, 606)], fill=OL + (255,), width=8)
        d.text((530, 410), "¡SOLO SABE", font=font(F_BAL, 92), fill=OL, anchor="mm"); d.text((530, 520), "UNA LETRA!", font=font(F_BAL, 92), fill=ROJO, anchor="mm")
        c.alpha_composite(lay.rotate(-3, center=(530, 460), resample=Image.BICUBIC))
    jaja(c, T, WI("L06B", 3) + .25, [(930, 800, 110, 10), (960, 1010, 84, -6), (170, 800, 80, -10)])
    return c

@esc(S("L07") - .2)
def no_volver(T, t0):
    c, tr = vista("bg_sala", 300, 900, 1.9); c = borroso(c, 8, 50); hx = 470 + 4 * math.sin(T * 15)
    mateo(c, "llora", hx, 720, 1.3 + .05 * u_(T, t0, 2), T, "L07", blink=False); lagrimas(c, hx, 810, T, 3, 1.2)
    put(c, "mochila", 900, 1180, .52, rot=-14)
    return c

@esc(WI("L07", 4) - .1)
def el_unico(T, t0):
    c, tr = vista("bg_sala", 300, 900, 2.3); c = borroso(c, 12, 80); mateo(c, "triste", 540, 780, 1.6 + .08 * u_(T, t0, 2.2), T, "L07", blink=False)
    return c

# ---------------------------------------------------------------- 6 · tú, la mamá: la verdad
@esc(S("L08") - .25, True)
def respiras(T, t0):
    c, tr = vista("bg_sala", 540, 900, 1.4 + .05 * math.sin((T - t0) * 2.4)); c = borroso(c, 14, 60)
    k = pop(T, t0 + .1, .3); tiza(c, "RESPIRAS.", 540, 760, 150 * k, CREMA, -2, f=F_BAL, stroke=3, borde=True)
    return c

@esc(WI("L08", 1) - .1)
def a_su_lado(T, t0):
    c, tr = vista("bg_sala", 380, 900, 1.8 + .08 * u_(T, t0, 2.6)); c = borroso(c, 6, 30); mateo(c, "triste" if T < WI("L08", 6) else "timido", 430, 740, 1.3, T, blink=False)
    brazo_mama(c, 430, 740, 1.3, ease((T - t0 - .15) / .6))
    return c

IMX = [150, 385, 565, 745, 925]
def imanes(c, T, y, hasta_M=1.0, gris=True, big=1.0):
    d = ImageDraw.Draw(c)
    for i, ch in enumerate("MATEO"):
        x = IMX[i]; s = (1.0 + .5 * big) if i == 0 else 1.0; w = 84 * s
        on = i == 0
        d.rounded_rectangle((x - w, y - w, x + w, y + w), int(26 * s), fill=IMAN[0] if on else (228, 222, 206), outline=OL, width=7)
        d.text((x, y - 4), ch, font=font(F_BAL, 150 * s), fill=CREMA if on else (176, 170, 156), anchor="mm")

T_SUYA = WI("L08", 21) - .08
@esc(WI("L08", 11) - .12)
def la_dificil(T, t0):
    c = _mesa(T, t0, 1.05); u = ease((T - t0) / .3); big = ease((T - WI("L08", 12) + .1) / .3) if T > WI("L08", 12) - .1 else 0
    imanes(c, T, 800 + 200 * (1 - u), big=big)
    k = pop(T, WI("L08", 16) - .08, .22)
    if k > 0: rotulo(c, "LA MÁS DIFÍCIL", 420, 520, 96, ROJO, CREMA, -4, k=k); tiza(c, "↓", 170, 620, 90 * k, OL, 0, f=DJ)
    return view(c, 480, 800, 1.0 + .1 * u_(T, t0, 3))

@esc(T_SUYA, True)
def ya_es_suya(T, t0):
    c = _mesa(T, t0, 1.05); imanes(c, T, 800, big=1.0); c = view(c, 330, 800, 1.5 + .25 * u_(T, t0, 1.6))
    k = pop(T, t0 + .1, .25); rotulo(c, "✔ YA ES SUYA", 600, 440, 104, VERDE_C, CREMA, -4, f=DJ, k=k); chispas(c, 300, 800, T, t0 + .15, 8, 380, 6)
    return c

# ---------------------------------------------------------------- 7 · el truco de hoy: dos montañas que se dan la mano
MT = [_poli([(250, 1130), (262, 760)], 12, 81, 2.5), _poli([(262, 760), (540, 1010)], 12, 82, 2.5), _poli([(540, 1010), (812, 752)], 12, 83, 2.5), _poli([(812, 752), (826, 1130)], 12, 84, 2.5)]
MT_ALL = [p for s_ in MT for p in s_]
def hoja_blanca(c, T, t0, dy=0):
    sombra(c, (110, 600 + dy, 970, 1250 + dy), 8, 110, 18); d = ImageDraw.Draw(c); d.rectangle((110, 600 + dy, 970, 1250 + dy), fill=CREMA, outline=(214, 190, 150), width=7)

def montanas(c, k):
    """Dos montañas (los dos picos de la M) que se dan la mano en el valle."""
    if k <= 0: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); a = int(255 * clamp(k))
    for (px, py), bx0, bx1 in (((262, 760), 250, 540), ((812, 752), 540, 826)):
        d.polygon([(bx0, 1130), (px, py), (bx1 if bx1 == 540 else 826, 1010 if bx1 == 540 else 1130), (540, 1010) if bx0 == 540 else (540, 1130)], fill=(196, 226, 246, a))
        sx = 1 if bx0 == 250 else -1
        d.polygon([(px, py), (px + sx * 62, py + 58), (px + sx * 30, py + 84), (px + sx * 4, py + 62), (px + (0 if sx > 0 else -0), py + 96)], fill=(255, 255, 255, a))
        ex = px + sx * 60; ey = py + 190
        for q in (-22, 22): d.ellipse((ex + q - 9, ey - 9, ex + q + 9, ey + 9), fill=OL + (a,))
        d.arc((ex - 30, ey + 6, ex + 30, ey + 52), 20, 160, fill=OL + (a,), width=7)
    d.polygon([(250, 1130), (540, 1130), (540, 1010)], fill=(196, 226, 246, a)); d.polygon([(826, 1130), (540, 1130), (540, 1010)], fill=(196, 226, 246, a))
    for sx in (-1, 1): d.line((540 + sx * 96, 960, 540 + sx * 20, 1000), fill=(120, 170, 210, a), width=16); d.ellipse((540 + sx * 26 - 24, 1000 - 24, 540 + sx * 26 + 24, 1000 + 24), fill=PIEL + (a,), outline=OL + (a,), width=5)
    c.alpha_composite(lay)

@esc(S("L09") - .2)
def despacio(T, t0):
    c = _mesa(T, t0, 1.05); u = ease((T - t0) / .35); hoja_blanca(c, T, t0, 500 * (1 - u))
    k = pop(T, WI("L09", 3) - .08, .22)
    if k > 0: rotulo(c, "DESPACIO", 540, 440, 104, AZUL, CREMA, -3, k=k)
    mano(c, (250 + 500 * (1 - u), 1130), T, .9); return c

T_MONT = WI("L09", 4) - .1; T_MANO = WI("L09", 8) - .05
@esc(T_MONT, True)
def dos_montanas(T, t0):
    c = _mesa(T, t0, 1.05); hoja_blanca(c, T, t0); montanas(c, u_(T, t0 + .05, .35))
    k = pop(T, WI("L09", 5) - .08, .22)
    if k > 0: rotulo(c, "DOS MONTAÑAS", 540, 440, 96, AZUL, CREMA, -3, k=k)
    if T >= T_MANO: chispas(c, 540, 1000, T, T_MANO, 5, 150, 4); corazon(c, 540, 900 - 40 * u_(T, T_MANO, 1.2), 24 * pop(T, T_MANO, .25))
    return view(c, 540, 930, 1.0 + .16 * u_(T, t0, 2.6))

T_SB = [WI("L09", i) - .04 for i in (11, 12, 13, 14)]; T_SB.append(T_SB[3] + .55)
@esc(T_SB[0] - .15, True)
def sube_baja(T, t0):
    """El trazo real, paso a paso: cada trazo cae con su palabra."""
    c = _mesa(T, t0, 1.05); hoja_blanca(c, T, t0); montanas(c, .42); pts = []
    for i in range(4):
        u = u_(T, T_SB[i], max(.22, (T_SB[i + 1] - T_SB[i]) * .8)); pts += parcial(MT[i], u)
    if len(pts) >= 2: crayon(c, pts, 30, VERDE)
    for i in range(4):
        if T_SB[i] <= T < T_SB[i + 1] or (i == 3 and T >= T_SB[3]):
            rotulo(c, ("SUBE " + SUB, "BAJA " + BAJ)[i % 2], 300, 440, 104, (VERDE_C, AZULC)[i % 2], CREMA, -3, f=DJ, k=pop(T, T_SB[i], .18))
    mano(c, pts[-1] if pts else MT[0][0], T, .9); return c

@esc(S("L10") - .2)
def mas_faciles(T, t0):
    c = _mesa(T, t0, 1.2); c = borroso(c, 8, 40); mateo(c, "timido", 380, 760, 1.35 + .05 * u_(T, t0, 2), T, "L10", blink=False)
    for i, ch in enumerate("ATEO"):
        k = pop(T, WI("L10", 1) - .05 + i * .1, .2)
        if k > 0: rotulo(c, ch, 800 + (i % 2) * 150 - 75, 480 + (i // 2) * 190, 120, (228, 222, 206), (150, 144, 130), (-6, 5, 4, -5)[i], k=k)
    k = pop(T, WI("L10", 4) - .05, .2)
    if k > 0: tiza(c, "?", 800, 880, 190 * k, AMA, 8, f=F_BAL, stroke=3, borde=True)
    return c

@esc(S("L11") - .2)
def que_si(T, t0):
    c = _mesa(T, t0, 1.25); c = borroso(c, 8, 40); tn = WI("L11", 4) - .08
    mateo(c, "neutral" if T < tn else "timido", 540, 800, 1.45 + .06 * u_(T, t0, 2.5), T, blink=False)
    k = pop(T, WI("L11", 3) - .1, .2)
    if k > 0 and T < tn: rotulo(c, "SÍ", 820, 470, 150, VERDE_C, CREMA, 5, k=k)
    k = pop(T, tn, .22)
    if k > 0: tiza(c, "mmm…", 800, 470, 130 * k, CREMA, 6, stroke=2, borde=True)
    return c

# ---------------------------------------------------------------- 8 · esa noche: vuelve Rex (el momento de ternura)
@esc(S("L12") - .25)
def duerme(T, t0):
    c = bg("bg_noche", T, t0, 1.0, 1.0, 1, .5, .5); put(c, "mateo_duerme", 540, 1000 + 5 * math.sin((T - t0) * 2), 1.0)
    c.alpha_composite(Image.new("RGBA", (W, H), NOCHE + (96,)))
    for i in range(3):
        u = ((T - t0) * .5 + i / 3) % 1; tiza(c, "z", 640 + 110 * u + 30 * i, 760 - 260 * u, 50 + 70 * u, CREMA, 10, f=F_BAL, alpha=int(255 * math.sin(PI_ * u)))
    k = pop(T, t0 + .1, .25); tiza(c, "ESA NOCHE…", 430, 430, 110 * k, CREMA, -3, f=F_BAL, stroke=3, borde=True)
    return view(c, 540, 950, 1.05 + .12 * u_(T, t0, 2.5))

NX, NY, NS = 540, 800, .9
def nota_base(c, dy=0):
    sombra(c, (NX - 470 * NS, NY - 570 * NS + dy, NX + 470 * NS, NY + 570 * NS + dy), 10, 120, 20); put(c, "nota", NX, NY + dy, NS)

@esc(WI("L12", 4) - .1)
def tomas_hoja(T, t0):
    c = _mesa(T, t0, 1.05); u = ease((T - t0) / .4); nota_base(c, 900 * (1 - u)); noche(c, 540, 800, 1050, 190)
    mano(c, (300 + 500 * (1 - ease((T - t0 - .5) / .5)), 470), T, .9)
    k = pop(T, WI("L12", 10) - .05, .22)
    if k > 0: rotulo(c, "CON LETRA TORCIDA", 540, 1240, 72, CREMA, OL, -3, k=k)
    return c

def _carta():
    """Cada letra de la nota de Rex con su sitio, su giro y el instante en que se escribe."""
    r = random.Random(9); out = []; f0 = 92
    filas = [("Hola, Mateo.", (0, 1), 470), ("Soy Rex.", (2, 3), 630), ("Yo no sé hacer la M.", (4, 5, 6, 7, 8, 9), 790), ("¿Me enseñas?", (10, 11), 950)]
    cap = [x for x in LINEAS if x[0] == "L13"][0][3].split(); wt = R.word_times("L13", cap); d = ImageDraw.Draw(Image.new("L", (8, 8)))
    for txt, idx, y in filas:
        x = 230; pal = txt.split(" ")
        for w, wi in zip(pal, idx):
            a, b = wt[wi]; a -= .12; b = max(b - .1, a + .12)
            for j, ch in enumerate(w):
                sz = f0 + r.uniform(-9, 9); f = font(F_HAND, sz); wd = d.textlength(ch, font=f)
                out.append((ch, x + wd / 2, y + r.uniform(-9, 9), r.uniform(-11, 11), sz, a + (b - a) * j / max(1, len(w)), w == "M." and ch == "M"))
                x += wd + r.uniform(0, 5)
            x += 26
    return out
CARTA = _carta(); T_HUELLA = E("L13") + .05
@lru_cache(None)
def _letra(ch, sz, rot, col):
    t = Image.new("RGBA", (int(sz * 1.6), int(sz * 1.8)), (0, 0, 0, 0)); ImageDraw.Draw(t).text((t.width / 2, t.height / 2), ch, font=font(F_HAND, sz), fill=col + (255,), anchor="mm", stroke_width=2, stroke_fill=col + (255,))
    return t.rotate(rot, resample=Image.BICUBIC)
def carta(c, T, tr=lambda p: p, z=1.0, todo=False):
    tip = None
    for ch, x, y, rot, sz, t, roja in CARTA:
        if todo or T >= t:
            im = _letra(ch, int(sz * z), round(rot), ROJO if roja else REXO); p = tr((x, y)); c.alpha_composite(im, (int(p[0] - im.width / 2), int(p[1] - im.height / 2)))
            if not todo and T < t + .14: tip = (p[0] + 14, p[1] + 26)
    if todo or T >= T_HUELLA:
        k = 1 if todo else pop(T, T_HUELLA, .25); p = tr((760, 1130)); huella(c, p[0], p[1], 1.0 * k * z, REXO, -14)
    return tip

@esc(S("L13") - .2, True)
def escribe_rex(T, t0):
    """Plano largo y tranquilo: la nota se escribe letra a letra, con la voz."""
    c = _mesa(T, t0, 1.05); nota_base(c); tip = carta(c, T); noche(c, 540, 800, 1100, 170)
    if tip is None:
        nxt = [q for q in CARTA if q[5] > T]; prv = [q for q in CARTA if q[5] <= T]
        tip = (nxt[0][1], nxt[0][2] + 20) if nxt and not prv else ((prv[-1][1] + 16, prv[-1][2] + 26) if nxt else (760 + 300 * u_(T, T_HUELLA, .5), 1130 + 200 * u_(T, T_HUELLA, .5)))
    mano(c, tip, T, .9)
    return view(c, 540, 800, 1.0 + .1 * u_(T, t0, 6))

RXD = (857, 471)      # Rex en la capa mateo_duerme (respecto a su esquina)
@esc(S("L14") - .2)
def entre_patas(T, t0):
    """La nota, entre las patas de Rex, mientras Mateo duerme."""
    c = bg("bg_noche", T, t0, 1.0, 1.0, 1, .5, .5); put(c, "mateo_duerme", 540, 1000, 1.0)
    u = ease((T - t0 - .25) / .7); x, y = 868, 1000 - 620 + 600 + 60 * (1 - u); a = clamp((T - t0 - .2) / .3)
    if a > 0:
        n = Image.new("RGBA", (120, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(n); d.rounded_rectangle((0, 0, 119, 149), 6, fill=CREMA + (255,), outline=OL + (255,), width=4)
        for i in range(4): d.line((16, 34 + i * 26, 104 - (30 if i == 3 else 0), 34 + i * 26), fill=REXO, width=5)
        d.ellipse((78, 112, 100, 134), fill=REXO); paste_rot(c, n, x + 250 * (1 - u), y + 80 * (1 - u), 1.0, -12 + 30 * (1 - u), a)
    c.alpha_composite(Image.new("RGBA", (W, H), NOCHE + (70,))); c.alpha_composite(luz_img(868, 950, 900, 150))
    if u >= 1: corazon(c, 980, 800 - 40 * u_(T, t0 + 1, 1.5), 20 * pop(T, t0 + 1, .3))
    return view(c, 800, 940, 1.5 + .35 * u_(T, t0, 2.4))

# ---------------------------------------------------------------- 9 · «¡Rex me escribió!»
def nota_mini(c, cx, cy, s, rot):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); put(lay, "nota", NX, NY, NS); carta(lay, 0, todo=True)
    im = lay.crop((int(NX - 480 * NS), int(NY - 580 * NS), int(NX + 480 * NS), int(NY + 580 * NS))); paste_rot(c, im, cx, cy, s, rot)
@lru_cache(1)
def nota_llena():
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); put(lay, "nota", NX, NY, NS); carta(lay, 0, todo=True)
    return lay.crop((int(NX - 480 * NS), int(NY - 580 * NS), int(NX + 480 * NS), int(NY + 580 * NS)))

@esc(S("L15") - .2)
def mami(T, t0):
    c = bg("bg_cuarto", T, t0, 1.25, 1.32, 3, .5, .4); j = 26 * abs(math.sin((T - t0) * 9))
    mateo(c, "feliz", 360, 760 - j, 1.2, T, "L15", blink=False); paste_rot(c, nota_llena(), 800, 900 - j * .6, .44, 8 + 3 * math.sin(T * 7))
    chispas(c, 800, 880, T, t0 + .1, 6, 300, 12)
    return c

T_YOSI = WI("L15", 8) - .08
@esc(WI("L15", 4) - .12)
def no_sabe(T, t0):
    c = bg("bg_cuarto", T, t0, 1.5, 1.56, 3, .5, .4); c = borroso(c, 8, 20)
    paste_rot(c, nota_llena(), 660, 860, .78, 5); lapiz_rojo(c, (330, 760, 1010, 920), u_(T, t0 + .15, .4), 12, 4)
    mateo(c, "feliz", 190, 1180 - 16 * abs(math.sin((T - t0) * 9)), .78, T, "L15", blink=False)
    k = pop(T, T_YOSI, .22)
    if k > 0: rotulo(c, "¡Y YO SÍ!", 600, 420, 120, VERDE_C, CREMA, -5, k=k)
    return c

def rex(c, x, y, s, T, rot=0): put(c, "dino", x, y + 4 * math.sin(T * 2.4), s, rot=rot)
def suelo(T, t0, cx=540, cy=1500, z=1.5):
    c, tr = vista("bg_cuarto", cx, cy, z); return c, tr

@esc(S("L16") - .2, True)
def en_el_suelo(T, t0):
    """Plano general tranquilo: Mateo se sienta en el suelo frente a Rex."""
    c, tr = suelo(T, t0, 540, 1480, 1.3 + .08 * u_(T, t0, 3)); u = ease((T - t0 - .1) / .6)
    rex(c, 760, 1010, .62, T); hoja_blanca_mini(c, 520, 1250, .42, -4)
    mateo(c, "concentra" if T > WI("L16", 6) else "feliz", 270, 560 + 220 * u, 1.0, T, blink=False)
    return c

def hoja_blanca_mini(c, cx, cy, s, rot):
    n = Image.new("RGBA", (880, 660), (0, 0, 0, 0)); d = ImageDraw.Draw(n); d.rectangle((4, 4, 875, 655), fill=CREMA + (255,), outline=(214, 190, 150, 255), width=8); paste_rot(c, n, cx, cy, s, rot)

T_PAT = WI("L16", 7) - .1
@esc(T_PAT, True)
def la_patita(T, t0):
    """Le toma la patita: la mano de Mateo llega hasta la pata de Rex."""
    c, tr = suelo(T, t0, 700, 1480, 1.9 + .1 * u_(T, t0, 2.4)); c = borroso(c, 5, 10)
    rex(c, 700, 760, 1.05, T, 3 * math.sin((T - t0) * 3)); u = ease((T - t0 - .15) / .7)
    px, py = 400, 1080; pata(c, px, py, 1.25, 8)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); hx, hy = px - 60 - 520 * (1 - u), py + 50 + 240 * (1 - u)
    d.line((hx - 700, hy + 420, hx, hy), fill=OL, width=150); d.line((hx - 700, hy + 420, hx, hy), fill=BATA_, width=134)
    d.ellipse((hx - 90, hy - 84, hx + 90, hy + 84), fill=PIEL, outline=OL, width=8); c.alpha_composite(lay)
    if u >= 1: corazon(c, px + 40, py - 190 - 30 * u_(T, t0 + .9, 1.5), 34 * pop(T, t0 + .9, .3) * (1 + .08 * math.sin(T * 8)))
    return c

MR = [_poli([(270, 1140), (290, 790)], 12, 91, 7), _poli([(290, 790), (520, 1000)], 12, 92, 8), _poli([(520, 1000), (770, 770)], 12, 93, 8), _poli([(770, 770), (800, 1150)], 12, 94, 7)]
T_SR = [WI("L16", i) - .04 for i in (14, 15, 16, 17)]; T_SR.append(T_SR[3] + .6)
@esc(T_SR[0] - .25, True)
def ensena(T, t0):
    """Mateo le enseña a Rex: la mano de Mateo guía la patita y la M sale, torcida y suya."""
    c, tr = suelo(T, t0, 540, 1620, 1.6); c = borroso(c, 6, 10); hoja_blanca(c, T, t0); pts = []
    put(c, "dino", 900, 470 + 4 * math.sin(T * 2.4), .72)
    for i in range(4):
        u = u_(T, T_SR[i], max(.25, (T_SR[i + 1] - T_SR[i]) * .82)); pts += parcial(MR[i], u)
    if len(pts) >= 2: crayon(c, pts, 30, VERDE)
    for i in range(4):
        if T_SR[i] <= T < T_SR[i + 1] or (i == 3 and T >= T_SR[3]):
            rotulo(c, ("SUBE " + SUB, "BAJA " + BAJ)[i % 2], 400, 450, 110, (VERDE_C, AZULC)[i % 2], CREMA, -3, f=DJ, k=pop(T, T_SR[i], .18))
    tip = pts[-1] if pts else MR[0][0]
    d = ImageDraw.Draw(c); d.line((930, 700, tip[0] + 330, tip[1] - 40), fill=OL, width=120); d.line((930, 700, tip[0] + 330, tip[1] - 40), fill=REXV, width=104)
    mano(c, tip, T, .9); pata(c, tip[0] + 230, tip[1] - 50, 1.0, 14)
    return c

T_EL = WI("L16", 18) - .12
@esc(T_EL, True)
def el_que_sabe(T, t0):
    """El cierre tierno: por primera vez, el que sabe es él."""
    c = bg("bg_cuarto", T, t0, 1.3, 1.42, 4, .5, .45); c = borroso(c, 5, 10)
    mateo(c, "feliz", 330, 800, 1.3 + .05 * u_(T, t0, 3.5), T, blink=False); rex(c, 800, 1010, .78, T, -4)
    corazones(c, 560, 760, T, t0 + .2, 6, 5)
    k = pop(T, WI("L16", 21) - .08, .25)
    if k > 0: rotulo(c, "EL QUE SABE ES ÉL", 540, 420, 92, AMA, OL, -3, k=k)
    return c

# ---------------------------------------------------------------- 10 · pero hay que volver
@esc(S("L17") - .2)
def volver(T, t0):
    c = bg("bg_escuela", T, t0, 1.1, 1.2, 3, .5, .4); u = ease((T - t0) / .5)
    mateo(c, "timido", 300, 1000 + 300 * (1 - u), .85, T, blink=False); put(c, "mochila", 640, 1420 + 300 * (1 - u), .4, rot=6)
    return c

@esc(WI("L17", 6) - .12)
def bruno_ahi(T, t0):
    c, tr = vista("bg_escuela", 540, 1120, 1.7 + .15 * u_(T, t0, 2)); k = clamp((T - t0) / .25)
    bruno_(c, "burlon", 560, 980 + 60 * (1 - k), .8, T)
    k = pop(T, WI("L17", 7) - .05, .2)
    if k > 0: rotulo(c, "BRUNO", 560, 520, 96, MORA, CREMA, 4, k=k)
    k = pop(T, WI("L17", 10) - .05, .22)
    if k > 0: tiza(c, "…", 900, 700, 190 * k, CREMA, 0, f=F_BAL, stroke=3, borde=True)
    return c

# ---------------------------------------------------------------- 11 · ¿qué harías tú? (cada opción con su pro y su contra)
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

@lru_cache(1)
def _mitades():
    A2 = bg("bg_escuela", 0, 0, 1.5, 1.5, 1, .3, .55); A2.alpha_composite(Image.new("RGBA", (W, H), AZUL + (70,)))
    B2 = borroso(pared_img().copy(), 8, 30); B2.alpha_composite(Image.new("RGBA", (W, H), VERDE_C + (60,)))
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon([(0, 0), (512, 0), (428, H), (0, H)], fill=255); return A2, B2, m
T_Q = S("L18") - .1; T_A, T_B, T_C = WI("L18", 3) - .05, WI("L18", 7) - .05, S("L19") - .05
T_TU = E("L19") + 1
@esc(S("L18") - .25)
def final(T, t0):
    """Pantalla partida: ¿hablas con la maestra o dejas que se defienda solo? Cada opción con su pro y su contra."""
    A2, B2, m = _mitades(); a = A2.copy(); b = B2.copy()
    maestra(a, 235, 1500, .9, T); mateo(b, "neutral", 730 + 4 * math.sin(T * 3), 1500, .9, T, blink=False)
    if T < T_B: b.alpha_composite(Image.new("RGBA", (W, H), (10, 14, 40, int(150 * (1 - u_(T, T_B - .2, .2))))))
    ka = u_(T, T_B, .2) * (1 - u_(T, T_C - .2, .2))
    c = b; c.paste(a, (0, 0), m); d = ImageDraw.Draw(c); d.line((512, 0, 428, H), fill=CREMA, width=16)
    pa = 1 + .07 * math.sin((T - T_C) * 10) if WI("L19", 1) - .08 <= T < WI("L19", 2) else 1; pb = 1 + .07 * math.sin((T - T_C) * 10) if WI("L19", 3) - .08 <= T < T_TU else 1
    tarjeta(c, 247, 640, .7 * pop(T, T_A, .3) * pa, "MAESTRA", AZUL, "hablar", 3, sub="hablas con ella")
    tarjeta(c, 719, 640, .7 * pop(T, T_B, .3) * pb, "SOLO", VERDE_C, "solo", -3, sub="que se defienda")
    pro_contra(c, 243, 892, "Bruno para", "no aprende solo", pop(T, T_A + .35, .22), pop(T, T_A + .6, .22), 2)
    pro_contra(c, 718, 892, "gana confianza", "puede volver llorando", pop(T, T_B + .35, .22), pop(T, T_B + .6, .22), -2)
    if ka > 0: c.paste(Image.alpha_composite(c, Image.new("RGBA", (W, H), (10, 14, 40, int(150 * ka)))), (0, 0), m); d = ImageDraw.Draw(c); d.line((512, 0, 428, H), fill=CREMA, width=16)
    k = pop(T, T_Q, .25)
    if k > 0: rotulo(c, "¿QUÉ HARÍAS TÚ?", 478, 345, 80, AMA, OL, -2, k=k)
    kv = pop(T, T_B + .1, .25)
    if kv > 0:
        r = 58 * kv; d = ImageDraw.Draw(c); d.ellipse((480 - r, 640 - r, 480 + r, 640 + r), fill=AMA, outline=OL, width=8); d.text((480, 638), "o", font=font(F_BAL, 84 * kv), fill=OL, anchor="mm")
    k = pop(T, T_C + .1, .25)
    if k > 0: rotulo(c, "Mándaselo a esa mamá", 478, 1250, 60, CREMA, OL, -2, k=k)
    return c


SC.sort(key=lambda x: x[0])
SCENES = [(t, f) for t, f, s_ in SC]; SUAVES = {t for t, f, s_ in SC if s_}
IMPACTS = [.05, T_UNA, WI("L02", 1) - .08, T_FOTO, S("L06B") - .05, T_YOSI]

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

