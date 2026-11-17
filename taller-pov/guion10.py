# Ep.10 CORTO "Cara a cara" (elegisteis la A: entrar). ~50 s. Estilo viral: gancho en el frame 0, golpe visual cada 3-4 s.
import re
VOCES = {
    "N": "orF2qy9215xjwqqxqsWW",   # narrador (Rafael)
    "M": "xH6DmlUWSqhSmFog5gxa",   # Manolo
    "L": "iHGx33VgO2KQ1Fdw6noG",   # Lucía
    "X": "HMCmDsbKeaSZp5LMOYKR",   # Nitro (Johnny The Rogue)
    "P": "x3VvCTOrOImnliuxR9Pq",   # padre de Lucía (Aldo)
}
RAW = [
 ("G01","N","Elegisteis la A: entrar y plantarle cara. Nitro abre la puerta de una patada."),
 ("G02","X","[shouting] ¡Suelte ese cajón!"),
 ("G03","N","El hombre ni se inmuta. Se quita el sombrero… y sonríe."),
 ("G04","P","[calm] Llegáis tarde, chicos. Muy tarde."),
 ("G05","L","[voice breaking] Papá… ¿qué haces aquí?"),
 ("G06","P","[quietly] Lo que Rubén me pidió. Firmé el pacto para proteger el taller."),
 ("G07","X","[tense] ¿Proteger? Hay una deuda de sesenta y cuatro mil euros."),
 ("G08","N","El padre de Lucía deja una llave oxidada sobre el banco."),
 ("G09","P","[serious] Esa deuda no es de Rubén. Es de quien os persigue desde el noventa y seis."),
 ("G10","N","Fuera, unos faros se encienden. Tres coches frenan en seco."),
 ("G11","P","[urgent] Son ellos. Han venido a por el contrato."),
 ("G12","X","[tense] Pues que vengan. El contrato lo tengo yo."),
 ("G13","N","Nitro saca el papel. Y el padre de Lucía… extiende la mano."),
 ("G14","N","Tú eliges: o confías en él… o te llevas el contrato y huyes."),
 ("G15","N","Confiar. O huir."),
 ("G16","N","Comenta confiar o huir: la parte once la decides tú."),
]
_STOP = set("para como pero esta este esas esos todo toda nunca desde antes entre sobre porque donde quien aquel aquí ahora siempre hacia hasta cuando".split())
def _cap(txt):
    txt = re.sub(r"\[[^\]]*\]\s*", "", txt)
    ws = txt.split(); out = []
    for i, w in enumerate(ws):
        core = re.sub(r"[^\wáéíóúüñÁÉÍÓÚÑ]", "", w)
        key = (len(core) >= 6 and core.lower() not in _STOP) or i == len(ws) - 1
        out.append("*" + w + "*" if key else w)
    return " ".join(out)
LINEAS = [(i, v, re.sub(r"\[[^\]]*\]\s*", "", t), _cap(t)) for i, v, t in RAW]
