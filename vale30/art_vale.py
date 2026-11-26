"""Serie «30 días sin celular» · diseño de Vale, la caja y una maqueta del Día 1 (todo por código, sin gastar créditos).
Uso: python3 art_vale.py"""
import os, sys, random, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "mateo30"))
import art30 as B
from playwright.sync_api import sync_playwright
FONT_CSS = B.A.FONT_CSS
OL = "#1b1330"; SK = "#f4c7a1"; SKS = "#e0a47c"; HAIR = "#3d2a66"; HAIR2 = "#2bd4c4"; HOOD = "#ffc93c"; HOODS = "#e0a51f"; PAPER = "#fff6dc"
def svg(w, h, body): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>'

def nota(w=420, h=330, texto="garabato", seed=3):
    """Hoja de cuaderno arrancada, con cinta y letra que no se entiende."""
    r = random.Random(seed); top = " ".join(f"L{x} {r.uniform(0, 14):.0f}" for x in range(20, w, 26))
    b = f'<path d="M0 8 {top} L{w} 6 L{w} {h} L0 {h}Z" fill="{PAPER}" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>'
    for y in range(70, h - 20, 52): b += f'<path d="M10 {y} L{w - 10} {y}" stroke="#9cc7ee" stroke-width="4"/>'
    b += f'<path d="M58 14 L58 {h - 6}" stroke="#f08a8a" stroke-width="4"/>'
    for i, y in enumerate(range(96, h - 30, 52)):          # letra de doctor: garabatos
        x = 80; pts = [(x, y)]
        while x < w - 60 - (90 if i == 2 else 0):
            x += r.uniform(10, 24); pts.append((x, y + r.uniform(-30, 14)))
            if r.random() < .22: x += 20; pts.append((x, y))
        b += '<path d="M' + " L".join(f"{px:.0f} {py:.0f}" for px, py in pts) + f'" fill="none" stroke="#2a3b8f" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>'
    b += f'<rect x="{w / 2 - 70}" y="-16" width="140" height="44" fill="#ffe27a" fill-opacity=".85" stroke="{OL}" stroke-width="4" transform="rotate(-4 {w / 2} 6)"/>'
    return b

def ojo(cx, cy, mirada=(0, 10), parpado=.42):
    b = f'<ellipse cx="{cx}" cy="{cy}" rx="74" ry="86" fill="#fff" stroke="{OL}" stroke-width="8"/>'
    b += f'<circle cx="{cx + mirada[0]}" cy="{cy + mirada[1]}" r="44" fill="#22b8aa"/><circle cx="{cx + mirada[0]}" cy="{cy + mirada[1]}" r="22" fill="{OL}"/><circle cx="{cx + mirada[0] - 14}" cy="{cy + mirada[1] - 16}" r="11" fill="#fff"/>'
    yp = cy - 86 + 172 * parpado     # párpado caído: cara de "qué flojera"
    b += f'<clipPath id="c{cx}"><ellipse cx="{cx}" cy="{cy}" rx="74" ry="86"/></clipPath><rect x="{cx - 80}" y="{cy - 90}" width="160" height="{yp - cy + 90}" fill="{SKS}" clip-path="url(#c{cx})"/>'
    b += f'<path d="M{cx - 74} {yp} Q{cx} {yp + 16} {cx + 74} {yp}" stroke="{OL}" stroke-width="10" fill="none" stroke-linecap="round"/>'
    b += f'<path d="M{cx - 60} {cy + 104} Q{cx} {cy + 124} {cx + 60} {cy + 104}" stroke="#b98ad6" stroke-width="9" fill="none" stroke-linecap="round" opacity=".8"/>'   # ojeras
    return b

