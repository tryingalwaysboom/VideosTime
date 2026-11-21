"""Base común de la biblioteca Pinti: lienzo, paleta, fuentes, easings, sombras suaves y cámara viva."""
import math
import os
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# --- Rutas -----------------------------------------------------------------
MARCA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAIZ = os.path.dirname(MARCA)                      # pinti-organico/
ASSETS = os.path.join(RAIZ, "assets")
FUENTES = os.path.join(MARCA, "fuentes")

# --- Lienzo y zona segura (ver guia.md) -------------------------------------
W, H, FPS = 1080, 1920, 30
SEGURA_ARRIBA = 120        # nada importante por encima
SEGURA_ABAJO = 1920 - 320  # nada importante por debajo de y=1600
SEGURA_IZQ = 60
SEGURA_DER = 1080 - 140    # iconos de TikTok/Reels a la derecha
TEXTO_Y0, TEXTO_Y1 = 250, 1440  # franja de texto de los guiones

# --- Paleta (hex muestreados de los assets reales) -------------------------
P = {
    # Pinti (assets/pinti.png)
    "pinti": "#FC8C44", "pinti_sombra": "#CC7C3C", "contorno": "#141424",
    "zapato": "#6C4C94", "mejilla": "#F4ACC4", "estrella": "#FCDC6C", "blanco": "#F7F4F0",
    # Libro (páginas)
    "tinta": "#3C342C", "papel": "#FFFDF8", "borde_pagina": "#F4BC94", "crema_tarjeta": "#FCF4E4",
    "b_naranja": "#E4542F", "d_azul": "#4A8FDB", "punto_verde": "#3AA65A", "badge_azul": "#4A8FDB",
    "estrella_oro": "#D8AC44",
    # Tarjetas de sílaba (pág. 21): (relleno, borde)
    "sil_melocoton": ("#FCF4E4", "#F4BC94"), "sil_azul": ("#ECF4FC", "#A4CCE4"),
    "sil_verde": ("#ECFCEC", "#ACD4A4"), "sil_amarillo": ("#FCF4DC", "#F4C454"),
    "sil_rosa": ("#FCECF4", "#E4ACC4"),
    # Cuento (pág. 22) y portada
    "cielo": "#DCECFC", "pasto": "#CCE4C4", "sol": "#FCD46C", "mama_rosa": "#F4ACC4",
    "portada_verde": "#0F5C5C", "portada_amarillo": "#FCDC4C", "portada_naranja": "#FC8C5C",
    # Fondos cálidos de vídeo (derivados, no del libro)
    "crema_claro": "#FFF7EC", "crema": "#FDEBD6", "melocoton_suave": "#FBD9C0",
}
SILABAS_CICLO = ["sil_melocoton", "sil_azul", "sil_verde", "sil_amarillo", "sil_rosa"]


def rgb(c, a=255):
    """Convierte '#RRGGBB' a tupla RGBA."""
    c = c.lstrip("#")
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), a)


@lru_cache(maxsize=64)
def fuente(tam, peso=700):
    """Fuente de marca Fredoka (500/600/700); cae a Poppins Bold si falta."""
    p = os.path.join(FUENTES, f"Fredoka-{peso}.ttf")
    if not os.path.exists(p):
        p = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
    return ImageFont.truetype(p, int(tam))


# --- Easings ---------------------------------------------------------------
def clamp(u, a=0.0, b=1.0):
    """Limita u a [a, b]."""
    return max(a, min(b, u))


def prog(t, t0, t1):
    """Progreso lineal 0..1 de t entre t0 y t1."""
    return clamp((t - t0) / max(1e-6, t1 - t0))


def suave(u):
    """Ease in-out (smoothstep)."""
    u = clamp(u)
    return u * u * (3 - 2 * u)


def sale(u, p=3):
    """Ease out (desacelera al llegar)."""
    u = clamp(u)
    return 1 - (1 - u) ** p


def rebote_atras(u, s=1.9):
    """Ease out back: se pasa un poco y vuelve (entradas pop)."""
    u = clamp(u) - 1
    return 1 + (s + 1) * u ** 3 + s * u ** 2


def muelle(t, t0, frec=3.2, amort=6.0):
    """Oscilación amortiguada que empieza en t0 (0 antes); útil para squash tras un golpe."""
    if t < t0:
        return 0.0
    d = t - t0
    return math.exp(-amort * d) * math.sin(2 * math.pi * frec * d)


def lerp(a, b, u):
    """Interpolación lineal."""
    return a + (b - a) * u


# --- Utilidades de composición --------------------------------------------
def pegar(lienzo, capa, x, y):
    """Pega una capa RGBA con su alfa en (x, y) (enteros), recortando fuera del lienzo."""
    x, y = int(round(x)), int(round(y))
    sx0, sy0 = max(0, -x), max(0, -y)
    dx0, dy0 = max(0, x), max(0, y)
    w = min(capa.width - sx0, lienzo.width - dx0)
    h = min(capa.height - sy0, lienzo.height - dy0)
    if w <= 0 or h <= 0:
        return lienzo
    lienzo.alpha_composite(capa.crop((sx0, sy0, sx0 + w, sy0 + h)), (dx0, dy0))
    return lienzo


