"""Portada 9:16 del tip de las 3 frases (inspirada en la del zurdo, composición propia). Zona central 3:4 (x 90-990, y 300-1620)."""
import os
from PIL import Image, ImageDraw
import art as A
import render as R

def fit(txt, size, col, maxw=880):
    im = R._tit(txt, size, col)
    if im.width > maxw: im = im.resize((maxw, int(im.height * maxw / im.width)), Image.LANCZOS)
    return im

b = Image.new("RGB", (R.W, R.H)); R.bg(b, "durazno", 0)
R.put(b, fit("3 FRASES QUE", 175, (255, 255, 255)), 540, 400, 1, 0)
R.put(b, fit("APAGAN A TU HIJO", 175, A.AMA), 540, 590, 1, 0)
for i, (txt, x, rot) in enumerate((("Bórralo y hazlo\notra vez", 460, -3), ("Mira cómo escribe\ntu primo", 520, 3), ("¡Date prisa!\nQue no terminamos", 460, -2))):
    y = 822 + i * 192
    R.put(b, A.globo(txt, 46, (255, 255, 255), "left"), x, y, 1, rot)
    R.put(b, A.xmark(110), 940, y - 20, 1, 8)
R.put(b, A.nina("triste"), 540, 1625, .7, 0)
b.save(os.path.join(R.HERE, "portada_tip_frases_9x16.jpg"), quality=93)
