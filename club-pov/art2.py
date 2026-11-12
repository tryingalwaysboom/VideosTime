"""Arte HD del Ep.1: fondos y personajes con luces, sombras y texturas. SVG -> PNG a 2x con Chromium."""
import os, re, sys, random
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "layers2"); os.makedirs(OUT, exist_ok=True)
OL = "#1d1630"; SK = "#f3c29b"; SKS = "#d8996f"; SKH = "#ffdcbf"
_id = [0]
def uid(p="c"): _id[0] += 1; return f"{p}{_id[0]}"

COMMON_DEFS = '''
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3" result="n"/>
<feColorMatrix type="saturate" values="0"/><feComponentTransfer><feFuncA type="table" tableValues="0 0.07"/></feComponentTransfer><feBlend in2="SourceGraphic" mode="multiply"/></filter>
<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="blur2" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.2"/></filter>
<filter id="blur12" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>
<filter id="blur40" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter>
<filter id="drop" x="-10%" y="-10%" width="130%" height="130%"><feDropShadow dx="0" dy="14" stdDeviation="12" flood-color="#000" flood-opacity="0.35"/></filter>
<filter id="tex" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="4" seed="8"/><feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.16 0"/><feComposite in2="SourceGraphic" operator="in"/></filter>
'''

def svg(w, h, body, defs="", grain=False):
    g = f'<rect width="{w}" height="{h}" fill="#888" filter="url(#grain)" opacity="0.9" style="mix-blend-mode:multiply"/>' if grain else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<defs>{COMMON_DEFS}{defs}</defs>{body}{g}</svg>')

def shaded(shape, fill, shade, light=None, sdx=40, sdy=10, ow=7, extra=""):
    """Forma con sombra interior desplazada (cel-shading) y brillo opcional. shape = elemento SVG sin fill."""
    i = uid()
    s = f'<clipPath id="{i}">{shape}</clipPath>'
    s += shape.replace("/>", f' fill="{fill}"/>', 1)
    s += f'<g clip-path="url(#{i})"><g transform="translate({sdx},{sdy})">{shape.replace("/>", f" fill=\"{shade}\" transform=\"scale(1)\"/>",1)}</g>'
    # truco: sombra = todo el clip pintado de sombra menos la forma desplazada a la izquierda
    s += '</g>'
    return s

def cel(shape, fill, shade, light=None, dx=-38, dy=-12, ow=7, lw=None):
    """Sombra = forma pintada en sombra, encima la forma desplazada (luz) recortada. Contorno al final."""
    i = uid()
    s = f'<clipPath id="{i}">{shape}</clipPath>'
    s += f'<g clip-path="url(#{i})">{_f(shape, shade)}<g transform="translate({dx},{dy})">{_f(shape, fill)}</g>'
    if light:
        s += f'<g transform="translate({dx*2.2},{dy*2.2})" opacity="0.55">{_f(shape, light)}</g>'
        s += f'<g transform="translate({dx*1.4},{dy*1.4})">{_f(shape, fill)}</g>'
    s += '</g>'
    s += _f(shape, "none", OL, ow)
    return s

