"""Portada del Día 7."""
import os
from portada_d2 import *
def m_estrella(c):
    cx, cy = 665, 640; d = ImageDraw.Draw(c); sombra(c, (cx - 290, cy - 210, cx + 290, cy + 210), 10, 120, 18)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay); dl.rectangle((cx - 290, cy - 210, cx + 290, cy + 210), fill=(255, 253, 244, 255), outline=(214, 190, 150, 255), width=7)
    P = [(cx - 170, cy + 140), (cx - 170, cy - 130), (cx, cy + 40), (cx + 170, cy - 130), (cx + 170, cy + 140)]; dl.line(P, fill=(63, 174, 74, 255), width=34, joint="curve")
    for x, y in P: dl.ellipse((x - 17, y - 17, x + 17, y + 17), fill=(63, 174, 74, 255))
    import math
    S = [(cx + 230 + (70 if i % 2 == 0 else 32) * math.sin(i * math.pi / 5), cy - 170 - (70 if i % 2 == 0 else 32) * math.cos(i * math.pi / 5)) for i in range(10)]
    dl.polygon(S, fill=(255, 212, 84, 255)); dl.line(S + [S[0]], fill=(29, 22, 48, 255), width=9, joint="curve")
    c.alpha_composite(lay.rotate(4, center=(cx, cy), resample=Image.BICUBIC))
base(7, m_estrella, "llora", "Escribió una M perfecta…", "¡Y SE PUSO A LLORAR!").convert("RGB").save(os.path.join(HERE, "portada_mateo_dia7_9x16.jpg"), quality=93)
