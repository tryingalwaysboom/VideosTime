import math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter
W,H,S,FPS,DUR=720,1280,3,30,18
GT=0
OW,OH=1080,1920
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
_fc={}
def font(sz):
    sz=max(4,int(sz*S))
    if sz not in _fc: _fc[sz]=ImageFont.truetype(FONT,sz)
    return _fc[sz]
BK=(26,26,32); WH=(255,255,255); RED=(229,57,43); YEL=(255,212,0); BLU=(77,163,255)
def sc(p): return (p[0]*S,p[1]*S)
def line(d,pts,w=12,col=BK):
    pp=[sc(p) for p in pts]
    d.line(pp,fill=col,width=int(w*S),joint='curve')
    r=w*S/2
    for x,y in pp: d.ellipse([x-r,y-r,x+r,y+r],fill=col)
def ell(d,c,rx,ry,fill=None,out=BK,w=8):
    x,y=sc(c); d.ellipse([x-rx*S,y-ry*S,x+rx*S,y+ry*S],fill=fill,outline=out,width=int(w*S) if out else 0)
def circ(d,c,r,fill=None,out=BK,w=10): ell(d,c,r,r,fill,out,w)
def rect(d,x0,y0,x1,y1,fill=None,out=BK,w=8,rad=0):
    d.rounded_rectangle([x0*S,y0*S,x1*S,y1*S],radius=rad*S,fill=fill,outline=out,width=int(w*S) if out else 0)
def text(d,xy,s,sz,col=BK):
    d.text(sc(xy),s,font=font(sz),fill=col,anchor='mm')
def ease(x): x=max(0,min(1,x)); return 1-(1-x)**3
def caption(d,s,t,y=1100):
    e=min(1,max(0,t/0.18)); k=0.5+0.5*e+0.18*math.sin(e*math.pi)
    f=font((60 if len(s)<17 else 48 if len(s)<20 else 42)*k)
    b=d.textbbox(sc((360,y)),s,font=f,anchor='mm')
    p=22*S*k
    d.rounded_rectangle([b[0]-p,b[1]-p,b[2]+p,b[3]+p],radius=14*S,fill=YEL,outline=BK,width=5*S)
    d.text(sc((360,y)),s,font=f,fill=BK,anchor='mm')
def P(p,a,L): return (p[0]+L*math.sin(a),p[1]+L*math.cos(a))
def arc(d,c,rx,ry,a0,a1,w=5):
    x,y=sc(c); d.arc([x-rx*S,y-ry*S,x+rx*S,y+ry*S],a0,a1,fill=BK,width=int(w*S))
def headd(d,c,r=52,hair=True):
    x,y=c
    if hair:
        for hx,cx in((-12,-20),(2,4),(16,26)):
            line(d,[(x+hx,y-r+4),(x+(hx+cx)/2,y-r-14),(x+cx,y-r-24)],w=4)
    circ(d,c,r,fill=(206,210,222),w=7); ell(d,(x-5,y-5),r-11,r-11,fill=(255,255,255),out=None)
