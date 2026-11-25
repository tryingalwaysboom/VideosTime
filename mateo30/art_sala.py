"""Capas del Día 4 (la sala y el sofá nuevo): bg_sala, marcador, papa_silueta, tarro, dulce, mano_marcador.
Uso: python3 art_sala.py"""
import os, re
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import art30 as B
A = B.A; OL = B.OL
SOFA, SOFAS, SOFAH = "#8fd0c2", "#6fb5a6", "#b5e6da"

def svg(w, h, body): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>'
def R(x, y, w, h, rx, fill, sw=8, extra=""): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{OL}" stroke-width="{sw}" {extra}/>'

def bg_sala():
    b = '<defs><linearGradient id="w" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f8e3c4"/><stop offset="1" stop-color="#f3d2ae"/></linearGradient>'
    b += '<linearGradient id="f" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cfa06a"/><stop offset="1" stop-color="#b98652"/></linearGradient></defs>'
    b += '<rect width="1080" height="1920" fill="url(#w)"/><rect y="1290" width="1080" height="630" fill="url(#f)"/>'
    for y in (1400, 1530, 1680, 1840): b += f'<path d="M0 {y} L1080 {y}" stroke="#a77444" stroke-width="5"/>'
    b += f'<rect y="1268" width="1080" height="26" fill="#fff6e6" stroke="{OL}" stroke-width="5"/>'
    # cuadros
    b += R(120, 300, 250, 300, 10, "#fff6e6") + '<path d="M150 560 L215 430 L262 505 L300 455 L342 560Z" fill="#9cc9a0"/><circle cx="300" cy="380" r="30" fill="#f4b65c"/>'
    b += R(420, 350, 190, 230, 10, "#fff6e6") + f'<path d="M455 540 Q470 430 515 470 Q560 430 575 540" fill="none" stroke="#e2685b" stroke-width="12" stroke-linecap="round"/>'
    # lámpara de pie
    b += f'<path d="M930 620 L930 1290" stroke="{OL}" stroke-width="16"/><path d="M930 620 L930 1290" stroke="#8a6a4a" stroke-width="8"/>'
    b += f'<path d="M850 640 L880 470 L980 470 L1010 640Z" fill="#f4c95c" stroke="{OL}" stroke-width="8" stroke-linejoin="round"/><ellipse cx="930" cy="1292" rx="70" ry="16" fill="#8a6a4a" stroke="{OL}" stroke-width="6"/>'
    # alfombra
    b += f'<ellipse cx="540" cy="1640" rx="470" ry="150" fill="#f0b558" stroke="#d9963a" stroke-width="10"/><ellipse cx="540" cy="1640" rx="380" ry="105" fill="none" stroke="#e2685b" stroke-width="8" stroke-dasharray="34 26"/>'
    # sofá: patas, respaldo, brazos, cojines
    for x in (130, 950): b += f'<rect x="{x - 22}" y="1400" width="44" height="60" rx="8" fill="#7a5636" stroke="{OL}" stroke-width="6"/>'
    b += R(96, 720, 888, 520, 70, SOFA) + f'<path d="M150 760 Q540 730 930 760" stroke="{SOFAH}" stroke-width="16" fill="none" stroke-linecap="round"/>'
    b += R(70, 1130, 940, 290, 50, SOFAS)
    b += R(150, 1080, 385, 190, 40, SOFA) + R(545, 1080, 385, 190, 40, SOFA)
    b += f'<path d="M190 1120 Q340 1100 495 1120" stroke="{SOFAH}" stroke-width="12" fill="none" stroke-linecap="round"/><path d="M585 1120 Q735 1100 890 1120" stroke="{SOFAH}" stroke-width="12" fill="none" stroke-linecap="round"/>'
    b += R(30, 960, 150, 460, 60, SOFA) + R(900, 960, 150, 460, 60, SOFA)
    # etiqueta de "NUEVO" colgando del brazo
    b += f'<path d="M980 1000 Q1010 1060 1000 1110" stroke="{OL}" stroke-width="5" fill="none"/>'
    b += f'<g transform="rotate(8 1000 1170)"><rect x="930" y="1108" width="140" height="92" rx="12" fill="#fff6e6" stroke="{OL}" stroke-width="6"/><circle cx="1000" cy="1124" r="7" fill="{OL}"/>'
    b += f'<text x="1000" y="1180" text-anchor="middle" font-family="Anton" font-size="44" fill="#e2483b">NUEVO</text></g>'
    return svg(1080, 1920, b)

def marcador():
    b = f'<rect x="20" y="100" width="420" height="120" rx="26" fill="#23202e" stroke="{OL}" stroke-width="10"/>'
    b += f'<rect x="120" y="108" width="210" height="104" fill="#f4f1e6"/><text x="225" y="176" text-anchor="middle" font-family="Anton" font-size="46" fill="#e2483b" letter-spacing="1">PERMANENTE</text>'
    b += f'<path d="M440 118 L520 136 L520 184 L440 202Z" fill="#3a3648" stroke="{OL}" stroke-width="10" stroke-linejoin="round"/>'
    b += f'<path d="M520 142 L592 156 Q604 160 592 164 L520 178Z" fill="#111" stroke="{OL}" stroke-width="8" stroke-linejoin="round"/>'
    b += '<path d="M44 124 L110 124" stroke="#4a465c" stroke-width="10" stroke-linecap="round"/>'
    return svg(620, 320, b)

