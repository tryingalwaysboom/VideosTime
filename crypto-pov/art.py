"""Arte del Ep.1 "You Wake Up in 2009 Knowing Everything About Bitcoin" (16:9, para X).
Mismo estilo cartoon 2D acogedor que las series del club y del taller (SVG -> PNG a 2x con Chromium)."""
import math, os, random, re, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "club-pov"))
from art2 import cel, svg, sky, eye, face, neck, SK, SKS, SKH  # noqa: E402

OUT = os.path.join(HERE, "layers"); os.makedirs(OUT, exist_ok=True)
OL = "#1d1630"
BTC = "#f7931a"; SCR = "#7fd6ff"; WALL = "#7c8fb8"
W, H = 1920, 1080


def wood_floor(y0, y1, cols=("#8a5a3a", "#7a4e32", "#946444"), seed=1):
    r = random.Random(seed); b = ""
    for i, y in enumerate(range(y0, y1, 34)):
        x = -r.randint(0, 200)
        while x < W:
            w = r.randint(220, 420)
            b += f'<rect x="{x+2}" y="{y+2}" width="{w-4}" height="30" fill="{r.choice(cols)}"/>'
            x += w
    return f'<rect x="0" y="{y0}" width="{W}" height="{y1-y0}" fill="#5e3a24"/>' + b


def poster(x, y, w, h, rot, bgc, body):
    return (f'<g transform="rotate({rot} {x+w/2} {y+h/2})" filter="url(#drop)">'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bgc}" stroke="{OL}" stroke-width="5"/>{body}'
            f'<circle cx="{x+14}" cy="{y+14}" r="6" fill="#d33"/><circle cx="{x+w-14}" cy="{y+14}" r="6" fill="#d33"/></g>')


def crt(x, y, s=1.0, screen="#123", glow=False):
    """Monitor CRT beige de 2009. (x,y) = esquina sup. izq. de la carcasa; pantalla en (x+40s, y+36s, 340s x 250s)."""
    k = lambda v: v * s
    b = cel(f'<path d="M{x+k(60)} {y+k(330)} L{x+k(360)} {y+k(330)} L{x+k(330)} {y+k(390)} L{x+k(90)} {y+k(390)}Z"/>', "#d9d0b8", "#b3a98f", None, -10, 0, 6)
    b += cel(f'<rect x="{x+k(120)}" y="{y+k(380)}" width="{k(180)}" height="{k(26)}" rx="{k(8)}"/>', "#d9d0b8", "#b3a98f", None, -10, 0, 6)
    b += cel(f'<rect x="{x}" y="{y}" width="{k(420)}" height="{k(330)}" rx="{k(26)}"/>', "#e6dec6", "#bfb497", "#f5efdc", -26, -10, 7)
    b += f'<rect x="{x+k(40)}" y="{y+k(36)}" width="{k(340)}" height="{k(250)}" rx="{k(18)}" fill="{screen}" stroke="{OL}" stroke-width="6"/>'
    if glow:
        b += f'<rect x="{x+k(40)}" y="{y+k(36)}" width="{k(340)}" height="{k(250)}" rx="{k(18)}" fill="{SCR}" opacity="0.25"/>'
    b += f'<circle cx="{x+k(380)}" cy="{y+k(308)}" r="{k(8)}" fill="#5bd35b" stroke="{OL}" stroke-width="3"/>'
    b += f'<rect x="{x+k(60)}" y="{y+k(300)}" width="{k(90)}" height="{k(12)}" rx="4" fill="#bfb497"/>'
    return b


