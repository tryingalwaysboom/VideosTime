"""Arte de "El cuaderno de la abuela": Sofía (5 años), desván, cuaderno de flores. Mismo estilo cartoon que Mateo
(cel-shading, contorno grueso). Diseño de personajes CERRADO desde la Parte 1 (guía de la serie)."""
import os, random, re, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "club-pov")); sys.path.insert(0, os.path.join(HERE, "..", "mateo-pov"))
from art2 import cel, svg, sky, eye, face, neck, SK, SKS, SKH  # noqa: E402
import importlib.util
_s = importlib.util.spec_from_file_location("MA", os.path.join(HERE, "..", "mateo-pov", "art.py"))
MA = importlib.util.module_from_spec(_s); _s.loader.exec_module(MA)

OUT = os.path.join(HERE, "layers"); os.makedirs(OUT, exist_ok=True)
OL = "#1d1630"
HAIR = "#3b2416"; HAIRS = "#24150c"; HAIRH = "#5c3a24"
TEE = "#f6c94a"; TEES = "#d6a52c"; TEEH = "#ffe07a"   # camiseta amarilla con estrella
LAZO = "#e8556d"

# ============================================================ SOFÍA
def _sofia_cuerpo():
    b = ''
    torso = '<path d="M160 1900 L170 900 Q180 770 300 730 Q400 712 500 730 Q620 770 630 900 L640 1900Z"/>'
    b += cel(torso, TEE, TEES, TEEH, -46, -8, 8)
    # estrella blanca
    import math
    pts = []
    for k in range(10):
        r = 92 if k % 2 == 0 else 40; a = -math.pi / 2 + k * math.pi / 5
        pts.append(f"{400 + r * math.cos(a):.1f} {960 + r * math.sin(a):.1f}")
    b += f'<path d="M{" L".join(pts)}Z" fill="#fffaf0" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
    b += cel('<path d="M330 722 Q400 772 470 722 L462 708 Q400 744 338 708Z"/>', TEES, "#b88a1e", None, -4, 0, 5)
    # mangas cortas y brazos
    b += cel('<path d="M180 800 Q120 900 128 1010 L188 1016 Q194 920 226 860Z"/>', TEE, TEES, None, 10, 0, 7)
    b += cel('<path d="M620 800 Q680 900 672 1010 L612 1016 Q606 920 574 860Z"/>', TEE, TEES, None, -10, 0, 7)
    b += cel('<ellipse cx="158" cy="1036" rx="40" ry="38"/>', SK, SKS, None, 8, -4, 6)
    b += cel('<ellipse cx="642" cy="1036" rx="40" ry="38"/>', SK, SKS, None, -8, -4, 6)
    return b

def _coletas_atras():
    """Pelo de detrás y las dos coletas con lazo rosa (van por detrás de la cara)."""
    b = cel('<path d="M236 470 Q210 250 400 214 Q590 250 564 470 Q560 560 520 600 L280 600 Q240 560 236 470Z"/>', HAIR, HAIRS, HAIRH, -24, -10, 8)
    for sx in (-1, 1):
        x0 = 400 + sx * 175
        b += cel(f'<path d="M{x0} 400 Q{x0 + sx * 120} 420 {x0 + sx * 130} 540 Q{x0 + sx * 120} 650 {x0 + sx * 60} 690 Q{x0 + sx * 70} 600 {x0 + sx * 30} 520 Q{x0 + sx * 10} 460 {x0} 440Z"/>',
                 HAIR, HAIRS, HAIRH, -sx * 14, -6, 8)
        # lazo
        lx, ly = x0 + sx * 34, 410
        b += cel(f'<path d="M{lx} {ly} L{lx - 46} {ly - 34} L{lx - 46} {ly + 34}Z"/>', LAZO, "#bf3a52", None, -4, 0, 6)
        b += cel(f'<path d="M{lx} {ly} L{lx + 46} {ly - 34} L{lx + 46} {ly + 34}Z"/>', LAZO, "#bf3a52", None, -4, 0, 6)
        b += f'<circle cx="{lx}" cy="{ly}" r="15" fill="{LAZO}" stroke="{OL}" stroke-width="5"/>'
    return b

