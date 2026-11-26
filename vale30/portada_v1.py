"""Portada 9:16 del Día 1 de «30 días sin celular». Todo lo importante dentro del recorte central 3:4 de la cuadrícula de TikTok (y 240-1680)."""
import render_v1 as V
from PIL import ImageDraw
c = V.bg("bg_cuarto", 0, 0, 1.0, 1.0, 1, .5, .5); V.rayos(c, 1.3, V.ROSA, 540, 900, 34)
d = ImageDraw.Draw(c); d.rectangle((540 - 290, 1500, 540 + 290, 1930), fill=V.AMA, outline=V.OL, width=9)
V.put(c, "vale_shock_manos", 540, 1010, .94)
V.caja_big(c, 880, 520, .62, 0); V.papel(c, "DÍA 1", 200, 470, 100, -7, 1, V.TUR, V.OL, V.F_ANTON)
V.titulo(c, "30 DÍAS", 540, 1215, 240, V.ROJO, -3, 1, 18, sfill=V.BLANCO); V.titulo(c, "SIN CELULAR", 540, 1415, 140, V.BLANCO, -3, 1, 16)
V.papel(c, "solo puede escribir a mano", 540, 1570, 58, 2, 1, V.AMA, f=V.F_HAND)
c.convert("RGB").save(V.HERE + "/portada_vale_dia1_9x16.jpg", quality=92)
g = c.convert("RGB").copy(); ImageDraw.Draw(g).rectangle((0, 240, 1079, 1680), outline=(0, 255, 0), width=6); g.save("/home/claude/an/cov.jpg", quality=80)
