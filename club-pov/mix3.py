"""Mezcla v3: voz + música + efectos de ElevenLabs con diseño de sonido profesional.
- recorta el silencio inicial de cada efecto y alinea su golpe con el fotograma exacto
- niveles por sonoridad real (RMS activo), no por pico: nada pasa por encima de la voz
- whooshes con variaciones (velocidad/tono) para que no suenen todos iguales
- ambientes filtrados (sin siseo ni graves sucios) y con fundidos largos
- música y ambiente bajan automáticamente cuando hay voz (ducking suave)
"""
import os, subprocess, wave
import numpy as np
import render as R

SR = 44100
N = int(R.TOTAL * SR) + SR
FX = os.path.join(R.HERE, "sfx")
db = lambda v: 10 ** (v / 20)

def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()

def ff(x, filt):
    """Pasa un array por un filtro de ffmpeg (EQ, velocidad...)."""
    p = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", filt, "-f", "f32le", "-ar", str(SR), "-ac", "1", "-"],
                       input=x.astype(np.float32).tobytes(), capture_output=True)
    return np.frombuffer(p.stdout, np.float32).copy()

def rms_activo(x):
    a = np.abs(x); m = a.max() + 1e-9
    act = x[a > m * db(-30)]
    return np.sqrt((act ** 2).mean()) if len(act) else m

def norm(x, target_db):
    return x * (db(target_db) / (rms_activo(x) + 1e-9))

def trim(x, thr_db=-36, pre=.008):
    a = np.abs(x); i = np.argmax(a > a.max() * db(thr_db))
    return x[max(0, i - int(pre * SR)):]

def fades(x, fi=.004, fo=.08):
    x = x.copy(); a, b = int(fi * SR), int(fo * SR)
    if len(x) > a + b:
        x[:a] *= np.linspace(0, 1, a); x[-b:] *= np.linspace(1, 0, b)
    return x

def peak_t(x):
    win = int(.015 * SR); e = np.convolve(x ** 2, np.ones(win) / win, "same")
    return np.argmax(e) / SR

_C = {}
def sfx(name, filt=None):
    k = (name, filt)
    if k not in _C:
        p = os.path.join(FX, name + ".mp3")
        if not os.path.exists(p): _C[k] = None
        else:
            x = load(p)
            if filt: x = ff(x, filt)
            _C[k] = fades(trim(x))
    return _C[k]

voice = np.zeros(N, np.float32); fx = np.zeros(N, np.float32); amb = np.zeros(N, np.float32); mus = np.zeros(N, np.float32)

def put(buf, x, t, gain_db=0.0, dur=None, align="start"):
    """align: 'start' empieza en t · 'peak' su golpe cae en t · 'end' termina en t."""
    if x is None: return
    if dur: x = fades(x[: int(dur * SR)], 0.004, min(.25, dur / 3))
    if align == "peak": t -= peak_t(x)
    if align == "end": t -= len(x) / SR
    i = int(t * SR)
    if i < 0: x = x[-i:]; i = 0
    x = x[: max(0, len(buf) - i)]
    buf[i:i + len(x)] += db(gain_db) * x

def loop(x, dur, xf=1.5):
    """Bucle sin cortes (fundido cruzado entre repeticiones) con fundido de entrada/salida."""
    n = int(dur * SR); f = int(xf * SR)
    out = np.zeros(n + len(x), np.float32); pos = 0
    while pos < n:
        seg = x.copy(); seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
        out[pos:pos + len(seg)] += seg; pos += len(seg) - f
    out = out[:n]; g = int(1.0 * SR); out[:g] *= np.linspace(0, 1, g); out[-g:] *= np.linspace(1, 0, g)
    return out

# ------------------------------------------------------------ VOZ (referencia: -20 dB RMS activo)
for lid, *_ in R.LINEAS:
    x = load(os.path.join(R.VOZ, lid + ".wav"))
    put(voice, norm(ff(x, "highpass=f=70"), -20), R.S(lid))

# ------------------------------------------------------------ niveles de cada efecto (dB RMS activo)
L = dict(whoosh=-31, boom=-29, stamp=-27, pop=-31, pen=-33, pages=-31, cabra=-29, caja=-29, monedas=-31,
         sobre=-30, coche=-30, riser=-29, latido=-30, telefono=-30, contador=-31)
def S_(name, filt=None):
    x = sfx(name, filt)
    return None if x is None else norm(x, L.get(name, -30))

def at(name, t, align="start", dur=None, d=0.0, filt=None):
    put(fx, S_(name, filt), t, d, dur, align)

# whooshes: 3 variantes que se alternan (más grave / normal / más aguda), golpe justo en el corte
WH = [("whoosh", "asetrate=44100*0.82,aresample=44100,highpass=f=120"),
      ("whoosh", "highpass=f=150"),
      ("whoosh", "asetrate=44100*1.18,aresample=44100,highpass=f=200")]
for i, (t, _) in enumerate(R.SCENES[1:]):
    n, f = WH[i % 3]
    at(n, t + .05, "peak", dur=.9, d=-1.5 if i % 2 else 0, filt=f)

