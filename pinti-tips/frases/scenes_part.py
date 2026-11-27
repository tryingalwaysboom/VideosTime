# ---------------------------------------------------------------- escenas
def per(b, quien, expr, t, x=540, y=960, s=1.0, rot=0.0, **kw):
    im = A.nina(expr) if quien == "n" else A.mama(expr, **kw)
    put(b, im, x, y + bob(t, 7), s, rot + bob(t, 1.5, .8))

def reloj(size=420):
    im = A.canvas(size, size); d = ImageDraw.Draw(im); A.ell(d, (10, 10, size - 10, size - 10), (255, 255, 255), A.OL, 12)
    c = size / 2
    for k in range(12):
        a = k * math.pi / 6; A.line(d, [(c + math.sin(a) * c * .78, c - math.cos(a) * c * .78), (c + math.sin(a) * c * .9, c - math.cos(a) * c * .9)], A.OL, 8)
    A.ell(d, (c - 14, c - 14, c + 14, c + 14), A.OL, None); return A.fin(im).copy()
_RL = {}
def reloj_vivo(b, x, y, s, t, v=1.0):
    if "r" not in _RL: _RL["r"] = reloj(420)
    im = _RL["r"].copy(); d = ImageDraw.Draw(im); c = 210; a1 = t * 6 * v; a2 = t * .5 * v
    d.line((c, c, c + math.sin(a1) * 150, c - math.cos(a1) * 150), fill=A.ROJO, width=11)
    d.line((c, c, c + math.sin(a2) * 100, c - math.cos(a2) * 100), fill=A.OL, width=14); put(b, im, x, y, s, 0)

def frase(b, t, txt, x, y, size, t0=.0, col=(255, 255, 255), tail="left", rot=-2):
    put(b, A.globo(txt, size, col, tail), x, y, pop(t, t0, .32), rot + bob(t, 2))

def numero(b, n, t, x=540, y=900, s=1.0, color=None):
    im = A.canvas(560, 560); d = ImageDraw.Draw(im); A.ell(d, (20, 20, 540, 540), color or A.AMA, A.OL, 14); im = A.fin(im).copy()
    ImageDraw.Draw(im).text((280, 300), str(n), font=A.font("anton", 380), fill=A.OL, anchor="mm")
    put(b, im, x, y + bob(t, 8, 1.2), pop(t, 0, .35) * s, -5 + bob(t, 2, 1))

def S00(b, t, T):  # gancho: todo visible desde el frame 0
    bg(b, "alerta", t); titulo(b, "3 FRASES QUE\n*APAGAN A TU HIJO", t, -1, 290, 96)
    put(b, A.bombilla(420), 540, 640 + bob(t, 6, 1.2), 1.0, 0); per(b, "n", "triste", t, 540, 1040, .72)
    put(b, A.xmark(200), 820, 660, pop(t, .5), 8)
def S01(b, t, T):
    bg(b, "noche", t); titulo(b, "SIN QUERER\n*LE APAGAN LAS GANAS", t, 0, 290, 80, (255, 236, 160))
    put(b, A.bateria(340, .08), 540, 720, pop(t, .2, .4), bob(t, 3, 1.5)); per(b, "n", "cansado", t, 540, 1080, .62)
def S02(b, t, T):
    bg(b, "lila", t); per(b, "m", "asombro", t, 540, 1010, 1.0); titulo(b, "SEGURO QUE\n*YA DIJISTE ALGUNA", t, 0, 290, 78)
    put(b, A.texto("¿YO?", 170, A.AMA, 12), 830, 700 + bob(t, 8, 1.6), pop(t, .8, .3), 8)
def S03(b, t, T):
    bg(b, "amarillo", t); numero(b, 1, t, 540, 820); titulo(b, "FRASE", t, 0, 330, 140); per(b, "m", "preocupado", t, 540, 1190, .45)
