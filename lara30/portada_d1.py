import os, sys; sys.argv=[sys.argv[0]]
import render_d1 as D, lara_art as A
from PIL import Image, ImageDraw
c = A.cam(A.bg_sala(True), 0, 0, 1.6, 1.6, .32, .32, .5, .5, dur=1).convert("RGBA")
c.alpha_composite(Image.new("RGBA", (1080, 1920), (40, 10, 20, 70)))
D.char(c, "lara", 0, 700, 1150, 1.05, "sad"); D.char(c, "caio", 0, 250, 1500, .62, "laugh"); D.mesa(c, 1560)
d = ImageDraw.Draw(c)
d.rounded_rectangle((70, 170, 1010, 370), 40, fill=(196, 40, 48, 255), outline=(255, 255, 255), width=6)
d.text((540, 272), "FALTA O I…", font=A.font(A.F_ANTON, 150), fill=(255, 255, 255), anchor="mm")
d.text((540, 1700), "DIA 1 DE 30", font=A.font(A.F_ANTON, 110), fill=(255, 222, 72), anchor="mm", stroke_width=9, stroke_fill=(52, 14, 22))
c.convert("RGB").save(os.path.join(D.HERE, "portada_lara_dia1.jpg"), quality=90)
