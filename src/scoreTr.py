import numpy as np,wave,subprocess
sr=44100; DUR=14.0; N=int(sr*DUR); A=np.zeros(N); rng=np.random.default_rng(9)
def add(sig,t0,vol=1.0):
    i=int(t0*sr)
    if i<0: sig=sig[-i:]; i=0
    if i>=N: return
    n=min(len(sig),N-i); A[i:i+n]+=sig[:n]*vol
def tone(f,dur,kind='sine',decay=0.0):
    t=np.arange(int(dur*sr))/sr
    s=np.sin(2*np.pi*f*t) if kind=='sine' else (np.sign(np.sin(2*np.pi*f*t)) if kind=='sq' else 2*((f*t)%1)-1)
    return s*np.exp(-decay*t)*np.minimum(1,t*300)*np.minimum(1,(dur-t)*300)
def noise(dur,decay):
    t=np.arange(int(dur*sr))/sr; return rng.uniform(-1,1,len(t))*np.exp(-decay*t)
def sweep(f0,f1,dur,kind='sine'):
    t=np.arange(int(dur*sr))/sr; f=f0*(f1/f0)**(t/dur); ph=np.cumsum(f)/sr
    s=np.sin(2*np.pi*ph) if kind=='sine' else 2*(ph%1)-1
    return s*np.minimum(1,t*300)*np.minimum(1,(dur-t)*300)
def clip(f,a=0,d=None,tempo=1.0):
    cmd=['ffmpeg','-v','error','-ss',str(a)]+(['-t',str(d)] if d else [])+['-i',f]+(['-af','atempo=%s'%tempo] if tempo!=1 else [])+['-ar',str(sr),'-ac','1','-f','f32le','-']
    x=np.frombuffer(subprocess.run(cmd,capture_output=True).stdout,np.float32).copy()
    fi=int(0.01*sr); x[:fi]*=np.linspace(0,1,fi); x[-fi:]*=np.linspace(1,0,fi); return x
W=lambda n,**k: clip('au12/w%d.mp3'%n,**k)
K=lambda n,**k: clip('au5/k%d.mp3'%n,**k)
C=lambda n,**k: clip('au6/c%d.mp3'%n,**k)
kick=lambda t0,v=0.9: add(sweep(150,45,0.18)*np.exp(-14*np.arange(int(0.18*sr))/sr),t0,v)
hit=lambda t0,v=0.9: (add(sweep(120,36,0.4)*np.exp(-8*np.arange(int(0.4*sr))/sr),t0,v),add(noise(0.25,14),t0,0.3))
G=lambda n,**k: clip('au10/g%d.mp3'%n,**k)
M=lambda n,**k: clip('au7/m%d.mp3'%n,**k)
# walking pizzicato
for i,t0 in enumerate(np.arange(0,1.6,0.4)): add(tone([392,440,392,330][i%4],0.15,'sine',12),t0,0.12)
# trip
add(W(2),1.55,1.0); hit(1.6,0.5)
add(sweep(900,200,0.6),1.7,0.05)
for k,tb in enumerate(np.arange(2.4,4.4,0.25)): add(tone(500+30*k,0.08,'sq',20),tb,0.05)
# frozen stiff
add(G(4,d=0.8),4.4,0.8); A[int(4.5*sr):int(5.2*sr)]*=0.6
# whistle
add(W(1),5.3,0.9); add(W(1,tempo=0.9),5.9,0.9); add(W(1),6.5,0.8)
# gasp
add(W(3),7.0,1.0); add(tone(110,1.4,'saw',1.5),7.0,0.06)
# rec beep + pings
add(W(4),8.5,1.0)
for i,tb in enumerate(np.arange(9.2,12.0,0.3)): add(M(3,d=0.4),tb,0.35+0.03*i)
for tb in np.arange(8.6,12.0,0.5): kick(tb,0.25)
add(sweep(200,3000,3.4,'saw')*np.linspace(0,1,int(3.4*sr)),8.6,0.04)
A[int(11.7*sr):int(12.0*sr)]*=0.05
# collapse
hit(12.0,1.0); add(K(7),12.15,0.9)
add(sweep(1200,60,0.5),12.0,0.15)
for k,(f,d) in enumerate([(311,0.35),(294,0.35),(277,0.35),(262,0.9)]): add(tone(f,d,'saw',2),12.9+k*0.28,0.07)
pk=np.abs(A).max(); A=np.tanh(A*0.9)/np.tanh(0.9) if pk>1 else A
pcm=(np.clip(A,-1,1)*32000).astype('<i2')
w=wave.open('audioTr.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes()); w.close()
