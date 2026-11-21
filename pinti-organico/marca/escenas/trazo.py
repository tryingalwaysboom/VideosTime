"""Trazo de letras como en el libro: una línea punteada por el centro que se rellena de color siguiendo la trayectoria, con punto verde numerado y flecha."""
import math

import numpy as np
from PIL import Image, ImageDraw

from .base import P, rgb, fuente, sale, clamp, rebote_atras


# --- Trayectorias -------------------------------------------------------------
def linea(p0, p1, n=60):
    """Trayectoria recta de p0 a p1 como lista de puntos."""
    return [(p0[0] + (p1[0] - p0[0]) * i / (n - 1), p0[1] + (p1[1] - p0[1]) * i / (n - 1)) for i in range(n)]


def arco(cx, cy, rx, ry, a0, a1, n=90):
    """Trayectoria de arco elíptico de a0 a a1 (grados; 0 = derecha, 90 = abajo, sentido horario en pantalla)."""
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / (n - 1))),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / (n - 1)))) for i in range(n)]


def unir(*tramos):
    """Concatena tramos en una sola trayectoria."""
    out = []
    for tr in tramos:
        out.extend(tr if not out else tr[1:] if out[-1] == tr[0] else tr)
    return out


def _longitudes(pts):
    d = [0.0]
    for a, b in zip(pts, pts[1:]):
        d.append(d[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    return d


def punto_en(pts, u):
    """Punto de la trayectoria a la fracción u (0..1) de su longitud, y ángulo de avance en grados."""
    L = _longitudes(pts)
    total = L[-1]
    obj = clamp(u) * total
    for i in range(1, len(L)):
        if L[i] >= obj:
            f = (obj - L[i - 1]) / max(1e-6, L[i] - L[i - 1])
            a, b = pts[i - 1], pts[i]
            return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f), math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    a, b = pts[-2], pts[-1]
    return pts[-1], math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def sub(pts, u):
    """Parte inicial de la trayectoria hasta la fracción u."""
    if u <= 0:
        return [pts[0]]
    L = _longitudes(pts)
    obj = clamp(u) * L[-1]
    out = [pts[0]]
    for i in range(1, len(pts)):
        if L[i] <= obj:
            out.append(pts[i])
        else:
            out.append(punto_en(pts, u)[0])
            break
    return out


# --- Dibujo -------------------------------------------------------------------
def punteado(d, pts, color=None, radio=5, paso=20):
    """Línea punteada (puntos redondos) a lo largo de la trayectoria, como las letras para repasar del libro."""
    color = rgb(color or P["tinta"])
    L = _longitudes(pts)
    s = 0.0
    while s <= L[-1] + 0.1:
        (x, y), _ = punto_en(pts, s / L[-1])
        d.ellipse((x - radio, y - radio, x + radio, y + radio), fill=color)
        s += paso


def solida(d, pts, color, grosor=26):
    """Línea sólida de crayón con extremos redondeados (estampando discos: sin costuras en las curvas)."""
    if len(pts) < 1:
        return
    c = rgb(color)
    r = grosor / 2
    paso = max(1.0, r * 0.35)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + [pts[-1]]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / paso))
        for k in range(n):
            x, y = x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n
            d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    x, y = pts[-1]
    d.ellipse((x - r, y - r, x + r, y + r), fill=c)


def punto_inicio(d, x, y, numero, escala=1.0, aparicion=1.0, color_num=None, lado=(-1, -1)):
    """Punto verde de inicio con su número en un círculo azul (estilo del libro, pág. 20), con pop de entrada."""
    e = rebote_atras(aparicion, 2.2) if aparicion < 1 else 1.0
    if e <= 0:
        return
    r = 15 * escala * e
    d.ellipse((x - r, y - r, x + r, y + r), fill=rgb(P["punto_verde"]), outline=rgb("#FFFFFF"), width=max(2, int(4 * escala)))
    br = 25 * escala * e
    bx, by = x + lado[0] * 44 * escala, y + lado[1] * 44 * escala
    d.ellipse((bx - br, by - br, bx + br, by + br), fill=rgb(color_num or P["badge_azul"]), outline=rgb("#FFFFFF"),
              width=max(2, int(4 * escala)))
    f = fuente(max(8, int(32 * escala * e)), 700)
    d.text((bx, by + 1), str(numero), font=f, fill=rgb("#FFFFFF"), anchor="mm")


