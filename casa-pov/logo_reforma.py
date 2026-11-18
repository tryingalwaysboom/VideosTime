"""Foto de perfil (reforma): casa partida mitad vieja / mitad reformada, puerta $1, rodillo de pintura."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art import font, F_ANTON
S = 2160; K = 2; C = S // 2
def P(v): return v * K
yy, xx = np.mgrid[0:S, 0:S]; d0 = np.sqrt((xx - C) ** 2 + (yy - C * .9) ** 2) / (S * .72)
a = np.array([255, 196, 110]); b = np.array([236, 120, 60]); t = np.clip(d0, 0, 1)[..., None]
im = Image.fromarray(np.dstack([(a * (1 - t) + b * t).astype(np.uint8), np.full((S, S), 255, np.uint8)]), "RGBA")
def layer(): return Image.new("RGBA", (S, S), (0, 0, 0, 0))
g = layer(); ImageDraw.Draw(g).ellipse((P(150), P(820), P(930), P(1000)), fill=(120, 60, 20, 90)); im.alpha_composite(g.filter(ImageFilter.GaussianBlur(P(14))))
# casa: cuerpo + tejado, mitad izquierda vieja, mitad derecha reformada
body = [(270, 520), (810, 520), (810, 880), (270, 880)]; roof = [(215, 540), (540, 270), (865, 540)]
old, new = layer(), layer()
for lay, wall, rf, tr in ((old, (128, 118, 110), (82, 70, 66), (96, 86, 80)), (new, (255, 246, 228), (200, 70, 60), (240, 230, 214))):
    d = ImageDraw.Draw(lay)
    d.rectangle((P(640), P(330), P(700), P(470)), fill=rf)
    d.polygon([(P(x), P(y)) for x, y in body], fill=wall); d.polygon([(P(x), P(y)) for x, y in roof], fill=rf)
    d.line([(P(215), P(540)), (P(540), P(270)), (P(865), P(540))], fill=tr, width=P(18), joint="curve")
    for wx in (330, 640):
        d.rectangle((P(wx), P(600), P(wx + 110), P(700)), fill=(150, 200, 230) if lay is new else (60, 56, 60))
        d.line((P(wx + 55), P(600), P(wx + 55), P(700)), fill=tr, width=P(8)); d.line((P(wx), P(650), P(wx + 110), P(650)), fill=tr, width=P(8))
    if lay is old:
        d.line((P(320), P(615), P(450), P(690)), fill=(150, 110, 70), width=P(14)); d.line((P(320), P(690), P(450), P(615)), fill=(150, 110, 70), width=P(14))
        for x, y in ((300, 760), (380, 560), (460, 820)): d.line((P(x), P(y), P(x + 30), P(y + 40)), fill=(90, 80, 74), width=P(5))
    else:
        for x in range(660, 760, 30): d.ellipse((P(x), P(860), P(x + 26), P(886)), fill=(90, 170, 90))
m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).rectangle((0, 0, C, S), fill=255)
house = new.copy(); house.paste(old, (0, 0), m)
im.alpha_composite(house); d = ImageDraw.Draw(im)
d.line((P(540), P(250), P(540), P(900)), fill=(255, 255, 255), width=P(6))
# puerta = placa $1
d.rounded_rectangle((P(470), P(720), P(610), P(880)), P(14), fill=(255, 206, 60), outline=(150, 96, 20), width=P(5))
d.text((P(540), P(800)), "$1", font=font(F_ANTON, P(96)), fill=(30, 22, 40), anchor="mm")
# rodillo de pintura pintando la mitad nueva
d.line((P(880), P(470), P(940), P(560)), fill=(60, 60, 70), width=P(10)); d.line((P(940), P(560), P(940), P(700)), fill=(60, 60, 70), width=P(10))
d.rounded_rectangle((P(925), P(690), P(955), P(800)), P(10), fill=(40, 40, 46))
d.rounded_rectangle((P(800), P(430), P(900), P(480)), P(20), fill=(255, 246, 228), outline=(200, 190, 170), width=P(4))
# rótulo
d.text((P(540), P(960)), "LA CASA DE 1 DÓLAR", font=font(F_ANTON, P(70)), fill=(255, 255, 255), anchor="mm", stroke_width=P(5), stroke_fill=(120, 50, 20))
im.resize((1080, 1080), Image.LANCZOS).convert("RGB").save("out/logo_reforma_lacasade1dolar.png")
p = Image.new("RGB", (420, 420), (240, 240, 240)); mk = Image.new("L", (400, 400), 0); ImageDraw.Draw(mk).ellipse((0, 0, 400, 400), fill=255)
p.paste(im.resize((400, 400), Image.LANCZOS).convert("RGB"), (10, 10), mk); p.save("/tmp/logo_r.jpg")
