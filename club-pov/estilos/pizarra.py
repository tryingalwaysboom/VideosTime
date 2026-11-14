"""Estilo 2: pizarra de tácticas — todo dibujado con tiza que se va trazando sola."""
import math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from comun import *

HAND = "Kalam-Bold.ttf"
CHALK = (238, 238, 228); YCH = (255, 222, 90); RCH = (255, 120, 110); BCH = (140, 200, 255)
rng0 = np.random.default_rng(3)

def tablero():
    a = np.zeros((H, W, 3), np.float32) + np.array([30, 52, 42])
    rng = np.random.default_rng(5)
    for _ in range(26):                                    # borrones de tiza antiguos
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(80, 300)
        yy, xx = np.ogrid[0:H, 0:W]
        m = np.exp(-(((xx - x) / r) ** 2 + ((yy - y) / (r * .45)) ** 2))
        a += m[..., None] * rng.uniform(6, 16)
    n = rng.normal(0, 1, (H, W)).astype(np.float32)
    a += n[..., None] * 4
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    for y0, y1 in ((0, 70), (H - 70, H)):                  # marco de madera
        d.rectangle((0, y0, W, y1), fill=(122, 82, 48)); d.line((0, y1 if y0 == 0 else y0, W, y1 if y0 == 0 else y0), fill=(80, 50, 28), width=6)
        for i in range(0, W, 9): d.line((i, y0, i + 40, y1), fill=(132, 90, 54), width=1)
    d.rectangle((40, H - 96, 300, H - 70), fill=(150, 104, 62))   # repisa con tizas
    for x, c in ((80, CHALK), (130, YCH), (170, RCH)): d.rounded_rectangle((x, H - 112, x + 34, H - 98), 6, fill=c)
    return im

GRAIN = None
def grano():
    global GRAIN
    if GRAIN is None:
        n = np.random.default_rng(9).random((H, W)).astype(np.float32)
        n = np.asarray(Image.fromarray((n * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.7))).astype(np.float32) / 255
        GRAIN = Image.fromarray((np.clip((n - .3) * 2.6, 0, 1) * 255).astype(np.uint8))
    return GRAIN

# ------------------------------------------------------------ trazos
def circulo(cx, cy, rx, ry, a0=0, a1=360, n=48):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

def jitter(pts, amp=3, seed=0):
    r = np.random.default_rng(seed)
    return [(x + r.normal(0, amp), y + r.normal(0, amp)) for x, y in pts]

def parcial(pts, u):
    if u >= 1: return pts
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    tot = sum(seg) * u; out = [pts[0]]; acc = 0
    for i, s in enumerate(seg):
        if acc + s >= tot:
            f = (tot - acc) / max(s, 1e-6); x0, y0 = pts[i]; x1, y1 = pts[i + 1]
            out.append((x0 + (x1 - x0) * f, y0 + (y1 - y0) * f)); break
        acc += s; out.append(pts[i + 1])
    return out

def tiza(d, pts, w=9, col=CHALK, seed=0):
    if len(pts) < 2: return
    for k, off in enumerate((0, 2.2)):
        p = jitter(pts, .8, seed + k)
        d.line([(x + off, y + off * .5) for x, y in p], fill=col, width=int(w * (1 if k == 0 else .55)), joint="curve")

# elementos: (inicio, duración, lista de polilíneas, ancho, color)
SC = .82
def paco_trazos(cx, cy):
    L = paco_base(0, 0)
    L = L[6:] + L[:6]
    return [[(cx + x * SC, cy + y * SC) for x, y in pl] for pl in L]

def silueta(cx, cy):
    pts = circulo(0, 0, 130, 145) 
    body = [(-45, 160), (-240, 235), (-285, 600), (285, 600), (240, 235), (45, 160)]
    cap = [(-175, -60), (-100, -160), (70, -175), (175, -60)]
    f = lambda pl: [(cx + x * SC, cy + y * SC) for x, y in pl]
    return [f(pts), f(body), f(cap)]

