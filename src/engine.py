# ---- shared engine (exec'd after ep7_pre.py header)
import sys
def smooth(u): u=max(0,min(1,u)); return u*u*(3-2*u)
def lerp2(a,b,u): return (lerp(a[0],b[0],u),lerp(a[1],b[1],u))
def upv(hip,lean,L,o=0): return (hip[0]+L*math.sin(lean)+o*math.cos(lean),hip[1]-L*math.cos(lean)+o*math.sin(lean))
def dec(T,t0,k=10): return math.exp(-k*(T-t0)) if T>=t0 else 0.0
def setbg(kind='room',tint=None):
    global BGS
    b=(bg_room(True) if kind=='room' else bg_street(False)); o=int(OFF*K); img=Image.new('RGB',(OW,OH))
    img.paste(b,(0,o)); img.paste(b.crop((0,OH-8,OW,OH)).resize((OW,-o)),(0,OH+o))
    if tint: img=Image.fromarray(np.clip(np.asarray(img,np.float32)*np.array(tint,np.float32),0,255).astype(np.uint8))
    BGS=img
# pose helpers  -> (hip,lean,arms,legs,face)
UP=((PI-0.4,PI-0.5),(PI+0.4,PI+0.5))
def stand(x,face='happy',y=796,lean=0.0,arms=None): return (x,y),lean,(arms or ((0.12,0.0),(-0.12,0.0))),STAND,face
def walkp(x,T,face='happy',amp=0.6,lean=0.08,arms=None):
    return (x,796-6*abs(math.sin(T*9))),lean,(arms or ((0.5*math.sin(T*9),0.3),(-0.5*math.sin(T*9),-0.3))),legsw(T*2*PI*2.2,amp),face
def legsw(ph,amp=0.5): return tuple((amp*math.sin(ph+o),amp*math.sin(ph+o)-0.4*max(0,math.cos(ph+o))) for o in (0,PI))
def lying(x,face='dead',y=905): return (x,y),-1.5,((1.9,1.9),(-1.6,-1.6)),((1.5,1.5),(1.5,1.55)),face
def fall(u,x0,x1,face='shock'):
    u=max(0,min(1,u)); e=ease(u); s=math.sin(PI*u)
    return (lerp(x0,x1,u),lerp(796,905,u*u)-150*s),-1.5*e-0.9*s,((PI-0.4+0.6*s,PI-0.5),(PI+0.4,PI+0.5+0.5*s)),((1.2*s*math.sin(u*22),0.4*s),(-1.0*s*math.sin(u*22),0.4*s)),face
def tumble(u,x,face='dead'):   # lying -> standing
    u=max(0,min(1,u)); e=smooth(u)
    return (x,lerp(905,796,e)),lerp(-1.5,0.0,e),((lerp(1.9,0.12,e),lerp(1.9,0.0,e)),(lerp(-1.6,-0.12,e),lerp(-1.6,0.0,e))),((lerp(1.5,0.1,e),lerp(1.5,0.0,e)),(lerp(1.5,-0.1,e),lerp(1.55,0.0,e))),face
def star(d,x,y,r,a):
    pts=[]
    for i in range(10): rr=r if i%2==0 else r*0.45; an=a+i*PI/5; pts.append((x+rr*math.sin(an),y-rr*math.cos(an)))
    poly(d,pts,(255,220,60),3)
def stars(d,head,T):
    for i in range(3): an=T*6+i*2*PI/3; star(d,head[0]+90*math.cos(an),head[1]-70+22*math.sin(an),20,an)
def zzz(d,head,T):
    for i in range(3): q_=((T*0.8+i/3)%1); text(d,(head[0]-40+i*18+q_*30,head[1]-70-q_*110),'Z',30+8*i+10*q_,(235,240,255))
def drawpil(d,s,look=1):
    hip,lean,arms,legs,fc=s; return stick(d,hip,lean,arms,legs,fc,look)