def _f(shape, fill, stroke=None, sw=0):
    a = f' fill="{fill}"' + (f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"' if stroke else "")
    return re.sub(r"\s*/>$", a + "/>", shape.strip())

# ============================================================ FONDOS
def sky(id_, stops):
    st = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{id_}" x1="0" y1="0" x2="0" y2="1">{st}</linearGradient>'

def cloud(x, y, s, col, op=0.9):
    return (f'<g opacity="{op}" transform="translate({x},{y}) scale({s})"><ellipse cx="0" cy="0" rx="120" ry="40" fill="{col}"/>'
            f'<ellipse cx="-60" cy="-20" rx="70" ry="45" fill="{col}"/><ellipse cx="40" cy="-35" rx="80" ry="55" fill="{col}"/><ellipse cx="110" cy="-5" rx="60" ry="35" fill="{col}"/></g>')

def bg_campo():
    r = random.Random(7)
    # cielo de atardecer apagado, nublado y melancólico
    d = sky("sk", [(0, "#3b3d58"), (0.35, "#7d6476"), (0.6, "#c98a6e"), (0.8, "#dcae86")])
    d += '<radialGradient id="sun" cx="0.68" cy="0.36" r="0.3"><stop offset="0" stop-color="#ffe9c4" stop-opacity="0.9"/><stop offset="0.3" stop-color="#f2b885" stop-opacity="0.45"/><stop offset="1" stop-color="#d99a72" stop-opacity="0"/></radialGradient>'
    d += sky("gr", [(0, "#7b8c46"), (0.4, "#62763a"), (1, "#3d4f22")])
    d += '<linearGradient id="undr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b0a14" stop-opacity="0.6"/><stop offset="1" stop-color="#0b0a14" stop-opacity="0.05"/></linearGradient>'
    d += '<linearGradient id="rust" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7a3e1e" stop-opacity="0.75"/><stop offset="1" stop-color="#7a3e1e" stop-opacity="0"/></linearGradient>'
    d += '<linearGradient id="dirt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a2016" stop-opacity="0.55"/><stop offset="1" stop-color="#2a2016" stop-opacity="0"/></linearGradient>'
    b = '<rect width="1080" height="1920" fill="url(#sk)"/><rect width="1080" height="1920" fill="url(#sun)"/>'
    b += '<circle cx="735" cy="690" r="95" fill="#f7dcb4" opacity="0.85"/>'
    for (x, y, s, c, o) in [(140, 330, 1.6, "#8a7488", .7), (560, 250, 1.9, "#7a6a80", .65), (930, 380, 1.3, "#9a7e8a", .6),
                            (380, 520, 1.1, "#b58c84", .55), (860, 600, .9, "#c49a86", .5), (60, 600, 1.0, "#a88690", .5)]:
        b += cloud(x, y, s, c, o)
    # montañas y pueblo con bruma
    b += '<path d="M0 830 L120 720 L240 790 L380 660 L520 770 L640 700 L800 800 L930 690 L1080 780 L1080 960 L0 960Z" fill="#6e5a6e" opacity="0.6"/>'
    b += '<path d="M0 880 L160 800 L300 860 L470 780 L640 860 L820 790 L1080 870 L1080 980 L0 980Z" fill="#5a4a5c" opacity="0.65"/>'
    for i in range(14):
        x = 20 + i * 78 + r.randint(-10, 10); h = r.randint(40, 90); w = r.randint(50, 70)
        b += f'<rect x="{x}" y="{930-h}" width="{w}" height="{h}" fill="#4f4252" opacity="0.85"/>'
        b += f'<path d="M{x-6} {930-h} L{x+w/2} {930-h-28} L{x+w+6} {930-h}Z" fill="#634a4a" opacity="0.85"/>'
        if r.random() < .35: b += f'<rect x="{x+12}" y="{930-h+14}" width="10" height="12" fill="#f2c27a" opacity="0.8"/>'
    # pájaros
    for (x, y, s) in ((300, 420, 1), (340, 400, .8), (380, 430, .7), (860, 300, .9)):
        b += f'<path d="M{x-12*s} {y} q{6*s} {-8*s} {12*s} 0 q{6*s} {-8*s} {12*s} 0" stroke="#2a2430" stroke-width="3" fill="none"/>'
    # torre de foco: oxidada, focos rotos, uno colgando, nido
    b += f'<path d="M110 440 L150 440 L175 1000 L85 1000Z" fill="#5a4038" stroke="{OL}" stroke-width="6"/>'
    for y in range(480, 980, 60):
        b += f'<path d="M{95+(y-300)*0.02} {y} L168 {y+50}" stroke="#3a2a22" stroke-width="5"/>'
    b += '<path d="M110 440 L120 1000" stroke="#8a4a26" stroke-width="7" opacity="0.6"/><path d="M146 470 L150 700" stroke="#9a5a2a" stroke-width="5" opacity="0.5"/>'
    b += f'<rect x="40" y="360" width="200" height="110" rx="8" fill="#4a3a34" stroke="{OL}" stroke-width="6"/>'
    b += '<rect x="40" y="440" width="200" height="30" fill="url(#rust)"/>'
    for i in range(3):
        for j in range(2):
            cx, cy = 80 + i * 60, 390 + j * 50
            if (i, j) == (2, 1): continue
            b += f'<circle cx="{cx}" cy="{cy}" r="20" fill="#2a2422" stroke="{OL}" stroke-width="4"/>'
            b += f'<path d="M{cx-12} {cy-8} L{cx+2} {cy+3} L{cx-4} {cy+14} M{cx+2} {cy+3} L{cx+14} {cy-4}" stroke="#8a8a96" stroke-width="2.5" fill="none"/>'
    b += f'<line x1="200" y1="440" x2="214" y2="520" stroke="#222" stroke-width="3"/><circle cx="214" cy="536" r="16" fill="#2a2422" stroke="{OL}" stroke-width="4"/>'
    b += '<path d="M60 360 q30 -26 70 0 q-35 12 -70 0Z" fill="#6a5034"/><path d="M66 356 l10 -8 M90 352 l4 -10 M110 354 l8 -8" stroke="#4a3420" stroke-width="3"/>'
    # ---------- tribuna abandonada
    top, rows, rh = 820, 7, 34
    b += f'<rect x="0" y="790" width="1080" height="{top-790+rows*rh}" fill="#57524c"/>'
    b += '<rect x="0" y="790" width="1080" height="40" fill="#3a3632"/>'
    aisles = (290, 770)
    seats = []
    for k in range(rows):
        y = top + k * rh
        b += f'<rect x="0" y="{y}" width="1080" height="{rh}" fill="#857e74"/>'
        b += f'<rect x="0" y="{y}" width="1080" height="9" fill="#a9a194"/>'
        b += f'<line x1="0" y1="{y+rh}" x2="1080" y2="{y+rh}" stroke="#4e4842" stroke-width="2"/>'
        # verdín en los escalones
        for m in range(r.randint(2, 4)):
            mx = r.randint(0, 1060)
            b += f'<ellipse cx="{mx}" cy="{y+8}" rx="{r.randint(20, 60)}" ry="5" fill="#5f7a32" opacity="0.55"/>'
        col, colsh = (("#4f78a6", "#355a82") if k % 2 == 0 else ("#cfcabd", "#a8a294"))
        x = 14 + (k % 2) * 8
        while x < 1066:
            if any(ax - 8 < x + 22 and x < ax + 52 for ax in aisles):
                x += 34; continue
            rr = r.random()
            if rr < .30:      # arrancado: tornillos y marca
                b += f'<rect x="{x+2}" y="{y+18}" width="18" height="6" rx="2" fill="#4e4842" opacity="0.6"/><circle cx="{x+6}" cy="{y+24}" r="2.5" fill="#2a2420"/><circle cx="{x+16}" cy="{y+24}" r="2.5" fill="#2a2420"/>'
            elif rr < .45:    # roto/inclinado
                ang = r.choice([-35, -22, 18, 30])
                b += f'<g transform="rotate({ang} {x+11} {y+26})"><rect x="{x}" y="{y+5}" width="22" height="19" rx="5" fill="{col}" opacity="0.75" stroke="{OL}" stroke-width="2.5"/></g>'
            elif rr < .50:    # quemado
                b += f'<rect x="{x}" y="{y+5}" width="22" height="19" rx="5" fill="#2a2420" stroke="{OL}" stroke-width="2.5"/><path d="M{x+4} {y+5} q7 -8 14 0" fill="#2a2420" opacity="0.6"/>'
            else:
                fade = r.choice([.95, .8, .7, .6])
                b += f'<rect x="{x}" y="{y+5}" width="22" height="19" rx="5" fill="{col}" opacity="{fade}" stroke="{OL}" stroke-width="2.5"/>'
                b += f'<rect x="{x}" y="{y+20}" width="22" height="6" rx="2" fill="{colsh}" stroke="{OL}" stroke-width="2"/>'
            x += 34
    # pasillos
    for ax in aisles:
        b += f'<rect x="{ax}" y="{top}" width="44" height="{rows*rh}" fill="#9a9286"/>'
        for k in range(rows * 2):
            b += f'<line x1="{ax}" y1="{top+k*rh/2}" x2="{ax+44}" y2="{top+k*rh/2}" stroke="#625b52" stroke-width="3"/>'
        b += f'<path d="M{ax+22} {top} L{ax+22} {top+130} L{ax+34} {top+150}" stroke="#a8a8b0" stroke-width="3" fill="none"/>'  # pasamanos doblado
        b += f'<path d="M{ax+8} {top+60} l12 18 l-6 22" stroke="#4e4842" stroke-width="2" fill="none"/>'  # grieta
    # chorretones de óxido desde el tejado
    for x in (60, 210, 400, 470, 660, 840, 980):
        w = r.randint(10, 26); h = r.randint(90, 230)
        b += f'<rect x="{x}" y="790" width="{w}" height="{h}" fill="url(#rust)" opacity="0.8"/>'
    # hierbajos y arbustos creciendo en la grada
    for _ in range(16):
        wx = r.randint(0, 1060); wy = top + r.randint(0, rows - 1) * rh
        sz = r.uniform(.7, 1.5)
        b += f'<path d="M{wx} {wy+30} q{4*sz} {-30*sz} {10*sz} {-40*sz} q{2*sz} {24*sz} {6*sz} {40*sz} q{6*sz} {-26*sz} {16*sz} {-32*sz} q{-2*sz} {20*sz} {-4*sz} {32*sz}Z" fill="{r.choice(["#5d7d26", "#6e8a2e", "#4a6a1e"])}"/>'
    b += '<path d="M500 1000 q-30 -70 10 -110 q20 40 40 -10 q30 60 -10 120Z" fill="#4f6e22"/>'  # arbusto grande
    # basura en la grada
    for _ in range(9):
        lx = r.randint(20, 1060); ly = top + r.randint(0, rows - 1) * rh + 22
        if r.random() < .5:
            b += f'<rect x="{lx}" y="{ly}" width="10" height="7" rx="2" fill="{r.choice(["#c0392b", "#d9d9d9", "#2e86c1"])}" transform="rotate({r.randint(-60, 60)} {lx} {ly})"/>'
        else:
            b += f'<path d="M{lx} {ly+8} q8 -14 16 -2 q6 -6 10 8Z" fill="#e8e8ee" opacity="0.85"/>'
    b += f'<rect x="0" y="790" width="1080" height="{rows*rh}" fill="url(#undr)"/>'
    # pancarta rasgada colgando
    b += '<path d="M600 830 L860 836 L852 880 L800 872 L790 900 L760 874 L640 880 L630 860Z" fill="#8a2a2a" stroke="#1d1630" stroke-width="4" transform="rotate(2 700 850)"/>'
    b += '<text x="650" y="868" font-family="Anton" font-size="32" fill="#e0d6c4" opacity="0.85" transform="rotate(2 700 850)">SIEMPRE S.L.</text>'
    # muro frontal: grafitis, desconchones, barandilla rota
    fy = top + rows * rh
    b += f'<rect x="0" y="{fy}" width="1080" height="{1095-fy}" fill="#958d82" stroke="{OL}" stroke-width="4"/>'
    for _ in range(6):
        px = r.randint(0, 1040)
        b += f'<path d="M{px} {fy+6} l{r.randint(20,50)} 2 l-6 {r.randint(8,18)} l-{r.randint(20,40)} -2Z" fill="#b8b0a2"/>'
    b += f'<text x="380" y="{fy+28}" font-family="Anton" font-size="30" fill="#2e86c1" opacity="0.75" transform="rotate(-3 380 {fy+20})">ULTRAS SL</text>'
    b += f'<text x="840" y="{fy+30}" font-family="Anton" font-size="28" fill="#c0392b" opacity="0.7">PEPE+MARI</text>'
    b += f'<path d="M80 {fy+10} q20 -10 40 4 q-10 14 -40 -4" fill="none" stroke="#2a2a2a" stroke-width="4" opacity="0.7"/>'
    b += f'<line x1="0" y1="{fy-20}" x2="300" y2="{fy-20}" stroke="#a9adb4" stroke-width="5"/>'
    b += f'<path d="M300 {fy-20} q30 6 46 28" stroke="#a9adb4" stroke-width="5" fill="none"/>'  # barandilla caída
    b += f'<line x1="430" y1="{fy-20}" x2="1080" y2="{fy-20}" stroke="#a9adb4" stroke-width="5"/>'
    for x in range(20, 1080, 60):
        if 320 < x < 430: continue
        b += f'<line x1="{x}" y1="{fy-20}" x2="{x + r.choice([0, 0, 4, -5])}" y2="{fy}" stroke="#a9adb4" stroke-width="4"/>'
    # columnas oxidadas
    for cx in (40, 520, 1000):
        b += f'<rect x="{cx-8}" y="770" width="16" height="{fy-770}" fill="#4a4448" stroke="{OL}" stroke-width="3"/>'
        b += f'<rect x="{cx-8}" y="{fy-80}" width="16" height="80" fill="#7a3e1e" opacity="0.6"/>'
    # tejado: chapas que faltan, una colgando, palomas
    b += f'<path d="M-10 735 L1090 735 L1090 790 L-10 790Z" fill="#3a3e48" stroke="{OL}" stroke-width="6"/>'
    for x in range(0, 1080, 36):
        b += f'<line x1="{x}" y1="738" x2="{x}" y2="788" stroke="#2a2e38" stroke-width="3"/>'
    for (hx, hw) in ((180, 70), (610, 120), (930, 60)):
        b += f'<path d="M{hx} 733 L{hx+hw} 733 L{hx+hw-8} 792 L{hx+8} 792Z" fill="#c99a7a"/><path d="M{hx} 733 L{hx+hw} 733" stroke="#1d1630" stroke-width="6"/>'
        b += f'<path d="M{hx+4} 790 l6 -10 l6 12 l8 -14 l6 12" stroke="#1d1630" stroke-width="3" fill="none"/>'
    b += f'<path d="M620 790 L700 792 L690 880 L640 872Z" fill="#4a4e58" stroke="{OL}" stroke-width="4" transform="translate(-230,0) rotate(14 660 790)"/>'
    for x in range(0, 1080, 90):
        b += f'<rect x="{x+r.randint(0,40)}" y="782" width="{r.randint(14,30)}" height="{r.randint(14,50)}" fill="url(#rust)"/>'
    for px in (90, 130, 760, 800, 1020):
        b += f'<g transform="translate({px},726)"><ellipse cx="0" cy="0" rx="13" ry="9" fill="#5a5a66"/><circle cx="10" cy="-7" r="6" fill="#5a5a66"/><path d="M15 -7 l5 1 l-5 2Z" fill="#c9a24a"/><path d="M-12 0 l-8 4 l8 2Z" fill="#4a4a56"/></g>'
    b += '<rect x="-10" y="782" width="1100" height="10" fill="#2a2e38"/>'
    # vallas publicitarias desvaídas, una caída
    b += f'<rect x="0" y="1095" width="520" height="70" fill="#466a8a" stroke="{OL}" stroke-width="5"/>'
    b += '<text x="40" y="1148" font-family="Anton" font-size="46" fill="#d8d2c4" opacity="0.55">BAR PEPE · DESDE 1974</text>'
    b += '<path d="M330 1100 L420 1100 L440 1160 L360 1160 Q380 1130 330 1100Z" fill="#b8b0a0" opacity="0.8"/>'
    b += f'<rect x="520" y="1095" width="240" height="70" fill="#4e4842" stroke="{OL}" stroke-width="4"/>'
    b += '<path d="M540 1100 l20 30 l-8 30 M700 1098 l-14 26" stroke="#2e2a26" stroke-width="3" fill="none"/>'
    b += f'<path d="M560 1165 L720 1150 L716 1170 L556 1175Z" fill="#7a5a4a" stroke="{OL}" stroke-width="4"/>'  # cartel caído
    b += '<path d="M540 1165 q10 -40 18 -50 q4 30 8 50 M690 1165 q6 -30 14 -36 q0 20 2 36" fill="#5d7d26"/>'
    b += f'<rect x="760" y="1095" width="320" height="70" fill="#8a5a3a" stroke="{OL}" stroke-width="5"/>'
    b += '<text x="790" y="1148" font-family="Anton" font-size="42" fill="#e8dcc4" opacity="0.45">FERRETERÍA LUIS</text>'
    b += '<rect x="760" y="1095" width="320" height="70" fill="url(#rust)" opacity="0.6"/>'
    # cartel de prohibido
    b += f'<rect x="996" y="1010" width="10" height="160" fill="#555" stroke="{OL}" stroke-width="3"/>'
    b += f'<g transform="rotate(-8 980 1010)"><rect x="920" y="980" width="140" height="70" rx="6" fill="#e8e0c8" stroke="{OL}" stroke-width="4"/><text x="990" y="1010" font-family="Anton" font-size="20" text-anchor="middle" fill="#b02a2a">PROHIBIDO</text><text x="990" y="1038" font-family="Anton" font-size="20" text-anchor="middle" fill="#1d1630">EL PASO</text></g>'
    # ---------- césped descuidado
    b += '<rect x="0" y="1165" width="1080" height="755" fill="url(#gr)"/>'
    b += '<rect x="0" y="1165" width="1080" height="60" fill="url(#dirt)"/>'
    # calvas de tierra y zonas secas
    import math as _m
    def blob(cx_, cy_, rx_, ry_, col, op):
        pts = []
        for k in range(14):
            a_ = k / 14 * 2 * _m.pi; f_ = r.uniform(.6, 1.15)
            pts.append(f"{cx_ + rx_ * f_ * _m.cos(a_):.1f},{cy_ + ry_ * f_ * _m.sin(a_):.1f}")
        return f'<polygon points="{" ".join(pts)}" fill="{col}" opacity="{op}" filter="url(#blur2)"/>'
    for _ in range(7):
        cx_, cy_ = r.randint(0, 1080), r.randint(1220, 1880)
        rx_ = r.randint(50, 130) * (0.6 + (cy_ - 1200) / 1000)
        b += blob(cx_, cy_, rx_, rx_ * .22, r.choice(["#7d6a46", "#8a7650"]), .7)
    for _ in range(10):
        cx_, cy_ = r.randint(0, 1080), r.randint(1200, 1880)
        b += blob(cx_, cy_, r.randint(80, 200), r.randint(16, 34), "#a99a58", .3)
    # matojos altos repartidos
    for _ in range(40):
        tx, ty = r.randint(0, 1080), r.randint(1190, 1900)
        s_ = .5 + (ty - 1190) / 700
        c_ = r.choice(["#4a6a1e", "#5d7d26", "#3d5a18", "#6e7a2e"])
        b += f'<path d="M{tx} {ty} q{-6*s_} {-30*s_} {-14*s_} {-44*s_} q{12*s_} {16*s_} {16*s_} {30*s_} q{2*s_} {-30*s_} {10*s_} {-48*s_} q{2*s_} {28*s_} {4*s_} {48*s_} q{8*s_} {-20*s_} {18*s_} {-30*s_} q{-4*s_} {18*s_} {-6*s_} {34*s_}Z" fill="{c_}"/>'
    # topera y charco
    b += '<ellipse cx="380" cy="1300" rx="28" ry="12" fill="#5a4a32"/><ellipse cx="380" cy="1294" rx="18" ry="8" fill="#6e5a3c"/>'
    b += '<ellipse cx="300" cy="1560" rx="120" ry="24" fill="#6f8a9a" opacity="0.65"/><ellipse cx="290" cy="1554" rx="70" ry="9" fill="#c9d8de" opacity="0.5"/>'
    # líneas casi borradas
    b += '<path d="M0 1190 L1080 1190" stroke="#e8ead0" stroke-width="7" opacity="0.28" stroke-dasharray="40 30 90 50 20 60"/>'
    b += '<path d="M540 1190 L540 1920" stroke="#e8ead0" stroke-width="9" opacity="0.25" stroke-dasharray="60 50 30 70"/>'
    b += '<ellipse cx="540" cy="1350" rx="230" ry="80" fill="none" stroke="#e8ead0" stroke-width="8" opacity="0.28" stroke-dasharray="50 40 20 60"/>'
    # porterías oxidadas: pintura saltada, larguero combado, hierba alrededor
    for gi, (gx, gy, w, h) in enumerate(((70, 1230, 220, 150), (790, 1230, 220, 150))):
        sag = 0 if gi == 0 else 16
        frame = f'M{gx} {gy+h} L{gx} {gy} Q{gx+w/2} {gy+sag*2} {gx+w} {gy+ (6 if gi else 0)} L{gx+w} {gy+h}'
        b += f'<path d="{frame}" fill="none" stroke="{OL}" stroke-width="20" stroke-linejoin="round"/>'
        b += f'<path d="{frame}" fill="none" stroke="#d6cfbf" stroke-width="12" stroke-linejoin="round"/>'
        for _ in range(9):
            t = r.random()
            if t < .33: px_, py_ = gx, gy + r.uniform(0, h)
            elif t < .66: px_, py_ = gx + w, gy + r.uniform(0, h)
            else:
                u_ = r.random(); px_ = gx + u_ * w; py_ = gy + sag * 2 * 4 * u_ * (1 - u_) / 2 * 2 * 0.5 + (0 if gi == 0 else 0)
            b += f'<ellipse cx="{px_}" cy="{py_}" rx="{r.uniform(3,7)}" ry="{r.uniform(4,9)}" fill="{r.choice(["#8a4a26", "#a0522d", "#6e3a1e"])}"/>'
        b += f'<path d="M{gx-4} {gy+h} L{gx-4} {gy+h-40}" stroke="#7a3e1e" stroke-width="8" opacity="0.7"/>'
        for xx in (gx - 20, gx + w - 20):
            b += f'<path d="M{xx} {gy+h+6} q6 -34 14 -44 q2 26 6 44 q6 -26 16 -32 q-2 22 -4 32Z" fill="#4a6a1e"/>'
        b += f'<path d="M{gx+10} {gy+h} L{gx+w-10} {gy+h}" stroke="#2a3a12" stroke-width="10" opacity="0.4"/>'
        # restos de red rotos colgando
        if gi == 0:
            b += f'<path d="M{gx+30} {gy+4} l-4 40 m14 -40 l2 30 m14 -30 l-3 22" stroke="#e8e8e8" stroke-width="2" opacity="0.7"/>'
    # silla de plástico volcada y neumático
    b += f'<g transform="rotate(-70 690 1460)"><rect x="660" y="1420" width="60" height="50" rx="6" fill="#e8e8ee" stroke="{OL}" stroke-width="4"/><rect x="660" y="1470" width="60" height="12" rx="4" fill="#d0d0d8" stroke="{OL}" stroke-width="3"/><line x1="666" y1="1482" x2="662" y2="1530" stroke="#d0d0d8" stroke-width="6"/><line x1="714" y1="1482" x2="718" y2="1530" stroke="#d0d0d8" stroke-width="6"/></g>'
    b += f'<ellipse cx="900" cy="1500" rx="58" ry="22" fill="#1e1e22" stroke="{OL}" stroke-width="4"/><ellipse cx="900" cy="1496" rx="30" ry="10" fill="#4a5a2a"/>'
    return svg(1080, 1920, b, d)


def hierba():
    r = random.Random(11); b = ''
    for y0, cols in ((1380, ("#6f8f30", "#5d7d26")), (1560, ("#56761f", "#4a6a1a")), (1740, ("#3f5c15", "#344e10"))):
        b += f'<rect x="0" y="{y0+170}" width="1080" height="{1920-y0}" fill="{cols[1]}"/>'
        for i in range(95):
            x = r.randint(-30, 1110); h = r.randint(170, 360); w = r.randint(14, 30); lean = r.randint(-70, 70)
            c = cols[i % 2]
            b += f'<path d="M{x} {y0+220} Q{x+lean*.4} {y0+220-h*.55} {x+lean} {y0+220-h} Q{x+w*.6+lean*.3} {y0+220-h*.5} {x+w} {y0+220}Z" fill="{c}"/>'
            if i % 7 == 0:
                b += f'<path d="M{x+3} {y0+220-h*.3} Q{x+lean*.5} {y0+220-h*.7} {x+lean} {y0+220-h}" stroke="#a8c45a" stroke-width="3" fill="none" opacity="0.6"/>'
        # flores silvestres
        for i in range(8):
            x = r.randint(0, 1080); y = y0 + r.randint(40, 160)
            b += f'<circle cx="{x}" cy="{y}" r="9" fill="#f6e27a"/><circle cx="{x}" cy="{y}" r="4" fill="#d9822b"/>'
    return svg(1080, 1920, b, grain=False)

def bg_vestuario():
    d = sky("w", [(0, "#2e4466"), (1, "#1a2440")])
    d += '<radialGradient id="cone" cx="0.5" cy="0.08" r="0.75"><stop offset="0" stop-color="#ffe7a8" stop-opacity="0.55"/><stop offset="0.6" stop-color="#ffe7a8" stop-opacity="0.08"/><stop offset="1" stop-color="#ffe7a8" stop-opacity="0"/></radialGradient>'
    d += sky("lk", [(0, "#4d6fa3"), (1, "#36507c")])
    d += sky("fl", [(0, "#3a3240"), (1, "#1e1a26")])
    b = '<rect width="1080" height="1920" fill="url(#w)"/>'
    # azulejos de pared
    for y in range(0, 1220, 62):
        for x in range((y // 62) % 2 * -31, 1080, 62):
            b += f'<rect x="{x+2}" y="{y+2}" width="58" height="58" rx="4" fill="#ffffff" opacity="{0.035 + ((x*7+y*3)%5)*0.006}"/>'
    # abandono: azulejos caídos, moho, óxido, desconchones, escombros
    rv0 = random.Random(21)
    for _ in range(22):
        x = rv0.randrange(0, 1080, 62) + rv0.choice([0, -31]); y = rv0.randrange(0, 480, 62)
        b += f'<rect x="{x+2}" y="{y+2}" width="58" height="58" fill="#2a3344"/><path d="M{x+8} {y+10} l20 14 l-6 22" stroke="#1a2230" stroke-width="3" fill="none"/>'
    for (mx, my, mr) in ((60, 420, 90), (980, 60, 120), (520, 470, 70)):
        b += f'<ellipse cx="{mx}" cy="{my}" rx="{mr}" ry="{mr*.6}" fill="#3a4a2a" opacity="0.45" filter="url(#blur12)"/>'
    # manchas de humedad
    b += '<ellipse cx="200" cy="180" rx="160" ry="90" fill="#13202f" opacity="0.35" filter="url(#blur12)"/><ellipse cx="900" cy="980" rx="120" ry="200" fill="#13202f" opacity="0.3" filter="url(#blur12)"/>'
    # póster antiguo
    b += f'<g transform="translate(0,-120) rotate(-3 880 260)"><rect x="770" y="140" width="230" height="270" fill="#e8dcc0" stroke="{OL}" stroke-width="5"/>'
    b += '<rect x="790" y="160" width="190" height="130" fill="#8a7a5a"/>'
    for i in range(6): b += f'<circle cx="{815+i*30}" cy="{235 + (i%2)*12}" r="12" fill="#3a3020"/>'
    b += '<text x="885" y="330" font-family="Anton" font-size="34" text-anchor="middle" fill="#3a2a1a">CAMPEONES</text><text x="885" y="375" font-family="Anton" font-size="30" text-anchor="middle" fill="#a52a2a">REGIONAL 1987</text>'
    b += '<path d="M770 140 L800 140 L770 175Z" fill="#c9b994"/></g>'
    # telaraña
    b += '<g stroke="#ffffff" stroke-opacity="0.25" stroke-width="2" fill="none"><path d="M0 0 L140 120 M0 0 L60 160 M0 0 L160 40"/><path d="M40 35 Q60 60 20 60 M80 70 Q100 110 40 115 M110 95 Q140 60 120 25"/></g>'
    # tendedero y camisetas con sombra
    b += '<path d="M-10 300 Q540 390 1090 300" fill="none" stroke="#9aa4b0" stroke-width="4"/>'
    for i, (c, cs) in enumerate((("#c0392b", "#8f2a20"), ("#f2efe8", "#c9c2b5"), ("#c0392b", "#8f2a20"), ("#f2efe8", "#c9c2b5"), ("#c0392b", "#8f2a20"))):
        x = 120 + i * 210; y = 318 + 26 * (1 - abs(i - 2) / 2)
        sh = f'<path d="M{x-58} {y} L{x-22} {y-9} Q{x} {y+12} {x+22} {y-9} L{x+58} {y} L{x+80} {y+48} L{x+48} {y+60} L{x+48} {y+165} L{x-48} {y+165} L{x-48} {y+60} L{x-80} {y+48}Z"/>'
        b += f'<g filter="url(#drop)">{cel(sh, c, cs, None, -22, -4, 5)}</g>'
        b += f'<text x="{x}" y="{y+120}" font-family="Anton" font-size="52" text-anchor="middle" fill="{"#f2efe8" if c=="#c0392b" else "#c0392b"}">{[7,10,4,9,1][i]}</text>'
        b += f'<rect x="{x-6}" y="{y-16}" width="12" height="22" rx="3" fill="#d9a441" stroke="{OL}" stroke-width="3"/>'
    # taquillas
    for i in range(6):
        x = 25 + i * 176
        b += f'<rect x="{x}" y="500" width="164" height="640" rx="8" fill="url(#lk)" stroke="{OL}" stroke-width="6"/>'
        b += f'<rect x="{x+130}" y="500" width="34" height="640" fill="#2b4064" opacity="0.6"/>'
        for k in range(5): b += f'<rect x="{x+36}" y="{540+k*18}" width="90" height="7" rx="3" fill="#24395c"/>'
        b += f'<rect x="{x+125}" y="780" width="12" height="56" rx="5" fill="#d7dee8" stroke="{OL}" stroke-width="3"/>'
        b += f'<rect x="{x+50}" y="660" width="60" height="34" rx="4" fill="#e8e1d0" opacity="0.85"/><text x="{x+80}" y="688" font-family="Anton" font-size="26" text-anchor="middle" fill="#3a3a4a">{i+1:02d}</text>'
        if i == 2: b += f'<path d="M{x+30} 900 q20 -10 40 10 q-15 25 -40 -10" fill="#26385a"/>'  # abolladura
        b += f'<path d="M{x+8} 510 L{x+8} 1130" stroke="#ffffff" stroke-opacity="0.12" stroke-width="6"/>'
    # taquilla abierta
    b += f'<path d="M729 500 L650 540 L650 1100 L729 1140Z" fill="#3b5683" stroke="{OL}" stroke-width="6"/>'
    # banco
    b += f'<rect x="50" y="1140" width="980" height="44" rx="10" fill="#9a6a40" stroke="{OL}" stroke-width="6"/><rect x="50" y="1140" width="980" height="12" rx="6" fill="#c08a58"/>'
    b += f'<rect x="110" y="1184" width="28" height="120" fill="#6a4226" stroke="{OL}" stroke-width="4"/><rect x="940" y="1184" width="28" height="120" fill="#6a4226" stroke="{OL}" stroke-width="4"/>'
    # botas en el banco
    b += f'<path d="M820 1140 L820 1090 L860 1090 L870 1120 L920 1125 L925 1140Z" fill="#222" stroke="{OL}" stroke-width="4"/><path d="M860 1140 L860 1100" stroke="#eee" stroke-width="3"/>'
    # suelo con charco y reflejo
    b += '<rect x="0" y="1300" width="1080" height="620" fill="url(#fl)"/>'
    for x in range(-600, 1700, 110): b += f'<line x1="{x}" y1="1300" x2="{x+(x-540)*0.9}" y2="1920" stroke="#ffffff" stroke-opacity="0.05" stroke-width="3"/>'
    for y in (1360, 1450, 1570, 1720, 1900): b += f'<line x1="0" y1="{y}" x2="1080" y2="{y}" stroke="#ffffff" stroke-opacity="0.04" stroke-width="3"/>'
    b += '<ellipse cx="300" cy="1700" rx="230" ry="50" fill="#5a6c8c" opacity="0.35"/><ellipse cx="320" cy="1690" rx="120" ry="16" fill="#ffe7a8" opacity="0.25"/>'
    rv = random.Random(21)
    for i in range(6):
        x = 25 + i * 176
        for _ in range(3):
            rx = x + rv.randint(10, 140); ry = rv.randint(520, 1100)
            b += f'<ellipse cx="{rx}" cy="{ry}" rx="{rv.randint(6,16)}" ry="{rv.randint(8,22)}" fill="#8a4a26" opacity="0.7"/>'
        b += f'<rect x="{x}" y="1060" width="164" height="80" fill="#6a3a1e" opacity="0.35"/>'
    b += '<path d="M380 1140 L470 1140 L500 1176 L430 1196Z" fill="#6a4226" stroke="#1d1630" stroke-width="4"/>'  # tabla rota del banco
    for _ in range(14):
        x = rv.randint(20, 1060); y = rv.randint(1320, 1880)
        b += f'<rect x="{x}" y="{y}" width="{rv.randint(14,34)}" height="{rv.randint(10,22)}" fill="{rv.choice(["#5a6a8a", "#4a5670", "#8a8a96"])}" transform="rotate({rv.randint(-40,40)} {x} {y})" opacity="0.85"/>'
    b += '<path d="M760 1420 q30 -20 60 0 q-10 16 -60 0Z" fill="#e8e6e0" opacity="0.8"/><rect x="900" y="1500" width="16" height="26" rx="3" fill="#2e7d32" transform="rotate(70 900 1500)"/>'
    # lámpara y cono de luz
    b += '<line x1="540" y1="0" x2="540" y2="120" stroke="#111" stroke-width="6"/>'
    b += f'<path d="M455 120 L625 120 L665 185 L415 185Z" fill="#2c2c34" stroke="{OL}" stroke-width="5"/><ellipse cx="540" cy="188" rx="46" ry="14" fill="#fff6d0"/>'
    b += '<path d="M430 190 L650 190 L1080 1400 L0 1400Z" fill="#ffe7a8" opacity="0.07"/>'
    b += '<rect width="1080" height="1920" fill="url(#cone)"/>'
    return svg(1080, 1920, b, d)

def bg_notaria():
    d = sky("wall", [(0, "#3a2b3e"), (1, "#24192c")])
    d += '<radialGradient id="lamp" cx="0.25" cy="0.47" r="0.55"><stop offset="0" stop-color="#ffd27a" stop-opacity="0.6"/><stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></radialGradient>'
    d += sky("desk", [(0, "#8a5532"), (0.06, "#6e4024"), (1, "#3d2212")])
    b = '<rect width="1080" height="1920" fill="url(#wall)"/>'
    # paneles de madera
    for x in range(0, 1080, 180):
        b += f'<rect x="{x+10}" y="640" width="160" height="380" rx="6" fill="#4a2f22" stroke="#2b1a12" stroke-width="5"/>'
        b += f'<rect x="{x+26}" y="656" width="128" height="348" rx="4" fill="none" stroke="#6a452f" stroke-width="3"/>'
    # ventana con persianas
    b += f'<rect x="640" y="90" width="380" height="470" fill="#1c2d4a" stroke="{OL}" stroke-width="10"/>'
    b += '<rect x="650" y="100" width="360" height="450" fill="#ffb26b" opacity="0.6"/>'
    for y in range(110, 550, 34): b += f'<rect x="650" y="{y}" width="360" height="20" fill="#d9b48a"/>'
    b += '<path d="M650 100 L1010 100 L560 1100 L200 1100Z" fill="#ffd6a0" opacity="0.08"/>'
    # estantería
    b += f'<rect x="40" y="80" width="560" height="530" fill="#3a2418" stroke="{OL}" stroke-width="8"/>'
    r = random.Random(3)
    for y in (250, 420, 590):
        b += f'<rect x="40" y="{y}" width="560" height="18" fill="#6a4228"/>'
        x = 60
        while x < 570:
            w = r.randint(26, 52); h = r.randint(110, 150)
            c = r.choice(["#8c2f39", "#2f5d8c", "#b08a2a", "#3e7d4f", "#6b4c9a", "#a5542e", "#2a3a5a"])
            if r.random() < .12:
                b += f'<rect x="{x}" y="{y-h+20}" width="{w}" height="{h-20}" fill="{c}" stroke="{OL}" stroke-width="3" transform="rotate(12 {x} {y})"/>'
                x += w + 20; continue
            b += f'<rect x="{x}" y="{y-h}" width="{w}" height="{h}" rx="3" fill="{c}" stroke="{OL}" stroke-width="3"/>'
            b += f'<rect x="{x+5}" y="{y-h+18}" width="{w-10}" height="6" fill="#e3c27a" opacity="0.7"/><rect x="{x+5}" y="{y-30}" width="{w-10}" height="6" fill="#e3c27a" opacity="0.7"/>'
            x += w + 4
    # reloj de pared
    b += f'<circle cx="840" cy="760" r="80" fill="#e9dcc0" stroke="#6a452f" stroke-width="14"/><line x1="840" y1="760" x2="840" y2="705" stroke="{OL}" stroke-width="7"/><line x1="840" y1="760" x2="880" y2="770" stroke="{OL}" stroke-width="5"/>'
    # lámpara de banquero
    b += f'<rect x="110" y="1000" width="160" height="22" rx="8" fill="#c9a24a" stroke="{OL}" stroke-width="5"/><rect x="180" y="900" width="18" height="100" fill="#c9a24a" stroke="{OL}" stroke-width="4"/>'
    b += f'<path d="M80 900 Q190 820 300 900Z" fill="#1f7a4a" stroke="{OL}" stroke-width="6"/><path d="M95 895 Q190 840 285 895" fill="none" stroke="#5ec48a" stroke-width="5" opacity="0.6"/>'
    b += '<rect width="1080" height="1920" fill="url(#lamp)"/>'
    # mesa
    b += '<rect x="0" y="1020" width="1080" height="900" fill="url(#desk)"/>'
    for i in range(9): b += f'<path d="M0 {1080+i*95} Q540 {1060+i*95} 1080 {1090+i*95}" stroke="#2e180c" stroke-opacity="0.35" stroke-width="3" fill="none"/>'
    b += '<rect x="0" y="1020" width="1080" height="16" fill="#a8703f"/>'
    # tintero y sello
    b += f'<rect x="860" y="1100" width="120" height="70" rx="10" fill="#26262e" stroke="{OL}" stroke-width="5"/><path d="M890 1100 L900 1060 L940 1060 L950 1100" fill="#3a3a44" stroke="{OL}" stroke-width="4"/>'
    return svg(1080, 1920, b, d)

def bg_puerta():
    d = sky("sk", [(0, "#2a2c5c"), (0.45, "#7a4f86"), (0.8, "#e88d67"), (1, "#f4b07a")])
    b = '<rect width="1080" height="1920" fill="url(#sk)"/>'
    b += cloud(250, 260, 1.4, "#9a6a9a", .5) + cloud(820, 180, 1.1, "#b07aa0", .45)
    # farola
    b += f'<rect x="950" y="420" width="18" height="860" fill="#2a2a30" stroke="{OL}" stroke-width="4"/><path d="M915 420 L1005 420 L990 380 L930 380Z" fill="#2a2a30" stroke="{OL}" stroke-width="4"/><ellipse cx="960" cy="430" rx="30" ry="10" fill="#ffe7a0"/>'
    b += '<circle cx="960" cy="440" r="120" fill="#ffe7a0" opacity="0.22" filter="url(#blur12)"/>'
    # muro de ladrillo
    b += f'<rect x="0" y="600" width="1080" height="700" fill="#a65b42" stroke="{OL}" stroke-width="6"/>'
    r = random.Random(5)
    for row, y in enumerate(range(605, 1300, 46)):
        off = 0 if row % 2 else 52
        for x in range(-off, 1080, 104):
            c = r.choice(["#b8674b", "#a85a40", "#c27255", "#9a5038"])
            b += f'<rect x="{x+3}" y="{y+3}" width="98" height="40" rx="3" fill="{c}"/>'
    b += '<rect x="0" y="600" width="1080" height="700" fill="#2a1a2a" opacity="0.25"/>'
    # grafiti
    b += '<text x="40" y="1200" font-family="Anton" font-size="64" fill="#5ac8e8" opacity="0.6" transform="rotate(-6 40 1200)">SL 1931</text>'
    # cartel desconchado
    b += f'<rect x="170" y="440" width="740" height="150" rx="14" fill="#1e5aa8" stroke="{OL}" stroke-width="8"/>'
    b += '<text x="540" y="548" font-family="Anton" font-size="92" text-anchor="middle" fill="#f2f2f2">C.D. SAN LORENZO</text>'
    b += '<path d="M866 448 L908 448 L908 500 Q892 490 880 512 Q872 470 866 448Z" fill="#8a7a6a" opacity="0.8"/>'
    b += '<path d="M180 560 Q230 540 260 580 L180 580Z" fill="#8a7a6a" opacity="0.8"/>'
    # verja oxidada con cadena y candado
    b += f'<rect x="290" y="720" width="500" height="580" fill="#1b1b24" stroke="{OL}" stroke-width="8"/>'
    for x in range(305, 785, 36):
        b += f'<rect x="{x}" y="725" width="16" height="575" fill="#4a4a58"/><rect x="{x}" y="725" width="5" height="575" fill="#6a6a7a"/>'
        b += f'<path d="M{x-2} 735 L{x+8} 712 L{x+18} 735Z" fill="#4a4a58"/>'
        if (x // 36) % 3 == 0: b += f'<rect x="{x}" y="{900 + (x%7)*20}" width="16" height="60" fill="#8a4a2a" opacity="0.7"/>'
    b += f'<rect x="290" y="960" width="500" height="22" fill="#3a3a48" stroke="{OL}" stroke-width="4"/>'
    for i in range(9):
        b += f'<ellipse cx="{470+i*18}" cy="{975+ (i%2)*6}" rx="14" ry="9" fill="none" stroke="#9a9aa8" stroke-width="6"/>'
    b += f'<rect x="520" y="985" width="50" height="46" rx="6" fill="#c9a24a" stroke="{OL}" stroke-width="5"/><path d="M528 985 Q545 950 562 985" fill="none" stroke="#9a9aa8" stroke-width="7"/>'
    # acera y calle
    b += '<rect x="0" y="1300" width="1080" height="80" fill="#8a8690"/><rect x="0" y="1300" width="1080" height="10" fill="#aaa6b0"/>'
    b += '<rect x="0" y="1380" width="1080" height="540" fill="#3a3a44"/>'
    for x in range(40, 1080, 260): b += f'<rect x="{x}" y="1640" width="140" height="16" fill="#e8e0c0" opacity="0.5"/>'
    b += '<ellipse cx="960" cy="1420" rx="200" ry="40" fill="#ffe7a0" opacity="0.12"/>'
    return svg(1080, 1920, b, d)

def bg_dark():
    d = '<radialGradient id="g" cx="0.5" cy="0.38" r="0.85"><stop offset="0" stop-color="#2a3560"/><stop offset="0.6" stop-color="#151c35"/><stop offset="1" stop-color="#0a0e1c"/></radialGradient>'
    b = '<rect width="1080" height="1920" fill="url(#g)"/>'
    # silueta de estadio y focos al fondo
    b += '<path d="M0 1500 L0 1380 Q540 1290 1080 1380 L1080 1500Z" fill="#0f1428"/>'
    for x in (150, 930):
        b += f'<rect x="{x-6}" y="1100" width="12" height="320" fill="#0f1428"/><rect x="{x-50}" y="1080" width="100" height="40" fill="#0f1428"/>'
        b += f'<path d="M{x} 1100 L{x-500} 300 L{x+200} 300Z" fill="#9fb4ff" opacity="0.05"/>'
        b += f'<circle cx="{x}" cy="1095" r="60" fill="#cfe0ff" opacity="0.18" filter="url(#blur12)"/>'
    b += '<rect x="0" y="1500" width="1080" height="420" fill="#0a0e1c"/>'
    return svg(1080, 1920, b, d)

def baldosas():
    d = '<radialGradient id="sp" cx="0.5" cy="0.58" r="0.5"><stop offset="0" stop-color="#ffd27a" stop-opacity="0.35"/><stop offset="1" stop-color="#000" stop-opacity="0.6"/></radialGradient>'
    b = '<rect width="1080" height="1920" fill="#2c2833"/>'
    r = random.Random(2)
    for y in range(-60, 1920, 190):
        for x in range(-40, 1080, 190):
            c = r.choice(["#4a4554", "#454050", "#504a5a"])
            b += f'<rect x="{x}" y="{y}" width="184" height="184" rx="6" fill="{c}"/>'
            b += f'<rect x="{x}" y="{y}" width="184" height="10" rx="5" fill="#ffffff" opacity="0.05"/>'
    b += f'<rect x="436" y="1080" width="184" height="184" rx="6" fill="#6b5a3a" stroke="#ffc93c" stroke-width="5"/>'
    b += '<path d="M450 1100 L500 1160 L470 1230 M600 1260 L560 1200 L590 1120" stroke="#1f1a10" stroke-width="5" fill="none"/>'
    b += '<rect x="436" y="1258" width="184" height="10" fill="#000" opacity="0.6"/>'
    b += '<rect width="1080" height="1920" fill="url(#sp)"/>'
    return svg(1080, 1920, b, d)

# ============================================================ PERSONAJES
def ear(x, y, flip=1):
    return (cel(f'<ellipse cx="{x}" cy="{y}" rx="28" ry="38"/>', SK, SKS, None, -10 * flip, -4, 6)
            + f'<path d="M{x-8*flip} {y-14} Q{x+6*flip} {y} {x-6*flip} {y+16}" stroke="{SKS}" stroke-width="6" fill="none"/>')

def face(cx, cy, r=120):
    return (ear(cx - r * .97, cy + 12, 1) + ear(cx + r * .97, cy + 12, -1)
            + cel(f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r*1.1}"/>', SK, SKS, SKH, -34, -16, 7))

def eye(x, y, r=13, look=0):
    return (f'<ellipse cx="{x}" cy="{y}" rx="{r*1.55}" ry="{r*1.35}" fill="#fff" stroke="{OL}" stroke-width="4"/>'
            f'<circle cx="{x+look}" cy="{y+1}" r="{r}" fill="#4a3424"/><circle cx="{x+look}" cy="{y+1}" r="{r*.55}" fill="{OL}"/>'
            f'<circle cx="{x+look+r*.35}" cy="{y-r*.35}" r="{r*.32}" fill="#fff"/>')

def neck(x, y, w, h):
    return cel(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>', SKS, "#b97b54", None, -14, 0, 6)

def paco():
    b = '<ellipse cx="400" cy="1000" rx="320" ry="40" fill="#000" opacity="0"/>'
    # torso chándal
    torso = '<path d="M112 1400 L120 1000 Q118 700 270 640 Q400 600 530 640 Q682 700 680 1000 L688 1400Z"/>'
    b += cel(torso, "#2d5fa8", "#1f437a", "#4a7fc8", -60, -10, 8)
    b += '<path d="M400 650 L400 1000" stroke="#d9dde6" stroke-width="10"/><rect x="392" y="700" width="16" height="30" rx="4" fill="#c9cfd9" stroke="#1d1630" stroke-width="3"/>'
    b += '<path d="M168 720 Q150 860 146 1400" stroke="#f2f2f2" stroke-width="16" fill="none"/><path d="M632 720 Q650 860 654 1400" stroke="#f2f2f2" stroke-width="16" fill="none"/><path d="M400 1000 L400 1400" stroke="#d9dde6" stroke-width="10"/>'
    b += '<path d="M220 780 Q260 820 240 880 M560 780 Q540 840 565 880" stroke="#1f437a" stroke-width="7" fill="none"/>'
    # cuello de chándal
    b += cel('<path d="M318 628 L400 700 L482 628 L470 600 L400 650 L330 600Z"/>', "#24508f", "#183a6a", None, -10, 0, 6)
    # escudo
    b += cel('<path d="M520 720 L580 720 L580 770 L550 795 L520 770Z"/>', "#f2f2f2", "#cfd3db", None, -6, 0, 4)
    b += '<rect x="520" y="740" width="60" height="12" fill="#2d5fa8"/>'
    # toalla
    towel = '<path d="M455 615 Q590 600 650 690 L615 900 L558 885 L588 735 Q545 676 455 662Z"/>'
    b += cel(towel, "#f6f4ef", "#d8d3c8", None, -20, -6, 6)
    b += '<path d="M565 860 L612 872 M570 840 L616 852" stroke="#c0392b" stroke-width="7"/>'
    # cesta
    b += cel('<path d="M195 860 Q195 840 215 840 L585 840 Q605 840 605 860 L572 1000 L228 1000Z"/>', "#c08f52", "#93683a", None, -30, 0, 7)
    for i in range(7): b += f'<path d="M{230+i*55} 850 L{245+i*52} 995" stroke="#7a5430" stroke-width="5"/>'
    for y in (890, 940): b += f'<path d="M210 {y} Q400 {y+14} 595 {y}" stroke="#7a5430" stroke-width="5" fill="none"/>'
    b += cel('<path d="M215 846 Q290 770 380 826 Q450 760 530 812 Q575 790 590 846Z"/>', "#c94236", "#94291f", None, -18, -4, 6)
    b += '<path d="M300 828 Q365 780 440 824" fill="#f2efe8" stroke="#1d1630" stroke-width="5"/><text x="370" y="822" font-family="Anton" font-size="34" fill="#c94236">8</text>'
    # manos con dedos
    for hx, f in ((222, 1), (578, -1)):
        b += cel(f'<ellipse cx="{hx}" cy="862" rx="44" ry="36"/>', SK, SKS, None, -10 * f, -6, 6)
        for k in range(3): b += f'<path d="M{hx-22+k*16} 840 L{hx-22+k*16} 868" stroke="{SKS}" stroke-width="4"/>'
    # cabeza
    b += '<g transform="translate(0,120)">'
    b += neck(352, 410, 96, 110)
    b += face(400, 330)
    # pelo canoso lateral
    b += cel('<path d="M286 320 Q266 240 296 196 L318 332Z"/>', "#e4e4e4", "#b9b9c2", None, 8, 0, 5)
    b += cel('<path d="M514 320 Q534 240 504 196 L482 332Z"/>', "#e4e4e4", "#b9b9c2", None, -8, 0, 5)
    # boina
    b += cel('<path d="M262 238 Q270 140 405 128 Q552 132 556 232 Q480 206 405 210 Q320 212 262 238Z"/>', "#44444f", "#2c2c35", "#62626f", -30, -10, 7)
    b += cel('<path d="M258 240 Q405 196 560 232 L574 256 Q405 222 244 262Z"/>', "#33333c", "#22222a", None, -10, 0, 6)
    b += '<circle cx="405" cy="130" r="9" fill="#33333c"/>'
    # cejas, ojos, gafas
    b += '<path d="M316 266 Q350 246 384 262" stroke="#ececec" stroke-width="14" fill="none" stroke-linecap="round"/><path d="M416 262 Q450 246 484 266" stroke="#ececec" stroke-width="14" fill="none" stroke-linecap="round"/>'
    b += eye(350, 316, 11) + eye(450, 316, 11)
    b += '<path d="M330 300 Q350 292 370 300" stroke="#1d1630" stroke-width="4" fill="none"/><path d="M430 300 Q450 292 470 300" stroke="#1d1630" stroke-width="4" fill="none"/>'
    b += '<path d="M318 340 Q350 350 380 340 M420 340 Q450 350 482 340" stroke="#c98a62" stroke-width="4" fill="none"/>'
    for gx in (298, 404):
        b += f'<rect x="{gx}" y="280" width="98" height="72" rx="24" fill="#cfe6ff" fill-opacity="0.18" stroke="#1d1630" stroke-width="9"/>'
        b += f'<path d="M{gx+16} 296 L{gx+40} 296" stroke="#fff" stroke-width="6" stroke-linecap="round" opacity="0.8"/>'
    b += '<path d="M396 306 L404 306" stroke="#1d1630" stroke-width="9"/><path d="M298 300 L282 296 M502 300 L518 296" stroke="#1d1630" stroke-width="8"/>'
    # nariz
    b += cel('<path d="M392 330 Q430 372 410 396 Q392 404 378 392 Q376 360 392 330Z"/>', SK, SKS, None, -8, -4, 5)
    b += '<circle cx="402" cy="378" r="6" fill="#fff" opacity="0.5"/>'
    # mejillas
    b += '<ellipse cx="318" cy="384" rx="26" ry="16" fill="#e7887a" opacity="0.45"/><ellipse cx="486" cy="384" rx="26" ry="16" fill="#e7887a" opacity="0.45"/>'
    # bigote
    b += cel('<path d="M318 418 Q350 382 400 404 Q450 382 482 418 Q452 440 400 424 Q348 440 318 418Z"/>', "#efefef", "#c4c4cc", None, -10, -4, 5)
    b += '<path d="M372 452 Q400 464 428 452" stroke="#1d1630" stroke-width="6" fill="none" stroke-linecap="round"/>'
    # arrugas
    b += '<path d="M286 360 Q298 382 294 400 M514 360 Q502 382 506 400 M360 222 Q400 214 440 222" stroke="#c98a62" stroke-width="5" fill="none" opacity="0.8"/>'
    b += '</g>'
    return svg(800, 1400, b, grain=False)

def arturo():
    b = ''
    torso = '<path d="M110 1000 Q108 700 260 640 Q400 600 540 640 Q692 700 690 1000Z"/>'
    b += cel(torso, "#262836", "#171822", "#3c3f52", -60, -10, 8)
    # camisa y corbata
    b += cel('<path d="M330 618 L400 790 L470 618 L440 600 L400 650 L360 600Z"/>', "#f4f4f6", "#cfd0d8", None, -8, 0, 5)
    b += cel('<path d="M384 650 L416 650 L430 790 L400 838 L370 790Z"/>', "#b8252d", "#861a20", "#d84850", -10, 0, 5)
    b += cel('<path d="M378 630 L422 630 L416 662 L384 662Z"/>', "#a3202a", "#7a1820", None, -4, 0, 4)
    # solapas
    b += cel('<path d="M290 628 L380 800 L322 850 L250 690Z"/>', "#2e3142", "#1d1f2b", None, -12, 0, 6)
    b += cel('<path d="M510 628 L420 800 L478 850 L550 690Z"/>', "#2e3142", "#1d1f2b", None, -12, 0, 6)
    b += '<path d="M330 760 L335 770" stroke="#c9a24a" stroke-width="8"/>'
    b += cel('<path d="M520 760 L585 758 L578 792 L526 794Z"/>', "#d9b13f", "#a8862a", None, -6, 0, 4)
    # brazos cruzados
    b += cel('<path d="M140 860 Q400 790 660 860 L660 945 Q400 880 140 945Z"/>', "#2b2e3e", "#1b1d28", "#41455a", -10, -12, 7)
    b += '<path d="M260 870 Q300 860 330 880 M470 870 Q510 860 540 880" stroke="#1b1d28" stroke-width="6" fill="none"/>'
    b += cel('<ellipse cx="642" cy="902" rx="48" ry="38"/>', SK, SKS, None, -10, -6, 6)
    b += cel('<rect x="560" y="876" width="34" height="54" rx="8"/>', "#e8bf4a", "#b38e2a", None, -6, 0, 4)
    b += '<circle cx="577" cy="903" r="10" fill="#fff6d6"/>'
    b += '<rect x="604" y="884" width="12" height="40" rx="4" fill="#f4f4f6" stroke="#1d1630" stroke-width="3"/>'
    # cabeza
    b += '<g transform="translate(0,120)">'
    b += neck(352, 410, 96, 110)
    b += face(400, 330, 118)
    # pelo engominado
    b += cel('<path d="M278 312 Q248 160 405 140 Q560 150 528 312 Q508 222 420 214 Q332 214 300 262Z"/>', "#1f1f28", "#121218", "#3c3c4a", -26, -14, 7)
    b += '<path d="M318 190 Q410 162 500 200 M330 214 Q420 186 506 226" stroke="#4a4a5a" stroke-width="5" fill="none"/>'
    b += '<path d="M282 300 Q278 258 298 244" stroke="#a9a9b6" stroke-width="12" fill="none"/><path d="M524 300 Q528 258 508 244" stroke="#a9a9b6" stroke-width="12" fill="none"/>'
    # cejas fruncidas
    b += '<path d="M300 262 L386 282" stroke="#1d1630" stroke-width="14" stroke-linecap="round"/><path d="M500 262 L414 282" stroke="#1d1630" stroke-width="14" stroke-linecap="round"/>'
    # gafas de sol
    for p in ('<path d="M292 290 L394 290 L388 346 Q345 364 302 342Z"/>', '<path d="M406 290 L508 290 L498 342 Q455 364 412 346Z"/>'):
        b += cel(p, "#22222c", "#0c0c12", None, -10, 0, 6)
    b += '<path d="M310 302 L350 302 M320 316 L340 316" stroke="#fff" stroke-opacity="0.55" stroke-width="6" stroke-linecap="round"/><path d="M424 302 L464 302" stroke="#fff" stroke-opacity="0.55" stroke-width="6" stroke-linecap="round"/>'
    b += '<path d="M394 300 L406 300" stroke="#0c0c12" stroke-width="9"/>'
    b += cel('<path d="M392 340 Q432 380 412 398 Q392 406 378 394 Q378 364 392 340Z"/>', SK, SKS, None, -8, -4, 5)
    # sonrisa malvada
    b += '<path d="M296 396 Q306 474 400 486 Q494 474 504 396 Q474 458 400 462 Q326 458 296 396Z" fill="#2b2b36" opacity="0.22"/>'
    b += cel('<path d="M326 414 Q400 486 480 406 Q474 452 400 466 Q340 460 326 414Z"/>', "#ffffff", "#d9d9e0", None, -6, 0, 6)
    b += '<path d="M336 424 Q400 444 472 418" stroke="#1d1630" stroke-width="3" fill="none"/>'
    b += '<path d="M470 410 L486 400" stroke="#1d1630" stroke-width="5" stroke-linecap="round"/>'
    b += '</g>'
    return svg(800, 1000, b, grain=False)

def jugador(kind):
    b = ''
    if kind == "ramon":
        b += cel('<path d="M14 520 Q14 340 200 312 Q386 340 386 520Z"/>', "#2fa463", "#1f7a46", "#4cc47e", -40, -8, 7)
        b += '<path d="M60 400 L340 400" stroke="#1f7a46" stroke-width="10" opacity="0.6"/>'
        b += '<text x="200" y="490" font-family="Anton" font-size="96" text-anchor="middle" fill="#fff" stroke="#1d1630" stroke-width="4">1</text>'
        b += neck(158, 250, 84, 80)
        b += face(200, 200, 100)
        b += cel('<path d="M106 182 Q114 96 200 92 Q292 96 298 182 Q262 136 200 136 Q140 136 106 182Z"/>', "#6e6e72", "#4a4a50", None, -14, -6, 6)
        b += eye(160, 198, 10) + eye(240, 198, 10)
        b += '<path d="M140 162 L186 176" stroke="#1d1630" stroke-width="10" stroke-linecap="round"/><path d="M262 162 L214 176" stroke="#1d1630" stroke-width="10" stroke-linecap="round"/>'
        b += cel('<path d="M104 222 Q112 326 200 336 Q288 326 296 222 Q262 264 200 266 Q138 264 104 222Z"/>', "#7c7c80", "#5a5a60", None, -12, -4, 6)
        b += '<path d="M172 282 Q200 292 228 282" stroke="#1d1630" stroke-width="6" fill="none"/>'
        b += cel('<path d="M188 212 Q214 240 200 256 Q184 258 178 248Z"/>', SK, SKS, None, -6, 0, 4)
        # guante
        b += cel('<path d="M290 430 Q290 380 330 380 Q372 380 372 430 L372 500 L290 500Z"/>', "#f2d64a", "#c9ad2a", None, -8, 0, 6)
    elif kind == "josito":
        b += cel('<path d="M44 520 Q44 352 200 330 Q356 352 356 520Z"/>', "#f6f4ef", "#d6d1c5", None, -36, -8, 7)
        b += '<path d="M44 420 L356 420 L356 456 L44 456Z" fill="#c94236"/>'
        b += cel('<path d="M160 330 L200 380 L240 330 L226 320 L200 350 L174 320Z"/>', "#c94236", "#94291f", None, -6, 0, 4)
        b += neck(170, 250, 60, 90)
        b += face(200, 205, 92)
        for i in range(10):
            x = 108 + i * 21; y = 122 + 12 * (i % 2)
            b += cel(f'<circle cx="{x}" cy="{y}" r="30"/>', "#3a2418", "#24160e", None, -6, -6, 5)
        b += eye(166, 206, 12, 4) + eye(234, 206, 12, 4)
        b += '<path d="M146 176 Q166 166 186 176 M214 176 Q234 166 254 176" stroke="#2a1a10" stroke-width="8" fill="none" stroke-linecap="round"/>'
        b += '<path d="M178 262 Q200 274 224 258" stroke="#1d1630" stroke-width="6" fill="none" stroke-linecap="round"/>'
        b += '<ellipse cx="144" cy="244" rx="18" ry="11" fill="#e7887a" opacity="0.5"/><ellipse cx="256" cy="244" rx="18" ry="11" fill="#e7887a" opacity="0.5"/>'
        b += '<path d="M196 216 Q212 236 198 244" stroke="#c98a62" stroke-width="5" fill="none"/>'
    else:
        b += cel('<path d="M0 520 Q0 320 200 296 Q400 320 400 520Z"/>', "#e0661c", "#a84a10", "#f58a3c", -40, -8, 7)
        b += '<text x="200" y="460" font-family="Anton" font-size="60" text-anchor="middle" fill="#ffffff" opacity="0.85">PRIMO</text>'
        b += neck(158, 250, 84, 70)
        b += face(200, 205, 110)
        b += cel('<path d="M86 166 Q96 72 200 70 Q306 72 316 166Z"/>', "#2c3e50", "#1a2836", "#41566b", -16, -6, 6)
        b += cel('<path d="M86 166 Q24 176 12 154 Q34 132 98 144Z"/>', "#24333f", "#162029", None, -6, 0, 5)
        b += eye(158, 210, 12, -6) + eye(242, 210, 12, -6)
        b += '<path d="M140 172 Q160 160 180 174" stroke="#1d1630" stroke-width="8" fill="none"/><path d="M222 162 Q244 150 262 164" stroke="#1d1630" stroke-width="8" fill="none"/>'
        b += '<ellipse cx="200" cy="276" rx="18" ry="15" fill="#5a1a1a" stroke="#1d1630" stroke-width="4"/>'
        b += '<ellipse cx="136" cy="256" rx="22" ry="13" fill="#e7887a" opacity="0.55"/><ellipse cx="264" cy="256" rx="22" ry="13" fill="#e7887a" opacity="0.55"/>'
        b += '<text x="300" y="120" font-family="Anton" font-size="60" fill="#ffc93c" stroke="#1d1630" stroke-width="3">?</text>'
    return svg(400, 520, b, grain=False)

def cabra():
    b = '<ellipse cx="330" cy="520" rx="250" ry="22" fill="#000" opacity="0.25"/>'
    for x in (170, 235, 385, 450):
        b += cel(f'<rect x="{x-15}" y="370" width="30" height="140" rx="12"/>', "#f6f2e6", "#d6cfbd", None, -8, 0, 6)
        b += f'<rect x="{x-17}" y="492" width="34" height="24" rx="6" fill="#3a3a3a"/>'
    b += cel('<ellipse cx="310" cy="300" rx="200" ry="115"/>', "#f8f5ec", "#d9d1bf", "#ffffff", -40, -20, 8)
    for i in range(7): b += f'<path d="M{150+i*45} {360+(i%2)*8} q10 18 20 0" stroke="#c9c0ab" stroke-width="5" fill="none"/>'
    b += '<path d="M115 270 Q70 230 96 205" stroke="#1d1630" stroke-width="9" fill="none" stroke-linecap="round"/>'
    # cabeza
    b += cel('<path d="M432 246 Q470 112 544 120 Q618 140 608 232 Q598 304 544 326 Q472 326 432 246Z"/>', "#f8f5ec", "#d9d1bf", None, -18, -8, 8)
    b += '<path d="M505 132 Q470 56 418 68" stroke="#8a7a5a" stroke-width="18" fill="none" stroke-linecap="round"/><path d="M563 128 Q562 46 614 46" stroke="#8a7a5a" stroke-width="18" fill="none" stroke-linecap="round"/>'
    b += '<path d="M498 120 Q474 76 440 76" stroke="#b3a27a" stroke-width="6" fill="none"/>'
    b += cel('<ellipse cx="454" cy="172" rx="44" ry="19" transform="rotate(-20 454 172)"/>', "#f8f5ec", "#d9d1bf", None, -6, 0, 6)
    b += cel('<ellipse cx="630" cy="172" rx="44" ry="19" transform="rotate(20 630 172)"/>', "#f8f5ec", "#d9d1bf", None, -6, 0, 6)
    for ex in (512, 578):
        b += f'<ellipse cx="{ex}" cy="202" rx="20" ry="15" fill="#f6e27a" stroke="#1d1630" stroke-width="5"/><rect x="{ex-11}" y="198" width="22" height="8" rx="2" fill="#1d1630"/>'
    b += cel('<ellipse cx="546" cy="278" rx="36" ry="24"/>', "#f2c6bd", "#d99d92", None, -6, 0, 5)
    b += '<ellipse cx="534" cy="276" rx="5" ry="7" fill="#1d1630"/><ellipse cx="558" cy="276" rx="5" ry="7" fill="#1d1630"/>'
    b += cel('<path d="M520 320 Q540 392 562 320Z"/>', "#e6dfcc", "#c4b9a0", None, -4, 0, 5)
    # brazalete de capitana
    b += cel('<rect x="236" y="250" width="110" height="44" rx="9"/>', "#ffc93c", "#d9a21a", None, -8, 0, 5)
    b += '<text x="291" y="285" font-family="Anton" font-size="34" text-anchor="middle" fill="#1d1630">C</text>'
    return svg(700, 560, b, grain=False)

def abuelo_foto():
    b = '<g filter="url(#drop)">'
    b += f'<rect x="20" y="20" width="560" height="700" rx="10" fill="#6b4a2a" stroke="{OL}" stroke-width="10"/>'
    b += '<rect x="34" y="34" width="532" height="672" rx="6" fill="none" stroke="#a87a4a" stroke-width="6"/>'
    b += '<rect x="60" y="60" width="480" height="620" fill="#e8d3a8"/></g>'
    b += '<rect x="60" y="60" width="480" height="620" fill="#c9a86a" opacity="0.35"/>'
    b += '<path d="M80 680 Q90 520 300 490 Q510 520 520 680Z" fill="#7a5a3a" stroke="#4a3520" stroke-width="6"/>'
    b += '<path d="M250 482 L300 580 L350 482" fill="#d9c9a8" stroke="#4a3520" stroke-width="5"/><path d="M290 520 L310 520 L316 600 L284 600Z" fill="#5a3a2a"/>'
    b += '<ellipse cx="300" cy="330" rx="124" ry="138" fill="#e3c39a" stroke="#4a3520" stroke-width="6"/>'
    b += '<path d="M176 300 Q168 176 300 166 Q432 176 424 300 Q402 226 300 222 Q206 226 176 300Z" fill="#f4f1ea" stroke="#4a3520" stroke-width="6"/>'
    b += '<path d="M226 294 Q254 280 282 294 M318 294 Q346 280 374 294" stroke="#f4f1ea" stroke-width="12" fill="none" stroke-linecap="round"/>'
    b += '<path d="M236 324 Q255 312 274 324 M326 324 Q345 312 364 324" stroke="#4a3520" stroke-width="7" fill="none" stroke-linecap="round"/>'
    b += '<path d="M292 330 Q316 372 298 386" stroke="#b08a62" stroke-width="6" fill="none"/>'
    b += '<path d="M236 386 Q300 362 364 386" fill="none" stroke="#f4f1ea" stroke-width="18" stroke-linecap="round"/>'
    b += '<path d="M252 410 Q300 444 348 410" fill="none" stroke="#4a3520" stroke-width="7" stroke-linecap="round"/>'
    b += '<path d="M222 352 Q232 372 226 384 M378 352 Q368 372 374 384" stroke="#b08a62" stroke-width="5" fill="none"/>'
    b += '<path d="M380 20 L580 20 L580 220Z" fill="#111"/>'
    b += '<path d="M90 90 L200 90 L90 200Z" fill="#fff" opacity="0.12"/>'
    return svg(600, 740, b, grain=False)

def manos():
    b = '<g filter="url(#drop)">'
    paper = '<rect x="250" y="400" width="590" height="820" rx="10" transform="rotate(-6 540 900)"/>'
    b += cel(paper, "#fbf8ef", "#e6e0cf", None, -20, -10, 8)
    b += '</g><g transform="rotate(-6 540 900)">'
    b += '<text x="545" y="500" font-family="Anton" font-size="58" text-anchor="middle" fill="#2a2a3a">TESTAMENTO</text>'
    b += '<line x1="330" y1="530" x2="760" y2="530" stroke="#2a2a3a" stroke-width="4"/>'
    for i in range(11):
        w = 440 - (i * 37) % 130
        b += f'<rect x="310" y="{570+i*46}" width="{w}" height="12" rx="6" fill="#c9c3b5"/>'
    b += '<circle cx="360" cy="1140" r="40" fill="#b5332e" opacity="0.85"/><circle cx="360" cy="1140" r="28" fill="none" stroke="#e8b0a0" stroke-width="3"/>'
    b += '<path d="M520 1140 Q560 1095 600 1140 T690 1128" stroke="#1e3a8a" stroke-width="6" fill="none"/>'
    b += '</g>'
    # manga + mano izq
    b += cel('<path d="M-20 1560 L150 1170 Q190 1100 262 1124 L330 1150 L250 1240 L180 1600Z"/>', "#3a4a70", "#283654", "#506292", -20, 0, 7)
    b += cel('<path d="M150 1170 L262 1124 L272 1160 L170 1210Z"/>', "#f2f2f2", "#cfd0d6", None, -6, 0, 5)
    b += cel('<path d="M212 1110 Q242 1056 304 1076 L392 1106 Q422 1128 400 1160 L304 1182 Q240 1194 212 1150Z"/>', SK, SKS, None, -10, -8, 7)
    b += '<path d="M300 1090 L386 1116 M296 1112 L380 1138" stroke="#d8996f" stroke-width="5"/>'
    # mano der con boli
    b += cel('<path d="M1100 1600 L860 1252 Q828 1200 778 1220 L716 1252 L880 1640Z"/>', "#3a4a70", "#283654", "#506292", 20, 0, 7)
    b += cel('<path d="M860 1252 L778 1220 L770 1260 L850 1300Z"/>', "#f2f2f2", "#cfd0d6", None, 6, 0, 5)
    b += '<path d="M706 1132 L598 1056" stroke="#1d1630" stroke-width="30" stroke-linecap="round"/><path d="M706 1132 L598 1056" stroke="#1e3a8a" stroke-width="20" stroke-linecap="round"/>'
    b += '<path d="M612 1064 L586 1046" stroke="#e3b341" stroke-width="12" stroke-linecap="round"/><path d="M690 1118 L660 1098" stroke="#e3b341" stroke-width="6"/>'
    b += cel('<path d="M678 1152 Q688 1098 742 1098 L824 1130 Q864 1162 842 1222 L780 1252 Q718 1252 688 1212Z"/>', SK, SKS, None, 10, -8, 7)
    b += cel('<path d="M702 1118 Q668 1096 656 1120 Q662 1142 702 1152Z"/>', SK, SKS, None, 4, -2, 6)
    b += '<path d="M740 1170 L800 1190 M736 1196 L792 1214" stroke="#d8996f" stroke-width="5"/>'
    return svg(1080, 1920, b, grain=False)

def caja():
    b = '<ellipse cx="560" cy="1040" rx="470" ry="40" fill="#000" opacity="0.4"/>'
    b += cel('<rect x="130" y="190" width="820" height="820" rx="34"/>', "#6c7782", "#4c5660", "#8994a0", -40, -20, 10)
    b += '<rect x="186" y="246" width="708" height="708" rx="18" fill="#15181f" stroke="#1d1630" stroke-width="8"/>'
    b += '<rect x="186" y="246" width="708" height="708" rx="18" fill="#ffd27a" opacity="0.07"/>'
    b += '<path d="M186 246 L894 246 L780 330 L300 330Z" fill="#000" opacity="0.35"/>'
    for (x, y) in ((160, 220), (920, 220), (160, 980), (920, 980)): b += f'<circle cx="{x}" cy="{y}" r="9" fill="#a8b2bc" stroke="#1d1630" stroke-width="3"/>'
    # puerta abierta
    b += cel('<path d="M948 210 L1066 150 L1066 1060 L948 1000Z"/>', "#7a8590", "#5a646e", None, -10, 0, 8)
    b += cel('<circle cx="1008" cy="600" r="46"/>', "#aab4be", "#838d97", None, -8, -6, 6)
    for k in range(12): b += f'<line x1="1008" y1="600" x2="{1008+40*__import__("math").cos(k*0.5236)}" y2="{600+40*__import__("math").sin(k*0.5236)}" stroke="#5a646e" stroke-width="3"/>'
    b += '<rect x="186" y="640" width="708" height="18" fill="#3a3f48"/>'
    for i, x in enumerate((262, 300, 340)):
        b += cel(f'<rect x="{x}" y="{552-i*10}" width="210" height="96" rx="8" transform="rotate({-8+i*6} {x+105} 600)"/>', "#86c084", "#5f9a5d", None, -10, -4, 5)
        b += f'<circle cx="{x+105}" cy="{600-i*10}" r="24" fill="none" stroke="#4f8a4d" stroke-width="4" transform="rotate({-8+i*6} {x+105} 600)"/>'
    b += cel('<circle cx="640" cy="616" r="24"/>', "#e8bf4a", "#b38e2a", None, -5, -3, 4) + cel('<circle cx="684" cy="622" r="20"/>', "#d0d0d6", "#a0a0a8", None, -5, -3, 4)
    # bocadillo viejo
    b += cel('<path d="M520 900 Q520 818 700 818 Q866 818 866 900Z"/>', "#d9a35c", "#a8783a", "#ecc282", -20, -10, 6)
    b += cel('<path d="M520 900 L866 900 L856 934 L530 934Z"/>', "#c98a42", "#9a6a2a", None, -10, 0, 6)
    b += '<path d="M540 900 Q600 878 700 906 Q780 884 846 900" stroke="#5a8a3a" stroke-width="12" fill="none"/>'
    for (x, y, r_) in ((600, 852, 12), (760, 846, 14), (690, 870, 8)): b += f'<circle cx="{x}" cy="{y}" r="{r_}" fill="#6a8a3a" opacity="0.85"/>'
    b += '<path d="M700 800 q10 -20 0 -40 M740 805 q12 -22 0 -44" stroke="#9ab070" stroke-width="5" fill="none" opacity="0.7"/>'
    # sobre
    b += '<g transform="rotate(5 380 840)">' + cel('<rect x="226" y="754" width="310" height="186" rx="8"/>', "#f4e8c9", "#d6c79f", None, -10, -6, 6)
    b += '<path d="M226 754 L381 862 L536 754" fill="none" stroke="#1d1630" stroke-width="6"/>'
    b += cel('<circle cx="381" cy="862" r="24"/>', "#b02a2a", "#7a1a1a", None, -5, -3, 4) + '</g>'
    return svg(1080, 1100, b, grain=False)

def carta():
    b = '<g filter="url(#drop)" transform="rotate(-3 540 700)">'
    b += cel('<rect x="140" y="160" width="800" height="1080" rx="8"/>', "#f5ecd3", "#e2d4ae", None, -16, -10, 8)
    b += '</g><g transform="rotate(-3 540 700)">'
    b += '<rect x="140" y="160" width="800" height="1080" fill="#c9a86a" opacity="0.10" filter="url(#tex)"/>'
    for i in range(14): b += f'<line x1="200" y1="{330+i*62}" x2="880" y2="{330+i*62}" stroke="#b9c7d9" stroke-width="3"/>'
    b += '<line x1="240" y1="180" x2="240" y2="1220" stroke="#e8a0a0" stroke-width="3"/>'
    b += '<ellipse cx="760" cy="1100" rx="90" ry="60" fill="#a07a3a" opacity="0.15"/>'
    b += '</g>'
    return svg(1080, 1400, b, grain=False)

def coche():
    b = '<ellipse cx="540" cy="512" rx="500" ry="28" fill="#000" opacity="0.45"/>'
    body = '<path d="M50 384 Q60 300 180 288 L300 196 Q342 166 424 166 L702 166 Q786 168 836 238 L908 298 Q1012 310 1024 384 L1024 448 L50 448Z"/>'
    b += cel(body, "#1c1d26", "#0d0e14", "#3a3c4c", -20, -18, 8)
    b += '<path d="M330 212 L420 190 L560 190 L560 290 L246 290Z" fill="#2f4361"/><path d="M590 190 L692 190 Q764 196 806 286 L590 290Z" fill="#2f4361"/>'
    b += '<path d="M360 206 L404 200 L330 286 L298 286Z" fill="#fff" opacity="0.25"/><path d="M620 196 L660 196 L620 286 L596 286Z" fill="#fff" opacity="0.18"/>'
    b += '<path d="M120 330 Q540 300 980 330" stroke="#fff" stroke-opacity="0.18" stroke-width="7" fill="none"/>'
    b += '<path d="M570 300 L570 440" stroke="#0a0a10" stroke-width="5"/><rect x="480" y="320" width="40" height="10" rx="4" fill="#9aa0aa"/><rect x="640" y="320" width="40" height="10" rx="4" fill="#9aa0aa"/>'
    b += '<rect x="70" y="350" width="70" height="28" rx="10" fill="#fff0b0" stroke="#1d1630" stroke-width="4"/><rect x="950" y="350" width="58" height="28" rx="8" fill="#d43a3a" stroke="#1d1630" stroke-width="4"/>'
    b += '<rect x="60" y="410" width="980" height="22" rx="10" fill="#2a2b36"/>'
    for x in (240, 810):
        b += f'<circle cx="{x}" cy="448" r="84" fill="#0b0b10" stroke="#1d1630" stroke-width="8"/><circle cx="{x}" cy="448" r="46" fill="#a9b0ba" stroke="#1d1630" stroke-width="5"/>'
        for k in range(5):
            import math
            a = k * 1.2566
            b += f'<line x1="{x}" y1="448" x2="{x+40*math.cos(a)}" y2="{448+40*math.sin(a)}" stroke="#6a707a" stroke-width="7"/>'
        b += f'<circle cx="{x}" cy="448" r="10" fill="#2a2b36"/>'
    b += '<path d="M40 380 L-60 330 L-60 430Z" fill="#fff0b0" opacity="0.18"/>'
    return svg(1080, 560, b, grain=False)


def escudo():
    b = '<g filter="url(#drop)">'
    shield = '<path d="M60 40 L540 40 L540 330 Q540 560 300 680 Q60 560 60 330Z"/>'
    b += cel(shield, "#1f5aa8", "#174486", "#2f74c8", -40, -14, 12)
    b += '</g>'
    i = uid()
    b += f'<clipPath id="{i}">{shield}</clipPath><g clip-path="url(#{i})">'
    for k in range(5):
        b += f'<rect x="{90 + k*96}" y="40" width="48" height="700" fill="#f2efe6" opacity="0.92"/>'
    b += '<rect x="60" y="40" width="480" height="150" fill="#16386e"/>'
    b += '<rect x="60" y="40" width="480" height="700" fill="#5a4a3a" opacity="0.18"/>'
    b += '<path d="M300 120 L330 220 L300 300 L350 420 L320 520" stroke="#1d1630" stroke-width="7" fill="none" opacity="0.7"/>'
    b += '</g>'
    b += '<text x="300" y="150" font-family="Anton" font-size="96" text-anchor="middle" fill="#f2c94c" stroke="#1d1630" stroke-width="4">C.D.</text>'
    b += cel('<circle cx="300" cy="380" r="95"/>', "#f6f4ee", "#d0cbbf", None, -16, -8, 8)
    for (x, y) in ((300, 340), (255, 400), (345, 400), (300, 440)):
        b += f'<path d="M{x-22} {y-8} L{x} {y-24} L{x+22} {y-8} L{x+14} {y+16} L{x-14} {y+16}Z" fill="#1d1630"/>'
    b += cel('<path d="M0 560 L600 560 L570 640 L600 720 L0 720 L30 640Z"/>', "#c0392b", "#8f2a20", None, -10, -6, 8)
    b += '<text x="300" y="665" font-family="Anton" font-size="78" text-anchor="middle" fill="#f6f4ee">SAN LORENZO</text>'
    b += '<text x="300" y="790" font-family="Anton" font-size="70" text-anchor="middle" fill="#f2c94c" stroke="#1d1630" stroke-width="3">1931</text>'
    return svg(600, 820, b)

LAYERS = {"escudo": escudo, "bg_notaria": bg_notaria, "bg_dark": bg_dark, "bg_campo": bg_campo, "hierba": hierba, "bg_vestuario": bg_vestuario,
          "bg_puerta": bg_puerta, "baldosas": baldosas, "paco": paco, "arturo": arturo, "abuelo_foto": abuelo_foto,
          "cabra": cabra, "ramon": lambda: jugador("ramon"), "josito": lambda: jugador("josito"), "primo": lambda: jugador("primo"),
          "manos": manos, "caja": caja, "carta": carta, "coche": coche}

FONT_CSS = "@font-face{font-family:Anton;src:url(file://%s/fonts/Anton-Regular.ttf)}" % HERE

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
            pg.goto("file://" + hp); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(100)
            pg.screenshot(path=os.path.join(OUT, name + ".png"), omit_background=True)
            pg.close(); print("ok", name, flush=True)
        br.close()
