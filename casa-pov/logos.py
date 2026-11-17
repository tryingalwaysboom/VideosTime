"""3 logos (foto de perfil 1080x1080, pensados para recorte circular) para @lacasade1dolar."""
import math
from PIL import Image, ImageDraw, ImageFilter
import art as A
from art import font, F_ANTON, F_UI
Z = 1080; C = Z // 2

def circ_mask(): m = Image.new("L", (Z, Z), 0); ImageDraw.Draw(m).ellipse((0, 0, Z, Z), fill=255); return m
def glow(im, fn, b): l = Image.new("RGBA", im.size, (0, 0, 0, 0)); fn(ImageDraw.Draw(l)); im.alpha_composite(l.filter(ImageFilter.GaussianBlur(b)))

# 1) La casa real de la serie, con chapa "$1"
def logo1():
    p = A.plate_casa()
    im = p.crop((0, 520, 1296, 520 + 1296)).resize((Z, Z), Image.LANCZOS).convert("RGBA")
    ax, ay = A.attic_xy(); fx, fy = (ax - 0) * Z / 1296, (ay - 520) * Z / 1296
    glow(im, lambda d: d.ellipse((fx - 120, fy - 120, fx + 120, fy + 120), fill=(255, 180, 80, 170)), 40)
    d = ImageDraw.Draw(im); r = 40; d.ellipse((fx - r, fy - r, fx + r, fy + r), fill=(255, 205, 120)); d.line((fx - r, fy, fx + r, fy), fill=(30, 30, 42), width=6); d.line((fx, fy - r, fx, fy + r), fill=(30, 30, 42), width=6)
    g = Image.new("RGBA", (Z, Z), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for y in range(620, Z): gd.line((0, y, Z, y), fill=(4, 4, 12, int(min(220, (y - 620) * .6))))
    im.alpha_composite(g); d = ImageDraw.Draw(im)
    d.text((C, 820), "LA CASA DE", font=font(F_ANTON, 92), fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=(10, 10, 20))
    d.text((C, 935), "$1", font=font(F_ANTON, 150), fill=(255, 206, 60), anchor="mm", stroke_width=10, stroke_fill=(10, 10, 20))
    return im

# 2) Icono minimalista: casa en silueta, luna, ventana encendida y "$1" en la puerta
def logo2():
    im = A.grad(Z, Z, (10, 12, 34), (34, 30, 70)).convert("RGBA"); d = ImageDraw.Draw(im)
    glow(im, lambda dd: dd.ellipse((640, 150, 900, 410), fill=(200, 210, 255, 120)), 40)
    d = ImageDraw.Draw(im); d.ellipse((680, 190, 860, 370), fill=(240, 240, 228)); d.ellipse((730, 220, 790, 280), fill=(220, 220, 208))
    roof = [(240, 520), (C, 280), (840, 520)]
    d.polygon([(290, 500), (790, 500), (790, 860), (290, 860)], fill=(18, 18, 34))
    d.rectangle((630, 300, 690, 440), fill=(18, 18, 34))
    d.polygon(roof, fill=(18, 18, 34)); d.line([roof[0], roof[1], roof[2]], fill=(255, 170, 70), width=18, joint="curve")
    glow(im, lambda dd: dd.ellipse((C - 80, 370, C + 80, 530), fill=(255, 180, 80, 200)), 30)
    d = ImageDraw.Draw(im); d.ellipse((C - 46, 404, C + 46, 496), fill=(255, 205, 120)); d.line((C - 46, 450, C + 46, 450), fill=(18, 18, 34), width=8); d.line((C, 404, C, 496), fill=(18, 18, 34), width=8)
    d.rounded_rectangle((C - 110, 610, C + 110, 860), 16, fill=(255, 206, 60))
    d.text((C, 740), "$1", font=font(F_ANTON, 170), fill=(18, 18, 34), anchor="mm")
    d.rectangle((150, 860, 930, 878), fill=(255, 170, 70))
    d.text((C, 950), "LA CASA DE 1 DÓLAR", font=font(F_ANTON, 64), fill=(255, 255, 255), anchor="mm")
    return im

# 3) Billete de dólar con la casa dentro del óvalo central
def logo3():
    im = Image.new("RGBA", (Z, Z), (14, 22, 18, 255)); d = ImageDraw.Draw(im)
    glow(im, lambda dd: dd.ellipse((60, 60, Z - 60, Z - 60), fill=(80, 140, 90, 90)), 80)
    d = ImageDraw.Draw(im)
    b = (90, 250, 990, 830)
    d.rounded_rectangle(b, 24, fill=(200, 218, 182), outline=(60, 92, 58), width=10)
    d.rounded_rectangle((120, 280, 960, 800), 16, outline=(90, 124, 82), width=4)
    pat = Image.new("RGBA", (Z, Z), (0, 0, 0, 0)); pd = ImageDraw.Draw(pat)
    for k in range(0, 1100, 22): pd.line((90 + k, 250, 90 + k - 120, 830), fill=(186, 206, 168), width=2)
    bm = Image.new("L", (Z, Z), 0); ImageDraw.Draw(bm).rounded_rectangle((100, 260, 980, 820), 20, fill=255)
    im.paste(pat, (0, 0), Image.fromarray(__import__("numpy").minimum(__import__("numpy").asarray(bm), __import__("numpy").asarray(pat.split()[3])))); d = ImageDraw.Draw(im)
    d.rounded_rectangle(b, 24, outline=(60, 92, 58), width=10)
    for cx, cy in ((190, 340), (890, 340), (190, 740), (890, 740)): d.text((cx, cy), "1", font=font(F_ANTON, 96), fill=(60, 92, 58), anchor="mm")
    ov = (340, 330, 740, 800)
    house = A.plate_casa().crop((150, 420, 1150, 1950)).resize((ov[2] - ov[0], ov[3] - ov[1]), Image.LANCZOS)
    m = Image.new("L", house.size, 0); ImageDraw.Draw(m).ellipse((0, 0, house.width, house.height), fill=255)
    gray = house.convert("L").point(lambda v: min(255, int(v * 1.5)))
    tint = Image.merge("RGBA", (gray.point(lambda v: int(v * .55 + 30)), gray.point(lambda v: int(v * .7 + 40)), gray.point(lambda v: int(v * .5 + 28)), m))
    im.alpha_composite(tint, (ov[0], ov[1])); d = ImageDraw.Draw(im)
    d.ellipse(ov, outline=(60, 92, 58), width=12); d.ellipse((ov[0] - 16, ov[1] - 16, ov[2] + 16, ov[3] + 16), outline=(90, 124, 82), width=4)
    d.text((C, 296), "LA CASA DE", font=font(F_ANTON, 40), fill=(60, 92, 58), anchor="mm")
    d.rounded_rectangle((C - 260, 860, C + 260, 990), 26, fill=(190, 30, 36))
    d.text((C, 925), "UN DÓLAR", font=font(F_ANTON, 92), fill=(255, 240, 220), anchor="mm")
    return im

out = []
for i, fn in enumerate((logo1, logo2, logo3), 1):
    im = fn().convert("RGB"); p = f"out/logo{i}_lacasade1dolar.png"; im.save(p); out.append(im)
prev = Image.new("RGB", (3 * 400, 400), (240, 240, 240)); m = circ_mask().resize((380, 380))
for i, im in enumerate(out): prev.paste(im.resize((380, 380)), (i * 400 + 10, 10), m)
prev.save("/tmp/logos_prev.jpg")
