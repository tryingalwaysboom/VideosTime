"""La casa de 1 dólar (reforma) — Parte 1: el salón (~25 s, 1080x1920, 30 fps).
python3 salon1.py frames -> fotogramas de control · python3 salon1.py -> vídeo final"""
import json, math, os, random, subprocess, sys
from functools import lru_cache
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import art as A, salon as SL, manos as M, bodycam as BC
from art import W, H, PW, PH, font, F_ANTON, F_UI, F_REG, lerp
from ep1 import cam, text, flash, ease, back, clamp, inout, paste_c, banda, grain, mirada, YEL, WHITE, OL, RED, GRIS, ic_coin, ic_casa, ic_cal, soft

HERE = os.path.dirname(os.path.abspath(__file__)); FPS = 30
SRC = os.path.join(HERE, "..", "descargas", "casa_salon"); SFXD = os.path.join(HERE, "..", "descargas", "casa_sfx")
TMP = os.path.join(HERE, "tmp_salon"); OUT = os.path.join(HERE, "out"); os.makedirs(TMP, exist_ok=True)
VOZ = os.path.join(SRC, "V01.mp3")
DISP = {"olía": "olía a", "300": "$300", "1840.": "$1,840.", "¡Fuera": "¡Fuera"}
RAW = json.load(open(os.path.join(SRC, "V01.json")))
WD = [(DISP.get(w["p"], w["p"]), w["inicio"], w["fin"]) for w in RAW]
def wt(word, n=1):
    k = 0
    for w, a, b in WD:
        if w.strip("¡!¿?.,").lower().startswith(word.strip("¡!¿?.,").lower()):
            k += 1
            if k == n: return a
    raise KeyError(word)
VDUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", VOZ], capture_output=True, text=True).stdout)
TOTAL = VDUR + .3

# ------------------------------------------------------------------ tiempos clave
T_SAB1, T_SAB2 = wt("sábanas") - .1, wt("polvo") - .15
T_MOQ, T_ARR = wt("moqueta"), wt("arranqué") - .2
T_ESTO = wt("esto")
T_LIJ, T_BAR, T_BRI = wt("Lijado"), wt("barniz"), wt("brilla")
T_300, T_QUE = wt("$300"), wt("$1,840.")
T_PAR, T_VER, T_AZU, T_TU = wt("paredes"), wt("Verde"), wt("azul"), wt("Tú")
CUTS = [0.0, wt("Fuera") - .08, T_MOQ - .2, wt("Y", 2) - .05, T_LIJ - .1, T_BRI - .08, wt("Llevo") - .1, T_VER - .25, TOTAL]

# ------------------------------------------------------------------ subtítulos
def chunks():
    out, g = [], []
    for w in WD:
        g.append(w)
        if len(g) == 3 or w[0][-1] in ".,!?" or (len(g) == 2 and len(g[0][0] + g[1][0]) > 13): out.append(g); g = []
    if g: out.append(g)
    return out
CH = chunks()
def caption(c, T):
    if T >= CUTS[7] - .05: return
    for i, g in enumerate(CH):
        t0, t1 = g[0][1], g[-1][2]; nxt = CH[i + 1][0][1] if i + 1 < len(CH) else 1e9
        if not (t0 - .05 <= T < min(t1 + .4, nxt - .05)): continue
        d = ImageDraw.Draw(c); k = .86 + .14 * back((T - t0 + .05) / .14)
        f = font(F_ANTON, 94 * k); ws = [d.textlength(w + " ", font=f) for w, _, _ in g]; tot = sum(ws) - d.textlength(" ", font=f)
        if tot > 860: f = font(F_ANTON, 94 * k * 860 / tot); ws = [d.textlength(w + " ", font=f) for w, _, _ in g]; tot = sum(ws) - d.textlength(" ", font=f)
        x = W / 2 - tot / 2; y = 1170
        for j, ((w, a, b), wd) in enumerate(zip(g, ws)):
            fin = g[j + 1][1] if j + 1 < len(g) else b + .4
            col = YEL if a - .03 <= T < fin - .03 else (WHITE if T >= a - .03 else (215, 215, 222))
            d.text((x, y), w, font=f, fill=col, anchor="lm", stroke_width=10, stroke_fill=OL); x += wd
        return

