"""Portada del Ep.1 (1080x1920). Todo lo importante dentro del recorte 3:4 de la cuadrícula del perfil (y 240..1680)."""
import os
from PIL import Image, ImageDraw, ImageFilter
import render as r

def portada(out):
    c = r.bg("bg_taller", 0, 0, 1.35, 1.35, 1, .5, .7); r.dark(c, 90)
    # foco sobre el coche
    ov = Image.new("RGBA", (r.W, r.H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).polygon([(380, 300), (700, 300), (1080, 1500), (0, 1500)], fill=(255, 230, 170, 70))
    c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(40)))
    gl = Image.new("RGBA", (r.W, r.H), (0, 0, 0, 0))
    ImageDraw.Draw(gl).ellipse((40, 970, 1040, 1270), fill=r.MAG + (90,))
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(50)))
    r.put(c, "deportivo", 540, 1080, 1.12)
    d = ImageDraw.Draw(c)
    # título
    r.text(d, (540, 380), "HEREDÉ EL TALLER", 112, r.WHITE, stroke=10)
    r.text(d, (540, 505), "DE MI TÍO", 112, r.WHITE, stroke=10)
    r.text(d, (540, 640), "DESAPARECIDO", 128, r.YEL, stroke=10)
    # PARTE 1
    pw = 560
    d.rounded_rectangle((540 - pw / 2, 1460, 540 + pw / 2, 1610), 36, fill=r.RED, outline=r.WHITE, width=8)
    r.text(d, (540, 1537), "PARTE 1", 120, r.WHITE, stroke=6)
    # sello
    r.stamp(c, 1, 0, "¿A o B?", 540, 800, r.CYAN, -6, 70)
    c.alpha_composite(r.VIG)
    c.convert("RGB").save(out, quality=93)

if __name__ == "__main__":
    portada(os.path.join(r.HERE, "portada_parte1.jpg"))
