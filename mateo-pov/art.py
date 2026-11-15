"""Arte de "Los 30 días de Mateo": fondos y personajes 2D cálidos (SVG -> PNG a 2x con Chromium).
Mismo estilo cartoon de las series del club y del taller (cel-shading, contorno grueso), pero de casa: tarde cálida."""
import os, random, re, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "club-pov"))
from art2 import cel, svg, sky, eye, face, neck, SK, SKS, SKH  # noqa: E402

OUT = os.path.join(HERE, "layers"); os.makedirs(OUT, exist_ok=True)
OL = "#1d1630"
HAIR = "#4a2e1e"; HAIRS = "#2f1c12"; HAIRH = "#6b4630"
TEE = "#4fb06a"; TEES = "#378a4f"; TEEH = "#74cc8a"

# ============================================================ FONDOS
def bg_cocina():
    """Cocina de casa a media tarde: ventana con luz dorada, alacenas, refri con dibujos de dinosaurios, mesa delante."""
    d = sky("wall", [(0, "#f6dcb4"), (1, "#e9c08e")])
    d += sky("win", [(0, "#ffd88a"), (0.6, "#ffb877"), (1, "#f59a6b")])
    d += sky("wood", [(0, "#b4743e"), (1, "#8a5428")])
    d += '<radialGradient id="sunl" cx="0.3" cy="0.3" r="0.7"><stop offset="0" stop-color="#fff1c8" stop-opacity="0.65"/><stop offset="1" stop-color="#fff1c8" stop-opacity="0"/></radialGradient>'
    b = '<rect width="1080" height="1920" fill="url(#wall)"/>'
    # azulejos detrás de la encimera
    for y in range(820, 1080, 60):
        for x in range(0 if (y // 60) % 2 else -30, 1080, 60):
            b += f'<rect x="{x+3}" y="{y+3}" width="54" height="54" rx="6" fill="#fbeedd" stroke="#e2c9a6" stroke-width="3"/>'
    # ventana
    b += f'<rect x="90" y="300" width="440" height="470" rx="18" fill="url(#win)" stroke="{OL}" stroke-width="9"/>'
    b += '<circle cx="380" cy="560" r="80" fill="#fff4d0" opacity="0.9"/>'
    b += '<path d="M90 640 Q200 600 300 640 T530 630 L530 770 L90 770Z" fill="#7cae6a" opacity="0.9"/>'
    b += '<path d="M90 690 Q240 660 380 700 T530 690 L530 770 L90 770Z" fill="#5f9455"/>'
    b += f'<path d="M310 300 L310 770 M90 535 L530 535" stroke="{OL}" stroke-width="9"/>'
    b += f'<rect x="70" y="760" width="480" height="34" rx="8" fill="#fff6e8" stroke="{OL}" stroke-width="7"/>'
    # cortinas
    b += cel('<path d="M70 280 Q120 520 90 800 L40 800 Q20 520 40 280Z"/>', "#e86f5c", "#c4513f", "#f49384", -14, 0, 7)
    b += cel('<path d="M550 280 Q500 520 530 800 L580 800 Q600 520 580 280Z"/>', "#e86f5c", "#c4513f", "#f49384", 14, 0, 7)
    b += f'<rect x="30" y="268" width="560" height="22" rx="10" fill="#a8683a" stroke="{OL}" stroke-width="6"/>'
    # macetita en la ventana
    b += cel('<path d="M140 700 L210 700 L200 760 L150 760Z"/>', "#d0703c", "#a4512a", None, -8, 0, 6)
    b += f'<path d="M175 700 Q150 640 160 610 M175 700 Q195 640 215 630 M175 700 Q172 650 185 600" stroke="#3f8a4a" stroke-width="12" fill="none" stroke-linecap="round"/>'
    # alacenas altas
    for x in (620, 820):
        b += cel(f'<rect x="{x}" y="120" width="190" height="300" rx="14"/>', "#f2f0e8", "#d8d2c2", None, -12, 0, 7)
        b += f'<rect x="{x+150}" y="250" width="16" height="50" rx="8" fill="#c9a24a" stroke="{OL}" stroke-width="4"/>'
    # refri con dibujos de dinos y imanes
    b += cel('<rect x="640" y="470" width="400" height="760" rx="30"/>', "#eef3f6", "#c9d3da", "#ffffff", -26, 0, 8)
    b += f'<path d="M640 720 L1040 720" stroke="{OL}" stroke-width="7"/>'
    b += f'<rect x="660" y="560" width="16" height="120" rx="8" fill="#b0bcc6" stroke="{OL}" stroke-width="4"/><rect x="660" y="760" width="16" height="140" rx="8" fill="#b0bcc6" stroke="{OL}" stroke-width="4"/>'
    for (x, y, rot, c) in ((720, 500, -6, "#7fc98f"), (880, 520, 5, "#f4b860"), (760, 780, 4, "#8ab7f0"), (900, 800, -5, "#f08a8a")):
        b += f'<g transform="rotate({rot} {x+60} {y+80})"><rect x="{x}" y="{y}" width="130" height="165" fill="#fffdf6" stroke="{OL}" stroke-width="5"/>'
        b += f'<path d="M{x+20} {y+120} Q{x+30} {y+60} {x+70} {y+70} Q{x+90} {y+40} {x+110} {y+60} L{x+100} {y+80} Q{x+110} {y+120} {x+90} {y+130} L{x+80} {y+150} M{x+40} {y+130} L{x+40} {y+150}" stroke="{c}" stroke-width="7" fill="none" stroke-linecap="round"/>'
        b += f'<circle cx="{x+65}" cy="{y}" r="11" fill="#e2483b" stroke="{OL}" stroke-width="3"/></g>'
    # encimera
    b += cel('<rect x="-20" y="1060" width="640" height="70" rx="10"/>', "#d9b48a", "#b8926a", None, 0, -10, 7)
    b += cel('<rect x="-20" y="1120" width="640" height="300" rx="6"/>', "#7aa6c9", "#5b86a8", None, -12, 0, 7)
    for x in (20, 220, 420): b += f'<rect x="{x+130}" y="1170" width="40" height="12" rx="6" fill="#c9a24a" stroke="{OL}" stroke-width="3"/>'
    # suelo
    b += '<rect x="0" y="1230" width="1080" height="700" fill="#d7b48c"/>'
    for y in range(1230, 1920, 90):
        b += f'<path d="M0 {y} L1080 {y}" stroke="#bf9a72" stroke-width="4"/>'
    # mesa de madera en primer plano
    b += cel('<path d="M-40 1380 L1120 1380 L1120 1500 L-40 1500Z"/>', "#c4844a", "#9c6232", "#dba06a", 0, -14, 8)
    b += '<path d="M-40 1500 L1120 1500 L1120 1960 L-40 1960Z" fill="url(#wood)"/>'
    r = random.Random(2)
    for _ in range(18):
        y = r.randint(1520, 1900)
        b += f'<path d="M-20 {y} Q540 {y + r.randint(-20, 20)} 1100 {y + r.randint(-14, 14)}" stroke="#6e4220" stroke-opacity="0.3" stroke-width="{r.randint(3, 7)}" fill="none"/>'
    b += '<rect width="1080" height="1920" fill="url(#sunl)"/>'
    return svg(1080, 1920, b, d)

def bg_cuarto():
    """Cuarto de Mateo: pared azul llena de dibujos de dinosaurios hechos con crayola, cama, peluches, juguetes."""
    d = sky("wl", [(0, "#a9c8e8"), (1, "#86aad0")])
    d += '<radialGradient id="lamp" cx="0.75" cy="0.35" r="0.6"><stop offset="0" stop-color="#ffe7b0" stop-opacity="0.55"/><stop offset="1" stop-color="#ffe7b0" stop-opacity="0"/></radialGradient>'
    b = '<rect width="1080" height="1920" fill="url(#wl)"/>'
    # estrellitas pintadas
    r = random.Random(11)
    for _ in range(26):
        x, y = r.randint(20, 1060), r.randint(40, 700)
        b += f'<circle cx="{x}" cy="{y}" r="{r.randint(4, 8)}" fill="#fff6c8" opacity="0.7"/>'
    cols = ["#3f9a52", "#e6762f", "#7a4fc2", "#d23f57", "#2f7fd0", "#e2b02a"]
    for i in range(16):
        x, y = 40 + (i % 4) * 255 + r.randint(-20, 20), 200 + (i // 4) * 270 + r.randint(-20, 20)
        rot = r.randint(-9, 9); c = cols[i % len(cols)]
        b += f'<g transform="rotate({rot} {x+95} {y+110})"><rect x="{x}" y="{y}" width="190" height="220" fill="#fffdf4" stroke="{OL}" stroke-width="5"/>'
        # dino garabateado
        b += (f'<path d="M{x+25} {y+170} Q{x+40} {y+90} {x+100} {y+100} Q{x+120} {y+50} {x+150} {y+60} Q{x+175} {y+70} {x+160} {y+92} '
              f'L{x+138} {y+96} Q{x+150} {y+150} {x+120} {y+170} L{x+118} {y+195} M{x+70} {y+170} L{x+70} {y+195} M{x+25} {y+170} Q{x+10} {y+150} {x+12} {y+130}" '
              f'stroke="{c}" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
        b += f'<circle cx="{x+150}" cy="{y+72}" r="5" fill="{OL}"/>'
        for k in range(3): b += f'<path d="M{x+80+k*18} {y+98} l8 -16 l8 16" stroke="{c}" stroke-width="5" fill="none"/>'
        b += f'<rect x="{x+80}" y="{y-12}" width="40" height="22" fill="#f4e6a8" opacity="0.9" transform="rotate({-rot} {x+100} {y})"/></g>'
    # zócalo y suelo
    b += '<rect x="0" y="1300" width="1080" height="30" fill="#f2efe6"/>'
    b += '<rect x="0" y="1330" width="1080" height="600" fill="#c99a6a"/>'
    for y in range(1330, 1920, 80): b += f'<path d="M0 {y} L1080 {y}" stroke="#ad7f52" stroke-width="4"/>'
    # alfombra
    b += '<ellipse cx="540" cy="1660" rx="460" ry="150" fill="#f0b45a" stroke="#d48f35" stroke-width="10"/>'
    b += '<ellipse cx="540" cy="1660" rx="360" ry="105" fill="none" stroke="#e8763a" stroke-width="12" stroke-dasharray="40 26"/>'
    # cama a la derecha
    b += cel('<rect x="700" y="1030" width="420" height="300" rx="20"/>', "#e05d4f", "#b8443a", "#f07a6c", -20, -10, 8)
    b += cel('<rect x="760" y="990" width="200" height="90" rx="40"/>', "#fffdf6", "#e2dccb", None, -10, 0, 6)
    b += f'<rect x="690" y="880" width="30" height="460" rx="12" fill="#9a6538" stroke="{OL}" stroke-width="6"/>'
    # cajón de juguetes a la izquierda
    b += cel('<rect x="40" y="1160" width="300" height="200" rx="16"/>', "#f2c84b", "#d1a532", None, -14, 0, 7)
    b += '<text x="190" y="1290" font-family="Anton" font-size="54" text-anchor="middle" fill="#fff" stroke="#1d1630" stroke-width="4">JUGUETES</text>'
    b += cel('<path d="M90 1160 L110 1080 L150 1100 L140 1160Z"/>', "#4fb06a", "#378a4f", None, -6, 0, 5)
    b += cel('<circle cx="250" cy="1130" r="45"/>', "#2f7fd0", "#1f5fa8", "#5a9de6", -10, -6, 6)
    b += '<rect width="1080" height="1920" fill="url(#lamp)"/>'
    return svg(1080, 1920, b, d)

def bg_mesa():
    """Mesa de la cocina vista desde arriba: madera cálida, mantelito, migas."""
    d = sky("wd", [(0, "#c08048"), (1, "#9a5f30")])
    d += '<radialGradient id="lz" cx="0.4" cy="0.35" r="0.75"><stop offset="0" stop-color="#ffe2a8" stop-opacity="0.45"/><stop offset="1" stop-color="#ffe2a8" stop-opacity="0"/></radialGradient>'
    b = '<rect width="1080" height="1920" fill="url(#wd)"/>'
    r = random.Random(5)
    for i in range(55):
        y = r.randint(0, 1920)
        b += f'<path d="M0 {y} Q540 {y + r.randint(-30, 30)} 1080 {y + r.randint(-20, 20)}" stroke="#5e3416" stroke-opacity="0.22" stroke-width="{r.randint(2, 6)}" fill="none"/>'
    for x in range(0, 1080, 270): b += f'<path d="M{x} 0 L{x} 1920" stroke="#5e3416" stroke-opacity="0.35" stroke-width="5"/>'
    # mantelito de cuadros
    b += '<g transform="rotate(-4 540 980)">'
    b += '<rect x="80" y="420" width="920" height="1120" rx="20" fill="#f6efe2"/>'
    for k in range(0, 920, 80): b += f'<rect x="{80+k}" y="420" width="40" height="1120" fill="#e86f5c" opacity="0.18"/>'
    for k in range(0, 1120, 80): b += f'<rect x="80" y="{420+k}" width="920" height="40" fill="#e86f5c" opacity="0.18"/>'
    b += '</g>'
    for _ in range(30):
        b += f'<circle cx="{r.randint(40, 1040)}" cy="{r.randint(80, 1850)}" r="{r.randint(3, 6)}" fill="#e9c58a" opacity="0.8"/>'
    b += '<rect width="1080" height="1920" fill="url(#lz)"/>'
    return svg(1080, 1920, b, d)

def bg_puerta():
    """Entrada de la casa: puerta de madera abierta, luz de la calle, perchero."""
    d = sky("wp", [(0, "#f3d7ae"), (1, "#e3b98a")])
    d += sky("cl", [(0, "#ffd9a0"), (1, "#f2a978")])
    b = '<rect width="1080" height="1920" fill="url(#wp)"/>'
    b += f'<rect x="260" y="260" width="560" height="1100" rx="10" fill="url(#cl)" stroke="{OL}" stroke-width="10"/>'
    b += '<path d="M260 1000 Q420 960 540 990 T820 980 L820 1360 L260 1360Z" fill="#8fbf74"/>'
    b += '<rect x="300" y="760" width="40" height="300" fill="#7a5a3a"/><circle cx="320" cy="720" r="90" fill="#5f9455"/>'
    # hoja de puerta abierta
    b += cel('<path d="M820 260 L1010 200 L1010 1420 L820 1360Z"/>', "#b06a36", "#8a4f24", "#c98048", -14, 0, 8)
    b += f'<circle cx="980" cy="820" r="16" fill="#e2b84a" stroke="{OL}" stroke-width="4"/>'
    # marco
    b += f'<rect x="230" y="230" width="620" height="40" rx="8" fill="#9a5f30" stroke="{OL}" stroke-width="7"/>'
    b += f'<rect x="230" y="230" width="40" height="1140" rx="8" fill="#9a5f30" stroke="{OL}" stroke-width="7"/>'
    # timbre
    b += f'<rect x="120" y="760" width="70" height="100" rx="14" fill="#f6efe2" stroke="{OL}" stroke-width="6"/><circle cx="155" cy="810" r="20" fill="#e2b84a" stroke="{OL}" stroke-width="5"/>'
    # perchero
    b += f'<rect x="40" y="420" width="16" height="900" fill="#7a4a24" stroke="{OL}" stroke-width="4"/>'
    b += cel('<path d="M40 470 Q120 480 130 640 L-10 640Z"/>', "#e2b84a", "#b88f2a", None, -8, 0, 6)
    # suelo
    b += '<rect x="0" y="1360" width="1080" height="560" fill="#c99a6a"/>'
    for y in range(1360, 1920, 80): b += f'<path d="M0 {y} L1080 {y}" stroke="#ad7f52" stroke-width="4"/>'
    b += '<rect x="330" y="1380" width="420" height="120" rx="20" fill="#7a4fc2" opacity="0.8"/><text x="540" y="1462" font-family="Anton" font-size="60" text-anchor="middle" fill="#f6efe2">HOLA</text>'
    return svg(1080, 1920, b, d)

def bg_noche():
    """Cuarto de mamá de noche: oscuro, azul, con la luz del celular."""
    d = sky("nn", [(0, "#151a33"), (1, "#0b0d1c")])
    b = '<rect width="1080" height="1920" fill="url(#nn)"/>'
    b += f'<rect x="640" y="200" width="320" height="400" rx="14" fill="#1f2b52" stroke="#0a0a14" stroke-width="10"/>'
    b += '<circle cx="860" cy="320" r="50" fill="#f6f0d0" opacity="0.9"/><circle cx="880" cy="305" r="46" fill="#1f2b52"/>'
    r = random.Random(4)
    for _ in range(20): b += f'<circle cx="{r.randint(660, 940)}" cy="{r.randint(220, 580)}" r="3" fill="#fff" opacity="{r.random()*.8+.2:.2f}"/>'
    b += '<path d="M800 200 L800 600 M640 400 L960 400" stroke="#0a0a14" stroke-width="10"/>'
    # cama (almohada y sábana)
    b += '<path d="M-20 1250 Q540 1160 1100 1250 L1100 1940 L-20 1940Z" fill="#2c3768"/>'
    b += '<path d="M-20 1380 Q540 1300 1100 1380" stroke="#3a4a86" stroke-width="16" fill="none"/>'
    b += '<ellipse cx="300" cy="1180" rx="260" ry="90" fill="#46558f"/>'
    return svg(1080, 1920, b, d)

# ============================================================ PERSONAJES
def _mateo_cuerpo():
    b = ''
    # camiseta verde con dino
    torso = '<path d="M150 1100 L160 900 Q170 760 300 720 Q400 700 500 720 Q630 760 640 900 L650 1100Z"/>'
    b += cel(torso, TEE, TEES, TEEH, -46, -8, 8)
    b += (f'<path d="M300 960 Q320 880 400 890 Q420 850 460 856 Q492 864 480 890 L456 894 Q470 950 430 968 L430 1000 M350 968 L350 1000 M300 960 Q280 940 284 916" '
          f'stroke="#f6efe2" stroke-width="13" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    b += '<circle cx="462" cy="872" r="6" fill="#f6efe2"/>'
    b += cel('<path d="M330 712 Q400 760 470 712 L462 700 Q400 732 338 700Z"/>', TEES, "#2c7040", None, -4, 0, 5)
    # brazos
    b += cel('<path d="M170 800 Q110 900 120 1010 L180 1016 Q186 920 220 860Z"/>', TEE, TEES, None, 10, 0, 7)
    b += cel('<path d="M630 800 Q690 900 680 1010 L620 1016 Q614 920 580 860Z"/>', TEE, TEES, None, -10, 0, 7)
    b += cel('<ellipse cx="150" cy="1036" rx="42" ry="40"/>', SK, SKS, None, 8, -4, 6)
    b += cel('<ellipse cx="650" cy="1036" rx="42" ry="40"/>', SK, SKS, None, -8, -4, 6)
    return b

def _mateo_cabeza():
    b = neck(362, 590, 76, 70)
    b += face(400, 430, 165)
    # pelo revuelto castaño
    b += cel('<path d="M232 420 Q214 250 330 214 Q400 180 480 210 Q590 250 572 420 Q556 330 500 300 Q470 340 420 318 Q380 350 330 316 Q280 340 262 400Z"/>',
             HAIR, HAIRS, HAIRH, -26, -14, 8)
    b += cel('<path d="M380 214 Q390 150 440 160 Q420 186 430 214Z"/>', HAIR, HAIRS, None, -6, -4, 6)
    b += cel('<path d="M300 236 Q260 200 268 160 Q300 200 336 222Z"/>', HAIR, HAIRS, None, -6, -4, 6)
    # mofletes
    b += '<ellipse cx="290" cy="520" rx="40" ry="24" fill="#f08a7a" opacity="0.45"/><ellipse cx="510" cy="520" rx="40" ry="24" fill="#f08a7a" opacity="0.45"/>'
    b += cel('<path d="M392 440 Q430 486 408 504 Q390 510 376 498 Q378 470 392 440Z"/>', SK, SKS, None, -8, -4, 5)
    return b

def _cejas(kind):
    if kind == "enojado":
        return ('<path d="M290 360 L380 394" stroke="#2f1c12" stroke-width="16" stroke-linecap="round"/>'
                '<path d="M510 360 L420 394" stroke="#2f1c12" stroke-width="16" stroke-linecap="round"/>')
    if kind in ("llora", "triste", "timido"):
        return ('<path d="M290 384 Q330 352 380 352" stroke="#2f1c12" stroke-width="14" fill="none" stroke-linecap="round"/>'
                '<path d="M510 384 Q470 352 420 352" stroke="#2f1c12" stroke-width="14" fill="none" stroke-linecap="round"/>')
    return ('<path d="M292 372 Q334 346 378 362" stroke="#2f1c12" stroke-width="14" fill="none" stroke-linecap="round"/>'
            '<path d="M508 372 Q466 346 422 362" stroke="#2f1c12" stroke-width="14" fill="none" stroke-linecap="round"/>')

def _ojos(kind):
    if kind == "llora":   # ojos apretados con lagrimones
        b = ('<path d="M298 430 Q336 412 372 432" stroke="#1d1630" stroke-width="9" fill="none" stroke-linecap="round"/>'
             '<path d="M428 432 Q464 412 502 430" stroke="#1d1630" stroke-width="9" fill="none" stroke-linecap="round"/>')
        for x in (330, 470):
            b += f'<path d="M{x} 446 Q{x-14} 520 {x-6} 600 Q{x+10} 610 {x+16} 596 Q{x+16} 520 {x+10} 446Z" fill="#8fd0ff" stroke="#3a7fbf" stroke-width="4" opacity="0.92"/>'
        return b
    look = {"timido": 0, "enojado": 0}.get(kind, 0)
    b = eye(336, 432, 21, look) + eye(464, 432, 21, look)
    if kind == "timido":
        b = (f'<ellipse cx="336" cy="432" rx="32" ry="28" fill="#fff" stroke="{OL}" stroke-width="4"/><circle cx="338" cy="420" r="21" fill="#4a3424"/><circle cx="338" cy="420" r="11" fill="{OL}"/><circle cx="346" cy="410" r="7" fill="#fff"/>'
             f'<ellipse cx="464" cy="432" rx="32" ry="28" fill="#fff" stroke="{OL}" stroke-width="4"/><circle cx="466" cy="420" r="21" fill="#4a3424"/><circle cx="466" cy="420" r="11" fill="{OL}"/><circle cx="474" cy="410" r="7" fill="#fff"/>')
        b += '<ellipse cx="290" cy="520" rx="50" ry="28" fill="#f2707a" opacity="0.55"/><ellipse cx="510" cy="520" rx="50" ry="28" fill="#f2707a" opacity="0.55"/>'
    if kind == "triste":   # ojos aguados con lágrima a punto de caer
        b += '<path d="M306 454 Q336 470 366 454" stroke="#8fd0ff" stroke-width="10" fill="none" stroke-linecap="round" opacity="0.9"/>'
        b += '<path d="M434 454 Q464 470 494 454" stroke="#8fd0ff" stroke-width="10" fill="none" stroke-linecap="round" opacity="0.9"/>'
        b += '<path d="M480 470 Q470 500 480 512 Q494 510 492 492Z" fill="#8fd0ff" stroke="#3a7fbf" stroke-width="3"/>'
    if kind == "enojado":
        b += '<path d="M300 408 L372 420" stroke="#f3c29b" stroke-width="18"/><path d="M500 408 L428 420" stroke="#f3c29b" stroke-width="18"/>'
    return b

def _boca(kind):
    return {
        "neutral": '<path d="M360 552 Q400 584 440 552" stroke="#1d1630" stroke-width="9" fill="none" stroke-linecap="round"/>',
        "enojado": '<path d="M356 572 Q400 546 444 572" stroke="#1d1630" stroke-width="10" fill="none" stroke-linecap="round"/><path d="M380 548 Q400 538 420 548" stroke="#c98a62" stroke-width="5" fill="none"/>',
        "llora": '<path d="M346 544 Q400 520 454 544 Q446 612 400 616 Q354 612 346 544Z" fill="#7a1e2c" stroke="#1d1630" stroke-width="8"/><path d="M366 590 Q400 572 434 590 Q420 610 400 610 Q380 610 366 590Z" fill="#e2707a"/>',
        "triste": '<path d="M360 574 Q380 556 400 566 Q420 556 440 574" stroke="#1d1630" stroke-width="9" fill="none" stroke-linecap="round"/>',
        "timido": '<path d="M372 556 Q400 574 428 556" stroke="#1d1630" stroke-width="8" fill="none" stroke-linecap="round"/>',
    }[kind]

def mateo(kind="neutral", hablando=False):
    """Mateo, 5 años y medio. hablando=True deja la boca vacía para animarla en el montaje (centro 400,560)."""
    h = _mateo_cabeza() + _cejas(kind) + _ojos(kind)
    if not hablando: h += _boca(kind)
    # cabeza grande de niño pequeño (boca hablando en 400,606)
    b = _mateo_cuerpo() + f'<g transform="translate(400,700) scale(1.18) translate(-400,-640)">{h}</g>'
    return svg(800, 1100, b)

def abuela(hablando=False):
    """Abuela Pilar: moño canoso, lentes, rebeca morada, collar de perlas, cara de 'en mis tiempos'."""
    b = ''
    torso = '<path d="M110 1300 L120 980 Q130 760 280 700 Q400 670 520 700 Q670 760 680 980 L690 1300Z"/>'
    b += cel(torso, "#8a5aa8", "#68407f", "#a77cc4", -50, -10, 8)
    b += cel('<path d="M330 690 L400 820 L470 690 L460 676 L400 760 L340 676Z"/>', "#f6efe2", "#d9cfbd", None, -8, 0, 5)
    for k in range(5): b += f'<circle cx="{400}" cy="{860+k*70}" r="12" fill="#e2b84a" stroke="{OL}" stroke-width="3"/>'
    for i, a in enumerate(range(-60, 61, 20)):
        b += f'<circle cx="{400 + a * 1.4}" cy="{700 + abs(a) * -0.6 + 64}" r="13" fill="#fbf6ee" stroke="{OL}" stroke-width="3"/>'
    # brazos cruzados
    b += cel('<path d="M150 980 Q400 900 650 980 L650 1070 Q400 1000 150 1070Z"/>', "#7a4c96", "#5a3672", "#9a6cb8", -10, -12, 7)
    b += cel('<ellipse cx="630" cy="1020" rx="46" ry="38"/>', SK, SKS, None, -10, -6, 6)
    b += cel('<ellipse cx="170" cy="1020" rx="46" ry="38"/>', SK, SKS, None, 10, -6, 6)
    b += '<g transform="translate(0,90)">'
    b += neck(358, 460, 84, 120)
    b += face(400, 360, 132)
    # pelo canoso con moño
    b += cel('<circle cx="400" cy="170" r="74"/>', "#e4e4ea", "#b9b9c4", "#ffffff", -14, -10, 7)
    b += cel('<path d="M270 360 Q256 220 400 210 Q544 220 530 360 Q512 286 440 270 Q400 300 360 270 Q290 286 270 360Z"/>', "#e4e4ea", "#b9b9c4", "#ffffff", -20, -10, 7)
    # cejas levantadas (desaprobación)
    b += '<path d="M318 300 Q350 284 382 300" stroke="#9a9aa6" stroke-width="12" fill="none" stroke-linecap="round"/><path d="M418 296 Q452 276 486 290" stroke="#9a9aa6" stroke-width="12" fill="none" stroke-linecap="round"/>'
    # ojos medio cerrados detrás de los lentes
    b += eye(350, 352, 12) + eye(452, 352, 12)
    b += '<path d="M326 342 Q350 330 374 342 L374 336 Q350 322 326 336Z" fill="#f3c29b" stroke="#1d1630" stroke-width="4"/>'
    b += '<path d="M428 342 Q452 330 476 342 L476 336 Q452 322 428 336Z" fill="#f3c29b" stroke="#1d1630" stroke-width="4"/>'
    b += f'<rect x="310" y="318" width="84" height="70" rx="20" fill="#cfe6ff" fill-opacity="0.25" stroke="#8a5a2a" stroke-width="7"/>'
    b += f'<rect x="410" y="318" width="84" height="70" rx="20" fill="#cfe6ff" fill-opacity="0.25" stroke="#8a5a2a" stroke-width="7"/>'
    b += '<path d="M394 346 L410 346" stroke="#8a5a2a" stroke-width="7"/>'
    b += cel('<path d="M392 366 Q430 404 410 424 Q392 430 378 418 Q378 392 392 366Z"/>', SK, SKS, None, -8, -4, 5)
    b += '<path d="M316 410 Q330 430 324 446 M484 410 Q470 430 476 446" stroke="#c98a62" stroke-width="5" fill="none"/>'
    b += '<ellipse cx="330" cy="420" rx="24" ry="14" fill="#e7887a" opacity="0.4"/><ellipse cx="474" cy="420" rx="24" ry="14" fill="#e7887a" opacity="0.4"/>'
    if not hablando:
        b += '<path d="M366 466 Q400 452 434 466" stroke="#9a2a3a" stroke-width="9" fill="none" stroke-linecap="round"/>'
    b += '</g>'
    return svg(800, 1300, b)

# ============================================================ OBJETOS
def mochila():
    b = cel('<path d="M160 260 Q160 150 400 140 Q640 150 640 260 L660 900 Q400 960 140 900Z"/>', "#e2483b", "#b8342a", "#f26a5c", -30, -10, 8)
    b += cel('<path d="M220 560 L580 560 L590 860 Q400 900 210 860Z"/>', "#c93a2e", "#9e2a22", None, -12, 0, 7)
    b += f'<path d="M220 600 L580 600" stroke="#f6efe2" stroke-width="10" stroke-dasharray="26 16"/>'
    b += cel('<path d="M300 150 Q400 40 500 150 L470 160 Q400 90 330 160Z"/>', "#9e2a22", "#7a1e18", None, -6, 0, 6)
    # llavero de dino
    b += f'<path d="M600 300 Q660 330 650 400" stroke="#c9a24a" stroke-width="7" fill="none"/>'
    b += cel('<path d="M610 420 Q620 380 660 384 Q672 360 690 366 Q704 374 696 390 L684 392 Q692 430 670 440 L670 460 M630 440 L630 460 Z"/>', TEE, TEES, None, -6, 0, 5)
    # nota asomando
    b += '<g transform="rotate(-10 400 300)"><rect x="300" y="200" width="240" height="190" fill="#fffdf4" stroke="#1d1630" stroke-width="6"/>'
    for k in range(4): b += f'<rect x="324" y="{240+k*34}" width="{190 - k*20}" height="10" rx="5" fill="#e2483b" opacity="0.8"/>'
    b += '</g>'
    return svg(800, 1000, b)

def nota():
    """Hoja de cuaderno escolar con renglones (el texto en rojo se escribe en el montaje)."""
    b = '<rect x="20" y="20" width="900" height="1100" rx="10" fill="#fffdf4" stroke="#1d1630" stroke-width="8" filter="url(#drop)"/>'
    for y in range(180, 1100, 70): b += f'<path d="M40 {y} L900 {y}" stroke="#9cc4e8" stroke-width="3"/>'
    b += '<path d="M130 30 L130 1110" stroke="#f08a8a" stroke-width="4"/>'
    for y in (140, 560, 980): b += f'<circle cx="70" cy="{y}" r="22" fill="#e9dcc4" stroke="#1d1630" stroke-width="4"/>'
    return svg(940, 1140, b)

def hoja():
    """Hoja blanca con pauta para escribir el nombre (las letras se dibujan en el montaje)."""
    b = '<rect x="20" y="20" width="900" height="640" rx="8" fill="#fffef8" stroke="#1d1630" stroke-width="7" filter="url(#drop)"/>'
    for y0 in (110, 400):
        b += f'<path d="M60 {y0} L880 {y0}" stroke="#8ab7e8" stroke-width="4"/><path d="M60 {y0+110} L880 {y0+110}" stroke="#d96a6a" stroke-width="4" stroke-dasharray="18 12"/><path d="M60 {y0+220} L880 {y0+220}" stroke="#8ab7e8" stroke-width="4"/>'
    return svg(940, 680, b)

def lapiz():
    b = '<g transform="rotate(-30 400 200)">'
    b += cel('<rect x="120" y="170" width="520" height="64" rx="8"/>', "#f2c84b", "#d1a532", "#fbe08a", 0, -10, 6)
    b += cel('<rect x="90" y="170" width="50" height="64" rx="6"/>', "#c9cfd9", "#9aa2ae", None, 0, -6, 5)
    b += cel('<rect x="50" y="172" width="48" height="60" rx="14"/>', "#f08a9a", "#c96a7a", None, 0, -6, 5)
    b += cel('<path d="M640 170 L740 202 L640 234Z"/>', "#f2d2a8", "#d6b088", None, 0, -4, 5)
    b += f'<path d="M712 192 L740 202 L712 212Z" fill="{OL}"/>'
    b += '</g>'
    return svg(800, 420, b)

def vaso():
    b = cel('<path d="M250 160 L550 160 L510 760 L290 760Z"/>', "#eaf6ff", "#c5dbe8", "#ffffff", -20, 0, 7)
    b += '<path d="M262 320 L538 320 L512 750 L288 750Z" fill="#fffef6" stroke="#1d1630" stroke-width="5"/>'
    b += '<path d="M280 360 L300 700" stroke="#ffffff" stroke-width="16" stroke-linecap="round" opacity="0.8"/>'
    return svg(800, 860, b)

def dino():
    """Peluche de T-rex verde: 'el Rex'."""
    b = cel('<path d="M200 760 Q140 600 220 480 Q260 340 420 330 Q470 220 600 230 Q720 240 720 340 Q720 420 640 430 L560 430 Q600 560 540 680 Q500 760 420 770Z"/>', "#6cc46a", "#4a9c4a", "#94dc8e", -30, -10, 8)
    b += cel('<path d="M210 680 Q80 700 40 610 Q120 640 220 600Z"/>', "#6cc46a", "#4a9c4a", None, 10, -4, 7)
    b += cel('<ellipse cx="380" cy="600" rx="110" ry="130"/>', "#d9f2b0", "#b8d88a", None, -12, -6, 6)
    b += cel('<ellipse cx="300" cy="790" rx="70" ry="40"/>', "#4a9c4a", "#367a36", None, -8, -4, 6)
    b += cel('<ellipse cx="480" cy="790" rx="70" ry="40"/>', "#4a9c4a", "#367a36", None, -8, -4, 6)
    b += cel('<path d="M520 470 Q560 500 540 540 Q500 530 500 490Z"/>', "#4a9c4a", "#367a36", None, -4, 0, 5)
    for k in range(5):
        x = 260 + k * 60; y = 360 - k * 10 + (0 if k < 3 else 30)
        b += cel(f'<path d="M{x} {y+40} L{x+24} {y-10} L{x+48} {y+40}Z"/>', "#f2c84b", "#d1a532", None, -4, 0, 5)
    b += eye(600, 300, 18)
    b += '<path d="M640 380 Q680 400 710 380" stroke="#1d1630" stroke-width="7" fill="none" stroke-linecap="round"/>'
    b += '<path d="M650 384 l8 14 l8 -14 M674 386 l8 14 l8 -14" fill="#fff" stroke="#1d1630" stroke-width="3"/>'
    b += '<ellipse cx="660" cy="350" rx="20" ry="10" fill="#f08a7a" opacity="0.5"/>'
    # costura de peluche
    b += '<path d="M300 480 Q380 450 460 480" stroke="#367a36" stroke-width="5" fill="none" stroke-dasharray="12 10"/>'
    return svg(800, 860, b)

def crayola():
    b = '<g transform="rotate(-20 300 150)">'
    b += cel('<rect x="80" y="110" width="400" height="80" rx="16"/>', "#3fae4a", "#2c8236", "#6fd078", 0, -10, 6)
    b += '<rect x="160" y="112" width="180" height="76" fill="#f6efe2" stroke="#1d1630" stroke-width="4"/><text x="250" y="166" font-family="Anton" font-size="40" text-anchor="middle" fill="#2c8236">VERDE</text>'
    b += cel('<path d="M480 116 L560 150 L480 184Z"/>', "#3fae4a", "#2c8236", None, 0, -4, 5)
    b += '</g>'
    return svg(620, 320, b)

def tablet():
    b = cel('<rect x="100" y="80" width="600" height="440" rx="40"/>', "#2a2a36", "#1a1a24", "#40404e", -16, -8, 8)
    b += '<rect x="140" y="118" width="520" height="364" rx="14" fill="#3a6ad0"/>'
    b += '<circle cx="400" cy="270" r="90" fill="#f6efe2" opacity="0.15"/>'
    b += cel('<rect x="336" y="270" width="128" height="104" rx="14"/>', "#e2b84a", "#b88f2a", None, -8, 0, 6)
    b += '<path d="M360 270 L360 228 Q400 180 440 228 L440 270" stroke="#1d1630" stroke-width="16" fill="none"/>'
    b += '<path d="M360 270 L360 228 Q400 180 440 228 L440 270" stroke="#c9cfd9" stroke-width="8" fill="none"/>'
    b += '<circle cx="400" cy="318" r="14" fill="#1d1630"/>'
    return svg(800, 600, b)

LAYERS = {"bg_cocina": bg_cocina, "bg_cuarto": bg_cuarto, "bg_mesa": bg_mesa, "bg_puerta": bg_puerta, "bg_noche": bg_noche,
          "mochila": mochila, "nota": nota, "hoja": hoja, "lapiz": lapiz, "vaso": vaso, "dino": dino, "crayola": crayola, "tablet": tablet,
          "abuela": lambda: abuela(False), "abuela_hab": lambda: abuela(True)}
for k in ("neutral", "enojado", "llora", "triste", "timido"):
    LAYERS["mateo_" + k] = (lambda kk: (lambda: mateo(kk)))(k)
    LAYERS["mateo_" + k + "_hab"] = (lambda kk: (lambda: mateo(kk, True)))(k)

FONT_CSS = ("@font-face{font-family:Anton;src:url(file://%s/fonts/Anton-Regular.ttf)}"
            "@font-face{font-family:Caveat;font-weight:700;src:url(file://%s/fonts/Caveat.ttf)}") % (HERE, HERE)

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
            pg.goto("file://" + hp); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(120)
            pg.screenshot(path=os.path.join(OUT, name + ".png"), omit_background=True)
            pg.close(); print("ok", name, flush=True)
        br.close()
        os.remove(os.path.join(OUT, "_tmp.html"))
