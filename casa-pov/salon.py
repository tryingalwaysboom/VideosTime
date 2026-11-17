"""El salón de "La casa de 1 dólar" (de día), con estados para la reforma:
paredes: vieja / salvia / noche · suelo: moqueta / parquet_sucio / parquet_lijado / parquet_brillo · sábanas sí/no.
Las texturas planas se proyectan en perspectiva (un punto de fuga) sobre suelo y paredes."""
import math, random
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import art as A
from art import PW, PH, lerp, font, F_ANTON

BACK = (340, 700, 956, 1260)                      # pared del fondo
FL_NEAR = ((-420, PH), (PW + 420, PH))             # esquinas cercanas del suelo (fuera de cuadro)
CE_NEAR = ((-420, -300), (PW + 420, -300))

def coeffs(dst, src):
    """Coeficientes de Image.PERSPECTIVE que llevan el cuadrilátero dst (salida) al src (textura)."""
    m = []
    for (x, y), (u, v) in zip(dst, src):
        m.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); m.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    A_ = np.array(m, float); b = np.array([p for uv in src for p in uv], float)
    return np.linalg.solve(A_, b).tolist()

def warp(tex, quad):
    """Proyecta tex (rectangular) en quad = [TL, TR, BR, BL] de la plancha."""
    w, h = tex.size
    out = tex.transform((PW, PH), Image.PERSPECTIVE, coeffs(quad, [(0, 0), (w, 0), (w, h), (0, h)]), Image.BILINEAR)
    m = Image.new("L", (PW, PH), 0); ImageDraw.Draw(m).polygon(quad, fill=255)
    out.putalpha(Image.fromarray(np.minimum(np.asarray(out.split()[3]), np.asarray(m))))
    return out

def floor_quad():
    x0, y0, x1, y1 = BACK; return [(x0, y1), (x1, y1), FL_NEAR[1], FL_NEAR[0]]
def wall_quads():
    x0, y0, x1, y1 = BACK
    L = [CE_NEAR[0], (x0, y0), (x0, y1), FL_NEAR[0]]; R = [(x1, y0), CE_NEAR[1], FL_NEAR[1], (x1, y1)]
    return L, R
def ceil_quad():
    x0, y0, x1, y1 = BACK; return [CE_NEAR[0], CE_NEAR[1], (x1, y0), (x0, y0)]

def noise(w, h, amt, seed, blur=0):
    rng = np.random.default_rng(seed); n = rng.normal(0, amt, (h, w))
    im = Image.fromarray(np.clip(128 + n, 0, 255).astype(np.uint8), "L")
    return im.filter(ImageFilter.GaussianBlur(blur)) if blur else im

def tint(base, nz, k=1.0):
    a = np.asarray(nz, np.float32)[..., None] - 128
    return Image.fromarray(np.clip(np.array(base, np.float32)[None, None] + a * k, 0, 255).astype(np.uint8), "RGB").convert("RGBA")

# ------------------------------------------------------------------ texturas del suelo (1600x1600 = suelo visto desde arriba)
TS = 1600
@lru_cache(None)
def tex_moqueta():
    im = tint((88, 92, 58), noise(TS, TS, 22, 1, 1.2), .8); d = ImageDraw.Draw(im); rng = random.Random(2)
    for _ in range(26):   # manchas
        x, y, r = rng.uniform(0, TS), rng.uniform(0, TS), rng.uniform(40, 160)
        st = Image.new("RGBA", (TS, TS), (0, 0, 0, 0)); ImageDraw.Draw(st).ellipse((x - r, y - r * .7, x + r, y + r * .7), fill=(40, 34, 20, 120))
        im.alpha_composite(st.filter(ImageFilter.GaussianBlur(18)))
    st = Image.new("RGBA", (TS, TS), (0, 0, 0, 0)); ImageDraw.Draw(st).rectangle((TS * .38, 0, TS * .62, TS), fill=(120, 116, 80, 70))   # camino gastado
    im.alpha_composite(st.filter(ImageFilter.GaussianBlur(60)))
    return im

