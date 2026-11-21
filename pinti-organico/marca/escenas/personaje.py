"""Personajes del libro (mamá, vaca, gato, pato Pepe) animados a partir de sus PNG reales de assets/ilustraciones (nunca redibujados)."""
import math
import os
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .base import ASSETS, rgb, pegar, sombra_suelo, clamp, muelle, rebote_atras, prog

# archivo, cajas de los ojos (px del PNG 700x700, con contorno), base de los pies (y) y eje (x)
FICHAS = {
    "mama": dict(png="pag22_119.png", ojos=[(270, 257, 337, 331), (384, 266, 450, 336)], pies=673, eje=350),
    "vaca": dict(png="pag52_212.png", ojos=[(150, 214, 206, 284), (286, 225, 331, 280)], pies=617, eje=330),
    "gato": dict(png="pag52_214.png", ojos=[(156, 206, 252, 305), (346, 221, 446, 320)], pies=673, eje=330),
    "pepe": dict(png="pag36_163.png", ojos=[(158, 238, 250, 330), (300, 267, 353, 331)], pies=560, eje=420),
}
CONTORNO = "#141414"


@lru_cache(maxsize=8)
def cargar(nombre):
    """PNG real del personaje (RGBA 700x700)."""
    return Image.open(os.path.join(ASSETS, "ilustraciones", FICHAS[nombre]["png"])).convert("RGBA")


@lru_cache(maxsize=16)
def _color_cara(nombre, i):
    """Color de piel alrededor del ojo i (mediana de un anillo justo fuera de la caja)."""
    a = np.array(cargar(nombre)).astype(int)
    x0, y0, x1, y1 = FICHAS[nombre]["ojos"][i]
    m = 8
    anillo = np.concatenate([a[y1:y1 + m, x0:x1].reshape(-1, 4), a[y0 - m:y0, x0:x1].reshape(-1, 4)])
    claro = anillo[(anillo[:, :3].sum(1) > 300) & (anillo[:, 3] > 200)]
    if len(claro) == 0:
        return (255, 255, 255, 255)
    return tuple(int(v) for v in np.median(claro, axis=0))


def _parpadear(img, nombre, v):
    """Cierra los ojos del PNG (v 0..1): parche del color de la cara + arco del mismo contorno."""
    if v <= 0.05:
        return img
    out = img.copy()
    for i, (x0, y0, x1, y1) in enumerate(FICHAS[nombre]["ojos"]):
        w, h = x1 - x0, y1 - y0
        ojo = img.crop((x0, y0, x1, y1))
        piel = _color_cara(nombre, i)
        parche = Image.new("RGBA", (w, h), piel)
        alto = max(1, int(h * (1 - clamp(v))))
        if v < 0.85:
            parche.alpha_composite(ojo.resize((w, alto), Image.LANCZOS), (0, int((h - alto) * 0.6)))
        else:
            s = 4
            arc = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
            ImageDraw.Draw(arc).arc((w * s * 0.1, h * s * 0.2, w * s * 0.9, h * s * 0.85), 20, 160,
                                    fill=rgb(CONTORNO), width=int(max(3, w * 0.11) * s))
            parche.alpha_composite(arc.resize((w, h), Image.LANCZOS))
        # máscara elíptica suave para no tocar pestañas ni cejas
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).ellipse((1, 1, w - 2, h - 2), fill=255)
        out.paste(parche, (x0, y0), m.filter(ImageFilter.GaussianBlur(1.5)))
    return out


def parpadeo_auto(t, semilla=0.0, cada=3.6):
    """Parpadeo natural (0..1) de ~0,16 s cada `cada` s; desfasa personajes con `semilla`."""
    f = (t + semilla * 1.3) % cada
    u = (f - (cada - 0.2)) / 0.16
    return 0.0 if u < 0 or u > 1 else math.sin(math.pi * u)


