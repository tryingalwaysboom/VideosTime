"""Mezcla del Día 1 de «30 días sin celular»: voces, efectos sincronizados con la imagen (siempre por debajo de la voz)
y música de fondo que se aparta sola cuando alguien habla. Une las escenas de tmp_v1/ y saca el vídeo final."""
import os, subprocess, sys
import render_v1 as V
from render_v1 import TL, TOTAL, S, E, WI, SCENES, TMP, HERE
D = os.path.join(HERE, "..", "descargas")
def sx(n, d="mateo_sfx"): return os.path.join(D, d, n + ".mp3")

def gate(nombre, tramos, out):
    expr = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in tramos)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", sx(nombre), "-t", f"{TOTAL:.2f}", "-af",
                    f"aresample=48000,loudnorm=I=-24:TP=-6,aresample=48000,asetpts=N/SR/TB,volume='min(1,{expr})':eval=frame,lowpass=f=9000", "-ac", "1", out], check=True)
    return out

def efectos():
    g = lambda n, tr: gate(n, tr, os.path.join(TMP, n + "_gate.wav")); st = {f.__name__: t for t, f in SCENES}
    e = [(g("lapiz", [(st["sc_letra"] + .05, st["sc_letra"] + 1.2), (st["sc_regla"] + .5, st["sc_en_nota"] - .05), (st["sc_hora3"] + .1, st["sc_11min"] - .1)]), 0, -6),
         (g("reloj", [(st["sc_11min"] + .05, st["sc_salio"] - .05), (st["sc_ojo"] + .1, st["sc_final"] - .1)]), 0, -9),
         (sx("candado", "casa_sfx"), WI("V01", 4) - .03, -5), (sx("boom", "casa_sfx"), st["sc_30"], -9), (sx("movil"), st["sc_9horas"] + .05, -11),
         (sx("brillo"), st["sc_recupera"] + .25, -10), (sx("brillo"), st["sc_concierto"] + .1, -9), (sx("boom", "casa_sfx"), WI("V04", 14) - .04, -9),
         (sx("candado", "casa_sfx"), st["sc_16"] + .05, -8), (sx("mochila"), st["sc_amano"], -9), (sx("mochila"), st["sc_prehistoria"], -10),
         (sx("mochila"), st["sc_salio"] + .05, -9), (sx("sello", "casa_sfx"), st["sc_no"], -6), (sx("risa"), WI("V10", 7) + .1, -13),
         (sx("corre"), st["sc_dame"] + .5, -11), (sx("camara"), WI("V12", 9), -6), (sx("brillo"), WI("V13", 8) - .05, -9),
         (sx("mochila"), WI("V14", 1) - .05, -10), (sx("mochila"), WI("V14", 9) - .05, -10), (sx("brillo"), st["sc_final"], -8)]
    for t, fn in SCENES[1:]: e.append((sx("whoosh"), t - .06, -14))
    return e

def main(out):
    ins, flt = [], []
    for i, lid in enumerate(TL):
        ins += ["-i", os.path.join(V.R.VOZ, lid + ".wav")]; ms = max(0, int(TL[lid][0] * 1000))
        flt.append(f"[{i}:a]aresample=48000,afade=t=in:d=0.012,adelay={ms}|{ms},apad[a{i}]")
    n = len(TL)
    flt.append("".join(f"[a{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},"
               "acompressor=threshold=-18dB:ratio=3:attack=5:release=120,loudnorm=I=-15:TP=-1.5:LRA=9,aresample=48000[voz]")
    vwav = os.path.join(TMP, "voces.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(flt), "-map", "[voz]", "-ar", "48000", "-ac", "1", vwav], check=True)
    mwav = os.path.join(TMP, "musica_duck.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", sx("musica"), "-i", vwav, "-filter_complex",
                    f"[0:a]aresample=48000,atempo=1.08,atrim=0:{TOTAL:.2f},loudnorm=I=-27:TP=-8,aresample=48000,aformat=channel_layouts=mono[m0];"
                    f"[1:a]apad,atrim=0:{TOTAL:.2f}[key];[m0][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350[mus]",
                    "-map", "[mus]", "-ar", "48000", "-ac", "1", mwav], check=True)
    ins, flt = ["-i", vwav, "-i", mwav], [f"[0:a]apad,atrim=0:{TOTAL:.2f}[voz]", f"[1:a]apad,atrim=0:{TOTAL:.2f}[mus]"]
    parts = ["[voz]", "[mus]"]
    for j, (p, t, db) in enumerate(efectos()):
        ins += ["-i", p]; ms = max(0, int(t * 1000))
        norm = "" if p.endswith("_gate.wav") else "atrim=0:1.6,afade=t=out:st=1.2:d=0.4,loudnorm=I=-25:TP=-6,aresample=48000,"
        flt.append(f"[{j + 2}:a]aresample=48000,{norm}volume={db}dB,adelay={ms}|{ms},apad[s{j}]"); parts.append(f"[s{j}]")
    flt.append("".join(parts) + f"amix=inputs={len(parts)}:normalize=0:duration=longest,alimiter=limit=0.95,apad,atrim=0:{TOTAL:.2f}[mx]")
    fx = "".join(parts[2:]) + f"amix=inputs={len(parts) - 2}:normalize=0:duration=longest,apad,atrim=0:{TOTAL:.2f}[fx]"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(flt[2:-1] + [fx]), "-map", "[fx]", "-ac", "1", os.path.join(TMP, "efectos.wav")], check=True)
    wav = os.path.join(TMP, "mezcla.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(flt), "-map", "[mx]", "-ac", "2", wav], check=True)
    lst = os.path.join(TMP, "list.txt")
    with open(lst, "w") as f:
        for i in range(len(SCENES)): f.write(f"file 's{i:02d}.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-maxrate", "2400k", "-bufsize", "4800k", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "128k", "-t", f"{TOTAL:.2f}", "-movflags", "+faststart", out], check=True)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "vale_dia1.mp4"))
