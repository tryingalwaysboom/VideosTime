"""Mezcla las voces del Ep.1 en su sitio del timeline y las une al vídeo."""
import os, subprocess, sys
from render import TL, TOTAL, VOZ, TMP, HERE

def main(out, prefix="s", sfx=()):
    """sfx: lista de (ruta_wav, segundo, dB) que se mezclan por debajo de la voz."""
    ins, flt = [], []
    for i, lid in enumerate(TL):
        ins += ["-i", os.path.join(VOZ, lid + ".wav")]
        ms = int(TL[lid][0] * 1000)
        flt.append(f"[{i}:a]aresample=48000,afade=t=in:d=0.015,adelay={ms}|{ms},apad[a{i}]")
    n = len(TL)
    flt.append("".join(f"[a{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},"
               "acompressor=threshold=-18dB:ratio=3:attack=5:release=120,loudnorm=I=-15:TP=-1.5:LRA=9[voz]")
    wav = os.path.join(TMP, prefix + "_voces.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(flt), "-map", "[voz]", "-ac", "2", wav], check=True)
    if sfx:   # efectos normalizados a -26 LUFS (+ ajuste) para que nunca tapen la voz (-15 LUFS)
        ins2, f2 = ["-i", wav], []
        for k, (p, t, db) in enumerate(sfx, 1):
            ins2 += ["-i", p]; ms = int(t * 1000)
            f2.append(f"[{k}:a]aresample=48000,loudnorm=I=-26:TP=-6,volume={db}dB,adelay={ms}|{ms},apad[s{k}]")
        f2.append("[0:a]" + "".join(f"[s{k}]" for k in range(1, len(sfx) + 1)) +
                  f"amix=inputs={len(sfx) + 1}:normalize=0:duration=first,alimiter=limit=0.95[mx]")
        wav2 = os.path.join(TMP, prefix + "_mezcla.wav")
        subprocess.run(["ffmpeg", "-y", "-v", "error", *ins2, "-filter_complex", ";".join(f2), "-map", "[mx]", "-ac", "2", wav2], check=True)
        wav = wav2
    lst = os.path.join(TMP, "list.txt")
    with open(lst, "w") as f:
        for k in sorted(x for x in os.listdir(TMP) if x.startswith(prefix) and x[len(prefix):len(prefix)+1].isdigit() and x.endswith(".mp4") and "part" not in x):
            f.write(f"file '{k}'\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-maxrate", "1150k", "-bufsize", "2300k", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out], check=True)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "heredas_un_taller_ep1.mp4"))
