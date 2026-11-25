"""Temporada "Mateo: 30 días para no repetir" · DÍA 2 — La M dormida (ganó SECRETO).
Mundo visual nuevo (pizarra verde, tiza amarilla, rojo de corrección), barra FALTAN X DÍAS + imanes M-A-T-E-O,
subtítulos palabra a palabra y cierre con dos tarjetas de una palabra.
Uso: python3 render_d1.py still 1 5 | scenes [i...] | info"""
import os, sys, math, json, subprocess, random
from functools import lru_cache
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["GUION"] = "guion_d2"; os.environ["VOZDIR"] = os.path.join(HERE, "voz_d2")
sys.path.insert(0, HERE)
import importlib.util
_spec = importlib.util.spec_from_file_location("R", os.path.join(HERE, "..", "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

R.LAY = os.path.join(HERE, "layers"); R.layer.cache_clear(); R.scaled.cache_clear()
TMP = os.path.join(HERE, "tmp_d2"); os.makedirs(TMP, exist_ok=True)
W, H, FPS = R.W, R.H, R.FPS
put, ease, clamp, back, font, mouth, bg = R.put, R.ease, R.clamp, R.back, R.font, R.mouth, R.bg
F_ANTON = R.F_ANTON
MF = os.path.join(HERE, "..", "mateo-pov", "fonts")
F_HAND = os.path.join(MF, "Caveat.ttf"); F_BAL = os.path.join(MF, "Baloo2-ExtraBold.ttf"); F_AND = os.path.join(MF, "Andika-Bold.ttf")
PI_ = math.pi
OL = (29, 22, 48); PIZ = (36, 82, 66); PIZ2 = (25, 60, 48); TIZA = (246, 244, 232); AMA = (255, 212, 84)
ROJO = (226, 72, 59); CREMA = (255, 253, 244); AZUL = (63, 127, 208); MADERA = (176, 122, 72)
DIAS_FALTAN = 29; LETRAS_ON = ""          # Día 1: ninguna letra dominada

# ---------------------------------------------------------------- tiempos
R.GAP.clear()
R.GAP.update({"H02": .12, "H03": .2, "H04": .2, "H05": .25, "H06": .25, "H07": .15, "H08": .25, "H09": .25, "H10": .6, "H11": .2,
              "H12": .25, "H13": .45, "H14": .3, "H15": .3, "H16": .35, "H17": .5, "H18": .45, "H19": .45, "H20": .4, "H21": .25})
R.TL, R.TOTAL = R.timeline()
R.TL = {k: (a - .1, b - .1) for k, (a, b) in R.TL.items()}      # la voz arranca en el fotograma 0
R.TOTAL = R.TL["H21"][1] + .1                                    # corte en seco ~0,1 s tras la última palabra
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
T_HUD = S("H03") - .1
def draw_hud(c, T):
    if T < T_HUD: return
    y = int(122 - 320 * (1 - ease((T - T_HUD) / .35)))
    if y >= 0: c.alpha_composite(BARRA, (10, y))
    elif -y < BARRA.height: c.alpha_composite(BARRA, (10, 0), (0, -y, BARRA.width, BARRA.height))

# ---------------------------------------------------------------- subtítulos palabra a palabra
T_FINAL = S("H20") - .25
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

# ================================================================ ESCENAS (un plano cada ~2 s)
@esc(0)
def gancho(T, t0):
    """Primer fotograma: la cara de Mateo junto al error (la M al revés, rodeada en rojo)."""
    c = bg("bg_cocina", T, t0, 1.3, 1.4, 3, .5, .45)
    mateo(c, "susto", 330 + 5 * math.sin(T * 17) * (1 - u_(T, 0, .6)), 880, 1.15 + .04 * u_(T, 0, 2), T, blink=False)
    h = Image.new("RGBA", (W, H), (0, 0, 0, 0)); paste_rot(h, hoja_img(), 760, 1010, .62, -7 + 2 * math.sin(T * 5))
    t = Image.new("RGBA", (300, 300), (0, 0, 0, 0)); ImageDraw.Draw(t).text((150, 150), "M", font=font(F_AND, 230), fill=VERDE + (255,), anchor="mm")
    h.alpha_composite(t.rotate(187, resample=Image.BICUBIC), (610, 860)); c.alpha_composite(h)
    lapiz_rojo(c, (600, 850, 920, 1170), u_(T, .1, .45), 14)
    k = pop(T, .5, .25)
    if k > 0: rotulo(c, "GANÓ: SECRETO", 330, 250, 62, AMA, OL, -4, k=k)
    return c

@esc(WI("H01", 7) - .1)
def reves(T, t0):
    c = _mesa(T, t0, 1.05); paste_rot(c, hoja_img(), 540, 840, 1.0, 0)
    a = 180 * ease((T - (WI("H01", 9) - .05)) / .3)
    t = Image.new("RGBA", (560, 560), (0, 0, 0, 0)); ImageDraw.Draw(t).text((280, 280), "M", font=font(F_AND, 430), fill=VERDE + (255,), anchor="mm")
    paste_rot(c, t, 540, 840, 1.0, a)
    k = pop(T, WI("H01", 11) - .05, .22)
    if k > 0: lapiz_rojo(c, (300, 600, 780, 1080), u_(T, WI("H01", 11) - .05, .3), 16, 2); tiza(c, "?", 860, 520, 260 * k, ROJO, 12, stroke=3, borde=True)
    return view(c, 540, 840, 1 + .12 * u_(T, t0, 2))

@esc(S("H02") - .1)
def primo_flash(T, t0):
    c = bg("bg_puerta", T, t0, 1.2, 1.3, 2, .5, .4); u = ease((T - t0) / .28)
    tomas(c, "feliz", 540, 760 + 700 * (1 - u), 1.3, T)
    k = pop(T, t0 + .3, .22)
    if k > 0: rotulo(c, "SU PRIMO", 760, 440, 70, AZUL, CREMA, 6, k=k)
    return c

@esc(S("H03") - .15)
def faltan(T, t0):
    c = pizarra(); tn = WI("H03", 1) - .08; u = ease((T - tn) / .25)
    tiza(c, "FALTAN", 540, 520, 170 * pop(T, t0 + .05, .22), TIZA, -2, f=F_BAL)
    if u < 1: tiza(c, "30", 540, 830 - 260 * u, 480, TIZA, 0, f=F_ANTON, alpha=int(255 * (1 - u)))
    if u > 0: tiza(c, "29", 540, 1090 - 260 * u, 480 * (1 + .08 * math.exp(-(T - tn - .25) * 8) if T > tn + .25 else 1), AMA, 0, f=F_ANTON, alpha=int(255 * u))
    k = pop(T, WI("H03", 2) - .05, .22)
    if k > 0: tiza(c, "DÍAS", 540, 1140, 180 * k, TIZA, -2, f=F_BAL)
    return c

@esc(WI("H03", 6) - .1)
def eligieron(T, t0):
    c = pizarra(); k = pop(T, t0, .28)
    tiza(c, "USTEDES ELIGIERON", 540, 400, 92 * k, TIZA, -2, f=F_BAL)
    tarjeta(c, 540, 830, 1.12 * k * (1 + .03 * math.sin((T - t0) * 8)), "SECRETO", (150, 110, 200), "secreto", -3, sub="GANÓ EL VOTO")
    ks = pop(T, WI("H03", 11) - .05, .2)
    if ks > 0: rotulo(c, "✔ GANÓ", 800, 560, 84, ROJO, CREMA, 12, f=DJ, k=ks)
    return c

@esc(S("H04") - .15)
def mochila(T, t0):
    c = bg("bg_cuarto", T, t0, 1.25, 1.35, 3, .5, .6); u = ease((T - (WI("H04", 2) - .1)) / .45)
    paste_rot(c, nota_img(), 560, 900 - 330 * u, .5, 8 - 4 * u)
    put(c, "mochila", 540, 1080, .52)
    if u > 0: manos(c, 560, 640 - 330 * u + 330, 150, 50)
    return view(c, 540, 860, 1.05 + .12 * u_(T, t0, 2.5))

@esc(WI("H04", 4) - .1)
def nota_cerca(T, t0):
    c = bg("bg_cuarto", T, t0, 1.5, 1.6, 3, .5, .5); oscurecer(c, (10, 14, 40), 110)
    z = .86 + .06 * u_(T, t0, 2); cy = 820; r = -4 + 1.5 * math.sin((T - t0) * 4)
    sombra(c, (540 - 440 * z, cy - 560 * z, 540 + 440 * z, cy + 560 * z), 18, 130, 20); paste_rot(c, nota_img(), 540, cy, z, r)
    b = NOTA_REPITE; lapiz_rojo(c, (540 + b[0] * z, cy + b[1] * z, 540 + b[2] * z, cy + b[3] * z), u_(T, t0 + .2, .4), 15, 3)
    return c

@esc(S("H05") - .2)
def dolido(T, t0):
    c = bg("bg_cocina", T, t0, 1.3, 1.36, 3, .5, .45)
    mateo(c, "triste", 540, 620, 1.3, T, "H05")
    paste_rot(c, nota_img(), 540, 1150, .33, -6 + 2 * math.sin((T - t0) * 3)); manos(c, 540, 1160, 190, 54)
    return c

@esc(WI("H05", 1) - .05, True)
def dolido2(T, t0):
    c = bg("bg_cocina", T, t0, 1.6, 1.66, 3, .5, .4); mateo(c, "triste", 540, 760, 1.75 + .08 * u_(T, t0, 2.5), T, "H05"); return c

@esc(S("H06") - .2)
def libro(T, t0):
    c = _mesa(T, t0); u = ease((T - t0) / .45)
    pagM(c, .78, 621, 520, 540, 900 + 1100 * (1 - u))
    uc = ease((T - (WI("H06", 2) - .1)) / .4)
    if uc > 0: put(c, "crayola", 800 + 500 * (1 - uc), 1500, .5, rot=60 + 200 * (1 - uc))
    return c

@esc(WI("H06", 4) - .1)
def primera(T, t0):
    c = _mesa(T, t0, 1.1); z = 2.1 + .25 * u_(T, t0, 2.2)
    pagM(c, z, 255, 420, 540, 900)
    k = pop(T, WI("H06", 7) - .08, .25)
    if k > 0:
        d = ImageDraw.Draw(c); r = 250 * k + 10 * math.sin(T * 9); d.ellipse((540 - r - 80, 720 - r, 540 + r - 80, 720 + r), outline=ROJO, width=14)
    return c

@esc(S("H07") - .15)
def reloj(T, t0):
    c = bg("bg_cocina", T, t0, 1.5, 1.56, 3, .3, .2); oscurecer(c, (255, 240, 200), 40); d = ImageDraw.Draw(c); cx, cy, r = 540, 760, 330
    d.ellipse((cx - r - 26, cy - r - 26, cx + r + 26, cy + r + 26), fill=AZUL, outline=OL, width=8); d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=CREMA, outline=OL, width=8)
    for i in range(12):
        a = i * PI_ / 6; d.line((cx + (r - 50) * math.sin(a), cy - (r - 50) * math.cos(a), cx + (r - 18) * math.sin(a), cy - (r - 18) * math.cos(a)), fill=OL, width=12 if i % 3 == 0 else 6)
    d.text((cx + (r - 105) * math.sin(5 * PI_ / 6), cy - (r - 105) * math.cos(5 * PI_ / 6)), "5", font=font(F_ANTON, 120), fill=ROJO, anchor="mm")
    u = ease((T - t0) / .9); am = 2 * PI_ * (.55 + .45 * u); ah = (4.55 + .45 * u) * PI_ / 6
    d.line((cx, cy, cx + 150 * math.sin(ah), cy - 150 * math.cos(ah)), fill=OL, width=24); d.line((cx, cy, cx + 250 * math.sin(am), cy - 250 * math.cos(am)), fill=ROJO, width=14)
    d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=OL)
    k = pop(T, WI("H07", 4) - .05, .22)
    if k > 0: rotulo(c, "LLEGA TOMÁS", 540, 1200, 78, AZUL, CREMA, -3, k=k)
    return c

