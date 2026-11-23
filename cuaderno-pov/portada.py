"""Portada de "El cuaderno de la abuela" (9:16). Como en Mateo: todo lo importante en el 3:4 central subido
(y 160..1600), apilado y centrado; la parte de abajo queda libre para la interfaz de TikTok."""
import os, sys, math
import render1 as V
from PIL import Image, ImageDraw, ImageFilter
R = V.R; W, H = 1080, 1920; OY = 250   # bajado: TikTok corta un poco arriba

def escena_foto(llora=True):
    s = R.layer("bg_desvan").resize((W, H)).copy(); R.dark(s, 40)
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((420, 500, 1080, 1200), fill=(255, 200, 90, 130))
    s.alpha_composite(gl.filter(ImageFilter.GaussianBlur(70)))
    R.put(s, "cuaderno", 760, 850, .5, rot=-8); V.brillos(s, 1.0, 0, 760, 850, 260, (255, 230, 150), 12)
    V.sofia(s, "llora" if llora else "timido", 330, 900, .78, 0.5)
    if llora: V.lagrimas(s, 330, 900, .78, 0.5)
    return s.crop((40, 420, 1040, 1180))   # 1000 x 760

def portada(parte, frase, palabra, out, rot=-3):
    c = R.layer("bg_desvan").resize((W, H)).filter(ImageFilter.GaussianBlur(14)).copy(); R.dark(c, 120)
    d = ImageDraw.Draw(c)
    # título
    for i, t in enumerate(("EL CUADERNO", "DE LA ABUELA")):
        d.text((540, OY + 115 + i * 104), t, font=V.font(V.F_ANTON, 96), fill=(255, 236, 200), anchor="mm", stroke_width=10, stroke_fill=V.OL)
    # foto con marco (como la polaroid de Mateo)
    foto = escena_foto().resize((800, 608))
    pol = Image.new("RGBA", (840, 700), (250, 246, 236, 255)); pol.alpha_composite(foto, (20, 20))
    ImageDraw.Draw(pol).rectangle((0, 0, 839, 699), outline=V.OL, width=6)
    pol = pol.rotate(rot, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", pol.size, (0, 0, 0, 0)); sh.putalpha(pol.getchannel("A").point(lambda v: v // 2))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), (int(540 - pol.width / 2 + 12), OY + 290 + 16))
    c.alpha_composite(pol, (int(540 - pol.width / 2), OY + 290))
    d = ImageDraw.Draw(c)
    # frase a mano + palabra grande dorada
    d.text((540, OY + 1045), frase, font=V.font(V.F_HAND, 84), fill=(255, 244, 214), anchor="mm")
    d.text((540, OY + 1150), palabra, font=V.font(V.F_BAL, 150), fill=V.ORO, anchor="mm", stroke_width=8, stroke_fill=(120, 70, 20))
    # sello PARTE N
    st = Image.new("RGBA", (330, 120), (0, 0, 0, 0)); ds = ImageDraw.Draw(st)
    ds.rounded_rectangle((0, 0, 329, 119), 22, fill=(250, 246, 236), outline=(194, 58, 90), width=8)
    ds.text((165, 62), f"PARTE {parte}", font=V.font(V.F_ANTON, 74), fill=(60, 40, 90), anchor="mm")
    st = st.rotate(3 if parte % 2 else -3, expand=True, resample=Image.BICUBIC)
    c.alpha_composite(st, (int(540 - st.width / 2), OY + 1255))
    c.convert("RGB").save(out, quality=92)

if __name__ == "__main__":
    portada(1, "si la escribes bien...", "SECRETO", os.path.join(V.HERE, "portada_cuaderno_parte1_9x16.jpg"))
