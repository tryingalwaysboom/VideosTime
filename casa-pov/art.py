"""Dibujos de "La casa de 1 dólar" (2D con perspectiva, de noche). Cada plancha se dibuja a PW x PH y se encuadra con cámara."""
import math, os, random
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
PW, PH = 1296, 2304
F_ANTON = os.path.join(HERE, "fonts/Anton-Regular.ttf")
F_HAND = os.path.join(HERE, "fonts/Caveat.ttf")
F_UI = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
F_REG = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
if not os.path.exists(F_REG): F_REG = F_UI

@lru_cache(None)
def font(p, s): return ImageFont.truetype(p, max(1, int(s)))

def lerp(a, b, u): return a + (b - a) * u
def mix(c1, c2, u): return tuple(int(lerp(a, b, u)) for a, b in zip(c1, c2))

def grad(w, h, top, bot, y0=0, y1=None):
    y1 = h if y1 is None else y1
    t = np.clip((np.arange(h) - y0) / max(1, (y1 - y0)), 0, 1)[:, None, None]
    a = np.array(top, float)[None, None, :]; b = np.array(bot, float)[None, None, :]
    arr = (a + (b - a) * t) * np.ones((1, w, 1))
    return Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")

def soft(size, fn, blur):
    """Capa RGBA dibujada con fn(d) y desenfocada."""
    im = Image.new("RGBA", size, (0, 0, 0, 0)); fn(ImageDraw.Draw(im)); return im.filter(ImageFilter.GaussianBlur(blur))

def noise_tex(w, h, amt, seed=0, scale=1):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, amt, (h // scale + 1, w // scale + 1))
    im = Image.fromarray(np.clip(128 + n, 0, 255).astype(np.uint8), "L")
    return im.resize((w, h), Image.BILINEAR)

def add_grain(im, amt=10, seed=0):
    n = np.asarray(noise_tex(im.width, im.height, amt, seed), np.int16) - 128
    a = np.asarray(im.convert("RGB"), np.int16) + n[..., None]
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    return out

def quad_pt(q, u, v):
    """Punto bilineal dentro del cuadrilátero q = [TL, TR, BR, BL]."""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = q
    tx, ty = lerp(x0, x1, u), lerp(y0, y1, u)
    bx, by = lerp(x3, x2, u), lerp(y3, y2, u)
    return (lerp(tx, bx, v), lerp(ty, by, v))

def sub_quad(q, u0, v0, u1, v1):
    return [quad_pt(q, u0, v0), quad_pt(q, u1, v0), quad_pt(q, u1, v1), quad_pt(q, u0, v1)]

def towards(p, vp, s): return (lerp(p[0], vp[0], s), lerp(p[1], vp[1], s))

def vignette(w, h, strength=200, r=.75):
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - w / 2) / (w * r)) ** 2 + ((yy - h / 2) / (h * r)) ** 2)
    a = np.clip((d - .55) / .6, 0, 1) ** 1.6 * strength
    v = np.zeros((h, w, 4), np.uint8); v[..., 3] = a.astype(np.uint8)
    return Image.fromarray(v, "RGBA")

# ------------------------------------------------------------------ CONTRATO (mesa vista desde arriba)
PAPEL = [(250, 330), (1050, 300), (1090, 1830), (230, 1860)]

@lru_cache(1)
def plate_contrato():
    im = Image.new("RGBA", (PW, PH), (60, 38, 24, 255)); d = ImageDraw.Draw(im)
    for i in range(0, PH, 150):   # tablones de la mesa
        c = (70 + (i // 150 % 3) * 8, 44 + (i // 150 % 2) * 6, 26)
        d.rectangle((0, i, PW, i + 146), fill=c + (255,)); d.line((0, i + 147, PW, i + 147), fill=(30, 18, 10, 255), width=4)
    rng = random.Random(3)
    for _ in range(260):   # vetas
        y = rng.randrange(PH); x = rng.randrange(-200, PW); L = rng.randrange(150, 600)
        d.line((x, y, x + L, y + rng.randrange(-6, 6)), fill=(40, 24, 12, 90), width=rng.choice((1, 2, 3)))
    sh = soft((PW, PH), lambda dd: dd.polygon([(x + 30, y + 40) for x, y in PAPEL], fill=(0, 0, 0, 170)), 30); im.alpha_composite(sh)
    paper = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); pd = ImageDraw.Draw(paper)
    pd.polygon(PAPEL, fill=(238, 228, 200, 255))
    # manchas y bordes amarillentos
    stain = soft((PW, PH), lambda dd: [dd.ellipse((x - r, y - r, x + r, y + r), fill=(170, 140, 80, 60)) for x, y, r in ((900, 520, 90), (380, 1650, 120), (960, 1700, 60))], 25)
    paper.alpha_composite(stain)
    pd = ImageDraw.Draw(paper)
    def tl(u, v): return quad_pt(PAPEL, u, v)
    def line(u, v, s, sz, col=(40, 32, 28), f=F_REG):
        x, y = tl(u, v); pd.text((x, y), s, font=font(f, sz), fill=col, anchor="lm")
    x, y = tl(.5, .07); pd.text((x, y), "CONTRATO DE COMPRAVENTA", font=font(F_ANTON, 64), fill=(35, 28, 26), anchor="mm")
    x, y = tl(.5, .115); pd.text((x, y), "Inmueble: Calle del Olvido, nº 13", font=font(F_REG, 32), fill=(80, 70, 60), anchor="mm")
    pd.line((*tl(.08, .145), *tl(.92, .145)), fill=(60, 50, 40), width=3)
    line(.09, .2, "PRECIO DE VENTA:", 40, f=F_UI); line(.6, .2, "$1", 64, (170, 30, 30), F_ANTON)
    for k in range(5):   # texto de relleno (líneas grises)
        v = .27 + k * .035
        pd.line((*tl(.09, v), *tl(.9 - .1 * (k % 2), v)), fill=(150, 140, 120), width=10)
    line(.09, .47, "CLÁUSULA 7", 44, (35, 28, 26), F_ANTON)
    line(.09, .52, "El comprador deberá REFORMAR", 37, f=F_UI)
    line(.09, .555, "la casa en un plazo de 12 MESES.", 37, f=F_UI)
    line(.09, .615, "Si no cumple, PIERDE la casa", 37, f=F_UI)
    line(.09, .65, "y la FIANZA de $5,000.", 37, f=F_UI)
    for k in range(4):
        v = .71 + k * .035
        pd.line((*tl(.09, v), *tl(.88 - .12 * (k % 2), v)), fill=(150, 140, 120), width=10)
    pd.line((*tl(.52, .92), *tl(.9, .92)), fill=(40, 32, 28), width=3)
    x, y = tl(.56, .895); pd.text((x, y), "Comprador", font=font(F_HAND, 64), fill=(30, 50, 120), anchor="lm")
    im.alpha_composite(paper)
    # bolígrafo
    pen = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); d2 = ImageDraw.Draw(pen)
    d2.line((150, 2120, 560, 1960), fill=(20, 20, 30, 255), width=34); d2.line((560, 1960, 610, 1941), fill=(200, 200, 205, 255), width=22)
    d2.line((160, 2112, 400, 2020), fill=(70, 70, 90, 255), width=6)
    im.alpha_composite(soft((PW, PH), lambda dd: dd.line((170, 2150, 590, 1990), fill=(0, 0, 0, 140), width=40), 14)); im.alpha_composite(pen)
    # luz de lámpara cálida
    im.alpha_composite(soft((PW, PH), lambda dd: dd.ellipse((200, 300, 1150, 1700), fill=(255, 200, 120, 40)), 160))
    return add_grain(im, 6, 1)

