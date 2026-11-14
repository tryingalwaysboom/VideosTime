"""Estilo 4: manga en blanco y negro con viñetas que aparecen, tramas, líneas de acción y bocadillos. Solo el rojo para lo importante."""
import math, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
from comun import *

CAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "capas_anime")
LY = {n: Image.open(os.path.join(CAP, n + ".png")).convert("RGBA") for n in ("paco_base", "gafas", "ojos_a", "ojos_c", "boca0", "boca1", "boca2")}
BGC = Image.open(os.path.join(CAP, "fondo.png")).convert("RGB")
INK = (16, 14, 18); PAPER = (250, 248, 242); RED = (225, 40, 50)
FM = "Bangers-Regular.ttf"; FT = "Kalam-Bold.ttf"

_pc = {}
def paco_full(T):
    blink = (T % 3.3) < .11
    m = boca(T); b = "boca2" if m > .55 else ("boca1" if m > .15 else "boca0")
    k = (blink, b)
    if k not in _pc:
        im = Image.new("RGBA", LY["paco_base"].size, (0, 0, 0, 0)); im.alpha_composite(LY["paco_base"])
        for n in ("ojos_c" if blink else "ojos_a", "gafas", b): im.alpha_composite(LY[n])
        _pc[k] = im
    return _pc[k]

_dots = {}
def dots(w, h, per):
    k = (w, h, per)
    if k not in _dots:
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        a = math.radians(45); u = x * math.cos(a) - y * math.sin(a); v = x * math.sin(a) + y * math.cos(a)
        _dots[k] = np.sqrt(((u % per) - per / 2) ** 2 + ((v % per) - per / 2) ** 2) / (per / 2)
    return _dots[k]

def manga(img):
    """Color -> manga: negro, trama oscura, trama clara, blanco + tinta en los bordes."""
    a = np.asarray(img.convert("RGB"))
    g = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY).astype(np.float32)
    h, w = g.shape
    out = np.full((h, w), 250, np.float32)
    dd = dots(w, h, 7)
    out[(g < 205) & (dd < .55)] = 30          # trama clara
    out[(g < 150) & (dd < .95)] = 30          # trama oscura
    out[g < 75] = 18                          # negro
    e = cv2.Canny(cv2.GaussianBlur(a, (3, 3), 0), 40, 110)
    out[cv2.dilate(e, np.ones((2, 2), np.uint8)) > 0] = 16
    o = Image.fromarray(out.astype(np.uint8)).convert("RGB")
    return o

def lineas_accion(w, h, T, cx=None, cy=None):
    im = Image.new("RGB", (w, h), PAPER); d = ImageDraw.Draw(im)
    cx = w / 2 if cx is None else cx; cy = h / 2 if cy is None else cy
    rng = np.random.default_rng(int(T * 12))
    for _ in range(90):
        ang = rng.uniform(0, 2 * math.pi); r0 = rng.uniform(.38, .55) * max(w, h)
        x0, y0 = cx + r0 * math.cos(ang), cy + r0 * math.sin(ang)
        x1, y1 = cx + 2 * max(w, h) * math.cos(ang), cy + 2 * max(w, h) * math.sin(ang)
        wd = rng.uniform(.004, .022)
        d.polygon([(x0, y0), (x1 + wd * 900 * math.sin(ang), y1 - wd * 900 * math.cos(ang)), (x1 - wd * 900 * math.sin(ang), y1 + wd * 900 * math.cos(ang))], fill=INK)
    return im

def cover(src, box):
    """Recorta src (PIL) al aspecto de box (w,h) y redimensiona."""
    w, h = box; sw, sh = src.size
    r = max(w / sw, h / sh)
    im = src.resize((int(sw * r) + 1, int(sh * r) + 1), Image.LANCZOS)
    x = (im.width - w) // 2; y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))

# ------------------------------------------------------------ viñetas
G = 22
P = {"A": (40, 220, 1040, 700), "B": (40, 700 + G, 600, 1250), "C": (600 + G, 700 + G, 1040, 1250), "D": (40, 1250 + G, 1040, 1880)}
TA = T0 + .05; TB = EV["paco"] - .15; TC = EV["9"] - .1; TD = EV["habla0"] - .25

