# Arte: pinti_org_03_asmr_m ("ASMR: la M se escribe sola")

Directora de arte · 2026-10-24 · Guion aprobado por el crítico (8,7). Guía: `marca/guia.md`. Biblioteca: `marca/escenas/`.
Referencia del primer fotograma: `episodios/pinti_org_03_asmr_m/arte_frame0.jpg` (renderizado con la biblioteca, sobre la pág. 20 real).

## Idea visual
Satisfying puro sobre papel real: la **pág. 20 real** sobre la mesa, en macro, y Pinti como crayón que deja una línea naranja exacta encima de los puntos. Nada gira: solo paneos, panorámicas verticales y zoom. El color lo ponen el naranja del trazo, el rosa de mamá y el amarillo de las estrellas sobre el blanco cálido del papel.

## Paleta del episodio
| Uso | Hex |
|---|---|
| Fondo bajo la página | `fondos.mesa` (madera clara cálida con lápices; solo se ve en el zoom out final) |
| Papel / pauta | la página real tal cual (papel `#FFFDF8`, pauta azul y roja del libro) |
| Trazo | naranja Pinti `#FC8C44`, sólido, extremos redondos, **una sola línea por el centro** que tapa los puntos |
| Mamá coloreada | rosa `#F4ACC4` (`pagina.colorear`, multiplicado: el contorno negro sigue negro) |
| Estrellas | relleno `#FCDC6C` sobre el borde dorado real de la página |
| Texto | tinta `#3C342C` con borde blanco; pastilla `#FC8C44` en el karaoke; `efectos.velo` crema detrás del texto en los macros |

## Primer fotograma (gancho, 0,0 s)
- `pagina.camara(L, t, 20, foco, 4.2, centro=(540, 900))` con `foco` = centro de `trazo.pag20_M_fila1(0)`: la primera M punteada mide ≈ 300 px de alto en pantalla. **No subir de 4,5x**: la página fuente mide 1084 px y más allá se ve borrosa.
- Encima, `trazo.render_tiempos(L, t, trazo.letra_M(caja_en_pantalla), [(0.0, 1.0), (1.2, 3.1)], grosor=30, badges=False)`: las cajas de la pág. 20 están medidas sobre los puntos reales, así que el trazo cae exacto sobre ellos (comprobado en `marca/escenas/_pruebas/asmr_macro_M.jpg`).
- Pinti (`alto=420`, `pose="quieto"`, `respira=False`, `sombra=False`) con la punta en el inicio del palito: `pinti.pies_para_punta` + `pinti.inclinacion_trazo(ang)`, suavizada frame a frame (`suave_de=inclinación_anterior`).
- Texto: `efectos.velo(L, 230, 500)` y `texto.karaoke` con **"La M, trazo a trazo"** (tam 84, ancho_max 860, y≈330; "La" y "M," activas de 0,0 a 1,2, "trazo a trazo" de 1,2 a 2,6) + `texto.titulo("Sube el volumen", tam=54, y≈430)`. Las dos líneas, enteras desde el frame 0. El resaltado de 1,2 s no mueve ni deforma el texto (pop de la pastilla al 8 %, sin desplazar palabras).
- Cámara: solo la respiración de la escala (1,00–1,01). Aquí no se usa `camara_viva` con deriva: el trazo tiene que quedar clavado sobre los puntos (si se usa, aplicarla al frame completo ya compuesto, nunca solo a la página).

