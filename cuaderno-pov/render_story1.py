"""Story: aviso de la serie nueva "El cuaderno de la abuela" (Mateo y su mamá la presentan, Sofía saluda).
Uso: python3 render_story1.py still 1 5 | video"""
import os, sys, math, json, subprocess, random
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["GUION"] = "guion_story1"; os.environ["VOZDIR"] = os.path.join(HERE, "voz_story1")
sys.path.insert(0, HERE); sys.path.append(os.path.join(HERE, "..", "taller-pov"))
import importlib.util
_spec = importlib.util.spec_from_file_location("R", os.path.join(HERE, "..", "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
from PIL import Image, ImageDraw, ImageFilter
import render1 as P   # solo utilidades de dibujo (no tiempos)

R.LAY = os.path.join(HERE, "layers"); R.layer.cache_clear(); R.scaled.cache_clear()
TMP = os.path.join(HERE, "tmp_story1"); os.makedirs(TMP, exist_ok=True)
W, H, FPS = R.W, R.H, R.FPS
put, ease, clamp, back, font, mouth = R.put, R.ease, R.clamp, R.back, R.font, R.mouth
OL, YEL, WHITE, PI_ = R.OL, R.YEL, R.WHITE, math.pi
R.GAP.update({"F02": .2, "F03": .25, "F04": .25, "F05": .25, "F06": .2})
R.TL, R.TOTAL = R.timeline()
R.TL = {k: (a - .1, b - .1) for k, (a, b) in R.TL.items()}; R.TOTAL = R.TL["F06"][1] + .15
R.CH = R.chunks(); TL = R.TL; TOTAL = R.TOTAL; S, E, WT = R.S, R.E, R.WT
R.NOMBRE = {"K": "MATEO", "S": "SOFÍA"}; R.HIDE_LAST_CAPTION = False
def talk(l, T): return S(l) <= T < E(l)

def mateo(c, cx, cy, s, T, lid=None, kind="feliz"):
    hab = lid is not None and talk(lid, T)
    put(c, f"mateo_{kind}_hab" if hab else f"mateo_{kind}", cx, cy + 400 * s, s)
    if hab: mouth(c, cx, cy + 56 * s, T, True, int(26 * s))

def sofia(c, cx, cy, s, T, lid=None, kind="feliz", ola=False):
    hab = lid is not None and talk(lid, T)
    put(c, f"sofia_{kind}_hab" if hab else f"sofia_{kind}", cx, cy + 400 * s, s)
    if hab: mouth(c, cx, cy + 60 * s, T, True, int(24 * s))
    if ola:   # manita que saluda
        a = .5 * math.sin(T * 9); d = ImageDraw.Draw(c); x, y = cx + 300 * s, cy + 120 * s
        hx, hy = x + 140 * s * math.sin(a), y - 160 * s * math.cos(a)
        d.line((x, y, hx, hy), fill=(246, 201, 74), width=int(60 * s)); d.ellipse((hx - 46 * s, hy - 46 * s, hx + 46 * s, hy + 46 * s), fill=(243, 194, 155), outline=OL, width=5)

def rot(c, T, t0, txt, cx, cy, **k): P.rotulo(c, T, t0, txt, cx, cy, **k)

def bgz(n, T, t0, z0=1.0, z1=1.08): return R.bg(n, T, t0, z0, z1, 6).copy()

def cam(c, T, t0, shots, iv=1.9):
    k = int((T - t0) / iv); cx, cy, z = shots[k % len(shots)]; z *= 1 + .03 * (((T - t0) % iv) / iv)
    if z <= 1.001: return c
    hw, hh = W / (2 * z), H / (2 * z); cx = min(max(cx, hw), W - hw); cy = min(max(cy, hh), H - hh)
    return c.crop((int(cx - hw), int(cy - hh), int(cx + hw), int(cy + hh))).resize((W, H), Image.BICUBIC)

# ---------------------------------------------------------------- escenas
def sc_mateo(T):   # F01
    c = bgz("bg_cuarto_mateo", T, 0)
    mateo(c, 540, 820, 1.0, T, "F01", "travieso" if T < .8 else "feliz")
    return cam(c, T, 0, [(540, 760, 1.15), (540, 900, 1.0)], 1.3)

def sc_titulo(T):   # F02: ¡serie nueva! El cuaderno de la abuela
    t0 = S("F02") - .15; tn = WT("F02", "nueva!") - .2; tt = WT("F02", "cuaderno") - .2
    c = bgz("bg_desvan", T, t0, 1.2, 1.3).filter(ImageFilter.GaussianBlur(8)); R.dark(c, 90)
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((190, 500, 890, 1200), fill=(255, 200, 90, 150))
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(80)))
    k = back((T - t0) / .5); put(c, "cuaderno", 540, 860, .72 * max(k, .01), rot=-6 + 3 * math.sin(T * 2))
    P.brillos(c, T, t0, 540, 860, 340, (255, 230, 150), 14)
    if T >= tn: rot(c, T, tn, "¡SERIE NUEVA!", 540, 330, fill=(232, 85, 109), fg=WHITE, size=72, rot=-4)
    if T >= tt:
        u = back((T - tt) / .45); d = ImageDraw.Draw(c)
        for i, t in enumerate(("EL CUADERNO", "DE LA ABUELA")):
            d.text((540, 1250 + i * 110), t, font=font(R.F_ANTON, int(100 * max(u, .01))), fill=(255, 236, 200), anchor="mm", stroke_width=10, stroke_fill=OL)
    return cam(c, T, t0, [(540, 900, 1.0), (540, 860, 1.2)], 2.2)