# ============================================================ FONDOS
def bg_bedroom():
    """Habitación de un chaval en 2009, mañana: ventana con luz, pósters, escritorio con CRT, cama deshecha."""
    d = sky("wl", [(0, "#8ea3cf"), (1, "#6f82ad")])
    d += '<radialGradient id="sun" cx="0.25" cy="0.3" r="0.6"><stop offset="0" stop-color="#ffe7a8" stop-opacity="0.55"/><stop offset="1" stop-color="#ffe7a8" stop-opacity="0"/></radialGradient>'
    b = f'<rect width="{W}" height="{H}" fill="url(#wl)"/>'
    r = random.Random(2)
    for i in range(0, W, 60): b += f'<rect x="{i}" y="0" width="28" height="{H}" fill="#fff" opacity="0.035"/>'
    # ventana
    b += cel('<rect x="170" y="150" width="420" height="380" rx="10"/>', "#f2ead6", "#cfc4a8", None, -14, -6, 7)
    b += '<rect x="200" y="180" width="360" height="320" fill="#bfe3ff"/><ellipse cx="300" cy="260" rx="110" ry="40" fill="#fff" opacity="0.9"/><ellipse cx="460" cy="320" rx="90" ry="30" fill="#fff" opacity="0.8"/>'
    b += f'<rect x="200" y="420" width="360" height="80" fill="#7fb36a"/><rect x="372" y="180" width="16" height="320" fill="#f2ead6" stroke="{OL}" stroke-width="4"/><rect x="200" y="332" width="360" height="16" fill="#f2ead6" stroke="{OL}" stroke-width="4"/>'
    b += cel('<path d="M140 130 L250 130 Q236 340 268 560 L140 560Z"/>', "#3a6fb0", "#2a5288", None, -10, 0, 6)
    b += cel('<path d="M620 130 L510 130 Q524 340 492 560 L620 560Z"/>', "#3a6fb0", "#2a5288", None, 10, 0, 6)
    # pósters
    b += poster(760, 120, 230, 320, -4, "#1e1e2e",
                '<circle cx="875" cy="250" r="70" fill="#e94b3c"/><path d="M820 330 L930 330" stroke="#fff" stroke-width="8"/>'
                '<text x="875" y="400" font-family="Anton" font-size="44" text-anchor="middle" fill="#fff">ROCK 07</text>')
    b += poster(1040, 160, 200, 270, 5, "#f2d64b",
                '<path d="M1080 360 L1140 220 L1200 360Z" fill="#2e2e44"/><text x="1140" y="410" font-family="Anton" font-size="36" text-anchor="middle" fill="#2e2e44">GAME OVER</text>')
    # calendario de pared (fecha la pinta render)
    b += cel('<rect x="1600" y="110" width="200" height="230" rx="8"/>', "#f6f3ea", "#d6d0c2", None, -10, -4, 6)
    b += f'<rect x="1600" y="110" width="200" height="60" rx="8" fill="#c62f2f" stroke="{OL}" stroke-width="6"/>'
    b += '<text x="1700" y="153" font-family="Anton" font-size="34" text-anchor="middle" fill="#fff">JANUARY</text>'
    b += '<text x="1700" y="290" font-family="Anton" font-size="86" text-anchor="middle" fill="#1d1630">2009</text>'
    # cama a la izquierda abajo
    b += wood_floor(820, H)
    b += f'<rect x="0" y="806" width="{W}" height="22" fill="#e9e1cc" stroke="{OL}" stroke-width="5"/>'
    b += cel('<rect x="40" y="640" width="640" height="260" rx="30"/>', "#4f7fc2", "#3a619a", "#6a98d8", -30, -12, 7)
    b += cel('<path d="M60 640 Q200 560 360 620 Q520 560 660 640 L660 700 L60 700Z"/>', "#f4f1ea", "#d2ccbd", None, -16, -6, 6)
    b += cel('<rect x="10" y="520" width="60" height="400" rx="16"/>', "#7a4e32", "#5a3622", None, -10, 0, 6)
    # mesita con despertador (el despertador es capa aparte)
    b += cel('<rect x="700" y="700" width="200" height="200" rx="10"/>', "#a8754e", "#7f5536", None, -14, -4, 6)
    b += f'<rect x="720" y="760" width="160" height="10" rx="4" fill="#7f5536"/>'
    # escritorio con CRT
    b += cel('<rect x="1180" y="640" width="680" height="34" rx="8"/>', "#b08156", "#8a6040", None, -12, -4, 6)
    b += cel('<rect x="1210" y="674" width="40" height="230" rx="6"/>', "#8a6040", "#6b4a30", None, -6, 0, 5)
    b += cel('<rect x="1790" y="674" width="40" height="230" rx="6"/>', "#8a6040", "#6b4a30", None, -6, 0, 5)
    b += crt(1300, 244, 0.95, "#0e1a2a")
    b += cel('<rect x="1330" y="606" width="330" height="34" rx="6"/>', "#e6dec6", "#bfb497", None, -6, -2, 5)
    for i in range(10): b += f'<rect x="{1342+i*31}" y="614" width="24" height="18" rx="3" fill="#cfc6ac"/>'
    # móvil de tapa cerrado sobre la mesa
    b += cel('<rect x="1236" y="596" width="56" height="44" rx="10"/>', "#3b3f4e", "#24272f", "#5a6070", -8, -3, 5)
    b += f'<rect x="1252" y="606" width="24" height="10" rx="3" fill="#9fd0ff" stroke="{OL}" stroke-width="2"/>'
    # torre del PC
    b += cel('<rect x="1690" y="420" width="130" height="220" rx="12"/>', "#e6dec6", "#bfb497", "#f5efdc", -14, -4, 6)
    b += f'<rect x="1712" y="450" width="86" height="16" rx="4" fill="#bfb497" stroke="{OL}" stroke-width="3"/><circle cx="1755" cy="600" r="12" fill="#cfc6ac" stroke="{OL}" stroke-width="4"/>'
    # ropa tirada
    b += cel('<path d="M900 960 Q960 920 1040 950 Q1100 990 1060 1030 Q960 1050 900 1010Z"/>', "#3d3d52", "#2a2a3a", None, -10, -4, 5)
    b += f'<rect width="{W}" height="{H}" fill="url(#sun)"/>'
    return svg(W, H, b, d)


