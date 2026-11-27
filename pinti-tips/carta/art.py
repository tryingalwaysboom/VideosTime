"""Arte del tip «Si tu hijo es zurdo, NO hagas esto» (@escribirconpinti). Todo dibujado en código con PIL (supersampling x2).
Mismo lenguaje visual que Mateo: contorno azul marino, colores planos, tipografías Baloo 2 / Anton / Caveat."""
import os, math, random
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "..", "..", "mateo-pov", "fonts")
FONTS = {"baloo": "Baloo2-ExtraBold.ttf", "anton": "Anton-Regular.ttf", "hand": "Caveat.ttf", "andika": "Andika-Bold.ttf"}
SS = 2
OL = (29, 22, 48); SKIN = (246, 200, 160); SKINS = (226, 170, 128); HAIR = (74, 48, 34); SHIRT = (63, 127, 208)
AMA = (255, 212, 84); ROJO = (226, 72, 59); VERDE = (62, 180, 110); CREMA = (255, 253, 244); TINTA = (36, 52, 120)
ROSA = (244, 143, 160); AZULC = (150, 190, 235)


@lru_cache(None)
def font(name, size): return ImageFont.truetype(os.path.join(FD, FONTS[name]), size)

def canvas(w, h): return Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
def fin(im): return im.resize((im.width // SS, im.height // SS), Image.LANCZOS)
def P(pts): return [(x * SS, y * SS) for x, y in pts]
def ell(d, b, fill=None, out=None, w=8): d.ellipse([v * SS for v in b], fill=fill, outline=out, width=w * SS)
def rrect(d, b, r, fill=None, out=None, w=8): d.rounded_rectangle([v * SS for v in b], radius=r * SS, fill=fill, outline=out, width=w * SS)
def line(d, pts, fill, w): d.line(P(pts), fill=fill, width=int(w * SS), joint="curve")
def arc(d, b, a0, a1, fill=OL, w=8): d.arc([v * SS for v in b], a0, a1, fill=fill, width=int(w * SS))
def poly(d, pts, fill=None, out=None, w=8):
    d.polygon(P(pts), fill=fill)
    if out: d.line(P(pts + [pts[0]]), fill=out, width=w * SS, joint="curve")

def cap(d, p0, p1, r, fill, out=None, ow=6):
    """Cápsula (línea con extremos redondos), con contorno opcional."""
    if out: cap(d, p0, p1, r + ow, out)
    line(d, [p0, p1], fill, 2 * r)
    for p in (p0, p1): ell(d, (p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill)


# ------------------------------------------------------------------ niño
@lru_cache(None)
def kid(expr="neutral"):
    W, H = 700, 820
    im = canvas(W, H); d = ImageDraw.Draw(im)
    rrect(d, (90, 650, 610, 1000), 110, SHIRT, OL, 8)
    rrect(d, (300, 540, 400, 700), 30, SKINS, OL, 7)
    poly(d, [(290, 655), (350, 720), (410, 655), (380, 640), (350, 668), (320, 640)], CREMA, OL, 6)
    ell(d, (100, 350, 195, 470), SKIN, OL, 8); ell(d, (505, 350, 600, 470), SKIN, OL, 8)
    ell(d, (130, 150, 570, 600), SKIN, OL, 9)
    poly(d, [(125, 405), (128, 270), (185, 195), (290, 150), (350, 140), (430, 150), (520, 195), (572, 270), (575, 405), (525, 322),
             (470, 352), (420, 292), (355, 342), (290, 287), (235, 352), (180, 317)], HAIR, OL, 8)
    ell(d, (200, 455, 270, 505), (246, 150, 150, 150)); ell(d, (430, 455, 500, 505), (246, 150, 150, 150))
    ojos = {"asombro": (38, 50), "cansado": (36, 42)}.get(expr, (34, 42))
    for cx in (275, 425):
        if expr in ("orgulloso", "risa"):
            arc(d, (cx - 38, 385, cx + 38, 445), 200, 340, OL, 10)
            continue
        rx, ry = ojos
        ell(d, (cx - rx, 405 - ry, cx + rx, 405 + ry), (255, 255, 255), OL, 6)
        dy = 14 if expr in ("triste", "preocupado") else (8 if expr == "cansado" else 0)
        pr = 11 if expr == "asombro" else 17
        ell(d, (cx - pr, 405 - pr + dy, cx + pr, 405 + pr + dy), OL)
        ell(d, (cx - 6, 405 - pr + dy + 3, cx + 2, 405 - pr + dy + 11), (255, 255, 255))
        if expr == "cansado":
            d.rectangle([(cx - rx - 4) * SS, (405 - ry - 4) * SS, (cx + rx + 4) * SS, (405 + 2) * SS], fill=SKIN)
            line(d, [(cx - rx, 405), (cx + rx, 405)], OL, 8); arc(d, (cx - 30, 440, cx + 30, 470), 20, 160, SKINS, 6)
    # cejas
    if expr in ("triste", "preocupado"):
        line(d, [(228, 335), (305, 352)], OL, 11); line(d, [(472, 335), (395, 352)], OL, 11)
    elif expr == "cansado":
        line(d, [(232, 358), (308, 352)], OL, 11); line(d, [(468, 358), (392, 352)], OL, 11)
    elif expr in ("asombro", "feliz", "orgulloso", "risa"):
        line(d, [(232, 335), (312, 326)], OL, 10); line(d, [(468, 335), (388, 326)], OL, 10)
    else:
        line(d, [(232, 345), (312, 342)], OL, 10); line(d, [(468, 345), (388, 342)], OL, 10)
    # boca
    if expr == "feliz": arc(d, (300, 455, 400, 530), 15, 165, OL, 9)
    elif expr in ("orgulloso", "risa"):
        d.pieslice([v * SS for v in (290, 450, 410, 560)], 0, 180, fill=(150, 40, 60), outline=OL, width=8 * SS)
        d.pieslice([v * SS for v in (322, 500, 378, 556)], 0, 180, fill=(244, 120, 130))
    elif expr == "triste": arc(d, (300, 510, 400, 570), 200, 340, OL, 9)
    elif expr == "preocupado": line(d, [(310, 525), (330, 512), (350, 526), (370, 512), (390, 525)], OL, 8)
    elif expr == "asombro": ell(d, (325, 495, 375, 560), (150, 40, 60), OL, 8)
    elif expr == "cansado": line(d, [(315, 525), (385, 525)], OL, 8)
    else: arc(d, (315, 480, 385, 530), 20, 160, OL, 8)
    return fin(im)


# ------------------------------------------------------------------ iconos
@lru_cache(None)
def xmark(size=260):
    im = canvas(size, size); d = ImageDraw.Draw(im); m = size * .06
    ell(d, (m, m, size - m, size - m), ROJO, OL, 12)
    a, b = size * .3, size * .7
    line(d, [(a, a), (b, b)], (255, 255, 255), size * .14); line(d, [(b, a), (a, b)], (255, 255, 255), size * .14)
    return fin(im)

@lru_cache(None)
def check(size=260):
    im = canvas(size, size); d = ImageDraw.Draw(im); m = size * .06
    ell(d, (m, m, size - m, size - m), VERDE, OL, 12)
    line(d, [(size * .27, size * .53), (size * .44, size * .70), (size * .74, size * .34)], (255, 255, 255), size * .14)
    return fin(im)

@lru_cache(None)
def sello(texto, w=820, h=330, color=ROJO, size=210):
    im = canvas(w, h); d = ImageDraw.Draw(im)
    rrect(d, (14, 14, w - 14, h - 14), 46, None, color, 22); rrect(d, (44, 44, w - 44, h - 44), 30, None, color, 8)
    d.text((w * SS / 2, h * SS / 2 + 6 * SS), texto, font=font("anton", size * SS), fill=color, anchor="mm")
    return fin(im)

@lru_cache(None)
def globo(texto, size=64, color=(255, 255, 255), tail="left", pad=44):
    f = font("baloo", size * SS); lines = texto.split("\n")
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    tw = max(probe.textlength(l, font=f) for l in lines) / SS; th = size * 1.25 * len(lines)
    W, H = int(tw + pad * 2), int(th + pad * 1.4 + 70)
    im = canvas(W, H); d = ImageDraw.Draw(im)
    rrect(d, (8, 8, W - 8, th + pad * 1.4), 46, color, OL, 8)
    tx = {"left": [(70, th + pad * 1.4 - 4), (50, th + pad * 1.4 + 56), (130, th + pad * 1.4 - 4)],
          "right": [(W - 130, th + pad * 1.4 - 4), (W - 50, th + pad * 1.4 + 56), (W - 70, th + pad * 1.4 - 4)]}[tail]
    poly(d, tx, color, None); line(d, [tx[0], tx[1], tx[2]], OL, 8)
    d.rectangle([(tx[0][0] + 6) * SS, (tx[0][1] - 12) * SS, (tx[2][0] - 6) * SS, (tx[0][1] + 2) * SS], fill=color)
    for i, l in enumerate(lines):
        lw = d.textlength(l, font=f)
        d.text(((W * SS - lw) / 2, (pad * .7 + i * size * 1.25) * SS - 6), l, font=f, fill=OL)
    return fin(im)

@lru_cache(None)
def cerebro(size=520):
    im = canvas(size, size); d = ImageDraw.Draw(im); s = size / 520
    bumps = []
    for i in range(11):
        a = i / 11 * 2 * math.pi
        bumps.append((260 + 190 * math.cos(a), 250 + 140 * math.sin(a) * (1 if math.sin(a) < 0 else .8), 78))
    for ow in (1, 0):
        for cx, cy, r in bumps:
            b = tuple(v * s for v in (cx - r - (9 if ow else 0), cy - r - (9 if ow else 0), cx + r + (9 if ow else 0), cy + r + (9 if ow else 0)))
            ell(d, b, OL if ow else ROSA)
        ell(d, tuple(v * s for v in (110, 110, 410, 390)), ROSA) if not ow else None
    for pts in ([(260, 120), (235, 190), (285, 250), (240, 320), (262, 380)], [(130, 230), (180, 210), (215, 255)], [(390, 230), (340, 205), (310, 250)],
                [(150, 320), (200, 300), (225, 340)], [(375, 320), (325, 295), (300, 335)]):
        line(d, [(x * s, y * s) for x, y in pts], (190, 80, 110), 9 * s)
    return fin(im)

@lru_cache(None)
def corazon(size=300, color=ROJO):
    im = canvas(size, size); d = ImageDraw.Draw(im); s = size / 300
    ell(d, (20 * s, 40 * s, 160 * s, 180 * s), color, None); ell(d, (140 * s, 40 * s, 280 * s, 180 * s), color, None)
    poly(d, [(26 * s, 130 * s), (150 * s, 285 * s), (274 * s, 130 * s)], color, None)
    line(d, [(40 * s, 120 * s), (30 * s, 80 * s), (60 * s, 46 * s)], (255, 255, 255), 9 * s)
    return fin(im)

@lru_cache(None)
def estrella(size=220, color=AMA):
    im = canvas(size, size); d = ImageDraw.Draw(im); c = size / 2; pts = []
    for i in range(10):
        r = c * .92 if i % 2 == 0 else c * .42; a = -math.pi / 2 + i * math.pi / 5
        pts.append((c + r * math.cos(a), c + r * math.sin(a)))
    poly(d, pts, color, OL, 8)
    return fin(im)

@lru_cache(None)
def ojo(size=300):
    im = canvas(size, size); d = ImageDraw.Draw(im); s = size / 300
    poly(d, [(20 * s, 150 * s), (150 * s, 70 * s), (280 * s, 150 * s), (150 * s, 230 * s)], (255, 255, 255), OL, 9)
    ell(d, (100 * s, 100 * s, 200 * s, 200 * s), (63, 127, 208), OL, 7); ell(d, (128 * s, 128 * s, 172 * s, 172 * s), OL)
    ell(d, (136 * s, 122 * s, 152 * s, 138 * s), (255, 255, 255))
    return fin(im)

@lru_cache(None)
def bateria(size=320, nivel=.12):
    im = canvas(size, size // 2); d = ImageDraw.Draw(im); w, h = size, size // 2
    rrect(d, (10, 20, w - 50, h - 20), 22, (255, 255, 255), OL, 9); rrect(d, (w - 48, h * .38, w - 14, h * .62), 8, OL, OL, 4)
    rrect(d, (26, 36, 26 + (w - 100) * nivel, h - 36), 10, ROJO, None)
    return fin(im)

@lru_cache(None)
def nube(w=620):
    h = int(w * .55); im = canvas(w, h); d = ImageDraw.Draw(im); s = w / 620; col = (86, 86, 110)
    for b in ((20, 140, 240, 330), (150, 60, 400, 300), (300, 100, 560, 320), (60, 190, 580, 340)):
        ell(d, tuple(v * s for v in b), col, OL, 9)
    for b in ((20, 140, 240, 330), (150, 60, 400, 300), (300, 100, 560, 320), (60, 190, 580, 340)):
        ell(d, tuple(v * s for v in b), col)
    poly(d, [(330 * s, 280 * s), (250 * s, 400 * s), (310 * s, 395 * s), (270 * s, 520 * s), (390 * s, 360 * s), (330 * s, 365 * s), (380 * s, 280 * s)], AMA, OL, 6)
    return fin(im)

@lru_cache(None)
def gota(size=90):
    im = canvas(size, size); d = ImageDraw.Draw(im); s = size / 90
    poly(d, [(45 * s, 6 * s), (14 * s, 56 * s), (76 * s, 56 * s)], (120, 200, 250), OL, 5); ell(d, (14 * s, 36 * s, 76 * s, 84 * s), (120, 200, 250), OL, 5)
    ell(d, (16 * s, 38 * s, 74 * s, 82 * s), (120, 200, 250)); poly(d, [(45 * s, 12 * s), (18 * s, 56 * s), (72 * s, 56 * s)], (120, 200, 250))
    return fin(im)

@lru_cache(None)
def boton_seguir(w=640):
    h = 170; im = canvas(w, h); d = ImageDraw.Draw(im)
    rrect(d, (8, 8, w - 8, h - 8), 80, ROJO, OL, 9)
    f = font("baloo", 92 * SS); t = "SÍGUEME"; tw = d.textlength(t, font=f)
    d.text(((w * SS - tw) / 2, 18 * SS), t, font=f, fill=(255, 255, 255))
    return fin(im)

@lru_cache(None)
def flecha_curva(size=400, color=ROJO, flip=False):
    im = canvas(size, size); d = ImageDraw.Draw(im); s = size / 400
    arc(d, (40 * s, 40 * s, 360 * s, 360 * s), 200, 340, color, 34 * s)
    poly(d, [(318 * s, 110 * s), (390 * s, 150 * s), (300 * s, 200 * s)], color, None)
    out = fin(im); return out.transpose(Image.FLIP_LEFT_RIGHT) if flip else out

@lru_cache(None)
def flecha_doble(w=420):
    h = 110; im = canvas(w, h); d = ImageDraw.Draw(im)
    line(d, [(40, h / 2), (w - 40, h / 2)], ROJO, 16)
    poly(d, [(8, h / 2), (60, 20), (60, h - 20)], ROJO, None); poly(d, [(w - 8, h / 2), (w - 60, 20), (w - 60, h - 20)], ROJO, None)
    return fin(im)

@lru_cache(None)
def lapiz(length=820, w=64):
    """Lápiz horizontal, punta a la derecha (para cartelitos)."""
    im = canvas(length, w + 20); d = ImageDraw.Draw(im); y0 = 10
    rrect(d, (60, y0, length - 150, y0 + w), 6, AMA, OL, 7)
    poly(d, [(length - 150, y0), (length - 40, y0 + w / 2), (length - 150, y0 + w)], (240, 200, 150), OL, 7)
    poly(d, [(length - 70, y0 + w * .33), (length - 40, y0 + w / 2), (length - 70, y0 + w * .67)], OL, None)
    rrect(d, (8, y0, 70, y0 + w), 10, ROSA, OL, 7); line(d, [(76, y0), (76, y0 + w)], (190, 190, 200), 10)
    return fin(im)

def pencil_hand(grip=220):
    return _pencil_hand2(int(round(grip / 8) * 8))

@lru_cache(None)
def _pencil_hand(g):
    """Mano izquierda sujetando un lápiz; la punta está en (600, 900). `g` = distancia de los dedos a la punta."""
    W, H = 800, 1000; im = canvas(W, H); d = ImageDraw.Draw(im)
    tip = (600, 900); u = (-0.45, -0.893); n = (0.893, -0.45)
    at = lambda dist, off=0: (tip[0] + u[0] * dist + n[0] * off, tip[1] + u[1] * dist + n[1] * off)
    cap(d, at(78), at(760), 30, AMA, OL, 7)                                   # cuerpo
    poly(d, [at(78, -30), tip, at(78, 30)], (240, 200, 150), OL, 7)           # madera
    poly(d, [at(30, -11), tip, at(30, 11)], OL, None)                         # grafito
    cap(d, at(740), at(800), 30, ROSA, OL, 7)                                 # goma
    hc = at(g + 340, -70)
    cap(d, (hc[0] - 40, hc[1] - 90), (hc[0] + 40, hc[1] + 70), 150, SKIN, OL, 8)  # dorso de la mano
    cap(d, at(g, 24), at(g + 250, 56), 36, SKIN, OL, 7)                       # índice
    cap(d, at(g - 6, -26), at(g + 230, -90), 36, SKIN, OL, 7)                 # pulgar
    return fin(im)


# ------------------------------------------------------------------ hoja y letra
@lru_cache(None)
def hoja():
    W, H = 720, 900; im = canvas(W, H); d = ImageDraw.Draw(im)
    rrect(d, (52, 48, 692, 868), 28, (60, 40, 90, 70), None)                 # sombra
    rrect(d, (40, 30, 680, 850), 26, CREMA, OL, 9)
    for y in range(210, 820, 150): line(d, [(70, y), (650, y)], AZULC, 5)
    line(d, [(100, 50), (100, 830)], (235, 120, 120), 5)
    return fin(im)

def letra(lineas, modo="limpia", seed=3, size=150):
    """Capa transparente 720x900 con el texto escrito sobre los renglones de la hoja."""
    key = (tuple(lineas), modo, seed, size)
    return _letra(key)

@lru_cache(None)
def _letra(key):
    lineas, modo, seed, size = key; rnd = random.Random(seed)
    im = Image.new("RGBA", (720, 900), (0, 0, 0, 0)); f = font("hand", size)
    for li, txt in enumerate(lineas):
        y = 210 + li * 150 - 6; x = 120
        for ch in txt:
            wch = f.getlength(ch)
            if modo == "limpia":
                ImageDraw.Draw(im).text((x, y), ch, font=f, fill=TINTA, anchor="ls")
            else:
                s = rnd.uniform(.78, 1.22) if modo == "fea" else 1; g = font("hand", int(size * s))
                tile = Image.new("RGBA", (int(size * 1.4), int(size * 1.6)), (0, 0, 0, 0))
                ImageDraw.Draw(tile).text((20, int(size * 1.15)), ch, font=g, fill=TINTA, anchor="ls")
                tile = tile.rotate(rnd.uniform(-16, 16), resample=Image.BICUBIC)
                im.alpha_composite(tile, (int(x - 20), int(y - size * 1.15 + rnd.uniform(-16, 16))))
            x += wch * (1.0 if modo == "limpia" else rnd.uniform(.9, 1.15))
    return im


def texto(txt, size, fill=(255, 255, 255), stroke=9, fnt="anton", sfill=OL, spacing=0):
    return _texto(txt, size, fill, stroke, fnt, sfill, spacing)

@lru_cache(None)
def _texto(txt, size, fill, stroke, fnt, sfill, spacing):
    f = font(fnt, size); lines = txt.split("\n")
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    w = int(max(probe.textlength(l, font=f) for l in lines)) + stroke * 2 + 20; lh = int(size * (1.12 + spacing))
    im = Image.new("RGBA", (w, lh * len(lines) + stroke * 2 + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        d.text((w / 2, stroke + 10 + i * lh), l, font=f, fill=fill, anchor="ma", stroke_width=stroke, stroke_fill=sfill)
    return im


# ------------------------------------------------------------------ personajes y objetos de la carta
import numpy as np
from PIL import ImageOps

def _recolor(im, src, dst, tol=10):
    a = np.array(im); m = (np.abs(a[..., :3].astype(int) - np.array(src)).max(axis=2) <= tol) & (a[..., 3] > 0)
    a[m, :3] = dst; return Image.fromarray(a)

@lru_cache(None)
def nina(expr="feliz"):
    """Niña zurda: coletas y moño rosa."""
    k = _recolor(kid(expr), SHIRT, (240, 120, 150)); im = canvas(700, 820); d = ImageDraw.Draw(im)
    for x0 in (28, 548):
        ell(d, (x0, 290, x0 + 124, 520), HAIR, OL, 8)
    base = fin(im); base.alpha_composite(k)
    im2 = canvas(700, 820); d = ImageDraw.Draw(im2)
    poly(d, [(350, 168), (265, 112), (262, 214)], ROSA, OL, 7); poly(d, [(350, 168), (435, 112), (438, 214)], ROSA, OL, 7); ell(d, (326, 144, 374, 192), (255, 190, 205), OL, 7)
    base.alpha_composite(fin(im2)); return base

@lru_cache(None)
def mama(expr="neutral", shirt=(150, 100, 190)):
    """Mamá (o maestra con otra camiseta): pelo largo detrás, camiseta de otro color."""
    k = _recolor(kid(expr), SHIRT, shirt); im = canvas(700, 820); d = ImageDraw.Draw(im)
    rrect(d, (95, 175, 605, 800), 120, HAIR, OL, 9)
    base = fin(im); base.alpha_composite(k)
    im2 = canvas(700, 820); d = ImageDraw.Draw(im2)
    for cx in (140, 560): ell(d, (cx - 14, 470, cx + 14, 510), AMA, OL, 5)
    base.alpha_composite(fin(im2)); return base

@lru_cache(None)
def mano_der(grip=200): return ImageOps.mirror(pencil_hand(grip))

@lru_cache(None)
def luna(size=300):
    im = canvas(size, size); d = ImageDraw.Draw(im); ell(d, (20, 20, size - 20, size - 20), (255, 236, 160), OL, 10)
    ell(d, (size * .38, size * .02, size * 1.02, size * .72), (52, 46, 84)); arc(d, (20, 20, size - 20, size - 20), 90, 270, OL, 10)
    return fin(im)

@lru_cache(None)
def sol(size=360):
    im = canvas(size, size); d = ImageDraw.Draw(im); c = size / 2
    for i in range(12):
        a = i / 12 * 2 * math.pi; line(d, [(c + math.cos(a) * size * .32, c + math.sin(a) * size * .32), (c + math.cos(a) * size * .47, c + math.sin(a) * size * .47)], OL, 22)
        line(d, [(c + math.cos(a) * size * .32, c + math.sin(a) * size * .32), (c + math.cos(a) * size * .47, c + math.sin(a) * size * .47)], AMA, 11)
    ell(d, (c - size * .28, c - size * .28, c + size * .28, c + size * .28), AMA, OL, 10); return fin(im)

@lru_cache(None)
def bombilla(size=420):
    im = canvas(size, size); d = ImageDraw.Draw(im); c = size / 2
    for i in range(7):
        a = math.pi * (1.08 + i / 6 * .84); line(d, [(c + math.cos(a) * size * .36, c * .82 + math.sin(a) * size * .36), (c + math.cos(a) * size * .48, c * .82 + math.sin(a) * size * .48)], AMA, 14)
    ell(d, (c - size * .24, c * .82 - size * .26, c + size * .24, c * .82 + size * .22), AMA, OL, 10)
    rrect(d, (c - size * .12, c * .82 + size * .18, c + size * .12, c * .82 + size * .34), 10, (190, 190, 200), OL, 8); return fin(im)

@lru_cache(None)
def puerta(w=560, h=900, abierta=False):
    im = canvas(w, h); d = ImageDraw.Draw(im)
    if abierta:
        rrect(d, (10, 10, w - 10, h - 10), 18, (255, 226, 120), OL, 10)
        poly(d, [(w * .55, 10), (w - 10, 60), (w - 10, h - 60), (w * .55, h - 10)], (150, 96, 56), OL, 10)
    else:
        rrect(d, (10, 10, w - 10, h - 10), 18, (176, 116, 68), OL, 10)
        rrect(d, (60, 70, w - 60, h * .42), 12, (196, 138, 88), OL, 7); rrect(d, (60, h * .5, w - 60, h - 70), 12, (196, 138, 88), OL, 7)
        ell(d, (w - 130, h * .46, w - 90, h * .46 + 40), AMA, OL, 7)
    return fin(im)

@lru_cache(None)
def cama(w=760, h=300, color=(63, 127, 208)):
    im = canvas(w, h); d = ImageDraw.Draw(im)
    rrect(d, (10, 90, w - 10, h - 10), 36, (150, 96, 56), OL, 9); rrect(d, (10, 20, 70, h - 10), 18, (120, 76, 44), OL, 9)
    rrect(d, (80, 60, 260, 150), 40, (255, 253, 244), OL, 8); rrect(d, (30, 140, w - 30, h - 30), 30, color, OL, 9)
    return fin(im)

@lru_cache(None)
def calendario(w=640, h=560, marcas=0):
    im = canvas(w, h); d = ImageDraw.Draw(im); rrect(d, (10, 10, w - 10, h - 10), 28, CREMA, OL, 9); rrect(d, (10, 10, w - 10, 130), 28, ROJO, OL, 9)
    d.rectangle([12 * SS, 90 * SS, (w - 12) * SS, 128 * SS], fill=ROJO)
    for r in range(3):
        for c in range(5):
            x, y = 60 + c * 110, 190 + r * 110; rrect(d, (x, y, x + 80, y + 80), 14, None, AZULC, 5)
            if r * 5 + c < marcas: line(d, [(x + 14, y + 14), (x + 66, y + 66)], ROJO, 10); line(d, [(x + 66, y + 14), (x + 14, y + 66)], ROJO, 10)
    return fin(im)


HAND_W, HAND_H = 1500, 2100; TIP = (1150, 2000)
# ---- MANO ANATÓMICA: estructura de datos primero, trazos después -------------------------------------------------
# Lateralidad: IZQUIERDA · Vista: DORSO (vemos el dorso de la mano, dedos hacia arriba, pulgar a la derecha). Sistema local: muñeca (0,0), y negativo = hacia los dedos.
PALM_H = 230.0; L_MED = PALM_H                      # dedo medio = altura de la palma
HAND = {
    "lateralidad": "izquierda", "vista": "dorso",
    # palma: pentágono irregular (trapecio muñeca→nudillos) + eminencia tenar (bulto del pulgar en el lateral derecho)
    "palma": [(-82, 0), (82, 0), (116, -48), (140, -108), (100, -PALM_H + 8), (-4, -PALM_H - 10), (-108, -PALM_H + 34), (-98, -110)],
    # 4 nudillos en ARCO: el más alto es el del medio
    "nudillos": {"menique": (-92, -PALM_H + 30), "anular": (-34, -PALM_H + 6), "medio": (26, -PALM_H - 8), "indice": (84, -PALM_H + 8)},
    # longitud total de cada dedo: medio 1.0 L · índice y anular .87 L (mitad de la última falange del medio) · meñique .60 L (altura de la distal del anular)
    "largo": {"medio": 1.0 * L_MED, "indice": .87 * L_MED, "anular": .87 * L_MED, "menique": .60 * L_MED},
    "falanges": (.46, .27, .27),                      # proporción proximal / media / distal
    # pulgar: nace bajo, cerca de la muñeca, a 35-45º hacia fuera; 2 falanges visibles desde la base tenar; la punta llega a mitad de la 1ª falange del índice
    "pulgar": {"base": (90, -36), "tenar": 80.0, "ang_base": 36.0, "falanges": (95.0, 80.0), "ang": (32.0, -24.0)},
}

def _pt(p, a, l): return (p[0] + l * math.sin(math.radians(a)), p[1] - l * math.cos(math.radians(a)))
def _cadena(p0, largos, angs):
    pts = [p0]
    for l, a in zip(largos, angs): pts.append(_pt(pts[-1], a, l))
    return pts

def _hand_points(pose):
    """Capa 1: puntos de articulación de cada dedo (esqueleto)."""
    H = HAND; kn = H["nudillos"]; out = {}
    for nombre, angs in pose.items():
        if nombre == "pulgar": continue
        tot = H["largo"][nombre]; out[nombre] = _cadena(kn[nombre], [tot * f for f in H["falanges"]], angs)
    th = H["pulgar"]; t0 = _pt(th["base"], th["ang_base"], th["tenar"])
    out["pulgar"] = _cadena(t0, th["falanges"], th["ang"]); out["pulgar_base"] = [th["base"], t0]
    return out

POSE_ESCRIBIR = {"indice": (6, 16, 28), "medio": (10, 26, 52), "anular": (8, 24, 50), "menique": (6, 22, 48), "pulgar": None}
CURL = .50                                          # los 3 dedos recogidos se ven acortados (escorzo)

def _suave(pts, n=3):
    """Chaikin: suaviza el contorno de la palma con curvas."""
    for _ in range(n):
        q = []
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            q += [(.75 * a[0] + .25 * b[0], .75 * a[1] + .25 * b[1]), (.25 * a[0] + .75 * b[0], .25 * a[1] + .75 * b[1])]
        pts = q
    return pts

@lru_cache(None)
def _pencil_hand2(g, debug=False):
    # lienzo grande: el antebrazo sale por el borde de la pantalla (sin corte visible). Punta del lápiz en TIP
    W, Hh = HAND_W, HAND_H; im = canvas(W, Hh); d = ImageDraw.Draw(im)
    pts = _hand_points(POSE_ESCRIBIR)
    # lápiz: pasa entre índice y pulgar; punta más allá de los dedos
    ind, pul = pts["indice"], pts["pulgar"]
    pinch = ((ind[1][0] + pul[-1][0]) / 2 + 2, (ind[1][1] + pul[-1][1]) / 2)
    ang_l = 12.0; dirf = (math.sin(math.radians(ang_l)), -math.cos(math.radians(ang_l)))
    tip_l = (pinch[0] + dirf[0] * 215, pinch[1] + dirf[1] * 215); back = (-dirf[0], -dirf[1])
    # transformación: el eje del lápiz (hacia atrás) debe coincidir con u=(-0.45,-0.893) y la punta con (600,900)
    ua = math.atan2(-0.893, -0.45); va = math.atan2(back[1], back[0]); th = ua - va
    c, s_ = math.cos(th), math.sin(th)
    def tf(p):
        x, y = p[0] - tip_l[0], p[1] - tip_l[1]; return (TIP[0] + x * c - y * s_, TIP[1] + x * s_ + y * c)
    def tube(P, R, fill=SKIN, ow=7):
        P = [tf(p) for p in P]
        for ow_, col in ((ow, OL), (0, fill)):
            for (a, b, ra, rb) in zip(P, P[1:], R, R[1:]):
                n = max(2, int(math.dist(a, b) / 3))
                for k in range(n + 1):
                    t = k / n; x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t; r = ra + (rb - ra) * t + ow_
                    ell(d, (x - r, y - r, x + r, y + r), col)
    def blob(P, fill=SKIN, out=OL, w=8):
        P = [tf(p) for p in P]; d.polygon([(x * SS, y * SS) for x, y in P], fill=fill)
        d.line([(x * SS, y * SS) for x, y in P + [P[0]]], fill=out, width=w * SS, joint="curve")
    # 3) lápiz
    ptip = tf(tip_l); pb = tf((tip_l[0] + back[0] * 700, tip_l[1] + back[1] * 700)); u = (-0.45, -0.893); n_ = (0.893, -0.45)
    at = lambda dist, off=0: (TIP[0] + u[0] * dist + n_[0] * off, TIP[1] + u[1] * dist + n_[1] * off)
    cap(d, at(78), at(700), 30, AMA, OL, 7); poly(d, [at(78, -30), TIP, at(78, 30)], (240, 200, 150), OL, 7); poly(d, [at(30, -11), TIP, at(30, 11)], OL, None)
    cap(d, at(690), at(760), 30, ROSA, OL, 7)
    # 1) antebrazo (cónico) + manga cerrada
    tube([(0, 20), (0, 2800)], [62, 100])
    # 2) dedos recogidos (escorzo): medio, anular, meñique por detrás del lápiz
    for n in ("menique", "anular", "medio"):
        pp = pts[n]; cur = [pp[0]] + [(pp[0][0] + (p[0] - pp[0][0]) * CURL, pp[0][1] + (p[1] - pp[0][1]) * CURL) for p in pp[1:]]
        tube(cur, [30, 28, 26, 25], SKIN if n == "medio" else SKINS)
    # 4) palma (pentágono irregular suavizado) con eminencia tenar
    blob(_suave(HAND["palma"]))
    # 5) índice por encima del lápiz y pulgar (2 falanges) por el otro lado
    tube(pts["pulgar_base"], [44, 38]); tube(pts["pulgar"], [38, 33, 29])
    tube(pts["indice"], [37, 33, 30, 27])
    for p in (pts["indice"][-1], pts["pulgar"][-1]):                                   # uñas
        q = tf(p); ell(d, (q[0] - 12, q[1] - 14, q[0] + 12, q[1] + 8), (255, 236, 226), OL, 4)
    # 6) nudillos: pequeños arcos de articulación
    for k in HAND["nudillos"].values():
        q = tf(k); arc(d, (q[0] - 20, q[1] - 14, q[0] + 20, q[1] + 18), 200, 340, SKINS, 5)
    if debug:
        for nm, P in pts.items():
            for p in P: q = tf(p); ell(d, (q[0] - 7, q[1] - 7, q[0] + 7, q[1] + 7), ROJO)
    return fin(im)

def pencil_hand(grip=220):
    return _pencil_hand2(int(round(grip / 8) * 8))