def flecha(d, x, y, ang, color, tam=34, opac=1.0):
    """Punta de flecha en (x, y) apuntando a `ang` grados (indica la dirección del trazo)."""
    a = math.radians(ang)
    pts = [(x + tam * math.cos(a), y + tam * math.sin(a)),
           (x + tam * 0.6 * math.cos(a + 2.4), y + tam * 0.6 * math.sin(a + 2.4)),
           (x + tam * 0.6 * math.cos(a - 2.4), y + tam * 0.6 * math.sin(a - 2.4))]
    d.polygon(pts, fill=rgb(color, int(255 * opac)))


def render(lienzo, t, trazos, t0, dur_trazo=1.2, pausa=0.15, color=None, grosor=26, escala=1.0,
           mostrar_guia=True):
    """Anima trazos [(trayectoria, numero, lado_badge), ...] en orden desde t0: guía punteada, punto verde+número y relleno de color; devuelve la punta actual."""
    color = color or P["pinti"]
    d = ImageDraw.Draw(lienzo)
    if mostrar_guia:
        for pts, _n, _l in trazos:
            punteado(d, pts, radio=5 * escala, paso=20 * escala)
    punta = None
    for i, (pts, n, lado) in enumerate(trazos):
        ti = t0 + i * (dur_trazo + pausa)
        u = sale(clamp((t - ti) / dur_trazo), 1.6)
        if u > 0:
            solida(d, sub(pts, u), color, grosor * escala)
            if u < 1:
                punta = punto_en(pts, u)[0]
    # puntos verdes, números y flecha de avance encima del trazo
    for i, (pts, n, lado) in enumerate(trazos):
        ti = t0 + i * (dur_trazo + pausa)
        ap = clamp((t - (ti - 0.25)) / 0.25)
        if ap > 0:
            punto_inicio(d, pts[0][0], pts[0][1], n, escala, ap, lado=lado)
        u = clamp((t - ti) / dur_trazo)
        if 0 < u < 1:
            (fx, fy), ang = punto_en(pts, min(1.0, sale(u, 1.6) + 0.04))
            flecha(d, fx, fy, ang, "#FFFFFF", tam=20 * escala, opac=0.9)
    return punta


# --- Letras del libro (sin girar nunca) ------------------------------------------
def letra_b(cx, cy, alto=520):
    """b del libro: 1 palito de arriba abajo; 2 barriga desde media altura hacia la derecha, cerrando abajo pegada al palito."""
    x = cx - alto * 0.20
    top, base = cy - alto / 2, cy + alto / 2
    r = alto * 0.25
    palito = linea((x, top), (x, base))
    by = base - r
    barriga = arco(x + r, by, r, r * 1.02, 200, 520, n=130)
    return [(palito, 1, (-1, -1)), (barriga, 2, (1, -1))]


def letra_d(cx, cy, alto=520):
    """d del libro: 1 barriga desde arriba a la derecha girando a la izquierda como una c; 2 palito de arriba abajo por la derecha."""
    x = cx + alto * 0.20
    top, base = cy - alto / 2, cy + alto / 2
    r = alto * 0.25
    by = base - r
    barriga = arco(x - r * 0.95, by, r, r, -40, -320, n=110)
    palito = linea((x, top), (x, base))
    return [(barriga, 1, (-1, -1)), (palito, 2, (-1, -1))]


# --- Letras de imprenta en una caja (x0, y0, x1, y1), en cualquier sistema de coordenadas ------
def letra_M(caja, pico=0.69):
    """M mayúscula del libro (pág. 20): 1 palito izquierdo de arriba abajo; 2 desde el mismo punto, diagonal al pico de la V, diagonal arriba y recto abajo por la derecha."""
    x0, y0, x1, y1 = caja
    xm, yv = (x0 + x1) / 2, y0 + (y1 - y0) * pico
    palito = linea((x0, y0), (x0, y1))
    zigzag = unir(linea((x0, y0), (xm, yv), 40), linea((xm, yv), (x1, y0), 40), linea((x1, y0), (x1, y1), 50))
    return [(palito, 1, (-1, -1)), (zigzag, 2, (1, -1))]


