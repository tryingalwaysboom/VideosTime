"""Portadas 'pro' 1080x1440 (3:4): escena protagonista grande con luz de cine, número gigante de fondo,
título corto del episodio y etiqueta PARTE N. Sin cartel de la serie."""
import os, math, random
import ep3
import portada as P
from luces import coche_faros
r = ep3.R
from render import Image, ImageDraw, ImageFilter, put, scaled, bg, dark, text, YEL, RED, WHITE, OL, CYAN, MAG, F_ANTON

CW, CH = 1080, 1440

def lienzo(name, z=1.2, fx=.5, fy=.55, d=150):
    c = bg(name, 0, 0, z, z, 1, fx, fy).crop((0, 240, 1080, 1680)); dark(c, d); return c

def grade(c, top, bottom, a=110):
    """Gradiente de color (tono cinematográfico) de arriba a abajo."""
    g = Image.new("RGBA", (CW, CH)); gd = ImageDraw.Draw(g)
    for y in range(CH):
        k = y / CH; col = tuple(int(top[i] * (1 - k) + bottom[i] * k) for i in range(3))
        gd.line((0, y, CW, y), fill=col + (a,))
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

def numero(c, n, col):
    """Número gigante del episodio detrás de la escena, solo contorno, semitransparente."""
    g = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    f = r.font(F_ANTON, 760)
    gd.text((540, 560), f"{n:02d}", font=f, anchor="mm", fill=(0, 0, 0, 0), stroke_width=10, stroke_fill=col + (120,))
    c.alpha_composite(g)

def polvo(c, seed, col=(255, 240, 210)):
    rnd = random.Random(seed); g = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for _ in range(70):
        x, y, rr = rnd.randint(0, CW), rnd.randint(0, CH), rnd.choice([2, 3, 4, 6, 9])
        gd.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col + (rnd.randint(40, 150),))
    c.alpha_composite(g.filter(ImageFilter.GaussianBlur(1.5)))

