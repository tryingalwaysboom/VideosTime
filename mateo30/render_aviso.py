"""Vídeo normal para la cuenta vieja (@aprendeconpinti): avisa de la serie nueva "Mateo: 30 días para no repetir" y manda a @escribirconpinti.
Pensado para el Para ti: se entiende sin conocer la serie, con un momento gracioso (postre, la raya, Rex) y otro tierno.
Uso: python3 render_aviso.py still 1 5 | info | video"""
import os, sys, math, json, subprocess, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import render_d1 as D                       # utilidades de dibujo de la temporada
import importlib.util
from PIL import Image, ImageDraw, ImageFilter

os.environ["GUION"] = "guion_daviso"; os.environ["VOZDIR"] = os.path.join(HERE, "voz_daviso")
_spec = importlib.util.spec_from_file_location("R2", os.path.join(HERE, "..", "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
R.LAY = D.R.LAY
R.GAP.clear(); R.GAP.update({"A02": .3, "A03": .25, "A04": .3, "A05": .35, "A06": .5, "A07": .45, "A08": .35, "A09": .5, "A10": .3, "A11": .3})
R.TL, R.TOTAL = R.timeline()
R.TL = {k: (a - .1, b - .1) for k, (a, b) in R.TL.items()}; R.TOTAL = R.TL["A11"][1] + .1     # corte en seco
TL, TOTAL, S, E, WT = R.TL, R.TOTAL, R.S, R.E, R.WT
# subtítulos con el estilo de la temporada pero con los tiempos de esta story
D.LINEAS = R.LINEAS; _R = D.R; D.R = R; D.CH = D.chunks(); D.R = _R
CH = D.CH
W, H, FPS = D.W, D.H, D.FPS
ease, clamp, back, font = D.ease, D.clamp, D.back, D.font
pop, u_, pizarra, tiza, rotulo, lapiz_rojo, paste_rot, sombra = D.pop, D.u_, D.pizarra, D.tiza, D.rotulo, D.lapiz_rojo, D.paste_rot, D.sombra
OL, AMA, ROJO, CREMA, AZUL, TIZA, PIZ2 = D.OL, D.AMA, D.ROJO, D.CREMA, D.AZUL, D.TIZA, D.PIZ2
ROSA = (232, 85, 109)
TMP = os.path.join(HERE, "tmp_aviso"); os.makedirs(TMP, exist_ok=True)
def talk(l, T): return S(l) <= T < E(l)

def mateo(c, kind, hx, hy, s, T, lid=None):
    hab = lid is not None and talk(lid, T)
    D.put(c, f"mateo_{kind}_hab" if hab else f"mateo_{kind}", hx, hy + 498 * s, s)
    if hab: D.mouth(c, hx, hy + 150 * s, T, True, int(26 * s))
    elif kind in ("neutral", "timido", "triste", "susto") and (T % 3.7) < .11: D.parpadeo(c, hx, hy, s)

def zoomcam(c, T, t0, z0, z1, d, cx=W / 2, cy=H / 2):
    z = z0 + (z1 - z0) * ease(u_(T, t0, d)); return D.view(c, cx, cy, z) if z > 1.001 else c

# ---------------------------------------------------------------- captura del perfil (real)
PERFIL = os.path.join(HERE, "story", "perfil_escribirconpinti.jpg")
TILE1 = (0, 1060, 357, 1537)          # portada del Día 1 en la captura
TILE_CUAD = (361, 1060, 718, 1537)    # portada del cuaderno de la abuela: se tapa
SEGUIR = (36, 521, 456, 640)          # botón Seguir
_P = {}
def perfil():
    if "p" not in _P:
        im = Image.open(PERFIL).convert("RGBA")
        x0, y0, x1, y1 = TILE_CUAD                     # tapar la portada del cuaderno
        reg = im.crop(TILE_CUAD).filter(ImageFilter.GaussianBlur(28))
        reg.alpha_composite(Image.new("RGBA", reg.size, PIZ2 + (215,)))
        im.paste(reg, (x0, y0))
        _P["p"] = im
    return _P["p"]

def telefono(c, T, sc, cx, cy, foco=None, z=1.0, brillo=0.0):
    """Pantalla de móvil con la captura; foco = punto de la captura que queda en el centro."""
    p = perfil(); pw, ph = p.size
    fx, fy = foco or (pw / 2, ph / 2)
    vw, vh = 820, 1300                                    # ventana visible del móvil
    cw, chh = vw / (sc * z), vh / (sc * z)
    x0 = max(0, min(pw - cw, fx - cw / 2)); y0 = max(0, min(ph - chh, fy - chh / 2))
    win = p.resize((vw, vh), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + chh))
    frame = Image.new("RGBA", (vw + 44, vh + 44), (0, 0, 0, 0)); d = ImageDraw.Draw(frame)
    d.rounded_rectangle((0, 0, vw + 43, vh + 43), 60, fill=(22, 22, 30, 255))
    m = Image.new("L", (vw, vh), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, vw - 1, vh - 1), 42, fill=255)
    frame.paste(win, (22, 22), m)
    sombra(c, (cx - frame.width / 2, cy - frame.height / 2, cx + frame.width / 2, cy + frame.height / 2), 60, 120, 20)
    c.alpha_composite(frame, (int(cx - frame.width / 2), int(cy - frame.height / 2)))
    k = vw / cw                                          # captura -> pantalla
    def to_scr(x, y): return cx - vw / 2 + (x - x0) * k, cy - vh / 2 + (y - y0) * k
    if brillo > 0:                                       # marco que late en la portada del Día 1
        a, b = to_scr(TILE1[0], TILE1[1]); a2, b2 = to_scr(TILE1[2], TILE1[3])
        g = 10 + 6 * math.sin(T * 9); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        for i in range(4):
            dl.rounded_rectangle((a - g - i * 7, b - g - i * 7, a2 + g + i * 7, b2 + g + i * 7), 20, outline=AMA + (int(255 * brillo * (1 - i * .23)),), width=9)
        c.alpha_composite(lay)
    return to_scr

