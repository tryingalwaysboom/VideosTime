"""Brazos y manos del protagonista vistos desde sus ojos (POV). Mano derecha por defecto; espejo para la izquierda.
Poses: linterna, palma, pinza (sujetar papel), llave."""
import math
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter
from art import font, F_ANTON

SK = (226, 176, 140); SK_D = (176, 120, 92); SK_L = (246, 204, 170); NAIL = (240, 200, 186)
MANGA = (46, 52, 66); MANGA_D = (30, 34, 44); MANGA_L = (68, 76, 96)
Q = 2   # supermuestreo

def _cap(d, pts, w, fill, out=None, ow=6):
    if out:
        d.line(pts, fill=out, width=int(w + ow), joint="curve")
        for x, y in (pts[0], pts[-1]): r = (w + ow) / 2; d.ellipse((x - r, y - r, x + r, y + r), fill=out)
    d.line(pts, fill=fill, width=int(w), joint="curve")
    for x, y in (pts[0], pts[-1]): r = w / 2; d.ellipse((x - r, y - r, x + r, y + r), fill=fill)

def _dedo(d, x, y, ang, segs, w, curl, uña=True):
    pts = [(x, y)]; a = ang
    for L, c in zip(segs, curl):
        a += math.radians(c); x += L * math.sin(a); y -= L * math.cos(a); pts.append((x, y))
    pts = [(px * Q, py * Q) for px, py in pts]
    _cap(ImageDraw.Draw(d), pts, w * Q, SK, SK_D, 7 * Q)
    dd = ImageDraw.Draw(d)
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):   # luz en el dorso del dedo
        dd.line(((x0 - w * .18 * Q, y0), (x1 - w * .18 * Q, y1)), fill=SK_L, width=int(w * .22 * Q))
    for (px, py) in pts[1:-1]:   # pliegues de nudillo
        dd.arc((px - w * .32 * Q, py - w * .2 * Q, px + w * .32 * Q, py + w * .2 * Q), 200, 340, fill=SK_D, width=int(2.4 * Q))
    if uña and sum(curl[1:]) < 60:
        tx, ty = pts[-1]; px, py = pts[-2]; a = math.atan2(ty - py, tx - px)
        cx, cy = tx - math.cos(a) * w * .32 * Q, ty - math.sin(a) * w * .32 * Q
        dd.ellipse((cx - w * .3 * Q, cy - w * .3 * Q, cx + w * .3 * Q, cy + w * .3 * Q), fill=NAIL, outline=SK_D, width=Q * 2)

def _manga(d, sx, sy, w, L, ang):
    a = math.radians(ang); dx, dy = math.sin(a), math.cos(a)
    p0 = (sx - w / 2 * dy, sy - w / 2 * dx * -1); p1 = (sx + w / 2 * dy, sy + w / 2 * -dx * -1)
    pts = [(sx - w / 2, sy), (sx + w / 2, sy), (sx + w * .62 - L * dx, sy + L * dy), (sx - w * .62 - L * dx, sy + L * dy)]
    d.polygon([(x * Q, y * Q) for x, y in pts], fill=MANGA, outline=MANGA_D, width=4 * Q)
    for k in range(1, 5):   # pliegues
        t = k / 5; ya = sy + L * dy * t
        d.line(((sx - w * .5 - L * dx * t) * Q, ya * Q, (sx + w * .1 - L * dx * t) * Q, (ya + 30) * Q), fill=MANGA_D, width=5 * Q)
    d.line(((sx + w * .3) * Q, sy * Q, (sx + w * .45 - L * dx) * Q, (sy + L * dy) * Q), fill=MANGA_L, width=8 * Q)
    d.rounded_rectangle(((sx - w * .56) * Q, (sy - 10) * Q, (sx + w * .56) * Q, (sy + 40) * Q), 16 * Q, fill=MANGA_D)   # puño de la sudadera

