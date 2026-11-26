import math, subprocess, sys, random
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageOps, ImageFont
W,H=1080,1920; SS=2; FPS=30
FLOOR=1330; GY=1375; OW=2.6
OX=OY=0
DARK=(70,44,38)
def mix(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
def OC(c,k=.5): return mix(c,DARK,k)
def cl(x,a=0.,b=1.): return max(a,min(b,x))
def sm(x): x=cl(x); return x*x*(3-2*x)
def seg(t,a,b): return sm((t-a)/(b-a)) if abs(b-a)>1e-6 else (1.0 if t>=a else 0.0)
def lerp(a,b,t): return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t)
def rot(p,c,a):
    x,y=p[0]-c[0],p[1]-c[1]; ca,sa=math.cos(a),math.sin(a)
    return (c[0]+x*ca-y*sa, c[1]+x*sa+y*ca)
def _p(p): return ((p[0]-OX)*SS,(p[1]-OY)*SS)
def _e(d,c,rx,ry,col): d.ellipse([_p((c[0]-rx,c[1]-ry)),_p((c[0]+rx,c[1]+ry))],fill=col)
def _cap(d,a,b,w,col):
    d.line([_p(a),_p(b)],fill=col,width=max(1,round(w*SS))); _e(d,a,w/2,w/2,col); _e(d,b,w/2,w/2,col)
def circ(d,c,r,col,o=0,oc=None): ell(d,c,r,r,col,o,oc)
def ell(d,c,rx,ry,col,o=0,oc=None):
    if o: _e(d,c,rx+o,ry+o,oc or OC(col))
    _e(d,c,rx,ry,col)
def ring(d,c,rx,ry,w,col): d.ellipse([_p((c[0]-rx,c[1]-ry)),_p((c[0]+rx,c[1]+ry))],outline=col,width=max(1,round(w*SS)))
def cap(d,a,b,w,col,o=0,oc=None):
    if o: _cap(d,a,b,w+2*o,oc or OC(col))
    _cap(d,a,b,w,col)
def limb(d,pts,ws,col,o=OW,oc=None):
    for i in range(len(pts)-1): _cap(d,pts[i],pts[i+1],ws[i]+2*o,oc or OC(col))
    for i in range(len(pts)-1): _cap(d,pts[i],pts[i+1],ws[i],col)
def curve(d,pts,w,col):
    d.line([_p(p) for p in pts],fill=col,width=max(1,round(w*SS)),joint="curve")
    _e(d,pts[0],w/2,w/2,col); _e(d,pts[-1],w/2,w/2,col)
def poly(d,pts,col,o=0,oc=None):
    if o: curve(d,list(pts)+[pts[0]],2*o,oc or OC(col))
    d.polygon([_p(p) for p in pts],fill=col)
def rrect(d,b,r,col,o=0,oc=None):
    if o: d.rounded_rectangle([_p((b[0]-o,b[1]-o)),_p((b[2]+o,b[3]+o))],radius=(r+o)*SS,fill=oc or OC(col))
    d.rounded_rectangle([_p(b[:2]),_p(b[2:])],radius=r*SS,fill=col)
def bez(a,c,b,n=12): return [((1-u)**2*a[0]+2*u*(1-u)*c[0]+u*u*b[0],(1-u)**2*a[1]+2*u*(1-u)*c[1]+u*u*b[1]) for u in [i/n for i in range(n+1)]]
def arcpts(c,w,dp,ang=0,ctr=None):
    pts=[(c[0]+w*u, c[1]+dp*(1-u*u)) for u in [i/6-1 for i in range(13)]]
    return [rot(p,ctr,ang) for p in pts] if ctr else pts
def smile(d,c,w,dp,th,col,ang=0,ctr=None): curve(d,arcpts(c,w,dp,ang,ctr),th,col)
def blink(t,times):
    o=1.
    for tb in times:
        if abs(t-tb)<.1: o=min(o,abs(t-tb)/.1)
    return o
def ik(s,t,l1,l2,sign):
    dx,dy=t[0]-s[0],t[1]-s[1]; dist=max(1,min(math.hypot(dx,dy),l1+l2-1))
    a=math.atan2(dy,dx); b=math.acos(cl((l1*l1+dist*dist-l2*l2)/(2*l1*dist),-1,1))
    return (s[0]+l1*math.cos(a+sign*b), s[1]+l1*math.sin(a+sign*b)),(s[0]+dist*math.cos(a), s[1]+dist*math.sin(a))

LIGHT=(255,234,184); SHADE=(78,52,70)
CH=(182,118,98); CARD=(112,138,118); SKA=(234,192,162); SKN=(244,206,178)
HAIR=(78,50,40); DRESS=(102,156,162); WHITE=(246,242,234); WOC=(176,162,152); CREAM=(250,240,222)

def curtain(d,xa,xb,t,flip=1):
    s=7*math.sin(t*.9)*flip; top=400; bot=862; c=(228,190,170)
    L=bez((xa,top),(xa+10*flip+s*.4,630),(xa-14*flip+s,bot)); R=bez((xb,top),(xb+6*flip+s*.5,630),(xb+22*flip+s,bot))
    poly(d,L+R[::-1],c,2,(186,146,130))
    for k in (.25,.5,.75):
        pts=[lerp(L[i],R[i],k) for i in range(len(L))]
        curve(d,pts,3,mix(c,(150,100,90),.35)); curve(d,[(p[0]+5,p[1]) for p in pts],3,mix(c,(255,255,255),.3))
    curve(d,[(L[-1][0],bot-10),(R[-1][0],bot-10)],4,(246,226,200))

