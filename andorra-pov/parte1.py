"""500 € en Andorra — Parte 1 (~38 s, 1080x1920, 30 fps). Mismo motor que La casa de 1 dólar.
python3 ep1.py frames -> fotogramas de control · python3 ep1.py -> vídeo final"""
import json, math, os, random, subprocess, sys
from functools import lru_cache
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "casa-pov"))
import arte as R
import art as A, manos as M, bodycam as BC
from art import W, H, PW, PH, font, F_ANTON, F_UI, F_REG, lerp, soft
from ep1 import cam, text, flash, ease, back, clamp, inout, paste_c, banda, grain, mirada, YEL, WHITE, OL, RED, GRIS, ic_coin

FPS = 30
SRC = os.path.join(HERE, "..", "descargas", "andorra_ep1"); SFXD = os.path.join(HERE, "..", "descargas", "andorra_sfx"); SFX_CASA = os.path.join(HERE, "..", "descargas", "casa_sfx")
TMP = os.path.join(HERE, "tmp1"); OUT = os.path.join(HERE, "out"); os.makedirs(TMP, exist_ok=True); os.makedirs(OUT, exist_ok=True)

def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)
GAP = .22
LINEAS = ["N01", "Y01", "N02"]; OFF = {}; _t = 0.0
for l in LINEAS: OFF[l] = _t; _t += dur(os.path.join(SRC, l + ".mp3")) + GAP
VEND = OFF["N02"] + json.load(open(os.path.join(SRC, "N02.json")))[-1]["fin"]
TOTAL = VEND + .35

DISP = {"500": "500 €", "euros,": None, "escaldes,": "Escaldes,", "30": "30.000 €", ".000": None, "euros.": None, "4": "4", "dos": "2.000 €", "mil": None, "euros": None, "50": "50 €", "450.": "450 €."}
WD = []   # (palabra, inicio, fin, quién)
for l in LINEAS:
    raw = json.load(open(os.path.join(SRC, l + ".json"))); prev = None
    for i, w in enumerate(raw):
        p = w["p"]; d = DISP.get(p, p)
        if p == "euros." and prev not in ("30", ".000", "50", "500"): d = p
        if p == "euros," and prev != "500": d = p
        prev = p
        if d is None:
            if WD: WD[-1] = (WD[-1][0], WD[-1][1], OFF[l] + w["fin"], WD[-1][3])
            continue
        WD.append((d, OFF[l] + w["inicio"], OFF[l] + w["fin"], l[0]))

def wt(word, n=1, quien=None, exacta=False):
    k = 0
    for w, a, b, q in WD:
        if quien and q != quien: continue
        ww, x = w.strip("¡!¿?.,").lower(), word.strip("¡!¿?.,").lower()
        if (ww == x) if exacta else ww.startswith(x):
            k += 1
            if k == n: return a
    raise KeyError(word)

# ------------------------------------------------------------------ tiempos clave
T_500, T_312, T_MADRE, T_AQUI, T_SOFA = wt("500"), wt("312"), wt("Mi") - .1, wt("Aquí") - .12, wt("dormía") - .45
T_ALQ, T_450, T_50 = wt("El") - .1, wt("450"), wt("50 €")
T_VID, T_CERO, T_TU = wt("Mi", 2) - .12, wt("cero") - .12, wt("¿Tú") - .15
T_BAR, T_SENTO, T_RELOJ, T_30 = wt("Esa") - .15, wt("sentó"), wt("reloj") - .25, wt("30.000")
T_Y, T_4M = OFF["Y01"] - .08, wt("4", 1, "Y")
T_N2, T_2000, T_COND, T_NADIE, T_ACEPTO, T_O = OFF["N02"] - .08, wt("2.000"), wt("Una"), wt("nadie"), wt("¿Acepto") - .12, wt("o", 1, "N", True)
CUTS = [0.0, T_MADRE, T_AQUI, T_SOFA, T_ALQ, T_VID, T_CERO, T_TU, T_BAR, T_RELOJ, T_Y, T_N2, T_NADIE - .1, T_ACEPTO, TOTAL]

# ------------------------------------------------------------------ subtítulos palabra a palabra
def chunks():
    out, g = [], []
    for w in WD:
        if g and g[-1][3] != w[3]: out.append(g); g = []
        g.append(w)
        if len(g) == 3 or w[0][-1] in ".,!?" or (len(g) == 2 and len(g[0][0] + g[1][0]) > 13): out.append(g); g = []
    if g: out.append(g)
    return out
