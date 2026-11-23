"""Story (único): Mateo NO termina + serie nueva "El cuaderno de la abuela". (Basado en story 1: "El cuaderno de la abuela" (Mateo y su mamá la presentan, Sofía saluda).
Uso: python3 render_story1.py still 1 5 | video"""
import os, sys, math, json, subprocess, random
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["GUION"] = "guion_story3"; os.environ["VOZDIR"] = os.path.join(HERE, "voz_story3")
sys.path.insert(0, HERE); sys.path.append(os.path.join(HERE, "..", "taller-pov"))
import importlib.util
_spec = importlib.util.spec_from_file_location("R", os.path.join(HERE, "..", "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
from PIL import Image, ImageDraw, ImageFilter
import render1 as P   # solo utilidades de dibujo (no tiempos)

R.LAY = os.path.join(HERE, "layers"); R.layer.cache_clear(); R.scaled.cache_clear()
TMP = os.path.join(HERE, "tmp_story3"); os.makedirs(TMP, exist_ok=True)
W, H, FPS = R.W, R.H, R.FPS
put, ease, clamp, back, font, mouth = R.put, R.ease, R.clamp, R.back, R.font, R.mouth
OL, YEL, WHITE, PI_ = R.OL, R.YEL, R.WHITE, math.pi
R.GAP.update({"F02": .15, "F03": .2, "F04": .2, "F05": .2})
R.TL, R.TOTAL = R.timeline()
R.TL = {k: (a - .1, b - .1) for k, (a, b) in R.TL.items()}; R.TOTAL = R.TL["F05"][1] + .15
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
def corazon(d, cx, cy, r, col):
    d.ellipse((cx - r, cy - r * .8, cx, cy + r * .2), fill=col); d.ellipse((cx, cy - r * .8, cx + r, cy + r * .2), fill=col)
    d.polygon([(cx - r * .97, cy - r * .15), (cx + r * .97, cy - r * .15), (cx, cy + r)], fill=col)

_IMG = {}
def portada(nombre, w):
    k = (nombre, w)
    if k not in _IMG:
        f = os.path.join(HERE, "..", "mateo-pov", "portada_cuaderno_parte15_9x16.jpg") if nombre == "mateo" else os.path.join(HERE, "portada_cuaderno_parte1_9x16.jpg")
        im = Image.open(f).convert("RGBA"); top = 160 if nombre == "mateo" else 250
        im = im.crop((0, top, 1080, top + 1440)).resize((w, int(w * 4 / 3)))
        fr = Image.new("RGBA", (im.width + 20, im.height + 20), (255, 255, 255, 255)); fr.alpha_composite(im, (10, 10)); _IMG[k] = fr
    return _IMG[k]

def dos_portadas(c, T, t0, y=860, w=420):
    for i, (n, cx, r) in enumerate((("mateo", 290, -4), ("cuaderno", 790, 4))):
        k = back((T - t0 - i * .25) / .45)
        if k <= 0: continue
        im = portada(n, w); im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k)))).rotate(r + 1.5 * math.sin(T * 3 + i), expand=True, resample=Image.BICUBIC)
        c.alpha_composite(im, (int(cx - im.width / 2), int(y - im.height / 2)))

def sc_preocupado(T):   # F01
    c = bgz("bg_cuarto_mateo", T, 0)
    mateo(c, 540, 820, 1.0, T, "F01", "triste")
    return cam(c, T, 0, [(540, 760, 1.2), (540, 900, 1.0)], 1.3)

def sc_sigue(T):   # F02: ¡tu historia sigue!
    t0 = S("F02") - .15
    c = bgz("bg_cuarto_mateo", T, t0, 1.05, 1.1)
    mateo(c, 540, 860, 1.0, T, None, "feliz"); P.confeti(c, T, WT("F02", "sigue,") - .1)
    rot(c, T, t0 + .1, "¡NOOO!", 540, 330, fill=(232, 85, 109), fg=WHITE, size=70)
    if T >= WT("F02", "sigue,") - .15: rot(c, T, WT("F02", "sigue,") - .15, "¡TU HISTORIA SIGUE!", 540, 1260, size=58, rot=3)
    return cam(c, T, t0, [(540, 820, 1.0), (540, 700, 1.35)], 1.4)

