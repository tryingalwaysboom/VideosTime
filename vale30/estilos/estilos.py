"""Tres propuestas de estilo para «30 días sin celular» (mismo fotograma: el gancho). Uso: python3 estilos/estilos.py"""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "mateo30"))
import art30 as B
from playwright.sync_api import sync_playwright
FONT_CSS = B.A.FONT_CSS

def chica(p):
    """Vale gritando con las manos en la cabeza. p: dict de estilo."""
    OL, sw, SK, SKS, HAIR, HL, HOOD, HOODS = p["ol"], p["sw"], p["sk"], p["sks"], p["hair"], p["hl"], p["hood"], p["hoods"]
    cx, hy, rx, ry = 540, p["hy"], p["rx"], p["ry"]; er = p["eye"]; st = f'stroke="{OL}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"'
    sh = p["hombros"]; ty = hy + ry + p["cuello"]; b = ""
    # pelo de atrás + moño
    b += f'<circle cx="{cx + rx * .15}" cy="{hy - ry - rx * .28}" r="{rx * .42}" fill="{HAIR}" {st}/>'
    if p.get("melena"): b += f'<path d="M{cx - rx * 1.08} {hy - ry * .2} Q{cx - rx * 1.35} {hy + ry * 1.4} {cx - rx * .9} {ty + 190} L{cx + rx * .9} {ty + 190} Q{cx + rx * 1.35} {hy + ry * 1.4} {cx + rx * 1.08} {hy - ry * .2}Z" fill="{HAIR}" {st}/>'
    # torso
    b += f'<path d="M{cx - sh} 1960 Q{cx - sh - 20} {ty + 60} {cx - sh * .55} {ty} Q{cx} {ty - 50} {cx + sh * .55} {ty} Q{cx + sh + 20} {ty + 60} {cx + sh} 1960Z" fill="{HOOD}" {st}/>'
    b += f'<path d="M{cx - sh * .42} {ty + 6} Q{cx} {ty + 150} {cx + sh * .42} {ty + 6} Q{cx} {ty - 36} {cx - sh * .42} {ty + 6}Z" fill="{HOODS}" {st}/>'
    b += f'<path d="M{cx - 44} {ty + 96} l-10 150 M{cx + 44} {ty + 96} l12 160" stroke="#fff6dc" stroke-width="{max(8, sw)}" stroke-linecap="round" fill="none"/>'
    if p.get("sombra"):
        b += f'<path d="M{cx + sh * .1} {ty + 30} Q{cx + sh + 10} {ty + 80} {cx + sh} 1960 L{cx + sh * .35} 1960 Q{cx + sh * .5} {ty + 400} {cx + sh * .1} {ty + 30}Z" fill="#000" opacity=".16"/>'
        b += f'<path d="M{cx - sh * .8} {ty + 300} q40 60 20 160 M{cx + sh * .7} {ty + 280} q-50 80 -20 200" stroke="{HOODS}" stroke-width="10" fill="none" stroke-linecap="round"/>'
    # cuello
    b += f'<rect x="{cx - p["cw"]}" y="{hy + ry - 40}" width="{2 * p["cw"]}" height="{p["cuello"] + 70}" rx="{p["cw"] * .6}" fill="{SKS}" {st}/>'
    # brazos levantados (trazo grueso: hombro → codo → mano)
    aw = p.get("brazo", 120)
    for s in (-1, 1):
        d = f'M{cx + s * sh * .78} {ty + 110} Q{cx + s * (sh + 150)} {hy + ry * 1.0} {cx + s * (rx + 50)} {hy - ry * .1}'
        b += f'<path d="{d}" stroke="{OL}" stroke-width="{aw + 2 * sw}" fill="none" stroke-linecap="round"/><path d="{d}" stroke="{HOOD}" stroke-width="{aw}" fill="none" stroke-linecap="round"/>'
    # cabeza
    b += f'<ellipse cx="{cx}" cy="{hy}" rx="{rx}" ry="{ry}" fill="{SK}" {st}/>'
    if p.get("sombra"): b += f'<path d="M{cx + rx * .25} {hy - ry} Q{cx + rx * 1.02} {hy - ry * .5} {cx + rx} {hy} Q{cx + rx * .9} {hy + ry * .8} {cx + rx * .1} {hy + ry} Q{cx + rx * .75} {hy + ry * .4} {cx + rx * .62} {hy - ry * .1} Q{cx + rx * .55} {hy - ry * .7} {cx + rx * .25} {hy - ry}Z" fill="{SKS}" opacity=".75"/>'
    for s in (-1, 1): b += f'<ellipse cx="{cx + s * rx}" cy="{hy + ry * .12}" rx="{rx * .14}" ry="{ry * .2}" fill="{SK}" {st}/>'
    # flequillo
    b += f'<path d="M{cx - rx * 1.03} {hy - ry * .05} Q{cx - rx * 1.15} {hy - ry * 1.2} {cx} {hy - ry * 1.14} Q{cx + rx * 1.15} {hy - ry * 1.2} {cx + rx * 1.03} {hy - ry * .05} Q{cx + rx * .9} {hy - ry * .55} {cx + rx * .5} {hy - ry * .62} Q{cx + rx * .55} {hy - ry * .3} {cx + rx * .2} {hy - ry * .42} Q{cx - rx * .1} {hy - ry * .66} {cx - rx * .55} {hy - ry * .36} Q{cx - rx * .8} {hy - ry * .45} {cx - rx * 1.03} {hy - ry * .05}Z" fill="{HAIR}" {st}/>'
    b += f'<path d="M{cx + rx * .32} {hy - ry * 1.02} Q{cx + rx * .8} {hy - ry * .9} {cx + rx * .9} {hy - ry * .42}" stroke="{HL}" stroke-width="{rx * .1}" fill="none" stroke-linecap="round"/>'
    # ojos
    ey = hy + ry * .05; ed = rx * p["ed"]
    for s in (-1, 1):
        x = cx + s * ed
        b += f'<ellipse cx="{x}" cy="{ey}" rx="{er}" ry="{er * 1.14}" fill="#fff" {st}/><circle cx="{x}" cy="{ey + 2}" r="{er * .5}" fill="{p["iris"]}"/><circle cx="{x}" cy="{ey + 2}" r="{er * .24}" fill="{OL}"/><circle cx="{x - er * .2}" cy="{ey - er * .22}" r="{er * .14}" fill="#fff"/>'
        b += f'<path d="M{x - er * 1.1} {ey - er * 1.75} Q{x} {ey - er * 2.25} {x + er * 1.1} {ey - er * 1.75}" stroke="{OL}" stroke-width="{max(sw, er * .22)}" fill="none" stroke-linecap="round"/>'
        if p.get("pestanas"): b += f'<path d="M{x + s * er * .9} {ey - er * .7} l{s * 16} -14 M{x + s * er * 1.02} {ey - er * .3} l{s * 18} -6" stroke="{OL}" stroke-width="5" stroke-linecap="round"/>'
        b += f'<path d="M{x - er * .8} {ey + er * 1.5} Q{x} {ey + er * 1.75} {x + er * .8} {ey + er * 1.5}" stroke="#b98ad6" stroke-width="6" fill="none" stroke-linecap="round" opacity=".7"/>'
    for i in range(6): s = -1 if i < 3 else 1; j = i % 3; b += f'<circle cx="{cx + s * (ed + er * .2 + (j - 1) * 20)}" cy="{ey + er * 2.1 + (j % 2) * 16}" r="5.5" fill="#d98f66"/>'
    b += f'<path d="M{cx - 12} {hy + ry * .36} q14 16 28 0" stroke="{OL}" stroke-width="{max(5, sw * .7)}" fill="none" stroke-linecap="round"/>'
    my = hy + ry * .66; mr = rx * p["boca"]
    b += f'<ellipse cx="{cx}" cy="{my}" rx="{mr}" ry="{mr * 1.05}" fill="#7a1f3d" {st}/><path d="M{cx - mr * .6} {my + mr * .55} Q{cx} {my + mr * 1.05} {cx + mr * .6} {my + mr * .55} Q{cx} {my + mr * .2} {cx - mr * .6} {my + mr * .55}Z" fill="#ff7b8a"/><rect x="{cx - mr * .5}" y="{my - mr * .92}" width="{mr}" height="{mr * .32}" rx="5" fill="#fff"/>'
    for s in (-1, 1):
        hx, hyy = cx + s * (rx + 20), hy - ry * .28
        b += f'<ellipse cx="{hx}" cy="{hyy}" rx="{p["mano"]}" ry="{p["mano"] * 1.08}" fill="{SK}" {st}/>'
        for k in range(3): b += f'<path d="M{hx - s * (p["mano"] * .9)} {hyy - p["mano"] * .45 + k * p["mano"] * .45} l{-s * p["mano"] * .5} 6" stroke="{OL}" stroke-width="{max(4, sw * .6)}" stroke-linecap="round"/>'
    return b

