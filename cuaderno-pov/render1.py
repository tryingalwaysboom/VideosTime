"""Monta la Parte 1 de "El cuaderno de la abuela". Reutiliza el motor del taller (subtítulos palabra a palabra,
tiempos de voz, transiciones) con escenas propias. Uso: python3 render1.py still 1 5 | scenes [i...] | info"""
import os, sys, math, json, subprocess, random
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["GUION"] = "guion_cuaderno1"; os.environ["VOZDIR"] = os.path.join(HERE, "voz1")
sys.path.insert(0, HERE); sys.path.append(os.path.join(HERE, "..", "taller-pov"))
import importlib.util
_spec = importlib.util.spec_from_file_location("R", os.path.join(HERE, "..", "taller-pov", "render.py"))
R = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(R)
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

R.LAY = os.path.join(HERE, "layers"); R.layer.cache_clear(); R.scaled.cache_clear()
TMP = os.path.join(HERE, "tmp1"); os.makedirs(TMP, exist_ok=True)
W, H, FPS = R.W, R.H, R.FPS
put, ease, clamp, back, font, mouth = R.put, R.ease, R.clamp, R.back, R.font, R.mouth
F_ANTON, F_UI, OL, YEL, WHITE = R.F_ANTON, R.F_UI, R.OL, R.YEL, R.WHITE
MF = os.path.join(HERE, "..", "mateo-pov", "fonts")
F_HAND = os.path.join(MF, "Caveat.ttf"); F_BAL = os.path.join(MF, "Baloo2-ExtraBold.ttf")
PI_ = math.pi
ORO = (255, 196, 60); ROSA = (232, 85, 109); TINTA = (52, 58, 130); CREMA = (252, 244, 226)

R.GAP.update({"F02": .2, "F03": .2, "F04": .25, "F05": .3, "F06": .25, "F07": .3, "F08": .25, "F09": .2, "F10": .2,
              "F11": .2, "F12": .3, "F13": .2, "F14": .2, "F15": .2, "F16": .2, "F17": .2, "F18": .2, "F19": .2, "F20": .3})
R.TL, R.TOTAL = R.timeline()
R.TL = {k: (a - .1, b - .1) for k, (a, b) in R.TL.items()}
R.TOTAL = R.TL["F20"][1] + .1          # corte en seco ~0,1 s tras la última palabra
R.CH = R.chunks(); TL = R.TL; TOTAL = R.TOTAL
S, E, WT = R.S, R.E, R.WT
R.NOMBRE = {"S": "SOFÍA", "A": "NOTA DE TU MAMÁ (LA ABUELA)"}
R.HIDE_LAST_CAPTION = False

def talk(lid, T): return S(lid) <= T < E(lid)
def u_(T, t0, d): return ease((T - t0) / d)

# ---------------------------------------------------------------- Sofía con boca animada
def sofia(c, kind, cx, cy, s, T, lid=None, rot=0):
    hab = lid is not None and talk(lid, T)
    put(c, f"sofia_{kind}_hab" if hab else f"sofia_{kind}", cx, cy + 400 * s, s, rot=rot)
    if hab: mouth(c, cx, cy + 60 * s, T, True, int(24 * s))
    if kind not in ("llora", "feliz") and (T % 3.9) < .12 and not rot:   # parpadeo
        d = ImageDraw.Draw(c)
        for ex in (-76, 76):
            x, y = cx + ex * s, cy - 84 * s
            d.ellipse((x - 40 * s, y - 34 * s, x + 40 * s, y + 34 * s), fill=(243, 194, 155))
            d.line((x - 34 * s, y + 4 * s, x + 34 * s, y + 4 * s), fill=OL, width=max(3, int(6 * s)))

def lagrimas(c, cx, cy, s, T):
    d = ImageDraw.Draw(c)
    for k, ex in enumerate((-78, 78)):
        for j in range(3):
            ph = ((T * 1.3) + j / 3 + k * .17) % 1
            x = cx + ex * s + 6 * math.sin(ph * 6); y = cy - 88 * s + ph * 230 * s; r = (10 + 4 * (1 - ph)) * s
            d.ellipse((x - r * .75, y - r, x + r * .75, y + r), fill=(143, 208, 255), outline=(58, 127, 191), width=3)

def bgz(name, T, t0, z0=1.0, z1=1.06, dur=7):
    """Fondo con zoom lento (Ken Burns)."""
    return R.bg(name, T, t0, z0, z1, dur)

# ---------------------------------------------------------------- papel, letras y crayola
_GR = Image.fromarray((np.random.default_rng(3).random((H, W)) * 70 + 185).astype(np.uint8))
def trazo(c, pts, w, col, alpha=255):
    """Trazo de crayola con textura de cera."""
    if len(pts) < 2: return
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    d.line(pts, fill=255, width=int(w), joint="curve")
    for p in (pts[0], pts[-1]): d.ellipse((p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2), fill=255)
    m = Image.composite(_GR, Image.new("L", (W, H), 0), m).point(lambda v: min(255, int(v * alpha / 255)))
    c.alpha_composite(Image.new("RGBA", (W, H), col + (255,)), (0, 0)) if False else None
    lay = Image.new("RGBA", (W, H), col + (0,)); lay.putalpha(m); c.alpha_composite(lay)

def s_path(cx, yt, h, wob=0.0, seed=0):
    """Puntos de una S (arriba-derecha -> abajo-izquierda) en pantalla. wob>0 = S torcida de niña."""
    rx, ry = h * .32, h / 4; pts = []
    r = random.Random(seed)
    for k in range(40):   # arco de arriba: de -25° a -270°
        a = math.radians(-25 - 245 * k / 39); pts.append((cx + rx * math.cos(a), yt + ry + ry * math.sin(a)))
    for k in range(1, 40):   # arco de abajo: de -90° a 205°
        a = math.radians(-90 + 295 * k / 39); pts.append((cx + rx * math.cos(a), yt + 3 * ry + ry * math.sin(a)))
    if wob:
        out = []
        for i, (x, y) in enumerate(pts):
            out.append((x + wob * h * (.22 * math.sin(i * .35 + seed) + .06 * r.uniform(-1, 1)) * (1 if i > 30 else .5),
                        y + wob * h * .08 * math.sin(i * .5 + 1)))
        pts = out
    return pts

