"""Story animado con voz: "La Parte 4 ya está publicada". python3 story_p4.py [still t1 t2 ...]"""
import os, sys, math
import ep4                      # escenas y piezas del Ep.4 (lados del final, puerto, foto, sepia)
import story_video as SV
from luces import coche_faros
import portada as P
R = ep4.R
from render import (Image, ImageDraw, ImageFilter, W, H, bg, put, text, stamp, dark, ease, clamp, popscale,
                    YEL, RED, WHITE, OL, CYAN, MAG, F_UI)

HERE = R.HERE
VOZ = os.path.join(HERE, "voz_story_p4", "voz.wav")
AZ = (60, 110, 220)

# tiempos de la voz (atempo 1.08, pausas medidas)
T_ELEG, T_ROBO, T_CARR, T_CARR_W, T_CORRE, T_VOTA, T_COMEN, T_SIG = 2.06, 4.32, 7.25, 8.75, 9.83, 10.55, 11.8, 13.42
SC_T = [0, 1.9, 4.15, 7.1, 9.7, 13.25]
IMPACTS = [.35, T_ELEG + .1, T_ROBO + 1.2, T_CARR_W, T_CORRE, T_SIG]
SFX = [("nitro_arranca", 0, -2), ("impacto", T_ELEG, -4), ("brillo", T_ROBO + .1, -3), ("impacto", T_ROBO + 1.2, -5),
       ("nitro_arranca", T_CARR - .1, -1), ("petardeo", T_CARR_W + .1, 0), ("impacto", T_CORRE - .1, -5),
       ("seat_acelera", 12.0, -6), ("brillo", T_SIG + .3, -4)]
etiqueta = SV.etiqueta; blank = SV.blank

_P4 = None
def badge(c, T, t0, y=650):
    global _P4
    if _P4 is None: _P4 = blank(); P._parte_n(_P4, 4, y)
    k = popscale(T, t0, .35)
    if k > 0: SV.zoom_on(c, _P4, (540, y), k * 1.25 * (1 + .04 * math.sin(T * 7)))

def sc_publicada(T):
    c = bg("bg_poligono", T, 0, 1.5, 1.3, 1.9, .5, .95); dark(c, 110)
    rev = 5 * math.sin(T * 60) * math.exp(-T * 1.5)
    coche_faros(c, 600, 1190, .8, 1.0, rev=rev)
    SV.titulo(c, T, -1)                 # visible desde el frame 0
    badge(c, T, -1)
    if T >= .4: stamp(c, T, .4, "YA DISPONIBLE", 540, 880, RED, -5, 85)
    return c

def sc_eleg(T):
    s0 = SC_T[1]
    c = bg("bg_poligono", T, s0, 1.2, 1.3, 3, .5, .95); dark(c, 130)
    ep4.glow(c, (-120, 620, 760, 1280), MAG, 90, 80)
    text(ImageDraw.Draw(c), (540, 560), "RESULTADO PARTE 3", 64, YEL, stroke=8)
    ep4.barra_voto(c, T, 760, "A", "HUIR CON EL SEAT", 32, AZ, False, s0)
    ep4.barra_voto(c, T, 950, "B", "ENFRENTARTE A NITRO", 68, MAG, True, s0)
    stamp(c, T, T_ELEG, "¡ELEGISTEIS LA B!", 540, 1180, YEL, -6, 110)
    ep4.confeti(c, T, T_ELEG)
    return c

def sc_robo(T):
    s0 = SC_T[2]; tq = T_ROBO + 1.2
    c = bg("bg_noche", T, s0, 1.0, 1.06, 3)
    put(c, "deportivo", 540, 1120, 1.0)
    ep4.put_img(c, ep4.foto(False), 540, 640, .5, rot=-4)
    c = ep4.sepia(c, .65); ep4.ralladuras(c, T)
    if T >= tq:
        pulse = .5 + .5 * math.sin((T - tq) * 7)
        ov = blank(); od = ImageDraw.Draw(ov)
        od.ellipse((660, 1070, 920, 1250), outline=RED + (255,), width=10); od.ellipse((640, 1050, 940, 1270), outline=RED + (int(140 * pulse),), width=6)
        c.alpha_composite(ov)
        stamp(c, T, tq, "¿QUÉ LE ROBÓ MI TÍO?", 540, 960, RED, -5, 76)
    return c

