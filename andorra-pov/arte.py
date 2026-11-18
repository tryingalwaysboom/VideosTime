"""Dibujos de "500 € en Andorra" (2D plano en perspectiva, mismo estilo que La casa de 1 dólar).
Las planchas se dibujan a 2x y se reducen a PW x PH; se encuadran con ep1.cam()."""
import math, os, random, sys
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "casa-pov"))
import art as A
from art import W, H, PW, PH, font, F_ANTON, F_UI, F_REG, lerp, mix, soft

K = 2   # supermuestreo de las planchas

class Cam3:
    """Proyección simple: X derecha, Y abajo (ojo en Y=0), Z profundidad."""
    def __init__(self, im, vpx, vpy, foc):
        self.im = im; self.d = ImageDraw.Draw(im); self.vpx, self.vpy, self.foc = vpx, vpy, foc
    def p(self, X, Y, Z): return ((self.vpx + X * self.foc / Z) * K, (self.vpy + Y * self.foc / Z) * K)
    def poly(self, pts, fill, outline=None, w=2):
        self.d.polygon([self.p(*q) for q in pts], fill=fill, outline=outline, width=w * K if outline else 0)
    def line(self, a, b, fill, w=2): self.d.line([self.p(*a), self.p(*b)], fill=fill, width=max(1, int(w * K)))
    def wall_x(self, X, z0, z1, y0, y1, fill, outline=None): self.poly([(X, y0, z0), (X, y0, z1), (X, y1, z1), (X, y1, z0)], fill, outline)
    def front(self, x0, x1, y0, y1, Z, fill, outline=None): self.poly([(x0, y0, Z), (x1, y0, Z), (x1, y1, Z), (x0, y1, Z)], fill, outline)

def glow(im, pts, col, *rest):
    """Halo suave: pts [(x, y, radio)], desenfoque = último argumento. Se dibuja solo en la zona afectada."""
    blur = rest[-1]
    for x, y, rr in pts:
        m = int(rr + blur * 3); x0, y0 = int(x - m), int(y - m)
        lay = Image.new("RGBA", (2 * m, 2 * m), (0, 0, 0, 0)); ImageDraw.Draw(lay).ellipse((x - rr - x0, y - rr - y0, x + rr - x0, y + rr - y0), fill=col)
        lay = lay.filter(ImageFilter.GaussianBlur(blur))
        big = Image.new("RGBA", im.size, (0, 0, 0, 0)); big.paste(lay, (x0, y0)); im.alpha_composite(big)

def down(im): return A.add_grain(im.resize((PW, PH), Image.LANCZOS), 4, 3)

def montanas(im, horizon, noche=True, seed=1):
    """Cordillera pirenaica con nieve y luces de pistas, dibujada sobre la línea del horizonte (coordenadas 2x)."""
    w = im.width; d = ImageDraw.Draw(im); rng = random.Random(seed)
    for capa, (col, nieve, base, amp) in enumerate([((44, 54, 86) if noche else (150, 170, 200), (150, 166, 200) if noche else (250, 252, 255), horizon - 900, 520),
                                                    ((30, 38, 64) if noche else (110, 132, 168), (120, 136, 172) if noche else (240, 244, 252), horizon - 560, 460)]):
        pts = [(0, horizon)]; x = 0; peaks = []
        while x <= w + 200:
            y = base + rng.uniform(-amp * .5, amp * .5); pts.append((x, y)); peaks.append((x, y)); x += rng.uniform(260, 520)
        pts.append((w, horizon)); d.polygon(pts, fill=col)
        for (x0, y0), (x1, y1) in zip(peaks[:-1], peaks[1:]):   # casquete de nieve en cada pico
            top = (x0, y0) if y0 < y1 else (x1, y1)
            if top[1] > horizon - 300: continue
            sw = 170 + rng.uniform(0, 90)
            d.polygon([(top[0], top[1]), (top[0] + sw, top[1] + sw * .75), (top[0] + sw * .55, top[1] + sw * .62), (top[0] + sw * .2, top[1] + sw * .82),
                       (top[0] - sw * .25, top[1] + sw * .6), (top[0] - sw * .7, top[1] + sw * .7)], fill=nieve)
    if noche:   # pistas iluminadas y un telesilla
        for k in range(3):
            x0 = w * (.18 + k * .3); y0 = horizon - 700 + k * 60
            for j in range(14):
                u = j / 13; d.ellipse((x0 + u * 260 - 6, y0 + u * 420 - 6, x0 + u * 260 + 6, y0 + u * 420 + 6), fill=(255, 230, 170))
        d.line((w * .55, horizon - 950, w * .78, horizon - 420), fill=(20, 24, 40), width=4)
    return im

# ====================================================================================================== calle
VPX, VPY, FOC = PW / 2, 1120, 760
TIENDAS = ["JOYERÍA", "RELOJES", "PERFUMES", "BOUTIQUE", "ELECTRÓNICA", "TABAC", "JOIES", "MODA"]