def dibujar(lienzo, t, nombre, x, y_pies, alto=520, respira=True, salto=0.0, squash=0.0, inclina=0.0,
            vaiven=0.0, voltear=False, parpadeo=None, semilla=0.0, sombra=True, alfa=1.0):
    """Dibuja el personaje con los pies en (x, y_pies): respiración, salto (px), squash (+aplasta / -estira), inclinación (°) y vaivén (°)."""
    f = FICHAS[nombre]
    src = cargar(nombre)
    v = parpadeo_auto(t, semilla) if parpadeo is None else parpadeo
    src = _parpadear(src, nombre, v)
    k = alto / (f["pies"] - 26)
    r = 0.014 * math.sin(t * 2 * math.pi * 0.8 + semilla) if respira else 0.0
    sx, sy = k * (1 - r * 0.6 + squash * 0.8), k * (1 + r - squash)
    img = src.resize((max(1, int(src.width * sx)), max(1, int(src.height * sy))), Image.LANCZOS)
    pax, pay = f["eje"] * sx, f["pies"] * sy
    if voltear:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        pax = img.width - pax
    ang = inclina + vaiven * math.sin(t * 2 * math.pi * 0.7 + semilla)
    if abs(ang) > 0.05:
        pad = max(img.size)
        g = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
        g.paste(img, (pad, pad))
        img = g.rotate(ang, resample=Image.BICUBIC, center=(pax + pad, pay + pad))
        pax, pay = pax + pad, pay + pad
    if alfa < 1:
        img.putalpha(img.getchannel("A").point(lambda a: int(a * alfa)))
    if sombra:
        lejos = clamp(salto / max(1.0, alto * 0.5))
        sombra_suelo(lienzo, x, y_pies + 4, alto * 0.55 * (1 - 0.35 * lejos), opacidad=0.18 * (1 - 0.5 * lejos) * alfa)
    pegar(lienzo, img, x - pax, y_pies - salto - pay)
    return lienzo


def saltitos(t, t0, t1, altura=60, frec=2.4):
    """Saltitos entre t0 y t1: devuelve (salto_px, squash) con squash al tocar suelo."""
    if not (t0 <= t <= t1):
        return 0.0, 0.0
    fase = ((t - t0) * frec) % 1.0
    s = math.sin(math.pi * fase)
    return altura * s, (0.07 * (1 - s) ** 6) - 0.03 * s


def grito(t, t0, t1, fuerza=0.10):
    """Squash & stretch de un grito (mugido, ¡CUAC!): estira al empezar y vibra; pásalo a `squash` (negativo = estira)."""
    if t < t0 or t > t1 + 0.6:
        return 0.0
    if t <= t1:
        return -fuerza * rebote_atras(prog(t, t0, t0 + 0.18)) + 0.015 * math.sin((t - t0) * 2 * math.pi * 9)
    return -fuerza * 0.0 + 0.10 * muelle(t, t1, frec=3.0, amort=7.0)


def ondas(lienzo, t, cx, cy, ancho=420, color="#9CC8E8", n=3, periodo=1.6):
    """Ondas de agua que se abren alrededor de (cx, cy) (charquito de Pepe); se dibujan detrás del personaje."""
    d = ImageDraw.Draw(lienzo)
    for i in range(n):
        u = ((t / periodo) + i / n) % 1.0
        w = ancho * (0.55 + 0.6 * u)
        h = w * 0.16
        op = int(200 * (1 - u))
        d.ellipse((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), outline=rgb(color, op), width=6)
    return lienzo


def salpicadura(lienzo, t, cx, cy, t0, color="#9CC8E8", n=7):
    """Gotitas que saltan en arco desde (cx, cy) en t0 (¡CUAC!, chapoteo)."""
    u = (t - t0) / 0.5
    if not 0 <= u <= 1:
        return lienzo
    d = ImageDraw.Draw(lienzo)
    for i in range(n):
        a = math.radians(200 + i * 140 / (n - 1))
        vx, vy = 260 * math.cos(a), 420 * math.sin(a)
        x, y = cx + vx * u, cy + vy * u + 900 * u * u
        r = 13 * (1 - 0.6 * u)
        d.ellipse((x - r, y - r * 1.2, x + r, y + r * 1.2), fill=rgb(color, int(230 * (1 - u))))
    return lienzo
