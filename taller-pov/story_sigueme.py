"""Story animado con voz: "Sígueme, la Parte 4 sale muy pronto". python3 story_sigueme.py [still t1 t2 ...]"""
import os, sys, math
import ep3
import story_video as SV
import portada as P
R = ep3.R
from render import (Image, ImageDraw, ImageFilter, W, H, bg, put, text, stamp, dark, ease, clamp, popscale,
                    YEL, RED, WHITE, OL, CYAN, MAG, F_UI)

HERE = R.HERE
VOZ = os.path.join(HERE, "voz_story_p4", "voz.wav")
VISTAS = 27293   # visualizaciones reales de las Partes 1-3 en Metricool (15/11 noche)

T_VOTOS, T_VIENE, T_CAMBIA, T_P4, T_SIG, T_DECIDES = 1.06, 2.64, 4.0, 5.62, 7.89, 9.63
SC_T = [0, .95, 2.5, 5.45, 7.75]
IMPACTS = [T_VOTOS, T_CAMBIA, T_P4, T_SIG, T_DECIDES]
SFX = [("impacto", 0, -6), ("brillo", T_VOTOS, -3), ("impacto", T_CAMBIA - .1, -4), ("arranque", T_P4 - .1, -3)]
blank = SV.blank

_PORT = {}
def portada(n, w=470):
    if n not in _PORT:
        im = Image.open(os.path.join(HERE, f"portada_serie_A_parte{n}.jpg")).convert("RGBA")
        im = im.resize((w, int(w * im.height / im.width)))
        fr = Image.new("RGBA", (im.width + 16, im.height + 16), WHITE + (255,)); fr.alpha_composite(im, (8, 8))
        _PORT[n] = fr
    return _PORT[n]

def sc_partes(T):
    c = bg("bg_taller", T, 0, 1.3, 1.2, 1, .5, .6); dark(c, 150)
    gl = blank(); ImageDraw.Draw(gl).ellipse((100, 600, 980, 1400), fill=MAG + (70,)); c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(80)))
    for i, (x, rot) in enumerate(((235, 9), (540, 0), (845, -9))):
        k = 1 if i == 0 else popscale(T, i * .22, .3)
        if k <= 0: continue
        card = portada(i + 1).rotate(rot, expand=True, resample=Image.BICUBIC)
        card = card.resize((int(card.width * k * .9), int(card.height * k * .9)))
        c.alpha_composite(card, (int(x - card.width / 2), int(950 - card.height / 2 + (40 if i != 1 else 0))))
    text(ImageDraw.Draw(c), (540, 420), "3 PARTES", 130, YEL, stroke=10)
    return c

def sc_votos(T):
    s0 = SC_T[1]
    c = bg("bg_poligono", T, s0, 1.2, 1.3, 2, .5, .45); dark(c, 130)
    gl = blank(); ImageDraw.Draw(gl).ellipse((60, 620, 1020, 1240), fill=AZ_GLOW); c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(80)))
    u = ease(clamp((T - s0) / 1.2)); v = int(VISTAS * (.55 + .45 * u)) // 10 * 10 if u < 1 else VISTAS
    d = ImageDraw.Draw(c)
    text(d, (540, 860), f"{v:,}".replace(",", "."), 170, WHITE, stroke=10)
    text(d, (540, 1000), "VISUALIZACIONES", 70, CYAN, stroke=7)
    ep3.confeti(c, T, s0 + .1)
    stamp(c, T, T_VOTOS, "MILES DE VOTOS", 540, 470, YEL, -6, 100)
    return c
AZ_GLOW = (60, 110, 220, 110)

