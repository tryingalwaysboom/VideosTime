setbg('street',(0.97,1.0,1.08))
WX=300
PK=[(0,100),(1.4,100),(1.6,85),(3,80),(4,60),(6,50),(7,35),(9,10),(9.5,0),(10.5,0),(10.6,100),(11.5,100),(12.0,60),(13.2,10),(14.0,0),(17,0)]
def pat(T):
    for i in range(len(PK)-1):
        a,b=PK[i],PK[i+1]
        if a[0]<=T<b[0]: return int(lerp(a[1],b[1],(T-a[0])/(b[0]-a[0])))
    return PK[-1][1]
def stE(T):
    A0=((0.25,0.1),(0.2,0.1))
    if T<1.4: return walkp(lerp(60,WX,smooth(T/1.4)),T,'happy',amp=0.25,lean=0.05,arms=A0)
    if T<1.8: return stand(WX,'happy',arms=((1.3,1.9),(1.1,1.8)))
    if T<3.0: return stand(WX,'shock',lean=-0.05,y=796-10*abs(math.sin((T-1.8)*9))*(1 if T<2.4 else 0),arms=((1.5,2.0),(1.3,1.9)))
    if T<6.0:
        s=math.sin(T*7); return stand(WX+3*s,'wtf',lean=0.1+0.05*s,arms=((1.3+0.4*s,1.8),(1.2-0.4*s,1.7)))
    if T<9.0:
        return stand(WX+5*math.sin(T*38),'shock',lean=0.2,y=796-4*abs(math.sin(T*20)),arms=((1.4+0.3*math.sin(T*30),1.9),(1.3-0.3*math.sin(T*30),1.8)))
    if T<10.5:
        return stand(WX+6*math.sin(T*25),'shock',lean=0.1,y=796-30*abs(math.sin((T-9.0)*7)),arms=((PI-0.6+0.8*math.sin(T*18),PI-0.3),(PI+0.6-0.8*math.sin(T*18),PI+0.3)))
    if T<11.0: return stand(WX,'happy',y=796-40*abs(math.sin((T-10.5)*6.3)),arms=((PI-0.3,PI-0.5),(PI+0.3,PI+0.5)))
    if T<12.0: return stand(WX,'wtf',lean=0.05,arms=((1.35,1.7),(1.2,1.6)))
    if T<13.3: return stand(WX,'dead',lean=0.0,arms=((1.35,1.7),(1.2,1.6)))
    if T<14.0: return stand(WX,'shock',lean=0.15+0.2*smooth((T-13.3)/0.7),arms=((0.4,0.3),(0.3,0.2)))
    u=smooth(min(1,(T-14.0)/0.5)); return stand(WX+12*u,'shock',lean=0.5*u,y=796+50*u,arms=((PI-0.2,PI-0.3),(PI+0.3,PI+0.4)))
def knot(d,c,r,seed=3,col=(30,30,36)):
    rr=np.random.default_rng(seed)
    for i in range(int(8+r/4)):
        pts=[]; a=rr.random()*6.28
        for k in range(7):
            a+=0.9+rr.random(); rad=r*(0.35+0.65*rr.random()); pts.append((c[0]+rad*math.cos(a),c[1]+rad*math.sin(a)*0.85))
        line(d,pts,w=4,col=col)
def phone(d,x,y,w=40,h=70):
    rect(d,x-w/2,y-h/2,x+w/2,y+h/2,fill=(40,46,60),w=4,rad=8); rect(d,x-w/2+5,y-h/2+7,x+w/2-5,y+h/2-7,fill=(120,190,255),out=None,w=0,rad=4)
def worldE(d,T):
    line(d,[(-20,932),(740,932)],w=6)
    s=stE(T); hd=drawpil(d,s); hip,lean,arms,legs,fc=s; hs=hands(hip,lean,arms)
    if 1.4<=T<10.6:
        # knot grows with attempts
        r=lerp(22,70,smooth(min(1,(T-1.6)/7.4))) if T>=1.6 else 18
        if T<1.8: c=(hs[0][0]+8,hs[0][1]-4)
        else: c=((hs[0][0]+hs[1][0])/2+6,(hs[0][1]+hs[1][1])/2-4)
        knot(d,c,r,seed=3)
        # dangling cables + earbuds
        sw=math.sin(T*9)*(8 if 3<=T<9.5 else 3)
        for sgn in (-1,1):
            pts=[(c[0]+sgn*r*0.5,c[1]+r*0.5)]
            for k in range(1,7): pts.append((c[0]+sgn*(r*0.5+k*8)+sw*k*0.4,c[1]+r*0.5+k*18))
            line(d,pts,w=4,col=(30,30,36)); circ(d,pts[-1],9,fill=(250,250,252),w=3)
        if 9.0<=T<10.6:
            for i in range(4):
                a=T*14+i*1.6; line(d,[(hip[0]+100*math.cos(a)*0.5,hip[1]-60+i*35),(hip[0]-100*math.cos(a)*0.5,hip[1]-50+i*35)],w=5,col=(30,30,36))
    if 3.0<=T<9.5:
        for i in range(3):
            q=((T*3+i/3)%1); ell(d,(hd[0]-34-i*8,hd[1]-10-q*30+q*q*60),6,10,fill=(120,200,255),w=2)
    if 6.0<=T<9.5:
        for i in range(4): line(d,[(hd[0]+36+i*14,hd[1]-60-i*8),(hd[0]+42+i*14,hd[1]-76-i*8)],w=4,col=(230,40,50))
    if 10.6<=T<12.5:
        e=(hs[0][0]+8,hs[0][1]-4)
        phone(d,hs[1][0]+16,hs[1][1]-6)
        line(d,[(hs[0][0],hs[0][1]),(hs[1][0]+16,hs[1][1]+30)],w=4,col=(30,30,36)); circ(d,(hs[1][0]+16,hs[1][1]+30),7,fill=(250,250,252),w=3)
    if 13.3<=T<14.0:
        u=(T-13.3)/0.7
        ell(d,(hip[0]+40,hip[1]+10),24,16,fill=(250,250,252),w=4)
        for i in range(6): line(d,[(hip[0]+40+34*math.cos(i*1.05),hip[1]+10+26*math.sin(i*1.05)),(hip[0]+40+(34+14*u)*math.cos(i*1.05),hip[1]+10+(26+14*u)*math.sin(i*1.05))],w=4,col=(255,230,90))
