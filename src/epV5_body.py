setbg('room',(1.0,0.97,0.92))
# timeline
tSearch=1.3; tCable=2.8; tPlug=4.2; tDie=5.4; tWait=6.2; tOn=9.0; tRing=9.7; tCall=10.6; tStare=12.4; tFall=14.0; tLie=15.4; tEnd=15.4
def bat(T):
    if T<tDie: return 1
    if T<6.8: return 0
    if T<8.8: return int(lerp(0,5.4,(T-6.8)/2.0))
    if T<13.6: return 5
    if T<14.0: return int(5*(1-(T-13.6)/0.4))
    return 0
def charging(T): return tPlug<=T
def stV(T):
    if T<tSearch: return stand(380,'shock',arms=((0.9,2.2),(-0.2,-0.3)))
    if T<tCable:
        x=380+200*math.sin((T-tSearch)*4.5); return walkp(x,T,'wtf',amp=0.7,lean=0.12)
    if T<tPlug: return stand(250,'happy',y=796-12*abs(math.sin(T*9)),arms=((PI-0.5,PI-0.7),(PI+0.4,PI+0.6)))
    if T<tDie: return stand(520,'happy',lean=0.05,arms=((0.5,0.3),(-0.3,-0.2)))
    if T<tWait: return stand(520,'shock',arms=((0.9,2.2),(-0.9,-2.2)))
    if T<tOn:
        x=480+40*math.sin((T-6.2)*2.2); return walkp(x,T,'wtf',amp=0.3,lean=0.0)
    if T<tRing: return stand(500,'happy',arms=((0.4,0.3),(-0.3,-0.2)))
    if T<tCall: return stand(500,'shock',y=796-14*abs(math.sin(T*16)),arms=((PI-0.4,PI-0.5),(PI+0.4,PI+0.5)))
    if T<tStare: return stand(500,'happy',arms=((PI-0.3,PI-1.0),(-0.15,0.0)))
    if T<13.4: return stand(500,'wtf',lean=-0.03,arms=((PI-0.3,PI-1.0),(PI-0.7,PI-1.6)))
    if T<tFall: return stand(500+2*math.sin(T*50),'happy',arms=((PI-0.3,PI-1.0),(-0.15,0.0)))
    if T<tEnd: return stand(500+5*math.sin(T*90),'shock',lean=-0.12,y=796+4*math.sin(T*70),arms=((PI-0.5,PI-0.9),(PI+0.5,PI+0.9)))
    return stand(500,'shock',lean=-0.12,arms=((PI-0.5,PI-0.9),(PI+0.5,PI+0.9)))
def worldV(d,T):
    if 6.6<=T<8.8:
        b=bat(T); u=(T-6.6)/2.2
        rect(d,-40,200,760,1000,fill=(236,214,176),out=None,w=0)
        line(d,[(-20,932),(740,932)],w=6)
        rect(d,110,420,590,760,fill=(235,235,240),w=10,rad=30); rect(d,590,520,630,660,fill=(235,235,240),w=8,rad=10)
        lvl=max(0.02,b/100*8*0.6+0.0)
        rect(d,128,438,128+int(444*max(0.03,b/5.0)),742,fill=(255,90,80) if b<3 else (120,230,140),out=None,w=0,rad=18)
        text(d,(350,590),f'{b}%',120,(40,40,50))
        for i in range(5): 
            q=(T*1.5+i/5)%1; text(d,(160+i*95,380-q*60),'⚡',44,(255,210,60))
        return
    line(d,[(-20,932),(740,932)],w=6)
    rect(d,40,780,250,930,fill=(210,90,80),w=6,rad=18); rect(d,40,720,250,800,fill=(225,110,100),w=6,rad=18)
    if tSearch<=T<tCable:
        u=T-tSearch
        for i in range(5): circ(d,(150+i*20,740+i*5-90*math.sin(min(1,u*1.2)*PI)*(i%2+1)),26,fill=(240,200,90),w=4)
    rect(d,420,400,560,560,fill=(200,225,245),w=6,rad=8)
    rect(d,630,850,690,910,fill=(240,240,235),w=5,rad=8); circ(d,(650,880),5,fill=BK,out=None); circ(d,(670,880),5,fill=BK,out=None)
    s=stV(T); hip,lean,arms,legs,fc=s; hs=hands(hip,lean,arms)
    ph=None
    if T<tCable: ph=hs[0]
    if tPlug<=T<tCall: ph=(600,915)
    if tCall<=T<tStare: ph=(hs[0][0]+10,hs[0][1]-20)
    if T>=tStare: ph=(hs[0][0]+10,hs[0][1]-20) if T<tFall+0.1 else (300,918)
    if tCable<=T<tPlug: line(d,[(hs[0][0],hs[0][1]),(hs[0][0]+30,hs[0][1]+80)],w=5,col=(50,50,60))
    if tPlug<=T<tCall: line(d,[(650,880),(640,930),(600,925)],w=5,col=(50,50,60))
    hd=drawpil(d,s)
    if ph is not None:
        on=(bat(T)>0 and not(tDie<=T<tOn)) or T>=tCall
        shk=3*math.sin(T*70) if tRing<=T<tCall else 0
        fillc=(30,200,120) if (tPlug<=T<tDie) else ((255,255,255) if on else (30,30,36))
        rect(d,ph[0]-16+shk,ph[1]-28,ph[0]+16+shk,ph[1]+28,fill=fillc,w=4,rad=5)
    if tSearch<=T<tCable:
        for i in range(3): line(d,[(hd[0]-70-i*22,hd[1]+20+i*14),(hd[0]-100-i*22,hd[1]+20+i*14)],w=4,col=(200,200,210))
    if T>=tFall:
        v=T-tFall; k=1.0+0.12*math.sin(v*40) if T<tEnd else 1.0
        ell(d,(hd[0]+4,hd[1]+34),30*k,44*k,fill=(40,10,20),w=6); ell(d,(hd[0]+4,hd[1]+60),18*k,14*k,fill=(230,90,90),out=None,w=0)
        if T<tEnd+0.8:
            for r_ in range(4):
                rr=((T*340+r_*110)%440)+40; circ(d,hd,rr,fill=None,out=(255,90,80) if r_%2 else (255,255,255),w=6)
        for i in range(5): line(d,[(hd[0]-34+i*17,hd[1]-62),(hd[0]-30+i*17,hd[1]-46)],w=4,col=(230,40,50))
    if tStare<=T<tFall:
        # dramatic tear
        q=((T-tStare)*1.5)%1; ell(d,(hd[0]+30,hd[1]+10+q*60),7,11,fill=(120,200,255),w=2)