def corazon(d, cx, cy, r, col):
    d.ellipse((cx - r, cy - r * .8, cx, cy + r * .2), fill=col); d.ellipse((cx, cy - r * .8, cx + r, cy + r * .2), fill=col)
    d.polygon([(cx - r * .97, cy - r * .15), (cx + r * .97, cy - r * .15), (cx, cy + r)], fill=col)

def chispas(c, T, t0, cx, cy, rad=300, n=14, seed=2):
    if T < t0: return
    r = random.Random(seed); d = ImageDraw.Draw(c); u = T - t0
    for k in range(n):
        a = r.uniform(0, 2 * math.pi); sp = r.uniform(.6, 1.2); v = min(1, u * 2.2 * sp)
        x, y = cx + math.cos(a) * rad * v, cy + math.sin(a) * rad * v; s = 14 * (1 - min(1, u / 1.4))
        if s > 1: d.polygon([(x, y - s * 2), (x + s * .6, y), (x, y + s * 2), (x - s * .6, y)], fill=AMA); d.polygon([(x - s * 2, y), (x, y - s * .6), (x + s * 2, y), (x, y + s * .6)], fill=AMA)

# ================================================================ ESCENAS
DINO = Image.open(os.path.join(HERE, "..", "mateo-pov", "layers", "dino.png")).convert("RGBA")
def rex(c, x, y, s, T, rot=0):
    paste_rot(c, DINO, x, y + 6 * math.sin(T * 3.2), s, rot + 4 * math.sin(T * 2.4))

def flan(c, cx, cy, s, T, t0):
    """Flan que tiembla (gelatina) al aparecer."""
    k = pop(T, t0, .35)
    if k <= 0: return
    s *= k; j = 1 + .08 * math.sin((T - t0) * 22) * math.exp(-(T - t0) * 2.5)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse((cx - 250 * s, cy + 80 * s, cx + 250 * s, cy + 170 * s), fill=CREMA, outline=OL, width=7)      # plato
    w0, w1, h = 190 * s * j, 130 * s / j, 220 * s / j
    d.polygon([(cx - w0, cy + 120 * s), (cx + w0, cy + 120 * s), (cx + w1, cy + 120 * s - h), (cx - w1, cy + 120 * s - h)], fill=(250, 200, 90), outline=OL)
    d.line([(cx - w0, cy + 120 * s), (cx - w1, cy + 120 * s - h), (cx + w1, cy + 120 * s - h), (cx + w0, cy + 120 * s)], fill=OL, width=7)
    d.ellipse((cx - w1, cy + 120 * s - h - 26 * s, cx + w1, cy + 120 * s - h + 26 * s), fill=(150, 80, 30), outline=OL, width=6)
    d.polygon([(cx - w1 * .8, cy + 120 * s - h + 10 * s), (cx - w1 * .6, cy + 120 * s - h + 80 * s), (cx - w1 * .4, cy + 120 * s - h + 14 * s)], fill=(150, 80, 30))
    c.alpha_composite(lay)

