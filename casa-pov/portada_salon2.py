"""Portada Parte 2: caja fuerte detrás del papel + PAGUÉ $1 + ¿QUÉ HAY DENTRO?"""
from PIL import Image, ImageDraw, ImageFilter
import salon2 as S2, ep1 as E, art as A
from art import font, F_ANTON
W, H = 1080, 1920
c = S2.pared_cerca(0, rasgado=.58); c = c.resize((int(W * 1.1), int(H * 1.1))).crop((54, 40, 54 + W, 40 + H))
c.alpha_composite(A.soft((W, H), lambda d: d.ellipse((150, 520, 930, 1260), fill=(255, 220, 140, 70)), 60))
g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
for y in range(240, 560): gd.line((0, y, W, y), fill=(6, 6, 14, int(max(0, 210 - (y - 240) * .6))))
for y in range(1180, 1720): gd.line((0, y, W, y), fill=(6, 6, 14, int(min(225, (y - 1180) * .55))))
c.alpha_composite(g); d = ImageDraw.Draw(c)
f1, f2 = font(F_ANTON, 120), font(F_ANTON, 160); w1 = d.textlength("PAGUÉ ", font=f1); w2 = d.textlength("$1", font=f2); x0 = W / 2 - (w1 + w2) / 2
d.text((x0, 400), "PAGUÉ ", font=f1, fill=(255, 255, 255), anchor="ls", stroke_width=12, stroke_fill=(14, 12, 24))
d.text((x0 + w1, 412), "$1", font=f2, fill=(255, 206, 60), anchor="ls", stroke_width=12, stroke_fill=(14, 12, 24))
E.text(d, (W / 2, 1370), "¿QUÉ HAY", 120, (255, 255, 255), stroke=12); E.text(d, (W / 2, 1500), "DENTRO?", 130, (255, 206, 60), stroke=12)
d.rounded_rectangle((W / 2 - 130, 1580, W / 2 + 130, 1650), 18, fill=(255, 170, 70)); d.text((W / 2, 1615), "PARTE 2", font=font(F_ANTON, 54), fill=(14, 12, 24), anchor="mm")
c.convert("RGB").save("out/portada_salon_parte2_9x16.jpg", quality=93); c.convert("RGB").resize((360, 640)).save("/tmp/p2.jpg")
