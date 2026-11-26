"""Portada del Día 5 (plantilla de la temporada, color del día: verde azulado)."""
import os
from portada_d2 import *
def hoja_una_letra(c):
    cx, cy = 665, 640; im = Image.open(os.path.join(HERE, "layers", "hoja.png")).convert("RGBA").resize((620, 448), Image.LANCZOS); d = ImageDraw.Draw(im)
    P = [(70, 350), (78, 130), (150, 270), (226, 124), (236, 352)]; d.line(P, fill=(63, 174, 74, 255), width=24, joint="curve")
    for x, y in P: d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=(63, 174, 74, 255))
    for k in range(4): d.line((290 + k * 78, 352, 290 + k * 78 + 54, 352), fill=(150, 150, 168, 255), width=8)
    d.text((330, 62), "Mi nombre:", font=font(F_AND, 34), fill=(120, 120, 140), anchor="lm")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); lay.alpha_composite(im, (cx - 310, cy - 224))
    sombra(c, (cx - 300, cy - 214, cx + 300, cy + 214), 10, 120, 18); c.alpha_composite(lay.rotate(4, center=(cx, cy), resample=Image.BICUBIC))
    lapiz_rojo(c, (cx - 290, cy - 150, cx - 20, cy + 170), 1, 15)
base(5, hoja_una_letra, "llora", "En clase se rieron de él…", "¡SOLO SABE UNA LETRA!").convert("RGB").save(os.path.join(HERE, "portada_mateo_dia5_9x16.jpg"), quality=93)
