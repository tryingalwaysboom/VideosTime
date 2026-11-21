import numpy as np,wave,subprocess
sr=44100; DUR=17.0; N=int(sr*DUR); A=np.zeros(N); rng=np.random.default_rng(3)
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
def clip(f,a=0,d=None):
    cmd=['ffmpeg','-v','error','-ss',str(a)]+(['-t',str(d)] if d else [])+['-i',f,'-ar',str(sr),'-ac','1','-f','f32le','-']
    x=np.frombuffer(subprocess.run(cmd,capture_output=True).stdout,np.float32).copy()
    fi=int(0.01*sr); x[:fi]*=np.linspace(0,1,fi); x[-fi:]*=np.linspace(1,0,fi); return x
L=lambda n,**k: clip('au4/s%d.mp3'%n,**k)
# 0-1.3 hook: phone buzz + notification + low batt beeps
for t0 in (0.05,0.3): add(tone(70,0.2,'sq',2)*0.6+noise(0.2,10)*0.3,t0,0.35)
add(tone(1568,0.25,'sine',8),0.6,0.3); add(tone(2093,0.3,'sine',8),0.68,0.22)
add(L(1),0.95,0.9)
# 1.3-4.2 chase: 128bpm chiptune
beat=60/128; mel=[392,466,523,466,392,349,392,523]; bass=[98,98,117,87]
for i,tb in enumerate(np.arange(1.3,4.2,beat)):
    k=sweep(150,45,0.18); add(k*np.exp(-14*np.arange(len(k))/sr),tb,0.9)
    add(np.diff(noise(0.06,60),prepend=0),tb+beat/2,0.3)
    for j in (0,1):
        tt=tb+j*beat/2
        add(tone(bass[i%4],beat/2*0.9,'sq',3),tt,0.12); add(tone(mel[(2*i+j)%8],beat/2*0.8,'saw',5),tt,0.10)
for t0 in (1.3,2.0,2.7,3.4,4.0):
    add(sweep(300,2600,0.3)*np.linspace(0,1,int(0.3*sr)),t0-0.25,0.13)
add(L(2),1.3,0.8); add(L(2),2.05,0.8); add(L(2),2.8,0.8); add(L(2),3.5,0.7)
# 4.2 plug: music cuts, click + happy sparkle
add(L(3),4.2,1.0)
for j,f in enumerate((784,988,1175,1568)): add(tone(f,0.15,'sine',9),4.45+j*0.12,0.18)
# 5.4 death: power-down sweep, boom, then near silence
add(sweep(900,60,0.55,'saw'),5.4,0.25); add(noise(0.3,10),5.4,0.5); add(L(4),5.4,1.0); add(L(1),5.0,0.7)
k=sweep(130,38,0.5); add(k*np.exp(-7*np.arange(len(k))/sr),5.42,1.0)
# 5.9-6.6 silence w/ tiny hum
add(tone(55,0.7,'sine',2),5.9,0.10)
# 6.6-8.8 big battery insert: ticks accelerating + rising charge blips + drone
t=6.6; gap=0.34
while t<8.8:
    add(tone(1500,0.03,'sine',50),t,0.28); t+=gap; gap=max(0.12,gap*0.93)
for k_,t0 in enumerate((6.8,7.2,7.6,8.0,8.4)): add(tone(420+110*k_,0.2,'sine',6),t0,0.25); add(tone((420+110*k_)*2,0.2,'sine',9),t0,0.10)
add(sweep(90,300,2.2,'saw'),6.6,0.10)
# 8.8 alive
add(L(5),8.8,1.0); add(noise(0.2,18),8.8,0.4)
# 9.7 ring
add(L(6),9.7,1.0); add(L(6),10.15,0.9)
for t0 in (9.7,9.95,10.2,10.45): add(tone(70,0.12,'sq',3),t0,0.18)
# 10.6 answer click + confused sting
add(tone(1000,0.04,'sine',40),10.6,0.3); add(sweep(700,350,0.35),11.3,0.2)
# 12.4 thinking: tension builds
add(L(7,d=1.6),12.4,0.8)
for t0 in (12.5,12.95,13.35): add(tone(55,0.18,'sine',12),t0,0.6); add(tone(55,0.18,'sine',12),t0+0.18,0.4)
add(sweep(200,2400,1.6,'saw'),12.4,0.06)
add(tone(1568,0.25,'sine',8),13.4,0.3); add(tone(2093,0.3,'sine',8),13.48,0.22)
for j,f in enumerate((880,740,620,520,440)): add(tone(f,0.09,'sq',10),13.6+j*0.08,0.14)
# 14.0 silent scream: everything cut, only tinnitus + slow heartbeat
add(tone(3400,1.4,'sine',0.0)*np.linspace(1,0.5,int(1.4*sr)),14.0,0.07)
for t0 in (14.3,14.9): add(tone(50,0.2,'sine',10),t0,0.5)
# 15.4 snap back: boom, glass, trombone
add(sweep(300,3200,0.2,'saw'),15.2,0.12)
k=sweep(130,38,0.5); add(k*np.exp(-7*np.arange(len(k))/sr),15.4,1.0); add(noise(0.3,12),15.4,0.5)
add(L(4),15.4,0.9); add(L(8),15.7,0.9)
for t0 in (16.2,16.6): add(tone(1900,0.09,'sq',10),t0,0.22)
A=A/np.abs(A).max()*0.9
w=wave.open('audioV5.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(A,-1,1)*32767).astype(np.int16).tobytes()); w.close()
