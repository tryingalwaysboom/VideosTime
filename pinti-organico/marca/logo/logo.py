"""Logo redondo de perfil "Aprende con Pinti" (1080x1080, pensado para el recorte circular de Instagram)."""
import math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..")
F7 = os.path.join(ROOT, "marca", "fuentes", "Fredoka-700.ttf")
S = 2160  # se dibuja a 2x y se reduce al final
C = S // 2
NAR, NARS, TINTA, PAPEL, MELO, AMA, ROSA, AZ = (252, 140, 68), (204, 124, 60), (60, 52, 44), (255, 253, 248), (244, 188, 148), (252, 220, 108), (244, 172, 196), (74, 143, 219)

def texto_en_arco(img, txt, radio, centro_ang, tam, color, borde, ancho_borde, abajo=False):
    f = ImageFont.truetype(F7, tam); d0 = ImageDraw.Draw(img)
    anchos = [d0.textlength(ch, font=f) for ch in txt]; esp = tam * .06
    total = sum(anchos) + esp * (len(txt) - 1)
    ang_total = total / radio
    a = centro_ang - ang_total / 2 if not abajo else centro_ang + ang_total / 2
    for ch, w in zip(txt, anchos):
        da = (w + esp) / radio
        am = a + (da / 2 if not abajo else -da / 2)
        g = Image.new("RGBA", (int(tam * 1.6), int(tam * 1.6)), (0, 0, 0, 0))
        ImageDraw.Draw(g).text((g.width / 2, g.height / 2), ch, font=f, fill=color, anchor="mm", stroke_width=ancho_borde, stroke_fill=borde)
        rot = -math.degrees(am) - 90 if not abajo else -math.degrees(am) + 90
        g = g.rotate(rot, resample=Image.BICUBIC, expand=True)
        x = C + radio * math.cos(am); y = C + radio * math.sin(am)
        img.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))
        a += da if not abajo else -da

def estrella(d, cx, cy, r, col, borde):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5; rr = r if i % 2 == 0 else r * .45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=col, outline=borde, width=6)

img = Image.new("RGBA", (S, S), PAPEL + (255,))
d = ImageDraw.Draw(img)
# fondo: sol amarillo suave con anillo melocotón
d.ellipse((C - 1040, C - 1040, C + 1040, C + 1040), fill=(253, 235, 214))
d.ellipse((C - 760, C - 760, C + 760, C + 760), fill=AMA)
gl = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((C - 620, C - 700, C + 520, C + 300), fill=(255, 245, 200, 150))
img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(120)))
d = ImageDraw.Draw(img)
# anillo punteado (como las letras para repasar)
for i in range(72):
    a = i * 2 * math.pi / 72
    x, y = C + 820 * math.cos(a), C + 820 * math.sin(a)
    d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=MELO)
# texto curvo
texto_en_arco(img, "APRENDE CON", 900, -math.pi / 2, 150, NAR, PAPEL, 14)
texto_en_arco(img, "PINTI", 905, math.pi / 2, 170, AZ, PAPEL, 14, abajo=True)
d = ImageDraw.Draw(img)
for ang in (math.radians(200), math.radians(-20)):
    estrella(d, C + 905 * math.cos(ang), C + 905 * math.sin(ang), 46, AMA, TINTA)
# Pinti con sombra suave
p = Image.open(os.path.join(ROOT, "assets", "pinti.png")).convert("RGBA")
h = 1180; p = p.resize((int(p.width * h / p.height), h), Image.LANCZOS)
sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
ImageDraw.Draw(sh).ellipse((C - 330, C + 520, C + 330, C + 620), fill=(150, 90, 40, 110))
img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30)))
img.alpha_composite(p, (C - p.width // 2 + 20, C - h // 2 + 30))
# brillitos
d = ImageDraw.Draw(img)
for (x, y, r) in ((C - 470, C - 300, 26), (C + 460, C - 180, 20), (C + 420, C + 320, 24), (C - 430, C + 260, 18)):
    d.polygon([(x, y - r * 2), (x + r * .5, y - r * .5), (x + r * 2, y), (x + r * .5, y + r * .5), (x, y + r * 2), (x - r * .5, y + r * .5), (x - r * 2, y), (x - r * .5, y - r * .5)], fill=(255, 255, 255))
out = img.resize((1080, 1080), Image.LANCZOS)
out.convert("RGB").save(os.path.join(HERE, "logo_aprende_con_pinti.png"))
# vista previa recortada en círculo, como en Instagram
m = Image.new("L", (1080, 1080), 0); ImageDraw.Draw(m).ellipse((0, 0, 1080, 1080), fill=255)
pv = Image.new("RGBA", (1080, 1080), (255, 255, 255, 255)); pv.paste(out, (0, 0), m)
pv.resize((540, 540), Image.LANCZOS).save("/tmp/logo_circulo.png")
print("ok")
