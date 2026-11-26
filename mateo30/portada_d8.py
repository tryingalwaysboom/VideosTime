"""Portada del Día 8."""
import os
from portada_d2 import *
def hoja_ma(c):
    cx, cy = 665, 640; sombra(c, (cx - 290, cy - 210, cx + 290, cy + 210), 10, 120, 18)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); d.rectangle((cx - 290, cy - 210, cx + 290, cy + 210), fill=(255, 253, 244, 255), outline=(214, 190, 150, 255), width=7); G = (63, 174, 74, 255)
    for P in ([(cx - 240, cy + 130), (cx - 232, cy - 120), (cx - 130, cy + 30), (cx - 30, cy - 124), (cx - 20, cy + 134)], [(cx + 40, cy + 134), (cx + 140, cy - 126), (cx + 244, cy + 130)], [(cx + 86, cy + 40), (cx + 200, cy + 44)]):
        d.line(P, fill=G, width=30, joint="curve")
        for x, y in P: d.ellipse((x - 15, y - 15, x + 15, y + 15), fill=G)
    r = 26; hx, hy = cx + 240, cy - 160; R_ = (230, 70, 70, 255)
    d.ellipse((hx - 2 * r, hy - r, hx, hy + r), fill=R_); d.ellipse((hx, hy - r, hx + 2 * r, hy + r), fill=R_); d.polygon([(hx - 1.86 * r, hy + .3 * r), (hx + 1.86 * r, hy + .3 * r), (hx, hy + 2.2 * r)], fill=R_)
    c.alpha_composite(lay.rotate(4, center=(cx, cy), resample=Image.BICUBIC))
base(8, hoja_ma, "feliz", "Escribió MA y me dijo:", "«MIRA, PONE MAMÁ»").convert("RGB").save(os.path.join(HERE, "portada_mateo_dia8_9x16.jpg"), quality=93)
