"""Portadas propias de la serie Mateo, estilo CUADERNO ESCOLAR (distinto del taller): hoja de cuaderno con renglones,
foto pegada con cinta de la escena de la opción que ganó, título escrito con crayola como lo escribiría Mateo y
etiqueta escolar "PARTE N". Se compone en 9:16 (1080x1920); el diseño cabe en el 3:4 central (subido)."""
import os, sys, math, random
import numpy as np
import render3 as V
from render3 import nino_trazos, ancho_nino
from render2 import Image, ImageDraw, ImageFilter, put, bg, font, F_ESC, F_BAL, F_HAND, OL, palabra_trazos, dibuja_trazos, rex_nino_trazos

CW, CH = 1080, 1920
OY = 160            # arriba del 3:4 que enseña la cuadrícula del perfil
PAPEL = (251, 247, 236); AZUL = (150, 185, 225); ROJO_M = (226, 120, 120); NAVY = (44, 36, 78)

def cuaderno():
    c = Image.new("RGBA", (CW, CH), PAPEL + (255,)); d = ImageDraw.Draw(c)
    rnd = np.random.default_rng(3)   # grano del papel
    g = Image.fromarray((rnd.random((CH, CW)) * 18).astype(np.uint8)); sh = Image.new("RGBA", (CW, CH), (120, 100, 70, 255)); sh.putalpha(g)
    c.alpha_composite(sh)
    for y in range(140, CH, 64): d.line((0, y, CW, y), fill=AZUL, width=3)
    d.line((128, 0, 128, CH), fill=ROJO_M, width=4); d.line((136, 0, 136, CH), fill=ROJO_M, width=2)
    for y in range(90, CH, 170):   # agujeros de la espiral
        d.ellipse((34, y, 74, y + 40), fill=(225, 218, 200)); d.ellipse((38, y + 4, 70, y + 36), fill=(205, 196, 176))
    return c

def cinta(c, cx, cy, w, rot, col):
    t = Image.new("RGBA", (w, 70), col + (170,)); td = ImageDraw.Draw(t)
    for x in range(0, w, 14): td.line((x, 0, x + 10, 70), fill=(255, 255, 255, 40), width=4)
    t = t.rotate(rot, expand=True, resample=Image.BICUBIC)
    c.alpha_composite(t, (int(cx - t.width / 2), int(cy - t.height / 2)))

def foto(c, escena, cx, cy, w, h, rot):
    """Foto tipo instantánea pegada en la hoja, con sombra."""
    marco = Image.new("RGBA", (w + 60, h + 150), (255, 255, 255, 255))
    marco.paste(escena.resize((w, h), Image.LANCZOS), (30, 30))
    ImageDraw.Draw(marco).rectangle((0, 0, marco.width - 1, marco.height - 1), outline=(220, 214, 200), width=3)
    m = marco.rotate(rot, expand=True, resample=Image.BICUBIC)
    sombra = Image.new("RGBA", m.size, (60, 40, 20, 0)); sombra.putalpha(m.getchannel("A").point(lambda v: int(v * .35)))
    c.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(18)), (int(cx - m.width / 2 + 14), int(cy - m.height / 2 + 22)))
    c.alpha_composite(m, (int(cx - m.width / 2), int(cy - m.height / 2)))
    return m.size

