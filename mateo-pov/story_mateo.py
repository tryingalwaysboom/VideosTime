"""Story emocional de la serie de Mateo: hueco central para el sticker de ENCUESTA + pastilla 'sígueme para no perder la próxima parte'.
Voz: descargas/mateo_story/S01.mp3 (Lily, narradora de la serie). Sin voz usa duración estimada y sale mudo."""
import math, os, subprocess, sys
sys.argv, _a = sys.argv[:1], sys.argv[1:]
import render5 as V
from render5 import *
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); FPS = 30
VOZ = os.path.join(HERE, "..", "descargas", "mateo_story", "S01.mp3")
TEXTO = ("Hola, mamás. Quiero preguntarte algo de corazón: ¿te está gustando la historia de Mateo? "
         "Cada parte la hago pensando en ti y en tu peque. Cuéntame votando aquí. Y sígueme, para no perderte la próxima parte.")
FRASES = [("Hola, mamás", .00, .12), ("¿Te está gustando\nla historia de Mateo?", .12, .42), ("Cada parte la hago pensando\nen ti y en tu peque", .42, .72),
          ("Cuéntame votando aquí", .72, .86), ("Sígueme para no perderte\nla próxima parte", .86, 1.0)]
HUECO = (150, 800, 930, 1130)
ORG, ORG2, NV = (244, 124, 42), (255, 160, 70), (22, 36, 66)

def dur():
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", VOZ], capture_output=True, text=True)
    return float(r.stdout.strip())

def txt(c, xy, t, sz, fill=WHITE, stroke=8, f=None):
    d = ImageDraw.Draw(c); fn = font(f or F_ANTON, sz)
    for i, ln in enumerate(t.split("\n")):
        d.text((xy[0], xy[1] + i * sz * 1.18), ln, font=fn, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=(20, 14, 30))

def _noche(c, a=110): c.alpha_composite(Image.new("RGBA", (W, H), (20, 18, 70, a)))

def esc_dormido(t, D):
    c = V.bg("bg_cuarto", t, 0, 1.15, 1.25, D * .3, .5, .55).convert("RGBA"); _noche(c, 130)
    k = 1 + .012 * math.sin(t * 1.6)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); put(lay, "mateo_duerme", 540, 690, .62 * k)
    from PIL import ImageChops; m = Image.new("L", (W, H), 255); md = ImageDraw.Draw(m)
    for y in range(640, 780): md.line((0, y, W, y), fill=int(255 * max(0, 1 - (y - 640) / 140)))
    md.rectangle((0, 780, W, H), fill=0); lay.putalpha(ImageChops.multiply(lay.split()[3], m)); c.alpha_composite(lay)
    d = ImageDraw.Draw(c)
    for i in range(3):                                   # zZz que suben
        u = ((t * .4 + i / 3) % 1.0); x = 700 + 60 * u + 20 * math.sin(u * 6); y = 520 - 230 * u
        d.text((x, y), "z" if i % 2 else "Z", font=font(F_ANTON, int(50 + 26 * u)), fill=(255, 255, 255, int(230 * (1 - u))), anchor="mm")
    return c

def _retrato(c, kind, t, cx=540, cy=650, sc=.62, extra=None):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); mateo(lay, kind, cx, cy, sc, t)
    if extra: extra(lay)
    al = lay.split()[3]; m = Image.new("L", (W, H), 255); md = ImageDraw.Draw(m)
    for y in range(690, 800): md.line((0, y, W, y), fill=int(255 * max(0, 1 - (y - 690) / 90)))
    md.rectangle((0, 800, W, H), fill=0)
    from PIL import ImageChops; lay.putalpha(ImageChops.multiply(al, m)); c.alpha_composite(lay)

def esc_carta(t, D):
    c = V.bg("bg_cuarto", t, 0, 1.15, 1.25, D * .3, .5, .55).convert("RGBA"); c.alpha_composite(Image.new("RGBA", (W, H), (255, 190, 120, 40)))
    u = ease(min(1, t / .8)); _retrato(c, "feliz", t, 540, 650 + 40 * (1 - u))
    sobre(c, 540 + 230 * math.sin(t * 1.4), 600 + 12 * math.sin(t * 3), .45, rot=8 * math.sin(t * 2))
    for i in range(7):
        w = ((t * .32 + i / 7) % 1.0); x = 540 + 260 * math.sin(i * 1.9 + t * .7); y = 640 - 330 * w
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); corazon(ImageDraw.Draw(lay), x, y, 14 + 8 * math.sin(i), (255, 110, 150, int(230 * (1 - w)))); c.alpha_composite(lay)
    return c

def esc_duda(t, D):
    c = V.bg("bg_mesa", t, 0, 1.15, 1.25, D * .3, .5, .5).convert("RGBA"); _noche(c, 70)
    carta(c, t + 99, 0, 1, 540, 600, .46, rot=-3 + 2 * math.sin(t * 1.5))
    mateo(c, "timido", 880, 720, .3, t) if False else None
    d = ImageDraw.Draw(c); k = 1 + .05 * math.sin(t * 3)
    txt(c, (850, 450), "¿?", int(120 * k), (255, 214, 160), 10)
    return c

