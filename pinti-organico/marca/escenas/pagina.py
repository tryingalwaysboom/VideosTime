"""Páginas reales del libro y portada: push-in, lupa, recortes de la página y entrada de portada con tilt 3D."""
import math
import os
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .base import ASSETS, W, H, P, rgb, pegar, sombra_suave, suave, sale, clamp, lerp, rect_redondeado

PAG_W, PAG_H = 1085, 1532  # tamaño real de assets/paginas/*.jpg


@lru_cache(maxsize=8)
def cargar(n):
    """Carga assets/paginas/pagina-NN.jpg (n=1..88) como RGBA."""
    return Image.open(os.path.join(ASSETS, "paginas", f"pagina-{int(n):02d}.jpg")).convert("RGBA")


@lru_cache(maxsize=1)
def portada():
    """Carga assets/portada.jpg como RGBA."""
    return Image.open(os.path.join(ASSETS, "portada.jpg")).convert("RGBA")


@lru_cache(maxsize=16)
def _hoja(n_o_portada, ancho, radio=26):
    """Página escalada con esquinas redondeadas y su sombra cálida (cacheada por ancho)."""
    src = portada() if n_o_portada == "portada" else cargar(n_o_portada)
    k = ancho / src.width
    img = src.resize((int(ancho), int(src.height * k)), Image.LANCZOS)
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, img.width - 1, img.height - 1), radio, fill=255)
    img.putalpha(m)
    return img, sombra_suave(img, radio=24, opacidad=0.28)


def render(lienzo, t, n, t0=0.0, t1=3.0, zoom0=1.0, zoom1=1.35, foco=(0.5, 0.5), centro=(540, 900),
           ancho=860):
    """Muestra la página n con push-in continuo de zoom0 a zoom1 entre t0 y t1 hacia `foco` (fracción de la página)."""
    u = suave(prog_local(t, t0, t1))
    z = lerp(zoom0, zoom1, u)
    # tras t1 sigue empujando muy despacio: nunca quieta
    if t > t1:
        z *= 1 + 0.01 * (t - t1)
    src = cargar(n)
    aw = ancho * z
    # recorte de la zona visible para no escalar la página entera a tamaños enormes
    k = aw / src.width
    fx, fy = foco[0] * src.width, foco[1] * src.height
    # el foco se desplaza hacia el centro de pantalla a medida que hacemos zoom
    cx, cy = centro
    ox = cx - lerp(src.width / 2, fx, u) * k
    oy = cy - lerp(src.height / 2, fy, u) * k
    if z <= 1.05:
        hoja, sombra = _hoja(n, int(round(aw / 10) * 10))
        pegar(lienzo, sombra, ox - 48, oy - 48 + 14)
        pegar(lienzo, hoja, ox, oy)
        return lienzo
    # zoom grande: recorta la región visible y la escala
    x0 = max(0, (-ox) / k)
    y0 = max(0, (-oy) / k)
    x1 = min(src.width, (W - ox) / k)
    y1 = min(src.height, (H - oy) / k)
    if x1 <= x0 or y1 <= y0:
        return lienzo
    trozo = src.crop((int(x0), int(y0), int(math.ceil(x1)), int(math.ceil(y1))))
    tw, th = int(round((int(math.ceil(x1)) - int(x0)) * k)), int(round((int(math.ceil(y1)) - int(y0)) * k))
    trozo = trozo.resize((max(1, tw), max(1, th)), Image.LANCZOS)
    pegar(lienzo, trozo, ox + int(x0) * k, oy + int(y0) * k)
    return lienzo


def prog_local(t, t0, t1):
    """Progreso 0..1 entre t0 y t1."""
    return clamp((t - t0) / max(1e-6, t1 - t0))


