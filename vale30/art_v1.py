"""Capas del Día 1 de «30 días sin celular». Uso: python3 art_v1.py"""
import os, re, random, math
from playwright.sync_api import sync_playwright
import art_vale as A
from art_vale import OL, SK, SKS, HAIR, HAIR2, HOOD, HOODS, PAPER, svg, nota, caja, FONT_CSS, HERE

def ojo(cx, cy, mirada=(0, 10), parpado=.42, ojera=True):
    b = f'<ellipse cx="{cx}" cy="{cy}" rx="74" ry="86" fill="#fff" stroke="{OL}" stroke-width="8"/>'
    b += f'<circle cx="{cx + mirada[0]}" cy="{cy + mirada[1]}" r="{44 if parpado > .05 else 34}" fill="#22b8aa"/><circle cx="{cx + mirada[0]}" cy="{cy + mirada[1]}" r="{22 if parpado > .05 else 15}" fill="{OL}"/><circle cx="{cx + mirada[0] - 14}" cy="{cy + mirada[1] - 16}" r="11" fill="#fff"/>'
    if parpado > .05:
        yp = cy - 86 + 172 * parpado
        b += f'<clipPath id="c{cx}"><ellipse cx="{cx}" cy="{cy}" rx="74" ry="86"/></clipPath><rect x="{cx - 80}" y="{cy - 90}" width="160" height="{yp - cy + 90}" fill="{SKS}" clip-path="url(#c{cx})"/>'
        b += f'<path d="M{cx - 74} {yp} Q{cx} {yp + 16} {cx + 74} {yp}" stroke="{OL}" stroke-width="10" fill="none" stroke-linecap="round"/>'
    if ojera: b += f'<path d="M{cx - 60} {cy + 104} Q{cx} {cy + 124} {cx + 60} {cy + 104}" stroke="#b98ad6" stroke-width="9" fill="none" stroke-linecap="round" opacity=".8"/>'
    return b

CEJAS = {"aburrida": ("M210 336 Q290 300 362 344", "M440 318 Q520 270 596 318"), "shock": ("M214 300 Q290 250 360 296", "M442 296 Q520 250 590 300"),
         "asco": ("M210 350 Q290 330 364 316", "M440 300 Q520 262 596 322"), "orgullosa": ("M214 320 Q290 286 360 320", "M442 320 Q520 286 590 320"),
         "enojada": ("M214 300 Q300 330 366 364", "M436 364 Q500 330 588 300")}
PARP = {"aburrida": .42, "shock": 0, "asco": .34, "orgullosa": .22, "enojada": .18}
MIR = {"aburrida": (0, 10), "shock": (0, 0), "asco": (-18, 14), "orgullosa": (0, 6), "enojada": (0, 4)}
def boca(kind, hab):
    if kind == "shock" or (kind == "enojada" and hab): return f'<ellipse cx="402" cy="658" rx="62" ry="{58 if hab else 50}" fill="#7a1f3d" stroke="{OL}" stroke-width="9"/><path d="M362 690 Q402 716 442 690" fill="#ff7b8a"/><rect x="370" y="610" width="64" height="20" rx="6" fill="#fff"/>'
    if kind == "enojada": return f'<path d="M340 676 Q402 630 466 676" stroke="{OL}" stroke-width="13" fill="none" stroke-linecap="round"/>'
    if kind == "orgullosa": return (f'<path d="M330 636 Q402 720 474 636Z" fill="#7a1f3d" stroke="{OL}" stroke-width="9" stroke-linejoin="round"/><rect x="356" y="640" width="92" height="18" rx="5" fill="#fff"/>' if hab else
                                   f'<path d="M330 640 Q402 706 474 640" stroke="{OL}" stroke-width="13" fill="none" stroke-linecap="round"/>')
    if hab: return f'<ellipse cx="404" cy="656" rx="44" ry="30" fill="#7a1f3d" stroke="{OL}" stroke-width="9"/>'
    return f'<path d="M338 652 Q400 622 470 664" stroke="{OL}" stroke-width="12" fill="none" stroke-linecap="round"/>' if kind != "asco" else f'<path d="M340 670 Q380 640 420 664 Q446 680 470 650" stroke="{OL}" stroke-width="12" fill="none" stroke-linecap="round"/>'

