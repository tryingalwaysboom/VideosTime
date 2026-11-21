setbg('room',(0.92,0.98,1.1))
RG=np.random.default_rng(5)
CFC=[(255,80,120),(255,220,60),(90,200,255),(120,230,120),(200,120,255)]
CF=[(RG.uniform(-300,300),RG.uniform(-700,-150),RG.uniform(0,6),int(RG.integers(0,5))) for _ in range(50)]
def db(d,x,y,s,col=(70,70,80)):
    line(d,[(x-34*s,y),(x+34*s,y)],w=max(4,int(10*s)))
    for sx in (-1,1):
        rect(d,x+sx*34*s-9*s,y-30*s,x+sx*34*s+9*s,y+30*s,fill=col,w=max(3,int(5*s)),rad=3)
        rect(d,x+sx*52*s-7*s,y-22*s,x+sx*52*s+7*s,y+22*s,fill=col,w=max(3,int(5*s)),rad=3)
REP0=3.0; RP=0.8; ENDR=10.2
def effE(T): return max(0,min(1,(T-REP0)/(ENDR-REP0)))
def curlE(T):
    if T<REP0: return 0.0
    if T>=ENDR: return 1.0
    return 0.5-0.5*math.cos(2*PI*(T-REP0)/RP)
def nE(T): return 0 if T<REP0 else min(9,int((min(T,ENDR)-REP0)/RP))
def gran(T):
    if T<13.0: return None
    if T<14.0: return 760-300*smooth((T-13.0)/1.0)
    return 460
def stE(T):
    if T<1.0: return walkp(60+190*T,T,'happy',arms=((0.3,0.2),(-0.3,-0.2)))
    if T<1.8: return stand(250,'happy',arms=((PI-0.5,PI-1.0),(PI+0.5,PI+1.0)))   # flex
    if T<2.4: return stand(250,'shock',y=796-10*abs(math.sin(T*14)))
    if T<REP0:
        u=smooth((T-2.4)/0.6); return stand(250,'wtf',arms=((0.25,lerp(0.1,0.6,u)),(-0.12,0.0)))
    if T<ENDR:
        e=effE(T); c=curlE(T); sh=1.2+6*e*e
        f='happy' if e<0.25 else ('achoo' if e<0.7 else 'shock')
        a=0.2+0.1*c; b=lerp(0.2,2.3,c)
        return stand(250+sh*math.sin(T*70),f,y=796+sh*0.8*math.sin(T*55),lean=-0.05-0.1*e*c,arms=((a,b),(-0.15,0.05)))
    if T<11.6: return stand(250+3*math.sin(T*60),'shock',lean=-0.1,arms=((0.25,2.4),(-0.15,0.05)))
    if T<13.0: return stand(250,'happy',y=796-18*abs(math.sin((T-11.6)*9)),arms=((PI-0.35,PI-0.45),(PI+0.4,PI+0.5)))
    if T<14.6: return stand(250,'wtf',arms=((PI-0.35,PI-0.45),(PI+0.4,PI+0.5)))
    return stand(250,'dead',lean=0.1,arms=((0.15,0.0),(-0.12,0.0)))