def a_pantalla(px, py, t, t0, t1, zoom0=1.0, zoom1=1.35, foco=(0.5, 0.5), centro=(540, 900), ancho=860):
    """Convierte un punto (px, py) en píxeles de la página a coordenadas de pantalla con el mismo push-in de render()."""
    src_w, src_h = PAG_W, PAG_H
    u = suave(prog_local(t, t0, t1))
    z = lerp(zoom0, zoom1, u)
    if t > t1:
        z *= 1 + 0.01 * (t - t1)
    k = ancho * z / src_w
    fx, fy = foco[0] * src_w, foco[1] * src_h
    ox = centro[0] - lerp(src_w / 2, fx, u) * k
    oy = centro[1] - lerp(src_h / 2, fy, u) * k
    return ox + px * k, oy + py * k, k


def recorte(n, caja, ancho=None, radio=22, fondo=None):
    """Recorta una zona real de la página n (caja en px de la página) como tarjeta redondeada RGBA."""
    img = cargar(n).crop(caja)
    if ancho:
        img = img.resize((int(ancho), int(img.height * ancho / img.width)), Image.LANCZOS)
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, img.width - 1, img.height - 1), radio, fill=255)
    img.putalpha(m)
    return img


def lupa(lienzo, cx, cy, fuente_img, fx, fy, radio=150, aumento=1.8, aparicion=1.0, latido=0.0):
    """Lupa redonda en (cx, cy) que amplía `fuente_img` (el fotograma ya compuesto) alrededor de (fx, fy)."""
    if aparicion <= 0:
        return lienzo
    r = radio * (0.4 + 0.6 * sale(aparicion)) * (1 + 0.04 * latido)
    rr = int(r)
    src_r = rr / aumento
    trozo = fuente_img.crop((int(fx - src_r), int(fy - src_r), int(fx + src_r), int(fy + src_r)))
    trozo = trozo.resize((2 * rr, 2 * rr), Image.LANCZOS)
    m = Image.new("L", (2 * rr, 2 * rr), 0)
    ImageDraw.Draw(m).ellipse((0, 0, 2 * rr - 1, 2 * rr - 1), fill=255)
    trozo.putalpha(m)
    sombra = sombra_suave(trozo, radio=20, opacidad=0.35)
    pegar(lienzo, sombra, cx - rr - 40, cy - rr - 40 + 12)
    pegar(lienzo, trozo, cx - rr, cy - rr)
    d = ImageDraw.Draw(lienzo)
    aro = max(10, int(r * 0.09))
    d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=rgb(P["pinti"]), width=aro)
    # mango de crayón naranja (sin contorno navy)
    a = math.radians(45)
    x0, y0 = cx + rr * math.cos(a), cy + rr * math.sin(a)
    d.line((x0, y0, x0 + r * 0.75, y0 + r * 0.75), fill=rgb(P["pinti_sombra"]), width=int(aro * 2.2))
    # brillo
    d.arc((cx - rr * 0.75, cy - rr * 0.75, cx + rr * 0.75, cy + rr * 0.75), 200, 245, fill=(255, 255, 255, 170),
          width=max(4, aro // 2))
    return lienzo


def portada_entra(lienzo, t, t0, dur=0.55, centro=(540, 860), ancho=700, desde="abajo", respira=True, tilt=True):
    """La portada entra deslizándose (tilt 3D ligero salvo tilt=False: entonces plano, pop 0,96→1, sin girar) y luego respira 1,00↔1,03."""
    u = clamp((t - t0) / dur)
    if u <= 0:
        return lienzo
    e = sale(u, 3)
    esc = 1.0
    if respira and u >= 1:
        esc = 1.015 + 0.015 * math.sin((t - t0 - dur) * 2 * math.pi / 2.4)
    if not tilt:
        esc *= lerp(0.96, 1.0, e)
    hoja, sombra = _hoja("portada", int(round(ancho * esc / 4) * 4), radio=30)
    if not tilt:  # entrada en plano: solo slide + escala, nada gira (ep. ASMR)
        dy = (1 - e) * (H * 0.75 if desde == "abajo" else -H * 0.75)
        pegar(lienzo, sombra, centro[0] - sombra.width / 2, centro[1] - sombra.height / 2 + dy + 16)
        pegar(lienzo, hoja, centro[0] - hoja.width / 2, centro[1] - hoja.height / 2 + dy)
        return lienzo
    # tilt 3D: perspectiva que pasa de ~14° a 0°
    ang = (1 - e) * 14
    if ang > 0.3:
        hoja = _perspectiva(hoja, ang)
        sombra = _perspectiva(sombra, ang)
    dy = (1 - e) * (H * 0.75 if desde == "abajo" else -H * 0.75)
    rot = (1 - e) * (-6)
    if abs(rot) > 0.2:
        hoja = hoja.rotate(rot, resample=Image.BICUBIC, expand=True)
        sombra = sombra.rotate(rot, resample=Image.BICUBIC, expand=True)
    x = centro[0] - hoja.width / 2
    y = centro[1] - hoja.height / 2 + dy
    pegar(lienzo, sombra, centro[0] - sombra.width / 2, centro[1] - sombra.height / 2 + dy + 16)
    pegar(lienzo, hoja, x, y)
    return lienzo


def _perspectiva(img, ang):
    """Inclina la imagen hacia atrás (eje X) ang grados con una transformación de perspectiva."""
    w, h = img.size
    s = math.sin(math.radians(ang)) * 0.5
    arriba = w * s * 0.5
    src = [(arriba, 0), (w - arriba, 0), (w, h), (0, h)]
    dst = [(0, 0), (w, 0), (w, h), (0, h)]
    coeffs = _coefs(dst, src)
    return img.transform((w, h), Image.PERSPECTIVE, coeffs, Image.BICUBIC)


def _coefs(pa, pb):
    m = []
    for (x, y), (X, Y) in zip(pa, pb):
        m.append([x, y, 1, 0, 0, 0, -X * x, -X * y])
        m.append([0, 0, 0, x, y, 1, -Y * x, -Y * y])
    A = np.array(m, float)
    B = np.array(pb, float).reshape(8)
    return np.linalg.solve(A, B).tolist()


def camara(lienzo, t, pag, foco, escala, centro=(540, 900), sombra=True, nitidez=True):
    """Cámara libre sobre una página: `foco` (px de la página) queda en `centro` a `escala` px de pantalla por px de página; devuelve a_pantalla(px, py)."""
    src = cargar(pag) if not isinstance(pag, Image.Image) else pag
    fx, fy = foco
    ox, oy = centro[0] - fx * escala, centro[1] - fy * escala
    a_pant = lambda px, py: (ox + px * escala, oy + py * escala)
    if escala * src.width <= W * 1.02 and sombra:
        aw = int(round(src.width * escala))
        m = Image.new("L", (aw, int(src.height * escala)), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, m.width - 1, m.height - 1), 26, fill=255)
        hoja = src.resize(m.size, Image.LANCZOS)
        hoja.putalpha(m)
        pegar(lienzo, sombra_suave(hoja, radio=24, opacidad=0.26), ox - 48, oy - 48 + 14)
        pegar(lienzo, hoja, ox, oy)
        return a_pant
    x0, y0 = max(0, -ox / escala), max(0, -oy / escala)
    x1, y1 = min(src.width, (W - ox) / escala), min(src.height, (H - oy) / escala)
    if x1 <= x0 or y1 <= y0:
        return a_pant
    ix0, iy0, ix1, iy1 = int(x0), int(y0), int(math.ceil(x1)), int(math.ceil(y1))
    trozo = src.crop((ix0, iy0, ix1, iy1)).resize(
        (max(1, int(round((ix1 - ix0) * escala))), max(1, int(round((iy1 - iy0) * escala)))), Image.LANCZOS)
    if nitidez and escala > 1.6:  # macro: devuelve borde a los puntos sin inventar detalle
        trozo = trozo.filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=2))
    pegar(lienzo, trozo, ox + ix0 * escala, oy + iy0 * escala)
    return a_pant


