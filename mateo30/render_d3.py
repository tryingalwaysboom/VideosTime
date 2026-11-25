"""Temporada "Mateo: 30 días para no repetir" · DÍA 3 — El berrinche (ganó NUNCA).
Mundo visual nuevo (pizarra verde, tiza amarilla, rojo de corrección), barra FALTAN X DÍAS + imanes M-A-T-E-O,
subtítulos palabra a palabra y cierre con dos tarjetas de una palabra.
Uso: python3 render_d1.py still 1 5 | scenes [i...] | info"""
import os, sys, math, json, subprocess, random
from functools import lru_cache
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["GUION"] = "guion_d3"; os.environ["VOZDIR"] = os.path.join(HERE, "voz_d3")
sys.path.insert(0, HERE)
import importlib.util
_spec = importlib.util.spec_from_file_location("R", os.path.join(HERE, "..", "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

R.LAY = os.path.join(HERE, "layers"); R.layer.cache_clear(); R.scaled.cache_clear()
TMP = os.path.join(HERE, "tmp_d3"); os.makedirs(TMP, exist_ok=True)
W, H, FPS = R.W, R.H, R.FPS
put, ease, clamp, back, font, mouth, bg = R.put, R.ease, R.clamp, R.back, R.font, R.mouth, R.bg
F_ANTON = R.F_ANTON
MF = os.path.join(HERE, "..", "mateo-pov", "fonts")
F_HAND = os.path.join(MF, "Caveat.ttf"); F_BAL = os.path.join(MF, "Baloo2-ExtraBold.ttf"); F_AND = os.path.join(MF, "Andika-Bold.ttf")
PI_ = math.pi
OL = (29, 22, 48); PIZ = (36, 82, 66); PIZ2 = (25, 60, 48); TIZA = (246, 244, 232); AMA = (255, 212, 84)
ROJO = (226, 72, 59); CREMA = (255, 253, 244); AZUL = (63, 127, 208); MADERA = (176, 122, 72)
DIAS_FALTAN = 28; LETRAS_ON = ""          # Día 1: ninguna letra dominada

# ---------------------------------------------------------------- tiempos
R.GAP.clear()
BASE = {"J02": .25, "J03": .25, "J04": .45, "J05": .3, "J06": .35, "J07": 1.3, "J08": .9, "J09": .45, "J10": .5, "J11": .4, "J12": .6, "J13": .5, "J14": .3}
FLEX = ("J04", "J05", "J09", "J10", "J11", "J12", "J13")      # pausas que absorben el ajuste para clavar la duración
OBJ, COLA = 64.0, .35                                          # el vídeo dura 64,00 s exactos (segundos enteros, mínimo 62)
R.GAP.update(BASE); _tl, _ = R.timeline(); _extra = (OBJ - COLA) - (_tl["J14"][1] - .1)
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
T_HUD = S("J02") - .1
def draw_hud(c, T):
    if T < T_HUD: return
    y = int(122 - 320 * (1 - ease((T - T_HUD) / .35)))
    if y >= 0: c.alpha_composite(BARRA, (10, y))
    elif -y < BARRA.height: c.alpha_composite(BARRA, (10, 0), (0, -y, BARRA.width, BARRA.height))

# ---------------------------------------------------------------- subtítulos palabra a palabra
T_FINAL = S("J13") - .25
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
    im = Image.open(os.path.join(HERE, "coment_d3", f"c{i}.jpg")).convert("RGB"); g = im.convert("L").point(lambda v: 255 if v < 244 else 0); bb = g.getbbox()
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
    if con_crayola: put(c, "crayola", mx + 30 * s * ux, my + 30 * s * uy, .62, rot=-a2)
    return mx, my

T_SUELTA = .215
@esc(0)
def gancho(T, t0):
    """Primer fotograma: Mateo enojado con la crayola en alto; la lanza y sale volando."""
    c = bg("bg_cocina", T, t0, 1.3, 1.4, 3, .5, .45); s = 1.08 + .05 * u_(T, 0, 2)
    lean = -14 * ease(T / .16) + 44 * ease((T - .16) / .14) if T < .5 else 30
    hx = 265 + lean + 6 * math.sin(T * 19) * (1 - u_(T, .3, .7)); hy = 860
    mateo(c, "enojado_tira", hx, hy, s, T, blink=False)
    a1, a2 = _ang(T); m = brazo_tira(c, hx + 224 * s, hy + 372 * s, a1, a2, s, T < T_SUELTA)
    if T >= T_SUELTA:
        a1r, a2r = _ang(T_SUELTA); sr = 1.08; x0 = 265 + 10 + 224 * sr + 150 * sr * math.cos(math.radians(a1r)) + 216 * sr * math.cos(math.radians(a2r))
        y0 = 860 + 372 * sr + 150 * sr * math.sin(math.radians(a1r)) + 216 * sr * math.sin(math.radians(a2r))
        u = (T - T_SUELTA) / .75; x = x0 + 760 * u; y = y0 - 300 * u + 420 * u * u
        d = ImageDraw.Draw(c)
        for i in range(4 if x < 1200 else 0):
            k = clamp(u * 5) * (1 - .18 * i); yy = y - 46 + i * 30
            d.line((x - 100 - 190 * k, yy + 110 * k, x - 100, yy + 30), fill=OL, width=7)
        put(c, "crayola", x, y, .62, rot=-40 - 900 * u)
    p = 1 + .04 * math.exp(-T * 6) * math.cos(T * 22)
    rotulo(c, "TIRÓ", 420, 250, 132, CREMA, OL, -4, k=p); rotulo(c, "LA CRAYOLA", 520, 410, 112, ROJO, CREMA, -4, k=p)
    k = pop(T, .55, .25)
    if k > 0: rotulo(c, "GANÓ: NUNCA", 280, 1240, 46, AMA, OL, -3, k=k)
    return c

@esc(WI("J01", 3) - .1)
def suelo(T, t0):
    c = Image.new("RGBA", (W, H), MADERA + (255,)); d = ImageDraw.Draw(c)
    for i in range(7): d.line((0, 300 + i * 260 + 40 * math.sin(i), W, 260 + i * 260), fill=(150, 100, 58), width=7)
    u = ease((T - t0) / .35); x = 1300 - 760 * u; r = 720 * (1 - u) + 18
    sombra(c, (x - 260, 880, x + 260, 960), 30, 90, 14); put(c, "crayola", x, 900, 1.0, rot=r)
    k = pop(T, t0 + .32, .2)
    if k > 0:
        for a in range(0, 360, 45): d.line((x + 280 * math.cos(math.radians(a)), 900 + 200 * math.sin(math.radians(a)), x + (280 + 90 * k) * math.cos(math.radians(a)), 900 + (200 + 70 * k) * math.sin(math.radians(a))), fill=TIZA, width=9)
    return view(c, 540, 900, 1 + .1 * u_(T, t0, 2))

@esc(WI("J01", 6) - .1)
def nunca1(T, t0):
    c = bg("bg_cocina", T, t0, 1.5, 1.56, 3, .5, .42); mateo(c, "enojado_x", 540, 700, 1.4 + .06 * u_(T, t0, 2), T, blink=False)
    k = pop(T, t0 + .05, .2)
    if k > 0: tiza(c, "¡NUNCA!", 560, 360, 150 * k, AMA, -5, f=F_BAL, stroke=3, borde=True)
    return c

@esc(S("J02") - .15)
def faltan(T, t0):
    """El objetivo completo antes del segundo 8, con Mateo en pantalla."""
    c = pizarra(); mateo(c, "timido", 270 - 420 * (1 - ease((T - t0) / .3)), 720, 1.05 + .03 * u_(T, t0, 2.5), T)
    k = pop(T, WI("J02", 1) - .08, .25)
    if k > 0: tiza(c, "28", 770, 480, 330 * k * (1 + .03 * math.sin((T - t0) * 9)), AMA, 0, f=F_ANTON)
    k = pop(T, WI("J02", 2) - .05, .22)
    if k > 0: tiza(c, "DÍAS", 770, 700, 130 * k, TIZA, -2, f=F_BAL)
    k = pop(T, WI("J02", 3) - .05, .22)
    if k > 0: tiza(c, "para escribir", 770, 830, 72 * k, TIZA, -2, f=F_BAL)
    k = pop(T, WI("J02", 5) - .05, .22)
    if k > 0: tiza(c, "SU NOMBRE", 750, 925, 84 * k, AMA, -2, f=F_BAL)
    return c

@esc(WI("J02", 7) - .1)
def o_repite(T, t0):
    c = pizarra(); tr_ = WI("J02", 8) - .05
    mateo(c, "neutral" if T < tr_ else "susto", 270 + (9 * math.sin(T * 40) * math.exp(-(T - tr_) * 5) if T >= tr_ else 0), 720, 1.1 + (.08 * ease((T - tr_) / .2) if T >= tr_ else 0), T, blink=False)
    tiza(c, "…o", 760, 470, 150 * pop(T, t0 + .03, .22), TIZA, -3, f=F_BAL)
    k2 = pop(T, tr_, .2)
    if k2 > 0: rotulo(c, "REPITE", 750, 670, 128, ROJO, CREMA, -5, k=k2)
    k3 = pop(T, WI("J02", 9) - .05, .2)
    if k3 > 0: tiza(c, "EL CURSO", 750, 850, 96 * k3, TIZA, -3, f=F_BAL)
    return c

@esc(S("J03") - .1)
def eligieron(T, t0):
    """Lo que eligió el público, con Mateo en pantalla (sin tarjeta)."""
    c = pizarra(); mateo(c, "neutral", 270 - 420 * (1 - ease((T - t0) / .3)), 720, 1.08 + .03 * u_(T, t0, 2.5), T)
    k = pop(T, t0 + .05, .22); tiza(c, "USTEDES", 750, 470, 100 * k, TIZA, -2, f=F_BAL)
    k = pop(T, WI("J03", 2) - .05, .22)
    if k > 0: tiza(c, "ELIGIERON:", 750, 590, 100 * k, AMA, -2, f=F_BAL)
    k = pop(T, WI("J03", 3) - .05, .2)
    if k > 0: rotulo(c, "NO COMPARARLO", 775, 760, 54, CREMA, OL, -3, k=k)
    k = pop(T, WI("J03", 5) - .05, .2)
    if k > 0: rotulo(c, "NUNCA", 750, 900, 120, ROJO, CREMA, -5, k=k)
    return c

def _com_y():
    ys, y = [], 400
    for i in range(6):
        h = _coment(i + 1).height; ys.append(y + h / 2); y += h * .62
    k = min(1.0, (1180 - 400) / (y + _coment(6).height * .38 - 400)); return [400 + (v - 400) * k for v in ys]
COM_Y = _com_y()
T_COM = S("J04") - .25 - 1.5        # 1,5 s exactos de comentarios
@esc(T_COM)
def comentarios(T, t0):
    """Seis comentarios reales de quienes votaron NUNCA (1,5 s) y el sello."""
    c = pizarra(); tiza(c, "USTEDES ELIGIERON", 470, 338, 74, AMA, -2, f=F_BAL)
    for i in range(6):
        ti = t0 + .04 + .9 * i / 6; k = pop(T, ti, .18)
        if k <= 0: continue
        im = _coment(i + 1); cx = 470 + (22 if i % 2 else -22); r = (-2.5, 2, -1.5, 2.5, -2, 1.5)[i]; cy = COM_Y[i] + 40 * (1 - ease((T - ti) / .18))
        sombra(c, (cx - im.width / 2, cy - im.height / 2, cx + im.width / 2, cy + im.height / 2), 26, 120, 14); paste_rot(c, im, cx, cy, k, r)
    ks = pop(T, t0 + 1.0, .2)
    if ks > 0: rotulo(c, "✔ GANÓ: NUNCA", 470, 1246, 58, ROJO, CREMA, -3, f=DJ, k=ks)
    return c

@esc(S("J04") - .25)
def noche(T, t0):
    c = bg("bg_noche", T, t0, 1.15, 1.3, 2.5, .5, .45); k = pop(T, t0 + .1, .25)
    if k > 0: rotulo(c, "ESA NOCHE", 470, 420, 84, (40, 50, 110), CREMA, -3, k=k)
    return c

@esc(WI("J04", 2) - .1)
def solo(T, t0):
    c = bg("bg_cuarto", T, t0, 1.3, 1.36, 3, .5, .5); oscurecer(c, (8, 12, 46), 150)
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((90, 520, 990, 1500), fill=(255, 226, 150, 120)); c.alpha_composite(g.filter(ImageFilter.GaussianBlur(80)))
    mateo(c, "concentra", 540, 700, 1.3 + .05 * u_(T, t0, 2), T); paste_rot(c, hoja_mateo(2), 540, 1190, .9, -4); manos(c, 540, 1190, 340, 54)
    return c

T_E0 = WI("J04", 5)
E_PTS = _poli([(392, 722), (395, 664), (409, 692), (421, 676), (428, 726), (454, 698)], 9, 31, 2.6)      # la M le sale torcida sobre la 3.ª punteada
@esc(WI("J04", 5) - .1)
def escondidas(T, t0):
    c = _mesa(T, t0, 1.05); tr, s = pagM(c, 4.2, 400, 694, 470, 900); cray(c, tr, s, W_PTS); cray(c, tr, s, M_PTS)
    u = u_(T, T_E0, 1.1); pts = parcial(E_PTS, u); cray(c, tr, s, pts)
    mano(c, tr(pts[-1]) if pts else tr(E_PTS[0]), T, .8)
    oscurecer(c, (8, 12, 46), 120); g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((40, 480, 900, 1320), fill=(255, 232, 170, 105)); c.alpha_composite(g.filter(ImageFilter.GaussianBlur(70)))
    return c

G_PTS = _poli([(380, 660), (470, 730), (390, 735), (480, 665), (400, 700), (470, 700)], 10, 33, 4)
@esc(S("J05") - .2)
def no_sale(T, t0):
    c = _mesa(T, t0, 1.1); tr, s = pagM(c, 4.6, 410, 694, 500, 880); cray(c, tr, s, M_PTS); cray(c, tr, s, E_PTS)
    a, b = tr((372, 644)), tr((470, 746)); lapiz_rojo(c, (a[0], a[1], b[0], b[1]), u_(T, t0 + .15, .35), 15, 6)
    k = pop(T, WI("J05", 5) - .05, .2)
    if k > 0: tiza(c, "✗", 820, 520, 240 * k, ROJO, 8, f=DJ, stroke=3, borde=True)
    return view(c, 540, 880, 1 + .08 * u_(T, t0, 2))

@esc(WI("J05", 6) - .12)
def explota(T, t0):
    c = _mesa(T, t0, 1.1); tr, s = pagM(c, 3.6, 400, 694, 500, 880); cray(c, tr, s, M_PTS); cray(c, tr, s, E_PTS)
    cray(c, tr, s, parcial(G_PTS, u_(T, t0 + .05, .45)), w=9)
    return view(c, 540, 880, 1.04 + .1 * u_(T, t0, 1.2))

@esc(S("J06") - .22)
def grito(T, t0):
    c = bg("bg_cocina", T, t0, 1.4, 1.5, 3, .5, .42)
    mateo(c, "enojado", 520 + 12 * math.sin(T * 38) * (1 - u_(T, t0, .9)), 760, 1.5 + .1 * u_(T, t0, 1.5), T, "J06", blink=False)
    u = u_(T, t0, .7); volando(c, 760 + 260 * u, 1100 - 500 * u, 30 + 400 * u, .5)
    return c

@esc(WI("J06", 4) - .08, True)
def grito2(T, t0):
    c = bg("bg_cocina", T, t0, 1.7, 1.76, 3, .5, .4); mateo(c, "llora", 540 + 6 * math.sin(T * 30), 930, 1.6, T, "J06", blink=False)
    k = pop(T, t0 + .02, .18)
    if k > 0: tiza(c, "¡NUNCA!", 500, 400, 128 * k, ROJO, -5 + 3 * math.sin(T * 25), f=F_BAL, stroke=3, borde=True)
    return c

@esc(E("J06") + .12)
def silencio(T, t0):
    """Un respiro: Mateo callado, con la mirada baja (sin repetir la hoja)."""
    c = bg("bg_cocina", T, t0, 1.4, 1.46, 3, .5, .42); mateo(c, "triste", 540, 740, 1.25, T, blink=False)
    k = pop(T, t0 + .25, .25)
    if k > 0: tiza(c, "…", 800, 430, 170 * k, TIZA, 0, f=F_BAL, stroke=3, borde=True)
    return view(c, 540, 760, 1.0 + .07 * u_(T, t0, 1.1))

@esc(S("J07") - .2)
def cambias(T, t0):
    c = _mesa(T, t0, 1.0); u = ease((T - (WI("J07", 1))) / .5); paste_rot(c, hoja_mateo(2), 520 - 1100 * u, 900, 1.15, -9 - 20 * u)
    ub = ease((T - (WI("J07", 3) - .1)) / .4)
    if ub > 0: bolsa(c, 1250 - 600 * ub, 760, 1.25, 8 - 4 * ub)
    return c

T_H0 = WI("J07", 5) - .1
@esc(WI("J07", 4) - .1)
def vuelca(T, t0):
    c = _mesa(T, t0, 1.0); u = ease((T - T_H0) / .6)
    if u > 0: harina(c, T, t0, 470, 1000, 380, 260, k=.25 + .75 * u)
    bolsa(c, 640, 560 + 20 * math.sin(T * 14), 1.2, 118)
    d = ImageDraw.Draw(c)
    if T >= T_H0 - .1:
        for i in range(14):
            ph = ((T - T_H0) * 2.2 + i / 14) % 1; x = 430 + 70 * math.sin(i * 2.1); d.ellipse((x - 26, 640 + 330 * ph - 26, x + 26, 640 + 330 * ph + 26), fill=HAR)
    return c

@esc(E("J07") + .1)
def nube(T, t0):
    c = _mesa(T, t0, 1.0); harina(c, T, t0); r = random.Random(3); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); u = u_(T, t0, 1.0)
    for i in range(16):
        a = r.uniform(0, 6.28); rr = (120 + 520 * u) * r.uniform(.5, 1); s_ = 90 + 120 * r.random(); d.ellipse((500 + rr * math.cos(a) - s_, 880 + rr * math.sin(a) * .8 - s_, 500 + rr * math.cos(a) + s_, 880 + rr * math.sin(a) * .8 + s_), fill=HAR + (int(150 * (1 - u)),))
    c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(24)))
    return c

