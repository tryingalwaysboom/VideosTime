"""Prepara las voces de «30 días sin celular»: recorta silencios y ajusta el ritmo. Uso: python3 prep_voz.py vale30_d1 1"""
import os, json, re, subprocess, sys, importlib
EP = sys.argv[2]; HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
LINEAS = importlib.import_module("guion_v" + EP).LINEAS
SRC = os.path.join(HERE, "..", "descargas", sys.argv[1]); DST = os.path.join(HERE, "voz_v" + EP); os.makedirs(DST, exist_ok=True)
TEMPO = {"N": 1.10, "V": 1.03}
def lead_silence(f):
    out = subprocess.run(["ffmpeg", "-i", f, "-af", "silencedetect=n=-40dB:d=0.02", "-t", "1.5", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"silence_start: (-?[\d.]+).*?silence_end: ([\d.]+)", out, re.S)
    return float(m.group(2)) if m and float(m.group(1)) <= 0.01 else 0.0
offs = {}
for lid, v, *_ in LINEAS:
    src = os.path.join(SRC, lid + ".mp3"); off = max(0.0, lead_silence(src) - .03); tp = TEMPO[v]
    af = f"aresample=44100,atrim=start={off:.3f},asetpts=PTS-STARTPTS,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo={tp}"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-af", af, "-ar", "44100", "-ac", "1", os.path.join(DST, lid + ".wav")], check=True)
    offs[lid] = {"off": off, "tempo": tp}
    j = os.path.join(SRC, lid + ".json")
    if os.path.exists(j):
        ws = [w for w in json.load(open(j, encoding="utf-8")) if w["inicio"] >= off - .02]
        json.dump(ws, open(os.path.join(DST, lid + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
json.dump(offs, open(os.path.join(DST, "offsets.json"), "w")); print("ok", len(offs))
