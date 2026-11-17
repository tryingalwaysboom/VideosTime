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


# ====================================================================================================
# CASA GRANDE EN 3D (v2): salón amplio con cocina, escalera, pasillo a baño y habitación.
# Todo se define en coordenadas 3D (X derecha, Y abajo, Z profundidad; ojo en 0,0,0) y se proyecta.
# ====================================================================================================
K2 = 2                       # supermuestreo
PLATE_K = K2                 # la plancha de la casa sale a este tamaño (2592x4608)
VPX, VPY, FOC = 648, 1040, 640
XL, XR, YC, YF, ZB = -2.8, 2.8, -1.65, 1.35, 8.0     # paredes, techo, suelo, fondo

def P(X, Y, Z): return ((VPX + X * FOC / Z) * K2, (VPY + Y * FOC / Z) * K2)
def Pp(X, Y, Z): return (VPX + X * FOC / Z, VPY + Y * FOC / Z)

class R3:
    def __init__(self, im): self.im = im; self.d = ImageDraw.Draw(im)
    def poly(self, pts3, fill, outline=None, w=2):
        self.d.polygon([P(*p) for p in pts3], fill=fill, outline=outline, width=w * K2 if outline else 0)
    def line(self, a, b, fill, w=2): self.d.line([P(*a), P(*b)], fill=fill, width=int(w * K2))
    def box(self, x0, x1, y0, y1, z0, z1, col, top=None, side=None):
        """Caja: cara frontal (z0), superior (y0) y la lateral que se ve según el lado."""
        dk = side or tuple(int(c * .72) for c in col); tp = top or tuple(min(255, int(c * 1.12)) for c in col)
        if (x0 + x1) / 2 > 0: self.poly([(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)], dk)
        else: self.poly([(x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0)], dk)
        if y0 > 0: self.poly([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], tp)
        self.poly([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], col)

def warp2(tex, quad3):
    q = [Pp(*p) for p in quad3]; w, h = tex.size
    q2 = [(x * K2, y * K2) for x, y in q]
    out = tex.transform((PW * K2, PH * K2), Image.PERSPECTIVE, coeffs(q2, [(0, 0), (w, 0), (w, h), (0, h)]), Image.BILINEAR)
    m = Image.new("L", (PW * K2, PH * K2), 0); ImageDraw.Draw(m).polygon(q2, fill=255)
    out.putalpha(Image.fromarray(np.minimum(np.asarray(out.split()[3]), np.asarray(m))))
    return out

ZN = .42   # plano cercano
# muebles (para sábanas y animaciones): nombre -> caja 3D
MUEBLES = {"sofa": (-2.6, -.7, .35, 1.35, 6.5, 7.4), "butaca": (.2, 1.3, .45, 1.35, 5.7, 6.5), "mesa": (-2.0, -.9, .95, 1.35, 5.2, 6.0)}

def box2d(name):
    x0, x1, y0, y1, z0, z1 = MUEBLES[name]
    pts = [Pp(x, y, z) for x in (x0, x1) for y in (y0 - .15, y1) for z in (z0, z1)]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))