def face(d,c,kind,look=1):
    x,y=c; dx=10*look; ex=(x-17+dx,x+21+dx); ey=y-6
    if kind=='wtf':
        tw=3*math.sin(GT*55); a=(ex[0]-4,ey-4+tw); b=(ex[1]+12,ey+6)
        circ(d,a,30,fill=(255,255,255),w=5); circ(d,b,13,fill=(255,255,255),w=5)
        circ(d,(a[0]+9*math.sin(GT*9),a[1]+9*math.cos(GT*9)),4,fill=BK,out=None); circ(d,b,3,fill=BK,out=None)
        line(d,[(a[0]-26,a[1]-42),(a[0]+22,a[1]-48)],w=5); line(d,[(b[0]-14,b[1]-20),(b[0]+14,b[1]-24+tw)],w=5)
        line(d,[(x+dx-22+i*9,y+35+(5 if (i+int(GT*14))%2 else -5)) for i in range(6)],w=4)
        return
    if kind=='sleep':
        for e in ex: arc(d,(e,ey-6),15,13,20,160,w=5)
        ell(d,(x+dx+2,y+26),7,6,fill=BK,out=None)
        return
    R={'shock':25,'run':21,'dead':21}[kind]; pr={'shock':5,'run':7,'dead':6}[kind]
    for e in ex: circ(d,(e,ey),R,fill=(255,255,255),w=5)
    px={'shock':0,'run':8*look,'dead':0}[kind]; py={'shock':0,'run':0,'dead':5}[kind]
    for e in ex: circ(d,(e+px,ey+py),pr,fill=BK,out=None)
    if kind=='shock':
        for e,s_ in zip(ex,(-1,1)): line(d,[(e-12,ey-36-4*s_),(e+12,ey-36+4*s_)],w=4)
        ell(d,(x+dx+2,y+34),10,12,fill=BK,out=None)
    elif kind=='run':
        line(d,[(ex[0]-16,ey-30),(ex[0]+12,ey-20)],w=5); line(d,[(ex[1]-12,ey-20),(ex[1]+16,ey-30)],w=5)
        ell(d,(x+dx+4,y+32),12,9,fill=BK,out=None); ell(d,(x+dx+4,y+36),7,4,fill=(230,90,90),out=None)
    else:
        for e in ex: line(d,[(e-R+3,ey-7),(e+R-3,ey-7)],w=5); 
        for e in ex: d.chord([ (e-R)*S,(ey-R)*S,(e+R)*S,(ey+R)*S ],190,350,fill=(206,210,222),outline=BK,width=5*S)
        line(d,[(x+dx-10,y+32),(x+dx+14,y+32)],w=5)
def sleeve(d,pts):
    line(d,pts,w=31); line(d,pts,w=23,col=(255,255,255))
    a,b=pts[-2],pts[-1]; L=math.hypot(b[0]-a[0],b[1]-a[1]) or 1
    h=(b[0]+(b[0]-a[0])/L*12,b[1]+(b[1]-a[1])/L*12)
    line(d,[b,h],w=27); circ(d,h,15,fill=BK,out=None)
def stick(d,hip,lean,arms,legs,fc,look=1,hoff=(0,0)):
    up=lambda L,o=0:(hip[0]+L*math.sin(lean)+o*math.cos(lean),hip[1]-L*math.cos(lean)+o*math.sin(lean))
    neck=up(118); head=up(168); head=(head[0]+hoff[0],head[1]+hoff[1]); sh=up(96)
    def arm(a,b):
        e=P(sh,a,50); sleeve(d,[sh,e,P(e,b,50)])
    arm(*arms[0])
    for (a,b),o in zip(legs,(11,-11)):
        h0=(hip[0]+o,hip[1]); k=P(h0,a,68); f=P(k,b,68)
        line(d,[h0,k,f],w=23); ell(d,(f[0]+13*look,f[1]+1),25,12,fill=BK,out=None)
    line(d,[up(60),up(130)],w=12)
    line(d,[up(8),up(92)],w=78); line(d,[up(8),up(92)],w=70,col=(255,255,255))
    line(d,[up(-14,-30),up(-14,30)],w=22); line(d,[up(-14,-30),up(-14,30)],w=14,col=(255,255,255))
    line(d,[up(40,-18),up(40,18)],w=4); line(d,[up(40,-18),up(22,-24)],w=4); line(d,[up(40,18),up(22,24)],w=4)
    line(d,[up(112,-30),up(100,0),up(112,30)],w=30); line(d,[up(112,-30),up(100,0),up(112,30)],w=22,col=(255,255,255))
    line(d,[up(96,-9),up(66,-11)],w=4); line(d,[up(96,9),up(70,11)],w=4)
    if hoff!=(0,0):
        n0=up(112); m=((n0[0]+head[0])/2,(n0[1]+head[1])/2-0.9*abs(hoff[0]))
        line(d,[((1-u)**2*n0[0]+2*u*(1-u)*m[0]+u*u*head[0],(1-u)**2*n0[1]+2*u*(1-u)*m[1]+u*u*head[1]) for u in [i/14 for i in range(15)]],w=12)
    headd(d,head); face(d,head,fc,look)
    arm(*arms[1])
    return head
