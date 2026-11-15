"""Monta la Parte 1 de "Los 30 días de Mateo". Reutiliza el motor del taller (subtítulos palabra a palabra, tiempos de voz,
transiciones) con escenas, barra y final propios.
Uso: python3 render.py still 10 20 | python3 render.py scenes [i...] | python3 render.py info"""
import os, sys, math, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["GUION"] = "guion_mateo"; os.environ["VOZDIR"] = os.path.join(HERE, "voz")
sys.path.insert(0, HERE); sys.path.append(os.path.join(HERE, "..", "taller-pov"))
import importlib.util
_spec = importlib.util.spec_from_file_location("R", os.path.join(HERE, "..", "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

R.LAY = os.path.join(HERE, "layers"); R.layer.cache_clear(); R.scaled.cache_clear()
TMP = os.path.join(HERE, "tmp"); os.makedirs(TMP, exist_ok=True)
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
R.GAP.update({"F02": .35, "F03": .3, "F04": .4, "F05": .4, "F06": .2, "F07": .25, "F08": .15, "F09": .3, "F10": .45,
              "F11": .25, "F12": .4, "F13": .9, "F14": .2, "F15": .25, "F16": .6, "F17": .7, "F18": .3, "F19": .6, "F20": .35})
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
    put(c, f"mateo_{kind}_hab" if hab else f"mateo_{kind}", cx, cy + 200 * s, s, rot=rot)   # capa de 1500 px: el cuerpo sigue bajo el encuadre
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
    d.text((CX0 + 40, CY0 + 150), "SU NOMBRE", font=font(F_BAL, 17), fill=(150, 130, 160), anchor="lm")
    d.text((CX0 + 552, CY0 + 150), "ÁNIMO DE MATEO", font=font(F_BAL, 17), fill=(150, 130, 160), anchor="mm")
    d.text((CX0 + 830, CY0 + 150), "TU PACIENCIA", font=font(F_BAL, 17), fill=(150, 130, 160), anchor="mm")
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
    if T >= S("F19") - .3: return
    if T < .3:
        k = ease(T / .3); c.alpha_composite(_BB.crop((0, 0, W, 360)), (0, int(-360 * (1 - k)))); return
    c.alpha_composite(_BB); d = ImageDraw.Draw(c)
    t_d2 = S("F13"); dia = 1 if T < t_d2 else 2
    def pop(t): return 1 + .3 * math.sin(clamp((T - t) / .3) * PI_) if 0 <= T - t < .3 else 1
    y1 = CY0 + 40
    d.rounded_rectangle((CX0 + 22, y1 - 24, CX0 + 120, y1 + 24), 24, fill=ROSA)
    d.text((CX0 + 71, y1 + 2), "EP. 1", font=font(F_BAL, 30), fill=WHITE, anchor="mm")
    d.text((CX0 + 140, y1 + 4), f"DÍA {dia}", font=font(F_BAL, 46 * pop(t_d2)), fill=NAVY, anchor="lm")
    t_30 = WT("F02", "30")
    falt = "¿?" if T < t_30 else ("30" if T < t_d2 else "29")
    # calendario
    cx_ = CX1 - 300
    d.rounded_rectangle((cx_ - 22, y1 - 22, cx_ + 22, y1 + 22), 8, fill=WHITE, outline=NAVY, width=3)
    d.rectangle((cx_ - 20, y1 - 20, cx_ + 20, y1 - 8), fill=ROJO)
    d.text((CX1 - 270, y1 + 4), "FALTAN", font=font(F_BAL, 26), fill=(150, 130, 160), anchor="lm")
    d.text((CX1 - 30, y1 + 4), f"{falt} DÍAS", font=font(F_BAL, 44 * pop(t_30 if T < t_d2 else t_d2)), fill=(214, 70, 110), anchor="rm")
    # las 5 letras de su nombre (vacías: todavía no sabe ninguna)
    y2 = CY0 + 112; t_l = WT("F09", "sola")
    for i, L_ in enumerate("MATEO"):
        x = CX0 + 60 + i * 64
        sh = 5 * math.sin((T - t_l) * 40) * math.exp(-(T - t_l) * 3) if T >= t_l and i == 0 else 0
        d.rounded_rectangle((x - 26 + sh, y2 - 28, x + 26 + sh, y2 + 28), 10, fill=(246, 240, 232), outline=(200, 186, 205), width=3)
        d.text((x + sh, y2 + 2), L_, font=font(F_ESC, 36), fill=(214, 204, 218), anchor="mm")
    # ánimo de Mateo (corazones) y tu paciencia (gotas de batería)
    an = interp(T, [(0, .7), (S("F06"), .5), (S("F08"), .3), (S("F14"), .15), (S("F15") + .3, .05), (S("F17"), .2), (S("F18"), .4)])
    pa = interp(T, [(0, .85), (S("F06"), .65), (S("F08"), .5), (S("F11"), .35), (S("F13"), .6), (S("F14"), .25), (S("F15"), .05), (S("F17"), .2)])
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

def charco(c, cx, cy, T, t0):
    if T < t0: return
    u = ease((T - t0) / 1.0)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k, (dx, dy, r) in enumerate(((0, 0, 260), (-160, 90, 150), (170, 70, 170), (40, 190, 140), (-60, -120, 120))):
        rr = r * u * (1 + .04 * math.sin(T * 3 + k))
        d.ellipse((cx + dx * u - rr, cy + dy * u - rr * .7, cx + dx * u + rr, cy + dy * u + rr * .7), fill=(252, 250, 244, 245))
    c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(2)))
    d = ImageDraw.Draw(c)
    for k in range(4):
        x = cx - 120 + k * 80; y = cy - 40 + 30 * math.sin(k)
        d.ellipse((x - 18, y - 8, x + 18, y + 8), fill=(255, 255, 255))


