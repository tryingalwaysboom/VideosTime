"""Prepara las voces de la Parte 1: recorta silencios y acelera un poco. voz1/*.wav"""
import os, re, json, subprocess, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "descargas", "casa_ep1"); DST = os.path.join(HERE, "voz1"); os.makedirs(DST, exist_ok=True)
TEMPO = {"C04": 1.0}
def lead(f):
    out = subprocess.run(["ffmpeg", "-i", f, "-af", "silencedetect=n=-40dB:d=0.02", "-t", "1.5", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"silence_start: (-?[\d.]+).*?silence_end: ([\d.]+)", out, re.S)
    return float(m.group(2)) if m and float(m.group(1)) <= 0.01 else 0.0
offs = {}
for i in range(1, 8):
    lid = f"C0{i}"; src = os.path.join(SRC, lid + ".mp3")
    off = max(0.0, lead(src) - .03); tp = TEMPO.get(lid, 1.07)
    af = f"atrim=start={off:.3f},asetpts=PTS-STARTPTS,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo={tp}"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-af", af, "-ar", "48000", "-ac", "1", os.path.join(DST, lid + ".wav")], check=True)
    offs[lid] = {"off": off, "tempo": tp}
json.dump(offs, open(os.path.join(DST, "offsets.json"), "w"))
for lid in offs:
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", os.path.join(DST, lid + ".wav")], capture_output=True, text=True).stdout.strip()
    print(lid, offs[lid], d)
