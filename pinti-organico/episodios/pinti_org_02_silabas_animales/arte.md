# Arte: pinti_org_02_silabas_animales ("M con U… ¡MUUU!")

Directora de arte · 2026-10-24 · Guion aprobado (crítico 8,7). Guía: `marca/guia.md`. Biblioteca: `marca/escenas/`.
Referencia del primer fotograma: `episodios/pinti_org_02_silabas_animales/arte_frame0.jpg` (renderizado con la biblioteca).

## Idea visual
Un sketch en la granja del libro (pág. 52, "Pinti en la granja"): cielo celeste, colina verde, nubes que pasan. Los animales son los **PNG reales** del libro, animados con `escenas/personaje.py`, y las sílabas son tarjetas con los colores exactos de la pág. 21. Humor físico tierno: squash & stretch, viento del mugido, letras que caen.

## Paleta del episodio
| Uso | Hex |
|---|---|
| Fondo | `fondos.cielo` (cielo `#E6F1FD` → `#DCECFC`, pasto `#CCE4C4`, sol `#FCD46C` arriba a la derecha) |
| Tarjeta ma / me / mi / mo / mu (pág. 21) | `#FCF4E4`/`#F4BC94` · `#ECF4FC`/`#A4CCE4` · `#ECFCEC`/`#ACD4A4` · `#FCF4DC`/`#F4C454` · `#FCECF4`/`#E4ACC4` |
| Tarjeta pe (pág. 24) | azul: `#ECF4FC` / `#A4CCE4`; "pe · pe" en azul `#4A8FDB` |
| Onomatopeyas | MUUUU y miau en tinta `#3C342C` con borde blanco 10 px; **CUAC en amarillo `#FCDC6C`** con borde blanco |
| Check de acierto | `efectos.check` (verde `#3AA65A` del punto de inicio) |
| Agua de Pepe | ondas y gotas `#9CC8E8` (`personaje.ondas`, `personaje.salpicadura`) |

## Primer fotograma (gancho, 0,0 s)
- Frase completa **"¿Cómo suena la M con la U?"** con `texto.karaoke` (tam 92, ancho_max 820, x=500, y=380), "¿Cómo" ya resaltado.
- Pinti de cerca, centrado (`alto=760`, pies en y≈1560, `pose="celebra"`), con la tarjeta **"m"** junto a su mano izquierda y la **"u"** junto a la derecha (`texto.silaba`, 200x190, tam 130, rosa de "mu"). Las tarjetas acompañan el vaivén de los brazos (mismo seno que la pose).
- 0–1,8 s: las tarjetas se acercan y chocan (squash horizontal de las tarjetas, nunca rotación) y se funden en la tarjeta rosa **"mu"** con pop (`texto.silaba` con `t0` en el frame del choque) + `efectos.chispas`.
- Cámara: `camara_viva(zoom=1.03, foco=(0.5, 0.55))` + leve zoom-in.

