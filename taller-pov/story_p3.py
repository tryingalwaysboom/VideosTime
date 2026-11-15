"""Story animado con voz: "La Parte 3 ya está publicada". python3 story_p3.py [still t1 t2 ...]"""
import os, sys, math
import ep3                      # motor con piezas del Ep.3 (candado, confeti, lados del final, llave)
import story_video as SV
import portada as P
R = ep3.R
from render import (Image, ImageDraw, ImageFilter, W, H, bg, put, text, stamp, dark, ease, clamp, popscale,
                    YEL, RED, WHITE, OL, CYAN, MAG, F_UI, GRIS)

HERE = R.HERE
VOZ = os.path.join(HERE, "voz_story_p3", "voz.wav")
AZ = (60, 110, 220)

# tiempos de la voz (atempo 1.08)
T_GANO, T_NAVE, T_DENTRO, T_SOLOS, T_CORRE, T_VOTA, T_COMEN, T_SIG = 2.0, 3.08, 5.03, 8.28, 10.21, 11.0, 12.2, 13.65
SC_T = [0, 1.85, 4.85, 8.1, 10.05, 13.45]
IMPACTS = [.35, T_GANO, 4.0, T_SOLOS + .5, T_CORRE, T_SIG]
SFX = [("arranque", 0, -1), ("impacto", 1.9, -4), ("candado", 3.95, 0), ("brillo", T_DENTRO + .3, -2),
       ("nitro_ruge", T_SOLOS - .1, -1), ("impacto", T_CORRE - .1, -5), ("arranque", 12.3, -7)]
etiqueta = SV.etiqueta; blank = SV.blank

_P3 = None
def badge(c, T, t0, y=650):
    global _P3
    if _P3 is None: _P3 = blank(); P._parte_n(_P3, 3, y)
    k = popscale(T, t0, .35)
    if k > 0: SV.zoom_on(c, _P3, (540, y), k * 1.25 * (1 + .04 * math.sin(T * 7)))

def sc_publicada(T):
    c = bg("bg_taller", T, 0, 1.5, 1.2, 1.9, .5, .6); dark(c, 110)
    SV.underglow(c, T, 540, 1330, 380, MAG)
    put(c, "deportivo", 540, 1180 + 6 * math.sin(T * 3), .9)
    SV.titulo(c, T, -1)                 # visible desde el frame 0
    badge(c, T, -1)
    if T >= .4: stamp(c, T, .4, "YA DISPONIBLE", 540, 880, RED, -5, 85)
    return c

def sc_nave(T):
    s0 = SC_T[1]; tclac = 4.0
    c = bg("bg_poligono", T, s0, 1.2, 1.3, 3, .5, .55); dark(c, 130)
    if T < T_NAVE:   # resultado
        ep3.barra_voto(c, T, 760, "A", "NAVE 7 ESTA NOCHE", 78, AZ, True, s0)
        ep3.barra_voto(c, T, 950, "B", "ARRANCAR EL COCHE", 22, MAG, False, s0)
        stamp(c, T, T_GANO, "¡GANÓ LA A!", 540, 470, YEL, -6, 120)
        ep3.confeti(c, T, T_GANO)
        return c
    # candado de la Nave 7 abriéndose
    ov = Image.new("RGBA", (W, H), (6, 5, 10, 200)); c.alpha_composite(ov)
    lay = blank(); d = ImageDraw.Draw(lay); op = ease(clamp((T - tclac) / .15)); up = 70 * op
    kv = ep3.llave_v(1 - .78 * ease(clamp((T - 3.6) / .3)))
    ins = ease(clamp((T - T_NAVE) / .4)); top = 900 - 170 * ins + 380 * (1 - ins)
    lay.alpha_composite(kv, (int(540 - kv.width / 2), int(top)))
    d.arc((395, 480 - up, 685, 820 - up), 180, 360, fill=OL, width=62); d.arc((399, 484 - up, 681, 816 - up), 180, 360, fill=(190, 196, 210), width=50)
    for x in (424, 656):
        d.line((x, 650 - up, x, 740), fill=OL, width=60); d.line((x, 650 - up, x, 740), fill=(190, 196, 210), width=48)
    d.rounded_rectangle((340, 720, 740, 1080), 46, fill=(214, 172, 74), outline=OL, width=10)
    d.rounded_rectangle((360, 1000, 720, 1066), 30, fill=(170, 130, 50))
    text(d, (560, 860), "7", 120, (150, 110, 35))
    c.alpha_composite(lay)
    if T >= tclac: ep3.ep_chispas(c, T, tclac, 540, 700); stamp(c, T, tclac, "NAVE 7", 800, 560, YEL, 10, 110)
    return c