@esc(S("J08") - .2)
def fria(T, t0):
    c = bg("bg_cocina", T, t0, 1.4, 1.46, 3, .5, .42); j = 20 * abs(math.sin((T - t0) * 9)) * (1 - u_(T, t0, 1.2))
    mateo(c, "feliz", 540, 700 - j, 1.45, T, "J08"); manchas(c, 540, 700 - j, 1.45); d = ImageDraw.Draw(c)
    return c

T_D = [WI("J09", i) - .02 for i in (3, 4, 5, 6)]
D_STK = [HM[0][0:9], HM[0][8:17], HM[0][16:25], HM[0][24:33]]
def _dedo_m(c, T):
    tip = D_STK[0][0]
    for i in range(4):
        u = u_(T, T_D[i], .45); pts = parcial(D_STK[i], u); surco(c, pts)
        if pts: tip = pts[-1]
    return tip
@esc(WI("J08", 1) - .05, True)
def fria2(T, t0):
    c = bg("bg_cocina", T, t0, 1.7, 1.76, 3, .5, .4); mateo(c, "feliz", 540, 800, 1.85 + .06 * u_(T, t0, 2), T, "J08"); manchas(c, 540, 800, 1.85); return c

@esc(S("J09") - .2)
def con_dedo(T, t0):
    c = _mesa(T, t0, 1.0); harina(c, T, t0); tip = _dedo_m(c, T)
    if T < T_D[0]: tip = (tip[0], tip[1] - 120 * (1 - u_(T, t0, T_D[0] - t0)))
    dedo(c, tip, T if T >= T_D[0] else 0, .9); return view(c, 300, 800, 1.5)