def paper_xy(u, v): return quad_pt(PAPEL, u, v)

def billete(scale=1.0, rot=-8):
    w, h = int(520 * scale), int(230 * scale)
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, 20 + w, 20 + h), 10, fill=(196, 214, 176), outline=(70, 100, 60), width=5)
    d.rounded_rectangle((38, 38, 2 + w, 2 + h), 6, outline=(90, 120, 80), width=3)
    d.ellipse((20 + w / 2 - h * .32, 20 + h * .18, 20 + w / 2 + h * .32, 20 + h * .82), fill=(160, 186, 140), outline=(70, 100, 60), width=4)
    d.text((20 + w / 2, 20 + h / 2), "$", font=font(F_ANTON, h * .5), fill=(60, 90, 55), anchor="mm")
    for cx in (20 + h * .3, 20 + w - h * .3):
        d.text((cx, 20 + h * .28), "1", font=font(F_ANTON, h * .32), fill=(60, 90, 55), anchor="mm")
        d.text((cx, 20 + h * .74), "1", font=font(F_ANTON, h * .32), fill=(60, 90, 55), anchor="mm")
    d.text((20 + w / 2, 20 + h * .12), "ONE DOLLAR", font=font(F_UI, h * .09), fill=(60, 90, 55), anchor="mm")
    return im.rotate(rot, expand=True, resample=Image.BICUBIC)

def sello(texto, sub=None, col=(205, 30, 40), rot=-14, s=1.0):
    f = font(F_ANTON, 120 * s); tw = int(f.getlength(texto)) + int(80 * s)
    hh = int((230 if sub else 170) * s)
    im = Image.new("RGBA", (tw + 40, hh + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, 20 + tw, 20 + hh), int(18 * s), outline=col + (235,), width=int(12 * s))
    d.text((20 + tw / 2, 20 + (85 if sub else 85) * s), texto, font=f, fill=col + (235,), anchor="mm")
    if sub: d.text((20 + tw / 2, 20 + 180 * s), sub, font=font(F_ANTON, 64 * s), fill=col + (235,), anchor="mm")
    m = noise_tex(im.width, im.height, 60, 7, 3).point(lambda v: 255 if v > 100 else 120)   # tinta irregular
    a = Image.fromarray((np.asarray(im.split()[3], np.float32) * np.asarray(m, np.float32) / 255).astype(np.uint8))
    im.putalpha(a)
    return im.rotate(rot, expand=True, resample=Image.BICUBIC)

# ------------------------------------------------------------------ FACHADA (contrapicado, 2 puntos de fuga)
VPL, VPR = (-1700, 1560), (3600, 1500)
CORNER_T, CORNER_B = (780, 760), (780, 1760)

def casa_geom():
    sL, sR = .30, .13
    LT = towards(CORNER_T, VPL, sL); LB = towards(CORNER_B, VPL, sL)
    RT = towards(CORNER_T, VPR, sR); RB = towards(CORNER_B, VPR, sR)
    front = [LT, CORNER_T, CORNER_B, LB]          # cara izquierda (fachada con puerta)
    side = [CORNER_T, RT, RB, CORNER_B]            # cara derecha
    mid = ((LT[0] + CORNER_T[0]) / 2, (LT[1] + CORNER_T[1]) / 2)
    apex = (mid[0], mid[1] - 360)
    apexR = towards(apex, VPR, sR)
    return front, side, apex, apexR, LT, RT

