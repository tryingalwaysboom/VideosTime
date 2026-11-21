# Guía de marca: vídeos orgánicos de Pinti

La mantiene la directora de arte. Se aplica a todos los vídeos de "Aprende a leer y escribir con Pinti". Si algo choca con `BRIEF.md`, gana el brief.
Código de referencia: `pinti-organico/marca/escenas/` (cada valor de esta guía está en `escenas/base.py`).

## 1. Pinti: solo a partir de los archivos reales
- Fuente única: `assets/pinti.png` (289x420, fondo transparente). También aparece en la portada (`assets/portada.jpg`) y en las páginas (p. ej. 20, 21, 22, 76).
- Pinti es un **crayón naranja** con punta, la franja blanca en zigzag con estrella amarilla, brazos de línea con guantes blancos, zapatos morados, ojos grandes con dos brillos, mejillas rosas y sonrisa abierta.
- **Nunca se redibuja ni se rediseña.** Todo movimiento sale de transformar el PNG: escala, rotación, deformación (squash/stretch), y rotar los brazos recortados del propio PNG (`escenas/pinti.py`).
- Lo único que se añade encima es el **parpadeo**: el ojo del PNG se aplasta en vertical y, en el frame cerrado, se dibuja un arco con el mismo color y grosor de contorno del PNG (`#141424`). Así no se nota.
- Para su mamá, el pato Pepe, la vaca y el gato se usan las ilustraciones de `assets/ilustraciones/` tal cual (misma regla: no se redibujan). Se animan con `escenas/personaje.py` (`"mama"`, `"vaca"`, `"gato"`, `"pepe"`): respiración, parpadeo sobre los ojos reales (cajas medidas en el PNG), saltitos con squash, `grito()` (squash & stretch del MUUU o el CUAC), vaivén, y para Pepe `ondas()` y `salpicadura()` del charquito.
- Si falta una pose que no se pueda lograr transformando el PNG (Pinti de perfil, sentado, de espaldas, etc.), **no se inventa**: se le piden a Wal los archivos.

### Poses disponibles (`pinti.sprite` / `pinti.dibujar`)
| Pose | Qué hace | Para qué |
|---|---|---|
| `saluda` | brazo izquierdo (el levantado del PNG) oscila a 1,6 Hz | entradas, cierre |
| `piensa` | mano hacia la cabeza, mirada arriba a la derecha | dudas, "¿?" |
| `celebra` | los dos brazos arriba, vaivén rápido | aciertos, estrellas |
| `señala` | brazo derecho horizontal hacia la derecha | señalar una letra o una página |
| `señala_arriba` | mano izquierda recta hacia arriba | "link en mi perfil" |
| `ríe` | brazos hacia la barriga y vibración | "se toca la barriga y se ríe" |
| `quieto` | brazos con balanceo mínimo | mientras traza o escucha |

## 2. Paleta (hex muestreados de los assets con Python)
**Pinti** (`pinti.png`)
| Uso | Hex |
|---|---|
| Cuerpo naranja | `#FC8C44` |
| Naranja en sombra | `#CC7C3C` |
| Contorno (solo el del PNG) | `#141424` |
| Zapatos | `#6C4C94` |
| Mejillas / corazones | `#F4ACC4` |
| Estrella del pecho | `#FCDC6C` |

**Libro** (páginas 20, 21, 22, 76)
| Uso | Hex |
|---|---|
| Tinta de texto (marrón cálido, nunca negro puro ni navy) | `#3C342C` |
| Papel | `#FFFDF8` |
| Borde melocotón de página y etiquetas | `#F4BC94` |
| b naranja (pág. 76) | `#E4542F` |
| d azul (pág. 76) y círculos de número | `#4A8FDB` |
| Punto verde de inicio (pág. 20) | `#3AA65A` |
| Contorno de estrellas "¡Lo logré!" | `#D8AC44` |