@esc(T_D[0] - .1, True)
def con_dedo_b(T, t0):
    c = _mesa(T, t0, 1.0); harina(c, T, t0); tip = _dedo_m(c, T); dedo(c, tip, T, .9); return view(c, 300, 800, 1.72 + .08 * u_(T, t0, 1.5))

@esc(WI("J09", 5) - .08, True)
def con_dedo2(T, t0):
    c = _mesa(T, t0, 1.0); harina(c, T, t0); tip = _dedo_m(c, T); dedo(c, tip, T if T < T_D[3] + .45 else 0, .9)
    return view(c, 280, 790, 1.9 - .15 * u_(T, t0, 1.5))

def _emes(c, T, n, upto=None):
    harina(c, T, 0)
    for i in range(n): surco(c, HM[i] if upto is None or i < n - 1 else parcial(HM[i], upto))
@esc(S("J10") - .2)
def una(T, t0):
    """Recompensa: la primera M en la harina."""
    c = _mesa(T, t0, 1.0); _emes(c, T, 1); c = view(c, 300, 800, 1.45 + .1 * u_(T, t0, 1.5)); chispas(c, 420, 860, T, t0 + .1, 7, 330)
    return c

@esc(WI("J10", 2) - .1)
def dos(T, t0):
    c = _mesa(T, t0, 1.0); u = u_(T, t0 + .05, .5); _emes(c, T, 2, u); dedo(c, parcial(HM[1], u)[-1] if u > 0 else HM[1][0], T, .9)
    return view(c, 520, 780, 1.3)

