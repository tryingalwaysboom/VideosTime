"""Ep.4 "Cara a cara" (elegisteis la B con 68 %: sales tú solo a la luz de los faros).
Uso: python3 ep4.py still 10 20 | python3 ep4.py scenes | python3 ep4.py mix | python3 ep4.py info"""
import os, sys, math, subprocess
os.environ["GUION"] = "guion4"; os.environ["VOZDIR"] = "voz4"
import render as R
from luces import coche_faros
from render import (Image, ImageDraw, ImageFilter, W, H, bg, put, scaled, text, panel, stamp, etiqueta, dust,
                    neon_flicker, mouth, dark, ease, clamp, popscale, euros, S, E, WT, YEL, RED, WHITE, OL,
                    CYAN, MAG, GRIS, F_UI, F_ANTON, F_HAND)
import ep_comun as C
from ep_comun import linterna, humo, llamas, tinte, confeti, barra_voto, ep_chispas, AZ

R.GAP.update({"G01": 0, "G02": .2, "G03": .25, "G04": .35, "G05": .3, "G06": .35, "G07": .25, "G08": .3, "G09": .25,
              "G10": .4, "G11": .3, "G12": .25, "G13": .35, "G14": .3, "G15": .3, "G16": .3, "G17": .35, "G18": .3,
              "G19": .3, "G20": .35, "G21": .5, "G22": .3})
R.TL, R.TOTAL = R.timeline()
R.TL = {k: (a - .1, b - .1) for k, (a, b) in R.TL.items()}; R.TOTAL -= .1   # la voz arranca en el frame 0
R.CH = R.chunks()
R.EPISODIO, R.DIA = 4, 3
G_ = (46, 160, 90)
SEPIA = (112, 78, 40)

def talk(lid, T): return S(lid) <= T < E(lid)
def blank(): return Image.new("RGBA", (W, H), (0, 0, 0, 0))

# ---------------------------------------------------------------- barra superior
def draw_hud(canvas, T):
    if T >= S("G21") - .1: return
    canvas.alpha_composite(R.barra_base())
    d = ImageDraw.Draw(canvas); x0, y0, x1 = 36, 168, 1044
    t_car = WT("G17", "carrera.")
    def pop(t): return 1 + .28 * math.sin(clamp((T - t) / .3) * math.pi) if 0 <= T - t < .3 else 1
    for k, v, x in (("coch", "2", x0 + 300), ("caja", euros(1010), x0 + 420), ("deuda", "-" + euros(64300), x0 + 600), ("rep", "1", x0 + 880)):
        cy = y0 + 34
        if k == "coch": R.carito(d, x, cy, CYAN)
        if k == "caja": R.coin(d, x, cy, 15)
        if k == "deuda": R.flecha(d, x, cy, 1.0)
        if k == "rep": R.estrella(d, x, cy, 17, (242, 190, 60))
        d.text((x + 24, y0 + 35), v, font=R.font(F_ANTON, 34), fill=(255, 120, 110) if k == "deuda" else WHITE, anchor="lm")
    obj = "Plantar cara a Nitro" if T < t_car else "Carrera: sábado, en el puerto"
    d.text((x0 + 132, y0 + 87), obj, font=R.font(F_UI, 24 * pop(t_car)), fill=(255, 140, 120) if T >= t_car else WHITE, anchor="lm")
    d.text((x1 - 20, y0 + 87), "REPUTACIÓN", font=R.font(F_UI, 18), fill=GRIS, anchor="rm")
    C.aviso_voto(canvas, T)

# ---------------------------------------------------------------- piezas propias
def suelo_niebla(c, y=1560, a=50):
    fog = blank(); ImageDraw.Draw(fog).rectangle((0, y, W, y + 200), fill=(150, 150, 190, a))
    c.alpha_composite(fog.filter(ImageFilter.GaussianBlur(40)))

def glow(c, box, col, a, blur=60):
    gl = blank(); ImageDraw.Draw(gl).ellipse(box, fill=col + (int(a),)); c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(blur)))

def poligono(T, t0, z0=1.35, z1=1.42, dur=8, oscuro=100):
    c = bg("bg_poligono", T, t0, z0, z1, dur, .5, .95); dark(c, oscuro); return c

def nitro(c, T, x, y, s, lid=None, ry=24):
    put(c, "nitro", x, y + 3 * math.sin(T * 1.8), s)
    if lid: mouth(c, x + 11.6 * s, y + 3 * math.sin(T * 1.8) + ry * s, T, talk(lid, T), 22 * s)

def manolo(c, T, x, y, s, lid=None):
    yy = y + 6 * math.sin(T * 2.2); put(c, "manolo", x, yy, s)
    if lid: mouth(c, x, yy - 126 * s, T, talk(lid, T), 28 * s)

def lucia(c, T, x, y, s, lid=None):
    yy = y + 4 * math.sin(T * 2.4); put(c, "lucia", x, yy, s)
    if lid: mouth(c, x, yy - 183 * s, T, talk(lid, T), 19 * s)

def seat(c, T, x, y, s, idle=True, flip=False):
    """Seat de rally con vibración de ralentí."""
    im = scaled("seat_rally", s)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    v = 2.5 * math.sin(T * 48) if idle else 0
    c.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2 + v)))

def sepia(c, k=1.0):
    from PIL import ImageOps
    sp = ImageOps.colorize(c.convert("L"), black=(34, 22, 10), white=(255, 232, 190), mid=(150, 108, 62)).convert("RGBA")
    return Image.blend(c, sp, k)

def ralladuras(c, T):
    d = ImageDraw.Draw(c)
    for i in range(5):
        x = (int(T * 37 + i * 211) * 97) % W
        d.line((x, 0, x + 6, H), fill=(255, 240, 210, 60), width=2)

