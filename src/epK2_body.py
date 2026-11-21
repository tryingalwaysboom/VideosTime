BGR=mkbgimg('room'); BGO=mkbgimg('street',True)
tOut=9.6
def bgfK(T): return BGR if T<tOut else BGO

def _T(x,y,s,a):
    c,sn=math.cos(a),math.sin(a)
    return lambda px,py:(x+s*(px*c-py*sn),y+s*(px*sn+py*c))
def key1(d,x,y,s,ang,col):
    Tf=_T(x,y,s,ang)
    poly(d,[Tf(-5,38),Tf(5,38),Tf(5,92),Tf(-5,92)],col,max(2,int(3.5*s)))
    poly(d,[Tf(5,70),Tf(15,70),Tf(15,79),Tf(5,79)],col,max(2,int(3*s)))
    poly(d,[Tf(5,83),Tf(13,83),Tf(13,90),Tf(5,90)],col,max(2,int(3*s)))
    bc=Tf(0,26); circ(d,bc,16*s,fill=col,w=max(2,int(4*s))); circ(d,bc,6*s,fill=(250,250,255),w=max(2,int(3*s)))
    h=Tf(-4,32); line(d,[Tf(-9,20),Tf(-3,12)],w=max(2,int(3*s)),col=(255,255,255,200))
def keybunch(d,x,y,s,a,glow=False):
    if glow:
        for k in range(10):
            an=k*PI/5+a*2; line(d,[(x+50*s*math.cos(an),y+60*s+50*s*math.sin(an)),(x+95*s*math.cos(an),y+60*s+95*s*math.sin(an))],w=4,col=(255,232,110))
    key1(d,x,y,s,a-0.55,(205,210,220)); key1(d,x,y,s,a+0.55,(205,135,65)); key1(d,x,y,s,a,(255,205,60))
    Tf=_T(x,y,s,a-1.15); poly(d,[Tf(-13,34),Tf(13,34),Tf(13,78),Tf(-13,78)],(225,60,70),max(2,int(3*s)))
    circ(d,Tf(0,44),4*s,fill=(250,250,255),w=2)
    circ(d,(x,y),12*s,fill=None,out=(140,142,155),w=max(3,int(5*s)))
def item(d,kind,x,y,a,s=1.0):
    if kind==0: rrc(d,x,y,56*s,40*s,a,(240,200,90),4); circ(d,(x,y),4*s,fill=(180,140,40),w=2)
    elif kind==1: rrc(d,x,y,46*s,34*s,a,(90,150,230),4); rrc(d,x,y+3*s,40*s,6*s,a,(250,250,250),2)
    elif kind==2:
        rrc(d,x,y,28*s,32*s,a,(240,240,245),4); ell(d,rotp((x+18*s,y),a,(x,y)),9*s,11*s,fill=None,w=4)
    elif kind==3:
        poly(d,[rotp(p,a,(x,y)) for p in ((x-10*s,y-24*s),(x+10*s,y-24*s),(x+10*s,y+4*s),(x+30*s,y+10*s),(x+30*s,y+26*s),(x-10*s,y+26*s))],(235,120,150),4)
    elif kind==4:
        rrc(d,x,y,18*s,50*s,a,(60,62,72),4)
        for i in range(3): circ(d,rotp((x,y-14*s+i*12*s),a,(x,y)),3*s,fill=(230,70,70),out=None)
    elif kind==5: sneaker(d,x,y,a,s)
    else: rrc(d,x,y,38*s,48*s,a,(250,250,250),3); [line(d,[rotp((x-12*s,y-12*s+i*10*s),a,(x,y)),rotp((x+12*s,y-12*s+i*10*s),a,(x,y))],w=2,col=(150,150,160)) for i in range(4)]
def sneaker(d,x,y,a,s=1.0):
    Tf=_T(x,y,s,a)
    poly(d,[Tf(-32,-2),Tf(-32,-30),Tf(-6,-34),Tf(10,-14),Tf(36,-4),Tf(36,8),Tf(-32,8)],(225,70,70),4)
    poly(d,[Tf(-32,6),Tf(36,6),Tf(38,16),Tf(-32,16)],(250,250,250),4)
    for i in range(3): line(d,[Tf(-4+i*7,-18+i*4),Tf(2+i*7,-22+i*4)],w=3,col=(255,255,255))