@esc(S("H08") - .2)
def agarra(T, t0):
    c = bg("bg_cocina", T, t0, 1.5, 1.6, 3, .5, .4); tl = WI("H08", 2)
    mateo(c, "neutral" if T < tl else "concentra", 540, 760, 1.5 + .05 * u_(T, t0, 2) + .18 * ease((T - tl) / .25), T)
    if T < tl + .25: put(c, "crayola", 720, 1250, .42, rot=30 + 3 * math.sin(T * 40)); ImageDraw.Draw(c).ellipse((640, 1250, 780, 1380), fill=PIEL, outline=OL, width=6)
    return c

T_W0, T_W1 = WI("H08", 5) - .05, WI("H08", 9) + .1
@esc(WI("H08", 4) - .1)
def escribeW(T, t0):
    c = _mesa(T, t0, 1.05); tr, s = pagM(c, 3.8, 238, 694, 500, 900); u = u_(T, T_W0, T_W1 - T_W0)
    pts = parcial(W_PTS, u); cray(c, tr, s, pts)
    tip = tr(pts[-1]) if pts else (tr(W_PTS[0])[0] - 20, tr(W_PTS[0])[1] - 80 * (1 - u_(T, t0, T_W0 - t0)))
    mano(c, tip, T if 0 < u < 1 else 0, .8); return c

