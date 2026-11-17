"""Brazos y manos del protagonista vistos desde sus ojos (POV), en estilo plano: formas redondeadas sin contorno,
dedos juntos con líneas finas de separación y una sombra lateral suave. Mano derecha por defecto; espejo para la izquierda.
Poses: palma, pinza (= palma), linterna, llave."""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art import font, F_ANTON

SK = (242, 190, 132); SK_D = (218, 152, 98); LINE = (196, 128, 80)
MANGA = (66, 68, 80); MANGA_L = (88, 90, 104); MANGA_D = (50, 52, 62)
Q = 2

def cap(d, p0, p1, w, fill):
    d.line((p0[0] * Q, p0[1] * Q, p1[0] * Q, p1[1] * Q), fill=fill, width=int(w * Q))
    for x, y in (p0, p1): r = w / 2; d.ellipse(((x - r) * Q, (y - r) * Q, (x + r) * Q, (y + r) * Q), fill=fill)

def tip(x, y, ang, L): a = math.radians(ang); return (x + L * math.sin(a), y - L * math.cos(a))

@lru_cache(None)
def mano(pose, lado="d", s=1.0):
    Wc, Hc = 700, 1200; size = (Wc * Q, Hc * Q)
    wx, wy = 330, 660
    arm = Image.new("RGBA", size, (0, 0, 0, 0)); ad = ImageDraw.Draw(arm)
    pts = [(wx - 128, wy - 10), (wx + 128, wy - 10), (wx + 160, wy + 560), (wx - 150, wy + 560)]
    ad.polygon([(x * Q, y * Q) for x, y in pts], fill=MANGA)
    ad.polygon([((wx + 70) * Q, (wy - 10) * Q), ((wx + 128) * Q, (wy - 10) * Q), ((wx + 160) * Q, (wy + 560) * Q), ((wx + 96) * Q, (wy + 560) * Q)], fill=MANGA_L)
    ad.rounded_rectangle(((wx - 134) * Q, (wy - 26) * Q, (wx + 134) * Q, (wy + 30) * Q), 28 * Q, fill=MANGA_D)
    h = Image.new("RGBA", size, (0, 0, 0, 0)); d = ImageDraw.Draw(h)
    lines = []; anc = (wx, wy - 330); lint = False
    if pose in ("palma", "pinza"):
        d.rounded_rectangle(((wx - 118) * Q, (wy - 230) * Q, (wx + 118) * Q, (wy + 10) * Q), 80 * Q, fill=SK)
        xs = [-88, -30, 28, 84]; Ls = [175, 205, 192, 150]; angs = [-7, -2, 3, 9]; tips = []
        for x, L, a in zip(xs, Ls, angs):
            p0 = (wx + x, wy - 190); p1 = tip(*p0, a, L); cap(d, p0, p1, 64, SK); tips.append((p0, p1))
        for (a0, a1), (b0, b1) in zip(tips[:-1], tips[1:]):   # líneas entre dedos
            m0 = ((a0[0] + b0[0]) / 2, (a0[1] + b0[1]) / 2 - 10); L = min(math.dist(a0, a1), math.dist(b0, b1)) - 38
            mt = ((a1[0] + b1[0]) / 2, (a1[1] + b1[1]) / 2); u = L / math.dist(m0, mt)
            lines.append((m0, (m0[0] + (mt[0] - m0[0]) * u, m0[1] + (mt[1] - m0[1]) * u)))
        th0 = (wx - 112, wy - 70); th1 = tip(*th0, -52, 130); cap(d, th0, th1, 68, SK)
        lines.append(((wx - 100, wy - 40), (wx - 70, wy - 130)))
    else:   # puño (linterna / llave)
        if pose == "linterna":
            lint = True
            d.rounded_rectangle(((wx - 44) * Q, (wy - 470) * Q, (wx + 44) * Q, (wy - 150) * Q), 18 * Q, fill=(112, 114, 128))
        d.rounded_rectangle(((wx - 130) * Q, (wy - 250) * Q, (wx + 130) * Q, (wy + 10) * Q), 90 * Q, fill=SK)
        for i, x in enumerate((-96, -34, 30, 92)):
            d.ellipse(((wx + x - 40) * Q, (wy - 278) * Q, (wx + x + 40) * Q, (wy - 196) * Q), fill=SK)
            if i < 3: lines.append(((wx + x + 31, wy - 262), (wx + x + 31, wy - 170)))
        cap(d, (wx - 128, wy - 90), (wx - 20, wy - 230), 70, SK)
        anc = (wx, wy - 470)
    a = np.asarray(h.split()[3]).astype(np.int16)   # sombra lateral
    sk = (np.asarray(h)[..., 0] > 200) & (a > 0)
    sh = np.clip(a - np.roll(np.roll(a, -22 * Q, axis=1), -8 * Q, axis=0), 0, 255) * sk
    shade = Image.new("RGBA", size, SK_D + (0,)); shade.putalpha(Image.fromarray(sh.astype(np.uint8)).filter(ImageFilter.GaussianBlur(3 * Q)))
    h.alpha_composite(shade); d = ImageDraw.Draw(h)
    for p0, p1 in lines: d.line((p0[0] * Q, p0[1] * Q, p1[0] * Q, p1[1] * Q), fill=LINE, width=5 * Q)
    if pose not in ("palma", "pinza"):
        d.line(((wx - 98) * Q, (wy - 120) * Q, (wx - 10) * Q, (wy - 236) * Q), fill=SK_D, width=10 * Q)
    if lint:
        d.rectangle(((wx + 12) * Q, (wy - 460) * Q, (wx + 26) * Q, (wy - 280) * Q), fill=(150, 152, 166))
        d.ellipse(((wx - 58) * Q, (wy - 500) * Q, (wx + 58) * Q, (wy - 448) * Q), fill=(80, 82, 94))
        d.ellipse(((wx - 46) * Q, (wy - 494) * Q, (wx + 46) * Q, (wy - 456) * Q), fill=(255, 248, 210))
    if pose == "llave":
        kx, ky = wx - 30, wy - 250
        d.rectangle(((kx - 10) * Q, (ky - 190) * Q, (kx + 10) * Q, (ky + 10) * Q), fill=(196, 160, 72))
        d.ellipse(((kx - 54) * Q, (ky - 290) * Q, (kx + 54) * Q, (ky - 180) * Q), outline=(196, 160, 72), width=20 * Q)
        d.rectangle(((kx + 10) * Q, (ky - 40) * Q, (kx + 46) * Q, (ky - 22) * Q), fill=(196, 160, 72))
        d.rounded_rectangle(((kx + 60) * Q, (ky - 280) * Q, (kx + 140) * Q, (ky - 226) * Q), 10 * Q, fill=(232, 222, 186))
        d.text(((kx + 100) * Q, (ky - 253) * Q), "13", font=font(F_ANTON, 36 * Q), fill=(70, 46, 24), anchor="mm")
        cap(d, (wx - 128, wy - 90), (wx - 20, wy - 230), 70, SK)
        anc = (kx, ky - 240)
    im = Image.alpha_composite(arm, h).resize((int(Wc * s), int(Hc * s)), Image.LANCZOS)
    ax, ay = anc[0] * s, anc[1] * s
    if lado == "i": im = im.transpose(Image.FLIP_LEFT_RIGHT); ax = Wc * s - ax
    return im, (ax, ay)

def poner(c, pose, x, y, lado="d", s=1.0, rot=0.0, luz=1.0):
    """Coloca la mano con la muñeca en (x, y) del fotograma. Devuelve el punto de anclaje en el fotograma."""
    s = round(s * 1.15, 3); im, (ax, ay) = mano(pose, lado, s)
    if luz < 1:
        m = im.split()[3]; dk = Image.new("RGBA", im.size, (8, 8, 20, int(255 * (1 - luz)))); z = Image.new("RGBA", im.size, (0, 0, 0, 0)); z.paste(dk, (0, 0), m)
        im = Image.alpha_composite(im, z)
    wx, wy = 330 * s, 660 * s
    if lado == "i": wx = im.width - wx
    if rot:
        im2 = im.rotate(rot, center=(wx, wy), resample=Image.BICUBIC)
        r = math.radians(-rot); dx, dy = ax - wx, ay - wy
        ax, ay = wx + dx * math.cos(r) - dy * math.sin(r), wy + dx * math.sin(r) + dy * math.cos(r); im = im2
    c.alpha_composite(im, (int(x - wx), int(y - wy)))
    return (x - wx + ax, y - wy + ay)
