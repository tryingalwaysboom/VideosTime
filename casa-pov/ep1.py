"""La casa de 1 dólar — Parte 1 (~40 s, 1080x1920, 30 fps).
python3 ep1.py frames  -> fotogramas de control en /tmp/casa_chk
python3 ep1.py         -> render completo + mezcla -> out/la_casa_de_1_dolar_parte1.mp4"""
import json, math, os, subprocess, sys, unicodedata
from functools import lru_cache
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import art as A
from art import W, H, PW, PH, font, F_ANTON, F_UI, F_REG, soft, lerp

HERE = os.path.dirname(os.path.abspath(__file__)); FPS = 30
VOZ = os.path.join(HERE, "voz1"); SRC = os.path.join(HERE, "..", "descargas", "casa_ep1"); SFXD = os.path.join(HERE, "..", "descargas", "casa_sfx")
TMP = os.path.join(HERE, "tmp1"); OUT = os.path.join(HERE, "out"); os.makedirs(TMP, exist_ok=True); os.makedirs(OUT, exist_ok=True)
YEL = (255, 206, 60); RED = (240, 60, 60); WHITE = (255, 255, 255); OL = (14, 12, 24); CYAN = (120, 220, 255); GRIS = (150, 156, 175)

LINEAS = [
    ("C01", "N", "Pagué un dólar por esta casa. Nadie me dijo por qué estaba tan barata."),
    ("C02", "N", "El contrato tenía trampa: 12 meses para reformarla, o la pierdo. Y pierdo $5,000 de fianza. Me quedan $2,140."),
    ("C03", "N", "Abrí la puerta. Polvo… muebles tapados con sábanas… y un calendario parado en 1987."),
    ("C04", "R", "Nadie ha durado ni una noche ahí dentro, mijo."),
    ("C05", "N", "Esa noche, a las 3 en punto… algo golpeó debajo del suelo."),
    ("C06", "N", "Había una trampilla. Con un candado nuevo. Y esta casa lleva 37 años vacía."),
    ("C07", "N", "¿Abro la trampilla esta noche… o la tapio y empiezo la reforma? Tú decides."),
]
GAP = {"C02": .2, "C03": .32, "C04": .25, "C05": .3, "C06": .22, "C07": .3}

def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)

OFFS = json.load(open(os.path.join(VOZ, "offsets.json")))
TL = {}; _t = 0.0
for lid, who, cap in LINEAS:
    _t += GAP.get(lid, 0); d_ = dur(os.path.join(VOZ, lid + ".wav")); TL[lid] = (_t, _t + d_); _t += d_
TOTAL = _t + .3
def S(l): return TL[l][0]
def E(l): return TL[l][1]

@lru_cache(None)
def words(lid):
    raw = json.load(open(os.path.join(SRC, lid + ".json")))
    m = []
    for w in raw:
        if m and w["p"][:1] in ",." and w["p"][1:2].isdigit(): m[-1] = dict(p=m[-1]["p"] + w["p"], inicio=m[-1]["inicio"], fin=w["fin"])
        else: m.append(dict(w))
    cap = [x for x in LINEAS if x[0] == lid][0][2].split()
    assert len(cap) == len(m), (lid, len(cap), len(m), [w["p"] for w in m])
    o = OFFS[lid]; t0 = S(lid)
    res = []
    for c, w in zip(cap, m):
        a = t0 + max(0, (w["inicio"] - o["off"]) / o["tempo"]); b = t0 + max(0, (w["fin"] - o["off"]) / o["tempo"])
        res.append((c, min(a, E(lid)), min(max(b, a + .08), E(lid) + .1)))
    return res
def WT(lid, i): return words(lid)[i][1]

# ------------------------------------------------------------------ utilidades
def ease(u): u = max(0., min(1., u)); return 1 - (1 - u) ** 3
def inout(u): u = max(0., min(1., u)); return u * u * (3 - 2 * u)
def back(u):
    u = max(0., min(1., u)); c = 1.7; return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2
def clamp(u): return max(0., min(1., u))

def cam(plate, z, cx, cy, rot=0.0, sx=0.0, sy=0.0):
    """Encuadre de la plancha: z=1 enseña toda la plancha; z>1 acerca. cx, cy en coordenadas de la plancha."""
    pw, ph = plate.size; cw, ch = pw / z, ph / z
    cx = min(max(cx, cw / 2), pw - cw / 2); cy = min(max(cy, ch / 2), ph - ch / 2)
    box = (cx - cw / 2 + sx, cy - ch / 2 + sy, cx + cw / 2 + sx, cy + ch / 2 + sy)
    if rot: return plate.transform((W, H), Image.AFFINE, _aff(box, rot), resample=Image.BILINEAR)
    return plate.resize((W, H), Image.BILINEAR, box=box)

def _aff(box, rot):
    x0, y0, x1, y1 = box; sx, sy = (x1 - x0) / W, (y1 - y0) / H; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    r = math.radians(rot); c, s = math.cos(r), math.sin(r)
    return (c * sx, -s * sy, cx - c * sx * W / 2 + s * sy * H / 2, s * sx, c * sy, cy - s * sx * W / 2 - c * sy * H / 2)

def to_frame(px, py, z, cx, cy, plate=(PW, PH)):
    pw, ph = plate; cw, ch = pw / z, ph / z
    cx = min(max(cx, cw / 2), pw - cw / 2); cy = min(max(cy, ch / 2), ph - ch / 2)
    return ((px - (cx - cw / 2)) / cw * W, (py - (cy - ch / 2)) / ch * H)

