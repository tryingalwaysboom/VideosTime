setbg('room',(1.0,0.95,1.05))
RG=np.random.default_rng(11)
CH=[(RG.uniform(-420,420),RG.uniform(-760,-120),RG.uniform(8,22),int(RG.integers(0,3))) for _ in range(46)]
CF=[(RG.uniform(-500,500),RG.uniform(-900,-200),RG.uniform(0,6),int(RG.integers(0,5))) for _ in range(60)]
CFC=[(255,80,120),(255,220,60),(90,200,255),(120,230,120),(200,120,255)]
CRC=[(255,205,225),(255,255,255),(150,90,60)]
def wq(T):
    if T<7.5: return 0.0
    if T<8.8: return 0.35*(T-7.5)
    return 0.455+(T-8.8)
def outs(i,T):
    iv=[(3.4+0.06*i,4.3+0.07*i)]
    if i<6: iv.append((1.5+0.08*i,2.6+0.04*i))
    return any(a<=T<b for a,b in iv)
def stD(T):
    if T<0.3: return stand(170,'happy',arms=UP)
    if T<1.0: return stand(170,'sleep',lean=0.0,arms=((PI-0.5,PI-0.8),(PI+0.5,PI+0.8)))
    if T<1.4: return stand(170,'run',lean=-0.15)
    if T<2.2: return stand(170+2*math.sin(T*50),'achoo',lean=0.35)
    if T<2.6: return stand(170,'wtf',lean=0.05)
    if T<3.2: return stand(170,'run',lean=-0.2)
    if T<4.1: return stand(170+3*math.sin(T*55),'achoo',lean=0.45)
    if T<4.6: return stand(170,'wtf')
    if T<5.5: return stand(170,'shock',y=796-14*abs(math.sin(T*10)),arms=((PI-0.4,PI-0.1),(PI+0.4,PI+0.1)))
    if T<7.5: return stand(170,'wtf',lean=lerp(0.0,0.4,smooth((T-5.5)/1.0)))
    q=wq(T)
    if q<0.9: return fall(q/0.9,170,230,'shock')
    if T<10.4: return lying(230)
    if T<10.8: return tumble((T-10.4)/0.4,230,'wtf')
    if T<11.4: return stand(230,'wtf')
    if T<12.0: return stand(230,'happy',arms=((PI/2+0.2,PI-0.5),(-0.12,0.0)))
    if T<14.3: 
        f='achoo' if int(T*1.6)%2==0 and (12.4<=T<12.8 or 13.0<=T<13.4 or 13.6<=T<14.0) else 'wtf'
        return stand(230,f,lean=0.1 if f=='achoo' else 0.0)
    return stand(230,'dead')
def cs(x,y,s): return (400+(x-400)*s,850-(850-y)*s)
def cake(d,s):
    def R(x0,y0,x1,y1,fill,w=5):
        a=cs(x0,y0,s); b=cs(x1,y1,s); rect(d,a[0],a[1],b[0],b[1],fill=fill,w=w,rad=6)
    R(250,790,550,850,(255,170,200)); R(290,735,510,790,(255,205,225)); R(250,782,550,798,(255,255,255),4)
    for x in range(270,540,40): 
        a=cs(x,798,s); ell(d,(a[0],a[1]+10*s),11*s,13*s,fill=(255,255,255),w=3)
    ell(d,cs(400,850,s),150*s,10*s,fill=(250,250,250),w=4) if False else None
