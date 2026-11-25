"""Portada del Día 2 — plantilla nueva de la temporada (opción D):
número del día GIGANTE a la izquierda, UN objeto grande con el error en círculo rojo a la derecha, Mateo asomado bajo el número,
título de 2 líneas y M-A-T-E-O sobre una franja del COLOR DEL DÍA (rota cada día para que ninguna portada se parezca a la anterior).
Todo dentro de la zona central 3:4 (x 90-990, y 300-1620): es lo que TikTok deja ver en la cuadrícula del perfil."""
import os, sys
from render_d2 import *
COLORES = [(226, 72, 59), (126, 87, 194), (52, 110, 200), (238, 124, 40), (40, 150, 140), (214, 72, 140)]   # día 1, 2, 3… (se repite)
def hoja_error(c, cx, cy, w, rot):
    h = int(w * .8); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); im = hoja_img().resize((w, h), Image.LANCZOS)
    lay.alpha_composite(im, (cx - w // 2, cy - h // 2)); ImageDraw.Draw(lay).rectangle((cx - w // 2, cy - h // 2, cx + w // 2 - 1, cy + h // 2 - 1), outline=OL + (255,), width=7)
    s = int(h * .86); t = Image.new("RGBA", (s, s), (0, 0, 0, 0)); ImageDraw.Draw(t).text((s / 2, s / 2), "M", font=font(F_AND, s * .78), fill=VERDE + (255,), anchor="mm")
    t = t.rotate(184, resample=Image.BICUBIC); lay.alpha_composite(t, (cx - s // 2, cy - s // 2 + int(h * .03)))
    lapiz_rojo(lay, (cx - w * .4, cy - h * .42, cx + w * .4, cy + h * .44), 1, 16)
    sombra(c, (cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2), 10, 120, 18); c.alpha_composite(lay.rotate(rot, center=(cx, cy), resample=Image.BICUBIC))
def base(dia, objeto, emocion, l1, l2):
    col = COLORES[(dia - 1) % len(COLORES)]; c = pizarra(); c.alpha_composite(Image.new("RGBA", (W, H), col + (120,))); objeto(c)
    d = ImageDraw.Draw(c); d.text((235, 372), "DÍA", font=font(F_BAL, 104), fill=CREMA, anchor="mm", stroke_width=8, stroke_fill=OL)
    d.text((235, 640), str(dia), font=font(F_ANTON, 470 if dia < 10 else 330), fill=AMA, anchor="mm", stroke_width=13, stroke_fill=OL)
    mateo(c, emocion, 300, 1002, .6, 0, blink=False)
    d = ImageDraw.Draw(c); d.rectangle((0, 1130, W, H), fill=col); d.line((0, 1130, W, 1130), fill=OL, width=9)
    d.text((540, 1225), l1, font=font(F_BAL, 80), fill=CREMA, anchor="mm", stroke_width=7, stroke_fill=OL)
    d.text((540, 1343), l2, font=font(F_BAL, 92), fill=AMA, anchor="mm", stroke_width=8, stroke_fill=OL)
    for i, ch in enumerate("MATEO"):
        x = 540 + (i - 2) * 141; r = 60
        d.rounded_rectangle((x - r, 1490 - r, x + r, 1490 + r), 20, fill=CREMA, outline=OL, width=7); d.text((x, 1492), ch, font=font(F_BAL, 88), fill=OL, anchor="mm")
    return c
if __name__ == "__main__":
    base(2, lambda c: hoja_error(c, 650, 660, 640, -3), "susto", "Escribió su primera M…", "¡y le salió AL REVÉS!").convert("RGB").save(os.path.join(HERE, "portada_mateo_dia2_9x16.jpg"), quality=93)
