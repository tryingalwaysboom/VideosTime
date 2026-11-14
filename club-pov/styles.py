"""Estilos visuales alternativos para la serie (se aplican al dibujo antes de la barra y los subtítulos)."""
import math
import numpy as np, cv2
from PIL import Image, ImageFilter, ImageDraw

W, H = 1080, 1920
_cache = {}
def once(key, fn):
    if key not in _cache: _cache[key] = fn()
    return _cache[key]

def _paper(seed=5, amp=10, warm=(250, 244, 230)):
    rng = np.random.default_rng(seed)
    n = cv2.resize(rng.normal(0, 1, (H // 6, W // 6)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    f = rng.normal(0, 1, (H, W)).astype(np.float32)
    return n * amp + f * amp * .4

def _edges(a, thr=40, thick=3):
    g = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY)
    e = cv2.Canny(cv2.GaussianBlur(g, (3, 3), 0), thr, thr * 2.5)
    return cv2.dilate(e, np.ones((thick, thick), np.uint8))

# ------------------------------------------------------------------ ANIME
# sombreado en dos tonos (cel), colores vivos, cielo luminoso, línea fina y brillos
def anime(img, T, energy=0):
    a = np.asarray(img.convert("RGB"))
    s = cv2.bilateralFilter(a, 9, 60, 9)
    hsv = cv2.cvtColor(s, cv2.COLOR_RGB2HSV).astype(np.float32)
    v = hsv[..., 2] / 255
    v = np.where(v < .33, .26, np.where(v < .62, .58, np.where(v < .86, .84, 1.0))) * .7 + v * .3   # tonos planos
    hsv[..., 2] = v * 255
    hsv[..., 1] = np.clip(hsv[..., 1] * 1.35 + 8, 0, 255)
    out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
    # tono cálido-violeta en sombras, luz cálida arriba (atmósfera anime)
    y = np.linspace(0, 1, H)[:, None, None]
    out = out * (1 - .12 * (1 - v[..., None])) + (1 - v[..., None]) * np.array([30, 10, 60]) * .35
    out += (1 - y) * np.array([30, 20, 0]) * .5
    e = _edges(a, 50, 2)
    out[e > 0] = out[e > 0] * .35 + np.array([40, 20, 50]) * .65
    # bloom suave
    b = cv2.GaussianBlur(np.clip(out - 170, 0, 255), (0, 0), 18)
    out = out + b * .55
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")

# ------------------------------------------------------------------ ACUARELA (cuento ilustrado)
def acuarela(img, T, energy=0):
    a = np.asarray(img.convert("RGB"))
    s = cv2.stylization(cv2.resize(a, (W // 2, H // 2)), sigma_s=40, sigma_r=.35)
    s = cv2.resize(s, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    # pigmento acumulado en los bordes de cada mancha
    g = cv2.cvtColor(s.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    lap = np.abs(cv2.Laplacian(cv2.GaussianBlur(g, (0, 0), 2), cv2.CV_32F))
    s = s * (1 - np.clip(lap / 40, 0, .35)[..., None])
    # lavado: aclara y mezcla con papel
    paper = np.array([248, 241, 226], np.float32)
    m_ = s.mean(-1, keepdims=True); s = m_ + (s - m_) * 1.35
    s = s * .88 + paper * .12 + 12
    tex = once("paperA", lambda: _paper(9, 9))
    gran = once("gran", lambda: cv2.GaussianBlur(np.random.default_rng(2).normal(0, 1, (H, W)).astype(np.float32), (0, 0), 1.2))
    s = s + tex[..., None] * .6 + gran[..., None] * 4 * (1 - g[..., None] / 255)
    # línea a lápiz suave
    e = _edges(a, 60, 1)
    s[e > 0] = s[e > 0] * .7 + np.array([60, 50, 60]) * .3
    return Image.fromarray(np.clip(s, 0, 255).astype(np.uint8)).convert("RGBA")

# ------------------------------------------------------------------ RISO (impresión de 3 tintas)
INK = [np.array(c, np.float32) for c in ((255, 72, 120), (0, 120, 191), (255, 232, 0))]   # rosa flúor, azul, amarillo
def _dots(angle, period):
    def mk():
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        a = math.radians(angle); u = x * math.cos(a) - y * math.sin(a); v = x * math.sin(a) + y * math.cos(a)
        return np.sqrt(((u % period) - period / 2) ** 2 + ((v % period) - period / 2) ** 2) / (period / 2 * 1.414)
    return once(("d", angle, period), mk)

def riso(img, T, energy=0):
    a = np.asarray(img.convert("RGB")).astype(np.float32) / 255
    lum = a @ np.array([.3, .59, .11], np.float32)
    hsv = cv2.cvtColor((a * 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    sat = hsv[..., 1] / 255
    warm = ((hsv[..., 0] < 25) | (hsv[..., 0] > 150)).astype(np.float32) * sat      # rojos/naranjas → rosa
    yel = ((hsv[..., 0] >= 18) & (hsv[..., 0] < 40)).astype(np.float32) * sat         # amarillos → amarillo
    blue = np.clip((1 - lum) * 1.15 - .05, 0, 1)                                      # sombras → azul
    out = np.ones((H, W, 3), np.float32) * np.array([247, 241, 228])
    for L, ink, ang, j in ((blue, (36, 70, 160), 15, (2, -2)), (warm, (255, 72, 140), 75, (-2, 2)), (yel, (255, 214, 0), 45, (0, 3))):
        L = cv2.GaussianBlur(L.astype(np.float32), (0, 0), 1)
        cov = (_dots(ang, 6) < np.sqrt(np.clip(L, 0, 1))).astype(np.float32)
        cov = cv2.GaussianBlur(np.roll(cov, j, axis=(0, 1)), (0, 0), .7)
        out = out * (1 - cov[..., None] * (1 - np.array(ink) / 255))
    out += once("paperR", lambda: _paper(4, 5))[..., None]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")

# ------------------------------------------------------------------ RECORTE DE PAPEL (stop-motion)
def recorte(img, T, energy=0):
    a = np.asarray(img.convert("RGB"))
    sm = cv2.resize(a, (W // 4, H // 4))
    Z = sm.reshape(-1, 3).astype(np.float32)
    key = ("km", int(T * 2))                              # paleta estable cada medio segundo
    if key not in _cache:
        crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 12, 1.0)
        _, _, cen = cv2.kmeans(Z, 12, None, crit, 2, cv2.KMEANS_PP_CENTERS)
        _cache[key] = cen
    cen = _cache[key]
    big = cv2.medianBlur(a, 11).reshape(-1, 3).astype(np.float32)
    d = ((big[:, None, :] - cen[None]) ** 2).sum(-1)
    lab = d.argmin(1).reshape(H, W)
    q = cen[lab].astype(np.float32)
    # sombra bajo cada pieza: bordes entre zonas, desplazada abajo-derecha
    edge = (cv2.Laplacian(lab.astype(np.float32), cv2.CV_32F) != 0).astype(np.uint8) * 255
    edge = cv2.dilate(edge, np.ones((3, 3), np.uint8))
    lum = q.mean(-1)
    sh = cv2.GaussianBlur(np.roll(edge, (6, 5), axis=(0, 1)).astype(np.float32), (0, 0), 4) / 255
    q = q * (1 - .35 * sh[..., None])
    # borde claro de papel cortado + fibra
    q[edge > 0] = q[edge > 0] * .75 + 255 * .25
    tex = once("paperC", lambda: _paper(7, 5))
    q = q + tex[..., None]
    # ligero "tembleque" de stop-motion
    j = int(T * 8) % 3 - 1
    q = np.roll(q, j, axis=1)
    return Image.fromarray(np.clip(q, 0, 255).astype(np.uint8)).convert("RGBA")

STYLES = {"anime": anime, "acuarela": acuarela, "riso": riso, "recorte": recorte}
