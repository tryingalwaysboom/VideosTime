"""Portada Parte 1 (9:16, 1080x1920; lo importante dentro del 3:4 central y algo subido para la cuadrícula del perfil)."""
import sys
from PIL import Image, ImageDraw, ImageFilter
import parte1 as E
import arte as R
from art import W, H, PW, font, F_ANTON
c = E.cam(R.calle(), 1.55, PW / 2, 1180)
back = c.filter(ImageFilter.GaussianBlur(5)); c = back
E.nevada(c, 2.0, 200)
car = R.coche_deportivo(); E.paste_c(c, car, 540, 930, .55)                     # deportivo alejándose calle abajo
R.glow(c, [(540, 1250, 330)], (255, 190, 100, 70), 60)
E.paste_c(c, E.maleta_im(), 700, 1330, 1.05)                                      # la maleta, nítida y con luz cálida
E.M.poner(c, "puno", 740, 1450, "d", 1.05, -6, 1.0)
c.alpha_composite(R.A.vignette(W, H, 200))
g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
for y in range(0, 700): gd.line((0, y, W, y), fill=(4, 6, 20, int(max(0, 200 - y * .3))))
c.alpha_composite(g)
d = ImageDraw.Draw(c)
E.text(d, (540, 430), "LLEGUÉ A ANDORRA", 104, (255, 255, 255), stroke=12)
E.text(d, (540, 580), "CON 500 €", 190, (255, 206, 60), stroke=14)
d.rounded_rectangle((540 - 190, 700, 540 + 190, 800), 22, fill=(120, 200, 255))
d.text((540, 750), "PARTE 1", font=font(F_ANTON, 78), fill=(14, 12, 24), anchor="mm")
c.convert("RGB").save("out/portada_pobre_andorra_parte1_9x16.jpg", quality=93)
