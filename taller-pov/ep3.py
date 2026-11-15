"""Ep.3 "Nave 7" (ganó la A con 78 %). Reutiliza render.py con escenas, barra, avisos de voto y final propios.
Uso: python3 ep3.py still 10 20 | python3 ep3.py scenes | python3 ep3.py mix | python3 ep3.py info"""
import os, sys, math
os.environ["GUION"] = "guion3"; os.environ["VOZDIR"] = "voz3"
import render as R
from render import (Image, ImageDraw, ImageFilter, W, H, bg, put, scaled, text, panel, stamp, ficha, etiqueta, dust,
                    neon_flicker, mouth, dark, ease, clamp, popscale, euros, S, E, WT, YEL, RED, WHITE, OL,
                    CYAN, MAG, GRIS, F_UI, F_ANTON)

# pausas propias del Ep.3 y línea de tiempo recalculada
R.GAP.update({"F01": 0, "F03": .3, "F05": .35, "F06": .3, "F07": 1.6, "F08": .2, "F10": .35, "F11": .2, "F12": .35,
              "F13": .25, "F14": .45, "F15": .3, "F16": .45, "F17": .5, "F18": .3, "F19": .25, "F20": .3, "F21": .5, "F22": .3})
R.TL, R.TOTAL = R.timeline(); R.CH = R.chunks()
TL = R.TL
R.EPISODIO, R.DIA = 3, 3
G_ = (46, 160, 90); AZ = (60, 110, 220)

def talk(lid, T): return S(lid) <= T < E(lid)

# ---------------------------------------------------------------- barra superior Ep.3
def draw_hud(canvas, T):
    if T >= S("F21") - .1: return
    base = R.barra_base()
    if T < .25:
        k = ease(T / .25); canvas.alpha_composite(base.crop((0, 0, W, 300)), (0, int(-300 * (1 - k)))); return
    canvas.alpha_composite(base)
    d = ImageDraw.Draw(canvas); x0, y0, x1 = 36, 168, 1044
    t_cen = WT("F13", "centralita.")
    def pop(t): return 1 + .28 * math.sin(clamp((T - t) / .3) * math.pi) if 0 <= T - t < .3 else 1
    for k, v, t, x in (("coch", "2", -9, x0 + 300), ("caja", euros(1010), -9, x0 + 420), ("deuda", "-" + euros(64300), -9, x0 + 600),
                       ("rep", "1", -9, x0 + 880)):
        cy = y0 + 34
        if k == "coch": R.carito(d, x, cy, CYAN)
        if k == "caja": R.coin(d, x, cy, 15)
        if k == "deuda": R.flecha(d, x, cy, 1.0)
        if k == "rep": R.estrella(d, x, cy, 17, (242, 190, 60))
        col = (255, 120, 110) if k == "deuda" else WHITE
        d.text((x + 24, y0 + 35), v, font=R.font(F_ANTON, 34 * pop(t)), fill=col, anchor="lm")
    obj = "Descubrir la Nave 7" if T < t_cen else "¡Centralita conseguida!"
    d.text((x0 + 132, y0 + 87), obj, font=R.font(F_UI, 24 * pop(t_cen)), fill=(120, 240, 150) if T >= t_cen else WHITE, anchor="lm")
    d.text((x1 - 20, y0 + 87), "REPUTACIÓN", font=R.font(F_UI, 18), fill=GRIS, anchor="rm")
    aviso_voto(canvas, T)

# aviso pequeño a mitad de vídeo: votar en la encuesta y comentar por qué
AVISOS = []
def aviso_voto(c, T):
    for t0 in AVISOS:
        if not (t0 <= T < t0 + 5.5): continue
        u = ease((T - t0) / .35) if T < t0 + 5.1 else 1 - ease((T - t0 - 5.1) / .35)
        y = 300 + 20 * (1 - u); a = int(255 * u)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        beat = 1 + .03 * math.sin((T - t0) * 8)
        w2 = 330 * beat
        d.rounded_rectangle((540 - w2, y, 540 + w2, y + 74), 37, fill=(255, 255, 255, a), outline=OL + (a,), width=5)
        d.ellipse((540 - w2 + 10, y + 9, 540 - w2 + 66, y + 65), fill=AZ + (a,)); d.text((540 - w2 + 38, y + 37), "A", font=R.font(F_ANTON, 38), fill=WHITE + (a,), anchor="mm")
        d.ellipse((540 + w2 - 66, y + 9, 540 + w2 - 10, y + 65), fill=MAG + (a,)); d.text((540 + w2 - 38, y + 37), "B", font=R.font(F_ANTON, 38), fill=WHITE + (a,), anchor="mm")
        d.text((540, y + 24), "¿TÚ QUÉ HARÍAS? VOTA EN LA ENCUESTA", font=R.font(F_ANTON, 27), fill=OL + (a,), anchor="mm")
        d.text((540, y + 54), "y dime en comentarios por qué", font=R.font(F_UI, 23), fill=(200, 50, 50, a), anchor="mm")
        c.alpha_composite(lay)

