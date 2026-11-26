"""Estilo 2 (cómic nocturno, detallado) para «30 días sin celular». Mismos nombres y tamaños de capa que art_v1.
Vale es peculiar: lápiz clavado en el moño, un ojo más grande que el otro, curita en la nariz, brackets, uñas turquesa
despintadas, tres aretes y un parche en la sudadera. Uso: python3 art_v2.py"""
import os, re, random, math, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "mateo30")); sys.path.insert(0, HERE)
import art30 as B
from playwright.sync_api import sync_playwright
FONT_CSS = B.A.FONT_CSS
OL = "#160f2c"; SK = "#f3c9a8"; SKS = "#d9a383"; SKL = "#fbe0c8"; HAIR = "#3d2a7a"; HAIRS = "#2a1b5c"; TUR = "#2bd4c4"; HOOD = "#f5bf2e"; HOODS = "#d79c14"; HOODL = "#ffd968"
PAPER = "#fff6dc"; TINTA = "#2a3b8f"; ROSA = "#ff5d73"
ST = f'stroke="{OL}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"'
def svg(w, h, body): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>'

# ---------------------------------------------------------------- la nota
def nota(w=420, h=330, texto="x", seed=3):
    r = random.Random(seed); top = " ".join(f"L{x} {r.uniform(0, 14):.0f}" for x in range(20, w, 22))
    b = f'<path d="M8 20 {top} L{w + 8} 18 L{w + 8} {h + 12} L8 {h + 12}Z" fill="#000" opacity=".28"/>'
    b += f'<path d="M0 8 {top} L{w} 6 L{w} {h} L0 {h}Z" fill="{PAPER}" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
    b += f'<path d="M{w * .62} 6 L{w} 6 L{w} {h} L{w * .8} {h}Z" fill="#e8d9b0" opacity=".35"/>'
    for y in range(70, h - 16, 52): b += f'<path d="M6 {y} L{w - 6} {y}" stroke="#9cc7ee" stroke-width="3.5"/>'
    b += f'<path d="M58 12 L58 {h - 4}" stroke="#f08a8a" stroke-width="3.5"/>'
    for y in range(60, h - 20, 90): b += f'<circle cx="28" cy="{y}" r="11" fill="#1d1640"/><circle cx="28" cy="{y}" r="11" fill="none" stroke="{OL}" stroke-width="4"/>'
    b += f'<circle cx="{w - 70}" cy="{h - 60}" r="34" fill="none" stroke="#b98a52" stroke-width="7" opacity=".35"/>'
    if texto:
        from nota_spec import NOTA
        for g, x, y, sz, rot in NOTA: b += f'<text x="{x}" y="{y}" font-family="Caveat" font-weight="700" font-size="{sz}" fill="{TINTA}" transform="rotate({rot} {x} {y})">{g}</text>'
        b += f'<circle cx="120" cy="290" r="9" fill="{TINTA}" opacity=".5"/>'
    b += f'<g transform="rotate(-4 {w / 2} 6)"><rect x="{w / 2 - 74}" y="-18" width="148" height="46" fill="#ffe27a" fill-opacity=".88" stroke="{OL}" stroke-width="4"/><path d="M{w / 2 - 60} -6 l120 0 M{w / 2 - 60} 8 l120 0" stroke="#fff" stroke-width="4" opacity=".5"/></g>'
    return b

# ---------------------------------------------------------------- Vale
def ojo(cx, cy, r, mir, parp, uid):
    b = f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r * 1.12}" fill="#fff" {ST}/>'
    ir = r * (.56 if parp > .05 else .44)
    b += f'<clipPath id="e{uid}"><ellipse cx="{cx}" cy="{cy}" rx="{r - 3}" ry="{r * 1.12 - 3}"/></clipPath><g clip-path="url(#e{uid})">'
    b += f'<circle cx="{cx + mir[0]}" cy="{cy + mir[1]}" r="{ir}" fill="#17988c"/><circle cx="{cx + mir[0]}" cy="{cy + mir[1] + 3}" r="{ir * .8}" fill="#2bd4c4"/><circle cx="{cx + mir[0]}" cy="{cy + mir[1]}" r="{ir * .45}" fill="{OL}"/>'
    b += f'<circle cx="{cx + mir[0] - ir * .4}" cy="{cy + mir[1] - ir * .45}" r="{ir * .26}" fill="#fff"/><circle cx="{cx + mir[0] + ir * .4}" cy="{cy + mir[1] + ir * .4}" r="{ir * .12}" fill="#fff" opacity=".8"/>'
    b += f'<ellipse cx="{cx}" cy="{cy - r * 1.05}" rx="{r}" ry="{r * .5}" fill="#b9a8d8" opacity=".35"/>'
    if parp > .05:
        yp = cy - r * 1.12 + r * 2.24 * parp
        b += f'<rect x="{cx - r - 4}" y="{cy - r * 1.3}" width="{2 * r + 8}" height="{yp - cy + r * 1.3}" fill="{SKS}"/><path d="M{cx - r} {yp} Q{cx} {yp + r * .2} {cx + r} {yp}" stroke="{OL}" stroke-width="8" fill="none"/>'
    b += '</g>'
    b += f'<path d="M{cx + r * .86} {cy - r * .62} l14 -14 M{cx + r * 1.0} {cy - r * .22} l17 -7 M{cx - r * .9} {cy - r * .6} l-12 -13" stroke="{OL}" stroke-width="5" stroke-linecap="round"/>'
    b += f'<path d="M{cx - r * .8} {cy + r * 1.5} Q{cx} {cy + r * 1.8} {cx + r * .8} {cy + r * 1.5}" stroke="#a97fd0" stroke-width="7" fill="none" stroke-linecap="round" opacity=".75"/>'
    return b

CEJ = {"aburrida": ((-14, 8), (-30, -14)), "shock": ((-52, -52), (-52, -52)), "asco": ((6, -6), (-36, 0)), "orgullosa": ((-24, -24), (-24, -24)), "enojada": ((-40, 14), (14, -40))}
PARP = {"aburrida": .44, "shock": 0, "asco": .36, "orgullosa": .24, "enojada": .2}
MIR = {"aburrida": (0, 8), "shock": (0, 0), "asco": (-16, 12), "orgullosa": (0, 5), "enojada": (0, 3)}
def brackets(x0, x1, y):
    b = f'<path d="M{x0} {y} L{x1} {y}" stroke="#aab3c8" stroke-width="4"/>'
    for x in range(int(x0 + 8), int(x1), 20): b += f'<rect x="{x - 5}" y="{y - 6}" width="10" height="12" rx="2" fill="#dfe5f2" stroke="#7d86a0" stroke-width="2"/>'
    return b
