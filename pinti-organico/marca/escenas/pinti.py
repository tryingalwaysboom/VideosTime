"""Pinti animado a partir de assets/pinti.png (nunca redibujado): respiración, rebote, saludo, parpadeo, mirada, poses."""
import math
import os
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .base import ASSETS, P, rgb, pegar, sombra_suelo, suave, clamp, muelle

# Geometría medida sobre pinti.png (289x420). Coordenadas en píxeles del PNG original.
SRC_W, SRC_H = 289, 420
BRAZO_IZQ_CAJA = (0, 88, 84, 240)          # brazo levantado (el que saluda), a la izquierda de la imagen
HOMBRO_IZQ = (76, 222)                      # pivote del saludo
BRAZO_DER_CAJA = (226, 236, 289, 332)       # brazo bajado de la derecha
HOMBRO_DER = (222, 240)                     # pivote para levantarlo (celebra / señala)
OJO_IZQ = (110, 157, 141, 197)              # caja de cada ojo (con contorno)
OJO_DER = (163, 161, 195, 201)
PIES_Y = 418                                # base de los zapatos
CENTRO_X = 148                              # eje del cuerpo


@lru_cache(maxsize=1)
def _fuente():
    return Image.open(os.path.join(ASSETS, "pinti.png")).convert("RGBA")


def _mascara_caja(img, caja, invertir=False):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rectangle(caja, fill=255)
    if invertir:
        m = Image.eval(m, lambda v: 255 - v)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), m)
    return out


def _bordes_cuerpo(alfa):
    """Bordes izq/der del cuerpo por fila, interpolando a través de la unión con los brazos."""
    L = np.full(SRC_H, -1.0)
    R = np.full(SRC_H, -1.0)
    for y in range(SRC_H):
        fila = alfa[y]
        if not fila[CENTRO_X]:
            continue
        x = CENTRO_X
        while x > 0 and fila[x - 1]:
            x -= 1
        L[y] = x
        x = CENTRO_X
        while x < SRC_W - 1 and fila[x + 1]:
            x += 1
        R[y] = x
    # Uniones: el brazo izq se pega al cuerpo entre y=190 y 238; el der entre 214 y 260.
    for arr, (ya, yb) in ((L, (190, 238)), (R, (214, 260))):
        va, vb = arr[ya], arr[yb]
        for y in range(ya, yb + 1):
            arr[y] = va + (vb - va) * (y - ya) / (yb - ya)
    return L, R


@lru_cache(maxsize=1)
def _capas():
    """Separa el PNG en cuerpo, brazo izquierdo y brazo derecho por el borde real del cuerpo (sin redibujar)."""
    a = np.array(_fuente())
    alfa = a[:, :, 3] > 100
    L, R = _bordes_cuerpo(alfa)
    yy, xx = np.mgrid[0:SRC_H, 0:SRC_W]
    Lc = L[:, None]
    Rc = R[:, None]
    zona_i = (yy >= 88) & (yy <= 240) & (xx < Lc) & (xx < 92)
    zona_d = (yy >= 214) & (yy <= 335) & (xx > Rc) & (xx > 210)
    # Limpia el halo semitransparente pegado al corte (si no, al rotar deja una línea fantasma).
    cerca_i = (xx >= Lc - 3)
    cerca_d = (xx <= Rc + 3)
    halo = a[:, :, 3] < 200
    brazo_i = np.where((zona_i & ~(cerca_i & halo))[..., None], a, 0).astype(np.uint8)
    brazo_d = np.where((zona_d & ~(cerca_d & halo))[..., None], a, 0).astype(np.uint8)
    cuerpo = np.where((zona_i | zona_d)[..., None], 0, a).astype(np.uint8)
    return (Image.fromarray(cuerpo), Image.fromarray(brazo_i), Image.fromarray(brazo_d))


@lru_cache(maxsize=32)
def _ojo_cerrado(w, h):
    """Párpado cerrado: arco con el mismo trazo oscuro del contorno de Pinti."""
    s = 4
    im = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.arc((w * s * 0.08, h * s * 0.25, w * s * 0.92, h * s * 0.95), 200, 340,
          fill=rgb(P["contorno"]), width=int(max(2, w * 0.14) * s))
    return im.resize((w, h), Image.LANCZOS)


