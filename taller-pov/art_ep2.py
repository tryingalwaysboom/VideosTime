"""Arte nuevo del Ep.2: Lucía, Seat de rally, fotos R96, llave Nave 7, centralita, cuadro de mandos, caja."""
import math, os, re, sys, random
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import art, cars
from art import svg, cel, eye, face, neck, SK, SKS, OL, NEON_C, NEON_M, OUT, FONT_CSS

def lucia():
    """Lucía, 24, piloto de rally: mono de carreras rojo y blanco, coleta, casco bajo el brazo."""
    b = ''
    # coleta detrás
    b += cel('<path d="M470 260 Q600 300 590 520 Q570 640 520 700 Q540 560 500 420Z"/>', "#5a2e1e", "#3a1c12", "#7a4430", -14, -6, 7)
    torso = '<path d="M120 1400 L130 1000 Q128 720 270 655 Q400 615 530 655 Q672 720 670 1000 L680 1400Z"/>'
    b += cel(torso, "#d8322e", "#a52220", "#f05a50", -50, -10, 8)
    b += '<path d="M330 660 L400 1400 L470 660Z" fill="#f2f2f4"/>'
    b += '<path d="M150 900 L650 900 L650 960 L150 960Z" fill="#1d1630" opacity="0.85"/>'
    b += '<text x="400" y="945" font-family="Anton" font-size="44" text-anchor="middle" fill="#fff">RALLY TEAM</text>'
    b += '<rect x="190" y="740" width="110" height="60" rx="8" fill="#f2c94c" stroke="#1d1630" stroke-width="4"/><text x="245" y="783" font-family="Anton" font-size="36" text-anchor="middle" fill="#1d1630">27</text>'
    b += f'<path d="M400 660 L400 1400" stroke="{OL}" stroke-width="6"/>'
    b += cel('<path d="M330 640 L400 700 L470 640 L455 610 L400 650 L345 610Z"/>', "#1d1630", "#0d0a18", None, -6, 0, 5)
    # casco bajo el brazo
    b += cel('<path d="M470 1040 Q470 900 600 890 Q730 900 730 1040 Q730 1130 600 1140 Q470 1130 470 1040Z"/>', "#f2f2f4", "#c4c6d0", "#ffffff", -20, -10, 7)
    b += '<path d="M500 1010 Q600 960 720 1010 L720 1060 Q600 1030 500 1060Z" fill="#26324a" stroke="#1d1630" stroke-width="5"/>'
    b += '<path d="M480 1090 L720 1090" stroke="#d8322e" stroke-width="16"/>'
    b += cel('<ellipse cx="560" cy="1150" rx="46" ry="36"/>', SK, SKS, None, -8, -4, 6)
    # cabeza
    b += '<g transform="translate(0,120)">'
    b += neck(352, 410, 96, 110)
    b += face(400, 330, 112)
    # pelo con flequillo
    b += cel('<path d="M282 330 Q262 180 400 150 Q540 170 522 330 Q500 240 420 228 Q340 236 300 300Z"/>', "#5a2e1e", "#3a1c12", "#7a4430", -16, -8, 7)
    b += cel('<path d="M300 250 Q360 180 470 196 Q430 236 360 250 Q330 262 300 290Z"/>', "#6a3a26", "#4a2618", None, -8, -4, 5)
    # cejas decididas, ojos, pestañas
    b += '<path d="M318 278 L384 284" stroke="#3a1c12" stroke-width="10" stroke-linecap="round"/><path d="M416 284 L482 278" stroke="#3a1c12" stroke-width="10" stroke-linecap="round"/>'
    b += eye(350, 322, 12) + eye(450, 322, 12)
    b += '<path d="M326 306 L318 298 M336 302 L332 292 M474 306 L482 298 M464 302 L468 292" stroke="#1d1630" stroke-width="4"/>'
    b += cel('<path d="M394 336 Q424 370 408 390 Q394 396 382 386 Q382 360 394 336Z"/>', SK, SKS, None, -6, -4, 4)
    b += '<ellipse cx="322" cy="388" rx="24" ry="14" fill="#e7887a" opacity="0.5"/><ellipse cx="478" cy="388" rx="24" ry="14" fill="#e7887a" opacity="0.5"/>'
    # sonrisa segura
    b += '<path d="M354 424 Q400 462 448 422" stroke="#1d1630" stroke-width="7" fill="#fff" stroke-linecap="round"/>'
    # mancha de grasa y pendiente
    b += '<ellipse cx="460" cy="406" rx="18" ry="8" fill="#2a2420" opacity="0.35" transform="rotate(-20 460 406)"/>'
    b += '<circle cx="290" cy="378" r="7" fill="#c9cfd9" stroke="#1d1630" stroke-width="3"/>'
    b += '</g>'
    return svg(800, 1400, b)

