"""Logos más originales (1080x1080, recorte circular) para la cuenta "El Pobre de Andorra". Dibujados a 2x."""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from logos import S, P, layer, blur, fondo, estrellas, cordillera, guardar, OUT
from art import font, F_ANTON

AZ, AM, RO = (16, 56, 160), (255, 204, 0), (210, 16, 52)   # colores de la bandera de Andorra
OL = (14, 12, 28)

def rotulo(im, l1, l2, y=880, c1=(255, 255, 255), c2=AM):
    d = ImageDraw.Draw(im)
    d.text((P(540), P(y)), l1, font=font(F_ANTON, P(62)), fill=c1, anchor="mm", stroke_width=P(5), stroke_fill=OL)
    d.text((P(540), P(y + 78)), l2, font=font(F_ANTON, P(84)), fill=c2, anchor="mm", stroke_width=P(6), stroke_fill=OL)

# ---------------------------------------------------------------- 1: la mascota — el chaval del gorro con los colores de Andorra, guiñando el ojo
im = fondo((120, 190, 255), (30, 80, 170), .5)
cordillera(im, 600, [((170, 196, 235), (255, 255, 255)), ((130, 160, 210), (246, 250, 255))], seed=4)
d = ImageDraw.Draw(im); SK, SKD = (242, 190, 132), (214, 150, 98)
d.polygon([(P(250), P(1080)), (P(300), P(800)), (P(780), P(800)), (P(830), P(1080))], fill=(70, 74, 92))                 # chaqueta
d.polygon([(P(470), P(830)), (P(520), P(830)), (P(500), P(900))], fill=(150, 150, 170))
d.rounded_rectangle((P(330), P(760), P(750), P(850)), P(40), fill=RO)                                                    # bufanda
d.rounded_rectangle((P(620), P(790), P(690), P(990)), P(26), fill=RO); d.line((P(630), P(960), P(680), P(960)), fill=AM, width=P(8))
d.ellipse((P(330), P(340), P(750), P(800)), fill=SK)                                                                      # cara
d.ellipse((P(305), P(540), P(365), P(630)), fill=SKD); d.ellipse((P(715), P(540), P(775), P(630)), fill=SKD)             # orejas
d.ellipse((P(380), P(620), P(450), P(670)), fill=(255, 150, 140)); d.ellipse((P(630), P(620), P(700), P(670)), fill=(255, 150, 140))   # mofletes del frío
d.ellipse((P(440), P(540), P(490), P(600)), fill=OL); d.ellipse((P(455), P(550), P(470), P(566)), fill=(255, 255, 255))   # ojo abierto
d.arc((P(585), P(545), P(655), P(600)), 200, 340, fill=OL, width=P(12))                                                   # ojo guiñado
d.chord((P(455), P(640), P(625), P(740)), 0, 180, fill=(110, 30, 30)); d.rectangle((P(470), P(690), P(610), P(704)), fill=(255, 255, 255))
d.rectangle((P(530), P(690), P(548), P(718)), fill=(110, 30, 30))                                                          # el diente que le falta
d.polygon([(P(530), P(590)), (P(510), P(640)), (P(548), P(642))], fill=SKD)
# gorro de lana con la bandera y pompón
gor = layer(); gd = ImageDraw.Draw(gor)
gd.rectangle((P(300), P(240), P(468), P(460)), fill=AZ); gd.rectangle((P(468), P(240), P(612), P(460)), fill=AM); gd.rectangle((P(612), P(240), P(780), P(460)), fill=RO)
mk = Image.new("L", (S, S), 0); ImageDraw.Draw(mk).chord((P(320), P(250), P(760), P(640)), 180, 360, fill=255)
gz = layer(); gz.paste(gor, (0, 0), mk); im.alpha_composite(gz); d = ImageDraw.Draw(im)
d.chord((P(320), P(250), P(760), P(640)), 180, 360, outline=OL, width=P(4))
d.rounded_rectangle((P(305), P(420), P(775), P(500)), P(30), fill=(240, 240, 248))
for x in range(330, 760, 34): d.line((P(x), P(430), P(x), P(490)), fill=(210, 214, 228), width=P(6))
d.ellipse((P(480), P(170), P(600), P(290)), fill=(250, 250, 255)); d.ellipse((P(505), P(195), P(545), P(235)), fill=(255, 255, 255))
# moneda con agujero (lo único que le queda)
d.ellipse((P(735), P(330), P(895), P(490)), fill=(255, 196, 56), outline=(190, 130, 30), width=P(8)); d.ellipse((P(800), P(395), P(830), P(425)), fill=(30, 80, 170))
d.text((P(815), P(455)), "50", font=font(F_ANTON, P(36)), fill=(120, 70, 10), anchor="mm")
rotulo(im, "EL POBRE DE", "ANDORRA")
guardar(im, "logo4_elpobredeandorra.png")

