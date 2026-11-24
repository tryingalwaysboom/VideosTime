"""Arte de la temporada "Mateo: 30 días para no repetir". Misma cara y pelo de Mateo; ropa nueva:
bata azul de preescolar con una etiqueta de nombre en el pecho que se va llenando letra a letra.
Uso: python3 art30.py [letras_dominadas]   (por defecto "", etiqueta vacía del Día 1)"""
import os, re, sys
from PIL import Image
import numpy as np
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "mateo-pov")); sys.path.insert(0, os.path.join(HERE, "..", "club-pov"))
import art as A
from art2 import cel, svg, SK, SKS, SKH
OUT = os.path.join(HERE, "layers"); OLD = os.path.join(HERE, "..", "mateo-pov", "layers")
OL = "#1d1630"; BATA = "#3f7fd0"; BATAS = "#2c5ea6"; BATAH = "#6da4ec"; CREMA = "#fffdf4"

def cuerpo(letras="", brazo_der=True):
    b = cel('<path d="M150 1900 L160 900 Q170 760 300 720 Q400 700 500 720 Q630 760 640 900 L650 1900Z"/>', BATA, BATAS, BATAH, -46, -8, 8)
    b += f'<path d="M400 760 L400 1900" stroke="{BATAS}" stroke-width="8"/>'
    for y in (1150, 1330, 1510, 1690): b += f'<circle cx="400" cy="{y}" r="15" fill="{CREMA}" stroke="{OL}" stroke-width="5"/>'
    # cuello redondo blanco
    b += cel('<path d="M290 722 Q300 800 392 800 L400 742 L408 800 Q500 800 510 722 Q460 700 400 704 Q340 700 290 722Z"/>', CREMA, "#d9cfbd", None, -6, -4, 6)
    # mangas largas con puño claro y manos
    b += cel('<path d="M170 800 Q104 900 108 1040 L186 1046 Q190 930 226 860Z"/>', BATA, BATAS, None, 10, 0, 7)
    b += cel('<path d="M104 1030 L190 1036 L188 1076 L104 1070Z"/>', CREMA, "#d9cfbd", None, 4, 0, 5)
    b += cel('<ellipse cx="146" cy="1104" rx="42" ry="40"/>', SK, SKS, None, 8, -4, 6)
    if brazo_der:
        b += cel('<path d="M630 800 Q696 900 692 1040 L614 1046 Q610 930 574 860Z"/>', BATA, BATAS, None, -10, 0, 7)
        b += cel('<path d="M696 1030 L610 1036 L612 1076 L696 1070Z"/>', CREMA, "#d9cfbd", None, -4, 0, 5)
        b += cel('<ellipse cx="654" cy="1104" rx="42" ry="40"/>', SK, SKS, None, -8, -4, 6)
    # etiqueta de nombre: vacía el Día 1; se llena letra a letra
    b += f'<g transform="rotate(-4 400 960)"><rect x="262" y="880" width="276" height="150" rx="16" fill="{CREMA}" stroke="{OL}" stroke-width="7"/>'
    b += '<rect x="262" y="880" width="276" height="46" rx="16" fill="#e2483b"/><rect x="262" y="906" width="276" height="20" fill="#e2483b"/>'
    b += f'<text x="400" y="915" text-anchor="middle" font-family="Anton" font-size="30" fill="{CREMA}" letter-spacing="2">MI NOMBRE</text>'
    for i, ch in enumerate("MATEO"):
        x = 300 + i * 50
        if ch in letras: b += f'<text x="{x}" y="1006" text-anchor="middle" font-family="Caveat" font-weight="700" font-size="74" fill="#2c5ea6">{ch}</text>'
        else: b += f'<path d="M{x-17} 1008 L{x+17} 1008" stroke="#9a9aa6" stroke-width="6" stroke-linecap="round"/>'
    b += '</g>'
    return b

BOCA_LENGUA = ('<path d="M366 556 Q400 574 434 556" stroke="#1d1630" stroke-width="9" fill="none" stroke-linecap="round"/>'
               '<path d="M408 562 Q436 566 438 590 Q434 610 414 606 Q400 596 408 562Z" fill="#e2707a" stroke="#1d1630" stroke-width="6"/>')
OJOS_ABAJO = (f'<ellipse cx="336" cy="436" rx="32" ry="26" fill="#fff" stroke="{OL}" stroke-width="4"/><circle cx="338" cy="446" r="19" fill="#4a3424"/><circle cx="338" cy="446" r="10" fill="{OL}"/>'
              f'<ellipse cx="464" cy="436" rx="32" ry="26" fill="#fff" stroke="{OL}" stroke-width="4"/><circle cx="466" cy="446" r="19" fill="#4a3424"/><circle cx="466" cy="446" r="10" fill="{OL}"/>'
              '<path d="M298 418 L374 422" stroke="#f3c29b" stroke-width="22"/><path d="M426 422 L502 418" stroke="#f3c29b" stroke-width="22"/>')
