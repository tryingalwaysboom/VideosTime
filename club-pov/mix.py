"""Mezcla: voces (voz/Lxx.wav) + base de tensión + efectos sincronizados con las escenas. Voz siempre por encima."""
import os, subprocess, wave
import numpy as np
import render as R

SR = 44100
N = int(R.TOTAL * SR) + SR
voice = np.zeros(N, np.float32); mus = np.zeros(N, np.float32); fx = np.zeros(N, np.float32)

def load(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32)

def add(buf, x, t, g=1.0):
    i = int(t * SR); x = x[: max(0, len(buf) - i)]; buf[i:i + len(x)] += g * x

for lid, *_ in R.LINEAS:
    p = os.path.join(R.VOZ, lid + ".wav")
    if os.path.exists(p):
        x = load(p); x = x / (np.abs(x).max() + 1e-9) * 0.89
        add(voice, x, R.S(lid))

t = np.arange(N) / SR
# base: dron grave + pulso tipo latido que acelera hacia la decisión
drone = 0.5 * np.sin(2 * np.pi * 55 * t) + 0.25 * np.sin(2 * np.pi * 82.4 * t + np.sin(t * .3)) + 0.15 * np.sin(2 * np.pi * 110 * t)
drone *= 0.6 + 0.4 * np.sin(2 * np.pi * t / 7) ** 2
bpm = 70 + 40 * np.clip((t - R.S("L13")) / 30, 0, 1)
ph = np.cumsum(bpm / 60 / SR)
beat = np.exp(-((ph % 1) * 9)) * np.sin(2 * np.pi * 48 * t)
mus += 0.06 * drone + 0.10 * beat
# silencio dramático justo antes de la decisión
gap0, gap1 = R.E("L15") + .05, R.S("L16")
mus[int(gap0 * SR):int(gap1 * SR)] *= 0.15

rng = np.random.default_rng(1)
def whoosh(d=.45):
    n = int(d * SR); w = rng.standard_normal(n).astype(np.float32)
    k = np.linspace(0, 1, n); env = np.sin(np.pi * k) ** 2
    # filtro paso bajo móvil sencillo
    out = np.zeros(n, np.float32); a = 0
    for i in range(n):
        c = 0.02 + 0.25 * k[i]; a += c * (w[i] - a); out[i] = a
    return out * env * 1.6
def thud(f=60, d=.5):
    n = int(d * SR); k = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * k * (1 - .4 * k)) * np.exp(-k * 9) + .3 * rng.standard_normal(n) * np.exp(-k * 40)).astype(np.float32)
def ding(f=1320, d=.6):
    k = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * f * k) * np.exp(-k * 7) + .4 * np.sin(2 * np.pi * f * 2 * k) * np.exp(-k * 10)).astype(np.float32)
def tick():
    k = np.arange(int(.05 * SR)) / SR
    return (np.sin(2 * np.pi * 2200 * k) * np.exp(-k * 120)).astype(np.float32)

W = whoosh()
for t0, _ in R.SCENES[1:]:
    add(fx, W, t0 - .15, .35)
add(fx, thud(70), R.E("L01") - .9, .9)                       # sello HEREDADO
for k in (0, .33, .68):                                       # cifras
    add(fx, thud(90, .3), R.S("L03") + .1 + (R.E("L03") - R.S("L03")) * k, .6)
add(fx, thud(50, .8), R.S("L04") + .05, .9)                   # 21 días
for i in range(5): add(fx, tick(), R.S("L04") + .6 + i * .18, .5)
add(fx, ding(1600), R.S("L11") + (R.E("L11") - R.S("L11")) * .35, .35)   # 312 €
s9, e9 = R.TL["L09"]
for k in (0, .33, .7): add(fx, thud(110, .25), s9 + (e9 - s9) * k, .5)
add(fx, thud(45, .9), R.E("L09") + .15, .9)                   # menos de 7
add(fx, thud(60, .6), R.S("L14") + (R.E("L14") - R.S("L14")) * .7, .7)   # pisos
add(fx, thud(40, 1.0), R.S("L16"), .9)

mix = voice + mus * 0.55 + fx * 0.45
# ducking: base y efectos bajan cuando hay voz
env = np.convolve(np.abs(voice), np.ones(2205) / 2205, mode="same")
duck = 1 - 0.55 * np.clip(env * 8, 0, 1)
mix = voice + (mus * 0.55 + fx * 0.45) * duck
mix = mix / max(1.0, np.abs(mix).max() / 0.95)
with wave.open(os.path.join(R.TMP, "mix.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix[: int(R.TOTAL * SR)] * 32767).astype(np.int16).tobytes())
print("mix ok", R.TOTAL)
