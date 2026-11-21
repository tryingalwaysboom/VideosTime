"""Papá solo — Parte 1. Escenas por código (arte.py), cortes medidos sobre la voz, cámara con zoom/punch/sacudida,
barra 'DÍA 1 de 30' y subtítulos palabra a palabra dentro de la zona segura de TikTok/Reels."""
import os, sys, json, math, wave, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from multiprocessing import Pool
import arte as A
from arte import S, W, H, s
from guion_papa1 import LINEAS

HERE = os.path.dirname(os.path.abspath(__file__))
VOZ = os.path.join(HERE, "voz1")
TMP = os.path.join(HERE, "tmp1"); os.makedirs(TMP, exist_ok=True)
FPS, OW, OH = 30, 1080, 1920
QUIEN = {l[0]: l[1] for l in LINEAS}
SUB = {l[0]: l[3] for l in LINEAS}
OFF = {"L01", "L02", "L07", "L08", "L16", "L20", "L23", "L25", "L29", "L31", "L32"}   # narración: la boca de Dani NO se mueve


# ---------------- tiempos ----------------
def _wav(lid):
    with wave.open(os.path.join(VOZ, lid + ".wav")) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        return a, w.getframerate()

DUR, ENV = {}, {}
for lid in QUIEN:
    a, sr = _wav(lid)
    DUR[lid] = len(a) / sr
    hop = sr // FPS
    rms = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a), hop)] or [0])
    ref = np.percentile(rms, 92) or 1
    e = np.clip(rms / ref, 0, 1.2)
    ENV[lid] = np.convolve(e, [.25, .5, .25], mode="same")

GAP = {"L02": .45, "L03": .25, "L07": .35, "L08": .55, "L09": .3, "L12": .35, "L13": .8, "L14": .45, "L16": .3,
       "L17": .3, "L20": .35, "L21": .55, "L22": .2, "L23": .45, "L24": .15, "L25": .2, "L26": .75, "L27": .25,
       "L28": .3, "L29": .35, "L30": 1.0, "L31": .3, "L32": .35}
TL, t = {}, .12
for lid in QUIEN:
    t += GAP.get(lid, .18) if lid != "L01" else 0
    TL[lid] = (t, t + DUR[lid]); t += DUR[lid]
TOTAL = TL["L32"][1] + .3

def S_(lid): return TL[lid][0]
def E_(lid): return TL[lid][1]

def _palabras(lid):
    """[(palabra mostrada, inicio, fin)] en tiempo de la línea. Whisper si existe; si no, reparto por letras."""
    disp = SUB[lid].split()
    js = os.path.join(VOZ, lid + ".json")
    off = json.load(open(os.path.join(VOZ, "offsets.json")))[lid] if os.path.exists(os.path.join(VOZ, "offsets.json")) else {"off": 0, "tempo": 1}
    if os.path.exists(js):
        wj = json.load(open(js))
        if wj:
            tt = [((w["inicio"] - off["off"]) / off["tempo"], (w["fin"] - off["off"]) / off["tempo"]) for w in wj]
            out = []
            for i, p in enumerate(disp):
                k = min(len(tt) - 1, round(i * (len(tt) - 1) / max(1, len(disp) - 1))) if len(tt) != len(disp) else i
                out.append((p, max(0, tt[k][0]), max(0, tt[k][1])))
            return out
    tot = sum(len(p) + 1 for p in disp); acc = 0; out = []
    for p in disp:
        a0 = acc / tot * DUR[lid]; acc += len(p) + 1
        out.append((p, a0, acc / tot * DUR[lid]))
    return out

PAL = {lid: _palabras(lid) for lid in QUIEN}

def WT(lid, palabra):
    for p, a0, _ in PAL[lid]:
        if palabra.lower() in p.lower().strip("*¿?¡!.,…"):
            return S_(lid) + a0
    return S_(lid)

def boca(voz, T):
    for lid, (a, b) in TL.items():
        if QUIEN[lid] == voz and a <= T < b and lid not in OFF:
            e = ENV[lid]; i = int((T - a) * FPS)
            return float(e[min(i, len(e) - 1)])
    return 0.0

