"""Story CTA tierna: el comentario con más corazones sale en el próximo vídeo (Mateo + mamá en off, con Rex).
Uso: python3 render_story_ayuda.py voz | still 1 5 | info | video"""
import os, sys, math, json, re, shutil, subprocess, random
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
VOZD = os.path.join(HERE, "voz_story_corazon"); SRC = os.path.join(ROOT, "descargas", "mateo_story_corazon")
import guion_story_corazon as G

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

os.environ["GUION"] = "guion_story_corazon"; os.environ["VOZDIR"] = VOZD
sys.path.insert(0, HERE); sys.path.append(os.path.join(ROOT, "taller-pov"))
import importlib.util
_spec = importlib.util.spec_from_file_location("R", os.path.join(ROOT, "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.join(ROOT, "cuaderno-pov"))
import render1 as P   # utilidades de dibujo (rótulos, confeti, brillos)

R.LAY = os.path.join(HERE, "layers"); R.layer.cache_clear(); R.scaled.cache_clear()
TMP = os.path.join(HERE, "tmp_story_corazon"); os.makedirs(TMP, exist_ok=True)
W, H, FPS = R.W, R.H, R.FPS
put, ease, clamp, back, font, mouth = R.put, R.ease, R.clamp, R.back, R.font, R.mouth
OL, YEL, WHITE, PI_ = R.OL, R.YEL, R.WHITE, math.pi
ROSA, VERDE = (232, 85, 109), (95, 191, 106)
R.GAP.update({"F02": .2, "F03": .2, "F04": .2})
R.TL, R.TOTAL = R.timeline()
R.TL = {k: (a - .1, b - .1) for k, (a, b) in R.TL.items()}; R.TOTAL = R.TL["F04"][1] + .1   # corte en seco
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


def corona(d, cx, cy, s):   # coronita dorada encima del comentario ganador
    pts = [(cx - 46 * s, cy + 22 * s), (cx - 52 * s, cy - 26 * s), (cx - 24 * s, cy), (cx, cy - 40 * s), (cx + 24 * s, cy), (cx + 52 * s, cy - 26 * s), (cx + 46 * s, cy + 22 * s)]
    d.polygon(pts, fill=(255, 196, 60), outline=OL); d.line(pts + [pts[0]], fill=OL, width=5)
    for x in (-52, 0, 52): d.ellipse((cx + x * s - 9 * s, cy - (40 if x == 0 else 26) * s - 9 * s, cx + x * s + 9 * s, cy - (40 if x == 0 else 26) * s + 9 * s), fill=ROSA, outline=OL, width=3)

def marco_video(c, T, t0, cx, cy, w, h):   # "pantalla" del próximo vídeo
    k = back((T - t0) / .4) if T >= t0 else 0
    if k <= 0: return
    d = ImageDraw.Draw(c); ww, hh = w * k, h * k
    d.rounded_rectangle((cx - ww / 2 + 10, cy - hh / 2 + 12, cx + ww / 2 + 10, cy + hh / 2 + 12), 36, fill=(20, 14, 30, 120))
    d.rounded_rectangle((cx - ww / 2, cy - hh / 2, cx + ww / 2, cy + hh / 2), 36, fill=(40, 36, 70), outline=WHITE, width=8)
    if k > .9:   # botón play
        d.polygon([(cx - 40, cy - 50), (cx - 40, cy + 50), (cx + 50, cy)], fill=(255, 255, 255, 200))

def sc_mira(T):   # F01: ¡Mami, mira! Un comentario salió en mi video
    c = bgz("bg_cuarto", T, 0, 1.0, 1.07)
    mateo(c, 540, 820, 1.0, T, "F01", "feliz")
    tc = WT("F01", "comentario") - .25
    if T >= tc:
        k = back((T - tc) / .4); burbuja(c, 760, 560 - 10 * math.sin(T * 4), 1.15, k, 2)
        if k > .9: corona(ImageDraw.Draw(c), 760, 470 - 10 * math.sin(T * 4), 1.0)
        P.brillos(c, T, tc, 760, 560, 200, (255, 236, 160), 10)
    if T >= WT("F01", "mira!") - .2: rot(c, T, WT("F01", "mira!") - .2, "¡MAMI, MIRA!", 540, 330, fill=YEL, size=72)
    return cam(c, T, 0, [(540, 700, 1.36), (640, 640, 1.25)], 1.6)

def sc_ranking(T):   # F02: el comentario con más corazones sale en el siguiente video
    t0 = S("F02") - .15
    c = bgz("bg_cuarto", T, t0, 1.2, 1.28).filter(ImageFilter.GaussianBlur(10)); R.dark(c, 105)
    tw = WT("F02", "corazones") - .2; ts = WT("F02", "siguiente") - .2
    pos = [(420, 540, 1.45), (420, 880, 1.45), (420, 1220, 1.45)]
    for i, (x, y, s) in enumerate(pos):
        ti = t0 + .1 + i * .2
        if T < ti: continue
        k = back((T - ti) / .35); grande = i == 1 and T >= tw
        if grande and T >= ts:   # el ganador viaja al "próximo video"
            u = ease((T - ts) / .5); x, y, s = x, y + (1150 - y) * u * 0, s * (1 + .25 * u)
        burbuja(c, x - 40, y, s * (1.12 if grande else 1), k, 2)
        d = ImageDraw.Draw(c); n = 5 if grande else (2 if i == 0 else 1)
        for j in range(n):   # corazones de votos (más = más corazones)
            hx = x + (330 if grande else 290) + j * (46 if grande else 52); hy = y - 10 * abs(math.sin(T * 6 + j)) if grande else y
            corazon(d, hx, hy, 24 if not grande else 28, ROSA)
        if grande: corona(d, x - 250, y - 100, 1.1)
    if tw <= T < ts: rot(c, T, tw, "EL DE MÁS CORAZONES", 540, 330, fill=ROSA, fg=WHITE, size=60)
    if T >= ts: rot(c, T, ts, "¡SALE EN EL PRÓXIMO VIDEO!", 540, 330, fill=YEL, size=56)
    return cam(c, T, t0, [(540, 880, 1.0), (540, 880, 1.06)], 1.6)

def sc_tuyo(T):   # F03: ¡El tuyo puede ser el próximo! Comenta... dale corazón
    t0 = S("F03") - .15; tc = WT("F03", "Comenta") - .15; th = WT("F03", "corazón") - .2
    c = bgz("bg_cuarto", T, t0, 1.04, 1.1)
    if T < tc:
        mateo(c, 540, 840, 1.0, T, "F03", "timido"); rex(c, T, 770, 980, .32, -6)
        rot(c, T, WT("F03", "tuyo") - .2, "¡EL TUYO PUEDE SER EL PRÓXIMO!", 540, 330, fill=YEL, size=50)
        return cam(c, T, t0, [(540, 700, 1.36), (560, 780, 1.22)], 1.4)
    mateo(c, 540, 840, 1.0, T, "F03", "feliz"); rex(c, T, 770, 980, .32, -6)
    if T < th: rot(c, T, tc, "COMENTA", 540, 330, fill=ROSA, fg=WHITE, size=72)
    if T >= th:
        d = ImageDraw.Draw(c); k = back((T - th) / .35)
        corazon(d, 820, 880, int(70 * k * (1 + .1 * math.sin(T * 9))), ROSA)
        corazones(c, T, th, 12, 5, 1250)
        rot(c, T, th, "DALE CORAZÓN A TU FAVORITO", 540, 330, fill=ROSA, fg=WHITE, size=52)
    return cam(c, T, tc, [(540, 720, 1.3), (560, 790, 1.18)], 1.4)

def sc_gracias(T):   # F04: Leemos todos sus comentarios. Gracias por acompañarnos
    t0 = S("F04") - .15; tg = WT("F04", "Gracias") - .2
    c = bgz("bg_cuarto", T, t0, 1.05, 1.12)
    mateo(c, 540, 840, 1.0, T, None, "feliz"); rex(c, T, 770, 980, .32, -6)
    if T < tg:
        tl = t0 + .1
        for i, (x, y) in enumerate(((250, 560), (830, 700), (260, 980))):
            ti = tl + i * .25
            if T >= ti: burbuja(c, x, y - 10 * math.sin(T * 4 + i), .8, back((T - ti) / .35), 2)
        rot(c, T, WT("F04", "Leemos") - .2, "LOS LEEMOS TODOS", 540, 330, fill=YEL, size=62)
        return cam(c, T, t0, [(540, 760, 1.15), (540, 700, 1.3)], 1.5)
    corazones(c, T, tg, 22, 9, 1300)
    rot(c, T, tg, "¡GRACIAS!", 540, 330, fill=ROSA, fg=WHITE, size=80)
    return cam(c, T, tg, [(540, 700, 1.36), (540, 780, 1.2)], 1.3)

SCENES = [(0, sc_mira), (S("F02") - .15, sc_ranking), (S("F03") - .15, sc_tuyo), (S("F04") - .15, sc_gracias)]
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
    efx = [(m("brillo"), WT("F01", "comentario") - .25, -7), (m("brillo"), WT("F01", "mira!") - .2, -9)]   # aparece el comentario con corona
    efx += [(m("teclea"), S("F02") - .05 + i * .2, -12) for i in range(3)]                                # entran los 3 comentarios
    efx += [(m("resultado"), WT("F02", "siguiente") - .2, -9), (m("brillo"), WT("F03", "tuyo") - .2, -8),
            (m("teclea"), WT("F03", "Comenta") - .15, -11), (m("brillo"), WT("F03", "corazón") - .2, -7),
            (m("teclea"), S("F04") - .05, -12), (m("brillo"), WT("F04", "Gracias") - .2, -7)]
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
    else: video(os.path.join(HERE, "story_mateo_comentario_corazon.mp4"))