def hudV(d,T):
    b=bat(T); chg=charging(T)
    col=(255,90,80) if b<=1 and not chg else ((120,255,140) if chg else (255,200,60))
    pill(d,110,610,[(150,128,'BATERÍA' if not chg else 'CARGANDO',22,(190,196,212),'lm'),(560,128,f'{b}%',50,col,'rm')])
    rect(d,150,160,570,176,fill=(50,54,66),out=None,w=0,rad=8)
    rect(d,150,160,150+max(6,420*b/100*4),176,fill=col,out=None,w=0,rad=8)
    card=None
    if 0.3<=T<tPlug: card=('Mamá','¡Llámame URGENTE!')
    if tRing<=T<tCall: card=('Mamá','Llamada entrante…')
    if tCall+0.4<=T<13.4: card=('Mamá','¿Cómo se llamaba esa serie?')
    if T>=13.4: card=('Mamá','¡Ya me acordé! Gracias, hijo 😊')
    if card:
        rect(d,40,215,680,310,fill=(245,245,248),out=BK,w=4,rad=18)
        text(d,(360,243),card[0],22,(90,90,110)); text(d,(360,280),card[1],26,(30,30,40))
def camV(T):
    if tStare<=T<tFall:
        u=smooth((T-tStare)/(tFall-tStare)); return 1+1.2*u,lerp(360,500,u),lerp(640,640,u)+OFF*u
    if tFall<=T<tEnd:
        u=ease((T-tFall)/1.4); return 2.2+1.4*u,500,590
    if tEnd<=T<tEnd+0.5:
        u=smooth((T-tEnd)/0.5); return lerp(3.6,1.25,u),500,lerp(590,690,u)
    if T>=tEnd+0.5: return 1.25,500,690
    return 1,360,640
def postV(img,T):
    if T>=16.5:
        k=max(0.0,1-(T-16.5)/0.5); a=np.asarray(img,np.float32)*k; return Image.fromarray(a.astype(np.uint8))
    return img
CV=dict(name='epV5',DUR=17.0,beats=[(1.3,4.2)],speed=[(1.3,2.2),(3.1,4.0)],world=worldV,hud=hudV,cam=camV,post=postV,EV=[tSearch,tPlug,tDie,6.6,8.8,tRing,tFall,tEnd],flash=[tDie,tFall,6.6,8.8,tEnd],freeze=(tDie,tDie+0.35),shakes=[(tFall,tEnd,10)],
 caps=[(0,tSearch,'Mamá: llámame urgente'),(tSearch,tCable,'Batería: 1%'),(tCable,tPlug,'¡El cargador!'),(tPlug,tDie,'Salvado…'),(tDie,tWait,'Se apaga'),(tWait,6.6,'Dame un minuto…'),(6.6,8.8,'Esperando al 5%'),(8.8,tOn,'¡Vive!'),(tOn,tRing,'¡Enciende!'),(tRing,tCall,'Por fin'),(tCall,tStare,'Dime, mamá'),(tStare,13.4,'¿Una serie?'),(13.4,tFall,'Ya se acordó'),(tFall,tEnd,'…'),(tEnd,17.1,'Solo era por una serie')],
 pops=[(tDie,tDie+0.6,'¡NOOO!',470,90,RED),(tRing,tRing+0.6,'¡RIIING!',470,90,YEL),(tEnd,tEnd+0.6,'¡PAM!',470,100,YEL)],
 Ts=(0.5,2.0,3.8,5.6,7.5,9.5,11.2,12.4,13.0,13.6,14.2,14.8,15.2,15.6,16.2,16.8,0.9,5.9,10.2,13.9,15.0))
run(CV)
