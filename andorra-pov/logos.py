"""3 logos (foto de perfil 1080x1080, pensados para el recorte circular) para @500enandorra. Dibujados a 2x."""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "casa-pov"))
from art import font, F_ANTON, F_UI
S = 2160; K = 2; OUT = os.path.join(HERE, "out")
def P(v): return v * K
def layer(): return Image.new("RGBA", (S, S), (0, 0, 0, 0))
def blur(l, r): return l.filter(ImageFilter.GaussianBlur(r * K))

def fondo(top, bot, cy=.8):
    yy, xx = np.mgrid[0:S, 0:S]; d = np.clip(np.sqrt((xx - S / 2) ** 2 + (yy - S / 2 * cy) ** 2) / (S * .7), 0, 1)[..., None]
    arr = (np.array(top)[None, None] * (1 - d) + np.array(bot)[None, None] * d).astype(np.uint8)
    return Image.fromarray(np.dstack([arr, np.full((S, S), 255, np.uint8)]), "RGBA")

def estrellas(im, n=120, y1=520, seed=3):
    d = ImageDraw.Draw(im); rng = random.Random(seed)
    for _ in range(n):
        x, y = rng.uniform(100, 980), rng.uniform(100, y1); r = rng.choice((1.2, 1.8, 2.4))
        d.ellipse((P(x - r), P(y - r), P(x + r), P(y + r)), fill=(235, 240, 255, rng.randrange(120, 255)))

def cordillera(im, base, cols, seed=2):
    """Picos pirenaicos con casquetes de nieve."""
    d = ImageDraw.Draw(im); rng = random.Random(seed)
    for k, (col, nieve) in enumerate(cols):
        x, pts, peaks = -60, [(-60, 1080)], []
        while x < 1140:
            y = base - 260 + k * 110 + rng.uniform(-90, 90); pts.append((x, y)); peaks.append((x, y)); x += rng.uniform(150, 240)
        pts.append((1140, 1080)); d.polygon([(P(a), P(b)) for a, b in pts], fill=col)
        for (x0, y0), (x1, y1) in zip(peaks[:-1], peaks[1:]):
            tx, ty = (x0, y0) if y0 < y1 else (x1, y1); w = rng.uniform(60, 90)
            d.polygon([(P(tx), P(ty)), (P(tx + w), P(ty + w * .7)), (P(tx + w * .5), P(ty + w * .55)), (P(tx + w * .15), P(ty + w * .75)), (P(tx - w * .3), P(ty + w * .55)), (P(tx - w * .75), P(ty + w * .68))], fill=nieve)

def moneda(im, cx, cy, r, txt="500€"):
    g = layer(); ImageDraw.Draw(g).ellipse((P(cx - r * 1.35), P(cy - r * 1.35), P(cx + r * 1.35), P(cy + r * 1.35)), fill=(255, 200, 70, 150)); im.alpha_composite(blur(g, 40))
    d = ImageDraw.Draw(im)
    d.ellipse((P(cx - r), P(cy - r + 14), P(cx + r), P(cy + r + 14)), fill=(170, 110, 20))
    d.ellipse((P(cx - r), P(cy - r), P(cx + r), P(cy + r)), fill=(255, 196, 56))
    d.ellipse((P(cx - r * .84), P(cy - r * .84), P(cx + r * .84), P(cy + r * .84)), fill=(255, 214, 90), outline=(206, 140, 30), width=P(8))
    d.chord((P(cx - r * .8), P(cy - r * .8), P(cx + r * .8), P(cy + r * .8)), 200, 300, fill=(255, 236, 160))
    d.text((P(cx), P(cy + 4)), txt, font=font(F_ANTON, P(r * .78)), fill=(120, 70, 10), anchor="mm")

def rotulo(im, l1, l2, y=850, c2=(255, 206, 60)):
    d = ImageDraw.Draw(im)
    d.text((P(540), P(y)), l1, font=font(F_ANTON, P(86)), fill=(255, 255, 255), anchor="mm", stroke_width=P(5), stroke_fill=(8, 10, 28))
    d.text((P(540), P(y + 92)), l2, font=font(F_ANTON, P(64)), fill=c2, anchor="mm", stroke_width=P(4), stroke_fill=(8, 10, 28))

def guardar(im, nombre):
    im.resize((1080, 1080), Image.LANCZOS).convert("RGB").save(os.path.join(OUT, nombre))

