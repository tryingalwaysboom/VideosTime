"""Série pt-BR "Lara e o Papai Noel" · DIA 1 — «PAPA NOEL» sem o I. Arte nova (lara_art.py), tiempos/subtítulos reutilizan taller-pov/render.py.
Uso: python3 render_d1.py still 3 12.5 | scenes | info"""
import os, sys, math, json, subprocess, random
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["GUION"] = "guion_d1"; os.environ["VOZDIR"] = os.path.join(HERE, "voz_d1")
sys.path.insert(0, HERE)
import importlib.util
_spec = importlib.util.spec_from_file_location("R", os.path.join(HERE, "..", "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import lara_art as A
from lara_art import font, F_ANTON, F_AND, F_BAL, PB

TMP = os.path.join(HERE, "tmp_d1"); os.makedirs(TMP, exist_ok=True)
W, H, FPS = 1080, 1920, 30
ease, clamp, back = R.ease, R.clamp, R.back
ROJO, VERDE, OURO, CREMA = A.ROJO, A.VERDE, A.OURO, A.CREMA

# ---------------------------------------------------------------- tiempos
R.GAP.clear()
BASE = {"L02": .12, "L03": .35, "L04": .3, "L05": .3, "L06": .4, "L07": .4, "L08": .35, "L09": .3, "L10": .45, "L11": .35, "L12": .45,
        "L13": .4, "L14": .45, "L15": .45, "L16": .5, "L17": .3, "L18": .3, "L19": .35, "L20": .45, "L21": .25}
FLEX = ("L03", "L06", "L07", "L10", "L13", "L14", "L16", "L18")
COLA = .6
R.GAP.update(BASE); _tl, _ = R.timeline(); _fin = _tl["L21"][1] - .1 + COLA
OBJ = float(math.ceil(_fin)); _extra = (OBJ - COLA) - (_tl["L21"][1] - .1)
for _k in FLEX: R.GAP[_k] = BASE[_k] + _extra / len(FLEX)
R.TL, R.TOTAL = R.timeline(); R.TL = {k: (a - .1, b - .1) for k, (a, b) in R.TL.items()}; R.TOTAL = OBJ
TL, TOTAL = R.TL, R.TOTAL; S, E = R.S, R.E; LINEAS = R.LINEAS
IDS = [l[0] for l in LINEAS]; WHO = {l[0]: l[1] for l in LINEAS}
def WI(lid, i):
    cap = [x for x in LINEAS if x[0] == lid][0][3].split(); return R.word_times(lid, cap)[i][0]
def talk(lid, T): return S(lid) <= T < E(lid)
def span(lid):
    i = IDS.index(lid); a = 0.0 if i == 0 else S(lid) - (S(lid) - E(IDS[i - 1])) / 2
    b = TOTAL if i == len(IDS) - 1 else E(lid) + (S(IDS[i + 1]) - E(lid)) / 2
    return a, b

# ---------------------------------------------------------------- subtítulos
def chunks():
    out = []
    for lid, who, tts, cap in LINEAS:
        words = cap.split(); times = R.word_times(lid, words); groups, cur = [], []
        for i, w in enumerate(words):
            cur.append(i)
            if sum(len(words[x].strip("*")) + 1 for x in cur) >= 11 or w.rstrip("*").endswith((".", ",", ":", "?", "!", "…")):
                groups.append(cur); cur = []
        if cur: groups.append(cur)
        for g in groups:
            out.append((times[g[0]][0], times[g[-1]][1], [(words[i].replace("*", "").rstrip(":").upper(), times[i], "*" in words[i]) for i in g], who, lid))
    return out
CH = chunks()
def draw_caption(c, T):
    cy, cx, maxw = 1372, 540, 900
    for idx, (t0, t1, g, who, lid) in enumerate(CH):
        nxt0 = CH[idx + 1][0] if idx + 1 < len(CH) else 1e9
        if not (t0 - .04 <= T < t1 + .3) or T >= nxt0 - .04: continue
        d = ImageDraw.Draw(c); size = 104; f = font(F_ANTON, size); sp = d.textlength(" ", font=f)
        widths = [d.textlength(p, font=f) for p, _, _ in g]; total = sum(widths) + sp * (len(g) - 1)
        if total > maxw:
            size = int(size * maxw / total); f = font(F_ANTON, size); sp = d.textlength(" ", font=f)
            widths = [d.textlength(p, font=f) for p, _, _ in g]; total = sum(widths) + sp * (len(g) - 1)
        x = cx - total / 2
        for (p, (ws, we), star), wd in zip(g, widths):
            if T >= ws - .04:
                k = .8 + .2 * back((T - ws + .04) / .13)
                d.text((x + wd / 2, cy), p, font=font(F_ANTON, size * k), fill=(255, 222, 72) if star else (255, 255, 255), anchor="mm", stroke_width=11, stroke_fill=(52, 14, 22))
            x += wd + sp
        return

# ---------------------------------------------------------------- barra superior (cartaz natalino)
def _barra(n=1):
    K = 3; w, h = 720, 112; im = Image.new("RGBA", (w * K, h * K), (0, 0, 0, 0)); d = ImageDraw.Draw(im); k = lambda *v: tuple(int(x * K) for x in v)
    d.rounded_rectangle(k(0, 0, w, h), 56 * K, fill=(196, 40, 48, 245), outline=(255, 255, 255, 255), width=4 * K)
    for i in range(0, 720, 36): d.ellipse(k(30 + i, 6, 38 + i, 14), fill=(255, 255, 255, 200)); d.ellipse(k(30 + i, h - 14, 38 + i, h - 6), fill=(255, 255, 255, 200))
    d.ellipse(k(10, 10, 102, 102), fill=(255, 205, 70, 255), outline=(255, 255, 255, 255), width=4 * K)
    A.estrela(d, 56 * K, 56 * K, 40 * K, (255, 232, 140, 255))
    d.text(k(56, 58), str(n), font=font(F_ANTON, 54 * K), fill=(150, 30, 30, 255), anchor="mm")
    d.text(k(122, 34), "DIA 1 DE 30", font=font(F_ANTON, 44 * K), fill=(255, 255, 255, 255), anchor="lm")
    d.text(k(122, 80), "A LARA ESCREVE A CARTA SOZINHA", font=font(PB, 25 * K), fill=(255, 226, 190, 255), anchor="lm")
    im = im.resize((w, h), Image.LANCZOS); pad = 22; o = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    a = Image.new("L", o.size, 0); a.paste(im.split()[3].point(lambda v: v * 80 // 255), (pad, pad + 7)); a = a.filter(ImageFilter.GaussianBlur(8))
    o.paste((0, 0, 0, 255), (0, 0), a); o.alpha_composite(im, (pad, pad)); return o
BARRA = _barra(); T_HUD = S("L02") - .1
def draw_hud(c, T):
    if T < T_HUD: return
    y = int(150 - 320 * (1 - ease((T - T_HUD) / .35))); x = (W - BARRA.width) // 2
    if y >= 0: c.alpha_composite(BARRA, (x, y))
    elif -y < BARRA.height: c.alpha_composite(BARRA, (x, 0), (0, -y, BARRA.width, BARRA.height))

# ---------------------------------------------------------------- neve (movimiento constante)
_rn = random.Random(11); FLAKES = [(_rn.random() * W, _rn.random() * H, _rn.uniform(5, 13), _rn.uniform(60, 150), _rn.uniform(0, 6.28)) for _ in range(70)]
def draw_snow(c, T):
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    for x, y, r, v, ph in FLAKES:
        px = (x + 40 * math.sin(T * .9 + ph)) % W; py = (y + v * T) % H
        d.ellipse((px - r, py - r, px + r, py + r), fill=(255, 255, 255, 200))
    c.alpha_composite(o)

# ---------------------------------------------------------------- personajes
EXPR = {"L01": ("sad", "shout"), "L02": ("angry", "angry"), "L03": ("sad", "angry"), "L04": ("neutral", "sad"), "L05": ("neutral", "angry"), "L06": ("neutral", "smile"),
        "L07": ("focus", "smile"), "L08": ("sad", "laugh"), "L09": ("sad", "laugh"), "L10": ("focus", "smile"), "L11": ("sad", "smile"), "L12": ("sad", "smile"),
        "L13": ("focus", "smile"), "L14": ("smile", "smile"), "L15": ("smile", "smile"), "L16": ("sad", "smile"), "L17": ("sad", "sad"), "L18": ("sad", "sad"), "L19": ("hope", "sad")}
def cur_line(T):
    for l in IDS:
        a, b = span(l)
        if a <= T < b: return l
    return IDS[-1]
def char(c, kind, T, cx, cy, s, expr=None, rot=0.0, bob=1.0):
    lid = cur_line(T); who = "L" if kind == "lara" else "C"
    ex = expr or EXPR.get(lid, ("neutral", "neutral"))[0 if kind == "lara" else 1]
    mo = 0
    if WHO[lid] == who and talk(lid, T):
        v = math.sin(T * 13) * (.6 + .4 * math.sin(T * 3.1)); mo = 2 if v > .45 else (1 if v > -.1 else 0)
    spr = A.bust(kind, ex, mo); y = cy + bob * 7 * math.sin(T * 5 + (0 if kind == "lara" else 2)); sx = spr.resize((int(spr.width * s), int(spr.height * s)), Image.BILINEAR)
    if rot: sx = sx.rotate(rot, resample=Image.BILINEAR, expand=True)
    c.alpha_composite(sx, (int(cx - sx.width / 2), int(y - sx.height / 2)))

def spr(c, im, cx, cy, s=1.0, rot=0, alpha=1.0):
    if s != 1: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
    if rot: im = im.rotate(rot, resample=Image.BILINEAR, expand=True)
    if alpha < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    c.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def crayon_img():
    im = Image.new("RGBA", (70, 330), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(35, 0), (62, 66), (8, 66)], fill=(190, 30, 36, 255)); d.rectangle((8, 66, 62, 310), fill=(214, 48, 49, 255))
    for y in (110, 150, 190, 230): d.rectangle((8, y, 62, y + 14), fill=(250, 226, 200, 255))
    d.rectangle((8, 66, 18, 310), fill=(240, 100, 100, 255)); return im
CRAYON = crayon_img()
def mao(c, pose, tip_x, tip_y, s=1.0, tool=True, off=(40, 150), rot=0):
    """mano con crayón: la punta del crayón queda en (tip_x, tip_y)."""
    h, meta = A.hand(pose)
    hx, hy = tip_x + off[0] * s, tip_y + off[1] * s
    h2 = h.resize((int(h.width * s), int(h.height * s)), Image.BILINEAR)
    px, py = meta["pinch"]; c.alpha_composite(h2, (int(hx - px * s), int(hy - py * s)))
    if tool:
        cr = CRAYON.resize((int(CRAYON.width * s), int(CRAYON.height * s)), Image.BILINEAR).rotate(-12, resample=Image.BILINEAR, expand=True)
        c.alpha_composite(cr, (int(tip_x - cr.width * .3), int(tip_y - 4 * s)))
        # dedos encima del crayón
        c.alpha_composite(h2.crop((int(px * s - 70 * s), int(py * s - 40 * s), int(px * s + 40 * s), int(py * s + 60 * s))), (int(hx - 70 * s), int(hy - 40 * s)))

def madeira(T, z0=1.0):
    im = Image.new("RGB", (W, H), (176, 122, 80)); d = ImageDraw.Draw(im)
    for y in range(0, H, 120): d.line((0, y, W, y), fill=(156, 104, 66), width=4)
    for i in range(0, W, 3): pass
    g = Image.linear_gradient("L").resize((W, H)).rotate(90); im.paste((120, 80, 52), (0, 0), g.point(lambda v: v // 4))
    return im.convert("RGBA")

def mesa(c, y=1440):
    d = ImageDraw.Draw(c); d.rectangle((0, y, W, H), fill=(170, 116, 76)); d.rectangle((0, y, W, y + 18), fill=(212, 160, 112))
    for i in range(1, 6): d.line((0, y + 18 + i * 90, W, y + 18 + i * 90), fill=(150, 100, 64), width=4)

def vignette(c, a=110):
    v = A.__dict__.get("_VIG")
    if v is None:
        v = Image.radial_gradient("L").resize((W, H)); v = v.point(lambda x: max(0, min(255, int((x - 150) * a / 105)))); A._VIG = v
    c.paste((20, 10, 30), (0, 0), v)

# ---------------------------------------------------------------- cenas (planos)
def camfor(bg, T, t0, t1, k, fx=.5, fy=.5, z=(1.25, 1.45)):
    up = k % 2 == 0; z0, z1 = z if up else z[::-1]
    return A.cam(bg, T, t0, z0, z1, fx - .08 * (1 if up else -1) * 0, fx + (.08 if up else -.08), fy, fy, dur=max(.1, t1 - t0)).convert("RGBA")

def sh_sala_wall(T, t0, t1, k, lid):
    c = camfor(A.bg_sala(True), T, t0, t1, k, .35, .45, (1.22, 1.5)); u = (T - t0)
    char(c, "caio", T, 280 - 40 * (1 - ease(u / .4)), 1450, .85, rot=-5 * math.sin(T * 14) * (1 if lid == "L01" else 0)); char(c, "lara", T, 830, 1500, .78)
    return c
def sh_wall_zoom(T, t0, t1, k, lid): return camfor(A.bg_sala(True), T, t0, t1, k, .4, .36, (1.5, 2.3))
def sh_close(kind):
    def f(T, t0, t1, k, lid):
        c = camfor(A.bg_sala(False), T, t0, t1, k, .45, .5, (1.5, 1.7)); c.alpha_composite(Image.new("RGBA", (W, H), (255, 240, 220, 60)))
        sh = 5 * math.sin(T * 40) if (kind == "caio" and lid in ("L01", "L08")) else 0
        char(c, kind, T, 540 + sh, 960, 1.22, rot=sh * .2); mesa(c); return c
    return f
def sh_two(T, t0, t1, k, lid):
    c = camfor(A.bg_sala(False), T, t0, t1, k, .4, .5, (1.3, 1.5)); char(c, "caio", T, 300, 1180, .8, rot=4); char(c, "lara", T, 780, 1200, .8, rot=-4); return c
def sh_mao_papel(T, t0, t1, k, lid):
    c = camfor(A.bg_cozinha(False), T, t0, t1, k, .35, .6, (1.4, 1.6)); u = ease((T - t0) / .5)
    p, _ = A.paper("", lines=True); spr(c, p, 760 + 420 * (1 - u), 800, .62, -6)
    mao(c, "pinza", 330, 1500 - 520 * u, .95, True, (40, 150)); return c
def sh_calendario(T, t0, t1, k, lid):
    c = camfor(A.bg_sala(False), T, t0, t1, k, .5, .5, (1.45, 1.5)); c.alpha_composite(Image.new("RGBA", (W, H), (60, 20, 30, 120)))
    d = ImageDraw.Draw(c); x0, y0, w, h = 60, 520, 960, 900
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 40, fill=(255, 250, 238), outline=ROJO, width=10); d.rounded_rectangle((x0, y0, x0 + w, y0 + 150), 40, fill=ROJO)
    d.rectangle((x0, y0 + 100, x0 + w, y0 + 150), fill=ROJO); d.text((x0 + w / 2, y0 + 78), "30 DIAS", font=font(F_ANTON, 100), fill=(255, 255, 255), anchor="mm")
    cw, ch = 150, 128
    for i in range(30):
        r, cc = divmod(i, 6); t_i = S("L06") + .55 + i * .08; uu = back((T - t_i) / .22) if T >= t_i else 0
        if uu <= 0: continue
        cx = x0 + 45 + cc * (cw + 3) + cw / 2; cy = y0 + 190 + r * (ch + 8) + ch / 2; s = .9 * uu
        col = (255, 205, 70) if i == 0 else ((234, 246, 236) if (i % 2) else (252, 232, 232))
        d.rounded_rectangle((cx - cw / 2 * s, cy - ch / 2 * s, cx + cw / 2 * s, cy + ch / 2 * s), 22, fill=col, outline=(200, 80, 80) if i == 0 else (210, 190, 180), width=4)
        d.text((cx, cy), str(i + 1), font=font(F_ANTON, 62 * s), fill=(150, 30, 30) if i == 0 else (90, 70, 70), anchor="mm")
    if T > S("L06") + 1.0:
        pu = back((T - S("L06") - 1.0) / .3); d.rounded_rectangle((x0 + 20, y0 + 150, x0 + 175 + 20, y0 + 190), 12, fill=(222, 50, 46)); d.text((x0 + 108, y0 + 170), "HOJE", font=font(PB, 26), fill=(255, 255, 255), anchor="mm")
    return c
TXT = {"L07": ("PAPA NOEL", False, 1), "L10": ("PAPAI NOEL", True, 2), "L13": ("PAPAI NOEL", False, 3)}
def sh_papel(lid):
    def f(T, t0, t1, k, _lid):
        txt, flip, seed = TXT[lid]; c = madeira(T)
        a, b = S(lid), E(lid); prog = clamp((T - a - .1) / max(.5, (b - a) - .5)); letters = len(txt.replace(" ", "")); n = int(prog * letters + .001) + (1 if prog > 0 else 0)
        n = min(n, letters); zoom = 1.0 + .05 * (T - t0) / max(.1, t1 - t0)
        p, last = A.paper(txt, n=n, flipE=flip, seed=seed); spr(c, p, 540, 900, .98 * zoom, 0)
        tip = (540 + (last[0] - 440) * .98 * zoom, 900 + (last[1] - 550) * .98 * zoom + 70)
        if prog < 1: mao(c, "pinza", tip[0], tip[1] - 30 + 6 * math.sin(T * 30), .9, True, (40, 150))
        else:
            if lid == "L10":  # el E virado: círculo rojo que pulsa
                u = clamp((T - b + .4) / .3); d = ImageDraw.Draw(c); px = 540 + 215; r = 85 * (1 + .06 * math.sin(T * 10))
                d.ellipse((px - r, 950 - r, px + r, 950 + r), outline=(255, 255, 255), width=10) if u > 0 else None
            if lid == "L13":
                d = ImageDraw.Draw(c); A.estrela(d, 880, 560, 70 * (1 + .08 * math.sin(T * 8)), OURO)
        return c
    return f
def sh_crumple(T, t0, t1, k, lid):
    c = madeira(T); u = clamp((T - t0) / 1.2); p, _ = A.paper("PAPAI NOEL", flipE=True, seed=2)
    s = .98 - .6 * ease(u); rot = 40 * u; spr(c, p, 540, 900 + 200 * u, s, rot)
    d = ImageDraw.Draw(c)
    if u > .8:
        for i in range(5): a = i * 1.26 + T; d.line((540 + 120 * math.cos(a), 1100 + 120 * math.sin(a), 540 + 180 * math.cos(a), 1100 + 180 * math.sin(a)), fill=(255, 255, 255), width=8)
    return c
def sh_lara_sad(T, t0, t1, k, lid):
    c = camfor(A.bg_sala(False), T, t0, t1, k, .5, .5, (1.5, 1.75)); c.alpha_composite(Image.new("RGBA", (W, H), (30, 30, 70, 70))); char(c, "lara", T, 540, 960, 1.22, "sad"); mesa(c); return c
def sh_telefone(T, t0, t1, k, lid):
    c = camfor(A.bg_sala(False), T, t0, t1, k, .5, .5, (1.5, 1.5)); c.alpha_composite(Image.new("RGBA", (W, H), (30, 20, 50, 130)))
    ring = clamp((T - S(lid)) / .01); sh = 6 * math.sin(T * 35) if T < S(lid) + .5 else 0
    spr(c, A.telefone(pulso=(T * .8) % 1), 540 + sh, 930, .92, rot=-3 + sh * .3); return c
def sh_pente(T, t0, t1, k, lid):
    c = camfor(A.bg_sala(False), T, t0, t1, k, .5, .5, (1.5, 1.5)); c.alpha_composite(Image.new("RGBA", (W, H), (255, 244, 220, 150)))
    u = back((T - t0) / .35); d = ImageDraw.Draw(c)
    d.rounded_rectangle((70, 520, 1010, 1260), 50, fill=(255, 252, 244), outline=(255, 190, 90), width=10)
    spr(c, A.comb(), 330, 880, 1.1 * u, rot=0); d.text((600, 880), "=", font=font(F_ANTON, 200), fill=(120, 90, 60), anchor="mm")
    p = Image.new("RGBA", (360, 420), (0, 0, 0, 0)); pd = ImageDraw.Draw(p); pd.text((180, 210), "E", font=font(F_AND, 360), fill=(222, 50, 46, 255), anchor="mm"); spr(c, p, 820, 880, 1.0 * back((T - t0 - .3) / .35))
    d.text((540, 1170), "UM RISCO E TRÊS DENTES", font=font(PB, 44), fill=(120, 80, 60), anchor="mm"); return c
def sh_geladeira(noite=False, apagar=False, lara=False, close=False):
    def f(T, t0, t1, k, lid):
        c = camfor(A.bg_cozinha(noite), T, t0, t1, k, .45, .5, (1.45, 1.7) if not close else (1.9, 2.2)); u = back((T - t0) / .4)
        ap = 0.0
        if lid == "L15": ap = clamp((T - S("L15") - 1.4) / 1.2)
        if lid in ("L16", "L17"): ap = 1.0
        b = A.bilhete(apagando=ap); cx, cy = (540, 560) if lara else (540, 880)
        if close: cy = 900
        spr(c, b, cx, cy, (.98 if not lara else .72) * (u if lid == "L14" else 1), -2)
        if lid == "L14":   # ímã que cai + mão
            my = cy - 270 * (1 - ease((T - t0 - .3) / .3)) - 110; d = ImageDraw.Draw(c); d.ellipse((cx - 40, my - 40, cx + 40, my + 40), fill=ROJO, outline=(255, 255, 255), width=6); A.estrela(d, cx, my, 24, OURO)
            mao(c, "apunta", cx + 30, my + 20, .95, False, (60, 200))
        if lid == "L15":   # sombra de mão que apaga o I
            h, meta = A.hand("apunta"); h = h.point(lambda v: v) if False else h
            tint = Image.new("RGBA", h.size, (20, 20, 60, 255)); sil = Image.composite(tint, Image.new("RGBA", h.size, (0, 0, 0, 0)), h.split()[3])
            ex, ey = meta["indice"]; tx = cx + 200 + 25 * math.sin(T * 18); ty = cy - 40
            u2 = ease((T - S("L15") - .3) / .6); sil2 = sil.resize((int(sil.width * .95), int(sil.height * .95)), Image.BILINEAR)
            c.alpha_composite(sil2, (int(tx - ex * .95 + 500 * (1 - u2)), int(ty - ey * .95 + 300 * (1 - u2))))
        if lara: char(c, "lara", T, 540, 1040, .8, "sad")
        return c
    return f
def sh_porta(T, t0, t1, k, lid):
    c = camfor(A.bg_corredor(), T, t0, t1, k, .55, .5, (1.3, 1.5)); char(c, "caio", T, 640, 1180, .78, "sad", rot=-3)
    d = ImageDraw.Draw(c); vignette(c, 150); return c
def sh_split(T, t0, t1, k, lid):
    c = camfor(A.bg_cozinha(False), T, t0, t1, k, .5, .5, (1.3, 1.35)); c.alpha_composite(Image.new("RGBA", (W, H), (20, 10, 40, 150))); d = ImageDraw.Draw(c)
    cards = [("CORRIGIR", (214, 48, 49), 30, 1), ("DEIXAR", (236, 96, 146), 555, 0)]
    for name, col, x0, left in cards:
        xs, ys, w, h = x0, 320, 495, 940
        d.rounded_rectangle((xs, ys, xs + w, ys + h), 40, fill=(255, 250, 240), outline=col, width=10)
        b = A.bilhete(apagando=1.0); spr(c, b, xs + w / 2, 700, .7)
        if left:
            # I vermelho escrito por cima + lápis
            tt = clamp((T - S("L20") - .5) / .6)
            if tt > 0:
                f = font(F_AND, 80); d.text((xs + 400 + 0, 645), "I", font=f, fill=(20, 150, 90) if False else (30, 140, 80), anchor="mm")
            mao(c, "pinza", xs + 410, 700, .5, True, (40, 150))
        else:
            ch = char_heart(T); spr(c, ch, xs + w / 2, 1060, 1.0)
            char(c, "lara", T, xs + w / 2, 1010, .5, "hope", bob=0)
        # tarjeta de una palabra (aparece con la palabra)
        wi = WI("L21", 1) if left else WI("L21", 3); u = back((T - wi + .1) / .25) if T >= wi - .1 else 0
        if T >= S("L21") - .05 and u <= 0: u = .0
        if u > 0 or T >= wi:
            u = max(u, 0.01); ww, hh = 440 * u, 130 * u; cx, cy = xs + w / 2, 1190
            d.rounded_rectangle((cx - ww / 2, cy - hh / 2, cx + ww / 2, cy + hh / 2), 30, fill=col, outline=(255, 255, 255), width=6)
            d.text((cx, cy + 4), name, font=font(F_ANTON, 82 * u), fill=(255, 255, 255), anchor="mm")
    d.line((540, 320, 540, 1260), fill=(255, 255, 255), width=8)
    return c
def char_heart(T):
    im = Image.new("RGBA", (220, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(im); col = (236, 70, 120, 255)
    d.ellipse((10, 10, 120, 120), fill=col); d.ellipse((100, 10, 210, 120), fill=col); d.polygon([(14, 80), (206, 80), (110, 190)], fill=col)
    s = 1 + .08 * math.sin(T * 9); return im.resize((int(220 * s * .8), int(200 * s * .8)), Image.BILINEAR)

SPEC = {"L01": [sh_sala_wall, sh_close("caio")], "L02": [sh_close("lara")], "L03": [sh_two, sh_wall_zoom, sh_sala_wall], "L04": [sh_mao_papel],
        "L05": [sh_close("lara")], "L06": [sh_calendario], "L07": [sh_papel("L07"), sh_close("lara")], "L08": [sh_close("caio")], "L09": [sh_close("lara")],
        "L10": [sh_papel("L10")], "L11": [sh_crumple, sh_lara_sad], "L12": [sh_telefone, sh_pente], "L13": [sh_papel("L13"), sh_close("lara"), sh_papel("L13")],
        "L14": [sh_geladeira()], "L15": [sh_geladeira(True)], "L16": [sh_geladeira(False, lara=True)], "L17": [sh_lara_sad, sh_geladeira(False, close=True)],
        "L18": [sh_porta], "L19": [sh_close("lara")], "L20": [sh_split], "L21": [sh_split]}
def build_shots():
    out = []
    for lid in IDS:
        a, b = span(lid); n = max(1, round((b - a) / 2.0)); fs = SPEC[lid]
        if lid in ("L20", "L21"): n = 1
        for i in range(n): out.append((a + (b - a) * i / n, a + (b - a) * (i + 1) / n, fs[i % len(fs)], i, lid))
    return out
SHOTS = build_shots()
SHOTS[-1] = (SHOTS[-1][0], TOTAL, *SHOTS[-1][2:])

def frame(T):
    for t0, t1, fn, k, lid in SHOTS:
        if t0 <= T < t1 or fn is SHOTS[-1][2] and t1 == TOTAL and T >= t0: break
    c = fn(T, t0, t1, k, lid)
    if T - t0 < .12 and t0 > 0: c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(120 * (1 - (T - t0) / .12)))))   # destello de corte (nunca negro)
    if lid not in ("L20", "L21"): draw_snow(c, T)
    draw_hud(c, T); draw_caption(c, T); return c.convert("RGB")

def pipe(path):
    return subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                             "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS), path], stdin=subprocess.PIPE)
def render_scene(i):
    t0, t1 = SHOTS[i][0], SHOTS[i][1]; f0 = int(round(t0 * FPS)); f1 = int(round(t1 * FPS)) if i < len(SHOTS) - 1 else int(TOTAL * FPS)
    tmp = os.path.join(TMP, f"s{i:02d}.tmp.mp4"); p = pipe(tmp)
    for f in range(f0, f1): p.stdin.write(frame(f / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.rename(tmp, os.path.join(TMP, f"s{i:02d}.mp4"))

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "still":
        for t in sys.argv[2:]: frame(float(t)).save(os.path.join(TMP, f"f_{float(t):06.2f}.jpg"), quality=88)
    elif cmd == "info":
        print("TOTAL", TOTAL, "shots", len(SHOTS))
        for t0, t1, fn, k, lid in SHOTS: print(f"{t0:6.2f} {t1:6.2f} {lid} {getattr(fn,'__name__','?')}")
    elif cmd == "scenes":
        from multiprocessing import Pool
        ids = [int(x) for x in sys.argv[2:]] or list(range(len(SHOTS)))
        with Pool(2) as pl: pl.map(render_scene, ids)
        with open(os.path.join(TMP, "list.txt"), "w") as fh:
            for i in range(len(SHOTS)): fh.write(f"file 's{i:02d}.mp4'\n")
