"""Mezcla del Ep.1 crypto: recoloca los tramos de narr.mp3, mete las otras voces y los efectos (si existen).
Los efectos nunca por encima de la voz."""
import os, subprocess
import numpy as np
import render as R

SR = 44100
AUD = R.AUD

def load(name, af=None):
    p = os.path.join(AUD, name)
    if not os.path.exists(p): return None
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p] + (["-af", af] if af else []) + ["-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()

def fade(x, ms=12):
    n = min(len(x) // 2, int(SR * ms / 1000))
    if n: x[:n] *= np.linspace(0, 1, n); x[-n:] *= np.linspace(1, 0, n)
    return x

out = np.zeros(int(SR * (R.TOTAL + 1)), np.float32)
def add(x, t, g=1.0):
    if x is None: return
    i = int(t * SR); x = x[: len(out) - i]; out[i:i + len(x)] += x * g

narr = load("narr.mp3")
for lid, (t0, t1, s0, src, ws) in R.TL.items():
    if src == "narr.mp3":
        add(fade(narr[int(s0 * SR):int((s0 + t1 - t0) * SR)].copy()), t0)
    elif src == "tv.mp3":   # suena a tele de tubo
        add(fade(load(src, "highpass=f=300,lowpass=f=3400,aecho=0.8:0.5:18:0.2")), t0, .9)
    elif src:
        add(fade(load(src)), t0, 1.0)

voz_rms = np.sqrt(np.mean(out[out != 0] ** 2))
# efectos (sólo los que existan en descargas/crypto_ep1), ganancias por debajo de la voz
SFX = [("sfx_whoosh.mp3", R.WT("N01", "2009") - .6, .14), ("sfx_alarm.mp3", R.S("N02") - .3, .13), ("sfx_alarm.mp3", R.S("N02") + 1.6, .10),
       ("sfx_steps.mp3", R.WT("N05", "run"), .14), ("sfx_spill.mp3", R.S("D02") + .4, .35),
       ("sfx_pc.mp3", R.WT("N12", "turn"), .28), ("sfx_click.mp3", R.WT("N14", "generate") + .2, .3),
       ("sfx_glitch.mp3", R.WT("N16", "flickers"), .32), ("sfx_heart.mp3", R.S("N18") - .3, .35)]
MAXDUR = {"sfx_spill.mp3": 2.2, "sfx_pc.mp3": 2.0}
for name, t, g in SFX:
    x = load(name)
    if x is not None and name in MAXDUR: x = fade(x[:int(MAXDUR[name] * SR)].copy(), 120)
    add(x, t, g)

pk = np.max(np.abs(out)); out *= min(1.0, .95 / pk) if pk else 1
dst = os.path.join(R.TMP, "audio.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", "loudnorm=I=-15:TP=-1.5:LRA=11",
                "-ar", str(SR), "-ac", "2", dst], input=out.tobytes(), check=True)
print("ok", dst, round(len(out) / SR, 2))
