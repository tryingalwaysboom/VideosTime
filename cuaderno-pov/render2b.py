"""Monta la Parte 2 de "El cuaderno de la abuela" (ganó B: la abren juntas). Mismo motor que la Parte 1.
tiempos de voz, transiciones) con escenas propias. Uso: python3 render1.py still 1 5 | scenes [i...] | info"""
import os, sys, math, json, subprocess, random
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["GUION"] = "guion_cuaderno2b"; os.environ["VOZDIR"] = os.path.join(HERE, "voz2b")
sys.path.insert(0, HERE); sys.path.append(os.path.join(HERE, "..", "taller-pov"))
import importlib.util
_spec = importlib.util.spec_from_file_location("R", os.path.join(HERE, "..", "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

R.LAY = os.path.join(HERE, "layers"); R.layer.cache_clear(); R.scaled.cache_clear()
TMP = os.path.join(HERE, "tmp2b"); os.makedirs(TMP, exist_ok=True)
W, H, FPS = R.W, R.H, R.FPS
put, ease, clamp, back, font, mouth = R.put, R.ease, R.clamp, R.back, R.font, R.mouth
F_ANTON, F_UI, OL, YEL, WHITE = R.F_ANTON, R.F_UI, R.OL, R.YEL, R.WHITE
MF = os.path.join(HERE, "..", "mateo-pov", "fonts")
F_HAND = os.path.join(MF, "Caveat.ttf"); F_BAL = os.path.join(MF, "Baloo2-ExtraBold.ttf")
PI_ = math.pi
ORO = (255, 196, 60); ROSA = (232, 85, 109); TINTA = (52, 58, 130); CREMA = (252, 244, 226)

R.GAP.update({"B2": .12, "B3": .12, "B4": .15, "F04": .2, "B5": .2, "B6": .15, "B7": .15, "F08B": .15, "F08C": .15, "B8": .3, "F12": .2, "F13": .3, "B9": .25})
R.TL, R.TOTAL = R.timeline()
R.TL = {k: (a - .1, b - .1) for k, (a, b) in R.TL.items()}
R.TOTAL = R.TL["B9"][1] + .1          # corte en seco ~0,1 s tras la última palabra
R.CH = R.chunks(); TL = R.TL; TOTAL = R.TOTAL
S, E, WT = R.S, R.E, R.WT
R.NOMBRE = {"S": "SOFÍA", "A": "NOTA DE TU MAMÁ (LA ABUELA)"}
R.HIDE_LAST_CAPTION = False

def talk(lid, T): return S(lid) <= T < E(lid)
def u_(T, t0, d): return ease((T - t0) / d)

# ---------------------------------------------------------------- Sofía con boca animada
def sofia(c, kind, cx, cy, s, T, lid=None, rot=0):
    hab = lid is not None and talk(lid, T)
    put(c, f"sofia_{kind}_hab" if hab else f"sofia_{kind}", cx, cy + 400 * s, s, rot=rot)
    if hab: mouth(c, cx, cy + 60 * s, T, True, int(24 * s))
    if kind not in ("llora", "feliz") and (T % 3.9) < .12 and not rot:   # parpadeo
        d = ImageDraw.Draw(c)
        for ex in (-76, 76):
            x, y = cx + ex * s, cy - 84 * s
            d.ellipse((x - 40 * s, y - 34 * s, x + 40 * s, y + 34 * s), fill=(243, 194, 155))
            d.line((x - 34 * s, y + 4 * s, x + 34 * s, y + 4 * s), fill=OL, width=max(3, int(6 * s)))

def lagrimas(c, cx, cy, s, T):
    d = ImageDraw.Draw(c)
    for k, ex in enumerate((-78, 78)):
        for j in range(3):
            ph = ((T * 1.3) + j / 3 + k * .17) % 1
            x = cx + ex * s + 6 * math.sin(ph * 6); y = cy - 88 * s + ph * 230 * s; r = (10 + 4 * (1 - ph)) * s
            d.ellipse((x - r * .75, y - r, x + r * .75, y + r), fill=(143, 208, 255), outline=(58, 127, 191), width=3)

def bgz(name, T, t0, z0=1.0, z1=1.06, dur=7):
    """Fondo con zoom lento (Ken Burns)."""
    return R.bg(name, T, t0, z0, z1, dur)

# ---------------------------------------------------------------- papel, letras y crayola
_GR = Image.fromarray((np.random.default_rng(3).random((H, W)) * 70 + 185).astype(np.uint8))
def trazo(c, pts, w, col, alpha=255):
    """Trazo de crayola con textura de cera."""
    if len(pts) < 2: return
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    d.line(pts, fill=255, width=int(w), joint="curve")
    for p in (pts[0], pts[-1]): d.ellipse((p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2), fill=255)
    m = Image.composite(_GR, Image.new("L", (W, H), 0), m).point(lambda v: min(255, int(v * alpha / 255)))
    c.alpha_composite(Image.new("RGBA", (W, H), col + (255,)), (0, 0)) if False else None
    lay = Image.new("RGBA", (W, H), col + (0,)); lay.putalpha(m); c.alpha_composite(lay)

def s_path(cx, yt, h, wob=0.0, seed=0):
    """Puntos de una S (arriba-derecha -> abajo-izquierda) en pantalla. wob>0 = S torcida de niña."""
    rx, ry = h * .32, h / 4; pts = []
    r = random.Random(seed)
    for k in range(40):   # arco de arriba: de -25° a -270°
        a = math.radians(-25 - 245 * k / 39); pts.append((cx + rx * math.cos(a), yt + ry + ry * math.sin(a)))
    for k in range(1, 40):   # arco de abajo: de -90° a 205°
        a = math.radians(-90 + 295 * k / 39); pts.append((cx + rx * math.cos(a), yt + 3 * ry + ry * math.sin(a)))
    if wob:
        out = []
        for i, (x, y) in enumerate(pts):
            out.append((x + wob * h * (.22 * math.sin(i * .35 + seed) + .06 * r.uniform(-1, 1)) * (1 if i > 30 else .5),
                        y + wob * h * .08 * math.sin(i * .5 + 1)))
        pts = out
    return pts

def recorrido(pts, u):
    n = max(2, int(len(pts) * clamp(u))); return pts[:n]

def mano(c, tip, T, s=.5):
    """Mano de Sofía con crayola rosa: la punta cae en tip."""
    x, y = tip; jx = 1.5 * math.sin(T * 31); jy = 1.5 * math.cos(T * 27)
    # en la capa (1000x1600 lógicos), la punta está en (330,1010); el centro en (500,800)
    put(c, "sofia_mano_crayola", x + (500 - 330) * s + jx, y + (800 - 1010) * s + jy, s)

def manuscrito(c, lineas, T, t0, t1, x, y, size=64, col=TINTA, lh=84, rot=0, centro=True):
    """Texto a mano que va apareciendo letra a letra entre t0 y t1."""
    total = sum(len(l) for l in lineas); n = int(total * clamp((T - t0) / max(.01, t1 - t0)))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); f = font(F_HAND, size)
    for i, l in enumerate(lineas):
        vis = l[:max(0, n)]; n -= len(l)
        if not vis: break
        xx = x - d.textlength(l, font=f) / 2 if centro else x
        d.text((xx, y + i * lh), vis, font=f, fill=col + (255,))
    if rot: lay = lay.rotate(rot, center=(x, y), resample=Image.BICUBIC)
    c.alpha_composite(lay)

def brillos(c, T, t0, cx, cy, r0=140, col=(255, 236, 160), n=12):
    if T < t0: return
    d = ImageDraw.Draw(c); u = T - t0
    for k in range(n):
        a = k * 2 * PI_ / n + u * .8; rr = r0 + 40 * math.sin(u * 3 + k)
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a); s = 10 + 8 * abs(math.sin(u * 5 + k))
        d.polygon([(x, y - s), (x + s * .3, y - s * .3), (x + s, y), (x + s * .3, y + s * .3), (x, y + s), (x - s * .3, y + s * .3), (x - s, y), (x - s * .3, y - s * .3)], fill=col)

def polvo(c, T, n=40, seed=1):
    r = random.Random(seed); d = ImageDraw.Draw(c)
    for k in range(n):
        x = (r.uniform(0, W) + T * r.uniform(-12, 12)) % W; y = (r.uniform(200, 1400) + T * r.uniform(-20, 6)) % 1500
        a = int(90 + 90 * math.sin(T * 1.7 + k)); rr = r.uniform(2, 5)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 230, 180, max(0, a)))

def confeti(c, T, t0, n=60):
    if T < t0: return
    r = random.Random(7); d = ImageDraw.Draw(c); u = T - t0
    for k in range(n):
        x = r.uniform(80, 1000) + 40 * math.sin(u * 3 + k); y = -40 + u * r.uniform(400, 800) + r.uniform(0, 200)
        if y > 1400: continue
        col = r.choice([(232, 85, 109), (255, 196, 60), (95, 191, 106), (74, 159, 224), (184, 138, 214)])
        d.rectangle((x - 9, y - 5, x + 9, y + 5), fill=col)