def alarma():
    """Despertador de campanas rojo (capa, se agita)."""
    b = ''
    for sx in (-1, 1):
        b += cel(f'<path d="M{150+sx*60} 70 Q{150+sx*110} 40 {150+sx*120} 90 Z"/>', "#d9d9e0", "#a9a9b6", None, -6 * sx, -4, 5)
    b += f'<path d="M150 46 L150 70" stroke="{OL}" stroke-width="8"/><circle cx="150" cy="42" r="10" fill="#d9d9e0" stroke="{OL}" stroke-width="4"/>'
    b += f'<path d="M90 250 L70 290 M210 250 L230 290" stroke="{OL}" stroke-width="12" stroke-linecap="round"/>'
    b += cel('<circle cx="150" cy="170" r="105"/>', "#d23a35", "#9e2522", "#ef6a5f", -20, -10, 7)
    b += f'<circle cx="150" cy="170" r="78" fill="#fbf7ee" stroke="{OL}" stroke-width="5"/>'
    for i in range(12):
        a = i * math.pi / 6
        b += f'<circle cx="{150+64*math.sin(a):.1f}" cy="{170-64*math.cos(a):.1f}" r="4" fill="{OL}"/>'
    b += f'<path d="M150 170 L150 116 M150 170 L186 182" stroke="{OL}" stroke-width="8" stroke-linecap="round"/><circle cx="150" cy="170" r="7" fill="{OL}"/>'
    return svg(300, 300, b)