def clockface(d,cx,cy):
    circ(d,(cx-30,cy-42),14,fill=RED,w=5); circ(d,(cx+30,cy-42),14,fill=RED,w=5)
    circ(d,(cx,cy),46,fill=WH)
    line(d,[(cx,cy),(cx,cy-26)],w=5); line(d,[(cx,cy),(cx+18,cy)],w=5)
def room(d,t,clock='ring',headface='sleep',inbed=True):
    rect(d,560,800,680,930,fill=(222,184,135)); circ(d,(620,865),7,fill=BK,out=None)
    if clock=='ring':
        cx,cy=620+6*math.sin(t*90),748+4*math.cos(t*70)
        clockface(d,cx,cy)
        if int(t*10)%2==0:
            for a in(-0.35,0.35,math.pi-0.35,math.pi+0.35):
                line(d,[(cx+62*math.cos(a),cy+62*math.sin(a)),(cx+84*math.cos(a),cy+84*math.sin(a))],w=5,col=RED)
    elif clock=='flat':
        ell(d,(620,784),64,17,fill=WH); circ(d,(575,775),10,fill=RED,w=4); circ(d,(665,775),10,fill=RED,w=4)
    else: clockface(d,620,748)
    rect(d,55,690,85,930,fill=(160,110,70))
    line(d,[(520,870),(520,928)],w=10); line(d,[(110,870),(110,928)],w=10)
    rect(d,85,810,530,870,fill=WH)
    rect(d,95,765,215,812,fill=WH,rad=20)
    if inbed:
        headd(d,(165,740),46,False); face(d,(165,740),headface,1)
        rect(d,215,740,530,815,fill=BLU,rad=22)
def s1(d,t):
    room(d,t)
    k=1+0.06*math.sin(t*14)
    text(d,(360,300),'7:00',170*k)
    text(d,(470+5*math.sin(t*60),610),'¡RIIIING!',46,RED)
    caption(d,'Suena la alarma',t)
def s2(d,t):
    room(d,t,clock='ring' if t<0.35 else 'flat')
    hand=None
    if t<0.9: e=ease(t/0.35); hand=(300+312*e,750-0*e+ -30*math.sin(e*math.pi)*0+ (720-750)*e)
    elif t<1.3: e=1-ease((t-0.9)/0.4); hand=(300+312*e,750-30*e)
    if hand:
        mid=((235+hand[0])/2,(760+hand[1])/2-90)
        sleeve(d,[(235,768),mid,hand])
    if 0.35<=t<0.8:
        text(d,(520,640),'¡PAM!',70,RED)
        for a in range(6):
            an=a*1.05+0.3; line(d,[(620+90*math.cos(an),770-70*abs(math.sin(an))-20),(620+125*math.cos(an),770-100*abs(math.sin(an))-20)],w=5,col=RED)
    if t>1.1:
        rect(d,50,430,500,540,fill=WH,rad=30)
        d.polygon([sc((140,536)),sc((205,536)),sc((165,640))],fill=WH)
        line(d,[(140,538),(165,640),(205,538)],w=8)
        text(d,(275,485),'5 minutitos más…',36)
    if t>1.6:
        for i in range(3):
            tt=t-1.6-i*0.35
            if tt>0:
                u=(tt%1.4)/1.4
                text(d,(235+i*35+12*math.sin(tt*4),705-u*100),'Z',28+i*10+u*14,(90,90,90))
    if t>1.9: caption(d,'Error fatal.',t-1.9)