# ---------------------------------------------------------------- piezas
def linterna(c, cx, cy, r=330, amb=215):
    """Oscurece todo salvo un círculo de linterna en (cx, cy)."""
    m = Image.new("L", (W, H), amb); ImageDraw.Draw(m).ellipse((cx - r, cy - r, cx + r, cy + r), fill=0)
    m = m.filter(ImageFilter.GaussianBlur(60))
    sh = Image.new("RGBA", (W, H), (4, 4, 10, 255)); sh.putalpha(m); c.alpha_composite(sh)
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((cx - r * .8, cy - r * .8, cx + r * .8, cy + r * .8), fill=(255, 235, 190, 40))
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(40)))

def humo(c, T, t0, x, y, dur=1.6, n=10):
    if not (0 <= T - t0 < dur): return
    u = (T - t0) / dur
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for i in range(n):
        px = x + (i - n / 2) * 40 + 180 * u * (1 if i % 2 else .6); py = y - 60 * u * (i % 3)
        r = 50 + 120 * u; d.ellipse((px - r, py - r * .6, px + r, py + r * .6), fill=(200, 200, 210, int(110 * (1 - u))))
    c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(14)))

def llamas(c, T, t0, ex, ey, n=3, gap=.28, s=1.0):
    d = ImageDraw.Draw(c)
    for i in range(n):
        tt = t0 + i * gap
        if 0 <= T - tt < .13:
            k = max(.25, 1 - (T - tt) / .13)
            d.ellipse((ex - 10 * s, ey - 34 * k * s, ex + 110 * k * s, ey + 34 * k * s), fill=(255, 150, 40))
            d.ellipse((ex + 5 * s, ey - 18 * k * s, ex + 70 * k * s, ey + 18 * k * s), fill=(255, 240, 160))

def tinte(c, col, a): c.alpha_composite(Image.new("RGBA", (W, H), col + (int(a),)))

# ---------------------------------------------------------------- escenas
def sc_intro(T):
    """F01: medianoche, la llave en la mano. Gancho: quédate hasta el final."""
    c = bg("bg_noche", T, 0, 1.0, 1.08, 6)
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((160, 640, 920, 1300), fill=(242, 190, 60, 70))
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(60)))
    k = popscale(T, .05, .45)
    put(c, "llave_nave7", 540, 900 + 10 * math.sin(T * 1.6), 1.3 * max(k, .02), rot=-8 + 6 * math.sin(T * 1.2))
    stamp(c, T, .15, "GANÓ LA A · 78 %", 540, 470, YEL, -6, 100)
    d = ImageDraw.Draw(c)
    if T >= WT("F01", "Medianoche."): text(d, (540, 640), "00:00", 110 * popscale(T, WT("F01", "Medianoche."), .3), CYAN, stroke=8)
    if T >= WT("F01", "final,"): etiqueta(c, T, WT("F01", "final,"), "QUÉDATE HASTA EL FINAL", 540, 1140, RED, WHITE, 44)
    if T >= WT("F01", "decides"): stamp(c, T, WT("F01", "decides"), "TÚ DECIDES", 540, 1270, MAG, 6, 90)
    return c

def sc_miedo(T):
    """F02: Manolo no lo ve claro."""
    s0 = S("F02")
    c = bg("bg_taller", T, s0, 1.0, 1.08, 6, .5, .55); dark(c, 120)
    neon_flicker(c, T, (300, 220, 800, 520), CYAN, 3)
    put(c, "manolo", 540, 1320 + 6 * math.sin(T * 2.2), 1.0)
    mouth(c, 540, 1194, T, talk("F02", T), 28)
    etiqueta(c, T, WT("F02", "Nave"), "NAVE 7", 540, 470, YEL, OL, 44)
    if T >= WT("F02", "muertos."): stamp(c, T, WT("F02", "muertos."), "ESTAMOS MUERTOS", 540, 620, RED, -8, 90)
    return c

