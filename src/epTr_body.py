def phone(d,x,y,w=40,h=70):
    rect(d,x-w/2,y-h/2,x+w/2,y+h/2,fill=(40,46,60),w=4,rad=8); rect(d,x-w/2+5,y-h/2+7,x+w/2-5,y+h/2-7,fill=(120,190,255),out=None,w=0,rad=4)
setbg('street',(1.0,1.0,1.05))
DK_=[(0,100),(1.6,100),(2.2,85),(4.4,25),(5.2,40),(7.0,40),(8.5,10),(10.0,0),(14,0)]
def dg(T):
    for i in range(len(DK_)-1):
        a,b=DK_[i],DK_[i+1]
        if a[0]<=T<b[0]: return int(lerp(a[1],b[1],(T-a[0])/(b[0]-a[0])))
    return 0
SPX=[560,650,720]
def stT(T):
    if T<1.6: return walkp(lerp(70,300,smooth(T/1.6)),T,'happy',amp=0.25,lean=0.05,arms=((0.3,0.1),(0.2,0.1)))
    if T<2.4:
        u=(T-1.6)/0.8; return stand(300+60*u,'shock',lean=0.1+0.7*smooth(u),y=796+10*u,arms=((1.5,1.9),(1.3,1.8)))
    if T<4.4:
        s=math.sin((T-2.4)*14); return stand(360+30*math.sin((T-2.4)*3),'wtf' if T<3.4 else 'shock',lean=0.5*math.sin((T-2.4)*5)+0.3,y=796+12*abs(s),arms=((PI-0.5+0.9*s,PI-0.3),(PI+0.5-0.9*s,PI+0.3)))
    if T<5.2: return stand(380,'shock',lean=0.0,arms=((0.1,0.1),(0.1,0.1)))
    if T<7.0: return walkp(lerp(380,430,smooth((T-5.2)/1.8)),T,'happy',amp=0.2,lean=0.0,arms=((0.2,0.1),(0.3,0.1)))
    if T<8.5: return stand(430,'wtf',lean=0.0,arms=((0.2,0.1),(0.3,0.1)))
    if T<12.0: return stand(430+3*math.sin(T*40),'shock',lean=0.0,arms=((0.2,0.1),(0.3,0.1)))
    u=smooth(min(1,(T-12.0)/0.4)); return stand(430,'shock',lean=0.6*u,y=796+60*u,arms=((PI-0.2,PI-0.3),(PI+0.3,PI+0.4)))
def worldT(d,T):
    line(d,[(-20,932),(740,932)],w=6)
    # curb step
    rect(d,320,915,380,932,fill=(170,170,176),w=5)
    s=stT(T); hd=drawpil(d,s); hip,lean,arms,legs,fc=s; hs=hands(hip,lean,arms)
    if T<4.4: phone(d,hs[1][0]+10,hs[1][1]-4,32,56) if T>=0 and T<2.4 else None
    if 2.4<=T<4.4:
        for i in range(4): line(d,[(hd[0]-60+i*30,hd[1]-90),(hd[0]-56+i*30,hd[1]-110)],w=4,col=(230,40,50))
    if 5.2<=T<7.0:
        for i in range(2): text(d,(hd[0]+50+i*30,hd[1]-60-i*20-8*math.sin(T*8+i)),'♪',34,(40,40,60))
    if 4.4<=T<8.5:
        for i in range(3):
            q=((T*3+i/3)%1); ell(d,(hd[0]-34-i*8,hd[1]-10-q*30+q*q*60),6,10,fill=(120,200,255),w=2)
    # spectators
    if T>=7.0:
        for i,sx in enumerate(SPX):
            arms_=((0.3,0.2),(0.3,0.2)) if i else ((PI-0.5,PI-0.2),(1.0,1.5))
            sp=stand(sx,'wtf' if i else 'happy',lean=-0.05,arms=arms_)
            drawpil(d,sp)
            if i==0:
                hh=hands(sp[0],sp[1],sp[2]); phone(d,hh[0][0]+4,hh[0][1]-30,34,60)
                circ(d,(hh[0][0]+4,hh[0][1]-52),6,fill=(255,40,40),out=None) if int(T*4)%2==0 else None
def hudT(d,T):
    n=dg(T); col=(120,255,140) if n>60 else ((255,210,60) if n>25 else (255,90,80))
    pill(d,110,610,[(150,128,'DIGNIDAD',22,(190,196,212),'lm'),(560,140,str(n)+'%',44,col,'rm')])
    rect(d,150,160,570,176,fill=(50,54,66),out=None,w=0,rad=8)
    rect(d,150,160,150+max(6,int(420*n/100)),176,fill=col,out=None,w=0,rad=8)
    if 8.5<=T:
        u=smooth(min(1,(T-8.5)/0.3)); w_=max(16,130*u)
        rect(d,360-w_,300,360+w_,740,fill=(20,22,30),w=7,rad=26)
        rect(d,360-w_+10,320,360+w_-10,720,fill=(30,34,50),out=None,w=0,rad=14)
        if u>0.9:
            text(d,(360,350),'EN DIRECTO',26,(255,70,70))
            v=int(min(10000000,2300*math.exp((T-8.5)*1.9)))
            text(d,(360,470),(format(v,',').replace(',','.')),40,(255,255,255)); text(d,(360,520),'visualizaciones',26,(190,196,212))
            for i in range(5):
                q=((T*1.3+i/5)%1); text(d,(260+i*40+10*math.sin(T*5+i),700-q*300),'♥',40+int(14*q),(255,60,100))
def camT(T):
    if T<7.0: return 1.15,330 if T>2 else 250,700
    if T<8.5: u=smooth((T-7.0)/1.5); return lerp(1.15,1.3,u),lerp(330,500,u),700
    return 1.0,360,640
CT=dict(name='epTr',DUR=14.0,beats=[],speed=[],world=worldT,hud=hudT,cam=camT,
 EV=[1.6,2.4,4.4,7.0,8.5,12.0],flash=[1.6,4.4,8.5,12.0],freeze=[(12.0,12.4)],shakes=[(2.4,4.4,6),(12.0,12.6,18)],
 caps=[(0,1.6,'Un día normal.'),(1.6,2.4,'¡¡ESCALÓN!!'),(2.4,4.4,'No… no… NO…'),(4.4,5.2,'…'),(5.2,7.0,'Nadie lo vio.'),(7.0,8.5,'¿Eh?'),(8.5,12.0,'Me están grabando.'),(12.0,14.1,'Ya es viral.')],
 pops=[(1.6,2.1,'¡¡UPS!!',470,90,RED),(7.0,7.5,'¿¿??',470,90,YEL),(12.4,13.2,'¡¡10M!!',470,110,RED)],
 Ts=(0.6,1.7,2.1,2.8,3.6,4.4,5.0,6.2,7.1,7.6,8.4,9.2,9.9,10.8,11.4,12.1,12.8,13.2,13.6,13.9,13.95))
run(CT)
