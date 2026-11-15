"""Prepara las voces del Ep.3: recorta silencios, acelera por personaje y guarda voz3/*.wav + offsets.json.
Copia también los JSON de whisper cuando ya existan."""
import os, json, re, shutil, subprocess
from guion3 import LINEAS

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "descargas", "taller_ep3")
DST = os.path.join(HERE, "voz3"); os.makedirs(DST, exist_ok=True)
TEMPO = {"N": 1.12, "M": 1.0, "L": 1.03, "X": 1.05, "T": 1.0}
FILTRO = {"T": "highpass=f=320,lowpass=f=3400,acompressor=threshold=-20dB:ratio=3,"}   # nota de voz de móvil

def lead_silence(f):
    out = subprocess.run(["ffmpeg", "-i", f, "-af", "silencedetect=n=-40dB:d=0.02", "-t", "1.5", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.search(r"silence_start: (-?[\d.]+).*?silence_end: ([\d.]+)", out, re.S)
    return float(m.group(2)) if m and float(m.group(1)) <= 0.01 else 0.0

offs = {}
for lid, v, *_ in LINEAS:
    src = os.path.join(SRC, lid + ".mp3")
    off = max(0.0, lead_silence(src) - .03); tp = TEMPO[v]
    af = (f"atrim=start={off:.3f},asetpts=PTS-STARTPTS," + FILTRO.get(v, "") +
          f"areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo={tp}")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-af", af, "-ar", "44100", "-ac", "1", os.path.join(DST, lid + ".wav")], check=True)
    offs[lid] = {"off": off, "tempo": tp}
    j = os.path.join(SRC, lid + ".json")
    if os.path.exists(j): shutil.copy(j, os.path.join(DST, lid + ".json"))
json.dump(offs, open(os.path.join(DST, "offsets.json"), "w"))
print("ok", len(offs))
