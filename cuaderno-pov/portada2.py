"""Portada Parte 2: misma maqueta que la Parte 1; la foto es el cuaderno de noche: la O de Sofía y la página nueva con tinta fresca."""
import os
import portada as P
import render2 as V
def foto(llora=True):
    c = V.fondo_libro(0, 0, 7, 150); V.glow(c, 540, 760, 520, (255, 200, 120), 130, 80)
    V.cuaderno_abierto(c, *V.CB, 0, V.izq_O(), V.der_msg2(1e9))
    V.brillos(c, 1.0, 0, V.PX_R + V.PW / 2, V.PY + 260, 230, (200, 220, 255), 10)
    return c.crop((40, 420, 1040, 1180))
P.escena_foto = foto
P.portada(2, "alguien escribió anoche...", "¿QUIÉN?", os.path.join(V.HERE, "portada_cuaderno_parte2_9x16.jpg"))
