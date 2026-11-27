"""Arte 100% nuevo de la serie pt-BR (Lara y el Papai Noel): personajes, manos, fondos y objetos dibujados en código con PIL."""
import os, math, random
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "..", "mateo-pov", "fonts")
F_BAL = os.path.join(FD, "Baloo2-ExtraBold.ttf"); F_AND = os.path.join(FD, "Andika-Bold.ttf"); F_HAND = os.path.join(FD, "Caveat.ttf")
F_ANTON = os.path.join(FD, "Anton-Regular.ttf"); PB = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
from PIL import ImageFont
@lru_cache(None)
def font(p, s): return ImageFont.truetype(p, max(1, int(s)))

PIEL = (246, 200, 160); PIEL_S = (222, 164, 124); OUT = (120, 70, 52)
ROJO = (214, 48, 49); VERDE = (30, 112, 78); CREMA = (252, 245, 232); OURO = (255, 205, 70); ROSA = (244, 126, 158)
MARROM = (92, 58, 40); AZUL = (62, 124, 214)

def ss(w, h, k=2): return Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
def down(im, k=2): return im.resize((im.width // k, im.height // k), Image.LANCZOS)

# ------------------------------------------------------------------ personajes (busto)
def bust(kind, expr="neutral", mo=0):
    """kind: 'lara' | 'caio'. expr: neutral|shout|angry|sad|smile|focus|laugh|hope. mo: 0 cerrada, 1 media, 2 abierta."""
    return _bust(kind, expr, mo)

@lru_cache(256)
def _bust(kind, expr, mo):
    K = 2; W, H = 800, 940; im = ss(W, H, K); d = ImageDraw.Draw(im)
    k = lambda *v: tuple(int(x * K) for x in v)
    lara = kind == "lara"
    cx, cy, R = 400, 400, (232 if lara else 244)
    cloth = (240, 110, 150) if lara else (52, 112, 205); cloth2 = (206, 78, 120) if lara else (36, 84, 168)
    hair = (110, 66, 44) if lara else (52, 38, 32); hair2 = (140, 88, 58) if lara else (80, 60, 50)
    # cuerpo
    if lara:
        d.ellipse(k(150, 700, 650, 1000), fill=cloth2 + (255,))      # capucha detrás
    d.rounded_rectangle(k(90, 740, 710, 1100), 150 * K, fill=cloth + (255,))
    d.pieslice(k(285, 650, 515, 830), 0, 180, fill=PIEL_S + (255,)) if not lara else None
    d.rectangle(k(335, 600, 465, 740), fill=PIEL_S + (255,))
    if lara:
        d.pieslice(k(250, 690, 550, 850), 0, 180, fill=cloth2 + (255,))
        d.line(k(360, 770, 350, 880), fill=CREMA + (255,), width=9 * K); d.line(k(440, 770, 450, 880), fill=CREMA + (255,), width=9 * K)
        d.ellipse(k(342, 872, 358, 892), fill=CREMA + (255,)); d.ellipse(k(442, 872, 458, 892), fill=CREMA + (255,))
    else:
        d.pieslice(k(300, 700, 500, 800), 0, 180, fill=PIEL_S + (255,)); d.arc(k(300, 690, 500, 800), 0, 180, fill=cloth2 + (255,), width=12 * K)
        d.rounded_rectangle(k(245, 905, 555, 925), 8 * K, fill=(255, 255, 255, 0))
    # pelo trasero / coletas
    if lara:
        for sx in (-1, 1):
            px = cx + sx * 255; d.ellipse(k(px - 75, 360, px + 75, 640), fill=hair + (255,), outline=MARROM + (255,), width=5 * K)
            d.ellipse(k(px - 30, 400, px + 30, 440), fill=hair2 + (255,))
    # orejas
    for sx in (-1, 1):
        d.ellipse(k(cx + sx * R - 40, cy - 12, cx + sx * R + 40, cy + 78), fill=PIEL + (255,), outline=OUT + (255,), width=5 * K)
    # cabeza
    d.ellipse(k(cx - R, cy - R + 20, cx + R, cy + R + 36), fill=PIEL + (255,), outline=OUT + (255,), width=6 * K)
    # pelo frontal
    top = cy - R + 20
    if lara:
        d.pieslice(k(cx - R - 6, top - 14, cx + R + 6, cy + 150), 180, 360, fill=hair + (255,), outline=MARROM + (255,), width=5 * K)
        d.pieslice(k(cx - 190, top + 38, cx + 40, cy - 30), 180, 360, fill=hair2 + (255,))   # flequillo
        d.pieslice(k(cx - 10, top + 30, cx + 190, cy - 60), 180, 360, fill=hair + (255,))
        for sx in (-1, 1):
            px = cx + sx * 232; d.ellipse(k(px - 26, 392, px + 26, 444), fill=ROJO + (255,), outline=(150, 30, 30, 255), width=4 * K)
    else:
        d.pieslice(k(cx - R - 4, top - 10, cx + R + 4, cy + 90), 180, 360, fill=hair + (255,), outline=(30, 22, 20, 255), width=5 * K)
        d.pieslice(k(cx - R + 30, top + 6, cx + 70, cy - 10), 180, 360, fill=hair2 + (255,))
        d.polygon([k(cx + 10, top - 6)[:2], k(cx - 10, top - 76)[:2], k(cx + 44, top - 20)[:2], k(cx + 70, top - 70)[:2], k(cx + 78, top)[:2]], fill=hair + (255,))   # remolino
    # mejillas
    cheek = (255, 150, 150, 170)
    d.ellipse(k(cx - 190, cy + 105, cx - 100, cy + 160), fill=cheek); d.ellipse(k(cx + 100, cy + 105, cx + 190, cy + 160), fill=cheek)
    # cejas y ojos
    ey = cy + 62; ex = 100
    brow = {"angry": (14, 0), "shout": (10, -8), "sad": (-16, 6), "hope": (-10, 0), "neutral": (0, 0), "smile": (0, -6), "focus": (8, 6), "laugh": (-4, -10)}[expr]
    for sx in (-1, 1):
        bx = cx + sx * ex; a, lift = brow
        d.line(k(bx - 52, ey - 68 - lift + sx * a * -1, bx + 52, ey - 68 - lift + sx * a), fill=MARROM + (255,), width=14 * K) if False else None
        y0 = ey - 74 - lift; yin = y0 + a; yout = y0 - a      # a>0: ceja baja hacia dentro (enfado); a<0: sube hacia dentro (triste)
        xin, xout = bx - sx * 38, bx + sx * 52
        d.line(k(xin, yin, xout, yout), fill=MARROM + (255,), width=15 * K)
        if expr in ("smile", "laugh"):
            d.arc(k(bx - 44, ey - 36, bx + 44, ey + 34), 200, 340, fill=(60, 40, 40, 255), width=13 * K)
        elif expr == "focus":
            d.line(k(bx - 38, ey, bx + 38, ey + 2), fill=(60, 40, 40, 255), width=14 * K)
        else:
            sz = 1.0 if expr != "angry" else .85
            d.ellipse(k(bx - 40, ey - 46 * sz, bx + 40, ey + 44 * sz), fill=(255, 255, 255, 255), outline=(60, 40, 40, 255), width=4 * K)
            ox = -sx * 6 if expr == "hope" else 0; oy = 8 if expr == "sad" else (-4 if expr == "hope" else 2)
            d.ellipse(k(bx - 24 + ox, ey - 26 + oy, bx + 24 + ox, ey + 28 + oy), fill=(86, 52, 34, 255)); d.ellipse(k(bx - 12 + ox, ey - 12 + oy, bx + 12 + ox, ey + 14 + oy), fill=(22, 14, 12, 255))
            d.ellipse(k(bx - 14 + ox, ey - 22 + oy, bx - 2 + ox, ey - 10 + oy), fill=(255, 255, 255, 255))
            if expr in ("sad",): d.ellipse(k(bx - 12, ey + 46, bx + 8, ey + 84), fill=(150, 205, 250, 230))     # lágrima
    # nariz
    d.arc(k(cx - 18, cy + 110, cx + 22, cy + 150), 20, 160, fill=OUT + (255,), width=6 * K)
    # boca
    my = cy + 190
    if mo == 0:
        if expr in ("smile", "laugh", "hope"): d.arc(k(cx - 62, my - 40, cx + 62, my + 30), 20, 160, fill=(150, 50, 60, 255), width=9 * K)
        elif expr in ("sad",): d.arc(k(cx - 50, my - 6, cx + 50, my + 56), 200, 340, fill=(150, 50, 60, 255), width=9 * K)
        elif expr == "focus": d.line(k(cx - 40, my, cx + 40, my - 6), fill=(150, 50, 60, 255), width=9 * K)
        else: d.line(k(cx - 38, my, cx + 38, my), fill=(150, 50, 60, 255), width=9 * K)
    else:
        w = 56 if mo == 1 else 70; h = 26 if mo == 1 else 64
        d.ellipse(k(cx - w, my - 14, cx + w, my - 14 + h * 1.1), fill=(112, 26, 40, 255), outline=(90, 20, 30, 255), width=5 * K)
        d.ellipse(k(cx - w * .55, my - 14 + h * .5, cx + w * .55, my - 14 + h * 1.05), fill=(235, 110, 120, 255))
        if mo == 2 and expr in ("shout", "laugh", "angry"): d.rectangle(k(cx - w * .7, my - 12, cx + w * .7, my + 6), fill=(255, 255, 255, 255))
    if expr == "focus":   # lengua fuera
        d.ellipse(k(cx + 8, my - 2, cx + 68, my + 50), fill=(235, 100, 115, 255), outline=(150, 50, 60, 255), width=4 * K)
    return down(im)

# ------------------------------------------------------------------ mano anatómica (estructura de datos + 2 capas)
HAND = {  # mano derecha, vista dorso, muñeca en (0,0), arriba = -y. Palma = pentágono irregular con eminencia tenar.
    "palma": [(-118, 0), (118, 0), (128, -150), (104, -250), (-88, -292), (-128, -150)],
    "dedos": {   # base, ángulo base (0=arriba, + = derecha), longitudes de falange
        "indice": ((-80, -285), -5, (120, 86, 66)),
        "medio": ((-12, -298), 0, (136, 96, 72)),
        "anular": ((52, -284), 4, (124, 88, 66)),
        "menique": ((104, -245), 10, (92, 62, 48)),
    },
    "pulgar": ((-104, -40), -40, (118, 98)),     # nace bajo, cerca de la muñeca, 35-45º hacia fuera, 2 falanges
}
def _fk(base, a0, lens, curls, fs=None):
    pts = [base]; a = a0; x, y = base
    for i, (l, c) in enumerate(zip(lens, curls)):
        a += c; l = l * (fs[i] if fs else 1)
        x += l * math.sin(math.radians(a)); y -= l * math.cos(math.radians(a)); pts.append((x, y))
    return pts

POSES = {
    "abierta": {"indice": ([0, 0, 0], None), "medio": ([0, 0, 0], None), "anular": ([0, 0, 0], None), "menique": ([0, 0, 0], None), "pulgar": ([-8, -8], None)},
    "pinza": {"indice": ([-6, 22, 34], [1, .8, .7]), "medio": ([42, 58, 40], [.7, .5, .45]), "anular": ([50, 60, 40], [.62, .46, .4]), "menique": ([56, 60, 40], [.6, .44, .36]),
              "pulgar": ([62, 22], [1, .85])},
    "apunta": {"indice": ([0, 0, 0], None), "medio": ([52, 58, 40], [.62, .46, .4]), "anular": ([54, 60, 40], [.6, .44, .38]), "menique": ([58, 60, 40], [.56, .42, .34]),
               "pulgar": ([48, 10], [.9, .8])},
}
@lru_cache(16)
def hand(pose="pinza", tool=None, sleeve=ROJO):
    K = 2; W, Hh = 760, 1500; ox, oy = 380, 1020          # muñeca
    P = POSES[pose]; chains = {}
    for n, (b, a0, ls) in HAND["dedos"].items():
        cu, fs = P[n]; chains[n] = _fk(b, a0, ls, cu, fs)
    b, a0, ls = HAND["pulgar"]; cu, fs = P["pulgar"]; chains["pulgar"] = _fk(b, a0, ls, cu, fs)
    rad = {"indice": (34, 27), "medio": (35, 28), "anular": (33, 26), "menique": (28, 22), "pulgar": (40, 30)}
    # capa 1: esqueleto/articulaciones
    sk = Image.new("L", (W * K, Hh * K), 0); sd = ImageDraw.Draw(sk)
    mask = Image.new("L", (W * K, Hh * K), 0); md = ImageDraw.Draw(mask)
    P2 = lambda p: ((ox + p[0]) * K, (oy + p[1]) * K)
    md.polygon([P2(p) for p in HAND["palma"]], fill=255)
    md.polygon([P2((-100, 20)), P2((100, 20)), P2((120, 900)), P2((-120, 900))], fill=255)        # antebrazo
    for n, ch in chains.items():
        r0, r1 = rad[n]
        for i in range(len(ch) - 1):
            (x0, y0), (x1, y1) = ch[i], ch[i + 1]; steps = max(2, int(math.hypot(x1 - x0, y1 - y0) / 3))
            for s in range(steps + 1):
                u = s / steps; g = (i + u) / (len(ch) - 1); r = (r0 + (r1 - r0) * g) * (1.0 if i == 0 else .94)
                x = x0 + (x1 - x0) * u; y = y0 + (y1 - y0) * u; cxp, cyp = P2((x, y))
                md.ellipse((cxp - r * K, cyp - r * K, cxp + r * K, cyp + r * K), fill=255)
        for p in ch: sd.ellipse((P2(p)[0] - 9 * K, P2(p)[1] - 9 * K, P2(p)[0] + 9 * K, P2(p)[1] + 9 * K), fill=255)
    # capa 2: contorno orgánico suave (sin trazo negro)
    mask = mask.filter(ImageFilter.GaussianBlur(7 * K)).point(lambda v: 255 if v > 118 else 0).filter(ImageFilter.GaussianBlur(1.4 * K))
    sh = ImageChops.offset(mask, 10 * K, 14 * K); sh = ImageChops.subtract(mask, sh).filter(ImageFilter.GaussianBlur(12 * K))   # sombra suave
    img = Image.new("RGBA", mask.size, (0, 0, 0, 0)); skin = Image.new("RGBA", mask.size, PIEL + (255,))
    img.paste(skin, (0, 0), mask)
    dark = Image.new("RGBA", mask.size, (205, 140, 105, 255)); img.paste(dark, (0, 0), ImageChops.multiply(sh, mask).point(lambda v: min(255, v * 2)))
    hl = ImageChops.subtract(mask, ImageChops.offset(mask, -9 * K, -12 * K)).filter(ImageFilter.GaussianBlur(10 * K))
    img.paste(Image.new("RGBA", mask.size, (255, 226, 200, 255)), (0, 0), ImageChops.multiply(hl, mask).point(lambda v: min(255, v)))
    d = ImageDraw.Draw(img)
    # manga
    d.polygon([P2((-122, 640)), P2((122, 640)), P2((132, 1010)), P2((-132, 1010))], fill=sleeve + (255,))
    d.rounded_rectangle((P2((-128, 600))[0], P2((-128, 600))[1], P2((128, 660))[0], P2((128, 660))[1]), 14 * K, fill=tuple(int(c * .85) for c in sleeve) + (255,))
    # nudillos (arcos) y uñas
    for n in ("indice", "medio", "anular", "menique"):
        bx, by = HAND["dedos"][n][0]; px, py = P2((bx, by + 10)); d.arc((px - 26 * K, py - 14 * K, px + 26 * K, py + 22 * K), 200, 340, fill=(214, 156, 122, 255), width=3 * K)
        tip = chains[n][-1]; tx, ty = P2(tip); d.ellipse((tx - 14 * K, ty - 12 * K, tx + 14 * K, ty + 12 * K), fill=(250, 214, 200, 255))
    tx, ty = P2(chains["pulgar"][-1]); d.ellipse((tx - 16 * K, ty - 14 * K, tx + 16 * K, ty + 14 * K), fill=(250, 214, 200, 255))
    res = down(img.crop((0, 0, W * K, Hh * K)))
    meta = {"pinch": ((chains["indice"][-1][0] + chains["pulgar"][-1][0]) / 2 + ox, (chains["indice"][-1][1] + chains["pulgar"][-1][1]) / 2 + oy),
            "indice": (chains["indice"][-1][0] + ox, chains["indice"][-1][1] + oy)}
    return res, meta

# ------------------------------------------------------------------ fondos (1296x2304, para zoom/paneo)
BW, BH = 1296, 2304
def _grad(w, h, c0, c1):
    g = Image.linear_gradient("L").resize((w, h)); return Image.composite(Image.new("RGB", (w, h), c1), Image.new("RGB", (w, h), c0), g)

def _blur_shadow(im, box, rad=18, alpha=70, off=(0, 10)):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((box[0] + off[0], box[1] + off[1], box[2] + off[0], box[3] + off[1]), 20, fill=(40, 20, 10, alpha))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(rad)))

