"""Coches detallados para la serie del taller: carrocería con degradados, reflejos, juntas de paneles,
llantas multirradio con pinzas de freno, neumáticos con flanco, faros con lente y pilotos con brillo.
Vista lateral, lienzo 1080x560 (el morro mira a la izquierda)."""
import math

OL = "#14101f"
_n = [0]
def gid(p): _n[0] += 1; return f"{p}{_n[0]}"

def lg(i, stops, x1=0, y1=0, x2=0, y2=1):
    st = "".join(f'<stop offset="{o}" stop-color="{c}"{f" stop-opacity={chr(34)}{a}{chr(34)}" if a is not None else ""}/>' for o, c, a in stops)
    return f'<linearGradient id="{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{st}</linearGradient>'

def rg(i, stops, cx=.5, cy=.5, r=.5):
    st = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
    return f'<radialGradient id="{i}" cx="{cx}" cy="{cy}" r="{r}">{st}</radialGradient>'

def wheel(x, y, R, rim, rim_dark, spokes=10, caliper="#e0322f", style="mesh", deep=True):
    """Rueda completa: neumático con flanco, llanta con profundidad, radios, buje y pinza de freno."""
    d, b = "", ""
    gt, gr, gl = gid("t"), gid("r"), gid("l")
    d += rg(gt, [(0, "#2a2a30", 1), (.86, "#141418", 1), (1, "#050507", 1)])
    d += lg(gr, [(0, rim, None), (.55, rim, None), (1, rim_dark, None)], 0, 0, 1, 1)
    d += rg(gl, [(0, "#000", .0), (.75, "#000", .0), (1, "#000", .55)])
    r_rim = R * .68
    # neumático
    b += f'<circle cx="{x}" cy="{y}" r="{R}" fill="url(#{gt})" stroke="{OL}" stroke-width="6"/>'
    b += f'<circle cx="{x}" cy="{y}" r="{R*.86}" fill="none" stroke="#3a3a44" stroke-width="2.5"/>'
    # letras del flanco (marcas genéricas en arco)
    pid = gid("p")
    rr = R * .79
    d += f'<path id="{pid}" d="M{x-rr} {y} A{rr} {rr} 0 0 1 {x+rr} {y}"/>'
    b += (f'<text font-family="Anton" font-size="{R*.13:.0f}" fill="#8a8a96" letter-spacing="3">'
          f'<textPath href="#{pid}" startOffset="50%" text-anchor="middle">R-SPEC  225/40 R18</textPath></text>')
    # disco de freno
    b += f'<circle cx="{x}" cy="{y}" r="{r_rim*.88}" fill="#5a5d66"/>'
    for k in range(18):
        a = k * math.pi / 9
        b += f'<circle cx="{x + r_rim*.62*math.cos(a):.1f}" cy="{y + r_rim*.62*math.sin(a):.1f}" r="{R*.025:.1f}" fill="#3a3c44"/>'
    # pinza de freno (visible entre radios)
    b += (f'<path d="M{x - r_rim*.78} {y - r_rim*.42} Q{x - r_rim*.95} {y} {x - r_rim*.78} {y + r_rim*.42} '
          f'L{x - r_rim*.55} {y + r_rim*.34} Q{x - r_rim*.68} {y} {x - r_rim*.55} {y - r_rim*.34}Z" fill="{caliper}" stroke="{OL}" stroke-width="3"/>')
    # aro de la llanta (labio)
    b += f'<circle cx="{x}" cy="{y}" r="{r_rim}" fill="none" stroke="url(#{gr})" stroke-width="{R*.09:.1f}"/>'
    b += f'<circle cx="{x}" cy="{y}" r="{r_rim + R*.045}" fill="none" stroke="{OL}" stroke-width="3"/>'
    if deep:
        b += f'<circle cx="{x}" cy="{y}" r="{r_rim - R*.05}" fill="url(#{gl})"/>'
    # radios
    for k in range(spokes):
        a = k * 2 * math.pi / spokes - math.pi / 2
        if style == "mesh":
            for s in (-1, 1):
                a2 = a + s * .2
                b += (f'<line x1="{x + R*.14*math.cos(a):.1f}" y1="{y + R*.14*math.sin(a):.1f}" '
                      f'x2="{x + r_rim*.94*math.cos(a2):.1f}" y2="{y + r_rim*.94*math.sin(a2):.1f}" stroke="{rim}" stroke-width="{R*.045:.1f}" stroke-linecap="round"/>')
        else:  # radios en Y anchos
            w = .16
            pts = [(R*.16, a - w), (r_rim*.95, a - w*.55), (r_rim*.95, a + w*.55), (R*.16, a + w)]
            p = " ".join(f"{x + r*math.cos(t):.1f},{y + r*math.sin(t):.1f}" for r, t in pts)
            b += f'<polygon points="{p}" fill="url(#{gr})" stroke="{OL}" stroke-width="2.5"/>'
            b += (f'<line x1="{x + R*.2*math.cos(a-.05):.1f}" y1="{y + R*.2*math.sin(a-.05):.1f}" '
                  f'x2="{x + r_rim*.9*math.cos(a-.05):.1f}" y2="{y + r_rim*.9*math.sin(a-.05):.1f}" stroke="#fff" stroke-opacity="0.35" stroke-width="2"/>')
    # buje y tuercas
    b += f'<circle cx="{x}" cy="{y}" r="{R*.17}" fill="url(#{gr})" stroke="{OL}" stroke-width="4"/>'
    for k in range(5):
        a = k * 2 * math.pi / 5
        b += f'<circle cx="{x + R*.1*math.cos(a):.1f}" cy="{y + R*.1*math.sin(a):.1f}" r="{R*.025:.1f}" fill="{rim_dark}"/>'
    b += f'<circle cx="{x}" cy="{y}" r="{R*.05}" fill="{OL}"/>'
    # brillo del aro
    b += f'<path d="M{x - r_rim*.7} {y - r_rim*.7} A{r_rim} {r_rim} 0 0 1 {x + r_rim*.2} {y - r_rim*.98}" stroke="#fff" stroke-opacity="0.6" stroke-width="{R*.03:.1f}" fill="none" stroke-linecap="round"/>'
    return d, b

