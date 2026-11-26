import math, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops
W,H=1080,1920; SS=2; FPS=30; DUR=8.0
FLOOR=1330; GY=1375
def mix(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
def cl(x,a=0.,b=1.): return max(a,min(b,x))
def sm(x): x=cl(x); return x*x*(3-2*x)
def seg(t,a,b): return sm((t-a)/(b-a))
def lerp(a,b,t): return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t)
def rot(p,c,a):
    x,y=p[0]-c[0],p[1]-c[1]; ca,sa=math.cos(a),math.sin(a)
    return (c[0]+x*ca-y*sa, c[1]+x*sa+y*ca)
def circ(d,c,r,col): d.ellipse([(c[0]-r)*SS,(c[1]-r)*SS,(c[0]+r)*SS,(c[1]+r)*SS],fill=col)
def ell(d,c,rx,ry,col,outline=None,width=0):
    d.ellipse([(c[0]-rx)*SS,(c[1]-ry)*SS,(c[0]+rx)*SS,(c[1]+ry)*SS],fill=col,outline=outline,width=int(width*SS))
def cap(d,a,b,w,col):
    d.line([a[0]*SS,a[1]*SS,b[0]*SS,b[1]*SS],fill=col,width=max(1,round(w*SS)))
    circ(d,a,w/2,col); circ(d,b,w/2,col)
def poly(d,pts,col): d.polygon([(x*SS,y*SS) for x,y in pts],fill=col)
def rrect(d,b,r,col): d.rounded_rectangle([b[0]*SS,b[1]*SS,b[2]*SS,b[3]*SS],radius=r*SS,fill=col)
def curve(d,pts,w,col):
    d.line([(x*SS,y*SS) for x,y in pts],fill=col,width=max(1,round(w*SS)),joint="curve")
    circ(d,pts[0],w/2,col); circ(d,pts[-1],w/2,col)
def smile(d,c,w,dp,th,col,ang=0,ctr=None):
    pts=[(c[0]+w*u, c[1]+dp*(1-u*u)) for u in [i/6-1 for i in range(13)]]
    if ctr: pts=[rot(p,ctr,ang) for p in pts]
    curve(d,pts,th,col)
def blink(t,times):
    o=1.
    for tb in times:
        if abs(t-tb)<.1: o=min(o,abs(t-tb)/.1)
    return o
def ik(s,t,l1,l2,sign):
    dx,dy=t[0]-s[0],t[1]-s[1]; dist=max(1,min(math.hypot(dx,dy),l1+l2-1))
    a=math.atan2(dy,dx); b=math.acos(cl((l1*l1+dist*dist-l2*l2)/(2*l1*dist),-1,1))
    e=(s[0]+l1*math.cos(a+sign*b), s[1]+l1*math.sin(a+sign*b))
    return e,(s[0]+dist*math.cos(a), s[1]+dist*math.sin(a))

CH=(178,116,96); CARD=(116,140,120); SKA=(232,190,160); SKN=(242,204,176)
HAIR=(74,48,38); DRESS=(104,156,160); WHITE=(242,238,230)