def _tree(d, x, y, s=1.0):
    for i, (w, h, col) in enumerate([(340, 250, (28, 110, 70)), (270, 230, (36, 128, 82)), (200, 210, (44, 146, 94))]):
        yy = y - i * 190 * s
        d.polygon([(x - w * s / 2, yy), (x + w * s / 2, yy), (x, yy - h * s)], fill=col)
    d.rectangle((x - 34 * s, y, x + 34 * s, y + 90 * s), fill=(110, 70, 40))
    star = [(x + 38 * s * math.sin(i * math.pi / 5) * (1 if i % 2 == 0 else .45), (y - 3 * 190 * s - 190 * s) - 38 * s * math.cos(i * math.pi / 5) * (1 if i % 2 == 0 else .45)) for i in range(10)]
    d.polygon(star, fill=OURO)
    rnd = random.Random(4)
    for i in range(14):
        yy = y - rnd.random() * 520 * s; half = (340 * s / 2) * (1 - (y - yy) / (600 * s)) * .7
        px = x + rnd.uniform(-half, half); col = rnd.choice([ROJO, OURO, (90, 160, 255), (255, 120, 180)])
        d.ellipse((px - 14 * s, yy - 14 * s, px + 14 * s, yy + 14 * s), fill=col)

def _lights(d, y0, amp, n=22, w=BW):
    rnd = random.Random(2); pts = []
    for i in range(n + 1):
        x = i * w / n; y = y0 + amp * math.sin(i / n * math.pi * 3)
        pts.append((x, y))
    d.line(pts, fill=(40, 70, 50), width=5)
    for i, (x, y) in enumerate(pts):
        col = [ROJO, OURO, (90, 190, 120), (90, 160, 255)][i % 4]
        d.ellipse((x - 17, y + 2, x + 17, y + 44), fill=col); d.ellipse((x - 9, y + 8, x + 3, y + 22), fill=(255, 255, 255))

