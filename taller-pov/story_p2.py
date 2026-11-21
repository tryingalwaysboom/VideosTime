"""Story animado con voz: "La Parte 2 ya está publicada". python3 story_p2.py [still t1 t2 ...]"""
import os, sys, math, subprocess
import ep2                      # carga render con el guion del Ep.2 y sus piezas (persiana, grafiti, lados del final)
import story_video as SV
import portada as P
R = ep2.R
from render import (Image, ImageDraw, ImageFilter, W, H, bg, put, text, stamp, etiqueta, dust, neon_flicker,
                    dark, ease, clamp, popscale, YEL, RED, WHITE, OL, CYAN, MAG, F_UI)

HERE = R.HERE
VOZ = os.path.join(HERE, "voz_story_p2", "voz.wav")
FPS = R.FPS
AZ = (60, 110, 220)

# tiempos de la voz (atempo 1.08)
T_YA, T_ELEG, T_PERS, T_SLAM, T_CARA = .15, 2.04, 3.9, 4.55, 5.0
T_MAN, T_MSG, T_CORRE, T_COM, T_NAVE, T_ARR, T_SIG = 6.17, 8.17, 10.4, 11.7, 12.64, 14.15, 16.18
SC_T = [0, 1.9, 6.0, 10.25, 15.9]
IMPACTS = [.35, T_ELEG, T_SLAM, T_MAN, 8.6, T_CORRE, T_NAVE, T_ARR, T_SIG]
SFX = [("arranque", 0, -1), ("petardeo", 5.35, 0), ("llave_no_arranca", 14.55, 2), ("arranque", 15.85, 1)]

blank = SV.blank
etiqueta = SV.etiqueta

_P2 = None
def badge(c, T, t0, y=650):
    global _P2
    if _P2 is None: _P2 = blank(); P._parte_n(_P2, 2, y)
    k = popscale(T, t0, .35)
    if k > 0: SV.zoom_on(c, _P2, (540, y), k * 1.25 * (1 + .04 * math.sin(T * 7)))

def sc_publicada(T):
    c = bg("bg_taller", T, 0, 1.5, 1.2, 1.9, .5, .6); dark(c, 110)
    SV.underglow(c, T, 540, 1330, 380, MAG)
    put(c, "deportivo", 540, 1180 + 6 * math.sin(T * 3), .9)
    SV.titulo(c, T, 0)
    badge(c, T, .35)
    if T >= .95: stamp(c, T, .95, "YA DISPONIBLE", 540, 880, RED, -5, 85)
    return c

def sc_persiana(T):
    s0 = SC_T[1]
    c = bg("bg_fachada", T, s0, 1.25, 1.12, 4, .5, .62)
    inner = bg("bg_taller", T, 0, 1.4, 1.4, 1, .5, .6).crop((150, 830, 930, 1400))
    put(inner, "deportivo", 390, 420, .55); c.alpha_composite(inner, (150, 830))
    u = ease((T - T_PERS) / (T_SLAM - T_PERS))
    sh = 12 * math.sin(T * 70) * math.exp(-(T - T_SLAM) * 6) if T > T_SLAM else 0
    ep2.persiana_en(c, T, u, sh)
    SV.chispas(c, T, T_SLAM, 540, 1395)
    put(c, "coche_negro", 300, 1610, .7)
    SV.llamas(c, T, 5.4, 690, 1690, 3)
    stamp(c, T, T_ELEG, "GANÓ LA B", 540, 400, YEL, -8, 110)
    if T >= T_CARA: stamp(c, T, T_CARA, "EN LA CARA", 540, 600, MAG, 8, 100)
    return c

_GR = None
def sc_mensaje(T):
    global _GR
    s0 = SC_T[2]
    c = bg("bg_fachada", T, s0, 1.0, 1.1, 4.3, .5, .62)
    c.alpha_composite(Image.new("RGBA", (W, H), (255, 220, 170, 35)))
    inner = bg("bg_taller", T, 0, 1.4, 1.4, 1, .5, .6).crop((150, 830, 930, 1400)); c.alpha_composite(inner, (150, 830))
    ep2.persiana_en(c, T, 1.0)
    # el mensaje pintado aparece borroso: hay que ver el episodio para leerlo
    if T >= 8.5:
        if _GR is None:
            g = blank(); ep2.grafiti(g, 99, 0); _GR = g.filter(ImageFilter.GaussianBlur(16))
        a = clamp((T - 8.5) / .4)
        g = _GR.copy(); g.putalpha(g.getchannel("A").point(lambda v: int(v * a))); c.alpha_composite(g)
        SV.golpe(c, T, 8.6, "?", 1110, 260, YEL, 12)
    SV.golpe(c, T, T_MAN, "A LA MAÑANA SIGUIENTE…", 400, 72, WHITE, 8)
    etiqueta(c, T, T_MSG, "ALGUIEN NOS DEJÓ UN MENSAJE", 540, 540, RED, WHITE, 40)
    return c

COMS = [("A, la Nave 7 ya", 0), ("B que ruja ese motor", 1), ("A!!", 0), ("B B B", 1), ("A, quiero saber el secreto", 0),
        ("la B obvio", 1), ("A", 0), ("B por el tío", 1), ("A sin miedo", 0), ("B", 1)]

