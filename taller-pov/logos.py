"""3 propuestas de logo / foto de perfil para la cuenta "El Taller de Rubén" (1080x1080, todo dentro del círculo)."""
import os, re, sys, math
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import art, cars
from art import svg, glowtext, bricks, NEON_C, NEON_M, OL

FONT_CSS = art.FONT_CSS
DEFS = ('<filter id="blur2"><feGaussianBlur stdDeviation="2"/></filter><filter id="blur12"><feGaussianBlur stdDeviation="12"/></filter>'
        '<filter id="blur40"><feGaussianBlur stdDeviation="40"/></filter>'
        '<filter id="drop"><feDropShadow dx="0" dy="10" stdDeviation="10" flood-opacity="0.5"/></filter>')

def logo_neon():
    """Cartel de neón sobre ladrillo, como el del taller."""
    b = '<rect width="1080" height="1080" fill="#1a1426"/>'
    b += bricks(0, 0, 1080, 1080, 4, ["#4a2a2a", "#432626", "#522e2c", "#3d2322"], 140, 62)
    b += '<rect width="1080" height="1080" fill="#0e0a1c" opacity="0.55"/>'
    b += f'<circle cx="540" cy="540" r="430" fill="{NEON_M}" opacity="0.10" filter="url(#blur40)"/>'
    b += f'<rect x="140" y="300" width="800" height="480" rx="40" fill="#120e1e" stroke="{OL}" stroke-width="12"/>'
    b += f'<rect x="160" y="320" width="760" height="440" rx="30" fill="none" stroke="{NEON_C}" stroke-width="6" filter="url(#blur2)"/>'
    b += glowtext(540, 440, "EL TALLER DE", 70, NEON_C)
    b += glowtext(540, 640, "RUBÉN", 200, NEON_M)
    b += glowtext(540, 720, "DESDE 1996", 40, NEON_C)
    # dos llaves fijas cruzadas sobre el cartel
    for rot in (-28, 28):
        b += f'<g transform="rotate({rot} 540 200)">'
        b += f'<rect x="370" y="184" width="340" height="34" rx="12" fill="#c9cfd9" stroke="{OL}" stroke-width="6"/>'
        for x in (370, 710):
            b += f'<circle cx="{x}" cy="201" r="46" fill="#c9cfd9" stroke="{OL}" stroke-width="6"/>'
            dx = -1 if x == 370 else 1
            b += f'<rect x="{x + dx*10 - 22}" y="183" width="44" height="36" fill="#1a1426" transform="translate({dx*24},0)"/>'
        b += '</g>'
    return svg(1080, 1080, b, DEFS)

def logo_insignia():
    """Insignia circular de taller con el deportivo del tío."""
    d, car = cars.deportivo()
    b = '<rect width="1080" height="1080" fill="#0f0c1c"/>'
    b += '<circle cx="540" cy="540" r="500" fill="#1d1830"/>'
    b += f'<circle cx="540" cy="540" r="470" fill="none" stroke="#e8c04a" stroke-width="16"/>'
    b += f'<circle cx="540" cy="540" r="440" fill="none" stroke="#e8c04a" stroke-width="4"/>'
    b += '<defs><path id="arcT" d="M150 540 A390 390 0 0 1 930 540"/><path id="arcB" d="M175 560 A365 365 0 0 0 905 560"/></defs>'
    b += '<text font-family="Anton" font-size="96" fill="#ffffff" letter-spacing="6"><textPath href="#arcT" startOffset="50%" text-anchor="middle">EL TALLER DE RUBÉN</textPath></text>'
    b += '<text font-family="Anton" font-size="50" fill="#e8c04a" letter-spacing="10"><textPath href="#arcB" startOffset="50%" text-anchor="middle">TUNING · MECÁNICA · 1996</textPath></text>'
    b += f'<circle cx="540" cy="560" r="290" fill="#2a2440"/>'
    b += f'<circle cx="540" cy="560" r="290" fill="{NEON_M}" opacity="0.12"/>'
    b += f'<g transform="translate(540,590) scale(0.6) translate(-540,-330)">{car}</g>'
    for x in (175, 905):
        b += f'<path d="M{x} 540 l14 -30 l14 30 l-14 30Z" fill="#e8c04a"/>'
    return svg(1080, 1080, b, DEFS + d)

def logo_gato():
    """La mascota: el gato negro del taller asomando por la persiana, con una 'R' de neón."""
    b = '<rect width="1080" height="1080" fill="#14102a"/>'
    b += f'<circle cx="540" cy="540" r="460" fill="{NEON_C}" opacity="0.10" filter="url(#blur40)"/>'
    # persiana a medio subir
    b += f'<rect x="190" y="230" width="700" height="620" rx="20" fill="#0a0812" stroke="{OL}" stroke-width="12"/>'
    for y in range(240, 520, 34):
        b += f'<rect x="200" y="{y}" width="680" height="34" fill="#7c7f88"/><rect x="200" y="{y}" width="680" height="10" fill="#a3a6ae"/>'
    b += f'<rect x="200" y="520" width="680" height="26" fill="#3a3c44"/>'
    # gato (de la serie) asomando
    b += '<g transform="translate(540,690) scale(1.15) translate(-200,-210)">' + re.sub(r"^<svg[^>]*>|</svg>$", "", art.gato()) + '</g>'
    b += f'<rect x="190" y="840" width="700" height="20" fill="{OL}"/>'
    # R de neón
    b += glowtext(540, 215, "TALLER  RUBÉN", 92, NEON_M)
    b += glowtext(540, 990, "TÚ DECIDES", 66, NEON_C)
    return svg(1080, 1080, b, DEFS)

if __name__ == "__main__":
    with sync_playwright() as p:
        br = p.chromium.launch()
        for i, fn in enumerate((logo_neon, logo_insignia, logo_gato), 1):
            s = fn()
            pg = br.new_page(viewport={"width": 1080, "height": 1080}, device_scale_factor=1)
            hp = "/tmp/_logo.html"
            open(hp, "w").write(f"<html><head><style>{FONT_CSS} html,body{{margin:0;overflow:hidden}}</style></head><body>{s}</body></html>")
            pg.goto("file://" + hp); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(200)
            pg.screenshot(path=os.path.join(HERE, f"logo_{i}.png")); pg.close(); print("ok", i)
        br.close()