def candle(d,i,T,s=1.0):
    x=310+20*i; y=735
    a=cs(x,y,s); rect(d,a[0]-4,a[1]-40*s,a[0]+4,a[1],fill=(120,200,255) if i%2 else (255,150,170),w=3,rad=2)
    fy=a[1]-40*s
    if T>=7.0 and T<7.5:
        sp=(T-7.0)/0.5; ell(d,(a[0],fy-8),7+10*(1-sp),12+10*(1-sp),fill=(255,240,120),w=0)
        line(d,[(a[0],fy),(lerp(a[0],400,sp*1.0),lerp(fy,790,sp*1.0))],w=4,col=(255,190,60)); return
    if outs(i,T):
        for a_,b_ in ((3.4+0.06*i,4.3+0.07*i),(1.5+0.08*i,2.6+0.04*i)):
            if a_<=T<a_+0.4 and not (i>=6 and a_==1.5+0.08*i): puff(d,a[0]+14*(T-a_)*8,fy-10-10*(T-a_)*8,(T-a_)/0.4,2,6)
        return
    bend=0.0
    for a_ in (3.4+0.06*i,1.5+0.08*i):
        if a_-0.3<=T<a_: bend=(T-(a_-0.3))/0.3*10
    fl=1+0.15*math.sin(T*30+i)+(0.8 if T>=7.0 else 0)
    ell(d,(a[0]+bend,fy-9*fl),6*s,(10+0*bend)*fl,fill=(255,150,40),w=0); ell(d,(a[0]+bend*0.8,fy-8*fl),3.5*s,6*fl,fill=(255,245,160),w=0)
def blob(d,x,y,r): circ(d,(x,y),r,fill=(255,225,235),w=2)
def worldD(d,T):
    line(d,[(-20,932),(740,932)],w=6)
    # banner
    line(d,[(10,300),(360,350),(710,300)],w=4,col=(120,100,90))
    for i,c in enumerate(CFC*3):
        x=20+i*45; yy_=300+50*math.sin((x/700)*PI)*0.9; poly(d,[(x,yy_),(x+30,yy_),(x+15,yy_+34)],c,3)
    text(d,(360,400),'FELIZ CUMPLE',44,(180,60,100)) if T<7.5 else None
    # table
    rect(d,230,850,640,866,fill=(150,100,70),w=5,rad=4); line(d,[(260,866),(260,932)],w=8); line(d,[(610,866),(610,932)],w=8)
    q=wq(T)
    # balloons
    for k,(bx,bc) in enumerate(((560,(255,90,120)),(620,(90,170,255)),(670,(255,210,70)))):
        if q<0.15+0.1*k:
            by=620-10*math.sin(T*2+k); line(d,[(bx,by+30),(bx-10,850)],w=2,col=(120,120,120)); ell(d,(bx,by),30,38,fill=bc,w=4)
    if T<7.5 or q<0.0:
        s_=1.0+(0.3*smooth((T-7.25)/0.25) if T>=7.25 else 0)+(0.03*math.sin(T*60) if T>=7.0 else 0)
        cake(d,s_)
        for i in range(10): candle(d,i,T,s_)
    else:
        ell(d,(400,850),130,10,fill=(250,250,250),w=3)
        for k in range(5): blob(d,320+k*40,848,8)
    s=stD(T); hip,lean,arms,legs,fc=s
    hd=drawpil(d,s)
    # hat
    poly(d,[(hd[0]-26,hd[1]-48),(hd[0]+26,hd[1]-48),(hd[0],hd[1]-120)],(255,90,120),4) if T<7.5 else None
    if T<7.5: circ(d,(hd[0],hd[1]-122),8,fill=(255,230,80),w=3)
    if q>=0.3:
        for L,o,r in ((40,-26,14),(70,20,16),(100,-10,12),(130,24,14),(168,-30,18),(210,6,20),(20,14,12)): 
            p=upv(hip,lean,L,o); blob(d,p[0],p[1],r)
    # blow lines
    if (1.4<=T<2.2) or (3.2<=T<4.1):
        for i in range(7):
            u=((T*3.2+i/7)%1); x=hd[0]+40+200*u; y=hd[1]+34+(i-3)*10*u; line(d,[(x,y),(x+34,y)],w=4,col=(255,255,255,200))
    # candle on head after explosion
    if T>=12.0:
        hx,hy=hd[0],hd[1]-52; rect(d,hx-5,hy-34,hx+5,hy,fill=(255,150,170),w=3,rad=2)
        fl=1.0+(0.9*smooth((T-13.4)/0.9) if T>=13.4 else 0)
        if T<14.3:
            ell(d,(hx,hy-44*1.0),7*fl,12*fl,fill=(255,150,40),w=0); ell(d,(hx,hy-42),3.5*fl,6*fl,fill=(255,245,160),w=0)
        else:
            puff(d,hx,hy-30,min(1,(T-14.3)/0.7),8,26)
    if 14.3<=T:
        for k in range(5): circ(d,(hd[0]-30+k*15,hd[1]-5+4*math.sin(k)),9,fill=(40,40,44),out=None)
    # explosion particles
    if q>0:
        for vx,vy,r,k in CH:
            x=400+vx*q; y=780+vy*q+450*q*q*2
            if y>925: y=925
            circ(d,(x,y),r,fill=CRC[k],w=2)
        for vx,vy,ph,k in CF:
            x=400+vx*q*1.1+20*math.sin(T*8+ph); y=770+vy*q+450*q*q
            if y<930: rrc(d,x,y,12,7,T*10+ph,CFC[k],0.5)
    if 0.1<=T<1.6:
        t0=T-0.1
        for vx,vy,ph,k in CF[:30]:
            x=170+60+vx*0.45*t0+10*math.sin(T*8+ph); y=620+vy*0.5*t0+600*t0*t0
            if y<930: rrc(d,x,y,12,7,T*10+ph,CFC[k],0.5)