_FOTO = {}
def foto(back=False):
    """La foto vieja: Rubén e Iván con el prototipo blanco (frente) o la fecha escrita a mano (dorso)."""
    if back in _FOTO: return _FOTO[back]
    base = R.layer("foto_r96")
    if back:
        im = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rectangle((40, 40, 1160, 1320), fill=(236, 226, 200), outline=(60, 50, 40), width=10)
        for i in range(9): d.line((90, 300 + i * 110, 1110, 300 + i * 110), fill=(205, 192, 160), width=3)
        d.text((600, 640), "14 · 09 · 1996", font=R.font(F_HAND, 210), fill=(40, 40, 110), anchor="mm")
        d.text((600, 900), "\"el último día\"", font=R.font(F_HAND, 120), fill=(40, 40, 110), anchor="mm")
        d.line((330, 760, 870, 760), fill=(40, 40, 110), width=8)
    else:
        im = base.copy()
        car = R.layer("deportivo"); car = car.resize((int(car.width * .47), int(car.height * .47)))
        lay = Image.new("RGBA", base.size, (0, 0, 0, 0)); lay.alpha_composite(car, (int(600 - car.width / 2), 700 - 210))
        m = Image.new("L", base.size, 0); ImageDraw.Draw(m).rectangle((100, 100, 1100, 1040), fill=255)
        im.paste(lay, (0, 0), Image.composite(lay.split()[3], Image.new("L", base.size, 0), m))
        tint = Image.new("RGBA", base.size, (255, 200, 120, 55)); tm = Image.new("RGBA", base.size, (0, 0, 0, 0)); tm.paste(tint, (0, 0), m)
        im.alpha_composite(tm)
    _FOTO[back] = im
    return im

def put_img(c, im, cx, cy, s, rot=0, sx=1.0):
    w, h = max(2, int(im.width * s / 2 * sx)), max(2, int(im.height * s / 2))
    t = im.resize((w, h), Image.LANCZOS)
    if rot: t = t.rotate(rot, expand=True, resample=Image.BICUBIC)
    c.alpha_composite(t, (int(cx - t.width / 2), int(cy - t.height / 2)))

_PUERTO = {}
def bg_puerto(T, t0, z0=1.0, z1=1.06, dur=8):
    if "b" not in _PUERTO:
        im = Image.new("RGBA", (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(im)
        for y in range(0, 1100):
            k = y / 1100; d.line((0, y, W, y), fill=(int(10 + 22 * k), int(10 + 14 * k), int(30 + 40 * k)))
        for i in range(90): x, y = (i * 389) % W, (i * 211) % 900; d.ellipse((x, y, x + 3, y + 3), fill=(230, 230, 255))
        d.ellipse((760, 440, 860, 540), fill=(245, 240, 215))
        for x, h, w in ((40, 260, 120), (190, 330, 90), (300, 210, 160), (520, 280, 110), (650, 190, 140)):   # contenedores y grúas
            d.rectangle((x, 1100 - h, x + w, 1100), fill=(18, 20, 36))
        for gx in (240, 820):
            d.line((gx, 1100, gx, 620), fill=(30, 34, 54), width=18); d.line((gx - 160, 640, gx + 220, 640), fill=(30, 34, 54), width=14)
            d.line((gx, 620, gx - 160, 640), fill=(30, 34, 54), width=6); d.ellipse((gx + 200, 630, gx + 222, 652), fill=(255, 60, 60))
        for y in range(1100, 1250):
            k = (y - 1100) / 150; d.line((0, y, W, y), fill=(int(14 + 10 * k), int(20 + 12 * k), int(44 + 20 * k)))
        for i in range(10):   # reflejo de la luna en el agua
            y = 1112 + i * 13; w = 40 - i * 3 + (i * 37) % 18
            d.line((810 - w, y, 810 + w, y), fill=(200, 195, 170, 255), width=2)
        d.rectangle((0, 1250, W, H), fill=(36, 36, 46)); d.rectangle((0, 1250, W, 1264), fill=(200, 180, 60))
        for x in (90, 990):
            d.line((x, 1250, x, 800), fill=(50, 52, 66), width=12); d.ellipse((x - 26, 780, x + 26, 820), fill=(255, 220, 140))
        im = im.filter(ImageFilter.GaussianBlur(1.2))
        gl = blank(); g = ImageDraw.Draw(gl)
        for x in (90, 990): g.ellipse((x - 220, 600, x + 220, 1400), fill=(255, 200, 110, 60))
        im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(60)))
        _PUERTO["b"] = im
    z = z0 + (z1 - z0) * clamp((T - t0) / dur)
    im = _PUERTO["b"].resize((int(W * z), int(H * z)), Image.BILINEAR)
    ox, oy = (im.width - W) / 2, (im.height - H) * .7
    return im.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))

def bandera(d, cx, cy, w=180, h=120, t=0):
    n = 6; cw, ch = w / n, h / 4
    for i in range(n):
        for j in range(4):
            ox = cx - w / 2 + i * cw; oy = cy - h / 2 + j * ch + 10 * math.sin(t * 6 + i * .8)
            d.rectangle((ox, oy, ox + cw, oy + ch), fill=WHITE if (i + j) % 2 else (20, 20, 24))
    d.line((cx - w / 2, cy - h / 2 - 10, cx - w / 2, cy + h / 2 + 150), fill=(200, 200, 210), width=10)

# ---------------------------------------------------------------- escenas
def sc_intro(T):
    """G01: resultado de la votación (B 68 %) con confeti; luego caminas hacia los faros."""
    tm = max(WT("G01", "Sales") - .15, 2.4)
    if T < tm:
        c = poligono(T, 0, 1.2, 1.3, tm, 120)
        glow(c, (-120, 520, 760, 1180), MAG, 90, 80); glow(c, (420, 700, 1200, 1300), AZ, 60, 80)
        d = ImageDraw.Draw(c)
        text(d, (540, 430), "RESULTADO PARTE 3", 70, YEL, stroke=8)
        barra_voto(c, T, 640, "A", "HUIR CON EL SEAT", 32, AZ, False, 0)
        barra_voto(c, T, 830, "B", "ENFRENTARTE A NITRO", 68, MAG, True, 0)
        R.estrella(ImageDraw.Draw(c), 960, 750, 30 * (1 + .15 * math.sin(T * 8)), (242, 190, 60))
        stamp(c, T, -1, "¡ELEGISTEIS LA B!", 540, 1080, YEL, -6, 116)
        confeti(c, T, .3)
        return c
    c = poligono(T, tm, 1.3, 1.5, 7, 110)
    bob = 8 * math.sin(T * 7)
    coche_faros(c, 640, 1230 + bob * .3, .8, 1.0)
    suelo_niebla(c)
    if T >= WT("G01", "faros."): etiqueta(c, T, WT("G01", "faros."), "TÚ SOLO · A LA LUZ DE LOS FAROS", 540, 560, YEL, OL, 40)
    if T >= WT("G01", "final,"): etiqueta(c, T, WT("G01", "final,"), "QUÉDATE HASTA EL FINAL", 540, 720, RED, WHITE, 44)
    if T >= WT("G01", "decides"): stamp(c, T, WT("G01", "decides"), "TÚ DECIDES", 540, 880, MAG, 6, 96)
    return c

