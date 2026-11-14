"""Estilo 1: videojuego retro de mánager de fútbol (pixel art 180x320 escalado x6)."""
import math, sys
import numpy as np
from PIL import Image, ImageDraw
from comun import *

LW, LH, K = 180, 320, 6
PF = "PressStart2P-Regular.ttf"
C = dict(ol=(24, 18, 36), wall=(46, 74, 86), wall2=(54, 86, 98), tile=(38, 62, 72), lock=(52, 96, 168), lock2=(40, 74, 140), lockh=(92, 138, 210),
         bench=(150, 96, 52), bench2=(110, 66, 36), floor=(92, 64, 50), floor2=(80, 54, 42), skin=(242, 182, 140), skin2=(214, 142, 104),
         cap=(80, 82, 92), cap2=(58, 60, 70), mou=(245, 245, 240), mou2=(205, 205, 210), blue=(46, 92, 196), blue2=(32, 66, 150),
         white=(250, 248, 240), bas=(196, 140, 72), bas2=(150, 98, 46), red=(222, 58, 58), red2=(170, 36, 40), yel=(255, 206, 60),
         box=(20, 26, 66), box2=(46, 60, 140), lamp=(255, 250, 210))

import unicodedata
def _plain(s):
    return "".join(ch if ch in "ÑñÜ" else unicodedata.normalize("NFD", ch)[0] for ch in s)
def txt(d, xy, s, col, size=8, anchor="la"):
    d.fontmode = "1"; s = _plain(s)
    d.text(xy, s, font=font(PF, size), fill=col, anchor=anchor)

def outline(sprite):
    a = np.asarray(sprite.getchannel("A")) > 0
    o = np.zeros_like(a)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        o |= np.roll(np.roll(a, dy, 0), dx, 1)
    o &= ~a
    out = Image.new("RGBA", sprite.size, (0, 0, 0, 0))
    arr = np.asarray(out).copy(); arr[o] = C["ol"] + (255,)
    out = Image.fromarray(arr); out.alpha_composite(sprite)
    return out

