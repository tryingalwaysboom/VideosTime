"""Papá solo 30 días — arte 2D plano con contorno (PIL, supersampling S=2). Fondos cacheables + personajes con boca/parpadeo."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math, os

S = 2
W, H = 1080 * S, 1920 * S
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "mateo-pov", "fonts")
F_BAL = os.path.join(FONTS, "Baloo2-ExtraBold.ttf")
F_POP = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
OL = (52, 36, 40)
_FC = {}


def font(size, path=F_BAL):
    k = (size, path)
    if k not in _FC: _FC[k] = ImageFont.truetype(path, int(size))
    return _FC[k]


def grad(w, h, top, bot):
    im = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        im.putpixel((0, y), tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    return im.resize((w, h))


def soft(im, fn, blur, op=255):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    fn(ImageDraw.Draw(lay))
    lay = lay.filter(ImageFilter.GaussianBlur(blur))
    im.alpha_composite(lay)


def sombra_pies(im, x, y, w):
    soft(im, lambda d: d.ellipse([x - w, y - w * .14, x + w, y + w * .14], fill=(40, 20, 10, 80)), int(w * .12))


def s(v): return v * S


# ======================= FONDOS =======================
def _suelo_madera(d, y0, col=(205, 150, 110), lin=(188, 134, 98)):
    d.rectangle([0, y0, W, H], fill=col)
    for k, x in enumerate(range(-W, W * 2, s(150))):
        d.line([x, y0, x + s(330), H], fill=lin, width=s(3))


def cocina(hora=(7, 5)):
    im = grad(W, H, (255, 238, 210), (250, 216, 180)).convert("RGBA")
    d = ImageDraw.Draw(im)
    for y in range(s(300), s(1100), s(90)):
        for x in range(0, W, s(90)):
            d.rounded_rectangle([x + s(3), y + s(3), x + s(87), y + s(87)], s(6), fill=(247, 228, 198))
    wx, wy, ww, wh = s(600), s(330), s(380), s(420)
    im.paste(grad(ww, wh, (255, 186, 136), (255, 236, 190)), (wx, wy))
    d.ellipse([wx + s(220), wy + s(230), wx + s(320), wy + s(330)], fill=(255, 246, 214))
    d.rectangle([wx, wy + s(300), wx + ww, wy + wh], fill=(160, 192, 226))
    for i, (bx, bh) in enumerate([(20, 70), (90, 110), (170, 60), (250, 95), (320, 80)]):
        d.rectangle([wx + s(bx), wy + wh - s(bh), wx + s(bx + 55), wy + wh], fill=(132, 160, 204))
    d.rectangle([wx - s(18), wy - s(18), wx + ww + s(18), wy + wh + s(18)], outline=(255, 255, 255), width=s(22))
    d.line([wx + ww // 2, wy, wx + ww // 2, wy + wh], fill=(255, 255, 255), width=s(14))
    d.line([wx, wy + wh // 2, wx + ww, wy + wh // 2], fill=(255, 255, 255), width=s(14))
    for cx in (wx - s(70), wx + ww + s(10)):
        d.rounded_rectangle([cx, wy - s(60), cx + s(60), wy + wh + s(40)], s(30), fill=(232, 110, 90))
    d.rounded_rectangle([s(60), s(420), s(480), s(445)], s(8), fill=(170, 110, 70))
    for i, (c, hh) in enumerate([((120, 180, 140), 90), ((240, 190, 80), 70), ((200, 120, 160), 100), ((110, 160, 210), 80)]):
        x = s(90) + i * s(95)
        d.rounded_rectangle([x, s(420 - hh), x + s(70), s(420)], s(14), fill=c, outline=OL, width=s(3))
        d.rounded_rectangle([x + s(8), s(420 - hh - 14), x + s(62), s(420 - hh + 4)], s(6), fill=(150, 100, 60), outline=OL, width=s(3))
    reloj(d, s(270), s(620), s(85), hora)
    d.rectangle([0, s(1100), W, s(1150)], fill=(240, 240, 235))
    d.rectangle([0, s(1150), W, s(1560)], fill=(120, 172, 160))
    for x in range(0, W, s(270)):
        d.rounded_rectangle([x + s(14), s(1170), x + s(256), s(1540)], s(16), outline=(100, 150, 140), width=s(6))
        d.rounded_rectangle([x + s(115), s(1200), x + s(155), s(1215)], s(6), fill=(230, 220, 200))
    # tostadora y frutero sobre la encimera
    d.rounded_rectangle([s(90), s(1020), s(250), s(1105)], s(26), fill=(220, 225, 232), outline=OL, width=s(4))
    for k in (0, 1): d.rounded_rectangle([s(120 + k * 60), s(1012), s(160 + k * 60), s(1030)], s(6), fill=(60, 60, 70))
    _suelo_madera(d, s(1560))
    return im


def reloj(d, cx, cy, r, hora):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255), outline=(60, 60, 80), width=s(10))
    for k in range(12):
        a = k / 12 * 2 * math.pi
        px, py = cx + r * .78 * math.sin(a), cy - r * .78 * math.cos(a)
        d.ellipse([px - s(5), py - s(5), px + s(5), py + s(5)], fill=(60, 60, 80))
    h, m = hora
    ah = math.radians((h % 12 + m / 60) * 30); am = math.radians(m * 6)
    d.line([cx, cy, cx + r * .48 * math.sin(ah), cy - r * .48 * math.cos(ah)], fill=(60, 60, 80), width=s(10))
    d.line([cx, cy, cx + r * .74 * math.sin(am), cy - r * .74 * math.cos(am)], fill=(226, 72, 60), width=s(6))
    d.ellipse([cx - s(8), cy - s(8), cx + s(8), cy + s(8)], fill=(60, 60, 80))


def recibidor(puerta=0.0, luz=False):
    """puerta: 0 cerrada .. 1 abierta. luz: claridad de la calle."""
    im = grad(W, H, (214, 232, 226), (190, 214, 206)).convert("RGBA")
    d = ImageDraw.Draw(im)
    for x in range(0, W, s(60)):
        d.line([x, 0, x, s(1500)], fill=(204, 224, 216), width=s(4))
    d.rectangle([0, s(1420), W, s(1500)], fill=(250, 250, 246))
    # marco y puerta
    fx0, fy0, fx1, fy1 = s(300), s(420), s(780), s(1500)
    d.rectangle([fx0 - s(30), fy0 - s(30), fx1 + s(30), fy1], fill=(250, 250, 246), outline=OL, width=s(5))
    if puerta > 0:
        exterior = grad(fx1 - fx0, fy1 - fy0, (255, 244, 214), (230, 214, 180))
        im.paste(exterior, (fx0, fy0))
        d.rectangle([fx0, fy0 + s(700), fx1, fy1], fill=(200, 190, 175))
    pw = int((fx1 - fx0) * (1 - .82 * puerta))
    d.rectangle([fx0, fy0, fx0 + pw, fy1], fill=(176, 108, 66), outline=OL, width=s(5))
    if pw > s(120):
        for (a, b) in ((.12, .42), (.52, .9)):
            d.rounded_rectangle([fx0 + pw * .15, fy0 + (fy1 - fy0) * a, fx0 + pw * .85, fy0 + (fy1 - fy0) * b], s(10), outline=(150, 88, 52), width=s(6))
        d.ellipse([fx0 + pw - s(70), s(950), fx0 + pw - s(40), s(980)], fill=(240, 200, 90), outline=OL, width=s(3))
    if luz and puerta > 0:
        soft(im, lambda q: q.polygon([(fx0 + pw, fy0), (fx1, fy0), (W, H), (fx0 + pw - s(100), H)], fill=(255, 236, 180, 90)), s(30))
    d = ImageDraw.Draw(im)
    # perchero y espejo
    d.rectangle([s(70), s(500), s(90), s(1420)], fill=(140, 90, 60))
    for k, c in enumerate([(232, 110, 90), (90, 130, 200)]):
        d.rounded_rectangle([s(30 + k * 40), s(560 + k * 30), s(110 + k * 40), s(820 + k * 30)], s(30), fill=c, outline=OL, width=s(4))
    d.ellipse([s(850), s(520), s(1030), s(780)], fill=(210, 236, 246), outline=(200, 160, 90), width=s(14))
    d.rounded_rectangle([s(840), s(1180), s(1060), s(1220)], s(8), fill=(176, 120, 80), outline=OL, width=s(4))
    d.rectangle([s(860), s(1220), s(880), s(1420)], fill=(150, 100, 66)); d.rectangle([s(1020), s(1220), s(1040), s(1420)], fill=(150, 100, 66))
    # felpudo y suelo
    d.rectangle([0, s(1500), W, H], fill=(220, 196, 160))
    for y in range(s(1500), H, s(90)):
        for x in range((y // s(90)) % 2 * s(90), W, s(180)):
            d.rectangle([x, y, x + s(90), y + s(90)], fill=(208, 182, 146))
    d.rounded_rectangle([s(330), s(1520), s(750), s(1600)], s(16), fill=(150, 80, 70))
    return im


def dormitorio():
    im = grad(W, H, (196, 204, 240), (172, 180, 224)).convert("RGBA")
    d = ImageDraw.Draw(im)
    for k in range(14):
        x, y = s(80 + (k * 173) % 900), s(200 + (k * 271) % 700)
        estrella(d, x, y, s(16), (255, 240, 170))
    d.rounded_rectangle([s(60), s(780), s(1020), s(1180)], s(40), fill=(120, 90, 160), outline=OL, width=s(5))
    d.rounded_rectangle([s(40), s(1100), s(1040), s(1330)], s(30), fill=(250, 250, 255), outline=OL, width=s(5))
    d.rounded_rectangle([s(30), s(1180), s(1050), s(1420)], s(30), fill=(110, 170, 230), outline=OL, width=s(5))
    for x in range(s(60), s(1040), s(110)):
        d.ellipse([x, s(1250), x + s(30), s(1280)], fill=(255, 255, 255))
    d.rectangle([0, s(1420), W, s(1700)], fill=(30, 26, 44))     # hueco oscuro bajo la cama
    d.rectangle([0, s(1700), W, H], fill=(186, 140, 110))
    for x in (s(60), s(980)): d.rectangle([x, s(1420), x + s(40), s(1700)], fill=(90, 70, 110))
    return im


def armario():
    im = grad(W, H, (246, 226, 206), (232, 206, 182)).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rectangle([s(120), s(300), s(960), s(1600)], fill=(80, 54, 40), outline=OL, width=s(6))
    d.line([s(160), s(420), s(920), s(420)], fill=(200, 200, 210), width=s(10))
    cols = [(232, 110, 90), (90, 130, 200), (250, 200, 80), (120, 190, 140), (200, 120, 180), (240, 240, 240)]
    for i, c in enumerate(cols):
        x = s(190 + i * 125)
        d.line([x + s(50), s(420), x + s(50), s(450)], fill=(200, 200, 210), width=s(6))
        d.polygon([(x, s(460)), (x + s(100), s(460)), (x + s(110), s(860)), (x - s(10), s(860))], fill=c, outline=OL)
    for x in (s(40), s(960)):
        d.rectangle([x, s(290), x + s(80), s(1610)], fill=(196, 140, 96), outline=OL, width=s(5))
    for i in range(4):
        d.rounded_rectangle([s(180 + i * 190), s(1300), s(340 + i * 190), s(1420)], s(14), fill=[(90, 90, 120), (230, 120, 90), (110, 160, 200), (240, 200, 90)][i], outline=OL, width=s(4))
    _suelo_madera(d, s(1600))
    return im


def salon():
    im = grad(W, H, (252, 228, 214), (240, 208, 190)).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rectangle([s(140), s(380), s(520), s(700)], fill=(255, 255, 255), outline=(200, 160, 90), width=s(12))
    d.polygon([(s(160), s(680)), (s(300), s(500)), (s(380), s(600)), (s(430), s(540)), (s(500), s(680))], fill=(120, 180, 150))
    d.ellipse([s(400), s(420), s(460), s(480)], fill=(255, 210, 90))
    d.rounded_rectangle([s(640), s(420), s(940), s(720)], s(20), fill=(70, 80, 100), outline=OL, width=s(5))
    # sofá
    d.rounded_rectangle([s(60), s(900), s(1020), s(1180)], s(60), fill=(80, 150, 170), outline=OL, width=s(6))
    d.rounded_rectangle([s(30), s(1100), s(1050), s(1400)], s(50), fill=(96, 170, 190), outline=OL, width=s(6))
    d.rectangle([s(90), s(1400), s(130), s(1480)], fill=(90, 60, 40)); d.rectangle([s(950), s(1400), s(990), s(1480)], fill=(90, 60, 40))
    _suelo_madera(d, s(1480), (196, 152, 120), (180, 138, 106))
    d.rounded_rectangle([s(180), s(1560), s(900), s(1760)], s(80), fill=(232, 160, 120))
    return im


def rellano():
    im = grad(W, H, (236, 226, 200), (220, 208, 178)).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rectangle([0, s(1450), W, H], fill=(170, 160, 150))
    for x in range(0, W, s(120)): d.line([x, s(1450), x, H], fill=(156, 146, 136), width=s(3))
    # puerta de Carmen
    d.rectangle([s(420), s(400), s(900), s(1450)], fill=(120, 70, 50), outline=OL, width=s(6))
    d.rectangle([s(450), s(430), s(870), s(1450)], fill=(140, 84, 60))
    d.ellipse([s(640), s(600), s(680), s(640)], fill=(240, 220, 150), outline=OL, width=s(3))
    d.text((s(560), s(470)), "2ºB", font=font(s(70)), fill=(240, 210, 140))
    # planta
    d.polygon([(s(110), s(1450)), (s(250), s(1450)), (s(230), s(1280)), (s(130), s(1280))], fill=(210, 110, 80), outline=OL)
    for a in range(-60, 61, 30):
        r = math.radians(a - 90)
        d.ellipse([s(180) + s(170) * math.cos(r) - s(50), s(1220) + s(170) * math.sin(r) - s(90), s(180) + s(170) * math.cos(r) + s(50), s(1220) + s(170) * math.sin(r) + s(90)], fill=(90, 160, 100), outline=OL, width=s(3))
    d.rectangle([s(990), s(300), s(1080), s(1450)], fill=(230, 230, 222), outline=OL, width=s(4))   # barandilla/ascensor
    return im


def bano(oscuro=0.0):
    im = grad(W, H, (200, 230, 240), (180, 214, 230)).convert("RGBA")
    d = ImageDraw.Draw(im)
    for y in range(0, s(1450), s(110)):
        for x in range(0, W, s(110)):
            d.rectangle([x + s(4), y + s(4), x + s(106), y + s(106)], fill=(214, 238, 246))
    # bañera y lavabo
    d.rounded_rectangle([s(-40), s(1000), s(430), s(1460)], s(60), fill=(255, 255, 255), outline=OL, width=s(6))
    d.rounded_rectangle([s(700), s(820), s(1000), s(900)], s(30), fill=(255, 255, 255), outline=OL, width=s(6))
    d.rectangle([s(820), s(900), s(880), s(1450)], fill=(240, 240, 240), outline=OL, width=s(4))
    d.rounded_rectangle([s(740), s(380), s(960), s(760)], s(40), fill=(220, 240, 250), outline=(200, 170, 110), width=s(12))
    d.rectangle([0, s(1450), W, H], fill=(150, 196, 214))
    for x in range(0, W, s(120)): d.line([x, s(1450), x - s(200), H], fill=(136, 182, 200), width=s(3))
    if oscuro > 0:
        lay = Image.new("RGBA", im.size, (20, 24, 50, int(150 * oscuro)))
        im.alpha_composite(lay)
    return im


def cesto(im, cx, by, sc, wob=0.0, tapa=0.0):
    """Cesto de mimbre. wob: inclinación (-1..1). tapa: 0 cerrada .. 1 levantada."""
    lay = Image.new("RGBA", (s(420), s(560)), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0, x1, y0, y1 = s(40), s(380), s(140), s(540)
    d.polygon([(x0, y0), (x1, y0), (x1 - s(30), y1), (x0 + s(30), y1)], fill=(214, 170, 110), outline=OL)
    for y in range(y0 + s(30), y1, s(46)):
        d.line([x0 + s(10), y, x1 - s(10), y], fill=(180, 136, 80), width=s(8))
    for x in range(x0 + s(40), x1, s(56)):
        d.line([x, y0, x + s(4), y1], fill=(196, 150, 92), width=s(5))
    # calcetín asomando
    d.rounded_rectangle([s(250), y0 - s(40), s(300), y0 + s(30)], s(20), fill=(240, 90, 120), outline=OL, width=s(3))
    if tapa < .5:
        d.rounded_rectangle([x0 - s(14), y0 - s(40) - tapa * s(80), x1 + s(14), y0 + s(10) - tapa * s(80)], s(20), fill=(200, 150, 90), outline=OL, width=s(5))
    lay = lay.rotate(wob * 7, resample=Image.BICUBIC, center=(s(210), s(540)))
    lay = lay.resize((int(lay.width * sc), int(lay.height * sc)))
    sombra_pies(im, cx, by, s(180) * sc)
    im.alpha_composite(lay, (int(cx - lay.width / 2), int(by - lay.height)))


def estrella(d, cx, cy, r, col, outline=None):
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * .45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=col, outline=outline)


# ======================= PERSONAJES =======================
PIEL = (255, 210, 175)
DANI = dict(piel=PIEL, pelo=(70, 45, 30), camisa=(110, 150, 220), pantalon=(80, 110, 180), pelo_estilo="corto", rayas=(150, 184, 240))
MAMA = dict(piel=PIEL, pelo=(140, 70, 40), camisa=(240, 120, 110), pantalon=(60, 60, 90), pelo_estilo="largo")
VERA = dict(piel=PIEL, pelo=(100, 55, 30), camisa=(160, 110, 210), pantalon=(80, 80, 140), pelo_estilo="coletas", tipo="nino", extra="estrella")
HUGO = dict(piel=PIEL, pelo=(230, 170, 80), camisa=(250, 200, 70), pantalon=(80, 120, 200), pelo_estilo="rizos", tipo="nino", extra="dino")
CARMEN = dict(piel=(250, 206, 176), pelo=(200, 200, 210), camisa=(170, 120, 190), pantalon=(120, 90, 150), pelo_estilo="rulos", gafas=True)


def _ojos(d, cx, cy, r, mira, susto, cerrado, lw):
    for dx in (-1, 1):
        ex = cx + dx * r * 1.9
        if cerrado:
            d.arc([ex - r, cy - r * .4, ex + r, cy + r * .8], 200, 340, fill=OL, width=lw)
            continue
        rr = r * (1.25 if susto else 1)
        d.ellipse([ex - rr, cy - rr * 1.15, ex + rr, cy + rr * 1.15], fill=(255, 255, 255), outline=OL, width=lw)
        pr = rr * (.45 if susto else .56)
        px, py = ex + mira[0] * rr * .38, cy + mira[1] * rr * .38
        d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(50, 35, 30))
        d.ellipse([px - pr * .05, py - pr * .75, px + pr * .45, py - pr * .25], fill=(255, 255, 255))


def persona(im, x, y, h, **kw):
    """Dibuja en una capa local (rápido) y la pega en im. Devuelve posiciones en coordenadas de im."""
    ox, oy = int(x - h * .62), int(y - h * 1.2)
    lay = Image.new("RGBA", (int(h * 1.24), int(h * 1.32)), (0, 0, 0, 0))
    info = _persona(lay, x - ox, y - oy, h, **kw)
    im.paste(lay, (ox, oy), lay)
    info["x"] += ox; info["hy"] += oy; info["ty"] += oy
    info["manos"] = [(a + ox, b + oy, c) for a, b, c in info["manos"]]
    return info


def _persona(im, x, y, h, piel, pelo, camisa, pantalon, tipo="adulto", expr="normal", brazos="abajo",
            pelo_estilo="corto", mira=(0, 0), extra=None, boca=0.0, cerrado=False, rayas=None, barba=False,
            gafas=False, ladeo=0.0, calcetin=False, lagrimas=False):
    """(x, y) = pies. h = altura total (px en lienzo S). boca 0..1 = apertura al hablar."""
    d = ImageDraw.Draw(im)
    nino = tipo != "adulto"
    head = h * (.115 if not nino else .2)
    body_h = h * (.34 if not nino else .30)
    leg_h = h - head * 2 - body_h if not nino else h - head * 1.9 - body_h
    bw = h * (.27 if not nino else .32)
    lw = max(3, int(h * .011))
    sombra_pies(im, x, y, bw * .8)
    ly = y - leg_h
    for dx in (-1, 1):
        d.rounded_rectangle([x + dx * bw * .22 - bw * .14, ly - 10, x + dx * bw * .22 + bw * .14, y - h * .02], int(bw * .1), fill=pantalon, outline=OL, width=lw)
        d.rounded_rectangle([x + dx * bw * .22 - bw * .2, y - h * .045, x + dx * bw * .22 + bw * .2 + dx * bw * .05, y], int(h * .02),
                            fill=(70, 70, 90) if not nino else (240, 90, 90), outline=OL, width=lw)
    ty = ly - body_h
    tor = Image.new("RGBA", im.size, (0, 0, 0, 0)); td = ImageDraw.Draw(tor)
    td.rounded_rectangle([x - bw / 2, ty, x + bw / 2, ly + 10], int(bw * .3), fill=camisa, outline=OL, width=lw)
    if rayas:
        mask = Image.new("L", im.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([x - bw / 2 + lw, ty + lw, x + bw / 2 - lw, ly + 10 - lw], int(bw * .3), fill=255)
        st = Image.new("RGBA", im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        k = int(bw * .16)
        for yy in range(int(ty), int(ly + 10), k * 2): sd.rectangle([x - bw, yy, x + bw, yy + k], fill=rayas)
        tor.paste(st, (0, 0), mask)
        td.rounded_rectangle([x - bw / 2, ty, x + bw / 2, ly + 10], int(bw * .3), outline=OL, width=lw)
    im.alpha_composite(tor)
    d = ImageDraw.Draw(im)
    if extra == "dino":
        d.ellipse([x - bw * .2, ty + body_h * .3, x + bw * .2, ty + body_h * .64], fill=(120, 200, 110), outline=OL, width=max(2, lw // 2))
        d.ellipse([x + bw * .02, ty + body_h * .38, x + bw * .1, ty + body_h * .46], fill=OL)
    if extra == "estrella":
        estrella(d, x, ty + body_h * .45, bw * .17, (255, 220, 90), OL)
    if extra == "bolsillo":
        d.rounded_rectangle([x + bw * .08, ty + body_h * .22, x + bw * .34, ty + body_h * .42], int(bw * .04), outline=OL, width=lw)
    aw = bw * .2
    sh_y = ty + body_h * .12
    manos = []
    for dx in (-1, 1):
        sx = x + dx * bw * .45
        m = {"arriba": (sx + dx * bw * .45, sh_y - body_h * .7), "jarras": (sx + dx * bw * .2, sh_y + body_h * .55),
             "cruzados": (x - dx * bw * .2, sh_y + body_h * .45), "tablet": (x + dx * bw * .2, sh_y + body_h * .4),
             "abrazo": (x - dx * bw * .05, sh_y + body_h * .5), "cabeza": (sx + dx * bw * .05, sh_y - body_h * .55),
             "abiertos": (sx + dx * bw * .55, sh_y + body_h * .2), "boca": (x + dx * bw * .08, sh_y - body_h * .05)}
        if brazos == "bebe":
            ex, ey = (x + bw * .05, sh_y + body_h * .62) if dx == -1 else (x + bw * .15, sh_y + body_h * .38)
        elif brazos == "maleta":
            ex, ey = (sx + dx * bw * .12, sh_y + body_h * .85) if dx == -1 else (sx + bw * .3, sh_y + body_h * .9)
        elif brazos == "saluda":
            ex, ey = (sx + dx * bw * .12, sh_y + body_h * .85) if dx == -1 else (sx + bw * .45, sh_y - body_h * .65)
        elif brazos == "movil":
            ex, ey = (sx + dx * bw * .12, sh_y + body_h * .85) if dx == -1 else (x + bw * .35, sh_y - body_h * .15)
        else:
            ex, ey = m.get(brazos, (sx + dx * bw * .12, sh_y + body_h * .85))
        d.line([sx, sh_y, ex, ey], fill=OL, width=int(aw + lw * 2))
        d.line([sx, sh_y, ex, ey], fill=camisa, width=int(aw))
        manos.append((ex, ey, aw))
    # cuello + cabeza (en capa para poder ladear)
    hy = ty - head * .95
    d.rectangle([x - head * .25, ty - head * .25, x + head * .25, ty + 6], fill=piel)
    cab = Image.new("RGBA", im.size, (0, 0, 0, 0)); c = ImageDraw.Draw(cab)
    if pelo_estilo == "largo":
        for dx in (-1, 1):
            c.rounded_rectangle([x + dx * head * .62 - head * .45, hy - head * .5, x + dx * head * .62 + head * .45, hy + head * 1.45], int(head * .4), fill=pelo, outline=OL, width=lw)
    if pelo_estilo == "coletas":
        for dx in (-1, 1):
            c.ellipse([x + dx * head * 1.05 - head * .42, hy + head * .1, x + dx * head * 1.05 + head * .42, hy + head * .95], fill=pelo, outline=OL, width=lw)
            c.ellipse([x + dx * head * .9 - head * .12, hy + head * .1, x + dx * head * .9 + head * .12, hy + head * .32], fill=(240, 90, 130))
    c.ellipse([x - head, hy - head, x + head, hy + head], fill=piel, outline=OL, width=lw)
    for dx in (-1, 1):
        c.ellipse([x + dx * head * .98 - head * .16, hy - head * .05, x + dx * head * .98 + head * .16, hy + head * .3], fill=piel, outline=OL, width=lw)
    if barba:
        for k in range(26):
            a = math.radians(20 + k * 140 / 25)
            px, py = x + head * .78 * math.cos(a), hy + head * .78 * math.sin(a)
            c.ellipse([px - lw * .5, py - lw * .5, px + lw * .5, py + lw * .5], fill=(150, 110, 90))
    if pelo_estilo == "rulos":
        c.chord([x - head * 1.05, hy - head * 1.1, x + head * 1.05, hy + head * .5], 180, 360, fill=pelo, outline=OL, width=lw)
        for k in range(4):
            rx = x - head * .75 + k * head * .5
            c.rounded_rectangle([rx - head * .18, hy - head * 1.2, rx + head * .18, hy - head * .72], int(head * .1), fill=(250, 140, 170), outline=OL, width=max(2, lw // 2))
    elif pelo_estilo in ("corto", "coletas", "largo", "rizos"):
        c.chord([x - head * 1.04, hy - head * 1.08, x + head * 1.04, hy + head * .55], 180, 360, fill=pelo, outline=OL, width=lw)
        if pelo_estilo == "rizos":
            for k in range(7):
                a = math.pi + k * math.pi / 6
                cx, cy = x + head * .95 * math.cos(a), hy - head * .15 + head * .9 * math.sin(a)
                c.ellipse([cx - head * .3, cy - head * .3, cx + head * .3, cy + head * .3], fill=pelo, outline=OL, width=lw)
        else:
            c.pieslice([x - head * .9, hy - head * .75, x + head * .2, hy + head * .05], 180, 270, fill=pelo)
    if pelo_estilo == "corto":
        c.polygon([(x - head * .2, hy - head * .95), (x + head * .1, hy - head * 1.28), (x + head * .25, hy - head * .9)], fill=pelo, outline=OL)
    for dx in (-1, 1):
        c.ellipse([x + dx * head * .55 - head * .16, hy + head * .25, x + dx * head * .55 + head * .16, hy + head * .42], fill=(250, 150, 140))
    er = head * (.17 if not nino else .2)
    _ojos(c, x, hy + head * .02, er, mira, expr in ("susto", "panico"), cerrado, lw)
    if gafas:
        for dx in (-1, 1):
            ex = x + dx * er * 1.9
            c.ellipse([ex - er * 1.5, hy - er * 1.4, ex + er * 1.5, hy + er * 1.6], outline=(120, 60, 120), width=lw)
        c.line([x - er * .4, hy, x + er * .4, hy], fill=(120, 60, 120), width=lw)
    for dx in (-1, 1):
        ex = x + dx * er * 1.9
        if expr in ("susto", "panico"):
            c.arc([ex - er * 1.1, hy - er * 2.7, ex + er * 1.1, hy - er * 1.0], 200, 340, fill=OL, width=lw)
        elif expr in ("enfado", "listilla"):
            c.line([ex - dx * er, hy - er * 1.8, ex + dx * er, hy - er * 1.35], fill=OL, width=lw)
        elif expr in ("triste", "llora"):
            c.line([ex - dx * er, hy - er * 1.35, ex + dx * er, hy - er * 1.85], fill=OL, width=lw)
        else:
            c.arc([ex - er, hy - er * 2.2, ex + er, hy - er * 1.1], 200, 340, fill=OL, width=lw)
    my = hy + head * .52
    if boca > .12:
        bh = head * (.08 + .3 * min(1, boca)); bwid = head * (.2 + .1 * min(1, boca))
        c.chord([x - bwid, my - bh * .4, x + bwid, my + bh], 0, 360, fill=(160, 50, 60), outline=OL, width=lw)
        c.ellipse([x - bwid * .5, my + bh * .35, x + bwid * .5, my + bh * .9], fill=(240, 120, 130))
    elif expr == "risa":
        c.chord([x - head * .32, my - head * .2, x + head * .32, my + head * .3], 0, 180, fill=(170, 50, 60), outline=OL, width=lw)
    elif expr in ("susto", "panico"):
        c.ellipse([x - head * .13, my - head * .08, x + head * .13, my + head * .2], fill=(120, 40, 50), outline=OL, width=lw)
    elif expr == "listilla":
        c.arc([x - head * .2, my - head * .15, x + head * .3, my + head * .1], 10, 150, fill=OL, width=lw)
    elif expr in ("triste", "llora"):
        c.arc([x - head * .2, my - head * .02, x + head * .2, my + head * .22], 200, 340, fill=OL, width=lw)
    elif expr == "forzada":
        c.rounded_rectangle([x - head * .32, my - head * .08, x + head * .32, my + head * .14], int(head * .06), fill=(255, 255, 255), outline=OL, width=lw)
        for k in range(1, 4): c.line([x - head * .32 + k * head * .16, my - head * .08, x - head * .32 + k * head * .16, my + head * .14], fill=OL, width=max(1, lw // 2))
    else:
        c.arc([x - head * .22, my - head * .18, x + head * .22, my + head * .1], 20, 160, fill=OL, width=lw)
    if lagrimas:
        for dx in (-1, 1):
            ex = x + dx * er * 1.9
            c.ellipse([ex - er * .3, hy + er * 1.3, ex + er * .3, hy + er * 2.3], fill=(130, 200, 255))
    if calcetin:
        c.polygon([(x - head * .7, hy - head * .85), (x + head * .5, hy - head * 1.05), (x + head * .9, hy - head * 1.6), (x + head * 1.2, hy - head * 1.35), (x + head * .75, hy - head * .7)], fill=(240, 90, 120), outline=OL)
    if ladeo:
        cab = cab.rotate(ladeo, resample=Image.BICUBIC, center=(x, ty))
    im.alpha_composite(cab)
    d = ImageDraw.Draw(im)
    for ex, ey, aw_ in manos:
        d.ellipse([ex - aw_ * .72, ey - aw_ * .72, ex + aw_ * .72, ey + aw_ * .72], fill=piel, outline=OL, width=lw)
    return dict(x=x, hy=hy, head=head, ty=ty, body_h=body_h, bw=bw, manos=manos)


def bebe(im, x, y, r, llora=True, t=0.0):
    d = ImageDraw.Draw(im)
    lw = max(3, int(r * .06))
    d.ellipse([x - r * 1.1, y, x + r * 1.1, y + r * 1.6], fill=(170, 215, 245), outline=OL, width=lw)
    d.ellipse([x - r, y - r * 1.6, x + r, y + r * .3], fill=(255, 214, 180), outline=OL, width=lw)
    hy = y - r * .65
    d.arc([x - r * .3, hy - r * 1.05, x + r * .1, hy - r * .65], 180, 360, fill=OL, width=lw)
    if llora:
        o = .75 + .25 * math.sin(t * 18)
        for dx in (-1, 1):
            ex = x + dx * r * .38
            d.arc([ex - r * .18, hy - r * .1, ex + r * .18, hy + r * .12], 200, 340, fill=OL, width=lw)
            ty_ = hy + r * .12 + ((t * 1.6 + (dx + 1) * .3) % 1) * r * .5
            d.ellipse([ex - r * .07, ty_, ex + r * .07, ty_ + r * .2], fill=(120, 190, 255))
        d.ellipse([x - r * .25 * o, hy + r * .3, x + r * .25 * o, hy + r * (.3 + .4 * o)], fill=(170, 50, 60), outline=OL, width=lw)
    else:
        for dx in (-1, 1):
            ex = x + dx * r * .38
            d.arc([ex - r * .14, hy - r * .05, ex + r * .14, hy + r * .12], 20, 160, fill=OL, width=lw)
        d.arc([x - r * .2, hy + r * .25, x + r * .2, hy + r * .5], 20, 160, fill=OL, width=lw)


def maleta(im, x, y, h):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([x - h * .32, y - h, x + h * .32, y], int(h * .08), fill=(230, 90, 90), outline=OL, width=max(3, int(h * .02)))
    d.rounded_rectangle([x - h * .14, y - h * 1.12, x + h * .14, y - h], int(h * .03), outline=OL, width=max(3, int(h * .025)))
    for k in (-1, 1): d.line([x + k * h * .16, y - h, x + k * h * .16, y], fill=(200, 70, 70), width=max(3, int(h * .03)))
    for k in (-1, 1): d.ellipse([x + k * h * .22 - h * .04, y - h * .02, x + k * h * .22 + h * .04, y + h * .06], fill=(60, 60, 60))


def tablet(im, cx, cy, w, t, sonando=True, nombre="MAMÁ"):
    d = ImageDraw.Draw(im)
    hgt = w * .7
    d.rounded_rectangle([cx - w / 2, cy - hgt / 2, cx + w / 2, cy + hgt / 2], int(w * .06), fill=(40, 40, 50), outline=OL, width=max(3, int(w * .015)))
    scr = [cx - w / 2 + w * .05, cy - hgt / 2 + w * .05, cx + w / 2 - w * .05, cy + hgt / 2 - w * .05]
    d.rounded_rectangle(scr, int(w * .03), fill=(70, 200, 140) if sonando else (30, 30, 40))
    if sonando:
        p = (t * 2) % 1
        for k in range(2):
            r = w * (.12 + .18 * ((p + k * .5) % 1))
            d.ellipse([cx - r, cy - w * .08 - r, cx + r, cy - w * .08 + r], outline=(255, 255, 255), width=max(2, int(w * .01)))
        d.ellipse([cx - w * .1, cy - w * .18, cx + w * .1, cy + w * .02], fill=(255, 210, 175), outline=OL, width=max(2, int(w * .01)))
        d.chord([cx - w * .11, cy - w * .2, cx + w * .11, cy - w * .02], 180, 360, fill=(140, 70, 40))
        f = font(w * .1)
        tw = d.textlength(nombre, font=f)
        d.text((cx - tw / 2, cy + w * .07), nombre, font=f, fill=(255, 255, 255))


def galleta(im, cx, cy, r):
    d = ImageDraw.Draw(im)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(210, 160, 90), outline=OL, width=max(3, int(r * .06)))
    for k in range(6):
        a = k * 1.05
        d.ellipse([cx + r * .55 * math.cos(a) - r * .1, cy + r * .55 * math.sin(a) - r * .1, cx + r * .55 * math.cos(a) + r * .1, cy + r * .55 * math.sin(a) + r * .1], fill=(90, 50, 30))
    for k in range(9):
        a = k * .7 + 2
        d.ellipse([cx + r * .7 * math.cos(a) - r * .13, cy + r * .7 * math.sin(a) - r * .13, cx + r * .7 * math.cos(a) + r * .13, cy + r * .7 * math.sin(a) + r * .13], fill=(130, 190, 110))
    d.rectangle([cx - r * .6, cy - r * .15, cx - r * .3, cy + r * .15], fill=(210, 160, 90))