def mover_camara(t, claves):
    """Interpola (foco, escala) entre fotogramas clave [(t, (fx, fy), escala), ...] con ease in-out: paneos y zooms sin giros."""
    if t <= claves[0][0]:
        return claves[0][1], claves[0][2]
    for (ta, fa, ea), (tb, fb, eb) in zip(claves, claves[1:]):
        if t <= tb:
            u = suave(prog_local(t, ta, tb))
            # zoom en escala logarítmica para que se sienta uniforme
            esc = math.exp(lerp(math.log(ea), math.log(eb), u))
            return (lerp(fa[0], fb[0], u), lerp(fa[1], fb[1], u)), esc
    return claves[-1][1], claves[-1][2]


# Pág. 20: zonas medidas (px de la página)
PAG20_MAMA_DIBUJO = (330, 1210, 460, 1450)      # mamá para colorear
PAG20_SEMILLAS_ROSA = [(380, 1300), (380, 1400), (389, 1222)]
PAG20_SEMILLAS_LAZO = [(366, 1245), (402, 1245)]
PAG20_ESTRELLAS = [(856, 1345), (911, 1345), (966, 1345)]   # centros de las 3 estrellas "¡Lo logré!" (r ≈ 16)


def mascara_zona(pag, caja, semillas):
    """Máscara (L) de las zonas cerradas del dibujo de la página que contienen las semillas (acepta listas)."""
    return _mascara_zona(pag, tuple(caja), tuple(tuple(s) for s in semillas))


