"""La nota bajo la puerta · Día 0. Escenas por código sobre las variantes de Sergio (var/), cámara con zoom, pegatinas de papel,
subtítulos de tira de papel con cinta (zona segura TikTok) y crossfades cortos dentro de cada escena (sin negro)."""
import os, sys, json, math, wave, subprocess
import numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__)); VOZ = os.path.join(HERE, "voz0b"); VAR = os.path.join(HERE, "var")
TMP = os.path.join(HERE, "tmp2"); os.makedirs(TMP, exist_ok=True)
FD = os.path.join(HERE, "..", "mateo-pov", "fonts")
FPS, W, H = 30, 1080, 1920
CORAL, CREAM, BROWN, TEAL, MUST, INK = (226, 86, 70), (250, 238, 212), (72, 40, 52), (44, 112, 128), (232, 178, 62), (52, 30, 40)
def F(n, s): return ImageFont.truetype(os.path.join(FD, n), s)

DISP = {"L01": "Llevo 6 años sin salir, nadie sabe dónde vivo, y acaba de aparecer esto.",
        "L02": "Tienes 30 días, hoy acércate a la puerta.",
        "L03": "Está firmada... alguien que te echa de menos.",
        "L04": "Y ahora oigo pasos. Se han parado... justo al otro lado.",
        "L05": "¿Me acerco a la puerta... o hago como que no estoy? Tú decides: A o B."}
IDS = list(DISP)

# ---------- tiempos ----------
DUR, ENV = {}, {}
for lid in IDS:
    with wave.open(os.path.join(VOZ, lid + ".wav")) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768; sr = w.getframerate()
    DUR[lid] = len(a) / sr; hop = sr // FPS
    r = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a), hop)] or [0]); ref = np.percentile(r, 92) or 1
    ENV[lid] = np.convolve(np.clip(r / ref, 0, 1.2), [.25, .5, .25], mode="same")
GAP = {"L02": .12, "L03": .1, "L04": .12, "L05": .14}
TL, t = {}, .12
for lid in IDS:
    t += GAP.get(lid, .2) if lid != "L01" else 0; TL[lid] = (t, t + DUR[lid]); t += DUR[lid]
TOTAL = TL["L05"][1] + 1.0     # el voto queda en pantalla un momento tras la última frase
def S_(l): return TL[l][0]
def E_(l): return TL[l][1]

def _pal(lid):
    disp = DISP[lid].split(); wj = json.load(open(os.path.join(VOZ, lid + ".json"))); off = json.load(open(os.path.join(VOZ, "offsets.json")))[lid]["off"]; tp = json.load(open(os.path.join(VOZ, "offsets.json")))[lid]["tempo"]
    tt = [(max(0, w["inicio"] - off) / tp, max(0, w["fin"] - off) / tp) for w in wj]; out = []
    for i, p in enumerate(disp):
        k = i if len(tt) == len(disp) else min(len(tt) - 1, round(i * (len(tt) - 1) / max(1, len(disp) - 1)))
        out.append((p, tt[k][0], tt[k][1]))
    return out
PAL = {l: _pal(l) for l in IDS}
def WT(lid, pal):
    for p, a0, _ in PAL[lid]:
        if pal.lower() in p.lower().strip("¿?¡!.,…:"): return S_(lid) + a0
    return S_(lid)

# ---------- utilidades ----------
def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def eout(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def back(x):
    x = min(max(x, 0), 1); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def lerp(a, b, k): return a + (b - a) * k

VARS = {}
def var(n):
    if n not in VARS: VARS[n] = Image.open(os.path.join(VAR, n + "_2x.png")).convert("RGB")
    return VARS[n]
SPRITE = Image.open(os.path.join(VAR, "nota_sprite.png")).convert("RGBA")

def sergio_var(T, boca="closed"):
    """Variante de Sergio: parpadeo cada ~2,7 s; boca según la voz si habla."""
    bl = (T % 2.7) < .13 or (T % 4.1) < .1 and T > 3
    if boca == "closed": return "blink_closed" if bl else "open_closed"
    return "blink_o" if bl else ("open_o" if boca == "o" else "open_small")

def paste(fr, spr, cx, cy, rot=0, sc=1.0, al=1.0):
    """pega un sprite RGBA centrado en (cx,cy) con giro/escala/opacidad (el sprite viene a 2x: se reduce a la mitad)."""
    if sc <= 0.01 or al <= 0: return
    w, h = spr.size; k = sc * .5
    im = spr.resize((max(1, int(w * k)), max(1, int(h * k))), Image.LANCZOS) if abs(k - 1) > .01 else spr
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if al < 1: im.putalpha(im.getchannel("A").point(lambda v: int(v * al)))
    fr.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2))) if (cx - im.width / 2) >= 0 and (cy - im.height / 2) >= 0 and cx + im.width / 2 <= W and cy + im.height / 2 <= H else _safe(fr, im, int(cx - im.width / 2), int(cy - im.height / 2))
