"""Portada pro Parte 10 "CARA A CARO": el padre de Lucía con sombrero, a contraluz rojo, frente a Nitro."""
import os, sys
import portada_pro as PP
import persp as P
from portada_pro import CW, CH, grade, glow, polvo, titulo, chip, bloom, acabado, a_916, r
from render import Image, ImageDraw, ImageFilter, YEL, WHITE, OL, dark
import render as R
from ep_comun import tinte
def glowc(c, box, col, a, blur=60):
    ov = Image.new('RGBA', c.size, (0,0,0,0)); ImageDraw.Draw(ov).ellipse(box, fill=col + (a,)); c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(blur)))
def sil(c, pr, name, x, z, alto, col=(4,4,8)):
    im = R.layer(name); im = im.crop(im.getbbox()); px, py, s = pr(x, z)
    h = int(alto * s); w = int(im.width * h / im.height); sp = im.resize((w, h), Image.LANCZOS)
    blk = Image.new('RGBA', sp.size, col + (255,)); blk.putalpha(sp.getchannel('A')); c.alpha_composite(blk, (int(px - w / 2), int(py - h * .96)))

def p10():
    c, pr = P.nave(0.0, hy=830, giro=0, cam_h=1.4, luz=1.0); c = c.convert("RGBA"); dark(c, 110)
    glowc(c, (60, 400, 1020, 1800), (255, 90, 70), 110, 110)
    sil(c, pr, "nitro_full", -.9, 3.0, 2.1)
    P.personaje(c, pr, "padre_full", .35, 3.3, 2.3, flip=True)
    c = c.crop((0, 240, 1080, 1680)).convert("RGBA")
    grade(c, (0, 20, 60), (110, 10, 20), 90)
    glow(c, [((300, 500, 780, 1000), (255, 150, 100, 110))], 80)
    polvo(c, 7, (255, 220, 190)); bloom(c)
    titulo(c, "CARA A CARA", (255, 255, 235), (255, 200, 60), (255, 70, 40))
    chip(c, 10, YEL); acabado(c, 10); return c

if __name__ == "__main__":
    p = os.path.join(r.HERE, "portada_pro_parte10.jpg")
    p10().convert("RGB").filter(ImageFilter.UnsharpMask(1.2, 60, 2)).save(p, quality=100, subsampling=0)
    a_916(p, "bg_nave7", .5, .8, os.path.join(r.HERE, "portada_pro_parte10_9x16.jpg")); print("ok")
