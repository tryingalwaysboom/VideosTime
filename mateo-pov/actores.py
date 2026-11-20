"""Personajes articulados (Mateo, Leo, la tía) dibujados en vectorial con supersampling: cabeza con mirada, cejas, párpados y
boca expresivos; brazos con codo (IK de dos huesos) y manos con dedos que agarran. Mismo estilo plano con contorno que el resto de la serie.
Uso: persona(c, quien, cx, cy, S, P, dino_cb=None)  -> dibuja sobre c (RGBA 1080x1920), (cx,cy)=centro de la cabeza en pantalla, S=px por unidad."""
import math
from PIL import Image, ImageDraw

SS = 2
OL = (27, 21, 48)
W_, H_ = 1080, 1920

ESTILOS = {
    "mateo": dict(piel=(243, 194, 155), piel_s=(224, 160, 124), pelo=(86, 52, 34), ropa=(82, 178, 104), ropa_s=(54, 142, 80), cuello=(60, 150, 86),
                  hx=205, hy=215, hs=1.16, torso=272, logo=True, mejilla=(236, 130, 124), iris=(112, 70, 48)),
    "leo": dict(piel=(246, 200, 164), piel_s=(226, 166, 130), pelo=(62, 40, 30), ropa=(255, 160, 92), ropa_s=(228, 124, 62), cuello=(238, 140, 72),
                hx=196, hy=206, hs=1.14, torso=262, logo=False, mejilla=(238, 134, 126), iris=(70, 52, 40), estrellas=True),
    "tia": dict(piel=(238, 192, 160), piel_s=(214, 160, 128), pelo=(66, 44, 40), ropa=(232, 122, 152), ropa_s=(196, 90, 122), cuello=(210, 100, 132),
                hx=158, hy=178, torso=262, logo=False, mejilla=(228, 138, 130), iris=(80, 58, 46), adulta=True),
}
JACKET = (72, 118, 196); JACKET_S = (50, 90, 160); JACKET_L = (118, 166, 232)


def ik(S, Hd, l1, l2, bend):
    dx, dy = Hd[0] - S[0], Hd[1] - S[1]
    d = math.hypot(dx, dy) or 1e-3
    dc = min(max(d, abs(l1 - l2) + 1e-3), l1 + l2 - 1e-3)
    a = (l1 * l1 - l2 * l2 + dc * dc) / (2 * dc)
    h = math.sqrt(max(l1 * l1 - a * a, 0))
    ux, uy = dx / d, dy / d
    px, py = S[0] + ux * a, S[1] + uy * a
    E = (px - uy * h * bend, py + ux * h * bend)
    Hc = (S[0] + ux * dc, S[1] + uy * dc)
    return E, Hc


def ellpts(cx, cy, rx, ry, rot=0, n=40, a0=0, a1=360):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def bez(p0, p1, p2, n=14):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
            for t in [i / n for i in range(n + 1)]]


class Pen:
    def __init__(s, x0, y0, x1, y1, S):
        s.x0, s.y0, s.S = x0, y0, S
        s.k = S * SS
        s.w, s.h = max(2, int((x1 - x0) * s.k)), max(2, int((y1 - y0) * s.k))
        s.im = Image.new("RGBA", (s.w, s.h), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.im)
        s.lw = 7

    def p(s, pt): return ((pt[0] - s.x0) * s.k, (pt[1] - s.y0) * s.k)
    def pts(s, L): return [s.p(q) for q in L]

    def poly(s, L, fill, ol=True, lw=None):
        P = s.pts(L)
        if fill is not None: s.d.polygon(P, fill=fill)
        if ol: s.d.line(P + [P[0]], fill=OL, width=int((lw or s.lw) * s.k), joint="curve")

    def line(s, L, col, w, cap=True):
        P = s.pts(L); wk = max(1, int(w * s.k))
        s.d.line(P, fill=col, width=wk, joint="curve")
        if cap:
            r = wk / 2
            for q in (P[0], P[-1]): s.d.ellipse((q[0] - r, q[1] - r, q[0] + r, q[1] + r), fill=col)

    def ell(s, cx, cy, rx, ry, fill, ol=True, rot=0, lw=None, n=44):
        s.poly(ellpts(cx, cy, rx, ry, rot, n), fill, ol, lw)

    def tube(s, a, b, w, fill, lw=None):
        lw = lw or s.lw
        s.line([a, b], OL, w + 2 * lw)
        s.line([a, b], fill, w)


