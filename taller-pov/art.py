"""Arte del Ep.1 del taller de tuning: fondos y personajes 2D (SVG -> PNG a 2x con Chromium).
Mismo estilo cartoon acogedor que la serie del club, pero de noche, con neones y luces de taller."""
import math, os, random, re, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "club-pov"))
from art2 import cel, svg, sky, eye, face, neck, SK, SKS, SKH  # noqa: E402

OUT = os.path.join(HERE, "layers"); os.makedirs(OUT, exist_ok=True)
OL = "#1d1630"
NEON_C = "#3ef0ff"; NEON_M = "#ff4fd8"; AMB = "#ffb347"

def glowtext(x, y, s, size, col, anchor="middle", rot=0, extra=""):
    t = f'font-family="Anton" font-size="{size}" text-anchor="{anchor}"'
    tr = f' transform="rotate({rot} {x} {y})"' if rot else ""
    return (f'<g{tr}><text x="{x}" y="{y}" {t} fill="{col}" filter="url(#blur12)" opacity="0.9">{s}</text>'
            f'<text x="{x}" y="{y}" {t} fill="{col}" filter="url(#blur2)">{s}</text>'
            f'<text x="{x}" y="{y}" {t} fill="#ffffff" fill-opacity="0.85" {extra}>{s}</text></g>')

def bricks(x0, y0, x1, y1, seed, cols, bw=104, bh=46):
    r = random.Random(seed); b = ""
    for row, y in enumerate(range(y0, y1, bh)):
        off = 0 if row % 2 else bw // 2
        for x in range(x0 - off, x1, bw):
            b += f'<rect x="{x+3}" y="{y+3}" width="{bw-6}" height="{bh-6}" rx="3" fill="{r.choice(cols)}"/>'
    return b

# ============================================================ FONDOS
def bg_mesa():
    """Notaría: mesa de madera vista desde arriba, papeles, lámpara cálida."""
    d = sky("wd", [(0, "#6b4128"), (1, "#4a2a18")])
    d += '<radialGradient id="lamp" cx="0.55" cy="0.42" r="0.6"><stop offset="0" stop-color="#ffd89a" stop-opacity="0.55"/><stop offset="1" stop-color="#ffd89a" stop-opacity="0"/></radialGradient>'
    b = '<rect width="1080" height="1920" fill="url(#wd)"/>'
    r = random.Random(3)
    for i in range(60):
        y = r.randint(0, 1920); b += f'<path d="M0 {y} Q540 {y + r.randint(-30, 30)} 1080 {y + r.randint(-20, 20)}" stroke="#3a2010" stroke-opacity="0.25" stroke-width="{r.randint(2,6)}" fill="none"/>'
    for k in range(4):
        x, y = 160 + k * 40, 380 + k * 22
        b += f'<g transform="rotate({-8 + k*5} {x+330} {y+420})"><rect x="{x}" y="{y}" width="660" height="860" fill="#f3ecd9" stroke="{OL}" stroke-width="5"/>'
        for j in range(16): b += f'<rect x="{x+60}" y="{y+90+j*44}" width="{r.randint(320, 540)}" height="10" rx="5" fill="#b9ae96"/>'
        b += '</g>'
    b += f'<text x="520" y="520" font-family="Anton" font-size="54" fill="#5a4a3a" transform="rotate(7 520 520)">ESCRITURA DE HERENCIA</text>'
    b += f'<path d="M400 1180 q60 -40 120 0 t120 0 t110 -20" stroke="#1f2f80" stroke-width="7" fill="none" transform="rotate(7 520 1180)"/>'
    # pluma
    b += f'<g transform="rotate(-35 860 1480)"><rect x="700" y="1460" width="320" height="34" rx="16" fill="#1f1f28" stroke="{OL}" stroke-width="5"/><path d="M1020 1462 L1080 1477 L1020 1494Z" fill="#d6b04a" stroke="{OL}" stroke-width="4"/></g>'
    # taza de café
    b += f'<circle cx="200" cy="1580" r="120" fill="#e9e4da" stroke="{OL}" stroke-width="7"/><circle cx="200" cy="1580" r="88" fill="#4a2a18"/><ellipse cx="180" cy="1560" rx="40" ry="20" fill="#6b4128"/>'
    b += '<rect width="1080" height="1920" fill="url(#lamp)"/>'
    return svg(1080, 1920, b, d)

def bg_noche():
    """Fondo oscuro para rótulos y números, con neón de taller difuminado."""
    d = sky("dk", [(0, "#120f22"), (0.6, "#1a1530"), (1, "#0c0a16")])
    b = '<rect width="1080" height="1920" fill="url(#dk)"/>'
    b += f'<ellipse cx="160" cy="300" rx="380" ry="260" fill="{NEON_M}" opacity="0.16" filter="url(#blur40)"/>'
    b += f'<ellipse cx="940" cy="1500" rx="420" ry="300" fill="{NEON_C}" opacity="0.13" filter="url(#blur40)"/>'
    for y in range(0, 1920, 8): b += f'<rect x="0" y="{y}" width="1080" height="2" fill="#000" opacity="0.18"/>'
    # rejilla de suelo de taller en perspectiva
    for i in range(-10, 21):
        b += f'<line x1="{540 + i*30}" y1="1300" x2="{540 + i*150}" y2="1920" stroke="{NEON_C}" stroke-opacity="0.07" stroke-width="3"/>'
    for k in range(8):
        y = 1300 + (k ** 1.6) * 30
        b += f'<line x1="0" y1="{y}" x2="1080" y2="{y}" stroke="{NEON_C}" stroke-opacity="0.07" stroke-width="3"/>'
    return svg(1080, 1920, b, d)