def sc_lucia(T):
    """F03-F04: el deportivo no arranca; Lucía llega derrapando con el Seat de rally."""
    s0 = S("F03"); td = WT("F03", "derrapando") - .25
    c = bg("bg_fachada", T, s0, 1.1, 1.16, 8, .5, .72); dark(c, 70)
    neon_flicker(c, T, (100, 300, 980, 900), MAG, 6)
    if T < WT("F03", "favor."):
        inner = bg("bg_taller", T, 0, 1.4, 1.4, 1, .5, .6).crop((150, 830, 930, 1400)); dark(inner, 80)
        put(inner, "deportivo", 390, 420, .62); c.alpha_composite(inner, (150, 830))
        if T >= WT("F03", "arranca."): stamp(c, T, WT("F03", "arranca."), "NO ARRANCA", 540, 1080, RED, -8, 90)
        return c
    inner = bg("bg_taller", T, 0, 1.4, 1.4, 1, .5, .6).crop((150, 830, 930, 1400)); dark(inner, 80); c.alpha_composite(inner, (150, 830))
    # derrape: entra desde la derecha girando y frena de lado
    u = ease(clamp((T - td) / .7))
    x = 360 + 1000 * (1 - u); rot = -14 * math.sin(u * math.pi) if u < 1 else 0
    if T >= td:
        d = ImageDraw.Draw(c)
        for k in range(2):   # marcas de neumático
            d.line((x + 280, 1430 + k * 30, min(1080, x + 280 + 600 * u), 1410 + k * 30 - 60 * u), fill=(20, 20, 24), width=14)
        put(c, "seat_rally", x + 110, 1310, .75, rot=rot)
        humo(c, T, td + .3, x + 330, 1400)
        if 0 <= T - (td + .55) < .3: text(ImageDraw.Draw(c), (780, 1200), "¡SKRRR!", 100, YEL, stroke=8)
    if T >= S("F04") - .2:
        lu = ease((T - S("F04") + .2) / .4); lx = 890; ly = 1080 + 400 * (1 - lu) + 4 * math.sin(T * 2.4)
        put(c, "lucia", lx, ly, .72); mouth(c, lx, ly - 132, T, talk("F04", T), 14)
        if T >= WT("F04", "conduzco"): etiqueta(c, T, WT("F04", "conduzco"), "\"CONDUZCO YO\"", 540, 560, YEL, OL, 44)
    return c

def sc_poligono(T):
    """F05-F06 (+ pausa): polígono a oscuras; la llave entra, clac, la puerta corre."""
    s0 = S("F05"); t6 = S("F06"); tclac = WT("F06", "Clac."); topen = tclac + .55
    z = 1.0 + .25 * ease(clamp((T - s0) / (t6 - s0 + 1.2)))
    c = bg("bg_poligono", T, s0, z, z, 1, .5, .55)
    # puerta: abre corriendo hacia la izquierda tras el clac (aprox. con el zoom actual)
    p = ease(clamp((T - topen) / 1.3))
    pu = scaled("puerta7", 1.0)
    cx, cy = 540 + (350 - 540) * z, 960 * (1 - z) + 760 * z
    dw = int(380 * z); dh = int(620 * z)
    door = pu.resize((dw, dh))
    if p > 0:
        luz = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(luz).rectangle((cx, cy, cx + dw * p, cy + dh), fill=(40, 60, 90, 120))
        c.alpha_composite(luz)
    c.alpha_composite(door, (int(cx - dw * p), int(cy)))
    c.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 0)))
    if T >= WT("F05", "farola."): etiqueta(c, T, WT("F05", "farola."), "NI UNA FAROLA", 540, 360, YEL, OL, 40)
    if T >= t6 - .1:   # primer plano del candado con la llave
        k = ease(clamp((T - t6 + .1) / .4)) * (1 - ease(clamp((T - tclac - .35) / .3)))
        if k > .02:
            dark(c, 170 * k)
            put(c, "puerta7", 540, 980, 2.3 * k + .01)
            ang = 0 if T < WT("F06", "Gira.") else -60 * ease(clamp((T - WT("F06", "Gira.")) / .3))
            ins = ease(clamp((T - WT("F06", "llave.")) / .4))
            put(c, "llave_nave7", 540 - 240 + 120 * ins, 990 + 40, 1.1 * k + .01, rot=ang)
    if T >= tclac:
        stamp(c, T, tclac, "CLAC", 540, 1210, YEL, -6, 130)
    return c