def mano(hx, hy, flip=1):
    b = f'<g transform="translate({hx},{hy}) scale({flip},1)"><ellipse cx="0" cy="0" rx="62" ry="54" fill="{SK}" stroke="{OL}" stroke-width="9"/>'
    for i in range(4): b += f'<rect x="{-50 + i * 26}" y="-74" width="24" height="60" rx="12" fill="{SK}" stroke="{OL}" stroke-width="7"/>'
    return b + '</g>'

def vale(kind="aburrida", hab=False, pose="quieta"):
    b = f'<circle cx="430" cy="118" r="120" fill="{HAIR}" stroke="{OL}" stroke-width="9"/><path d="M360 60 Q420 10 500 70" stroke="{HAIR2}" stroke-width="20" fill="none" stroke-linecap="round"/>'
    for a in (-60, -20, 25, 70): b += f'<path d="M430 118 l{150 * math.sin(math.radians(a)):.0f} {-150 * math.cos(math.radians(a)):.0f}" stroke="{HAIR}" stroke-width="16" stroke-linecap="round"/>'
    # brazos según la pose (detrás del torso)
    if pose == "quieta":
        for sx in (1, -1): b += f'<g transform="translate(400,0) scale({sx},1)"><path d="M-270 860 Q-350 1000 -330 1240 L-240 1240 Q-250 1020 -200 900Z" fill="{HOOD}" stroke="{OL}" stroke-width="10"/></g>'
    b += f'<path d="M90 1300 Q70 840 210 770 Q400 720 590 770 Q730 840 710 1300Z" fill="{HOOD}" stroke="{OL}" stroke-width="10"/>'
    b += f'<path d="M250 770 Q400 900 550 770 Q470 730 400 734 Q330 730 250 770Z" fill="{HOODS}" stroke="{OL}" stroke-width="9"/>'
    b += f'<path d="M350 840 L340 980" stroke="#fff6dc" stroke-width="12" stroke-linecap="round"/><path d="M450 840 L462 990" stroke="#fff6dc" stroke-width="12" stroke-linecap="round"/>'
    b += f'<rect x="320" y="1090" width="160" height="120" rx="24" fill="{HOODS}" stroke="{OL}" stroke-width="8"/>'
    b += f'<rect x="352" y="640" width="96" height="130" rx="30" fill="{SKS}" stroke="{OL}" stroke-width="9"/>'
    b += f'<path d="M140 420 Q140 170 400 170 Q660 170 660 420 Q660 600 520 690 Q400 750 280 690 Q140 600 140 420Z" fill="{SK}" stroke="{OL}" stroke-width="10"/>'
    b += f'<ellipse cx="136" cy="450" rx="34" ry="50" fill="{SK}" stroke="{OL}" stroke-width="9"/><ellipse cx="664" cy="450" rx="34" ry="50" fill="{SK}" stroke="{OL}" stroke-width="9"/><circle cx="672" cy="520" r="24" fill="none" stroke="{HAIR2}" stroke-width="9"/>'
    b += f'<path d="M134 430 Q110 150 400 150 Q690 150 666 430 Q640 300 540 250 Q560 330 470 300 Q420 250 300 330 Q220 300 190 360 Q150 380 134 430Z" fill="{HAIR}" stroke="{OL}" stroke-width="10" stroke-linejoin="round"/>'
    b += f'<path d="M480 190 Q560 220 590 300" stroke="{HAIR2}" stroke-width="22" fill="none" stroke-linecap="round"/>'
    b += ojo(292, 452, MIR[kind], PARP[kind]) + ojo(508, 452, MIR[kind], PARP[kind])
    c1, c2 = CEJAS[kind]; b += f'<path d="{c1}" stroke="{OL}" stroke-width="20" fill="none" stroke-linecap="round"/><path d="{c2}" stroke="{OL}" stroke-width="20" fill="none" stroke-linecap="round"/>'
    b += f'<path d="M388 560 Q402 584 420 562" stroke="{OL}" stroke-width="8" fill="none" stroke-linecap="round"/>'
    for x, y in ((230, 590), (262, 606), (246, 626), (540, 606), (572, 590), (556, 626)): b += f'<circle cx="{x}" cy="{y}" r="7" fill="#d98f66"/>'
    b += boca(kind, hab)
    if pose == "nota":
        b += f'<g transform="translate(190,830) rotate(-5)">{nota()}</g>' + mano(170, 1010) + mano(640, 1010)
        b += f'<path d="M90 1300 Q70 1040 150 1040 L230 1060 L240 1300Z" fill="{HOOD}" stroke="{OL}" stroke-width="10"/><path d="M710 1300 Q730 1040 660 1040 L580 1060 L570 1300Z" fill="{HOOD}" stroke="{OL}" stroke-width="10"/>'
    elif pose == "manos":       # manos a la cabeza
        for sx in (1, -1): b += f'<g transform="translate(400,0) scale({sx},1)"><path d="M-300 900 Q-400 700 -330 470 L-250 500 Q-290 700 -210 860Z" fill="{HOOD}" stroke="{OL}" stroke-width="10"/><ellipse cx="-290" cy="440" rx="58" ry="62" fill="{SK}" stroke="{OL}" stroke-width="9"/></g>'
    elif pose == "senala":      # señala a la cámara
        b += f'<path d="M560 900 Q660 860 720 960 L650 1030 Q610 980 540 1010Z" fill="{HOOD}" stroke="{OL}" stroke-width="10"/><ellipse cx="700" cy="1010" rx="74" ry="70" fill="{SK}" stroke="{OL}" stroke-width="9"/><rect x="676" y="900" width="44" height="110" rx="22" fill="{SK}" stroke="{OL}" stroke-width="8"/>'
        b += f'<path d="M130 880 Q60 1000 80 1240 L170 1240 Q160 1020 200 900Z" fill="{HOOD}" stroke="{OL}" stroke-width="10"/>'
    return svg(800, 1300, b)

