"""Portada del Día 6."""
import os
from portada_d2 import *
def abu(c):
    im = Image.open(os.path.join(HERE, "layers", "abuela_guino.png")).convert("RGBA").crop((250, 380, 1350, 1700)).resize((608, 730), Image.LANCZOS)
    c.alpha_composite(im, (420, 396))
base(6, abu, "feliz", "Mi hijo no quería volver…", "¡Y HABLÓ LA ABUELA!").convert("RGB").save(os.path.join(HERE, "portada_mateo_dia6_9x16.jpg"), quality=93)
