"""Portada del Día 9: papá cerrando el cuaderno de golpe (guía)."""
import os
from portada_d2 import *
def cuaderno_papa(c):
    cx, cy = 660, 650; lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((cx - 230, cy - 200, cx + 230, cy + 200), 18, fill=(63, 127, 208, 255), outline=(29, 22, 48, 255), width=9)
    d.rectangle((cx - 214, cy - 184, cx - 10, cy + 184), fill=(255, 253, 244, 255))
    G = (63, 174, 74, 255)
    for P in ([(cx - 196, cy + 90), (cx - 190, cy - 80), (cx - 150, cy + 10), (cx - 110, cy - 82), (cx - 104, cy + 92)], [(cx - 84, cy + 92), (cx - 54, cy - 84), (cx - 22, cy + 90)]):
        d.line(P, fill=G, width=20, joint="curve")
    for k in range(7): yy = cy - 168 + k * 56; d.ellipse((cx - 22, yy - 11, cx, yy + 11), fill=(200, 204, 214, 255), outline=(29, 22, 48, 255), width=4)
    d.line((cx + 520, cy - 420, cx + 150, cy - 40), fill=(34, 28, 58, 255), width=150); d.ellipse((cx + 60, cy - 120, cx + 240, cy + 40), fill=(34, 28, 58, 255))
    c.alpha_composite(lay.rotate(5, center=(cx, cy), resample=Image.BICUBIC))
base(9, cuaderno_papa, "triste", "Mi esposo me dijo:", "«DÉJALO JUGAR»").convert("RGB").save(os.path.join(HERE, "portada_mateo_dia9_9x16.jpg"), quality=93)