## Escenas de la biblioteca por tramo
| Tramo | Escenas |
|---|---|
| 0,0–3,1 | Macro M1: `pagina.camara` + `trazo.render_tiempos` + Pinti trazando + karaoke con velo |
| 3,1–3,4 | `efectos.destello` recorriendo la M terminada · "La M suena mmm" (`texto.titulo`, pop a 3,10) · Pinti levanta la punta y "se relame": **con su boca del PNG, sin dibujar lengua**: ojos cerrados de gusto (`parpadeo=1.0` 0,3 s), squash 0,06 y un `efectos.corazones` pequeño |
| 3,4–6,65 | `pagina.mover_camara` a ~2x siguiendo a Pinti por la fila (M2, M3 y M4 = `pag20_M_fila1(1..3)`) con los tiempos exactos del guion en `render_tiempos` (palito 0,40 s, punta arriba 0,05 s, trazo 2 0,60 s) |
| 6,65–9,8 | Panorámica vertical a la fila 3 (`mover_camara`, sin giro) · m lenta con `trazo.letra_m(pag20_m_fila3(0))` en 3 trazos (7,2–7,8 · 7,9–8,8 · 8,9–9,8) · saltito de Pinti con `pinti.aterriza` |
| 9,8–12,6 | Bajada a la fila "Mamá" (`trazo.PAG20_MAMA`: M, a, m, a y tilde con `letra_M`, `letra_a`, `letra_m`, `tilde`), letra de imprenta con la punta levantada entre letras y entre trazos · "Guárdalo: la M en el orden correcto" (`texto.titulo`, tam ≥ 48, y≈300, con `velo`) |
| 12,6–14,8 | Bajada a "Colorea a mamá": `pagina.colorear(img, pagina.mascara_zona(20, PAG20_MAMA_DIBUJO, PAG20_SEMILLAS_ROSA), "#F4ACC4", u, PAG20_MAMA_DIBUJO)` con u de 0 a 1 entre 12,65 y 14,40 (el rayado avanza del cuerpo al lazo). La imagen coloreada se pasa a `pagina.camara` en lugar del número de página. A 14,5 mamá parpadea: aquí **solo** se puede hacer un destello suave sobre sus ojos, porque es un dibujo de la página (no se redibuja) |
| 14,8–16,0 | Estrellas "¡Lo logré!" de la pág. 20 en `pagina.PAG20_ESTRELLAS` (r ≈ 16 px de página): relleno amarillo una tras otra (15,0 · 15,4 · 15,8) con `efectos.estrella` + `efectos.chispas`, encima de la página y a su escala |
| 16,0–17,4 | Zoom out continuo con `mover_camara` hasta la página completa (escala ≈ 0,9) sobre `fondos.mesa`, con todo lo trazado/coloreado; la 5.ª M sigue punteada · "Página 20" · Pinti se asoma por el borde derecho (`pose="saluda"`) |
| 17,4–19,8 | `pagina.portada_entra(tilt=False)`: entra en plano con pop 0,96 → 1,00 y luego respira; **sin tilt ni perspectiva** · textos del CTA en y≈1180–1360 · Pinti `pose="señala_arriba"` |
| 19,8–21,6 | Puente de loop: salto de Pinti + `mover_camara` de vuelta a **foco = centro de `pag20_M_fila1(4)`, escala 4,2, centro (540, 900)**: el mismo encuadre del frame 0, con la 5.ª M sin trazar. Pinti con la punta apoyada arriba a la izquierda en la misma pose que en el frame 0. Corte seco |

Para la página que se va trazando: guardar el estado (trazos terminados) como capa sobre la página para no repintarlo en cada plano, y comprobar que en 16,0–21,6 la 5.ª M sigue punteada.

## Qué debe verse distinto respecto a los otros vídeos de la tanda
- Es el único **sin fondo dibujado**: todo pasa dentro del papel real y la mesa solo aparece en el zoom out. El 01 es crema con letras gigantes y el 02 es la granja con personajes.
- Ritmo más lento y continuo (ASMR): sin cortes bruscos ni rebotes grandes; easings in-out en todos los movimientos de cámara.
- Es experimental: se mide contra 01 y 02. Sin vídeos publicados aún, no hay dato de métricas.

## Notas que el animador debe cumplir (de `revision.md`)
- Nada gira: ni letras, ni página, ni portada (`tilt=False`).
- El trazo empieza y termina en el frame exacto de cada scratch (tiempos de `render_tiempos` = tiempos del guion). Con la punta en el aire, `render_tiempos` devuelve `apoyada=False`: úsalo para que el scratch nunca suene en el aire.
- "a" de "Mamá": redondo desde arriba a la derecha hacia la izquierda (antihorario) hasta cerrarse, luego palito. Tilde de arriba a la derecha hacia abajo a la izquierda. Así está en `letra_a` y `tilde`.
- Texto entre y=250–1440 y x=60–940; nada por debajo de 1440.
- Cada frame al vídeo con `base.aplanar(frame)`; el último frame y el frame 0 casi idénticos (solo cambia el texto del gancho).
