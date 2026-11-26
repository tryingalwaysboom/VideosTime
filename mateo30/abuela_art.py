"""La abuela Pilar: personaje propio de la temporada, dibujado por código.
Cara redonda, moño gris, gafas redondas, chal lila sobre vestido verde agua, collar de perlas.
Genera layers/abuela_{sonrie,habla,habla2,sorpresa,guino}.png (1600x3800, cabeza centrada en (800, 904))."""
import os
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
OL = (29, 22, 48); PIEL = (240, 196, 164); PIEL2 = (218, 168, 136); PELO = (214, 214, 226); PELO2 = (176, 178, 198)
VEST = (98, 178, 170); CHAL = (190, 150, 214); CHAL2 = (158, 116, 190); BL = (255, 253, 244); BOCA = (150, 50, 70); LAB = (206, 96, 110)
CX, CY = 800, 904; LW = 13
def dibuja(kind):
    im = Image.new("RGBA", (1600, 3800), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # moño (detrás de la cabeza)
    d.ellipse((CX - 130, CY - 470, CX + 130, CY - 230), fill=PELO, outline=OL, width=LW); d.arc((CX - 80, CY - 430, CX + 80, CY - 290), 200, 340, fill=PELO2, width=12)
    # cuerpo: vestido y chal
    d.rounded_rectangle((CX - 430, 1260, CX + 430, 3900), 190, fill=VEST, outline=OL, width=LW)
    for sx in (-1, 1):
        d.rounded_rectangle((CX + sx * 430 - 100, 1360, CX + sx * 430 + 100, 2300), 100, fill=CHAL2 if sx > 0 else CHAL, outline=OL, width=LW)
        d.ellipse((CX + sx * 430 - 80, 2260, CX + sx * 430 + 80, 2420), fill=PIEL, outline=OL, width=LW)
    P = [(CX - 440, 1300), (CX - 120, 1210), (CX, 1420), (CX + 120, 1210), (CX + 440, 1300), (CX + 470, 1900), (CX + 120, 2080), (CX, 1760), (CX - 120, 2080), (CX - 470, 1900)]
    d.polygon(P, fill=CHAL); d.line(P + [P[0]], fill=OL, width=LW, joint="curve")
    for i in range(9):   # flecos
        for sx in (-1, 1): x = CX + sx * (150 + i * 38); y = 2070 - i * 21; d.line((x, y, x, y + 70), fill=CHAL2, width=12)
    d.rounded_rectangle((CX - 90, 1090, CX + 90, 1290), 40, fill=PIEL2, outline=OL, width=LW)
    for i in range(-4, 5): x = CX + i * 34; y = 1262 + (16 - i * i) * 3; d.ellipse((x - 19, y - 19, x + 19, y + 19), fill=BL, outline=OL, width=6)   # perlas
    # orejas con pendiente
    for sx in (-1, 1):
        d.ellipse((CX + sx * 285 - 52, CY - 30, CX + sx * 285 + 52, CY + 100), fill=PIEL, outline=OL, width=LW); d.ellipse((CX + sx * 292 - 17, CY + 96, CX + sx * 292 + 17, CY + 130), fill=BL, outline=OL, width=6)
    # cara redonda
    d.ellipse((CX - 285, CY - 265, CX + 285, CY + 275), fill=PIEL, outline=OL, width=LW)
    # pelo gris: flequillo ondulado partido al medio
    P = [(CX - 292, CY - 20), (CX - 300, CY - 170), (CX - 190, CY - 290), (CX, CY - 320), (CX + 190, CY - 290), (CX + 300, CY - 170), (CX + 292, CY - 20),
         (CX + 230, CY - 120), (CX + 120, CY - 190), (CX, CY - 150), (CX - 120, CY - 190), (CX - 230, CY - 120)]
    d.polygon(P, fill=PELO); d.line(P + [P[0]], fill=OL, width=LW, joint="curve"); d.line((CX, CY - 318, CX, CY - 156), fill=PELO2, width=10)
    for sx in (-1, 1): d.arc((CX + sx * 150 - 110, CY - 300, CX + sx * 150 + 110, CY - 120), 200 if sx < 0 else 250, 290 if sx < 0 else 340, fill=PELO2, width=10)
    # mejillas
    ch = Image.new("RGBA", im.size, (0, 0, 0, 0)); dc = ImageDraw.Draw(ch)
    for sx in (-1, 1): dc.ellipse((CX + sx * 180 - 74, CY + 50, CX + sx * 180 + 74, CY + 140), fill=(236, 120, 130, 120))
    im.alpha_composite(ch); d = ImageDraw.Draw(im)
    ey = CY - 30
    # ojos
    for sx in (-1, 1):
        x = CX + sx * 125
        if kind == "guino" and sx > 0: d.arc((x - 50, ey - 14, x + 50, ey + 50), 200, 340, fill=OL, width=16)
        elif kind == "sorpresa": d.ellipse((x - 44, ey - 50, x + 44, ey + 50), fill=BL, outline=OL, width=10); d.ellipse((x - 18, ey - 18, x + 18, ey + 18), fill=OL)
        else: d.arc((x - 50, ey - 22, x + 50, ey + 56), 200, 340, fill=OL, width=16) if kind in ("sonrie", "habla", "habla2") else (d.ellipse((x - 30, ey - 30, x + 30, ey + 30), fill=OL), d.ellipse((x - 16, ey - 20, x - 2, ey - 6), fill=BL))
        d.arc((x + sx * 40 - 30, ey + 10, x + sx * 40 + 30, ey + 50), 20 if sx > 0 else 100, 80 if sx > 0 else 160, fill=PIEL2, width=7)   # patas de gallo
    # cejas grises
    up = 34 if kind == "sorpresa" else 0
    for sx in (-1, 1): d.arc((CX + sx * 125 - 70, ey - 120 - up, CX + sx * 125 + 70, ey - 40 - up), 200, 340, fill=PELO2, width=18)
    # gafas redondas
    for sx in (-1, 1): d.ellipse((CX + sx * 125 - 98, ey - 92, CX + sx * 125 + 98, ey + 104), outline=(170, 60, 80), width=15)
    d.line((CX - 28, ey - 4, CX + 28, ey - 4), fill=(170, 60, 80), width=15)
    for sx in (-1, 1): d.line((CX + sx * 222, ey - 10, CX + sx * 282, ey - 30), fill=(170, 60, 80), width=13)
    # nariz y boca
    d.arc((CX - 34, CY + 40, CX + 34, CY + 100), 20, 160, fill=PIEL2, width=11)
    if kind in ("sonrie", "guino"): d.arc((CX - 120, CY + 60, CX + 120, CY + 210), 25, 155, fill=OL, width=16); d.arc((CX - 60, CY + 150, CX + 60, CY + 220), 30, 150, fill=LAB, width=10)
    elif kind == "sorpresa": d.ellipse((CX - 46, CY + 130, CX + 46, CY + 216), fill=BOCA, outline=OL, width=11)
    else:
        h = 78 if kind == "habla" else 40
        d.chord((CX - 100, CY + 150 - h, CX + 100, CY + 150 + h), 0, 180, fill=BOCA, outline=OL, width=11); d.line((CX - 100, CY + 150, CX + 100, CY + 150), fill=OL, width=11)
        d.rectangle((CX - 60, CY + 156, CX + 60, CY + 156 + (24 if kind == "habla" else 14)), fill=BL)
    for sx in (-1, 1): d.arc((CX + sx * 150 - 26, CY + 110, CX + sx * 150 + 26, CY + 190), 300 if sx < 0 else 180, 60 if sx < 0 else 240, fill=PIEL2, width=7)   # arruguitas de la sonrisa
    im.save(os.path.join(HERE, "layers", f"abuela_{kind}.png")); return im
if __name__ == "__main__":
    K = ("sonrie", "habla", "habla2", "sorpresa", "guino"); S = Image.new("RGB", (2000, 500), (90, 90, 90))
    for i, k in enumerate(K):
        t = dibuja(k).crop((200, 300, 1400, 1800)).resize((400, 500)); S.paste(t, (i * 400, 0), t)
    S.save("/tmp/abuela.jpg", quality=88)
