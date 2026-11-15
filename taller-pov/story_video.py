"""Story animado con voz (CTA Parte 1) en el estilo del episodio: escenas, cámara, golpes y SFX.
python3 story_video.py [still t1 t2 ...]"""
import os, sys, math, subprocess
import numpy as np
import render as R
import portada as P
from render import (Image, ImageDraw, ImageFilter, W, H, bg, put, text, panel, stamp, etiqueta, dust, neon_flicker,
                    dark, ease, clamp, popscale, euros, YEL, RED, WHITE, OL, CYAN, MAG, F_UI, F_ANTON)

HERE = R.HERE
VOZ = os.path.join(HERE, "voz_story", "voz.wav")
G_ = (46, 160, 90)
FPS = R.FPS
OUT = "story_parte1.mp4"

# tiempos de la voz (voz_story/voz.wav, atempo 1.1)
T_Q, T_NITRO, T_NUM0, T_NUM1, T_TALLER, T_COCHE = .12, 1.71, 2.4, 3.7, 4.0, 5.06
T_A, T_DEUDA, T_SOBRA, T_SEVA, T_B, T_PERS, T_SLAM = 6.94, 8.40, 10.5, 11.0, 12.25, 12.92, 13.5
T_COM, T_AOB, T_TU, T_HIST = 15.09, 15.62, 17.76, 18.41
T_SIN, T_NOHAY, T_SIG, T_END = 19.71, 20.76, 21.78, 22.36

SC_T = [0, 1.55, 6.75, 12.1, 14.95, 19.6]          # inicio de cada escena
IMPACTS = [.3, 1.85, T_NUM1, T_A, T_SOBRA, T_B, T_SLAM, T_COM, T_TU, T_NOHAY, T_SIG]
SFX = [("arranque", 1.5, 0), ("se_aleja", T_SEVA, 0), ("petardeo", 13.8, 0), ("arranque", 19.55, 1)]

def etiqueta(c, T, t0, *a, **k):
    if popscale(T, t0) > .02: R.etiqueta(c, T, t0, *a, **k)

def blank(): return Image.new("RGBA", (W, H), (0, 0, 0, 0))

def zoom_on(c, lay, ctr, s):
    """Compone una capa a pantalla completa escalada 's' alrededor de ctr."""
    if s <= .01: return
    if abs(s - 1) < .003: c.alpha_composite(lay); return
    sc = lay.resize((int(W * s), int(H * s)), Image.BILINEAR)
    ox, oy = int(ctr[0] - ctr[0] * s), int(ctr[1] - ctr[1] * s)
    sc = sc.crop((max(0, -ox), max(0, -oy), max(0, -ox) + W, max(0, -oy) + H))
    c.alpha_composite(sc, (max(0, ox), max(0, oy)))

_TIT = None
def titulo(c, T, t0, y=400):
    global _TIT
    if _TIT is None: _TIT = blank(); P._neon_titulo(_TIT, y)
    k = popscale(T, t0, .4)
    if k <= 0: return
    neon_flicker(c, T, (150, y - 160, 930, y + 160), MAG, 2)
    zoom_on(c, _TIT, (540, y), k)

def golpe(c, T, t0, s, y, size, col, stroke=10, rot=0):
    """Texto que cae de golpe desde grande (estilo sello) y luego respira."""
    if T < t0: return
    u = clamp((T - t0) / .2); k = 2.2 - 1.2 * ease(u)
    k *= 1 + .025 * math.sin((T - t0) * 5)
    lay = Image.new("RGBA", (1080, 400), (0, 0, 0, 0))
    text(ImageDraw.Draw(lay), (540, 200), s, size, col, stroke=stroke)
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC)
    lay = lay.resize((int(1080 * k), int(400 * k)), Image.BILINEAR)
    if u < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * u)))
    c.alpha_composite(lay, (int(540 - lay.width / 2), int(y - lay.height / 2)))