def sc_sofia(T):   # F03
    t0 = S("F03") - .15
    c = bgz("bg_desvan", T, t0); P.polvo(c, T, 30, 2)
    put(c, "cuaderno", 830, 1180, .3, rot=10); P.brillos(c, T, t0, 830, 1180, 140, (255, 230, 150), 8)
    sofia(c, 470, 860, .98, T, "F03")
    if T >= WT("F03", "Sofía…") - .1: rot(c, T, WT("F03", "Sofía…") - .1, "SOFÍA, 5 AÑOS", 540, 330, size=50)
    if T >= WT("F03", "mágico.") - .2: rot(c, T, WT("F03", "mágico.") - .2, "UN CUADERNO MÁGICO", 540, 1250, fill=(255, 236, 200), size=50)
    return cam(c, T, t0, [(540, 860, 1.0), (470, 720, 1.35), (700, 1050, 1.3)], 1.6)

def sc_secreto(T):   # F04: letra -> mensaje secreto -> ustedes deciden
    t0 = S("F04") - .15; ts = WT("F04", "secreto…") - .2; td = WT("F04", "ustedes") - .2
    c = P.fondo_libro(T, t0)
    def izq(cc, x0, y0, s):
        P.s_punteada(cc, x0, y0, s)
        u = clamp((T - t0 - .2) / 1.6)
        P.trazo(cc, P.recorrido(P.s_path(x0 + 225 * s, y0 + 150 * s, 330 * s), u), 18 * s, P.ROSA)
    def der(cc, x0, y0, s):
        if T >= ts: P.manuscrito(cc, ["Si la escribes", "bien… te cuento", "un secreto."], T, ts, ts + 1.6, x0 + 225 * s, y0 + 120 * s, int(54 * s), P.TINTA, int(78 * s), 3)
    P.cuaderno_abierto(c, *P.CB, T, izq, der)
    if T >= ts: P.brillos(c, T, ts, 780, 700, 170, (200, 220, 255), 8)
    c = cam(c, T, t0, [(540, 800, 1.0), (300, 800, 1.5), (780, 760, 1.5)], 1.6)
    if T >= ts: rot(c, T, ts, "MENSAJE SECRETO", 540, 330, fill=P.ORO, size=52)
    if T >= td:   # mini tarjetas A / B: ustedes deciden
        for cx, l, col, t in ((330, "A", (96, 78, 200), td), (750, "B", (226, 76, 108), td + .25)):
            k = R.popscale(T, t, .35)
            if k <= 0: continue
            d = ImageDraw.Draw(c); r = 90 * k
            d.ellipse((cx - r, 1180 - r, cx + r, 1180 + r), fill=col, outline=WHITE, width=8)
            d.text((cx, 1180), l, font=font(R.F_ANTON, int(110 * k) + 1), fill=WHITE, anchor="mm")
        rot(c, T, td + .3, "¡USTEDES DECIDEN!", 540, 1320, size=54)
    return c