def sc_carrera(T):
    s0 = SC_T[3]
    c = ep4.bg_puerto(T, s0, 1.0, 1.08, 3)
    put(c, "deportivo", 300, 1250, .52)
    rev = 4 * math.sin(T * 60) if T >= T_CARR else 0
    coche_faros(c, 790, 1190, .52, .8, largo=260, rev=rev)
    ep4.llamas(c, T, T_CARR_W + .1, 790 + 470 * .52, 1190 + 85 * .52, 2, .3, .55)
    d = ImageDraw.Draw(c); ep4.bandera(d, 540, 1060, 90, 60, T)
    if T >= T_CARR + .3: SV.etiqueta(c, T, T_CARR + .3, "SÁBADO · NOCHE · PUERTO", 540, 560, YEL, OL, 44)
    if T >= T_CARR_W - .2: stamp(c, T, T_CARR_W - .2, "NITRO TE RETA", 540, 760, RED, -6, 110)
    return c

COMS = [("A, a ganarle", 0), ("B, quiero saber qué hay", 1), ("A!!", 0), ("B B B", 1), ("A, el coche es nuestro", 0),
        ("B que es una trampa", 1), ("A", 0), ("la B obvio", 1)]

def sc_vota(T):
    s0 = SC_T[4]
    hiA = int((T - s0) / .5) % 2 == 0
    u = ease((T - s0) / .45)
    blk = Image.new("RGBA", (W, H), (0, 0, 0, 255)); c = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    A, B = ep4._lado("A"), ep4._lado("B")
    c.alpha_composite(Image.blend(B, blk, .4) if hiA else B, (int(500 * (1 - u)), 0))
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon([(0, 0)] + R.RAYO + [(0, H)], fill=255)
    c.paste(A if hiA else Image.blend(A, blk, .4), (int(-700 * (1 - u)), 0), mask)
    if u > .9:
        v = .6 + .4 * abs(math.sin(T * 13)) * abs(math.sin(T * 3.1))
        gl = blank(); ImageDraw.Draw(gl).line(R.RAYO, fill=CYAN + (int(255 * v),), width=44, joint="curve")
        c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(c)
        d.line(R.RAYO, fill=WHITE, width=12, joint="curve"); d.line(R.RAYO, fill=CYAN, width=5, joint="curve")
    d = ImageDraw.Draw(c)
    for cx, L_, t1, t2, t3, col, t0, h in ((270, "A", "CARRERA", "+ El coche puede ser tuyo", "- Nitro no pierde nunca", AZ, s0 + .15, hiA),
                                           (790, "B", "DEPÓSITO", "+ Sabrás qué hay dentro", "- Sin tiempo para preparar", MAG, s0 + .35, not hiA)):
        k = popscale(T, t0, .35)
        if k > 0: R._texto_opcion(d, cx, 420, L_, t1, t2, t3, col, k, 1.08 if h else 1.0)
    k = popscale(T, T_VOTA - .1, .35)
    if k > 0:
        lay = blank(); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((90, 1060, 990, 1220), 50, fill=WHITE, outline=OL, width=6)
        text(ld, (540, 1112), "VOTA EN LA ENCUESTA DE LA PARTE 4", 46, OL)
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

SV.SC_T, SV.SCENES, SV.IMPACTS = SC_T, [sc_publicada, sc_eleg, sc_robo, sc_carrera, sc_vota, sc_siguenos], IMPACTS
SV.VOZ, SV.SFX, SV.OUT, SV.TAIL = VOZ, SFX, "story_parte4_publicada.mp4", 1.1

if __name__ == "__main__":
    SV.main()
