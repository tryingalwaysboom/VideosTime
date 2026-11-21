"""Fondos acogedores animados: crema con luz cálida, cuarto infantil, mesa con lápices, cielo del cuento."""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .base import W, H, P, rgb


def _grad_vertical(c0, c1, w=W, h=H):
    a = np.linspace(0, 1, h)[:, None, None]
    c0 = np.array(rgb(c0)[:3], float)
    c1 = np.array(rgb(c1)[:3], float)
    arr = (c0 * (1 - a) + c1 * a).repeat(w, axis=1)
    return Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")


@lru_cache(maxsize=8)
def _grano(seed=3):
    rng = np.random.default_rng(seed)
    g = rng.normal(0, 2.0, (H, W, 1)).repeat(3, axis=2)
    return g


def _con_grano(img, fuerza=1.0):
    a = np.array(img.convert("RGB"), float) + _grano() * fuerza
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


@lru_cache(maxsize=4)
def _crema_base(c0, c1):
    return _con_grano(_grad_vertical(c0, c1))


def _manchas_luz(img, t, puntos, opac=0.35):
    """Manchas de luz cálida difusas que derivan despacio (bokeh suave; máscara aparte para no ensuciar de gris)."""
    for i, (x, y, r, col) in enumerate(puntos):
        m = Image.new("L", (W // 4, H // 4), 0)
        dx = 18 * math.sin(t * 0.5 + i * 1.7)
        dy = 14 * math.cos(t * 0.4 + i * 2.3)
        cx, cy, rr = (x + dx) / 4, (y + dy) / 4, r / 4
        ImageDraw.Draw(m).ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=int(255 * opac))
        m = m.filter(ImageFilter.GaussianBlur(22)).resize((W, H), Image.BILINEAR)
        img.paste(Image.new("RGBA", (W, H), rgb(col)), (0, 0), m)
    return img


def crema(t, c0=None, c1=None):
    """Fondo base de marca: degradado crema cálido con grano fino y luces que respiran."""
    img = _crema_base(c0 or P["crema_claro"], c1 or P["crema"]).copy()
    return _manchas_luz(img, t, [(200, 380, 300, "#FFFFFF"), (880, 900, 340, "#FFFBF2"),
                                 (300, 1500, 300, "#FFFFFF")], 0.45)


@lru_cache(maxsize=1)
def _cuarto_estatico():
    img = _grad_vertical("#FFF4E6", "#FCE6CF")
    d = ImageDraw.Draw(img)
    # pared con lunares suaves
    for y in range(60, 1300, 120):
        for x in range((y // 120) % 2 * 60, W, 120):
            d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=rgb("#F9DCC0"))
    # ventana redondeada con cielo del cuento
    d.rounded_rectangle((640, 210, 980, 620), 46, fill=rgb(P["cielo"]), outline=rgb("#F4C8A2"), width=16)
    d.line((810, 220, 810, 610), fill=rgb("#F4C8A2"), width=10)
    d.line((650, 415, 970, 415), fill=rgb("#F4C8A2"), width=10)
    # repisa con libros de colores
    d.rounded_rectangle((90, 520, 470, 548), 12, fill=rgb("#E9B98E"))
    x = 110
    for i, col in enumerate(["#F4ACC4", "#A4CCE4", "#FCD46C", "#ACD4A4", "#FC8C44"]):
        h = 120 + (i * 37) % 50
        d.rounded_rectangle((x, 520 - h, x + 52, 520), 10, fill=rgb(col))
        x += 66
    # suelo de madera clara y alfombra
    d.rectangle((0, 1380, W, H), fill=rgb("#F2D2B0"))
    for y in range(1420, H, 90):
        d.line((0, y, W, y), fill=rgb("#EAC59F"), width=4)
    d.ellipse((60, 1460, 1020, 1800), fill=rgb("#FBE3EC"), outline=rgb("#F4ACC4"), width=10)
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    return _con_grano(img, 0.8)


def cuarto(t):
    """Cuarto infantil cálido (ventana, repisa con libros, alfombra rosa) con nube que pasa y luz que respira."""
    img = _cuarto_estatico().copy()
    d = ImageDraw.Draw(img)
    # nube cruzando la ventana (recortada a la ventana)
    nube = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nube)
    cx = 600 + ((t * 30) % 520)
    for ox, oy, r in ((0, 0, 40), (40, -14, 48), (86, 0, 38)):
        nd.ellipse((cx + ox - r, 330 + oy - r, cx + ox + r, 330 + oy + r), fill=(255, 255, 255, 235))
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rounded_rectangle((656, 226, 964, 604), 34, fill=255)
    img.paste(nube, (0, 0), Image.composite(nube.getchannel("A"), Image.new("L", (W, H), 0), m))
    return _manchas_luz(img, t, [(810, 420, 360, "#FFFBEA"), (300, 1100, 300, "#FFFFFF")], 0.30)


@lru_cache(maxsize=1)
def _mesa_estatica():
    img = _grad_vertical("#FCEBD8", "#F3D2AE")
    d = ImageDraw.Draw(img)
    # vetas de madera suaves
    for i in range(0, H, 46):
        d.line((0, i, W, i + 18), fill=rgb("#EECBA4"), width=3)
    img = img.filter(ImageFilter.GaussianBlur(2))
    d = ImageDraw.Draw(img)
    # lápices de colores en las esquinas (fuera de la zona central)
    cols = ["#FC8C44", "#4A8FDB", "#3AA65A", "#FCD46C", "#F4ACC4", "#8C7CC4"]
    for i, col in enumerate(cols):
        _lapiz(d, 40 + i * 34, 1700 + i * 10, -62 + i * 4, col)
        _lapiz(d, 1020 - i * 30, 180 + i * 16, 118 + i * 5, cols[-1 - i])
    return _con_grano(img, 0.8)


def _lapiz(d, x, y, ang, col, largo=230, ancho=30):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy * ancho / 2, ux * ancho / 2
    x2, y2 = x + ux * largo, y + uy * largo
    d.polygon([(x + px, y + py), (x2 + px, y2 + py), (x2 - px, y2 - py), (x - px, y - py)], fill=rgb(col))
    tx, ty = x2 + ux * 46, y2 + uy * 46
    d.polygon([(x2 + px, y2 + py), (tx, ty), (x2 - px, y2 - py)], fill=rgb("#F6DDB8"))
    d.polygon([(x2 + ux * 32 + px * 0.3, y2 + uy * 32 + py * 0.3), (tx, ty),
               (x2 + ux * 32 - px * 0.3, y2 + uy * 32 - py * 0.3)], fill=rgb(col))


def mesa(t):
    """Mesa de madera clara con lápices de colores en las esquinas y luz cálida que respira."""
    return _manchas_luz(_mesa_estatica().copy(), t, [(540, 900, 560, "#FFFBF0")], 0.40)


@lru_cache(maxsize=1)
def _cielo_estatico():
    img = _grad_vertical("#E6F1FD", P["cielo"])
    d = ImageDraw.Draw(img)
    d.ellipse((-300, 1380, 1380, 2300), fill=rgb(P["pasto"]))
    return _con_grano(img, 0.6)


def cielo(t, sol=(930, 190)):
    """Paisaje del cuento (pág. 22): cielo celeste, colina verde, sol que late (arriba a la derecha, fuera de la franja de texto) y nubes que pasan por detrás."""
    img = _cielo_estatico().copy()
    d = ImageDraw.Draw(img)
    r = 70 + 4 * math.sin(t * 2)
    d.ellipse((sol[0] - r, sol[1] - r, sol[0] + r, sol[1] + r), fill=rgb(P["sol"]))
    for i, (y, v) in enumerate(((620, 22), (900, 15))):
        cx = (t * v + i * 500) % (W + 400) - 200
        for ox, oy, rr in ((0, 0, 50), (55, -18, 62), (115, 0, 48)):
            d.ellipse((cx + ox - rr, y + oy - rr, cx + ox + rr, y + oy + rr), fill=(255, 255, 255, 255))
    return img


def pizarra(t):
    """Pizarra verde suave de la portada con marco de madera; para retos y preguntas."""
    img = crema(t)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((70, 330, 1010, 1330), 48, fill=rgb("#E9B98E"))
    d.rounded_rectangle((100, 360, 980, 1300), 36, fill=rgb("#1F6B66"))
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(capa).ellipse((200, 420, 760, 900), fill=(255, 255, 255, 26))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(60)))
    return img


FONDOS = {"crema": crema, "cuarto": cuarto, "mesa": mesa, "cielo": cielo, "pizarra": pizarra}


def render(t, tipo="crema"):
    """Devuelve el fondo `tipo` (crema | cuarto | mesa | cielo | pizarra) en el instante t, RGBA 1080x1920."""
    return FONDOS[tipo](t)