@lru_cache(1)
def plate_casa():
    im = grad(PW, PH, (6, 9, 26), (40, 46, 88), 0, 1560)
    d = ImageDraw.Draw(im); rng = random.Random(5)
    for _ in range(220):
        x, y = rng.randrange(PW), rng.randrange(1300); r = rng.choice((1, 1, 2, 2, 3))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(230, 235, 255, rng.randrange(90, 255)))
    mx, my = 1040, 470
    im.alpha_composite(soft((PW, PH), lambda dd: dd.ellipse((mx - 420, my - 420, mx + 420, my + 420), fill=(150, 170, 255, 70)), 120))
    im.alpha_composite(soft((PW, PH), lambda dd: dd.ellipse((mx - 190, my - 190, mx + 190, my + 190), fill=(220, 230, 255, 120)), 40))
    d = ImageDraw.Draw(im)
    d.ellipse((mx - 120, my - 120, mx + 120, my + 120), fill=(240, 240, 228))
    for cx, cy, r in ((-40, -30, 26), (35, 20, 18), (-10, 55, 14), (50, -55, 10)):
        d.ellipse((mx + cx - r, my + cy - r, mx + cx + r, my + cy + r), fill=(215, 215, 205))
    # nubes oscuras
    for cx, cy, rw, rh, a in ((760, 560, 330, 60, 200), (1180, 610, 260, 46, 180), (300, 380, 380, 70, 150), (980, 330, 220, 40, 120)):
        im.alpha_composite(soft((PW, PH), lambda dd: dd.ellipse((cx - rw, cy - rh, cx + rw, cy + rh), fill=(14, 16, 36, a)), 22))
    d = ImageDraw.Draw(im)
    # colinas
    pts = [(0, 1500)] + [(x, 1470 - 60 * math.sin(x / 260) - 30 * math.sin(x / 90 + 1)) for x in range(0, PW + 40, 40)] + [(PW, PH), (0, PH)]
    d.polygon(pts, fill=(18, 22, 44))
    pts = [(0, 1600)] + [(x, 1580 - 40 * math.sin(x / 200 + 2)) for x in range(0, PW + 40, 40)] + [(PW, PH), (0, PH)]
    d.polygon(pts, fill=(14, 18, 34))
    # árbol seco a la izquierda
    def rama(x, y, a, L, w, n):
        if n == 0 or L < 12: return
        x2, y2 = x + L * math.cos(a), y - L * math.sin(a)
        d.line((x, y, x2, y2), fill=(8, 9, 18), width=max(2, int(w)))
        rama(x2, y2, a + .45 + rng.uniform(-.15, .15), L * .72, w * .66, n - 1)
        rama(x2, y2, a - .4 + rng.uniform(-.15, .15), L * .68, w * .66, n - 1)
    rama(150, 1900, math.pi / 2 + .08, 420, 46, 7)
    # casa
    front, side, apex, apexR, LT, RT = casa_geom()
    WOOD_F, WOOD_S = (66, 74, 96), (88, 98, 128)
    d.polygon(front, fill=WOOD_F); d.polygon(side, fill=WOOD_S)
    for k in range(1, 26):   # tablas horizontales (siding)
        v = k / 26
        d.line((*quad_pt(front, 0, v), *quad_pt(front, 1, v)), fill=(46, 52, 72), width=3)
        d.line((*quad_pt(side, 0, v), *quad_pt(side, 1, v)), fill=(62, 70, 96), width=3)
    # pintura descascarillada
    for _ in range(40):
        u, v = rng.random(), rng.random(); q = sub_quad(front, u, v, min(1, u + .05), min(1, v + .03))
        d.polygon(q, fill=(40, 44, 60))
    # tejado
    roofF = [apex, LT, CORNER_T]
    d.polygon([(apex[0], apex[1] - 14), (LT[0] - 50, LT[1] + 30), (CORNER_T[0] + 30, CORNER_T[1] + 24)], fill=(26, 24, 34))
    d.polygon([apex, apexR, (RT[0] + 30, RT[1] + 22), (CORNER_T[0] + 30, CORNER_T[1] + 24)], fill=(38, 34, 46))
    for k in range(1, 9):   # tejas en la vertiente lateral
        u = k / 9
        a = (lerp(apex[0], CORNER_T[0] + 30, u), lerp(apex[1], CORNER_T[1] + 24, u)); b = (lerp(apexR[0], RT[0] + 30, u), lerp(apexR[1], RT[1] + 22, u))
        d.line((*a, *b), fill=(22, 20, 30), width=4)
    d.polygon([(apex[0] - 2, apex[1] + 30), (LT[0] + 10, LT[1] + 4), (CORNER_T[0] - 6, CORNER_T[1] + 4)], fill=(58, 64, 86))   # frontón
    # ventana redonda del desván (frontón)
    ax, ay = apex[0], apex[1] + 210
    d.ellipse((ax - 52, ay - 52, ax + 52, ay + 52), fill=(12, 12, 20), outline=(30, 30, 42), width=10)
    d.line((ax - 52, ay, ax + 52, ay), fill=(30, 30, 42), width=6); d.line((ax, ay - 52, ax, ay + 52), fill=(30, 30, 42), width=6)
    # chimenea
    d.polygon([towards(apex, VPR, .06), towards(apex, VPR, .085), (towards(apex, VPR, .085)[0], apex[1] - 120), (towards(apex, VPR, .06)[0], apex[1] - 110)], fill=(48, 36, 40))
    def ventana(face, u0, v0, u1, v1, rota=False, tablas=True):
        q = sub_quad(face, u0, v0, u1, v1)
        d.polygon(sub_quad(face, u0 - .02, v0 - .015, u1 + .02, v1 + .02), fill=(30, 34, 48))
        d.polygon(q, fill=(10, 12, 22))
        if rota:
            cx, cy = quad_pt(q, .55, .45)
            d.polygon([quad_pt(q, .2, .1), (cx, cy), quad_pt(q, .9, .2), quad_pt(q, .95, .9), quad_pt(q, .1, .95)], fill=(24, 30, 52))
        d.line((*quad_pt(q, .5, 0), *quad_pt(q, .5, 1)), fill=(34, 36, 50), width=7); d.line((*quad_pt(q, 0, .5), *quad_pt(q, 1, .5)), fill=(34, 36, 50), width=7)
        if tablas:
            for a, b in ((.15, .35), (.6, .8)):
                d.polygon([quad_pt(q, -.08, a), quad_pt(q, 1.08, a + .12), quad_pt(q, 1.08, a + .24), quad_pt(q, -.08, b)], fill=(92, 70, 50), outline=(50, 36, 26))
    ventana(front, .1, .16, .34, .42, tablas=True)
    ventana(front, .66, .16, .9, .42, rota=True, tablas=False)
    ventana(side, .2, .16, .78, .4, tablas=True)
    ventana(side, .2, .55, .78, .78, rota=True, tablas=False)
    # puerta + porche
    door = sub_quad(front, .38, .55, .62, 1.0)
    d.polygon(sub_quad(front, .35, .52, .65, 1.0), fill=(34, 36, 48)); d.polygon(door, fill=(54, 34, 26))
    for a, b in ((.08, .45), (.55, .92)):
        d.polygon(sub_quad(door, .15, a, .85, b), outline=(36, 22, 16), width=5)
    kx, ky = quad_pt(door, .82, .58); d.ellipse((kx - 9, ky - 9, kx + 9, ky + 9), fill=(170, 140, 70))
    p0, p1 = quad_pt(front, .26, 1.0), quad_pt(front, .74, 1.0)
    for k in range(3):   # escalones
        y = p0[1] + 18 + k * 30
        d.polygon([(p0[0] - 20 - k * 22, y), (p1[0] + 20 + k * 22, y - 8), (p1[0] + 20 + k * 22, y + 30), (p0[0] - 20 - k * 22, y + 38)], fill=(50, 46, 56), outline=(30, 28, 36))
    # luz de luna en la arista
    d.line((*CORNER_T, *CORNER_B), fill=(140, 156, 200), width=6)
    # suelo, hierba, valla
    d.polygon([(0, 1860), (PW, 1820), (PW, PH), (0, PH)], fill=(16, 22, 26))
    for _ in range(500):
        x = rng.randrange(PW); y = rng.randrange(1800, PH); h = rng.randrange(14, 50)
        d.line((x, y, x + rng.randrange(-10, 10), y - h), fill=(28 + rng.randrange(20), 40 + rng.randrange(25), 34), width=3)
    for i, x in enumerate(range(-20, PW + 60, 92)):   # valla rota en primer plano
        if i in (4, 9): continue
        top = 1880 + (i % 3) * 18 - (40 if i % 4 == 0 else 0); lean = (i % 5 - 2) * 8
        d.polygon([(x, 2304), (x + 60, 2304), (x + 60 + lean, top + 24), (x + 30 + lean, top), (x + lean, top + 24)], fill=(26, 24, 30), outline=(12, 12, 16))
    d.polygon([(-20, 2010), (PW, 1990), (PW, 2030), (-20, 2050)], fill=(30, 28, 34))
    # cartel SE VENDE $1
    sx, sy = 1050, 1700
    d.line((sx, sy, sx + 10, sy + 420), fill=(40, 30, 22), width=22)
    sign = Image.new("RGBA", (380, 250), (0, 0, 0, 0)); sd = ImageDraw.Draw(sign)
    sd.rectangle((10, 10, 370, 240), fill=(218, 206, 172), outline=(70, 50, 30), width=8)
    sd.text((190, 76), "SE VENDE", font=font(F_ANTON, 80), fill=(40, 30, 26), anchor="mm")
    sd.text((190, 178), "$1", font=font(F_ANTON, 112), fill=(190, 30, 30), anchor="mm")
    sign = sign.rotate(7, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(sign, (sx - 190, sy - 150))
    # niebla
    for y, a in ((1720, 70), (1840, 90), (1960, 60)):
        im.alpha_composite(soft((PW, PH), lambda dd: dd.rectangle((-100, y - 40, PW + 100, y + 40), fill=(150, 160, 200, a)), 40))
    return add_grain(im, 7, 2)

ATTIC = None
def attic_xy():
    _, _, apex, *_ = casa_geom(); return apex[0], apex[1] + 210

# ------------------------------------------------------------------ PASILLO (un punto de fuga)
VP = (648, 1060)
FAR = (468, 820, 828, 1330)   # pared del fondo

def far_rect(): return FAR

@lru_cache(1)
def plate_pasillo():
    im = Image.new("RGBA", (PW, PH), (0, 0, 0, 255)); d = ImageDraw.Draw(im)
    fx0, fy0, fx1, fy1 = FAR
    L = [(0, 0), (fx0, fy0), (fx0, fy1), (0, PH)]; R = [(PW, 0), (fx1, fy0), (fx1, fy1), (PW, PH)]
    C = [(0, 0), (PW, 0), (fx1, fy0), (fx0, fy0)]; F = [(0, PH), (PW, PH), (fx1, fy1), (fx0, fy1)]
    d.polygon(C, fill=(34, 32, 40)); d.polygon(L, fill=(62, 58, 74)); d.polygon(R, fill=(56, 54, 70)); d.polygon(F, fill=(58, 40, 30))
    d.rectangle(FAR, fill=(44, 42, 56))
    # papel pintado: rayas que fugan
    for k in range(1, 14):
        u = k / 14
        for wall, col in ((L, (52, 48, 64)), (R, (48, 46, 62))):
            a = (lerp(wall[0][0], wall[1][0], u), lerp(wall[0][1], wall[1][1], u)); b = (lerp(wall[3][0], wall[2][0], u), lerp(wall[3][1], wall[2][1], u))
            d.line((*a, *b), fill=col, width=int(lerp(18, 4, u)))
    # zócalo
    for wall in (L, R):
        for v in (.86, .9):
            pass
    d.polygon([(0, PH - 300), (fx0, fy1 - 46), (fx0, fy1), (0, PH)], fill=(44, 32, 26))
    d.polygon([(PW, PH - 300), (fx1, fy1 - 46), (fx1, fy1), (PW, PH)], fill=(40, 30, 24))
    # tablas del suelo
    for k in range(-6, 7):
        x_near = PW / 2 + k * 170; x_far = lerp(fx0, fx1, (k + 6.5) / 13)
        d.line((x_near, PH, x_far, fy1), fill=(36, 24, 18), width=5)
    z = 1.0
    for k in range(1, 14):
        z = 1 / (1 + k * .35); y = lerp(fy1, PH, (z - 1 / (1 + 14 * .35)) / (1 - 1 / (1 + 14 * .35)))
        x0 = lerp(fx0, 0, (y - fy1) / (PH - fy1)); x1 = lerp(fx1, PW, (y - fy1) / (PH - fy1))
        d.line((x0, y, x1, y), fill=(42, 28, 20), width=3)
    # puerta del fondo entreabierta (oscura) con luz de luna
    d.rectangle((fx0 + 110, fy0 + 120, fx1 - 110, fy1), fill=(14, 14, 22)); d.rectangle((fx0 + 104, fy0 + 114, fx1 - 104, fy1), outline=(70, 60, 54), width=8)
    d.polygon([(fx0 + 118, fy0 + 128), (fx0 + 170, fy0 + 140), (fx0 + 170, fy1 - 6), (fx0 + 118, fy1)], fill=(60, 50, 44))
    # ventana en la pared derecha con rayo de luna
    win = [(1080, 520), (1210, 380), (1210, 980), (1080, 1010)]
    d.polygon(win, fill=(120, 140, 200)); d.line((1145, 450, 1145, 995), fill=(40, 40, 56), width=10); d.line((1080, 760, 1210, 690), fill=(40, 40, 56), width=10)
    d.polygon(win, outline=(30, 28, 36), width=16)
    im.alpha_composite(soft((PW, PH), lambda dd: dd.polygon([(1080, 520), (1210, 380), (700, 2100), (180, 1900)], fill=(150, 170, 255, 46)), 30))
    # cuadro torcido en la pared izquierda
    pic = [(150, 640), (380, 700), (390, 1000), (150, 990)]
    d = ImageDraw.Draw(im)
    d.polygon(pic, fill=(80, 60, 40)); d.polygon([quad_pt(pic, .12, .1), quad_pt(pic, .88, .1), quad_pt(pic, .88, .9), quad_pt(pic, .12, .9)], fill=(60, 66, 70))
    hx, hy = quad_pt(pic, .5, .45); d.ellipse((hx - 34, hy - 50, hx + 34, hy + 30), fill=(40, 42, 46))
    # muebles tapados con sábanas
    def sabana(pts, base, seed):
        lay = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); sd = ImageDraw.Draw(lay)
        sd.polygon(pts, fill=base + (255,))
        r2 = random.Random(seed); xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        for _ in range(9):   # pliegues
            x = r2.uniform(min(xs) + 20, max(xs) - 20); sd.line((x, min(ys) + 40, x + r2.uniform(-30, 30), max(ys)), fill=tuple(int(c * .78) for c in base) + (255,), width=r2.randrange(6, 14))
        msk = Image.new("L", (PW, PH), 0); ImageDraw.Draw(msk).polygon(pts, fill=255)
        lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.split()[3]), np.asarray(msk))))
        sh = soft((PW, PH), lambda dd: dd.ellipse((min(xs) - 20, max(ys) - 30, max(xs) + 40, max(ys) + 40), fill=(0, 0, 0, 160)), 18)
        im.alpha_composite(sh); im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.2)))
    sabana([(20, 1500), (110, 1360), (300, 1330), (420, 1400), (460, 1560), (480, 1980), (0, 2010)], (178, 180, 192), 1)   # sillón
    sabana([(860, 1100), (1010, 1060), (1050, 1080), (1060, 1560), (850, 1600)], (160, 164, 180), 2)                       # armario
    sabana([(560, 1240), (600, 1200), (720, 1196), (760, 1240), (770, 1320), (550, 1324)], (130, 132, 150), 3)             # sofá al fondo
    # telarañas
    d = ImageDraw.Draw(im)
    for cx, cy, sgx, sgy in ((0, 0, 1, 1), (PW, 0, -1, 1)):
        for a in range(0, 90, 15):
            r = math.radians(a); d.line((cx, cy, cx + sgx * 320 * math.cos(r), cy + sgy * 320 * math.sin(r)), fill=(200, 200, 210, 70), width=2)
        for rr in (80, 150, 230, 300):
            pts = [(cx + sgx * rr * math.cos(math.radians(a)), cy + sgy * rr * math.sin(math.radians(a))) for a in range(0, 91, 15)]
            d.line(pts, fill=(200, 200, 210, 60), width=2)
    return add_grain(im, 8, 3)

