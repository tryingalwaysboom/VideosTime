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
L=lambda n,**k: clip('au6/c%d.mp3'%n,**k)
K7=lambda **k: clip('au5/k7.mp3',**k)
kick=lambda t0,v=0.9: add(sweep(150,45,0.18)*np.exp(-14*np.arange(int(0.18*sr))/sr),t0,v)
hit=lambda t0,v=0.9: (add(sweep(120,36,0.4)*np.exp(-8*np.arange(int(0.4*sr))/sr),t0,v),add(noise(0.25,14),t0,0.3))
# 0-1.2 soft intro
add(L(1,d=0.5),0.35,0.8)
# beat 1.2-7.0
beat=60/128; mel=[392,466,523,466,392,349,392,523]; bass=[98,98,117,87]
for i,tb in enumerate(np.arange(1.2,7.0,beat)):
    kick(tb); add(np.diff(noise(0.06,60),prepend=0),tb+beat/2,0.3)
    for j in (0,1):
        tt=tb+j*beat/2; add(tone(bass[i%4],beat/2*0.9,'sq',3),tt,0.12); add(tone(mel[(2*i+j)%8],beat/2*0.8,'saw',5),tt,0.10)
    if tb>5.0: add(np.diff(noise(0.04,80),prepend=0),tb+beat/4,0.25); add(np.diff(noise(0.04,80),prepend=0),tb+3*beat/4,0.25)
# attempts
for t0 in (1.2,2.15,3.1,4.05):
    add(L(1,d=0.5),t0+0.1,0.8); add(L(1,d=0.5),t0+0.45,0.7); add(L(2),t0+0.66,0.9)
add(sweep(300,2800,0.5,'saw'),1.9,0.1)
add(sweep(200,1800,0.4,'saw'),2.1,0.2)   # gasp
add(L(8),2.2,0.9)
add(sweep(300,2400,0.45,'saw'),3.4,0.12)
add(L(3),3.8,1.0); hit(3.8,0.8); add(L(8),3.85,1.0); add(L(8,tempo=0.8),4.45,0.8)
# frantic
add(L(4),5.0,0.95); add(L(4),6.0,0.9)
for t0 in np.arange(5.0,7.0,0.2): add(tone(180,0.08,'sq',20),t0+0.15,0.2)
add(sweep(200,3200,2.0,'saw'),5.0,0.08)
# 7.0 silence + heartbeat tension
for t0 in np.arange(7.05,8.4,0.45):
    add(tone(55,0.18,'sine',12),t0,0.7); add(tone(55,0.18,'sine',12),t0+0.18,0.5)
add(sweep(80,140,1.3,'saw'),7.05,0.05)
for t0 in np.arange(7.2,8.4,0.15): add(tone(1800,0.02,'sine',100),t0,0.12)
# 8.4 time-lapse
hit(8.4,0.7); add(L(5,d=4.2),8.4,0.95)
for t0 in np.linspace(8.4,12.3,40)**1: pass
tt=8.5; step=0.25
while tt<12.3:
    add(tone(900,0.02,'sine',100),tt,0.14); tt+=step; step=max(0.05,step*0.93)
add(sweep(100,2000,3.9,'saw'),8.4,0.05)
# 12.4 skeleton
hit(12.4,1.0); add(L(7),12.5,0.9)
# 13.4 verified
add(L(6),13.35,1.0)
for j,f in enumerate((523,659,784,1047)): add(tone(f,0.12,'sq',8),13.4+j*0.1,0.1)
# 14.4 expired
add(L(2),14.4,1.0); hit(14.4,1.0); add(sweep(900,300,0.5,'saw'),14.4,0.12)
add(L(7,tempo=0.8),14.8,0.9); add(K7(),15.0,0.9)
A=A/np.abs(A).max()*0.9
w=wave.open('audioC.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(A,-1,1)*32767).astype(np.int16).tobytes()); w.close()
