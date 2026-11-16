"""Piezas comunes de los episodios (sacadas del Ep.3)."""
import math
import render as R
from render import Image, ImageDraw, ImageFilter, W, H, panel, text, ease, clamp, YEL, CYAN, MAG, WHITE, OL, GRIS, F_UI, F_ANTON
AZ = (60, 110, 220)
AVISOS = []

def aviso_voto(c, T):
    for t0 in AVISOS:
        if not (t0 <= T < t0 + 5.5): continue
        u = ease((T - t0) / .35) if T < t0 + 5.1 else 1 - ease((T - t0 - 5.1) / .35)
        y = 300 + 20 * (1 - u); a = int(255 * u)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        beat = 1 + .03 * math.sin((T - t0) * 8)
        w2 = 330 * beat
        d.rounded_rectangle((540 - w2, y, 540 + w2, y + 74), 37, fill=(255, 255, 255, a), outline=OL + (a,), width=5)
        d.ellipse((540 - w2 + 10, y + 9, 540 - w2 + 66, y + 65), fill=AZ + (a,)); d.text((540 - w2 + 38, y + 37), "A", font=R.font(F_ANTON, 38), fill=WHITE + (a,), anchor="mm")
        d.ellipse((540 + w2 - 66, y + 9, 540 + w2 - 10, y + 65), fill=MAG + (a,)); d.text((540 + w2 - 38, y + 37), "B", font=R.font(F_ANTON, 38), fill=WHITE + (a,), anchor="mm")
        d.text((540, y + 24), "¿TÚ QUÉ HARÍAS? VOTA EN LA ENCUESTA", font=R.font(F_ANTON, 27), fill=OL + (a,), anchor="mm")
        d.text((540, y + 54), "y dime en comentarios por qué", font=R.font(F_UI, 23), fill=(200, 50, 50, a), anchor="mm")
        c.alpha_composite(lay)

def linterna(c, cx, cy, r=330, amb=215):
    """Oscurece todo salvo un círculo de linterna en (cx, cy)."""
    m = Image.new("L", (W, H), amb); ImageDraw.Draw(m).ellipse((cx - r, cy - r, cx + r, cy + r), fill=0)
    m = m.filter(ImageFilter.GaussianBlur(60))
    sh = Image.new("RGBA", (W, H), (4, 4, 10, 255)); sh.putalpha(m); c.alpha_composite(sh)
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((cx - r * .8, cy - r * .8, cx + r * .8, cy + r * .8), fill=(255, 235, 190, 40))
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(40)))

def humo(c, T, t0, x, y, dur=1.6, n=10):
    if not (0 <= T - t0 < dur): return
    u = (T - t0) / dur
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for i in range(n):
        px = x + (i - n / 2) * 40 + 180 * u * (1 if i % 2 else .6); py = y - 60 * u * (i % 3)
        r = 50 + 120 * u; d.ellipse((px - r, py - r * .6, px + r, py + r * .6), fill=(200, 200, 210, int(110 * (1 - u))))
    c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(14)))

def llamas(c, T, t0, ex, ey, n=3, gap=.28, s=1.0):
    d = ImageDraw.Draw(c)
    for i in range(n):
        tt = t0 + i * gap
        if 0 <= T - tt < .13:
            k = max(.25, 1 - (T - tt) / .13)
            d.ellipse((ex - 10 * s, ey - 34 * k * s, ex + 110 * k * s, ey + 34 * k * s), fill=(255, 150, 40))
            d.ellipse((ex + 5 * s, ey - 18 * k * s, ex + 70 * k * s, ey + 18 * k * s), fill=(255, 240, 160))

def tinte(c, col, a): c.alpha_composite(Image.new("RGBA", (W, H), col + (int(a),)))

def confeti(c, T, t0, n=70):
    if T < t0: return
    d = ImageDraw.Draw(c); cols = [YEL, CYAN, MAG, WHITE, (90, 140, 255)]
    for i in range(n):
        x0 = (i * 137) % 1080; sp = 380 + (i * 53) % 420; ph = i * .7
        tt = T - t0 - (i % 9) * .05
        if tt < 0: continue
        y = 300 + tt * sp; x = x0 + 40 * math.sin(tt * 3 + ph)
        if y > 1700: continue
        w, h = 18, 9 + 7 * abs(math.sin(tt * 6 + ph))
        d.rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), fill=cols[i % 5])

def barra_voto(c, T, y, L_, txt, pct, col, win, t0):
    d = ImageDraw.Draw(c)
    p = pct * (.7 + .3 * ease(clamp((T - t0) / .4)))
    panel(c, (90, y - 75, 990, y + 75), fill=(16, 14, 30), alpha=235, rad=28, outline=col if win else (70, 70, 90), ow=6 if win else 3)
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((112, y - 52, 212, y + 48), 22, fill=col)
    text(d, (162, y - 2), L_, 76, WHITE)
    d.rounded_rectangle((240, y + 8, 960, y + 44), 18, fill=(40, 38, 60))
    d.rounded_rectangle((240, y + 8, 240 + 720 * p / 100, y + 44), 18, fill=col)
    text(d, (240, y - 30), txt, 40, WHITE, "lm")
    text(d, (960, y - 30), f"{int(round(p))} %", 52, YEL if win else GRIS, "rm", stroke=5)

def ep_chispas(c, T, t0, x, y, n=26, dur=.5):
    if not (0 <= T - t0 < dur): return
    d = ImageDraw.Draw(c); u = (T - t0) / dur
    for i in range(n):
        a = -math.pi * (.05 + .9 * ((i * 37) % 100) / 100); v = 260 + (i * 53) % 260
        px = x + math.cos(a) * v * u; py = y + math.sin(a) * v * u + 400 * u * u
        d.line((px, py, px - 14 * math.cos(a), py - 14 * math.sin(a)), fill=(255, 220, 120), width=5)
