"""Gancho de la Parte 1 (estilo gafas con cámara, visión nocturna): golpes, susurro "ábreme…" y "sabe mi nombre"."""
import math, os, subprocess
import numpy as np
from PIL import Image, ImageDraw
import art as A, ep1 as E, bodycam as BC
from ep1 import W, H, FPS, cam, text, flash, ease, clamp, YEL, OL
from art import font, F_ANTON, F_UI
T_ = E.TMP; G = os.path.join(E.SRC, "G01.mp3"); WH = os.path.join(E.SRC, "G02.mp3")
A0, A1, B0, B1, W0, W1 = .12, 2.19, 2.776, 3.81, .218, 1.279
tA, tW, tB = 0.0, 2.2, 3.4
DUR = tB + (B1 - B0) + .35
t_eyes = tB + .55
KN = [.08, .5, .88]
CAPS = [(["Algo", "debajo", "del", "suelo", "de", "mi", "casa…"], tA, A1 - A0), (["sabe", "mi", "nombre."], tB, B1 - B0)]

# rendija bajo el borde de la trampilla (se levanta un poco) y ojos
TR = A.TRAP
def ojos(c_pl, t):
    d = ImageDraw.Draw(c_pl)
    p0, p1 = A.quad_pt(TR, .2, 0), A.quad_pt(TR, .8, 0)
    gap = 6 + 16 * clamp((t - tW) / 1.0)
    pts = [p0] + [(lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u) - 3 * math.sin(u * 40)) for u in np.linspace(0, 1, 30)] + [p1, (p1[0] - 40, p1[1] + gap * .5)] + [(lerp(p1[0], p0[0], u), lerp(p1[1], p0[1], u) + gap * (1 - abs(u - .5) * 1.2) + 2 * math.sin(u * 33)) for u in np.linspace(0, 1, 30)] + [(p0[0] + 40, p0[1] + gap * .5)]
    d.polygon(pts, fill=(4, 4, 6))
    if t >= t_eyes:
        o = ease((t - t_eyes) / .25); cx = (p0[0] + p1[0]) / 2; cy = p0[1] + gap / 2
        for ex in (-60, 60):
            g = Image.new("RGBA", c_pl.size, (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((cx + ex - 60, cy - 34, cx + ex + 60, cy + 34), fill=(255, 255, 255, int(190 * o)))
            c_pl.alpha_composite(g.filter(__import__("PIL.ImageFilter", fromlist=["x"]).GaussianBlur(10)))
            d = ImageDraw.Draw(c_pl); hh = max(1, 8 * o)
            d.ellipse((cx + ex - 26, cy - hh, cx + ex + 26, cy + hh), fill=(255, 255, 240)); d.ellipse((cx + ex - 5, cy - hh * .9, cx + ex + 5, cy + hh * .9), fill=(10, 10, 10))

def escena(t):
    shake = max([1 - (t - k) / .3 for k in KN + [t_eyes] if 0 <= t - k < .3] + [0])
    pl = A.plate_trampilla().copy(); ojos(pl, t)
    if t < t_eyes: z = 1.3 + .35 * ease(t / t_eyes); cx, cy = 648, 1150 - 120 * ease(t / t_eyes)
    else: u = ease((t - t_eyes) / .4); z = lerp(1.65, 2.6, u); cx, cy = 648, lerp(1030, 1040, u)
    return cam(pl, z, cx, cy, rot=3 * shake * math.sin(t * 50), sx=26 * shake * math.sin(t * 95), sy=28 * shake * math.cos(t * 80))
def lerp(a, b, u): return a + (b - a) * u

def glitch(t):
    ev = [(k, 1.0) for k in KN] + [(tW, .8), (t_eyes, 1.0), (DUR - .25, 1.0)]
    return max([g * (1 - (t - e) / .18) for e, g in ev if 0 <= t - e < .18] + [0.0])

def frame(t):
    g = glitch(t); c = BC.lente(escena(t), t, g, True); BC.interfaz(c, t, (3, 0, 41), True, g)
    c.alpha_composite(E.banda()); d = ImageDraw.Draw(c)
    for ws, t0, dur in CAPS:
        if not (t0 - .05 <= t < t0 + dur + .3): continue
        lens = [len(w) + 1 for w in ws]; tot = sum(lens); acc = 0; tw = []
        for L in lens: tw.append(t0 + dur * acc / tot); acc += L
        lines = [ws] if len(ws) <= 3 else [ws[:4], ws[4:]]
        y = 1490 if len(lines) == 1 else 1440; i = 0
        for ln in lines:
            f = font(F_ANTON, 92); ls = [d.textlength(w + " ", font=f) for w in ln]; x = W / 2 - (sum(ls) - d.textlength(" ", font=f)) / 2
            for w, L in zip(ln, ls):
                col = YEL if tw[i] - .03 <= t else (215, 215, 222)
                d.text((x, y), w, font=f, fill=col, anchor="lm", stroke_width=10, stroke_fill=OL); x += L; i += 1
            y += 104
    if tW - .05 <= t < tW + (W1 - W0) + .25:   # el susurro
        k = clamp((t - tW) / .3); jit = 4 * math.sin(t * 70)
        d.text((W / 2 + jit, 760), "…ábreme…", font=font(F_ANTON, 120), fill=(220, 255, 220, int(230 * k)), anchor="mm", stroke_width=6, stroke_fill=(0, 20, 0))
    flash(c, t, t_eyes, .12, (255, 255, 255), 170)
    a = np.asarray(c.convert("RGB"), np.int16) + E.grain(int(t * FPS) % 6)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        for q in (.5, 2.6, 4.3): frame(q).resize((360, 640)).save(f"/tmp/hk_{q}.jpg")
        sys.exit()
    part = os.path.join(T_, "hook2.part.mp4"); vid = os.path.join(T_, "hook2_v.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", part], stdin=subprocess.PIPE)
    for f in range(round(DUR * FPS)): p.stdin.write(frame(f / FPS).tobytes())
    p.stdin.close(); p.wait(); os.replace(part, vid)
    sfx = lambda n: os.path.join(E.SFXD, n + ".mp3")
    ms = lambda t: int(t * 1000)
    flt = [f"[0]atrim={A0}:{A1},asetpts=PTS-STARTPTS,aresample=48000,adelay={ms(tA)}|{ms(tA)},apad[a]",
           f"[0]atrim={B0}:{B1},asetpts=PTS-STARTPTS,aresample=48000,adelay={ms(tB)}|{ms(tB)},apad[b]",
           f"[a][b]amix=inputs=2:normalize=0,atrim=0:{DUR + 4:.2f},acompressor=threshold=-18dB:ratio=3,loudnorm=I=-15:TP=-1.5:LRA=9,atrim=0:{DUR:.2f}[v]",
           f"[1]atrim={W0}:{W1},asetpts=PTS-STARTPTS,aresample=48000,lowpass=f=2600,aecho=0.8:0.7:60|140:0.45|0.3,loudnorm=I=-19:TP=-4,adelay={ms(tW)}|{ms(tW)},apad[w]"]
    items = [(sfx("golpes"), 0.0, -2), (sfx("boom"), t_eyes - .02, 1), (sfx("whoosh"), DUR - .3, -2)]
    ins = ["-i", G, "-i", WH]
    for k, (pth, t0, db) in enumerate(items):
        ins += ["-i", pth]; flt.append(f"[{k + 2}:a]aresample=48000,loudnorm=I=-26:TP=-6,volume={db}dB,adelay={ms(t0)}|{ms(t0)},apad[s{k}]")
    flt.append("[v][w]" + "".join(f"[s{k}]" for k in range(len(items))) + f"amix=inputs={len(items) + 2}:normalize=0:duration=longest,atrim=0:{DUR:.2f},alimiter=limit=0.95,aformat=channel_layouts=stereo[m]")
    wav = os.path.join(T_, "hook2.wav"); subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(flt), "-map", "[m]", wav], check=True)
    print("ok", DUR)
