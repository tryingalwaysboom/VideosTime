"""Ep.10 CORTO "Cara a cara" (~50 s, viral): gancho frame 0, golpe visual cada 3-4 s, cierre ENTRAR / ESCUCHAR.
Uso: python3 ep8L.py still 10 20 | scenes [i..] | mix | info"""
import os, sys, math, subprocess
os.environ["GUION"] = "guion10"; os.environ["VOZDIR"] = "voz10"
import render as R
from luces import coche_faros
from render import (Image, ImageDraw, ImageFilter, W, H, bg, put, scaled, text, panel, stamp, etiqueta, dust,
                    neon_flicker, mouth, dark, ease, clamp, popscale, euros, S, E, WT, YEL, RED, WHITE, OL,
                    CYAN, MAG, GRIS, F_UI, F_ANTON, F_HAND)
import persp as P
import ep_comun as C
from ep_comun import linterna, humo, llamas, tinte, confeti, barra_voto, ep_chispas, AZ

R.GAP.update({"G01": 0, "G02": .05, "G03": .06, "G04": .08, "G05": .08, "G06": .08, "G07": .05, "G08": .08, "G09": .08, "G10": .06, "G11": .05, "G12": .06, "G13": .12, "G14": .12, "G15": .1, "G16": .3})
R.TL, R.TOTAL = R.timeline()
R.TL = {k: (a - .1, b - .1) for k, (a, b) in R.TL.items()}; R.TOTAL = R.TL['G16'][1] + .25
R.CH = R.chunks()
R.EPISODIO, R.DIA = 10, 0
G_ = (46, 160, 90)
SEPIA = (112, 78, 40)
G_ = (46, 160, 90)
SEPIA = (112, 78, 40)

def talk(lid, T): return S(lid) <= T < E(lid)
def blank(): return Image.new("RGBA", (W, H), (0, 0, 0, 0))

# ---------------------------------------------------------------- barra superior
def draw_hud(canvas, T):
    if T >= WT("G13", "Leer") - .1: return
    canvas.alpha_composite(R.barra_base())
    d = ImageDraw.Draw(canvas); x0, y0, x1 = 36, 168, 1044
    t_car = WT("G06", "ruge")
    def pop(t): return 1 + .28 * math.sin(clamp((T - t) / .3) * math.pi) if 0 <= T - t < .3 else 1
    for k, v, x in (("coch", "2", x0 + 300), ("caja", euros(1010), x0 + 420), ("deuda", "-" + euros(64300), x0 + 600), ("rep", "1", x0 + 880)):
        cy = y0 + 34
        if k == "coch": R.carito(d, x, cy, CYAN)
        if k == "caja": R.coin(d, x, cy, 15)
        if k == "deuda": R.flecha(d, x, cy, 1.0)
        if k == "rep": R.estrella(d, x, cy, 17, (242, 190, 60))
        d.text((x + 24, y0 + 35), v, font=R.font(F_ANTON, 34), fill=(255, 120, 110) if k == "deuda" else WHITE, anchor="lm")
    obj = "Escuchar a Manolo" if T < t_car else "Seguir a Nitro"
    d.text((x0 + 132, y0 + 87), obj, font=R.font(F_UI, 24 * pop(t_car)), fill=(255, 140, 120) if T >= t_car else WHITE, anchor="lm")
    d.text((x1 - 20, y0 + 87), "REPUTACIÓN", font=R.font(F_UI, 18), fill=GRIS, anchor="rm")
    aviso6(canvas, T)

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
        im = base.copy(); pd = ImageDraw.Draw(im)
        col = base.getpixel((120, 1290))
        pd.rectangle((100, 1100, 1100, 1300), fill=col)
        pd.text((600, 1200), "Rubén y Nitro · 1996", font=R.font(F_HAND, 118), fill=(40, 40, 110), anchor="mm")
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
# ---------------------------------------------------------------- piezas nuevas
def nave(T, t0, dur=4, fx=.5, fy=.55, z0=1.0, z1=1.08, osc=110):
    c = bg("bg_nave7", T, t0, z0, z1, dur, fx, fy); dark(c, osc); return c

def zoom(T, t0, dur, a=1.0, b=1.25): return a + (b - a) * ease(clamp((T - t0) / dur))

def cuaderno(c, cx, cy, s=1.0, rot=-4, pagina=0, T=0):
    """Cuaderno de Rubén dibujado: tapa de cuero con goma elástica y página con anotaciones."""
    lay = Image.new("RGBA", (760, 960), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((20, 20, 740, 940), 30, fill=(58, 36, 26), outline=OL, width=8)
    if pagina == 0:
        d.rounded_rectangle((60, 60, 700, 900), 18, fill=(92, 58, 40)); d.rectangle((590, 20, 650, 940), fill=(150, 30, 40))
        text(d, (330, 330), "RUBÉN", 120, (235, 205, 150), stroke=6); text(d, (330, 470), "1996", 90, (235, 205, 150), stroke=5)
    else:
        d.rounded_rectangle((50, 50, 710, 910), 14, fill=(240, 228, 196), outline=OL, width=5)
        for i in range(9): d.line((90, 170 + i * 80, 670, 170 + i * 80), fill=(150, 160, 190), width=3)
        d.line((140, 60, 140, 900), fill=(200, 80, 80), width=3)
        text(d, (390, 150), "SÁBADO", 110, (170, 30, 40), stroke=0)
        d.ellipse((120, 80, 660, 230), outline=(190, 30, 40), width=9)
        text(d, (390, 400), "PUERTO · 00:00", 56, (40, 40, 70), stroke=0); text(d, (390, 480), "LA LLAVE NO", 56, (40, 40, 70), stroke=0)
        text(d, (390, 560), "DEBE SALIR", 56, (40, 40, 70), stroke=0)
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    lay = lay.resize((int(lay.width * s), int(lay.height * s)), Image.LANCZOS)
    c.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def sombra_cabina(c, T, x, y, s=1.0):
    """Silueta de Nitro y sus faros (sólo se ven los faros) al otro lado de la ventana."""
    put(c, "faros", x, y, s)

# ---------------------------------------------------------------- escenas (cada una = 1 plano de 2-3 s)
def sh_resultado(T, t0, dur):
    c = poligono(T, 0, 1.2, 1.3, 4, 120)
    glow(c, (-120, 520, 760, 1180), MAG, 90, 80); glow(c, (420, 700, 1200, 1300), AZ, 60, 80)
    d = ImageDraw.Draw(c)
    text(d, (540, 430), "RESULTADO PARTE 4", 70, YEL, stroke=8)
    barra_voto(c, T, 640, "A", "ACEPTAR LA CARRERA", 28, AZ, False, 0)
    barra_voto(c, T, 830, "B", "ABRIR EL DEPÓSITO", 72, MAG, True, 0)
    R.estrella(ImageDraw.Draw(c), 960, 750, 30 * (1 + .15 * math.sin(T * 8)), (242, 190, 60))
    stamp(c, T, -1, "¡ELEGISTEIS LA B!", 540, 1080, YEL, -6, 116)
    confeti(c, T, .3)
    return c

def sh_flash(T, t0, dur):
    c = fondo_taller(T, t0, 200)
    rayos(c, T, 540, 1000, (255, 225, 150), 85, 14, 1700); glow(c, (60, 700, 1020, 1380), (255, 210, 120), 130, 80)
    tubo(c, 540, 1000, 1.05, rot=-10 + 6 * math.sin(T * 14))
    c = shake(c, T, 6, 40); vineta(c, 150)
    stamp(c, T, 0, "64.300 € DE DEUDA", 540, 520, RED, -5, 96)
    return c

def pregunta(c, T, t):
    if T >= t: stamp(c, T, t, "¿POR QUÉ?", 540, 560, YEL, 5, 120)

def cuenta(c, T, t):
    """cuenta atrás de Nitro (10:00 bajando rápido)"""
    if T < t: return
    rem = max(0, 600 - (T - t) * 24); m, sg = int(rem // 60), int(rem % 60)
    pu = 1 + .06 * abs(math.sin(T * 9)); d = ImageDraw.Draw(c)
    d.rounded_rectangle((250, 660, 830, 860), 36, fill=(20, 8, 12), outline=RED, width=8)
    text(d, (540, 760), f"{m:02d}:{sg:02d}", int(130 * pu), RED, stroke=8)
    text(d, (540, 640), "NITRO LLEGA EN", 44, WHITE, stroke=5)

def sh_deportivo_noche(T, t0, dur):
    c = nave(T, t0, dur, .5, .75, 1.1, 1.2, 130)
    put(c, "deportivo", 540, 1250, .95)
    a = T * 1.6; linterna(c, 540 + 330 * math.sin(a), 1230, 300, 200)
    if T >= WT("G01", "noche"): stamp(c, T, WT("G01", "noche"), "ESTA MISMA NOCHE", 540, 520, RED, -5, 88)
    return c

def sh_final_tu(T, t0, dur):
    c = nave(T, t0, dur, .5, .3, 1.15, 1.25, 120)
    ov = blank(); od = ImageDraw.Draw(ov)
    for i, x in enumerate((220, 540, 860)): od.rounded_rectangle((x - 70, 1180, x + 70, 1500), 24, fill=(20, 18, 30, 255))
    c.alpha_composite(ov)
    if T >= WT("G01", "final"): etiqueta(c, T, WT("G01", "final"), "QUÉDATE HASTA EL FINAL", 540, 560, YEL, OL, 44)
    if T >= WT("G01", "decides"): stamp(c, T, WT("G01", "decides"), "TÚ DECIDES", 540, 760, MAG, 6, 104)
    put(c, "deportivo", 540, 1320, .85); linterna(c, 540, 1300, 320, 170)
    return c

def sh_baja(T, t0, dur):
    c = nave(T, t0, dur, .5, .2 + .5 * clamp((T - t0) / dur), 1.15, 1.3, 140)
    linterna(c, 540 + 160 * math.sin(T * 2.2), 1000, 340, 180)
    if T >= S("G02") + .3: etiqueta(c, T, S("G02") + .3, "LA NAVE · DE NOCHE", 540, 470, GRIS, OL, 42)
    return c

def sh_fondo(T, t0, dur):
    c = nave(T, t0, dur, .5, .8, 1.0, 1.15, 140)
    put(c, "lona", 540, 1180, .5 + .25 * ease(clamp((T - t0) / dur)))
    linterna(c, 540, 1150, 330, 170)
    if T >= WT("G02", "fondo"): etiqueta(c, T, WT("G02", "fondo"), "AL FONDO", 540, 470, YEL, OL, 44)
    return c

def sh_manolo(lid, x=540, y=1380, s=1.15, tin=None, txt=None, tw=None, col=RED):
    def f(T, t0, dur):
        c = nave(T, t0, dur, .5, .5, 1.1, 1.18, 125)
        if tin: tinte(c, tin, 45)
        manolo(c, T, x + 5 * math.sin(T * 40) * (1 if tin else 0), y, s * zoom(T, t0, dur, 1.0, 1.06), lid)
        if txt and T >= WT(lid, tw): stamp(c, T, WT(lid, tw), txt, 540, 620, col, -5, 92)
        return c
    return f

def sh_lucia(lid, x=540, y=1330, s=1.0, txt=None, tw=None):
    def f(T, t0, dur):
        c = nave(T, t0, dur, .5, .45, 1.1, 1.18, 125)
        lucia(c, T, x, y, s * zoom(T, t0, dur, 1.0, 1.06), lid)
        if txt and T >= WT(lid, tw): stamp(c, T, WT(lid, tw), txt, 540, 600, YEL, -5, 92)
        return c
    return f

def sh_candado(T, t0, dur):
    c = nave(T, t0, dur, .5, .5, 1.2, 1.3, 140)
    put(c, "puerta7", 540, 1180, .8 * zoom(T, t0, dur, 1.0, 1.35))
    sh = 8 * math.sin(T * 60) if T >= S("G04") + .9 else 0
    put(c, "llaves", 780 + sh, 1500, .2)
    stamp(c, T, S("G04") + .2, "SELLADO POR RUBÉN", 540, 520, RED, -5, 74)
    return c

def sh_cruje(T, t0, dur):
    c = nave(T, t0, dur, .5, .8, 1.1, 1.2, 135)
    put(c, "deportivo", 540 + 6 * math.sin(T * 50), 1280, 1.0)
    humo(c, T, t0, 700, 1400, 1.6, 8); linterna(c, 700, 1380, 260, 180)
    if T >= WT("G04", "cruje"): stamp(c, T, WT("G04", "cruje"), "¡CRUUUJE!", 540, 560, YEL, 6, 108)
    return c

def sh_tela(T, t0, dur):
    c = nave(T, t0, dur, .5, .75, 1.1, 1.2, 140)
    put(c, "lona", 540, 1250, .55 + .1 * ease(clamp((T - t0) / dur))); linterna(c, 540, 1230, 340, 170)
    if T >= WT("G05", "tela"): etiqueta(c, T, WT("G05", "tela"), "UNA TELA VIEJA", 540, 520, GRIS, OL, 44)
    return c

def sh_caja(T, t0, dur):
    c = nave(T, t0, dur, .5, .75, 1.15, 1.25, 150)
    glow(c, (160, 960, 920, 1560), (255, 200, 90), 90, 70)
    k = popscale(T, t0, .35)
    put(c, "caja", 540, 1250, .62 * max(k, .05) * (1 + .03 * math.sin(T * 7))); linterna(c, 540, 1240, 330, 160)
    if T >= WT("G05", "caja"): stamp(c, T, WT("G05", "caja"), "UNA CAJA METÁLICA", 540, 540, YEL, -5, 78)
    return c

def sh_cuaderno(T, t0, dur):
    c = nave(T, t0, dur, .5, .6, 1.15, 1.25, 150); glow(c, (140, 760, 940, 1500), (255, 220, 140), 70, 70)
    cuaderno(c, 540, 1150, .85 * zoom(T, t0, dur, 1.0, 1.12), rot=-4 + 2 * math.sin(T * 2), pagina=0)
    if T >= WT("G07", "cuaderno"): etiqueta(c, T, WT("G07", "cuaderno"), "EL CUADERNO DE RUBÉN", 540, 470, YEL, OL, 42)
    return c

def sh_llave(T, t0, dur):
    c = nave(T, t0, dur, .5, .5, 1.2, 1.3, 150)
    glow(c, (60, 820, 1020, 1400), (255, 210, 90), 100 + 30 * math.sin(T * 6), 70)
    put_llave(c, 540, 1130, 1.1 * zoom(T, t0, dur, .8, 1.05), rot=-8 + 4 * math.sin(T * 3))
    if T >= WT("G07", "llave"): etiqueta(c, T, WT("G07", "llave"), "UNA LLAVE", 540, 470, WHITE, OL, 44)
    if T >= WT("G07", "siete"): stamp(c, T, WT("G07", "siete"), "NAVE 7", 540, 640, RED, -6, 120)
    return c

def sh_foto96(T, t0, dur):
    c = nave(T, t0, dur, .5, .5, 1.2, 1.3, 145); tinte(c, SEPIA, 70)
    put_img(c, foto(False), 540, 1130, .85 * zoom(T, t0, dur, .9, 1.05), rot=-3)
    c = sepia(c, .5)
    if T >= WT("G09", "Nitro"): etiqueta(c, T, WT("G09", "Nitro"), "LO QUE NITRO BUSCA", 540, 470, YEL, OL, 42)
    if T >= WT("G09", "30"): stamp(c, T, WT("G09", "30"), "30 AÑOS", 540, 700, RED, -5, 112)
    return c

def sh_pagina(T, t0, dur):
    c = nave(T, t0, dur, .5, .6, 1.15, 1.25, 150)
    cuaderno(c, 540, 1130, .85, rot=0, pagina=1, T=T)
    if T >= S("G10") + .2: etiqueta(c, T, S("G10") + .2, "LA ÚLTIMA PÁGINA", 540, 470, GRIS, OL, 42)
    return c

def sh_fecha(T, t0, dur):
    c = poligono(T, t0, 1.2, 1.3, 4, 130)
    cal = blank(); cd = ImageDraw.Draw(cal)
    cd.rounded_rectangle((200, 700, 880, 1300), 40, fill=(245, 245, 250), outline=OL, width=8); cd.rounded_rectangle((200, 700, 880, 850), 40, fill=RED, outline=OL, width=8)
    text(cd, (540, 775), "SÁBADO", 100, WHITE, stroke=6); text(cd, (540, 1060), "00:00", 190, OL, stroke=0)
    k = popscale(T, WT("G10", "sábado"), .35)
    if k > 0: SV_zoom(c, cal, k)
    if T >= WT("G10", "fecha"): stamp(c, T, WT("G10", "fecha"), "UNA FECHA", 540, 520, YEL, -5, 100)
    return c

def SV_zoom(c, lay, k):
    big = lay.resize((int(W * k), int(H * k)), Image.BILINEAR)
    c.alpha_composite(big, (int(540 - 540 * k), int(960 - 960 * k)), (max(0, int(540 * k - 540)), max(0, int(960 * k - 960))))

def sh_carrera(T, t0, dur):
    c = bg_puerto(T, t0, 1.0, 1.08, 4)
    put(c, "deportivo", 300, 1250, .52); coche_faros(c, 790, 1190, .52, .7, largo=260)
    bandera(ImageDraw.Draw(c), 540, 1060, 90, 60, T)
    stamp(c, T, WT("G10", "carrera"), "EL DÍA DE LA CARRERA", 540, 560, RED, -5, 80)
    return c

def sh_faros_fuera(T, t0, dur):
    c = nave(T, t0, dur, .5, .35, 1.1, 1.25, 150)
    glow(c, (0, 560, 1080, 1560), (255, 245, 210), 110 + 40 * math.sin(T * 9), 90)
    put(c, "persiana", 540, 900, 1.3)
    ov = blank(); od = ImageDraw.Draw(ov)
    for i in range(7): od.rectangle((0, 520 + i * 90, W, 540 + i * 90), fill=(255, 245, 210, 150))
    c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(10)))
    if T >= WT("G12", "faros"): stamp(c, T, WT("G12", "faros"), "FAROS FUERA", 540, 420, YEL, -5, 96)
    cuenta(c, T, WT("G12", "diez") - .1)
    return c

def sh_el(T, t0, dur):
    c = nave(T, t0, dur, .5, .5, 1.1, 1.2, 160); tinte(c, (90, 0, 20), 50)
    rev = 4 * math.sin(T * 60)
    coche_faros(c, 600, 1250, .75, 1.0, rev=rev); suelo_niebla(c)
    if T >= WT("G12", "Nitro"): stamp(c, T, WT("G12", "Nitro"), "ES NITRO", 540, 560, RED, -6, 130)
    cuenta(c, T, WT("G12", "diez") - .1)
    return c

def sh_llave_peligro(T, t0, dur):
    c = nave(T, t0, dur, .5, .5, 1.2, 1.3, 150)
    pulse = .5 + .5 * math.sin(T * 9)
    glow(c, (60, 760, 1020, 1480), RED, 80 + 60 * pulse, 70)
    put(c, "llave_nave7", 540, 1130, .85, rot=-8)
    if T >= WT("G12", "llave"): stamp(c, T, WT("G12", "llave"), "VIENE A POR LA LLAVE", 540, 560, RED, -5, 70)
    return c

def sh_caminos(T, t0, dur):
    c = nave(T, t0, dur, .5, .5, 1.2, 1.3, 150)
    bolsa(c, 540, 1150, .6, abierta=True)
    d = ImageDraw.Draw(c)
    text(d, (180, 1150), "A", 140, AZ, stroke=9); text(d, (900, 1150), "B", 140, MAG, stroke=9)
    d.polygon([(260, 1150), (330, 1100), (330, 1200)], fill=WHITE); d.polygon([(820, 1150), (750, 1100), (750, 1200)], fill=WHITE)
    stamp(c, T, WT("G13", "dos"), "DOS CAMINOS", 540, 540, YEL, -5, 104)
    return c

def lado(name):
    key = "L" + name
    if key in _LC: return _LC[key]
    if name == "A":   # escuchar a Manolo
        A = bg("bg_nave7", 0, 0, 1.15, 1.15, 1, .5, .7).convert("RGBA"); dark(A, 110)
        glow(A, (0, 900, 1000, 1600), AZ, 90, 80)
        put(A, "manolo", 300, 1400, .95)
    else:             # perseguir a Nitro
        A = bg("bg_nave7", 0, 0, 1.3, 1.3, 1, .5, .8).convert("RGBA"); dark(A, 130)
        coche_faros(A, 790, 1400, .9, .8, largo=330)
        A.alpha_composite(Image.new("RGBA", (W, H), (60, 10, 50, 60)))
    _LC[key] = A
    return A