_OV = []
def rotulo(c, T, t0, txt, cx, cy, fill=YEL, fg=OL, size=46, rot=-3):
    """Rótulo corto tipo cinta de papel que aparece con rebote (solo palabras que dice la voz)."""
    if T < t0: return
    k = R.popscale(T, t0); f = font(F_BAL, size)
    tw = ImageDraw.Draw(c).textlength(txt, font=f)
    lay = Image.new("RGBA", (int(tw + 80), size + 50), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((4, 8, lay.width - 4, lay.height - 4), 16, fill=(20, 14, 30, 120))
    d.rounded_rectangle((0, 0, lay.width - 8, lay.height - 12), 16, fill=fill, outline=OL, width=5)
    d.text(((lay.width - 8) / 2, (lay.height - 12) / 2 + 2), txt, font=f, fill=fg, anchor="mm")
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    if k < .99: lay = lay.resize((max(1, int(lay.width * k)), max(1, int(lay.height * k))))
    (_OV[-1] if _OV else c).alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

# ---------------------------------------------------------------- hoja de Sofía con su nombre a medias
def hoja_nombre(c, T, cx, cy, s, sof_u=1.0, rot=-4, tachon=False):
    lay = Image.new("RGBA", (int(760 * s), int(520 * s)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, lay.width - 1, lay.height - 1), int(14 * s), fill=(253, 250, 240), outline=OL, width=max(3, int(6 * s)))
    for k in range(4):
        y = (110 + k * 100) * s; d.line((30 * s, y, lay.width - 30 * s, y), fill=(160, 200, 235), width=max(2, int(4 * s)))
    c2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # SOF torcido con crayola rosa (como lo escribe una niña que no puede)
    base = [(160, 300, 4), (290, 312, 5), (410, 296, 6)]
    for i, (lx, ly, sd) in enumerate(base[:3]):
        u = clamp(sof_u * 3 - i)
        if u <= 0: continue
        X, Y = cx - 380 * s + lx * s, cy - 260 * s + ly * s
        if i == 0: pts = s_path(X, Y - 90 * s, 170 * s, .35, 2)
        elif i == 1:
            pts = [(X + 60 * s * math.cos(a) * (1 + .1 * math.sin(a * 3)), Y - 5 * s + 80 * s * math.sin(a)) for a in np.linspace(-PI_ / 2, 3 * PI_ / 2 - .3, 40)]
        else:
            pts = [(X, Y - 90 * s), (X - 4 * s, Y + 80 * s)] + [(X - 4 * s, Y - 90 * s), (X + 80 * s, Y - 100 * s)] + [(X, Y - 10 * s), (X + 60 * s, Y - 4 * s)]
        trazo(c2, recorrido(pts, u), 16 * s, ROSA)
    # huecos de la Í y la A
    for k, lx in enumerate((560, 660)):
        d.text((lx * s, 300 * s), "?", font=font(F_BAL, 120 * s), fill=(200, 200, 215), anchor="mm")
    if tachon:
        for k in range(3):
            d.line((80 * s + k * 20 * s, 380 * s, 500 * s, 230 * s + k * 30 * s), fill=ROSA + (200,), width=int(10 * s))
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A").point(lambda v: v // 3))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (int(cx - lay.width / 2 + 10), int(cy - lay.height / 2 + 14)))
    c.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))
    c2 = c2.rotate(rot, center=(cx, cy), resample=Image.BICUBIC)
    c.alpha_composite(c2)


def foto_infancia(k=1.0):
    """Foto vieja (sepia): tú con 5 años escribiendo en este mismo cuaderno; la mano de tu mamá te guía.
    A la abuela no se le ve la cara (canon: no se ve hasta la Parte 14), solo su manga de flores."""
    ph = Image.new("RGBA", (W, H), (236, 210, 170, 255)); d = ImageDraw.Draw(ph)
    d.rectangle((0, 1150, W, H), fill=(190, 140, 96))
    put(ph, "nina_mama", 400, 760 + 360, .9)
    put(ph, "cuaderno", 560, 1300, .5, rot=-10)
    # brazo de tu mamá entrando por la derecha, manga con flores, mano sobre la tuya
    d.polygon([(W, 900), (W, 1120), (760, 1290), (700, 1200)], fill=(150, 110, 190), outline=OL)
    for (x, y) in ((900, 1040), (980, 990), (820, 1150), (950, 1100)):
        for j in range(5):
            a = j * 2 * PI_ / 5; d.ellipse((x + 14 * math.cos(a) - 11, y + 14 * math.sin(a) - 11, x + 14 * math.cos(a) + 11, y + 14 * math.sin(a) + 11), fill=(245, 150, 180))
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(255, 210, 74))
    d.ellipse((610, 1170, 760, 1300), fill=(243, 194, 155), outline=OL, width=5)
    d.ellipse((540, 1230, 640, 1310), fill=(243, 194, 155), outline=OL, width=4)
    g = ph.convert("L"); sep = Image.merge("RGBA", (g.point(lambda v: min(255, int(v * 1.05) + 30)), g.point(lambda v: min(255, v + 10)), g.point(lambda v: int(v * .82)), Image.new("L", (W, H), 255)))
    return sep


def cuaderno_abierto(c, cx, cy, s, T, izq=None, der=None):
    """Dibuja el cuaderno abierto; izq/der son funciones que pintan sobre cada página (reciben (c, x0, y0, s))."""
    w, h = 900 * s, 640 * s
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((cx - w / 2 - 22 * s, cy - h / 2 - 16 * s, cx + w / 2 + 22 * s, cy + h / 2 + 22 * s), int(26 * s), fill=(108, 148, 120), outline=OL, width=max(4, int(8 * s)))
    for side in (-1, 1):
        x0 = cx if side > 0 else cx - w / 2
        d.rounded_rectangle((x0, cy - h / 2, x0 + w / 2, cy + h / 2), int(10 * s), fill=(250, 240, 214), outline=OL, width=max(3, int(5 * s)))
        for k in range(7):
            y = cy - h / 2 + (90 + k * 78) * s; d.line((x0 + 30 * s, y, x0 + w / 2 - 30 * s, y), fill=(190, 205, 225), width=max(2, int(3 * s)))
    d.line((cx, cy - h / 2, cx, cy + h / 2), fill=(150, 130, 100), width=max(3, int(6 * s)))
    if izq: izq(c, cx - w / 2, cy - h / 2, s)
    if der: der(c, cx, cy - h / 2, s)
    return w, h

def s_punteada(c, x0, y0, s, alpha=255):
    d = ImageDraw.Draw(c)
    for i, (x, y) in enumerate(s_path(x0 + 225 * s, y0 + 150 * s, 330 * s)):
        if i % 3 == 0: d.ellipse((x - 7 * s, y - 7 * s, x + 7 * s, y + 7 * s), fill=(60, 60, 80, alpha))

# ---------------------------------------------------------------- el cuaderno abierto: estado coherente de sus páginas
CB = (540, 800, 1.05)                      # cuaderno abierto: centro y escala (siempre el mismo encuadre base)
PW, PH = 900 * CB[2] / 2, 640 * CB[2]      # tamaño de una página en pantalla
PX_L, PX_R, PY = CB[0] - PW, CB[0], CB[1] - PH / 2

NOTA = ["Si la escribes", "bien… te cuento", "un secreto."]
MSG = ["Tu mamá también", "decía que no servía", "para escribir.", "Lloró tres tardes", "con esta misma S."]

def izq_S(T, escrita=1.0):
    def f(cc, x0, y0, s):
        s_punteada(cc, x0, y0, s)
        if escrita > 0: trazo(cc, recorrido(s_path(x0 + 225 * s, y0 + 150 * s, 330 * s), escrita), 18 * s, ROSA)
    return f

def der_nota(T, t0=-1, t1=0):
    def f(cc, x0, y0, s):
        manuscrito(cc, NOTA, T, t0, t1, x0 + 225 * s, y0 + 120 * s, int(54 * s), TINTA, int(78 * s), 3)
        if T >= t1: ImageDraw.Draw(cc).text((x0 + 330 * s, y0 + 420 * s), "— R.", font=font(F_HAND, int(54 * s)), fill=TINTA)
    return f

def der_msg(T, t0=-1, t1=0, conC=0.0):
    def f(cc, x0, y0, s):
        manuscrito(cc, MSG, T, t0, t1, x0 + 225 * s, y0 + 60 * s, int(44 * s), TINTA, int(66 * s), 2)
    return f

_PAGE = {}
def pagina_img_de(fn):
    """Recorta la página derecha dibujada por fn como imagen suelta (para hacerla girar)."""
    tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0)); cuaderno_abierto(tmp, *CB, 0, None, fn)
    return tmp.crop((int(PX_R), int(PY), int(PX_R + PW), int(PY + PH)))

def reverso(front):
    """Reverso de una hoja: papel con la tinta del otro lado transparentándose (en espejo)."""
    if "rev" not in _PAGE:
        blank = pagina_img_de(None)
        ghost = front.transpose(Image.FLIP_LEFT_RIGHT)
        g = Image.blend(blank, ghost, .14)
        _PAGE["rev"] = g
    return _PAGE["rev"]

def izq_reverso(cc, x0, y0, s):
    if "nota" not in _PAGE: _PAGE["nota"] = pagina_img_de(der_nota(1e9))
    cc.alpha_composite(reverso(_PAGE["nota"]), (int(x0), int(y0)))

def hoja_girando(c, u, front, back):
    """Una hoja que gira de derecha a izquierda (u: 0 -> 1) mostrando su frente y luego su reverso."""
    cx = CB[0]; k = abs(math.cos(u * PI_)); ww = max(2, int(PW * k)); lift = int(36 * math.sin(u * PI_))
    im = (front if u < .5 else back).resize((ww, int(PH) + 2 * lift))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    if u < .5:
        ds.rectangle((cx, PY, cx + ww + 30, PY + PH), fill=(30, 20, 10, int(90 * math.sin(u * PI_))))
        c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20))); c.alpha_composite(im, (int(cx), int(PY - lift)))
    else:
        ds.rectangle((cx - ww - 30, PY, cx, PY + PH), fill=(30, 20, 10, int(90 * math.sin(u * PI_))))
        c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20))); c.alpha_composite(im, (int(cx - ww), int(PY - lift)))
    ImageDraw.Draw(c).line((cx, PY - lift, cx, PY + PH + lift), fill=(150, 130, 100), width=6)

def fondo_libro(T, t0, blur=7, osc=80):
    c = bgz("bg_desvan", T, t0, 1.3, 1.36, 9).filter(ImageFilter.GaussianBlur(blur)).copy(); R.dark(c, osc); polvo(c, T, 25, 3)
    return c

