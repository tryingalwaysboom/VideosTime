import numpy as np,wave,subprocess
sr=44100; DUR=17.0; N=int(sr*DUR); A=np.zeros(N); rng=np.random.default_rng(9)
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
H=lambda n,**k: clip('au11/h%d.mp3'%n,**k)
K=lambda n,**k: clip('au5/k%d.mp3'%n,**k)
C=lambda n,**k: clip('au6/c%d.mp3'%n,**k)
kick=lambda t0,v=0.9: add(sweep(150,45,0.18)*np.exp(-14*np.arange(int(0.18*sr))/sr),t0,v)
hit=lambda t0,v=0.9: (add(sweep(120,36,0.4)*np.exp(-8*np.arange(int(0.4*sr))/sr),t0,v),add(noise(0.25,14),t0,0.3))
# calm library: soft pad + page
for i,t0 in enumerate(np.arange(0,3.0,1.0)): add(tone([262,330,392][i%3],1.0,'sine',1.5),t0,0.05)
add(H(1),1.7,0.8); add(H(1),2.6,0.6)
# itch
add(H(2),3.1,0.9); add(H(2),4.2,0.8)
add(sweep(300,800,0.3),3.0,0.06)
# tension build 5.5-10
for i,tb in enumerate(np.arange(5.5,10.0,0.5)): kick(tb,0.3+0.04*i)
add(sweep(200,2400,4.5,'saw')*np.linspace(0,1,int(4.5*sr)),5.5,0.05)
add(H(2,tempo=1.0),6.5,0.9); add(H(2),8.6,0.9)
# librarian shh at 8.0
add(H(3),8.0,1.0); add(sweep(300,150,0.5),8.0,0.1)
# relief
A[int(10.0*sr):int(10.3*sr)]*=0.3
add(sweep(600,300,0.5),10.2,0.08)
# inhale build
add(H(4),11.9,1.0); add(H(4,tempo=0.9),12.7,1.0)
for tb in np.arange(11.6,14.0,0.4): kick(tb,0.3)
add(sweep(200,3000,2.0,'saw')*np.linspace(0,1,int(2.0*sr)),11.8,0.05)
A[int(13.6*sr):int(14.0*sr)]*=0.05
# SNEEZE
hit(14.0,1.0); hit(14.0,0.9); add(H(5),14.0,1.0)
add(H(7),14.05,1.0); add(H(6),14.3,0.9)
add(sweep(400,100,1.2),14.4,0.1)
for k,(f,d) in enumerate([(311,0.35),(294,0.35),(277,0.35),(262,0.9)]): add(tone(f,d,'saw',2),15.4+k*0.38,0.09)
pk=np.abs(A).max(); A=np.tanh(A*0.9)/np.tanh(0.9) if pk>1 else A
pcm=(np.clip(A,-1,1)*32000).astype('<i2')
w=wave.open('audioSn.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes()); w.close()
