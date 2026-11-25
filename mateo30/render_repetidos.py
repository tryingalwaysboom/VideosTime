"""Story: aclarar que NO son los mismos vídeos de la otra cuenta — historia nueva de 30 días, cada día un vídeo nuevo.
Uso: python3 render_repetidos.py still 1 5 | info | video"""
import os, sys, math, json, subprocess, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import render_d1 as D                       # utilidades de dibujo de la temporada
import importlib.util
from PIL import Image, ImageDraw, ImageFilter

os.environ["GUION"] = "guion_drepetidos"; os.environ["VOZDIR"] = os.path.join(HERE, "voz_drepetidos")
_spec = importlib.util.spec_from_file_location("R2", os.path.join(HERE, "..", "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
R.LAY = D.R.LAY
R.GAP.clear(); R.GAP.update({"R02": .3, "R03": .3, "R04": .35, "R05": .25})
R.TL, R.TOTAL = R.timeline()
R.TL = {k: (a - .1, b - .1) for k, (a, b) in R.TL.items()}; R.TOTAL = R.TL["R05"][1] + .1     # corte en seco
TL, TOTAL, S, E, WT = R.TL, R.TOTAL, R.S, R.E, R.WT
# subtítulos con el estilo de la temporada pero con los tiempos de esta story
D.LINEAS = R.LINEAS; _R = D.R; D.R = R; D.CH = D.chunks(); D.R = _R
CH = D.CH
W, H, FPS = D.W, D.H, D.FPS
ease, clamp, back, font = D.ease, D.clamp, D.back, D.font
pop, u_, pizarra, tiza, rotulo, lapiz_rojo, paste_rot, sombra = D.pop, D.u_, D.pizarra, D.tiza, D.rotulo, D.lapiz_rojo, D.paste_rot, D.sombra
OL, AMA, ROJO, CREMA, AZUL, TIZA, PIZ2 = D.OL, D.AMA, D.ROJO, D.CREMA, D.AZUL, D.TIZA, D.PIZ2
ROSA = (232, 85, 109)
TMP = os.path.join(HERE, "tmp_repetidos"); os.makedirs(TMP, exist_ok=True)
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

COMENT = Image.open(os.path.join(HERE, "story", "comentario_repetido_anon.jpg")).convert("RGBA")
MATEO_VIEJO = Image.open(os.path.join(HERE, "..", "mateo-pov", "layers", "mateo_feliz.png")).convert("RGBA")
TILE_OLD = (722, 1060, 1079, 1537)    # portada "Parte 29" de la serie anterior en la captura

def tarjeta(img, w, borde=CREMA):
    im = img.resize((w, int(img.height * w / img.width)), Image.BILINEAR)
    fr = Image.new("RGBA", (im.width + 20, im.height + 20), borde + (255,)); fr.paste(im, (10, 10)); return fr

def sc_repetidos(T):
    """'Mami… dicen que mis videos son repetidos…': el comentario real (sin nombre) y Mateo triste."""
    c = pizarra(); tr = WT("R01", "repetidos…") - .2
    mateo(c, "triste" if T < tr else "llora", W / 2, 900, 1.2, T, "R01")
    k = pop(T, .05, .35)
    if k > 0:
        card = tarjeta(COMENT, 920); sombra(c, (W / 2 - 470, 420 - 135, W / 2 + 470, 420 + 135), 20, 110, 16)
        paste_rot(c, card, W / 2, 420 + 6 * math.sin(T * 3), k, -2)
    if T >= tr: tiza(c, "¿REPETIDOS?", W / 2, 250, int(110 * pop(T, tr, .3)), ROJO, -3, f=D.F_ANTON, borde=True)
    if T < tr: return zoomcam(c, T, 0, 1.0, 1.05, 2.0, W / 2, 800)
    return zoomcam(c, T, tr, 1.06, 1.1, 2.0, W / 2, 700)

def sc_antes_ahora(T):
    """'No, mi amor. Esta es una historia nueva…': portada de la serie anterior vs la del Día 1."""
    t0 = S("R02") - .15; c = pizarra(); p = perfil()
    old = tarjeta(p.crop(TILE_OLD), 380, (150, 150, 160)); new = tarjeta(p.crop(TILE1), 380, AMA)
    ko = pop(T, t0 + .05, .3); kn = pop(T, WT("R02", "nueva:") - .25, .35)
    if ko > 0:
        g = old.copy(); g.alpha_composite(Image.new("RGBA", g.size, (20, 20, 30, 120)))
        paste_rot(c, g, 285, 820, ko, -4)
        rotulo(c, "ANTES", 285, 520, 60, (90, 90, 100), CREMA, -4, k=ko)
    if kn > 0:
        paste_rot(c, new, 795, 820, kn, 4); chispas(c, T, WT("R02", "nueva:") - .1, 795, 820, 330, 16, 6)
        rotulo(c, "SERIE NUEVA", 795, 520, 60, AMA, OL, 4, k=kn)
        tiza(c, "≠", W / 2, 820, int(170 * kn), CREMA, 0, f=D.F_ANTON, borde=True)
    rotulo(c, "¡NO SON LOS MISMOS!", W / 2, 1180, 64, ROJO, CREMA, -2, k=pop(T, t0 + .1, .3))
    return zoomcam(c, T, t0, 1.0, 1.05, 3.0, W / 2, 820)

def sc_cada_dia(T):
    """'…30 días, y cada día un video nuevo, hecho desde cero.': el calendario y los días que se van sumando."""
    t0 = WT("R02", "30") - .15; c = pizarra(); d = ImageDraw.Draw(c)
    k = pop(T, t0, .3)
    if k > 0: D.calendario(d, W / 2, 460, 2.0 * k, 30)
    tv = WT("R02", "video") - .2
    for i in range(10):    # fichas DÍA 1 … DÍA 10 que van entrando: un vídeo cada día
        kk = pop(T, tv + i * .09, .25)
        if kk <= 0: continue
        x = 150 + (i % 5) * 195; y = 860 + (i // 5) * 190
        d.rounded_rectangle((x - 80 * kk, y - 70 * kk, x + 80 * kk, y + 70 * kk), 18, fill=CREMA if i else AMA, outline=OL, width=6)
        d.text((x, y - 22 * kk), "DÍA", font=font(D.F_BAL, int(30 * kk)), fill=OL, anchor="mm")
        d.text((x, y + 22 * kk), str(i + 1), font=font(D.F_ANTON, int(56 * kk)), fill=ROJO, anchor="mm")
    tc = WT("R02", "cero.") - .3
    if T >= tc: rotulo(c, "HECHO DESDE CERO", W / 2, 1270, 62, AMA, OL, 3, k=pop(T, tc, .3))
    return zoomcam(c, T, t0, 1.0, 1.05, 3.0)

def sc_novedades(T):
    """'¡Nueva escuela, nueva bata… y letras nuevas!': la escuela, Mateo con su bata nueva y los imanes."""
    t0 = S("R03") - .15
    tb = WT("R03", "bata…") - .2; tl = WT("R03", "nuevas!") - .3
    if T < tb:
        c = D.bg("bg_escuela", T, t0, 1.0, 1.08, 3, .5, .55)
        rotulo(c, "NUEVA ESCUELA", W / 2, 300, 72, AMA, OL, -3, k=pop(T, WT("R03", "escuela,") - .2, .3))
        return c
    c = pizarra(); d = ImageDraw.Draw(c)
    paste_rot(c, MATEO_VIEJO, 230, 1050, .2, -6)                       # el Mateo de antes, pequeñito y tachado
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    dl.line((120, 870, 340, 1230), fill=ROJO + (230,), width=16); dl.line((340, 870, 120, 1230), fill=ROJO + (230,), width=16)
    c.alpha_composite(lay); tiza(c, "ANTES", 230, 820, 50, TIZA, -6, f=D.F_BAL, borde=True)
    mateo(c, "feliz", 680, 760, 1.05, T, "R03")
    if T < tl: rotulo(c, "¡NUEVA BATA!", 680, 330, 64, AMA, OL, 3, k=pop(T, tb, .3))
    if T >= tl:
        on = "".join(ch for i, ch in enumerate("MATEO") if T >= tl + i * .1)
        D.imanes(d, W / 2 - 2 * 126 * 1.05, 300, 1.05, T, on=on, t0=tl)
    return zoomcam(c, T, tb, 1.0, 1.05, 2.0, W / 2, 900)

def sc_manana(T):
    """'Si ya viste el día 1, cuéntanos en los comentarios qué quieres que pase mañana.'"""
    t0 = S("R04") - .15
    c, to = grid_view(T, t0, 1.0, pop(T, WT("R04", "1,") - .25, .3))
    a, b = to(178, 0); flecha(c, a, b - 20, T, pop(T, WT("R04", "1,") - .25, .3))
    tq = WT("R04", "comentarios") - .2
    if T < tq: rotulo(c, "DÍA 1 · YA EN EL PERFIL", W / 2, 230, 58, AMA, OL, -2, k=pop(T, t0, .3))
    else:
        rotulo(c, "¿QUÉ QUIERES QUE PASE MAÑANA?", W / 2, 230, 50, ROJO, CREMA, -2, k=pop(T, tq, .3))
        burbuja(c, 640, 650, 1.0, pop(T, tq + .1, .3))
    return zoomcam(c, T, t0, 1.0, 1.08, 4.0, 360, 860)

def sc_leo(T):
    """'¡Los leo todos!': Mateo feliz rodeado de comentarios y corazones."""
    t0 = S("R05") - .15; c = pizarra()
    for i, (x, y) in enumerate(((230, 520), (850, 640), (240, 1060), (860, 1180))):
        burbuja(c, x, y - 10 * math.sin(T * 4 + i), .75, pop(T, t0 + i * .1, .3))
    mateo(c, "feliz", W / 2, 840, 1.15, T, "R05")
    dd = ImageDraw.Draw(c)
    for i, (x, y) in enumerate(((540, 380), (420, 330), (660, 330))):
        kk = pop(T, t0 + .3 + i * .08, .3)
        if kk > 0: corazon(dd, x, y - 10 * math.sin(T * 5 + i), int(40 * kk), ROSA)
    return zoomcam(c, T, t0, 1.0, 1.08, 2.0, W / 2, 840)

SCENES = [(0, sc_repetidos), (S("R02") - .15, sc_antes_ahora), (WT("R02", "30") - .15, sc_cada_dia), (S("R03") - .15, sc_novedades),
          (WT("R03", "bata…") - .2, sc_novedades), (S("R04") - .15, sc_manana), (S("R05") - .15, sc_leo)]
IMPACTS = [WT("R02", "nueva:") - .25, WT("R04", "1,") - .25]

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
    efx = [(sx("teclea"), .05, -12), (sx("piano"), WT("R01", "repetidos…") - .2, -14), (sx("resultado"), WT("R02", "nueva:") - .25, -10),
           (sx("brillo"), WT("R02", "video") - .2, -10), (sx("brillo"), WT("R02", "cero.") - .3, -9), (sx("timbre"), WT("R03", "escuela,") - .3, -16),
           (sx("brillo"), WT("R03", "bata…") - .2, -9), (sx("brillo"), WT("R04", "1,") - .25, -9), (sx("teclea"), WT("R04", "comentarios") - .1, -13),
           (sx("brillo"), S("R05"), -10), (sx("musica"), 0, -17)]
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
    else: video(os.path.join(HERE, "story_mateo_no_son_repetidos.mp4"))