@lru_cache(8)
def bg_sala(parede=False):
    im = _grad(BW, BH, (255, 244, 226), (246, 226, 200)).convert("RGBA"); d = ImageDraw.Draw(im)
    # papel de parede: listras suaves + rodapé
    for x in range(0, BW, 96): d.rectangle((x, 0, x + 44, 1500), fill=(255, 240, 216))
    d.rectangle((0, 1500, BW, 1560), fill=(232, 200, 170)); d.rectangle((0, 1560, BW, BH), fill=(186, 134, 92))
    for i in range(0, BW, 180): d.line((i, 1560, i - 260 + (i // 180) * 20, BH), fill=(160, 112, 76), width=4)
    for y in range(1640, BH, 130): d.line((0, y, BW, y), fill=(168, 118, 80), width=3)
    # janela (direita)
    d.rounded_rectangle((870, 360, 1220, 900), 20, fill=(150, 205, 240), outline=(255, 255, 255), width=18)
    d.line((1045, 360, 1045, 900), fill=(255, 255, 255), width=14); d.line((870, 630, 1220, 630), fill=(255, 255, 255), width=14)
    for sx, sy in ((920, 440), (1110, 500), (960, 740), (1140, 760)): d.ellipse((sx, sy, sx + 22, sy + 22), fill=(255, 255, 255))
    # árvore (esquerda), luzes, tapete
    _tree(d, 170, 1540, 1.0)
    _lights(d, 140, 34)
    d.ellipse((220, 1700, 1180, 2150), fill=(196, 52, 56)); d.ellipse((300, 1760, 1100, 2090), fill=(222, 92, 84))
    d.rounded_rectangle((90, 1130, 360, 1200), 10, fill=(130, 90, 60))                   # prateleira com quadros
    for i, c in enumerate([(244, 190, 80), (120, 180, 230), (240, 140, 160)]): d.rectangle((110 + i * 80, 1060, 170 + i * 80, 1130), fill=c)
    if parede:   # frase na parede, giz de cera vermelho torto
        txt = "PAPA NOEL"; f = font(F_AND, 112); x = 250
        for i, ch in enumerate(txt):
            if ch == " ": x += 70; continue
            wd = d.textlength(ch, font=f); lay = Image.new("RGBA", (300, 300), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            ld.text((150, 150), ch, font=f, fill=(222, 50, 46, 255), anchor="mm", stroke_width=3, stroke_fill=(190, 40, 40, 255))
            lay = lay.rotate(random.Random(i).uniform(-9, 9), resample=Image.BICUBIC)
            im.alpha_composite(lay, (int(x - 40), 700 + int(18 * math.sin(i * 1.3)) - 40 - 0)); x += wd + 14
    return im.convert("RGB")

@lru_cache(8)
def bg_cozinha(noite=False):
    im = _grad(BW, BH, (214, 238, 226), (190, 224, 208)).convert("RGBA"); d = ImageDraw.Draw(im)
    for y in range(0, 1500, 110):
        for x in range(0, BW, 220): d.rectangle((x + (110 if (y // 110) % 2 else 0), y, x + 214 + (110 if (y // 110) % 2 else 0), y + 104), fill=(228, 246, 238))
    d.rectangle((0, 1500, BW, BH), fill=(172, 126, 90))
    for y in range(1560, BH, 120): d.line((0, y, BW, y), fill=(150, 108, 76), width=3)
    # geladeira grande
    box = (250, 220, 1050, 1900); _blur_shadow(im, box, 26, 90, (14, 18))
    d.rounded_rectangle(box, 56, fill=(250, 250, 246), outline=(205, 210, 205), width=8)
    d.line((250, 820, 1050, 820), fill=(205, 210, 205), width=10)
    d.rounded_rectangle((968, 400, 996, 720), 12, fill=(170, 176, 180)); d.rounded_rectangle((968, 900, 996, 1240), 12, fill=(170, 176, 180))
    d.rectangle((300, 260, 1000, 290), fill=(255, 255, 255))
    # ímãs e desenhos de criança
    rnd = random.Random(8)
    for (x, y, c) in ((330, 960, (240, 190, 80)), (640, 1500, (120, 180, 230)), (330, 1500, (244, 140, 170))):
        d.rectangle((x, y, x + 200, y + 150), fill=(255, 255, 255), outline=(220, 220, 220), width=3); d.ellipse((x + 40, y + 30, x + 150, y + 120), fill=c)
        d.ellipse((x + 90, y - 14, x + 112, y + 8), fill=ROJO)
    for (x, y, c) in ((820, 1000, ROJO), (820, 1120, VERDE)): d.rounded_rectangle((x, y, x + 120, y + 80), 14, fill=c)
    # bancada e janela
    d.rounded_rectangle((-60, 1180, 250, 1560), 20, fill=(196, 150, 110)); d.rectangle((-60, 1160, 250, 1210), fill=(240, 236, 228))
    d.rounded_rectangle((1090, 400, 1280, 880), 16, fill=(40, 52, 110) if noite else (160, 210, 240), outline=(255, 255, 255), width=14)
    if noite:
        for sx, sy in ((1130, 470), (1220, 560), (1150, 700), (1210, 800)): d.ellipse((sx, sy, sx + 12, sy + 12), fill=(255, 240, 180))
        d.ellipse((1140, 430, 1180, 470), fill=(255, 245, 200))
    _lights(d, 90, 28, 18)
    out = im.convert("RGB")
    if noite: out = ImageChops.multiply(out, Image.new("RGB", out.size, (122, 134, 210)))
    return out

@lru_cache(4)
def bg_corredor():
    im = _grad(BW, BH, (70, 58, 92), (46, 38, 64)).convert("RGBA"); d = ImageDraw.Draw(im)
    d.rectangle((0, 1560, BW, BH), fill=(76, 56, 58))
    # porta entreaberta com luz saindo
    d.rectangle((300, 300, 1000, 1700), fill=(20, 16, 28)); d.polygon([(560, 330), (980, 330), (980, 1660), (560, 1660)], fill=(255, 226, 150))
    d.rectangle((300, 300, 560, 1700), fill=(130, 88, 60)); d.rectangle((318, 330, 542, 960), outline=(104, 68, 46), width=8); d.rectangle((318, 1000, 542, 1620), outline=(104, 68, 46), width=8)
    d.ellipse((500, 1020, 540, 1060), fill=OURO)
    d.rectangle((280, 280, 1020, 320), fill=(96, 62, 44))
    return im.convert("RGB")

def cam(bgim, T, t0, z0=1.25, z1=1.45, fx0=.5, fx1=.5, fy0=.5, fy1=.5, dur=3.0):
    u = max(0., min(1., (T - t0) / dur)); u = u * u * (3 - 2 * u) if False else u
    z = z0 + (z1 - z0) * u; fx = fx0 + (fx1 - fx0) * u; fy = fy0 + (fy1 - fy0) * u
    w, h = BW / z * 1.0, BH / z * 1.0
    w, h = (h * 1080 / 1920, h) if w / h > 1080 / 1920 else (w, w * 1920 / 1080)
    x0 = (bgim.width - w) * fx; y0 = (bgim.height - h) * fy
    return bgim.resize((1080, 1920), Image.BILINEAR, box=(x0, y0, x0 + w, y0 + h))

# ------------------------------------------------------------------ objetos
def crayon_text(d, xy, text, size, col=(222, 50, 46), jitter=5, flipE=False, seed=0, n=None, anchor="lm", gap=4):
    """Escribe letra a letra con temblor de giz de cera. n = cuántas letras visibles. Devuelve posición del final."""
    f = font(F_AND, size); x, y = xy; rnd = random.Random(seed); vis = 0; last = (x, y)
    for i, ch in enumerate(text):
        wd = d.textlength(ch, font=f) + gap
        if ch != " " and (n is None or vis < n):
            dy = rnd.uniform(-jitter, jitter)
            if ch == "E" and flipE:
                lay = Image.new("RGBA", (int(size * 1.4), int(size * 1.6)), (0, 0, 0, 0)); ImageDraw.Draw(lay).text((lay.width / 2, lay.height / 2), "E", font=f, fill=col + (255,), anchor="mm")
                lay = lay.transpose(Image.FLIP_LEFT_RIGHT); d._image.alpha_composite(lay, (int(x - lay.width / 2 + wd / 2), int(y + dy - lay.height / 2)))
            else:
                d.text((x, y + dy), ch, font=f, fill=col + (255,), anchor=anchor, stroke_width=2, stroke_fill=col + (255,))
            last = (x + wd, y)
        if ch != " ": vis += 1
        x += wd if ch != " " else size * .36
    return last

def paper(texto="", n=None, flipE=False, w=980, h=1100, seed=1, lines=True, erased_i=False):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    _blur_shadow(im, (30, 30, w - 30, h - 30), 22, 80, (10, 16))
    d.rounded_rectangle((30, 30, w - 30, h - 30), 10, fill=(255, 254, 248)); d._image = im
    if lines:
        for y in range(180, h - 80, 74): d.line((60, y, w - 60, y), fill=(196, 214, 238), width=3)
        d.line((120, 40, 120, h - 40), fill=(244, 170, 170), width=3)
    last = crayon_text(d, (140, 420), texto, 122, flipE=flipE, seed=seed, n=n) if texto else (150, 420)
    return im, last

def comb(w=420, h=520):
    im = ss(w, h); d = ImageDraw.Draw(im); K = 2
    k = lambda *v: tuple(int(x * K) for x in v)
    d.rounded_rectangle(k(60, 30, 130, 490), 30 * K, fill=(255, 170, 60, 255), outline=(190, 110, 20, 255), width=6 * K)
    for y in (70, 230, 390): d.rounded_rectangle(k(100, y, 380, y + 66), 30 * K, fill=(255, 170, 60, 255), outline=(190, 110, 20, 255), width=6 * K)
    return down(im)

def estrela(d, cx, cy, r, fill):
    pts = [(cx + r * math.sin(i * math.pi / 5) * (1 if i % 2 == 0 else .45), cy - r * math.cos(i * math.pi / 5) * (1 if i % 2 == 0 else .45)) for i in range(10)]
    d.polygon(pts, fill=fill)

def telefone(w=760, h=1240, nome="Tia Bia", pulso=0.0):
    K = 2; im = ss(w, h); d = ImageDraw.Draw(im); k = lambda *v: tuple(int(x * K) for x in v)
    d.rounded_rectangle(k(0, 0, w, h), 90 * K, fill=(22, 22, 30, 255)); d.rounded_rectangle(k(22, 22, w - 22, h - 22), 72 * K, fill=(24, 94, 76, 255))
    d.rounded_rectangle(k(w / 2 - 80, 44, w / 2 + 80, 66), 11 * K, fill=(10, 10, 16, 255))
    for i, r in enumerate((250, 300, 350)):
        a = int(110 * (1 - ((pulso + i / 3) % 1))); rr = 150 + (pulso + i / 3) % 1 * 220
        d.ellipse(k(w / 2 - rr, 470 - rr, w / 2 + rr, 470 + rr), outline=(255, 255, 255, a), width=6 * K)
    # avatar da tia: rosto, cabelo cacheado, óculos
    cx, cy = w / 2, 470
    d.ellipse(k(cx - 150, cy - 160, cx + 150, cy + 140), fill=(96, 58, 40, 255)); d.ellipse(k(cx - 112, cy - 112, cx + 112, cy + 124), fill=(198, 134, 98, 255))
    for sx in (-1, 1):
        d.ellipse(k(cx + sx * 50 - 34, cy - 24, cx + sx * 50 + 34, cy + 36), outline=(40, 30, 30, 255), width=6 * K, fill=(255, 255, 255, 120))
        d.ellipse(k(cx + sx * 50 - 10, cy - 4, cx + sx * 50 + 10, cy + 18), fill=(40, 26, 20, 255))
    d.line(k(cx - 16, cy + 6, cx + 16, cy + 6), fill=(40, 30, 30, 255), width=5 * K); d.arc(k(cx - 44, cy + 50, cx + 44, cy + 100), 20, 160, fill=(150, 50, 60, 255), width=7 * K)
    d.text(k(w / 2, 790), nome, font=font(PB, 86 * K), fill=(255, 255, 255, 255), anchor="mm")
    d.text(k(w / 2, 880), "chamada de voz", font=font(PB, 38 * K), fill=(205, 240, 225, 255), anchor="mm")
    d.ellipse(k(w / 2 - 70, 1030, w / 2 + 70, 1170), fill=(222, 60, 60, 255)); d.line(k(w / 2 - 28, 1100, w / 2 + 28, 1100), fill=(255, 255, 255, 255), width=12 * K)
    return down(im)

def bilhete(n_i=True, w=640, h=520, apagando=0.0):
    """recado na geladeira. n_i: mostra o I. apagando 0..1: o I vai sumindo (borracha)."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d._image = im
    _blur_shadow(im, (20, 20, w - 20, h - 20), 14, 90, (6, 10))
    d.rectangle((20, 20, w - 20, h - 20), fill=(255, 254, 246)); d.rectangle((20, 20, w - 20, 56), fill=(250, 232, 190))
    f = font(F_AND, 118); x = 70; rnd = random.Random(3); I_pos = None
    for i, ch in enumerate("PAPAI"):
        wd = d.textlength(ch, font=f) + 4; dy = rnd.uniform(-5, 5)
        if ch == "I" and i == 4:
            I_pos = (x, 190 + dy)
            if n_i and apagando < 1:
                lay = Image.new("RGBA", (90, 160), (0, 0, 0, 0)); ImageDraw.Draw(lay).text((45, 80), "I", font=f, fill=(222, 50, 46, int(255 * (1 - apagando))), anchor="mm")
                im.alpha_composite(lay, (int(x - 45 + wd / 2), int(190 + dy - 80)))
            if apagando > 0: d.ellipse((x - 4, 170, x + wd + 6, 250), fill=(244, 238, 230, int(150 * min(1, apagando * 2)))) if False else None
        else: d.text((x, 190 + dy), ch, font=f, fill=(222, 50, 46, 255), anchor="lm", stroke_width=2, stroke_fill=(222, 50, 46, 255))
        x += wd
    x = 70
    for i, ch in enumerate("NOEL"):
        wd = d.textlength(ch, font=f) + 4; d.text((x, 340 + rnd.uniform(-5, 5)), ch, font=f, fill=(222, 50, 46, 255), anchor="lm", stroke_width=2, stroke_fill=(222, 50, 46, 255)); x += wd
    return im

def ima(cx, cy, r=34, col=ROJO):
    return (cx, cy, r, col)