def cabeza_extra(quien):
    """Nico (9), Dani y Renata: cabezas sencillas del mismo estilo."""
    skin = {"nico": SK, "dani": "#e8b48c", "renata": "#c98d62"}[quien]; b = ""
    if quien == "renata":
        for cx, cy, r in ((150, 250, 110), (250, 140, 120), (400, 100, 130), (550, 140, 120), (650, 250, 110), (130, 400, 90), (670, 400, 90)): b += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#2a1a12" stroke="{OL}" stroke-width="9"/>'
    b += f'<rect x="352" y="640" width="96" height="120" rx="30" fill="{skin}" stroke="{OL}" stroke-width="9"/>'
    col = {"nico": "#2bd4c4", "dani": "#ff5d73", "renata": "#b98ad6"}[quien]
    b += f'<path d="M110 1000 Q100 800 250 770 Q400 740 550 770 Q700 800 690 1000Z" fill="{col}" stroke="{OL}" stroke-width="10"/>'
    b += f'<path d="M150 420 Q150 180 400 180 Q650 180 650 420 Q650 600 520 690 Q400 740 280 690 Q150 600 150 420Z" fill="{skin}" stroke="{OL}" stroke-width="10"/>'
    b += f'<ellipse cx="146" cy="450" rx="32" ry="48" fill="{skin}" stroke="{OL}" stroke-width="9"/><ellipse cx="654" cy="450" rx="32" ry="48" fill="{skin}" stroke="{OL}" stroke-width="9"/>'
    if quien == "nico":
        b += f'<path d="M140 380 Q130 150 400 150 Q670 150 660 380 Q520 300 400 310 Q280 300 140 380Z" fill="#ff5d73" stroke="{OL}" stroke-width="10"/><path d="M130 370 Q0 380 20 440 Q160 420 300 330Z" fill="#e0445a" stroke="{OL}" stroke-width="10" stroke-linejoin="round"/>'
    elif quien == "dani":
        b += f'<path d="M146 400 Q120 130 400 140 Q690 130 654 400 Q620 280 520 250 Q400 300 260 260 Q180 300 146 400Z" fill="#5a3a22" stroke="{OL}" stroke-width="10" stroke-linejoin="round"/>'
    for cx in (300, 500):
        b += f'<ellipse cx="{cx}" cy="450" rx="56" ry="64" fill="#fff" stroke="{OL}" stroke-width="8"/><circle cx="{cx}" cy="{456}" r="30" fill="#3a2a1a"/><circle cx="{cx - 10}" cy="444" r="9" fill="#fff"/>'
    if quien == "renata": b += f'<rect x="226" y="380" width="148" height="140" rx="30" fill="none" stroke="{OL}" stroke-width="12"/><rect x="426" y="380" width="148" height="140" rx="30" fill="none" stroke="{OL}" stroke-width="12"/><path d="M374 440 L426 440" stroke="{OL}" stroke-width="12"/>'
    b += f'<path d="M240 360 Q300 330 350 362" stroke="{OL}" stroke-width="16" fill="none" stroke-linecap="round"/><path d="M450 362 Q500 330 560 360" stroke="{OL}" stroke-width="16" fill="none" stroke-linecap="round"/>'
    b += f'<path d="M388 548 Q402 570 420 550" stroke="{OL}" stroke-width="8" fill="none" stroke-linecap="round"/>'
    if quien == "nico": b += f'<path d="M320 610 Q400 700 480 610Z" fill="#7a1f3d" stroke="{OL}" stroke-width="9" stroke-linejoin="round"/><rect x="372" y="612" width="24" height="26" fill="#fff"/><rect x="410" y="612" width="24" height="26" fill="#fff"/>'
    else: b += f'<path d="M330 620 Q400 680 470 620" stroke="{OL}" stroke-width="12" fill="none" stroke-linecap="round"/>'
    return svg(800, 1000, b)