def recorrido(pts, u):
    n = max(2, int(len(pts) * clamp(u))); return pts[:n]

def mano(c, tip, T, s=.5):
    """Mano de Sofía con crayola rosa: la punta cae en tip."""
    x, y = tip; jx = 1.5 * math.sin(T * 31); jy = 1.5 * math.cos(T * 27)
    # en la capa (1000x1600 lógicos), la punta está en (330,1010); el centro en (500,800)
    put(c, "sofia_mano_crayola", x + (500 - 330) * s + jx, y + (800 - 1010) * s + jy, s)

def manuscrito(c, lineas, T, t0, t1, x, y, size=64, col=TINTA, lh=84, rot=0, centro=True):
    """Texto a mano que va apareciendo letra a letra entre t0 y t1."""
    total = sum(len(l) for l in lineas); n = int(total * clamp((T - t0) / max(.01, t1 - t0)))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); f = font(F_HAND, size)
    for i, l in enumerate(lineas):
        vis = l[:max(0, n)]; n -= len(l)
        if not vis: break
        xx = x - d.textlength(l, font=f) / 2 if centro else x
        d.text((xx, y + i * lh), vis, font=f, fill=col + (255,))
    if rot: lay = lay.rotate(rot, center=(x, y), resample=Image.BICUBIC)
    c.alpha_composite(lay)

def brillos(c, T, t0, cx, cy, r0=140, col=(255, 236, 160), n=12):
    if T < t0: return
    d = ImageDraw.Draw(c); u = T - t0
    for k in range(n):
        a = k * 2 * PI_ / n + u * .8; rr = r0 + 40 * math.sin(u * 3 + k)
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a); s = 10 + 8 * abs(math.sin(u * 5 + k))
        d.polygon([(x, y - s), (x + s * .3, y - s * .3), (x + s, y), (x + s * .3, y + s * .3), (x, y + s), (x - s * .3, y + s * .3), (x - s, y), (x - s * .3, y - s * .3)], fill=col)

def polvo(c, T, n=40, seed=1):
    r = random.Random(seed); d = ImageDraw.Draw(c)
    for k in range(n):
        x = (r.uniform(0, W) + T * r.uniform(-12, 12)) % W; y = (r.uniform(200, 1400) + T * r.uniform(-20, 6)) % 1500
        a = int(90 + 90 * math.sin(T * 1.7 + k)); rr = r.uniform(2, 5)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 230, 180, max(0, a)))

def confeti(c, T, t0, n=60):
    if T < t0: return
    r = random.Random(7); d = ImageDraw.Draw(c); u = T - t0
    for k in range(n):
        x = r.uniform(80, 1000) + 40 * math.sin(u * 3 + k); y = -40 + u * r.uniform(400, 800) + r.uniform(0, 200)
        if y > 1400: continue
        col = r.choice([(232, 85, 109), (255, 196, 60), (95, 191, 106), (74, 159, 224), (184, 138, 214)])
        d.rectangle((x - 9, y - 5, x + 9, y + 5), fill=col)

def rotulo(c, T, t0, txt, cx, cy, fill=YEL, fg=OL, size=46, rot=-3):
    """Rótulo corto tipo cinta de papel que aparece con rebote (solo palabras que dice la voz)."""
    if T < t0: return
    k = R.popscale(T, t0); f = font(F_BAL, size)
    tw = ImageDraw.Draw(c).textlength(txt, font=f)
    lay = Image.new("RGBA", (int(tw + 80), size + 50), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((4, 8, lay.width - 4, lay.height - 4), 16, fill=(20, 14, 30, 120))
    d.rounded_rectangle((0, 0, lay.width - 8, lay.height - 12), 16, fill=fill, outline=OL, width=5)
    d.text(((lay.width - 8) / 2, (lay.height - 12) / 2 + 2), txt, font=f, fill=fg, anchor="mm")
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    if k < .99: lay = lay.resize((max(1, int(lay.width * k)), max(1, int(lay.height * k))))
    c.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

# ---------------------------------------------------------------- hoja de Sofía con su nombre a medias
def hoja_nombre(c, T, cx, cy, s, sof_u=1.0, rot=-4, tachon=False):
    lay = Image.new("RGBA", (int(760 * s), int(520 * s)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, lay.width - 1, lay.height - 1), int(14 * s), fill=(253, 250, 240), outline=OL, width=max(3, int(6 * s)))
    for k in range(4):
        y = (110 + k * 100) * s; d.line((30 * s, y, lay.width - 30 * s, y), fill=(160, 200, 235), width=max(2, int(4 * s)))
    c2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # SOF torcido con crayola rosa (como lo escribe una niña que no puede)
    base = [(160, 300, 4), (290, 312, 5), (410, 296, 6)]
    for i, (lx, ly, sd) in enumerate(base[:3]):
        u = clamp(sof_u * 3 - i)
        if u <= 0: continue
        X, Y = cx - 380 * s + lx * s, cy - 260 * s + ly * s
        if i == 0: pts = s_path(X, Y - 90 * s, 170 * s, .35, 2)
        elif i == 1:
            pts = [(X + 60 * s * math.cos(a) * (1 + .1 * math.sin(a * 3)), Y - 5 * s + 80 * s * math.sin(a)) for a in np.linspace(-PI_ / 2, 3 * PI_ / 2 - .3, 40)]
        else:
            pts = [(X, Y - 90 * s), (X - 4 * s, Y + 80 * s)] + [(X - 4 * s, Y - 90 * s), (X + 80 * s, Y - 100 * s)] + [(X, Y - 10 * s), (X + 60 * s, Y - 4 * s)]
        trazo(c2, recorrido(pts, u), 16 * s, ROSA)
    # huecos de la Í y la A
    for k, lx in enumerate((560, 660)):
        d.text((lx * s, 300 * s), "?", font=font(F_BAL, 120 * s), fill=(200, 200, 215), anchor="mm")
    if tachon:
        for k in range(3):
            d.line((80 * s + k * 20 * s, 380 * s, 500 * s, 230 * s + k * 30 * s), fill=ROSA + (200,), width=int(10 * s))
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A").point(lambda v: v // 3))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (int(cx - lay.width / 2 + 10), int(cy - lay.height / 2 + 14)))
    c.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))
    c2 = c2.rotate(rot, center=(cx, cy), resample=Image.BICUBIC)
    c.alpha_composite(c2)

