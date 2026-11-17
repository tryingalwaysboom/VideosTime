"""Logo pulido para @lacasade1dolar (dibujado a 2x y reducido)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art import font, F_ANTON
S2 = 2160; K = 2; C = S2 // 2
def P(v): return v * K

def layer(): return Image.new("RGBA", (S2, S2), (0, 0, 0, 0))
def blur(l, r): return l.filter(ImageFilter.GaussianBlur(r * K))

# fondo: degradado radial noche
yy, xx = np.mgrid[0:S2, 0:S2]
d = np.sqrt((xx - C) ** 2 + (yy - C * .8) ** 2) / (S2 * .7)
top = np.array([44, 36, 92]); bot = np.array([8, 8, 24])
arr = (top[None, None] * (1 - np.clip(d, 0, 1))[..., None] + bot[None, None] * np.clip(d, 0, 1)[..., None]).astype(np.uint8)
im = Image.fromarray(np.dstack([arr, np.full((S2, S2), 255, np.uint8)]), "RGBA")
dr = ImageDraw.Draw(im); rng = random.Random(3)
for _ in range(140):
    x, y = rng.uniform(80, 1000), rng.uniform(80, 560); r = rng.choice((1.2, 1.6, 2.2, 3))
    dr.ellipse((P(x - r), P(y - r), P(x + r), P(y + r)), fill=(235, 238, 255, rng.randrange(120, 255)))
for x, y in ((250, 230), (860, 560), (170, 470)):   # estrellas brillantes
    for a in (0, 90):
        r = math.radians(a); dr.line((P(x - 14 * math.cos(r)), P(y - 14 * math.sin(r)), P(x + 14 * math.cos(r)), P(y + 14 * math.sin(r))), fill=(255, 255, 255, 220), width=P(2))
# luna con halo
g = layer(); ImageDraw.Draw(g).ellipse((P(600), P(110), P(940), P(450)), fill=(190, 200, 255, 110)); im.alpha_composite(blur(g, 50))
dr = ImageDraw.Draw(im); mx, my, mr = 770, 280, 92
dr.ellipse((P(mx - mr), P(my - mr), P(mx + mr), P(my + mr)), fill=(246, 244, 230))
for cx, cy, r in ((-30, -24, 20), (28, 18, 14), (-6, 44, 10), (40, -40, 8)):
    dr.ellipse((P(mx + cx - r), P(my + cy - r), P(mx + cx + r), P(my + cy + r)), fill=(224, 222, 208))
# nube delante de la luna
g = layer(); gd = ImageDraw.Draw(g)
for cx, cy, rw, rh in ((700, 360, 150, 34), (820, 380, 120, 28)): gd.ellipse((P(cx - rw), P(cy - rh), P(cx + rw), P(cy + rh)), fill=(24, 22, 56, 230))
im.alpha_composite(blur(g, 6))
# colina
dr = ImageDraw.Draw(im)
dr.ellipse((P(-200), P(800), P(1280), P(1400)), fill=(14, 14, 32))
# casa: silueta con detalles
H_ = (14, 13, 30); OR = (255, 166, 60)
body = [(300, 560), (780, 560), (780, 878), (300, 878)]
roof = [(240, 580), (540, 330), (840, 580)]
dr.rectangle((P(650), P(360), P(710), P(500)), fill=H_); dr.rectangle((P(640), P(350), P(720), P(372)), fill=H_)
g = layer(); gd = ImageDraw.Draw(g)   # humo de la chimenea
for i in range(6): r = 18 + i * 8; gd.ellipse((P(690 + i * 22 - r), P(330 - i * 34 - r), P(690 + i * 22 + r), P(330 - i * 34 + r)), fill=(170, 170, 200, 60 - i * 8))
im.alpha_composite(blur(g, 8)); dr = ImageDraw.Draw(im)
dr.polygon([(P(x), P(y)) for x, y in body], fill=H_)
dr.polygon([(P(x), P(y)) for x, y in roof], fill=H_)
# ventanas iluminadas (con halo)
wins = [(400, 640, 470, 720), (610, 640, 680, 720)]
g = layer(); gd = ImageDraw.Draw(g)
for b in wins: gd.rectangle(tuple(P(v) for v in (b[0] - 30, b[1] - 30, b[2] + 30, b[3] + 30)), fill=(255, 170, 70, 120))
gd.ellipse((P(480), P(400), P(600), P(520)), fill=(255, 170, 70, 160)); im.alpha_composite(blur(g, 26))
dr = ImageDraw.Draw(im)
for i, b in enumerate(wins):
    dr.rectangle(tuple(P(v) for v in b), fill=(255, 196, 104) if i == 0 else (60, 50, 70))
    cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    dr.line((P(cx), P(b[1]), P(cx), P(b[3])), fill=H_, width=P(6)); dr.line((P(b[0]), P(cy), P(b[2]), P(cy)), fill=H_, width=P(6))
    if i == 1:   # ventana tapiada con tablas
        dr.line((P(b[0] - 8), P(b[1] + 18), P(b[2] + 8), P(b[1] + 34)), fill=(120, 84, 50), width=P(10)); dr.line((P(b[0] - 8), P(b[3] - 26), P(b[2] + 8), P(b[3] - 40)), fill=(120, 84, 50), width=P(10))
dr.ellipse((P(500), P(420), P(580), P(500)), fill=(255, 210, 120)); dr.line((P(500), P(460), P(580), P(460)), fill=H_, width=P(6)); dr.line((P(540), P(420), P(540), P(500)), fill=H_, width=P(6))
dr.ellipse((P(526), P(436), P(554), P(470)), fill=(30, 20, 26))   # silueta en el desván
# contorno del tejado en neón
g = layer(); ImageDraw.Draw(g).line([(P(x), P(y)) for x, y in roof], fill=OR + (255,), width=P(26), joint="curve"); im.alpha_composite(blur(g, 14))
dr = ImageDraw.Draw(im); dr.line([(P(x), P(y)) for x, y in roof], fill=(255, 214, 140), width=P(12), joint="curve")
# puerta = placa dorada con $1
g = layer(); ImageDraw.Draw(g).rounded_rectangle((P(455), P(710), P(625), P(852)), P(14), fill=(255, 190, 60, 160)); im.alpha_composite(blur(g, 18))
gold = layer(); gdr = ImageDraw.Draw(gold)
gdr.rounded_rectangle((P(462), P(716), P(618), P(846)), P(12), fill=(255, 200, 64))
for k in range(30): gdr.line((P(462), P(716 + k * 4.2), P(618), P(716 + k * 4.2)), fill=(255, int(214 - k * 2.2), int(90 - k * 1.6)), width=P(5))
gdr.polygon([(P(470), P(722)), (P(530), P(722)), (P(486), P(840)), (P(470), P(840))], fill=(255, 245, 200, 90))   # brillo
m = layer(); ImageDraw.Draw(m).rounded_rectangle((P(462), P(716), P(618), P(846)), P(12), fill=(0, 0, 0, 255))
gold.putalpha(Image.fromarray(np.minimum(np.asarray(gold.split()[3]), np.asarray(m.split()[3]))))
im.alpha_composite(gold); dr = ImageDraw.Draw(im)
dr.rounded_rectangle((P(462), P(716), P(618), P(846)), P(12), outline=(150, 96, 20), width=P(4))
dr.text((P(540), P(783)), "$1", font=font(F_ANTON, P(108)), fill=(26, 20, 40), anchor="mm")
# niebla y suelo
g = layer(); gd = ImageDraw.Draw(g); gd.rectangle((0, P(850), S2, P(905)), fill=(150, 160, 220, 60)); im.alpha_composite(blur(g, 20))
dr = ImageDraw.Draw(im)
for x in [x for x in range(110, 980, 12) if not 450 < x < 630]:   # hierba
    h = 14 + 10 * abs(math.sin(x * .7)); dr.line((P(x), P(882), P(x + 4), P(882 - h)), fill=(24, 30, 50), width=P(3))
dr.rectangle((P(140), P(876), P(940), P(884)), fill=OR)
# rótulo
dr.text((P(540), P(950)), "LA CASA DE 1 DÓLAR", font=font(F_ANTON, P(70)), fill=(255, 255, 255), anchor="mm", stroke_width=P(4), stroke_fill=(10, 8, 24))
im.resize((1080, 1080), Image.LANCZOS).convert("RGB").save("out/logo_lacasade1dolar.png")
p = Image.new("RGB", (420, 420), (240, 240, 240)); mk = Image.new("L", (400, 400), 0); ImageDraw.Draw(mk).ellipse((0, 0, 400, 400), fill=255)
p.paste(im.resize((400, 400), Image.LANCZOS).convert("RGB"), (10, 10), mk); p.save("/tmp/logo_pro.jpg")
