"""Portada del Día 1 (diseño nuevo de la temporada): pizarra verde, hoja de calendario DÍA N, cara de Mateo con emoción,
UN objeto enorme con el error en círculo rojo, título de 2 líneas en tiza (palabra clave en amarillo) e imanes M-A-T-E-O."""
import os
import render_d1 as V
from render_d1 import *
def main():
    c = pizarra(); d = ImageDraw.Draw(c)
    # hoja de calendario DÍA 1
    d.rounded_rectangle((60, 170, 300, 440), 26, fill=CREMA, outline=OL, width=8)
    d.rounded_rectangle((60, 170, 300, 250), 26, fill=ROJO, outline=OL, width=8); d.rectangle((66, 220, 294, 250), fill=ROJO)
    d.text((180, 212), "DÍA", font=font(F_BAL, 58), fill=CREMA, anchor="mm"); d.text((180, 350), "1", font=font(F_ANTON, 170), fill=OL, anchor="mm")
    tiza(c, "de 30", 180, 490, 70, TIZA, -3)
    # objeto enorme: la nota con REPITE en círculo rojo
    nb = nota_img(); z = .68; cx, cy, rot = 700, 590, 5
    sombra(c, (cx - 440 * z, cy - 560 * z, cx + 440 * z, cy + 560 * z), 24, 120, 20); paste_rot(c, nb, cx, cy, z, rot)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); x0, y0, x1, y1 = NOTA_REPITE
    lapiz_rojo(lay, (cx + x0 * z, cy + y0 * z, cx + x1 * z, cy + y1 * z), 1, 16)
    c.alpha_composite(lay.rotate(rot, center=(cx, cy), resample=Image.BICUBIC))
    # Mateo, cara y pecho, con susto
    mateo(c, "susto", 285, 1030, .98, 0, blink=False)
    # título en tiza
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    dl.rectangle((0, 1262, W, H), fill=PIZ2 + (255,)); dl.line((0, 1262, W, 1262), fill=(214, 190, 150, 255), width=8); c.alpha_composite(lay)
    tiza(c, "30 días para escribir", 540, 1360, 100, TIZA, 0, f=F_BAL)
    tiza(c, "su nombre… o REPITE", 540, 1484, 96, AMA, 0, f=F_BAL)
    imanes(ImageDraw.Draw(c), 540 - 2 * 126 * 1.25, 1700, 1.25, 0)
    c.convert("RGB").save(os.path.join(HERE, "portada_mateo_dia1_9x16.jpg"), quality=93)
main()
