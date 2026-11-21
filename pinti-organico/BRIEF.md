# Brief maestro — Contenido orgánico "Aprende a leer y escribir con Pinti"

Todos los agentes leen este archivo ANTES de trabajar. Si algo choca con él, gana el brief.

## Producto
- Nombre exacto: **Aprende a leer y escribir con Pinti** (nunca "Aprendo…").
- Libro imprimible para niños de **3 a 6 años** para aprender a leer y escribir en casa.
- Contenido: letras para trazar (UNA sola línea punteada por el centro, nunca contorno doble), sílabas, sílabas trabadas, mini-cuentos de Pinti, "Escribo mi nombre", medallas para recortar, hojas de pauta en blanco.
- El niño hace todo **solo** (sin dictados ni actividades guiadas por papá/mamá). Cada actividad cabe en una página. Sin fondos de color bajo los trazos (imprime bien en blanco y negro).
- Precio: $9 (antes $18). El precio NUNCA se dice en voz; si aparece, solo en pantalla.
- Link único: https://aprendeconpinti.lovable.app
- El libro real está en `pinti-organico/assets/` (portada, 88 páginas, ilustraciones y Pinti en PNG). Mira `assets/indice.md` antes de trabajar.
- **Pinti es un crayón naranja** (ver `assets/pinti.png`). Personajes del libro: su mamá (crayón rosa con lazo), su papá, el pato Pepe, la vaca y el gato. Nunca rediseñes a Pinti.
- Mercados: Chile, Perú, México, Colombia, Ecuador → español LATAM neutro (prohibido "peque", "vale", "guay", "vosotros").

## Público
Mamás y papás de niños 3–6 años, cansados de pantallas, preocupados porque su hijo "no se concentra", "aún no reconoce letras", "entra al cole y no sabe escribir su nombre".

## Estilo visual (orgánico) — OBLIGATORIO
- Formato vertical **1080x1920 (9:16)**, 30 fps, para TikTok / Reels / Shorts.
- Diseño **tierno, acogedor, cálido**, que a los padres les guste mirar. Paleta suave y luminosa.
- **Animación real** (movimiento constante, cámara viva, personajes con volumen y ojos expresivos). PROHIBIDO: tarjetas estáticas, look de contorno navy grueso + sombra dura, estética escolar fría.
- **Gancho directo desde el primer segundo** (nada de logo ni intro).
- Sin fade-in desde negro ni fade-out a negro.
- Mostrar páginas reales del libro y la portada con claridad cuando el vídeo lo pida.
- Pinti es la mascota/protagonista; las animaciones se hacen por código (PIL/numpy/ffmpeg, ver `src/engine.py` como base técnica).

## Audio
- ElevenLabs SOLO para voces, efectos de sonido y música. **PROHIBIDO generar imágenes o vídeo con ElevenLabs.**
- Narradora preferida: Liz (Sweet & Warm Storyteller). Frases de niños ("¡Me aburro!") con voces de niño, nunca la narradora.
- Ritmo rápido y fluido, sin pausas muertas. Texto en pantalla sincronizado con la voz.
- SFX sincronizados al frame con lo que pasa en pantalla y SIEMPRE por debajo de la voz (voz ≈ -14 LUFS, SFX/música 10–14 dB por debajo).
- Antes de una tanda de generaciones, decir a Wal cuántos créditos aproximados se van a gastar y esperar su OK.
- Si hay canción: dar primero la letra a Wal antes de generar.

## Entrega
- Primero el vídeo completo comprimido (<30 MB). La versión HQ por partes solo si la pide.
- Nombres de archivo reales y descriptivos (ej. `pinti_org_03_letra_m.mp4`).
- Audios: dar el enlace directo.

## Datos
- Nunca inventar métricas, vistas ni tendencias. Todo dato viene de Metricool, de búsquedas web reales o de lo que diga Wal. Si no hay dato, se dice "sin dato".