def deportivo():
    """Deportivo japonés de los 90 (genérico, sin marca), blanco perla con franja magenta,
    capó y aleta delantera en imprimación: a medio restaurar pero precioso."""
    d, b = "", ""
    gb, gw, gs, gp, gg = gid("b"), gid("w"), gid("s"), gid("p"), gid("g")
    d += lg(gb, [(0, "#ffffff", None), (.35, "#eef2f7", None), (.62, "#c9d2de", None), (.64, "#9aa6b6", None), (1, "#dfe5ee", None)])
    d += lg(gw, [(0, "#3b5478", None), (.5, "#18233a", None), (1, "#0b111e", None)])
    d += lg(gs, [(0, "#ff6be6", None), (1, "#c2189f", None)])
    d += lg(gp, [(0, "#a7adb6", None), (.6, "#8a9099", None), (1, "#6e747e", None)])
    d += rg(gg, [(0, "#000", .65), (1, "#000", 0)])
    b += f'<ellipse cx="545" cy="502" rx="520" ry="34" fill="url(#{gg})"/>'
    body = ("M40 398 Q38 362 66 352 L200 330 Q300 312 380 300 Q430 248 500 232 L690 230 Q770 236 860 298 "
            "Q960 312 1036 332 Q1054 344 1052 404 L1048 452 Q1046 470 1020 472 L938 472 "
            "A92 92 0 0 0 754 472 L330 472 A92 92 0 0 0 146 472 L66 472 Q40 470 40 446Z")
    b += f'<path d="{body}" fill="url(#{gb})" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>'
    # capó + aleta delantera en imprimación (restauración)
    cid = gid("c")
    d += f'<clipPath id="{cid}"><path d="{body}"/></clipPath>'
    b += f'<g clip-path="url(#{cid})">'
    b += f'<path d="M30 320 L392 300 L400 330 L404 472 L30 472Z" fill="url(#{gp})"/>'
    b += '<path d="M392 300 L400 330 L404 472" stroke="#5a606a" stroke-width="3" fill="none"/>'
    for (x, y, r) in ((120, 400, 14), (210, 360, 9), (250, 430, 11)):
        b += f'<circle cx="{x}" cy="{y}" r="{r}" fill="#b4693a" opacity="0.45"/>'
    b += '<path d="M90 360 Q160 350 240 352" stroke="#c6ccd4" stroke-width="5" opacity="0.6" fill="none"/>'
    # reflejo del entorno en la parte baja (horizonte)
    b += '<rect x="404" y="398" width="660" height="10" fill="#7f8ea3" opacity="0.5"/>'
    b += '<path d="M404 318 Q700 306 1050 346" stroke="#fff" stroke-width="12" opacity="0.75" fill="none"/>'
    # franja lateral magenta con filo
    b += f'<path d="M404 362 L1000 362 L1000 384 L404 384Z" fill="url(#{gs})"/>'
    b += '<path d="M404 391 L1000 391" stroke="#ff6be6" stroke-width="4"/>'
    b += '<text x="470" y="380" font-family="Anton" font-size="18" fill="#fff" letter-spacing="6" opacity="0.9">TWIN TURBO</text>'
    b += '</g>'
    # ventanas con marco negro y reflejos
    win1 = "M410 302 Q446 260 506 246 L640 244 L640 304Z"
    win2 = "M664 244 L690 244 Q752 250 822 300 L664 304Z"
    for w in (win1, win2):
        b += f'<path d="{w}" fill="url(#{gw})" stroke="#0b0b12" stroke-width="9" stroke-linejoin="round"/>'
    b += '<path d="M444 290 L492 256 L520 252 L466 302Z" fill="#fff" opacity="0.28"/><path d="M540 250 L560 250 L512 302 L494 302Z" fill="#fff" opacity="0.15"/>'
    b += '<path d="M690 250 L716 252 L688 300 L672 300Z" fill="#fff" opacity="0.2"/>'
    b += '<rect x="640" y="240" width="24" height="68" fill="#0b0b12"/>'
    # retrovisor
    b += f'<path d="M408 310 Q396 294 414 288 L440 288 Q448 300 438 314Z" fill="#e8edf3" stroke="{OL}" stroke-width="4"/>'
    # juntas de puerta (coupé, 1 puerta larga) y maneta
    b += f'<path d="M400 318 Q396 400 404 466 M716 306 Q726 390 716 466" stroke="#8a95a6" stroke-width="3" fill="none"/>'
    b += f'<rect x="650" y="330" width="44" height="10" rx="5" fill="#2a2f3a"/>'
    # tomas de aire laterales
    b += f'<path d="M740 330 L800 322 L800 344 L744 348Z" fill="#1a1c24" stroke="{OL}" stroke-width="3"/>'
    # tapa de gasolina
    b += f'<circle cx="872" cy="342" r="16" fill="none" stroke="#8a95a6" stroke-width="3"/>'
    # faldón lateral y paragolpes
    b += f'<path d="M332 462 L752 462 L748 478 L336 478Z" fill="#1a1c24"/>'
    b += f'<path d="M44 444 L140 444 L140 470 L60 474 Q42 466 44 444Z" fill="#1a1c24"/>'
    # faros escamoteables (un poco levantados) + intermitente
    b += f'<path d="M110 336 L210 318 L216 336 L116 352Z" fill="#e8edf3" stroke="{OL}" stroke-width="5"/>'
    b += f'<path d="M120 340 L204 326 L206 332 L122 346Z" fill="#fff8d0"/>'
    b += f'<rect x="50" y="374" width="54" height="18" rx="6" fill="#ffb347" stroke="{OL}" stroke-width="4"/>'
    b += '<rect x="56" y="378" width="20" height="8" rx="3" fill="#fff" opacity="0.6"/>'
    # pilotos traseros con brillo
    b += f'<path d="M1002 352 L1046 360 L1046 392 L1006 388Z" fill="#c4171d" stroke="{OL}" stroke-width="4"/>'
    b += '<path d="M1010 360 L1040 364 L1040 372 L1010 370Z" fill="#ff8a8a" opacity="0.7"/>'
    # alerón GT
    b += f'<path d="M910 282 L1068 262 L1072 284 L920 306Z" fill="#16161e" stroke="{OL}" stroke-width="5"/>'
    b += '<path d="M920 288 L1060 268" stroke="#fff" stroke-opacity="0.25" stroke-width="3"/>'
    b += f'<path d="M950 302 L954 322 L966 322 L964 300Z M1030 280 L1034 330 L1046 330 L1044 278Z" fill="#16161e" stroke="{OL}" stroke-width="3"/>'
    # matrícula tapada con cinta americana
    b += f'<rect x="1000" y="414" width="52" height="30" fill="#f2efe8" stroke="{OL}" stroke-width="3"/>'
    b += '<rect x="992" y="422" width="68" height="14" fill="#9aa0aa" transform="rotate(-7 1026 429)"/>'
    # escape doble cromado
    b += f'<ellipse cx="1030" cy="466" rx="14" ry="10" fill="#c9cfd9" stroke="{OL}" stroke-width="3"/><ellipse cx="1030" cy="466" rx="7" ry="5" fill="#1a1a20"/>'
    # pasos de rueda (sombra interior)
    for cx in (238, 846):
        b += f'<path d="M{cx-100} 472 A100 100 0 0 1 {cx+100} 472" fill="#0b0b10"/>'
    for cx in (238, 846):
        wd, wb = wheel(cx, 472, 86, "#e2c15a", "#9a7a20", 6, "#e0322f", "y")
        d += wd; b += wb
    return d, b