@esc(WI("H08", 9) - .08)
def patas(T, t0):
    c = _mesa(T, t0, 1.1); tr, s = pagM(c, 4.6, 238, 694, 540, 880); cray(c, tr, s, W_PTS)
    a, b = tr((186, 644)), tr((290, 744)); lapiz_rojo(c, (a[0], a[1], b[0], b[1]), u_(T, t0 + .12, .35), 15, 5)
    k = pop(T, WI("H08", 10), .22)
    if k > 0: tiza(c, "?", 850, 520, 260 * k, ROJO, 10, f=F_BAL, stroke=3, borde=True)
    return view(c, 540, 880, 1 + .08 * u_(T, t0, 2))

@esc(S("H09") - .2)
def terco(T, t0):
    c = bg("bg_cocina", T, t0, 1.3, 1.36, 3, .5, .45)
    mateo(c, "neutral", 540 + 10 * math.sin((T - t0) * 9) * (1 - u_(T, t0, .8)), 640, 1.35 + .1 * u_(T, t0, 1.5), T, "H09"); return c

@esc(WI("H09", 2) - .1)
def dormida(T, t0):
    c = pizarra(); bob = 12 * math.sin((T - t0) * 2.4)
    tiza(c, "M", 540, 860 + bob, 640, VERDE, 180 + 3 * math.sin((T - t0) * 2.4), f=F_AND, stroke=4)
    d = ImageDraw.Draw(c)
    for sx in (-1, 1): d.arc((540 + sx * 100 - 46, 800 + bob, 540 + sx * 100 + 46, 860 + bob), 0, 180, fill=TIZA, width=10)
    d.arc((500, 880 + bob, 580, 930 + bob), 20, 160, fill=TIZA, width=8)
    for i in range(3):
        ph = ((T - t0) * .9 + i * .33) % 1; tiza(c, "Z", 800 + 90 * ph + i * 30, 560 - 220 * ph, 70 + 90 * ph, AMA, 12, f=F_BAL, alpha=int(255 * (1 - ph) ** .6))
    return c