VIG = A.vignette(W, H, 210)
@lru_cache(None)
def grain(i):
    rng = np.random.default_rng(i); n = rng.normal(0, 7, (H // 2, W // 2)).astype(np.int16)
    return np.kron(n, np.ones((2, 2), np.int16))

def finish(c, T):
    c.alpha_composite(VIG)
    a = np.asarray(c.convert("RGB"), np.int16) + grain(int(T * FPS) % 6)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").convert("RGBA")

def dark(c, a): c.alpha_composite(Image.new("RGBA", (W, H), (4, 4, 12, int(a))))
def flash(c, T, t0, d=.18, col=(255, 255, 255), amax=200):
    if 0 <= T - t0 < d: c.alpha_composite(Image.new("RGBA", (W, H), col + (int(amax * (1 - (T - t0) / d)),)))

def polvo(c, T, n=70, seed=1, col=(255, 240, 210), amax=150):
    d = ImageDraw.Draw(c); rng = np.random.default_rng(seed)
    xs, ys, sp, ph, sz = rng.uniform(0, W, n), rng.uniform(0, H, n), rng.uniform(8, 30, n), rng.uniform(0, 6.28, n), rng.uniform(2, 6, n)
    for x, y, s, p, r in zip(xs, ys, sp, ph, sz):
        px = (x + 26 * math.sin(T * .6 + p)) % W; py = (y - s * T + 14 * math.cos(T * .8 + p)) % H
        a = int(amax * (.5 + .5 * math.sin(T * 1.7 + p)))
        d.ellipse((px - r, py - r, px + r, py + r), fill=col + (a,))

@lru_cache(None)
def _lint_mask(r, amb):
    m = Image.new("L", (W * 2, H * 2), amb); ImageDraw.Draw(m).ellipse((W - r, H - r, W + r, H + r), fill=0)
    m = m.filter(ImageFilter.GaussianBlur(r * .35))
    sh = Image.new("RGBA", (W * 2, H * 2), (2, 2, 8, 255)); sh.putalpha(m)
    gl = soft((W * 2, H * 2), lambda dd: dd.ellipse((W - r * .8, H - r * .8, W + r * .8, H + r * .8), fill=(255, 236, 190, 46)), r * .3)
    sh.alpha_composite(gl); return sh
def linterna(c, cx, cy, r=360, amb=225):
    m = _lint_mask(r, amb); c.alpha_composite(m.crop((int(W - cx), int(H - cy), int(W - cx) + W, int(H - cy) + H)))

def paste_c(c, im, cx, cy, s=1.0, alpha=1.0, rot=0):
    if s != 1: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
    if rot: im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1: im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * alpha)))
    c.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def text(d, xy, s, size, fill=WHITE, anchor="mm", f=F_ANTON, stroke=8, sfill=OL):
    d.text(xy, s, font=font(f, size), fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sfill)

# ------------------------------------------------------------------ subtítulos palabra a palabra
def chunks():
    out = []
    for lid, who, cap in LINEAS:
        g = []
        for (w, a, b) in words(lid):
            g.append((w, a, b))
            if len(g) == 3 or w[-1] in ".,:?…" or (len(g) == 2 and len("".join(x[0] for x in g)) > 13):
                out.append((g, who, lid)); g = []
        if g: out.append((g, who, lid))
    return out
CH = None
TAG = {"R": "DOÑA REMEDIOS · LA VECINA"}

def caption(c, T):
    global CH
    if CH is None: CH = chunks()
    if T >= S("C07") - .05: return
    for i, (g, who, lid) in enumerate(CH):
        t0, t1 = g[0][1], g[-1][2]; nxt = CH[i + 1][0][0][1] if i + 1 < len(CH) else 1e9
        if not (t0 - .05 <= T < min(t1 + .4, nxt - .05)): continue
        d = ImageDraw.Draw(c); k = .86 + .14 * back((T - t0 + .05) / .14)
        f = font(F_ANTON, 94 * k); ws = [d.textlength(w + " ", font=f) for w, _, _ in g]; tot = sum(ws) - d.textlength(" ", font=f)
        if tot > 860:
            f = font(F_ANTON, 94 * k * 860 / tot); ws = [d.textlength(w + " ", font=f) for w, _, _ in g]; tot = sum(ws) - d.textlength(" ", font=f)
        x = W / 2 - tot / 2; y = 1490
        for j, ((w, a, b), wd) in enumerate(zip(g, ws)):
            fin = g[j + 1][1] if j + 1 < len(g) else b + .4
            act = a - .03 <= T < fin - .03; dicha = T >= a - .03
            col = YEL if act else (WHITE if dicha else (215, 215, 222))
            if act:
                u = clamp((T - a + .03) / .12); fa = font(F_ANTON, f.size * (1 + .07 * math.sin(u * math.pi)))
                d.text((x + (wd - d.textlength(" ", font=f)) / 2, y), w, font=fa, fill=col, anchor="mm", stroke_width=11, stroke_fill=OL)
            else:
                d.text((x, y), w, font=f, fill=col, anchor="lm", stroke_width=10, stroke_fill=OL)
            x += wd
        if who in TAG:
            ft = font(F_UI, 30); tw = d.textlength(TAG[who], font=ft)
            d.rounded_rectangle((W / 2 - tw / 2 - 20, 1388, W / 2 + tw / 2 + 20, 1436), 12, fill=(255, 170, 70))
            d.text((W / 2, 1412), TAG[who], font=ft, fill=OL, anchor="mm")
        return