def sc_cambia(T):
    s0 = SC_T[2]
    c = bg("bg_noche", T, s0, 1.0, 1.12, 3, .5, .55); dark(c, 90)
    put(c, "deportivo", 540, 1150, 1.05)
    pulse = .5 + .5 * math.sin((T - s0) * 7)
    ov = blank(); od = ImageDraw.Draw(ov)
    od.ellipse((640, 1130, 900, 1310), outline=RED + (255,), width=10); od.ellipse((610, 1100, 930, 1340), outline=RED + (int(150 * pulse),), width=6)
    c.alpha_composite(ov)
    SV.golpe(c, T, s0 + .2, "?", 760, 230, YEL, 12)
    if T >= T_CAMBIA: stamp(c, T, T_CAMBIA, "LO CAMBIA TODO", 540, 470, RED, -6, 100)
    return c

_P4 = None
def sc_parte4(T):
    global _P4
    s0 = SC_T[3]
    c = bg("bg_taller", T, s0, 1.3, 1.2, 2.5, .5, .6); dark(c, 110)
    SV.underglow(c, T, 540, 1330, 380, MAG)
    rev = 4 * math.sin(T * 40) * math.exp(-(T - s0 - .1) * 3) if T > s0 + .1 else 0
    put(c, "deportivo", 540 + rev, 1180, .9)
    SV.titulo(c, T, s0)
    if _P4 is None: _P4 = blank(); P._parte_n(_P4, 4, 650)
    k = popscale(T, s0 + .15, .35)
    if k > 0: SV.zoom_on(c, _P4, (540, 650), k * 1.25 * (1 + .04 * math.sin(T * 7)))
    if T >= 6.6: stamp(c, T, 6.6, "MUY PRONTO", 540, 880, RED, -5, 95)
    return c

def sc_sigueme(T):
    s0 = SC_T[4]
    c = bg("bg_taller", T, s0, 1.25, 1.15, 3, .5, .62); dark(c, 120)
    SV.underglow(c, T, 540, 1210, 420, MAG)
    put(c, "deportivo", 540, 1030, 1.0)
    SV.titulo(c, T, s0)
    done = T >= T_SIG + .6
    press = 1 - .08 * math.sin(clamp((T - T_SIG - .35) / .25) * math.pi)
    lay = blank(); ld = ImageDraw.Draw(lay)
    fill, fg, s = ((RED, WHITE, "+  SÍGUEME") if not done else (WHITE, OL, "   SIGUIENDO"))
    ld.rounded_rectangle((210, 1340, 870, 1460), 60, fill=fill, outline=WHITE if not done else OL, width=6)
    text(ld, (540, 1400), s, 64, fg)
    if done: ld.line((330, 1400, 352, 1424, 390, 1376), fill=(46, 160, 90), width=12, joint="curve")
    SV.zoom_on(c, lay, (540, 1400), popscale(T, s0 + .05, .3) * press * (1 + (.05 * math.sin(T * 9) if not done else 0)))
    ts = T_SIG + .35
    if ts - .3 <= T < ts + .9:
        p = ease((T - (ts - .3)) / .3); fx, fy = 760 + 160 * (1 - p), 1430 + 160 * (1 - p)
        if T >= ts:
            r_ = 30 + 220 * clamp((T - ts) / .5); a = int(255 * (1 - clamp((T - ts) / .5)))
            ov = blank(); ImageDraw.Draw(ov).ellipse((fx - r_, fy - r_, fx + r_, fy + r_), outline=(255, 255, 255, a), width=8); c.alpha_composite(ov)
        ImageDraw.Draw(c).ellipse((fx - 38, fy - 38, fx + 38, fy + 38), fill=(255, 255, 255, 230), outline=OL, width=5)
    if T >= T_DECIDES: SV.golpe(c, T, T_DECIDES, "LA DECIDES TÚ", 680, 110, YEL, 9, rot=-4)
    return c

SV.SC_T, SV.SCENES, SV.IMPACTS = SC_T, [sc_partes, sc_votos, sc_cambia, sc_parte4, sc_sigueme], IMPACTS
SV.VOZ, SV.SFX, SV.OUT, SV.TAIL = VOZ, SFX, "story_sigueme_parte4.mp4", 1.0

if __name__ == "__main__":
    SV.main()
