"""Portada del Día 1 (diseño nuevo de la temporada): pizarra verde, hoja de calendario DÍA N, cara de Mateo con emoción,
UN objeto enorme con el error en círculo rojo, título de 2 líneas en tiza (palabra clave en amarillo) e imanes M-A-T-E-O.
Todo dentro de la zona central 3:4 (x 90-990, y 300-1620): es lo que TikTok deja ver en la cuadrícula del perfil."""
import os
from render_d1 import *
def main():
    c = pizarra(); d = ImageDraw.Draw(c)
    d.rounded_rectangle((110, 340, 330, 590), 26, fill=CREMA, outline=OL, width=8)
    d.rounded_rectangle((110, 340, 330, 416), 26, fill=ROJO, outline=OL, width=8); d.rectangle((116, 390, 324, 416), fill=ROJO)
    d.text((220, 380), "DÍA", font=font(F_BAL, 54), fill=CREMA, anchor="mm"); d.text((220, 508), "1", font=font(F_ANTON, 150), fill=OL, anchor="mm")
    nb = nota_img(); z = .57; cx, cy, rot = 690, 660, 5
    sombra(c, (cx - 440 * z, cy - 560 * z, cx + 440 * z, cy + 560 * z), 24, 120, 18); paste_rot(c, nb, cx, cy, z, rot)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); x0, y0, x1, y1 = NOTA_REPITE
    lapiz_rojo(lay, (cx + x0 * z, cy + y0 * z, cx + x1 * z, cy + y1 * z), 1, 14)
    c.alpha_composite(lay.rotate(rot, center=(cx, cy), resample=Image.BICUBIC))
    mateo(c, "susto", 290, 905, .8, 0, blink=False)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    dl.rectangle((0, 1080, W, H), fill=PIZ2 + (255,)); dl.line((0, 1080, W, 1080), fill=(214, 190, 150, 255), width=8); c.alpha_composite(lay)
    tiza(c, "30 días para escribir", 540, 1175, 86, TIZA, 0, f=F_BAL)
    tiza(c, "su nombre… o REPITE", 540, 1290, 84, AMA, 0, f=F_BAL)
    imanes(ImageDraw.Draw(c), 540 - 2 * 126 * 1.12, 1470, 1.12, 0)
    c.convert("RGB").save(os.path.join(HERE, "portada_mateo_dia1_9x16.jpg"), quality=93)
main()