def movil():
    """Móvil de tapa abierto (pantalla en blanco: la fecha la escribe render)."""
    b = cel('<rect x="60" y="30" width="300" height="420" rx="46"/>', "#3b3f4e", "#24272f", "#5a6070", -24, -10, 7)
    b += f'<rect x="96" y="80" width="228" height="300" rx="14" fill="#9fd0ff" stroke="{OL}" stroke-width="6"/>'
    b += f'<rect x="170" y="48" width="80" height="12" rx="6" fill="#1b1d24"/>'
    b += cel('<rect x="70" y="440" width="280" height="40" rx="14"/>', "#2c2f3a", "#1b1d24", None, -8, 0, 6)
    b += cel('<rect x="60" y="470" width="300" height="420" rx="46"/>', "#3b3f4e", "#24272f", "#5a6070", -24, -10, 7)
    for rr in range(4):
        for cc in range(3):
            b += f'<rect x="{110+cc*72}" y="{620+rr*62}" width="56" height="42" rx="12" fill="#c9cdd8" stroke="{OL}" stroke-width="4"/>'
    b += f'<rect x="150" y="510" width="120" height="80" rx="30" fill="#c9cdd8" stroke="{OL}" stroke-width="5"/><circle cx="210" cy="550" r="18" fill="#9aa0b0" stroke="{OL}" stroke-width="4"/>'
    return svg(420, 920, b)


def heroe(expr="shock", luz=None):
    """Tú, con 19 años en 2009: flequillo de lado, sudadera gris con capucha."""
    b = ''
    torso = '<path d="M80 1000 L96 760 Q110 600 250 560 Q350 530 450 560 Q590 600 604 760 L620 1000Z"/>'
    b += cel(torso, "#7d8496", "#5d6476", "#9aa1b2", -50, -10, 8)
    b += cel('<path d="M250 560 Q350 640 450 560 Q440 520 350 520 Q260 520 250 560Z"/>', "#6c7385", "#525a6a", None, -10, 0, 6)
    b += f'<path d="M318 600 Q312 680 300 720 M382 600 Q388 680 400 720" stroke="#e9e9ef" stroke-width="7" fill="none" stroke-linecap="round"/>'
    b += cel('<rect x="230" y="820" width="240" height="110" rx="20"/>', "#6c7385", "#525a6a", None, -10, 0, 6)
    b += '<g transform="translate(0,60)">'
    b += neck(305, 360, 90, 110)
    b += face(350, 300, 118)
    # pelo: casquete con flequillo de lado hacia la derecha (2009)
    b += cel('<path d="M230 300 Q206 190 280 150 Q350 112 430 138 Q492 162 484 250 Q478 290 468 300 '
             'Q462 252 440 236 Q396 252 340 236 Q290 238 262 262 Q246 276 240 304Z"/>', "#4a2f22", "#2f1d15", "#6b4630", -18, -10, 7)
    b += cel('<path d="M250 250 Q290 176 380 168 Q452 166 474 214 Q478 236 462 244 Q430 214 380 220 '
             'Q320 226 270 262 Q252 268 250 250Z"/>', "#5a3a2a", "#3a2418", "#7a5038", -10, -6, 6)
    b += '<path d="M300 200 Q350 186 400 192 M330 176 Q380 168 430 178" stroke="#2f1d15" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.6"/>'
    if expr == "shock":
        b += eye(305, 300, 15) + eye(398, 300, 15)
        b += '<path d="M280 268 Q305 254 332 264 M372 264 Q398 254 424 268" stroke="#2f1d15" stroke-width="11" fill="none" stroke-linecap="round"/>'
        b += f'<ellipse cx="351" cy="388" rx="20" ry="25" fill="#6a2a2a" stroke="{OL}" stroke-width="6"/><ellipse cx="351" cy="398" rx="11" ry="8" fill="#e07070"/>'
    elif expr == "miedo":
        b += eye(305, 302, 14, -3) + eye(398, 302, 14, -3)
        b += '<path d="M280 266 Q305 274 332 268 M372 268 Q398 274 424 266" stroke="#2f1d15" stroke-width="11" fill="none" stroke-linecap="round"/>'
        b += f'<path d="M326 392 Q338 382 351 390 Q364 382 378 392" stroke="{OL}" stroke-width="6" fill="none" stroke-linecap="round"/>'
        b += '<path d="M462 268 Q474 296 464 314 Q452 296 462 268Z" fill="#9fdcff" stroke="#1d1630" stroke-width="3"/>'
    elif expr == "dormido":
        b += f'<path d="M286 302 Q305 316 326 302 M378 302 Q398 316 418 302" stroke="{OL}" stroke-width="7" fill="none" stroke-linecap="round"/>'
        b += '<path d="M280 274 Q305 268 332 274 M372 274 Q398 268 424 274" stroke="#2f1d15" stroke-width="10" fill="none" stroke-linecap="round"/>'
        b += f'<ellipse cx="352" cy="390" rx="12" ry="9" fill="#6a2a2a" stroke="{OL}" stroke-width="5"/>'
    else:  # decidido
        b += eye(305, 296, 13) + eye(398, 296, 13)
        b += '<path d="M276 262 Q305 254 334 268 M370 268 Q398 254 428 262" stroke="#2f1d15" stroke-width="11" fill="none" stroke-linecap="round"/>'
        b += f'<path d="M322 384 Q352 400 384 380" stroke="{OL}" stroke-width="6" fill="none" stroke-linecap="round"/>'
    b += f'<path d="M352 306 Q344 334 338 346 Q346 356 360 352" stroke="{OL}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    b += '<ellipse cx="272" cy="350" rx="22" ry="13" fill="#e7887a" opacity="0.4"/><ellipse cx="430" cy="350" rx="22" ry="13" fill="#e7887a" opacity="0.4"/>'
    b += '</g>'
    if luz:
        b += f'<rect width="700" height="1000" fill="{luz}" opacity="0.28" style="mix-blend-mode:multiply"/>'
    return svg(700, 1000, b)


