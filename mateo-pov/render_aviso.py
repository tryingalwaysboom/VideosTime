"""AVISO de cambio de cuenta (mamá y Mateo). Motor de la serie. Monta la Parte 7 de "Mateo no sabe escribir". Reutiliza el motor del taller (subtítulos palabra a palabra, tiempos de voz,
transiciones) con escenas, barra y final propios.
Uso: python3 render.py still 10 20 | python3 render.py scenes [i...] | python3 render.py info"""
import os, sys, math, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["GUION"] = "guion_mateo_aviso"; os.environ["VOZDIR"] = os.path.join(HERE, "voz_aviso")
sys.path.insert(0, HERE); sys.path.append(os.path.join(HERE, "..", "taller-pov"))
import importlib.util
_spec = importlib.util.spec_from_file_location("R", os.path.join(HERE, "..", "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

R.LAY = os.path.join(HERE, "layers"); R.layer.cache_clear(); R.scaled.cache_clear()
TMP = os.path.join(HERE, "tmp_aviso"); os.makedirs(TMP, exist_ok=True)
W, H, FPS = R.W, R.H, R.FPS
put, bg, text, panel, stamp, ficha, etiqueta, dark = R.put, R.bg, R.text, R.panel, R.stamp, R.ficha, R.etiqueta, R.dark
ease, clamp, popscale, back, font, mouth = R.ease, R.clamp, R.popscale, R.back, R.font, R.mouth
F_ANTON, F_UI, F_HAND = R.F_ANTON, R.F_UI, R.F_HAND
YEL, WHITE, OL, GRIS = R.YEL, R.WHITE, R.OL, R.GRIS
ROSA = (255, 120, 150); VERDE = (70, 190, 110); AZ = (70, 130, 230); ROJO = (226, 72, 59); CREMA = (255, 248, 236)
PI_ = math.pi
F_ESC = os.path.join(HERE, "fonts", "Andika-Bold.ttf")      # letra escolar (la que escribe mamá)
F_BAL = os.path.join(HERE, "fonts", "Baloo2-ExtraBold.ttf")  # rótulos de la barra
NAVY = (44, 36, 78)

# pausas entre frases (respiración dramática donde hace falta)
R.GAP.update({"F02": .3, "F03": .45, "F04": .4, "F05": .4, "F06": .35, "F07": .3, "F08": .3, "F09": .5, "F10": .5, "F11": .35, "F12": .5, "F13": .6, "F14": .35, "F15": .4, "F16": .35, "F17": .45, "F18": .5})
R.TL, R.TOTAL = R.timeline()
R.TL = {k: (a - .1, b - .1) for k, (a, b) in R.TL.items()}; R.TOTAL -= .1   # la voz arranca en el frame 0
R.CH = R.chunks(); TL = R.TL; TOTAL = R.TOTAL
S, E, WT = R.S, R.E, R.WT
R.NOMBRE = {"K": "MATEO", "A": "ABUELA PILAR", "P": "MAESTRA MARTA"}
R.HIDE_LAST_CAPTION = False

def talk(lid, T): return S(lid) <= T < E(lid)
def u_(T, t0, d): return ease((T - t0) / d)

# ---------------------------------------------------------------- personajes con boca animada
def mateo(c, kind, cx, cy, s, T, lid=None, rot=0):
    hab = lid is not None and talk(lid, T)
    put(c, f"mateo_{kind}_hab" if hab else f"mateo_{kind}", cx, cy + 400 * s, s, rot=rot)   # capa de 1900 px: el cuerpo sigue bajo el encuadre
    if hab: mouth(c, cx, cy + 56 * s, T, True, int(26 * s))
    if kind.split("_")[0] not in ("llora", "feliz", "travieso") and (T * 1.0) % 3.7 < .12 and not rot:   # parpadeo
        d = ImageDraw.Draw(c)
        for ex in (-78, 78):
            x, y = cx + ex * s, cy - 86 * s
            d.ellipse((x - 40 * s, y - 34 * s, x + 40 * s, y + 34 * s), fill=(243, 194, 155))
            d.line((x - 34 * s, y + 4 * s, x + 34 * s, y + 4 * s), fill=OL, width=max(3, int(6 * s)))

def abuela(c, cx, cy, s, T, lid=None):
    hab = lid is not None and talk(lid, T)
    put(c, "abuela_hab" if hab else "abuela", cx, cy + 200 * s, s)
    if hab: mouth(c, cx, cy - 94 * s, T, True, int(24 * s))

def lagrimas(c, cx, cy, s, T):
    """Lágrimas que caen por las mejillas de Mateo."""
    d = ImageDraw.Draw(c)
    for k, ex in enumerate((-80, 80)):
        for j in range(3):
            ph = ((T * 1.3) + j / 3 + k * .17) % 1
            x = cx + ex * s + 6 * math.sin(ph * 6); y = cy - 90 * s + ph * 240 * s
            r = (10 + 4 * (1 - ph)) * s
            d.ellipse((x - r * .75, y - r, x + r * .75, y + r), fill=(143, 208, 255), outline=(58, 127, 191), width=3)

# ---------------------------------------------------------------- barra superior (cuaderno acogedor)
CX0, CY0, CX1, CY1 = 40, 150, 1040, 322
def barra_base():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((CX0, CY0 + 10, CX1, CY1 + 12), 34, fill=(40, 20, 40, 95))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((CX0, CY0, CX1, CY1), 34, fill=(255, 250, 240, 246), outline=NAVY, width=5)
    for y in range(CY0 + 84, CY1 - 6, 30): d.line((CX0 + 30, y, CX1 - 30, y), fill=(150, 190, 235, 70), width=2)   # renglones
    d.line((CX0 + 26, CY0 + 76, CX1 - 26, CY0 + 76), fill=(240, 150, 170, 160), width=3)
    # cinta adhesiva
    tp = Image.new("RGBA", (150, 44), (255, 214, 120, 190)); tp = tp.rotate(-8, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(tp, (CX0 + 410, CY0 - 22))
    d.text((CX0 + 40, CY0 + 150), "SU NOMBRE", font=font(F_BAL, 20), fill=(140, 118, 150), anchor="lm")
    d.text((CX0 + 552, CY0 + 150), "ÁNIMO DE MATEO", font=font(F_BAL, 20), fill=(140, 118, 150), anchor="mm")
    d.text((CX0 + 830, CY0 + 150), "TU PACIENCIA", font=font(F_BAL, 20), fill=(140, 118, 150), anchor="mm")
    return im
_BB = barra_base()

def corazon(d, cx, cy, r, col, outline=None):
    pts = [(cx + r * 16 * math.sin(t) ** 3 / 17, cy - r * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 17)
           for t in np.linspace(0, 2 * PI_, 40)]
    d.polygon(pts, fill=col, outline=outline)

def interp(T, keys):
    """keys: [(t, valor)] -> valor animado (rampa de .6 s en cada cambio)."""
    v = keys[0][1]
    for t, nv in keys[1:]:
        if T >= t: v = v + (nv - v) * ease((T - t) / .6)
    return v

def draw_hud(c, T):
    return
    if T >= S("F18") - .3: return
    if T < .3:
        k = ease(T / .3); c.alpha_composite(_BB.crop((0, 0, W, 360)), (0, int(-360 * (1 - k)))); return
    c.alpha_composite(_BB); d = ImageDraw.Draw(c)
    cambios = []
    dia, t_d = 16, -9
    for t, n in cambios:
        if T >= t: dia, t_d = n, t
    def pop(t): return 1 + .3 * math.sin(clamp((T - t) / .3) * PI_) if 0 <= T - t < .3 else 1
    y1 = CY0 + 40
    d.rounded_rectangle((CX0 + 22, y1 - 24, CX0 + 120, y1 + 24), 24, fill=ROSA)
    d.text((CX0 + 71, y1 + 2), "EP. 8", font=font(F_BAL, 30), fill=WHITE, anchor="mm")
    d.text((CX0 + 140, y1 + 4), f"DÍA {dia}", font=font(F_BAL, 46 * pop(t_d)), fill=NAVY, anchor="lm")
    fq = font(F_BAL, 40); txt = "META: FIN DE AÑO"
    d.text((CX1 - 30, y1 + 4), txt, font=fq, fill=(214, 70, 110), anchor="rm")
    fx = CX1 - 30 - d.textlength(txt, font=fq) - 30
    d.line((fx - 10, y1 - 22, fx - 10, y1 + 22), fill=NAVY, width=5)
    d.polygon([(fx - 8, y1 - 22), (fx + 22, y1 - 13), (fx - 8, y1 - 2)], fill=ROJO, outline=NAVY)
    # MATEO: la E ya la sabía; M, A, T y O se van encendiendo al aprenderlas
    y2 = CY0 + 112
    for i, L_ in enumerate("MATEO"):
        x = CX0 + 60 + i * 64; t_ok = LETRA_OK[L_]
        ok = T >= t_ok
        k = popscale(T, t_ok, .4) if ok and T - t_ok < .5 else 1
        r_ = 26 * k
        d.rounded_rectangle((x - r_, y2 - 28 * k, x + r_, y2 + 28 * k), 10, fill=(120, 205, 140) if ok else (246, 240, 232), outline=(60, 150, 90) if ok else (200, 186, 205), width=3)
        d.text((x, y2 + 2), L_, font=font(F_ESC, int(36 * k)), fill=WHITE if ok else (214, 204, 218), anchor="mm")
    an = interp(T, [(0, .8), (S("F05"), .75), (S("F10"), .6), (S("F13"), .9), (S("F16"), 1.0)])
    pa = interp(T, [(0, .6), (S("F04"), .5), (S("F08"), .8), (S("F12"), .7), (S("F16"), .4)])
    for i in range(5):
        x = CX0 + 448 + i * 52; f = clamp(an * 5 - i)
        corazon(d, x, y2, 21, (236, 226, 232), outline=(200, 186, 205))
        if f > 0:
            hl = Image.new("RGBA", (60, 60), (0, 0, 0, 0)); corazon(ImageDraw.Draw(hl), 30, 30, 21, (255, 92, 130))
            hl = hl.crop((0, 0, int(9 + 42 * f), 60)); c.alpha_composite(hl, (int(x - 30), int(y2 - 30)))
    d = ImageDraw.Draw(c)
    bx = CX0 + 742
    for i in range(5):
        x = bx + i * 36; f = clamp(pa * 5 - i)
        d.rounded_rectangle((x, y2 - 22, x + 28, y2 + 22), 8, fill=(236, 230, 240), outline=(200, 186, 205), width=2)
        if f > 0: d.rounded_rectangle((x + 3, y2 + 19 - 38 * f, x + 25, y2 + 19), 6, fill=(110, 170, 255) if pa > .3 else (255, 150, 90))
    aviso_voto(c, T)

AVISOS = []
def aviso_voto(c, T):
    for t0 in AVISOS:
        if not (t0 <= T < t0 + 5): continue
        u = ease((T - t0) / .35) if T < t0 + 4.6 else 1 - ease((T - t0 - 4.6) / .35)
        y = 346 + 20 * (1 - u); a = int(255 * u)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        w2 = 330 * (1 + .03 * math.sin((T - t0) * 8))
        d.rounded_rectangle((540 - w2, y, 540 + w2, y + 74), 37, fill=(255, 255, 255, a), outline=OL + (a,), width=5)
        d.ellipse((540 - w2 + 10, y + 9, 540 - w2 + 66, y + 65), fill=AZ + (a,)); d.text((540 - w2 + 38, y + 37), "A", font=font(F_ANTON, 38), fill=WHITE + (a,), anchor="mm")
        d.ellipse((540 + w2 - 66, y + 9, 540 + w2 - 10, y + 65), fill=VERDE + (a,)); d.text((540 + w2 - 38, y + 37), "B", font=font(F_ANTON, 38), fill=WHITE + (a,), anchor="mm")
        d.text((540, y + 24), "¿TÚ QUÉ HARÍAS? VOTA AL FINAL", font=font(F_ANTON, 27), fill=OL + (a,), anchor="mm")
        d.text((540, y + 54), "y dime en comentarios por qué", font=font(F_UI, 23), fill=(200, 50, 80, a), anchor="mm")
        c.alpha_composite(lay)

# ---------------------------------------------------------------- piezas dibujadas
def manuscrito(c, lines, T, t0, t1, x, y, size=58, col=(200, 40, 40), lh=78, rot=0):
    """Escribe líneas a mano (Caveat) letra a letra entre t0 y t1."""
    total = sum(len(l) for l in lines); n = int(total * clamp((T - t0) / max(.1, t1 - t0)))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); f = font(F_HAND, size)
    for i, l in enumerate(lines):
        if n <= 0: break
        d.text((x, y + i * lh), l[:n], font=f, fill=col, anchor="ls"); n -= len(l)
    if rot: lay = lay.rotate(rot, center=(x, y), resample=Image.BICUBIC)
    c.alpha_composite(lay)

def celular(c, cx, cy, s, T, contenido, shake=0):
    w, h = 520 * s, 1000 * s
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    sx = shake * math.sin(T * 90)
    x0, y0 = cx - w / 2 + sx, cy - h / 2
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 60 * s, fill=(28, 26, 36), outline=OL, width=8)
    d.rounded_rectangle((x0 + 22 * s, y0 + 22 * s, x0 + w - 22 * s, y0 + h - 22 * s), 44 * s, fill=(246, 241, 234))
    d.rounded_rectangle((cx - 70 * s + sx, y0 + 34 * s, cx + 70 * s + sx, y0 + 62 * s), 14 * s, fill=(28, 26, 36))
    contenido(d, lay, x0 + 22 * s, y0 + 22 * s, w - 44 * s, h - 44 * s, s)
    c.alpha_composite(lay)

def burbuja(d, x, y, w, nombre, txt, s, col=(255, 255, 255)):
    lines = txt.split("\n"); h = (70 + 44 * len(lines)) * s
    d.rounded_rectangle((x, y, x + w, y + h), 26 * s, fill=col, outline=(210, 200, 190), width=2)
    d.text((x + 24 * s, y + 34 * s), nombre, font=font(F_UI, int(26 * s)), fill=(214, 84, 120), anchor="lm")
    for i, l in enumerate(lines): d.text((x + 24 * s, y + (78 + 44 * i) * s), l, font=font(F_UI, int(30 * s)), fill=OL, anchor="lm")
    return h

def charco(c, cx, cy, T, t0, sc=1.0):
    if T < t0: return
    u = ease((T - t0) / 1.0)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k, (dx, dy, r) in enumerate(((0, 0, 260), (-160, 90, 150), (170, 70, 170), (40, 190, 140), (-60, -120, 120))):
        dx, dy, r = dx * sc, dy * sc, r * sc
        rr = r * u * (1 + .04 * math.sin(T * 3 + k))
        d.ellipse((cx + dx * u - rr, cy + dy * u - rr * .7, cx + dx * u + rr, cy + dy * u + rr * .7), fill=(252, 250, 244, 245))
    c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(2)))
    d = ImageDraw.Draw(c)
    for k in range(4):
        x = cx + (-120 + k * 80) * sc; y = cy + (-40 + 30 * math.sin(k)) * sc
        d.ellipse((x - 18, y - 8, x + 18, y + 8), fill=(255, 255, 255))


# ---------------------------------------------------------------- letras sobre la pauta
HOJA_FILAS = ((120, 200, 280), (380, 460, 540))   # (línea de arriba, punteada, base) en coordenadas de la hoja
def fila(cx, cy, s, n):
    top, mid, base = HOJA_FILAS[n]
    y0 = cy - 340 * s
    return y0 + top * s, y0 + base * s