def sc_dos(T):   # F03: ahora tenemos dos series
    t0 = S("F03") - .15
    c = bgz("bg_desvan", T, t0, 1.2, 1.28).filter(ImageFilter.GaussianBlur(10)); R.dark(c, 110)
    dos_portadas(c, T, t0 + .1)
    if T >= WT("F03", "dos") - .2: rot(c, T, WT("F03", "dos") - .2, "¡2 SERIES!", 540, 330, fill=YEL, size=72)
    if T >= WT("F03", "Mateo…") - .2: rot(c, T, WT("F03", "Mateo…") - .2, "MATEO", 290, 1250, fill=(95, 191, 106), fg=WHITE, size=48)
    if T >= WT("F03", "cuaderno") - .2: rot(c, T, WT("F03", "cuaderno") - .2, "EL CUADERNO", 790, 1250, fill=(232, 85, 109), fg=WHITE, size=48, rot=3)
    return c

def sc_sofia(T):   # F04
    t0 = S("F04") - .15
    c = bgz("bg_desvan", T, t0); P.polvo(c, T, 30, 2)
    put(c, "cuaderno", 830, 1180, .3, rot=10); P.brillos(c, T, t0, 830, 1180, 140, (255, 230, 150), 8)
    sofia(c, 470, 860, .98, T, "F04")
    rot(c, T, t0 + .3, "SOFÍA, 5 AÑOS", 540, 330, size=56)
    if T >= WT("F04", "mágico.") - .2: rot(c, T, WT("F04", "mágico.") - .2, "UN CUADERNO MÁGICO", 540, 1250, fill=(255, 236, 200), size=50)
    return cam(c, T, t0, [(540, 860, 1.0), (470, 720, 1.3), (700, 1050, 1.3)], 1.5)

def sc_escribe(T):   # F05: Mateo sigue aprendiendo a escribir
    t0 = S("F05") - .15
    c = bgz("bg_cuarto_mateo", T, t0, 1.05, 1.12)
    mateo(c, 540, 860, 1.0, T, None, "feliz_crayola")
    if talk("F05", T): mouth(c, 540, 860 + 56, T, True, 26)
    if T >= WT("F05", "escribir!") - .2: rot(c, T, WT("F05", "escribir!") - .2, "¡SIGO APRENDIENDO!", 540, 330, size=56)
    if T >= WT("F05", "viendo?") - .25:
        rot(c, T, WT("F05", "viendo?") - .25, "¿ME SIGUES VIENDO?", 540, 1260, fill=(95, 191, 106), fg=WHITE, size=54, rot=3)
    return cam(c, T, t0, [(540, 820, 1.05), (540, 720, 1.35)], 1.5)

def sc_perfil(T):   # F05: las dos en el perfil, vota en las dos
    t0 = S("F05") - .15; tv = WT("F05", "Vota") - .2
    c = bgz("bg_desvan", T, t0, 1.2, 1.28).filter(ImageFilter.GaussianBlur(10)); R.dark(c, 110)
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).rounded_rectangle((40, 480, 1040, 1250), 40, fill=(255, 210, 120, int(110 + 50 * math.sin(T * 6))))
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(40)))
    dos_portadas(c, T, t0 - 1)
    rot(c, T, t0, "LAS 2 EN EL PERFIL", 540, 330, fill=YEL, size=58)
    if T >= tv:
        rot(c, T, tv, "VOTA EN LAS DOS", 540, 1300, fill=(232, 85, 109), fg=WHITE, size=56)
        d = ImageDraw.Draw(c)
        for i, x in enumerate((290, 790)): corazon(d, x, 1150 - 10 * abs(math.sin(T * 7 + i)), 34, (232, 85, 109))
    return c

SCENES = [(0, sc_preocupado), (S("F02") - .15, sc_sigue), (S("F03") - .15, sc_dos), (S("F04") - .15, sc_sofia),
          (S("F05") - .15, sc_perfil)]
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
    efx = [(m("brillo"), WT("F02", "sigue,") - .15, -5), (m("brillo"), WT("F03", "dos") - .2, -5), (m("brillo"), WT("F04", "mágico.") - .2, -6),
           (m("brillo"), WT("F05", "Vota") - .2, -5)]
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
