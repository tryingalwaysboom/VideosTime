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
R.GAP.update({"F02": .25, "F03": .35, "F04": .35, "F05": 1.7, "F06": .3, "F07": .4, "F08": 1.3, "F09": 1.0, "F10": .45, "F11": .25, "F12": .35, "F13": .8, "F14": .3, "F15": .35, "F16": .3, "F17": .6, "F18": .35})
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
    t_bar = .25; u = ease((T - t_bar) / .8)
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

def sc_puntitos(T):
    """F04: la hoja de puntitos (con Pinti en la esquina): aparecen R, E, X punteadas y Mateo las repasa trazo a trazo con su mano."""
    s0, e0 = TL["F04"]
    c = bg("bg_mesa", T, s0, 1.2, 1.32, 12, .5, .5)
    put(c, "hoja", 540, 900, 1.05)
    pinti(c, 920, 640, 150, rot=-8)
    yt, yb = fila(540, 900, 1.05, 0); h = yb - yt
    letras = palabra_trazos("REX", 540, yt, yb)
    for L, t in zip(letras, (WT("F04", "R,"), WT("F04", "E,"), WT("F04", "X"))):
        if T >= t:
            k = popscale(T, t, .3)
            if k > .95: puntitos(c, L, h)
    ta, t0, t1 = WT("F04", "aprieta"), WT("F04", "sigue"), e0 + 1.3
    tip, u = escribir(c, letras, T, t0, t1, h * .13, .55, entra=t0 - ta)
    for i, tf in enumerate(fines(letras, t0, t1)):   # check verde al terminar cada letra
        if T >= tf:
            xs = [q[0] for p in letras[i] for q in p]
            k = popscale(T, tf, .3); d = ImageDraw.Draw(c); cx = (min(xs) + max(xs)) / 2; r = 26 * k
            d.ellipse((cx - r, yt - 70 - r, cx + r, yt - 70 + r), fill=VERDE, outline=WHITE, width=4)
            if k > .6: d.line([(cx - 11, yt - 70), (cx - 3, yt - 61), (cx + 13, yt - 82)], fill=WHITE, width=6)
    z = 1 + .45 * ease((T - t0 + .4) / .8) * (1 - ease((T - t1 - .3) / .6)) if T >= t0 - .4 else 1
    if tip: c = seguir(c, tip[0], tip[1], z)
    else: c = seguir(c, 540, (yt + yb) / 2, z)
    if T >= WT("F04", "Despacio."): etiqueta(c, T, WT("F04", "Despacio."), "DESPACIO... MUY DESPACIO", 540, 420, CREMA, OL, 38)
    return c

def r_dino(c, cx, cy, sz, T, t0):
    """La R verde gigante con ojito y colita: 'parece un dinosaurio sentado'."""
    k = popscale(T, t0, .45)
    if k <= 0: return
    f = font(F_ESC, sz * k)
    d = ImageDraw.Draw(c)
    d.text((cx, cy), "R", font=f, fill=(63, 174, 74), anchor="mm", stroke_width=int(8 * k), stroke_fill=WHITE)
    if k > .9:
        d.ellipse((cx + sz * .0, cy - sz * .24, cx + sz * .07, cy - sz * .17), fill=OL)
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

def sc_rayitas(T):
    """F07: en la fila de abajo lo escribe él solo, sin puntitos: E con cuatro rayitas, X chueca y una cola."""
    s0, e0 = TL["F07"]
    c = bg("bg_mesa", T, s0, 1.3, 1.4, 8, .5, .5)
    put(c, "hoja", 540, 900, 1.05)
    pinti(c, 920, 640, 150, rot=-8)
    yt, yb = fila(540, 900, 1.05, 0); h = yb - yt
    letras = palabra_trazos("REX", 540, yt, yb)
    for L in letras: puntitos(c, L, h)
    dibuja_trazos(c, [p for L in letras for p in L], h * .13)
    y1, b1 = fila(540, 900, 1.05, 1); h1 = b1 - y1
    R, E, X = rex_nino_trazos(540 - 1.31 * h1, y1, h1)
    tE, tR, tX, tC = WT("F07", "E"), WT("F07", "rayitas."), WT("F07", "X,"), WT("F07", "cola.")
    grupos = [([R], s0 + .1, tE - .1), ([[p] for p in E], tE, tR + .5), ([X[:2]], tX, WT("F07", "chueca.") + .3), ([[X[2]]], tC - .5, e0 + .9)]
    tip = None; activo = False
    for i, (ls, a, b) in enumerate(grupos):
        if T >= b:
            dibuja_trazos(c, [p for L in ls for p in L], h1 * .1)
        elif T >= a:
            tip, u = escribir(c, ls, T, a, b, h1 * .1, .55, entra=.01); activo = True
        if i == 1 and T >= a:   # cuenta las rayitas de la E
            for j, tf in enumerate(fines(ls, a, b)[1:]):
                if T >= tf:
                    yy = E[j + 1][-1][1]; xx = E[j + 1][-1][0] + 40
                    k = popscale(T, tf, .3); d = ImageDraw.Draw(c)
                    d.ellipse((xx - 24 * k, yy - 24 * k, xx + 24 * k, yy + 24 * k), fill=ROSA, outline=WHITE, width=4)
                    if k > .5: text(d, (xx, yy), str(j + 1), 34, WHITE, stroke=0)
    if not activo:   # entre letra y letra la mano espera levantada sobre la última punta
        prev = [g for g in grupos if T >= g[2]]
        if prev and T < e0 + .9:
            p = prev[-1][0][-1][-1][-1]; mano_crayola(c, p, T, .55, True)
            tip = p
        elif T >= e0 + .9:
            k = ease((T - e0 - .9) / .5); p = X[2][-1]
            if k < 1: mano_crayola(c, (p[0] + 500 * k, p[1] + 700 * k), T, .55, True)
    c = seguir(c, tip[0] if tip else 540, tip[1] if tip else (y1 + b1) / 2, 1.42, f=.6)
    if T >= tR + .3 and T < WT("F07", "chueca."): etiqueta(c, T, tR + .3, "¡4 RAYITAS!", 540, 1200, CREMA, OL, 40)
    if WT("F07", "chueca.") <= T < e0 + .4: etiqueta(c, T, WT("F07", "chueca."), "LA X, CHUECA", 540, 1200, CREMA, OL, 40)
    if T >= e0 + .4: stamp(c, T, e0 + .4, "¡CON COLA!", 540, 1210, VERDE, -6, 80)
    return c