def _sleeve_shade(pen, a, b, w, col):
    """Sombra a un lado de la manga."""
    dx, dy = b[0] - a[0], b[1] - a[1]; d = math.hypot(dx, dy) or 1
    nx, ny = -dy / d, dx / d
    o = w * .28
    pen.line([(a[0] + nx * o, a[1] + ny * o), (b[0] + nx * o, b[1] + ny * o)], col, w * .34, cap=False)


def mano(pen, E, H, st, grip, thumb=1.0, side=1, ropa=None):
    """Mano con dedos. grip 0 = abierta, 1 = puño. thumb: 1 = pulgar fuera."""
    dx, dy = H[0] - E[0], H[1] - E[1]; d = math.hypot(dx, dy) or 1
    ux, uy = dx / d, dy / d
    nx, ny = -uy, ux
    ang = math.degrees(math.atan2(uy, ux))
    pc = (H[0] + ux * 26, H[1] + uy * 26)
    piel = st["piel"]
    # pulgar (detrás de la palma)
    tp = (pc[0] + nx * 40 * side - ux * 4, pc[1] + ny * 40 * side - uy * 4)
    pen.ell(tp[0], tp[1], 30, 18 + 4 * (1 - grip), piel, rot=ang + 40 * side * (1 - .5 * grip) * thumb)
    # dedos
    n = 4
    for i in range(n):
        o = (i - 1.5) * 25
        L = 40 * (1 - grip) + 22 * grip
        fc = (pc[0] + ux * (24 + L * .5 * (1 - .4 * grip)) + nx * o, pc[1] + uy * (24 + L * .5 * (1 - .4 * grip)) + ny * o)
        pen.ell(fc[0], fc[1], L * .5 + 12, 13.5, piel, rot=ang, lw=5)
    pen.ell(pc[0], pc[1], 50, 47, piel)
    # nudillos / pliegue
    if grip > .35:
        for i in range(3):
            o = (i - 1) * 21
            pen.line([(pc[0] + ux * 14 + nx * o - ux * 3, pc[1] + uy * 14 + ny * o - uy * 3), (pc[0] + ux * 22 + nx * o, pc[1] + uy * 22 + ny * o)], st["piel_s"], 4)