_NAVE = {}
def nave(T, t0, z0=1.0, z1=1.06, dur=8, fx=.5, fy=.55, luz=True):
    c = bg("bg_nave7", T, t0, z0, z1, dur, fx, fy)
    put(c, "trofeo", 900, 1010, .32)      # vitrina al fondo
    if not luz: return c
    return c

def sc_linterna(T):
    """F07-F08: la linterna descubre un taller escondido; luego se encienden los fluorescentes."""
    s0 = S("F07"); s8 = S("F08")
    c = nave(T, s0, 1.15, 1.2, 10)
    if T < s8 - .1:
        k = clamp((T - s0) / (s8 - s0))
        cx = 300 + 520 * math.sin(k * 2.2) ** 2; cy = 600 + 380 * math.sin(k * 3.1)
        linterna(c, cx, cy, 300 + 60 * k)
        if T >= WT("F07", "escondido."): stamp(c, T, WT("F07", "escondido."), "TALLER ESCONDIDO", 540, 1000, CYAN, -6, 84)
        if T >= WT("F07", "Mejor"): etiqueta(c, T, WT("F07", "Mejor"), "MEJOR QUE EL VUESTRO", 540, 1150, YEL, OL, 40)
        return c
    # fluorescentes: parpadeo y luz
    fl = T - (s8 - .1)
    on = fl > .45 or (fl % .12) < .05
    if not on: linterna(c, 540, 900, 380)
    else:
        for x in (200, 540, 880):
            gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).rectangle((x - 120, 60, x + 120, 80), fill=(230, 245, 255, 255))
            c.alpha_composite(gl); c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(30)))
    for t_, s, x, y in ((WT("F08", "nuevas,"), "HERRAMIENTAS NUEVAS", 540, 420), (WT("F08", "hidráulico…"), "ELEVADOR HIDRÁULICO", 540, 1250),
                        (WT("F08", "planos"), "PLANOS DEL DEPORTIVO", 540, 760)):
        if T >= t_: etiqueta(c, T, t_, s, x, y, CYAN, OL, 40)
    return c

def sc_mentira(T):
    """F09: Manolo, dolido."""
    s0 = S("F09")
    c = nave(T, s0, 1.0, 1.06, 6); dark(c, 40)
    put(c, "manolo", 540, 1320 + 6 * math.sin(T * 2.2), 1.0)
    mouth(c, 540, 1194, T, talk("F09", T), 28)
    if T >= WT("F09", "pescar."): etiqueta(c, T, WT("F09", "pescar."), "\"ME IBA A PESCAR\"", 540, 470, YEL, OL, 42)
    if T >= WT("F09", "ocultó"): stamp(c, T, WT("F09", "ocultó"), "30 AÑOS DE MENTIRA", 540, 630, RED, -6, 80)
    return c

def sc_trofeo(T):
    """F10-F11: el trofeo del Rally 1996: Rubén y Salcedo. Lucía ata cabos."""
    s0 = S("F10"); s11 = S("F11")
    c = Image.new("RGBA", (W, H), (10, 10, 18, 255))
    base = nave(T, s0, 1.6, 1.7, 6, .85, .52); dark(base, 150); c.alpha_composite(base)
    z = .9 + .5 * ease(clamp((T - WT("F10", "trofeo.")) / 1.6)) if T >= WT("F10", "trofeo.") else .9
    if T < s11 - .1:
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((140, 420, 940, 1400), fill=(255, 210, 90, 80))
        c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(70)))
        put(c, "trofeo", 540, 900, z)
        sh = (T * .6) % 1.6   # brillo que recorre la copa
        if sh < .5:
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(ov).polygon([(300 + sh * 900, 400), (380 + sh * 900, 400), (220 + sh * 900, 1300), (140 + sh * 900, 1300)], fill=(255, 255, 255, 60))
            c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(10)))
        if T >= WT("F10", "1996."): etiqueta(c, T, WT("F10", "1996."), "RALLY 1996", 540, 420, YEL, OL, 44)
        if T >= WT("F10", "Salcedo."): stamp(c, T, WT("F10", "Salcedo."), "SALCEDO = NITRO", 540, 1480, RED, -6, 90)
        return c
    put(c, "trofeo", 760, 900, .75, rot=6); dark(c, 30)
    lx, ly = 330, 1060 + 4 * math.sin(T * 2.4)
    put(c, "lucia", lx, ly, .82); mouth(c, lx, ly - 150, T, talk("F11", T), 16)
    if T >= WT("F11", "Nitro"): stamp(c, T, WT("F11", "Nitro"), "¿NITRO CORRÍA CON TU TÍO?", 540, 470, MAG, -4, 64)
    return c

