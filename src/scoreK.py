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
L=lambda n,**k: clip('au5/k%d.mp3'%n,**k)
kick=lambda t0,v=0.9: add(sweep(150,45,0.18)*np.exp(-14*np.arange(int(0.18*sr))/sr),t0,v)
# 0-1.4 hook
add(L(1),0.15,0.8); add(L(8),0.3,0.9); add(L(8),0.85,0.9)
# 1.4-4.6 chase beat
beat=60/128; mel=[392,466,523,466,392,349,392,523]; bass=[98,98,117,87]
for i,tb in enumerate(np.arange(1.4,6.0,beat)):
    kick(tb); add(np.diff(noise(0.06,60),prepend=0),tb+beat/2,0.3)
    if i%1==0:
        for j in (0,1):
            tt=tb+j*beat/2; add(tone(bass[i%4],beat/2*0.9,'sq',3),tt,0.12); add(tone(mel[(2*i+j)%8],beat/2*0.8,'saw',5),tt,0.10)
    if tb>4.6: add(np.diff(noise(0.04,80),prepend=0),tb+beat/4,0.25); add(np.diff(noise(0.04,80),prepend=0),tb+3*beat/4,0.25)
for t0 in (1.4,2.2,3.0,3.8,4.6): add(sweep(300,2600,0.3)*np.linspace(0,1,int(0.3*sr)),t0-0.25,0.12)
for t0 in (1.5,2.3,3.1,3.9,4.7,5.0,5.3,5.6): add(L(2),t0,0.85)
add(sweep(200,3000,1.4,'saw'),4.6,0.07)
# 6.0-7.2 defeat: silence, sad slide
add(sweep(400,90,0.9),6.1,0.18)
for t0 in (6.5,6.9): add(tone(1100,0.03,'sine',50),t0,0.25)
# 7.2-8.8 realization
add(L(1),7.35,1.0); add(sweep(300,2800,0.35,'saw'),7.45,0.14)
k=sweep(150,40,0.4); add(k*np.exp(-9*np.arange(len(k))/sr),7.7,0.9)
add(L(3),7.95,1.0)
# 8.8-9.6 joy
for j,f in enumerate((523,659,784,1047,1319)): add(tone(f,0.13,'sq',8),8.85+j*0.1,0.15)
add(L(1),9.1,0.9)
# 10.0 door slam
add(L(4),9.95,1.0); kick(10.0,0.8)
# 10.6-11.4 pat pockets
add(L(8),10.65,0.9); add(L(8),11.1,0.8)
add(sweep(900,400,0.3),11.4,0.18)
add(L(5),11.5,1.0); add(L(5),11.95,0.9)
# 12.4 face on glass
add(tone(2093,0.3,'sine',6),12.35,0.2); add(tone(2637,0.3,'sine',6),12.45,0.15)
add(L(6),12.55,1.0); add(L(6),13.1,0.9)
add(sweep(90,60,1.6,'saw'),12.4,0.07)
for t0 in (12.6,13.1,13.6): add(tone(55,0.18,'sine',12),t0,0.6); add(tone(55,0.18,'sine',12),t0+0.18,0.4)
# 14.0 slide
add(L(6,tempo=0.5),14.0,1.0)
# 15.2 end
k=sweep(120,36,0.4); add(k*np.exp(-8*np.arange(len(k))/sr),15.2,0.8); add(noise(0.2,14),15.2,0.3)
add(L(7),15.4,0.9)
A=A/np.abs(A).max()*0.9
w=wave.open('audioK.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(A,-1,1)*32767).astype(np.int16).tobytes()); w.close()