# ------------------------------------------------------------------ barra superior
@lru_cache(1)
def hud_base():
    im = Image.new("RGBA", (W, 400), (0, 0, 0, 0)); x0, y0, x1, y1 = 36, 238, 1044, 348
    im.alpha_composite(soft((W, 400), lambda dd: dd.rounded_rectangle((x0, y0 + 8, x1, y1 + 10), 26, fill=(0, 0, 0, 130)), 10))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0, y0, x1, y1), 26, fill=(12, 10, 26, 215), outline=(255, 170, 70, 140), width=2)
    d.rounded_rectangle((x0 + 14, y0 + 12, x0 + 160, y0 + 56), 12, fill=(255, 170, 70)); d.text((x0 + 87, y0 + 34), "PARTE 1", font=font(F_ANTON, 32), fill=OL, anchor="mm")
    d.line((x0 + 16, y0 + 64, x1 - 16, y0 + 64), fill=(255, 255, 255, 30), width=2)
    d.text((x0 + 18, y0 + 87), "OBJETIVO", font=font(F_UI, 20), fill=(255, 170, 70), anchor="lm"); d.text((x0 + 132, y0 + 87), "Arreglar el salón", font=font(F_UI, 24), fill=WHITE, anchor="lm")
    d.text((x1 - 20, y0 + 87), "12 MESES PARA TERMINAR", font=font(F_UI, 18), fill=GRIS, anchor="rm")
    return im
def hud(c, T):
    if T >= CUTS[7] - .1: return
    base = hud_base()
    if T < .3: c.alpha_composite(base, (0, int(-400 * (1 - ease(T / .3))))); return
    c.alpha_composite(base); d = ImageDraw.Draw(c); x0, y0 = 36, 238
    def pop(t): return 1 + .3 * math.sin(clamp((T - t) / .3) * math.pi) if 0 <= T - t < .3 else 1
    v = int(lerp(2140, 1840, ease((T - T_300) / .6))) if T >= T_300 else 2140
    ic_coin(d, x0 + 230, y0 + 34); d.text((x0 + 256, y0 + 35), f"${v:,}", font=font(F_ANTON, 36 * pop(T_300)), fill=(255, 120, 110) if T_300 <= T < T_300 + 1 else WHITE, anchor="lm")
    pct = 8 if T >= T_BRI else 0
    ic_casa(d, x0 + 470, y0 + 34, (255, 170, 70)); d.text((x0 + 498, y0 + 35), f"CASA {pct}%", font=font(F_ANTON, 34 * pop(T_BRI)), fill=(120, 230, 120) if T >= T_BRI else WHITE, anchor="lm")
    ic_cal(d, x0 + 770, y0 + 34, WHITE); d.text((x0 + 798, y0 + 35), "12 MESES", font=font(F_ANTON, 34), fill=WHITE, anchor="lm")

# ------------------------------------------------------------------ efectos
def polvo_nube(c, T, t0, cx, cy, n=60, seed=3, dur=1.4):
    dt = T - t0
    if not (0 <= dt < dur): return
    rng = np.random.default_rng(seed); d = ImageDraw.Draw(c)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for i in range(n):
        a = rng.uniform(0, 6.28); sp = rng.uniform(150, 600); r = rng.uniform(20, 70) * (1 + dt)
        x = cx + math.cos(a) * sp * dt; y = cy + math.sin(a) * sp * dt * .6 - 120 * dt
        ld.ellipse((x - r, y - r, x + r, y + r), fill=(214, 200, 180, int(110 * (1 - dt / dur))))
    c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(14)))

def destellos(c, T, t0, pts, dur=1.2, s=1.0):
    dt = T - t0
    if not (0 <= dt < dur): return
    d = ImageDraw.Draw(c)
    for i, (x, y) in enumerate(pts):
        u = clamp((dt - i * .08) / .5); k = math.sin(u * math.pi)
        if k <= 0: continue
        L = 46 * k * s
        d.polygon([(x, y - L), (x + 8 * s, y), (x, y + L), (x - 8 * s, y)], fill=(255, 255, 240)); d.polygon([(x - L, y), (x, y - 8 * s), (x + L, y), (x, y + 8 * s)], fill=(255, 255, 240))