def celular(pantalla="#3a3760"):
    return svg(300, 520, f'<rect x="20" y="20" width="260" height="480" rx="40" fill="#22203a" stroke="{OL}" stroke-width="12"/><rect x="42" y="60" width="216" height="400" rx="14" fill="{pantalla}"/><rect x="110" y="34" width="80" height="14" rx="7" fill="#0c0a18"/>')
def tablet():
    b = f'<rect x="10" y="10" width="620" height="460" rx="36" fill="#22203a" stroke="{OL}" stroke-width="12"/><rect x="40" y="40" width="560" height="400" rx="10" fill="#e9f6ff"/>'
    b += f'<g transform="translate(180,70) rotate(6) scale(.66)">{nota()}</g><circle cx="560" cy="80" r="16" fill="#ff3b4e"/>'
    return svg(640, 480, b)
def candado(abierto=False):
    arc = "M88 150 Q88 60 150 60 Q212 60 212 150" if not abierto else "M88 120 Q88 30 150 30 Q212 30 212 120 L212 60"
    return svg(300, 330, f'<path d="{arc}" fill="none" stroke="{OL}" stroke-width="44"/><path d="{arc}" fill="none" stroke="#c9d3e6" stroke-width="26"/><rect x="50" y="140" width="200" height="170" rx="26" fill="#ffc93c" stroke="{OL}" stroke-width="12"/><circle cx="150" cy="210" r="24" fill="{OL}"/><rect x="138" y="214" width="24" height="60" rx="8" fill="{OL}"/>')