def cartas_ab(c, T, t0):
    """Dos tarjetas de decisión que se balancean: tú decides."""
    for i, (txt, col) in enumerate((("A", AZUL), ("B", ROJO))):
        k = pop(T, t0 + i * .12, .3)
        if k <= 0: continue
        x = W / 2 + (-210 if i == 0 else 210); y = 1000 + 14 * math.sin(T * 4 + i * 2)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        w, h = 170 * k, 220 * k
        d.rounded_rectangle((x - w, y - h, x + w, y + h), 30, fill=CREMA, outline=OL, width=8)
        d.ellipse((x - 90 * k, y - 140 * k, x + 90 * k, y + 40 * k), fill=col, outline=OL, width=6)
        d.text((x, y - 50 * k), txt, font=font(D.F_BAL, int(130 * k)), fill=CREMA, anchor="mm")
        d.text((x, y + 130 * k), "?", font=font(D.F_BAL, int(90 * k)), fill=OL, anchor="mm")
        c.alpha_composite(lay.rotate((-6 if i == 0 else 6) + 3 * math.sin(T * 3 + i), center=(x, y), resample=Image.BICUBIC))

def sc_nota(T):
    """0 s: la nota enorme con REPITE ya rodeado en rojo."""
    c = pizarra(); u = ease(T / .45); z = 1.18 - .14 * u + .03 * T
    cx, cy = W / 2, 820 + 40 * (1 - u); rot = -7 + 4 * u
    nb = D.nota_img(); sombra(c, (cx - 440 * z, cy - 560 * z, cx + 440 * z, cy + 560 * z), 24, 110, 22)
    paste_rot(c, nb, cx, cy, z, rot)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); x0, y0, x1, y1 = D.NOTA_REPITE
    lapiz_rojo(lay, (cx + x0 * z, cy + y0 * z, cx + x1 * z, cy + y1 * z), .35 + .65 * u_(T, 0, .4), 15)
    c.alpha_composite(lay.rotate(rot, center=(cx, cy), resample=Image.BICUBIC))
    return c

def sc_plazo(T):
    """'…30 días para escribir su nombre… o repite': Mateo y el calendario; al decir 'repite' se asusta."""
    t0 = WT("A01", "días") - .15; tr = WT("A01", "repite") - .15; c = pizarra(); d = ImageDraw.Draw(c)
    kind = "susto" if T >= tr else "timido"
    mateo(c, kind, W / 2, 820, 1.32, T)
    k = pop(T, t0 + .05, .3)
    if k > 0: D.calendario(d, 220, 420 + 6 * math.sin(T * 3), 1.6 * k, 30)
    kr = pop(T, tr, .3)
    if kr > 0: tiza(c, "¡REPITE!", 700, 380, int(130 * kr), ROJO, 6, f=D.F_ANTON, borde=True)
    return zoomcam(c, T, t0, 1.0, 1.08, 2.4, W / 2, 820)

def sc_postre(T):
    """'¿repetir es como repetir postre?': Mateo inocente y aparece un flan que tiembla."""
    t0 = S("A02") - .15; tp = WT("A02", "postre?") - .2; c = pizarra()
    mateo(c, "neutral" if T < tp else "feliz", W / 2 - (120 if T >= tp else 0) * ease(u_(T, tp, .3)), 820, 1.25, T, "A02")
    flan(c, 820, 1060, .8, T, tp)
    if T >= tp:
        dd = ImageDraw.Draw(c)
        for i, (x, y) in enumerate(((700, 760), (940, 720))):
            if pop(T, tp + .2 + i * .1, .25) > 0: corazon(dd, x, y - 8 * math.sin(T * 6 + i), 28, ROSA)
    return zoomcam(c, T, t0, 1.06, 1.0, 1.8, W / 2, 900)