def dedos(c, x, y, T, s=1.0):
    """Deditos de Sofía pellizcando la esquina de una hoja (sin crayola)."""
    d = ImageDraw.Draw(c); sk = (243, 194, 155)
    d.polygon([(x + 40 * s, y + 30 * s), (x + 230 * s, y + 260 * s), (x + 330 * s, y + 200 * s), (x + 120 * s, y - 20 * s)], fill=(246, 201, 74), outline=OL)
    d.ellipse((x - 20 * s, y - 40 * s, x + 120 * s, y + 70 * s), fill=sk, outline=OL, width=5)
    for k in range(3):
        fx, fy = x - 40 * s + k * 26 * s, y - 50 * s + k * 18 * s
        d.ellipse((fx - 30 * s, fy - 16 * s, fx + 30 * s, fy + 16 * s), fill=sk, outline=OL, width=4)
    d.ellipse((x - 70 * s, y - 10 * s, x - 10 * s, y + 30 * s), fill=sk, outline=OL, width=4)

def casillas(c, T, t0, llena=0.0):
    """Las 5 casillas de la palabra secreta; la C entra en la primera cuando llena=1."""
    d = ImageDraw.Draw(c); u = ease((T - t0) / .5)
    for k in range(5):
        x = 540 + (k - 2) * 150; y = 1300 + 80 * (1 - u)
        d.rounded_rectangle((x - 62, y - 76, x + 62, y + 76), 18, fill=(40, 28, 60, int(235 * u)), outline=ORO, width=6)
        if k == 0 and llena >= 1:
            d.text((x, y), "C", font=font(F_BAL, 104), fill=ORO, anchor="mm", stroke_width=4, stroke_fill=(140, 90, 20))
        elif k > 0:   # candadito
            d.rounded_rectangle((x - 22, y - 4, x + 22, y + 32), 6, fill=(130, 110, 160)); d.arc((x - 16, y - 30, x + 16, y + 6), 180, 360, fill=(130, 110, 160), width=7)

RAYO = [(600, 0), (560, 520), (612, 560), (522, 1100), (578, 1132), (480, H)]
def _tarjeta(c, cx, cy, letra, txt, mas, menos, col, k, big=1.0):
    """Opción final estilo Mateo: tarjeta de color con borde blanco, letra en círculo arriba, texto grande y +/-."""
    if k <= 0: return
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    w2, h1, h2 = 212 * k * big, 150 * k * big, (250 + 70 * (len(txt) - 2)) * k * big
    d.rounded_rectangle((cx - w2 + 8, cy - h1 + 12, cx + w2 + 8, cy + h2 + 12), 40, fill=(10, 6, 20, 120))
    d.rounded_rectangle((cx - w2, cy - h1, cx + w2, cy + h2), 40, fill=col + (240,), outline=WHITE, width=8)
    r = 62 * k * big
    d.ellipse((cx - r, cy - h1 - r * .9, cx + r, cy - h1 + r * 1.1), fill=WHITE, outline=OL, width=6)
    d.text((cx, cy - h1 + r * .1), letra, font=font(F_ANTON, int(92 * k * big) + 1), fill=col, anchor="mm")
    if k > .5:
        for i, l in enumerate(txt):
            d.text((cx, cy - 20 + i * 70 * big), l, font=font(F_ANTON, int(62 * big)), fill=WHITE, anchor="mm", stroke_width=7, stroke_fill=OL)
        y = cy + 60 + 70 * big * (len(txt) - 1)
        d.text((cx, y + 30), "+ " + mas, font=font(F_UI, int(36 * big)), fill=(170, 255, 180), anchor="mm", stroke_width=6, stroke_fill=OL)
        d.text((cx, y + 82), "– " + menos, font=font(F_UI, int(34 * big)), fill=(255, 190, 180), anchor="mm", stroke_width=6, stroke_fill=OL)
    c.alpha_composite(ov)

# ================================================================ PARTE 2: helpers
AZUL_NOCHE = (18, 22, 60)
MANGA_MAMA = (96, 160, 196)

def noche(c, a=150):
    c.alpha_composite(Image.new("RGBA", (W, H), AZUL_NOCHE + (int(a),)))

def sofia_dormida(c, cx, cy, s, T):
    """Sofía dormida en su cama: almohada, ojos cerrados, manta y zetas."""
    d = ImageDraw.Draw(c)
    d.ellipse((cx - 420 * s, cy - 380 * s, cx + 420 * s, cy + 120 * s), fill=(236, 230, 246), outline=OL, width=6)
    put(c, "sofia_neutral", cx, cy + 400 * s, s)
    d = ImageDraw.Draw(c)
    for ex in (-76, 76):
        x, y = cx + ex * s, cy - 84 * s
        d.ellipse((x - 42 * s, y - 36 * s, x + 42 * s, y + 36 * s), fill=(243, 194, 155))
        d.arc((x - 30 * s, y - 20 * s, x + 30 * s, y + 16 * s), 20, 160, fill=OL, width=max(3, int(7 * s)))
    br = 6 * math.sin(T * 2.2)   # respira
    d.rounded_rectangle((cx - 520 * s, cy + 150 * s - br, cx + 520 * s, cy + 1000 * s), int(60 * s), fill=(150, 178, 226), outline=OL, width=7)
    for k in range(5):
        x = cx - 400 * s + k * 200 * s
        d.ellipse((x - 26 * s, cy + 330 * s - br, x + 26 * s, cy + 382 * s - br), fill=(255, 236, 160))
    for k in range(3):
        ph = (T * .5 + k / 3) % 1
        d.text((cx + 250 * s + ph * 160, cy - 300 * s - ph * 260), "z", font=font(F_BAL, int((40 + 40 * ph) * s)),
               fill=(255, 255, 255, int(255 * (1 - ph))), anchor="mm")

def nota_andrea(sc=1.0, rot=-8, brillo=0):
    lay = Image.new("RGBA", (int(440 * sc), int(240 * sc)), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    dl.rounded_rectangle((0, 0, lay.width - 1, lay.height - 1), int(12 * sc), fill=(255, 240, 160), outline=OL, width=max(3, int(5 * sc)))
    dl.text((lay.width / 2, 70 * sc), "Para:", font=font(F_HAND, int(64 * sc)), fill=TINTA, anchor="mm")
    dl.text((lay.width / 2, 160 * sc), "Andrea", font=font(F_HAND, int(84 * sc)), fill=(194, 58, 90), anchor="mm")
    return lay.rotate(rot, expand=True, resample=Image.BICUBIC)

def glow(c, x, y, r, col=(255, 214, 120), a=150, blur=40):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((x - r, y - r, x + r, y + r), fill=col + (int(a),))
    c.alpha_composite(g.filter(ImageFilter.GaussianBlur(blur)))

def o_path(cx, cy, rx, ry, wob=0.0, seed=0, n=60):
    """O que empieza arriba y gira hacia la izquierda (como enseña la página)."""
    r = random.Random(seed); pts = []
    for i in range(n + 1):
        t = 2 * PI_ * i / n * 1.02
        k = 1 + wob * (.12 * math.sin(t * 2 + seed) + .04 * r.uniform(-1, 1))
        pts.append((cx - rx * k * math.sin(t), cy - ry * k * math.cos(t)))
    return pts

def mano_mama(c, tip, T, s=.62):
    """La mano de la mamá encima de la de Sofía (abrazo por la espalda), manga azul que entra por la derecha."""
    x, y = tip[0] + 150 * s, tip[1] - 230 * s
    d = ImageDraw.Draw(c)
    d.polygon([(x + 40 * s, y - 60 * s), (W + 40, y - 380 * s), (W + 40, y + 160 * s), (x + 110 * s, y + 90 * s)], fill=MANGA_MAMA, outline=OL)
    d.ellipse((x - 120 * s, y - 80 * s, x + 130 * s, y + 110 * s), fill=(238, 188, 150), outline=OL, width=5)
    for k in range(3):
        fx = x - 130 * s + k * 18 * s; fy = y - 20 * s + k * 50 * s
        d.ellipse((fx - 60 * s, fy - 24 * s, fx + 40 * s, fy + 24 * s), fill=(238, 188, 150), outline=OL, width=4)

def brazos_abrazo(c, cx, cy, s, u=1.0):
    """Brazos de la mamá (manga azul) rodeando a Sofía por la espalda."""
    d = ImageDraw.Draw(c); y = cy + 560 * s; e = 1 - u
    for side in (-1, 1):
        x0 = cx + side * (620 + 300 * e) * s
        d.polygon([(x0, y - 140 * s), (cx + side * 40 * s, y - 40 * s), (cx + side * 40 * s, y + 90 * s), (x0, y + 60 * s)], fill=MANGA_MAMA, outline=OL)
        d.ellipse((cx + side * 40 * s - 80 * s, y - 70 * s, cx + side * 40 * s + 80 * s, y + 110 * s), fill=(238, 188, 150), outline=OL, width=5)

_PG = {}
_FOTO = {}
def pagina_n(n, s):
    key = (n, s)
    if key not in _PG:
        f = os.path.join(HERE, "..", "pinti-organico", "assets", "paginas", f"pagina-{n:02d}.jpg")
        im = Image.open(f).convert("RGBA"); im = im.crop((0, 0, im.width, int(im.height * .965)))   # sin número de página
        _PG[key] = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    return _PG[key]

def foto_abrazo(u_circ=0.0):
    """Recuerdo sepia: tú con 5 años; tu mamá te abraza por la espalda (solo sus mangas de flores, sin cara)
    y te guía la mano en círculo. u_circ dibuja el círculo."""
    if "base" not in _FOTO:
        ph = Image.new("RGBA", (W, H), (236, 210, 170, 255)); d = ImageDraw.Draw(ph)
        d.rectangle((0, 1150, W, H), fill=(190, 140, 96))
        put(ph, "nina_mama", 480, 760 + 360, .9)
        d.rectangle((300, 1240, 760, 1440), fill=(250, 246, 236), outline=OL, width=5)   # hoja
        for side in (-1, 1):   # dos mangas de flores que rodean a la niña
            if side > 0: poly = [(W, 860), (W, 1080), (700, 1300), (650, 1210)]
            else: poly = [(0, 880), (0, 1100), (300, 1240), (330, 1150)]
            d.polygon(poly, fill=(150, 110, 190), outline=OL)
            for (x, y) in ((900, 1000), (980, 950), (800, 1120)) if side > 0 else ((80, 980), (160, 1060), (260, 1150)):
                for j in range(5):
                    a = j * 2 * PI_ / 5; d.ellipse((x + 14 * math.cos(a) - 11, y + 14 * math.sin(a) - 11, x + 14 * math.cos(a) + 11, y + 14 * math.sin(a) + 11), fill=(245, 150, 180))
                d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(255, 210, 74))
        d.ellipse((600, 1200, 740, 1310), fill=(243, 194, 155), outline=OL, width=5)   # mano de tu mamá sobre la tuya
        d.ellipse((560, 1250, 650, 1320), fill=(243, 194, 155), outline=OL, width=4)
        g = ph.convert("L")
        sep = Image.merge("RGBA", (g.point(lambda v: min(255, int(v * 1.05) + 30)), g.point(lambda v: min(255, v + 10)), g.point(lambda v: int(v * .82)), Image.new("L", (W, H), 255)))
        _FOTO["base"] = sep.crop((60, 360, 1020, 1500)).resize((640, 760))
    pol = Image.new("RGBA", (700, 920), (250, 246, 236, 255)); dp = ImageDraw.Draw(pol)
    pol.alpha_composite(_FOTO["base"], (30, 30)); dp.rectangle((0, 0, 699, 919), outline=OL, width=5)
    if u_circ > 0:   # el círculo en la hoja de la foto
        pts = recorrido(o_path(370, 690, 62, 50), u_circ); dp.line(pts, fill=(110, 70, 40), width=7, joint="curve")
    dp.text((350, 850), "yo, con 5 años", font=font(F_HAND, 64), fill=(90, 70, 60), anchor="mm")
    return pol