# ================================================================ ESCENAS
def sc_llanto(T):   # F01 (segundo 0): Sofía llora, la hoja con SOF delante
    c = bgz("bg_cuarto_sofia", T, 0, 1.06, 1.0, 4).copy()
    sofia(c, "llora", 540, 700, .95, T, "F01")
    lagrimas(c, 540, 700, .95, T)
    hoja_nombre(c, T, 540, 1230, .95, 1.0, -5)
    return c

def sc_sof(T):   # F02: la hoja de cerca, el nombre a medias
    t0 = S("F02") - .15
    c = Image.new("RGBA", (W, H), (0, 0, 0, 255)); c.alpha_composite(bgz("bg_cuarto_sofia", T, t0, 1.12, 1.18, 6).filter(ImageFilter.GaussianBlur(10)))
    hoja_nombre(c, T, 540, 820, 1.35, clamp((T - WT("F02", "S,") + .1) / 1.5), -3)
    rotulo(c, T, WT("F02", "hora"), "MEDIA HORA", 300, 330, size=50, rot=-5)
    for k, w in enumerate(("S,", "O,", "F.")):
        t = WT("F02", w)
        if T >= t: rotulo(c, T, t, w[0], 330 + k * 200, 1210, fill=(255, 255, 255), size=64, rot=(-6, 4, -2)[k])
    return c

def sc_unica(T):   # F03: "las demás ya saben"
    t0 = S("F03") - .15
    c = bgz("bg_cuarto_sofia", T, t0, 1.0, 1.06, 6).copy()
    d = ImageDraw.Draw(c)
    # burbujas con los nombres de otras niñas (bien escritos) y una tachada
    for k, (nm, x, y) in enumerate((("LUCÍA", 220, 330), ("MÍA", 860, 300), ("ANA", 210, 620), ("EMMA", 880, 600))):
        tk = t0 + .3 + k * .35
        if T < tk: continue
        sc = R.popscale(T, tk)
        r = 120 * sc
        d.ellipse((x - r, y - r * .7, x + r, y + r * .7), fill=(255, 255, 255, 235), outline=OL, width=5)
        if sc > .6: d.text((x, y), nm, font=font(F_BAL, 52 * sc), fill=(60, 150, 80), anchor="mm")
    sofia(c, "triste", 540, 940, .95, T, "F03")
    if talk("F03", T) and T > WT("F03", "única"): lagrimas(c, 540, 940, .95, T)
    return c

def sc_rompe(T):   # F04: rompe la hoja y portazo
    t0 = S("F04") - .15; tr = WT("F04", "rompe"); te = WT("F04", "encierra")
    c = bgz("bg_cuarto_sofia", T, t0, 1.08, 1.12, 6).copy()
    if T < te - .2:
        sofia(c, "enojado", 540, 700, .95, T)
        if T < tr:
            hoja_nombre(c, T, 540, 1230, .9, 1.0, -4)
        else:   # dos mitades que se separan
            u = ease((T - tr) / .5)
            tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0)); hoja_nombre(tmp, T, 540, 1230, .9, 1.0, -4)
            L = tmp.crop((0, 0, 540, H)).rotate(-18 * u, center=(540, 1150), resample=Image.BICUBIC)
            Rr = tmp.crop((540, 0, W, H)).rotate(18 * u, center=(0, 1150), resample=Image.BICUBIC)
            c.alpha_composite(L, (int(-160 * u), int(120 * u))); c.alpha_composite(Rr, (540 + int(160 * u), int(120 * u)))
            rotulo(c, T, tr, "¡RRRAS!", 540, 1000, fill=(255, 255, 255), fg=ROSA, size=70)
    else:   # puerta de su cuarto que se cierra de golpe
        d = ImageDraw.Draw(c); u = ease((T - te + .2) / .35)
        d.rectangle((250, 260, 830, 1340), fill=(70, 50, 80))
        ww = int(580 * (.25 + .75 * u))
        d.rectangle((250, 260, 250 + ww, 1340), fill=(186, 130, 86), outline=OL, width=8)
        if u > .9:
            d.rectangle((300, 320, 780, 760), outline=(140, 92, 56), width=8); d.rectangle((300, 820, 780, 1280), outline=(140, 92, 56), width=8)
            d.ellipse((720, 760, 760, 800), fill=(226, 184, 74), outline=OL, width=4)
            d.rounded_rectangle((420, 420, 660, 520), 20, fill=(247, 198, 212), outline=OL, width=5)
            for k, col in enumerate(((232, 85, 109), (74, 159, 224), (95, 191, 106))):
                d.ellipse((460 + k * 60, 448, 500 + k * 60, 488), fill=col)
        if 0 < T - te < .25:   # sacudida del portazo
            c = c.rotate(1.5 * math.sin((T - te) * 60), resample=Image.BICUBIC)
    return c

def sc_desvan(T):   # F05: subes al desván, algo se cae
    t0 = S("F05") - .3; tc = WT("F05", "cae")
    c = bgz("bg_desvan", T, t0, 1.18, 1.05, 6).copy()
    polvo(c, T)
    # caja que se tambalea y suelta el cuaderno
    wob = 6 * math.sin((T - tc + .6) * 14) * math.exp(-max(0, T - tc + .6) * 1.5) if T > tc - .6 else 0
    put(c, "caja_desvan", 760, 1010, .55, rot=wob)
    if T >= tc - .1:
        u = clamp((T - tc + .1) / .45)
        y = 900 + 520 * u * u; rr = -60 * u
        put(c, "cuaderno", 640 - 120 * u, y, .32, rot=rr)
        if u >= 1: polvo(c, T * 3, 25, 9)
    # luz de la bombilla que parpadea un poco
    if (T * 3) % 2.3 < .1: R.dark(c, 60)
    return c