def parpadeo(T, seed=0): return ((T * .31 + seed * .37) % 1) < .045
def ease(u): u = max(0, min(1, u)); return u * u * (3 - 2 * u)
def u_(T, t0, d): return ease((T - t0) / d)


# ---------------- fondos cacheados ----------------
_BG = {}
def bg(nombre, *args):
    k = (nombre,) + args
    if k not in _BG: _BG[k] = getattr(A, nombre)(*args)
    return _BG[k].copy()


# ---------------- personajes con estado ----------------
def dani(c, x, y, T, h=1250, **kw):
    kw.setdefault("expr", "normal")
    kw.setdefault("cerrado", parpadeo(T, 1) and kw["expr"] not in ("panico", "susto"))
    return A.persona(c, s(x), s(y), s(h), **A.DANI, boca=boca("D", T), **kw)

def vera(c, x, y, T, h=560, **kw):
    return A.persona(c, s(x), s(y), s(h), **A.VERA, boca=boca("V", T), cerrado=parpadeo(T, 2), **kw)

def hugo(c, x, y, T, h=470, **kw):
    kw.setdefault("cerrado", parpadeo(T, 3))
    return A.persona(c, s(x), s(y), s(h), **A.HUGO, boca=boca("H", T), **kw)

def mama(c, x, y, T, h=1200, **kw):
    return A.persona(c, s(x), s(y), s(h), **A.MAMA, boca=boca("M", T), cerrado=parpadeo(T, 4), **kw)

def carmen(c, x, y, T, h=1150, **kw):
    return A.persona(c, s(x), s(y), s(h), **A.CARMEN, boca=boca("C", T), cerrado=parpadeo(T, 5), **kw)

def con_bebe(c, info, T, llora=True):
    A.bebe(c, info["x"] + info["bw"] * .12, info["ty"] + info["body_h"] * .28, info["bw"] * .19, llora=llora, t=T)


def signos(c, T, x, y, n=3, txt="?", col=(255, 255, 255)):
    d = ImageDraw.Draw(c)
    f = A.font(s(110))
    for k in range(n):
        a = T * 3 + k * 2.1
        px, py = s(x) + math.cos(a) * s(150 + k * 30), s(y) + math.sin(a * .7) * s(60) - k * s(40)
        d.text((px, py), txt, font=f, fill=col, stroke_width=s(8), stroke_fill=A.OL)


def gota_sudor(c, info, T):
    d = ImageDraw.Draw(c)
    x, y, hd = info["x"] + info["head"] * .85, info["hy"] - info["head"] * .5, info["head"]
    k = (T * 1.5) % 1
    d.polygon([(x, y + k * hd * .3), (x - hd * .1, y + hd * .2 + k * hd * .3), (x + hd * .1, y + hd * .2 + k * hd * .3)], fill=(140, 200, 255))
    d.ellipse([x - hd * .1, y + hd * .12 + k * hd * .3, x + hd * .1, y + hd * .32 + k * hd * .3], fill=(140, 200, 255), outline=A.OL, width=s(3))


# ---------------- ESCENAS: devuelven (lienzo S, (zoom, cx, cy), sacudida) ----------------
def sc_hook(T):
    c = bg("recibidor", 0.0)
    d = dani(c, 540, 1800, T, expr="panico", brazos="bebe", mira=(math.sin(T * 7), 0))
    con_bebe(c, d, T)
    signos(c, T, 540, 470)
    z = 1.0 + .25 * u_(T, 0, DUR["L01"])
    sh = 1.0 if WT("L01", "hijo") - .05 < T < WT("L01", "hijo") + .4 else .15
    return c, (z, s(540), s(1080)), sh


def sc_rebobina(T):
    t0 = S_("L02") - GAP["L02"]
    u = (T - t0) / (E_("L02") - t0 + .25)
    c = bg("cocina", (7, 5))
    d = ImageDraw.Draw(c)
    ang = 5 - 5 * ease(u) - 60 * (1 - ease(u)) * math.sin(u * 9)
    A.reloj(d, s(270), s(620), s(85), (7, max(0, int(5 * (1 - ease(u * 1.2))))))
    return c, (1.9 - .3 * ease(u), s(330), s(680)), .2