# ------------------------------------------------------------------ PUERTA (porche, vista frontal)
DOOR = (388, 640, 908, 1900)

@lru_cache(1)
def plate_porche():
    im = Image.new("RGBA", (PW, PH), (50, 56, 76, 255)); d = ImageDraw.Draw(im)
    for y in range(0, PH, 64): d.line((0, y, PW, y), fill=(38, 42, 58), width=4)
    x0, y0, x1, y1 = DOOR
    d.rectangle((x0 - 70, y0 - 80, x1 + 70, y1 + 20), fill=(42, 36, 34)); d.rectangle((x0 - 40, y0 - 50, x1 + 40, y1 + 10), fill=(30, 26, 26))
    d.polygon([(0, 1950), (PW, 1950), (PW, PH), (0, PH)], fill=(40, 32, 30))
    for x in range(-80, PW, 150): d.line((x, PH, x + 60, 1950), fill=(28, 22, 20), width=6)
    # aplique de luz rota
    d.rectangle((x1 + 120, 900, x1 + 170, 1000), fill=(20, 20, 24)); d.ellipse((x1 + 115, 880, x1 + 175, 920), fill=(34, 34, 40))
    im.alpha_composite(soft((PW, PH), lambda dd: dd.ellipse((-200, 200, 900, 1600), fill=(140, 160, 230, 40)), 120))
    return add_grain(im, 7, 4)

