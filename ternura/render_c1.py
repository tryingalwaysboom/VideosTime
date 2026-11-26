"""«La letra de mi abuelo» · Capítulo 1 — «El libro al revés». Animación por código (marionetas) 1080x1920, 30 fps.
Uso: python3 render_c1.py info | still T.. | part A B out.mp4"""
import os, sys, json, math, wave, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont
import rig as R
from rig import *
from guion_c1 import LINEAS
HERE=os.path.dirname(os.path.abspath(__file__)); VOZ=os.path.join(HERE,"voz_c1"); MF=os.path.join(HERE,"..","mateo-pov","fonts")
F_SUB=os.path.join(MF,"Andika-Bold.ttf"); F_HAND=os.path.join(MF,"Caveat.ttf"); F_SERIF="/usr/share/fonts/truetype/google-fonts/ofl/crimsontext/CrimsonText-Regular.ttf"
def wdur(l):
    with wave.open(os.path.join(VOZ,l+".wav")) as w: return w.getnframes()/w.getframerate()
GAP={"L01":.55,"L02":.5,"L03":.45,"L04":.6,"L05":.5,"L06":.45,"L07":.65,"L08":.55,"L09":.75,"L10":.9,"L11":.65,"L12":1.15,"L13":.75}
TL={}; _t=.45
for lid,v,txt in LINEAS:
    dd=wdur(lid); TL[lid]=(_t,_t+dd); _t+=dd+GAP.get(lid,.55)
TOTAL=float(math.ceil(TL["L14"][1]+2.4))
WORDS={l:json.load(open(os.path.join(VOZ,l+".json"),encoding="utf-8")) for l,_,_ in LINEAS}
def S(l): return TL[l][0]
def E(l): return TL[l][1]
def WI(l,i): return TL[l][0]+WORDS[l][i]["inicio"]
def WE(l,i): return TL[l][0]+WORDS[l][i]["fin"]
_ENV={}
def env(l,T):
    if l not in _ENV:
        with wave.open(os.path.join(VOZ,l+".wav")) as w: a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32); sr=w.getframerate()
        n=int(sr/FPS); r=np.array([np.sqrt(np.mean(a[i:i+n]**2)+1) for i in range(0,len(a),n)]); r=np.clip(r/np.percentile(r,88),0,1)
        r=np.convolve(r,[.25,.5,.25],mode="same"); _ENV[l]=r
    i=int((T-TL[l][0])*FPS); r=_ENV[l]
    return float(r[i]) if 0<=i<len(r) else 0.0

def cam(im,cx,cy,z):
    s=R.SS; w,h=W*s/z,H*s/z; x0=cl(cx*s-w/2,0,W*s-w); y0=cl(cy*s-h/2,0,H*s-h)
    return im.resize((W,H),Image.LANCZOS,box=(x0,y0,x0+w,y0+h))
def vgrad(d,x0,y0,x1,y1,c0,c1,p=1.0):
    for y in range(int(y0),int(y1)): d.rectangle([R._p((x0,y)),R._p((x1,y+1))],fill=mix(c0,c1,((y-y0)/max(1,y1-y0))**p))
