setbg('room',(0.9,0.92,1.0))
BX=40; TOPY=200; BOTY=760; PW=1000; PH=500
def sitp(T,face='happy',arms=None,legs=None,lean=0.03):
    return (360,864),lean,(arms or ((1.3,1.6),(1.1,1.5))),(legs or ((1.5,0.1),(1.4,0.1))),face
def stB(T):
    if T<1.5: return sitp(T,'happy',((0.9+0.3*math.sin(T*10),2.2),(1.2,1.6)))
    if T<4.5:
        c=max(0,math.sin(T*4)); return sitp(T,'happy',((1.2+0.9*c,1.6+0.8*c),(1.0,1.5)),((1.5,0.1+0.3*abs(math.sin(T*8))),(1.4,0.1)))
    if T<4.8: return sitp(T,'shock')
    if T<5.4:
        u=smooth((T-4.8)/0.6); h=lerp2((360,864),(400,796),u)
        return h,lerp(0.03,0.08,u),((1.4,1.7),(1.3,1.6)),((lerp(1.5,0.1,u),lerp(0.1,0.0,u)),(lerp(1.4,-0.1,u),lerp(0.1,0.0,u))),'shock'
    if T<7.4: return walkp(lerp(400,600,(T-5.4)/2.0),T,'run',0.6,0.08,((1.4,1.7),(1.3,1.6)))
    if T<8.0: return stand(600,'wtf',arms=((1.4,1.7),(1.3,1.6)))
    if T<10.4: return stand(600,'shock' if T<9.0 else 'wtf',lean=0.0,arms=((0.35,0.05),(0.25,0.0)))
    if T<12.5: return stand(600,'happy',arms=((PI-0.5,PI-0.2),(0.3,0.1)))
    return stand(600,'happy',y=796-12*abs(math.sin(T*9)),arms=UP)
def laptop(d,x,y,a=0.0):
    rrc(d,x,y,90,60,a,(60,64,80),4); rrc(d,x,y,76,46,a,(120,190,255),2); rrc(d,x,y+36,100,10,a,(150,154,170),3)
def worldB(d,T):
    line(d,[(-20,932),(740,932)],w=6)
    # door
    rect(d,610,720,730,932,fill=(176,130,80),w=6,rad=4); circ(d,(630,830),7,fill=YEL,w=3)
    # chair + desk
    rect(d,300,868,420,880,fill=(90,90,110),w=5,rad=4); rect(d,292,780,308,880,fill=(90,90,110),w=5,rad=4); line(d,[(360,880),(360,932)],w=8); line(d,[(320,932),(400,932)],w=8)
    rect(d,450,850,700,864,fill=(150,100,70),w=5,rad=3); line(d,[(470,864),(470,932)],w=8); line(d,[(680,864),(680,932)],w=8)
    ell(d,(640,842),34,12,fill=(250,250,250),w=3); text(d,(640,838),'cereal',12)
    s=stB(T); hip,lean,arms,legs,fc=s
    hd=drawpil(d,s)
    # tie + boxers
    t0=upv(hip,lean,100,0); poly(d,[(t0[0]-9,t0[1]),(t0[0]+9,t0[1]),(t0[0],t0[1]+46)],(220,40,40),3)
    rect(d,hip[0]-30,hip[1]-6,hip[0]+30,hip[1]+30,fill=(110,160,255),w=4,rad=6)
    for k in (-18,0,18): circ(d,(hip[0]+k,hip[1]+12),6,fill=(255,225,60),w=2)
    h2=hands(hip,lean,arms)
    if T<4.8: laptop(d,520,812)
    else:
        mp=((h2[0][0]+h2[1][0])/2+6,(h2[0][1]+h2[1][1])/2-4); laptop(d,mp[0],mp[1])
    if 4.5<=T<5.0: text(d,(640,700),'DING DONG',34,RED)
def tile_face(dr,cx,cy,r,kind):
    dr.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(236,238,246),outline=BK,width=5)
    ex=r*0.38; er=r*(0.34 if kind!='shock' else 0.5)
    for s_ in (-1,1):
        dr.ellipse([cx+s_*ex-er,cy-r*0.15-er,cx+s_*ex+er,cy-r*0.15+er],fill=WH,outline=BK,width=4)
        dr.ellipse([cx+s_*ex-er*0.35,cy-r*0.15-er*0.35,cx+s_*ex+er*0.35,cy-r*0.15+er*0.35],fill=BK)
    if kind=='smile': dr.arc([cx-r*0.4,cy+r*0.05,cx+r*0.4,cy+r*0.6],0,180,fill=BK,width=5)
    elif kind=='shock': dr.ellipse([cx-r*0.18,cy+r*0.25,cx+r*0.18,cy+r*0.62],fill=BK)
    else: dr.line([cx-r*0.3,cy+r*0.4,cx+r*0.3,cy+r*0.4],fill=BK,width=5)
def figure(dr,cx,top,sc_,box,kind,tie=True,legs=True):
    r=60*sc_; cy=top+r; tile_face(dr,cx,cy,r,kind)
    ty=cy+r; dr.rectangle([cx-r*1.05,ty,cx+r*1.05,ty+r*2.0],fill=WH,outline=BK,width=5)
    if tie: dr.polygon([(cx-9*sc_,ty),(cx+9*sc_,ty),(cx,ty+r*1.2)],fill=(220,40,40))
    by=ty+r*2.0; dr.rectangle([cx-r*1.05,by,cx+r*1.05,by+r*0.9],fill=box,outline=BK,width=5)
    for k in (-0.6,0,0.6): dr.ellipse([cx+k*r-7*sc_,by+r*0.35-7*sc_,cx+k*r+7*sc_,by+r*0.35+7*sc_],fill=(255,225,60) if box==(110,160,255) else (255,120,160))
    if legs:
        for s_ in (-1,1): dr.rectangle([cx+s_*r*0.55-r*0.18,by+r*0.9,cx+s_*r*0.55+r*0.18,by+r*1.9],fill=(240,200,170),outline=BK,width=4)
