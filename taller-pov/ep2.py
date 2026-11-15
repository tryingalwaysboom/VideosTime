"""Ep.2 "Persiana abajo" (ganó la B). Reutiliza el motor de render.py con escenas, barra y final propios.
Uso: python3 ep2.py still 10 20 | python3 ep2.py scenes | python3 ep2.py mix"""
import os, sys, math
os.environ["GUION"] = "guion2"; os.environ["VOZDIR"] = "voz2"
import render as R
from render import (Image, ImageDraw, ImageFilter, W, H, bg, put, scaled, text, panel, stamp, ficha, etiqueta, dust,
                    neon_flicker, mouth, dark, ease, back, clamp, popscale, euros, S, E, WT, TL, YEL, RED, WHITE, OL,
                    CYAN, MAG, GRIS, F_UI, F_ANTON)

R.EPISODIO, R.DIA = 2, 2
G_ = (46, 160, 90)

# ---------------------------------------------------------------- barra superior Ep.2
def draw_hud(canvas, T):
    if T >= S("E18") - .1: return
    base = R.barra_base()
    if T < .25:
        k = ease(T / .25); canvas.alpha_composite(base.crop((0, 0, W, 300)), (0, int(-300 * (1 - k)))); return
    canvas.alpha_composite(base)
    d = ImageDraw.Draw(canvas); x0, y0, x1 = 36, 168, 1044
    t_caja, t_rep = WT("E10", "fuerza.") - .4, S("E11") + .3
    def pop(t): return 1 + .28 * math.sin(clamp((T - t) / .3) * math.pi) if 0 <= T - t < .3 else 1
    caja = euros(410 + int(600 * ease((T - t_caja) / .9))) if T >= t_caja else euros(410)
    rep = "1" if T >= t_rep else "0"
    for k, v, t, x in (("coch", "2", -9, x0 + 300), ("caja", caja, t_caja, x0 + 420), ("deuda", "-" + euros(64300), -9, x0 + 600),
                       ("rep", rep, t_rep, x0 + 880)):
        cy = y0 + 34
        if k == "coch": R.carito(d, x, cy, CYAN)
        if k == "caja": R.coin(d, x, cy, 15)
        if k == "deuda": R.flecha(d, x, cy, 1.0)
        if k == "rep": R.estrella(d, x, cy, 17, (242, 190, 60))
        col = (255, 120, 110) if k == "deuda" else ((120, 240, 150) if (k == "caja" and T >= t_caja) else WHITE)
        d.text((x + 24, y0 + 35), v, font=R.font(F_ANTON, 34 * pop(t)), fill=col, anchor="lm")
    d.text((x0 + 132, y0 + 87), "Arrancar el coche del tío", font=R.font(F_UI, 24), fill=WHITE, anchor="lm")
    d.text((x1 - 20, y0 + 87), "REPUTACIÓN", font=R.font(F_UI, 18), fill=GRIS, anchor="rm")

# ---------------------------------------------------------------- piezas
def chispas(c, T, t0, x, y, n=26, dur=.6, col=(255, 200, 80)):
    if not (0 <= T - t0 < dur): return
    d = ImageDraw.Draw(c); u = (T - t0) / dur
    for i in range(n):
        a = -math.pi * (.1 + .8 * ((i * 37) % 100) / 100); v = 260 + (i * 53) % 240
        px = x + math.cos(a) * v * u * (1 if i % 2 else -1); py = y + math.sin(a) * v * u + 500 * u * u
        d.line((px, py, px - 10 * math.cos(a), py - 10 * math.sin(a)), fill=col, width=4)

def persiana_en(c, T, frac, shake=0):
    """Persiana del marco de la fachada bajada 'frac' (0 = arriba, 1 = cerrada)."""
    pers = scaled("persiana", 1.0); h = int(570 * frac)
    if h > 2: c.alpha_composite(pers.crop((0, 570 - h, 780, 570)), (150 + int(shake), 830))

def grafiti(c, T, t0):
    if T < t0: return
    u = clamp((T - t0) / .7)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    txt = "DEVUÉLVELO"; f = R.font(F_ANTON, 120); full = d.textlength(txt, font=f)
    x0 = 540 - full / 2
    d.text((x0, 1115), txt, font=f, fill=(210, 20, 30, 235), anchor="lm")
    for i in range(14):   # chorretones de pintura
        x = x0 + 30 + i * full / 14; L = 30 + (i * 37) % 70
        d.line((x, 1160, x, 1160 + L * u), fill=(190, 15, 25, 220), width=7)
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rectangle((0, 0, int(x0 + full * u + 20), H), fill=255)
    lay.putalpha(Image.composite(lay.getchannel("A"), Image.new("L", (W, H), 0), m))
    c.alpha_composite(lay)