def heroe_shock(): return heroe("shock")
def heroe_miedo(): return heroe("miedo")
def heroe_decidido(): return heroe("decidido")
def heroe_dormido(): return heroe("dormido")


def bg_espejo():
    """Baño: azulejos, espejo grande con marco (el reflejo lo compone render)."""
    b = f'<rect width="{W}" height="{H}" fill="#cfe3e6"/>'
    for y in range(0, H, 80):
        for x in range(0, W, 80):
            b += f'<rect x="{x+3}" y="{y+3}" width="74" height="74" rx="4" fill="#e3f0f1"/>'
    b += cel('<rect x="580" y="140" width="760" height="720" rx="40"/>', "#c9a46a", "#9c7a44", "#e6c48a", -20, -8, 9)
    b += f'<rect x="620" y="180" width="680" height="640" rx="26" fill="#a7c4cf" stroke="{OL}" stroke-width="7"/>'
    b += cel(f'<rect x="420" y="890" width="1080" height="220" rx="24"/>', "#f4f4f6", "#cfd0d8", None, -16, -6, 7)
    b += f'<rect x="880" y="860" width="40" height="50" rx="8" fill="#b9bcc8" stroke="{OL}" stroke-width="5"/><rect x="860" y="850" width="120" height="22" rx="10" fill="#d9dce6" stroke="{OL}" stroke-width="5"/>'
    b += cel(f'<rect x="1280" y="900" width="110" height="70" rx="12"/>', "#9fd6c9", "#76b0a3", None, -8, -3, 5)
    return svg(W, H, b)