def mano_mama():
    b = f'<path d="M260 210 L900 150 L900 330 L260 300Z" fill="#7a4fb5" stroke="{OL}" stroke-width="12" stroke-linejoin="round"/><ellipse cx="200" cy="255" rx="120" ry="96" fill="#e8b48c" stroke="{OL}" stroke-width="11"/>'
    for i in range(4): b += f'<rect x="{60 + i * 6}" y="{176 + i * 42}" width="130" height="40" rx="20" fill="#e8b48c" stroke="{OL}" stroke-width="9"/>'
    b += f'<rect x="20" y="150" width="120" height="26" rx="10" fill="#c9d3e6" stroke="{OL}" stroke-width="7"/><circle cx="150" cy="163" r="30" fill="#c9d3e6" stroke="{OL}" stroke-width="7"/>'
    return svg(900, 480, b)
def mano_pluma():
    """Mano que escribe: la punta de la pluma queda en (60, 560) de un lienzo de 700x620."""
    b = f'<path d="M60 560 L330 250" stroke="{OL}" stroke-width="40" stroke-linecap="round"/><path d="M96 520 L330 250" stroke="#2bd4c4" stroke-width="26" stroke-linecap="round"/><path d="M60 560 L92 524" stroke="#22203a" stroke-width="16" stroke-linecap="round"/>'
    b += f'<path d="M360 330 L700 520 L700 620 L420 620Z" fill="{HOOD}" stroke="{OL}" stroke-width="11" stroke-linejoin="round"/><ellipse cx="300" cy="340" rx="110" ry="92" fill="{SK}" stroke="{OL}" stroke-width="11" transform="rotate(-30 300 340)"/>'
    for i in range(3): b += f'<rect x="{190 + i * 38}" y="{318 + i * 34}" width="120" height="40" rx="20" fill="{SK}" stroke="{OL}" stroke-width="9" transform="rotate(-38 {250 + i * 38} {338 + i * 34})"/>'
    return svg(700, 620, b)
def microondas():
    b = f'<rect x="10" y="20" width="700" height="430" rx="30" fill="#c9d3e6" stroke="{OL}" stroke-width="12"/><rect x="50" y="60" width="440" height="350" rx="18" fill="#16122a" stroke="{OL}" stroke-width="10"/>'
    b += f'<circle cx="200" cy="200" r="34" fill="#fff"/><circle cx="340" cy="200" r="34" fill="#fff"/><circle cx="208" cy="206" r="14" fill="{OL}"/><circle cx="348" cy="206" r="14" fill="{OL}"/><path d="M210 300 Q270 330 330 300" stroke="#fff" stroke-width="10" fill="none" stroke-linecap="round"/>'
    b += f'<rect x="530" y="70" width="150" height="70" rx="10" fill="#16122a"/><text x="605" y="122" text-anchor="middle" font-family="Anton" font-size="50" fill="#2bd4c4">0:00</text>'
    for i in range(6): b += f'<circle cx="{560 + (i % 2) * 90}" cy="{200 + (i // 2) * 76}" r="26" fill="#8894b0" stroke="{OL}" stroke-width="7"/>'
    return svg(720, 470, b)
def boleto():
    b = f'<path d="M10 10 L590 10 L590 100 Q560 130 590 160 L590 250 L10 250 L10 160 Q40 130 10 100Z" fill="#ff5d73" stroke="{OL}" stroke-width="11" stroke-linejoin="round"/><path d="M440 20 L440 240" stroke="{OL}" stroke-width="6" stroke-dasharray="14 12"/>'
    b += f'<text x="225" y="110" text-anchor="middle" font-family="Anton" font-size="70" fill="#fff6dc">CONCIERTO</text><text x="225" y="190" text-anchor="middle" font-family="Anton" font-size="52" fill="#16122a">DEL AÑO ★</text><text x="516" y="150" text-anchor="middle" font-family="Anton" font-size="60" fill="#fff6dc" transform="rotate(90 516 130)">VIP</text>'
    return svg(600, 260, b)