def vale(boca="mueca", con_nota=True):
    b = ""
    # moño despeinado, detrás
    b += f'<circle cx="430" cy="118" r="120" fill="{HAIR}" stroke="{OL}" stroke-width="9"/><path d="M360 60 Q420 10 500 70" stroke="{HAIR2}" stroke-width="20" fill="none" stroke-linecap="round"/>'
    for a in (-60, -20, 25, 70): b += f'<path d="M430 118 l{150 * math.sin(math.radians(a)):.0f} {-150 * math.cos(math.radians(a)):.0f}" stroke="{HAIR}" stroke-width="16" stroke-linecap="round"/>'
    # sudadera enorme
    b += f'<path d="M70 1150 Q60 840 210 770 Q400 720 590 770 Q740 840 730 1150Z" fill="{HOOD}" stroke="{OL}" stroke-width="10"/>'
    b += f'<path d="M250 770 Q400 900 550 770 Q470 730 400 734 Q330 730 250 770Z" fill="{HOODS}" stroke="{OL}" stroke-width="9"/>'
    b += f'<path d="M350 840 L340 980" stroke="#fff6dc" stroke-width="12" stroke-linecap="round"/><path d="M450 840 L462 990" stroke="#fff6dc" stroke-width="12" stroke-linecap="round"/>'
    # cuello y cabeza
    b += f'<rect x="352" y="640" width="96" height="130" rx="30" fill="{SKS}" stroke="{OL}" stroke-width="9"/>'
    b += f'<path d="M140 420 Q140 170 400 170 Q660 170 660 420 Q660 600 520 690 Q400 750 280 690 Q140 600 140 420Z" fill="{SK}" stroke="{OL}" stroke-width="10"/>'
    b += f'<ellipse cx="136" cy="450" rx="34" ry="50" fill="{SK}" stroke="{OL}" stroke-width="9"/><ellipse cx="664" cy="450" rx="34" ry="50" fill="{SK}" stroke="{OL}" stroke-width="9"/><circle cx="672" cy="520" r="24" fill="none" stroke="{HAIR2}" stroke-width="9"/>'
    # flequillo
    b += f'<path d="M134 430 Q110 150 400 150 Q690 150 666 430 Q640 300 540 250 Q560 330 470 300 Q420 250 300 330 Q220 300 190 360 Q150 380 134 430Z" fill="{HAIR}" stroke="{OL}" stroke-width="10" stroke-linejoin="round"/>'
    b += f'<path d="M480 190 Q560 220 590 300" stroke="{HAIR2}" stroke-width="22" fill="none" stroke-linecap="round"/>'
    b += ojo(292, 452) + ojo(508, 452)
    b += f'<path d="M210 336 Q290 300 362 344" stroke="{OL}" stroke-width="20" fill="none" stroke-linecap="round"/><path d="M440 318 Q520 270 596 318" stroke="{OL}" stroke-width="20" fill="none" stroke-linecap="round"/>'
    b += f'<path d="M388 560 Q402 584 420 562" stroke="{OL}" stroke-width="8" fill="none" stroke-linecap="round"/>'
    for x, y in ((230, 590), (262, 606), (246, 626), (540, 606), (572, 590), (556, 626)): b += f'<circle cx="{x}" cy="{y}" r="7" fill="#d98f66"/>'
    if boca == "mueca": b += f'<path d="M338 652 Q400 622 470 664" stroke="{OL}" stroke-width="12" fill="none" stroke-linecap="round"/>'
    elif boca == "grito": b += f'<ellipse cx="402" cy="654" rx="56" ry="44" fill="#7a1f3d" stroke="{OL}" stroke-width="9"/><path d="M366 680 Q402 700 438 680" fill="#ff7b8a"/>'
    if con_nota:
        b += f'<g transform="translate(190,830) rotate(-5)">{nota()}</g>'
        for hx in (170, 640):      # manos con dedos sujetando la nota
            b += f'<g transform="translate({hx},1010)"><ellipse cx="0" cy="0" rx="62" ry="54" fill="{SK}" stroke="{OL}" stroke-width="9"/>'
            for i in range(4): b += f'<rect x="{-50 + i * 26}" y="-74" width="24" height="60" rx="12" fill="{SK}" stroke="{OL}" stroke-width="7"/>'
            b += '</g>'
        b += f'<path d="M70 1150 Q70 1040 150 1040 L230 1060 L230 1150Z" fill="{HOOD}" stroke="{OL}" stroke-width="10"/><path d="M730 1150 Q730 1040 660 1040 L580 1060 L580 1150Z" fill="{HOOD}" stroke="{OL}" stroke-width="10"/>'
    return b