def hudD(d,T):
    n=sum(1 for i in range(10) if outs(i,T)) if T<7.0 else 0
    pill(d,110,610,[(150,128,'VELAS',26,(190,196,212),'lm'),(150,160,'APAGADAS',22,(150,156,172),'lm'),(500,150,f'{n}/10',62,(255,120,110) if n<10 else (120,255,140),'mm')])
def camD(T):
    if T<0.25: return 1.2-0.2*(T/0.25),200,800+OFF
    if 1.4<=T<2.2: return 1.2,300,720+OFF
    if 3.2<=T<4.1: return 1.2+0.15*ease((T-3.2)/0.4),300,720+OFF
    if 5.5<=T<7.0: return 1+0.5*smooth((T-5.5)/1.5),400,730+OFF
    if 7.0<=T<7.5: return 1.5,400,740+OFF
    if 7.5<=T<8.8: return 1.4,300,740+OFF
    if 12.0<=T<14.8: return 1.5,230,660+OFF
    return 1,360,640
CD=dict(name='epD',world=worldD,hud=hudD,cam=camD,EV=[1.4,3.2,7.0,7.5,12.0],flash=[0.15,2.6,7.5],freeze=(7.0,7.25),
 shakes=[(0.0,0.2,8),(7.5,8.1,24),(14.3,14.8,14)],speed=[(7.5,7.9)],
 caps=[(0,1.0,'Pido un deseo…'),(1.0,2.2,'Soplando…'),(2.2,3.2,'¿Se han encendido otra vez?'),(3.2,4.1,'Más fuerte'),(4.1,5.5,'Velas trampa'),(5.5,7.5,'Algo huele a pólvora'),(8.0,10.4,'Sorpresa'),(10.4,12.0,'Está rico, la verdad'),(12.0,14.3,'Una vela. Solo una'),(14.3,15.1,'Feliz cumpleaños')],
 pops=[(0.1,0.7,'¡PRRRT!',330,90,YEL),(2.6,3.2,'¡JIJIJI!',330,90,RED),(5.6,7.0,'¡BZZZT!',330,70,(255,190,60)),(7.5,8.4,'¡BOOOM!',500,130,RED),(9.3,10.0,'¡SPLAT!',330,100,(255,150,200)),(14.3,14.9,'¡PUF!',330,100,(200,200,200))],
 Ts=(0.2,0.6,1.8,2.4,2.8,3.6,4.3,5.0,6.4,7.1,7.55,7.9,8.5,9.3,10.2,10.7,11.6,12.5,13.4,14.0,14.6))
run(CD)