@lru_cache(maxsize=16)
def _mascara_zona(pag, caja, semillas):
    """Máscara (L, tamaño de la página) de las zonas cerradas del dibujo que contienen las semillas (para colorear sin salirse)."""
    from scipy import ndimage as nd
    g = np.array(cargar(pag).convert("L"))
    x0, y0, x1, y1 = caja
    claro = g[y0:y1, x0:x1] > 170
    lab, _ = nd.label(claro)
    ids = {lab[sy - y0, sx - x0] for sx, sy in semillas if lab[sy - y0, sx - x0] > 0}
    m = np.isin(lab, list(ids))
    m = nd.binary_dilation(m, iterations=1)
    out = np.zeros_like(g, dtype=np.uint8)
    out[y0:y1, x0:x1] = m * 255
    return Image.fromarray(out)


def colorear(img_pagina, mascara, color, u, caja, desde="abajo", rayado=14):
    """Colorea con crayón (rayado de vaivén que se va llenando) la zona `mascara` de la página hasta el progreso u; respeta el contorno negro."""
    if u <= 0:
        return img_pagina
    x0, y0, x1, y1 = caja
    hh = y1 - y0
    frente = y1 - hh * u * 1.15 if desde == "abajo" else y0 + hh * u * 1.15
    yy, xx = np.mgrid[0:img_pagina.height, 0:img_pagina.width]
    detras = (yy >= frente) if desde == "abajo" else (yy <= frente)
    cerca = np.abs(yy - frente) < hh * 0.12
    rayas = ((xx + yy * 0.6) % rayado) < rayado * 0.62
    alfa = np.where(detras, 0.92, 0.0)
    alfa = np.where(cerca & ~detras & rayas, 0.85, alfa)      # el frente avanza en rayas de crayón
    rng = np.random.default_rng(3)
    grano = rng.random((img_pagina.height // 3 + 1, img_pagina.width // 3 + 1))
    grano = np.kron(grano, np.ones((3, 3)))[:img_pagina.height, :img_pagina.width]
    alfa = alfa * (0.86 + 0.14 * grano) * (np.array(mascara) / 255.0)
    base = np.array(img_pagina.convert("RGBA")).astype(float)
    col = np.array(rgb(color)[:3], float)
    mult = base[..., :3] * (col / 255.0)          # multiplicar: el contorno negro sigue negro
    base[..., :3] = base[..., :3] * (1 - alfa[..., None]) + mult * alfa[..., None]
    return Image.fromarray(base.astype(np.uint8), "RGBA")
