setbg('street')
REPLAY=False
def tmA(T):
    global REPLAY
    REPLAY=2.7<=T<4.1
    if REPLAY: return 1.7+(T-2.7)*(0.8/1.4)
    return T
def stA(T):
    if T<1.85: return walkp(lerp(60,290,T/1.85),T,'happy',0.6)
    if T<2.45: return fall((T-1.85)/0.6,290,350)
    if T<4.0: return lying(350)
    if T<4.4: return tumble((T-4.0)/0.4,350)
    if T<5.3: return walkp(lerp(350,450,(T-4.4)/0.9),T,'happy',0.6)
    if T<5.45: return stand(450,'shock')
    if T<6.1: return fall((T-5.45)/0.65,450,380)
    if T<7.2: return lying(380)
    if T<7.6: return tumble((T-7.2)/0.4,380)
    if T<8.8: return walkp(lerp(380,560,(T-7.6)/1.2),T,'run',0.3,0.15)
    if T<9.4: return fall((T-8.8)/0.6,560,600)
    if T<10.3: return lying(600)
    if T<10.7: return tumble((T-10.3)/0.4,600,'wtf')
    if T<12.3:
        x=lerp(560,500,(T-10.7)/1.6); return stand(x,'wtf',lean=-0.05)
    if T<13.05: return walkp(lerp(500,370,(T-12.3)/0.75),T,'shock',0.9,0.2)
    if T<13.6: return fall((T-13.05)/0.55,370,340)
    return None
def tipx(T):
    if T<12.9: return 640
    if T<13.2: return lerp(640,330,ease((T-12.9)/0.3))
    if T<13.6: return 330
    if T<14.3: return lerp(330,650,smooth((T-13.6)/0.7))
    return 640
def worldA(d,T):
    line(d,[(-20,932),(740,932)],w=6)
    # banana
    if T<1.85: ell(d,(300,923),26,9,fill=(250,220,60),w=4); line(d,[(280,918),(320,918)],w=3,col=(170,130,30))
    elif T<2.5:
        u=(T-1.85)/0.65; bx,by=300+70*u,925-230*math.sin(PI*u); ell(d,(bx,by),26,9,fill=(250,220,60),w=4)
    else: ell(d,(370,925),26,9,fill=(250,220,60),w=4)
    # rake
    if T<7.2:
        a=0.0 if T<5.3 else (-1.7*ease((T-5.3)/0.15) if T<5.45 else lerp(-1.7,-3.0,smooth((T-5.45)/0.75)))
        rrect(d,490,919,820,931,a,(490,925),WOOD,4); rect(d,430,915,490,931,fill=(150,154,170),w=4,rad=3)
        for k in range(5): line(d,[(436+k*13,915),(436+k*13,903)],w=4,col=(150,154,170))
    # sign
    line(d,[(520,932),(520,880)],w=6); rect(d,466,846,574,892,fill=(255,255,255),w=4,rad=4); text(d,(520,869),'SUELO LISO',17)
    # floor face
    eo=smooth((T-9.7)/0.3)
    s=stA(T); px=s[0][0] if s else 640
    if T>=9.4:
        for k in range(5):
            x0=560+30*k; line(d,[(x0,934),(x0+10,950),(x0-6,966),(x0+8,982)],w=3,col=(60,50,50))
    if eo>0:
        for ex in (600,690):
            ell(d,(ex,925-10*(1-eo)),32*eo,38*eo,fill=(255,255,255),w=5)
            off=max(-1,min(1,(px-ex)/140))*12; circ(d,(ex+off,925+4),12*eo,fill=BK,out=None)
        mo=1.0 if T<14.2 else max(0.15,1-(T-14.2)/0.08)
        ell(d,(640,968),95*eo,26*eo*mo,fill=(90,20,35),w=5)
        if mo>0.5:
            for k in range(-4,5): rect(d,640+k*18-7,945*1.0+10,640+k*18+7,958,fill=(255,255,255),w=2,rad=2)
        if 12.9<=T<14.3:
            tx=tipx(T); line(d,[(640,970),(tx,962)],w=22,col=(240,100,130)); circ(d,(tx,962),11,fill=(240,100,130),out=None)
    if s is not None and not (T>=13.6 and False):
        hd=drawpil(d,s)
        if 2.6<=T<4.0 or 6.2<=T<7.2 or 9.5<=T<10.3: stars(d,hd,T)
    if T>=13.6 and T<14.25:
        tx=tipx(T); sx=lying(tx-10,'shock'); drawpil(d,sx)
    if REPLAY and s is not None:
        fx=s[0][0]; ell(d,(fx+10,918),64+8*math.sin(T*30),34,fill=None,out=RED,w=6)
    if 14.3<=T<14.9: puff(d,640,925,(T-14.3)/0.6,8,30)