def door_leaf(w, h):
    im = Image.new("RGBA", (w, h), (78, 50, 36, 255)); d = ImageDraw.Draw(im)
    for x in range(0, w, 26): d.line((x, 0, x + 6, h), fill=(66, 42, 30), width=3)
    for a, b in ((.06, .44), (.54, .94)):
        for c, e in ((.1, .46), (.54, .9)):
            d.rectangle((w * c, h * a, w * e, h * b), outline=(46, 28, 20), width=10)
            d.rectangle((w * c + 10, h * a + 10, w * e - 10, h * b - 10), outline=(96, 66, 48), width=3)
    d.ellipse((w * .84 - 22, h * .5 - 22, w * .84 + 22, h * .5 + 22), fill=(176, 146, 72), outline=(90, 70, 30), width=4)
    d.rectangle((w * .84 - 10, h * .5 + 34, w * .84 + 10, h * .5 + 70), fill=(60, 48, 30))
    d.rounded_rectangle((w * .4, h * .015, w * .6, h * .05), 8, fill=(160, 130, 70)); d.text((w * .5, h * .033), "13", font=font(F_ANTON, 46), fill=(50, 34, 20), anchor="mm")
    return add_grain(im, 8, 5)

# ------------------------------------------------------------------ CALENDARIO 1987
@lru_cache(1)
def plate_calendario():
    im = Image.new("RGBA", (PW, PH), (70, 64, 60, 255)); d = ImageDraw.Draw(im)
    for x in range(0, PW, 90):   # papel pintado viejo
        d.rectangle((x, 0, x + 44, PH), fill=(78, 70, 64))
        for y in range(40, PH, 140): d.ellipse((x + 52, y, x + 82, y + 30), fill=(86, 74, 66))
    stain = soft((PW, PH), lambda dd: [dd.ellipse((x - r, y - r, x + r, y + r), fill=(40, 34, 30, 120)) for x, y, r in ((200, 400, 200), (1100, 1900, 260), (300, 2000, 160))], 60)
    im.alpha_composite(stain)
    cx0, cy0, cx1, cy1 = 230, 520, 1066, 1880
    im.alpha_composite(soft((PW, PH), lambda dd: dd.rectangle((cx0 + 24, cy0 + 34, cx1 + 24, cy1 + 34), fill=(0, 0, 0, 160)), 24))
    d = ImageDraw.Draw(im)
    d.rectangle((cx0, cy0, cx1, cy1), fill=(226, 214, 186))
    # foto descolorida (playa)
    ph = (cx0 + 40, cy0 + 40, cx1 - 40, cy0 + 520)
    d.rectangle(ph, fill=(160, 186, 190)); d.rectangle((ph[0], ph[1] + 300, ph[2], ph[3]), fill=(120, 150, 170)); d.rectangle((ph[0], ph[1] + 390, ph[2], ph[3]), fill=(200, 180, 140))
    d.ellipse((ph[2] - 200, ph[1] + 60, ph[2] - 90, ph[1] + 170), fill=(240, 220, 160))
    d.line((ph[0] + 140, ph[3], ph[0] + 180, ph[1] + 180), fill=(90, 70, 50), width=14)
    for a in range(-60, 61, 30):
        r = math.radians(a - 90); d.line((ph[0] + 180, ph[1] + 180, ph[0] + 180 + 130 * math.cos(r), ph[1] + 180 + 60 * math.sin(r) + 40), fill=(70, 110, 70), width=12)
    d.text(((cx0 + cx1) / 2, cy0 + 610), "OCTUBRE", font=font(F_ANTON, 120), fill=(150, 30, 30), anchor="mm")
    d.text(((cx0 + cx1) / 2, cy0 + 750), "1987", font=font(F_ANTON, 150), fill=(40, 32, 30), anchor="mm")
    gx0, gy0, cw, ch = cx0 + 60, cy0 + 860, (cx1 - cx0 - 120) / 7, 110
    for i, s in enumerate("LMXJVSD"): d.text((gx0 + cw * (i + .5), gy0), s, font=font(F_UI, 36), fill=(90, 70, 60), anchor="mm")
    for n in range(1, 32):
        k = n + 2; r, c = divmod(k, 7)
        d.text((gx0 + cw * (c + .5), gy0 + 80 + r * ch), str(n), font=font(F_UI, 44), fill=(60, 50, 46), anchor="mm")
        if n < 13: # días tachados
            x, y = gx0 + cw * (c + .5), gy0 + 80 + r * ch; d.line((x - 30, y - 30, x + 30, y + 30), fill=(60, 60, 80), width=5)
    k = 15; r, c = divmod(k, 7); x, y = gx0 + cw * (c + .5), gy0 + 80 + r * ch
    d.ellipse((x - 52, y - 46, x + 52, y + 46), outline=(190, 30, 30), width=8)
    # clavo y telaraña
    d.ellipse((640, 470, 660, 490), fill=(60, 60, 64)); d.line((650, 480, cx0 + 60, cy0), fill=(40, 36, 34), width=3); d.line((650, 480, cx1 - 60, cy0), fill=(40, 36, 34), width=3)
    for a in range(0, 90, 18):
        rr = math.radians(a); d.line((cx1, cy0, cx1 - 260 * math.cos(rr), cy0 + 260 * math.sin(rr)), fill=(230, 230, 230, 110), width=2)
    for rr in (70, 140, 210):
        d.line([(cx1 - rr * math.cos(math.radians(a)), cy0 + rr * math.sin(math.radians(a))) for a in range(0, 91, 18)], fill=(230, 230, 230, 90), width=2)
    # amarillento
    im.alpha_composite(Image.new("RGBA", (PW, PH), (110, 80, 30, 40)))
    return add_grain(im, 9, 6)