def hudE(d,T):
    n=pat(T); col=(120,255,140) if n>60 else ((255,210,60) if n>25 else (255,90,80))
    pill(d,110,610,[(150,128,'PACIENCIA',22,(190,196,212),'lm'),(560,140,str(n)+'%',44,col,'rm')])
    rect(d,150,160,570,176,fill=(50,54,66),out=None,w=0,rad=8)
    rect(d,150,160,150+max(6,int(420*n/100)),176,fill=col,out=None,w=0,rad=8)
    if 12.0<=T<13.3:
        u=smooth(min(1,(T-12.0)/0.25))
        rect(d,360-120*u,330,360+120*u,760,fill=(40,46,60),w=8,rad=30); rect(d,360-104*u,350,360+104*u,730,fill=(120,190,255),out=None,w=0,rad=18)
        rect(d,350,752,370,758,fill=(10,10,14),out=None,w=0,rad=3)
        text(d,(360,500),'SIN',44,(20,30,60)); text(d,(360,550),'ENTRADA',44,(20,30,60))
        line(d,[(470,640),(380,748)],w=8,col=(255,70,60)); text(d,(520,620),'USB-C',32,(255,70,60))
    if T>=14.0:
        u=min(1,(T-14.0)/0.4)
        for i in range(14): line(d,[(360+130*math.cos(i*0.45),690+90*math.sin(i*0.45)),(360+(130+160*u)*math.cos(i*0.45),690+(90+110*u)*math.sin(i*0.45))],w=6,col=(255,230,90))
        ell(d,(360,690),110*(0.6+0.4*u),70*(0.6+0.4*u),fill=(250,250,252),w=8); ell(d,(360,675),70*(0.6+0.4*u),24*(0.6+0.4*u),fill=(225,228,238),w=3)
        text(d,(360,780),'BLUETOOTH',36,(40,60,200))
def camE(T):
    if T<1.4: return 1.1,lerp(200,300,T/1.4),700
    if T<13.2: return 1.25,320,700
    if T<14.0: u=smooth((T-13.2)/0.8); return lerp(1.25,1.8,u),lerp(320,360,u),lerp(700,760,u)
    return 1.15,360,720
def postE(img,T):
    if T>=16.5:
        k=max(0.0,1-(T-16.5)/0.5); return Image.fromarray((np.asarray(img,np.float32)*k).astype(np.uint8))
    return img
CE=dict(name='epEar',DUR=17.0,beats=[],speed=[(13.3,14.0)],world=worldE,hud=hudE,cam=camE,post=postE,
 EV=[1.4,1.8,3.0,6.0,9.0,10.5,11.0,12.0,13.3,14.0],flash=[1.8,10.5,12.0,14.0],freeze=[(14.0,14.45)],shakes=[(6.0,9.0,5),(9.0,10.5,9),(14.0,14.5,18)],
 caps=[(0,1.4,'Quiero música.'),(1.4,3.0,'¿QUIÉN HIZO ESTO?'),(3.0,6.0,'Solo tiro de aquí…'),(6.0,9.0,'Paciencia… paciencia…'),(9.0,10.5,'¡¡SUÉLTATEEE!!'),(10.5,11.0,'¡LO LOGRÉ!'),(11.0,12.0,'Enchufo…'),(12.0,13.3,'No tiene entrada.'),(13.3,14.0,'Un momento…'),(14.0,17.1,'Tenía Bluetooth.')],
 pops=[(1.8,2.4,'¡¡NUDO!!',470,90,RED),(6.0,6.6,'¡PEOR!',470,90,RED),(10.5,11.0,'¡¡SÍÍ!!',470,90,YEL),(14.45,15.2,'¡¡DESDE 2019!!',470,80,RED)],
 Ts=(0.6,1.7,2.1,2.8,3.6,4.4,5.0,6.2,7.1,7.6,8.4,9.2,9.9,10.8,11.4,12.4,12.8,13.6,13.9,14.1,15.5))
run(CE)