def palabra(c, word, cx, cy, s, n, T, tiempos=None, col=(40, 60, 160), punteado=False, track=.06):
    """Escribe 'word' con letra escolar dentro de la fila n de la hoja (mayúsculas: de la línea de arriba a la base)."""
    ytop, ybase = fila(cx, cy, s, n)
    capH = (ybase - ytop) * .96
    f0 = font(F_ESC, 100); bb = f0.getbbox("M"); ratio = (bb[3] - bb[1]) / 100
    size = capH / ratio; f = font(F_ESC, size)
    adv = [f.getlength(L) for L in word]; gap = size * track
    total = sum(adv) + gap * (len(word) - 1)
    if total > 780 * s:   # si no cabe a lo ancho, letras algo más bajas pero apoyadas en la base
        k = 780 * s / total; size *= k; capH *= k; f = font(F_ESC, size); adv = [f.getlength(L) for L in word]; gap = size * track
        total = sum(adv) + gap * (len(word) - 1)
    x = cx - total / 2
    tiempos = tiempos or [-1] * len(word)
    xs = []
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for L, a, t in zip(word, adv, tiempos):
        xs.append((x, x + a))
        if T >= t:
            k = popscale(T, t, .3) if t >= 0 else 1
            if k >= .999: d.text((x, ybase), L, font=f, fill=col, anchor="ls")
            else:
                g = Image.new("RGBA", (int(a * 2 + 20), int(size * 2)), (0, 0, 0, 0))
                ImageDraw.Draw(g).text((g.width / 2, size * 1.4), L, font=f, fill=col, anchor="ms")
                kk = max(.05, k); g = g.resize((max(1, int(g.width * kk)), max(1, int(g.height * kk))))
                cxl, cyl = x + a / 2, ybase - capH / 2
                lay.alpha_composite(g, (int(cxl - g.width / 2), int(cyl - (size * 1.4 - capH / 2) * kk)))
        x += a + gap
    if punteado:
        m = np.array(lay); m[((np.arange(H) // 9) % 2) == 0, :, 3] = 0
        lay = Image.fromarray(m)
    c.alpha_composite(lay)
    return xs

PINTI = Image.open(os.path.join(HERE, "..", "pinti-organico", "assets", "pinti.png")).convert("RGBA")
def pinti(c, cx, cy, h, rot=0):
    p = PINTI.resize((int(PINTI.width * h / PINTI.height), int(h)), Image.LANCZOS)
    if rot: p = p.rotate(rot, expand=True, resample=Image.BICUBIC)
    c.alpha_composite(p, (int(cx - p.width / 2), int(cy - p.height / 2)))

def brillos(c, T, t0, cx, cy, r0=120):
    if T < t0: return
    d = ImageDraw.Draw(c)
    for i in range(7):
        a = i * 0.9 + T * .8; r = r0 + 30 * math.sin(T * 3 + i)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a) * .7
        s = 10 + 6 * math.sin(T * 6 + i)
        d.polygon([(x, y - s * 2), (x + s * .5, y - s * .5), (x + s * 2, y), (x + s * .5, y + s * .5), (x, y + s * 2), (x - s * .5, y + s * .5), (x - s * 2, y), (x - s * .5, y - s * .5)], fill=(255, 240, 150))

def confeti(c, T, t0, n=60):
    if T < t0 or T > t0 + 3: return
    d = ImageDraw.Draw(c); r = __import__("random").Random(7)
    for i in range(n):
        x0 = r.uniform(0, W); vy = r.uniform(500, 900); vx = r.uniform(-120, 120); col = r.choice([ROSA, YEL, VERDE, AZ, (255, 160, 80)])
        t = T - t0; x = x0 + vx * t + 30 * math.sin(t * 6 + i); y = -40 + vy * t
        a = t * 8 + i; s = 14
        d.polygon([(x + s * math.cos(a), y + s * math.sin(a)), (x + s * math.cos(a + 2.4), y + s * math.sin(a + 2.4)), (x + s * math.cos(a + 3.9), y + s * math.sin(a + 3.9))], fill=col)


# ---------------------------------------------------------------- motor de escritura: trazos reales con la mano de Mateo
VERDE_C = (58, 168, 72)
_RNG = np.random.default_rng(5)
_GRANO = Image.fromarray((_RNG.random((H, W)) * 70 + 185).astype(np.uint8))   # textura de cera de la crayola

def _arco(cx, cy, r, a0, a1, n=18):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

def letra_trazos(L, x, yt, yb):
    """Trazos de una mayúscula escolar (orden y sentido reales de escritura) dentro de [yt, yb]. Devuelve (trazos, ancho)."""
    h = yb - yt; ym = yt + h * .5
    if L == "R":
        r = h * .25
        return [[(x, yt), (x, yb)], [(x, yt), (x + h * .3, yt)] + _arco(x + h * .3, yt + r, r, -90, 90)[1:] + [(x, ym)], [(x + h * .22, ym), (x + h * .62, yb)]], h * .62
    if L == "E":
        return [[(x, yt), (x, yb)], [(x, yt), (x + h * .52, yt)], [(x, ym), (x + h * .44, ym)], [(x, yb), (x + h * .52, yb)]], h * .52
    if L == "X":
        return [[(x, yt), (x + h * .62, yb)], [(x + h * .62, yt), (x, yb)]], h * .62
    if L == "M":
        return [[(x, yb), (x, yt), (x + h * .36, yb * .62 + yt * .38), (x + h * .72, yt), (x + h * .72, yb)]], h * .72
    if L == "A":
        return [[(x, yb), (x + h * .32, yt), (x + h * .64, yb)], [(x + h * .14, yt + h * .62), (x + h * .5, yt + h * .62)]], h * .64
    if L == "T":
        return [[(x, yt), (x + h * .6, yt)], [(x + h * .3, yt), (x + h * .3, yb)]], h * .6
    if L == "O":
        return [_arco(x + h * .34, yt + h * .5, h * .5, -90, 270, 36)], h * .68
    return [], h * .5

def palabra_trazos(word, cx, yt, yb):
    """Trazos de toda la palabra, centrada en cx y apoyada entre la línea de arriba y la base."""
    h = yb - yt; gap = h * .22
    ws = [letra_trazos(L, 0, yt, yb)[1] for L in word]
    x = cx - (sum(ws) + gap * (len(word) - 1)) / 2; out = []
    for L, w in zip(word, ws):
        out.append(letra_trazos(L, x, yt, yb)[0]); x += w + gap
    return out   # lista por letra de listas de trazos

def _largo(p): return sum(math.dist(p[i], p[i + 1]) for i in range(len(p) - 1))

def _recorrido(trazos, u):
    """Parte dibujada de los trazos con progreso u (0..1) y la posición de la punta. Entre trazos la mano se levanta y viaja."""
    segs = []   # (puntos, dibuja?)
    for i, p in enumerate(trazos):
        if i: segs.append(([trazos[i - 1][-1], p[0]], False))
        segs.append((p, True))
    pesos = [_largo(p) * (1 if dib else .55) + (0 if dib else 1) for p, dib in segs]
    objetivo = clamp(u) * sum(pesos); hechos = []; tip = trazos[0][0]; arriba = False
    for (p, dib), wgt in zip(segs, pesos):
        if objetivo >= wgt:
            if dib: hechos.append(p)
            objetivo -= wgt; tip = p[-1]; continue
        f = objetivo / max(wgt, 1e-6); lt = _largo(p) * f; acc = 0; parc = [p[0]]
        for a, b in zip(p, p[1:]):
            dd = math.dist(a, b)
            if acc + dd >= lt:
                k = (lt - acc) / max(dd, 1e-6); tip = (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k); parc.append(tip); break
            acc += dd; parc.append(b); tip = b
        if dib and len(parc) > 1: hechos.append(parc)
        arriba = not dib
        break
    return hechos, tip, arriba

def dibuja_trazos(c, trazos, w, col=VERDE_C):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for p in trazos:
        if len(p) > 1: d.line(p, fill=col, width=int(w), joint="curve")
        for q in (p[0], p[-1]): d.ellipse((q[0] - w / 2, q[1] - w / 2, q[0] + w / 2, q[1] + w / 2), fill=col)
    a = np.array(lay); a[..., 3] = (a[..., 3].astype(np.uint16) * np.array(_GRANO) // 255).astype(np.uint8)
    c.alpha_composite(Image.fromarray(a))

def puntitos(c, trazos, h, col=(150, 160, 200)):
    """Letra de puntitos de las hojas para repasar: puntos a lo largo del trazo."""
    d = ImageDraw.Draw(c); paso = h * .085; r = h * .028
    for p in trazos:
        acc = 0
        for a, b in zip(p, p[1:]):
            dd = math.dist(a, b); t = (paso - acc) % paso if acc else 0
            while t <= dd:
                x, y = a[0] + (b[0] - a[0]) * t / dd, a[1] + (b[1] - a[1]) * t / dd
                d.ellipse((x - r, y - r, x + r, y + r), fill=col); t += paso
            acc = (acc + dd) % paso

def mano_crayola(c, tip, T, sm=.6, arriba=False, temblor=1.5):
    """La mano de Mateo con la crayola: la punta exactamente en 'tip' (se levanta un poco entre trazos)."""
    dx, dy = temblor * math.sin(T * 47), temblor * math.cos(T * 39)
    lift = -18 if arriba else 0
    put(c, "mano_crayola", tip[0] + (900 - 150) * sm + dx, tip[1] + (900 - 830) * sm + dy + lift, sm)

def escribir(c, letras, T, t0, t1, w, sm=.6, mano=True, entra=.5):
    """Escribe las letras (lista de listas de trazos) de t0 a t1 con la mano siguiendo la punta. Devuelve (tip, nº letras acabadas)."""
    todos = [p for L in letras for p in L]
    if T < t0:
        if mano and T >= t0 - entra:   # la mano entra desde abajo a la derecha hasta el primer punto
            k = ease((T - t0 + entra) / entra); p0 = todos[0][0]
            mano_crayola(c, (p0[0] + 500 * (1 - k), p0[1] + 700 * (1 - k)), T, sm, True)
        return None, 0
    u = (T - t0) / max(.2, t1 - t0)
    hechos, tip, arriba = _recorrido(todos, u)
    dibuja_trazos(c, hechos, w)
    if mano:
        if u <= 1: mano_crayola(c, tip, T, sm, arriba)
        else:   # termina: la mano se retira
            k = ease((T - t1) / .5)
            if k < 1: mano_crayola(c, (tip[0] + 500 * k, tip[1] + 700 * k), T, sm, True)
    return tip, u

def fines(letras, t0, t1):
    """Momento en que se termina cada letra (para el check / el sonido)."""
    todos = [p for L in letras for p in L]; pesos = []
    for i, p in enumerate(todos):
        if i: pesos.append(math.dist(todos[i - 1][-1], p[0]) * .55 + 1)
        pesos.append(_largo(p))
    tot = sum(pesos); out = []; k = 0; acc = 0
    for L in letras:
        for j in range(len(L)):
            if k: acc += pesos[2 * k - 1]
            acc += pesos[2 * k if k == 0 else 2 * k]; k += 1
        out.append(t0 + (t1 - t0) * acc / tot)
    return out

def seguir(c, tx, ty, z, cx=540, cy=960, f=.55):
    """Cámara que se acerca y sigue la punta de la crayola (zoom z), para que se vea bien cómo escribe."""
    if z <= 1.001: return c
    px, py = cx + (tx - cx) * f, cy + (ty - cy) * f
    w, h = W / z, H / z
    x0 = min(max(px - w / 2, 0), W - w); y0 = min(max(py - h / 2, 0), H - h)
    return c.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.BICUBIC)

def rex_nino_trazos(x, y, sz, cola=True):
    """REX a lo Mateo: R grande, E con CUATRO rayitas, X chueca y una cola en la última letra (con temblor de niño)."""
    def tb(p, s=1.0):
        return [(a + sz * .025 * s * math.sin(b * .05 + a * .03), b + sz * .02 * s * math.cos(a * .045)) for a, b in p]
    r = sz * .26
    R = [tb([(x, y), (x + 3, y + sz)]), tb([(x, y)] + [(x + sz * .2, y)] + _arco(x + sz * .2, y + r, r, -90, 90, 14) + [(x + 6, y + sz * .52)]),
         tb([(x + sz * .14, y + sz * .52), (x + sz * .48, y + sz * 1.02)])]
    ex = x + sz * .72
    E = [tb([(ex, y + 4), (ex - 6, y + sz)])] + [tb([(ex - 2, y + i * sz / 3 + (8 if i == 2 else 0)), (ex + sz * (.44 if i in (0, 3) else .34), y + i * sz / 3 - (10 if i == 1 else 0))]) for i in range(4)]
    xx = ex + sz * .74
    X = [tb([(xx, y + sz * .08), (xx + sz * .52, y + sz * .98)], 1.6), tb([(xx + sz * .62, y - sz * .06), (xx - sz * .04, y + sz * .84)], 1.6)]
    if cola:
        X.append([(xx + sz * .52 + sz * .55 * t, y + sz * .98 - sz * .28 * math.sin(t * 3.2)) for t in np.linspace(0, 1, 16)])
    return [R, E, X]

def rex_nino_full(c, x, y, sz):
    dibuja_trazos(c, [p for L in rex_nino_trazos(x, y, sz) for p in L], sz * .1)


def corazones(c, T, t0, cx, cy):
    if T < t0: return
    d = ImageDraw.Draw(c)
    for i in range(9):
        ph = ((T - t0) * .5 + i / 9) % 1
        x = cx + 380 * math.sin(i * 2.1) + 30 * math.sin(T * 2 + i); y = cy + 300 - 700 * ph
        corazon(d, x, y, 22 + 10 * math.sin(i), (255, 120, 150, int(255 * (1 - ph))))


RAYO = [(600, 0), (560, 520), (612, 560), (522, 1100), (578, 1132), (480, H)]
_FC = {}
def _opcion(d, cx, cy, letra, t1, t2, t3, col, k, big=1.0):
    r = 82 * k * big
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col, outline=WHITE, width=8)
    text(d, (cx, cy), letra, 116 * k * big, WHITE)
    if k > .5:
        for i, l in enumerate(t1.split("\n")):
            text(d, (cx, cy + 146 + i * 66), l, 60 * big, WHITE, stroke=7)
        off = 66 * (len(t1.split("\n")) - 1)
        text(d, (cx, cy + 230 + off), t2, 36, (150, 255, 170), "mm", F_UI, stroke=6)
        text(d, (cx, cy + 280 + off), t3, 34, (255, 170, 160), "mm", F_UI, stroke=6)


# ---------------------------------------------------------------- escenas de la Parte 3 (ganó la A: Rex le enseña su nombre)
HOJA = (540, 900, 1.05)
NOCHE_AZ = (20, 26, 70)

def nino_trazos(word, x, y, sz, erev=False, seed=0):
    """Letras escritas por Mateo a mano alzada (temblor de niño). erev: la E le sale al revés."""
    out = []; cx = x
    def tb(p):
        return [(a + sz * .03 * math.sin(b * .05 + a * .031 + seed), b + sz * .025 * math.cos(a * .043 + seed)) for a, b in p]
    for i, L in enumerate(word):
        tr, w = letra_trazos(L, 0, y, y + sz * (1 + .06 * math.sin(i * 2.3 + seed)))
        if L == "E" and erev: tr = [[(w - a, b) for a, b in p] for p in tr]
        out.append([tb([(a + cx, b + sz * .05 * math.sin(i * 1.7)) for a, b in p]) for p in tr]); cx += w + sz * .24
    return out

def ancho_nino(word, sz): return sum(letra_trazos(L, 0, 0, sz)[1] for L in word) + sz * .24 * (len(word) - 1)

def nino_full(c, word, x, y, sz, erev=False, col=VERDE_C, seed=0):
    dibuja_trazos(c, [p for L in nino_trazos(word, x, y, sz, erev, seed) for p in L], sz * .1, col)

def tarjeta(c, T, t0, txt, sub=None):
    """Tarjeta de noche/día: cielo oscuro con luna, título enorme."""
    c.alpha_composite(Image.new("RGBA", (W, H), NOCHE_AZ + (215,)))
    d = ImageDraw.Draw(c); k = popscale(T, t0, .4)
    d.ellipse((700, 470, 860, 630), fill=(255, 236, 170)); d.ellipse((745, 450, 905, 610), fill=NOCHE_AZ)
    for i in range(14):
        x, y = (i * 173) % 1000 + 40, 420 + (i * 97) % 380; r = 3 + (i % 3) * 2 + 1.5 * math.sin(T * 4 + i)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 250, 220))
    text(d, (540, 940), txt, int(200 * max(k, .01)), WHITE, stroke=14, sfill=(214, 84, 120))
    if sub and k > .9: text(d, (540, 1110), sub, 54, (255, 236, 170), stroke=6)