@esc(WI("J10", 3) - .1)
def tres(T, t0):
    """Plano general: la mamá cuenta tres… y en la harina hay cuatro (el error escondido, nadie lo dice)."""
    c = _mesa(T, t0, 1.0); _emes(c, T, 4); return view(c, 500, 900, 1.02 + .06 * u_(T, t0, 2))

T_BR = WI("J10", 4) - .1
@esc(T_BR)
def se_cruza(T, t0):
    """El siguiente conflicto entra mientras aún celebra: se cruza de brazos."""
    c = bg("bg_cocina", T, t0, 1.3, 1.36, 3, .5, .45); tb = WI("J10", 8) - .1
    mateo(c, "feliz" if T < tb else "neutral_x", 540, 720, 1.3, T, blink=False); manchas(c, 540, 720, 1.3)
    return c

@esc(WI("J10", 8) - .1, True)
def se_cruza2(T, t0):
    c = bg("bg_cocina", T, t0, 1.6, 1.66, 3, .5, .42); mateo(c, "neutral_x", 540, 740, 1.5 + .08 * ease((T - t0) / .25), T, blink=False); manchas(c, 540, 740, 1.5)
    return c

@esc(S("J11") - .2)
def que_me_das(T, t0):
    c = bg("bg_cocina", T, t0, 1.5, 1.56, 3, .5, .42); mateo(c, "neutral_x", 540, 760, 1.42 + .06 * u_(T, t0, 2), T, "J11", blink=False); manchas(c, 540, 760, 1.42)
    return c