def s3a(d,t):
    circ(d,(360,540),230,fill=WH,w=16)
    for i in range(12):
        a=i*math.pi/6; line(d,[(360+195*math.sin(a),540-195*math.cos(a)),(360+215*math.sin(a),540-215*math.cos(a))],w=8)
    e=ease(t/1.9); m=int(425+162*e)
    am=m/60*2*math.pi; ah=m/720*2*math.pi
    line(d,[(360,540),(360+175*math.sin(am),540-175*math.cos(am))],w=10,col=RED)
    line(d,[(360,540),(360+110*math.sin(ah),540-110*math.cos(ah))],w=14)
    circ(d,(360,540),14,fill=BK,out=None)
    text(d,(360,880),f'{m//60}:{m%60:02d}',120,RED if e>0.97 else BK)
    caption(d,'«5 minutos» después',t)
def s3b(d,t):
    room(d,t,clock='normal',inbed=False)
    hd=stick(d,(260,805),0.05,((-2.0,-2.5),(2.0,2.5)),((1.45,1.5),(1.5,1.55)),'shock',1,hoff=(0,-110*abs(math.sin(t*9))*math.exp(-t*3)))
    rect(d,250,770,530,822,fill=BLU,rad=22)
    for i in range(8):
        a=i*math.pi/4+0.2; line(d,[(hd[0]+88*math.cos(a),hd[1]+88*math.sin(a)),(hd[0]+118*math.cos(a),hd[1]+118*math.sin(a))],w=5,col=RED)
    text(d,(380+6*math.sin(t*70),300),'¡¡9:47!!',130,RED)
    caption(d,'Oh no.',t)
def s4(d,t):
    for i in range(6):
        x=((i*260-t*250)%1560)-260; h=220+(i*73%170)
        rect(d,x,932-h,x+180,932,fill=(170,186,208),out=(108,124,150),w=4)
        for wy in range(int(932-h)+26,890,56):
            for wx in (x+24,x+76,x+128): rect(d,wx,wy,wx+28,wy+32,fill=(228,240,252),out=None)
    for i in range(3):
        x=((i*480-t*900)%1440)-200
        line(d,[(x,932),(x,620),(x+55,620)],w=8,col=(130,130,130)); circ(d,(x+55,632),12,fill=YEL,out=(130,130,130),w=4)
    line(d,[(-20,932),(740,932)],w=6)
    for i in range(8):
        x=((i*130-t*1100)%1040)-160; line(d,[(x,1010),(x+70,1010)],w=8,col=(240,240,235))
    for i in range(7):
        y=430+i*68; x=((i*311-t*1600)%1100)-200
        line(d,[(x,y),(x+110+i*12,y)],w=4,col=(255,255,255))
    ph=t*2*math.pi*3.2
    hip=(310,792-12*abs(math.sin(ph)))
    for k in range(3):
        circ(d,(hip[0]-120-k*48-(t*300%48),912-k*10),24-k*6,fill=(236,232,224),out=None)
    legs=[]
    for o in(0,math.pi):
        a=0.95*math.sin(ph+o); legs.append((a,a-(0.5+0.75*max(0,math.cos(ph+o)))))
    arms=[]
    for o in(math.pi,0):
        a=0.9*math.sin(ph+o); arms.append((a,a+1.4))
    arms=[(math.pi-0.9+0.5*math.sin(ph*0.7),math.pi-0.2+0.9*math.sin(ph*1.4)),(math.pi+0.5+0.5*math.sin(ph*0.7+2),math.pi+0.9*math.sin(ph*1.4+2))]
    head=stick(d,hip,0.3,arms,legs,'run',1,hoff=(-38+20*math.sin(ph*0.5),12*math.sin(ph)))
    for k in range(2):
        u=(t*2.4+k*0.5)%1
        ell(d,(head[0]-66-u*95,head[1]-25+u*45+k*14),6,9,fill=BLU,out=BK,w=3)
    mm=min(59,48+int(t/4*12))
    text(d,(360,210),f'9:{mm}',110,RED)
    text(d,(360,300),'LLEGAS TARDE',34,BK)
    caps=['Sin ducharse','Sin desayunar','Sin dignidad']; i=min(2,int(t/1.33))
    caption(d,caps[i],t-i*1.33)