def reloj(c, T, t0, t1, cx=820, cy=520, r=110):
    """Reloj de taller que avanza 12 horas entre t0 y t1."""
    d = ImageDraw.Draw(c); p = clamp((T - t0) / (t1 - t0)); h = 8 + 12 * p
    d.ellipse((cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10), fill=OL)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(245, 242, 232))
    for k in range(12):
        a = k * math.pi / 6; d.line((cx + .82 * r * math.sin(a), cy - .82 * r * math.cos(a), cx + .95 * r * math.sin(a), cy - .95 * r * math.cos(a)), fill=OL, width=6)
    ah = (h % 12) / 12 * 2 * math.pi; am = (h % 1) * 2 * math.pi
    d.line((cx, cy, cx + .5 * r * math.sin(ah), cy - .5 * r * math.cos(ah)), fill=OL, width=12)
    d.line((cx, cy, cx + .8 * r * math.sin(am), cy - .8 * r * math.cos(am)), fill=RED, width=6)
    d.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=OL)
    hh = int(h) % 24
    text(d, (cx, cy + r + 50), f"{hh:02d}:{int((h % 1) * 60):02d}", 56, YEL, stroke=6)

def cristal_roto(c, cx, cy):
    d = ImageDraw.Draw(c)
    for k in range(9):
        a = k * 2 * math.pi / 9 + .3; L = 70 + (k * 29) % 60
        d.line((cx, cy, cx + L * math.cos(a), cy + L * math.sin(a)), fill=(235, 245, 255), width=4)
    for rr in (30, 60):
        pts = [(cx + rr * math.cos(k * 2 * math.pi / 9 + .3), cy + rr * math.sin(k * 2 * math.pi / 9 + .3)) for k in range(10)]
        d.line(pts, fill=(235, 245, 255), width=3)
    d.ellipse((cx - 14, cy - 14, cx + 14, cy + 14), fill=(10, 14, 24))

# ---------------------------------------------------------------- escenas
def sc_cierre(T):
    """E01: la persiana baja de golpe en la cara de Nitro (fachada de noche)."""
    c = bg("bg_fachada", T, 0, 1.25, 1.12, 3, .5, .62)
    inner = bg("bg_taller", T, 0, 1.4, 1.4, 1, .5, .6).crop((150, 830, 930, 1400)); c.alpha_composite(inner, (150, 830))
    put(c, "coche_negro", 300, 1500, .7)
    u = ease((T - .15) / .55)
    tb = .7
    shake = 10 * math.sin(T * 70) * math.exp(-(T - tb) * 6) if T > tb else 0
    persiana_en(c, T, u, shake)
    chispas(c, T, tb, 540, 1395)
    stamp(c, T, WT("E01", "B."), "GANÓ LA B", 540, 460, YEL, -8, 110)
    return c

def sc_nitro_fuera(T):
    """E02: Nitro grita desde fuera, al otro lado de la persiana."""
    s0 = S("E02")
    c = bg("bg_fachada", T, s0, 1.55, 1.6, 4, .5, 1.0); dark(c, 110)
    neon_flicker(c, T, (100, 300, 980, 900), MAG, 7)
    put(c, "nitro", 540, 820 + 4 * math.sin(T * 2), 1.0)
    mouth(c, 552, 844, T, S("E02") <= T < E("E02"), 24)
    put(c, "coche_negro", 540, 1180, 1.0)
    etiqueta(c, T, WT("E02", "semana"), "\"EN UNA SEMANA\"", 540, 400, RED, WHITE, 40)
    return c