def _sofia_cabeza():
    b = neck(362, 590, 76, 70)
    b += face(400, 430, 162)
    # flequillo recto con mechones
    b += cel('<path d="M240 400 Q236 250 400 236 Q564 250 560 400 Q540 340 500 334 L480 372 L452 330 L420 370 L392 328 L360 368 L332 330 L304 366 Q270 350 240 400Z"/>',
             HAIR, HAIRS, HAIRH, -20, -10, 8)
    b += '<ellipse cx="290" cy="520" rx="40" ry="24" fill="#f08a7a" opacity="0.5"/><ellipse cx="510" cy="520" rx="40" ry="24" fill="#f08a7a" opacity="0.5"/>'
    b += cel('<path d="M394 446 Q424 482 408 498 Q392 504 380 494 Q382 470 394 446Z"/>', SK, SKS, None, -8, -4, 5)
    return b

def _pestanas():
    """Pestañas de niña sobre cada ojo."""
    b = ''
    for x in (336, 464):
        s = -1 if x < 400 else 1
        b += f'<path d="M{x + s * 30} 414 l{s * 14} -12 M{x + s * 22} 406 l{s * 10} -14" stroke="{OL}" stroke-width="6" stroke-linecap="round"/>'
    return b

def sofia(kind="neutral", hablando=False):
    """Sofía, 5 años. hablando=True deja la boca vacía (centro de boca en 400,606 tras la escala)."""
    h = _coletas_atras() + _sofia_cabeza() + MA._cejas(kind) + MA._ojos(kind)
    if kind not in ("feliz", "llora"): h += _pestanas()
    if not hablando: h += MA._boca(kind)
    b = _sofia_cuerpo() + f'<g transform="translate(400,700) scale(1.18) translate(-400,-640)">{h}</g>'
    return svg(800, 1900, b)

def sofia_mano_crayola():
    """Mano de Sofía (manga amarilla) con crayola rosa, para las escenas de escritura (punta en 330,1010 del lienzo)."""
    b = cel('<path d="M820 1500 L560 1120 L650 1060 L900 1420Z"/>', TEE, TEES, None, -8, 0, 7)
    b += MA._crayola_diag(560, 1000, 330, 1010, 50).replace("#3fae4a", "#e8556d").replace("#2c8236", "#bf3a52").replace("#6fd078", "#f48aa0")
    b += cel('<path d="M470 1000 Q470 920 560 920 Q650 930 660 1010 Q660 1100 570 1110 Q480 1100 470 1000Z"/>', SK, SKS, SKH, -10, -8, 7)
    for (x, y) in ((488, 960), (482, 1000), (492, 1040)):
        b += cel(f'<ellipse cx="{x}" cy="{y}" rx="30" ry="20"/>', SK, SKS, None, -4, -4, 5)
    return svg(1000, 1600, b)

# ============================================================ FONDOS
def bg_cuarto_sofia():
    """Cuarto de Sofía a la tarde: pared lila con dibujos, mesita, ventana."""
    d = sky("wl", [(0, "#d9c3ee"), (1, "#bfa3dc")])
    d += '<radialGradient id="lamp" cx="0.3" cy="0.3" r="0.7"><stop offset="0" stop-color="#ffe7b0" stop-opacity="0.5"/><stop offset="1" stop-color="#ffe7b0" stop-opacity="0"/></radialGradient>'
    b = '<rect width="1080" height="1920" fill="url(#wl)"/>'
    r = random.Random(4)
    for _ in range(30):
        b += f'<circle cx="{r.randint(20, 1060)}" cy="{r.randint(40, 1200)}" r="{r.randint(5, 9)}" fill="#fff" opacity="0.35"/>'
    b += f'<rect x="640" y="260" width="360" height="420" rx="18" fill="#ffd89a" stroke="{OL}" stroke-width="9"/>'
    b += f'<path d="M820 260 L820 680 M640 470 L1000 470" stroke="{OL}" stroke-width="8"/>'
    b += cel('<path d="M620 240 Q660 460 640 700 L600 700 Q590 460 600 240Z"/>', "#f28ab0", "#cf6690", None, -10, 0, 7)
    b += cel('<path d="M1020 240 Q980 460 1000 700 L1040 700 Q1050 460 1040 240Z"/>', "#f28ab0", "#cf6690", None, 10, 0, 7)
    cols = ["#e8556d", "#4a9fe0", "#5fbf6a", "#f2a23a"]
    for i in range(4):
        x, y, rot = 60 + i * 140, 300 + (i % 2) * 60, r.randint(-8, 8)
        b += f'<g transform="rotate({rot} {x+60} {y+75})"><rect x="{x}" y="{y}" width="120" height="150" fill="#fffdf6" stroke="{OL}" stroke-width="5"/>'
        b += f'<circle cx="{x+60}" cy="{y+60}" r="30" fill="none" stroke="{cols[i]}" stroke-width="7"/><path d="M{x+30} {y+130} L{x+60} {y+90} L{x+90} {y+130}" stroke="{cols[i]}" stroke-width="7" fill="none"/></g>'
    b += '<rect x="0" y="1300" width="1080" height="30" fill="#f2efe6"/><rect x="0" y="1330" width="1080" height="600" fill="#caa07a"/>'
    for y in range(1330, 1920, 80): b += f'<path d="M0 {y} L1080 {y}" stroke="#ad8358" stroke-width="4"/>'
    b += '<ellipse cx="540" cy="1660" rx="460" ry="150" fill="#f7c6d4" stroke="#e48aa4" stroke-width="10"/>'
    b += '<rect width="1080" height="1920" fill="url(#lamp)"/>'
    return svg(1080, 1920, b, d)

