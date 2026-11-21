"""Día 0: recorta silencios de las voces (voz0/*.wav) y guarda desfase para alinear los tiempos de whisper."""
import os, re, json, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "descargas", "nota_ep0b"); DST = os.path.join(HERE, "voz0b"); os.makedirs(DST, exist_ok=True)
def lead(f):
    o = subprocess.run(["ffmpeg", "-i", f, "-af", "silencedetect=n=-40dB:d=0.02", "-t", "1.5", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"silence_start: (-?[\d.]+).*?silence_end: ([\d.]+)", o, re.S)
    return float(m.group(2)) if m and float(m.group(1)) <= 0.01 else 0.0
offs = {}
for i in range(1, 6):
    lid = f"L{i:02d}"; src = os.path.join(SRC, lid + ".mp3"); off = max(0.0, lead(src) - .03)
    af = f"aresample=44100,atrim=start={off:.3f},asetpts=PTS-STARTPTS,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo=1.1"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-af", af, "-ar", "44100", "-ac", "1", os.path.join(DST, lid + ".wav")], check=True)
    offs[lid] = {"off": off, "tempo": 1.1}
    shutil.copy(os.path.join(SRC, lid + ".json"), os.path.join(DST, lid + ".json"))
json.dump(offs, open(os.path.join(DST, "offsets.json"), "w")); print(offs)