def garabatos(c, seed):
    d = ImageDraw.Draw(c); r = random.Random(seed)
    cols = [(244, 196, 48), (232, 110, 140), (90, 160, 230), (63, 174, 74)]
    sitios = [(210, OY + 60), (930, OY + 70), (985, OY + 1000), (205, OY + 1120), (870, OY + 1330), (230, OY + 1330)]
    for i, (x, y) in enumerate(sitios):
        col = cols[i % 4]; k = r.choice(["estrella", "corazon", "espiral"])
        if k == "estrella":
            pts = [(x + 34 * math.cos(math.radians(-90 + j * 36)) * (1 if j % 2 == 0 else .45), y + 34 * math.sin(math.radians(-90 + j * 36)) * (1 if j % 2 == 0 else .45)) for j in range(11)]
            d.line(pts, fill=col, width=7, joint="curve")
        elif k == "corazon":
            pts = [(x + 26 * 16 * math.sin(t) ** 3 / 16, y - 26 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16) for t in np.linspace(0, 2 * math.pi, 40)]
            d.line(pts, fill=col, width=7, joint="curve")
        else:
            pts = [(x + 4 * t * math.cos(t), y + 4 * t * math.sin(t)) for t in np.linspace(0, 12, 60)]
            d.line(pts, fill=col, width=6, joint="curve")

def etiqueta_parte(c, n, cx, cy, rot=-4):
    """Etiqueta escolar de nombre, como las del cuaderno: borde rojo y 'PARTE N' con letra de escuela."""
    w, h = 470, 140
    e = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(e)
    d.rounded_rectangle((10, 10, w + 10, h + 10), 34, fill=(255, 255, 255), outline=(214, 70, 80), width=8)
    d.rounded_rectangle((26, 26, w - 6, h - 6), 24, outline=(214, 70, 80), width=3)
    d.text((w / 2 + 10, h / 2 + 12), f"PARTE {n}", font=font(F_ESC, 92), fill=NAVY, anchor="mm")
    e = e.rotate(rot, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", e.size, (60, 40, 20, 0)); sh.putalpha(e.getchannel("A").point(lambda v: int(v * .3)))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (int(cx - e.width / 2 + 8), int(cy - e.height / 2 + 12)))
    c.alpha_composite(e, (int(cx - e.width / 2), int(cy - e.height / 2)))

def escena_p2():
    """La escena dentro de la foto: Mateo feliz con la crayola verde y su Rex, en la cocina."""
    s = bg("bg_cocina", 0, 0, 1.15, 1.15, 1, .5, .55)
    put(s, "mateo_feliz_crayola", 430, 860 + 400 * 1.05, 1.05)
    put(s, "dino", 840, 1250, .62, rot=6)
    return s.crop((0, 380, 1080, 1460))   # 1080x1080

def p2():
    c = cuaderno()
    garabatos(c, 2)
    cx, cy = 560, OY + 480
    foto(c, escena_p2(), cx, cy, 680, 680, -3)
    cinta(c, cx - 275, cy - 395, 210, 30, (244, 196, 48)); cinta(c, cx + 285, cy - 382, 210, -28, (232, 110, 140))
    # título: "se llama" a mano y REX enorme con crayola, escrito como Mateo (E de 4 rayitas, X chueca y cola)
    d = ImageDraw.Draw(c)
    d.text((540, OY + 945), "se llama...", font=font(F_HAND, 110), fill=NAVY, anchor="mm")
    sz = 190; rex = rex_nino_trazos(540 - 1.31 * sz, OY + 1010, sz)
    sombra = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); dibuja_trazos(sombra, [p for L in rex for p in L], sz * .13, (20, 70, 30))
    c.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(2)), (6, 8))
    dibuja_trazos(c, [p for L in rex for p in L], sz * .13, (58, 168, 72))
    etiqueta_parte(c, 2, 540, OY + 1340, -3)
    return c

def escena_p3():
    """Noche 3: Mateo feliz enseñando la hoja con su nombre (la E al revés)."""
    s = bg("bg_cocina", 0, 0, 1.15, 1.15, 1, .5, .55)
    put(s, "mateo_feliz", 540, 980 + 400 * 1.0, 1.0)
    lay = Image.new("RGBA", s.size, (0, 0, 0, 0)); put(lay, "hoja", 540, 1290, .7)
    tr = nino_trazos("MATEO", 540 - ancho_nino("MATEO", 115) / 2, 1175, 115, erev=True, seed=1)
    dibuja_trazos(lay, [p for L in tr for p in L], 11.5, (58, 168, 72))
    s.alpha_composite(lay.rotate(-4, center=(540, 1290), resample=Image.BICUBIC))
    put(s, "dino", 900, 1300, .5, rot=8)
    return s.crop((0, 380, 1080, 1460))

