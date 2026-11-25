"""Story: Mateo llora porque nadie comenta qué quiere que pase en el próximo episodio; señala el vídeo nuevo (Día 1).
Uso: python3 render_llora.py still 1 5 | info | video"""
import os, sys, math, json, subprocess, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import render_d1 as D                       # utilidades de dibujo de la temporada
import importlib.util
from PIL import Image, ImageDraw, ImageFilter

os.environ["GUION"] = "guion_dllora"; os.environ["VOZDIR"] = os.path.join(HERE, "voz_dllora")
_spec = importlib.util.spec_from_file_location("R2", os.path.join(HERE, "..", "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
R.LAY = D.R.LAY
R.GAP.clear(); R.GAP.update({"L02": .35, "L03": .3, "L04": .35, "L05": .3})
R.TL, R.TOTAL = R.timeline()
R.TL = {k: (a - .1, b - .1) for k, (a, b) in R.TL.items()}; R.TOTAL = R.TL["L05"][1] + .1     # corte en seco
TL, TOTAL, S, E, WT = R.TL, R.TOTAL, R.S, R.E, R.WT
# subtítulos con el estilo de la temporada pero con los tiempos de esta story
D.LINEAS = R.LINEAS; _R = D.R; D.R = R; D.CH = D.chunks(); D.R = _R
CH = D.CH
W, H, FPS = D.W, D.H, D.FPS
ease, clamp, back, font = D.ease, D.clamp, D.back, D.font
pop, u_, pizarra, tiza, rotulo, lapiz_rojo, paste_rot, sombra = D.pop, D.u_, D.pizarra, D.tiza, D.rotulo, D.lapiz_rojo, D.paste_rot, D.sombra
OL, AMA, ROJO, CREMA, AZUL, TIZA, PIZ2 = D.OL, D.AMA, D.ROJO, D.CREMA, D.AZUL, D.TIZA, D.PIZ2
ROSA = (232, 85, 109)
TMP = os.path.join(HERE, "tmp_llora"); os.makedirs(TMP, exist_ok=True)
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

DINO = Image.open(os.path.join(HERE, "..", "mateo-pov", "layers", "dino.png")).convert("RGBA")
def lagrimas(c, hx, hy, s, T):
    """Dos lagrimones que caen por las mejillas."""
    d = ImageDraw.Draw(c)
    for ex in (-75, 75):
        for i in range(2):
            ph = ((T * 1.3 + i * .5 + (ex > 0) * .25) % 1.0)
            x = hx + ex * s; y = hy + (20 + 160 * ph) * s; r = 13 * s * (1 - .3 * ph)
            d.ellipse((x - r, y - r * 1.4, x + r, y + r), fill=(140, 200, 245), outline=(70, 130, 200), width=3)

def sc_llora(T):
    """'Mami… nadie me dijo qué hago mañana.': Mateo llora (dos planos)."""
    c = pizarra(); tm = WT("L01", "mañana.") - .15
    mateo(c, "llora", W / 2, 760, 1.45, T, "L01"); lagrimas(c, W / 2, 760, 1.45, T)
    if T >= tm: tiza(c, "¿Y MAÑANA?", W / 2, 330, int(120 * pop(T, tm, .3)), AMA, -4, f=D.F_ANTON, borde=True)
    if T < tm - .3: return zoomcam(c, T, 0, 1.0, 1.06, 2.0, W / 2, 760)
    return zoomcam(c, T, tm - .3, 1.25, 1.32, 2.0, W / 2, 700)

def sc_video_nuevo(T):
    """'En el video nuevo, Mateo necesita saber qué quieres que pase…': el Día 1 en el perfil, con flecha y un comentario vacío."""
    t0 = S("L02") - .15
    c, to = grid_view(T, t0, 1.0, pop(T, WT("L02", "nuevo,") - .25, .3))
    a, b = to(178, 0); flecha(c, a, b - 20, T, pop(T, WT("L02", "nuevo,") - .25, .3))
    tq = WT("L02", "quieres") - .2
    if T < tq: rotulo(c, "VIDEO NUEVO", W / 2, 230, 70, AMA, OL, -3, k=pop(T, t0, .3))
    else:
        rotulo(c, "¿QUÉ QUIERES QUE PASE?", W / 2, 230, 58, ROJO, CREMA, -2, k=pop(T, tq, .3))
        k = pop(T, tq + .1, .3)
        if k > 0:   # globito de comentario vacío con puntos suspensivos que parpadean
            x, y = 640, 650; w, h = 320 * k, 130 * k; d = ImageDraw.Draw(c)
            d.rounded_rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), 30, fill=CREMA, outline=OL, width=6)
            d.polygon([(x - w * .25, y + h / 2 - 3), (x - w * .05, y + h / 2 - 3), (x - w * .3, y + h / 2 + 34 * k)], fill=CREMA, outline=OL)
            for i in range(3):
                on = int(T * 3) % 3 >= i
                d.ellipse((x - 70 + i * 70 - 16 * k, y - 16 * k, x - 70 + i * 70 + 16 * k, y + 16 * k), fill=OL if on else (200, 200, 215))
    return zoomcam(c, T, t0, 1.0, 1.08, 4.0, 360, 860)