# ------------------------------------------------------------------ barra superior
def ic_coin(d, x, y):
    d.ellipse((x - 17, y - 17, x + 17, y + 17), fill=(120, 200, 110), outline=(40, 90, 40), width=3); d.text((x, y + 1), "$", font=font(F_ANTON, 26), fill=(30, 70, 30), anchor="mm")
def ic_casa(d, x, y, col):
    d.polygon([(x - 18, y - 2), (x, y - 20), (x + 18, y - 2)], fill=col); d.rectangle((x - 13, y - 3, x + 13, y + 16), fill=col); d.rectangle((x - 4, y + 5, x + 4, y + 16), fill=(12, 10, 26))
def ic_cal(d, x, y, col):
    d.rounded_rectangle((x - 17, y - 15, x + 17, y + 17), 4, fill=col); d.rectangle((x - 17, y - 15, x + 17, y - 5), fill=RED)
    for k in (-8, 8): d.line((x + k, y - 20, x + k, y - 11), fill=WHITE, width=4)

@lru_cache(1)
def hud_base():
    im = Image.new("RGBA", (W, 320), (0, 0, 0, 0)); x0, y0, x1, y1 = 36, 168, 1044, 278
    im.alpha_composite(soft((W, 320), lambda dd: dd.rounded_rectangle((x0, y0 + 8, x1, y1 + 10), 26, fill=(0, 0, 0, 130)), 10))
    im.alpha_composite(soft((W, 320), lambda dd: dd.rounded_rectangle((x0, y0, x1, y1), 26, outline=(255, 170, 70, 140), width=6), 6))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0, y0, x1, y1), 26, fill=(12, 10, 26, 210), outline=(255, 170, 70, 120), width=2)
    d.rounded_rectangle((x0 + 14, y0 + 12, x0 + 160, y0 + 56), 12, fill=(255, 170, 70))
    d.text((x0 + 87, y0 + 34), "PARTE 1", font=font(F_ANTON, 32), fill=OL, anchor="mm")
    d.line((x0 + 16, y0 + 64, x1 - 16, y0 + 64), fill=(255, 255, 255, 30), width=2)
    d.text((x0 + 18, y0 + 87), "OBJETIVO", font=font(F_UI, 20), fill=(255, 170, 70), anchor="lm")
    return im

def hud(c, T):
    if T >= S("C07") - .1: return
    base = hud_base()
    if T < .3: c.alpha_composite(base, (0, int(-320 * (1 - ease(T / .3))))); return
    c.alpha_composite(base); d = ImageDraw.Draw(c); x0, y0 = 36, 168
    t_caja, t_mes, t_ref = WT("C02", 16), WT("C02", 4), WT("C02", 7)
    def pop(t): return 1 + .3 * math.sin(clamp((T - t) / .3) * math.pi) if 0 <= T - t < .3 else 1
    if T < t_caja: caja = "?"
    else:
        u = ease((T - t_caja) / 1.0); caja = f"${int(lerp(7140, 2140, u)):,}"
    ic_coin(d, x0 + 230, y0 + 34)
    d.text((x0 + 256, y0 + 35), caja, font=font(F_ANTON, 36 * pop(t_caja)), fill=GRIS if caja == "?" else ((255, 120, 110) if T < t_caja + 1.0 else WHITE), anchor="lm")
    on = T >= t_ref
    ic_casa(d, x0 + 470, y0 + 34, (255, 170, 70) if on else (70, 70, 96))
    d.text((x0 + 498, y0 + 35), "REFORMA 0%" if on else "?", font=font(F_ANTON, 34 * pop(t_ref)), fill=WHITE if on else GRIS, anchor="lm")
    on2 = T >= t_mes
    ic_cal(d, x0 + 770, y0 + 34, WHITE if on2 else (70, 70, 96))
    d.text((x0 + 798, y0 + 35), "12 MESES" if on2 else "?", font=font(F_ANTON, 34 * pop(t_mes)), fill=WHITE if on2 else GRIS, anchor="lm")
    d.text((x0 + 132, y0 + 87), "Reformar la casa" if on else "Entrar en la casa", font=font(F_UI, 24), fill=WHITE, anchor="lm")
    d.text((1044 - 20, y0 + 87), "SE PIERDE EN 12 MESES" if on2 else "", font=font(F_UI, 18), fill=GRIS, anchor="rm")

# ------------------------------------------------------------------ escenas
BILL = A.billete(1.0, -9)
SELLO1 = A.sello("VENDIDA", "POR $1", rot=-12, s=.9)
SELLO2 = A.sello("37 AÑOS", "VACÍA", rot=-8, s=1.35)
SELLO3 = A.sello("TRAMPA", rot=8, s=.8)

def sc_hook(T):   # el billete cae sobre el contrato + sello VENDIDA
    t0 = 0.0; z = lerp(1.9, 1.7, ease(T / 1.4)); cx, cy = 640, 640
    c = cam(A.plate_contrato(), z, cx, cy, rot=lerp(-3, -1, ease(T / 1.4)))
    u = ease((T - t0) / .16); bx, by = lerp(W / 2 - 900, W / 2 - 60, u), lerp(1300, 1080, u)
    paste_c(c, BILL, bx, by, s=1.05 + .4 * (1 - u))
    ts = WT("C01", 2) - .05
    if T >= ts:
        k = back((T - ts) / .22); paste_c(c, SELLO1, W / 2 + 140, 760, s=lerp(2.2, 1.0, min(1, (T - ts) / .16)) * (k if k < 1 else 1), alpha=min(1, (T - ts) / .08))
    flash(c, T, ts, .12, (255, 240, 220), 120)
    return c

