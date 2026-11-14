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
    c.alpha_composite(r.VIG)
    c.convert("RGB").save(out, quality=93)

def _parte(c, y=1537):
    d = ImageDraw.Draw(c); pw = 560
    d.rounded_rectangle((540 - pw / 2, y - 77, 540 + pw / 2, y + 73), 36, fill=r.RED, outline=r.WHITE, width=8)
    r.text(d, (540, y), "PARTE 1", 120, r.WHITE, stroke=6)

def portada_nitro(out):
    """Pantalla partida: Nitro y su dinero contra el coche del tío."""
    os.environ["FINAL"] = "1"
    A, B = r._lado("A", 0), r._lado("B", 0)
    A2 = Image.new("RGBA", A.size, (8, 6, 18, 255)); A2.paste(A, (0, 110)); A = A2   # baja a Nitro para que la franja del título no le tape
    c = Image.new("RGBA", (r.W, r.H), (0, 0, 0, 255))
    c.alpha_composite(B)
    mask = Image.new("L", (r.W, r.H), 0); ImageDraw.Draw(mask).polygon([(0, 0)] + r.RAYO + [(0, r.H)], fill=255)
    c.paste(A, (0, 0), mask)
    gl = Image.new("RGBA", (r.W, r.H), (0, 0, 0, 0)); ImageDraw.Draw(gl).line(r.RAYO, fill=r.CYAN + (255,), width=40, joint="curve")
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(c); d.line(r.RAYO, fill=r.WHITE, width=12, joint="curve"); d.line(r.RAYO, fill=r.CYAN, width=5, joint="curve")
    band = Image.new("RGBA", (r.W, r.H), (0, 0, 0, 0)); ImageDraw.Draw(band).rectangle((0, 0, r.W, 640), fill=(8, 6, 18, 175))
    c.alpha_composite(band); d = ImageDraw.Draw(c)
    r.text(d, (540, 350), "ME OFRECE", 110, r.WHITE, stroke=10)
    r.text(d, (540, 470), "90.000 €", 140, (90, 230, 130), stroke=10)
    r.text(d, (540, 585), "POR EL COCHE DE MI TÍO", 62, r.YEL, stroke=8)
    _parte(c, 1600)
    c.alpha_composite(r.VIG); c.convert("RGB").save(out, quality=93)

def portada_lona(out):
    """Misterio: la lona 'NO TOCAR' bajo un foco en el taller a oscuras."""
    c = r.bg("bg_taller", 0, 0, 1.3, 1.3, 1, .5, .72); r.dark(c, 160)
    ov = Image.new("RGBA", (r.W, r.H), (0, 0, 0, 0))
    ImageDraw.Draw(ov).polygon([(440, 0), (640, 0), (1020, 1400), (60, 1400)], fill=(255, 230, 170, 75))
    c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(35)))
    r.put(c, "lona", 540, 1130, 1.0)
    for i in range(70):   # polvo en el foco
        x = 300 + (i * 137) % 480; y = 300 + (i * 251) % 900
        ImageDraw.Draw(c).ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 236, 190, 120))
    d = ImageDraw.Draw(c)
    r.text(d, (540, 380), "MI TÍO DESAPARECIÓ", 98, r.WHITE, stroke=10)
    r.text(d, (540, 500), "Y DEJÓ ESTO", 120, r.YEL, stroke=10)
    r.text(d, (540, 610), "DEBAJO DE LA LONA", 70, r.WHITE, stroke=8)
    _parte(c)
    c.alpha_composite(r.VIG); c.convert("RGB").save(out, quality=93)

if __name__ == "__main__":
    portada(os.path.join(r.HERE, "portada_1.jpg"))
    portada_nitro(os.path.join(r.HERE, "portada_2.jpg"))
    portada_lona(os.path.join(r.HERE, "portada_3.jpg"))