def boca(kind, hab):
    cx, y = 400, 610
    if kind == "shock" or (kind == "enojada" and hab):
        ry = 60 if hab else 52
        return (f'<ellipse cx="{cx}" cy="{y}" rx="56" ry="{ry}" fill="#6a1836" {ST}/><path d="M{cx - 36} {y + ry * .5} Q{cx} {y + ry * 1.0} {cx + 36} {y + ry * .5} Q{cx} {y + ry * .1} {cx - 36} {y + ry * .5}Z" fill="#ff7b8a"/>'
                f'<path d="M{cx - 40} {y - ry * .72} Q{cx} {y - ry * 1.02} {cx + 40} {y - ry * .72} L{cx + 36} {y - ry * .44} L{cx - 36} {y - ry * .44}Z" fill="#fff"/>' + brackets(cx - 34, cx + 36, y - ry * .6))
    if kind == "enojada": return f'<path d="M{cx - 62} {y + 22} Q{cx} {y - 30} {cx + 62} {y + 22}" stroke="{OL}" stroke-width="11" fill="none" stroke-linecap="round"/><path d="M{cx - 70} {y + 30} l-8 12 M{cx + 70} {y + 30} l8 12" stroke="{OL}" stroke-width="6" stroke-linecap="round"/>'
    if kind == "orgullosa":
        if hab: return f'<path d="M{cx - 66} {y - 18} Q{cx} {y + 74} {cx + 66} {y - 18}Z" fill="#6a1836" {ST}/><path d="M{cx - 56} {y - 14} L{cx + 56} {y - 14} L{cx + 46} {y + 8} L{cx - 46} {y + 8}Z" fill="#fff"/>' + brackets(cx - 46, cx + 48, y - 2) + f'<path d="M{cx - 26} {y + 36} Q{cx} {y + 20} {cx + 26} {y + 36} Q{cx} {y + 56} {cx - 26} {y + 36}Z" fill="#ff7b8a"/>'
        return f'<path d="M{cx - 66} {y - 14} Q{cx} {y + 52} {cx + 66} {y - 14}" fill="#fff" {ST}/><path d="M{cx - 66} {y - 14} L{cx + 66} {y - 14}" stroke="{OL}" stroke-width="7"/>' + brackets(cx - 50, cx + 52, y + 4)
    if hab: return f'<ellipse cx="{cx + 4}" cy="{y + 4}" rx="40" ry="28" fill="#6a1836" {ST}/><path d="M{cx - 24} {y - 10} L{cx + 30} {y - 10} L{cx + 24} {y + 2} L{cx - 18} {y + 2}Z" fill="#fff"/>' + brackets(cx - 20, cx + 28, y - 4)
    if kind == "asco": return f'<path d="M{cx - 60} {y + 18} Q{cx - 24} {y - 16} {cx + 10} {y + 8} Q{cx + 36} {y + 26} {cx + 62} {y - 8}" stroke="{OL}" stroke-width="11" fill="none" stroke-linecap="round"/><path d="M{cx + 30} {y + 26} q10 18 24 6" stroke="{OL}" stroke-width="6" fill="none" stroke-linecap="round"/>'
    return f'<path d="M{cx - 60} {y + 4} Q{cx - 6} {y - 24} {cx + 62} {y + 16}" stroke="{OL}" stroke-width="11" fill="none" stroke-linecap="round"/>'

def mano(hx, hy, s=1.0, flip=1, rot=0, dedos=4):
    """Mano con dedos, nudillos y uñas turquesa despintadas."""
    b = f'<g transform="translate({hx},{hy}) rotate({rot}) scale({flip * s},{s})"><path d="M-62 10 Q-70 -40 -30 -52 L40 -52 Q70 -40 62 14 Q56 60 0 62 Q-54 60 -62 10Z" fill="{SK}" {ST}/>'
    for i in range(dedos):
        x = -52 + i * 28; h = (78, 92, 88, 70)[i]
        b += f'<rect x="{x}" y="{-40 - h}" width="25" height="{h + 14}" rx="12" fill="{SK}" {ST}/><rect x="{x + 5}" y="{-36 - h}" width="15" height="{16 if i != 2 else 9}" rx="6" fill="{TUR}" opacity=".95"/><path d="M{x + 5} {-52} q8 5 15 0" stroke="{SKS}" stroke-width="4" fill="none"/>'
    b += f'<path d="M-58 0 Q-96 -6 -92 -44 Q-74 -52 -62 -30Z" fill="{SK}" {ST}/><path d="M-30 20 q30 14 62 -4" stroke="{SKS}" stroke-width="5" fill="none" stroke-linecap="round"/></g>'
    return b