def etiqueta(c, T, t0, txt, y=760, col=(255, 206, 60)):
    if T < t0: return
    k = min(1, back((T - t0) / .3)); d = ImageDraw.Draw(c); f = font(F_ANTON, 78 * k); tw = d.textlength(txt, font=f)
    d.rounded_rectangle((W / 2 - tw / 2 - 30, y - 56 * k, W / 2 + tw / 2 + 30, y + 56 * k), 24, fill=col)
    d.text((W / 2, y), txt, font=f, fill=OL, anchor="mm")

# ------------------------------------------------------------------ herramientas en la mano
def lijadora(c, x, y, T):
    j = 4 * math.sin(T * 90); d = ImageDraw.Draw(c)
    d.rounded_rectangle((x - 130 + j, y - 120, x + 130 + j, y + 30), 40, fill=(236, 120, 40)); d.rounded_rectangle((x - 140 + j, y + 10, x + 140 + j, y + 50), 14, fill=(30, 30, 34))
    d.rounded_rectangle((x - 60 + j, y - 170, x + 60 + j, y - 110), 20, fill=(40, 40, 46)); d.text((x + j, y - 50), "PRO", font=font(F_ANTON, 44), fill=(255, 240, 220), anchor="mm")
def brocha(c, x, y):
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((x - 22, y - 140, x + 22, y + 40), 14, fill=(170, 120, 70)); d.rectangle((x - 60, y - 200, x + 60, y - 140), fill=(180, 186, 196))
    d.polygon([(x - 64, y - 200), (x + 64, y - 200), (x + 54, y - 290), (x - 54, y - 290)], fill=(120, 70, 30)); d.polygon([(x - 54, y - 290), (x + 54, y - 290), (x + 40, y - 300), (x - 40, y - 300)], fill=(200, 130, 50))

# ------------------------------------------------------------------ suelo de cerca (moqueta que se arranca / lijado / barniz)
FLOOR_BOX = (0, 0, SL.TS, SL.TS)
def suelo_cerca(capa_fn):
    """Proyecta una textura de suelo compuesta en perspectiva de cerca (mirando al suelo)."""
    tex = capa_fn()
    q = [(-200, 420), (W + 200, 420), (W + 900, H + 300), (-900, H + 300)]
    out = tex.transform((W, H), Image.PERSPECTIVE, SL.coeffs(q, [(0, 0), (SL.TS, 0), (SL.TS, SL.TS), (0, SL.TS)]), Image.BILINEAR)
    c = Image.new("RGBA", (W, H), (40, 30, 24, 255)); c.alpha_composite(out)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle((0, 0, W, 470), fill=(20, 14, 10, 255)); c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(60)))
    return c

def sc_moqueta(T):
    t0, t1 = CUTS[2], CUTS[3]
    p = ease((T - T_ARR) / .75) if T >= T_ARR else 0   # 0 = todo moqueta, 1 = arrancada
    yb = int(SL.TS * (1 - p))   # frontera en coordenadas de la textura (desde abajo hacia el fondo)
    def capa():
        t = SL.tex_parquet_sucio().copy()
        if yb > 0: t.paste(SL.tex_moqueta().crop((0, 0, SL.TS, yb)), (0, 0))
        return t
    c = suelo_cerca(capa)
    # rollo de moqueta en la frontera
    yy = lerp(H + 200, 420, p)
    if 0 < p < 1:
        d = ImageDraw.Draw(c); r = lerp(70, 26, p)
        d.rounded_rectangle((-100, yy - r * 2, W + 100, yy), r, fill=(70, 74, 46)); d.line((-100, yy - r * 1.4, W + 100, yy - r * 1.4), fill=(110, 116, 74), width=int(r * .4))
    if T_MOQ + .9 <= T < T_ARR:   # olor a muerto: ondas verdes
        d = ImageDraw.Draw(c)
        for k in range(3):
            x0 = 300 + k * 240; ph = T * 4 + k
            d.line([(x0 + 30 * math.sin(ph + v / 40), 1400 - v - 60 * ((T * 1.4 + k * .3) % 1)) for v in range(0, 360, 20)], fill=(150, 210, 90, 200), width=12)
    bx, by = BC.respiracion(T * 1.15 + 3, .9)
    if T >= T_ARR - .3:
        yh = max(1250, min(1800, yy + 300)); M.poner(c, "pinza", 260 + bx, yh + 280, "i", 1.0, 14, 1.0); M.poner(c, "pinza", 800 + bx, yh + 280, "d", 1.0, -14, 1.0)
    else:
        M.poner(c, "palma", 300 + bx, 1880 + by * 1.6 - 330 + 300, "i", 1.0, 10, 1.0)
    flash(c, T, t0, .1)
    return c

