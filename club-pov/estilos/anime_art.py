"""Arte anime (SVG -> PNG): vestuario al atardecer y Paco con capas (ojos, boca) para animar."""
import os, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "capas_anime"); os.makedirs(OUT, exist_ok=True)
LN = "#3a2838"                   # línea anime (marrón-violeta, no negro)
SK, SKS, BL = "#f8d0b0", "#e7a98a", "#f29a94"
WH, WHS = "#f7f4f2", "#d9d2da"
CAP, CAPS = "#62667a", "#4a4d5f"
BLU, BLUS, BLUH = "#3f74db", "#2b55b0", "#7aa3f2"
BAS, BASS = "#d39a57", "#a06c36"
RD, RDS = "#e2474b", "#b3303a"

def svg(w, h, body, defs=""):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs>{defs}</defs>{body}</svg>'

def sombra(shape_d, shade_d, fill, shade, lw=5, extra=""):
    """Relleno + sombra anime (forma de sombra recortada por la forma) + línea."""
    cid = "c" + str(abs(hash(shape_d)) % 10**8)
    return (f'<clipPath id="{cid}"><path d="{shape_d}"/></clipPath>'
            f'<path d="{shape_d}" fill="{fill}"/>'
            f'<g clip-path="url(#{cid})"><path d="{shade_d}" fill="{shade}"/>{extra}</g>'
            f'<path d="{shape_d}" fill="none" stroke="{LN}" stroke-width="{lw}" stroke-linejoin="round" stroke-linecap="round"/>')