def vale(kind="aburrida", hab=False, pose="quieta", uid="v"):
    b = '<defs><linearGradient id="hd" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffd968"/><stop offset=".45" stop-color="#f5bf2e"/><stop offset="1" stop-color="#c98a0c"/></linearGradient>'
    b += '<linearGradient id="hr" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5a3fa8"/><stop offset=".5" stop-color="#3d2a7a"/><stop offset="1" stop-color="#22154e"/></linearGradient></defs>'
    # melena por detrás
    b += f'<path d="M196 330 Q130 620 172 900 Q210 950 250 900 Q268 950 300 902 L520 902 Q548 952 570 900 Q606 952 640 892 Q676 620 604 330Z" fill="url(#hr)" {ST}/>'
    for x in (220, 270, 560, 610): b += f'<path d="M{x} 520 Q{x - 14} 720 {x + 6} 880" stroke="{HAIRS}" stroke-width="6" fill="none" opacity=".8"/>'
    # moño ladeado con lápiz y coletero
    b += f'<g transform="rotate(14 470 150)"><rect x="300" y="128" width="330" height="26" rx="4" fill="#ffc93c" {ST}/><rect x="300" y="128" width="46" height="26" rx="4" fill="#ff8fa3" {ST}/><rect x="346" y="128" width="16" height="26" fill="#c9d3e6" stroke="{OL}" stroke-width="5"/><path d="M630 128 L676 141 L630 154Z" fill="#f3d9b0" {ST}/><path d="M660 136.500 L676 141 L660 145.500Z" fill="{OL}"/><path d="M380 141 L610 141" stroke="#e0a51f" stroke-width="5"/></g>'
    b += f'<circle cx="462" cy="160" r="112" fill="url(#hr)" {ST}/><path d="M392 120 Q450 60 530 110 M380 180 Q460 130 548 176 M410 232 Q470 196 530 232" stroke="{HAIRS}" stroke-width="7" fill="none" stroke-linecap="round"/><path d="M400 100 Q440 64 492 74" stroke="#7d63c8" stroke-width="9" fill="none" stroke-linecap="round"/>'
    b += f'<path d="M372 250 Q462 214 556 250 L550 286 Q462 252 378 286Z" fill="{TUR}" {ST}/><path d="M400 262 l14 -12 M440 252 l14 -10 M486 250 l14 -8 M526 256 l10 -8" stroke="#17988c" stroke-width="5" stroke-linecap="round"/>'
    # brazos según pose (detrás del torso)
    if pose == "quieta":
        for sx in (1, -1): b += f'<g transform="translate(400,0) scale({sx},1)"><path d="M-262 830 Q-350 980 -330 1310 L-226 1310 Q-240 1040 -196 900Z" fill="url(#hd)" {ST}/><path d="M-300 1000 q30 30 60 10 M-310 1120 q34 24 70 6" stroke="{HOODS}" stroke-width="7" fill="none" stroke-linecap="round"/></g>'
    if pose == "manos":
        for sx in (1, -1): b += f'<g transform="translate(400,0) scale({sx},1)"><path d="M-250 900 Q-430 760 -330 440 L-236 470 Q-290 700 -180 830Z" fill="url(#hd)" {ST}/><path d="M-330 640 q34 4 60 -18 M-300 560 q30 6 54 -14" stroke="{HOODS}" stroke-width="7" fill="none" stroke-linecap="round"/><path d="M-340 452 L-232 482 L-240 440 L-328 414Z" fill="{HOODS}" {ST}/></g>'
    # capucha detrás del cuello y torso
    b += f'<path d="M210 800 Q200 690 300 680 L500 680 Q600 690 590 800 Q400 860 210 800Z" fill="{HOODS}" {ST}/>'
    b += f'<path d="M96 1310 Q70 880 190 800 Q300 760 400 772 Q500 760 610 800 Q730 880 704 1310Z" fill="url(#hd)" {ST}/>'
    b += f'<path d="M520 790 Q690 860 704 1310 L560 1310 Q600 1000 520 790Z" fill="#000" opacity=".13"/>'
    b += f'<path d="M256 792 Q400 930 544 792 Q470 756 400 760 Q330 756 256 792Z" fill="{HOODS}" {ST}/><path d="M290 800 Q400 890 510 800" stroke="#b47d08" stroke-width="6" fill="none"/>'
    b += f'<path d="M352 860 L340 1010" stroke="#fff6dc" stroke-width="12" stroke-linecap="round"/><path d="M448 860 L462 1026" stroke="#fff6dc" stroke-width="12" stroke-linecap="round"/><rect x="330" y="1004" width="20" height="34" rx="6" fill="#c9d3e6" {ST}/><rect x="452" y="1020" width="20" height="34" rx="6" fill="#c9d3e6" {ST}/>'
    b += f'<path d="M300 1130 L500 1130 Q520 1130 524 1150 L548 1260 L252 1260 L276 1150 Q280 1130 300 1130Z" fill="{HOODS}" {ST}/><path d="M290 1150 L510 1150" stroke="#b47d08" stroke-width="5" stroke-dasharray="14 10"/>'
    b += f'<g transform="rotate(-8 590 960)"><circle cx="590" cy="960" r="44" fill="#ff5d73" {ST}/><circle cx="590" cy="960" r="34" fill="none" stroke="#fff6dc" stroke-width="4" stroke-dasharray="8 7"/><path d="M572 952 l10 0 M600 952 l10 0 M572 972 Q590 990 608 972" stroke="{OL}" stroke-width="6" fill="none" stroke-linecap="round"/><path d="M566 936 l50 50" stroke="{OL}" stroke-width="6" stroke-linecap="round"/></g>'
    b += f'<path d="M150 1000 q30 60 10 160 M650 980 q-36 70 -14 190 M200 880 q40 30 80 20" stroke="{HOODS}" stroke-width="8" fill="none" stroke-linecap="round"/><path d="M130 940 Q150 840 220 812" stroke="{TUR}" stroke-width="8" fill="none" stroke-linecap="round" opacity=".7"/>'
    # cuello
    b += f'<path d="M350 610 L350 760 Q400 800 450 760 L450 610Z" fill="{SKS}" {ST}/><path d="M350 690 Q400 730 450 690 L450 640 L350 640Z" fill="#000" opacity=".14"/>'
    # cabeza
    b += f'<path d="M196 430 Q190 210 400 206 Q610 210 604 430 Q600 580 500 650 Q400 706 300 650 Q200 580 196 430Z" fill="{SK}" {ST}/>'
    b += f'<path d="M470 212 Q612 240 604 430 Q600 580 500 650 Q440 684 400 680 Q520 620 540 470 Q556 300 470 212Z" fill="{SKS}" opacity=".6"/><path d="M214 440 Q210 300 300 240" stroke="{TUR}" stroke-width="7" fill="none" stroke-linecap="round" opacity=".55"/>'
    b += f'<ellipse cx="194" cy="450" rx="30" ry="46" fill="{SK}" {ST}/><ellipse cx="606" cy="450" rx="30" ry="46" fill="{SKS}" {ST}/><path d="M186 432 q14 16 4 36" stroke="{SKS}" stroke-width="5" fill="none"/>'
    for i, (x, y, r) in enumerate(((620, 430, 9), (628, 462, 11), (618, 498, 15))): b += f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{TUR if i != 1 else "#ffc93c"}" stroke-width="6"/>'
    b += f'<ellipse cx="276" cy="560" rx="44" ry="26" fill="#ff8fa3" opacity=".4"/><ellipse cx="524" cy="560" rx="44" ry="26" fill="#ff8fa3" opacity=".35"/>'
    # flequillo asimétrico + mechón
    b += f'<path d="M190 446 Q160 190 400 186 Q640 190 610 446 Q596 330 520 286 Q530 356 452 330 Q468 270 400 258 Q330 300 318 392 Q270 400 250 340 Q210 360 190 446Z" fill="url(#hr)" {ST}/>'
    b += f'<path d="M300 230 Q350 300 322 384 M362 222 Q392 262 388 262 M250 270 Q262 310 252 336" stroke="{HAIRS}" stroke-width="6" fill="none" stroke-linecap="round"/>'
    b += f'<path d="M474 206 Q566 240 588 340 L556 330 Q548 262 474 236Z" fill="{TUR}" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/><path d="M240 250 Q300 200 380 204" stroke="#7d63c8" stroke-width="8" fill="none" stroke-linecap="round"/>'
    # ojos (el izquierdo más grande: es su rasgo)
    b += ojo(298, 462, 60, MIR[kind], PARP[kind], uid + "a") + ojo(502, 468, 47, MIR[kind], PARP[kind], uid + "b")
    (a1, a2), (b1, b2) = CEJ[kind]
    b += f'<path d="M232 {372 + a1} Q298 {340 + (a1 + a2) / 2 - 16} 364 {372 + a2}" stroke="{OL}" stroke-width="19" fill="none" stroke-linecap="round"/><path d="M440 {388 + b1} Q500 {360 + (b1 + b2) / 2 - 14} 560 {388 + b2}" stroke="{OL}" stroke-width="19" fill="none" stroke-linecap="round"/>'
    b += f'<path d="M528 {360 + (b1 + b2) / 2} l10 34" stroke="{SK}" stroke-width="8" stroke-linecap="round"/>'
    # nariz con curita
    b += f'<path d="M388 520 Q400 544 418 522" stroke="{OL}" stroke-width="7" fill="none" stroke-linecap="round"/><g transform="rotate(-12 402 494)"><rect x="352" y="480" width="100" height="30" rx="14" fill="#f7b79a" stroke="{OL}" stroke-width="5"/><rect x="384" y="480" width="36" height="30" fill="#fbd3bd"/><circle cx="364" cy="495" r="2.500" fill="#c98466"/><circle cx="372" cy="489" r="2.500" fill="#c98466"/><circle cx="436" cy="495" r="2.500" fill="#c98466"/><circle cx="444" cy="501" r="2.500" fill="#c98466"/></g>'
    for x, y in ((238, 540), (262, 556), (246, 576), (284, 532), (538, 552), (560, 538), (548, 576), (514, 536)): b += f'<circle cx="{x}" cy="{y}" r="6" fill="#c98466"/>'
    b += boca(kind, hab)
    # manos / objetos por delante
    if pose == "nota":
        b += f'<g transform="translate(190,850) rotate(-5)">{nota()}</g>'
        b += f'<path d="M96 1310 Q76 1060 160 1050 L246 1080 L250 1310Z" fill="url(#hd)" {ST}/><path d="M704 1310 Q724 1060 650 1050 L566 1080 L560 1310Z" fill="url(#hd)" {ST}/>'
        b += mano(176, 1070, .9, 1, -8) + mano(636, 1070, .9, -1, 8)
    elif pose == "manos":
        b += mano(128, 372, 1.0, 1, 38) + mano(672, 372, 1.0, -1, -38)
    elif pose == "senala":
        b += f'<path d="M550 930 Q680 880 740 990 L672 1066 Q620 1010 530 1040Z" fill="url(#hd)" {ST}/><path d="M650 1050 L742 990 L750 1024 L676 1080Z" fill="{HOODS}" {ST}/>'
        # mano que señala A LA CÁMARA: puño de frente y la yema del índice en primer plano
        b += f'<g transform="translate(690,1060)"><path d="M-84 0 Q-90 -70 -20 -78 L40 -76 Q92 -60 86 10 Q78 84 0 88 Q-76 84 -84 0Z" fill="{SK}" {ST}/>'
        b += f'<path d="M-60 34 q30 -16 60 0 M-66 62 q34 -12 70 2" stroke="{SKS}" stroke-width="6" fill="none" stroke-linecap="round"/><path d="M-78 -20 Q-118 -30 -112 -70 Q-90 -80 -76 -52Z" fill="{SK}" {ST}/>'
        b += f'<circle cx="10" cy="-18" r="50" fill="{SKL}" {ST}/><path d="M-22 -34 Q10 -66 42 -34 Q10 -44 -22 -34Z" fill="{TUR}" stroke="{OL}" stroke-width="4"/><path d="M-14 0 q24 16 48 0" stroke="{SKS}" stroke-width="5" fill="none" stroke-linecap="round"/>'
        b += f'<path d="M-96 -110 l-22 -26 M10 -120 l0 -36 M110 -100 l24 -26" stroke="#fff6dc" stroke-width="9" stroke-linecap="round"/></g>'
        b += f'<path d="M134 880 Q60 1010 82 1310 L186 1310 Q170 1040 206 910Z" fill="url(#hd)" {ST}/>'
    return svg(800, 1300, b)

