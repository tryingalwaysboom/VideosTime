# Arte: pinti_org_01_b_d ("¿b o d? El truco de la barriga")

Directora de arte · 2026-10-24 · Guion v3 aprobado (crítico 8,5). Guía: `marca/guia.md`. Biblioteca: `marca/escenas/`.
Referencia del primer fotograma: `episodios/pinti_org_01_b_d/arte_frame0.jpg` (renderizado con la biblioteca).

## Idea visual
Un "tip" que se siente cuento: fondo crema cálido, dos letras gigantes con volumen que juegan como personajes y Pinti que las dibuja. Es el vídeo **más limpio** de la tanda: casi todo pasa sobre crema y la página 76 real es el clímax.

## Paleta del episodio
| Uso | Hex |
|---|---|
| Fondo | `crema` (`#FFF7EC` → `#FDEBD6`) en todo el vídeo, sin cambiar de fondo |
| b | `#E4542F` (naranja de la pág. 76) |
| d | `#4A8FDB` (azul de la pág. 76) |
| Punto de inicio / números | verde `#3AA65A` con borde blanco · círculo azul `#4A8FDB` con número blanco |
| Texto | tinta `#3C342C`, borde blanco 10 px; palabra activa en pastilla `#FC8C44` |
| Estrellas "¡Lo logré!" | borde `#D8AC44`, relleno `#FCDC6C` |

Un acento por plano: mientras se enseña la b, el único naranja fuerte es la b (Pinti cerca, el texto en tinta). Cuando se enseña la d, el azul manda.

## Primer fotograma (gancho, 0,0 s)
- Frase completa **"¿Tu hijo confunde la b y la d?"** con `texto.karaoke` (tam 92, ancho_max 800, centro x=500, y=380). "¿Tu" ya en pastilla naranja en el frame 0.
- **b** naranja y **d** azul enormes (Fredoka 600, unos 560 px; base en y≈1180–1240), con borde blanco 12 px y `base.sombra_suave`. En el frame 0 la b ya está despegando (60 px más alta que la d): hay movimiento desde el primer frame.
- Intercambio de sitio (×2, con "swish"): las letras saltan en arco por encima/debajo una de otra, con squash al aterrizar (`base.muelle`). **Solo traslación y escala vertical: nunca giran ni se espejan.**
- Cámara: `base.camara_viva(frame, t, zoom=1.02)` + push-in de 1,02 a 1,06 en 0–2,7 s.

## Escenas de la biblioteca por tramo
| Tramo | Escenas |
|---|---|
| 0,0–2,7 | `fondos.crema` · letras b/d (texto Fredoka con sombra suave) · `texto.karaoke` · `camara_viva` |
| 2,7–3,8 | `pinti.dibujar(pose="piensa")` con `pinti.entrada` desde la izquierda y `mirar` hacia la b y luego la d · `texto.bocadillo("¡Son iguales!", cola hacia Pinti)` · `efectos.interrogacion` (2, con rebote) · a 3,3: `efectos.bombilla` + `texto.titulo("El truco de la barriga", tam=84, y≈330)`; las letras se apartan a los lados con `sale()` |
| 3,8–8,0 | `trazo.render(trazo.letra_b(330, 900, alto=500), color=b_naranja, grosor=34)` con Pinti trazando: `pinti.pies_para_punta` + `pinti.inclinacion_trazo(ang)` (el cuerpo detrás del avance, no encima de la barriga). Textos "b = palito…" y "…+ barriga adelante →" con `texto.titulo`. A 7,4: la barriga se infla (escala 1→1,12→1 con `muelle`, solo la capa de la b) y Pinti `pose="ríe"` |
| 8,0–11,4 | `trazo.render(trazo.letra_d(770, 900, alto=500), color=d_azul)` igual que la b. Al final, b y d juntas con etiquetas ("palito + barriga" / "barriga + palito") |
| 11,4–13,3 | Transición `circulo` (centro en la d) a `pagina.render(76, zoom0=1.0, zoom1=1.22, foco=(0.5, 0.33))` · `pagina.lupa` sobre la primera d de la fila (`pagina.a_pantalla(223, 470, …)`, ya probado en `_pruebas/pagina76_lupa.jpg`) con `latido` · texto "¿Lo sabe tu hijo?" · a 12,6 la d de la lupa se pinta de azul con un trazo de crayón corto |
| 13,3–15,7 | Puntos 1 y 2 de repaso sobre la d pintada · `pinti.dibujar(pose="celebra")` con salto + `pinti.aterriza` · abrazo: Pinti entre la b y la d, **sus brazos no tapan ninguna letra** · `efectos.estrellas_logre` como recorte que entra junto a Pinti (no se corta a la página) |
| 15,7–17,2 | Pág. 76 entera (`pagina.render`, push-in lento que no se detiene) · a 16,9 `pagina.portada_entra(tilt=True)` por delante |
| 17,2–19,5 | Portada respirando · `pinti.dibujar(pose="señala_arriba")` a la derecha, guiño a 19,0 con `parpadeo=(0.0, v)` (solo el ojo derecho, 0,25 s) · textos en y≈1150–1400 · **corte seco** |

Transiciones permitidas aquí: `circulo` (11,4) y `barrido_crayon` si hace falta un cambio de plano. Nada de fundidos a negro.

## Qué debe verse distinto respecto a los otros vídeos de la tanda
- 01 es el único con **letras gigantes como protagonistas** sobre crema liso. El 02 vive en el cielo/granja con personajes y el 03 en la página real en macro. Así, en el feed se reconoce a Pinti (mismo personaje, misma tipografía y pastilla naranja), pero cada vídeo tiene su propio mundo.
- Aún no hay vídeos publicados ni ganadores (`memoria/ganadores.md` vacío): sin dato para comparar con métricas.

## Notas que el animador debe cumplir (de `revision.md`)
- Letras siempre derechas, también en saltos, intercambios, inflado de la barriga y abrazo.
- Primero termina el trazo de la barriga (hasta 7,4) y después Pinti se toca la barriga.
- "Guárdalo para practicar con tu hijo" (y≈300) no pisa "¿Lo sabe tu hijo?".
- Cada frame al vídeo con `base.aplanar(frame)`; el último frame es un plano vivo (portada respirando), sin negro.
