"""Papá solo 30 días — arte 2D (PIL, supersampling 2x)."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math

S = 2
W, H = 1080 * S, 1920 * S
FONT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FONT_B = "/usr/share/fonts/truetype/google-fonts/Poppins-ExtraBold.ttf"


def f(size, bold=True):
    try:
        return ImageFont.truetype(FONT_B if bold else FONT, size * S)
    except OSError:
        return ImageFont.truetype(FONT, size * S)


def grad(w, h, top, bot):
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    return im


def shadow(im, box, r=40, op=90):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse(box, fill=(40, 20, 10, op))
    sh = sh.filter(ImageFilter.GaussianBlur(r))
    im.alpha_composite(sh)


# ---------- fondo: cocina ----------
def cocina():
    im = grad(W, H, (255, 236, 205), (250, 214, 176)).convert("RGBA")
    d = ImageDraw.Draw(im)
    s = S
    # azulejos pared
    for y in range(300 * s, 1100 * s, 90 * s):
        for x in range(0, W, 90 * s):
            d.rectangle([x + 3 * s, y + 3 * s, x + 87 * s, y + 87 * s], fill=(246, 226, 196))
    # ventana con amanecer
    wx, wy, ww, wh = 600 * s, 330 * s, 380 * s, 420 * s
    sky = grad(ww, wh, (255, 190, 140), (255, 236, 190))
    im.paste(sky, (wx, wy))
    d.ellipse([wx + 220 * s, wy + 230 * s, wx + 320 * s, wy + 330 * s], fill=(255, 245, 210))
    for i, c in enumerate([(170, 200, 230), (150, 185, 220)]):
        d.rectangle([wx, wy + 300 * s + i * 40 * s, wx + ww, wy + wh], fill=c)
    d.rectangle([wx - 18 * s, wy - 18 * s, wx + ww + 18 * s, wy + wh + 18 * s], outline=(255, 255, 255), width=22 * s)
    d.line([wx + ww // 2, wy, wx + ww // 2, wy + wh], fill=(255, 255, 255), width=14 * s)
    d.line([wx, wy + wh // 2, wx + ww, wy + wh // 2], fill=(255, 255, 255), width=14 * s)
    # cortinas
    for cx in (wx - 70 * s, wx + ww + 10 * s):
        d.rounded_rectangle([cx, wy - 60 * s, cx + 60 * s, wy + wh + 40 * s], 30 * s, fill=(232, 110, 90))
    # estantería con tarros
    d.rounded_rectangle([60 * s, 420 * s, 480 * s, 445 * s], 8 * s, fill=(170, 110, 70))
    for i, (c, hh) in enumerate([((120, 180, 140), 90), ((240, 190, 80), 70), ((200, 120, 160), 100), ((110, 160, 210), 80)]):
        x = 90 * s + i * 95 * s
        d.rounded_rectangle([x, (420 - hh) * s, x + 70 * s, 420 * s], 14 * s, fill=c)
        d.rounded_rectangle([x + 8 * s, (420 - hh - 14) * s, x + 62 * s, (420 - hh + 4) * s], 6 * s, fill=(150, 100, 60))
    # reloj 7:05
    cx, cy = 270 * s, 620 * s
    d.ellipse([cx - 85 * s, cy - 85 * s, cx + 85 * s, cy + 85 * s], fill=(255, 255, 255), outline=(60, 60, 80), width=10 * s)
    for k in range(12):
        a = k / 12 * 2 * math.pi
        d.ellipse([cx + 66 * s * math.sin(a) - 5 * s, cy - 66 * s * math.cos(a) - 5 * s, cx + 66 * s * math.sin(a) + 5 * s, cy - 66 * s * math.cos(a) + 5 * s], fill=(60, 60, 80))
    d.line([cx, cy, cx + 40 * s * math.sin(math.radians(212)), cy - 40 * s * math.cos(math.radians(212))], fill=(60, 60, 80), width=10 * s)
    d.line([cx, cy, cx + 62 * s * math.sin(math.radians(30)), cy - 62 * s * math.cos(math.radians(30))], fill=(220, 70, 60), width=6 * s)
    # encimera y muebles
    d.rectangle([0, 1100 * s, W, 1150 * s], fill=(240, 240, 235))
    d.rectangle([0, 1150 * s, W, 1560 * s], fill=(120, 170, 160))
    for x in range(0, W, 270 * s):
        d.rounded_rectangle([x + 14 * s, 1170 * s, x + 256 * s, 1540 * s], 16 * s, outline=(100, 150, 140), width=6 * s)
        d.rounded_rectangle([x + 115 * s, 1200 * s, x + 155 * s, 1215 * s], 6 * s, fill=(230, 220, 200))
    # suelo
    d.rectangle([0, 1560 * s, W, H], fill=(205, 150, 110))
    for x in range(-W, W * 2, 140 * s):
        d.line([x, 1560 * s, x + 300 * s, H], fill=(190, 135, 98), width=4 * s)
    return im


# ---------- personajes ----------
def ojos(d, cx, cy, r, mira=(0, 0), susto=False, s=S):
    for dx in (-1, 1):
        ex = cx + dx * r * 1.9
        rr = r * (1.25 if susto else 1)
        d.ellipse([ex - rr, cy - rr * 1.15, ex + rr, cy + rr * 1.15], fill=(255, 255, 255), outline=(40, 30, 30), width=max(2, int(r * .18)))
        pr = rr * .55
        px, py = ex + mira[0] * rr * .35, cy + mira[1] * rr * .35
        d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(50, 35, 30))
        d.ellipse([px - pr * .35 + pr * .3, py - pr * .7, px + pr * .3 + pr * .1, py - pr * .1], fill=(255, 255, 255))


def persona(im, x, y, h, piel, pelo, camisa, pantalon, tipo="adulto", expr="normal",
            brazos="abajo", pelo_estilo="corto", mira=(0, 0), extra=None):
    """x,y = pies (centro). h = altura total en px (ya en escala S)."""
    d = ImageDraw.Draw(im)
    shadow(im, [x - h * .22, y - h * .03, x + h * .22, y + h * .03], r=int(h * .03))
    nino = tipo != "adulto"
    head = h * (.115 if not nino else .2)
    body_h = h * (.34 if not nino else .30)
    leg_h = h - head * 2 - body_h if not nino else h - head * 1.9 - body_h
    bw = h * (.27 if not nino else .32)
    lw = max(4, int(h * .012))
    ol = (60, 40, 35)
    # piernas
    ly = y - leg_h
    for dx in (-1, 1):
        d.rounded_rectangle([x + dx * bw * .22 - bw * .14, ly - 10, x + dx * bw * .22 + bw * .14, y - h * .02], int(bw * .1), fill=pantalon, outline=ol, width=lw)
        d.rounded_rectangle([x + dx * bw * .22 - bw * .2, y - h * .045, x + dx * bw * .22 + bw * .2 + dx * bw * .05, y], int(h * .02), fill=(70, 70, 90) if not nino else (240, 90, 90), outline=ol, width=lw)
    # torso
    ty = ly - body_h
    d.rounded_rectangle([x - bw / 2, ty, x + bw / 2, ly + 10], int(bw * .3), fill=camisa, outline=ol, width=lw)
    if extra == "dino":
        d.ellipse([x - bw * .18, ty + body_h * .3, x + bw * .18, ty + body_h * .62], fill=(120, 200, 110), outline=ol, width=lw // 2)
    if extra == "estrella":
        cx, cy, r = x, ty + body_h * .45, bw * .17
        pts = []
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            rr = r if k % 2 == 0 else r * .45
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d.polygon(pts, fill=(255, 220, 90), outline=ol)
    # brazos
    aw = bw * .2
    sh_y = ty + body_h * .12
    for dx in (-1, 1):
        sx = x + dx * bw * .45
        if brazos == "arriba":
            ex, ey = sx + dx * bw * .45, sh_y - body_h * .7
        elif brazos == "jarras":
            ex, ey = sx + dx * bw * .2, sh_y + body_h * .55
        elif brazos == "cruzados":
            ex, ey = x - dx * bw * .2, sh_y + body_h * .45
        elif brazos == "bebe" and dx == -1:
            ex, ey = x + bw * .05, sh_y + body_h * .62
        elif brazos == "bebe":
            ex, ey = x + bw * .15, sh_y + body_h * .38
        elif brazos == "tablet" :
            ex, ey = x + dx * bw * .18, sh_y + body_h * .42
        else:
            ex, ey = sx + dx * bw * .12, sh_y + body_h * .85
        d.line([sx, sh_y, ex, ey], fill=ol, width=int(aw + lw * 2))
        d.line([sx, sh_y, ex, ey], fill=camisa, width=int(aw))
        d.ellipse([ex - aw * .7, ey - aw * .7, ex + aw * .7, ey + aw * .7], fill=piel, outline=ol, width=lw)
    # cuello y cabeza
    hy = ty - head * .95
    d.rectangle([x - head * .25, ty - head * .25, x + head * .25, ty + 6], fill=piel)
    if pelo_estilo == "largo":
        d.rounded_rectangle([x - head * 1.08, hy - head * .2, x + head * 1.08, hy + head * 1.55], int(head * .6), fill=pelo, outline=ol, width=lw)
    if pelo_estilo == "coletas":
        for dx in (-1, 1):
            d.ellipse([x + dx * head * 1.05 - head * .42, hy + head * .1, x + dx * head * 1.05 + head * .42, hy + head * .95], fill=pelo, outline=ol, width=lw)
    d.ellipse([x - head, hy - head, x + head, hy + head], fill=piel, outline=ol, width=lw)
    # orejas
    for dx in (-1, 1):
        d.ellipse([x + dx * head * .98 - head * .16, hy - head * .05, x + dx * head * .98 + head * .16, hy + head * .3], fill=piel, outline=ol, width=lw)
    # pelo
    if pelo_estilo in ("corto", "coletas", "largo", "rizos"):
        d.chord([x - head * 1.04, hy - head * 1.08, x + head * 1.04, hy + head * .55], 180, 360, fill=pelo, outline=ol, width=lw)
        if pelo_estilo == "rizos":
            for k in range(7):
                a = math.pi + k * math.pi / 6
                cx, cy = x + head * .95 * math.cos(a), hy - head * .15 + head * .9 * math.sin(a)
                d.ellipse([cx - head * .3, cy - head * .3, cx + head * .3, cy + head * .3], fill=pelo, outline=ol, width=lw)
        else:
            d.pieslice([x - head * .9, hy - head * .75, x + head * .2, hy + head * .05], 180, 270, fill=pelo)
    if pelo_estilo == "corto":
        d.polygon([(x - head * .2, hy - head * .95), (x + head * .1, hy - head * 1.25), (x + head * .25, hy - head * .9)], fill=pelo, outline=ol)
    # mejillas
    for dx in (-1, 1):
        d.ellipse([x + dx * head * .55 - head * .16, hy + head * .25, x + dx * head * .55 + head * .16, hy + head * .42], fill=(250, 150, 140))
    # ojos
    er = head * (.17 if not nino else .2)
    ojos(d, x, hy + head * .02, er, mira=mira, susto=expr in ("susto", "panico"))
    # cejas
    for dx in (-1, 1):
        ex = x + dx * er * 1.9
        if expr in ("susto", "panico"):
            d.arc([ex - er * 1.1, hy - er * 2.6, ex + er * 1.1, hy - er * .9], 200, 340, fill=ol, width=lw)
        elif expr in ("enfado", "listilla"):
            d.line([ex - dx * er, hy - er * 1.8, ex + dx * er, hy - er * 1.3], fill=ol, width=lw)
        else:
            d.arc([ex - er, hy - er * 2.2, ex + er, hy - er * 1.1], 200, 340, fill=ol, width=lw)
    # boca
    my = hy + head * .5
    if expr == "risa":
        d.chord([x - head * .32, my - head * .18, x + head * .32, my + head * .3], 0, 180, fill=(170, 50, 60), outline=ol, width=lw)
    elif expr in ("susto", "panico"):
        d.ellipse([x - head * .14, my - head * .08, x + head * .14, my + head * .22], fill=(120, 40, 50), outline=ol, width=lw)
    elif expr == "listilla":
        d.arc([x - head * .2, my - head * .15, x + head * .3, my + head * .1], 10, 150, fill=ol, width=lw)
    elif expr == "llora":
        d.chord([x - head * .3, my - head * .05, x + head * .3, my + head * .35], 180, 360, fill=(170, 50, 60), outline=ol, width=lw)
    else:
        d.arc([x - head * .22, my - head * .18, x + head * .22, my + head * .1], 20, 160, fill=ol, width=lw)
    return dict(x=x, hy=hy, head=head, ty=ty, body_h=body_h, bw=bw)


def bebe(im, x, y, r, expr="llora"):
    d = ImageDraw.Draw(im)
    ol = (60, 40, 35)
    lw = max(3, int(r * .06))
    d.ellipse([x - r * 1.1, y, x + r * 1.1, y + r * 1.6], fill=(170, 215, 245), outline=ol, width=lw)
    d.ellipse([x - r, y - r * 1.6, x + r, y + r * .3], fill=(255, 214, 180), outline=ol, width=lw)
    hy = y - r * .65
    d.arc([x - r * .3, hy - r * 1.05, x + r * .1, hy - r * .65], 180, 360, fill=ol, width=lw)
    if expr == "llora":
        for dx in (-1, 1):
            ex = x + dx * r * .38
            d.arc([ex - r * .18, hy - r * .1, ex + r * .18, hy + r * .12], 200, 340, fill=ol, width=lw)
            d.ellipse([ex - r * .07, hy + r * .12, ex + r * .07, hy + r * .32], fill=(120, 190, 255))
        d.ellipse([x - r * .25, hy + r * .3, x + r * .25, hy + r * .7], fill=(170, 50, 60), outline=ol, width=lw)
    else:
        for dx in (-1, 1):
            ex = x + dx * r * .38
            d.ellipse([ex - r * .1, hy - r * .05, ex + r * .1, hy + r * .15], fill=ol)
        d.arc([x - r * .2, hy + r * .25, x + r * .2, hy + r * .5], 20, 160, fill=ol, width=lw)


def tostada(im, x, y, w, quemada=True):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([x - w / 2, y - w * .45, x + w / 2, y + w * .45], int(w * .25), fill=(60, 40, 30) if quemada else (230, 170, 90), outline=(40, 25, 20), width=6)
    if quemada:
        for k in range(3):
            sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
            ImageDraw.Draw(sh).ellipse([x - w * .2 + k * w * .15, y - w * (1.2 + k * .4), x + k * w * .15, y - w * (.8 + k * .4)], fill=(120, 120, 120, 110))
            im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))


def hud(im, dia=1, de=30):
    """Barra superior (zona segura: deja ~120px arriba)."""
    d = ImageDraw.Draw(im)
    s = S
    x0, y0, x1, y1 = 60 * s, 130 * s, 1020 * s, 250 * s
    pan = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(pan).rounded_rectangle([x0, y0, x1, y1], 40 * s, fill=(255, 255, 255, 235))
    im.alpha_composite(pan)
    d.text((x0 + 40 * s, y0 + 16 * s), "PAPÁ SOLO", font=f(30), fill=(40, 50, 90))
    d.text((x0 + 40 * s, y0 + 58 * s), f"DÍA {dia} de {de}", font=f(40), fill=(232, 90, 70))
    # barra progreso
    bx0, bx1, by = x0 + 400 * s, x1 - 40 * s, y0 + 75 * s
    d.rounded_rectangle([bx0, by - 14 * s, bx1, by + 14 * s], 14 * s, fill=(235, 228, 220))
    d.rounded_rectangle([bx0, by - 14 * s, bx0 + (bx1 - bx0) * dia / de, by + 14 * s], 14 * s, fill=(232, 90, 70))
    d.text((bx0, y0 + 14 * s), "Hasta que vuelva mamá", font=f(24, False), fill=(110, 110, 130))


def subtitulo(im, palabras, activa, y=1380):
    d = ImageDraw.Draw(im)
    fnt = f(66)
    txt = " ".join(palabras)
    tw = d.textlength(txt, font=fnt)
    x = (W - tw) / 2
    for i, p in enumerate(palabras):
        pw = d.textlength(p, font=fnt)
        col = (255, 214, 60) if i == activa else (255, 255, 255)
        d.text((x, y * S), p, font=fnt, fill=col, stroke_width=9 * S, stroke_fill=(25, 20, 30))
        x += pw + d.textlength(" ", font=fnt)


PIEL = (255, 210, 175)
DANI = dict(piel=PIEL, pelo=(70, 45, 30), camisa=(90, 130, 200), pantalon=(60, 70, 100), pelo_estilo="corto")
MAMA = dict(piel=PIEL, pelo=(140, 70, 40), camisa=(240, 120, 110), pantalon=(60, 60, 90), pelo_estilo="largo")
VERA = dict(piel=PIEL, pelo=(100, 55, 30), camisa=(160, 110, 210), pantalon=(80, 80, 140), pelo_estilo="coletas", tipo="nino", extra="estrella")
HUGO = dict(piel=PIEL, pelo=(230, 170, 80), camisa=(250, 200, 70), pantalon=(80, 120, 200), pelo_estilo="rizos", tipo="nino", extra="dino")


def frame_cocina():
    im = cocina()
    d = ImageDraw.Draw(im)
    # mesa
    d.rounded_rectangle([140 * S, 1480 * S, 940 * S, 1530 * S], 16 * S, fill=(200, 140, 90), outline=(120, 80, 50), width=8)
    # leche derramada
    d.ellipse([560 * S, 1470 * S, 760 * S, 1500 * S], fill=(255, 255, 250))
    tostada(im, 360 * S, 1465 * S, 120 * S)
    p = persona(im, 540 * S, 1860 * S, 1250 * S, **DANI, expr="panico", brazos="bebe", mira=(-1, 0))
    bebe(im, p["x"] + p["bw"] * .12, p["ty"] + p["body_h"] * .28, 62 * S)
    persona(im, 230 * S, 1880 * S, 560 * S, **VERA, expr="listilla", brazos="jarras", mira=(1, -1))
    persona(im, 880 * S, 1890 * S, 470 * S, **HUGO, expr="risa", brazos="arriba", mira=(-1, 0))
    hud(im)
    subtitulo(im, ["Lo", "has", "perdido."], 2, y=1300)
    return im


if __name__ == "__main__":
    im = frame_cocina().convert("RGB").resize((1080, 1920), Image.LANCZOS)
    im.save("/home/claude/papa/prueba_estilo.jpg", quality=92)