# ---------------------------------------------------------------- otros personajes
def cabeza(quien):
    skin, sks = {"nico": (SK, SKS), "dani": ("#e2ab82", "#c48a60"), "renata": ("#b9794e", "#96592f")}[quien]; col, cols = {"nico": ("#2bd4c4", "#17988c"), "dani": ("#ff5d73", "#c93a52"), "renata": ("#b98ad6", "#8e5fb5")}[quien]; b = ""
    if quien == "renata":
        for cx, cy, r in ((170, 300, 120), (260, 180, 128), (400, 140, 136), (540, 180, 128), (630, 300, 120)): b += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#24140c" {ST}/>'
        for cx, cy in ((230, 200), (330, 130), (470, 120), (570, 210), (180, 310), (620, 320)): b += f'<path d="M{cx - 30} {cy} q30 -30 60 0" stroke="#4a2c1a" stroke-width="7" fill="none" stroke-linecap="round"/>'
    b += f'<path d="M110 1010 Q96 830 240 790 Q400 760 560 790 Q704 830 690 1010Z" fill="{col}" {ST}/><path d="M540 790 Q700 840 690 1010 L570 1010 Q600 880 540 790Z" fill="#000" opacity=".15"/>'
    if quien == "dani": b += f'<path d="M250 800 Q400 900 550 800" stroke="#16122a" stroke-width="30" fill="none" stroke-linecap="round"/><rect x="214" y="760" width="60" height="96" rx="24" fill="#22203a" {ST}/><rect x="526" y="760" width="60" height="96" rx="24" fill="#22203a" {ST}/>'
    if quien == "nico": b += f'<text x="400" y="960" text-anchor="middle" font-family="Anton" font-size="84" fill="#fff6dc" stroke="{OL}" stroke-width="5">GG</text>'
    if quien == "renata": b += f'<path d="M300 800 Q400 880 500 800" stroke="{cols}" stroke-width="10" fill="none"/><circle cx="400" cy="900" r="22" fill="#ffc93c" {ST}/>'
    b += f'<path d="M352 640 L352 790 Q400 820 448 790 L448 640Z" fill="{sks}" {ST}/>'
    b += f'<path d="M190 430 Q186 220 400 216 Q614 220 610 430 Q606 590 510 664 Q400 720 290 664 Q194 590 190 430Z" fill="{skin}" {ST}/><path d="M480 224 Q616 250 610 430 Q606 590 510 664 Q450 694 410 692 Q526 630 546 480 Q560 310 480 224Z" fill="{sks}" opacity=".6"/>'
    b += f'<ellipse cx="188" cy="458" rx="30" ry="46" fill="{skin}" {ST}/><ellipse cx="612" cy="458" rx="30" ry="46" fill="{sks}" {ST}/>'
    if quien == "nico":
        b += f'<path d="M184 400 Q170 190 400 190 Q630 190 616 400 Q500 330 400 336 Q300 330 184 400Z" fill="{ROSA}" {ST}/><path d="M176 392 Q30 400 40 470 Q190 450 330 344Z" fill="#c93a52" {ST}/><circle cx="400" cy="196" r="20" fill="#c93a52" {ST}/><path d="M250 300 Q400 250 550 300" stroke="#c93a52" stroke-width="7" fill="none"/>'
        b += f'<path d="M560 420 q30 30 40 80" stroke="#5a3a22" stroke-width="16" fill="none" stroke-linecap="round"/><g transform="rotate(20 250 590)"><rect x="216" y="576" width="72" height="26" rx="12" fill="#f7b79a" stroke="{OL}" stroke-width="5"/></g>'
    elif quien == "dani":
        for cx, cy, r in ((230, 280, 74), (300, 220, 82), (400, 196, 88), (500, 220, 82), (570, 280, 74), (200, 350, 54), (600, 350, 54)): b += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#4a2f1c" {ST}/>'
        for cx, cy in ((290, 220), (400, 180), (510, 230), (240, 300), (560, 300)): b += f'<path d="M{cx - 24} {cy} q24 -26 48 0" stroke="#6e4a2e" stroke-width="7" fill="none" stroke-linecap="round"/>'
    else:
        b += f'<path d="M190 420 Q200 300 300 280 Q400 320 500 280 Q600 300 610 420 Q560 340 400 350 Q240 340 190 420Z" fill="#24140c" {ST}/>'
    for i, cx in enumerate((300, 500)):
        r = 50 if quien != "nico" else 56
        b += f'<ellipse cx="{cx}" cy="470" rx="{r}" ry="{r * 1.1}" fill="#fff" {ST}/><circle cx="{cx}" cy="476" r="{r * .55}" fill="#5a3a22"/><circle cx="{cx}" cy="476" r="{r * .28}" fill="{OL}"/><circle cx="{cx - r * .22}" cy="{476 - r * .25}" r="{r * .16}" fill="#fff"/>'
        b += f'<path d="M{cx - 60} {382 - (10 if quien == "nico" and i else 0)} Q{cx} {352 - (24 if quien == "nico" and i else 0)} {cx + 60} 382" stroke="{OL}" stroke-width="16" fill="none" stroke-linecap="round"/>'
    if quien == "renata":
        b += f'<rect x="226" y="400" width="148" height="140" rx="34" fill="none" stroke="#ff5d73" stroke-width="13"/><rect x="426" y="400" width="148" height="140" rx="34" fill="none" stroke="#ff5d73" stroke-width="13"/><path d="M374 456 L426 456" stroke="#ff5d73" stroke-width="13"/><path d="M246 420 l40 0 M446 420 l40 0" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity=".8"/>'
    b += f'<path d="M388 556 Q402 580 420 558" stroke="{OL}" stroke-width="7" fill="none" stroke-linecap="round"/>'
    for x, y in ((250, 560), (270, 580), (540, 566), (556, 584)): b += f'<circle cx="{x}" cy="{y}" r="5" fill="#00000030"/>'
    if quien == "nico": b += f'<path d="M318 606 Q400 716 482 606Z" fill="#6a1836" {ST}/><rect x="356" y="608" width="34" height="30" rx="4" fill="#fff"/><rect x="424" y="608" width="30" height="24" rx="4" fill="#fff"/><path d="M366 680 Q400 660 434 680 Q400 704 366 680Z" fill="#ff7b8a"/>'
    elif quien == "dani": b += f'<path d="M330 620 Q410 690 474 610" stroke="{OL}" stroke-width="11" fill="none" stroke-linecap="round"/><path d="M470 600 q14 8 10 22" stroke="{OL}" stroke-width="6" fill="none" stroke-linecap="round"/>'
    else: b += f'<path d="M326 610 Q400 690 474 610Z" fill="#fff" {ST}/><path d="M326 610 L474 610" stroke="{OL}" stroke-width="7"/>'
    return svg(800, 1000, b)