def sc_caja(T):
    s0 = SC_T[2]
    c = bg("bg_nave7", T, s0, 1.3, 1.4, 3.5, .5, .75); dark(c, 120)
    u = ease(clamp((T - T_DENTRO - .3) / .5))
    rays = blank(); rd = ImageDraw.Draw(rays)
    for i in range(12):
        a = i * math.pi / 6 + T * .4
        rd.polygon([(540, 980), (540 + 900 * math.cos(a - .08), 980 + 900 * math.sin(a - .08)), (540 + 900 * math.cos(a + .08), 980 + 900 * math.sin(a + .08))], fill=(255, 230, 140, int(70 * u)))
    c.alpha_composite(rays.filter(ImageFilter.GaussianBlur(6)))
    put(c, "caja_chaval", 540, 1150, 1.3)
    SV.golpe(c, T, T_DENTRO + .3, "?", 760, 260, YEL, 12)
    if T >= 6.4: etiqueta(c, T, 6.4, "LO QUE TU TÍO DEJÓ PARA TI", 540, 470, YEL, OL, 42)
    return c

def sc_solos(T):
    s0 = SC_T[3]; tf = T_SOLOS + .45
    c = bg("bg_poligono", T, s0, 1.35, 1.42, 2.5, .5, .95); dark(c, 110)
    rev = 5 * math.sin(T * 60) if T >= tf else 0
    put(c, "coche_negro", 560 + rev, 1500, 1.0)
    put(c, "nitro", 420, 880, .9)
    if T >= tf:
        u = ease(clamp((T - tf) / .2))
        put(c, "faros", 560, 1420, 1.2 * u + .01, alpha=u)
        glare = blank(); gd = ImageDraw.Draw(glare)
        for x in (360, 760): gd.ellipse((x - 260, 1230, x + 260, 1570), fill=(255, 250, 220, int(200 * u)))
        c.alpha_composite(glare.filter(ImageFilter.GaussianBlur(50)))
        ep3.llamas(c, T, tf + .1, 1030, 1585, 3, .22)
    stamp(c, T, T_SOLOS + .5, "NO ESTÁBAMOS SOLOS", 540, 480, RED, -6, 86)
    return c

COMS = [("A, a correr con el Seat", 0), ("B, que hable Nitro", 1), ("A!!", 0), ("B B B", 1), ("A porque Nitro da miedo", 0),
        ("B quiero saber qué robó", 1), ("A", 0), ("la B obvio", 1)]

