"""Mezcla de la Parte 4: voces en su sitio, efectos sincronizados (siempre por debajo de la voz) y música de fondo que se
aparta sola cuando alguien habla. Une las escenas de tmp/ y saca el vídeo final."""
import os, subprocess, sys
import render4 as V
from render4 import TL, TOTAL, S, E, WT, SCENES, SUAVES, TMP, HERE

SFX = os.path.join(HERE, "..", "descargas", "mateo_sfx")
def sx(n): return os.path.join(SFX, n + ".mp3")

def efectos():
    e = [(sx("resultado"), .15, -4),
         (sx("borrar"), WT("F01", "detienes") + .2, -6),
         (sx("brillo"), WT("F01", "perfecto.") - .05, -4),
         (sx("brillo"), S("F03") + .3, -3),
         (sx("risa"), S("F04") - .1, -9),
         (sx("crayola"), WT("F05", "adelante,") - .2, -3),
         (sx("brillo"), S("F06") - .1, -4),
         (sx("crayola"), WT("F07", "escribe") - .1, -3), (sx("crayola"), WT("F07", "escribe") + 2.6, -4),
         (sx("piano"), S("F08") - .1, -7),
         (sx("brillo"), WT("F08B", "link") - .2, -5), (sx("movil"), WT("F09", "tablet") - .2, -5),
         (sx("brillo"), WT("F09", "A:") - .1, -5), (sx("brillo"), WT("F09", "B:") - .1, -5)]
    for t, fn in SCENES[1:]:
        if t not in SUAVES: e.append((sx("whoosh"), t - .05, -7))
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
        flt.append(f"[{k}:a]aresample=48000,loudnorm=I=-25:TP=-6,aresample=48000,volume={db}dB,adelay={ms}|{ms},apad[s{j}]")
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
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "mateo_parte4.mp4"))