def sc_lijar(T):
    t0, t1 = CUTS[4], CUTS[5]
    sx = lerp(-.1, 1.1, ease((T - t0) / (T_BAR - t0 - .1)))   # avance del lijado (fracción del ancho)
    vb = ease((T - T_BAR) / (T_BRI - T_BAR - .15)) if T >= T_BAR else 0   # avance del barniz
    def capa():
        t = SL.tex_parquet_sucio().copy()
        xs = int(SL.TS * sx)
        if xs > 0: t.paste(SL.tex_parquet_lijado().crop((0, 0, min(SL.TS, xs), SL.TS)), (0, 0))
        if vb > 0:
            xv = int(SL.TS * vb); t.paste(SL.tex_parquet_brillo().crop((0, 0, xv, SL.TS)), (0, 0))
        return t
    c = suelo_cerca(capa)
    bx, by = BC.respiracion(T * 1.15 + 3, .9)
    if T < T_BAR:
        x = lerp(260, 820, clamp(sx)); y = 1420 + 60 * math.sin(T * 7)
        M.poner(c, "puno", x + bx, y + 560, "d", 1.0, 0, 1.0); lijadora(c, x + bx, y + 560 - 300, T)
        polvo_nube(c, T, t0 + .2, x, y, 30, 5, 1.2)
    else:
        x = lerp(300, 820, clamp(vb)); y = 1400 + 40 * math.sin(T * 9)
        brocha(c, x + bx, y + 560 - 250); M.poner(c, "puno", x + bx, y + 560, "d", 1.0, 0, 1.0)
    flash(c, T, t0, .1)
    return c

def sabanas_volando(c, T, z, cx, cy):
    x0, y0, x1, y1 = SL.BACK
    items = [((x1 - 370, y1 - 262, x1 - 20, y1 + 4), 1, T_SAB1), ((300 - 190, 1640 - 450, 300 + 190, 1640), 2, T_SAB2), ((520, 1440, 880, 1610), 3, T_SAB2 + .08)]
    pl = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    for box, seed, t0 in items:
        u = clamp((T - t0) / .55)
        if u >= 1: continue
        SL.sabana_sobre(pl, box, seed, int(255 * (1 - u ** 2)), dy=-700 * ease(u), dx=(200 if seed % 2 else -200) * ease(u), rot=(20 if seed % 2 else -25) * u)
    c.alpha_composite(cam(pl, z, cx, cy))

def sc_wide(estado, z0, z1, t0, t1, cy0=1250, cy1=1200):
    def fn(T):
        u = inout((T - t0) / (t1 - t0)); z = lerp(z0, z1, u); cy = lerp(cy0, cy1, u)
        return cam(SL.salon(*estado), z, 648, cy), z, cy
    return fn

def sc_entrada(T):
    c, z, cy = sc_wide(("vieja", "moqueta", True), 1.0, 1.15, CUTS[0], CUTS[1])(T)
    BC_ = BC.respiracion(T * 1.15 + 3, .9); M.poner(c, "llave", 820 + BC_[0], 1880 + BC_[1] * 1.6 - 250 + 300 * ease((T - 2.6) / .6), "d", 1.0, -12, 1.0)
    return c

def sc_sabanas(T):
    t0, t1 = CUTS[1], CUTS[2]; u = inout((T - t0) / (t1 - t0)); z = lerp(1.15, 1.22, u); cy = 1240
    c = cam(SL.salon("vieja", "moqueta", False), z, 648, cy)
    sabanas_volando(c, T, z, 648, cy)
    polvo_nube(c, T, T_SAB1 + .1, 820, 1050, 50, 1); polvo_nube(c, T, T_SAB2 + .05, 360, 1250, 60, 2)
    bx, by = BC.respiracion(T * 1.15 + 3, .9)
    for side, x, tt in (("d", 800, T_SAB1), ("i", 280, T_SAB2)):
        k = math.sin(clamp((T - tt + .15) / .6) * math.pi)
        M.poner(c, "pinza", x + bx, 1700 + by - 260 * k, side, 1.0, (-12 if side == "d" else 12), 1.0)
    flash(c, T, t0, .1)
    return c