def build_bg():
    rnd=random.Random(7)
    im=Image.new("RGB",(W*SS,H*SS)); d=ImageDraw.Draw(im)
    for y in range(FLOOR): d.rectangle([0,y*SS,W*SS,(y+1)*SS],fill=mix((238,218,190),(224,192,158),y/FLOOR))
    for x in range(0,W,64):
        d.rectangle([x*SS,0,(x+30)*SS,FLOOR*SS],fill=None)
        for y in range(40,1110,74):
            c=mix((238,218,190),(224,192,158),y/FLOOR)
            xx=x+16+(32 if (y//74)%2 else 0)
            poly(d,[(xx,y-7),(xx+5,y),(xx,y+7),(xx-5,y)],mix(c,(255,250,236),.5)); circ(d,(xx,y+18),1.8,mix(c,(196,150,120),.5))
    # zocalo de madera
    rrect(d,(0,1120,W,FLOOR),0,(214,176,138)); rrect(d,(0,1112,W,1128),0,(196,156,118)); rrect(d,(0,1126,W,1130),0,(170,130,98))
    for x in range(0,W,92):
        rrect(d,(x+10,1146,x+82,1280),8,(204,164,126)); rrect(d,(x+14,1150,x+78,1276),6,(220,184,146))
    rrect(d,(0,FLOOR-30,W,FLOOR),0,(190,150,114)); rrect(d,(0,FLOOR-32,W,FLOOR-27),0,(166,126,94))
    # suelo
    ys=[FLOOR,FLOOR+48,FLOOR+112,FLOOR+192,FLOOR+292,FLOOR+412,H]
    for i in range(6):
        y0,y1=ys[i],ys[i+1]; x=-rnd.randint(0,300)
        while x<W:
            w=rnd.randint(260,520); base=mix((176,128,92),(140,98,70),(y0-FLOOR)/(H-FLOOR)); c=mix(base,(110,70,48) if rnd.random()<.5 else (214,170,126),rnd.random()*.16)
            d.rectangle([_p((x,y0)),_p((x+w,y1))],fill=c)
            for _ in range(rnd.randint(2,4)):
                gy=rnd.uniform(y0+6,y1-6); gx=rnd.uniform(x+10,x+w-120); gl=rnd.uniform(60,200)
                curve(d,bez((gx,gy),(gx+gl/2,gy+rnd.uniform(-5,5)),(gx+gl,gy)),1.6,mix(c,(96,60,40),.35))
            if rnd.random()<.3: ell(d,(rnd.uniform(x+30,x+w-30),(y0+y1)/2),7,4,mix(c,(96,60,40),.4))
            d.line([_p((x+w,y0)),_p((x+w,y1))],fill=mix(c,(80,50,36),.55),width=4); x+=w
        d.line([_p((0,y0)),_p((W,y0))],fill=(118,80,58),width=4)
    # ventana
    x0,y0,x1,y1=130,440,410,820
    rrect(d,(x0-24,y0-24,x1+24,y1+24),10,CREAM,3,(190,160,130)); rrect(d,(x0-6,y0-6,x1+6,y1+6),4,(200,170,140))
    for y in range(y0,y1): d.rectangle([_p((x0,y)),_p((x1,y+1))],fill=mix((70,78,132),(240,178,138),((y-y0)/(y1-y0))**1.5))
    for r,k in ((60,.10),(44,.16),(32,.26)): circ(d,(340,520),r,mix((98,104,152),(252,244,214),k))
    circ(d,(340,520),23,(252,246,220)); circ(d,(332,514),5,(236,228,200)); circ(d,(348,528),3.5,(236,228,200))
    for _ in range(26):
        sx,sy=rnd.uniform(x0+6,x1-6),rnd.uniform(y0+6,y0+230); circ(d,(sx,sy),rnd.choice((1.4,1.8,2.6)),(250,244,222))
    for cx,cy,rw in ((200,610,60),(250,622,46),(330,650,54)): ell(d,(cx,cy),rw,13,(170,140,170))
    poly(d,[(x0,y1),(x0,728),(190,690),(250,730),(310,700),(370,740),(x1,716),(x1,y1)],(124,112,140))
    poly(d,[(x0,y1),(x0,770),(220,745),(300,778),(x1,756),(x1,y1)],(96,90,118))
    for hx,hy in ((180,772),(196,776),(330,780),(352,774),(266,790)): rrect(d,(hx,hy,hx+5,hy+6),1,(250,214,130))
    poly(d,[(x0+30,y0),(x0+70,y0),(x0+10,y0+150),(x0,y0+150),(x0,y0+90)],mix((90,98,146),(255,255,255),.10))
    rrect(d,(x0+134,y0,x0+146,y1),0,CREAM); rrect(d,(x0,y0+176,x1,y0+188),0,CREAM)
    rrect(d,(x0+134,y0,x0+137,y1),0,(214,190,160)); rrect(d,(x0,y0+185,x1,y0+188),0,(214,190,160))
    rrect(d,(x0-44,y1+22,x1+44,y1+46),8,(244,230,208),3,(190,160,130)); rrect(d,(x0-36,y1+46,x1+36,y1+54),3,(206,176,146))
    # maceta en el alféizar
    rrect(d,(160,y1-14,204,y1+24),6,(198,128,104),2.5); 
    for a,l in ((-.7,44),(-.2,56),(.4,48),(.9,36)):
        tip=(182+l*math.sin(a),y1-14-l*math.cos(a)); curve(d,[(182,y1-14),tip],3,(96,128,100)); ell(d,tip,9,14,(118,150,116),2)
    curtain(d,84,170,0,-1)
    rrect(d,(60,388,480,402),7,(140,100,76),2.5); circ(d,(56,395),13,(140,100,76),2.5); circ(d,(484,395),13,(140,100,76),2.5)
    # dibujo de la niña pegado en la pared
    P=lambda p:rot(p,(535,720),-.06)
    poly(d,[P((480,655)),P((590,655)),P((590,790)),P((480,790))],(252,248,238),2,(200,180,160))
    poly(d,[P((505,740)),P((565,740)),P((565,775)),P((505,775))],(226,150,130)); poly(d,[P((498,740)),P((535,708)),P((572,740))],(150,120,170))
    circ(d,P((566,682)),11,(244,200,110)); curve(d,[P((486,778)),P((584,778))],4,(130,170,120))
    poly(d,[P((520,648)),P((552,648)),P((552,664)),P((520,664))],(236,214,150))
    # repisa
    rrect(d,(560,612,884,630),4,(150,108,82),2.5); poly(d,[(590,630),(606,630),(590,660)],(128,92,70)); poly(d,[(840,630),(856,630),(856,660)],(128,92,70))
    bx=578
    for w,h,c in ((28,100,(156,118,110)),(20,116,(104,134,142)),(32,90,(210,172,110)),(24,108,(174,128,120)),(28,96,(118,132,112)),(18,86,(200,150,132))):
        rrect(d,(bx,612-h,bx+w,612),3,c,2); rrect(d,(bx+3,612-h+14,bx+w-3,612-h+20),1,mix(c,(255,255,255),.45)); rrect(d,(bx+3,612-22,bx+w-3,612-18),1,mix(c,(0,0,0),.25)); bx+=w+3
    poly(d,[(bx+6,612),(bx+30,612),(bx+62,520),(bx+38,514)],(150,130,160),2)
    rrect(d,(800,560,856,612),5,(204,146,118),2.5); rrect(d,(796,556,860,570),5,(216,160,130),2.5)
    for a,l in ((-.9,50),(-.4,70),(.1,80),(.6,64),(1.0,46)):
        tip=(828+l*math.sin(a),556-l*math.cos(a)); curve(d,bez((828,556),(828+l*.2*math.sin(a),556-l*.7),tip),3.5,(92,124,98)); ell(d,tip,10,16,(116,148,114),2)
    # lampara
    cap(d,(905,640),(905,800),8,(110,84,68),2); circ(d,(905,652),8,(196,160,96),2)
    poly(d,[(838,772),(972,772),(944,664),(866,664)],(250,224,164),2.5,(190,150,100))
    poly(d,[(840,764),(970,764),(972,772),(838,772)],(226,180,120)); poly(d,[(866,664),(944,664),(946,672),(864,672)],(226,180,120))
    cap(d,(930,772),(930,806),2,(150,120,90)); circ(d,(930,810),4,(196,160,96))
    # alfombra
    ell(d,(520,1446),478,104,(176,130,114)); ell(d,(520,1444),470,100,(190,146,128)); ell(d,(520,1444),430,84,(206,170,150)); ell(d,(520,1444),410,76,(196,154,136))
    for i in range(44):
        a=i/44*2*math.pi; circ(d,(520+420*math.cos(a),1444+80*math.sin(a)),3.2,(236,214,190))
    ell(d,(520,1444),250,40,(206,170,150)); ell(d,(520,1444),236,34,(196,154,136))
    for sx in (-1,1):
        for k in range(-5,6): cap(d,(520+sx*466,1444+k*8),(520+sx*(484-abs(k)),1444+k*9),2.5,(226,200,176))
    # sillon
    for lx in (628,946): rrect(d,(lx,1288,lx+32,1350),8,(100,72,58),2.5)
    rrect(d,(655,796,992,1272),66,CH,3); rrect(d,(684,826,964,1164),52,mix(CH,(0,0,0),.07)); 
    curve(d,bez((690,1000),(690,836),(830,832)),3,mix(CH,(255,255,255),.2))
    for bx_,by_ in ((760,900),(880,900),(820,1000),(760,1100),(880,1100)): circ(d,(bx_,by_),7,mix(CH,(0,0,0),.25)); circ(d,(bx_-1.5,by_-1.5),3,mix(CH,(255,255,255),.15))
    rrect(d,(605,1150,992,1304),42,mix(CH,(0,0,0),.1),3); curve(d,[(640,1176),(960,1176)],3,mix(CH,(0,0,0),.25))
    # manta tejida sobre el respaldo
    poly(d,[(872,790),(996,800),(1000,960),(900,930)],(226,196,150),2.5,(170,130,96))
    for k in range(1,6):
        a=lerp((872,790),(900,930),k/6); b=lerp((996,800),(1000,960),k/6); curve(d,[a,b],5,(196,128,104) if k%2 else (120,146,140))
    for k in range(9): a=lerp((900,930),(1000,960),k/8); cap(d,a,(a[0]-2,a[1]+14),3,(226,196,150))
    # luz
    g=Image.new("RGB",(W//8,H//8)); gd=ImageDraw.Draw(g)
    gd.ellipse([(905-400)//8,(770-400)//8,(905+400)//8,(770+400)//8],fill=(92,64,30))
    gd.ellipse([(905-150)//8,(730-150)//8,(905+150)//8,(730+150)//8],fill=(96,70,36))
    gd.ellipse([(270-190)//8,(640-250)//8,(270+190)//8,(640+250)//8],fill=(22,20,34))
    gd.polygon([(120//8,860//8),(430//8,860//8),(560//8,1500//8),(60//8,1500//8)],fill=(10,10,22))
    g=g.filter(ImageFilter.GaussianBlur(20)).resize(im.size,Image.BICUBIC); im=ImageChops.add(im,g)
    v=Image.new("L",(W//8,H//8),0); vd=ImageDraw.Draw(v); vd.ellipse([-36,-6,W//8+36,H//8+6],fill=255)
    v=v.filter(ImageFilter.GaussianBlur(34)).resize(im.size,Image.BICUBIC)
    return Image.composite(im,Image.eval(im,lambda p:int(p*.68)),v)

def layer(box):
    global OX,OY
    OX,OY=box[0],box[1]
    L=Image.new("RGBA",((box[2]-box[0])*SS,(box[3]-box[1])*SS),(0,0,0,0)); return L,ImageDraw.Draw(L)
def put(im,L,box,cast=None,mirror=False,scale=1.0,at=None,shade=True):
    global OX,OY
    if mirror: L=ImageOps.mirror(L)
    if scale!=1.0: L=L.resize((max(1,int(L.width*scale)),max(1,int(L.height*scale))),Image.LANCZOS)
    a=L.getchannel("A"); pos=(int(box[0]*SS),int(box[1]*SS)) if at is None else (int(at[0]*SS),int(at[1]*SS))
    k=SS/2
    if cast:
        sil=ImageChops.offset(a,int(cast[0]*k),int(cast[1]*k)).filter(ImageFilter.GaussianBlur(cast[2]*k)).point(lambda v:int(v*cast[3]))
        im.paste((44,28,34),pos,sil)
    rgb=L.convert("RGB")
    if shade:
        hl=ImageChops.subtract(a,ImageChops.offset(a,int(-9*k),int(7*k))).filter(ImageFilter.GaussianBlur(3*k)).point(lambda v:int(v*.5))
        sh=ImageChops.subtract(a,ImageChops.offset(a,int(15*k),int(-9*k))).filter(ImageFilter.GaussianBlur(5*k)).point(lambda v:int(v*.3))
        rgb=Image.composite(Image.new("RGB",L.size,LIGHT),rgb,hl)
        rgb=Image.composite(Image.new("RGB",L.size,SHADE),rgb,sh)
    im.paste(rgb,pos,a); OX=OY=0

def hand(d,h,u,sk,spread=.16,fl=17):
    ang=math.atan2(u[1],u[0])
    for k in (-1.5,-.5,.5,1.5):
        a=ang+k*spread; b=(h[0]+10*math.cos(ang)-k*9*math.sin(ang),h[1]+10*math.sin(ang)+k*9*math.cos(ang))
        cap(d,b,(b[0]+fl*math.cos(a),b[1]+fl*math.sin(a)),10.5,sk,2)
    tb=(h[0]-4*math.cos(ang)+20*math.sin(ang),h[1]-4*math.sin(ang)-20*math.cos(ang))
    cap(d,tb,(tb[0]+12*math.cos(ang-.5),tb[1]+12*math.sin(ang-.5)),11,sk,2)
    circ(d,h,23,sk,2)
    for k in (-1.5,-.5,.5,1.5):
        b=(h[0]+10*math.cos(ang)-k*9*math.sin(ang),h[1]+10*math.sin(ang)+k*9*math.cos(ang)); circ(d,b,6,sk)

def chair_front(d):
    c=mix(CH,(255,255,255),.1)
    rrect(d,(630,1078,968,1144),33,c,3); rrect(d,(630,1078,708,1304),34,c,3); rrect(d,(634,1082,964,1140),30,c)
    curve(d,[(662,1098),(934,1098)],4,mix(c,(255,255,255),.16)); curve(d,[(700,1140),(950,1140)],3,mix(c,(0,0,0),.2))
    ring(d,(669,1116),26,26,3,mix(c,(0,0,0),.2)); ring(d,(669,1116),12,12,3,mix(c,(0,0,0),.2))
    curve(d,[(648,1160),(648,1280)],3,mix(c,(255,255,255),.14))

def cat(d,t,x):
    c0=(362,1492); br=1+.03*math.sin(t*1.9); CT=(224,164,108); near=math.exp(-((x-362)/90)**2)
    fl=math.sin(t*5)*near*14
    tail=bez((447,1500),(462,1540+fl*.2),(362,1536))+bez((362,1536),(302,1534),(276+fl*.3,1508-fl))[1:]
    curve(d,tail,26,OC(CT)); curve(d,tail,21,CT); circ(d,tail[-1],9,CREAM)
    ell(d,c0,96,48*br,CT,OW)
    for k in (-40,-8,24,54): curve(d,bez((c0[0]+k,c0[1]-44*br+abs(k)*.12),(c0[0]+k+10,c0[1]-26),(c0[0]+k+4,c0[1]-8)),6,mix(CT,(150,90,50),.5))
    h=(294,1486+1.5*math.sin(t*1.9)); tw=near*math.sin(t*9)*.25
    for sg in (-1,1):
        b=(h[0]+sg*20,h[1]-24); tipp=rot((h[0]+sg*30,h[1]-50),b,sg*tw)
        poly(d,[(b[0]-12,b[1]+4),tipp,(b[0]+13,b[1]+6)],CT,OW); poly(d,[(b[0]-5,b[1]+2),lerp(b,tipp,.7),(b[0]+6,b[1]+3)],(238,170,150))
    circ(d,h,34,CT,OW); ell(d,(h[0],h[1]+12),18,13,CREAM)
    for sg in (-1,1):
        smile(d,(h[0]+sg*14,h[1]-2),7,4,3,(70,44,38))
        for k in (-1,0,1): curve(d,[(h[0]+sg*16,h[1]+12+k*2),(h[0]+sg*44,h[1]+10+k*7)],1.4,(250,240,226))
    poly(d,[(h[0]-4,h[1]+7),(h[0]+4,h[1]+7),(h[0],h[1]+12)],(226,130,124)); curve(d,[(h[0]-6,h[1]+17),(h[0],h[1]+13),(h[0]+6,h[1]+17)],2,(110,70,60))
    for k in (-8,4,16): curve(d,[(h[0]+k-4,h[1]-30),(h[0]+k,h[1]-18)],4,mix(CT,(150,90,50),.5))
    ell(d,(332,1528),22,11,CREAM,2.5,OC(CT))


# ======================= personajes parametrizados =======================
def set_ss(n):
    global SS
    SS=n
_BG={}
def sala():
    k=("sala",SS)
    if k not in _BG: _BG[k]=build_bg()
    return _BG[k]

def hand(d,h,u,sk,spread=.16,fl=17,k=1.0,o=2):
    ang=math.atan2(u[1],u[0])
    def fb(q): return (h[0]+10*k*math.cos(ang)-q*9*k*math.sin(ang),h[1]+10*k*math.sin(ang)+q*9*k*math.cos(ang))
    for q in (-1.5,-.5,.5,1.5):
        a=ang+q*spread; b=fb(q); cap(d,b,(b[0]+fl*k*math.cos(a),b[1]+fl*k*math.sin(a)),10.5*k,sk,o)
    tb=(h[0]-4*k*math.cos(ang)+20*k*math.sin(ang),h[1]-4*k*math.sin(ang)-20*k*math.cos(ang))
    cap(d,tb,(tb[0]+12*k*math.cos(ang-.5),tb[1]+12*k*math.sin(ang-.5)),11*k,sk,o)
    circ(d,h,23*k,sk,o)
    for q in (-1.5,-.5,.5,1.5): circ(d,fb(q),6*k,sk)

def lia_walk(t,T=5.0,x0=-110,x1=475):
    u=cl(t/T); e=1-(1-u)**1.7; x=x0+(x1-x0)*e
    speed=(x1-x0)*1.7*(1-u)**.7/T if u<1 else 0
    amp=cl(speed/120); ph=x/78*math.pi
    return dict(x=x,amp=amp,
        legs=[(.5*math.sin(ph+o)*amp,.95*max(0,math.cos(ph+o))*amp) for o in (math.pi,0)],
        arms=[(-.55*sg*math.sin(ph)*amp+.04,.35+.25*amp) for sg in (-1,1)],
        sw=7*math.sin(ph*2-.6)*amp, pig=(-.35-.3*math.sin(ph*2-1.2)*amp,.15-.25*math.sin(ph*2-2.0)*amp),
        tilt=.05*math.sin(ph)*amp, bobh=2*math.sin(ph*2)*amp)

def lia(d,x,hy=None,legs=((0,0),(0,0)),arms=((.04,.35),(.04,.35)),sw=0,tilt=0,look=(0,0),op=1,happy=0,smv=.5,
        pig=(-.35,.15),bobh=0,amp=0,brow=0,item=None,t=0,tip=0,dress=DRESS):
    L=[]; brow=0
    for th,kn in legs:
        knee=(72*math.sin(th),72*math.cos(th)); a2=th-kn
        L.append((knee,(knee[0]+72*math.sin(a2),knee[1]+72*math.cos(a2))))
    if hy is None: hy=GY-22-max(l[1][1] for l in L)-tip-1.5*math.sin(t*1.6)*(1-amp)
    sy=hy-138; hands=[]
    def draw_arm(i,dk):
        a,bend=arms[i]; s=(x+2,sy+24); el=(s[0]+54*math.sin(a),s[1]+54*math.cos(a)); a2=a+bend
        hd=(el[0]+50*math.sin(a2),el[1]+50*math.cos(a2)); sk=mix(SKN,(0,0,0),dk)
        limb(d,[s,el,hd],[23,21],sk); circ(d,hd,12.5,sk,OW)
        circ(d,(hd[0]+11*math.sin(a2+1.2),hd[1]+11*math.cos(a2+1.2)),5.5,sk,2); circ(d,hd,12,sk)
        dc=mix(dress,(0,0,0),dk); circ(d,lerp(s,el,.18),21,dc,OW)
        pm=lerp(s,el,.48); pr=(math.cos(a)*15,-math.sin(a)*15)
        cap(d,(pm[0]-pr[0],pm[1]-pr[1]),(pm[0]+pr[0],pm[1]+pr[1]),8,WHITE,2,WOC); hands.append(hd)
    def draw_leg(i,dk):
        knee,ank=L[i]; hp=(x+(-8 if i==0 else 8),hy); K=(hp[0]+knee[0],hp[1]+knee[1]); A=(hp[0]+ank[0],hp[1]+ank[1]); sk=mix(SKN,(0,0,0),dk)
        limb(d,[hp,K,A],[30,26],sk)
        sw_=mix(WHITE,(0,0,0),dk); m=lerp(K,A,.5)
        limb(d,[m,A],[27],sw_,OW,WOC); cap(d,lerp(K,A,.46),lerp(K,A,.54),30,sw_,2,WOC)
        sc=mix((132,78,74),(0,0,0),dk); f=(A[0]+13,A[1]+11)
        ell(d,(f[0],f[1]+3),30,13,OC(sc,.6)); ell(d,f,29,13,sc,OW); ell(d,(f[0]+10,f[1]-4),9,4,mix(sc,(255,255,255),.3))
        curve(d,bez((A[0]-12,A[1]+2),(A[0]+2,A[1]-6),(A[0]+14,A[1]+3)),5,sc); circ(d,(A[0]+12,A[1]+2),3,(226,190,120))
    draw_arm(0,.14); draw_leg(0,.12); draw_leg(1,0)
    hemL,hemR=(x-76+sw,hy+38),(x+76+sw,hy+38)
    cap(d,(x,sy+26),(x,hy-20),82,dress,OW)
    sk_=[(x-42,hy-72)]+bez((x-42,hy-72),(x-52,hy-10),hemL)[1:]+bez(hemL,(x+sw,hy+50),hemR)[1:]+bez(hemR,(x+52,hy-10),(x+42,hy-72))[1:]
    poly(d,sk_,dress,OW)
    for fx_ in (-.5,-.05,.45):
        a_=(x+fx_*60,hy-60); b_=(x+fx_*150+sw,hy+34); curve(d,bez(a_,lerp(a_,b_,.5),b_),3,mix(dress,(0,0,0),.16))
    curve(d,bez((hemL[0]+3,hemL[1]-10),(x+sw,hy+40),(hemR[0]-3,hemR[1]-10)),6,mix(dress,(255,255,255),.5))
    for px_,py_ in ((-34,-30),(6,-36),(38,-22),(-12,-4),(26,6),(-46,6),(52,12),(4,18)):
        circ(d,(x+px_+sw*(py_+72)/110,hy+py_),3.6,mix(dress,(255,255,255),.42))
    cap(d,(x-40,hy-72),(x+40,hy-72),11,mix(dress,(0,0,0),.22))
    for k in range(3): circ(d,(x+8,sy+44+k*22),4,CREAM,1.5,(150,130,110))
    cap(d,(x+2,sy+8),(x+4,sy-18),34,mix(SKN,(190,120,100),.2),OW)
    ell(d,(x-14,sy+12),24,12,WHITE,2.5,WOC); ell(d,(x+26,sy+12),22,12,WHITE,2.5,WOC)
    draw_arm(1,0)
    if item=="cuaderno":
        h=hands[1]; P_=lambda p:rot((h[0]+p[0],h[1]+p[1]),h,-.25)
        poly(d,[P_((-8,-30)),P_((44,-30)),P_((44,36)),P_((-8,36))],(232,186,104),OW); poly(d,[P_((-8,-30)),P_((2,-30)),P_((2,36)),P_((-8,36))],(196,120,100))
        poly(d,[P_((10,-12)),P_((36,-12)),P_((36,4)),P_((10,4))],CREAM); circ(d,(h[0]+2,h[1]+2),10,SKN,2)
    hx=x+10+3*amp; hyy=sy-64+bobh
    C=(hx,hyy); F=lambda p:rot((hx+p[0],hyy+p[1]),C,tilt)
    root=F((-72,0)); mid=(root[0]+46*math.sin(pig[0]),root[1]+46*math.cos(pig[0])); pa2=pig[0]+pig[1]
    end=(mid[0]+40*math.sin(pa2),mid[1]+40*math.cos(pa2))
    limb(d,[root,mid,end],[44,30],HAIR,OW,(46,28,24)); curve(d,[lerp(root,mid,.3),mid,lerp(mid,end,.7)],4,(118,82,64))
    circ(d,C,81,HAIR,OW,(46,28,24))
    ell(d,F((10,10)),65,62,SKN)
    ell(d,F((16,-52)),60,25,HAIR); ell(d,F((-32,-28)),30,44,HAIR); ell(d,F((68,-22)),10,26,HAIR)
    for a_,b_ in (((-20,-34),(-6,-28)),((14,-32),(30,-27)),((44,-34),(56,-26))): poly(d,[F(a_),F((a_[0]+16,a_[1])),F(b_)],HAIR)
    curve(d,bez(F((-46,-56)),F((0,-80)),F((48,-58))),6,(124,86,66)); curve(d,bez(F((-58,-30)),F((-66,-6)),F((-60,18))),4,(110,76,58))
    for sgn in (-1,1): poly(d,[root,(root[0]+sgn*24,root[1]-14),(root[0]+sgn*24,root[1]+14)],(230,182,96),2,(150,110,60))
    circ(d,root,8,(240,198,112),2,(150,110,60))
    lx,ly=look
    for ex in (-12,34):
        c=F((ex+lx*.6,6+ly*.6)); ck=F((ex-22 if ex<0 else ex+18,32+ly*.4))
        circ(d,ck,15,mix(SKN,(238,150,138),.32+.15*happy)); circ(d,ck,9,mix(SKN,(238,146,134),.55+.2*happy))
        b=F((ex+lx,-20+ly-4*brow)); smile(d,b,11,-4-2*brow,4,HAIR)
        if happy>.5: smile(d,(c[0],c[1]+5),11,-9,5,(60,40,34))
        elif op<.45: smile(d,(c[0],c[1]+2),11,4,5,(60,40,34))
        else:
            ell(d,c,10.5,13*op,(255,253,248),1.5,(120,84,70))
            p=(c[0]+lx*.5,c[1]+ly*.5+1); ell(d,p,8.5,min(9.5,13*op),(110,70,50)); ell(d,p,5,min(5.5,12*op),(44,28,26))
            circ(d,(p[0]+3.5,p[1]-4.5),3.2,(255,255,255)); circ(d,(p[0]-3,p[1]+3.5),1.6,(255,255,255))
            curve(d,arcpts((c[0],c[1]-13*op+1),11,-3),4,(54,34,30))
            sg=-1 if ex<0 else 1; curve(d,[(c[0]+sg*11,c[1]-11*op+3),(c[0]+sg*16,c[1]-13*op)],3,(54,34,30))
    curve(d,bez(F((16+lx,20+ly)),F((22+lx,24+ly)),F((16+lx,27+ly))),3,mix(SKN,(180,110,96),.6))
    mc=F((12+lx,36+ly*.5)); w_=9+9*smv; dp=1+11*smv
    if smv>.75:
        pts=arcpts(mc,w_,dp+3,tilt,mc); d.polygon([_p(p) for p in pts],fill=(146,62,62)); ell(d,(mc[0],mc[1]+dp-1),7,4,(232,134,128)); curve(d,pts+[pts[0]],3.5,(112,50,50))
    elif smv<0: ell(d,mc,6,5,(146,62,62),2,(112,50,50))
    else: smile(d,mc,w_,dp,5,(150,80,74),tilt,mc)
    return dict(top=(hx-4,hyy-80),C=C,hands=hands,hy=hy,sy=sy)

def libro(d,bc,ba,t=0,flip=False,k=1.0,ribbon=True):
    R=lambda p:rot((bc[0]+p[0]*k,bc[1]+p[1]*k),bc,ba)
    poly(d,[R((-60,-40)),R((66,-40)),R((66,50)),R((-60,50))],(246,238,220),2.5*k,(170,150,130))
    for q in (0,3,6): curve(d,[R((-56,44+q)),R((62,44+q))],1.2*k,(196,180,160))
    BK=(96,122,156)
    poly(d,[R((-64,-46)),R((62,-46)),R((62,44)),R((-64,44))],BK,OW*k)
    poly(d,[R((-64,-46)),R((-52,-46)),R((-52,44)),R((-64,44))],mix(BK,(0,0,0),.22))
    poly(d,[R((-40,-36)),R((52,-36)),R((52,34)),R((-40,34))],mix(BK,(255,255,255),.12))
    s=-1 if flip else 1; cx,cy=6,(0 if flip else 4); FO=(226,138,84)
    G=lambda p:R((cx+s*p[0],cy+s*p[1]))
    poly(d,[G((-24,-10)),G((24,-10)),G((0,24))],FO,2*k)
    poly(d,[G((-26,-30)),G((-8,-10)),G((-26,-8))],FO,2*k); poly(d,[G((26,-30)),G((8,-10)),G((26,-8))],FO,2*k)
    poly(d,[G((-12,6)),G((12,6)),G((0,24))],CREAM); circ(d,G((0,22)),3.5*k,(60,40,36))
    circ(d,G((-10,-2)),2.5*k,(60,40,36)); circ(d,G((10,-2)),2.5*k,(60,40,36))
    yb=-30 if flip else 30
    curve(d,[R((-30,-yb)),R((40,-yb))],3*k,(236,206,140))
    if ribbon:
        rb=R((30,50)); sway=6*math.sin(t*1.8); curve(d,bez(rb,(rb[0]+sway*.4,rb[1]+16*k),(rb[0]+sway,rb[1]+30*k)),5*k,(206,120,100))

def abuelo_base(d,t,lift=0,sma=0,low=0,talk=0,eye=(0,0),brow=0,op=None,book=True,flip=False,bc=None,ba=None,pocket=False,nod=0,far=None,look_dx=0):
    br=math.sin(t*1.5)*2
    TR=(110,102,104)
    for knee,foot,dk in (((608,1168),(602,1318),.16),((584,1172),(574,1322),0)):
        c=mix(TR,(0,0,0),dk); sc=mix((158,100,88),(0,0,0),dk)
        limb(d,[(790,1170),knee,foot],[62,50],c)
        curve(d,[(knee[0]-6,knee[1]+30),(foot[0]-8,foot[1]-24)],2.5,mix(c,(255,255,255),.18))
        cap(d,(foot[0]-2,foot[1]-6),(foot[0]-2,foot[1]+2),50,mix((214,176,110),(0,0,0),dk),2)
        f=(foot[0]-22,foot[1]+16); ell(d,(f[0],f[1]+5),44,15,OC(sc,.65)); ell(d,f,43,17,sc,OW)
        for q in (-18,0,18): curve(d,[(f[0]+q-6,f[1]-14),(f[0]+q+4,f[1]+14)],2.5,mix(sc,(255,230,200),.35))
        curve(d,[(f[0]-36,f[1]),(f[0]+36,f[1])],2.5,mix(sc,(255,230,200),.35))
        cap(d,(f[0]+14,f[1]-14),(f[0]+40,f[1]-10),12,mix(CREAM,(0,0,0),dk),2,WOC)
    cap(d,(785,1165),(770,985-br),150,CARD,OW)
    for q in range(-2,4): curve(d,[(770+q*22,960-br+abs(q)*6),(782+q*24,1200)],2,mix(CARD,(255,255,255),.1))
    cap(d,(758,940-br),(750,905-br),46,mix(SKA,(0,0,0),.09),OW)
    poly(d,[(708,930-br),(764,922-br),(744,1016-br)],WHITE,2.5,WOC)
    poly(d,[(704,926-br),(736,930-br),(722,962-br)],WHITE,2.5,WOC); poly(d,[(770,920-br),(742,930-br),(760,960-br)],WHITE,2.5,WOC)
    curve(d,bez((704,936-br),(716,990-br),(744,1022-br)),11,mix(CARD,(0,0,0),.2)); curve(d,bez((774,926-br),(772,980-br),(746,1022-br)),11,mix(CARD,(0,0,0),.2))
    curve(d,bez((744,1022-br),(738,1100),(742,1200)),3,mix(CARD,(0,0,0),.3))
    for q in range(3): circ(d,(736,1046+q*42-br*(1-q/3)),6.5,(150,104,78),2); circ(d,(734,1044+q*42-br*(1-q/3)),2,(110,74,56))
    if pocket:
        poly(d,[(786,1032),(812,1024),(820,1060),(790,1066)],(252,248,236),2,(180,160,140)); curve(d,[(794,1040),(808,1036)],1.6,(120,110,120)); curve(d,[(796,1048),(812,1044)],1.6,(120,110,120))
        curve(d,bez((776,1058),(802,1068),(830,1052)),4,mix(CARD,(0,0,0),.3)); curve(d,bez((778,1060),(784,1100),(806,1104)),3,mix(CARD,(0,0,0),.25)); curve(d,bez((830,1054),(832,1090),(806,1104)),3,mix(CARD,(0,0,0),.25))
    if bc is None: bc=(640,1000+50*low-br*.5)
    if ba is None: ba=.28-.5*low
    fh=far if far else (bc[0]+36,bc[1]+30); s2=(772,990-br)
    e,h=ik(s2,fh,120,120,-1); dc=mix(CARD,(0,0,0),.15)
    limb(d,[s2,e,h],[54,48],dc)
    if book: libro(d,bc,ba,t,flip)
    cap(d,lerp(e,h,.84),h,50,mix(dc,(255,255,255),.2),2)
    hand(d,(h[0]-6,h[1]+4),(-.9,-.45),mix(SKA,(0,0,0),.08),.14,14)
    # cabeza
    C=(746-6*lift+look_dx,852+9*(1-lift)-br*.6+math.sin(t*2.1)*1.2*(1-lift)+nod)
    tilt=-.2*(1-lift)
    F=lambda p:rot((C[0]+p[0],C[1]+p[1]),C,tilt)
    circ(d,F((12,6)),84,WHITE,OW,WOC); circ(d,C,80,SKA,OW)
    for p_,rx,ry in (((58,-34),22,24),((66,-6),24,26),((60,24),22,24),((44,44),20,18)): ell(d,F(p_),rx,ry,WHITE,2.5,WOC)
    for p_,rx,ry in (((54,-30),20,22),((60,-6),22,24),((54,22),20,22)): ell(d,F(p_),rx,ry,WHITE)
    ell(d,F((44,12)),13,20,mix(SKA,(0,0,0),.08),2.5); curve(d,bez(F((40,4)),F((50,12)),F((42,22))),2.5,mix(SKA,(150,90,80),.5))
    fx=-22-6*lift; fy=16*(1-lift)+6*lift
    if op is None: op=1
    wr=mix(SKA,(170,110,96),.45)
    for q in (0,1): curve(d,bez(F((-44+fx*.5,-52+q*12+fy*.4)),F((-10+fx*.5,-58+q*12+fy*.4-3*brow)),F((24+fx*.5,-52+q*12+fy*.4))),2.5,wr)
    eyes=[F((-36+fx,-8+fy)),F((18+fx,-8+fy))]
    for sx in (-56,40):
        ck=F((sx+fx*.6,28+fy*.5)); circ(d,ck,18,mix(SKA,(236,150,130),.12+.3*sma)); circ(d,ck,11,mix(SKA,(236,146,128),.2+.4*sma))
    for i,c in enumerate(eyes):
        ell(d,c,24,24,mix(SKA,(255,255,255),.22))
        if sma>.85 and op>.5: smile(d,(c[0],c[1]+3),10,-7,5,(64,46,40))
        elif op<.4: smile(d,(c[0],c[1]+1),9,3,4.5,(64,46,40))
        else:
            pc=(c[0]+eye[0],c[1]+eye[1]); ell(d,pc,7.5,9.5*op,(64,46,40)); circ(d,(pc[0]+2.5,pc[1]-3),2.4,(255,255,255))
        curve(d,[(c[0]-13,c[1]+13),(c[0]+2,c[1]+16)],2,wr)
        b=F(((-36,18)[i]+fx,-44+fy-8*brow-3*sma))
        bp=[(b[0]-17,b[1]+4),(b[0]-4,b[1]-4),(b[0]+16,b[1]+2)]; curve(d,bp,13,WOC); curve(d,bp,9,WHITE)
        curve(d,[(c[0]-14,c[1]-16),(c[0]-4,c[1]-21)],3,(255,252,240)); curve(d,[(c[0]+8,c[1]-18),(c[0]+13,c[1]-14)],2.5,(255,252,240))
        ring(d,c,27,27,4.5,(104,78,66))
    curve(d,bez((eyes[0][0]+26,eyes[0][1]-2),((eyes[0][0]+eyes[1][0])/2,eyes[0][1]-9),(eyes[1][0]-26,eyes[1][1]-2)),4.5,(104,78,66))
    curve(d,[(eyes[1][0]+27,eyes[1][1]-2),F((46,0))],4.5,(104,78,66))
    if sma>.3:
        for q in (-1,1): curve(d,[(eyes[1][0]+30,eyes[1][1]+10+q*5),(eyes[1][0]+38,eyes[1][1]+10+q*9)],2,wr)
    nz=F((-12+fx,16+fy)); ell(d,nz,16,13,mix(SKA,(214,140,120),.4)); curve(d,bez((nz[0]-14,nz[1]+2),(nz[0]-4,nz[1]+16),(nz[0]+12,nz[1]+6)),2.5,mix(SKA,(150,90,80),.55)); circ(d,(nz[0]-4,nz[1]-5),4,mix(SKA,(255,255,255),.35))
    mc=F((-12+fx,52+fy))
    if talk>.12:
        ell(d,(mc[0],mc[1]+3+4*talk),13+3*talk,3+11*talk,(118,54,54),2.5,(90,44,44)); ell(d,(mc[0],mc[1]+8+10*talk),8,3+2*talk,(214,120,116))
    else: smile(d,mc,16+9*sma,2+11*sma,5,(128,74,66),tilt,mc)
    curve(d,bez(F((-30+fx,74+fy*.6+8*talk)),F((-12+fx,80+fy*.6+10*talk)),F((6+fx,74+fy*.6+8*talk))),2.5,wr)
    for mx_,sg in ((-30,-1),(6,1)):
        m=F((mx_+fx,38+fy-2*talk)); ell(d,m,25,12,WHITE,2.5,WOC); ell(d,(m[0]+sg*18,m[1]+5),12,8,WHITE,2.5,WOC)
    for mx_,sg in ((-30,-1),(6,1)):
        m=F((mx_+fx,38+fy-2*talk)); ell(d,m,24,11,WHITE); ell(d,(m[0]+sg*18,m[1]+5),11,7,WHITE)
        for q in (-8,2,12): curve(d,[(m[0]+sg*q,m[1]-5),(m[0]+sg*(q+6),m[1]+6)],1.8,WOC)
    return bc,ba,br

def abuelo_arm(d,br,tg,dirv=None,spoon=False):
    s=(738,985-br); e,h=ik(s,tg,142,142,-1)
    limb(d,[s,e,h],[58,50],CARD)
    ell(d,(e[0]+4,e[1]-2),20,26,(150,110,84),2)
    cu=mix(CARD,(255,255,255),.22); cap(d,lerp(e,h,.84),lerp(e,h,.97),53,cu,2)
    ux,uy=h[0]-e[0],h[1]-e[1]; n=math.hypot(ux,uy) or 1
    for q in (.86,.9,.94):
        m=lerp(e,h,q); px,py=-uy/n*24,ux/n*24; curve(d,[(m[0]-px,m[1]-py),(m[0]+px,m[1]+py)],1.8,mix(cu,(0,0,0),.2))
    hc=(h[0]+ux/n*10,h[1]+uy/n*10)
    if spoon: cap(d,(hc[0]-6,hc[1]-30),(hc[0]-14,hc[1]+52),5,(200,196,190),1.5,(130,126,122))
    hand(d,hc,dirv or (ux,uy),SKA,.15,16)
    return hc
