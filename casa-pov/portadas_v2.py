"""3 propuestas de diseño de portada (ejemplo: Parte 2). Todo en el 3:4 central (y 240-1680)."""
import math
from PIL import Image, ImageDraw, ImageFilter
import salon2 as S2, salon as SL, ep1 as E, art as A, manos as M
from art import font, F_ANTON, F_UI
W, H = 1080, 1920
def grad_v(c, y0, y1, a0, a1, col=(6, 6, 14)):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    for y in range(y0, y1): d.line((0, y, W, y), fill=col + (int(a0 + (a1 - a0) * (y - y0) / max(1, y1 - y0)),))
    c.alpha_composite(g)

# A) PLANTILLA DE SERIE: franja de marca arriba, número de parte grande, escena, gancho con palabra resaltada, etiqueta de precio
def diseno_a():
    c = S2.pared_cerca(0, rasgado=.6); c = c.resize((int(W * 1.15), int(H * 1.15))).crop((80, 60, 80 + W, 60 + H))
    grad_v(c, 1150, 1700, 0, 235)
    d = ImageDraw.Draw(c)
    d.rectangle((0, 250, W, 360), fill=(255, 170, 70)); d.text((60, 305), "LA CASA DE $1", font=font(F_ANTON, 64), fill=(14, 12, 24), anchor="lm")
    d.ellipse((W - 260, 200, W - 60, 400), fill=(14, 12, 24), outline=(255, 170, 70), width=10); d.text((W - 160, 288), "2", font=font(F_ANTON, 130), fill=(255, 206, 60), anchor="mm"); d.text((W - 160, 368), "PARTE", font=font(F_UI, 22), fill=(255, 255, 255), anchor="mm")
    E.text(d, (W / 2, 1360), "ENCONTRÉ UNA", 96, (255, 255, 255), stroke=10)
    d.rounded_rectangle((90, 1420, W - 90, 1560), 26, fill=(255, 206, 60)); d.text((W / 2, 1490), "CAJA FUERTE", font=font(F_ANTON, 120), fill=(14, 12, 24), anchor="mm")
    st = Image.new("RGBA", (360, 140), (0, 0, 0, 0)); sd = ImageDraw.Draw(st); sd.rounded_rectangle((0, 0, 360, 140), 24, fill=(230, 60, 50)); sd.text((180, 70), "$1,725", font=font(F_ANTON, 84), fill=(255, 255, 255), anchor="mm")
    c.alpha_composite(st.rotate(8, expand=True, resample=Image.BICUBIC), (640, 1040))
    return c

# B) CINEMATOGRÁFICA: imagen a sangre, poco texto, una palabra gigante y "PARTE 2" vertical
def diseno_b():
    c = S2.pared_cerca(0, rasgado=.6); c = c.resize((int(W * 1.35), int(H * 1.35))).crop((200, 220, 200 + W, 220 + H))
    c.alpha_composite(A.soft((W, H), lambda d: d.ellipse((120, 500, 960, 1300), fill=(255, 200, 120, 60)), 80))
    c.alpha_composite(A.vignette(W, H, 240)); grad_v(c, 1200, 1700, 0, 220)
    d = ImageDraw.Draw(c)
    E.text(d, (W / 2, 1450), "¿QUÉ HAY DENTRO?", 118, (255, 255, 255), stroke=10)
    d.rectangle((W / 2 - 120, 1540, W / 2 + 120, 1550), fill=(255, 206, 60))
    d.text((W / 2, 1600), "LA CASA DE $1  ·  PARTE 2", font=font(F_UI, 34), fill=(255, 206, 60), anchor="mm")
    return c

# C) ESTILO MINIATURA: POV con la mano, círculo rojo y flecha, texto corto con números
def diseno_c():
    c = S2.pared_cerca(0, rasgado=.6); c = c.resize((int(W * 1.1), int(H * 1.1))).crop((50, 0, 50 + W, H))
    M.poner(c, "palma", 820, 1780, "d", 1.15, -18, 1.0)
    d = ImageDraw.Draw(c)
    d.ellipse((260, 560, 880, 1180), outline=(240, 40, 40), width=18)
    d.line((140, 420, 300, 600), fill=(240, 40, 40), width=26); d.polygon([(330, 640), (250, 600), (310, 540)], fill=(240, 40, 40))
    E.text(d, (W / 2, 330), "PAGUÉ $1…", 110, (255, 255, 255), stroke=12)
    d.rounded_rectangle((70, 1260, 620, 1400), 26, fill=(14, 12, 24)); d.text((345, 1330), "Y ENCONTRÉ ESTO", font=font(F_ANTON, 70), fill=(255, 206, 60), anchor="mm")
    d.rounded_rectangle((70, 1420, 330, 1500), 18, fill=(255, 170, 70)); d.text((200, 1460), "PARTE 2", font=font(F_ANTON, 54), fill=(14, 12, 24), anchor="mm")
    return c

out = []
for k, fn in (("A", diseno_a), ("B", diseno_b), ("C", diseno_c)):
    im = fn().convert("RGB"); im.save(f"out/portada_diseno_{k}.jpg", quality=92); out.append(im)
sh = Image.new("RGB", (3 * 400 + 40, 760), (30, 30, 34)); d = ImageDraw.Draw(sh)
for i, im in enumerate(out):
    sh.paste(im.resize((400, 711)), (10 + i * 415, 40)); d.text((10 + i * 415 + 200, 20), "ABC"[i], font=font(F_ANTON, 30), fill=(255, 206, 60), anchor="mm")
    g = im.crop((0, 240, W, 1680)).resize((240, 320)); sh.paste(g, (10 + i * 415 + 80, 430)) if False else None
sh.save("out/portadas_propuestas.jpg", quality=90)