# ---------------------------------------------------------------- letras sobre la pauta
HOJA_FILAS = ((110, 220, 330), (400, 510, 620))   # (línea de arriba, punteada, base) en coordenadas de la hoja
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
    total = sum(adv) + gap * (len(word) - 1); x = cx - total / 2
    tiempos = tiempos or [-1] * len(word)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for L, a, t in zip(word, adv, tiempos):
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

# ---------------------------------------------------------------- escenas
def sc_mochila(T):
    """F01: la mochila cae en la mesa, se abre y asoma la nota en rojo. Gancho: tú decides."""
    c = bg("bg_mesa", T, 0, 1.25, 1.0, 3.0)
    u = ease(T / .35); b = 26 * abs(math.sin((T - .35) * 10)) * math.exp(-(T - .35) * 5) if T > .35 else 0
    put(c, "mochila", 540, 930 - 900 * (1 - u) - b, 1.12, rot=-4)
    tn = WT("F01", "nota")
    if T >= tn:   # la nota sale volando hacia cámara
        k = ease((T - tn) / .5)
        put(c, "nota", 540, 820 - 120 * k, .3 + .45 * k, rot=-10 + 8 * k)
        if k > .6: manuscrito(c, ["¡URGENTE!"], T, tn + .3, tn + .9, 400, 700, 80, ROJO)
    if T >= WT("F01", "rojo."): stamp(c, T, WT("F01", "rojo."), "EN ROJO", 820, 520, ROJO, 10, 90)
    if T >= WT("F01", "final,"): etiqueta(c, T, WT("F01", "final,"), "QUÉDATE HASTA EL FINAL", 540, 1090, ROSA, OL, 42)
    if T >= WT("F01", "decides"): stamp(c, T, WT("F01", "decides"), "TÚ DECIDES", 540, 1260, AZ, -5, 84)
    return c

def sc_nota(T):
    """F02: la nota de la maestra, escrita en rojo mientras habla."""
    s0, e0 = TL["F02"]
    c = bg("bg_mesa", T, s0 - .3, 1.15, 1.25, 10, .5, .45)
    put(c, "nota", 540, 830, 1.0, rot=-2 + .6 * math.sin(T * .8))
    L = ["Mamá de Mateo:", "es el ÚNICO del salón", "que todavía NO escribe", "su nombre. En 30 días", "empieza el año escolar.", "Si no lo logra...", "tendrá que REPETIR."]
    manuscrito(c, L, T, s0 + .1, e0 - .3, 210, 420, 60, (196, 36, 36), 72, rot=2)
    d = ImageDraw.Draw(c)
    if T >= WT("F02", "único"):   # círculo rojo garabateado alrededor de "ÚNICO"
        k = clamp((T - WT("F02", "único")) / .5)
        d.arc((330, 420, 640, 520), -200, -200 + 360 * k, fill=(220, 40, 40), width=7)
    if T >= WT("F02", "repita."): stamp(c, T, WT("F02", "repita."), "¿REPETIR?", 760, 1180, ROJO, -10, 92)
    manuscrito(c, ["Maestra Marta"], T, e0 - .6, e0, 610, 1290, 52, (40, 40, 120))
    return c