def sc_puerta(T):
    c = bg("recibidor", 0.0)
    A.maleta(c, s(200), s(1820), s(300))
    m = mama(c, 330, 1830, T, expr="normal" if T < S_("L05") else "listilla", brazos="maleta", mira=(1, 0))
    expr = "normal" if T < S_("L04") else ("listilla" if T < S_("L06") else "risa")
    d = dani(c, 760, 1830, T, expr=expr, brazos="bebe", mira=(-1, 0))
    con_bebe(c, d, T, llora=False)
    hablando = "M" if (S_("L03") - .3 <= T < E_("L03") + .1 or S_("L05") - .2 <= T < E_("L05") + .1) else "D"
    tgt = (s(400), s(1000)) if hablando == "M" else (s(680), s(1000))
    z = 1.35
    return c, (z, *tgt), 0


def sc_cierra(T):
    t0 = S_("L07") - GAP["L07"]
    corte = WT("L07", "llorar") - .15
    if T < corte:
        p = 1 - u_(T, t0, .45)
        c = bg("recibidor", round(p * 10) / 10, True)
        d = dani(c, 760, 1830, T, expr="normal" if T < t0 + .6 else "susto", brazos="bebe", mira=(-1, 0))
        con_bebe(c, d, T, llora=T > t0 + .55)
        sh = .9 if t0 + .4 < T < t0 + .75 else 0
        return c, (1.15, s(540), s(1000)), sh
    c = bg("recibidor", 0.0)
    d = dani(c, 760, 1830, T, expr="panico", brazos="bebe", mira=(0, 1))
    con_bebe(c, d, T, llora=True)
    return c, (2.2 + .2 * u_(T, corte, 1.5), s(790), s(820)), .35