def sc_debajo(T):
    c, z, cy = sc_wide(("vieja", "parquet_sucio", False), 1.05, 1.2, CUTS[3], CUTS[4], 1300, 1240)(T)
    if T >= T_ESTO:   # barrido de luz por el suelo
        u = clamp((T - T_ESTO) / .9); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        x = lerp(-300, W + 300, u); ImageDraw.Draw(lay).polygon([(x - 120, 900), (x + 60, 900), (x + 260, H), (x - 40, H)], fill=(255, 240, 200, 110))
        c.alpha_composite(lay.filter(ImageFilter.GaussianBlur(30)))
        destellos(c, T, T_ESTO + .2, [(300, 1250), (760, 1380), (520, 1600), (880, 1700)])
    etiqueta(c, T, wt("Parquet"), "ROBLE ORIGINAL")
    return c

def sc_brilla(T):
    c, z, cy = sc_wide(("vieja", "parquet_brillo", False), 1.1, 1.22, CUTS[5], CUTS[6], 1300, 1240)(T)
    destellos(c, T, CUTS[5] + .05, [(260, 1300), (700, 1250), (480, 1550), (900, 1650), (620, 1800)], 1.4, 1.3)
    flash(c, T, CUTS[5], .12, (255, 250, 230), 150)
    return c