def cocodrilo():
    b = f'<path d="M40 300 Q20 220 120 200 L420 180 Q520 170 560 230 Q600 300 520 330 L120 350 Q50 350 40 300Z" fill="#5fc46a" stroke="{OL}" stroke-width="11"/><path d="M60 300 L500 290" stroke="{OL}" stroke-width="8"/>'
    for i in range(8): b += f'<path d="M{90 + i * 50} 300 l16 30 l16 -30Z" fill="#fff" stroke="{OL}" stroke-width="5"/>'
    b += f'<circle cx="420" cy="170" r="46" fill="#5fc46a" stroke="{OL}" stroke-width="10"/><circle cx="424" cy="166" r="24" fill="#fff"/><circle cx="430" cy="168" r="11" fill="{OL}"/>'
    b += f'<path d="M380 120 Q470 20 600 130 Q640 260 600 330 Q560 250 470 140Z" fill="#fff" fill-opacity=".85" stroke="{OL}" stroke-width="8"/><circle cx="110" cy="230" r="9" fill="{OL}"/><path d="M500 60 l14 -30 l14 30 l30 4 l-22 22 l6 30 l-28 -16 l-28 16 l6 -30 l-22 -22Z" fill="#ffc93c" stroke="{OL}" stroke-width="6"/>'
    return svg(660, 380, b)
def piedra():
    b = f'<path d="M40 80 Q120 10 300 30 Q520 20 560 120 Q600 300 520 400 Q300 460 100 410 Q10 300 40 80Z" fill="#9a8f84" stroke="{OL}" stroke-width="12"/>'
    b += f'<path d="M150 160 l40 90 l40 -90 M300 150 l0 110 M300 150 l60 0 M300 205 l44 0 M420 160 q-50 50 0 100 q50 -50 0 -100" stroke="#4a3f36" stroke-width="16" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M140 330 q60 -40 120 0 t120 0 t100 0" stroke="#4a3f36" stroke-width="14" fill="none" stroke-linecap="round"/>'
    return svg(620, 460, b)

def fondo(tipo):
    b = '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a1757"/><stop offset="1" stop-color="#140c2e"/></linearGradient></defs><rect width="1080" height="1920" fill="url(#g)"/>'
    b += '<rect y="1420" width="1080" height="500" fill="#1d1240"/><path d="M0 1420 L1080 1420" stroke="#3b2a7a" stroke-width="8"/>'
    if tipo == "cuarto":
        b += '<rect x="640" y="250" width="360" height="420" rx="18" fill="#101a3c" stroke="#2bd4c4" stroke-width="10"/><circle cx="900" cy="350" r="46" fill="#fff6dc"/><path d="M640 460 L1000 460 M820 250 L820 670" stroke="#2bd4c4" stroke-width="8"/>'
        b += '<path d="M60 300 Q300 380 560 300" stroke="#3b2a7a" stroke-width="6" fill="none"/>'
        for i, c in enumerate(("#ffc93c", "#2bd4c4", "#ff5d73", "#b98ad6", "#fff6dc", "#ffc93c")): b += f'<circle cx="{90 + i * 88}" cy="{318 + 32 * math.sin(i * .62 + .3):.0f}" r="18" fill="{c}"/><circle cx="{90 + i * 88}" cy="{318 + 32 * math.sin(i * .62 + .3):.0f}" r="40" fill="{c}" opacity=".18"/>'
        for x, y, r, c in ((120, 760, -6, "#ff5d73"), (330, 820, 5, "#2bd4c4"), (130, 1010, 4, "#ffc93c")): b += f'<rect x="{x}" y="{y}" width="170" height="210" rx="8" fill="{c}" opacity=".5" stroke="#3b2a7a" stroke-width="6" transform="rotate({r} {x + 85} {y + 105})"/>'
        b += '<rect x="0" y="1300" width="620" height="150" rx="30" fill="#3b2a7a"/><rect x="40" y="1230" width="230" height="110" rx="40" fill="#b98ad6"/>'
    else:   # cocina
        for i in range(4): b += f'<rect x="{40 + i * 255}" y="200" width="235" height="330" rx="14" fill="#241a52" stroke="#3b2a7a" stroke-width="8"/><circle cx="{240 + i * 255}" cy="370" r="12" fill="#2bd4c4"/>'
        b += '<rect x="0" y="1140" width="1080" height="290" fill="#241a52"/><rect x="-10" y="1100" width="1100" height="60" rx="12" fill="#3b2a7a" stroke="#4b3a9a" stroke-width="6"/>'
        for i in range(9): b += f'<rect x="{20 + i * 120}" y="620" width="104" height="104" rx="8" fill="#1d1648" stroke="#3b2a7a" stroke-width="5"/><rect x="{20 + i * 120}" y="740" width="104" height="104" rx="8" fill="#1d1648" stroke="#3b2a7a" stroke-width="5"/>'
        b += '<path d="M0 590 L1080 590" stroke="#ff5d73" stroke-width="10" opacity=".8"/><path d="M0 590 L1080 590" stroke="#ff5d73" stroke-width="40" opacity=".15"/>'
    return svg(1080, 1920, b)