def edificio(c, side, z0, z1, h, base, seed):
    """Fachada de piedra/revoque con balcones de madera, tejado de pizarra nevado y tienda iluminada abajo."""
    rng = random.Random(seed); X = side * 7.0; G = 1.6
    piedra = rng.random() < .5
    c.wall_x(X, z0, z1, G - h, G, base)
    if piedra:   # sillares de granito
        for row in range(int(h / .55)):
            y = G - row * .55
            for k in range(int((z1 - z0) / .9) + 1):
                za = z0 + k * .9 + (row % 2) * .45
                if za + .85 > z1: continue
                tono = tuple(int(v * rng.uniform(.88, 1.08)) for v in base)
                c.wall_x(X, za + .04, za + .86, y - .51, y - .04, tono)
    # tejado con alero y nieve
    c.wall_x(X, z0 - .1, z1 + .1, G - h - .5, G - h, (52, 52, 62))
    c.poly([(X, G - h - .5, z0 - .1), (X - side * .9, G - h - .45, z0 - .1), (X - side * .9, G - h - .45, z1 + .1), (X, G - h - .5, z1 + .1)], (238, 242, 250))
    c.poly([(X, G - h - .62, z0 - .1), (X, G - h - .5, z0 - .1), (X, G - h - .5, z1 + .1), (X, G - h - .62, z1 + .1)], (250, 252, 255))
    # ventanas por planta (algunas iluminadas) + balcón de madera
    floors = int((h - 4.2) / 3.0)
    for f in range(floors):
        yb = G - 4.4 - f * 3.0
        nw = max(1, int((z1 - z0) / 2.6))
        for k in range(nw):
            zc = z0 + (k + .5) * (z1 - z0) / nw
            lit = rng.random() < .55
            c.wall_x(X, zc - .55, zc + .55, yb - 1.6, yb, (34, 30, 30))
            c.wall_x(X, zc - .45, zc + .45, yb - 1.5, yb - .1, (255, 206, 120) if lit else (40, 52, 76))
            c.line((X, yb - .8, zc - .45), (X, yb - .8, zc + .45), (34, 30, 30), 2); c.line((X, yb - 1.5, zc), (X, yb - .1, zc), (34, 30, 30), 2)
            if lit:
                p = c.p(X, yb - .8, zc); glow(c.im, [(p[0], p[1], 70 * K * 6 / zc)], (255, 190, 100, 70), 18 * K); c.d = ImageDraw.Draw(c.im)
        if f % 2 == 0:   # balcón corrido de madera
            wood = (110, 70, 42)
            c.poly([(X, yb, z0 + .3), (X - side * .8, yb, z0 + .3), (X - side * .8, yb, z1 - .3), (X, yb, z1 - .3)], (90, 58, 36))
            c.poly([(X - side * .8, yb - 1.0, z0 + .3), (X - side * .8, yb - 1.0, z1 - .3), (X - side * .8, yb, z1 - .3), (X - side * .8, yb, z0 + .3)], wood + (235,))
            for k in range(int((z1 - z0 - .6) / .22)):
                z = z0 + .3 + k * .22; c.line((X - side * .8, yb - 1.0, z), (X - side * .8, yb, z), (70, 44, 26), 1)
            c.poly([(X - side * .8, yb - 1.08, z0 + .3), (X - side * .8, yb - 1.0, z0 + .3), (X - side * .8, yb - 1.0, z1 - .3), (X - side * .8, yb - 1.08, z1 - .3)], (246, 248, 252))
    # tienda a pie de calle
    name = TIENDAS[seed % len(TIENDAS)]
    c.wall_x(X, z0 + .4, z1 - .4, G - 3.4, G - .05, (24, 22, 26))
    c.wall_x(X, z0 + .55, z1 - .55, G - 3.0, G - .25, (255, 226, 170))
    for k in range(4):   # artículos en el escaparate
        z = lerp(z0 + .9, z1 - .9, k / 3); c.wall_x(X, z - .25, z + .25, G - 1.3, G - .7, (60, 40, 30) if k % 2 else (200, 160, 70))
    c.wall_x(X, z0 + .4, z1 - .4, G - 4.1, G - 3.4, (16, 16, 22))
    pa, pb = c.p(X, G - 3.75, z0 + .5), c.p(X, G - 3.75, z1 - .5)
    lay = Image.new("RGBA", c.im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    sz = max(10, int(abs(pa[1] - c.p(X, G - 3.4, z0 + .5)[1]) * 1.1))
    ld.text(((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2), name, font=font(F_ANTON, sz), fill=(255, 220, 150), anchor="mm")
    ang = math.degrees(math.atan2(pb[1] - pa[1], pb[0] - pa[0])); ang = ang if abs(ang) < 90 else ang - 180
    cx, cy = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
    lay = lay.rotate(-ang, center=(cx, cy), resample=Image.BICUBIC)
    sx = abs(pb[0] - pa[0]) / max(1, ld.textlength(name, font=font(F_ANTON, sz))) * .9
    c.im.alpha_composite(lay)
    p = c.p(X - side * 1.5, G - .8, (z0 + z1) / 2); glow(c.im, [(p[0], p[1], 240 * K * 6 / ((z0 + z1) / 2))], (255, 210, 140, 60), 40 * K)
    c.d = ImageDraw.Draw(c.im)

def farola(c, X, Z):
    G = 1.6; c.line((X, G, Z), (X, G - 4.6, Z), (30, 30, 36), 5); c.line((X, G - 4.6, Z), (X * .86, G - 4.9, Z), (30, 30, 36), 4)
    p = c.p(X * .86, G - 4.8, Z); r = 9 * K * 8 / Z
    glow(c.im, [(p[0], p[1], r * 6)], (255, 214, 150, 120), 30 * K); c.d = ImageDraw.Draw(c.im)
    c.d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=(255, 244, 210))

@lru_cache(None)
def calle():
    im = A.grad(PW * K, PH * K, (8, 12, 34), (40, 46, 84), 0, VPY * K).convert("RGBA")
    d = ImageDraw.Draw(im); rng = random.Random(7)
    for _ in range(140):   # estrellas
        x, y = rng.uniform(0, PW * K), rng.uniform(0, VPY * K * .6); d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(230, 236, 255, rng.randint(80, 220)))
    montanas(im, VPY * K + 10, True)
    c = Cam3(im, VPX, VPY, FOC); G = 1.6
    c.poly([(-60, G, 120), (60, G, 120), (60, G, .9), (-60, G, .9)], (190, 200, 220))   # nieve del fondo del valle
    c.poly([(-4, G, 120), (4, G, 120), (4, G, .9), (-4, G, .9)], (46, 48, 60))          # asfalto mojado
    for X in (-1.0, 1.0, -2.6, 2.6):   # roderas en la nieve fina
        c.poly([(X - .25, G - .001, 120), (X + .25, G - .001, 120), (X + .25, G - .001, .9), (X - .25, G - .001, .9)], (36, 38, 48))
    for z in range(2, 120, 6): c.poly([(-.08, G - .002, z), (.08, G - .002, z), (.08, G - .002, z + 2.5), (-.08, G - .002, z + 2.5)], (210, 210, 200))
    for s in (-1, 1):   # aceras nevadas y bordillo
        c.poly([(s * 4, G, 120), (s * 7, G, 120), (s * 7, G, .9), (s * 4, G, .9)], (214, 222, 238))
        c.poly([(s * 4, G - .15, 120), (s * 4, G, 120), (s * 4, G, .9), (s * 4, G - .15, .9)], (170, 176, 196))
    # edificios de lejos a cerca
    zs = [(60, 70), (50, 60), (40, 50), (30, 40), (21, 30), (13, 21), (6, 13), (1, 6)]
    for i, (z0, z1) in enumerate(zs):
        for s in (-1, 1):
            base = [(176, 160, 140), (150, 136, 120), (196, 176, 150), (136, 128, 120)][(i + (s > 0)) % 4]
            edificio(c, s, z0, z1, rng.choice([13.5, 16.5, 19.5]), base, i * 2 + (s > 0))
    for z in (48, 34, 22, 12, 5):
        farola(c, -4.4, z); farola(c, 4.4, z + 4)
    # reflejos en el asfalto mojado
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for z in (48, 34, 22, 12, 5):
        for X in (-3.6, 3.6):
            a, b = c.p(X * .9, G, z), c.p(X * .9, G, max(1, z - 4)); ld.line((a, b), fill=(255, 210, 140, 90), width=int(14 * K * 8 / z))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10 * K)))
    # cartel de la parada
    c.d = ImageDraw.Draw(im); c.line((-4.6, G, 3.2), (-4.6, G - 3.0, 3.2), (40, 40, 48), 6)
    a, b = c.p(-5.6, G - 3.6, 3.2), c.p(-3.4, G - 2.9, 3.2)
    c.d.rounded_rectangle((a[0], a[1], b[0], b[1]), 12 * K, fill=(26, 70, 150), outline=(240, 240, 250), width=4 * K)
    c.d.text(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), "ANDORRA LA VELLA", font=font(F_ANTON, 34 * K), fill=(255, 255, 255), anchor="mm")
    return down(im)

