setbg('room',(0.95,0.9,0.78))
TX=360
SK=[(0,0),(1.5,0),(2.0,20),(3.4,35),(5.5,55),(7,80),(8,92),(10,99),(10.2,60),(11.5,55),(12,80),(13,95),(14.0,100),(17,100)]
def sk(T):
    for i in range(len(SK)-1):
        a,b=SK[i],SK[i+1]
        if a[0]<=T<b[0]: return int(lerp(a[1],b[1],(T-a[0])/(b[0]-a[0])))
    return 100
def libx(T):
    if T<5.5: return 600
    if T<8.0: return lerp(600,470,smooth((T-5.5)/2.5))
    if T<10.0: return 470
    if T<11.0: return lerp(470,600,smooth((T-10.0)/1.0))
    if T<14.0: return 600
    return 600-(T-14)*500
def stW(T):
    bk=((1.5,2.0),(1.3,1.9))
    if T<1.5: return walkp(lerp(60,TX,smooth(T/1.5)),T,'happy',amp=0.25,lean=0.05,arms=((0.25,0.1),(0.2,0.1)))
    if T<3.0: return stand(TX,'happy',arms=bk)
    if T<5.5: return stand(TX+2*math.sin(T*30),'wtf',lean=0.06,arms=((1.5,2.0),(2.5,2.9)))
    if T<8.0: return stand(TX+4*math.sin(T*40),'shock',lean=0.12,y=796-3*abs(math.sin(T*22)),arms=((2.6,3.0),(2.5,2.9)))
    if T<10.0: return stand(TX+3*math.sin(T*55),'shock',lean=0.05,arms=((2.6,3.0),(2.5,2.9)))
    if T<11.5: return stand(TX,'happy',lean=0.0,arms=((0.3,0.2),(0.2,0.1)))
    if T<13.5: return stand(TX,'wtf',lean=-0.15-0.15*smooth((T-11.5)/2.0),arms=((0.3,0.2),(0.2,0.1)))
    if T<14.0: return stand(TX,'shock',lean=-0.45,y=796-6*smooth((T-13.5)/0.5),arms=((PI-0.6,PI-0.4),(PI-0.9,PI-0.6)))
    u=T-14.0; return stand(TX-u*900,'shock',lean=-1.25,y=796-60*u-10,arms=((PI-0.4,PI-0.5),(PI+0.2,PI+0.3)))
def stL(T):
    x=libx(T)
    if T<5.5: return stand(x,'wtf',lean=0.0,arms=((0.3,0.5),(0.3,0.5)))
    if T<8.0: return walkp(x,T,'wtf',amp=0.2,lean=0.0,arms=((0.3,0.5),(0.3,0.5)))
    if T<10.0: return stand(x,'wtf',lean=0.05,arms=((1.0,1.6),(0.2,0.1)))
    if T<11.0: return walkp(x,T,'wtf',amp=0.2,lean=0.0,arms=((0.3,0.5),(0.3,0.5)))
    if T<14.0: return stand(x,'wtf',arms=((0.3,0.5),(0.3,0.5)))
    return stand(x,'shock',lean=-1.2,y=796-70*(T-14)-10,arms=((PI-0.4,PI-0.5),(PI+0.2,PI+0.3)))
