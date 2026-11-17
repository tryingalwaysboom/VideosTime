"""Portada nueva Parte 1: candado nuevo sobre la trampilla + $1 (9:16, contenido en el 3:4 central)."""
import math
from PIL import Image, ImageDraw
import art as A, ep1 as E
from art import font, F_ANTON, F_UI
W, H = 1080, 1920
hx, hy = A.quad_pt(A.TRAP, .82, .5)
pl = A.plate_trampilla().copy(); A.candado(pl, hx + 50, hy + 40, 1.0, 1.0)
c = E.cam(pl, 2.0, hx - 40, hy + 120)
E.linterna(c, 700, 980, 600, 225)
# resplandor rojo desde la rendija de la trampilla
c.alpha_composite(A.soft((W, H), lambda d: d.rectangle((0, 1240, W, 1300), fill=(255, 60, 30, 150)), 40))
c.alpha_composite(A.vignette(W, H, 235))
g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
for y in range(240, 620): gd.line((0, y, W, y), fill=(4, 4, 12, int(max(0, 200 - (y - 240) * .5))))
for y in range(1180, 1700): gd.line((0, y, W, y), fill=(4, 4, 12, int(min(230, (y - 1180) * .7))))
c.alpha_composite(g); d = ImageDraw.Draw(c)
# arriba: titular
f1, f2 = font(F_ANTON, 120), font(F_ANTON, 160); w1 = d.textlength("PAGUÉ ", font=f1); w2 = d.textlength("$1", font=f2); x0 = W / 2 - (w1 + w2) / 2
d.text((x0, 360), "PAGUÉ ", font=f1, fill=(255, 255, 255), anchor="ls", stroke_width=12, stroke_fill=(14, 12, 24))
d.text((x0 + w1, 372), "$1", font=f2, fill=(255, 206, 60), anchor="ls", stroke_width=12, stroke_fill=(14, 12, 24))
d.rounded_rectangle((W / 2 - 130, 400, W / 2 + 130, 470), 18, fill=(255, 170, 70)); d.text((W / 2, 435), "PARTE 1", font=font(F_ANTON, 54), fill=(14, 12, 24), anchor="mm")
# flecha y etiqueta NUEVO hacia el candado
d.rounded_rectangle((90, 760, 380, 860), 22, fill=(255, 206, 60)); d.text((235, 810), "NUEVO", font=font(F_ANTON, 72), fill=(14, 12, 24), anchor="mm")
d.line((380, 820, 480, 900), fill=(255, 206, 60), width=14); d.polygon([(500, 925), (440, 905), (480, 865)], fill=(255, 206, 60))
# abajo: la pregunta + sello
E.text(d, (W / 2, 1330), "¿QUIÉN PUSO", 120, (255, 255, 255), stroke=12)
E.text(d, (W / 2, 1460), "ESTE CANDADO?", 120, (255, 80, 70), stroke=12)
E.paste_c(c, A.sello("37 AÑOS VACÍA", rot=-6, s=.55), W / 2, 1585)
c.convert("RGB").save("out/portada_casa_parte1_v2_9x16.jpg", quality=93)
p = c.convert("RGB").resize((360, 640)); p.save("/tmp/pv2.jpg")