def S04(b, t, T):
    bg(b, "alerta", t); per(b, "m", "neutral", t, 400, 1120, .8); frase(b, t, "Eso está mal,\nbórralo y hazlo\notra vez.", 540, 640, 76, .05)
    put(b, A.xmark(230), 830, 1000, pop(t, 2.0, .3), 0)
def S05(b, t, T):
    bg(b, "crema", t); h = A.hoja().copy(); h.alpha_composite(A.letra(("mamá", "sol"), "fea", 4, 150)); put(b, h, 540, 880 + bob(t, 6), .9, -4)
    k = ease(u_(t, .5, .5)); ImageDraw.Draw(b).line((250, 700, 250 + 560 * k, 1000), fill=A.ROJO, width=30)
    put(b, A.sello("PARECE AYUDAR", 760, 210, A.AMA, 100), 540, 380, pop(t, .15, .3), -3)
def S06(b, t, T):
    bg(b, "cielo", t); per(b, "n", "triste", t, 540, 1030, .85)
    for i, (xx, yy) in enumerate(((220, 640), (860, 620), (800, 940), (250, 930))): put(b, A.xmark(150), xx, yy + bob(t, 7, 1.4, i), pop(t, .3 + i * .45, .3), -10 + i * 8)
    titulo(b, "TODO LO QUE HACE\n*ES UN ERROR", t, 0, 290, 76)
def S07(b, t, T):
    bg(b, "menta", t); titulo(b, "MEJOR DILE:", t, 0, 280, 120); per(b, "m", "feliz", t, 400, 1130, .8)
    frase(b, t, "Mira, esta letra\nte quedó muy bien.", 560, 600, 70, 1.1, (255, 255, 255)); put(b, A.check(210), 830, 1000, pop(t, 1.9), 6)
def S08(b, t, T):
    bg(b, "durazno", t); per(b, "n", "feliz", t, 400, 1130, .75); frase(b, t, "¿Probamos otra\nigual?", 580, 620, 80, .1, tail="left", rot=2)
    put(b, A.lapiz(440), 820, 1180, pop(t, .5, .3), -8 + bob(t, 2, 2))
def S09(b, t, T):
    bg(b, "amarillo", t); numero(b, 2, t, 540, 820); titulo(b, "FRASE", t, 0, 330, 140); per(b, "m", "preocupado", t, 540, 1190, .45)
def S10(b, t, T):
    bg(b, "alerta", t); per(b, "m", "neutral", t, 340, 1130, .75); put(b, A.kid("orgulloso"), 840, 1130 + bob(t, 6), .5, 0)
    frase(b, t, "Mira cómo\nescribe tu primo.", 560, 620, 76, .05)
def S11(b, t, T):
    bg(b, "cielo", t); per(b, "n", "triste", t, 540, 1040, .8); put(b, A.sello("COMPARAR", 700, 230, A.ROJO, 120), 540, 360, pop(t, .15, .3), -3)
    put(b, A.kid("orgulloso"), 860, 800, pop(t, .6, .3) * .45, 0)
def S12(b, t, T):
    bg(b, "noche", t); per(b, "n", "triste", t, 540, 1100, .62, 0); titulo(b, "NUNCA\n*LLEGA", t, 0, 330, 140, (255, 236, 160))
    put(b, A.flecha_curva(260, A.ROJO), 820, 760, pop(t, .8), 100)
def S13(b, t, T):
    bg(b, "lila", t); put(b, A.calendario(600, 520, 4), 540, 700, pop(t, .15, .4), -3); titulo(b, "CADA NIÑO\n*SU RITMO", t, 0, 290, 96)
    per(b, "n", "neutral", t, 540, 1220, .42)
def S14(b, t, T):
    bg(b, "menta", t); per(b, "n", "feliz", t, 540, 1040, .85); put(b, A.check(260), 830, 640, pop(t, .5), 6); titulo(b, "EL TUYO\n*ESTÁ AVANZANDO", t, 0, 290, 84)