def build_bg():
    im=Image.new("RGB",(W*SS,H*SS)); d=ImageDraw.Draw(im)
    for y in range(FLOOR): d.rectangle([0,y*SS,W*SS,(y+1)*SS],fill=mix((238,218,190),(222,190,156),y/FLOOR))
    for y in range(FLOOR,H): d.rectangle([0,y*SS,W*SS,(y+1)*SS],fill=mix((172,126,92),(138,96,70),(y-FLOOR)/(H-FLOOR)))
    for k in (48,110,190,290,410,540): d.line([0,(FLOOR+k)*SS,W*SS,(FLOOR+k)*SS],fill=(132,92,66),width=3)
    for i,k in enumerate((0,48,110,190,290,410)):
        for x in range(120+(i%2)*260,W,520): d.line([x*SS,(FLOOR+k)*SS,x*SS,(FLOOR+(48,110,190,290,410,540)[i])*SS],fill=(132,92,66),width=3)
    rrect(d,(0,FLOOR-36,W,FLOOR),0,(200,164,130)); d.line([0,(FLOOR-36)*SS,W*SS,(FLOOR-36)*SS],fill=(180,144,112),width=4)
    # ventana
    x0,y0,x1,y1=120,440,410,820
    rrect(d,(x0-18,y0-18,x1+18,y1+18),14,(250,240,222))
    for y in range(y0,y1): d.rectangle([x0*SS,y*SS,x1*SS,(y+1)*SS],fill=mix((92,98,146),(238,176,136),((y-y0)/(y1-y0))**1.4))
    circ(d,(340,520),24,(252,244,214))
    for sx,sy in ((170,480),(230,560),(300,470),(380,600),(200,640)): circ(d,(sx,sy),2.5,(250,244,220))
    poly(d,[(x0,y1),(x0,740),(200,700),(290,750),(360,715),(x1,760),(x1,y1)],(120,112,130))
    rrect(d,(x0-4+141,y0,x0+4+145,y1),0,(250,240,222)); rrect(d,(x0,y0+176,x1,y0+186),0,(250,240,222))
    rrect(d,(x0-40,y1+18,x1+40,y1+38),8,(240,226,204))
    poly(d,[(x0-50,y0-40),(x0+50,y0-40),(x0+10,y1-40),(x0-50,y1+10)],(226,186,166))
    poly(d,[(x1+50,y0-40),(x1-50,y0-40),(x1-10,y1-40),(x1+50,y1+10)],(226,186,166))
    rrect(d,(x0-70,y0-56,x1+70,y0-38),8,(150,110,84))
    # repisa con libros
    rrect(d,(560,610,880,626),4,(150,110,84))
    bx=580
    for w,h,c in ((26,96,(150,120,110)),(20,110,(110,136,140)),(30,88,(206,170,110)),(22,104,(170,130,120)),(26,92,(120,130,112)),(18,84,(196,150,130))):
        rrect(d,(bx,610-h,bx+w,610),3,c); bx+=w+4
    circ(d,(820,580),30,(206,150,120)); cap(d,(820,548),(812,500),6,(112,134,112)); ell(d,(800,500),16,9,(112,134,112)); ell(d,(832,512),16,9,(124,146,120))
    # lampara
    cap(d,(972,770),(972,1335),9,(96,74,62)); ell(d,(972,1340),50,12,(96,74,62))
    poly(d,[(905,775),(1040,775),(1010,660),(935,660)],(248,220,160))
    # alfombra
    ell(d,(520,1440),470,100,(188,146,128)); ell(d,(520,1440),420,80,(202,166,146)); ell(d,(520,1440),300,52,(194,154,136))
    # sillon (respaldo y asiento)
    for lx in (630,945): rrect(d,(lx,1285,lx+30,1345),6,(96,70,58))
    rrect(d,(655,800,990,1270),64,CH); rrect(d,(685,830,960,1160),50,mix(CH,(0,0,0),.07))
    rrect(d,(605,1150,990,1300),40,mix(CH,(0,0,0),.1))
    # luz de lampara + viñeta (baja resolucion)
    g=Image.new("RGB",(W//8,H//8)); gd=ImageDraw.Draw(g)
    gd.ellipse([(972-380)//8,(760-380)//8,(972+380)//8,(760+380)//8],fill=(120,84,40))
    gd.ellipse([(265-200)//8,(640-240)//8,(265+200)//8,(640+240)//8],fill=(26,22,30))
    g=g.filter(ImageFilter.GaussianBlur(22)).resize(im.size,Image.BICUBIC)
    im=ImageChops.add(im,g)
    v=Image.new("L",(W//8,H//8),0); vd=ImageDraw.Draw(v); vd.ellipse([-30,-10,W//8+30,H//8+10],fill=255)
    v=v.filter(ImageFilter.GaussianBlur(34)).resize(im.size,Image.BICUBIC)
    dark=Image.eval(im,lambda p:int(p*.72))
    return Image.composite(im,dark,v)

def alma_state(t):
    u=cl(t/5.0); e=1-(1-u)**1.7
    x=-110+585*e
    speed=585*1.7*(1-u)**.7/5.0 if u<1 else 0
    amp=cl(speed/120)
    return x,amp,x/78*math.pi

def draw_alma(d,t):
    x,amp,ph=alma_state(t)
    tip=math.sin(cl((t-5.0)/.6)*math.pi)*9
    legs=[]
    for k,o in ((0,math.pi),(1,0)):
        th=.5*math.sin(ph+o)*amp; kn=.95*max(0,math.cos(ph+o))*amp
        knee=(72*math.sin(th),72*math.cos(th)); a2=th-kn
        ank=(knee[0]+72*math.sin(a2),knee[1]+72*math.cos(a2)); legs.append((knee,ank))
    hy=GY-20-max(l[1][1] for l in legs)-tip - 1.5*math.sin(t*1.6)*(1-amp)
    sy=hy-138
    floorc=(160,116,84)
    ell(d,(x+4,GY+6),86,13,mix(floorc,(0,0,0),.28))
    arm=lambda sgn:(-.55*sgn*math.sin(ph)*amp+.04)
    def draw_arm(sgn,dk):
        a=arm(sgn); s=(x+2,sy+24); el=(s[0]+54*math.sin(a),s[1]+54*math.cos(a)); a2=a+.35+.25*amp
        hd=(el[0]+50*math.sin(a2),el[1]+50*math.cos(a2)); sk=mix(SKN,(0,0,0),dk)
        cap(d,el,hd,22,sk); cap(d,s,el,24,sk); cap(d,s,lerp(s,el,.45),30,mix(DRESS,(0,0,0),dk)); circ(d,hd,13,sk)
    def draw_leg(i,dk):
        knee,ank=legs[i]; hp=(x,hy); K=(hp[0]+knee[0],hp[1]+knee[1]); A=(hp[0]+ank[0],hp[1]+ank[1]); sk=mix(SKN,(0,0,0),dk)
        cap(d,hp,K,32,sk); cap(d,K,A,27,sk); cap(d,lerp(K,A,.55),A,28,mix(WHITE,(0,0,0),dk))
        ell(d,(A[0]+12,A[1]+9),27,13,mix((128,86,76),(0,0,0),dk))
    draw_arm(-1,.14); draw_leg(0,.12); draw_leg(1,0)
    sw=7*math.sin(ph*2-.6)*amp
    cap(d,(x,sy+26),(x,hy-8),84,DRESS)
    poly(d,[(x-42,hy-70),(x+42,hy-70),(x+74+sw,hy+36),(x-74+sw,hy+36)],DRESS)
    cap(d,(x-62+sw,hy+36),(x+62+sw,hy+36),24,DRESS)
    curve(d,[(x-70+sw,hy+30),(x+70+sw,hy+30)],5,mix(DRESS,(255,255,255),.35))
    cap(d,(x+2,sy+8),(x+4,sy-18),34,SKN)
    ell(d,(x+6,sy+10),34,13,WHITE)
    draw_arm(1,0)
    # cabeza
    look=seg(t,4.0,5.1); pat=seg(t,6.0,6.3)*(1-seg(t,7.3,7.7))
    hx=x+10+3*amp; hyy=sy-64+3*pat+2*math.sin(ph*2)*amp
    C=(hx,hyy); tilt=-.16*look+.05*math.sin(ph)*amp
    pa=-.35-.3*math.sin(ph*2-1.2)*amp+.1*look
    root=rot((hx-70,hyy+2),C,tilt)
    cap(d,root,(root[0]+74*math.sin(pa),root[1]+74*math.cos(pa)),42,HAIR)
    circ(d,C,80,HAIR)
    F=lambda p:rot((hx+p[0],hyy+p[1]),C,tilt)
    ell(d,F((10,10)),65,62,SKN)
    ell(d,F((16,-50)),58,24,HAIR); ell(d,F((-30,-30)),30,40,HAIR)
    circ(d,root,12,(222,176,96))
    lx,ly=8*look,-9*look
    op=blink(t,(1.0,3.2,5.5))
    smv=.3+.7*seg(t,3.4,4.6)
    for ex in (-12,32):
        c=F((ex+lx,6+ly))
        circ(d,F((ex-20 if ex<0 else ex+20,30+ly*.4)),13,mix(SKN,(236,146,134),.5+.2*pat))
        if pat>.5: smile(d,(c[0],c[1]+4),10,-8,5,(60,40,34))
        else:
            ell(d,c,8,max(1.5,11.5*op),(60,40,34))
            if op>.6: circ(d,(c[0]+3,c[1]-4),3,(255,255,255))
        b=F((ex+lx,-16+ly-3*look)); smile(d,(b[0],b[1]-2),10,-4,4,HAIR)
    smile(d,F((12+lx,34+ly*.5)),11+7*smv,3+8*smv,5,(150,84,76),tilt,None)
    return (hx-4,hyy-80+3*pat)

def abuelo_base(d,t):
    br=math.sin(t*1.5)*2
    lift=seg(t,2.5,3.4); sma=seg(t,3.3,4.3); low=seg(t,4.9,5.8)
    TR=(108,100,98)
    for knee,foot,dk in (((606,1168),(600,1322),.15),((584,1172),(574,1326),0)):
        c=mix(TR,(0,0,0),dk)
        cap(d,(790,1170),knee,62,c); cap(d,knee,foot,50,c)
        ell(d,(foot[0]-20,foot[1]+8),40,17,mix((128,88,74),(0,0,0),dk))
    cap(d,(785,1165),(770,985-br),150,CARD)
    poly(d,[(716,930-br),(760,925-br),(748,1010-br)],WHITE)
    cap(d,(758,940-br),(750,905-br),46,mix(SKA,(0,0,0),.08))
    # libro y brazo lejano
    bc=(642,1002+50*low-br*.5); ba=.28-.5*low
    fh=(bc[0]+34,bc[1]+30)
    e,h=ik((772,990-br),fh,120,120,-1)
    cap(d,(772,990-br),e,54,mix(CARD,(0,0,0),.14)); cap(d,e,h,48,mix(CARD,(0,0,0),.14))
    R=lambda p:rot((bc[0]+p[0],bc[1]+p[1]),bc,ba)
    poly(d,[R((-62,-44)),R((62,-44)),R((62,44)),R((-62,44))],(98,122,152))
    poly(d,[R((-54,-36)),R((54,-36)),R((54,36)),R((-54,36))],(108,134,164))
    poly(d,[R((-26,-14)),R((26,-14)),R((26,14)),R((-26,14))],(226,186,120))
    circ(d,h,22,mix(SKA,(0,0,0),.1))
    # cabeza
    C=(746-6*lift,852+9*(1-lift)-br*.6+math.sin(t*2.1)*1.2*(1-lift))
    tilt=-.2*(1-lift)-.06*seg(t,5.6,6.4)
    F=lambda p:rot((C[0]+p[0],C[1]+p[1]),C,tilt)
    circ(d,F((12,6)),84,WHITE); circ(d,C,80,SKA)
    ell(d,F((52,-6)),30,44,WHITE); ell(d,F((46,14)),13,20,mix(SKA,(0,0,0),.1))
    fx=-22-6*lift+ (3*math.sin(t*2.4))*(1-lift); fy=16*(1-lift)+8*seg(t,3.6,5.0)
    op=blink(t,(1.3,4.7,7.0))
    eyes=[F((-36+fx,-8+fy)),F((18+fx,-8+fy))]
    for sx in (-56,40): circ(d,F((sx+fx*.6,26+fy*.5)),17,mix(SKA,(236,150,130),.15+.45*sma))
    for i,c in enumerate(eyes):
        if sma>.85 and op>.5: smile(d,(c[0],c[1]+3),9,-6,5,(64,46,40))
        else: ell(d,c,7,max(1.5,9*op),(64,46,40))
        b=F(((-36,18)[i]+fx,-44+fy-8*math.sin(lift*math.pi)-3*sma))
        curve(d,[(b[0]-15,b[1]+3),(b[0],b[1]-3),(b[0]+15,b[1]+2)],8,WHITE)
        ell(d,c,27,27,None,(112,90,80),4)
    curve(d,[(eyes[0][0]+27,eyes[0][1]),(eyes[1][0]-27,eyes[1][1])],4,(112,90,80))
    curve(d,[(eyes[1][0]+27,eyes[1][1]),F((48,2))],4,(112,90,80))
    ell(d,F((-12+fx,16+fy)),15,12,mix(SKA,(190,130,110),.45))
    smile(d,F((-12+fx,50+fy)),16+9*sma,2+11*sma,5,(128,74,66),tilt,None)
    ell(d,F((-28+fx,37+fy)),23,11,WHITE); ell(d,F((4+fx,37+fy)),23,11,WHITE)
    return bc,br

def chair_front(d):
    c=mix(CH,(255,255,255),.1)
    rrect(d,(630,1078,965,1142),32,c); rrect(d,(630,1078,706,1300),32,c)
    curve(d,[(660,1100),(930,1100)],4,mix(c,(255,255,255),.12))

def abuelo_arm(d,t,bc,br,top):
    p=seg(t,5.2,6.1)
    rd=(bc[0]-30,bc[1]+34)
    tg=lerp(rd,(top[0]+6,top[1]-6),p)
    tg=(tg[0],tg[1]-46*math.sin(p*math.pi)+(5*math.sin((t-6.1)*2*math.pi/1.1) if t>6.1 else 0))
    s=(738,985-br); e,h=ik(s,tg,142,142,-1)
    cap(d,s,e,58,CARD); cap(d,e,h,50,CARD); cap(d,lerp(e,h,.86),h,52,mix(CARD,(255,255,255),.2))
    circ(d,h,25,SKA); cap(d,(h[0]-16,h[1]+6),(h[0]-30,h[1]+12),16,SKA)

BG=None
MOTES=[(880+ (i*53)%200, 800+(i*97)%420, .3+(i%5)*.12, i*1.3) for i in range(14)]
def frame(t):
    global BG
    if BG is None: BG=build_bg()
    im=BG.copy(); d=ImageDraw.Draw(im)
    for mx,my,sp,p0 in MOTES:
        circ(d,(mx+18*math.sin(t*sp+p0),my-12*t*sp+10*math.cos(t*sp*.7+p0)),2.2,(255,236,196))
    bc,br=abuelo_base(d,t)
    chair_front(d)
    top=draw_alma(d,t)
    abuelo_arm(d,t,bc,br,top)
    z=1.30+.10*sm(t/DUR); cx,cy=585+15*sm(t/DUR),1070-25*sm(t/DUR)
    w,h=W*SS/z,H*SS/z; x0=cl(cx*SS-w/2,0,W*SS-w); y0=cl(cy*SS-h/2,0,H*SS-h)
    return im.resize((W,H),Image.LANCZOS,box=(x0,y0,x0+w,y0+h))

if __name__=="__main__":
    if sys.argv[1]=="still":
        ts=[float(a) for a in sys.argv[2:]]
        sh=Image.new("RGB",(360*len(ts),640))
        for i,t in enumerate(ts): sh.paste(frame(t).resize((360,640)),(360*i,0))
        sh.save("still.jpg",quality=88)
    else:
        p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-shortest","-c:v","libx264","-crf","19","-preset","medium","-pix_fmt","yuv420p","-c:a","aac","-b:a","64k","-movflags","+faststart","prueba_animacion_ternura.mp4"],stdin=subprocess.PIPE)
        for i in range(int(DUR*FPS)): p.stdin.write(frame(i/FPS).tobytes())
        p.stdin.close(); p.wait()
