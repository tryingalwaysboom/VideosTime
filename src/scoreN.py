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
F=lambda n,**k: clip('au9/f%d.mp3'%n,**k)
kick=lambda t0,v=0.9: add(sweep(150,45,0.18)*np.exp(-14*np.arange(int(0.18*sr))/sr),t0,v)
hit=lambda t0,v=0.9: (add(sweep(120,36,0.4)*np.exp(-8*np.arange(int(0.4*sr))/sr),t0,v),add(noise(0.25,14),t0,0.3))
# sneaky pizzicato bed 0-3
for i,t0 in enumerate(np.arange(0,3.0,0.5)): add(tone([196,233,262,233][i%4],0.12,'sq',25),t0,0.07)
add(F(7),0.2,0.7); add(F(1),1.45,0.8)
add(F(2),1.85,0.9); hit(1.95,0.5); add(sweep(500,200,0.3),2.0,0.08)
add(F(7),3.0,0.5)
# microwave hum + tension heartbeat 4.6-7.4
add(F(3,d=3.0),4.6,0.35)
for tb in np.arange(4.6,7.4,0.5): kick(tb,0.5)
add(sweep(200,1800,2.8,'saw'),4.6,0.05)
# stop at 1: click + victory
add(noise(0.05,80),7.4,0.5); add(tone(660,0.1,'sq',8),7.45,0.15); add(tone(990,0.2,'sq',6),7.55,0.15)
# hot plate scream
add(F(5),7.95,0.9); hit(7.9,0.5)
# beeps
for tb in (9.0,9.35,9.7,10.05,10.4): add(F(4),tb,0.9)
hit(9.3,0.6)
for tb in np.arange(9.0,11.2,0.35): add(tone(2400,0.12,'sine',4),tb+0.02,0.12)
# light + silence
add(F(6),11.2,0.9)
add(tone(55,2.4,'sine',0.5),11.6,0.12)
for tb in np.arange(11.6,14.0,0.6): kick(tb,0.35)
# mom shout
add(F(12),12.4,1.0); add(sweep(60,40,1.2),12.4,0.12)
# duck before impact: dramatic silence
i0=int(13.55*sr); i1=int(14.0*sr); A[i0:i1]*=0.05
add(sweep(3000,300,0.3),13.7,0.12); add(F(8),13.6,1.0)
# IMPACT: boom + screams
hit(14.0,1.0); hit(14.0,0.8); add(F(9),14.0,0.9); add(F(10,tempo=1.0),14.05,0.9)
add(sweep(400,120,1.2),14.4,0.08)
for k,(f,d) in enumerate([(311,0.35),(294,0.35),(277,0.35),(262,0.9)]): add(tone(f,d,'saw',2),15.0+k*0.38,0.09)
A*=1.0; pk=np.abs(A).max(); A=np.tanh(A*0.9)/np.tanh(0.9) if pk>1 else A
pcm=(np.clip(A,-1,1)*32000).astype('<i2')
w=wave.open('audioN.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes()); w.close()