def sc_cuaderno(T):   # F06: el cuaderno de flores con tu nombre
    t0 = S("F06") - .15
    c = bgz("bg_desvan", T, t0, 1.25, 1.3, 6).filter(ImageFilter.GaussianBlur(6)).copy()
    R.dark(c, 70)
    put(c, "cuaderno", 540, 820, .9 + .03 * clamp((T - t0) / 4), rot=-4)
    polvo(c, T, 30, 4)
    tn = WT("F06", "nombre.")
    if T >= tn - .1:
        rotulo(c, T, tn - .1, "TU NOMBRE", 760, 1180, size=54, rot=4)
        d = ImageDraw.Draw(c); d.line((700, 1140, 600, 1010), fill=YEL, width=10); d.polygon([(600, 990), (585, 1030), (625, 1022)], fill=YEL)
    elif T >= WT("F06", "flores.") - .05:
        brillos(c, T, WT("F06", "flores."), 560, 600, 200, (255, 200, 220), 8)
    return c

def foto_infancia(k=1.0):
    """Foto vieja (sepia): tú con 5 años escribiendo en este mismo cuaderno; la mano de tu mamá te guía.
    A la abuela no se le ve la cara (canon: no se ve hasta la Parte 14), solo su manga de flores."""
    ph = Image.new("RGBA", (W, H), (236, 210, 170, 255)); d = ImageDraw.Draw(ph)
    d.rectangle((0, 1150, W, H), fill=(190, 140, 96))
    put(ph, "nina_mama", 400, 760 + 360, .9)
    put(ph, "cuaderno", 560, 1300, .5, rot=-10)
    # brazo de tu mamá entrando por la derecha, manga con flores, mano sobre la tuya
    d.polygon([(W, 900), (W, 1120), (760, 1290), (700, 1200)], fill=(150, 110, 190), outline=OL)
    for (x, y) in ((900, 1040), (980, 990), (820, 1150), (950, 1100)):
        for j in range(5):
            a = j * 2 * PI_ / 5; d.ellipse((x + 14 * math.cos(a) - 11, y + 14 * math.sin(a) - 11, x + 14 * math.cos(a) + 11, y + 14 * math.sin(a) + 11), fill=(245, 150, 180))
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(255, 210, 74))
    d.ellipse((610, 1170, 760, 1300), fill=(243, 194, 155), outline=OL, width=5)
    d.ellipse((540, 1230, 640, 1310), fill=(243, 194, 155), outline=OL, width=4)
    g = ph.convert("L"); sep = Image.merge("RGBA", (g.point(lambda v: min(255, int(v * 1.05) + 30)), g.point(lambda v: min(255, v + 10)), g.point(lambda v: int(v * .82)), Image.new("L", (W, H), 255)))
    return sep

_FOTO = {}
def sc_recuerdo(T):   # F07: es TU cuaderno; con él te enseñó a escribir TU mamá (= la abuela de Sofía)
    t0 = S("F07") - .15
    c = bgz("bg_desvan", T, t0, 1.25, 1.3, 6).filter(ImageFilter.GaussianBlur(8)).copy(); R.dark(c, 110)
    if "f" not in _FOTO: _FOTO["f"] = foto_infancia().crop((60, 360, 1020, 1500)).resize((640, 760))
    k = .92 + .05 * clamp((T - t0) / 5)
    pol = Image.new("RGBA", (700, 920), (250, 246, 236, 255)); dp = ImageDraw.Draw(pol)
    pol.alpha_composite(_FOTO["f"], (30, 30)); dp.rectangle((0, 0, 699, 919), outline=OL, width=5)
    dp.text((350, 850), "yo, con 5 años", font=font(F_HAND, 64), fill=(90, 70, 60), anchor="mm")
    pol = pol.resize((int(700 * k), int(920 * k))).rotate(4, expand=True, resample=Image.BICUBIC)
    c.alpha_composite(pol, (int(540 - pol.width / 2), int(820 - pol.height / 2)))
    if T >= WT("F07", "mamá,") - .1:
        rotulo(c, T, WT("F07", "mamá,") - .1, "TU MAMÁ = LA ABUELA DE SOFÍA", 540, 300, fill=(255, 236, 200), size=44, rot=-2)
    if T >= WT("F07", "treinta") - .1:
        rotulo(c, T, WT("F07", "treinta") - .1, "HACE 30 AÑOS", 540, 1330, size=50, rot=3)
    return c

def cuaderno_abierto(c, cx, cy, s, T, izq=None, der=None):
    """Dibuja el cuaderno abierto; izq/der son funciones que pintan sobre cada página (reciben (c, x0, y0, s))."""
    w, h = 900 * s, 640 * s
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((cx - w / 2 - 22 * s, cy - h / 2 - 16 * s, cx + w / 2 + 22 * s, cy + h / 2 + 22 * s), int(26 * s), fill=(108, 148, 120), outline=OL, width=max(4, int(8 * s)))
    for side in (-1, 1):
        x0 = cx if side > 0 else cx - w / 2
        d.rounded_rectangle((x0, cy - h / 2, x0 + w / 2, cy + h / 2), int(10 * s), fill=(250, 240, 214), outline=OL, width=max(3, int(5 * s)))
        for k in range(7):
            y = cy - h / 2 + (90 + k * 78) * s; d.line((x0 + 30 * s, y, x0 + w / 2 - 30 * s, y), fill=(190, 205, 225), width=max(2, int(3 * s)))
    d.line((cx, cy - h / 2, cx, cy + h / 2), fill=(150, 130, 100), width=max(3, int(6 * s)))
    if izq: izq(c, cx - w / 2, cy - h / 2, s)
    if der: der(c, cx, cy - h / 2, s)
    return w, h