def sc_vota(T):
    s0 = SC_T[4]
    hiA = int((T - s0) / .5) % 2 == 0
    u = ease((T - s0) / .45)
    blk = Image.new("RGBA", (W, H), (0, 0, 0, 255)); c = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    A, B = ep3._lado("A"), ep3._lado("B")
    c.alpha_composite(Image.blend(B, blk, .4) if hiA else B, (int(500 * (1 - u)), 0))
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon([(0, 0)] + R.RAYO + [(0, H)], fill=255)
    c.paste(A if hiA else Image.blend(A, blk, .4), (int(-700 * (1 - u)), 0), mask)
    if u > .9:
        v = .6 + .4 * abs(math.sin(T * 13)) * abs(math.sin(T * 3.1))
        gl = blank(); ImageDraw.Draw(gl).line(R.RAYO, fill=CYAN + (int(255 * v),), width=44, joint="curve")
        c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(c)
        d.line(R.RAYO, fill=WHITE, width=12, joint="curve"); d.line(R.RAYO, fill=CYAN, width=5, joint="curve")
    d = ImageDraw.Draw(c)
    for cx, L_, t1, t2, t3, col, t0, h in ((270, "A", "HUIR", "+ Te llevas la centralita", "- Nitro os persigue", AZ, s0 + .15, hiA),
                                           (790, "B", "ENFRENTARLO", "+ Sabrás qué robó tu tío", "- Tú solo ante Nitro", MAG, s0 + .35, not hiA)):
        k = popscale(T, t0, .35)
        if k > 0: R._texto_opcion(d, cx, 420, L_, t1, t2, t3, col, k, 1.08 if h else 1.0)
    k = popscale(T, T_VOTA - .1, .35)
    if k > 0:
        lay = blank(); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((90, 1060, 990, 1220), 50, fill=WHITE, outline=OL, width=6)
        text(ld, (540, 1112), "VOTA EN LA ENCUESTA DE LA PARTE 3", 46, OL)
        ld.text((540, 1172), "y dime en comentarios por qué", font=R.font(F_UI, 34), fill=(200, 50, 50), anchor="mm")
        SV.zoom_on(c, lay, (540, 1140), k * (1 + .035 * math.sin((T - T_VOTA) * 7)))
    SV.COMS = COMS; SV.comentarios(c, T, T_COMEN - .3)
    return c

def sc_siguenos(T):
    s0 = SC_T[5]
    c = bg("bg_taller", T, s0, 1.25, 1.15, 1.5, .5, .62); dark(c, 120)
    rev = 4 * math.sin(T * 40) * math.exp(-(T - s0 - .1) * 3) if T > s0 + .1 else 0
    SV.underglow(c, T, 540, 1210, 420, MAG)
    put(c, "deportivo", 540 + rev, 1030, 1.0)
    SV.titulo(c, T, -1)
    badge(c, T, -1, 650)
    done = T >= T_SIG + .25
    press = 1 - .08 * math.sin(clamp((T - T_SIG) / .25) * math.pi)
    lay = blank(); ld = ImageDraw.Draw(lay)
    fill, fg, s = ((RED, WHITE, "+  SÍGUENOS") if not done else (WHITE, OL, "   SIGUIENDO"))
    ld.rounded_rectangle((210, 1340, 870, 1460), 60, fill=fill, outline=WHITE if not done else OL, width=6)
    text(ld, (540, 1400), s, 64, fg)
    if done: ld.line((330, 1400, 352, 1424, 390, 1376), fill=(46, 160, 90), width=12, joint="curve")
    SV.zoom_on(c, lay, (540, 1400), press)
    if T_SIG - .25 <= T < T_SIG + .9:
        p = ease((T - (T_SIG - .25)) / .25); fx, fy = 760 + 160 * (1 - p), 1430 + 160 * (1 - p)
        if T >= T_SIG:
            r_ = 30 + 220 * clamp((T - T_SIG) / .5); a = int(255 * (1 - clamp((T - T_SIG) / .5)))
            ov = blank(); ImageDraw.Draw(ov).ellipse((fx - r_, fy - r_, fx + r_, fy + r_), outline=(255, 255, 255, a), width=8)
            c.alpha_composite(ov)
        ImageDraw.Draw(c).ellipse((fx - 38, fy - 38, fx + 38, fy + 38), fill=(255, 255, 255, 230), outline=OL, width=5)
    return c

SV.SC_T, SV.SCENES, SV.IMPACTS = SC_T, [sc_publicada, sc_nave, sc_caja, sc_solos, sc_vota, sc_siguenos], IMPACTS
SV.VOZ, SV.SFX, SV.OUT, SV.TAIL = VOZ, SFX, "story_parte3_publicada.mp4", 1.1

if __name__ == "__main__":
    SV.main()
