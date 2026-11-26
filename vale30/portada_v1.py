"""Portada 9:16 del Día 1 de «30 días sin celular»."""
import render_v1 as V
from PIL import ImageDraw
c = V.bg("bg_cuarto", 0, 0, 1.0, 1.0, 1, .5, .5); V.rayos(c, 1.3, V.ROSA, 540, 900, 34)
V.put(c, "vale_shock_manos", 370, 1500, .98); V.caja_big(c, 850, 1480, .85, 0)
V.titulo(c, "30 DÍAS", 540, 420, 250, V.ROJO, -4, 1, 18, sfill=V.BLANCO); V.titulo(c, "SIN CELULAR", 540, 640, 150, V.BLANCO, -4, 1, 16)
V.papel(c, "solo puede escribir a mano", 540, 800, 60, 3, 1, V.AMA, f=V.F_HAND)
V.papel(c, "DÍA 1", 850, 1040, 110, 6, 1, V.TUR, V.OL, V.F_ANTON)
c.convert("RGB").save(V.HERE + "/portada_vale_dia1_9x16.jpg", quality=92)