def dialog(d,cx,cy,k):
    w,h=250*k,105*k
    rect(d,cx-w,cy-h,cx+w,cy+h,fill=(236,236,240),w=5,rad=10)
    rect(d,cx-w,cy-h,cx+w,cy-h+46*k,fill=(40,90,200),w=5,rad=10)
    text(d,(cx-w+100*k,cy-h+23*k),'Sticky.exe',24*k,WH)
    circ(d,(cx-w+62*k,cy+4*k),30*k,fill=RED,w=4); text(d,(cx-w+62*k,cy+4*k),'X',34*k,WH)
    text(d,(cx+48*k,cy-8*k),'ha dejado de',25*k); text(d,(cx+48*k,cy+24*k),'funcionar',25*k)
    rect(d,cx+70*k,cy+h-46*k,cx+w-20*k,cy+h-12*k,fill=WH,w=3,rad=6); text(d,(cx+150*k,cy+h-29*k),'Aceptar',17*k)
def s5(d,t):
    line(d,[(-20,932),(740,932)],w=6)
    rect(d,430,446,650,506,fill=WH,rad=8,w=5); text(d,(540,476),'OFICINA',34)
    rect(d,430,520,650,932,fill=(205,165,115))
    circ(d,(625,740),10,fill=YEL,w=4)
    rect(d,452,608,628,700,fill=WH,rad=6); text(d,(540,654),'CERRADO',27,RED)
    e=ease(t/0.4); x=-120+380*e; sp=0.35*(1-e)
    if t<0.9:
        for k in range(3): circ(d,(x-70-k*45,912-k*8),(22-k*6)*(1-t/0.9)+2,fill=(236,232,224),out=None)
    fc='dead' if t<1.3 else 'wtf'
    hoff=(0,0); lean=-0.3*(1-e); hip=(x,796); legs=((0.15+sp,sp),(-0.15+sp,sp)); arms=((0.62,0.1),(-0.62,-0.1))
    if 1.9<=t<2.9:
        u=ease((t-1.9)/0.8); rd=14*math.sin((t-2.4)*16) if t>2.4 else 0
        hoff=(132*u+rd,26*u)
    elif 2.9<=t<3.4:
        q_=t-2.9; u=1-ease(q_/0.12); w_=34*math.sin(q_*42)*math.exp(-q_*7)
        hoff=(132*u+w_,26*u-abs(w_)*0.6)
    if t>=3.4:
        v=min(1,(t-3.4)/0.5); phi=(math.pi/2)*v*v
        bo=-16*abs(math.sin((t-3.9)*18))*math.exp(-(t-3.9)*7) if t>3.9 else 0
        hip=(260+136*math.sin(phi),932-136*math.cos(phi)-24*math.sin(phi)+bo); lean=phi
        legs=((-phi,-phi),(-phi,-phi)); arms=((-phi+0.22,-phi),(-phi-0.22,-phi))
    head=stick(d,hip,lean,arms,legs,fc,1,hoff=hoff)
    if 1.1<t<1.9:
        u=min(1,(t-1.1)/0.8); ell(d,(head[0]+66,head[1]-20+u*45),6,9,fill=BLU,out=BK,w=3)
    if 3.9<=t<4.3:
        for i in range(7):
            an=math.pi+0.2+i*0.45; r0=70+260*(t-3.9); line(d,[(560+r0*math.cos(an),905+0.6*r0*math.sin(an)),(560+(r0+26)*math.cos(an),905+0.6*(r0+26)*math.sin(an))],w=5,col=YEL)
    if t>0.75:
        e2=min(1,(t-0.75)/0.18); k=0.5+0.5*e2+0.2*math.sin(e2*math.pi)
        rect(d,200-115*k,290-120*k,200+115*k,290+120*k,fill=WH,rad=14)
        rect(d,200-115*k,290-120*k,200+115*k,290-55*k,fill=RED,rad=14)
        text(d,(200,290-88*k),'DOMINGO',30*k,WH); text(d,(200,290+30*k),'11',120*k)
    for i,t0 in enumerate((4.0,4.3,4.55,4.75)):
        if t>t0:
            e3=min(1,(t-t0)/0.14); dialog(d,330+i*26,585+i*34,0.6+0.4*e3+0.12*math.sin(e3*math.pi))
    if 1.0<t<3.4: caption(d,'Era domingo.',t-1.0)
    elif t>=4.0: caption(d,'Cerebro no encontrado',t-4.0)