def sc_caja(T):
    """F12-F13: la caja "para el chaval": centralita nueva + un móvil."""
    s0 = S("F12"); tc = WT("F13", "centralita."); tm = WT("F13", "móvil")
    c = nave(T, s0, 1.4, 1.48, 8, .5, .8); dark(c, 90)
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((120, 800, 960, 1500), fill=(255, 230, 170, 60))
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(60)))
    k = popscale(T, s0 + .1, .4)
    put(c, "caja_chaval", 540, 1180, 1.25 * max(k, .02))
    if T >= WT("F12", "chaval.") and T < tc - .2:
        etiqueta(c, T, WT("F12", "chaval."), "\"PARA EL CHAVAL\"", 540, 820, YEL, OL, 44)
    if T >= tc - .2:
        u = ease(clamp((T - tc + .2) / .45))
        rays = Image.new("RGBA", (W, H), (0, 0, 0, 0)); rd = ImageDraw.Draw(rays)
        for i in range(12):
            a = i * math.pi / 6 + T * .4
            rd.polygon([(540, 760), (540 + 900 * math.cos(a - .08), 760 + 900 * math.sin(a - .08)), (540 + 900 * math.cos(a + .08), 760 + 900 * math.sin(a + .08))], fill=(255, 230, 140, int(60 * u)))
        c.alpha_composite(rays.filter(ImageFilter.GaussianBlur(6)))
        put(c, "centralita", 540, 1000 - 300 * u, .9 * max(u, .02))
        if T >= WT("F13", "falta"): etiqueta(c, T, WT("F13", "falta"), "¡LA PIEZA QUE FALTABA!", 540, 920, G_, WHITE, 44)
    if T >= tm:
        u = ease(clamp((T - tm) / .4)); put(c, "movil", 860, 1500 - 120 * u, .42 * max(u, .02), rot=10)
        if u > .6: text(ImageDraw.Draw(c), (860, 1250), "1 NOTA DE VOZ", 34, CYAN, stroke=5)
    return c

def sc_nota(T):
    """F14: segunda nota de voz del tío."""
    s0, e0 = R.TL["F14"]
    c = bg("bg_noche", T, s0, 1.0, 1.05, e0 - s0)
    put(c, "movil", 540, 900, 1.2)
    d = ImageDraw.Draw(c)
    p = clamp((T - s0) / (e0 - s0))
    bx0, bx1 = 540 - 230 * 1.2 / 2 + 160 * .6, 540 + 230 * .6
    d.rounded_rectangle((bx0, 960, bx0 + (bx1 - bx0) * p, 972), 6, fill=CYAN)
    for i in range(14):
        ph = (T * 1.4 + i / 14) % 1
        if T < e0 and i % 5 == 0:
            r = 280 + 260 * ph
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(ov).ellipse((540 - r, 900 - r, 540 + r, 900 + r), outline=CYAN + (int(140 * (1 - ph)),), width=5)
            c.alpha_composite(ov)
    put(c, "tio_foto", 860, 470, .55, rot=8)
    if T >= WT("F14", "socios."): etiqueta(c, T, WT("F14", "socios."), "FUERON SOCIOS", 330, 470, YEL, OL, 40)
    if T >= WT("F14", "esconde."): stamp(c, T, WT("F14", "esconde."), "LO QUE EL COCHE ESCONDE", 540, 1300, RED, -6, 74)
    return c

