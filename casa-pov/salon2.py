"""La casa de 1 dólar (reforma) — Parte 2: pintar el salón de azul noche + la caja fuerte escondida.
python3 salon2.py frames -> fotogramas de control · python3 salon2.py -> vídeo final"""
import json, math, os, random, subprocess, sys
from functools import lru_cache
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import art as A, salon as SL, manos as M, bodycam as BC
from art import W, H, PW, PH, font, F_ANTON, F_UI, lerp
from ep1 import cam, text, flash, ease, back, clamp, inout, paste_c, banda, grain, mirada, YEL, WHITE, OL, RED, GRIS, ic_coin, ic_casa, ic_cal, soft
from salon1 import precio, destellos, polvo_nube, sc_wide

HERE = os.path.dirname(os.path.abspath(__file__)); FPS = 30
SRC = os.path.join(HERE, "..", "descargas", "casa_salon2"); SFXD = os.path.join(HERE, "..", "descargas", "casa_sfx")
TMP = os.path.join(HERE, "tmp_salon2"); OUT = os.path.join(HERE, "out"); os.makedirs(TMP, exist_ok=True)
VOZ = os.path.join(SRC, "V01.mp3")
RAW = json.load(open(os.path.join(SRC, "V01.json")))
TXT = "Arranqué el papel de la pared… y detrás había una caja fuerte. Pero vamos por partes: ganó el azul noche. Pintura azul noche: $90 dólares. Rodillo y cinta: $25. Primera mano… segunda mano… y mira qué salón. Me quedan $1,725. ¿Y la caja fuerte? Un cerrajero cobra $200 dólares… o la abro yo con un taladro. Tú decides.".split()
assert len(TXT) == len(RAW), (len(TXT), len(RAW))
WD = [(t, w["inicio"], w["fin"]) for t, w in zip(TXT, RAW)]
def wt(word, n=1):
    k = 0; q = word.strip("¡!¿?.,:").lower()
    for w, a, b in WD:
        if w.strip("¡!¿?.,:").lower().startswith(q):
            k += 1
            if k == n: return a
    raise KeyError(word)
VDUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", VOZ], capture_output=True, text=True).stdout)
TOTAL = VDUR + .3

T_CAJA = wt("caja"); T_GANO = wt("ganó"); T_PINT = wt("Pintura"); T_90 = wt("$90"); T_ROD = wt("Rodillo"); T_25 = wt("$25")
T_PRI = wt("Primera"); T_SEG = wt("segunda"); T_MIRA = wt("mira"); T_QUE = wt("quedan"); T_CAJA2 = wt("caja", 2)
T_CERR = wt("cerrajero"); T_200 = wt("$200"); T_TAL = wt("taladro"); T_TU = wt("Tú")
CUTS = [0.0, wt("Pero") - .08, T_PINT - .1, T_PRI - .1, T_MIRA - .1, wt("Me") - .1, wt("y", 4) - .1, TOTAL]

# ------------------------------------------------------------------ subtítulos y barra (PARTE 2)
def chunks():
    out, g = [], []
    for w in WD:
        g.append(w)
        if len(g) == 3 or w[0][-1] in ".,!?:" or (len(g) == 2 and len(g[0][0] + g[1][0]) > 13): out.append(g); g = []
    if g: out.append(g)
    return out
CH = chunks()
def caption(c, T):
    if T >= CUTS[6] - .05: return
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

@lru_cache(1)
def hud_base():
    im = Image.new("RGBA", (W, 400), (0, 0, 0, 0)); x0, y0, x1, y1 = 36, 238, 1044, 348
    im.alpha_composite(soft((W, 400), lambda dd: dd.rounded_rectangle((x0, y0 + 8, x1, y1 + 10), 26, fill=(0, 0, 0, 130)), 10))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0, y0, x1, y1), 26, fill=(12, 10, 26, 215), outline=(255, 170, 70, 140), width=2)
    d.rounded_rectangle((x0 + 14, y0 + 12, x0 + 160, y0 + 56), 12, fill=(255, 170, 70)); d.text((x0 + 87, y0 + 34), "PARTE 2", font=font(F_ANTON, 32), fill=OL, anchor="mm")
    d.line((x0 + 16, y0 + 64, x1 - 16, y0 + 64), fill=(255, 255, 255, 30), width=2)
    d.text((x0 + 18, y0 + 87), "OBJETIVO", font=font(F_UI, 20), fill=(255, 170, 70), anchor="lm"); d.text((x0 + 132, y0 + 87), "Pintar el salón", font=font(F_UI, 24), fill=WHITE, anchor="lm")
    d.text((x1 - 20, y0 + 87), "12 MESES PARA TERMINAR", font=font(F_UI, 18), fill=GRIS, anchor="rm")
    return im