def caja(dias=30):
    b = f'<rect x="20" y="90" width="360" height="330" rx="26" fill="#bfe9f5" fill-opacity=".55" stroke="{OL}" stroke-width="10"/>'
    b += f'<rect x="150" y="150" width="120" height="220" rx="18" fill="#22203a" stroke="{OL}" stroke-width="8" transform="rotate(8 210 260)"/><rect x="164" y="170" width="92" height="170" rx="8" fill="#3a3760" transform="rotate(8 210 260)"/>'
    b += f'<rect x="0" y="60" width="400" height="64" rx="18" fill="#ff5d73" stroke="{OL}" stroke-width="10"/>'
    b += f'<rect x="96" y="0" width="208" height="92" rx="14" fill="#16122a" stroke="{OL}" stroke-width="8"/><text x="200" y="66" text-anchor="middle" font-family="Anton" font-size="60" fill="#ff3b4e" letter-spacing="3">{dias} DÍAS</text>'
    b += f'<path d="M168 300 Q168 250 200 250 Q232 250 232 300" fill="none" stroke="{OL}" stroke-width="16"/><rect x="150" y="296" width="100" height="84" rx="14" fill="#ffc93c" stroke="{OL}" stroke-width="9"/><circle cx="200" cy="332" r="12" fill="{OL}"/>'
    b += '<path d="M44 130 Q36 250 48 390" stroke="#fff" stroke-width="14" fill="none" stroke-linecap="round" opacity=".7"/>'
    return b

def maqueta():
    b = '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a1757"/><stop offset="1" stop-color="#140c2e"/></linearGradient></defs><rect width="1080" height="1920" fill="url(#g)"/>'
    b += f'<rect x="-40" y="1500" width="1160" height="460" fill="#1d1240"/><path d="M0 1500 L1080 1500" stroke="#3b2a7a" stroke-width="8"/>'
    b += '<rect x="640" y="250" width="360" height="420" rx="18" fill="#101a3c" stroke="#2bd4c4" stroke-width="10"/><circle cx="900" cy="350" r="46" fill="#fff6dc"/><path d="M640 460 L1000 460 M820 250 L820 670" stroke="#2bd4c4" stroke-width="8"/>'
    b += f'<g transform="translate(20,420) scale(.84)">{vale()}</g>'
    b += f'<g transform="translate(716,930) scale(.8)">{caja()}</g>'
    # marcador (zona segura, arriba)
    b += f'<rect x="40" y="130" width="760" height="110" rx="55" fill="#16122a" stroke="#2bd4c4" stroke-width="6"/><circle cx="100" cy="185" r="46" fill="#ff5d73"/><text x="100" y="204" text-anchor="middle" font-family="Anton" font-size="52" fill="#fff">1</text>'
    b += '<text x="170" y="172" font-family="Baloo 2" font-weight="800" font-size="30" fill="#bfe9f5">DÍA 1 DE 30 · SIN CELULAR</text><text x="170" y="216" font-family="Anton" font-size="38" fill="#ffc93c" letter-spacing="1">NOTAS: 0   ·   LETRA: 1/10</text>'
    # rótulo estilo nota + subtítulo
    b += f'<g transform="translate(50,290) rotate(-3)"><rect width="540" height="104" rx="10" fill="{PAPER}" stroke="{OL}" stroke-width="8"/><text x="270" y="76" text-anchor="middle" font-family="Anton" font-size="62" fill="{OL}">30 DÍAS SIN CELULAR</text></g>'
    b += f'<text x="490" y="1450" text-anchor="middle" font-family="Anton" font-size="104" fill="#fff" stroke="#0c0a18" stroke-width="20" paint-order="stroke">SOLO PUEDE <tspan fill="#ffc93c">ESCRIBIR</tspan></text>'
    return svg(1080, 1920, b)

if __name__ == "__main__":
    L = {"maqueta_dia1": maqueta(), "vale": svg(800, 1160, vale()), "caja": svg(400, 430, caja())}
    import re
    with sync_playwright() as p:
        br = p.chromium.launch(channel="chrome")
        for name, s in L.items():
            w, h = map(int, re.search(r'width="(\d+)" height="(\d+)"', s).groups())
            pg = br.new_page(viewport={"width": w, "height": h}, device_scale_factor=1 if name.startswith("maqueta") else 2); hp = os.path.join(HERE, "_tmp.html")
            open(hp, "w").write(f"<html><head><style>{FONT_CSS} html,body{{margin:0;background:transparent;overflow:hidden}}</style></head><body>{s}</body></html>")
            pg.goto("file://" + hp); pg.wait_for_timeout(250); pg.screenshot(path=os.path.join(HERE, "layers" if not name.startswith("maqueta") else "", name + ".png"), omit_background=not name.startswith("maqueta")); pg.close()
        br.close(); os.remove(os.path.join(HERE, "_tmp.html"))
    print("ok")