def sc_deposito(T):
    """F15: el depósito que Rubén nunca dejó tocar."""
    s0 = S("F15"); td = WT("F15", "depósito.")
    if T < td - .3:
        c = nave(T, s0, 1.0, 1.05, 6); dark(c, 50)
        put(c, "manolo", 540, 1320 + 6 * math.sin(T * 2.2), 1.0)
        mouth(c, 540, 1194, T, talk("F15", T), 28)
        if T >= WT("F15", "tornillo"): etiqueta(c, T, WT("F15", "tornillo"), "TORNILLO A TORNILLO", 540, 470, YEL, OL, 42)
        return c
    c = bg("bg_noche", T, td, 1.0, 1.05, 4)
    put(c, "deportivo", 540, 1000, 1.05)
    # rayos X sobre el depósito (parte trasera)
    pulse = .5 + .5 * math.sin((T - td) * 7)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.ellipse((640, 980, 900, 1160), outline=RED + (255,), width=10)
    od.ellipse((620, 960, 920, 1180), outline=RED + (int(140 * pulse),), width=6)
    c.alpha_composite(ov)
    stamp(c, T, td - .1, "EL DEPÓSITO", 540, 620, RED, -6, 100)
    if T >= WT("F15", "nunca."): etiqueta(c, T, WT("F15", "nunca."), "NUNCA LO DEJÓ TOCAR", 540, 1420, YEL, OL, 42)
    return c

def sc_fuera(T):
    """F16-F17: un motor grave fuera. Lucía mira por la ventana: el coche negro sin luces."""
    s0 = S("F16"); s17 = S("F17")
    if T < s17 - .1:
        c = nave(T, s0, 1.1, 1.18, 6); dark(c, 170)
        sh = 4 * math.sin(T * 50) * (.5 + .5 * math.sin(T * 3))
        c = c.transform(c.size, Image.AFFINE, (1, 0, sh, 0, 1, 0))
        d = ImageDraw.Draw(c)
        for i in range(3):   # ondas de sonido del motor
            ph = (T * .9 + i / 3) % 1
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(ov).arc((540 - 200 - 500 * ph, 900 - 200 - 500 * ph, 540 + 200 + 500 * ph, 900 + 200 + 500 * ph), 150, 390, fill=(255, 90, 60, int(160 * (1 - ph))), width=8)
            c.alpha_composite(ov)
        if T >= WT("F16", "motor."): text(ImageDraw.Draw(c), (540, 900), "BRRRMMM…", 110 * popscale(T, WT("F16", "motor."), .3), (255, 110, 80), stroke=8)
        if T >= WT("F16", "conoces."): stamp(c, T, WT("F16", "conoces."), "LO CONOCES", 540, 1250, RED, -6, 90)
        return c
    # vista por la ventana: polígono con el coche negro con luces apagadas
    c = bg("bg_poligono", T, s17, 1.25, 1.32, 6, .5, .9); dark(c, 60)
    put(c, "coche_negro", 540, 1560, .8)
    win = Image.new("RGBA", (W, H), (6, 6, 12, 255)); m = Image.new("L", (W, H), 255)
    ImageDraw.Draw(m).rounded_rectangle((90, 520, 990, 1780), 20, fill=0); win.putalpha(m); c.alpha_composite(win)
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((90, 520, 990, 1780), 20, outline=(60, 64, 80), width=22)
    d.line((540, 520, 540, 1780), fill=(60, 64, 80), width=16); d.line((90, 1150, 990, 1150), fill=(60, 64, 80), width=16)
    lx, ly = 860, 1560 + 4 * math.sin(T * 2.4); put(c, "lucia", lx, ly, .7); mouth(c, lx, ly - 128, T, talk("F17", T), 14)
    if T >= WT("F17", "negro"): etiqueta(c, T, WT("F17", "negro"), "COCHE NEGRO · LUCES APAGADAS", 540, 420, RED, WHITE, 38)
    if T >= WT("F17", "seguido."): stamp(c, T, WT("F17", "seguido."), "OS HA SEGUIDO", 470, 640, YEL, -6, 84)
    return c