def hud(c, T):
    if T >= CUTS[6] - .1: return
    base = hud_base()
    if T < .3: c.alpha_composite(base, (0, int(-400 * (1 - ease(T / .3))))); return
    c.alpha_composite(base); d = ImageDraw.Draw(c); x0, y0 = 36, 238
    def pop(t): return 1 + .3 * math.sin(clamp((T - t) / .3) * math.pi) if 0 <= T - t < .3 else 1
    v = int(1840 - 90 * ease((T - T_90) / .5) * (T >= T_90) - 25 * ease((T - T_25) / .5) * (T >= T_25))
    hot = (T_90 <= T < T_90 + 1) or (T_25 <= T < T_25 + 1)
    ic_coin(d, x0 + 230, y0 + 34); d.text((x0 + 256, y0 + 35), f"${v:,}", font=font(F_ANTON, 36 * max(pop(T_90), pop(T_25))), fill=(255, 120, 110) if hot else WHITE, anchor="lm")
    pct = 15 if T >= CUTS[4] else 8
    ic_casa(d, x0 + 470, y0 + 34, (255, 170, 70)); d.text((x0 + 498, y0 + 35), f"CASA {pct}%", font=font(F_ANTON, 34 * pop(CUTS[4])), fill=(120, 230, 120) if T >= CUTS[4] else WHITE, anchor="lm")
    ic_cal(d, x0 + 770, y0 + 34, WHITE); d.text((x0 + 798, y0 + 35), "12 MESES", font=font(F_ANTON, 34), fill=WHITE, anchor="lm")

# ------------------------------------------------------------------ pared de cerca (frontal): papel, yeso, caja fuerte, pintura
@lru_cache(None)
def tex_yeso():
    im = SL.tint((206, 198, 184), SL.noise(W, H, 10, 21, 2)); d = ImageDraw.Draw(im); rng = random.Random(8)
    for _ in range(12):   # grietas y restos de cola
        x, y = rng.uniform(0, W), rng.uniform(0, H); pts = [(x, y)]
        for _ in range(7): x += rng.uniform(-40, 40); y += rng.uniform(15, 60); pts.append((x, y))
        d.line(pts, fill=(150, 140, 126), width=3)
    for _ in range(18):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(20, 70); d.ellipse((x - r, y - r * .6, x + r, y + r * .6), fill=(186, 176, 150))
    return im
@lru_cache(None)
def tex_papel(): return SL.tex_pared("vieja", W, H, seed=5).convert("RGBA")
SAFE = (300, 640, 780, 1120)
@lru_cache(None)
def caja_fuerte():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x0, y0, x1, y1 = SAFE
    d.rectangle((x0 - 30, y0 - 30, x1 + 30, y1 + 30), fill=(60, 54, 50))   # hueco en la pared
    d.rectangle((x0 - 18, y0 - 18, x1 + 18, y1 + 18), fill=(30, 28, 30))
    d.rectangle((x0, y0, x1, y1), fill=(84, 92, 96))
    for k in range(30): d.line((x0, y0 + k * 16, x1, y0 + k * 16), fill=(78 + k % 3 * 4, 86, 90), width=2)
    d.rectangle((x0 + 30, y0 + 30, x1 - 30, y1 - 30), outline=(52, 58, 62), width=8)
    for x in (x0 + 16, x1 - 16):
        for y in (y0 + 16, y1 - 16): d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=(130, 136, 140))
    cx, cy = (x0 + x1) / 2 - 40, (y0 + y1) / 2
    d.ellipse((cx - 90, cy - 90, cx + 90, cy + 90), fill=(40, 42, 46), outline=(160, 166, 170), width=8)
    for a in range(0, 360, 15):
        r = math.radians(a); L = 18 if a % 45 == 0 else 9
        d.line((cx + 80 * math.cos(r), cy + 80 * math.sin(r), cx + (80 - L) * math.cos(r), cy + (80 - L) * math.sin(r)), fill=(200, 200, 200), width=3)
    d.ellipse((cx - 40, cy - 40, cx + 40, cy + 40), fill=(150, 156, 160)); d.polygon([(cx - 8, cy - 90), (cx + 8, cy - 90), (cx, cy - 70)], fill=(230, 60, 50))
    hx = x1 - 80; d.rounded_rectangle((hx - 20, cy - 110, hx + 20, cy + 110), 14, fill=(170, 176, 180)); d.ellipse((hx - 36, cy - 36, hx + 36, cy + 36), fill=(130, 136, 140))
    for _ in range(40):   # óxido
        rng = random.Random(_); x, y, r = rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(4, 14); d.ellipse((x - r, y - r, x + r, y + r), fill=(120, 70, 40, 140))
    d.text(((x0 + x1) / 2, y1 - 50), "1987", font=font(F_ANTON, 40), fill=(170, 160, 120), anchor="mm")
    return im

