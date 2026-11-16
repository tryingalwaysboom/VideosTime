"""Monta la Parte 2 de "Mateo no sabe escribir". Reutiliza el motor del taller (subtítulos palabra a palabra, tiempos de voz,
transiciones) con escenas, barra y final propios.
Uso: python3 render.py still 10 20 | python3 render.py scenes [i...] | python3 render.py info"""
import os, sys, math, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["GUION"] = "guion_mateo2"; os.environ["VOZDIR"] = os.path.join(HERE, "voz2")
sys.path.insert(0, HERE); sys.path.append(os.path.join(HERE, "..", "taller-pov"))
import importlib.util
_spec = importlib.util.spec_from_file_location("R", os.path.join(HERE, "..", "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

R.LAY = os.path.join(HERE, "layers"); R.layer.cache_clear(); R.scaled.cache_clear()
TMP = os.path.join(HERE, "tmp2"); os.makedirs(TMP, exist_ok=True)
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
R.GAP.update({"F02": .3, "F03": .35, "F04": .35, "F05": .3, "F06": .3, "F07": .4, "F08": .35, "F09": .3, "F10": .45, "F11": .25, "F12": .35, "F13": .8, "F14": .3, "F15": .35, "F16": .3, "F17": .6, "F18": .35})
R.TL, R.TOTAL = R.timeline()
R.TL = {k: (a - .1, b - .1) for k, (a, b) in R.TL.items()}; R.TOTAL -= .1   # la voz arranca en el frame 0
R.CH = R.chunks(); TL = R.TL; TOTAL = R.TOTAL
S, E, WT = R.S, R.E, R.WT
R.NOMBRE = {"K": "MATEO", "A": "ABUELA PILAR", "P": "NOTA DE LA MAESTRA"}
R.HIDE_LAST_CAPTION = False

def talk(lid, T): return S(lid) <= T < E(lid)
def u_(T, t0, d): return ease((T - t0) / d)

# ---------------------------------------------------------------- personajes con boca animada
def mateo(c, kind, cx, cy, s, T, lid=None, rot=0):
    hab = lid is not None and talk(lid, T)
    put(c, f"mateo_{kind}_hab" if hab else f"mateo_{kind}", cx, cy + 400 * s, s, rot=rot)   # capa de 1900 px: el cuerpo sigue bajo el encuadre
    if hab: mouth(c, cx, cy + 56 * s, T, True, int(26 * s))
    if kind not in ("llora",) and (T * 1.0) % 3.7 < .12 and not rot:   # parpadeo
        d = ImageDraw.Draw(c)
        for ex in (-75, 75):
            x, y = cx + ex * s, cy - 136 * s
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
    if T >= S("F17") - .3: return
    if T < .3:
        k = ease(T / .3); c.alpha_composite(_BB.crop((0, 0, W, 360)), (0, int(-360 * (1 - k)))); return
    c.alpha_composite(_BB); d = ImageDraw.Draw(c)
    t_d2 = S("F13"); dia = 2 if T < t_d2 else 3
    def pop(t): return 1 + .3 * math.sin(clamp((T - t) / .3) * PI_) if 0 <= T - t < .3 else 1
    y1 = CY0 + 40
    d.rounded_rectangle((CX0 + 22, y1 - 24, CX0 + 120, y1 + 24), 24, fill=ROSA)
    d.text((CX0 + 71, y1 + 2), "EP. 2", font=font(F_BAL, 30), fill=WHITE, anchor="mm")
    d.text((CX0 + 140, y1 + 4), f"DÍA {dia}", font=font(F_BAL, 46 * pop(t_d2)), fill=NAVY, anchor="lm")
    t_m = -9
    fq = font(F_BAL, 40); txt = "META: FIN DE AÑO"
    d.text((CX1 - 30, y1 + 4), txt, font=fq, fill=(214, 70, 110), anchor="rm")
    fx = CX1 - 30 - d.textlength(txt, font=fq) - 30   # banderita de meta
    d.line((fx - 10, y1 - 22, fx - 10, y1 + 22), fill=NAVY, width=5)
    d.polygon([(fx - 8, y1 - 22), (fx + 22, y1 - 13), (fx - 8, y1 - 2)], fill=ROJO, outline=NAVY)
    # las 5 letras de su nombre (vacías: todavía no sabe ninguna)
    y2 = CY0 + 112; t_e = WT("F15", "también")
    for i, L_ in enumerate("MATEO"):
        x = CX0 + 60 + i * 64
        ok = (L_ == "E" and T >= t_e)
        k = popscale(T, t_e, .4) if ok else 1
        r_ = 26 * max(k, .3)
        d.rounded_rectangle((x - r_, y2 - 28 * max(k, .3), x + r_, y2 + 28 * max(k, .3)), 10, fill=(120, 205, 140) if ok else (246, 240, 232), outline=(60, 150, 90) if ok else (200, 186, 205), width=3)
        d.text((x, y2 + 2), L_, font=font(F_ESC, 36 * (max(k, .3) if ok else 1)), fill=WHITE if ok else (214, 204, 218), anchor="mm")
    # ánimo de Mateo (corazones) y tu paciencia (gotas de batería)
    an = interp(T, [(0, .4), (S("F02"), .55), (S("F03"), .65), (S("F05"), .85), (S("F08"), 1.0), (S("F14"), .8), (S("F16"), .85)])
    pa = interp(T, [(0, .2), (S("F03"), .35), (S("F06"), .6), (S("F09"), .45), (S("F11"), .3), (S("F12"), .4), (S("F14"), .25)])
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

# ---------------------------------------------------------------- escenas de la Parte 2
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

def sc_resultado(T):
    """F01: el resultado de la votación de la Parte 1 (A 10 % / B 90 %) con barras que se llenan y confeti."""
    s0, e0 = TL["F01"]
    c = bg("bg_cuarto", T, 0, 1.2, 1.25, 10, .5, .5)
    c.alpha_composite(Image.new("RGBA", (W, H), (30, 20, 60, 120)))
    d = ImageDraw.Draw(c)
    k = popscale(T, 0, .35)
    d.rounded_rectangle((90, 420, 990, 1150), 44, fill=(255, 250, 240), outline=NAVY, width=7)
    d.text((540, 500), "RESULTADO PARTE 1", font=font(F_BAL, 50), fill=NAVY, anchor="mm")
    d.text((540, 556), "¿Qué hago con mi hijo?", font=font(F_BAL, 34), fill=(150, 130, 160), anchor="mm")
    t_bar = .35; u = ease((T - t_bar) / 1.4)
    for i, (L_, txt, pct, col) in enumerate((("A", "Sin tablet hasta que escriba", 10, AZ), ("B", "Escribir el nombre de su dino", 90, VERDE))):
        y = 680 + i * 190
        d.ellipse((130, y - 50, 230, y + 50), fill=col, outline=WHITE, width=6)
        d.text((180, y + 2), L_, font=font(F_ANTON, 64), fill=WHITE, anchor="mm")
        d.text((260, y - 34), txt, font=font(F_BAL, 34), fill=NAVY, anchor="lm")
        d.rounded_rectangle((260, y + 4, 940, y + 52), 24, fill=(236, 228, 236))
        w = 680 * pct / 100 * u
        if w > 30: d.rounded_rectangle((260, y + 4, 260 + w, y + 52), 24, fill=col)
        d.text((950, y - 34), f"{int(round(pct * u))}%", font=font(F_BAL, 44), fill=col, anchor="rm")
    tg = WT("F01", "B:")
    if T >= tg:
        stamp(c, T, tg, "¡GANÓ LA B!", 540, 1060, VERDE, -5, 90)
        confeti(c, T, tg)
    if T >= WT("F01", "final."): etiqueta(c, T, WT("F01", "final."), "QUÉDATE HASTA EL FINAL", 540, 1260, ROSA, OL, 40)
    return c

def sc_rex_nombre(T):
    """F02: '¡Se llama Rex! ¡Grrr!' Mateo feliz con su dinosaurio."""
    s0, e0 = TL["F02"]
    c = bg("bg_cocina", T, s0 - .2, 1.15, 1.22, 6, .5, .6)
    mateo(c, "feliz", 430, 1240, 1.05, T, "F02")
    tg = WT("F02", "Grrr!")
    jump = 30 * abs(math.sin((T - tg) * 9)) * math.exp(-(T - tg) * 3) if T >= tg else 0
    put(c, "dino", 850, 1400 - jump, .62, rot=6 * math.sin(T * 3))
    if T >= WT("F02", "Rex!"): stamp(c, T, WT("F02", "Rex!"), "¡REX!", 760, 520, VERDE, 8, 120)
    if T >= tg: etiqueta(c, T, tg, "¡GRRR!", 840, 1060, CREMA, OL, 44)
    return c

def sc_no_esconde(T):
    """F03: le das la crayola y, por primera vez, no se esconde."""
    s0, e0 = TL["F03"]
    c = bg("bg_cocina", T, s0, 1.05, 1.12, 9, .5, .6)
    tc = WT("F03", "crayola")
    kind = "neutral_crayola" if T >= tc else "neutral"
    mateo(c, kind, 540, 1240, 1.0, T)
    if T < tc: put(c, "crayola", 540 + 300 * (1 - ease((T - s0) / 1.0)), 1500, .55, rot=-20)
    put(c, "dino", 880, 1520, .45, rot=4 * math.sin(T * 2))
    te = WT("F03", "esconde.")
    if T >= te:
        etiqueta(c, T, te, "NO SE ESCONDE", 540, 470, CREMA, OL, 44)
        brillos(c, T, te, 540, 900, 260)
    return c

def trazo_verde(c, word, cx, cy, s, n, T, t0, t1):
    """La crayola verde repasa las letras punteadas de izquierda a derecha entre t0 y t1."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    xs = palabra(lay, word, cx, cy, s, n, T, col=(63, 174, 74))
    if not xs: return xs
    x0, x1 = xs[0][0] - 10, xs[-1][1] + 10
    xr = x0 + (x1 - x0) * clamp((T - t0) / max(.2, t1 - t0))
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rectangle((0, 0, xr, H), fill=255)
    lay.putalpha(Image.fromarray(np.minimum(np.array(lay.split()[3]), np.array(m))))
    c.alpha_composite(lay)
    return xs, xr

def sc_puntitos(T):
    """F04: imprimes hojas con letras de puntitos (con Pinti en la esquina) y él repasa REX con la crayola verde."""
    s0, e0 = TL["F04"]
    c = bg("bg_mesa", T, s0, 1.2, 1.32, 12, .5, .5)
    put(c, "hoja", 540, 900, 1.05)
    pinti(c, 920, 640, 150, rot=-8)   # la hoja impresa del libro de Pinti
    tt = [WT("F04", "R,"), WT("F04", "E,"), WT("F04", "X")]
    palabra(c, "REX", 540, 900, 1.05, 0, T, tt, (150, 160, 200))
    d = ImageDraw.Draw(c)
    # mismas letras punteadas: ahora sí con puntos
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); palabra(lay, "REX", 540, 900, 1.05, 0, T, tt, (150, 160, 200))
    ta = WT("F04", "sigue"); te = e0
    if T >= ta - .3:
        r = trazo_verde(c, "REX", 540, 900, 1.05, 0, T, ta, te)
        if r:
            xs, xr = r; _, yb = fila(540, 900, 1.05, 0)
            yy = yb - 90 + 40 * math.sin((T - ta) * 5)
            put(c, "crayola", xr + 150, yy - 70, .55, rot=35)
    if T >= WT("F04", "Despacio."): etiqueta(c, T, WT("F04", "Despacio."), "DESPACIO... MUY DESPACIO", 540, 430, CREMA, OL, 38)
    return c

def r_dino(c, cx, cy, sz, T, t0):
    """La R verde gigante con ojito y colita: 'parece un dinosaurio sentado'."""
    k = popscale(T, t0, .45)
    if k <= 0: return
    f = font(F_ESC, sz * k)
    d = ImageDraw.Draw(c)
    d.text((cx, cy), "R", font=f, fill=(63, 174, 74), anchor="mm", stroke_width=int(8 * k), stroke_fill=WHITE)
    if k > .9:
        d.ellipse((cx + sz * .02, cy - sz * .33, cx + sz * .1, cy - sz * .25), fill=OL)
        d.polygon([(cx - sz * .28, cy + sz * .3), (cx - sz * .55, cy + sz * .4), (cx - sz * .28, cy + sz * .22)], fill=(63, 174, 74), outline=WHITE)

def sc_risa(T):
    """F05: '¡La erre parece un dinosaurio sentado!' Mateo se ríe."""
    s0, e0 = TL["F05"]
    c = bg("bg_cocina", T, s0 - .2, 1.2, 1.28, 6, .5, .6)
    mateo(c, "feliz", 400, 1260, 1.05, T, "F05")
    r_dino(c, 830, 760, 380, T, WT("F05", "erre"))
    if T >= WT("F05", "sentado!"): etiqueta(c, T, WT("F05", "sentado!"), "¡UN DINO SENTADO!", 780, 1080, CREMA, OL, 38)
    return c

def corazones(c, T, t0, cx, cy):
    if T < t0: return
    d = ImageDraw.Draw(c)
    for i in range(9):
        ph = ((T - t0) * .5 + i / 9) % 1
        x = cx + 380 * math.sin(i * 2.1) + 30 * math.sin(T * 2 + i); y = cy + 300 - 700 * ph
        corazon(d, x, y, 22 + 10 * math.sin(i), (255, 120, 150, int(255 * (1 - ph))))

def sc_te_ries(T):
    """F06: y te ríes. Momento cálido, luz dorada y corazones."""
    s0, e0 = TL["F06"]
    c = bg("bg_cocina", T, s0, 1.28, 1.2, 6, .5, .6)
    gl = Image.new("RGBA", (W, H), (255, 200, 120, 70)); c.alpha_composite(gl)
    mateo(c, "feliz", 540, 1220, 1.15, T)
    corazones(c, T, s0, 540, 900)
    etiqueta(c, T, s0 + .2, "HACE DÍAS QUE NO REÍAN", 540, 470, ROSA, OL, 38)
    return c

def rex_nino(d, x, y, sz, T, t_e, t_x, t_c):
    """REX escrito por Mateo: E con cuatro rayitas, X chueca y una cola en la última letra."""
    g = (63, 174, 74); w = int(sz * .1)
    # R
    d.line((x, y + sz, x, y), fill=g, width=w); d.arc((x - sz * .35, y, x + sz * .4, y + sz * .5), -90, 90, fill=g, width=w)
    d.line((x + sz * .05, y + sz * .5, x + sz * .38, y + sz), fill=g, width=w)
    ex = x + sz * .65
    if T >= t_e:   # E con 4 rayitas
        d.line((ex, y, ex, y + sz), fill=g, width=w)
        for i in range(4): d.line((ex, y + i * sz / 3, ex + sz * (.45 if i % 3 == 0 else .35), y + i * sz / 3 + (6 if i == 2 else 0)), fill=g, width=w)
    xx = ex + sz * .75
    if T >= t_x:   # X chueca
        d.line((xx, y + sz * .05, xx + sz * .5, y + sz * .95), fill=g, width=w)
        d.line((xx + sz * .6, y - sz * .05, xx - sz * .05, y + sz * .8), fill=g, width=w)
    if T >= t_c:   # la cola
        u = clamp((T - t_c) / .5)
        pts = [(xx + sz * .5 + sz * .5 * t, y + sz * .95 - sz * .25 * math.sin(t * 3)) for t in np.linspace(0, u, 12)]
        if len(pts) > 1: d.line(pts, fill=g, width=w, joint="curve")

def sc_rayitas(T):
    """F07: la E con cuatro rayitas, la X chueca... y una cola en la última letra."""
    s0, e0 = TL["F07"]
    c = bg("bg_mesa", T, s0, 1.3, 1.4, 8, .5, .5)
    put(c, "hoja", 540, 900, 1.05)
    d = ImageDraw.Draw(c)
    te, tx, tc = WT("F07", "E"), WT("F07", "X,"), WT("F07", "cola.")
    rex_nino(d, 210, 700, 300, T, te - .1, tx - .1, tc - .2)
    if T >= WT("F07", "rayitas."): etiqueta(c, T, WT("F07", "rayitas."), "4 RAYITAS", 360, 470, CREMA, OL, 36)
    if T >= WT("F07", "chueca."): etiqueta(c, T, WT("F07", "chueca."), "CHUECA", 720, 470, CREMA, OL, 36)
    if T >= tc: stamp(c, T, tc, "¡CON COLA!", 760, 1250, VERDE, -6, 80)
    return c

def sc_once(T):
    """F08: escribe REX once veces: en la hoja, en la caja del cereal... y en la pared."""
    s0, e0 = TL["F08"]; th, tc, tp = WT("F08", "hoja,"), WT("F08", "cereal…"), WT("F08", "pared.")
    if T < tc - .1:
        c = bg("bg_mesa", T, s0, 1.2, 1.3, 6, .5, .5)
        for i in range(5):   # varias hojas con REX
            k = popscale(T, s0 + .3 + i * .35, .3)
            if k <= 0: continue
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            put(lay, "hoja", 540, 860, .62 * k)
            rex_nino(ImageDraw.Draw(lay), 360, 780, 150 * k, 99, 0, 0, 0)
            lay = lay.rotate([-12, 8, -4, 14, -8][i], center=(540, 860), resample=Image.BICUBIC)
            c.alpha_composite(lay, ([-220, 200, -120, 180, 0][i], [-260, -200, 220, 260, 0][i]))
        d = ImageDraw.Draw(c); n = min(11, int(1 + (T - s0) / .22))
        text(d, (540, 1300), f"x{n}", 120, VERDE, stroke=10)
        return c
    if T < tp - .05:
        c = bg("bg_cocina", T, tc, 1.25, 1.35, 6, .5, .6)
        put(c, "cereal", 540, 960, .95, rot=-4)
        rex_nino(ImageDraw.Draw(c), 330, 1110, 150, 99, 0, 0, 0)
        etiqueta(c, T, tc, "EN LA CAJA DEL CEREAL", 540, 470, CREMA, OL, 38)
        return c
    c = bg("bg_sala", T, tp, 1.0, 1.08, 5, .5, .5)
    k = clamp((T - tp) / .6)
    rex_nino(ImageDraw.Draw(c), 160, 560, 360 * (1 + .1 * (1 - k)), 99, 0, 0, 0)
    stamp(c, T, tp + .1, "¿¡EN LA PARED!?", 540, 1180, ROJO, -6, 96)
    return c

def sc_foto(T):
    """F09: la pared con REX en crayola verde; respiras... y le tomas una foto (marco de cámara y flash)."""
    s0, e0 = TL["F09"]; tf = WT("F09", "foto.")
    c = bg("bg_sala", T, s0, 1.08, 1.15, 8, .5, .5)
    rex_nino(ImageDraw.Draw(c), 160, 560, 380, 99, 0, 0, 0)
    mateo(c, "timido", 820, 1300, .85, T)
    put(c, "crayola", 650, 1500, .45, rot=-30)
    tr = WT("F09", "hondo…")
    if T >= tr - .2:   # interfaz de cámara del celular
        d = ImageDraw.Draw(c); a = int(255 * clamp((T - tr + .2) / .3))
        for (x, y, dx, dy) in ((90, 360, 1, 1), (990, 360, -1, 1), (90, 1580, 1, -1), (990, 1580, -1, -1)):
            d.line((x, y, x + 90 * dx, y), fill=(255, 255, 255, a), width=8); d.line((x, y, x, y + 90 * dy), fill=(255, 255, 255, a), width=8)
        d.ellipse((480, 1640, 600, 1760), outline=(255, 255, 255, a), width=10); d.ellipse((496, 1656, 584, 1744), fill=(255, 255, 255, a))
    if 0 <= T - tf < .35:
        c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - (T - tf) / .35)))))
    return c

def sc_grupo(T):
    """F10: mandas la foto al grupo de la familia (tus manos con el celular) y la abuela contesta."""
    s0, e0 = TL["F10"]; ta = WT("F10", "abuela")
    c = bg("bg_noche", T, s0, 1.0, 1.06, 12)
    def cont(d, lay, x, y, w, h, s):
        d.rectangle((x, y, x + w, y + 110 * s), fill=(80, 160, 110))
        d.text((x + 40 * s, y + 72 * s), "Familia ♥", font=font(F_UI, int(32 * s)), fill=WHITE, anchor="lm")
        yy = y + 150 * s
        # tu foto de la pared
        bx0, bx1 = x + w * .3, x + w - 26 * s
        d.rounded_rectangle((bx0, yy, bx1, yy + 330 * s), 22 * s, fill=(220, 248, 200))
        d.rounded_rectangle((bx0 + 14 * s, yy + 14 * s, bx1 - 14 * s, yy + 270 * s), 14 * s, fill=(247, 227, 196))
        rex_nino(d, bx0 + 40 * s, yy + 70 * s, 110 * s, 99, 0, 0, 0)
        d.text((bx1 - 20 * s, yy + 300 * s), "21:47 ✓✓".replace("✓✓", "vv"), font=font(F_UI, int(20 * s)), fill=(120, 140, 120), anchor="rm")
        yy += 360 * s
        if T >= ta:
            k = ease((T - ta) / .3)
            d.rounded_rectangle((x + 26 * s, yy + 30 * (1 - k), x + w * .78, yy + 150 * s), 22 * s, fill=WHITE)
            d.text((x + 50 * s, yy + 40 * s), "Abuela Pilar", font=font(F_UI, int(24 * s)), fill=(130, 70, 170), anchor="lm")
            # nota de voz
            d.ellipse((x + 50 * s, yy + 70 * s, x + 110 * s, yy + 130 * s), fill=(130, 70, 170))
            d.polygon([(x + 72 * s, yy + 84 * s), (x + 96 * s, yy + 100 * s), (x + 72 * s, yy + 116 * s)], fill=WHITE)
            for i in range(18):
                hh = (10 + 22 * abs(math.sin(i * 1.7 + T * 4))) * s
                xx = x + 130 * s + i * 14 * s
                d.line((xx, yy + 100 * s - hh / 2, xx, yy + 100 * s + hh / 2), fill=(150, 120, 180), width=max(2, int(6 * s)))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    put(lay, "manos_atras", 540, 960, 1.0); celular(lay, 540, 980, 1.25, T, cont); put(lay, "manos_delante", 540, 960, 1.0)
    k = ease((T - s0 + .1) / .5); c.alpha_composite(lay, (0, int(500 * (1 - k))))
    return c

def sc_abuela2(T):
    """F11: la nota de voz de la abuela: '¿Y el nombre de él para cuándo?'"""
    s0, e0 = TL["F11"]
    c = bg("bg_puerta", T, s0 - .2, 1.15, 1.22, 8, .5, .5)
    c.alpha_composite(Image.new("RGBA", (W, H), (20, 20, 60, 90)))
    abuela(c, 540, 1260, 1.1, T, "F11")
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((310, 380, 770, 450), 35, fill=(130, 70, 170)); d.text((540, 416), "NOTA DE VOZ · ABUELA", font=font(F_BAL, 30), fill=WHITE, anchor="mm")
    if T >= WT("F11", "cuándo?"): stamp(c, T, WT("F11", "cuándo?"), "¿Y SU NOMBRE?", 540, 560, (130, 70, 170), -6, 90)
    return c

def etiqueta_nombre(c, cx, cy, txt, ok, k):
    d = ImageDraw.Draw(c); w = 230 * k
    d.rounded_rectangle((cx - w, cy - 60 * k, cx + w, cy + 60 * k), 24, fill=WHITE, outline=NAVY, width=6)
    d.text((cx, cy - 4), txt, font=font(F_ESC, max(10, int(76 * k))), fill=NAVY if ok else (200, 190, 205), anchor="mm")
    r = 40 * k
    d.ellipse((cx + w - r, cy - 60 * k - r, cx + w + r, cy - 60 * k + r), fill=VERDE if ok else ROJO, outline=WHITE, width=5)
    text(d, (cx + w, cy - 60 * k + 2), "✓" if False else ("SI" if ok else "?"), 40 * k, WHITE)

def sc_razon(T):
    """F12: Rex ya tiene nombre (etiqueta REX con check). Mateo, todavía no (etiqueta vacía)."""
    s0, e0 = TL["F12"]; tr, tm = WT("F12", "Rex"), WT("F12", "Mateo,")
    c = bg("bg_cuarto", T, s0, 1.2, 1.28, 8, .5, .5)
    c.alpha_composite(Image.new("RGBA", (W, H), (30, 20, 60, 70)))
    put(c, "dino", 290, 1050, .6)
    mateo(c, "triste", 780, 1250, .85, T)
    if T >= tr: etiqueta_nombre(c, 290, 700, "REX", True, popscale(T, tr, .4))
    if T >= tm: etiqueta_nombre(c, 780, 600, "_ _ _ _ _", False, popscale(T, tm, .4))
    return c

def sc_dia3(T):
    """F13: DÍA 3 y otra nota de la maestra en la mochila."""
    s0, e0 = TL["F13"]
    if T < s0 + .9:
        c = bg("bg_cocina", T, s0 - .8, 1.3, 1.2, 2, .2, .3)
        c.alpha_composite(Image.new("RGBA", (W, H), (255, 200, 120, 90)))
        d = ImageDraw.Draw(c); k = popscale(T, s0 - .6, .4)
        text(d, (540, 900), "DÍA 3", 230 * max(k, .01), WHITE, stroke=14, sfill=(214, 84, 120))
        return c
    c = bg("bg_mesa", T, s0, 1.25, 1.15, 5, .5, .5)
    put(c, "mochila", 540, 930, 1.05, rot=-4)
    tn = WT("F13", "nota")
    if T >= tn:
        k = ease((T - tn) / .5); put(c, "nota", 540, 820 - 120 * k, .3 + .45 * k, rot=-10 + 8 * k)
    if T >= tn: stamp(c, T, tn, "OTRA NOTA", 540, 1350, ROJO, -5, 90)
    return c

def sc_nota2(T):
    """F14: la nota: el viernes, exposición, cada niño escribe su nombre delante de los papás."""
    s0, e0 = TL["F14"]
    c = bg("bg_mesa", T, s0 - .3, 1.15, 1.25, 10, .5, .45)
    put(c, "nota", 540, 830, 1.0, rot=-2 + .6 * math.sin(T * .8))
    L = ["Mamá de Mateo:", "este VIERNES cada niño", "escribirá su NOMBRE", "en su dibujo para la", "EXPOSICIÓN.", "Delante de todos", "los papás."]
    manuscrito(c, L, T, s0 + .1, e0 - .3, 210, 420, 60, (196, 36, 36), 72, rot=2)
    if T >= WT("F14", "viernes"):
        d = ImageDraw.Draw(c); k = clamp((T - WT("F14", "viernes")) / .5)
        d.arc((420, 470, 700, 560), -200, -200 + 360 * k, fill=(220, 40, 40), width=7)
    if T >= WT("F14", "papás."): stamp(c, T, WT("F14", "papás."), "¡DELANTE DE TODOS!", 600, 1130, ROJO, -8, 70)
    manuscrito(c, ["Maestra Marta"], T, e0 - .6, e0, 610, 1290, 52, (40, 40, 120))
    return c

def sc_viernes(T):
    """F15: calendario con el VIERNES marcado; solo sabe R, E, X... y la E también está en su nombre."""
    s0, e0 = TL["F15"]; tr = WT("F15", "R,"); te = WT("F15", "también")
    c = bg("bg_cocina", T, s0, 1.1, 1.18, 9, .5, .5)
    c.alpha_composite(Image.new("RGBA", (W, H), (30, 20, 60, 90)))
    d = ImageDraw.Draw(c)
    if T < tr - .2:   # calendario
        d.rounded_rectangle((170, 480, 910, 1180), 30, fill=WHITE, outline=NAVY, width=7)
        d.rectangle((174, 484, 906, 600), fill=ROJO)
        d.text((540, 542), "ESTA SEMANA", font=font(F_BAL, 50), fill=WHITE, anchor="mm")
        dias = ["MIÉ", "JUE", "VIE"]
        for i, dd in enumerate(dias):
            x = 300 + i * 240
            d.text((x, 700), dd, font=font(F_BAL, 50), fill=NAVY, anchor="mm")
            d.text((x, 860), str(13 + i), font=font(F_BAL, 120), fill=NAVY, anchor="mm")
        if T >= WT("F15", "viernes."):
            k = clamp((T - WT("F15", "viernes.")) / .5)
            d.arc((640, 740, 900, 1000), -90, -90 + 360 * k, fill=ROJO, width=12)
        if T >= WT("F15", "Faltan"): stamp(c, T, WT("F15", "Faltan"), "FALTAN 3 DÍAS", 540, 1080, ROJO, -4, 76)
        return c
    # las letras que sabe: R E X, y la E se ilumina como la de su nombre
    for i, L_ in enumerate("REX"):
        t = tr + i * .35
        k = popscale(T, t, .35)
        if k > 0:
            x = 300 + i * 240
            d.rounded_rectangle((x - 100 * k, 640 - 120 * k, x + 100 * k, 640 + 120 * k), 24, fill=(120, 205, 140) if (L_ == "E" and T >= te) else WHITE, outline=NAVY, width=6)
            d.text((x, 640), L_, font=font(F_ESC, max(10, int(170 * k))), fill=(63, 174, 74) if not (L_ == "E" and T >= te) else WHITE, anchor="mm")
    if T >= te:
        k = popscale(T, te, .4)
        palabra_simple = "MATEO"
        for i, L_ in enumerate(palabra_simple):
            x = 220 + i * 160; ok = L_ == "E"
            d.rounded_rectangle((x - 66, 960, x + 66, 1120), 20, fill=(120, 205, 140) if ok else (246, 240, 232), outline=NAVY, width=5)
            d.text((x, 1040), L_, font=font(F_ESC, 100), fill=WHITE if ok else (200, 190, 205), anchor="mm")
        brillos(c, T, te, 540, 1040, 140)
        etiqueta(c, T, te + .2, "¡LA PRIMERA LETRA DE SU NOMBRE!", 540, 1260, VERDE, WHITE, 36)
    return c

def sc_travieso(T):
    """F16: '¿Y si pongo REX en mi dibujo? ¡Nadie se va a dar cuenta!'"""
    s0, e0 = TL["F16"]
    c = bg("bg_cocina", T, s0 - .2, 1.2, 1.28, 6, .5, .6)
    mateo(c, "travieso", 400, 1280, 1.05, T, "F16")
    put(c, "dibujo", 800, 760, .62, rot=6 + 2 * math.sin(T * 2))
    rex_nino(ImageDraw.Draw(c), 760, 860, 70, 99, 0, 0, 0)
    if T >= WT("F16", "cuenta!"): stamp(c, T, WT("F16", "cuenta!"), "¿NADIE?", 780, 1100, ROSA, -6, 90)
    return c

# ---------------------------------------------------------------- final A/B (pantalla partida con rayo)
RAYO = [(600, 0), (560, 520), (612, 560), (522, 1100), (578, 1132), (480, H)]
_FC = {}
def _lado(name):
    if name in _FC: return _FC[name]
    if name == "A":
        A = bg("bg_cuarto", 0, 0, 1.2, 1.2, 1, .5, .6).convert("RGBA")
        put(A, "dino", 260, 1080, .5); put(A, "hoja", 300, 1500, .42, rot=-6)
        A.alpha_composite(Image.new("RGBA", (W, H), (20, 90, 50, 90)))
    else:
        A = bg("bg_mesa", 0, 0, 1.2, 1.2, 1, .5, .5).convert("RGBA")
        put(A, "nota", 800, 1100, .45, rot=8); put(A, "mateo_triste", 820, 2140, .75)
        A.alpha_composite(Image.new("RGBA", (W, H), (40, 30, 90, 110)))
    _FC[name] = A
    return A

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

def sc_final(T):
    s0, e0 = TL["F17"]; ta, tb = WT("F17", "A:"), WT("F17", "B:")
    hiA = ta <= T < tb; hiB = tb <= T < e0
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
    for cx, L_, t1, t2, t3, col, t0, h in ((270, "A", "QUE EL REX\nLE ENSEÑE\nJUGANDO", "+ Lo hace feliz", "- Quizá no llega", AZ, ta, hiA),
                                           (790, "B", "HABLAR CON\nLA MAESTRA", "+ Gana tiempo", "- Todos lo notarán", VERDE, tb, hiB)):
        k = popscale(T, t0, .35)
        if k > 0: _opcion(d, cx, 420, L_, t1, t2, t3, col, k, 1.08 if h else 1.0)
    if T >= S("F18") - .1:
        k = popscale(T, S("F18") - .1, .4)
        d.rounded_rectangle((540 - 390 * k, 1250, 540 + 390 * k, 1350), 50, fill=WHITE, outline=OL, width=6)
        if k > .5:
            text(d, (540, 1286), "VOTA EN LA ENCUESTA", 54, OL)
            text(d, (540, 1328), "y dime en comentarios por qué", 28, (200, 50, 80), "mm", F_UI)
    return c

# ---------------------------------------------------------------- orden y transiciones
SCENES = [
    (0, sc_resultado), (S("F02") - .15, sc_rex_nombre), (S("F03") - .15, sc_no_esconde), (S("F04") - .15, sc_puntitos),
    (S("F05") - .15, sc_risa), (S("F06") - .1, sc_te_ries), (S("F07") - .2, sc_rayitas), (S("F08") - .15, sc_once),
    (S("F09") - .1, sc_foto), (S("F10") - .25, sc_grupo), (S("F11") - .15, sc_abuela2), (S("F12") - .2, sc_razon),
    (S("F13") - .8, sc_dia3), (S("F14") - .2, sc_nota2), (S("F15") - .2, sc_viernes), (S("F16") - .15, sc_travieso),
    (S("F17") - .3, sc_final),
]
IMPACTS = [WT("F01", "B:"), WT("F02", "Grrr!"), WT("F08", "pared."), WT("F09", "foto."), WT("F12", "no."), WT("F14", "papás."), WT("F15", "viernes."), S("F17")]
AVISOS[:] = [S("F05") - .1, S("F12") + .3]
SUAVES = {S("F06") - .1, S("F12") - .2}

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
    if T < S("F18") - .1: R.draw_caption(c, T)   # en el cierre manda la píldora de votar
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