def coche_negro():
    """Coche del rival: negro brillante, muy bajo, kit ancho, llantas negras con labio cromado y neón cian de bajos."""
    d, b = "", ""
    gb, gw, gn, gg = gid("b"), gid("w"), gid("n"), gid("g")
    d += lg(gb, [(0, "#4a4d5c", None), (.18, "#20222c", None), (.55, "#0b0b10", None), (.58, "#2d3140", None), (1, "#08080c", None)])
    d += lg(gw, [(0, "#1a2a44", None), (1, "#05070d", None)])
    d += rg(gn, [(0, "#3ef0ff", .85), (.6, "#3ef0ff", .25), (1, "#3ef0ff", 0)])
    d += rg(gg, [(0, "#000", .7), (1, "#000", 0)])
    b += f'<ellipse cx="545" cy="500" rx="540" ry="38" fill="url(#{gn})"/>'
    b += f'<ellipse cx="545" cy="500" rx="480" ry="20" fill="url(#{gg})"/>'
    body = ("M34 408 Q32 374 62 362 L220 340 Q320 324 400 312 Q456 262 530 250 L700 248 Q780 256 870 312 "
            "Q980 326 1036 348 Q1054 360 1052 414 L1050 458 Q1048 474 1022 476 L938 476 "
            "A92 92 0 0 0 754 476 L330 476 A92 92 0 0 0 146 476 L60 476 Q34 474 34 452Z")
    b += f'<path d="{body}" fill="url(#{gb})" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>'
    cid = gid("c")
    d += f'<clipPath id="{cid}"><path d="{body}"/></clipPath>'
    b += f'<g clip-path="url(#{cid})">'
    # reflejos de la calle (farolas y neón)
    b += '<path d="M60 340 Q560 306 1050 344" stroke="#fff" stroke-width="7" opacity="0.55" fill="none"/>'
    b += '<path d="M200 392 Q600 380 1040 396" stroke="#ff4fd8" stroke-width="5" opacity="0.45" fill="none"/>'
    b += '<path d="M520 260 L560 476" stroke="#fff" stroke-width="26" opacity="0.06"/><path d="M590 260 L620 476" stroke="#fff" stroke-width="10" opacity="0.08"/>'
    b += '</g>'
    # lunas tintadas
    win1 = "M432 314 Q470 276 534 264 L660 262 L660 316Z"
    win2 = "M684 262 L700 262 Q764 270 832 312 L684 316Z"
    for w in (win1, win2):
        b += f'<path d="{w}" fill="url(#{gw})" stroke="#000" stroke-width="9" stroke-linejoin="round"/>'
    b += '<path d="M466 302 L512 274 L536 270 L486 314Z" fill="#9ad8ff" opacity="0.18"/>'
    b += '<rect x="660" y="258" width="24" height="62" fill="#000"/>'
    b += f'<path d="M428 322 Q416 306 432 300 L458 300 Q466 312 456 326Z" fill="#1a1c24" stroke="{OL}" stroke-width="4"/>'
    # juntas y maneta
    b += '<path d="M420 330 Q416 400 424 470 M730 320 Q740 400 730 470" stroke="#3a3e4c" stroke-width="3" fill="none"/>'
    b += '<rect x="668" y="340" width="42" height="9" rx="4" fill="#5a5e6c"/>'
    # faro LED afilado + luz de día
    b += f'<path d="M44 368 L182 350 L174 378 L50 392Z" fill="#0b0b10" stroke="{OL}" stroke-width="4"/>'
    b += '<path d="M60 372 L172 358 L168 368 L62 380Z" fill="#fffbe0"/>'
    b += '<path d="M70 384 L150 374" stroke="#9ff8ff" stroke-width="4"/>'
    # entradas de aire y labio delantero
    b += f'<path d="M40 420 L150 420 L150 440 L46 444Z" fill="#000"/>'
    for x in range(54, 146, 14): b += f'<line x1="{x}" y1="422" x2="{x}" y2="440" stroke="#2a2a33" stroke-width="3"/>'
    b += f'<path d="M30 462 L160 462 L160 474 L26 476Z" fill="#c22f2f" stroke="{OL}" stroke-width="3"/>'
    # faldón con línea roja
    b += f'<path d="M332 466 L752 466 L748 482 L336 482Z" fill="#0b0b10"/><path d="M340 466 L748 466" stroke="#c22f2f" stroke-width="4"/>'
    # piloto trasero en barra
    b += f'<path d="M990 360 L1050 372 L1050 388 L992 378Z" fill="#ff2a2a" stroke="{OL}" stroke-width="3"/>'
    b += '<path d="M996 368 L1046 378" stroke="#ffb0b0" stroke-width="3"/>'
    # alerón cuello de cisne
    b += f'<path d="M900 292 L1070 270 L1072 292 L910 316Z" fill="#0b0b10" stroke="{OL}" stroke-width="5"/>'
    b += f'<path d="M950 312 Q942 338 958 350 M1030 284 Q1026 330 1040 346" stroke="#0b0b10" stroke-width="10" fill="none"/>'
    # difusor y escape
    b += f'<ellipse cx="1036" cy="462" rx="18" ry="13" fill="#7a7f8c" stroke="{OL}" stroke-width="3"/><ellipse cx="1036" cy="462" rx="9" ry="7" fill="#000"/>'
    b += '<ellipse cx="1036" cy="462" rx="6" ry="4" fill="#3a8aff" opacity="0.6"/>'
    # pegatina NITRO en la puerta trasera
    b += '<text x="470" y="420" font-family="Anton" font-size="44" fill="none" stroke="#3ef0ff" stroke-width="2" letter-spacing="4">NITRO</text>'
    for cx in (238, 846):
        b += f'<path d="M{cx-100} 476 A100 100 0 0 1 {cx+100} 476" fill="#000"/>'
    for cx in (238, 846):
        wd, wb = wheel(cx, 476, 86, "#2a2c34", "#0b0b10", 10, "#3ef0ff", "mesh")
        d += wd; b += wb
        b += f'<circle cx="{cx}" cy="476" r="{86*.68+3}" fill="none" stroke="#e8ecf2" stroke-width="5"/>'
    return d, b

