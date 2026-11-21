"""Renderiza un fotograma de prueba de cada escena en esta carpeta: python3 pinti-organico/marca/escenas/_pruebas/probar.py"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(AQUI)))

from escenas import base, pinti, fondos, pagina, trazo, texto, transiciones, efectos, personaje  # noqa: E402
from escenas.base import P  # noqa: E402


def guardar(img, nombre, zona=False):
    if zona:
        img = base.guia_zona_segura(img.copy())
    base.aplanar(img).save(os.path.join(AQUI, nombre), quality=92)


# 1. Fondos
for tipo in ("crema", "cuarto", "mesa", "cielo", "pizarra"):
    guardar(fondos.render(1.0, tipo), f"fondo_{tipo}.jpg")

# 2. Pinti en sus poses sobre el cuarto, con respiración y parpadeo
L = fondos.cuarto(0.5)
for i, pose in enumerate(("saluda", "piensa", "celebra", "señala")):
    pinti.dibujar(L, 0.4 + i * 0.1, 270 + (i % 2) * 540, 900 + (i // 2) * 680, alto=560, pose=pose)
guardar(L, "pinti_poses_cuarto.jpg")

# 3. Página real con push-in hacia la fila de b/d de la pág. 76 (a mitad del zoom)
L = fondos.crema(2.0)
pagina.render(L, 1.2, 76, t0=0.0, t1=2.0, zoom0=1.0, zoom1=1.22, foco=(0.5, 0.33), centro=(540, 860))
guardar(L, "pagina76_pushin.jpg", zona=True)

# 4. Lupa sobre una d de la fila (pág. 76 a zoom completo)
L = fondos.crema(2.0)
kw = dict(t0=0.0, t1=2.0, zoom0=1.0, zoom1=1.22, foco=(0.5, 0.33), centro=(540, 860))
pagina.render(L, 2.0, 76, **kw)
dx, dy, _ = pagina.a_pantalla(223, 470, 2.0, **kw)   # primera d de la fila (px de la página)
base_img = L.copy()
pagina.lupa(L, dx, dy, base_img, dx, dy, radio=170, aumento=1.7, aparicion=1.0, latido=0.5)
guardar(L, "pagina76_lupa.jpg", zona=True)

# 5. Portada entrando con tilt 3D y Pinti señalando arriba
L = fondos.crema(3.0)
pagina.portada_entra(L, 0.25, 0.0, dur=0.55, centro=(540, 820), ancho=640)
guardar(L, "portada_entrando.jpg")
L = fondos.crema(3.0)
pagina.portada_entra(L, 1.5, 0.0, dur=0.55, centro=(500, 760), ancho=620)
pinti.dibujar(L, 1.5, 900, 1430, alto=380, pose="señala_arriba")
texto.titulo(L, 1.5, "Link en mi perfil", 500, 1360, t0=1.0, tam=72)
guardar(L, "portada_cierre.jpg", zona=True)

# 6. Trazo de la b (mitad de la barriga) y de la d (mitad del palito), con Pinti trazando
L = fondos.crema(1.0)
tb = trazo.letra_b(330, 900, alto=500)
p = trazo.render(L, 2.0, tb, t0=0.5, dur_trazo=1.0, color=P["b_naranja"], grosor=34)
td = trazo.letra_d(770, 900, alto=500)
trazo.render(L, 2.0, td, t0=0.0, dur_trazo=1.2, color=P["d_azul"], grosor=34)
if p:  # Pinti se inclina 35° y su punta va pegada al trazo (nunca boca abajo)
    fx, fy = pinti.pies_para_punta(p[0], p[1], alto=300, inclina=35)
    pinti.dibujar(L, 2.0, fx, fy, alto=300, pose="quieto", inclina=35, sombra=False, respira=False)
guardar(L, "trazo_b_d.jpg", zona=True)

# 7. Karaoke del gancho (palabra activa: "confunde")
L = fondos.crema(0.8)
pal = [("¿Tu", 0.0, 0.3), ("hijo", 0.3, 0.6), ("confunde", 0.6, 1.2), ("la", 1.2, 1.4), ("b", 1.4, 1.7),
       ("y", 1.7, 1.9), ("la", 1.9, 2.1), ("d?", 2.1, 2.7)]
texto.karaoke(L, 0.75, pal, 470, 380, tam=92, ancho_max=780)
guardar(L, "texto_karaoke.jpg", zona=True)

# 8. Titular pop a mitad de entrada + bocadillo + ? + bombilla
L = fondos.crema(1.0)
texto.titulo(L, 0.2, "El truco de la barriga", 470, 330, t0=0.0, tam=88)
texto.bocadillo(L, 1.0, "¡Son iguales!", 520, 640, t0=0.6, tam=72, cola=(-0.6, 1))
pinti.dibujar(L, 1.0, 330, 1300, alto=460, pose="piensa")
efectos.interrogacion(L, 1.0, 560, 900, t0=0.6)
efectos.bombilla(L, 1.0, 700, 880, t0=0.7)
guardar(L, "texto_titulo_bocadillo.jpg", zona=True)

# 9. Sílabas de la pág. 21
L = fondos.mesa(1.0)
texto.fila_silabas(L, 1.0, ["ma", "me", "mi", "mo", "mu"], 700, t0=0.0)
texto.silaba(L, 0.12, "ma", 500, 1100, t0=0.0, ancho=300, alto=220, tam=140)
guardar(L, "silabas.jpg", zona=True)

# 10. Estrellas "¡Lo logré!" y corazones
L = fondos.cielo(1.0)
efectos.estrellas_logre(L, 1.0, 500, 600, t0=0.4)
pinti.dibujar(L, 1.0, 500, 1400, alto=520, pose="celebra")
efectos.corazones(L, 1.0, 500, 900, t0=0.3)
guardar(L, "estrellas_corazones.jpg")

# 11. Transiciones a mitad (sin negro)
a = fondos.crema(0.0)
pinti.dibujar(a, 0.0, 540, 1300, alto=600, pose="saluda")
b = fondos.cielo(0.0)
pagina.render(b, 0.0, 22, t0=0, t1=1, zoom0=1.0, zoom1=1.0, centro=(540, 900), ancho=820)
guardar(transiciones.render(a, b, 0.3, "barrido_crayon"), "trans_barrido.jpg")
guardar(transiciones.render(a, b, 0.15, "circulo"), "trans_circulo.jpg")
guardar(transiciones.render(a, b, 0.2, "deslizar"), "trans_deslizar.jpg")

# 12. Cámara viva
guardar(base.camara_viva(a, 1.3, zoom=1.04), "camara_viva.jpg")

# 13. Personajes del libro (PNG reales): vaca gritando, gato con parpadeo cerrado, Pepe con ondas, mamá
L = fondos.cuarto(1.0)
personaje.dibujar(L, 1.0, "vaca", 290, 900, alto=430, squash=personaje.grito(1.05, 1.0, 1.8))
personaje.dibujar(L, 1.0, "gato", 790, 900, alto=430, parpadeo=1.0)
personaje.ondas(L, 1.0, 290, 1500, ancho=460)
personaje.dibujar(L, 1.0, "pepe", 290, 1520, alto=330)
personaje.salpicadura(L, 1.2, 290, 1450, t0=1.0)
personaje.dibujar(L, 1.0, "mama", 790, 1560, alto=520, salto=personaje.saltitos(1.1, 1.0, 2.0)[0])
guardar(L, "personajes_libro.jpg", zona=True)

# 14. ASMR pág. 20: macro de la 1.ª M (≈4x) con el trazo 2 a mitad y Pinti trazando
L = fondos.mesa(0.0)
caja = trazo.pag20_M_fila1(0)
foco = ((caja[0] + caja[2]) / 2, (caja[1] + caja[3]) / 2)
a_p = pagina.camara(L, 0.0, 20, foco, 4.2, centro=(540, 860))
cp = [a_p(caja[0], caja[1]), a_p(caja[2], caja[3])]
tr = trazo.letra_M((cp[0][0], cp[0][1], cp[1][0], cp[1][1]))
punta, apoyada, ang = trazo.render_tiempos(L, 1.9, tr, [(0.0, 1.0), (1.2, 3.1)], grosor=30, badges=False)
inc = pinti.inclinacion_trazo(ang)   # el cuerpo va detrás del avance: no tapa lo que se dibuja
fx, fy = pinti.pies_para_punta(punta[0], punta[1], alto=420, inclina=inc)
pinti.dibujar(L, 1.9, fx, fy, alto=420, pose="quieto", inclina=inc, sombra=False, respira=False)
texto.karaoke(L, 0.3, [("La", 0, 1.2), ("M,", 0, 1.2), ("trazo", 1.2, 2.6), ("a", 1.2, 2.6), ("trazo", 1.2, 2.6)],
              500, 330, tam=84, ancho_max=860)
texto.titulo(L, 0.3, "Sube el volumen", 500, 440, t0=-1, tam=56)
guardar(L, "asmr_macro_M.jpg", zona=True)

# 15. ASMR: "Mamá" escrita + mamá coloreada al 60 % (página real modificada solo con el trazo/color)
img = pagina.cargar(20)
mr = pagina.mascara_zona(20, pagina.PAG20_MAMA_DIBUJO, tuple(pagina.PAG20_SEMILLAS_ROSA))
img = pagina.colorear(img, mr, base.P["mama_rosa"], 0.6, pagina.PAG20_MAMA_DIBUJO)
L = fondos.mesa(0.0)
a_p = pagina.camara(L, 0.0, img, (450, 1200), 1.9, centro=(540, 900))
for k in ("M", "a1", "m", "a2"):
    c = trazo.PAG20_MAMA[k]
    (ax, ay), (bx, by) = a_p(c[0], c[1]), a_p(c[2], c[3])
    f = {"M": trazo.letra_M, "a1": trazo.letra_a, "m": trazo.letra_m, "a2": trazo.letra_a}[k]
    tr = f((ax, ay, bx, by))
    trazo.render_tiempos(L, 9, tr, [(0, 1)] * len(tr), grosor=9, badges=False)
(p0, p1) = trazo.PAG20_MAMA["tilde"]
trazo.render_tiempos(L, 9, trazo.tilde(a_p(*p0), a_p(*p1)), [(0, 1)], grosor=9, badges=False)
efectos.check(L, 1.0, 860, 760, t0=0.5)
guardar(L, "asmr_mama_colorear.jpg", zona=True)

# 16. Portada en plano (sin tilt) para el ASMR + letras que caen sin rotar
L = fondos.crema(0.0)
pagina.portada_entra(L, 0.3, 0.0, dur=0.55, centro=(540, 760), ancho=620, tilt=False)
efectos.letra_cae(L, 0.25, "a", 600, 1100, 1400, t0=0.0)
efectos.letra_cae(L, 0.25, "u", 700, 1100, 1400, t0=0.0, retraso=0.08)
guardar(L, "portada_plana_letras_caen.jpg", zona=True)
print("ok")