def sc_amigos(T):
    """'Es quedarte un año más… sin tus amigos': la pared de nombres con su hueco."""
    t0 = S("A03") - .15; ta = WT("A03", "amigos.") - .25
    if T < WT("A03", "año") - .15:
        c = pizarra(); mateo(c, "triste", W / 2, 800, 1.4, T)
        return zoomcam(c, T, t0, 1.0, 1.05, 1.5, W / 2, 800)
    m = ease((T - ta) / .45)
    cx = 540 * (1 - m) + D.HUECO[0] * m; cy = 900 * (1 - m) + D.HUECO[1] * m; z = 1.08 + .5 * m
    im = D.pared_img().copy()
    if m > 0:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        a = int((120 + 80 * math.sin(T * 9)) * m)
        dl.rounded_rectangle((D.HUECO[0] - 110, D.HUECO[1] - 78, D.HUECO[0] + 110, D.HUECO[1] + 78), 14, fill=AMA + (a,))
        im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10)))
        ImageDraw.Draw(im).text(D.HUECO, "?", font=font(D.F_BAL, 110), fill=(110, 72, 40), anchor="mm")
    return D.view(im, cx, cy, z)

def sc_decidido(T):
    """'¡Entonces hoy aprendo! Dame una hoja.': Mateo se levanta decidido; la hoja cae del cielo."""
    t0 = S("A04") - .15; c = D.bg("bg_cocina", T, t0, 1.25, 1.32, 3, .5, .45)
    jump = 30 * abs(math.sin((T - t0) * 6)) * (1 - u_(T, t0, 1.0))
    mateo(c, "travieso" if T < WT("A04", "Dame") - .1 else "feliz", W / 2, 640 - jump, 1.3, T, "A04")
    k = pop(T, WT("A04", "hoy") - .15, .25)
    if k > 0: tiza(c, "¡HOY!", 820, 330, int(120 * k), AMA, 10, f=D.F_ANTON, borde=True)
    th = WT("A04", "hoja.") - .25
    if T >= th:
        u = ease(u_(T, th, .45)); paste_rot(c, D.hoja_img(), 540, 1250 - 900 * (1 - u), .55, 12 * (1 - u))
    return c

def sc_concentra(T):
    """'Aprieta la crayola, saca la lengua…': cara de concentración."""
    t0 = S("A05") - .2; c = D.bg("bg_cocina", T, t0, 1.5, 1.6, 3, .5, .4)
    tl = WT("A05", "saca") - .1
    z = 1.5 + .05 * u_(T, t0, 2) + .22 * ease((T - tl) / .25)
    mateo(c, "neutral" if T < tl else "concentra", W / 2, 760, z, T)
    if T < tl:
        D.put(c, "crayola", 720, 1250, .42, rot=30 + 3 * math.sin(T * 40))
        ImageDraw.Draw(c).ellipse((640, 1250, 780, 1380), fill=(243, 194, 155), outline=OL, width=6)
        k = pop(T, WT("A05", "crayola,") - .15, .2)
        if k > 0: tiza(c, "¡ÑIC!", 850, 1050, int(104 * k), AMA, 14, stroke=2, borde=True)
    return c

RAYA = D.raya_pts(210, 850, 892, 16, 3)
def sc_raya(T):
    """'…y escribe…': la mano agarra la crayola y traza de verdad, de izquierda a derecha."""
    t0 = WT("A05", "y") - .15; r0 = WT("A05", "escribe…") - .1; r1 = S("A06") - .05
    c = D._mesa(T, t0, 1.05); paste_rot(c, D.hoja_img(), D.HOJA_C[0], D.HOJA_C[1], 1.0, 0)
    u = u_(T, r0, r1 - r0); ue = u * u * (3 - 2 * u)
    n = max(1, int(len(RAYA) * ue)); pts = RAYA[:n + 1]; D.crayon(c, pts, 20)
    tip = pts[-1] if T >= r0 else (RAYA[0][0] - 30, RAYA[0][1] - 60 * (1 - u_(T, t0, max(.1, r0 - t0))))
    D.mano(c, tip, T if r0 <= T <= r1 else 0)
    return c