def caja(x, y, s, OL="#1b1330", sw=10):
    return (f'<g transform="translate({x},{y}) scale({s})"><rect x="20" y="90" width="360" height="330" rx="26" fill="#bfe9f5" fill-opacity=".55" stroke="{OL}" stroke-width="{sw}"/>'
            f'<rect x="150" y="150" width="120" height="220" rx="18" fill="#22203a" stroke="{OL}" stroke-width="8" transform="rotate(8 210 260)"/><rect x="0" y="60" width="400" height="64" rx="18" fill="#ff5d73" stroke="{OL}" stroke-width="{sw}"/>'
            f'<rect x="96" y="0" width="208" height="92" rx="14" fill="#16122a" stroke="{OL}" stroke-width="8"/><text x="200" y="66" text-anchor="middle" font-family="Anton" font-size="60" fill="#ff3b4e" letter-spacing="3">30 DÍAS</text>'
            f'<path d="M168 300 Q168 250 200 250 Q232 250 232 300" fill="none" stroke="{OL}" stroke-width="16"/><rect x="150" y="296" width="100" height="84" rx="14" fill="#ffc93c" stroke="{OL}" stroke-width="9"/><circle cx="200" cy="332" r="12" fill="{OL}"/></g>')

def cap(txt, y=1372, col="#fff", ol="#0e0a1a", f="Anton", size=108):
    return f'<text x="540" y="{y + 38}" text-anchor="middle" font-family="{f}" font-size="{size}" fill="{col}" stroke="{ol}" stroke-width="22" paint-order="stroke" stroke-linejoin="round">{txt}</text>'