def utilitario():
    """Utilitario rojo de finales de los 90, con óxido y abolladuras (cliente que no volvió)."""
    d, b = "", ""
    gb, gw, gg = gid("b"), gid("w"), gid("g")
    d += lg(gb, [(0, "#f2675a", None), (.4, "#d8402f", None), (.62, "#a82a20", None), (.64, "#c43a2c", None), (1, "#8a2018", None)])
    d += lg(gw, [(0, "#4a6488", None), (1, "#141c2c", None)])
    d += rg(gg, [(0, "#000", .6), (1, "#000", 0)])
    b += f'<ellipse cx="540" cy="500" rx="480" ry="30" fill="url(#{gg})"/>'
    body = ("M80 400 Q78 340 120 326 L250 300 Q320 216 400 200 L760 196 Q840 198 890 260 L960 330 "
            "Q1000 350 1000 400 L998 452 Q996 470 970 472 L900 472 A86 86 0 0 0 728 472 L368 472 "
            "A86 86 0 0 0 196 472 L104 472 Q80 470 80 446Z")
    b += f'<path d="{body}" fill="url(#{gb})" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>'
    cid = gid("c")
    d += f'<clipPath id="{cid}"><path d="{body}"/></clipPath>'
    b += f'<g clip-path="url(#{cid})">'
    b += '<path d="M90 330 Q540 300 1000 340" stroke="#fff" stroke-width="10" opacity="0.4" fill="none"/>'
    for (x, y, rx, ry) in ((160, 440, 40, 20), (930, 430, 34, 26), (520, 452, 60, 14)):
        b += f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#6a3a1c" opacity="0.6"/>'
    b += '<path d="M600 360 q30 -16 60 6 q-30 20 -60 -6Z" fill="#7a1a12" opacity="0.5"/>'
    b += '<rect x="80" y="380" width="920" height="16" fill="#1a1c24" opacity="0.85"/>'
    b += '</g>'
    win1 = "M410 220 L560 216 L560 312 L320 314 Q360 236 410 220Z"
    win2 = "M584 216 L748 214 Q812 218 852 300 L856 312 L584 312Z"
    for w in (win1, win2):
        b += f'<path d="{w}" fill="url(#{gw})" stroke="#111" stroke-width="9" stroke-linejoin="round"/>'
    b += '<path d="M420 226 L470 222 L370 310 L340 310Z" fill="#fff" opacity="0.25"/>'
    b += '<path d="M640 240 L700 300 M680 230 L650 290" stroke="#dfe6ef" stroke-width="2" opacity="0.6"/>'  # luna rajada
    b += '<rect x="560" y="212" width="24" height="104" fill="#111"/>'
    b += f'<path d="M318 310 Q306 292 324 288 L348 288 Q356 300 346 314Z" fill="#c43a2c" stroke="{OL}" stroke-width="4"/>'
    b += '<path d="M330 320 L334 466 M584 316 L590 466" stroke="#7a1a12" stroke-width="3"/>'
    b += '<rect x="530" y="332" width="42" height="10" rx="5" fill="#2a2a33"/>'
    b += f'<path d="M84 340 L170 330 L168 362 L86 370Z" fill="#fff8d6" stroke="{OL}" stroke-width="4"/>'
    b += '<path d="M92 346 L160 338" stroke="#fff" stroke-width="3"/>'
    b += f'<path d="M960 340 L998 352 L998 392 L962 386Z" fill="#c4171d" stroke="{OL}" stroke-width="4"/>'
    b += f'<rect x="900" y="410" width="80" height="32" rx="4" fill="#f2efe8" stroke="{OL}" stroke-width="3"/>'
    b += '<text x="940" y="434" font-family="Anton" font-size="22" text-anchor="middle" fill="#1d1d26">B-4512-KX</text>'
    b += f'<path d="M84 440 L170 440 L170 466 L96 470 Q84 462 84 440Z" fill="#2a2a33"/>'
    for cx in (282, 814):
        b += f'<path d="M{cx-94} 472 A94 94 0 0 1 {cx+94} 472" fill="#0b0b10"/>'
    for cx in (282, 814):
        wd, wb = wheel(cx, 472, 80, "#b8bec8", "#6a707a", 4, "#5a5d66", "y", deep=False)
        d += wd; b += wb
        b += f'<circle cx="{cx}" cy="472" r="{80*.6}" fill="#c9cfd9" opacity="0.35"/>'  # tapacubos
    return d, b