def coche_deportivo(lado=1.0, col=(240, 200, 40)):
    """Deportivo visto por detrás (se aleja por la calle): cuña baja, alerón y franja de pilotos."""
    w, h = 900, 420; im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    dk = tuple(int(v * .62) for v in col)
    d.ellipse((60, 340, 840, 420), fill=(0, 0, 0, 120))
    d.rounded_rectangle((70, 300, 200, 390), 26, fill=(18, 18, 20)); d.rounded_rectangle((700, 300, 830, 390), 26, fill=(18, 18, 20))   # ruedas
    d.polygon([(40, 330), (860, 330), (840, 190), (700, 150), (200, 150), (60, 190)], fill=col)   # carrocería
    d.polygon([(230, 150), (670, 150), (600, 70), (300, 70)], fill=dk)                            # techo
    d.polygon([(255, 145), (645, 145), (585, 85), (315, 85)], fill=(30, 40, 60))                  # luna trasera
    d.rectangle((90, 210, 810, 238), fill=(255, 40, 40)); d.rectangle((110, 214, 790, 222), fill=(255, 170, 160))   # franja de pilotos
    d.rounded_rectangle((300, 262, 600, 312), 10, fill=(20, 20, 24))                               # difusor
    for x in (360, 420, 480, 540): d.ellipse((x - 18, 280, x + 18, 304), fill=(70, 70, 76))     # escapes
    d.rounded_rectangle((370, 244, 530, 268), 4, fill=(240, 240, 240)); d.text((450, 256), "AND 777", font=font(F_ANTON, 20), fill=(20, 20, 20), anchor="mm")
    d.rectangle((150, 120, 750, 140), fill=dk); d.rectangle((200, 140, 220, 165), fill=dk); d.rectangle((680, 140, 700, 165), fill=dk)   # alerón
    glow(im, [(200, 224, 90), (700, 224, 90)], (255, 40, 40, 110), 30)
    return im