def sc_celular(T):
    """F03: 30 DÍAS enorme y el grupo de mamás: la hija de la vecina ya escribe nombre y apellido."""
    s0, e0 = TL["F03"]; tc = WT("F03", "celular:")
    c = bg("bg_mesa", T, s0, 1.4, 1.5, 12, .5, .5); dark(c, 70)
    if T < tc - .1:
        d = ImageDraw.Draw(c); k = popscale(T, s0, .35)
        text(d, (540, 720), "30", 380 * max(k, .01), YEL, stroke=14)
        text(d, (540, 960), "DÍAS", 130 * max(k, .01), WHITE, stroke=10)
        if T >= WT("F03", "tres"): etiqueta(c, T, WT("F03", "tres"), "LO LEES 3 VECES", 540, 1180, ROSA, OL, 40)
        return c
    ts = WT("F03", "Sofía"); ta = WT("F03", "apellido.")
    def cont(d, lay, x, y, w, h, s):
        d.rectangle((x, y, x + w, y + 120 * s), fill=(214, 84, 120))
        d.text((x + 40 * s, y + 80 * s), "Mamás 1.º B", font=font(F_UI, int(34 * s)), fill=WHITE, anchor="lm")
        d.text((x + 40 * s, y + 112 * s), "38 participantes", font=font(F_UI, int(20 * s)), fill=(255, 220, 230), anchor="lm")
        yy = y + 160 * s
        yy += burbuja(d, x + 24 * s, yy, w - 120 * s, "Mamá de Lucas", "¿Alguien tiene la lista\nde útiles? 🙏".replace(" 🙏", ""), s) + 20 * s
        if T >= ts:
            k = ease((T - ts) / .3)
            hh = burbuja(d, x + 24 * s, yy + 40 * (1 - k), w - 70 * s, "Mamá de Sofía", "¡Miren! Sofía ya escribe\nsu nombre COMPLETO", s)
            yy += hh + 16 * s
            # foto de la hoja de Sofía
            px0, py0 = x + 24 * s, yy
            d.rounded_rectangle((px0, py0, px0 + w - 70 * s, py0 + 250 * s), 20 * s, fill=(255, 253, 244), outline=(210, 200, 190), width=2)
            d.text((px0 + (w - 70 * s) / 2, py0 + 100 * s), "Sofía", font=font(F_HAND, int(96 * s)), fill=(214, 84, 160), anchor="mm")
            if T >= ta: d.text((px0 + (w - 70 * s) / 2, py0 + 190 * s), "Ramírez López", font=font(F_HAND, int(70 * s)), fill=(214, 84, 160), anchor="mm")
            yy += 270 * s
            if T >= ta:
                for i, r_ in enumerate(("Qué orgullo!!", "Wow, tan chiquita", "Mi hija también")):
                    if T >= ta + .25 * i:
                        d.rounded_rectangle((x + 24 * s + i * 150 * s, yy, x + 160 * s + i * 150 * s, yy + 50 * s), 25 * s, fill=(255, 228, 236))
                        d.text((x + 92 * s + i * 150 * s, yy + 25 * s), ["❤ 12", "❤ 9", "❤ 7"][i].replace("❤", "♥"), font=font(F_UI, int(24 * s)), fill=(214, 84, 120), anchor="mm")
    sh = 14 * math.exp(-(T - tc) * 6) if T >= tc else 0
    k = ease((T - tc) / .4)
    celular(c, T=T, cx=540, cy=900 + 700 * (1 - k), s=1.2, contenido=cont, shake=sh)
    return c

def sc_mateo_intro(T):
    """F04: Mateo en su cuarto lleno de dinosaurios; aparece un lápiz y se esconde."""
    s0, e0 = TL["F04"]
    c = bg("bg_cuarto", T, s0, 1.0, 1.1, 9, .5, .4)
    tl = WT("F04", "lápiz…"); te = WT("F04", "esconde.")
    hide = ease((T - te + .2) / .45) if T >= te - .2 else 0
    kind = "neutral" if T < tl else "triste"
    bob = 8 * math.sin(T * 2.4)
    mateo(c, kind, 430, 1260 + bob + 900 * hide, 1.05, T)
    put(c, "dino", 900, 1560, .45, rot=6 * math.sin(T * 1.5))
    ficha(c, T, s0 + .15, 60, 440, "MATEO", "4 AÑOS Y MEDIO", "AMA LOS DINOSAURIOS", 470)
    if T >= tl:   # el lápiz entra amenazante
        k = ease((T - tl) / .4)
        put(c, "lapiz", 1300 - 560 * k, 760 + 20 * math.sin(T * 5), 1.0, rot=-6)
    if T >= te: etiqueta(c, T, te, "SE ESCONDE", 540, 1180, ROSA, OL, 46)
    return c