def sc_listo(T):
    """'¡Listo! Ahí dice Mateo.': Mateo orgulloso enseñando la hoja."""
    t0 = S("A06") - .2; c = D.bg("bg_cocina", T, t0, 1.3, 1.36, 3, .5, .45)
    jump = 26 * abs(math.sin((T - t0) * 7)) * (1 - u_(T, t0, 1.2))
    mateo(c, "feliz", W / 2, 600 - jump, 1.35, T, "A06")
    cy = 1200 - jump; lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    paste_rot(lay, D.hoja_img(), 540, cy, .7, 0); D.crayon(lay, D.raya_pts(310, 770, cy - 6, 11, 3), 15)
    c.alpha_composite(lay.rotate(-5, center=(540, cy), resample=Image.BICUBIC))
    d = ImageDraw.Draw(c)
    for sx in (-1, 1): d.ellipse((540 + sx * 370 - 58, cy - 54, 540 + sx * 370 + 58, cy + 54), fill=(243, 194, 155), outline=OL, width=6)
    k = pop(T, t0 + .2, .22)
    if k > 0: tiza(c, "¡LISTO!", 810, 420, int(112 * k), AMA, 10, stroke=2, borde=True)
    return c

def sc_era_raya(T):
    """'…era una raya.': zoom seco a la hoja; la raya rodeada en rojo."""
    t0 = S("A07") - .2; c = D._mesa(T, t0, 1.05); paste_rot(c, D.hoja_img(), D.HOJA_C[0], D.HOJA_C[1], 1.0, 0)
    D.crayon(c, RAYA, 20)
    lapiz_rojo(c, (150, 820, 910, 990), u_(T, WT("A07", "raya.") - .25, .35), 13, 4)
    return zoomcam(c, T, t0, 1.0, 1.35, .35, 540, 900)

def sc_rex(T):
    """'Rex dice que está perfecta.': Mateo abraza a su dino y susurra, feliz con su raya."""
    t0 = S("A08") - .2; c = D.bg("bg_cocina", T, t0, 1.4, 1.45, 3, .5, .45)
    mateo(c, "feliz", W / 2, 700, 1.3, T, "A08")
    rex(c, 760, 1180, .55, T, -10)
    k = pop(T, WT("A08", "perfecta.") - .2, .3)
    if k > 0: tiza(c, "¡PERFECTA!", 300, 360, int(96 * k), AMA, -8, f=D.F_ANTON, borde=True)
    return zoomcam(c, T, t0, 1.0, 1.08, 2.2, 640, 900)

def sc_decides(T):
    """'Treinta días. Y tú vas a decidir cada paso.': calendario + dos tarjetas que cambian la historia."""
    t0 = S("A09") - .2; c = pizarra(); d = ImageDraw.Draw(c)
    k = pop(T, t0 + .05, .3)
    if k > 0: D.calendario(d, W / 2, 520 + 6 * math.sin(T * 3), 2.4 * k, 30)
    cartas_ab(c, T, WT("A09", "tú") - .15)
    return zoomcam(c, T, t0, 1.0, 1.06, 2.5)

def sc_perfil(T):
    """'La serie nueva empieza hoy en @escribirconpinti…': perfil real con zoom a la portada del Día 1."""
    t0 = S("A10") - .15; c = pizarra()
    tz = WT("A10", "nueva") - .1; u = ease(u_(T, tz, 2.2))
    foco = ((1 - u) * 540 + u * (TILE1[0] + TILE1[2]) / 2, (1 - u) * 900 + u * (TILE1[1] + TILE1[3]) / 2)
    tb = WT("A10", "@escribirconpinti.") - .2
    telefono(c, T, .76, W / 2, 900 + 30 * (1 - ease(u_(T, t0, .4))), foco, 1 + 1.9 * u, pop(T, tb, .3))
    rotulo(c, "¡SERIE NUEVA!", W / 2, 205, 74, AMA, OL, -3, k=pop(T, tz, .3))
    if T >= tb: rotulo(c, "@escribirconpinti", W / 2, 305, 56, ROJO, CREMA, 2, f=D.F_BAL, k=pop(T, tb, .3))
    return c

