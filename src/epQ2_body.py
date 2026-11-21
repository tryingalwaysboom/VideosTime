setbg('room',(1.0,0.97,0.92))
AX,BX=560,1280
DEP=[3.0,3.4,3.8,4.2]
def PAN(T):
    if T<1.4: return 0.0
    if T<2.6: return 720*smooth((T-1.4)/1.2)
    if T<4.4: return 720.0
    if T<5.2: return lerp(720,0,smooth((T-4.4)/0.8))
    if T<5.6: return 0.0
    if T<6.4: return lerp(0,720,smooth((T-5.6)/0.8))
    return 720.0
def wx(T):
    if T<1.4: return 120.0
    if T<2.6: return lerp(120,1060,smooth((T-1.4)/1.2))
    if T<4.4: return 1060.0
    if T<5.2: return lerp(1060,120,smooth((T-4.4)/0.8))
    if T<5.6: return 120.0
    if T<6.4: return lerp(120,1060,smooth((T-5.6)/0.8))
    if T<7.0: return 1060.0
    if T<7.8: return lerp(1060,1150,smooth((T-7.0)/0.8))
    return 1150.0
def runphase(T): return (1.4<=T<2.6) or (4.4<=T<5.2) or (5.6<=T<6.4)
def wallane(T): return 2 if wx(T)>600 else 1
def stQ(T):
    X=wx(T)-PAN(T); run=lambda f: walkp(X,T,f,amp=1.0,lean=0.3,arms=((0.9*math.sin(T*14),1.4),(-0.9*math.sin(T*14),-1.4)))
    if T<0.8: return stand(X,'wtf',arms=((0.3,0.2),(-0.3,-0.2)))
    if T<1.4: return stand(X,'shock',lean=-0.1,y=796-6*abs(math.sin(T*16)),arms=((PI-0.4,PI-0.6),(PI-0.2,PI-0.4)))
    if T<2.6: return run('shock')
    if T<2.9: return stand(X,'happy',y=796-8*abs(math.sin(T*10)),arms=((PI-0.5,PI-0.7),(PI+0.4,PI+0.6)))
    if T<3.8: return stand(X,'wtf',lean=0.05,arms=((0.5,0.3),(-0.3,-0.2)))
    if T<4.4: return stand(X+3*math.sin(T*40),'shock',lean=0.12,y=796-4*abs(math.sin(T*30)),arms=((PI-0.3,PI-1.9),(PI-0.45,PI-1.8)))
    if T<5.2: return run('shock')
    if T<5.6: return stand(X,'dead',lean=0.05,arms=((0.3,0.2),(-0.3,-0.2)))
    if T<6.4: return run('shock')
    if T<7.0: return stand(X,'wtf',lean=0.05,arms=((0.5,0.3),(-0.3,-0.2)))
    if T<7.8: return walkp(X,T,'wtf',amp=0.4,lean=0.1,arms=((0.3,0.2),(-0.3,-0.2)))
    if T<8.4: return stand(X,'happy',arms=((0.3,0.2),(-0.3,-0.2)))
    if T<11.0: return stand(X,'happy' if T<10.0 else 'shock',lean=0.0,arms=((0.9,1.0),(0.4,0.6)))
    return None
def served(T): return sum(smooth((T-t)/0.25) for t in DEP)
def slotx(k,T):
    sl=k-served(T)
    return 440-80*sl if sl>=0 else 440+(-sl)*400
