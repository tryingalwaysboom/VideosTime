setbg('room',(0.42,0.46,0.78))
FX=230; MX=430
KEYS=[(0,12),(1.0,26),(1.4,38),(1.8,40),(1.95,58),(2.4,36),(3.0,38),(3.4,48),(3.6,44),(5.8,46),(6.0,40),(7.0,30),(7.8,55),(8.4,64),(8.9,70),(9.0,82),(9.3,100),(10.6,108),(11.2,60),(11.6,18),(13.9,18),(14.0,140),(14.6,120),(17.0,100)]
def noiseN(T):
    for i in range(len(KEYS)-1):
        a,b=KEYS[i],KEYS[i+1]
        if a[0]<=T<b[0]: return int(lerp(a[1],b[1],(T-a[0])/(b[0]-a[0])))
    return KEYS[-1][1]
def beeping(T): return 9.3<=T<11.2 and int((T-9.3)/0.25)%2==0
def stN(T):
    lips=((PI-0.3,PI-1.4),(0.3,0.2))
    if T<1.4: return walkp(lerp(60,FX,smooth(T/1.4)),T,'wtf',amp=0.25,lean=0.15,arms=lips)
    if T<1.8: return stand(FX,'shock',lean=0.1,arms=((0.9,1.6),(0.7,1.5)))
    if T<2.5: return stand(FX+14*smooth((T-1.8)/0.3),'wtf',lean=0.1+0.4*smooth((T-1.8)/0.2),y=796+10*smooth((T-1.8)/0.2),arms=((1.3,1.65),(1.1,1.6)))
    if T<3.0: return stand(FX+14,'happy',lean=0.1,arms=((0.9,1.6),(0.7,1.5)))
    if T<3.9: return walkp(lerp(FX+14,MX,smooth((T-3.0)/0.9)),T,'wtf',amp=0.25,lean=0.1,arms=((1.0,1.5),(0.9,1.4)))
    if T<4.6: return stand(MX,'wtf',lean=0.12,arms=((1.25,1.6),(1.1,1.5)))
    if T<7.4: return stand(MX+1.5*math.sin(T*35),'wtf' if T<6.6 else 'shock',lean=0.14,y=796-3*abs(math.sin(T*25)),arms=((1.25,1.6),(1.1,1.5)))
    if T<7.9: return stand(MX,'happy',y=796-18*abs(math.sin((T-7.4)*12)),arms=((PI-0.4,PI-0.6),(PI+0.4,PI+0.6)))
    if T<9.0: return stand(MX+2*math.sin(T*40),'shock',lean=0.1,y=796-8*abs(math.sin(T*22)),arms=((1.2,1.6+0.2*math.sin(T*30)),(1.1,1.6-0.2*math.sin(T*30))))
    if T<9.9: return stand(MX+10*math.sin(T*30),'shock',lean=0.32,arms=((1.4,1.7),(1.25,1.65)))
    return lying(560,'shock',y=588+3*math.sin(T*60))
def plate(d,x,y,hot=False):
    ell(d,(x,y),34,9,fill=(250,250,252),w=4); ell(d,(x,y-4),22,5,fill=(240,170,60),out=None,w=0)