SC=[(0,3,s1),(3,6,s2),(6,8,s3a),(8,9,s3b),(9,13,s4),(13,18.01,s5)]
K=OW/W
def grad(c0,c1,y0=0,y1=OH):
    a=np.zeros((OH,OW,3),np.float32); t=np.clip((np.arange(OH)-y0)/max(1,(y1-y0)),0,1)[:,None,None]
    return np.array(c0,np.float32)*(1-t)+np.array(c1,np.float32)*t+a
def q(*v): return [x*K for x in v]
def bg_room(window=True):
    a=grad((252,240,216),(236,214,182),0,932*K)
    img=Image.fromarray(a.astype(np.uint8)); d=ImageDraw.Draw(img,'RGBA')
    for x in range(0,720,60): d.line(q(x,0,x,900),fill=(225,200,165,70),width=2)
    d.rectangle(q(0,932,720,1280),fill=(176,128,84))
    for i,y in enumerate(range(932,1280,58)):
        d.line(q(0,y,720,y),fill=(120,82,50),width=3)
        for x in range((i*137)%240-240,720,240): d.line(q(x,y,x,y+58),fill=(130,90,56),width=2)
    d.rectangle(q(0,900,720,932),fill=(250,246,236)); d.line(q(0,900,720,900),fill=(150,130,105),width=3)
    if window:
        d.polygon(q(60,932,250,932,470,1280,180,1280),fill=(255,236,170,70))
        d.rectangle(q(52,412,258,648),fill=(245,240,230),outline=(120,95,70),width=5)
        sky=grad((120,190,250),(255,226,170),430*K,640*K)
        img.paste(Image.fromarray(sky.astype(np.uint8)).crop([int(v) for v in q(66,426,244,634)]),[int(v) for v in q(66,426)])
        d.ellipse(q(165,555,225,615),fill=(255,244,190)); d.ellipse(q(80,460,160,490),fill=(255,255,255,230)); d.ellipse(q(120,448,190,482),fill=(255,255,255,230))
        d.line(q(155,426,155,634),fill=(245,240,230),width=9); d.line(q(66,530,244,530),fill=(245,240,230),width=9)
        d.ellipse(q(300,950,700,1040),fill=(196,70,70)); d.ellipse(q(325,960,675,1030),outline=(240,200,170),width=5)
    return img
def bg_street(office=False):
    a=grad((92,170,245),(214,236,252),0,932*K)
    img=Image.fromarray(a.astype(np.uint8)); d=ImageDraw.Draw(img,'RGBA')
    d.ellipse(q(540,70,660,190),fill=(255,243,176)); d.ellipse(q(520,50,680,210),fill=(255,243,176,60))
    for cx,cy,s_ in ((120,420,1.0),(560,520,0.8),(330,110,0.7)):
        for dx,dy,r in ((0,0,38),(40,-18,46),(86,0,36),(44,12,42)):
            d.ellipse(q(cx+dx*s_-r*s_,cy+dy*s_-r*s_*0.7,cx+dx*s_+r*s_,cy+dy*s_+r*s_*0.7),fill=(255,255,255,235))
    if office:
        d.rectangle(q(330,360,720,932),fill=(190,104,86))
        for i,y in enumerate(range(360,932,26)):
            d.line(q(330,y,720,y),fill=(150,78,64),width=2)
            for x in range(330+(i%2)*30,720,60): d.line(q(x,y,x,y+26),fill=(150,78,64),width=2)
        d.rectangle(q(330,345,720,365),fill=(120,66,56))
    d.rectangle(q(0,932,720,968),fill=(200,200,204)); d.rectangle(q(0,968,720,1280),fill=(84,88,98))
    d.line(q(0,968,720,968),fill=(60,62,70),width=4)
    for x in range(0,720,90): d.line(q(x,932,x-14,968),fill=(160,160,166),width=2)
    return img
