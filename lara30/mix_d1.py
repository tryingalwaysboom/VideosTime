"""Mezcla del Día 1: voces + SFX sincronizados (siempre por debajo de la voz) + música con ducking → lara_dia1.mp4"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.argv = [sys.argv[0]]
import render_d1 as D
SFX = os.path.join(HERE, "..", "descargas", "mateo_sfx"); VOZ = os.path.join(HERE, "voz_d1"); S, E, WI, TOTAL = D.S, D.E, D.WI, D.TOTAL
# (archivo, tiempo, duración máx, volumen, atrás_offset)
ev = [("whoosh", S("L03") - .05, 1.0, .5), ("crayola", S("L07") + .1, E("L07") - S("L07") - .5, .55), ("crayola", S("L10") + .1, E("L10") - S("L10") - .5, .55),
      ("crayola", S("L13") + .1, E("L13") - S("L13") - .5, .55), ("rasgar", S("L11") + .1, 1.4, .6), ("timbre", S("L12") - .45, .9, .45),
      ("brillo", E("L13") - .35, 1.2, .45), ("whoosh", S("L14") + .2, .6, .4), ("borrar", S("L15") + 1.4, 1.0, .6), ("whoosh", S("L20") - .08, 1.0, .5),
      ("brillo", WI("L21", 1) - .05, .8, .45), ("brillo", WI("L21", 3) - .05, .8, .45)]
ins = []; fl = []; n = 0
for lid, *_ in D.LINEAS:
    ins += ["-i", os.path.join(VOZ, lid + ".wav")]; fl.append(f"[{n}:a]adelay={int(S(lid) * 1000)}|{int(S(lid) * 1000)},volume=1.0[v{n}]"); n += 1
vn = n
for f, t, du, vol in ev:
    ins += ["-i", os.path.join(SFX, f + ".mp3")]; fl.append(f"[{n}:a]atrim=0:{du:.2f},afade=t=out:st={max(0, du - .15):.2f}:d=0.15,aresample=44100,pan=mono|c0=.5*c0+.5*c1,volume={vol * .5},adelay={int(t * 1000)}|{int(t * 1000)}[x{n}]"); n += 1
ins += ["-i", os.path.join(SFX, "musica.mp3")]; mus = n
fl.append("".join(f"[v{i}]" for i in range(vn)) + f"amix=inputs={vn}:normalize=0:duration=longest,apad,atrim=0:{TOTAL},acompressor=threshold=-20dB:ratio=3:attack=5:release=80[voz]")
fl.append("[voz]asplit=2[vo][sc]")
fl.append("".join(f"[x{i}]" for i in range(vn, mus)) + f"amix=inputs={mus - vn}:normalize=0:duration=longest,apad,atrim=0:{TOTAL}[sfx]")
fl.append(f"[{mus}:a]atrim=0:{TOTAL},aresample=44100,pan=mono|c0=.5*c0+.5*c1,volume=.2,afade=t=out:st={TOTAL - 1.5}:d=1.5[m0]")
fl.append("[m0][sc]sidechaincompress=threshold=0.03:ratio=9:attack=20:release=400[m]")
fl.append(f"[vo][sfx][m]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-15:TP=-1.5:LRA=9,atrim=0:{TOTAL}[a]")
out = os.path.join(HERE, "tmp_d1", "audio.m4a")
subprocess.run(["ffmpeg", "-y", "-v", "error"] + ins + ["-filter_complex", ";".join(fl), "-map", "[a]", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", out], check=True)
fin = os.path.join(HERE, "lara_dia1.mp4"); tmp = fin + ".tmp.mp4"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(HERE, "tmp_d1", "video_mudo.mp4"), "-i", out, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "copy", "-t", str(TOTAL), "-movflags", "+faststart", tmp], check=True)
os.rename(tmp, fin); print("ok", fin)
