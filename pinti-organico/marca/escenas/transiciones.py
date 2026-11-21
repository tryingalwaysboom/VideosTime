"""Transiciones sin negro: barrido de crayón, círculo que se abre, deslizamiento con rebote y fundido cruzado entre planos."""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .base import W, H, P, rgb, suave, sale, clamp


def cruzado(a, b, u):
    """Fundido cruzado entre dos fotogramas (nunca pasa por negro)."""
    return Image.blend(a.convert("RGBA"), b.convert("RGBA"), suave(u))


def barrido_crayon(a, b, u, color=None, grosor=260):
    """Una pasada de crayón naranja ondulada cruza la pantalla en diagonal y descubre el plano b detrás."""
    u = clamp(u)
    color = rgb(color or P["pinti"])
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    frente = -400 + (W + H + 800) * sale(u, 2)
    # todo lo que queda detrás del frente (x + y < frente) es b
    pts = [(-10, -10)]
    for i in range(0, 41):
        y = -10 + i * (H + 20) / 40
        x = frente - y + 30 * math.sin(i * 0.9)
        pts.append((x, y))
    pts.append((-10, H + 10))
    d.polygon(pts, fill=255)
    out = Image.composite(b.convert("RGBA"), a.convert("RGBA"), m)
    # la banda del crayón sobre el frente
    banda = Image.new("L", (W, H), 0)
    db = ImageDraw.Draw(banda)
    linea = [(x, y) for x, y in pts[1:-1]]
    db.line(linea, fill=255, width=grosor, joint="curve")
    banda = banda.filter(ImageFilter.GaussianBlur(2))
    if 0 < u < 1:
        capa = Image.new("RGBA", (W, H), color)
        # textura de cera
        rng = np.random.default_rng(7)
        tex = (rng.random((H // 4, W // 4)) * 18).astype(np.uint8)
        tex = Image.fromarray(tex).resize((W, H), Image.BILINEAR)
        banda = Image.fromarray(np.clip(np.array(banda, int) - np.array(tex, int), 0, 255).astype(np.uint8))
        out.paste(capa, (0, 0), banda)
    return out


def circulo(a, b, u, cx=540, cy=900):
    """El plano b aparece dentro de un círculo que crece desde (cx, cy), con aro naranja suave."""
    u = clamp(u)
    r = sale(u, 3) * math.hypot(W, H)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    out = Image.composite(b.convert("RGBA"), a.convert("RGBA"), m.filter(ImageFilter.GaussianBlur(3)))
    if 0 < u < 1:
        ImageDraw.Draw(out).ellipse((cx - r, cy - r, cx + r, cy + r), outline=rgb(P["pinti"]), width=18)
    return out


def deslizar(a, b, u, direccion="izq"):
    """b empuja a a fuera con un deslizamiento con rebote suave (izq | der | arriba)."""
    u = clamp(u)
    e = sale(u, 3)
    out = b.convert("RGBA").copy()  # base b: sin rendijas vacías por redondeo
    if direccion in ("izq", "der"):
        s = -1 if direccion == "izq" else 1
        out.paste(a.convert("RGBA"), (int(s * e * W), 0))
        out.paste(b.convert("RGBA"), (int(s * (e - 1) * W), 0))
    else:
        out.paste(a.convert("RGBA"), (0, int(-e * H)))
        out.paste(b.convert("RGBA"), (0, int((1 - e) * H)))
    return out


def render(a, b, u, tipo="barrido_crayon", **kw):
    """Aplica la transición `tipo` (cruzado | barrido_crayon | circulo | deslizar) entre los fotogramas a y b con progreso u."""
    return {"cruzado": cruzado, "barrido_crayon": barrido_crayon, "circulo": circulo, "deslizar": deslizar}[tipo](a, b, u, **kw)