def vineta_A(T):
    w, h = P["A"][2] - P["A"][0], P["A"][3] - P["A"][1]
    z = 1 + .04 * clamp((T - TA) / 4)
    src = BGC.crop((0, 380, 1080, 1340)); src = src.resize((int(src.width * z), int(src.height * z)))
    im = manga(cover(src, (w, h)))
    d = ImageDraw.Draw(im)
    return im

def vineta_B(T):
    w, h = P["B"][2] - P["B"][0], P["B"][3] - P["B"][1]
    p = paco_full(T).crop((560, 300, 1240, 1080))
    bg = Image.new("RGBA", p.size, (238, 232, 228, 255)); bg.alpha_composite(p)
    return manga(cover(bg.convert("RGB"), (w, h)))

def vineta_C(T):
    w, h = P["C"][2] - P["C"][0], P["C"][3] - P["C"][1]
    p = paco_full(T).crop((380, 1560, 1420, 2320))
    bg = Image.new("RGBA", p.size, (200, 196, 200, 255)); bg.alpha_composite(p)
    return manga(cover(bg.convert("RGB"), (w, h)))

def vineta_D(T):
    w, h = P["D"][2] - P["D"][0], P["D"][3] - P["D"][1]
    im = lineas_accion(w, h, T, w * .62, h * .35)
    p = paco_full(T).crop((200, 200, 1600, 1500))
    p = p.resize((int(p.width * .62), int(p.height * .62)), Image.LANCZOS)
    pm = manga(Image.alpha_composite(Image.new("RGBA", p.size, (250, 248, 242, 255)), p).convert("RGB"))
    im.paste(pm, (int(w * .62 - p.width / 2), h - p.height + 120), p.getchannel("A"))
    return im

def bocadillo(d, box, texto_pal, T, cola):
    x0, y0, x1, y1 = box
    d.ellipse(box, fill=PAPER, outline=INK, width=6)
    d.polygon(cola, fill=PAPER); d.line(cola[:2], fill=INK, width=6); d.line(cola[1:], fill=INK, width=6)
    f = font(FT, 46)
    lines, cur, wsum = [], [], 0
    for w, a, b in texto_pal:
        tw = d.textlength(w + " ", font=f)
        if wsum + tw > (x1 - x0) * .78 and cur: lines.append(cur); cur, wsum = [], 0
        cur.append((w, a, b)); wsum += tw
    if cur: lines.append(cur)
    cy = (y0 + y1) / 2 - (len(lines) - 1) * 28
    for i, ln in enumerate(lines):
        tot = sum(d.textlength(w + " ", font=f) for w, _, _ in ln)
        x = (x0 + x1) / 2 - tot / 2
        for w, a, b in ln:
            col = INK if T >= a else (190, 186, 182)
            d.text((x, cy + i * 56), w, font=f, fill=col, anchor="lm"); x += d.textlength(w + " ", font=f)

def caja_narr(d, xy, pal, T, ancho=520):
    f = font(FT, 40)
    vis = [(w, a) for w, a, b in pal]
    lines, cur, wsum = [], [], 0
    for w, a in vis:
        tw = d.textlength(w + " ", font=f)
        if wsum + tw > ancho - 40 and cur: lines.append(cur); cur, wsum = [], 0
        cur.append((w, a)); wsum += tw
    if cur: lines.append(cur)
    x, y = xy; hh = 30 + 50 * len(lines)
    d.rectangle((x, y, x + ancho, y + hh), fill=PAPER, outline=INK, width=5)
    for i, ln in enumerate(lines):
        xx = x + 20
        for w, a in ln:
            d.text((xx, y + 40 + i * 50), w, font=f, fill=INK if T >= a else (190, 186, 182), anchor="lm"); xx += d.textlength(w + " ", font=f)

