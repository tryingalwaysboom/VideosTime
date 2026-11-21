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
G=lambda n,**k: clip('au10/g%d.mp3'%n,**k)
C=lambda n,**k: clip('au6/c%d.mp3'%n,**k)
K=lambda n,**k: clip('au5/k%d.mp3'%n,**k)
kick=lambda t0,v=0.9: add(sweep(150,45,0.18)*np.exp(-14*np.arange(int(0.18*sr))/sr),t0,v)
hit=lambda t0,v=0.9: (add(sweep(120,36,0.4)*np.exp(-8*np.arange(int(0.4*sr))/sr),t0,v),add(noise(0.25,14),t0,0.3))
beat=60/128
# cheerful walk 0-1.4
for i,t0 in enumerate(np.arange(0,1.4,beat)): add(tone([262,330,392,330][i%4],beat*0.7,'sq',5),t0,0.08); kick(t0,0.4)
# knot reveal
add(sweep(300,1800,0.25,'saw'),1.6,0.1); hit(1.8,0.6); add(G(1),1.9,0.8)
# tension: rustle + grunts + rising pulse 3-9
for t0 in (3.1,4.1,5.1): add(G(1),t0,0.7)
add(G(2,d=1.5),3.5,0.7)
for t0 in (6.0,6.9,7.8,8.5): add(G(1),t0,0.8)
add(G(2),6.1,0.8); add(G(2,tempo=1.2),7.6,0.9)
for i,tb in enumerate(np.arange(3.0,9.0,0.5-0.0)):
    kick(tb,0.25+0.03*i)
add(sweep(200,2000,3.0,'saw')*np.linspace(0,1,int(3.0*sr)),6.0,0.05)
# rage 9-10.5
for t0 in np.arange(9.0,10.5,0.25): add(G(1,d=0.3),t0,0.6); kick(t0,0.7)
add(G(2,tempo=1.5),9.2,0.9)
add(sweep(300,2500,1.4,'saw'),9.0,0.09)
# victory
A[int(10.4*sr):int(10.5*sr)]*=0.1
add(G(3),10.5,1.0)
for k,(f,d) in enumerate([(523,0.12),(659,0.12),(784,0.12),(1047,0.3)]): add(tone(f,d,'sq',4),10.55+k*0.12,0.1)
# plug in, silence, record scratch
add(noise(0.04,60),11.2,0.4); add(tone(1400,0.05,'sq',20),11.2,0.1)
A[int(11.95*sr):int(13.3*sr)]*=0.05
add(G(4),12.0,1.0)
add(tone(220,1.2,'sine',3),12.1,0.05)
# no entry buzz
add(C(2),12.6,0.8)
# pocket glow bluetooth
add(G(5),13.4,0.9); add(sweep(400,3000,0.6,'saw'),13.4,0.08)
A[int(13.8*sr):int(14.0*sr)]*=0.05
# IMPACT: boom + scream
hit(14.0,1.0); hit(14.0,0.8); add(G(6),14.0,1.0); add(C(8),14.05,0.7)
add(sweep(400,120,1.2),14.4,0.08)
for k,(f,d) in enumerate([(311,0.35),(294,0.35),(277,0.35),(262,0.9)]): add(tone(f,d,'saw',2),15.2+k*0.38,0.09)
pk=np.abs(A).max(); A=np.tanh(A*0.9)/np.tanh(0.9) if pk>1 else A
pcm=(np.clip(A,-1,1)*32000).astype('<i2')
w=wave.open('audioEar.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes()); w.close()
