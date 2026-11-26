"""Mezcla del capítulo 1: voces en su sitio (−15 LUFS), nana de caja de música por debajo y apartándose cuando alguien habla,
y el lápiz sobre el papel sincronizado con cada letra. Une las partes de tmp_c1/ y saca el vídeo final."""
import os, subprocess, sys
import render_c1 as V
from render_c1 import TL, TOTAL, WI, WE, HERE, VOZ
TMP=os.path.join(HERE,"tmp_c1"); SFX=os.path.join(HERE,"..","descargas","mateo_sfx")
def run(a): subprocess.run(a,check=True)
def main(out):
    ins,flt=[],[]
    for i,lid in enumerate(TL):
        ins+=["-i",os.path.join(VOZ,lid+".wav")]; ms=int(TL[lid][0]*1000); flt.append(f"[{i}:a]aresample=48000,afade=t=in:d=0.012,adelay={ms}|{ms},apad[a{i}]")
    n=len(TL)
    flt.append("".join(f"[a{i}]" for i in range(n))+f"amix=inputs={n}:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},acompressor=threshold=-18dB:ratio=3:attack=5:release=120,loudnorm=I=-15:TP=-1.5:LRA=9,aresample=48000[voz]")
    vwav=os.path.join(TMP,"voces.wav"); run(["ffmpeg","-y","-v","error",*ins,"-filter_complex",";".join(flt),"-map","[voz]","-ar","48000","-ac","1",vwav])
    mraw=os.path.join(TMP,"musica.wav"); run([sys.executable,os.path.join(HERE,"musica_c1.py"),mraw,f"{TOTAL:.2f}"])
    mwav=os.path.join(TMP,"musica_duck.wav")
    run(["ffmpeg","-y","-v","error","-i",mraw,"-i",vwav,"-filter_complex",
         f"[0:a]aecho=0.8:0.6:90|180:0.25|0.15,lowpass=f=7000,loudnorm=I=-27:TP=-8,aresample=48000[m0];[1:a]apad,atrim=0:{TOTAL:.2f}[key];"
         f"[m0][key]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[mus]","-map","[mus]","-ar","48000","-ac","1","-t",f"{TOTAL:.2f}",mwav])
    tl=[WI("L11",9+i) for i in range(5)]; te=[min(WE("L11",9+i),tl[i]+.95) for i in range(5)]
    expr="+".join(f"between(t,{a:.3f},{b:.3f})" for a,b in zip(tl,te))
    lap=os.path.join(TMP,"lapiz.wav")
    run(["ffmpeg","-y","-v","error","-stream_loop","-1","-i",os.path.join(SFX,"crayola.mp3"),"-t",f"{TOTAL:.2f}","-af",
         f"aresample=48000,loudnorm=I=-24:TP=-6,aresample=48000,asetpts=N/SR/TB,volume='min(1,{expr})':eval=frame,lowpass=f=8000,volume=-9dB","-ac","1",lap])
    wav=os.path.join(TMP,"mezcla.wav")
    run(["ffmpeg","-y","-v","error","-i",vwav,"-i",mwav,"-i",lap,"-filter_complex",
         f"[0:a]apad,atrim=0:{TOTAL:.2f}[v];[1:a]apad,atrim=0:{TOTAL:.2f}[m];[2:a]apad,atrim=0:{TOTAL:.2f}[l];[v][m][l]amix=inputs=3:normalize=0:duration=longest,alimiter=limit=0.95[mx]","-map","[mx]","-ac","2",wav])
    lst=os.path.join(TMP,"list.txt"); open(lst,"w").write("".join(f"file 'p{i}.mp4'\n" for i in range(6)))
    run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",lst,"-i",wav,"-map","0:v","-map","1:a","-c:v","libx264","-preset","medium","-crf","21","-maxrate","2800k","-bufsize","5600k",
         "-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-t",f"{TOTAL:.2f}","-movflags","+faststart",out])
if __name__=="__main__": main(sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,"abuelo_cap1.mp4"))