FNT=lambda n: ImageFont.truetype(FONT,n)
def topB(img,T):
    if 9.7<=T<10.5:
        p=Image.new('RGB',(PW,PH),(60,70,90)); dr=ImageDraw.Draw(p); u=smooth((T-9.9)/0.5)
        oy=lerp(20,-330,u); figure(dr,500,oy,1.9,(255,120,160),'smile',True,False)
        dr.text((500,PH-24),'JEFE',font=FNT(34),fill=WH,anchor='mm'); return p
    if T>=12.5:
        p=Image.new('RGB',(PW,PH),(30,34,46)); dr=ImageDraw.Draw(p)
        cols=[(110,160,255),(255,120,160),(120,220,140),(255,190,70)]
        for i in range(4):
            x0=(i%2)*500; y0=(i//2)*250; dr.rectangle([x0+4,y0+4,x0+496,y0+246],fill=(54,60,80),outline=(90,96,120),width=3)
            figure(dr,x0+250,y0+8+4*math.sin(T*8+i),0.62,cols[i],'smile',i!=2,True)
        return p
    # webcam crop
    if T<4.8: cxp,cyp=540,990
    elif T<5.6:
        u=smooth((T-4.8)/0.8); cxp,cyp=lerp(540,lerp(400,430,u)*1.5,u),lerp(990,1110,u)
    elif T<8.0: cxp,cyp=stB(T)[0][0]*1.5+14*math.sin(T*13),1110+10*math.sin(T*17)
    elif T<9.0:
        u=smooth((T-8.0)/0.7); cxp,cyp=stB(T)[0][0]*1.5,lerp(1110,870,u)
    elif T<12.5: cxp,cyp=stB(T)[0][0]*1.5,870
    x0=int(min(max(cxp-250,0),OW-500)); y0=int(min(max(cyp-125,0),OH-250))
    src=base_img[0].crop((x0,y0,x0+500,y0+250)).resize((PW,PH),Image.BICUBIC)
    dr=ImageDraw.Draw(src,'RGBA')
    kind='normal' if T<5.4 else ('shock' if T<10.4 else 'smile')
    dr.rectangle([PW-250,16,PW-16,150],fill=(70,80,105),outline=WH,width=3); tile_face(dr,PW-133,86,40,kind); dr.text((PW-133,138),'JEFE',font=FNT(20),fill=WH,anchor='mm')
    if 9.0<=T<9.7:
        dr.rounded_rectangle([40,PH-130,PW-40,PH-40],radius=20,fill=(255,255,255,235)); dr.text((PW//2,PH-85),'Jefe: Tranquilo… yo también.',font=FNT(40),fill=BK,anchor='mm')
    return src
base_img=[None]
def postB(img,T):
    base_img[0]=img
    cv=Image.new('RGB',(OW,OH),(22,24,34)); d=ImageDraw.Draw(cv)
    s_=min(1,smooth(T/0.35)); oy1=int((1-s_)*-600); oy2=int((1-s_)*700)
    top=topB(img,T); cv.paste(top,(BX,TOPY+oy1)); cv.paste(img.crop((40,780,1040,1280)),(BX,BOTY+oy2))
    for y in (TOPY+oy1,BOTY+oy2): d.rectangle([BX-3,y-3,BX+PW+3,y+PH+3],outline=(255,255,255),width=4) if False else d.rectangle([BX-4,y-4,BX+PW+4,y+PH+4],outline=(70,76,100),width=6)
    return cv
def hudB(d,T):
    rect(d,40,135,330,175,fill=(20,22,30,230),out=None,rad=10) if False else None
    d.text(sc((62,152)),'● REUNIÓN · 4 personas',font=font(22),fill=(120,230,150),anchor='lm')
    if int(T*2)%2==0 and T<12.5: pass
    d.text(sc((62,525)),'LA REALIDAD',font=font(22),fill=(255,140,120),anchor='lm')
    if 1.7<=T<4.5: d.text(sc((660,152)),'MICRO SILENCIADO',font=font(22),fill=(255,110,100),anchor='rm')
CB=dict(name='epB',world=worldB,hud=hudB,post=postB,EV=[],flash=[4.5,7.4,10.0],freeze=(7.4,7.65),
 shakes=[(4.5,4.8,12),(7.4,7.8,14)],speed=[],
 caps=[(0,1.5,'Reunión importante'),(1.5,3.5,'Cámara: profesional'),(3.5,4.5,'Realidad: cereales'),(4.5,5.4,'Suena el timbre'),(5.4,7.4,'Se lleva el portátil'),(7.4,8.0,'¡La cámara!'),(8.0,9.7,'Ay no…'),(9.7,10.5,'Giro de guion'),(10.5,12.5,'Reunión salvada'),(12.5,15.1,'Todos sin pantalones')],
 pops=[(7.45,8.1,'¿¡QUÉ!?',520,100,RED),(12.5,13.4,'¡PRODUCTIVIDAD!',500,64,YEL)],
 Ts=(0.2,0.8,1.8,2.8,3.9,4.6,5.2,5.8,6.8,7.5,7.9,8.5,9.4,10.1,10.7,11.5,12.2,12.8,13.6,14.4,14.9))
run(CB)