def billetes(c, T, t0, n=22):
    if T < t0: return
    rng = np.random.default_rng(9)
    for i in range(n):
        x0, sp, ph, dl = rng.uniform(60, 1020), rng.uniform(500, 800), rng.uniform(0, 6.3), rng.uniform(0, .8)
        tt = T - t0 - dl
        if tt < 0: continue
        y = 450 + tt * sp; x = x0 + 40 * math.sin(tt * 4 + ph)
        if y > 1700: continue
        a = 30 * math.sin(tt * 6 + ph); w, h = 90, 46
        bill = Image.new("RGBA", (w, h), (0, 0, 0, 0)); bd = ImageDraw.Draw(bill)
        bd.rounded_rectangle((0, 0, w - 1, h - 1), 6, fill=(70, 170, 100), outline=(20, 80, 40), width=3)
        bd.ellipse((w / 2 - 12, h / 2 - 12, w / 2 + 12, h / 2 + 12), outline=(20, 80, 40), width=3)
        bill = bill.rotate(a, expand=True, resample=Image.BICUBIC)
        c.alpha_composite(bill, (int(x - bill.width / 2), int(y)))

def underglow(c, T, x, y, w, col):
    v = .7 + .3 * math.sin(T * 9)
    ov = blank(); ImageDraw.Draw(ov).ellipse((x - w, y - 50, x + w, y + 50), fill=col + (int(170 * v),))
    c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(28)))

def llamas(c, T, t0, ex, ey, n=3, gap=.28):
    d = ImageDraw.Draw(c)
    for i in range(n):
        tt = t0 + i * gap
        if 0 <= T - tt < .13:
            k = max(.2, 1 - (T - tt) / .13)
            d.ellipse((ex - 10, ey - 34 * k, ex + 110 * k, ey + 34 * k), fill=(255, 150, 40))
            d.ellipse((ex + 5, ey - 18 * k, ex + 70 * k, ey + 18 * k), fill=(255, 240, 160))

def chispas(c, T, t0, x, y, n=30, dur=.6, col=(255, 200, 80)):
    if not (0 <= T - t0 < dur): return
    d = ImageDraw.Draw(c); u = (T - t0) / dur
    for i in range(n):
        a = -math.pi * (.1 + .8 * ((i * 37) % 100) / 100); v = 260 + (i * 53) % 240
        px = x + math.cos(a) * v * u * (1 if i % 2 else -1); py = y + math.sin(a) * v * u + 500 * u * u
        d.line((px, py, px - 12 * math.cos(a), py - 12 * math.sin(a)), fill=col, width=5)

def tinte(c, col, a): c.alpha_composite(Image.new("RGBA", (W, H), col + (a,)))

# ---------------------------------------------------------------- escenas
def sc_pregunta(T):
    c = bg("bg_taller", T, 0, 1.5, 1.2, 1.6, .5, .6); dark(c, 110)
    put(c, "deportivo", 540, 1180 + 6 * math.sin(T * 3), .9, alpha=.85)
    underglow(c, T, 540, 1330, 380, MAG)
    titulo(c, T, 0)
    golpe(c, T, .28, "¿QUÉ HARÍAS TÚ?", 640, 120, YEL)
    return c

def sc_oferta(T):
    s0 = SC_T[1]
    c = bg("bg_fachada", T, s0, 1.5, 1.6, 4.3, .5, 1.0); dark(c, 120)
    neon_flicker(c, T, (100, 300, 980, 900), MAG, 7)
    u = ease((T - s0) / .5)
    put(c, "nitro", 540, 760 + 380 * (1 - ease((T - 1.85) / .45)) + 4 * math.sin(T * 1.8), 1.0)
    cx = 540 + 1100 * (1 - u)
    underglow(c, T, cx, 1250, 420, CYAN)
    put(c, "coche_negro", cx, 1090, 1.0)
    llamas(c, T, s0 + .35, cx + 440, 1175, 2, .25)
    d = ImageDraw.Draw(c)
    k = popscale(T, T_NUM0 - .2, .35)
    if k > 0:
        v = int(90000 * ease((T - T_NUM0) / (T_NUM1 - T_NUM0))) if T > T_NUM0 else 0
        v = v // 1000 * 1000
        beat = 1 + .1 * max(0, 1 - (T - T_NUM1) / .25) if T >= T_NUM1 else 1
        d.rounded_rectangle((540 - 330 * k, 280, 540 + 330 * k, 430), 22, fill=G_, outline=OL, width=6)
        if k > .5: text(d, (540, 355), euros(v), 118 * beat, WHITE, stroke=6)
    billetes(c, T, T_NUM1)
    etiqueta(c, T, T_TALLER, "POR EL TALLER", 540, 495, YEL, OL, 40)
    if T >= T_COCHE: stamp(c, T, T_COCHE, "+ EL COCHE DE TU TÍO", 540, 1480, RED, -4, 70)
    return c