def sc_casa(T):
    t0 = WT("C01", 4) - .08; t1 = S("C02"); u = inout((T - t0) / (t1 - t0))
    z = lerp(1.0, 1.22, u); cx, cy = lerp(648, 600, u), lerp(1300, 1250, u)
    c = cam(A.plate_casa(), z, cx, cy)
    ax, ay = A.attic_xy(); fx, fy = to_frame(ax, ay, z, cx, cy)
    ta = WT("C01", 9)   # luz en el desván cuando dice "por qué"
    if T >= ta:
        fl = (.6 + .4 * math.sin((T - ta) * 31)) * clamp((T - ta) / .2)
        r = 52 * W / (PW / z)
        g = soft((W, H), lambda dd: dd.ellipse((fx - r * 3, fy - r * 3, fx + r * 3, fy + r * 3), fill=(255, 190, 90, int(90 * fl))), 30); c.alpha_composite(g)
        d = ImageDraw.Draw(c); d.ellipse((fx - r * .85, fy - r * .85, fx + r * .85, fy + r * .85), fill=(255, 200, 110, int(255 * fl)))
        d.line((fx - r * .9, fy, fx + r * .9, fy), fill=(30, 30, 42), width=max(3, int(r * .12))); d.line((fx, fy - r * .9, fx, fy + r * .9), fill=(30, 30, 42), width=max(3, int(r * .12)))
        d.ellipse((fx - r * .25, fy - r * .55, fx + r * .25, fy + r * .05), fill=(20, 14, 18, int(230 * fl)))   # silueta
    flash(c, T, t0, .14)
    return c

def hl(c, d, u0, v0, u1, v1, z, cx, cy, p, col=(255, 230, 60, 120)):
    if p <= 0: return
    a = to_frame(*A.paper_xy(u0, v0), z, cx, cy); b = to_frame(*A.paper_xy(lerp(u0, u1, p), v1), z, cx, cy)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).rectangle((min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])), fill=col); c.alpha_composite(lay)

def sc_contrato(T):
    t0, t1 = S("C02"), WT("C02", 16) - .05; tcut = WT("C02", 8) - .04
    t12, tp, tf = WT("C02", 4), WT("C02", 9), WT("C02", 12)
    if T < tcut:   # plano 1: el contrato entero, sello TRAMPA y los 12 meses
        u = inout((T - t0) / (tcut - t0)); z = lerp(1.3, 1.5, u); cx, cy = 640, lerp(1000, 1150, u); rot = lerp(2, 0, u)
    else:          # plano 2: muy cerca de la cláusula que te quita la casa
        u = inout((T - tcut) / (t1 - tcut)); z = lerp(2.15, 2.35, u); cx, cy = lerp(560, 600, u), lerp(1340, 1380, u); rot = lerp(-3, -1.5, u)
    c = cam(A.plate_contrato(), z, cx, cy, rot=rot); d = ImageDraw.Draw(c)
    hl(c, d, .09, .54, .82, .575, z, cx, cy, ease((T - t12) / .35))
    hl(c, d, .09, .6, .9, .632, z, cx, cy, ease((T - tp) / .35), (255, 80, 60, 110))
    hl(c, d, .09, .635, .7, .667, z, cx, cy, ease((T - tf) / .35), (255, 80, 60, 110))
    ts = WT("C02", 3)
    if ts <= T < tcut: paste_c(c, SELLO3, W / 2 + 230, 560, s=lerp(1.8, 1.0, min(1, (T - ts) / .15)), alpha=min(1, (T - ts) / .08))
    if T >= tf:
        k = back((T - tf) / .25); d = ImageDraw.Draw(c)
        text(d, (W / 2, 1150), "- $5,000", 170 * min(1, k), RED, stroke=11)
    flash(c, T, t0, .12); flash(c, T, tcut, .1, (255, 255, 255), 150)
    return c

def sc_dinero(T):
    t0 = WT("C02", 16) - .05
    c = cam(A.plate_contrato(), 1.3, 650, 1150).filter(ImageFilter.GaussianBlur(14)); dark(c, 150)
    d = ImageDraw.Draw(c); u = ease((T - t0 - .15) / 1.0); v = int(lerp(7140, 2140, u))
    for i in range(10):   # billetes que se van volando
        tt = T - t0 - .15 - i * .08
        if 0 <= tt < .9:
            paste_c(c, BILL, W / 2 + (i - 5) * 60 + 500 * tt * (1 if i % 2 else -1), 760 - 900 * tt + 300 * tt * tt * 0, s=.35, alpha=1 - tt / .9, rot=int(tt * 300 * (1 if i % 2 else -1)))
    k = max(.02, back((T - t0) / .3))
    pw, ph = 760 * min(1, k), 470 * min(1, k)
    c.alpha_composite(soft((W, H), lambda dd: dd.rounded_rectangle((W / 2 - pw / 2, 760 - ph / 2, W / 2 + pw / 2, 760 + ph / 2), 40, fill=(0, 0, 0, 160)), 20))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((W / 2 - pw / 2, 760 - ph / 2, W / 2 + pw / 2, 760 + ph / 2), 40, fill=(18, 14, 28, 235), outline=(255, 170, 70), width=5)
    if k > .6:
        text(d, (W / 2, 620), "ME QUEDAN", 64, (255, 170, 70), stroke=0)
        col = RED if u < 1 else (120, 230, 120)
        sh = 6 * math.sin(T * 60) * (1 - u)
        text(d, (W / 2 + sh, 790), f"${v:,}", 210, col, stroke=10)
        d.rounded_rectangle((W / 2 - 300, 900, W / 2 + 300, 930), 15, fill=(40, 36, 60)); d.rounded_rectangle((W / 2 - 300, 900, W / 2 - 300 + 600 * (v / 7140), 930), 15, fill=col)
    return c