@lru_cache(None)
def mano(pose, lado="d", s=1.0):
    """Devuelve (imagen RGBA, (ax, ay)) — ax, ay: punto de anclaje (punta de la linterna / centro de la palma)."""
    Wc, Hc = 700, 1100; im = Image.new("RGBA", (Wc * Q, Hc * Q), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    wx, wy = 330, 640   # muñeca
    _manga(d, wx, wy + 30, 250, 520, 8)
    anc = (wx, wy - 200)
    # palma (dorso)
    pw, ph = 236, 200
    palm = [(wx - pw / 2, wy), (wx - pw / 2 - 12, wy - ph * .6), (wx - pw / 2 + 6, wy - ph), (wx + pw / 2 - 4, wy - ph - 8), (wx + pw / 2 + 10, wy - ph * .55), (wx + pw / 2, wy)]
    d.polygon([((wx - pw * .46) * Q, (wy - 40) * Q), ((wx + pw * .46) * Q, (wy - 40) * Q), ((wx + pw * .44) * Q, (wy + 40) * Q), ((wx - pw * .44) * Q, (wy + 40) * Q)], fill=SK, outline=SK_D, width=6 * Q)
    d.polygon([(x * Q, y * Q) for x, y in palm], fill=SK, outline=SK_D, width=6 * Q)
    for k in range(4):   # tendones del dorso
        x = wx - 66 + k * 44; d.line((x * Q, (wy - 30) * Q, (x + (k - 1.5) * 8) * Q, (wy - ph + 20) * Q), fill=SK_D + (110,), width=4 * Q)
    hl = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(hl).ellipse(((wx - 80) * Q, (wy - ph + 30) * Q, (wx + 30) * Q, (wy - 50) * Q), fill=SK_L + (110,))
    pm = Image.new("L", im.size, 0); ImageDraw.Draw(pm).polygon([(x * Q, y * Q) for x, y in palm], fill=255)
    hl2 = Image.new("RGBA", im.size, (0, 0, 0, 0)); hl2.paste(hl.filter(ImageFilter.GaussianBlur(20 * Q)), (0, 0), pm); im.alpha_composite(hl2); d = ImageDraw.Draw(im)
    xs = [wx - 84, wx - 28, wx + 28, wx + 82]; segs = [(74, 52, 40), (82, 58, 44), (78, 54, 42), (62, 42, 34)]; ws = [52, 54, 52, 46]
    if pose in ("linterna", "llave"): curls = [(0, 120, 0), (0, 120, 0), (0, 120, 0), (0, 120, 0)]; angs = [-6, -2, 2, 6]; segs = [(56, 26, 1), (60, 28, 1), (58, 26, 1), (48, 22, 1)]
    elif pose == "palma": curls = [(-12, 6, 4), (-4, 6, 4), (4, 6, 4), (14, 6, 4)]; angs = [-12, -4, 4, 14]
    elif pose == "pinza": curls = [(-6, 70, 60), (-2, 76, 60), (2, 76, 60), (6, 70, 56)]; angs = [-6, -2, 2, 6]
    order = range(4)
    for i in order:
        _dedo(im, xs[i], wy - ph + 10 - (6 if i in (1, 2) else 0), math.radians(angs[i]), segs[i], ws[i], curls[i], uña=pose == "palma")
    d = ImageDraw.Draw(im)
    for i in range(4):   # nudillos
        x = xs[i]; y = wy - ph + 6; d.ellipse(((x - 18) * Q, (y - 10) * Q, (x + 18) * Q, (y + 10) * Q), fill=SK_L)
    # pulgar
    if pose == "pinza": _dedo(im, wx - 100, wy - 60, math.radians(-30), (80, 70, 58), 50, (0, 16, 10), uña=True)
    elif pose == "palma": _dedo(im, wx - 100, wy - 50, math.radians(-62), (80, 64, 50), 50, (0, 10, 8), uña=True)
    else: _dedo(im, wx - 112, wy - 60, math.radians(40), (70, 60), 54, (0, 30), uña=True)
    if pose == "linterna":
        d = ImageDraw.Draw(im); bx, by = wx - 30, wy - ph - 20
        d.polygon([((bx - 40) * Q, (by + 40) * Q), ((bx + 40) * Q, (by + 40) * Q), ((bx + 30) * Q, (by - 170) * Q), ((bx - 30) * Q, (by - 170) * Q)], fill=(44, 44, 52), outline=(16, 16, 20), width=4 * Q)
        for k in range(5): yk = by - 10 - k * 22; d.line(((bx - 36) * Q, yk * Q, (bx + 36) * Q, yk * Q), fill=(28, 28, 34), width=3 * Q)
        d.line(((bx - 16) * Q, (by + 30) * Q, (bx - 13) * Q, (by - 160) * Q), fill=(100, 100, 112), width=6 * Q)
        d.ellipse(((bx - 48) * Q, (by - 200) * Q, (bx + 48) * Q, (by - 150) * Q), fill=(76, 76, 86), outline=(20, 20, 24), width=4 * Q)
        d.ellipse(((bx - 38) * Q, (by - 194) * Q, (bx + 38) * Q, (by - 158) * Q), fill=(255, 250, 220))
        _dedo(im, wx - 112, wy - 60, math.radians(40), (70, 60), 54, (0, 30), uña=True)   # el pulgar por delante
        anc = (bx, by - 176)
    if pose == "llave":   # llave antigua entre pulgar e índice
        d = ImageDraw.Draw(im); kx, ky = wx - 100, wy - 230
        d.line(((kx) * Q, (ky + 40) * Q, (kx - 40) * Q, (ky - 160) * Q), fill=(176, 144, 70), width=18 * Q)
        d.ellipse(((kx - 80) * Q, (ky - 240) * Q, (kx + 0) * Q, (ky - 150) * Q), outline=(176, 144, 70), width=16 * Q)
        d.rectangle(((kx - 6) * Q, (ky + 10) * Q, (kx + 30) * Q, (ky + 26) * Q), fill=(176, 144, 70))
        d.rounded_rectangle(((kx - 120) * Q, (ky - 140) * Q, (kx - 66) * Q, (ky - 100) * Q), 8 * Q, fill=(200, 190, 150))
        d.text(((kx - 93) * Q, (ky - 120) * Q), "13", font=font(F_ANTON, 30 * Q), fill=(60, 40, 20), anchor="mm")
        anc = (kx - 40, ky - 200)
    im = im.filter(ImageFilter.GaussianBlur(.6 * Q)).resize((int(Wc * s), int(Hc * s)), Image.LANCZOS)
    ax, ay = anc[0] * s, anc[1] * s
    if lado == "i": im = im.transpose(Image.FLIP_LEFT_RIGHT); ax = Wc * s - ax
    return im, (ax, ay)

def poner(c, pose, x, y, lado="d", s=1.0, rot=0.0, luz=1.0):
    """Coloca la mano con la muñeca en (x, y) del fotograma. Devuelve el punto de anclaje en el fotograma."""
    im, (ax, ay) = mano(pose, lado, s)
    if luz < 1:
        dark = Image.new("RGBA", im.size, (6, 6, 16, int(255 * (1 - luz)))); m = im.split()[3]
        dk = Image.new("RGBA", im.size, (0, 0, 0, 0)); dk.paste(dark, (0, 0), m); im = Image.alpha_composite(im, dk)
    wx, wy = 330 * s, 640 * s
    if lado == "i": wx = im.width - wx
    if rot:
        im2 = im.rotate(rot, center=(wx, wy), resample=Image.BICUBIC)
        r = math.radians(-rot); dx, dy = ax - wx, ay - wy
        ax, ay = wx + dx * math.cos(r) - dy * math.sin(r), wy + dx * math.sin(r) + dy * math.cos(r); im = im2
    c.alpha_composite(im, (int(x - wx), int(y - wy)))
    return (x - wx + ax, y - wy + ay)