**Tarjetas de sílaba** (pág. 21), relleno / borde
| ma | me | mi | mo | mu |
|---|---|---|---|---|
| `#FCF4E4` / `#F4BC94` | `#ECF4FC` / `#A4CCE4` | `#ECFCEC` / `#ACD4A4` | `#FCF4DC` / `#F4C454` | `#FCECF4` / `#E4ACC4` |

**Cuento** (pág. 22): cielo `#DCECFC`, pasto `#CCE4C4`, sol `#FCD46C`, mamá rosa `#F4ACC4`.
**Portada:** verde petróleo `#0F5C5C`, amarillo `#FCDC4C`, naranja `#FC8C5C`. El verde se usa **solo** en la portada y en la pizarra; no como fondo general (enfría).

**Fondos de vídeo** (derivados, cálidos): crema claro `#FFF7EC` → crema `#FDEBD6`, melocotón suave `#FBD9C0`.

Reglas de color:
- Fondo siempre cálido y luminoso (crema, cuarto, mesa, cielo del cuento). Nunca blanco puro plano, negro ni gris.
- Un acento por plano: naranja Pinti para resaltar; azul solo para "d", números o contrapunto.
- Las letras que se enseñan llevan **el color que les da el libro** (b naranja `#E4542F`, d azul `#4A8FDB`).

## 3. Tipografía
- **Fredoka** (redonda, amable, parecida a la del libro y la portada), en `marca/fuentes/Fredoka-500/600/700.ttf` (licencia OFL, incluida). No está en el sistema: la instalamos ahí. Se carga con `base.fuente(tam, peso)`.
- Respaldo si faltara: Poppins Bold (`/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf`), la única sans geométrica del sistema (`fc-list`). Nada de DejaVu, Liberation ni serif.
- Pesos: titulares y karaoke 700; sílabas 600; textos pequeños 500.
- Tamaños en 1080x1920: gancho 84–96 px; titular de sección 72–88; bocadillo 64–72; sílaba grande 110–140; etiquetas ≥ 44. Nunca por debajo de 40 px.
- Color del texto `#3C342C` con **borde blanco de 8–10 px** y sombra difusa. Prohibido el contorno navy grueso.
- Máximo 2 líneas por bloque, ≤ 7 palabras por línea.

## 4. Trazo, bordes y sombras
- **Contorno:** el único contorno oscuro es el de los dibujos reales (Pinti y el libro). Lo que dibujamos por código (tarjetas, bocadillos, lupa) lleva borde de color pastel (8–10 px) o ningún borde.
- **Esquinas:** radio 22–36 px en tarjetas, 26–30 px en páginas y portada.
- **Sombras:** solo difusas y cálidas: `#8A5A3C`, opacidad 0,16–0,28, desenfoque 14–24 px, desplazamiento vertical de 8–16 px (`base.sombra_suave`). Bajo los personajes, una elipse de contacto (`base.sombra_suelo`) que se encoge cuando saltan. **Prohibida la sombra dura desplazada.**
- **Trazo de letras** (como en el libro): una sola línea punteada por el centro (puntos de 10 px cada 20 px, en `#3C342C`) que se rellena con un crayón sólido de 30–36 px con extremos redondos. Cada trazo empieza en el **punto verde** (`#3AA65A`, borde blanco) con su **número** en un círculo azul. Una flechita blanca va por delante del relleno para marcar la dirección (`escenas/trazo.py`).
- Las letras **nunca giran ni se voltean**: solo se trasladan, escalan o rebotan en vertical.

## 5. Animación (tierno, cálido, con volumen)
Referencia de sensación: cuento ilustrado que respira. No es el look de Pifio (stickman, golpes, cortes bruscos), ni tarjetas que aparecen y se quedan quietas.