# ------------------------------------------------------------ PACO (900 x 1300)
def paco_base():
    b = ""
    # cuerpo: chaqueta de chándal
    jac = "M 300 560 Q 450 515 600 560 Q 715 600 735 790 L 760 1300 L 140 1300 L 165 790 Q 185 600 300 560 Z"
    b += sombra(jac, "M 520 540 Q 640 570 700 640 Q 745 800 770 1300 L 560 1300 Q 600 900 520 540 Z", BLU, BLUS, 6,
                extra='<path d="M 210 640 Q 260 590 330 575 L 300 700 Q 240 720 210 640 Z" fill="#6f9bf0" opacity=".55"/>')
    for x0, x1 in ((205, 175), (690, 725)):                       # rayas blancas de las mangas
        b += f'<path d="M {x0} 620 Q {x0 - (8 if x0 < 450 else -8)} 900 {x1} 1300" stroke="{WH}" stroke-width="16" fill="none"/>'
        b += f'<path d="M {x0 + (22 if x0 < 450 else -22)} 625 Q {x0 + (14 if x0 < 450 else -30)} 900 {x1 + (22 if x0 < 450 else -22)} 1300" stroke="{WH}" stroke-width="8" fill="none"/>'
    b += f'<path d="M 395 545 L 450 620 L 505 545 Z" fill="#ece6dc" stroke="{LN}" stroke-width="4"/>'        # camiseta interior
    b += f'<path d="M 450 620 L 450 1300" stroke="{BLUS}" stroke-width="6"/><path d="M 450 620 L 450 1300" stroke="#c9d4ea" stroke-width="2" stroke-dasharray="6 8"/>'
    b += f'<path d="M 380 545 Q 450 600 520 545" fill="none" stroke="{LN}" stroke-width="5"/>'
    # cuello
    b += sombra("M 405 470 L 495 470 L 500 555 Q 450 575 400 555 Z", "M 405 470 L 495 470 L 497 520 Q 450 540 403 520 Z", SK, SKS, 5)
    # orejas
    for cx, sx in ((322, 1), (578, -1)):
        b += sombra(f"M {cx} 315 Q {cx - 34 * sx} 312 {cx - 36 * sx} 352 Q {cx - 30 * sx} 392 {cx + 4 * sx} 388 Z",
                    f"M {cx} 315 Q {cx - 20 * sx} 330 {cx - 18 * sx} 370 L {cx + 4 * sx} 388 Z", SK, SKS, 5)
    # cara
    face = "M 330 300 Q 332 205 450 198 Q 568 205 570 300 L 566 395 Q 556 485 450 498 Q 344 485 334 395 Z"
    b += sombra(face, "M 520 205 Q 570 230 570 300 L 566 395 Q 556 485 450 498 Q 520 450 530 360 Q 540 270 520 205 Z", SK, SKS, 6)
    b += f'<ellipse cx="370" cy="410" rx="30" ry="16" fill="{BL}" opacity=".55"/><ellipse cx="530" cy="410" rx="30" ry="16" fill="{BL}" opacity=".55"/>'
    for x, s in ((356, 1), (544, -1)):                            # arrugas
        b += f'<path d="M {x} 352 q {-10 * s} 8 {-6 * s} 20" stroke="{SKS}" stroke-width="3" fill="none"/>'
        b += f'<path d="M {x + 12 * s} 440 q {-12 * s} 10 {-6 * s} 26" stroke="{SKS}" stroke-width="3" fill="none"/>'
    b += f'<path d="M 400 262 q 50 -10 100 0" stroke="{SKS}" stroke-width="3" fill="none"/>'
    # pelo blanco a los lados
    for x, s in ((332, 1), (568, -1)):
        b += sombra(f"M {x} 250 Q {x - 26 * s} 280 {x - 20 * s} 330 Q {x - 4 * s} 316 {x + 8 * s} 330 Q {x + 6 * s} 290 {x + 14 * s} 262 Z",
                    f"M {x} 300 Q {x - 10 * s} 320 {x - 20 * s} 330 Q {x - 4 * s} 316 {x + 8 * s} 330 Z", WH, WHS, 4)
    # gorra plana
    b += sombra("M 314 262 Q 324 178 452 170 Q 592 174 606 250 Q 610 270 588 276 L 326 278 Q 306 276 314 262 Z",
                "M 470 170 Q 592 176 606 250 Q 610 270 588 276 L 470 276 Q 530 220 470 170 Z", CAP, CAPS, 6,
                extra='<path d="M 352 214 Q 420 184 480 186" stroke="#8a8ea2" stroke-width="10" fill="none" opacity=".7"/>')
    b += sombra("M 302 268 Q 452 300 620 262 Q 628 280 606 290 Q 452 318 306 290 Q 292 284 302 268 Z",
                "M 450 306 Q 540 300 620 270 Q 628 280 606 290 Q 452 318 450 306 Z", CAPS, "#3a3c4c", 5)
    # nariz
    b += f'<path d="M 452 360 Q 444 398 430 412 Q 450 424 472 414" fill="none" stroke="{SKS}" stroke-width="5" stroke-linecap="round"/>'
    b += f'<ellipse cx="452" cy="408" rx="20" ry="13" fill="#f2a98f" opacity=".7"/>'
    # cesta y camisetas
    b += sombra("M 250 845 Q 330 805 430 820 Q 500 800 560 822 Q 640 805 660 845 L 640 880 L 270 880 Z",
                "M 250 845 Q 330 805 430 820 L 450 880 L 270 880 Z", RD, RDS, 5)
    b += sombra("M 300 838 Q 380 800 470 818 L 480 870 L 310 870 Z", "M 300 838 L 310 870 L 380 870 Q 360 840 300 838 Z", "#f5f1ea", "#d6cfc6", 4)
    bas = "M 215 870 L 685 870 L 645 1130 Q 450 1160 255 1130 Z"
    weave = "".join(f'<path d="M {215 + i * 4} {900 + i * 42} Q 450 {915 + i * 42} {685 - i * 4} {900 + i * 42}" stroke="{BASS}" stroke-width="6" fill="none"/>' for i in range(6))
    weave += "".join(f'<path d="M {250 + i * 50} 872 Q {245 + i * 50 + (i - 4) * 4} 1000 {262 + i * 46} 1140" stroke="{BASS}" stroke-width="5" fill="none" opacity=".8"/>' for i in range(9))
    b += sombra(bas, "M 520 870 L 685 870 L 645 1130 Q 560 1145 500 1148 Z", BAS, BASS, 6, extra=weave)
    b += f'<path d="M 200 862 Q 450 890 700 862 L 702 884 Q 450 912 198 884 Z" fill="{BAS}" stroke="{LN}" stroke-width="5"/>'
    # manos
    for cx, s in ((222, 1), (678, -1)):
        b += sombra(f"M {cx - 30 * s} 860 Q {cx - 34 * s} 920 {cx + 4 * s} 935 Q {cx + 34 * s} 930 {cx + 30 * s} 880 Q {cx + 10 * s} 850 {cx - 30 * s} 860 Z",
                    f"M {cx} 860 Q {cx + 34 * s} 870 {cx + 30 * s} 900 L {cx + 4 * s} 935 Z", SK, SKS, 5)
    # gafas (montura encima de los ojos: capa aparte)
    return svg(900, 1300, b)