def nsites(T):
    if T<1.4: return 0
    if T<2.2: return 1
    if T<3.0: return 2
    if T<3.8: return 3
    if T<4.6: return 4
    if T<6.0: return int(lerp(5,23,(T-4.6)/1.4))
    return 23
def stK_raw(T):
    if T<1.4: return stand(380,'wtf',arms=((0.55,0.35),(-0.3+0.25*math.sin(T*18),0.25)),y=796-4*abs(math.sin(T*10)))
    if T<2.2: return stand(180,'wtf',lean=0.55,arms=((0.9,0.5),(0.6,0.7)))
    if T<3.0: return stand(500,'wtf',lean=0.3,arms=((0.3,0.2),(-0.2,0.1)))
    if T<3.8: return stand(350,'wtf',lean=0.9,arms=((0.8,0.8),(0.5,0.9)))
    if T<4.6: return stand(200,'wtf',lean=0.5,arms=((0.6,0.6),(0.4,0.8)))
    if T<6.0: return walkp(360+250*math.sin(T*7),T,'shock',amp=0.9,lean=0.2,arms=((0.9*math.sin(T*14),1.4),(-0.9*math.sin(T*14),-1.4)))
    if T<7.2: return stand(380,'dead',lean=0.3,y=796+8,arms=((0.3,0.1),(-0.2,0.1)))
    if T<8.8: return stand(380,'shock',lean=0.0,arms=((PI-0.35,PI-1.3),(-0.2,0.0)))
    if T<9.6: return walkp(380+380*smooth((T-8.8)/0.8),T,'happy',amp=0.7,lean=0.15,arms=((PI-0.4,PI-0.6),(PI+0.4,PI+0.6)))
    if T<10.6: return walkp(lerp(590,250,smooth((T-9.6)/1.0)),T,'happy',amp=0.5,lean=0.08,arms=((0.3,0.2),(-0.3,-0.2)))
    if T<11.4: return stand(250,'wtf',arms=((0.5,2.2),(-0.5,-2.2)),y=796-4*abs(math.sin(T*14)))
    if T<12.4: return stand(250,'shock',lean=0.1,arms=((PI/2+0.2,PI/2+0.2),(-0.2,0.0)))
    if T<15.0: return None
    return lying(300,'dead')

SEGB=[1.4,2.2,3.0,3.8,4.6,6.0,7.2,8.8,9.6,10.6,11.4,12.4]
def mixpose(p,q,u):
    if p is None or q is None: return q
    (h1,l1,a1,g1,f1),(h2,l2,a2,g2,f2)=p,q
    L_=lambda x,y: x+(y-x)*u
    return ((L_(h1[0],h2[0]),L_(h1[1],h2[1])),L_(l1,l2),tuple((L_(a1[i][0],a2[i][0]),L_(a1[i][1],a2[i][1])) for i in (0,1)),tuple((L_(g1[i][0],g2[i][0]),L_(g1[i][1],g2[i][1])) for i in (0,1)),f2)
def stK(T):
    cur=stK_raw(T)
    for b in SEGB:
        if b<=T<b+0.2 and b<tOut:
            prev=stK_raw(b-0.001)
            if prev is not None and cur is not None: return mixpose(prev,cur,smooth((T-b)/0.2))
    return cur