def worldE(d,T):
    line(d,[(-20,932),(740,932)],w=6)
    # wall mirror
    rect(d,40,420,200,780,fill=(200,225,245),w=6,rad=8); line(d,[(70,700),(120,500)],w=5,col=(255,255,255)); line(d,[(100,720),(150,540)],w=3,col=(255,255,255))
    text(d,(430,380),'GYM',60,(120,120,150))
    # rack with giant dumbbells
    rect(d,470,650,730,664,fill=(90,90,100),w=5); line(d,[(490,664),(490,932)],w=8); line(d,[(710,664),(710,932)],w=8)
    rect(d,470,780,730,794,fill=(90,90,100),w=5)
    db(d,560,622,1.15,(60,60,75)); db(d,660,622,1.15,(60,60,75))
    if not (gran(T) is not None and 13.9<=T<14.9) : db(d,610,752,1.35,(60,60,75))
    text(d,(560,578),'80',26,(255,255,255)); text(d,(660,578),'80',26,(255,255,255))
    # tiny dumbbell
    s=stE(T); hip,lean,arms,legs,fc=s
    hs=hands(hip,lean,arms)
    if T<2.4: db(d,420,918,0.3)
    elif T<13.0 or T>=14.6:
        if T>=14.6: db(d,300,918,0.3)
        else: db(d,hs[0][0],hs[0][1],0.45,(230,90,60))
    else:
        db(d,hs[0][0]+0,hs[0][1]-4,0.32)
    # tiny label
    if T<2.4: text(d,(420,880),'1kg',22,(120,120,140))
    hd=drawpil(d,s)
    if 2.4<=T<13.0: db(d,hs[0][0]+8,hs[0][1],0.5,(230,90,60))
    if T>=2.4 and T<ENDR:
        e=effE(T)
        # sweat
        for i in range(int(2+8*e)):
            q=((T*2.2+i*0.37)%1); an=i*2.4; x=hd[0]+55*math.cos(an)*(1.0+q*0.6); y=hd[1]-40+q*90-30*abs(math.sin(an))
            ell(d,(x,y),7,11,fill=(120,200,255),w=2)
        # veins/red
        if e>0.4:
            for k in range(int(e*5)): line(d,[(hd[0]-30+k*14,hd[1]-60),(hd[0]-26+k*14,hd[1]-48)],w=4,col=(230,40,50))
    if 10.2<=T<11.6:
        el=hs[0]; circ(d,(el[0]-10,el[1]+40),38,fill=(255,200,170),w=5)
    if 11.6<=T<13.0:
        db(d,hd[0],hd[1]-110,0.32) if False else None
        # trophy
        rect(d,380,780,430,800,fill=(90,60,40),w=4); poly(d,[(375,700),(435,700),(420,775),(390,775)],(255,210,60),4); line(d,[(405,775),(405,780)],w=6)
        text(d,(405,740),'1',34,(180,120,0))
    if T>=11.6 and T<13.4:
        t0=T-11.6
        for vx,vy,ph,k in CF:
            x=250+vx*0.6*t0+10*math.sin(T*8+ph); y=450+vy*0.35*t0+420*t0*t0
            if y<930: rrc(d,x,y,12,7,T*10+ph,CFC[k],0.5)
    g=gran(T)
    if g is not None:
        walk=T<14.0
        if T<14.0: gs=walkp(g,T,'happy',amp=0.4,lean=0.1,arms=((0.2,0.1),(-0.2,-0.1)))
        elif T<14.6: gs=stand(g,'happy',arms=((0.2,0.3),(-0.2,-0.3)))
        else:
            cc=0.5-0.5*math.cos((T-14.6)*5); gs=stand(g,'happy',arms=((0.2,lerp(0.2,2.3,cc)),(-0.2,-0.1)))
        hd2=drawpil(d,gs,look=-1)
        circ(d,(hd2[0]+14,hd2[1]-56),22,fill=(235,235,240),w=5)   # bun
        for dx in (-14,22): circ(d,(hd2[0]+dx+4,hd2[1]-4),16,fill=None,w=3)
        line(d,[(hd2[0]+6,hd2[1]-4),(hd2[0]+8,hd2[1]-4)],w=3)
        hg=hands(gs[0],gs[1],gs[2])
        if T>=14.0: db(d,hg[0][0]-10 if T<14.6 else hg[0][0]-6,hg[0][1]-6,1.35,(60,60,75))
def hudE(d,T):
    n=nE(T) if T<ENDR else 10
    if T>=ENDR: n=10
    pill(d,110,610,[(150,128,'REPS',26,(190,196,212),'lm'),(150,160,'ESFUERZO',20,(150,156,172),'lm'),(500,150,f'{n}',62,(120,255,140) if n>=10 else (255,255,255),'mm')])
    e=effE(T) if T<ENDR else 1.0
    rect(d,310,152,440,172,fill=(50,54,66),out=None,w=0,rad=8)
    if e>0.02: rect(d,310,152,310+130*e,172,fill=(255,int(220-170*e),60),out=None,w=0,rad=8)
def camE(T):
    if 1.0<=T<1.8: return 1.25,250,720+OFF
    if 2.4<=T<ENDR: return 1.15+0.45*effE(T),270,700+OFF
    if 10.2<=T<11.6: return 1.7,270,690+OFF
    if 13.0<=T<15.0: return 1.2,380,700+OFF
    return 1,360,640
CE=dict(name='epE',world=worldE,hud=hudE,cam=camE,EV=[1.0,2.4,10.2,11.6,13.0,14.6],flash=[10.4,11.6,14.6],freeze=(10.2,10.45),
 shakes=[(10.4,11.0,20),(14.6,15.0,12)],speed=[(10.4,10.8)],
 caps=[(0,1.0,'Hoy rompo mi récord'),(1.0,1.8,'Calentando'),(1.8,2.4,'¿Qué pesa más aquí?'),(2.4,3.0,'Mi pesa de 1 kg'),(3.0,6.0,'Esto va a doler'),(6.0,10.2,'No… puedo… más'),(10.2,11.6,'MODO BESTIA'),(11.6,13.0,'¡RÉCORD PERSONAL!'),(13.0,14.6,'Entonces entró la abuela'),(14.6,15.1,'80 kg. Una mano.')],
 pops=[(3.0,3.6,'¡UGH!',330,90,YEL),(6.0,6.6,'¡GRRR!',330,90,RED),(8.5,9.1,'¡ARGH!',330,100,RED),(10.4,11.2,'¡BOOM!',480,130,RED),(11.6,12.3,'¡SÍÍÍ!',330,100,YEL),(14.6,15.1,'¡PLAF!',330,90,(200,200,200))],
 Ts=(0.5,1.4,2.1,2.7,3.5,4.5,6.0,7.5,9.0,10.0,10.6,11.2,12.0,12.8,13.4,14.0,14.4,14.8,15.0,0.9,5.2))
run(CE)