# ====================================================================================================== piso compartido
@lru_cache(None)
def piso():
    S = (PW * K, PH * K); im = Image.new("RGBA", S, (0, 0, 0, 255)); c = Cam3(im, VPX, 1060, 640); G = 1.35; T = -1.55
    XL, XR, ZB = -2.4, 2.4, 6.5
    c.poly([(XL, T, .4), (XR, T, .4), (XR, T, ZB), (XL, T, ZB)], (150, 140, 128))
    c.poly([(XL, T, .4), (XL, T, ZB), (XL, G, ZB), (XL, G, .4)], (176, 158, 130)); c.poly([(XR, T, ZB), (XR, T, .4), (XR, G, .4), (XR, G, ZB)], (166, 150, 124))
    c.poly([(XL, T, ZB), (XR, T, ZB), (XR, G, ZB), (XL, G, ZB)], (186, 168, 140))
    c.poly([(XL, G, ZB), (XR, G, ZB), (XR, G, .4), (XL, G, .4)], (112, 84, 62))
    for k in range(1, 12): x = XL + (XR - XL) * k / 12; c.line((x, G, ZB), (x, G, .4), (92, 68, 50), 2)
    # ventana con montañas nevadas de noche
    wx0, wx1, wy0, wy1 = -1.0, .9, -1.05, .1
    a, b = c.p(wx0, wy0, ZB), c.p(wx1, wy1, ZB)
    sky = A.grad(int(b[0] - a[0]), int(b[1] - a[1]), (10, 14, 40), (50, 60, 100)).convert("RGBA"); montanas(sky, sky.height - 10, True, 4)
    sd = ImageDraw.Draw(sky); rng = random.Random(3)
    for _ in range(40): x, y = rng.uniform(0, sky.width), rng.uniform(sky.height * .75, sky.height); sd.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(255, 210, 140))
    im.alpha_composite(sky, (int(a[0]), int(a[1]))); c.d = ImageDraw.Draw(im)
    c.poly([(wx0, wy0, ZB), (wx1, wy0, ZB), (wx1, wy1, ZB), (wx0, wy1, ZB)], None, (236, 230, 220), 10)
    c.line(((wx0 + wx1) / 2, wy0, ZB), ((wx0 + wx1) / 2, wy1, ZB), (236, 230, 220), 7)
    c.poly([(wx0 - .1, wy1, ZB - .02), (wx1 + .1, wy1, ZB - .02), (wx1 + .1, wy1 + .08, ZB - .25), (wx0 - .1, wy1 + .08, ZB - .25)], (226, 220, 210))
    # cajas de mudanza, lámpara desnuda y póster
    for x0, z0, s_ in ((1.2, 4.6, 1.0), (1.5, 4.0, .8)):
        c.poly([(x0, G - .7 * s_, z0), (x0 + .8 * s_, G - .7 * s_, z0), (x0 + .8 * s_, G, z0), (x0, G, z0)], (196, 150, 96))
        c.poly([(x0, G - .7 * s_, z0), (x0 + .8 * s_, G - .7 * s_, z0), (x0 + .8 * s_, G - .7 * s_, z0 + .6), (x0, G - .7 * s_, z0 + .6)], (214, 170, 116))
        c.line((x0 + .4 * s_, G - .7 * s_, z0), (x0 + .4 * s_, G - .35 * s_, z0), (150, 110, 66), 6)
    c.line((0, T, 4.0), (0, -.95, 4.0), (40, 36, 30), 2); p = c.p(0, -.9, 4.0)
    glow(im, [(p[0], p[1], 240 * K)], (255, 220, 160, 80), 60 * K); c.d = ImageDraw.Draw(im); c.d.ellipse((p[0] - 14 * K, p[1] - 18 * K, p[0] + 14 * K, p[1] + 12 * K), fill=(255, 240, 200))
    # sofá viejo con manta y almohada
    sc = (96, 110, 90); x0, x1, z0, z1 = -2.3, -.2, 4.6, 5.6
    c.poly([(x0, .1, z1), (x1, .1, z1), (x1, G, z1), (x0, G, z1)], tuple(int(v * .78) for v in sc))
    c.poly([(x0 + .2, .7, z0), (x1 - .2, .7, z0), (x1 - .2, .7, z1), (x0 + .2, .7, z1)], tuple(int(v * 1.1) for v in sc))
    c.poly([(x0 + .2, .7, z0), (x1 - .2, .7, z0), (x1 - .2, G, z0), (x0 + .2, G, z0)], sc)
    for xx in (x0, x1 - .25):
        c.poly([(xx, .35, z0), (xx + .25, .35, z0), (xx + .25, G, z0), (xx, G, z0)], tuple(int(v * .86) for v in sc))
        c.poly([(xx, .35, z0), (xx + .25, .35, z0), (xx + .25, .35, z1), (xx, .35, z1)], tuple(int(v * .95) for v in sc))
    c.poly([(x0 + .5, .62, z0 - .05), (x1 - .3, .62, z0 - .05), (x1 - .25, .95, z0 - .08), (x0 + .4, 1.05, z0 - .08)], (170, 60, 60))   # manta
    for k in range(5): xx = x0 + .6 + k * .25; c.line((xx, .62, z0 - .06), (xx + .03, 1.0, z0 - .07), (140, 44, 44), 3)
    c.poly([(x0 + .25, .35, z0 + .3), (x0 + .75, .3, z0 + .3), (x0 + .8, .68, z0 + .2), (x0 + .25, .7, z0 + .2)], (230, 230, 236))   # almohada
    # maleta abierta
    c.poly([(.2, 1.0, 3.2), (1.0, 1.0, 3.2), (1.0, G, 3.2), (.2, G, 3.2)], (40, 60, 110)); c.poly([(.2, 1.0, 3.2), (1.0, 1.0, 3.2), (1.0, 1.0, 3.8), (.2, 1.0, 3.8)], (220, 214, 200))
    im.alpha_composite(Image.new("RGBA", S, (30, 20, 40, 40)))
    return down(im)

