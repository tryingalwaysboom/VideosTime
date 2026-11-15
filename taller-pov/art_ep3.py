"""Arte nuevo del Ep.3 "Nave 7": polígono de noche, puerta de la nave, taller escondido, trofeo, caja "para el chaval", planos."""
import math, os, re, sys, random
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import art
from art import svg, cel, sky, OL, NEON_C, NEON_M, OUT, FONT_CSS, glowtext

def bg_poligono():
    """Polígono industrial muerto: naves en fila, sin farolas, la Nave 7 al fondo con la puerta oxidada."""
    d = sky("sk", [(0, "#07061a"), (0.55, "#141233"), (1, "#22183a")])
    d += sky("as", [(0, "#24222c"), (1, "#0f0e14")])
    b = '<rect width="1080" height="1920" fill="url(#sk)"/>'
    r = random.Random(7)
    for _ in range(90):
        b += f'<circle cx="{r.randint(0,1080)}" cy="{r.randint(0,620)}" r="{r.choice([1.2,1.8,2.4])}" fill="#fff" opacity="{r.uniform(.25,.9):.2f}"/>'
    b += '<circle cx="230" cy="230" r="64" fill="#f4ecd0" opacity="0.95"/><circle cx="252" cy="215" r="64" fill="#141233"/>'
    # grúas y chimeneas lejanas
    b += '<path d="M780 600 L780 300 L980 300 M780 330 L700 330" stroke="#1c1a30" stroke-width="14" fill="none"/>'
    b += '<rect x="60" y="430" width="40" height="190" fill="#1c1a30"/><rect x="120" y="470" width="30" height="150" fill="#1c1a30"/>'
    # naves laterales en perspectiva (izquierda y derecha)
    for side in (-1, 1):
        for k in range(3):
            x0 = 540 + side * (540 - k * 120); x1 = 540 + side * (420 - k * 120)
            top = 640 + k * 25; bot = 1380 - k * 70
            pts = f"{x0},{top - 120 + k*40} {x1},{top} {x1},{bot} {x0},{bot + 140 - k*40}"
            b += f'<polygon points="{pts}" fill="{["#2e2c3c","#34324a","#3a3852"][k]}" stroke="{OL}" stroke-width="5"/>'
            n = (5 - k) if side < 0 else (6 + k)
            cx = (x0 + x1) / 2; cy = (top + bot) / 2 + 60
            b += f'<text x="{cx:.0f}" y="{cy - 170:.0f}" font-family="Anton" font-size="{70 - k*14}" text-anchor="middle" fill="#7a7890" opacity="0.6">{n if n != 7 else 8}</text>'
    # nave 7 al fondo (centro)
    b += f'<rect x="300" y="560" width="480" height="820" fill="#4a4250" stroke="{OL}" stroke-width="8"/>'
    for y in range(580, 1380, 34): b += f'<line x1="300" y1="{y}" x2="780" y2="{y}" stroke="#3a3442" stroke-width="5"/>'
    b += '<path d="M290 560 L540 470 L790 560Z" fill="#3a3442" stroke="#1d1630" stroke-width="8"/>'
    b += f'<circle cx="540" cy="640" r="62" fill="#e8e0c0" stroke="{OL}" stroke-width="8"/>'
    b += '<text x="540" y="672" font-family="Anton" font-size="92" text-anchor="middle" fill="#c62f2f">7</text>'
    # manchas de óxido en la fachada
    for _ in range(18):
        x, y = r.randint(310, 770), r.randint(580, 1370)
        b += f'<ellipse cx="{x}" cy="{y}" rx="{r.randint(10,40)}" ry="{r.randint(16,60)}" fill="#8a4a2a" opacity="0.35"/>'
    # marco de la puerta (la puerta va en otra capa)
    b += f'<rect x="350" y="760" width="380" height="620" fill="#050408" stroke="{OL}" stroke-width="10"/>'
    # farolas apagadas
    for x in (120, 960):
        b += f'<rect x="{x-8}" y="700" width="16" height="760" fill="#1a1a22" stroke="{OL}" stroke-width="3"/><path d="M{x-40} 700 L{x+40} 700 L{x+28} 676 L{x-28} 676Z" fill="#1a1a22" stroke="{OL}" stroke-width="3"/>'
        b += f'<ellipse cx="{x}" cy="704" rx="26" ry="7" fill="#2a2a30"/>'
    # valla
    b += '<rect x="0" y="1330" width="1080" height="8" fill="#5a5a66"/>'
    for x in range(0, 1080, 36): b += f'<line x1="{x}" y1="1250" x2="{x+60}" y2="1380" stroke="#5a5a66" stroke-width="3" opacity="0.5"/><line x1="{x+60}" y1="1250" x2="{x}" y2="1380" stroke="#5a5a66" stroke-width="3" opacity="0.5"/>'
    # asfalto mojado
    b += '<rect x="0" y="1380" width="1080" height="540" fill="url(#as)"/>'
    for _ in range(16):
        x = r.randint(0, 1080); y = r.randint(1420, 1900)
        b += f'<ellipse cx="{x}" cy="{y}" rx="{r.randint(40,110)}" ry="{r.randint(6,12)}" fill="#7a7aa0" opacity="0.13"/>'
    b += '<path d="M540 1380 L540 1920" stroke="#e8e0c0" stroke-width="10" stroke-dasharray="70 60" opacity="0.35"/>'
    return svg(1080, 1920, b, d)

