"""Story: subimos toda la serie de Mateo a la cuenta nueva + CTA seguir (estilo cuaderno)."""
from portada_cuaderno import *

def escena():
    s = bg("bg_cuarto", 0, 0, 1.2, 1.2, 1, .5, .5).convert("RGBA")
    put(s, "mateo_feliz", 400, 1000 + 400 * 1.0, 1.0); put(s, "dino", 800, 1560, .5)
    return s.crop((0, 560, 1080, 1640))

def corazon(d, x, y, r, col):
    d.ellipse((x - r, y - r * .9, x, y + r * .3), fill=col); d.ellipse((x, y - r * .9, x + r, y + r * .3), fill=col)
    d.polygon([(x - r, y - r * .2), (x + r, y - r * .2), (x, y + r * 1.05)], fill=col)

c = cuaderno(); garabatos(c, 33)
cx, cy, w = 540, 430, 500
foto(c, escena(), cx, cy, w, w, -2)
cinta(c, cx - 215, cy - 290, 170, 26, (150, 200, 240)); cinta(c, cx + 205, cy - 298, 170, -28, (250, 220, 90))
d = ImageDraw.Draw(c)
d.text((540, 830), "¿quieren que suba", font=font(F_HAND, 84), fill=NAVY, anchor="mm")
d.text((540, 920), "toda la serie aquí?", font=font(F_HAND, 84), fill=NAVY, anchor="mm")
cw_, ch_ = 200, 84; x0 = 540 - (4 * cw_ + 3 * 24) / 2
for i in range(8):
    r, k = divmod(i, 4); x = x0 + k * (cw_ + 24); y = 995 + r * 110
    ya = i >= 6
    d.rounded_rectangle((x, y, x + cw_, y + ch_), 20, fill=(255, 255, 255) if not ya else (222, 244, 226), outline=(58, 168, 72) if ya else (200, 186, 205), width=6)
    d.text((x + cw_ / 2 - (14 if ya else 0), y + ch_ / 2 + 2), f"PARTE {i + 1}", font=font(F_ESC, 34), fill=NAVY if ya else (170, 160, 185), anchor="mm")
    if ya: d.line([(x + cw_ - 40, y + 42), (x + cw_ - 30, y + 54), (x + cw_ - 12, y + 28)], fill=(58, 168, 72), width=7)
d.text((540, 1235), "la 7 y la 8 ya están · faltan la 1 a la 6", font=font(F_HAND, 46), fill=NAVY, anchor="mm")
d.text((540, 1335), "¡vota aquí abajo!", font=font(F_HAND, 64), fill=NAVY, anchor="mm")
for x, y, r, col in ((170, 1250, 28, (236, 92, 130)), (930, 1330, 26, (246, 190, 40))): corazon(d, x, y, r, col)
# flechas hacia el espacio del sticker de encuesta
for dx in (-150, 150):
    d.line([(540 + dx, 1395), (540 + dx, 1455)], fill=(222, 70, 90), width=8)
    d.polygon([(540 + dx - 22, 1447), (540 + dx + 22, 1447), (540 + dx, 1485)], fill=(222, 70, 90))
c = c.convert("RGB").filter(ImageFilter.UnsharpMask(1.0, 50, 2))
c.save("story_subimos_serie_9x16.jpg", quality=100, subsampling=0); print("ok")