def sc_caos(T):
    c = bg("cocina", (7, 6))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([s(140), s(1480), s(940), s(1530)], s(16), fill=(200, 140, 90), outline=A.OL, width=s(4))
    tl = WT("L08", "leche"); tt = WT("L08", "tostada")
    # vaso de leche cayendo y charco
    ang = 90 * u_(T, tl - .2, .3)
    vaso = Image.new("RGBA", (s(120), s(170)), (0, 0, 0, 0)); vd = ImageDraw.Draw(vaso)
    vd.polygon([(s(10), 0), (s(110), 0), (s(95), s(165)), (s(25), s(165))], fill=(230, 245, 255), outline=A.OL)
    vd.rectangle([s(22), s(50), s(98), s(160)], fill=(255, 255, 255))
    vaso = vaso.rotate(-ang, expand=True, resample=Image.BICUBIC)
    c.alpha_composite(vaso, (s(700) - vaso.width // 2, s(1480) - vaso.height))
    r = s(30 + 170 * u_(T, tl, .5))
    if T > tl: d.ellipse([s(760) - r, s(1495) - r * .18, s(760) + r * 1.3, s(1495) + r * .22], fill=(255, 255, 252), outline=(220, 220, 220), width=s(3))
    # tostada quemada humeando
    d.rounded_rectangle([s(260), s(1405), s(420), s(1490)], s(30), fill=(55, 38, 30), outline=A.OL, width=s(5))
    for k in range(4):
        q = ((T - tt) * .6 + k * .25) % 1 if T > tt - .4 else 0
        if q:
            A.soft(c, lambda dd, q=q, k=k: dd.ellipse([s(290 + k * 25) - s(40) * q, s(1380) - s(500) * q - s(40), s(340 + k * 25) + s(40) * q, s(1380) - s(500) * q + s(40)], fill=(90, 90, 90, int(160 * (1 - q)))), s(14))
    dd = dani(c, 900, 1880, T, h=1300, expr="panico", brazos="bebe", mira=(-1, 1))
    con_bebe(c, dd, T)
    tgt = (s(720), s(1400)) if T < tt - .1 else (s(360), s(1360))
    return c, (1.45, *tgt), (.5 if abs(T - tl - .1) < .2 else 0)


def _cocina_familia(T, hugo_x=None, hugo_visible=True):
    c = bg("cocina", (7, 8))
    d = ImageDraw.Draw(c)
    # sillas y mesa
    for x in (230, 860):
        d.rounded_rectangle([s(x - 110), s(1250), s(x + 110), s(1300)], s(10), fill=(170, 110, 70), outline=A.OL, width=s(4))
        d.rectangle([s(x - 100), s(1300), s(x - 80), s(1700)], fill=(150, 96, 60)); d.rectangle([s(x + 80), s(1300), s(x + 100), s(1700)], fill=(150, 96, 60))
    return c


def sc_cocina(T):
    c = _cocina_familia(T)
    v = vera(c, 230, 1640, T, expr="listilla", brazos="jarras", mira=(1, -1))
    # Hugo se escabulle mientras papá y Vera discuten la corteza
    t_sale = S_("L10")
    hx = 860 + 700 * u_(T, t_sale, 2.2)
    hy = 1640 + (60 * u_(T, t_sale, .3))
    if hx < 1250:
        hugo(c, hx, hy + math.sin(T * 14) * 6 * (T > t_sale), T, expr="risa" if T > t_sale else "normal", brazos="boca" if T > t_sale else "arriba", mira=(1, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([s(-20), s(1500), s(1100), s(1560)], s(16), fill=(200, 140, 90), outline=A.OL, width=s(5))
    d.rectangle([s(60), s(1560), s(90), H], fill=(170, 110, 70)); d.rectangle([s(990), s(1560), s(1020), H], fill=(170, 110, 70))
    dd = dani(c, 560, 1900, T, h=1320, expr="normal" if T < S_("L10") else "susto", brazos="bebe", mira=(-1, 0))
    con_bebe(c, dd, T)
    if T < S_("L10"): tgt, z = (s(540), s(1150)), 1.05
    elif T < S_("L11"): tgt, z = (s(620), s(800)), 1.7
    else: tgt, z = (s(330), s(1150)), 1.55
    return c, (z, *tgt), 0


def sc_grito(T):
    c = _cocina_familia(T)
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([s(-20), s(1500), s(1100), s(1560)], s(16), fill=(200, 140, 90), outline=A.OL, width=s(5))
    if T < S_("L13") - .2:
        dd = dani(c, 560, 1900, T, h=1320, expr="normal", brazos="bebe", mira=(1, -1))
        con_bebe(c, dd, T)
        return c, (1.6 + .3 * u_(T, S_("L12"), .3), s(560), s(760)), .5
    # la silla de Hugo, vacía... y unas migas
    for k in range(7): d.ellipse([s(820 + k * 13), s(1240 + (k % 3) * 6), s(830 + k * 13), s(1250 + (k % 3) * 6)], fill=(200, 150, 80))
    vera(c, 230, 1640, T, expr="listilla", brazos="cruzados", mira=(1, 0))
    dd = dani(c, 560, 1900, T, h=1320, expr="susto", brazos="bebe", mira=(1, 0))
    con_bebe(c, dd, T, llora=False)
    p = u_(T, S_("L13"), 1.4)
    return c, (1.6, s(560 + 300 * p), s(1150 + 100 * p)), 0


def sc_perdido(T):
    c = _cocina_familia(T)
    v = vera(c, 300, 1700, T, h=620, expr="listilla", brazos="cruzados", mira=(1, 0))
    dd = dani(c, 780, 1900, T, h=1320, expr="forzada" if T >= S_("L15") else "susto", brazos="bebe", mira=(-1, 0))
    con_bebe(c, dd, T, llora=False)
    if T >= S_("L15"): gota_sudor(c, dd, T)
    if T < S_("L15") - .1:
        return c, (2.1 + .15 * u_(T, S_("L14"), 1.2), s(300), s(1240)), 0
    return c, (1.9, s(760), s(820)), 0


def sc_busca(T):
    ta, ts = WT("L16", "armario") - .1, WT("L16", "sofá") - .1
    if T < ta:
        c = bg("dormitorio")
        d = ImageDraw.Draw(c)
        A.soft(c, lambda q: q.polygon([(s(780), s(1560)), (s(80), s(1450)), (s(80), s(1690))], fill=(255, 240, 160, 150)), s(18))
        dd = dani(c, 860, 2350, T, h=1250, expr="susto", brazos="abiertos", mira=(-1, 0))
        return c, (1.2, s(540), s(1300)), 0
    if T < ts:
        c = bg("armario")
        dani(c, 540, 1950, T, h=1250, expr="panico", brazos="arriba", mira=(math.sin(T * 9), -1))
        return c, (1.25, s(540), s(1000)), .2
    c = bg("salon")
    dd = dani(c, 540, 1880, T, h=1250, expr="listilla", brazos="abiertos", mira=(1, -1))
    mx, my, _ = dd["manos"][1]
    A.galleta(c, mx, my - s(40), s(70))
    return c, (1.45, s(640), s(900)), 0


def sc_tablet(T):
    c = bg("cocina", (7, 12))
    v = vera(c, 300, 1720, T, h=640, expr="listilla" if T < S_("L19") else "risa", brazos="tablet", mira=(1, 0))
    A.tablet(c, v["x"], v["ty"] + v["body_h"] * .38, s(230), T, sonando=False)
    dd = dani(c, 760, 1900, T, h=1320, expr="panico", brazos="cabeza" if T >= S_("L18") else "bebe", mira=(-1, 0))
    if T < S_("L18"): con_bebe(c, dd, T, llora=False)
    if S_("L19") - .1 <= T:
        d = ImageDraw.Draw(c)
        k = u_(T, S_("L19") - .1, .2)
        f = A.font(s(260 * (.6 + .4 * k)))
        d.text((s(150), s(900)), "1", font=f, fill=(255, 214, 60), stroke_width=s(14), stroke_fill=A.OL)
        return c, (1.9, s(320), s(1200)), 0
    if T < S_("L18"): return c, (1.7, s(330), s(1250)), 0
    return c, (1.7, s(740), s(830)), .4


def sc_calle(T):
    c = bg("recibidor", 0.3, True)
    dd = dani(c, 900, 2000, T, h=1350, expr="susto", brazos="bebe", mira=(-1, 0))
    con_bebe(c, dd, T, llora=False)
    p = u_(T, S_("L20"), DUR["L20"] + .3)
    return c, (1.1 + .55 * p, s(540 - 40 * p), s(960)), (.6 if T > WT("L20", "abierta") else 0)


def sc_rellano(T):
    c = bg("rellano")
    cm = carmen(c, 660, 1800, T, expr="listilla", brazos="movil", mira=(-1, 0))
    mx, my, _ = cm["manos"][1]
    ImageDraw.Draw(c).rounded_rectangle([mx - s(30), my - s(80), mx + s(30), my + s(20)], s(8), fill=(40, 40, 50), outline=A.OL, width=s(4))
    if T > S_("L21") + .5:
        dd = dani(c, 250, 1880, T, h=1300, expr="forzada" if T >= S_("L22") else "susto", brazos="bebe", mira=(1, 0))
        con_bebe(c, dd, T, llora=False)
        if T >= S_("L22"): gota_sudor(c, dd, T)
    tgt = (s(640), s(900)) if T < S_("L22") else (s(330), s(900))
    return c, (1.6, *tgt), 0


def sc_bano(T):
    c = bg("bano", 0.5)
    wob = 0
    if S_("L24") <= T < E_("L24") + .3: wob = .35 * math.sin(T * 30)
    if T >= S_("L25") + .5: wob = .8 * math.sin(T * 24) * (1 if int(T * 3) % 2 else .3)
    A.cesto(c, s(640), s(1700), 1.25, wob=wob)
    p = u_(T, S_("L23"), E_("L25") - S_("L23"))
    dani(c, 60 + 220 * p, 2000, T, h=1350, expr="susto", brazos="abiertos", mira=(1, 0))
    return c, (1.3 + .4 * p, s(560), s(1250)), (.25 if abs(wob) > .5 else 0)


def sc_encontrado(T):
    c = bg("bano", 0.0)
    tp = S_("L26") - .25
    if T < S_("L27") - .1:
        A.cesto(c, s(640), s(1700), 1.25, tapa=1)
        up = u_(T, tp, .25)
        hg = hugo(c, 640, 1700 - 260 * up, T, h=520, expr="risa", brazos="arriba", calcetin=True, mira=(-1, 0))
        dd = dani(c, 200, 2000, T, h=1350, expr="susto", brazos="abiertos", mira=(1, 0))
        if T > tp:
            d = ImageDraw.Draw(c)
            for k in range(6):
                q = u_(T, tp, .8)
                a = -math.pi / 2 + (k - 2.5) * .45
                x, y = s(640) + math.cos(a) * s(420) * q, s(1300) + math.sin(a) * s(380) * q + s(300) * q * q
                d.rounded_rectangle([x - s(40), y - s(25), x + s(40), y + s(25)], s(12), fill=[(240, 90, 120), (90, 160, 230), (250, 210, 80)][k % 3], outline=A.OL, width=s(3))
        return c, (1.35, s(560), s(1200)), (.5 if tp < T < tp + .3 else 0)
    # abrazo
    A.cesto(c, s(880), s(1700), 1.0, tapa=1)
    dd = dani(c, 540, 2150, T, h=1450, expr="triste", brazos="abrazo", mira=(0, 1), cerrado=True)
    hugo(c, 540, 1950, T, h=520, expr="risa", brazos="arriba", calcetin=True, mira=(0, -1))
    return c, (1.55, s(540), s(1150)), 0


def sc_frase(T):
    c = bg("bano", 0.0)
    if T < S_("L29") - .1:
        hugo(c, 540, 1850, T, h=620, expr="normal", brazos="abajo", calcetin=True, mira=(0, -1))
        return c, (2.0 + .2 * u_(T, S_("L28"), 2), s(540), s(1300)), 0
    dd = dani(c, 540, 2000, T, h=1400, expr="triste", brazos="abajo", mira=(0, 1))
    return c, (2.2 + .25 * u_(T, S_("L29"), 2.5), s(540), s(760)), 0


def sc_llamada(T):
    c = bg("cocina", (7, 21))
    v = vera(c, 300, 1720, T, h=640, expr="susto", brazos="tablet", mira=(1, 0))
    A.tablet(c, v["x"], v["ty"] + v["body_h"] * .38, s(240), T, sonando=True)
    dd = dani(c, 770, 1900, T, h=1320, expr="susto", brazos="abajo", mira=(-1, 1))
    hugo(c, 980, 1880, T, h=470, expr="normal", calcetin=True, mira=(-1, 0))
    if T < S_("L31") - .1:
        return c, (1.5 + .3 * u_(T, S_("L30") - 1, 2), s(400), s(1260)), 0
    return c, (1.8 + .35 * u_(T, S_("L31"), DUR["L31"]), s(640), s(900)), .15


def _panel(T, lado):
    c = bg("cocina", (7, 22))
    if lado == 0:
        dd = dani(c, 330, 1900, T, h=1320, expr="triste", brazos="tablet", mira=(1, 0))
        A.tablet(c, dd["x"], dd["ty"] + dd["body_h"] * .38, s(260), T, sonando=True)
    else:
        vera(c, 590, 1720, T, h=640, expr="listilla", brazos="cruzados", mira=(1, 0))
        dd = dani(c, 830, 1900, T, h=1320, expr="listilla", brazos="boca", mira=(-1, 0))
    return c


def sc_final(T):
    return None, None, 0


ESCENAS = [
    (0.0, sc_hook), (S_("L02") - GAP["L02"], sc_rebobina), (S_("L03") - .1, sc_puerta), (S_("L07") - GAP["L07"], sc_cierra),
    (S_("L08") - .2, sc_caos), (S_("L09") - .15, sc_cocina), (S_("L12") - .1, sc_grito), (S_("L14") - .15, sc_perdido),
    (S_("L16") - .1, sc_busca), (S_("L17") - .15, sc_tablet), (S_("L20") - .15, sc_calle), (S_("L21") - .3, sc_rellano),
    (S_("L23") - .2, sc_bano), (S_("L26") - .35, sc_encontrado), (S_("L28") - .15, sc_frase), (S_("L30") - GAP["L30"], sc_llamada),
    (S_("L32") - .2, sc_final)]
SUAVES = set()   # escenas que entran sin latigazo


# ---------------- capas en 1x ----------------
_HUD = None
def hud(fr, T):
    global _HUD
    if _HUD is None:
        lay = Image.new("RGBA", (OW, 160), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.rounded_rectangle([60, 10, 1020, 130], 36, fill=(255, 255, 255, 236), outline=(52, 36, 40), width=4)
        d.text((96, 22), "PAPÁ SOLO", font=A.font(34), fill=(40, 50, 90))
        d.text((96, 60), "DÍA 1 de 30", font=A.font(50), fill=(232, 90, 70))
        d.text((440, 24), "Hasta que vuelva mamá", font=A.font(28), fill=(110, 110, 130))
        d.rounded_rectangle([440, 76, 980, 104], 14, fill=(235, 228, 220))
        _HUD = lay
    lay = _HUD.copy(); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([440, 76, 440 + 540 / 30 * min(1, .2 + T / 3), 104], 14, fill=(232, 90, 70))
    fr.alpha_composite(lay, (0, 160))   # zona segura arriba: empieza en y=170


def subtitulos(fr, T):
    for lid, (a, b) in TL.items():
        if a - .05 <= T < b + .25:
            pal = PAL[lid]; t = T - a
            # bloque de hasta 4 palabras que contiene la palabra activa
            act = max([i for i, (_, a0, _) in enumerate(pal) if a0 <= t] or [0])
            i0 = (act // 4) * 4
            grupo = pal[i0:i0 + 4]
            d = ImageDraw.Draw(fr)
            f = A.font(70)
            words = [p.strip("*") for p, *_ in grupo]
            tw = sum(d.textlength(w, font=f) for w in words) + d.textlength(" ", font=f) * (len(words) - 1)
            x = (OW - tw) / 2 - 20
            y = 1250
            for j, w in enumerate(words):
                on = (i0 + j) == act
                col = (255, 214, 60) if on else (255, 255, 255)
                yy = y - (8 if on else 0)
                d.text((x, yy), w, font=f, fill=col, stroke_width=9, stroke_fill=(25, 20, 30))
                x += d.textlength(w + " ", font=f)
            return


def final_frame(T):
    """Pantalla partida: izquierda contárselo, derecha guardar el secreto. Se ilumina la opción que se está diciendo."""
    L = _panel(T, 0); R = _panel(T, 1)
    def recorte(cv, cx):
        cw, ch = int(W / 1.4), int(H / 1.4)
        im = cv.crop((int(cx - cw / 2), int(s(1000) - ch / 2), int(cx + cw / 2), int(s(1000) + ch / 2))).convert("RGB")
        return im.resize((OW, OH), Image.BILINEAR)
    a, b = recorte(L, s(540)), recorte(R, s(540))
    fr = Image.new("RGB", (OW, OH))
    mask = Image.new("L", (OW, OH), 0)
    ImageDraw.Draw(mask).polygon([(0, 0), (600, 0), (480, OH), (0, OH)], fill=255)
    fr.paste(b, (0, 0)); fr.paste(a, (0, 0), mask)
    fr = fr.convert("RGBA")
    d = ImageDraw.Draw(fr)
    d.line([(600, 0), (480, OH)], fill=(255, 255, 255), width=14)
    tg = WT("L32", "guardamos") - .1
    on = 0 if T < tg else 1
    dim = Image.new("RGBA", (OW, OH), (0, 0, 0, 0)); dd = ImageDraw.Draw(dim)
    if on == 0: dd.polygon([(600, 0), (OW, 0), (OW, OH), (480, OH)], fill=(0, 0, 0, 120))
    else: dd.polygon([(0, 0), (600, 0), (480, OH), (0, OH)], fill=(0, 0, 0, 120))
    fr.alpha_composite(dim)
    d = ImageDraw.Draw(fr)
    for i, (txt, cx, col) in enumerate([("Contárselo\na mamá", 270, (70, 200, 140)), ("Guardar\nel secreto", 790, (240, 110, 150))]):
        k = 1.0 if i == on else .82
        f = A.font(int(64 * k))
        lines = txt.split("\n")
        y = 330
        for ln in lines:
            tw = d.textlength(ln, font=f)
            d.text((cx - tw / 2, y), ln, font=f, fill=(255, 255, 255) if i == on else (220, 220, 220), stroke_width=10, stroke_fill=col if i == on else (60, 60, 70))
            y += int(72 * k)
    return fr


def frame(T, fn):
    if fn is sc_final:
        fr = final_frame(T)
    else:
        c, (z, cx, cy), sh = fn(T)
        cw, ch = W / z, H / z
        if sh:
            cx += math.sin(T * 61) * s(14) * sh; cy += math.cos(T * 47) * s(12) * sh
        x0 = min(max(cx - cw / 2, 0), W - cw); y0 = min(max(cy - ch / 2, 0), H - ch)
        fr = c.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((OW, OH), Image.BILINEAR)
    if fn is sc_rebobina: vhs(fr, T)
    hud(fr, T)
    subtitulos(fr, T)
    return fr


def vhs(fr, T):
    lay = Image.new("RGBA", (OW, OH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for y in range(0, OH, 6): d.line([(0, y), (OW, y)], fill=(0, 0, 40, 40), width=2)
    yb = int((T * 900) % OH)
    d.rectangle([0, yb, OW, yb + 40], fill=(255, 255, 255, 50))
    fr.alpha_composite(lay)
    d = ImageDraw.Draw(fr)
    if int(T * 3) % 2 == 0:
        for k in range(2):
            x0 = 80 + k * 60
            d.polygon([(x0 + 60, 340), (x0 + 60, 420), (x0, 380)], fill=(255, 255, 255), outline=(30, 30, 30))
    d.text((80, 440), "7:00", font=A.font(110), fill=(255, 255, 255), stroke_width=8, stroke_fill=(30, 30, 30))


def latigazo(fr, k):
    """Entrada en latigazo horizontal (k: 0 inicio .. 1 asentado)."""
    if k >= 1: return fr
    dx = int((1 - ease(k)) * 420)
    im = fr.convert("RGB")
    sh = Image.new("RGB", im.size); sh.paste(im, (dx, 0)); sh.paste(im.crop((OW - dx, 0, OW, OH)), (0, 0)) if dx else None
    return sh.filter(ImageFilter.BoxBlur(int(18 * (1 - k)))).convert("RGBA") if k < .9 else sh.convert("RGBA")


def render_escena(i):
    t0, fn = ESCENAS[i]
    t1 = ESCENAS[i + 1][0] if i + 1 < len(ESCENAS) else TOTAL
    n0, n1 = round(t0 * FPS), round(t1 * FPS)
    out = os.path.join(TMP, f"s{i:02d}.mp4"); part = out[:-4] + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", part], stdin=subprocess.PIPE)
    for n in range(n0, n1):
        T = n / FPS
        fr = frame(T, fn)
        if i > 0 and fn not in SUAVES and T - t0 < .2: fr = latigazo(fr, (T - t0) / .2)
        p.stdin.write(fr.convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(part, out)
    return i


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "frames":
        for T in map(float, sys.argv[2:]):
            fn = [f for t, f in ESCENAS if t <= T][-1]
            frame(T, fn).convert("RGB").save(os.path.join(TMP, f"f_{T:06.2f}.jpg"), quality=90)
        print("TOTAL", round(TOTAL, 2))
    else:
        sel = [int(x) for x in sys.argv[1:]] or list(range(len(ESCENAS)))
        with Pool(2) as pool:
            for i in pool.imap_unordered(render_escena, sel): print("escena", i, flush=True)
        print("TOTAL", round(TOTAL, 2))