CH = chunks()
def caption(c, T):
    if T >= T_ACEPTO - .05: return
    for i, g in enumerate(CH):
        t0, t1 = g[0][1], g[-1][2]; nxt = CH[i + 1][0][1] if i + 1 < len(CH) else 1e9
        if not (t0 - .05 <= T < min(t1 + .4, nxt - .05)): continue
        d = ImageDraw.Draw(c); k = .86 + .14 * back((T - t0 + .05) / .14)
        f = font(F_ANTON, 94 * k); ws = [d.textlength(w + " ", font=f) for w, _, _, _ in g]; tot = sum(ws) - d.textlength(" ", font=f)
        if tot > 860: f = font(F_ANTON, 94 * k * 860 / tot); ws = [d.textlength(w + " ", font=f) for w, _, _, _ in g]; tot = sum(ws) - d.textlength(" ", font=f)
        x = W / 2 - tot / 2; y = 1170
        hi = (120, 220, 255) if g[0][3] == "Y" else YEL   # el millonario, en otro color
        if g[0][3] == "Y":
            tg = font(F_UI, 26); tw = d.textlength("EL MILLONARIO", font=tg)
            d.rounded_rectangle((W / 2 - tw / 2 - 18, 1062, W / 2 + tw / 2 + 18, 1104), 14, fill=(120, 220, 255)); d.text((W / 2, 1083), "EL MILLONARIO", font=tg, fill=OL, anchor="mm")
        for j, ((w, a, b, _), wd) in enumerate(zip(g, ws)):
            fin = g[j + 1][1] if j + 1 < len(g) else b + .4
            col = hi if a - .03 <= T < fin - .03 else (WHITE if T >= a - .03 else (215, 215, 222))
            d.text((x, y), w, font=f, fill=col, anchor="lm", stroke_width=10, stroke_fill=OL); x += wd
        return

# ------------------------------------------------------------------ barra superior
def ic_user(d, x, y, col):
    d.ellipse((x - 9, y - 16, x + 9, y + 2), fill=col); d.pieslice((x - 16, y + 2, x + 16, y + 30), 180, 360, fill=col)
def ic_casa(d, x, y, col):
    d.polygon([(x - 16, y), (x, y - 15), (x + 16, y)], fill=col); d.rectangle((x - 11, y, x + 11, y + 14), fill=col)

@lru_cache(1)
def hud_base():
    im = Image.new("RGBA", (W, 400), (0, 0, 0, 0)); x0, y0, x1, y1 = 36, 238, 1044, 348
    im.alpha_composite(soft((W, 400), lambda dd: dd.rounded_rectangle((x0, y0 + 8, x1, y1 + 10), 26, fill=(0, 0, 0, 130)), 10))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0, y0, x1, y1), 26, fill=(10, 14, 32, 215), outline=(120, 200, 255, 140), width=2)
    d.rounded_rectangle((x0 + 14, y0 + 12, x0 + 160, y0 + 56), 12, fill=(120, 200, 255)); d.text((x0 + 87, y0 + 34), "PARTE 1", font=font(F_ANTON, 32), fill=OL, anchor="mm")
    d.line((x0 + 16, y0 + 64, x1 - 16, y0 + 64), fill=(255, 255, 255, 30), width=2)
    d.text((x0 + 18, y0 + 87), "OBJETIVO", font=font(F_UI, 20), fill=(120, 200, 255), anchor="lm"); d.text((x0 + 132, y0 + 87), "Triunfar como youtuber en Andorra", font=font(F_UI, 24), fill=WHITE, anchor="lm")
    return im
def hud(c, T):
    if T >= T_ACEPTO - .1: return
    base = hud_base()
    if T < .3: c.alpha_composite(base, (0, int(-400 * (1 - ease(T / .3))))); return
    c.alpha_composite(base); d = ImageDraw.Draw(c); x0, y0 = 36, 238
    def pop(t): return 1 + .3 * math.sin(clamp((T - t) / .3) * math.pi) if 0 <= T - t < .3 else 1
    v = int(500 - 450 * ease((T - T_450) / .6) * (T >= T_450))
    hot = T_450 <= T < T_450 + 2.5
    ic_coin(d, x0 + 230, y0 + 34); d.text((x0 + 256, y0 + 35), f"{v} €", font=font(F_ANTON, 36 * max(pop(T_500), pop(T_450))), fill=(255, 120, 110) if hot else WHITE, anchor="lm")
    ic_user(d, x0 + 430, y0 + 30, (120, 200, 255)); d.text((x0 + 456, y0 + 35), "312", font=font(F_ANTON, 36 * pop(T_312)), fill=WHITE, anchor="lm")
    ic_casa(d, x0 + 640, y0 + 34, (255, 170, 70)); d.text((x0 + 666, y0 + 35), "RESIDENCIA", font=font(F_ANTON, 30), fill=WHITE, anchor="lm")
    d.text((x0 + 900, y0 + 35), "✗", font=font(F_UI, 36), fill=(255, 100, 100), anchor="lm")

