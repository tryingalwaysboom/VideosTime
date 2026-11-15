"""Story animado con voz (CTA parte 1). python3 story_video.py <tiempos: q,car,A,B,com,sig>"""
import os, sys, json, subprocess, math
from PIL import Image, ImageDraw, ImageFilter
import render as r
import portada as P

HERE = r.HERE
VOZ = os.path.join(HERE, "voz_story", "voz.wav")
T = dict(zip(["q", "car", "A", "B", "com", "sig"], map(float, sys.argv[1].split(","))))

def layer():
    return Image.new("RGBA", (r.W, r.H), (0, 0, 0, 0))

def base():
    c = r.bg("bg_taller", 0, 0, 1.2, 1.2, 1, .5, .62); r.dark(c, 140)
    gl = layer(); ImageDraw.Draw(gl).ellipse((-100, 1000, 1180, 1400), fill=r.MAG + (90,))
    c.alpha_composite(gl.filter(ImageFilter.GaussianBlur(70)))
    P._neon_titulo(c, 400)
    return c

def L_preg():
    c = layer(); r.text(ImageDraw.Draw(c), (540, 600), "¿QUÉ HARÍAS TÚ?", 96, r.YEL, stroke=9); return c, (540, 600)

def L_opt(y, L_, t1, t2, col):
    c = layer(); r.panel(c, (90, y - 70, 990, y + 70), fill=(16, 14, 30), alpha=235, rad=28, outline=col, ow=6)
    d = ImageDraw.Draw(c); d.rounded_rectangle((112, y - 50, 212, y + 50), 22, fill=col)
    r.text(d, (162, y), L_, 76, r.WHITE); r.text(d, (240, y - 20), t1, 52, r.WHITE, "lm")
    r.text(d, (240, y + 34), t2, 30, r.YEL, "lm", r.F_UI); return c, (540, y)

def L_car():
    c = layer(); P._suelo_reflejo(c, "deportivo", 540, 1130, .78); return c

def L_com():
    c = layer(); d = ImageDraw.Draw(c)
    d.rounded_rectangle((120, 1330, 960, 1440), 55, fill=r.WHITE, outline=r.OL, width=6)
    r.text(d, (540, 1385), "COMENTA A o B EN LA PARTE 1", 54, r.OL); return c, (540, 1385)

def L_sig():
    c = layer(); d = ImageDraw.Draw(c)
    d.rounded_rectangle((150, 1475, 930, 1565), 45, fill=r.RED, outline=r.WHITE, width=6)
    r.text(d, (540, 1520), "SÍGUENOS · TÚ DECIDES CÓMO SIGUE", 46, r.WHITE); return c, (540, 1520)

def pop(c, lay, ctr, t, t0, pulse=False):
    """Aparece con rebote (escala 0.4→1.08→1) centrado en ctr."""
    k = (t - t0) / .28
    if k <= 0: return
    if k < 1: s = .4 + .68 * math.sin(min(k / .7, 1) * math.pi / 2) - .08 * max(0, k - .7) / .3
    else: s = 1.0
    if pulse and t > t0 + .4: s *= 1 + .035 * math.sin((t - t0) * 6)
    if abs(s - 1) < .002: c.alpha_composite(lay); return
    sc = lay.resize((int(r.W * s), int(r.H * s)), Image.BILINEAR)
    ox, oy = int(ctr[0] - ctr[0] * s), int(ctr[1] - ctr[1] * s)
    sc = sc.crop((max(0, -ox), max(0, -oy), max(0, -ox) + r.W, max(0, -oy) + r.H))
    c.alpha_composite(sc, (max(0, ox), max(0, oy)))

def main():
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", VOZ])) + .6
    B = base(); preg = L_preg(); car = L_car()
    A = L_opt(730, "A", "VENDER A NITRO", "+25.700 € · pierdes el coche", (46, 160, 90))
    Bo = L_opt(900, "B", "CERRARLE LA PERSIANA", "410 € · te quedas el coche", r.MAG)
    com = L_com(); sig = L_sig()
    os.makedirs("/tmp/sv", exist_ok=True)
    n = int(dur * r.FPS)
    for i in range(n):
        t = i / r.FPS; c = B.copy()
        pop(c, *preg, t, T["q"])
        # coche entra deslizando desde la derecha
        k = (t - T["car"]) / .45
        if k > 0:
            e = 1 - (1 - min(k, 1)) ** 3; dx = int((1 - e) * 1100)
            c.alpha_composite(car, (dx, 0)) if dx == 0 else c.alpha_composite(car.crop((0, 0, r.W - dx, r.H)), (dx, 0))
        pop(c, *A, t, T["A"]); pop(c, *Bo, t, T["B"])
        pop(c, *com, t, T["com"], pulse=True); pop(c, *sig, t, T["sig"], pulse=True)
        c.alpha_composite(r.VIG); c.convert("RGB").save(f"/tmp/sv/{i:05d}.jpg", quality=92)
    sx = os.path.join(HERE, "sfx", "arranque.wav")
    out = os.path.join(HERE, "story_parte1.mp4")
    ms = int(max(0, T["car"] - .2) * 1000)
    fc = (f"[1:a]loudnorm=I=-15:TP=-1.5[v];[2:a]loudnorm=I=-26,volume=-2dB,adelay={ms}|{ms}[s];"
          f"[v][s]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(r.FPS), "-i", "/tmp/sv/%05d.jpg", "-i", VOZ, "-i", sx,
                    "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-t", f"{dur:.2f}", out], check=True)
    print(out, dur)

if __name__ == "__main__":
    main()
