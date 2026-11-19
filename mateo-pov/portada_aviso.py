"""Portada del aviso de cambio de cuenta (estilo cuaderno de la serie)."""
import sys
from portada_cuaderno import *

def escena():
    s = bg("bg_cuarto", 0, 0, 1.2, 1.2, 1, .5, .5).convert("RGBA")
    put(s, "mateo_feliz", 420, 1000 + 400 * 1.0, 1.0); put(s, "dino", 800, 1560, .5)
    return s.crop((0, 560, 1080, 1640))

c = cuaderno(); garabatos(c, 21)
cx, cy = 540, OY + 460
foto(c, escena(), cx, cy, 660, 660, 2)
cinta(c, cx - 275, cy - 372, 210, 26, (150, 200, 240)); cinta(c, cx + 265, cy - 385, 210, -28, (250, 220, 90))
d = ImageDraw.Draw(c)
d.text((540, OY + 900), "¡nos cambiamos de cuenta!", font=font(F_HAND, 92), fill=NAVY, anchor="mm")
f = font(F_ESC, 92); t = "@escribirconpinti"
for dx, dy, col in ((6, 7, (20, 70, 30)), (0, 0, (58, 168, 72))):
    d.text((540 + dx, OY + 1040 + dy), t, font=f, fill=col, anchor="mm", stroke_width=3, stroke_fill=col)
st = Image.new("RGBA", (640, 150), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
sd.rounded_rectangle((6, 6, 634, 144), 30, fill=(255, 255, 255), outline=(222, 70, 90), width=10); sd.rounded_rectangle((24, 22, 616, 128), 20, outline=(222, 70, 90), width=3)
sd.text((320, 76), "PARTES 7 y 8 YA ALLÁ", font=font(F_ESC, 52), fill=NAVY, anchor="mm")
st = st.rotate(-3, expand=True, resample=Image.BICUBIC); c.alpha_composite(st, (540 - st.width // 2, OY + 1180))
c = c.convert("RGB").filter(ImageFilter.UnsharpMask(1.0, 50, 2))
c.save(os.path.join(V.HERE, "portada_aviso_cuenta_9x16.jpg"), quality=100, subsampling=0)
c.crop((0, OY, CW, OY + 1440)).save(os.path.join(V.HERE, "portada_aviso_cuenta.jpg"), quality=95); print("ok")
