"""Portada del Día 4 (plantilla de la temporada, color del día: naranja)."""
import os
from portada_d2 import *
def sofa_rayado(c):
    cx, cy = 660, 650; im = Image.open(os.path.join(HERE, "layers", "bg_sala.png")).convert("RGBA"); d = ImageDraw.Draw(im)
    P = [(400, 1030), (398, 800), (540, 962), (682, 800), (684, 1030)]; d.line([(x * 2, y * 2) for x, y in P], fill=(24, 22, 30, 255), width=56, joint="curve")
    for x, y in P: d.ellipse((x * 2 - 28, y * 2 - 28, x * 2 + 28, y * 2 + 28), fill=(24, 22, 30, 255))
    im = im.crop((500, 1340, 1660, 2340)).resize((600, 517), Image.LANCZOS); m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), 30, fill=255); im.putalpha(m)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); lay.alpha_composite(im, (cx - 300, cy - 258)); ImageDraw.Draw(lay).rounded_rectangle((cx - 300, cy - 258, cx + 300, cy + 258), 30, outline=OL + (255,), width=8)
    sombra(c, (cx - 300, cy - 258, cx + 300, cy + 258), 30, 120, 18); c.alpha_composite(lay.rotate(4, center=(cx, cy), resample=Image.BICUBIC))
    lapiz_rojo(c, (cx - 200, cy - 200, cx + 210, cy + 130), 1, 16)
base(4, sofa_rayado, "susto", "Rayó el sofá nuevo…", "¡Y PAPÁ YA LLEGÓ!").convert("RGB").save(os.path.join(HERE, "portada_mateo_dia4_9x16.jpg"), quality=93)
