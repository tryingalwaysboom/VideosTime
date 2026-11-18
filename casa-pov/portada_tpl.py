"""Plantilla fija de portada de "La casa de 1 dólar" (estilo póster): fondo de color con rayas, foto con marco blanco
inclinado, PARTE N gigante y gancho en franja oscura. Todo dentro del 3:4 central.
Uso: portada(n, escena_rgba_1080x1920, "¿GANCHO?", color="salon", salida="out/...jpg")"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art import font, F_ANTON
W, H = 1080, 1920
COLORES = {"salon": ((255, 170, 70), (210, 90, 40)), "bano": ((90, 170, 230), (30, 90, 170)), "cocina": ((130, 200, 110), (50, 130, 60)),
           "habitacion": ((200, 140, 220), (120, 60, 160)), "jardin": ((170, 210, 90), (80, 140, 40))}

def portada(n, escena, gancho, color="salon", salida=None, foto_box=None, rot=-3):
    c0, c1 = COLORES[color]
    yy, xx = np.mgrid[0:H, 0:W]; t = np.clip(np.sqrt((xx - W / 2) ** 2 + (yy - 900) ** 2) / 1300, 0, 1)[..., None]
    bg = (np.array(c0) * (1 - t) + np.array(c1) * t).astype(np.uint8)
    c = Image.fromarray(np.dstack([bg, np.full((H, W), 255, np.uint8)]), "RGBA"); d = ImageDraw.Draw(c)
    hi = tuple(min(255, v + 25) for v in c0)
    for k in range(-20, 40): d.line((k * 60, 0, k * 60 - 900, H), fill=hi + (60,), width=14)
    dk = tuple(int(v * .45) for v in c1)
    d.text((W / 2, 330), "LA CASA DE $1", font=font(F_ANTON, 70), fill=(255, 255, 255), anchor="mm", stroke_width=6, stroke_fill=dk)
    box = foto_box or (0, 0, W, 760)
    foto = escena.crop(box).resize((820, 640), Image.LANCZOS)
    fr = Image.new("RGBA", (860, 680), (255, 255, 255, 255)); fr.paste(foto, (20, 20))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle((140, 440, 980, 1140), fill=(0, 0, 0, 120)); c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)))
    fr = fr.rotate(rot, expand=True, resample=Image.BICUBIC); c.alpha_composite(fr, (W // 2 - fr.width // 2, 420))
    d = ImageDraw.Draw(c)
    d.text((W / 2, 1270), f"PARTE {n}", font=font(F_ANTON, 230), fill=(255, 255, 255), anchor="mm", stroke_width=14, stroke_fill=(30, 20, 40))
    f = font(F_ANTON, 92); tw = d.textlength(gancho, font=f)
    if tw > 780: f = font(F_ANTON, int(92 * 780 / tw)); tw = d.textlength(gancho, font=f)
    d.rounded_rectangle((W / 2 - tw / 2 - 50, 1420, W / 2 + tw / 2 + 50, 1560), 30, fill=(30, 20, 40)); d.text((W / 2, 1490), gancho, font=f, fill=(255, 206, 60), anchor="mm")
    out = c.convert("RGB")
    if salida: out.save(salida, quality=93)
    return out

if __name__ == "__main__":
    import salon2 as S2
    W2, H2 = 1080, 1920
    e = S2.pared_cerca(0, rasgado=.6).resize((int(W2 * 1.25), int(H2 * 1.25))).crop((160, 520, 160 + W2, 520 + H2))
    portada(2, e, "¿UNA CAJA FUERTE?", "salon", "out/portada_salon_parte2_9x16.jpg")