def hudA(d,T):
    n=sum(1 for t in (2.45,6.1,9.4,13.55) if T>=t); last=max([t for t in (2.45,6.1,9.4,13.55) if T>=t],default=-9); pp=1+0.5*max(0,1-(T-last)/0.25)
    pill(d,110,610,[(152,128,'CAÍDAS',26,(190,196,212),'lm'),(152,160,'HOY',22,(150,156,172),'lm'),(520,150,str(n),66*pp,(255,120,110) if n else WH,'mm')])
    if REPLAY: 
        if int(T*4)%2==0: circ(d,(150,262),11,fill=RED,out=None)
        d.text(sc((180,262)),'REPLAY ◀◀',font=font(36),fill=WH,anchor='lm')
def preA(img,T,base):
    if not REPLAY: return img
    a=np.asarray(img,np.float32); g=a.mean(axis=2,keepdims=True); sep=g*np.array([1.1,0.95,0.75],np.float32)
    sep[::6]*=0.8; return Image.fromarray(np.clip(sep,0,255).astype(np.uint8))
def camA(T):
    if REPLAY: return 1.45,330,820+OFF
    if 10.7<=T<12.3: return 1.0+0.4*ease((T-10.7)/0.5),560,860+OFF
    if 12.3<=T<12.7: return 1.4-0.4*ease((T-12.3)/0.4),560,860+OFF
    if 14.0<=T<14.8: return 1.0+0.4*ease((T-14.0)/0.3),620,880+OFF
    return 1,360,640
CA=dict(name='epA',world=worldA,hud=hudA,tmap=tmA,pre=preA,cam=camA,EV=[1.85,5.45,8.8,10.0,13.0,14.3],flash=[1.85,5.45,8.8,14.3],freeze=(10.0,10.25),
 shakes=[(1.9,2.3,14),(5.45,5.9,20),(8.9,9.3,14),(14.3,14.7,22)],speed=[(1.85,2.2),(5.45,5.8)],
 caps=[(0,1.85,'Hoy me siento genial'),(2.7,4.1,'Repetición en cámara lenta'),(4.1,5.3,'Tranquilo. Ya pasó'),(6.1,7.6,'Vale. Dos caídas'),(7.6,8.8,'Ahora voy con cuidado'),(9.4,10.0,'¿Qué…?'),(10.3,12.3,'El suelo me tiene manía'),(12.3,13.0,'¡Corre!'),(14.5,15.1,'El suelo gana')],
 pops=[(1.95,2.6,'¡PLAF!',330,86,YEL),(5.45,6.1,'¡BONK!',330,100,RED),(8.9,9.5,'¡PAM!',330,86,YEL),(13.2,13.8,'¡AAAH!',330,86,RED),(14.3,14.9,'¡ÑAM!',420,110,RED)],
 Ts=(0.3,1.2,2.0,2.4,3.0,3.8,4.2,5.0,5.4,5.8,6.6,8.2,9.0,9.8,10.1,10.9,11.8,12.6,13.3,13.9,14.5))
run(CA)