def esc_final(t, D):
    c = V.bg("bg_cuarto", t, 0, 1.2, 1.28, D * .3, .5, .55).convert("RGBA"); _noche(c, 150)
    _retrato(c, "feliz", t)
    return c

def put(c, name, x, y, s, rot=0): V.put(c, name, x, y, s, rot=rot)
mateo = V.mateo; sobre = V.sobre; carta = V.carta; corazon = V.corazon; ease = V.ease

def frame(t, D):
    P = [(0, .12, esc_carta), (.12, .42, esc_carta), (.42, .72, esc_dormido), (.72, 1.0, esc_final)]
    c = None
    for i, (a_, b_, fn) in enumerate(P):
        ta, tb = a_ * D, b_ * D
        if i == len(P) - 1: tb = D + 1
        if ta - .45 <= t < tb:
            im = fn(max(0, t - ta + .45) if False else t - ta, D) if t >= ta else None
            if t < ta:      # fundido de entrada
                lay = fn(0, D); lay.putalpha(lay.split()[3].point(lambda v: int(v * (1 - (ta - t) / .45))))
                c = (c if c is not None else lay).copy(); c.alpha_composite(lay) if c is not None else None
            else: c = im
    if c is None: c = esc_dormido(t, D)
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for y in range(H):
        a = max(0, 150 - y * .35) if y < 430 else (max(0, (y - 1350) * .32) if y > 1350 else 0)
        gd.line((0, y, W, y), fill=(14, 8, 30, int(min(190, a))))
    c.alpha_composite(g)
    txt(c, (540, 300), "UNA PREGUNTA DE CORAZÓN", 50, (255, 214, 160), 8)
    x0, y0, x1, y1 = HUECO
    box = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(box).rounded_rectangle(HUECO, 54, fill=(10, 8, 30, 70), outline=(255, 255, 255, 120), width=4)
    c.alpha_composite(box)
    al = .5 + .5 * math.sin(t * 3); d = ImageDraw.Draw(c)
    d.rounded_rectangle((x0 - 6, y0 - 6, x1 + 6, y1 + 6), 60, outline=(255, int(190 + 50 * al), int(120 + 80 * al)), width=6)
    if t > FRASES[3][1] * D - .6:
        txt(c, (540, 772), "VOTA AQUÍ", 56, (255, 226, 170), 8)
        for sx in (x0 + 140, x1 - 140):
            off = 14 * math.sin(t * 4); d = ImageDraw.Draw(c)
            d.polygon([(sx - 36, y0 - 62 + off), (sx + 36, y0 - 62 + off), (sx, y0 - 14 + off)], fill=(255, 214, 160), outline=(20, 14, 30))
    for s_, a_, b_ in FRASES[:4]:
        ta, tb = a_ * D, b_ * D
        if ta <= t < tb:
            kk = min(1, (t - ta) / .35) * min(1, (tb - t) / .3)
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); txt(lay, (540, 1290), s_, 56, WHITE, 8, F_BAL)
            if kk < 1: lay.putalpha(lay.split()[3].point(lambda v: int(v * kk)))
            c.alpha_composite(lay)
    ts = FRASES[4][1] * D - .2
    if t >= ts:
        kk = ease((t - ts) / .5); pw, ph = 760, 150; y = 1480 + 60 * (1 - kk)
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((540 - pw / 2, y + 12, 540 + pw / 2, y + ph + 12), 75, fill=(0, 0, 0, 140))
        c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((540 - pw / 2, y, 540 + pw / 2, y + ph), 75, fill=ORG, outline=(255, 255, 255), width=5)
        ld.ellipse((540 - pw / 2 + 24, y + 24, 540 - pw / 2 + 126, y + 126), fill=WHITE); corazon(ld, 540 - pw / 2 + 75, y + 70, 26, ORG)
        ld.text((540 + 70, y + 54), "SÍGUEME", font=font(F_ANTON, 64), fill=WHITE, anchor="mm")
        ld.text((540 + 70, y + 108), "para no perderte la Parte 6", font=font(F_BAL, 34), fill=(255, 240, 220), anchor="mm")
        if kk < 1: lay.putalpha(lay.split()[3].point(lambda v: int(v * kk)))
        c.alpha_composite(lay)
    return c.convert("RGB")

if __name__ == "__main__":
    D = dur() + .9 if os.path.exists(VOZ) else 24.0
    if _a and _a[0] == "still":
        for t in _a[1:]: frame(float(t), D).save(f"/tmp/sm_{float(t):05.1f}.jpg", quality=88)
        sys.exit()
    out = os.path.join(HERE, "out"); os.makedirs(out, exist_ok=True)
    tmp = os.path.join(out, "_story_mudo.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for i in range(int(D * FPS)): p.stdin.write(frame(i / FPS, D).tobytes())
    p.stdin.close(); p.wait()
    fin = os.path.join(out, "story_mateo_encuesta.mp4")
    if os.path.exists(VOZ):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-i", VOZ, "-af", "adelay=150|150,loudnorm=I=-15:TP=-1.5,aresample=48000,apad", "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", fin], check=True); os.remove(tmp)
    else: os.replace(tmp, fin)
    print("ok", fin)