def sc_grito(T):
    """G02: Manolo grita desde la puerta de la nave."""
    s0 = S("G02")
    c = bg("bg_nave7", T, s0, 1.0, 1.08, 4, .5, .55); dark(c, 120)
    glow(c, (300, 300, 1300, 1300), (255, 245, 210), 70 + 30 * math.sin(T * 9), 90)   # faros colándose
    manolo(c, T, 540 + 4 * math.sin(T * 30), 1320, 1.0, "G02")
    tinte(c, (140, 0, 0), 30)
    if T >= WT("G02", "aquí!"): stamp(c, T, WT("G02", "aquí!"), "¡VUELVE!", 540, 520, RED, -8, 120)
    if T >= WT("G02", "loco!"): etiqueta(c, T, WT("G02", "loco!"), "\"ESE TÍO ESTÁ LOCO\"", 540, 700, YEL, OL, 42)
    return c

def sc_camina(T):
    """G03: caminas hacia el coche negro; los faros ciegan; el motor ruge una vez y se apaga."""
    s0, e0 = R.TL["G03"]; tc = WT("G03", "ciegan."); tr = WT("G03", "ruge"); ta = WT("G03", "apaga.")
    k = ease(clamp((T - s0) / (tc - s0)))
    c = poligono(T, s0, 1.4 + .25 * k, 1.45 + .25 * k, 1, 110)
    bob = 9 * math.sin(T * 7) * (1 - clamp((T - tc) / .5))
    rev = 6 * math.sin(T * 60) if tr <= T < ta else 0
    u = 1.0 if T < ta else .55 + .45 * math.exp(-(T - ta) * 6)
    sx = 640 + 60 * k; s = .8 + .25 * k
    coche_faros(c, sx, 1230 + bob - 80 * k, s, u, rev=rev, largo=900 + 300 * k)
    llamas(c, T, tr + .05, sx + 470 * s, 1230 + bob - 80 * k + 85 * s, 3, .2, s)
    if tr <= T < ta: humo(c, T, tr + .1, sx + 470 * s, 1330, 1.2, 6)
    suelo_niebla(c)
    if tc - .05 <= T < tc + .35: tinte(c, (255, 255, 240), 230 * (1 - (T - tc + .05) / .4))
    if T >= WT("G03", "negro."): etiqueta(c, T, WT("G03", "negro."), "EL COCHE NEGRO", 540, 520, GRIS, OL, 40)
    if tc <= T < tr - .1: stamp(c, T, tc, "TE CIEGAN", 540, 680, YEL, -6, 96)
    if tr - .1 <= T < ta: stamp(c, T, tr - .1, "¡BRRRAAM!", 540, 680, RED, 6, 100)
    if T >= ta: stamp(c, T, ta, "…Y SE APAGA", 540, 680, CYAN, -4, 90)
    return c

def sc_nitro1(T):
    """G04: Nitro, burlón, delante de su coche."""
    s0 = S("G04")
    c = poligono(T, s0, 1.35, 1.42, 6, 100)
    coche_faros(c, 740, 1200, .8, .55, largo=700)
    nitro(c, T, 400, 960, 1.0, "G04")
    if T >= WT("G04", "sobrino"): etiqueta(c, T, WT("G04", "sobrino"), "\"EL SOBRINO DE RUBÉN\"", 540, 470, YEL, OL, 40)
    if T >= WT("G04", "agallas"): stamp(c, T, WT("G04", "agallas"), "MÁS AGALLAS QUE SU TÍO", 540, 640, RED, -5, 74)
    return c

def sc_pregunta(T):
    """G05: la única pregunta que importa."""
    s0, e0 = R.TL["G05"]; tq = WT("G05", "robó") - .35
    c = poligono(T, s0, 1.6, 1.7, 5, 170)
    put(c, "nitro", 540, 1130, 1.25, alpha=.55)
    linterna(c, 540, 820, 380, 170)
    d = ImageDraw.Draw(c)
    if T >= WT("G05", "importa:") - .2: etiqueta(c, T, WT("G05", "importa:") - .2, "LA ÚNICA PREGUNTA QUE IMPORTA", 540, 500, GRIS, OL, 36)
    if T >= tq:
        u = ease(clamp((T - tq) / .35))
        panel(c, (110, 640, 970, 900), fill=(14, 12, 26), alpha=int(235 * u), rad=30, outline=RED, ow=6)
        d = ImageDraw.Draw(c)
        if u > .5:
            text(d, (540, 720), "¿QUÉ TE ROBÓ", 92 * (1 + .03 * math.sin(T * 7)), WHITE, stroke=7)
            text(d, (540, 830), "MI TÍO?", 92 * (1 + .03 * math.sin(T * 7)), RED, stroke=7)
    return c