def paco_base(cx, cy):
    L = []
    L += [circulo(cx - 70, cy - 52, 28, 8, 190, 350, 10), circulo(cx + 70, cy - 52, 28, 8, 190, 350, 10)]   # cejas
    L += [[(cx - 118, cy - 60), (cx - 135, cy - 30), (cx - 122, cy - 10)], [(cx + 118, cy - 60), (cx + 135, cy - 30), (cx + 122, cy - 10)]]   # pelo
    L += [circulo(cx - 245, cy + 420, 34, 26), circulo(cx + 245, cy + 420, 34, 26)]   # manos
    L += [circulo(cx, cy, 120, 135)]                                            # cabeza
    L += [circulo(cx + 5, cy - 68, 150, 95, 180, 360, 30)]   # gorra
    L += [circulo(cx + 10, cy - 64, 172, 14, -10, 190, 24)]
    L += [circulo(cx - 52, cy - 10, 44, 34), circulo(cx + 52, cy - 10, 44, 34), [(cx - 8, cy - 12), (cx + 8, cy - 12)]]   # gafas
    L += [[(cx - 10, cy + 5), (cx - 22, cy + 45), (cx + 8, cy + 50)]]           # nariz
    L += [[(cx - 95, cy + 80), (cx - 45, cy + 55), (cx, cy + 68), (cx + 45, cy + 55), (cx + 95, cy + 80), (cx + 50, cy + 82), (cx, cy + 74), (cx - 50, cy + 82), (cx - 95, cy + 80)]]  # bigote
    L += [circulo(cx - 128, cy + 5, 18, 32, 90, 270, 16), circulo(cx + 128, cy + 5, 18, 32, -90, 90, 16)]   # orejas
    L += [[(cx - 40, cy + 132), (cx - 45, cy + 175)], [(cx + 40, cy + 132), (cx + 45, cy + 175)]]           # cuello
    L += [[(cx - 45, cy + 175), (cx - 230, cy + 240), (cx - 270, cy + 560)], [(cx + 45, cy + 175), (cx + 230, cy + 240), (cx + 270, cy + 560)]]   # hombros/cuerpo
    L += [[(cx, cy + 180), (cx, cy + 560)]]                                                                  # cremallera
    L += [[(cx - 215, cy + 260), (cx - 245, cy + 560)], [(cx + 215, cy + 260), (cx + 245, cy + 560)]]       # rayas del chándal
    b = [(cx - 230, cy + 330), (cx + 230, cy + 330), (cx + 190, cy + 520), (cx - 190, cy + 520), (cx - 230, cy + 330)]   # cesta
    L += [b] + [[(cx - 215 + i * 8, cy + 395 + i * 60), (cx + 215 - i * 8, cy + 395 + i * 60)] for i in range(2)]
    L += [[(cx - 180, cy + 330), (cx - 140, cy + 290), (cx + 20, cy + 300), (cx + 60, cy + 330)], [(cx + 10, cy + 330), (cx + 60, cy + 295), (cx + 190, cy + 305), (cx + 200, cy + 330)]]   # camisetas
    return L

def taquillas():
    L = []
    for i in range(6):
        x = 40 + i * 168
        L += [[(x, 520), (x + 150, 520), (x + 150, 1080), (x, 1080), (x, 520)]]
        L += [[(x + 30, 570 + k * 22), (x + 120, 570 + k * 22)] for k in range(3)]
    L += [[(20, 1110), (1060, 1110)]]
    return L

def camisetas():
    L = []
    for i, x in enumerate((110, 360, 610, 860)):
        L += [[(x, 330), (x + 40, 310), (x + 70, 320), (x + 100, 310), (x + 140, 330), (x + 160, 380), (x + 125, 390), (x + 125, 470), (x + 15, 470), (x + 15, 390), (x - 20, 380), (x, 330)]]
    return L

CX, CY = 650, 830
ELEM = []
def build():
    tp = EV["paco"]
    ELEM.append((T0 + .05, .9, taquillas(), 5, (150, 175, 160)))
    ELEM.append((T0 + .5, .7, camisetas(), 5, (150, 175, 160)))
    ELEM.append((tp - .55, 1.6, paco_trazos(CX, CY), 10, CHALK))
build()

def texto(d, xy, s, size, col, anchor="mm", rot=0):
    d.text(xy, s, font=font(HAND, size), fill=col, anchor=anchor)

def karaoke(d, T):
    for t0, t1, g, who, lid in R.CH:
        if not (t0 - .04 <= T < t1 + .35) or lid not in ("N08", "N09"): continue
        nxt = [c for c in R.CH if c[0] > t0]
        if nxt and T >= nxt[0][0] - .04: continue
        f = font(HAND, 96)
        words = [p for p, _ in g]
        ws = [d.textlength(w + " ", font=f) for w in words]
        x = W / 2 - (sum(ws) - d.textlength(" ", font=f)) / 2
        for w, (a, b), wd in zip(words, [tt for _, tt in g], ws):
            col = YCH if a <= T < b + .05 else (CHALK if T >= a else (120, 140, 130))
            d.text((x, 1560), w.capitalize() if False else w, font=f, fill=col, anchor="lm"); x += wd
        if who == "P": texto(d, (W / 2, 1470), "— Paco —", 52, BCH)