def sc_vota(T):
    s0 = SC_T[3]
    on = T >= T_NAVE
    hiA = T_NAVE <= T < T_ARR or (T >= 15.6 and int(T / .5) % 2 == 0)
    hiB = T_ARR <= T < 15.6 or (T >= 15.6 and not hiA)
    u = ease((T - s0) / .45)
    blk = Image.new("RGBA", (W, H), (0, 0, 0, 255)); c = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    A, B = ep2._lado("A", T), ep2._lado("B", T)
    c.alpha_composite(Image.blend(B, blk, .4) if (on and hiA) else B, (int(500 * (1 - u)), 0))
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon([(0, 0)] + R.RAYO + [(0, H)], fill=255)
    c.paste(Image.blend(A, blk, .4) if (on and hiB) else A, (int(-700 * (1 - u)), 0), mask)
    if u > .9:
        v = .6 + .4 * abs(math.sin(T * 13)) * abs(math.sin(T * 3.1))
        gl = blank(); ImageDraw.Draw(gl).line(R.RAYO, fill=CYAN + (int(255 * v),), width=44, joint="curve")
        c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(c)
        d.line(R.RAYO, fill=WHITE, width=12, joint="curve"); d.line(R.RAYO, fill=CYAN, width=5, joint="curve")
    d = ImageDraw.Draw(c)
    for cx, L_, t1, t2, t3, col, t0, h in ((270, "A", "NAVE 7", "Descubrir el secreto", "- Esta noche, a oscuras", AZ, T_NAVE, hiA),
                                           (790, "B", "ARRANCARLO", "+ El coche vuelve a rugir", "- Gastas los 600 €", MAG, T_ARR, hiB)):
        k = popscale(T, t0, .35)
        if k > 0: R._texto_opcion(d, cx, 420, L_, t1, t2, t3, col, k, 1.08 if h else 1.0)
    etiqueta(c, T, T_CORRE, "PARTE 2 YA PUBLICADA", 540, 960, YEL, OL, 42)
    k = popscale(T, T_COM, .35)
    if k > 0:
        lay = blank(); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((110, 1095, 970, 1205), 55, fill=WHITE, outline=OL, width=6)
        text(ld, (540, 1150), "COMENTA A o B EN LA PARTE 2", 56, OL)
        SV.zoom_on(c, lay, (540, 1150), k * (1 + .04 * math.sin((T - T_COM) * 7)))
    SV.COMS = COMS; SV.comentarios(c, T, 12.0)
    return c

def sc_siguenos(T):
    s0 = SC_T[4]
    c = bg("bg_taller", T, s0, 1.25, 1.15, 1.5, .5, .62); dark(c, 120)
    rev = 4 * math.sin(T * 40) * math.exp(-(T - s0 - .2) * 3) if T > s0 + .2 else 0
    SV.underglow(c, T, 540, 1210, 420, MAG)
    put(c, "deportivo", 540 + rev, 1030, 1.0)
    SV.titulo(c, T, s0 + .05)
    SV.golpe(c, T, s0 + .1, "TÚ DECIDES CÓMO SIGUE", 650, 80, YEL, 8, rot=-3)
    k = popscale(T, s0 + .15, .3)
    if k > 0:
        done = T >= T_SIG + .25
        press = 1 - .08 * math.sin(clamp((T - T_SIG) / .25) * math.pi)
        lay = blank(); ld = ImageDraw.Draw(lay)
        fill, fg, s = ((RED, WHITE, "+  SÍGUENOS") if not done else (WHITE, OL, "   SIGUIENDO"))
        ld.rounded_rectangle((210, 1340, 870, 1460), 60, fill=fill, outline=WHITE if not done else OL, width=6)
        text(ld, (540, 1400), s, 64, fg)
        if done: ld.line((330, 1400, 352, 1424, 390, 1376), fill=(46, 160, 90), width=12, joint="curve")
        SV.zoom_on(c, lay, (540, 1400), k * press)
        if T_SIG - .3 <= T < T_SIG + .9:
            p = ease((T - (T_SIG - .3)) / .3); fx, fy = 760 + 160 * (1 - p), 1430 + 160 * (1 - p)
            if T >= T_SIG:
                r_ = 30 + 220 * clamp((T - T_SIG) / .5); a = int(255 * (1 - clamp((T - T_SIG) / .5)))
                ov = blank(); ImageDraw.Draw(ov).ellipse((fx - r_, fy - r_, fx + r_, fy + r_), outline=(255, 255, 255, a), width=8)
                c.alpha_composite(ov)
            ImageDraw.Draw(c).ellipse((fx - 38, fy - 38, fx + 38, fy + 38), fill=(255, 255, 255, 230), outline=OL, width=5)
    return c

SV.SC_T, SV.SCENES, SV.IMPACTS = SC_T, [sc_publicada, sc_persiana, sc_mensaje, sc_vota, sc_siguenos], IMPACTS
SV.VOZ, SV.SFX, SV.OUT = VOZ, SFX, "story_parte2_publicada.mp4"

if __name__ == "__main__":
    SV.main()
