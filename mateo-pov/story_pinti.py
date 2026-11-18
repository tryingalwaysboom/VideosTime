"""Story emocional de la serie de Mateo: hueco central para el sticker de ENCUESTA + pastilla 'sígueme para no perder la próxima parte'.
Voz: descargas/mateo_story/S01.mp3 (Lily, narradora de la serie). Sin voz usa duración estimada y sale mudo."""
import math, os, subprocess, sys
sys.argv, _a = sys.argv[:1], sys.argv[1:]
import render5 as V
from render5 import *
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); FPS = 30
VOZ = os.path.join(HERE, "..", "descargas", "pinti_story", "V01.mp3")
import json, unicodedata
RR = V.R
WORDS = json.load(open(os.path.join(HERE, "..", "descargas", "pinti_story", "V01.json"), encoding="utf-8")); OFF = .15
for _w in WORDS: _w["p"] = {"Ese": "Es el", "Pinty.": "Pinti."}.get(_w["p"], _w["p"])   # adelay del mix
def _n(w): return "".join(ch for ch in unicodedata.normalize("NFD", w.lower()) if ch.isalnum() and not unicodedata.combining(ch))
def tw(p): return next(w["inicio"] for w in WORDS if _n(w["p"]) == _n(p)) + OFF
def _grupos():
    out, cur = [], []
    for i, w in enumerate(WORDS):
        cur.append(i)
        if sum(len(WORDS[x]["p"]) + 1 for x in cur) >= 14 or w["p"].endswith((".", ",", ":", "?", "!")): out.append(cur); cur = []
    if cur: out.append(cur)
    return out
GRUPOS = _grupos()

def caption(c, t):
    """Mismo subtítulo que los vídeos de la serie: Anton 96 px, mayúsculas, palabra activa en amarillo con salto, contorno negro."""
    for gi, g in enumerate(GRUPOS):
        t0 = WORDS[g[0]]["inicio"] + OFF; t1 = WORDS[g[-1]]["fin"] + OFF
        nxt = WORDS[GRUPOS[gi + 1][0]]["inicio"] + OFF if gi + 1 < len(GRUPOS) else 1e9
        if not (t0 - .04 <= t < t1 + .35) or t >= nxt - .04: continue
        d = ImageDraw.Draw(c); k = .85 + .15 * RR.back((t - t0 + .04) / .14); f = font(F_ANTON, 96 * k)
        ps = [WORDS[i]["p"].upper() for i in g]; wd = [d.textlength(p + " ", font=f) for p in ps]; tot = sum(wd) - d.textlength(" ", font=f)
        sc = min(1.0, 820 / tot)
        if sc < 1: f = font(F_ANTON, 96 * k * sc); wd = [d.textlength(p + " ", font=f) for p in ps]; tot = sum(wd) - d.textlength(" ", font=f)
        x = W / 2 - tot / 2; y = 1480; st = [WORDS[i]["inicio"] + OFF for i in g] + [1e9]
        for j, (i, p) in enumerate(zip(g, ps)):
            ws, we = WORDS[i]["inicio"] + OFF, WORDS[i]["fin"] + OFF; fin_ = min(st[j + 1], we + .35) if j + 1 < len(g) else we + .35
            act = ws - .03 <= t < fin_ - .03; dicha = t >= ws - .03; col = RR.YEL if act else (WHITE if dicha else (225, 225, 230))
            if act:
                u = RR.clamp((t - ws + .03) / .12); fa = font(F_ANTON, f.size * (1 + .06 * math.sin(u * math.pi)))
                d.text((x + (wd[j] - d.textlength(" ", font=f)) / 2, y), p, font=fa, fill=col, anchor="mm", stroke_width=10, stroke_fill=(10, 10, 20))
            else: d.text((x, y), p, font=f, fill=col, anchor="lm", stroke_width=9, stroke_fill=(10, 10, 20))
            x += wd[j]
        return

ORG, ORG2, NV = (244, 124, 42), (255, 160, 70), (22, 36, 66)
def tw(p, i=0):
    ms = [w for w in WORDS if _n(w["p"]) == _n(p)]; return ms[i]["inicio"] + OFF