def sc_nitro(T):
    """F18-F19: Nitro grita; el motor ruge y los faros os apuntan."""
    s0 = S("F18"); s19 = S("F19"); tf = WT("F19", "faros")
    c = bg("bg_poligono", T, s0, 1.35, 1.42, 8, .5, .95); dark(c, 100)
    rev = 5 * math.sin(T * 60) if T >= WT("F19", "ruge.") else 0
    put(c, "coche_negro", 560 + rev, 1530, 1.0)
    llamas(c, T, WT("F19", "ruge.") + .05, 560 + 470, 1615, 3, .22)
    nx, ny = 420, 900 + 3 * math.sin(T * 1.8)
    if T < s19 + .2:
        put(c, "nitro", nx, ny, .95); mouth(c, nx + 11, ny + 23, T, talk("F18", T), 22)
        if T >= WT("F18", "robó"): etiqueta(c, T, WT("F18", "robó"), "\"RUBÉN ME ROBÓ ALGO\"", 540, 420, RED, WHITE, 42)
        if T >= WT("F18", "cobro."): stamp(c, T, WT("F18", "cobro."), "ME LO COBRO", 540, 580, YEL, -6, 90)
    if T >= tf:   # faros de golpe
        u = ease(clamp((T - tf) / .2))
        put(c, "faros", 560, 1450, 1.2 * u + .01, alpha=u)
        glare = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glare)
        for x in (360, 760): gd.ellipse((x - 260, 1260, x + 260, 1600), fill=(255, 250, 220, int(200 * u)))
        c.alpha_composite(glare.filter(ImageFilter.GaussianBlur(50)))
        if T - tf < .15: tinte(c, (255, 255, 240), 200 * (1 - (T - tf) / .15))
        if T >= WT("F19", "apuntan"): stamp(c, T, WT("F19", "apuntan"), "OS APUNTAN", 540, 600, RED, -6, 100)
    return c

def sc_salida(T):
    """F20: hay una salida por detrás."""
    s0 = S("F20")
    c = nave(T, s0, 1.0, 1.05, 5); dark(c, 110)
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).rectangle((0, 0, W, H), fill=(255, 250, 230, int(40 + 30 * math.sin(T * 9))))
    c.alpha_composite(gl)   # luz de faros colándose
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((640, 380, 960, 480), 12, fill=(30, 160, 80), outline=OL, width=5)
    text(d, (770, 432), "SALIDA", 54, WHITE, stroke=4); d.polygon([(880, 405), (930, 430), (880, 455)], fill=WHITE)
    put(c, "seat_rally", 760, 1530, .6)
    put(c, "manolo", 400, 1320 + 6 * math.sin(T * 2.2), 1.0)
    mouth(c, 400, 1194, T, talk("F20", T), 28)
    if T >= WT("F20", "algo."): etiqueta(c, T, WT("F20", "algo."), "SABRÁ QUE TENEMOS ALGO", 540, 640, YEL, OL, 42)
    return c

RAYO = R.RAYO
_LC = {}
def _lado(name):
    if name in _LC: return _LC[name]
    if name == "A":   # huir con el Seat por detrás
        A = bg("bg_poligono", 0, 0, 1.2, 1.2, 1, .5, .9).convert("RGBA"); dark(A, 60)
        d = ImageDraw.Draw(A)
        for i in range(10): d.line((0, 1200 + i * 40, 700, 1200 + i * 40 - 20), fill=(255, 255, 255, 60), width=4)
        put(A, "seat_rally", 330, 1380, .78, rot=-4)
        put(A, "centralita", 290, 1030, .45, rot=-10)
        A.alpha_composite(Image.new("RGBA", (W, H), (20, 40, 90, 60)))
    else:   # enfrentarse a Nitro ante los faros
        A = bg("bg_poligono", 0, 0, 1.35, 1.35, 1, .5, .95).convert("RGBA"); dark(A, 90)
        put(A, "coche_negro", 790, 1480, .85); put(A, "faros", 790, 1420, 1.0)
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((500, 1250, 1080, 1600), fill=(255, 250, 220, 160))
        A.alpha_composite(gl.filter(ImageFilter.GaussianBlur(50)))
        put(A, "nitro", 820, 960, .7)
        A.alpha_composite(Image.new("RGBA", (W, H), (60, 10, 50, 60)))
    _LC[name] = A
    return A

