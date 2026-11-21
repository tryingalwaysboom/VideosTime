"""Texto de marca: titulares con entrada pop, resaltado karaoke palabra a palabra, bocadillos y tarjetas de sílaba (pág. 21)."""
import math

from PIL import Image, ImageDraw, ImageFilter

from .base import P, W, rgb, fuente, pegar, sombra_suave, rebote_atras, sale, clamp, rect_redondeado, SEGURA_DER

TINTA = P["tinta"]


def _medir(txt, f):
    b = f.getbbox(txt)
    return b[2] - b[0], b[3] - b[1]


def partir(texto, f, ancho_max):
    """Parte un texto en líneas que caben en ancho_max con la fuente f."""
    lineas, cur = [], ""
    for p in texto.split():
        prueba = (cur + " " + p).strip()
        if _medir(prueba, f)[0] <= ancho_max or not cur:
            cur = prueba
        else:
            lineas.append(cur)
            cur = p
    if cur:
        lineas.append(cur)
    return lineas


def _capa_texto(lineas, f, color, borde_col, borde, interlinea=1.12):
    alto_l = int(f.size * interlinea)
    anchos = [_medir(l, f)[0] for l in lineas]
    w = max(anchos) + 2 * borde + 20
    h = alto_l * len(lineas) + 2 * borde + 20
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, l in enumerate(lineas):
        d.text((w / 2, borde + 10 + i * alto_l + alto_l / 2), l, font=f, fill=rgb(color), anchor="mm",
               stroke_width=borde, stroke_fill=rgb(borde_col) if borde else None)
    return img


def titulo(lienzo, t, texto, cx, cy, t0=0.0, tam=86, color=None, borde_col="#FFFFFF", borde=10,
           ancho_max=900, dur=0.38, sombra=True):
    """Titular redondo con entrada pop (escala 0,6→1 con rebote y leve giro) desde t0; borde blanco suave, nunca navy."""
    u = clamp((t - t0) / dur)
    if u <= 0:
        return lienzo
    f = fuente(tam, 700)
    capa = _capa_texto(partir(texto, f, ancho_max), f, color or TINTA, borde_col, borde)
    e = rebote_atras(u, 2.0)
    esc = 0.6 + 0.4 * e
    rot = (1 - sale(u)) * -4
    # respiración leve tras la entrada
    if u >= 1:
        esc *= 1 + 0.012 * math.sin((t - t0) * 2 * math.pi / 2.2)
    capa = capa.resize((max(1, int(capa.width * esc)), max(1, int(capa.height * esc))), Image.LANCZOS)
    if abs(rot) > 0.1:
        capa = capa.rotate(rot, resample=Image.BICUBIC, expand=True)
    if u < 1:
        a = capa.getchannel("A").point(lambda v: int(v * min(1, u * 3)))
        capa.putalpha(a)
    if sombra:
        s = sombra_suave(capa, radio=14, opacidad=0.18)
        pegar(lienzo, s, cx - s.width / 2, cy - s.height / 2 + 8)
    pegar(lienzo, capa, cx - capa.width / 2, cy - capa.height / 2)
    return lienzo


def karaoke(lienzo, t, palabras, cx, cy, tam=84, ancho_max=880, color=None, color_activo=None,
            color_resalte=None, borde=10, pop_activa=0.10):
    """Frase completa visible desde el frame 0 con resaltado karaoke: palabras=[(texto, t_ini, t_fin), ...]; las palabras activas (una o varias) crecen y llevan pastilla naranja."""
    f = fuente(tam, 700)
    color = rgb(color or TINTA)
    color_activo = rgb(color_activo or "#FFFFFF")
    resalte = rgb(color_resalte or P["pinti"])
    esp = _medir("a a", f)[0] - _medir("aa", f)[0] + int(tam * 0.14)  # aire para que el resalte no pise vecinas
    # maquetar en líneas
    lineas, cur, ancho = [], [], 0
    for i, (p, a, b) in enumerate(palabras):
        w = _medir(p, f)[0]
        if cur and ancho + esp + w > ancho_max:
            lineas.append((cur, ancho))
            cur, ancho = [], 0
        cur.append(i)
        ancho += (esp if len(cur) > 1 else 0) + w
    if cur:
        lineas.append((cur, ancho))
    alto_l = int(tam * 1.25)
    y0 = cy - alto_l * len(lineas) / 2 + alto_l / 2
    d = ImageDraw.Draw(lienzo)
    activas = []
    for li, (idxs, ancho) in enumerate(lineas):
        x = cx - ancho / 2
        y = y0 + li * alto_l
        for i in idxs:
            p, a, b = palabras[i]
            w = _medir(p, f)[0]
            if a <= t < b:
                activas.append((p, a, x, y, w))
            else:
                d.text((x + w / 2, y), p, font=f, fill=color, anchor="mm", stroke_width=borde,
                       stroke_fill=rgb("#FFFFFF"))
            x += w + esp
    for p, a, x, y, w in activas:  # las activas (una o un grupo, p. ej. "La M,") se dibujan al final, encima
        u = clamp((t - a) / max(0.05, pop_activa))
        esc = 1 + 0.08 * rebote_atras(u, 2.5)
        pad = int(tam * 0.12)
        fondo = rect_redondeado((w + 2 * pad, int(tam * 1.12)), int(tam * 0.26), resalte)
        fondo = fondo.resize((int(fondo.width * esc), int(fondo.height * esc)), Image.LANCZOS)
        s_ = sombra_suave(fondo, radio=10, opacidad=0.18)
        pegar(lienzo, s_, x + w / 2 - s_.width / 2, y - s_.height / 2 + 8)
        pegar(lienzo, fondo, x + w / 2 - fondo.width / 2, y - fondo.height / 2 + 2)
        d.text((x + w / 2, y), p, font=fuente(int(tam * esc), 700), fill=color_activo, anchor="mm")
    return lienzo