def bg_salon():
    """Salón-cocina de 2009: tele de tubo con las noticias (pinta render), sofá, mesa con taza."""
    d = sky("sl", [(0, "#d9b98c"), (1, "#c49f6f")])
    b = f'<rect width="{W}" height="{H}" fill="url(#sl)"/>'
    for x in range(0, W, 120): b += f'<rect x="{x}" y="0" width="60" height="{H}" fill="#fff" opacity="0.05"/>'
    # cuadro y lámpara
    b += cel('<rect x="160" y="140" width="280" height="200" rx="6"/>', "#7a4e32", "#5a3622", None, -8, -4, 6)
    b += '<rect x="182" y="162" width="236" height="156" fill="#9cc6a2"/><path d="M182 318 L260 230 L320 290 L360 250 L418 318Z" fill="#5e8f68"/>'
    # mueble de la tele
    b += wood_floor(800, H, ("#9b6b45", "#8a5c3a", "#a7774f"), 4)
    b += cel('<rect x="1100" y="620" width="700" height="200" rx="10"/>', "#6b4a30", "#4f3522", None, -14, -4, 7)
    # tele de tubo (pantalla en 1180,250 600x380)
    b += cel('<rect x="1130" y="200" width="640" height="440" rx="34"/>', "#3a3d48", "#25272f", "#55596a", -26, -10, 8)
    b += f'<rect x="1170" y="236" width="520" height="368" rx="22" fill="#1a2a3a" stroke="{OL}" stroke-width="7"/>'
    for i in range(5): b += f'<circle cx="1730" cy="{300+i*50}" r="12" fill="#6a6e7c" stroke="{OL}" stroke-width="4"/>'
    b += f'<path d="M1400 200 L1340 110 M1440 200 L1520 100" stroke="{OL}" stroke-width="7" stroke-linecap="round"/>'
    # mesa con taza (la taza va como capa)
    b += cel('<rect x="420" y="720" width="560" height="40" rx="10"/>', "#b08156", "#8a6040", None, -12, -4, 6)
    b += cel('<rect x="460" y="760" width="36" height="200" rx="6"/>', "#8a6040", "#6b4a30", None, -6, 0, 5)
    b += cel('<rect x="904" y="760" width="36" height="200" rx="6"/>', "#8a6040", "#6b4a30", None, -6, 0, 5)
    b += f'<rect x="560" y="690" width="160" height="34" rx="4" fill="#f2eee2" stroke="{OL}" stroke-width="5"/>'
    b += f'<text x="640" y="716" font-family="Anton" font-size="22" text-anchor="middle" fill="#1d1630">THE DAILY</text>'
    return svg(W, H, b, d)


def papa(expr="serio"):
    """Tu padre: 50 y pocos, gafas, entradas, camisa de cuadros, taza en mano."""
    b = ''
    torso = '<path d="M90 1100 L100 820 Q110 660 260 620 Q360 596 460 620 Q610 660 620 820 L630 1100Z"/>'
    b += cel(torso, "#b9463d", "#8a2f29", "#d65c51", -50, -10, 8)
    pl = ''.join(f'<path d="M{x} 600 L{x} 1100" stroke="#7a2520" stroke-width="10" opacity="0.5"/>' for x in range(140, 600, 70))
    pl += ''.join(f'<path d="M80 {y} L640 {y}" stroke="#7a2520" stroke-width="10" opacity="0.5"/>' for y in range(680, 1100, 70))
    b += f'<clipPath id="plaid">{torso}</clipPath><g clip-path="url(#plaid)">{pl}</g>'
    b += f'<path d="{torso.split(chr(34))[1]}" fill="none" stroke="{OL}" stroke-width="8"/>'
    b += cel('<path d="M300 620 L360 700 L420 620 L400 600 L360 650 L320 600Z"/>', "#f1ece0", "#cfc7b4", None, -8, 0, 6)
    b += '<g transform="translate(10,140)">'
    b += neck(305, 380, 90, 110)
    b += face(350, 310, 120)
    b += cel('<path d="M234 318 Q226 248 252 214 Q270 200 284 210 Q262 246 266 322Z"/>', "#8a8a92", "#66666e", None, 6, 0, 6)
    b += cel('<path d="M466 318 Q474 248 448 214 Q430 200 416 210 Q438 246 434 322Z"/>', "#8a8a92", "#66666e", None, -6, 0, 6)
    b += '<path d="M318 196 Q350 186 382 196" stroke="#8a8a92" stroke-width="8" fill="none" stroke-linecap="round"/>'
    if expr == "serio":
        b += eye(305, 312, 11) + eye(395, 312, 11)
        b += '<path d="M278 276 Q305 288 334 278 M366 278 Q395 288 422 276" stroke="#4b4b52" stroke-width="11" fill="none" stroke-linecap="round"/>'
        b += f'<path d="M322 420 Q350 410 378 420" stroke="{OL}" stroke-width="7" fill="none" stroke-linecap="round"/>'
    else:  # risa
        b += f'<path d="M286 314 Q305 296 324 314 M376 314 Q395 296 414 314" stroke="{OL}" stroke-width="8" fill="none" stroke-linecap="round"/>'
        b += '<path d="M278 268 Q305 252 334 262 M366 262 Q395 252 422 268" stroke="#4b4b52" stroke-width="11" fill="none" stroke-linecap="round"/>'
        b += f'<path d="M296 398 Q350 480 404 398Z" fill="#7a2a2a" stroke="{OL}" stroke-width="7"/><path d="M310 404 L390 404" stroke="#fff" stroke-width="10"/>'
        b += '<path d="M262 340 Q250 360 256 380" stroke="#9fdcff" stroke-width="6" fill="none"/>'
    # gafas
    b += f'<rect x="268" y="288" width="74" height="54" rx="14" fill="#fff" fill-opacity="0.15" stroke="{OL}" stroke-width="6"/>'
    b += f'<rect x="358" y="288" width="74" height="54" rx="14" fill="#fff" fill-opacity="0.15" stroke="{OL}" stroke-width="6"/><path d="M342 312 L358 312" stroke="{OL}" stroke-width="6"/>'
    b += cel('<path d="M346 326 Q376 366 356 386 Q338 392 328 380 Q332 356 346 326Z"/>', SK, SKS, None, -6, -4, 5)
    b += cel('<path d="M300 380 Q350 360 400 380 Q380 396 350 390 Q320 396 300 380Z"/>', "#6b6b72", "#4b4b52", None, -6, -2, 5)
    b += '</g>'
    return svg(720, 1100, b)