T_MIRA, T_ES, T_109, T_LET, T_TRAZO, T_FLE, T_SIL, T_HOJ, T_LO, T_SOLO, T_SIN, T_MISMO, T_SI = (tw("Mira") - .1, tw("Es", 0) - .2, tw("109") - .3, tw("Letras") - .2, tw("trazo", 0), tw("flechas"), tw("Sílabas") - .2, tw("hojas") - .15, tw("Lo") - .2, tw("solito") - .5, tw("sin") - .15, tw("mismo") - .5, tw("Si") - .2)
PW = lambda n: V.pagina_img(n, 1.0).size

def txt(c, xy, t, sz, fill=WHITE, stroke=8, f=None):
    d = ImageDraw.Draw(c); fn = font(f or F_ANTON, sz)
    for i, ln in enumerate(t.split("\n")):
        d.text((xy[0], xy[1] + i * sz * 1.18), ln, font=fn, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=(20, 14, 30))

def fondo(t, D, name="bg_mesa", tint=(255, 214, 160, 40)):
    c = V.bg(name, t, 0, 1.15, 1.25, D * .3, .5, .55).convert("RGBA"); c.alpha_composite(Image.new("RGBA", (W, H), tint)); return c

def pag(c, n, cx, cy, s, rot=0, sombra=True):
    w, h = PW(n); im = V.pagina_img(n, s)
    if rot: im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if sombra:
        sh = Image.new("RGBA", (im.width + 60, im.height + 60), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle((30, 30, im.width + 30, im.height + 30), fill=(30, 20, 40, 120))
        c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)), (int(cx - im.width / 2 - 30 + 12), int(cy - im.height / 2 - 30 + 16)))
    c.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
    return lambda x, y: (cx + (x - w / 2) * s, cy + (y - h / 2) * s)

def retrato(c, kind, t, cx=540, cy=700, sc=.6):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); V.mateo(lay, kind, cx, cy, sc, t)
    from PIL import ImageChops
    m = Image.new("L", (W, H), 255); md = ImageDraw.Draw(m)
    for y in range(cy + 40, cy + 150): md.line((0, y, W, y), fill=int(255 * max(0, 1 - (y - cy - 40) / 110)))
    md.rectangle((0, cy + 150, W, H), fill=0); lay.putalpha(ImageChops.multiply(lay.split()[3], m)); c.alpha_composite(lay)