def fachada_base(lit=False):
    d = sky("sk", [(0, "#0d0b22"), (0.5, "#1e1840"), (1, "#3a2450")])
    d += sky("as", [(0, "#2a2832"), (1, "#16151c")])
    b = '<rect width="1080" height="1920" fill="url(#sk)"/>'
    r = random.Random(11)
    for _ in range(70):
        b += f'<circle cx="{r.randint(0,1080)}" cy="{r.randint(0,500)}" r="{r.choice([1.5,2,2.5])}" fill="#fff" opacity="{r.uniform(.3,.9):.2f}"/>'
    b += '<circle cx="860" cy="200" r="70" fill="#f4ecd0" opacity="0.9"/><circle cx="885" cy="185" r="70" fill="#1e1840"/>'
    # edificios de fondo
    for i in range(9):
        x = i * 130 - 20; h = r.randint(260, 460)
        b += f'<rect x="{x}" y="{620-h}" width="128" height="{h}" fill="#1b1830"/>'
        for wy in range(620 - h + 30, 600, 56):
            for wx in (x + 22, x + 74):
                if r.random() < .35: b += f'<rect x="{wx}" y="{wy}" width="30" height="34" fill="#ffcf7a" opacity="0.7"/>'
    # nave del taller (ladrillo)
    b += f'<rect x="0" y="560" width="1080" height="840" fill="#5a2f2a" stroke="{OL}" stroke-width="6"/>'
    b += bricks(0, 565, 1080, 1400, 4, ["#6a3a32", "#5e332c", "#743f35", "#53302a"])
    b += '<rect x="0" y="560" width="1080" height="840" fill="#120c22" opacity="0.38"/>'
    # cartel con letras de neón (apagadas salvo dos)
    b += f'<rect x="120" y="610" width="840" height="170" rx="16" fill="#151220" stroke="{OL}" stroke-width="8"/>'
    sign = "TALLER RUBÉN"
    xs = [170 + i * 62 for i in range(len(sign))]
    for i, (ch, x) in enumerate(zip(sign, xs)):
        if ch == " ": continue
        on = lit or i in (0, 7)
        if on: b += glowtext(x + 30, 735, ch, 120, NEON_M)
        else: b += f'<text x="{x+30}" y="735" font-family="Anton" font-size="120" text-anchor="middle" fill="#3a2a40" stroke="#5a4a66" stroke-width="2">{ch}</text>'
    b += f'<text x="540" y="770" font-family="Anton" font-size="30" text-anchor="middle" fill="#8a7a9a" letter-spacing="8">TUNING · MECÁNICA · DESDE 1996</text>'
    # marco de la persiana
    b += f'<rect x="150" y="830" width="780" height="570" fill="#0c0a12" stroke="{OL}" stroke-width="10"/>'
    # grafitis en el muro
    b += f'<text x="30" y="1100" font-family="Anton" font-size="70" fill="{NEON_C}" opacity="0.55" transform="rotate(-8 30 1100)">R96</text>'
    b += f'<text x="950" y="1250" font-family="Anton" font-size="56" fill="#ffd34a" opacity="0.5" transform="rotate(6 950 1250)">NITRO</text>'
    b += f'<path d="M960 1180 l40 -10" stroke="#ff4f4f" stroke-width="8" opacity="0.6"/>'
    # farola
    b += f'<rect x="1010" y="380" width="18" height="1020" fill="#22222a" stroke="{OL}" stroke-width="4"/><path d="M960 380 L1050 380 L1035 345 L975 345Z" fill="#22222a" stroke="{OL}" stroke-width="4"/>'
    b += '<ellipse cx="1005" cy="392" rx="34" ry="10" fill="#ffe7a0"/><circle cx="1005" cy="420" r="150" fill="#ffe7a0" opacity="0.16" filter="url(#blur12)"/>'
    # acera y asfalto mojado con reflejos
    b += '<rect x="0" y="1400" width="1080" height="70" fill="#5a5862"/><rect x="0" y="1400" width="1080" height="9" fill="#7a7882"/>'
    b += '<rect x="0" y="1470" width="1080" height="450" fill="url(#as)"/>'
    b += f'<ellipse cx="540" cy="1560" rx="420" ry="40" fill="{NEON_M}" opacity="0.12" filter="url(#blur12)"/>'
    b += '<ellipse cx="1000" cy="1520" rx="140" ry="26" fill="#ffe7a0" opacity="0.13" filter="url(#blur12)"/>'
    for x in range(30, 1080, 280): b += f'<rect x="{x}" y="1760" width="160" height="16" fill="#e8e0c0" opacity="0.4"/>'
    for _ in range(14):
        x = r.randint(0, 1080); y = r.randint(1500, 1900)
        b += f'<ellipse cx="{x}" cy="{y}" rx="{r.randint(30,90)}" ry="{r.randint(5,10)}" fill="#8a8aa8" opacity="0.12"/>'
    return svg(1080, 1920, b, d)

def bg_fachada(): return fachada_base(False)

def persiana():
    """Persiana metálica oxidada (encaja en el marco 150..930 x 830..1400)."""
    b = ''
    for k, y in enumerate(range(0, 570, 30)):
        b += f'<rect x="0" y="{y}" width="780" height="30" fill="#7c7f88"/><rect x="0" y="{y}" width="780" height="9" fill="#a3a6ae"/><rect x="0" y="{y+24}" width="780" height="6" fill="#4e505a"/>'
    r = random.Random(9)
    for _ in range(26):
        x, y = r.randint(0, 760), r.randint(0, 560)
        b += f'<ellipse cx="{x}" cy="{y}" rx="{r.randint(16,60)}" ry="{r.randint(8,26)}" fill="#8a4a24" opacity="{r.uniform(.35,.7):.2f}"/>'
    b += '<path d="M60 560 Q200 520 300 560" stroke="#6a3a1c" stroke-width="14" opacity="0.5" fill="none"/>'
    b += f'<text x="390" y="250" font-family="Anton" font-size="96" text-anchor="middle" fill="#1d1d26" opacity="0.65" transform="rotate(-4 390 250)">SE VENDE?</text>'
    b += f'<text x="230" y="420" font-family="Anton" font-size="60" fill="{NEON_C}" opacity="0.5" transform="rotate(5 230 420)">R.I.P. 96</text>'
    b += f'<rect x="0" y="540" width="780" height="30" fill="#3a3c44" stroke="{OL}" stroke-width="5"/><rect x="360" y="545" width="60" height="18" rx="6" fill="#c9a24a" stroke="{OL}" stroke-width="3"/>'
    b += f'<rect x="0" y="0" width="780" height="570" fill="none" stroke="{OL}" stroke-width="6"/>'
    return svg(780, 570, b)

def aviso():
    b = '<g filter="url(#drop)">'
    b += f'<rect x="20" y="20" width="520" height="680" fill="#f6f1e2" stroke="{OL}" stroke-width="6"/></g>'
    b += f'<rect x="20" y="20" width="520" height="120" fill="#c62f2f"/>'
    b += '<text x="280" y="105" font-family="Anton" font-size="72" text-anchor="middle" fill="#fff">AVISO</text>'
    b += '<text x="280" y="210" font-family="Anton" font-size="54" text-anchor="middle" fill="#2a2a34">DE DESAHUCIO</text>'
    r = random.Random(2)
    for j in range(8): b += f'<rect x="70" y="{260+j*40}" width="{r.randint(260, 420)}" height="12" rx="6" fill="#b5ab98"/>'
    b += '<text x="280" y="640" font-family="Anton" font-size="40" text-anchor="middle" fill="#c62f2f">BANCO DEL VALLE</text>'
    b += f'<rect x="250" y="0" width="70" height="44" fill="#e8d98a" opacity="0.85" transform="rotate(-6 285 22)"/>'
    return svg(560, 720, b)