def _parquet(base, var, grain, seed, gloss=False):
    im = Image.new("RGBA", (TS, TS), (40, 28, 18, 255)); d = ImageDraw.Draw(im); rng = random.Random(seed)
    Wd = 80   # tablas largas a lo largo del salón, con juntas escalonadas
    for col in range(TS // Wd + 1):
        y = -rng.uniform(0, 600)
        while y < TS:
            L = rng.uniform(380, 700); t = rng.uniform(-var, var); c = tuple(int(max(0, min(255, v + t))) for v in base)
            d.rectangle((col * Wd + 2, y + 2, col * Wd + Wd - 2, y + L - 2), fill=c)
            for _ in range(5):   # vetas
                gx = col * Wd + rng.uniform(8, Wd - 8); d.line([(gx + 4 * math.sin(v / 40 + gx), v) for v in np.linspace(y + 6, y + L - 6, 14)], fill=tuple(int(max(0, x - 22)) for x in c), width=2)
            if rng.random() < .3:
                kx, ky = col * Wd + rng.uniform(20, Wd - 20), y + rng.uniform(40, L - 40); d.ellipse((kx - 9, ky - 14, kx + 9, ky + 14), fill=tuple(int(max(0, x - 40)) for x in c))
            y += L
    g = tint((128, 128, 128), noise(TS, TS, grain, seed + 1, .6)).split()[0]
    a = np.asarray(im, np.float32); gg = (np.asarray(g, np.float32) - 128)[..., None] * .5
    a[..., :3] = np.clip(a[..., :3] + gg, 0, 255); im = Image.fromarray(a.astype(np.uint8), "RGBA")
    if gloss:   # reflejos de la ventana sobre el barniz
        sh = Image.new("RGBA", (TS, TS), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
        sd.polygon([(0, 300), (TS, 700), (TS, 950), (0, 520)], fill=(255, 240, 210, 70)); sd.polygon([(0, 700), (TS, 1100), (TS, 1180), (0, 780)], fill=(255, 240, 210, 50))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(40)))
    return im

@lru_cache(None)
def tex_parquet_sucio():
    im = _parquet((118, 96, 74), 16, 30, 5)
    dirt = tint((70, 62, 50), noise(TS, TS, 30, 9, 6)); dirt.putalpha(140); im.alpha_composite(dirt)
    return im
@lru_cache(None)
def tex_parquet_lijado(): return _parquet((214, 176, 128), 14, 22, 5)
@lru_cache(None)
def tex_parquet_brillo(): return _parquet((196, 124, 62), 22, 26, 5, gloss=True)

# ------------------------------------------------------------------ texturas de pared
def tex_pared(estado, w=1000, h=1000, seed=0):
    if estado == "vieja":
        im = tint((150, 128, 104), noise(w, h, 10, seed, 2)); d = ImageDraw.Draw(im); rng = random.Random(seed)
        for x in range(0, w, 70):
            d.rectangle((x, 0, x + 26, h), fill=(140, 116, 92))
            for y in range(20, h, 90): d.ellipse((x + 38, y, x + 60, y + 22), fill=(128, 104, 82))
        for _ in range(7):   # papel despegado y manchas de humedad
            x, y = rng.uniform(0, w), rng.uniform(0, h * .7); ww, hh = rng.uniform(40, 120), rng.uniform(120, 300)
            d.polygon([(x, y), (x + ww, y), (x + ww * .8, y + hh), (x + ww * .2, y + hh * .8)], fill=(196, 182, 160))
            st = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ImageDraw.Draw(st).ellipse((x - 120, y + 100, x + 140, y + 420), fill=(80, 64, 44, 90)); im.alpha_composite(st.filter(ImageFilter.GaussianBlur(30)))
        return im
    col = {"salvia": (150, 172, 138), "noche": (38, 52, 84)}[estado]
    return tint(col, noise(w, h, 5, seed, 3))

# ------------------------------------------------------------------ objetos (en la pared del fondo, frontales)
def chimenea(d, cx, by):
    d.rectangle((cx - 190, by - 330, cx + 190, by), fill=(150, 80, 60))
    for r in range(15):
        y = by - 330 + r * 22
        for k in range(10):
            x = cx - 190 + k * 40 + (r % 2) * 20
            if x + 38 <= cx - 190 or x + 2 >= cx + 190: continue
            d.rectangle((max(cx - 190, x + 2), y + 2, min(cx + 190, x + 38), y + 20), fill=(160 + (r * 7 + k * 5) % 24, 86, 64))
    d.rectangle((cx - 110, by - 200, cx + 110, by), fill=(20, 14, 12)); d.ellipse((cx - 110, by - 260, cx + 110, by - 140), fill=(20, 14, 12))
    d.rectangle((cx - 230, by - 350, cx + 230, by - 318), fill=(232, 220, 196)); d.rectangle((cx - 214, by - 318, cx + 214, by - 306), fill=(200, 188, 166))
    for x in (-60, 0, 60): d.rectangle((cx + x - 8, by - 40, cx + x + 8, by), fill=(60, 40, 30))   # leña

