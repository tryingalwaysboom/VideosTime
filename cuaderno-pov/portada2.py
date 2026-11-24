"""Portada Parte 2 (v2): la O torcida gigante rodeada en rojo y Sofía llorando. Misma maqueta que la Parte 1."""
import os
import portada as P
import render2 as V
from PIL import Image
def foto(llora=True):
    c = V.R.layer("bg_cuarto_sofia").resize((V.W, V.H)).copy()
    V.sofia(c, "triste", 540, 330, .72, 0.5); V.lagrimas(c, 540, 330, .72, 0.5)
    V.hoja_huevo(c, 540, 800, .98, -4, 1.0)
    return c.crop((40, 150, 1040, 910))
P.escena_foto = foto
P.portada(2, "mami, mi O parece un...", "¿HUEVO?", os.path.join(V.HERE, "portada_cuaderno_parte2_9x16.jpg"))