# ------------------------------------------------------------ 1 · CUADERNO
def cuaderno():
    r = random.Random(5); b = '<defs><filter id="w" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".018" numOctaves="2" seed="4"/><feDisplacementMap in="SourceGraphic" scale="9"/></filter>'
    b += '<filter id="pap"><feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" seed="2"/><feColorMatrix values="0 0 0 0 .5  0 0 0 0 .45  0 0 0 0 .3  0 0 0 .07 0"/></filter></defs>'
    b += '<rect width="1080" height="1920" fill="#fbf5e3"/><rect width="1080" height="1920" filter="url(#pap)"/>'
    for y in range(150, 1920, 66): b += f'<path d="M0 {y} L1080 {y}" stroke="#a9cdee" stroke-width="3"/>'
    b += '<path d="M150 0 L150 1920" stroke="#ef8f8f" stroke-width="4"/>'
    for y in range(120, 1920, 150): b += f'<circle cx="62" cy="{y}" r="24" fill="#2a2440"/><circle cx="62" cy="{y}" r="24" fill="none" stroke="#c9c2ad" stroke-width="5"/>'
    g = '<g filter="url(#w)">'
    # rotulador: manchas de color desplazadas detrás del personaje
    g += '<ellipse cx="560" cy="1010" rx="330" ry="330" fill="#ffe14d" opacity=".55"/>'
    for i in range(16): a = i * math.pi / 8; g += f'<path d="M{560 + 380 * math.cos(a):.0f} {1000 + 380 * math.sin(a):.0f} L{560 + (450 + 30 * (i % 2)) * math.cos(a):.0f} {1000 + (450 + 30 * (i % 2)) * math.sin(a):.0f}" stroke="#1b1330" stroke-width="9" stroke-linecap="round"/>'
    g += chica(dict(ol="#1b1330", sw=9, sk="#fbd9bd", sks="#f1c4a3", hair="#5b3fa8", hl="#2bd4c4", hood="#ffd23f", hoods="#f2b61c", hy=980, rx=215, ry=205, eye=62, ed=.45, iris="#2bb7a9", boca=.25, hombros=300, cuello=10, cw=46, mano=58))
    # título a rotulador con subrayador
    g += '<rect x="170" y="318" width="800" height="150" fill="#ff8fa3" opacity=".75" transform="rotate(-3 540 390)"/><text x="570" y="440" text-anchor="middle" font-family="Caveat" font-weight="700" font-size="230" fill="#1b1330" transform="rotate(-3 540 390)">30 días</text>'
    g += '<rect x="230" y="505" width="700" height="96" fill="#7fe3d8" opacity=".8" transform="rotate(-2 540 560)"/><text x="580" y="592" text-anchor="middle" font-family="Caveat" font-weight="700" font-size="140" fill="#1b1330" transform="rotate(-2 540 560)">sin celular</text>'
    # garabatos: celular tachado, candado, flechas, estrellas
    g += '<g transform="translate(905,1500) rotate(10)" fill="none" stroke="#1b1330" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"><rect x="0" y="0" width="110" height="190" rx="18" fill="#fff"/><path d="M38 20 L72 20"/><path d="M-30 -20 L140 210 M140 -20 L-30 210" stroke="#ff3b4e" stroke-width="13"/></g>'
    g += '<g transform="translate(70,1520)" fill="none" stroke="#1b1330" stroke-width="8" stroke-linecap="round"><path d="M20 60 Q20 0 60 0 Q100 0 100 60"/><rect x="0" y="56" width="120" height="96" rx="14" fill="#ffd23f"/><circle cx="60" cy="100" r="10" fill="#1b1330"/></g>'
    for x, y, s in ((230, 640, 30), (930, 620, 24), (900, 1240, 28), (210, 1260, 22)): g += f'<path d="M{x} {y - s} L{x + s * .3} {y - s * .3} L{x + s} {y} L{x + s * .3} {y + s * .3} L{x} {y + s} L{x - s * .3} {y + s * .3} L{x - s} {y} L{x - s * .3} {y - s * .3}Z" fill="#ffd23f" stroke="#1b1330" stroke-width="6"/>'
    g += '<text x="250" y="262" font-family="Caveat" font-weight="700" font-size="74" fill="#2a3b8f" transform="rotate(-4 250 250)">día 1 de 30</text><path d="M240 280 q120 22 300 -2" stroke="#ff3b4e" stroke-width="8" fill="none" stroke-linecap="round"/>'
    g += '</g>'
    return b + g + cap("¿¡TREINTA!?", col="#fff", ol="#1b1330", f="Caveat", size=150)

