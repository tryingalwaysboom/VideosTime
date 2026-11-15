"""Portada fija de la serie (1080x1440, 3:4 como la cuadrícula del perfil). Solo cambia "PARTE N".
Uso: python3 portada.py 1"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter
import render as V

YOFF = int(os.environ.get('YOFF', '0'))
def portada(n, out):
    W, H = 1080, 1440
    full = V.bg("bg_cocina", 0, 0, 1.25, 1.25, 1, .5, .55)
    c = full.crop((0, 240, W, 240 + H)).convert("RGBA")
    V.dark(c, 40) if False else c.alpha_composite(Image.new("RGBA", (W, H), (40, 20, 50, 70)))
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((140, 520, 940, 1300), fill=(255, 200, 140, 110))
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(70)))
    V.put(c, "mateo_llora", 580, 1050 + 180 + YOFF, .9)
    V.lagrimas(c, 580, 878 + YOFF, .9, .4)
    V.put(c, "nota", 200, 1180, .42, rot=-12)
    V.manuscrito(c, ["Mateo NO", "escribe su", "nombre."], 99, 0, 1, 60, 1010, 56, (200, 40, 40), 62, rot=-14)
    d = ImageDraw.Draw(c)
    V.text(d, (540, 120), "MI HIJO NO SABE", 104, V.WHITE, stroke=10)
    V.text(d, (540, 235), "ESCRIBIR SU NOMBRE", 104, V.WHITE, stroke=10)
    d.rounded_rectangle((300, 300, 780, 420), 30, fill=V.ROSA, outline=V.WHITE, width=7)
    V.text(d, (540, 362), "¿REPETIRÁ EL AÑO?", 62, V.OL)
    # PARTE N por encima del contador de visitas (tres cuartos de la altura)
    pw = 520
    d.rounded_rectangle((540 - pw / 2, 1010, 540 + pw / 2, 1150), 36, fill=V.AZ, outline=V.WHITE, width=8)
    V.text(d, (540, 1082), f"PARTE {n}", 112, V.WHITE, stroke=6)
    c.convert("RGB").save(out, quality=93)

if __name__ == "__main__":
    n = sys.argv[1] if len(sys.argv) > 1 else "1"
    portada(n, os.path.join(V.HERE, f"portada_mateo_parte{n}.jpg"))
