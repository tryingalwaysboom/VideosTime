"""Story de Instagram para llevar gente a @lacasade1dolar: casa abandonada de noche, gancho '$1',
hueco vacío en el centro para el sticker de mención (@) y flechas animadas apuntando a él. Sale PNG + MP4 de 7 s."""
import math, os, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, DUR = 1080, 1920, 30, 7.0
ANTON = os.path.join(HERE, "fonts", "Anton-Regular.ttf")
YEL, RED, WHITE, INK = (255, 206, 60), (255, 70, 60), (255, 255, 255), (12, 10, 22)
HUECO = (240, 830, 840, 1090)   # zona vacía para el @

def F(s): return ImageFont.truetype(ANTON, int(s))

BASE = Image.open(os.path.join(HERE, "out", "casa_fachada_detalle.jpg")).convert("RGBA").resize((W, H), Image.LANCZOS)

def fondo(t):
    z = 1.04 + .03 * t / DUR
    w, h = int(W * z), int(H * z); im = BASE.resize((w, h), Image.BICUBIC)
    c = im.crop(((w - W) // 2, (h - H) // 2, (w - W) // 2 + W, (h - H) // 2 + H))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for y in range(H):   # oscurece arriba y abajo para el texto
        a = 175 if y < 560 else (int(175 - (y - 560) * .9) if y < 650 else (95 if y < 1250 else int(95 + (y - 1250) * .25)))
        gd.line((0, y, W, y), fill=(6, 6, 18, min(215, a)))
    c.alpha_composite(g)
    return c

def texto(d, xy, s, size, fill, stroke=12):
    d.text(xy, s, font=F(size), fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=INK)

def flecha(c, x, y, ang, L, col, t, fase):
    """Flecha gruesa que late hacia su punta (x, y)."""
    off = 26 * (.5 + .5 * math.sin(t * 7 + fase))
    ux, uy = math.cos(ang), math.sin(ang)
    tx, ty = x - ux * off, y - uy * off   # punta
    bx, by = tx - ux * L, ty - uy * L      # cola
    px, py = -uy, ux; hw, hl, sw = 62, 80, 30
    hx, hy = tx - ux * hl, ty - uy * hl
    poly = [(bx + px * sw, by + py * sw), (hx + px * sw, hy + py * sw), (hx + px * hw, hy + py * hw), (tx, ty),
            (hx - px * hw, hy - py * hw), (hx - px * sw, hy - py * sw), (bx - px * sw, by - py * sw)]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.polygon(poly, fill=col + (120,)); lay = lay.filter(ImageFilter.GaussianBlur(14))
    ld = ImageDraw.Draw(lay); ld.polygon(poly, fill=col, outline=INK); ld.line(poly + [poly[0]], fill=INK, width=8, joint="curve")
    c.alpha_composite(lay)

def frame(t):
    c = fondo(t); d = ImageDraw.Draw(c)
    # titular arriba (fuera de la zona del nombre de la story)
    texto(d, (540, 330), "COMPRÉ UNA CASA", 104, WHITE)
    k = 1 + .05 * math.sin(t * 4)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.text((540, 520), "POR $1", font=F(230 * k), fill=YEL, anchor="mm", stroke_width=16, stroke_fill=INK)
    gl = lay.filter(ImageFilter.GaussianBlur(22)); c.alpha_composite(Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 0)), gl, .7)); c.alpha_composite(lay)
    d = ImageDraw.Draw(c)
    # hueco para el @: marco discontinuo que brilla, vacío por dentro
    x0, y0, x1, y1 = HUECO
    box = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(box)
    bd.rounded_rectangle(HUECO, 46, fill=(8, 8, 20, 120))
    c.alpha_composite(box)
    d = ImageDraw.Draw(c); a = .55 + .45 * math.sin(t * 5)
    col = tuple(int(YEL[i] * a + WHITE[i] * (1 - a)) for i in range(3))
    per = 2 * (x1 - x0) + 2 * (y1 - y0); seg, gap = 46, 26; s = (t * 120) % (seg + gap)
    def pt(u):
        u %= per
        if u < x1 - x0: return (x0 + u, y0)
        u -= x1 - x0
        if u < y1 - y0: return (x1, y0 + u)
        u -= y1 - y0
        if u < x1 - x0: return (x1 - u, y1)
        u -= x1 - x0; return (x0, y1 - u)
    u = s
    while u < per + s:
        a1, a2 = pt(u), pt(u + seg)
        if abs(a1[0] - a2[0]) < 1 or abs(a1[1] - a2[1]) < 1: d.line((a1, a2), fill=col, width=9)
        u += seg + gap
    texto(d, (540, 760), "TOCA AQUÍ", 70, col, 9)
    # flechas hacia el centro del hueco
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    flecha(c, x0 - 8, cy, 0, 110, YEL, t, 0)                 # desde la izquierda
    flecha(c, x1 + 8, cy, math.pi, 110, YEL, t, 0)           # desde la derecha
    flecha(c, x0 + 90, y1 + 10, -math.pi * .62, 150, RED, t, 1.6)   # desde abajo
    flecha(c, x1 - 90, y1 + 10, -math.pi * .38, 150, RED, t, 1.6)
    d = ImageDraw.Draw(c)
    # abajo
    texto(d, (540, 1390), "37 AÑOS ABANDONADA", 78, WHITE, 10)
    texto(d, (540, 1490), "Y LA ESTOY ARREGLANDO", 78, YEL, 10)
    d.rounded_rectangle((300, 1550, 780, 1630), 40, fill=RED, outline=INK, width=6)
    d.text((540, 1592), "PARTE NUEVA CADA DÍA", font=F(46), fill=WHITE, anchor="mm")
    return c.convert("RGB")

if __name__ == "__main__":
    out = os.path.join(HERE, "out")
    frame(1.0).save(os.path.join(out, "story_lacasade1dolar.png"))
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", os.path.join(out, "story_lacasade1dolar.mp4")], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("ok")