def sc_buscanos(T):
    """'Búscanos y mira el día 1': cabecera real del perfil, Seguir latiendo y la portada del Día 1."""
    t0 = WT("A10", "Búscanos") - .15; c = pizarra()
    p = perfil(); head = p.crop((0, 150, 1079, 660)); sw = 940; s = sw / head.width
    head = head.resize((sw, int(head.height * s)), Image.BILINEAR)
    card = Image.new("RGBA", (sw + 30, head.height + 30), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 36, fill=(255, 255, 255, 255), outline=OL + (255,), width=6)
    m = Image.new("L", head.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, head.width - 1, head.height - 1), 30, fill=255)
    card.paste(head, (15, 15), m)
    k = pop(T, t0, .35); cy = 420
    if k > 0:
        sombra(c, (W / 2 - card.width / 2, cy - card.height / 2, W / 2 + card.width / 2, cy + card.height / 2), 36, 110, 18)
        paste_rot(c, card, W / 2, cy, k, -1.5 * k)
    if k >= .99:
        sx0 = W / 2 - card.width / 2 + 15 + SEGUIR[0] * s; sy0 = cy - card.height / 2 + 15 + (SEGUIR[1] - 150) * s
        sx1 = W / 2 - card.width / 2 + 15 + SEGUIR[2] * s; sy1 = cy - card.height / 2 + 15 + (SEGUIR[3] - 150) * s
        g = 8 + 8 * (.5 + .5 * math.sin(T * 10)); ImageDraw.Draw(c).rounded_rectangle((sx0 - g, sy0 - g, sx1 + g, sy1 + g), 60, outline=AMA, width=10)
    td = WT("A10", "día") - .2; kt = pop(T, td, .35)
    if kt > 0:   # portada real del Día 1 recortada de la captura
        tile = p.crop(TILE1); tile = tile.resize((int(tile.width * 1.05), int(tile.height * 1.05)), Image.BILINEAR)
        fr = Image.new("RGBA", (tile.width + 24, tile.height + 24), AMA + (255,)); fr.paste(tile, (12, 12))
        sombra(c, (W / 2 - fr.width / 2, 1010 - fr.height / 2, W / 2 + fr.width / 2, 1010 + fr.height / 2), 20, 110, 18)
        paste_rot(c, fr, W / 2, 1010, kt, 4 * kt)
        chispas(c, T, td + .2, W / 2, 1010, 330, 16, 7)
    return c

def sc_espero(T):
    """'¡Te espero allá! ¿Me ayudas?': Mateo tierno con Rex y el @ grande."""
    t0 = S("A11") - .15; c = pizarra()
    rotulo(c, "@escribirconpinti", W / 2, 330, 70, AMA, OL, -2, f=D.F_BAL, k=pop(T, t0, .3))
    mateo(c, "feliz", W / 2, 820, 1.25, T, "A11"); rex(c, 790, 1160, .5, T, -8)
    ta = WT("A11", "ayudas?") - .2
    if T >= ta:
        dd = ImageDraw.Draw(c)
        for i, (x, y) in enumerate(((170, 820), (910, 760), (230, 1120))):
            kk = pop(T, ta + i * .08, .3)
            if kk > 0: corazon(dd, x, y - 10 * math.sin(T * 5 + i), int(42 * kk), ROSA)
    return zoomcam(c, T, t0, 1.0, 1.1, 2.2, W / 2, 820)

SCENES = [(0, sc_nota), (WT("A01", "días") - .15, sc_plazo), (S("A02") - .15, sc_postre), (S("A03") - .15, sc_amigos),
          (S("A04") - .15, sc_decidido), (S("A05") - .2, sc_concentra), (WT("A05", "y") - .15, sc_raya), (S("A06") - .2, sc_listo),
          (S("A07") - .2, sc_era_raya), (S("A08") - .2, sc_rex), (S("A09") - .2, sc_decides), (S("A10") - .15, sc_perfil),
          (WT("A10", "Búscanos") - .15, sc_buscanos), (S("A11") - .15, sc_espero)]
IMPACTS = [WT("A01", "repite") - .1, WT("A07", "raya.") - .25, WT("A10", "@escribirconpinti.") - .2]