def sc_flash(T):
    """G06-G07: flashback en sepia: Rally 1996, el prototipo, la huida de Rubén y lo escondido dentro."""
    s0 = S("G06"); s7 = S("G07"); tp = WT("G06", "premio?"); tdes = WT("G07", "desapareció"); tdent = WT("G07", "escondido")
    if T < tp - .1:   # podio con flashes
        c = bg("bg_noche", T, s0, 1.0, 1.06, 5); glow(c, (140, 420, 940, 1400), (255, 210, 90), 90, 70)
        put(c, "trofeo", 540, 960, .9 + .08 * ease(clamp((T - s0) / 3)))
        confeti(c, T, WT("G06", "ganamos") if T >= S("G06") + .3 else 99, 50)
        fl = (T - s0) % .9
        if fl < .08: tinte(c, (255, 255, 255), 160 * (1 - fl / .08))
        c = sepia(c, .85); ralladuras(c, T)
        d = ImageDraw.Draw(c)
        text(d, (540, 470), "1996", 180 * (1 + .03 * math.sin(T * 5)), YEL, stroke=9)
        if T >= WT("G06", "juntos."): etiqueta(c, T, WT("G06", "juntos."), "RUBÉN + NITRO · CAMPEONES", 540, 1440, YEL, OL, 40)
        return c
    if T < s7 - .1:   # el premio: el prototipo blanco
        c = bg("bg_noche", T, tp, 1.0, 1.05, 4)
        u = ease(clamp((T - tp) / .5))
        rays = blank(); rd = ImageDraw.Draw(rays)
        for i in range(12):
            a = i * math.pi / 6 + T * .4
            rd.polygon([(540, 980), (540 + 1000 * math.cos(a - .08), 980 + 1000 * math.sin(a - .08)), (540 + 1000 * math.cos(a + .08), 980 + 1000 * math.sin(a + .08))], fill=(255, 230, 140, int(55 * u)))
        c.alpha_composite(rays.filter(ImageFilter.GaussianBlur(6)))
        put(c, "deportivo", 540, 1060 + 40 * (1 - u), 1.0 * max(u, .05))
        c = sepia(c, .7); ralladuras(c, T)
        if T >= WT("G06", "coche."): etiqueta(c, T, WT("G06", "coche."), "EL PREMIO: ESE COCHE", 540, 560, YEL, OL, 42)
        if T >= WT("G06", "único."): stamp(c, T, WT("G06", "único."), "PROTOTIPO ÚNICO", 540, 740, RED, -5, 96)
        return c
    # G07: era de los dos… Rubén se lo lleva de noche… y lo que había dentro
    c = bg("bg_noche", T, s7, 1.0, 1.05, 6)
    gone = ease(clamp((T - tdes - .2) / .9))
    if T < tdent - .2:
        x = 540 - 1300 * gone
        put(c, "deportivo", x, 1060, 1.0)
        if gone > 0: humo(c, T, tdes + .2, x + 560, 1150, 1.2, 6)
        put_img(c, R.layer("foto_r96"), 540, 640, .55 * (1 - gone) + .001, rot=-4)
        c = sepia(c, .7); ralladuras(c, T)
        if T >= WT("G07", "dos."): etiqueta(c, T, WT("G07", "dos."), "ERA DE LOS DOS", 540, 1000 if gone < .5 else 560, YEL, OL, 42)
        if T >= tdes: stamp(c, T, tdes, "RUBÉN DESAPARECIÓ", 540, 760, RED, -6, 86)
        return c
    put(c, "deportivo", 540, 1060, 1.05)
    pulse = .5 + .5 * math.sin((T - tdent) * 7)
    ov = blank(); od = ImageDraw.Draw(ov)
    od.ellipse((660, 1010, 920, 1190), outline=RED + (255,), width=10); od.ellipse((640, 990, 940, 1210), outline=RED + (int(140 * pulse),), width=6)
    c = sepia(c, .5); c.alpha_composite(ov)
    stamp(c, T, tdent, "ESCONDIDO DENTRO", 540, 640, RED, -6, 96)
    text(ImageDraw.Draw(c), (790, 860), "?", 150 * (1 + .1 * math.sin(T * 8)), YEL, stroke=8)
    return c

def sc_acerca(T):
    """G08: Nitro se acerca, a contraluz de sus faros."""
    s0, e0 = R.TL["G08"]
    c = poligono(T, s0, 1.4, 1.5, 6, 130)
    coche_faros(c, 700, 1180, .7, .6, largo=500)
    k = ease(clamp((T - s0) / (e0 - s0 + .3)))
    glow(c, (240, 500, 840, 1500), (255, 240, 200), 70, 70)   # contraluz
    nitro(c, T, 540, 1000 + 160 * k, .8 + .55 * k)
    dark(c, 30)
    if T >= WT("G08", "gasolina…"): etiqueta(c, T, WT("G08", "gasolina…"), "HUELE A GASOLINA…", 540, 520, YEL, OL, 42)
    if T >= WT("G08", "rencor."): stamp(c, T, WT("G08", "rencor."), "…Y A RENCOR", 540, 680, RED, -6, 100)
    return c

def sc_lona(T):
    """G09: treinta años buscándolo; estaba bajo una lona en un taller de barrio."""
    s0 = S("G09"); tl = WT("G09", "barrio,") - .2
    c = poligono(T, s0, 1.35, 1.42, 6, 120)
    nitro(c, T, 330, 1000, .9, "G09")
    if T >= WT("G09", "30"): stamp(c, T, WT("G09", "30"), "30 AÑOS BUSCÁNDOLO", 540, 520, RED, -5, 84)
    if T >= tl:   # recuadro: el deportivo bajo la lona en el taller
        u = ease(clamp((T - tl) / .4))
        inner = bg("bg_taller", T, 0, 1.4, 1.4, 1, .5, .6).crop((150, 830, 930, 1400)); dark(inner, 60)
        put(inner, "deportivo", 390, 420, .62); put(inner, "lona", 390, 400, .64)
        inner = inner.resize((int(inner.width * (.4 + .6 * u)), int(inner.height * (.4 + .6 * u))))
        bx, by = int(640 - inner.width / 2), int(1000 - inner.height / 2)
        ImageDraw.Draw(c).rounded_rectangle((bx - 10, by - 10, bx + inner.width + 10, by + inner.height + 10), 16, fill=WHITE)
        c.alpha_composite(inner, (bx, by))
        if T >= WT("G09", "lona."): etiqueta(c, T, WT("G09", "lona."), "DEBAJO DE UNA LONA", 640, 1230, YEL, OL, 40)
    return c