def sc_mesa_nombre(T):
    """F05: en la mesa de la cocina; mamá escribe MATEO grande, letra a letra, y debajo en punteado para que lo repase."""
    s0, e0 = TL["F05"]; tg = WT("F05", "grande:")
    if T < WT("F05", "nombre") - .1:
        c = bg("bg_cocina", T, s0, 1.0, 1.08, 6, .5, .6)
        mateo(c, "neutral", 540, 1250, .95, T)
        put(c, "lapiz", 640, 1640, .7, rot=10)
        etiqueta(c, T, s0 + .3, "ESA TARDE · LA COCINA", 540, 470, CREMA, OL, 34)
        return c
    c = bg("bg_mesa", T, s0, 1.1, 1.2, 9, .5, .5)
    put(c, "hoja", 540, 900, 1.05)
    tt = [WT("F05", "M,"), WT("F05", "A,"), WT("F05", "T,"), WT("F05", "E,"), WT("F05", "O.")]
    palabra(c, "MATEO", 540, 900, 1.05, 0, T, tt)
    palabra(c, "MATEO", 540, 900, 1.05, 1, T, [x + .12 for x in tt], (150, 160, 200), punteado=True)
    return c

def sc_berrinche(T):
    """F06: Mateo no quiere ('¡Me aburro!')."""
    s0, e0 = TL["F06"]
    c = bg("bg_cocina", T, s0 - .2, 1.15, 1.22, 5, .5, .62)
    sh = 6 * math.sin(T * 30) if talk("F06", T) else 0
    mateo(c, "enojado", 540 + sh, 1230, 1.1, T, "F06")
    put(c, "hoja", 540, 1640, .6, rot=-3)
    if T >= WT("F06", "aburro!"): stamp(c, T, WT("F06", "aburro!"), "¡ME ABURRO!", 540, 560, ROJO, -6, 100)
    return c

def sc_lapiz(T):
    """F07: le pones el lápiz en la mano (plano medio) ... aprieta tan fuerte (cenital: su puño) que la punta se rompe."""
    s0, e0 = TL["F07"]; ta = WT("F07", "Aprieta"); tr = WT("F07", "rompe.")
    if T < ta - .1:
        c = bg("bg_cocina", T, s0 - .2, 1.15, 1.22, 5, .5, .62)
        cx, cy, sc = 540, 1250, 1.05
        mateo(c, "enojado", cx, cy, sc, T)
        hx, hy = cx + 250 * sc, cy + 200 * sc + 286 * sc   # su mano derecha
        put(c, "lapiz_v", hx, hy - 120, .9, rot=-14)
        d = ImageDraw.Draw(c)   # dedos que cierran el puño sobre el lápiz
        for k in range(3):
            d.ellipse((hx - 46 + k * 4, hy - 40 + k * 26, hx + 30 + k * 4, hy + k * 26), fill=(243, 194, 155), outline=OL, width=5)
        etiqueta(c, T, s0 + .3, "EL LÁPIZ EN SU MANO", 540, 520, CREMA, OL, 36)
        return c
    c = bg("bg_mesa", T, ta, 1.3, 1.45, 6, .5, .5)
    put(c, "hoja", 540, 900, 1.15)
    palabra(c, "MATEO", 540, 900, 1.15, 0, T)
    palabra(c, "MATEO", 540, 900, 1.15, 1, T, col=(150, 160, 200), punteado=True)
    _, yb = fila(540, 900, 1.15, 1)
    tf = WT("F07", "fuerte…")
    tremor = 2 + 10 * clamp((T - ta) / max(.3, tr - ta))
    tipx, tipy = 260, yb - 20    # la punta apoyada al empezar la M punteada
    sm = .62                     # escala de la capa mano_lapiz (punta en 150,830 de 1000x1000)
    def mano(name, dx=0, dy=0, rot=0):
        put(c, name, tipx + (500 - 150) * sm + dx, tipy + (500 - 830) * sm + dy, sm, rot=rot)
    if T < tr:
        mano("mano_lapiz", tremor * math.sin(T * 70), tremor * math.cos(T * 63))
        if T >= tf: etiqueta(c, T, tf, "APRIETA... APRIETA...", 540, 520, CREMA, OL, 40)
    else:
        k = ease((T - tr) / .5)
        mano("mano_lapiz_rota", 30 * k, 26 * k)
        d = ImageDraw.Draw(c)
        px, py = tipx - 60 - 260 * k, tipy - 40 - 420 * k + 520 * k * k   # la punta sale volando
        d.polygon([(px, py), (px + 30, py + 14), (px + 4, py + 30)], fill=(242, 210, 168), outline=OL)
        d.ellipse((px - 4, py - 4, px + 8, py + 8), fill=OL)
        for a in range(0, 360, 45):   # chispazo del crac
            r1, r2 = 26 + 50 * k, 60 + 110 * k
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            d.line((tipx + ca * r1, tipy + sa * r1, tipx + ca * r2, tipy + sa * r2), fill=(255, 200, 70), width=8)
        stamp(c, T, tr, "¡CRAC!", 540, 520, ROJO, 8, 140)
    return c