# ---------------------------------------------------------------- 1: moneda de 500 € delante de los Pirineos nevados de noche
im = fondo((40, 54, 120), (6, 10, 30)); estrellas(im)
cordillera(im, 560, [((44, 58, 104), (170, 186, 225)), ((26, 34, 70), (130, 146, 190))])
d = ImageDraw.Draw(im); rng = random.Random(9)
for _ in range(120):   # luces del pueblo
    x, y = rng.uniform(150, 930), rng.uniform(700, 760); r = rng.uniform(2, 4); d.ellipse((P(x - r), P(y - r), P(x + r), P(y + r)), fill=(255, 210, 140))
moneda(im, 540, 420, 190)
rotulo(im, "500 € EN", "ANDORRA")
guardar(im, "logo1_500enandorra.png")

# ---------------------------------------------------------------- 2: botón de play en una montaña nevada (el sueño de ser creador)
im = fondo((90, 160, 240), (20, 60, 140), .6)
g = layer(); ImageDraw.Draw(g).ellipse((P(700), P(150), P(900), P(350)), fill=(255, 250, 220, 255)); im.alpha_composite(blur(g, 30))
cordillera(im, 640, [((150, 175, 215), (250, 252, 255)), ((110, 136, 186), (240, 246, 255))], seed=5)
d = ImageDraw.Draw(im); d.rectangle((0, P(760), S, S), fill=(240, 246, 255))
g = layer(); ImageDraw.Draw(g).rounded_rectangle((P(300), P(300), P(780), P(640)), P(90), fill=(0, 0, 0, 120)); im.alpha_composite(blur(g, 20))
d = ImageDraw.Draw(im)
d.rounded_rectangle((P(300), P(280), P(780), P(620)), P(90), fill=(20, 140, 255))
d.rounded_rectangle((P(300), P(280), P(780), P(330)), P(40), fill=(80, 180, 255))
d.polygon([(P(480), P(360)), (P(480), P(540)), (P(630), P(450))], fill=(255, 255, 255))
moneda(im, 760, 620, 105)
rotulo(im, "500 € EN", "ANDORRA", c2=(20, 120, 230))
guardar(im, "logo2_500enandorra.png")

# ---------------------------------------------------------------- 3: maleta con pegatina AND y nieve (el que llega con todo en una maleta)
im = fondo((255, 180, 90), (180, 60, 60), .7)
cordillera(im, 600, [((200, 90, 90), (255, 236, 220)), ((150, 60, 70), (255, 220, 200))], seed=8)
d = ImageDraw.Draw(im)
g = layer(); ImageDraw.Draw(g).rounded_rectangle((P(360), P(330), P(720), P(780)), P(50), fill=(0, 0, 0, 120)); im.alpha_composite(blur(g, 20)); d = ImageDraw.Draw(im)
d.rectangle((P(485), P(180), P(505), P(330)), fill=(170, 170, 180)); d.rectangle((P(575), P(180), P(595), P(330)), fill=(170, 170, 180)); d.rounded_rectangle((P(470), P(160), P(610), P(200)), P(16), fill=(40, 40, 50))
d.rounded_rectangle((P(360), P(320), P(720), P(770)), P(50), fill=(30, 60, 130)); d.rounded_rectangle((P(385), P(345), P(695), P(745)), P(38), fill=(44, 82, 160))
for x in (460, 540, 620): d.line((P(x), P(345), P(x), P(745)), fill=(30, 60, 130), width=P(10))
d.rounded_rectangle((P(410), P(420), P(570), P(510)), P(14), fill=(250, 220, 90)); d.text((P(490), P(466)), "AND", font=font(F_ANTON, P(60)), fill=(80, 50, 10), anchor="mm")
d.ellipse((P(560), P(560), P(680), P(680)), fill=(240, 60, 60)); d.text((P(620), P(620)), "▶", font=font(F_UI, P(54)), fill=(255, 255, 255), anchor="mm")
for x in (395, 685): d.ellipse((P(x - 22), P(760), P(x + 22), P(804)), fill=(20, 20, 26))
moneda(im, 300, 650, 85, "500€")
rotulo(im, "500 € EN", "ANDORRA", c2=(255, 236, 160))
guardar(im, "logo3_500enandorra.png")

prev = Image.new("RGB", (3 * 420, 420), (240, 240, 240)); mk = Image.new("L", (400, 400), 0); ImageDraw.Draw(mk).ellipse((0, 0, 400, 400), fill=255)
for i in range(3): prev.paste(Image.open(os.path.join(OUT, f"logo{i + 1}_500enandorra.png")).resize((400, 400), Image.LANCZOS), (i * 420 + 10, 10), mk)
prev.save("/tmp/logos_and.jpg")
