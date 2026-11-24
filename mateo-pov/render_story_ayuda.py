"""Story CTA tierna "¿Nos ayudas?" (Mateo + mamá en off, con Rex). Comentar en todos los vídeos de Mateo.
Uso: python3 render_story_ayuda.py voz | still 1 5 | info | video"""
import os, sys, math, json, re, shutil, subprocess, random
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
VOZD = os.path.join(HERE, "voz_story_ayuda"); SRC = os.path.join(ROOT, "descargas", "mateo_story_ayuda")
import guion_story_ayuda as G

def prep_voz():   # mismo tratamiento que prep_voz.py de la serie (Mateo más agudo, mamá un pelín más rápida)
    os.makedirs(VOZD, exist_ok=True); TEMPO = {"N": 1.07, "K": 1.0}; PITCH = {"K": 1.13}; offs = {}
    for lid, v, *_ in G.LINEAS:
        src = os.path.join(SRC, lid + ".mp3")
        out = subprocess.run(["ffmpeg", "-i", src, "-af", "silencedetect=n=-40dB:d=0.02", "-t", "1.5", "-f", "null", "-"], capture_output=True, text=True).stderr
        m = re.search(r"silence_start: (-?[\d.]+).*?silence_end: ([\d.]+)", out, re.S)
        off = max(0.0, (float(m.group(2)) if m and float(m.group(1)) <= .01 else 0.0) - .03); tp = TEMPO[v]; pt = PITCH.get(v)
        pf = f"asetrate={int(44100 * pt)},aresample=44100,atempo={1 / pt:.4f}," if pt else ""
        af = (f"aresample=44100,atrim=start={off:.3f},asetpts=PTS-STARTPTS," + pf +
              f"areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo={tp}")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-af", af, "-ar", "44100", "-ac", "1", os.path.join(VOZD, lid + ".wav")], check=True)
        offs[lid] = {"off": off, "tempo": tp}
        j = os.path.join(SRC, lid + ".json")
        if os.path.exists(j): shutil.copy(j, os.path.join(VOZD, lid + ".json"))
    json.dump(offs, open(os.path.join(VOZD, "offsets.json"), "w")); print("voz ok", len(offs))

if len(sys.argv) > 1 and sys.argv[1] == "voz": prep_voz(); sys.exit()

