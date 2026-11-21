import math, subprocess, wave
src=open('make_video.py').read()
exec(src[:src.index('SC=[')])
DUR=15.0
a0=src.index('K=OW/W'); a1=src.index('BG={'); exec(src[a0:a1])
b0=src.index('yy,xx=np.mgrid'); b1=src.index('def frame('); exec(src[b0:b1])
PI=math.pi; OFF=-80; DK=(28,32,44); WOOD=(224,172,112); WOOD2=(196,146,92); RNG=np.random.default_rng(7)
def lerp(a,b,u): u=max(0,min(1,u)); return a+(b-a)*u
def mkbg():
    b=bg_room(True); o=int(OFF*K); img=Image.new('RGB',(OW,OH))
    img.paste(b,(0,o)); img.paste(b.crop((0,OH-8,OW,OH)).resize((OW,-o)),(0,OH+o))
    return img
BGS=mkbg()
_face=face
def face(d,c,kind,look=1):
    x,y=c; dx=10*look; ex=(x-17+dx,x+21+dx); ey=y-6
    if kind=='happy':
        for e in ex: circ(d,(e,ey),21,fill=(255,255,255),w=5); circ(d,(e+4*look,ey-2),7,fill=BK,out=None)
        d.chord([(x+dx-20)*S,(y+8)*S,(x+dx+26)*S,(y+44)*S],0,180,fill=BK); ell(d,(x+dx+3,y+37),9,5,fill=(230,90,90),out=None); return
    if kind=='achoo':
        line(d,[(ex[0]-12,ey-12),(ex[0]+8,ey),(ex[0]-12,ey+12)],w=5); line(d,[(ex[1]+12,ey-12),(ex[1]-8,ey),(ex[1]+12,ey+12)],w=5)
        ell(d,(x+dx+3,y+36),15,19,fill=BK,out=None); ell(d,(x+dx+3,y+44),8,7,fill=(230,90,90),out=None); return
    return _face(d,c,kind,look)
def poly(d,pts,fill,w=6):
    d.polygon([sc(p) for p in pts],fill=fill); line(d,pts+[pts[0]],w=w)
def rotp(p,a,pv):
    c,s_=math.cos(a),math.sin(a); x,y=p[0]-pv[0],p[1]-pv[1]; return (pv[0]+x*c-y*s_,pv[1]+x*s_+y*c)
def rrect(d,x0,y0,x1,y1,a,pv,fill,w=5):
    pts=[rotp(p,a,pv) for p in ((x0,y0),(x1,y0),(x1,y1),(x0,y1))]; poly(d,pts,fill,w)
def rrc(d,cx,cy,w_,h_,a,fill,wd=4): rrect(d,cx-w_/2,cy-h_/2,cx+w_/2,cy+h_/2,a,(cx,cy),fill,wd)
def part(d,x,y,kind,a=0,s_=1.0):
    if kind==0: rrc(d,x,y,60*s_,14*s_,a,WOOD,max(2,4*s_))
    elif kind==1: rrc(d,x,y,34*s_,34*s_,a,WOOD2,max(2,4*s_))
    elif kind==2: circ(d,(x,y),7*s_+1,fill=(190,194,204),w=max(2,3*s_)); line(d,[(x-5*s_,y),(x+5*s_,y)],w=2)
    else: rrc(d,x,y,16*s_,40*s_,a,(180,184,198),max(2,3*s_))
def hands(hip,lean,arms):
    sh=(hip[0]+96*math.sin(lean),hip[1]-96*math.cos(lean)); out=[]
    for a,b in arms: e=P(sh,a,50); out.append(P(e,b,50))
    return out
STAND=((0.1,0.0),(-0.1,0.0))
def runlegs(T):
    ph=T*2*PI*4.5; L=[]
    for o in (0,PI): a=0.9*math.sin(ph+o); L.append((a,a-(0.5+0.7*max(0,math.cos(ph+o)))))
    return tuple(L)
def puff(d,x,y,t,n=6,sz=26):
    for i in range(n):
        an=i*2*PI/n+0.5; r0=10+90*t; circ(d,(x+r0*math.cos(an),y+r0*0.6*math.sin(an)),max(3,sz*(1-0.7*t)),fill=(240,236,228),out=None)