def sc_se_va(T):
    """E03-E04: el coche negro se va calle abajo petardeando; Manolo respira."""
    s0, s4 = S("E03"), S("E04")
    if T < s4 - .1:
        c = bg("bg_fachada", T, s0, 1.0, 1.06, 4, .5, .62)
        inner = bg("bg_taller", T, 0, 1.4, 1.4, 1, .5, .6).crop((150, 830, 930, 1400)); dark(inner, 60); c.alpha_composite(inner, (150, 830))
        persiana_en(c, T, 1.0)
        u = ease((T - s0) / 1.8)
        x = 540 - 1300 * u
        put(c, "coche_negro", x, 1560, .85)
        tp = WT("E03", "petardea")
        for i in range(4):
            tt = tp + i * .3
            if 0 <= T - tt < .12:
                d = ImageDraw.Draw(c); ex = x + 470; d.ellipse((ex - 10, 1630, ex + 90, 1690), fill=(255, 160, 40)); d.ellipse((ex + 10, 1645, ex + 60, 1675), fill=(255, 240, 160))
        return c
    c = bg("bg_taller", T, s4, 1.0, 1.08, 6, .5, .55)
    neon_flicker(c, T, (300, 220, 800, 520), CYAN, 3)
    put(c, "manolo", 540, 1320 + 6 * math.sin(T * 2.2), 1.0)
    mouth(c, 540, 1194, T, s4 <= T < E("E04"), 28)
    dust(c, T)
    etiqueta(c, T, WT("E04", "dinero"), "HAY QUE SACAR DINERO", 540, 470, YEL, OL, 40)
    return c

def sc_cuadro(T):
    """E05: giras la llave… y nada."""
    s0 = S("E05")
    c = Image.new("RGBA", (W, H), (8, 8, 12, 255))
    put(c, "cuadro", 540, 900, 1.0 + .06 * clamp((T - s0) / 3))
    tg = WT("E05", "giras")
    d = ImageDraw.Draw(c)
    if tg <= T < tg + .6:   # las agujas intentan subir y caen
        k = math.sin(clamp((T - tg) / .6) * math.pi)
        for cx in (330, 750):
            a = math.radians(135 + 30 * k); d.line((cx, 900 - 210 + 440 - 440, cx + 150 * math.cos(a), 690 + 150 * math.sin(a)), fill=(255, 80, 60), width=8)
    tn = WT("E05", "Nada.")
    if T >= tn: text(d, (540, 1330), "NADA", 160 * popscale(T, tn, .3), RED, stroke=10)
    return c

def sc_centralita(T):
    """E06: falta la centralita."""
    s0 = S("E06")
    c = bg("bg_taller", T, s0, 1.25, 1.18, 5, .5, .7); dark(c, 80)
    put(c, "deportivo", 540, 1250, 1.0)
    tc = WT("E06", "centralita.")
    if T >= tc:
        k = popscale(T, tc, .45)
        panel(c, (210, 380, 870, 900), fill=(14, 12, 26), alpha=int(220 * min(1, k)), rad=30, outline=CYAN, ow=5)
        put(c, "centralita", 540, 600, .85 * max(k, .02))
        d = ImageDraw.Draw(c)
        if k > .6:
            text(d, (540, 800), "PIEZA QUE FALTA", 46, WHITE, stroke=5)
            text(d, (540, 860), "PRECIO: ¿?", 40, YEL, "mm", F_UI, stroke=4)
    return c

def sc_golpes(T):
    """E07: alguien golpea la persiana desde fuera."""
    s0 = S("E07")
    c = bg("bg_taller", T, s0, 1.5, 1.5, 1, .5, .45); dark(c, 40)
    # persiana vista desde dentro (temblando con cada golpe)
    golpes = [WT("E07", "golpea") + i * .32 for i in range(3)]
    sh = sum(14 * math.exp(-(T - g) * 12) * math.sin((T - g) * 60) for g in golpes if T >= g)
    pers = scaled("persiana", 1.3)
    c.alpha_composite(pers, (int(540 - pers.width / 2 + sh), 520))
    for g in golpes:
        if 0 <= T - g < .25:
            d = ImageDraw.Draw(c); text(d, (540 + 80 * (golpes.index(g) - 1), 470), "¡TOC!", 110, YEL, stroke=8)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(ov).rectangle((0, 1250, W, 1290), fill=(255, 220, 160, 160))
    c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(12)))   # luz de la mañana por debajo
    reloj(c, T, s0, s0 + .01, 860, 360, 80)
    return c