def polaroid(c, T, t0, rot=4, cy=820, u_circ=0.0, k0=.92):
    k = k0 + .06 * clamp((T - t0) / 5)
    pol = foto_abrazo(u_circ)
    pol = pol.resize((int(700 * k), int(920 * k))).rotate(rot, expand=True, resample=Image.BICUBIC)
    c.alpha_composite(pol, (int(540 - pol.width / 2), int(cy - pol.height / 2)))

def o_punteada(c, x0, y0, s):
    d = ImageDraw.Draw(c)
    for i, (x, y) in enumerate(o_path(x0 + 225 * s, y0 + 300 * s, 120 * s, 170 * s, n=48)):
        if i % 2 == 0: d.ellipse((x - 7 * s, y - 7 * s, x + 7 * s, y + 7 * s), fill=(60, 60, 80))

def izq_O(escrita=1.0):
    def f(cc, x0, y0, s):
        o_punteada(cc, x0, y0, s)
        if escrita > 0: trazo(cc, recorrido(o_path(x0 + 225 * s, y0 + 300 * s, 120 * s, 170 * s), escrita), 18 * s, ROSA)
    return f

CARTA = ["Enséñale la O", "como te la", "enseñé a ti:", "con un abrazo", "redondo."]
MSG2 = ["Qué bonita O.", "Mañana, la F.", "Pregúntale qué", "quiere ser", "de mayor."]
def der_msg2(T, t0=-1, t1=0, firma=True):
    def f(cc, x0, y0, s):
        manuscrito(cc, MSG2, T, t0, t1, x0 + 225 * s, y0 + 50 * s, int(48 * s), TINTA, int(72 * s), 2)
        if firma and T >= t1: ImageDraw.Draw(cc).text((x0 + 300 * s, y0 + 440 * s), "— R.", font=font(F_HAND, int(50 * s)), fill=TINTA)
    return f

def tinta_brilla(c, T, t0, x0, y0, w, h):
    """Brillo húmedo que recorre la tinta recién escrita."""
    if T < t0: return
    d = ImageDraw.Draw(c); ph = ((T - t0) * 1.2) % 1
    for k in range(3):
        x = x0 + 20 + ph * (w - 40) + k * 30; d.line((x, y0 + 30, x - 60, y0 + h - 60), fill=(255, 255, 255, 40), width=12)
    brillos(c, T, t0, x0 + w / 2, y0 + h / 2 - 40, min(w, h) * .45, (200, 220, 255), 8)

# ================================================================ ESCENAS PARTE 2
def hoja_huevo(c, cx, cy, s, rot=-4, aro=1.0, wob=1.0, seed=7):
    """Hoja rayada con una O torcida (huevo) enorme y un aro rojo de corrector."""
    lay = Image.new("RGBA", (int(760 * s), int(620 * s)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, lay.width - 1, lay.height - 1), int(14 * s), fill=(253, 250, 240), outline=OL, width=max(3, int(6 * s)))
    for k in range(5):
        y = int((110 + k * 110) * s); d.line((int(30 * s), y, int(730 * s), y), fill=(150, 190, 230), width=max(2, int(4 * s)))
    pts = [(x + 380 * s - 380 * s, y) for x, y in o_path(380 * s, 310 * s, 150 * s, 235 * s, wob, seed)]
    pts = [(x + (y - 310 * s) * .22, y) for x, y in pts]          # aplastada y torcida: parece un huevo
    trazo(lay, pts, 20 * s, (226, 86, 108))
    if aro > 0:
        ring = recorrido(o_path(380 * s, 310 * s, 250 * s, 290 * s, 0.3, 3), aro); d = ImageDraw.Draw(lay)
        d.line(ring, fill=(214, 40, 40), width=max(5, int(14 * s)), joint="curve")
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    c.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def sc_huevo(T):   # H1 (segundo 0): Sofía llora y enseña su O torcida enorme: "mi O parece un huevo"
    c = bgz("bg_cuarto_sofia", T, 0, 1.06, 1.0, 4).copy()
    sofia(c, "llora", 540, 560, .88, T, "H1")
    lagrimas(c, 540, 560, .88, T)
    hoja_huevo(c, 540, 1130, 1.18, -4 + 2 * math.sin(T * 5), clamp((T - .25) / .6))
    return c

