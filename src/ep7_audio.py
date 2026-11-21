import math, wave, sys, os, numpy as np
src=open('make_video.py').read()
exec(src[:src.index('SC=[')])
a0=src.index('K=OW/W'); a1=src.index('BG={'); exec(src[a0:a1])
DUR=15.0; sr=44100; N=int(sr*DUR); A=np.zeros(N); rng=np.random.default_rng(55)
c0=src.index('def add(sig'); c1=src.index('for g in np.arange'); exec(src[c0:c1])
BEAT=60/128
def env(sig,d_): return sig*np.exp(-d_*np.arange(len(sig))/sr)
def kick(t,v=0.6): add(env(sweep(160,42,0.2),14),t,v); add(noise(0.01,200),t,0.15)
def snare(t,v=0.3): add(env(noise(0.16,22),1),t,v); add(tone(190,0.08,'sine',40),t,v*0.5)
def hat(t,v=0.1): add(env(noise(0.04,60),1),t,v)
FLY=None
def _fly():
    global FLY
    if FLY is None:
        with wave.open('/tmp/stk/vo/fly.wav') as w: FLY=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
        FLY=FLY/ (np.abs(FLY).max()+1e-6)
    return FLY
def buzz(t0,t1,f=210,v=0.12):
    x=_fly(); n=int((t1-t0)*sr); out=np.zeros(n); cf=int(0.15*sr); pos=0; k=0
    while pos<n:
        seg=x.copy(); seg[:cf]*=np.linspace(0,1,cf); seg[-cf:]*=np.linspace(1,0,cf)
        e=min(n,pos+len(seg)); out[pos:e]+=seg[:e-pos]; pos+=len(seg)-cf
    tt=np.arange(n)/sr; out*=np.minimum(1,np.minimum(tt/0.08,(t1-t0-tt)/0.08))
    add(out,t0,v*5.0)
def buzz_old(t0,t1,f=210,v=0.12):
    n=int((t1-t0)*sr); tt=np.arange(n)/sr; fm=f*(1+0.25*np.sin(2*np.pi*(9*tt+2*np.sin(2*np.pi*3*tt))))
    ph=2*np.pi*np.cumsum(fm)/sr; sig=np.sign(np.sin(ph))*0.5+np.sin(ph*2)*0.3; add(sig*np.minimum(1,np.minimum(tt/0.05,(t1-t0-tt)/0.05)),t0,v)
# fly buzz
buzz(0.0,1.2); buzz(1.2,2.0,260,0.08); buzz(2.0,3.4,230,0.1); buzz(3.4,5.2,240,0.1); buzz(5.35,6.0,240,0.1); buzz(6.0,8.4,170,0.07); buzz(8.8,10.4,240,0.1); buzz(12.8,15.0,230,0.1)
add(env(sweep(150,60,0.3),10),0.0,0.35); add(sweep(300,1400,0.4),0.0,0.1)
# wake / hop
add(env(sweep(500,900,0.15,'sq'),12),1.2,0.2)
# slipper throw + lamp crash
add(env(sweep(300,900,0.4),4),2.8,0.18); add(tone(200,0.1,'sine',20),2.0,0.2)
for t in (2.0,2.7,3.3,4.0,10.4):
    add(env(sweep(150,420,0.25),6),t,0.3)
for i,t in enumerate(np.arange(2.0,5.4,BEAT)): kick(t,0.4); hat(t+BEAT/2,0.1)
add(env(noise(0.5,6),1),3.3,0.9); add(env(sweep(180,50,0.4),8),3.3,0.9)
for f in (1900,2300,1500,2700): add(tone(f,0.08,'sine',30),3.35+rng.uniform(0,0.2),0.15)
# spray
add(env(noise(1.0,1.5),1)*np.linspace(1,0.6,sr),4.3,0.4); add(env(noise(0.7,3),1),5.25,0.5)
for t in (5.4,5.55,5.7): add(env(sweep(800,300,0.12,'sq'),20),t,0.18)
# sniper: heartbeat + riser
for t in np.arange(6.0,8.4,0.5): add(env(sweep(120,45,0.15),20),t,0.6); add(env(sweep(120,45,0.15),20),t+0.14,0.4)
add(sweep(200,2500,2.3),6.0,0.07); add(tone(1500,0.6,'sine',0.3)*0,6.0,0)
for t in (6.4,7.1,7.8): add(tone(2200,0.04,'sine',60),t,0.1)
# slap
add(env(noise(0.3,10),1),8.45,1.0); add(env(sweep(300,40,0.4),6),8.45,1.0); add(tone(140,0.1,'sq',20),8.45,0.3)
n_=int(0.3*sr); add(env(sweep(1400,120,0.3,'saw'),3)*(0.6+0.4*np.sign(np.sin(2*np.pi*70*np.arange(n_)/sr))),8.45,0.4)
# fall + stars
add(env(sweep(800,100,0.7),3),8.9,0.25); add(env(noise(0.25,12),1),9.4,0.7); add(env(sweep(120,40,0.4),8),9.4,0.8)
for i in range(6): add(tone(1318+120*i,0.1,'sine',18),9.6+i*0.14,0.1)
# sad trombone
for i,(f,dur,tt) in enumerate(((233,0.45,13.2),(220,0.45,13.6),(208,0.5,14.0),(196,0.9,14.4))): add(tone(f,dur,'saw',3)*np.linspace(1,0.6,int(dur*sr)),tt,0.08)
# snore
for t in (13.4,14.2): add(env(sweep(90,60,0.5,'saw'),3),t,0.12)
A=A/np.abs(A).max()*0.9
voices=[a for a in sys.argv[1:]]  # "file:time"
for v in voices:
    f,t=v.rsplit(':',1)
    os.system(f'ffmpeg -y -loglevel error -i "{f}" -ar 44100 -ac 1 /tmp/stk/vo/_t.wav')
    with wave.open('/tmp/stk/vo/_t.wav') as w: x=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
    i=int(float(t)*sr); A[i:i+len(x)]=A[i:i+len(x)]*0.45+x[:N-i]*1.0
A=np.clip(A,-1,1)
with wave.open('audio7.wav','wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((A*32767).astype(np.int16).tobytes())