def s_punteada(c, x0, y0, s, alpha=255):
    d = ImageDraw.Draw(c)
    for i, (x, y) in enumerate(s_path(x0 + 225 * s, y0 + 150 * s, 330 * s)):
        if i % 3 == 0: d.ellipse((x - 7 * s, y - 7 * s, x + 7 * s, y + 7 * s), fill=(60, 60, 80, alpha))

def sc_abre(T):   # F08-F10: abres; la S punteada; la nota aparece; la tinta está fresca
    t0 = S("F08") - .15
    c = bgz("bg_desvan", T, t0, 1.3, 1.36, 9).filter(ImageFilter.GaussianBlur(7)).copy(); R.dark(c, 80)
    tz = WT("F10", "tinta") - .1
    z = 1.0 + .55 * ease((T - tz) / .6) if T > tz else 1.0
    tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    def izq(cc, x0, y0, s):
        if T >= WT("F08", "S") - .1: s_punteada(cc, x0, y0, s)
    def der(cc, x0, y0, s):
        if T >= S("F09") - .05:
            manuscrito(cc, ["Si la escribes", "bien… te cuento", "un secreto."], T, S("F09"), E("F09"), x0 + 225 * s, y0 + 120 * s, int(54 * s), TINTA, int(78 * s), 3)
            if T > E("F09"): cc.alpha_composite(Image.new("RGBA", (1, 1)), (0, 0)); ImageDraw.Draw(cc).text((x0 + 330 * s, y0 + 420 * s), "— R.", font=font(F_HAND, int(54 * s)), fill=TINTA)
    cuaderno_abierto(tmp, 540, 800, 1.05, T, izq, der)
    if z > 1.001:
        cx, cy = 780, 700
        tmp = tmp.resize((int(W * z), int(H * z)), Image.BICUBIC).crop((int(cx * z - cx), int(cy * z - cy), int(cx * z - cx) + W, int(cy * z - cy) + H))
    c.alpha_composite(tmp)
    if WT("F08", "mamá…") - .1 <= T < tz:
        rotulo(c, T, WT("F08", "mamá…") - .1, "LETRA DE TU MAMÁ", 760, 380, fill=(255, 255, 255), fg=TINTA, size=42, rot=3)
    if T >= WT("F10", "fresca.") - .1:   # brillo húmedo de la tinta
        d = ImageDraw.Draw(c); ph = (T - WT("F10", "fresca.")) * 1.4 % 1
        for k in range(3):
            x = 380 + ph * 600 + k * 40; d.line((x, 500, x - 80, 900), fill=(255, 255, 255, 70), width=18)
        rotulo(c, T, WT("F10", "fresca.") - .1, "TINTA FRESCA", 540, 1200, fill=(255, 255, 255), fg=TINTA, size=56)
    elif T >= WT("F10", "niña.") - .2 and T < tz:
        rotulo(c, T, WT("F10", "niña.") - .2, "ANTES NO ESTABA", 540, 1230, size=48)
    return c

def sc_puerta(T):   # F11: Sofía se asoma
    t0 = S("F11") - .2
    c = bgz("bg_desvan", T, t0, 1.1, 1.15, 5).copy(); polvo(c, T, 30, 6)
    k = ease((T - t0) / .5)
    sofia(c, "timido", 540, 900 + 200 * (1 - k), .98, T, "F11")
    return c

def pagina_s(s):
    """Página real del libro: 'La S de sol' (sin número de página)."""
    f = os.path.join(HERE, "..", "pinti-organico", "assets", "paginas", "pagina-27.jpg")
    im = Image.open(f).convert("RGBA"); im = im.crop((0, 0, im.width, int(im.height * .965)))
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
_PS = {}
def pg(s):
    if s not in _PS: _PS[s] = pagina_s(s)
    return _PS[s]

def sc_imprime(T):   # F12: el cuaderno es muy viejo -> imprimes la hoja de la S para practicar primero -> se sientan juntas
    t0 = S("F12") - .15; tp = WT("F12", "imprimes") - .15; tj = WT("F12", "juntas") - .3
    c = bgz("bg_desvan", T, t0, 1.05, 1.1, 6).copy()
    if T < tp:   # el cuaderno viejo: hojas amarillas que se deshacen
        R.dark(c, 90)
        def izq(cc, x0, y0, s): s_punteada(cc, x0, y0, s)
        tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0)); cuaderno_abierto(tmp, 540, 800, 1.0, T, izq, None)
        d = ImageDraw.Draw(tmp)
        for k in range(14):   # migas de papel que caen
            x = 300 + (k * 53) % 520; y = 1120 + ((T - t0) * 160 + k * 37) % 260
            d.polygon([(x, y), (x + 10, y + 4), (x + 4, y + 12)], fill=(230, 210, 170))
        d.line((560, 470, 600, 620, 580, 760), fill=(150, 120, 80), width=4)   # grieta en la hoja
        c.alpha_composite(tmp)
        rotulo(c, T, WT("F12", "viejo…") - .1, "MUY VIEJO", 540, 1230, fill=(255, 255, 255), fg=(150, 90, 40), size=54)
    elif T < tj:   # la hoja sale de la impresora
        R.dark(c, 90); d = ImageDraw.Draw(c)
        d.rounded_rectangle((210, 980, 870, 1260), 30, fill=(236, 236, 242), outline=OL, width=8)
        d.rectangle((260, 1000, 820, 1030), fill=(60, 60, 70))
        u = ease((T - tp - .1) / 1.6); im = pg(.48)
        crop = im.crop((0, im.height - int(im.height * u), im.width, im.height)) if u > 0 else None
        if crop and crop.height > 2: c.alpha_composite(crop, (int(540 - im.width / 2), int(1010 - crop.height)))
        d.rounded_rectangle((210, 1030, 870, 1260), 30, fill=(236, 236, 242), outline=OL, width=8)
        d.ellipse((780, 1100, 820, 1140), fill=(95, 191, 106))
        if T >= WT("F12", "practique") - .1: rotulo(c, T, WT("F12", "practique") - .1, "PRIMERO, PRACTICAR", 540, 1330, size=50)
    else:   # en el suelo del desván: la hoja impresa delante, el cuaderno guardado al lado
        k = ease((T - tj) / .4)
        sofia(c, "neutral", 300, 900, .9, T)
        im = pg(.5).rotate(4, expand=True, resample=Image.BICUBIC)
        c.alpha_composite(im, (int(600 - im.width / 2), int(900 - im.height / 2 + 400 * (1 - k))))
        put(c, "cuaderno", 880, 1300, .25, rot=12)
    return c

