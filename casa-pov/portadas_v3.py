"""Dos estilos nuevos con PARTE 2 muy grande (D: póster con marco · E: número gigante en diagonal)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import salon2 as S2, ep1 as E, art as A
from art import font, F_ANTON, F_UI
W, H = 1080, 1920
def escena(z=1.2, ox=120, oy=380):
    c = S2.pared_cerca(0, rasgado=.6); return c.resize((int(W * z), int(H * z))).crop((ox, oy, ox + W, oy + H))

# D) PÓSTER: fondo naranja con textura, foto con marco blanco inclinado, "PARTE 2" gigante, gancho debajo
def diseno_d():
    yy, xx = np.mgrid[0:H, 0:W]; t = np.clip(np.sqrt((xx - W / 2) ** 2 + (yy - 900) ** 2) / 1300, 0, 1)[..., None]
    bg = (np.array([255, 170, 70]) * (1 - t) + np.array([210, 90, 40]) * t).astype(np.uint8)
    c = Image.fromarray(np.dstack([bg, np.full((H, W), 255, np.uint8)]), "RGBA"); d = ImageDraw.Draw(c)
    for k in range(-20, 40): d.line((k * 60, 0, k * 60 - 900, H), fill=(255, 190, 110, 40), width=14)
    d.text((W / 2, 330), "LA CASA DE $1", font=font(F_ANTON, 70), fill=(255, 255, 255), anchor="mm", stroke_width=6, stroke_fill=(120, 50, 20))
    foto = escena(1.25, 160, 520).crop((0, 0, W, 760)).resize((820, 640))
    fr = Image.new("RGBA", (860, 680), (255, 255, 255, 255)); fr.paste(foto, (20, 20))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle((140, 440, 980, 1140), fill=(0, 0, 0, 120)); c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)))
    fr = fr.rotate(-3, expand=True, resample=Image.BICUBIC); c.alpha_composite(fr, (W // 2 - fr.width // 2, 420))
    d = ImageDraw.Draw(c)
    d.text((W / 2, 1270), "PARTE 2", font=font(F_ANTON, 230), fill=(255, 255, 255), anchor="mm", stroke_width=14, stroke_fill=(30, 20, 40))
    d.rounded_rectangle((110, 1420, W - 110, 1560), 30, fill=(30, 20, 40)); d.text((W / 2, 1490), "¿UNA CAJA FUERTE?", font=font(F_ANTON, 92), fill=(255, 206, 60), anchor="mm")
    return c

# E) NÚMERO GIGANTE: escena a sangre oscurecida, "2" enorme detrás, "PARTE" encima, gancho abajo
def diseno_e():
    c = S2.pared_cerca(0, rasgado=.45, safe=False).resize((int(W * 1.3), int(H * 1.3))).crop((160, 380, 160 + W, 380 + H)); c.alpha_composite(Image.new("RGBA", (W, H), (10, 8, 20, 120)))
    n = Image.new("RGBA", (W, H), (0, 0, 0, 0)); nd = ImageDraw.Draw(n)
    nd.text((W / 2 + 40, 980), "2", font=font(F_ANTON, 1100), fill=(255, 206, 60, 255), anchor="mm", stroke_width=20, stroke_fill=(30, 20, 40))
    c.alpha_composite(n.rotate(-6, resample=Image.BICUBIC, center=(W / 2, 980)))
    s = S2.caja_fuerte().crop((260, 600, 820, 1160)).resize((500, 500)); c.alpha_composite(s, (50, 960))   # la caja delante del número
    d = ImageDraw.Draw(c)
    E.text(d, (W / 2, 330), "PARTE", 150, (255, 255, 255), stroke=12)
    d.rounded_rectangle((90, 1500, W - 90, 1640), 28, fill=(255, 255, 255)); d.text((W / 2, 1570), "¿QUÉ HAY DENTRO?", font=font(F_ANTON, 92), fill=(30, 20, 40), anchor="mm")
    d.text((W / 2, 1460), "LA CASA DE $1", font=font(F_UI, 34), fill=(255, 206, 60), anchor="mm")
    return c

ims = []
for k, fn in (("D", diseno_d), ("E", diseno_e)):
    im = fn().convert("RGB"); im.save(f"out/portada_diseno_{k}.jpg", quality=92); ims.append(im)
sh = Image.new("RGB", (2 * 420 + 20, 780), (30, 30, 34)); d = ImageDraw.Draw(sh)
for i, im in enumerate(ims):
    sh.paste(im.resize((420, 747)), (10 + i * 430, 30)); d.text((10 + i * 430 + 210, 15), "DE"[i], font=font(F_ANTON, 26), fill=(255, 206, 60), anchor="mm")
sh.save("out/portadas_propuestas_2.jpg", quality=90)