@esc(WI("J11", 3) - .08)
def la_mano(T, t0):
    c = bg("bg_cocina", T, t0, 1.3, 1.36, 3, .5, .45); hx, hy, sc = 330, 640, 1.2
    mateo(c, "feliz_tira", hx, hy, sc, T, "J11", blink=False); manchas(c, hx, hy, sc)
    u = ease((T - t0) / .25); x, y = brazo_tira(c, hx + 224 * sc, hy + 372 * sc, 75 - 35 * u, 10 - 80 * u + 3 * math.sin(T * 9), sc, False)
    k = pop(T, t0 + .25, .2)
    if k > 0: tiza(c, "?", x + 6, y - 170 - 10 * math.sin(T * 8), 190 * k, AMA, 8, f=F_BAL, stroke=3, borde=True)
    return c

@esc(S("J12") - .4)
def mientras(T, t0):
    c = pizarra(); tiza(c, "MIENTRAS", 500, 780, 190 * pop(T, t0 + .05, .25), AMA, -4, f=F_BAL)
    if T >= t0 + .22: tiza(c, "TANTO…", 500, 990, 190 * pop(T, t0 + .22, .25), TIZA, -4, f=F_BAL)
    return c

@esc(WI("J12", 2) - .05)
def escuela(T, t0): return bg("bg_escuela", T, t0, 1.05, 1.3, 2.2, .5, .45)