def ventana_luz(im, d, q):
    """Ventana en la pared izquierda (q en perspectiva) + haces de sol al suelo."""
    d.polygon(q, fill=(232, 222, 200)); inner = [A.quad_pt(q, .08, .06), A.quad_pt(q, .92, .06), A.quad_pt(q, .92, .94), A.quad_pt(q, .08, .94)]
    d.polygon(inner, fill=(198, 226, 236))
    for u in (.5,): d.line([A.quad_pt(inner, u, 0), A.quad_pt(inner, u, 1)], fill=(232, 222, 200), width=10)
    d.line([A.quad_pt(inner, 0, .5), A.quad_pt(inner, 1, .5)], fill=(232, 222, 200), width=10)
    tree = [A.quad_pt(inner, .1, .7), A.quad_pt(inner, .4, .3), A.quad_pt(inner, .8, .6), A.quad_pt(inner, .9, 1), A.quad_pt(inner, .1, 1)]
    d.polygon(tree, fill=(150, 196, 150))
    sun = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    ImageDraw.Draw(sun).polygon([A.quad_pt(inner, 1, 0), A.quad_pt(inner, 1, 1), (900, 2100), (1250, 1500)], fill=(255, 236, 180, 70))
    im.alpha_composite(sun.filter(ImageFilter.GaussianBlur(30)))

def sofa(d, x0, y1, w, h, col, viejo=True):
    dk = tuple(int(c * .78) for c in col)
    d.rounded_rectangle((x0, y1 - h, x0 + w, y1 - h * .35), 30, fill=dk)                    # respaldo
    d.rounded_rectangle((x0 + 30, y1 - h * .5, x0 + w - 30, y1 - h * .12), 20, fill=col)    # asiento
    for k in range(3):
        cx = x0 + 30 + (w - 60) * (k + .5) / 3; d.rounded_rectangle((cx - (w - 60) / 6 + 6, y1 - h * .52, cx + (w - 60) / 6 - 6, y1 - h * .3), 18, fill=tuple(min(255, int(c * 1.08)) for c in col))
    d.rounded_rectangle((x0 - 10, y1 - h * .7, x0 + 60, y1 - h * .1), 26, fill=dk); d.rounded_rectangle((x0 + w - 60, y1 - h * .7, x0 + w + 10, y1 - h * .1), 26, fill=dk)
    for fx in (x0 + 20, x0 + w - 40): d.rectangle((fx, y1 - h * .12, fx + 20, y1), fill=(70, 46, 30))
    if viejo:
        d.line((x0 + w * .3, y1 - h * .45, x0 + w * .38, y1 - h * .3), fill=(200, 190, 170), width=6); d.ellipse((x0 + w * .6, y1 - h * .9, x0 + w * .7, y1 - h * .78), fill=(dk[0] - 20, dk[1] - 20, dk[2] - 20))

def butaca(d, cx, y1, s, col):
    dk = tuple(int(c * .78) for c in col); w, h = 300 * s, 360 * s
    d.rounded_rectangle((cx - w / 2 + 20 * s, y1 - h, cx + w / 2 - 20 * s, y1 - h * .4), 60 * s, fill=dk)
    d.rounded_rectangle((cx - w / 2 + 40 * s, y1 - h * .5, cx + w / 2 - 40 * s, y1 - h * .15), 24 * s, fill=col)
    d.rounded_rectangle((cx - w / 2, y1 - h * .66, cx - w / 2 + 70 * s, y1 - h * .1), 30 * s, fill=dk); d.rounded_rectangle((cx + w / 2 - 70 * s, y1 - h * .66, cx + w / 2, y1 - h * .1), 30 * s, fill=dk)
    for fx in (cx - w / 2 + 20 * s, cx + w / 2 - 40 * s): d.rectangle((fx, y1 - h * .1, fx + 20 * s, y1), fill=(70, 46, 30))

def sabana_sobre(im, box, seed, alpha=255, dy=0, dx=0, rot=0):
    x0, y0, x1, y1 = box; rng = random.Random(seed)
    lay = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); sd = ImageDraw.Draw(lay)
    pts = [(x0 - 20, y1 + 10), (x0 - 10, y0 + (y1 - y0) * .3), (x0 + (x1 - x0) * .2, y0 - 10), (x1 - (x1 - x0) * .25, y0 - 20), (x1 + 10, y0 + (y1 - y0) * .25), (x1 + 25, y1 + 10)]
    sd.polygon(pts, fill=(226, 224, 216, alpha))
    for _ in range(8):
        x = rng.uniform(x0 + 10, x1 - 10); sd.line([(x + 8 * math.sin(v), lerp(y0, y1, v / 3)) for v in np.linspace(0, 3, 10)], fill=(190, 188, 182, alpha), width=8)
    if dx or dy or rot:
        lay = lay.rotate(rot, center=((x0 + x1) / 2, (y0 + y1) / 2), resample=Image.BICUBIC, translate=(dx, dy))
    im.alpha_composite(lay)

