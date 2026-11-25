"""Portada del vídeo de aviso para la cuenta vieja: estilo de la temporada nueva (pizarra verde) para que se note que es otra
serie, con «¡SERIE NUEVA!», la nota REPITE, Mateo asustado y el @ de la cuenta nueva. Todo dentro de la zona 3:4 (x 90-990, y 300-1620)."""
import os
from render_d1 import *
def main():
    c = pizarra(); d = ImageDraw.Draw(c)
    rotulo(c, "¡SERIE NUEVA!", 540, 372, 92, AMA, OL, -3)
    nb = nota_img(); z = .55; cx, cy, rot = 700, 760, 6
    sombra(c, (cx - 440 * z, cy - 560 * z, cx + 440 * z, cy + 560 * z), 24, 120, 18); paste_rot(c, nb, cx, cy, z, rot)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); x0, y0, x1, y1 = NOTA_REPITE
    lapiz_rojo(lay, (cx + x0 * z, cy + y0 * z, cx + x1 * z, cy + y1 * z), 1, 14)
    c.alpha_composite(lay.rotate(rot, center=(cx, cy), resample=Image.BICUBIC))
    calendario(d, 200, 560, 1.15, 30)
    mateo(c, "susto", 300, 990, .78, 0, blink=False)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    dl.rectangle((0, 1150, W, H), fill=PIZ2 + (255,)); dl.line((0, 1150, W, 1150), fill=(214, 190, 150, 255), width=8); c.alpha_composite(lay)
    tiza(c, "30 días para escribir", 540, 1240, 84, TIZA, 0, f=F_BAL)
    tiza(c, "su nombre… o REPITE", 540, 1350, 82, AMA, 0, f=F_BAL)
    rotulo(c, "@escribirconpinti", 540, 1505, 66, ROJO, CREMA, 0)
    c.convert("RGB").save(os.path.join(HERE, "portada_aviso_cuenta_vieja_9x16.jpg"), quality=93)
main()