def pared_cerca(T, rasgado=0.0, safe=True, pintura=0.0, capa2=0.0, cinta=0.0):
    """rasgado 0..1: cuánto papel se ha arrancado (diagonal) · pintura/capa2 0..1: avance del rodillo (izq->der)."""
    c = tex_yeso().copy()
    if safe: c.alpha_composite(caja_fuerte())
    if rasgado < 1:   # papel que aún queda (se arranca en diagonal desde arriba a la izquierda)
        m = Image.new("L", (W, H), 255); md = ImageDraw.Draw(m); e = lerp(-400, 2600, rasgado)
        md.polygon([(0, 0), (e, 0), (e - 900, H * 1.4), (0, H * 1.4)], fill=0) if rasgado > 0 else None
        pap = tex_papel().copy(); pap.putalpha(m); c.alpha_composite(pap)
        if 0 < rasgado < 1:   # tira curvada (reverso claro)
            d = ImageDraw.Draw(c); d.polygon([(e, 0), (e + 140, 60), (e - 760, H * 1.2), (e - 900, H * 1.2)], fill=(232, 222, 196))
    if pintura > 0 or capa2 > 0:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        for k in range(12):   # franjas del rodillo
            x0 = k * W / 12
            if x0 > W * pintura: break
            hgt = min(1, (W * pintura - x0) / (W / 12)) * H
            ld.rectangle((x0, 0, x0 + W / 12 + 4, hgt), fill=(44, 60, 98, 175))
        if capa2 > 0: ld.rectangle((0, 0, W * capa2, H), fill=(36, 50, 86, 255))
        c.alpha_composite(lay)
    d = ImageDraw.Draw(c)
    d.rectangle((0, 1700, W, H), fill=(236, 230, 216)); d.line((0, 1700, W, 1700), fill=(200, 192, 176), width=6)   # rodapié
    if cinta > 0: d.rectangle((0, 1676, W * cinta, 1704), fill=(70, 140, 220))   # cinta de pintor
    return c

def rodillo(c, x, y, wet=True):
    d = ImageDraw.Draw(c)
    d.line((x, y + 40, x, y + 230), fill=(200, 200, 205), width=12); d.line((x, y + 40, x + 120, y + 40), fill=(200, 200, 205), width=12)
    d.rounded_rectangle((x + 40, y - 90, x + 200, y + 40), 30, fill=(44, 60, 98) if wet else (240, 240, 240))
    d.line((x + 70, y - 70, x + 70, y + 20), fill=(80, 100, 140), width=6)

