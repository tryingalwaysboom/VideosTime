"""Portada 9:16 del tip del zurdo. Todo dentro de la zona central 3:4 (x 90-990, y 300-1620), lo que TikTok deja ver en la cuadrícula."""
import os
from PIL import Image, ImageDraw
import art as A
import render as R

def main():
    b = Image.new("RGB", (R.W, R.H)); R.bg(b, "cielo", 0)
    d = ImageDraw.Draw(b); d.rectangle((0, 1290, R.W, R.H), fill=(214, 150, 92)); d.rectangle((0, 1290, R.W, 1310), fill=(238, 184, 130)); d.line((0, 1290, R.W, 1290), fill=A.OL, width=7)
    R.put(b, A.kid("feliz"), 540, 1010, 1.12, 0)
    R.put(b, A.texto("SI TU HIJO", 175, (255, 255, 255), 14), 540, 440, 1, 0)
    R.put(b, A.texto("ES ZURDO", 175, A.AMA, 14), 540, 630, 1, 0)
    d.rounded_rectangle((100, 1330, 980, 1610), 40, fill=A.CREMA, outline=A.OL, width=9)
    R.put(b, A.sello("NO HAGAS ESTO", 820, 300, A.ROJO, 128), 540, 1470, .93, -3)
    b.save(os.path.join(R.HERE, "portada_tip_zurdo_9x16.jpg"), quality=93)

main()
