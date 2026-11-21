"""Coche negro de Nitro de perfil con el faro encendido saliendo del morro (no faros frontales encima de un coche de lado)."""
import math
from PIL import Image, ImageDraw, ImageFilter
import render as R

W, H = R.W, R.H
FARO = (-470, 75)    # posición del faro respecto al centro del coche (escala 1, morro a la izquierda)

def coche_faros(c, x, y, s=1.0, u=1.0, flip=False, largo=900, rev=0.0):
    """Dibuja coche_negro centrado en (x, y) con escala s; u = intensidad del faro (0 apagado, 1 encendido).
    flip=True pone el morro a la derecha. El haz sale del faro hacia delante y hacia el suelo."""
    im = R.scaled("coche_negro", s)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    c.alpha_composite(im, (int(x + rev - im.width / 2), int(y - im.height / 2)))
    if u <= .01: return
    dx = -1 if not flip else 1
    hx, hy = x + rev + dx * abs(FARO[0]) * s, y + FARO[1] * s
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(beam)
    tip = hx + dx * largo
    # cono exterior amplio + cono interior intenso + charco de luz en el suelo
    bd.polygon([(hx, hy - 20 * s), (hx, hy + 24 * s), (tip, hy + 380 * s + 160), (tip, hy - 160 * s - 80)], fill=(255, 244, 205, int(150 * u)))
    c.alpha_composite(beam.filter(ImageFilter.GaussianBlur(34)))
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(beam)
    bd.polygon([(hx, hy - 10 * s), (hx, hy + 12 * s), (hx + dx * largo * .75, hy + 170 * s + 60), (hx + dx * largo * .75, hy - 60 * s - 20)], fill=(255, 252, 230, int(190 * u)))
    lo, hi = sorted((hx + dx * 80, tip))
    bd.ellipse((lo, hy + 150 * s, hi, hy + 300 * s + 70), fill=(255, 246, 210, int(120 * u)))
    c.alpha_composite(beam.filter(ImageFilter.GaussianBlur(22)))
    fl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(fl)
    r1 = 130 * s; fd.ellipse((hx - r1, hy - r1 * .7, hx + r1, hy + r1 * .7), fill=(255, 250, 225, int(170 * u)))
    c.alpha_composite(fl.filter(ImageFilter.GaussianBlur(26)))
    d = ImageDraw.Draw(c); r2 = 34 * s
    d.ellipse((hx - r2, hy - r2 * .55, hx + r2, hy + r2 * .55), fill=(255, 255, 240, int(255 * u)))
    for k in (-1, 1):   # destellos en estrella
        d.line((hx - 90 * s, hy + k * 22 * s, hx + 90 * s, hy - k * 22 * s), fill=(255, 255, 235, int(160 * u)), width=max(2, int(4 * s)))