@esc(S("H10") - .2)
def truco(T, t0):
    c = pizarra(); k = pop(T, t0 + .05, .25); d = ImageDraw.Draw(c)
    if k > 0:
        r = 150 * k; g = 30 * (1 + math.sin(T * 10))
        d.ellipse((540 - r - g, 640 - r - g, 540 + r + g, 640 + r + g), outline=AMA, width=6); d.ellipse((540 - r, 640 - r, 540 + r, 640 + r), fill=AMA, outline=OL, width=8)
        d.rounded_rectangle((540 - 60 * k, 640 + r - 14, 540 + 60 * k, 640 + r + 6 + 70 * k), 8, fill=(190, 196, 210), outline=OL, width=7)
        tiza(c, "EL TRUCO", 540, 1020, 170 * pop(T, WI("H10", 3) - .1, .22), TIZA, -3, f=F_BAL) if T >= WI("H10", 3) - .1 else None
    return c

MONT = [(120, 1260), (330, 560), (540, 980), (750, 560), (960, 1260)]
@esc(WI("H10", 5) - .1)
def montanas(T, t0):
    c = Image.new("RGBA", (W, H), (150, 208, 240, 255)); d = ImageDraw.Draw(c)
    for i in range(24): d.rectangle((0, i * 80, W, i * 80 + 80), fill=(150 + i * 3, 208 + i, 240 - i))
    sy = 420 - 60 * u_(T, t0, 3); d.ellipse((760, sy - 90, 940, sy + 90), fill=AMA, outline=OL, width=7)
    up = ease((T - t0) / .4); off = 900 * (1 - up)
    P = [(x, y + off) for x, y in MONT]
    d.polygon([P[0], P[1], P[2], (540, 1260 + off)], fill=(92, 176, 104), outline=OL); d.polygon([(540, 1260 + off), P[2], P[3], P[4]], fill=(72, 156, 92), outline=OL)
    for (px, py) in (P[1], P[3]): d.polygon([(px, py), (px - 72, py + 236), (px - 20, py + 190), (px + 20, py + 240), (px + 70, py + 232)], fill=CREMA, outline=OL)
    d.rectangle((0, min(H - 1, 1250 + off), W, H), fill=(120, 190, 110)); d.line((0, 1250 + off, W, 1250 + off), fill=OL, width=7)
    um = u_(T, WI("H10", 6) - .05, .55)
    if um > 0:
        pts = parcial(_poli(P, 14, 3, 0), um); d.line(pts, fill=ROJO, width=30, joint="curve")
        for p in (pts[0], pts[-1]): d.ellipse((p[0] - 15, p[1] - 15, p[0] + 15, p[1] + 15), fill=ROJO)
    for i, px in enumerate((330, 750)):
        k = pop(T, WI("H10", 8) - .15 + i * .15, .2)
        if k > 0: rotulo(c, str(i + 1), px, 440, 120, AMA, OL, 0, k=k)
    return c

@esc(WI("H10", 9) - .05)
def pag79(T, t0):
    c = _mesa(T, t0, 1.1); im = _pag("p079.png", (40, 150, 1212, 660), 1500); x0 = 60 - 380 * u_(T, t0, 1.6); y0 = 640
    sombra(c, (x0, y0, x0 + im.width, y0 + im.height), 12, 110, 16); c.paste(im, (int(x0), y0))
    return c

T_M = [WI("H11", i) - .02 for i in range(4)]
def _trazos(c, tr, s, T, hasta=4):
    tip = None
    for i in range(hasta):
        u = u_(T, T_M[i], .5 if i < 3 else .4); pts = parcial(M_STK[i], u); cray(c, tr, s, pts)
        if pts and u < 1: tip = tr(pts[-1])
        elif pts: tip = tr(pts[-1])
    return tip