def _ojos(cuerpo, parpadeo=0.0, mirar=(0.0, 0.0)):
    """Aplica parpadeo (0 abierto..1 cerrado, o tupla (izq, der) para guiñar) y mirada (dx,dy en -1..1) a los ojos del PNG original."""
    pp = parpadeo if isinstance(parpadeo, tuple) else (parpadeo, parpadeo)   # (izq, der): guiño = (0, 1)
    if max(pp) <= 0.02 and mirar == (0.0, 0.0):
        return cuerpo
    out = cuerpo.copy()
    naranja = rgb(P["pinti"])
    for caja, parpadeo in zip((OJO_IZQ, OJO_DER), pp):
        x0, y0, x1, y1 = caja
        ojo = cuerpo.crop(caja)
        w, h = ojo.size
        parche = Image.new("RGBA", (w, h), naranja)
        alto = h * (1 - clamp(parpadeo))
        if parpadeo < 0.85:
            ojo_m = ojo.resize((w, max(1, int(alto))), Image.LANCZOS)
            dx = int(round(mirar[0] * w * 0.12))
            dy = int(round(mirar[1] * h * 0.08)) + int((h - alto) * 0.6)
            parche.alpha_composite(ojo_m, (max(0, min(w - ojo_m.width, dx)), max(0, min(h - ojo_m.height, dy))))
        else:
            parche.alpha_composite(_ojo_cerrado(w, h), (0, 0))
        out.paste(parche, (x0, y0))
    return out


def parpadeo_auto(t, semilla=0.0, cada=3.3):
    """Valor de parpadeo 0..1 natural: un parpadeo de ~0,16 s cada `cada` s (a veces doble)."""
    fase = (t + semilla * 1.7) % cada
    def p(f, t0):
        u = (f - t0) / 0.16
        return 0.0 if u < 0 or u > 1 else math.sin(math.pi * u)
    v = p(fase, cada - 0.2)
    if int((t + semilla) / cada) % 3 == 2:
        v = max(v, p(fase, cada - 0.55))
    return v


def _rotar(capa, ang, pivote):
    """Rota una capa RGBA (tamaño del PNG) alrededor de un pivote, en grados (positivo = antihorario)."""
    return capa.rotate(ang, resample=Image.BICUBIC, center=pivote)


POSES = ("quieto", "saluda", "piensa", "celebra", "señala", "señala_arriba", "ríe")


def sprite(t, pose="saluda", parpadeo=None, mirar=(0.0, 0.0), brazo_i=None, brazo_d=None):
    """Pinti en el tamaño original (289x420 + margen) para la pose y el instante t; devuelve RGBA."""
    cuerpo, bi, bd = _capas()
    if parpadeo is None:
        parpadeo = parpadeo_auto(t)
    # Ángulos por pose (grados). Rotación PIL: + = antihorario. Brazo izq (arriba-izq): - lo lleva hacia la cara. Brazo der (abajo-der): + lo sube.
    ai, ad = 0.0, 0.0
    if pose == "saluda":
        ai = 14 * math.sin(t * 2 * math.pi * 1.6)
    elif pose == "piensa":
        ai = -30 + 3 * math.sin(t * 2.2)       # mano baja hacia la cara
        ad = 4 * math.sin(t * 1.3)
        mirar = mirar if mirar != (0.0, 0.0) else (0.6, -0.6)
    elif pose == "celebra":
        ai = 12 + 10 * math.sin(t * 2 * math.pi * 2.4)
        ad = 118 + 10 * math.sin(t * 2 * math.pi * 2.4 + 1)
    elif pose == "señala":
        ai = 2 * math.sin(t * 1.5)
        ad = 78 + 4 * math.sin(t * 2 * math.pi * 1.2)
    elif pose == "señala_arriba":
        ai = -24 + 3 * math.sin(t * 2 * math.pi * 1.2)   # la mano izquierda (ya levantada) apunta recto arriba
        ad = 2 * math.sin(t * 1.5)
    elif pose == "ríe":
        ai = 105 + 8 * math.sin(t * 2 * math.pi * 6)      # manos bajas a los lados de la barriga
        ad = -30 - 8 * math.sin(t * 2 * math.pi * 6 + 0.6)
    else:
        ai = 2 * math.sin(t * 1.4)
        ad = 2 * math.sin(t * 1.4 + 1)
    if brazo_i is not None:
        ai = brazo_i
    if brazo_d is not None:
        ad = brazo_d
    m = 140  # margen para que los brazos rotados no se corten
    lienzo = Image.new("RGBA", (SRC_W + 2 * m, SRC_H + m), (0, 0, 0, 0))
    def colocar(capa, ang, piv):
        grande = Image.new("RGBA", lienzo.size, (0, 0, 0, 0))
        grande.paste(capa, (m, m))
        if abs(ang) > 0.01:
            grande = grande.rotate(ang, resample=Image.BICUBIC, center=(piv[0] + m, piv[1] + m))
        lienzo.alpha_composite(grande)
    colocar(bi, ai, HOMBRO_IZQ)          # brazos detrás del cuerpo: la unión queda oculta
    colocar(bd, ad, HOMBRO_DER)
    c = _ojos(cuerpo, parpadeo, mirar)
    lienzo.alpha_composite(c, (m, m))
    return lienzo, (CENTRO_X + m, PIES_Y + m)