# ---------------------------------------------------------------- objetos
def celular():
    b = f'<rect x="28" y="28" width="256" height="476" rx="42" fill="#000" opacity=".3"/><rect x="20" y="16" width="260" height="484" rx="42" fill="#2a2748" {ST}/><rect x="20" y="16" width="260" height="484" rx="42" fill="none" stroke="#5a568a" stroke-width="3" transform="translate(4,4) scale(.972)"/>'
    b += f'<rect x="38" y="42" width="224" height="432" rx="24" fill="#101028"/><rect x="38" y="42" width="224" height="432" rx="24" fill="#3a3760" opacity=".7"/><rect x="112" y="52" width="76" height="18" rx="9" fill="#06060f"/>'
    b += '<path d="M60 60 L150 60 L70 300 L60 300Z" fill="#fff" opacity=".08"/>'
    b += '<path d="M210 60 L186 150 L226 210 L196 290 M186 150 L150 170 M226 210 L250 226" stroke="#c9d3e6" stroke-width="3" fill="none" opacity=".8"/>'       # pantalla rajada
    b += f'<text x="150" y="232" text-anchor="middle" font-family="Anton" font-size="62" fill="#c9d3e6" opacity=".9">23:59</text><rect x="70" y="270" width="160" height="50" rx="14" fill="#fff" opacity=".12"/><circle cx="92" cy="295" r="12" fill="{ROSA}"/><rect x="112" y="288" width="100" height="8" rx="4" fill="#fff" opacity=".5"/><rect x="112" y="302" width="70" height="6" rx="3" fill="#fff" opacity=".3"/>'
    b += f'<rect x="10" y="130" width="12" height="60" rx="5" fill="#2a2748" {ST}/><rect x="278" y="150" width="12" height="90" rx="5" fill="#2a2748" {ST}/>'
    return svg(300, 520, b)
def caja(dias=30):
    b = '<defs><linearGradient id="vd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#d8f4fb" stop-opacity=".75"/><stop offset=".5" stop-color="#9fd4e6" stop-opacity=".42"/><stop offset="1" stop-color="#6fa8c4" stop-opacity=".6"/></linearGradient></defs>'
    b += '<ellipse cx="200" cy="420" rx="190" ry="14" fill="#000" opacity=".35"/>'
    b += f'<rect x="22" y="96" width="356" height="322" rx="26" fill="url(#vd)" {ST}/>'
    b += f'<g transform="rotate(9 210 265)"><rect x="150" y="156" width="118" height="214" rx="18" fill="#2a2748" {ST}/><rect x="162" y="174" width="94" height="170" rx="8" fill="#3a3760"/><path d="M236 180 l-14 50 l22 36" stroke="#c9d3e6" stroke-width="2.500" fill="none"/><rect x="190" y="162" width="38" height="8" rx="4" fill="#06060f"/></g>'
    b += '<path d="M46 132 Q38 250 50 392" stroke="#fff" stroke-width="13" fill="none" stroke-linecap="round" opacity=".75"/><path d="M76 124 L130 124" stroke="#fff" stroke-width="8" stroke-linecap="round" opacity=".6"/><path d="M330 150 L350 380" stroke="#fff" stroke-width="5" opacity=".35"/>'
    b += f'<rect x="2" y="60" width="396" height="68" rx="18" fill="{ROSA}" {ST}/><path d="M16 74 L384 74" stroke="#ff9aa8" stroke-width="6" stroke-linecap="round"/><path d="M2 112 L398 112" stroke="#c93a52" stroke-width="8"/>'
    b += f'<rect x="92" y="0" width="216" height="96" rx="14" fill="#16122a" {ST}/><rect x="104" y="12" width="192" height="62" rx="8" fill="#280a14"/><text x="200" y="64" text-anchor="middle" font-family="Anton" font-size="54" fill="#ff3b4e" letter-spacing="3">{dias} DÍAS</text><circle cx="116" cy="84" r="5" fill="#ff3b4e"/><rect x="250" y="80" width="40" height="8" rx="4" fill="#3a3760"/>'
    b += f'<path d="M166 304 Q166 250 200 250 Q234 250 234 304" fill="none" stroke="{OL}" stroke-width="20"/><path d="M166 304 Q166 250 200 250 Q234 250 234 304" fill="none" stroke="#c9d3e6" stroke-width="9"/>'
    b += f'<rect x="146" y="298" width="108" height="88" rx="14" fill="#ffc93c" {ST}/><rect x="146" y="298" width="108" height="20" rx="10" fill="#ffe27a"/><circle cx="200" cy="336" r="12" fill="{OL}"/><rect x="194" y="338" width="12" height="28" rx="4" fill="{OL}"/>'
    return b
def candado(abierto=False):
    arc = "M88 152 Q88 56 150 56 Q212 56 212 152" if not abierto else "M88 124 Q88 28 150 28 Q212 28 212 124 L212 64"
    b = f'<path d="{arc}" fill="none" stroke="{OL}" stroke-width="46"/><path d="{arc}" fill="none" stroke="#c9d3e6" stroke-width="30"/><path d="{arc}" fill="none" stroke="#fff" stroke-width="7" opacity=".7" transform="translate(-6,-4)"/>'
    b += f'<rect x="48" y="140" width="204" height="174" rx="26" fill="#ffc93c" {ST}/><rect x="48" y="140" width="204" height="36" rx="18" fill="#ffe27a"/><path d="M210 150 Q252 180 252 290 Q250 314 226 314 L190 314 Q230 250 210 150Z" fill="#d79c14" opacity=".8"/>'
    b += f'<circle cx="150" cy="214" r="26" fill="{OL}"/><rect x="138" y="218" width="24" height="62" rx="8" fill="{OL}"/><circle cx="72" cy="290" r="6" fill="#d79c14"/><circle cx="228" cy="164" r="6" fill="#fff6dc"/>'
    return svg(300, 330, b)
def mano_mama():
    b = f'<path d="M270 196 L900 130 L900 350 L270 316Z" fill="#7a4fb5" {ST}/><path d="M270 276 L900 300 L900 350 L270 316Z" fill="#000" opacity=".2"/><path d="M270 196 L330 190 L330 320 L270 316Z" fill="#5a3690" {ST}/>'
    for x in (420, 560, 700): b += f'<circle cx="{x}" cy="{232 + (x % 3) * 8}" r="9" fill="#fff6dc" opacity=".8"/>'
    b += f'<ellipse cx="200" cy="255" rx="122" ry="98" fill="#e2ab82" {ST}/>'
    for i in range(4): b += f'<rect x="{56 + i * 6}" y="{174 + i * 43}" width="134" height="41" rx="20" fill="#e2ab82" {ST}/><rect x="{60 + i * 6}" y="{180 + i * 43}" width="30" height="29" rx="12" fill="#c93a52"/>'
    b += f'<rect x="120" y="212" width="20" height="46" rx="6" fill="#ffc93c" {ST}/><circle cx="130" cy="216" r="9" fill="{TUR}" {ST}/>'
    b += f'<rect x="286" y="190" width="26" height="130" rx="10" fill="#ffc93c" {ST}/>'
    b += f'<rect x="10" y="150" width="130" height="24" rx="8" fill="#c9d3e6" {ST}/><path d="M20 174 l0 16 l14 0 l0 -16 M48 174 l0 22 l12 0 l0 -22" fill="#c9d3e6" {ST}/><circle cx="160" cy="160" r="34" fill="#c9d3e6" {ST}/><circle cx="160" cy="160" r="14" fill="#16122a"/>'
    return svg(900, 480, b)