def corazon(d, cx, cy, r, col):
    d.ellipse((cx - r, cy - r * .8, cx, cy + r * .2), fill=col); d.ellipse((cx, cy - r * .8, cx + r, cy + r * .2), fill=col)
    d.polygon([(cx - r * .97, cy - r * .15), (cx + r * .97, cy - r * .15), (cx, cy + r)], fill=col)

def sc_voto(T):   # F05: Mateo ya votó
    t0 = S("F05") - .15; tv = WT("F05", "voté!") - .1
    c = bgz("bg_cuarto_mateo", T, t0, 1.05, 1.12)
    mateo(c, 540, 860, 1.0, T, "F05")
    if T >= tv:
        d = ImageDraw.Draw(c)
        for k in range(7):   # corazones que suben
            u = (T - tv) * .9 + k * .14; x = 300 + (k * 97) % 480 + 30 * math.sin(u * 5); y = 1250 - (u % 1) * 900
            corazon(d, x, y, 34 + 10 * (k % 3), (232, 85, 109))
        rot(c, T, tv, "¡YO YA VOTÉ!", 540, 330, size=58)
    if T >= WT("F05", "ti.") - .25: rot(c, T, WT("F05", "ti.") - .25, "¡TE TOCA A TI!", 540, 1260, fill=(232, 85, 109), fg=WHITE, size=60, rot=3)
    return cam(c, T, t0, [(540, 820, 1.1), (540, 720, 1.4)], 1.4)

_PORT = {}
def sc_perfil(T):   # F06: la parte 1 ya está en el perfil; vota en comentarios
    t0 = S("F06") - .15; tp = WT("F06", "perfil.") - .2; tc = WT("F06", "comentarios.") - .4
    c = bgz("bg_desvan", T, t0, 1.2, 1.28).filter(ImageFilter.GaussianBlur(10)); R.dark(c, 110)
    if "p" not in _PORT: _PORT["p"] = Image.open(os.path.join(HERE, "portada_cuaderno_parte1_9x16.jpg")).convert("RGBA").crop((0, 160, 1080, 1600)).resize((600, 800))
    k = back((T - t0) / .5); im = _PORT["p"].resize((max(1, int(600 * k)), max(1, int(800 * k))))
    fr = Image.new("RGBA", (im.width + 24, im.height + 24), (255, 255, 255, 255)); fr.alpha_composite(im, (12, 12))
    fr = fr.rotate(-3 + 2 * math.sin(T * 2), expand=True, resample=Image.BICUBIC)
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).rounded_rectangle((200, 420, 880, 1300), 40, fill=(255, 210, 120, int(130 + 60 * math.sin(T * 6))))
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(40)))
    c.alpha_composite(fr, (int(540 - fr.width / 2), int(860 - fr.height / 2)))
    if T >= tp:
        rot(c, T, tp, "YA EN EL PERFIL", 540, 330, fill=YEL, size=58)
        d = ImageDraw.Draw(c); bob = 14 * math.sin(T * 8)   # flecha que señala la portada
        d.polygon([(890, 560 + bob), (960, 480 + bob), (960, 530 + bob), (1040, 530 + bob), (1040, 590 + bob), (960, 590 + bob), (960, 640 + bob)], fill=YEL, outline=OL)
    if T >= tc:
        rot(c, T, tc, "VOTA EN COMENTARIOS", 540, 1340, fill=(232, 85, 109), fg=WHITE, size=56)
        d = ImageDraw.Draw(c); corazon(d, 540 + 330, 1335 - 6 * abs(math.sin(T * 7)), 30, (255, 255, 255))
    return c

