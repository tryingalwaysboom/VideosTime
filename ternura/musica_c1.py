"""Música del capítulo 1: una nana de caja de música hecha por código (sin créditos). Fa mayor, 3/4, tranquila."""
import numpy as np, wave, sys, random
SR=48000; BPM=64; B=60/BPM
def hz(m): return 440*2**((m-69)/12)
def nota(m,dur,vel):
    n=int(SR*min(dur,4.5)); t=np.arange(n)/SR; f=hz(m)
    y=np.sin(2*np.pi*f*t)*np.exp(-t/1.25)+.28*np.sin(2*np.pi*2*f*t)*np.exp(-t/.7)+.10*np.sin(2*np.pi*3.01*f*t)*np.exp(-t/.28)+.05*np.sin(2*np.pi*5.4*f*t)*np.exp(-t/.09)
    a=int(.004*SR); y[:a]*=np.linspace(0,1,a); y[-int(.05*SR):]*=np.linspace(1,0,int(.05*SR)); return y*vel
ACO={"F":(53,60,65),"Dm":(50,57,62),"Bb":(46,53,58),"C":(48,55,60),"Am":(45,52,57),"Gm":(43,50,58)}
FR=[("F",[(69,1),(72,1),(77,1)]),("Dm",[(74,2),(69,1)]),("Bb",[(70,1),(74,1),(77,1)]),("C",[(76,2),(72,1)]),
    ("F",[(77,1),(72,1),(69,1)]),("Am",[(76,1),(72,1),(69,1)]),("Bb",[(70,1),(69,1),(67,1)]),("C",[(67,3)]),
    ("F",[(69,1),(72,1),(77,1)]),("Dm",[(74,2),(77,1)]),("Gm",[(70,1),(74,1),(70,1)]),("C",[(72,2),(76,1)]),
    ("F",[(77,2),(72,1)]),("Bb",[(74,1),(70,1),(67,1)]),("C",[(67,1),(69,1),(64,1)]),("F",[(65,3)])]
def main(out,total):
    rnd=random.Random(4); y=np.zeros(int(SR*(total+6))); t=.3; bar=0
    while t<total-5:
        ch,mel=FR[bar%len(FR)]
        for i,m in enumerate(ACO[ch]):
            s=int((t+i*B+rnd.uniform(-.008,.008))*SR); x=nota(m+12,3,.16+.03*rnd.random()); y[s:s+len(x)]+=x
        tt=t
        for m,d in mel:
            s=int((tt+rnd.uniform(-.008,.008))*SR); x=nota(m+12,d*B+2,.36+.08*rnd.random()); y[s:s+len(x)]+=x; tt+=d*B
        t+=3*B; bar+=1
    for i,m in enumerate((53,60,65,69,77)):
        s=int((t+i*.16)*SR); x=nota(m+12,4.5,.3); y[s:s+len(x)]+=x
    y=y[:int(SR*total)]; y[-int(SR*1.2):]*=np.linspace(1,.0,int(SR*1.2)); y=y/np.max(np.abs(y))*.7
    with wave.open(out,"w") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y*32767).astype(np.int16).tobytes())
if __name__=="__main__": main(sys.argv[1],float(sys.argv[2]))
