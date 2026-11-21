import numpy as np,wave,subprocess
sr=44100; DUR=17.0; N=int(sr*DUR); A=np.zeros(N); rng=np.random.default_rng(5)
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
S=lambda n,**k: clip('au8/s%d.mp3'%n,**k)
C=lambda n,**k: clip('au6/c%d.mp3'%n,**k)
M3x=None
K=lambda n,**k: clip('au5/k%d.mp3'%n,**k)
kick=lambda t0,v=0.9: add(sweep(150,45,0.18)*np.exp(-14*np.arange(int(0.18*sr))/sr),t0,v)
hit=lambda t0,v=0.9: (add(sweep(120,36,0.4)*np.exp(-8*np.arange(int(0.4*sr))/sr),t0,v),add(noise(0.25,14),t0,0.3))
beat=60/128; mel=[392,466,523,466,392,349,392,523]; bass=[98,98,117,87]
def chase(a,b):
    for i,tb in enumerate(np.arange(a,b,beat)):
        kick(tb); add(np.diff(noise(0.06,60),prepend=0),tb+beat/2,0.3)
        for j in (0,1):
            tt=tb+j*beat/2; add(tone(bass[i%4],beat/2*0.9,'sq',3),tt,0.12); add(tone(mel[(2*i+j)%8],beat/2*0.8,'saw',5),tt,0.10)
for i,t0 in enumerate(np.arange(0,1.2,beat)): add(tone([98,117][i%2],beat*0.8,'sq',4),t0,0.07)
add(S(2),0.1,0.8)
M3=lambda **k: clip('au7/m3.mp3',**k)
# sigh / kid tease
add(tone(300,0.25,'sine',6),0.9,0.1)
chase(1.4,2.6); add(sweep(300,2600,0.4,'saw'),1.2,0.1); add(S(3),1.5,0.9)
# price check shout + lane1 draining
add(tone(900,0.06,'sine',30),2.8,0.2); add(sweep(500,300,0.6,'saw'),2.9,0.12)
for t0 in (3.0,3.4,3.8,4.2): add(M3(d=0.6),t0,0.6); add(S(1,d=0.4),t0+0.1,0.5)
for t0 in (3.2,4.2): add(sweep(200,1800,0.5,'saw'),t0-0.1,0.1)
add(sweep(200,1800,0.5,'saw'),3.3,0.12)
chase(4.4,6.4); add(S(3),4.6,0.8); add(S(3),5.7,0.8)
add(S(2),4.8,1.0); add(C(8),4.85,1.0); hit(4.8,0.8)
add(C(2),6.0,0.9); add(M3(),6.1,0.8)
add(sweep(200,3000,1.0,'saw'),4.4,0.07)
# defeat/approach
add(sweep(400,90,0.8),7.0,0.14)
add(S(1),8.6,0.9); add(S(1),9.6,0.8)
for i in range(11): add(tone(1760,0.05,'sq',30),8.6+i*0.12,0.12)
add(sweep(200,2000,0.9,'saw'),9.9,0.07)
for t0 in np.arange(10.05,10.7,0.32):
    add(tone(55,0.18,'sine',12),t0,0.7); add(tone(55,0.18,'sine',12),t0+0.18,0.5)
add(sweep(2200,150,0.3,'saw'),10.7,0.15)
add(S(4),10.95,1.0); add(S(5),11.0,1.0); hit(11.0,1.0)
# stamp lifts, door opens, wind
add(sweep(150,600,0.7),12.5,0.1)
add(sweep(200,1500,1.2,'saw')*np.linspace(0,1,int(1.2*sr)),12.4,0.07)
add(noise(2.2,0.6),12.5,0.15)
for t0 in np.arange(12.8,14.6,0.16): add(np.diff(noise(0.05,40),prepend=0),t0,0.35)
add(K(7),13.1,0.9); add(S(2),13.6,0.9)
A=A/np.abs(A).max()*0.9
w=wave.open('audioQ2.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(A,-1,1)*32767).astype(np.int16).tobytes()); w.close()
