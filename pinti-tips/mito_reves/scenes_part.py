# ---------------------------------------------------------------- escenas
def per(b, quien, expr, t, x=540, y=960, s=1.0, rot=0.0, **kw):
    im = A.nina(expr) if quien == "n" else A.mama(expr, **kw)
    put(b, im, x, y + 60 + bob(t, 7), s * 1.2, rot + bob(t, 1.5, .8))

def frase(b, t, txt, x, y, size, t0=.0, col=(255, 255, 255), tail="left", rot=-2):
    put(b, A.globo(txt, size, col, tail), x, y, pop(t, t0, .32), rot + bob(t, 2))

def numero(b, n, t, x=540, y=900, s=1.0, color=None):
    im = A.canvas(560, 560); d = ImageDraw.Draw(im); A.ell(d, (20, 20, 540, 540), color or A.AMA, A.OL, 14); im = A.fin(im).copy()
    ImageDraw.Draw(im).text((280, 300), str(n), font=A.font("anton", 380), fill=A.OL, anchor="mm")
    put(b, im, x, y + bob(t, 8, 1.2), pop(t, 0, .35) * s, -5 + bob(t, 2, 1))

def tarjeta(txt, w=420, h=520, size=380, color=A.CREMA, espejo=False, fcol=None):
    im = A.canvas(w, h); d = ImageDraw.Draw(im); A.rrect(d, (8, 8, w - 8, h - 8), 44, color, A.OL, 10); im = A.fin(im).copy()
    g = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ImageDraw.Draw(g).text((w // 2, h // 2 + 10), txt, font=A.font("hand", size), fill=fcol or A.OL, anchor="mm")
    if espejo: g = ImageOps.mirror(g)
    im.alpha_composite(g); return im

@lru_cache(None)
def perro(der=True):
    im = A.canvas(520, 380); d = ImageDraw.Draw(im); C = (222, 170, 108)
    A.rrect(d, (90, 130, 380, 270), 70, C, A.OL, 10)
    for x in (120, 320): A.rrect(d, (x, 240, x + 50, 350), 20, C, A.OL, 10)
    A.line(d, [(95, 160), (45, 100)], A.OL, 26); A.line(d, [(95, 160), (45, 100)], C, 14)
    A.ell(d, (320, 60, 470, 200), C, A.OL, 10); A.ell(d, (410, 110, 505, 175), (240, 205, 160), A.OL, 10); A.ell(d, (480, 112, 505, 134), A.OL, None)
    A.ell(d, (385, 95, 410, 120), (255, 255, 255), A.OL, 6); A.ell(d, (392, 102, 404, 114), A.OL, None)
    A.poly(d, [(330, 70), (350, 10), (385, 75)], (150, 100, 60), A.OL, 8)
    im = A.fin(im).copy(); return im if der else ImageOps.mirror(im)

def trazo(letra, p, size=520):
    """Dibuja la b o la d en dos trazos: el 1.º en rojo, el 2.º en azul."""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im); W = 44
    def seg(pts, col):
        for i in range(len(pts) - 1): d.line([pts[i], pts[i + 1]], fill=col, width=W)
        for q in pts: d.ellipse((q[0] - W // 2, q[1] - W // 2, q[0] + W // 2, q[1] + W // 2), fill=col)
    def arco(cx, cy, r, a0, sg, k, col): seg([(cx + r * math.cos(math.radians(a0 + sg * 360 * j / 40)), cy - r * math.sin(math.radians(a0 + sg * 360 * j / 40))) for j in range(int(40 * k) + 1)], col)
    ROJ, AZU = (230, 70, 60), (60, 130, 220)
    if letra == "b":
        k1 = min(1, p / .5); k2 = max(0, (p - .5) / .5)
        seg([(170, 60), (170, 60 + 440 * k1)], ROJ)
        if k2 > 0: arco(300, 380, 120, 180, -1, k2, AZU)
    else:
        k1 = min(1, p / .5); k2 = max(0, (p - .5) / .5)
        arco(230, 380, 120, 0, 1, k1, ROJ)
        if k2 > 0: seg([(350, 60), (350, 60 + 440 * k2)], AZU)
    return im

def tabla_trazo(b, letra, t, x, y, s=1.0):
    k = pop(t, 0, .35); card = tarjeta("", 560, 640); put(b, card, x, y, k * s, 0)
    ImageDraw.Draw(b)  # no-op para mantener el orden
    put(b, trazo(letra, ease(u_(t, .3, 2.2)), 520), x, y, k * s, 0)
    put(b, A.texto("1", 90, (255, 255, 255), 8), x - 250 * s, y - 280 * s, pop(t, .2) * s, 0)
    put(b, A.texto("2", 90, (255, 255, 255), 8), x + 250 * s, y - 280 * s, pop(t, 1.5) * s, 0)

def S00(b, t, T):  # gancho visible desde el frame 0
    bg(b, "cielo", t); titulo(b, "SI TU HIJO ESCRIBE\n*LAS LETRAS AL REVÉS", t, -1, 290, 78)
    put(b, tarjeta("b"), 360, 880 + bob(t, 6, 1.2), 1.0, -5); put(b, tarjeta("d", espejo=True), 720, 880 + bob(t, 6, 1.2, 1), 1.0, 5)
    per(b, "n", "asombro", t, 540, 1330, .6)
def S01(b, t, T):
    bg(b, "alerta", t); put(b, A.sello("NO HAGAS ESTO", 940, 280, A.ROJO, 120), 540, 640 + bob(t, 4, 1.5), pop(t, 0, .3), -4); per(b, "m", "preocupado", t, 540, 1120, .85)
def S02(b, t, T):
    bg(b, "lila", t); per(b, "m", "preocupado", t, 400, 1130, .8); frase(b, t, "¡Es dislexia!", 590, 620, 90, .2, tail="left"); titulo(b, "ALGUIEN\n*TE LO DIJO", t, 0, 290, 96)
def S03(b, t, T):
    bg(b, "amarillo", t); put(b, A.sello("MITO", 760, 300, A.ROJO, 200), 540, 760, pop(t, .05, .3), -5); put(b, A.xmark(260), 840, 1130, pop(t, .5), 8)
def S04(b, t, T):
    bg(b, "noche", t); per(b, "n", "triste", t, 540, 1130, .85); titulo(b, "TU MIEDO\n*LE HACE DAÑO", t, 0, 290, 96, (255, 236, 160))
def S05(b, t, T):
    bg(b, "menta", t); numero(b, 7, t, 540, 760, .95); titulo(b, "HASTA LOS\n*7 AÑOS", t, 0, 290, 96); put(b, A.sello("ES NORMAL", 700, 230, A.VERDE, 120), 540, 1130, pop(t, 1.0, .3), -3)
def S06(b, t, T):
    bg(b, "cielo", t); put(b, tarjeta("b"), 330, 850, pop(t, 0, .3), -4); put(b, A.flecha_doble(420), 540, 850, pop(t, .5), 0); put(b, tarjeta("d"), 750, 850, pop(t, .8, .3), 4)
    titulo(b, "B  COMO  D", t, 0, 400, 120)
def S07(b, t, T):
    bg(b, "durazno", t); put(b, tarjeta("p"), 330, 850, pop(t, 0, .3), -4); put(b, A.flecha_doble(420), 540, 850, pop(t, .4), 0); put(b, tarjeta("q"), 750, 850, pop(t, .6, .3), 4)
    titulo(b, "P  COMO  Q", t, 0, 400, 120)
def S08(b, t, T):
    bg(b, "crema", t); h = A.hoja().copy(); h.alpha_composite(ImageOps.mirror(A.letra(("LUCÍA",), "limpia", 4, 150))); put(b, h, 540, 880 + bob(t, 6), .95, -3)
    titulo(b, "SU NOMBRE\n*EN ESPEJO", t, 0, 290, 96)
def S09(b, t, T):
    bg(b, "lila", t); put(b, A.cerebro(520), 540, 780 + bob(t, 8, 1.2), pop(t, .1, .4), 0); titulo(b, "SU CEREBRO\n*ESTÁ APRENDIENDO", t, 0, 290, 80); per(b, "n", "neutral", t, 540, 1330, .45)
def S10(b, t, T):
    bg(b, "amarillo", t); titulo(b, "LA DIRECCIÓN\n*IMPORTA", t, 0, 330, 100); put(b, A.flecha_doble(560), 540, 760, pop(t, .3), 0); put(b, tarjeta("b", 300, 380, 280), 540, 1090, pop(t, .6, .3), 0)
def S11(b, t, T):
    bg(b, "menta", t); put(b, perro(False), 300, 800 + bob(t, 6, 1.6), .9 * pop(t, 0, .3), 0); put(b, perro(True), 780, 800 + bob(t, 6, 1.6, 1), .9 * pop(t, .5, .3), 0)
    put(b, A.check(170), 540, 1020, pop(t, 1.3), 6); titulo(b, "SIGUE SIENDO\n*UN PERRO", t, 0, 290, 96)
def S12(b, t, T):
    bg(b, "alerta", t); put(b, tarjeta("b"), 330, 850, pop(t, 0, .3), -4); put(b, tarjeta("b", espejo=True), 750, 850, pop(t, .35, .3), 4); put(b, A.texto("¿?", 170, A.AMA, 12), 540, 1250, pop(t, 1.0, .3), 5)
def S13(b, t, T):
    bg(b, "amarillo", t); put(b, A.sello("OTRA LETRA", 860, 260, A.ROJO, 130), 540, 760, pop(t, .05, .3), -4); estrellas(b, t, .3, (540, 760), 6, 420)
def S14(b, t, T):
    bg(b, "cielo", t); per(b, "n", "feliz", t, 540, 1120, .85); put(b, A.bombilla(260), 830, 640 + bob(t, 6, 1.4), pop(t, .5, .4), 0); titulo(b, "ES NUEVO\n*PARA ÉL", t, 0, 290, 100)
def S15(b, t, T):
    bg(b, "alerta", t); titulo(b, "LO QUE NO\n*HAY QUE HACER", t, 0, 290, 96); per(b, "m", "neutral", t, 540, 1130, .85); put(b, A.xmark(220), 830, 780, pop(t, .6), 8)
def S16(b, t, T):
    bg(b, "crema", t); h = A.hoja().copy(); h.alpha_composite(A.letra(("b  d  p",), "limpia", 4, 150)); put(b, h, 540, 880 + bob(t, 6), .95, -3)
    k = ease(u_(t, .4, .6)); ImageDraw.Draw(b).line((220, 760, 220 + 640 * k, 960), fill=A.ROJO, width=30); titulo(b, "TACHARLE", t, 0, 300, 120)
def S17(b, t, T):
    bg(b, "alerta", t); per(b, "m", "neutral", t, 380, 1130, .8); frase(b, t, "Está mal,\notra vez.", 600, 620, 84, .05); put(b, A.xmark(210), 850, 1010, pop(t, 1.0, .3), 0)
def S18(b, t, T):
    bg(b, "lila", t); per(b, "m", "preocupado", t, 540, 1100, .9); titulo(b, "CARA DE\n*PREOCUPACIÓN", t, 0, 290, 96); put(b, A.xmark(190), 840, 760, pop(t, .8), 8)
def S19(b, t, T):
    bg(b, "noche", t); per(b, "n", "triste", t, 540, 1110, .85); titulo(b, "SE FRUSTRA Y\n*EVITA ESCRIBIR", t, 0, 290, 84, (255, 236, 160)); put(b, A.lapiz(480), 820 + t * 120, 1260 + t * 20, 1.0, -8)
def S20(b, t, T):
    bg(b, "menta", t); titulo(b, "LO QUE SÍ", t, 0, 420, 170); put(b, A.check(300), 540, 820, pop(t, .3, .4), 6)
def S21(b, t, T):
    bg(b, "menta", t); per(b, "m", "feliz", t, 540, 1120, .85); titulo(b, "ENSÉÑALE POR DÓNDE\n*EMPIEZA CADA LETRA", t, 0, 290, 76); put(b, A.flecha_curva(260, A.ROJO), 850, 760, pop(t, .8), 100)
def S22(b, t, T):
    bg(b, "amarillo", t); tabla_trazo(b, "b", t, 540, 800, 1.0); titulo(b, "LA B", t, 0, 300, 120); put(b, A.texto("palito, luego barriga", 62, (255, 255, 255), 8, "baloo"), 540, 1180, pop(t, 1.0))
def S23(b, t, T):
    bg(b, "cielo", t); tabla_trazo(b, "d", t, 540, 800, 1.0); titulo(b, "LA D", t, 0, 300, 120); put(b, A.texto("barriga, luego palito", 62, (255, 255, 255), 8, "baloo"), 540, 1180, pop(t, 1.0))
def S24(b, t, T):
    bg(b, "durazno", t); put(b, A.ojo(300), 540, 700 + bob(t, 6, 1.3), pop(t, .1, .35), 0); put(b, tarjeta("b", 260, 330, 230), 250, 1060, pop(t, .6, .3), -6); put(b, tarjeta("d", 260, 330, 230), 830, 1060, pop(t, .9, .3), 6); titulo(b, "BÚSCALAS EN\n*CARTELES Y CUENTOS", t, 0, 290, 80)
def S25(b, t, T):
    bg(b, "amarillo", t); put(b, A.sello("OTRO TRUCO", 860, 260, A.VERDE, 130), 540, 760, pop(t, .05, .3), -4); estrellas(b, t, .3, (540, 760), 6, 420)
def S26(b, t, T):
    bg(b, "lila", t); per(b, "n", "feliz", t, 540, 1160, .8); u = ease(u_(t, .4, 2.0)); put(b, trazo("b", u, 460), 540, 780, 1.0, 0); titulo(b, "DIBÚJALA CON\n*EL DEDO EN EL AIRE", t, 0, 290, 76)
def S27(b, t, T):
    bg(b, "durazno", t); d = ImageDraw.Draw(b); d.rounded_rectangle((120, 560, 960, 1180), 50, fill=(236, 205, 150), outline=A.OL, width=10)
    put(b, trazo("d", ease(u_(t, .2, 1.3)), 560), 540, 870, 1.0, 0); titulo(b, "EN LA ARENA\n*O EN HARINA", t, 0, 290, 90)
def S28(b, t, T):
    bg(b, "menta", t); per(b, "n", "feliz", t, 540, 1110, .85); titulo(b, "SIENTE EL\n*MOVIMIENTO", t, 0, 290, 100); estrellas(b, t, 1.2, (540, 640), 5, 380)
def S29(b, t, T):
    bg(b, "cielo", t); put(b, A.cerebro(380), 540, 760 + bob(t, 8, 1.2), pop(t, .1, .4), 0); put(b, A.corazon(180), 790, 640, pop(t, .8), 8); titulo(b, "SU CUERPO\n*RECUERDA", t, 0, 290, 100)
def S30(b, t, T):
    bg(b, "crema", t); put(b, A.calendario(600, 520, 5), 540, 760, pop(t, .1, .4), -3); titulo(b, "PASADOS LOS\n*7 U 8 AÑOS", t, 0, 290, 96)
def S31(b, t, T):
    bg(b, "alerta", t); put(b, tarjeta("b"), 330, 830, pop(t, 0, .3), -4); put(b, tarjeta("d", espejo=True), 750, 830, pop(t, .3, .3), 4); titulo(b, "SIGUE HACIÉNDOLO\n*MUCHO", t, 0, 290, 80)
def S32(b, t, T):
    bg(b, "lila", t); per(b, "n", "triste", t, 540, 1120, .8); titulo(b, "ADEMÁS LE\n*CUESTA LEER", t, 0, 290, 100)
def S33(b, t, T):
    bg(b, "menta", t); per(b, "m", "feliz", t, 540, 1120, .85, shirt=(60, 160, 110)); titulo(b, "CONSÚLTALO CON\n*SU MAESTRA", t, 0, 290, 90); put(b, A.check(190), 840, 780, pop(t, .7), 6)
def S34(b, t, T):
    bg(b, "cielo", t); numero(b, 5, t, 540, 700, .8); per(b, "n", "feliz", t, 540, 1230, .6); titulo(b, "NIÑO DE 5 AÑOS", t, 0, 1010, 90)
def S35(b, t, T):
    bg(b, "menta", t); put(b, A.sello("NADA RARO", 800, 270, A.VERDE, 140), 540, 760, pop(t, .05, .3), -4); put(b, A.check(260), 540, 1110, pop(t, .5, .4), 6)
def S36(b, t, T):
    bg(b, "amarillo", t); per(b, "n", "orgulloso", t, 540, 1130, .85); titulo(b, "ESTÁ\n*APRENDIENDO", t, 0, 290, 110); estrellas(b, t, .3, (540, 560), 6, 380)
def S37(b, t, T):
    bg(b, "cielo", t); titulo(b, "DÉJALO EN\n*COMENTARIOS", t, 0, 300, 100); per(b, "m", "feliz", t, 540, 1380, .8)
def S38(b, t, T):
    bg(b, "amarillo", t); frase(b, t, "¿Qué letra escribe\nal revés tu hijo?", 540, 640, 76, .1, tail="left"); put(b, tarjeta("b"), 330, 1000, pop(t, .5, .3), -4); put(b, tarjeta("d", espejo=True), 750, 1000, pop(t, .8, .3), 4)