def worldN(d,T):
    rect(d,-40,200,760,1000,fill=(6,8,34,110),out=None,w=0)
    line(d,[(-20,932),(740,932)],w=6)
    # clock
    rect(d,320,300,420,346,fill=(20,24,36),w=5,rad=6); text(d,(370,323),'03:00',24,(255,70,60))
    # hallway door
    lit=T>=11.2
    rect(d,290,480,410,932,fill=(255,236,180) if lit else (14,14,34),w=6)
    # fridge
    op=1.4<=T<3.0
    rect(d,20,350,210,932,fill=(205,215,228),w=7,rad=10); line(d,[(20,500),(210,500)],w=5)
    rect(d,190,600,200,700,fill=(130,134,150),w=3,rad=3)
    if op:
        poly(d,[(210,350),(265,372),(265,915),(210,932)],(190,200,214),6)
        poly(d,[(30,360),(205,360),(205,925),(30,925)],(250,252,255),4)
        for yy in (470,600,730): line(d,[(30,yy),(205,yy)],w=4,col=(170,180,195))
        for i,c in enumerate([(235,90,90),(245,200,80),(120,210,120)]): rect(d,50+i*45,640,78+i*45,730,fill=c,w=3,rad=3)
        rect(d,150,520,176,600,fill=(90,170,235),w=3,rad=4) if not (1.8<=T<3.0) else None
        poly(d,[(215,360),(215,925),(560,932),(560,820)],(255,250,215,70),0)
    # bottle falling gag
    if 1.8<=T<2.5:
        u=(T-1.8)/0.7; bx_=163+u*60; by_=560+u*u*330; ang=u*5.0
        rrc(d,bx_,by_,26,80,ang,(90,170,235),4)
        if 1.95<=T<2.5: rrc(d,bx_,by_,26,80,ang,(90,170,235),4)
    if 2.5<=T<3.0: rrc(d,FX+80,720,26,80,0.9,(90,170,235),4)
    # counter + microwave
    rect(d,430,780,740,932,fill=(150,110,80),w=6,rad=4); rect(d,430,770,740,790,fill=(190,150,110),w=5)
    mo=(7.9<=T<9.3)
    rect(d,470,620,690,772,fill=(215,218,226),w=6,rad=8)
    if mo: poly(d,[(485,635),(485,765),(420,790),(420,615)],(190,194,206),5)
    else: rect(d,485,635,610,765,fill=(40,46,60),w=5,rad=4)
    rect(d,620,635,680,765,fill=(180,184,196),w=4,rad=4)
    run_=(3.9<=T<7.4); disp='00:00'
    sec=0
    if T<4.6: disp='00:05' if T>=3.9 else '00:00'
    elif T<7.4:
        k=min(4,int((T-4.6)/0.55)); disp='00:0%d'%(4-k) if k<4 else '00:01'
        if k>=4: disp='00:01'
    else: disp='00:01' if T<9.3 else '--:--'
    on=(T>=3.9)
    if on and not beeping(T): text(d,(650,650),disp,17,(120,255,150))
    if beeping(T): text(d,(650,650),'END',17,(255,70,60))
    if not mo and T>=3.9 and T<9.3 or (T>=3.0 and not mo):
        rect(d,490,640,606,760,fill=(255,230,150,200) if (4.6<=T<7.4) else (40,46,60,0),out=None,w=0) if 4.6<=T<7.4 else None
        if 3.2<=T<9.3: plate(d,548,742)
    if 4.6<=T<7.4:
        for i in range(3):
            q=((T*2+i/3)%1); circ(d,(548+(i-1)*24,730-q*70),6,fill=(255,255,255,120),out=None)
    # plate after
    if 9.0<=T<9.9: plate(d,520,770+0)
    if 9.9<=T and T<11.2: plate(d,520,768)
    # light cone fridge
    # Wal
    s=stN(T); hd=drawpil(d,s)
    hip,lean,arms,legs,fc=s; hs=hands(hip,lean,arms)
    if 7.9<=T<9.0:
        ph=int(T*8)%2; plate(d,hs[ph][0]+6,hs[ph][1]+2)
        for i in range(4):
            q=((T*3+i/4)%1); circ(d,(hs[0][0]+(i-1.5)*14,hs[0][1]-q*50),9,fill=(255,255,255,140),out=None)
        circ(d,(hd[0]-14,hd[1]+18),16,fill=(255,90,90,170),out=None); circ(d,(hd[0]+26,hd[1]+18),16,fill=(255,90,90,170),out=None)
        for i in range(3): line(d,[(hd[0]+36+i*14,hd[1]-60-i*8),(hd[0]+42+i*14,hd[1]-76-i*8)],w=4,col=(230,40,50))
        for i in range(5):
            q=((T*3+i/5)%1); ell(d,(hd[0]-40-i*10,hd[1]-10-q*30+q*q*60),6,10,fill=(120,200,255),w=2)
    if 1.4<=T<3.0 and False: pass
    if 4.6<=T<7.4:
        for i in range(4):
            q=((T*3+i/4)%1); ell(d,(hd[0]-30-i*9,hd[1]-10-q*30+q*q*60),6,10,fill=(120,200,255),w=2)
    if 9.3<=T<11.2:
        for r_ in range(3):
            rr=((T*300+r_*80)%240)+30
            circ(d,(580,700),rr,fill=None,out=(255,255,255,140) if int(rr)%2 else (255,90,80,140),w=5)
        for i in range(5): line(d,[(hd[0]-30+i*16,hd[1]-60),(hd[0]-26+i*16,hd[1]-44)],w=4,col=(230,40,50))
    if T>=11.6:
        e=min(1,(T-11.6)/0.4)
        for ex in (-12,24): ell(d,(hd[0]+ex,hd[1]-4),22+14*e,26+14*e,fill=(255,255,255),w=5); circ(d,(hd[0]+ex+4,hd[1]-4),5,fill=BK,out=None)
    # light cone from hall + mom
    if T>=11.2:
        poly(d,[(410,640),(410,932),(740,932),(740,860)],(255,240,170,110),0)
    if T>=11.2:
        # long shadow on floor
        sl=min(1,(T-11.2)/0.6)
        poly(d,[(300,925),(300+420*sl,935),(300+420*sl,915)],(20,20,40),4) if False else None
    if T>=11.6:
        e=smooth((T-11.6)/0.5)
        mx_=350
        rect(d,mx_-80,640,mx_+80,932,fill=(25,20,40),w=6,rad=30)
        circ(d,(mx_,590),74,fill=(25,20,40),w=6)
        for i in range(5): circ(d,(mx_-50+i*25,528+4*abs(i-2)),18,fill=(60,50,90),w=4)
        for ex in (-26,26): ell(d,(mx_+ex,588),14,7,fill=(255,255,255),out=None,w=0)
        for ex in (-1,1): line(d,[(mx_+ex*44,556),(mx_+ex*12,574)],w=8,col=(255,255,255))
        # arm with slipper raised
        up=1.0 if T<13.2 else 1.0
        line(d,[(mx_+70,700),(mx_+110,610),(mx_+80,520)],w=26,col=(25,20,40))
        sl_=(mx_+80,500)
        ell(d,(sl_[0],sl_[1]),42,20,fill=(255,150,190),w=5); ell(d,(sl_[0]+6,sl_[1]-8),24,10,fill=(255,200,225),w=3)
    if 13.0<=T<14.0:
        u=smooth((T-13.0)/1.0)
        for i in range(10): line(d,[(300+i*20,640),(300+i*20-8,640-30*u)],w=3,col=(255,90,80))