def seat_rally():
    d, b = cars.utilitario(rally=True)
    return svg(1080, 580, b, d)

def foto_r96():
    """Polaroid vieja: Rubén y Nitro de jóvenes, abrazados, con chaquetas iguales R96."""
    b = '<g filter="url(#drop)">'
    b += f'<rect x="20" y="20" width="560" height="640" fill="#efe6cf" stroke="{OL}" stroke-width="6"/></g>'
    b += '<rect x="50" y="50" width="500" height="470" fill="#3c4a6a"/>'
    b += '<rect x="50" y="380" width="500" height="140" fill="#2a2a32"/>'
    for x in (90, 170, 250, 330, 410, 490):
        b += f'<rect x="{x}" y="90" width="40" height="160" fill="#f2c94c" opacity="0.25"/>'
    for cx, hair, skin in ((210, "#4a3a30", SK), (390, "#2a2420", "#f0bd96")):
        b += f'<g transform="translate({cx},360) scale(0.36) translate(-400,-560)">'
        b += cel('<path d="M110 1000 Q108 700 260 640 Q400 600 540 640 Q692 700 690 1000Z"/>', "#1d1d26", "#0e0e14", "#3a3a48", -30, -8, 10)
        b += '<text x="400" y="860" font-family="Anton" font-size="120" text-anchor="middle" fill="#ff4fd8">R96</text>'
        b += neck(352, 530, 96, 110) + face(400, 450, 118)
        b += cel('<path d="M286 430 Q280 300 400 290 Q520 300 514 430 Q480 360 400 360 Q320 360 286 430Z"/>', hair, "#1a1410", None, -14, -6, 8)
        b += eye(352, 446, 14) + eye(448, 446, 14)
        b += '<path d="M350 540 Q400 580 450 540" stroke="#1d1630" stroke-width="9" fill="#fff" stroke-linecap="round"/>'
        b += '</g>'
    b += '<path d="M260 470 Q300 430 340 470" stroke="#1d1d26" stroke-width="22" fill="none"/>'  # brazos abrazados
    b += '<rect x="50" y="50" width="500" height="470" fill="#c8a060" opacity="0.18"/>'
    b += '<text x="300" y="610" font-family="Caveat" font-weight="700" font-size="56" text-anchor="middle" fill="#2a2a5a">Rubén y Iván · 1996</text>'
    b += '<rect x="230" y="0" width="140" height="44" fill="#e8d98a" opacity="0.85" transform="rotate(4 300 22)"/>'
    return svg(600, 680, b)

def llave_nave7():
    b = '<g filter="url(#drop)">'
    b += f'<circle cx="150" cy="200" r="70" fill="#c9a24a" stroke="{OL}" stroke-width="8"/><circle cx="150" cy="200" r="24" fill="#3a2a1a"/>'
    b += f'<rect x="215" y="182" width="300" height="36" fill="#c9a24a" stroke="{OL}" stroke-width="7"/>'
    b += f'<path d="M440 218 l0 34 l22 0 l0 -18 l20 0 l0 26 l22 0 l0 -42" fill="#c9a24a" stroke="{OL}" stroke-width="6"/>'
    b += f'<path d="M86 180 Q30 120 80 60" stroke="#8a7a5a" stroke-width="6" fill="none"/>'
    b += f'<g transform="translate(40,60) rotate(-12 80 60)"><rect x="-10" y="-10" width="210" height="110" rx="12" fill="#f2efe8" stroke="{OL}" stroke-width="6"/>'
    b += '<circle cx="14" cy="45" r="10" fill="#1d1630"/>'
    b += '<text x="110" y="70" font-family="Caveat" font-weight="700" font-size="58" text-anchor="middle" fill="#c62f2f">Nave 7</text></g>'
    b += '</g>'
    return svg(560, 320, b)