@esc(S("H11") - .2)
def trazaM(T, t0):
    c = _mesa(T, t0, 1.05); tr, s = pagM(c, 4.2, 318, 694, 470, 900); cray(c, tr, s, W_PTS)
    tip = _trazos(c, tr, s, T) or (tr(M_STK[0][0])[0], tr(M_STK[0][0])[1] - 60 * (1 - u_(T, t0, .2)))
    for i, (a, tx) in enumerate(((0, "↑"),)):
        k = pop(T, T_M[i], .2)
        if k > 0 and T < T_M[i] + .7: tiza(c, tx, 860, 560, 220 * k, AMA, 0, f=DJ, stroke=3, borde=True)
    mano(c, tip, T, .8); return c

@esc(WI("H11", 1) - .1, True)
def trazaM_b(T, t0):
    c = _mesa(T, t0, 1.1); tr, s = pagM(c, 4.8, 326, 694, 480, 900); cray(c, tr, s, W_PTS)
    tip = _trazos(c, tr, s, T); mano(c, tip, T if T < T_M[1] + .5 else 0, .8)
    k = pop(T, T_M[1], .2)
    if k > 0: tiza(c, "↓", 860, 520, 220 * k, AMA, 0, f=DJ, stroke=3, borde=True)
    return c

@esc(WI("H11", 2) - .1)
def cara_m(T, t0):
    c = bg("bg_cocina", T, t0, 1.7, 1.76, 3, .5, .4); mateo(c, "concentra", 540, 800, 1.85 + .06 * u_(T, t0, 2), T, "H11")
    k = pop(T, t0 + .1, .2)
    if k > 0: tiza(c, "↑", 860, 520, 220 * k, AMA, 0, f=DJ, stroke=3, borde=True)
    return c

@esc(WI("H11", 3) - .1)
def trazaM2(T, t0):
    c = _mesa(T, t0, 1.1); tr, s = pagM(c, 5.0, 338, 694, 480, 900); cray(c, tr, s, W_PTS)
    tip = _trazos(c, tr, s, T); mano(c, tip, T if T < T_M[3] + .55 else 0, .8)
    k = pop(T, T_M[3], .2)
    if k > 0: tiza(c, "↓", 860, 520, 220 * k, AMA, 0, f=DJ, stroke=3, borde=True)
    return c

@esc(S("H12") + .2)
def ahi(T, t0):
    """Pago del gancho: su primera M, bien hecha."""
    c = _mesa(T, t0, 1.1); tr, s = pagM(c, 4.4, 300, 694, 540, 880); cray(c, tr, s, W_PTS); cray(c, tr, s, M_PTS)
    c = view(c, 660, 880, 1 + .14 * u_(T, t0, 2.5)); chispas(c, 660, 880, T, t0 + .1, 8, 330)
    return c

@esc(WI("H12", 3) - .1)
def orgullo(T, t0):
    c = bg("bg_cocina", T, t0, 1.3, 1.36, 3, .5, .45); jump = 28 * abs(math.sin((T - t0) * 7)) * (1 - u_(T, t0, 1.3))
    mateo(c, "feliz", 540, 600 - jump, 1.35, T); paste_rot(c, hoja_mateo(2), 540, 1150 - jump, 1.0, -5); manos(c, 540, 1150 - jump, 370, 56)
    k = pop(T, t0 + .2, .22)
    if k > 0: tiza(c, "¡MI M!", 820, 400, 120 * k, AMA, 10, f=F_BAL, stroke=2, borde=True)
    return c

@esc(S("H13") - .25)
def timbre(T, t0):
    c = bg("bg_puerta", T, t0, 2.2, 2.3, 2, .12, .42); oscurecer(c, (40, 24, 10), 70); d = ImageDraw.Draw(c); tr_ = WI("H13", 3) - .08; pr = T >= tr_
    sombra(c, (350, 560, 730, 1080), 40, 110, 16)
    d.rounded_rectangle((350, 560, 730, 1080), 44, fill=CREMA, outline=OL, width=9)
    r = 118 - (10 if pr and T < tr_ + .2 else 0); d.ellipse((540 - r, 820 - r, 540 + r, 820 + r), fill=AMA if not pr else (255, 150, 60), outline=OL, width=9)
    if pr:
        for i in range(3):
            ph = ((T - tr_) * 1.8 + i / 3) % 1; rr = 150 + 330 * ph; d.ellipse((540 - rr, 820 - rr, 540 + rr, 820 + rr), outline=AMA + (int(255 * (1 - ph)),), width=10)
        k = pop(T, tr_, .2); tiza(c, "¡DING DONG!", 540, 1230, 130 * k, AMA, -4 + 4 * math.sin(T * 30), f=F_BAL, stroke=3, borde=True)
    else:
        u = ease((T - t0) / (tr_ - t0)); d.ellipse((690 - 240 * u * .5, 1000 - 180 * u * .5, 800 - 240 * u * .5, 1110 - 180 * u * .5), fill=PIEL, outline=OL, width=7)
    return c

