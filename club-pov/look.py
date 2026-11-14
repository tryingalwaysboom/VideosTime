"""Estilos de acabado (post-proceso por fotograma) para la serie. LOOK = "actual" | "cine" | "comic"."""
import math
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageChops

W, H = 1080, 1920
LOOK = "cine"

# ------------------------------------------------------------------ utilidades
def _lut(fn):
    x = np.arange(256) / 255.0
    return np.clip(fn(x) * 255, 0, 255).astype(np.uint8)

def _radial():
    y, x = np.mgrid[0:H, 0:W]
    r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / 1.414
    return r
_R = None
def radial():
    global _R
    if _R is None: _R = _radial()
    return _R

# ------------------------------------------------------------------ CINE
def _curve(x, lift, gain, k):
    y = x + k * (x - .5) * np.sin(np.pi * x) * 0 
    y = 1 / (1 + np.exp(-k * (x - .5)))
    y = (y - 1 / (1 + np.exp(k * .5))) / (1 / (1 + np.exp(-k * .5)) - 1 / (1 + np.exp(k * .5)))
    return lift + (gain - lift) * (.55 * y + .45 * x)
LUT_R = _lut(lambda x: _curve(x, .0, 1.03, 6.5))
LUT_G = _lut(lambda x: _curve(x, .012, 1.0, 6.5))
LUT_B = _lut(lambda x: _curve(x, .05, .95, 6.0))

_leak = {}
def light_leak(T):
    k = int(T * 12)
    if k in _leak: return _leak[k]
    t = k / 12
    im = Image.new("RGB", (W // 8, H // 8), (0, 0, 0)); d = ImageDraw.Draw(im)
    cx = W / 8 * (.15 + .7 * (.5 + .5 * math.sin(t * .23)))
    cy = H / 8 * (.1 + .12 * math.sin(t * .31))
    r = 60 + 15 * math.sin(t * .7)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 150, 60))
    d.ellipse((W / 8 - 40 - r / 2, H / 8 * .85 - r / 2, W / 8 - 40 + r / 2, H / 8 * .85 + r / 2), fill=(120, 60, 255))
    im = im.filter(ImageFilter.GaussianBlur(28)).resize((W, H), Image.BILINEAR)
    if len(_leak) > 64: _leak.clear()
    _leak[k] = im
    return im