def mano_pluma():
    """La punta queda en (60, 560) de un lienzo de 700x620."""
    b = f'<path d="M60 560 L350 226" stroke="{OL}" stroke-width="46" stroke-linecap="round"/><path d="M118 494 L350 226" stroke="{TUR}" stroke-width="32" stroke-linecap="round"/><path d="M128 482 L340 238" stroke="#7ff0e4" stroke-width="7" stroke-linecap="round"/>'
    b += f'<path d="M60 560 L118 494" stroke="#c9d3e6" stroke-width="30" stroke-linecap="butt"/><path d="M60 560 L84 532" stroke="#22203a" stroke-width="14" stroke-linecap="round"/><circle cx="60" cy="560" r="5" fill="{TINTA}"/>'
    b += f'<path d="M150 458 L176 480 M166 440 L192 462 M182 422 L208 444" stroke="#17988c" stroke-width="7" stroke-linecap="round"/><path d="M300 268 L372 330" stroke="{OL}" stroke-width="16" stroke-linecap="round"/><path d="M300 268 L372 330" stroke="#c9d3e6" stroke-width="7" stroke-linecap="round"/>'
    b += f'<path d="M372 318 L700 500 L700 620 L430 620 Q340 480 372 318Z" fill="{HOOD}" {ST}/><path d="M392 360 L430 620 L500 620 Q430 480 392 360Z" fill="{HOODS}" opacity=".8"/><path d="M366 312 L420 600" stroke="{HOODS}" stroke-width="22" stroke-linecap="round"/>'
    b += f'<g transform="rotate(-32 300 350)"><path d="M190 330 Q190 270 250 262 L350 262 Q420 280 410 360 Q400 430 300 432 Q200 430 190 330Z" fill="{SK}" {ST}/>'
    for i in range(3): b += f'<rect x="{150 - i * 4}" y="{300 + i * 40}" width="128" height="38" rx="19" fill="{SK}" {ST}/><rect x="{156 - i * 4}" y="{306 + i * 40}" width="{28 if i != 1 else 16}" height="26" rx="10" fill="{TUR}"/><path d="M{236 - i * 4} {304 + i * 40} q8 14 0 30" stroke="{SKS}" stroke-width="5" fill="none"/>'
    b += f'<path d="M250 262 Q210 220 160 250 Q170 290 230 300Z" fill="{SK}" {ST}/><rect x="162" y="252" width="26" height="22" rx="9" fill="{TUR}" transform="rotate(-20 175 263)"/></g>'
    return svg(700, 620, b)
def microondas():
    b = '<defs><linearGradient id="mc" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e3e9f5"/><stop offset="1" stop-color="#9aa6c2"/></linearGradient></defs>'
    b += f'<ellipse cx="360" cy="456" rx="330" ry="12" fill="#000" opacity=".35"/><rect x="10" y="16" width="700" height="430" rx="30" fill="url(#mc)" {ST}/><rect x="60" y="438" width="60" height="18" rx="6" fill="#22203a"/><rect x="600" y="438" width="60" height="18" rx="6" fill="#22203a"/>'
    b += f'<rect x="44" y="52" width="452" height="358" rx="20" fill="#22203a" {ST}/><rect x="64" y="72" width="412" height="318" rx="12" fill="#0e0b20"/>'
    for y in range(86, 386, 14):
        for x in range(78, 470, 14): b += f'<circle cx="{x}" cy="{y}" r="2" fill="#2a2748"/>'
    b += '<ellipse cx="270" cy="350" rx="150" ry="18" fill="#3a3760"/><rect x="230" y="280" width="80" height="66" rx="10" fill="#fff6dc" opacity=".9"/><path d="M250 270 q10 -24 0 -40 M290 270 q10 -24 0 -40" stroke="#fff" stroke-width="5" fill="none" opacity=".5" stroke-linecap="round"/>'
    b += '<circle cx="200" cy="180" r="40" fill="#ffd27a"/><circle cx="340" cy="180" r="40" fill="#ffd27a"/><circle cx="210" cy="188" r="17" fill="#160f2c"/><circle cx="350" cy="188" r="17" fill="#160f2c"/><circle cx="204" cy="180" r="6" fill="#fff"/><circle cx="344" cy="180" r="6" fill="#fff"/><path d="M226 250 Q270 276 314 250" stroke="#ffd27a" stroke-width="9" fill="none" stroke-linecap="round"/>'
    b += '<path d="M70 80 L200 80 L110 384 L70 384Z" fill="#fff" opacity=".07"/>'
    b += f'<rect x="504" y="60" width="18" height="340" rx="8" fill="#c9d3e6" {ST}/><rect x="544" y="64" width="148" height="72" rx="10" fill="#0e0b20" {ST}/><text x="618" y="118" text-anchor="middle" font-family="Anton" font-size="50" fill="#2bd4c4">0:00</text>'
    for i in range(9): b += f'<rect x="{548 + (i % 3) * 50}" y="{158 + (i // 3) * 48}" width="40" height="36" rx="8" fill="#7d86a0" {ST}/>'
    b += f'<circle cx="618" cy="356" r="40" fill="#22203a" {ST}/><path d="M618 356 L640 334" stroke="#fff6dc" stroke-width="8" stroke-linecap="round"/><rect x="30" y="24" width="60" height="18" rx="6" fill="{ROSA}" {ST}/>'
    return svg(720, 470, b)
def boleto():
    b = f'<path d="M18 22 L598 22 L598 108 Q568 136 598 164 L598 258 L18 258 L18 164 Q48 136 18 108Z" fill="#000" opacity=".3"/><path d="M10 10 L590 10 L590 100 Q560 130 590 160 L590 250 L10 250 L10 160 Q40 130 10 100Z" fill="{ROSA}" {ST}/>'
    b += f'<path d="M24 24 L576 24" stroke="#ff9aa8" stroke-width="6" stroke-linecap="round"/><path d="M440 20 L440 240" stroke="{OL}" stroke-width="5" stroke-dasharray="14 12"/><path d="M10 200 L440 200 L440 250 L10 250Z" fill="#c93a52" opacity=".6"/>'
    b += f'<text x="225" y="104" text-anchor="middle" font-family="Anton" font-size="70" fill="#fff6dc" stroke="{OL}" stroke-width="3">CONCIERTO</text><text x="225" y="176" text-anchor="middle" font-family="Anton" font-size="50" fill="#16122a">DEL AÑO ★ FILA 1</text><text x="225" y="236" text-anchor="middle" font-family="Anton" font-size="28" fill="#fff6dc">ENTRADA GENERAL · NO REEMBOLSABLE</text>'
    r = random.Random(2); x = 458
    while x < 572: w = r.choice((3, 5, 8)); b += f'<rect x="{x}" y="40" width="{w}" height="150" fill="{OL}"/>'; x += w + r.choice((3, 5))
    b += f'<text x="516" y="226" text-anchor="middle" font-family="Anton" font-size="30" fill="#fff6dc">VIP</text><circle cx="60" cy="60" r="20" fill="#ffc93c" {ST}/><path d="M50 60 l8 8 l14 -16" stroke="{OL}" stroke-width="6" fill="none" stroke-linecap="round"/>'
    return svg(600, 260, b)