# ---------------------------------------------------------------- 2: corona de cartón con celo, nevada, sobre los Pirineos de noche (el "rey" sin dinero)
im = fondo((60, 50, 130), (8, 8, 30)); estrellas(im, 140, 600, 7)
cordillera(im, 640, [((50, 50, 110), (190, 190, 235)), ((28, 28, 70), (140, 140, 200))], seed=11)
g = layer(); ImageDraw.Draw(g).ellipse((P(250), P(180), P(830), P(720)), fill=(255, 190, 90, 120)); im.alpha_composite(blur(g, 60))
d = ImageDraw.Draw(im); cart, cartd = (198, 150, 96), (160, 116, 70)
pts = [(250, 650), (250, 330), (360, 470), (430, 260), (540, 450), (650, 260), (720, 470), (830, 330), (830, 650)]
d.polygon([(P(x), P(y + 16)) for x, y in pts], fill=(90, 60, 30))
d.polygon([(P(x), P(y)) for x, y in pts], fill=cart)
for x in range(270, 830, 40): d.line((P(x), P(520), P(x), P(645)), fill=cartd, width=P(4))                                 # cartón ondulado
d.rectangle((P(250), P(520), P(830), P(650)), outline=cartd, width=P(6))
d.polygon([(P(330), P(560)), (P(470), P(530)), (P(480), P(570)), (P(340), P(600))], fill=(236, 226, 190, 210))               # celo
d.polygon([(P(600), P(380)), (P(700), P(420)), (P(690), P(455)), (P(592), P(415))], fill=(236, 226, 190, 210))
for (x, y) in ((430, 260), (650, 260), (250, 330), (830, 330)):                                                            # nieve en las puntas
    d.ellipse((P(x - 34), P(y - 22), P(x + 34), P(y + 16)), fill=(250, 252, 255))
d.ellipse((P(500), P(540), P(580), P(620)), fill=AM); d.ellipse((P(515), P(555), P(565), P(605)), fill=RO)                 # "joya" = chapa de refresco
for k in range(12):
    a = k * math.pi / 6; d.line((P(540 + 40 * math.cos(a)), P(580 + 40 * math.sin(a)), P(540 + 48 * math.cos(a)), P(580 + 48 * math.sin(a))), fill=(200, 160, 20), width=P(5))
d.text((P(400), P(608)), "500€", font=font(F_ANTON, P(48)), fill=(110, 70, 30), anchor="mm")
rng = random.Random(2)
for _ in range(70):   # nevada
    x, y, r = rng.uniform(120, 960), rng.uniform(120, 800), rng.uniform(3, 7); d.ellipse((P(x - r), P(y - r), P(x + r), P(y + r)), fill=(255, 255, 255, 200))
rotulo(im, "EL POBRE DE", "ANDORRA")
guardar(im, "logo5_elpobredeandorra.png")

# ---------------------------------------------------------------- 3: telesilla subiendo con la maleta como único pasajero, al atardecer
im = fondo((255, 170, 110), (120, 40, 90), .45)
g = layer(); ImageDraw.Draw(g).ellipse((P(620), P(360), P(860), P(600)), fill=(255, 230, 160, 255)); im.alpha_composite(blur(g, 10))
cordillera(im, 680, [((200, 90, 120), (255, 226, 220)), ((140, 50, 90), (255, 200, 200))], seed=6)
d = ImageDraw.Draw(im)
d.line((P(80), P(330), P(1000), P(170)), fill=OL, width=P(8))                                                              # cable
cx, cy = 560, 250
d.line((P(cx), P(cy), P(cx), P(470)), fill=OL, width=P(12)); d.ellipse((P(cx - 26), P(cy - 26), P(cx + 26), P(cy + 26)), fill=(60, 60, 70))
d.line((P(cx), P(470), P(cx - 190), P(470)), fill=OL, width=P(10)); d.line((P(cx - 190), P(470), P(cx - 190), P(640)), fill=OL, width=P(10))
d.rounded_rectangle((P(cx - 230), P(620), P(cx + 230), P(670)), P(16), fill=AZ)                                            # asiento
d.rounded_rectangle((P(cx - 230), P(500), P(cx + 230), P(620)), P(20), fill=(30, 76, 190))                                 # respaldo
d.line((P(cx - 230), P(700), P(cx + 230), P(700)), fill=OL, width=P(8))                                                    # barra
d.rectangle((P(cx - 200), P(670), P(cx - 190), P(700)), fill=OL); d.rectangle((P(cx + 190), P(670), P(cx + 200), P(700)), fill=OL)
# la maleta sentada sola en el telesilla
d.rounded_rectangle((P(cx - 60), P(420), P(cx + 150), P(625)), P(26), fill=RO); d.rounded_rectangle((P(cx - 45), P(435), P(cx + 135), P(610)), P(18), fill=(236, 40, 70))
for x in (cx + 5, cx + 45, cx + 85): d.line((P(x), P(435), P(x), P(610)), fill=RO, width=P(6))
d.rounded_rectangle((P(cx + 15), P(395), P(cx + 75), P(425)), P(10), outline=OL, width=P(8))
d.rounded_rectangle((P(cx - 35), P(470), P(cx + 40), P(520)), P(8), fill=AM); d.text((P(cx + 2), P(495)), "AND", font=font(F_ANTON, P(34)), fill=(80, 50, 10), anchor="mm")
d.ellipse((P(cx + 70), P(535), P(cx + 125), P(590)), fill=(255, 255, 255)); d.polygon([(P(cx + 90), P(548)), (P(cx + 90), P(577)), (P(cx + 113), P(562))], fill=RO)
d.text((P(cx - 140), P(560)), "?", font=font(F_ANTON, P(90)), fill=(255, 255, 255), anchor="mm", stroke_width=P(4), stroke_fill=OL)   # sitio vacío: ¿y él?
rotulo(im, "EL POBRE DE", "ANDORRA", c2=(255, 236, 160))
guardar(im, "logo6_elpobredeandorra.png")

prev = Image.new("RGB", (3 * 420, 420), (240, 240, 240)); mk = Image.new("L", (400, 400), 0); ImageDraw.Draw(mk).ellipse((0, 0, 400, 400), fill=255)
for i in range(3): prev.paste(Image.open(os.path.join(OUT, f"logo{i + 4}_elpobredeandorra.png")).resize((400, 400), Image.LANCZOS), (i * 420 + 10, 10), mk)
prev.save("/tmp/logos2.jpg")
