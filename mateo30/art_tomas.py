"""Primo Tomás: otro niño (pelo negro liso con flequillo, lentes redondos, sudadera naranja). Uso: python3 art_tomas.py"""
import os, re, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "mateo-pov")); sys.path.insert(0, os.path.join(HERE, "..", "club-pov"))
import art as A
from art2 import cel, svg, SK, SKS
OUT = os.path.join(HERE, "layers"); OL = "#1d1630"
HA, HAS, HAH = "#22202c", "#121019", "#3d3a4c"; SUD, SUDS, SUDH = "#f08a2c", "#c4661a", "#ffb062"
def cabeza_t():
    b = A.neck(362, 590, 76, 70) + A.face(400, 430, 165)
    b += cel('<path d="M228 440 Q200 230 400 196 Q600 230 572 440 Q566 360 540 330 Q470 350 400 340 Q320 350 262 322 Q236 360 228 440Z"/>', HA, HAS, HAH, -26, -14, 8)
    b += '<ellipse cx="290" cy="520" rx="40" ry="24" fill="#f08a7a" opacity="0.45"/><ellipse cx="510" cy="520" rx="40" ry="24" fill="#f08a7a" opacity="0.45"/>'
    b += cel('<path d="M392 440 Q430 486 408 504 Q390 510 376 498 Q378 470 392 440Z"/>', SK, SKS, None, -8, -4, 5)
    return b
LENTES = (f'<circle cx="336" cy="432" r="58" fill="#ffffff" fill-opacity=".18" stroke="{OL}" stroke-width="9"/><circle cx="464" cy="432" r="58" fill="#ffffff" fill-opacity=".18" stroke="{OL}" stroke-width="9"/>'
          f'<path d="M394 428 Q400 420 406 428" stroke="{OL}" stroke-width="9" fill="none"/><path d="M278 428 L240 416 M522 428 L560 416" stroke="{OL}" stroke-width="9"/>')
def cuerpo_t():
    b = cel('<path d="M150 1900 L160 900 Q170 760 300 720 Q400 700 500 720 Q630 760 640 900 L650 1900Z"/>', SUD, SUDS, SUDH, -46, -8, 8)
    b += cel('<path d="M286 722 Q320 800 400 806 Q480 800 514 722 Q460 744 400 744 Q340 744 286 722Z"/>', SUDS, "#8f4a12", None, -6, -4, 6)
    b += f'<rect x="250" y="1240" width="300" height="170" rx="40" fill="{SUDS}" stroke="{OL}" stroke-width="7"/>'
    b += cel('<path d="M170 800 Q104 900 108 1040 L186 1046 Q190 930 226 860Z"/>', SUD, SUDS, None, 10, 0, 7) + cel('<ellipse cx="146" cy="1084" rx="42" ry="40"/>', SK, SKS, None, 8, -4, 6)
    b += cel('<path d="M630 800 Q696 900 692 1040 L614 1046 Q610 930 574 860Z"/>', SUD, SUDS, None, -10, 0, 7) + cel('<ellipse cx="654" cy="1084" rx="42" ry="40"/>', SK, SKS, None, -8, -4, 6)
    return b
def tomas(kind, hab=False):
    h = cabeza_t() + A._cejas(kind) + A._ojos(kind) + LENTES + ("" if hab else A._boca(kind))
    return svg(800, 1900, cuerpo_t() + f'<g transform="translate(400,700) scale(1.18) translate(-400,-640)">{h}</g>')
L = {"tomas_feliz": tomas("feliz"), "tomas_feliz_hab": tomas("feliz", True), "tomas_neutral": tomas("neutral"), "tomas_travieso": tomas("travieso")}
with sync_playwright() as p:
    br = p.chromium.launch(channel="chrome")
    for name, s in L.items():
        w, h = map(int, re.search(r'width="(\d+)" height="(\d+)"', s).groups())
        pg = br.new_page(viewport={"width": w, "height": h}, device_scale_factor=2); hp = os.path.join(OUT, "_tmp.html")
        open(hp, "w").write(f"<html><head><style>{A.FONT_CSS} html,body{{margin:0;background:transparent;overflow:hidden}}</style></head><body>{s}</body></html>")
        pg.goto("file://" + hp); pg.wait_for_timeout(150); pg.screenshot(path=os.path.join(OUT, name + ".png"), omit_background=True); pg.close()
    br.close(); os.remove(os.path.join(OUT, "_tmp.html"))
