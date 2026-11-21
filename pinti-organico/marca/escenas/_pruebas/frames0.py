"""Renderiza el primer fotograma de referencia de cada episodio en episodios/<slug>/arte_frame0.jpg: python3 pinti-organico/marca/escenas/_pruebas/frames0.py"""
import sys, math
import os
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, R + "/marca")
from PIL import ImageDraw
from escenas import base, pinti, personaje, fondos, pagina, trazo, texto, efectos
from escenas.base import P

def letra(L, ch, x, y, tam, color):
    lay = base.nuevo_lienzo()
    d = ImageDraw.Draw(lay)
    d.text((x, y), ch, font=base.fuente(tam, 600), fill=base.rgb(color), anchor="ms", stroke_width=12, stroke_fill=base.rgb("#FFFFFF"))
    L.alpha_composite(base.sombra_suave(lay, radio=18, opacidad=0.22).crop((72, 72 - 12, 72 + 1080, 72 + 1920 - 12)))
    L.alpha_composite(lay)

def ep01(t=0.0):
    L = fondos.crema(t)
    # b y d saltan e intercambian sitio (siempre derechas): frame 0 = despegando
    letra(L, "b", 330, 1240 - 60, 560, P["b_naranja"])
    letra(L, "d", 760, 1240, 560, P["d_azul"])
    pal = [("¿Tu", 0.0, 0.3), ("hijo", 0.3, 0.6), ("confunde", 0.6, 1.2), ("la", 1.2, 1.4), ("b", 1.4, 1.7),
           ("y", 1.7, 1.9), ("la", 1.9, 2.1), ("d?", 2.1, 2.7)]
    texto.karaoke(L, t, pal, 500, 380, tam=92, ancho_max=800)
    return base.camara_viva(L, t, zoom=1.02)

def ep02(t=0.0):
    L = fondos.cielo(t)
    pinti.dibujar(L, t, 540, 1560, alto=760, pose="celebra")
    texto.silaba(L, 0.5, "m", 260, 900, t0=0.0, color="sil_rosa", ancho=200, alto=190, tam=130)
    texto.silaba(L, 0.5, "u", 820, 900, t0=0.0, color="sil_rosa", ancho=200, alto=190, tam=130)
    pal = [("¿Cómo", 0, 0.35), ("suena", 0.35, 0.7), ("la", 0.7, 0.85), ("M", 0.85, 1.1), ("con", 1.1, 1.3),
           ("la", 1.3, 1.45), ("U?", 1.45, 1.8)]
    texto.karaoke(L, t + 0.01, pal, 500, 380, tam=92, ancho_max=820)
    return base.camara_viva(L, t, zoom=1.03, foco=(0.5, 0.55))

def ep03(t=0.0):
    L = fondos.mesa(t)
    caja = trazo.pag20_M_fila1(0)
    foco = ((caja[0] + caja[2]) / 2, (caja[1] + caja[3]) / 2)
    a_p = pagina.camara(L, t, 20, foco, 4.2, centro=(540, 900))
    (ax, ay), (bx, by) = a_p(caja[0], caja[1]), a_p(caja[2], caja[3])
    tr = trazo.letra_M((ax, ay, bx, by))
    punta, ap, ang = trazo.render_tiempos(L, t + 0.001, tr, [(0.0, 1.0), (1.2, 3.1)], grosor=30, badges=False)
    inc = pinti.inclinacion_trazo(ang)
    fx, fy = pinti.pies_para_punta(punta[0], punta[1], alto=420, inclina=inc)
    pinti.dibujar(L, t, fx, fy, alto=420, pose="quieto", inclina=inc, sombra=False, respira=False)
    efectos.velo(L, 230, 500)
    texto.karaoke(L, t, [("La", 0, 1.2), ("M,", 0, 1.2), ("trazo", 1.2, 2.6), ("a", 1.2, 2.6), ("trazo", 1.2, 2.6)],
                  500, 330, tam=84, ancho_max=860)
    texto.titulo(L, 1.0, "Sube el volumen", 500, 430, t0=-1, tam=54)
    return L

for slug, f in [("pinti_org_01_b_d", ep01), ("pinti_org_02_silabas_animales", ep02), ("pinti_org_03_asmr_m", ep03)]:
    base.aplanar(f(0.0)).save(f"{R}/episodios/{slug}/arte_frame0.jpg", quality=90)
print("ok")