@lru_cache(None)
def salon(paredes="vieja", suelo="moqueta", sabanas=True, muebles=True):
    im = Image.new("RGBA", (PW, PH), (0, 0, 0, 255))
    L, R = wall_quads()
    im.alpha_composite(warp(tex_pared("vieja" if paredes == "vieja" else paredes, seed=1).convert("RGBA"), ceil_quad()) if False else Image.new("RGBA", (PW, PH), (0, 0, 0, 0)))
    ce = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); ImageDraw.Draw(ce).polygon(ceil_quad(), fill=(214, 206, 192) if paredes != "vieja" else (170, 160, 146)); im.alpha_composite(ce)
    wtex = tex_pared(paredes, seed=3)
    im.alpha_composite(warp(wtex, L)); im.alpha_composite(warp(wtex, R))
    x0, y0, x1, y1 = BACK
    back = tex_pared(paredes, x1 - x0, y1 - y0, seed=4); im.alpha_composite(back, (x0, y0))
    # sombras de esquina
    sh = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    for q in (L, R): sd.polygon(q, fill=(0, 0, 0, 0))
    sd.line([(x0, y0), (x0, y1)], fill=(0, 0, 0, 90), width=18); sd.line([(x1, y0), (x1, y1)], fill=(0, 0, 0, 90), width=18)
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    # suelo
    ft = {"moqueta": tex_moqueta, "parquet_sucio": tex_parquet_sucio, "parquet_lijado": tex_parquet_lijado, "parquet_brillo": tex_parquet_brillo}[suelo]()
    im.alpha_composite(warp(ft, floor_quad()))
    d = ImageDraw.Draw(im)
    # rodapié
    d.rectangle((x0, y1 - 26, x1, y1), fill=(236, 228, 214) if paredes != "vieja" else (120, 100, 80))
    for q, a, b in ((L, (x0, y1), FL_NEAR[0]), (R, (x1, y1), FL_NEAR[1])):
        d.polygon([a, b, (b[0], b[1] - 60), (a[0], a[1] - 26)], fill=(236, 228, 214) if paredes != "vieja" else (120, 100, 80))
    # ventana pared izquierda
    win = [A.quad_pt(L, .45, .3), A.quad_pt(L, .78, .33), A.quad_pt(L, .78, .62), A.quad_pt(L, .45, .66)]
    ventana_luz(im, d, win); d = ImageDraw.Draw(im)
    # chimenea y cuadro
    chimenea(d, (x0 + x1) / 2, y1)
    fr = ((x0 + x1) / 2 - 130, y0 + 120, (x0 + x1) / 2 + 130, y0 + 300)
    d.rectangle(fr, fill=(150, 116, 60)); d.rectangle((fr[0] + 16, fr[1] + 16, fr[2] - 16, fr[3] - 16), fill=(120, 150, 170) if paredes != "vieja" else (90, 96, 100))
    d.polygon([(fr[0] + 16, fr[3] - 16), (fr[0] + 90, fr[1] + 70), (fr[0] + 150, fr[3] - 40), (fr[0] + 190, fr[1] + 90), (fr[2] - 16, fr[3] - 16)], fill=(80, 110, 90))
    if muebles:
        sofa(d, x1 - 360, y1 + 4, 330, 260, (150, 70, 70) if paredes == "vieja" else (196, 160, 120), viejo=paredes == "vieja")
        butaca(d, 300, 1640, 1.25, (120, 104, 70) if paredes == "vieja" else (210, 180, 140))
        d.polygon([(560, 1460), (840, 1460), (880, 1520), (520, 1520)], fill=(110, 76, 48)); d.rectangle((520, 1520, 880, 1540), fill=(86, 58, 36))
        for fx in (540, 850): d.rectangle((fx, 1540, fx + 16, 1610), fill=(86, 58, 36))
        if sabanas:
            sabana_sobre(im, (x1 - 370, y1 - 262, x1 - 20, y1 + 4), 1)
            sabana_sobre(im, (300 - 190, 1640 - 450, 300 + 190, 1640), 2)
            sabana_sobre(im, (520, 1440, 880, 1610), 3)
    if paredes == "vieja":   # suciedad general, telarañas
        d = ImageDraw.Draw(im)
        for cx, cy, sx in ((0, 0, 1), (PW, 0, -1)):
            for a in range(0, 91, 15):
                r = math.radians(a); d.line((cx, cy, cx + sx * 300 * math.cos(r), cy + 300 * math.sin(r)), fill=(240, 240, 240, 90), width=2)
        im.alpha_composite(Image.new("RGBA", (PW, PH), (40, 30, 20, 50)))
    return A.add_grain(im, 5, 7)