@esc(WI("H13", 5) - .05)
def susto(T, t0):
    c = bg("bg_cocina", T, t0, 1.5, 1.56, 3, .5, .42); mateo(c, "susto", 540 + 8 * math.sin(T * 40) * (1 - u_(T, t0, .35)), 780, 1.6, T, blink=False)
    k = pop(T, t0 + .05, .18)
    if k > 0: tiza(c, "!", 850, 440, 260 * k, ROJO, 10, f=F_ANTON, stroke=3, borde=True)
    return c

@esc(S("H14") - .2)
def hola(T, t0):
    c = bg("bg_puerta", T, t0, 1.2, 1.28, 3, .5, .4); tomas(c, "feliz", 540, 650 - 16 * abs(math.sin((T - t0) * 8)) * (1 - u_(T, t0, .8)), 1.3, T, "H14")
    k = pop(T, t0 + .2, .22)
    if k > 0: rotulo(c, "TOMÁS · SU PRIMO", 540, 1210, 64, AZUL, CREMA, -2, k=k)
    return c

@esc(WI("H14", 2) - .08)
def yase(T, t0):
    c = bg("bg_puerta", T, t0, 1.5, 1.56, 3, .5, .36); tomas(c, "feliz", 480, 760, 1.7 + .05 * u_(T, t0, 2), T, "H14")
    u = ease((T - t0) / .25); put(c, "crayola", 850, 1180 - 250 * u, .8, rot=-12 + 6 * math.sin(T * 8)); ImageDraw.Draw(c).ellipse((770, 1260 - 250 * u, 930, 1410 - 250 * u), fill=PIEL, outline=OL, width=6)
    return c

T_T0 = WI("H15", 1) - .05; T_TD = max(.9, WI("H15", 4) + .3 - T_T0)
LX = [220, 372, 524, 676, 828]
def _nombre(c, T, cy=900, upto=None):
    paste_rot(c, hoja_img(), 540, cy, 1.0, 0); d = ImageDraw.Draw(c); n = 0
    for i, ch in enumerate("TOMÁS"):
        if upto is None and T < T_T0 + T_TD * i / 5: break
        d.text((LX[i] - 10, cy - 10), ch, font=font(F_AND, 190), fill=AZULC, anchor="mm"); n += 1
    return n
@esc(S("H15") - .2)
def tomas_escribe(T, t0):
    c = _mesa(T, t0, 1.05); n = _nombre(c, T); u = clamp((T - T_T0) / T_TD); x = LX[0] - 60 + (LX[4] + 80 - LX[0]) * u
    mano(c, (x, 930 + 60 * math.sin(T * 26) * (1 if 0 < u < 1 else 0)), T, .66, "mano_tomas"); return c

@esc(WI("H15", 5) - .1)
def cinco(T, t0):
    c = _mesa(T, t0, 1.1); _nombre(c, T, 900, 5)
    for i in range(5):
        k = pop(T, t0 + .08 + i * .1, .2)
        if k > 0: tiza(c, str(i + 1), LX[i] - 10, 600, 120 * k, AMA, 0, f=F_BAL, stroke=3, borde=True)
    return view(c, 540, 860, 1.12 + .08 * u_(T, t0, 2))

@esc(WI("H15", 7) - .1)
def crono(T, t0):
    c = pizarra(); d = ImageDraw.Draw(c); cx, cy, r = 540, 820, 300; k = pop(T, t0, .25)
    if k > 0:
        r *= k; d.rounded_rectangle((cx - 46, cy - r - 80, cx + 46, cy - r + 10), 12, fill=(190, 196, 210), outline=OL, width=8)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=CREMA, outline=OL, width=12); u = clamp((T - t0) / (E("H15") - t0))
        d.pieslice((cx - r + 30, cy - r + 30, cx + r - 30, cy + r - 30), -90, -90 + 30 * (1 + 4 * u) / 5 * 1.0, fill=ROJO)
        d.text((cx, cy), f"0:0{min(5, int(1 + 5 * u))}", font=font(F_ANTON, 190 * k), fill=OL, anchor="mm")
    return c

@esc(S("H16") - .2)
def su_m(T, t0):
    """Su renglón: la M dormida, su primera M… y una tercera con tres montañas (el error escondido, nadie lo dice)."""
    c = _mesa(T, t0, 1.05); tr, s = pagM(c, 1.7, 452, 694, 540, 900)
    for p in (W_PTS, M_PTS, MP3_PTS, ML_PTS, M3_PTS): cray(c, tr, s, p)
    return view(c, 540, 900, 1 + .1 * u_(T, t0, 2.2))