def frame(T):
    im = BOARD.copy()
    layer = Image.new("L", (W, H), 0); col_l = Image.new("RGB", (W, H), CHALK)
    dl = ImageDraw.Draw(layer); dc = ImageDraw.Draw(col_l)
    def draw_set(pts_list, w, col, u, seed=0):
        n = len(pts_list)
        for i, pts in enumerate(pts_list):
            ui = clamp(u * n - i)
            if ui <= 0: break
            p = parcial(pts, ui)
            tiza(dl, p, w, 255, seed + i); tiza(dc, p, w + 2, col, seed + i)
    for t0, dur, L, w, col in ELEM[:2]:
        if T >= t0: draw_set(L, w, col, clamp((T - t0) / dur))
    tp_ = ELEM[2][0]
    if T >= tp_:
        k = int(255 * clamp((T - tp_) / .4))
        er = Image.new("L", (W, H), 0); de = ImageDraw.Draw(er)
        for pl in silueta(CX, CY): de.polygon(pl, fill=k)
        er = er.filter(ImageFilter.GaussianBlur(10))
        layer.paste(0, (0, 0), er)
        im.paste(Image.new("RGB", (W, H), (34, 58, 47)), (0, 0), er.point(lambda v: int(v * .8)))
        dl = ImageDraw.Draw(layer)
    t0, dur, L, w, col = ELEM[2]
    if T >= t0: draw_set(L, w, col, clamp((T - t0) / dur))
    # boca de Paco (habla)
    if T >= EV["paco"] + 1:
        m = boca(T)
        my = CY + 98 * SC
        pts = circulo(CX, my, 22, 3 + 18 * m, 0, 360, 20) if m > .08 else [(CX - 20, my), (CX + 20, my)]
        tiza(dl, pts, 7, 255, 77); tiza(dc, pts, 9, CHALK, 77)
        if (T % 3.4) < .12:                                   # parpadeo
            for ex in (CX - 52 * SC, CX + 52 * SC): ey = CY - 10 * SC; tiza(dl, [(ex - 16, ey), (ex + 16, ey)], 7, 255); tiza(dc, [(ex - 16, ey), (ex + 16, ey)], 9, CHALK)
        else:
            for ex in (CX - 52 * SC, CX + 52 * SC): ey = CY - 10 * SC; dl.ellipse((ex - 7, ey - 7, ex + 7, ey + 7), fill=255); dc.ellipse((ex - 7, ey - 7, ex + 7, ey + 7), fill=CHALK)
    # anotaciones
    tp = EV["paco"]
    if T >= tp + .3:
        u = clamp((T - tp - .3) / .5)
        p = parcial([(300, 560), (390, 600), (450, 680)], u); tiza(dl, p, 7, 255, 5); tiza(dc, p, 9, YCH, 5)
        if u > .5: dl.text((60, 470), "PACO", font=font(HAND, 120), fill=255); dc.text((60, 470), "PACO", font=font(HAND, 120), fill=YCH)
    for key, s, xy, col in (("41", "41 años", (195, 880), CHALK), ("9", "9 meses", (195, 1110), RCH)):
        t = EV[key]
        if T >= t:
            dl.text(xy, s, font=font(HAND, 84), fill=255, anchor="mm"); dc.text(xy, s, font=font(HAND, 84), fill=col, anchor="mm")
            u = clamp((T - t) / .5)
            ring = parcial(jitter(circulo(xy[0], xy[1] + 6, 165, 70, -100, 250, 40), 4, 11), u)
            tiza(dl, ring, 6, 255, 2); tiza(dc, ring, 8, col, 2)
    if T >= EV["9"] + .5:                                      # sueldo tachado
        u = clamp((T - EV["9"] - .5) / .4)
        dl.text((195, 1270), "€", font=font(HAND, 130), fill=255, anchor="mm"); dc.text((195, 1270), "€", font=font(HAND, 130), fill=RCH, anchor="mm")
        for a, b in (((115, 1200), (275, 1340)), ((275, 1200), (115, 1340))):
            p = parcial([a, b], u); tiza(dl, p, 10, 255, 4); tiza(dc, p, 12, RCH, 4)
    # aplicar textura de tiza
    m = Image.fromarray((np.asarray(layer).astype(np.float32) * (np.asarray(grano()).astype(np.float32) / 255 * .85 + .15)).astype(np.uint8))
    m = m.filter(ImageFilter.GaussianBlur(.8))
    im.paste(col_l, (0, 0), m)
    d = ImageDraw.Draw(im)
    # cabecera escrita a tiza
    d.text((60, 140), "EP.1 · DÍA 1", font=font(HAND, 60), fill=YCH, anchor="lm")
    d.text((W - 60, 140), "-182.400 €", font=font(HAND, 60), fill=RCH, anchor="rm")
    d.line((60, 182, W - 60, 182), fill=(170, 190, 175), width=3)
    karaoke(d, T)
    return im

BOARD = tablero()

if __name__ == "__main__":
    if sys.argv[1:] and sys.argv[1] == "still":
        for t in sys.argv[2:]: frame(T0 + float(t)).save(os.path.join(CLUB, "tmp", f"pz_{t}.jpg"), quality=88)
    else:
        print(exportar(frame, "estilo_2_pizarra_tiza"))
