"""Story animada con voz para llevar gente a @lacasade1dolar (serie de reforma):
el salón pasa de ANTES a DESPUÉS con una cortina que barre, hueco vacío en el centro para el sticker @ y flechas."""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import salon as SL
from ep1 import cam
from story import F, texto, flecha, YEL, RED, WHITE, INK
HERE = os.path.dirname(os.path.abspath(__file__)); W, H, FPS = 1080, 1920, 30
VOZ = os.path.join(HERE, "..", "descargas", "casa_story", "S01.mp3")
HUECO = (240, 860, 840, 1110)
GREEN = (90, 200, 110)

A_IMG = cam(SL.salon("vieja", "moqueta", True), 1.35, 1296, 2150).convert("RGBA")
B_IMG = cam(SL.salon("salvia", "parquet_brillo", False), 1.35, 1296, 2150).convert("RGBA")

def dur():
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", VOZ], capture_output=True, text=True)
    return float(r.stdout.strip())

def frame(t, D):
    z = 1.0 + .04 * t / D
    def zoom(im):
        w, h = int(W * z), int(H * z); im = im.resize((w, h), Image.BICUBIC)
        return im.crop(((w - W) // 2, (h - H) // 2, (w - W) // 2 + W, (h - H) // 2 + H))
    a, b = zoom(A_IMG), zoom(B_IMG)
    # la cortina ANTES -> DESPUÉS va y viene
    u = .5 - .5 * math.cos(min(1, t / 2.6) * math.pi) if t < 2.6 else .5 + .5 * math.cos((t - 2.6) * 1.1)
    xs = int(W * (1 - u))
    c = a.copy(); c.paste(b.crop((xs, 0, W, H)), (xs, 0))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for y in range(H):
        al = 185 if y < 600 else (int(185 - (y - 600) * 1.1) if y < 690 else (85 if y < 1250 else int(85 + (y - 1250) * .25)))
        gd.line((0, y, W, y), fill=(6, 6, 18, min(215, max(0, al))))
    c.alpha_composite(g); d = ImageDraw.Draw(c)
    d.rectangle((xs - 5, 600, xs + 5, H), fill=WHITE)
    d.ellipse((xs - 34, 1180 - 34, xs + 34, 1180 + 34), fill=WHITE, outline=INK, width=5)
    d.polygon([(xs - 22, 1180), (xs - 8, 1168), (xs - 8, 1192)], fill=INK); d.polygon([(xs + 22, 1180), (xs + 8, 1168), (xs + 8, 1192)], fill=INK)
    if xs > 200: d.rounded_rectangle((40, 665, 250, 735), 18, fill=RED); d.text((145, 701), "ANTES", font=F(48), fill=WHITE, anchor="mm")
    if xs < W - 200: d.rounded_rectangle((W - 290, 665, W - 40, 735), 18, fill=GREEN); d.text((W - 165, 701), "DESPUÉS", font=F(48), fill=WHITE, anchor="mm")
    # titular
    texto(d, (540, 300), "COMPRÉ UNA CASA POR", 84, WHITE, 10)
    k = 1 + .05 * math.sin(t * 4)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).text((540, 450), "$1", font=F(210 * k), fill=YEL, anchor="mm", stroke_width=16, stroke_fill=INK)
    c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(20))); c.alpha_composite(lay); d = ImageDraw.Draw(c)
    texto(d, (540, 600), "Y LA ESTOY REFORMANDO", 64, WHITE, 8)
    # hueco para el @
    x0, y0, x1, y1 = HUECO
    box = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(box).rounded_rectangle(HUECO, 46, fill=(8, 8, 20, 130)); c.alpha_composite(box)
    d = ImageDraw.Draw(c); al = .55 + .45 * math.sin(t * 5); col = tuple(int(YEL[i] * al + WHITE[i] * (1 - al)) for i in range(3))
    per = 2 * (x1 - x0) + 2 * (y1 - y0); seg, gap = 46, 26
    def pt(v):
        v %= per
        if v < x1 - x0: return (x0 + v, y0)
        v -= x1 - x0
        if v < y1 - y0: return (x1, y0 + v)
        v -= y1 - y0
        if v < x1 - x0: return (x1 - v, y1)
        v -= x1 - x0; return (x0, y1 - v)
    v = (t * 120) % (seg + gap)
    s0 = v
    while v < per + s0:
        p1, p2 = pt(v), pt(v + seg)
        if abs(p1[0] - p2[0]) < 1 or abs(p1[1] - p2[1]) < 1: d.line((p1, p2), fill=col, width=9)
        v += seg + gap
    texto(d, (540, 800), "TOCA AQUÍ", 66, col, 9)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    flecha(c, x0 - 8, cy, 0, 110, YEL, t, 0); flecha(c, x1 + 8, cy, math.pi, 110, YEL, t, 0)
    flecha(c, x0 + 90, y1 + 10, -math.pi * .62, 150, RED, t, 1.6); flecha(c, x1 - 90, y1 + 10, -math.pi * .38, 150, RED, t, 1.6)
    d = ImageDraw.Draw(c)
    # barra de reforma + pastilla
    d.rounded_rectangle((190, 1400, 890, 1450), 25, fill=(40, 40, 56), outline=INK, width=5)
    p = .12 * min(1, t / 2)
    d.rounded_rectangle((196, 1406, 196 + 688 * max(p, .03), 1444), 20, fill=GREEN)
    d.text((540, 1370), f"REFORMA {int(round(p * 100))}%", font=F(46), fill=WHITE, anchor="mm", stroke_width=6, stroke_fill=INK)
    d.rounded_rectangle((300, 1490, 780, 1570), 40, fill=RED, outline=INK, width=6)
    d.text((540, 1532), "PARTE NUEVA CADA DÍA", font=F(46), fill=WHITE, anchor="mm")
    return c.convert("RGB")

if __name__ == "__main__":
    D = dur() + .8 if os.path.exists(VOZ) else 9.0
    out = os.path.join(HERE, "out")
    if len(sys.argv) > 1:
        frame(float(sys.argv[1]), D).save("/tmp/sr.png"); sys.exit()
    frame(1.6, D).save(os.path.join(out, "story_reforma_lacasade1dolar.png"))
    tmp = os.path.join(out, "_story_mudo.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for i in range(int(D * FPS)): p.stdin.write(frame(i / FPS, D).tobytes())
    p.stdin.close(); p.wait()
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-i", VOZ, "-af", "adelay=150|150,loudnorm=I=-15:TP=-1.5,aresample=48000,apad", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", os.path.join(out, "story_reforma_lacasade1dolar.mp4")], check=True)
    os.remove(tmp); print("ok")