# ====================================================================================================== pista de esquí (día)
@lru_cache(None)
def nieve_dia():
    S = (PW * K, PH * K); im = A.grad(S[0], S[1], (70, 140, 230), (190, 220, 250), 0, 1100 * K).convert("RGBA")
    glow(im, [(PW * K * .78, 380 * K, 120 * K)], (255, 250, 220, 255), 40 * K); glow(im, [(PW * K * .78, 380 * K, 260 * K)], (255, 250, 220, 90), 90 * K)
    montanas(im, 1150 * K, False, 9)
    d = ImageDraw.Draw(im); rng = random.Random(5)
    d.polygon([(0, 1100 * K), (PW * K, 980 * K), (PW * K, PH * K), (0, PH * K)], fill=(246, 248, 255))
    for _ in range(26):   # abetos nevados
        x, y = rng.uniform(0, PW * K), rng.uniform(1060 * K, 1300 * K); s = (y / K - 900) / 300 * 70 * K
        d.polygon([(x, y - s * 2.2), (x - s * .8, y), (x + s * .8, y)], fill=(30, 70, 50)); d.polygon([(x, y - s * 2.2), (x - s * .4, y - s * 1.2), (x + s * .4, y - s * 1.2)], fill=(240, 246, 255))
    for k in range(6):   # telesilla
        x = lerp(120, 1180, k / 5) * K; y = lerp(1040, 700, k / 5) * K
        d.line((x, y, x, y + (90 - k * 10) * K), fill=(70, 70, 80), width=5 * K)
    d.line((120 * K, 1040 * K, 1180 * K, 700 * K), fill=(60, 60, 70), width=3 * K)
    for _ in range(40):   # huellas y surcos en la nieve
        x, y = rng.uniform(0, PW * K), rng.uniform(1300 * K, PH * K); d.arc((x - 80 * K, y - 20 * K, x + 80 * K, y + 20 * K), 200, 340, fill=(214, 222, 240), width=4 * K)
    return down(im)

