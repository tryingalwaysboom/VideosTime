"""Mateo con los brazos cruzados (capas mateo_<cara>_x). Uso: python3 art_cruzado.py"""
import os, re
from playwright.sync_api import sync_playwright
import art30 as B
A = B.A; cel = B.cel; OL = B.OL
def cuerpo_x(brazos=True):
    b = cel('<path d="M150 1900 L160 900 Q170 760 300 720 Q400 700 500 720 Q630 760 640 900 L650 1900Z"/>', B.BATA, B.BATAS, B.BATAH, -46, -8, 8)
    b += f'<path d="M400 760 L400 1900" stroke="{B.BATAS}" stroke-width="8"/>'
    for y in (1330, 1510, 1690): b += f'<circle cx="400" cy="{y}" r="15" fill="{B.CREMA}" stroke="{OL}" stroke-width="5"/>'
    b += cel('<path d="M290 722 Q300 800 392 800 L400 742 L408 800 Q500 800 510 722 Q460 700 400 704 Q340 700 290 722Z"/>', B.CREMA, "#d9cfbd", None, -6, -4, 6)
    if not brazos: return b
    # brazos: del hombro al codo
    b += cel('<path d="M172 800 Q96 900 112 1050 L214 1066 Q204 930 232 860Z"/>', B.BATA, B.BATAS, None, 10, 0, 7)
    b += cel('<path d="M628 800 Q704 900 688 1050 L586 1066 Q596 930 568 860Z"/>', B.BATA, B.BATAS, None, -10, 0, 7)
    def antebrazo(x0, y0, x1, y1):      # del codo a la mano, con puño claro
        ux, uy = x1 - x0, y1 - y0; L = (ux * ux + uy * uy) ** .5; ux, uy = ux / L, uy / L; cx, cy = x1 - ux * 58, y1 - uy * 58
        s = f'<path d="M{x0} {y0} L{x1} {y1}" stroke="{OL}" stroke-width="112" stroke-linecap="round"/><path d="M{x0} {y0} L{x1} {y1}" stroke="{B.BATA}" stroke-width="98" stroke-linecap="round"/>'
        s += f'<path d="M{cx} {cy} L{x1} {y1}" stroke="{OL}" stroke-width="112"/><path d="M{cx + ux * 5} {cy + uy * 5} L{x1 - ux * 5} {y1 - uy * 5}" stroke="{B.CREMA}" stroke-width="98"/>'
        s += f'<ellipse cx="{x1 + ux * 34}" cy="{y1 + uy * 34}" rx="46" ry="44" fill="{B.SK}" stroke="{OL}" stroke-width="7"/>'
        return s
    b += antebrazo(628, 1040, 300, 1000)      # el derecho, por detrás: su mano asoma a la izquierda
    b += antebrazo(172, 1050, 500, 1090)      # el izquierdo, por delante
    return b
def mateo_x(kind, hablando=False):
    h = A._mateo_cabeza() + A._cejas(kind) + A._ojos(kind) + ("" if hablando else A._boca(kind))
    return B.svg(800, 1900, cuerpo_x() + f'<g transform="translate(400,700) scale(1.18) translate(-400,-640)">{h}</g>')
def mateo_tira():
    """Enojado, con su brazo izquierdo colgando y sin el derecho (el que lanza se anima en el render)."""
    b = cuerpo_x(False)
    b += cel('<path d="M172 800 Q84 900 92 1250 L196 1250 Q204 930 232 860Z"/>', B.BATA, B.BATAS, None, 10, 0, 7)
    b += f'<rect x="88" y="1236" width="112" height="52" rx="10" fill="{B.CREMA}" stroke="{OL}" stroke-width="7"/><ellipse cx="144" cy="1326" rx="46" ry="44" fill="{B.SK}" stroke="{OL}" stroke-width="7"/>'
    h = A._mateo_cabeza() + A._cejas("enojado") + A._ojos("enojado") + A._boca("enojado")
    return B.svg(800, 1900, b + f'<g transform="translate(400,700) scale(1.18) translate(-400,-640)">{h}</g>')
L = {"mateo_enojado_x": mateo_x("enojado"), "mateo_neutral_x": mateo_x("neutral"), "mateo_neutral_x_hab": mateo_x("neutral", True), "mateo_enojado_tira": B.mateo("enojado", False, brazo_der=False), "mateo_feliz_tira": B.mateo("feliz", False, brazo_der=False), "mateo_feliz_tira_hab": B.mateo("feliz", True, brazo_der=False)}
with sync_playwright() as p:
    br = p.chromium.launch(channel="chrome")
    for name, s in L.items():
        w, h = map(int, re.search(r'width="(\d+)" height="(\d+)"', s).groups())
        pg = br.new_page(viewport={"width": w, "height": h}, device_scale_factor=2); hp = os.path.join(B.OUT, "_tmp.html")
        open(hp, "w").write(f"<html><head><style>{A.FONT_CSS} html,body{{margin:0;background:transparent;overflow:hidden}}</style></head><body>{s}</body></html>")
        pg.goto("file://" + hp); pg.wait_for_timeout(150); pg.screenshot(path=os.path.join(B.OUT, name + ".png"), omit_background=True); pg.close()
    br.close(); os.remove(os.path.join(B.OUT, "_tmp.html"))
