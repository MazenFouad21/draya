# Synthesizes the soundtrack for youth-ad.html (27s, 120 BPM), synced to its scene cuts.
# Usage: python3 ads/make-beat.py  -> ads/youth-ad.wav
import wave, os
import numpy as np

SR, DUR, BPM = 44100, 27.0, 120
BEAT = 60 / BPM
rng = np.random.default_rng(7)
mix = np.zeros(int(SR * DUR))

def add(sig, at, gain=1.0):
    i = int(at * SR)
    sig = sig[: max(0, len(mix) - i)]
    mix[i:i + len(sig)] += sig * gain

def env(n, decay):
    return np.exp(-np.arange(n) / (decay * SR))

def kick():
    n = int(.35 * SR); t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .12)

def hat():
    n = int(.06 * SR); w = np.diff(rng.standard_normal(n + 1))
    return w * env(n, .015) * .5

def clap():
    n = int(.2 * SR); w = rng.standard_normal(n)
    w = np.convolve(w, np.ones(6) / 6, 'same') - np.convolve(w, np.ones(40) / 40, 'same')
    return w * env(n, .05) * 1.4

def tone(freq, length, decay, shape=np.sin):
    n = int(length * SR); t = np.arange(n) / SR
    return shape(2 * np.pi * freq * t) * env(n, decay)

def riser(length):
    n = int(length * SR); w = rng.standard_normal(n)
    w = w - np.convolve(w, np.ones(30) / 30, 'same')
    return w * np.linspace(0, 1, n) ** 2 * .5

def impact(big=True):
    n = int((1.2 if big else .4) * SR); t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (38 + 60 * np.exp(-t * 12)) * t) * env(n, .35 if big else .1)
    noise = rng.standard_normal(n) * env(n, .06) * .6
    return (boom + noise) * (1.0 if big else .6)

# A minor loop: Am F C G (one chord per bar)
ROOTS = [55.0, 43.65, 65.41, 49.0]
CHORDS = [[220, 261.6, 329.6], [174.6, 220, 261.6], [261.6, 329.6, 392], [196, 246.9, 293.7]]
PARENTS = (13.4, 18.0)

for b in range(int(DUR / BEAT)):
    t = b * BEAT; bar = (b // 4) % 4; beat_in_bar = b % 4
    in_parents = PARENTS[0] <= t < PARENTS[1]
    if t >= 25.5: break
    if not in_parents or beat_in_bar == 0:
        add(kick(), t, .9 if not in_parents else .5)
    if t >= 2.8 and not in_parents:
        add(hat(), t + BEAT / 2, .35)
        add(tone(ROOTS[bar], BEAT * .9, .25, lambda x: np.sign(np.sin(x)) * .5 + np.sin(x) * .5), t, .28)
    if t >= 5.6 and not in_parents and beat_in_bar in (1, 3):
        add(clap(), t, .5)
    if beat_in_bar == 0 and (in_parents or t >= 18):
        pad = sum(tone(f, BEAT * 4, 1.2) for f in CHORDS[bar]) / 3
        add(pad, t, .35 if in_parents else .18)

for at in (.35, .65, .95):  # notification dings
    add(tone(1318.5, .25, .06) + tone(1975.5, .25, .04) * .5, at, .35)
for start, end in ((3.3, 4.3), (7.0, 7.9), (21.0, 22.0)):
    add(riser(end - start), start, .6)
for at in (4.3, 7.9, 22.0):
    add(impact(True), at, .9)
for at in (2.8, 5.6, 9.0, 10.1, 11.2, 12.3, 13.4, 18.0):
    add(impact(False), at, .7)

fade = int(1.5 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)
mix = np.tanh(mix * 1.3)
mix /= np.abs(mix).max() / .9

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'youth-ad.wav')
with wave.open(out, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('wrote', out)