def sc_escribe(T):   # F13-F14: traza la S: la primera torcida, la segunda perfecta
    t0 = S("F13") - .15
    c = Image.new("RGBA", (W, H), (107, 74, 48, 255))
    s = 1.9; im = pg(s)
    # encuadre: fila de S punteadas (en la página: S1 en x≈205, S2 en x≈283, filas y 485..560)
    px, py = 250, 520; ox, oy = 540 - px * s, 760 - py * s
    c.paste(im, (int(ox), int(oy)), im)
    def P(x, y): return (ox + x * s, oy + y * s)
    t1a, t1b = S("F13") + .3, WT("F13", "abajo.") + .3          # primera S (torcida) mientras la describe
    t2a, t2b = WT("F14", "segunda…") - .2, WT("F14", "perfecta.") + .1
    cx1, yt = P(205, 486); cx2, _ = P(283, 486); hS = 74 * s
    p1 = s_path(cx1[0] if isinstance(cx1, tuple) else cx1, yt, hS, .55, 5) if False else s_path(P(205, 0)[0], P(0, 486)[1], hS, .55, 5)
    p2 = s_path(P(283, 0)[0], P(0, 486)[1], hS)
    tip = None
    if T >= t1a:
        pts = recorrido(p1, (T - t1a) / (t1b - t1a)); trazo(c, pts, 15, ROSA); tip = pts[-1] if T < t1b + .2 else None
    if T >= t2a:
        pts = recorrido(p2, (T - t2a) / (t2b - t2a)); trazo(c, pts, 15, ROSA); tip = pts[-1] if T < t2b + .15 else tip
    if T >= WT("F14", "torcida.") - .1:
        rotulo(c, T, WT("F14", "torcida.") - .1, "TORCIDA", 300, 1200, fill=(255, 255, 255), fg=ROSA, size=48, rot=-6)
    if T >= t2b:
        rotulo(c, T, t2b, "¡PERFECTA!", 780, 1200, size=54, rot=4); brillos(c, T, t2b, P(283, 0)[0], P(0, 522)[1], 120)
    if tip: mano(c, tip, T, .62)
    elif T < t2a: mano(c, (P(205, 0)[0] - 60, P(0, 560)[1] + 40), T, .62)
    return c

def sc_salio(T):   # F15
    t0 = S("F15") - .15
    c = bgz("bg_desvan", T, t0, 1.0, 1.05, 4).copy()
    k = back((T - t0) / .4)
    sofia(c, "feliz", 540, 860 - 40 * abs(math.sin((T - t0) * 6)) * clamp(1 - (T - t0) / 2), .98, T, "F15")
    confeti(c, T, t0)
    return c

def sc_mensaje(T):   # F16-F17: escribe su S EN EL CUADERNO, encima de la punteada; pasas la página: mensaje de tu mamá
    t0 = S("F16") - .15; ta = WT("F16", "escribe") - .1; tb = WT("F16", "punteada.") + .2; tf = WT("F16", "página…")
    c = bgz("bg_desvan", T, t0, 1.3, 1.36, 9).filter(ImageFilter.GaussianBlur(7)).copy(); R.dark(c, 80)
    def S_cuaderno(x0, y0, s): return s_path(x0 + 225 * s, y0 + 150 * s, 330 * s)
    if T < tf - .1:   # escribe su S en el cuaderno, sobre la punteada
        tip = [None]
        def izq(cc, x0, y0, s):
            s_punteada(cc, x0, y0, s)
            if T >= ta:
                pts = recorrido(S_cuaderno(x0, y0, s), (T - ta) / max(.3, tb - ta)); trazo(cc, pts, 18 * s, ROSA)
                if T < tb + .1: tip[0] = pts[-1]
        cuaderno_abierto(c, 540, 800, 1.05, T, izq, None)
        rotulo(c, T, WT("F16", "cuaderno,") - .1, "AHORA, EN EL CUADERNO", 540, 330, size=46, rot=-2)
        if tip[0]: mano(c, tip[0], T, .62)
        return c
    def izq(cc, x0, y0, s):
        s_punteada(cc, x0, y0, s); trazo(cc, S_cuaderno(x0, y0, s), 18 * s, ROSA)
    def der(cc, x0, y0, s):
        if T >= S("F17") - .05:
            manuscrito(cc, ["Tu mamá también", "decía que no servía", "para escribir.", "Lloró tres tardes", "con esta misma S."],
                       T, S("F17"), E("F17") - .3, x0 + 225 * s, y0 + 70 * s, int(46 * s), TINTA, int(70 * s), 2)
    if T < tf + .5:   # la hoja dando la vuelta
        u = clamp((T - tf + .1) / .6)
        tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0)); cuaderno_abierto(tmp, 540, 800, 1.05, T, izq, None)
        d = ImageDraw.Draw(tmp); xr = 540 + 472 * math.cos(u * PI_)
        d.polygon([(540, 464), (xr, 464 - 40 * math.sin(u * PI_)), (xr, 1136 + 40 * math.sin(u * PI_)), (540, 1136)], fill=(244, 232, 204), outline=OL)
        c.alpha_composite(tmp)
    else:
        cuaderno_abierto(c, 540, 800, 1.05, T, izq, der)
        if T >= S("F17") - .05: rotulo(c, T, S("F17") - .05, "LETRA DE TU MAMÁ", 760, 360, fill=(255, 255, 255), fg=TINTA, size=42, rot=3)
        if T >= WT("F17", "S."): rotulo(c, T, WT("F17", "S.") - .1, "TÚ TAMBIÉN LLORASTE", 540, 1230, size=50)
    return c