_BK = {}
def bokeh(T):
    k = int(T * 30)
    if k in _BK: return _BK[k]
    if len(_BK) > 8: _BK.clear()
    im = Image.new("RGBA", (W // 3, H // 3), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rr = np.random.default_rng(11)
    for j in range(9):
        x = (rr.uniform(0, W // 3) + T * rr.uniform(-6, 6)) % (W // 3)
        y = (rr.uniform(0, H // 3) - T * rr.uniform(3, 9)) % (H // 3)
        r = rr.uniform(10, 30); a = int(18 + 16 * (.5 + .5 * math.sin(T * .9 + j)))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 230, 190, a))
    im = im.filter(ImageFilter.GaussianBlur(4)).resize((W, H), Image.BILINEAR)
    _BK[k] = im
    return im

def cine(img, T, energy=0.0):
    """img RGBA 1080x1920 → RGBA graduado."""
    rgb = img.convert("RGB")
    # bloom: zonas brillantes difuminadas y sumadas en modo pantalla
    small = rgb.resize((W // 4, H // 4), Image.BILINEAR)
    a = np.asarray(small).astype(np.float32)
    lum = a.mean(axis=2, keepdims=True)
    hi = np.clip((lum - 205) / 50, 0, 1) * a
    bl = Image.fromarray(hi.astype(np.uint8)).filter(ImageFilter.GaussianBlur(14)).resize((W, H), Image.BILINEAR)
    hal = Image.fromarray((hi * np.array([1.0, .45, .25])).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5)).resize((W, H), Image.BILINEAR)
    rgb = ImageChops.screen(rgb, Image.eval(bl, lambda v: int(v * .32)))
    rgb = ImageChops.screen(rgb, Image.eval(hal, lambda v: int(v * .18)))
    # gradación de color
    r, g, b = rgb.split()
    rgb = Image.merge("RGB", (r.point(LUT_R.tolist()), g.point(LUT_G.tolist()), b.point(LUT_B.tolist())))
    # saturación +18%
    a = np.asarray(rgb).astype(np.float32); m = a.mean(axis=2, keepdims=True)
    rgb = Image.fromarray(np.clip(m + (a - m) * 1.18, 0, 255).astype(np.uint8))
    rgb = rgb.convert("RGBA"); rgb.alpha_composite(bokeh(T)); rgb = rgb.convert("RGB")
    # fuga de luz suave
    rgb = ImageChops.screen(rgb, Image.eval(light_leak(T), lambda v: int(v * .22)))
    # aberración cromática en los bordes (más fuerte en impactos)
    sh = int(2 + 6 * energy)
    if sh:
        r, g, b = rgb.split()
        r2 = ImageChops.offset(r, sh, 0); b2 = ImageChops.offset(b, -sh, 0)
        mask = edge_mask()
        r = Image.composite(r2, r, mask); b = Image.composite(b2, b, mask)
        rgb = Image.merge("RGB", (r, g, b))
    return rgb.convert("RGBA")

_EM = None
def edge_mask():
    global _EM
    if _EM is None:
        _EM = Image.fromarray((np.clip((radial() - .45) / .5, 0, 1) * 255).astype(np.uint8))
    return _EM

# ------------------------------------------------------------------ CÓMIC
_PAPER = None
def paper():
    global _PAPER
    if _PAPER is None:
        rng = np.random.default_rng(7)
        n = rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
        n = np.asarray(Image.fromarray(((n * 20) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)).resize((W, H), Image.BICUBIC)).astype(np.float32)
        fib = rng.normal(0, 1, (H, W)).astype(np.float32) * 6
        _PAPER = ((n - 128) * .5 + fib)[..., None]
    return _PAPER

_DOTS = None
def dots():
    global _DOTS
    if _DOTS is None:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        a = math.radians(45); u = x * math.cos(a) - y * math.sin(a); v = x * math.sin(a) + y * math.cos(a)
        p = 11.0
        _DOTS = np.sqrt(((u % p) - p / 2) ** 2 + ((v % p) - p / 2) ** 2) / (p / 2)   # 0 centro → 1.41 esquina
    return _DOTS

def comic(img, T, energy=0.0):
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    lum = a.mean(axis=2)
    # posterizado suave + saturación
    m = lum[..., None]
    a = m + (a - m) * 1.25
    a = np.round(a / 28) * 28 * .55 + a * .45
    # trama de puntos en las sombras
    shade = np.clip((120 - lum) / 120, 0, 1)
    dot = (dots() < shade * 1.1).astype(np.float32)
    a = a * (1 - .45 * dot[..., None])
    # papel cálido
    a = a * np.array([1.0, .97, .9]) + np.array([10, 6, 0]) + paper()
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    # tinta: bordes oscuros
    e = img.convert("L").resize((W // 2, H // 2)).filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 38 else 0)
    e = e.filter(ImageFilter.MaxFilter(3)).resize((W, H), Image.BILINEAR)
    out = Image.composite(Image.new("RGB", (W, H), (18, 14, 20)), out, e.point(lambda v: int(v * .55)))
    # marco de viñeta de cómic
    d = ImageDraw.Draw(out)
    d.rectangle((0, 0, W - 1, H - 1), outline=(245, 238, 222), width=26)
    d.rectangle((26, 26, W - 27, H - 27), outline=(18, 14, 20), width=7)
    # líneas de acción en impactos
    if energy > .15:
        rng = np.random.default_rng(int(T * 30))
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        for _ in range(46):
            ang = rng.uniform(0, 2 * math.pi); r0 = rng.uniform(560, 700)
            x0, y0 = W / 2 + r0 * math.cos(ang), H / 2 + r0 * 1.6 * math.sin(ang)
            x1, y1 = W / 2 + 1500 * math.cos(ang), H / 2 + 2400 * math.sin(ang)
            od.line((x0, y0, x1, y1), fill=(255, 255, 255, int(200 * energy)), width=int(rng.uniform(3, 9)))
        out = out.convert("RGBA"); out.alpha_composite(ov); return out
    return out.convert("RGBA")

def apply(img, T, energy=0.0, look=None):
    look = look or LOOK
    import styles
    if look in styles.STYLES: return styles.STYLES[look](img, T, energy)
    if look == "cine": return cine(img, T, energy)
    if look == "comic": return comic(img, T, energy)
    return img
