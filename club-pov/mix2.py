"""Mezcla final: voces + música y efectos de ElevenLabs (sfx/*.mp3), sincronizados con las escenas. Voz siempre por encima."""
import os, subprocess, wave
import numpy as np
import render as R

SR = 44100
N = int(R.TOTAL * SR) + SR
FX = os.path.join(R.HERE, "sfx")

def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()

def add(buf, x, t, g=1.0, dur=None, fade=.25):
    if dur: x = x[: int(dur * SR)]
    x = x.copy(); f = int(fade * SR)
    if len(x) > 2 * f and dur:
        x[-f:] *= np.linspace(1, 0, f)
    i = int(max(0, t) * SR); x = x[: max(0, len(buf) - i)]; buf[i:i + len(x)] += g * x

def loop(x, dur):
    n = int(dur * SR); reps = int(np.ceil(n / len(x))) + 1
    y = np.tile(x, reps)[:n]
    f = int(.6 * SR); y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f)
    return y

def sfx(name):
    p = os.path.join(FX, name + ".mp3")
    if not os.path.exists(p): return None
    x = load(p); return x / (np.abs(x).max() + 1e-9)

voice = np.zeros(N, np.float32); fx = np.zeros(N, np.float32); amb = np.zeros(N, np.float32); mus = np.zeros(N, np.float32)
for lid, *_ in R.LINEAS:
    x = load(os.path.join(R.VOZ, lid + ".wav")); x = x / (np.abs(x).max() + 1e-9) * .9
    add(voice, x, R.S(lid))

m = sfx("musica")
if m is not None:
    mm = loop(m, R.TOTAL) if len(m) < R.TOTAL * SR else m[: int(R.TOTAL * SR)]
    add(mus, mm, 0)
    g0, g1 = R.E("L15") + .05, R.S("L16")       # silencio dramático antes de la decisión
    mus[int(g0 * SR):int(g1 * SR)] *= .2

def at(name, t, g=1.0, dur=None):
    x = sfx(name)
    if x is not None: add(fx, x, t, g, dur)

SC = [t for t, _ in R.SCENES]
for t in SC[1:]: at("whoosh", t - .08, .55)
at("pen", .5, .45, 2.0)
at("boom", R.WT("L01", "Un") - .05, .9)
at("stamp", R.WT("L01", "Un") + .5, .8)
at("pop", R.WT("L02", "Última"), .4)
for w in ("deuda", "43", "cero"): at("pop", R.WT("L03", w), .45)
at("pages", R.S("L04") + .2, .55, 1.1)
at("boom", R.S("L04") + .05, .5)
at("pop", R.WT("L04", "11"), .4)
# ambiente del campo y cabra
x = sfx("estadio")
if x is not None: add(amb, loop(x, R.E("L05") - R.S("L05") + 1.0), R.S("L05") - .3, .5)
at("cabra", R.WT("L05", "cabra"), .55)
# vestuario
x = sfx("vestuario")
if x is not None: add(amb, loop(x, R.E("L07") - R.S("L06") + 1.0), R.S("L06") - .3, .45)
at("pop", R.WT("L08", "tres."), .45)
for w in ("Ramón:", "Josito:"): at("pop", R.WT("L09", w), .45)
at("pop", R.WT("L09", "el"), .45)
at("boom", R.E("L09") + .12, .7)
at("caja", R.S("L11") - .1, .6, 2.2)
at("monedas", R.WT("L11", "312"), .5)
at("sobre", R.WT("L11", "sobre"), .6, 1.6)
at("boom", R.WT("L12", "Debajo") - .15, .45)
at("coche", R.S("L13") + .1, .7, 4.0)
at("stamp", R.WT("L14", "pisos."), .6)
at("riser", R.S("L16") - 2.6, .55, 2.5)
at("boom", R.S("L16"), .8)
x = sfx("latido")
if x is not None: add(fx, loop(x, R.TOTAL - R.S("L16")), R.S("L16"), .55)

# ducking: música y ambiente bajan cuando hay voz; efectos nunca por encima de la voz
env = np.convolve(np.abs(voice), np.ones(2205) / 2205, mode="same")
talk = np.clip(env * 10, 0, 1)
bed = mus * (0.30 - 0.20 * talk) + amb * (0.55 - 0.30 * talk)
fxm = fx * (0.55 - 0.25 * talk)
mix = voice + bed + fxm
mix = mix / max(1.0, np.abs(mix).max() / 0.95)
with wave.open(os.path.join(R.TMP, "mix.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix[: int(R.TOTAL * SR)] * 32767).astype(np.int16).tobytes())
print("mix ok", R.TOTAL)
