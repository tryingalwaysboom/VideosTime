"""Prepara las voces del capítulo 1: quita el silencio inicial y final y guarda voz_c1/*.wav + los tiempos de palabra corregidos."""
import os, json, re, subprocess
from guion_c1 import LINEAS
HERE=os.path.dirname(os.path.abspath(__file__)); SRC=os.path.join(HERE,"..","descargas","abuelo_c1"); DST=os.path.join(HERE,"voz_c1"); os.makedirs(DST,exist_ok=True)
def lead(f):
    out=subprocess.run(["ffmpeg","-i",f,"-af","silencedetect=n=-40dB:d=0.02","-t","1.5","-f","null","-"],capture_output=True,text=True).stderr
    m=re.search(r"silence_start: (-?[\d.]+).*?silence_end: ([\d.]+)",out,re.S)
    return float(m.group(2)) if m and float(m.group(1))<=0.01 else 0.0
for lid,v,_ in LINEAS:
    src=os.path.join(SRC,lid+".mp3"); off=max(0.0,lead(src)-.03)
    af=f"aresample=44100,atrim=start={off:.3f},asetpts=PTS-STARTPTS,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse"
    subprocess.run(["ffmpeg","-y","-v","error","-i",src,"-af",af,"-ar","44100","-ac","1",os.path.join(DST,lid+".wav")],check=True)
    ws=json.load(open(os.path.join(SRC,lid+".json"),encoding="utf-8"))
    for w in ws: w["inicio"]=round(max(0,w["inicio"]-off),3); w["fin"]=round(max(0,w["fin"]-off),3)
    json.dump(ws,open(os.path.join(DST,lid+".json"),"w",encoding="utf-8"),ensure_ascii=False)
print("ok")