def sc_lucia(T):
    """E08-E09: Lucía y el Seat que lleva 2 años parado."""
    s0, e9 = S("E08"), E("E09")
    c = bg("bg_fachada", T, s0, 1.15, 1.2, 6, .5, .7)
    ov = Image.new("RGBA", (W, H), (255, 210, 150, 40)); c.alpha_composite(ov)   # luz de mañana
    put(c, "icon_utilitario", 560, 1330, .95)
    lx = 330 + 500 * (1 - ease((T - s0 + .3) / .5))
    put(c, "lucia", lx, 980 + 4 * math.sin(T * 2.4), .82)
    mouth(c, lx, 980 - 150 + 4 * math.sin(T * 2.4), T, S("E08") <= T < E("E08"), 16)
    ficha(c, T, s0 - .2, 520, 330, "LUCÍA", "24 AÑOS · PILOTO DE RALLY", "DUEÑA DEL SEAT IBIZA", 500)
    t6 = WT("E08", "600")
    if T >= t6 and T < S("E09"):
        k = popscale(T, t6, .4); d = ImageDraw.Draw(c)
        d.rounded_rectangle((560, 600, 980, 730), 20, fill=G_, outline=OL, width=6)
        if k > .5: text(d, (770, 665), "600 €", 100 * min(1.1, k), WHITE, stroke=6)
    if T >= S("E09"):
        etiqueta(c, T, WT("E09", "dos"), "2 AÑOS SIN MOVERSE", 760, 720, RED, WHITE, 36)
    return c

def sc_montaje(T):
    """E10: doce horas sin parar. Montaje rápido del Seat transformándose en coche de rally."""
    s0 = S("E10"); e1 = S("E11") - .1
    c = bg("bg_taller", T, s0, 1.2, 1.1, e1 - s0, .5, .7)
    neon_flicker(c, T, (300, 220, 800, 520), CYAN, 3)
    p = clamp((T - s0) / (e1 - s0))
    # el Seat pasa de viejo a rally a mitad del montaje
    tr = s0 + (e1 - s0) * .62
    if T < tr: put(c, "icon_utilitario", 540, 1250, .95)
    else:
        put(c, "seat_rally", 540, 1250 - 10 * math.sin(clamp((T - tr) / .4) * math.pi), .95)
        if T - tr < .25: c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(200 * (1 - (T - tr) / .25)))))
    # cortes rápidos con herramientas y chispas cada ~0.7 s
    beat = int((T - s0) / .7)
    for k in range(beat + 1):
        chispas(c, T, s0 + k * .7, 300 + (k * 211) % 480, 1300 + (k % 3) * 40, 20, .5)
    put(c, "gato", 930 if beat % 2 else 150, 1160, .3)
    reloj(c, T, s0, e1, 820, 560, 105)
    d = ImageDraw.Draw(c)
    text(d, (300, 560), f"{int(12 * p):d} H", 120, WHITE, stroke=8)
    return c

def sc_lucia_feliz(T):
    """E11: Lucía con su coche de rally terminado."""
    s0 = S("E11")
    c = bg("bg_fachada", T, s0, 1.15, 1.22, 5, .5, .7)
    c.alpha_composite(Image.new("RGBA", (W, H), (255, 210, 150, 40)))
    put(c, "seat_rally", 560, 1330, .95)
    ly = 980 + 6 * abs(math.sin(T * 4)); put(c, "lucia", 300, ly, .82)
    mouth(c, 300, ly - 150, T, S("E11") <= T < E("E11"), 16)
    stamp(c, T, WT("E11", "nunca!"), "+1 REPUTACIÓN", 690, 560, YEL, -6, 80)
    for i in range(6):   # estrellitas
        tt = S("E11") + .2 + i * .15
        if T >= tt:
            d = ImageDraw.Draw(c); R.estrella(d, 640 + 60 * math.cos(i), 760 + 50 * math.sin(i * 1.7), 18 * popscale(T, tt, .3), (242, 190, 60))
    return c