def gafas():
    b = ""
    for x in (355, 465):
        b += f'<rect x="{x}" y="318" width="82" height="64" rx="22" fill="#ffffff" fill-opacity=".12" stroke="#2b2230" stroke-width="10"/>'
        b += f'<path d="M {x + 14} {372} L {x + 40} {330}" stroke="#ffffff" stroke-width="6" opacity=".55"/>'
    b += '<path d="M 437 345 Q 451 336 465 345" stroke="#2b2230" stroke-width="8" fill="none"/>'
    for x, s_ in ((395, 1), (505, -1)):
        b += f'<path d="M {x - 44 * s_} 316 Q {x} 292 {x + 42 * s_} 310 Q {x} 306 {x - 44 * s_} 324 Z" fill="{WH}" stroke="{LN}" stroke-width="4"/>'
    b += '<path d="M 355 340 L 330 334" stroke="#2b2230" stroke-width="8"/><path d="M 547 340 L 572 334" stroke="#2b2230" stroke-width="8"/>'
    return svg(900, 1300, b)

def ojos(cerrados=False):
    b = '<radialGradient id="ir" cx=".5" cy=".35" r=".7"><stop offset="0" stop-color="#9a6a3f"/><stop offset=".6" stop-color="#5a3620"/><stop offset="1" stop-color="#2d1b14"/></radialGradient>'
    if cerrados:
        for cx in (396, 506):
            b += f'<path d="M {cx - 26} 350 Q {cx} 364 {cx + 26} 350" stroke="{LN}" stroke-width="6" fill="none" stroke-linecap="round"/>'
        return svg(900, 1300, b)
    for cx in (396, 506):
        b += f'<path d="M {cx - 28} 332 Q {cx} 318 {cx + 28} 334 L {cx + 26} 368 Q {cx} 378 {cx - 26} 368 Z" fill="#ffffff"/>'
        b += f'<ellipse cx="{cx + 2}" cy="350" rx="20" ry="24" fill="url(#ir)"/><ellipse cx="{cx + 2}" cy="353" rx="9" ry="12" fill="#1b100c"/>'
        b += f'<ellipse cx="{cx - 6}" cy="340" rx="8" ry="9" fill="#fff"/><ellipse cx="{cx + 6}" cy="362" rx="9" ry="4" fill="#d9a46a" opacity=".6"/><circle cx="{cx + 9}" cy="360" r="3" fill="#fff"/>'
        b += f'<path d="M {cx - 30} 334 Q {cx} 314 {cx + 30} 334" stroke="{LN}" stroke-width="7" fill="none" stroke-linecap="round"/>'
    return svg(900, 1300, b)