def sc_dorada(T):   # F18: no te acordabas; letra dorada C; palabra secreta C _ _ _ _
    t0 = S("F18") - .15; tg = WT("F18", "dorada:") - .1
    c = bgz("bg_desvan", T, t0, 1.3, 1.36, 9).filter(ImageFilter.GaussianBlur(8)).copy(); R.dark(c, 110)
    cuaderno_abierto(c, 540, 760, 1.0, T)
    d = ImageDraw.Draw(c)
    if T >= tg:
        k = back((T - tg) / .5); glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(glow)
        dg.ellipse((540 - 260 * k, 760 - 260 * k, 540 + 260 * k, 760 + 260 * k), fill=(255, 200, 80, 140)); c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(50)))
        d.text((540, 760), "C", font=font(F_BAL, int(330 * k) + 1), fill=ORO, anchor="mm", stroke_width=10, stroke_fill=(140, 90, 20))
        brillos(c, T, tg, 540, 760, 220)
    ts = WT("F18", "palabra") - .1
    if T >= ts:   # casillas de la palabra secreta
        u = ease((T - ts) / .5)
        for k in range(5):
            x = 540 + (k - 2) * 150; y = 1210 + 60 * (1 - u)
            d.rounded_rectangle((x - 62, y - 76, x + 62, y + 76), 18, fill=(40, 28, 60, int(230 * u)), outline=ORO, width=6)
            d.text((x, y), "C" if k == 0 else "?", font=font(F_BAL, 96), fill=ORO if k == 0 else (130, 110, 160), anchor="mm")
        rotulo(c, T, ts, "PALABRA SECRETA", 540, 1060, fill=ORO, size=48, rot=0)
    return c

def sc_pegada(T):   # F19: la página siguiente está pegada; asoma una nota con tu nombre
    t0 = S("F19") - .15; tn = WT("F19", "nota,") - .1
    c = bgz("bg_desvan", T, t0, 1.3, 1.36, 9).filter(ImageFilter.GaussianBlur(7)).copy(); R.dark(c, 90)
    cuaderno_abierto(c, 540, 820, 1.05, T)
    d = ImageDraw.Draw(c)
    # esquina que Sofía intenta levantar y no se despega
    tug = abs(math.sin((T - t0) * 7)) * 30 * clamp(1 - max(0, T - tn) / .5)
    d.polygon([(1012, 1136), (1012 - 120, 1136), (1012, 1136 - 120 - tug)], fill=(232, 220, 190), outline=OL)
    if T >= WT("F19", "pegada.") - .1: rotulo(c, T, WT("F19", "pegada.") - .1, "PEGADA", 860, 430, fill=(255, 255, 255), fg=ROSA, size=52, rot=6)
    if T >= tn:   # la nota asoma por el borde
        u = ease((T - tn) / .8)
        lay = Image.new("RGBA", (420, 230), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        dl.rounded_rectangle((0, 0, 419, 229), 12, fill=(255, 240, 160), outline=OL, width=5)
        dl.text((210, 80), "Para:", font=font(F_HAND, 64), fill=TINTA, anchor="mm")
        dl.line((70, 160, 350, 160), fill=TINTA, width=4)
        dl.text((210, 145), "Andrea", font=font(F_HAND, 74), fill=(194, 58, 90), anchor="mm")
        lay = lay.rotate(8, expand=True, resample=Image.BICUBIC); lay = lay.resize((int(lay.width * 1.3), int(lay.height * 1.3)))
        c.alpha_composite(lay, (int(1040 - 520 * u), int(1060 - 120 * u)))
        brillos(c, T, tn + .5, 860, 1000, 150, (255, 240, 170), 8)
    mano(c, (1000, 1110 - tug), T, .55)
    return c

# ---------------------------------------------------------------- final: dilema
RAYO = [(600, 0), (560, 520), (612, 560), (522, 1100), (578, 1132), (480, H)]
def _opcion(d, cx, cy, letra, txt, mas, menos, col, k):
    if k <= 0: return
    r = int(70 * k)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col, outline=WHITE, width=7)
    d.text((cx, cy + 2), letra, font=font(F_ANTON, int(90 * k)), fill=WHITE, anchor="mm")
    f = font(F_BAL, 60)
    for i, l in enumerate(txt): d.text((cx, cy + 135 + i * 68), l, font=f, fill=WHITE, anchor="mm", stroke_width=6, stroke_fill=OL)
    ff = font(F_UI, 38)
    d.text((cx, cy + 290), "+ " + mas, font=ff, fill=(160, 240, 170), anchor="mm", stroke_width=4, stroke_fill=OL)
    d.text((cx, cy + 345), "– " + menos, font=ff, fill=(255, 170, 170), anchor="mm", stroke_width=4, stroke_fill=OL)