# ------------------------------------------------------------------ efectos
@lru_cache(1)
def _copos():
    rng = np.random.default_rng(9); n = 160
    return rng.uniform(0, W, n), rng.uniform(0, H, n), rng.uniform(60, 220, n), rng.uniform(0, 6.28, n), rng.uniform(3, 9, n)
def nevada(c, T, amax=220):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for x, y, sp, ph, r in zip(*_copos()):
        px = (x + 40 * math.sin(T * .8 + ph) - 30 * T) % W; py = (y + sp * T) % H
        d.ellipse((px - r, py - r, px + r, py + r), fill=(255, 255, 255, int(amax * min(1, r / 6))))
    c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.2)))

def etiqueta(c, T, t0, txt, y=760, col=(255, 206, 60), size=78, t1=1e9):
    if not (t0 <= T < t1): return
    k = min(1, back((T - t0) / .3)); d = ImageDraw.Draw(c); f = font(F_ANTON, size * k); tw = d.textlength(txt, font=f)
    c.alpha_composite(soft((W, H), lambda dd: dd.rounded_rectangle((W / 2 - tw / 2 - 30, y - size * .72 * k + 10, W / 2 + tw / 2 + 30, y + size * .72 * k + 10), 24, fill=(0, 0, 0, 120)), 12))
    d = ImageDraw.Draw(c); d.rounded_rectangle((W / 2 - tw / 2 - 30, y - size * .72 * k, W / 2 + tw / 2 + 30, y + size * .72 * k), 24, fill=col)
    d.text((W / 2, y), txt, font=f, fill=OL, anchor="mm")

def precio(c, T, t0, t1, linea1, linea2, col, y=640, c2=WHITE):
    if not (t0 <= T < t1): return
    k = min(1, back((T - t0) / .3)); w, h = 620 * k, 230 * k
    c.alpha_composite(soft((W, H), lambda dd: dd.rounded_rectangle((W / 2 - w / 2, y - h / 2 + 12, W / 2 + w / 2, y + h / 2 + 12), 34, fill=(0, 0, 0, 140)), 14)); d = ImageDraw.Draw(c)
    d.rounded_rectangle((W / 2 - w / 2, y - h / 2, W / 2 + w / 2, y + h / 2), 34, fill=(14, 16, 32, 235), outline=col, width=6)
    if k > .6:
        d.text((W / 2, y - 52), linea1, font=font(F_ANTON, 54), fill=col, anchor="mm"); text(d, (W / 2, y + 40), linea2, 118, c2, stroke=0)