def sombra_suave(capa, radio=18, opacidad=0.22, color="#8A5A3C"):
    """Sombra cálida y difusa de una capa (nunca sombra dura): devuelve capa RGBA con margen = 2*radio."""
    m = radio * 2
    a = capa.getchannel("A").point(lambda v: int(v * opacidad))
    base = Image.new("L", (capa.width + 2 * m, capa.height + 2 * m), 0)
    base.paste(a, (m, m))
    base = base.filter(ImageFilter.GaussianBlur(radio))
    out = Image.new("RGBA", base.size, rgb(color, 0))
    col = Image.new("RGBA", base.size, rgb(color))
    out.paste(col, (0, 0), base)
    return out


def sombra_suelo(lienzo, cx, cy, ancho, opacidad=0.18, color="#8A5A3C"):
    """Elipse de sombra difusa bajo un personaje (contacto con el suelo)."""
    ancho = max(4, int(ancho))
    alto = max(3, int(ancho * 0.18))
    pad = 24
    m = Image.new("L", (ancho + 2 * pad, alto + 2 * pad), 0)
    ImageDraw.Draw(m).ellipse((pad, pad, pad + ancho, pad + alto), fill=int(255 * opacidad))
    m = m.filter(ImageFilter.GaussianBlur(9))
    capa = Image.new("RGBA", m.size, rgb(color, 0))
    capa.paste(Image.new("RGBA", m.size, rgb(color)), (0, 0), m)
    return pegar(lienzo, capa, cx - m.width / 2, cy - m.height / 2)


def rect_redondeado(tam, radio, relleno, borde=None, grosor=0, escala=2):
    """Rectángulo redondeado antialias (supermuestreo) como capa RGBA."""
    w, h = int(tam[0]), int(tam[1])
    im = Image.new("RGBA", (w * escala, h * escala), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w * escala - 1, h * escala - 1), radio * escala,
                        fill=rgb(relleno) if isinstance(relleno, str) else relleno,
                        outline=(rgb(borde) if borde else None), width=int(grosor * escala))
    return im.resize((w, h), Image.LANCZOS)


def camara_viva(frame, t, zoom=1.0, deriva=6.0, respira=0.008, foco=(0.5, 0.5)):
    """Cámara viva: aplica zoom + respiración + deriva lenta al fotograma (nunca plano quieto ni bordes vacíos)."""
    fx, fy = foco[0] * W, foco[1] * H
    # zoom mínimo para que la deriva y la respiración nunca dejen ver el borde (saldría negro)
    mx = max(40.0, min(fx, W - fx))
    my = max(40.0, min(fy, H - fy))
    z_min = max(1 + (deriva + 2) / mx, 1 + (deriva * 0.6 + 2) / my) / (1 - respira)
    z = max(zoom, z_min) * (1 + respira * math.sin(t * 2 * math.pi / 3.7))
    dx = deriva * math.sin(t * 2 * math.pi / 5.3)
    dy = deriva * 0.6 * math.cos(t * 2 * math.pi / 6.1)
    # punto de salida (x,y) <- origen ((x - fx)/z + fx - dx, ...)
    a, e = 1 / z, 1 / z
    c = fx - fx / z - dx / z
    f = fy - fy / z - dy / z
    return frame.transform(frame.size, Image.AFFINE, (a, 0, c, 0, e, f), resample=Image.BILINEAR)


def aplanar(frame, color=None):
    """Pasa el fotograma a RGB sobre crema (nunca sobre negro): úsalo siempre antes de escribir el frame al vídeo."""
    fondo = Image.new("RGBA", frame.size, rgb(color or P["crema_claro"]))
    fondo.alpha_composite(frame.convert("RGBA"))
    return fondo.convert("RGB")


def nuevo_lienzo(color=None):
    """Lienzo RGBA 1080x1920 (transparente o del color dado)."""
    return Image.new("RGBA", (W, H), rgb(color) if color else (0, 0, 0, 0))


def guia_zona_segura(lienzo):
    """Superpone la zona segura (solo para pruebas/revisión, nunca en el vídeo)."""
    d = ImageDraw.Draw(lienzo)
    d.rectangle((0, 0, W, SEGURA_ARRIBA), outline=(255, 0, 0, 255), width=3)
    d.rectangle((0, SEGURA_ABAJO, W, H), outline=(255, 0, 0, 255), width=3)
    d.line((SEGURA_DER, 0, SEGURA_DER, H), fill=(255, 0, 0, 160), width=2)
    d.line((0, TEXTO_Y0, W, TEXTO_Y0), fill=(0, 140, 255, 160), width=2)
    d.line((0, TEXTO_Y1, W, TEXTO_Y1), fill=(0, 140, 255, 160), width=2)
    return lienzo
