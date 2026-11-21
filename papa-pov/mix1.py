"""Mezcla de la Parte 1: voces en su sitio, efectos sincronizados (siempre por debajo de la voz) y música de fondo que se
aparta cuando alguien habla. Une las escenas de tmp1/ y saca papa_solo_parte1.mp4."""
import os, subprocess, sys
import render1 as V
from render1 import TL, TOTAL, S_, E_, WT, ESCENAS, TMP, HERE, GAP

D = os.path.join(HERE, "..", "descargas")
def sx(carpeta, n): return os.path.join(D, carpeta, n + ".mp3")


def efectos():
    e = [(sx("taller_sfx", "impacto"), WT("L01", "hijo") - .05, -9),
         (sx("mateo_sfx", "reloj"), S_("L02") - .35, -12),
         (sx("casa_sfx", "puerta"), S_("L07") - GAP["L07"] + .35, -7),
         (sx("mateo_sfx", "leche"), WT("L08", "leche") - .1, -8),
         (sx("mateo_sfx", "corre"), S_("L16"), -14),
         (sx("taller_sfx", "tension"), S_("L20") - .1, -15),
         (sx("taller_sfx", "impacto"), S_("L26") - .3, -10),
         (sx("mateo_sfx", "movil"), S_("L30") - .95, -13),
         (sx("mateo_sfx", "brillo"), S_("L32") - .1, -9),
         (sx("mateo_sfx", "brillo"), WT("L32", "guardamos") - .15, -9)]
    for t, fn in ESCENAS[1:]:
        e.append((sx("mateo_sfx", "whoosh"), t - .05, -9))
    return e


def main(out):
    ins, flt = [], []
    for i, lid in enumerate(TL):
        ins += ["-i", os.path.join(V.VOZ, lid + ".wav")]
        ms = int(TL[lid][0] * 1000)
        flt.append(f"[{i}:a]aresample=48000,afade=t=in:d=0.015,adelay={ms}|{ms},apad[a{i}]")
    n = len(TL)
    flt.append("".join(f"[a{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},"
               "acompressor=threshold=-18dB:ratio=3:attack=5:release=120,loudnorm=I=-15:TP=-1.5:LRA=9,aresample=48000[voz]")
    vwav = os.path.join(TMP, "voces.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(flt), "-map", "[voz]", "-ar", "48000", "-ac", "1", vwav], check=True)
    mwav = os.path.join(TMP, "musica_duck.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", sx("mateo_sfx", "musica"), "-i", vwav, "-filter_complex",
                    f"[0:a]aresample=48000,atrim=0:{TOTAL:.2f},loudnorm=I=-30:TP=-8,aresample=48000,aformat=channel_layouts=mono[m0];"
                    f"[1:a]apad,atrim=0:{TOTAL:.2f}[key];[m0][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[mus]",
                    "-map", "[mus]", "-ar", "48000", "-ac", "1", mwav], check=True)
    ins, flt = ["-i", vwav, "-i", mwav], [f"[0:a]apad,atrim=0:{TOTAL:.2f}[voz]", f"[1:a]apad,atrim=0:{TOTAL:.2f}[mus]"]
    parts, k = ["[voz]", "[mus]"], 2
    for j, (p, t, db) in enumerate(efectos()):
        ins += ["-i", p]; ms = max(0, int(t * 1000))
        flt.append(f"[{k}:a]aresample=48000,loudnorm=I=-25:TP=-6,aresample=48000,volume={db}dB,atrim=0:6,adelay={ms}|{ms},apad[s{j}]")
        parts.append(f"[s{j}]"); k += 1
    flt.append("".join(parts) + f"amix=inputs={len(parts)}:normalize=0:duration=longest,alimiter=limit=0.95,apad,atrim=0:{TOTAL:.2f}[mx]")
    wav = os.path.join(TMP, "mezcla.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(flt), "-map", "[mx]", "-ac", "2", wav], check=True)
    lst = os.path.join(TMP, "list.txt")
    with open(lst, "w") as f:
        for i in range(len(ESCENAS)): f.write(f"file 's{i:02d}.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-maxrate", "1500k", "-bufsize", "3000k", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out], check=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "papa_solo_parte1.mp4"))
