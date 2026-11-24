"""Mezcla de la Parte 2: voces, efectos sincronizados (siempre por debajo de la voz) y música que se aparta cuando hablan."""
import os, subprocess, sys
import render3 as V
from render3 import TL, TOTAL, S, E, WT, SCENES, SUAVES, TMP, HERE

MSFX = os.path.join(HERE, "..", "descargas", "mateo_sfx"); CSFX = os.path.join(HERE, "..", "descargas", "cuaderno_sfx")
def m(n): return os.path.join(MSFX, n + ".mp3")
def c(n): return os.path.join(CSFX, n + ".mp3")

def crayola(t0, t1):
    out = os.path.join(TMP, f"cray_{t0:.2f}.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", m("crayola"), "-t", f"{max(.2, t1 - t0):.2f}",
                    "-af", "aresample=48000,afade=t=in:d=0.05,afade=t=out:st=%.2f:d=0.1" % max(0, t1 - t0 - .1), "-ac", "1", out], check=True)
    return out

def efectos():
    e = [(m("brillo"), S("H1") + .1, -8), (m("brillo"), WT("H1", "respuesta.") - .1, -8),
         (m("resultado"), S("E1") + .2, -9), (c("pagina"), S("C1") - .05, -7), (m("teclea"), S("C1") + .1, -12),
         (m("brillo"), WT("C1", "firma"), -9), (m("risa"), WT("S1", "salió!"), -12),
         (c("pagina"), S("C2") + .1, -6), (m("brillo"), WT("C2", "mañana,") - .1, -8), (m("brillo"), WT("C2", "respuesta.") - .1, -8),
         (c("pagina"), S("A1") - .1, -6), (m("brillo"), WT("A1", "maestra.") - .1, -9), (m("brillo"), WT("A1", "F.") - .1, -9),
         (m("teclea"), S("C3") - .05, -12),
         (crayola(WT("C3", "línea…") - .6, WT("C3", "línea…") + .1), WT("C3", "línea…") - .6, -5),
         (crayola(WT("C3", "otra", 1) - .5, WT("C3", "otra", 1) + .1), WT("C3", "otra", 1) - .5, -5),
         (crayola(WT("C3", "otra", 2) - .5, WT("C3", "otra", 2) + .15), WT("C3", "otra", 2) - .5, -5),
         (m("brillo"), E("C3") + .05, -6), (m("risa"), WT("S2", "F!"), -12),
         (m("brillo"), WT("Z1", "cuentas") - .3, -7), (m("brillo"), WT("Z1", "guardas") - .3, -7)]
    for t, fn in SCENES[1:]:
        if t not in SUAVES: e.append((m("whoosh"), t - .05, -10))
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
    vwav = os.path.join(TMP, "voces.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(flt), "-map", "[voz]", "-ar", "48000", "-ac", "1", vwav], check=True)
    mwav = os.path.join(TMP, "musica_duck.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", m("musica"), "-i", vwav, "-filter_complex",
                    f"[0:a]aresample=48000,atrim=0:{TOTAL:.2f},loudnorm=I=-29:TP=-8,aresample=48000,aformat=channel_layouts=mono[m0];"
                    f"[1:a]apad,atrim=0:{TOTAL:.2f}[key];[m0][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[mus]",
                    "-map", "[mus]", "-ar", "48000", "-ac", "1", mwav], check=True)
    ins, flt = ["-i", vwav, "-i", mwav], [f"[0:a]apad,atrim=0:{TOTAL:.2f}[voz]", f"[1:a]apad,atrim=0:{TOTAL:.2f}[mus]"]
    k = 2; parts = ["[voz]", "[mus]"]
    for j, (p, t, db) in enumerate(efectos()):
        ins += ["-i", p]; ms = max(0, int(t * 1000))
        norm = "" if os.path.basename(p).startswith("cray_") else "loudnorm=I=-25:TP=-6,aresample=48000,"
        flt.append(f"[{k}:a]aresample=48000,{norm}volume={db}dB,adelay={ms}|{ms},apad[s{j}]")
        parts.append(f"[s{j}]"); k += 1
    flt.append("".join(parts) + f"amix=inputs={len(parts)}:normalize=0:duration=longest,alimiter=limit=0.95,apad,atrim=0:{TOTAL:.2f}[mx]")
    wav = os.path.join(TMP, "mezcla.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(flt), "-map", "[mx]", "-ac", "2", wav], check=True)
    lst = os.path.join(TMP, "list.txt")
    with open(lst, "w") as f:
        for i in range(len(SCENES)): f.write(f"file 's{i:02d}.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-maxrate", "1500k", "-bufsize", "3000k", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "128k", "-t", f"{TOTAL:.2f}", "-movflags", "+faststart", out], check=True)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "cuaderno_parte3.mp4"))
