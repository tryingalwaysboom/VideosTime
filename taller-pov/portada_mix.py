"""Portadas mezcla: plantilla fija (neón arriba + PARTE N) y la imagen central cambia con el momento clave de cada parte."""
import os, math
import ep3
import portada as P
from luces import coche_faros
r = ep3.R
from render import Image, ImageDraw, ImageFilter, W, H, bg, put, dark, scaled, text, CYAN, MAG, OL

def glow(c, boxes):
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(gl)
    for b, col in boxes: g.ellipse(b, fill=col)
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(70)))

def centro1(c):   # Parte 1: el deportivo del tío bajo la lona, a medio destapar
    c.alpha_composite(bg("bg_taller", 0, 0, 1.25, 1.25, 1, .5, .62)); dark(c, 120)
    glow(c, [((-100, 1020, 1180, 1520), MAG + (95,)), ((200, 700, 880, 1100), CYAN + (50,))])
    P._suelo_reflejo(c, "deportivo", 540, 990, .78)
    put(c, "lona", 700, 960, .62, rot=-6)
    sp = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sp).polygon([(440, 760), (640, 760), (900, 1180), (180, 1180)], fill=(255, 240, 200, 45))
    c.alpha_composite(sp.filter(ImageFilter.GaussianBlur(20)))

def centro2(c):   # Parte 2: la persiana bajando delante de Nitro
    c.alpha_composite(bg("bg_fachada", 0, 0, 1.25, 1.25, 1, .5, .66)); dark(c, 60)
    inner = bg("bg_taller", 0, 0, 1.4, 1.4, 1, .5, .6).crop((150, 830, 930, 1400)); dark(inner, 60)
    put(inner, "deportivo", 390, 420, .55)
    pers = scaled("persiana", 1.0); h = int(570 * .55)
    inner.alpha_composite(pers.crop((0, 570 - h, 780, 570)), (0, 0))
    c.alpha_composite(inner.resize((int(780 * .78), int(570 * .78))), (540 - int(390 * .78), 790))
    glow(c, [((-100, 1100, 1180, 1500), MAG + (80,))])
    put(c, "nitro", 910, 1100, .42)
    put(c, "coche_negro", 215, 1150, .38)

def centro3(c):   # Parte 3: los faros de Nitro en el polígono, delante de la Nave 7
    c.alpha_composite(bg("bg_poligono", 0, 0, 1.3, 1.3, 1, .5, .62)); dark(c, 90)
    coche_faros(c, 640, 1060, .85, 1.0, largo=760)
    glow(c, [((-100, 1150, 1180, 1500), CYAN + (70,))])


def centro3_candado(c):   # Parte 3 (A: ir a la Nave 7): el candado abriéndose con la llave
    c.alpha_composite(bg("bg_poligono", 0, 0, 1.45, 1.45, 1, .5, .55)); dark(c, 150)
    glow(c, [((140, 700, 940, 1250), (255, 210, 120, 90)), ((-100, 1150, 1180, 1500), MAG + (60,))])
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    s = .55; ox, oy = 540, 960
    def T_(x, y): return (ox + (x - 540) * s, oy + (y - 880) * s)
    kv = ep3.llave_v(.6); kv = kv.resize((int(kv.width * s * .8), int(kv.height * s * .8)))
    lay.alpha_composite(kv, (int(ox - kv.width / 2), int(T_(0, 900)[1])))
    up = 70; a0 = T_(395, 480 - up); a1 = T_(685, 820 - up)
    d.arc((a0[0], a0[1], a1[0], a1[1]), 180, 360, fill=OL, width=int(62 * s)); d.arc((a0[0] + 3, a0[1] + 3, a1[0] - 3, a1[1] - 3), 180, 360, fill=(190, 196, 210), width=int(50 * s))
    for x in (424, 656):
        p0 = T_(x, 650 - up); p1 = T_(x, 740)
        d.line((p0[0], p0[1], p1[0], p1[1]), fill=OL, width=int(60 * s)); d.line((p0[0], p0[1], p1[0], p1[1]), fill=(190, 196, 210), width=int(48 * s))
    b0 = T_(340, 720); b1 = T_(740, 1080)
    d.rounded_rectangle((b0[0], b0[1], b1[0], b1[1]), int(46 * s), fill=(214, 172, 74), outline=OL, width=8)
    text(d, T_(560, 880), "7", int(120 * s), (150, 110, 35))
    c.alpha_composite(lay)
    ep3.ep_chispas(c, .2, 0, ox, T_(0, 690)[1], n=30, dur=.5)

def centro3_linterna(c):   # Parte 3: la linterna descubre los planos del deportivo
    c.alpha_composite(bg("bg_nave7", 0, 0, 1.6, 1.6, 1, .25, .02))
    ep3.linterna(c, 560, 1000, 280, 225)

def portada_mix(n, centro, out, titulo=True):
    c = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    centro(c)
    if titulo: P._neon_titulo(c, 640)
    P._parte_n(c, n, 1290)
    c.alpha_composite(r.VIG); c.convert("RGB").save(out, quality=94); P.a_34(out)

if __name__ == "__main__":
    for n, f in ((1, centro1), (2, centro2), (3, centro3)):
        portada_mix(n, f, os.path.join(r.HERE, f"portada_mix_parte{n}.jpg"))
    ims = [Image.open(os.path.join(r.HERE, f"portada_mix_parte{n}.jpg")) for n in (3, 2, 1)]
    grid = Image.new("RGB", (3 * 360 + 8, 480), (255, 255, 255))
    for i, im in enumerate(ims): grid.paste(im.resize((360, 480)), (i * 364, 0))
    grid.save(os.path.join(r.HERE, "perfil_ejemplo_mix.jpg"), quality=92)
    print("ok")