def sh_lado(name, lid, pal):
    def f(T, t0, dur):
        c = lado(name).copy(); d = ImageDraw.Draw(c)
        col, t1, t2 = (AZ, "A", "LE DAS SU MITAD") if name == "A" else (MAG, "B", "TE QUEDAS CON TODO")
        k = popscale(T, t0, .35)
        text(d, (540, 520), t1, 220 * max(k, .05), col, stroke=12)
        text(d, (540, 700), t2, 70, WHITE, stroke=7)
        return c
    return f

def tapon_img(T=0):
    lay = Image.new("RGBA", (600, 600), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse((40, 40, 560, 560), fill=(70, 70, 80), outline=OL, width=10); d.ellipse((120, 120, 480, 480), fill=(110, 110, 124), outline=OL, width=8)
    d.rectangle((270, 150, 330, 450), fill=(60, 60, 70)); d.rectangle((150, 270, 450, 330), fill=(60, 60, 70))
    return lay

def bolsa(c, cx, cy, s=1.0, abierta=False, rot=0):
    lay = Image.new("RGBA", (700, 700), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((90, 190, 610, 640), 70, fill=(112, 100, 60), outline=OL, width=10)
    d.rounded_rectangle((140, 240, 560, 590), 50, fill=(132, 120, 76))
    if abierta:
        for i, x in enumerate((170, 260, 350, 440)):
            d.rounded_rectangle((x, 90 + (i % 2) * 30, x + 130, 230 + (i % 2) * 30), 10, fill=(150, 200, 150), outline=OL, width=6)
            text(d, (x + 65, 160 + (i % 2) * 30), "1996", 34, (30, 80, 40), stroke=0)
    d.rectangle((90, 190, 610, 230), fill=(80, 70, 40), outline=OL, width=8)
    text(d, (350, 430), "R.+ I.", 110, (240, 220, 150), stroke=6)
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC); lay = lay.resize((int(lay.width * s), int(lay.height * s)), Image.LANCZOS)
    c.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def tubo(c, cx, cy, s=1.0, rot=-8, abierto=False):
    lay = Image.new("RGBA", (900, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((40, 110, 860, 310), 80, fill=(150, 156, 170), outline=OL, width=10)
    d.rounded_rectangle((60, 130, 840, 190), 40, fill=(200, 206, 220))
    d.rounded_rectangle((690 + (60 if abierto else 0), 90, 810 + (60 if abierto else 0), 330), 28, fill=(185, 40, 40), outline=OL, width=8)
    d.line((300, 110, 300, 310), fill=OL, width=8); d.line((520, 110, 520, 310), fill=OL, width=8)
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC); lay = lay.resize((int(lay.width * s), int(lay.height * s)), Image.LANCZOS)
    c.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def sh_acerca(T, t0, dur):
    c = nave(T, t0, dur, .5, .75, 1.1, 1.25, 135)
    put(c, "deportivo", 540, 1250, .8 + .3 * ease(clamp((T - t0) / dur))); linterna(c, 540, 1230, 340, 190)
    if T >= WT("G02", "deportivo"): etiqueta(c, T, WT("G02", "deportivo"), "EL DEPORTIVO", 540, 470, YEL, OL, 46)
    return c

def sh_bolsa(T, t0, dur):
    c = nave(T, t0, dur, .5, .6, 1.2, 1.3, 150); glow(c, (60, 780, 1020, 1500), (255, 220, 120), 100, 70)
    bolsa(c, 540, 1150, 1.1 * zoom(T, t0, dur, .9, 1.1), abierta=True, rot=-4)
    f = clamp(1 - (T - t0) / .3)
    if f > 0: c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(235 * f))))
    if T >= WT("G07", "bolsa"): etiqueta(c, T, WT("G07", "bolsa"), "UNA BOLSA DE LONA", 540, 470, WHITE, OL, 44)
    return c

def sh_billetes(T, t0, dur):
    c = poligono(T, t0, 1.2, 1.3, 4, 130)
    d = ImageDraw.Draw(c)
    for i in range(14):
        ph = (T * .6 + i * .31) % 1.0; x = (i * 137) % 900 + 90; y = 300 + ph * 1500
        d.rounded_rectangle((x - 60, y - 34, x + 60, y + 34), 8, fill=(150, 205, 150), outline=OL, width=5)
        text(d, (x, y), "1996", 30, (30, 80, 40), stroke=0)
    stamp(c, T, WT("G07", "billetes"), "BILLETES DE 1996", 540, 640, YEL, -5, 100)
    return c

def sh_trofeo(T, t0, dur):
    c = nave(T, t0, dur, .5, .5, 1.15, 1.25, 150); tinte(c, SEPIA, 60)
    put(c, "trofeo", 540, 1180, .8 * zoom(T, t0, dur, .9, 1.1))
    if T >= WT("G08", "premio"): etiqueta(c, T, WT("G08", "premio"), "EL PREMIO DEL RALLY", 540, 470, YEL, OL, 44)
    if T >= WT("G08", "esto"): stamp(c, T, WT("G08", "esto"), "ERA ESTO", 540, 700, RED, -5, 120)
    return c

def sh_nota(T, t0, dur):
    c = nave(T, t0, dur, .5, .6, 1.15, 1.25, 150)
    lay = Image.new("RGBA", (700, 900), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((20, 20, 680, 880), 14, fill=(240, 228, 196), outline=OL, width=6)
    text(d, (350, 160), "PARA EL CHAVAL", 60, (170, 30, 40), stroke=0)
    for i, t in enumerate(("La mitad es de Nitro.", "La otra mitad,", "para salvar", "el taller.")): text(d, (350, 360 + i * 110), t, 54, (40, 40, 70), stroke=0)
    text(d, (540, 800), "— Rubén", 46, (40, 40, 70), stroke=0)
    sc = .78 * zoom(T, t0, dur, .95, 1.05); lay = lay.rotate(-3, expand=True, resample=Image.BICUBIC)
    lay = lay.resize((int(lay.width * sc), int(lay.height * sc)), Image.LANCZOS)
    c.alpha_composite(lay, (int(540 - lay.width / 2), int(1000 - lay.height / 2)))
    if T >= WT("G09", "nota"): etiqueta(c, T, WT("G09", "nota"), "UNA NOTA CON TU NOMBRE", 540, 470, YEL, OL, 42)
    return c

def sh_mitad(T, t0, dur):
    c = nave(T, t0, dur, .5, .6, 1.2, 1.3, 150)
    d = ImageDraw.Draw(c)
    bolsa(c, 300, 1150, .75, abierta=True, rot=-6); bolsa(c, 780, 1150, .75, abierta=True, rot=6)
    d = ImageDraw.Draw(c); text(d, (300, 1500), "NITRO", 80, RED, stroke=7); text(d, (780, 1500), "EL TALLER", 70, AZ, stroke=7)
    if T >= WT("G10", "mitad"): stamp(c, T, WT("G10", "mitad"), "MITAD Y MITAD", 540, 560, YEL, -5, 100)
    return c

def sh_deuda(T, t0, dur):
    c = poligono(T, t0, 1.2, 1.3, 4, 130)
    d = ImageDraw.Draw(c)
    text(d, (540, 640), "DEUDA", 120, WHITE, stroke=8)
    k = popscale(T, WT("G11", "deuda"), .4)
    text(d, (540, 900), "0 €", 330 * max(k, .05), G_, stroke=12)
    if k > 0: stamp(c, T, WT("G11", "entera"), "¡PAGADA!", 540, 1250, YEL, -6, 120)
    return c

def sh_mitad_peligro(T, t0, dur):
    c = nave(T, t0, dur, .5, .5, 1.2, 1.3, 150)
    pulse = .5 + .5 * math.sin(T * 9); glow(c, (60, 760, 1020, 1480), RED, 80 + 60 * pulse, 70)
    bolsa(c, 540, 1150, .95, abierta=True, rot=-4)
    if T >= WT("G12", "mitad"): stamp(c, T, WT("G12", "mitad"), "VIENE A POR SU MITAD", 540, 560, RED, -5, 70)
    cuenta(c, T, WT("G12", "diez") - .1)
    return c


# ---------------- depósito: planos de detalle (v2)
def shake(c, T, amp=6, f=38):
    from PIL import ImageChops
    return ImageChops.offset(c, int(amp * math.sin(T * f)), int(amp * math.cos(T * f * 1.3)))

def vineta(c, a=190):
    v = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(v)
    for i in range(14):
        d.rectangle((i * 22, i * 40, W - i * 22, H - i * 40), outline=(0, 0, 0, int(a / 14)), width=60)
    c.alpha_composite(v.filter(ImageFilter.GaussianBlur(50)))

def polvo(c, T, n=34, y0=380, y1=1500, col=(255, 235, 190)):
    ov = blank(); d = ImageDraw.Draw(ov)
    for i in range(n):
        x = (i * 211 + 40 * math.sin(T * .8 + i)) % W; y = y0 + ((i * 97 + T * 60 * (.5 + (i % 5) * .2)) % (y1 - y0)); r = 3 + i % 4
        d.ellipse((x - r, y - r, x + r, y + r), fill=col + (110,))
    c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(1.5)))

def rayos(c, T, cx, cy, col=(255, 225, 150), a=70, n=12, L=1500):
    ov = blank(); d = ImageDraw.Draw(ov)
    for i in range(n):
        ang = T * .35 + i * (2 * math.pi / n); w = .09
        d.polygon([(cx, cy), (cx + L * math.cos(ang - w), cy + L * math.sin(ang - w)), (cx + L * math.cos(ang + w), cy + L * math.sin(ang + w))], fill=col + (a,))
    c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(18)))

def chispas(c, T, t0, cx, cy, n=26, v=900, col=(255, 210, 90)):
    if T < t0: return
    ov = blank(); d = ImageDraw.Draw(ov); k = T - t0
    for i in range(n):
        ang = i * 2.399; sp = v * (.4 + (i % 5) * .18)
        x = cx + sp * k * math.cos(ang); y = cy + sp * k * math.sin(ang) + 900 * k * k; a = int(255 * max(0, 1 - k / .9))
        if a > 0: d.line((x, y, x - 22 * math.cos(ang), y - 22 * math.sin(ang)), fill=col + (a,), width=6)
    c.alpha_composite(ov)

def guante(c, cx, cy, s=1.0, rot=0, cerrado=False):
    lay = Image.new("RGBA", (520, 700), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((120, 380, 400, 700), 40, fill=(60, 90, 160), outline=OL, width=8)     # manga
    d.rounded_rectangle((110, 220, 410, 440), 70, fill=(236, 186, 140), outline=OL, width=8)       # palma
    for i, x in enumerate((120, 190, 262, 334)):
        h = (250 if not cerrado else 130) + (30 if i in (1, 2) else 0)
        d.rounded_rectangle((x, 220 - h + 60, x + 62, 300), 30, fill=(236, 186, 140), outline=OL, width=7)
    d.rounded_rectangle((60, 300, 150, 380), 34, fill=(236, 186, 140), outline=OL, width=7)
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC); lay = lay.resize((int(lay.width * s), int(lay.height * s)), Image.LANCZOS)
    c.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def fondo_taller(T, t0, a=175, z0=1.2, z1=1.35, fy=.8):
    c = nave(T, t0, 4, .5, fy, z0, z1, a); return c

def sh_sello(T, t0, dur):
    c = fondo_taller(T, t0, 185); k = clamp((T - t0) / dur); d = ImageDraw.Draw(c)
    z = 1 + .35 * ease(k); cx, cy = 540, 1060
    d.rounded_rectangle((cx - 400 * z, cy - 470 * z, cx + 400 * z, cy + 470 * z), 70, fill=(226, 228, 236), outline=OL, width=10)   # chapa del coche
    glow(c, (cx - 420 * z, cy - 520 * z, cx + 60 * z, cy - 120 * z), WHITE, 90, 80); d = ImageDraw.Draw(c)
    R_ = 250 * z; d.ellipse((cx - R_, cy - R_, cx + R_, cy + R_), fill=(176, 180, 192), outline=OL, width=10)
    d.ellipse((cx - R_ + 30, cy - R_ + 30, cx + R_ - 30, cy + R_ - 30), fill=(130, 134, 148), outline=OL, width=8)
    d.arc((cx - R_ + 70, cy - R_ + 70, cx + R_ - 70, cy + R_ - 70), 200, 340, fill=(220, 224, 236), width=14)
    tr = WT("G04", "sello") + .05
    d.rounded_rectangle((cx - 180 * z, cy - 70 * z, cx + 180 * z, cy + 70 * z), 24, fill=(180, 30, 36), outline=OL, width=8) if T < tr else None
    if T < tr:
        text(d, (cx, cy), "R.", int(100 * z), (255, 200, 200), stroke=5)
        d.line((cx - 330 * z, cy + 160 * z, cx + 330 * z, cy - 160 * z), fill=(255, 255, 255), width=0)
    else:
        kk = T - tr
        for i, sg in enumerate((-1, 1)):
            x = cx + sg * (90 * z + 700 * kk); y = cy + 1200 * kk * kk - 140 * kk * 100
            d.rounded_rectangle((x - 90, y - 60, x + 90, y + 60), 20, fill=(180, 30, 36), outline=OL, width=8)
        chispas(c, T, tr, cx, cy, 22, 700, (255, 120, 90))
    rayos(c, T, cx, cy, (255, 240, 200), 40, 8, 1300)
    c = shake(c, T, 3 + (12 if tr <= T < tr + .4 else 0)); vineta(c, 170)
    stamp(c, T, tr, "SELLO ROTO", 540, 460, RED, -5, 100)
    return c

def sh_tapon(T, t0, dur):
    c = fondo_taller(T, t0, 195); k = clamp((T - t0) / dur); d = ImageDraw.Draw(c)
    cx, cy = 540, 1000; R_ = 270
    out = clamp((T - (t0 + dur * .55)) / .35)
    glow(c, (cx - 520, cy - 520, cx + 520, cy + 520), (255, 220, 140), 70, 90); d = ImageDraw.Draw(c)
    cx2, cy2, R2 = cx + 140 * out, cy - 500 * out, R_ * (1 + .6 * out)
    d.ellipse((cx - R_ - 20, cy - R_ - 20, cx + R_ + 20, cy + R_ + 20), fill=(12, 12, 18), outline=OL, width=8)       # boca del depósito
    cap = Image.new("RGBA", (900, 900), (0, 0, 0, 0)); cd = ImageDraw.Draw(cap)
    cd.ellipse((50, 50, 850, 850), fill=(150, 154, 168), outline=OL, width=12)
    for i in range(40): a = i * math.pi / 20; cd.line((450 + 360 * math.cos(a), 450 + 360 * math.sin(a), 450 + 400 * math.cos(a), 450 + 400 * math.sin(a)), fill=OL, width=10)
    cd.ellipse((140, 140, 760, 760), fill=(196, 200, 214), outline=OL, width=8); cd.rectangle((380, 200, 520, 700), fill=(120, 124, 140)); cd.rectangle((200, 380, 700, 520), fill=(120, 124, 140))
    cap = cap.rotate(-720 * ease(clamp((T - t0) / (dur * .7))), resample=Image.BICUBIC)
    cap = cap.resize((int(900 * R2 / 400), int(900 * R2 / 400)), Image.LANCZOS)
    c.alpha_composite(cap, (int(cx2 - cap.width / 2), int(cy2 - cap.height / 2)))
    guante(c, 220 + 100 * math.sin(T * 14), 1450, .9, rot=-30, cerrado=True) if out < 1 else None
    chispas(c, T, t0 + dur * .5, cx, cy, 18, 600, (255, 230, 170))
    humo(c, T, t0 + dur * .5, cx, cy, 1.6, 8)
    c = shake(c, T, 5 + (10 if .4 < out < .8 else 0)); vineta(c, 180)
    if T >= WT("G04", "tapón"): etiqueta(c, T, WT("G04", "tapón"), "QUITAS EL TAPÓN", 540, 420, WHITE, OL, 48)
    return c

def sh_vacio(T, t0, dur):
    c = fondo_taller(T, t0, 210); d = ImageDraw.Draw(c)
    cx, cy = 540, 760
    for i in range(9):
        r = 400 - i * 40; col = 8 + i * 3; d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(col, col, col + 6), outline=(70 + i * 5, 74 + i * 5, 90 + i * 5), width=6)
    ang = math.sin(T * 1.6) * .5
    linterna(c, cx + 320 * ang, cy + 40, 260, 230); d = ImageDraw.Draw(c)
    # aguja de gasolina en E
    gx, gy = 540, 1330; d.pieslice((gx - 280, gy - 280, gx + 280, gy + 280), 180, 360, fill=(24, 24, 34), outline=WHITE, width=8)
    text(d, (gx - 210, gy - 40), "E", 56, RED, stroke=4); text(d, (gx + 210, gy - 40), "F", 56, WHITE, stroke=4)
    na = math.radians(180 + 4 + 5 * math.sin(T * 20)); d.line((gx, gy, gx + 230 * math.cos(na), gy + 230 * math.sin(na)), fill=RED, width=12)
    d.ellipse((gx - 18, gy - 18, gx + 18, gy + 18), fill=WHITE)
    text(d, (540, 1160), "0 L", 90, RED, stroke=8)
    polvo(c, T, 26, 400, 1200, (200, 200, 210)); c = shake(c, T, 2); vineta(c, 190)
    if T >= WT("G04", "gota"): stamp(c, T, WT("G04", "gota"), "NI UNA GOTA", 540, 480, RED, -5, 104)
    return c

def sh_mano(T, t0, dur):
    c = fondo_taller(T, t0, 215); d = ImageDraw.Draw(c); k = ease(clamp((T - t0) / dur))
    d.rounded_rectangle((90, 760, 990, 1480), 150, fill=(70, 78, 98), outline=OL, width=12)       # depósito en corte
    d.rounded_rectangle((130, 800, 950, 1440), 120, fill=(14, 14, 22), outline=(120, 130, 150), width=8)
    for x, y in ((140, 790), (940, 790), (140, 1450), (940, 1450), (540, 770)): d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=(190, 196, 210), outline=OL, width=4)
    tubo(c, 600, 1330, .72, rot=-4)                                      # el tubo yace dentro
    linterna(c, 560, 1180, 280, 230); d = ImageDraw.Draw(c)
    guante(c, 330 + 200 * k, 560 + 760 * k, 1.1, rot=-8 + 18 * k, cerrado=False)
    polvo(c, T, 30, 800, 1440); glow(c, (300, 1180, 900, 1440), (255, 230, 160), 60, 60)
    c = shake(c, T, 3); vineta(c, 175)
    if T >= WT("G05", "metálico"): etiqueta(c, T, WT("G05", "metálico"), "ALGO METÁLICO", 540, 420, YEL, OL, 48)
    return c

def sh_tubo(T, t0, dur):
    c = fondo_taller(T, t0, 200); k = popscale(T, t0, .4)
    rayos(c, T, 540, 1100, (255, 225, 150), 85, 14, 1700); glow(c, (60, 760, 1020, 1440), (255, 210, 120), 130, 80)
    tubo(c, 540, 1100, 1.15 * max(k, .05), rot=-10 + 4 * math.sin(T * 2.5))
    polvo(c, T, 40, 350, 1600); c = shake(c, T, 2, 30); vineta(c, 150)
    if T >= WT("G05", "tubo"): stamp(c, T, WT("G05", "tubo"), "TUBO ESTANCO", 540, 460, YEL, -5, 100)
    return c

def sh_pregunta(T, t0, dur):
    c = sh_vacio(T, t0, dur)
    pregunta(c, T, S("G15") + .2)
    return c

def sh_split(T, t0, dur):
    s0 = WT("G13", "Leer") - .1
    A, B = lado8("A"), lado8("B")
    u = ease((T - s0 + .25) / .45)
    tb = WT("G13", "volver") - .05; tn = S("G14") - .05
    hiA = T < tb
    neutro = T >= tn
    blk = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    c = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    c.alpha_composite(B if (neutro or not hiA) else Image.blend(B, blk, .45), (int(500 * (1 - u)), 0))
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon([(0, 0)] + RAYO + [(0, H)], fill=255)
    c.paste(A if (neutro or hiA) else Image.blend(A, blk, .45), (int(-700 * (1 - u)), 0), mask)
    d = ImageDraw.Draw(c)
    if u > .9:
        v = .6 + .4 * abs(math.sin(T * 13)) * abs(math.sin(T * 3.1))
        gl = blank(); ImageDraw.Draw(gl).line(RAYO, fill=CYAN + (int(255 * v),), width=40, joint="curve")
        c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(c)
        d.line(RAYO, fill=WHITE, width=12, joint="curve"); d.line(RAYO, fill=CYAN, width=5, joint="curve")
    for cx, L_, t1, t2, t3, col in ((270, "A", "LEER", "+ Descubres la firma", "- Nitro se escapa", AZ),
                                    (790, "B", "VOLVER", "+ Pillas al firmante", "- No lees la firma", MAG)):
        k = popscale(T, s0 + .2, .35)
        if k > 0: opcion8(d, cx, 420, t1, t2, t3, col, k)
    boton_seguir(c, T, WT("G14", "sígueme"))
    return c