BOOKC=[(220,80,80),(80,140,220),(230,190,70),(90,190,120),(170,100,210),(240,140,70)]
def worldS(d,T):
    rect(d,-40,200,760,1000,fill=(60,40,20,40),out=None,w=0)
    line(d,[(-20,932),(740,932)],w=6)
    # shelves on back wall
    for si,sy in enumerate((420,560,700)):
        rect(d,150,sy,720,sy+14,fill=(120,80,50),w=4)
        if T<14.0 or True:
            for bi in range(14):
                bx=160+bi*40; bh=60+(bi*7+si*13)%24
                if T>=14.0:
                    u=T-14.0; fx=-u*(600+bi*40+si*80)
                    if bx+fx<-60: continue
                    rect(d,bx+fx,sy-bh-u*40*(bi%3)+u*u*300,bx+fx+26,sy-u*40*(bi%3)+u*u*300,fill=BOOKC[(bi+si)%6],w=3)
                else:
                    rect(d,bx,sy-bh,bx+26,sy,fill=BOOKC[(bi+si)%6],w=3)
    # window on left (breaks)
    if T<14.2: rect(d,20,380,130,640,fill=(170,220,255),w=7)
    else:
        rect(d,20,380,130,640,fill=(140,190,230),w=7)
        for i in range(8): poly(d,[(20+i*14,380),(34+i*14,380),(24+i*14,420)],(190,230,255),3)
    # SILENCIO sign
    rect(d,400,250,600,300,fill=(250,250,252),w=5,rad=6); text(d,(500,275),'SILENCIO',32,(200,40,40))
    # table + book
    rect(d,230,830,470,850,fill=(150,110,80),w=5); rect(d,260,850,276,932,fill=(130,95,65),w=4); rect(d,424,850,440,932,fill=(130,95,65),w=4)
    # librarian desk
    rect(d,560,800,740,932,fill=(130,95,65),w=5,rad=4)
    # background readers
    for rx in (180,): pass
    # librarian
    sL=stL(T); hdL=drawpil(d,sL)
    circ(d,(hdL[0]+4,hdL[1]-48),16,fill=(80,60,50),w=4)
    for ex in (-14,18): circ(d,(hdL[0]+ex,hdL[1]-6),14,fill=None,out=BK,w=4)
    line(d,[(hdL[0]+4,hdL[1]-6),(hdL[0]+4,hdL[1]-6)],w=3)
    if 8.0<=T<10.0: text(d,(hdL[0]-20,hdL[1]-90),'SHHH',36,(200,40,40))
    # Wal
    s=stW(T); hd=drawpil(d,s); hip,lean,arms,legs,fc=s; hs=hands(hip,lean,arms)
    if T<14.0 and 1.5<=T<3.0: rect(d,hs[0][0]-8,hs[0][1]-26,hs[0][0]+28,hs[0][1]+10,fill=(220,90,80),w=4,rad=3)
    if 3.0<=T<14.0 and T<5.5:
        rect(d,TX-100,810,TX-60,830,fill=(220,90,80),w=4,rad=3)
    if 5.5<=T<10.0:
        circ(d,(hd[0]-14,hd[1]+18),18,fill=(255,90,90,190),out=None); circ(d,(hd[0]+26,hd[1]+18),18,fill=(255,90,90,190),out=None)
        for i in range(4):
            q=((T*3+i/4)%1); ell(d,(hd[0]-36-i*9,hd[1]-10-q*30+q*q*60),6,10,fill=(120,200,255),w=2)
        for i in range(4): line(d,[(hd[0]+36+i*14,hd[1]-60-i*8),(hd[0]+42+i*14,hd[1]-76-i*8)],w=4,col=(230,40,50))
    if 11.5<=T<14.0:
        u=smooth((T-11.5)/1.5); fy=lerp(430,hd[1]-30,u)
        ell(d,(hd[0]+30*(1-u),fy),9,5,fill=(250,250,252),w=2)
    if 14.0<=T<14.6:
        u=(T-14.0)/0.6
        for i in range(10):
            a=i*0.62; line(d,[(TX+70*math.cos(a),700+70*math.sin(a)),(TX+(70+400*u)*math.cos(a),700+(70+400*u)*math.sin(a))],w=5,col=(255,255,255))
        for k in range(14):
            px=TX-40-k*45-u*500; py=500+((k*83)%300)-u*80
            rect(d,px,py,px+36,py+26,fill=(250,250,245),w=3)
    if T>=14.6:
        for k in range(10):
            px=100+k*60; py=300+((T*80+k*97)%500)
            rect(d,px,py,px+36,py+26,fill=(250,250,245),w=3)
def hudS(d,T):
    n=sk(T); col=(120,255,140) if n<50 else ((255,210,60) if n<85 else (255,90,80))
    pill(d,110,610,[(150,128,'ACHÍS EN',22,(190,196,212),'lm'),(560,140,'MAX' if T>=14.0 else str(n)+'%',44,col,'rm')])
    rect(d,150,160,570,176,fill=(50,54,66),out=None,w=0,rad=8)
    rect(d,150,160,150+max(6,int(420*n/100)),176,fill=col,out=None,w=0,rad=8)
    if 14.0<=T<14.5:
        for r_ in range(4): circ(d,(360,700),(T-14.0)*900+r_*60,fill=None,out=(255,255,255,200),w=8)
def camS(T):
    if T<1.5: return 1.05,360,700
    if T<11.5: u=smooth(min(1,(T-1.5)/2.0)); return lerp(1.05,1.15,u),410,700
    if T<14.0: u=smooth((T-11.5)/2.5); return lerp(1.15,1.6,u),lerp(410,360,u),lerp(700,660,u)
    return 1.0,360,640
def postS(img,T):
    if T>=16.5:
        k=max(0.0,1-(T-16.5)/0.5); return Image.fromarray((np.asarray(img,np.float32)*k).astype(np.uint8))
    return img
CS=dict(name='epSn',DUR=17.0,beats=[],speed=[(13.0,14.0)],world=worldS,hud=hudS,cam=camS,post=postS,
 EV=[1.5,3.0,5.5,8.0,10.0,11.5,13.5,14.0],flash=[3.0,10.0,14.0],freeze=[(14.0,14.4)],shakes=[(5.5,10.0,5),(11.5,14.0,6),(14.0,14.6,22)],
 caps=[(0,1.5,'Biblioteca. Silencio total.'),(1.5,3.0,'Qué paz…'),(3.0,5.5,'Me pica la nariz…'),(5.5,8.0,'NO. AQUÍ NO.'),(8.0,10.0,'Me está mirando…'),(10.0,11.5,'Uf… se fue.'),(11.5,13.5,'A… A… A…'),(13.5,14.0,'…'),(14.0,17.1,'Silencio, decían.')],
 pops=[(3.0,3.5,'¿EH?',470,90,YEL),(8.0,8.6,'¡¡SHHH!!',470,90,RED),(14.4,15.2,'¡¡ACHÍÍS!!',470,100,RED)],
 Ts=(0.6,1.7,2.1,2.8,3.6,4.4,5.0,6.2,7.1,7.6,8.4,9.2,9.9,10.8,11.4,12.4,12.8,13.6,13.9,14.1,15.5))
run(CS)