DOORLEAF = A.door_leaf(A.DOOR[2] - A.DOOR[0], A.DOOR[3] - A.DOOR[1])
def sc_puerta(T):
    t0 = S("C03") - GAP["C03"]; t1 = WT("C03", 3) - .04
    u = inout((T - t0) / (t1 - t0)); z = lerp(1.05, 1.5, u); cx, cy = 648, lerp(1300, 1260, u)
    pl = A.plate_porche().copy()
    x0, y0, x1, y1 = A.DOOR; ang = ease((T - t0) / 1.1) * 78
    inside = cam(A.plate_pasillo(), 1.0, 648, 1152).resize((x1 - x0, y1 - y0)); inside.alpha_composite(Image.new("RGBA", inside.size, (0, 0, 0, 120)))
    pl.alpha_composite(inside, (x0, y0))
    wv = (x1 - x0) * math.cos(math.radians(ang)); sh = 60 * math.sin(math.radians(ang))
    if wv > 4:
        leaf = DOORLEAF.transform(DOORLEAF.size, Image.QUAD, (0, 0, 0, DOORLEAF.height, DOORLEAF.width, DOORLEAF.height - 0, DOORLEAF.width, 0), Image.BILINEAR)
        leaf = leaf.resize((int(wv), y1 - y0)); pl.alpha_composite(leaf, (x0, y0))
        lay = Image.new("RGBA", pl.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).polygon([(x0 + wv, y0), (x0 + wv + 18, y0 - sh * .3), (x0 + wv + 18, y1), (x0 + wv, y1)], fill=(30, 20, 14, 255)); pl.alpha_composite(lay)
    c = cam(pl, z, cx, cy)
    linterna(c, W / 2 + 60 * math.sin(T * 1.3), 1000, 520, 150)
    return c

def sc_pasillo(T):
    t0, t1 = WT("C03", 3) - .04, WT("C03", 10) - .05; u = inout((T - t0) / (t1 - t0))
    z = lerp(1.0, 1.35, u); cx, cy = lerp(620, 660, u), lerp(1180, 1120, u)
    c = cam(A.plate_pasillo(), z, cx, cy, rot=1.2 * math.sin(T * 1.1))
    ts = WT("C03", 7)
    if T >= ts and T - ts < 1.0:   # la sábana del sillón se mueve
        k = math.sin(clamp((T - ts) / 1.0) * math.pi)
        c.alpha_composite(soft((W, H), lambda dd: dd.ellipse((-80, 1100 - 80 * k, 420, 1500), fill=(220, 222, 235, int(60 * k))), 30))
    polvo(c, T, 90, 2)
    lx = W / 2 + 260 * math.sin(T * .9); ly = 1050 + 120 * math.sin(T * .6)
    linterna(c, lx, ly, 470, 175)
    return c

def sc_calendario(T):
    t0 = WT("C03", 10) - .05; t1 = S("C04") - .05; u = inout((T - t0) / max(.1, t1 - t0))
    z = lerp(1.15, 1.6, u); cx, cy = 648, lerp(1300, 1260, u)
    tb = WT("C03", 13)
    sx = sy = 0
    if 0 <= T - tb < .4: sx, sy = 14 * math.sin(T * 90) * (1 - (T - tb) / .4), 10 * math.cos(T * 70) * (1 - (T - tb) / .4)
    c = cam(A.plate_calendario(), z + (.08 * ease((T - tb) / .3) if T >= tb else 0), cx, cy, sx=sx, sy=sy)
    polvo(c, T, 50, 3, amax=110)
    linterna(c, W / 2 + 40 * math.sin(T * 2), 900, 560, 170)
    flash(c, T, tb, .16, (255, 220, 200), 150)
    return c

@lru_cache(1)
def rem_base():
    im = A.plate_remedios_bg().copy(); A.farol(im, 300, 1560, 0, 1.1); return im
@lru_cache(1)
def rem_valla():
    im = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); A.valla(im, 1640); return im
@lru_cache(1)
def rem_luz():
    return soft((PW, PH), lambda dd: dd.ellipse((-200, 900, 900, 2000), fill=(255, 160, 70, 70)), 140)
@lru_cache(None)
def env(lid):
    a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(VOZ, lid + ".wav"), "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True).stdout, np.int16).astype(float)
    hop = 8000 // FPS; e = np.array([np.sqrt((a[i:i + hop] ** 2).mean()) for i in range(0, len(a) - hop, hop)])
    return e / (np.percentile(e, 95) + 1e-6)