def cabeza(pen, st, P, T):
    """Dibuja cabeza y cara. Rotación de la cabeza alrededor de la base del cuello."""
    rot = math.radians(P.get("head_rot", 0))
    ox, oy = P.get("head_dx", 0), P.get("head_dy", 0)
    pivot = (0, 230)
    cr, sr = math.cos(rot), math.sin(rot)

    hs = st.get("hs", 1.0)

    def Hh(q):
        x, y = (q[0] - pivot[0]) * hs, (q[1] - pivot[1]) * hs
        return (pivot[0] + x * cr - y * sr + ox, pivot[1] + x * sr + y * cr + oy)

    def tr(L): return [Hh(q) for q in L]

    hx, hy = st["hx"], st["hy"]
    adulta = st.get("adulta")
    piel, pelo = st["piel"], st["pelo"]
    # pelo trasero (tía: pelo largo detrás)
    if adulta and P.get("_back"):
        pen.poly(tr([(-hx - 24, -40), (-hx - 40, 220), (-hx + 30, 330), (hx - 30, 330), (hx + 40, 220), (hx + 24, -40)]), pelo)
        return
    # orejas
    for sx in (-1, 1): pen.poly(tr(ellpts(sx * (hx - 4), 28, 32, 42)), piel)
    # cabeza
    pen.poly(tr(ellpts(0, 0, hx, hy, n=60)), piel)
    # sombra bajo flequillo / mejilla
    pen.poly(tr(ellpts(hx * .55, hy * .34, hx * .46, hy * .62, rot=-20, n=40, a0=-70, a1=120)), None, False)
    # mejillas
    mej = P.get("mejilla", .55) * (1 + .15 * math.sin(T * 2))
    ov = Image.new("RGBA", (pen.w, pen.h), (0, 0, 0, 0)); dv = ImageDraw.Draw(ov)
    for sx in (-1, 1):
        pts = [pen.p(q) for q in tr(ellpts(sx * (hx * .6), 72, 46, 30, n=30))]
        dv.polygon(pts, fill=st["mejilla"] + (int(150 * mej),))
    pen.im.alpha_composite(ov); pen.d = ImageDraw.Draw(pen.im)

    # ojos
    look = P.get("look", (0, 0)); blink = P.get("blink", 0); happy = P.get("ojos_felices", 0)
    ey = -4; ex = hx * .4
    brow_l = P.get("brow_l", (0, 0)); brow_r = P.get("brow_r", (0, 0))
    llor = P.get("lloro", 0); brillo = P.get("brillo", 0)
    adr = P.get("parpado", 0)  # 0..1 párpados caídos (sueño)
    for idx, sx in enumerate((-1, 1)):
        cx = sx * ex
        if happy > .5:
            pen.line(tr(bez((cx - 44, ey + 14), (cx, ey - 40), (cx + 44, ey + 14), 14)), OL, 11)
        elif blink > .88:
            pen.line(tr(bez((cx - 44, ey + 4), (cx, ey + 22), (cx + 44, ey + 4), 12)), OL, 10)
        else:
            rx, ry = 49, 55
            pen.poly(tr(ellpts(cx, ey, rx, ry)), (255, 255, 255))
            gx, gy = look[0] * 17, look[1] * 15
            pen.poly(tr(ellpts(cx + gx, ey + gy, 31, 33)), st["iris"], ol=False)
            pen.poly(tr(ellpts(cx + gx, ey + gy, 17, 18)), (18, 14, 30), ol=False)
            pen.poly(tr(ellpts(cx + gx - 9, ey + gy - 11, 8.5, 8.5)), (255, 255, 255), ol=False)
            pen.poly(tr(ellpts(cx + gx + 11, ey + gy + 11, 4.5, 4.5)), (255, 255, 255), ol=False)
            if brillo:
                pen.poly(tr(ellpts(cx + gx + 4, ey + gy + 6, 12 * brillo, 7 * brillo)), (255, 255, 255), ol=False)
            # párpado superior: parpadeo + caída
            cover = max(blink, adr * .6, P.get("entorna", 0) * .45)
            if cover > .02:
                ytop = ey - ry - 4
                ybot = ytop + (2 * ry + 8) * cover
                pts = [(cx - rx - 4, ytop - 10), (cx + rx + 4, ytop - 10)] + [(cx + rx + 4 - (2 * rx + 8) * t / 8, ybot + 8 * math.sin(math.pi * t / 8)) for t in range(9)]
                pen.poly(tr(pts), piel, ol=False)
                pen.line(tr([(cx - rx - 2, ybot + 2), (cx, ybot + 10), (cx + rx + 2, ybot + 2)]), OL, 8)
            # contorno del ojo
            pen.line(tr(ellpts(cx, ey, rx, ry, a0=200, a1=340, n=20)), OL, 7, cap=False)
            if llor > 0:  # ojos llorosos
                pen.line(tr(bez((cx - 44, ey + 40), (cx, ey + 66), (cx + 44, ey + 40), 10)), (150, 205, 245), 9 * min(1, llor))
        # cejas
        bl = brow_l if sx < 0 else brow_r
        raise_, tilt = bl
        by = -100 - raise_ * 34
        inner = (cx - sx * 38, by - tilt * 26)   # extremo interior (hacia el centro)
        outer = (cx + sx * 56, by + tilt * 12 + 4)
        mid = ((inner[0] + outer[0]) / 2, min(inner[1], outer[1]) - 10 + (tilt * -4))
        pen.line(tr(bez(inner, mid, outer, 10)), (58, 36, 24) if not adulta else (40, 28, 28), 21)

    # nariz
    pen.line(tr(bez((-6, 40), (14, 70), (-8, 78), 8)), OL, 8)
    # boca
    m = P.get("boca", "flat"); ab = P.get("abre", 0)
    my = 126
    if m == "sonrisa":
        pen.line(tr(bez((-58, my - 14), (0, my + 52), (58, my - 14), 16)), OL, 10)
    elif m == "sonrisa_abierta":
        pts = [(-62, my - 14), (62, my - 14)] + [(62 * math.cos(math.radians(a)), my - 14 + 70 * math.sin(math.radians(a))) for a in range(0, 181, 12)]
        pen.poly(tr(pts), (124, 34, 52))
        pen.poly(tr([(-34, my + 30), (34, my + 30)] + [(34 * math.cos(math.radians(a)), my + 30 - 18 * math.sin(math.radians(a))) for a in range(0, 181, 15)]), (236, 104, 124), ol=False)
    elif m == "triste":
        pen.line(tr(bez((-50, my + 20), (0, my - 22), (50, my + 20), 16)), OL, 10)
    elif m == "tiembla":
        q = math.sin(T * 26) * 4
        pen.line(tr(bez((-46, my + 20 + q), (0, my - 14 - q), (46, my + 20 + q), 16)), OL, 10)
    elif m == "llora":
        top = bez((-56, my + 14), (0, my - 30), (56, my + 14), 14)
        bot = ellpts(0, my + 14, 56, 40 + 22 * ab, a0=0, a1=180, n=18)
        pen.poly(tr(top + bot), (124, 34, 52))
        pen.poly(tr(ellpts(0, my + 14 + (40 + 22 * ab) * .62, 30, 16 + 6 * ab, a0=180, a1=360, n=12)), (236, 104, 124), ol=False)
    elif m == "habla":
        o = 8 + 52 * ab
        pen.poly(tr(ellpts(0, my + o * .2, 46 - 6 * ab, o, n=30)), (124, 34, 52))
        if o > 26: pen.poly(tr(ellpts(0, my + o * .75, 28, o * .38, a0=180, a1=360, n=14)), (236, 104, 124), ol=False)
    elif m == "o":
        pen.poly(tr(ellpts(0, my + 6, 20 + 8 * ab, 24 + 10 * ab)), (124, 34, 52))
    elif m == "sorbe":   # boca de lado, labio inferior
        pen.line(tr(bez((-40, my + 10), (4, my + 26), (46, my - 6), 12)), OL, 10)
    else:
        pen.line(tr([(-34, my + 4), (34, my + 4)]), OL, 9)
    # lágrimas
    tz = P.get("lagrimas", 0)
    if tz > 0:
        for sx in (-1, 1):
            for k in range(3):
                u = ((T * (1.1 + .2 * k) + k * .37 + (0 if sx < 0 else .2)) % 1)
                x = sx * (ex + 6 + 8 * k) + sx * 10 * u
                y = ey + 56 + 190 * u
                a = tz * (1 - u * .35)
                pen.poly(tr(ellpts(x, y, 11 * a + 3, 18 * a + 4, n=14)), (150, 205, 248), ol=False)
                pen.poly(tr(ellpts(x - 3, y - 4, 3, 5, n=8)), (230, 245, 255), ol=False)
            # reguero fijo
            pen.line(tr([(sx * (ex + 4), ey + 58), (sx * (ex + 14), ey + 170)]), (150, 205, 248), 15 * tz)
    # moco (Leo)
    if P.get("moco", 0) > 0:
        a = P["moco"]
        pen.poly(tr(ellpts(10, 92 + 12 * a, 11 * a + 2, 20 * a + 4, n=12)), (190, 225, 245), ol=False)
    # flequillo
    if adulta:
        pen.poly(tr([(-hx - 18, -30)] + ellpts(0, -8, hx + 14, hy + 18, a0=180, a1=360, n=30) + [(hx + 18, -30), (hx - 20, -86), (hx * .35, -118), (0, -100), (-hx * .4, -130), (-hx + 20, -92)]), pelo)
        # mechones sueltos (recién levantada)
    else:
        top = ellpts(0, -8, hx + 12, hy + 16, a0=180, a1=360, n=36)
        fring = [(hx + 8, -50), (hx * .78, -118), (hx * .52, -100), (hx * .26, -146), (0, -112), (-hx * .26, -150), (-hx * .52, -108), (-hx * .76, -128), (-hx - 8, -50)]
        pen.poly(tr(top + fring[:0] + fring), pelo)
        pen.poly(tr([(-34, -hy + 2), (-48, -hy - 44), (-8, -hy - 40), (14, -hy + 4)]), pelo)
        pen.poly(tr([(22, -hy + 2), (62, -hy - 50), (84, -hy - 22), (60, -hy + 14)]), pelo)
        # brillo del pelo
        pen.line(tr(bez((-hx * .62, -hy * .62), (-hx * .2, -hy * .98), (hx * .34, -hy * .86), 10)), (130, 88, 62), 12, cap=True)