def letra_m(caja, arranque=0.38):
    """m minúscula del libro (pág. 20): 1 palito; 2 desde el punto verde del palito sube, primer puente y baja; 3 igual desde el palito del medio."""
    x0, y0, x1, y1 = caja
    xm = (x0 + x1) / 2
    h = y1 - y0
    r = (xm - x0) / 2
    ys = y0 + h * arranque                     # punto verde, a media altura del palito
    palito = linea((x0, y0), (x0, y1))

    def puente(xa, xb):
        rr = (xb - xa) / 2
        return unir(linea((xa, ys), (xa, y0 + rr * 0.9), 12),
                    arco(xa + rr, y0 + rr * 0.9, rr, rr * 0.9, 180, 360, 40),
                    linea((xb, y0 + rr * 0.9), (xb, y1), 30))
    return [(palito, 1, (-1, -1)), (puente(x0, xm), 2, (-1, 1)), (puente(xm, x1), 3, (-1, 1))]


def letra_a(caja):
    """a del libro (pág. 14): 1 redondo desde arriba a la derecha hacia la izquierda (antihorario) hasta cerrarse; 2 palito de arriba abajo por la derecha."""
    x0, y0, x1, y1 = caja
    xp = x1                                  # palito a la derecha
    rx, ry = (xp - x0) / 2, (y1 - y0) / 2
    cx, cy = x0 + rx, y0 + ry
    redondo = arco(cx, cy, rx * 0.98, ry, -40, -400, 110)   # ángulos de pantalla: negativo = sube por arriba hacia la izquierda
    palito = linea((xp, y0), (xp, y1))
    return [(redondo, 1, (1, -1)), (palito, 2, (1, -1))]


def tilde(p_arriba_der, p_abajo_izq):
    """Tilde corta e inclinada: de arriba a la derecha hacia abajo a la izquierda."""
    return [(linea(p_arriba_der, p_abajo_izq, 20), 1, (1, -1))]


def render_tiempos(lienzo, t, trazos, tiempos, color=None, grosor=26, escala=1.0, guia=False, badges=True,
                   flecha_on=True):
    """Como render() pero cada trazo con su (t_ini, t_fin) exacto del guion; devuelve (punta, apoyada, ang) para sincronizar a Pinti (pinti.inclinacion_trazo(ang)) y el scratch."""
    color = color or P["pinti"]
    d = ImageDraw.Draw(lienzo)
    if guia:
        for pts, _n, _l in trazos:
            punteado(d, pts, radio=5 * escala, paso=20 * escala)
    punta, apoyada, ang = None, False, 90.0
    for (pts, n, lado), (ti, tf) in zip(trazos, tiempos):
        u = sale(clamp((t - ti) / max(1e-6, tf - ti)), 1.3)
        if u > 0:
            solida(d, sub(pts, u), color, grosor * escala)
        if ti <= t <= tf:
            (punta, ang), apoyada = punto_en(pts, min(1.0, u)), True
    for (pts, n, lado), (ti, tf) in zip(trazos, tiempos):
        if badges:
            ap = clamp((t - (ti - 0.2)) / 0.2)
            if ap > 0:
                punto_inicio(d, pts[0][0], pts[0][1], n, escala, ap, lado=lado)
        if flecha_on and ti < t < tf:
            u = sale(clamp((t - ti) / (tf - ti)), 1.3)
            (fx, fy), ang = punto_en(pts, min(1.0, u + 0.04))
            flecha(d, fx, fy, ang, "#FFFFFF", tam=20 * escala, opac=0.9)
    if punta is None:  # entre trazos: la punta espera sobre el inicio del siguiente trazo (en el aire)
        sig = [(pts, ti) for (pts, _n, _l), (ti, _tf) in zip(trazos, tiempos) if ti > t]
        if sig:
            punta = sig[0][0][0]
    return punta, apoyada, ang


# --- Pág. 20 real ("La M de mamá"): cajas medidas sobre los puntos de assets/paginas/pagina-20.jpg (px de la página) ---
def pag20_M_fila1(i):
    """Caja de la i-ésima M punteada (0..8) de la fila 1 de la pág. 20."""
    x = 194 + 89.9 * i
    return (x, 487, x + 55, 558)


def pag20_m_fila3(i):
    """Caja de la i-ésima m punteada (0..8) de la fila 3 de la pág. 20."""
    x = 190 + 85.5 * i
    return (x, 727, x + 50, 762)


PAG20_MAMA = {  # "Mamá" punteada de la fila 6
    "M": (354, 1000, 408, 1071), "a1": (419, 1036, 453, 1071), "m": (466, 1035, 516, 1071),
    "a2": (527, 1036, 561, 1071), "tilde": ((554, 1012), (541, 1029)),
}
