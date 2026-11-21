"""Prepara las voces: recorta silencios, ajusta ritmo y sube el tono a los niños. Guarda voz1/*.wav (+ json de whisper)."""
import os, re, json, shutil, subprocess
from guion_papa1 import LINEAS

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "descargas", "papa_ep1")
DST = os.path.join(HERE, "voz1"); os.makedirs(DST, exist_ok=True)
TEMPO = {"D": 1.05, "M": 1.03, "V": 1.0, "H": 1.0, "C": 1.0}
PITCH = {"V": 1.08, "H": 1.22}   # Vera 7 años, Hugo 4 años


def lead_silence(f):
    out = subprocess.run(["ffmpeg", "-i", f, "-af", "silencedetect=n=-40dB:d=0.02", "-t", "1.5", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.search(r"silence_start: (-?[\d.]+).*?silence_end: ([\d.]+)", out, re.S)
    return float(m.group(2)) if m and float(m.group(1)) <= 0.01 else 0.0


offs = {}
for lid, v, *_ in LINEAS:
    src = os.path.join(SRC, lid + ".mp3")
    off = max(0.0, lead_silence(src) - .03); tp = TEMPO[v]; pt = PITCH.get(v)
    pf = f"asetrate={int(44100 * pt)},aresample=44100,atempo={1 / pt:.4f}," if pt else ""
    af = (f"aresample=44100,atrim=start={off:.3f},asetpts=PTS-STARTPTS," + pf +
          f"areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo={tp}")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-af", af, "-ar", "44100", "-ac", "1", os.path.join(DST, lid + ".wav")], check=True)
    offs[lid] = {"off": off, "tempo": tp}
    j = os.path.join(SRC, lid + ".json")
    if os.path.exists(j): shutil.copy(j, os.path.join(DST, lid + ".json"))
json.dump(offs, open(os.path.join(DST, "offsets.json"), "w"))
print("ok", len(offs))
