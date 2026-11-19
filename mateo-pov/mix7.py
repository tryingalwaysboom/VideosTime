"""Mezcla de la Parte 7: voces en su sitio, efectos sincronizados (siempre por debajo de la voz) y música de fondo que se
aparta sola cuando alguien habla. Une las escenas de tmp/ y saca el vídeo final."""
import os, subprocess, sys
import render7 as V
from render7 import TL, TOTAL, S, E, WT, SCENES, SUAVES, TMP, HERE

SFX = os.path.join(HERE, "..", "descargas", "mateo_sfx")
def sx(n): return os.path.join(SFX, n + ".mp3")

def pista_crayola():
    """Sonido de crayola solo mientras la mano escribe: se registran los tramos con la punta apoyada y se abre la pista justo ahí."""
    for i, (t, fn) in enumerate(SCENES):
        if fn.__name__ not in V.ESCENAS_ESCRITURA: continue
        t_fin = SCENES[i + 1][0] if i + 1 < len(SCENES) else TOTAL
        T = t
        while T < t_fin: fn(T); T += .2
    iv = sorted(x for v in V.TRAZOS_ON.values() for x in v) + V.tiza_intervalos()
    iv = sorted(iv); merged = []
    for a, b in iv:
        if merged and a - merged[-1][1] < .06: merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else: merged.append((a, b))
    expr = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in merged)
    out = os.path.join(TMP, "crayola_gate.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", sx("crayola"), "-t", f"{TOTAL:.2f}", "-af",
                    f"aresample=48000,loudnorm=I=-25:TP=-6,aresample=48000,asetpts=N/SR/TB,volume='min(1,{expr})':eval=frame,lowpass=f=9000", "-ac", "1", out], check=True)
    print("tramos de escritura:", len(merged))
    return out

def efectos():
    e = [(sx("resultado"), .15, -4),
         (sx("brillo"), S("F05") + .1, -5),
         (sx("movil"), S("F08") + .4, -7),
         (sx("movil"), S("F08B") + .1, -8),
         (sx("brillo"), WT("F14", "Una") + .1, -4),
         (sx("piano"), WT("F06", "helada") - .1, -6),
         (sx("brillo"), S("F18"), -5),
         (sx("brillo"), WT("F22", "A:") - .1, -5), (sx("brillo"), WT("F22", "B:") - .1, -5)]
    for t, fn in SCENES[1:]:
        if t not in SUAVES: e.append((sx("whoosh"), t - .05, -7))
    e.append((pista_crayola(), 0, -3))
    return e

def main(out):
    ins, flt = [], []
    for i, lid in enumerate(TL):
        ins += ["-i", os.path.join(V.R.VOZ, lid + ".wav")]
        ms = int(TL[lid][0] * 1000)
        flt.append(f"[{i}:a]aresample=48000,afade=t=in:d=0.015,adelay={ms}|{ms},apad[a{i}]")
    n = len(TL)
    flt.append("".join(f"[a{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},"
               "acompressor=threshold=-18dB:ratio=3:attack=5:release=120,loudnorm=I=-15:TP=-1.5:LRA=9,aresample=48000[voz]")
    vwav = os.path.join(TMP, "voces.wav")   # la voz se mezcla aparte: así nada en la mezcla final puede recortarla
    subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(flt), "-map", "[voz]", "-ar", "48000", "-ac", "1", vwav], check=True)
    mwav = os.path.join(TMP, "musica_duck.wav")   # música a -29 LUFS que se aparta (sidechain) cuando suena la voz
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(SFX, "musica.mp3"), "-i", vwav, "-filter_complex",
                    f"[0:a]aresample=48000,atrim=0:{TOTAL:.2f},loudnorm=I=-29:TP=-8,aresample=48000,aformat=channel_layouts=mono,afade=t=out:st={TOTAL - 2.5:.2f}:d=2.5[m0];"
                    f"[1:a]apad,atrim=0:{TOTAL:.2f}[key];[m0][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[mus]",
                    "-map", "[mus]", "-ar", "48000", "-ac", "1", mwav], check=True)
    ins, flt = ["-i", vwav, "-i", mwav], [f"[0:a]apad,atrim=0:{TOTAL:.2f}[voz]", f"[1:a]apad,atrim=0:{TOTAL:.2f}[mus]"]
    k = 2
    parts = ["[voz]", "[mus]"]
    for j, (p, t, db) in enumerate(efectos()):
        ins += ["-i", p]; ms = max(0, int(t * 1000))
        norm = "" if p.endswith("_gate.wav") else "loudnorm=I=-25:TP=-6,aresample=48000,"
        flt.append(f"[{k}:a]aresample=48000,{norm}volume={db}dB,adelay={ms}|{ms},apad[s{j}]")
        parts.append(f"[s{j}]"); k += 1
    flt.append("".join(parts) + f"amix=inputs={len(parts)}:normalize=0:duration=longest,alimiter=limit=0.95,apad,atrim=0:{TOTAL:.2f}[mx]")
    wav = os.path.join(TMP, "mezcla.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(flt), "-map", "[mx]", "-ac", "2", wav], check=True)
    lst = os.path.join(TMP, "list.txt")
    with open(lst, "w") as f:
        for i in range(len(SCENES)): f.write(f"file 's{i:02d}.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-maxrate", "1300k", "-bufsize", "2600k", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out], check=True)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "mateo_parte7.mp4"))