def sc_opcion_a(T):
    s0 = SC_T[2]
    c = bg("bg_fachada", T, s0, 1.35, 1.45, 5.3, .5, .9); dark(c, 70)
    tinte(c, (10, 60, 30), 70)
    put(c, "nitro", 250, 900 + 3 * math.sin(T * 2), .75)
    # el deportivo del tío se va con Nitro: arranca y sale disparado a la izquierda
    u = clamp((T - T_SEVA) / .9) ** 2
    x = 640 - 1500 * u
    if u > .05:
        d = ImageDraw.Draw(c)
        for i in range(7):
            yy = 1060 + i * 34; d.line((x + 470, yy, x + 470 + 380 * u, yy), fill=(255, 255, 255), width=4)
    put(c, "deportivo", x, 1140, .95)
    golpe(c, T, T_A, "A · ACEPTAS", 285, 130, WHITE, rot=4)
    # 90.000 - deuda 64.300 = te quedan 25.700
    k = popscale(T, T_A + .25, .35)
    if k > 0:
        v = 90000 - int(64300 * ease((T - T_DEUDA) / (T_SOBRA - T_DEUDA))) if T > T_DEUDA else 90000
        d = ImageDraw.Draw(c)
        d.rounded_rectangle((540 - 300 * k, 470, 540 + 300 * k, 600), 22, fill=G_, outline=OL, width=6)
        if k > .5: text(d, (540, 535), euros(v), 100 * (1 + .1 * max(0, 1 - (T - T_SOBRA) / .25) if T >= T_SOBRA else 1), WHITE, stroke=6)
    etiqueta(c, T, T_DEUDA, "- 64.300 € DE DEUDA", 540, 665, RED, WHITE, 38)
    if T >= T_SOBRA: etiqueta(c, T, T_SOBRA, "TE QUEDAN", 540, 410, YEL, OL, 34)
    if T >= T_SEVA + .4: stamp(c, T, T_SEVA + .4, "ADIÓS AL COCHE", 620, 820, RED, -10, 90)
    return c

def sc_opcion_b(T):
    s0 = SC_T[3]
    c = bg("bg_fachada", T, s0, 1.2, 1.12, 2.5, .5, .62)
    inner = bg("bg_taller", T, 0, 1.4, 1.4, 1, .5, .6).crop((150, 830, 930, 1400))
    put(inner, "deportivo", 390, 420, .55); c.alpha_composite(inner, (150, 830))
    tb = T_SLAM
    u = ease((T - T_PERS) / (tb - T_PERS))
    sh = 12 * math.sin(T * 70) * math.exp(-(T - tb) * 6) if T > tb else 0
    pers = R.scaled("persiana", 1.0); h = int(570 * u)
    if h > 2: c.alpha_composite(pers.crop((0, 570 - h, 780, 570)), (150 + int(sh), 830))
    chispas(c, T, tb, 540, 1395)
    put(c, "coche_negro", 300, 1610, .7)
    llamas(c, T, 13.85, 690, 1690, 3)
    tinte(c, (60, 10, 50), 50)
    golpe(c, T, T_B, "B · PERSIANA", 330, 130, WHITE, rot=-4)
    if T >= tb: stamp(c, T, tb, "EN LA CARA", 540, 600, MAG, 8, 110)
    return c

RAYO = R.RAYO
_LC = {}
def lado(n):
    if n not in _LC: _LC[n] = R._lado(n, 0)
    return _LC[n]

COMS = [("A sin dudarlo", 0), ("B B B", 1), ("la B obvio", 1), ("A, dinero es dinero", 0), ("B!!", 1), ("A", 0),
        ("ni loco vendo, B", 1), ("A y a otra cosa", 0), ("B por el tío", 1), ("A", 0), ("B", 1), ("la A bro", 0)]