def sc_remedios(T):
    t0, t1 = S("C04") - .05, S("C05") - .02; u = inout((T - t0) / (t1 - t0))
    pl = rem_base().copy()
    e = env("C04"); i = int((T - S("C04")) * FPS)
    mouth = float(np.clip(e[i], 0, 1)) if 0 <= i < len(e) and T < E("C04") else 0.0
    bl = 1.0 if abs(T - (S("C04") + 1.25)) < .07 else 0.0
    A.remedios(pl, 700, 1180 + 6 * math.sin(T * 2), mouth=mouth, blink=bl, s=1.05)
    pl.alpha_composite(rem_luz()); pl.alpha_composite(rem_valla())
    z = lerp(1.12, 1.4, u); c = cam(pl, z, lerp(660, 690, u), lerp(1300, 1250, u))
    flash(c, T, t0, .12)
    return c

def sc_reloj(T):
    t0, t1 = S("C05") - .05, WT("C05", 8) - .04; u = inout((T - t0) / (t1 - t0))
    z = lerp(1.0, 1.25, u); c = cam(A.plate_reloj(), z, 648, lerp(1200, 1160, u))
    d = ImageDraw.Draw(c); t3 = WT("C05", 4)
    x0, y0 = to_frame(310, 960, z, 648, lerp(1200, 1160, u)); x1, y1 = to_frame(980, 1360, z, 648, lerp(1200, 1160, u))
    cxm, cym = (x0 + x1) / 2, (y0 + y1) / 2; hh = (y1 - y0)
    s = "3:00" if T >= t3 else "2:59"
    if T < t3 or int((T - t3) * 2) % 2 == 0 or T > t3 + 1.6: pass
    g = soft((W, H), lambda dd: dd.text((cxm, cym), s, font=font(F_ANTON, hh * .62), fill=(255, 40, 40, 200), anchor="mm"), 18); c.alpha_composite(g)
    d = ImageDraw.Draw(c); d.text((cxm, cym), s, font=font(F_ANTON, hh * .62), fill=(255, 70, 60), anchor="mm")
    flash(c, T, t0, .12)
    if T >= t3: flash(c, T, t3, .15, (255, 60, 60), 90)
    return c

KNOCKS = [.2, .65, 1.05]
def sc_golpes(T):
    t0, t1 = WT("C05", 8) - .04, S("C06") - .02
    shake = 0.0
    for k in KNOCKS:
        dt = T - (t0 + k)
        if 0 <= dt < .3: shake = max(shake, 1 - dt / .3)
    sx, sy = 26 * shake * math.sin(T * 95), 30 * shake * math.cos(T * 80)
    u = inout((T - t0) / (t1 - t0)); z = lerp(1.6, 1.75, u)
    c = cam(A.plate_trampilla(), z, 380, 1700, rot=4 * shake * math.sin(T * 50), sx=sx, sy=sy)
    d = ImageDraw.Draw(c)
    for j, k in enumerate(KNOCKS):   # el polvo salta de las juntas
        dt = T - (t0 + k)
        if 0 <= dt < .8:
            for i in range(26):
                x = 180 + (i * 37 + j * 90) % 760; vy = 240 + (i * 53) % 300
                y = 1250 - vy * dt + 420 * dt * dt
                r = 4 + i % 4; d.ellipse((x - r, y - r, x + r, y + r), fill=(200, 170, 130, int(220 * (1 - dt / .8))))
    dark(c, 60); linterna(c, W / 2, 1100, 420, 215)
    for k in KNOCKS: flash(c, T, t0 + k, .08, (255, 255, 255), 70)
    return c

def sc_trampilla(T):
    t0, t1 = S("C06") - .02, S("C07") - .1
    tt, tc, t37 = WT("C06", 2), WT("C06", 5), WT("C06", 11)
    hx, hy = A.quad_pt(A.TRAP, .82, .5)
    if T < tc - .05:
        u = inout((T - t0) / (tc - .05 - t0)); z = lerp(1.25, 1.35, u); cx, cy = 648, 1340
    else:
        u = ease((T - tc + .05) / .45); z = lerp(1.35, 2.1, u); cx, cy = lerp(648, hx + 40, u), lerp(1340, hy + 190, u)
    if T >= t37: z += .15 * ease((T - t37) / .3)
    pl = A.plate_trampilla().copy()
    br = clamp((T - tc) / .2) * (1 - clamp((T - tc - .7) / .5)) + (.6 + .4 * math.sin(T * 9)) * clamp((T - tc - 1.2) / .3)
    A.candado(pl, hx + 50, hy + 40, 1.0, max(0, br))
    c = cam(pl, z, cx, cy)
    lu = ease((T - t0) / .7)
    lx, ly = lerp(150, W / 2, lu), lerp(1500, 980, lu)
    linterna(c, lx, ly, lerp(300, 520, lu), 215)
    if T >= t37:
        k = back((T - t37) / .22); paste_c(c, SELLO2, W / 2, 1200, s=lerp(2.3, 1.0, min(1, (T - t37) / .16)), alpha=min(1, (T - t37) / .08))
        flash(c, T, t37, .15, (255, 230, 220), 160)
    flash(c, T, t0, .1)
    return c

