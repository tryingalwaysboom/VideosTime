"""Vista de gafas con cámara (POV grabado): lente ojo de pez + aberración cromática, respiración, fallos de señal,
visión nocturna y la interfaz de grabación (REC, hora, batería). Estilo fijo de la serie."""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art import W, H, font, F_ANTON, F_UI

@lru_cache(1)
def _maps():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx, ny = (xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)
    r2 = (nx * nx) * .55 + ny * ny * .45
    out = []
    for k in (.075, .065, .055):   # R, G, B: cada canal con un poco más/menos de curva -> aberración en los bordes
        s = (1 - k * .9) * (1 + k * r2)
        sx = np.clip(W / 2 + nx * s * W / 2, 0, W - 1).astype(np.int32); sy = np.clip(H / 2 + ny * s * H / 2, 0, H - 1).astype(np.int32)
        out.append((sx, sy))
    return out

def respiracion(T, fuerte=1.0):
    dx = 7 * math.sin(T * 1.3) + 3 * math.sin(T * 3.1 + 1) + 1.5 * math.sin(T * 7.7)
    dy = 9 * math.sin(T * 1.05 + .5) + 3 * math.sin(T * 2.6) + 1.5 * math.cos(T * 8.3)
    return dx * fuerte, dy * fuerte

def lente(img, T, glitch=0.0, nv=False, fuerte=1.0):
    """img RGBA/RGB (W x H) -> RGBA con lente, respiración, glitch y visión nocturna."""
    a = np.asarray(img.convert("RGB"))
    dx, dy = respiracion(T, fuerte); dx, dy = int(dx), int(dy)
    ch = []
    for i, (sx, sy) in enumerate(_maps()):
        x = np.clip(sx + dx + (int(14 * glitch) * (i - 1)), 0, W - 1); y = np.clip(sy + dy, 0, H - 1)
        ch.append(a[y, x, i])
    o = np.dstack(ch)
    if glitch > 0:   # bandas horizontales desplazadas
        rng = np.random.default_rng(int(T * 1000))
        for _ in range(int(4 + 8 * glitch)):
            y0 = rng.integers(0, H - 60); h = rng.integers(8, 70); sh = int(rng.integers(-80, 80) * glitch)
            o[y0:y0 + h] = np.roll(o[y0:y0 + h], sh, axis=1)
        if rng.random() < .5 * glitch: o = np.clip(o.astype(np.int16) + 40, 0, 255).astype(np.uint8)
    if nv:   # visión nocturna verde
        l = (o[..., 0] * .3 + o[..., 1] * .59 + o[..., 2] * .11)
        l = np.clip((l / 255) ** .6 * 255 * 1.25, 0, 255)
        o = np.dstack([l * .35, l, l * .4]).astype(np.uint8)
    o[::3] = (o[::3] * .9).astype(np.uint8)   # líneas de barrido muy suaves
    return Image.fromarray(o, "RGB").convert("RGBA")

@lru_cache(1)
def _vig():
    yy, xx = np.mgrid[0:H, 0:W]; d = np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2)
    a = np.clip((d - .6) / .5, 0, 1) ** 1.4 * 230
    v = np.zeros((H, W, 4), np.uint8); v[..., 3] = a.astype(np.uint8); return Image.fromarray(v, "RGBA")

def interfaz(c, T, hora, nv=False, glitch=0.0):
    """Interfaz de las gafas: esquinas del visor, ● REC, hora, batería, IR."""
    c.alpha_composite(_vig()); d = ImageDraw.Draw(c)
    col = (235, 240, 235, 230) if not nv else (190, 255, 190, 230)
    L, x0, y0, x1, y1 = 70, 44, 300, W - 44, 1650
    for (x, y, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line((x, y, x + sx * L, y), fill=col, width=5); d.line((x, y, x, y + sy * L), fill=col, width=5)
    if int(T * 2) % 2 == 0: d.ellipse((76, 322, 104, 350), fill=(240, 40, 40, 255))
    d.text((116, 336), "REC", font=font(F_UI, 34), fill=col, anchor="lm")
    hh, mm, ss = hora
    tot = int(hh * 3600 + mm * 60 + ss + T); s_ = f"{tot // 3600 % 24:02d}:{tot // 60 % 60:02d}:{tot % 60:02d}"
    d.text((W - 76, 336), s_, font=font(F_UI, 34), fill=col, anchor="rm")
    bx, by = W - 320, 322   # batería baja parpadeando
    d.rectangle((bx, by, bx + 52, by + 28), outline=col, width=3); d.rectangle((bx + 52, by + 8, bx + 58, by + 20), fill=col)
    if int(T * 1.5) % 2 == 0: d.rectangle((bx + 5, by + 5, bx + 14, by + 23), fill=(240, 60, 50, 255))
    if nv: d.text((W / 2, 336), "IR ON", font=font(F_UI, 30), fill=col, anchor="mm")
    if glitch > .3: d.text((W / 2, 400), "SEÑAL INESTABLE", font=font(F_UI, 30), fill=(255, 80, 70, 230), anchor="mm")
