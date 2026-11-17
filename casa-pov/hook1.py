"""Gancho de apertura (~4 s) para la Parte 1: candado nuevo + 37 años vacía. Se pega delante del episodio."""
import math, os, subprocess
from PIL import Image, ImageDraw
import art as A, ep1 as E
from ep1 import W, H, FPS, cam, paste_c, text, flash, back, ease, clamp, linterna, finish, YEL, WHITE, OL, RED
from art import font, F_ANTON, F_UI
T = E.TMP; V6 = os.path.join(E.VOZ, "C06.wav"); S6 = E.S("C06")
# voz: "Con un candado nuevo." + "esta casa lleva 37 años vacía."
SEG = [(1.36, 2.84), (3.44, 5.83)]
voz = os.path.join(T, "hook_voz.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", V6, "-filter_complex",
                f"[0]atrim={SEG[0][0]}:{SEG[0][1]},asetpts=PTS-STARTPTS[a];[0]atrim={SEG[1][0]}:{SEG[1][1]},asetpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=0:a=1", voz], check=True)
D1 = SEG[0][1] - SEG[0][0]; DUR = D1 + SEG[1][1] - SEG[1][0] + .25
def wt(i):   # tiempo de la palabra i de C06 dentro del gancho
    t = E.words("C06")[i][1] - S6
    return t - SEG[0][0] if t < SEG[0][1] else D1 + t - SEG[1][0]
CAP = [(["Con", "un", "candado", "nuevo."], [3, 4, 5, 6]), (["esta", "casa", "lleva"], [8, 9, 10]), (["37", "años", "vacía."], [11, 12, 13])]
KN = [.05, .5, .9]
SELLO = A.sello("37 AÑOS", "VACÍA", rot=-8, s=1.35)
hx, hy = A.quad_pt(A.TRAP, .82, .5)

def frame(t):
    shake = max([1 - (t - k) / .3 for k in KN if 0 <= t - k < .3] + [0])
    z = 2.25 + .25 * ease(t / DUR); cx, cy = hx + 40, hy + 190
    pl = A.plate_trampilla().copy(); A.candado(pl, hx + 50, hy + 40, 1.0, .6 + .4 * math.sin(t * 9))
    c = cam(pl, z, cx, cy, rot=3 * shake * math.sin(t * 50), sx=24 * shake * math.sin(t * 95), sy=26 * shake * math.cos(t * 80))
    linterna(c, W / 2 + 30 * math.sin(t * 2), 760, 520, 215)
    d = ImageDraw.Draw(c)
    tn = wt(5)
    if t >= tn and t < wt(11):   # etiqueta "NUEVO" con flecha
        k = min(1, back((t - tn) / .25)); d.rounded_rectangle((W / 2 + 170, 430, W / 2 + 470, 530), 20, fill=(255, 206, 60))
        d.text((W / 2 + 320, 480), "NUEVO", font=font(F_ANTON, 70 * k), fill=OL, anchor="mm")
        d.line((W / 2 + 180, 520, W / 2 + 70, 640), fill=(255, 206, 60), width=12); d.polygon([(W / 2 + 50, 670), (W / 2 + 60, 610), (W / 2 + 110, 640)], fill=(255, 206, 60))
    t37 = wt(11)
    if t >= t37:
        paste_c(c, SELLO, W / 2, 1200, s=E.lerp(2.3, 1.0, min(1, (t - t37) / .16)), alpha=min(1, (t - t37) / .08)); flash(c, t, t37, .15, (255, 230, 220), 160)
    for k in KN: flash(c, t, k, .08, (255, 255, 255), 80)
    c.alpha_composite(E.banda()); d = ImageDraw.Draw(c)
    for ws, idx in CAP:   # subtítulos palabra a palabra
        t0 = wt(idx[0]); t1 = wt(idx[-1]) + .45
        if not (t0 - .05 <= t < t1): continue
        f = font(F_ANTON, 94); lens = [d.textlength(w + " ", font=f) for w in ws]; x = W / 2 - (sum(lens) - d.textlength(" ", font=f)) / 2
        for w, i, L in zip(ws, idx, lens):
            col = YEL if wt(i) - .03 <= t else (215, 215, 222)
            d.text((x, 1490), w, font=f, fill=col, anchor="lm", stroke_width=10, stroke_fill=OL); x += L
        break
    return finish(c, t).convert("RGB")

part = os.path.join(T, "hook.part.mp4"); vid = os.path.join(T, "hook_v.mp4")
p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", part], stdin=subprocess.PIPE)
for f in range(round(DUR * FPS)): p.stdin.write(frame(f / FPS).tobytes())
p.stdin.close(); p.wait(); os.replace(part, vid)
# audio del gancho: voz + golpes + candado + boom (mismos niveles que el episodio)
sfx = lambda n: os.path.join(E.SFXD, n + ".mp3")
items = [(sfx("golpes"), 0.0, -2), (sfx("candado"), wt(5) - .05, 0), (sfx("boom"), wt(11) - .02, 0), (sfx("whoosh"), DUR - .3, -3)]
ins = ["-i", voz]; flt = [f"[0:a]aresample=48000,apad=pad_dur=4,acompressor=threshold=-18dB:ratio=3:attack=5:release=120,loudnorm=I=-15:TP=-1.5:LRA=9,atrim=0:{DUR:.2f}[v]"]
for k, (pth, t0, db) in enumerate(items):
    ins += ["-i", pth]; ms = int(max(0, t0) * 1000); flt.append(f"[{k + 1}:a]aresample=48000,loudnorm=I=-26:TP=-6,volume={db}dB,adelay={ms}|{ms},apad[s{k}]")
flt.append("[v]" + "".join(f"[s{k}]" for k in range(len(items))) + f"amix=inputs={len(items) + 1}:normalize=0:duration=longest,atrim=0:{DUR:.2f},alimiter=limit=0.95,aformat=channel_layouts=stereo[m]")
wav = os.path.join(T, "hook.wav"); subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(flt), "-map", "[m]", wav], check=True)
# episodio completo con el gancho delante
hq = os.path.join(T, "video_hq.mp4"); mz = os.path.join(T, "mezcla.wav"); out = os.path.join(E.OUT, "la_casa_de_1_dolar_parte1_gancho.mp4")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", vid, "-i", wav, "-i", hq, "-i", mz, "-filter_complex",
                "[0:v][1:a][2:v][3:a]concat=n=2:v=1:a=1[v][a]", "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-maxrate", "4500k", "-bufsize", "9000k",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out], check=True)
print("ok", round(DUR, 2), out)
