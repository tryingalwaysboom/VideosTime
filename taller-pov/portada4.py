"""Portada pro Parte 4 "CARA A CARA": Nitro iluminado delante de su coche negro de perfil, faro encendido; la foto de 1996."""
import os, math
import portada_pro as PP
from portada_pro import CW, CH, grade, glow, rayos, polvo, titulo, chip, bloom, acabado, a_916, r
from luces import coche_faros
from render import Image, ImageDraw, ImageFilter, put, scaled, bg, dark, YEL, RED, CYAN, MAG

def p4():
    full = bg("bg_poligono", 0, 0, 1.45, 1.45, 1, .5, .95).filter(ImageFilter.GaussianBlur(4)); dark(full, 150)
    ni = scaled("nitro", .88)   # detrás del coche: el coche le tapa la cintura
    rim = Image.new("RGBA", ni.size, (255, 236, 200, 255)); rim.putalpha(ni.getchannel("A").filter(ImageFilter.MaxFilter(11)))
    full.alpha_composite(rim.filter(ImageFilter.GaussianBlur(8)), (790 - ni.width // 2, 760 - ni.height // 2))
    full.alpha_composite(ni, (790 - ni.width // 2, 760 - ni.height // 2))
    coche_faros(full, 600, 1050, .85, 1.0, largo=900)          # de perfil: el haz sale del morro hacia la izquierda
    c = full.crop((0, 240, 1080, 1680))
    grade(c, (0, 30, 60), (60, 10, 30), 100)
    glow(c, [((-200, 760, 500, 1100), (255, 245, 210, 70))])
    fo = r.layer("foto_r96"); fo = fo.resize((int(fo.width * .26), int(fo.height * .26))).rotate(9, expand=True, resample=Image.BICUBIC)
    c.alpha_composite(fo, (70, 250))
    rayos(c, 130, 870, (255, 245, 215), 9, 22, 1.2, math.pi)
    polvo(c, 4, (255, 240, 220))
    bloom(c)
    titulo(c, "CARA A CARA", (255, 255, 255), (130, 230, 255), CYAN)
    chip(c, 4, YEL); acabado(c, 4); return c

if __name__ == "__main__":
    from PIL import ImageFilter as IF
    p = os.path.join(r.HERE, "portada_pro_parte4.jpg")
    p4().convert("RGB").filter(IF.UnsharpMask(1.2, 60, 2)).save(p, quality=100, subsampling=0)
    a_916(p, "bg_poligono", .5, .95, os.path.join(r.HERE, "portada_pro_parte4_9x16.jpg"))
    print("ok")