os.environ["GUION"] = "guion_story_ayuda"; os.environ["VOZDIR"] = VOZD
sys.path.insert(0, HERE); sys.path.append(os.path.join(ROOT, "taller-pov"))
import importlib.util
_spec = importlib.util.spec_from_file_location("R", os.path.join(ROOT, "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.join(ROOT, "cuaderno-pov"))
import render1 as P   # utilidades de dibujo (rótulos, confeti, brillos)

R.LAY = os.path.join(HERE, "layers"); R.layer.cache_clear(); R.scaled.cache_clear()
TMP = os.path.join(HERE, "tmp_story_ayuda"); os.makedirs(TMP, exist_ok=True)
W, H, FPS = R.W, R.H, R.FPS
put, ease, clamp, back, font, mouth = R.put, R.ease, R.clamp, R.back, R.font, R.mouth
OL, YEL, WHITE, PI_ = R.OL, R.YEL, R.WHITE, math.pi
ROSA, VERDE = (232, 85, 109), (95, 191, 106)
R.GAP.update({"F02": .2, "F03": .2})
R.TL, R.TOTAL = R.timeline()
R.TL = {k: (a - .1, b - .1) for k, (a, b) in R.TL.items()}; R.TOTAL = R.TL["F03"][1] + .1   # corte en seco
R.CH = R.chunks(); TL = R.TL; TOTAL = R.TOTAL; S, E, WT = R.S, R.E, R.WT
R.NOMBRE = {"K": "MATEO", "N": "MAMÁ"}; R.HIDE_LAST_CAPTION = False
def talk(l, T): return S(l) <= T < E(l)

def mateo(c, cx, cy, s, T, lid=None, kind="feliz"):
    hab = lid is not None and talk(lid, T)
    nm = f"mateo_{kind}_hab" if hab and os.path.exists(os.path.join(R.LAY, f"mateo_{kind}_hab.png")) else f"mateo_{kind}"
    put(c, nm, cx, cy + 400 * s, s)
    if hab: mouth(c, cx, cy + 56 * s, T, True, int(26 * s))

def rex(c, T, x, y, s=.42, rot=0):   # Rex abrazado contra el pecho, se mece un poquito
    put(c, "dino", x, y + 6 * math.sin(T * 3.2), s, rot=rot + 4 * math.sin(T * 2.4))

def rot(c, T, t0, txt, cx, cy, **k): P.rotulo(c, T, t0, txt, cx, cy, **k)
def bgz(n, T, t0, z0=1.0, z1=1.08): return R.bg(n, T, t0, z0, z1, 6).copy()

def cam(c, T, t0, shots, iv=1.9):   # cambio de plano cada ~2 s, siempre con un leve zoom
    k = int((T - t0) / iv); cx, cy, z = shots[k % len(shots)]; z *= 1 + .035 * (((T - t0) % iv) / iv)
    if z <= 1.001: return c
    hw, hh = W / (2 * z), H / (2 * z); cx = min(max(cx, hw), W - hw); cy = min(max(cy, hh), H - hh)
    return c.crop((int(cx - hw), int(cy - hh), int(cx + hw), int(cy + hh))).resize((W, H), Image.BICUBIC)

def corazon(d, cx, cy, r, col):
    d.ellipse((cx - r, cy - r * .8, cx, cy + r * .2), fill=col); d.ellipse((cx, cy - r * .8, cx + r, cy + r * .2), fill=col)
    d.polygon([(cx - r * .97, cy - r * .15), (cx + r * .97, cy - r * .15), (cx, cy + r)], fill=col)

def corazones(c, T, t0, n=18, seed=3, y0=1350):   # corazoncitos que suben
    if T < t0: return
    r = random.Random(seed); d = ImageDraw.Draw(c); u = T - t0
    for k in range(n):
        st = r.uniform(0, 1.2)
        if u < st: continue
        v = u - st; x = r.uniform(90, 990) + 30 * math.sin(v * 3 + k); y = y0 - v * r.uniform(260, 420)
        if y < 220: continue
        corazon(d, x, y, r.uniform(18, 34), r.choice([ROSA, (255, 120, 150), (255, 196, 60)]))

def burbuja(c, x, y, s, k, txt_lines=2):   # globito de comentario
    if k <= 0: return
    w, h = 300 * s * k, 120 * s * k; d = ImageDraw.Draw(c)
    d.rounded_rectangle((x - w / 2 + 6, y - h / 2 + 8, x + w / 2 + 6, y + h / 2 + 8), 28 * s, fill=(20, 14, 30, 110))
    d.rounded_rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), 28 * s, fill=WHITE, outline=OL, width=5)
    d.polygon([(x - w * .25, y + h / 2 - 3), (x - w * .05, y + h / 2 - 3), (x - w * .3, y + h / 2 + 34 * s * k)], fill=WHITE, outline=OL)
    d.line((x - w * .25 + 3, y + h / 2 - 3, x - w * .05 - 3, y + h / 2 - 3), fill=WHITE, width=7)
    corazon(d, x - w / 2 + 50 * s * k, y, 22 * s * k, ROSA)
    for i in range(txt_lines):
        yy = y - h * .18 + i * h * .36; d.rounded_rectangle((x - w / 2 + 92 * s * k, yy - 8 * s, x + w / 2 - (40 + 60 * i) * s * k, yy + 8 * s), 8, fill=(200, 200, 215))

_GRID = {}
def grid(w):
    if w not in _GRID:
        im = Image.open(os.path.join(R.LAY, "grid_perfil.jpg")).convert("RGBA"); im = im.resize((w, int(im.height * w / im.width)))
        fr = Image.new("RGBA", (im.width + 24, im.height + 24), (255, 255, 255, 255)); fr.alpha_composite(im, (12, 12)); _GRID[w] = fr
    return _GRID[w]

# ---------------------------------------------------------------- escenas
def sc_hola(T):   # F01: Mateo tímido, abrazando a Rex
    c = bgz("bg_cuarto", T, 0, 1.0, 1.07)
    mateo(c, 540, 820, 1.0, T, "F01", "timido"); rex(c, T, 700, 1050, .36, -8)
    if T >= WT("F01", "ayudas") - .2: rot(c, T, WT("F01", "ayudas") - .2, "¿NOS AYUDAS?", 540, 330, fill=YEL, size=72)
    return cam(c, T, 0, [(540, 700, 1.36), (570, 780, 1.22)], 1.5)

