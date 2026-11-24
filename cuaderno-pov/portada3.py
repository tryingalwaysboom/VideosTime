"""Portada Parte 2 v3: la página con tinta fresca."""
import os
import portada as P
import render2b as V
def foto(llora=True):
    V._OV.append(V.Image.new("RGBA", (V.W, V.H), (0, 0, 0, 0)))
    try: c = V.sc_b1(1.2)
    finally: V._OV.pop()
    return c.crop((40, 150, 1040, 910))
P.escena_foto = foto
P.portada(2, "alguien escribió aquí...", "¿QUIÉN?", os.path.join(V.HERE, "portada_cuaderno_parte2_v3_9x16.jpg"))