@esc(WI("H16", 4) - .1)
def su_nombre(T, t0):
    c = _mesa(T, t0, 1.1); paste_rot(c, hoja_tomas(), 540, 880, 1.0, 3); chispas(c, 540, 860, T, t0 + .1, 6, 420, 5)
    return view(c, 540, 880, 1.0 + .1 * u_(T, t0, 2))

@esc(WI("H16", 9) - .1)
def esconde(T, t0):
    c = bg("bg_cocina", T, t0, 1.3, 1.36, 3, .5, .45); u = ease((T - (WI("H16", 10) - .05)) / .7)
    mateo(c, "triste", 540, 640, 1.3, T); y = 1140 + 700 * u
    paste_rot(c, hoja_mateo(3), 540, y, 1.0, -5 - 20 * u); manos(c, 540, y, 370, 56)
    d = ImageDraw.Draw(c); d.rectangle((0, 1560, W, H), fill=MADERA); d.line((0, 1560, W, 1560), fill=OL, width=8)
    return c

@esc(WI("H16", 13) - .08)
def bajo_mesa(T, t0):
    c = Image.new("RGBA", (W, H), (58, 40, 30, 255)); d = ImageDraw.Draw(c)
    d.rectangle((0, 0, W, 430), fill=(120, 80, 46)); d.line((0, 430, W, 430), fill=OL, width=9)
    for x in (70, 900): d.rectangle((x, 430, x + 110, H), fill=(104, 68, 40), outline=OL, width=7)
    for x in (360, 600): d.rounded_rectangle((x, 1380, x + 130, H), 40, fill=(52, 70, 150), outline=OL, width=7)
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((90, 480, 990, 1320), fill=(255, 226, 160, 70)); c.alpha_composite(g.filter(ImageFilter.GaussianBlur(60)))
    u = ease((T - t0) / .3); y = 900 - 500 * (1 - u); wob = 2 * math.sin((T - t0) * 14)
    sombra(c, (130, y - 180, 950, y + 180), 10, 140, 18); paste_rot(c, hoja_mateo(3), 540, y, 1.25, -7 + wob); manos(c, 540, y + 20, 450, 64)
    return view(c, 540, 900, 1 + .1 * u_(T, t0, 2.5))

@esc(S("H17") - .4)
def mientras(T, t0):
    c = pizarra(); tiza(c, "MIENTRAS", 540, 780, 190 * pop(T, t0 + .05, .25), AMA, -4, f=F_BAL)
    if T >= t0 + .22: tiza(c, "TANTO…", 540, 990, 190 * pop(T, t0 + .22, .25), TIZA, -4, f=F_BAL)
    return c

@esc(WI("H17", 2) - .05)
def escuela(T, t0): return bg("bg_escuela", T, t0, 1.05, 1.3, 2.2, .5, .45)