CAL_DAY13 = None
def cal13():
    cx0, cy0, cx1 = 230, 520, 1066; gx0, gy0, cw, ch = cx0 + 60, cy0 + 860, (cx1 - cx0 - 120) / 7, 110
    r, c = divmod(15, 7); return gx0 + cw * (c + .5), gy0 + 80 + r * ch

# ------------------------------------------------------------------ DOÑA REMEDIOS en la valla
SKIN = (214, 170, 140)

@lru_cache(1)
def plate_remedios_bg():
    im = grad(PW, PH, (8, 10, 28), (30, 34, 64), 0, 1500); d = ImageDraw.Draw(im)
    rng = random.Random(9)
    for _ in range(120):
        x, y = rng.randrange(PW), rng.randrange(1100); d.point((x, y), fill=(220, 225, 255))
    # silueta de la casa al fondo (desenfocada)
    back = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); bd = ImageDraw.Draw(back)
    bd.polygon([(820, 1250), (1010, 1060), (1200, 1250), (1200, 1600), (820, 1600)], fill=(20, 22, 38))
    bd.rectangle((880, 1300, 940, 1380), fill=(10, 10, 16)); bd.rectangle((1080, 1300, 1140, 1380), fill=(10, 10, 16))
    bd.ellipse((990, 1150, 1030, 1190), fill=(10, 10, 16))
    bd.polygon([(0, 1480), (PW, 1440), (PW, PH), (0, PH)], fill=(16, 20, 30))
    im.alpha_composite(back.filter(ImageFilter.GaussianBlur(6)))
    return im

