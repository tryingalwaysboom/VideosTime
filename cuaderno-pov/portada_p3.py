"""Portada Parte 3: Sofía con la nota firmada S+O y el cuaderno que contestó."""
import os
import portada as P
import render3 as V
from PIL import Image
def foto(llora=True):
    c = V.bgz("bg_cuarto_sofia", 1.0, 0, 1.0, 1.0, 4).copy()
    V.sofia(c, "feliz", 540, 560, .85, 0.5)
    n = V.nota_firma(.62, -5); c.alpha_composite(n, (int(540 - n.width / 2), 1010))
    return c.crop((40, 150, 1040, 910 + 60))
P.escena_foto = foto
P.portada(3, "le dejé una nota al cuaderno y...", "¡CONTESTÓ!", os.path.join(V.HERE, "portada_cuaderno_parte3_9x16.jpg"))