TW = .18
def frame(T):
    idx = max(i for i, (t, f) in enumerate(SCENES) if T >= t)
    t0, fn = SCENES[idx]; c = fn(T); u = (T - t0) / TW
    if idx > 0 and u < 1:                   # barrido rápido (nunca fundido a negro)
        e = ease(u); prev = SCENES[idx - 1][1](T); k = int(2 + 20 * math.sin(D.PI_ * u))
        cv = Image.new("RGBA", (W, H), PIZ2 + (255,))
        cv.alpha_composite(D.hblur(prev, k), (int(-W * e), 0)); cv.alpha_composite(D.hblur(c, k), (int(W * (1 - e)), 0)); c = cv
    amp = sum(14 * math.exp(-(T - ti) * 7) for ti in IMPACTS if 0 <= T - ti < .6)
    if amp > .6:
        zz = 1.035; cc = c.resize((int(W * zz), int(H * zz)), Image.BILINEAR)
        ox = (cc.width - W) / 2 + amp * math.sin(T * 95); oy = (cc.height - H) / 2 + amp * math.cos(T * 71)
        c = cc.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    D.draw_caption(c, T)
    return c.convert("RGB")

SFX = os.path.join(HERE, "..", "descargas", "mateo_sfx")
def sx(n): return os.path.join(SFX, n + ".mp3")
def video(out):
    mudo = os.path.join(TMP, "mudo.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", mudo], stdin=subprocess.PIPE)
    for f in range(int(round(TOTAL * FPS))): p.stdin.write(frame(f / FPS).tobytes())
    p.stdin.close(); p.wait()
    ins, flt = [], []
    for i, lid in enumerate(TL):
        ins += ["-i", os.path.join(R.VOZ, lid + ".wav")]; ms = max(0, int(TL[lid][0] * 1000))
        flt.append(f"[{i}:a]aresample=48000,afade=t=in:d=0.012,adelay={ms}|{ms},apad[a{i}]")
    n = len(TL)
    efx = [(sx("lapiz"), 0, -7), (sx("piano"), WT("A01", "repite") - .2, -12), (sx("brillo"), WT("A02", "postre?") - .2, -8),
           (sx("timbre"), WT("A03", "amigos.") - .3, -15), (sx("brillo"), WT("A04", "hoy") - .15, -9), (sx("rasgar"), WT("A04", "hoja.") - .25, -14),
           (sx("crayola"), WT("A05", "escribe…") - .1, -7), (sx("risa"), WT("A07", "raya.") - .1, -13), (sx("rugido"), S("A08") - .35, -18),
           (sx("brillo"), WT("A08", "perfecta.") - .2, -9), (sx("brillo"), WT("A09", "tú") - .15, -9),
           (sx("resultado"), WT("A10", "@escribirconpinti.") - .2, -10), (sx("brillo"), WT("A10", "día") - .2, -8),
           (sx("brillo"), WT("A11", "ayudas?") - .2, -9), (sx("musica"), 0, -16)]
    efx += [(sx("whoosh"), t - .05, -11) for t, f in SCENES[1:]]
    for j, (pth, t, db) in enumerate(efx):
        ins += ["-i", pth]; ms = max(0, int(t * 1000))
        flt.append(f"[{n + j}:a]aresample=48000,loudnorm=I=-25:TP=-6,aresample=48000,volume={db}dB,adelay={ms}|{ms},apad[s{j}]")
    flt.append("".join(f"[a{i}]" for i in range(n)) + "".join(f"[s{j}]" for j in range(len(efx))) +
               f"amix=inputs={n + len(efx)}:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},loudnorm=I=-15:TP=-1.5,aresample=48000[mx]")
    wav = os.path.join(TMP, "mezcla.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(flt), "-map", "[mx]", "-ac", "2", wav], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mudo, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "22",
                    "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-t", f"{TOTAL:.2f}", "-movflags", "+faststart", out], check=True)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "still":
        for t in sys.argv[2:]: frame(float(t)).save(os.path.join(TMP, f"f_{float(t):05.2f}.jpg"), quality=86)
    elif cmd == "info":
        print({k: [round(a, 2), round(b, 2)] for k, (a, b) in TL.items()}, round(TOTAL, 2), [round(t, 2) for t, f in SCENES])
    else: video(os.path.join(HERE, "mateo_30dias_aviso_cuenta_vieja.mp4"))