def worldK(d,T):
    if T<tOut:
        line(d,[(-20,932),(740,932)],w=6)
        # rug
        ell(d,(250,925),150,16,fill=(120,170,150),w=4)
        # sofa
        rect(d,30,740,260,860,fill=(205,85,80),w=6,rad=30)           # back
        rect(d,15,790,60,930,fill=(190,72,68),w=6,rad=20); rect(d,235,790,280,930,fill=(190,72,68),w=6,rad=20)  # arms
        lift=0
        if 1.4<=T<2.2: lift=70*math.sin(PI*(T-1.4)/0.8)
        rrc(d,170,846-lift,100,34,-0.12*(lift>0)*1.0,(228,112,104),5)   # right cushion (lifts)
        rect(d,60,846,120,884,fill=(228,112,104),w=5,rad=10)
        rect(d,55,884,235,930,fill=(215,98,92),w=6,rad=10)
        # cabinet with drawer
        rect(d,440,720,640,932,fill=(150,110,80),w=6,rad=8)
        dr=0
        if 2.2<=T<3.0: dr=70*math.sin(PI*(T-2.2)/0.8)
        rect(d,455,740,625,826,fill=(172,132,96),w=4,rad=4); rect(d,520,772,560,782,fill=(80,55,35),w=3,rad=4)
        rect(d,455,840+0,625,920,fill=(172,132,96),w=4,rad=4)
        if dr>0:
            rect(d,450-dr*0.4,760+dr*0.3,630-dr*0.4,846+dr*0.3,fill=(125,92,66),w=5,rad=4)
        # window
        rect(d,300,400,440,560,fill=(200,225,245),w=6,rad=8); line(d,[(370,400),(370,560)],w=4); line(d,[(300,480),(440,480)],w=4)
        if 9.4<=T:
            rect(d,560,640,700,652,fill=(110,80,55),w=5); keybunch(d,630,568,0.85,0.2*math.sin(T*3),glow=True)
        # search effects
        if 1.4<=T<2.2:
            u=(T-1.4)/0.8
            item(d,0,150,800-110*math.sin(PI*u),0.5*math.sin(T*9),1.0)
            item(d,4,95,820-80*math.sin(PI*min(1,u*1.2)),-0.4,0.9)
        if 2.2<=T<3.0:
            u=(T-2.2)/0.8
            for i in range(5):
                item(d,[1,6,2,3,0][i],500+(i-2)*60*u,700-120*math.sin(PI*u)*(1+i%2*0.4),u*6*(1 if i%2 else -1),0.9)
        if 3.0<=T<3.8:
            u=(T-3.0)/0.8; f=min(1,u*1.5)
            poly(d,[(90,930),(410,930),(410-40*f,915-70*f*math.sin(PI*min(1,u*1.2))),(90+40*f,915-70*f*math.sin(PI*min(1,u*1.2)))],(120,170,150),5)
            item(d,3,250,900-30*math.sin(PI*u),0.2,0.8)
        if 3.8<=T<4.6:
            u=(T-3.8)/0.8
            for i in range(3):
                item(d,5,130+i*90+60*u*(i-1),900-170*math.sin(PI*min(1,u*1.05))*(1+i%2*0.4),u*7*(1-2*(i%2)),1.0)
        if 4.6<=T<6.0:
            for i in range(14):
                u=((T-4.6)*1.6+i*0.17)%1; x=360+300*math.sin(i*1.9+u*3); y=860-480*math.sin(PI*u)
                item(d,i%7,x,y,T*8+i,0.8)
    s=stK(T)
    if T<tOut:
        hip,lean,arms,legs,fc=s; hs=hands(hip,lean,arms)
        hd=drawpil(d,s)
        if T<9.4:
            hk=hs[0]; keybunch(d,hk[0]+2,hk[1]-4,1.0,0.25*math.sin(T*9),glow=(T<1.4 or 7.2<=T<9.4))
        if 7.2<=T<8.8:
            for i in range(10):
                an=i*PI/5+T*2; line(d,[(hd[0]+80*math.cos(an),hd[1]+80*math.sin(an)),(hd[0]+130*math.cos(an),hd[1]+130*math.sin(an))],w=5,col=(255,235,120))
        if 6.0<=T<7.2:
            for i in range(3): text(d,(hd[0]-30+i*22,hd[1]-90-((T*1.5+i*0.3)%1)*30),'z',28,(90,90,120))
    else:
        # exterior
        door_open=T<10.0
        rect(d,520,520,660,932,fill=(40,30,30) if door_open else (205,165,115),w=6)
        if not door_open: circ(d,(640,740),9,fill=YEL,w=4)
        rect(d,345,560,490,760,fill=(230,236,244),w=7,rad=6)
        rect(d,355,570,480,750,fill=(222,184,140),out=None,w=0); rect(d,360,680,475,692,fill=(110,80,55),w=4)
        if T>=11.0: keybunch(d,420,598,0.8,0.15*math.sin(T*3),glow=True)
        if s is not None:
            hd=drawpil(d,s)
        if 12.4<=T<15.0:
            u=smooth((T-12.4)/0.4) if T<14.0 else 1.0
            sl=smooth((T-14.0)/1.0) if T>=14.0 else 0.0
            cx=418; cy=650+130*sl
            if sl>0: line(d,[(cx,650),(cx,cy)],w=22,col=(255,255,255,120))
            for k in range(5): circ(d,(cx-40+k*20,cy-30+8*math.sin(k)),(20+8*u),fill=(255,255,255,70),out=None)
            ell(d,(cx,cy),62*(0.6+0.4*u),52*(0.9+0.1*u),fill=(255,255,255),w=6)
            for ex in (-24,24): ell(d,(cx+ex,cy-10),12,(16 if u>0.5 else 14),fill=(255,255,255),w=4); circ(d,(cx+ex+3,cy-10),5,fill=BK,out=None)
            ell(d,(cx,cy+26),(20 if u>0.5 else 14),6,fill=BK,out=None); line(d,[(cx-34,cy-26),(cx-14,cy-36)],w=5); line(d,[(cx+34,cy-26),(cx+14,cy-36)],w=5)
            if T>=12.4+0.5:
                for k in range(4): circ(d,(cx-26+k*17,cy+44+((T*2+k*0.3)%1)*10),7,fill=(255,255,255,140),out=None)