LETRA_OK = {"E": -9, "M": 99, "A": 99, "T": 99, "O": 99}   # se rellena abajo con los tiempos reales

def mano_dino(c, tip, T, s=.17):
    """Rex chiquito subiendo por el trazo, justo encima de la punta de la crayola."""
    put(c, "dino", tip[0] - 30, tip[1] - 95 + 6 * math.sin(T * 14), s, rot=8 * math.sin(T * 7))

def hoja_mateo(c, T, solidas, punteadas):
    """Hoja con MATEO en la fila de arriba: letras ya aprendidas en verde, las que faltan en puntitos."""
    put(c, "hoja", *HOJA); pinti(c, 920, 640, 150, rot=-8)
    yt, yb = fila(*HOJA, 0); h = yb - yt
    letras = palabra_trazos("MATEO", 540, yt, yb)
    for i, L in enumerate("MATEO"):
        if L in punteadas: puntitos(c, letras[i], h)
        if L in solidas: dibuja_trazos(c, letras[i], h * .13)
    return letras, yt, yb, h

def sc_llegas(T):
    """F01: ganó la A. Llegas del trabajo de noche, agotada; Mateo te espera con Rex. Solo 20 minutos."""
    s0, e0 = TL["F01"]
    c = bg("bg_puerta", T, s0, 1.12, 1.2, 8, .5, .5)
    c.alpha_composite(Image.new("RGBA", (W, H), NOCHE_AZ + (120,)))
    mateo(c, "feliz", 470, 1260, .95, T)
    put(c, "dino", 820, 1480, .45, rot=5 * math.sin(T * 3))
    d = ImageDraw.Draw(c)
    tp = WT("F01", "Pero")
    if T < tp:   # resultado de la encuesta, rápido
        k = max(.02, popscale(T, 0, .3)); y = 470
        d.rounded_rectangle((540 - 400 * k, y - 80, 540 + 400 * k, y + 80), 36, fill=WHITE, outline=NAVY, width=6)
        if k > .8:
            d.ellipse((170, y - 50, 270, y + 50), fill=AZ, outline=WHITE, width=5); d.text((220, y + 2), "A", font=font(F_ANTON, 60), fill=WHITE, anchor="mm")
            d.text((300, y - 34), "Rex le enseña su nombre", font=font(F_BAL, 34), fill=NAVY, anchor="lm")
            u = ease((T - .3) / .7)
            d.rounded_rectangle((300, y + 4, 900, y + 44), 20, fill=(236, 228, 236))
            if u > .05: d.rounded_rectangle((300, y + 4, 300 + 600 * .91 * u, y + 44), 20, fill=AZ)
            d.text((905, y - 34), f"{int(91 * u)}%", font=font(F_BAL, 40), fill=AZ, anchor="rm")
    else:
        ta = WT("F01", "agotada…")
        if T >= ta: stamp(c, T, ta, "AGOTADA", 540, 520, ROJO, -5, 96)
        tv = WT("F01", "veinte")
        if T >= tv:   # reloj de 20 minutos
            k = popscale(T, tv, .35); cx, cy, r = 540, 760, 120 * k
            d = ImageDraw.Draw(c)
            d.ellipse((cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10), fill=NAVY)
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=WHITE)
            if k > .9:
                u = clamp((T - tv) / 3)
                d.pieslice((cx - r + 12, cy - r + 12, cx + r - 12, cy + r - 12), -90, -90 + 360 * (1 - u), fill=(255, 205, 210))
                d.text((cx, cy - 6), "20:00", font=font(F_BAL, 64), fill=NAVY, anchor="mm")
                d.text((cx, cy + 50), "MIN", font=font(F_BAL, 30), fill=(214, 84, 120), anchor="mm")
    return c

def sc_m(T):
    """F02: noche 1. Rex: la M son dos montañas. Mateo repasa la M: sube, baja, sube, baja (cada tramo con su palabra)."""
    s0, e0 = TL["F02"]; tr = WT("F02", "Rex")
    if T < tr - .05:
        c = bg("bg_mesa", T, s0, 1.2, 1.3, 4, .5, .5); tarjeta(c, T, s0 - .2, "NOCHE 1", "20 minutos"); return c
    c = bg("bg_mesa", T, tr, 1.2, 1.3, 6, .5, .5)
    c.alpha_composite(Image.new("RGBA", (W, H), NOCHE_AZ + (50,)))
    letras, yt, yb, h = hoja_mateo(c, T, "E", "MATO")
    M = letras[0][0]   # un solo trazo de 5 puntos: 4 tramos
    tramos = [[M[i], M[i + 1]] for i in range(4)]
    tws = [WT("F02", "Sube…"), WT("F02", "baja…"), WT("F02", "sube…", 2), WT("F02", "baja.")]
    tip = None
    for i, (p, t) in enumerate(zip(tramos, tws)):
        t1 = t + .55
        if T >= t1: dibuja_trazos(c, [p], h * .13)
        elif T >= t - .05:
            tip, u = escribir(c, [[p]], T, t, t1, h * .13, .55, entra=.01)
    if tip is None:   # entre tramo y tramo: la mano espera en el último punto
        hechos = [i for i, t in enumerate(tws) if T >= t + .55]
        tip = M[hechos[-1] + 1] if hechos else M[0]
        if T < tws[-1] + 1.4:
            if not hechos and T < tws[0]:
                k = ease((T - tr) / .6); mano_crayola(c, (tip[0] + 400 * (1 - k), tip[1] + 600 * (1 - k)), T, .55, True)
            else: mano_crayola(c, tip, T, .55, True)
    mano_dino(c, tip, T)
    tm = WT("F02", "montañas.")
    c = seguir(c, tip[0], tip[1], 1.4, f=.6)
    if T >= tm - .1 and T < tws[0]: etiqueta(c, T, tm - .1, "2 MONTAÑAS", 540, 1200, CREMA, OL, 40)
    for i, t in enumerate(tws):
        if t <= T < t + .7: etiqueta(c, T, t, ["SUBE", "BAJA", "SUBE", "BAJA"][i], 540, 1200, VERDE if i % 2 == 0 else ROSA, WHITE, 46)
    return c

def letra_grande(c, L, cx, cy, sz, T, t0, col=(63, 174, 74)):
    k = popscale(T, t0, .45)
    if k <= 0: return
    ImageDraw.Draw(c).text((cx, cy), L, font=font(F_ESC, max(10, int(sz * k))), fill=col, anchor="mm", stroke_width=int(9 * k), stroke_fill=WHITE)

def sc_rex_m(T):
    """F03: '¡Rex subió las montañas!' Mateo feliz con su primera letra nueva."""
    s0, e0 = TL["F03"]
    c = bg("bg_cocina", T, s0 - .2, 1.2, 1.28, 6, .5, .6)
    c.alpha_composite(Image.new("RGBA", (W, H), NOCHE_AZ + (50,)))
    mateo(c, "feliz", 420, 1260, 1.05, T, "F03")
    letra_grande(c, "M", 820, 760, 380, T, s0)
    put(c, "dino", 830 + 60 * math.sin(T * 4), 560 - 40 * abs(math.sin(T * 5)), .3, rot=10 * math.sin(T * 5))
    brillos(c, T, s0 + .2, 820, 760, 200)
    return c

def chat(d, lay, x, y, w, h, s, T):
    """Grupo de WhatsApp de las mamás del salón."""
    d.rectangle((x, y, x + w, y + 120 * s), fill=(40, 120, 90))
    d.text((x + 40 * s, y + 52 * s), "Mamás Preescolar B", font=font(F_UI, int(30 * s)), fill=WHITE, anchor="lm")
    d.text((x + 40 * s, y + 92 * s), "32 participantes", font=font(F_UI, int(20 * s)), fill=(200, 235, 215), anchor="lm")
    d.rectangle((x, y + 120 * s, x + w, y + h), fill=(236, 229, 221))
    yy = y + 150 * s
    msgs = [(S("F04") - .2, "Andrea", "¿Mañana hay que llevar\nalgo para la exposición?", None),
            (WT("F05", "Sofía") - .2, "Laura · mamá de Sofía", "Sofía ya escribe su\nnombre completo ♥", "SOFÍA"),
            (WT("F05", "completo.") + .3, "Paty", "¡Qué lista! Felicidades", None),
            (WT("F05", "Dejas") - .1, "Caro", "¡Bravo, Sofi!", None)]
    for t, nom, txt, foto in msgs:
        if T < t: continue
        k = ease((T - t) / .25)
        bh = burbuja(d, x + 24 * s, yy + 20 * (1 - k), w * .8, nom, txt, s)
        yy += bh + 16 * s
        if foto:
            fh = 170 * s
            d.rounded_rectangle((x + 24 * s, yy, x + 24 * s + w * .62, yy + fh), 20 * s, fill=WHITE)
            d.rounded_rectangle((x + 40 * s, yy + 16 * s, x + 8 * s + w * .62, yy + fh - 16 * s), 12 * s, fill=(250, 247, 236))
            d.text((x + 24 * s + w * .31, yy + fh / 2), foto, font=font(F_ESC, int(64 * s)), fill=(214, 84, 120), anchor="mm")
            yy += fh + 16 * s

def sc_grupo(T):
    """F04-F05: el grupo de mamás. 'Sofía ya escribe su nombre completo'. Dejas el celular boca abajo."""
    s0 = S("F04"); tb = WT("F05", "boca")
    if T < tb + .3:
        c = bg("bg_noche", T, s0, 1.0, 1.06, 12)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        put(lay, "manos_atras", 540, 960, 1.0); celular(lay, 540, 1000, 1.25, T, lambda d, l, x, y, w, h, s: chat(d, l, x, y, w, h, s, T)); put(lay, "manos_delante", 540, 960, 1.0)
        if T >= tb:   # lo giras: se aplasta como una carta
            k = clamp((T - tb) / .3); hh = max(2, int(H * (1 - k)))
            lay = lay.resize((W, hh), Image.BILINEAR); tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0)); tmp.alpha_composite(lay, (0, (H - hh) // 2)); lay = tmp
        k = ease((T - s0 + .1) / .5); c.alpha_composite(lay, (0, int(400 * (1 - k))))
        return c
    c = bg("bg_mesa", T, tb, 1.15, 1.2, 4, .5, .5)
    c.alpha_composite(Image.new("RGBA", (W, H), NOCHE_AZ + (140,)))
    d = ImageDraw.Draw(c)   # el celular boca abajo sobre la mesa
    d.rounded_rectangle((300, 620, 780, 1500), 70, fill=(36, 34, 46), outline=OL, width=8)
    d.rounded_rectangle((350, 670, 500, 850), 40, fill=(54, 52, 66))
    for cx_, cy_ in ((395, 715), (455, 715), (395, 800)): d.ellipse((cx_ - 22, cy_ - 22, cx_ + 22, cy_ + 22), fill=(20, 20, 26), outline=(90, 90, 110), width=3)
    if T >= tb + .5: etiqueta(c, T, tb + .5, "NO ERES LA ÚNICA", 540, 470, CREMA, OL, 40)
    return c

def hojita_hojas(c, x, y, k):
    """Copa del árbol sobre la T."""
    d = ImageDraw.Draw(c)
    for dx, dy, r in ((0, -40, 52), (-48, -14, 40), (48, -14, 40), (-26, -66, 34), (26, -66, 34)):
        rr = r * k; d.ellipse((x + dx * k - rr, y + dy * k - rr, x + dx * k + rr, y + dy * k + rr), fill=(120, 200, 110), outline=(60, 140, 70), width=3)

def sc_noche2(T):
    """F06: noche 2. La A es la tienda de Rex (Rex se mete dentro), la T un árbol (le salen hojas)."""
    s0, e0 = TL["F06"]; tl = WT("F06", "La")
    if T < tl - .05:
        c = bg("bg_mesa", T, s0, 1.2, 1.3, 4, .5, .5); tarjeta(c, T, s0 - .8, "NOCHE 2"); return c
    c = bg("bg_mesa", T, tl, 1.2, 1.3, 6, .5, .5)
    c.alpha_composite(Image.new("RGBA", (W, H), NOCHE_AZ + (50,)))
    letras, yt, yb, h = hoja_mateo(c, T, "ME", "ATO")
    ta0, ta1 = WT("F06", "A") - .1, WT("F06", "tienda") + .6
    tt0, tt1 = WT("F06", "T,") - .1, e0 + .35
    tip = None
    for ls, a, b in (([letras[1]], ta0, ta1), ([letras[2]], tt0, tt1)):
        if T >= b: dibuja_trazos(c, [p for L in ls for p in L], h * .13)
        elif T >= a - .3:
            tip, u = escribir(c, ls, T, a, b, h * .13, .55, entra=.3)
    if tip is None and ta1 <= T < tt0 - .3:
        tip = letras[1][-1][-1]; mano_crayola(c, tip, T, .55, True)
    # la tienda: Rex se asoma dentro de la A
    if T >= ta1:
        xs = [q[0] for p in letras[1] for q in p]; ax = (min(xs) + max(xs)) / 2
        k = popscale(T, ta1, .4); put(c, "dino", ax, yb - 34, .14 * k)
    if T >= tt1:
        xs = [q[0] for p in letras[2] for q in p]; tx = (min(xs) + max(xs)) / 2
        hojita_hojas(c, tx, yt + 8, popscale(T, tt1, .4) * .9)
    c = seguir(c, tip[0] if tip else 540, tip[1] if tip else (yt + yb) / 2, 1.4, f=.6)
    if T >= ta1: etiqueta(c, T, ta1, "LA A = LA TIENDA DE REX", 540, 1200, CREMA, OL, 38) if T < tt0 else None
    if T >= tt1 - .2: etiqueta(c, T, tt1 - .2, "LA T = UN ÁRBOL", 540, 1200, CREMA, OL, 38)
    return c

def sc_no_sale(T):
    """F07: '¡No me sale! ¡Ya no quiero!' Mateo llora."""
    s0, e0 = TL["F07"]
    c = bg("bg_cocina", T, s0 - .2, 1.15, 1.22, 8, .5, .6)
    c.alpha_composite(Image.new("RGBA", (W, H), NOCHE_AZ + (90,)))
    mateo(c, "llora", 540, 1260, 1.05, T, "F07"); lagrimas(c, 540, 1260, 1.05, T)
    return c

def sc_rompe(T):
    """F08: rompe la hoja en dos. Respiras... y sacas otra hoja limpia."""
    s0, e0 = TL["F08"]; tr = WT("F08", "Rompe") + .35; trs, to = WT("F08", "Respiras…"), WT("F08", "otra.")
    c = bg("bg_mesa", T, s0, 1.2, 1.28, 6, .5, .5)
    c.alpha_composite(Image.new("RGBA", (W, H), NOCHE_AZ + (60,)))
    hoja = Image.new("RGBA", (W, H), (0, 0, 0, 0)); put(hoja, "hoja", *HOJA)
    yt, yb = fila(*HOJA, 0)
    nino_full(hoja, "MAT", 300, yt, yb - yt, seed=3)
    ImageDraw.Draw(hoja).line([(420 + 30 * i, yt + 40 + 50 * (i % 2)) for i in range(9)], fill=VERDE_C, width=14)   # garabato de rabia
    if T < tr: c.alpha_composite(hoja)
    else:
        k = ease((T - tr) / .8)
        m = Image.new("L", (W, H), 0); pts = [(540 + 25 * math.sin(y * .05), y) for y in range(300, 1600, 30)]
        ImageDraw.Draw(m).polygon([(0, 0)] + [(540 + 25 * math.sin(300 * .05), 0)] + pts + [(540, H), (0, H)], fill=255)
        izq = Image.new("RGBA", (W, H), (0, 0, 0, 0)); izq.paste(hoja, (0, 0), m)
        der = Image.new("RGBA", (W, H), (0, 0, 0, 0)); der.paste(hoja, (0, 0), m.point(lambda v: 255 - v))
        if T < to - .2:
            c.alpha_composite(izq.rotate(14 * k, center=(540, 1300), resample=Image.BICUBIC), (int(-260 * k), int(80 * k)))
            c.alpha_composite(der.rotate(-14 * k, center=(540, 1300), resample=Image.BICUBIC), (int(260 * k), int(80 * k)))
    if trs <= T < to + .2:   # respiras: círculo que crece y se encoge
        u = (T - trs); r = 140 + 80 * math.sin(min(u, 2.0) * PI_ / 1.0 - PI_ / 2)
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((540 - r, 900 - r, 540 + r, 900 + r), fill=(255, 255, 255, 110))
        c.alpha_composite(g.filter(ImageFilter.GaussianBlur(20)))
        text(ImageDraw.Draw(c), (540, 900), "RESPIRA", 70, NAVY, stroke=0)
    if T >= to - .2:   # hoja nueva que entra desde abajo
        k = ease((T - to + .2) / .5); put(c, "hoja", 540, 900 + 1000 * (1 - k), 1.05)
    return c

def sc_noche3(T):
    """F09: noche 3. La O es el huevo de Rex... y por primera vez escribe su nombre él solo (con la E al revés, sin que nadie lo note)."""
    s0, e0 = TL["F09"]; tl = WT("F09", "La")
    if T < tl - .05:
        c = bg("bg_mesa", T, s0, 1.2, 1.3, 4, .5, .5); tarjeta(c, T, s0 - .8, "NOCHE 3"); return c
    c = bg("bg_mesa", T, tl, 1.2, 1.3, 6, .5, .5)
    c.alpha_composite(Image.new("RGBA", (W, H), NOCHE_AZ + (50,)))
    letras, yt, yb, h = hoja_mateo(c, T, "MATE", "O")
    to0, to1 = WT("F09", "O") - .1, WT("F09", "huevo") + .7
    y1, b1 = fila(*HOJA, 1); h1 = b1 - y1
    nombre = nino_trazos("MATEO", 540 - ancho_nino("MATEO", h1) / 2, y1, h1, erev=True, seed=1)
    tn0, tn1 = WT("F09", "primera") - .2, e0 + 1.1
    tip = None
    if T >= to1:
        dibuja_trazos(c, letras[4], h * .13)
        xs = [q[0] for q in letras[4][0]]; ox = (min(xs) + max(xs)) / 2; oy = (yt + yb) / 2
        k = popscale(T, to1, .4); d = ImageDraw.Draw(c)   # manchitas de huevo de dinosaurio
        for dx, dy, r in ((-18, -20, 12), (20, 4, 9), (-6, 28, 8)): d.ellipse((ox + dx * k - r * k, oy + dy * k - r * k, ox + dx * k + r * k, oy + dy * k + r * k), fill=(120, 200, 110))
    elif T >= to0 - .3: tip, u = escribir(c, [letras[4]], T, to0, to1, h * .13, .55, entra=.3)
    if T >= tn1: dibuja_trazos(c, [p for L in nombre for p in L], h1 * .1)
    elif T >= tn0 - .3: tip, u = escribir(c, nombre, T, tn0, tn1, h1 * .1, .55, entra=.3)
    elif T >= to1 and tip is None: tip = letras[4][0][-1]; mano_crayola(c, tip, T, .55, True)
    z = 1.4 if T < to1 + .2 else 1.4 - .3 * ease((T - to1 - .2) / .6)
    c = seguir(c, tip[0] if tip else 540, tip[1] if tip else (yt + b1) / 2, z, f=.55)
    if T >= to1 and T < tn0: etiqueta(c, T, to1, "LA O = EL HUEVO DE REX", 540, 1200, CREMA, OL, 38)
    if T >= tn1 - .3: stamp(c, T, tn1 - .3, "¡SU NOMBRE!", 540, 1250, VERDE, -5, 90)
    return c

def sc_lagrimas(T):
    """F10: se te llenan los ojos de lágrimas: Mateo levanta la hoja con su nombre y la imagen se nubla."""
    s0, e0 = TL["F10"]
    c = bg("bg_cocina", T, s0 - .3, 1.15, 1.2, 6, .5, .6)
    c.alpha_composite(Image.new("RGBA", (W, H), (255, 200, 120, 50)))
    mateo(c, "feliz", 540, 1330, .95, T)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); put(lay, "hoja", 540, 700, .62)
    nino_full(lay, "MATEO", 540 - ancho_nino("MATEO", 100) / 2, 600, 100, erev=True, seed=1)
    c.alpha_composite(lay.rotate(-3 + 2 * math.sin(T * 3), center=(540, 700), resample=Image.BICUBIC))
    corazones(c, T, s0, 540, 900)
    k = ease((T - WT("F10", "lágrimas.") + .3) / 1.2)
    if k > 0:   # visión borrosa de lágrimas, con gotas en los bordes
        c = Image.blend(c, c.filter(ImageFilter.GaussianBlur(10)), .75 * k)
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        for i in range(10):
            x = (i * 211) % W; y = ((i * 337) % 1200 + 500 + 120 * (T - s0)) % H; r = 30 + (i % 4) * 12
            gd.ellipse((x - r, y - r * 1.3, x + r, y + r * 1.3), fill=(200, 230, 255, int(90 * k)), outline=(255, 255, 255, int(140 * k)), width=3)
        c.alpha_composite(g)
    return c

def pared_expo(T, titulo=True):
    """La pared de la exposición: tres dibujos con nombres; el de Mateo en medio, con su E al revés."""
    c = Image.new("RGBA", (W, H), (238, 222, 196, 255)); d = ImageDraw.Draw(c)
    for x in range(0, W, 90): d.line((x, 0, x, H), fill=(230, 212, 184), width=3)
    d.rounded_rectangle((60, 520, 1020, 1380), 26, fill=(192, 146, 98), outline=(120, 82, 50), width=12)
    rnd = np.random.default_rng(2); g = Image.fromarray((rnd.random((860, 960)) * 60).astype(np.uint8))
    sh = Image.new("RGBA", (960, 860), (90, 60, 30, 255)); sh.putalpha(g); c.alpha_composite(sh, (60, 520))
    d = ImageDraw.Draw(c)
    if titulo: d.text((540, 470), "EXPOSICIÓN · PREESCOLAR B", font=font(F_BAL, 44), fill=NAVY, anchor="mm")
    for i, (x, rot, nom) in enumerate(((230, -4, "SOFÍA"), (540, 2, None), (850, 5, "LUCAS"))):
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); put(lay, "dibujo", x, 820, .5)
        lay = lay.rotate(rot, center=(x, 820), resample=Image.BICUBIC); c.alpha_composite(lay)
        d = ImageDraw.Draw(c)
        d.rounded_rectangle((x - 130, 1040, x + 130, 1170), 16, fill=WHITE, outline=(200, 190, 175), width=3)
        d.ellipse((x - 10, 1030, x + 10, 1050), fill=ROJO)
        if nom: d.text((x, 1108), nom, font=font(F_ESC, 60), fill=NAVY, anchor="mm")
        else: nino_full(c, "MATEO", x - ancho_nino("MATEO", 62) / 2, 1078, 62, erev=True, seed=1)
    return c