BG={s1:bg_room(),s2:bg_room(),s3a:bg_room(False),s3b:bg_room(),s4:bg_street(),s5:bg_street(True)}
yy,xx=np.mgrid[0:OH,0:OW]
VIG=(1-0.42*np.clip(((xx-OW/2)/(OW*0.75))**2+((yy-OH/2)/(OH*0.75))**2,0,1))[:,:,None].astype(np.float32)
def frame(T):
    for a,b,f in SC:
        if a<=T<b:
            t=T-a
            global GT; GT=T
            lay=Image.new('RGBA',(W*S,H*S),(0,0,0,0)); d=ImageDraw.Draw(lay); f(d,t)
            lay=lay.resize((OW,OH),Image.LANCZOS)
            ox=oy=0
            if f is s3b: ox,oy=int(13*math.sin(t*80)*(1-t)),int(9*math.cos(t*65)*(1-t))
            if f is s2 and 0.35<=t<0.6: oy=int(12*math.sin(t*90))
            if f is s5 and 3.9<=t<4.2: oy=int(16*math.sin(t*90))
            if ox or oy: lay=ImageChops.offset(lay,ox,oy)
            img=BG[f].copy()
            if f is s3b and t<0.14: img=Image.blend(img,Image.new('RGB',(OW,OH),(255,90,70)),0.45)
            al=lay.getchannel('A')
            sh=al.resize((OW//4,OH//4)).filter(ImageFilter.GaussianBlur(3.2)).resize((OW,OH),Image.BILINEAR)
            sh=ImageChops.offset(sh,12,18).point(lambda v:int(v*0.34))
            img.paste((30,20,30),(0,0),sh)
            img.paste(lay,(0,0),lay)
            arr=np.asarray(img,np.float32)*VIG
            return Image.fromarray(arr.astype(np.uint8))
# ---------- audio
sr=44100; N=sr*DUR; A=np.zeros(N); rng=np.random.default_rng(3)
def add(sig,t0,vol=1.0):
    i=int(t0*sr)
    if i>=N: return
    n=min(len(sig),N-i); A[i:i+n]+=sig[:n]*vol
def tone(f,dur,kind='sine',decay=0.0):
    t=np.arange(int(dur*sr))/sr
    if kind=='sine': s=np.sin(2*np.pi*f*t)
    elif kind=='sq': s=np.sign(np.sin(2*np.pi*f*t))
    else: s=2*((f*t)%1)-1
    return s*np.exp(-decay*t)*np.minimum(1,t*300)*np.minimum(1,(dur-t)*300)
def noise(dur,decay): 
    t=np.arange(int(dur*sr))/sr; return rng.uniform(-1,1,len(t))*np.exp(-decay*t)
def sweep(f0,f1,dur,kind='sine'):
    t=np.arange(int(dur*sr))/sr; f=f0*(f1/f0)**(t/dur); ph=np.cumsum(f)/sr
    s=np.sin(2*np.pi*ph) if kind=='sine' else 2*(ph%1)-1
    return s*np.minimum(1,t*300)*np.minimum(1,(dur-t)*300)
for g in np.arange(0,3.3,0.6):
    for b in range(3):
        if g+b*0.13<3.3: add(tone(1900,0.07,'sq'),g+b*0.13,0.22)
add(noise(0.25,18),3.35,0.8); add(sweep(120,45,0.35)*np.exp(-8*np.arange(int(0.35*sr))/sr),3.35,1.0)
for s0 in(4.7,5.4):
    n=int(0.55*sr); t=np.arange(n)/sr; add(sweep(95,70,0.55,'saw')*np.sin(np.pi*t/0.55),s0,0.16)
n=2*sr; t=np.arange(n)/sr; add(sweep(300,1700,2.0)*(np.sin(2*np.pi*(6+5*t)*t)>0),6.0,0.22)
add(noise(0.6,7),8.0,0.55); add(tone(110,0.8,'sq',4),8.0,0.2); add(tone(117,0.8,'sq',4),8.0,0.2)
beat=60/176; mel=[440,523,659,523,587,659,784,659]; bass=[110,110,131,147]
for i,tb in enumerate(np.arange(9,12.95,beat)):
    k=sweep(150,45,0.18); add(k*np.exp(-14*np.arange(len(k))/sr),tb,0.9)
    add(np.diff(noise(0.06,60),prepend=0),tb+beat/2,0.35)
    for j in(0,1):
        tt=tb+j*beat/2
        add(tone(bass[i%4],beat/2*0.9,'sq',3),tt,0.11)
        add(tone(mel[(2*i+j)%8],beat/2*0.8,'saw',5),tt,0.10)
add(sweep(2600,700,0.38,'saw'),13.0,0.22); add(noise(0.38,6),13.0,0.15)
add(tone(1568,0.5,'sine',7),13.75,0.3); add(tone(2093,0.5,'sine',7),13.75,0.2)
for c0 in (14.05,14.45,14.85,15.2):
    for j in range(3): add(tone(4300,0.035,'sine',20),c0+j*0.055,0.10)
for tw_ in (14.3,14.42,14.54): add(tone(900,0.03,'sq',40),tw_,0.12)
n=int(0.85*sr); tq=np.arange(n)/sr
add(sweep(140,620,0.85,'saw')*(0.55+0.45*np.sign(np.sin(2*np.pi*26*tq))),14.9,0.20)
for r_ in (15.45,15.6,15.75): add(tone(700,0.05,'sine',30),r_,0.18)
n=int(0.5*sr); tq=np.arange(n)/sr
fq=260+420*np.exp(-tq*5)*np.abs(np.sin(2*np.pi*9*tq)); add(np.sin(2*np.pi*np.cumsum(fq)/sr)*np.exp(-tq*5),15.9,0.45)
add(sweep(1500,220,0.5),16.4,0.28)
add(noise(0.35,14),16.9,0.9); kk=sweep(130,38,0.45); add(kk*np.exp(-7*np.arange(len(kk))/sr),16.9,1.0)
for i,t0 in enumerate((17.0,17.3,17.55,17.75)):
    add(tone(392,0.12,'sq',6),t0,0.2); add(tone(277,0.2,'sq',6),t0+0.11,0.2)
add(tone(1200,0.05,'sine',30),8.0,0.4)
A=A/np.abs(A).max()*0.9
with wave.open('audio.wav','wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((A*32767).astype(np.int16).tobytes())
# ---------- render
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{OW}x{OH}','-r',str(FPS),'-i','-','-i','audio.wav','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','slow','-c:a','aac','-b:a','128k','-shortest','stickman_5_minutitos_mas_v4.mp4'],stdin=subprocess.PIPE)
checks={45:0,135:1,210:2,255:3,330:4,435:5}; sheet=Image.new('RGB',(360*6,640),WH)
for n in range(FPS*DUR):
    im=frame(n/FPS); p.stdin.write(im.tobytes())
    if n in checks: sheet.paste(im.resize((360,640)),(360*checks[n],0))
p.stdin.close(); p.wait(); sheet.save('check.png')