def cocodrilo():
    b = '<ellipse cx="320" cy="364" rx="270" ry="12" fill="#000" opacity=".3"/>'
    b += f'<path d="M40 300 Q16 214 124 196 L400 176 Q520 164 562 228 Q604 300 520 332 L124 352 Q50 352 40 300Z" fill="#5fc46a" {ST}/><path d="M60 322 Q300 300 540 310 Q520 334 500 334 L124 352 Q70 350 60 322Z" fill="#b9e8a0"/><path d="M60 300 L500 288" stroke="{OL}" stroke-width="7"/>'
    for i in range(9): b += f'<path d="M{84 + i * 46} 298 l14 30 l14 -30Z" fill="#fff" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>'
    for i in range(6): b += f'<path d="M{170 + i * 56} {196 - i * 3} l16 -24 l18 22" fill="#3f9a4c" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
    for x, y in ((180, 240), (260, 232), (340, 226), (220, 268), (300, 262), (420, 250)): b += f'<ellipse cx="{x}" cy="{y}" rx="16" ry="9" fill="#3f9a4c" opacity=".7"/>'
    b += f'<circle cx="104" cy="226" r="8" fill="{OL}"/><circle cx="420" cy="168" r="48" fill="#5fc46a" {ST}/><circle cx="424" cy="164" r="27" fill="#fff" {ST}/><circle cx="432" cy="168" r="12" fill="{OL}"/><circle cx="427" cy="162" r="4" fill="#fff"/><path d="M400 130 l-10 -16 M418 122 l-2 -18 M438 124 l8 -16" stroke="{OL}" stroke-width="5" stroke-linecap="round"/>'
    b += f'<path d="M376 120 Q470 16 604 128 Q646 262 604 334 Q560 250 470 142Z" fill="#fff" fill-opacity=".86" {ST}/><path d="M420 110 Q500 60 590 140 M450 150 Q540 150 600 250" stroke="#d8d0f0" stroke-width="5" fill="none"/>'
    b += f'<path d="M500 56 l14 -30 l14 30 l30 4 l-22 22 l6 30 l-28 -16 l-28 16 l6 -30 l-22 -22Z" fill="#ffc93c" {ST}/>'
    b += f'<g transform="translate(120,150)"><circle cx="0" cy="0" r="20" fill="{ROSA}" {ST}/><circle cx="-24" cy="16" r="18" fill="#ff8fa3" {ST}/><circle cx="24" cy="16" r="18" fill="#fff6dc" {ST}/><path d="M0 30 L0 80" stroke="#3f9a4c" stroke-width="9" stroke-linecap="round"/></g>'
    return svg(660, 380, b)
def piedra():
    b = '<ellipse cx="310" cy="440" rx="270" ry="14" fill="#000" opacity=".35"/>'
    b += f'<path d="M40 86 Q120 10 300 30 Q520 20 562 122 Q602 300 520 400 Q300 460 100 410 Q10 300 40 86Z" fill="#9a8f84" {ST}/><path d="M430 40 Q540 60 562 122 Q602 300 520 400 Q420 430 340 436 Q480 360 500 220 Q510 110 430 40Z" fill="#6f655c" opacity=".7"/><path d="M70 110 Q150 46 280 50" stroke="#c4bab0" stroke-width="10" fill="none" stroke-linecap="round"/>'
    b += '<path d="M150 160 l40 92 l40 -92 M300 150 l0 112 M300 150 l60 0 M300 206 l44 0 M420 160 q-50 52 0 104 q50 -52 0 -104" stroke="#3d342c" stroke-width="18" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M140 334 q60 -40 120 0 t120 0 t100 0" stroke="#3d342c" stroke-width="15" fill="none" stroke-linecap="round"/>'
    b += '<path d="M470 100 l-30 50 l20 30 l-24 44 M90 300 l40 20 l-10 40" stroke="#3d342c" stroke-width="5" fill="none"/><circle cx="110" cy="200" r="8" fill="#6f655c"/><circle cx="500" cy="330" r="10" fill="#5a5048"/>'
    return svg(620, 460, b)
def tablet():
    b = f'<rect x="22" y="24" width="616" height="456" rx="38" fill="#000" opacity=".3"/><rect x="10" y="10" width="620" height="460" rx="38" fill="#ff8a3c" {ST}/><rect x="26" y="26" width="588" height="428" rx="26" fill="#22203a" {ST}/><rect x="44" y="44" width="552" height="392" rx="10" fill="#e9f6ff"/>'
    b += '<rect x="44" y="44" width="552" height="50" fill="#16122a" opacity=".85"/><rect x="44" y="386" width="552" height="50" fill="#16122a" opacity=".85"/>'
    b += f'<g transform="translate(196,96) rotate(5) scale(.62)">{nota()}</g><circle cx="560" cy="69" r="13" fill="#ff3b4e"/><text x="70" y="80" font-family="Anton" font-size="28" fill="#fff">FOTO</text><circle cx="320" cy="411" r="19" fill="#fff"/><circle cx="320" cy="411" r="14" fill="#ff3b4e"/>'
    b += f'<path d="M60 100 L200 100 L120 380 L60 380Z" fill="#fff" opacity=".12"/><circle cx="30" cy="240" r="6" fill="#0e0b20"/><g transform="rotate(-14 90 430)"><rect x="50" y="440" width="70" height="26" rx="8" fill="#2bd4c4" stroke="{OL}" stroke-width="4"/></g>'
    return svg(640, 480, b)

