"""Portada 9:16 del tip de las 3 frases (mismo estilo que la del zurdo). Todo dentro de la zona central 3:4 (x 90-990, y 300-1620)."""
import os
from PIL import Image, ImageDraw
import art as A
import render as R

def fit(txt, size, col, maxw=880):
    im = R._tit(txt, size, col)
    if im.width > maxw: im = im.resize((maxw, int(im.height * maxw / im.width)), Image.LANCZOS)
    return im

b = Image.new("RGB", (R.W, R.H)); R.bg(b, "cielo", 0)
d = ImageDraw.Draw(b); d.rectangle((0, 1290, R.W, R.H), fill=(214, 150, 92)); d.rectangle((0, 1290, R.W, 1310), fill=(238, 184, 130)); d.line((0, 1290, R.W, 1290), fill=A.OL, width=7)
R.put(b, A.nina("triste"), 540, 1090, 1.1, 0)
R.put(b, fit("NO LE DIGAS", 175, (255, 255, 255)), 540, 440, 1, 0)
R.put(b, fit("ESTAS 3 FRASES", 175, A.AMA), 540, 640, 1, 0)
d.rounded_rectangle((100, 1330, 980, 1610), 40, fill=A.CREMA, outline=A.OL, width=9)
R.put(b, A.sello("APAGAN SUS GANAS", 820, 300, A.ROJO, 92), 540, 1470, .93, -3)
b.save(os.path.join(R.HERE, "portada_tip_frases_9x16.jpg"), quality=93)