**Pinti**
- **Respiración** siempre activa: escala vertical ±1,6 % a 0,85 Hz, compensada en horizontal, con el pivote en los pies.
- **Parpadeo:** dura unos 0,16 s y se repite cada 3,3 s; uno de cada tres es doble (`pinti.parpadeo_auto`). Si hay varios personajes, se desfasan con `semilla`. **Guiño:** `parpadeo=(0.0, v)` cierra solo el ojo derecho (0,25 s).
- **Mirada:** los ojos se desplazan hasta un 12 % hacia lo que importa (la letra, la página) antes de que pase la acción.
- **Saltos:** anticipación (squash 0,05) → salto → aterrizaje con squash amortiguado (`pinti.aterriza`). La sombra de suelo acompaña.
- **Entradas:** desde fuera del cuadro con rebote suave (`pinti.entrada`, ease-out-back 1,3). Nunca "aparece" de golpe.
- **Al trazar:** Pinti lleva su punta pegada al trazo (`pinti.pies_para_punta`) y su cuerpo va **detrás del avance** para no tapar lo que aún no se ha trazado: inclinación con `pinti.inclinacion_trazo(ang)` (máx. ±55°, suavizada frame a frame). Nunca boca abajo. En planos macro, Pinti no pasa de 1,4 veces el alto de la letra.

**Texto**
- **Entrada pop:** escala 0,6 → 1 con ease-out-back (≈ 0,38 s), giro de -4° a 0° y alfa rápido. Después respira (±1,2 %).
- **Karaoke:** la frase completa se ve desde el frame 0. La palabra que suena lleva una pastilla naranja `#FC8C44` con texto blanco y un pop del 8 %; el resto, en tinta con borde blanco (`texto.karaoke`).
- **Bocadillos** blancos y redondos, con la cola hacia quien habla y entrada pop. Las voces de niño van siempre en bocadillo; la narradora, en texto libre.

**Cámara y planos**
- **Ningún plano queda quieto:** cámara viva con zoom que respira (±0,8 %) y deriva lenta de ±6 px (`base.camara_viva`), o push-in continuo sobre las páginas. `camara_viva` calcula sola el zoom mínimo para que nunca se vea el borde del lienzo.
- **Nunca negro por transparencia:** cada fotograma se escribe al vídeo con `base.aplanar(frame)` (compone sobre crema). Un píxel transparente convertido con `.convert("RGB")` sale negro.
- **Páginas reales:** entran enteras y legibles, luego push-in suave (`pagina.render`), sin pasar de 1,25x salvo que se quiera leer una fila. Al terminar el push-in sigue avanzando un 1 % por segundo.
- **Portada:** entra deslizándose con un tilt 3D de 14° → 0° y luego respira entre 1,00 y 1,03 (`pagina.portada_entra`). En vídeos donde "nada gira" (ASMR) se usa `tilt=False`: entra en plano con pop 0,96 → 1,00.
- **Cámara libre sobre la página** (`pagina.camara` + `pagina.mover_camara`): paneos, panorámicas verticales y macros con fotogramas clave (foco en px de la página, escala). Zoom en escala logarítmica y ease in-out; nunca gira. **Macro máximo: 4,5 px de pantalla por px de página** (la página mide 1084 px; más allá se ve borrosa). La página real solo se modifica con lo que hace el niño: trazo naranja encima (`trazo.render_tiempos`) y color de crayón (`pagina.colorear`, que respeta el contorno negro).
- **Trazos sobre la página real:** las cajas de las letras punteadas de la pág. 20 están medidas sobre sus puntos (`trazo.pag20_M_fila1(i)`, `pag20_m_fila3(i)`, `PAG20_MAMA`) y las letras de imprenta se construyen con `trazo.letra_M / letra_m / letra_a / tilde`. Para otras páginas se miden igual (centros de los puntos con `scipy.ndimage`), nunca a ojo.
- **Transiciones sin negro** (`escenas/transiciones.py`): barrido de crayón naranja, círculo que se abre con aro naranja, deslizamiento con rebote o fundido cruzado. Duran 0,25–0,45 s. **Prohibido el fade desde negro o a negro**, y también el corte a un frame vacío. El vídeo acaba en corte seco sobre un plano vivo.
- **Easings:** ease-out (`sale`) para lo que llega, ease-in-out (`suave`) para cámara y push-in, ease-out-back (`rebote_atras`) para pops. Nada lineal salvo los trazos de letra, que van con un ease-out ligero.
- **Ritmo:** algo nuevo cada 1–2 s, y cada acción visible empieza en el frame de su sonido.

