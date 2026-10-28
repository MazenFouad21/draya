# Synthesizes the sound-effects track for youth-ad.html (27s): no music, no instruments, no melody —
# only whooshes, impacts, phone vibrations and pops, synced to the animation.
# Usage: python3 ads/make-sfx.py  -> ads/youth-sfx.wav
import wave, os
import numpy as np

SR, DUR = 44100, 27.0
rng = np.random.default_rng(7)
mix = np.zeros(int(SR * DUR))

def add(sig, at, gain=1.0):
    i = int(at * SR)
    sig = sig[: max(0, len(mix) - i)]
    mix[i:i + len(sig)] += sig * gain

def env(n, decay):
    return np.exp(-np.arange(n) / (decay * SR))

def smooth(x, k):
    return np.convolve(x, np.ones(k) / k, 'same')

def whoosh(length=.45, rising=False):
    """Air swish: noise whose brightness and loudness swell then fade."""
    n = int(length * SR); w = rng.standard_normal(n)
    shape = np.sin(np.linspace(0, np.pi, n)) ** (1.5 if rising else 2)
    bright = w - smooth(w, 12)
    dark = smooth(w, 12)
    sweep = np.linspace(0, 1, n) if rising else np.sin(np.linspace(0, np.pi, n))
    return (dark * (1 - sweep) + bright * sweep) * shape * .8

def riser(length):
    n = int(length * SR); w = rng.standard_normal(n)
    return (w - smooth(w, 25)) * np.linspace(0, 1, n) ** 2.5 * .6

def impact(big=True):
    """Deep thud with a short burst of noise — a hit, not a note."""
    n = int((1.0 if big else .35) * SR); t = np.arange(n) / SR
    thud = np.sin(2 * np.pi * (35 + 70 * np.exp(-t * 25)) * t) * env(n, .25 if big else .07)
    crack = smooth(rng.standard_normal(n), 3) * env(n, .03 if big else .015)
    return (thud + crack * .7) * (1.0 if big else .55)

def vibrate(length=.3):
    """Phone buzzing on a table."""
    n = int(length * SR); t = np.arange(n) / SR
    motor = np.sign(np.sin(2 * np.pi * 170 * t)) * .5 + smooth(rng.standard_normal(n), 30) * .5
    gate = (np.sin(2 * np.pi * 14 * t) > -.2).astype(float)
    return smooth(motor * gate, 8) * np.sin(np.linspace(0, np.pi, n)) ** .3 * .7

def pop():
    """Short tap/click as a card appears."""
    n = int(.06 * SR)
    return smooth(rng.standard_normal(n), 2) * env(n, .008)

def swipe(length=.3):
    n = int(length * SR); w = rng.standard_normal(n)
    return (w - smooth(w, 4)) * np.linspace(.2, 1, n) * env(n, .12) * .5

# phone notifications sliding in
for at in (.35, .65, .95):
    add(vibrate(), at, .7)
# "٩ ساعات" slam
add(impact(False), 1.5, .8)
# scene cuts
for at in (2.8, 5.6, 9.0, 10.1, 11.2, 12.3, 13.4, 18.0, 22.0):
    add(whoosh(), at - .2, .7)
# build-ups and big hits
for start, end in ((3.4, 4.3), (6.0, 7.9), (21.2, 22.0)):
    add(riser(end - start), start, .7)
for at in (4.3, 7.9, 22.0):
    add(impact(True), at, 1.0)
# rapid-fire words: a hit on each
for at in (9.0, 10.1, 11.2, 12.3):
    add(impact(False), at + .05, .8)
# parents scene: strike-through and checklist
add(swipe(), 14.8, .8)
for at in (16.0, 16.4, 16.8):
    add(pop(), at + .15, .9)
# course card
add(whoosh(.35, rising=True), 18.1, .5)
for at in (18.7, 19.0, 19.3, 19.6):
    add(pop(), at + .1, .8)
# call to action
for at in (23.0, 23.6, 23.9, 24.2):
    add(pop(), at + .1, .8)

fade = int(.8 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)
mix = np.tanh(mix * 1.2)
mix /= np.abs(mix).max() / .9

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'youth-sfx.wav')
with wave.open(out, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('wrote', out)