# ------------------------------------------------------------ 2 · CÓMIC MÁS ADULTO
def comic():
    b = '''<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#101638"/><stop offset=".6" stop-color="#231548"/><stop offset="1" stop-color="#0c0a20"/></linearGradient>
    <radialGradient id="lamp" cx=".2" cy=".52" r=".6"><stop offset="0" stop-color="#ffb65c" stop-opacity=".55"/><stop offset="1" stop-color="#ffb65c" stop-opacity="0"/></radialGradient>
    <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".6"/></radialGradient>
    <pattern id="ht" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(30)"><circle cx="7" cy="7" r="2.6" fill="#fff" opacity=".1"/></pattern></defs>
    <rect width="1080" height="1920" fill="url(#g)"/>'''
    # ventana con ciudad
    b += '<rect x="560" y="300" width="430" height="520" rx="10" fill="#0a1030" stroke="#3a3470" stroke-width="12"/>'
    r = random.Random(9)
    for i in range(9):
        x = 575 + i * 46; h = r.randint(120, 330); b += f'<rect x="{x}" y="{805 - h}" width="40" height="{h}" fill="#141a44"/>'
        for k in range(0, h - 30, 34):
            if r.random() < .55: b += f'<rect x="{x + 8}" y="{780 - k}" width="10" height="14" fill="#ffd27a"/>'
            if r.random() < .4: b += f'<rect x="{x + 24}" y="{780 - k}" width="10" height="14" fill="#7fe3d8"/>'
    b += '<circle cx="900" cy="390" r="44" fill="#fff6dc"/><path d="M560 560 L990 560 M775 300 L775 820" stroke="#3a3470" stroke-width="10"/>'
    # estantes, pósters, luces
    b += '<rect x="70" y="420" width="400" height="20" fill="#3a2a66"/>'
    for i, c in enumerate(("#ff5d73", "#2bd4c4", "#ffc93c", "#b98ad6", "#ff5d73", "#fff6dc")): b += f'<rect x="{90 + i * 44}" y="{300 + (i % 3) * 14}" width="36" height="{120 - (i % 3) * 14}" fill="{c}" opacity=".85"/>'
    b += '<rect x="90" y="520" width="170" height="230" fill="#2bd4c4" opacity=".35" transform="rotate(-4 175 635)"/><rect x="290" y="540" width="160" height="210" fill="#ff5d73" opacity=".35" transform="rotate(3 370 645)"/>'
    b += '<path d="M40 250 Q300 330 540 250" stroke="#4b3a9a" stroke-width="5" fill="none"/>'
    for i in range(7): x = 70 + i * 72; y = 262 + 34 * math.sin(i * .5 + .3); c = ("#ffc93c", "#2bd4c4", "#ff5d73", "#b98ad6")[i % 4]; b += f'<circle cx="{x}" cy="{y:.0f}" r="46" fill="{c}" opacity=".16"/><circle cx="{x}" cy="{y:.0f}" r="14" fill="{c}"/>'
    # escritorio con la caja iluminada
    b += '<rect x="0" y="1500" width="1080" height="420" fill="#1a1238"/><rect x="0" y="1480" width="1080" height="40" fill="#3a2a66"/>'
    b += '<rect width="1080" height="1920" fill="url(#lamp)"/>'
    g = chica(dict(ol="#160f2c", sw=6, sk="#f3c9a8", sks="#d9a383", hair="#3d2a7a", hl="#2bd4c4", hood="#f5bf2e", hoods="#d79c14", hy=900, rx=165, ry=190, brazo=96, eye=40, ed=.42, iris="#22b8aa", boca=.24, hombros=250, cuello=46, cw=44, mano=50, melena=True, sombra=True, pestanas=True))
    b += g
    b += '<path d="M392 820 Q380 640 540 630" stroke="#2bd4c4" stroke-width="9" fill="none" opacity=".8" stroke-linecap="round"/>'      # luz de contra turquesa
    b += caja(720, 1175, .78, "#160f2c", 7) + '<ellipse cx="846" cy="1500" rx="190" ry="26" fill="#ff3b4e" opacity=".3"/>'
    b += '<rect width="1080" height="1920" fill="url(#ht)"/><rect width="1080" height="1920" fill="url(#vig)"/>'
    b += '<text x="540" y="1150" text-anchor="middle" font-family="Anton" font-size="0"></text>'
    b += '<g transform="rotate(-3 540 380)"><text x="540" y="400" text-anchor="middle" font-family="Anton" font-size="190" fill="#ff3b4e" stroke="#fff" stroke-width="16" paint-order="stroke" stroke-linejoin="round">30 DÍAS</text><text x="540" y="520" text-anchor="middle" font-family="Anton" font-size="104" fill="#fff" stroke="#160f2c" stroke-width="16" paint-order="stroke" stroke-linejoin="round">SIN CELULAR</text></g>'
    return b + cap("¿¡TREINTA!?", y=1372, col="#2bd4c4")