def centralita():
    b = '<g filter="url(#drop)">'
    b += cel('<rect x="40" y="60" width="440" height="280" rx="18"/>', "#6a707c", "#4a505a", "#8a909c", -20, -8, 8)
    for i in range(10): b += f'<rect x="{70 + i*40}" y="40" width="20" height="30" fill="#c9cfd9" stroke="{OL}" stroke-width="3"/>'
    b += f'<rect x="90" y="120" width="340" height="160" rx="10" fill="#1d4a2e" stroke="{OL}" stroke-width="5"/>'
    for i in range(6): b += f'<rect x="{110 + i*52}" y="150" width="34" height="34" fill="#111" stroke="#2f6a44" stroke-width="3"/>'
    b += '<path d="M110 220 L410 220 M110 250 L380 250" stroke="#d4b04a" stroke-width="4"/>'
    b += '<text x="260" y="320" font-family="Anton" font-size="34" text-anchor="middle" fill="#1d1630">ECU · ORIGINAL</text>'
    b += '</g>'
    return svg(520, 380, b)

def cuadro():
    """Cuadro de mandos del deportivo, apagado."""
    b = '<rect width="1080" height="700" fill="#0c0b12"/>'
    b += cel('<path d="M40 700 Q60 200 540 160 Q1020 200 1040 700Z"/>', "#1d1c26", "#121118", "#2e2d3a", -20, -10, 8)
    for cx, lab in ((330, "RPM"), (750, "KM/H")):
        b += f'<circle cx="{cx}" cy="440" r="190" fill="#08080c" stroke="#3a3a48" stroke-width="12"/>'
        for k in range(11):
            a = math.radians(135 + k * 27)
            b += f'<line x1="{cx + 150*math.cos(a):.0f}" y1="{440 + 150*math.sin(a):.0f}" x2="{cx + 175*math.cos(a):.0f}" y2="{440 + 175*math.sin(a):.0f}" stroke="#5a5a68" stroke-width="7"/>'
        b += f'<line x1="{cx}" y1="440" x2="{cx - 110}" y2="{440 + 100}" stroke="#7a2a2a" stroke-width="10" stroke-linecap="round"/>'
        b += f'<circle cx="{cx}" cy="440" r="18" fill="#2a2a33"/>'
        b += f'<text x="{cx}" y="560" font-family="Anton" font-size="40" text-anchor="middle" fill="#3a3a48">{lab}</text>'
    b += '<rect x="500" y="560" width="80" height="40" rx="6" fill="#141420" stroke="#3a3a48" stroke-width="4"/>'
    # llave puesta en el contacto
    b += f'<g transform="rotate(20 960 560)"><rect x="900" y="545" width="120" height="30" rx="8" fill="#c9cfd9" stroke="{OL}" stroke-width="5"/><circle cx="1040" cy="560" r="34" fill="#1d1d26" stroke="{OL}" stroke-width="5"/></g>'
    return svg(1080, 700, b)

def caja():
    b = '<ellipse cx="260" cy="390" rx="230" ry="26" fill="#000" opacity="0.4"/>'
    b += cel('<path d="M40 150 L480 150 L460 380 L60 380Z"/>', "#b98a52", "#8a6238", "#d4a468", -20, -8, 8)
    b += cel('<path d="M40 150 L120 60 L400 60 L480 150Z"/>', "#c99a62", "#9a7040", None, -8, 0, 7)
    b += '<path d="M60 230 L460 230" stroke="#8a6238" stroke-width="6"/>'
    b += '<text x="260" y="320" font-family="Caveat" font-weight="700" font-size="60" text-anchor="middle" fill="#3a2a1a">R. — NO TIRAR</text>'
    return svg(520, 420, b)

LAYERS = {"lucia": lucia, "seat_rally": seat_rally, "foto_r96": foto_r96, "llave_nave7": llave_nave7,
          "centralita": centralita, "cuadro": cuadro, "caja": caja}

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