def hudN(d,T):
    n=noiseN(T)
    col=(120,255,140) if n<40 else ((255,210,60) if n<80 else (255,90,80))
    lab='RUIDO' if T<11.6 or T>=14.0 else 'SILENCIO'
    pill(d,110,610,[(150,128,lab,22,(190,196,212),'lm'),(560,140,(str(n)+' dB') if lab=='RUIDO' else 'TOTAL',44,col,'rm')])
    rect(d,150,160,570,176,fill=(50,54,66),out=None,w=0,rad=8)
    rect(d,150,160,150+max(6,int(420*min(1,n/140))),176,fill=col,out=None,w=0,rad=8)
    if 13.7<=T<14.0:
        u=(T-13.7)/0.3; k=lerp(0.15,1.0,u*u); cx=lerp(430,360,u); cy=lerp(520,640,u)
        ell(d,(cx,cy),190*k,110*k,fill=(255,150,190),w=max(3,int(8*k))); ell(d,(cx+20*k,cy-30*k),110*k,50*k,fill=(255,200,225),w=max(2,int(5*k)))
    if T>=14.0:
        u=min(1,(T-14.0)/2.5); cy=640+90*u
        rr=np.random.default_rng(5)
        for i in range(22):
            an=i*2*PI/22+0.1; pts=[(360,640)]; r_=0
            for sgm in range(6):
                r_+=60+30*rr.random(); a2=an+(rr.random()-0.5)*0.3
                pts.append((360+r_*math.cos(a2),640+r_*math.sin(a2)))
            line(d,pts,w=4,col=(255,255,255)); line(d,pts,w=1,col=(30,30,40))
        ell(d,(360,cy),190,110,fill=(255,150,190),w=9); ell(d,(380,cy-30),110,50,fill=(255,200,225),w=5)
        for i in range(6): ell(d,(360-150+i*60,cy+60),22,14,fill=(255,185,215),w=3)
