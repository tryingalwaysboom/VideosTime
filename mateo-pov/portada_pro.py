"""Portadas 'pro' de la serie Mateo, mismo estilo que las del taller: escena de la opción que ganó con luz de cine,
fondo desenfocado, color propio por episodio, título corto grande + etiqueta PARTE N. Sale 3:4 y 9:16 (1080x1920)."""
import os, sys, math, random
import render2 as V
import numpy as np
from render2 import Image, ImageDraw, ImageFilter, put, bg, rex_nino_full, font, F_ANTON, OL, YEL

CW, CH = 1080, 1920   # se compone en 9:16; la portada 3:4 es el recorte central (subido SUBE px)
SUBE = 80
OY = 240 - SUBE

def dark(c, a): c.alpha_composite(Image.new("RGBA", c.size, (0, 0, 0, a)))

def grade(c, top, bottom, a=110):
    g = Image.new("RGBA", (CW, CH)); gd = ImageDraw.Draw(g)
    for y in range(CH):
        k = y / CH; gd.line((0, y, CW, y), fill=tuple(int(top[i] * (1 - k) + bottom[i] * k) for i in range(3)) + (a,))
    c.alpha_composite(g)

def glow(c, items, blur=80):
    g = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for box, col in items: gd.ellipse(box, fill=col)
    c.alpha_composite(g.filter(ImageFilter.GaussianBlur(blur)))

def rayos(c, x, y, col, n=9, a=40, spread=1.2, ang0=math.pi / 2):
    g = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for i in range(n):
        an = ang0 + (i - (n - 1) / 2) * spread / n
        gd.polygon([(x, y), (x + 1800 * math.cos(an - .04), y + 1800 * math.sin(an - .04)), (x + 1800 * math.cos(an + .04), y + 1800 * math.sin(an + .04))], fill=col + (a,))
    c.alpha_composite(g.filter(ImageFilter.GaussianBlur(14)))

def polvo(c, seed, col=(255, 240, 210)):
    rnd = random.Random(seed); g = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for _ in range(70):
        x, y, rr = rnd.randint(0, CW), rnd.randint(0, CH), rnd.choice([2, 3, 4, 6, 9])
        gd.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col + (rnd.randint(40, 150),))
    c.alpha_composite(g.filter(ImageFilter.GaussianBlur(1.5)))