# ------------------------------------------------------------------ escenas
def sc_gancho(T):
    r = lerp(.14, .30, clamp(T / 2.4)) if T < 2.4 else (lerp(.30, .62, clamp((T - 2.4) / (T_CAJA + .1 - 2.4))) if T < T_CAJA + .1 else lerp(.62, 1.0, ease((T - T_CAJA - .1) / .5))); z = 1.0 + (.12 * ease((T - T_CAJA) / .3) if T >= T_CAJA else 0)
    c = pared_cerca(T, rasgado=r)
    if z > 1: c = c.resize((int(W * z), int(H * z)), Image.BILINEAR).crop((int(W * (z - 1) / 2), int(H * (z - 1) / 2) - 40, int(W * (z - 1) / 2) + W, int(H * (z - 1) / 2) - 40 + H))
    bx, by = BC.respiracion(T * 1.15 + 3, .9)
    e = lerp(-400, 2600, r)
    if T < T_CAJA + .2: M.poner(c, "pinza", min(900, e * .45 + 250) + bx, min(1900, 900 + 900 * r) + by, "d", 1.0, -20, 1.0)
    if T >= T_CAJA:
        flash(c, T, T_CAJA, .14, (255, 255, 255), 180)
        k = min(1, back((T - T_CAJA) / .3)); d = ImageDraw.Draw(c)
        text(d, (W / 2, 520), "¿UNA CAJA FUERTE?", 96 * k, (255, 206, 60), stroke=10)
        destellos(c, T, T_CAJA + .1, [(330, 680), (760, 690), (520, 1100)])
    return c

def sc_gano(T):
    t0, t1 = CUTS[1], CUTS[2]; c = cam(SL.salon("vieja", "parquet_brillo", False), lerp(1.5, 1.6, inout((T - t0) / (t1 - t0))), 1296, 2080)
    if T >= T_GANO - .1:
        k = min(1, back((T - T_GANO + .1) / .3)); d = ImageDraw.Draw(c)
        w, h = 700 * k, 300 * k
        d.rounded_rectangle((W / 2 - w / 2, 760 - h / 2, W / 2 + w / 2, 760 + h / 2), 36, fill=(24, 34, 64, 240), outline=(120, 170, 255), width=6)
        if k > .6:
            d.text((W / 2, 690), "ELEGISTEIS", font=font(F_ANTON, 56), fill=(150, 190, 255), anchor="mm"); text(d, (W / 2, 790), "AZUL NOCHE 🌙".replace(" 🌙", ""), 110, WHITE, stroke=0)
    flash(c, T, t0, .12)
    return c

def sc_precios(T):
    t0, t1 = CUTS[2], CUTS[3]
    cin = ease((T - T_ROD) / .9) if T >= T_ROD else 0
    c = pared_cerca(T, rasgado=1, safe=False, cinta=cin)
    bx, by = BC.respiracion(T * 1.15 + 3, .9)
    # bote de pintura y rodillo nuevos en primer plano
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((180, 1180, 520, 1560), 30, fill=(200, 200, 206)); d.ellipse((180, 1140, 520, 1220), fill=(36, 50, 86)); d.rounded_rectangle((220, 1300, 480, 1460), 16, fill=(36, 50, 86))
    d.text((350, 1380), "AZUL\nNOCHE", font=font(F_ANTON, 50), fill=WHITE, anchor="mm", align="center")
    if T >= T_ROD - .1: rodillo(c, 700, 1280, wet=False)
    M.poner(c, "pinza", lerp(200, 600, cin) + bx, 1980 + by, "i", 1.0, 20, 1.0)
    precio(c, T, T_90 - .05, T_ROD - .05, "PINTURA AZUL NOCHE", "- $90", (255, 120, 100), 700)
    precio(c, T, T_25 - .05, t1, "RODILLO + CINTA", "- $25", (255, 120, 100), 700)
    flash(c, T, t0, .1)
    return c

def sc_pintar(T):
    t0, t1 = CUTS[3], CUTS[4]
    p1 = ease((T - T_PRI) / (T_SEG - T_PRI - .1)); p2 = ease((T - T_SEG) / (t1 - T_SEG - .05)) if T >= T_SEG else 0
    c = pared_cerca(T, rasgado=1, safe=False, pintura=p1, capa2=p2, cinta=1)
    x = lerp(60, W - 220, p2 if T >= T_SEG else p1); y = 900 + 380 * math.sin(T * 6)
    rodillo(c, x, y - 40); M.poner(c, "puno", x + 4, y + 470, "d", 1.0, 0, 1.0)
    d = ImageDraw.Draw(c)
    lbl = "2ª MANO" if T >= T_SEG else "1ª MANO"; d.rounded_rectangle((W / 2 - 150, 430, W / 2 + 150, 510), 20, fill=(255, 206, 60)); d.text((W / 2, 470), lbl, font=font(F_ANTON, 56), fill=OL, anchor="mm")
    flash(c, T, t0, .1); flash(c, T, T_SEG, .08)
    return c