# ====================================================================================================== mirador nocturno (pregunta)
@lru_cache(None)
def mirador():
    S = (PW * K, PH * K); im = A.grad(S[0], S[1], (6, 10, 30), (36, 44, 90), 0, 1200 * K).convert("RGBA")
    d = ImageDraw.Draw(im); rng = random.Random(11)
    for _ in range(220): x, y = rng.uniform(0, S[0]), rng.uniform(0, 900 * K); d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(230, 236, 255, rng.randint(80, 230)))
    glow(im, [(PW * K * .2, 300 * K, 70 * K)], (240, 244, 255, 255), 10 * K)
    montanas(im, 1250 * K, True, 21)
    d = ImageDraw.Draw(im)
    d.polygon([(0, 1250 * K), (S[0], 1200 * K), (S[0], 1700 * K), (0, 1750 * K)], fill=(26, 30, 52))   # fondo del valle
    for _ in range(700):   # luces del pueblo en el valle
        x = rng.uniform(0, S[0]); y = rng.uniform(1280 * K, 1640 * K) + (x / S[0]) * -40 * K
        col = rng.choice([(255, 210, 140), (255, 236, 200), (255, 180, 100)]); r = rng.uniform(2, 5) * K
        d.ellipse((x - r, y - r, x + r, y + r), fill=col)
    glow(im, [(S[0] * .5, 1450 * K, 500 * K)], (255, 190, 110, 40), 120 * K)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 1720 * K, S[0], S[1]), fill=(80, 56, 40))   # barandilla de madera del mirador
    d.rectangle((0, 1700 * K, S[0], 1740 * K), fill=(110, 76, 50)); d.rectangle((0, 1690 * K, S[0], 1704 * K), fill=(246, 248, 255))
    for x in range(0, S[0], 150 * K): d.rectangle((x, 1740 * K, x + 30 * K, S[1]), fill=(96, 66, 44))
    return down(im)

# ====================================================================================================== bar de Escaldes
BAR_VP = (PW / 2 - 60, 980, 700)
@lru_cache(None)
def bar():
    S = (PW * K, PH * K); im = Image.new("RGBA", S, (20, 14, 12, 255)); c = Cam3(im, *BAR_VP); G = 1.5; T = -2.0
    XL, XR, ZB = -3.2, 3.6, 9.0
    c.poly([(XL, T, .4), (XR, T, .4), (XR, T, ZB), (XL, T, ZB)], (40, 28, 22))
    for z in (1.5, 3.0, 4.6, 6.2, 7.8): c.poly([(XL, T, z), (XR, T, z), (XR, T, z + .25), (XL, T, z + .25)], (70, 46, 30))
    c.poly([(XL, T, .4), (XL, T, ZB), (XL, G, ZB), (XL, G, .4)], (74, 50, 36)); c.poly([(XR, T, ZB), (XR, T, .4), (XR, G, .4), (XR, G, ZB)], (60, 40, 30))
    for z in np.arange(.6, ZB, .5): c.line((XL, T, z), (XL, G, z), (60, 40, 28), 2)   # friso de madera
    c.poly([(XL, T, ZB), (XR, T, ZB), (XR, G, ZB), (XL, G, ZB)], (54, 36, 28))
    c.poly([(XL, G, ZB), (XR, G, ZB), (XR, G, .4), (XL, G, .4)], (40, 30, 26))
    for k in range(1, 10): x = XL + (XR - XL) * k / 10; c.line((x, G, ZB), (x, G, .4), (30, 22, 20), 2)
    # estanterías de botellas en la pared del fondo (retroiluminadas)
    a, b = c.p(-2.6, -1.7, ZB - .01), c.p(2.8, .2, ZB - .01)
    glow(im, [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (b[0] - a[0]) * .55)], (255, 170, 80, 90), 50 * K); c.d = ImageDraw.Draw(im)
    rng = random.Random(4)
    for row, y in enumerate((-1.25, -.65, -.05)):
        c.poly([(-2.6, y, ZB - .02), (2.8, y, ZB - .02), (2.8, y + .06, ZB - .02), (-2.6, y + .06, ZB - .02)], (120, 80, 50))
        x = -2.5
        while x < 2.6:
            bw = rng.uniform(.13, .2); bh = rng.uniform(.32, .5); col = rng.choice([(60, 120, 60), (140, 80, 30), (200, 170, 90), (90, 40, 30), (220, 220, 230), (40, 70, 110)])
            c.poly([(x, y - bh, ZB - .03), (x + bw, y - bh, ZB - .03), (x + bw, y, ZB - .03), (x, y, ZB - .03)], col)
            c.poly([(x + bw * .35, y - bh - .12, ZB - .03), (x + bw * .65, y - bh - .12, ZB - .03), (x + bw * .65, y - bh, ZB - .03), (x + bw * .35, y - bh, ZB - .03)], col)
            c.poly([(x + bw * .15, y - bh * .6, ZB - .035), (x + bw * .85, y - bh * .6, ZB - .035), (x + bw * .85, y - bh * .3, ZB - .035), (x + bw * .15, y - bh * .3, ZB - .035)], (236, 226, 200))
            x += bw + .05
    # letrero de neón
    p = c.p(.1, -1.75, ZB - .05); glow(im, [(p[0], p[1], 170 * K)], (255, 60, 140, 90), 40 * K); c.d = ImageDraw.Draw(im)
    c.d.text(p, "ESCALDES", font=font(F_ANTON, 52 * K), fill=(255, 150, 210), anchor="mm", stroke_width=2 * K, stroke_fill=(255, 60, 140))
    # lámparas colgantes
    for x, z in ((-1.6, 3.4), (.4, 3.4), (2.2, 3.4), (-1.4, 6.0), (1.6, 6.0)):
        c.line((x, T, z), (x, -1.1, z), (20, 16, 14), 2); p = c.p(x, -1.05, z)
        glow(im, [(p[0], p[1] + 30 * K, 200 * K * 3.4 / z)], (255, 190, 110, 70), 40 * K); c.d = ImageDraw.Draw(im)
        r = 34 * K * 3.4 / z; c.d.pieslice((p[0] - r, p[1] - r * .7, p[0] + r, p[1] + r * .9), 180, 360, fill=(30, 30, 34)); c.d.ellipse((p[0] - r * .4, p[1] - r * .1, p[0] + r * .4, p[1] + r * .25), fill=(255, 236, 190))
    # barra de madera que viene hacia nosotros (a la izquierda) con taburetes
    bx0, bx1, by = -3.0, -1.5, .25
    c.poly([(bx0, by, ZB - .6), (bx1, by, ZB - .6), (bx1, by, .4), (bx0, by, .4)], (110, 66, 38))
    c.poly([(bx1, by, ZB - .6), (bx1, by, .4), (bx1, G, .4), (bx1, G, ZB - .6)], (70, 42, 26))
    for z in np.arange(1.0, ZB - .6, .7): c.line((bx1, by + .1, z), (bx1, G, z), (56, 34, 20), 2)
    c.poly([(bx1, by, ZB - .6), (bx1 + .06, by, ZB - .6), (bx1 + .06, by, .4), (bx1, by, .4)], (180, 120, 60))
    for z in (2.2, 3.6, 5.0, 6.4):
        c.line((bx1 + .45, G, z), (bx1 + .45, .75, z), (150, 150, 160), 4); c.poly([(bx1 + .2, .72, z - .22), (bx1 + .7, .72, z - .22), (bx1 + .7, .72, z + .22), (bx1 + .2, .72, z + .22)], (150, 40, 40))
    # mesas y gente desenfocada al fondo derecha
    for x, z in ((1.6, 7.0), (2.6, 5.4)):
        c.poly([(x - .5, .6, z), (x + .5, .6, z), (x + .5, .66, z), (x - .5, .66, z)], (90, 60, 40)); c.line((x, .66, z), (x, G, z), (60, 40, 30), 4)
        for dx in (-.55, .55):
            hx, hy = c.p(x + dx, -.1, z); r = 60 * K / z * 3
            c.d.ellipse((hx - r * .5, hy - r * .6, hx + r * .5, hy + r * .5), fill=(70, 50, 44)); c.d.rounded_rectangle((hx - r * .8, hy + r * .5, hx + r * .8, hy + r * 2.6), int(r * .4), fill=(50, 40, 50))
    im.alpha_composite(Image.new("RGBA", S, (40, 16, 0, 30)))
    return down(im)