RAYO = R.RAYO
_LC = {}
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

# ---------------------------------------------------------------- piezas del Ep.6
AV6 = []
def aviso6(c, T):
    for t0 in AV6:
        if not (t0 <= T < t0 + 5.0): continue
        u = ease((T - t0) / .35) if T < t0 + 4.6 else 1 - ease((T - t0 - 4.6) / .35)
        y = 300 + 20 * (1 - u); a = int(255 * u)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        w2 = 330 * (1 + .03 * math.sin((T - t0) * 8))
        d.rounded_rectangle((540 - w2, y, 540 + w2, y + 74), 37, fill=(255, 255, 255, a), outline=OL + (a,), width=5)
        d.ellipse((540 - w2 + 10, y + 9, 540 - w2 + 66, y + 65), fill=AZ + (a,)); d.text((540 - w2 + 38, y + 37), "A", font=R.font(F_ANTON, 38), fill=WHITE + (a,), anchor="mm")
        d.ellipse((540 + w2 - 66, y + 9, 540 + w2 - 10, y + 65), fill=MAG + (a,)); d.text((540 + w2 - 38, y + 37), "B", font=R.font(F_ANTON, 38), fill=WHITE + (a,), anchor="mm")
        d.text((540, y + 24), "¿TÚ QUÉ HARÍAS? VOTA EN LA ENCUESTA", font=R.font(F_ANTON, 27), fill=OL + (a,), anchor="mm")
        d.text((540, y + 54), "tu voto decide la parte 9", font=R.font(F_UI, 23), fill=(200, 50, 50, a), anchor="mm")
        c.alpha_composite(lay)

def cuenta6(c, T, t, box=(250, 430, 830, 630)):
    """cuenta atrás de 10 segundos (rápida, para tensión)"""
    if T < t: return
    rem = max(0.0, 10 - (T - t) * 2.2); pu = 1 + .06 * abs(math.sin(T * 9)); d = ImageDraw.Draw(c)
    x0, y0, x1, y1 = box; cx = (x0 + x1) // 2
    d.rounded_rectangle(box, 36, fill=(20, 8, 12), outline=RED, width=8)
    text(d, (cx, (y0 + y1) // 2), f"00:{int(rem):02d}", int(130 * pu), RED, stroke=8)
    text(d, (cx, y0 - 20), "TIEMPO PARA RESPONDER", 34, WHITE, stroke=5)

def corazon(d, cx, cy, s, col):
    d.ellipse((cx - s * .5, cy - s * .45, cx, cy + s * .05), fill=col); d.ellipse((cx, cy - s * .45, cx + s * .5, cy + s * .05), fill=col)
    d.polygon([(cx - s * .49, cy - s * .1), (cx + s * .49, cy - s * .1), (cx, cy + s * .5)], fill=col)

def calle_nitro(T, t0, dur, lid=None, tin=None, k0=0.0, car=True):
    """Estilo original (plano, sin perspectiva): polígono de noche, coche de Nitro de lado con faros y Nitro delante."""
    c = poligono(T, t0, 1.35, 1.42, 6, 100)
    if k0 >= .3:   # Nitro se acerca a contraluz de sus faros
        k = ease(clamp((T - t0) / max(dur, 1.0))) * .5 + k0 * .5
        coche_faros(c, 700, 1180, .7, .6, largo=500)
        glow(c, (240, 500, 840, 1500), (255, 240, 200), 70, 70)
        nitro(c, T, 540, 1000 + 120 * k, .8 + .4 * k, lid)
    else:
        if car: coche_faros(c, 740, 1200, .8, .55, largo=700)
        nitro(c, T, 400, 960, 1.0, lid)
    if tin: tinte(c, tin, 55)
    dark(c, 30)
    return c

# ------------------------------------------------------------ escenas
def put_llave(c, cx, cy, s=1.0, rot=0):
    """Llave vieja del cajón 7 (dibujada): aro, caña, dientes y etiqueta con el 7."""
    lay = Image.new("RGBA", (900, 360), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse((30, 90, 210, 270), fill=(196, 150, 60), outline=OL, width=10); d.ellipse((85, 145, 155, 215), fill=(0, 0, 0, 0), outline=OL, width=8)
    d.rounded_rectangle((200, 160, 800, 200), 16, fill=(196, 150, 60), outline=OL, width=9)
    d.rectangle((700, 200, 760, 270), fill=(196, 150, 60), outline=OL, width=8); d.rectangle((770, 200, 810, 250), fill=(196, 150, 60), outline=OL, width=8)
    d.rounded_rectangle((100, 250, 300, 340), 14, fill=(240, 228, 196), outline=OL, width=7); text(d, (200, 295), "7", 76, (150, 30, 40), stroke=0)
    d.line((120, 255, 120, 235), fill=OL, width=6)
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    lay = lay.resize((int(lay.width * s), int(lay.height * s)), Image.LANCZOS)
    c.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def sh_nitro(lid, txt=None, tw=None, tin=None, k0=0.0, y=470):
    def f(T, t0, dur):
        c = calle_nitro(T, t0, dur, lid, tin, k0)
        if txt and T >= WT(lid, tw): stamp(c, T, WT(lid, tw), txt, 640, y, RED, -5, 62)
        return c
    return f

def sh_flash7(T, t0, dur):
    c = nave(T, t0, dur, .5, .5, 1.2, 1.3, 150); tinte(c, SEPIA, 70)
    glow(c, (140, 760, 940, 1500), (255, 210, 90), 110, 70)
    put_llave(c, 540, 1130, 1.0, rot=-8 + 6 * math.sin(T * 16))
    c = shake(c, T, 6, 40); vineta(c, 160)
    stamp(c, T, 0, "¿QUÉ ABRE?", 540, 520, RED, -5, 110)
    return c

def sh_resultado7(T, t0, dur):
    c = poligono(T, 0, 1.2, 1.3, 4, 120)
    glow(c, (-120, 520, 760, 1180), AZ, 60, 80); glow(c, (420, 700, 1200, 1300), MAG, 90, 80)
    d = ImageDraw.Draw(c)
    text(d, (540, 430), "RESULTADO PARTE 6", 70, YEL, stroke=8)
    barra_voto(c, T, 640, "A", "CREERLE A NITRO", 13, AZ, False, 0)
    barra_voto(c, T, 830, "B", "DEFENDER A RUBÉN", 87, MAG, True, 0)
    R.estrella(ImageDraw.Draw(c), 960, 850, 30 * (1 + .15 * math.sin(T * 8)), (242, 190, 60))
    stamp(c, T, -1, "¡ELEGISTEIS LA B!", 540, 1080, YEL, -6, 116)
    confeti(c, T, .3)
    return c

def sh_suelta(T, t0, dur):
    c = nave(T, t0, dur, .5, .5, 1.2, 1.3, 145); tinte(c, SEPIA, 70)
    k = ease(clamp((T - WT("G01", "llave") + .1) / .35))
    put_llave(c, 540, 1250, .95 * max(k, .05), rot=-8 + 4 * math.sin(T * 3))
    put_img(c, foto(False), 540, 1000 + 40 * math.sin(T * 2), .9 * zoom(T, t0, dur, .9, 1.0), rot=-3)
    c = sepia(c, .5)
    if T >= WT("G01", "suelta"): etiqueta(c, T, WT("G01", "suelta"), "LA FOTO", 540, 440, YEL, OL, 44)
    if T >= WT("G01", "llave"): stamp(c, T, WT("G01", "llave"), "UNA LLAVE", 540, 720, RED, -5, 110)
    return c

def sh_se_va(T, t0, dur):
    c = poligono(T, t0, 1.35, 1.42, 6, 100)
    k = ease(clamp((T - WT("G04", "arranca") + .2) / 1.3))
    coche_faros(c, 700 + 900 * k, 1200, .8, .55, largo=700, rev=3 * math.sin(T * 60) * (1 - k))
    dark(c, 30)
    if T >= WT("G04", "arranca"): stamp(c, T, WT("G04", "arranca"), "SE VA", 540, 420, RED, -6, 120)
    return c

def sh_llave7(T, t0, dur):
    c = nave(T, t0, dur, .5, .5, 1.2, 1.3, 150)
    glow(c, (60, 820, 1020, 1400), (255, 210, 90), 100 + 30 * math.sin(T * 6), 70)
    put_llave(c, 540, 1130, 1.1 * zoom(T, t0, dur, .8, 1.05), rot=-8 + 4 * math.sin(T * 3))
    if T >= WT("G04", "llave"): etiqueta(c, T, WT("G04", "llave"), "TE QUEDAS SOLO", 540, 470, WHITE, OL, 44)
    return c

def papel(c, cx, cy, s=1.0, rot=0, firmas=2, resalta=False, T=0, final=False):
    """Contrato de 1996 con firmas a mano."""
    lay = Image.new("RGBA", (760, 960), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((20, 20, 740, 940), 18, fill=(240, 228, 196), outline=OL, width=8)
    text(d, (380, 110), "CONTRATO · 1996", 62, (50, 40, 40), stroke=0)
    for i in range(5): d.line((80, 190 + i * 46, 680, 190 + i * 46), fill=(150, 150, 150), width=4)
    text(d, (380, 450), "SOCIOS 50 / 50", 66, (150, 30, 40), stroke=0)
    for (x0, y0, nom) in ((60, 680, "RUBÉN"), (400, 680, "NITRO")):
        d.line((x0, y0, x0 + 300, y0), fill=(40, 40, 70), width=5)
        d.text((x0 + 150, y0 - 40), nom.capitalize(), font=R.font(F_HAND, 66), fill=(40, 40, 110), anchor="mm")
        d.text((x0 + 150, y0 + 30), nom, font=R.font(F_UI, 22), fill=(80, 80, 90), anchor="mm")
    if firmas >= 3:
        d.line((220, 850, 540, 850), fill=(40, 40, 70), width=5)
        d.text((380, 810), "Manolo" if final else "~~~~", font=R.font(F_HAND, 70), fill=(170, 30, 40) if final else (40, 40, 110), anchor="mm")
        d.text((380, 885), "TESTIGO", font=R.font(F_UI, 22), fill=(80, 80, 90), anchor="mm")
        if resalta:
            v = 160 + int(90 * abs(math.sin(T * 9)))
            d.rounded_rectangle((190, 760, 570, 910), 24, outline=(220, 40, 50, v), width=10)
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    lay = lay.resize((int(lay.width * s), int(lay.height * s)), Image.LANCZOS)
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * .55))); sh = sh.filter(ImageFilter.GaussianBlur(18))
    c.alpha_composite(sh, (int(cx - lay.width / 2) + 14, int(cy - lay.height / 2) + 26))
    c.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def llave_pivote(c, px, py, s, ang, sx=1.0):
    """Llave con la punta (izquierda) en (px,py); sx<1 la acorta (vista de frente al entrar); gira 'ang' grados sobre la punta."""
    L = Image.new("RGBA", (900, 360), (0, 0, 0, 0)); put_llave(L, 450, 180, 1.0, 0)
    L = L.transpose(Image.FLIP_LEFT_RIGHT)                       # aro a la derecha, punta a la izquierda (x≈90)
    if sx < 1: L = L.resize((max(int(900 * sx), 20), 360), Image.LANCZOS)
    tipx = int(90 * sx)
    big = Image.new("RGBA", (2000, 2000), (0, 0, 0, 0)); big.alpha_composite(L, (1000 - tipx, 1000 - 180))
    big = big.rotate(ang, resample=Image.BICUBIC, center=(1000, 1000))
    big = big.resize((int(2000 * s), int(2000 * s)), Image.LANCZOS)
    c.alpha_composite(big, (int(px - big.width / 2), int(py - big.height / 2)))

def sh_cajon(T, t0, dur):
    c = fondo_taller(T, t0, 150)
    tc = WT("G05", "contrato"); tg = WT("G05", "Giras")
    kx, ky = 540, 1180                                   # ojo de la cerradura
    out = ease(clamp((T - tc) / .55))                    # el cajón se desliza hacia ti
    glow(c, (60, 700, 1020, 1500), (255, 205, 120), 70 + 40 * out, 90)
    y = ky - 40 + 70 * out; sc = 1 + .18 * out
    lay = blank(); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((120, 880, 960, 1480), 34, fill=(40, 44, 54), outline=OL, width=10)                         # carcasa
    for i in range(24):                                                                                             # degradado metálico
        yy = 900 + i * 24; v = 104 - i * 2
        d.rectangle((140, yy, 940, yy + 24), fill=(v, v + 6, v + 18))
    d.rounded_rectangle((120, 880, 960, 1480), 34, outline=OL, width=10)
    d.rounded_rectangle((170, 940, 910, 1420), 22, outline=(24, 26, 34), width=8)
    for (rx, ry) in ((150, 910), (930, 910), (150, 1450), (930, 1450)): d.ellipse((rx - 12, ry - 12, rx + 12, ry + 12), fill=(150, 156, 170), outline=OL, width=4)
    d.rounded_rectangle((300, 990, 780, 1110), 18, fill=(220, 200, 150), outline=OL, width=7)                      # placa con el 7
    text(d, (540, 1050), "7", 120, (150, 30, 40), stroke=0)
    d.rounded_rectangle((380, 1300, 700, 1340), 20, fill=(70, 74, 86), outline=OL, width=6)                       # tirador
    d.ellipse((kx - 46, ky - 46, kx + 46, ky + 46), fill=(196, 150, 60), outline=OL, width=7)                      # escudo de la cerradura
    d.ellipse((kx - 14, ky - 22, kx + 14, ky + 6), fill=(10, 10, 14)); d.polygon([(kx - 8, ky), (kx + 8, ky), (kx + 14, ky + 30), (kx - 14, ky + 30)], fill=(10, 10, 14))
    lay = lay.resize((int(W * sc), int(H * sc)), Image.LANCZOS)
    c.alpha_composite(lay, (int(540 - 540 * sc), int(y - ky * sc - 20 * out)))
    if T < tc:
        ap = ease(clamp((T - S("G05") - .1) / (max(tg - S("G05"), 1.0) - .1)))        # la llave se acerca y entra
        gi = ease(clamp((T - tg) / .45))
        tx = kx + 560 * (1 - ap); ty = ky + 20 * (1 - ap)
        sx = 1 - .72 * ease(clamp((T - tg + .35) / .3))
        if ap > .02: llave_pivote(c, tx, ty, .9, -90 * gi, sx)
        if gi > .95 and T < tc: glow(c, (kx - 160, ky - 160, kx + 160, ky + 160), (255, 235, 150), 200, 40)
    if T >= tc:
        k = ease(clamp((T - tc - .15) / .55))
        glow(c, (60, 380, 1020, 1100), (255, 220, 140), 120, 90)
        papel(c, 540, 1000 - 240 * k, .62 + .2 * k, rot=-4 + 2 * k)
        stamp(c, T, tc, "UN CONTRATO", 540, 330, YEL, -5, 80)
    elif T >= WT("G05", "Cajón"): etiqueta(c, T, WT("G05", "Cajón"), "CAJÓN 7", 540, 660, WHITE, OL, 44)
    return c

def sh_contrato(T, t0, dur):
    c = nave(T, t0, dur, .5, .6, 1.15, 1.25, 150); glow(c, (140, 760, 940, 1500), (255, 220, 140), 70, 70)
    rayos(c, T, 540, 300, (255, 225, 160), 30, 12, 1500)
    papel(c, 540, 930, .98 * zoom(T, t0, dur, .95, 1.03), rot=-3, firmas=2)
    if T >= WT("G07", "Socios"): stamp(c, T, WT("G07", "Socios"), "SOCIOS", 540, 390, YEL, -5, 110)
    return c

def sh_contrato2(T, t0, dur):
    c = nave(T, t0, dur, .5, .6, 1.15, 1.25, 150); glow(c, (140, 760, 940, 1500), (255, 120, 120), 70, 70)
    tt = WT("G08", "tercera")
    rayos(c, T, 540, 300, (255, 225, 160), 30, 12, 1500)
    papel(c, 540, 930, .98 * zoom(T, t0, dur, .95, 1.03), rot=-3, firmas=3 if T >= tt else 2, resalta=True, T=T)
    if T >= tt: stamp(c, T, tt, "TERCERA FIRMA", 540, 390, RED, -5, 96)
    return c

def sh_contrato3(T, t0, dur):
    c = nave(T, t0, dur, .5, .6, 1.15, 1.25, 150); tinte(c, (90, 0, 20), 55)
    rayos(c, T, 540, 300, (255, 225, 160), 30, 12, 1500)
    papel(c, 540, 930, .98 * zoom(T, t0, dur, 1.0, 1.04), rot=-3, firmas=3, resalta=True, T=T, final=True)
    f = clamp(1 - (T - t0) / .3)
    if f > 0: c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(235 * f))))
    c = shake(c, T, 5, 40)
    if T >= WT("G11", "ocultó"): stamp(c, T, WT("G11", "ocultó"), "TE LO OCULTÓ", 540, 390, RED, -5, 100)
    return c

def sh_helado(T, t0, dur):
    c = nave(T, t0, dur, .5, .5, 1.1, 1.18, 125); tinte(c, (0, 40, 90), 60)
    manolo(c, T, 540, 1380, 1.15 * zoom(T, t0, dur, 1.0, 1.06), None)
    if T >= WT("G13", "helado"): stamp(c, T, WT("G13", "helado"), "HELADO", 540, 470, YEL, -5, 110)
    return c

# ================= ESCENAS NUEVAS (Parte 8): fondos y planos variados =================
def lluvia(c, T, n=110, a=110, vel=1500, x0=0, x1=W, y0=0, y1=H):
    ov = blank(); d = ImageDraw.Draw(ov)
    for i in range(n):
        x = x0 + ((i * 137 + 40) % max(1, x1 - x0)); y = y0 + ((i * 331 + T * vel * (.7 + (i % 5) * .12)) % (y1 - y0)); L = 40 + (i % 4) * 14
        d.line((x, y, x - L * .25, y + L), fill=(200, 215, 255, a), width=3)
    c.alpha_composite(ov)