def persona(c, quien, cx, cy, S, P, dino_cb=None, T=0.0):
    """Dibuja el personaje en c. Parámetros en P (ver cabeza / brazos)."""
    st = ESTILOS[quien]
    # región local visible
    x0, x1 = max(-760, (-60 - cx) / S), min(760, (W_ + 60 - cx) / S)
    y0, y1 = -hy_top(st), min(1700, (H_ + 40 - cy) / S)
    if x1 <= x0 or y1 <= y0: return
    pen = Pen(x0, y0, x1, y1, S)
    br = P.get("resp", 0) * 7 * math.sin(T * 2.6)
    lean = P.get("lean", 0)
    tors = st["torso"]; adulta = st.get("adulta")
    chaqueta = P.get("chaqueta", 0)
    ropa, ropa_s = st["ropa"], st["ropa_s"]
    # --- hombros / brazos objetivo
    shL = (-tors * .86 + lean, 346 + br); shR = (tors * .86 + lean, 346 + br)
    l1, l2 = (210, 200) if not adulta else (230, 220)
    slv = JACKET if chaqueta else ropa
    slv_s = JACKET_S if chaqueta else ropa_s

    def brazo(sh, key, bend, side):
        tgt = P.get(key, (sh[0] + side * 30, sh[1] + 400))
        E, Hc = ik(sh, tgt, l1, l2, bend)
        return sh, E, Hc

    armL = brazo(shL, "mano_i", P.get("codo_i", 1), -1)
    armR = brazo(shR, "mano_d", P.get("codo_d", -1), 1)

    def dibuja_brazo(arm, grip, side, cuff=True):
        sh, E, Hc = arm
        pen.tube(sh, E, 112, slv)
        pen.tube(E, Hc, 96, slv)
        pen.ell(E[0], E[1], 48, 48, slv, ol=False)
        # puño de la manga
        dx, dy = Hc[0] - E[0], Hc[1] - E[1]; d = math.hypot(dx, dy) or 1
        ux, uy = dx / d, dy / d
        cuffc = (Hc[0] - ux * 8, Hc[1] - uy * 8)
        nx, ny = -uy, ux
        pen.poly([(cuffc[0] + nx * 52 - ux * 20, cuffc[1] + ny * 52 - uy * 20), (cuffc[0] - nx * 52 - ux * 20, cuffc[1] - ny * 52 - uy * 20),
                  (cuffc[0] - nx * 52 + ux * 6, cuffc[1] - ny * 52 + uy * 6), (cuffc[0] + nx * 52 + ux * 6, cuffc[1] + ny * 52 + uy * 6)],
                 JACKET_S if chaqueta else st["cuello"], lw=6)
        mano(pen, E, Hc, st, grip, thumb=P.get("pulgar", 1), side=side)

    # ---- cuerpo
    def torso():
        yS = 300 + br
        pts = [(-46 + lean * .3, 246), (-176 + lean * .5, 268 + br), (-tors + lean, 340 + br), (-tors - 8 + lean, 470), (-tors - 12, 1700),
               (tors + 12, 1700), (tors + 8 + lean, 470), (tors + lean, 340 + br), (176 + lean * .5, 268 + br), (46 + lean * .3, 246)]
        # cuello
        pen.poly([(-40 + lean * .3, 170), (40 + lean * .3, 170), (44 + lean * .3, 270), (-44 + lean * .3, 270)], st["piel"])
        pen.poly([(-40 + lean * .3, 232), (40 + lean * .3, 232), (44 + lean * .3, 270), (-44 + lean * .3, 270)], st["piel_s"], ol=False)
        pen.poly(pts, ropa)
        # sombra lateral
        pen.poly([(tors * .55 + lean, 330 + br), (tors + lean, 340 + br), (tors + 8 + lean, 470), (tors + 12, 1700), (tors * .58, 1700), (tors * .5, 520)], ropa_s, ol=False)
        pen.poly(pts, None)
        # cuello de la camiseta
        pen.poly(ellpts(lean * .3, 262, 86, 46, a0=0, a1=180, n=20), st["cuello"])
        if st.get("logo"):
            lx, ly = -86 + lean, 560
            Lg = [(-70, 50), (-52, 14), (-20, 0), (6, -26), (44, -30), (70, -8), (60, 18), (30, 20), (22, 46)]
            pen.line([(lx + a, ly + b) for a, b in Lg], (252, 250, 240), 11)
            pen.line([(lx - 40, ly + 50), (lx - 40, ly + 82)], (252, 250, 240), 11); pen.line([(lx + 6, ly + 30), (lx + 6, ly + 82)], (252, 250, 240), 11)
        if st.get("estrellas"):
            for (a, b) in ((-120, 520), (90, 600), (-30, 720), (140, 470)):
                pen.poly([(lx2, ly2) for lx2, ly2 in [(a + lean + 18 * math.cos(math.radians(90 + 72 * i + (36 if i % 2 else 0))) * (1 if i % 2 == 0 else .45) * 1.6,
                                                         b - 18 * math.sin(math.radians(90 + 72 * i + (36 if i % 2 else 0))) * (1 if i % 2 == 0 else .45) * 1.6) for i in range(10)]],
                         (255, 224, 120), ol=False)
        if adulta:  # cinturón de la bata
            pen.poly([(-tors - 10 + lean, 760), (tors + 10 + lean, 760), (tors + 10 + lean, 820), (-tors - 10 + lean, 820)], ropa_s)
            pen.poly([(-40, 262), (0, 520), (40, 262)], st["piel"], ol=True)
        if chaqueta:
            jp = [(-62 + lean * .3, 248), (-190 + lean * .5, 266 + br), (-tors - 6 + lean, 340 + br), (-tors - 12 + lean, 470), (-tors - 16, 1700),
                  (tors + 16, 1700), (tors + 12 + lean, 470), (tors + 6 + lean, 340 + br), (190 + lean * .5, 266 + br), (62 + lean * .3, 248)]
            pen.poly(jp, JACKET)
            pen.poly([(tors * .5 + lean, 340 + br), (tors + 6 + lean, 340 + br), (tors + 12 + lean, 470), (tors + 16, 1700), (tors * .52, 1700), (tors * .46, 560)], JACKET_S, ol=False)
            pen.poly(jp, None)
            pen.line([(lean * .3, 292), (lean * .3 + 2, 1700)], (226, 228, 240), 9, cap=False)   # cremallera
            for k in range(16):
                pen.line([(lean * .3 - 9, 300 + 36 * k), (lean * .3 + 9, 300 + 36 * k)], (170, 176, 200), 5, cap=False)
            pen.poly([(lean * .3 - 18, 288), (lean * .3 + 18, 288), (lean * .3 + 14, 340), (lean * .3 - 14, 340)], (232, 232, 242), lw=5)  # tirador
            # cuello alto
            pen.poly([(-88 + lean * .3, 244), (-14 + lean * .3, 300), (-30 + lean * .3, 226)], JACKET_L)
            pen.poly([(88 + lean * .3, 244), (14 + lean * .3, 300), (30 + lean * .3, 226)], JACKET_L)
            pen.poly([(-tors * .74 + lean, 700), (-tors * .3 + lean, 700), (-tors * .3 + lean, 800), (-tors * .74 + lean, 780)], JACKET_S, lw=5)  # bolsillo

    # orden: [dino detrás] [brazos detrás] torso, cabeza, [dino], brazos
    if P.get("dino_atras") and dino_cb: _flush(c, pen, cx, cy); dino_cb(c); pen = _nuevo(pen)
    if P.get("brazos_atras"):
        dibuja_brazo(armL, P.get("grip_i", .3), -1); dibuja_brazo(armR, P.get("grip_d", .3), 1)
    if adulta: cabeza(pen, st, dict(P, _back=1), T)
    torso()
    cabeza(pen, st, P, T)
    _flush(c, pen, cx, cy)
    pen = _nuevo(pen)
    if dino_cb and not P.get("dino_atras"): dino_cb(c)
    if not P.get("brazos_atras"):
        dibuja_brazo(armL, P.get("grip_i", .3), -1)
        dibuja_brazo(armR, P.get("grip_d", .3), 1)
        _flush(c, pen, cx, cy)
    else:
        _flush(c, pen, cx, cy)
    return {"mano_i": armL[2], "mano_d": armR[2]}