# ------------------------------------------------------------ fondo (estático, se cachea)
def fondo():
    im = Image.new("RGB", (LW, LH), C["wall"]); d = ImageDraw.Draw(im)
    for y in range(0, 175, 8):                       # azulejos
        for x in range(0, LW, 8):
            if (x // 8 + y // 8) % 2: d.rectangle((x, y, x + 7, y + 7), fill=C["wall2"])
            d.point((x, y), fill=C["tile"])
    for (x, y, w, h) in ((14, 30, 10, 7), (130, 22, 14, 6), (100, 46, 6, 9)):   # desconchones
        d.rectangle((x, y, x + w, y + h), fill=(150, 140, 120)); d.rectangle((x + 1, y + 1, x + w - 1, y + h - 1), fill=(168, 158, 136))
    d.rectangle((0, 56, LW, 58), fill=C["bench2"])   # perchero
    for i, (x, col, n) in enumerate(((16, C["red"], "7"), (52, C["white"], "10"), (100, C["red"], "4"), (142, C["white"], "9"))):
        d.point((x + 7, 59), fill=(200, 200, 200))
        sh = [(x, 62), (x + 4, 60), (x + 10, 60), (x + 14, 62), (x + 16, 67), (x + 13, 68), (x + 13, 80), (x + 1, 80), (x + 1, 68), (x - 2, 67)]
        d.polygon(sh, fill=col, outline=C["ol"])
        txt(d, (x + 7, 66), n, C["ol"] if col == C["white"] else C["white"], 8, "ma")
    for i in range(6):                               # taquillas
        x = i * 30
        d.rectangle((x, 86, x + 29, 168), fill=C["lock"], outline=C["ol"])
        d.rectangle((x + 2, 88, x + 4, 166), fill=C["lockh"])
        for v in range(4): d.line((x + 9, 94 + v * 3, x + 21, 94 + v * 3), fill=C["lock2"])
        d.rectangle((x + 23, 124, x + 25, 130), fill=(200, 200, 210))
        d.rectangle((x + 10, 108, x + 20, 113), fill=(230, 226, 210)); txt(d, (x + 15, 109), f"0{i+1}", C["ol"], 5 if False else 8, "ma") if False else None
    d.rectangle((60, 86, 89, 168), fill=(14, 18, 34)); d.polygon([(60, 86), (72, 90), (72, 172), (60, 168)], fill=C["lock2"], outline=C["ol"])   # puerta abierta
    d.rectangle((0, 164, LW, 170), fill=C["bench"], outline=C["ol"]); d.rectangle((0, 168, LW, 170), fill=C["bench2"])
    for x in (20, 160): d.rectangle((x, 171, x + 4, 182), fill=C["bench2"])
    for y in range(176, LH, 10):                     # suelo
        for x in range(0, LW, 10):
            d.rectangle((x, y, x + 9, y + 9), fill=C["floor"] if (x // 10 + y // 10) % 2 else C["floor2"])
    d.rectangle((0, 174, LW, 176), fill=C["ol"])
    for (x, y) in ((30, 200), (150, 230), (60, 260)):   # papeles / charcos
        d.rectangle((x, y, x + 6, y + 3), fill=(220, 214, 200))
    return im

# ------------------------------------------------------------ Paco
def paco_sprite(T):
    w, h = 76, 150
    s = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(s)
    cx = w // 2
    # cuerpo
    d.rounded_rectangle((cx - 30, 72, cx + 30, 149), 8, fill=C["blue"])
    d.rectangle((cx + 10, 76, cx + 30, 149), fill=C["blue2"])
    for xx in (cx - 27, cx + 24): d.rectangle((xx, 80, xx + 2, 149), fill=C["white"])
    d.line((cx, 74, cx, 149), fill=C["blue2"]); d.rectangle((cx - 6, 70, cx + 6, 76), fill=(230, 226, 214))
    # cabeza
    d.rectangle((cx - 4, 62, cx + 4, 72), fill=C["skin2"])
    d.rounded_rectangle((cx - 19, 20, cx + 19, 64), 9, fill=C["skin"])
    d.rectangle((cx + 8, 26, cx + 19, 62), fill=C["skin2"])
    d.ellipse((cx - 24, 36, cx - 16, 48), fill=C["skin"]); d.ellipse((cx + 16, 36, cx + 24, 48), fill=C["skin2"])
    d.rectangle((cx - 20, 24, cx - 16, 40), fill=(220, 220, 225)); d.rectangle((cx + 16, 24, cx + 20, 40), fill=(200, 200, 205))   # pelo blanco
    # gorra plana
    d.rounded_rectangle((cx - 21, 8, cx + 21, 26), 7, fill=C["cap"]); d.rectangle((cx - 23, 22, cx + 25, 27), fill=C["cap2"])
    d.line((cx - 16, 12, cx + 12, 12), fill=(100, 102, 112))
    # gafas + ojos (parpadeo)
    blink = (T % 3.6) < .12
    for ex in (cx - 11, cx + 9):
        d.rectangle((ex - 7, 31, ex + 7, 41), fill=(236, 240, 246), outline=C["ol"])
        if blink: d.line((ex - 4, 37, ex + 4, 37), fill=C["ol"])
        else: d.rectangle((ex - 2, 34, ex + 1, 38), fill=(70, 46, 30)); d.point((ex - 1, 35), fill=C["white"])
    d.line((cx - 4, 35, cx + 2, 35), fill=C["ol"])
    d.rectangle((cx - 3, 40, cx + 3, 48), fill=(232, 140, 110))                 # nariz
    # bigote y boca
    m = boca(T)
    if m > .05:
        d.rectangle((cx - 6, 54, cx + 6, 54 + int(1 + 5 * m)), fill=(120, 30, 40))
    d.polygon([(cx - 17, 52), (cx - 10, 47), (cx, 50), (cx + 10, 47), (cx + 17, 52), (cx + 12, 55), (cx, 53), (cx - 12, 55)], fill=C["mou"])
    d.line((cx - 12, 53, cx + 12, 53), fill=C["mou2"])
    # cesta con camisetas
    d.rectangle((cx - 30, 98, cx + 30, 104), fill=C["red"]); d.rectangle((cx - 22, 95, cx + 6, 100), fill=C["white"]); d.rectangle((cx + 4, 96, cx + 26, 101), fill=C["red2"])
    d.polygon([(cx - 34, 103), (cx + 34, 103), (cx + 28, 134), (cx - 28, 134)], fill=C["bas"])
    for yy in range(106, 134, 4): d.line((cx - 32 + (yy - 103) // 5, yy, cx + 32 - (yy - 103) // 5, yy), fill=C["bas2"])
    for xx in range(cx - 28, cx + 30, 8): d.line((xx, 104, xx + (1 if xx > cx else -1), 133), fill=C["bas2"])
    d.rectangle((cx - 36, 112, cx - 28, 122), fill=C["skin"]); d.rectangle((cx + 28, 112, cx + 36, 122), fill=C["skin2"])   # manos
    return outline(s)

# ------------------------------------------------------------ interfaz
def ventana(d, box, titulo=None):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=C["box"]); d.rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), outline=C["white"])
    d.rectangle((x0 + 3, y0 + 3, x1 - 3, y1 - 3), outline=C["box2"])
    if titulo:
        tw = len(titulo) * 8 + 8
        d.rectangle((x0 + 6, y0 - 7, x0 + 6 + tw, y0 + 4), fill=C["yel"], outline=C["ol"]); txt(d, (x0 + 10, y0 - 5), titulo, C["ol"])

def envolver(ws, ancho=19):
    lines, cur = [], ""
    for w in ws:
        if len(cur) + len(w) + (1 if cur else 0) > ancho: lines.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    if cur: lines.append(cur)
    return lines

def dialogo(d, T):
    for lid, quien in (("N08", None), ("N09", "PACO")):
        pal = palabras(lid)
        if not (pal[0][1] - .15 <= T < (pal[-1][2] + .6 if lid == "N09" else R.S("N09") - .05)): continue
        # páginas: cada frase completa
        pags, cur = [], []
        for p in pal:
            cur.append(p)
            if p[0].endswith((".", "...", "?")) and len(cur) >= 5: pags.append(cur); cur = []
        if cur: pags.append(cur)
        pag = max([pg for pg in pags if pg[0][1] - .1 <= T] or [pags[0]], key=lambda pg: pg[0][1])
        dichas = [w.upper() for w, a, b in pag if a - .02 <= T]
        ventana(d, (6, 238, 173, 300), quien)
        for i, ln in enumerate(envolver(dichas)[-3:]):
            txt(d, (14, 248 + i * 14), ln, C["white"])
        fin = pag[-1][2]
        if T > fin and int(T * 3) % 2: d.polygon([(160, 290), (166, 290), (163, 294)], fill=C["yel"])

def hud(d):
    d.rectangle((0, 18, LW, 34), fill=(10, 12, 30)); d.line((0, 34, LW, 34), fill=C["white"])
    d.rectangle((3, 21, 31, 31), fill=C["yel"]); txt(d, (5, 22), "EP1", C["ol"])
    txt(d, (36, 22), "DIA 1", C["white"])
    txt(d, (90, 22), "-182400", (255, 110, 110))
    txt(d, (171, 22), "€", (255, 110, 110), 8, "ra")

def ficha(d, T):
    t = EV["paco"]
    if T < t: return
    u = ease((T - t) / .3); x = int(-90 + 96 * u)
    ventana(d, (x, 44, x + 84, 104), "PACO")
    txt(d, (x + 7, 52), "UTILLERO", C["white"])
    txt(d, (x + 7, 64), "EDAD  72", C["white"])
    anos = int(41 * clamp((T - EV["41"]) / .6)) if T >= EV["41"] else 0
    txt(d, (x + 7, 76), f"AÑOS  {anos}", C["yel"] if anos else (120, 130, 170))
    txt(d, (x + 7, 88), "SUELDO 0", (255, 110, 110) if T >= EV["9"] else (120, 130, 170))

def flotante(d, T, t, s, col):
    if not (t <= T < t + 1.4): return
    u = (T - t) / 1.4
    y = int(150 - 22 * ease(u))
    if int(T * 12) % 2 or u < .7: txt(d, (124, y), s, col, 8, "ma")

def frame(T):
    im = FONDO.copy().convert("RGBA"); d = ImageDraw.Draw(im)
    # luz del fluorescente con tramado (dither)
    on = not (int(T * 30) % 113 in (0, 1, 3))
    d.rectangle((70, 4, 110, 7), fill=C["lamp"] if on else (120, 120, 110))
    if on:
        for y in range(8, 170, 1):
            half = 8 + (y - 8) * .35
            for x in range(int(90 - half), int(90 + half)):
                if (x + 2 * y) % 5 == 0 and 0 <= x < LW: d.point((x, y), fill=(130, 150, 140))
    # Paco: entra desde la derecha, respira
    tin = EV["paco"] - .9
    u = ease((T - tin) / .7) if T >= tin else 0
    sp = paco_sprite(T)
    bob = 1 if (T * 1.6) % 1 < .5 else 0
    if u > 0: im.alpha_composite(sp, (int(52 + 130 * (1 - u)), 104 + bob))
    # polvo
    rng = np.random.default_rng(1)
    for i in range(14):
        x = int((rng.uniform(0, LW) + T * rng.uniform(-3, 3)) % LW); y = int((rng.uniform(40, 230) - T * rng.uniform(2, 5)) % 200 + 30)
        d.point((x, y), fill=(240, 230, 190))
    hud(d); ficha(d, T)
    flotante(d, T, EV["41"], "+41 AÑOS", C["yel"])
    flotante(d, T, EV["9"], "-9 MESES", (255, 110, 110))
    dialogo(d, T)
    return im.convert("RGB").resize((W, H), Image.NEAREST)

FONDO = fondo()

if __name__ == "__main__":
    if sys.argv[1:] and sys.argv[1] == "still":
        for t in sys.argv[2:]: frame(T0 + float(t)).save(os.path.join(CLUB, "tmp", f"px_{t}.png"))
    else:
        print(exportar(frame, "estilo_1_pixel_retro"))