def sc_revela(T):
    t0, t1 = CUTS[4], CUTS[5]; u = inout((T - t0) / (t1 - t0))
    c = cam(SL.salon("noche", "parquet_brillo", False), lerp(1.7, 1.5, u), 1296, 2080)
    destellos(c, T, t0 + .05, [(260, 700), (820, 720), (540, 980), (300, 1000), (760, 1060)], 1.6, 1.3)
    flash(c, T, t0, .14, (255, 250, 230), 160)
    return c

def sc_antesdespues(T):
    t0 = CUTS[5]
    a = cam(SL.salon("vieja", "parquet_brillo", False), 1.5, 1296, 2100); b = cam(SL.salon("noche", "parquet_brillo", False), 1.5, 1296, 2100)
    c = Image.new("RGBA", (W, H)); c.paste(a.crop((W // 4, 0, W // 4 + W // 2, H)), (0, 0)); c.paste(b.crop((W // 4, 0, W // 4 + W // 2, H)), (W // 2, 0))
    d = ImageDraw.Draw(c); d.rectangle((W // 2 - 4, 0, W // 2 + 4, H), fill=(255, 255, 255))
    for x, t, col in ((W / 4, "ANTES", (230, 80, 70)), (3 * W / 4, "DESPUÉS", (90, 200, 110))):
        d.rounded_rectangle((x - 150, 420, x + 150, 500), 20, fill=col); d.text((x, 460), t, font=font(F_ANTON, 58), fill=WHITE, anchor="mm")
    k = min(1, back((T - t0 - .1) / .3)); text(d, (W / 2, 760), "GASTADO", 70 * k, WHITE, stroke=8); text(d, (W / 2, 880), "- $115", 170 * k, RED, stroke=12)
    flash(c, T, t0, .1)
    return c

RAYO = [(560, 0), (520, 520), (580, 560), (490, 1100), (560, 1140), (470, H)]
def sc_elige(T):
    t0 = CUTS[6]
    hiA = 1.0 if T_CERR - .2 <= T < T_TAL - .3 else (.35 if T_TAL - .3 <= T < T_TU else 1.0)
    hiB = 1.0 if T_TAL - .3 <= T < T_TU else (.35 if T_CERR - .2 <= T < T_TAL - .3 else 1.0)
    base = pared_cerca(T, rasgado=1)
    L = base.copy(); R = base.copy()
    # A: cerrajero (móvil con la llamada)
    d = ImageDraw.Draw(L)
    d.rounded_rectangle((140, 1180, 470, 1700), 40, fill=(30, 30, 36)); d.rounded_rectangle((160, 1210, 450, 1670), 26, fill=(40, 60, 90))
    d.ellipse((240, 1280, 370, 1410), fill=(255, 206, 60)); d.text((305, 1345), "🔑".replace("🔑", "K"), font=font(F_ANTON, 70), fill=OL, anchor="mm")
    d.text((305, 1470), "CERRAJERO", font=font(F_ANTON, 40), fill=WHITE, anchor="mm"); d.ellipse((265, 1540, 345, 1620), fill=(80, 190, 90))
    # B: taladro con chispas
    d = ImageDraw.Draw(R); tx, ty = 760, 1000
    d.rounded_rectangle((tx, ty - 60, tx + 260, ty + 60), 30, fill=(240, 180, 40)); d.rectangle((tx - 120, ty - 12, tx, ty + 12), fill=(170, 170, 176))
    d.rounded_rectangle((tx + 120, ty + 40, tx + 200, ty + 260), 24, fill=(40, 40, 46))
    if int(T * 20) % 2 == 0:
        for a in range(-60, 61, 20): r = math.radians(a + 180); d.line((tx - 120, ty, tx - 120 + 90 * math.cos(r), ty + 90 * math.sin(r)), fill=(255, 220, 120), width=6)
    c = R.copy(); mL = Image.new("L", (W, H), 0); ImageDraw.Draw(mL).polygon([(0, 0)] + RAYO + [(0, H)], fill=255); c.paste(L, (0, 0), mL)
    for poly, h in (([(0, 0)] + RAYO + [(0, H)], hiA), ([(W, 0)] + RAYO + [(W, H)], hiB)):
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).polygon(poly, fill=(0, 0, 0, int(170 * (1 - h)))); c.alpha_composite(lay)
    c.alpha_composite(soft((W, H), lambda dd: dd.line(RAYO, fill=(255, 190, 90, 255), width=30), 16)); d = ImageDraw.Draw(c); d.line(RAYO, fill=(255, 245, 220), width=9)
    for cx, t1, t2, col, h, tin in ((270, "CERRAJERO", "- $200", (255, 206, 60), hiA, T_CERR - .2), (810, "TALADRO", "LO ABRO YO", (120, 220, 255), hiB, T_TAL - .3)):
        if T < tin: continue
        k = min(1, back((T - tin) / .3)) * (1 + .08 * h)
        text(d, (cx, 440), t1, 84 * k, col if h > .5 else (190, 190, 200), stroke=10); text(d, (cx, 540), t2, 64 * k, WHITE if h > .5 else (170, 170, 180), stroke=8)
    flash(c, T, t0, .14)
    return c

ESC = [sc_gancho, sc_gano, sc_precios, sc_pintar, sc_revela, sc_antesdespues, sc_elige]
def escena(T):
    for i in range(len(ESC)):
        if CUTS[i] <= T < CUTS[i + 1]: return i
    return len(ESC) - 1

def frame(T):
    i = escena(T); c = mirada(ESC[i](T), T, .5 if i in (5, 6) else 1.0)
    hud(c, T)
    if T < CUTS[6] - .05: c.alpha_composite(banda())
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
    SFX = [(s("papel"), 0.0, 2), (s("boom"), T_CAJA - .02, 1), (s("caja_fuerte"), T_CAJA + .1, 0), (s("whoosh"), CUTS[1] - .2, -3),
           (s("caja"), T_90 - .05, -1), (s("cinta"), T_ROD, -2), (s("caja"), T_25 - .05, -1),
           (s("rodillo"), T_PRI, 1), (s("rodillo"), T_PRI + .8, 1), (s("rodillo"), T_SEG, 1), (s("rodillo"), T_SEG + .8, 1),
           (s("brillo"), CUTS[4], 2), (s("whoosh"), CUTS[6] - .25, -2), (s("taladro"), T_TAL, -3)]
    ins = ["-i", VOZ]; flt = [f"[0:a]aresample=48000,apad=pad_dur=4,acompressor=threshold=-18dB:ratio=3:attack=5:release=120,loudnorm=I=-15:TP=-1.5:LRA=9,atrim=0:{TOTAL:.2f}[v]"]
    for k, (p, t, db) in enumerate(SFX):
        ins += ["-i", p]; ms = int(max(0, t) * 1000); flt.append(f"[{k + 1}:a]aresample=48000,loudnorm=I=-26:TP=-6,volume={db}dB,adelay={ms}|{ms},apad[s{k}]")
    flt.append("[v]" + "".join(f"[s{k}]" for k in range(len(SFX))) + f"amix=inputs={len(SFX) + 1}:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.95[m]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(flt), "-map", "[m]", "-ac", "2", wav], check=True)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        os.makedirs("/tmp/s2_chk", exist_ok=True)
        for i in range(len(ESC)):
            for q in (.3, .85):
                t = lerp(CUTS[i], CUTS[i + 1], q); frame(t).resize((270, 480)).save(f"/tmp/s2_chk/{i}_{q}.jpg")
        print("TOTAL", round(TOTAL, 2), [round(x, 2) for x in CUTS]); sys.exit()
    with Pool(3) as p: list(p.imap_unordered(render, range(len(ESC))))
    lst = os.path.join(TMP, "list.txt"); open(lst, "w").write("".join(f"file 'e{i}.mp4'\n" for i in range(len(ESC))))
    hq = os.path.join(TMP, "hq.mp4"); subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", hq], check=True)
    wav = os.path.join(TMP, "mezcla.wav"); mezcla(wav)
    out = os.path.join(OUT, "la_casa_de_1_dolar_parte2_salon.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", hq, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-maxrate", "5000k", "-bufsize", "10000k",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], check=True)
    print("ok", out, round(TOTAL, 2))