def sc_seat(T):
    """G10: detrás de ti, el Seat de Lucía sale de la nave despacio, sin luces, al ralentí."""
    s0, e0 = R.TL["G10"]
    c = bg("bg_poligono", T, s0, 1.15, 1.22, 7, .5, .7); dark(c, 120)
    u = ease(clamp((T - WT("G10", "sale") + .2) / 3.2))
    seat(c, T, 540 - 60 * u, 1150 + 260 * u, .55 + .4 * u)
    humo(c, T, s0 + .5 + int((T - s0) / 1.1) * 1.1, 540 - 60 * u + 460 * (.55 + .4 * u), 1150 + 260 * u + 150 * (.55 + .4 * u), 1.1, 4)
    suelo_niebla(c, 1500, 40)
    if T >= WT("G10", "ti,") - .3: etiqueta(c, T, WT("G10", "ti,") - .3, "DETRÁS DE TI", 540, 480, GRIS, OL, 40)
    if T >= WT("G10", "luces."): stamp(c, T, WT("G10", "luces."), "SIN LUCES", 540, 640, CYAN, -6, 96)
    if T >= WT("G10", "ralentí."): etiqueta(c, T, WT("G10", "ralentí."), "MOTOR AL RALENTÍ", 540, 800, YEL, OL, 42)
    return c

def sc_lucia(T):
    """G11: Lucía, apoyada en el Seat, calienta el motor."""
    s0 = S("G11"); tc = WT("G11", "caliento")
    c = poligono(T, s0, 1.3, 1.36, 5, 90)
    rev = 4 * math.sin(T * 70) if T >= tc else 0
    seat(c, T, 600 + rev, 1260, .85, flip=True)
    if T >= tc: humo(c, T, tc, 209, 1387, 1.4, 6)
    lucia(c, T, 820, 1130, .78, "G11")
    if T >= WT("G11", "pegar,"): etiqueta(c, T, WT("G11", "pegar,"), "\"SI OS VAIS A PEGAR, AVISAD\"", 540, 480, YEL, OL, 38)
    if T >= tc: stamp(c, T, tc, "CALENTANDO MOTOR", 540, 650, MAG, -5, 84)
    return c

def sc_punos(T):
    """G12: Nitro no pelea con los puños."""
    s0 = S("G12")
    c = poligono(T, s0, 1.35, 1.42, 5, 100)
    seat(c, T, 860, 1420, .5, flip=True)
    nitro(c, T, 470, 960, 1.0, "G12")
    if T >= WT("G12", "rallista."): etiqueta(c, T, WT("G12", "rallista."), "\"TRANQUILA, RALLISTA\"", 540, 470, YEL, OL, 40)
    if T >= WT("G12", "puños."): stamp(c, T, WT("G12", "puños."), "NO PELEA CON LOS PUÑOS", 540, 640, RED, -5, 72)
    return c

def sc_foto(T):
    """G13: la foto vieja: dos chavales, un coche blanco… y una fecha por detrás."""
    s0, e0 = R.TL["G13"]; tf = WT("G13", "fecha") - .1
    c = poligono(T, s0, 1.6, 1.66, 7, 170)
    glow(c, (120, 400, 960, 1400), (255, 220, 160), 70, 70)
    up = ease(clamp((T - WT("G13", "foto") + .3) / .6))
    y = 960 + 900 * (1 - up)
    fl = clamp((T - tf) / .45)   # giro de la foto
    sx = abs(math.cos(fl * math.pi)); back = fl > .5
    put_img(c, foto(back), 540, y, 1.0, rot=-3 + 3 * fl, sx=max(sx, .02))
    d = ImageDraw.Draw(c)
    if not back and T >= WT("G13", "chavales,"):
        u = ease(clamp((T - WT("G13", "chavales,")) / .3))
        d.ellipse((330, 650, 750, 820), outline=YEL, width=int(8 * u) + 1)
        etiqueta(c, T, WT("G13", "chavales,"), "RUBÉN E IVÁN", 540, 520, YEL, OL, 40)
    if not back and T >= WT("G13", "blanco…"):
        etiqueta(c, T, WT("G13", "blanco…"), "EL COCHE BLANCO", 540, 1300, CYAN, OL, 40)
    if back and T >= tf + .3: stamp(c, T, tf + .3, "UNA FECHA", 540, 520, RED, -5, 90)
    return c

def sc_manolo_foto(T):
    """G14: Manolo hizo esa foto."""
    s0 = S("G14")
    c = poligono(T, s0, 1.2, 1.26, 5, 120)
    tinte(c, (20, 40, 110), 50)
    put_img(c, foto(False), 820, 620, .4, rot=8)
    manolo(c, T, 470, 1320, 1.0, "G14")
    if T >= WT("G14", "yo."): etiqueta(c, T, WT("G14", "yo."), "\"LA HICE YO\"", 400, 560, YEL, OL, 42)
    if T >= WT("G14", "antes"): stamp(c, T, WT("G14", "antes"), "EL DÍA ANTES", 540, 760, RED, -6, 96)
    return c

def sc_nitro_manolo(T):
    """G15: Nitro provoca a Manolo."""
    s0 = S("G15")
    c = poligono(T, s0, 1.35, 1.42, 6, 100)
    manolo(c, T, 820, 1470, .7)
    nitro(c, T, 360, 960, .95, "G15")
    if T >= WT("G15", "tiempo."): etiqueta(c, T, WT("G15", "tiempo."), "\"MANOLO… CUÁNTO TIEMPO\"", 540, 480, YEL, OL, 40)
    if T >= WT("G15", "secretos"): stamp(c, T, WT("G15", "secretos"), "¿QUÉ SECRETOS?", 540, 650, RED, -5, 90)
    return c