def titulo(c, s, col1, col2, glowcol, y=1170):
    """Título del episodio con degradado, contorno y halo."""
    f = r.font(F_ANTON, 150)
    m = Image.new("L", (CW, 260), 0); ImageDraw.Draw(m).text((540, 130), s, font=f, anchor="mm", fill=255)
    gr = Image.new("RGBA", (CW, 260)); gd = ImageDraw.Draw(gr)
    for yy in range(260):
        k = yy / 260; gd.line((0, yy, CW, yy), fill=tuple(int(col1[i] * (1 - k) + col2[i] * k) for i in range(3)) + (255,))
    halo = Image.new("RGBA", (CW, 260), (0, 0, 0, 0)); ImageDraw.Draw(halo).text((540, 130), s, font=f, anchor="mm", fill=glowcol + (230,), stroke_width=14, stroke_fill=glowcol + (230,))
    c.alpha_composite(halo.filter(ImageFilter.GaussianBlur(22)), (0, y - 130))
    sh = Image.new("RGBA", (CW, 260), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((540, 130), s, font=f, anchor="mm", fill=OL, stroke_width=12, stroke_fill=OL)
    c.alpha_composite(sh, (0, y - 130))
    txt = Image.new("RGBA", (CW, 260), (0, 0, 0, 0)); txt.paste(gr, (0, 0), m); c.alpha_composite(txt, (0, y - 130))

def chip(c, n, col, y=1320):
    d = ImageDraw.Draw(c); s = f"PARTE {n}"; f = r.font(F_ANTON, 64)
    w = d.textlength(s, font=f) + 80
    d.rounded_rectangle((540 - w / 2, y - 46, 540 + w / 2, y + 46), 46, fill=col, outline=OL, width=5)
    d.text((540, y + 2), s, font=f, fill=OL, anchor="mm")

def acabado(c, seed):
    v = Image.new("L", (CW, CH), 0); ImageDraw.Draw(v).ellipse((-260, -200, CW + 260, CH + 260), fill=255)
    v = v.filter(ImageFilter.GaussianBlur(160)); sh = Image.new("RGBA", (CW, CH), (0, 0, 0, 230)); sh.putalpha(v.point(lambda p: 230 - int(p * .9)))
    c.alpha_composite(sh)
    rnd = random.Random(seed); g = Image.new("L", (CW // 2, CH // 2)); g.putdata([rnd.randint(0, 255) for _ in range(CW * CH // 4)])
    gr = Image.new("RGBA", (CW, CH), (255, 255, 255, 0)); gr.putalpha(g.resize((CW, CH)).point(lambda p: int(p * .06))); c.alpha_composite(gr)

def p1():
    c = lienzo("bg_taller", 1.3, .5, .62, 170); grade(c, (40, 10, 70), (120, 20, 90), 90)
    numero(c, 1, MAG)
    rayos(c, 540, -60, (255, 230, 190), 7, 34, .9)
    glow(c, [((80, 520, 1000, 1020), (255, 220, 170, 80)), ((-100, 850, 1180, 1200), MAG + (110,))])
    car = scaled("deportivo", .92).rotate(-3, resample=Image.BICUBIC, expand=True)
    ref = car.transpose(Image.FLIP_TOP_BOTTOM); ref.putalpha(ref.getchannel("A").point(lambda v: int(v * .22)))
    c.alpha_composite(ref, (540 - ref.width // 2, 870 - 60))
    c.alpha_composite(car, (540 - car.width // 2, 760 - car.height // 2))
    put(c, "lona", 700, 700, .72, rot=-10)
    polvo(c, 1)
    titulo(c, "LA HERENCIA", (255, 245, 220), (242, 190, 60), MAG)
    chip(c, 1, YEL); acabado(c, 1); return c

def p2():
    c = lienzo("bg_fachada", 1.15, .5, .7, 120); grade(c, (60, 0, 10), (150, 30, 20), 110)
    numero(c, 2, RED)
    pers = scaled("persiana", 1.25)
    c.alpha_composite(Image.new("RGBA", (pers.width, pers.height), (8, 6, 10, 255)), (540 - pers.width // 2, 250))
    h = int(pers.height * .62); c.alpha_composite(pers.crop((0, pers.height - h, pers.width, pers.height)), (540 - pers.width // 2, 250))
    glow(c, [((140, 700, 940, 1100), (255, 120, 60, 120))])
    # Nitro a contraluz delante de la persiana
    ni = scaled("nitro", 1.0); sil = Image.new("RGBA", ni.size, (10, 8, 14, 255)); sil.putalpha(ni.getchannel("A"))
    rim = Image.new("RGBA", ni.size, (255, 140, 80, 255)); rim.putalpha(ni.getchannel("A").filter(ImageFilter.MaxFilter(9)))
    c.alpha_composite(rim.filter(ImageFilter.GaussianBlur(6)), (540 - ni.width // 2, 640 - ni.height // 2))
    c.alpha_composite(sil, (540 - ni.width // 2, 640 - ni.height // 2))
    rayos(c, 540, 1080, (255, 170, 110), 9, 30, 1.6, -math.pi / 2)
    polvo(c, 2, (255, 200, 170))
    titulo(c, "PERSIANA ABAJO", (255, 240, 225), (255, 120, 80), RED)
    chip(c, 2, YEL); acabado(c, 2); return c

def p3():
    c = lienzo("bg_poligono", 1.5, .5, .5, 170); grade(c, (5, 25, 50), (60, 40, 10), 100)
    numero(c, 3, CYAN)
    glow(c, [((120, 260, 960, 1000), (255, 200, 110, 120))])
    rayos(c, 540, 330, (255, 220, 150), 12, 26, 6.2, 0)
    lay = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    s, ox, oy = 1.05, 540, 690
    def T_(x, y): return (ox + (x - 540) * s, oy + (y - 880) * s)
    kv = ep3.llave_v(.55); kv = kv.resize((int(kv.width * s * .62), int(kv.height * s * .62)))
    kv = kv.rotate(8, resample=Image.BICUBIC, expand=True)
    lay.alpha_composite(kv, (int(ox - kv.width / 2 + 14), int(T_(0, 960)[1])))
    up = 80; a0 = T_(395, 480 - up); a1 = T_(685, 820 - up)
    d.arc((a0[0], a0[1], a1[0], a1[1]), 180, 360, fill=OL, width=int(62 * s)); d.arc((a0[0] + 4, a0[1] + 4, a1[0] - 4, a1[1] - 4), 180, 360, fill=(200, 206, 220), width=int(50 * s))
    for x in (424, 656):
        p0 = T_(x, 650 - up); p1_ = T_(x, 740 if x == 656 else 650 - up + 60)
        d.line((p0[0], p0[1], p1_[0], p1_[1]), fill=OL, width=int(60 * s)); d.line((p0[0], p0[1], p1_[0], p1_[1]), fill=(200, 206, 220), width=int(48 * s))
    b0 = T_(340, 720); b1 = T_(740, 1080)
    d.rounded_rectangle((b0[0], b0[1], b1[0], b1[1]), int(46 * s), fill=(220, 178, 78), outline=OL, width=10)
    d.rounded_rectangle((b0[0] + 24, b0[1] + 20, b0[0] + 70, b1[1] - 30), 20, fill=(245, 215, 140))
    text(d, T_(560, 900), "7", int(140 * s), (150, 110, 35))
    c.alpha_composite(lay)
    ep3.ep_chispas(c, .25, 0, ox - 120, T_(0, 640)[1], n=40, dur=.6)
    ep3.ep_chispas(c, .18, 0, ox + 110, T_(0, 640)[1], n=30, dur=.5)
    polvo(c, 3, (255, 230, 170))
    titulo(c, "NAVE 7", (255, 250, 230), (255, 190, 80), (255, 170, 60))
    chip(c, 3, YEL); acabado(c, 3); return c

if __name__ == "__main__":
    outs = []
    for n, f in ((1, p1), (2, p2), (3, p3)):
        p = os.path.join(r.HERE, f"portada_pro_parte{n}.jpg"); f().convert("RGB").save(p, quality=94); outs.append(p)
    grid = Image.new("RGB", (3 * 360 + 8, 480), (255, 255, 255))
    for i, p in enumerate(reversed(outs)): grid.paste(Image.open(p).resize((360, 480)), (i * 364, 0))
    grid.save(os.path.join(r.HERE, "perfil_ejemplo_pro.jpg"), quality=92)
    print("ok")