@esc(WI("H17", 5) - .1)
def tacha(T, t0):
    c = pizarra(); d = ImageDraw.Draw(c); x0, y0, cw, ch_ = 96, 440, 148, 142
    sombra(c, (x0 - 26, y0 - 110, x0 + 6 * cw + 26, y0 + 5 * ch_ + 26), 18, 110, 14)
    d.rounded_rectangle((x0 - 26, y0 - 110, x0 + 6 * cw + 26, y0 + 5 * ch_ + 26), 18, fill=CREMA, outline=OL, width=8)
    d.rounded_rectangle((x0 - 26, y0 - 110, x0 + 6 * cw + 26, y0 - 14), 18, fill=ROJO, outline=OL, width=8); d.text((540, y0 - 62), "30 DÍAS · MATEO", font=font(F_BAL, 62), fill=CREMA, anchor="mm")
    for i in range(30):
        x, y = x0 + (i % 6) * cw, y0 + (i // 6) * ch_; d.rectangle((x + 6, y + 6, x + cw - 6, y + ch_ - 6), outline=(190, 186, 170), width=4)
        d.text((x + cw / 2, y + ch_ / 2), str(i + 1), font=font(F_ANTON, 64), fill=OL if i else (150, 150, 160), anchor="mm")
    tx = WI("H17", 7) - .05; a = (x0 + 18, y0 + 18); b = (x0 + cw - 18, y0 + ch_ - 18)
    for j, (p, q) in enumerate(((a, b), ((b[0], a[1]), (a[0], b[1])))):
        u = u_(T, tx + j * .16, .14)
        if u > 0: d.line((p[0], p[1], p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u), fill=ROJO, width=18)
    return view(c, 540, 800, 1 + .06 * u_(T, t0, 2.5))

@esc(S("H18") - .25)
def lento(T, t0):
    c = bg("bg_cuarto", T, t0, 1.3, 1.36, 3, .5, .5); mateo(c, "timido", 540, 660, 1.35, T, "H18"); return c

@esc(WI("H18", 3) - .05, True)
def lento2(T, t0):
    c = bg("bg_cuarto", T, t0, 1.6, 1.66, 3, .5, .45); mateo(c, "triste", 540, 780, 1.8 + .08 * u_(T, t0, 2.5), T, "H18"); return c

@esc(S("H19") - .3)
def faltan2(T, t0):
    c = pizarra(); k = pop(T, t0 + .05, .25)
    tiza(c, "FALTAN", 540, 560, 150 * k, TIZA, -2, f=F_BAL); tiza(c, "29", 540, 850, 460 * k * (1 + .04 * math.sin((T - t0) * 9)), AMA, 0, f=F_ANTON)
    if T >= WI("H19", 2) - .05: tiza(c, "DÍAS", 540, 1130, 170 * pop(T, WI("H19", 2) - .05, .22), TIZA, -2, f=F_BAL)
    return c

@esc(WI("H19", 3) - .1)
def sobre(T, t0):
    c = bg("bg_cocina", T, t0, 1.4, 1.5, 3, .7, .3); oscurecer(c, (10, 14, 40), 120); z = 1.0 + .12 * u_(T, t0, 2.5)
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((40, 420, 1040, 1300), fill=(255, 226, 150, 110)); c.alpha_composite(g.filter(ImageFilter.GaussianBlur(70)))
    sombra(c, (540 - 410 * z, 860 - 270 * z, 540 + 410 * z, 860 + 270 * z), 20, 130, 20); paste_rot(c, sobre_img(), 540, 860, z, -3 + 1.5 * math.sin((T - t0) * 3))
    k = pop(T, WI("H19", 7) - .05, .22)
    if k > 0: rotulo(c, "CERRADO", 760, 1130, 78, ROJO, CREMA, -8, k=k)
    return c

@lru_cache(1)
def _mitades():
    A2 = bg("bg_cocina", 0, 0, 1.3, 1.3, 1, .5, .45); A2.alpha_composite(Image.new("RGBA", (W, H), (60, 150, 90, 70)))
    B2 = bg("bg_cuarto", 0, 0, 1.3, 1.3, 1, .5, .5); B2.alpha_composite(Image.new("RGBA", (W, H), (130, 90, 190, 70)))
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon([(0, 0), (512, 0), (428, H), (0, H)], fill=255); return A2, B2, m
T_A, T_B, T_C = WI("H20", 0) - .05, WI("H20", 11) - .05, S("H21") - .05
@esc(S("H20") - .25)
def final(T, t0):
    """Pantalla partida: cada opción con su consecuencia. Tarjetas dentro de x<900. Corte en seco al terminar la voz."""
    A2, B2, m = _mitades(); a = A2.copy(); b = B2.copy()
    mateo(a, "triste", 245, 1490, .92, T, blink=False); mateo(b, "neutral", 720 + 4 * math.sin(T * 3), 1490, .92, T, blink=False)
    if T < T_B: b.alpha_composite(Image.new("RGBA", (W, H), (10, 14, 40, int(150 * (1 - u_(T, T_B - .2, .2))))))
    c = b; c.paste(a, (0, 0), m); d = ImageDraw.Draw(c); d.line((512, 0, 428, H), fill=CREMA, width=16)
    pa = 1 + .07 * math.sin((T - T_C) * 10) if WI("H21", 1) - .08 <= T < WI("H21", 2) else 1; pb = 1 + .07 * math.sin((T - T_C) * 10) if T >= WI("H21", 3) - .08 else 1
    tarjeta(c, 247, 660, .74 * pop(T, T_A, .3) * pa, "COMPARAR", (86, 176, 110), "comparar", 3)
    tarjeta(c, 719, 660, .74 * pop(T, T_B, .3) * pb, "NUNCA", (150, 110, 200), "nunca", -3)
    dos_lineas(c, 243, 950, "aprende mirando", "a Tomás", 2, pop(T, WI("H20", 3) - .05, .25)); dos_lineas(c, 715, 950, "a su ritmo,", "sin presión", -2, pop(T, WI("H20", 15) - .05, .25))
    kv = pop(T, T_B + .1, .25)
    if kv > 0:
        r = 65 * kv; d = ImageDraw.Draw(c); d.ellipse((483 - r, 659 - r, 483 + r, 659 + r), fill=AMA, outline=OL, width=8); d.text((483, 657), "vs", font=font(F_BAL, 78 * kv), fill=OL, anchor="mm")
    return c

SC.sort(key=lambda x: x[0])
SCENES = [(t, f) for t, f, s_ in SC]; SUAVES = {t for t, f, s_ in SC if s_}
IMPACTS = [WI("H01", 11), WI("H04", 4) + .15, WI("H08", 10), WI("H13", 3), WI("H16", 13) + .2]

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