@lru_cache(None)
def casa(paredes="vieja", suelo="moqueta", sabanas=True, muebles=True):
    S2 = (PW * K2, PH * K2); im = Image.new("RGBA", S2, (0, 0, 0, 255)); r = R3(im); rng = random.Random(4)
    vieja = paredes == "vieja"
    ceil = (176, 166, 150) if vieja else (226, 220, 206)
    # techo + vigas
    r.poly([(XL, YC, ZN), (XR, YC, ZN), (XR, YC, ZB), (XL, YC, ZB)], ceil)
    for z in (1.2, 2.2, 3.4, 4.8, 6.3, 7.6):
        r.box(XL, XR, YC, YC + .22, z, z + .25, (110, 78, 52) if vieja else (150, 110, 74))
    # paredes con textura
    wt = tex_pared(paredes, 1400, 700, seed=3)
    im.alpha_composite(warp2(wt, [(XL, YC, ZN), (XL, YC, ZB), (XL, YF, ZB), (XL, YF, ZN)]))
    im.alpha_composite(warp2(wt, [(XR, YC, ZB), (XR, YC, ZN), (XR, YF, ZN), (XR, YF, ZB)]))
    im.alpha_composite(warp2(tex_pared(paredes, 1000, 300, seed=4), [(XL, YC, ZB), (XR, YC, ZB), (XR, YF, ZB), (XL, YF, ZB)]))
    # suelo
    ft = {"moqueta": tex_moqueta, "parquet_sucio": tex_parquet_sucio, "parquet_lijado": tex_parquet_lijado, "parquet_brillo": tex_parquet_brillo}[suelo]()
    big = Image.new("RGBA", (TS, TS * 2)); big.paste(ft, (0, 0)); big.paste(ft, (0, TS))
    im.alpha_composite(warp2(big, [(XL, YF, ZB), (XR, YF, ZB), (XR, YF, ZN), (XL, YF, ZN)]))
    r = R3(im)
    # zócalos y molduras
    zc = (110, 86, 64) if vieja else (240, 234, 222)
    r.poly([(XL, YF - .14, ZN), (XL, YF - .14, ZB), (XL, YF, ZB), (XL, YF, ZN)], zc); r.poly([(XR, YF - .14, ZB), (XR, YF - .14, ZN), (XR, YF, ZN), (XR, YF, ZB)], zc)
    r.poly([(XL, YF - .14, ZB), (XR, YF - .14, ZB), (XR, YF, ZB), (XL, YF, ZB)], zc)
    for X in (XL, XR): r.line((X, YC + .02, ZN), (X, YC + .02, ZB), (200, 190, 170) if vieja else (250, 246, 236), 5)
    # ---------------- pared izquierda: ventanal + arco a la COCINA
    def ventana_izq(z0, z1, y0, y1):
        r.poly([(XL, y0 - .1, z0 - .1), (XL, y0 - .1, z1 + .1), (XL, y1 + .12, z1 + .1), (XL, y1 + .12, z0 - .1)], (236, 228, 210))
        r.poly([(XL, y0, z0), (XL, y0, z1), (XL, y1, z1), (XL, y1, z0)], (190, 222, 236))
        r.poly([(XL, (y0 + y1) / 2 + .1, z0), (XL, (y0 + y1) / 2 + .1, z1), (XL, y1, z1), (XL, y1, z0)], (150, 196, 150))
        for z in (z0 + (z1 - z0) / 3, z0 + 2 * (z1 - z0) / 3): r.line((XL, y0, z), (XL, y1, z), (236, 228, 210), 6)
        r.line((XL, (y0 + y1) / 2, z0), (XL, (y0 + y1) / 2, z1), (236, 228, 210), 6)
        if vieja:
            for k in range(3):
                zz = z0 + (z1 - z0) * (k + .5) / 3
                r.poly([(XL, y0 + .3 + k * .45, z0 - .05), (XL, y0 + .42 + k * .45, z1 + .05), (XL, y0 + .58 + k * .45, z1 + .05), (XL, y0 + .46 + k * .45, z0 - .05)], (120, 90, 60))
    ventana_izq(6.3, 7.6, -.75, .65)
    # arco de la cocina con la cocina dentro
    z0, z1, ya = 4.3, 5.9, -.85
    r.poly([(XL, ya - .12, z0 - .12), (XL, ya - .12, z1 + .12), (XL, YF, z1 + .12), (XL, YF, z0 - .12)], (230, 222, 204) if not vieja else (140, 120, 96))
    XK = -5.8
    r.poly([(XL, ya, z0), (XL, ya, z1), (XL, YF, z1), (XL, YF, z0)], (30, 26, 24))
    r.poly([(XK, ya, z0), (XK, ya, z1), (XK, YF, z1), (XK, YF, z0)], (200, 196, 180) if not vieja else (120, 112, 96))          # pared del fondo de la cocina (pared paralela a la izq)
    r.poly([(XL, YF, z0), (XL, YF, z1), (XK, YF, z1), (XK, YF, z0)], (160, 150, 136))                                              # suelo de baldosas
    for k in range(1, 8): x = XL + (XK - XL) * k / 8; r.line((x, YF, z0), (x, YF, z1), (130, 120, 108), 2)
    r.poly([(XL, ya, z1), (XK, ya, z1), (XK, YF, z1), (XL, YF, z1)], (186, 180, 166) if not vieja else (112, 104, 90))            # pared lateral de la cocina
    for k in range(5):   # muebles de cocina en el lateral (al fondo del arco)
        xa, xb = XL - .3 - k * .5, XL - .75 - k * .5
        r.poly([(xa, .45, z1 - .01), (xb, .45, z1 - .01), (xb, YF - .05, z1 - .01), (xa, YF - .05, z1 - .01)], (120, 150, 140) if not vieja else (110, 96, 76), (60, 60, 60), 1)
    r.poly([(XL - .25, .38, z1 - .02), (XK, .38, z1 - .02), (XK, .5, z1 - .02), (XL - .25, .5, z1 - .02)], (220, 216, 206))
    for k in range(5):
        xa, xb = XL - .3 - k * .5, XL - .75 - k * .5
        r.poly([(xa, -.75, z1 - .01), (xb, -.75, z1 - .01), (xb, -.15, z1 - .01), (xa, -.15, z1 - .01)], (120, 150, 140) if not vieja else (110, 96, 76), (60, 60, 60), 1)
    r.box(-5.4, -4.8, -.5, .38, z1 - .5, z1 - .02, (200, 200, 205))   # nevera
    # ---------------- pared del fondo: chimenea, cuadro y PASILLO (baño / habitación)
    cx = -.9
    r.box(cx - 1.0, cx + 1.0, -.05, YF, ZB - .35, ZB, (156, 84, 62))
    for row in range(10):
        y = -.05 + row * .14
        for k in range(8):
            xa = cx - 1.0 + k * .25 + (row % 2) * .125
            if xa + .23 > cx + 1.0: continue
            r.poly([(xa + .01, y + .01, ZB - .35), (xa + .23, y + .01, ZB - .35), (xa + .23, y + .13, ZB - .35), (xa + .01, y + .13, ZB - .35)], (166 + (row * 7 + k * 5) % 22, 90, 66))
    r.poly([(cx - .55, .45, ZB - .36), (cx + .55, .45, ZB - .36), (cx + .55, YF, ZB - .36), (cx - .55, YF, ZB - .36)], (22, 16, 14))
    r.box(cx - 1.2, cx + 1.2, -.18, -.05, ZB - .5, ZB, (236, 226, 202))
    r.poly([(cx - .7, -1.35, ZB - .01), (cx + .7, -1.35, ZB - .01), (cx + .7, -.45, ZB - .01), (cx - .7, -.45, ZB - .01)], (150, 116, 60))
    r.poly([(cx - .6, -1.26, ZB - .02), (cx + .6, -1.26, ZB - .02), (cx + .6, -.54, ZB - .02), (cx - .6, -.54, ZB - .02)], (120, 150, 170) if not vieja else (90, 96, 100))
    r.poly([(cx - .6, -.54, ZB - .02), (cx - .2, -1.0, ZB - .02), (cx + .1, -.7, ZB - .02), (cx + .35, -1.1, ZB - .02), (cx + .6, -.54, ZB - .02)], (80, 110, 90))
    # pasillo (abertura en la pared del fondo) con puertas BAÑO y HABITACIÓN
    hx0, hx1, hy = .7, 1.9, -.75
    r.poly([(hx0 - .12, hy - .12, ZB), (hx1 + .12, hy - .12, ZB), (hx1 + .12, YF, ZB), (hx0 - .12, YF, ZB)], (230, 222, 204) if not vieja else (140, 120, 96))
    ZH = 13.0
    r.poly([(hx0, hy, ZB), (hx1, hy, ZB), (hx1, YF, ZB), (hx0, YF, ZB)], (40, 34, 32))
    r.poly([(hx0, YF, ZB), (hx1, YF, ZB), (hx1, YF, ZH), (hx0, YF, ZH)], (110, 80, 56) if suelo.startswith("parquet") else (80, 70, 50))
    hw = (150, 136, 120) if vieja else (214, 206, 190)
    r.poly([(hx0, hy, ZB), (hx0, hy, ZH), (hx0, YF, ZH), (hx0, YF, ZB)], tuple(int(c * .85) for c in hw)); r.poly([(hx1, hy, ZH), (hx1, hy, ZB), (hx1, YF, ZB), (hx1, YF, ZH)], tuple(int(c * .75) for c in hw))
    r.poly([(hx0, hy, ZH), (hx1, hy, ZH), (hx1, YF, ZH), (hx0, YF, ZH)], tuple(int(c * .9) for c in hw))
    r.poly([(hx0, hy, ZB), (hx1, hy, ZB), (hx1, hy, ZH), (hx0, hy, ZH)], tuple(int(c * .7) for c in hw))
    for (X, z0d, lbl) in ((hx0, 9.4, "BAÑO"), (hx1, 10.6, "HABITACIÓN")):   # puertas laterales del pasillo
        pts = [(X, -.35, z0d), (X, -.35, z0d + 1.0), (X, YF, z0d + 1.0), (X, YF, z0d)]
        r.poly(pts, (110, 76, 52) if vieja else (236, 230, 216), (60, 40, 30), 2)
        kx, ky = Pp(X, .45, z0d + .85); r.d.ellipse(((kx - 3) * K2, (ky - 3) * K2, (kx + 3) * K2, (ky + 3) * K2), fill=(200, 170, 80))
        tx, ty = Pp(X, -.15, z0d + .5); r.d.text((tx * K2, ty * K2), lbl, font=font(F_ANTON, 13 * K2), fill=(40, 30, 24), anchor="mm")
    r.poly([((hx0 + hx1) / 2 - .4, -.4, ZH - .01), ((hx0 + hx1) / 2 + .4, -.4, ZH - .01), ((hx0 + hx1) / 2 + .4, YF, ZH - .01), ((hx0 + hx1) / 2 - .4, YF, ZH - .01)], (90, 70, 56), (50, 40, 30), 2)
    # ---------------- pared derecha: ESCALERA al piso de arriba + puerta bajo la escalera
    sx0, sx1 = 2.0, XR - .02; zs0, zs1 = 3.4, 7.6; n = 14
    hstep = (YF - (YC + .05)) / n; dz = (zs1 - zs0) / n
    st = (130, 92, 62) if vieja else (176, 128, 84)
    r.poly([(sx0, YF, zs0), (sx0, YC + .05, zs1), (sx0, YF, zs1)], tuple(int(c * .55) for c in st))   # zanca (lateral bajo la escalera)
    r.poly([(sx0 + .02, .35, 5.6), (sx0 + .02, .35, 6.4), (sx0 + .02, YF, 6.4), (sx0 + .02, YF, 5.6)], (90, 60, 40), (50, 34, 24), 2)   # puertecita bajo la escalera
    for i in range(n - 1, -1, -1):
        za, zb = zs0 + i * dz, zs0 + (i + 1) * dz; yt = YF - (i + 1) * hstep
        r.poly([(sx0, yt, za), (sx1, yt, za), (sx1, yt + hstep, za), (sx0, yt + hstep, za)], tuple(int(c * .8) for c in st))   # contrahuella
        r.poly([(sx0, yt, za), (sx1, yt, za), (sx1, yt, zb), (sx0, yt, zb)], st)                                                 # huella
        if i % 2 == 0: r.line((sx0 + .05, yt, za + dz / 2), (sx0 + .05, yt - .9, za + dz / 2), (200, 186, 160) if not vieja else (150, 126, 96), 3)   # balaustres
    r.line((sx0 + .05, YF - hstep - .9, zs0), (sx0 + .05, YC + .05 - .9 + .9, zs1), (120, 84, 56), 7)   # pasamanos
    r.poly([(sx0 - .1, YC, zs1 - 1.2), (XR, YC, zs1 - 1.2), (XR, YC, zs1 + .3), (sx0 - .1, YC, zs1 + .3)], (30, 26, 24))   # hueco al piso de arriba
    # ---------------- lámpara de techo
    lx, lz = -.6, 4.6
    r.line((lx, YC, lz), (lx, -1.05, lz), (40, 36, 30), 2)
    for k in range(-2, 3):
        r.line((lx, -1.05, lz), (lx + k * .18, -.92, lz), (150, 120, 60), 2)
        ax, ay = Pp(lx + k * .18, -.95, lz); r.d.ellipse(((ax - 5) * K2, (ay - 7) * K2, (ax + 5) * K2, (ay + 3) * K2), fill=(255, 236, 180) if not vieja else (160, 150, 130))
    # ---------------- muebles
    if muebles:
        rug = [(-2.5, YF - .001, 4.9), (.9, YF - .001, 4.9), (.9, YF - .001, 7.5), (-2.5, YF - .001, 7.5)]
        r.poly(rug, (150, 60, 50) if vieja else (196, 170, 130)); r.poly([(-2.35, YF - .002, 5.05), (.75, YF - .002, 5.05), (.75, YF - .002, 7.35), (-2.35, YF - .002, 7.35)], None, (220, 190, 120), 3)
        # sofá frontal
        x0, x1, y0, y1, z0, z1 = MUEBLES["sofa"]; sc = (150, 70, 70) if vieja else (176, 150, 116)
        r.box(x0, x1, y0, y1 - .45, z1 - .25, z1, tuple(int(c * .8) for c in sc))
        r.box(x0 + .2, x1 - .2, .78, y1 - .1, z0 + .2, z1 - .2, sc)
        r.box(x0, x0 + .3, .5, y1 - .1, z0 + .1, z1, tuple(int(c * .85) for c in sc)); r.box(x1 - .3, x1, .5, y1 - .1, z0 + .1, z1, tuple(int(c * .85) for c in sc))
        for k in range(3):
            xa = x0 + .3 + k * (x1 - x0 - .6) / 3; r.box(xa + .03, xa + (x1 - x0 - .6) / 3 - .03, .62, .82, z0 + .25, z1 - .3, tuple(min(255, int(c * 1.1)) for c in sc))
        # butaca
        x0, x1, y0, y1, z0, z1 = MUEBLES["butaca"]; bc = (120, 104, 70) if vieja else (214, 196, 160)
        r.box(x0, x1, y0, y1 - .5, z1 - .25, z1, tuple(int(c * .8) for c in bc)); r.box(x0 + .1, x1 - .1, .82, y1 - .1, z0 + .1, z1 - .2, bc)
        r.box(x0, x0 + .22, .55, y1 - .1, z0 + .05, z1, tuple(int(c * .85) for c in bc)); r.box(x1 - .22, x1, .55, y1 - .1, z0 + .05, z1, tuple(int(c * .85) for c in bc))
        # mesa baja
        x0, x1, y0, y1, z0, z1 = MUEBLES["mesa"]
        r.box(x0, x1, y0, y0 + .08, z0, z1, (110, 76, 48))
        for xx in (x0 + .05, x1 - .12):
            for zz in (z0 + .05,): r.box(xx, xx + .07, y0 + .08, y1, zz, zz + .07, (86, 58, 36))
        r.line((-2.6, YF, 6.2), (-2.6, -.3, 6.2), (40, 40, 44), 4); r.poly([(-2.8, -.55, 6.2), (-2.4, -.55, 6.2), (-2.47, -.25, 6.2), (-2.73, -.25, 6.2)], (230, 210, 160) if not vieja else (160, 140, 110))
        # cortinas del ventanal, planta, reloj de pared y mesita con lámpara
        for z0c, z1c in ((6.15, 6.35), (7.55, 7.75)):
            r.poly([(XL + .01, -.95, z0c), (XL + .01, -.95, z1c), (XL + .01, .95, z1c + .05), (XL + .01, .95, z0c - .05)], (150, 60, 60) if vieja else (220, 200, 160))
        r.box(-.55, -.25, .95, YF, 7.45, 7.75, (170, 110, 80)); 
        for k in range(6):
            a = -1.2 + k * .5; x, y = Pp(-.4, .95, 7.6); r.d.ellipse(((x + 28 * math.cos(a) - 14) * K2, (y - 30 + 18 * math.sin(a) - 10) * K2, (x + 28 * math.cos(a) + 14) * K2, (y - 30 + 18 * math.sin(a) + 10) * K2), fill=(70, 130, 70) if not vieja else (90, 80, 50))
        cx_, cy_ = Pp(XR, -.9, 2.9); r.d.ellipse(((cx_ - 36) * K2, (cy_ - 46) * K2, (cx_ + 10) * K2, (cy_ + 46) * K2), fill=(236, 226, 200), outline=(90, 60, 40), width=4 * K2)
        r.d.line(((cx_ - 13) * K2, cy_ * K2, (cx_ - 13) * K2, (cy_ - 24) * K2), fill=(30, 30, 30), width=3 * K2); r.d.line(((cx_ - 13) * K2, cy_ * K2, (cx_ - 2) * K2, (cy_ + 8) * K2), fill=(30, 30, 30), width=3 * K2)
        r.box(1.45, 1.85, .7, YF, 6.6, 7.0, (120, 84, 56)); r.line((1.65, .7, 6.8), (1.65, .25, 6.8), (60, 60, 60), 3); r.poly([(1.45, .05, 6.8), (1.85, .05, 6.8), (1.78, .3, 6.8), (1.52, .3, 6.8)], (240, 220, 170) if not vieja else (170, 150, 120))
        if sabanas:
            for nm, seed in (("sofa", 1), ("butaca", 2), ("mesa", 3)):
                b = box2d(nm); sabana2(im, b, seed)
    if vieja:
        r = R3(im)
        for X, s_ in ((XL, 1), (XR, -1)):
            cxp, cyp = Pp(X, YC, ZN + .3)
            for a in range(0, 91, 15):
                rr = math.radians(a); r.d.line((cxp * K2, cyp * K2, (cxp + s_ * 280 * math.cos(rr)) * K2, (cyp + 280 * math.sin(rr)) * K2), fill=(240, 240, 240, 90), width=2 * K2)
        im.alpha_composite(Image.new("RGBA", S2, (40, 30, 20, 46)))
    # luz de la ventana
    sun = Image.new("RGBA", S2, (0, 0, 0, 0)); sd = ImageDraw.Draw(sun)
    a, b = P(XL, -.75, 7.6), P(XL, .65, 7.6); c_, d_ = P(.6, YF, 7.4), P(-.6, YF, 5.6)
    sd.polygon([P(XL, -.75, 6.3), a, b, c_, d_, P(XL, .65, 6.3)], fill=(255, 236, 180, 50))
    im.alpha_composite(sun.filter(ImageFilter.GaussianBlur(30)))
    return A.add_grain(im, 5, 7)   # se devuelve a 2x (PLATE_K) para encuadres cerrados nítidos