def sello(c, T, t0, txt, y=760, col=(220, 40, 50)):
    if T < t0: return
    u = clamp((T - t0) / .22); s = lerp(2.2, 1.0, ease(u)); a = int(255 * min(1, u * 2))
    f = font(F_ANTON, 92); tmp = Image.new("RGBA", (1000, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(tmp)
    d.rounded_rectangle((20, 20, 980, 240), 26, outline=col + (a,), width=14); d.text((500, 130), txt, font=f, fill=col + (a,), anchor="mm")
    tmp = tmp.rotate(-8, expand=True, resample=Image.BICUBIC); paste_c(c, tmp, W / 2, y, s * .9)

# ------------------------------------------------------------------ objetos en la mano
@lru_cache(None)
def maleta_im():
    im = Image.new("RGBA", (520, 760), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((246, 0, 262, 260), fill=(150, 150, 160)); d.rectangle((296, 0, 312, 260), fill=(150, 150, 160)); d.rounded_rectangle((230, -10, 330, 30), 14, fill=(40, 40, 46))
    d.rounded_rectangle((40, 240, 500, 740), 46, fill=(40, 70, 130)); d.rounded_rectangle((70, 270, 470, 710), 34, fill=(50, 86, 156))
    for x in (160, 280, 400): d.line((x, 270, x, 710), fill=(36, 62, 120), width=10)
    d.rounded_rectangle((120, 420, 260, 520), 16, fill=(240, 220, 120)); d.text((190, 470), "AND", font=font(F_ANTON, 44), fill=(60, 40, 20), anchor="mm")
    return im

def movil_en_mano(c, T, pantalla, x=540, y=1300, s=1.0, rot=0, lado="d"):
    ph = R.movil(pantalla=pantalla) if isinstance(pantalla, Image.Image) else R.movil(chat=pantalla)
    paste_c(c, ph, x, y, s, rot=rot)
    M.poner(c, "puno", x + 40 * s, y + 470 * s + 300 * s, lado, 1.0 * s, rot, 1.0)

def chat(T):
    msgs = [("ella", "¿¿ANDORRA??"), ("ella", "Estás loco hijo"), ("ella", "Vuelve a casa ya"), ("yo", "Confía en mí mamá")]
    n = sum(1 for k in range(4) if T >= T_MADRE + .15 + k * .42)
    return tuple(msgs[:n])

# ------------------------------------------------------------------ escenas
def resp(T, f=.9): return BC.respiracion(T * 1.15 + 3, f)

def sc_llegada(T):
    t0, t1 = CUTS[0], CUTS[1]; u = inout((T - t0) / (t1 - t0))
    c = cam(R.calle(), lerp(1.45, 1.7, u), PW / 2, lerp(1260, 1180, u))
    nevada(c, T)
    bx, by = resp(T)
    paste_c(c, maleta_im(), 760 + bx * .6, 1560 + by * .6, 1.0)
    M.poner(c, "puno", 800 + bx, 1680 + by, "d", 1.0, -6, 1.0)
    etiqueta(c, T, T_500 - .05, "500 €", 640, (120, 230, 140), 96, T_312 - .1)
    etiqueta(c, T, T_312 - .05, "312 SEGUIDORES", 640, (120, 200, 255), 80)
    flash(c, T, 0, .12)
    return c

def sc_madre(T):
    c = cam(R.calle(), 1.9, PW / 2 - 60, 1150); c = c.filter(ImageFilter.GaussianBlur(10)); nevada(c, T, 160)
    bx, by = resp(T)
    k = ease((T - CUTS[1]) / .3); movil_en_mano(c, T, chat(T), 540 + bx, lerp(1900, 1080, k) + by, 1.25, -3)
    flash(c, T, CUTS[1], .1)
    return c

def sc_ricos(T):
    t0, t1 = CUTS[2], CUTS[3]; u = (T - t0) / (t1 - t0)
    c = cam(R.calle(), lerp(1.5, 1.62, u), PW / 2, 1220); nevada(c, T)
    # deportivo que pasa a nuestro lado y se aleja calle abajo (visto por detrás, alineado con la calzada)
    z = lerp(1.6, 14, ease(u * 1.1)); X = 1.6; G = 1.6
    px = W / 2 + X * 760 / z * (W / (PW / 1.55)); py = 1120 * W / (PW / 1.55) / 1.55 + 0  # aproximado al encuadre
    fx, fy = (PW / 2 + X * 760 / z), (1120 + G * 760 / z)
    zc = lerp(1.5, 1.62, u); cw, ch = PW / zc, PH / zc
    sx = (fx - (PW / 2 - cw / 2)) / cw * W; sy = (fy - (1220 - ch / 2)) / ch * H
    car = R.coche_deportivo(); s = 3.4 / z * 1.35
    paste_c(c, car, sx, sy - car.height * s * .45, s)
    etiqueta(c, T, wt("youtubers") - .05, "YOUTUBERS MILLONARIOS", 640, (255, 206, 60), 72)
    flash(c, T, t0, .1)
    return c

def sc_sofa(T):
    t0, t1 = CUTS[3], CUTS[4]; u = inout((T - t0) / (t1 - t0))
    c = cam(R.piso(), lerp(1.7, 2.1, u), lerp(470, 430, u), lerp(1300, 1320, u))
    etiqueta(c, T, wt("sofá") - .05, "SOFÁ PRESTADO", 760, (255, 160, 90))
    flash(c, T, t0, .1)
    return c

@lru_cache(None)
def billetes():
    im = Image.new("RGBA", (460, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k, col in enumerate([(230, 160, 120), (120, 180, 220), (230, 160, 120), (150, 200, 140)]):
        d.rounded_rectangle((20 + k * 14, 30 + k * 18, 420 + k * 14, 220 + k * 18), 12, fill=col, outline=tuple(int(v * .7) for v in col), width=4)
        d.text((220 + k * 14, 125 + k * 18), ["50 €", "20 €", "50 €", "10 €"][k], font=font(F_ANTON, 60), fill=tuple(int(v * .55) for v in col), anchor="mm")
    return im

def sc_alquiler(T):
    t0, t1 = CUTS[4], CUTS[5]; u = inout((T - t0) / (t1 - t0))
    c = cam(R.piso(), lerp(1.35, 1.5, u), PW / 2, 1220)
    bx, by = resp(T); g = ease((T - T_450) / .5) if T >= T_450 else 0
    paste_c(c, billetes(), 560 + bx, lerp(1450, 900, g) + by, lerp(1.0, .55, g), alpha=1 - .9 * clamp((T - T_450 - .4) / .4), rot=-8)
    M.poner(c, "pinza", 600 + bx, lerp(1980, 2300, g) + by, "d", 1.0, -8, 1.0)
    precio(c, T, T_450 - .05, T_50 - .1, "ALQUILER", "- 450 €", (255, 120, 100))
    precio(c, T, T_50 - .05, t1, "ME QUEDAN", "50 €", (255, 120, 100), c2=(255, 120, 100))
    flash(c, T, t0, .1)
    return c

@lru_cache(None)
def pantalla_grabando():
    p = cam(R.nieve_dia(), 2.6, PW / 2 + 140, 1050).resize((448, 948)); d = ImageDraw.Draw(p)
    d.rounded_rectangle((150, 60, 300, 104), 20, fill=(0, 0, 0, 140)); d.ellipse((168, 72, 188, 92), fill=(240, 40, 40)); d.text((240, 82), "0:07", font=font(F_UI, 26), fill=WHITE, anchor="mm")
    d.ellipse((174, 800, 274, 900), outline=(255, 255, 255), width=8); d.rounded_rectangle((204, 830, 244, 870), 8, fill=(240, 40, 40))
    return p

def sc_video(T):
    t0, t1 = CUTS[5], CUTS[6]; u = inout((T - t0) / (t1 - t0))
    c = cam(R.nieve_dia(), lerp(1.35, 1.45, u), PW / 2, 1300); nevada(c, T, 140)
    bx, by = resp(T); k = ease((T - t0) / .3)
    movil_en_mano(c, T, pantalla_grabando(), 560 + bx, lerp(1900, 1060, k) + by, 1.2, 4)
    flash(c, T, t0, .1)
    return c

@lru_cache(None)
def pantalla_cero():
    p = Image.new("RGBA", (448, 948), (18, 18, 22, 255)); d = ImageDraw.Draw(p)
    th = cam(R.nieve_dia(), 2.0, PW / 2, 1100).resize((448, 252)); p.paste(th, (0, 140))
    d.rounded_rectangle((360, 360, 436, 386), 6, fill=(0, 0, 0)); d.text((398, 373), "0:42", font=font(F_UI, 18), fill=WHITE, anchor="mm")
    d.text((24, 420), "MI PRIMER DÍA EN ANDORRA", font=font(F_ANTON, 34), fill=WHITE, anchor="lm")
    d.text((24, 462), "hace 6 horas", font=font(F_REG, 22), fill=(170, 170, 180), anchor="lm")
    d.text((224, 560), "0", font=font(F_ANTON, 170), fill=(255, 90, 90), anchor="mm"); d.text((224, 680), "VISUALIZACIONES", font=font(F_ANTON, 44), fill=(255, 90, 90), anchor="mm")
    return p

def sc_cero(T):
    t0 = CUTS[6]
    c = cam(R.piso(), 2.3, 470, 1300).filter(ImageFilter.GaussianBlur(12)); c.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 90)))
    bx, by = resp(T); z = 1.45 + .06 * ease((T - t0) / .8)
    movil_en_mano(c, T, pantalla_cero(), 540 + bx, 860 + by, z * .95, 0)
    flash(c, T, t0, .14, (255, 80, 80), 120)
    return c

def sc_pregunta(T):
    t0, t1 = CUTS[7], CUTS[8]; u = inout((T - t0) / (t1 - t0))
    c = cam(R.mirador(), lerp(1.3, 1.4, u), PW / 2, 1300); nevada(c, T, 160)
    d = ImageDraw.Draw(c); k = min(1, back((T - t0 - .05) / .3))
    text(d, (W / 2, 620), "¿TÚ TE HABRÍAS", 104 * k, WHITE, stroke=12); text(d, (W / 2, 740), "VENIDO?", 132 * k, YEL, stroke=12)
    if T >= t0 + .5:
        kk = min(1, back((T - t0 - .5) / .3)); f = font(F_UI, 34 * kk); tw = d.textlength("DÍMELO EN COMENTARIOS", font=f)
        d.rounded_rectangle((W / 2 - tw / 2 - 30, 840, W / 2 + tw / 2 + 30, 910), 30, fill=(255, 255, 255)); d.text((W / 2, 875), "DÍMELO EN COMENTARIOS", font=f, fill=OL, anchor="mm")
    flash(c, T, t0, .1)
    return c

# --- bar: el POV está sentado en la barra; el millonario se sienta a la derecha
def barra_frente(c):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.polygon([(0, 1500), (W, 1460), (W, H), (0, H)], fill=(120, 72, 40)); d.polygon([(0, 1500), (W, 1460), (W, 1490), (0, 1530)], fill=(176, 116, 62))
    for k in range(10): y = 1560 + k * 40; d.line((0, y + 6, W, y - 30), fill=(104, 62, 34), width=3)
    c.alpha_composite(lay)
    d = ImageDraw.Draw(c); d.polygon([(150, 1480), (300, 1480), (285, 1640), (165, 1640)], fill=(200, 220, 230, 140)); d.rectangle((168, 1560, 282, 1636), fill=(190, 120, 50))   # nuestra copa

@lru_cache(None)
def mill(boca=0, dedo=False): return R.millonario(boca / 4, 0, dedo)

def sc_bar(T):
    t0, t1 = CUTS[8], CUTS[9]; u = inout((T - t0) / (t1 - t0))
    c = cam(R.bar(), lerp(1.35, 1.6, u), PW / 2 + 60, lerp(1150, 1100, u))
    g = ease((T - T_SENTO + .15) / .5) if T >= T_SENTO - .15 else 0
    if g > 0: paste_c(c, mill(0), lerp(1400, 800, g), 1080, 1.15)
    barra_frente(c)
    bx, by = resp(T); M.poner(c, "palma", 360 + bx, 1960 + by, "i", 1.0, 30, 1.0)
    etiqueta(c, T, wt("Escaldes") - .05, "BAR · ESCALDES", 640, (255, 150, 210), 70, T_SENTO - .2)
    flash(c, T, t0, .1)
    return c

def sc_reloj(T):
    t0, t1 = CUTS[9], CUTS[10]; u = inout((T - t0) / (t1 - t0))
    c = cam(R.bar(), 2.2, PW / 2 + 200, 1200).filter(ImageFilter.GaussianBlur(8))
    m = mill(0); z = lerp(2.2, 2.5, u)   # primer plano del reloj
    paste_c(c, m, W / 2 - (515 - 450) * z, H / 2 - (1032 - 650) * z + 40, z)
    R.glow(c, [(W / 2, H / 2 + 40, 90)], (255, 230, 140, 120), 30)
    d = ImageDraw.Draw(c)
    for k in range(5):   # destellos del oro
        a = T * 3 + k * 1.3; x, y = W / 2 + 160 * math.cos(a), H / 2 + 40 + 160 * math.sin(a)
        L = 30 * abs(math.sin(T * 6 + k)); d.polygon([(x, y - L), (x + 6, y), (x, y + L), (x - 6, y)], fill=(255, 250, 220)); d.polygon([(x - L, y), (x, y - 6), (x + L, y), (x, y + 6)], fill=(255, 250, 220))
    precio(c, T, T_30 - .05, t1, "SU RELOJ", "30.000 €", (255, 206, 60), 620, (255, 206, 60))
    flash(c, T, t0, .1)
    return c

@lru_cache(1)
def env_y():
    """Envolvente de volumen de la voz del millonario por fotograma (para mover la boca solo cuando habla él)."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(SRC, "Y01.mp3"), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768; n = len(a) // (16000 // FPS)
    e = np.array([np.sqrt(np.mean(a[i * 533:(i + 1) * 533] ** 2)) for i in range(n)]); return e / (e.max() + 1e-6)

def sc_habla(T):
    t0, t1 = CUTS[10], CUTS[11]; u = inout((T - t0) / (t1 - t0))
    c = cam(R.bar(), 1.9, PW / 2 + 120, 1150).filter(ImageFilter.GaussianBlur(6))
    i = int((T - OFF["Y01"]) * FPS); e = env_y(); v = e[i] if 0 <= i < len(e) else 0
    boca = int(round(min(4, v * 7))) if v > .12 else 0
    paste_c(c, mill(boca), W / 2 + 40, lerp(1150, 1110, u), lerp(1.55, 1.7, u))
    barra_frente(c)
    if T >= T_4M - .05:
        k = min(1, back((T - T_4M + .05) / .3)); d = ImageDraw.Draw(c); f = font(F_ANTON, 64 * k); tw = d.textlength("4.000.000", font=f)
        c.alpha_composite(soft((W, H), lambda dd: dd.rounded_rectangle((W / 2 - tw / 2 - 90, 520, W / 2 + tw / 2 + 40, 640), 30, fill=(0, 0, 0, 120)), 12)); d = ImageDraw.Draw(c)
        d.rounded_rectangle((W / 2 - tw / 2 - 90, 510, W / 2 + tw / 2 + 40, 630), 30, fill=(255, 255, 255)); ic_user(d, W / 2 - tw / 2 - 45, 566, (230, 40, 60))
        d.text((W / 2 - 25, 570), "4.000.000", font=f, fill=OL, anchor="mm"); d.text((W / 2 - 25, 650), "SEGUIDORES", font=font(F_ANTON, 40 * k), fill=WHITE, anchor="mm", stroke_width=6, stroke_fill=OL)
    flash(c, T, t0, .1)
    return c

def sc_sobre(T):
    t0, t1 = CUTS[11], CUTS[12]; u = inout((T - t0) / (t1 - t0))
    c = cam(R.bar(), 1.6, PW / 2 + 60, 1120)
    paste_c(c, mill(0), 820, 1080, 1.15); barra_frente(c)
    g = ease((T - t0 - .1) / .9)
    paste_c(c, R.sobre(True), lerp(900, 560, g), lerp(1520, 1700, g), lerp(.7, 1.15, g), rot=lerp(20, -6, g))
    bx, by = resp(T); M.poner(c, "palma", 360 + bx, 1960 + by, "i", 1.0, 30, 1.0)
    precio(c, T, T_2000 - .05, T_COND - .1, "POR UN VÍDEO", "2.000 €", (120, 230, 140), 640, (120, 230, 140))
    etiqueta(c, T, T_COND - .05, "UNA CONDICIÓN…", 640, (255, 206, 60), 80)
    flash(c, T, t0, .1)
    return c

def sc_secreto(T):
    t0, t1 = CUTS[12], CUTS[13]; u = inout((T - t0) / (t1 - t0))
    c = cam(R.bar(), 1.9, PW / 2 + 120, 1150).filter(ImageFilter.GaussianBlur(6))
    paste_c(c, mill(0, True), W / 2 + 40, lerp(1150, 1120, u), lerp(1.6, 1.75, u))
    barra_frente(c)
    c.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 20, 60)))
    sello(c, T, t0 + .25, "NADIE PUEDE SABERLO", 1500)
    flash(c, T, t0, .1)
    return c

RAYO = [(560, 0), (520, 520), (580, 560), (490, 1100), (560, 1140), (470, H)]
@lru_cache(None)
def lado_a():
    c = cam(R.bar(), 1.7, PW / 2 - 100, 1150); c = c.filter(ImageFilter.GaussianBlur(3)); paste_c(c, R.sobre(True), 250, 960, .8, rot=-8)
    return c
@lru_cache(None)
def lado_b():
    c = cam(R.calle(), 1.5, PW / 2, 1200); ph = R.movil(pantalla=pantalla_grabando()); paste_c(c, ph, 800, 1000, .95, rot=6)
    return c
def sc_elige(T):
    hiA = 1.0 if T < T_O else .35; hiB = 1.0 if T >= T_O else .35
    c = lado_b().copy(); mL = Image.new("L", (W, H), 0); ImageDraw.Draw(mL).polygon([(0, 0)] + RAYO + [(0, H)], fill=255); c.paste(lado_a(), (0, 0), mL)
    nevada(c, T, 120)
    for poly, h in (([(0, 0)] + RAYO + [(0, H)], hiA), ([(W, 0)] + RAYO + [(W, H)], hiB)):
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).polygon(poly, fill=(0, 0, 0, int(170 * (1 - h)))); c.alpha_composite(lay)
    c.alpha_composite(soft((W, H), lambda dd: dd.line(RAYO, fill=(120, 200, 255, 255), width=30), 16)); d = ImageDraw.Draw(c); d.line(RAYO, fill=(235, 245, 255), width=9)
    for cx, t1, t2, col, h, tin in ((270, "ACEPTAR", "EL SOBRE", (120, 230, 140), hiA, T_ACEPTO), (810, "A MI", "MANERA", (120, 200, 255), hiB, T_O - .05)):
        if T < tin: continue
        k = min(1, back((T - tin) / .3)) * (1 + .08 * h)
        text(d, (cx, 1300), t1, 96 * k, col if h > .5 else (190, 190, 200), stroke=10); text(d, (cx, 1405), t2, 96 * k, col if h > .5 else (190, 190, 200), stroke=10)
    flash(c, T, T_ACEPTO, .14)
    return c

ESC = [sc_llegada, sc_madre, sc_ricos, sc_sofa, sc_alquiler, sc_video, sc_cero, sc_pregunta, sc_bar, sc_reloj, sc_habla, sc_sobre, sc_secreto, sc_elige]
def escena(T):
    for i in range(len(ESC)):
        if CUTS[i] <= T < CUTS[i + 1]: return i
    return len(ESC) - 1

def frame(T):
    i = escena(T); c = mirada(ESC[i](T), T, .5 if i in (10, 12, 13) else 1.0)
    hud(c, T)
    if T < T_ACEPTO - .05: c.alpha_composite(banda())
    caption(c, T)
    a = np.asarray(c.convert("RGB"), np.int16) + grain(int(T * FPS) % 6)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")

def render(i):
    fa, fb = round(CUTS[i] * FPS), round(CUTS[i + 1] * FPS)
    part = os.path.join(TMP, f"e{i}.part.mp4"); out = os.path.join(TMP, f"e{i}.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", part], stdin=subprocess.PIPE)
    for f in range(fa, fb): p.stdin.write(frame(f / FPS).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(part, out)
    return i

def mezcla(wav):
    s = lambda n: os.path.join(SFXD, n + ".mp3"); sc = lambda n: os.path.join(SFX_CASA, n + ".mp3")
    SFX = [(s("bus"), 0, -2), (s("nieve"), .4, -6), (s("movil"), CUTS[1] - .05, 0), (sc("whoosh"), CUTS[2] - .2, -3), (s("nieve"), CUTS[2], -9),
           (sc("whoosh"), CUTS[3] - .2, -5), (sc("caja"), T_450 - .05, -1), (sc("boom"), T_50 - .05, -8), (s("nieve"), CUTS[5], -8), (sc("boom"), CUTS[6], -4),
           (sc("whoosh"), CUTS[7] - .2, -4), (s("bar"), CUTS[8], -4), (sc("brillo"), T_30 - .05, -2), (sc("whoosh"), CUTS[10] - .2, -6), (sc("caja"), T_4M - .05, -6),
           (s("bar"), CUTS[11] - 2.0, -2), (sc("sello"), CUTS[12] + .2, -2), (sc("whoosh"), T_ACEPTO - .25, -2), (sc("whoosh"), T_O - .2, -5)]
    ins, flt, vz = [], [], []
    for k, l in enumerate(LINEAS):
        ins += ["-i", os.path.join(SRC, l + ".mp3")]; ms = int(OFF[l] * 1000)
        flt.append(f"[{k}:a]aresample=48000,adelay={ms}|{ms},apad[l{k}]"); vz.append(f"[l{k}]")
    flt.append("".join(vz) + f"amix=inputs=3:normalize=0:duration=longest,acompressor=threshold=-18dB:ratio=3:attack=5:release=120,loudnorm=I=-15:TP=-1.5:LRA=9,atrim=0:{TOTAL:.2f}[v]")
    n0 = len(LINEAS)
    for k, (p, t, db) in enumerate(SFX):
        ins += ["-i", p]; ms = int(max(0, t) * 1000); flt.append(f"[{n0 + k}:a]aresample=48000,loudnorm=I=-26:TP=-6,volume={db}dB,adelay={ms}|{ms},apad[s{k}]")
    flt.append("[v]" + "".join(f"[s{k}]" for k in range(len(SFX))) + f"amix=inputs={len(SFX) + 1}:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.95[m]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(flt), "-map", "[m]", "-ac", "2", wav], check=True)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        os.makedirs("/tmp/and_chk", exist_ok=True); ims = []
        for i in range(len(ESC)):
            for q in (.35, .9):
                t = lerp(CUTS[i], CUTS[i + 1], q); ims.append(frame(t).resize((216, 384)))
        sh = Image.new("RGB", (216 * 7, 384 * 4))
        for k, im in enumerate(ims): sh.paste(im, ((k % 7) * 216, (k // 7) * 384))
        sh.save("/tmp/and_chk/hoja.jpg", quality=85)
        print("TOTAL", round(TOTAL, 2), [round(x, 2) for x in CUTS]); sys.exit()
    with Pool(3) as p: list(p.imap_unordered(render, range(len(ESC))))
    lst = os.path.join(TMP, "list.txt"); open(lst, "w").write("".join(f"file 'e{i}.mp4'\n" for i in range(len(ESC))))
    hq = os.path.join(TMP, "hq.mp4"); subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", hq], check=True)
    wav = os.path.join(TMP, "mezcla.wav"); mezcla(wav)
    out = os.path.join(OUT, "500_euros_en_andorra_parte1.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", hq, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-maxrate", "5000k", "-bufsize", "10000k",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], check=True)
    print("ok", out, round(TOTAL, 2))
