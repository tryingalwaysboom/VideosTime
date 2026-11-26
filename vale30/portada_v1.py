"""Portada 9:16 del Día 1 de «30 días sin celular». Todo lo importante dentro del recorte central 3:4 de la cuadrícula de TikTok (y 240-1680)."""
import render_v1 as V
from PIL import ImageDraw
c = V.bg("bg_cuarto", 0, 0, 1.0, 1.0, 1, .5, .5); V.osc(c, 60); V.rayos(c, 1.3, V.ROSA, 540, 1000, 36)
d = ImageDraw.Draw(c); d.rectangle((540 - 290, 1560, 540 + 290, 1930), fill=(240, 184, 40), outline=V.OL, width=7)
V.put(c, "vale_shock_manos", 540, 1090, .94)
V.caja_big(c, 905, 760, .5, 0); V.papel(c, "DÍA 1", 175, 700, 92, -7, 1, V.TUR, V.OL, V.F_ANTON)
# la notificación que no pudo leer
d = ImageDraw.Draw(c); d.rounded_rectangle((108, 318, 988, 528), 58, fill=(0, 0, 0)); d.rounded_rectangle((100, 306, 980, 516), 58, fill=V.BLANCO, outline=V.OL, width=9)
d.ellipse((130, 342, 268, 480), fill=V.ROSA, outline=V.OL, width=7); d.text((199, 409), "D", font=V.font(V.F_ANTON, 92), fill=V.BLANCO, anchor="mm")
d.text((300, 370), "Dani · 23:58", font=V.font(V.F_BAL, 44), fill=(120, 116, 150), anchor="lm"); d.text((300, 444), "tengo que decirte algo…", font=V.font(V.F_BAL, 55), fill=V.OL, anchor="lm")
V.titulo(c, "30 DÍAS", 540, 1275, 230, V.ROJO, -3, 1, 18, sfill=V.BLANCO); V.titulo(c, "SIN CELULAR", 540, 1465, 136, V.BLANCO, -3, 1, 16)
V.papel(c, "nunca leyó el mensaje", 540, 1608, 60, 2, 1, V.AMA, f=V.F_HAND)
c.alpha_composite(V.acabado()); c.convert("RGB").save(V.HERE + "/portada_vale_dia1_9x16.jpg", quality=92)
g = c.convert("RGB").copy(); ImageDraw.Draw(g).rectangle((0, 240, 1079, 1680), outline=(0, 255, 0), width=6); g.save("/home/claude/an/cov.jpg", quality=80)
