"""Mezcla de la Parte 2: voces, efectos sincronizados (siempre por debajo de la voz) y música que se aparta cuando hablan."""
import os, subprocess, sys
import render2 as V
from render2 import TL, TOTAL, S, E, WT, SCENES, SUAVES, TMP, HERE

MSFX = os.path.join(HERE, "..", "descargas", "mateo_sfx"); CSFX = os.path.join(HERE, "..", "descargas", "cuaderno_sfx")
def m(n): return os.path.join(MSFX, n + ".mp3")
def c(n): return os.path.join(CSFX, n + ".mp3")

def crayola(t0, t1):
    out = os.path.join(TMP, f"cray_{t0:.2f}.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", m("crayola"), "-t", f"{max(.2, t1 - t0):.2f}",
                    "-af", "aresample=48000,afade=t=in:d=0.05,afade=t=out:st=%.2f:d=0.1" % max(0, t1 - t0 - .1), "-ac", "1", out], check=True)
    return out

def efectos():
    t1a, t1b = WT("F07", "crayola"), E("F07") + .2
    t2a, t2b = E("F07") + .45, S("F08") - .1
    tf = WT("F11", "página") - .2
    e = [(m("brillo"), WT("H2", "Entonces"), -9), (m("resultado"), S("F03") + .35, -9), (m("reloj"), WT("H2", "Diez"), -12),
         (c("pagina"), S("F03") + .1, -6), (m("brillo"), WT("F03", "mamá…") - .1, -8),
         (m("piano"), S("F06") - .15, -9), (m("brillo"), WT("F06", "círculo.") - .5, -9),
         (m("teclea"), S("F07") - .05, -12), (crayola(t1a, t1b), t1a, -5), (crayola(t2a, t2b), t2a, -5),
         (m("brillo"), t1b, -5), (m("brillo"), t2b, -4), (m("risa"), WT("F08", "redondita!"), -12),
         (crayola(WT("F09", "cuaderno,") - .1, E("F09") + .3), WT("F09", "cuaderno,") - .1, -6),
         (c("escalera"), WT("F10", "pasas") - .3, -9), (m("brillo"), WT("F10", "encendida.") - .1, -6),
         (c("pagina"), tf, -4), (m("brillo"), WT("F11", "brilla.") - .1, -6),
         (m("brillo"), WT("F13", "apaga.") - .05, -9),
         (m("brillo"), WT("F14", "vigilar") - .3, -7), (m("brillo"), WT("F14", "respuesta") - .3, -7)]
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
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "cuaderno_parte2.mp4"))