def sc_mas_videos(T):
    """'Si nadie comenta… ¿ya no hay más videos?': Mateo llorando abrazado a Rex."""
    t0 = S("L03") - .15; c = pizarra()
    mateo(c, "llora", W / 2, 780, 1.3, T, "L03"); lagrimas(c, W / 2, 780, 1.3, T)
    paste_rot(c, DINO, 770, 1220 + 6 * math.sin(T * 3), .5, -10 + 4 * math.sin(T * 2.4))
    tv = WT("L03", "videos?") - .2
    if T >= tv: rotulo(c, "¿YA NO HAY MÁS VIDEOS?", W / 2, 300, 56, CREMA, OL, 3, k=pop(T, tv, .3))
    return zoomcam(c, T, t0, 1.1, 1.0, 2.5, W / 2, 800)

def sc_sin(T):
    """'Sin comentarios, no podemos seguir…': la pizarra se apaga y el calendario se queda en 30."""
    t0 = S("L04") - .15; c = pizarra(); d = ImageDraw.Draw(c)
    mateo(c, "triste", W / 2, 900, 1.15, T)
    k = pop(T, t0 + .05, .3)
    if k > 0: D.calendario(d, 200, 470, 1.4 * k, 30)
    tg = WT("L04", "gustando.") - .3
    if T >= WT("L04", "videos…") - .25:
        tiza(c, "SIN COMENTARIOS", 640, 380, int(70 * pop(T, WT("L04", "videos…") - .25, .3)), TIZA, -3, f=D.F_BAL, borde=True)
        tiza(c, "NO HAY DÍA 2", 640, 480, int(80 * pop(T, WT("L04", "videos…") - .1, .3)), ROJO, -3, f=D.F_ANTON, borde=True)
    oscurecer(c, (8, 12, 30), 90 * ease(u_(T, tg, 1.0)))
    return zoomcam(c, T, t0, 1.0, 1.1, 4.5, W / 2, 800)

def sc_porfavor(T):
    """'¿Me dejas un comentario? Por favor…': flecha al Día 1 y Mateo pidiéndolo con carita tímida."""
    t0 = S("L05") - .15
    c, to = grid_view(T, t0, 1.0, 1.0)
    a, b = to(178, 0); flecha(c, a, b - 20, T, 1.0)
    rotulo(c, "¡COMENTA EN EL DÍA 1!", W / 2, 230, 62, ROJO, CREMA, -2, k=pop(T, t0, .3))
    hab = talk("L05", T); hx, hy, s = 790, 1130, .85
    D.put(c, "cab_timido_hab" if hab else "cab_timido", hx, hy + 138 * s, s)
    if hab: D.mouth(c, hx, hy + 150 * s, T, True, int(22 * s))
    dd = ImageDraw.Draw(c)
    for i, (x, y) in enumerate(((620, 990), (950, 960))):
        kk = pop(T, WT("L05", "favor…") - .2 + i * .1, .3)
        if kk > 0: corazon(dd, x, y - 8 * math.sin(T * 5 + i), int(34 * kk), ROSA)
    return zoomcam(c, T, t0, 1.0, 1.06, 3.0, W / 2, 860)

SCENES = [(0, sc_llora), (S("L02") - .15, sc_video_nuevo), (S("L03") - .15, sc_mas_videos), (S("L04") - .15, sc_sin), (S("L05") - .15, sc_porfavor)]
IMPACTS = [WT("L02", "nuevo,") - .25, WT("L04", "videos…") - .1]

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
    efx = [(sx("piano"), 0, -14), (sx("brillo"), WT("L02", "nuevo,") - .25, -9), (sx("teclea"), WT("L02", "quieres") - .1, -13),
           (sx("reloj"), S("L04") - .1, -15), (sx("brillo"), S("L05"), -10), (sx("musica"), 0, -18)]
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
    else: video(os.path.join(HERE, "story_mateo_llora_comentarios.mp4"))