def p3():
    c = cuaderno()
    garabatos(c, 3)
    cx, cy = 540, OY + 480
    foto(c, escena_p3(), cx, cy, 680, 680, 3)
    cinta(c, cx - 285, cy - 382, 210, 28, (120, 200, 230)); cinta(c, cx + 275, cy - 395, 210, -30, (244, 196, 48))
    d = ImageDraw.Draw(c)
    d.text((540, OY + 945), "por fin escribe...", font=font(F_HAND, 100), fill=NAVY, anchor="mm")
    sz = 150; tr = nino_trazos("MATEO", 540 - ancho_nino("MATEO", sz) / 2, OY + 1015, sz, erev=True, seed=1)
    sombra = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); dibuja_trazos(sombra, [p for L in tr for p in L], sz * .13, (20, 70, 30))
    c.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(2)), (6, 8))
    dibuja_trazos(c, [p for L in tr for p in L], sz * .13, (58, 168, 72))
    etiqueta_parte(c, 3, 540, OY + 1340, 3)
    return c

def escena_p4():
    """Ganó dejarlo así: su MATEO con la E al revés, con la estrella de la maestra y Mateo feliz delante."""
    import render4 as R4
    s = R4.pared_expo(0, False)
    s = R4.seguir(s, 600, 1080, 1.6, f=1.0)
    R4.estrella(ImageDraw.Draw(s), 680, 1015, 70)
    put(s, "mateo_feliz", 830, 1440 + 400 * .62, .62)
    return s.crop((0, 600, 1080, 1680))

def p4():
    c = cuaderno()
    garabatos(c, 4)
    cx, cy = 540, OY + 480
    foto(c, escena_p4(), cx, cy, 680, 680, -2)
    cinta(c, cx - 285, cy - 382, 210, 28, (232, 110, 140)); cinta(c, cx + 275, cy - 395, 210, -30, (120, 200, 230))
    d = ImageDraw.Draw(c)
    d.text((540, OY + 955), "así está...", font=font(F_HAND, 110), fill=NAVY, anchor="mm")
    d.text((546, OY + 1101), "¡perfecto!", font=font(F_HAND, 170), fill=(20, 70, 30), anchor="mm")
    d.text((540, OY + 1095), "¡perfecto!", font=font(F_HAND, 170), fill=(58, 168, 72), anchor="mm")
    etiqueta_parte(c, 4, 540, OY + 1340, -3)
    return c

def escena_p5():
    """Ganó el premio sin pantallas: el buzón de Rex con la carta saliendo y Mateo feliz."""
    import render5 as R5
    s = bg("bg_cocina", 0, 0, 1.15, 1.15, 1, .5, .55).convert("RGBA")
    s.alpha_composite(Image.new("RGBA", s.size, (255, 220, 160, 40)))
    put(s, "mateo_feliz", 330, 1000 + 400 * .95, .95)
    R5.buzon(s, 780, 1330, .8, 0)
    R5.sobre(s, 800, 1050, .9, rot=10)
    return s.crop((0, 380, 1080, 1460))