def boca(n):
    """0 cerrada (sonrisa), 1 entreabierta, 2 abierta. Bigote encima."""
    b = ""
    if n == 0: b += f'<path d="M 428 466 Q 450 474 472 466" stroke="{LN}" stroke-width="5" fill="none" stroke-linecap="round"/>'
    else:
        h = 14 if n == 1 else 30
        b += f'<path d="M 424 458 Q 450 {458 + h + 8} 476 458 Q 450 {462} 424 458 Z" fill="#7a2e3a" stroke="{LN}" stroke-width="4"/>'
        b += f'<ellipse cx="452" cy="{458 + h * .7}" rx="13" ry="{h * .25 + 2}" fill="#e07a84"/>'
    must = "M 378 446 Q 398 414 450 424 Q 502 414 522 446 Q 548 470 526 468 Q 492 458 450 452 Q 408 458 374 468 Q 352 470 378 446 Z"
    b += sombra(must, "M 450 440 Q 500 432 526 468 Q 492 458 450 452 Z", WH, WHS, 4,
                extra="".join(f'<path d="M {400 + i * 14} 432 q 4 14 -2 26" stroke="{WHS}" stroke-width="3" fill="none"/>' for i in range(8)))
    return svg(900, 1300, b)

# ------------------------------------------------------------ FONDO 1080 x 1920
def fondo():
    d = ('<linearGradient id="pared" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f3d9b8"/><stop offset=".55" stop-color="#cdbfae"/><stop offset="1" stop-color="#8f8a8c"/></linearGradient>'
         '<linearGradient id="cielo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7a6fd0"/><stop offset=".45" stop-color="#f29ab0"/><stop offset=".8" stop-color="#ffd08a"/><stop offset="1" stop-color="#fff0c4"/></linearGradient>'
         '<linearGradient id="rayo" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff2c8" stop-opacity=".75"/><stop offset="1" stop-color="#fff2c8" stop-opacity="0"/></linearGradient>'
         '<linearGradient id="suelo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9c7a68"/><stop offset="1" stop-color="#5e4a48"/></linearGradient>'
         '<linearGradient id="tq" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#5f9fc4"/><stop offset="1" stop-color="#3f7aa3"/></linearGradient>'
         '<filter id="b6"><feGaussianBlur stdDeviation="6"/></filter><filter id="b30"><feGaussianBlur stdDeviation="30"/></filter>')
    b = '<rect width="1080" height="1920" fill="url(#pared)"/>'
    for y in range(0, 1150, 70):                                # azulejos suaves
        b += f'<line x1="0" y1="{y}" x2="1080" y2="{y}" stroke="#b9a996" stroke-width="2" opacity=".5"/>'
    for x in range(0, 1080, 70):
        b += f'<line x1="{x}" y1="0" x2="{x}" y2="1150" stroke="#b9a996" stroke-width="2" opacity=".35"/>'
    # ventana con cielo de atardecer
    b += '<rect x="90" y="150" width="380" height="300" rx="10" fill="url(#cielo)" stroke="#6b5148" stroke-width="16"/>'
    for cx, cy, s in ((200, 260, 1), (380, 220, .8), (300, 330, .7)):
        b += f'<g transform="translate({cx},{cy}) scale({s})" opacity=".9"><ellipse rx="70" ry="22" fill="#ffe4ec"/><ellipse cx="-30" cy="-12" rx="40" ry="26" fill="#ffeef2"/><ellipse cx="28" cy="-16" rx="46" ry="30" fill="#fff6f7"/></g>'
    b += '<circle cx="370" cy="400" r="46" fill="#fff4cc" filter="url(#b6)"/>'
    b += '<line x1="280" y1="150" x2="280" y2="450" stroke="#6b5148" stroke-width="12"/><line x1="90" y1="300" x2="470" y2="300" stroke="#6b5148" stroke-width="12"/>'
    # rayos de luz
    b += '<path d="M 90 150 L 470 150 L 1080 900 L 1080 1400 L 300 1100 Z" fill="url(#rayo)" opacity=".55"/>'
    # perchero y camisetas
    b += '<rect x="0" y="520" width="1080" height="18" fill="#8a5a3a"/>'
    for x, c, cs, n in ((560, RD, RDS, "7"), (720, "#f5f1ea", "#d6cfc6", "10"), (880, RD, RDS, "4")):
        sh = f"M {x} 560 L {x + 40} 545 Q {x + 65} 560 {x + 90} 545 L {x + 130} 560 L {x + 150} 610 L {x + 120} 618 L {x + 118} 720 L {x + 12} 720 L {x + 10} 618 L {x - 20} 610 Z"
        b += sombra(sh, f"M {x + 80} 545 L {x + 130} 560 L {x + 150} 610 L {x + 120} 618 L {x + 118} 720 L {x + 90} 720 Z", c, cs, 5)
        b += f'<text x="{x + 65}" y="672" font-family="Anton" font-size="56" text-anchor="middle" fill="{"#fff" if c == RD else RD}">{n}</text>'
    # taquillas
    for i in range(7):
        x = -40 + i * 165
        b += f'<rect x="{x}" y="760" width="158" height="560" fill="url(#tq)" stroke="{LN}" stroke-width="5"/>'
        b += f'<rect x="{x + 8}" y="770" width="16" height="540" fill="#8cc2e0" opacity=".6"/>'
        for k in range(4): b += f'<rect x="{x + 40}" y="{810 + k * 22}" width="80" height="8" rx="4" fill="#2f6488"/>'
        b += f'<rect x="{x + 126}" y="1010" width="10" height="44" rx="4" fill="#d9e2ea" stroke="{LN}" stroke-width="3"/>'
    b += '<path d="M 0 900 L 1080 1300 L 1080 1330 L 0 1330 Z" fill="#fff2c8" opacity=".25"/>'
    # banco y suelo
    b += f'<rect x="0" y="1320" width="1080" height="600" fill="url(#suelo)"/>'
    for i in range(12): b += f'<line x1="{-200 + i * 140}" y1="1920" x2="{300 + i * 70}" y2="1330" stroke="#4e3c3a" stroke-width="3" opacity=".5"/>'
    b += f'<rect x="-20" y="1300" width="1120" height="40" rx="8" fill="#b9814f" stroke="{LN}" stroke-width="5"/>'
    b += '<ellipse cx="760" cy="1600" rx="420" ry="120" fill="#ffe9b8" opacity=".22" filter="url(#b30)"/>'
    return svg(1080, 1920, b, d)

CAPAS = {"paco_base": paco_base, "gafas": gafas, "ojos_a": lambda: ojos(False), "ojos_c": lambda: ojos(True),
         "boca0": lambda: boca(0), "boca1": lambda: boca(1), "boca2": lambda: boca(2), "fondo": fondo}
CSS = "@font-face{font-family:Anton;src:url(file://%s/fonts/Anton-Regular.ttf)}" % os.path.dirname(HERE)

if __name__ == "__main__":
    import re
    with sync_playwright() as p:
        br = p.chromium.launch()
        for name in sys.argv[1:] or CAPAS:
            s = CAPAS[name]()
            w, h = map(int, re.search(r'width="(\d+)" height="(\d+)"', s).groups())
            pg = br.new_page(viewport={"width": w, "height": h}, device_scale_factor=2 if name != "fondo" else 1)
            hp = os.path.join(OUT, "_t.html")
            open(hp, "w").write(f"<html><head><style>{CSS} html,body{{margin:0;background:transparent;overflow:hidden}}</style></head><body>{s}</body></html>")
            pg.goto("file://" + hp); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(80)
            pg.screenshot(path=os.path.join(OUT, name + ".png"), omit_background=True); pg.close(); print("ok", name)
        br.close()