def comp(img,lay):
    al=lay.getchannel('A'); sh=al.resize((OW//4,OH//4)).filter(ImageFilter.GaussianBlur(3.2)).resize((OW,OH),Image.BILINEAR)
    sh=ImageChops.offset(sh,12,18).point(lambda v:int(v*0.34)); img.paste((30,20,30),(0,0),sh); img.paste(lay,(0,0),lay)
WM=Image.new('RGBA',(OW,OH),(0,0,0,0)); ImageDraw.Draw(WM).text((1000,1870),'PIFIO',font=ImageFont.truetype(FONT,28),fill=(255,255,255,60),anchor='mm')
def ca(img,px):
    if px<1: return img
    a=np.asarray(img).copy(); a[...,0]=np.roll(a[...,0],px,axis=1); a[...,2]=np.roll(a[...,2],-px,axis=1); return Image.fromarray(a)
def speedlines(d,T,t0,t1):
    if not t0<=T<t1: return
    for i in range(28):
        an=i*2*PI/28+0.13*math.sin(i*7.1); r0=330+60*math.sin(T*50+i); r1=r0+260+80*math.sin(i*3.3+T*40)
        line(d,[(360+r0*math.cos(an)*0.82,640+r0*math.sin(an)*1.15),(360+r1*math.cos(an)*0.82,640+r1*math.sin(an)*1.15)],w=5,col=(255,255,255,150))
def pop(d,T,t0,t1,s_,y,sz,col=YEL):
    if t0<=T<t1:
        e=ease((T-t0)/0.12); k=0.4+0.6*e+0.25*math.sin(e*PI)
        for dx,dy in ((-4,-4),(4,-4),(-4,4),(4,4)): d.text(sc((360+dx,y+dy+(1-e)*30)),s_,font=font(sz*k),fill=BK,anchor='mm')
        d.text(sc((360,y+(1-e)*30)),s_,font=font(sz*k),fill=col,anchor='mm')
def pill(d,x0,x1,labels):
    rect(d,x0,100,x1,198,fill=DK,out=BK,w=5,rad=44)
    for (tx,ty,s_,sz,col,anc) in labels: d.text(sc((tx,ty)),s_,font=font(sz),fill=col,anchor=anc)
def run(C):
    DURc=C.get('DUR',15.0); fr=C.get('freeze'); worldf=C['world']; ev=C.get('EV',[]); beats=C.get('beats',[]); tm=C.get('tmap',lambda T:T)
    def base(T):
        raw=Image.new('RGBA',(W*S,H*S),(0,0,0,0)); worldf(ImageDraw.Draw(raw),T)
        lay=Image.new('RGBA',(OW,OH),(0,0,0,0)); lay.paste(raw.resize((OW,OH),Image.LANCZOS),(0,int(OFF*K)))
        img=BGS.copy(); comp(img,lay); return img
    def camf(T):
        z,cx,cy=C.get('cam',lambda T:(1,360,640))(T)
        if ev: z*=1+0.10*max(dec(T,t0,9) for t0 in ev)
        for a,b in beats:
            if a<=T<b: z*=1+0.02*dec(T,(T-a)//BEAT*BEAT+a,9)
        return z,cx,cy
    def shakef(T):
        for a,b,m in C.get('shakes',[]):
            if a<=T<b: k=(1-(T-a)/(b-a)); return int(m*math.sin(T*95)*k),int(m*math.cos(T*83)*k)
        return 0,0
    def frame(T):
        Tw=tm(T)
        if fr and fr[0]<=T<fr[1]: Tw=fr[0]
        img=base(Tw)
        if C.get('pre'): img=C['pre'](img,T,base)
        ox,oy=shakef(T)
        if ox or oy: img=ImageChops.offset(img,ox,oy)
        z,cx,cy=camf(T)
        if fr and fr[0]<=T<fr[1]: u=(T-fr[0])/(fr[1]-fr[0]); z=z*(1.0+0.35*ease(u*3))
        if z>1.001:
            w,h=OW/z,OH/z; x0=min(max(cx*K-w/2,0),OW-w); y0=min(max(cy*K-h/2,0),OH-h); img=img.resize((OW,OH),Image.BICUBIC,box=(x0,y0,x0+w,y0+h))
        if C.get('post'): img=C['post'](img,T)
        cp=max([14*dec(T,t0,7) for t0 in ev]+[22 if (fr and fr[0]<=T<fr[1]+0.15) else 0]+[0]); img=ca(img,int(cp))
        if fr and fr[0]<=T<fr[0]+0.06: img=ImageChops.invert(img)
        u=Image.new('RGBA',(W*S,H*S),(0,0,0,0)); d=ImageDraw.Draw(u)
        C['hud'](d,T)
        for a,b,s_ in C['caps']:
            if a<=T<b: caption(d,s_,T-a,y=905)
        for a,b in C.get('speed',[]): speedlines(d,T,a,b)
        for p_ in C.get('pops',[]): pop(d,T,*p_)
        if C.get('ui2'): C['ui2'](d,T)
        comp(img,u.resize((OW,OH),Image.LANCZOS)); img.paste(WM,(0,0),WM)
        fl=max([0.55*dec(T,t0,22) for t0 in C.get('flash',[])]+[0])
        arr=np.asarray(img,np.float32)*VIG
        if fl>0.02: arr=arr+(255-arr)*fl
        return Image.fromarray(np.clip(arr,0,255).astype(np.uint8))
    Ts=C['Ts']; sheet=Image.new('RGB',(300*7,533*3),WH); checks={int(t*FPS):i for i,t in enumerate(Ts)}
    quick='--check' in sys.argv
    if quick:
        for n,i in checks.items(): sheet.paste(frame(n/FPS).resize((300,533)),(300*(i%7),533*(i//7)))
        sheet.save('check_%s.png'%C['name']); return
    p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{OW}x{OH}','-r',str(FPS),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','medium',C['name']+'_silent.mp4'],stdin=subprocess.PIPE)
    for n in range(int(FPS*DURc)):
        im=frame(n/FPS); p.stdin.write(im.tobytes())
        if n in checks: i=checks[n]; sheet.paste(im.resize((300,533)),(300*(i%7),533*(i//7)))
    p.stdin.close(); p.wait(); sheet.save('check_%s.png'%C['name'])
BEAT=60/128
