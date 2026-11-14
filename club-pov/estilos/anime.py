"""Estilo 3: anime dibujado (vestuario al atardecer, Paco con ojos y boca animados)."""
import math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from comun import *
import look

CAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "capas_anime")
L = {n: Image.open(os.path.join(CAP, n + ".png")).convert("RGBA") for n in ("paco_base", "gafas", "ojos_a", "ojos_c", "boca0", "boca1", "boca2")}
BG = Image.open(os.path.join(CAP, "fondo.png")).convert("RGB").filter(ImageFilter.GaussianBlur(1.2))
PS = .5
_cache = {}
def paco(ojo, b):
    k = (ojo, b)
    if k not in _cache:
        im = L["paco_base"].copy()
        for n in (ojo, "gafas", b): im.alpha_composite(L[n])
        _cache[k] = im.resize((int(im.width * PS), int(im.height * PS)), Image.LANCZOS)
    return _cache[k]

def estrella(d, x, y, r, col, a=255):
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * .28
        ang = math.pi / 4 * i
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
    d.polygon(pts, fill=col + (a,))

def gota(d, x, y, s):
    d.ellipse((x - 18 * s, y, x + 18 * s, y + 40 * s), fill=(140, 200, 255, 230), outline=(40, 60, 110, 255), width=4)
    d.polygon([(x - 15 * s, y + 14 * s), (x, y - 26 * s), (x + 15 * s, y + 14 * s)], fill=(140, 200, 255, 230))
    d.line((x - 15 * s, y + 14 * s, x, y - 26 * s, x + 15 * s, y + 14 * s), fill=(40, 60, 110, 255), width=4)
    d.ellipse((x - 8 * s, y + 8 * s, x - 1 * s, y + 20 * s), fill=(255, 255, 255, 230))

def frame(T):
    t = T - T0
    z = 1.0 + .05 * t / D
    bg = BG.resize((int(W * z), int(H * z)), Image.BILINEAR)
    c = bg.crop((int((bg.width - W) * .4), int((bg.height - H) * .5), int((bg.width - W) * .4) + W, int((bg.height - H) * .5) + H)).convert("RGBA")
    # Paco entra con un deslizamiento suave
    tin = EV["paco"] - .55
    u = ease((T - tin) / .5) if T >= tin else 0
    if u > 0:
        blink = (T % 3.3) < .11
        m = boca(T); b = "boca2" if m > .55 else ("boca1" if m > .15 else "boca0")
        p = paco("ojos_c" if blink else "ojos_a", b)
        br = 1 + .005 * math.sin(t * 2.3)
        if br != 1: p = p.resize((p.width, int(p.height * br)), Image.BILINEAR)
        x = 540 - p.width / 2 + 420 * (1 - u)
        y = H - p.height + 60
        c.alpha_composite(p, (int(x), int(y)))
    d = ImageDraw.Draw(c)
    # partículas brillantes en el rayo de luz
    rng = np.random.default_rng(2)
    for i in range(34):
        px = (rng.uniform(100, 1080) + t * rng.uniform(5, 20)) % 1080
        py = (rng.uniform(150, 1400) - t * rng.uniform(10, 30)) % 1300 + 150
        a = int(120 + 100 * math.sin(t * 2 + i))
        r = rng.uniform(2, 5)
        d.ellipse((px - r, py - r, px + r, py + r), fill=(255, 245, 210, max(0, a)))
    # tarjeta de presentación tipo anime (franja diagonal)
    tp = EV["paco"]
    if T >= tp:
        k = ease((T - tp) / .35)
        band = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
        x0 = -700 + 760 * k
        bd.polygon([(x0, 420), (x0 + 700, 420), (x0 + 640, 560), (x0 - 60, 560)], fill=(255, 201, 60, 240))
        bd.polygon([(x0 + 40, 560), (x0 + 600, 560), (x0 + 570, 620), (x0 + 10, 620)], fill=(40, 30, 60, 235))
        bd.text((x0 + 70, 490), "PACO", font=font("Bangers-Regular.ttf", 120), fill=(40, 30, 60), anchor="lm")
        bd.text((x0 + 70, 590), "UTILLERO DESDE 1985", font=font("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", 34), fill=(255, 255, 255), anchor="lm")
        c.alpha_composite(band)
        d = ImageDraw.Draw(c)
    # 41 años: destello de estrellas
    t41 = EV["41"]
    if t41 <= T < t41 + 1.6:
        k = back((T - t41) / .35); fa = 1 - clamp((T - t41 - 1.1) / .5)
        for i, (sx, sy) in enumerate(((820, 830), (900, 900), (760, 900))):
            estrella(d, sx, sy, 34 * k * (1 + .2 * math.sin(T * 10 + i)), (255, 240, 150), int(255 * fa))
        if fa > 0:
            d.text((830, 700), "41 AÑOS", font=font("Bangers-Regular.ttf", 92 * max(k, .1)), fill=(255, 226, 90, int(255 * fa)), anchor="mm", stroke_width=6, stroke_fill=(60, 30, 50, int(255 * fa)))
    # 9 meses: gota de sudor anime + texto rojo
    t9 = EV["9"]
    if T >= t9:
        k = back((T - t9) / .3)
        if T < EV["habla0"] + .3:
            gota(d, 790, 930 + 6 * math.sin(T * 6), max(k, .01))
            d.text((540, 760), "9 MESES SIN COBRAR", font=font("Bangers-Regular.ttf", 72 * max(k, .1)), fill=(255, 90, 90), anchor="mm", stroke_width=6, stroke_fill=(50, 20, 40))
    c.alpha_composite(R.VIG)
    R.draw_hud(c, T)
    R.draw_caption(c, T)
    return c.convert("RGB")

if __name__ == "__main__":
    if sys.argv[1:] and sys.argv[1] == "still":
        for tt in sys.argv[2:]: frame(T0 + float(tt)).save(os.path.join(CLUB, "tmp", f"an_{tt}.jpg"), quality=88)
    else:
        print(exportar(frame, "estilo_3_anime"))