def sc_grid(T):   # F02 (1.ª mitad): comentar en los vídeos de Mateo
    t0 = S("F02") - .15
    c = bgz("bg_cuarto", T, t0, 1.2, 1.28).filter(ImageFilter.GaussianBlur(10)); R.dark(c, 105)
    k = back((T - t0) / .45)
    if k > 0:
        g = grid(900); g = g.resize((max(1, int(g.width * k)), max(1, int(g.height * k)))).rotate(-2 + 1.2 * math.sin(T * 2.5), expand=True, resample=Image.BICUBIC)
        c.alpha_composite(g, (int(540 - g.width / 2), int(860 - g.height / 2)))
    tc = WT("F02", "comentas") - .2
    for i, (x, y) in enumerate(((280, 560), (800, 760), (300, 1050), (790, 1220))):
        burbuja(c, x, y - 12 * math.sin(T * 4 + i), .95, back((T - tc - i * .18) / .35) if T >= tc + i * .18 else 0)
    rot(c, T, tc, "¡COMENTA!", 540, 330, fill=ROSA, fg=WHITE, size=72)
    return cam(c, T, t0, [(540, 900, 1.0), (540, 820, 1.12)], 1.6)

def sc_personas(T):   # F02 (2.ª mitad): más personas conocen su historia
    t0 = WT("F02", "más") - .15
    c = bgz("bg_cuarto", T, t0, 1.04, 1.1)
    mateo(c, 540, 840, 1.0, T, None, "feliz"); rex(c, T, 720, 1050, .36, -6)
    corazones(c, T, t0 + .1)
    if T >= WT("F02", "personas") - .2: rot(c, T, WT("F02", "personas") - .2, "¡MÁS PERSONAS!", 540, 330, fill=YEL, size=66)
    if T >= WT("F02", "historia.") - .2: rot(c, T, WT("F02", "historia.") - .2, "CONOCEN SU HISTORIA", 540, 1250, fill=WHITE, size=50, rot=3)
    return cam(c, T, t0, [(540, 700, 1.36), (540, 790, 1.2)], 1.4)

def sc_escribir(T):   # F03: ¡y así puedo seguir aprendiendo a escribir!
    t0 = S("F03") - .15
    c = bgz("bg_cuarto", T, t0, 1.05, 1.12)
    mateo(c, 540, 840, 1.0, T, None, "feliz_crayola")
    if talk("F03", T): mouth(c, 540, 840 + 56, T, True, 26)
    P.confeti(c, T, WT("F03", "seguir") - .1)
    rot(c, T, t0 + .05, "COMENTA EN TODOS LOS VÍDEOS", 540, 330, fill=ROSA, fg=WHITE, size=52)
    if T >= WT("F03", "escribir!") - .2:
        tt = WT("F03", "escribir!") - .2; d = ImageDraw.Draw(c); k = back((T - tt) / .35)
        corazon(d, 800, 900, int(60 * k * (1 + .08 * math.sin(T * 9))), ROSA)
    return cam(c, T, t0, [(540, 720, 1.32), (540, 800, 1.18)], 1.3)

SCENES = [(0, sc_hola), (S("F02") - .15, sc_grid), (WT("F02", "más") - .15, sc_personas), (S("F03") - .15, sc_escribir)]
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
    m = lambda n: os.path.join(ROOT, "descargas", "mateo_sfx", n + ".mp3")
    ins, flt = [], []
    for i, lid in enumerate(TL):
        ins += ["-i", os.path.join(R.VOZ, lid + ".wav")]; ms = int(TL[lid][0] * 1000)
        flt.append(f"[{i}:a]aresample=48000,adelay={ms}|{ms},apad[a{i}]")
    n = len(TL)
    tc = WT("F02", "comentas") - .2
    efx = [(m("brillo"), WT("F01", "ayudas") - .2, -7)]                       # rótulo ¿NOS AYUDAS?
    efx += [(m("teclea"), tc + i * .18, -12) for i in range(4)]                 # globitos de comentario
    efx += [(m("brillo"), WT("F02", "personas") - .2, -7), (m("brillo"), WT("F03", "seguir") - .1, -6),
            (m("resultado"), WT("F03", "escribir!") - .2, -9)]                  # confeti + corazón final
    efx += [(m("whoosh"), t - .05, -11) for t, f in SCENES[1:]]
    efx.append((m("musica"), 0, -10))
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
    else: video(os.path.join(HERE, "story_mateo_nos_ayudas.mp4"))