def puerta7():
    """Puerta corredera oxidada de la Nave 7 con candado."""
    d = sky("pt", [(0, "#7a5040"), (0.5, "#6a4434"), (1, "#5a3a2c")])
    b = f'<rect x="0" y="0" width="380" height="620" fill="url(#pt)" stroke="{OL}" stroke-width="8"/>'
    for y in range(20, 620, 40): b += f'<line x1="0" y1="{y}" x2="380" y2="{y}" stroke="#4a2e22" stroke-width="6"/>'
    r = random.Random(3)
    for _ in range(26):
        b += f'<ellipse cx="{r.randint(0,380)}" cy="{r.randint(0,620)}" rx="{r.randint(8,34)}" ry="{r.randint(6,22)}" fill="#a8582a" opacity="{r.uniform(.25,.6):.2f}"/>'
    b += f'<rect x="20" y="290" width="70" height="40" rx="6" fill="#8a8a96" stroke="{OL}" stroke-width="5"/>'
    b += f'<path d="M40 290 Q40 250 62 250 Q84 250 84 290" stroke="#b0b0bc" stroke-width="9" fill="none"/>'
    b += f'<rect x="30" y="300" width="60" height="56" rx="8" fill="#c9a24a" stroke="{OL}" stroke-width="5"/><circle cx="60" cy="324" r="7" fill="#3a2a1a"/>'
    b += '<text x="190" y="140" font-family="Anton" font-size="64" text-anchor="middle" fill="#2a1a12" opacity="0.6">NO PASAR</text>'
    return svg(380, 620, b, d)