def remedios(c, ox, oy, mouth=0.0, blink=0.0, s=1.0):
    """Dibuja a Doña Remedios (busto) con el centro de la cara en (ox, oy)."""
    lay = Image.new("RGBA", c.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    S = lambda v: v * s
    # cuerpo con chal
    d.polygon([(ox - S(330), oy + S(900)), (ox - S(290), oy + S(400)), (ox - S(150), oy + S(260)), (ox + S(150), oy + S(260)), (ox + S(290), oy + S(400)), (ox + S(330), oy + S(900))], fill=(70, 40, 70))
    for k in range(-5, 6):
        d.line((ox + S(k * 50), oy + S(300), ox + S(k * 62), oy + S(900)), fill=(56, 30, 56), width=int(S(6)))
    d.polygon([(ox - S(150), oy + S(260)), (ox, oy + S(520)), (ox + S(150), oy + S(260)), (ox + S(90), oy + S(250)), (ox, oy + S(330)), (ox - S(90), oy + S(250))], fill=(110, 60, 60))   # cuello del vestido
    for i in range(7):   # flecos del chal
        x = ox - S(280) + i * S(18); d.line((x, oy + S(440), x - S(6), oy + S(520)), fill=(56, 30, 56), width=int(S(5)))
    d.rectangle((ox - S(60), oy + S(150), ox + S(60), oy + S(280)), fill=mix(SKIN, (0, 0, 0), .15))   # cuello
    # pelo (moño gris)
    d.ellipse((ox - S(200), oy - S(300), ox + S(200), oy + S(60)), fill=(170, 170, 176))
    d.ellipse((ox - S(90), oy - S(400), ox + S(90), oy - S(250)), fill=(160, 160, 168))
    # cara
    d.ellipse((ox - S(165), oy - S(210), ox + S(165), oy + S(210)), fill=SKIN)
    d.ellipse((ox - S(190), oy - S(30), ox - S(140), oy + S(60)), fill=mix(SKIN, (0, 0, 0), .1)); d.ellipse((ox + S(140), oy - S(30), ox + S(190), oy + S(60)), fill=mix(SKIN, (0, 0, 0), .1))
    d.ellipse((ox - S(184), oy + S(40), ox - S(164), oy + S(66)), fill=(220, 190, 90)); d.ellipse((ox + S(164), oy + S(40), ox + S(184), oy + S(66)), fill=(220, 190, 90))
    # flequillo
    d.chord((ox - S(170), oy - S(230), ox + S(170), oy - S(20)), 180, 360, fill=(176, 176, 182))
    for k in range(-4, 5): d.arc((ox + S(k * 34) - S(60), oy - S(220), ox + S(k * 34) + S(60), oy - S(90)), 200, 340, fill=(140, 140, 150), width=int(S(4)))
    # ojos
    for sx in (-1, 1):
        ex, ey = ox + sx * S(66), oy - S(18)
        d.line((ex - S(48), ey - S(52) + sx * 0, ex + S(44), ey - S(60) - sx * S(-8)), fill=(110, 110, 116), width=int(S(12)))   # ceja
        hh = S(26) * (1 - blink)
        d.ellipse((ex - S(36), ey - hh, ex + S(36), ey + hh), fill=(244, 240, 232))
        if hh > S(4):
            d.ellipse((ex - S(17) + sx * S(4), ey - min(hh, S(17)), ex + S(17) + sx * S(4), ey + min(hh, S(17))), fill=(50, 34, 26))
            d.ellipse((ex - S(6) + sx * S(4), ey - S(9), ex + S(2) + sx * S(4), ey - S(1)), fill=(255, 255, 255))
        d.arc((ex - S(40), ey - S(34), ex + S(40), ey + S(30)), 200, 340, fill=(130, 90, 70), width=int(S(6)))   # párpado
        d.arc((ex - S(38), ey + S(10), ex + S(38), ey + S(48)), 20, 160, fill=(170, 120, 100), width=int(S(4)))  # ojeras
        for k in range(3): d.line((ex + sx * S(46), ey + S(k * 10 - 8), ex + sx * S(66), ey + S(k * 14 - 14)), fill=(170, 120, 100), width=int(S(3)))
    # nariz
    d.line((ox, oy - S(10), ox - S(16), oy + S(70)), fill=(170, 120, 96), width=int(S(5))); d.arc((ox - S(30), oy + S(50), ox + S(20), oy + S(90)), 0, 180, fill=(170, 120, 96), width=int(S(5)))
    # arrugas
    for sx in (-1, 1): d.arc((ox + sx * S(70) - S(60), oy + S(40), ox + sx * S(70) + S(60), oy + S(160)), 90 + sx * 45 - 30, 90 + sx * 45 + 30, fill=(176, 126, 104), width=int(S(4)))
    for k in range(3): d.arc((ox - S(80), oy - S(170) + k * S(18), ox + S(80), oy - S(110) + k * S(18)), 200, 340, fill=(190, 140, 116), width=int(S(3)))
    # boca
    my = oy + S(128); mw = S(52); mo = S(4) + S(34) * mouth
    d.ellipse((ox - mw, my - mo / 2, ox + mw, my + mo / 2 + S(2)), fill=(80, 30, 34))
    if mo > S(14): d.ellipse((ox - mw * .6, my + mo * .1, ox + mw * .6, my + mo / 2), fill=(170, 70, 70))
    d.arc((ox - mw - S(4), my - mo / 2 - S(8), ox + mw + S(4), my + mo / 2 + S(4)), 180, 360, fill=(150, 80, 80), width=int(S(6)))
    c.alpha_composite(lay)

def farol(c, x, y, T, s=1.0):
    d = ImageDraw.Draw(c); fl = .85 + .15 * math.sin(T * 17) * math.sin(T * 5.3)
    c.alpha_composite(soft(c.size, lambda dd: dd.ellipse((x - 520 * s, y - 520 * s, x + 520 * s, y + 520 * s), fill=(255, 170, 70, int(70 * fl))), 120))
    d = ImageDraw.Draw(c)
    d.line((x, y - 160 * s, x, y - 110 * s), fill=(30, 26, 20), width=int(8 * s)); d.arc((x - 40 * s, y - 200 * s, x + 40 * s, y - 120 * s), 180, 360, fill=(30, 26, 20), width=int(8 * s))
    d.polygon([(x - 60 * s, y - 110 * s), (x + 60 * s, y - 110 * s), (x + 50 * s, y + 90 * s), (x - 50 * s, y + 90 * s)], fill=(255, 200, 110), outline=(40, 32, 24))
    d.rectangle((x - 70 * s, y + 90 * s, x + 70 * s, y + 120 * s), fill=(40, 32, 24)); d.rectangle((x - 70 * s, y - 130 * s, x + 70 * s, y - 110 * s), fill=(40, 32, 24))
    d.ellipse((x - 18 * s, y - 30 * s, x + 18 * s, y + 40 * s), fill=(255, 250, 220))
    c.alpha_composite(soft(c.size, lambda dd: dd.ellipse((x - 120 * s, y - 140 * s, x + 120 * s, y + 140 * s), fill=(255, 210, 120, int(120 * fl))), 30))

def valla(c, y0):
    d = ImageDraw.Draw(c)
    d.rectangle((0, y0 + 80, c.width, y0 + 130), fill=(84, 64, 46)); d.rectangle((0, y0 + 330, c.width, y0 + 380), fill=(84, 64, 46))
    for x in range(-30, c.width + 80, 120):
        d.polygon([(x, y0 + 900), (x + 84, y0 + 900), (x + 84, y0 + 30), (x + 42, y0 - 20), (x, y0 + 30)], fill=(110, 86, 62), outline=(60, 44, 30))
        d.line((x + 20, y0 + 60, x + 22, y0 + 880), fill=(96, 74, 52), width=4)

# ------------------------------------------------------------------ RELOJ 3:00
@lru_cache(1)
def plate_reloj():
    im = grad(PW, PH, (14, 14, 26), (26, 24, 36)); d = ImageDraw.Draw(im)
    # mesita en perspectiva
    d.polygon([(80, 1300), (1220, 1300), (1296, 1560), (0, 1560)], fill=(70, 46, 32)); d.rectangle((0, 1560, PW, 2304), fill=(52, 34, 24))
    d.line((0, 1560, PW, 1560), fill=(90, 62, 42), width=8)
    d.rectangle((140, 1700, 1150, 1980), outline=(36, 22, 16), width=10); d.ellipse((620, 1820, 680, 1880), fill=(170, 140, 70))
    # ventana con luna detrás
    d.rectangle((760, 140, 1200, 900), fill=(30, 40, 80)); d.ellipse((960, 260, 1100, 400), fill=(230, 232, 220))
    d.line((980, 140, 980, 900), fill=(14, 14, 24), width=18); d.line((760, 520, 1200, 520), fill=(14, 14, 24), width=18); d.rectangle((760, 140, 1200, 900), outline=(14, 14, 24), width=26)
    im.alpha_composite(soft((PW, PH), lambda dd: dd.polygon([(760, 900), (1200, 900), (1100, 1540), (300, 1540)], fill=(140, 160, 230, 40)), 30))
    # cuerpo del despertador
    im.alpha_composite(soft((PW, PH), lambda dd: dd.ellipse((240, 1350, 1040, 1520), fill=(0, 0, 0, 200)), 20))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((250, 880, 1040, 1440), 70, fill=(36, 34, 40), outline=(70, 68, 78), width=8)
    d.rounded_rectangle((310, 960, 980, 1360), 40, fill=(8, 6, 8))
    return add_grain(im, 6, 8)

# ------------------------------------------------------------------ SUELO + TRAMPILLA (perspectiva desde arriba)
VPF = (648, -900)
TRAP = [(340, 1020), (960, 1020), (1070, 1660), (230, 1660)]

@lru_cache(1)
def plate_trampilla():
    im = Image.new("RGBA", (PW, PH), (70, 48, 34, 255)); d = ImageDraw.Draw(im)
    for k in range(-14, 15):   # tablas que fugan hacia arriba
        xb = PW / 2 + k * 130; xt = lerp(xb, VPF[0], .38)
        col = (74 + (k % 3) * 6, 50 + (k % 2) * 4, 34)
        d.polygon([(xb, PH), (xb + 130, PH), (lerp(xb + 130, VPF[0], .38), 0), (xt, 0)], fill=col)
        d.line((xb, PH, xt, 0), fill=(36, 24, 16), width=6)
    for y in (260, 700, 1210, 1820):
        d.line((0, y, PW, y), fill=(40, 26, 18), width=4)
    rng = random.Random(11)
    for _ in range(300):
        x, y = rng.randrange(PW), rng.randrange(PH); d.line((x, y, x + rng.randrange(-3, 3), y + rng.randrange(20, 70)), fill=(54, 36, 24), width=2)
    # trampilla
    im.alpha_composite(soft((PW, PH), lambda dd: dd.polygon(TRAP, outline=(0, 0, 0, 220), width=40), 10))
    d = ImageDraw.Draw(im)
    d.polygon(TRAP, fill=(62, 40, 28))
    for k in range(1, 6):
        u = k / 6; d.line((*quad_pt(TRAP, u, 0), *quad_pt(TRAP, u, 1)), fill=(30, 18, 12), width=8)
    d.polygon(TRAP, outline=(20, 12, 8), width=14)
    for v in (.15, .85):   # bisagras de hierro
        q = [quad_pt(TRAP, .02, v - .05), quad_pt(TRAP, .35, v - .05), quad_pt(TRAP, .35, v + .05), quad_pt(TRAP, .02, v + .05)]
        d.polygon(q, fill=(46, 44, 48), outline=(20, 20, 24))
        for u in (.08, .2, .3): x, y = quad_pt(TRAP, u, v); d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=(80, 76, 80))
    # aldaba
    hx, hy = quad_pt(TRAP, .82, .5)
    d.rectangle((hx - 90, hy - 30, hx + 40, hy + 30), fill=(50, 48, 52), outline=(20, 20, 24), width=4)
    d.ellipse((hx + 20, hy - 46, hx + 80, hy + 46), outline=(60, 58, 62), width=14)
    # polvo / arañazos alrededor
    for _ in range(40):
        a = rng.uniform(0, 6.28); r = rng.uniform(340, 520); x, y = 650 + r * math.cos(a), 1340 + r * .6 * math.sin(a)
        d.arc((x - 40, y - 10, x + 40, y + 10), 0, rng.randrange(60, 180), fill=(110, 84, 60), width=3)
    return add_grain(im, 8, 9)