# ====================================================================================================== el millonario (personaje)
PIEL = (232, 178, 128); PIEL_D = (204, 146, 98)
def millonario(boca=0.0, mira=0.0, dedo=False):
    """Hombre de unos 35: pelo engominado, barba corta, jersey negro de cuello alto y abrigo camel, reloj de oro.
    boca 0..1 abre la boca (solo cuando habla él). Lienzo 900x1300, de cintura para arriba, girado 3/4 hacia el POV."""
    w, h = 900, 1300; im = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im); s = 2
    def P(*pts): return [(x * s, y * s) for x, y in pts]
    def E(x0, y0, x1, y1): return (x0 * s, y0 * s, x1 * s, y1 * s)
    camel = (176, 126, 74); camel_d = (140, 96, 54); negro = (28, 28, 34)
    d.polygon(P((120, 1300), (160, 760), (300, 640), (600, 640), (740, 760), (790, 1300)), fill=camel)        # abrigo
    d.polygon(P((300, 640), (450, 700), (600, 640), (560, 1300), (340, 1300)), fill=negro)                    # jersey
    d.polygon(P((300, 640), (390, 680), (350, 1000), (290, 760)), fill=camel_d); d.polygon(P((600, 640), (510, 680), (560, 1000), (620, 760)), fill=camel_d)   # solapas
    d.rounded_rectangle(E(380, 590, 520, 690), 40 * s, fill=negro)                                            # cuello alto
    d.rounded_rectangle(E(400, 520, 500, 640), 30 * s, fill=PIEL_D)                                            # cuello
    d.ellipse(E(320, 240, 580, 560), fill=PIEL)                                                               # cabeza
    d.ellipse(E(306, 380, 346, 450), fill=PIEL_D); d.ellipse(E(556, 380, 596, 450), fill=PIEL_D)             # orejas
    d.pieslice(E(316, 300, 584, 600), 0, 180, fill=(52, 36, 28))                                               # barba
    d.ellipse(E(350, 360, 550, 560), fill=PIEL)                                                               # cara (sobre la barba)
    d.polygon(P((360, 470), (540, 470), (530, 545), (450, 572), (370, 545)), fill=(64, 44, 34))                # barba en mandíbula
    d.chord(E(312, 210, 588, 420), 180, 360, fill=(38, 28, 24)); d.polygon(P((312, 315), (588, 315), (575, 280), (450, 236), (330, 270)), fill=(38, 28, 24))   # pelo engominado
    d.arc(E(360, 236, 560, 330), 200, 330, fill=(80, 64, 54), width=6 * s)                                     # brillo del pelo
    ex = 8 * mira
    for x in (405, 495):                                                                                       # ojos y cejas
        d.ellipse(E(x - 22, 392, x + 22, 420), fill=(250, 248, 244)); d.ellipse(E(x - 10 + ex, 395, x + 10 + ex, 417), fill=(40, 30, 26))
        d.line(P((x - 26, 376), (x + 24, 370 if x < 450 else 380)), fill=(38, 28, 24), width=9 * s)
    d.polygon(P((450, 420), (432, 470), (462, 474)), fill=PIEL_D)                                              # nariz
    d.line(P((410, 490), (490, 488)), fill=(52, 36, 28), width=10 * s)                                         # bigote
    if boca > .05: d.ellipse(E(425, 500 - 2, 475, 506 + 26 * boca), fill=(90, 30, 30)); d.rectangle(E(430, 500, 470, 506), fill=(250, 246, 240))
    else: d.line(P((428, 507), (452, 510), (474, 505)), fill=(110, 50, 44), width=6 * s)
    # brazo apoyado en la barra con el reloj de oro
    d.polygon(P((620, 820), (760, 900), (700, 1080), (470, 1060), (480, 980)), fill=camel)
    d.rounded_rectangle(E(400, 990, 500, 1080), 30 * s, fill=PIEL)                                              # mano
    d.rounded_rectangle(E(470, 975, 560, 1090), 22 * s, fill=(212, 170, 60)); d.ellipse(E(482, 992, 548, 1072), fill=(240, 210, 110))   # reloj
    d.ellipse(E(492, 1002, 538, 1062), fill=(30, 50, 60)); d.line(P((515, 1032), (515, 1012)), fill=(240, 220, 150), width=3 * s); d.line(P((515, 1032), (530, 1040)), fill=(240, 220, 150), width=3 * s)
    if dedo:   # dedo en los labios: "nadie puede saberlo"
        d.polygon(P((330, 1300), (360, 820), (450, 700), (500, 760), (430, 900), (420, 1300)), fill=camel)
        d.rounded_rectangle(E(420, 640, 490, 760), 28 * s, fill=PIEL); d.rounded_rectangle(E(440, 470, 470, 650), 14 * s, fill=PIEL); d.line(P((441, 600), (469, 600)), fill=PIEL_D, width=3 * s)
    return im.resize((w, h), Image.LANCZOS)

