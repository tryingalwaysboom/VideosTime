setbg('room',(0.97,1.05,0.95))
PH=[3.0,4.0,5.1,6.4,7.7,8.9,10.0]      # salad lands hits on Pifio
SH=[2.5,3.5,4.5,5.9,7.1,8.5]           # Pifio lands hits on salad
def hpP(T): return max(3,100-sum(13.8*smooth((T-h)/0.15) for h in PH))
def hpS(T): return max(0,100-sum(9.5*smooth((T-h)/0.15) for h in SH))
def near(T,L,w=0.3): return any(h-0.0<=T<h+w for h in L)
def sx(T):  # salad x
    x=520
    for h in PH:
        if h-0.35<=T<h: x-=75*smooth((T-(h-0.35))/0.3)
        elif h<=T<h+0.35: x-=75*(1-smooth((T-h)/0.35))
    for h in SH:
        if h<=T<h+0.3: x+=22*math.sin((T-h)/0.3*PI)
    return x
def pizza_u(T): return smooth((T-12.8)/0.5)
def stF(T):
    if T<1.2: return stand(220,'happy',arms=((0.12,0.0),(-0.12,0.0)))
    if T<2.0: return stand(220,'wtf',y=796-8*abs(math.sin(T*12)))
    if T<10.0:
        for h in PH:
            if h<=T<h+0.35: return stand(220-18*math.sin((T-h)/0.35*PI),'shock',lean=-0.3*math.sin((T-h)/0.35*PI))
        for h in SH:
            if h-0.2<=T<h+0.3:
                u=math.sin((T-(h-0.2))/0.5*PI); return stand(220+25*u,'achoo',lean=0.2*u,arms=((1.0+0.5*u,1.55),(-0.3,0.2)))
        return stand(220+2*math.sin(T*9),'wtf',lean=0.05,arms=((0.5,1.1),(-0.2,0.9)))
    if T<10.4: return stand(200,'shock',lean=-0.3)
    if T<11.8: return lying(190)
    if T<12.4: return tumble((T-11.8)/0.6,190,'wtf')
    if T<12.8: return stand(190,'happy',arms=((0.9,2.1),(-0.12,0.0)))
    if T<13.8: return stand(190+60*smooth((T-12.8)/1.0),'happy',arms=((0.15,0.0),(-0.15,0.0)))
    return stand(250,'happy',arms=((0.9,2.3+0.2*math.sin(T*12)),(-0.12,0.0)))
def saladF(d,T,x,lunge):
    y=800
    # bowl
    d.pieslice([(x-72)*S,(y-72)*S,(x+72)*S,(y+72)*S],0,180,fill=(240,235,225),outline=BK,width=7*S)
    for dx,dy,r,c in ((-45,-62,26,(80,190,90)),(-5,-78,30,(100,210,100)),(40,-60,26,(70,175,85)),(-25,-48,16,(255,70,70)),(30,-45,15,(255,70,70)),(8,-60,12,(255,210,60))):
        circ(d,(x+dx,y+dy),r,fill=c,w=4)
    hurt=any(h<=T<h+0.25 for h in SH)
    dead=T>=12.8
    for ex in (-24,24):
        circ(d,(x+ex,y-6),15,fill=(255,255,255),w=4)
        if hurt: line(d,[(x+ex-9,y-12),(x+ex+9,y),],w=4); line(d,[(x+ex+9,y-12),(x+ex-9,y)],w=4)
        else: circ(d,(x+ex-4,y-6),6,fill=BK,out=None)
    if not dead:
        line(d,[(x-40,y-30),(x-10,y-20)],w=6); line(d,[(x+40,y-30),(x+10,y-20)],w=6)
        pts=[(x-24+i*8,y+30+(8 if i%2 else 0)) for i in range(7)]; line(d,pts,w=5)
    else:
        d.chord([(x-20)*S,(y+14)*S,(x+20)*S,(y+44)*S],0,180,fill=BK)
    return