def sc_tension(T):
    """G16: Manolo aprieta los puños; Lucía acelera en vacío; tensión cortante."""
    s0, e0 = R.TL["G16"]; ta = WT("G16", "acelera"); tc = WT("G16", "cortar")
    if T < ta - .15:   # primer plano de Manolo temblando de rabia
        c = poligono(T, s0, 1.5, 1.6, 4, 120); tinte(c, (120, 0, 0), 50)
        manolo(c, T, 540 + 6 * math.sin(T * 45), 1380, 1.15)
        if T >= WT("G16", "puños."): stamp(c, T, WT("G16", "puños."), "PUÑOS APRETADOS", 540, 560, RED, -5, 86)
        return c
    c = poligono(T, ta - .15, 1.3, 1.4, 4, 100)
    rev = 6 * math.sin(T * 75)
    seat(c, T, 540 + rev, 1200, .95)
    llamas(c, T, ta + .1, 977, 1342, 4, .25, .9)
    humo(c, T, ta + .1, 977, 1342, 1.6, 7)
    if T >= ta: etiqueta(c, T, ta, "LUCÍA ACELERA EN VACÍO", 540, 520, MAG, WHITE, 40)
    if T >= tc - .1:   # tajo de cuchillo cruzando la pantalla
        u = ease(clamp((T - tc + .1) / .25))
        ov = blank(); od = ImageDraw.Draw(ov)
        od.line((60, 1150, 60 + 960 * u, 650), fill=WHITE + (255,), width=10)
        c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(6))); c.alpha_composite(ov)
        stamp(c, T, WT("G16", "cuchillo."), "TENSIÓN MÁXIMA", 540, 980, RED, -8, 90)
    return c

def sc_carrera(T):
    """G17: como en los viejos tiempos: una carrera."""
    s0 = S("G17"); tc = WT("G17", "carrera.")
    c = poligono(T, s0, 1.35, 1.42, 6, 100)
    nitro(c, T, 540 if T < tc else 330, 980, .95 if T < tc else .8, "G17")
    if T >= WT("G17", "viejos"): etiqueta(c, T, WT("G17", "viejos"), "COMO EN LOS VIEJOS TIEMPOS", 540, 480, YEL, OL, 40)
    if T >= tc:
        u = ease(clamp((T - tc) / .3)); d = ImageDraw.Draw(c)
        bandera(d, 760, 900, 220 * max(u, .05), 150 * max(u, .05), T)
        stamp(c, T, tc, "UNA CARRERA", 540, 650, RED, -6, 120)
    return c

def sc_puerto(T):
    """G18: sábado, de noche, en el puerto. Lo que hay en juego."""
    s0, e0 = R.TL["G18"]; tg = WT("G18", "ganas,"); ty = WT("G18", "yo…"); td = WT("G18", "dentro.")
    c = bg_puerto(T, s0, 1.0, 1.08, e0 - s0)
    put(c, "deportivo", 300, 1250, .52); coche_faros(c, 790, 1190, .52, .7, largo=260)
    d = ImageDraw.Draw(c)
    bandera(d, 540, 1060, 90, 60, T)
    if T >= WT("G18", "sábado,"): etiqueta(c, T, WT("G18", "sábado,"), "SÁBADO", 540, 470, YEL, OL, 44)
    if T >= WT("G18", "noche,"): etiqueta(c, T, WT("G18", "noche,"), "DE NOCHE", 540, 560, CYAN, OL, 40)
    if T >= WT("G18", "puerto."): etiqueta(c, T, WT("G18", "puerto."), "EN EL PUERTO", 540, 650, WHITE, OL, 40)
    if tg <= T < ty:
        panel(c, (110, 760, 970, 940), fill=(14, 40, 24), alpha=230, rad=26, outline=G_, ow=6); d = ImageDraw.Draw(c)
        text(d, (540, 810), "SI GANAS", 56, (120, 240, 150), stroke=5); text(d, (540, 885), "EL COCHE ES TUYO", 60, WHITE, stroke=5)
    if ty <= T < td - .1:
        panel(c, (110, 760, 970, 940), fill=(50, 12, 12), alpha=230, rad=26, outline=RED, ow=6); d = ImageDraw.Draw(c)
        text(d, (540, 810), "SI GANA ÉL", 56, (255, 140, 130), stroke=5); text(d, (540, 885), "SE LO LLEVA", 60, WHITE, stroke=5)
    if T >= td - .1:
        stamp(c, T, td - .1, "CON TODO LO QUE LLEVA DENTRO", 540, 850, RED, -5, 60)
        pulse = .5 + .5 * math.sin((T - td) * 7)
        ov = blank(); ImageDraw.Draw(ov).ellipse((370, 1210, 500, 1300), outline=RED + (int(255 * pulse),), width=8); c.alpha_composite(ov)
    return c

def sc_se_va(T):
    """G19: Nitro se sube al coche, petardea dos veces y desaparece en la oscuridad."""
    s0, e0 = R.TL["G19"]; tp = WT("G19", "Petardea"); td = WT("G19", "desaparece") - .3
    c = poligono(T, s0, 1.35, 1.42, 7, 110)
    on = T >= WT("G19", "negro.") - .2
    rev = 5 * math.sin(T * 60) if on and T < td else 0
    go = ease(clamp((T - td) / 1.6)) ** 1.6
    x = 700 - 1700 * go
    if T < WT("G19", "negro.") - .2: nitro(c, T, 380, 960, .8)
    coche_faros(c, x, 1150, .8, 1.0 if on else .5, rev=rev)
    llamas(c, T, tp + .1, x + 376, 1218, 2, .38, .8)
    if go > 0:
        d = ImageDraw.Draw(c)
        for i in range(8): d.line((x + 470, 1070 + i * 25, x + 470 + 500 * go, 1150 + i * 25), fill=(255, 255, 255, 50), width=3)
        humo(c, T, td, x + 470, 1220, 1.5, 7)
        dark(c, 120 * go)
    suelo_niebla(c)
    if T >= tp: stamp(c, T, tp, "¡PAM! ¡PAM!", 540, 560, YEL, -6, 96)
    if T >= WT("G19", "oscuridad."): etiqueta(c, T, WT("G19", "oscuridad."), "DESAPARECE EN LA OSCURIDAD", 540, 740, GRIS, OL, 40)
    return c