L = {"bg_cuarto": fondo("cuarto"), "bg_cocina": fondo("cocina"), "celular": celular(), "tablet": tablet(), "candado": candado(), "candado_abierto": candado(True), "mano_mama": mano_mama(),
     "mano_pluma": mano_pluma(), "microondas": microondas(), "boleto": boleto(), "cocodrilo": cocodrilo(), "piedra": piedra(), "caja": svg(400, 430, caja()), "nota": svg(440, 360, f'<g transform="translate(10,22)">{nota()}</g>'),
     "nota_blanca": svg(440, 360, '<g transform="translate(10,22)">' + re.sub(r'<path d="M[^"]*" fill="none" stroke="#2a3b8f"[^>]*/>', "", nota()) + '</g>'),
     "nico": cabeza_extra("nico"), "dani": cabeza_extra("dani"), "renata": cabeza_extra("renata")}
for k in ("aburrida", "shock", "asco", "orgullosa", "enojada"):
    L[f"vale_{k}"] = vale(k); L[f"vale_{k}_hab"] = vale(k, True)
L["vale_orgullosa_nota"] = vale("orgullosa", pose="nota"); L["vale_orgullosa_nota_hab"] = vale("orgullosa", True, "nota"); L["vale_aburrida_nota"] = vale("aburrida", pose="nota")
L["vale_shock_manos"] = vale("shock", pose="manos"); L["vale_aburrida_senala"] = vale("orgullosa", pose="senala")
if __name__ == "__main__":
    with sync_playwright() as p:
        br = p.chromium.launch(channel="chrome")
        for name, s in L.items():
            w, h = map(int, re.search(r'width="(\d+)" height="(\d+)"', s).groups())
            pg = br.new_page(viewport={"width": w, "height": h}, device_scale_factor=2); hp = os.path.join(HERE, "_tmp.html")
            open(hp, "w").write(f"<html><head><style>{FONT_CSS} html,body{{margin:0;background:transparent;overflow:hidden}}</style></head><body>{s}</body></html>")
            pg.goto("file://" + hp); pg.wait_for_timeout(180); pg.screenshot(path=os.path.join(HERE, "layers", name + ".png"), omit_background=not name.startswith("bg_")); pg.close()
        br.close(); os.remove(os.path.join(HERE, "_tmp.html"))
    print("ok", len(L))