def S15(b, t, T):
    bg(b, "menta", t); titulo(b, "MEJOR DILE:", t, 0, 280, 120); per(b, "m", "feliz", t, 400, 1130, .8)
    frase(b, t, "Hoy escribes\nmejor que ayer.", 560, 600, 76, 1.0); put(b, A.estrella(190), 830, 980, pop(t, 1.6), 10)
def S16(b, t, T):
    bg(b, "durazno", t); per(b, "n", "orgulloso", t, 540, 1030, .85); frase(b, t, "Lo veo.", 540, 500, 120, .1, tail="left"); estrellas(b, t, .4, (540, 780), 6, 400)
def S17(b, t, T):
    bg(b, "amarillo", t); numero(b, 3, t, 540, 820); titulo(b, "FRASE", t, 0, 330, 140); per(b, "m", "preocupado", t, 540, 1190, .45)
def S18(b, t, T):
    bg(b, "alerta", t); shake(t, .05, 10); per(b, "m", "cansado", t, 360, 1130, .8); frase(b, t, "¡Date prisa!\nQue no\nterminamos.", 580, 640, 80, .05)
def S19(b, t, T):
    bg(b, "cielo", t); per(b, "n", "neutral", t, 540, 1060, .78); put(b, A.bombilla(300), 820, 640 + bob(t, 6, 1.4), pop(t, .5, .4), 0)
    titulo(b, "MUCHA\n*CONCENTRACIÓN", t, 0, 290, 92)
def S20(b, t, T):
    bg(b, "alerta", t); reloj_vivo(b, 540, 640, 1.0, t, 3.0)
    h = A.hoja().copy(); h.alpha_composite(A.letra(("mamá",), "fea", 8, 150)); put(b, h, 540, 1080 + bob(t, 6), .5, -6); titulo(b, "LETRAS PEOR", t, 0, 300, 100)
def S21(b, t, T):
    bg(b, "noche", t); per(b, "n", "asombro", t, 540, 1030, .85); put(b, A.texto("?!", 200, A.AMA, 12), 820, 640 + bob(t, 8, 1.8), pop(t, .5, .3), 8)
    titulo(b, "MIEDO A\n*EQUIVOCARSE", t, 0, 290, 96, (255, 236, 160))
def S22(b, t, T):
    bg(b, "menta", t); titulo(b, "MEJOR DILE:", t, 0, 280, 120); per(b, "m", "feliz", t, 400, 1130, .8)
    frase(b, t, "Tómate tu tiempo,\nyo espero.", 560, 600, 70, 1.1); put(b, A.check(210), 830, 1000, pop(t, 2.2), 6)
def S23(b, t, T):
    bg(b, "durazno", t); per(b, "m", "feliz", t, 360, 1080, .75); per(b, "n", "feliz", t, 760, 1140, .6); put(b, A.corazon(240), 560, 560 + bob(t, 6, 2), pop(t, .2, .4), 8)
def S24(b, t, T):
    bg(b, "crema", t); titulo(b, "NINGUNA ES\n*MALA INTENCIÓN", t, 0, 290, 90); per(b, "m", "preocupado", t, 540, 1040, .9); put(b, A.corazon(200), 820, 700, pop(t, .6), 8)
def S25(b, t, T):
    bg(b, "noche", t); per(b, "m", "cansado", t, 540, 1050, .9); titulo(b, "LAS DECIMOS\n*CANSADOS", t, 0, 290, 96, (255, 236, 160))
    for i in range(3): put(b, A.texto("Z", 110 + i * 30, (255, 255, 255), 8), 770 + i * 70, 800 - i * 100 - (t * 40 % 40), pop(t, .5 + i * .35), 8)
def S26(b, t, T):
    bg(b, "alerta", t); reloj_vivo(b, 540, 760, 1.2, t, 3.0); titulo(b, "CON PRISA", t, 0, 380, 120)
