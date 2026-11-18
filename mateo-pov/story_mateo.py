"""Story emocional de la serie de Mateo: hueco central para el sticker de ENCUESTA + pastilla 'sígueme para no perder la próxima parte'.
Voz: descargas/mateo_story/S01.mp3 (Lily, narradora de la serie). Sin voz usa duración estimada y sale mudo."""
import math, os, subprocess, sys
sys.argv, _a = sys.argv[:1], sys.argv[1:]
import render5 as V
from render5 import *
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); FPS = 30
VOZ = os.path.join(HERE, "..", "descargas", "mateo_story", "S01.mp3")
TEXTO = ("Mateo todavía cree que Rex le escribe. Cada noche espera su cartita… y yo no sé si decirle la verdad. "
         "¿Le cuento que era yo, o lo dejo creer un poquito más? Tú decides. Vota aquí. Y sígueme, para no perderte la próxima parte.")
FRASES = [("Mateo todavía cree\nque Rex le escribe", .00, .17), ("Cada noche espera su cartita…\ny yo no sé si decirle la verdad", .17, .46),
          ("¿Le cuento que era yo,\no lo dejo creer un poquito más?", .46, .76), ("Tú decides", .76, .86), ("Sígueme para no perderte\nla próxima parte", .86, 1.0)]
HUECO = (150, 800, 930, 1130)
ORG, ORG2, NV = (244, 124, 42), (255, 160, 70), (22, 36, 66)

def dur():
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", VOZ], capture_output=True, text=True)
    return float(r.stdout.strip())

def txt(c, xy, t, sz, fill=WHITE, stroke=8, f=None):
    d = ImageDraw.Draw(c); fn = font(f or F_ANTON, sz)
    for i, ln in enumerate(t.split("\n")):
        d.text((xy[0], xy[1] + i * sz * 1.18), ln, font=fn, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=(20, 14, 30))

def frame(t, D):
    c = V.bg("bg_cocina", t, 0, 1.12, 1.2, D, .5, .6).convert("RGBA")
    c.alpha_composite(Image.new("RGBA", (W, H), (30, 20, 70, 95)))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)       # viñeta cálida arriba y abajo
    for y in range(H):
        a = max(0, 150 - y * .35) if y < 430 else (max(0, (y - 1350) * .32) if y > 1350 else 0)
        gd.line((0, y, W, y), fill=(14, 8, 30, int(min(190, a))))
    c.alpha_composite(g)
    # titular fijo arriba (zona segura: debajo de y 250)
    txt(c, (540, 330), "ANTES DE DORMIR…", 62, (255, 214, 160), 8)
    # el buzón de Rex con la cartita que sube y corazones
    bob = 8 * math.sin(t * 2)
    buzon(c, 540, 600 + bob, .62, t, rotulo=False)
    k = (t * .45) % 1.0
    lay0 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sobre(lay0, 540 + 18 * math.sin(t * 2.2), 520 - 110 * k + bob, .55 * (1 - .25 * k), rot=6 * math.sin(t * 2))
    lay0.putalpha(lay0.split()[3].point(lambda v: int(v * min(1, (1 - k) * 2.2)))); c.alpha_composite(lay0)
    d = ImageDraw.Draw(c)
    for i in range(6):
        u = ((t * .35 + i / 6) % 1.0); x = 540 + 230 * math.sin(i * 2.1 + t * .8); y = 560 - 340 * u
        r = 16 + 8 * math.sin(i); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); corazon(ImageDraw.Draw(lay), x, y, r, (255, 110, 150, int(220 * (1 - u))))
        c.alpha_composite(lay)
    # hueco del sticker de encuesta, con marco que respira y flechas
    x0, y0, x1, y1 = HUECO
    box = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(box).rounded_rectangle(HUECO, 54, fill=(255, 255, 255, 28), outline=(255, 255, 255, 120), width=4)
    c.alpha_composite(box.filter(ImageFilter.GaussianBlur(.6)))
    al = .5 + .5 * math.sin(t * 3); d = ImageDraw.Draw(c)
    d.rounded_rectangle((x0 - 6, y0 - 6, x1 + 6, y1 + 6), 60, outline=(255, int(190 + 50 * al), int(120 + 80 * al)), width=6)
    txt(c, (540, 760), "VOTA AQUÍ", 58, (255, 226, 170), 8)
    for sx in (x0 + 140, x1 - 140):                                            # flechas suaves hacia el hueco
        off = 14 * math.sin(t * 4); d = ImageDraw.Draw(c)
        d.polygon([(sx - 36, y0 - 62 + off), (sx + 36, y0 - 62 + off), (sx, y0 - 14 + off)], fill=(255, 214, 160), outline=(20, 14, 30))
    # frases emocionales sincronizadas (fundido suave)
    for s_, a_, b_ in FRASES[:4]:
        ta, tb = a_ * D, b_ * D
        if ta <= t < tb:
            kk = min(1, (t - ta) / .35) * min(1, (tb - t) / .3)
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); txt(lay, (540, 1290), s_, 56, WHITE, 8, F_BAL)
            if kk < 1: lay.putalpha(lay.split()[3].point(lambda v: int(v * kk)))
            c.alpha_composite(lay)
    # pastilla SÍGUEME (aparece al final)
    ts = FRASES[4][1] * D - .2
    if t >= ts:
        kk = ease((t - ts) / .5); pw, ph = 760, 150; y = 1480 + 60 * (1 - kk)
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((540 - pw / 2, y + 12, 540 + pw / 2, y + ph + 12), 75, fill=(0, 0, 0, 140))
        c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((540 - pw / 2, y, 540 + pw / 2, y + ph), 75, fill=ORG, outline=(255, 255, 255), width=5)
        ld.ellipse((540 - pw / 2 + 24, y + 24, 540 - pw / 2 + 126, y + 126), fill=WHITE)
        corazon(ld, 540 - pw / 2 + 75, y + 70, 26, ORG)
        ld.text((540 + 70, y + 54), "SÍGUEME", font=font(F_ANTON, 64), fill=WHITE, anchor="mm")
        ld.text((540 + 70, y + 108), "para no perderte la Parte 6", font=font(F_BAL, 34), fill=(255, 240, 220), anchor="mm")
        if kk < 1: lay.putalpha(lay.split()[3].point(lambda v: int(v * kk)))
        sc = 1 + .025 * math.sin(t * 5)
        lay = lay.resize((int(W * sc), int(H * sc)), Image.BICUBIC); c.alpha_composite(lay, (int((W - lay.width) / 2), int(y + ph / 2 - (y + ph / 2) * sc)))
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