def sc_llanto(T):
    """F08: '¡Yo no sé escribir!' llorando."""
    c = bg("bg_cocina", T, S("F08") - .2, 1.25, 1.32, 5, .5, .62)
    sh = 5 * math.sin(T * 34)
    mateo(c, "llora", 540 + sh, 1220, 1.18, T, "F08")
    lagrimas(c, 540 + sh, 1220, 1.18, T)
    return c

def sc_sehuye(T):
    """F09: se va corriendo; en la hoja queda una sola M torcida y al revés."""
    s0, e0 = TL["F09"]; th = WT("F09", "hoja")
    if T < th - .1:
        c = bg("bg_cocina", T, s0, 1.12, 1.0, 2, .5, .6)
        k = ease((T - s0) / .9)
        x = 540 - 1300 * k
        mateo(c, "llora", x, 1230 - 40 * abs(math.sin(T * 14)), 1.0, T, rot=8)
        for i in range(4):   # líneas de velocidad
            ImageDraw.Draw(c).line((x + 380 + i * 30, 900 + i * 90, x + 620 + i * 60, 900 + i * 90), fill=(255, 255, 255), width=10)
        return c
    c = bg("bg_mesa", T, th, 1.3, 1.45, 7, .5, .48); dark(c, 40)
    put(c, "hoja", 540, 900, 1.15)
    palabra(c, "MATEO", 540, 900, 1.15, 0, T)
    palabra(c, "MATEO", 540, 900, 1.15, 1, T, col=(150, 160, 200), punteado=True)
    k = popscale(T, WT("F09", "letra:"), .35)
    if k > 0:   # la M de Mateo: torcida, al revés y saliéndose de la pauta
        ytop, yb = fila(540, 900, 1.15, 1)
        g = Image.new("RGBA", (420, 420), (0, 0, 0, 0))
        ImageDraw.Draw(g).text((210, 210), "M", font=font(F_ESC, 300), fill=(70, 70, 96), anchor="mm")
        g = g.rotate(163, resample=Image.BICUBIC)
        g = g.resize((max(1, int(420 * k)), max(1, int(420 * k))))
        c.alpha_composite(g, (int(300 - g.width / 2), int((ytop + yb) / 2 + 20 - g.height / 2)))
    if T >= WT("F09", "torcida…"): etiqueta(c, T, WT("F09", "torcida…"), "TORCIDA", 300, 1350, CREMA, OL, 42)
    if T >= WT("F09", "revés."): etiqueta(c, T, WT("F09", "revés."), "Y AL REVÉS", 760, 1350, ROSA, OL, 42)
    return c

def sc_timbre(T):
    """F10: suena el timbre; entra la abuela Pilar y suspira al ver la hoja."""
    s0, e0 = TL["F10"]; ta = WT("F10", "mamá,")
    c = bg("bg_puerta", T, s0, 1.0, 1.1, 8, .5, .55)
    d = ImageDraw.Draw(c)
    tt = WT("F10", "timbre.")
    if 0 <= T - tt < 1.2:   # ondas del timbre
        for i in range(3):
            r = 40 + ((T - tt) * 200 + i * 40) % 160
            d.arc((155 - r, 810 - r, 155 + r, 810 + r), -60, 60, fill=YEL, width=7)
            d.arc((155 - r, 810 - r, 155 + r, 810 + r), 120, 240, fill=YEL, width=7)
    if T >= ta - .3:
        k = ease((T - ta + .3) / .6)
        abuela(c, 540, 1180 + 700 * (1 - k), 1.0, T)
        ficha(c, T, ta + .2, 60, 440, "ABUELA PILAR", "TU MAMÁ", "'EN MIS TIEMPOS…'", 470)
    if T >= WT("F10", "suspira."): etiqueta(c, T, WT("F10", "suspira."), "*SUSPIRA*", 760, 820, CREMA, OL, 40)
    return c

def sc_abuela(T):
    """F11: 'A ese niño le falta mano dura.'"""
    s0, e0 = TL["F11"]
    c = bg("bg_cocina", T, s0 - .2, 1.2, 1.28, 9, .3, .55)
    abuela(c, 560, 1260, 1.12, T, "F11")
    if T >= WT("F11", "cursiva."): etiqueta(c, T, WT("F11", "cursiva."), "¿¿EN CURSIVA??", 540, 470, CREMA, OL, 40)
    if T >= WT("F11", "dura."): stamp(c, T, WT("F11", "dura."), "MANO DURA", 540, 600, (130, 70, 170), -8, 100)
    return c