def hudK(d,T):
    if T<tOut:
        n=nsites(T)
        pill(d,110,610,[(150,128,'SITIOS REVISADOS',20,(190,196,212),'lm'),(560,140,str(n),56,(255,255,255) if n<20 else (255,90,80),'rm'),(150,166,'¿dónde están?',20,(150,156,172),'lm')])
    else:
        pill(d,110,610,[(150,128,'LLAVES',22,(190,196,212),'lm'),(560,128,'DENTRO',44,(255,90,80),'rm'),(150,166,'puerta cerrada',20,(150,156,172),'lm')])
def camK(T):
    if 7.5<=T<8.5:
        u=ease((T-7.5)/0.3); return 1+1.2*u,380,600
    if 12.2<=T<14.0:
        u=smooth((T-12.2)/0.8); return 1+2.0*u,lerp(360,418,u),lerp(640,650,u)
    if 14.0<=T<15.2:
        u=smooth((T-14.0)/1.2); return 3.0-1.0*u,418,lerp(650,780,u)
    if T>=15.2:
        u=smooth((T-15.2)/0.8); return lerp(2.0,1.2,u),lerp(418,300,u),780
    return 1,360,640
def postK(img,T):
    if T>=16.5:
        k=max(0.0,1-(T-16.5)/0.5); return Image.fromarray((np.asarray(img,np.float32)*k).astype(np.uint8))
    return img
CK=dict(name='epK2',DUR=17.0,bgf=bgfK,world=worldK,hud=hudK,cam=camK,post=postK,beats=[(1.4,4.6)],speed=[(4.6,6.0)],
 EV=[1.4,2.2,3.0,3.8,4.6,7.2,8.8,tOut,11.0,12.4],flash=[4.6,7.5,8.8,tOut,12.4],freeze=(7.7,7.95),shakes=[(10.0,10.3,12),(11.4,12.2,6)],
 caps=[(0,1.4,'¿Dónde están mis llaves?'),(1.4,2.2,'Sofá.'),(2.2,3.0,'Cajón.'),(3.0,3.8,'Alfombra.'),(3.8,4.6,'Zapatos.'),(4.6,6.0,'23 sitios después'),(6.0,7.2,'Me rindo.'),(7.2,8.8,'…'),(8.8,tOut,'¡LAS TENGO!'),(tOut,10.6,'Hora de salir'),(10.6,11.4,'Un segundo…'),(11.4,12.4,'Puerta cerrada.'),(12.4,14.0,'Las veo…'),(14.0,15.2,'Tan cerca.'),(15.2,17.1,'Las llaves. Dentro.')],
 pops=[(1.4,1.9,'¡NADA!',470,90,RED),(4.6,5.2,'¡CAOS!',470,90,YEL),(8.8,9.4,'¡SÍÍÍ!',470,90,YEL),(10.0,10.5,'¡PAM!',470,90,(200,200,200))],
 Ts=(0.6,1.8,2.6,3.4,4.2,5.3,6.6,7.9,9.2,9.9,10.8,11.8,12.8,13.6,14.5,15.6,16.4,0.9,3.6,8.2,12.2))
run(CK)
