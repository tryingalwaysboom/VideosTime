setbg('room',(1.0,0.97,0.92))
tVer=7.0; tAge=8.4; tSk=12.4; tOk=13.4; tExp=14.4
def attempt(T):
    # returns (k, u) attempt index and progress
    if T<1.2: return 0,0.0
    if T<5.0:
        k=int((T-1.2)/0.95); return k+1,((T-1.2)-k*0.95)/0.95
    if T<tVer:
        k=int((T-5.0)/0.2); return 5+k,((T-5.0)-k*0.2)/0.2
    return 99,0.0
def nint(T):
    if T<1.2: return 0
    k,u=attempt(T)
    if T<tVer: return k-1+(1 if u>0.7 else 0) if T<5.0 else int(lerp(4,47,(T-5.0)/(tVer-5.0)))
    return 47
def years(T):
    if T<tAge: return 0
    if T<tSk: return int(lerp(0,60,(T-tAge)/(tSk-tAge)))
    return 60
PROMPTS=['semáforos','autobuses','bicicletas','escaleras','pasos de cebra','motos','puentes']
def stC(T):
    if T<1.2: return stand(190,'happy',arms=((1.35+0.1*math.sin(T*20),1.5),(1.25,1.4)))
    if T<2.1: return stand(190,'happy',lean=0.06,arms=((1.4,1.5),(1.3,1.5+0.2*math.sin(T*14))))
    if T<3.0: return stand(170,'shock',lean=-0.15,y=796-6*abs(math.sin(T*12)),arms=((PI-0.7,PI-0.4),(PI-0.6,PI-0.3)))
    if T<3.5: return stand(190,'wtf',lean=0.12,arms=((1.4,1.5),(1.3,1.5+0.2*math.sin(T*14))))
    if T<3.8: return stand(180,'wtf',lean=-0.25,arms=((PI-0.2,PI-0.3),(PI-0.3,PI-0.2)))
    if T<4.1: return stand(200,'wtf',lean=0.35,y=796+14,arms=((2.3,2.6),(2.1,2.5)))
    if T<5.0: return stand(170+5*math.sin(T*30),'wtf',lean=-0.2,y=796-5*abs(math.sin(T*20)),arms=((PI-0.35,PI-1.9),(PI-0.45,PI-1.8)))
    if T<tVer: return stand(200+3*math.sin(T*40),'shock',lean=0.2,y=796-6*abs(math.sin(T*30)),arms=((1.4+0.25*math.sin(T*45),1.5),(1.3-0.25*math.sin(T*45),1.5)))
    if T<tAge: return stand(200,'shock',lean=0.15+0.01*math.sin(T*60),arms=((1.4,1.5),(1.3,1.45)))
    a=(T-tAge)/(tSk-tAge)
    if T<tSk: return stand(200,'dead' if a>0.5 else 'shock',lean=0.15+0.5*a,y=796+25*a,arms=((1.4+0.3*a,1.5),(1.3+0.3*a,1.45)))
    return None
def skeleton(d,T,jaw=0.0):
    sh=0 if T<tSk+0.0 else 0
    hip=(190,800); sk=(300,735)
    for col,w in ((BK,14),((250,250,250),7)):
        line(d,[hip,(235,775),sk],w=w,col=col)
        for i in range(4):
            y=790-i*14; xx=200+i*20
            line(d,[(xx-16,y),(xx+22,y-8)],w=w-1,col=col)
        line(d,[(235,770),(330,805)],w=w,col=col); line(d,[(250,775),(345,810)],w=w,col=col)
        line(d,[hip,(170,932)],w=w,col=col); line(d,[hip,(215,932)],w=w,col=col); line(d,[(170,932),(150,932)],w=w,col=col); line(d,[(215,932),(238,932)],w=w,col=col)
    circ(d,(190,800),12,fill=(250,250,250),w=4)
    circ(d,sk,36,fill=(250,250,250),w=5)
    ell(d,(sk[0]+26,sk[1]+22+jaw),16,8+jaw*0.4,fill=(250,250,250),w=4)
    circ(d,(sk[0]-8,sk[1]-4),9,fill=BK,out=None); circ(d,(sk[0]+14,sk[1]-4),9,fill=BK,out=None)
    poly(d,[(sk[0]+4,sk[1]+8),(sk[0]+10,sk[1]+8),(sk[0]+7,sk[1]+15)],BK,2)