def sc_aviso(T):
    """G20: Manolo, preocupado: ese coche no corre desde hace 30 años; Nitro no pierde nunca."""
    s0 = S("G20")
    c = bg("bg_nave7", T, s0, 1.0, 1.06, 6, .5, .55); dark(c, 110)
    put(c, "deportivo", 760, 1210, .5)
    dust(c, T, 40)
    manolo(c, T, 400, 1320, 1.0, "G20")
    if T >= WT("G20", "corrido"): etiqueta(c, T, WT("G20", "corrido"), "30 AÑOS SIN CORRER", 540, 480, YEL, OL, 42)
    if T >= WT("G20", "nunca."): stamp(c, T, WT("G20", "nunca."), "NITRO NO PIERDE NUNCA", 540, 660, RED, -6, 80)
    return c

RAYO = R.RAYO
_LC = {}
def _lado(name):
    if name in _LC: return _LC[name]
    if name == "A":   # aceptar la carrera: preparar el deportivo en la nave
        A = bg("bg_nave7", 0, 0, 1.15, 1.15, 1, .5, .6).convert("RGBA"); dark(A, 60)
        glow(A, (40, 1100, 760, 1600), CYAN, 110, 40)
        put(A, "deportivo", 330, 1340, .7)
        put(A, "centralita", 300, 1020, .42, rot=-10)
        A.alpha_composite(Image.new("RGBA", (W, H), (20, 40, 90, 60)))
    else:   # abrir el depósito esta noche
        A = bg("bg_nave7", 0, 0, 1.3, 1.3, 1, .5, .6).convert("RGBA"); dark(A, 150)
        put(A, "deportivo", 820, 1340, .7)
        linterna(A, 900, 1330, 260, 190)
        ov = blank(); od = ImageDraw.Draw(ov)
        od.ellipse((860, 1290, 990, 1380), outline=RED + (255,), width=8); A.alpha_composite(ov)
        text(ImageDraw.Draw(A), (930, 1180), "?", 110, YEL, stroke=7)
        A.alpha_composite(Image.new("RGBA", (W, H), (60, 10, 50, 60)))
    _LC[name] = A
    return A

def boton_seguir(c, T, ts, y=1150):
    """+ SÍGUEME: aparece, el dedo lo pulsa y pasa a SIGUIENDO."""
    k = popscale(T, ts - .3, .3)
    if k <= 0: return
    done = T >= ts + .6
    press = 1 - .08 * math.sin(clamp((T - ts - .35) / .25) * math.pi)
    lay = blank(); ld = ImageDraw.Draw(lay)
    fill, fg, s = ((RED, WHITE, "+  SÍGUEME") if not done else (WHITE, OL, "   SIGUIENDO"))
    ld.rounded_rectangle((250, y - 56, 830, y + 56), 56, fill=fill, outline=WHITE if not done else OL, width=6)
    text(ld, (540, y), s, 60, fg)
    if done: ld.line((360, y, 382, y + 24, 420, y - 24), fill=G_, width=12, joint="curve")
    sc = k * press * (1 + (.05 * math.sin(T * 9) if not done else 0))
    if abs(sc - 1) > .01:
        big = lay.resize((int(W * sc), int(H * sc)), Image.BILINEAR)
        ox, oy = int(540 - 540 * sc), int(y - y * sc)
        lay = blank(); lay.alpha_composite(big, (max(0, ox), max(0, oy)), (max(0, -ox), max(0, -oy)))
    c.alpha_composite(lay)
    tt = ts + .35
    if tt - .3 <= T < tt + .9:
        p = ease((T - (tt - .3)) / .3); fx, fy = 700 + 160 * (1 - p), y + 30 + 160 * (1 - p)
        if T >= tt:
            r_ = 30 + 220 * clamp((T - tt) / .5); a = int(255 * (1 - clamp((T - tt) / .5)))
            ov = blank(); ImageDraw.Draw(ov).ellipse((fx - r_, fy - r_, fx + r_, fy + r_), outline=(255, 255, 255, a), width=8); c.alpha_composite(ov)
        ImageDraw.Draw(c).ellipse((fx - 38, fy - 38, fx + 38, fy + 38), fill=(255, 255, 255, 230), outline=OL, width=5)

def sc_final(T):
    s0, e0 = R.TL["G21"]; ta, tb = WT("G21", "A:"), WT("G21", "B:")
    hiA, hiB = ta <= T < tb, tb <= T < e0
    if T >= e0: hiA = int((T - e0) / .5) % 2 == 0; hiB = not hiA
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
        gl = blank(); ImageDraw.Draw(gl).line(RAYO, fill=CYAN + (int(255 * v),), width=40, joint="curve")
        c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(c)
        d.line(RAYO, fill=WHITE, width=12, joint="curve"); d.line(RAYO, fill=CYAN, width=5, joint="curve")
    for cx, L_, t1, t2, t3, col, t0, h in ((270, "A", "CARRERA", "+ El coche puede ser tuyo", "- Nitro no pierde nunca", AZ, ta, hiA),
                                           (790, "B", "DEPÓSITO", "+ Sabrás qué hay dentro", "- Sin tiempo para preparar", MAG, tb, hiB)):
        k = popscale(T, t0, .35)
        if k > 0: R._texto_opcion(d, cx, 420, L_, t1, t2, t3, col, k, 1.08 if h else 1.0)
    if T >= S("G22"): boton_seguir(c, T, WT("G22", "sígueme,"))
    return c

R.SCENES = [
    (0, sc_intro), (S("G02") - .15, sc_grito), (S("G03") - .15, sc_camina), (S("G04") - .15, sc_nitro1),
    (S("G05") - .15, sc_pregunta), (S("G06") - .2, sc_flash), (S("G08") - .15, sc_acerca), (S("G09") - .15, sc_lona),
    (S("G10") - .2, sc_seat), (S("G11") - .15, sc_lucia), (S("G12") - .15, sc_punos), (S("G13") - .2, sc_foto),
    (S("G14") - .15, sc_manolo_foto), (S("G15") - .15, sc_nitro_manolo), (S("G16") - .15, sc_tension),
    (S("G17") - .15, sc_carrera), (S("G18") - .2, sc_puerto), (S("G19") - .15, sc_se_va), (S("G20") - .15, sc_aviso),
    (S("G21") - .25, sc_final),
]
R.IMPACTS = [.2, WT("G02", "aquí!"), WT("G03", "ciegan."), WT("G03", "ruge"), WT("G05", "robó"), WT("G06", "único."),
             WT("G07", "desapareció"), WT("G08", "rencor."), WT("G10", "luces."), WT("G12", "puños."), WT("G13", "fecha"),
             WT("G14", "antes"), WT("G16", "cuchillo."), WT("G17", "carrera."), WT("G18", "dentro."),
             WT("G19", "Petardea"), WT("G20", "nunca."), S("G21")]
