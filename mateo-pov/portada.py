"""Portada fija de la serie (1080x1440, 3:4 como la cuadrícula del perfil). Solo cambia "PARTE N".
Misma escala que las portadas del taller: título en un cartel, el personaje mediano y "PARTE N" a 3/4 de altura.
Uso: python3 portada.py 1"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter
import render as V

def portada(n, out):
    W, H = 1080, 1440
    c = V.bg("bg_cocina", 0, 0, 1.0, 1.0, 1, .5, .5).crop((0, 240, W, 240 + H)).convert("RGBA")
    c.alpha_composite(Image.new("RGBA", (W, H), (40, 20, 50, 60)))
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((240, 560, 840, 1160), fill=(255, 210, 150, 120))
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(80)))
    # cartel del título (estilo cuaderno, como la barra de la serie)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((150, 252, 930, 512), 34, fill=(40, 20, 40, 110))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((150, 240, 930, 500), 34, fill=(255, 250, 240), outline=V.NAVY, width=6)
    for y in (330, 380, 430, 480): d.line((180, y, 900, y), fill=(150, 190, 235, 90), width=2)
    tp = Image.new("RGBA", (170, 46), (255, 214, 120, 200)).rotate(-6, expand=True, resample=Image.BICUBIC); c.alpha_composite(tp, (455, 214))
    d = ImageDraw.Draw(c)
    d.text((540, 312), "MI HIJO NO SABE", font=V.font(V.F_BAL, 74), fill=V.NAVY, anchor="mm")
    d.text((540, 392), "ESCRIBIR SU NOMBRE", font=V.font(V.F_BAL, 74), fill=(214, 70, 110), anchor="mm")
    d.rounded_rectangle((340, 432, 740, 482), 25, fill=V.ROSA)
    d.text((540, 459), "¿REPETIRÁ EL AÑO?", font=V.font(V.F_BAL, 32), fill=V.WHITE, anchor="mm")
    # Mateo llorando, mediano, con la nota de la maestra
    V.put(c, "nota", 290, 880, .3, rot=-12)
    V.manuscrito(c, ["Mateo NO", "escribe su", "nombre."], 99, 0, 1, 205, 820, 40, (200, 40, 40), 44, rot=-14)
    V.put(c, "mateo_llora", 600, 840 + 400 * .62, .62)
    V.lagrimas(c, 600, 840, .62, .4)
    # PARTE N a 3/4 de altura (por encima del contador de visitas)
    pw = 400
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((540 - pw / 2, 1062, 540 + pw / 2, 1172), 30, fill=(0, 0, 0, 120))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((540 - pw / 2, 1050, 540 + pw / 2, 1160), 30, fill=V.AZ, outline=V.WHITE, width=7)
    V.text(d, (540, 1105), f"PARTE {n}", 88, V.WHITE, stroke=5)
    c.alpha_composite(V.R.VIG.crop((0, 240, W, 240 + H)))
    c.convert("RGB").save(out, quality=93)

if __name__ == "__main__":
    n = sys.argv[1] if len(sys.argv) > 1 else "1"
    portada(n, os.path.join(V.HERE, f"portada_mateo_parte{n}.jpg"))
