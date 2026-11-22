#!/usr/bin/env python3
"""Original synthesized sound for the pixel-loop ad: one soft pop per tile landing
(pitch climbs a pentatonic scale), a whoosh on the opening burst, a shimmer arpeggio,
a pop for the illustration and a whoosh + chime for the end card. 16 s, 44.1 kHz stereo."""
import subprocess, wave, numpy as np

SR, DUR = 44100, 16.0
n = int(SR * DUR)
L = np.zeros(n); R = np.zeros(n)
rng = np.random.default_rng(7)

def add(sig, t, pan=0.0, gain=1.0):
    i = int(t * SR); j = min(n, i + len(sig))
    if i >= n: return
    s = sig[: j - i] * gain
    L[i:j] += s * (1 - max(0, pan)); R[i:j] += s * (1 + min(0, pan))

def pop(freq, dur=0.14):
    t = np.arange(int(SR * dur)) / SR
    f = freq * (1 + 0.6 * np.exp(-t * 60))          # quick downward chirp = "bloop"
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.exp(-t * 28) * (1 - np.exp(-t * 900))
    click = rng.standard_normal(len(t)) * np.exp(-t * 900) * 0.25
    return (np.sin(ph) + 0.25 * np.sin(2 * ph)) * env + click

def whoosh(dur, rising=True):
    m = int(SR * dur); t = np.arange(m) / SR
    noise = rng.standard_normal(m)
    k = np.linspace(0.02, 0.25, m) if rising else np.linspace(0.25, 0.02, m)
    out = np.zeros(m); acc = 0.0
    for i in range(m):                                # one-pole low-pass, sweeping
        acc += k[i] * (noise[i] - acc); out[i] = acc
    return out * np.sin(np.pi * t / dur) ** 2 * 1.6

def bell(freq, dur=1.2):
    t = np.arange(int(SR * dur)) / SR
    return (np.sin(2*np.pi*freq*t) + 0.4*np.sin(2*np.pi*freq*2.01*t) + 0.2*np.sin(2*np.pi*freq*3.02*t)) \
        * np.exp(-t * 3.2) * (1 - np.exp(-t * 400))

lands = [float(x) for x in subprocess.check_output(
    ["python3", "render_clip.py", "--events"], text=True).split()]
scale = [0, 2, 4, 7, 9]
for k, t in enumerate(lands):
    step = k * 15 // len(lands)
    semis = 12 * (step // 5) + scale[step % 5]
    f = 392 * 2 ** (semis / 12)
    add(pop(f), t, pan=np.sin(k * 1.7) * 0.4, gain=0.42)

add(whoosh(0.7, rising=False), 0.0, gain=0.5)
for k, s in enumerate([0, 4, 7, 12, 16]):          # shimmer arpeggio with the sweep
    add(bell(784 * 2 ** (s / 12), 0.9), 8.4 + k * 0.22, pan=(k - 2) * 0.2, gain=0.16)
add(pop(260, 0.22), 8.5, gain=0.5)                  # illustration pops in
add(whoosh(0.9), 13.1, gain=0.45)                   # into the end card
add(bell(1046.5, 1.6), 14.93, gain=0.22)            # card field comes to rest
t = np.arange(n) / SR                               # soft bed so silence never gaps
pad = (np.sin(2*np.pi*98*t) + 0.5*np.sin(2*np.pi*147*t)) * 0.025 * (0.6 + 0.4*np.sin(2*np.pi*0.25*t))
L += pad; R += pad
st = np.stack([L, R], 1)
st /= max(1e-9, np.abs(st).max()) / 0.9
with wave.open("audio.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype("<i2").tobytes())
print("wrote audio.wav", len(lands), "pops")