def candado(c, x, y, s=1.0, brillo=0.0):
    d = ImageDraw.Draw(c)
    d.arc((x - 70 * s, y - 170 * s, x + 70 * s, y - 20 * s), 180, 360, fill=(200, 205, 212), width=int(26 * s))
    d.line((x - 70 * s, y - 95 * s, x - 70 * s, y - 20 * s), fill=(200, 205, 212), width=int(26 * s)); d.line((x + 70 * s, y - 95 * s, x + 70 * s, y - 40 * s), fill=(200, 205, 212), width=int(26 * s))
    d.rounded_rectangle((x - 110 * s, y - 40 * s, x + 110 * s, y + 170 * s), int(30 * s), fill=(218, 172, 60), outline=(120, 88, 20), width=int(6 * s))
    d.rounded_rectangle((x - 90 * s, y - 20 * s, x - 40 * s, y + 150 * s), int(20 * s), fill=(250, 220, 120))
    d.ellipse((x - 20 * s, y + 40 * s, x + 20 * s, y + 80 * s), fill=(60, 40, 10)); d.polygon([(x - 8 * s, y + 70 * s), (x + 8 * s, y + 70 * s), (x + 12 * s, y + 120 * s), (x - 12 * s, y + 120 * s)], fill=(60, 40, 10))
    if brillo > 0:
        a = int(255 * brillo); sx, sy = x - 64 * s, y - 2 * s; L = 70 * s * (.6 + .4 * brillo)
        st = Image.new("RGBA", c.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.polygon([(sx, sy - L), (sx + 9 * s, sy), (sx, sy + L), (sx - 9 * s, sy)], fill=(255, 255, 255, a))
        sd.polygon([(sx - L, sy), (sx, sy - 9 * s), (sx + L, sy), (sx, sy + 9 * s)], fill=(255, 255, 255, a))
        c.alpha_composite(st); c.alpha_composite(soft(c.size, lambda dd: dd.ellipse((sx - 40 * s, sy - 40 * s, sx + 40 * s, sy + 40 * s), fill=(255, 255, 240, a // 2)), 14))

# ------------------------------------------------------------------ FINAL: dos opciones
@lru_cache(1)
def plate_op_abrir():
    im = Image.new("RGBA", (W, H), (20, 12, 10, 255)); d = ImageDraw.Draw(im)
    for k in range(-8, 9):
        xb = W / 2 + k * 120; d.line((xb, H, lerp(xb, W / 2, .45), 0), fill=(34, 22, 16), width=5)
    q = [(300, 760), (780, 760), (880, 1260), (200, 1260)]
    im.alpha_composite(soft((W, H), lambda dd: dd.polygon(q, fill=(255, 90, 30, 200)), 60))
    d = ImageDraw.Draw(im)
    d.polygon(q, fill=(16, 6, 4))
    for k in range(5):   # escalones que bajan
        y = lerp(800, 1230, k / 5); x0 = lerp(320, 220, k / 5); x1 = lerp(760, 860, k / 5)
        d.rectangle((x0 + 60, y, x1 - 60, y + 40), fill=(90 - k * 12, 40 - k * 5, 20))
    im.alpha_composite(soft((W, H), lambda dd: dd.polygon([(360, 1000), (720, 1000), (760, 1240), (320, 1240)], fill=(255, 120, 40, 150)), 30))
    d = ImageDraw.Draw(im)
    lid = [(300, 760), (780, 760), (840, 380), (360, 380)]   # tapa abierta
    d.polygon(lid, fill=(62, 40, 28), outline=(20, 12, 8), width=10)
    for k in range(1, 6): d.line((*quad_pt(lid, k / 6, 0), *quad_pt(lid, k / 6, 1)), fill=(30, 18, 12), width=7)
    return im

@lru_cache(1)
def plate_op_tapiar():
    im = Image.new("RGBA", (W, H), (40, 34, 34, 255)); d = ImageDraw.Draw(im)
    bw, bh = 150, 70
    for r in range(0, 30):
        y = -40 + r * bh; off = (r % 2) * bw / 2
        for k in range(-1, 9):
            x = k * bw + off; col = (150 + (r * 7 + k * 13) % 30, 70 + (r * 5 + k * 11) % 20, 50)
            d.rectangle((x + 6, y + 6, x + bw - 6, y + bh - 6), fill=col)
    im.alpha_composite(soft((W, H), lambda dd: dd.ellipse((100, 300, 1000, 1500), fill=(255, 220, 150, 60)), 120))
    d = ImageDraw.Draw(im)
    # paleta de albañil + martillo
    d.polygon([(560, 1180), (860, 1060), (900, 1160), (620, 1300)], fill=(190, 196, 204), outline=(80, 84, 90), width=6)
    d.line((560, 1220, 440, 1300), fill=(120, 80, 40), width=34)
    d.line((300, 1100, 520, 900), fill=(150, 100, 50), width=30); d.polygon([(470, 860), (580, 920), (560, 960), (450, 900)], fill=(70, 72, 80))
    return im

# fachada detallada (casa_hd) sustituye a la versión simple
_plate_casa_simple = plate_casa
@lru_cache(1)
def plate_casa():
    import casa_hd
    return casa_hd.plate_casa_hd()