def titulo(c, s, col1, col2, glowcol, y=1170, size=150):
    f = font(F_ANTON, size)
    m = Image.new("L", (CW, 260), 0); ImageDraw.Draw(m).text((540, 130), s, font=f, anchor="mm", fill=255)
    gr = Image.new("RGBA", (CW, 260)); gd = ImageDraw.Draw(gr)
    for yy in range(260):
        k = yy / 260; gd.line((0, yy, CW, yy), fill=tuple(int(col1[i] * (1 - k) + col2[i] * k) for i in range(3)) + (255,))
    halo = Image.new("RGBA", (CW, 260), (0, 0, 0, 0)); ImageDraw.Draw(halo).text((540, 130), s, font=f, anchor="mm", fill=glowcol + (230,), stroke_width=14, stroke_fill=glowcol + (230,))
    c.alpha_composite(halo.filter(ImageFilter.GaussianBlur(22)), (0, y - 130))
    for k in range(14, 0, -2):
        sh = Image.new("RGBA", (CW, 260), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((540, 130), s, font=f, anchor="mm", fill=(20, 12, 30), stroke_width=10, stroke_fill=(20, 12, 30))
        c.alpha_composite(sh, (k // 2, y - 130 + k))
    sh = Image.new("RGBA", (CW, 260), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((540, 130), s, font=f, anchor="mm", fill=OL, stroke_width=12, stroke_fill=OL)
    c.alpha_composite(sh, (0, y - 130))
    txt = Image.new("RGBA", (CW, 260), (0, 0, 0, 0)); txt.paste(gr, (0, 0), m); c.alpha_composite(txt, (0, y - 130))

def chip(c, n, col, y=1318):
    d = ImageDraw.Draw(c); s = f"PARTE {n}"; f = font(F_ANTON, 80)
    w = d.textlength(s, font=f) + 90
    d.rounded_rectangle((540 - w / 2, y - 56, 540 + w / 2, y + 56), 56, fill=col, outline=OL, width=5)
    d.text((540, y + 2), s, font=f, fill=OL, anchor="mm")

def bloom(c, thr=210, k=.35):
    lum = c.convert("L").point(lambda v: 255 if v > thr else 0)
    br = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); br.paste(c, (0, 0), lum)
    br = br.filter(ImageFilter.GaussianBlur(26)); br.putalpha(br.getchannel("A").point(lambda v: int(v * k)))
    c.alpha_composite(br)

def acabado(c, seed):
    v = Image.new("L", (CW, CH), 0); ImageDraw.Draw(v).ellipse((-260, -200, CW + 260, CH + 260), fill=255)
    v = v.filter(ImageFilter.GaussianBlur(160)); sh = Image.new("RGBA", (CW, CH), (0, 0, 0, 230)); sh.putalpha(v.point(lambda p: 230 - int(p * .9)))
    c.alpha_composite(sh)

def a_916(c34, bgname, fx, fy, out):
    full = bg(bgname, 0, 0, 1.3, 1.3, 1, fx, fy).filter(ImageFilter.GaussianBlur(14)); dark(full, 190)
    m = Image.new("L", c34.size, 255); md = ImageDraw.Draw(m)
    for i in range(90):
        a = int(255 * i / 90); md.line((0, i, CW, i), fill=a); md.line((0, CH - 1 - i, CW, CH - 1 - i), fill=a)
    full.paste(c34, (0, 240 - SUBE), m)
    full.convert("RGB").filter(ImageFilter.UnsharpMask(1.2, 60, 2)).save(out, quality=100, subsampling=0)

def p2():
    """Ganó la B: escribir el nombre de su dino. Mateo feliz con la crayola verde, el Rex, y REX escrito por él en la hoja."""
    c = bg("bg_cuarto", 0, 0, 1.35, 1.35, 1, .5, .55).filter(ImageFilter.GaussianBlur(6)); dark(c, 120)
    grade(c, (10, 60, 40), (90, 40, 20), 110)
    rayos(c, 540, OY - 80, (255, 235, 180), 9, 34, 1.1)
    glow(c, [((80, OY + 120, 1000, OY + 960), (255, 215, 150, 110)), ((-120, OY + 820, 1200, OY + 1150), (60, 200, 110, 110))])
    hoja = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); put(hoja, "hoja", 540, OY + 330, .9)
    rex_nino_full(hoja, 270, OY + 230, 200)
    c.alpha_composite(hoja.rotate(-5, center=(540, OY + 330), resample=Image.BICUBIC))
    lay = Image.new("RGBA", (CW, CH + 1200), (0, 0, 0, 0))
    s_ = .72
    put(lay, "mateo_feliz_crayola", 400, OY + 760 + 400 * s_, s_)
    put(lay, "dino", 820, OY + 930, .55, rot=6)
    lay = lay.crop((0, 0, CW, CH))
    fade = Image.new("L", (CW, CH), 255); fd = ImageDraw.Draw(fade)   # el cuerpo se funde por debajo del título
    for y in range(OY + 1080, CH): fd.line((0, y, CW, y), fill=max(0, int(255 * (1 - (y - OY - 1080) / 260))))
    lay.putalpha(Image.fromarray(np.minimum(np.array(lay.getchannel("A")), np.array(fade))))
    rim = Image.new("RGBA", lay.size, (255, 236, 190, 255)); rim.putalpha(lay.getchannel("A").filter(ImageFilter.MaxFilter(11)))
    c.alpha_composite(rim.filter(ImageFilter.GaussianBlur(8)))
    c.alpha_composite(lay)
    sombra = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); sd = ImageDraw.Draw(sombra)
    for y in range(OY + 1000, CH): sd.line((0, y, CW, y), fill=(14, 10, 24, min(170, int((y - OY - 1000) * .9))))
    c.alpha_composite(sombra)
    polvo(c, 2, (255, 245, 210))
    bloom(c)
    titulo(c, "SE LLAMA REX", (255, 252, 230), (255, 205, 70), (60, 200, 90), y=OY + 1170)
    chip(c, 2, (120, 220, 130), y=OY + 1318); acabado(c, 2); return c

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    c = {2: p2}[n]().convert("RGB").filter(ImageFilter.UnsharpMask(1.2, 60, 2))
    c.save(os.path.join(V.HERE, f"portada_pro_parte{n}_9x16.jpg"), quality=100, subsampling=0)
    c.crop((0, OY, CW, OY + 1440)).save(os.path.join(V.HERE, f"portada_pro_parte{n}.jpg"), quality=100, subsampling=0)
    print("ok")