def sc_final(T):
    s0, e0 = R.TL["F21"]; ta, tb = WT("F21", "A:"), WT("F21", "B:")
    hiA, hiB = ta <= T < tb, tb <= T < e0
    if T >= e0:   # F22: alternan para invitar a votar
        hiA = int((T - e0) / .5) % 2 == 0; hiB = not hiA
    A, B = _lado("A"), _lado("B")
    u = ease((T - s0 + .25) / .45)
    blk = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    c = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    c.alpha_composite(B if not hiA else Image.blend(B, blk, .45), (int(500 * (1 - u)), 0))
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon([(0, 0)] + RAYO + [(0, H)], fill=255)
    c.paste(A if not hiB else Image.blend(A, blk, .45), (int(-700 * (1 - u)), 0), mask)
    d = ImageDraw.Draw(c)
    if u > .9:
        v = .6 + .4 * abs(math.sin(T * 13)) * abs(math.sin(T * 3.1))
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).line(RAYO, fill=CYAN + (int(255 * v),), width=40, joint="curve")
        c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(c)
        d.line(RAYO, fill=WHITE, width=12, joint="curve"); d.line(RAYO, fill=CYAN, width=5, joint="curve")
    for cx, L_, t1, t2, t3, col, t0, h in ((270, "A", "HUIR", "+ Te llevas la centralita", "- Nitro os persigue", AZ, ta, hiA),
                                           (790, "B", "ENFRENTARLO", "+ Sabrás qué robó tu tío", "- Tú solo ante Nitro", MAG, tb, hiB)):
        k = popscale(T, t0, .35)
        if k > 0: R._texto_opcion(d, cx, 420, L_, t1, t2, t3, col, k, 1.08 if h else 1.0)
    return c

R.SCENES = [
    (0, sc_intro), (S("F02") - .15, sc_miedo), (S("F03") - .15, sc_lucia), (S("F05") - .2, sc_poligono),
    (S("F07") - .25, sc_linterna), (S("F09") - .15, sc_mentira), (S("F10") - .15, sc_trofeo), (S("F12") - .15, sc_caja),
    (S("F14") - .2, sc_nota), (S("F15") - .15, sc_deposito), (S("F16") - .2, sc_fuera), (S("F18") - .15, sc_nitro),
    (S("F20") - .15, sc_salida), (S("F21") - .25, sc_final),
]
R.IMPACTS = [.2, WT("F02", "muertos."), WT("F03", "derrapando") + .3, WT("F06", "Clac."), WT("F07", "escondido."),
             WT("F10", "Salcedo."), WT("F13", "centralita."), WT("F14", "esconde."), WT("F15", "depósito."),
             WT("F16", "motor."), WT("F18", "cobro."), WT("F19", "faros"), S("F21")]
AVISOS[:] = [S("F09") - .2, S("F16") - .3]   # a mitad (≈ donde la gente se va) y antes del clímax
R.draw_hud = draw_hud
R.HIDE_LAST_CAPTION = False

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "still":
        for t in sys.argv[2:]: R.frame(float(t)).save(os.path.join(R.TMP, f"e3_{float(t):06.2f}.jpg"), quality=88)
    elif cmd == "info":
        print({k: [round(a, 2), round(b, 2)] for k, (a, b) in R.TL.items()}, round(R.TOTAL, 2))
        print([round(t, 2) for t, f in R.SCENES])
    elif cmd == "scenes":
        from multiprocessing import Pool
        ids = [int(x) for x in sys.argv[2:]] or list(range(len(R.SCENES)))
        with Pool(2) as pool:
            pool.starmap(R.render_scene, [(i, os.path.join(R.TMP, f"e3s{i:02d}.mp4")) for i in ids])
    elif cmd == "mix":
        import mix
        SFX = os.path.join(R.HERE, "sfx")
        efectos = [
            (os.path.join(SFX, "arranque.wav"), WT("F03", "Lucía") - .6, -5),             # el Seat llega acelerando
            (os.path.join(SFX, "seat_derrape.wav"), WT("F03", "derrapando") + .3, -4),     # frenazo de lado
            (os.path.join(SFX, "puerta_nave.wav"), WT("F06", "Clac.") - .05, 0),          # candado + puerta oxidada
            (os.path.join(SFX, "nitro_ralenti.wav"), WT("F16", "motor.") - .2, 0),        # motor grave fuera
            (os.path.join(SFX, "nitro_ruge.wav"), WT("F19", "ruge.") - .25, -2),           # acelerones
            (os.path.join(SFX, "petardeo.wav"), WT("F19", "ruge.") + .1, -5),
        ]
        mix.main(os.path.join(R.HERE, "el_taller_de_ruben_ep3.mp4"), "e3s", efectos)
