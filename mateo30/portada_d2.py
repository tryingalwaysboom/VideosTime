"""Portada del Día 2 (misma plantilla de la temporada): pizarra verde, hoja de calendario DÍA N, cara de Mateo con emoción,
UN objeto enorme con el error en círculo rojo, título de 2 líneas en tiza y las letras M-A-T-E-O.
Todo dentro de la zona central 3:4 (x 90-990, y 300-1620): es lo que TikTok deja ver en la cuadrícula del perfil."""
import os
from render_d2 import *
def main():
    c = pizarra(); d = ImageDraw.Draw(c)
    d.rounded_rectangle((110, 340, 330, 590), 26, fill=CREMA, outline=OL, width=8)
    d.rounded_rectangle((110, 340, 330, 416), 26, fill=ROJO, outline=OL, width=8); d.rectangle((116, 390, 324, 416), fill=ROJO)
    d.text((220, 380), "DÍA", font=font(F_BAL, 54), fill=CREMA, anchor="mm"); d.text((220, 508), "2", font=font(F_ANTON, 150), fill=OL, anchor="mm")
    cx, cy, rot = 690, 660, 5; lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); h = hoja_img().resize((620, 520), Image.LANCZOS)
    lay.alpha_composite(h, (cx - 310, cy - 260)); ImageDraw.Draw(lay).rectangle((cx - 310, cy - 260, cx + 309, cy + 259), outline=OL + (255,), width=7)
    t = Image.new("RGBA", (460, 460), (0, 0, 0, 0)); ImageDraw.Draw(t).text((230, 230), "M", font=font(F_AND, 360), fill=VERDE + (255,), anchor="mm")
    t = t.rotate(184, resample=Image.BICUBIC); lay.alpha_composite(t, (cx - 230, cy - 240)); lapiz_rojo(lay, (cx - 250, cy - 215, cx + 250, cy + 225), 1, 16)
    sombra(c, (cx - 310, cy - 260, cx + 310, cy + 260), 10, 120, 18); c.alpha_composite(lay.rotate(rot, center=(cx, cy), resample=Image.BICUBIC))
    mateo(c, "susto", 290, 905, .8, 0, blink=False)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    dl.rectangle((0, 1080, W, H), fill=PIZ2 + (255,)); dl.line((0, 1080, W, 1080), fill=(214, 190, 150, 255), width=8); c.alpha_composite(lay)
    tiza(c, "Escribió su primera M…", 540, 1175, 80, TIZA, 0, f=F_BAL)
    tiza(c, "¡y le salió AL REVÉS!", 540, 1290, 88, AMA, 0, f=F_BAL)
    d = ImageDraw.Draw(c)
    for i, ch in enumerate("MATEO"):
        x = 540 + (i - 2) * 141; r = 60
        d.rounded_rectangle((x - r, 1470 - r, x + r, 1470 + r), 20, fill=(58, 92, 80), outline=OL, width=7); d.text((x, 1472), ch, font=font(F_BAL, 88), fill=(196, 208, 202), anchor="mm")
    c.convert("RGB").save(os.path.join(HERE, "portada_mateo_dia2_9x16.jpg"), quality=93)
main()