def sc_once(T):
    """F08: escribe REX once veces: en hojas, en la caja del cereal... y en la pared (siempre con su mano escribiendo)."""
    s0, e0 = TL["F08"]; tc, tp = WT("F08", "cereal…"), WT("F08", "pared.")
    if T < tc - .1:
        c = bg("bg_mesa", T, s0, 1.2, 1.3, 6, .5, .5)
        orden = [(-220, -260, -12), (200, -200, 8), (-120, 220, -4), (180, 260, 14), (0, 0, -8)]
        dur = (tc - .1 - s0) / 5
        for i, (ox, oy, rot) in enumerate(orden):
            a = s0 + i * dur
            if T < a: continue
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            put(lay, "hoja", 540, 860, .62)
            if T >= a + dur * .9 or i < 4: rex_nino_full(lay, 380, 790, 120)
            lay = lay.rotate(rot, center=(540, 860), resample=Image.BICUBIC)
            c.alpha_composite(lay, (ox, oy))
        # la última hoja: la está escribiendo ahora mismo
        a = s0 + 4 * dur
        if T >= a:
            letras = rex_nino_trazos(380, 790, 120)
            escribir(c, letras, T, a, a + dur * .9, 12, .42, entra=.01)
        d = ImageDraw.Draw(c); n = min(11, int(1 + (T - s0) / .25))
        text(d, (540, 1330), f"x{n}", 120, VERDE, stroke=10)
        return c
    if T < tp - .05:
        c = bg("bg_cocina", T, tc, 1.25, 1.35, 6, .5, .6)
        put(c, "cereal", 540, 960, .95, rot=-4)
        escribir(c, rex_nino_trazos(330, 1060, 150), T, tc + .05, tp - .15, 15, .45, entra=.01)
        etiqueta(c, T, tc, "EN LA CAJA DEL CEREAL", 540, 470, CREMA, OL, 38)
        return c
    c = bg("bg_sala", T, tp, 1.0, 1.08, 5, .5, .5)
    tip, u = escribir(c, rex_nino_trazos(110, 580, 330), T, tp - .05, e0 + .7, 33, 1.05, entra=.01)
    if T >= tp + .3: stamp(c, T, tp + .3, "¿¡EN LA PARED!?", 540, 1250, ROJO, -6, 96)
    return c

def sc_foto(T):
    """F09: la pared con REX en crayola verde; respiras... y le tomas una foto (marco de cámara y flash)."""
    s0, e0 = TL["F09"]; tf = WT("F09", "foto.")
    c = bg("bg_sala", T, s0, 1.08, 1.15, 8, .5, .5)
    rex_nino_full(c, 110, 580, 330)
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
        rex_nino_full(lay, bx0 + 40 * s, yy + 70 * s, 110 * s)
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
    if T >= tm: etiqueta_nombre(c, 760, 600, "_ _ _ _ _", False, popscale(T, tm, .4))
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
        k = ease((T - tn) / .5); put(c, "nota", 540, 760 - 120 * k, .25 + .17 * k, rot=-10 + 8 * k)
    if T >= tn: stamp(c, T, tn, "OTRA NOTA", 540, 1200, NAVY, -5, 90)
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
        d.arc((195, 405, 545, 500), -200, -200 + 360 * k, fill=(220, 40, 40), width=7)
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
    rex_nino_full(c, 760, 860, 70)
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