def papa_serio(): return papa("serio")
def papa_risa(): return papa("risa")


def taza():
    b = cel('<path d="M40 40 L200 40 L186 210 Q120 232 54 210Z"/>', "#f2eee2", "#cfc7b4", "#ffffff", -16, -6, 7)
    b += f'<path d="M196 80 Q262 86 252 140 Q244 186 190 180" stroke="{OL}" stroke-width="22" fill="none"/><path d="M196 80 Q262 86 252 140 Q244 186 190 180" stroke="#f2eee2" stroke-width="12" fill="none"/>'
    b += f'<ellipse cx="120" cy="44" rx="80" ry="16" fill="#5a3320" stroke="{OL}" stroke-width="5"/>'
    b += '<text x="120" y="150" font-family="Anton" font-size="40" text-anchor="middle" fill="#c62f2f">#1 DAD</text>'
    return svg(280, 250, b)


def bg_noche():
    """Tu habitación de noche: todo oscuro y azul, luz del monitor (el monitor lo pinta render encima)."""
    d = sky("nt", [(0, "#151a33"), (1, "#0b0e1e")])
    d += '<radialGradient id="mon" cx="0.5" cy="0.45" r="0.55"><stop offset="0" stop-color="#7fd6ff" stop-opacity="0.35"/><stop offset="1" stop-color="#7fd6ff" stop-opacity="0"/></radialGradient>'
    b = f'<rect width="{W}" height="{H}" fill="url(#nt)"/>'
    # ventana con luna
    b += f'<rect x="120" y="120" width="360" height="320" fill="#1e2a52" stroke="#0a0c18" stroke-width="8"/><circle cx="380" cy="210" r="46" fill="#e8ecff" opacity="0.9"/>'
    r = random.Random(9)
    for _ in range(25): b += f'<circle cx="{r.randint(130,470)}" cy="{r.randint(130,430)}" r="{r.choice([1.5,2,2.5])}" fill="#fff" opacity="{r.uniform(.4,.9):.2f}"/>'
    b += '<rect x="292" y="120" width="12" height="320" fill="#0a0c18"/><rect x="120" y="272" width="360" height="12" fill="#0a0c18"/>'
    # pósters en sombra
    b += '<rect x="1500" y="140" width="220" height="300" fill="#1c2140" transform="rotate(4 1610 290)"/>'
    b += '<rect x="560" y="150" width="200" height="270" fill="#1c2140" transform="rotate(-5 660 285)"/>'
    # escritorio
    b += f'<rect x="300" y="760" width="1320" height="40" rx="8" fill="#2a2234"/><rect x="0" y="880" width="{W}" height="{H-880}" fill="#120f1c"/>'
    b += f'<rect width="{W}" height="{H}" fill="url(#mon)"/>'
    return svg(W, H, b, d)


