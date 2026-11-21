"""Efectos tiernos: signos ? con rebote, bombilla con pop, chispas, corazones y estrellas "¡Lo logré!" que se rellenan."""
import math

from PIL import Image, ImageDraw

from .base import P, rgb, fuente, pegar, sombra_suave, rebote_atras, sale, clamp


def _estrella_pts(cx, cy, r, ri=0.45, rot=-90):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * ri
        a = math.radians(rot + i * 36)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def estrella(d, cx, cy, r, relleno=None, borde=None, grosor=5):
    """Estrella de 5 puntas (borde dorado del libro; relleno amarillo cuando se consigue)."""
    pts = _estrella_pts(cx, cy, r)
    d.polygon(pts, fill=rgb(relleno) if relleno else None)
    d.line(pts + [pts[0]], fill=rgb(borde or P["estrella_oro"]), width=grosor, joint="curve")


def estrellas_logre(lienzo, t, cx, cy, t0, paso=0.35, r=46, texto="¡Lo logré!"):
    """Tira "¡Lo logré!" de las páginas con 3 estrellas que se rellenan de amarillo una tras otra desde t0 (con pop)."""
    capa = Image.new("RGBA", (620, 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    d.rounded_rectangle((0, 0, 619, 149), 60, fill=rgb("#FFFFFF"))
    d.text((150, 76), texto, font=fuente(48, 600), fill=rgb(P["tinta"]), anchor="mm")
    s = sombra_suave(capa, radio=14, opacidad=0.18)
    pegar(lienzo, s, cx - s.width / 2, cy - s.height / 2 + 8)
    pegar(lienzo, capa, cx - 310, cy - 75)
    d = ImageDraw.Draw(lienzo)
    for i in range(3):
        x = cx - 310 + 345 + i * 105
        u = clamp((t - (t0 + i * paso)) / 0.3)
        esc = 1 + 0.35 * math.sin(math.pi * u) if 0 < u < 1 else 1
        estrella(d, x, cy, r * esc, P["estrella"] if u > 0.3 else None, P["estrella_oro"], 6)
        if 0 < u < 1:
            chispas(lienzo, x, cy, u, n=6, radio=r * 1.6)
    return lienzo


def chispas(lienzo, cx, cy, u, n=8, radio=90, color=None):
    """Chispas que salen en anillo desde (cx, cy) con progreso u (0..1)."""
    d = ImageDraw.Draw(lienzo)
    col = color or P["estrella"]
    e = sale(u, 2)
    for i in range(n):
        a = 2 * math.pi * i / n + 0.3
        rr = radio * (0.4 + 0.6 * e)
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        s = 12 * (1 - u) + 2
        d.ellipse((x - s, y - s, x + s, y + s), fill=rgb(col, int(255 * (1 - u * 0.8))))


def interrogacion(lienzo, t, x, y, t0, tam=120, color=None):
    """Signo ? redondo que sale con rebote en t0 y luego se balancea."""
    u = clamp((t - t0) / 0.35)
    if u <= 0:
        return lienzo
    e = rebote_atras(u, 2.6)
    f = fuente(int(tam * (0.3 + 0.7 * e)), 700)
    rot = 10 * math.sin((t - t0) * 5)
    capa = Image.new("RGBA", (tam * 2, tam * 2), (0, 0, 0, 0))
    ImageDraw.Draw(capa).text((tam, tam), "?", font=f, fill=rgb(color or P["d_azul"]), anchor="mm",
                              stroke_width=8, stroke_fill=rgb("#FFFFFF"))
    capa = capa.rotate(rot, resample=Image.BICUBIC)
    pegar(lienzo, capa, x - tam, y - tam - 30 * e)
    return lienzo


def bombilla(lienzo, t, x, y, t0, tam=110):
    """Bombilla amarilla con pop y rayos que laten (idea, «el truco»)."""
    u = clamp((t - t0) / 0.35)
    if u <= 0:
        return lienzo
    e = rebote_atras(u, 2.4)
    r = tam * 0.5 * e
    d = ImageDraw.Draw(lienzo)
    lat = 1 + 0.08 * math.sin((t - t0) * 8)
    for i in range(8):
        a = math.radians(-90 + (i - 3.5) * 26)
        r0, r1 = r * 1.25 * lat, r * 1.7 * lat
        d.line((x + r0 * math.cos(a), y + r0 * math.sin(a), x + r1 * math.cos(a), y + r1 * math.sin(a)),
               fill=rgb(P["estrella"]), width=max(2, int(10 * e)))
    d.ellipse((x - r, y - r, x + r, y + r), fill=rgb("#FFE88A"), outline=rgb(P["estrella_oro"]), width=max(2, int(6 * e)))
    d.rounded_rectangle((x - r * 0.45, y + r * 0.85, x + r * 0.45, y + r * 1.35), max(1, int(r * 0.15)), fill=rgb("#C9BBA8"))
    d.ellipse((x - r * 0.55, y - r * 0.55, x - r * 0.1, y - r * 0.1), fill=(255, 255, 255, 200))
    return lienzo


def corazones(lienzo, t, cx, cy, t0, n=3):
    """Corazones rosas (como en la pág. 22) que suben flotando desde (cx, cy)."""
    d = ImageDraw.Draw(lienzo)
    for i in range(n):
        u = clamp((t - t0 - i * 0.2) / 1.4)
        if u <= 0 or u >= 1:
            continue
        x = cx + (i - 1) * 70 + 20 * math.sin(u * 6 + i)
        y = cy - 260 * sale(u, 2)
        s = 26 * (0.5 + 0.5 * sale(u * 3)) * (1 - 0.3 * u)
        col = rgb(P["mejilla"], int(255 * (1 - u ** 3)))
        d.ellipse((x - s, y - s * 0.6, x, y + s * 0.3), fill=col)
        d.ellipse((x, y - s * 0.6, x + s, y + s * 0.3), fill=col)
        d.polygon([(x - s * 0.97, y), (x + s * 0.97, y), (x, y + s * 1.05)], fill=col)
    return lienzo


def check(lienzo, t, x, y, t0, tam=90, color=None):
    """Check verde (color del punto de inicio del libro) que se dibuja en 0,25 s con pop desde t0, sobre círculo blanco."""
    u = clamp((t - t0) / 0.25)
    if u <= 0:
        return lienzo
    esc = rebote_atras(clamp((t - t0) / 0.35))
    r = tam / 2 * esc
    d = ImageDraw.Draw(lienzo)
    d.ellipse((x - r, y - r, x + r, y + r), fill=rgb("#FFFFFF"))
    col = rgb(color or P["punto_verde"])
    p = [(x - r * 0.45, y + r * 0.02), (x - r * 0.1, y + r * 0.35), (x + r * 0.5, y - r * 0.35)]
    l1 = min(1.0, u * 2)
    a = (p[0][0] + (p[1][0] - p[0][0]) * l1, p[0][1] + (p[1][1] - p[0][1]) * l1)
    d.line([p[0], a], fill=col, width=max(4, int(r * 0.22)), joint="curve")
    if u > 0.5:
        l2 = (u - 0.5) * 2
        b = (p[1][0] + (p[2][0] - p[1][0]) * l2, p[1][1] + (p[2][1] - p[1][1]) * l2)
        d.line([p[1], b], fill=col, width=max(4, int(r * 0.22)), joint="curve")
    return lienzo


def destello(lienzo, t, pts, t0, dur=0.45, ancho=26):
    """Brillo suave que recorre una trayectoria ya trazada (la M terminada brilla una vez)."""
    u = (t - t0) / dur
    if not 0 <= u <= 1 or len(pts) < 2:
        return lienzo
    capa = Image.new("RGBA", lienzo.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    n = len(pts)
    i0, i1 = int(max(0, (u - 0.25) * n)), int(min(n, u * n + 1))
    if i1 - i0 >= 2:
        d.line(pts[i0:i1], fill=(255, 255, 255, 170), width=ancho, joint="curve")
    from PIL import ImageFilter
    lienzo.alpha_composite(capa.filter(ImageFilter.GaussianBlur(6)))
    return lienzo


def letra_cae(lienzo, t, letra, x, y, suelo, t0, tam=150, color=None, retraso=0.0):
    """Una letra se despega y cae en vertical con gravedad y rebota en `suelo` sin rotar nunca (gag de "miau")."""
    from .base import fuente as _f
    tt = t - t0 - retraso
    if tt < 0:
        yy = y
    else:
        g = 3200.0
        caida = suelo - y
        tc = math.sqrt(2 * max(1, caida) / g)
        if tt < tc:
            yy = y + 0.5 * g * tt * tt
        else:
            v = g * tc * 0.35
            tb = tt - tc
            alto_rebote = max(0.0, v * tb - 0.5 * g * tb * tb)
            yy = suelo - alto_rebote
    d = ImageDraw.Draw(lienzo)
    d.text((x, yy), letra, font=_f(tam, 700), fill=rgb(color or P["tinta"]), anchor="ms",
           stroke_width=8, stroke_fill=rgb("#FFFFFF"))
    return lienzo


def velo(lienzo, y0, y1, opacidad=0.72, color="#FFF7EC"):
    """Banda crema difusa detrás del texto cuando el fondo es una página llena (macro): da lectura sin tarjeta ni borde."""
    from PIL import ImageFilter
    m = Image.new("L", lienzo.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((-40, y0, lienzo.width + 40, y1), 60, fill=int(255 * opacidad))
    m = m.filter(ImageFilter.GaussianBlur(28))
    capa = Image.new("RGBA", lienzo.size, rgb(color))
    capa.putalpha(m)
    lienzo.alpha_composite(capa)
    return lienzo
