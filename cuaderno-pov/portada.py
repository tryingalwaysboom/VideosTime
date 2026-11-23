"""Portada de "El cuaderno de la abuela" (9:16, diseño centrado en la zona segura 3:4)."""
import os, sys, math
import render1 as V
from PIL import Image, ImageDraw, ImageFilter
R = V.R; W, H = 1080, 1920
def portada(parte, frase, out):
    c = R.layer("bg_desvan").resize((W, H)).filter(ImageFilter.GaussianBlur(3)).copy(); R.dark(c, 70)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse((140, 520, 940, 1320), fill=(255, 200, 90, 120))
    c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(90)))
    R.put(c, "cuaderno", 560, 930, .78, rot=-7)
    V.brillos(c, 1.0, 0, 560, 930, 380, (255, 230, 150), 14)
    # nota escrita a mano sobre el cuaderno
    lay = Image.new("RGBA", (560, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, 559, 299), 14, fill=(255, 246, 200), outline=V.OL, width=6)
    for i, l in enumerate(frase): d.text((280, 70 + i * 80), l, font=V.font(V.F_HAND, 66), fill=V.TINTA, anchor="mm")
    lay = lay.rotate(6, expand=True, resample=Image.BICUBIC); c.alpha_composite(lay, (440, 1140))
    V.sofia(c, "llora", 250, 1300, .62, 0.5); V.lagrimas(c, 250, 1300, .62, 0.5)
    d = ImageDraw.Draw(c)
    for i, (t, sz) in enumerate((("EL CUADERNO", 118), ("DE LA ABUELA", 118))):
        d.text((540, 330 + i * 130), t, font=V.font(V.F_ANTON, sz), fill=(255, 236, 200), anchor="mm", stroke_width=12, stroke_fill=V.OL)
    st = Image.new("RGBA", (330, 130), (0, 0, 0, 0)); ds = ImageDraw.Draw(st)
    ds.rounded_rectangle((0, 0, 329, 129), 22, fill=V.ORO, outline=V.OL, width=7)
    ds.text((165, 66), f"PARTE {parte}", font=V.font(V.F_ANTON, 78), fill=V.OL, anchor="mm")
    st = st.rotate(-8 if parte % 2 else 8, expand=True, resample=Image.BICUBIC); c.alpha_composite(st, (690, 1500))
    c.convert("RGB").save(out, quality=92)
if __name__ == "__main__":
    portada(1, ["Si la escribes bien…", "te cuento un secreto"], os.path.join(V.HERE, "portada_cuaderno_parte1_9x16.jpg"))
