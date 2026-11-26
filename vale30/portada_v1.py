"""Portada 9:16 del Día 1 de «30 días sin celular». Todo lo importante dentro del recorte central 3:4 de la cuadrícula de TikTok (y 240-1680)."""
import render_c as V
from PIL import ImageDraw
c = V.bg("bg_cuarto", 0, 0, 1.0, 1.0, 1, .5, .5); V.osc(c, 70); V.rayos(c, 1.3, V.AMA, 540, 1000, 34)
d = ImageDraw.Draw(c); d.rectangle((540 - 300, 1500, 540 + 300, 1930), fill=(240, 184, 40), outline=V.OL, width=7)
V.put(c, "vale_orgullosa_nota", 540, 1010, 1.05); V.put(c, "nota", 540, 1250, 1.75, rot=-4)
V.titulo(c, "¿PUEDES", 540, 330, 150, V.AMA, -3, 1, 16); V.titulo(c, "LEERLA?", 540, 480, 170, V.AMA, -3, 1, 16)
V.papel(c, "DÍA 1", 180, 680, 92, -7, 1, V.TUR, V.OL, V.F_ANTON); V.caja_big(c, 905, 740, .5, 0)
V.papel(c, "30 DÍAS SIN CELULAR", 540, 1600, 78, 2, 1, V.ROJO, V.BLANCO, V.F_ANTON)
c.alpha_composite(V.acabado()); c.convert("RGB").save(V.HERE + "/portada_vale_dia1_9x16.jpg", quality=92)
g = c.convert("RGB").copy(); ImageDraw.Draw(g).rectangle((0, 240, 1079, 1680), outline=(0, 255, 0), width=6); g.save("/home/claude/an/cov.jpg", quality=80)