CONSEJOS = ["Castígalo sin tablet", "¡No lo presiones!", "Espera a los 7 años", "Practica 1 hora diaria", "Dale premios", "Solo con juegos",
            "Que repita planas", "Llévalo a terapia", "Es flojera", "Cada niño a su ritmo", "Usa cuadernos caros", "No hagas nada"]
def sc_noche(T):
    """F12: de noche, buscas en el celular y llueven mil consejos contradictorios."""
    s0, e0 = TL["F12"]; tb = WT("F12", "buscas"); tm = WT("F12", "Mil")
    c = bg("bg_noche", T, s0, 1.0, 1.08, 12)
    q = "mi hijo no quiere escribir"
    t0q, t1q = WT("F12", "mi"), WT("F12", "escribir.") + .3
    nq = int(len(q) * clamp((T - t0q) / max(.2, t1q - t0q))) if T >= t0q else 0
    def cont(d, lay, x, y, w, h, s):
        d.rounded_rectangle((x + 30 * s, y + 120 * s, x + w - 30 * s, y + 200 * s), 40 * s, fill=WHITE, outline=(200, 200, 210), width=3)
        d.text((x + 70 * s, y + 160 * s), q[:nq] + ("|" if (T * 2) % 1 < .5 else ""), font=font(F_UI, int(30 * s)), fill=OL, anchor="lm")
        if T >= tm:
            for i, cs in enumerate(CONSEJOS[:int(clamp((T - tm) / 1.6) * len(CONSEJOS)) + 1]):
                yy = y + (240 + i * 62) * s
                if yy > y + h - 40 * s: break
                d.rounded_rectangle((x + 30 * s, yy, x + w - 30 * s, yy + 52 * s), 14 * s, fill=(232, 238, 255) if i % 2 else (255, 236, 240))
                d.text((x + 50 * s, yy + 26 * s), cs, font=font(F_UI, int(26 * s)), fill=OL, anchor="lm")
    k = ease((T - s0) / .5)
    if T >= tb - .2:
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((140, 420, 940, 1500), fill=(120, 170, 255, 60))
        c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(70)))
        celular(c, 540, 930 + 600 * (1 - ease((T - tb + .2) / .5)), 1.25, T, cont)
    if T >= WT("F12", "distintos."):
        td = WT("F12", "distintos.")
        dark(c, 150 * ease((T - td) / .25))
        stamp(c, T, td, "¿A QUIÉN", 540, 820, YEL, -4, 120)
        stamp(c, T, td + .15, "LE HAGO CASO?", 540, 1030, YEL, 3, 110)
    if T < tb - .2:
        etiqueta(c, T, s0 + .2, "ESA NOCHE", 540, 600, (60, 70, 130), WHITE, 44)
    return c

def sc_dia2(T):
    """F13: DÍA 2. Desayuno: Mateo empuja el cuaderno y la leche cae sobre la hoja."""
    s0, e0 = TL["F13"]; tl = WT("F13", "leche")
    if T < s0 + .9:   # cartel DÍA 2 con amanecer
        c = bg("bg_cocina", T, s0 - .9, 1.3, 1.2, 2, .2, .3)
        gl = Image.new("RGBA", (W, H), (255, 200, 120, 90)); c.alpha_composite(gl)
        d = ImageDraw.Draw(c); k = popscale(T, s0 - .6, .4)
        text(d, (540, 880), "DÍA 2", 230 * max(k, .01), WHITE, stroke=14, sfill=(214, 84, 120))
        text(d, (540, 1060), "QUEDAN 29", 80 * max(k, .01), YEL, stroke=8)
        return c
    c = bg("bg_mesa", T, s0, 1.15, 1.3, 9, .5, .5)
    te = WT("F13", "empuja")
    dx = 160 * ease((T - te) / .4) if T >= te else 0
    put(c, "hoja", 520 + dx, 1000, 1.0)
    palabra(c, "MATEO", 520 + dx, 1000, 1.0, 0, T)
    palabra(c, "MATEO", 520 + dx, 1000, 1.0, 1, T, col=(150, 160, 200), punteado=True)
    if T < tl:
        put(c, "vaso", 860, 620, .55)
    else:
        k = ease((T - tl) / .35)
        put(c, "vaso", 860 - 120 * k, 640 + 40 * k, .55, rot=-95 * k)
        charco(c, 600, 900, T, tl + .2)
    if T >= WT("F13", "encima"): stamp(c, T, WT("F13", "encima"), "¡NOOO!", 540, 1260, ROJO, -6, 100)
    etiqueta(c, T, s0 + 1.0, "DESAYUNO", 540, 380, CREMA, OL, 36)
    return c