def monitor_grande():
    """Primer plano del monitor CRT (pantalla 120,90 a 1460,880 en el lienzo 1580x1060)."""
    b = cel('<rect x="20" y="20" width="1540" height="1000" rx="70"/>', "#e6dec6", "#bfb497", "#f5efdc", -40, -16, 9)
    b += f'<rect x="100" y="80" width="1380" height="820" rx="46" fill="#0c1220" stroke="{OL}" stroke-width="9"/>'
    b += f'<circle cx="1470" cy="960" r="16" fill="#5bd35b" stroke="{OL}" stroke-width="5"/>'
    b += f'<rect x="140" y="944" width="240" height="26" rx="8" fill="#bfb497"/>'
    b += '<text x="790" y="975" font-family="Anton" font-size="34" text-anchor="middle" fill="#a89d80">SYNCMASTER</text>'
    return svg(1580, 1060, b)


def nakamoto():
    """Silueta misteriosa con capucha (Satoshi: nadie sabe quién es)."""
    b = cel('<path d="M60 760 Q60 520 200 470 Q160 400 170 300 Q190 110 330 100 Q470 110 490 300 Q500 400 460 470 Q600 520 600 760Z"/>',
            "#2a2d3e", "#1a1c28", "#3b3f55", -30, -10, 7)
    b += '<path d="M230 300 Q250 190 330 180 Q410 190 430 300 Q440 400 330 430 Q220 400 230 300Z" fill="#0b0c12"/>'
    b += '<text x="330" y="360" font-family="Anton" font-size="150" text-anchor="middle" fill="#f7931a" opacity="0.9">?</text>'
    return svg(660, 780, b)


def btc_coin():
    b = f'<circle cx="160" cy="160" r="150" fill="{BTC}" stroke="#7a4300" stroke-width="10"/>'
    b += '<circle cx="160" cy="160" r="122" fill="none" stroke="#ffb54d" stroke-width="8"/>'
    b += '<text x="160" y="222" font-family="Anton" font-size="190" text-anchor="middle" fill="#fff" transform="rotate(14 160 160)">₿</text>'
    return svg(320, 320, b)


LAYERS = {"bg_bedroom": bg_bedroom, "alarma": alarma, "movil": movil, "heroe_shock": heroe_shock,
          "heroe_miedo": heroe_miedo, "heroe_decidido": heroe_decidido, "heroe_dormido": heroe_dormido, "bg_espejo": bg_espejo, "bg_salon": bg_salon,
          "papa_serio": papa_serio, "papa_risa": papa_risa, "taza": taza, "bg_noche": bg_noche,
          "monitor_grande": monitor_grande, "nakamoto": nakamoto, "btc_coin": btc_coin}

FONTS = os.path.join(HERE, "..", "taller-pov", "fonts")
FONT_CSS = "@font-face{font-family:Anton;src:url(file://%s/Anton-Regular.ttf)}" % FONTS

if __name__ == "__main__":
    only = sys.argv[1:] or list(LAYERS)
    with sync_playwright() as p:
        br = p.chromium.launch()
        for name in only:
            s = LAYERS[name]()
            w, h = map(int, re.search(r'width="(\d+)" height="(\d+)"', s).groups())
            pg = br.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
            hp = os.path.join(OUT, "_tmp.html")
            open(hp, "w").write(f"<html><head><style>{FONT_CSS} html,body{{margin:0;background:transparent;overflow:hidden}}</style></head><body>{s}</body></html>")
            pg.goto("file://" + hp); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(150)
            pg.screenshot(path=os.path.join(OUT, name + ".png"), omit_background=True)
            pg.close(); print("ok", name, flush=True)
        br.close()