@esc(WI("J12", 4) - .1)
def tacha(T, t0):
    c = pizarra(); d = ImageDraw.Draw(c); x0, y0, cw, ch_ = 70, 440, 136, 136
    sombra(c, (x0 - 26, y0 - 110, x0 + 6 * cw + 26, y0 + 5 * ch_ + 26), 18, 110, 14)
    d.rounded_rectangle((x0 - 26, y0 - 110, x0 + 6 * cw + 26, y0 + 5 * ch_ + 26), 18, fill=CREMA, outline=OL, width=8)
    d.rounded_rectangle((x0 - 26, y0 - 110, x0 + 6 * cw + 26, y0 - 14), 18, fill=ROJO, outline=OL, width=8); d.text((x0 + 3 * cw, y0 - 62), "30 DÍAS · MATEO", font=font(F_BAL, 58), fill=CREMA, anchor="mm")
    for i in range(30):
        x, y = x0 + (i % 6) * cw, y0 + (i // 6) * ch_; d.rectangle((x + 6, y + 6, x + cw - 6, y + ch_ - 6), outline=(190, 186, 170), width=4)
        d.text((x + cw / 2, y + ch_ / 2), str(i + 1), font=font(F_ANTON, 58), fill=OL if i > 1 else (150, 150, 160), anchor="mm")
    tx = WI("J12", 4) - .02
    for n in range(2):
        a = (x0 + n * cw + 18, y0 + 18); b = (x0 + (n + 1) * cw - 18, y0 + ch_ - 18)
        for j, (p, q) in enumerate(((a, b), ((b[0], a[1]), (a[0], b[1])))):
            u = 1 if n == 0 else u_(T, tx + j * .16, .14)
            if u > 0: d.line((p[0], p[1], p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u), fill=ROJO, width=18)
    return view(c, 480, 800, 1 + .05 * u_(T, t0, 2.5))

@esc(WI("J12", 8) - .1)
def sobre(T, t0):
    c = bg("bg_cocina", T, t0, 1.4, 1.5, 3, .7, .3); oscurecer(c, (10, 14, 40), 120); z = .95 + .1 * u_(T, t0, 2.5)
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((0, 420, 960, 1300), fill=(255, 226, 150, 110)); c.alpha_composite(g.filter(ImageFilter.GaussianBlur(70)))
    sombra(c, (480 - 410 * z, 860 - 270 * z, 480 + 410 * z, 860 + 270 * z), 20, 130, 20); paste_rot(c, sobre_img(), 480, 860, z, -3 + 1.5 * math.sin((T - t0) * 3))
    k = pop(T, WI("J12", 12) - .05, .22)
    if k > 0: rotulo(c, "CERRADO", 640, 1140, 78, ROJO, CREMA, -8, k=k)
    return c

@lru_cache(1)
def _mitades():
    A2 = bg("bg_cocina", 0, 0, 1.3, 1.3, 1, .5, .45); A2.alpha_composite(Image.new("RGBA", (W, H), NAR + (70,)))
    B2 = bg("bg_cuarto", 0, 0, 1.3, 1.3, 1, .5, .5); B2.alpha_composite(Image.new("RGBA", (W, H), (130, 90, 190, 70)))
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon([(0, 0), (512, 0), (428, H), (0, H)], fill=255); return A2, B2, m
T_A, T_B, T_C = WI("J13", 0) - .05, WI("J13", 8) - .05, S("J14") - .05
T_TU = WI("J14", 5) - .08
@esc(S("J13") - .25)
def final(T, t0):
    """Pantalla partida: cada opción con su consecuencia. Sin "mañana": las tarjetas dicen "¿EN EL DÍA 4?"."""
    A2, B2, m = _mitades(); a = A2.copy(); b = B2.copy()
    mateo(a, "feliz", 245, 1490, .92, T, blink=False); mateo(b, "neutral", 720 + 4 * math.sin(T * 3), 1490, .92, T, blink=False)
    if T < T_B: b.alpha_composite(Image.new("RGBA", (W, H), (10, 14, 40, int(150 * (1 - u_(T, T_B - .2, .2))))))
    ka = u_(T, T_B, .2) * (1 - u_(T, T_C - .2, .2))      # mientras se habla de la B, la A queda en oscuro
    c = b; c.paste(a, (0, 0), m); d = ImageDraw.Draw(c); d.line((512, 0, 428, H), fill=CREMA, width=16)
    pa = 1 + .07 * math.sin((T - T_C) * 10) if WI("J14", 1) - .08 <= T < WI("J14", 2) else 1; pb = 1 + .07 * math.sin((T - T_C) * 10) if WI("J14", 3) - .08 <= T < T_TU else 1
    tarjeta(c, 247, 660, .74 * pop(T, T_A, .3) * pa, "PREMIO", NAR, "premio", 3, sub="¿EN EL DÍA 4?")
    tarjeta(c, 719, 660, .74 * pop(T, T_B, .3) * pb, "SIN PREMIO", MORA, "sinpremio", -3, sub="¿EN EL DÍA 4?")
    dos_lineas(c, 243, 950, "escribe por", "el dulce", 2, pop(T, WI("J13", 3) - .05, .25)); dos_lineas(c, 715, 950, "escribe porque", "él quiere", -2, pop(T, WI("J13", 14) - .05, .25))
    if ka > 0: c.paste(Image.alpha_composite(c, Image.new("RGBA", (W, H), (10, 14, 40, int(150 * ka)))), (0, 0), m); d = ImageDraw.Draw(c); d.line((512, 0, 428, H), fill=CREMA, width=16)
    kv = pop(T, T_B + .1, .25)
    if kv > 0:
        r = 65 * kv; d = ImageDraw.Draw(c); d.ellipse((483 - r, 659 - r, 483 + r, 659 + r), fill=AMA, outline=OL, width=8); d.text((483, 657), "vs", font=font(F_BAL, 78 * kv), fill=OL, anchor="mm")
    kt = pop(T, T_TU, .25)
    if kt > 0: paste_rot(c, _coment(3, 540), 478, 356 - 30 * (1 - ease((T - T_TU) / .25)), kt, -3)     # "Tu comentario puede salir…": asoma un comentario real
    return c

SC.sort(key=lambda x: x[0])
SCENES = [(t, f) for t, f, s_ in SC]; SUAVES = {t for t, f, s_ in SC if s_}
IMPACTS = [.05, WI("J02", 8), WI("J05", 6), WI("J06", 4), WI("J10", 8)]

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
