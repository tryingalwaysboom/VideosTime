"""Fachada detallada de "La casa de 1 dólar" (se reutiliza en todos los episodios).
Se dibuja al doble de tamaño y se reduce para que todo quede nítido."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import art as A
from art import PW, PH, lerp, quad_pt, sub_quad, towards, font, F_ANTON

K = 2

class D:
    """ImageDraw que trabaja en coordenadas de la plancha y pinta a K aumentos."""
    def __init__(self, im): self.d = ImageDraw.Draw(im)
    def _p(self, pts): return [(x * K, y * K) for x, y in pts]
    def poly(self, pts, fill=None, outline=None, width=1): self.d.polygon(self._p(pts), fill=fill, outline=outline, width=int(width * K))
    def line(self, pts, fill, width=1, joint=None): self.d.line(self._p(pts), fill=fill, width=max(1, int(width * K)), joint=joint)
    def ell(self, b, fill=None, outline=None, width=1): self.d.ellipse([v * K for v in b], fill=fill, outline=outline, width=int(width * K))
    def rect(self, b, fill=None, outline=None, width=1): self.d.rectangle([v * K for v in b], fill=fill, outline=outline, width=int(width * K))
    def arc(self, b, a0, a1, fill, width=1): self.d.arc([v * K for v in b], a0, a1, fill=fill, width=int(width * K))
    def text(self, xy, s, size, fill, anchor="mm"): self.d.text((xy[0] * K, xy[1] * K), s, font=font(F_ANTON, size * K), fill=fill, anchor=anchor)

def soft(size, fn, blur):
    im = Image.new("RGBA", size, (0, 0, 0, 0)); fn(D(im)); return im.filter(ImageFilter.GaussianBlur(blur * K))

def qline(d, q, u0, v0, u1, v1, fill, width):
    d.line([quad_pt(q, u0, v0), quad_pt(q, u1, v1)], fill, width)

def shade(c):
    return tuple(max(0, min(255, int(v))) for v in c)

def plate_casa_hd():
    S = (PW * K, PH * K)
    im = A.grad(PW, PH, (5, 8, 24), (44, 50, 96), 0, 1560).resize(S, Image.BILINEAR)
    d = D(im); rng = random.Random(21)
    # ---------------- cielo
    for _ in range(260):
        x, y = rng.uniform(0, PW), rng.uniform(0, 1250); r = rng.choice((.8, 1, 1.4, 2, 2.6))
        d.ell((x - r, y - r, x + r, y + r), fill=(230, 235, 255, rng.randrange(80, 255)))
    mx, my = 1040, 470
    im.alpha_composite(soft(S, lambda dd: dd.ell((mx - 460, my - 460, mx + 460, my + 460), fill=(140, 160, 255, 60)), 130))
    im.alpha_composite(soft(S, lambda dd: dd.ell((mx - 200, my - 200, mx + 200, my + 200), fill=(220, 230, 255, 120)), 40))
    d = D(im); d.ell((mx - 120, my - 120, mx + 120, my + 120), fill=(242, 242, 230))
    for cx, cy, r, a in ((-40, -30, 28, 255), (35, 22, 18, 255), (-12, 58, 14, 255), (52, -56, 11, 255), (10, -5, 8, 255), (-70, 30, 9, 255)):
        d.ell((mx + cx - r, my + cy - r, mx + cx + r, my + cy + r), fill=(214, 214, 204, a))
    for cx, cy, rw, rh in ((780, 560, 340, 58), (1200, 615, 270, 44), (300, 380, 400, 70), (980, 330, 230, 38), (560, 760, 300, 40)):
        im.alpha_composite(soft(S, lambda dd: dd.ell((cx - rw, cy - rh - 8, cx + rw, cy + rh - 8), fill=(150, 160, 210, 70)), 10))   # borde iluminado
        im.alpha_composite(soft(S, lambda dd: dd.ell((cx - rw, cy - rh, cx + rw, cy + rh), fill=(14, 16, 38, 215)), 18))
    d = D(im)
    # ---------------- fondo: colinas, pueblo lejano, arboleda
    pts = [(0, 1500)] + [(x, 1468 - 62 * math.sin(x / 260) - 28 * math.sin(x / 90 + 1)) for x in range(0, PW + 20, 20)] + [(PW, PH), (0, PH)]
    d.poly(pts, fill=(20, 24, 48))
    for x0 in (60, 160, 230):   # casitas del pueblo con luz
        y0 = 1450 - 50 * math.sin(x0 / 260)
        d.rect((x0, y0 - 20, x0 + 34, y0 + 6), fill=(14, 16, 32)); d.poly([(x0 - 4, y0 - 20), (x0 + 17, y0 - 36), (x0 + 38, y0 - 20)], fill=(14, 16, 32))
        d.rect((x0 + 12, y0 - 12, x0 + 20, y0 - 4), fill=(255, 200, 110))
    for x in range(0, PW, 26):   # arboleda
        h = 40 + 30 * abs(math.sin(x * .37)); y = 1550 - 30 * math.sin(x / 200 + 2)
        d.poly([(x - 18, y), (x, y - h), (x + 18, y)], fill=(12, 16, 30))
    pts = [(0, 1600)] + [(x, 1580 - 40 * math.sin(x / 200 + 2)) for x in range(0, PW + 20, 20)] + [(PW, PH), (0, PH)]
    d.poly(pts, fill=(14, 18, 32))
    # ---------------- árbol seco detallado
    def rama(x, y, a, L, w, n):
        if n == 0 or L < 8: return
        x2, y2 = x + L * math.cos(a), y - L * math.sin(a)
        d.line([(x, y), (x2, y2)], (8, 9, 18), max(1.2, w), joint="curve")
        rama(x2, y2, a + .42 + rng.uniform(-.2, .2), L * .72, w * .64, n - 1)
        rama(x2, y2, a - .38 + rng.uniform(-.2, .2), L * .68, w * .64, n - 1)
        if n > 3 and rng.random() < .5: rama(x2, y2, a + rng.uniform(-.1, .1), L * .5, w * .5, n - 2)
    rama(140, 1910, math.pi / 2 + .07, 430, 50, 9)
    d.poly([(90, 1910), (190, 1910), (165, 1700), (115, 1700)], fill=(8, 9, 18))
    # ---------------- geometría de la casa
    front, side, apex, apexR, LT, RT = A.casa_geom()
    CB, CT = A.CORNER_B, A.CORNER_T
    FW, SW = (50, 56, 76), (72, 82, 110)        # cara frontal en sombra / lateral iluminada por la luna
    d.poly(front, fill=FW); d.poly(side, fill=SW)
    # tablas: cada una con su tono, línea de luz y de sombra
    n = 30
    for k in range(n):
        v0, v1 = k / n, (k + 1) / n; t = rng.uniform(-8, 8)
        d.poly(sub_quad(front, 0, v0, 1, v1), fill=shade((FW[0] + t, FW[1] + t, FW[2] + t)))
        d.poly(sub_quad(side, 0, v0, 1, v1), fill=shade((SW[0] + t, SW[1] + t, SW[2] + t)))
        qline(d, front, 0, v1, 1, v1, (40, 46, 64), 2.4); qline(d, front, 0, v0 + .004, 1, v0 + .004, (92, 102, 128), 1)
        qline(d, side, 0, v1, 1, v1, (56, 64, 90), 2.4); qline(d, side, 0, v0 + .004, 1, v0 + .004, (126, 138, 172), 1)
    # vetas y pintura descascarillada
    for face, base in ((front, (52, 58, 78)), (side, (70, 78, 104))):
        for _ in range(170):
            u, v = rng.random(), rng.random(); L = rng.uniform(.02, .08)
            qline(d, face, u, v, min(1, u + L), v + rng.uniform(-.002, .002), base + (150,), 1)
        for _ in range(16):   # pintura levantada: manchas irregulares de madera gris
            u, v = rng.uniform(0, .9), rng.uniform(.05, .88); w, h = rng.uniform(.03, .08), rng.uniform(.015, .04)
            pts = [quad_pt(face, u + w * (.5 + .5 * math.cos(a)) * rng.uniform(.7, 1), v + h * (.5 + .5 * math.sin(a)) * rng.uniform(.7, 1)) for a in np.linspace(0, 6.28, 9)[:-1]]
            d.poly(pts, fill=(88, 86, 84) if face is side else (64, 62, 64))
    # chorretones de humedad
    for face in (front, side):
        for _ in range(9):
            u = rng.random(); v = rng.uniform(.2, .6)
            im.alpha_composite(soft(S, lambda dd: dd.line([quad_pt(face, u, v), quad_pt(face, u + .005, v + rng.uniform(.15, .35))], (20, 24, 30, 90), 10), 4))
    d = D(im)
    # banda entre plantas, esquineras y zócalo de piedra
    for face, col in ((front, (110, 118, 140)), (side, (150, 160, 190))):
        d.poly(sub_quad(face, 0, .5, 1, .525), fill=col); qline(d, face, 0, .525, 1, .525, (30, 34, 48), 2)
    d.poly([towards(CT, A.VPL, 0), towards(CT, A.VPL, .012), towards(CB, A.VPL, .012), towards(CB, A.VPL, 0)], fill=(120, 128, 150))
    d.poly([CT, towards(CT, A.VPR, .01), towards(CB, A.VPR, .01), CB], fill=(176, 188, 220))
    for face in (front, side):
        z = sub_quad(face, 0, .93, 1, 1.0); d.poly(z, fill=(64, 62, 70))
        for r in range(3):
            for kk in range(14):
                u0 = (kk + (r % 2) * .5) / 14; vv = .93 + r * .0233
                d.poly(sub_quad(face, u0 + .004, vv + .002, min(1, u0 + 1 / 14 - .004), vv + .021), fill=(88 + rng.randrange(-10, 12), 86 + rng.randrange(-10, 10), 92 + rng.randrange(-8, 8)), outline=(40, 38, 44), width=1)
    # sombra bajo el alero
    for face in (front, side):
        q = sub_quad(face, 0, 0, 1, .08)
        im.alpha_composite(soft(S, lambda dd: dd.poly(q, fill=(0, 0, 0, 120)), 10))
    d = D(im)
    # hiedra subiendo por la cara lateral
    for vine in range(3):
        u = .05 + vine * .35; v = 1.0
        for st in range(40):
            u += rng.uniform(-.02, .02); v -= rng.uniform(.012, .02)
            if v < .35: break
            x, y = quad_pt(side, max(0, min(1, u)), v)
            for _ in range(3):
                lx, ly = x + rng.uniform(-14, 14), y + rng.uniform(-10, 10); r = rng.uniform(5, 9)
                d.ell((lx - r, ly - r * .7, lx + r, ly + r * .7), fill=(30 + rng.randrange(20), 60 + rng.randrange(30), 40))
    # ---------------- tejado
    eL, eC, eR = (LT[0] - 60, LT[1] + 36), (CT[0] + 34, CT[1] + 26), (RT[0] + 34, RT[1] + 24)
    ap2 = (apex[0], apex[1] - 16)
    d.poly([ap2, apexR, eR, eC], fill=(40, 36, 48))
    rows = 16
    for r in range(rows):   # tejas en hileras escalonadas
        u0, u1 = r / rows, (r + 1) / rows
        a0, b0 = (lerp(ap2[0], eC[0], u0), lerp(ap2[1], eC[1], u0)), (lerp(apexR[0], eR[0], u0), lerp(apexR[1], eR[1], u0))
        a1, b1 = (lerp(ap2[0], eC[0], u1), lerp(ap2[1], eC[1], u1)), (lerp(apexR[0], eR[0], u1), lerp(apexR[1], eR[1], u1))
        cols = 22
        for c in range(cols):
            s0 = (c + (r % 2) * .5) / cols; s1 = min(1, s0 + 1 / cols)
            if s0 >= 1: continue
            p = [(lerp(a0[0], b0[0], s0), lerp(a0[1], b0[1], s0)), (lerp(a0[0], b0[0], s1), lerp(a0[1], b0[1], s1)), (lerp(a1[0], b1[0], s1), lerp(a1[1], b1[1], s1)), (lerp(a1[0], b1[0], s0), lerp(a1[1], b1[1], s0))]
            if rng.random() < .04: d.poly(p, fill=(16, 14, 20)); continue   # teja que falta
            t = rng.randrange(-8, 10); d.poly(p, fill=(48 + t, 42 + t, 56 + t), outline=(26, 22, 32), width=1.2)
            d.line([p[2], p[3]], (70 + t, 64 + t, 82 + t), 1.2)
    d.poly([ap2, (apex[0] + 8, apex[1] - 26), towards((apex[0] + 8, apex[1] - 26), A.VPR, .13), apexR], fill=(60, 56, 70))   # cumbrera
    # frontón con tablas verticales y alero frontal
    g = [(apex[0], apex[1] + 26), (LT[0] + 12, LT[1] + 4), (CT[0] - 6, CT[1] + 4)]
    d.poly(g, fill=(64, 72, 96))
    for k in range(1, 18):
        x = lerp(LT[0] + 12, CT[0] - 6, k / 18); yb = lerp(LT[1] + 4, CT[1] + 4, k / 18)
        yt = apex[1] + 26 + abs(x - apex[0]) / abs(apex[0] - LT[0]) * (LT[1] - apex[1] - 22)
        d.line([(x, yt), (x, yb)], (48, 54, 74), 2)
    for s in (1, -1):   # tablas del alero (bargeboards) con festón
        p0 = (apex[0], apex[1] - 10); p1 = eL if s == 1 else eC
        d.line([p0, p1], (34, 30, 40), 26); d.line([(p0[0], p0[1] + 12), (p1[0], p1[1] + 12)], (120, 112, 104), 4)
        for k in range(1, 12):
            x, y = lerp(p0[0], p1[0], k / 12), lerp(p0[1], p1[1], k / 12) + 14
            d.arc((x - 12, y - 8, x + 12, y + 12), 0, 180, (34, 30, 40), 4)
    # ventana redonda del desván
    ax, ay = apex[0], apex[1] + 210
    d.ell((ax - 66, ay - 66, ax + 66, ay + 66), fill=(130, 124, 116)); d.ell((ax - 56, ay - 56, ax + 56, ay + 56), fill=(40, 38, 46))
    d.ell((ax - 50, ay - 50, ax + 50, ay + 50), fill=(12, 12, 22))
    d.line([(ax - 50, ay), (ax + 50, ay)], (40, 38, 46), 7); d.line([(ax, ay - 50), (ax, ay + 50)], (40, 38, 46), 7)
    d.line([(ax + 10, ay - 46), (ax + 36, ay - 10)], (90, 100, 150, 150), 4)
    # chimenea de ladrillo
    c0, c1 = towards(apex, A.VPR, .055), towards(apex, A.VPR, .088)
    top = apex[1] - 150
    ch = [(c0[0], top), (c1[0], top - 6), (c1[0], c1[1] + 30), (c0[0], c0[1] + 30)]
    d.poly(ch, fill=(92, 52, 46))
    for r in range(14):
        y = top + r * 14
        for kk in range(4):
            x0 = lerp(c0[0], c1[0], (kk + (r % 2) * .5) / 4); x1 = lerp(c0[0], c1[0], min(1, (kk + 1 + (r % 2) * .5) / 4))
            d.rect((x0 + 1, y + 1, x1 - 1, y + 12), fill=(110 + rng.randrange(-14, 14), 60 + rng.randrange(-8, 8), 50))
    d.rect((c0[0] - 8, top - 18, c1[0] + 8, top), fill=(70, 66, 70)); d.poly([(c1[0] - 6, top - 18), (c1[0] + 8, top - 18), (c1[0] + 8, top + 20)], fill=(20, 18, 24))   # ladrillos caídos
    # canalón roto colgando de la esquina
    d.line([eC, towards(eC, A.VPR, .1)], (60, 64, 72), 9)
    d.line([eC, (eC[0] + 14, eC[1] + 140), (eC[0] + 40, eC[1] + 380)], (60, 64, 72), 9)
    # ---------------- ventanas
    def ventana(face, u0, v0, u1, v1, tipo, lit=False):
        q = sub_quad(face, u0, v0, u1, v1)
        d.poly(sub_quad(face, u0 - .025, v0 - .018, u1 + .025, v1 + .012), fill=(150, 146, 138))           # marco
        d.poly(sub_quad(face, u0 - .04, v1 + .006, u1 + .04, v1 + .03), fill=(170, 166, 156))              # alféizar
        d.poly(sub_quad(face, u0 - .04, v1 + .026, u1 + .04, v1 + .034), fill=(40, 40, 48))
        d.poly(q, fill=(8, 10, 20))
        refl = [quad_pt(q, .55, 0), quad_pt(q, .8, 0), quad_pt(q, .35, 1), quad_pt(q, .1, 1)]
        d.poly(refl, fill=(60, 72, 120, 120))
        if tipo == "cortina":
            d.poly([quad_pt(q, 0, 0), quad_pt(q, .3, 0), quad_pt(q, .22, .7), quad_pt(q, .1, 1), quad_pt(q, 0, 1)], fill=(130, 110, 120))
            d.poly([quad_pt(q, .7, 0), quad_pt(q, 1, 0), quad_pt(q, 1, .55), quad_pt(q, .86, .4)], fill=(118, 98, 108))
        if tipo == "rota":
            cx, cy = quad_pt(q, .6, .4)
            d.poly([quad_pt(q, .25, .05), (cx, cy), quad_pt(q, .95, .25), quad_pt(q, .9, .85), quad_pt(q, .3, .9)], fill=(2, 2, 6))
            for a in range(0, 360, 50):
                d.line([(cx, cy), (cx + 60 * math.cos(math.radians(a)), cy + 60 * math.sin(math.radians(a)))], (150, 160, 200, 150), 1.4)
        for u in (.5,): qline(d, q, u, 0, u, 1, (150, 146, 138), 6)
        for v in (.5,): qline(d, q, 0, v, 1, v, (150, 146, 138), 6)
        if tipo == "tablas":
            for a, b, ofs in ((.12, .3, .08), (.45, .62, -.06), (.74, .9, .05)):
                p = [quad_pt(q, -.1, a + ofs), quad_pt(q, 1.1, a - ofs), quad_pt(q, 1.1, b - ofs), quad_pt(q, -.1, b + ofs)]
                d.poly(p, fill=(102 + rng.randrange(-10, 10), 76, 54), outline=(46, 32, 22), width=2)
                for uu in (-.04, 1.04):
                    x, y = quad_pt(p, 0 if uu < 0 else 1, .5); d.ell((x - 4, y - 4, x + 4, y + 4), fill=(30, 30, 34))
        # contraventanas
        for sgn, u in ((-1, u0), (1, u1)):
            w = (u1 - u0) * .36
            if tipo == "rota" and sgn == 1:   # una contraventana descolgada
                p = sub_quad(face, u + .03, v0 + .1, u + .03 + w, v1 + .08)
                p = [p[0], (p[1][0] + 10, p[1][1] + 40), (p[2][0] - 20, p[2][1] + 60), p[3]]
            else:
                if (sgn < 0 and u - w - .03 < .02) or (sgn > 0 and u + .03 + w > .98): continue   # no cabe en la pared
                p = sub_quad(face, u - w - .03, v0, u - .03, v1) if sgn < 0 else sub_quad(face, u + .03, v0, u + .03 + w, v1)
            d.poly(p, fill=(42, 64, 58), outline=(20, 30, 28), width=2)
            for k in range(1, 9): qline(d, p, .1, k / 9, .9, k / 9 + .02, (28, 44, 40), 2)
    ventana(front, .12, .17, .32, .41, "tablas")
    ventana(front, .6, .17, .78, .41, "rota")
    ventana(side, .3, .16, .7, .4, "cortina")
    ventana(side, .3, .58, .7, .8, "tablas")
    # ---------------- porche cubierto
    pl, pr = quad_pt(front, .02, .66), quad_pt(front, .98, .66)
    floorL, floorR = quad_pt(front, -.05, 1.0), quad_pt(front, 1.04, 1.0)
    roofp = [(pl[0] - 70, pl[1] - 6), (pr[0] + 40, pr[1] - 10), (pr[0] + 70, pr[1] + 60), (pl[0] - 100, pl[1] + 70)]
    d.poly(roofp, fill=(40, 36, 46)); d.line([roofp[3], roofp[2]], (90, 86, 96), 6)
    for k in range(1, 12): d.line([(lerp(roofp[0][0], roofp[1][0], k / 12), lerp(roofp[0][1], roofp[1][1], k / 12)), (lerp(roofp[3][0], roofp[2][0], k / 12), lerp(roofp[3][1], roofp[2][1], k / 12))], (28, 24, 34), 2)
    im.alpha_composite(soft(S, lambda dd: dd.poly([roofp[3], roofp[2], quad_pt(front, 1, .78), quad_pt(front, 0, .78)], fill=(0, 0, 0, 140)), 14))
    d = D(im)
    door = sub_quad(front, .39, .7, .61, 1.0)
    d.poly(sub_quad(front, .36, .68, .64, 1.0), fill=(150, 146, 138))
    d.poly(door, fill=(70, 42, 30))
    for x in range(1, 7): qline(d, door, x / 7, 0, x / 7, 1, (58, 34, 24), 1.4)
    for a, b in ((.06, .42), (.52, .92)):
        for c, e in ((.12, .46), (.54, .88)):
            pp = sub_quad(door, c, a, e, b); d.poly(pp, outline=(40, 24, 16), width=4); d.poly(sub_quad(pp, .1, .06, .9, .94), outline=(96, 64, 46), width=1.6)
    kx, ky = quad_pt(door, .84, .55); d.ell((kx - 8, ky - 8, kx + 8, ky + 8), fill=(190, 160, 80))
    nx, ny = quad_pt(door, .5, .03); d.rect((nx - 18, ny - 4, nx + 18, ny + 22), fill=(170, 140, 80)); d.text((nx, ny + 9), "13", 20, (50, 34, 20))
    # columnas y barandilla
    for u in (.04, .33, .67, .96):
        top = quad_pt(front, u, .675); bot = quad_pt(front, u, 1.0)
        d.poly([(top[0] - 13, top[1] + 30), (top[0] + 13, top[1] + 30), (bot[0] + 15, bot[1]), (bot[0] - 15, bot[1])], fill=(176, 172, 164))
        d.line([(top[0] + 6, top[1] + 30), (bot[0] + 8, bot[1])], (120, 116, 110), 4)
        d.rect((top[0] - 20, top[1] + 22, top[0] + 20, top[1] + 34), fill=(190, 186, 176)); d.rect((bot[0] - 22, bot[1] - 14, bot[0] + 22, bot[1]), fill=(150, 146, 138))
    for seg in ((.04, .33), (.67, .96)):
        a0, a1 = quad_pt(front, seg[0], .86), quad_pt(front, seg[1], .86); b0, b1 = quad_pt(front, seg[0], .99), quad_pt(front, seg[1], .99)
        d.line([a0, a1], (176, 172, 164), 8)
        for k in range(1, 9):
            if (k + int(seg[0] * 10)) % 4 == 0: continue   # balaustres que faltan
            t = k / 9; d.line([(lerp(a0[0], a1[0], t), lerp(a0[1], a1[1], t)), (lerp(b0[0], b1[0], t), lerp(b0[1], b1[1], t))], (160, 156, 148), 5)
    for k in range(4):   # escalones
        y = floorL[1] + 8 + k * 30; xl = quad_pt(front, .3, 1)[0] - k * 26; xr = quad_pt(front, .7, 1)[0] + k * 26
        d.poly([(xl, y), (xr, y - 6), (xr, y + 30), (xl, y + 36)], fill=(84, 80, 88), outline=(40, 38, 46), width=2)
        d.line([(xl, y), (xr, y - 6)], (130, 126, 132), 2)
    # luz de luna sobre la arista y cara lateral
    im.alpha_composite(soft(S, lambda dd: dd.poly(side, fill=(140, 160, 230, 26)), 20))
    im.alpha_composite(soft(S, lambda dd: dd.line([CT, CB], (170, 186, 230, 160), 6), 3))
    d = D(im)
    # ---------------- primer plano
    d.poly([(0, 1860), (PW, 1820), (PW, PH), (0, PH)], fill=(16, 22, 26))
    for k in range(9):   # camino de piedras hacia el porche
        t = k / 9; cx = lerp(quad_pt(front, .5, 1)[0], 620, t) ; cy = lerp(1800, 2290, t ** 1.2); w = lerp(60, 170, t); h = lerp(14, 44, t)
        d.ell((cx - w, cy - h, cx + w, cy + h), fill=(70 + rng.randrange(10), 70, 78), outline=(36, 36, 42), width=2)
    for _ in range(1400):
        x = rng.uniform(0, PW); y = rng.uniform(1790, PH); h = rng.uniform(14, 70) * (1 + (y - 1800) / 600)
        g_ = 30 + rng.randrange(30); d.line([(x, y), (x + rng.uniform(-14, 14), y - h)], (g_ - 6, g_ + 14, g_ - 2), rng.uniform(1.5, 3.5))
    for i, x in enumerate(range(-20, PW + 60, 92)):   # valla rota
        if i in (4, 9): continue
        top = 1880 + (i % 3) * 18 - (40 if i % 4 == 0 else 0); lean = (i % 5 - 2) * 8
        d.poly([(x, PH), (x + 60, PH), (x + 60 + lean, top + 24), (x + 30 + lean, top), (x + lean, top + 24)], fill=(30, 28, 34), outline=(12, 12, 16), width=2)
        d.line([(x + 20 + lean / 2, top + 40), (x + 18, PH)], (44, 42, 48), 3)
    d.poly([(-20, 2010), (PW, 1990), (PW, 2030), (-20, 2050)], fill=(34, 32, 38))
    # buzón torcido
    bx, by = 210, 1900
    d.line([(bx, by), (bx - 14, by + 300)], (44, 34, 26), 18)
    mb = Image.new("RGBA", (220 * K, 150 * K), (0, 0, 0, 0)); md = D(mb)
    md.rect((20, 30, 200, 120), fill=(70, 74, 86)); md.ell((20, 0, 200, 60), fill=(80, 84, 96)); md.rect((150, 20, 162, 70), fill=(180, 40, 40)); md.text((90, 80), "13", 34, (200, 200, 200))
    mb = mb.rotate(-9, expand=True, resample=Image.BICUBIC); im.alpha_composite(mb, (int((bx - 110) * K), int((by - 120) * K)))
    d = D(im)
    # cartel SE VENDE $1
    sx, sy = 1050, 1700
    d.line([(sx, sy), (sx + 10, sy + 420)], (40, 30, 22), 22)
    sign = Image.new("RGBA", (380 * K, 250 * K), (0, 0, 0, 0)); sd = D(sign)
    sd.rect((10, 10, 370, 240), fill=(218, 206, 172), outline=(70, 50, 30), width=8)
    sd.text((190, 76), "SE VENDE", 80, (40, 30, 26)); sd.text((190, 178), "$1", 112, (190, 30, 30))
    sign = sign.rotate(7, expand=True, resample=Image.BICUBIC); im.alpha_composite(sign, (int((sx - 190) * K), int((sy - 150) * K)))
    # niebla
    for y, a in ((1720, 70), (1840, 90), (1970, 60)):
        im.alpha_composite(soft(S, lambda dd: dd.rect((-100, y - 40, PW + 100, y + 40), fill=(150, 160, 200, a)), 40))
    im.alpha_composite(Image.new("RGBA", S, (10, 14, 40, 50)))
    out = im.resize((PW, PH), Image.LANCZOS)
    return A.add_grain(out, 5, 2)