def sabana2(im, box, seed, alpha=255, dy=0, dx=0, rot=0, k=K2):
    x0, y0, x1, y1 = [v * k for v in box]; rng = random.Random(seed)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(lay)
    pts = [(x0 - 10 * k, y1 + 8 * k), (x0 - 4 * k, y0 + (y1 - y0) * .3), (x0 + (x1 - x0) * .2, y0 - 8 * k), (x1 - (x1 - x0) * .25, y0 - 14 * k), (x1 + 6 * k, y0 + (y1 - y0) * .25), (x1 + 14 * k, y1 + 8 * k)]
    sd.polygon(pts, fill=(228, 226, 218, alpha))
    for _ in range(7):
        x = rng.uniform(x0 + 6 * k, x1 - 6 * k); sd.line([(x + 6 * k * math.sin(v), lerp(y0, y1, v / 3)) for v in np.linspace(0, 3, 10)], fill=(192, 190, 184, alpha), width=5 * k)
    if dx or dy or rot: lay = lay.rotate(rot, center=((x0 + x1) / 2, (y0 + y1) / 2), resample=Image.BICUBIC, translate=(dx * k, dy * k))
    im.alpha_composite(lay)

salon_v1 = salon
def salon(paredes="vieja", suelo="moqueta", sabanas=True, muebles=True):
    return casa(paredes, suelo, sabanas, muebles)