def glow(im,spots,blur=20):
    g=Image.new("RGB",(W//8,H//8)); gd=ImageDraw.Draw(g)
    for kind,pts,col in spots:
        if kind=="e": gd.ellipse([pts[0]//8,pts[1]//8,pts[2]//8,pts[3]//8],fill=col)
        else: gd.polygon([(x//8,y//8) for x,y in pts],fill=col)
    return ImageChops.add(im,g.filter(ImageFilter.GaussianBlur(blur)).resize(im.size,Image.BICUBIC))
def vign(im,k=.7):
    v=Image.new("L",(W//8,H//8),0); ImageDraw.Draw(v).ellipse([-36,-6,W//8+36,H//8+6],fill=255)
    v=v.filter(ImageFilter.GaussianBlur(34)).resize(im.size,Image.BICUBIC)
    return Image.composite(im,Image.eval(im,lambda p:int(p*k)),v)
def mul(im,c): return ImageChops.multiply(im,Image.new("RGB",im.size,tuple(int(255*x) for x in c)))
MOTES=[(790+(i*53)%230,800+(i*97)%420,.3+(i%5)*.12,i*1.3) for i in range(16)]

# ------------------------------------------------ sala
def sala_frame(t,ab,lap=None,walk=None,arm=None,book_front=None,catx=-999):
    im=R.sala().copy(); d=ImageDraw.Draw(im)
    R.curtain(d,372,456,t,1)
    for mx,my,sp,p0 in MOTES:
        p=(mx+18*math.sin(t*sp+p0),my-12*(t%20)*sp+10*math.cos(t*sp*.7+p0)); circ(d,p,3.4,(252,226,170)); circ(d,p,1.8,(255,244,214))
    box=(480,730,1000,1380); L,ld=R.layer(box); bc,ba,br=R.abuelo_base(ld,t,**ab); R.put(im,L,box,(-18,14,12,.28))
    if lap:
        lp=dict(lap); dx=lp.pop("dx",0); dy=lp.pop("dy",0)
        box=(0,0,400,640); L,ld=R.layer(box); R.lia(ld,200,hy=470,t=t,**lp); R.put(im,L,box,(-10,8,10,.2),mirror=True,scale=.9,at=(590+dx-180,1140+dy-423))
    d=ImageDraw.Draw(im); R.chair_front(d)
    top=None
    if walk:
        x=walk["x"]; ell(d,(x+4,GY+8),88,13,(112,76,58)); ell(d,(x+4,GY+8),64,8,(96,64,50))
        box=(int(x)-190,880,int(x)+170,1410); L,ld=R.layer(box); top=R.lia(ld,t=t,**walk)["top"]; R.put(im,L,box,(-14,6,10,.14))
    if arm is not None or book_front:
        box=(360,740,860,1240); L,ld=R.layer(box)
        if book_front: R.libro(ld,book_front[0],book_front[1],t,book_front[2])
        tg=arm["tg"] if arm and "tg" in arm else (bc[0]-30,bc[1]+34)
        R.abuelo_arm(ld,br,tg,arm.get("dir") if arm else None); R.put(im,L,box,(-8,10,8,.2))
    d=ImageDraw.Draw(im); ell(d,(362,1540),120,14,(150,108,92))
    box=(232,1400,492,1570); L,ld=R.layer(box); R.cat(ld,t,catx); R.put(im,L,box)
    return im

def s01(t,T):
    R.set_ss(3); k=seg(T,WI("L01",11)-.1,WI("L01",11)+.5); u=sm(t/7)
    ab=dict(lift=.18,talk=max(0,math.sin(t*7.5))*.45*(1-.6*k),eye=(3*math.sin(t*1.4),2),book=False,far=(536,1126),op=blink(t,(1.6,4.4)))
    lap=dict(legs=((1.35,1.25+.12*math.sin(t*2)),(1.3,1.1-.12*math.sin(t*2))),arms=((1.2,.3),(1.0,.3)),look=(6-14*k,2-10*k),tilt=-.14*k,smv=.8-.65*k,brow=k,op=blink(t,(2.6,5.2)))
    im=sala_frame(t,ab,lap=lap,arm=dict(tg=(532,1120),dir=(-1,-.3)),book_front=((500,1082),.12,False))
    return cam(im,600+12*u,1005-20*u,1.5+.24*u)
def s02(t,T):
    R.set_ss(2); P=R.lia_walk(t,T=3.5,x0=-60,x1=440); k=seg(t,1.4,2.4); u=sm(t/5)
    P["arms"][1]=(.3+.1*P["amp"]*math.sin(t*6),1.0); P.update(item="cuaderno",look=(8*k,-9*k),tilt=P["tilt"]-.14*k,smv=.45+.5*seg(t,2.0,2.9),op=blink(t,(1.0,3.0)))
    ab=dict(lift=seg(t,1.7,2.5),sma=seg(t,2.3,3.1),brow=math.sin(seg(t,1.7,2.5)*math.pi),eye=(2*math.sin(t*2.2),0),op=blink(t,(1.2,3.4)))
    im=sala_frame(t,ab,walk=P,arm={},catx=P["x"])
    return cam(im,575+15*u,1085-15*u,1.26+.08*u)
def s03(t,T):
    R.set_ss(3); u=sm(t/8); g=.5+.5*math.sin(t*1.7)
    ab=dict(lift=.6,talk=abs(math.sin(t*6.5))*(.45+.5*g),brow=.5+.5*math.sin(t*2.3),nod=4*math.sin(t*3.1),eye=(-2,3),book=False,far=(536,1126),sma=.3,op=blink(t,(2.2,5.6)))
    hp=1 if math.sin(t*1.5-.6)>.25 else 0
    lap=dict(legs=((1.35,1.2+.25*math.sin(t*3)),(1.3,1.15-.25*math.sin(t*3))),arms=((1.2,.3),(1.0,.3)),look=(4,0),smv=.9,happy=hp,dy=-4*abs(math.sin(t*5.5))*hp,tilt=-.05*hp,op=blink(t,(1.1,4.0)))
    im=sala_frame(t,ab,lap=lap,arm=dict(tg=(532,1120+5*math.sin(t*6.5)),dir=(-1,-.3)),book_front=((500,1082+5*math.sin(t*6.5)),.12+.05*math.sin(t*3.2),False))
    return cam(im,595+8*u,985-8*u,1.48+.12*u)
def s04(t,T):
    R.set_ss(3); e=env("L04",T); u=sm(t/5.5)
    ab=dict(lift=.75,talk=e,brow=.4+.6*e,nod=3*math.sin(t*4),eye=(-3,4),book=False,far=(536,1126),sma=.35,op=blink(t,(2.9,)))
    lap=dict(legs=((1.35,1.25),(1.3,1.1)),arms=((1.2,.3),(1.0,.3)),look=(-9,-9),tilt=-.16,smv=.85,op=blink(t,(1.7,4.2)))
    im=sala_frame(t,ab,lap=lap,arm=dict(tg=(532,1120),dir=(-1,-.3)),book_front=((500,1082),.12,False))
    return cam(im,672+8*u,905-6*u,2.0+.14*u)
def s06(t,T):
    R.set_ss(3); u=sm(t/3.2); pg=math.sin(cl((t-1.1)/.7)*math.pi)
    ab=dict(lift=.2,talk=max(0,math.sin(t*7))*.35,eye=(3*math.sin(t*1.6),2),book=False,far=(536,1126),op=blink(t,(2.0,)))
    lap=dict(legs=((1.35,1.25),(1.3,1.1)),arms=((1.2,.3),(1.0,.3)),look=(6,2),smv=.6,op=blink(t,(.8,)))
    im=sala_frame(t,ab,lap=lap,arm=dict(tg=(532-8*pg,1120-26*pg),dir=(-1,-.3)),book_front=((500,1082),.12+.04*pg,True))
    return cam(im,580-40*u,1020+30*u,1.7+.35*u)
def s07(t,T):
    R.set_ss(3); e=env("L07",T); k=seg(t,1.3,1.9); u=sm(t/4.2)
    ab=dict(lift=.35,talk=e*.9,sma=.45,eye=(2*math.sin(t*1.5),2),book=False,far=(536,1126),brow=.3*e,op=blink(t,(2.6,)))
    lap=dict(legs=((1.35,1.25),(1.3,1.1)),arms=((1.2,.3),(1.0,.3)),look=(6-15*k,2-7*k),tilt=-.15*k,smv=.6-.35*k,brow=k,op=blink(t,(.9,3.1)))
    im=sala_frame(t,ab,lap=lap,arm=dict(tg=(532,1120),dir=(-1,-.3)),book_front=((500,1082),.12,True))
    return cam(im,640+6*u,948-6*u,1.85+.1*u)
EYE_POS=[(-5,3),(4,4),(-2,0),(5,1),(-4,4),(2,2)]
def s09(t,T):
    td=WI("L09",9)-.2
    i=int(t/.62); f=sm((t/.62-i)/.35); a=EYE_POS[i%6]; b=EYE_POS[(i+1)%6]; ey=lerp(a,b,f)
    if T<td:
        R.set_ss(3); u=sm(t/4.5)
        ab=dict(lift=.22,talk=max(0,math.sin(t*7))*.3,eye=ey,book=False,far=(536,1126),op=blink(t,(2.4,)),brow=.2)
        im=sala_frame(t,ab,lap=dict(legs=((1.35,1.25),(1.3,1.1)),arms=((1.2,.3),(1.0,.3)),look=(-8,-9),tilt=-.15,smv=.3),arm=dict(tg=(532,1120),dir=(-1,-.3)),book_front=((500,1082),.12,True))
        return cam(im,706-6*u,868,2.55+.25*u)
    R.set_ss(2); q=T-td; u=sm(q/4)
    ab=dict(lift=.22,talk=max(0,math.sin(t*7))*.3,eye=ey,book=False,far=(536,1126),sma=.3,op=blink(q,(1.6,)))
    lap=dict(legs=((1.35,1.25+.1*math.sin(t*2)),(1.3,1.1)),arms=((1.2,.3),(1.0,.3)),look=(-8,-9),tilt=-.15,smv=.25+.4*seg(q,.6,1.6),op=blink(q,(.9,)))
    im=sala_frame(t,ab,lap=lap,arm=dict(tg=(532,1120),dir=(-1,-.3)),book_front=((500,1082),.12,True))
    return cam(im,590,1045+10*u,1.42-.1*u)
def s10(t,T):
    R.set_ss(2); k=seg(t,.5,1.6); u=sm(t/5)
    ab=dict(lift=.2+.15*seg(t,1.6,2.4)*(1-seg(t,2.8,3.6)),talk=max(0,math.sin(t*7))*.3,eye=(3*math.sin(t*1.4),2),book=False,far=(536,1126),sma=.3+.5*seg(t,1.6,2.6),op=blink(t,(2.2,)))
    lap=dict(legs=((1.35,1.25),(1.3,1.1)),arms=((1.2,.3),(1.0,.3)),look=(2,0),tilt=-.24*k,smv=.6,happy=1 if k>.8 else 0,op=1-.5*k,dx=10*k)
    im=sala_frame(t,ab,lap=lap,arm=dict(tg=(532,1120),dir=(-1,-.3)),book_front=((500,1082),.12,True))
    return cam(im,590,1050+12*u,1.36-.14*u)

# ------------------------------------------------ insertos
_C={}
def fondo_borroso(k=.8):
    key=("fb",R.SS,k)
    if key not in _C:
        b=R.sala().resize((W//6,H//6)).filter(ImageFilter.GaussianBlur(9)).resize((W*R.SS,H*R.SS),Image.BICUBIC); _C[key]=Image.eval(b,lambda p:int(p*k))
    return _C[key]
def s05(t,T):
    R.set_ss(2); im=fondo_borroso(.86).copy(); u=sm(t/3.2); g=1-seg(t,.9,2.2)
    bc=(540-80+110*u,985+6*math.sin(t*2)); ba=.05*math.sin(t*1.3)-.04; K=3.3
    box=(0,560,1080,1420); L,d=R.layer(box)
    for sy_ in (-105,125):
        y=bc[1]+sy_; ex=bc[0]-66*K
        cap(d,(-80,y+70),(ex-70,y+8),74,DRESS,3); cap(d,(ex-78,y+12),(ex-52,y+4),78,WHITE,3,WOC); circ(d,(ex-8,y),44,SKN,3)
        gx=bc[0]+66*K+230*g
        cap(d,(1180,y+90),(gx+110,y+14),128,CARD,3.5); cap(d,(gx+118,y+16),(gx+78,y+8),132,mix(CARD,(255,255,255),.22),3); circ(d,(gx+14,y),66,SKA,3.5)
    R.libro(d,bc,ba,t,True,K,False)
    for sy_ in (-105,125):
        y=bc[1]+sy_; ex=bc[0]-66*K; gx=bc[0]+66*K+230*g
        cap(d,(ex-10,y-6),(ex+52,y-20),27,SKN,2.5)
        cap(d,(gx+20,y-10),(gx-58,y-30),40,SKA,3); circ(d,(gx-58,y-30),13,mix(SKA,(255,255,255),.25))
    R.put(im,L,box,(-14,16,14,.3))
    return cam(im,540+10*u,985,1.45+.1*u)

PAG=["El árbol más alto","del bosque guardaba","un nido pequeño.","Cada mañana,","el pájaro cantaba","para despertarlo."]
def pagina():
    key=("pag",R.SS)
    if key in _C: return _C[key]
    box=(100,640,980,1300); L,d=R.layer(box); s=R.SS
    rrect(d,(118,662,962,1282),14,(150,120,100)); rrect(d,(128,668,952,1272),10,(236,226,206))
    rrect(d,(136,672,538,1262),8,(250,242,226),2,(196,180,160)); rrect(d,(542,672,944,1262),8,(250,242,226),2,(196,180,160))
    for q in range(8): rrect(d,(524+q*4,676,528+q*4,1258),0,mix((250,242,226),(170,150,130),.5*(1-abs(q-3.5)/4)))
    # ilustración: un árbol con un nido y un pájaro
    vgrad(d,160,700,514,1090,(206,226,226),(236,236,214)); 
    ell(d,(337,1090),170,26,(150,180,130)); cap(d,(337,1090),(337,930),34,(140,100,74),2.5); cap(d,(337,960),(290,900),16,(140,100,74),2.5); cap(d,(337,940),(392,880),16,(140,100,74),2.5)
    for cx_,cy_,r_ in ((337,840,96),(262,880,66),(412,872,70),(300,790,60),(378,786,62)): circ(d,(cx_,cy_),r_,(120,160,118),2.5)
    for cx_,cy_ in ((300,820),(380,850),(336,770),(260,880),(420,880)): circ(d,(cx_,cy_),22,(140,178,132))
    ell(d,(396,884),26,10,(170,130,90),2); circ(d,(396,872),8,CREAM,1.5); circ(d,(408,874),8,CREAM,1.5)
    ell(d,(222,760),20,14,(226,138,110),2); circ(d,(206,752),10,(226,138,110),2); poly(d,[(196,752),(184,756),(196,759)],(236,190,110)); circ(d,(204,750),2,(50,34,30)); poly(d,[(236,756),(258,746),(254,768)],(196,110,90),1.5)
    for fx_,c_ in ((200,(226,150,140)),(250,(236,200,120)),(430,(226,150,140)),(470,(190,160,200))): cap(d,(fx_,1090),(fx_,1068),3,(110,150,104)); circ(d,(fx_,1064),8,c_,1.5)
    f=ImageFont.truetype(F_SERIF,int(38*s)); dd=d
    for i,ln in enumerate(PAG): dd.text(R._p((574,730+i*62)),ln,font=f,fill=(84,62,52))
    f2=ImageFont.truetype(F_SERIF,int(26*s)); dd.text(R._p((726,1200)),"7",font=f2,fill=(140,120,104)); dd.text(R._p((330,1200)),"6",font=f2,fill=(140,120,104))
    _C[key]=(L.rotate(180),box); return _C[key]
def s08(t,T):
    R.set_ss(3); im=fondo_borroso(.62).copy(); L,box=pagina(); u=sm(t/4.4)
    bob=4*math.sin(t*1.4)
    R.put(im,L,box,(-10,14,14,.35),at=(box[0],box[1]+bob),shade=False)
    d=ImageDraw.Draw(im)
    for x_,sg in ((150,1),(930,-1)):
        cap(d,(x_-sg*90,1330+bob),(x_-sg*30,1290+bob),120,CARD,3.5); cap(d,(x_-sg*10,1240+bob),(x_+sg*40,1196+bob),44,SKA,3); circ(d,(x_+sg*40,1196+bob),14,mix(SKA,(255,255,255),.25))
    return cam(im,395+290*u,975,1.75)

def letras():
    rnd=random.Random(5)
    base={"E":[[(.6,0),(0,0),(0,1),(.62,1)],[(0,.5),(.46,.5)]],"L":[[(0,0),(0,1),(.56,1)]],"I":[[(.2,0),(.2,1)],[(.14,-.14),(.36,-.32)]],
          "A":[[(0,1),(.3,0),(.6,1)],[(.11,.62),(.5,.62)]],"S":[[(.56,.14),(.3,0),(.06,.15),(.1,.4),(.3,.5),(.5,.6),(.56,.84),(.3,1),(.03,.88)]]}
    out=[]
    for i,ch in enumerate("ELIAS"):
        x0=262+i*126; y0=900+rnd.uniform(-8,8); h=165+rnd.uniform(-10,12); wv=150
        st=[]
        for s_ in base[ch]:
            pts=[(x0+px*wv+rnd.uniform(-4,4),y0+py*h+rnd.uniform(-4,4)) for px,py in s_]
            if len(pts)>4:
                sp=[]
                for j in range(len(pts)-2): sp+=bez(lerp(pts[j],pts[j+1],.5) if j else pts[0],pts[j+1],lerp(pts[j+1],pts[j+2],.5) if j<len(pts)-3 else pts[-1],8)
                pts=sp
            else:
                dn=[]
                for j in range(len(pts)-1): dn+=[lerp(pts[j],pts[j+1],q/10) for q in range(10)]
                pts=dn+[pts[-1]]
            st.append(pts)
        out.append(st)
    return out
LET=letras()
def escritorio():
    key=("esc",R.SS)
    if key in _C: return _C[key]
    rnd=random.Random(11); im=Image.new("RGB",(W*R.SS,H*R.SS)); d=ImageDraw.Draw(im); y=0
    while y<H:
        hh=rnd.randint(150,210); c=mix((160,112,80),(196,150,110),rnd.random()); d.rectangle([R._p((0,y)),R._p((W,y+hh))],fill=c)
        for _ in range(7):
            gy=rnd.uniform(y+8,y+hh-8); gx=rnd.uniform(-50,W-200); gl=rnd.uniform(160,520); curve(d,bez((gx,gy),(gx+gl/2,gy+rnd.uniform(-8,8)),(gx+gl,gy)),2,mix(c,(96,60,40),.3))
        d.rectangle([R._p((0,y+hh-3)),R._p((W,y+hh))],fill=mix(c,(70,44,30),.5)); y+=hh
    Pp=lambda p:rot(p,(540,985),-.035)
    poly(d,[Pp((160,740)),Pp((930,746)),Pp((924,1236)),Pp((154,1230))],(120,84,64)); poly(d,[Pp((150,726)),Pp((920,732)),Pp((914,1222)),Pp((144,1216))],(252,248,236),2,(200,186,170))
    im=glow(mul(im,(.82,.8,.86)),[("e",(60,300,900,1500),(70,50,22))],26); _C[key]=vign(im,.55); return _C[key]
def s11(t,T):
    R.set_ss(2); im=escritorio().copy(); u=sm(t/9)
    tl=[WI("L11",9+i) for i in range(5)]; te=[min(WE("L11",9+i),tl[i]+.95) for i in range(5)]
    d=ImageDraw.Draw(im); pen=None; G=(74,70,92)
    for i,st in enumerate(LET):
        if T<tl[i]: continue
        f=cl((T-tl[i])/(te[i]-tl[i])); n=sum(len(s_) for s_ in st); m=int(f*n); 
        for s_ in st:
            q=min(len(s_),m); m-=q
            if q>=2: curve(d,s_[:q],8,G)
            if q>0 and f<1: pen=s_[q-1]
    if pen is None:
        nxt=[i for i in range(5) if T<tl[i]]
        if nxt:
            i=nxt[0]; start=LET[i][0][0]; prev=LET[i-1][-1][-1] if i else (760,1120)
            t0=te[i-1] if i else S("L11")+.6; f=seg(T,t0,tl[i]-.05); pen=lerp(prev,start,f); pen=(pen[0],pen[1]-26*math.sin(f*math.pi))
        else:
            f=seg(T,te[4],te[4]+.8); e_=LET[4][-1][-1]; pen=(e_[0]+70*f,e_[1]+40*f-30*math.sin(f*math.pi))
    pen=(pen[0]+1.2*math.sin(T*23),pen[1]+1.2*math.cos(T*19))
    box=(int(pen[0])-80,int(pen[1])-330,int(pen[0])+520,int(pen[1])+460); L,d=R.layer(box)
    dv=(.5,-.86); top=(pen[0]+dv[0]*300,pen[1]+dv[1]*300); nk=(pen[0]+dv[0]*34,pen[1]+dv[1]*34)
    NG=(240,206,196)
    cap(d,(pen[0]+470,pen[1]+430),(pen[0]+150,pen[1]+96),96,NG,3); cap(d,(pen[0]+162,pen[1]+108),(pen[0]+132,pen[1]+78),100,WHITE,3,WOC)
    for q in range(6): circ(d,(pen[0]+210+q*46,pen[1]+150+q*52+14*math.sin(q*2.1)),6,mix(NG,(206,130,130),.5))
    circ(d,(pen[0]+92,pen[1]+36),54,SKN,3)
    cap(d,nk,top,24,(240,196,90),2.5); cap(d,lerp(nk,top,.9),top,24,(206,200,196),2.5); cap(d,lerp(nk,top,.96),top,22,(232,150,150),2.5)
    poly(d,[pen,(nk[0]-11,nk[1]-5),(nk[0]+10,nk[1]+7)],(232,200,160),2.5); poly(d,[pen,lerp(pen,(nk[0]-11,nk[1]-5),.35),lerp(pen,(nk[0]+10,nk[1]+7),.35)],G)
    for q,(fx_,fy_) in enumerate(((40,-44),(62,-22),(80,4))): cap(d,(pen[0]+92+fx_*.2,pen[1]+30+fy_*.3),(pen[0]+fx_,pen[1]+fy_),27,SKN,2.5)
    cap(d,(pen[0]+70,pen[1]+62),(pen[0]+24,pen[1]+18),26,SKN,2.5)
    R.put(im,L,box,(-16,18,12,.3))
    return cam(im,545-8*u,990,1.18+.08*u)

# ------------------------------------------------ mesita de noche
def firma(d,o,k,col,w):
    for st in LET:
        for s_ in st: curve(d,[(o[0]+(p[0]-262)*k+(p[1]-900)*k*.08,o[1]+(p[1]-900)*k*.42) for p in s_[::3]+[s_[-1]]],w,col)
def mesita_bg(dia):
    key=("mes",R.SS,dia)
    if key in _C: return _C[key]
    im=Image.new("RGB",(W*R.SS,H*R.SS)); d=ImageDraw.Draw(im)
    vgrad(d,0,0,W,1480,(226,214,196),(210,194,172))
    for x in range(0,W,72):
        for y in range(60,1440,84): xx=x+18+(36 if (y//84)%2 else 0); poly(d,[(xx,y-7),(xx+5,y),(xx,y+7),(xx-5,y)],(236,228,214))
    rrect(d,(0,1480,W,1520),0,(176,140,110)); vgrad(d,0,1520,W,H,(150,108,80),(120,84,62))
    x0,y0,x1,y1=70,400,390,850
    rrect(d,(x0-24,y0-24,x1+24,y1+24),10,CREAM,3,(190,160,130))
    if dia:
        vgrad(d,x0,y0,x1,y1,(170,206,232),(252,224,180),1.2); 
        for r_,k_ in ((90,.25),(64,.45),(44,.7)): circ(d,(300,760),r_,mix((250,226,184),(255,246,206),k_))
        poly(d,[(x0,y1),(x0,760),(170,720),(250,770),(x1,740),(x1,y1)],(150,176,150))
        for cx_,cy_,rw in ((150,520,56),(200,534,44),(310,480,50)): ell(d,(cx_,cy_),rw,14,(250,246,240))
    else:
        vgrad(d,x0,y0,x1,y1,(50,58,112),(104,104,150),1.3)
        for r_,k_ in ((62,.12),(46,.2),(34,.32)): circ(d,(250,540),r_,mix((70,78,130),(252,244,214),k_))
        circ(d,(250,540),24,(252,246,220)); 
        rr=random.Random(3)
        for _ in range(24): circ(d,(rr.uniform(x0+8,x1-8),rr.uniform(y0+8,y0+300)),rr.choice((1.4,2,2.6)),(244,240,222))
        poly(d,[(x0,y1),(x0,760),(170,720),(250,770),(x1,740),(x1,y1)],(66,70,104))
    rrect(d,(x0+154,y0,x0+166,y1),0,CREAM); rrect(d,(x0,y0+210,x1,y0+222),0,CREAM)
    rrect(d,(x0-44,y1+22,x1+44,y1+46),8,(244,230,208),3,(190,160,130))
    R.curtain(d,20,92,0,-1); rrect(d,(0,348,470,362),7,(140,100,76),2.5)
    # cama
    rrect(d,(700,800,1120,1300),40,(150,106,80),3); rrect(d,(730,836,1100,1200),28,(170,124,94))
    ell(d,(900,1118),170,56,(250,244,232),3,WOC)
    rrect(d,(670,1160,1120,1500),36,(214,190,170),3); 
    for q in range(5): curve(d,[(690+q*90,1180),(700+q*90,1480)],3,(196,168,150))
    for q in range(3): curve(d,[(680,1250+q*80),(1100,1250+q*80)],3,(196,168,150))
    rrect(d,(670,1160,1120,1214),26,(238,226,210),3)
    # mesita
    for lx in (244,596): rrect(d,(lx,1500,lx+34,1580),6,(110,78,60),2.5)
    rrect(d,(226,1130,650,1520),18,(168,118,86),3); rrect(d,(258,1176,618,1310),12,(184,134,98),2.5); circ(d,(438,1244),13,(226,190,120),2.5)
    rrect(d,(258,1340,618,1480),12,(150,104,76),2.5)
    poly(d,[(238,1036),(640,1036),(676,1134),(204,1134)],(198,150,110),3); rrect(d,(204,1134,676,1156),6,(160,112,82),2.5)
    for q in range(4): curve(d,[(250+q*20,1060+q*18),(600+q*14,1060+q*18)],2,(178,130,94))
    # lampara y vaso
    ell(d,(590,1070),40,12,(120,90,70),2.5); cap(d,(590,1066),(590,960),10,(120,90,70),2.5); poly(d,[(528,968),(652,968),(628,872),(552,872)],(236,216,176),2.5,(170,140,100))
    rrect(d,(258,1000,304,1078),8,(214,228,232),2.5,(150,170,180)); rrect(d,(262,1030,300,1074),6,(190,214,226))
    if dia: im=glow(mul(im,(1.0,.97,.9)),[("p",[(80,420),(380,420),(760,1160),(240,1160)],(60,44,14)),("e",(120,560,460,960),(50,40,20))],22)
    else: im=glow(mul(im,(.54,.6,.86)),[("p",[(110,430),(360,430),(640,1150),(250,1150)],(34,42,74)),("e",(150,440,350,640),(40,46,70))],18)
    _C[key]=vign(im,.62); return _C[key]
def gafas(d,c):
    for dx in (-40,40): ell(d,(c[0]+dx,c[1]),34,17,mix((198,150,110),(255,255,255),.35)); ring(d,(c[0]+dx,c[1]),34,17,4.5,(96,72,62))
    curve(d,[(c[0]-8,c[1]-3),(c[0]+8,c[1]-3)],4.5,(96,72,62)); curve(d,[(c[0]+72,c[1]-4),(c[0]+40,c[1]-34),(c[0]-50,c[1]-30)],4.5,(96,72,62)); curve(d,[(c[0]-72,c[1]-4),(c[0]-40,c[1]-22)],4.5,(96,72,62))
def s12(t,T):
    R.set_ss(3); im=mesita_bg(False).copy(); u=sm(t/4.5); M=(.58,.64,.88)
    k=seg(t,.25,1.5); out=seg(t,1.7,2.6)
    box=(120,940,760,1300); L,d=R.layer(box)
    px=lerp((250,1108),(388,1090),k); Pp=lambda p:(px[0]+p[0]+p[1]*.25,px[1]+p[1])
    poly(d,[Pp((-78,-26)),Pp((86,-26)),Pp((86,30)),Pp((-78,30))],(252,248,236),2.5,(190,176,160)); firma(d,Pp((-52,-12)),.2,(74,70,92),2.6)
    gafas(d,(430,1078))
    hx=px[0]-96-150*out; hy_=px[1]+10+60*out
    cap(d,(hx-190,hy_+150),(hx-40,hy_+22),64,(240,206,196),3); cap(d,(hx-48,hy_+28),(hx-30,hy_+14),68,WHITE,3,WOC); circ(d,(hx,hy_),30,SKN,3)
    for q in (-14,0,14): cap(d,(hx+10,hy_+q*.8),(hx+40,hy_-6+q),15,SKN,2.5)
    R.put(im,mul_layer(L,M),box,(-10,10,8,.25),shade=False)
    bx=(640,1100,1120,1420); L,d=R.layer(bx); b=5*math.sin(t*1.1)
    ell(d,(905,1250),200,96+b,(214,190,170),3); circ(d,(900,1088),50,SKA,3); ell(d,(934,1076),30,36,WHITE,2.5,WOC); smile(d,(884,1090),9,3,4,(64,46,40)); ell(d,(880,1110),22,9,WHITE,2,WOC)
    rrect(d,(700,1150,1110,1210),26,(238,226,210),3)
    R.put(im,mul_layer(L,(.54,.6,.86)),bx,shade=False)
    return cam(im,470-40*u,1050+20*u,1.5+.3*u)
def mul_layer(L,c):
    a=L.getchannel("A"); r=mul(L.convert("RGB"),c).convert("RGBA"); r.putalpha(a); return r
def s13(t,T):
    R.set_ss(3); im=mesita_bg(True).copy(); u=sm(t/4.2); d=ImageDraw.Draw(im)
    R.curtain(d,20,92,t,-1)
    box=(300,1000,560,1130); L,d=R.layer(box); gafas(d,(430,1078)); R.put(im,L,box,(-10,10,8,.25),shade=False)
    d=ImageDraw.Draw(im)
    for i in range(14):
        p=(260+(i*61)%300+16*math.sin(t*.5+i),620+(i*89)%420-10*t*(.3+(i%4)*.1)); circ(d,p,2.6,(255,244,210))
    return cam(im,430,1060,1.55+.3*u)

# ------------------------------------------------ cocina
def cocina_bg():
    key=("coc",R.SS)
    if key in _C: return _C[key]
    im=Image.new("RGB",(W*R.SS,H*R.SS)); d=ImageDraw.Draw(im)
    vgrad(d,0,0,W,900,(232,232,208),(224,222,196))
    vgrad(d,0,900,W,1160,(244,236,216),(236,226,204)); vgrad(d,0,1160,W,1560,(226,216,194),(214,202,180)); rrect(d,(0,1540,W,1566),0,(176,140,110)); vgrad(d,0,1566,W,H,(186,150,118),(150,116,90))
    for x in range(0,W,60): rrect(d,(x,900,x+2,1160),0,(214,202,180))
    for y in range(900,1160,60): rrect(d,(0,y,W,y+2),0,(214,202,180))
    for x in range(30,W,120):
        for y in (930,1050): poly(d,[(x,y-9),(x+9,y),(x,y+9),(x-9,y)],(156,186,180))
    rrect(d,(0,892,W,904),0,(186,160,130))
    x0,y0,x1,y1=90,420,430,840
    rrect(d,(x0-24,y0-24,x1+24,y1+24),10,CREAM,3,(190,160,130)); vgrad(d,x0,y0,x1,y1,(168,208,234),(254,228,186),1.2)
    for r_,k_ in ((100,.25),(70,.5),(46,.8)): circ(d,(170,740),r_,mix((248,222,180),(255,248,214),k_))
    for cx_,cy_,rw in ((300,500,60),(350,516,44),(180,560,50)): ell(d,(cx_,cy_),rw,14,(252,248,242))
    poly(d,[(x0,y1),(x0,780),(220,742),(320,784),(x1,756),(x1,y1)],(150,178,150))
    rrect(d,(x0+164,y0,x0+176,y1),0,CREAM); rrect(d,(x0,y0+200,x1,y0+212),0,CREAM); rrect(d,(x0-44,y1+22,x1+44,y1+46),8,(244,230,208),3,(190,160,130))
    for xa in (x0-40,x1-60):
        poly(d,[(xa,y0-40),(xa+100,y0-40),(xa+104,y0+150),(xa-4,y0+150)],(236,206,170),2.5,(190,150,120))
        for q in range(1,5): curve(d,[(xa+q*20,y0-36),(xa+q*20,y0+146)],3,(214,150,130))
        for q in range(1,5): curve(d,[(xa,y0-40+q*38),(xa+100,y0-40+q*38)],3,(214,150,130))
    rrect(d,(x0-60,y0-56,x1+60,y0-40),8,(140,100,76),2.5)
    # repisa
    rrect(d,(600,600,1010,618),4,(150,108,82),2.5)
    for jx,c_,h_ in ((630,(206,150,120),70),(700,(150,176,170),90),(770,(236,200,130),62)):
        rrect(d,(jx,600-h_,jx+54,600),8,c_,2.5); rrect(d,(jx-3,600-h_-10,jx+57,600-h_+4),4,mix(c_,(0,0,0),.2),2)
    for q in range(3): rrect(d,(850+q*50,556,888+q*50,600),8,(246,240,230),2.5,WOC); ring(d,(892+q*50,578),9,11,3.5,WOC)
    circ(d,(560,470),46,CREAM,3,(140,100,76)); cap(d,(560,470),(560,440),4,(90,64,54)); cap(d,(560,470),(580,480),4,(90,64,54))
    # sillas
    for cx_ in (700,860): rrect(d,(cx_-10,870,cx_+10,1220),8,(150,106,80),2.5)
    for q in range(3): rrect(d,(700,890+q*70,860,920+q*70),10,(170,124,94),2.5)
    for cx_ in (270,400): rrect(d,(cx_-8,960,cx_+8,1220),8,(150,106,80),2.5)
    for q in range(2): rrect(d,(270,980+q*70,400,1008+q*70),10,(170,124,94),2.5)
    im=glow(mul(im,(1.0,.98,.93)),[("p",[(90,430),(430,430),(900,1300),(300,1300)],(46,34,12)),("e",(40,560,360,900),(50,40,18))],24)
    _C[key]=vign(im,.7); return _C[key]
def mesa(d,t):
    rrect(d,(-20,1150,W+20,1196),10,(214,170,124),3); rrect(d,(-20,1196,W+20,1250),0,(176,130,94)); rrect(d,(-20,1246,W+20,1254),0,(140,100,72))
    for x in (60,960): rrect(d,(x,1250,x+50,1580),6,(160,116,84),2.5)
    poly(d,[(180,1150),(900,1150),(880,1300),(200,1300)],(248,240,224),2.5,(200,186,166))
    for q in range(1,9): curve(d,[(180+q*80,1152),(200+q*76,1298)],4,(214,150,130))
    for q in range(1,3): curve(d,[(186,1150+q*50),(894,1150+q*50)],4,(214,150,130))
    # tazón y vaso de Lía
    poly(d,[(380,1104),(470,1104),(452,1150),(398,1150)],(150,176,170),2.5); ell(d,(425,1104),45,9,(246,240,226),2.5,(110,136,130)); cap(d,(446,1100),(482,1066),5,(200,196,190),1.5,(130,126,122))
    rrect(d,(256,1076,300,1150),8,(236,240,240),2.5,(170,180,184)); rrect(d,(260,1100,296,1146),6,(252,250,244))
    # cesta de pan y mermelada
    poly(d,[(500,1108),(600,1108),(588,1150),(512,1150)],(196,150,100),2.5)
    for q in range(4): curve(d,[(506+q*4,1118+q*9),(594-q*4,1118+q*9)],2.5,(160,116,76))
    for bx_,by_ in ((522,1100),(556,1092),(584,1102)): ell(d,(bx_,by_),24,16,(226,176,116),2.5); curve(d,[(bx_-8,by_-6),(bx_+8,by_-2)],2.5,(196,140,90))
    rrect(d,(772,1096,826,1150),8,(196,96,96),2.5); rrect(d,(768,1084,830,1100),5,(236,214,150),2.5)
    # café del abuelo
    ell(d,(640,1148),58,9,(246,240,230),2.5,WOC); poly(d,[(606,1092),(674,1092),(666,1146),(614,1146)],(246,240,230),2.5,WOC); ring(d,(684,1116),13,15,5,WOC)
    rrect(d,(610,1104,670,1114),0,(110,140,170)); ell(d,(640,1092),34,6,(110,76,56),2,WOC)
    for q in range(3):
        ph=t*.9+q*2.1; y0_=1080-((t*26+q*40)%90); x_=626+q*14
        curve(d,[(x_+6*math.sin(ph+j*.9),y0_-j*12) for j in range(5)],3,(252,248,240))
def s14(t,T):
    R.set_ss(3); im=cocina_bg().copy(); q=max(0,T-E("L14")); u=sm(t/7.5)
    ab=dict(lift=.04,eye=(-1,6),book=False,far=(700,1170),op=blink(t,(2.3,5.0)),brow=-.3)
    box=(480,730,1000,1380); L,ld=R.layer(box); bc,ba,br=R.abuelo_base(ld,t,**ab); R.put(im,L,box,(-18,14,12,.2))
    box=(520,760,900,1200); L,ld=R.layer(box); R.abuelo_arm(ld,br,(650+9*math.cos(t*3.2),1040+4*math.sin(t*3.2)),(-.1,1),spoon=True); R.put(im,L,box,(-8,10,8,.2))
    k=seg(t,1.0,1.8)
    box=(140,820,520,1420); L,ld=R.layer(box)
    R.lia(ld,330,hy=1196,arms=((.5,.9),(.85,.75)),look=(7,0),tilt=-.06*k,smv=.3,op=blink(t,(1.5,3.9,6.0)),t=t); R.put(im,L,box,(-12,10,10,.18))
    d=ImageDraw.Draw(im); mesa(d,t)
    return cam(im,545+45*u,1030+8*u,1.34+.26*u)

SC=[(0,s01),(S("L02")-.3,s02),(S("L03")-.3,s03),(S("L04")-.3,s04),(S("L05")-.3,s05),(S("L06")-.25,s06),(S("L07")-.3,s07),(S("L08")-.3,s08),
    (S("L09")-.3,s09),(S("L10")-.3,s10),(S("L11")-.35,s11),(S("L12")-.3,s12),(S("L13")-.35,s13),(S("L14")-.35,s14)]
XF=.33
# ------------------------------------------------ subtítulos y título
def chunks():
    out=[]
    for lid,v,txt in LINEAS:
        ws=txt.replace("«","").replace("»","").split(); js=WORDS[lid]; n=min(len(ws),len(js)); cur=[]; i0=0
        if lid=="L11": ws=ws[:9]+["E","L","Í","A","S."]
        for i in range(n):
            cur.append(ws[i]); end=ws[i][-1] in ".,:…?!"
            if (len(" ".join(cur))>=17 and (end or len(" ".join(cur))>=24)) or (end and len(cur)>=3) or i==n-1:
                if i<n-1 and n-1-i==1 and len(" ".join(cur+[ws[i+1]]))<30: continue
                out.append((WI(lid,i0),WE(lid,i)+.25," ".join(cur),v)); cur=[]; i0=i+1
    for j in range(len(out)-1):
        if out[j][1]>out[j+1][0]: out[j]=(out[j][0],out[j+1][0],out[j][2],out[j][3])
    return out
CH=chunks()
_F={}
def font(p,s):
    if (p,s) not in _F: _F[(p,s)]=ImageFont.truetype(p,s)
    return _F[(p,s)]
def overlay(im,T):
    ov=None
    for a,b,txt,v in CH:
        if a-.06<=T<b:
            k=min(1,(T-a+.06)/.14,(b-T)/.12); ov=Image.new("RGBA",(W,150),(0,0,0,0)); d=ImageDraw.Draw(ov); f=font(F_SUB,48)
            if v=="A": txt="— "+txt
            d.text((W/2,75),txt,font=f,fill=(70,44,38,int(235*k)),anchor="mm",stroke_width=6,stroke_fill=(70,44,38,int(235*k)))
            d.text((W/2,75),txt,font=f,fill=(255,250,236,int(255*k)) if v=="N" else (255,226,160,int(255*k)),anchor="mm")
            im.paste(ov,(0,1395),ov); break
    if T<3.4:
        k=min(1,T/.5,(3.4-T)/.5); ov=Image.new("RGBA",(W,220),(0,0,0,0)); d=ImageDraw.Draw(ov)
        for txt,y,s_ in (("La letra de mi abuelo",70,92),("Capítulo 1",160,60)):
            f=font(F_HAND,s_); d.text((W/2,y),txt,font=f,fill=(70,44,38,int(220*k)),anchor="mm",stroke_width=7,stroke_fill=(70,44,38,int(220*k))); d.text((W/2,y),txt,font=f,fill=(255,246,224,int(255*k)),anchor="mm")
        im.paste(ov,(0,250),ov)
    return im
def frame(T,subs=True):
    i=max(j for j,(a,f) in enumerate(SC) if a<=T+1e-6); a,f=SC[i]; im=f(T-a,T)
    if i>0 and T-a<XF:
        pa,pf=SC[i-1]; im=Image.blend(pf(T-pa,T),im,sm((T-a)/XF))
    return overlay(im,T) if subs else im
def fbytes(n): return frame(n/FPS).tobytes()

if __name__=="__main__":
    c=sys.argv[1]
    if c=="info":
        print("TOTAL",TOTAL); [print(l,round(TL[l][0],2),round(TL[l][1],2)) for l in TL]; [print(round(a,2),f.__name__) for a,f in SC]; [print(round(a,2),round(b,2),x) for a,b,x,_ in CH]
    elif c=="still":
        ts=[float(x) for x in sys.argv[2:]]; sh=Image.new("RGB",(540*len(ts),960))
        for i,t in enumerate(ts): sh.paste(frame(t).resize((540,960),Image.LANCZOS),(540*i,0))
        sh.save("still.jpg",quality=88)
    elif c=="part":
        from multiprocessing import Pool
        a,b,out=int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
        p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-crf","16","-preset","fast","-pix_fmt","yuv420p",out+".part.mp4"],stdin=subprocess.PIPE)
        with Pool(2) as pool:
            for bts in pool.imap(fbytes,range(a,b),chunksize=3): p.stdin.write(bts)
        p.stdin.close(); p.wait(); os.replace(out+".part.mp4",out)