OJOS_SUSTO = (f'<ellipse cx="336" cy="430" rx="38" ry="36" fill="#fff" stroke="{OL}" stroke-width="4"/><circle cx="336" cy="430" r="20" fill="#4a3424"/><circle cx="336" cy="430" r="10" fill="{OL}"/><circle cx="345" cy="420" r="7" fill="#fff"/>'
              f'<ellipse cx="464" cy="430" rx="38" ry="36" fill="#fff" stroke="{OL}" stroke-width="4"/><circle cx="464" cy="430" r="20" fill="#4a3424"/><circle cx="464" cy="430" r="10" fill="{OL}"/><circle cx="473" cy="420" r="7" fill="#fff"/>')

def mateo(kind="neutral", hablando=False, letras="", brazo_der=True):
    base = {"concentra": "neutral", "susto": "triste"}.get(kind, kind)
    h = A._mateo_cabeza() + A._cejas("enojado" if kind == "concentra" else base)
    h += OJOS_ABAJO if kind == "concentra" else (OJOS_SUSTO if kind == "susto" else A._ojos(base))
    if not hablando: h += BOCA_LENGUA if kind == "concentra" else (A._boca("timido") if kind == "susto" else A._boca(base))
    return svg(800, 1900, cuerpo(letras, brazo_der) + f'<g transform="translate(400,700) scale(1.18) translate(-400,-640)">{h}</g>')

def cabeza(kind="timido", hablando=False):
    """Solo cabeza y cuello (para la cama)."""
    base = {"susto": "triste"}.get(kind, kind)
    h = A._mateo_cabeza() + A._cejas(base) + (OJOS_SUSTO if kind == "susto" else A._ojos(base))
    if not hablando: h += A._boca("timido" if kind == "susto" else base)
    return svg(800, 900, f'<g transform="translate(400,560) scale(1.18) translate(-400,-640)">{h}</g>')

def render(letras):
    L = {}
    for k in ("neutral", "timido", "triste", "feliz", "travieso", "concentra", "susto", "llora"):
        L["mateo_" + k] = mateo(k, False, letras)
        L["mateo_" + k + "_hab"] = mateo(k, True, letras)
    L["mateo_concentra_sinbrazo"] = mateo("concentra", False, letras, False)
    for k in ("timido", "susto", "triste"):
        L["cab_" + k] = cabeza(k); L["cab_" + k + "_hab"] = cabeza(k, True)
    with sync_playwright() as p:
        br = p.chromium.launch(channel="chrome")
        for name, s in L.items():
            w, h = map(int, re.search(r'width="(\d+)" height="(\d+)"', s).groups())
            pg = br.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
            hp = os.path.join(OUT, "_tmp.html")
            open(hp, "w").write(f"<html><head><style>{A.FONT_CSS} html,body{{margin:0;background:transparent;overflow:hidden}}</style></head><body>{s}</body></html>")
            pg.goto("file://" + hp); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(120)
            pg.screenshot(path=os.path.join(OUT, name + ".png"), omit_background=True); pg.close()
        br.close(); os.remove(os.path.join(OUT, "_tmp.html"))
    # capas que se reutilizan tal cual
    for n in ("bg_escuela", "bg_cocina", "bg_mesa", "bg_noche", "bg_cuarto", "bg_puerta", "maestra", "maestra_hab", "hoja", "crayola"):
        Image.open(os.path.join(OLD, n + ".png")).save(os.path.join(OUT, n + ".png"))
    # mano con crayola: la manga verde pasa a azul de la bata (la crayola sigue verde)
    im = np.array(Image.open(os.path.join(OLD, "mano_crayola.png")).convert("RGBA")).astype(np.int32)
    r, g, b_ = im[..., 0], im[..., 1], im[..., 2]
    yy, xx = np.mgrid[0:im.shape[0], 0:im.shape[1]]
    verde = (g > r + 12) & (g > b_ + 12) & (yy > im.shape[0] * .28) & (xx > im.shape[1] * .62)
    lum = g[verde] / 176.0
    im[..., 0][verde] = np.clip(63 * lum, 0, 255); im[..., 1][verde] = np.clip(127 * lum, 0, 255); im[..., 2][verde] = np.clip(208 * lum, 0, 255)
    Image.fromarray(im.astype(np.uint8), "RGBA").save(os.path.join(OUT, "mano_crayola.png"))
    print("ok", len(L))

if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else "")