C.AVISOS[:] = [S("G09") - .2, S("G15") - .3]   # a mitad y antes del clímax
R.draw_hud = draw_hud
R.HIDE_LAST_CAPTION = False

def lecho(nombre, src, dur, fade=.4, loop=False):
    """Recorta (o alarga) un SFX a 'dur' segundos con fundido final, para camas de motor continuas.
    loop=True: solapa copias con ventana de Hann (sin clics ni cortes) para un ralentí continuo."""
    import numpy as np, wave
    out = os.path.join(R.HERE, "sfx", nombre + ".wav"); sr = 44100
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(R.HERE, "sfx", src + ".wav"), "-ac", "2", "-ar", str(sr),
                          "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32).reshape(-1, 2) / 32768
    n = int(dur * sr)
    if loop:   # el clip ya es un bucle perfecto: se repite tal cual
        y = np.tile(x, (n // len(x) + 1, 1))[:n]
    else:
        y = np.zeros((n, 2), np.float32); m = min(n, len(x)); y[:m] = x[:m]
    f = int(fade * sr); y[-f:] *= np.linspace(1, 0, f)[:, None]
    w = wave.open(out, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    return out

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "still":
        for t in sys.argv[2:]: R.frame(float(t)).save(os.path.join(R.TMP, f"e4_{float(t):06.2f}.jpg"), quality=88)
    elif cmd == "info":
        print({k: [round(a, 2), round(b, 2)] for k, (a, b) in R.TL.items()}, round(R.TOTAL, 2))
        print([round(t, 2) for t, f in R.SCENES])
    elif cmd == "scenes":
        from multiprocessing import Pool
        ids = [int(x) for x in sys.argv[2:]] or list(range(len(R.SCENES)))
        with Pool(max(2, os.cpu_count() - 0)) as pool:
            pool.starmap(R.render_scene, [(i, os.path.join(R.TMP, f"e4s{i:02d}.mp4")) for i in ids])
    elif cmd == "mix":
        import mix
        F = lambda n: os.path.join(R.HERE, "sfx", n + ".wav")
        t_sales = WT("G01", "Sales") - .2; t_ruge = WT("G03", "ruge")
        cama_nitro = lecho("e4_cama_nitro", "v8_ralenti", t_ruge - .3 - t_sales, .4, loop=True)
        t_seat0 = S("G10") - .3; t_seat1 = WT("G16", "acelera") - .1
        cama_seat = lecho("e4_cama_seat", "seat_ralenti2", t_seat1 - t_seat0 + .2, .2, loop=True)
        t_seat2 = WT("G16", "acelera") + 1.2; t_seat3 = S("G21") - .3
        cama_seat2 = lecho("e4_cama_seat2", "seat_ralenti2", t_seat3 - t_seat2, .6, loop=True)
        efectos = [
            (F("impacto"), .25, -3), (F("brillo"), .4, -6),                      # ¡ELEGISTEIS LA B!
            (cama_nitro, t_sales, 5),                                           # coche de Nitro encendido mientras caminas
            (F("impacto"), WT("G02", "aquí!") - .1, -6),
            (F("brillo"), WT("G03", "ciegan.") - .1, -2),                        # destello de los faros
            (F("v8_apaga"), t_ruge - .6, 7),                               # ruge una vez y se apaga
            (F("impacto"), WT("G04", "Vaya,") - .1, -8),
            (F("impacto"), WT("G05", "robó") - .1, -5),
            (F("brillo"), S("G06") + .05, -3), (F("brillo"), S("G06") + .95, -5), # flashes de foto del podio
            (F("impacto"), WT("G06", "único.") - .1, -5),
            (F("se_aleja"), WT("G07", "desapareció"), -2),                       # Rubén se lo lleva de noche
            (F("impacto"), WT("G07", "escondido") - .1, -4),
            (F("impacto"), WT("G08", "rencor.") - .1, -5),
            (F("brillo"), WT("G09", "barrio,") - .2, -5),
            (cama_seat, t_seat0, 4),                                            # Seat al ralentí, sin parar
            (F("seat_acelera"), WT("G11", "caliento") - .15, 3),
            (F("impacto"), WT("G12", "puños.") - .1, -6),
            (F("caja"), WT("G13", "foto") - .3, -6),                             # papel saliendo del bolsillo
            (F("brillo"), WT("G13", "fecha") - .1, -3),
            (F("impacto"), WT("G14", "antes") - .1, -6),
            (F("impacto"), WT("G15", "secretos") - .1, -7),
            (F("seat_acelera"), WT("G16", "acelera") - .1, 3),                    # Lucía acelera en vacío
            (F("impacto"), WT("G16", "cuchillo.") - .1, -3),
            (cama_seat2, t_seat2, 2),
            (F("impacto"), WT("G17", "carrera.") - .1, -3),
            (F("impacto"), WT("G18", "ganas,") - .1, -8), (F("impacto"), WT("G18", "yo…") - .1, -8),
            (F("impacto"), WT("G18", "dentro.") - .15, -4),
            (F("nitro_arranca"), WT("G19", "negro.") - .3, 5),                        # Nitro arranca
            (F("petardeo"), WT("G19", "Petardea") + .05, 3),
            (F("nitro_se_va"), WT("G19", "desaparece") - .45, 4),               # se pierde en la noche
            (F("impacto"), WT("G20", "nunca.") - .1, -5),
            (F("impacto"), S("G21") - .3, -5),
            (F("brillo"), WT("G22", "sígueme,") + .3, -3),
        ]
        mix.main(os.path.join(R.HERE, "el_taller_de_ruben_ep4.mp4"), "e4s", efectos)