def siluetas(c, T):
    """Cabezas de los papás mirando, de espaldas, en primer plano."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for i, (x, y, r) in enumerate(((120, 1640, 120), (380, 1700, 130), (660, 1660, 125), (930, 1690, 135))):
        yy = y + 6 * math.sin(T * 2 + i)
        d.ellipse((x - r * 1.6, yy + r * .6, x + r * 1.6, yy + r * 3), fill=(46, 40, 66, 235))
        d.ellipse((x - r * .8, yy - r, x + r * .8, yy + r * .8), fill=(46, 40, 66, 235))
    c.alpha_composite(lay)

def sc_viernes(T):
    """F11: viernes. Todos los papás mirando la exposición... y ahí está su nombre. Con la E al revés."""
    s0, e0 = TL["F11"]; tt = WT("F11", "Todos")
    if T < tt - .05:
        c = bg("bg_puerta", T, s0, 1.2, 1.3, 4, .5, .5); tarjeta(c, T, s0 - .3, "VIERNES", "la exposición"); return c
    c = pared_expo(T); siluetas(c, T)
    tn, tr = WT("F11", "nombre."), WT("F11", "revés.")
    xE = 540 - ancho_nino("MATEO", 62) / 2 + letra_trazos("M", 0, 0, 62)[1] + letra_trazos("A", 0, 0, 62)[1] + letra_trazos("T", 0, 0, 62)[1] + 62 * .72
    z = 1.0 + .9 * ease((T - tn + .2) / .8) if T >= tn - .2 else 1.0 + .05 * (T - tt)
    fx, fy = (540, 1108) if T < tr - .3 else (540 + (xE + 16 - 540) * ease((T - tr + .3) / .5), 1108)
    c = seguir(c, fx, fy, z + (.5 * ease((T - tr + .3) / .5) if T >= tr - .3 else 0), cx=540, cy=960, f=1.0)
    if T >= tr:
        d = ImageDraw.Draw(c); k = clamp((T - tr) / .5)
        d.arc((345, 850, 605, 1110), -90, -90 + 360 * k, fill=ROJO, width=14)
        if T >= tr + .3: stamp(c, T, tr + .3, "¡AL REVÉS!", 540, 1300, ROJO, -6, 96)
    return c

def borrador(c, x, y, s, rot):
    lay = Image.new("RGBA", (int(260 * s), int(150 * s)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((4, 4, 256 * s, 146 * s), 22 * s, fill=(250, 140, 160), outline=OL, width=6)
    d.rectangle((150 * s, 8, 252 * s, 142 * s), fill=(110, 160, 235)); d.rounded_rectangle((4, 4, 256 * s, 146 * s), 22 * s, outline=OL, width=6)
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC); c.alpha_composite(lay, (int(x - lay.width / 2), int(y - lay.height / 2)))

def sc_risa(T):
    """F12: una mamá se ríe. Mateo te mira... y agarra el borrador."""
    s0, e0 = TL["F12"]; tm = WT("F12", "Mateo")
    if T < tm - .1:
        c = pared_expo(T); c = seguir(c, 540, 1000, 1.15, f=1.0); siluetas(c, T)
        tr = WT("F12", "ríe.")
        if T >= tr - .2:
            k = popscale(T, tr - .2, .3); d = ImageDraw.Draw(c)
            d.rounded_rectangle((60, 1250, 60 + 340 * k, 1250 + 120 * k), 40, fill=WHITE, outline=OL, width=6)
            d.polygon([(110, 1370 * k + 1250 * (1 - k)), (150, 1370 * k + 1250 * (1 - k)), (100, 1440)], fill=WHITE)
            if k > .8: d.text((230, 1310), "jajaja", font=font(F_BAL, 64), fill=(214, 84, 120), anchor="mm")
        return c
    c = pared_expo(T).filter(ImageFilter.GaussianBlur(8))
    mateo(c, "timido", 540, 1260, 1.0, T)
    tb = WT("F12", "borrador.")
    if T >= tb - .3:
        k = ease((T - tb + .3) / .4); borrador(c, 780 - 120 * (1 - k), 1520 - 300 * (1 - k), .9, 20)
    if T >= tb: etiqueta(c, T, tb, "¿LO BORRA?", 540, 470, CREMA, OL, 44)
    return c

# ---------------------------------------------------------------- final A/B (pantalla partida con rayo)
_FC = {}
def _lado(name):
    if name in _FC: return _FC[name]
    if name == "A":
        A = pared_expo(0, False); A = seguir(A, 540, 1000, 1.25, f=1.0)
        d = ImageDraw.Draw(A); corazon(d, 250, 760, 70, (255, 92, 130), outline=WHITE)
        A.alpha_composite(Image.new("RGBA", (W, H), (20, 90, 50, 70)))
    else:
        A = bg("bg_mesa", 0, 0, 1.2, 1.2, 1, .5, .5).convert("RGBA")
        put(A, "mateo_timido", 800, 1180 + 400 * .78, .78); borrador(A, 900, 1550, .8, 25)
        A.alpha_composite(Image.new("RGBA", (W, H), (40, 30, 90, 110)))
    _FC[name] = A
    return A

def sc_final(T):
    s0, e0 = TL["F13"]; ta, tb, tv = WT("F13", "A:"), WT("F13", "B:"), WT("F13", "Vota…")
    hiA = ta <= T < tb; hiB = tb <= T < tv
    A, B = _lado("A"), _lado("B")
    u = ease((T - s0 + .25) / .45)
    c = Image.new("RGBA", (W, H), (0, 0, 0, 255)); negro = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    c.alpha_composite(B if not hiA else Image.blend(B, negro, .45), (int(500 * (1 - u)), 0))
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon([(0, 0)] + RAYO + [(0, H)], fill=255)
    c.paste(A if not hiB else Image.blend(A, negro, .45), (int(-700 * (1 - u)), 0), mask)
    d = ImageDraw.Draw(c)
    if u > .9:
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).line(RAYO, fill=(255, 210, 120, 255), width=40, joint="curve")
        c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(c)
        d.line(RAYO, fill=WHITE, width=12, joint="curve"); d.line(RAYO, fill=YEL, width=5, joint="curve")
    k0 = popscale(T, s0, .4)
    text(d, (540, 220), "¿QUÉ HARÍAS TÚ?", 96 * max(k0, .01), YEL, stroke=8)
    for cx, L_, t1, t2, t3, col, t0, h in ((270, "A", "DEJARLO\nASÍ", "+ Orgulloso de él", "- Con la E al revés", AZ, ta, hiA),
                                           (790, "B", "QUE LO\nBORRE", "+ Lo aprende bien", "- Delante de todos", VERDE, tb, hiB)):
        k = popscale(T, t0, .35)
        if k > 0: _opcion(d, cx, 420, L_, t1, t2, t3, col, k, 1.08 if h else 1.0)
    if T >= tv - .1:
        k = popscale(T, tv - .1, .4)
        d.rounded_rectangle((540 - 390 * k, 1250, 540 + 390 * k, 1350), 50, fill=WHITE, outline=OL, width=6)
        if k > .5:
            text(d, (540, 1286), "VOTA EN LA ENCUESTA", 54, OL)
            text(d, (540, 1328), "y dime en comentarios por qué", 28, (200, 50, 80), "mm", F_UI)
    return c

# ---------------------------------------------------------------- escenas de la Parte 4 (ganó la A: dejarlo así)
LETRA_OK.update({"M": -9, "A": -9, "T": -9, "O": -9})

def estrella(d, cx, cy, r, col=(255, 200, 40)):
    pts = [(cx + r * (1 if i % 2 == 0 else .45) * math.cos(math.radians(-90 + i * 36)), cy + r * (1 if i % 2 == 0 else .45) * math.sin(math.radians(-90 + i * 36))) for i in range(10)]
    d.polygon(pts, fill=col, outline=OL); d.line(pts + [pts[0]], fill=OL, width=5)

def sc_perfecto(T):
    """F01: eligieron dejarlo así. Le detienes la mano (el borrador se cae) y le susurras: está perfecto."""
    s0, e0 = TL["F01"]
    c = pared_expo(T).filter(ImageFilter.GaussianBlur(7))
    td, tp = WT("F01", "detienes"), WT("F01", "perfecto.")
    mateo(c, "feliz" if T >= tp - .1 else "timido", 540, 1260, 1.0, T)
    if T < td + .1: borrador(c, 780, 1520, .9, 20)
    elif T < td + 1.2:   # se le cae de la mano
        k = (T - td - .1) / 1.1; borrador(c, 780 + 60 * k, 1520 + 700 * k * k, .9, 20 + 200 * k)
    d = ImageDraw.Draw(c)
    if T < WT("F01", "Le") - .1:   # resultado de la encuesta, sin números inventados
        k = max(.02, popscale(T, 0, .3)); y = 470
        d.rounded_rectangle((540 - 400 * k, y - 75, 540 + 400 * k, y + 75), 36, fill=WHITE, outline=NAVY, width=6)
        if k > .8:
            d.ellipse((170, y - 50, 270, y + 50), fill=AZ, outline=WHITE, width=5); d.text((220, y + 2), "A", font=font(F_ANTON, 60), fill=WHITE, anchor="mm")
            d.text((300, y - 24), "ELIGIERON:", font=font(F_BAL, 34), fill=(150, 130, 160), anchor="lm")
            d.text((300, y + 22), "Dejarlo así", font=font(F_BAL, 48), fill=NAVY, anchor="lm")
            if T > .4: confeti(c, T, .4, 40)
    if T >= tp:
        corazones(c, T, tp, 540, 900)
        stamp(c, T, tp, "¡ESTÁ PERFECTO!", 540, 520, ROSA, -5, 86)
    return c

def sc_maestra(T):
    """F02-F03: la maestra mira la E y sonríe; le pega una estrella. 'Es normal que la escriban al revés al principio.'"""
    s0 = S("F03"); ts = S("F03") + .4
    c = pared_expo(T)
    xs = 540 + 150
    if T >= ts - .2:
        k = popscale(T, ts - .2, .4); estrella(ImageDraw.Draw(c), xs, 1050, 55 * k)
    z = 1.0 + .7 * ease((T - s0) / 1.5)
    c = seguir(c, 540, 1080, z, f=1.0)
    siluetas(c, T)
    if T >= WT("F03", "normal"): etiqueta(c, T, WT("F03", "normal"), "¡ES NORMAL AL PRINCIPIO!", 540, 470, CREMA, OL, 40)
    if T >= WT("F03", "solito!"): stamp(c, T, WT("F03", "solito!"), "¡ÉL SOLITO!", 540, 1250, VERDE, -5, 90)
    return c

def sc_ya_no(T):
    """F04: la mamá que se reía... ya no se ríe."""
    s0, e0 = TL["F04"]
    c = pared_expo(T); c = seguir(c, 540, 1000, 1.15, f=1.0)
    estrella(ImageDraw.Draw(c), 540 + 150 * 1.15, 1050 + 50 * 1.15, 60)
    siluetas(c, T)
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((60, 1250, 400, 1370), 40, fill=WHITE, outline=OL, width=6)
    d.polygon([(110, 1370), (150, 1370), (100, 1440)], fill=WHITE)
    d.text((230, 1310), "jajaja", font=font(F_BAL, 64), fill=(214, 84, 120), anchor="mm")
    tr = WT("F04", "ríe.")
    if T >= tr - .3:
        k = clamp((T - tr + .3) / .3); d.line((80, 1360, 80 + 300 * k, 1260), fill=ROJO, width=14)
    if T >= tr: stamp(c, T, tr, "YA NO SE RÍE", 600, 520, NAVY, -4, 86)
    return c

def sc_truco(T):
    """F05: el truco de Rex: la E mira hacia adelante, como Rex cuando camina. Mateo la repasa al derecho."""
    s0, e0 = TL["F05"]
    c = bg("bg_mesa", T, s0, 1.2, 1.3, 6, .5, .5)
    c.alpha_composite(Image.new("RGBA", (W, H), NOCHE_AZ + (50,)))
    put(c, "hoja", *HOJA); pinti(c, 920, 640, 150, rot=-8)
    yt, yb = fila(*HOJA, 0); h = yb - yt
    # a la izquierda, su E al revés tachada; a la derecha la E buena en puntitos
    eal = nino_trazos("E", 250, yt, h, erev=True, seed=1)
    dibuja_trazos(c, [p for L in eal for p in L], h * .1, (150, 160, 170))
    d = ImageDraw.Draw(c); te = WT("F05", "E")
    if T >= te:
        k = clamp((T - te) / .3); d.line((220, yt - 10, 220 + 140 * k, yt - 10 + (h + 20) * k), fill=ROJO, width=12)
        d.line((360, yt - 10, 360 - 140 * k, yt - 10 + (h + 20) * k), fill=ROJO, width=12)
    Ebuena = letra_trazos("E", 600, yt, yb)[0]
    puntitos(c, Ebuena, h)
    # Rex camina hacia adelante por la línea de abajo, con su flecha
    y1, b1 = fila(*HOJA, 1); tc = WT("F05", "camina.")
    if T >= WT("F05", "adelante,") - .2:
        u = clamp((T - WT("F05", "adelante,") + .2) / 2.5)
        put(c, "dino", 260 + 480 * u, b1 - 50 + 8 * abs(math.sin(T * 9)), .14)
        d = ImageDraw.Draw(c); ax = 260 + 480 * u + 90
        d.line((ax, b1 - 60, ax + 70, b1 - 60), fill=ROSA, width=10); d.polygon([(ax + 70, b1 - 80), (ax + 100, b1 - 60), (ax + 70, b1 - 40)], fill=ROSA)
    t0, t1 = WT("F05", "Rex", 2) - .2, e0 + .8
    tip, u = escribir(c, [Ebuena], T, t0, t1, h * .13, .55, entra=.5)
    if u is not None and T >= t1:
        k = popscale(T, t1, .3); d = ImageDraw.Draw(c); r = 30 * k
        d.ellipse((720 - r, yt - 70 - r, 720 + r, yt - 70 + r), fill=VERDE, outline=WHITE, width=4)
        if k > .6: d.line([(707, yt - 70), (716, yt - 60), (735, yt - 84)], fill=WHITE, width=6)
    c = seguir(c, tip[0] if tip else 480, tip[1] if tip else (yt + b1) / 2, 1.35, f=.55)
    if T >= WT("F05", "truco:") and T < WT("F05", "adelante,"): etiqueta(c, T, WT("F05", "truco:"), "EL TRUCO DE REX", 540, 1220, CREMA, OL, 40)
    if T >= WT("F05", "adelante,"): etiqueta(c, T, WT("F05", "adelante,"), "LA E MIRA HACIA ADELANTE", 540, 1220, VERDE, WHITE, 38)
    return c

def sc_bien(T):
    """F06: '¡Mami, ya me salió bien!'"""
    s0, e0 = TL["F06"]
    c = bg("bg_cocina", T, s0 - .2, 1.2, 1.28, 6, .5, .6)
    c.alpha_composite(Image.new("RGBA", (W, H), NOCHE_AZ + (50,)))
    mateo(c, "feliz", 420, 1260, 1.05, T, "F06")
    letra_grande(c, "E", 820, 760, 380, T, s0)
    brillos(c, T, s0 + .2, 820, 760, 200)
    return c

def mama_trazos(x, y, sz):
    L = nino_trazos("MAMA", x, y, sz, seed=2)
    xs = [q[0] for p in L[3] for q in p]; ax = (min(xs) + max(xs)) / 2
    L[3] = L[3] + [[(ax - sz * .05, y - sz * .12), (ax + sz * .14, y - sz * .3)]]   # la tilde de MAMÁ
    return L

def sc_mama(T):
    """F07: antes de dormir escribe algo más, para ti: MAMÁ, letra a letra, con su mano."""
    s0, e0 = TL["F07"]
    c = bg("bg_mesa", T, s0, 1.2, 1.3, 6, .5, .5)
    c.alpha_composite(Image.new("RGBA", (W, H), NOCHE_AZ + (60,)))
    put(c, "hoja", *HOJA); pinti(c, 920, 640, 150, rot=-8)
    yt, yb = fila(*HOJA, 0); h = yb - yt
    L = mama_trazos(540 - ancho_nino("MAMA", h) / 2, yt, h)
    t0, t1 = WT("F07", "escribe") - .1, e0 + 1.1
    tip, u = escribir(c, L, T, t0, t1, h * .1, .55, entra=.5)
    c = seguir(c, tip[0] if tip else 540, tip[1] if tip else (yt + yb) / 2, 1.4, f=.6)
    if T >= WT("F07", "ti."): etiqueta(c, T, WT("F07", "ti."), "PARA TI", 540, 1220, ROSA, WHITE, 44)
    return c

def sc_mama2(T):
    """F08: 'Ma... má.' Te enseña la hoja y se te nubla la vista."""
    s0, e0 = TL["F08"]
    c = bg("bg_cocina", T, s0 - .3, 1.15, 1.2, 6, .5, .6)
    c.alpha_composite(Image.new("RGBA", (W, H), (255, 200, 120, 50)))
    mateo(c, "feliz", 540, 1330, .95, T, "F08")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); put(lay, "hoja", 540, 700, .62)
    dibuja_trazos(lay, [p for Lx in mama_trazos(540 - ancho_nino("MAMA", 100) / 2, 600, 100) for p in Lx], 10)
    c.alpha_composite(lay.rotate(-3 + 2 * math.sin(T * 3), center=(540, 700), resample=Image.BICUBIC))
    corazones(c, T, s0 - .3, 540, 900)
    k = ease((T - s0 - .6) / 1.2)
    if k > 0:
        c = Image.blend(c, c.filter(ImageFilter.GaussianBlur(9)), .7 * k)
    return c

def sc_premio(T):
    """F09 (inicio): al día siguiente te pide la tablet de premio."""
    s0, e0 = TL["F09"]
    c = bg("bg_cuarto", T, s0, 1.15, 1.22, 8, .5, .55)
    mateo(c, "feliz", 400, 1270, 1.0, T)
    tt = WT("F09", "tablet")
    if T >= tt - .2:
        k = popscale(T, tt - .2, .4)
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse((560, 620, 1060, 1060), fill=(120, 190, 255, 120))
        c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(50)))
        put(c, "tablet", 810, 840, .32 * k, rot=-8)
    if T >= WT("F09", "premio."): stamp(c, T, WT("F09", "premio."), "¿Y MI PREMIO?", 600, 520, ROSA, -5, 86)
    return c

_FC = {}
def _lado(name):
    if name in _FC: return _FC[name]
    if name == "A":
        A = bg("bg_cuarto", 0, 0, 1.2, 1.2, 1, .5, .6).convert("RGBA")
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse((80, 1500, 580, 1950), fill=(120, 190, 255, 140))
        A.alpha_composite(glow.filter(ImageFilter.GaussianBlur(50)))
        put(A, "mateo_feliz", 280, 1450 + 400 * .7, .7); put(A, "tablet", 330, 1760, .3, rot=-6)
        A.alpha_composite(Image.new("RGBA", (W, H), (30, 40, 110, 80)))
    else:
        A = bg("bg_cocina", 0, 0, 1.2, 1.2, 1, .5, .6).convert("RGBA")
        put(A, "mateo_feliz", 820, 1450 + 400 * .72, .72); put(A, "dino", 950, 1700, .35, rot=6)
        put(A, "crayola", 700, 1720, .3, rot=-20)
        A.alpha_composite(Image.new("RGBA", (W, H), (20, 90, 50, 80)))
    _FC[name] = A
    return A

def sc_final(T):
    s0, e0 = TL["F09"]; ta, tb, tv = WT("F09", "A:"), WT("F09", "B:"), WT("F09", "Vota…")
    hiA = ta <= T < tb; hiB = tb <= T < tv
    A, B = _lado("A"), _lado("B")
    u = ease((T - ta + .4) / .45)
    c = Image.new("RGBA", (W, H), (0, 0, 0, 255)); negro = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    c.alpha_composite(B if not hiA else Image.blend(B, negro, .45), (int(500 * (1 - u)), 0))
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon([(0, 0)] + RAYO + [(0, H)], fill=255)
    c.paste(A if not hiB else Image.blend(A, negro, .45), (int(-700 * (1 - u)), 0), mask)
    d = ImageDraw.Draw(c)
    if u > .9:
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).line(RAYO, fill=(255, 210, 120, 255), width=40, joint="curve")
        c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(c)
        d.line(RAYO, fill=WHITE, width=12, joint="curve"); d.line(RAYO, fill=YEL, width=5, joint="curve")
    k0 = popscale(T, ta - .4, .4)
    text(d, (540, 220), "¿QUÉ HARÍAS TÚ?", 96 * max(k0, .01), YEL, stroke=8)
    for cx, L_, t1, t2, t3, col, t0, h in ((270, "A", "DARLE LA\nTABLET", "+ Se lo ganó", "- Vuelve la pantalla", AZ, ta, hiA),
                                           (790, "B", "PREMIO SIN\nPANTALLAS", "+ Juegan juntos", "- Puede enojarse", VERDE, tb, hiB)):
        k = popscale(T, t0, .35)
        if k > 0: _opcion(d, cx, 420, L_, t1, t2, t3, col, k, 1.08 if h else 1.0)
    if T >= tv - .1:
        k = popscale(T, tv - .1, .4)
        d.rounded_rectangle((540 - 390 * k, 1250, 540 + 390 * k, 1350), 50, fill=WHITE, outline=OL, width=6)
        if k > .5:
            text(d, (540, 1286), "VOTA EN LA ENCUESTA", 54, OL)
            text(d, (540, 1328), "y dime en comentarios por qué", 28, (200, 50, 80), "mm", F_UI)
    return c

# ---------------------------------------------------------------- hojas reales del libro de Pinti (venta discreta)
LIBRO = os.path.join(HERE, "..", "pinti-organico", "assets")
_PG = {}
def pagina_img(n, s):
    k = (n, round(s, 3))
    if k not in _PG:
        f = os.path.join(LIBRO, "portada.jpg" if n == 0 else f"paginas/pagina-{n:02d}.jpg")
        im = Image.open(f).convert("RGBA"); _PG[k] = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    return _PG[k]

def pagina(c, n, px, py, cx, cy, s, sombra=True):
    """Pone la página n del libro (escala s) de modo que su punto (px, py) caiga en (cx, cy). Devuelve el mapeo página->pantalla."""
    im = pagina_img(n, s); x0, y0 = cx - px * s, cy - py * s
    if sombra:
        sh = Image.new("RGBA", (im.width + 60, im.height + 60), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle((30, 30, im.width + 30, im.height + 30), fill=(40, 30, 20, 110))
        c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)), (int(x0 - 18), int(y0 - 14)))
    c.alpha_composite(im, (int(x0), int(y0)))
    return lambda x, y: (x0 + x * s, y0 + y * s)

_PL = {}
def _pl_rmask(size, r):
    m = Image.new("L", (size[0] * 2, size[1] * 2), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] * 2 - 1, size[1] * 2 - 1), r * 2, fill=255)
    return m.resize(size, Image.LANCZOS)

def _pl_grad(size, a, b):
    g = Image.linear_gradient("L").resize(size)
    return Image.composite(Image.new("RGB", size, b), Image.new("RGB", size, a), g)

def _pl_book(h):
    im = pagina_img(0, 1.0).convert("RGBA"); sw, sh = im.size
    d = ImageDraw.Draw(im)   # tapa la insignia '88 páginas' de la portada (el libro actual tiene 109)
    d.ellipse((sw * .045, sh * .815, sw * .225, sh * .93), fill=im.getpixel((int(sw * .035), int(sh * .87))))
    im = im.resize((int(sw * h / sh), h), Image.LANCZOS); w = im.width; d = ImageDraw.Draw(im)
    for i in range(10): d.line((i, 0, i, h), fill=(0, 0, 0, int(70 - i * 7)))
    d.line((12, 0, 12, h), fill=(255, 255, 255, 50), width=2)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); out.paste(im, (0, 0), _pl_rmask((w, h), 8)); return out

def _pl_base():
    """Tarjeta base (sin barra de progreso), con sombra. Se cachea."""
    if "b" in _PL: return _PL["b"]
    ORG, ORG2, NV, NV2 = (244, 124, 42), (255, 160, 70), (22, 36, 66), (34, 54, 96)
    cw, ch, pad = 980, 285, 60
    lay = Image.new("RGBA", (cw + 2 * pad, ch + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 18, pad + cw, pad + ch + 18), 40, fill=(0, 0, 0, 140))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(26)))
    lay.paste(_pl_grad((cw, ch), NV2, NV).convert("RGBA"), (pad, pad), _pl_rmask((cw, ch), 40))
    d = ImageDraw.Draw(lay); d.rounded_rectangle((pad, pad, pad + cw, pad + ch), 40, outline=(120, 140, 185, 255), width=2)
    b = _pl_book(190); bx, by = pad + 44, pad + 26
    bs = Image.new("RGBA", lay.size, (0, 0, 0, 0)); ImageDraw.Draw(bs).rounded_rectangle((bx, by + 12, bx + b.width, by + 202), 8, fill=(0, 0, 0, 150))
    lay.alpha_composite(bs.filter(ImageFilter.GaussianBlur(14))); lay.alpha_composite(b, (bx, by))
    tx = bx + b.width + 36; d = ImageDraw.Draw(lay)
    d.ellipse((tx, pad + 43, tx + 16, pad + 59), fill=(90, 220, 130))
    d.text((tx + 28, pad + 51), "MAMÁ, ESTAS HOJAS SON PARA TI", font=font(F_BAL, 28), fill=ORG2, anchor="lm")
    d.text((tx, pad + 104), "Que tu hijo escriba sus letras", font=font(F_BAL, 44), fill=WHITE, anchor="lm")
    d.text((tx, pad + 150), "Paso a paso · 109 hojas para imprimir", font=font(F_BAL, 30), fill=(180, 195, 225), anchor="lm")
    bw, bh, by2 = 600, 58, pad + 176
    lay.paste(_pl_grad((bw, bh), ORG2, ORG).convert("RGBA"), (tx, by2), _pl_rmask((bw, bh), bh // 2))
    d = ImageDraw.Draw(lay); d.text((tx + 34, by2 + bh // 2 + 1), "Descárgalas · link en mi bio", font=font(F_BAL, 32), fill=WHITE, anchor="lm")
    cx, cy = tx + bw - bh // 2 - 8, by2 + bh // 2
    d.ellipse((cx - bh * .3, cy - bh * .3, cx + bh * .3, cy + bh * .3), fill=(255, 255, 255, 255)); s_ = bh * .11
    d.line((cx - s_, cy - s_ * 1.3, cx + s_, cy, cx - s_, cy + s_ * 1.3), fill=ORG, width=5, joint="curve")
    _PL["b"] = (lay, pad, tx, ch)
    return _PL["b"]

def pill_libro(c, T, t0, dur=3.2, y=380):
    """Tarjeta de producto para madres (azul marino): entra deslizando, se queda con barra de progreso y sale suave."""
    if not (t0 <= T < t0 + dur): return
    kin = ease((T - t0) / .45); kout = 1 - ease((T - t0 - dur + .35) / .35); k = kin * kout
    if k <= .02: return
    lay, pad, tx, ch = _pl_base(); lay = lay.copy(); d = ImageDraw.Draw(lay)
    px, py, pw = tx, pad + ch - 24, pad + 980 - 40 - tx
    d.rounded_rectangle((px, py, px + pw, py + 6), 3, fill=(58, 76, 118)); d.rounded_rectangle((px, py, px + max(6, int(pw * (T - t0) / dur)), py + 6), 3, fill=(255, 160, 70))
    if k < 1: lay.putalpha(lay.split()[3].point(lambda v: int(v * k)))
    c.alpha_composite(lay, (50 - pad, int(y - pad + 70 * (1 - kin) - 30 * (1 - kout))))

def impresora(c, T, t0, n=15):
    """La impresora sacando una hoja real del libro."""
    d = ImageDraw.Draw(c)
    u = clamp((T - t0) / 1.4)
    pg = pagina_img(n, .4)
    yb = 960 - pg.height * u   # la hoja sale por la ranura de arriba
    vis = int(960 - yb)
    if vis > 2: c.alpha_composite(pg.crop((0, 0, pg.width, vis)), (int(540 - pg.width / 2), int(yb)))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((170, 960, 910, 1330), 46, fill=(236, 236, 242), outline=OL, width=8)
    d.rounded_rectangle((250, 940, 830, 1000), 20, fill=(70, 70, 86), outline=OL, width=6)
    d.rounded_rectangle((250, 1160, 830, 1230), 20, fill=(210, 210, 220), outline=OL, width=5)
    d.ellipse((780, 1040, 830, 1090), fill=(90, 210, 120) if int(T * 4) % 2 else (60, 160, 90), outline=OL, width=4)

def pagina_trazos_E(mp):
    """Los 4 trazos de una E punteada de la página 15 (en coordenadas de la página), en el orden del libro."""
    out = []
    for x0, x1, xm in ((255, 290, 285), (329, 364, 359)):
        p = [[(x0, 589), (x0, 660)], [(x0, 589), (x1, 589)], [(x0, 625), (xm, 625)], [(x0, 660), (x1, 660)]]
        out.append([[mp(*q) for q in s] for s in p])
    return out

def sc_truco(T):
    """F05: imprimes la hoja de la E del libro; el truco de Rex: la E mira hacia adelante. Mateo repasa las E punteadas de la página real."""
    s0, e0 = TL["F05"]; tr = WT("F05", "Rex") - .1
    c = bg("bg_mesa", T, s0, 1.2, 1.3, 6, .5, .5)
    c.alpha_composite(Image.new("RGBA", (W, H), NOCHE_AZ + (50,)))
    if T < tr:
        impresora(c, T, s0 - .1)
        return c
    mp = pagina(c, 15, 230, 560, 400, 900, 1.5)
    Es = pagina_trazos_E(mp)
    t0, t1 = WT("F05", "adelante,") - .2, e0 + .45
    tip, u = escribir(c, Es, T, t0, t1, 15, .5, entra=.6)
    # Rex camina hacia adelante por la línea de abajo
    if T >= WT("F05", "adelante,") - .2:
        uu = clamp((T - WT("F05", "adelante,") + .2) / 2.5); bx, by = mp(250 + 260 * uu, 700)
        put(c, "dino", bx, by - 40 + 8 * abs(math.sin(T * 9)), .12)
        d = ImageDraw.Draw(c); ax = bx + 80
        d.line((ax, by - 50, ax + 60, by - 50), fill=ROSA, width=10); d.polygon([(ax + 60, by - 68), (ax + 88, by - 50), (ax + 60, by - 32)], fill=ROSA)
    for i, tf in enumerate(fines(Es, t0, t1)):
        if T >= tf:
            x, y = mp((255, 329)[i] + 18, 560); k = popscale(T, tf, .3); d = ImageDraw.Draw(c); r = 26 * k
            d.ellipse((x - r, y - r, x + r, y + r), fill=VERDE, outline=WHITE, width=4)
            if k > .6: d.line([(x - 11, y), (x - 3, y + 9), (x + 13, y - 12)], fill=WHITE, width=6)
    c = seguir(c, tip[0] if tip else 480, tip[1] if tip else 900, 1.3, f=.5)
    if T < WT("F05", "adelante,"): etiqueta(c, T, tr, "EL TRUCO DE REX", 540, 1220, CREMA, OL, 40)
    else: etiqueta(c, T, WT("F05", "adelante,"), "LA E MIRA HACIA ADELANTE", 540, 1220, VERDE, WHITE, 38)
    pill_libro(c, T, tr + .2, 3.4)
    return c

def sc_mama(T):
    """F07: antes de dormir escribe algo más, para ti: MAMÁ, en la hoja de práctica del libro, con su mano."""
    s0, e0 = TL["F07"]
    c = bg("bg_mesa", T, s0, 1.2, 1.3, 6, .5, .5)
    c.alpha_composite(Image.new("RGBA", (W, H), NOCHE_AZ + (60,)))
    mp = pagina(c, 85, 540, 320, 540, 900, 1.5)
    (xa, yt), (_, yb) = mp(0, 265), mp(0, 374); h = yb - yt
    L = mama_trazos(540 - ancho_nino("MAMA", h) / 2, yt, h)
    t0, t1 = WT("F07", "escribe") - .1, e0 + 1.1
    tip, u = escribir(c, L, T, t0, t1, h * .1, .55, entra=.5)
    c = seguir(c, tip[0] if tip else 540, tip[1] if tip else (yt + yb) / 2, 1.3, f=.55)
    if T >= WT("F07", "ti."): etiqueta(c, T, WT("F07", "ti."), "PARA TI", 540, 1220, ROSA, WHITE, 44)
    pill_libro(c, T, t0 + .3, 3.0)
    return c

def sc_hojas(T):
    """F08B: las hojas que usa Mateo son del libro de Pinti; está en el link de la bio. Hojas reales en abanico."""
    s0, e0 = TL["F08B"]
    c = bg("bg_mesa", T, s0, 1.15, 1.2, 4, .5, .5)
    c.alpha_composite(Image.new("RGBA", (W, H), (255, 220, 170, 40)))
    for i, (n, x, y, rot) in enumerate(((20, 330, 880, -12), (85, 750, 900, 11), (15, 540, 860, -2))):
        k = popscale(T, s0 - .1 + i * .25, .35)
        if k <= 0: continue
        pg = pagina_img(n, .42 * k).rotate(rot, expand=True, resample=Image.BICUBIC)
        sh = Image.new("RGBA", pg.size, (40, 30, 20, 0)); sh.putalpha(pg.getchannel("A").point(lambda v: int(v * .35)))
        c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)), (int(x - pg.width / 2 + 12), int(y - pg.height / 2 + 16)))
        c.alpha_composite(pg, (int(x - pg.width / 2), int(y - pg.height / 2)))
    tl_ = WT("F08B", "link")
    if T >= s0 + .8:   # la portada del libro
        k = popscale(T, s0 + .8, .4); cov = pagina_img(0, .2 * k).rotate(6, expand=True, resample=Image.BICUBIC)
        c.alpha_composite(cov, (int(830 - cov.width / 2), int(1270 - cov.height / 2)))
    if T >= tl_ - .2:
        k = popscale(T, tl_ - .2, .35); d = ImageDraw.Draw(c)
        d.rounded_rectangle((540 - 300 * k, 440 - 55 * k, 540 + 300 * k, 440 + 55 * k), 55, fill=(240, 140, 60), outline=WHITE, width=6)
        if k > .7:
            d.text((540, 442), "LINK EN MI BIO", font=font(F_BAL, 56), fill=WHITE, anchor="mm")
            d.polygon([(540, 330 - 10 * math.sin(T * 6)), (505, 370 - 10 * math.sin(T * 6)), (575, 370 - 10 * math.sin(T * 6))], fill=(240, 140, 60))
    return c

# ---------------------------------------------------------------- escenas de la Parte 5 (ganó la B: premio sin pantallas -> el buzón de Rex)
_letra_base = letra_trazos
def letra_trazos(L, x, yt, yb):
    h = yb - yt
    if L == "L": return [[(x, yt), (x, yb), (x + h * .5, yb)]], h * .5
    if L == "U":
        r = h * .3
        return [[(x, yt), (x, yb - r)] + _arco(x + r, yb - r, r, 180, 0, 16)[1:] + [(x + 2 * r, yt)]], h * .6
    if L == "N": return [[(x, yb), (x, yt), (x + h * .6, yb), (x + h * .6, yt)]], h * .6
    return _letra_base(L, x, yt, yb)

CARTA = ["Gracias, Mateo.", "Ya sé escribir", "mi nombre: REX.", "¿Me enseñas la X?"]
LISTA = ["Leche", "Pan", "Huevos", "Plátanos"]
AZ_TINTA = (40, 60, 150)
ULT = {}
def dur_lectura(): return 1

def luna_img(s):
    k = ("luna", s)
    if k not in _PG:
        im = pagina_img(25, 1.0).crop((290, 1225, 520, 1460)).convert("RGBA")
        a = np.array(im); m = (a[..., :3].min(2) > 235); a[m, 3] = 0
        im = Image.fromarray(a); _PG[k] = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    return _PG[k]

def buzon(c, cx, cy, s, T, rotulo=True):
    """La caja de zapatos convertida en el buzón de Rex."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    w, h, tp = 300 * s, 190 * s, 90 * s
    d.polygon([(cx - w, cy - h + tp), (cx - w + tp, cy - h), (cx + w + tp, cy - h), (cx + w, cy - h + tp)], fill=(206, 150, 96), outline=OL)
    d.polygon([(cx + w, cy - h + tp), (cx + w + tp, cy - h), (cx + w + tp, cy + h - tp), (cx + w, cy + h)], fill=(150, 100, 60), outline=OL)
    d.rectangle((cx - w, cy - h + tp, cx + w, cy + h), fill=(186, 128, 78), outline=OL, width=6)
    d.rounded_rectangle((cx - 130 * s + tp / 2, cy - h + tp * .3, cx + 130 * s + tp / 2, cy - h + tp * .7), 10, fill=(60, 36, 20))
    if rotulo:
        nino_full(lay, "REX", cx - ancho_nino("REX", 110 * s) / 2 - 60 * s, cy - 40 * s, 110 * s, seed=4)
        put(lay, "dino", cx + 210 * s, cy + 60 * s, .2 * s / 1.0)
    c.alpha_composite(lay)