def sc_intentos(T):   # H2 (1): diez intentos, todas huevos
    t0 = S("H2") - .15
    c = Image.new("RGBA", (W, H), (0, 0, 0, 255)); c.alpha_composite(bgz("bg_cuarto_sofia", T, t0, 1.1, 1.18, 6).filter(ImageFilter.GaussianBlur(8)))
    R.dark(c, 70)
    tf = WT("H2", "huevos.") - .1; paso = max(.14, (tf - t0 - .3) / 10)
    n = min(10, int(max(0.0, (T - t0 - .05) / paso)) + (1 if T >= t0 + .05 else 0))
    pos = lambda k: (290 + (k % 2) * 500 + ((k // 2) % 2) * 20, 500 + (k // 2) * 215)
    for k in range(min(n, 10)):
        x, y = pos(k); sc = R.popscale(T, t0 + .05 + k * paso)
        if sc <= .05: continue
        lay = Image.new("RGBA", (340, 280), (0, 0, 0, 0)); hoja_huevo(lay, 170, 140, .42, [-6, 5, -3, 7, -5][(k // 2) % 5] + (k % 2) * 3, 0, .8 + .1 * k, 11 + k)
        lay = lay.resize((max(1, int(340 * sc)), max(1, int(280 * sc))))
        c.alpha_composite(lay, (int(x - lay.width / 2), int(y - lay.height / 2)))
    if T >= WT("H2", "Diez") - .05: rotulo(c, T, WT("H2", "Diez") - .05, f"INTENTO {min(max(n, 1), 10)}", 540, 330, size=54, rot=-3)
    if T >= tf:
        d = ImageDraw.Draw(c)
        for k in range(10):
            x, y = pos(k); u = R.popscale(T, tf + k * .04)
            if u > .1: d.text((x + 100, y - 20), "×", font=font(F_ANTON, int(110 * u)), fill=(214, 40, 40), anchor="mm", stroke_width=4, stroke_fill=OL)
    return c

def sc_nota(T):   # H2 (2): miras la nota pegada en el cuaderno de tu madre: "Para: Andrea"
    t0 = WT("H2", "Entonces") - .15
    c = fondo_libro(T, t0, 6, 40); glow(c, 540, 800, 420, (255, 214, 120), 130, 70)
    cuaderno_abierto(c, *CB, T, izq_reverso, der_msg(1e9))
    n = nota_andrea(1.0, -8 + 2 * math.sin(T * 3))
    c.alpha_composite(n, (int(PX_R + PW / 2 - n.width / 2), int(PY + 230 + 5 * math.sin(T * 4))))
    brillos(c, T, t0, PX_R + PW / 2, PY + 330, 220, (255, 236, 160), 10)
    if T >= WT("H2", "nota") - .05: rotulo(c, T, WT("H2", "nota") - .05, "UNA NOTA", 540, 330, size=52, rot=-3)
    return c

def _sc_despegan(T):   # F03-F04: despegan la nota de la página pegada; se abre: letra de tu mamá (voz de la abuela)
    t0 = S("F03") - .15; ta = WT("F03", "dice,") - .15
    c = fondo_libro(T, t0, 7, 40)
    c.alpha_composite(Image.new("RGBA", (W, H), (255, 200, 140, 30)))
    if T < ta:   # la nota sale despacio de entre las páginas pegadas
        cuaderno_abierto(c, *CB, T, izq_reverso, der_msg(1e9))
        u = ease((T - t0 - .2) / 1.6)
        n = nota_andrea(1.0, -8 + 10 * u)
        x = PX_R + PW - 140 - 300 * u; y = PY + 120 - 220 * u
        c.alpha_composite(n, (int(x), int(y)))
        dedos(c, x + 60, y + n.height - 20, T, .8)
        if T >= WT("F03", "cuidado.") - .2: rotulo(c, T, WT("F03", "cuidado.") - .2, "CON CUIDADO…", 540, 1250, fill=(255, 255, 255), fg=TINTA, size=50)
        return c
    # la nota abierta, grande, con la letra de tu mamá apareciendo al ritmo de su voz
    R.dark(c, 60)
    u = back((T - ta) / .5)
    w, h = int(820 * u) + 2, int(900 * u) + 2
    lay = Image.new("RGBA", (820, 900), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    dl.rounded_rectangle((0, 0, 819, 899), 18, fill=(255, 243, 175), outline=OL, width=6)
    dl.line((0, 450, 819, 450), fill=(230, 210, 130), width=4); dl.line((410, 0, 410, 899), fill=(236, 218, 140), width=3)   # dobleces
    lay = lay.rotate(2, expand=True, resample=Image.BICUBIC).resize((max(2, int(w)), max(2, int(h))))
    c.alpha_composite(lay, (int(540 - lay.width / 2), int(800 - lay.height / 2)))
    if u > .9:
        manuscrito(c, CARTA, T, S("F04"), E("F04") - .2, 540, 420, 78, TINTA, 118, 2)
        if T >= E("F04") - .2: ImageDraw.Draw(c).text((700, 1060), "— R.", font=font(F_HAND, 64), fill=TINTA)
    if T >= WT("F03", "mamá…") - .1: rotulo(c, T, WT("F03", "mamá…") - .1, "LETRA DE TU MAMÁ", 760, 330, fill=(255, 255, 255), fg=TINTA, size=44, rot=3)
    if T >= WT("F04", "redondo.") - .05:   # un corazón-O alrededor de "abrazo redondo"
        uu = ease((T - WT("F04", "redondo.") + .05) / .6)
        pts = recorrido(o_path(540, 870, 310, 125), uu); trazo(c, pts, 10, ROSA)
    return c

def sc_despegan(T):
    c = _sc_despegan(T); t0 = S("F03") - .15
    if t0 + .35 <= T < t0 + 3.3: rotulo(c, T, t0 + .35, "GANÓ: LA ABREN JUNTAS", 540, 330, fill=(120, 214, 140), size=44, rot=-2)
    return c

def sc_curiosa(T):   # F05: "¿cómo se abraza una letra?"
    t0 = S("F05") - .15
    c = bgz("bg_desvan", T, t0, 1.0, 1.06, 5).copy(); polvo(c, T, 25, 2)
    d = ImageDraw.Draw(c)
    for k, (x, y, r0) in enumerate(((230, 380, -10), (860, 340, 12), (850, 760, -6))):
        tk = t0 + .3 + k * .4
        if T < tk: continue
        sc = R.popscale(T, tk) * (1 + .04 * math.sin(T * 4 + k))
        d.text((x, y), "?", font=font(F_ANTON, int(170 * sc) + 1), fill=YEL, anchor="mm", stroke_width=8, stroke_fill=OL)
    # una O gordita con bracitos (la letra que hay que abrazar)
    if T >= WT("F05", "letra?") - .2:
        k = R.popscale(T, WT("F05", "letra?") - .2)
        x, y = 230, 820
        d.ellipse((x - 90 * k, y - 120 * k, x + 90 * k, y + 120 * k), outline=ROSA, width=max(1, int(34 * k)))
        if k > .6:
            d.ellipse((x - 30, y - 20, x - 14, y - 2), fill=OL); d.ellipse((x + 14, y - 20, x + 30, y - 2), fill=OL)
            d.arc((x - 24, y, x + 24, y + 30), 10, 170, fill=OL, width=5)
    sofia(c, "timido", 600, 900, .95, T, "F05")
    return c

def sc_flash(T):   # F06: te acuerdas de golpe: tu mamá te abrazaba por la espalda y te guiaba la mano en círculo
    t0 = S("B5") - .15
    c = bgz("bg_desvan", T, t0, 1.25, 1.3, 6).filter(ImageFilter.GaussianBlur(8)).copy(); R.dark(c, 110)
    if T < t0 + .25:   # destello del recuerdo
        c.alpha_composite(Image.new("RGBA", (W, H), (255, 246, 220, int(255 * (1 - (T - t0) / .25)))))
    tc = WT("B5", "círculo.") - .5
    polaroid(c, T, t0, 4, 820, clamp((T - tc) / 1.1) if T >= tc else 0)
    if T >= WT("B5", "golpe.") - .1: rotulo(c, T, WT("B5", "golpe.") - .1, "TE ACUERDAS", 540, 300, fill=(255, 236, 200), size=50, rot=-3)
    if T >= WT("B5", "espalda…") - .1: rotulo(c, T, WT("B5", "espalda…") - .1, "POR LA ESPALDA", 540, 1340, size=48, rot=3)
    return c

def sc_imprimeO(T):   # F07 (1): imprimes la hoja de la O
    t0 = S("B6") - .15
    c = bgz("bg_desvan", T, t0, 1.05, 1.1, 6).copy(); R.dark(c, 80); d = ImageDraw.Draw(c)
    d.rounded_rectangle((210, 980, 870, 1260), 30, fill=(236, 236, 242), outline=OL, width=8)
    d.rectangle((260, 1000, 820, 1030), fill=(60, 60, 70))
    u = ease((T - t0 - .1) / 1.3); im = pagina_n(17, .48)
    crop = im.crop((0, im.height - int(im.height * u), im.width, im.height)) if u > 0 else None
    if crop and crop.height > 2: c.alpha_composite(crop, (int(540 - im.width / 2), int(1010 - crop.height)))
    d.rounded_rectangle((210, 1030, 870, 1260), 30, fill=(236, 236, 242), outline=OL, width=8)
    d.ellipse((780, 1100, 820, 1140), fill=(95, 191, 106))
    if T >= WT("B6", "O.") - .1: rotulo(c, T, WT("B6", "O.") - .1, "LA O", 800, 330, size=64, rot=4)
    return c

def sc_abrazo(T):   # F07 (2): la abrazas por la espalda
    t0 = WT("B6", "abrazas") - .2
    c = bgz("bg_desvan", T, t0, 1.0, 1.05, 4).copy()
    c.alpha_composite(Image.new("RGBA", (W, H), (255, 190, 140, 35)))
    glow(c, 540, 800, 420, (255, 220, 160), 110, 70)
    sofia(c, "feliz", 540, 700, .9, T)
    brazos_abrazo(c, 540, 700, .9, ease((T - t0) / .5))
    im = pagina_n(17, .36).rotate(-3, expand=True, resample=Image.BICUBIC)
    c.alpha_composite(im, (int(540 - im.width / 2), 1160))
    if T >= t0 + .3: rotulo(c, T, t0 + .3, "UN ABRAZO", 540, 300, fill=(255, 236, 200), fg=ROSA, size=54, rot=-3)
    return c

OPAGE = (214, 524), (296, 524)   # O punteadas de la fila 1 de la página real (px de la página)
def sc_trazaO(T):   # F07 (3) + pausa: la crayola da la vuelta entera, con tu mano encima; luego otra O, sola
    t0 = WT("B6", "crayola") - .2
    c = Image.new("RGBA", (W, H), (107, 74, 48, 255))
    s = 1.9; im = pagina_n(17, s)
    px, py = 255, 520; ox, oy = 540 - px * s, 760 - py * s
    c.paste(im, (int(ox), int(oy)), im)
    def P(x, y): return (ox + x * s, oy + y * s)
    t1a, t1b = WT("B6", "crayola"), E("B6") + .2
    t2a, t2b = E("B6") + .45, S("B7") - .1
    p1 = o_path(*P(*OPAGE[0]), 28 * s, 36 * s, .25, 3)
    p2 = o_path(*P(*OPAGE[1]), 28 * s, 36 * s)
    tip = None; guiada = False
    if T >= t1a:
        pts = recorrido(p1, (T - t1a) / (t1b - t1a)); trazo(c, pts, 15, ROSA)
        if T < t1b + .1: tip = pts[-1]; guiada = True
    if T >= t1b + .1: brillos(c, T, t1b, *P(*OPAGE[0]), 90)
    if T >= t2a:
        pts = recorrido(p2, (T - t2a) / (t2b - t2a)); trazo(c, pts, 15, ROSA)
        if T < t2b + .1: tip = pts[-1]
    if T >= WT("B6", "entera.") - .1: rotulo(c, T, WT("B6", "entera.") - .1, "¡VUELTA ENTERA!", 540, 1220, size=54, rot=-3)
    if T >= t2a: rotulo(c, T, t2a, "Y AHORA, SOLA", 540, 330, fill=(255, 255, 255), fg=ROSA, size=50, rot=3)
    if tip:
        mano(c, tip, T, .62)
        if guiada: mano_mama(c, tip, T, .62)
    elif T < t1a: mano(c, (P(*OPAGE[0])[0] - 40, P(*OPAGE[0])[1] - 60), T, .62); mano_mama(c, (P(*OPAGE[0])[0] - 40, P(*OPAGE[0])[1] - 60), T, .62)
    return c

def sc_redondita(T):   # F08: ¡es una O! ¡me salió redondita!
    t0 = S("B7") - .1
    c = bgz("bg_desvan", T, t0, 1.0, 1.05, 4).copy()
    sofia(c, "feliz", 540, 760 - 40 * abs(math.sin((T - t0) * 6)) * clamp(1 - (T - t0) / 2), .95, T, "B7")
    im = pagina_n(17, .34).rotate(5, expand=True, resample=Image.BICUBIC)
    c.alpha_composite(im, (int(540 - im.width / 2), 1150))
    confeti(c, T, t0)
    if T >= WT("B7", "redonda!") - .1: rotulo(c, T, WT("B7", "redonda!") - .1, "¡REDONDA!", 540, 300, size=60, rot=-4)
    return c

def sc_pregunta(T):   # F08B: "mami… ¿la abuela también te abrazaba así?"
    t0 = S("F08B") - .15
    c = bgz("bg_desvan", T, t0, 1.12, 1.18, 5).copy()
    c.alpha_composite(Image.new("RGBA", (W, H), (255, 180, 130, 45)))
    glow(c, 540, 600, 380, (255, 226, 170), 120, 60)
    sofia(c, "timido", 540, 760, 1.05, T, "F08B")
    brazos_abrazo(c, 540, 760, 1.05)
    return c

def sc_tardes(T):   # F08C: "y tú solo puedes decir que sí. Todas las tardes."
    t0 = S("F08C") - .15
    c = bgz("bg_desvan", T, t0, 1.25, 1.3, 6).filter(ImageFilter.GaussianBlur(9)).copy(); R.dark(c, 90)
    glow(c, 540, 820, 480, (255, 210, 150), 120, 70)
    polaroid(c, T, t0, -3, 800, 1.0, .9)
    if T >= WT("F08C", "tardes.") - .15: rotulo(c, T, WT("F08C", "tardes.") - .15, "TODAS LAS TARDES", 540, 1330, fill=(255, 236, 200), size=50, rot=2)
    return c

def sc_cuadernoO(T):   # F09: luego la escribe en el cuaderno, encima de la punteada
    t0 = S("F09") - .3; ta = WT("F09", "cuaderno,") - .1; tb = E("F09") + .3
    c = fondo_libro(T, t0, 7, 50)
    tip = [None]
    def izq(cc, x0, y0, s):
        o_punteada(cc, x0, y0, s)
        if T >= ta:
            pts = recorrido(o_path(x0 + 225 * s, y0 + 300 * s, 120 * s, 170 * s), (T - ta) / (tb - ta)); trazo(cc, pts, 18 * s, ROSA)
            if T < tb + .1: tip[0] = pts[-1]
    cuaderno_abierto(c, *CB, T, izq, None)
    if tip[0]: mano(c, tip[0], T, .62)
    elif T >= tb: brillos(c, T, tb, PX_L + PW / 2, PY + 300, 170)
    if T >= ta: rotulo(c, T, ta, "EN EL CUADERNO", 540, 330, size=48, rot=-2)
    return c

def sc_noche(T):   # F10: esa noche, con Sofía dormida, pasas por el desván… y la luz está encendida
    t0 = S("B8") - .3; tp = WT("B8", "pasas") - .2; te = WT("B8", "encendida.") - .1
    if T < tp:
        c = bgz("bg_cuarto_sofia", T, t0, 1.05, 1.0, 4).copy(); noche(c, 165)
        sofia_dormida(c, 540, 760, .85, T)
        if T >= WT("B8", "noche,") - .1: rotulo(c, T, WT("B8", "noche,") - .1, "ESA NOCHE", 540, 300, fill=(40, 40, 90), fg=WHITE, size=54, rot=-3)
        return c
    # el pasillo oscuro: la escalera del desván y una raya de luz bajo la puerta
    c = Image.new("RGBA", (W, H), (22, 20, 40, 255)); d = ImageDraw.Draw(c)
    on = 1.0 if T >= te else .35 + .1 * math.sin(T * 9)
    for k in range(9):   # peldaños
        y = 1500 - k * 95; w2 = 420 - k * 22
        d.polygon([(540 - w2, y), (540 + w2, y), (540 + w2 - 20, y - 70), (540 - w2 + 20, y - 70)], fill=(70 - k * 3, 52 - k * 2, 46), outline=(20, 14, 20))
    d.rectangle((360, 210, 720, 640), fill=(92, 62, 44), outline=(14, 10, 16), width=10)
    d.rectangle((390, 240, 690, 610), outline=(60, 40, 30), width=6)
    d.ellipse((650, 420, 676, 446), fill=(220, 180, 80))
    glow(c, 540, 650, 240 + 120 * (on - .35), (255, 210, 110), 170 * on, 40)
    d = ImageDraw.Draw(c); d.rectangle((370, 636, 710, 650), fill=(255, 230, 150))
    for x in (356, 724): d.line((x, 210, x, 640), fill=(255, 220, 130, int(200 * on)), width=6)
    if T >= te: rotulo(c, T, te, "ENCENDIDA", 540, 1180, fill=(255, 220, 120), size=56, rot=-2)
    return c

def sc_pagina(T):   # F11-F12: en el cuaderno hay una página nueva; la tinta todavía brilla; y dice… (voz de la abuela)
    t0 = S("B8") - .5; tf = WT("B8", "página") - .2; tf1 = tf + 1.0
    c = fondo_libro(T, t0, 7, 150)
    glow(c, 540, 760, 520, (255, 200, 120), 120, 80)   # luz de la lámpara del desván
    blank = None
    if T < tf:
        cuaderno_abierto(c, *CB, T, izq_O(), None)
        return c
    if "blank" not in _PAGE: _PAGE["blank"] = pagina_img_de(None)
    if T < tf1:   # la página gira sola
        cuaderno_abierto(c, *CB, T, izq_O(), der_msg2(T, 1e9, 1e9 + 1, False))
        uu = clamp((T - tf) / (tf1 - tf)); hoja_girando(c, uu * uu * (3 - 2 * uu), _PAGE["blank"], _PAGE["blank"])
        return c
    # página nueva: la tinta brilla; el texto se ve al leerlo la voz de tu mamá
    t_a, t_b = S("F12"), E("F12") - .3
    def izq_blank(cc, x0, y0, s): cc.alpha_composite(_PAGE["blank"], (int(x0), int(y0)))
    if T < t_a:   # todavía no se lee: solo un brillo de tinta mojada
        cuaderno_abierto(c, *CB, T, izq_blank, der_msg2(1e9))
        reg = c.crop((int(PX_R), int(PY), int(PX_R + PW), int(PY + PH))).filter(ImageFilter.GaussianBlur(9))
        c.paste(reg, (int(PX_R), int(PY)))
    else:
        cuaderno_abierto(c, *CB, T, izq_blank, der_msg2(T, t_a, t_b))
    tinta_brilla(c, T, tf1, PX_R, PY, PW, PH)
    if T >= WT("B8", "nueva.") - .1 and T < t_a: rotulo(c, T, WT("B8", "nueva.") - .1, "PÁGINA NUEVA", 540, 300, fill=(255, 255, 255), fg=TINTA, size=52)
    if T >= WT("B8", "brilla.") - .1 and T < t_a: rotulo(c, T, WT("B8", "brilla.") - .1, "TINTA FRESCA", 540, 1250, fill=(255, 220, 120), size=54)
    if T >= WT("F12", "F.") - .1: rotulo(c, T, WT("F12", "F.") - .1, "MAÑANA: LA F", 540, 300, fill=ORO, size=52)
    if T >= WT("F12", "mayor.") - .2: rotulo(c, T, WT("F12", "mayor.") - .2, "¿QUÉ QUIERE SER?", 540, 1250, size=52, rot=2)
    return c

def sc_ventana(T):   # F13: miras por la ventana… en la casa de enfrente, una luz se apaga (pista sin comentar: un pañuelo de flores)
    t0 = S("F13") - .4; toff = WT("F13", "apaga.") + .05
    c = Image.new("RGBA", (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(c)
    for y in range(0, H, 8):   # cielo
        k = y / H; d.rectangle((0, y, W, y + 8), fill=(int(14 + 20 * k), int(18 + 22 * k), int(52 + 40 * k)))
    r = random.Random(5)
    for k in range(60):
        x, y = r.uniform(0, W), r.uniform(0, 900); a = int(150 + 100 * math.sin(T * 2 + k)); d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 255, 230, a))
    d.ellipse((150, 220, 290, 360), fill=(255, 246, 200))
    # la casa de enfrente
    d.polygon([(180, 760), (540, 470), (900, 760)], fill=(40, 32, 58), outline=(10, 8, 20))
    d.rectangle((230, 760, 850, 1500), fill=(52, 44, 72), outline=(10, 8, 20), width=6)
    for (x, y) in ((330, 880), (330, 1150), (750, 1150)):
        d.rectangle((x - 70, y - 80, x + 70, y + 80), fill=(26, 24, 44), outline=(10, 8, 20), width=6)
    on = T < toff or (toff <= T < toff + .25 and int((T - toff) * 30) % 2 == 0)
    x, y = 750, 880
    if on:
        d.rectangle((x - 70, y - 80, x + 70, y + 80), fill=(255, 214, 120), outline=(10, 8, 20), width=6)
        # silueta con pañuelo de flores (sin comentar)
        d.ellipse((x - 26, y - 30, x + 26, y + 26), fill=(60, 40, 50))
        d.polygon([(x - 40, y - 8), (x, y - 50), (x + 40, y - 8), (x + 30, y + 10), (x - 30, y + 10)], fill=(150, 110, 190))
        for (fx, fy) in ((x - 18, y - 18), (x + 14, y - 26), (x + 4, y - 4)): d.ellipse((fx - 5, fy - 5, fx + 5, fy + 5), fill=(245, 150, 180))
        d.polygon([(x - 50, y + 80), (x - 36, y + 26), (x + 36, y + 26), (x + 50, y + 80)], fill=(60, 40, 50))
        glow(c, x, y, 160, (255, 210, 110), 90, 40); d = ImageDraw.Draw(c)
        for k in range(2): d.line((x - 70 + k * 140, y - 80, x - 70 + k * 140, y + 80), fill=(10, 8, 20), width=6)
    # nuestro marco de ventana en primer plano y la cortina
    d.rectangle((0, 0, W, 110), fill=(120, 84, 58)); d.rectangle((0, 1380, W, H), fill=(120, 84, 58))
    d.rectangle((0, 0, 60, H), fill=(120, 84, 58)); d.rectangle((W - 60, 0, W, H), fill=(120, 84, 58))
    d.rectangle((520, 0, 560, 1400), fill=(120, 84, 58)); d.rectangle((0, 720, W, 760), fill=(120, 84, 58))
    d.polygon([(0, 0), (230, 0), (150, 1400), (0, 1400)], fill=(214, 150, 170, 235))
    if T >= WT("F13", "enfrente,") - .1 and T < toff: rotulo(c, T, WT("F13", "enfrente,") - .1, "LA CASA DE ENFRENTE", 540, 1300, fill=(255, 255, 255), fg=TINTA, size=46)
    if T >= toff: rotulo(c, T, toff, "SE APAGA", 540, 1300, fill=(40, 40, 90), fg=WHITE, size=54, rot=-3)
    return c

_FC = {}
def _lado(name):
    if name in _FC: return _FC[name]
    if name == "A":   # te quedas a vigilar: el desván a oscuras, la puerta entreabierta
        im = Image.new("RGBA", (W, H), (20, 20, 50, 255)); put(im, "bg_desvan", 300, 960, 1.0); R.dark(im, 150)
        noche(im, 90); d = ImageDraw.Draw(im)
        d.rectangle((120, 900, 420, 1500), fill=(80, 56, 40), outline=OL, width=8)
        d.polygon([(420, 900), (520, 940), (520, 1460), (420, 1500)], fill=(255, 214, 120))
        glow(im, 470, 1200, 200, (255, 210, 110), 120, 40)
        im.alpha_composite(Image.new("RGBA", (W, H), (40, 40, 140, 60)))
    else:   # le dejas una respuesta: el cuaderno con tu letra y un lápiz
        im = Image.new("RGBA", (W, H), (255, 220, 170, 255)); put(im, "bg_desvan", 780, 960, 1.0)
        put(im, "cuaderno", 820, 980, .5, rot=8)
        lay = Image.new("RGBA", (380, 300), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        dl.rounded_rectangle((0, 0, 379, 299), 14, fill=(255, 255, 250), outline=OL, width=5)
        dl.text((190, 90), "¿Mamá?", font=font(F_HAND, 72), fill=TINTA, anchor="mm")
        dl.text((190, 190), "¿Eres tú?", font=font(F_HAND, 66), fill=TINTA, anchor="mm")
        lay = lay.rotate(-6, expand=True, resample=Image.BICUBIC); im.alpha_composite(lay, (610, 1040))
        im.alpha_composite(Image.new("RGBA", (W, H), (255, 160, 120, 40)))
    _FC[name] = im
    return im

def sc_final(T):   # F14: el dilema, como en Mateo
    s0 = S("B9"); ta = WT("B9", "vigilar") - .35; tb = WT("B9", "respuesta") - .35
    hiA = ta <= T < tb; hiB = T >= tb
    A_, B_ = _lado("A"), _lado("B"); negro = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    u = ease((T - s0 + .3) / .45)
    c = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    c.alpha_composite(Image.blend(B_, negro, .5) if hiA else B_, (int(500 * (1 - u)), 0))
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon([(0, 0)] + RAYO + [(0, H)], fill=255)
    c.paste(Image.blend(A_, negro, .5) if hiB else A_, (int(-700 * (1 - u)), 0), mask)
    d = ImageDraw.Draw(c)
    if u > .9:
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).line(RAYO, fill=(255, 210, 120, 255), width=40, joint="curve")
        c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(c)
        d.line(RAYO, fill=WHITE, width=12, joint="curve"); d.line(RAYO, fill=YEL, width=5, joint="curve")
    k0 = R.popscale(T, s0 - .2, .4)
    if k0 > 0: d.text((540, 230), "¿QUÉ HARÍAS TÚ?", font=font(F_ANTON, int(96 * k0) + 1), fill=YEL, anchor="mm", stroke_width=9, stroke_fill=OL)
    for k in range(5):
        x = 540 + (k - 2) * 86; y = 345
        d.rounded_rectangle((x - 34, y - 42, x + 34, y + 42), 10, fill=(40, 28, 60), outline=ORO, width=4)
        d.text((x, y), "C" if k == 0 else "?", font=font(F_BAL, 52), fill=ORO if k == 0 else (130, 110, 160), anchor="mm")
    _tarjeta(c, 262, 720, "A", ["TE QUEDAS", "A VIGILAR"], "quizá lo descubres", "noche sin dormir", (96, 78, 200), R.popscale(T, ta, .35), 1.07 if hiA else 1.0)
    _tarjeta(c, 818, 720, "B", ["LE DEJAS", "UNA", "RESPUESTA"], "te contesta", "no sabrás quién es", (226, 76, 108), R.popscale(T, tb, .35), 1.07 if hiB else 1.0)
    return c

def etiqueta_serie(c, T):
    d = ImageDraw.Draw(c); f = font(F_BAL, 34); txt = "EL CUADERNO DE LA ABUELA · PARTE 2"
    tw = d.textlength(txt, font=f)
    d.rounded_rectangle((540 - tw / 2 - 26, 176, 540 + tw / 2 + 26, 236), 18, fill=(250, 240, 214, 235), outline=OL, width=4)
    d.text((540, 207), txt, font=f, fill=(90, 60, 110), anchor="mm")

def _blank(): 
    if "blank" not in _PAGE: _PAGE["blank"] = pagina_img_de(None)
    return _PAGE["blank"]

def sc_b1(T):   # B1 (segundo 0): primer plano de la página con tinta fresca, borrosa, brillando; luego se abre el plano
    c = fondo_libro(T, 0, 6, 150); glow(c, 540, 760, 520, (255, 200, 120), 150 + int(20 * math.sin(T * 9)), 80)
    _blank()
    def izq_blank(cc, x0, y0, s): cc.alpha_composite(_PAGE["blank"], (int(x0), int(y0)))
    cuaderno_abierto(c, *CB, T, izq_blank, der_msg2(1e9))
    reg = c.crop((int(PX_R), int(PY), int(PX_R + PW), int(PY + PH))).filter(ImageFilter.GaussianBlur(11))
    c.paste(reg, (int(PX_R), int(PY)))
    tinta_brilla(c, T, 0, PX_R, PY, PW, PH)
    rotulo(c, T, -.2, "¡TINTA FRESCA!", 540, 330, fill=(255, 220, 120), size=78, rot=-3)
    if T >= WT("B1", "madre…") - .1: rotulo(c, T, WT("B1", "madre…") - .1, "EL CUADERNO DE TU MADRE", 540, 1330, fill=(255, 255, 255), fg=TINTA, size=42, rot=2)
    return c

def sc_b2(T):   # B2: el reloj gira hacia atrás: 12 horas antes
    t0 = S("B2") - .12
    c = bgz("bg_cuarto_sofia", T, t0, 1.0, 1.08, 3).copy(); R.dark(c, 110)
    d = ImageDraw.Draw(c); cx, cy, r = 540, 840, 330
    d.ellipse((cx - r - 16, cy - r - 16, cx + r + 16, cy + r + 16), fill=(60, 44, 70), outline=OL, width=8)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(250, 244, 226), outline=OL, width=6)
    for k in range(12):
        a = k * PI_ / 6; d.line((cx + (r - 50) * math.sin(a), cy - (r - 50) * math.cos(a), cx + (r - 14) * math.sin(a), cy - (r - 14) * math.cos(a)), fill=OL, width=10)
    u = T - t0; am = -u * 26; ah = -u * 26 / 12 - .4
    d.line((cx, cy, cx + (r - 70) * math.sin(am), cy - (r - 70) * math.cos(am)), fill=(190, 40, 60), width=12)
    d.line((cx, cy, cx + (r - 140) * math.sin(ah), cy - (r - 140) * math.cos(ah)), fill=OL, width=18)
    d.ellipse((cx - 20, cy - 20, cx + 20, cy + 20), fill=OL)
    if T >= WT("B2", "Doce") - .05: rotulo(c, T, WT("B2", "Doce") - .05, "12 H ANTES", 540, 330, fill=(255, 255, 255), fg=TINTA, size=64, rot=-3)
    return c

def sc_b3(T):   # B3: Sofía llora con su O torcida
    t0 = S("B3") - .12
    c = bgz("bg_cuarto_sofia", T, t0, 1.06, 1.0, 4).copy()
    sofia(c, "llora", 540, 560, .88, T, "B3"); lagrimas(c, 540, 560, .88, T)
    hoja_huevo(c, 540, 1130, 1.18, -4 + 2 * math.sin(T * 5), clamp((T - t0 - .2) / .6))
    if T >= WT("B3", "papa!") - .1: rotulo(c, T, WT("B3", "papa!") - .1, "¡UNA PAPA!", 540, 330, size=60, rot=-3)
    return c

def sc_b4(T):   # B4: la nota pegada: "Para: Andrea"; ganó la opción B
    t0 = S("B4") - .15
    c = fondo_libro(T, t0, 6, 40); glow(c, 540, 800, 420, (255, 214, 120), 130, 70)
    cuaderno_abierto(c, *CB, T, izq_reverso, der_msg(1e9))
    n = nota_andrea(1.0, -8 + 2 * math.sin(T * 3))
    c.alpha_composite(n, (int(PX_R + PW / 2 - n.width / 2), int(PY + 230 + 5 * math.sin(T * 4))))
    brillos(c, T, t0, PX_R + PW / 2, PY + 330, 220, (255, 236, 160), 10)
    tj = WT("B4", "juntas.") - .45
    if WT("B4", "nota.") - .05 <= T < tj: rotulo(c, T, WT("B4", "nota.") - .05, "UNA NOTA", 540, 330, size=52, rot=-3)
    if T >= tj: rotulo(c, T, tj, "GANÓ: LA ABREN JUNTAS", 540, 330, fill=(120, 214, 140), size=44, rot=-2)
    return c

def sc_carta(T):   # F04: la nota abierta, con la letra de tu mamá (voz de la abuela)
    ta = S("F04") - .15
    c = fondo_libro(T, ta, 7, 40); c.alpha_composite(Image.new("RGBA", (W, H), (255, 200, 140, 30))); R.dark(c, 60)
    u = back((T - ta) / .5); w, h = int(820 * u) + 2, int(900 * u) + 2
    lay = Image.new("RGBA", (820, 900), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    dl.rounded_rectangle((0, 0, 819, 899), 18, fill=(255, 243, 175), outline=OL, width=6)
    dl.line((0, 450, 819, 450), fill=(230, 210, 130), width=4); dl.line((410, 0, 410, 899), fill=(236, 218, 140), width=3)
    lay = lay.rotate(2, expand=True, resample=Image.BICUBIC).resize((max(2, int(w)), max(2, int(h))))
    c.alpha_composite(lay, (int(540 - lay.width / 2), int(800 - lay.height / 2)))
    if u > .9:
        manuscrito(c, CARTA, T, S("F04"), E("F04") - .2, 540, 420, 78, TINTA, 118, 2)
        if T >= E("F04") - .2: ImageDraw.Draw(c).text((700, 1060), "— R.", font=font(F_HAND, 64), fill=TINTA)
    rotulo(c, T, ta + .1, "LETRA DE TU MAMÁ", 760, 330, fill=(255, 255, 255), fg=TINTA, size=44, rot=3)
    if T >= WT("F04", "redondo.") - .05:
        uu = ease((T - WT("F04", "redondo.") + .05) / .6); trazo(c, recorrido(o_path(540, 870, 310, 125), uu), 10, ROSA)
    return c

def sc_b8(T):   # B8: vuelves a la página mojada; la tinta se aclara y se lee (voz de la abuela en F12)
    t0 = S("B8") - .3; t_a, t_b = S("F12"), E("F12") - .3
    c = fondo_libro(T, t0, 7, 150); glow(c, 540, 760, 520, (255, 200, 120), 120, 80)
    _blank()
    def izq_blank(cc, x0, y0, s): cc.alpha_composite(_PAGE["blank"], (int(x0), int(y0)))
    if T < t_a:
        cuaderno_abierto(c, *CB, T, izq_blank, der_msg2(1e9))
        reg = c.crop((int(PX_R), int(PY), int(PX_R + PW), int(PY + PH))).filter(ImageFilter.GaussianBlur(max(1, 10 * (1 - clamp((T - WT("B8", "leerla.")) / .6)))))
        c.paste(reg, (int(PX_R), int(PY)))
    else:
        cuaderno_abierto(c, *CB, T, izq_blank, der_msg2(T, t_a, t_b))
    tinta_brilla(c, T, t0, PX_R, PY, PW, PH)
    if T >= WT("B8", "página") - .1 and T < t_a: rotulo(c, T, WT("B8", "página") - .1, "LA PÁGINA MOJADA", 540, 300, fill=(255, 255, 255), fg=TINTA, size=50)
    if T >= WT("B8", "leerla.") - .1 and T < t_a: rotulo(c, T, WT("B8", "leerla.") - .1, "¡SE PUEDE LEER!", 540, 1250, fill=(255, 220, 120), size=54)
    if T >= WT("F12", "F.") - .1: rotulo(c, T, WT("F12", "F.") - .1, "MAÑANA: LA F", 540, 300, fill=ORO, size=52)
    if T >= WT("F12", "mayor.") - .2: rotulo(c, T, WT("F12", "mayor.") - .2, "¿QUÉ QUIERE SER?", 540, 1250, size=52, rot=2)
    return c

SCENES = [
    (0, sc_b1), (S("B2") - .12, sc_b2), (S("B3") - .12, sc_b3), (S("B4") - .15, sc_b4), (S("F04") - .15, sc_carta),
    (S("B5") - .15, sc_flash), (S("B6") - .15, sc_imprimeO), (WT("B6", "abrazas") - .2, sc_abrazo),
    (WT("B6", "crayola") - .2, sc_trazaO), (S("B7") - .1, sc_redondita), (S("F08B") - .15, sc_pregunta),
    (S("F08C") - .15, sc_tardes), (S("B8") - .3, sc_b8), (S("F13") - .4, sc_ventana), (S("B9") - .2, sc_final),
]
IMPACTS = [S("B4") + .3, WT("B1", "mojada."), WT("F13", "apaga."), WT("B7", "O!")]
SUAVES = {S("B5") - .15, S("F08C") - .15, S("B8") - .3}

SHOTS = {
    "sc_b1": (1.1, [(790, 760, 2.7), (700, 900, 2.1), (840, 700, 2.3), (640, 800, 1.5), (540, 800, 1.15), (540, 800, 1.0)]),
    "sc_b2": (1.1, [(540, 840, 1.0), (540, 840, 1.45)]),
    "sc_b3": (1.1, [(540, 820, 1.1), (540, 960, 1.3), (540, 700, 1.2)]),
    "sc_b4": (1.2, [(540, 800, 1.0), (820, 700, 1.7), (540, 820, 1.2)]),
    "sc_carta": (1.6, [(540, 800, 1.0), (540, 650, 1.35), (540, 900, 1.3), (540, 800, 1.05)]),
    "sc_flash": (1.6, [(540, 820, 1.0), (500, 640, 1.45), (600, 1000, 1.55), (540, 820, 1.1)]),
    "sc_imprimeO": (1.0, [(540, 900, 1.0), (540, 1000, 1.35)]),
    "sc_abrazo": (1.0, [(540, 900, 1.0), (540, 760, 1.4)]),
    "sc_trazaO": (1.5, [(540, 760, 1.0), (440, 780, 1.6), (540, 760, 1.15), (640, 780, 1.6)]),
    "sc_redondita": (1.3, [(540, 900, 1.0), (540, 700, 1.4), (540, 1150, 1.4)]),
    "sc_pregunta": (1.4, [(540, 760, 1.25), (540, 960, 1.0)]),
    "sc_tardes": (1.6, [(540, 800, 1.0), (540, 700, 1.3)]),
    "sc_b8": (1.4, [(540, 800, 1.0), (780, 760, 1.5), (540, 800, 1.1), (780, 700, 1.6), (780, 880, 1.7), (540, 800, 1.05)]),
    "sc_ventana": (1.4, [(540, 960, 1.0), (750, 900, 1.7), (680, 920, 2.4)]),
    "sc_final": (99, [(540, 960, 1.0)]),
}

def camara(c, name, T, t0):
    iv, shots = SHOTS.get(name, (99, [(540, 960, 1.0)]))
    k = int((T - t0) / iv); cx, cy, z = shots[k % len(shots)]
    u = ((T - t0) % iv) / iv; z = z * (1 + .025 * u)          # deriva lenta dentro de cada plano
    if z <= 1.001 and abs(cx - 540) < 1 and abs(cy - 960) < 1: return c
    z = max(z, 1.0); hw, hh = W / (2 * z), H / (2 * z)
    cx = min(max(cx, hw), W - hw); cy = min(max(cy, hh), H - hh)
    return c.crop((int(cx - hw), int(cy - hh), int(cx + hw), int(cy + hh))).resize((W, H), Image.BICUBIC)

def escena(i, T):
    """Pinta la escena i en T con su plano de cámara; los rótulos van encima, sin zoom."""
    t0, fn = SCENES[i]
    _OV.append(Image.new("RGBA", (W, H), (0, 0, 0, 0)))
    try:
        c = fn(T); c = camara(c, fn.__name__, T, t0)
        c.alpha_composite(_OV[-1])
    finally:
        _OV.pop()
    return c

TW = .22
def frame(T):
    idx = max(i for i, (t, f) in enumerate(SCENES) if T >= t)
    t0, fn = SCENES[idx]
    c = escena(idx, T)
    u = (T - t0) / TW
    if idx > 0 and u < 1 and t0 not in SUAVES:   # whip-pan
        e = ease(u); prev = escena(idx - 1, T)
        k = int(2 + 22 * math.sin(PI_ * u))
        cv = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        cv.alpha_composite(R.hblur(prev, k), (int(-W * e), 0)); cv.alpha_composite(R.hblur(c, k), (int(W * (1 - e)), 0))
        c = cv
    elif idx > 0 and (T - t0) < .4 and t0 in SUAVES:
        prev = escena(idx - 1, T); c = Image.blend(prev, c, ease((T - t0) / .4))
    punch = sum(.025 * math.exp(-(T - ch[0]) * 9) for ch in R.CH if 0 <= T - ch[0] < .5)
    zz = 1 + punch + .02 * ((T - t0) / 6 % 1)
    if zz > 1.002:
        cc = c.resize((int(W * zz), int(H * zz)), Image.BILINEAR)
        ox = (cc.width - W) / 2 + 6 * math.sin(T * .7); oy = (cc.height - H) / 2 + 5 * math.cos(T * .5)
        c = cc.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    amp = sum(12 * math.exp(-(T - ti) * 7) for ti in IMPACTS if 0 <= T - ti < .7)
    if amp > .6:
        cc = c.resize((int(W * 1.04), int(H * 1.04)), Image.BILINEAR)
        ox = (cc.width - W) / 2 + amp * math.sin(T * 95); oy = (cc.height - H) / 2 + amp * math.cos(T * 71)
        c = cc.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    c.alpha_composite(R.VIG)
    c.alpha_composite(R.grains()[int(T * 24) % 4])
    if T < S("B9") - .2: etiqueta_serie(c, T)
    R.draw_caption(c, T)
    return c.convert("RGB")

def render_scene(i, out):
    t0 = SCENES[i][0]; t1 = SCENES[i + 1][0] if i + 1 < len(SCENES) else TOTAL
    f0, f1 = round(t0 * FPS), round(t1 * FPS)
    tmp = out[:-4] + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-crf", "17", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
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
        with Pool(int(os.environ.get("JOBS", "3"))) as pool:
            pool.starmap(render_scene, [(i, os.path.join(TMP, f"s{i:02d}.mp4")) for i in ids])