## 6. Zona segura (1080x1920)
| Zona | Valor |
|---|---|
| Arriba, sin nada importante | y < 120 |
| Abajo, sin nada importante | y > 1600 (320 px de margen) |
| Derecha (iconos de TikTok/Reels) | x > 940 sin texto |
| Franja de texto de los guiones | y 250 – 1440 |
| Margen lateral mínimo | 60 px |

Fondos y decoración pueden ocupar toda la pantalla. Texto, letras que se enseñan, páginas que hay que leer y el "Link en mi perfil" van siempre dentro. Para revisar, se superpone con `base.guia_zona_segura()` (solo en las pruebas, nunca en el vídeo).

## 7. Fondos de la biblioteca
| Fondo | Cuándo |
|---|---|
| `crema` | trucos, letras, ganchos de texto. Es el fondo base de marca |
| `cuarto` | historias y sketches (Pinti en casa) |
| `mesa` | sílabas, ASMR de trazo, "lo hace solito" |
| `cielo` | cuentos (sale de la pág. 22), celebraciones |
| `pizarra` | retos y preguntas (verde de la portada con marco de madera) |

## 8. Prohibido
- Redibujar, rediseñar o "mejorar" a Pinti, o generar imágenes con IA (ElevenLabs incluido).
- Contorno navy grueso con sombra dura desplazada, look de stickers, estética escolar fría, blanco puro plano.
- Tarjetas estáticas, o planos quietos de más de 0,5 s.
- Fade desde o hacia negro.
- Letras que giran o se voltean. Letras con doble contorno.
- Páginas "falsas" que imiten el libro: solo se usan páginas reales de `assets/paginas/`, o recortes de ellas.
- Logo o intro antes del gancho.

## 9. Cómo se usa la biblioteca
```python
import sys; sys.path.insert(0, "pinti-organico/marca")
from escenas import base, pinti, personaje, fondos, pagina, trazo, texto, transiciones, efectos
```
| Módulo | Qué tiene |
|---|---|
| `base` | lienzo, paleta `P`, `fuente`, easings, `sombra_suave`, `sombra_suelo`, `camara_viva`, `aplanar`, `guia_zona_segura` |
| `pinti` | `dibujar` (poses, respiración, parpadeo, salto, squash), `entrada`, `aterriza`, `pies_para_punta`, `inclinacion_trazo` |
| `personaje` | mamá, vaca, gato y Pepe desde sus PNG: `dibujar`, `saltitos`, `grito`, `ondas`, `salpicadura` |
| `fondos` | `crema`, `cuarto`, `mesa`, `cielo`, `pizarra` (`render(t, tipo)`) |
| `pagina` | `render` (push-in), `camara` + `mover_camara`, `a_pantalla`, `recorte`, `lupa`, `portada_entra`, `mascara_zona` + `colorear` |
| `trazo` | `render` (tiempos iguales), `render_tiempos` (tiempos del guion), `letra_b/d/M/m/a`, `tilde`, cajas de la pág. 20 |
| `texto` | `titulo` (pop), `karaoke` (una o varias palabras activas), `bocadillo`, `silaba`, `fila_silabas` |
| `efectos` | `estrellas_logre`, `chispas`, `interrogacion`, `bombilla`, `corazones`, `check`, `destello`, `letra_cae` |
| `transiciones` | `barrido_crayon`, `circulo`, `deslizar`, `cruzado` (`render(a, b, u, tipo)`) |
Pruebas visuales: `python3 pinti-organico/marca/escenas/_pruebas/probar.py` (genera un JPG por escena en `_pruebas/`). Primer fotograma de referencia de cada episodio: `python3 pinti-organico/marca/escenas/_pruebas/frames0.py` (escribe `episodios/<slug>/arte_frame0.jpg`).
