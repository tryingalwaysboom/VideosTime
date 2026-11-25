"""Story explicativa: es una SERIE NUEVA (no el capítulo 1 de la anterior); la historia de Mateo sigue solo aquí, más divertida,
mejor hecha y sin relleno, paso a paso hasta que escriba su nombre completo solo. CTA: comentar en el Día 1 del perfil.
Uso: python3 render_explica.py still 1 5 | info | video"""
import os, sys, math, json, subprocess, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import render_d1 as D                       # utilidades de dibujo de la temporada
import importlib.util
from PIL import Image, ImageDraw, ImageFilter

os.environ["GUION"] = "guion_dexplica"; os.environ["VOZDIR"] = os.path.join(HERE, "voz_dexplica")
_spec = importlib.util.spec_from_file_location("R2", os.path.join(HERE, "..", "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
R.LAY = D.R.LAY
R.GAP.clear(); R.GAP.update({"Y02": .25, "X01": .3, "X02": .2, "Y03": .3, "X04": .15, "Y04": .35, "Y05": .25})
R.TL, R.TOTAL = R.timeline()
R.TL = {k: (a - .1, b - .1) for k, (a, b) in R.TL.items()}; R.TOTAL = R.TL["Y05"][1] + .1     # corte en seco
TL, TOTAL, S, E, WT = R.TL, R.TOTAL, R.S, R.E, R.WT
# subtítulos con el estilo de la temporada pero con los tiempos de esta story
D.LINEAS = R.LINEAS; _R = D.R; D.R = R; D.CH = D.chunks(); D.R = _R
CH = D.CH
W, H, FPS = D.W, D.H, D.FPS
ease, clamp, back, font = D.ease, D.clamp, D.back, D.font
pop, u_, pizarra, tiza, rotulo, lapiz_rojo, paste_rot, sombra = D.pop, D.u_, D.pizarra, D.tiza, D.rotulo, D.lapiz_rojo, D.paste_rot, D.sombra
OL, AMA, ROJO, CREMA, AZUL, TIZA, PIZ2 = D.OL, D.AMA, D.ROJO, D.CREMA, D.AZUL, D.TIZA, D.PIZ2
ROSA = (232, 85, 109)
TMP = os.path.join(HERE, "tmp_explica"); os.makedirs(TMP, exist_ok=True)
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
GRID = (0, 1060, 1079, 2013)        # cuadrícula de vídeos en la captura (fila 1: Día 1 | cuaderno tapado | Parte 29)
def grid_view(T, t0, dim_old=0.0, glow=0.0):
    """Cuadrícula real del perfil: las portadas de la serie anterior se apagan y la del Día 1 se ilumina."""
    p = perfil().crop(GRID).copy(); pw, ph = p.size
    if dim_old > 0:
        lay = Image.new("RGBA", p.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        for (x0, y0, x1, y1) in ((361, 0, 718, 477), (722, 0, 1079, 477), (0, 481, 357, 953), (361, 481, 718, 953), (722, 481, 1079, 953)):
            dl.rectangle((x0, y0, x1, y1), fill=(10, 14, 30, int(170 * dim_old)))
        p.alpha_composite(lay)
    sc = 1000 / pw; im = p.resize((1000, int(ph * sc)), Image.BILINEAR)
    c = pizarra(); cy = 900
    sombra(c, (40, cy - im.height / 2, 1040, cy + im.height / 2), 30, 110, 18)
    c.alpha_composite(im, (40, int(cy - im.height / 2)))
    to = lambda x, y: (40 + x * sc, cy - im.height / 2 + y * sc)
    if glow > 0:
        a, b = to(0, 0); a2, b2 = to(357, 477)
        g = 10 + 6 * math.sin(T * 9); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        for i in range(4): dl.rounded_rectangle((a - g - i * 7, b - g - i * 7, a2 + g + i * 7, b2 + g + i * 7), 20, outline=AMA + (int(255 * glow * (1 - i * .23)),), width=9)
        c.alpha_composite(lay)
    return c, to

def flecha(c, x, y, T, k=1.0, rot=0):
    """Flecha amarilla que señala hacia abajo y bota."""
    if k <= 0: return
    b = 18 * math.sin(T * 8); s = k
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    pts = [(x - 45 * s, y - 170 * s + b), (x + 45 * s, y - 170 * s + b), (x + 45 * s, y - 70 * s + b), (x + 95 * s, y - 70 * s + b), (x, y + b), (x - 95 * s, y - 70 * s + b), (x - 45 * s, y - 70 * s + b)]
    d.polygon(pts, fill=AMA, outline=OL); d.line(pts + [pts[0]], fill=OL, width=8)
    if rot: lay = lay.rotate(rot, center=(x, y), resample=Image.BICUBIC)
    c.alpha_composite(lay)

def burbuja(c, x, y, s, k):
    if k <= 0: return
    w, h = 300 * s * k, 120 * s * k; d = ImageDraw.Draw(c)
    d.rounded_rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), 28 * s, fill=CREMA, outline=OL, width=6)
    d.polygon([(x - w * .25, y + h / 2 - 3), (x - w * .05, y + h / 2 - 3), (x - w * .3, y + h / 2 + 34 * s * k)], fill=CREMA, outline=OL)
    corazon(d, x - w / 2 + 50 * s * k, y, 22 * s * k, ROSA)
    for i in range(2):
        yy = y - h * .18 + i * h * .36; d.rounded_rectangle((x - w / 2 + 92 * s * k, yy - 8 * s, x + w / 2 - (40 + 60 * i) * s * k, yy + 8 * s), 8, fill=(200, 200, 215))

def check(c, txt, y, T, t0):
    k = pop(T, t0, .3)
    if k <= 0: return
    d = ImageDraw.Draw(c); x = 170
    d.rounded_rectangle((x - 58 * k, y - 58 * k, x + 58 * k, y + 58 * k), 18, fill=CREMA, outline=OL, width=6)
    u = u_(T, t0 + .1, .25)
    if u > 0:
        p1, p2, p3 = (x - 30, y), (x - 8, y + 26), (x + 34, y - 30)
        pts = [p1, (p1[0] + (p2[0] - p1[0]) * min(1, u * 2), p1[1] + (p2[1] - p1[1]) * min(1, u * 2))]
        if u > .5: pts.append((p2[0] + (p3[0] - p2[0]) * (u - .5) * 2, p2[1] + (p3[1] - p2[1]) * (u - .5) * 2))
        d.line(pts, fill=(60, 170, 90), width=16, joint="curve")
    tiza(c, txt, 260, y, int(96 * k), TIZA, 0, f=D.F_BAL, anchor="lm")

def sc_ojo(T):
    """'¡Ojo! Esto no es otro capítulo de la serie de antes: es una serie nueva.'"""
    tn = WT("Y01", "serie", 2) - .15
    c, to = grid_view(T, 0, ease(u_(T, WT("Y01", "antes:") - .3, .4)), pop(T, tn, .3))
    rotulo(c, "¡OJO!", W / 2, 230, 96, ROJO, CREMA, -4, k=pop(T, 0, .25))
    if T >= WT("Y01", "antes:") - .3:
        a, b = to(540, 240); kx = pop(T, WT("Y01", "antes:") - .3, .3)
        rotulo(c, "SERIE ANTERIOR", 720, 700, int(48 * kx) or 1, (60, 60, 70), CREMA, 4, k=kx)
    if T >= tn:
        a, b = to(178, 0); rotulo(c, "¡SERIE NUEVA!", 300, 360, 60, AMA, OL, -4, k=pop(T, tn, .3))
        chispas(c, T, tn, 218, 700, 300, 16, 3)
    return zoomcam(c, T, 0, 1.0, 1.06, 5.0, W / 2, 800)

def sc_empieza(T):
    """'¡Mi historia empieza otra vez!': Mateo feliz con el calendario DÍA 1."""
    t0 = S("Y02") - .15; c = pizarra(); d = ImageDraw.Draw(c)
    jump = 28 * abs(math.sin((T - t0) * 7)) * (1 - u_(T, t0, 1.2))
    mateo(c, "feliz", W / 2, 820 - jump, 1.3, T, "Y02")
    k = pop(T, t0 + .1, .3)
    if k > 0:
        x, y, s = 200, 440, 1.5 * k
        d.rounded_rectangle((x - 75 * s, y - 84 * s, x + 75 * s, y + 84 * s), 20 * s, fill=CREMA, outline=OL, width=6)
        d.rounded_rectangle((x - 75 * s, y - 84 * s, x + 75 * s, y - 34 * s), 20 * s, fill=ROJO, outline=OL, width=6)
        d.text((x, y - 58 * s), "DÍA", font=font(D.F_BAL, int(32 * s)), fill=CREMA, anchor="mm")
        d.text((x, y + 22 * s), "1", font=font(D.F_ANTON, int(96 * s)), fill=OL, anchor="mm")
    return zoomcam(c, T, t0, 1.0, 1.08, 2.0, W / 2, 820)

def sc_una(T):
    """'A partir de hoy, en esta cuenta solo habrá una historia.'"""
    t0 = S("X01") - .15; c = pizarra()
    k = pop(T, WT("X01", "solo") - .2, .3)
    if k > 0: tiza(c, "1", W / 2, 760, int(560 * k), AMA, -4, f=D.F_ANTON, borde=True)
    rotulo(c, "SOLO UNA HISTORIA", W / 2, 1140, 64, CREMA, OL, 2, k=pop(T, WT("X01", "historia.") - .25, .3))
    rotulo(c, "DESDE HOY", W / 2, 330, 70, ROJO, CREMA, -3, k=pop(T, t0 + .1, .3))
    return zoomcam(c, T, t0, 1.0, 1.06, 3.0)

def sc_mia(T):
    """'¡La mía!': Mateo se señala, orgulloso."""
    t0 = S("X02") - .12; c = pizarra()
    mateo(c, "travieso", W / 2, 760, 1.55, T, "X02")
    chispas(c, T, t0 + .1, W / 2, 700, 420, 18, 9)
    return zoomcam(c, T, t0, 1.12, 1.0, .5, W / 2, 760)

def sc_promesa(T):
    """'Más divertida, mejor hecha y sin relleno. Paso a paso…'"""
    t0 = S("Y03") - .15; c = pizarra(); d = ImageDraw.Draw(c)
    rotulo(c, "LA SERIE NUEVA", W / 2, 300, 70, AMA, OL, -2, k=pop(T, t0, .3))
    check(c, "Más divertida", 560, T, WT("Y03", "divertida,") - .3)
    check(c, "Mejor hecha", 740, T, WT("Y03", "hecha,") - .3)
    check(c, "Sin relleno", 920, T, WT("Y03", "relleno.") - .3)
    tp = WT("Y03", "Paso") - .15
    if T >= tp: D.imanes(d, W / 2 - 2 * 126 * 1.2, 1140, 1.2, T, on="", t0=tp)
    return zoomcam(c, T, t0, 1.0, 1.05, 4.0)

def sc_solito(T):
    """'…hasta que escriba mi nombre completo, yo solito!': los imanes M-A-T-E-O se encienden uno a uno."""
    t0 = S("X04") - .1; c = pizarra(); d = ImageDraw.Draw(c)
    mateo(c, "feliz", W / 2, 900, 1.2, T, "X04")
    tl = WT("X04", "nombre") - .15
    on = "".join(ch for i, ch in enumerate("MATEO") if T >= tl + i * .2)
    D.imanes(d, W / 2 - 2 * 126 * 1.3, 360, 1.3, T, on=on)
    if len(on) == 5: chispas(c, T, tl + 1.0, W / 2, 360, 460, 20, 4)
    if T >= WT("X04", "solito!") - .2: rotulo(c, "¡YO SOLITO!", W / 2, 560, 70, AMA, OL, 3, k=pop(T, WT("X04", "solito!") - .2, .3))
    return zoomcam(c, T, t0, 1.0, 1.06, 3.0, W / 2, 800)

def sc_comenta(T):
    """'El día 1 ya está en el perfil. Entra y déjale un comentario.': flecha a la portada del Día 1."""
    t0 = S("Y04") - .15
    c, to = grid_view(T, t0, 1.0, pop(T, WT("Y04", "perfil.") - .25, .3))
    tc = WT("Y04", "comentario.") - .3
    if T < tc: rotulo(c, "DÍA 1 · YA EN EL PERFIL", W / 2, 230, 58, AMA, OL, -2, k=pop(T, t0, .3))
    a, b = to(178, 0); flecha(c, a, b - 20, T, pop(T, WT("Y04", "perfil.") - .25, .3))
    tc = WT("Y04", "comentario.") - .3
    if T >= tc:
        rotulo(c, "¡DÉJALE UN COMENTARIO!", W / 2, 230, 58, ROJO, CREMA, -2, k=pop(T, tc, .3))
        burbuja(c, 620, 640, 1.0, pop(T, tc + .1, .3))
    return zoomcam(c, T, t0, 1.0, 1.1, 4.0, 360, 860)

def sc_leo(T):
    """'¡Los leo todos!': Mateo feliz rodeado de comentarios y corazones."""
    t0 = S("Y05") - .15; c = pizarra()
    for i, (x, y) in enumerate(((230, 520), (850, 640), (240, 1060), (860, 1180))):
        burbuja(c, x, y - 10 * math.sin(T * 4 + i), .75, pop(T, t0 + i * .1, .3))
    mateo(c, "feliz", W / 2, 840, 1.15, T, "Y05")
    dd = ImageDraw.Draw(c)
    for i, (x, y) in enumerate(((540, 380), (420, 330), (660, 330))):
        kk = pop(T, t0 + .3 + i * .08, .3)
        if kk > 0: corazon(dd, x, y - 10 * math.sin(T * 5 + i), int(40 * kk), ROSA)
    return zoomcam(c, T, t0, 1.0, 1.08, 2.0, W / 2, 840)

SCENES = [(0, sc_ojo), (S("Y02") - .15, sc_empieza), (S("X01") - .15, sc_una), (S("X02") - .12, sc_mia), (S("Y03") - .15, sc_promesa),
          (S("X04") - .1, sc_solito), (S("Y04") - .15, sc_comenta), (S("Y05") - .15, sc_leo)]
IMPACTS = [WT("Y01", "serie", 2) - .15, WT("X01", "solo") - .2, WT("Y04", "perfil.") - .25]

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
    efx = [(sx("timbre"), 0, -15), (sx("resultado"), WT("Y01", "serie", 2) - .15, -10), (sx("brillo"), S("Y02"), -10),
           (sx("brillo"), WT("X01", "solo") - .2, -8), (sx("lapiz"), WT("Y03", "divertida,") - .2, -10), (sx("lapiz"), WT("Y03", "hecha,") - .2, -10),
           (sx("lapiz"), WT("Y03", "relleno.") - .2, -10), (sx("brillo"), WT("X04", "solito!") - .2, -8),
           (sx("brillo"), WT("Y04", "perfil.") - .25, -8), (sx("teclea"), WT("Y04", "comentario.") - .2, -12), (sx("brillo"), S("Y05"), -9),
           (sx("musica"), 0, -16)]
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
    else: video(os.path.join(HERE, "story_mateo_30dias_que_cambia.mp4"))