def S27(b, t, T):
    bg(b, "cielo", t); per(b, "n", "triste", t, 540, 1030, .85); put(b, A.sello("JUZGADO", 720, 230, A.ROJO, 130), 540, 400, pop(t, .5, .3), -4); put(b, A.ojo(260), 820, 700, pop(t, .2, .3), 0)
def S28(b, t, T):
    bg(b, "crema", t); escritorio(b); per(b, "n", "triste", t, 400, 990, .8)
    put(b, A.lapiz(480), 800 + t * 200, 1235 + t * 30, 1.0, -6); titulo(b, "EMPIEZA A\n*EVITARLO", t, 0, 290, 96)
def S29(b, t, T):
    bg(b, "menta", t); per(b, "m", "feliz", t, 360, 1050, .78); per(b, "n", "feliz", t, 760, 1110, .62); put(b, A.corazon(220), 560, 560 + bob(t, 6, 2), pop(t, .3, .4), 8)
    titulo(b, "ACOMPAÑADO", t, 0, 290, 100)
def S30(b, t, T):
    bg(b, "amarillo", t); hoja_escribiendo(b, 560, 900, .95, -4, t, .1, 1.3, ["Quiero", "escribir"], "limpia", True, .6); titulo(b, "QUIERE\n*ESCRIBIR MÁS", t, 0, 290, 92)
def S31(b, t, T):
    bg(b, "cielo", t); titulo(b, "CAMBIA SOLO\n*UNA FRASE", t, 0, 300, 100); numero(b, 1, t, 540, 860, .85); per(b, "m", "feliz", t, 540, 1290, .35)
def S32(b, t, T):
    bg(b, "amarillo", t); put(b, A.sello("SOLO UNA", 760, 260, A.VERDE, 150), 540, 760, pop(t, .05, .3), -4); estrellas(b, t, .3, (540, 760), 6, 420)
def S33(b, t, T):
    bg(b, "lila", t); put(b, A.calendario(640, 560, 1 + int(t * 3.5) % 8), 540, 700, pop(t, .1, .4), -3); titulo(b, "EN UNA SEMANA", t, .1, 1130, 92)
def S34(b, t, T):
    bg(b, "cielo", t); titulo(b, "CUÉNTAME EN\n*COMENTARIOS", t, 0, 300, 90); frase(b, t, "¿Cuál de las\ntres dices más?", 540, 760, 76, .35)
    put(b, A.flecha_curva(300, A.ROJO), 800, 1110, pop(t, 1.0), 90)
def S35(b, t, T):
    bg(b, "amarillo", t)
    for i in range(3): numero(b, i + 1, t - i * .22, 230 + i * 310, 820, .42)
    put(b, A.texto("¿CUÁL?", 190, A.ROJO, 14), 540, 1080 + bob(t, 6, 1.5), pop(t, .5, .3), -4)
def S36(b, t, T):
    bg(b, "amarillo", t); titulo(b, "SÍGUEME", t, 0, 300, 150); put(b, A.boton_seguir(700), 540, 720, pop(t, .2, .4) * (1 + .03 * math.sin(t * 6)), bob(t, 1.5, 1.2))
    put(b, A.texto("@escribirconpinti", 72, (255, 255, 255), 9, "baloo"), 540, 900, pop(t, .5))
def S37(b, t, T):
    bg(b, "cielo", t); titulo(b, "1 TIP\n*CADA DÍA", t, 0, 290, 140); per(b, "m", "feliz", t, 540, 1020, .85); estrellas(b, t, .4, (540, 760), 5, 400)
def S38(b, t, T):
    bg(b, "menta", t); hoja_escribiendo(b, 560, 880, .95, -4, t, .2, 2.6, ["¡Gracias,", "mamá!"], "limpia", True, .6); titulo(b, "TU HIJO\n*ESCRIBE MEJOR", t, 0, 290, 92); estrellas(b, t, 3.0, (540, 880), 6, 430)