# ---------------------------------------------------------------- fondos
def fondo(tipo):
    r = random.Random(9)
    b = '''<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#101638"/><stop offset=".6" stop-color="#231548"/><stop offset="1" stop-color="#0c0a20"/></linearGradient>
    <radialGradient id="lamp" cx=".18" cy=".5" r=".62"><stop offset="0" stop-color="#ffb65c" stop-opacity=".5"/><stop offset="1" stop-color="#ffb65c" stop-opacity="0"/></radialGradient></defs><rect width="1080" height="1920" fill="url(#g)"/>'''
    if tipo == "cuarto":
        b += '<rect x="560" y="300" width="430" height="520" rx="10" fill="#0a1030" stroke="#3a3470" stroke-width="12"/>'
        for i in range(9):
            x = 575 + i * 46; h = r.randint(120, 330); b += f'<rect x="{x}" y="{805 - h}" width="40" height="{h}" fill="#141a44"/>'
            for k in range(0, h - 30, 34):
                if r.random() < .55: b += f'<rect x="{x + 8}" y="{780 - k}" width="10" height="14" fill="#ffd27a"/>'
                if r.random() < .4: b += f'<rect x="{x + 24}" y="{780 - k}" width="10" height="14" fill="#7fe3d8"/>'
        b += '<circle cx="900" cy="390" r="44" fill="#fff6dc"/><circle cx="884" cy="380" r="9" fill="#e8dcb8"/><path d="M560 560 L990 560 M775 300 L775 820" stroke="#3a3470" stroke-width="10"/><rect x="540" y="820" width="470" height="26" rx="6" fill="#3a3470"/>'
        b += '<path d="M560 300 Q520 560 580 820 L620 820 Q590 560 640 300Z" fill="#4b2f8a" opacity=".9"/><path d="M990 300 Q1040 560 970 820 L930 820 Q960 560 920 300Z" fill="#4b2f8a" opacity=".9"/>'
        b += '<rect x="70" y="430" width="400" height="20" rx="4" fill="#3a2a66"/><rect x="90" y="450" width="14" height="60" fill="#2a1d50"/><rect x="430" y="450" width="14" height="60" fill="#2a1d50"/>'
        for i, c in enumerate(("#ff5d73", "#2bd4c4", "#ffc93c", "#b98ad6", "#ff5d73", "#fff6dc")): b += f'<rect x="{90 + i * 44}" y="{310 + (i % 3) * 14}" width="36" height="{120 - (i % 3) * 14}" fill="{c}" opacity=".85"/><rect x="{96 + i * 44}" y="{330 + (i % 3) * 14}" width="24" height="6" fill="#000" opacity=".25"/>'
        b += '<path d="M380 430 q-10 -60 20 -90 q30 30 20 90Z" fill="#3f9a4c"/><path d="M400 430 q-40 -40 -50 -80 M400 430 q40 -50 46 -84" stroke="#3f9a4c" stroke-width="10" fill="none" stroke-linecap="round"/><rect x="372" y="398" width="56" height="34" rx="6" fill="#c9773a"/>'
        b += '<rect x="90" y="540" width="170" height="230" fill="#2bd4c4" opacity=".4" transform="rotate(-4 175 655)"/><text x="175" y="680" text-anchor="middle" font-family="Anton" font-size="70" fill="#101638" opacity=".7" transform="rotate(-4 175 655)">POP</text><rect x="290" y="560" width="160" height="210" fill="#ff5d73" opacity=".4" transform="rotate(3 370 665)"/><circle cx="370" cy="650" r="46" fill="#101638" opacity=".5"/>'
        b += '<path d="M40 250 Q300 330 540 250" stroke="#4b3a9a" stroke-width="5" fill="none"/>'
        for i in range(7): x = 70 + i * 72; y = 262 + 34 * math.sin(i * .5 + .3); c = ("#ffc93c", "#2bd4c4", "#ff5d73", "#b98ad6")[i % 4]; b += f'<circle cx="{x}" cy="{y:.0f}" r="46" fill="{c}" opacity=".16"/><circle cx="{x}" cy="{y:.0f}" r="14" fill="{c}"/>'
        b += '<rect x="0" y="1420" width="1080" height="500" fill="#1a1238"/><rect x="0" y="1400" width="1080" height="36" fill="#3a2a66"/><rect x="0" y="1436" width="1080" height="10" fill="#0c0a20" opacity=".5"/>'
        b += '<rect x="-20" y="1250" width="420" height="200" rx="40" fill="#4b2f8a"/><rect x="20" y="1190" width="220" height="110" rx="46" fill="#b98ad6"/><path d="M-20 1330 Q200 1300 400 1340" stroke="#3a2470" stroke-width="8" fill="none"/>'
    else:
        for i in range(4): b += f'<rect x="{40 + i * 255}" y="200" width="235" height="330" rx="14" fill="#241a52" stroke="#3b2a7a" stroke-width="8"/><rect x="{60 + i * 255}" y="220" width="195" height="290" rx="8" fill="none" stroke="#2f2466" stroke-width="5"/><rect x="{232 + i * 255}" y="340" width="12" height="60" rx="6" fill="#2bd4c4"/>'
        for i in range(9):
            for j in range(2): b += f'<rect x="{20 + i * 120}" y="{620 + j * 120}" width="104" height="104" rx="8" fill="#1d1648" stroke="#3b2a7a" stroke-width="5"/>'
        b += '<path d="M0 590 L1080 590" stroke="#ff5d73" stroke-width="10" opacity=".85"/><path d="M0 590 L1080 590" stroke="#ff5d73" stroke-width="46" opacity=".15"/>'
        b += '<circle cx="880" cy="740" r="74" fill="#fff6dc" stroke="#3b2a7a" stroke-width="10"/><path d="M880 740 L880 690 M880 740 L916 756" stroke="#160f2c" stroke-width="8" stroke-linecap="round"/>'
        b += '<rect x="80" y="660" width="150" height="190" rx="8" fill="#fff6dc" opacity=".85" transform="rotate(-3 155 755)"/><path d="M100 700 l110 -4 M100 730 l90 -3 M100 760 l110 -4 M100 790 l70 -3" stroke="#2a3b8f" stroke-width="6" stroke-linecap="round" transform="rotate(-3 155 755)"/><circle cx="155" cy="664" r="12" fill="#ff5d73"/>'
        b += '<rect x="0" y="1150" width="1080" height="770" fill="#1d1444"/><rect x="-10" y="1100" width="1100" height="66" rx="12" fill="#3b2a7a" stroke="#4b3a9a" stroke-width="6"/><path d="M0 1120 L1080 1120" stroke="#5a48b0" stroke-width="5"/>'
        for i in range(3): b += f'<rect x="{40 + i * 345}" y="1200" width="320" height="620" rx="12" fill="#241a52" stroke="#3b2a7a" stroke-width="8"/><rect x="{170 + i * 345}" y="1230" width="60" height="12" rx="6" fill="#2bd4c4"/>'
        b += '<rect x="420" y="1010" width="70" height="92" rx="10" fill="#ff5d73" stroke="#160f2c" stroke-width="6"/><path d="M490 1030 q30 0 30 26 q0 26 -30 26" stroke="#160f2c" stroke-width="6" fill="none"/><path d="M440 1000 q8 -24 0 -44 M468 1000 q8 -24 0 -44" stroke="#fff" stroke-width="5" fill="none" opacity=".4" stroke-linecap="round"/>'
    b += '<rect width="1080" height="1920" fill="url(#lamp)"/>'
    return svg(1080, 1920, b)

L = {"bg_cuarto": fondo("cuarto"), "bg_cocina": fondo("cocina"), "celular": celular(), "tablet": tablet(), "candado": candado(), "candado_abierto": candado(True), "mano_mama": mano_mama(),
     "mano_pluma": mano_pluma(), "microondas": microondas(), "boleto": boleto(), "cocodrilo": cocodrilo(), "piedra": piedra(), "caja": svg(400, 430, caja()),
     "nota": svg(440, 360, f'<g transform="translate(10,22)">{nota()}</g>'), "nota_blanca": svg(440, 360, f'<g transform="translate(10,22)">{nota(texto="")}</g>'),
     "nico": cabeza("nico"), "dani": cabeza("dani"), "renata": cabeza("renata")}
for k in ("aburrida", "shock", "asco", "orgullosa", "enojada"):
    L[f"vale_{k}"] = vale(k, uid=k); L[f"vale_{k}_hab"] = vale(k, True, uid=k + "h")
L["vale_orgullosa_nota"] = vale("orgullosa", pose="nota", uid="on"); L["vale_orgullosa_nota_hab"] = vale("orgullosa", True, "nota", "onh"); L["vale_aburrida_nota"] = vale("aburrida", pose="nota", uid="an")
L["vale_shock_manos"] = vale("shock", pose="manos", uid="sm"); L["vale_shock_manos_hab"] = vale("shock", True, "manos", "smh"); L["vale_aburrida_senala"] = vale("orgullosa", pose="senala", uid="as")
if __name__ == "__main__":
    solo = sys.argv[1:]
    with sync_playwright() as p:
        br = p.chromium.launch(channel="chrome")
        for name, s in L.items():
            if solo and not any(name.startswith(x) for x in solo): continue
            w, h = map(int, re.search(r'width="(\d+)" height="(\d+)"', s).groups())
            pg = br.new_page(viewport={"width": w, "height": h}, device_scale_factor=2); hp = os.path.join(HERE, "_tmp.html")
            open(hp, "w").write(f"<html><head><style>{FONT_CSS} html,body{{margin:0;background:transparent;overflow:hidden}}</style></head><body>{s}</body></html>")
            pg.goto("file://" + hp); pg.wait_for_timeout(200); pg.screenshot(path=os.path.join(HERE, "layers", name + ".png"), omit_background=not name.startswith("bg_")); pg.close()
        br.close(); os.remove(os.path.join(HERE, "_tmp.html"))
    print("ok", len(L))