def papa():
    """Papá a contraluz en la puerta: silueta oscura con maletín."""
    c = "#2a2440"
    b = f'<g fill="{c}" stroke="{c}" stroke-width="6" stroke-linejoin="round">'
    b += '<ellipse cx="300" cy="150" rx="92" ry="104"/><path d="M212 130 Q230 40 300 44 Q380 40 390 130 Q350 80 300 92 Q250 80 212 130Z"/>'
    b += '<rect x="262" y="236" width="76" height="60" rx="16"/>'
    b += '<path d="M120 420 Q130 300 250 284 L350 284 Q470 300 480 420 L490 900 L110 900Z"/>'
    b += '<path d="M124 400 Q60 520 76 820 L150 820 Q150 560 190 470Z"/><path d="M476 400 Q540 520 524 820 L450 820 Q450 560 410 470Z"/>'
    b += '<ellipse cx="112" cy="850" rx="44" ry="42"/><ellipse cx="488" cy="850" rx="44" ry="42"/>'
    b += '<path d="M150 880 L140 1560 L270 1560 L300 1000 L330 1560 L460 1560 L450 880Z"/>'
    b += '<path d="M120 1560 Q120 1520 180 1520 L270 1520 L270 1600 L120 1600Z"/><path d="M480 1560 Q480 1520 420 1520 L330 1520 L330 1600 L480 1600Z"/>'
    b += '<rect x="420" y="900" width="170" height="130" rx="14"/><path d="M466 900 Q466 860 505 860 Q544 860 544 900" fill="none" stroke-width="14"/></g>'
    return svg(620, 1620, b)

def tarro():
    b = f'<rect x="70" y="20" width="260" height="70" rx="18" fill="#e2483b" stroke="{OL}" stroke-width="9"/>'
    b += f'<path d="M60 100 Q40 110 40 150 L40 430 Q40 480 90 480 L310 480 Q360 480 360 430 L360 150 Q360 110 340 100Z" fill="#dff1f7" fill-opacity=".9" stroke="{OL}" stroke-width="9"/>'
    import random; r = random.Random(4); cols = ["#e2483b", "#f4b65c", "#6fb5e8", "#9a6fd0", "#63b86a", "#f08ab0"]
    for i in range(34):
        x, y = r.uniform(78, 322), r.uniform(190, 444); b += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r.uniform(24, 32):.0f}" fill="{cols[i % 6]}" stroke="{OL}" stroke-width="5"/>'
    b += f'<path d="M70 150 Q64 280 74 420" stroke="#ffffff" stroke-width="14" fill="none" stroke-linecap="round" opacity=".8"/>'
    b += f'<rect x="120" y="250" width="160" height="80" rx="10" fill="#fff6e6" stroke="{OL}" stroke-width="6"/><text x="200" y="308" text-anchor="middle" font-family="Anton" font-size="50" fill="{OL}">DULCES</text>'
    return svg(400, 500, b)

def dulce():
    b = f'<path d="M110 100 L20 40 L36 100 L20 160Z" fill="#f4b65c" stroke="{OL}" stroke-width="8" stroke-linejoin="round"/><path d="M290 100 L380 40 L364 100 L380 160Z" fill="#f4b65c" stroke="{OL}" stroke-width="8" stroke-linejoin="round"/>'
    b += f'<ellipse cx="200" cy="100" rx="104" ry="78" fill="#e2483b" stroke="{OL}" stroke-width="9"/><path d="M130 70 Q200 30 270 70" stroke="#fff6e6" stroke-width="14" fill="none" stroke-linecap="round"/><path d="M130 130 Q200 170 270 130" stroke="#fff6e6" stroke-width="14" fill="none" stroke-linecap="round"/>'
    return svg(400, 200, b)

L = {"bg_sala": bg_sala(), "marcador": marcador(), "papa_silueta": papa(), "tarro": tarro(), "dulce": dulce()}
with sync_playwright() as p:
    br = p.chromium.launch(channel="chrome")
    for name, s in L.items():
        w, h = map(int, re.search(r'width="(\d+)" height="(\d+)"', s).groups())
        pg = br.new_page(viewport={"width": w, "height": h}, device_scale_factor=2); hp = os.path.join(B.OUT, "_tmp.html")
        open(hp, "w").write(f"<html><head><style>{A.FONT_CSS} html,body{{margin:0;background:transparent;overflow:hidden}}</style></head><body>{s}</body></html>")
        pg.goto("file://" + hp); pg.wait_for_timeout(200); pg.screenshot(path=os.path.join(B.OUT, name + ".png"), omit_background=True); pg.close()
    br.close(); os.remove(os.path.join(B.OUT, "_tmp.html"))
# la mano que escribe, con marcador negro en vez de crayola verde
im = np.array(Image.open(os.path.join(B.OUT, "mano_crayola.png")).convert("RGBA")).astype(np.float32)
r, g, b_ = im[..., 0], im[..., 1], im[..., 2]; m = (g > r * 1.25) & (g > b_ * 1.25)
lum = (.3 * r + .6 * g + .1 * b_) * .28
for k in range(3): im[..., k] = np.where(m, lum, im[..., k])
Image.fromarray(im.astype(np.uint8)).save(os.path.join(B.OUT, "mano_marcador.png"))
print("ok")
