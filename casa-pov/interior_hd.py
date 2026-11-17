"""Interiores detallados de "La casa de 1 dólar" (pasillo, puerta, calendario, cuarto, trampilla).
Se dibujan a K aumentos y se reducen. Las geometrías (FAR, DOOR, TRAP) son las de art.py para que la cámara no cambie."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import art as A
from art import PW, PH, lerp, quad_pt, sub_quad, font, F_ANTON, F_UI
from casa_hd import D, K, soft, qline, shade

S = (PW * K, PH * K)

def finish(im, grain=6, seed=0, tint=None):
    if tint: im.alpha_composite(Image.new("RGBA", S, tint))
    out = im.resize((PW, PH), Image.LANCZOS)
    return A.add_grain(out, grain, seed)

def wood_planks(d, q, n, base, rng, vertical=False, gap=(26, 16, 12)):
    """Tablas dentro del cuadrilátero q (en perspectiva), cada una con tono, vetas, nudos y clavos."""
    for k in range(n):
        u0, u1 = k / n, (k + 1) / n
        p = sub_quad(q, u0, 0, u1, 1) if not vertical else sub_quad(q, 0, u0, 1, u1)
        t = rng.randrange(-12, 12); d.poly(p, fill=shade((base[0] + t, base[1] + t * .7, base[2] + t * .5)))
        for _ in range(7):
            a = rng.uniform(.15, .85)
            pts = [quad_pt(p, a + .05 * math.sin(v * 9 + k), v) if not vertical else quad_pt(p, v, a + .05 * math.sin(v * 9 + k)) for v in np.linspace(0, 1, 12)]
            d.line(pts, shade((base[0] - 18 + t, base[1] - 14 + t, base[2] - 10)) + (160,), 1.2)
        if rng.random() < .35:
            u, v = rng.uniform(.3, .7), rng.uniform(.1, .9); x, y = quad_pt(p, u, v) if not vertical else quad_pt(p, v, u)
            d.ell((x - 7, y - 4, x + 7, y + 4), fill=shade((base[0] - 30, base[1] - 22, base[2] - 16)))
        for v in (.08, .92):
            x, y = quad_pt(p, .5, v) if not vertical else quad_pt(p, v, .5); d.ell((x - 2.5, y - 2.5, x + 2.5, y + 2.5), fill=(30, 28, 30))
        e0, e1 = (quad_pt(p, 0, 0), quad_pt(p, 0, 1)) if not vertical else (quad_pt(p, 0, 0), quad_pt(p, 1, 0))
        d.line([e0, e1], gap, 3)

def damask(d, q, cols, rows, base, motif, rng, peel=()):
    """Papel pintado con rayas y medallones proyectados en el cuadrilátero q."""
    d.poly(q, fill=base)
    for c in range(cols):
        u = (c + .5) / cols
        qline(d, q, c / cols, 0, c / cols, 1, shade((base[0] - 8, base[1] - 8, base[2] - 6)), 2)
        for r in range(rows):
            v = (r + .5 + (c % 2) * .5) / rows
            if v > 1: continue
            x, y = quad_pt(q, u, v); x2, _ = quad_pt(q, u + .3 / cols, v); _, y2 = quad_pt(q, u, v + .3 / rows)
            rw, rh = abs(x2 - x) + 1, abs(y2 - y) + 1
            d.poly([(x, y - rh), (x + rw * .55, y), (x, y + rh), (x - rw * .55, y)], fill=motif)
            d.ell((x - rw * .2, y - rh * .2, x + rw * .2, y + rh * .2), fill=base)
    for u0, v0, u1, v1 in peel:   # tiras de papel despegadas
        p = sub_quad(q, u0, v0, u1, v1); d.poly(p, fill=(150, 140, 120))
        c = quad_pt(q, (u0 + u1) / 2, v0); d.poly([quad_pt(q, u0, v0), quad_pt(q, u1, v0), (c[0] + 18, c[1] + 40)], fill=shade((base[0] + 30, base[1] + 26, base[2] + 18)))

# ================================================================== PASILLO
def plate_pasillo_hd():
    im = Image.new("RGBA", S, (0, 0, 0, 255)); d = D(im); rng = random.Random(31)
    fx0, fy0, fx1, fy1 = A.FAR
    L = [(0, 0), (fx0, fy0), (fx0, fy1), (0, PH)]; R = [(PW, 0), (fx1, fy0), (fx1, fy1), (PW, PH)]
    C = [(0, 0), (PW, 0), (fx1, fy0), (fx0, fy0)]; F = [(0, PH), (PW, PH), (fx1, fy1), (fx0, fy1)]
    # techo con vigas y yeso agrietado
    d.poly(C, fill=(52, 50, 58))
    for k in range(1, 9):
        z = k / 9; y0 = lerp(0, fy0, z); x0 = lerp(0, fx0, z); x1 = lerp(PW, fx1, z)
        y1 = lerp(0, fy0, min(1, z + .03)); xx0 = lerp(0, fx0, min(1, z + .03)); xx1 = lerp(PW, fx1, min(1, z + .03))
        d.poly([(x0, y0), (x1, y0), (xx1, y1), (xx0, y1)], fill=(38, 30, 26))
    for _ in range(6):
        x, y = rng.uniform(200, 1100), rng.uniform(40, 500); pts = [(x, y)]
        for _ in range(6): x += rng.uniform(-40, 40); y += rng.uniform(10, 50); pts.append((x, y))
        d.line(pts, (30, 28, 34), 2)
    # paredes con papel pintado (derecha e izquierda) + zócalo de madera alto
    WL = [(0, 0), (fx0, fy0), (fx0, lerp(fy0, fy1, .6)), (0, PH * .62)]
    WR = [(PW, 0), (fx1, fy0), (fx1, lerp(fy0, fy1, .6)), (PW, PH * .62)]
    damask(d, WL, 9, 10, (78, 66, 70), (92, 78, 82), rng, peel=((.15, .05, .22, .4), (.6, .1, .64, .3)))
    damask(d, WR, 9, 10, (72, 62, 68), (86, 74, 80), rng, peel=((.35, .1, .4, .45),))
    for W_, side in ((WL, -1), (WR, 1)):   # moldura de techo
        d.poly(sub_quad(W_, 0, 0, 1, .03), fill=(120, 110, 100))
    BL = [(0, PH * .62), (fx0, lerp(fy0, fy1, .6)), (fx0, fy1), (0, PH)]
    BR = [(PW, PH * .62), (fx1, lerp(fy0, fy1, .6)), (fx1, fy1), (PW, PH)]
    for B in (BL, BR):
        d.poly(B, fill=(70, 46, 32)); d.poly(sub_quad(B, 0, 0, 1, .07), fill=(96, 66, 46))
        for k in range(7):   # paneles enmarcados
            p = sub_quad(B, k / 7 + .015, .16, (k + 1) / 7 - .015, .9); d.poly(p, fill=(62, 40, 28), outline=(40, 26, 18), width=3)
            d.poly(sub_quad(p, .1, .08, .9, .92), outline=(88, 60, 42), width=1.5)
        d.poly(sub_quad(B, 0, .93, 1, 1), fill=(40, 26, 20))
    # pared del fondo con puerta entreabierta y luz fría
    d.rect(A.FAR, fill=(66, 56, 62))
    damask(d, [(fx0, fy0), (fx1, fy0), (fx1, lerp(fy0, fy1, .6)), (fx0, lerp(fy0, fy1, .6))], 4, 5, (66, 56, 62), (78, 66, 72), rng)
    d.rect((fx0, lerp(fy0, fy1, .6), fx1, fy1), fill=(58, 38, 28))
    dx0, dy0, dx1 = fx0 + 108, fy0 + 116, fx1 - 108
    d.rect((dx0 - 10, dy0 - 12, dx1 + 10, fy1), fill=(120, 108, 96))
    d.rect((dx0, dy0, dx1, fy1), fill=(10, 10, 18))
    im.alpha_composite(soft(S, lambda dd: dd.poly([(dx0 + 60, dy0 + 10), (dx1 - 6, dy0 + 10), (dx1 - 6, fy1), (dx0 + 30, fy1)], fill=(110, 130, 200, 90)), 10))
    d = D(im)
    d.poly([(dx0 + 4, dy0 + 6), (dx0 + 58, dy0 + 18), (dx0 + 58, fy1 - 4), (dx0 + 4, fy1)], fill=(84, 60, 44))
    # puertas laterales en perspectiva
    for W_, B, sgn in ((WL, BL, -1), (WR, BR, 1)):
        u0, u1 = (.84, .93) if sgn < 0 else (.52, .7)
        top = [quad_pt(W_, u0, .22), quad_pt(W_, u1, .22)]; bot = [quad_pt(B, u0, 1), quad_pt(B, u1, 1)]
        fr = [top[0], top[1], bot[1], bot[0]]
        d.poly(fr, fill=(120, 106, 92)); inner = [lerp_pt(fr, .1, .05), lerp_pt(fr, .9, .05), lerp_pt(fr, .9, 1), lerp_pt(fr, .1, 1)]
        d.poly(inner, fill=(64, 42, 30) if sgn < 0 else (14, 12, 18))
        if sgn < 0:
            for a, b in ((.08, .45), (.55, .92)): d.poly(sub_quad(inner, .15, a, .85, b), outline=(40, 26, 18), width=3)
            x, y = quad_pt(inner, .82, .55); d.ell((x - 5, y - 5, x + 5, y + 5), fill=(180, 150, 80))
    # cuadros y aplique de pared
    pic = [(150, 640), (380, 700), (390, 1000), (150, 990)]
    d.poly(pic, fill=(110, 80, 40)); d.poly(sub_quad(pic, .06, .05, .94, .95), fill=(70, 50, 30))
    por = sub_quad(pic, .14, .12, .86, .88); d.poly(por, fill=(80, 84, 82))
    hx, hy = quad_pt(por, .5, .42); d.ell((hx - 40, hy - 56, hx + 40, hy + 34), fill=(46, 44, 48)); d.poly([quad_pt(por, .15, 1), quad_pt(por, .3, .62), quad_pt(por, .7, .62), quad_pt(por, .85, 1)], fill=(46, 44, 48))
    for ex in (-16, 16): d.ell((hx + ex - 6, hy - 18, hx + ex + 6, hy - 8), fill=(200, 200, 200))   # ojos del retrato
    d.line([quad_pt(pic, .5, -.05), quad_pt(pic, .3, 0)], (40, 36, 30), 2); d.line([quad_pt(pic, .5, -.05), quad_pt(pic, .75, .02)], (40, 36, 30), 2)
    pic2 = sub_quad(WR, .7, .3, .82, .5); d.poly(pic2, fill=(100, 72, 40)); d.poly(sub_quad(pic2, .1, .08, .9, .92), fill=(60, 74, 70))
    sx, sy = quad_pt(WL, .78, .4)   # aplique roto
    d.rect((sx - 6, sy - 20, sx + 6, sy + 20), fill=(120, 100, 60)); d.line([(sx, sy), (sx + 30, sy - 20)], (120, 100, 60), 4); d.ell((sx + 18, sy - 50, sx + 50, sy - 20), fill=(180, 170, 150, 160))
    # ventana derecha con luz de luna y cortina rota
    win = [(1080, 520), (1210, 380), (1210, 980), (1080, 1010)]
    d.poly([(1066, 500), (1224, 360), (1224, 1000), (1066, 1030)], fill=(130, 118, 104))
    d.poly(win, fill=(110, 130, 190)); d.line([quad_pt(win, .5, 0), quad_pt(win, .5, 1)], (40, 40, 56), 8); d.line([quad_pt(win, 0, .45), quad_pt(win, 1, .45)], (40, 40, 56), 8)
    d.poly([(1072, 520), (1130, 470), (1110, 820), (1090, 1000), (1072, 1004)], fill=(120, 40, 50))
    # suelo: tablas en perspectiva con huecos, alfombra rota, escombros
    d.poly(F, fill=(62, 42, 30))
    n = 16
    for k in range(n):
        xb0, xb1 = lerp(-200, PW + 200, k / n), lerp(-200, PW + 200, (k + 1) / n)
        xf0, xf1 = lerp(fx0, fx1, k / n), lerp(fx0, fx1, (k + 1) / n)
        t = rng.randrange(-10, 10); d.poly([(xb0, PH), (xb1, PH), (xf1, fy1), (xf0, fy1)], fill=(64 + t, 44 + t, 30 + t))
        d.line([(xb0, PH), (xf0, fy1)], (30, 20, 14), 3)
        for j in range(4):
            v = rng.uniform(.1, .95); yy = lerp(fy1, PH, v ** 2); a = lerp(xf0, xb0, v ** 2); b = lerp(xf1, xb1, v ** 2)
            d.line([(a, yy), (b, yy)], (36, 24, 16), 2)
    rug = [(lerp(fx0, fx1, .32), fy1 + 4), (lerp(fx0, fx1, .68), fy1 + 4), (820, 2304), (470, 2304)]
    d.poly(rug, fill=(96, 34, 36))
    d.poly(sub_quad(rug, .06, 0, .94, 1), fill=(120, 46, 46)); d.poly(sub_quad(rug, .12, 0, .88, 1), outline=(170, 130, 70), width=3)
    for v in np.linspace(.05, .95, 8):
        x, y = quad_pt(rug, .5, v); w_ = abs(quad_pt(rug, .88, v)[0] - x) * .5
        d.poly([(x, y - 10 - 30 * v), (x + w_, y), (x, y + 10 + 30 * v), (x - w_, y)], outline=(170, 130, 70), width=2)
    d.poly([quad_pt(rug, .7, .7), quad_pt(rug, 1, .62), quad_pt(rug, 1, .9), quad_pt(rug, .8, .86)], fill=(62, 42, 30))   # trozo arrancado
    for _ in range(40):   # escombros y yeso caído
        x, y = rng.uniform(100, 1200), rng.uniform(1500, 2280); r = rng.uniform(3, 10)
        d.poly([(x - r, y), (x, y - r * .6), (x + r, y), (x, y + r * .4)], fill=(150 + rng.randrange(30), 140, 130))
    # muebles con sábanas detallados
    def sabana(pts, base, seed, bulk=.5):
        rr = random.Random(seed); lay = Image.new("RGBA", S, (0, 0, 0, 0)); sd = D(lay)
        sd.poly(pts, fill=base)
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        for _ in range(9):   # pliegues con luz y sombra
            x = rr.uniform(min(xs) + 10, max(xs) - 10); y0 = min(ys) + rr.uniform(20, 120)
            sl = rr.uniform(-.12, .12); ph = rr.uniform(0, 6); pts2 = [(x + (yy - y0) * sl + 6 * math.sin(ph + (yy - y0) / 90), yy) for yy in np.linspace(y0, max(ys), 16)]
            sd.line(pts2, shade(tuple(c * .72 for c in base)), rr.uniform(4, 12)); sd.line([(p[0] + 7, p[1]) for p in pts2], shade(tuple(c * 1.12 for c in base)), 2)
        msk = Image.new("L", S, 0); D(msk).poly(pts, fill=255)
        shp = Image.new("RGBA", S, (0, 0, 0, 0)); D(shp).poly(pts, fill=(0, 0, 0, 255))
        lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.split()[3]), np.asarray(msk))))
        grad_ = soft(S, lambda dd: dd.poly([(min(xs), max(ys) - (max(ys) - min(ys)) * .4), (max(xs), max(ys) - (max(ys) - min(ys)) * .4), (max(xs), max(ys)), (min(xs), max(ys))], fill=(0, 0, 0, 110)), 20)
        g2 = Image.new("RGBA", S, (0, 0, 0, 0)); g2.paste(grad_, (0, 0), msk)
        im.alpha_composite(soft(S, lambda dd: dd.ell((min(xs) - 20, max(ys) - 30, max(xs) + 40, max(ys) + 40), fill=(0, 0, 0, 170)), 14))
        im.alpha_composite(lay); im.alpha_composite(g2)
        dd = D(im); dd.line(pts + [pts[0]], shade(tuple(c * .6 for c in base)), 2)
        # patas asomando
        for fx in (min(xs) + 30, max(xs) - 40):
            dd.poly([(fx, max(ys) - 4), (fx + 16, max(ys) - 4), (fx + 12, max(ys) + 30), (fx + 4, max(ys) + 30)], fill=(60, 38, 24))
    sabana([(20, 1500), (60, 1400), (130, 1330), (300, 1320), (400, 1370), (440, 1470), (430, 1560), (480, 1960), (0, 1990)], (184, 186, 198), 1)
    sabana([(860, 1100), (900, 1070), (1010, 1050), (1050, 1080), (1060, 1560), (850, 1600)], (164, 168, 184), 2)
    sabana([(560, 1240), (590, 1205), (650, 1196), (720, 1196), (760, 1236), (770, 1320), (550, 1324)], (136, 138, 156), 3)
    d = D(im)
    # rayo de luna sobre el suelo
    im.alpha_composite(soft(S, lambda dd: dd.poly([(1080, 520), (1210, 380), (760, 2200), (240, 2000)], fill=(150, 170, 255, 44)), 30))
    im.alpha_composite(soft(S, lambda dd: [dd.line([(lerp(240, 760, t), lerp(2000, 2200, t)), (lerp(1080, 1210, t), lerp(1010, 700, t))], (20, 20, 40, 60), 10) for t in (.5,)], 6))
    # telarañas detalladas en las esquinas del techo
    d = D(im)
    for cx, cy, sx_, sy_ in ((0, 0, 1, 1), (PW, 0, -1, 1), (fx0, fy0, -1, -1)):
        R_ = 320 if cx in (0, PW) else 70
        for a in range(0, 91, 12):
            r = math.radians(a); d.line([(cx, cy), (cx + sx_ * R_ * math.cos(r), cy + sy_ * R_ * math.sin(r))], (220, 220, 230, 80), 1.2)
        for rr in np.linspace(R_ * .2, R_ * .95, 6):
            pts = [(cx + sx_ * rr * math.cos(math.radians(a)) * (1 - .06 * (a % 24 == 12)), cy + sy_ * rr * math.sin(math.radians(a)) * (1 - .06 * (a % 24 == 12))) for a in range(0, 91, 12)]
            d.line(pts, (220, 220, 230, 70), 1.2)
    # bombilla desnuda colgando
    d.line([(648, 0), (648, 360)], (30, 30, 34), 3); d.rect((636, 356, 660, 380), fill=(60, 56, 50)); d.ell((628, 376, 668, 430), fill=(180, 176, 160))
    # polvo en suspensión estático y oscurecido general
    for _ in range(160):
        x, y, r = rng.uniform(0, PW), rng.uniform(0, PH), rng.uniform(1, 3); d.ell((x - r, y - r, x + r, y + r), fill=(230, 220, 200, rng.randrange(30, 110)))
    return finish(im, 7, 3, (6, 8, 24, 40))

def lerp_pt(q, u, v): return quad_pt(q, u, v)

# ================================================================== PORCHE / PUERTA
def plate_porche_hd():
    im = Image.new("RGBA", S, (52, 58, 80, 255)); d = D(im); rng = random.Random(41)
    x0, y0, x1, y1 = A.DOOR
    # tablas de la fachada con detalle
    for k in range(40):
        y = k * 50; t = rng.randrange(-8, 8)
        d.rect((0, y, PW, y + 48), fill=(52 + t, 58 + t, 80 + t)); d.line([(0, y + 48), (PW, y + 48)], (32, 36, 52), 3); d.line([(0, y + 2), (PW, y + 2)], (74, 80, 104), 1)
    for _ in range(300):
        x, y = rng.uniform(0, PW), rng.uniform(0, PH); d.line([(x, y), (x + rng.uniform(30, 120), y)], (40, 44, 62, 140), 1)
    for _ in range(14):
        x, y = rng.uniform(0, PW), rng.uniform(0, 1900); w, h = rng.uniform(30, 90), rng.uniform(14, 40)
        d.poly([(x + w * (.5 + .5 * math.cos(a)) * rng.uniform(.7, 1), y + h * (.5 + .5 * math.sin(a)) * rng.uniform(.7, 1)) for a in np.linspace(0, 6.28, 9)[:-1]], fill=(70, 68, 70))
    # marco de la puerta con molduras y frontón
    d.rect((x0 - 90, y0 - 110, x1 + 90, y1 + 20), fill=(150, 144, 132)); d.rect((x0 - 70, y0 - 90, x1 + 70, y1 + 20), fill=(126, 120, 110))
    d.poly([(x0 - 110, y0 - 110), (x1 + 110, y0 - 110), ((x0 + x1) / 2, y0 - 240)], fill=(150, 144, 132)); d.poly([(x0 - 80, y0 - 120), (x1 + 80, y0 - 120), ((x0 + x1) / 2, y0 - 220)], fill=(110, 104, 96))
    d.rect((x0 - 40, y0 - 50, x1 + 40, y1 + 10), fill=(22, 18, 18))
    for xx in (x0 - 60, x1 + 60):
        for yy in range(int(y0), int(y1), 30): d.line([(xx - 10, yy), (xx + 10, yy)], (110, 104, 96), 2)
    # ventana lateral tapiada
    wx0, wy0 = 80, 760
    d.rect((wx0 - 20, wy0 - 20, wx0 + 230, wy0 + 520), fill=(150, 144, 132)); d.rect((wx0, wy0, wx0 + 210, wy0 + 500), fill=(10, 10, 18))
    for a, b in ((60, 150), (230, 320), (380, 460)):
        d.poly([(wx0 - 30, wy0 + a), (wx0 + 240, wy0 + a - 30), (wx0 + 240, wy0 + b - 30), (wx0 - 30, wy0 + b)], fill=(100, 76, 54), outline=(46, 32, 22), width=2)
    # lámpara rota
    lx = x1 + 160
    d.rect((lx - 26, 880, lx + 26, 1010), fill=(26, 24, 28)); d.poly([(lx - 40, 880), (lx + 40, 880), (lx + 26, 840), (lx - 26, 840)], fill=(40, 38, 44))
    d.line([(lx - 20, 900), (lx + 10, 990)], (120, 130, 150), 2); d.line([(lx + 18, 900), (lx - 4, 960)], (120, 130, 150), 2)
    # suelo del porche en perspectiva
    d.poly([(0, 1950), (PW, 1950), (PW, PH), (0, PH)], fill=(52, 40, 34))
    for k in range(-10, 11):
        d.line([(PW / 2 + k * 160, PH), (PW / 2 + k * 70, 1950)], (30, 22, 18), 4)
    for v in (.15, .4, .7): y = lerp(1950, PH, v ** 1.4); d.line([(0, y), (PW, y)], (36, 26, 20), 2)
    # felpudo gastado
    mat = [(470, 1985), (830, 1985), (900, 2160), (400, 2160)]
    d.poly(mat, fill=(120, 96, 60)); d.poly(sub_quad(mat, .05, .1, .95, .9), outline=(80, 60, 36), width=3)
    mx, my = quad_pt(mat, .5, .5); d.text((mx, my), "BIENVENIDOS", 46, (80, 58, 34))
    d.poly([quad_pt(mat, .7, 0), quad_pt(mat, 1, 0), quad_pt(mat, 1, .5)], fill=(52, 40, 34))
    # hojas secas
    for _ in range(26):
        x, y = rng.uniform(0, PW), rng.uniform(1960, PH); r = rng.uniform(12, 24); a = rng.uniform(0, 6.28)
        d.poly([(x + r * math.cos(a), y + r * .5 * math.sin(a)), (x + r * .4 * math.cos(a + 1.6), y + r * .4 * math.sin(a + 1.6)), (x - r * math.cos(a), y - r * .5 * math.sin(a)), (x + r * .4 * math.cos(a - 1.6), y + r * .4 * math.sin(a - 1.6))], fill=(110 + rng.randrange(40), 70 + rng.randrange(30), 30))
    im.alpha_composite(soft(S, lambda dd: dd.ell((-200, 200, 900, 1600), fill=(140, 160, 230, 40)), 120))
    return finish(im, 6, 4, (6, 8, 24, 30))

def door_leaf_hd(w, h):
    im = Image.new("RGBA", (w * K, h * K), (78, 50, 36, 255)); dd = ImageDraw.Draw(im); rng = random.Random(5)
    def R(b, **kw): dd.rectangle([v * K for v in b], **kw)
    for x in range(0, w, 14):
        dd.line([(x * K, 0), ((x + rng.uniform(-3, 3)) * K, h * K)], fill=(64 + rng.randrange(12), 40, 28), width=int(2 * K))
    for a, b in ((.05, .44), (.53, .95)):
        for c, e in ((.1, .46), (.54, .9)):
            R((w * c, h * a, w * e, h * b), fill=(70, 44, 32), outline=(40, 24, 16), width=int(9 * K))
            R((w * c + 16, h * a + 16, w * e - 16, h * b - 16), outline=(104, 72, 52), width=int(3 * K))
            R((w * c + 9, h * a + 9, w * e - 9, h * a + 13), fill=(30, 18, 12))
    for _ in range(20):   # arañazos
        x, y = rng.uniform(20, w - 20), rng.uniform(40, h - 40); dd.line([(x * K, y * K), ((x + rng.uniform(-30, 30)) * K, (y + rng.uniform(10, 50)) * K)], fill=(110, 80, 60), width=K)
    cx, cy = w * .84, h * .52
    R((cx - 22, cy - 60, cx + 22, cy + 90), fill=(150, 120, 60), outline=(80, 60, 24), width=K * 2)
    dd.ellipse([(cx - 24) * K, (cy - 24) * K, (cx + 24) * K, (cy + 24) * K], fill=(186, 156, 76), outline=(90, 70, 30), width=4 * K)
    dd.ellipse([(cx - 7) * K, (cy + 40) * K, (cx + 7) * K, (cy + 54) * K], fill=(30, 20, 10)); dd.rectangle([(cx - 3) * K, (cy + 50) * K, (cx + 3) * K, (cy + 72) * K], fill=(30, 20, 10))
    R((w * .38, h * .012, w * .62, h * .05), fill=(170, 140, 76), outline=(90, 70, 30), width=2 * K)
    dd.text((w * .5 * K, h * .031 * K), "13", font=font(F_ANTON, 44 * K), fill=(50, 34, 20), anchor="mm")
    # aldaba
    dd.ellipse([(w * .5 - 30) * K, (h * .26 - 30) * K, (w * .5 + 30) * K, (h * .26 + 30) * K], outline=(150, 120, 60), width=8 * K)
    out = im.resize((w, h), Image.LANCZOS)
    return A.add_grain(out, 7, 5)

# ================================================================== PARED DEL CALENDARIO
def plate_calendario_hd():
    im = Image.new("RGBA", S, (0, 0, 0, 255)); d = D(im); rng = random.Random(51)
    wall = [(0, 0), (PW, 0), (PW, PH), (0, PH)]
    damask(d, wall, 7, 14, (84, 72, 64), (98, 84, 74), rng, peel=((.0, .0, .08, .3), (.82, .55, .9, .9)))
    for _ in range(5):   # manchas de humedad
        x, y, r = rng.uniform(0, PW), rng.uniform(0, PH), rng.uniform(120, 300)
        im.alpha_composite(soft(S, lambda dd: dd.ell((x - r, y - r * .8, x + r, y + r * .8), fill=(40, 32, 26, 120)), 50))
    d = D(im)
    # interruptor antiguo y marcas de cuadros que ya no están
    d.rect((1110, 1100, 1190, 1230), fill=(190, 180, 160), outline=(110, 100, 90), width=3); d.rect((1140, 1140, 1160, 1190), fill=(120, 100, 80))
    d.rect((80, 1950, 360, 2240), outline=(110, 96, 84), width=6)
    base = A._plate_calendario_simple()   # el calendario en sí (ya detallado) se copia encima
    cal = base.crop((200, 440, 1100, 1920)).resize((900 * K, 1480 * K), Image.LANCZOS)
    m = Image.new("L", cal.size, 0); ImageDraw.Draw(m).rectangle((30 * K, 80 * K, 866 * K, 1440 * K), fill=255)
    for a in range(0, 91, 18):   # telaraña de la esquina
        pass
    im.alpha_composite(soft(S, lambda dd: dd.rect((254, 554, 1090, 1914), fill=(0, 0, 0, 170)), 24))
    im.paste(cal, (200 * K, 440 * K), m)
    d = D(im)
    # esquinas dobladas y chinchetas
    d.poly([(1066, 1880), (1066, 1810), (996, 1880)], fill=(200, 188, 160)); d.poly([(1066, 1810), (996, 1880), (1066, 1880)], outline=(150, 140, 120), width=2)
    d.ell((640, 470, 660, 490), fill=(70, 70, 76)); d.line([(650, 480), (290, 520)], (40, 36, 34), 2.4); d.line([(650, 480), (1006, 520)], (40, 36, 34), 2.4)
    return finish(im, 8, 6, (40, 26, 6, 26))

# ================================================================== CUARTO DEL RELOJ
def plate_reloj_hd():
    im = Image.new("RGBA", S, (0, 0, 0, 255)); d = D(im); rng = random.Random(61)
    damask(d, [(0, 0), (PW, 0), (PW, 1300), (0, 1300)], 8, 10, (40, 40, 58), (48, 48, 68), rng)
    # ventana con cortinas y luna
    d.rect((740, 120, 1220, 920), fill=(120, 110, 100)); d.rect((760, 140, 1200, 900), fill=(26, 36, 78))
    for _ in range(40): x, y = rng.uniform(770, 1190), rng.uniform(150, 880); d.ell((x - 1.5, y - 1.5, x + 1.5, y + 1.5), fill=(220, 225, 255))
    d.ell((960, 260, 1100, 400), fill=(234, 234, 222))
    d.line([(980, 140), (980, 900)], (100, 92, 84), 14); d.line([(760, 520), (1200, 520)], (100, 92, 84), 14)
    d.poly([(700, 90), (820, 90), (800, 600), (760, 980), (700, 980)], fill=(90, 40, 50)); d.poly([(1160, 90), (1270, 90), (1270, 980), (1210, 980), (1190, 500)], fill=(80, 36, 46))
    for x in (720, 750, 780): d.line([(x, 90), (x - 10, 980)], (70, 28, 38), 3)
    d.rect((680, 70, 1290, 96), fill=(110, 90, 60))
    im.alpha_composite(soft(S, lambda dd: dd.poly([(760, 900), (1200, 900), (1100, 1540), (300, 1540)], fill=(140, 160, 230, 46)), 30))
    d = D(im)
    # mesita de noche con madera
    top = [(60, 1290), (1240, 1290), (1296, 1560), (0, 1560)]
    wood_planks(d, top, 6, (86, 56, 38), rng)
    d.rect((0, 1560, PW, 1600), fill=(70, 46, 30))
    front = [(20, 1600), (1276, 1600), (1276, 2304), (20, 2304)]
    wood_planks(d, front, 5, (66, 42, 28), rng, vertical=True)
    d.rect((120, 1700, 1170, 2000), fill=(72, 46, 30), outline=(36, 22, 16), width=8); d.rect((140, 1720, 1150, 1980), outline=(96, 64, 44), width=2)
    d.rect((560, 1820, 740, 1860), fill=(160, 130, 70), outline=(90, 70, 30), width=3)
    # objetos: vaso de agua, libro, gafas
    d.rect((1060, 1180, 1200, 1300), fill=(150, 170, 190, 120), outline=(200, 210, 220), width=3); d.rect((1062, 1230, 1198, 1298), fill=(110, 140, 170, 120))
    d.poly([(60, 1360), (300, 1330), (330, 1400), (80, 1440)], fill=(110, 30, 30)); d.poly([(80, 1440), (330, 1400), (330, 1416), (80, 1456)], fill=(220, 210, 190))
    d.ell((120, 1300, 190, 1340), outline=(170, 170, 180), width=3); d.ell((200, 1296, 270, 1336), outline=(170, 170, 180), width=3); d.line([(190, 1318), (200, 1316)], (170, 170, 180), 3)
    # despertador retro (radio-reloj) con rejilla
    im.alpha_composite(soft(S, lambda dd: dd.ell((240, 1350, 1040, 1520), fill=(0, 0, 0, 200)), 20))
    d = D(im)
    d.rounded = None
    ImageDraw.Draw(im).rounded_rectangle([250 * K, 880 * K, 1040 * K, 1440 * K], 70 * K, fill=(44, 40, 46), outline=(90, 86, 96), width=8 * K)
    ImageDraw.Draw(im).rounded_rectangle([262 * K, 892 * K, 1028 * K, 960 * K], 40 * K, fill=(60, 56, 64))
    ImageDraw.Draw(im).rounded_rectangle([310 * K, 960 * K, 980 * K, 1360 * K], 40 * K, fill=(8, 6, 8))
    for x in range(280, 300, 6): pass
    for k in range(5): d.rect((340 + k * 130, 1376, 400 + k * 130, 1400), fill=(70, 66, 74))   # botones
    d.text((645, 1424), "SANYO 1987", 22, (140, 136, 146))
    return finish(im, 6, 8, (6, 8, 24, 30))

# ================================================================== SUELO + TRAMPILLA
def plate_trampilla_hd():
    im = Image.new("RGBA", S, (66, 46, 32, 255)); d = D(im); rng = random.Random(71)
    VPF = A.VPF
    for k in range(-14, 15):
        xb = PW / 2 + k * 130
        q = [(lerp(xb, VPF[0], .38), 0), (lerp(xb + 130, VPF[0], .38), 0), (xb + 130, PH), (xb, PH)]
        t = rng.randrange(-12, 12); base = (76 + t, 52 + t * .7, 36 + t * .5)
        d.poly(q, fill=shade(base))
        for _ in range(8):   # vetas
            a = rng.uniform(.1, .9); pts = [quad_pt(q, a + .04 * math.sin(v * 7 + k), v) for v in np.linspace(0, 1, 14)]
            d.line(pts, shade((base[0] - 16, base[1] - 12, base[2] - 8)) + (170,), 1.3)
        for v in (rng.uniform(.1, .3), rng.uniform(.5, .7)):
            if rng.random() < .5:
                x, y = quad_pt(q, rng.uniform(.3, .7), v); d.ell((x - 9, y - 5, x + 9, y + 5), fill=shade((base[0] - 34, base[1] - 26, base[2] - 18))); d.ell((x - 4, y - 2, x + 4, y + 2), fill=shade((base[0] - 50, base[1] - 40, base[2] - 28)))
        d.line([q[3], q[0]], (28, 18, 12), 6)
        for v in (.12, .5, .88):
            for u in (.2, .8):
                x, y = quad_pt(q, u, v); d.ell((x - 3, y - 3, x + 3, y + 3), fill=(34, 30, 30))
    for y in (260, 700, 1210, 1820):
        d.line([(0, y), (PW, y)], (36, 24, 16), 4)
    # polvo acumulado (más claro) salvo donde se ha arrastrado la trampilla
    for _ in range(900):
        x, y = rng.uniform(0, PW), rng.uniform(0, PH)
        if 180 < x < 1120 and 960 < y < 1720: continue
        r = rng.uniform(1, 3); d.ell((x - r, y - r, x + r, y + r), fill=(150, 130, 110, 90))
    # trampilla con herrajes
    TRAP = A.TRAP
    im.alpha_composite(soft(S, lambda dd: dd.poly(TRAP, outline=(0, 0, 0, 230), width=44), 10))
    d = D(im)
    wood_planks(d, TRAP, 6, (64, 42, 28), rng, gap=(18, 10, 6))
    d.poly(TRAP, outline=(16, 10, 6), width=14)
    for v in (.15, .85):   # bisagras con remaches
        q = [quad_pt(TRAP, -.02, v - .05), quad_pt(TRAP, .4, v - .045), quad_pt(TRAP, .42, v + .045), quad_pt(TRAP, -.02, v + .05)]
        d.poly(q, fill=(52, 50, 56), outline=(18, 18, 22), width=3)
        d.line([quad_pt(q, 0, .3), quad_pt(q, 1, .3)], (90, 88, 96), 2)
        for u in (.06, .18, .3, .38):
            x, y = quad_pt(TRAP, u, v); d.ell((x - 7, y - 7, x + 7, y + 7), fill=(86, 82, 88)); d.ell((x - 3, y - 4, x + 1, y), fill=(140, 136, 144))
        for _ in range(6):   # óxido
            x, y = quad_pt(TRAP, rng.uniform(0, .38), v + rng.uniform(-.04, .04)); r = rng.uniform(4, 10); d.ell((x - r, y - r, x + r, y + r), fill=(110, 58, 30, 160))
    # aldaba y argolla
    hx, hy = quad_pt(TRAP, .82, .5)
    d.rect((hx - 100, hy - 34, hx + 40, hy + 34), fill=(56, 54, 60), outline=(18, 18, 22), width=4)
    for x in (hx - 80, hx - 50): d.ell((x - 7, hy - 7, x + 7, hy + 7), fill=(96, 92, 100))
    d.ell((hx + 18, hy - 50, hx + 84, hy + 50), outline=(70, 68, 74), width=14)
    rx, ry = quad_pt(TRAP, .5, .3)   # argolla para tirar
    d.ell((rx - 46, ry - 26, rx + 46, ry + 26), outline=(60, 58, 64), width=10); d.rect((rx - 14, ry - 34, rx + 14, ry - 18), fill=(56, 54, 60))
    # arañazos frescos en arco: alguien la ha abierto hace poco
    for k in range(9):
        r = 380 + k * 22; cx, cy = quad_pt(TRAP, .5, 1.0)
        d.arc((cx - r, cy - r * .45, cx + r, cy + r * .45), 200 + k, 250 - k, (200, 170, 130, 200), 2.2)
    for _ in range(14):   # astillas
        x, y = rng.uniform(250, 1050), rng.uniform(980, 1080); d.line([(x, y), (x + rng.uniform(-14, 14), y - rng.uniform(4, 14))], (180, 150, 110), 2)
    # huellas en el polvo hacia la trampilla
    for i in range(6):
        x = 1080 - i * 60 + (i % 2) * 30; y = 2200 - i * 110
        d.ell((x - 22, y - 44, x + 22, y + 44), fill=(48, 32, 22, 170)); d.ell((x - 18, y + 52, x + 18, y + 74), fill=(48, 32, 22, 170))
    return finish(im, 7, 9, (6, 6, 20, 26))
