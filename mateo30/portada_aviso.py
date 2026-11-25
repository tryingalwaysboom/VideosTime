"""Portada del vídeo de aviso para la cuenta vieja — distinta de la del Día 1: cocina cálida (no pizarra), Mateo orgulloso
enseñando su "nombre" (una raya rodeada en rojo) con Rex, título gracioso y sello SERIE NUEVA + @escribirconpinti.
Todo dentro de la zona 3:4 (x 90-990, y 300-1620)."""
import os
from render_d1 import *
DINO = Image.open(os.path.join(HERE, "..", "mateo-pov", "layers", "dino.png")).convert("RGBA")
def main():
    c = bg("bg_cocina", 0, 0, 1.3, 1.3, 1, .5, .45)
    oscurecer(c, (255, 236, 200), 40)
    mateo(c, "feliz", 540, 640, 1.05, 0, blink=False)
    cy = 1030; lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    paste_rot(lay, hoja_img(), 540, cy, .66, 0); crayon(lay, raya_pts(320, 760, cy - 6, 11, 3), 15)
    lapiz_rojo(lay, (280, cy - 70, 800, cy + 70), 1, 12, 4)
    c.alpha_composite(lay.rotate(-5, center=(540, cy), resample=Image.BICUBIC))
    d = ImageDraw.Draw(c)
    for sx in (-1, 1): d.ellipse((540 + sx * 345 - 56, cy - 52, 540 + sx * 345 + 56, cy + 52), fill=(243, 194, 155), outline=OL, width=6)
    paste_rot(c, DINO, 860, 1180, .42, -12)
    tiza(c, "¡Ahí dice", 330, 380, 96, CREMA, -6, f=F_BAL, borde=True)
    tiza(c, "MATEO!", 330, 480, 110, AMA, -6, f=F_ANTON, borde=True)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    dl.rounded_rectangle((90, 1250, 990, 1610), 40, fill=(255, 253, 244, 245), outline=OL, width=8); c.alpha_composite(lay)
    rotulo(c, "SERIE NUEVA", 540, 1250, 70, ROJO, CREMA, -3)
    tiza(c, "30 días para escribir", 540, 1365, 72, OL, 0, f=F_BAL)
    tiza(c, "su nombre… o repite", 540, 1450, 72, ROJO, 0, f=F_BAL)
    rotulo(c, "@escribirconpinti", 540, 1550, 56, AMA, OL, 0)
    c.convert("RGB").save(os.path.join(HERE, "portada_aviso_cuenta_vieja_9x16.jpg"), quality=93)
main()