def bg_desvan():
    """Desván de noche: vigas inclinadas, ventanita redonda con luna, cajas de cartón, bombilla cálida colgando."""
    d = sky("wd", [(0, "#4a3a5e"), (1, "#2c2240")])
    d += '<radialGradient id="bulb" cx="0.5" cy="0.22" r="0.65"><stop offset="0" stop-color="#ffd98a" stop-opacity="0.75"/><stop offset="0.5" stop-color="#ffb860" stop-opacity="0.25"/><stop offset="1" stop-color="#ffb860" stop-opacity="0"/></radialGradient>'
    b = '<rect width="1080" height="1920" fill="url(#wd)"/>'
    # tablas de la pared
    for x in range(0, 1080, 120): b += f'<path d="M{x} 0 L{x} 1350" stroke="#22192f" stroke-width="5" opacity="0.6"/>'
    # techo inclinado (vigas)
    b += f'<path d="M-20 0 L-20 700 L540 80 L1100 700 L1100 0Z" fill="#5a4330" stroke="{OL}" stroke-width="9"/>'
    for k in range(6):
        y = 60 + k * 110
        b += f'<path d="M-20 {700 - k * 120} L540 {80 + k * 0}" stroke="#3e2d20" stroke-width="6" opacity="0.5"/>'
    b += f'<path d="M-20 700 L540 80 L1100 700" stroke="#7a5a3e" stroke-width="40" fill="none"/><path d="M-20 700 L540 80 L1100 700" stroke="{OL}" stroke-width="8" fill="none"/>'
    # ventanita redonda con luna
    b += f'<circle cx="540" cy="470" r="120" fill="#1c2a5a" stroke="{OL}" stroke-width="10"/>'
    b += '<circle cx="585" cy="440" r="44" fill="#fff4c8"/><circle cx="605" cy="425" r="40" fill="#1c2a5a"/>'
    for (x, y) in ((480, 420), (500, 520), (560, 540), (470, 480)): b += f'<circle cx="{x}" cy="{y}" r="4" fill="#fff" opacity="0.9"/>'
    b += f'<path d="M540 350 L540 590 M420 470 L660 470" stroke="#7a5a3e" stroke-width="12"/><circle cx="540" cy="470" r="120" fill="none" stroke="{OL}" stroke-width="10"/>'
    # bombilla
    b += f'<path d="M540 80 L540 250" stroke="{OL}" stroke-width="5"/><circle cx="540" cy="275" r="30" fill="#ffe9a8" stroke="{OL}" stroke-width="5"/>'
    # suelo de tablas
    b += '<rect x="0" y="1350" width="1080" height="570" fill="#6b4a30"/>'
    for y in range(1350, 1920, 70): b += f'<path d="M0 {y} L1080 {y}" stroke="#4f3520" stroke-width="5"/>'
    # cajas
    for (x, y, w, h, rot) in ((40, 1020, 300, 340, -3), (760, 960, 300, 400, 4), (300, 1160, 220, 200, 2)):
        b += f'<g transform="rotate({rot} {x+w/2} {y+h/2})">' + cel(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>', "#c8955a", "#9e7040", "#ddb07a", -16, -6, 7)
        b += f'<path d="M{x} {y+40} L{x+w} {y+40}" stroke="#8a5e34" stroke-width="5"/><rect x="{x+w/2-40}" y="{y}" width="80" height="{h}" fill="#e0c088" opacity="0.5"/></g>'
    b += '<text x="190" y="1220" font-family="Caveat" font-weight="700" font-size="54" text-anchor="middle" fill="#5a3a1a" transform="rotate(-3 190 1220)">Recuerdos</text>'
    b += '<rect width="1080" height="1920" fill="url(#bulb)"/>'
    return svg(1080, 1920, b, d)

# ============================================================ OBJETOS
def _flores(cx, cy, s, cols):
    b = ''
    for k, (dx, dy) in enumerate(((0, 0), (-70, 50), (70, 60), (-30, -70), (60, -50))):
        x, y = cx + dx * s, cy + dy * s; col = cols[k % len(cols)]
        for j in range(5):
            import math
            a = j * 2 * math.pi / 5
            b += f'<circle cx="{x + 22 * s * math.cos(a):.1f}" cy="{y + 22 * s * math.sin(a):.1f}" r="{18 * s:.1f}" fill="{col}" stroke="{OL}" stroke-width="3"/>'
        b += f'<circle cx="{x}" cy="{y}" r="{11 * s:.1f}" fill="#ffd24a" stroke="{OL}" stroke-width="3"/>'
    return b

def cuaderno():
    """Cuaderno viejo cerrado: tapa verde salvia con flores, esquinas gastadas, etiqueta con un nombre de niña."""
    b = f'<rect x="60" y="40" width="680" height="900" rx="26" fill="#7a5a3e" stroke="{OL}" stroke-width="9"/>'
    b += cel('<rect x="40" y="20" width="680" height="900" rx="26"/>', "#8fb59a", "#6c9478", "#b4d4bc", -20, -10, 9)
    b += f'<rect x="40" y="20" width="70" height="900" rx="20" fill="#6c9478" stroke="{OL}" stroke-width="7"/>'
    b += _flores(470, 230, 1.3, ["#f28ab0", "#f6efe2", "#e8556d"])
    b += _flores(250, 760, 1.1, ["#f6efe2", "#f28ab0", "#b88ad6"])
    # etiqueta con nombre a mano (garabato ilegible + subrayado)
    b += f'<rect x="200" y="420" width="420" height="190" rx="18" fill="#fbf3df" stroke="{OL}" stroke-width="7" transform="rotate(-3 410 515)"/>'
    b += '<text x="410" y="490" font-family="Caveat" font-weight="700" font-size="48" text-anchor="middle" fill="#6a5a4a" transform="rotate(-3 410 490)">Este cuaderno es de:</text>'
    b += '<path d="M260 560 Q290 520 320 560 Q350 590 380 550 Q410 520 440 560 Q470 590 500 545 Q530 520 560 556" stroke="#c23a5a" stroke-width="9" fill="none" stroke-linecap="round" transform="rotate(-3 410 550)"/>'
    # desgaste
    b += '<path d="M40 860 Q90 900 140 920" stroke="#e8dfc8" stroke-width="10" fill="none" opacity="0.6"/>'
    return svg(780, 960, b)

def caja_desvan():
    b = cel('<path d="M60 220 L700 220 L680 760 L80 760Z"/>', "#c8955a", "#9e7040", "#ddb07a", -16, -6, 8)
    b += cel('<path d="M60 220 L-20 120 L330 120 L380 220Z"/>', "#d6a46a", "#a87a48", None, -6, -4, 7)
    b += cel('<path d="M700 220 L790 110 L440 110 L380 220Z"/>', "#d6a46a", "#a87a48", None, 6, -4, 7)
    b += '<text x="380" y="520" font-family="Caveat" font-weight="700" font-size="84" text-anchor="middle" fill="#5a3a1a">Recuerdos</text>'
    return svg(800, 800, b)

LAYERS = {"bg_desvan": bg_desvan, "bg_cuarto_sofia": bg_cuarto_sofia, "cuaderno": cuaderno, "caja_desvan": caja_desvan,
          "sofia_mano_crayola": sofia_mano_crayola}
for k in ("neutral", "llora", "triste", "timido", "feliz", "enojado"):
    LAYERS["sofia_" + k] = (lambda kk: (lambda: sofia(kk)))(k)
    LAYERS["sofia_" + k + "_hab"] = (lambda kk: (lambda: sofia(kk, True)))(k)

FONT_CSS = ("@font-face{font-family:Anton;src:url(file://%s/../mateo-pov/fonts/Anton-Regular.ttf)}"
            "@font-face{font-family:Caveat;font-weight:700;src:url(file://%s/../mateo-pov/fonts/Caveat.ttf)}") % (HERE, HERE)

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
            pg.goto("file://" + hp); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(120)
            pg.screenshot(path=os.path.join(OUT, name + ".png"), omit_background=True)
            pg.close(); print("ok", name, flush=True)
        br.close()
        os.remove(os.path.join(OUT, "_tmp.html"))