def comentarios(c, T, t0):
    if T < t0: return
    f = R.font(F_UI, 30)
    for i, (s, lado_) in enumerate(COMS):
        tt = T - (t0 + i * .32)
        if not (0 <= tt < 1.6): continue
        y = 1530 - 270 * ease(tt / 1.6); a = clamp(min(tt / .2, (1.6 - tt) / .3))
        ov = blank(); od = ImageDraw.Draw(ov)
        tw = od.textlength(s, font=f) + 90
        x0 = 70 if lado_ == 0 else 1010 - tw
        od.rounded_rectangle((x0, y - 32, x0 + tw, y + 32), 32, fill=(255, 255, 255, int(235 * a)))
        col = MAG if lado_ else G_
        od.ellipse((x0 + 10, y - 22, x0 + 54, y + 22), fill=col + (int(255 * a),))
        od.text((x0 + 68, y), s, font=f, fill=OL + (int(255 * a),), anchor="lm")
        c.alpha_composite(ov)

def sc_comenta(T):
    s0 = SC_T[4]
    on = T >= T_AOB
    hiA = int((T - T_AOB) / .5) % 2 == 0 if on else False
    u = ease((T - s0) / .45)
    blk = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    c = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    A, B = lado("A"), lado("B")
    c.alpha_composite(Image.blend(B, blk, .35) if (on and hiA) else B, (int(500 * (1 - u)), 0))
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon([(0, 0)] + RAYO + [(0, H)], fill=255)
    c.paste(Image.blend(A, blk, .35) if (on and not hiA) else A, (int(-700 * (1 - u)), 0), mask)
    if u > .9:
        v = .6 + .4 * abs(math.sin(T * 13)) * abs(math.sin(T * 3.1))
        gl = blank(); ImageDraw.Draw(gl).line(RAYO, fill=CYAN + (int(255 * v),), width=44, joint="curve")
        c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(c)
        d.line(RAYO, fill=WHITE, width=12, joint="curve"); d.line(RAYO, fill=CYAN, width=5, joint="curve")
    d = ImageDraw.Draw(c)
    for cx, L_, t1, t2, t3, col, t0, h in ((270, "A", "VENDER", "+ 25.700 €", "- El coche, para Nitro", G_, s0 + .15, hiA),
                                           (790, "B", "QUEDARTE", "+ El coche del tío", "- Solo 410 €", MAG, s0 + .35, not hiA)):
        k = popscale(T, t0, .35)
        if k > 0: R._texto_opcion(d, cx, 420, L_, t1, t2, t3, col, k, 1.08 if (h and on) else 1.0)
    k = popscale(T, T_COM, .35)
    if k > 0:
        beat = 1 + .04 * math.sin((T - T_COM) * 7)
        lay = blank(); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((110, 1095, 970, 1205), 55, fill=WHITE, outline=OL, width=6)
        text(ld, (540, 1150), "COMENTA A o B EN LA PARTE 1", 56, OL)
        zoom_on(c, lay, (540, 1150), k * beat)
    comentarios(c, T, T_AOB)
    golpe(c, T, T_TU, "TÚ DECIDES", 820, 140, YEL, rot=-5)
    if T >= T_HIST: etiqueta(c, T, T_HIST, "CÓMO SIGUE LA HISTORIA", 540, 990, RED, WHITE, 40)
    return c

def sc_siguenos(T):
    s0 = SC_T[5]
    c = bg("bg_taller", T, s0, 1.25, 1.15, 3, .5, .62); dark(c, 120)
    ov = blank(); ImageDraw.Draw(ov).polygon([(420, 0), (660, 0), (1000, 1300), (80, 1300)], fill=(255, 230, 170, 45))
    c.alpha_composite(ov.filter(ImageFilter.GaussianBlur(30)))
    rev = 4 * math.sin(T * 40) * math.exp(-(T - s0 - .2) * 3) if T > s0 + .2 else 0
    underglow(c, T, 540, 1210, 420, MAG)
    put(c, "deportivo", 540 + rev, 1030, 1.0)
    titulo(c, T, s0 + .05)
    golpe(c, T, T_SIN, "SIN TUS COMENTARIOS", 620, 82, WHITE, 8)
    golpe(c, T, T_NOHAY, "NO HAY SERIE", 735, 110, RED, 9, rot=-3)
    # botón seguir: aparece, el dedo lo pulsa en "Síguenos" y pasa a SIGUIENDO
    k = popscale(T, T_NOHAY + .3, .35)
    if k > 0:
        done = T >= T_SIG + .25
        beat = 1 + (.05 * math.sin(T * 9) if not done else 0)
        press = 1 - .08 * math.sin(clamp((T - T_SIG) / .25) * math.pi)
        lay = blank(); ld = ImageDraw.Draw(lay)
        fill, fg, s = ((RED, WHITE, "+  SÍGUENOS") if not done else (WHITE, OL, "   SIGUIENDO"))
        ld.rounded_rectangle((210, 1340, 870, 1460), 60, fill=fill, outline=WHITE if not done else OL, width=6)
        text(ld, (540, 1400), s, 64, fg)
        if done: ld.line((330, 1400, 352, 1424, 390, 1376), fill=G_, width=12, joint="curve")
        zoom_on(c, lay, (540, 1400), k * beat * press)
        if T_SIG - .45 <= T < T_SIG + .9:   # dedo + onda de toque
            p = ease((T - (T_SIG - .45)) / .45)
            fx, fy = 760 + 160 * (1 - p), 1430 + 160 * (1 - p)
            if T >= T_SIG:
                r_ = 30 + 220 * clamp((T - T_SIG) / .5); a = int(255 * (1 - clamp((T - T_SIG) / .5)))
                ov = blank(); ImageDraw.Draw(ov).ellipse((fx - r_, fy - r_, fx + r_, fy + r_), outline=(255, 255, 255, a), width=8)
                c.alpha_composite(ov)
            ImageDraw.Draw(c).ellipse((fx - 38, fy - 38, fx + 38, fy + 38), fill=(255, 255, 255, 230), outline=OL, width=5)
    return c

