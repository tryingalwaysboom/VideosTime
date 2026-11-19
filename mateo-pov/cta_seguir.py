"""Imagen CTA de la serie Mateo: ayúdanos a llegar a 10.000 seguidores (estilo cuaderno)."""
import os
from portada_cuaderno import *

def escena():
    s = bg("bg_cuarto", 0, 0, 1.2, 1.2, 1, .5, .5).convert("RGBA")
    put(s, "mateo_feliz", 400, 1000 + 400 * 1.0, 1.0); put(s, "dino", 800, 1560, .5)
    return s.crop((0, 560, 1080, 1640))

def corazon(d, x, y, r, col):
    d.ellipse((x - r, y - r * .9, x, y + r * .3), fill=col); d.ellipse((x, y - r * .9, x + r, y + r * .3), fill=col)
    d.polygon([(x - r, y - r * .2), (x + r, y - r * .2), (x, y + r * 1.05)], fill=col)

c = cuaderno(); garabatos(c, 21)
cx, cy, w = 540, 470, 600
foto(c, escena(), cx, cy, w, w, 2)
cinta(c, cx - 255, cy - 345, 190, 26, (244, 196, 48)); cinta(c, cx + 245, cy - 355, 190, -28, (240, 150, 190))
d = ImageDraw.Draw(c)
d.text((540, 900), "ayúdanos a llegar a", font=font(F_HAND, 100), fill=NAVY, anchor="mm")
f = font(F_ESC, 225); tx = "10.000"
for dx, dy, col in ((7, 9, (20, 70, 30)), (0, 0, (58, 168, 72))):
    d.text((560 + dx, 1070 + dy), tx, font=f, fill=col, anchor="mm", stroke_width=14 if col != (20, 70, 30) else 14, stroke_fill=col)
fh = font(F_HAND, 130)
d.text((545, 1262), "seguidores", font=fh, fill=(20, 70, 30), anchor="mm", stroke_width=3, stroke_fill=(20, 70, 30))
d.text((540, 1256), "seguidores", font=fh, fill=(58, 168, 72), anchor="mm", stroke_width=3, stroke_fill=(58, 168, 72))
# sello SÍGUENOS
st = Image.new("RGBA", (640, 170), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
sd.rounded_rectangle((6, 6, 634, 164), 30, fill=(255, 255, 255), outline=(222, 70, 90), width=10); sd.rounded_rectangle((24, 24, 616, 146), 20, outline=(222, 70, 90), width=3)
sd.text((320, 88), "SÍGUENOS", font=font(F_ESC, 100), fill=NAVY, anchor="mm")
st = st.rotate(-3, expand=True, resample=Image.BICUBIC); c.alpha_composite(st, (540 - st.width // 2, 1340))
d = ImageDraw.Draw(c)
d.text((540, 1580), "porfa, nos ayuda un montón", font=font(F_HAND, 66), fill=NAVY, anchor="mm")
d.text((540, 1650), "a seguir con la serie", font=font(F_HAND, 66), fill=NAVY, anchor="mm")
for x, y, r, col in ((190, 1500, 30, (236, 92, 130)), (920, 1420, 26, (246, 190, 40)), (900, 1700, 28, (110, 170, 255))): corazon(d, x, y, r, col)
c = c.convert("RGB").filter(ImageFilter.UnsharpMask(1.0, 50, 2))
c.save("cta_seguir_10000_9x16.jpg", quality=100, subsampling=0); print("ok")
