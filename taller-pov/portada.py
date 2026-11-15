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

if __name__ == "__main__" and not os.environ.get("SERIE"):
    portada(os.path.join(r.HERE, "portada_1.jpg"))
    portada_nitro(os.path.join(r.HERE, "portada_2.jpg"))
    portada_lona(os.path.join(r.HERE, "portada_3.jpg"))


# ---------------------------------------------------------------- portada fija de la serie (solo cambia el número)
def _neon_titulo(c, y=330):
    """Cartel 'EL TALLER DE RUBÉN' en neón (mismo estilo que el logo)."""
    lay = Image.new("RGBA", (r.W, r.H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((220, y - 115, 860, y + 125), 28, fill=(14, 10, 28, 235), outline=(20, 16, 36), width=8)
    glow = Image.new("RGBA", (r.W, r.H), (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
    g.rounded_rectangle((236, y - 99, 844, y + 109), 22, outline=r.CYAN + (255,), width=8)
    r.text(g, (540, y - 45), "EL TALLER DE", 56, r.CYAN)
    r.text(g, (540, y + 45), "RUBÉN", 126, r.MAG)
    lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(16)))
    lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(4)))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((236, y - 99, 844, y + 109), 22, outline=(200, 250, 255), width=3)
    r.text(d, (540, y - 45), "EL TALLER DE", 56, (140, 248, 255))
    r.text(d, (540, y + 45), "RUBÉN", 126, (255, 120, 228))
    c.alpha_composite(lay)

def _parte_n(c, n, y=1560):
    lay = Image.new("RGBA", (r.W, r.H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((340, y - 58, 740, y + 58), 30, fill=r.YEL + (255,))
    sh = lay.filter(ImageFilter.GaussianBlur(18))
    c.alpha_composite(Image.eval(sh, lambda v: v) if False else sh)
    d2 = ImageDraw.Draw(c)
    d2.rounded_rectangle((340, y - 58, 740, y + 58), 30, fill=r.YEL, outline=r.OL, width=6)
    r.text(d2, (540, y + 2), f"PARTE {n}", 88, r.OL)

def _suelo_reflejo(c, name, x, y, s):
    """Coche con reflejo en el suelo mojado."""
    im = r.scaled(name, s)
    ref = im.transpose(Image.FLIP_TOP_BOTTOM)
    a = ref.getchannel("A").point(lambda v: int(v * .28))
    grad = Image.linear_gradient("L").resize(ref.size).point(lambda v: 255 - v)
    ref.putalpha(Image.composite(a, Image.new("L", ref.size, 0), grad))
    c.alpha_composite(ref, (int(x - im.width / 2), int(y + im.height / 2 - 40)))
    r.put(c, name, x, y, s)

def serie_A(n, out):
    """Taller de noche: cartel de neón arriba, el deportivo con reflejo y luz magenta."""
    c = r.bg("bg_taller", 0, 0, 1.25, 1.25, 1, .5, .62); r.dark(c, 120)
    gl = Image.new("RGBA", (r.W, r.H), (0, 0, 0, 0)); g = ImageDraw.Draw(gl)
    g.ellipse((-100, 1020, 1180, 1520), fill=r.MAG + (95,)); g.ellipse((200, 700, 880, 1100), fill=r.CYAN + (50,))
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(70)))
    _suelo_reflejo(c, "deportivo", 540, 990, .78)
    _neon_titulo(c, 640)
    _parte_n(c, n, 1290)
    c.alpha_composite(r.VIG); c.convert("RGB").save(out, quality=94)

def serie_B(n, out):
    """Fachada de noche con todas las letras encendidas y el deportivo saliendo por la persiana."""
    c = r.bg("bg_fachada", 0, 0, 1.0, 1.0, 1)
    inner = r.bg("bg_taller", 0, 0, 1.4, 1.4, 1, .5, .6).crop((150, 830, 930, 1400)); c.alpha_composite(inner, (150, 830))
    gl = Image.new("RGBA", (r.W, r.H), (0, 0, 0, 0)); g = ImageDraw.Draw(gl)
    g.rectangle((150, 830, 930, 1400), fill=(255, 220, 160, 60)); g.ellipse((0, 1250, 1080, 1650), fill=r.MAG + (80,))
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(40)))
    _suelo_reflejo(c, "deportivo", 540, 1150, .85)
    band = Image.new("RGBA", (r.W, r.H), (0, 0, 0, 0)); ImageDraw.Draw(band).rectangle((0, 560, r.W, 830), fill=(8, 6, 20, 235))
    c.alpha_composite(band.filter(ImageFilter.GaussianBlur(30)))
    _neon_titulo(c, 690)
    _parte_n(c, n, 1450)
    c.alpha_composite(r.VIG); c.convert("RGB").save(out, quality=94)

def serie_C(n, out):
    """Duelo: el deportivo del tío y el coche de Nitro frente a frente, con el cartel en medio."""
    c = r.bg("bg_noche", 0, 0, 1.0, 1.0, 1)
    gl = Image.new("RGBA", (r.W, r.H), (0, 0, 0, 0)); g = ImageDraw.Draw(gl)
    g.ellipse((-200, 300, 900, 900), fill=r.CYAN + (70,)); g.ellipse((200, 1000, 1300, 1600), fill=r.MAG + (80,))
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(80)))
    co = r.scaled("coche_negro", .75).transpose(Image.FLIP_LEFT_RIGHT)
    c.alpha_composite(co, (int(560 - co.width / 2), int(640 - co.height / 2)))
    _suelo_reflejo(c, "deportivo", 530, 1180, .75)
    _neon_titulo(c, 930)
    _parte_n(c, n, 1450)
    c.alpha_composite(r.VIG); c.convert("RGB").save(out, quality=94)

def a_34(path):
    """Recorta al formato 3:4 (1080x1440) de la cuadrícula del perfil de TikTok e Instagram."""
    im = Image.open(path); im.crop((0, 240, 1080, 1680)).save(path, quality=94)

if __name__ == "__main__" and os.environ.get("SERIE"):
    n = int(os.environ.get("PARTE", "1"))
    for k, fn in (("A", serie_A), ("B", serie_B), ("C", serie_C)):
        p = os.path.join(r.HERE, f"portada_serie_{k}_parte{n}.jpg"); fn(n, p); a_34(p)
