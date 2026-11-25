"""Portada del Día 3 (plantilla de la temporada, color del día: azul)."""
import os
from portada_d2 import *
def crayola_tirada(c):
    cx, cy = 660, 650; lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((cx - 300, cy - 250, cx + 300, cy + 250), 30, fill=MADERA + (255,), outline=OL + (255,), width=8)
    for i in range(4): d.line((cx - 296, cy - 150 + i * 110, cx + 296, cy - 170 + i * 110), fill=(150, 100, 58, 255), width=6)
    sombra(c, (cx - 300, cy - 250, cx + 300, cy + 250), 30, 120, 18); c.alpha_composite(lay.rotate(4, center=(cx, cy), resample=Image.BICUBIC))
    put(c, "crayola", cx, cy + 10, 1.05, rot=28); d = ImageDraw.Draw(c)
    for a in (200, 230, 260, 290, 320): d.line((cx + 250 * math.cos(math.radians(a)), cy + 190 * math.sin(math.radians(a)), cx + 330 * math.cos(math.radians(a)), cy + 250 * math.sin(math.radians(a))), fill=TIZA, width=10)
    lapiz_rojo(c, (cx - 270, cy - 200, cx + 270, cy + 210), 1, 16)
base(3, crayola_tirada, "enojado", "Tiró la crayola y gritó:", "¡NO ESCRIBO NUNCA!").convert("RGB").save(os.path.join(HERE, "portada_mateo_dia3_9x16.jpg"), quality=93)
