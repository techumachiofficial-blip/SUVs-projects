"""Original synthesized background track (no samples, no third-party audio).
Usage: python3 music.py OUT.wav SECONDS
"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 44100
out, dur = sys.argv[1], float(sys.argv[2])
BPM = 112
beat = 60 / BPM
bar = 4 * beat
n_bars = int(np.ceil(dur / bar)) + 1
N = int(n_bars * bar * SR)
rng = np.random.default_rng(7)

def midi(m): return 440 * 2 ** ((m - 69) / 12)
def lp(x, fc, order=2): return sosfilt(butter(order, fc, "low", fs=SR, output="sos"), x)
def hp(x, fc, order=2): return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x)
def env(n, a, r):
    e = np.ones(n); a = min(int(a * SR), n); r = min(int(r * SR), n - a)
    e[:a] = np.linspace(0, 1, a); e[n - r:] = np.linspace(1, 0, r) if r else 1
    return e
def add(buf, sig, t):
    i = int(t * SR); j = min(N, i + len(sig))
    if i < N: buf[i:j] += sig[:j - i]

# Am - F - C - G  (A minor, upbeat "tech" feel)
chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
roots = [45, 41, 48, 43]

pad, bass, arp, drums = (np.zeros(N) for _ in range(4))
for b in range(n_bars):
    t0 = b * bar; ch = chords[b % 4]
    n = int(bar * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for m in ch + [ch[0] + 12]:
        for det in (-0.12, 0.12):
            f = midi(m + det)
            s += 2 * ((t * f) % 1) - 1          # detuned saws
    add(pad, lp(s, 1400) * env(n, 0.25, 0.3) * 0.1, t0)
    # bass: eighth notes, root with octave bounce
    for k in range(8):
        m = roots[b % 4] - 12 + (12 if k % 4 == 3 else 0)
        nn = int(beat / 2 * SR); tt = np.arange(nn) / SR
        x = np.tanh(2.2 * np.sin(2 * np.pi * midi(m) * tt)) * np.exp(-tt * 5)
        add(bass, x * 0.26, t0 + k * beat / 2)
    # pluck arpeggio, 16ths, from bar 2
    if b >= 1:
        seq = [0, 1, 2, 3, 2, 1, 0, 2]
        notes = ch + [ch[0] + 12]
        for k in range(16):
            m = notes[seq[k % 8]] + 12
            nn = int(0.35 * SR); tt = np.arange(nn) / SR
            f = midi(m)
            x = (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt * 14)
            add(arp, x * 0.26, t0 + k * beat / 4)
    # drums from bar 2
    if b >= 1:
        for k in range(4):
            nn = int(0.4 * SR); tt = np.arange(nn) / SR
            f = 50 + 110 * np.exp(-tt * 30)
            kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)
            add(drums, kick * 0.85, t0 + k * beat)
            if k in (1, 3):
                nn2 = int(0.25 * SR); t2 = np.arange(nn2) / SR
                clap = hp(rng.standard_normal(nn2), 900) * np.exp(-t2 * 22) * 0.2
                add(drums, clap, t0 + k * beat)
        for k in range(16):
            nn = int(0.06 * SR); tt = np.arange(nn) / SR
            hat = hp(rng.standard_normal(nn), 7000) * np.exp(-tt * 70) * (0.045 if k % 2 else 0.025)
            add(drums, hat, t0 + k * beat / 4)

# sidechain-style pump on pad/arp
pump = np.ones(N)
for k in range(int(N / SR / beat) + 1):
    i = int((k * beat) * SR); n = int(beat * SR)
    if k * beat >= bar:
        seg = 1 - 0.55 * np.exp(-np.arange(n) / SR * 9)
        pump[i:i + n] = seg[:max(0, min(n, N - i))]

ir_n = int(1.8 * SR)
ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / SR * 3.2)
ir = lp(ir, 5000); ir /= np.sqrt(np.sum(ir ** 2))
wet = fftconvolve((pad + arp) * pump, ir)[:N] * 0.35

mix = (pad + arp) * pump + wet + bass + drums
mix = hp(mix, 30)
st = np.stack([mix, np.concatenate([np.zeros(int(0.012 * SR)), (pad + arp + wet)[:-int(0.012 * SR)]]) * 0.5 + (mix - (pad + arp + wet)) * 1 + (pad + arp + wet) * 0.5], 1)
st = st[:int(dur * SR)]
fade = int(1.5 * SR); st[-fade:] *= np.linspace(1, 0, fade)[:, None]
st[:int(0.05 * SR)] *= np.linspace(0, 1, int(0.05 * SR))[:, None]
st = np.tanh(st * 0.9)
st *= 0.89 / np.max(np.abs(st))
wavfile.write(out, SR, (st * 32767).astype(np.int16))
print("wrote", out, st.shape[0] / SR, "s")