def dibujar(lienzo, t, x, y_pies, alto=620, pose="saluda", respira=True, rebote=0.0,
            salto=0.0, inclina=0.0, squash=0.0, parpadeo=None, mirar=(0.0, 0.0),
            sombra=True, voltear=False, brazo_i=None, brazo_d=None):
    """Dibuja a Pinti con los pies en (x, y_pies), alto en px, pose, respiración, rebote, salto (px), inclinación (°) y squash."""
    sp, (ax, ay) = sprite(t, pose, parpadeo, mirar, brazo_i, brazo_d)
    k = alto / SRC_H
    # Respiración: 0,9 Hz aprox, estira en vertical y estrecha un poco.
    r = 0.016 * math.sin(t * 2 * math.pi * 0.85) if respira else 0.0
    # Rebote continuo (rebote = amplitud en px) con squash al tocar suelo.
    by = 0.0
    sq = squash
    if rebote:
        fase = (t * 2.2) % 1.0
        by = -abs(math.sin(math.pi * fase)) * rebote
        if fase < 0.12 or fase > 0.88:
            sq += 0.05
    if pose == "ríe":  # risa: el cuerpo vibra con un vaivén rápido y pequeño
        inclina += 3.0 * math.sin(t * 2 * math.pi * 5)
        sq += 0.02 * abs(math.sin(t * 2 * math.pi * 5))
    sx = k * (1 - r * 0.6 + sq * 0.8)
    sy = k * (1 + r - sq)
    nw, nh = max(1, int(sp.width * sx)), max(1, int(sp.height * sy))
    img = sp.resize((nw, nh), Image.LANCZOS)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
    pax, pay = ax * sx, ay * sy
    if voltear:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        pax = nw - pax
    if abs(inclina) > 0.05:
        # rotar alrededor de los pies
        pad = int(max(nw, nh))
        grande = Image.new("RGBA", (nw + 2 * pad, nh + 2 * pad), (0, 0, 0, 0))
        grande.paste(img, (pad, pad))
        img = grande.rotate(inclina, resample=Image.BICUBIC, center=(pax + pad, pay + pad))
        pax += pad
        pay += pad
    alt_y = y_pies + by - salto
    if sombra:
        lejos = clamp((-by + salto) / max(1.0, alto * 0.5))
        sombra_suelo(lienzo, x, y_pies + 4, alto * 0.42 * (1 - 0.35 * lejos), opacidad=0.20 * (1 - 0.5 * lejos))
    pegar(lienzo, img, x - pax, alt_y - pay)
    return lienzo


def punta(x, y_pies, alto=620):
    """Posición en pantalla de la punta del crayón de Pinti (para trazar con él)."""
    k = alto / SRC_H
    return (x + (162 - CENTRO_X) * k, y_pies - (PIES_Y - 2) * k)


def pies_para_punta(px, py, alto=620, inclina=0.0):
    """Dónde poner los pies (x, y_pies) para que la punta del crayón quede en (px, py) con esa inclinación (°): Pinti traza."""
    k = alto / SRC_H
    vx, vy = (162 - CENTRO_X) * k, -(PIES_Y - 2) * k     # pies -> punta, sin rotar
    a = math.radians(inclina)                            # PIL: + = antihorario en pantalla
    rx = vx * math.cos(a) + vy * math.sin(a)
    ry = -vx * math.sin(a) + vy * math.cos(a)
    return px - rx, py - ry


def entrada(t, t0, dur=0.6, desde=-500, hasta=0):
    """Desplazamiento x de entrada con rebote (para que Pinti entre por un lado)."""
    from .base import rebote_atras, prog
    return desde + (hasta - desde) * rebote_atras(prog(t, t0, t0 + dur), 1.3)


def aterriza(t, t0):
    """Squash amortiguado tras aterrizar en t0 (pásalo a `squash`)."""
    return 0.12 * muelle(t, t0, frec=3.0, amort=7.0)


def inclinacion_trazo(ang, limite=55.0, suave_de=None, k=0.25):
    """Inclinación (°) para que, al trazar, el cuerpo de Pinti quede DETRÁS del avance (no tapa lo que se dibuja); ang = dirección del trazo en grados (la que devuelve trazo.punto_en / render_tiempos). Nunca boca abajo."""
    dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    inc = math.degrees(math.atan2(-dx, -dy))            # cuerpo opuesto al movimiento
    if abs(inc) > 90:                                   # si baja, el cuerpo iría arriba: lo dejamos al lado (35°)
        inc = math.copysign(35.0, inc if abs(dx) > 0.15 else 1.0)
    inc = max(-limite, min(limite, inc))
    if suave_de is not None:                            # suavizado frame a frame (pasa la inclinación anterior)
        inc = suave_de + (inc - suave_de) * k
    return inc
