"""Story de aviso: empieza la serie nueva "Mateo: 30 días para no repetir" en @escribirconpinti.
Usa el mundo visual de la temporada (pizarra verde, tiza, rojo de corrección, bata azul) y la captura real del perfil.
Uso: python3 render_story.py still 1 5 | info | video"""
import os, sys, math, json, subprocess, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import render_d1 as D                       # utilidades de dibujo de la temporada
import importlib.util
from PIL import Image, ImageDraw, ImageFilter

os.environ["GUION"] = "guion_dstory"; os.environ["VOZDIR"] = os.path.join(HERE, "voz_dstory")
_spec = importlib.util.spec_from_file_location("R2", os.path.join(HERE, "..", "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
R.LAY = D.R.LAY
R.GAP.clear(); R.GAP.update({"F02": .35, "F03": .3, "F04": .3})
R.TL, R.TOTAL = R.timeline()
R.TL = {k: (a - .1, b - .1) for k, (a, b) in R.TL.items()}; R.TOTAL = R.TL["F04"][1] + .1     # corte en seco
TL, TOTAL, S, E, WT = R.TL, R.TOTAL, R.S, R.E, R.WT
# subtítulos con el estilo de la temporada pero con los tiempos de esta story
D.LINEAS = R.LINEAS; _R = D.R; D.R = R; D.CH = D.chunks(); D.R = _R
CH = D.CH
W, H, FPS = D.W, D.H, D.FPS
ease, clamp, back, font = D.ease, D.clamp, D.back, D.font
pop, u_, pizarra, tiza, rotulo, lapiz_rojo, paste_rot, sombra = D.pop, D.u_, D.pizarra, D.tiza, D.rotulo, D.lapiz_rojo, D.paste_rot, D.sombra
OL, AMA, ROJO, CREMA, AZUL, TIZA, PIZ2 = D.OL, D.AMA, D.ROJO, D.CREMA, D.AZUL, D.TIZA, D.PIZ2
ROSA = (232, 85, 109)
TMP = os.path.join(HERE, "tmp_story"); os.makedirs(TMP, exist_ok=True)
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
def sc_nota(T):
    """0 s: la nota enorme con REPITE ya rodeado en rojo (impacto desde el fotograma 0)."""
    c = pizarra(); u = ease(T / .45); z = 1.18 - .14 * u + .03 * T
    cx, cy = W / 2, 820 + 40 * (1 - u); rot = -7 + 4 * u
    nb = D.nota_img(); sombra(c, (cx - 440 * z, cy - 560 * z, cx + 440 * z, cy + 560 * z), 24, 110, 22)
    paste_rot(c, nb, cx, cy, z, rot)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); x0, y0, x1, y1 = D.NOTA_REPITE
    caja = (cx + x0 * z, cy + y0 * z, cx + x1 * z, cy + y1 * z)
    lapiz_rojo(lay, caja, .35 + .65 * u_(T, 0, .4), 15)
    c.alpha_composite(lay.rotate(rot, center=(cx, cy), resample=Image.BICUBIC))
    return c

def sc_mateo_miedo(T):
    """Mateo, preocupado, lo pregunta. Al decir 'repito' la palabra REPITE sale en tiza roja."""
    t0 = WT("F01", "dice") - .15; c = pizarra()
    tr = WT("F01", "repito") - .15
    kind = "susto" if T >= tr else "timido"
    mateo(c, kind, W / 2, 760, 1.5, T, "F01")
    k = pop(T, tr, .3)
    if k > 0: tiza(c, "¿REPITE?", W / 2, 400, int(150 * k), ROJO, -4, f=D.F_ANTON, borde=True)
    tn = WT("F01", "nombre…") - .1                       # cambio de plano a mitad de la frase
    if T < tn: return zoomcam(c, T, t0, 1.0, 1.1, 2.0, W / 2, 760)
    return zoomcam(c, T, tn, 1.28, 1.36, 2.0, W / 2, 700)

def sc_calendario(T):
    """'Tenemos treinta días': el calendario FALTAN 30 DÍAS enorme."""
    t0 = S("F02") - .15; c = pizarra(); d = ImageDraw.Draw(c)
    k = pop(T, t0 + .05, .35); s = 3.6 * k
    if s > .05:
        sombra(c, (W / 2 - 75 * s, 760 - 84 * s, W / 2 + 75 * s, 760 + 84 * s), 40, 100, 18)
        D.calendario(d, W / 2, 760 + 8 * math.sin(T * 3), s, 30)
    tm = WT("F02", "amor.") - .2
    if T >= tm: rotulo(c, "30 DÍAS PARA ESCRIBIR SU NOMBRE", W / 2, 330, 44, CREMA, OL, -2, k=pop(T, tm, .3))
    return zoomcam(c, T, t0, 1.0, 1.06, 2.0)

def sc_lograr(T):
    """'Y lo vamos a lograr': los imanes M-A-T-E-O se encienden uno a uno sobre Mateo feliz."""
    t0 = WT("F02", "Y") - .15; c = pizarra(); d = ImageDraw.Draw(c)
    mateo(c, "feliz", W / 2, 860, 1.32, T)
    tl = WT("F02", "lograr.") - .35
    on = "".join(ch for i, ch in enumerate("MATEO") if T >= tl + i * .12)
    D.imanes(d, W / 2 - 2 * 126 * 1.25, 360, 1.25, T, on=on, t0=t0)
    chispas(c, T, tl + .5, W / 2, 360, 420)
    return zoomcam(c, T, t0, 1.04, 1.0, 1.6)

def sc_perfil(T):
    """'Hoy empieza nuestra serie nueva…': el perfil real y zoom lento hasta la portada del Día 1."""
    t0 = S("F03") - .15; c = pizarra()
    tz = WT("F03", "serie") - .1; u = ease(u_(T, tz, 2.6))
    foco = ((1 - u) * 540 + u * (TILE1[0] + TILE1[2]) / 2, (1 - u) * 900 + u * (TILE1[1] + TILE1[3]) / 2)
    tb = WT("F03", "Mateo,") - .15
    to_scr = telefono(c, T, .76, W / 2, 900 + 30 * (1 - ease(u_(T, t0, .4))), foco, 1 + 1.9 * u, pop(T, tb, .3))
    rotulo(c, "¡SERIE NUEVA!", W / 2, 205, 74, AMA, OL, -3, k=pop(T, tz, .3))
    if T >= tb:
        a, b = to_scr(TILE1[0], TILE1[3]); a2, _ = to_scr(TILE1[2], TILE1[3])
        rotulo(c, "DÍA 1 · EMPIEZA HOY", W / 2, 300, 50, ROJO, CREMA, 2, k=pop(T, tb + .15, .3))
        chispas(c, T, tb, (a + a2) / 2, b - 260, 380, 18, 5)
    return c

def sc_arroba(T):
    """'¡Búscame en @escribirconpinti…!': cabecera real del perfil + @ enorme, Seguir latiendo, Mateo feliz."""
    t0 = S("F04") - .15; c = pizarra()
    p = perfil(); head = p.crop((0, 150, 1079, 660)); sw = 940; s = sw / head.width
    head = head.resize((sw, int(head.height * s)), Image.BILINEAR)
    card = Image.new("RGBA", (sw + 30, head.height + 30), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 36, fill=(255, 255, 255, 255), outline=OL + (255,), width=6)
    m = Image.new("L", head.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, head.width - 1, head.height - 1), 30, fill=255)
    card.paste(head, (15, 15), m)
    k = pop(T, t0, .35); cy = 470
    if k > 0:
        sombra(c, (W / 2 - card.width / 2, cy - card.height / 2, W / 2 + card.width / 2, cy + card.height / 2), 36, 110, 18)
        paste_rot(c, card, W / 2, cy, k, -1.5 * k)
    # anillo que late sobre "Seguir"
    sx0 = W / 2 - card.width / 2 + 15 + SEGUIR[0] * s; sy0 = cy - card.height / 2 + 15 + (SEGUIR[1] - 150) * s
    sx1 = W / 2 - card.width / 2 + 15 + SEGUIR[2] * s; sy1 = cy - card.height / 2 + 15 + (SEGUIR[3] - 150) * s
    ta = WT("F04", "@escribirconpinti,") - .2
    if T >= ta and k >= .99:
        g = 8 + 8 * (.5 + .5 * math.sin(T * 10)); d = ImageDraw.Draw(c)
        d.rounded_rectangle((sx0 - g, sy0 - g, sx1 + g, sy1 + g), 60, outline=AMA, width=10)
    # @ enorme en tiza amarilla
    ka = pop(T, ta, .3)
    if ka > 0:
        rotulo(c, "@escribirconpinti", W / 2, 790, int(82 * ka), AMA, OL, -2, f=D.F_BAL)
    mateo(c, "feliz", W / 2, 1150, .95, T, "F04")
    td = WT("F04", "día") - .15
    if T >= td:
        dd = ImageDraw.Draw(c)
        for i, (x, y) in enumerate(((170, 1060), (910, 1000), (250, 1250), (840, 1230))):
            kk = pop(T, td + i * .08, .3)
            if kk > 0: corazon(dd, x, y - 10 * math.sin(T * 5 + i), int(40 * kk), ROSA)
    tc = WT("F04", "acompáñame") - .1
    if T < tc: return zoomcam(c, T, t0, 1.0, 1.04, 2.5, W / 2, 700)
    return zoomcam(c, T, tc, 1.12, 1.18, 2.5, W / 2, 1000)

SCENES = [(0, sc_nota), (WT("F01", "dice") - .15, sc_mateo_miedo), (S("F02") - .15, sc_calendario),
          (WT("F02", "Y") - .15, sc_lograr), (S("F03") - .15, sc_perfil), (S("F04") - .15, sc_arroba)]
IMPACTS = [WT("F01", "repito") - .1, WT("F03", "Mateo,") - .1, WT("F04", "@escribirconpinti,") - .15]

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
    efx = [(sx("lapiz"), 0, -7), (sx("whoosh"), WT("F01", "dice") - .2, -10), (sx("piano"), WT("F01", "repito") - .2, -12),
           (sx("whoosh"), S("F02") - .2, -10), (sx("brillo"), WT("F02", "lograr.") - .35, -8), (sx("whoosh"), S("F03") - .2, -10),
           (sx("resultado"), WT("F03", "Mateo,") - .15, -10), (sx("whoosh"), S("F04") - .2, -10), (sx("brillo"), WT("F04", "@escribirconpinti,") - .2, -8),
           (sx("brillo"), WT("F04", "día") - .15, -9), (sx("musica"), 0, -16)]
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
    else: video(os.path.join(HERE, "story_mateo_30dias_nueva_serie.mp4"))