def sc_fotos(T):
    """E12-E13: el gato tira la caja y caen fotos de Rubén y Nitro jóvenes."""
    s0 = S("E12"); e13 = E("E13")
    c = bg("bg_taller", T, s0, 1.3, 1.36, 6, .5, .78); dark(c, 70)
    tc = WT("E12", "caja")
    y = 520 + 520 * ease((T - tc) / .5) if T >= tc else 520
    bounce = 30 * abs(math.sin((T - tc - .5) * 9)) * math.exp(-(T - tc - .5) * 4) if T > tc + .5 else 0
    put(c, "caja", 540, y - bounce, .9, rot=-12 if T < tc + .5 else 6)
    put(c, "gato", 760, 470 if T < tc else 1330, .38)
    tf = WT("E12", "fotos")
    if T >= tf:
        for i, (fx, fy, rr) in enumerate(((260, 1050, -14), (820, 1030, 12), (540, 1180, 6))):
            if T >= tf + i * .12: put(c, "foto_r96", fx, fy, .45, rot=rr)
    tz = S("E13")
    if T >= tz:   # zoom a la foto
        z = ease((T - tz) / .6); dark(c, 160 * z)
        put(c, "foto_r96", 540, 960, .45 + .85 * z, rot=6 * (1 - z))
        d = ImageDraw.Draw(c)
        if T >= WT("E13", "Rubén…"): etiqueta(c, T, WT("E13", "Rubén…"), "TU TÍO", 330, 1460, CYAN, OL, 40)
        if T >= WT("E13", "Nitro."): etiqueta(c, T, WT("E13", "Nitro."), "NITRO", 760, 1460, RED, WHITE, 40)
    return c

def sc_socios(T):
    """E14: Manolo confiesa que eran socios."""
    s0 = S("E14")
    c = bg("bg_taller", T, s0, 1.1, 1.16, 5, .5, .55); dark(c, 90)
    put(c, "manolo", 540, 1320 + 4 * math.sin(T * 1.6), 1.0)
    mouth(c, 540, 1194, T, s0 <= T < E("E14"), 28)
    put(c, "foto_r96", 170, 540, .36, rot=-8)
    stamp(c, T, WT("E14", "socios."), "ERAN SOCIOS", 640, 520, RED, -8, 90)
    return c

def sc_llave(T):
    """E15: la llave de la Nave 7."""
    s0 = S("E15")
    c = R.bg("bg_noche", T, s0, 1.0, 1.06, 5)
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((140, 560, 940, 1260), fill=(242, 190, 60, 70))
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(60)))
    k = popscale(T, s0 + .1, .5)
    put(c, "llave_nave7", 540, 900, 1.25 * max(k, .02), rot=-8 + 6 * math.sin(T * 1.3))
    if T >= WT("E15", "Nave"): stamp(c, T, WT("E15", "Nave"), "NAVE 7", 540, 1300, YEL, 6, 110)
    return c

def sc_amanecer(T):
    """E16-E17: ventana rota, lona movida y el grafiti DEVUÉLVELO."""
    s0 = S("E16"); tl = WT("E16", "persiana,")
    if T < tl - .1:
        c = bg("bg_taller", T, s0, 1.0, 1.08, 4, .5, .5)
        c.alpha_composite(Image.new("RGBA", (W, H), (255, 220, 170, 30)))
        if T >= WT("E16", "rota."): cristal_roto(c, 330, 205); stamp(c, T, WT("E16", "rota."), "ROTA", 330, 420, RED, -10, 80)
        put(c, "deportivo", 540, 1320, .95)
        if T >= WT("E16", "lona"):
            put(c, "lona", 680, 1220, .95, rot=-9)
            etiqueta(c, T, WT("E16", "movida."), "ALGUIEN ENTRÓ", 540, 900, RED, WHITE, 40)
        return c
    c = bg("bg_fachada", T, tl, 1.0, 1.05, 4, .5, .62)
    c.alpha_composite(Image.new("RGBA", (W, H), (255, 220, 170, 35)))
    inner = bg("bg_taller", T, 0, 1.4, 1.4, 1, .5, .6).crop((150, 830, 930, 1400)); c.alpha_composite(inner, (150, 830))
    persiana_en(c, T, 1.0)
    grafiti(c, T, WT("E16", "DEVUÉLVELO.") - .15)
    if T >= S("E17"):
        etiqueta(c, T, WT("E17", "todavía."), "…TODAVÍA", 540, 520, YEL, OL, 46)
    return c

