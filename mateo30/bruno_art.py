"""Bruno (compañero de clase de Mateo): personaje propio de la temporada, dibujado por código.
Grandote, cabeza ancha, pelo rubio de punta, orejas salidas, curita en la mejilla, le falta un diente, suéter morado de rayas.
Genera layers/bruno_{burlon,rie,rie2}.png (1600x3800, cabeza centrada en (800, 904) como las capas de Mateo)."""
import os, math
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
OL = (29, 22, 48); PIEL = (250, 214, 182); PIEL2 = (232, 186, 150); PELO = (244, 202, 78); PELO2 = (212, 160, 48); CEJA = (150, 104, 28)
SUE = (126, 87, 194); SUE2 = (96, 62, 160); RAYA = (255, 212, 84); BOCA = (130, 28, 48); LEN = (240, 120, 140); BL = (255, 253, 244)
CX, CY = 800, 904; LW = 13
def dibuja(kind):
    im = Image.new("RGBA", (1600, 3800), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # cuerpo: suéter ancho de rayas
    d.rounded_rectangle((CX - 400, 1250, CX + 400, 3900), 150, fill=SUE, outline=OL, width=LW)
    for y in range(1500, 3800, 260): d.rectangle((CX - 394, y, CX + 394, y + 90), fill=RAYA)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((CX + 240, 1262, CX + 388, 3900), 120, fill=(40, 20, 80, 60)); im.alpha_composite(sh); d = ImageDraw.Draw(im)
    d.rounded_rectangle((CX - 400, 1250, CX + 400, 3900), 150, outline=OL, width=LW)
    for sx in (-1, 1):   # brazos pegados al cuerpo y manos
        d.rounded_rectangle((CX + sx * 400 - 95, 1330, CX + sx * 400 + 95, 2250), 95, fill=SUE2 if sx > 0 else SUE, outline=OL, width=LW)
        d.rounded_rectangle((CX + sx * 400 - 95, 2150, CX + sx * 400 + 95, 2250), 30, fill=RAYA, outline=OL, width=LW)
        d.ellipse((CX + sx * 400 - 78, 2230, CX + sx * 400 + 78, 2386), fill=PIEL, outline=OL, width=LW)
    d.rounded_rectangle((CX - 95, 1100, CX + 95, 1300), 40, fill=PIEL2, outline=OL, width=LW)          # cuello
    d.chord((CX - 210, 1160, CX + 210, 1400), 0, 180, fill=RAYA, outline=OL, width=LW)                   # cuello del suéter
    # orejas salidas
    for sx in (-1, 1):
        d.ellipse((CX + sx * 300 - 72, CY - 60, CX + sx * 300 + 72, CY + 110), fill=PIEL, outline=OL, width=LW)
        d.arc((CX + sx * 300 - 34, CY - 14, CX + sx * 300 + 34, CY + 64), 90 if sx < 0 else 270, 270 if sx < 0 else 90, fill=PIEL2, width=10)
    # cabeza ancha, de mandíbula cuadrada
    d.rounded_rectangle((CX - 300, CY - 250, CX + 300, CY + 250), 190, fill=PIEL, outline=OL, width=LW)
    d = ImageDraw.Draw(im)
    # pelo rubio de punta (corte plano)
    P = [(CX - 306, CY - 70), (CX - 300, CY - 190), (CX - 250, CY - 330), (CX - 170, CY - 250), (CX - 120, CY - 380), (CX - 30, CY - 270), (CX + 30, CY - 400), (CX + 110, CY - 270),
         (CX + 180, CY - 370), (CX + 240, CY - 250), (CX + 310, CY - 300), (CX + 304, CY - 70), (CX + 250, CY - 150), (CX + 120, CY - 170), (CX - 40, CY - 150), (CX - 200, CY - 170)]
    d.polygon(P, fill=PELO); d.line(P + [P[0]], fill=OL, width=LW, joint="curve")
    d.polygon([(CX + 180, CY - 370), (CX + 240, CY - 250), (CX + 310, CY - 300), (CX + 304, CY - 70), (CX + 250, CY - 150), (CX + 200, CY - 160)], fill=PELO2); d.line([(CX + 180, CY - 370), (CX + 240, CY - 250), (CX + 310, CY - 300), (CX + 304, CY - 70), (CX + 250, CY - 150)], fill=OL, width=LW, joint="curve")
    # mejillas y curita
    ch = Image.new("RGBA", im.size, (0, 0, 0, 0)); dc = ImageDraw.Draw(ch)
    for sx in (-1, 1): dc.ellipse((CX + sx * 200 - 70, CY + 40, CX + sx * 200 + 70, CY + 120), fill=(240, 130, 130, 110))
    im.alpha_composite(ch)
    cur = Image.new("RGBA", (200, 90), (0, 0, 0, 0)); dq = ImageDraw.Draw(cur); dq.rounded_rectangle((4, 14, 196, 76), 30, fill=(240, 200, 150), outline=OL, width=9); dq.rectangle((76, 22, 124, 68), fill=(252, 232, 200))
    cur = cur.rotate(28, resample=Image.BICUBIC, expand=True); im.alpha_composite(cur, (CX + 120, CY + 20)); d = ImageDraw.Draw(im)
    # nariz chata
    d.ellipse((CX - 52, CY - 10, CX + 52, CY + 66), fill=PIEL2, outline=OL, width=11)
    for sx in (-1, 1): d.ellipse((CX + sx * 22 - 9, CY + 30, CX + sx * 22 + 9, CY + 48), fill=OL)
    ey = CY - 70
    if kind == "burlon":
        for sx in (-1, 1):
            x = CX + sx * 135; d.ellipse((x - 58, ey - 50, x + 58, ey + 50), fill=BL, outline=OL, width=11)
            d.ellipse((x - 58 + 6, ey - 16, x - 58 + 62, ey + 40), fill=OL); d.ellipse((x - 40, ey - 6, x - 26, ey + 8), fill=BL)       # mira de reojo, hacia Mateo
            d.chord((x - 60, ey - 54, x + 60, ey + 54), 180, 360, fill=PIEL2); d.line((x - 60, ey, x + 60, ey), fill=OL, width=11)                  # párpado a media asta
        d.line((CX - 205, ey - 92, CX - 70, ey - 62), fill=CEJA, width=30); d.line((CX + 70, ey - 100, CX + 205, ey - 130), fill=CEJA, width=30)   # una ceja baja y otra arriba
        d.arc((CX - 150, CY + 30, CX + 170, CY + 200), 20, 150, fill=OL, width=16); d.line((CX + 150, CY + 120, CX + 190, CY + 96), fill=OL, width=16)   # sonrisa torcida
        d.rectangle((CX - 20, CY + 186, CX + 22, CY + 226), fill=BL, outline=OL, width=8)
    else:
        for sx in (-1, 1):
            x = CX + sx * 135; d.arc((x - 62, ey - 30, x + 62, ey + 70), 190, 350, fill=OL, width=17)                                                 # ojos cerrados de risa
        d.line((CX - 205, ey - 120, CX - 70, ey - 96), fill=CEJA, width=30); d.line((CX + 70, ey - 96, CX + 205, ey - 120), fill=CEJA, width=30)
        h = 150 if kind == "rie" else 84
        d.chord((CX - 170, CY + 110 - h, CX + 170, CY + 110 + h), 0, 180, fill=BOCA, outline=OL, width=LW); d.line((CX - 170, CY + 110, CX + 170, CY + 110), fill=OL, width=LW)
        if kind == "rie": d.chord((CX - 80, CY + 190, CX + 80, CY + 300), 180, 360, fill=LEN)
        for x0, x1 in ((-120, -48), (-40, 30), (104, 150)): d.rectangle((CX + x0, CY + 116, CX + x1, CY + 116 + (46 if kind == "rie" else 34)), fill=BL, outline=OL, width=7)   # le falta un diente
        d.chord((CX - 170, CY + 110 - h, CX + 170, CY + 110 + h), 0, 180, outline=OL, width=LW)
    im.save(os.path.join(HERE, "layers", f"bruno_{kind}.png"))
    return im
if __name__ == "__main__":
    S = Image.new("RGB", (1200, 700), (90, 90, 90))
    for i, k in enumerate(("burlon", "rie", "rie2")):
        t = dibuja(k).crop((200, 400, 1400, 1800)).resize((400, 467)); S.paste(t, (i * 400, 0), t)
    m = Image.open(os.path.join(HERE, "layers", "mateo_triste.png")).crop((200, 400, 1400, 1100)).resize((400, 233)); S.paste(m, (0, 467), m)
    S.save("/tmp/bruno.jpg", quality=88)
