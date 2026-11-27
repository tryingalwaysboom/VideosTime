"""Lara: recorta silencios, ajusta ritmo/tono por personaje, filtro teléfono para la tía; guarda voz_dN/*.wav, offsets.json y json de palabras."""
import os, json, re, subprocess, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
EP = sys.argv[1] if len(sys.argv) > 1 else "1"
LINEAS = importlib.import_module("guion_d" + EP).LINEAS
SRC = os.path.join(HERE, "..", "descargas", f"lara30_d{EP}")
DST = os.path.join(HERE, "voz_d" + EP); os.makedirs(DST, exist_ok=True)
TEMPO = {"N": 1.06, "L": 1.0, "C": 1.0, "B": 1.0}
PITCH = {"L": 1.25, "C": 1.2}
PHONE = "highpass=f=350,lowpass=f=3200,acompressor=threshold=-24dB:ratio=3,"

def lead(f):
    o = subprocess.run(["ffmpeg", "-i", f, "-af", "silencedetect=n=-40dB:d=0.02", "-t", "1.5", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"silence_start: (-?[\d.]+).*?silence_end: ([\d.]+)", o, re.S)
    return float(m.group(2)) if m and float(m.group(1)) <= 0.01 else 0.0

offs = {}
for lid, v, *_ in LINEAS:
    src = os.path.join(SRC, lid + ".mp3"); off = max(0.0, lead(src) - .03); tp = TEMPO[v]; pt = PITCH.get(v)
    pf = f"asetrate={int(44100*pt)},aresample=44100,atempo={1/pt:.4f}," if pt else ""
    af = ("aresample=44100," + f"atrim=start={off:.3f},asetpts=PTS-STARTPTS," + pf + (PHONE if v == "B" else "") +
          f"areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo={tp}")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-af", af, "-ar", "44100", "-ac", "1", os.path.join(DST, lid + ".wav")], check=True)
    offs[lid] = {"off": off, "tempo": tp}
    j = os.path.join(SRC, lid + ".json")
    if os.path.exists(j):
        ws = [w for w in json.load(open(j, encoding="utf-8")) if w["inicio"] >= off - .02]
        json.dump(ws, open(os.path.join(DST, lid + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
json.dump(offs, open(os.path.join(DST, "offsets.json"), "w"))
print("ok", len(offs))