SCENES = [sc_pregunta, sc_oferta, sc_opcion_a, sc_opcion_b, sc_comenta, sc_siguenos]

def frame(T):
    i = max(j for j, t in enumerate(SC_T) if T >= t)
    c = SCENES[i](T)
    dust(c, T, 30)
    if i > 0 and T - SC_T[i] < .18:   # barrido rápido con desenfoque al entrar en cada escena
        u = (T - SC_T[i]) / .18
        c = R.hblur(c, int(40 * (1 - u))); c2 = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        c2.alpha_composite(c, (int(-160 * (1 - u)), 0)); c = c2
    sh = 0
    for t in IMPACTS:                 # golpe de cámara + destello
        if 0 <= T - t < .35:
            sh += 16 * math.exp(-(T - t) * 10)
            if T - t < .08: tinte(c, (255, 255, 255), int(110 * (1 - (T - t) / .08)))
    if sh > .5:
        z = 1 + sh / 400
        c = c.resize((int(W * z), int(H * z)), Image.BILINEAR)
        ox = int((c.width - W) / 2 + sh * math.sin(T * 90)); oy = int((c.height - H) / 2 + sh * math.cos(T * 77))
        c = c.crop((ox, oy, ox + W, oy + H))
    c.alpha_composite(R.grains()[int(T * FPS) % 4]); c.alpha_composite(R.VIG)
    return c.convert("RGB")

def main():
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", VOZ])) + .55
    if len(sys.argv) > 1 and sys.argv[1] == "still":
        ims = [frame(float(t)).resize((270, 480)) for t in sys.argv[2:]]
        o = Image.new("RGB", (270 * len(ims), 480)); [o.paste(im, (i * 270, 0)) for i, im in enumerate(ims)]
        o.save("/tmp/strip.jpg"); return
    tmp = "/tmp/sv"; os.makedirs(tmp, exist_ok=True); [os.remove(os.path.join(tmp, f)) for f in os.listdir(tmp)]
    for i in range(int(dur * FPS)): frame(i / FPS).save(f"{tmp}/{i:05d}.jpg", quality=92)
    ins, fc, labs = ["-i", VOZ], "[1:a]loudnorm=I=-15:TP=-1.5[v];", []
    for j, (n, t, db) in enumerate(SFX):
        ins += ["-i", os.path.join(HERE, "sfx", n + ".wav")]; ms = int(t * 1000)
        fc += f"[{j + 2}:a]loudnorm=I=-26,volume={db}dB,adelay={ms}|{ms}[s{j}];"; labs.append(f"[s{j}]")
    fc += f"[v]{''.join(labs)}amix=inputs={len(labs) + 1}:duration=first:normalize=0,alimiter=limit=0.95[a]"
    out = os.path.join(HERE, OUT)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", f"{tmp}/%05d.jpg", *ins,
                    "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-t", f"{dur:.2f}", out], check=True)
    print(out, dur)

if __name__ == "__main__":
    main()
