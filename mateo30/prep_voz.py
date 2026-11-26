"""Prepara las voces de la Parte 1: recorta silencios, ajusta ritmo por personaje, sube el tono de Mateo (voz de niño)
y guarda voz/*.wav + offsets.json. Copia los JSON de whisper cuando ya existan."""
import os, json, re, shutil, subprocess, sys
import importlib
EP = sys.argv[2] if len(sys.argv) > 2 else "1"
LINEAS = importlib.import_module("guion_d" + EP).LINEAS

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "descargas", sys.argv[1] if len(sys.argv) > 1 else "mateo_ep1")
DST = os.path.join(HERE, "voz_d" + EP); os.makedirs(DST, exist_ok=True)
TEMPO = {"N": 1.08, "K": 1.0, "T": 1.04, "P": 1.0, "B": 1.0, "A": 1.0}
PITCH = {"K": 1.13, "P": 1.28, "B": 1.25}
if EP == "2": TEMPO.update(N=1.12, K=1.06)
if EP in ("3", "4", "5", "6"): TEMPO.update(N=1.04, K=1.0)
if EP == "7": TEMPO.update(N=.96, K=1.0)   # día 7: narradora a su velocidad natural   # Mateo: más agudo sin cambiar la velocidad

def lead_silence(f):
    out = subprocess.run(["ffmpeg", "-i", f, "-af", "silencedetect=n=-40dB:d=0.02", "-t", "1.5", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.search(r"silence_start: (-?[\d.]+).*?silence_end: ([\d.]+)", out, re.S)
    return float(m.group(2)) if m and float(m.group(1)) <= 0.01 else 0.0

offs = {}
CUTS = {"L01": [(1.80, 2.05), (2.48, 2.60)]} if EP == "4" else {}      # pausas dentro del gancho: fuera, para que dure menos
TEMPO_L = {"L01": 1.10} if EP == "4" else {}
FIN = {"L17": 2.80} if EP == "4" else ({"L06": 2.42} if EP == "5" else {})   # día 5: la frase de Bruno la dice Bruno (L06B)      # el cierre acaba en "…o celebrar." (fuera "tu comentario puede salir…")
for lid, v, *_ in LINEAS:
    src = os.path.join(SRC, lid + ".mp3")
    off = max(0.0, lead_silence(src) - .03); tp = TEMPO_L.get(lid, TEMPO[v]); pt = PITCH.get(v); cuts = CUTS.get(lid, [])
    if EP == "2" and lid == "H09": off = 1.80   # se corta "No es una doble u": Mateo aún no conoce las letras
    pf = f"asetrate={int(44100 * pt)},aresample=44100,atempo={1 / pt:.4f}," if pt else ""
    sel = ("aselect='not(" + "+".join(f"between(t,{a},{b})" for a, b in cuts) + ")',asetpts=N/SR/TB,") if cuts else ""
    fin = f"atrim=end={FIN[lid]},afade=t=out:st={FIN[lid] - .08:.3f}:d=0.08," if lid in FIN else ""
    af = (f"aresample=44100," + fin + sel + f"atrim=start={off:.3f},asetpts=PTS-STARTPTS," + pf +
          f"areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo={tp}")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-af", af, "-ar", "44100", "-ac", "1", os.path.join(DST, lid + ".wav")], check=True)
    offs[lid] = {"off": off, "tempo": tp}
    j = os.path.join(SRC, lid + ".json")
    if os.path.exists(j):
        ws = json.load(open(j, encoding="utf-8"))
        for w in ws:
            q = sum(b - a for a, b in cuts if b <= w["inicio"] + .05); w["inicio"] = round(w["inicio"] - q, 3); w["fin"] = round(w["fin"] - sum(b - a for a, b in cuts if b <= w["fin"] + .05), 3)
        ws = [w for w in ws if w["inicio"] >= off - .02 and (lid not in FIN or w["inicio"] < FIN[lid])]
        json.dump(ws, open(os.path.join(DST, lid + ".json"), "w", encoding="utf-8"), ensure_ascii=False)
json.dump(offs, open(os.path.join(DST, "offsets.json"), "w"))
print("ok", len(offs))