# ---------- gancho
at("boom", R.WT("N01", "Heredas") + .05, "peak", d=-3)
at("cabra", R.WT("N01", "cabra"), "start", d=-2)
at("contador", R.WT("N01", "182.400"), "start", d=-1)
at("stamp", R.WT("N01", "182.400") + .3, "peak", d=-2)
at("stamp", R.WT("N01", "21") + .3, "peak", d=-2)
# ---------- notaría: teléfono, testamento y firma
at("telefono", R.WT("N02", "Hacía") - .1, "start", d=-4)
at("pen", R.S("N03") + .7, "start", dur=1.6, d=-3)
at("boom", R.WT("N03", "Un") - .02, "peak")
at("stamp", R.WT("N03", "Un") + .55 + .18, "peak")
# ---------- escudo
at("pop", R.WT("N04", "Última") + .12, "peak")
at("stamp", R.WT("N04", "43") + .2, "peak", d=-3)
# ---------- ultimátum
at("pages", R.S("N05") + .2, "start", dur=1.1)
at("pop", R.WT("N05", "11") + .1, "peak", d=-2)
at("boom", R.WT("N05", "desaparece.") + .05, "peak", d=-4)
# ---------- coche de noche (lejos, filtrado)
put(fx, S_("coche", "lowpass=f=2500,volume=0.9"), R.S("N06") - .8, -6, 4.5)
# ---------- campo
x = sfx("estadio", "highpass=f=120,lowpass=f=9000")
if x is not None: put(amb, norm(loop(x, R.E("N07") - R.S("N07") + 1.6), -33), R.S("N07") - .5)
at("cabra", R.WT("N07", "cabra"), "start", d=-3)
# ---------- vestuario (Paco)
x = sfx("vestuario", "highpass=f=150,lowpass=f=7000")
if x is not None: put(amb, norm(loop(x, R.E("N10") - R.S("N08") + 1.6), -35), R.S("N08") - .5)
at("pop", R.WT("N08", "Paco.") + .25, "peak", d=-3)
# ---------- plantilla
at("pop", R.WT("N11", "tres.") + .1, "peak")
for w in ("Ramón:", "Josito:"): at("pop", R.WT("N12", w) + .15, "peak", d=-2)
at("pop", R.WT("N12", "el") + .15, "peak", d=-2)
at("boom", R.E("N12") + .2, "peak", d=-2)
# ---------- caja fuerte
at("caja", R.S("N14") - .15, "start")
at("monedas", R.WT("N14", "312"), "start", d=-2)
at("contador", R.WT("N14", "312"), "start", d=-5)
at("sobre", R.WT("N14", "sobre"), "start")
# ---------- carta
at("boom", R.WT("N15", "Debajo") - .1, "peak", d=-6)
# ---------- coche de Arturo
at("coche", R.S("N16") - 1.2, "start", dur=4.8)
# ---------- Arturo
at("contador", R.S("N17") + .1, "start", d=-2)
at("stamp", R.WT("N17", "pisos.") + .18, "peak")
at("pop", R.WT("N18", "presidente") + .15, "peak", d=-2)
at("pop", R.WT("N19", "viejo.") + .15, "peak", d=-2)
at("stamp", R.WT("N19", "banco") + .18, "peak")
# ---------- decisión
at("riser", R.S("N20") - .05, "end")
at("boom", R.S("N20") + .02, "peak")
at("stamp", R.S("N20") - .05, "peak", d=-4)
at("pop", R.WT("N20", "¿Vendes") + .2, "peak")
at("pop", R.WT("N20", "luchas") + .2, "peak")
x = sfx("latido", "lowpass=f=900")
if x is not None:
    put(fx, norm(loop(x, R.TOTAL - R.S("N20") - .4, .3), L["latido"]), R.S("N20") + .4, -4)
at("pop", R.S("N21") + .2, "peak", d=-2)
at("pop", R.WT("N21", "parte") + .2, "peak", d=-2)

# ------------------------------------------------------------ música (muy de fondo)
m = sfx("musica", "highpass=f=60")
if m is not None:
    mm = loop(m, R.TOTAL, 2.0) if len(m) < R.TOTAL * SR else fades(m[: int(R.TOTAL * SR)], .01, 1.5)
    put(mus, norm(mm, -34), 0)
    g0, g1 = R.E("N19") + .05, R.S("N20")
    a, b = int(g0 * SR), int(g1 * SR); mus[a:b] *= np.linspace(1, .25, b - a); mus[b:] *= .55

# ------------------------------------------------------------ techo: los efectos nunca por encima de la voz
def env_rms(b, w=2205):
    return np.sqrt(np.convolve(b ** 2, np.ones(w) / w, mode="same") + 1e-12)
_v = env_rms(voice); techo = db(20 * np.log10(np.median(_v[_v > db(-45)])) - 4)
for buf in (fx, amb):
    e = env_rms(buf); g = np.minimum(1.0, techo / e)
    g = np.convolve(g, np.ones(441) / 441, mode="same")          # sin clics
    buf *= g.astype(np.float32)

# ------------------------------------------------------------ ducking y suma
env = np.convolve(np.abs(voice), np.ones(4410) / 4410, mode="same")
talk = np.clip(env / (env.max() * .25 + 1e-9), 0, 1)
talk = np.convolve(talk, np.ones(8820) / 8820, mode="same")          # suaviza (sin bombeo)
mix = voice + mus * db(-4 * talk) + amb * db(-5 * talk) + fx * db(-3 * talk)
mix = mix / max(1.0, np.abs(mix).max() / .95)
with wave.open(os.path.join(R.TMP, "mix.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix[: int(R.TOTAL * SR)] * 32767).astype(np.int16).tobytes())
# informe de niveles
def lev(b): return 20 * np.log10(np.sqrt((b ** 2).mean()) + 1e-9)
print(f"mix ok {R.TOTAL:.1f}s  voz {lev(voice):.1f}  música {lev(mus):.1f}  ambiente {lev(amb):.1f}  efectos {lev(fx):.1f} dB")