def worldF(d,T):
    line(d,[(-20,932),(740,932)],w=6)
    # table
    rect(d,380,850,720,866,fill=(150,100,70),w=5,rad=4); line(d,[(410,866),(410,932)],w=8); line(d,[(690,866),(690,932)],w=8)
    # window
    rect(d,60,330,200,500,fill=(190,225,250),w=6,rad=4); line(d,[(130,330),(130,500)],w=4); line(d,[(60,415),(200,415)],w=4)
    s=stF(T); hip,lean,arms,legs,fc=s
    hd=drawpil(d,s)
    hs=hands(hip,lean,arms)
    x=sx(T)
    if T<12.8: saladF(d,T,x,0)
    else: saladF(d,T,x+0,0)
    # leaf whip/tomato projectile
    for h in PH:
        if h-0.15<=T<h+0.1:
            u=(T-(h-0.15))/0.25
            if abs(h-4.0)<1e-6 or abs(h-8.9)<1e-6:
                px=lerp(x-60,hd[0]+40,u); py=lerp(760,hd[1],u)-60*math.sin(u*PI); circ(d,(px,py),17,fill=(255,60,60),w=4)
            else:
                line(d,[(x-60,780),(lerp(x-60,hd[0]+30,u),lerp(780,hd[1]+30,u))],w=14,col=(80,190,90))
    # impact stars
    for h in PH+SH:
        if h<=T<h+0.25:
            cx_=hd[0]+50 if h in PH else x-70; cy_=hd[1]+20 if h in PH else 770
            star(d,cx_,cy_,40+60*(T-h)*4,T*10)
    # pizza
    if 12.8<=T:
        u=pizza_u(T); py=lerp(300,806,u)
        ell(d,(450,py+30),88,18,fill=(255,200,90),w=5)
        circ(d,(450,py+26),64,fill=(255,190,70),w=5) if False else None
        for a_ in range(0,360,60):
            q=math.radians(a_)
            line(d,[(450,py+30),(450+88*math.cos(q),py+30+18*math.sin(q))],w=3,col=(200,120,40))
        for k in range(6): ell(d,(450+55*math.cos(k*1.05+0.4),py+28+11*math.sin(k*1.05+0.4)),9,5,fill=(220,50,50),w=2)
    if 11.8<=T<12.8:
        ph_=(hs[0][0],hs[0][1]); rect(d,ph_[0]-12,ph_[1]-22,ph_[0]+12,ph_[1]+10,fill=(40,40,50),w=3,rad=3)
    if 10.4<=T<11.8:
        stars(d,hd,T)
def bar(d,x0,x1,v,flip,col):
    rect(d,x0,132,x1,162,fill=(150,40,40),out=None,w=0,rad=6)
    w=(x1-x0)*max(0,v)/100
    if flip: rect(d,x1-w,132,x1,162,fill=col,out=None,w=0,rad=6) if w>2 else None
    else: rect(d,x0,132,x0+w,162,fill=col,out=None,w=0,rad=6) if w>2 else None
def hudF(d,T):
    pill(d,40,640,[(315,148,'VS',30,(255,220,90),'mm'),(70,115,'PIFIO',20,(190,196,212),'lm'),(560,115,'ENSALADA',20,(190,196,212),'rm')])
    bar(d,70,285,hpP(T),False,(255,210,60)); bar(d,345,610,hpS(T),True,(90,210,100)) if False else bar(d,345,600,hpS(T),True,(90,210,100))
def camF(T):
    if T<1.2: return 1.1,300,740+OFF
    if 1.2<=T<2.0: return 1.4,380,720+OFF
    if 10.2<=T<11.8: return 1.5,200,780+OFF
    if 12.8<=T<15.0: return 1.15,380,740+OFF
    return 1,360,640
CF_=dict(name='epF',world=worldF,hud=hudF,cam=camF,EV=[1.2,2.5,3.0,6.4,8.9,10.0,12.8],flash=[1.4,10.0,12.8],freeze=(10.4,10.7),
 shakes=[(1.4,1.8,10),(10.0,10.5,22),(12.8,13.3,14)],speed=[(10.0,10.4)],
 caps=[(0,1.2,'Día 1 de dieta'),(1.2,2.0,'La ensalada me miró mal'),(2.0,4.0,'Primer asalto'),(4.0,7.0,'¡Me está ganando!'),(7.0,10.0,'Una ensalada. UNA.'),(10.0,11.8,'Derrotado por lechuga'),(11.8,12.8,'Pidiendo refuerzos'),(12.8,15.1,'Todos quieren pizza')],
 pops=[(1.3,2.0,'¡FIGHT!',400,120,RED),(4.0,4.6,'¡COMBO!',330,90,YEL),(6.4,7.0,'¡x3!',330,100,YEL),(8.9,9.5,'¡x5!',330,100,RED),(10.4,11.6,'K.O.',480,170,RED),(12.8,13.6,'¡PIZZA!',330,100,YEL)],
 Ts=(0.5,1.6,2.6,3.1,4.0,5.2,6.5,7.8,9.0,10.1,10.6,11.2,12.0,12.6,13.0,13.6,14.4,14.9,2.9,8.0,9.9))
run(CF_)