def sc_final(T):   # F20
    t0 = S("F20") - .2; ta = WT("F20", "sola") - .2; tb = WT("F20", "juntas") - .2
    izq = Image.new("RGBA", (W, H), (36, 30, 70, 255)); put(izq, "bg_desvan", 300, 960, 1.0)
    R.dark(izq, 120)
    put(izq, "cuaderno", 300, 760, .42, rot=-8)
    dz = ImageDraw.Draw(izq); dz.ellipse((420, 380, 480, 440), fill=(255, 244, 200))   # luna: de noche, tú sola
    der = Image.new("RGBA", (W, H), (255, 220, 170, 255)); put(der, "bg_cuarto_sofia", 780, 960, 1.0)
    sofia(der, "feliz", 800, 760, .86, T); put(der, "cuaderno", 820, 1180, .28, rot=8)
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon([(0, 0)] + RAYO[::-1][:0] + RAYO + [(0, H)], fill=255)
    c = der.copy(); c.paste(izq, (0, 0), mask)
    d = ImageDraw.Draw(c); d.line(RAYO, fill=WHITE, width=14); d.line(RAYO, fill=ORO, width=6)
    d.text((540, 300), "¿QUÉ HARÍAS TÚ?", font=font(F_ANTON, 92), fill=WHITE, anchor="mm", stroke_width=10, stroke_fill=OL)
    _opcion(d, 270, 1000, "A", ["La lees tú", "sola"], "sabes qué dice", "Sofía queda fuera", (110, 90, 200), back((T - ta) / .35) if T >= ta else 0)
    _opcion(d, 810, 1000, "B", ["La abren", "juntas mañana"], "lo viven juntas", "una noche de dudas", ROSA, back((T - tb) / .35) if T >= tb else 0)
    # palabra secreta abajo del título
    for k in range(5):
        x = 540 + (k - 2) * 86; y = 430
        d.rounded_rectangle((x - 34, y - 42, x + 34, y + 42), 10, fill=(40, 28, 60), outline=ORO, width=4)
        d.text((x, y), "C" if k == 0 else "?", font=font(F_BAL, 52), fill=ORO if k == 0 else (130, 110, 160), anchor="mm")
    return c

# ---------------------------------------------------------------- etiqueta de la serie (arriba, zona segura)
def etiqueta_serie(c, T):
    d = ImageDraw.Draw(c); f = font(F_BAL, 34); txt = "EL CUADERNO DE LA ABUELA · PARTE 1"
    tw = d.textlength(txt, font=f)
    d.rounded_rectangle((540 - tw / 2 - 26, 176, 540 + tw / 2 + 26, 236), 18, fill=(250, 240, 214, 235), outline=OL, width=4)
    d.text((540, 207), txt, font=f, fill=(90, 60, 110), anchor="mm")

SCENES = [
    (0, sc_llanto), (S("F02") - .15, sc_sof), (S("F03") - .15, sc_unica), (S("F04") - .15, sc_rompe),
    (S("F05") - .3, sc_desvan), (S("F06") - .15, sc_cuaderno), (S("F07") - .15, sc_recuerdo), (S("F08") - .15, sc_abre),
    (S("F11") - .2, sc_puerta), (S("F12") - .15, sc_imprime), (S("F13") - .15, sc_escribe), (S("F15") - .15, sc_salio),
    (S("F16") - .15, sc_mensaje), (S("F18") - .15, sc_dorada), (S("F19") - .15, sc_pegada), (S("F20") - .2, sc_final),
]
IMPACTS = [WT("F04", "rompe"), WT("F04", "encierra"), WT("F05", "cae"), WT("F10", "fresca."), WT("F15", "salió!"), WT("F18", "dorada:")]
SUAVES = {S("F07") - .15, S("F08") - .15, S("F16") - .15}

TW = .22
def frame(T):
    idx = max(i for i, (t, f) in enumerate(SCENES) if T >= t)
    t0, fn = SCENES[idx]
    c = fn(T)
    u = (T - t0) / TW
    if idx > 0 and u < 1 and t0 not in SUAVES:   # whip-pan
        e = ease(u); prev = SCENES[idx - 1][1](T)
        k = int(2 + 22 * math.sin(PI_ * u))
        cv = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        cv.alpha_composite(R.hblur(prev, k), (int(-W * e), 0)); cv.alpha_composite(R.hblur(c, k), (int(W * (1 - e)), 0))
        c = cv
    elif idx > 0 and (T - t0) < .4 and t0 in SUAVES:
        prev = SCENES[idx - 1][1](T); c = Image.blend(prev, c, ease((T - t0) / .4))
    punch = sum(.025 * math.exp(-(T - ch[0]) * 9) for ch in R.CH if 0 <= T - ch[0] < .5)
    zz = 1 + punch + .02 * ((T - t0) / 6 % 1)
    if zz > 1.002:
        cc = c.resize((int(W * zz), int(H * zz)), Image.BILINEAR)
        ox = (cc.width - W) / 2 + 6 * math.sin(T * .7); oy = (cc.height - H) / 2 + 5 * math.cos(T * .5)
        c = cc.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    amp = sum(12 * math.exp(-(T - ti) * 7) for ti in IMPACTS if 0 <= T - ti < .7)
    if amp > .6:
        cc = c.resize((int(W * 1.04), int(H * 1.04)), Image.BILINEAR)
        ox = (cc.width - W) / 2 + amp * math.sin(T * 95); oy = (cc.height - H) / 2 + amp * math.cos(T * 71)
        c = cc.crop((int(ox), int(oy), int(ox) + W, int(oy) + H))
    c.alpha_composite(R.VIG)
    c.alpha_composite(R.grains()[int(T * 24) % 4])
    if T < S("F20") - .2: etiqueta_serie(c, T)
    R.draw_caption(c, T)
    return c.convert("RGB")

def render_scene(i, out):
    t0 = SCENES[i][0]; t1 = SCENES[i + 1][0] if i + 1 < len(SCENES) else TOTAL
    f0, f1 = round(t0 * FPS), round(t1 * FPS)
    tmp = out[:-4] + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-crf", "17", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in range(f0, f1): p.stdin.write(frame(f / FPS).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0: os.replace(tmp, out)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "still":
        for t in sys.argv[2:]: frame(float(t)).save(os.path.join(TMP, f"f_{float(t):06.2f}.jpg"), quality=86)
    elif cmd == "info":
        print(json.dumps({k: [round(a, 2), round(b, 2)] for k, (a, b) in TL.items()}), round(TOTAL, 2))
        print([round(t, 2) for t, f in SCENES])
    elif cmd == "scenes":
        from multiprocessing import Pool
        ids = [int(x) for x in sys.argv[2:]] or list(range(len(SCENES)))
        with Pool(int(os.environ.get("JOBS", "3"))) as pool:
            pool.starmap(render_scene, [(i, os.path.join(TMP, f"s{i:02d}.mp4")) for i in ids])