_VENT = {}
def bg_ventana(T, t0, z0=1.0, z1=1.08, dur=6):
    """Ventana del taller de noche con lluvia: luces de la ciudad desenfocadas + marco."""
    if "v" not in _VENT:
        im = bg("bg_fachada", 0, 0, 1.0, 1.0, 1, .5, .15).filter(ImageFilter.GaussianBlur(14)); im = dark(im, 120) or im
        im = Image.blend(im, Image.new("RGBA", (W, H), (20, 40, 90, 255)), .45)
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, W, 90), fill=(34, 26, 24)); d.rectangle((0, H - 560, W, H), fill=(34, 26, 24))
        d.rectangle((W // 2 - 14, 0, W // 2 + 14, H), fill=(34, 26, 24))
        _VENT["v"] = im
    z = z0 + (z1 - z0) * clamp((T - t0) / dur)
    im = _VENT["v"].resize((int(W * z), int(H * z)), Image.BILINEAR)
    ox, oy = (im.width - W) // 2, (im.height - H) // 2
    c = im.crop((ox, oy, ox + W, oy + H)); lluvia(c, T, 120, 100); return c

def sh_manolo_ventana(lid, x=540, y=1500, s=1.35, txt=None, tw=None, z=(1.0, 1.1), tin=None, col=RED, txt2=None, tw2=None):
    def f(T, t0, dur):
        c = bg_ventana(T, t0, 1.0, 1.1, dur)
        glow(c, (100, 900, 980, 1900), (255, 190, 110), 90, 90)
        manolo(c, T, x, y, s * zoom(T, t0, dur, z[0], z[1]), lid)
        if tin: tinte(c, tin, 40)
        if txt and T >= WT(lid, tw): stamp(c, T, WT(lid, tw), txt, 540, 560, col, -5, 92)
        if txt2 and T >= WT(lid, tw2): stamp(c, T, WT(lid, tw2), txt2, 540, 700, YEL, 4, 80)
        return c
    return f

def sh_res8(T, t0, dur):
    c = poligono(T, 0, 1.2, 1.3, 4, 120)
    glow(c, (-120, 520, 760, 1180), AZ, 90, 80); glow(c, (420, 700, 1200, 1300), MAG, 60, 80)
    d = ImageDraw.Draw(c)
    text(d, (540, 430), "RESULTADO PARTE 7", 70, YEL, stroke=8)
    barra_voto(c, T, 640, "A", "ESCUCHAR A MANOLO", 81, AZ, True, 0)
    barra_voto(c, T, 830, "B", "PERSEGUIR A NITRO", 19, MAG, False, 0)
    R.estrella(ImageDraw.Draw(c), 120, 660, 30 * (1 + .15 * math.sin(T * 8)), (242, 190, 60))
    stamp(c, T, -1, "¡ELEGISTEIS LA A!", 540, 1080, YEL, -6, 116)
    confeti(c, T, .3)
    return c

def sh_puerta8(T, t0, dur):
    c = bg("bg_taller", T, t0, 1.1, 1.3, dur, .5, .45); dark(c, 90)
    glow(c, (100, 300, 980, 1500), (255, 230, 170), 80, 90)
    manolo(c, T, 300, 1400, .95, None)
    k = ease(clamp((T - t0 - .15) / .9))
    pr = layer_persiana()
    c.alpha_composite(pr, (0, int(-pr.height + (pr.height + 40) * k)))
    if k > .95: stamp(c, T, t0 + 1.0, "A SOLAS", 540, 520, YEL, -5, 110)
    return c

_PER = {}
def layer_persiana():
    if "p" not in _PER:
        im = R.layer("persiana").convert("RGBA"); _PER["p"] = im.resize((W, int(W * im.height / im.width)), Image.LANCZOS)
    return _PER["p"]

def sh_flash8(lid, extra):
    def f(T, t0, dur):
        c = bg("bg_mesa", T, t0, 1.1, 1.3, dur, .5, .4); dark(c, 150)
        glow(c, (100, 400, 980, 1500), (255, 214, 140), 110, 90)
        extra(c, T, t0, dur)
        c = sepia(c, .6); vineta(c, 200)
        return c
    return f

def fx_venta(c, T, t0, dur):
    k = ease(clamp((T - WT("G03", "prototipo") - .5) / .6))
    put(c, "motor", 540 + 700 * k, 900, .75 * (1 - .25 * k))          # el prototipo se va
    k2 = ease(clamp((T - WT("G03", "deuda") + .2) / .6))
    d = ImageDraw.Draw(c)
    for i in range(5):                                                  # fajo de billetes
        y = 1320 - i * 34
        d.rounded_rectangle((540 - 230 + 5 * i, y, 540 + 230 + 5 * i, y + 28), 8, fill=(96, 168, 92), outline=OL, width=5)
    c2 = blank(); text(ImageDraw.Draw(c2), (540, 1180), "DEUDA DE NITRO", 56, (255, 120, 110), stroke=6); c.alpha_composite(c2)
    if T >= WT("G03", "prototipo"): stamp(c, T, WT("G03", "prototipo"), "VENDIÓ EL PROTOTIPO", 540, 470, YEL, -5, 70)
    if T >= WT("G03", "salvarlo"):
        d = ImageDraw.Draw(c); corazon(d, 540, 700, 220 * popscale(T, WT("G03", "salvarlo"), .4), (230, 60, 80))
        stamp(c, T, WT("G03", "salvarlo"), "SALVARLO", 540, 900, YEL, 4, 90)

def sh_lucia8(T, t0, dur):
    c = bg("bg_taller", T, t0, 1.25, 1.4, dur, .5, .75); dark(c, 110); tinte(c, (30, 50, 110), 50)
    glow(c, (100, 700, 980, 1700), (255, 190, 130), 70, 90)
    lucia(c, T, 540, 1400, 1.25 * zoom(T, t0, dur, 1.0, 1.06), "G04")
    if T >= WT("G04", "qué"): stamp(c, T, WT("G04", "qué"), "¿POR QUÉ?", 540, 560, YEL, -5, 100)
    return c

def sh_exterior(T, t0, dur, z0=1.0, z1=1.12, fy=.3):
    c = bg("bg_fachada", T, t0, z0, z1, dur, .5, fy); dark(c, 70); tinte(c, (10, 20, 70), 55); lluvia(c, T, 90, 90); return c

def sh_fuera(T, t0, dur):
    c = sh_exterior(T, t0, dur, 1.15, 1.3, .62)
    glow(c, (160, 930, 920, 1180), (255, 215, 140), 120 + 50 * math.sin(T * 25), 40); glow(c, (60, 900, 360, 1060), (255, 240, 200), 160, 25); glow(c, (720, 900, 1020, 1060), (255, 240, 200), 160, 25)
    c = shake(c, T, 7, 45)
    if T >= WT("G06", "ruge"): stamp(c, T, WT("G06", "ruge"), "¡RUGE!", 540, 520, RED, -6, 120)
    return c

def sh_oido(T, t0, dur):
    c = bg_ventana(T, t0, 1.0, 1.08, dur); tinte(c, (60, 0, 20), 35)
    nitro(c, T, 540, 1500, 1.5 * zoom(T, t0, dur, 1.0, 1.08), None)
    vineta(c, 200)
    if T >= WT("G06", "oído"): stamp(c, T, WT("G06", "oído"), "LO HA OÍDO TODO", 540, 560, RED, -4, 84)
    return c

def sh_deportivo_sale(T, t0, dur):
    c = sh_exterior(T, t0, dur, 1.0, 1.06, .62)
    k = ease(clamp((T - t0) / max(dur, .6)))
    coche_faros(c, 100 + 1300 * k, 1260 + 6 * math.sin(T * 50) * (1 - k), .45 + .5 * k, .8, flip=True, largo=800, rev=-30 * (1 - k))
    if T >= WT("G06", "coche"): etiqueta(c, T, WT("G06", "coche"), "SE LARGA", 540, 470, YEL, OL, 52)
    return c

def mont_bg(T, vel=0, tipo="montana"):
    """Fondo plano apaisado para persecución; tipo = calle | puerto | montana. Se desplaza con 'vel'."""
    if tipo == "calle": base = bg("bg_fachada", 0, 0, 1.0, 1.0, 1, .5, .35); dark(base, 90); tinte(base, (10, 20, 70), 50)
    elif tipo == "puerto": base = bg_puerto(0, 0, 1.0, 1.0, 1)
    else: base = cielo_montana(.0)
    off = int(vel) % W
    out = Image.new("RGBA", (W, H)); out.alpha_composite(base, (-off, 0)); out.alpha_composite(base, (W - off, 0))
    return out

_MC = {}
def cielo_montana(dusk):
    key = round(dusk, 1)
    if key in _MC: return _MC[key]
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(im)
    for y in range(0, 1300):
        k = y / 1300; d.line((0, y, W, y), fill=(int(40 + 190 * k * .8), int(30 + 80 * k), int(90 + 40 * (1 - k))))
    d.ellipse((600, 880, 840, 1120), fill=(255, 190, 110))
    for col, base_y, amp, ph in (((70, 50, 100), 1020, 300, 0), ((46, 34, 74), 1120, 240, 2), ((26, 20, 44), 1230, 170, 5)):
        pts = [(0, 1500)] + [(x, base_y - amp * abs(math.sin(x / 260 + ph)) * (.6 + .4 * math.sin(x / 90 + ph))) for x in range(0, W + 40, 40)] + [(W, 1500)]
        d.polygon(pts, fill=col)
    d.rectangle((0, 1300, W, H), fill=(34, 30, 44))
    _MC[key] = im.filter(ImageFilter.GaussianBlur(1.0)); return _MC[key]

def chase(tipo, lid=None, tw=None, txt=None):
    def f(T, t0, dur):
        c = mont_bg(T, (T - t0) * 380, tipo)
        d = ImageDraw.Draw(c); d.rectangle((0, 1380, W, H), fill=(26, 24, 34)); d.rectangle((0, 1380, W, 1392), fill=(200, 180, 60))
        for i in range(8):   # marcas de la carretera en movimiento
            x = ((i * 220 - (T - t0) * 1300) % (W + 220)) - 220; d.rectangle((x, 1560, x + 110, 1574), fill=(220, 220, 220))
        by = 1450 + 5 * math.sin(T * 40)
        coche_faros(c, 700, by, .62, .8, flip=True, largo=520)
        ov = blank(); od = ImageDraw.Draw(ov)
        for i in range(14):   # líneas de velocidad
            x = ((i * 173 - (T - t0) * 2600) % (W + 400)) - 200; y = 480 + (i * 127) % 800; od.line((x, y, x + 260, y), fill=(255, 255, 255, 70), width=4)
        c.alpha_composite(ov)
        if txt: stamp(c, T, t0, txt, 540, 480, YEL, -4, 110)
        return c
    return f

def sh_nitro_coche(T, t0, dur):
    c = cielo_montana(0).copy(); tinte(c, (0, 0, 30), 110)
    glow(c, (120, 760, 960, 1700), (80, 200, 255), 60, 90)
    d = ImageDraw.Draw(c); d.rectangle((0, 1560, W, H), fill=(12, 12, 20))
    nitro(c, T, 540, 1380, 1.35 * zoom(T, t0, dur, 1.0, 1.08), "G08")
    vineta(c, 200)
    if T >= WT("G08", "sigas"): stamp(c, T, WT("G08", "sigas"), "NO ME SIGAS", 540, 560, RED, -5, 96)
    return c

def mirador_bg(T):
    c = cielo_montana(0).copy(); d = ImageDraw.Draw(c)
    for i in range(60):   # luces de la ciudad abajo
        x = (i * 211) % W; y = 1060 + (i * 59) % 240; d.ellipse((x, y, x + 6, y + 6), fill=(255, 220, 140))
    d.rectangle((0, 1380, W, H), fill=(40, 34, 50)); d.rectangle((0, 1380, W, 1400), fill=(90, 80, 96))
    for x in range(0, W + 60, 90): d.rectangle((x, 1280, x + 14, 1400), fill=(60, 56, 70))   # barandilla
    d.rectangle((0, 1270, W, 1290), fill=(70, 66, 84))
    return c

def sh_derrape(T, t0, dur):
    c = mirador_bg(T)
    k = ease(clamp((T - t0) / max(dur * .6, .5)))
    im = R.scaled("coche_negro", .66).rotate(-14 * math.sin(k * math.pi) * (1 - k), resample=Image.BICUBIC, expand=True)
    x = 1500 - 900 * k
    humo_ = blank(); hd = ImageDraw.Draw(humo_)
    for i in range(8):
        r = 60 + i * 18 + 40 * k; hd.ellipse((x + 200 + i * 40 - r, 1560 - r * .5, x + 200 + i * 40 + r, 1560 + r * .5), fill=(220, 220, 230, int(100 * (1 - i / 9))))
    c.alpha_composite(humo_.filter(ImageFilter.GaussianBlur(14)))
    c.alpha_composite(im, (int(x - im.width / 2), int(1460 - im.height / 2)))
    if T >= WT("G09", "derrapa"): etiqueta(c, T, WT("G09", "derrapa"), "¡DERRAPA!", 540, 470, YEL, OL, 56)
    return c

def sh_baja(T, t0, dur):
    c = mirador_bg(T)
    im = R.scaled("coche_negro", .66); c.alpha_composite(im, (int(620 - im.width / 2), int(1460 - im.height / 2)))
    k = ease(clamp((T - t0) / .6))
    nitro(c, T, 280, 1500, .85 + .0 * k, None)
    papel(c, 330, 1000 - 40 * k, .34 * k + .02, rot=-8, firmas=2, T=T)
    if T >= WT("G09", "papel"): stamp(c, T, WT("G09", "papel"), "UN PAPEL", 540, 470, RED, -5, 100)
    return c

def mitad_papel(c, cx, cy, s=1.0, rot=0, T=0, resalta=False):
    lay = Image.new("RGBA", (760, 960), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((20, 20, 740, 940), 18, fill=(240, 228, 196), outline=OL, width=8)
    d.polygon([(20, 20), (150, 20), (20, 150)], fill=(212, 196, 160))      # esquina rota
    text(d, (380, 110), "CONTRATO · 2/2", 62, (50, 40, 40), stroke=0)
    for i in range(5): d.line((80, 190 + i * 46, 680, 190 + i * 46), fill=(150, 150, 150), width=4)
    text(d, (380, 470), "CLÁUSULA SECRETA", 58, (150, 30, 40), stroke=0)
    d.line((120, 760, 640, 760), fill=(40, 40, 70), width=5)
    for k in range(7):
        d.line((180 + k * 60, 730, 210 + k * 60, 690 + (k % 2) * 40), fill=(40, 40, 110), width=7)
    text(d, (380, 820), "FIRMA ¿?", 40, (80, 80, 90), stroke=0)
    if resalta:
        v = 160 + int(90 * abs(math.sin(T * 9))); d.rounded_rectangle((90, 640, 670, 860), 24, outline=(220, 40, 50, v), width=10)
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    lay = lay.resize((int(lay.width * s), int(lay.height * s)), Image.LANCZOS)
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * .55))); sh = sh.filter(ImageFilter.GaussianBlur(18))
    c.alpha_composite(sh, (int(cx - lay.width / 2) + 14, int(cy - lay.height / 2) + 26)); c.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def sh_mitad8(T, t0, dur):
    c = mirador_bg(T); tinte(c, (0, 0, 30), 60)
    nitro(c, T, 540, 1450, 1.25 * zoom(T, t0, dur, 1.0, 1.05), "G10")
    mitad_papel(c, 540, 800, .44 + .03 * ease(clamp((T - t0) / .5)), rot=-5 + 2 * math.sin(T * 3), T=T, resalta=T >= WT("G10", "firma"))
    if T >= WT("G10", "mitad"): stamp(c, T, WT("G10", "mitad"), "LA OTRA MITAD", 540, 470, YEL, -5, 100)
    return c

def sh_firma8(T, t0, dur):
    c = bg("bg_mesa", T, t0, 1.2, 1.4, dur, .5, .5); dark(c, 80); tinte(c, (70, 10, 20), 55)
    glow(c, (60, 400, 1020, 1400), (255, 214, 140), 110, 90)
    mitad_papel(c, 540, 790, .78 * zoom(T, t0, dur, .95, 1.05), rot=3, T=T, resalta=True)
    manolo(c, T, 540, 1700, .95, "G11")
    c = shake(c, T, 4, 40); vineta(c, 190)
    if T >= WT("G11", "firma"): stamp(c, T, WT("G11", "firma"), "ESA FIRMA…", 540, 470, RED, -5, 100)
    return c

def sh_sombra(T, t0, dur):
    c = bg("bg_taller", T, t0, 1.15, 1.3, dur, .5, .5); dark(c, 140); tinte(c, (60, 0, 20), 60)
    glow(c, (120, 600, 960, 1700), (255, 60, 60), 90 + 30 * math.sin(T * 5), 100)
    ov = blank(); d = ImageDraw.Draw(ov); cx = 540; k = zoom(T, t0, dur, .95, 1.06)
    d.ellipse((cx - 150 * k, 760, cx + 150 * k, 1060), fill=(6, 6, 12, 255))
    d.rounded_rectangle((cx - 330 * k, 1040, cx + 330 * k, 1800), 150, fill=(6, 6, 12, 255))
    c.alpha_composite(ov)
    for ex in (-60, 60): ImageDraw.Draw(c).ellipse((cx + ex * k - 14, 900, cx + ex * k + 14, 922), fill=(255, 70, 70))
    text(ImageDraw.Draw(c), (540, 930 - 0), "", 10, WHITE)
    c = vineta(c, 200) or c
    if T >= WT("G12", "Alguien"): stamp(c, T, WT("G12", "Alguien"), "¿QUIÉN?", 540, 500, RED, -5, 130)
    return c

def opcion8(d, cx, cy, t1, t2, t3, col, k):
    """Opción limpia (sin letra A/B): título grande con barra de color y pros/contras."""
    if k <= .5: return
    d.rounded_rectangle((cx - 230 * k, cy + 60, cx + 230 * k, cy + 74), 7, fill=col)
    text(d, (cx, cy), t1, 120 * k, WHITE, stroke=9)
    text(d, (cx, cy + 128), t2, 40, YEL, "mm", F_UI, stroke=5)
    text(d, (cx, cy + 178), t3, 34, (255, 150, 140), "mm", F_UI, stroke=5)

def lado8(name):
    key = "L8" + name
    if key in _LC: return _LC[key]
    if name == "A":
        A = bg("bg_mesa", 0, 0, 1.2, 1.2, 1, .5, .5).convert("RGBA"); dark(A, 90); glow(A, (0, 500, 1000, 1500), AZ, 80, 80)
        mitad_papel(A, 300, 1250, .62, rot=-8, T=0, resalta=False)
    else:
        A = bg("bg_taller", 0, 0, 1.3, 1.3, 1, .5, .8).convert("RGBA"); dark(A, 130)
        A.alpha_composite(Image.new("RGBA", (W, H), (60, 10, 50, 60)))
        put(A, "manolo", 790, 1420, .85)
    _LC[key] = A; return A

def bruma_luz(c, T, a=34):
    """Brillo suave (bloom) + viñeta + polvo flotante + ligera gradación fría/cálida: acabado de cine."""
    im = c.convert("RGB")
    br = im.point(lambda v: max(0, v - 150) * 3).filter(ImageFilter.GaussianBlur(26))
    from PIL import ImageChops
    im = ImageChops.screen(im, Image.eval(br, lambda v: int(v * a / 100)))
    out = im.convert("RGBA"); vineta(out, 120); polvo(out, T, 22, 360, 1560)
    return out

def con_post(f):
    return lambda T, t0, dur: bruma_luz(f(T, t0, dur), T)

# ======================================================================= EP.8 LARGO: piezas nuevas
_NV = {}
def nave_c(hy=830, giro=0, cam_h=1.4, luz=1.0):
    k = (hy, giro, cam_h, luz)
    if k not in _NV: _NV[k] = P.nave(0.0, hy=hy, giro=giro, cam_h=cam_h, luz=luz)
    c, pr = _NV[k]; return c.copy(), pr

def cam(c, T, t0, dur, z0=1.0, z1=1.08, fx=.5, fy=.5, dx=0):
    k = ease(clamp((T - t0) / max(dur, .1))); z = max(1.0, z0 + (z1 - z0) * k)
    if z < 1.002 and not dx: return c
    cc = c.resize((int(W * z), int(H * z)), Image.BILINEAR)
    ox = max(0, min(cc.width - W, int((cc.width - W) * fx + dx * k))); oy = max(0, min(cc.height - H, int((cc.height - H) * fy)))
    return cc.crop((ox, oy, ox + W, oy + H))

MOUTH = {"manolo_full": (800, 1148, 56), "nitro_full": (823, 1084, 44), "lucia_full": (780, 1088, 60), "padre_full": (799, 1100, 50), "padre_sin_sombrero": (799, 1100, 50)}
def pj(c, pr, name, x, z, alto, T, lid=None, flip=False):
    info = P.personaje(c, pr, name, x, z, alto, flip=flip, T=T)
    if lid:
        cx, cy, w = MOUTH[name]
        if flip: b = R.layer(name).getbbox(); cx = b[0] + b[2] - cx
        P.boca(c, info, T, talk(lid, T), cx, cy, w)
    return info

