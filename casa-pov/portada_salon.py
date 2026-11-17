"""Portada Parte 1 (reforma): salón antes/después + PAGUÉ $1 (9:16, contenido en el 3:4 central)."""
from PIL import Image, ImageDraw
import salon as SL, ep1 as E, art as A
from art import font, F_ANTON
W, H = 1080, 1920
a = E.cam(SL.salon("vieja", "moqueta", True), 1.55, 1296, 2060); b = E.cam(SL.salon("vieja", "parquet_brillo", False), 1.55, 1296, 2060)
c = Image.new("RGBA", (W, H)); m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon([(0, 0), (W * .62, 0), (W * .38, H), (0, H)], fill=255)
c.paste(b, (0, 0)); c.paste(a, (0, 0), m)
d = ImageDraw.Draw(c); d.line([(W * .62, 0), (W * .38, H)], fill=(255, 255, 255), width=10)
g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
for y in range(240, 640): gd.line((0, y, W, y), fill=(6, 6, 14, int(max(0, 210 - (y - 240) * .5))))
for y in range(1150, 1720): gd.line((0, y, W, y), fill=(6, 6, 14, int(min(225, (y - 1150) * .55))))
c.alpha_composite(g); d = ImageDraw.Draw(c)
f1, f2 = font(F_ANTON, 120), font(F_ANTON, 160); w1 = d.textlength("PAGUÉ ", font=f1); w2 = d.textlength("$1", font=f2); x0 = W / 2 - (w1 + w2) / 2
d.text((x0, 400), "PAGUÉ ", font=f1, fill=(255, 255, 255), anchor="ls", stroke_width=12, stroke_fill=(14, 12, 24))
d.text((x0 + w1, 412), "$1", font=f2, fill=(255, 206, 60), anchor="ls", stroke_width=12, stroke_fill=(14, 12, 24))
for x, t, col in ((250, "ANTES", (230, 80, 70)), (830, "DESPUÉS", (90, 200, 110))):
    d.rounded_rectangle((x - 150, 560, x + 150, 640), 20, fill=col); d.text((x, 600), t, font=font(F_ANTON, 58), fill=(255, 255, 255), anchor="mm")
E.text(d, (W / 2, 1360), "DEBAJO DE LA", 104, (255, 255, 255), stroke=12)
E.text(d, (W / 2, 1480), "MOQUETA HABÍA…", 104, (255, 206, 60), stroke=12)
d.rounded_rectangle((W / 2 - 130, 1570, W / 2 + 130, 1640), 18, fill=(255, 170, 70)); d.text((W / 2, 1605), "PARTE 1", font=font(F_ANTON, 54), fill=(14, 12, 24), anchor="mm")
c.convert("RGB").save("out/portada_salon_parte1_9x16.jpg", quality=93); c.convert("RGB").resize((360, 640)).save("/tmp/ps.jpg")