def bg_nave7():
    """Taller escondido de Rubén: limpio, herramientas nuevas, elevador hidráulico, planos del deportivo en las paredes."""
    d = sky("wl", [(0, "#2a2e3c"), (1, "#1a1d28")])
    d += sky("fl", [(0, "#454a56"), (1, "#22252e")])
    b = '<rect width="1080" height="1920" fill="url(#wl)"/>'
    for x in range(0, 1080, 90): b += f'<rect x="{x}" y="0" width="86" height="1150" fill="#2e3242" opacity="0.6"/>'
    # planos del deportivo (azules)
    def plano(x, y, w, h, rot, seed):
        rr = random.Random(seed); s = f'<g transform="rotate({rot} {x+w/2} {y+h/2})"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#1f4f8a" stroke="#e8eef8" stroke-width="5"/>'
        for gx in range(x + 20, x + w, 30): s += f'<line x1="{gx}" y1="{y}" x2="{gx}" y2="{y+h}" stroke="#5a8ac8" stroke-width="1.5" opacity="0.5"/>'
        for gy in range(y + 20, y + h, 30): s += f'<line x1="{x}" y1="{gy}" x2="{x+w}" y2="{gy}" stroke="#5a8ac8" stroke-width="1.5" opacity="0.5"/>'
        cx, cy, k = x + w / 2, y + h * .55, w / 420
        s += (f'<path d="M{cx-180*k} {cy+30*k} Q{cx-170*k} {cy-20*k} {cx-100*k} {cy-30*k} L{cx-40*k} {cy-80*k} Q{cx} {cy-95*k} {cx+60*k} {cy-90*k} '
              f'L{cx+120*k} {cy-40*k} Q{cx+180*k} {cy-30*k} {cx+185*k} {cy+30*k}Z" fill="none" stroke="#e8eef8" stroke-width="4"/>')
        for wx in (-110, 110): s += f'<circle cx="{cx+wx*k}" cy="{cy+30*k}" r="{34*k}" fill="none" stroke="#e8eef8" stroke-width="4"/>'
        s += f'<line x1="{cx-180*k}" y1="{cy+80*k}" x2="{cx+185*k}" y2="{cy+80*k}" stroke="#e8eef8" stroke-width="2" stroke-dasharray="8 6"/>'
        s += f'<text x="{x+16}" y="{y+40}" font-family="Anton" font-size="28" fill="#e8eef8">{rr.choice(["MOTOR","CHASIS","DEPÓSITO","ESCAPE"])} · R</text></g>'
        return s
    b += plano(60, 120, 420, 300, -3, 1) + plano(600, 100, 420, 300, 2, 2) + plano(110, 470, 330, 240, 4, 3) + plano(660, 450, 330, 240, -2, 4)
    # banco con armario de herramientas rojo
    b += cel('<rect x="40" y="800" width="380" height="330" rx="10"/>', "#c62f2f", "#9a2222", "#e04a4a", -18, -8, 7)
    for k in range(5): b += f'<rect x="60" y="{820+k*60}" width="340" height="46" rx="6" fill="#b02a2a" stroke="{OL}" stroke-width="4"/><rect x="190" y="{838+k*60}" width="80" height="10" rx="4" fill="#d9dde6"/>'
    # tablero de herramientas nuevas
    b += f'<rect x="620" y="760" width="420" height="330" fill="#3a4050" stroke="{OL}" stroke-width="6"/>'
    for i in range(14):
        x = 650 + (i % 7) * 54; y = 790 + (i // 7) * 150
        b += f'<rect x="{x+10}" y="{y}" width="20" height="{90 + (i*17)%40}" rx="6" fill="#d9dde6" stroke="{OL}" stroke-width="3"/>'
    # suelo pulido
    b += '<rect x="0" y="1150" width="1080" height="770" fill="url(#fl)"/>'
    b += '<path d="M0 1150 L1080 1150" stroke="#0e0c14" stroke-width="8"/>'
    b += '<path d="M200 1920 L380 1150 M880 1920 L700 1150" stroke="#e8b02f" stroke-width="14" opacity="0.6"/>'
    # elevador hidráulico (dos columnas)
    for x in (300, 780):
        b += cel(f'<rect x="{x-28}" y="880" width="56" height="480" rx="6"/>', "#2f6ac6", "#224f96", "#4a86e0", -10, -4, 6)
        b += f'<rect x="{x-60}" y="1340" width="120" height="30" fill="#1d1d26" stroke="{OL}" stroke-width="4"/>'
    b += f'<rect x="270" y="1180" width="540" height="22" fill="#9aa0ac" stroke="{OL}" stroke-width="5"/>'
    for x in range(0, 1080, 160): b += f'<ellipse cx="{x+80}" cy="1500" rx="60" ry="8" fill="#ffffff" opacity="0.05"/>'
    return svg(1080, 1920, b, d)

def trofeo():
    """Copa del Rally 1996 con placa: 1º Rubén & Salcedo."""
    d = sky("au", [(0, "#ffe9a0"), (0.5, "#e8b830"), (1, "#a8780a")])
    b = '<g filter="url(#drop)">'
    b += '<path d="M150 80 L450 80 Q450 330 300 360 Q150 330 150 80Z" fill="url(#au)" stroke="#1d1630" stroke-width="8"/>'
    b += '<path d="M150 120 Q60 120 70 200 Q80 260 160 270" stroke="#e8b830" stroke-width="22" fill="none"/><path d="M450 120 Q540 120 530 200 Q520 260 440 270" stroke="#e8b830" stroke-width="22" fill="none"/>'
    b += '<path d="M200 110 Q210 260 290 320" stroke="#fff6d0" stroke-width="12" fill="none" opacity="0.7"/>'
    b += '<rect x="265" y="355" width="70" height="90" fill="#c99a20" stroke="#1d1630" stroke-width="6"/>'
    b += '<rect x="160" y="440" width="280" height="60" rx="8" fill="#e8b830" stroke="#1d1630" stroke-width="7"/>'
    b += '<rect x="110" y="495" width="380" height="150" rx="10" fill="#2a1e14" stroke="#1d1630" stroke-width="7"/>'
    b += '<rect x="130" y="512" width="340" height="116" rx="6" fill="#d9c27a" stroke="#8a6a20" stroke-width="4"/>'
    b += '<text x="300" y="560" font-family="Anton" font-size="38" text-anchor="middle" fill="#2a1e14">RALLY 1996 · 1º</text>'
    b += '<text x="300" y="610" font-family="Anton" font-size="36" text-anchor="middle" fill="#2a1e14">RUBÉN &amp; SALCEDO</text>'
    b += '</g>'
    return svg(600, 680, b, d)

def caja_chaval():
    """Caja metálica de herramientas con la tapa escrita a mano: PARA EL CHAVAL."""
    b = '<ellipse cx="300" cy="420" rx="280" ry="30" fill="#000" opacity="0.45"/>'
    b += cel('<path d="M40 170 L560 170 L540 410 L60 410Z"/>', "#3a5a7a", "#2a4460", "#4e7298", -20, -8, 8)
    b += cel('<path d="M30 110 L570 110 L560 180 L40 180Z"/>', "#44688c", "#2f4c6a", None, -8, 0, 7)
    b += f'<rect x="250" y="80" width="100" height="36" rx="10" fill="#9aa0ac" stroke="{OL}" stroke-width="6"/>'
    b += '<rect x="110" y="230" width="380" height="120" rx="8" fill="#f2ead4" stroke="#1d1630" stroke-width="5" transform="rotate(-2 300 290)"/>'
    b += '<text x="300" y="315" font-family="Caveat" font-weight="700" font-size="68" text-anchor="middle" fill="#1a2a6a" transform="rotate(-2 300 290)">para el chaval</text>'
    for x in (70, 530): b += f'<rect x="{x-12}" y="190" width="24" height="40" rx="5" fill="#c9cfd9" stroke="{OL}" stroke-width="4"/>'
    return svg(600, 460, b)

LAYERS = {"bg_poligono": bg_poligono, "puerta7": puerta7, "bg_nave7": bg_nave7, "trofeo": trofeo, "caja_chaval": caja_chaval}

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