def sc_feas(T):
    """F14: '¡Las letras son feas!'"""
    c = bg("bg_cocina", T, S("F14") - .2, 1.25, 1.3, 4, .5, .62)
    sh = 7 * math.sin(T * 36)
    mateo(c, "enojado", 540 + sh, 1220, 1.2, T, "F14")
    lagrimas(c, 540 + sh, 1220, 1.2, T)
    if T >= WT("F14", "feas!"): stamp(c, T, WT("F14", "feas!"), "¡SON FEAS!", 540, 520, ROJO, 6, 110)
    return c

def sc_grito(T):
    """F15: le gritas. Silencio. Mateo con los ojos llenos de lágrimas (empuje lento)."""
    s0, e0 = TL["F15"]; tg = WT("F15", "gritas.")
    c = bg("bg_cocina", T, s0, 1.35, 1.6, e0 - s0, .5, .6)
    dark(c, 60 * clamp((T - tg) / .5))
    z = 1.3 + .25 * clamp((T - s0) / (e0 - s0))
    mateo(c, "triste", 540, 1250 + (z - 1.3) * 300, z, T)
    if T >= tg:   # onda del grito
        k = (T - tg) / .7
        if k < 1:
            d = ImageDraw.Draw(c)
            for i in range(3):
                r = 200 + 900 * k + i * 90
                d.ellipse((540 - r, 1900 - r, 540 + r, 1900 + r), outline=(255, 255, 255), width=int(10 * (1 - k)) + 1)
    if T >= WT("F15", "callado…"):
        etiqueta(c, T, WT("F15", "callado…"), "...", 540, 520, CREMA, OL, 60)
    return c

def sc_piso(T):
    """F16: te sientas en el piso. 29 días. 0 letras."""
    s0, e0 = TL["F16"]
    c = bg("bg_cocina", T, s0, 1.05, 1.0, 6, .5, .9); dark(c, 120)
    d = ImageDraw.Draw(c)
    t29 = WT("F16", "29"); tl = WT("F16", "una")
    if T >= t29:
        k = popscale(T, t29, .4)
        text(d, (540, 740), "29", 300 * max(k, .01), YEL, stroke=12)
        text(d, (540, 920), "DÍAS", 100 * max(k, .01), WHITE, stroke=8)
    if T >= tl:
        k = popscale(T, tl, .4)
        text(d, (540, 1130), "0 LETRAS", 130 * max(k, .01), (255, 130, 120), stroke=10)
    return c

def sc_vuelve(T):
    """F17: Mateo vuelve despacito con su dinosaurio y una crayola verde."""
    s0, e0 = TL["F17"]
    c = bg("bg_cocina", T, s0, 1.1, 1.0, 7, .5, .62)
    dark(c, 70 * (1 - clamp((T - s0) / 4)))
    k = ease((T - s0) / 2.2)
    x = -300 + 840 * k; bob = 14 * abs(math.sin(T * 3)) * (1 - k)
    mateo(c, "timido", x, 1260 - bob, 1.0, T)
    if T >= WT("F17", "dinosaurio…") - .2:
        put(c, "dino", x - 210, 1440, .55 * max(.05, popscale(T, WT("F17", "dinosaurio…") - .2, .4)))
    if T >= WT("F17", "crayola"):
        put(c, "crayola", x + 260, 1420, .6 * max(.05, popscale(T, WT("F17", "crayola"), .4)), rot=10)
        brillos(c, T, WT("F17", "crayola"), x + 260, 1400)
    return c

def brillos(c, T, t0, cx, cy):
    if T < t0: return
    d = ImageDraw.Draw(c)
    for i in range(7):
        a = i * 0.9 + T * .8; r = 120 + 30 * math.sin(T * 3 + i)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a) * .7
        s = 10 + 6 * math.sin(T * 6 + i)
        d.polygon([(x, y - s * 2), (x + s * .5, y - s * .5), (x + s * 2, y), (x + s * .5, y + s * .5), (x, y + s * 2), (x - s * .5, y + s * .5), (x - s * 2, y), (x - s * .5, y - s * .5)], fill=(255, 240, 150))

def sc_rex(T):
    """F18: '¿El Rex puede tener nombre también?'"""
    s0, e0 = TL["F18"]
    c = bg("bg_cocina", T, s0 - .3, 1.22, 1.28, 6, .5, .62)
    mateo(c, "timido", 470, 1250, 1.15, T, "F18")
    put(c, "dino", 860, 1450, .7, rot=5 * math.sin(T * 2))
    put(c, "crayola", 250, 1560, .55, rot=-15)
    brillos(c, T, s0, 860, 1300)
    return c