def bg_taller():
    """Interior del taller abandonado: luz por la puerta, coches desmontados, herramientas, neón roto."""
    d = sky("wl", [(0, "#232038"), (1, "#15131f")])
    d += sky("fl", [(0, "#3a3644"), (1, "#1c1a24")])
    d += '<radialGradient id="beam" cx="0.5" cy="0" r="1"><stop offset="0" stop-color="#ffd99a" stop-opacity="0.45"/><stop offset="1" stop-color="#ffd99a" stop-opacity="0"/></radialGradient>'
    b = '<rect width="1080" height="1920" fill="url(#wl)"/>'
    # pared de bloques
    for row, y in enumerate(range(0, 1150, 70)):
        off = 0 if row % 2 else 70
        for x in range(-off, 1080, 140):
            b += f'<rect x="{x+3}" y="{y+3}" width="134" height="64" rx="4" fill="#2c2840" opacity="0.9"/>'
    # ventanas altas sucias
    for x in (90, 420, 750):
        b += f'<rect x="{x}" y="90" width="240" height="140" fill="#3a5070" stroke="{OL}" stroke-width="8"/>'
        b += f'<path d="M{x+120} 90 L{x+120} 230 M{x} 160 L{x+240} 160" stroke="{OL}" stroke-width="6"/>'
        b += f'<rect x="{x}" y="90" width="240" height="140" fill="#6a6a5a" opacity="0.35"/>'
    b += '<path d="M480 120 l30 25 l-12 30" stroke="#1a2230" stroke-width="4" fill="none"/>'
    # pósters de coches y calendario
    b += f'<g transform="rotate(-4 200 480)"><rect x="80" y="330" width="250" height="320" fill="#e8dcc0" stroke="{OL}" stroke-width="5"/>'
    b += f'<rect x="96" y="346" width="218" height="190" fill="#24324a"/><path d="M110 500 Q150 440 220 440 L300 470 L300 510 L110 510Z" fill="{NEON_M}"/>'
    b += f'<circle cx="150" cy="512" r="20" fill="#111"/><circle cx="270" cy="512" r="20" fill="#111"/>'
    b += '<text x="205" y="600" font-family="Anton" font-size="44" text-anchor="middle" fill="#2a1a1a">DRIFT 98</text></g>'
    b += f'<g transform="rotate(3 900 470)"><rect x="800" y="340" width="200" height="260" fill="#f2efe8" stroke="{OL}" stroke-width="5"/><rect x="800" y="340" width="200" height="60" fill="#c62f2f"/>'
    b += '<text x="900" y="385" font-family="Anton" font-size="38" text-anchor="middle" fill="#fff">2024</text>'
    for i in range(5):
        for j in range(4): b += f'<rect x="{815+i*36}" y="{420+j*40}" width="28" height="30" fill="#d9d2c2"/>'
    b += '</g>'
    # neón roto "RUBÉN MOTOR" (sólo una parte encendida)
    b += f'<rect x="350" y="300" width="400" height="120" rx="14" fill="#141220" stroke="{OL}" stroke-width="6"/>'
    word = "RUBÉN MOTOR"
    for i, ch in enumerate(word):
        x = 382 + i * 34
        if ch == " ": continue
        if i in (0, 6, 7, 9): b += glowtext(x, 386, ch, 64, NEON_C)
        else: b += f'<text x="{x}" y="386" font-family="Anton" font-size="64" text-anchor="middle" fill="#2a3442" stroke="#4a5a6a" stroke-width="2">{ch}</text>'
    b += f'<path d="M700 420 L720 470 L705 520" stroke="#2a2a33" stroke-width="5" fill="none"/>'
    # panel de herramientas
    b += f'<rect x="60" y="700" width="420" height="300" fill="#5a4a3a" stroke="{OL}" stroke-width="6"/>'
    for i in range(12):
        x = 90 + (i % 6) * 65; y = 730 + (i // 6) * 130
        b += f'<circle cx="{x+20}" cy="{y}" r="5" fill="#2a2018"/>'
        if i in (2, 5, 9): b += f'<path d="M{x} {y+10} l40 0 l0 90 l-40 0Z" fill="none" stroke="#2a2018" stroke-width="3" stroke-dasharray="6 5"/>'
        else: b += f'<rect x="{x+12}" y="{y+10}" width="16" height="{70 + (i*13)%30}" rx="5" fill="#9aa0ac" stroke="{OL}" stroke-width="3"/>'
    # estanterías con neumáticos
    b += f'<rect x="620" y="680" width="420" height="20" fill="#3a3646" stroke="{OL}" stroke-width="4"/><rect x="620" y="860" width="420" height="20" fill="#3a3646" stroke="{OL}" stroke-width="4"/>'
    for k in range(4):
        b += f'<ellipse cx="{680+k*100}" cy="{620}" rx="46" ry="58" fill="#1a1a20" stroke="{OL}" stroke-width="5"/><ellipse cx="{680+k*100}" cy="620" rx="20" ry="26" fill="#2c2c34"/>'
    for k in range(5): b += f'<rect x="{640+k*78}" y="{790-k%2*20}" width="56" height="{70+k%2*20}" rx="6" fill="{["#c62f2f","#2f6ac6","#e8b02f","#2fa463","#9a9aa8"][k]}" stroke="{OL}" stroke-width="4"/>'
    # suelo con manchas de aceite y líneas amarillas
    b += '<rect x="0" y="1150" width="1080" height="770" fill="url(#fl)"/>'
    b += '<path d="M0 1150 L1080 1150" stroke="#0e0c14" stroke-width="8"/>'
    b += '<path d="M120 1920 L340 1150 M960 1920 L740 1150" stroke="#e8b02f" stroke-width="14" opacity="0.55" stroke-dasharray="60 40"/>'
    r = random.Random(17)
    for _ in range(9):
        x, y = r.randint(80, 1000), r.randint(1250, 1880)
        b += f'<ellipse cx="{x}" cy="{y}" rx="{r.randint(40,120)}" ry="{r.randint(14,34)}" fill="#0c0a10" opacity="0.55"/>'
        b += f'<ellipse cx="{x-10}" cy="{y-4}" rx="{r.randint(10,30)}" ry="5" fill="{NEON_M}" opacity="0.18"/>'
    # coche a medio desmontar (fondo derecha) sobre borriquetas
    b += f'<g opacity="0.95"><path d="M600 1080 Q620 990 720 980 L790 920 Q820 900 880 900 L980 905 Q1040 910 1070 980 L1080 1080Z" fill="#3c4a5a" stroke="{OL}" stroke-width="6"/>'
    b += f'<path d="M800 930 L860 920 L940 920 L960 975 L780 975Z" fill="#1e2632"/><rect x="640" y="1080" width="40" height="70" fill="#7a6a5a" stroke="{OL}" stroke-width="4"/><rect x="980" y="1080" width="40" height="70" fill="#7a6a5a" stroke="{OL}" stroke-width="4"/></g>'
    # haz de luz entrando
    b += '<path d="M380 0 L700 0 L1080 1920 L0 1920Z" fill="url(#beam)" opacity="0.55"/>'
    # cadena colgando
    b += f'<path d="M540 0 L540 160" stroke="#6a6a78" stroke-width="6" stroke-dasharray="10 6"/><path d="M520 160 q20 30 40 0" stroke="#6a6a78" stroke-width="8" fill="none"/>'
    return svg(1080, 1920, b, d)

def motor():
    """Bloque de motor abierto en el suelo (el gato asoma por la boca)."""
    b = '<ellipse cx="300" cy="470" rx="290" ry="30" fill="#000" opacity="0.45"/>'
    b += cel('<path d="M40 200 L560 200 L540 460 L60 460Z"/>', "#7a8090", "#555a68", "#9aa0ae", -24, -8, 8)
    for i in range(4):
        x = 110 + i * 120
        b += f'<ellipse cx="{x}" cy="200" rx="46" ry="22" fill="#14121c" stroke="{OL}" stroke-width="6"/>'
    b += cel('<path d="M20 120 L580 120 L560 200 L40 200Z"/>', "#9a3a2a", "#6a2a1e", None, -12, -4, 7)
    b += '<text x="300" y="180" font-family="Anton" font-size="50" text-anchor="middle" fill="#f2c94c" opacity="0.8">TWIN CAM</text>'
    b += f'<path d="M560 260 Q640 270 640 360" stroke="#2a2a33" stroke-width="18" fill="none"/>'
    b += f'<path d="M40 300 Q-20 320 -10 420" stroke="#2a2a33" stroke-width="14" fill="none"/>'
    for (x, y) in ((140, 300), (300, 330), (460, 300)): b += f'<circle cx="{x}" cy="{y}" r="16" fill="#3a3a44" stroke="{OL}" stroke-width="4"/>'
    b += '<path d="M60 420 L540 420" stroke="#3a3a44" stroke-width="6"/>'
    return svg(620, 500, b)

def gato():
    b = ''
    body = '<path d="M60 360 Q40 200 150 170 Q270 150 300 260 Q320 340 300 380 Z"/>'
    b += cel(body, "#1c1a26", "#0f0e16", "#34303f", -18, -8, 7)
    b += cel('<path d="M70 150 L95 50 L140 120 Q180 104 220 120 L270 50 L285 150 Q300 250 180 262 Q60 252 70 150Z"/>', "#1c1a26", "#0f0e16", "#34303f", -14, -8, 7)
    b += '<path d="M105 70 L130 118 L102 118Z M262 70 L236 118 L264 118Z" fill="#e38a9a" opacity="0.7"/>'
    for ex in (135, 230):
        b += f'<ellipse cx="{ex}" cy="180" rx="30" ry="34" fill="#c9f24a" filter="url(#blur12)" opacity="0.6"/>'
        b += f'<ellipse cx="{ex}" cy="180" rx="24" ry="28" fill="#d8ff5a" stroke="{OL}" stroke-width="4"/><ellipse cx="{ex}" cy="182" rx="6" ry="22" fill="{OL}"/><circle cx="{ex+8}" cy="170" r="6" fill="#fff"/>'
    b += '<path d="M172 214 L188 214 L180 226Z" fill="#e38a9a"/><path d="M180 226 Q166 240 156 232 M180 226 Q194 240 204 232" stroke="#8a8aa0" stroke-width="4" fill="none"/>'
    for s in (-1, 1):
        for k in range(3): b += f'<path d="M{180+s*40} {222+k*8} L{180+s*120} {206+k*16}" stroke="#bfbfd0" stroke-width="3"/>'
    b += f'<path d="M290 340 Q380 300 360 200 Q350 170 330 190" stroke="#1c1a26" stroke-width="30" fill="none" stroke-linecap="round"/>'
    return svg(400, 400, b)

def manolo():
    """Mecánico veterano, 60 y tantos: mono azul con grasa, gorra, bigote canoso, trapo al hombro."""
    b = ''
    torso = '<path d="M112 1400 L120 1000 Q118 700 270 640 Q400 600 530 640 Q682 700 680 1000 L688 1400Z"/>'
    b += cel(torso, "#2e4a72", "#1f3452", "#43648f", -60, -10, 8)
    # manchas de grasa
    r = random.Random(4)
    for _ in range(12):
        b += f'<ellipse cx="{r.randint(170,630)}" cy="{r.randint(760,1350)}" rx="{r.randint(14,40)}" ry="{r.randint(8,20)}" fill="#14121a" opacity="0.35"/>'
    # cremallera y bolsillos
    b += '<path d="M400 660 L400 1400" stroke="#1a2a40" stroke-width="10"/><rect x="390" y="690" width="20" height="34" rx="5" fill="#c9cfd9" stroke="#1d1630" stroke-width="3"/>'
    b += cel('<rect x="200" y="800" width="130" height="110" rx="10"/>', "#2a4468", "#1c304c", None, -8, 0, 5)
    b += cel('<rect x="470" y="800" width="130" height="110" rx="10"/>', "#2a4468", "#1c304c", None, -8, 0, 5)
    b += '<rect x="500" y="760" width="12" height="60" rx="4" fill="#e8b02f" stroke="#1d1630" stroke-width="3"/><rect x="520" y="770" width="10" height="50" rx="4" fill="#c62f2f" stroke="#1d1630" stroke-width="3"/>'
    # parche con nombre
    b += '<ellipse cx="265" cy="745" rx="70" ry="30" fill="#f2efe8" stroke="#1d1630" stroke-width="4"/><text x="265" y="758" font-family="Anton" font-size="34" text-anchor="middle" fill="#c62f2f">MANOLO</text>'
    # cuello de camiseta
    b += cel('<path d="M318 628 L400 700 L482 628 L470 600 L400 650 L330 600Z"/>', "#e9e4d8", "#c9c2b2", None, -10, 0, 6)
    # trapo al hombro
    b += cel('<path d="M470 615 Q600 600 650 690 L610 880 L558 865 L590 730 Q545 676 470 662Z"/>', "#c62f2f", "#8f2020", None, -20, -6, 6)
    b += '<path d="M570 840 L612 852 M575 815 L618 827" stroke="#f2efe8" stroke-width="6"/>'
    # llave inglesa en la mano
    b += cel('<ellipse cx="222" cy="1060" rx="46" ry="38"/>', SK, SKS, None, 10, -6, 6)
    b += f'<g transform="rotate(-30 222 1060)"><rect x="210" y="900" width="26" height="200" rx="10" fill="#b8bec8" stroke="{OL}" stroke-width="5"/><path d="M196 880 Q223 840 250 880 L240 905 L206 905Z" fill="#b8bec8" stroke="{OL}" stroke-width="5"/></g>'
    for k in range(3): b += f'<path d="M{200+k*16} 1040 L{200+k*16} 1068" stroke="{SKS}" stroke-width="4"/>'
    # cabeza
    b += '<g transform="translate(0,120)">'
    b += neck(352, 410, 96, 110)
    b += face(400, 330)
    b += cel('<path d="M286 320 Q266 250 296 210 L318 332Z"/>', "#e6e6e6", "#b9b9c2", None, 8, 0, 5)
    b += cel('<path d="M514 320 Q534 250 504 210 L482 332Z"/>', "#e6e6e6", "#b9b9c2", None, -8, 0, 5)
    # gorra de taller
    b += cel('<path d="M266 246 Q272 140 404 128 Q540 134 548 244 Q404 220 266 246Z"/>', "#c62f2f", "#8f2020", "#e04848", -26, -10, 7)
    b += cel('<path d="M262 244 Q404 214 552 240 L640 262 Q600 282 548 268 Q404 246 252 272Z"/>', "#a82424", "#701818", None, -10, 0, 6)
    b += '<rect x="372" y="168" width="64" height="40" rx="8" fill="#f2efe8" stroke="#1d1630" stroke-width="4"/><text x="404" y="200" font-family="Anton" font-size="30" text-anchor="middle" fill="#1d1630">R</text>'
    # cejas, ojos cansados
    b += '<path d="M316 272 Q350 256 384 270" stroke="#ececec" stroke-width="15" fill="none" stroke-linecap="round"/><path d="M416 270 Q450 256 484 272" stroke="#ececec" stroke-width="15" fill="none" stroke-linecap="round"/>'
    b += eye(350, 318, 11) + eye(450, 318, 11)
    b += '<path d="M326 306 Q350 296 374 306" stroke="#1d1630" stroke-width="5" fill="#f3c29b"/><path d="M426 306 Q450 296 474 306" stroke="#1d1630" stroke-width="5" fill="#f3c29b"/>'
    b += '<path d="M318 344 Q350 356 382 344 M418 344 Q450 356 482 344" stroke="#c98a62" stroke-width="4" fill="none"/>'
    b += cel('<path d="M392 330 Q434 372 412 398 Q392 406 376 392 Q374 360 392 330Z"/>', SK, SKS, None, -8, -4, 5)
    b += '<ellipse cx="318" cy="388" rx="26" ry="16" fill="#e7887a" opacity="0.45"/><ellipse cx="486" cy="388" rx="26" ry="16" fill="#e7887a" opacity="0.45"/>'
    # mancha de grasa en la mejilla
    b += '<ellipse cx="470" cy="410" rx="22" ry="10" fill="#2a2420" opacity="0.4" transform="rotate(-20 470 410)"/>'
    # bigote grande canoso
    b += cel('<path d="M306 422 Q348 380 400 406 Q452 380 494 422 Q460 448 400 428 Q340 448 306 422Z"/>', "#efefef", "#c4c4cc", None, -10, -4, 5)
    b += '<path d="M372 456 Q400 466 428 456" stroke="#1d1630" stroke-width="6" fill="none" stroke-linecap="round"/>'
    b += '<path d="M286 362 Q298 384 294 402 M514 362 Q502 384 506 402" stroke="#c98a62" stroke-width="5" fill="none" opacity="0.8"/>'
    b += '</g>'
    return svg(800, 1400, b)

def lona():
    """Coche cubierto por una lona polvorienta."""
    b = '<ellipse cx="540" cy="520" rx="520" ry="34" fill="#000" opacity="0.5"/>'
    shape = '<path d="M30 500 Q40 360 170 330 Q260 230 400 210 Q560 196 700 214 Q850 240 930 330 Q1050 360 1050 500 Q980 520 900 492 Q800 520 700 494 Q600 522 500 494 Q400 522 300 496 Q200 520 120 494 Q70 516 30 500Z"/>'
    b += cel(shape, "#6e6a5e", "#4a463e", "#8e897a", -40, -20, 8)
    for x in (230, 400, 560, 720, 880):
        b += f'<path d="M{x} {300 - (x-540)**2/1600} Q{x+30} 400 {x-10} 490" stroke="#3e3a32" stroke-width="7" fill="none" opacity="0.6"/>'
    r = random.Random(6)
    for _ in range(40):
        b += f'<circle cx="{r.randint(80,1000)}" cy="{r.randint(240,480)}" r="{r.randint(3,9)}" fill="#a39d8a" opacity="0.5"/>'
    b += f'<rect x="420" y="330" width="240" height="70" rx="6" fill="#f2efe8" stroke="{OL}" stroke-width="4" transform="rotate(-4 540 365)"/>'
    b += '<text x="540" y="380" font-family="Caveat" font-weight="700" font-size="54" text-anchor="middle" fill="#c62f2f" transform="rotate(-4 540 365)">NO TOCAR</text>'
    return svg(1080, 560, b)

def deportivo():
    """Deportivo japonés de los 90 a medio restaurar: capó abierto, paneles en imprimación, sin marca."""
    b = '<ellipse cx="540" cy="520" rx="520" ry="34" fill="#000" opacity="0.5"/>'
    body = '<path d="M40 420 Q46 350 150 330 L300 240 Q350 210 430 206 L690 206 Q770 210 830 262 L930 330 Q1040 346 1046 420 L1046 470 L40 470Z"/>'
    b += cel(body, "#e8eef4", "#b6c0cc", "#ffffff", -22, -18, 8)
    # paneles en imprimación gris y óxido
    b += '<path d="M600 300 L830 300 L930 340 L930 450 L600 450Z" fill="#8c9098" opacity="0.92"/>'
    b += '<path d="M150 380 Q200 360 240 400 L220 450 L140 450Z" fill="#9a5a2a" opacity="0.55"/>'
    # franja lateral
    b += f'<path d="M60 400 L1030 400 L1030 420 L60 420Z" fill="{NEON_M}"/>'
    # ventanas
    b += '<path d="M320 250 L430 226 L560 226 L560 326 L250 326Z" fill="#26324a"/><path d="M590 226 L690 226 Q760 232 800 322 L590 326Z" fill="#26324a"/>'
    b += '<path d="M350 244 L392 236 L322 320 L292 320Z" fill="#fff" opacity="0.25"/>'
    # alerón
    b += f'<path d="M930 290 L1060 270 L1064 292 L940 312Z" fill="#1c1c24" stroke="{OL}" stroke-width="5"/><rect x="960" y="300" width="14" height="40" fill="#1c1c24"/><rect x="1030" y="292" width="14" height="44" fill="#1c1c24"/>'
    # capó abierto delante
    b += cel('<path d="M70 330 L300 250 L250 120 L40 230Z"/>', "#e8eef4", "#b6c0cc", None, -10, -6, 7)
    # faros escamoteables cerrados
    b += f'<rect x="80" y="360" width="90" height="20" rx="6" fill="#2a2a34" stroke="{OL}" stroke-width="4"/>'
    b += f'<rect x="1000" y="370" width="40" height="26" rx="6" fill="#d43a3a" stroke="{OL}" stroke-width="4"/>'
    # matrícula tapada con cinta
    b += f'<rect x="980" y="430" width="70" height="34" fill="#f2efe8" stroke="{OL}" stroke-width="3"/><rect x="972" y="438" width="86" height="18" fill="#9a9aa8" transform="rotate(-8 1015 447)"/>'
    b += f'<rect x="56" y="440" width="980" height="22" rx="10" fill="#2a2b36"/>'
    for x in (240, 830):
        b += f'<circle cx="{x}" cy="470" r="86" fill="#0b0b10" stroke="{OL}" stroke-width="8"/><circle cx="{x}" cy="470" r="52" fill="#d4b04a" stroke="{OL}" stroke-width="5"/>'
        for k in range(6):
            a = k * math.pi / 3
            b += f'<line x1="{x}" y1="470" x2="{x+46*math.cos(a):.1f}" y2="{470+46*math.sin(a):.1f}" stroke="#8a6a20" stroke-width="9"/>'
        b += f'<circle cx="{x}" cy="470" r="12" fill="#2a2b36"/>'
    return svg(1080, 580, b)

def movil():
    """Móvil viejo con una nota de voz en pantalla."""
    b = '<g filter="url(#drop)">'
    b += cel('<rect x="20" y="20" width="420" height="820" rx="56"/>', "#2a2a34", "#1a1a22", "#44444f", -12, -8, 8)
    b += '</g>'
    b += '<rect x="48" y="90" width="364" height="680" rx="18" fill="#101a2a"/>'
    b += '<path d="M48 330 L412 160 M48 520 L412 300" stroke="#ffffff" stroke-opacity="0.18" stroke-width="5"/>'  # pantalla rajada
    b += '<rect x="48" y="90" width="364" height="70" fill="#1d6a5a"/><circle cx="96" cy="125" r="22" fill="#9aa0ac"/><text x="134" y="136" font-family="Anton" font-size="34" fill="#fff">RUBÉN</text>'
    b += '<rect x="80" y="420" width="300" height="110" rx="26" fill="#2a8a6a"/>'
    b += '<circle cx="124" cy="475" r="28" fill="#fff"/><path d="M116 460 L138 475 L116 490Z" fill="#2a8a6a"/>'
    for i in range(18):
        h = [10, 26, 40, 18, 34, 48, 22, 14, 38, 30, 44, 16, 28, 36, 20, 12, 30, 18][i]
        b += f'<rect x="{166+i*11}" y="{475-h/2}" width="6" height="{h}" rx="3" fill="#d8f5ea"/>'
    b += '<text x="360" y="520" font-family="Anton" font-size="24" text-anchor="end" fill="#d8f5ea">0:11</text>'
    b += '<text x="230" y="600" font-family="Anton" font-size="28" text-anchor="middle" fill="#7a8a9a">hace 2 años</text>'
    b += '<circle cx="230" cy="806" r="18" fill="none" stroke="#5a5a66" stroke-width="5"/>'
    return svg(460, 860, b)

def coche_negro():
    """Coche negro bajo y tuneado del rival, con faros encendidos."""
    b = '<ellipse cx="540" cy="512" rx="500" ry="28" fill="#000" opacity="0.5"/>'
    body = '<path d="M40 400 Q50 330 170 316 L310 236 Q352 210 430 208 L700 208 Q780 212 830 262 L920 316 Q1030 330 1040 400 L1040 452 L40 452Z"/>'
    b += cel(body, "#18181f", "#0b0b10", "#34343f", -20, -18, 8)
    b += '<path d="M330 248 L430 226 L560 226 L560 310 L256 310Z" fill="#0e1420"/><path d="M590 226 L692 226 Q764 232 806 306 L590 310Z" fill="#0e1420"/>'
    b += f'<path d="M120 350 Q540 320 990 350" stroke="{NEON_C}" stroke-opacity="0.35" stroke-width="5" fill="none"/>'
    # neón de bajos
    b += f'<ellipse cx="540" cy="478" rx="460" ry="22" fill="{NEON_C}" opacity="0.55" filter="url(#blur12)"/>'
    b += f'<rect x="56" y="420" width="980" height="22" rx="10" fill="#22222c"/>'
    # faros
    b += '<path d="M48 360 L170 352 L160 384 L52 388Z" fill="#fffbe0" stroke="#1d1630" stroke-width="4"/>'
    b += '<rect x="960" y="352" width="64" height="26" rx="8" fill="#ff3a3a" stroke="#1d1630" stroke-width="4"/>'
    # alerón y escape
    b += f'<path d="M900 280 L1030 262 L1034 284 L910 302Z" fill="#0b0b10" stroke="{OL}" stroke-width="5"/>'
    b += f'<ellipse cx="1030" cy="440" rx="22" ry="14" fill="#5a5a66" stroke="{OL}" stroke-width="4"/>'
    for x in (240, 820):
        b += f'<circle cx="{x}" cy="452" r="84" fill="#0b0b10" stroke="{OL}" stroke-width="8"/><circle cx="{x}" cy="452" r="54" fill="#2c2c36" stroke="{NEON_C}" stroke-width="4"/>'
        for k in range(10):
            a = k * math.pi / 5
            b += f'<line x1="{x}" y1="452" x2="{x+48*math.cos(a):.1f}" y2="{452+48*math.sin(a):.1f}" stroke="#5a5a68" stroke-width="5"/>'
        b += f'<circle cx="{x}" cy="452" r="10" fill="#9aa0aa"/>'
    return svg(1080, 560, b)

def faros():
    """Dos focos de luz cegadores (se superponen al llegar el coche)."""
    b = ''
    for x in (330, 750):
        b += f'<circle cx="{x}" cy="400" r="300" fill="#fff6d0" opacity="0.35" filter="url(#blur40)"/>'
        b += f'<circle cx="{x}" cy="400" r="110" fill="#fffbea" opacity="0.9" filter="url(#blur12)"/>'
        b += f'<circle cx="{x}" cy="400" r="50" fill="#ffffff"/>'
        for k in range(8):
            a = k * math.pi / 4
            b += f'<line x1="{x}" y1="400" x2="{x+360*math.cos(a):.0f}" y2="{400+360*math.sin(a):.0f}" stroke="#fff6d0" stroke-width="10" opacity="0.35" filter="url(#blur2)"/>'
    return svg(1080, 800, b)

def nitro():
    """Iván 'Nitro' Salcedo: ~35, chaqueta de cuero, cadena, pelo degradado con tupé, sonrisa chula."""
    b = ''
    torso = '<path d="M110 1000 Q108 700 260 640 Q400 600 540 640 Q692 700 690 1000Z"/>'
    b += cel(torso, "#1f1d26", "#111017", "#3a3746", -60, -10, 8)
    # camiseta blanca y cadena
    b += cel('<path d="M330 618 L400 820 L470 618 L440 600 L400 650 L360 600Z"/>', "#f4f4f6", "#cfd0d8", None, -8, 0, 5)
    b += '<path d="M352 640 Q400 760 448 640" stroke="#e8c04a" stroke-width="9" fill="none" stroke-dasharray="10 4"/><circle cx="400" cy="752" r="16" fill="#e8c04a" stroke="#1d1630" stroke-width="4"/>'
    # solapas de cuero con brillo
    b += cel('<path d="M290 628 L388 830 L322 880 L240 690Z"/>', "#26232e", "#15131b", "#4a4656", -12, 0, 6)
    b += cel('<path d="M510 628 L412 830 L478 880 L560 690Z"/>', "#26232e", "#15131b", "#4a4656", -12, 0, 6)
    b += '<path d="M180 760 Q200 860 190 980 M620 760 Q600 860 610 980" stroke="#5a566a" stroke-width="6" fill="none" opacity="0.7"/>'
    b += f'<path d="M560 720 L620 740" stroke="#c9cfd9" stroke-width="8"/>'
    # parche en la chaqueta
    b += f'<circle cx="220" cy="760" r="38" fill="#ff4f4f" stroke="{OL}" stroke-width="4"/><text x="220" y="776" font-family="Anton" font-size="42" text-anchor="middle" fill="#fff">N</text>'
    # mano con llaves del coche
    b += cel('<ellipse cx="640" cy="940" rx="48" ry="40"/>', SK, SKS, None, -10, -6, 6)
    b += f'<path d="M640 960 L640 1000" stroke="#9aa0aa" stroke-width="6"/><rect x="622" y="996" width="36" height="52" rx="10" fill="#1c1c24" stroke="{OL}" stroke-width="4"/>'
    # cabeza
    b += '<g transform="translate(0,120)">'
    b += neck(352, 410, 96, 110)
    b += face(400, 330, 116)
    # pelo: laterales rapados (degradado) y tupé arriba
    b += '<path d="M290 250 Q286 200 312 178 L318 300Z M510 250 Q514 200 488 178 L482 300Z" fill="#5a4a40" opacity="0.55"/>'
    b += cel('<path d="M300 236 Q296 150 380 128 Q470 110 520 160 Q536 190 512 236 Q480 200 410 204 Q340 206 300 236Z"/>', "#2a2420", "#1a1512", "#5a4a40", -16, -10, 6)
    b += '<path d="M330 170 Q400 140 480 160 M340 196 Q410 170 490 186" stroke="#5a4a40" stroke-width="5" fill="none"/>'
    # cejas (una con corte) y ojos entrecerrados
    b += '<path d="M310 268 L384 278" stroke="#1d1630" stroke-width="13" stroke-linecap="round"/><path d="M416 278 L452 272 M466 270 L490 266" stroke="#1d1630" stroke-width="13" stroke-linecap="round"/>'
    b += eye(350, 316, 11, 4) + eye(450, 316, 11, 4)
    b += '<path d="M326 302 L376 302 L376 312 L326 312Z M426 302 L476 302 L476 312 L426 312Z" fill="#f3c29b"/><path d="M326 308 L376 304 M426 304 L476 308" stroke="#1d1630" stroke-width="5"/>'
    b += cel('<path d="M392 330 Q430 372 410 396 Q392 404 378 392 Q376 360 392 330Z"/>', SK, SKS, None, -8, -4, 5)
    # barba de tres días
    b += '<path d="M296 380 Q306 470 400 488 Q494 470 504 380 Q476 446 400 452 Q324 446 296 380Z" fill="#3a302a" opacity="0.18"/>'
    # sonrisa ladeada chula
    b += '<path d="M350 430 Q410 452 470 416" stroke="#1d1630" stroke-width="7" fill="none" stroke-linecap="round"/>'
    b += cel('<path d="M418 432 Q450 432 466 420 Q458 440 424 442Z"/>', "#ffffff", "#d9d9e0", None, -4, 0, 3)
    # pendiente
    b += '<circle cx="290" cy="372" r="8" fill="#e8c04a" stroke="#1d1630" stroke-width="3"/>'
    b += '</g>'
    return svg(800, 1050, b)

def llaves():
    """Llaves del taller con llavero de pistón."""
    b = '<g filter="url(#drop)">'
    b += '<circle cx="200" cy="140" r="70" fill="none" stroke="#c9cfd9" stroke-width="14"/>'
    for k, (rot, col) in enumerate(((-20, "#d4b04a"), (15, "#c9cfd9"), (45, "#b88a3a"))):
        b += f'<g transform="rotate({rot} 200 140)"><circle cx="200" cy="230" r="40" fill="{col}" stroke="{OL}" stroke-width="6"/><circle cx="200" cy="230" r="13" fill="#3a2a1a"/>'
        b += f'<rect x="188" y="266" width="24" height="170" fill="{col}" stroke="{OL}" stroke-width="5"/><path d="M212 380 l18 0 l0 14 l-10 0 l0 12 l10 0 l0 14 l-18 0" fill="{col}" stroke="{OL}" stroke-width="4"/></g>'
    # pistón
    b += f'<g transform="rotate(-10 380 120)"><rect x="300" y="60" width="160" height="130" rx="18" fill="#a9b0ba" stroke="{OL}" stroke-width="7"/>'
    for y in (82, 104, 126): b += f'<rect x="300" y="{y}" width="160" height="9" fill="#6a707a"/>'
    b += f'<path d="M340 190 L420 190 L400 290 L360 290Z" fill="#8a909a" stroke="{OL}" stroke-width="6"/><circle cx="380" cy="300" r="26" fill="#8a909a" stroke="{OL}" stroke-width="6"/></g>'
    b += f'<path d="M262 120 L300 110" stroke="#c9cfd9" stroke-width="10"/>'
    b += '</g>'
    return svg(520, 520, b)

def icon_elevador():
    b = f'<rect x="40" y="320" width="320" height="30" fill="#4a4a56" stroke="{OL}" stroke-width="6"/>'
    b += f'<rect x="70" y="80" width="40" height="240" fill="#e8b02f" stroke="{OL}" stroke-width="6"/><rect x="290" y="80" width="40" height="240" fill="#e8b02f" stroke="{OL}" stroke-width="6"/>'
    b += f'<rect x="60" y="180" width="280" height="24" fill="#c62f2f" stroke="{OL}" stroke-width="6"/>'
    b += '<path d="M100 120 L120 150 L90 160" stroke="#1d1630" stroke-width="5" fill="none"/>'
    return svg(400, 380, b)

def icon_caja():
    b = cel('<rect x="40" y="150" width="320" height="180" rx="14"/>', "#c62f2f", "#8f2020", "#e04848", -16, -6, 7)
    b += f'<path d="M130 150 L130 100 L270 100 L270 150" stroke="{OL}" stroke-width="12" fill="none"/>'
    b += f'<rect x="40" y="210" width="320" height="16" fill="{OL}"/><rect x="180" y="200" width="40" height="36" rx="6" fill="#c9cfd9" stroke="{OL}" stroke-width="4"/>'
    b += '<path d="M230 150 L250 110 M260 150 L250 120" stroke="#9aa0aa" stroke-width="10"/>'
    return svg(400, 380, b)

def icon_utilitario():
    b = '<ellipse cx="200" cy="320" rx="180" ry="16" fill="#000" opacity="0.35"/>'
    b += cel('<path d="M30 270 Q36 210 90 200 L140 130 Q160 110 200 110 L280 110 Q320 112 340 150 L360 200 Q380 210 378 270 L378 300 L30 300Z"/>', "#d84a3a", "#a83226", "#f06a5a", -14, -10, 7)
    b += '<path d="M150 140 L196 130 L196 196 L120 196Z" fill="#26324a"/><path d="M212 130 L280 130 Q310 136 330 196 L212 196Z" fill="#26324a"/>'
    for x in (100, 300): b += f'<circle cx="{x}" cy="300" r="44" fill="#0b0b10" stroke="{OL}" stroke-width="6"/><circle cx="{x}" cy="300" r="20" fill="#9aa0aa"/>'
    b += '<path d="M60 240 L110 260 M300 160 L330 230" stroke="#8a4a24" stroke-width="10" opacity="0.6"/>'
    return svg(400, 380, b)

def tio_foto():
    """Polaroid del tío Rubén (unos 50, perilla, chaqueta vaquera)."""
    b = f'<rect x="20" y="20" width="360" height="430" fill="#f6f2e6" stroke="{OL}" stroke-width="6"/><rect x="45" y="45" width="310" height="300" fill="#4a3a5a"/>'
    b += '<g transform="translate(200,240) scale(0.42) translate(-400,-420)">'
    b += cel('<path d="M110 1000 Q108 700 260 640 Q400 600 540 640 Q692 700 690 1000Z"/>', "#4a6a9a", "#33507a", None, -40, -8, 8)
    b += neck(352, 530, 96, 110) + face(400, 450, 118)
    b += cel('<path d="M286 430 Q280 300 400 290 Q520 300 514 430 Q480 360 400 360 Q320 360 286 430Z"/>', "#4a3a30", "#2e241e", None, -14, -6, 7)
    b += eye(352, 446, 12) + eye(448, 446, 12)
    b += '<path d="M318 400 L384 408 M416 408 L482 400" stroke="#1d1630" stroke-width="12" stroke-linecap="round"/>'
    b += cel('<path d="M360 560 Q400 620 440 560 Q420 590 400 592 Q380 590 360 560Z"/>', "#4a3a30", "#2e241e", None, -4, 0, 5)
    b += '<path d="M356 530 Q400 550 444 530" stroke="#1d1630" stroke-width="7" fill="none" stroke-linecap="round"/>'
    b += '</g>'
    b += '<text x="200" y="410" font-family="Caveat" font-weight="700" font-size="48" text-anchor="middle" fill="#2a2a5a">Rubén · 2022</text>'
    return svg(400, 470, b)

LAYERS = {"bg_mesa": bg_mesa, "bg_noche": bg_noche, "bg_fachada": bg_fachada, "persiana": persiana, "aviso": aviso,
          "bg_taller": bg_taller, "motor": motor, "gato": gato, "manolo": manolo, "lona": lona, "deportivo": deportivo,
          "movil": movil, "coche_negro": coche_negro, "faros": faros, "nitro": nitro, "llaves": llaves,
          "icon_elevador": icon_elevador, "icon_caja": icon_caja, "icon_utilitario": icon_utilitario, "tio_foto": tio_foto}

FONT_CSS = ("@font-face{font-family:Anton;src:url(file://%s/fonts/Anton-Regular.ttf)}"
            "@font-face{font-family:Caveat;font-weight:700;src:url(file://%s/fonts/Caveat.ttf)}") % (HERE, HERE)

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
            pg.goto("file://" + hp); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(150)
            pg.screenshot(path=os.path.join(OUT, name + ".png"), omit_background=True)
            pg.close(); print("ok", name, flush=True)
        br.close()