def antes_despues(T):
    a = cam(SL.salon("vieja", "moqueta", True), 1.15, 648, 1250); b = cam(SL.salon("vieja", "parquet_brillo", False), 1.15, 648, 1250)
    c = Image.new("RGBA", (W, H)); c.paste(a.crop((W // 4, 0, W // 4 + W // 2, H)), (0, 0)); c.paste(b.crop((W // 4, 0, W // 4 + W // 2, H)), (W // 2, 0))
    d = ImageDraw.Draw(c); d.rectangle((W // 2 - 4, 0, W // 2 + 4, H), fill=(255, 255, 255))
    for x, t, col in ((W / 4, "ANTES", (230, 80, 70)), (3 * W / 4, "DESPUÉS", (90, 200, 110))):
        d.rounded_rectangle((x - 150, 420, x + 150, 500), 20, fill=col); d.text((x, 460), t, font=font(F_ANTON, 58), fill=WHITE, anchor="mm")
    if T >= T_300:
        k = min(1, back((T - T_300) / .3)); text(d, (W / 2, 820), "- $300", 170 * k, RED, stroke=12)
    flash(c, T, CUTS[6], .1)
    return c

RAYO = [(560, 0), (520, 520), (580, 560), (490, 1100), (560, 1140), (470, H)]
def sc_elige(T):
    t0 = CUTS[7]; hiA = 1.0 if T_VER <= T < T_AZU else (.35 if T_AZU <= T < T_TU else 1.0); hiB = 1.0 if T_AZU <= T < T_TU else (.35 if T_VER <= T < T_AZU else 1.0)
    L = cam(SL.salon("salvia", "parquet_brillo", False), 1.15, 648 - 150, 1250); R = cam(SL.salon("noche", "parquet_brillo", False), 1.15, 648 + 150, 1250)
    c = R.copy(); mL = Image.new("L", (W, H), 0); ImageDraw.Draw(mL).polygon([(0, 0)] + RAYO + [(0, H)], fill=255); c.paste(L, (0, 0), mL)
    for poly, h in (([(0, 0)] + RAYO + [(0, H)], hiA), ([(W, 0)] + RAYO + [(W, H)], hiB)):
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).polygon(poly, fill=(0, 0, 0, int(170 * (1 - h)))); c.alpha_composite(lay)
    c.alpha_composite(soft((W, H), lambda dd: dd.line(RAYO, fill=(255, 190, 90, 255), width=30), 16)); d = ImageDraw.Draw(c); d.line(RAYO, fill=(255, 245, 220), width=9)
    for cx, t1, t2, col, h, tin in ((275, "VERDE", "SALVIA", (170, 220, 150), hiA, T_VER - .05), (800, "AZUL", "NOCHE", (120, 170, 255), hiB, T_AZU - .05)):
        if T < tin: continue
        k = min(1, back((T - tin) / .3)) * (1 + .08 * h)
        text(d, (cx, 1300), t1, 100 * k, col if h > .5 else (190, 190, 200), stroke=10); text(d, (cx, 1405), t2, 100 * k, col if h > .5 else (190, 190, 200), stroke=10)
    if T < T_VER - .05:   # antes de las opciones: la pared vieja y la pregunta
        c2 = cam(SL.salon("vieja", "parquet_brillo", False), 1.2, 648, 1240); text(ImageDraw.Draw(c2), (W / 2, 760), "¿DE QUÉ COLOR?", 120, WHITE, stroke=12); return c2
    flash(c, T, T_VER - .05, .14)
    return c

ESC = [sc_entrada, sc_sabanas, sc_moqueta, sc_debajo, sc_lijar, sc_brilla, antes_despues, sc_elige]
def escena(T):
    for i in range(len(ESC)):
        if CUTS[i] <= T < CUTS[i + 1]: return i
    return len(ESC) - 1

def frame(T):
    i = escena(T); c = mirada(ESC[i](T), T, .5 if i in (6, 7) else 1.0)
    hud(c, T)
    if T < CUTS[7] - .05: c.alpha_composite(banda())
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
    s = lambda n: os.path.join(SFXD, n + ".mp3")
    SFX = [(s("sabana"), T_SAB1 - .55, 0), (s("polvo"), T_SAB1 + .05, -2), (s("sabana"), T_SAB2 - .55, -1), (s("polvo"), T_SAB2 + .05, 0),
           (s("moqueta"), T_ARR - .05, 3), (s("whoosh"), CUTS[3] - .2, -4), (s("brillo"), T_ESTO + .15, 0),
           (s("lijadora"), CUTS[4] + .05, 1), (s("lijadora"), CUTS[4] + .95, 1), (s("barniz"), T_BAR, 2), (s("barniz"), T_BAR + .7, 2),
           (s("brillo"), CUTS[5], 2), (s("caja"), T_300 - .05, 0), (s("whoosh"), CUTS[7] - .25, -2), (s("whoosh"), T_VER - .2, -4)]
    ins = ["-i", VOZ]; flt = [f"[0:a]aresample=48000,apad=pad_dur=4,acompressor=threshold=-18dB:ratio=3:attack=5:release=120,loudnorm=I=-15:TP=-1.5:LRA=9,atrim=0:{TOTAL:.2f}[v]"]
    for k, (p, t, db) in enumerate(SFX):
        ins += ["-i", p]; ms = int(max(0, t) * 1000); flt.append(f"[{k + 1}:a]aresample=48000,loudnorm=I=-26:TP=-6,volume={db}dB,adelay={ms}|{ms},apad[s{k}]")
    flt.append("[v]" + "".join(f"[s{k}]" for k in range(len(SFX))) + f"amix=inputs={len(SFX) + 1}:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.95[m]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(flt), "-map", "[m]", "-ac", "2", wav], check=True)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        os.makedirs("/tmp/salon_chk", exist_ok=True)
        for i in range(len(ESC)):
            for q in (.3, .85):
                t = lerp(CUTS[i], CUTS[i + 1], q); frame(t).resize((270, 480)).save(f"/tmp/salon_chk/{i}_{q}.jpg")
        print("TOTAL", round(TOTAL, 2), [round(x, 2) for x in CUTS]); sys.exit()
    with Pool(3) as p: list(p.imap_unordered(render, range(len(ESC))))
    lst = os.path.join(TMP, "list.txt"); open(lst, "w").write("".join(f"file 'e{i}.mp4'\n" for i in range(len(ESC))))
    hq = os.path.join(TMP, "hq.mp4"); subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", hq], check=True)
    wav = os.path.join(TMP, "mezcla.wav"); mezcla(wav)
    out = os.path.join(OUT, "la_casa_de_1_dolar_parte1_salon.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", hq, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-maxrate", "5000k", "-bufsize", "10000k",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], check=True)
    print("ok", out, round(TOTAL, 2))