def _safe(fr, im, x, y):
    fr.paste(im, (x, y), im)

@lru_cache(maxsize=256)
def tag(text, fill=CREAM, col=INK, size=64, pad=30, tape=True, font="Baloo2-ExtraBold.ttf", w2=None):
    """etiqueta de papel con cinta, a 2x."""
    f = F(font, size * 2); lines = text.split("\n")
    wd = max(f.getbbox(l)[2] for l in lines) + pad * 4; ht = int(len(lines) * size * 2.0) + pad * 3
    im = Image.new("RGBA", (wd + 40, ht + 50), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((26, 36, wd + 20, ht + 30), 22, fill=(40, 20, 30, 90))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d.rounded_rectangle((20, 20, wd + 14, ht + 10), 20, fill=fill + (255,))
    for i in range(0, wd - 40, 46): d.line((40 + i, 34, 40 + i + 22, 34), fill=tuple(int(c * .93) for c in fill) + (255,), width=3)
    for i, l in enumerate(lines): d.text(((wd + 34) / 2, 20 + pad + int(size * 1.0) + i * size * 2.0), l, font=f, fill=col, anchor="mm")
    if tape:
        for x0, rr in ((wd * .12, -8), (wd * .86, 7)):
            tp = Image.new("RGBA", (150, 54), (240, 214, 130, 210)); tp = tp.rotate(rr, expand=True); im.alpha_composite(tp, (int(x0 - tp.width / 2), 2))
    return im

def pop(fr, spr, cx, cy, t0, T, rot=0, dur=.3, hold=None):
    if T < t0: return
    k = back((T - t0) / dur); al = 1.0
    if hold and T > hold: al = max(0, 1 - (T - hold) / .15)
    paste(fr, spr, cx, cy, rot, k, al)

# ---------- subtítulos: tiras de papel con cinta (zona segura: y≈1250) ----------
def _chunk(lid, T):
    pal = PAL[lid]; tl = T - S_(lid); idx = 0
    for i, (_, a0, a1) in enumerate(pal):
        if tl >= a0 - .02: idx = i
    # trozos de ≤4 palabras que cortan en signos de puntuación
    ch, cur = [], []
    for i, (p, *_) in enumerate(pal):
        cur.append(i)
        if len(cur) >= 4 or p[-1] in ".?!…" or p[-1] == ",": ch.append(cur); cur = []
    if cur: ch.append(cur)
    for c in ch:
        if idx in c: return c, idx
    return ch[-1], idx

@lru_cache(maxsize=512)
def strip(words, act, rot):
    f = F("Baloo2-ExtraBold.ttf", 120); sp = f.getlength(" ")
    wl = [f.getlength(w) for w in words]; tw = sum(wl) + sp * (len(words) - 1); pad = 70
    im = Image.new("RGBA", (int(tw + pad * 2 + 60), 330), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((34, 64, im.width - 20, 300), 26, fill=(40, 20, 30, 110))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    d.rounded_rectangle((26, 40, im.width - 28, 280), 26, fill=CREAM + (255,))
    d.rounded_rectangle((26, 40, im.width - 28, 280), 26, outline=(226, 206, 160, 255), width=5)
    x = 26 + pad
    for i, (w, wl_) in enumerate(zip(words, wl)):
        d.text((x, 160), w, font=f, fill=CORAL if i == act else BROWN, anchor="lm"); x += wl_ + sp
    for x0, rr in ((70, -9), (im.width - 90, 8)):
        tp = Image.new("RGBA", (130, 50), (240, 214, 130, 215)).rotate(rr, expand=True); im.alpha_composite(tp, (x0 - tp.width // 2, 14))
    return im.rotate(rot, resample=Image.BICUBIC, expand=True)

def subs(fr, T):
    for lid in IDS:
        if S_(lid) - .05 <= T <= E_(lid) + .35:
            c, idx = _chunk(lid, T); words = tuple(PAL[lid][i][0] for i in c); act = c.index(idx) if idx in c else 0
            spr = strip(words, act, 1.1 if c[0] % 2 else -1.1)
            k = min(1.0, 930 / (spr.width * .5)); paste(fr, spr, W / 2, 1250, 0, k); return

# ---------- cámara ----------
def cam(base, z, cx, cy):
    cw, ch = W / z, H / z; x0 = min(max(cx - cw / 2, 0), W - cw); y0 = min(max(cy - ch / 2, 0), H - ch)
    im = base.crop((int(x0 * 2), int(y0 * 2), int((x0 + cw) * 2), int((y0 + ch) * 2))).resize((W, H), Image.LANCZOS)
    return im.convert("RGBA"), x0, y0
def w2s(x, y, z, x0, y0): return (x - x0) * z, (y - y0) * z

def spark(fr, x, y, T, seed, size=22, col=(120, 200, 255)):
    k = (math.sin(T * 7 + seed * 2.1) + 1) / 2
    if k < .15: return
    r = size * (.5 + k); d = ImageDraw.Draw(fr)
    d.polygon([(x, y - r), (x + r * .22, y - r * .22), (x + r, y), (x + r * .22, y + r * .22), (x, y + r), (x - r * .22, y + r * .22), (x - r, y), (x - r * .22, y - r * .22)], fill=col + (235,))

# ---------- escenas (planos cortos, un corte cada ~2 s) ----------
def punch(T, t0): return 1 + .07 * max(0, 1 - (T - t0) / .18)
def zc(T, t0, t1, z0, z1, c0, c1):
    k = ease((T - t0) / max(.01, t1 - t0)); return lerp(z0, z1, k) * punch(T, t0), lerp(c0[0], c1[0], k), lerp(c0[1], c1[1], k)
def shot(T, t0, t1, z0, z1, c0, c1, boca="closed"):
    z, cx, cy = zc(T, t0, t1, z0, z1, c0, c1); return cam(var(sergio_var(T, boca)), z, cx, cy) + (z,)

B1 = WT("L01", "nadie") - .05; B2 = WT("L01", "acaba") - .05
NOTE_T0 = B2 + .05; NOTE_D = .8; NOTE_END = (330, 1250)
def note_pos(T):
    k = eout((T - NOTE_T0) / NOTE_D); return lerp(236, NOTE_END[0], k), lerp(1100, NOTE_END[1], k), lerp(.28, 1.0, k), lerp(-3, -8, k)
def draw_note_world(fr, T, z, x0, y0):
    if T < NOTE_T0: return
    nx, ny, ns, nr = note_pos(T); cx, cy = w2s(nx, ny, z, x0, y0); layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    paste(layer, SPRITE, cx, cy, nr, ns * z)
    cut = int((1106 - y0) * z)
    if cut > 0: layer.paste((0, 0, 0, 0), (0, 0, W, min(H, cut)))
    fr.alpha_composite(layer)
def top_tag(fr, T): pop(fr, tag("DÍA 0", MUST, INK, 66, 26), 205, 250, .15, T, -4)

def s_intro(T):
    t0 = 0.0; fr, x0, y0, z = shot(T, t0, B1, 1.0, 1.4, (540, 960), (640, 640), "closed"); top_tag(fr, T)
    pop(fr, tag("6 AÑOS\nSIN SALIR", CREAM, CORAL, 62, 24), 790, 300, WT("L01", "6") - .05, T, 3); return fr
def s_puerta(T):
    fr, x0, y0, z = shot(T, B1, B2, 1.9, 2.3, (240, 600), (240, 640))
    sh = math.sin(T * 50) * 3 * max(0, 1 - (T - B1) / .4); fr = fr.transform(fr.size, Image.AFFINE, (1, 0, sh, 0, 1, 0))
    pop(fr, tag("NADIE SABE\nDÓNDE VIVO", MUST, INK, 62, 24), 640, 330, B1 + .05, T, -3); top_tag(fr, T); return fr
def s_nota(T):
    fr, x0, y0, z = shot(T, B2, S_("L02") - .1, 1.5, 2.1, (300, 1100), (310, 1200)); draw_note_world(fr, T, z, x0, y0)
    nx, ny, *_ = note_pos(T); sx, sy = w2s(nx, ny, z, x0, y0)
    if T > NOTE_T0 + .6:
        for j, (dx, dy, sz) in enumerate([(-150, -90, 28), (130, -110, 22), (-50, 100, 18), (170, 50, 26), (10, -150, 16)]): spark(fr, sx + dx * z / 2, sy + dy * z / 2, T, j, sz)
    top_tag(fr, T); return fr

@lru_cache(maxsize=1)
def papel_grande():
    im = Image.new("RGBA", (1960, 1500), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((60, 90, 1920, 1460), 30, fill=(30, 12, 24, 130)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(26)))
    d.rounded_rectangle((40, 40, 1900, 1400), 30, fill=(252, 244, 222, 255))
    for y in range(240, 1360, 180): d.line((120, y, 1820, y), fill=(206, 222, 238, 255), width=5)
    d.line((250, 60, 250, 1380), fill=(232, 150, 140, 255), width=5)
    rng = np.random.default_rng(4)
    for _ in range(95):                         # purpurina azul
        x, y, r = int(rng.integers(90, 1850)), int(rng.integers(80, 1360)), int(rng.integers(5, 12)); d.ellipse((x - r, y - r, x + r, y + r), fill=(110, 190, 255, 255))
    return im

@lru_cache(maxsize=64)
def manuscrito(lines_shown):
    im = papel_grande().copy(); d = ImageDraw.Draw(im); f = F("Caveat.ttf", 250)
    for i, (txt, col) in enumerate(lines_shown): d.text((310, 240 + i * 230), txt, font=f, fill=col, anchor="ls")
    return im

def carta(T, t0, lid, lineas, colores, rot=-4):
    from PIL import ImageEnhance
    fr = ImageEnhance.Brightness(var("open_closed").resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(14))).enhance(.45).convert("RGBA")
    k = back((T - t0) / .3); pal = PAL[lid]; tl = T - S_(lid); show = []
    for (txt, idxs), col in zip(lineas, colores):
        w = txt.split(); nvis = sum(1 for j in idxs if tl >= pal[j][1] - .02)
        if nvis: show.append((" ".join(w[:nvis]) if len(w) == len(idxs) else txt, col))
    paste(fr, manuscrito(tuple(show)), 540, 720, rot + math.sin(T * 1.6), k)
    for j, (dx, dy, sz) in enumerate([(-420, -160, 24), (400, -300, 20), (330, 250, 26), (-380, 220, 18)]): spark(fr, 540 + dx, 720 + dy, T, j, sz)
    top_tag(fr, T); return fr
C2 = WT("L02", "hoy") - .1
def s_carta1(T): return carta(T, S_("L02") - .1, "L02", [("Tienes 30 días.", [0, 1, 2]), ("Hoy, acércate", [3, 4]), ("a la puerta.", [5, 6, 7])], [INK, INK, CORAL])
def s_radio(T):
    fr, x0, y0, z = shot(T, C2, S_("L03") - .1, 1.8, 2.1, (240, 1130), (250, 1140)); draw_note_world(fr, T, z, x0, y0)
    pop(fr, tag("RADIO DE LIBERTAD\n0 m", (46, 70, 66), (255, 214, 150), 58, 26), 600, 330, C2 + .05, T, 2)
    d = ImageDraw.Draw(fr)
    if T > C2 + .3:
        for i in range(30):
            x = 70 + i * 31; d.rounded_rectangle((x, 450, x + 22, 490), 5, fill=(250, 238, 212, 255) if i else CORAL + (255,), outline=(120, 70, 60, 255), width=2)
    top_tag(fr, T); return fr
def s_quien(T):
    t0 = S_("L03") - .1; fr, x0, y0, z = shot(T, t0, WT("L03", "alguien") - .1, 1.7, 2.0, (640, 560), (640, 580), "small")
    pop(fr, tag("?", CREAM, CORAL, 130, 30, False), 170, 520, t0 + .1, T, -8); pop(fr, tag("¿QUIÉN?", MUST, INK, 64, 24), 760, 300, t0 + .25, T, 4)
    top_tag(fr, T); return fr
def s_firma(T):
    return carta(T, WT("L03", "alguien") - .1, "L03", [("alguien", [2]), ("que te echa", [3, 4, 5]), ("de menos.", [6, 7])], [CORAL, INK, INK], 3)
P0 = S_("L04") - .1
def s_pasos(T):
    fr, x0, y0, z = shot(T, P0, WT("L04", "parado") - .1, 1.5, 2.0, (640, 700), (640, 600), "small")
    pop(fr, tag("pas...\npas...", CREAM, TEAL, 64, 24), 780, 330, WT("L04", "pasos") - .05, T, 5); top_tag(fr, T); return fr
def zapatos(fr, T, ta, z, x0, y0, big=1):
    a = min(1, max(0, (T - ta) / .2)); d = ImageDraw.Draw(fr)
    for gx in (150, 215):
        sx, sy = w2s(gx, 1103, z, x0, y0); sw = 24 * z * big; col = (46, 26, 38, int(255 * a))
        d.rounded_rectangle((sx - sw, sy - 10 * z * big, sx + sw, sy + 9 * z * big), int(5 * z), fill=col)
PA = WT("L04", "parado") - .1; PB = WT("L04", "otro") - .15
def s_slit(T):
    fr, x0, y0, z = shot(T, PA, PB, 2.0, 2.4, (240, 1130), (200, 1120)); draw_note_world(fr, T, z, x0, y0); zapatos(fr, T, PA + .15, z, x0, y0); top_tag(fr, T); return fr
def s_extremo(T):
    fr, x0, y0, z = shot(T, PB, S_("L05") - .1, 3.4, 3.8, (190, 1105), (190, 1105)); zapatos(fr, T, PB - 1, z, x0, y0)
    from PIL import ImageEnhance
    v = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(v).rectangle((0, 0, W, H), fill=(10, 4, 10, 110)); fr.alpha_composite(v)
    pop(fr, tag("AL OTRO LADO", CORAL, CREAM, 66, 24), 540, 330, PB + .05, T, -2); top_tag(fr, T); return fr

@lru_cache(maxsize=4)
def ticket(letra, texto, col):
    im = Image.new("RGBA", (1800, 460), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((50, 70, 1760, 430), 40, fill=(30, 12, 24, 120)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    d.rounded_rectangle((30, 30, 1740, 400), 40, fill=CREAM + (255,)); d.rounded_rectangle((30, 30, 520, 400), 40, fill=col + (255,)); d.rectangle((460, 30, 520, 400), fill=col + (255,))
    for y in range(52, 390, 36): d.line((530, y, 530, y + 18), fill=(190, 170, 130, 255), width=4)
    d.text((275, 232), letra, font=F("Baloo2-ExtraBold.ttf", 330), fill=CREAM, anchor="mm")
    ff = F("Baloo2-ExtraBold.ttf", 118); lines = texto.split("\n")
    for i, l in enumerate(lines): d.text((640, 215 + (i - (len(lines) - 1) / 2) * 130), l, font=ff, fill=BROWN, anchor="lm")
    return im
V0 = S_("L05") - .1
def s_voto(T):
    z, cx, cy = lerp(1.2, 1.0, ease((T - V0) / .6)), 540, 960
    fr, x0, y0 = cam(var(sergio_var(T)), z * punch(T, V0), cx, cy)
    from PIL import ImageEnhance
    fr = ImageEnhance.Brightness(fr).enhance(.62)
    ta, tb, tc = WT("L05", "acerco") - .1, WT("L05", "hago") - .1, S_("L05") + PAL["L05"][13][1] - .15
    pop(fr, ticket("A", "Acercarme\na la puerta", TEAL), 540, 560, ta, T, -2, .35)
    pop(fr, ticket("B", "Hacer como\nque no estoy", CORAL), 540, 830, tb, T, 2, .35)
    pop(fr, tag("¡COMENTA A o B!", MUST, INK, 74, 28), 540, 1065, tc, T, -2, .3); top_tag(fr, T); return fr

ESCENAS = [(0.0, s_intro), (B1, s_puerta), (B2, s_nota), (S_("L02") - .1, s_carta1), (C2, s_radio), (S_("L03") - .1, s_quien),
           (WT("L03", "alguien") - .1, s_firma), (P0, s_pasos), (PA, s_slit), (PB, s_extremo), (V0, s_voto)]

def frame(T, fn):
    fr = fn(T); subs(fr, T); return fr

def render_escena(i):
    t0, fn = ESCENAS[i]; t1 = ESCENAS[i + 1][0] if i + 1 < len(ESCENAS) else TOTAL
    n0, n1 = round(t0 * FPS), round(t1 * FPS); out = os.path.join(TMP, f"s{i:02d}.mp4"); part = out[:-4] + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", part], stdin=subprocess.PIPE)
    pf = ESCENAS[i - 1][1] if i > 0 else None
    for n in range(n0, n1):
        T = n / FPS; fr = frame(T, fn)
        if pf and T - t0 < .08:
            fr = Image.blend(frame(T, pf).convert("RGBA"), fr, ease((T - t0) / .08))
        p.stdin.write(fr.convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(part, out)
    return i

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "frames":
        for T in map(float, sys.argv[2:]):
            fn = [f for t, f in ESCENAS if t <= T][-1]; frame(T, fn).convert("RGB").save(os.path.join(TMP, f"f_{T:06.2f}.jpg"), quality=90)
        print("TOTAL", round(TOTAL, 2), [(round(t, 2), f.__name__) for t, f in ESCENAS])
    else:
        sel = [int(x) for x in sys.argv[1:]] or list(range(len(ESCENAS)))
        with Pool(2) as pool:
            for i in pool.imap_unordered(render_escena, sel): print("escena", i, flush=True)
        print("TOTAL", round(TOTAL, 2))