## Escenas de la biblioteca por tramo
| Tramo | Escenas |
|---|---|
| 0,0–1,8 | `fondos.cielo` · `pinti.dibujar(pose="celebra")` · `texto.silaba` ×2 → 1 · `texto.karaoke` |
| 1,8–3,4 | `personaje.dibujar("vaca", salto=…)` con `personaje.saltitos` entrando desde la izquierda · mugido: `squash=personaje.grito(t, 2.3, 3.2)` · MUUUU con `texto.titulo` (y≈1150) que vibra en vertical · Pinti empujado: `inclina` −12° → 0 con `base.muelle`, `squash` y `parpadeo=1.0` (ojos apretados) |
| 3,4–4,6 | "m + u = mu" (`texto.silaba` + "+" y "=" en Fredoka 600); la "m" vibra en vertical (±4 px a 18 Hz) durante el "mmm"; unión con pop; `efectos.check` sobre la fórmula; `efectos.estrellas_logre` o `efectos.chispas` |
| 4,6–5,8 | Barrido lateral de cámara: `transiciones.deslizar(a, b, u, "izq")` (sin giro) · tarjeta verde "mi" |
| 5,8–8,6 | `personaje.dibujar("gato")` sube desde abajo con `rebote_atras` y queda sentado con `vaiven=2` (cola) y parpadeo automático · "miau" con `texto.titulo`; luego la "a" y la "u" caen con `efectos.letra_cae` (retraso 0,08 s entre ellas, rebotan sin rotar); "mi" sube y encaja en la tarjeta |
| 8,6–10,9 | Cabecera "Sílabas con M" sale hacia arriba, "Sílabas con P" entra desde abajo con pop (`texto.titulo`) · tarjetas de la M fuera con `sale()` · tarjeta "pe" (`texto.silaba(color="sil_azul")`) · `personaje.ondas` + `personaje.dibujar("pepe")` entrando en su charquito |
| 10,9–11,9 | CUAC: `squash=personaje.grito(…)` en Pepe + `personaje.salpicadura` · Pinti congelado 0,5 s con `parpadeo=0` y ojos grandes (`mirar=(0, -0.4)`) y escala 1,04 |
| 11,9–16,1 | "p + e = pe" iluminando cada parte (pastilla naranja como el karaoke) · "pe · pe" azul sobre Pepe que se desliza hasta "Pepe" · Pepe con `saltitos` en el agua · `efectos.check` |
| 16,1–19,4 | `transiciones.circulo` a la **pág. 21 real** con `pagina.render(21, zoom1=1.2, foco=(0.5, 0.2))` entre y≈500 y 1300 · saltito en cascada de las tarjetas: `pagina.recorte(21, caja_de_cada_tarjeta)` encima de la página, con salto vertical de 18 px uno tras otro · Pinti abajo a la izquierda con guiño `parpadeo=(0.0, v)` · Pepe asoma por el borde inferior · "Guárdalo…" con `texto.titulo(tam ≥ 44)` |
| 19,4–23,8 | `pagina.portada_entra(tilt=True, ancho=640, centro=(540, 712))` · vaca y gato asomados a media altura de la portada **sin tapar el título ni los sellos "88 páginas" y "3–6 años"** · Pepe con ondas debajo de y=1440 · textos del CTA en y≈1190–1440 · últimos 0,3 s: Pinti entra desde abajo con las tarjetas "m" y "u" en la misma pose del frame 0 (bucle) |

Recortes de tarjetas de la pág. 21: medir sus cajas en `assets/paginas/pagina-21.jpg` (fila "ma me mi mo mu", y≈270–395 en px de la página) antes de animar; no a ojo.

## Qué debe verse distinto respecto a los otros vídeos de la tanda
- Es el único con **escenario exterior (cielo y colina) y reparto completo** de personajes del libro. El 01 vive en crema con letras gigantes y el 03 en la página real en macro.
- Ritmo más rápido y cómico: cambios de plano cada 1–2 s y gags con física (gravedad, rebote, viento). Las tarjetas mantienen la identidad de marca: colores de la pág. 21, Fredoka y la pastilla naranja del karaoke.
- Sin vídeos publicados aún: sin dato de métricas para comparar.

## Notas que el animador debe cumplir (de `revision.md`)
- Ninguna letra ni tarjeta gira, se voltea o se espeja (sobre todo en 6,9 s con las letras que caen y en 8,6 s con el cambio de cabecera). El barrido de 4,6 s es solo desplazamiento lateral.
- Pinti no tiene pelo: en el mugido, solo inclinación, squash y ojos apretados.
- El "Guárdalo" de 16,1 s con cuerpo de letra ≥ 40 px (mejor 44).
- Texto solo entre y=250–1440 y x=60–940.
- Los animales se mueven solo transformando sus PNG (escala, squash, inclinación, vaivén, parpadeo sobre sus ojos). No se les dibujan bocas ni patas nuevas.
- Cada frame al vídeo con `base.aplanar(frame)`; sin negro al principio ni al final.