def frame(T):
    page = Image.new("RGB", (W, H), PAPER); d = ImageDraw.Draw(page)
    pal8 = palabras("N08")
    for key, t0, fn in (("A", TA, vineta_A), ("B", TB, vineta_B), ("C", TC, vineta_C), ("D", TD, vineta_D)):
        if T < t0: continue
        x0, y0, x1, y1 = P[key]
        u = clamp((T - t0) / .22)
        im = fn(T)
        s = 1.12 - .12 * ease(u)                                   # golpe de entrada de la viñeta
        if s != 1:
            im = im.resize((int(im.width * s), int(im.height * s)), Image.BILINEAR)
            ox = (im.width - (x1 - x0)) // 2; oy = (im.height - (y1 - y0)) // 2
            im = im.crop((ox, oy, ox + x1 - x0, oy + y1 - y0))
        page.paste(im, (x0, y0))
        d.rectangle((x0, y0, x1, y1), outline=INK, width=8)
    # textos de cada viñeta
    if T >= TA:
        caja_narr(d, (70, 250), [p for p in pal8 if p[1] < EV["paco"] - .05], T)
    if T >= TB:
        d.text((60, 1238), "PACO", font=font(FM, 130), fill=PAPER, anchor="ls", stroke_width=10, stroke_fill=INK)
        if T >= EV["41"]:
            k = back((T - EV["41"]) / .3)
            d.text((440, 790), "41 AÑOS", font=font(FM, 80 * max(k, .1)), fill=INK, anchor="mm", stroke_width=6, stroke_fill=PAPER)
    if T >= TB + .3:
        caja_narr(d, (300, 1100), [p for p in pal8 if EV["paco"] < p[1] < R.WT("N08", "Y") - .02], T, 290)
    if T >= TC + .3:
        caja_narr(d, (640, 1100), [p for p in pal8 if p[1] >= R.WT("N08", "Y") - .02], T, 380)
    if T >= TC:
        k = back((T - TC) / .3)
        d.text((820, 790), "9 MESES", font=font(FM, 92 * max(k, .1)), fill=RED, anchor="mm", stroke_width=7, stroke_fill=PAPER)
        d.text((820, 880), "SIN COBRAR", font=font(FM, 62 * max(k, .1)), fill=RED, anchor="mm", stroke_width=6, stroke_fill=PAPER)
    if T >= TD + .2:
        bocadillo(d, (70, 1300, 600, 1600), palabras("N09"), T, [(470, 1560), (640, 1700), (540, 1540)])
    # cabecera en tinta (la deuda en rojo)
    d.rectangle((40, 120, 1040, 196), fill=INK)
    d.text((70, 158), "EP.1 · DÍA 1", font=font(FM, 58), fill=PAPER, anchor="lm")
    d.text((1010, 158), "-182.400 €", font=font(FM, 58), fill=RED, anchor="rm")
    # cámara: se acerca a la viñeta activa
    act = "A"
    for key, t0 in (("B", TB), ("C", TC), ("D", TD)):
        if T >= t0 + .3: act = key
    x0, y0, x1, y1 = P[act]
    tz = {"A": TA, "B": TB, "C": TC, "D": TD}[act] + .3
    k = ease((T - tz) / .6) if T >= tz else 0
    z = 1.0
    cx = W / 2 + ((x0 + x1) / 2 - W / 2) * .35 * k; cy = H / 2 + ((y0 + y1) / 2 - H / 2) * .35 * k
    if z > 1.001:
        ww, hh = W / z, H / z
        bx = min(max(cx - ww / 2, 0), W - ww); by = min(max(cy - hh / 2, 0), H - hh)
        page = page.resize((W, H), Image.BICUBIC, box=(bx, by, bx + ww, by + hh))
    return page

if __name__ == "__main__":
    if sys.argv[1:] and sys.argv[1] == "still":
        for tt in sys.argv[2:]: frame(T0 + float(tt)).save(os.path.join(CLUB, "tmp", f"mg_{tt}.jpg"), quality=88)
    else:
        print(exportar(frame, "estilo_4_manga"))