SCENES = [(0, sc_mateo), (S("F02") - .15, sc_titulo), (S("F03") - .15, sc_sofia), (S("F04") - .15, sc_secreto),
          (S("F05") - .15, sc_voto), (S("F06") - .15, sc_perfil)]
TW = .22
def escena(i, T):
    P._OV.append(Image.new("RGBA", (W, H), (0, 0, 0, 0)))
    try:
        c = SCENES[i][1](T); c.alpha_composite(P._OV[-1])
    finally: P._OV.pop()
    return c

def frame(T):
    idx = max(i for i, (t, f) in enumerate(SCENES) if T >= t); t0 = SCENES[idx][0]
    c = escena(idx, T); u = (T - t0) / TW
    if idx > 0 and u < 1:
        e = ease(u); prev = escena(idx - 1, T); k = int(2 + 22 * math.sin(PI_ * u))
        cv = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        cv.alpha_composite(R.hblur(prev, k), (int(-W * e), 0)); cv.alpha_composite(R.hblur(c, k), (int(W * (1 - e)), 0)); c = cv
    c.alpha_composite(R.VIG); c.alpha_composite(R.grains()[int(T * 24) % 4])
    R.draw_caption(c, T)
    return c.convert("RGB")

def video(out):
    silent = os.path.join(TMP, "mudo.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
    for f in range(int(TOTAL * FPS)): p.stdin.write(frame(f / FPS).tobytes())
    p.stdin.close(); p.wait()
    m = lambda n: os.path.join(HERE, "..", "descargas", "mateo_sfx", n + ".mp3")
    ins, flt = [], []
    for i, lid in enumerate(TL):
        ins += ["-i", os.path.join(R.VOZ, lid + ".wav")]; ms = int(TL[lid][0] * 1000)
        flt.append(f"[{i}:a]aresample=48000,adelay={ms}|{ms},apad[a{i}]")
    n = len(TL)
    efx = [(m("brillo"), WT("F02", "nueva!") - .2, -5), (m("brillo"), WT("F03", "mágico.") - .2, -6), (m("brillo"), WT("F04", "secreto…") - .2, -6),
           (m("resultado"), WT("F05", "voté!") - .1, -8), (m("brillo"), WT("F06", "perfil.") - .2, -5)]
    efx += [(m("whoosh"), t - .05, -9) for t, f in SCENES[1:]]
    efx.append((m("musica"), 0, -8))
    for j, (pth, t, db) in enumerate(efx):
        ins += ["-i", pth]; ms = max(0, int(t * 1000))
        flt.append(f"[{n + j}:a]aresample=48000,loudnorm=I=-25:TP=-6,aresample=48000,volume={db}dB,adelay={ms}|{ms},apad[s{j}]")
    flt.append("".join(f"[a{i}]" for i in range(n)) + "".join(f"[s{j}]" for j in range(len(efx))) +
               f"amix=inputs={n + len(efx)}:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},loudnorm=I=-15:TP=-1.5,aresample=48000[mx]")
    wav = os.path.join(TMP, "mezcla.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(flt), "-map", "[mx]", "-ac", "2", wav], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "23",
                    "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-t", f"{TOTAL:.2f}", "-movflags", "+faststart", out], check=True)

if __name__ == "__main__":
    if sys.argv[1] == "still":
        for t in sys.argv[2:]: frame(float(t)).save(os.path.join(TMP, f"f_{float(t):05.2f}.jpg"), quality=86)
    elif sys.argv[1] == "info": print({k: [round(a, 2), round(b, 2)] for k, (a, b) in TL.items()}, round(TOTAL, 2))
    else: video(os.path.join(HERE, "story_cuaderno_nueva_serie.mp4"))
