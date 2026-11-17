"""Portada 9:16 de la Parte 1 (contenido en el 3:4 central, un poco subido)."""
import math
from PIL import Image, ImageDraw, ImageFilter
import art as A
import ep1 as E
c = E.cam(A.plate_casa(), 1.32, 610, 1180)
ax, ay = A.attic_xy(); fx, fy = E.to_frame(ax, ay, 1.32, 610, 1180); r = 52 * 1080 / (A.PW / 1.32)
c.alpha_composite(A.soft((1080, 1920), lambda dd: dd.ellipse((fx - r * 4, fy - r * 4, fx + r * 4, fy + r * 4), fill=(255, 180, 80, 130)), 40))
d = ImageDraw.Draw(c); d.ellipse((fx - r * .85, fy - r * .85, fx + r * .85, fy + r * .85), fill=(255, 205, 120))
d.line((fx - r * .9, fy, fx + r * .9, fy), fill=(30, 30, 42), width=6); d.line((fx, fy - r * .9, fx, fy + r * .9), fill=(30, 30, 42), width=6)
d.ellipse((fx - r * .25, fy - r * .55, fx + r * .25, fy + r * .05), fill=(20, 14, 18))
c.alpha_composite(A.vignette(1080, 1920, 230))
g = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
for y in range(1050, 1920): gd.line((0, y, 1080, y), fill=(4, 4, 12, int(min(235, (y - 1050) * .45))))
c.alpha_composite(g)
E.paste_c(c, A.billete(1.0, -12), 800, 1080, s=.75)
d = ImageDraw.Draw(c)
E.text(d, (540, 1250), "COMPRÉ ESTA CASA", 118, (255, 255, 255), stroke=12)
E.text(d, (540, 1395), "POR $1", 190, (255, 206, 60), stroke=14)
d.rounded_rectangle((540 - 190, 1520, 540 + 190, 1620), 22, fill=(255, 170, 70))
d.text((540, 1570), "PARTE 1", font=A.font(A.F_ANTON, 78), fill=(14, 12, 24), anchor="mm")
c.convert("RGB").save("out/portada_casa_parte1_9x16.jpg", quality=93)