# ------------------------------------------------------------ 3 · MUNDO MATEO (pizarra)
def pizarra():
    b = '''<defs><radialGradient id="pz" cx=".5" cy=".45" r=".8"><stop offset="0" stop-color="#2c624f"/><stop offset="1" stop-color="#173b30"/></radialGradient>
    <filter id="tz" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="3" result="n"/><feColorMatrix in="n" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 -.9 1.35" result="m"/><feComposite in="SourceGraphic" in2="m" operator="in"/></filter></defs>
    <rect width="1080" height="1920" fill="url(#pz)"/>'''
    r = random.Random(3)
    for _ in range(14): x, y = r.uniform(0, 1080), r.uniform(0, 1920); b += f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{r.uniform(200, 480):.0f}" ry="{r.uniform(40, 100):.0f}" fill="#fff" opacity=".03"/>'
    b += '<rect x="0" y="1560" width="1080" height="60" fill="#b07a48" stroke="#1d1630" stroke-width="8"/><rect x="120" y="1530" width="120" height="34" rx="8" fill="#f6f4e8" stroke="#1d1630" stroke-width="6"/><rect x="280" y="1536" width="90" height="28" rx="8" fill="#ffd454" stroke="#1d1630" stroke-width="6"/>'
    # barra superior como la de Mateo
    b += '<rect x="170" y="176" width="740" height="84" rx="20" fill="#fffdf4" stroke="#1d1630" stroke-width="8"/><text x="200" y="236" font-family="Anton" font-size="50" fill="#1d1630">FALTAN</text><text x="352" y="238" font-family="Anton" font-size="58" fill="#e2483b">30 DÍAS</text>'
    for i, ch in enumerate("NOTAS"): b += f'<rect x="{600 + i * 58}" y="190" width="50" height="56" rx="8" fill="#d8d3c2" stroke="#1d1630" stroke-width="5"/><text x="{625 + i * 58}" y="234" text-anchor="middle" font-family="Anton" font-size="38" fill="#9a9584">{ch}</text>'
    b += '<g filter="url(#tz)"><text x="540" y="500" text-anchor="middle" font-family="Caveat" font-weight="700" font-size="250" fill="#ffd454" transform="rotate(-3 540 440)">30 días</text><text x="540" y="650" text-anchor="middle" font-family="Caveat" font-weight="700" font-size="150" fill="#f6f4e8" transform="rotate(-2 540 620)">sin celular</text>'
    b += '<path d="M250 690 q280 30 600 -6" stroke="#e2483b" stroke-width="14" fill="none" stroke-linecap="round"/><path d="M120 760 l40 40 M160 760 l-40 40 M930 780 l40 40 M970 780 l-40 40" stroke="#f6f4e8" stroke-width="10" stroke-linecap="round"/></g>'
    b += chica(dict(ol="#1d1630", sw=11, sk="#f7cfa8", sks="#e6b088", hair="#4a2f8c", hl="#3fd0c0", hood="#ffd454", hoods="#e8b52c", hy=1090, rx=225, ry=212, eye=66, ed=.44, iris="#3f7fd0", boca=.25, hombros=310, cuello=6, cw=50, mano=60))
    # cartulina pegada con cinta
    b += '<g transform="rotate(6 850 900)"><rect x="740" y="820" width="230" height="130" rx="8" fill="#fffdf4" stroke="#1d1630" stroke-width="7"/><rect x="805" y="800" width="100" height="36" fill="#ffe27a" opacity=".9" stroke="#1d1630" stroke-width="3"/><text x="855" y="918" text-anchor="middle" font-family="Anton" font-size="76" fill="#1d1630">DÍA 1</text></g>'
    return b + cap("¿¡TREINTA!?", col="#ffd454", ol="#0c1016")

EST = {"estilo_1_cuaderno": cuaderno, "estilo_2_comic": comic, "estilo_3_pizarra": pizarra}
if __name__ == "__main__":
    with sync_playwright() as p:
        br = p.chromium.launch(channel="chrome")
        for name, fn in EST.items():
            pg = br.new_page(viewport={"width": 1080, "height": 1920}); hp = os.path.join(HERE, "_t.html")
            open(hp, "w").write(f'<html><head><style>{FONT_CSS} html,body{{margin:0;overflow:hidden}}</style></head><body><svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">{fn()}</svg></body></html>')
            pg.goto("file://" + hp); pg.wait_for_timeout(400); pg.screenshot(path=os.path.join(HERE, name + ".jpg"), type="jpeg", quality=90); pg.close()
        br.close(); os.remove(os.path.join(HERE, "_t.html"))
    print("ok")