RAYO = [(560, 0), (520, 520), (580, 560), (490, 1100), (560, 1140), (470, H)]
def sc_final(T):
    t0 = S("C07") - .1; ta, tb, tc = S("C07"), WT("C07", 5), WT("C07", 12)
    c = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    hiA = 1.0 if ta <= T < tb else (.35 if tb <= T < tc else (1.0 if T >= tc else .7))
    hiB = 1.0 if tb <= T < tc else (.35 if ta <= T < tb else (1.0 if T >= tc else .7))
    L = A.plate_op_abrir(); R = A.plate_op_tapiar()
    zl = 1.0 + .06 * clamp((T - t0) / 6); zr = 1.0 + .06 * clamp((T - t0) / 6)
    l = L.resize((int(W * zl), int(H * zl))).crop((int(W * (zl - 1) / 2) + 270, 0, int(W * (zl - 1) / 2) + 270 + W // 2 + 60, H))
    r = R.resize((int(W * zr), int(H * zr))).crop((int(W * (zr - 1) / 2) + 240, 0, int(W * (zr - 1) / 2) + 240 + W // 2 + 60, H))
    sl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sl.paste(l, (0, 0)); sr = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sr.paste(r, (W // 2 - 60, 0))
    mL = Image.new("L", (W, H), 0); ImageDraw.Draw(mL).polygon([(0, 0)] + RAYO + [(0, H)], fill=255)
    c.paste(sr, (0, 0)); c.paste(sl, (0, 0), mL)
    dl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(dl).polygon([(0, 0)] + RAYO + [(0, H)], fill=(0, 0, 0, int(170 * (1 - hiA))))
    dr = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(dr).polygon([(W, 0)] + RAYO + [(W, H)], fill=(0, 0, 0, int(170 * (1 - hiB))))
    c.alpha_composite(dl); c.alpha_composite(dr)
    c.alpha_composite(soft((W, H), lambda dd: dd.line(RAYO, fill=(255, 190, 90, 255), width=30), 16))
    d = ImageDraw.Draw(c); d.line(RAYO, fill=(255, 245, 220), width=9)
    def lab(cx, y, t1, t2, col, h, t_in):
        k = back((T - t_in) / .3) if T >= t_in else 0
        if k <= 0: return
        s = (1 + .08 * h) * min(1, k)
        text(d, (cx, y), t1, 92 * s, col if h > .5 else (190, 190, 200), stroke=10)
        text(d, (cx, y + 96 * s), t2, 56 * s, WHITE if h > .5 else (170, 170, 180), stroke=8)
    lab(275, 1420, "ABRIRLA", "esta noche", (255, 150, 70), hiA, ta)
    lab(800, 1420, "TAPIARLA", "y reformar", (120, 220, 255), hiB, tb - .05)
    flash(c, T, t0, .14)
    return c

ESCENAS = [
    ("s01", 0.0, lambda: WT("C01", 4) - .08, sc_hook),
    ("s02", lambda: WT("C01", 4) - .08, lambda: S("C02"), sc_casa),
    ("s03", lambda: S("C02"), lambda: WT("C02", 16) - .05, sc_contrato),
    ("s04", lambda: WT("C02", 16) - .05, lambda: S("C03") - GAP["C03"], sc_dinero),
    ("s05", lambda: S("C03") - GAP["C03"], lambda: WT("C03", 3) - .04, sc_puerta),
    ("s06", lambda: WT("C03", 3) - .04, lambda: WT("C03", 10) - .05, sc_pasillo),
    ("s07", lambda: WT("C03", 10) - .05, lambda: S("C04") - .05, sc_calendario),
    ("s08", lambda: S("C04") - .05, lambda: S("C05") - .05, sc_remedios),
    ("s09", lambda: S("C05") - .05, lambda: WT("C05", 8) - .04, sc_reloj),
    ("s10", lambda: WT("C05", 8) - .04, lambda: S("C06") - .02, sc_golpes),
    ("s11", lambda: S("C06") - .02, lambda: S("C07") - .1, sc_trampilla),
    ("s12", lambda: S("C07") - .1, lambda: TOTAL, sc_final),
]
def _v(x): return x() if callable(x) else x
def cortes():
    out = []
    for name, a, b, fn in ESCENAS:
        fa, fb = round(_v(a) * FPS), round(_v(b) * FPS); out.append((name, fa, fb, fn))
    return out

@lru_cache(1)
def banda():
    a = np.zeros((H, W, 4), np.uint8); y = np.arange(H)
    a[..., 3] = (np.clip(1 - np.abs(y - 1490) / 190, 0, 1) ** 1.2 * 120).astype(np.uint8)[:, None]
    return Image.fromarray(a, "RGBA")

def frame(T, fn):
    c = fn(T); hud(c, T)
    if T < S("C07") - .05: c.alpha_composite(banda())
    caption(c, T); return finish(c, T).convert("RGB")

def render_escena(args):
    name, fa, fb, _ = args; fn = dict((n, f) for n, *_x, f in ESCENAS)[name]
    out = os.path.join(TMP, name + ".mp4"); part = os.path.join(TMP, name + ".part.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", part], stdin=subprocess.PIPE)
    for f in range(fa, fb): p.stdin.write(frame(f / FPS, fn).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(part, out)
    return name

# ------------------------------------------------------------------ audio
SR = 48000
def synth_amb(path):
    n = int(TOTAL * SR); t = np.arange(n) / SR; rng = np.random.default_rng(4)
    w = rng.normal(0, 1, n)
    k = np.ones(400) / 400; wind = np.convolve(w, k, "same") * (0.6 + 0.4 * np.sin(2 * np.pi * .13 * t + 1) * np.sin(2 * np.pi * .07 * t))
    drone = .5 * np.sin(2 * np.pi * 49 * t) + .3 * np.sin(2 * np.pi * 73.5 * t + .5) + .15 * np.sin(2 * np.pi * 98.2 * t)
    drone *= .6 + .4 * np.sin(2 * np.pi * .25 * t)
    hb = np.zeros(n)   # latido suave durante la trampilla
    for tb in np.arange(S("C06"), S("C07"), .72):
        for off, a in ((0, 1), (.18, .6)):
            i = int((tb + off) * SR); L = int(.12 * SR)
            if i + L < n: hb[i:i + L] += a * np.sin(2 * np.pi * 52 * np.arange(L) / SR) * np.exp(-np.arange(L) / (.035 * SR))
    x = .5 * wind / (np.abs(wind).max() + 1e-9) + .35 * drone + .9 * hb
    write_wav(path, x)

def synth_reloj(path):
    n = int(2.6 * SR); x = np.zeros(n)
    for k in range(5):   # tic-tac
        i = int(k * .5 * SR); L = int(.02 * SR); x[i:i + L] += .5 * np.random.default_rng(k).normal(0, 1, L) * np.exp(-np.arange(L) / (.004 * SR))
    i = int(1.0 * SR); L = int(1.6 * SR); tt = np.arange(L) / SR   # campanada
    bell = sum(a * np.sin(2 * np.pi * f * tt) for f, a in ((392, 1), (784, .5), (1176, .25), (523, .3))) * np.exp(-tt / .5)
    x[i:i + L] += .8 * bell[: n - i]
    write_wav(path, x)

def write_wav(path, x):
    x = (x / (np.abs(x).max() + 1e-9) * .8 * 32767).astype(np.int16)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", path], input=x.tobytes(), check=True)

def mezcla(out_wav):
    amb = os.path.join(TMP, "amb.wav"); synth_amb(amb); rel = os.path.join(TMP, "reloj.wav"); synth_reloj(rel)
    sfx = lambda n: os.path.join(SFXD, n + ".mp3")
    SFX = [
        (sfx("sello"), 0.0, 2), (sfx("sello"), WT("C01", 2) - .15, 4), (sfx("whoosh"), WT("C01", 4) - .2, -2),
        (sfx("whoosh"), S("C02") - .15, -3), (sfx("sello"), WT("C02", 3) - .15, 1), (sfx("boom"), WT("C02", 12) - .02, -1),
        (sfx("whoosh"), WT("C02", 16) - .2, -1),
        (sfx("puerta"), S("C03") - GAP["C03"], 3), (sfx("sabana"), WT("C03", 7) - .6, 0), (sfx("boom"), WT("C03", 13) - .02, 1),
        (sfx("whoosh"), S("C04") - .2, -4),
        (rel, S("C05") - .05 - 1.0 + (WT("C05", 4) - S("C05")) , -2),
        (sfx("golpes"), WT("C05", 8) - .04, -2),
        (sfx("candado"), WT("C06", 5) - .05, 0), (sfx("boom"), WT("C06", 11) - .02, 0),
        (sfx("whoosh"), S("C07") - .25, -2),
        (amb, 0.0, -6),
    ]
    ins, flt = [], []
    for i, (lid, *_x) in enumerate(LINEAS):
        ins += ["-i", os.path.join(VOZ, lid + ".wav")]; ms = int(S(lid) * 1000)
        flt.append(f"[{i}:a]aresample=48000,afade=t=in:d=0.012,adelay={ms}|{ms},apad[v{i}]")
    n = len(LINEAS)
    flt.append("".join(f"[v{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0:duration=longest,atrim=0:{TOTAL + 4:.2f},acompressor=threshold=-18dB:ratio=3:attack=5:release=120,loudnorm=I=-15:TP=-1.5:LRA=9,atrim=0:{TOTAL:.2f}[voz]")
    for k, (p, t, db) in enumerate(SFX):
        ins += ["-i", p]; ms = int(max(0, t) * 1000); j = n + k
        flt.append(f"[{j}:a]aresample=48000,loudnorm=I=-26:TP=-6,volume={db}dB,adelay={ms}|{ms},apad[s{k}]")
    flt.append("[voz]" + "".join(f"[s{k}]" for k in range(len(SFX))) + f"amix=inputs={len(SFX) + 1}:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.95[mx]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(flt), "-map", "[mx]", "-ac", "2", out_wav], check=True)

if __name__ == "__main__":
    cs = cortes()
    if len(sys.argv) > 1 and sys.argv[1] == "frames":
        os.makedirs("/tmp/casa_chk", exist_ok=True)
        for name, fa, fb, fn in cs:
            for q in (.3, .85):
                f = int(fa + (fb - fa) * q); frame(f / FPS, fn).save(f"/tmp/casa_chk/{name}_{q}.jpg", quality=85)
        print("TOTAL", round(TOTAL, 2), [(n, round(a / FPS, 2), round(b / FPS, 2)) for n, a, b, _ in cs]); sys.exit()
    with Pool(min(6, os.cpu_count() or 2)) as pool: list(pool.imap_unordered(render_escena, cs))
    wav = os.path.join(TMP, "mezcla.wav"); mezcla(wav)
    lst = os.path.join(TMP, "list.txt"); open(lst, "w").write("".join(f"file '{n}.mp4'\n" for n, *_ in cs))
    hq = os.path.join(TMP, "video_hq.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", hq], check=True)
    out = os.path.join(OUT, "la_casa_de_1_dolar_parte1.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", hq, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-maxrate", "4500k", "-bufsize", "9000k",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], check=True)
    print("ok", out, round(TOTAL, 2))
