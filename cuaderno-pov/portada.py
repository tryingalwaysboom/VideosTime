"""Portada de "El cuaderno de la abuela" (9:16, diseño centrado en la zona segura 3:4)."""
import os, sys, math
import render1 as V
from PIL import Image, ImageDraw, ImageFilter
R = V.R; W, H = 1080, 1920
def portada(parte, frase, out):
    c = R.layer("bg_desvan").resize((W, H)).filter(ImageFilter.GaussianBlur(3)).copy(); R.dark(c, 70)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse((200, 540, 1000, 1260), fill=(255, 200, 90, 120))
    c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(90)))
    R.put(c, "cuaderno", 600, 900, .62, rot=-7)
    V.brillos(c, 1.0, 0, 600, 900, 330, (255, 230, 150), 14)
    # nota escrita a mano sobre el cuaderno
    lay = Image.new("RGBA", (520, 280), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, 519, 279), 14, fill=(255, 246, 200), outline=V.OL, width=6)
    for i, l in enumerate(frase): d.text((260, 70 + i * 74), l, font=V.font(V.F_HAND, 60), fill=V.TINTA, anchor="mm")
    lay = lay.rotate(6, expand=True, resample=Image.BICUBIC); c.alpha_composite(lay, (470, 1130))
    V.sofia(c, "llora", 250, 1330, .56, 0.5); V.lagrimas(c, 250, 1330, .56, 0.5)
    d = ImageDraw.Draw(c)
    for i, (t, sz) in enumerate((("EL CUADERNO", 104), ("DE LA ABUELA", 104))):
        d.text((540, 360 + i * 116), t, font=V.font(V.F_ANTON, sz), fill=(255, 236, 200), anchor="mm", stroke_width=12, stroke_fill=V.OL)
    st = Image.new("RGBA", (300, 120), (0, 0, 0, 0)); ds = ImageDraw.Draw(st)
    ds.rounded_rectangle((0, 0, 299, 119), 22, fill=V.ORO, outline=V.OL, width=7)
    ds.text((150, 61), f"PARTE {parte}", font=V.font(V.F_ANTON, 72), fill=V.OL, anchor="mm")
    st = st.rotate(-8 if parte % 2 else 8, expand=True, resample=Image.BICUBIC); c.alpha_composite(st, (690, 1440))
    c.convert("RGB").save(out, quality=92)
if __name__ == "__main__":
    portada(1, ["Si la escribes bien…", "te cuento un secreto"], os.path.join(V.HERE, "portada_cuaderno_parte1_9x16.jpg"))