def sobre(abierto=True):
    """Sobre marrón grueso con billetes de 100 € asomando. 620x420."""
    im = Image.new("RGBA", (620, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if abierto:
        for k in range(5):
            d.rounded_rectangle((70 + k * 8, 20 + k * 6, 470 + k * 8, 230 + k * 6), 10, fill=(120, 180, 140), outline=(70, 120, 90), width=3)
            d.text((270 + k * 8, 125 + k * 6), "100 €", font=font(F_ANTON, 64), fill=(60, 110, 80), anchor="mm")
    d.rounded_rectangle((20, 140, 600, 410), 18, fill=(196, 150, 96)); d.polygon([(20, 140), (310, 270), (600, 140)], fill=(214, 170, 116))
    d.line((20, 140, 310, 270, 600, 140), fill=(160, 116, 70), width=4)
    return im

def movil(chat=None, pantalla=None):
    """Móvil en vertical (480x980) con la pantalla que se le pase (imagen) o un chat [(quien, texto)]."""
    im = Image.new("RGBA", (480, 980), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, 480, 980), 60, fill=(24, 24, 30)); d.rounded_rectangle((16, 16, 464, 964), 48, fill=(240, 236, 228))
    if pantalla is not None:
        m = Image.new("L", (448, 948), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 448, 948), 48, fill=255)
        im.paste(pantalla.convert("RGBA").resize((448, 948)), (16, 16), m)
    if chat is not None:
        d.rectangle((16, 60, 464, 170), fill=(28, 120, 100)); d.ellipse((40, 85, 100, 145), fill=(250, 210, 180)); d.text((120, 115), "Mamá ❤", font=font(F_UI, 34), fill=(255, 255, 255), anchor="lm")
        y = 210
        for quien, txt in chat:
            f = font(F_REG, 30); tw = min(360, d.textlength(txt, font=f)); hh = 70
            if quien == "ella": d.rounded_rectangle((36, y, 36 + tw + 40, y + hh), 22, fill=(255, 255, 255)); d.text((56, y + hh / 2), txt, font=f, fill=(20, 20, 20), anchor="lm")
            else: d.rounded_rectangle((444 - tw - 40, y, 444, y + hh), 22, fill=(214, 248, 196)); d.text((464 - tw - 40, y + hh / 2), txt, font=f, fill=(20, 20, 20), anchor="lm")
            y += hh + 24
    d.rounded_rectangle((180, 30, 300, 52), 11, fill=(24, 24, 30))
    return im