def sticker(c, cx, cy, t1, t2, rot, k=1.0, col=ORG):
    lay = Image.new("RGBA", (700, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((20, 40, 680, 260), 60, fill=col, outline=WHITE, width=8)
    d.text((350, 105), t1, font=font(F_ANTON, 100), fill=WHITE, anchor="mm", stroke_width=5, stroke_fill=(150, 60, 10))
    d.text((350, 205), t2, font=font(F_BAL, 56), fill=(255, 240, 220), anchor="mm")
    lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC); lay = lay.resize((int(lay.width * k), int(lay.height * k)), Image.LANCZOS)
    c.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def esc_hook(t, D):
    c = fondo(t, D, "bg_cuarto"); retrato(c, "timido", t, 540, 780, .62)
    k = ease(min(1, t / .35)); txt(c, (540, 330), "¿TU HIJO NO SABE\nCÓMO EMPEZAR?", int(86 * (.9 + .1 * k)), WHITE, 10)
    return c

def esc_libro(t, D):
    c = fondo(t, D, "bg_mesa", (22, 36, 66, 90)); u = ease((t - T_MIRA) / .5)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = 110, 430 + 60 * (1 - u), 970, 1130 + 60 * (1 - u)
    d.rounded_rectangle((x0, y0 + 14, x1, y1 + 14), 70, fill=(0, 0, 0, 120)); d.rounded_rectangle((x0, y0, x1, y1), 70, fill=NV, outline=WHITE, width=7)
    for i, (ln, f_, sz, yy, col) in enumerate((("MÉTODO PASO A PASO", F_BAL, 36, 490, ORG2), ("Aprende a leer", F_ANTON, 100, 600, WHITE), ("y escribir", F_ANTON, 100, 725, WHITE), ("con Pinti", F_BAL, 76, 840, (255, 214, 120)))):
        d.text((540, yy + 60 * (1 - u)), ln, font=font(f_, sz), fill=col, anchor="mm")
    if u < 1: lay.putalpha(lay.split()[3].point(lambda v: int(v * u)))
    c.alpha_composite(lay)
    V.pinti(c, 760, 1090 + 14 * math.sin(t * 3), 360, rot=6 * math.sin(t * 2))
    return c

def esc_abanico(t, D):
    c = fondo(t, D, "bg_mesa", (22, 36, 66, 90)); u = ease((t - T_109 + .3) / .6)
    for i, (n, dx, rot) in enumerate(((3, -250, -9), (15, 0, 0), (39, 250, 9))):
        k = ease((t - T_109 + .3 - i * .12) / .5); pag(c, n, 540 + dx * k, 800 + 40 * (1 - k), .66, rot * k)
    sticker(c, 540, 1230, "109 PÁGINAS", "listas para imprimir", -4, 1.0 + .04 * math.sin(t * 5))
    return c

def esc_trazos(t, D):
    c = fondo(t, D, "bg_mesa", (255, 214, 160, 30)); k = ease((t - T_LET + .2) / .5)
    mp = pag(c, 15, 540, 900 + 50 * (1 - k), .72)
    st = [s for g in V.pagina_trazos_E(mp) for s in g]
    d = ImageDraw.Draw(c); u = RR.clamp((t - T_TRAZO + .3) / 3.6) * len(st)
    for i, s in enumerate(st[:8]):
        f = RR.clamp(u - i)
        if f <= 0: continue
        (xa, ya), (xb, yb) = s[0], s[-1]; xe, ye = xa + (xb - xa) * f, ya + (yb - ya) * f
        d.line((xa, ya, xe, ye), fill=(60, 180, 90), width=14); d.ellipse((xa - 10, ya - 10, xa + 10, ya + 10), fill=(60, 180, 90))
        if f < 1: d.ellipse((xe - 16, ye - 16, xe + 16, ye + 16), fill=(255, 160, 70), outline=WHITE, width=4)
    txt(c, (540, 310), "TRAZO A TRAZO", 80, (255, 226, 170), 9)
    return c

def esc_silabas(t, D):
    c = fondo(t, D, "bg_mesa", (255, 214, 160, 30))
    if t < T_HOJ:
        k = ease((t - T_SIL + .2) / .5); pag(c, 55, 540, 900 + 50 * (1 - k), .72); txt(c, (540, 330), "SÍLABAS Y PALABRAS", 74, (255, 226, 170), 9)
    else:
        k = ease((t - T_HOJ + .15) / .5); pag(c, 85, 540, 900 + 50 * (1 - k), .72); txt(c, (540, 330), "HOJAS DE PRÁCTICA", 74, (255, 226, 170), 9)
    return c

def esc_imprime(t, D):
    c = fondo(t, D, "bg_mesa", (22, 36, 66, 80)); V.impresora(c, t, T_LO + .1, 15)
    n = int(max(0, (t - T_LO - 1.6) * 1.6)) + 1
    if t > T_LO + 1.6: sticker(c, 540, 330, "¡TODAS LAS VECES!", "imprime sin límite", 3, .9 + .03 * math.sin(t * 6), (60, 160, 90))
    return c

def esc_solo(t, D):
    c = fondo(t, D, "bg_cuarto"); retrato(c, "feliz", t, 540, 780, .62)
    d = ImageDraw.Draw(c)
    if t >= T_SIN:
        k = ease((t - T_SIN) / .35); cx, cy = 540, 1160; s = 1.0 + .06 * math.sin(t * 5)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((cx - 55, cy - 95, cx + 55, cy + 95), 20, fill=(40, 44, 66), outline=WHITE, width=6); ld.rounded_rectangle((cx - 42, cy - 72, cx + 42, cy + 62), 8, fill=(120, 170, 230))
        ld.line((cx - 120, cy - 120, cx + 120, cy + 120), fill=(230, 50, 60), width=22); ld.ellipse((cx - 140, cy - 140, cx + 140, cy + 140), outline=(230, 50, 60), width=20)
        lay = lay.resize((int(W * s), int(H * s)), Image.LANCZOS); lay = lay.crop((int((lay.width - W) / 2), int((lay.height - H) / 2), int((lay.width + W) / 2), int((lay.height + H) / 2)))
        lay.putalpha(lay.split()[3].point(lambda v: int(v * k))); c.alpha_composite(lay)
    txt(c, (540, 330), "TU HIJO PRACTICA SOLITO", 66, WHITE, 9)
    return c

def esc_mateo(t, D):
    c = fondo(t, D, "bg_cuarto", (255, 190, 120, 50)); retrato(c, "feliz", t, 360, 800, .55)
    k = ease((t - T_MISMO + .5) / .5); pag(c, 15, 760, 800 + 40 * (1 - k), .5, 6)
    txt(c, (540, 330), "EL LIBRO DE MATEO", 82, (255, 226, 170), 10)
    if t >= T_SI:
        kk = ease((t - T_SI) / .5); pw, ph = 800, 140; y = 1190 + 40 * (1 - kk)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((540 - pw / 2, y + 10, 540 + pw / 2, y + ph + 10), 70, fill=(0, 0, 0, 130))
        ld.rounded_rectangle((540 - pw / 2, y, 540 + pw / 2, y + ph), 70, fill=ORG, outline=WHITE, width=5)
        ld.text((540, y + ph / 2 - 8), "LINK EN MI BIO", font=font(F_ANTON, 78), fill=WHITE, anchor="mm")
        off = 8 * math.sin(t * 5); ld.polygon([(540 - 30, y - 22 + off), (540 + 30, y - 22 + off), (540, y - 62 + off)], fill=WHITE, outline=(20, 14, 30))
        if kk < 1: lay.putalpha(lay.split()[3].point(lambda v: int(v * kk)))
        c.alpha_composite(lay)
    return c

ESC = [(0, esc_hook), (T_MIRA, esc_libro), (T_109, esc_abanico), (T_LET, esc_trazos), (T_SIL, esc_silabas), (T_LO, esc_imprime), (T_SOLO, esc_solo), (T_MISMO, esc_mateo)]
ease = V.ease

def frame(t, D):
    i = max(j for j, (a, _) in enumerate(ESC) if t >= a - (0 if j == 0 else .0)); ta, fn = ESC[i]
    c = fn(t, D)
    if i > 0 and t < ta + .25:   # fundido cruzado corto desde la escena anterior
        prev = ESC[i - 1][1](t, D); a = (t - ta) / .25; c = Image.blend(prev.convert("RGBA"), c.convert("RGBA"), max(0, min(1, a)))
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for y in range(H):
        a = max(0, 150 - y * .35) if y < 430 else (max(0, (y - 1350) * .32) if y > 1350 else 0)
        gd.line((0, y, W, y), fill=(14, 8, 30, int(min(190, a))))
    c = c.convert("RGBA"); c.alpha_composite(g); caption(c, t)
    return c.convert("RGB")

def dur():
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", VOZ], capture_output=True, text=True); return float(r.stdout.strip())

if __name__ == "__main__":
    D = dur() + .9
    if _a and _a[0] == "still":
        for t in _a[1:]: frame(float(t), D).save(f"/tmp/sp_{float(t):05.1f}.jpg", quality=88)
        sys.exit()
    out = os.path.join(HERE, "out"); os.makedirs(out, exist_ok=True); tmp = os.path.join(out, "_sp_mudo.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for i in range(int(D * FPS)): p.stdin.write(frame(i / FPS, D).tobytes())
    p.stdin.close(); p.wait(); fin = os.path.join(out, "story_pinti_venta.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-i", VOZ, "-af", "adelay=150|150,loudnorm=I=-15:TP=-1.5,aresample=48000,apad", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", fin], check=True); os.remove(tmp); print("ok", fin)