# ---------------------------------------------------------------- final: pantalla partida
RAYO = R.RAYO
_LC = {}
def _lado(name, T):
    if name in _LC: return _LC[name]
    if name == "A":   # Nave 7 de noche
        A = R.bg("bg_noche", 0, 0, 1, 1, 1).convert("RGBA")
        d = ImageDraw.Draw(A)
        d.rectangle((40, 520, 640, 1500), fill=(40, 44, 58), outline=OL, width=10)
        for y in range(560, 1480, 36): d.line((60, y, 620, y), fill=(28, 30, 42), width=8)
        d.text((340, 1000), "7", font=R.font(F_ANTON, 380), fill=(242, 190, 60), anchor="mm", stroke_width=10, stroke_fill=OL)
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((60, 1250, 640, 1600), fill=(242, 190, 60, 70))
        A.alpha_composite(gl.filter(ImageFilter.GaussianBlur(50)))
        put(A, "llave_nave7", 300, 1360, .75, rot=-10)
        A.alpha_composite(Image.new("RGBA", (W, H), (20, 30, 60, 60)))
    else:
        A = bg("bg_taller", 0, 0, 1.25, 1.25, 1, .5, .7).convert("RGBA")
        put(A, "deportivo", 790, 1120, .95); put(A, "centralita", 820, 830, .5)
        A.alpha_composite(Image.new("RGBA", (W, H), (60, 10, 50, 70)))
    _LC[name] = A
    return A

def sc_final(T):
    s0, e0 = TL["E18"]; ta, tb = WT("E18", "A:"), WT("E18", "B:")
    hiA, hiB = ta <= T < tb, tb <= T < e0
    A, B = _lado("A", T), _lado("B", T)
    u = ease((T - s0 + .25) / .45)
    blk = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    c = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    c.alpha_composite(B if not hiA else Image.blend(B, blk, .45), (int(500 * (1 - u)), 0))
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon([(0, 0)] + RAYO + [(0, H)], fill=255)
    c.paste(A if not hiB else Image.blend(A, blk, .45), (int(-700 * (1 - u)), 0), mask)
    d = ImageDraw.Draw(c)
    if u > .9:
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).line(RAYO, fill=CYAN + (255,), width=40, joint="curve")
        c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(c)
        d.line(RAYO, fill=WHITE, width=12, joint="curve"); d.line(RAYO, fill=CYAN, width=5, joint="curve")
    for cx, L_, t1, t2, t3, col, t0, h in ((270, "A", "NAVE 7", "Descubrir el secreto", "- Esta noche, a oscuras", (60, 110, 220), ta, hiA),
                                           (790, "B", "ARRANCARLO", "+ El coche vuelve a rugir", "- Gastas los 600 €", MAG, tb, hiB)):
        k = popscale(T, t0, .35)
        if k > 0: R._texto_opcion(d, cx, 420, L_, t1, t2, t3, col, k, 1.08 if h else 1.0)
    if T >= S("E19"):
        uu = popscale(T, WT("E19", "Comenta"))
        if uu > 0:
            d.rounded_rectangle((470 - 300 * uu, 1400, 470 + 300 * uu, 1480), 40, fill=WHITE)
            if uu > .5: text(d, (470, 1440), "COMENTA  A  o  B", 56, OL)
    return c

R.SCENES = [
    (0, sc_cierre), (S("E02") - .15, sc_nitro_fuera), (S("E03") - .15, sc_se_va), (S("E05") - .2, sc_cuadro),
    (S("E06") - .1, sc_centralita), (S("E07") - .2, sc_golpes), (S("E08") - .25, sc_lucia), (S("E10") - .15, sc_montaje),
    (S("E11") - .1, sc_lucia_feliz), (S("E12") - .15, sc_fotos), (S("E14") - .15, sc_socios), (S("E15") - .15, sc_llave),
    (S("E16") - .15, sc_amanecer), (S("E18") - .25, sc_final),
]
R.IMPACTS = [.7, WT("E01", "B."), WT("E05", "Nada."), WT("E12", "caja") + .5, WT("E14", "socios."), WT("E15", "Nave"),
             WT("E16", "DEVUÉLVELO."), S("E18")]
R.draw_hud = draw_hud

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "still":
        for t in sys.argv[2:]: R.frame(float(t)).save(os.path.join(R.TMP, f"e2_{float(t):06.2f}.jpg"), quality=88)
    elif cmd == "scenes":
        from multiprocessing import Pool
        with Pool(2) as pool:
            pool.starmap(R.render_scene, [(i, os.path.join(R.TMP, f"e2s{i:02d}.mp4")) for i in range(len(R.SCENES))])
    elif cmd == "mix":
        import mix
        mix.main(os.path.join(R.HERE, "el_taller_de_ruben_ep2.mp4"), "e2s")
    elif cmd == "info":
        print({k: [round(a, 2), round(b, 2)] for k, (a, b) in TL.items()}, R.TOTAL)