def hy_top(st): return (st["hy"] + 260) * st.get("hs", 1.0) + (60 if st.get("adulta") else 0)


def _flush(c, pen, cx, cy):
    im = pen.im.resize((max(1, pen.w // SS), max(1, pen.h // SS)), Image.LANCZOS)
    c.alpha_composite(im, (int(round(cx + pen.x0 * pen.S)), int(round(cy + pen.y0 * pen.S)))) if _fits(c, im, cx, cy, pen) else _paste_clip(c, im, cx + pen.x0 * pen.S, cy + pen.y0 * pen.S)
    pen.im.paste((0, 0, 0, 0), (0, 0, pen.w, pen.h))


def _nuevo(pen):
    pen.d = ImageDraw.Draw(pen.im)
    return pen


def _fits(c, im, cx, cy, pen):
    x, y = int(round(cx + pen.x0 * pen.S)), int(round(cy + pen.y0 * pen.S))
    return x >= 0 and y >= 0 and x + im.width <= c.width and y + im.height <= c.height


def _paste_clip(c, im, x, y):
    x, y = int(round(x)), int(round(y))
    sx0, sy0 = max(0, -x), max(0, -y)
    sx1, sy1 = min(im.width, c.width - x), min(im.height, c.height - y)
    if sx1 <= sx0 or sy1 <= sy0: return
    c.alpha_composite(im.crop((sx0, sy0, sx1, sy1)), (x + sx0, y + sy0))


def brazo_mama(c, x, y, S, apret=0.0, T=0.0):
    """Mano de la madre (punto de vista): antebrazo que sube desde abajo a la derecha; x,y = muñeca en pantalla."""
    st = dict(ESTILOS["tia"]); 
    pen = Pen(-420, -330, 520, 900, S)
    a = (330, 760); b = (0, 0)
    pen.tube(a, b, 132, (226, 132, 126))
    pen.poly([(b[0] - 70, b[1] + 70), (b[0] + 70, b[1] - 10), (b[0] + 90, b[1] + 40), (b[0] - 50, b[1] + 130)], (244, 214, 196), lw=6)
    mano(pen, (120, 160), (0, 0), st, .25 + .4 * apret, thumb=1, side=-1)
    _flush(c, pen, x, y)