def screen(d,T):
    X0,Y0,X1,Y1=380,520,690,770
    rect(d,X0-10,Y0-10,X1+10,Y1+10,fill=(40,44,56),w=6,rad=10)
    rect(d,X0,Y0,X1,Y1,fill=(250,250,252),out=None,w=0)
    rect(d,515,775,555,800,fill=(90,94,106),w=4); rect(d,480,796,590,806,fill=(90,94,106),w=4,rad=4)
    if T<tVer:
        k,u=attempt(T)
        rect(d,X0,Y0,X1,Y0+36,fill=(60,120,230),out=None,w=0)
        text(d,(535,Y0+10),'Selecciona todos los',13,(255,255,255)); text(d,(535,Y0+26),PROMPTS[k%7].upper() if k else 'SEMÁFOROS',17,(255,255,255))
        rng_=np.random.default_rng(k*7+1)
        sel=rng_.integers(0,2,9) if k else np.zeros(9,int)
        for i in range(9):
            cx=X0+22+(i%3)*(88); cy=Y0+48+(i//3)*58
            on=(sel[i] and u>0.08+i*0.06) if k else False
            rect(d,cx,cy,cx+84,cy+54,fill=(206,214,226) if not on else (150,190,250),w=3 if on else 2,rad=4)
            circ(d,(cx+42,cy+26),9,fill=(240,200,60) if i%3==0 else ((90,200,120) if i%3==1 else (230,90,90)),w=2)
        if u>0.7 and k:
            rect(d,X0,Y1-34,X1,Y1,fill=(230,60,60),out=None,w=0); text(d,(535,Y1-17),'✖ Inténtalo de nuevo',20,(255,255,255))
        else:
            rect(d,X1-110,Y1-32,X1-10,Y1-6,fill=(60,120,230),w=3,rad=6); text(d,(X1-60,Y1-19),'VERIFICAR',14,(255,255,255))
    elif T<tOk:
        rect(d,X0,Y0,X1,Y1,fill=(245,246,250),out=None,w=0)
        a=T*8; 
        for i in range(8):
            an=a+i*PI/4; circ(d,(535+48*math.cos(an),640+48*math.sin(an)),9-i*0.8 if 9-i*0.8>1 else 1,fill=(60,120,230),out=None)
        text(d,(535,720),'Verificando…',26,(60,70,90))
    elif T<tExp:
        rect(d,X0,Y0,X1,Y1,fill=(225,248,232),out=None,w=0)
        circ(d,(535,630),56,fill=(60,190,110),w=6); line(d,[(510,630),(528,652),(565,606)],w=12,col=(255,255,255))
        text(d,(535,715),'✔ Verificado',30,(30,120,70))
    else:
        rect(d,X0,Y0,X1,Y1,fill=(252,230,230),out=None,w=0)
        text(d,(535,610),'Tu sesión ha',30,(170,30,40)); text(d,(535,650),'caducado',38,(170,30,40))
        rect(d,455,690,615,735,fill=(60,120,230),w=4,rad=8); text(d,(535,712),'Iniciar sesión',20,(255,255,255))
def worldC(d,T):
    line(d,[(-20,932),(740,932)],w=6)
    wd=(T>=tAge and T<tSk and int(T*4)%2==1)
    rect(d,40,400,200,560,fill=(40,50,90) if wd else (200,225,245),w=6,rad=8)
    if wd: circ(d,(120,470),22,fill=(240,240,200),w=3)
    else: circ(d,(150,450),22,fill=(255,220,90),w=3)
    ds=0
    if 3.8<=T<4.0: ds=-10*math.sin(PI*(T-3.8)/0.2)
    rect(d,300,810+ds,720,826+ds,fill=(150,110,80),w=6,rad=4); rect(d,320,826,336,932,fill=(130,95,68),w=5); rect(d,684,826,700,932,fill=(130,95,68),w=5)
    ph=0
    s=stC(T)
    if T<tSk:
        hip,lean,arms,legs,fc=s; hs=hands(hip,lean,arms)
        hd=drawpil(d,s)
        # beard & gray
        if T>=tAge:
            a=min(1,(T-tAge)/(tSk-tAge))
            poly(d,[(hd[0]-26,hd[1]+14),(hd[0]+26,hd[1]+14),(hd[0]+4,hd[1]+14+110*a)],(225,225,230),4)
            for i in range(5): line(d,[(hd[0]-14+i*8,hd[1]-34),(hd[0]-14+i*8,hd[1]-52-4*a)],w=4,col=(190,190,200))
        # rage
        if 3.5<=T<5.0 or 5.0<=T<tVer:
            for i in range(3):
                q=((T*2+i/3)%1); circ(d,(hd[0]+40+i*18,hd[1]-60-q*70),12+q*10,fill=(235,235,240,160),out=None)
            line(d,[(hd[0]-6,hd[1]-60),(hd[0]+4,hd[1]-48)],w=5,col=(230,40,50)); line(d,[(hd[0]+4,hd[1]-60),(hd[0]-6,hd[1]-48)],w=5,col=(230,40,50))
        if 5.0<=T<tAge:
            for i in range(4):
                q=((T*3+i/4)%1); ell(d,(hd[0]-40-i*12,hd[1]-10-q*30+q*q*60),6,10,fill=(120,200,255),w=2)
        if 2.1<=T<3.0:
            ell(d,(hd[0]-14,hd[1]-4),12+6*math.sin(T*30),16+6*math.sin(T*30),fill=(255,255,255),w=3); circ(d,(hd[0]-14,hd[1]-4),4,fill=BK,out=None)
        if T>=tAge:
            for i in range(10):
                x=60+((i*97+T*40)%640); y=850+(i*37)%70; circ(d,(x,y),3,fill=(190,190,190),out=None)
            c=min(1,(T-tAge)/3.0)
            line(d,[(300,810),(300+60*c,810-80*c)],w=2,col=(200,200,205)); line(d,[(300,810),(300+90*c,810-30*c)],w=2,col=(200,200,205)); line(d,[(300,810),(300+30*c,810-110*c)],w=2,col=(200,200,205))
    else:
        jw=0 if T<tExp+0.2 else min(26,(T-tExp-0.2)*80)
        skeleton(d,T,jw)
        c=1
        for pts in (((300,810),(360,730)),((300,810),(390,780)),((300,810),(330,700)),((720,520),(660,560)),((720,520),(700,610))):
            line(d,list(pts),w=2,col=(200,200,205))
        for i in range(10):
            x=60+((i*97+T*20)%640); y=850+(i*37)%70; circ(d,(x,y),3,fill=(190,190,190),out=None)
    screen(d,T)
def hudC(d,T):
    if T<tAge:
        n=nint(T)
        pill(d,110,610,[(150,128,'INTENTOS',20,(190,196,212),'lm'),(560,140,str(n),56,(255,255,255) if n<20 else (255,90,80),'rm'),(150,166,'¿eres un robot?',20,(150,156,172),'lm')])
    else:
        y=years(T)
        pill(d,110,610,[(150,128,'AÑOS',22,(190,196,212),'lm'),(560,140,str(y),56,(255,200,60),'rm'),(150,166,'verificando…',20,(150,156,172),'lm')])
def camC(T):
    if 1.2<=T<5.0:
        u=smooth(min(1,(T-1.2)/0.4)); return lerp(1,1.12,u),lerp(360,370,u),lerp(640,690,u)
    if 5.0<=T<tVer:
        u=smooth((T-5.0)/2.0); return 1.12+0.18*u,lerp(370,400,u),690
    if tVer<=T<tAge:
        u=smooth((T-tVer)/1.2); return 1.3+0.7*u,lerp(400,520,u),lerp(690,650,u)
    if tAge<=T<tAge+0.5:
        u=smooth((T-tAge)/0.5); return lerp(2.0,1.0,u),lerp(520,360,u),lerp(650,700,u)
    if tOk<=T<tExp:
        u=smooth((T-tOk)/0.4); return lerp(1.0,2.2,u),lerp(360,535,u),lerp(700,650,u)
    if tExp<=T<tExp+0.6:
        u=ease((T-tExp)/0.3) if T<tExp+0.3 else 1; return 2.2+0.6*u,535,650
    if T>=tExp+0.6:
        u=smooth((T-tExp-0.6)/1.2); return lerp(2.8,1.15,u),lerp(535,400,u),lerp(650,700,u)
    return 1,360,640
def postC(img,T):
    if T>=16.5:
        k=max(0.0,1-(T-16.5)/0.5); return Image.fromarray((np.asarray(img,np.float32)*k).astype(np.uint8))
    return img
CC=dict(name='epC',DUR=17.0,beats=[(1.2,5.0)],speed=[(5.0,tVer)],world=worldC,hud=hudC,cam=camC,post=postC,
 EV=[1.2,2.1,3.0,3.8,5.0,tVer,tAge,tSk,tOk,tExp],flash=[3.8,5.0,tVer,tAge,tSk,tOk,tExp],freeze=(tOk+0.0,tOk+0.2),shakes=[(3.8,4.1,12),(tExp,tExp+0.4,14)],
 caps=[(0,1.2,'Solo quiero entrar'),(1.2,2.1,'Semáforos'),(2.1,3.0,'¿Cómo que no?'),(3.0,3.8,'¿La esquina cuenta?'),(3.8,5.0,'¡Son semáforos!'),(5.0,tVer,'Intento 47'),(tVer,tAge,'Verificando…'),(tAge,tSk,'Sigue verificando…'),(tSk,tOk,'…'),(tOk,tExp,'¡Verificado!'),(tExp,17.1,'Sesión caducada.')],
 pops=[(2.1,2.6,'¿¿QUÉ??',470,90,RED),(3.8,4.3,'¡¡ARGH!!',470,90,YEL)],
 Ts=(0.6,1.8,2.5,3.4,3.9,4.6,5.8,6.6,7.7,9.0,10.5,11.8,12.9,13.8,14.8,16.0,16.7,1.9,3.7,8.5,14.5))
run(CC)