def bocadillo(lienzo, t, texto, cx, cy, t0=0.0, tam=70, cola=(-1, 1), color_fondo="#FFFFFF", color=None, dur=0.32):
    """Bocadillo redondo blanco con cola hacia el hablante (cola=(dx,dy) en -1..1) y entrada pop."""
    u = clamp((t - t0) / dur)
    if u <= 0:
        return lienzo
    f = fuente(tam, 700)
    tw, th = _medir(texto, f)
    pw, ph = tw + 80, int(tam * 1.6)
    capa = Image.new("RGBA", (pw + 120, ph + 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    ox, oy = 60, 40
    d.rounded_rectangle((ox, oy, ox + pw, oy + ph), ph // 2, fill=rgb(color_fondo))
    bx = ox + pw / 2 + cola[0] * pw * 0.28
    by = oy + ph
    d.polygon([(bx - 26, by - 6), (bx + 26, by - 6), (bx + cola[0] * 52, by + 52 * max(0.4, cola[1]))], fill=rgb(color_fondo))
    d.text((ox + pw / 2, oy + ph / 2 + 2), texto, font=f, fill=rgb(color or TINTA), anchor="mm")
    e = rebote_atras(u, 2.4)
    esc = 0.5 + 0.5 * e
    capa = capa.resize((max(1, int(capa.width * esc)), max(1, int(capa.height * esc))), Image.LANCZOS)
    s = sombra_suave(capa, radio=16, opacidad=0.20)
    pegar(lienzo, s, cx - s.width / 2, cy - s.height / 2 + 10)
    pegar(lienzo, capa, cx - capa.width / 2, cy - capa.height / 2)
    return lienzo


def silaba(lienzo, t, texto, cx, cy, t0=0.0, color="sil_melocoton", ancho=240, alto=170, tam=110,
           dur=0.35, rebote=True):
    """Tarjeta de sílaba con los colores reales de la pág. 21 (fondo pastel + borde), entrada pop y flotación suave."""
    u = clamp((t - t0) / dur)
    if u <= 0:
        return lienzo
    relleno, borde = P[color]
    tarjeta = rect_redondeado((ancho, alto), 34, relleno, borde, 10)
    d = ImageDraw.Draw(tarjeta)
    d.text((ancho / 2, alto / 2 + 4), texto, font=fuente(tam, 600), fill=rgb(TINTA), anchor="mm")
    e = rebote_atras(u, 2.2)
    esc = 0.55 + 0.45 * e
    fl = 6 * math.sin((t - t0) * 2 * math.pi / 1.9) if rebote and u >= 1 else 0
    tarjeta = tarjeta.resize((max(1, int(ancho * esc)), max(1, int(alto * esc))), Image.LANCZOS)
    s = sombra_suave(tarjeta, radio=14, opacidad=0.16)
    pegar(lienzo, s, cx - s.width / 2, cy - s.height / 2 + 10 + fl)
    pegar(lienzo, tarjeta, cx - tarjeta.width / 2, cy - tarjeta.height / 2 + fl)
    return lienzo


def fila_silabas(lienzo, t, silabas, cy, t0=0.0, paso=0.18, ancho=176, alto=150, tam=84, sep=14):
    """Fila de sílabas (p. ej. ma me mi mo mu) con los 5 colores de la pág. 21, entrando una tras otra."""
    from .base import SILABAS_CICLO
    total = len(silabas) * ancho + (len(silabas) - 1) * sep
    x0 = (60 + SEGURA_DER) / 2 - total / 2 + ancho / 2
    for i, s in enumerate(silabas):
        silaba(lienzo, t, s, x0 + i * (ancho + sep), cy, t0 + i * paso, SILABAS_CICLO[i % 5], ancho, alto, tam)
    return lienzo