def camN(T):
    if T<1.4: return 1.1,lerp(200,300,T/1.4),700
    if 1.4<=T<3.0:
        u=smooth((T-1.4)/0.5); z=lerp(1.1,1.5,u) if T<2.6 else lerp(1.5,1.1,smooth((T-2.6)/0.4)); return z,230,640
    if 3.0<=T<4.6: return 1.1,lerp(300,470,smooth((T-3.0)/1.2)),700
    if 4.6<=T<5.4: u=smooth((T-4.6)/0.5); return lerp(1.1,2.1,u),lerp(470,570,u),680
    if 5.4<=T<7.4: return 2.1,570,680
    if 7.4<=T<9.0: u=smooth((T-7.4)/0.4); return lerp(2.1,1.7,u),lerp(570,480,u),lerp(680,700,u)
    if 9.0<=T<11.6: u=smooth((T-9.0)/0.5); return lerp(1.7,1.2,u),lerp(480,480,u),lerp(700,700,u)
    if 11.6<=T<14.0: u=smooth((T-11.6)/2.0); return lerp(1.2,1.9,u),lerp(480,420,u),lerp(700,640,u)
    return 1.0,360,640
def postN(img,T):
    if T>=16.5:
        k=max(0.0,1-(T-16.5)/0.5); return Image.fromarray((np.asarray(img,np.float32)*k).astype(np.uint8))
    return img
CN=dict(name='epN',DUR=17.0,beats=[],world=worldN,hud=hudN,cam=camN,post=postN,
 EV=[1.4,1.95,3.0,3.9,4.6,7.4,7.9,9.0,9.3,11.2,11.6,14.0],flash=[1.95,7.9,9.3,11.2,14.0],freeze=[(1.95,2.2),(14.0,14.45)],speed=[(12.9,14.0)],shakes=[(7.9,9.0,5),(9.3,11.2,6),(14.0,14.5,18)],
 caps=[(0,1.4,'3:00 AM. Hambre.'),(1.4,3.0,'Nevera… sin ruido'),(3.0,4.6,'Solo 5 segundos'),(4.6,7.4,'5… 4… 3… 2…'),(7.4,7.9,'¡Para en 1!'),(7.9,9.0,'Quema. No grites.'),(9.0,11.2,'¡Cállate, microondas!'),(11.2,12.4,'…'),(12.4,14.0,'Mamá.'),(14.0,17.1,'Sin hacer ruido, decía.')],
 pops=[(1.95,2.45,'¡¡CASI!!',470,90,RED),(7.4,7.9,'¡SÍÍ!',470,90,YEL),(9.3,9.8,'¡BIP BIP!',470,90,RED),(12.45,13.3,'¡¿AQUÍ ESTÁS?!',470,70,RED),(14.45,15.1,'¡¡PLAF!!',470,110,YEL)],
 Ts=(0.6,1.7,2.1,2.8,3.6,4.4,5.0,6.2,7.1,7.6,8.4,9.2,9.9,10.8,11.4,12.0,12.8,13.6,13.9,14.1,15.5))
run(CN)