def cust(d,x,col,T,kind=0,sc=1.0,mini=False):
    b=2*math.sin(T*6+x*0.1)
    rect(d,x-22,770+b,x+22,860,fill=col,w=5,rad=10)
    line(d,[(x-10,860),(x-10,932)],w=6); line(d,[(x+10,860),(x+10,932)],w=6)
    circ(d,(x,740+b),24,fill=(250,250,250),w=5)
    circ(d,(x+9,738+b),3,fill=BK,out=None); circ(d,(x-5,738+b),3,fill=BK,out=None)
    if kind==0: # grandma bun + glasses
        circ(d,(x-14,716+b),11,fill=(200,200,205),w=3); circ(d,(x+9,738+b),8,fill=None,out=BK,w=2); circ(d,(x-5,738+b),8,fill=None,out=BK,w=2)
        rect(d,x+20,800,x+80,872,fill=(150,150,165),w=4,rad=4)
        for i in range(6): rect(d,x+24+(i%3)*18,780-(i//3)*14,x+40+(i%3)*18,800-(i//3)*14,fill=[(245,200,80),(120,210,120),(235,90,90)][i%3],w=3)
        line(d,[(x+20,870),(x+80,870)],w=4)
        circ(d,(x+30,882),6,fill=(70,70,80),w=2); circ(d,(x+70,882),6,fill=(70,70,80),w=2)
    if kind==1: # mom + kid
        circ(d,(x-6,712+b),14,fill=(120,80,50),out=None)
        kx=x-48; rect(d,kx-12,850,kx+12,900,fill=(250,210,70),w=4,rad=6); circ(d,(kx,832),14,fill=(250,250,250),w=4)
        circ(d,(kx+4,830),2,fill=BK,out=None); circ(d,(kx-4,830),2,fill=BK,out=None)
        if 0.0<=T<2.6 and int(T*3)%2==0: ell(d,(kx+8,840),5,4,fill=(230,90,90),out=None)  # tongue at Wal
    if kind==2: # businessman with tie checking watch
        poly(d,[(x-4,770),(x+4,770),(x+6,820),(x,830),(x-6,820)],(215,40,50),3)
        if 0.0<=T<2.6: line(d,[(x+14,800+b),(x+34,820+b)],w=5)
    if kind==3: # teen headphones
        d.arc([(x-28)*S,(716+b)*S,(x+28)*S,(760+b)*S],180,360,fill=BK,width=int(6*S)) if False else None
        rect(d,x-28,732+b,x-20,750+b,fill=(230,70,70),w=3,rad=3); rect(d,x+20,732+b,x+28,750+b,fill=(230,70,70),w=3,rad=3); line(d,[(x-24,732+b),(x,714+b),(x+24,732+b)],w=4)
def cashier(d,x,T,scan=0.0,col=(70,110,200)):
    rect(d,x-22,740,x+22,830,fill=col,w=5,rad=10)
    circ(d,(x,712),24,fill=(250,250,250),w=5)
    circ(d,(x-6,710),3,fill=BK,out=None); circ(d,(x+8,710),3,fill=BK,out=None); line(d,[(x-8,724),(x+10,724)],w=3)
    a=scan*math.sin(T*28)
    line(d,[(x-14,780),(x-48+14*a,812)],w=7)
def register(d,x,title,closed=False,sign=None):
    rect(d,x-90,820,x+70,932,fill=(130,134,150),w=6,rad=6)
    rect(d,x-250,830,x-90,850,fill=(40,42,52),w=5,rad=6)
    rect(d,x-30,780,x+40,820,fill=(210,212,222),w=5,rad=6); rect(d,x-22,788,x+32,806,fill=(120,220,150) if not closed else (230,90,90),w=3,rad=3)
    rect(d,x-6,560,x+6,720,fill=(90,92,104),out=None,w=0)
    rect(d,x-110,560,x+110,610,fill=(250,230,90) if not closed else (230,70,70),w=5,rad=8)
    text(d,(x,575),title[0],18,(30,30,40)); text(d,(x,596),title[1],14,(30,30,40))
def shelves(d,ox):
    for i in range(-1,5):
        x=i*360-ox%360
        for yy in (430,560,690): rect(d,x+10,yy,x+330,yy+18,fill=(120,90,70),w=4)
        for j in range(8):
            c=[(235,90,90),(90,180,235),(245,200,80),(120,210,120)][(i*3+j)%4]
            for yy in (396,526,656): rect(d,x+22+j*38,yy,x+22+j*38+28,yy+34,fill=c,w=3,rad=3)
def bub(d,x,y,w,h,s1,s2=None,col=(255,255,255),tc=(30,30,40)):
    rect(d,x,y,x+w,y+h,fill=col,w=4,rad=12); text(d,(x+w/2,y+(h/2 if s2 is None else h/3)),s1,20,tc)
    if s2: text(d,(x+w/2,y+2*h/3),s2,20,tc)
def lane2_leave(T): return 6.0
def worldQ(d,T):
    P=PAN(T)
    rect(d,-40,200,760,935,fill=(238,232,224),out=None,w=0)
    shelves(d,P*0.3)
    line(d,[(-20,932),(740,932)],w=6)
    ax=AX-P; cl=T>=4.8
    register(d,ax,('CAJA 1','ABIERTA') if not cl else ('CAJA 1','CERRADA'),closed=cl)
    if T<4.8: cashier(d,ax+10,T,scan=1.0 if (T<4.4 and (T<0 or 2.9<=T<4.4 or T<1.4)) else 0.0)
    elif T<5.8: cashier(d,ax+10+(T-4.8)*260,T)
    # receipt strip from grandma
    if T<3.0:
        L=min(260,60+T*90); line(d,[(ax-100,832),(ax-100,832+L*0.5)],w=14,col=(255,255,255)); line(d,[(ax-100,832),(ax-100,832+L*0.5)],w=2)
    cols=[(230,120,150),(120,180,230),(240,200,90),(150,210,150)]
    for k in range(4):
        x=slotx(k,T)-P
        if -80<x<800: cust(d,x,cols[k],T,kind=k)
    # lane2
    bx=BX-P; register(d,bx,('CAJA RÁPIDA','MÁX. 10 ARTÍCULOS'))
    pcs=2.8<=T<6.0
    cashier(d,bx+10,T,col=(200,90,90),scan=(1.0 if 8.6<=T<9.9 else 0.0))
    cx=1160-P if T<6.0 else 1160-P+(T-6.0)*500
    if T<7.0: cust(d,cx,(140,110,200),T,kind=2)
    if pcs:
        bub(d,cx-120,540,200,64,'¿PRECIO','del yogur?') if int(T*2)%2==0 or T<3.6 else None
        # employee runner
        if 3.2<=T<4.0: ex=lerp(bx-260,bx+420,(T-3.2)/0.8); 
        elif 4.2<=T<5.0: ex=lerp(bx+420,bx-260,(T-4.2)/0.8)
        else: ex=None
        if ex is not None:
            rect(d,ex-18,770,ex+18,850,fill=(220,50,60),w=5,rad=8); circ(d,(ex,745),20,fill=(250,250,250),w=5); line(d,[(ex-8,860),(ex+10,900)],w=6); line(d,[(ex+8,860),(ex-10,900)],w=6)
            for i in range(3): line(d,[(ex-30-i*18,760+i*22),(ex-60-i*18,760+i*22)],w=4,col=(200,200,210))
    if 6.0<=T<6.6: bub(d,cx-130,540,190,60,'¡Resuelto!',col=(210,255,210))
    # Wal
    s=stQ(T)
    if s is not None:
        hd=drawpil(d,s)
        if runphase(T):
            for i in range(3): line(d,[(hd[0]-60-i*20,hd[1]+30+i*18),(hd[0]-100-i*20,hd[1]+30+i*18)],w=4,col=(200,200,210))
        if 2.9<=T<4.4 or 5.2<=T<5.6:
            for i in range(4):
                q=((T*3+i/4)%1); ell(d,(hd[0]-40-i*10,hd[1]-10-q*30+q*q*60),6,10,fill=(120,200,255),w=2)
            if T>=3.4:
                for i in range(3):
                    q=((T*2+i/3)%1); circ(d,(hd[0]+40+i*16,hd[1]-50-q*60),10+q*8,fill=(235,235,240,160),out=None)
        hip,lean,arms,legs,fc=s; hs=hands(hip,lean,arms); h=hs[0]
        if T<8.4 or T>=8.4:
            rect(d,h[0]-26,h[1]-6,h[0]+26,h[1]+30,fill=(235,90,90),w=4,rad=6)
    if 4.8<=T<5.6: bub(d,ax-30,500,140,56,'¡Vuelvo en 5!')
    if 5.0<=T<5.6: pass
    # scanning items
    if 8.4<=T<11.0:
        for i in range(11):
            t0=8.6+i*0.12
            if T>=t0:
                u=min(1,(T-t0)/0.4); x=bx-230+u*190
                if u<1: circ(d,(x,822),9,fill=[(245,200,80),(120,210,120),(90,180,235)][i%3],w=3)
                if T<t0+0.5 and u>=1 or (0<(T-(t0+0.4))<0.1): text(d,(bx-20,760),'BIP',24,(255,60,60))
        if 10.0<=T<11.0: circ(d,(bx,585),90+10*math.sin(T*20),fill=None,out=(255,40,40),w=7)
    # stamp
    sx=1150-P
    if 10.7<=T<12.5:
        y=lerp(-300,905,smooth((T-10.7)/0.3)) if T<11.0 else 905
        rect(d,sx-26,y-300,sx+26,y-120,fill=(120,80,50),w=6,rad=8); rect(d,sx-110,y-130,sx+110,y,fill=(225,40,50),w=7,rad=10); text(d,(sx,y-65),'RECHAZADO',30,(255,255,255))
    elif 12.5<=T<13.2:
        y=905-(T-12.5)/0.7*320
        rect(d,sx-26,y-300,sx+26,y-120,fill=(120,80,50),w=6,rad=8); rect(d,sx-110,y-130,sx+110,y,fill=(225,40,50),w=7,rad=10); text(d,(sx,y-65),'RECHAZADO',30,(255,255,255))
    # pancake Wal
    if T>=11.0:
        if T<12.7:
            px_,py_,ang=sx,920,0.0
        else:
            u=(T-12.7)
            px_=sx+u*u*180+u*120; py_=920-min(u,1.2)*260+30*math.sin(u*9); ang=u*7.0
        if T<12.7 or px_-0+0<2200:
            pts=[]
            for i in range(24):
                a=i*2*PI/24; wv=1+0.35*math.sin(T*18+i)*(0 if T<12.7 else 1)
                pts.append(rotp((px_+110*math.cos(a),py_+14*wv*math.sin(a)*(1 if T<12.7 else 3)),ang,(px_,py_)))
            poly(d,pts,(250,250,250),5)
            for ex in (-30,30):
                p1=rotp((px_+ex-8,py_-6),ang,(px_,py_)); p2=rotp((px_+ex+8,py_+6),ang,(px_,py_)); p3=rotp((px_+ex+8,py_-6),ang,(px_,py_)); p4=rotp((px_+ex-8,py_+6),ang,(px_,py_))
                line(d,[p1,p2],w=4); line(d,[p3,p4],w=4)
        if 11.0<=T<12.5:
            for i in range(14):
                an=i*2*PI/14+0.2; ln=70+60*((i*7)%5)
                line(d,[(sx+30*math.cos(an),800+30*math.sin(an)),(sx+ln*math.cos(an),800+ln*math.sin(an))],w=4,col=(30,30,40))
    # exit door (right)
    dx=1700-P
    open_=12.4<=T<14.8
    rect(d,dx-60,560,dx+90,932,fill=(190,225,245) if not open_ else (255,250,200),w=6)
    line(d,[(dx+15,560),(dx+15,932)],w=5)
    text(d,(dx+15,540),'SALIDA',26,(30,160,80))
    if open_:
        for i in range(6): line(d,[(dx-100-i*30,640+i*40),(dx-180-i*30,640+i*40)],w=5,col=(230,230,240))
    if T>=13.6: bub(d,BX-P-250,540,160,60,'Siguiente.')
def pip(d,T):
    x0,y0,x1,y1=430,215,700,372
    lane=1 if wallane(T)==2 else 2
    rect(d,x0,y0,x1,y1,fill=(28,32,44),w=5,rad=14)
    flash=0
    sc=0.3; fy=y1-14
    def mx(w,off): return x0+10+(w-off)*sc
    if lane==1:
        left=sum(1 for t in DEP if t>T); closed=T>=4.8
        text(d,(x0+54,y0+16),'CAJA 1',17,(190,196,212)); text(d,(x1-30,y0+22),str(left),44,(255,255,255) if left else (120,230,140))
        line(d,[(x0+6,fy),(x1-6,fy)],w=3,col=(150,156,172))
        rect(d,mx(AX,0)-18,fy-36,mx(AX,0)+10,fy,fill=(130,134,150),w=2)
        if not closed:
            circ(d,(mx(AX,0)+2,fy-48),6,fill=(250,250,250),w=2)
        else: rect(d,mx(AX,0)-26,fy-74,mx(AX,0)+14,fy-56,fill=(230,70,70),w=2); text(d,(mx(AX,0)-6,fy-65),'CERRADA',9,(255,255,255))
        for k in range(4):
            x=slotx(k,T)
            if x<700 and x>0: 
                cx_=mx(x,0); rect(d,cx_-5,fy-30,cx_+5,fy-10,fill=[(230,120,150),(120,180,230),(240,200,90),(150,210,150)][k],w=2,rad=3); circ(d,(cx_,fy-38),6,fill=(250,250,250),w=2)
        if any(0<T-t<0.3 for t in DEP): rect(d,x0,y0,x1,y1,fill=None,out=(120,230,140),w=6,rad=14)
    else:
        text(d,(x0+54,y0+16),'CAJA 2',17,(190,196,212)); 
        pc=2.8<=T<6.0; gone=T>=6.0
        n=0 if gone else 1
        text(d,(x1-30,y0+22),str(n),44,(255,255,255) if n else (120,230,140))
        line(d,[(x0+6,fy),(x1-6,fy)],w=3,col=(150,156,172))
        rect(d,mx(AX,0)-18,fy-36,mx(AX,0)+10,fy,fill=(130,134,150),w=2); circ(d,(mx(AX,0)+2,fy-48),6,fill=(250,250,250),w=2)
        if not gone:
            cx_=mx(440,0); rect(d,cx_-5,fy-30,cx_+5,fy-10,fill=(140,110,200),w=2,rad=3); circ(d,(cx_,fy-38),6,fill=(250,250,250),w=2)
            if pc: text(d,(cx_,fy-60),'¿?',16,(230,60,60))
        else:
            text(d,(mx(300,0),fy-40),'¡LIBRE!',16,(30,160,80))
def hudQ(d,T):
    if T<8.4:
        n=0 if T<1.6 else (1 if T<4.6 else (2 if T<5.8 else 3))
        pill(d,110,610,[(150,128,'CAMBIOS DE COLA',20,(190,196,212),'lm'),(560,140,str(n),56,(255,255,255) if n<2 else (255,90,80),'rm'),(150,166,'la otra va más rápida',20,(150,156,172),'lm')])
        if T<8.0: pip(d,T)
    else:
        n=int(lerp(0,11,min(1,max(0,(T-8.6)/1.3)))) if T<11.0 else 11
        pill(d,110,610,[(150,128,'ARTÍCULOS',22,(190,196,212),'lm'),(560,140,str(n),56,(255,255,255) if n<=10 else (255,90,80),'rm'),(150,166,'caja rápida: máx. 10',20,(150,156,172),'lm')])
def camQ(T):
    if 8.4<=T<10.0: u=smooth((T-8.4)/0.5); return lerp(1.2,1.5,u),lerp(380,470,u),lerp(700,720,u)
    if 10.0<=T<10.7: u=smooth((T-10.0)/0.4); return lerp(1.5,2.6,u),lerp(470,580,u),lerp(720,590,u)
    if 10.7<=T<11.0: u=smooth((T-10.7)/0.3); return lerp(2.6,2.0,u),lerp(580,450,u),lerp(590,780,u)
    if 11.0<=T<12.5: return 2.2,450,790
    if 12.5<=T<14.5: u=smooth((T-12.5)/2.0); return lerp(2.2,1.0,u),lerp(450,520,u),lerp(790,700,u)
    if T>=14.5: u=smooth((T-14.5)/0.8); return lerp(1.0,1.15,u),lerp(520,400,u),700
    X=wx(T)-PAN(T)
    z=1.06 if runphase(T) else 1.12
    return z,360,700
def postQ(img,T):
    if T>=16.5:
        k=max(0.0,1-(T-16.5)/0.5); return Image.fromarray((np.asarray(img,np.float32)*k).astype(np.uint8))
    return img
CQ=dict(name='epQ2',DUR=17.0,beats=[(1.4,2.6),(4.4,6.4)],speed=[(4.4,5.2)],world=worldQ,hud=hudQ,cam=camQ,post=postQ,
 EV=[1.4,2.6,2.8,3.0,3.4,3.8,4.2,4.4,5.2,5.6,6.0,7.0,8.4,10.0,11.0,12.5],flash=[1.4,4.4,4.8,5.6,8.4,11.0,12.5],freeze=(11.0,11.25),shakes=[(4.8,5.0,10),(11.0,11.5,16)],
 caps=[(0,1.4,'Cola larguísima'),(1.4,2.6,'¡La otra va más rápida!'),(2.6,4.4,'Y la que dejé… vuela'),(4.4,5.6,'¡Vuelvo!'),(5.6,6.4,'¡Otra vez!'),(6.4,8.4,'Ahora sí'),(8.4,10.0,'Por fin mi turno'),(10.0,11.0,'…'),(11.0,12.5,'11 artículos'),(12.5,14.8,'…'),(14.8,17.1,'Era caja rápida.')],
 pops=[(4.8,5.3,'¡¡CERRADA!!',470,90,RED),(6.0,6.5,'¡¿LIBRE?!',470,90,YEL)],
 Ts=(0.5,1.0,1.9,2.4,3.1,3.6,4.0,4.6,5.0,5.8,6.2,7.2,8.0,8.9,9.8,10.4,10.9,11.2,12.0,12.9,13.6,14.4,15.5,16.6,16.8))
run(CQ)