# ---------------------------------------------------------------- final A/B (pantalla partida con rayo)
RAYO = [(600, 0), (560, 520), (612, 560), (522, 1100), (578, 1132), (480, H)]
_FC = {}
def _lado(name):
    if name in _FC: return _FC[name]
    if name == "A":
        A = bg("bg_cocina", 0, 0, 1.3, 1.3, 1, .9, .6).convert("RGBA")
        put(A, "abuela", 250, 1820, .75); put(A, "tablet", 280, 960, .62)
        A.alpha_composite(Image.new("RGBA", (W, H), (40, 30, 90, 110)))
    else:
        A = bg("bg_cuarto", 0, 0, 1.2, 1.2, 1, .5, .6).convert("RGBA")
        put(A, "mateo_timido", 820, 1880, .75); put(A, "dino", 780, 990, .5); put(A, "crayola", 930, 1110, .4, rot=-20)
        A.alpha_composite(Image.new("RGBA", (W, H), (20, 90, 50, 90)))
    _FC[name] = A
    return A

def _opcion(d, cx, cy, letra, t1, t2, t3, col, k, big=1.0):
    r = 82 * k * big
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col, outline=WHITE, width=8)
    text(d, (cx, cy), letra, 116 * k * big, WHITE)
    if k > .5:
        for i, l in enumerate(t1.split("\n")):
            text(d, (cx, cy + 150 + i * 78), l, 70 * big, WHITE, stroke=8)
        off = 78 * (len(t1.split("\n")) - 1)
        text(d, (cx, cy + 230 + off), t2, 38, (150, 255, 170), "mm", F_UI, stroke=6)
        text(d, (cx, cy + 282 + off), t3, 36, (255, 170, 160), "mm", F_UI, stroke=6)

def sc_final(T):
    s0, e0 = TL["F19"]; ta, tb = WT("F19", "A:"), WT("F19", "B:")
    hiA = ta <= T < tb; hiB = tb <= T < e0
    A, B = _lado("A"), _lado("B")
    u = ease((T - s0 + .25) / .45)
    c = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    negro = Image.new("RGBA", (W, H), (0, 0, 0, 255))
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
    for cx, L_, t1, t2, t3, col, t0, h in ((270, "A", "MANO\nDURA", "+ Disciplina", "- Más lágrimas", AZ, ta, hiA),
                                           (790, "B", "EL NOMBRE\nDEL REX", "+ Lo hace jugando", "- Pierdes otro día", VERDE, tb, hiB)):
        k = popscale(T, t0, .35)
        if k > 0: _opcion(d, cx, 420, L_, t1, t2, t3, col, k, 1.08 if h else 1.0)
    if T >= S("F20") - .1:   # cierre: vota en la encuesta, las opciones se iluminan por turnos
        k = popscale(T, S("F20") - .1, .4)
        d.rounded_rectangle((540 - 390 * k, 1250, 540 + 390 * k, 1350), 50, fill=WHITE, outline=OL, width=6)
        if k > .5:
            text(d, (540, 1286), "VOTA EN LA ENCUESTA", 54, OL)
            text(d, (540, 1328), "y dime en comentarios por qué", 28, (200, 50, 80), "mm", F_UI)
    return c

# ---------------------------------------------------------------- orden y transiciones
SCENES = [
    (0, sc_mochila), (S("F02") - .15, sc_nota), (S("F03") - .15, sc_celular), (S("F04") - .2, sc_mateo_intro),
    (S("F05") - .2, sc_mesa_nombre), (S("F06") - .15, sc_berrinche), (S("F07") - .15, sc_lapiz), (S("F08") - .1, sc_llanto),
    (S("F09") - .1, sc_sehuye), (S("F10") - .2, sc_timbre), (S("F11") - .15, sc_abuela), (S("F12") - .25, sc_noche),
    (S("F13") - .9, sc_dia2), (S("F14") - .1, sc_feas), (S("F15") - .1, sc_grito), (S("F16") - .3, sc_piso),
    (S("F17") - .4, sc_vuelve), (S("F18") - .2, sc_rex), (S("F19") - .3, sc_final),
]
IMPACTS = [WT("F01", "rojo."), WT("F02", "repita."), WT("F07", "rompe."), WT("F09", "revés."), WT("F13", "leche"),
           WT("F14", "feas!"), WT("F15", "gritas."), S("F19")]
AVISOS[:] = [S("F05") - .2, S("F10") + .6]
SUAVES = {S("F15") - .1, S("F16") - .3, S("F17") - .4, S("F18") - .2}   # cortes sin flash, más tiernos

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
    if T < S("F20") - .1: R.draw_caption(c, T)   # en el cierre manda la píldora de votar
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
