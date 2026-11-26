"""La letra de Vale, letra a letra. La usan el arte (SVG) y el render (PIL) para que la nota que ESCRIBE sea
exactamente la misma que luego se enseña: torcida, apretada y con letras deformes (casi no se entiende)."""
import random
CAMBIA = {"a": "o", "g": "q", "t": "l", "u": "v", "e": "c", "n": "u"}
def glifos(lineas, seed=3, x0=76, y0=104, dy=56, tam=(50, 76)):
    r = random.Random(seed); out = []
    for i, linea in enumerate(lineas):
        x = x0 + r.uniform(0, 26); y = y0 + i * dy
        for ch in linea:
            if ch == " ": x += 16; continue
            sz = r.uniform(*tam); g = CAMBIA.get(ch, ch) if r.random() < .45 else ch
            out.append((g, round(x, 1), round(y + r.uniform(-15, 16), 1), round(sz, 1), round(r.uniform(-36, 36), 1)))
            x += sz * r.uniform(.2, .36)
        if r.random() < .6: out.append(("~", round(x + 6, 1), round(y - 6, 1), 60, round(r.uniform(-20, 20), 1)))      # rayón al final de la línea
    return out
NOTA = glifos(("vamos", "al cine", "el sabado?"), 7, 80, 118, 72, (60, 88))