def sobre(c, cx, cy, s, rot=0):
    lay = Image.new("RGBA", (int(320 * s) + 20, int(210 * s) + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    w, h = 320 * s, 210 * s
    d.rectangle((10, 10, 10 + w, 10 + h), fill=(255, 248, 230), outline=OL, width=5)
    d.line([(10, 10), (10 + w / 2, 10 + h * .55), (10 + w, 10)], fill=OL, width=5)
    corazon(d, 10 + w / 2, 10 + h * .55, 22 * s, (255, 92, 130))
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC); c.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def carta(c, T, t0, t1, cx=540, cy=900, s=1.0, rot=-3):
    """La carta de 'Rex' escrita a mano (tu letra)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    w, h = 380 * s, 460 * s
    d.rounded_rectangle((cx - w, cy - h, cx + w, cy + h), 20, fill=(255, 250, 236), outline=(220, 206, 180), width=4)
    for y in range(int(cy - h + 120 * s), int(cy + h - 40), int(84 * s)): d.line((cx - w + 30, y, cx + w - 30, y), fill=(200, 215, 240), width=2)
    manuscrito(lay, CARTA, T, t0, t1, cx - w + 50 * s, cy - h + 140 * s, int(78 * s), AZ_TINTA, int(84 * s))
    if T >= t1 - .2:
        put(lay, "dino", cx + w - 110 * s, cy + h - 120 * s, .2 * s)
        lu = luna_img(.55 * s); lay.alpha_composite(lu, (int(cx - w + 30 * s), int(cy + h - lu.height - 20 * s)))
    c.alpha_composite(lay.rotate(rot, center=(cx, cy), resample=Image.BICUBIC))

def sc_premio_no(T):
    """F01-F02: eligieron premio sin pantallas: le dices que no a la tablet y Mateo se enfada."""
    s0 = S("F01"); tn, tb = WT("F01", "no"), WT("F01", "brazos.")
    c = bg("bg_cuarto", T, s0, 1.15, 1.22, 8, .5, .55)
    enojado = T >= tb - .3
    mateo(c, "enojado" if enojado else "neutral", 400, 1270, 1.0, T, "F02" if T >= S("F02") else None)
    put(c, "tablet", 820, 980, .3, rot=-8)
    d = ImageDraw.Draw(c)
    if T >= tn:   # la tablet queda bloqueada
        k = clamp((T - tn) / .3)
        d.line((720, 880, 720 + 200 * k, 880 + 200 * k), fill=ROJO, width=22); d.line((920, 880, 920 - 200 * k, 880 + 200 * k), fill=ROJO, width=22)
    if T < WT("F01", "Le") - .1:
        k = max(.02, popscale(T, 0, .3)); y = 470
        d.rounded_rectangle((540 - 400 * k, y - 75, 540 + 400 * k, y + 75), 36, fill=WHITE, outline=NAVY, width=6)
        if k > .8:
            d.ellipse((170, y - 50, 270, y + 50), fill=VERDE, outline=WHITE, width=5); d.text((220, y + 2), "B", font=font(F_ANTON, 60), fill=WHITE, anchor="mm")
            d.text((300, y - 24), "ELIGIERON:", font=font(F_BAL, 34), fill=(150, 130, 160), anchor="lm")
            d.text((300, y + 22), "Premio sin pantallas", font=font(F_BAL, 46), fill=NAVY, anchor="lm")
            if T > .4: confeti(c, T, .4, 40)
    if T >= WT("F02", "justo!"): stamp(c, T, WT("F02", "justo!"), "¡NO ES JUSTO!", 560, 500, ROJO, -6, 90)
    return c

def sc_caja(T):
    """F03-F04: sacas una caja de zapatos con un agujero: el buzón de Rex. Si escribe una palabra, Rex contesta."""
    s0 = S("F03"); tc, tbz, tca = WT("F03", "caja"), WT("F04", "buzón"), WT("F04", "carta.")
    c = bg("bg_mesa", T, s0, 1.15, 1.22, 6, .5, .5)
    if T >= tc - .2:
        k = ease((T - tc + .2) / .5); buzon(c, 540, 1000 + 700 * (1 - k), 1.15, T, rotulo=T >= tbz)
    if WT("F03", "agujero") <= T < tbz:
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((380, 700, 760, 860), outline=(255, 230, 120, 230), width=12)
        c.alpha_composite(g.filter(ImageFilter.GaussianBlur(3)))
    if T >= tbz: etiqueta(c, T, tbz, "EL BUZÓN DE REX", 540, 470, CREMA, OL, 44)
    if T >= tca - .3:   # sale una carta del buzón
        k = ease((T - tca + .3) / .6); sobre(c, 600, 760 - 260 * k, .9 * max(k, .05), rot=8 * k)
    return c

def sc_sabe(T):
    """F05: '¿Rex sabe escribir?'"""
    s0, e0 = TL["F05"]
    c = bg("bg_cocina", T, s0 - .2, 1.2, 1.28, 6, .5, .6)
    mateo(c, "neutral", 420, 1260, 1.05, T, "F05")
    put(c, "dino", 830, 1300, .5, rot=6 * math.sin(T * 3))
    d = ImageDraw.Draw(c)
    for i in range(3):
        k = popscale(T, s0 + i * .25, .3)
        if k > 0: text(d, (700 + i * 90, 640 - i * 70), "?", int(110 * k), YEL, stroke=8)
    return c

def trazos_R_p39(mp):
    out = []
    for x0 in (252, 325):
        r = 17
        st = [[(x0, 583), (x0, 649)], [(x0, 583), (x0 + 18, 583)] + _arco(x0 + 18, 600, r, -90, 90, 14)[1:] + [(x0, 617)], [(x0 + 14, 617), (x0 + 36, 649)]]
        out.append([[mp(*q) for q in s] for s in st])
    return out

def trazos_L_p25(mp):
    return [[[mp(x0, 589), mp(x0, 660), mp(x1, 660)]] for x0, x1 in ((249, 284), (320, 356))]

def sc_r(T):
    """F06: imprimes la hoja de la R (La R de regalo) y Mateo repasa las R punteadas con su mano."""
    s0, e0 = TL["F06"]; tr = WT("F06", "R.") + .1
    c = bg("bg_mesa", T, s0, 1.2, 1.3, 6, .5, .5)
    if T < tr:
        impresora(c, T, s0 - .1, 39); return c
    mp = pagina(c, 39, 230, 560, 400, 900, 1.5)
    Rs = trazos_R_p39(mp)
    t0, t1 = WT("F06", "Rex.") + .1, e0 + 1.1   # repasa más despacio: empieza antes y ocupa todo el final de la escena
    tip, u = escribir(c, Rs, T, t0, t1, 15, .5, entra=.8)
    for i, tf in enumerate(fines(Rs, t0, t1)):
        if T >= tf:
            x, y = mp((252, 325)[i] + 18, 560); k = popscale(T, tf, .3); d = ImageDraw.Draw(c); r = 26 * k
            d.ellipse((x - r, y - r, x + r, y + r), fill=VERDE, outline=WHITE, width=4)
            if k > .6: d.line([(x - 11, y), (x - 3, y + 9), (x + 13, y - 12)], fill=WHITE, width=6)
    c = seguir(c, tip[0] if tip else 470, tip[1] if tip else 900, 1.3, f=.5)
    if T < WT("F06", "Rex."): etiqueta(c, T, tr, "LA R DE REGALO", 540, 1220, CREMA, OL, 40)
    else: etiqueta(c, T, WT("F06", "Rex."), "...Y DE REX", 540, 1220, VERDE, WHITE, 42)
    pill_libro(c, T, t0 + .2, 3.3)   # una sola vez por vídeo: mientras repasa las letras
    return c

def sc_noche_carta(T):
    """F07-F08: la hoja entra en el buzón; de noche, mientras duerme, escribes la carta de Rex."""
    s0 = S("F07"); tb, tn = WT("F07", "buzón."), WT("F07", "noche,")
    if T < tn - .1:
        c = bg("bg_mesa", T, s0, 1.15, 1.2, 6, .5, .5)
        buzon(c, 540, 1050, 1.1, T)
        k = clamp((T - s0 - .2) / (tb - s0 + .2))
        pg = pagina_img(39, .3).rotate(4, expand=True)
        y = 380 + 380 * k
        vis = int(max(0, min(pg.height, 790 - y)))
        if vis > 2: c.alpha_composite(pg.crop((0, 0, pg.width, vis)), (int(560 - pg.width / 2), int(y)))
        return c
    c = bg("bg_noche", T, tn, 1.0, 1.06, 10)
    c.alpha_composite(Image.new("RGBA", (W, H), NOCHE_AZ + (90,)))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((140, 420, 940, 1400), fill=(255, 220, 150, 90))
    c.alpha_composite(g.filter(ImageFilter.GaussianBlur(80)))   # luz de lámpara
    t0 = max(WT("F07", "respuesta.") - .3, tn + .5); t1 = E("F08") - .2
    carta(c, T, t0 if T < S("F08") else S("F08"), t1)
    if T < S("F08"): etiqueta(c, T, tn + .2, "MIENTRAS DUERME", 540, 470, CREMA, OL, 40)
    return c

def sc_corre(T):
    """F09-F10: a la mañana siguiente corre al buzón: '¡Rex me contestó!'"""
    s0 = S("F09")
    c = bg("bg_cocina", T, s0, 1.12, 1.2, 8, .5, .6)
    c.alpha_composite(Image.new("RGBA", (W, H), (255, 220, 160, 40)))
    if T < S("F10") - .1:
        buzon(c, 230, 1560, .6, T)
        u = ease((T - s0) / 1.6); mateo(c, "feliz", 1250 - 620 * u, 1270, 1.0, T)
    else:
        mateo(c, "feliz", 420, 1270, 1.05, T, "F10")
        sobre(c, 800, 1180 + 20 * math.sin(T * 8), 1.0, rot=10 * math.sin(T * 5))
        brillos(c, T, S("F10"), 800, 1180, 170)
    etiqueta(c, T, s0 + .2, "A LA MAÑANA SIGUIENTE", 540, 470, CREMA, OL, 38) if T < S("F10") else None
    return c

def sc_l(T):
    """F11: le lees la carta y él solo agarra la crayola: repasa las L punteadas de la hoja 'La L de luna'."""
    s0, e0 = TL["F11"]; tp = WT("F11", "pedir")
    if T < tp - .1:
        c = bg("bg_cocina", T, s0, 1.12, 1.18, 6, .5, .6); c.alpha_composite(Image.new("RGBA", (W, H), (255, 220, 160, 40)))
        carta(c, 99, 0, 1, 540, 960, .95, rot=2)
        return c
    c = bg("bg_mesa", T, tp, 1.2, 1.3, 6, .5, .5)
    mp = pagina(c, 25, 230, 560, 400, 900, 1.5)
    Ls = trazos_L_p25(mp)
    t0, t1 = WT("F11", "agarra") - .3, e0 + .5
    tip, u = escribir(c, Ls, T, t0, t1, 15, .5, entra=1.0)
    c = seguir(c, tip[0] if tip else 470, tip[1] if tip else 900, 1.3, f=.5)
    etiqueta(c, T, WT("F11", "solo"), "ÉL SOLO", 540, 1220, VERDE, WHITE, 46) if T >= WT("F11", "solo") else None
    return c

def sc_luna(T):
    """F12: escribe LUNA en la hoja de práctica: L palo con zapato, U sonrisa, N montaña con rayo, A tienda de Rex."""
    s0, e0 = TL["F12"]
    c = bg("bg_mesa", T, s0, 1.2, 1.3, 6, .5, .5)
    mp = pagina(c, 85, 540, 320, 540, 900, 1.5)
    (_, yt), (_, yb) = mp(0, 265), mp(0, 374); h = yb - yt
    L = nino_trazos("LUNA", 540 - ancho_nino("LUNA", h) / 2, yt, h, seed=5)
    ws = [WT("F12", "L"), WT("F12", "U,"), WT("F12", "N,"), WT("F12", "A,")]
    tip = None
    for i, (ls, t) in enumerate(zip(L, ws)):
        t1 = min(t + 1.0, ws[i + 1] - .35) if i < 3 else e0 + .4
        if T >= t1: dibuja_trazos(c, ls, h * .1)
        elif T >= t - .25: tip, u = escribir(c, [ls], T, t, t1, h * .1, .55, entra=.25)
    if tip is None and ws[0] - .5 <= T < e0 + .4:
        hechas = [i for i, t in enumerate(ws) if T >= (min(t + 1.0, ws[i + 1] - .35) if i < 3 else e0 + .4)]
        nxt_ok = all(not (t - .25 <= T) for t in ws[len(hechas):len(hechas) + 1])
        if hechas and nxt_ok: tip = L[hechas[-1]][-1][-1]; mano_crayola(c, tip, T, .55, True)
    if T >= e0 + .4:
        lu = luna_img(.9); k = popscale(T, e0 + .4, .4)
        if k > 0: c.alpha_composite(lu.resize((max(2, int(lu.width * k)), max(2, int(lu.height * k)))), (760, 520))
    c = seguir(c, tip[0] if tip else 540, tip[1] if tip else (yt + yb) / 2, 1.3, f=.55)
    labs = ["PALO CON ZAPATO", "UNA SONRISA", "MONTAÑA CON RAYO", "LA TIENDA DE REX"]
    for i, t in enumerate(ws):
        nxt = ws[i + 1] if i < 3 else e0 + 1.5
        if t <= T < nxt: etiqueta(c, T, t, f"{'LUNA'[i]} = {labs[i]}", 540, 1220, CREMA, OL, 38)
    return c

def sc_listo(T):
    """F13: '¡Listo! ¡Rex va a estar feliz!'"""
    s0, e0 = TL["F13"]
    c = bg("bg_cocina", T, s0 - .2, 1.2, 1.28, 6, .5, .6)
    mateo(c, "feliz", 420, 1260, 1.05, T, "F13")
    buzon(c, 800, 1450, .62, T)
    sobre(c, 800, 1150 + 120 * ease((T - s0) / .8), .7, rot=6)
    brillos(c, T, s0, 800, 1300, 200)
    return c

def sc_tres(T):
    """F14: tres días, tres cartas, tres palabras nuevas (LUNA, MANO, TOMATE) y ni una sola pantalla."""
    s0, e0 = TL["F14"]; tp = WT("F14", "pantalla.")
    c = bg("bg_mesa", T, s0, 1.15, 1.2, 4, .5, .5)
    for i, (w_, t) in enumerate((("LUNA", WT("F14", "días.")), ("MANO", WT("F14", "cartas.")), ("TOMATE", WT("F14", "palabras")))):
        k = popscale(T, t - .2, .35)
        if k <= 0: continue
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        cx, cy, rot = (270, 820, -8), (810, 820, 7), (540, 1120, -2)
        x, y, r = [(270, 760, -8), (810, 760, 7), (540, 1060, -3)][i]
        d.rounded_rectangle((x - 230, y - 140, x + 230, y + 140), 18, fill=(255, 250, 236), outline=(210, 196, 170), width=4)
        sz = 90 if len(w_) < 6 else 66
        nino_full(lay, w_, x - ancho_nino(w_, sz) / 2, y - sz / 2, sz, seed=i + 2)
        lay = lay.rotate(r, center=(x, y), resample=Image.BICUBIC)
        if k < 1: lay = lay.resize((W, H))
        c.alpha_composite(lay)
    if T >= tp - .2:
        k = popscale(T, tp - .2, .4)
        put(c, "tablet", 540, 1450, .26 * max(k, .01), rot=4)
        d = ImageDraw.Draw(c)
        if k > .8:
            d.line((420, 1340, 660, 1560), fill=ROJO, width=20); d.line((660, 1340, 420, 1560), fill=ROJO, width=20)
    etiqueta(c, T, s0 + .1, "3 DÍAS · 3 CARTAS", 540, 520, CREMA, OL, 42)
    return c

def pizarra(c, T, t0):
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((110, 520, 970, 1180), 20, fill=(46, 84, 66), outline=(150, 100, 60), width=26)
    k = clamp((T - t0) / 1.2)
    M = [(360, 1020), (360, 680), (540, 880), (720, 680), (720, 1020)]
    hechos, tip, _ = _recorrido([M], k)
    for p in hechos: d.line(p, fill=(245, 245, 235), width=22, joint="curve")
    put(c, "dino", 880, 1080, .18)
    return tip

def maestra(c, cx, cy, s, T, lid=None):
    hab = lid is not None and talk(lid, T)
    put(c, "maestra_hab" if hab else "maestra", cx, cy + 200 * s, s)
    if hab: mouth(c, cx, cy - 104 * s, T, True, int(24 * s))

def sc_maestra5(T):
    """F15-F16: el jueves, en la puerta del preescolar, la maestra te cuenta que Mateo le enseñó la M a un compañero."""
    s0 = S("F15")
    c = bg("bg_escuela", T, s0, 1.08, 1.14, 6, .5, .45)
    maestra(c, 540, 1180, .95, T, "F16" if T >= S("F16") else None)
    if T < S("F16") - .1:
        etiqueta(c, T, s0 + .1, "JUEVES · A LA SALIDA", 540, 1330, CREMA, OL, 40)
        return c
    # recuerdo: la M en la pizarra, en un globo junto a la maestra
    tm = WT("F16", "escribir")
    if T >= tm - .3:
        k = popscale(T, tm - .3, .35)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        bx, by, bw, bh = 840, 860, 200 * k, 160 * k
        d.rounded_rectangle((bx - bw, by - bh, bx + bw, by + bh), 22, fill=(46, 84, 66), outline=(150, 100, 60), width=12)
        if k > .9:
            u = clamp((T - tm) / 1.0); M = [(bx - 90, by + 90), (bx - 90, by - 90), (bx, by + 20), (bx + 90, by - 90), (bx + 90, by + 90)]
            hechos, tip, _ = _recorrido([M], u)
            for p in hechos: d.line(p, fill=(245, 245, 235), width=16, joint="curve")
        c.alpha_composite(lay)
    if T >= WT("F16", "dinosaurio."): stamp(c, T, WT("F16", "dinosaurio."), "¡UN DINOSAURIO!", 540, 1330, VERDE, -5, 80)
    return c

def sc_lista(T):
    """F17: esa noche encuentra la lista del súper en la cocina... con la misma letra que la carta de Rex."""
    s0, e0 = TL["F17"]; tl, tm = WT("F17", "lista"), WT("F17", "misma")
    c = bg("bg_cocina", T, s0, 1.12, 1.18, 6, .5, .6)
    c.alpha_composite(Image.new("RGBA", (W, H), NOCHE_AZ + (120,)))
    d = ImageDraw.Draw(c)
    u = ease((T - tm + .2) / .6) if T >= tm - .2 else 0
    # la lista del súper, en tu letra
    lx = 540 - 240 * u
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle((lx - 210, 640, lx + 210, 1160), 14, fill=(255, 252, 240), outline=(210, 196, 170), width=4)
    ld.text((lx, 690), "Súper", font=font(F_HAND, 64), fill=AZ_TINTA, anchor="mm")
    manuscrito(lay, LISTA, 99, 0, 1, lx - 160, 800, 72, AZ_TINTA, 86)
    c.alpha_composite(lay.rotate(3, center=(lx, 900), resample=Image.BICUBIC))
    if u > 0:   # al lado, la carta de Rex: la misma letra
        carta(c, 99, 0, 1, 540 + 300 * u + 300 * (1 - u), 900, .6, rot=-4)
    if T >= tm + .5:
        d = ImageDraw.Draw(c); k = clamp((T - tm - .5) / .5)
        for (x, y) in ((lx - 110, 790), (640, 760)):
            d.arc((x - 70, y - 60, x + 70, y + 60), -90, -90 + 360 * k, fill=ROJO, width=9)
        if T >= tm + 1.0: stamp(c, T, tm + 1.0, "LA MISMA LETRA", 540, 1300, ROJO, -5, 84)
    if T < tm: etiqueta(c, T, tl, "LA LISTA DEL SÚPER", 540, 470, CREMA, OL, 40)
    return c

def sc_eres(T):
    """F18: 'Mami... ¿tú eres Rex?'"""
    s0, e0 = TL["F18"]
    c = bg("bg_cocina", T, s0 - .2, 1.2, 1.26, 6, .5, .6)
    c.alpha_composite(Image.new("RGBA", (W, H), NOCHE_AZ + (120,)))
    mateo(c, "timido", 540, 1260, 1.05, T, "F18")
    carta(c, 99, 0, 1, 830, 1450, .38, rot=12)
    return c

_FC = {}
def _lado(name):
    if name in _FC: return _FC[name]
    if name == "A":
        A = bg("bg_cocina", 0, 0, 1.2, 1.2, 1, .5, .6).convert("RGBA")
        put(A, "mateo_timido", 280, 1480 + 400 * .72, .72); carta(A, 99, 0, 1, 330, 1650, .3, rot=10)
        A.alpha_composite(Image.new("RGBA", (W, H), (30, 40, 110, 80)))
    else:
        A = bg("bg_mesa", 0, 0, 1.2, 1.2, 1, .5, .5).convert("RGBA")
        buzon(A, 820, 1560, .8, 0); brillos(A, 1.0, 0, 820, 1480, 230)
        A.alpha_composite(Image.new("RGBA", (W, H), (20, 90, 50, 70)))
    _FC[name] = A
    return A

def _lado(name):
    if name in _FC: return _FC[name]
    if name == "A":
        A = bg("bg_cuarto", 0, 0, 1.2, 1.2, 1, .5, .5).convert("RGBA")
        put(A, "dino", 300, 1560, .7); put(A, "abuela", 760, 1500 + 200 * .45, .45)
        A.alpha_composite(Image.new("RGBA", (W, H), (30, 40, 110, 80)))
    else:
        A = bg("bg_puerta", 0, 0, 1.0, 1.06, 1).convert("RGBA")
        put(A, "abuela", 780, 1380 + 200 * .8, .8)
        A.alpha_composite(Image.new("RGBA", (W, H), (20, 90, 50, 80)))
    _FC[name] = A
    return A

def sc_final(T):
    s0, e0 = TL["F18"]; ta, tb, tv = WT("F18", "A:"), WT("F18", "B:"), WT("F18", "Vota…")
    hiA = ta <= T < tb; hiB = tb <= T < tv
    A, B = _lado("A"), _lado("B")
    u = ease((T - s0 + .25) / .45)
    c = Image.new("RGBA", (W, H), (0, 0, 0, 255)); negro = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    c.alpha_composite(B if not hiA else Image.blend(B, negro, .45), (int(500 * (1 - u)), 0))
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon([(0, 0)] + RAYO + [(0, H)], fill=255)
    c.paste(A if not hiB else Image.blend(A, negro, .45), (int(-700 * (1 - u)), 0), mask)
    d = ImageDraw.Draw(c)
    if u > .9:
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).line(RAYO, fill=(255, 210, 120, 255), width=40, joint="curve")
        c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(c)
        d.line(RAYO, fill=WHITE, width=12, joint="curve"); d.line(RAYO, fill=YEL, width=5, joint="curve")
    k0 = popscale(T, s0, .4)
    text(d, (540, 220), "¿QUÉ HARÍAS TÚ?", 96 * max(k0, .01), YEL, stroke=8)
    for cx, L_, t1, t2, t3, col, t0, h in ((270, "A", "REX USA LA MANO\nDE LA ABUELA", "+ Sigue la magia", "- Mateo se confunde", AZ, ta, hiA),
                                           (790, "B", "QUE LA ABUELA\nLO CONFIESE", "+ Sin mentiras", "- Se acaba la magia", VERDE, tb, hiB)):
        k = popscale(T, t0, .35)
        if k > 0: _opcion(d, cx, 420, L_, t1, t2, t3, col, k, 1.08 if h else 1.0)
    if T >= tv - .1:
        k = popscale(T, tv - .1, .4)
        d.rounded_rectangle((540 - 390 * k, 1250, 540 + 390 * k, 1350), 50, fill=WHITE, outline=OL, width=6)
        if k > .5:
            text(d, (540, 1286), "VOTA EN LA ENCUESTA", 54, OL)
            text(d, (540, 1328), "y dime en comentarios por qué", 28, (200, 50, 80), "mm", F_UI)
    return c

# ---- registro de trazos con la crayola apoyada (para que el sonido de escribir vaya exacto con la mano)
TRAZOS_ON = {}
def _intervalos(letras, t0, t1):
    todos = [p for L in letras for p in L]; segs = []
    for i, p in enumerate(todos):
        if i: segs.append((math.dist(todos[i - 1][-1], p[0]) * .55 + 1, False))
        segs.append((_largo(p), True))
    tot = sum(w for w, _ in segs); acc = 0; out = []
    for w, dib in segs:
        a = t0 + (t1 - t0) * acc / tot; acc += w; b = t0 + (t1 - t0) * acc / tot
        if dib and b - a > .04: out.append((a, b))
    return out
_escribir_base = escribir
def escribir(c, letras, T, t0, t1, w, sm=.6, mano=True, entra=.5):
    TRAZOS_ON[(round(t0, 3), round(t1, 3))] = _intervalos(letras, t0, t1)
    return _escribir_base(c, letras, T, t0, t1, w, sm, mano, entra)
ESCENAS_ESCRITURA = ("sc_ll",)
def tiza_intervalos(): return []

LETRA_REX = ["Hola, Mateo.", "Soy Rex.", "Gracias por", "enseñarme mi nombre.", "Ahora quiero", "aprender la X."]
LETRA_REX2 = ["Gracias, Mateo.", "Ya sé hacer la X.", "Mañana te cuento", "un secreto."]
VERDE_TINTA = (58, 150, 84)

def carta7(c, T, t0, t1, cx=540, cy=900, s=1.0, rot=-3, lines=None, corazon_k=0, pulso=0):
    """La hoja de la carta nueva: letras torcidas en crayola verde, con un corazoncito en la esquina (la letra de la abuela)."""
    lines = lines or LETRA_REX
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    w, h = 380 * s, 520 * s
    d.rounded_rectangle((cx - w + 10, cy - h + 16, cx + w + 10, cy + h + 16), 20, fill=(0, 0, 0, 70))
    d.rounded_rectangle((cx - w, cy - h, cx + w, cy + h), 20, fill=(255, 250, 236), outline=(220, 206, 180), width=4)
    for y in range(int(cy - h + 110 * s), int(cy + h - 40), int(84 * s)): d.line((cx - w + 30, y, cx + w - 30, y), fill=(200, 215, 240), width=2)
    manuscrito(lay, lines, T, t0, t1, cx - w + 50 * s, cy - h + 150 * s, int(78 * s), VERDE_TINTA, int(84 * s))
    if corazon_k > 0:
        hx, hy = cx + w - 90 * s, cy - h + 80 * s
        corazon(d, hx, hy, 34 * s * corazon_k, (230, 70, 100))
        if pulso:
            r = (70 + 12 * math.sin(T * 7)) * s; d.ellipse((hx - r, hy - r, hx + r, hy + r), outline=YEL, width=8)
    c.alpha_composite(lay.rotate(rot, center=(cx, cy), resample=Image.BICUBIC))

def tinte(c, a=35, col=(255, 214, 160)): c.alpha_composite(Image.new("RGBA", (W, H), col + (a,)))

def tarjeta_ganadora(c, T, letra, texto, col, hasta):
    if T >= hasta: return
    d = ImageDraw.Draw(c); k = max(.02, popscale(T, 0, .3)); y = 470
    d.rounded_rectangle((540 - 400 * k, y - 75, 540 + 400 * k, y + 75), 36, fill=WHITE, outline=NAVY, width=6)
    if k > .8:
        d.ellipse((170, y - 50, 270, y + 50), fill=col, outline=WHITE, width=5); d.text((220, y + 2), letra, font=font(F_ANTON, 60), fill=WHITE, anchor="mm")
        d.text((300, y - 24), "ELIGIERON:", font=font(F_BAL, 34), fill=(150, 130, 160), anchor="lm")
        d.text((300, y + 22), texto, font=font(F_BAL, 40), fill=NAVY, anchor="lm")
        if T > .4: confeti(c, T, .4, 40)

def oscuro(c, T, t0, t1, a1=120):
    """Tinte azul noche (nunca negro) que sube entre t0 y t1."""
    c.alpha_composite(Image.new("RGBA", (W, H), (14, 22, 70, int(a1 * clamp((T - t0) / max(t1 - t0, .01))))))


PERFIL = Image.open(os.path.join(HERE, "layers", "perfil_pinti.jpg")).convert("RGBA")

def _tw(lid, w, n=1, fb=0.0):
    try: return WT(lid, w, n)
    except Exception: return S(lid) + fb

def sc_hola(T):
    """F01-F03: mamá y Mateo saludan a la cámara."""
    c = bg("bg_cuarto", T, 0, 1.15, 1.25, 8, .5, .5)
    mateo(c, "feliz", 540, 1130, 1.1, T, "F02")
    put(c, "dino", 880, 1560, .5, rot=3 * math.sin(T * 2))
    if T > S("F03"): brillos(c, T, S("F03") + .6, 540, 1000, 200)
    return c

def marca(c, T, t0, box, col=(255, 70, 90), w=9, pulso=True):
    """Marcador alrededor de una zona de la captura (coordenadas ya en pantalla)."""
    if T < t0: return
    k = popscale(T, t0, .35); x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; hw, hh = (x1 - x0) / 2 * k, (y1 - y0) / 2 * k
    if pulso: hw += 5 * math.sin((T - t0) * 7); hh += 5 * math.sin((T - t0) * 7)
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((cx - hw - 3, cy - hh - 3, cx + hw + 3, cy + hh + 3), 26, outline=WHITE, width=w + 6)
    d.rounded_rectangle((cx - hw, cy - hh, cx + hw, cy + hh), 24, outline=col, width=w)

def sc_cuenta(T):
    """F04-F07: la captura del perfil nuevo, con el nombre, las partes 7 y 8 y el botón de seguir marcados."""
    s0 = S("F04")
    c = bg("bg_cuarto", T, s0, 1.15, 1.25, 6, .5, .5)
    oscuro(c, T, s0, s0 + .5, 90)
    k = back((T - s0) / .5) if T < s0 + .5 else 1; sc = .66 * max(k, .01)
    cx, cy = 540, 790 + 6 * math.sin(T * 1.4)
    im = PERFIL.resize((int(1080 * sc), int(1444 * sc)), Image.LANCZOS)
    w_, h_ = im.size; fr = Image.new("RGBA", (w_ + 36, h_ + 36), (255, 255, 255, 255)); fr.paste(im, (18, 18))
    sh = Image.new("RGBA", (fr.width + 80, fr.height + 80), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((40, 52, 40 + fr.width, 52 + fr.height), 18, fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    rot = -2.5 + 1.2 * math.sin(T * .9)
    # recuadro marcado con la misma rotación: se dibuja en la captura y se rota con ella
    lay = Image.new("RGBA", fr.size, (0, 0, 0, 0)); fl = ImageDraw.Draw(lay)
    s_ = .66
    def zona(x0, y0, x1, y1): return (18 + x0 * s_ * k, 18 + y0 * s_ * k, 18 + x1 * s_ * k, 18 + y1 * s_ * k)
    fr.alpha_composite(lay)
    c2 = Image.new("RGBA", fr.size, (0, 0, 0, 0)); c2.alpha_composite(fr)
    t_n = S("F05") + .5 * (E("F05") - S("F05")); t_p = _tw("F06", "siete", 1, .3) - .3; t_s = _tw("F07", "seguirnos", 1, .6) - .2
    if T >= s0 + .5:
        marca(c2, T, t_n, zona(30, 140, 360, 190))
        marca(c2, T, t_p, zona(2, 925, 718, 1398))
        marca(c2, T, t_s, zona(30, 380, 460, 508))
    c2 = c2.rotate(rot, expand=True, resample=Image.BICUBIC); shr = sh.rotate(rot, expand=True)
    c.alpha_composite(shr, (int(cx - shr.width / 2), int(cy - shr.height / 2) + 10))
    c.alpha_composite(c2, (int(cx - c2.width / 2), int(cy - c2.height / 2)))
    lid = "F04" if talk("F04", T) else ("F06" if talk("F06", T) else None)
    mateo(c, "feliz", 880, 1290, .5, T, lid)
    etiqueta(c, T, s0 + .3, "NUESTRA CUENTA NUEVA", 540, 235, YEL, OL, 38)
    if T >= t_p: brillos(c, T, t_p, 540, 1160, 200)
    return c

def sc_gusta(T):
    """F08-F10: Mateo pregunta si les gusta su historia; corazones suben."""
    s0 = S("F08")
    c = bg("bg_cuarto", T, s0, 1.15, 1.25, 6, .5, .5)
    mateo(c, "feliz", 540, 1100, 1.15, T, "F08" if talk("F08", T) else ("F10" if talk("F10", T) else None))
    put(c, "dino", 880, 1560, .5, rot=3 * math.sin(T * 2.2))
    corazones(c, T, S("F09") + .3, 540, 1000)
    etiqueta(c, T, S("F09") + .1, "¿TE ESTÁ GUSTANDO LA SERIE?", 540, 235, YEL, OL, 38)
    if T >= S("F10"): brillos(c, T, S("F10"), 540, 900, 240)
    return c

SCENES = [(0, sc_hola), (S("F04") - .15, sc_cuenta), (S("F08") - .15, sc_gusta)]
IMPACTS = []
AVISOS[:] = []
SUAVES = set()

TW = .22
def frame(T):
    idx = max(i for i, (t, f) in enumerate(SCENES) if T >= t)
    t0, fn = SCENES[idx]
    c = fn(T)
    u = (T - t0) / TW
    if idx > 0 and u < 1 and t0 not in SUAVES:   # whip-pan
        e = ease(u); prev = SCENES[idx - 1][1](T)
        k = int(2 + 22 * math.sin(PI_ * u))
        cv = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        cv.alpha_composite(R.hblur(prev, k), (int(-W * e), 0)); cv.alpha_composite(R.hblur(c, k), (int(W * (1 - e)), 0))
        c = cv
    elif idx > 0 and (T - t0) < .45 and t0 in SUAVES:   # fundido cruzado suave
        prev = SCENES[idx - 1][1](T); c = Image.blend(prev, c, ease((T - t0) / .45))
    punch = sum(.03 * math.exp(-(T - ch[0]) * 9) for ch in R.CH if 0 <= T - ch[0] < .5)
    zz = 1 + punch + .02 * ((T - t0) / 6 % 1)
    if zz > 1.002:
        cc = c.resize((int(W * zz), int(H * zz)), Image.BILINEAR)
        ox = (cc.width - W) / 2 + 6 * math.sin(T * .7); oy = (cc.height - H) / 2 + 5 * math.cos(T * .5)
        c = cc.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    if idx > 0 and 0 <= T - t0 < .16 and t0 not in SUAVES:
        c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(100 * (1 - (T - t0) / .16)))))
    amp = sum(14 * math.exp(-(T - ti) * 7) for ti in IMPACTS if 0 <= T - ti < .7)
    if amp > .6:
        cc = c.resize((int(W * 1.04), int(H * 1.04)), Image.BILINEAR)
        ox = (cc.width - W) / 2 + amp * math.sin(T * 95); oy = (cc.height - H) / 2 + amp * math.cos(T * 71)
        c = cc.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    c.alpha_composite(R.VIG)
    c.alpha_composite(R.grains()[int(T * 24) % 4])
    draw_hud(c, T)
    R.draw_caption(c, T)   # en el cierre manda la píldora de votar
    return c.convert("RGB")

def render_scene(i, out):
    t0 = SCENES[i][0]; t1 = SCENES[i + 1][0] if i + 1 < len(SCENES) else TOTAL
    f0, f1 = round(t0 * FPS), round(t1 * FPS)
    tmp = out[:-4] + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-crf", "17", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in range(f0, f1): p.stdin.write(frame(f / FPS).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0: os.replace(tmp, out)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "still":
        for t in sys.argv[2:]: frame(float(t)).save(os.path.join(TMP, f"f_{float(t):06.2f}.jpg"), quality=86)
    elif cmd == "info":
        print(json.dumps({k: [round(a, 2), round(b, 2)] for k, (a, b) in TL.items()}), round(TOTAL, 2))
        print([round(t, 2) for t, f in SCENES])
    elif cmd == "scenes":
        from multiprocessing import Pool
        ids = [int(x) for x in sys.argv[2:]] or list(range(len(SCENES)))
        with Pool(int(os.environ.get("JOBS", "3"))) as pool:
            pool.starmap(render_scene, [(i, os.path.join(TMP, f"s{i:02d}.mp4")) for i in ids])