def sil(c, pr, name, x, z, alto, col=(4, 4, 8), flip=False, a=255):
    """Silueta negra de un personaje (para sombras / luz de contraluz)."""
    im = R.layer(name); im = im.crop(im.getbbox()); px, py, s = pr(x, z)
    h = int(alto * s); w = int(im.width * h / im.height); sp = im.resize((w, h), Image.LANCZOS)
    if flip: sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
    blk = Image.new("RGBA", sp.size, col + (255,)); blk.putalpha(sp.getchannel("A").point(lambda v: v * a // 255))
    c.alpha_composite(blk, (int(px - w / 2), int(py - h * .96)))
    return int(px), int(py - h * .96), w, h

def sep(c, T, k=.9):
    c = sepia(c, k); ov = blank(); d = ImageDraw.Draw(ov)
    for i in range(3):
        x = (int(T * 23 + i * 331) * 97) % W; d.line((x, 0, x + 4, H), fill=(255, 240, 210, 22), width=2)
    c.alpha_composite(ov); vineta(c, 215); return c

def tx(c, T, t, s, y, col=YEL, rot=-5, size=100):
    if T >= t: stamp(c, T, t, s, 540, y, col, rot, size)

def et(c, T, t, s, y, col=YEL, size=48):
    if T >= t: etiqueta(c, T, t, s, 540, y, col, OL, size)

def hombro(c, T, side=-1, s=1.0, y=1790):
    P.hombro(c, T, 150 if side < 0 else 930, y, s)

# ---------------------------------------------------------------- carreteras (calle / puerto / montaña)
def via(T, v=40., hy=860, giro=0., modo="calle"):
    if modo == "puerto":
        return P.carretera(T, v, hy, 540, giro)
    F = 1500.0; vx = 540 + giro; cam_h = 1.0
    def pr(x, z, y=0.0):
        z = max(z, .3); s = F / z; return vx + x * s, hy + (cam_h - y) * s, s
    c = Image.new("RGBA", (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(c)
    for y in range(0, hy + 1):
        k = y / hy
        d.line((0, y, W, y), fill=((int(14 + 70 * k * k), int(14 + 30 * k), int(40 + 20 * k)) if modo == "calle" else (int(40 + 190 * k * .8), int(26 + 70 * k), int(90 + 40 * (1 - k)))))
    if modo == "montana":
        d.ellipse((650, hy - 190, 850, hy + 10), fill=(255, 190, 110))
        for col, bo, amp, ph in (((70, 50, 100), 0, 300, 0), ((46, 34, 74), 40, 230, 2), ((26, 20, 44), 80, 160, 5)):
            pts = [(0, hy + 60)] + [(x, hy + bo - amp * abs(math.sin(x / 260 + ph + giro / 400)) * (.6 + .4 * math.sin(x / 90 + ph))) for x in range(0, W + 40, 40)] + [(W, hy + 60)]
            d.polygon(pts, fill=col)
    gcol = (12, 12, 20) if modo == "calle" else (10, 8, 18)
    d.rectangle((0, hy, W, H), fill=gcol)
    def quad(x0, x1, z0, z1, col, y0=0.0, y1=0.0):
        a, b, c2, e = pr(x0, z0, y0), pr(x1, z0, y0), pr(x1, z1, y1), pr(x0, z1, y1)
        d.polygon([(a[0], a[1]), (b[0], b[1]), (c2[0], c2[1]), (e[0], e[1])], fill=col)
    zf, zn = 400, .9
    quad(-5.2, 5.2, zf, zn, (28, 29, 40) if modo == "calle" else (36, 34, 46))
    quad(-5.2, -5.0, zf, zn, (200, 180, 60)); quad(5.0, 5.2, zf, zn, (200, 180, 60))
    off = (T * v) % 12; z = 12 * 22 - off
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(gl)
    while z > 3:
        for sgn in (-1, 1):
            if modo == "calle":
                hh = 7 + (int(z / 12 + (sgn > 0) * 3) % 4) * 3
                base = 7.5 + (int(z / 12) % 2) * .8
                a, b, e, f = pr(sgn * base, z), pr(sgn * base, z + 10), pr(sgn * base, z, hh), pr(sgn * base, z + 10, hh)
                col = (20 + int(z / 12) % 3 * 6, 24 + int(z / 12) % 4 * 4, 44 + int(z / 12) % 2 * 12)
                d.polygon([(a[0], a[1]), (b[0], b[1]), (f[0], f[1]), (e[0], e[1])], fill=col)
                for wy in range(1, int(hh * .8), 2):          # ventanas
                    if (int(z) + wy * 3 + (sgn > 0)) % 3:
                        p0, p1 = pr(sgn * base, z + 2, wy + .3), pr(sgn * base, z + 8, wy + 1.0)
                        d.rectangle((min(p0[0], p1[0]), min(p0[1], p1[1]), max(p0[0], p1[0]), max(p0[1], p1[1])), fill=(255, 205, 120))
            else:
                if sgn > 0:      # pared de roca
                    pts = [pr(7, z), pr(7, z + 12), pr(9 + (int(z) % 3), z + 12, 14), pr(9 + (int(z) % 3), z, 12)]
                    d.polygon([(p[0], p[1]) for p in pts], fill=(30 + int(z) % 4 * 5, 26 + int(z) % 3 * 4, 40))
                else:            # quitamiedos
                    a, e = pr(-6.2, z), pr(-6.2, z, 1.0)
                    d.line((a[0], a[1], e[0], e[1]), fill=(160, 160, 175), width=max(2, int(a[2] * .12)))
        z -= 12
    if modo == "montana":
        for i in range(40):   # luces del valle a la izquierda, abajo
            x = (i * 137 + int(giro)) % 520; y = hy + 20 + (i * 53) % 220
            d.ellipse((x, y, x + 5, y + 5), fill=(255, 215, 140))
    off2 = (T * v) % 24; z = 24 * 14 - off2
    while z > 4:
        for sgn in (-1, 1):
            if modo == "montana" and sgn > 0: continue
            top = pr(sgn * 6.4, z, 7.5); base = pr(sgn * 6.4, z)
            d.line((base[0], base[1], top[0], top[1]), fill=(50, 52, 70), width=max(1, int(top[2] * .05)))
            s = top[2]; g.ellipse((top[0] - s * .9, top[1] - s * .5, top[0] + s * .9, top[1] + s * .5), fill=(255, 190, 100, int(clamp(.4 + s / 900) * 255)))
            p = pr(sgn * 3.0, z + 3); g.ellipse((p[0] - p[2] * 2.6, p[1] - p[2] * .22, p[0] + p[2] * 2.6, p[1] + p[2] * .22), fill=(255, 190, 100, 60))
        z -= 24
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(c)
    off3 = (T * v) % 8; z = 8 * 40 - off3
    while z > 1.2:
        a0, a1, b0, b1 = pr(-.12, z), pr(.12, z), pr(-.12, z - 3.6), pr(.12, z - 3.6)
        d.polygon([(a0[0], a0[1]), (a1[0], a1[1]), (b1[0], b1[1]), (b0[0], b0[1])], fill=(225, 225, 215)); z -= 8
    c = c.filter(ImageFilter.GaussianBlur(.8))
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(fog)
    for i in range(14): fd.rectangle((0, hy - 200 + i * 18, W, hy - 80 + i * 18), fill=(60, 70, 120, 27 * (14 - i) // 14))
    c.alpha_composite(fog.filter(ImageFilter.GaussianBlur(40)))
    return c, pr

MODELOS = {"negro": dict(car=(14, 14, 20), cab=(18, 18, 28), vid=(34, 40, 62), alerón=True, neon=(60, 220, 255)),
           "deportivo": dict(car=(236, 236, 242), cab=(224, 224, 232), vid=(70, 82, 120), banda=(236, 100, 160)),
           "seat": dict(car=(206, 44, 44), cab=(236, 236, 240), vid=(50, 60, 90), banda=(250, 250, 250))}

def trasera(c, pr, x_m, z, frena=0.0, s_=1.0, modelo="negro", ang=0.0):
    """Coche visto por detrás, alineado con la carretera (pilotos, luneta, matrícula, escape, sombra)."""
    m = MODELOS[modelo]; px, py, s = pr(x_m, z); w, h = 1.95 * s * s_, 1.28 * s * s_
    ov = blank(); d = ImageDraw.Draw(ov)
    d.ellipse((px - w * .62, py - h * .10, px + w * .62, py + h * .08), fill=(0, 0, 0, 150))                                  # sombra
    if m.get("neon"):
        d.ellipse((px - w * .5, py - h * .06, px + w * .5, py + h * .05), fill=m["neon"] + (150,))
    d.rounded_rectangle((px - w / 2, py - h * .78, px + w / 2, py - h * .12), int(h * .1), fill=m["car"] + (255,))
    d.polygon([(px - w * .38, py - h * .78), (px + w * .38, py - h * .78), (px + w * .27, py - h * 1.0), (px - w * .27, py - h * 1.0)], fill=m["cab"] + (255,))
    d.polygon([(px - w * .31, py - h * .80), (px + w * .31, py - h * .80), (px + w * .23, py - h * .96), (px - w * .23, py - h * .96)], fill=m["vid"] + (255,))
    if m.get("alerón"): d.rectangle((px - w * .46, py - h * 1.02, px + w * .46, py - h * .95), fill=(6, 6, 10, 255)); d.rectangle((px - w * .40, py - h * .96, px - w * .36, py - h * .78), fill=(6, 6, 10, 255)); d.rectangle((px + w * .36, py - h * .96, px + w * .40, py - h * .78), fill=(6, 6, 10, 255))
    if m.get("banda"): d.rectangle((px - w / 2, py - h * .50, px + w / 2, py - h * .44), fill=m["banda"] + (255,))
    for sx in (-1, 1): d.rounded_rectangle((px + sx * w * .36 - w * .09, py - h * .16, px + sx * w * .36 + w * .09, py - h * .02), int(h * .03), fill=(8, 8, 12, 255))   # ruedas
    d.rectangle((px - w * .5, py - h * .27, px + w * .5, py - h * .21), fill=(8, 8, 12, 255))
    for sx in (-1, 1):
        x0 = px + sx * w * .40
        d.rounded_rectangle((x0 - w * .12, py - h * .62, x0 + w * .12, py - h * .46), int(h * .04), fill=(255, 40 + int(60 * frena), 40, 255))
        d.ellipse((px + sx * w * .22 - w * .035, py - h * .23, px + sx * w * .22 + w * .035, py - h * .17), fill=(70, 70, 80, 255))            # escapes
    d.rectangle((px - w * .09, py - h * .43, px + w * .09, py - h * .33), fill=(235, 235, 225, 255))
    gl = blank(); g = ImageDraw.Draw(gl); r = w * (.2 + .22 * frena)
    for sx in (-1, 1):
        x0 = px + sx * w * .40; g.ellipse((x0 - r, py - h * .54 - r * .7, x0 + r, py - h * .54 + r * .7), fill=(255, 30, 30, int((200 + 55 * frena) * .8)))
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(max(6, w * .07))))
    c.alpha_composite(ov)
    if frena > 0: c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(max(10, w * .15))))
    return px, py, w, h

def volante(c, cx, cy, rx, ry, ang=0.0, manos=True):
    wh = blank(); wd = ImageDraw.Draw(wh)
    wd.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=(16, 16, 24, 255), width=int(rx * .16))
    wd.ellipse((cx - rx + 8, cy - ry + 8, cx + rx - 8, cy + ry - 8), outline=(70, 70, 92, 255), width=3)
    wd.rounded_rectangle((cx - rx * .2, cy - ry * .2, cx + rx * .2, cy + ry * .2), 14, fill=(28, 28, 40, 255), outline=(70, 70, 92, 255), width=3)
    wd.line((cx - rx * .9, cy, cx - rx * .2, cy), fill=(16, 16, 24, 255), width=int(rx * .1)); wd.line((cx + rx * .9, cy, cx + rx * .2, cy), fill=(16, 16, 24, 255), width=int(rx * .1))
    wh = wh.rotate(ang, center=(cx, cy), resample=Image.BICUBIC); c.alpha_composite(wh)
    if manos:
        hd = ImageDraw.Draw(c)
        for sx in (-1, 1):
            a = math.radians(ang); hx = cx + sx * rx * .78 * math.cos(a) - (-ry * .5) * math.sin(a) * 0; hy_ = cy - ry * .62 + sx * rx * .78 * math.sin(a) * .5
            hd.rounded_rectangle((hx - rx * .2, hy_ - rx * .11, hx + rx * .2, hy_ + rx * .12), 26, fill=(224, 176, 134, 255), outline=OL, width=6)
            for k in range(4): hd.rounded_rectangle((hx - rx * .17 + k * rx * .09, hy_ - rx * .17, hx - rx * .1 + k * rx * .09, hy_ - rx * .02), 10, fill=(224, 176, 134, 255), outline=OL, width=4)

def cabina(c, T, volante_ang=0.0, llueve=True, vib=0.0, lid=None):
    """Asiento del copiloto: parabrisas con lluvia, Lucía al volante (de frente a ti), salpicadero y espejo."""
    ov = blank(); d = ImageDraw.Draw(ov)
    # ventanilla izquierda con luces pasando y montante
    d.rectangle((0, 520, 190, 1500), fill=(10, 14, 28, 255))
    for k in range(6):
        y = 640 + (k * 157) % 760; x = ((k * 97 - T * 1500) % 260) - 60; d.rectangle((x, y, x + 120, y + 10), fill=(255, 205, 120, 200))
    ov = ov.filter(ImageFilter.GaussianBlur(5)); c.alpha_composite(ov)
    ov = blank(); d = ImageDraw.Draw(ov)
    d.polygon([(0, 0), (210, 0), (170, 1500), (0, 1500)], fill=(8, 8, 12, 255)); d.polygon([(W, 0), (W - 120, 0), (W - 40, 1500), (W, 1500)], fill=(8, 8, 12, 255))
    d.polygon([(190, 0), (240, 0), (200, 1500), (160, 1500)], fill=(14, 14, 20, 255))
    d.rounded_rectangle((420, 300, 700, 372), 20, fill=(10, 10, 16, 255), outline=(50, 50, 66, 255), width=4)                   # retrovisor
    d.rectangle((0, 1450, W, H), fill=(10, 10, 16, 255)); d.rectangle((0, 1440, W, 1460), fill=(30, 30, 42, 255))
    for cx_, col in ((760, (255, 170, 60)), (930, (90, 220, 255))):            # relojes del salpicadero
        d.ellipse((cx_ - 70, 1500, cx_ + 70, 1640), fill=(6, 6, 10, 255), outline=col + (255,), width=4)
        ang = -2.5 + 4.6 * (.5 + .5 * math.sin(T * 3 + cx_)) if vib else -2.2
        d.line((cx_, 1570, cx_ + 52 * math.cos(ang), 1570 + 52 * math.sin(ang)), fill=(255, 80, 70, 255), width=5)
    d.rounded_rectangle((520, 1700, 1000, 1860), 26, fill=(18, 18, 28, 255), outline=(40, 40, 56, 255), width=4)               # guantera
    c.alpha_composite(ov)
    if llueve:
        lluvia(c, T, 90, 120, 700, 0, W, 0, 1440)
        ph = (T * .9) % 1.0; ang = math.radians(150 - 120 * (1 - abs(2 * ph - 1)))
        lay = blank(); ImageDraw.Draw(lay).line((560, 1450, 560 + 640 * math.cos(ang), 1450 - 640 * math.sin(ang)), fill=(6, 6, 10, 230), width=14)
        c.alpha_composite(lay)
    lucia(c, T, 360, 1560, 1.3, lid)                                                        # Lucía conduciendo
    ov = blank(); ImageDraw.Draw(ov).rectangle((0, 1640, W, H), fill=(10, 10, 16, 255)); c.alpha_composite(ov)
    volante(c, 360, 1720, 300, 130, max(-12, min(12, volante_ang)))
    return c

def interior_coche(T, t0):
    """Fondo de ventanilla con las luces de la calle pasando en bandas."""
    c = Image.new("RGBA", (W, H), (10, 12, 24, 255)); d = ImageDraw.Draw(c)
    for i in range(7):
        x = ((i * 290 - (T - t0) * 1800) % (W + 600)) - 300; y = 520 + (i * 173) % 700
        d.rectangle((x, y, x + 280, y + 16), fill=(255, 205, 120, 255) if i % 2 else (140, 190, 255, 255))
    c = c.filter(ImageFilter.GaussianBlur(10)); d = ImageDraw.Draw(c)
    d.polygon([(0, 0), (220, 0), (100, H), (0, H)], fill=(8, 8, 12)); d.polygon([(W, 0), (W - 160, 0), (W, H)], fill=(8, 8, 12))
    return c

def lucia_conduce(lid, txts=(), ang0=6, x=540):
    """Cutaway: Lucía al volante, de frente, con el volante delante y el parabrisas con lluvia detrás."""
    def fn(T, t0, dur):
        c = interior_coche(T, t0); glow(c, (160, 700, 920, 1700), (255, 190, 120), 50, 90)
        k = zoom(T, t0, dur, 1.0, 1.08)
        lucia(c, T, x, 1470, 1.75 * k, lid)
        ov = blank(); ImageDraw.Draw(ov).rectangle((0, 1560, W, H), fill=(8, 8, 14, 255)); c.alpha_composite(ov)
        volante(c, x, 1700, 380 * k, 150 * k, ang0 * math.sin(T * 2.2))
        lluvia(c, T, 70, 120, 700, 0, W, 0, 1560)
        c = shake(c, T, 3, 50); vineta(c, 200)
        for tw, s_, y, col in txts: tx(c, T, WT(lid, tw), s_, y, col, -5, 86)
        return c
    return fn

def mirador_p():
    if "m" not in _NV:
        hy = 840; F = 1500.0
        def pr(x, z, y=0.0): z = max(z, .3); s = F / z; return 540 + x * s, hy + (1.0 - y) * s, s
        c = cielo_montana(0).copy(); d = ImageDraw.Draw(c)
        d.rectangle((0, hy - 60, W, H), fill=(14, 12, 22))
        for i in range(70):   # ciudad lejana, abajo
            x = (i * 211) % W; y = hy - 60 + (i * 59) % 260; d.ellipse((x, y, x + 6, y + 6), fill=(255, 220, 140))
        a, b, e, f = pr(-14, 22), pr(14, 22), pr(14, 3.4), pr(-14, 3.4)
        d.polygon([(a[0], a[1]), (b[0], b[1]), (e[0], e[1]), (f[0], f[1])], fill=(40, 36, 52))        # explanada
        a2, b2 = pr(-14, 22, 1.0), pr(14, 22, 1.0)
        d.line((a2[0], a2[1], b2[0], b2[1]), fill=(120, 116, 136), width=10)
        for xm in range(-14, 15, 2):
            p0, p1 = pr(xm, 22), pr(xm, 22, 1.0); d.line((p0[0], p0[1], p1[0], p1[1]), fill=(90, 86, 106), width=8)
        for zz in (6, 9, 13, 18):     # marcas del suelo
            p0, p1 = pr(-14, zz), pr(14, zz); d.line((p0[0], p0[1], p1[0], p1[1]), fill=(52, 48, 66), width=3)
        _NV["m"] = (c.filter(ImageFilter.GaussianBlur(.8)), pr)
    c, pr = _NV["m"]; return c.copy(), pr

# ======================================================================= ACTO 1: el taller, de noche y lloviendo
def s_puerta(T, t0, dur):
    c, pr = nave_c(830, 0)
    a, b = pr(-2.2, 15, 3.3), pr(2.2, 15, 0.0); d = ImageDraw.Draw(c, "RGBA")
    d.rectangle((a[0], a[1], b[0], b[1]), fill=(70, 100, 170, 255))                                  # la calle al fondo, abierta
    ov = blank(); lluvia(ov, T, 40, 120, 900, int(a[0]), int(b[0]), int(a[1]), int(b[1])); c.alpha_composite(ov)
    tc = WT("G01", "puerta"); k = ease(clamp((T - tc + .15) / .9))
    yb = a[1] + (b[1] - a[1]) * k; d = ImageDraw.Draw(c)
    d.rectangle((a[0], a[1], b[0], yb), fill=(70, 74, 98))
    for i in range(1, 14):
        y = a[1] + (b[1] - a[1]) * i / 14
        if y < yb: d.line((a[0], y, b[0], y), fill=(48, 52, 74), width=3)
    glow(c, (int(a[0]) - 140, int(a[1]), int(b[0]) + 140, int(b[1]) + 160), (110, 150, 255), int(70 * (1 - k)), 70)
    info = pj(c, pr, "manolo_full", 0.5, 6.4 - 1.2 * k, 1.9, T)
    c = cam(c, T, t0, dur, 1.0, 1.16, .5, .45)
    tint_ = tinte(c, (20, 30, 80), 40)
    if k > .95: tx(c, T, tc + 1.0, "A SOLAS", 520, YEL, -5, 110)
    return c

def s_manolo_nave(lid, x=.2, z=3.4, alto=2.0, giro=12, z0=1.0, z1=1.1, fx=.5, txts=(), cam_h=1.4, hom=-1, rain=True):
    def f(T, t0, dur):
        c, pr = nave_c(830, giro, cam_h)
        glow(c, (60, 700, 1020, 1500), (255, 200, 120), 60, 90)
        pj(c, pr, "manolo_full", x, z, alto, T, lid)
        if hom: hombro(c, T, hom, 1.0)
        c = cam(c, T, t0, dur, z0, z1, fx, .45); tinte(c, (20, 30, 90), 35)
        for tw, s_, y, col in txts: tx(c, T, WT(lid, tw) if isinstance(tw, str) else tw, s_, y, col, -5, 90)
        return c
    return f

def s_lucia_nave(lid, x=-.5, z=3.4, giro=-14, z0=1.0, z1=1.08, txts=(), fx=.5):
    def f(T, t0, dur):
        c, pr = nave_c(830, giro)
        glow(c, (60, 700, 1020, 1500), (255, 200, 120), 60, 90)
        pj(c, pr, "manolo_full", 1.6, 9.0, 1.9, T, None, True)          # Manolo escucha al fondo
        pj(c, pr, "lucia_full", x, z, 2.0, T, lid)
        c = cam(c, T, t0, dur, z0, z1, fx, .45); tinte(c, (20, 30, 90), 35)
        for tw, s_, y, col in txts: tx(c, T, WT(lid, tw), s_, y, col, -5, 90)
        return c
    return f

def manolo_gorra(c, T, x, y, s, lid, modo=None, tc=0.0):
    """Busto de Manolo: modo 'quita' = se quita la gorra en tc (sale volando); 'sin' = ya sin gorra."""
    yy = y + 6 * math.sin(T * 2.2); u = (T - tc) / 1.1
    sin_ = modo == "sin" or (modo == "quita" and T >= tc)
    put(c, "manolo_sin_gorra" if sin_ else "manolo", x, yy, s)
    if lid: mouth(c, x, yy - 126 * s, T, talk(lid, T), 28 * s)
    if modo == "quita" and 0 <= u < 1.4:
        cp = Image.open(os.path.join(R.LAY, "gorra_manolo.png")).convert("RGBA"); k = s / 2
        cp = cp.resize((int(cp.width * k), int(cp.height * k)), Image.LANCZOS)
        cx = x + 92 * k - 520 * u; cy = yy - 755 * k - 360 * u + 1100 * u * u
        cp = cp.rotate(-70 * u, resample=Image.BICUBIC, expand=True)
        c.alpha_composite(cp, (int(cx - cp.width / 2), int(cy - cp.height / 2)))

def s_ventana(lid_ref, lid_talk, txts=(), y=1500, s=1.35, z=(1.0, 1.1), tin=None, gorra=None):
    def f(T, t0, dur):
        c = bg_ventana(T, t0, 1.0, 1.1, dur)
        glow(c, (100, 900, 980, 1900), (255, 190, 110), 90, 90)
        manolo_gorra(c, T, 540, y, s * zoom(T, t0, dur, z[0], z[1]), lid_talk, gorra, (WT(lid_ref, "quita") - .05) if gorra == "quita" else 0)
        P.hombro(c, T, 130, 1830, 1.1)
        if tin: tinte(c, tin, 40)
        for tw, s_, yy, col in txts: tx(c, T, WT(lid_ref, tw), s_, yy, col, -4, 86)
        return c
    return f

def s_vuelta_96(T, t0, dur):
    tv = WT("G08", "volver"); tf = S("G09") - .25
    k = ease(clamp((T - tv) / max(tf - tv, .5)))
    c = bg("bg_mesa", T, t0, 1.0, 1.25, dur, .5, .5); dark(c, 100)
    glow(c, (60, 400, 1020, 1500), (255, 214, 140), 100, 90)
    put_img(c, foto(False), 540, 1000, .9 + .12 * k, rot=-4 + 8 * k)
    yr = int(2026 - 30 * k)
    c = sepia(c, .1 + .85 * k)
    d = ImageDraw.Draw(c)
    ov = blank(); od = ImageDraw.Draw(ov)
    for i in range(10):      # estelas de rebobinado
        y = 420 + (i * 173) % 1100; x = ((i * 241 + T * 2600 * k) % (W + 500)) - 250; od.line((x, y, x + 300, y), fill=(255, 235, 190, int(110 * k)), width=4)
    c.alpha_composite(ov)
    if T >= tv - .1:
        text(d, (540, 560), f"{yr}", 230, YEL, stroke=12)
        text(d, (540, 740), "◀◀  REBOBINANDO", 44, WHITE, stroke=5)
    return c

# ======================================================================= ACTO 2: 1996 (sepia)
def s_foto_96(T, t0, dur):
    c = bg("bg_mesa", T, t0, 1.05, 1.2, dur, .5, .5); dark(c, 110); glow(c, (60, 400, 1020, 1500), (255, 214, 140), 90, 90)
    k = zoom(T, t0, dur, .95, 1.12); put_img(c, foto(False), 540, 1000, .95 * k, rot=-3 + 2 * math.sin(T * .8))
    c = sep(c, T, .95)
    tx(c, T, WT("G09", "uña"), "UÑA Y CARNE", 540, RED, -5, 110)
    return c

def s_nitro_joven(T, t0, dur):
    c, pr = nave_c(830, 10)
    glow(c, (60, 700, 1020, 1500), (255, 200, 120), 80, 90)
    put(c, "motor", 880, 1330, .5)
    pj(c, pr, "nitro_full", -.6, 3.4, 2.1, T)
    c = cam(c, T, t0, dur, 1.0, 1.12, .4, .45); c = sep(c, T)
    tx(c, T, WT("G10", "diecinueve"), "19 AÑOS", 520, YEL, -5, 110)
    tx(c, T, WT("G10", "hijo."), "COMO A UN HIJO", 680, RED, 4, 80)
    return c

def s_madrugada(T, t0, dur):
    c, pr = nave_c(830, -10, 1.2)
    glow(c, (260, 800, 900, 1400), (255, 230, 150), 120, 60)
    put(c, "motor", 560, 1180, .95)
    chispas(c, T, t0, 560, 1000, 22, 700); chispas(c, T, t0 + 2.2, 640, 1010, 22, 700)
    c = cam(c, T, t0, dur, 1.0, 1.15, .5, .5); c = sep(c, T)
    tx(c, T, WT("G11", "madrugada"), "DE MADRUGADA", 540, YEL, -5, 96)
    return c

def s_noches(T, t0, dur):
    tw = WT("G11", "desaparecía"); c, pr = via(T, 0, 850, -6, "calle"); dark(c, 80)
    k = ease(clamp((T - tw) / 2.2)) ** 1.6
    trasera(c, pr, -.9 + .7 * k, 5.5 + 55 * k, 0.0 if k > .02 else .7, 1.0, "deportivo")
    c = sep(c, T, .8)
    tx(c, T, tw, "NITRO, DE NOCHE", 560, CYAN, -5, 90)
    return c

def s_rally(T, t0, dur):
    c, pr = via(T, 70, 840, 0, "puerto")
    sw = 1.1 * math.sin((T - t0) * 1.4)
    trasera(c, pr, -1.7 + .5 * sw, 11, 0, 1.0, "deportivo"); trasera(c, pr, 1.7 - .5 * sw, 13.5, 0, 1.0, "negro")
    P.lineas_velocidad(c, T)
    put(c, "trofeo", 880, 1350, .5 * popscale(T, WT("G12", "Ganaron"), .4))
    c = shake(c, T, 2.5, 48); c = sep(c, T, .85)
    tx(c, T, WT("G12", "Ganaron"), "RALLY '96", 540, YEL, -5, 120)
    tx(c, T, WT("G12", "conducía"), "ÉL CONDUCÍA", 720, CYAN, 4, 76)
    tx(c, T, WT("G12", "preparaba"), "RUBÉN, TODO LO DEMÁS", 880, RED, -3, 56)
    return c

def s_apuestas(T, t0, dur):
    c, pr = via(T, 0, 850, 14, "calle"); dark(c, 110); tinte(c, (90, 10, 20), 70)
    for i in range(10):   # corrillo a los lados de la salida
        sx = -1 if i % 2 == 0 else 1; sil(c, pr, "manolo_full", sx * (3.6 + (i // 2) * .5), 9 + (i // 2) * 3, 1.8, (6, 4, 10), flip=sx > 0)
    trasera(c, pr, -1.3, 11, 1.0, 1.0, "negro"); trasera(c, pr, 1.3, 11, 1.0, 1.0, "deportivo")
    glow(c, (40, 900, 1040, 1500), (255, 40, 60), 70 + 30 * math.sin(T * 6), 90)
    c = sep(c, T, .6)
    tx(c, T, WT("G13", "apostaba."), "APOSTABA", 540, RED, -5, 120)
    tx(c, T, WT("G13", "ilegales,"), "CARRERAS ILEGALES", 700, YEL, 4, 74)
    return c

def s_deuda(T, t0, dur):
    c, pr = nave_c(830, -8); dark(c, 120); tinte(c, (60, 0, 10), 60)
    k = ease(clamp((T - S("G14") - .5) / 2.4))
    c = sep(c, T, .7); d = ImageDraw.Draw(c)
    text(d, (540, 760), "-" + euros(int(64300 * k)), 150, (255, 120, 110), stroke=10)
    text(d, (540, 900), "DEUDA", 64, WHITE, stroke=6)
    tx(c, T, WT("G14", "avisa"), "NO AVISAN DOS VECES", 1130, RED, -4, 78)
    return c

def s_tres_hombres(T, t0, dur):
    c, pr = nave_c(830, 0); dark(c, 150); tinte(c, (70, 0, 10), 70)
    a, b = pr(-2.2, 15, 3.3), pr(2.2, 15, 0.0)
    glow(c, (int(a[0]) - 220, int(a[1]) - 60, int(b[0]) + 220, int(b[1]) + 200), (255, 230, 170), 150, 80)
    ImageDraw.Draw(c).rectangle((a[0], a[1], b[0], b[1]), fill=(255, 238, 190, 255))
    k = ease(clamp((T - t0) / 3.0))
    for i, xm in enumerate((-1.3, 0.0, 1.3)):
        sil(c, pr, "manolo_full", xm * (.5 + k * .9), 13 - 8.5 * k - (i == 1) * .8, 1.95, (3, 3, 6), flip=i == 2)
    c = shake(c, T, 3 + 5 * k, 40); c = cam(c, T, t0, dur, 1.0, 1.12, .5, .4); c = sep(c, T, .5)
    tx(c, T, WT("G15", "hombres"), "TRES HOMBRES", 540, RED, -5, 110)
    return c

def s_suplica(T, t0, dur):
    c, pr = nave_c(830, 6); dark(c, 130); tinte(c, (70, 0, 10), 55)
    for i, xm in enumerate((-2.0, 0.0, 2.0)): sil(c, pr, "manolo_full", xm, 9.0, 1.95, (3, 3, 6), flip=i == 2)
    pj(c, pr, "nitro_full", 0.0, 2.4, 2.1, T, "G16")
    c = cam(c, T, t0, dur, 1.0, 1.18, .5, .35); c = sep(c, T, .6)
    tx(c, T, WT("G16", "semana."), "UNA SEMANA", 540, YEL, -5, 110)
    return c

def s_venta(T, t0, dur):
    c, pr = nave_c(830, -12); glow(c, (260, 700, 900, 1400), (255, 220, 150), 110, 70)
    k = ease(clamp((T - WT("G17", "vendió.") + .3) / 1.2))
    put(c, "motor", 560 + 900 * k, 1150, 1.0 * (1 - .25 * k))
    d = ImageDraw.Draw(c)
    k2 = ease(clamp((T - WT("G17", "vendió.")) / 1.0))
    for i in range(int(6 * k2)):
        y = 1620 - i * 40; d.rounded_rectangle((200 + 6 * i, y, 880 + 6 * i, y + 36), 8, fill=(96, 168, 92), outline=OL, width=5)
    c = cam(c, T, t0, dur, 1.0, 1.12, .4, .5); c = sep(c, T)
    tx(c, T, WT("G17", "vendió."), "LO VENDIÓ", 540, YEL, -5, 120)
    tx(c, T, WT("G17", "prototipo…"), "EL PROTOTIPO", 700, RED, 4, 74)
    return c

def s_pago(T, t0, dur):
    c, pr = nave_c(830, 12); dark(c, 130)
    for i, xm in enumerate((-1.8, 0.0, 1.8)): sil(c, pr, "manolo_full", xm, 6.5, 1.95, (3, 3, 6), flip=i == 2)
    k = ease(clamp((T - WT("G18", "billete") + .2) / 2.0))
    ov = blank(); od = ImageDraw.Draw(ov)
    for i in range(14):
        p = clamp(k * 1.4 - i * .05); x = 150 + 750 * p; y = 1500 - 700 * p + 90 * math.sin(i + T * 4)
        od.rounded_rectangle((x, y, x + 140, y + 66), 8, fill=(96, 168, 92, 255), outline=OL + (255,), width=4)
    c.alpha_composite(ov); c = sep(c, T, .8)
    d = ImageDraw.Draw(c); text(d, (540, 700), "-" + euros(int(64300 * (1 - k))), 120, (255, 120, 110) if k < 1 else (120, 240, 150), stroke=9)
    tx(c, T, WT("G18", "deuda"), "DEUDA PAGADA", 900, YEL, -4, 96)
    return c

def s_socios(T, t0, dur):
    c = bg("bg_mesa", T, t0, 1.1, 1.3, dur, .5, .5); dark(c, 100); glow(c, (60, 400, 1020, 1500), (255, 214, 140), 90, 90)
    k = popscale(T, WT("G19", "mitad"), .5); d = ImageDraw.Draw(c); cx, cy, r = 540, 960, 280 * max(k, .05)
    d.pieslice((cx - r, cy - r, cx + r, cy + r), -90, 90, fill=(60, 140, 230), outline=OL, width=8)
    d.pieslice((cx - r, cy - r, cx + r, cy + r), 90, 270, fill=(236, 190, 70), outline=OL, width=8)
    if k > .9: text(d, (cx + 150, cy), "50%", 96, WHITE, stroke=8); text(d, (cx - 150, cy), "50%", 96, OL, stroke=0)
    put_img(c, foto(False), 540, 1500, .42, rot=-4)
    c = sep(c, T, .9)
    tx(c, T, WT("G19", "socios,"), "SOCIOS", 520, YEL, -5, 116)
    return c

def s_contrato(T, t0, dur):
    c = bg("bg_mesa", T, t0, 1.2, 1.5, dur, .5, .5); dark(c, 90); glow(c, (60, 400, 1020, 1500), (255, 214, 140), 110, 90)
    k = ease(clamp((T - WT("G20", "testigo.") + .2) / .6))
    papel(c, 540, 1030, .98 * zoom(T, t0, dur, 1.0, 1.1), rot=-3, firmas=3 if k > .5 else 2, resalta=k > .5, T=T, final=False)
    c = sep(c, T, .9)
    tx(c, T, WT("G20", "firmas…"), "DOS FIRMAS", 400, YEL, -5, 110)
    tx(c, T, WT("G20", "testigo."), "…Y UN TESTIGO", 560, RED, 4, 84)
    return c

# ======================================================================= ACTO 3: de vuelta al presente
def s_pregunta_lucia(T, t0, dur):
    return s_lucia_nave("G21", -.3, 3.2, 16, 1.0, 1.1, (("dijisteis?", "¿POR QUÉ CALLASTEIS?", 560, YEL),))(T, t0, dur)

def s_exterior_esc(T, t0, dur):
    tw = S("G23")
    c = bg("bg_fachada", T, t0, 1.1, 1.3, dur, .5, .6); dark(c, 90); tinte(c, (10, 20, 70), 55)
    glow(c, (300, 960, 760, 1240), (255, 215, 140), 90, 50)                                  # luz por la rendija de la puerta
    ov = blank(); ImageDraw.Draw(ov).rectangle((520, 1000, 560, 1260), fill=(255, 235, 180, 200)); c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(3)))
    k = zoom(T, t0, dur, .9, 1.05)
    im = R.layer("nitro_full"); im = im.crop(im.getbbox()); h = int(980 * k); w = int(im.width * h / im.height); sp = im.resize((w, h), Image.LANCZOS)
    blk = Image.new("RGBA", sp.size, (4, 4, 8, 255)); blk.putalpha(sp.getchannel("A")); c.alpha_composite(blk, (620 - w // 2, 1560 - h))
    lluvia(c, T, 120, 130, 1400); vineta(c, 220)
    tx(c, T, WT("G23", "escucha"), "ALGUIEN ESCUCHA", 540, RED, -5, 96)
    return c

def s_puño(T, t0, dur):
    c = bg("bg_fachada", T, t0, 1.6, 1.8, dur, .5, .6); dark(c, 130); tinte(c, (60, 0, 20), 70)
    glow(c, (200, 700, 880, 1500), (255, 40, 40), 100 + 30 * math.sin(T * 6), 90)
    k = zoom(T, t0, dur, 1.4, 1.9); guante(c, 540, 1200, 1.0 * k, rot=8, cerrado=T >= WT("G24", "puño."))
    c = shake(c, T, 3 + 6 * clamp((T - WT("G24", "puño.")) / .3), 44); lluvia(c, T, 90, 100, 1400); vineta(c, 220)
    tx(c, T, WT("G24", "sombra"), "UNA SOMBRA", 540, RED, -4, 110)
    return c

def s_se_lleva(T, t0, dur):
    tr = WT("G25", "ruge"); tl = WT("G25", "coche.") - .2
    go = ease(clamp((T - tl) / 1.8)) ** 1.7
    c, pr = via(T, 0, 850, -8, "calle"); dark(c, 90); tinte(c, (10, 20, 70), 50)
    rev = .02 * math.sin(T * 60) if tr <= T < tl else 0
    trasera(c, pr, .3 - .2 * go + rev, 5.0 + 60 * go, 1.0 if T < tl else .1, 1.0, "negro")
    if tr <= T < tl + .5: humo(c, T, tr, 560, 1290, 1.4, 6)
    llamas(c, T, tr + .3, 600, 1290, 2, .38, .8)
    lluvia(c, T, 90, 100, 1400); suelo_niebla(c)
    tx(c, T, tr, "¡RUGE!", 560, RED, -6, 120)
    tx(c, T, WT("G25", "oído"), "LO HA OÍDO TODO", 790, YEL, 4, 70)
    return c

def s_espera(T, t0, dur):
    c, pr = nave_c(830, 0); a, b = pr(-2.2, 15, 3.3), pr(2.2, 15, 0)
    ImageDraw.Draw(c).rectangle((a[0], a[1], b[0], b[1]), fill=(70, 100, 170, 255))
    ov = blank(); lluvia(ov, T, 40, 120, 900, int(a[0]), int(b[0]), int(a[1]), int(b[1])); c.alpha_composite(ov)
    pj(c, pr, "manolo_full", .3, 3.1, 2.0, T, "G26"); pj(c, pr, "lucia_full", -1.9, 5.0, 2.0, T, None)
    c = shake(c, T, 5, 40); c = cam(c, T, t0, dur, 1.0, 1.18, .5, .4); tinte(c, (20, 30, 90), 35)
    tx(c, T, WT("G26", "espera!"), "¡NITRO, ESPERA!", 540, RED, -5, 96)
    return c

def s_seat_no(T, t0, dur):
    tk = WT("G27", "arranca,") - .1
    c, pr = nave_c(830, -12); glow(c, (60, 700, 1020, 1500), (255, 200, 120), 60, 90)
    P.coche_34(c, 230, 1010, .5, lado=-1, fuerza=.16, capa="deportivo"); dark_ = blank(); ImageDraw.Draw(dark_).rectangle((0, 0, 460, H), fill=(0, 0, 0, 70)); c.alpha_composite(dark_)
    P.coche_34(c, 700, 1230 + 2.5 * math.sin(T * 48), .8, lado=1, fuerza=.18, capa="seat_rally")
    pj(c, pr, "lucia_full", .85, 3.4, 2.0, T, "G27", True)
    c = cam(c, T, t0, dur, 1.0, 1.1, .5, .45); tinte(c, (20, 30, 90), 30)
    if T >= tk: stamp(c, T, tk, "NO ARRANCA", 330, 640, RED, -5, 74)
    if T >= WT("G27", "Seat"): stamp(c, T, WT("G27", "Seat"), "EL SEAT, SÍ", 700, 520, YEL, 4, 86)
    return c

def s_contacto(T, t0, dur):
    c, pr = via(T, 0 if T < S("G28") + 2.3 else 22, 850, 0, "calle"); dark(c, 60)
    c = cabina(c, T, 0, True, 1)
    c = shake(c, T, 2.5, 52)
    tx(c, T, WT("G28", "Contacto,"), "CONTACTO", 560, CYAN, -5, 96)
    tx(c, T, WT("G28", "primera…"), "PRIMERA", 740, YEL, 4, 84)
    return c

def s_persigue(modo, lid, tw=None, txt=None, v=36, giro_a=22, lejos=26.0, cerca=14.0, f=1.0):
    def fn(T, t0, dur):
        k = ease(clamp((T - t0) / max(dur, 1)))
        giro = giro_a * math.sin(T * .9 * f) + (60 * math.sin(T * 1.3) if modo == "montana" else 0)
        c, pr = via(T, v, 850, giro, modo)
        z = lejos + (cerca - lejos) * k
        trasera(c, pr, .4 * math.sin(T * .9 * f), z, 0.0)
        c = cabina(c, T, -giro * .45, True, 1)
        if modo == "montana": c = c.rotate(2.8 * math.sin(T * .9 * f), center=(540, 1500), resample=Image.BILINEAR)
        c = shake(c, T, 3, 50); c = tinte(c, (10, 20, 70), 30) or c
        if txt: tx(c, T, WT(lid, tw), txt, 560, YEL, -5, 110)
        return c
    return fn

def s_curvas(T, t0, dur):
    tw = [WT("G35", "Cuatro"), WT("G35", "derrapa,"), WT("G35", "parachoques…"), WT("G35", "alcanzas.")]
    n = sum(T >= t for t in tw[:3])
    giro = 150 * math.sin((T - t0) * 3.2)
    c, pr = via(T, 44, 850, giro, "montana")
    p = clamp((T - tw[1]) / 1.6)
    trasera(c, pr, 0, 15 - 8 * p, 1.0 if p > .85 else 0)
    ov = blank(); od = ImageDraw.Draw(ov)
    for i in range(7):
        r = 80 + i * 22; x = 380 + i * 60 + 50 * math.sin(T * 5 + i); od.ellipse((x - r, 1540 - r * .5, x + r, 1540 + r * .5), fill=(225, 225, 235, int(110 * (1 - i / 8))))
    if T >= tw[1] - .1 and T < tw[2] + .6: c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(14)))
    c = cabina(c, T, -giro * .35, True, 1) if T >= tw[2] - .1 else c
    c = c.rotate(5 * math.sin((T - t0) * 3.2), center=(540, 1500), resample=Image.BILINEAR)
    c = shake(c, T, 5, 55)
    if T >= tw[0] and T < tw[1] + .8: tx(c, T, tw[0], "4 CURVAS", 560, YEL, -5, 120)
    if T >= tw[1]: tx(c, T, tw[1], "¡DERRAPA!", 740, RED, 5, 110)
    if T >= tw[3] - .1: tx(c, T, tw[3] - .1, "¡LO ALCANZAS!", 980, CYAN, -4, 84)
    return c

def s_frena(T, t0, dur):
    tw = WT("G36", "detienen."); c, pr = via(T, 0 if T > tw else 30, 850, 0, "montana")
    zz = 14 + 2 * (1 - clamp((T - t0) / dur)); trasera(c, pr, 0, zz, 1.0)
    c = cabina(c, T, 0, True, 0); tinte(c, (60, 0, 10), 25 * (T >= WT("G36", "luces")))
    tx(c, T, WT("G36", "rojas"), "LUCES ROJAS", 560, RED, -5, 104)
    return c

def s_mirador(T, t0, dur):
    tx_ = WT("G36", "mirador.") if T < S("G37") else 0
    c, pr = mirador_p()
    P.coche_34(c, 720, 1210, .78, lado=1, fuerza=.2, capa="coche_negro")
    P.coche_34(c, 280, 1310, .6, lado=-1, fuerza=.16, capa="seat_rally")
    humo(c, T, S("G36"), 650, 1250, 1.2, 4)
    lluvia(c, T, 120, 130, 1400); c = cam(c, T, t0, dur, 1.0, 1.1, .5, .5); vineta(c, 200); tinte(c, (10, 20, 70), 35)
    et(c, T, WT("G36", "mirador."), "EL MIRADOR", 560, WHITE, 56)
    return c

def s_nitro_baja(T, t0, dur):
    c, pr = mirador_p()
    P.coche_34(c, 780, 1130, .7, lado=1, fuerza=.2, capa="coche_negro")
    k = ease(clamp((T - t0) / 2.5)); pj(c, pr, "nitro_full", 1.2 - 2.2 * k, 6.5 - 2.4 * k, 2.1, T)
    papel(c, 340 + 0 * k, 1000, .22 + .16 * k, rot=-8, firmas=2, T=T)
    lluvia(c, T, 120, 130, 1400); c = cam(c, T, t0, dur, 1.0, 1.12, .5, .5); vineta(c, 210); tinte(c, (10, 20, 70), 35)
    tx(c, T, WT("G37", "papel"), "UN PAPEL", 560, RED, -5, 110)
    return c

def s_silencio(T, t0, dur):
    c, pr = mirador_p()
    P.coche_34(c, 720, 1210, .78, lado=1, fuerza=.2, capa="coche_negro"); P.coche_34(c, 280, 1310, .6, lado=-1, fuerza=.16, capa="seat_rally")
    pj(c, pr, "nitro_full", -1.0, 7.0, 2.1, T); pj(c, pr, "lucia_full", 2.2, 5.5, 2.0, T, None, True)
    humo(c, T, S("G38") - 1, 600, 1240, 1.0, 3); humo(c, T, S("G38") - .5, 300, 1330, 1.0, 3)
    lluvia(c, T, 140, 140, 1300); c = cam(c, T, t0, dur, 1.0, 1.1, .5, .5); vineta(c, 220); tinte(c, (10, 20, 70), 45)
    return c

def s_nitro_habla(lid, z=3.3, x=-.2, giro=8, z1=1.15, txts=(), tin=None):
    z = 3.3
    def fn(T, t0, dur):
        c, pr = mirador_p()
        P.coche_34(c, 840, 1050, .5, lado=1, fuerza=.2, capa="coche_negro")
        c = c.filter(ImageFilter.GaussianBlur(5))                                  # fondo desenfocado (profundidad de campo)
        pj(c, pr, "nitro_full", x, z, 2.1, T, lid)
        lluvia(c, T, 110, 130, 1300); c = cam(c, T, t0, dur, 1.0, z1, .45, .4); vineta(c, 220); tinte(c, tin or (10, 20, 70), 35)
        for tw, s_, y, col in txts: tx(c, T, WT(lid, tw), s_, y, col, -5, 88)
        return c
    return fn

def s_otra_mitad(T, t0, dur):
    c = bg("bg_mesa", T, t0, 1.2, 1.4, dur, .5, .5); dark(c, 100); glow(c, (60, 400, 1020, 1500), (255, 214, 140), 110, 90); tinte(c, (10, 20, 70), 35)
    k = ease(clamp((T - t0) / .8))
    papel(c, 300 - 220 * (1 - k), 560, .5, rot=-12, firmas=2, T=T)
    mitad_papel(c, 640, 1060, .62 + .04 * zoom(T, t0, dur, 0, 1), rot=-4 + 2 * math.sin(T * 3), T=T)
    c = vineta(c, 200) or c
    tx(c, T, WT("G42", "otra"), "LA OTRA MITAD", 420, YEL, -5, 100)
    return c

def s_firma_macro(T, t0, dur):
    c = bg("bg_mesa", T, t0, 1.4, 1.7, dur, .5, .5); dark(c, 80); tinte(c, (70, 10, 20), 40)
    glow(c, (60, 400, 1020, 1500), (255, 214, 140), 110, 90)
    mitad_papel(c, 540, 1250, 1.1 * zoom(T, t0, dur, 1.0, 1.22), rot=2, T=T, resalta=True)
    c = shake(c, T, 3, 40); vineta(c, 200)
    tx(c, T, WT("G43", "firma"), "LA FIRMA", 400, YEL, -5, 110)
    tx(c, T, WT("G43", "Rubén."), "NO ES DE RUBÉN", 560, RED, 4, 84)
    return c

def s_letra(T, t0, dur):
    c, pr = nave_c(830, 16); glow(c, (60, 700, 1020, 1500), (255, 200, 120), 60, 90)
    pj(c, pr, "lucia_full", .2, 2.7, 2.1, T, "G44"); c = cam(c, T, t0, dur, 1.0, 1.2, .5, .3); tinte(c, (20, 30, 90), 40); vineta(c, 190)
    tx(c, T, WT("G44", "antes."), "LA HA VISTO ANTES", 540, YEL, -4, 84)
    return c

def s_clausula(T, t0, dur):
    c = bg("bg_mesa", T, t0, 1.3, 1.5, dur, .5, .5); dark(c, 80); tinte(c, (70, 10, 20), 45); glow(c, (60, 400, 1020, 1500), (255, 214, 140), 110, 90)
    mitad_papel(c, 540, 1000, 1.0, rot=0, T=T)
    txt = "SI RUBÉN MUERE,\nEL TALLER PASA ENTERO\nA QUIEN FIRMA AQUÍ"
    k = clamp((T - WT("G45", "secreta.")) / 2.6); n = int(len(txt) * k)
    panel(c, (110, 700, 970, 1130), fill=(20, 6, 10), alpha=230, rad=26, outline=RED, ow=6); d = ImageDraw.Draw(c)
    for i, ln in enumerate(txt[:n].split("\n")): text(d, (540, 790 + i * 120), ln, 62, (255, 200, 190), stroke=5)
    c = vineta(c, 200) or c
    tx(c, T, WT("G45", "secreta."), "CLÁUSULA SECRETA", 420, RED, -5, 96)
    return c

def s_ni_mia(T, t0, dur):
    return s_nitro_habla("G46", 2.3, .1, -6, 1.22, (("firma.", "NI LA SUYA, NI LA MÍA", 540, RED),), (60, 10, 20))(T, t0, dur)

def s_alguien(T, t0, dur):
    c, pr = nave_c(830, 0); dark(c, 140); tinte(c, (70, 0, 10), 70)
    glow(c, (120, 600, 960, 1700), (255, 60, 60), 80 + 30 * math.sin(T * 5), 100)
    k = ease(clamp((T - t0) / dur))
    ix, iy, w, h = sil(c, pr, "manolo_full", 0, 9.0 - 4.5 * k, 2.1, (4, 4, 8))
    for ex in (-.1, .1): ImageDraw.Draw(c).ellipse((ix + w // 2 + ex * w - 7, iy + h * .12, ix + w // 2 + ex * w + 7, iy + h * .12 + 12), fill=(255, 70, 70))
    c = shake(c, T, 2, 40); c = cam(c, T, t0, dur, 1.0, 1.15, .5, .4); vineta(c, 210)
    tx(c, T, WT("G47", "Alguien"), "¿QUIÉN?", 540, RED, -5, 130)
    return c

def s_luz_taller(T, t0, dur):
    tw = WT("G48", "enciende."); c, pr = mirador_p()
    d = ImageDraw.Draw(c); bx, by = 700, 1080
    d.rectangle((bx - 190, by - 150, bx + 190, by + 60), fill=(14, 12, 22)); d.polygon([(bx - 210, by - 150), (bx + 210, by - 150), (bx, by - 260)], fill=(14, 12, 22))
    on = ease(clamp((T - tw + .3) / .4))
    for wx in (-110, 40):
        d.rectangle((bx + wx - 10, by - 90, bx + wx + 70, by - 10), fill=(int(30 + 225 * (on if wx > 0 else 0)), int(28 + 180 * (on if wx > 0 else 0)), int(26 + 100 * (on if wx > 0 else 0))))
    glow(c, (bx - 300, by - 300, bx + 300, by + 160), (255, 210, 120), int(160 * on), 50)
    sil(c, pr, "nitro_full", -.9, 4.6, 2.1, (4, 4, 8)); sil(c, pr, "lucia_full", 1.0, 4.3, 2.0, (4, 4, 8), flip=True)
    lluvia(c, T, 120, 130, 1300); c = cam(c, T, t0, dur, 1.0, 1.25, .62, .6); vineta(c, 220); tinte(c, (10, 20, 70), 40)
    tx(c, T, WT("G48", "luz"), "UNA LUZ", 520, YEL, -5, 110)
    return c

def s_tu_eliges(T, t0, dur):
    return s_nitro_habla("G49", 2.3, .0, 4, 1.22, (("eliges:", "TÚ ELIGES", 520, YEL),))(T, t0, dur)

def lado9(name):
    key = "L9" + name
    if key in _LC: return _LC[key]
    if name == "A":
        A = bg("bg_mesa", 0, 0, 1.2, 1.2, 1, .5, .5).convert("RGBA"); dark(A, 90); glow(A, (0, 500, 1000, 1500), AZ, 80, 80)
        mitad_papel(A, 300, 1250, .62, rot=-8, T=0, resalta=False)
    else:
        A, pr = nave_c(830, 0); A = A.convert("RGBA"); dark(A, 130); A.alpha_composite(Image.new("RGBA", (W, H), (60, 10, 50, 60)))
        pj(A, pr, "manolo_full", 1.6, 4.0, 2.0, 0, None, True)
    _LC[key] = A; return A

def s_split(T, t0, dur):
    s0 = WT("G50", "Leer") - .1
    A, B = lado9("A"), lado9("B")
    u = ease((T - s0 + .25) / .45); tb = WT("G50", "volver") - .05; tn = S("G51") - .05
    hiA = T < tb; neutro = T >= tn
    blk = Image.new("RGBA", (W, H), (0, 0, 0, 255)); c = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    c.alpha_composite(B if (neutro or not hiA) else Image.blend(B, blk, .45), (int(500 * (1 - u)), 0))
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon([(0, 0)] + RAYO + [(0, H)], fill=255)
    c.paste(A if (neutro or hiA) else Image.blend(A, blk, .45), (int(-700 * (1 - u)), 0), mask)
    d = ImageDraw.Draw(c)
    if u > .9:
        v = .6 + .4 * abs(math.sin(T * 13)) * abs(math.sin(T * 3.1))
        gl = blank(); ImageDraw.Draw(gl).line(RAYO, fill=CYAN + (int(255 * v),), width=40, joint="curve")
        c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(c)
        d.line(RAYO, fill=WHITE, width=12, joint="curve"); d.line(RAYO, fill=CYAN, width=5, joint="curve")
    for cx, t1, t2, t3, col in ((270, "LEER", "+ Descubres la firma", "- Nitro se escapa", AZ), (790, "VOLVER", "+ Pillas al firmante", "- No lees la firma", MAG)):
        k = popscale(T, s0 + .2, .35)
        if k > 0: opcion8(d, cx, 420, t1, t2, t3, col, k)
    boton_seguir(c, T, WT("G51", "sígueme"))
    return c

# ======================================================================= ESCENAS NUEVAS (Ep.10 "Cara a cara")
def silf(c, name, cx, base, h, flip=False, col=(4, 4, 8)):
    im = R.layer(name); im = im.crop(im.getbbox()); w = int(im.width * h / im.height); sp = im.resize((w, h), Image.LANCZOS)
    if flip: sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
    blk = Image.new("RGBA", sp.size, col + (255,)); blk.putalpha(sp.getchannel("A")); c.alpha_composite(blk, (cx - w // 2, base - h))

def fachada(T, t0, dur, ab=0.0, z0=1.1, z1=1.3):
    c = bg("bg_fachada", T, t0, z0, z1, dur, .5, .6); dark(c, 90); tinte(c, (10, 20, 70), 55)
    glow(c, (300, 960, 760, 1240), (255, 215, 140), int(90 + 70 * ab), 50)
    ov = blank(); ImageDraw.Draw(ov).rectangle((540 - 20 - int(110 * ab), 1000, 540 + 20 + int(110 * ab), 1260), fill=(255, 235, 180, 210)); c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(4)))
    return c

def sombrero(c, cx, cy, w, ang=0):
    lay = Image.new("RGBA", (int(w * 2.4), int(w * 1.4)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); m, n = lay.width // 2, lay.height // 2
    d.ellipse((m - w, n - w * .13, m + w, n + w * .13), fill=(24, 22, 28, 255), outline=(8, 8, 12, 255), width=3)
    d.rounded_rectangle((m - w * .62, n - w * .6, m + w * .62, n), int(w * .2), fill=(34, 32, 40, 255), outline=(8, 8, 12, 255), width=3)
    d.rectangle((m - w * .61, n - w * .18, m + w * .61, n - w * .02), fill=(120, 38, 38, 255))
    lay = lay.rotate(ang, expand=True, resample=Image.BICUBIC); c.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def padre(c, pr, T, x, z, alto, lid=None, hat=True, flip=False):
    return pj(c, pr, "padre_full" if hat else "padre_sin_sombrero", x, z, alto, T, lid, flip)

def mensaje(c, T, t0, t1, user, txt):
    if not (t0 <= T < t1): return
    k = popscale(T, t0, .35)
    if T > t1 - .3: k *= clamp((t1 - T) / .3)
    if k <= 0: return
    lay = blank(); d = ImageDraw.Draw(lay); x0, y0, x1, y1 = 90, 690, 990, 930
    d.rounded_rectangle((x0, y0, x1, y1), 38, fill=(255, 255, 255, 245), outline=OL, width=6)
    d.ellipse((x0 + 28, y0 + 30, x0 + 108, y0 + 110), fill=(60, 120, 230), outline=OL, width=4)
    d.text((x0 + 68, y0 + 70), user[0].upper(), font=R.font(F_ANTON, 44), fill=WHITE, anchor="mm")
    d.text((x0 + 130, y0 + 48), "@" + user, font=R.font(F_ANTON, 38), fill=OL, anchor="lm")
    d.text((x0 + 130, y0 + 90), "MENSAJE NUEVO", font=R.font(F_UI, 24), fill=(200, 50, 50), anchor="lm")
    f = R.font(F_UI, 36); words = txt.split(); lines = []; cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) > x1 - x0 - 70: lines.append(cur); cur = w
        else: cur = t
    lines.append(cur)
    for i, l in enumerate(lines): d.text((x0 + 35, y0 + 140 + i * 44), l, font=f, fill=OL, anchor="lm")
    if abs(k - 1) > .01:
        cx, cy = 540, (y0 + y1) // 2
        big = lay.resize((max(1, int(W * k)), max(1, int(H * k))), Image.BILINEAR); ox, oy = int(cx - cx * k), int(cy - cy * k)
        lay = blank(); lay.alpha_composite(big, (max(0, ox), max(0, oy)), (max(0, -ox), max(0, -oy)))
    c.alpha_composite(lay)

# ---- 1. la patada (frame 0 ya es acción)
def s_patada(T, t0, dur):
    tp = WT("G01", "patada.")
    ab = ease(clamp((T - t0 + .4) / .5)) if T < tp else 1.0
    c = fachada(T, t0, dur, max(.55, ab), 1.15, 1.7)
    k = zoom(T, t0, dur, .95, 1.1)
    silf(c, "nitro_full", int(300), 1650, int(900 * k)); silf(c, "lucia_full", 800, 1650, int(840 * k), flip=True)
    if T >= tp:
        u = clamp((T - tp) / .35); fl = Image.new("RGBA", (W, H), (255, 240, 200, int(170 * (1 - u)))); c.alpha_composite(fl)
    lluvia(c, T, 110, 120, 1400); vineta(c, 220); c = shake(c, T, 3 + 6 * (T >= tp and T < tp + .4), 44)
    if T < tp + .8: et(c, T, .12, "ELEGISTEIS LA A", 440, YEL, 46)
    mensaje(c, T, .5, tp - .35, "danineos100", "Toca plantarle cara y enterarse de toda la historia")
    tx(c, T, tp, "¡A PATADA!", 600, RED, -5, 128)
    return c

# ---- 2. grito
def s_grito(T, t0, dur):
    c, pr = nave_c(830, 6); dark(c, 120); tinte(c, (60, 20, 10), 45)
    glow(c, (60, 700, 1020, 1700), (255, 190, 90), 70 + 20 * math.sin(T * 9), 90)
    ix, iy, w, h = sil(c, pr, "padre_sin_sombrero", .45, 6.6, 2.0, (4, 4, 8)); hat(c, ix, iy + int(h * .02), int(w * .42))
    pj(c, pr, "nitro_full", -.5, 3.0, 2.1, T, "G02")
    c = shake(c, T, 3, 44); c = cam(c, T, t0, dur, 1.0, 1.18, .45, .4); vineta(c, 210)
    tx(c, T, S("G02") + .12, "¡SUELTE ESE CAJÓN!", 400, RED, -4, 84)
    return c

def hat(c, cx, cy, w):
    d = ImageDraw.Draw(c); d.ellipse((cx - w, cy - 14, cx + w, cy + 14), fill=(4, 4, 8)); d.rounded_rectangle((cx - w * .55, cy - 70, cx + w * .55, cy), 14, fill=(4, 4, 8))

# ---- 3. se quita el sombrero
def s_sombrero(T, t0, dur):
    ts = WT("G03", "sombrero")
    c, pr = nave_c(830, 0); dark(c, 120); tinte(c, (70, 10, 10), 45)
    glow(c, (120, 500, 960, 1800), (255, 200, 120), 110, 110)
    k = ease(clamp((T - t0) / dur))
    info = padre(c, pr, T, .15, 4.9 - .9 * k, 2.1, None, hat=T < ts + .05)
    f = info["f"]
    if T >= ts + .05:
        u = ease(clamp((T - ts - .05) / .5)); hx = info["x0"] + (799 - info["ox"]) * f; hy = info["y0"] + (700 - info["oy"]) * f
        sombrero(c, hx - 430 * u * f, hy + 1330 * u * f, 330 * f, -20 * u)
    c = cam(c, T, t0, dur, 1.0, 1.22, .5, .35); c = shake(c, T, 2, 40); vineta(c, 215)
    tx(c, T, WT("G03", "inmuta."), "NI SE INMUTA", 400, YEL, -5, 100)
    return c

def s_sonrie(T, t0, dur):
    c, pr = nave_c(830, 0); dark(c, 120); tinte(c, (70, 0, 10), 55)
    glow(c, (120, 500, 960, 1800), (255, 200, 120), 130, 110)
    info = padre(c, pr, T, .1, 4.0, 2.2, None, hat=False)
    f = info["f"]; mx = info["x0"] + (799 - info["ox"]) * f; my = info["y0"] + (1128 - info["oy"]) * f
    d = ImageDraw.Draw(c); u = ease(clamp((T - t0) / .35))
    d.arc((mx - 60 * f * 1.4, my - 40 * f, mx + 60 * f * 1.4, my + 30 * f * (1 + u)), 20, 160, fill=(40, 14, 14), width=max(3, int(10 * f)))
    c = cam(c, T, t0, dur, 1.35, 1.75, .5, .17); vineta(c, 235)
    tx(c, T, t0 + .1, "SONRÍE…", 1420, RED, -4, 110)
    return c

# ---- 4. "Llegáis tarde"
def s_tarde(T, t0, dur):
    c, pr = nave_c(830, -6); dark(c, 110); tinte(c, (20, 30, 90), 30)
    glow(c, (60, 600, 1020, 1700), (255, 200, 120), 80, 90)
    sil(c, pr, "nitro_full", -.9, 2.8, 2.0, (4, 4, 8)); sil(c, pr, "lucia_full", -.2, 3.2, 1.9, (4, 4, 8), True)
    padre(c, pr, T, .7, 4.6 - .5 * ease(clamp((T - t0) / dur)), 2.1, "G04", hat=False, flip=True)
    c = cam(c, T, t0, dur, 1.0, 1.2, .6, .4); vineta(c, 215)
    tx(c, T, S("G04") + .15, "LLEGÁIS TARDE", 400, YEL, -4, 98)
    return c

# ---- 5. Lucía
def s_lucia10(T, t0, dur):
    c, pr = nave_c(830, 12); dark(c, 100); tinte(c, (60, 0, 20), 50)
    silf(c, "padre_sin_sombrero", 800, 1500, 1500, True, (10, 8, 14))
    pj(c, pr, "lucia_full", -.2, 2.5, 2.2, T, "G05")
    c = cam(c, T, t0, dur, 1.1, 1.4, .45, .3); c = shake(c, T, 2, 40); vineta(c, 230)
    tx(c, T, S("G05") + .1, "¡PAPÁ!", 380, RED, -4, 140)
    return c

# ---- 6. el pacto
def s_pacto(T, t0, dur):
    c, pr = nave_c(830, 0); dark(c, 120); tinte(c, (70, 10, 10), 40)
    glow(c, (120, 500, 960, 1800), (255, 200, 120), 110, 110)
    padre(c, pr, T, .1, 4.3 - .6 * ease(clamp((T - t0) / dur)), 2.1, "G06", hat=False)
    tp = WT("G06", "pacto")
    if T >= tp - .1:
        k = popscale(T, tp - .1, .35)
        if k > 0: papel(c, 800, 1350, .62 * k, rot=8, firmas=3, resalta=True, T=T)
    c = cam(c, T, t0, dur, 1.0, 1.15, .5, .4); vineta(c, 215)
    tx(c, T, tp, "FIRMÓ EL PACTO", 400, YEL, -4, 92)
    return c

# ---- 7. la deuda
def s_deuda(T, t0, dur):
    c, pr = nave_c(830, 8); dark(c, 110); tinte(c, (60, 0, 20), 50)
    glow(c, (60, 700, 1020, 1500), (255, 200, 120), 60, 90)
    sil(c, pr, "padre_sin_sombrero", 1.0, 6.0, 2.0, (4, 4, 8), True)
    pj(c, pr, "nitro_full", -.3, 3.1, 2.1, T, "G07")
    c = cam(c, T, t0, dur, 1.0, 1.18, .45, .4); vineta(c, 215)
    tx(c, T, WT("G07", "deuda"), "-64.300 €", 400, RED, -5, 140)
    return c

# ---- 8. la llave
def llave(c, x, y, s, ang):
    lay = Image.new("RGBA", (520, 220), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); o = (60, 30, 10, 255); m = (176, 120, 60, 255)
    d.ellipse((10, 50, 130, 170), fill=m, outline=o, width=8); d.ellipse((46, 86, 94, 134), fill=(0, 0, 0, 0), outline=o, width=8)
    d.rectangle((126, 96, 430, 124), fill=m, outline=o, width=8)
    for xx in (360, 400): d.rectangle((xx, 120, xx + 24, 170), fill=m, outline=o, width=6)
    lay = lay.rotate(ang, expand=True, resample=Image.BICUBIC); lay = lay.resize((int(lay.width * s), int(lay.height * s)), Image.LANCZOS)
    c.alpha_composite(lay, (int(x - lay.width / 2), int(y - lay.height / 2)))

def s_llave(T, t0, dur):
    tl = WT("G08", "llave")
    c = bg("bg_mesa", T, t0, 1.3, 1.6, dur, .5, .5); dark(c, 100); tinte(c, (60, 20, 10), 35)
    glow(c, (60, 500, 1020, 1500), (255, 200, 130), 110, 90)
    u = ease(clamp((T - tl + .25) / .3)); y = -200 + 1480 * u
    if T > tl + .05: y = 1480 - 22 * abs(math.sin((T - tl - .05) * 18)) * math.exp(-(T - tl) * 4)
    llave(c, 540, y, 1.5 + .2 * math.sin(T * 3) * (T > tl + .2), -22)
    if T >= tl + .05:
        k = clamp((T - tl - .05) / .5); d = ImageDraw.Draw(c)
        for i in range(8): d.ellipse((540 + (i - 4) * 70 * k - 8, 1520 - 40 * k * ((i * 7) % 5) / 4 - 8, 540 + (i - 4) * 70 * k + 8, 1520 - 40 * k * ((i * 7) % 5) / 4 + 8), fill=(255, 220, 160, 200))
    c = shake(c, T, 6 * (tl <= T < tl + .25), 40); vineta(c, 200)
    tx(c, T, WT("G08", "oxidada"), "UNA LLAVE VIEJA", 520, YEL, -4, 96)
    return c

# ---- 9. la deuda del 96
def s_del96(T, t0, dur):
    c, pr = nave_c(830, -4); dark(c, 130); tinte(c, (80, 0, 10), 70)
    glow(c, (120, 500, 960, 1800), (255, 120, 80), 110, 110)
    sil(c, pr, "nitro_full", -.9, 2.7, 2.0, (4, 4, 8)); sil(c, pr, "lucia_full", -.25, 3.2, 1.9, (4, 4, 8), True)
    padre(c, pr, T, .5, 4.4 - .5 * ease(clamp((T - t0) / dur)), 2.1, "G09", hat=False, flip=True)
    c = cam(c, T, t0, dur, 1.0, 1.2, .6, .4); vineta(c, 225)
    tx(c, T, WT("G09", "noventa"), "DESDE EL 96", 400, RED, -4, 110)
    return c

# ---- 10. faros fuera
def s_faros(T, t0, dur):
    c = fachada(T, t0, dur, 1.0, 1.1, 1.25); dark(c, 40); tn = WT("G10", "coches")
    for i, (cx, d0) in enumerate(((220, 0), (540, .35), (860, .7))):
        k = ease(clamp((T - t0 - d0) / 1.6)); r = 18 + 90 * k; yy = 1330 - 30 * k
        for dx in (-1, 1):
            xx = cx + dx * (60 + 120 * k)
            glow(c, (xx - r * 3, yy - r * 2, xx + r * 3, yy + r * 2), (255, 240, 200), int(110 + 90 * k), 40)
            ImageDraw.Draw(c).ellipse((xx - r * .5, yy - r * .35, xx + r * .5, yy + r * .35), fill=(255, 252, 235))
    silf(c, "nitro_full", 250, 1900, 820); silf(c, "lucia_full", 840, 1900, 770, flip=True)
    lluvia(c, T, 120, 130, 1400); vineta(c, 215); c = shake(c, T, 2 + 3 * (T > tn), 44)
    tx(c, T, tn, "TRES COCHES", 560, RED, -5, 110)
    return c

# ---- 11. vienen por el contrato
def s_vienen(T, t0, dur):
    c, pr = nave_c(830, 0); dark(c, 120); tinte(c, (90, 0, 10), 70)
    glow(c, (120, 500, 960, 1800), (255, 90, 70), 100 + 40 * math.sin(T * 12), 110)
    padre(c, pr, T, .1, 4.3 - .7 * ease(clamp((T - t0) / dur)), 2.1, "G11", hat=False)
    c = shake(c, T, 5, 46); c = cam(c, T, t0, dur, 1.0, 1.22, .5, .35); vineta(c, 225)
    tx(c, T, WT("G11", "contrato."), "¡VIENEN POR EL CONTRATO!", 400, YEL, -4, 74)
    return c

# ---- 12. lo tengo yo
def s_loteng(T, t0, dur):
    c, pr = nave_c(830, 8); dark(c, 110); tinte(c, (20, 30, 90), 35); glow(c, (60, 700, 1020, 1500), (255, 200, 120), 60, 90)
    pj(c, pr, "nitro_full", -.2, 2.8, 2.2, T, "G12")
    k = popscale(T, S("G12") + .3, .3)
    if k > 0: papel(c, 760, 1380, .5 * k, rot=-10, firmas=3, T=T)
    c = cam(c, T, t0, dur, 1.0, 1.18, .45, .4); vineta(c, 215)
    tx(c, T, WT("G12", "tengo"), "LO TENGO YO", 400, YEL, -5, 108)
    return c

# ---- 13. la mano
def s_mano(T, t0, dur):
    k = ease(clamp((T - t0) / dur)); te = WT("G13", "extiende")
    c, pr = nave_c(830, 0); dark(c, 110); tinte(c, (60, 10, 30), 45); glow(c, (60, 700, 1020, 1600), (255, 200, 120), 80, 90)
    pj(c, pr, "nitro_full", -.7, 3.4, 2.1, T, None)
    padre(c, pr, T, .7, 3.6, 2.1, None, hat=False, flip=True)
    pp = popscale(T, S("G13") + .2, .3)
    if pp > 0:
        glow(c, (380, 1000, 700, 1300), (255, 235, 170), 140, 60); papel(c, 540, 1160, .42 * pp, rot=-6, firmas=3, T=T)
    c = cam(c, T, t0, dur, 1.0, 1.15, .5, .5); vineta(c, 215)
    tx(c, T, te, "¿SE LO DAS?", 400, YEL, -4, 108)
    return c

# ---- final partido
T_SPLIT = WT("G15", "Confiar.") - .1
def lado10(name):
    key = "L10" + name
    if key in _LC: return _LC[key]
    if name == "A":
        A, pr = nave_c(830, 0); A = A.convert("RGBA"); dark(A, 110); A.alpha_composite(Image.new("RGBA", (W, H), (60, 20, 40, 50)))
        glow(A, (120, 500, 960, 1800), (255, 200, 120), 90, 110)
        pj(A, pr, "nitro_full", -.8, 3.4, 2.1, 0, None); padre(A, pr, 0, .9, 3.6, 2.1, None, hat=False, flip=True)
    else:
        A = fachada(0, 0, 1, 1.0, 1.15, 1.15).convert("RGBA"); dark(A, 40)
        for cx in (200, 540, 880):
            for dx in (-1, 1):
                xx = cx + dx * 140; glow(A, (xx - 150, 1180, xx + 150, 1420), (255, 240, 200), 150, 40); ImageDraw.Draw(A).ellipse((xx - 40, 1270, xx + 40, 1330), fill=(255, 252, 235))
        silf(A, "nitro_full", 300, 1900, 840); silf(A, "lucia_full", 760, 1900, 790, flip=True)
    _LC[key] = A; return A

def s_split10(T, t0, dur):
    s0 = T_SPLIT
    A, B = lado10("A"), lado10("B")
    u = ease((T - s0 + .25) / .45); tb = WT("G15", "huir.") - .05; tn = S("G16") - .05
    hiA = T < tb; neutro = T >= tn
    blk = Image.new("RGBA", (W, H), (0, 0, 0, 255)); c = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    c.alpha_composite(B if (neutro or not hiA) else Image.blend(B, blk, .45), (int(500 * (1 - u)), 0))
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon([(0, 0)] + RAYO + [(0, H)], fill=255)
    c.paste(A if (neutro or hiA) else Image.blend(A, blk, .45), (int(-700 * (1 - u)), 0), mask)
    d = ImageDraw.Draw(c)
    if u > .9:
        v = .6 + .4 * abs(math.sin(T * 13)) * abs(math.sin(T * 3.1))
        gl = blank(); ImageDraw.Draw(gl).line(RAYO, fill=CYAN + (int(255 * v),), width=40, joint="curve")
        c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(c)
        d.line(RAYO, fill=WHITE, width=12, joint="curve"); d.line(RAYO, fill=CYAN, width=5, joint="curve")
    for cx, t1, t2, t3, col in ((270, "CONFIAR", "+ Sabrás la verdad", "- Puede mentir", AZ), (790, "HUIR", "+ Te lo quedas", "- Os perseguirán", MAG)):
        k = popscale(T, s0 + .2, .35)
        if k > 0: opcion8(d, cx, 420, t1, t2, t3, col, k)
    tc = WT("G16", "Comenta") - .05
    if T >= tc:
        k = popscale(T, tc, .3)
        if k > 0:
            lay = blank(); ld = ImageDraw.Draw(lay)
            ld.rounded_rectangle((120, 1100, 960, 1210), 55, fill=(255, 255, 255, 245), outline=OL, width=6)
            text(ld, (540, 1155), "COMENTA CONFIAR O HUIR", 50, OL, stroke=0)
            if abs(k - 1) > .01:
                big = lay.resize((int(W * k), int(H * k)), Image.BILINEAR); ox, oy = int(540 - 540 * k), int(1155 - 1155 * k)
                lay = blank(); lay.alpha_composite(big, (max(0, ox), max(0, oy)), (max(0, -ox), max(0, -oy)))
            c.alpha_composite(lay)
    return c

AV6[:] = [S("G09") + .2]
def aviso6(c, T):
    for t0 in AV6:
        if not (t0 <= T < t0 + 5.0): continue
        u = ease((T - t0) / .35) if T < t0 + 4.6 else 1 - ease((T - t0 - 4.6) / .35)
        y = 300 + 20 * (1 - u); a = int(255 * u)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        w2 = 330 * (1 + .03 * math.sin((T - t0) * 8))
        d.rounded_rectangle((540 - w2, y, 540 + w2, y + 74), 37, fill=(255, 255, 255, a), outline=OL + (a,), width=5)
        d.text((540, y + 24), "¿TÚ QUÉ HARÍAS? CUÉNTALO", font=R.font(F_ANTON, 29), fill=OL + (a,), anchor="mm")
        d.text((540, y + 54), "tu comentario decide la parte 11", font=R.font(F_UI, 23), fill=(200, 50, 50, a), anchor="mm")
        c.alpha_composite(lay)

FASES = [(0, "Entrar al taller"), (S("G03"), "Plantar cara al intruso"), (S("G09"), "Proteger el contrato"), (S("G13"), "Tú eliges")]
def draw_hud10(canvas, T):
    if T >= T_SPLIT: return
    canvas.alpha_composite(R.barra_base())
    d = ImageDraw.Draw(canvas); x0, y0, x1 = 36, 168, 1044
    def pop(t): return 1 + .28 * math.sin(clamp((T - t) / .3) * math.pi) if 0 <= T - t < .3 else 1
    for k, v, x in (("coch", "1", x0 + 300), ("caja", euros(1010), x0 + 420), ("deuda", "-" + euros(64300), x0 + 600), ("rep", "2", x0 + 880)):
        cy = y0 + 34
        if k == "coch": R.carito(d, x, cy, CYAN)
        if k == "caja": R.coin(d, x, cy, 15)
        if k == "deuda": R.flecha(d, x, cy, 1.0)
        if k == "rep": R.estrella(d, x, cy, 17, (242, 190, 60))
        d.text((x + 24, y0 + 35), v, font=R.font(F_ANTON, 34), fill=(255, 120, 110) if k == "deuda" else WHITE, anchor="lm")
    idx = max(i for i, (t, _) in enumerate(FASES) if T >= t); t_fase, obj = FASES[idx]
    d.text((x0 + 132, y0 + 87), obj, font=R.font(F_UI, 24 * pop(t_fase)), fill=(255, 140, 120) if idx else WHITE, anchor="lm")
    d.text((x1 - 20, y0 + 87), "REPUTACIÓN", font=R.font(F_UI, 18), fill=GRIS, anchor="rm")
    p = clamp(T / (T_SPLIT - .1)); xb0, xb1 = x0 + 24, x1 - 24
    d.rounded_rectangle((xb0, y0 + 102, xb1, y0 + 107), 3, fill=(255, 255, 255, 40))
    d.rounded_rectangle((xb0, y0 + 102, xb0 + (xb1 - xb0) * p, y0 + 107), 3, fill=CYAN)
    d.ellipse((xb0 + (xb1 - xb0) * p - 7, y0 + 99, xb0 + (xb1 - xb0) * p + 7, y0 + 110), fill=WHITE)
    aviso6(canvas, T)

# ======================================================================= guion de planos
PLANOS = []
def add(t0, fn): PLANOS.append((t0, fn))
def A_(lid, fn, off=-.12): add(S(lid) + off, fn)
def W_(lid, w, fn, off=-.1): add(WT(lid, w) + off, fn)
add(0, s_patada)
A_("G02", s_grito)
A_("G03", s_sombrero); W_("G03", "sonríe", s_sonrie, -.05)
A_("G04", s_tarde); A_("G05", s_lucia10); A_("G06", s_pacto); A_("G07", s_deuda); A_("G08", s_llave)
A_("G09", s_del96); A_("G10", s_faros); A_("G11", s_vienen); A_("G12", s_loteng); A_("G13", s_mano)
add(T_SPLIT, s_split10)
PLANOS.sort(key=lambda p: p[0])
R.SCENES = []
for i, (t, f) in enumerate(PLANOS):
    dur = ((PLANOS[i + 1][0] if i + 1 < len(PLANOS) else R.TOTAL) - t)
    R.SCENES.append((t, (lambda f, t, dur: (lambda T: (bruma_luz(f(T, t, dur), T) if f is not s_split10 else f(T, t, dur))))(f, t, dur)))

R.IMPACTS = [WT("G01", "patada.") - .05, S("G02"), WT("G03", "sombrero"), S("G05"), WT("G08", "llave"), WT("G10", "coches"), S("G11"), T_SPLIT]
R.draw_hud = draw_hud10
R.HIDE_LAST_CAPTION = False

def lecho(nombre, src, dur, fade=.4, loop=False):
    import numpy as np, wave
    out = os.path.join(R.HERE, "sfx", nombre + ".wav"); sr = 44100
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(R.HERE, "sfx", src + ".wav"), "-ac", "2", "-ar", str(sr), "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32).reshape(-1, 2) / 32768
    n = int(dur * sr)
    if loop: y = np.tile(x, (n // len(x) + 1, 1))[:n]
    else:
        y = np.zeros((n, 2), np.float32); m = min(n, len(x)); y[:m] = x[:m]
    f = int(fade * sr); y[-f:] *= np.linspace(1, 0, f)[:, None]
    w = wave.open(out, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    return out

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "still":
        for t in sys.argv[2:]: R.frame(float(t)).save(os.path.join(R.TMP, f"e10_{float(t):06.2f}.jpg"), quality=88)
    elif cmd == "info":
        print({k: [round(a, 2), round(b, 2)] for k, (a, b) in R.TL.items()}, round(R.TOTAL, 2))
        print(len(R.SCENES), [round(t, 1) for t, f in R.SCENES])
    elif cmd == "scenes":
        from multiprocessing import Pool
        ids = [int(x) for x in sys.argv[2:]] or list(range(len(R.SCENES)))
        with Pool(2) as pool:
            pool.starmap(R.render_scene, [(i, os.path.join(R.TMP, f"e10s{i:02d}.mp4")) for i in ids])
    elif cmd == "mix":
        import mix
        F = lambda n: os.path.join(R.HERE, "sfx", n + ".wav")
        tf = S("G10"); tfr = WT("G10", "frenan")
        idle0 = lecho("e10_idle_nitro", "nitro_ralenti", 4.6, .6, True)
        llega = lecho("e10_llegan", "nitro_motor", tfr - tf + .4, .15)
        idle1 = lecho("e10_idle_coches", "v8_ralenti", WT("G13", "extiende") - tfr + 2.5, 1.0, True)
        huye = lecho("e10_huye", "seat_acelera", 3.0, .5)
        efectos = [
            (F("impacto"), WT("G01", "patada.") - .08, -3), (F("puerta_nave"), WT("G01", "patada.") - .45, -5), (F("movil"), .5, -2), (F("brillo"), .3, -8),
            (F("seat_derrape"), .05, 1), (idle0, .3, -1), (F("petardeo"), 2.4, 0),
            (F("tension"), S("G03") - .1, -9), (F("impacto"), S("G02") + .05, -9),
            (F("brillo"), WT("G03", "sombrero") - .05, -8), (F("impacto"), S("G05") - .05, -8),
            (F("tension"), S("G06") - .1, -10), (F("impacto"), WT("G07", "deuda") - .05, -8),
            (F("caja"), WT("G08", "llave") - .05, -7), (F("tension"), S("G09") - .1, -10),
            (llega, tf - .1, 3), (F("nitro_ruge"), tf + .5, 1), (F("petardeo"), tf + 1.3, 0),
            (F("seat_derrape"), tfr - .15, 4), (F("seat_derrape"), tfr + .25, 3), (idle1, tfr + .1, -2),
            (F("petardeo"), S("G11") + 1.0, 0), (F("tension"), S("G12") - .1, -10),
            (F("impacto"), S("G11") - .05, -6),
            (F("brillo"), WT("G13", "extiende") - .05, -7), (F("impacto"), T_SPLIT, -6),
            (huye, WT("G15", "huir.") - .15, 3), (F("petardeo"), WT("G15", "huir.") + .9, 0),
            (F("brillo"), WT("G16", "Comenta") - .05, -4),
        ]
        mix.main(os.path.join(R.HERE, "el_taller_de_ruben_ep10_corto.mp4"), "e10s", efectos)
