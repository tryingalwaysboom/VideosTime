"""Sergio v3: personaje propio, adorable y raro (sin moscas, sin olor, sin granos). Mas detalle, luz y textura."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import random, math, os
BLINK = os.environ.get("BLINK", "0") == "1"
MOUTH = os.environ.get("MOUTH", "closed")
NOTE = os.environ.get("NOTE", "0") == "1"
TAGS = os.environ.get("TAGS", "0") == "1"
OUT = os.environ.get("OUT", "/tmp/sergio_var")

S = 2
W, H = 1080 * S, 1920 * S
F = "/home/claude/videostime/mateo-pov/fonts/Baloo2-ExtraBold.ttf"
def s(v): return int(round(v * S))
def font(n): return ImageFont.truetype(F, s(n))
def dark(c, k=0.72): return tuple(int(x * k) for x in c[:3])
def light(c, k=1.18): return tuple(min(255, int(x * k)) for x in c[:3])

# ---------- fondo con degradado ----------
im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
d = ImageDraw.Draw(im)
for y in range(0, s(1120)):
    t = y / s(1120)
    d.line([0, y, W, y], fill=(int(226 - 28 * t), int(170 - 20 * t), int(150 - 10 * t)))
for y in range(s(1120), H):
    t = (y - s(1120)) / (H - s(1120))
    d.line([0, y, W, y], fill=(int(150 - 40 * t), int(86 - 26 * t), int(76 - 22 * t)))
# papel pintado de estrellitas
rr = random.Random(2)
for _ in range(190):
    x, y = rr.randint(0, 1080), rr.randint(0, 1100)
    r = rr.choice((3, 4, 5))
    d.polygon([(s(x), s(y - r * 2)), (s(x + r / 1.5), s(y - r / 1.5)), (s(x + r * 2), s(y)), (s(x + r / 1.5), s(y + r / 1.5)),
               (s(x), s(y + r * 2)), (s(x - r / 1.5), s(y + r / 1.5)), (s(x - r * 2), s(y)), (s(x - r / 1.5), s(y - r / 1.5))], fill=(236, 188, 160))
d.rectangle([0, s(1108), W, s(1132)], fill=(96, 56, 52))
for y in range(1132, 1920, 100):                      # tarimas
    d.line([0, s(y), W, s(y)], fill=(120, 66, 60), width=s(3))

def shp(kind, box, fill, w=4, **kw):
    o = dark(fill, .7)
    if kind == "rr": d.rounded_rectangle([s(v) for v in box], s(kw.get("r", 20)), fill=fill, outline=o, width=s(w))
    elif kind == "el": d.ellipse([s(v) for v in box], fill=fill, outline=o, width=s(w))
    elif kind == "po": d.polygon([(s(x), s(y)) for x, y in box], fill=fill, outline=o)

def ov(fn, blur=0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fn(ImageDraw.Draw(lay))
    if blur: lay = lay.filter(ImageFilter.GaussianBlur(s(blur)))
    im.alpha_composite(lay)

# ---------- luz de guirnalda (arriba, decorativa) ----------
pts = [(x, 215 + 34 * math.sin(x / 170 * math.pi)) for x in range(-20, 1110, 20)]
d.line([(s(x), s(y)) for x, y in pts], fill=(70, 50, 54), width=s(3))
cols = [(255, 214, 90), (255, 140, 120), (150, 230, 255), (255, 214, 90)]
for i, (x, y) in enumerate(pts[::3]):
    c = cols[i % 4]
    ov(lambda g, x=x, y=y, c=c: g.ellipse([s(x - 40), s(y - 30), s(x + 40), s(y + 50)], fill=c + (70,)), 12)
    d.ellipse([s(x - 9), s(y + 4), s(x + 9), s(y + 28)], fill=c, outline=dark(c, .7), width=s(2))

# ---------- mapa del barrio con circulo rojo (el "radio") ----------
shp("rr", (840, 330, 1050, 530), (250, 244, 224), 5, r=8)
for k in range(5):
    d.line([s(850), s(360 + k * 34), s(1040), s(352 + k * 34)], fill=(200, 190, 160), width=s(2))
    d.line([s(870 + k * 40), s(338), s(862 + k * 40), s(522)], fill=(200, 190, 160), width=s(2))
d.line([s(850), s(500), s(1040), s(380)], fill=(150, 190, 220), width=s(7))        # rio
d.ellipse([s(920), s(400), s(970), s(450)], outline=(214, 60, 60), width=s(5))
d.ellipse([s(939), s(419), s(951), s(431)], fill=(214, 60, 60))
d.text((s(852), s(334)), "MI BARRIO", font=font(26), fill=(120, 90, 80))
d.ellipse([s(937), s(322), s(953), s(338)], fill=(230, 70, 70))                    # chincheta
# calendario 2020 colgado debajo
shp("rr", (880, 560, 1010, 690), (255, 252, 246), 5, r=8)
d.rectangle([s(880), s(560), s(1010), s(598)], fill=(220, 90, 80))
d.text((s(897), s(604)), "2020", font=font(44), fill=(90, 70, 70))

# ---------- PUERTA con cerrojos y cadena ----------
shp("rr", (40, 300, 430, 1110), (44, 96, 110), 7, r=14)
for b in ((75, 345, 395, 700), (75, 740, 395, 1070)):
    shp("rr", b, (52, 112, 126), 5, r=10)
    ov(lambda g, b=b: g.rounded_rectangle([s(b[0] + 8), s(b[1] + 8), s(b[2] - 8), s(b[1] + 30)], s(8), fill=(255, 255, 255, 35)))
d.ellipse([s(346), s(770), s(386), s(810)], fill=(240, 200, 90), outline=(150, 110, 30), width=s(4))
# 3 cerrojos
for y in (420, 520, 620):
    shp("rr", (320, y, 410, y + 34), (170, 170, 184), 4, r=8)
    d.ellipse([s(396), s(y + 5), s(414), s(y + 23)], fill=(100, 100, 116))
# cadena
for i in range(7):
    d.ellipse([s(300 + i * 14), s(660 + (6 if i % 2 else 0)), s(318 + i * 14), s(680 + (6 if i % 2 else 0))], outline=(190, 190, 204), width=s(4))
# mirilla y cartel
d.ellipse([s(228), s(380), s(252), s(404)], fill=(30, 30, 40), outline=(220, 200, 120), width=s(5))
shp("rr", (150, 870, 340, 930), (255, 236, 170), 4, r=10)
d.text((s(162), s(881)), "NO MOLESTAR", font=font(28), fill=(150, 60, 50))
d.line([s(235), s(870), s(366), s(800)], fill=(150, 110, 30), width=s(3))
# luz por la rendija + nota
ov(lambda g: g.ellipse([s(20), s(1070), s(470), s(1280)], fill=(255, 236, 170, 110)), 30)
d.rectangle([s(40), s(1094), s(430), s(1112)], fill=(255, 238, 180))
nota = Image.new("RGBA", (s(250), s(180)), (0, 0, 0, 0))
nd = ImageDraw.Draw(nota)
nd.rectangle([s(7), s(7), s(238), s(166)], fill=(0, 0, 0, 55))
nd.rectangle([0, 0, s(232), s(158)], fill=(252, 250, 242), outline=(190, 180, 160), width=s(3))
for i, ly in enumerate((40, 72, 104)):
    nd.line([s(22), s(ly), s(176 - i * 24), s(ly)], fill=(60, 84, 205), width=s(6))
r2 = random.Random(4)
for _ in range(30):
    x, y = r2.randint(14, 216), r2.randint(14, 142)
    nd.ellipse([s(x), s(y), s(x + 5), s(y + 5)], fill=(110, 170, 255))
nd.ellipse([s(176), s(112), s(214), s(148)], fill=(214, 70, 90))
nota = nota.rotate(-8, expand=True, resample=Image.BICUBIC)
nota.save(os.path.join(os.path.dirname(OUT), "nota_sprite.png"))
if NOTE:
    im.alpha_composite(nota, (s(115), s(1000)))
d = ImageDraw.Draw(im)

# ---------- cajas de cartón con gato dormido ----------
for (x0, y0, x1, y1) in [(850, 930, 1070, 1110), (880, 800, 1050, 935)]:
    shp("rr", (x0, y0, x1, y1), (200, 150, 96), 5, r=8)
    d.line([s((x0 + x1) // 2), s(y0), s((x0 + x1) // 2), s(y1)], fill=(226, 190, 140), width=s(10))
d.text((s(900), s(1000)), "FRÁGIL", font=font(30), fill=(150, 70, 50))
cat = (232, 150, 70)
d.ellipse([s(880), s(742), s(1040), s(830)], fill=cat, outline=dark(cat, .7), width=s(4))
d.ellipse([s(980), s(735), s(1052), s(800)], fill=cat, outline=dark(cat, .7), width=s(4))
d.polygon([(s(986), s(745)), (s(992), s(712)), (s(1010), s(738))], fill=cat, outline=dark(cat, .7))
d.polygon([(s(1024), s(738)), (s(1044), s(714)), (s(1050), s(750))], fill=cat, outline=dark(cat, .7))
d.arc([s(990), s(762), s(1008), s(772)], 0, 180, fill=(70, 40, 40), width=s(3))
d.arc([s(1022), s(762), s(1040), s(772)], 0, 180, fill=(70, 40, 40), width=s(3))
d.text((s(1060), s(690)), "z", font=font(36), fill=(255, 255, 255))

# ================= SERGIO =================
cx = 640
skin = (238, 216, 198)
poncho_a, poncho_b = (122, 72, 128), (240, 226, 196)
# sombra suave
ov(lambda g: g.ellipse([s(cx - 240), s(1090), s(cx + 240), s(1170)], fill=(60, 30, 30, 150)), 14)
d = ImageDraw.Draw(im)
# circulo de tiza alrededor (el "radio de libertad")
d.ellipse([s(cx - 260), s(1060), s(cx + 260), s(1190)], outline=(255, 255, 245), width=s(5))

def thick(pts, w, fill, ol=True):
    P = [(s(x), s(y)) for x, y in pts]
    if ol:
        o = dark(fill, .62)
        d.line(P, fill=o, width=s(w + 8), joint="curve")
        for p in (P[0], P[-1]):
            d.ellipse([p[0] - s(w / 2 + 4), p[1] - s(w / 2 + 4), p[0] + s(w / 2 + 4), p[1] + s(w / 2 + 4)], fill=o)
    d.line(P, fill=fill, width=s(w), joint="curve")
    for p in (P[0], P[-1]):
        d.ellipse([p[0] - s(w / 2), p[1] - s(w / 2), p[0] + s(w / 2), p[1] + s(w / 2)], fill=fill)

# ---- piernas de pijama a rayas con arrugas y puños ----
for dx in (-78, 38):
    x0 = cx + dx
    shp("rr", (x0, 955, x0 + 70, 1110), (244, 244, 248), 4, r=14)
    for yy in range(968, 1100, 26):
        d.rectangle([s(x0 + 4), s(yy), s(x0 + 66), s(yy + 11)], fill=(96, 170, 190))
    for k in range(3):
        d.arc([s(x0 + 6), s(1000 + k * 28), s(x0 + 64), s(1030 + k * 28)], 20, 160, fill=(150, 160, 180), width=s(3))
    d.rectangle([s(x0 - 2), s(1086), s(x0 + 72), s(1108)], fill=(96, 170, 190), outline=dark((96, 170, 190), .7), width=s(3))
    ov(lambda g, x0=x0: g.rounded_rectangle([s(x0 + 4), s(960), s(x0 + 22), s(1100)], s(8), fill=(255, 255, 255, 60)))
# ---- zapatillas de conejo: pelo en el borde, costuras, ojitos y orejas ----
for dx in (-102, 20):
    x0 = cx + dx
    for ex in (14, 64):
        shp("el", (x0 + ex, 1024, x0 + ex + 30, 1090), (250, 198, 214), 4)
        d.ellipse([s(x0 + ex + 8), s(1034), s(x0 + ex + 22), s(1076)], fill=(238, 140, 170))
    shp("rr", (x0, 1074, x0 + 138, 1146), (246, 176, 196), 5, r=34)
    zz = []
    for i in range(12):
        zz += [(s(x0 + 8 + i * 11), s(1080 + (0 if i % 2 else 10)))]
    d.line(zz, fill=(255, 232, 240), width=s(6))
    d.ellipse([s(x0 + 96), s(1098), s(x0 + 106), s(1108)], fill=(60, 40, 50))
    d.ellipse([s(x0 + 112), s(1098), s(x0 + 122), s(1108)], fill=(60, 40, 50))
    d.ellipse([s(x0 + 106), s(1112), s(x0 + 116), s(1120)], fill=(226, 110, 140))
    for i in range(6):
        d.line([s(x0 + 14 + i * 12), s(1132), s(x0 + 18 + i * 12), s(1140)], fill=(214, 140, 166), width=s(3))

# ---- poncho de punto: degradado, rayas, puntos de tejer, pliegues, cuello acanalado ----
pon = [(cx - 165, 645), (cx + 165, 645), (cx + 240, 1012), (cx - 240, 1012)]
mask = Image.new("L", (W, H), 0)
ImageDraw.Draw(mask).polygon([(s(x), s(y)) for x, y in pon], fill=255)
lay = Image.new("RGBA", (W, H), poncho_a + (255,))
ld = ImageDraw.Draw(lay)
bands = [(690, 735, poncho_b), (775, 800, (232, 180, 72)), (840, 885, poncho_b), (925, 950, (232, 180, 72)), (975, 1020, poncho_b)]
for y0, y1, c in bands:
    ld.rectangle([0, s(y0), W, s(y1)], fill=c)
# punto: pequeñas "v" repetidas
for yy in range(660, 1015, 13):
    for xx in range(cx - 250, cx + 252, 13):
        off = 6 if (yy // 13) % 2 else 0
        ld.line([s(xx + off), s(yy), s(xx + off + 4), s(yy + 9)], fill=(0, 0, 0, 22), width=s(2))
        ld.line([s(xx + off + 8), s(yy), s(xx + off + 4), s(yy + 9)], fill=(0, 0, 0, 22), width=s(2))
# motivo de rombos en la franja ancha
for xx in range(cx - 220, cx + 221, 44):
    ld.polygon([(s(xx), s(905)), (s(xx + 12), s(918)), (s(xx), s(931)), (s(xx - 12), s(918))], fill=(122, 72, 128))
# sombras laterales y luz izquierda
shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(shade)
sd.polygon([(s(cx + 90), s(645)), (s(cx + 165), s(645)), (s(cx + 245), s(1012)), (s(cx + 130), s(1012))], fill=(40, 10, 50, 85))
sd.polygon([(s(cx - 165), s(645)), (s(cx - 100), s(645)), (s(cx - 160), s(1012)), (s(cx - 245), s(1012))], fill=(255, 255, 255, 40))
for fx in (-60, 20, 95):                             # pliegues de tela
    sd.line([(s(cx + fx), s(680)), (s(cx + fx * 1.5 + 6), s(850)), (s(cx + fx * 1.9), s(1010))], fill=(40, 10, 50, 70), width=s(7))
lay.alpha_composite(shade.filter(ImageFilter.GaussianBlur(s(3))))
im.paste(lay, (0, 0), mask)
d = ImageDraw.Draw(im)
d.polygon([(s(x), s(y)) for x, y in pon], outline=dark(poncho_a, .6), width=s(5))
# flecos retorcidos en mechones
for gx in range(cx - 236, cx + 240, 16):
    for k in range(2):
        d.line([s(gx + k * 5), s(1012), s(gx + k * 5 + (2 if k else -2)), s(1046)], fill=poncho_b if (gx // 16) % 2 else (232, 180, 72), width=s(5))
    d.ellipse([s(gx - 1), s(1042), s(gx + 9), s(1050)], fill=dark(poncho_b, .8))
# parche de corazón cosido
d.polygon([(s(cx - 180), s(955)), (s(cx - 160), s(935)), (s(cx - 142), s(955)), (s(cx - 160), s(985))], fill=(220, 80, 100), outline=(250, 220, 220), width=s(2))
for i in range(6):
    d.line([s(cx - 184 + i * 8), s(958 + i * 2), s(cx - 180 + i * 8), s(962 + i * 2)], fill=(250, 230, 230), width=s(2))
# cuello acanalado del poncho
shp("rr", (cx - 82, 626, cx + 82, 676), (122, 72, 128), 4, r=22)
for xx in range(cx - 70, cx + 72, 12):
    d.line([s(xx), s(632), s(xx), s(670)], fill=dark((122, 72, 128), .75), width=s(3))

# ---- brazos con manga de jersey mostaza y puños acanalados ----
manga = (232, 184, 74)
for sx in (-1, 1):
    pts = [(cx + sx * 150, 700), (cx + sx * 208, 800), (cx + sx * 100, 858)]
    thick(pts, 58, manga, ol=False)
    ov(lambda g, sx=sx: g.line([(s(cx + sx * 150 - 8), s(704)), (s(cx + sx * 206 - 8), s(802))], fill=(255, 255, 255, 60), width=s(10)))
    # puño acanalado
    wx, wy = cx + sx * 100, 858
    cuff = [(wx + sx * 14, wy - 8), (wx - sx * 4, wy + 8)]
    thick(cuff, 54, dark(manga, .82), ol=False)
    for k in range(-24, 25, 8):
        d.line([s(wx + sx * 14 - k * 0.2), s(wy - 8 + k), s(wx - sx * 4 - k * 0.2), s(wy + 8 + k)], fill=dark(manga, .6), width=s(2)) if False else None

# ---- taza ceramica con brillo y chorreo ----
shp("rr", (cx - 64, 818, cx + 64, 930), (252, 250, 244), 5, r=26)
d.rectangle([s(cx - 58), s(824), s(cx + 58), s(848)], fill=(196, 120, 70))
for dxx in (-34, 6, 40):
    d.rounded_rectangle([s(cx + dxx), s(836), s(cx + dxx + 12), s(868)], s(6), fill=(196, 120, 70))
ov(lambda g: g.rounded_rectangle([s(cx - 54), s(850), s(cx - 38), s(920)], s(8), fill=(255, 255, 255, 140)))
# asa
d.arc([s(cx + 46), s(836), s(cx + 116), s(908)], -80, 80, fill=dark((252, 250, 244), .72), width=s(16))
d.arc([s(cx + 46), s(836), s(cx + 116), s(908)], -80, 80, fill=(252, 250, 244), width=s(10))
for k in (-30, 0, 30):
    pts2 = [(s(cx + k + math.sin(t / 10 + k) * 12), s(800 - t)) for t in range(0, 74, 4)]
    d.line(pts2, fill=(255, 255, 255), width=s(5))

# ---- manos estilo plano suave: sin contorno, dedos redondeados, lineas finas de pliegue, grano ----
hskin = (244, 208, 176)
crease = (196, 138, 108)
def mano(px, py, sx, nd=4):
    """Mano plana y suave. sx=-1: mano izquierda (en pantalla), dedos hacia la derecha sobre la taza."""
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(L)
    g.rounded_rectangle([s(px - 36), s(py - 36), s(px + 36), s(py + 40)], s(30), fill=hskin)         # palma
    ys = [py - 28 + i * (56 // (nd - 1)) for i in range(nd)]
    for i, yy in enumerate(ys):
        largo = 58 - (6 if i in (0, nd - 1) else 0)
        x0 = px - sx * 4
        xa, xb = sorted((x0, x0 - sx * largo))
        g.rounded_rectangle([s(xa), s(yy - 11), s(xb), s(yy + 11)], s(11), fill=hskin)
        g.line([s(xa + 6), s(yy + 12), s(xb - 6), s(yy + 12)], fill=crease + (230,), width=s(2))         # linea entre dedos
        kx = xb - 14 if sx < 0 else xa + 14
        g.line([s(kx), s(yy - 5), s(kx + 2), s(yy + 4)], fill=crease + (170,), width=s(2))              # nudillo
    # pulgar sobre el borde de la taza, casi horizontal
    th = Image.new("RGBA", (s(58), s(26)), (0, 0, 0, 0))
    ImageDraw.Draw(th).rounded_rectangle([0, 0, s(58), s(24)], s(12), fill=hskin)
    th = th.rotate(sx * 14, expand=True, resample=Image.BICUBIC)
    tx = px - sx * 44 if sx > 0 else px + 6
    L.alpha_composite(th, (s(tx), s(py - 62)))
    g.line([s(tx + (6 if sx < 0 else 10)), s(py - 40), s(tx + (50 if sx < 0 else 54)), s(py - 46)], fill=crease + (150,), width=s(2))
    # pliegue de palma
    g.arc([s(px - 30), s(py - 16), s(px + 6), s(py + 28)], 200, 300, fill=crease + (190,), width=s(2))
    # luz arriba, sombra suave abajo
    m = L.split()[3]
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([s(px - 36), s(py + 22), s(px + 36), s(py + 40)], s(14), fill=(150, 90, 70, 30))
    ImageDraw.Draw(sh).rounded_rectangle([s(px - 28), s(py - 34), s(px + 28), s(py - 18)], s(10), fill=(255, 255, 255, 50))
    sh.putalpha(Image.composite(sh.split()[3], Image.new("L", (W, H), 0), m))
    L.alpha_composite(sh)
    n = Image.effect_noise((W, H), 30).convert("L")
    L.alpha_composite(Image.merge("RGBA", (n, n, n, m.point(lambda v: 20 if v > 0 else 0))))
    im.alpha_composite(L)

mano(cx - 70, 880, -1)
mano(cx + 70, 880, 1, 3)
d = ImageDraw.Draw(im)

# cuello
shp("rr", (cx - 38, 596, cx + 38, 670), skin, 4, r=10)
# orejas
for sx in (-1, 1):
    shp("el", (cx + sx * 135 - 38, 440, cx + sx * 135 + 38, 560), skin, 5)
    d.ellipse([s(cx + sx * 135 - 18), s(468), s(cx + sx * 135 + 18), s(532)], fill=(224, 170, 160))
# cabeza alargada con luz y sombra
shp("rr", (cx - 135, 280, cx + 135, 650), skin, 6, r=122)
ov(lambda g: g.rounded_rectangle([s(cx - 128), s(290), s(cx - 60), s(640)], s(100), fill=(255, 255, 255, 40)), 6)
ov(lambda g: g.rounded_rectangle([s(cx + 70), s(300), s(cx + 132), s(640)], s(100), fill=(120, 70, 70, 36)), 6)
d = ImageDraw.Draw(im)
# mofletes
for sx in (-1, 1):
    ov(lambda g, sx=sx: g.ellipse([s(cx + sx * 80 - 40), s(540), s(cx + sx * 80 + 40), s(590)], fill=(240, 130, 140, 120)), 4)
d = ImageDraw.Draw(im)
# pelo castaño, remolinos y mechones locos
hair = (116, 74, 52)
d.rounded_rectangle([s(cx - 132), s(300), s(cx + 132), s(372)], s(40), fill=hair, outline=dark(hair, .7), width=s(4))
for ox, h, w in [(-104, 70, 34), (-62, 104, 36), (-18, 128, 38), (28, 118, 38), (72, 96, 34), (110, 66, 30), (0, 80, 28)]:
    d.polygon([(s(cx + ox - w), s(332)), (s(cx + ox + 10 + (ox // 40) * 6), s(300 - h)), (s(cx + ox + w), s(332))], fill=hair, outline=dark(hair, .7), width=s(3))
    d.line([s(cx + ox), s(330), s(cx + ox + 8), s(300 - h + 24)], fill=light(hair, 1.3), width=s(4))
d.arc([s(cx - 60), s(318), s(cx + 20), s(366)], 190, 350, fill=dark(hair, .6), width=s(4))
# gafas redondas enormes
frame = (38, 70, 96)
for dx in (-62, 62):
    d.ellipse([s(cx + dx - 76), s(394), s(cx + dx + 76), s(548)], fill=(248, 250, 252), outline=frame, width=s(11))
    # ojo: parpado pesado
    d.ellipse([s(cx + dx - 18), s(450), s(cx + dx + 20), s(488)], fill=(70, 48, 40))
    d.ellipse([s(cx + dx - 8), s(458), s(cx + dx + 4), s(470)], fill=(255, 255, 255))
    d.chord([s(cx + dx - 66), s(402), s(cx + dx + 66), s(540)], 180, 360, fill=skin)
    d.rectangle([s(cx + dx - 66), s(470), s(cx + dx + 66), s(476)], fill=skin)
    d.arc([s(cx + dx - 66), s(402), s(cx + dx + 66), s(540)], 190, 350, fill=dark(skin, .55), width=s(5))
    d.line([s(cx + dx - 60), s(470), s(cx + dx + 62), s(470)], fill=dark(skin, .55), width=s(5))
    # ojeras suaves
    ov(lambda g, dx=dx: g.ellipse([s(cx + dx - 52), s(512), s(cx + dx + 52), s(560)], fill=(150, 120, 190, 90)), 3)
    # reflejo de pantalla (mini marciano pixel) y brillo
    for px, py in [(-30, 0), (-18, 0), (-6, 0), (-24, 12), (-12, 12), (-30, 24), (-6, 24)]:
        d.rectangle([s(cx + dx + 22 + px * 0.6), s(500 + py * 0.6), s(cx + dx + 30 + px * 0.6), s(508 + py * 0.6)], fill=(120, 210, 240))
    d.arc([s(cx + dx - 58), s(412), s(cx + dx + 20), s(500)], 200, 270, fill=(255, 255, 255), width=s(6))
    if BLINK:
        d.ellipse([s(cx + dx - 66), s(436), s(cx + dx + 66), s(520)], fill=skin)
        d.arc([s(cx + dx - 60), s(450), s(cx + dx + 60), s(500)], 20, 160, fill=dark(skin, .5), width=s(6))
    # ceja preocupada
    d.line([s(cx + dx - 52 * (1 if dx > 0 else -1) * -1), s(412 - 10 * (1 if dx < 0 else 0)),
            s(cx + dx + 48 * (1 if dx > 0 else -1) * -1), s(404 + 14 * (1 if dx < 0 else 0))], fill=hair, width=s(9))
d.line([s(cx - 8), s(470), s(cx + 8), s(470)], fill=frame, width=s(10))
for sx in (-1, 1):                                      # patillas de las gafas
    d.line([s(cx + sx * 138), s(466), s(cx + sx * 150), s(470)], fill=frame, width=s(8))
# nariz grande con brillo
d.ellipse([s(cx - 22), s(536), s(cx + 22), s(584)], fill=(236, 190, 170), outline=dark(skin, .6), width=s(3))
d.ellipse([s(cx - 8), s(546), s(cx + 2), s(556)], fill=(255, 235, 225))
# boca segun variante
if MOUTH == "o":
    d.ellipse([s(cx - 22), s(600), s(cx + 22), s(634)], fill=(120, 50, 60), outline=dark((120, 50, 60), .6), width=s(3))
    d.ellipse([s(cx - 12), s(614), s(cx + 12), s(632)], fill=(224, 110, 120))
elif MOUTH == "small":
    d.ellipse([s(cx - 13), s(604), s(cx + 13), s(626)], fill=(120, 50, 60), outline=dark((120, 50, 60), .6), width=s(3))
else:
    d.arc([s(cx - 26), s(596), s(cx + 26), s(628)], 20, 160, fill=(150, 70, 80), width=s(6))
# manchitas de tiza en la bata? no; detalle: tirita en la nariz
d.rounded_rectangle([s(cx + 6), s(540), s(cx + 50), s(556)], s(6), fill=(255, 216, 170), outline=dark((255, 216, 170), .7), width=s(2))

# ---------- rótulos propios (pegatina con cinta + pizarra) ----------
def sticky(text, xy, rot, fill=(255, 226, 110), color=(120, 60, 40), size=56):
    f = font(size)
    bb = d.textbbox((0, 0), text, font=f)
    w, h = bb[2] - bb[0] + s(60), bb[3] - bb[1] + s(50)
    lay = Image.new("RGBA", (w + s(30), h + s(30)), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.rectangle([s(12), s(14), w + s(12), h + s(14)], fill=(0, 0, 0, 70))
    ld.rectangle([s(4), s(4), w + s(4), h + s(4)], fill=fill)
    ld.text((s(34) - bb[0], s(24) - bb[1]), text, font=f, fill=color)
    ld.rectangle([w // 2 - s(30), s(-4) + s(4), w // 2 + s(50), s(26)], fill=(255, 255, 255, 170))   # cinta
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(lay, (s(xy[0]), s(xy[1])))

if TAGS:
    sticky("DÍA 0", (70, 180), 4)
    sticky("SERGIO · 31 AÑOS", (140, 1205), -2, (250, 244, 232), (70, 90, 130), 44)
    # pizarra de tiza con el marcador
    shp("rr", (170, 1330, 910, 1510), (170, 120, 76), 6, r=16)
    d.rounded_rectangle([s(188), s(1348), s(892), s(1492)], s(10), fill=(40, 70, 62))
    d.text((s(230), s(1352)), "RADIO DE LIBERTAD", font=font(50), fill=(250, 250, 240))
    d.text((s(440), s(1396)), "0 m", font=font(62), fill=(255, 214, 120))
    for k in range(30):
        x, y = random.Random(k).randint(200, 880), random.Random(k + 50).randint(1360, 1470)
        d.point((s(x), s(y)), fill=(120, 150, 140))


# ---------- grano de película + viñeta ----------
g = Image.effect_noise((W, H), 18).convert("L")
grain = Image.merge("RGBA", (g, g, g, Image.new("L", (W, H), 22)))
im.alpha_composite(grain)
vig = Image.new("L", (W, H), 0)
ImageDraw.Draw(vig).ellipse([-W // 4, -H // 6, W + W // 4, H + H // 6], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(s(180)))
shade = Image.new("RGBA", (W, H), (30, 14, 24, 255))
shade.putalpha(vig.point(lambda v: int((255 - v) * 0.5)))
im.alpha_composite(shade)

out = im.convert("RGB").resize((1080, 1920), Image.LANCZOS)
out.save(OUT + ".jpg", quality=93)
im.convert("RGB").save(OUT + "_2x.png")
print("ok")
