"""Base común de los mini vídeos de estilo: mismo tramo (vestuario: narrador N08 + Paco N09), mismos tiempos y audio."""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from functools import lru_cache

CLUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, CLUB)
import render as R

W, H, FPS = 1080, 1920, 30
FONTS = os.path.join(CLUB, "fonts")
T0 = R.S("N08") - .3
T1 = R.E("N09") + .7
D = T1 - T0

def ease(u): return R.ease(u)
def clamp(u): return max(0., min(1., u))
def back(u): return R.back(u)

@lru_cache(None)
def font(name, size): return ImageFont.truetype(os.path.join(FONTS, name) if not name.startswith("/") else name, max(1, int(size)))

def palabras(lid):
    """[(palabra_subtitulo, inicio, fin)] con tiempos absolutos alineados a la voz."""
    cap = [x for x in R.LINEAS if x[0] == lid][0][3].split()
    return [(w, a, b) for w, (a, b) in zip(cap, R.word_times(lid, cap))]

EV = {  # momentos clave (tiempo absoluto)
    "paco": R.WT("N08", "Paco."),
    "41": R.WT("N08", "41"),
    "9": R.WT("N08", "9"),
    "cobra": R.WT("N08", "cobra."),
    "habla0": R.S("N09"), "habla1": R.E("N09"),
}

def boca(T):
    """Apertura de boca 0..1 mientras Paco habla (sigue las sílabas aproximadas)."""
    if not (EV["habla0"] <= T < EV["habla1"]): return 0.
    for w, a, b in palabras("N09"):
        if a <= T < b:
            u = (T - a) / max(.05, b - a)
            n = max(1, round(len(w) / 3))
            return abs(math.sin(u * n * math.pi)) * (.6 + .4 * ((hash(w) % 5) / 4))
    return 0.

def exportar(frame_fn, nombre, workers=2):
    """Renderiza el tramo con frame_fn(T)->PIL RGB y le pone la voz original."""
    from multiprocessing import Pool
    tmpdir = os.path.join(CLUB, "tmp"); os.makedirs(tmpdir, exist_ok=True)
    n = int(D * FPS); half = n // 2
    parts = [(0, half, os.path.join(tmpdir, f"{nombre}_a.mp4")), (half, n, os.path.join(tmpdir, f"{nombre}_b.mp4"))]
    global _FN; _FN = frame_fn
    with Pool(workers) as p: p.map(_part, parts)
    lst = os.path.join(tmpdir, f"{nombre}_l.txt")
    open(lst, "w").write("".join(f"file '{x[2]}'\n" for x in parts))
    out = os.path.join(CLUB, f"{nombre}.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-ss", str(T0), "-t", str(D),
                    "-i", os.path.join(tmpdir, "voz_prev.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "21",
                    "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", out], check=True)
    return out

_FN = None
def _part(a):
    f0, f1, out = a
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in range(f0, f1): p.stdin.write(_FN(T0 + f / FPS).tobytes())
    p.stdin.close(); p.wait()