def p5():
    c = cuaderno()
    garabatos(c, 5)
    cx, cy = 540, OY + 480
    foto(c, escena_p5(), cx, cy, 680, 680, 2)
    cinta(c, cx - 285, cy - 382, 210, 28, (244, 196, 48)); cinta(c, cx + 275, cy - 395, 210, -30, (120, 200, 230))
    d = ImageDraw.Draw(c)
    d.text((540, OY + 945), "el buzón de...", font=font(F_HAND, 110), fill=NAVY, anchor="mm")
    sz = 170; tr = nino_trazos("REX", 540 - ancho_nino("REX", sz) / 2, OY + 1010, sz, seed=4)
    sombra = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); dibuja_trazos(sombra, [p for L in tr for p in L], sz * .13, (20, 70, 30))
    c.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(2)), (6, 8))
    dibuja_trazos(c, [p for L in tr for p in L], sz * .13, (58, 168, 72))
    etiqueta_parte(c, 5, 540, OY + 1340, 3)
    return c

def escena_p6():
    """Ganó seguir con la magia de Rex: Mateo en la mesa junto a Rex (formato apaisado)."""
    import render5 as R5
    s = bg("bg_cocina", 0, 0, 1.15, 1.15, 1, .5, .55).convert("RGBA")
    s.alpha_composite(Image.new("RGBA", s.size, (255, 220, 160, 40)))
    d = ImageDraw.Draw(s)
    for x in (330, 800):
        d.rounded_rectangle((x - 110, 930, x + 110, 1290), 26, fill=(176, 120, 72), outline=OL, width=6)
        d.rounded_rectangle((x - 80, 960, x + 80, 1260), 18, fill=(196, 140, 90))
    put(s, "dino", 800, 1180, .5)
    ml = Image.new("RGBA", s.size, (0, 0, 0, 0)); put(ml, "mateo_neutral_crayola", 330, 960 + 400 * .85, .85)
    ml.paste((0, 0, 0, 0), (0, 1290, s.width, s.height)); s.alpha_composite(ml)
    d = ImageDraw.Draw(s)
    d.rectangle((90, 1315, 130, 1760), fill=(170, 120, 72), outline=OL, width=6); d.rectangle((950, 1315, 990, 1760), fill=(170, 120, 72), outline=OL, width=6)
    d.rectangle((90, 1315, 990, 1400), fill=(190, 138, 84), outline=OL, width=6)
    d.rounded_rectangle((30, 1250, 1050, 1320), 18, fill=(214, 160, 100), outline=OL, width=7)
    return s.crop((0, 470, 1080, 1440))

def p6():
    c = cuaderno()
    garabatos(c, 11)
    cx, cy = 540, OY + 480
    sc = escena_p6().crop((60, 0, 1020, 970))   # mesa con Mateo y Rex, casi cuadrada
    foto(c, sc, cx, cy, 680, 680, -2)
    cinta(c, cx - 290, cy - 385, 210, -26, (240, 150, 190)); cinta(c, cx + 285, cy - 392, 210, 24, (150, 210, 130))
    import render5 as R5
    R5.sobre(c, cx + 250, cy + 270, .55, rot=12)   # la carta de Rex pegada en la foto
    d = ImageDraw.Draw(c)
    d.text((540, OY + 945), "mi alumno se llama...", font=font(F_HAND, 100), fill=NAVY, anchor="mm")
    sz = 170; tr = nino_trazos("REX", 540 - ancho_nino("REX", sz) / 2, OY + 1010, sz, seed=9)
    sombra = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); dibuja_trazos(sombra, [p for L in tr for p in L], sz * .13, (20, 70, 30))
    c.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(2)), (6, 8))
    dibuja_trazos(c, [p for L in tr for p in L], sz * .13, (58, 168, 72))
    etiqueta_parte(c, 6, 540, OY + 1340, -3)
    return c

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    c = {2: p2, 3: p3, 4: p4, 5: p5, 6: p6}[n]().convert("RGB").filter(ImageFilter.UnsharpMask(1.0, 50, 2))
    c.save(os.path.join(V.HERE, f"portada_cuaderno_parte{n}_9x16.jpg"), quality=100, subsampling=0)
    c.crop((0, OY, CW, OY + 1440)).save(os.path.join(V.HERE, f"portada_cuaderno_parte{n}.jpg"), quality=95)
    print("ok")
