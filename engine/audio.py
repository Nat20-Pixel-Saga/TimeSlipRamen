"""Generated sound: four lo-fi tracks, weather, the shop's simmering pot, and every effect.

Nothing here is sampled: instruments are small synthesis recipes (FM electric piano,
Karplus-Strong koto and shamisen, breathy flute, music-box bells, soft drums), so the
music is original and free of any licence or Content ID claim.
"""
import math
import wave

import numpy as np
from scipy.signal import lfilter, butter, sosfilt

SR = 48000
_rng = np.random.default_rng(11)


def rng(seed):
    return np.random.default_rng(seed)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def add(buf, sig, t, gain=1.0):
    i = int(round(t * SR))
    if i >= len(buf) or i + len(sig) <= 0:
        return
    j0 = max(0, -i)
    n = min(len(sig) - j0, len(buf) - (i + j0))
    if n > 0:
        buf[i + j0:i + j0 + n] += sig[j0:j0 + n] * gain


def env_ad(n, att, dec):
    t = np.arange(n) / SR
    e = np.exp(-t / dec)
    a = max(1, int(att * SR))
    e[:a] *= np.linspace(0, 1, a)
    return e


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], 'bandpass', fs=SR, output='sos'), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, 'lowpass', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, 'highpass', fs=SR, output='sos'), x)


def reverb(x, wet):
    out = np.zeros_like(x)
    for d, g in ((1557, 0.78), (1617, 0.77), (1491, 0.79), (1422, 0.80)):
        a = np.zeros(d + 1)
        a[0] = 1
        a[d] = -g
        out += lfilter([1], a, x)
    for d, g in ((225, 0.5), (556, 0.5)):
        b = np.zeros(d + 1)
        b[0] = -g
        b[d] = 1
        a = np.zeros(d + 1)
        a[0] = 1
        a[d] = -g
        out = lfilter(b, a, out)
    return x + wet * lp(out, 5000) * 0.25


# ============================================================================ instruments
def ep(m, dur, vel=1.0):
    f = mtof(m)
    n = int((dur + 1.2) * SR)
    t = np.arange(n) / SR
    idx = 1.3 * np.exp(-t / 0.35) + 0.15
    s = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    s += 0.12 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.25)
    s *= 1 + 0.08 * np.sin(2 * np.pi * 4.3 * t)
    e = env_ad(n, 0.006, 1.8)
    rel = np.clip((dur + 0.35 - t) / 0.35, 0, 1)
    return s * e * rel * vel


def pluck(m, vel=1.0, dur=2.6, bright=0.6, decay=0.996, r=None):
    """Karplus-Strong string: bright=0.6 koto, 0.9 shamisen-ish."""
    r = r if r is not None else _rng
    f = mtof(m)
    N = max(2, int(round(SR / f - 0.5)))
    n = int(dur * SR)
    exc = np.zeros(n)
    burst = r.uniform(-1, 1, N)
    burst = lfilter([bright, 1 - bright], [1], burst)
    exc[:N] = burst
    g = decay if m < 76 else decay - 0.003
    a = np.zeros(N + 2)
    a[0] = 1
    a[N] = -0.5 * g
    a[N + 1] = -0.5 * g
    y = lfilter([1.0], a, exc)
    t = np.arange(n) / SR
    y += 0.25 * np.sin(2 * np.pi * f * t) * np.exp(-t / 0.5)
    y *= np.clip((dur - t) / 0.3, 0, 1)
    return y * vel


def koto(m, vel=1.0, dur=2.6, r=None):
    return pluck(m, vel, dur, 0.6, 0.996, r)


def shamisen(m, vel=1.0, dur=1.4, r=None):
    y = pluck(m, vel, dur, 0.95, 0.990, r)
    t = np.arange(len(y)) / SR
    y += 0.15 * np.sign(np.sin(2 * np.pi * mtof(m) * t)) * np.exp(-t / 0.03) * vel
    return hp(y, 180)


def bell(m, vel=1.0, dur=2.2):
    f = mtof(m)
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.9)
    s += 0.35 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t / 0.35)
    s += 0.18 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / 0.12)
    s[:60] *= np.linspace(0, 1, 60)
    return s * vel * 0.8


def flute(m, dur, vel=1.0, r=None):
    r = r if r is not None else _rng
    f = mtof(m)
    n = int((dur + 0.25) * SR)
    t = np.arange(n) / SR
    scoop = -0.035 * np.exp(-t / 0.09)
    vib = 0.006 * np.clip((t - 0.35) / 0.4, 0, 1) * np.sin(2 * np.pi * 5.2 * t)
    ph = 2 * np.pi * np.cumsum(f * (1 + scoop + vib)) / SR
    s = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.06 * np.sin(3 * ph)
    breath = bp(r.standard_normal(n), f * 0.8, min(f * 3.0, 15000)) * 0.35
    e = np.clip(t / 0.09, 0, 1) * np.clip((dur + 0.12 - t) / 0.2, 0, 1) * (1 - 0.15 * t / (dur + 0.25))
    return (s + breath) * e * vel


def bass(m, dur, vel=1.0):
    f = mtof(m)
    n = int((dur + 0.3) * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t) + 0.08 * np.sin(6 * np.pi * f * t)
    e = env_ad(n, 0.012, 1.6) * np.clip((dur + 0.15 - t) / 0.15, 0, 1)
    return s * e * vel


def kick(vel=1.0, r=None):
    r = r if r is not None else _rng
    n = int(0.4 * SR)
    t = np.arange(n) / SR
    f = 48 + 75 * np.exp(-t / 0.035)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22)
    s[:120] += r.uniform(-0.3, 0.3, 120) * np.linspace(1, 0, 120)
    return s * vel


def snare(vel=1.0, r=None, brush=False):
    r = r if r is not None else _rng
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    nz = bp(r.standard_normal(n), 1400, 6000) * np.exp(-t / (0.14 if brush else 0.09))
    tone = np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.05)
    return (0.7 * nz + (0.15 if brush else 0.5) * tone) * vel


def hat(vel=1.0, r=None):
    r = r if r is not None else _rng
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    return hp(r.standard_normal(n), 7000) * np.exp(-t / 0.022) * vel


def rim(vel=1.0):
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1700 * t) * np.exp(-t / 0.012) + 0.4 * np.sin(2 * np.pi * 820 * t) * np.exp(-t / 0.02)) * vel


# ============================================================================ the tracks
CH = {
    'G': ([55, 59, 62, 66, 69], 43), 'A': ([55, 61, 64, 66], 45), 'F#m': ([57, 61, 64, 66], 42),
    'Bm': ([59, 62, 66, 69], 47), 'Em': ([55, 59, 62, 66], 40), 'D': ([54, 57, 61, 64], 38),
    # Paper Lantern (A minor)
    'Am9': ([55, 60, 64, 71], 45), 'Fmaj7': ([57, 60, 64, 65], 41), 'G6': ([55, 59, 62, 64], 43),
    'Em7': ([55, 59, 62, 64], 40), 'Dm9': ([57, 60, 64, 65], 38), 'G13': ([53, 59, 64, 65], 43),
    'Cmaj7': ([55, 59, 60, 64], 36), 'E7': ([56, 59, 62, 64], 40),
    # Snow on the Noren (G major)
    'Gmaj7': ([54, 59, 62, 67], 43), 'Bm7': ([57, 62, 66, 69], 47), 'Cmaj9': ([59, 62, 64, 67], 36),
    'D6': ([57, 59, 62, 66], 38), 'Em9': ([55, 59, 62, 66], 40), 'Am7': ([55, 60, 64, 67], 45),
    'D7sus': ([55, 60, 62, 67], 38),
    # Night Market (F major)
    'Fmaj9': ([60, 64, 67, 69], 41), 'Gm7': ([58, 62, 65, 69], 43), 'Am7b': ([60, 64, 67, 69], 45),
    'C7': ([58, 64, 67, 70], 36), 'Bbmaj7': ([57, 62, 65, 69], 46), 'Csus': ([60, 65, 67, 70], 36),
    'Dm7': ([57, 60, 65, 69], 38),
}

TRACKS = {
    'last_bowl': dict(
        title='Last Bowl', bpm=76, lead='koto', lead_b='flute', drums=1, bells=False,
        prog={'A': ['G', 'A', 'F#m', 'Bm'], 'B': ['Em', 'A', 'D', 'Bm'], 'end': ['D', 'D']},
        mel={
            'A1': [(0.5, 78, .5), (1, 76, .5), (1.5, 74, 1), (3, 71, .5), (3.5, 74, .5), (4, 76, 1.5), (5.5, 78, .5),
                   (6, 81, 1), (7.5, 78, .5), (8, 76, 1), (9, 73, .5), (9.5, 69, 1.5), (11.5, 71, .5), (12, 74, 1),
                   (13, 71, .5), (13.5, 69, .5), (14, 71, 2)],
            'A2': [(0, 81, 1), (1, 78, .5), (1.5, 76, .5), (2, 78, 1.5), (3.5, 74, .5), (4, 76, 1), (5, 73, .5),
                   (5.5, 76, .5), (6, 69, 2), (8.5, 73, .5), (9, 76, .5), (9.5, 78, 1), (10.5, 76, .5), (11, 73, 1),
                   (12, 74, 3), (15, 69, .5), (15.5, 71, .5)],
            'B1': [(0, 71, 1.5), (1.5, 74, .5), (2, 76, 2), (4, 73, 1), (5, 76, 1), (6, 78, 2), (8, 81, 2.5),
                   (10.5, 78, .5), (11, 76, 1), (12, 74, 2), (14, 71, 2)],
            'B2': [(0, 79, 1.5), (1.5, 78, .5), (2, 76, 2), (4, 76, 1), (5, 73, 1), (6, 69, 2), (8, 74, 1),
                   (9, 76, 1), (10, 78, 2), (12, 76, 1.5), (13.5, 74, 2.5)],
            'intro': [(10, 74, 1), (11, 76, 1), (12, 78, 2), (14, 69, 2)],
        },
        form=[('A', 0, 'intro'), ('A', 1, 'A1'), ('A', 1, 'A2'), ('A', 1, None), ('A', 1, 'A2'), ('B', 2, 'B1'),
              ('B', 2, 'B2'), ('A', 1, 'A1'), ('A', 1, 'A2'), ('A', 1, None), ('A', 1, 'A1'), ('B', 2, 'B1'),
              ('B', 2, 'B2'), ('end', 0, None)],
        final=(74, 81)),
    'paper_lantern': dict(
        title='Paper Lantern', bpm=70, lead='koto', lead_b='koto', drums=2, bells=False,
        prog={'A': ['Am9', 'Fmaj7', 'G6', 'Em7'], 'B': ['Dm9', 'G13', 'Cmaj7', 'E7'], 'end': ['Am9', 'Am9']},
        mel={
            'A1': [(0, 76, 1), (1, 74, .5), (1.5, 72, 1.5), (3, 69, 1), (4, 72, 1), (5, 74, .5), (5.5, 76, 1.5),
                   (8, 79, 1), (9, 76, 1), (10, 74, 2), (12, 72, 1), (13, 74, .5), (13.5, 71, 2.5)],
            'A2': [(0, 81, 1.5), (1.5, 79, .5), (2, 76, 2), (4, 74, 1), (5, 76, 1), (6, 72, 2), (8, 74, 1),
                   (9, 72, .5), (9.5, 69, 1.5), (12, 67, 1), (13, 69, 3)],
            'B1': [(0, 77, 1), (1, 76, 1), (2, 74, 2), (4, 79, 1.5), (5.5, 77, .5), (6, 76, 2), (8, 76, 1),
                   (9, 79, 1), (10, 84, 2), (12, 83, 1), (13, 80, 3)],
            'B2': [(0, 81, 2), (2, 79, 1), (3, 77, 1), (4, 76, 2), (6, 74, 2), (8, 72, 1), (9, 74, 1), (10, 76, 2),
                   (12, 71, 1.5), (13.5, 69, 2.5)],
            'intro': [(8, 69, 1), (9, 72, 1), (10, 74, 1), (11, 76, 1), (12, 79, 4)],
        },
        form=[('A', 0, 'intro'), ('A', 2, 'A1'), ('A', 2, 'A2'), ('B', 2, 'B1'), ('B', 2, 'B2'), ('A', 2, None),
              ('A', 2, 'A1'), ('A', 2, 'A2'), ('B', 2, 'B1'), ('B', 2, 'B2'), ('end', 0, None)],
        final=(69, 76)),
    'snow_noren': dict(
        title='Snow on the Noren', bpm=64, lead='bell', lead_b='flute', drums=0, bells=True,
        prog={'A': ['Gmaj7', 'Bm7', 'Cmaj9', 'D6'], 'B': ['Em9', 'Am7', 'Cmaj9', 'D7sus'], 'end': ['Gmaj7', 'Gmaj7']},
        mel={
            'A1': [(0, 79, 1), (1, 78, 1), (2, 74, 2), (4, 78, 1), (5, 76, 1), (6, 74, 2), (8, 76, 1), (9, 79, 1),
                   (10, 83, 2), (12, 81, 1), (13, 78, 1), (14, 81, 2)],
            'A2': [(0, 83, 1.5), (1.5, 81, .5), (2, 79, 2), (4, 78, 1), (5, 79, 1), (6, 74, 2), (8, 72, 1),
                   (9, 76, 1), (10, 79, 2), (12, 78, 2), (14, 74, 2)],
            'B1': [(0, 76, 2), (2, 79, 1), (3, 78, 1), (4, 76, 2), (6, 72, 2), (8, 76, 1), (9, 79, 1), (10, 84, 2),
                   (12, 81, 2), (14, 79, 2)],
            'B2': [(0, 83, 2), (2, 79, 2), (4, 81, 1), (5, 79, 1), (6, 76, 2), (8, 76, 1), (9, 79, 1), (10, 79, 2),
                   (12, 78, 2), (14, 74, 2)],
            'intro': [(8, 74, 1), (9, 78, 1), (10, 79, 1), (11, 83, 1), (12, 86, 4)],
        },
        form=[('A', 0, 'intro'), ('A', 0, 'A1'), ('A', 3, 'A2'), ('B', 3, 'B1'), ('B', 3, 'B2'), ('A', 3, None),
              ('A', 3, 'A1'), ('B', 3, 'B1'), ('B', 3, 'B2'), ('A', 0, 'A2'), ('end', 0, None)],
        final=(79, 86)),
    'night_market': dict(
        title='Night Market', bpm=86, lead='shamisen', lead_b='flute', drums=3, bells=False,
        prog={'A': ['Fmaj9', 'Gm7', 'Am7b', 'C7'], 'B': ['Bbmaj7', 'Csus', 'Am7b', 'Dm7'], 'end': ['Fmaj9', 'Fmaj9']},
        mel={
            'A1': [(0, 72, .5), (0.5, 74, .5), (1, 77, 1), (2.5, 74, .5), (3, 72, 1), (4, 74, .5), (4.5, 77, .5),
                   (5, 79, 1), (6.5, 77, .5), (7, 74, 1), (8, 76, .5), (8.5, 77, .5), (9, 81, 1), (10.5, 79, .5),
                   (11, 77, 1), (12, 79, .5), (12.5, 76, .5), (13, 72, 1.5), (15, 70, .5), (15.5, 72, .5)],
            'A2': [(0, 77, 1), (1.5, 74, .5), (2, 72, 1), (3, 69, 1), (4, 70, .5), (4.5, 72, .5), (5, 74, 1),
                   (6.5, 70, .5), (7, 67, 1), (8, 69, .5), (8.5, 72, .5), (9, 76, 1), (10.5, 74, .5), (11, 72, 1),
                   (12, 70, .5), (12.5, 67, .5), (13, 65, 2)],
            'B1': [(0, 74, 1), (1, 77, 1), (2, 81, 2), (4, 79, 1), (5, 77, 1), (6, 76, 2), (8, 76, .5), (8.5, 77, .5),
                   (9, 79, 1), (10, 81, 1), (11, 84, 1), (12, 81, 1), (13, 77, 3)],
            'B2': [(0, 82, 1), (1, 81, 1), (2, 77, 2), (4, 79, 1), (5, 77, .5), (5.5, 76, .5), (6, 72, 2),
                   (8, 76, 1), (9, 77, 1), (10, 79, 1), (11, 76, 1), (12, 74, 4)],
            'intro': [(12, 72, .5), (12.5, 74, .5), (13, 77, .5), (13.5, 79, .5), (14, 81, 2)],
        },
        form=[('A', 0, 'intro'), ('A', 3, 'A1'), ('A', 3, 'A2'), ('B', 3, 'B1'), ('B', 3, 'B2'), ('A', 3, 'A1'),
              ('A', 3, None), ('B', 3, 'B1'), ('B', 3, 'B2'), ('A', 3, 'A2'), ('end', 0, None)],
        final=(77, 84)),
}


def track_length(name):
    tr = TRACKS[name]
    bar = 4 * 60.0 / tr['bpm']
    return (len(tr['form']) - 1) * 4 * bar + 2 * bar + 3.0


def render_track(name, seed=1):
    """One full pass of a track, mono, with its natural ending."""
    tr = TRACKS[name]
    r = rng(seed)
    beat = 60.0 / tr['bpm']
    bar = 4 * beat
    dur = track_length(name)
    n = int((dur + 3) * SR)
    keys, bassb, mel, drums, bells = (np.zeros(n) for _ in range(5))
    hum = lambda: r.normal(0, 0.006)
    for si, (prog, dr, phrase) in enumerate(tr['form']):
        b0 = si * 4
        bars = tr['prog'][prog]
        nb = 4 if prog != 'end' else 2
        for k in range(nb):
            t0 = (b0 + k) * bar
            notes, root = CH[bars[k % len(bars)]]
            hold = bar * (2 if prog == 'end' else 1)
            for i, m in enumerate(notes):
                add(keys, ep(m, hold - 0.05, 0.9 - 0.08 * i), t0 + 0.012 * i + hum())
            if prog != 'end' and k % 2 == 1 and dr != 0:
                for i, m in enumerate(notes[1:]):
                    add(keys, ep(m, beat * 1.2, 0.35), t0 + 2.5 * beat + 0.01 * i + hum())
            if dr or prog == 'end' or tr['drums'] == 0:
                add(bassb, bass(root, beat * (2.3 if dr != 3 else 1.2)), t0 + hum())
                if prog != 'end' and dr:
                    if dr == 3:
                        for bt, off in ((1.5, 7), (2.5, 12), (3.5, 7)):
                            add(bassb, bass(root + off, beat * 0.45, 0.6), t0 + bt * beat + hum())
                    else:
                        add(bassb, bass(root + (7 if k % 2 == 0 else 12), beat * 0.9, 0.7), t0 + 2.5 * beat + hum())
                        add(bassb, bass(root, beat * 0.9, 0.8), t0 + 3.5 * beat + hum())
            if dr == 1:
                for bt in (0, 1.5, 2.75 if k % 2 else 2.5):
                    add(drums, kick(1.0, r), t0 + bt * beat + hum())
                for bt in (1, 3):
                    add(drums, snare(0.55, r), t0 + bt * beat + 0.012 + hum())
                for e in range(8):
                    sw = 0.0 if e % 2 == 0 else 0.11 * beat
                    add(drums, hat(r.uniform(0.35, 0.7), r), t0 + e * 0.5 * beat + sw + hum())
            elif dr == 2:
                for bt in (0, 2.5):
                    add(drums, kick(0.7, r), t0 + bt * beat + hum())
                for bt in (1, 3):
                    add(drums, snare(0.45, r, brush=True), t0 + bt * beat + 0.015 + hum())
                for e in range(8):
                    sw = 0.0 if e % 2 == 0 else 0.12 * beat
                    add(drums, hat(r.uniform(0.2, 0.4), r), t0 + e * 0.5 * beat + sw + hum())
            elif dr == 3:
                for bt in (0, 1.75, 2.5):
                    add(drums, kick(0.85, r), t0 + bt * beat + hum())
                for bt in (1, 3):
                    add(drums, rim(0.5), t0 + bt * beat + hum())
                for e in range(8):
                    sw = 0.0 if e % 2 == 0 else 0.1 * beat
                    add(drums, hat(r.uniform(0.3, 0.6), r), t0 + e * 0.5 * beat + sw + hum())
            if tr['bells'] and prog != 'end' and dr:
                for e, m in enumerate(notes[1:] + notes[1:2]):
                    add(bells, bell(m + 12, 0.25), t0 + e * beat + hum())
        if phrase:
            inst = tr['lead_b'] if prog == 'B' else tr['lead']
            for (bt, m, d) in tr['mel'][phrase]:
                t = b0 * bar + bt * beat + hum()
                v = r.uniform(0.8, 1.0)
                if inst == 'koto':
                    add(mel, koto(m, v, r=r), t)
                    if r.random() < 0.2:
                        add(mel, koto(m - 12, 0.4, r=r), t + 0.03)
                elif inst == 'shamisen':
                    add(mel, shamisen(m, v * 0.9, r=r), t)
                elif inst == 'bell':
                    add(mel, bell(m, v), t)
                else:
                    add(mel, flute(m, d * beat * 0.95, v, r=r), t)
        if prog == 'end':
            a, b = tr['final']
            add(mel, koto(a, 0.9, 4.0, r=r), b0 * bar + 0.02)
            add(mel, koto(b, 0.5, 4.0, r=r), b0 * bar + 0.25)
    bus = 0.20 * lp(keys, 3800) + 0.30 * bassb + 0.23 * mel + 0.30 * drums + 0.12 * bells
    bus = reverb(bus, 0.22)
    t = np.arange(n) / SR
    warp = np.arange(n) + 0.0009 * SR * np.sin(2 * np.pi * 0.33 * t) + 0.0003 * SR * np.sin(2 * np.pi * 1.7 * t)
    bus = np.interp(warp, np.arange(n), bus)
    bus = np.tanh(bus * 1.6) / 1.6
    bus = lp(hp(bus, 35), 7500)
    crack = np.zeros(n)
    pos = r.integers(0, n, int(dur * 9))
    crack[pos] = r.uniform(-1, 1, len(pos)) ** 3
    bus += 0.05 * bp(crack, 1500, 9000) + 0.0025 * lp(r.standard_normal(n), 5000)
    bus = bus[:int(dur * SR)]
    f = int(1.5 * SR)
    bus[-f:] *= np.linspace(1, 0, f)
    return bus


def playlist(names, duration, seed=1, start=0.0):
    """Tracks back to back (crossfaded) until `duration` is filled, starting `start` s into the first."""
    out = np.zeros(int(duration * SR) + SR)
    t = -start
    i = 0
    cache = {}
    while t < duration:
        nm = names[i % len(names)]
        if nm not in cache:
            cache[nm] = render_track(nm, seed + i)
        x = cache[nm]
        if t < 0:
            cut = int(-t * SR)
            seg = x[cut:].copy()
            f = int(0.6 * SR)
            seg[:f] *= np.linspace(0, 1, f)
            add(out, seg, 0.0)
        else:
            add(out, x, t)
        t += len(x) / SR - 1.0
        i += 1
    return out[:int(duration * SR)]


# ============================================================================ effects
def _nz(n, seed=None):
    return (rng(seed) if seed is not None else _rng).standard_normal(n)


def sfx_click(f0, f1, dec, n=0.12):
    N = int(n * SR)
    t = np.arange(N) / SR
    return bp(_nz(N), f0, f1) * np.exp(-t / dec)


def sfx_roll(d=0.55):
    N = int(d * SR)
    t = np.arange(N) / SR
    rum = 0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 23 * t + _rng.uniform(0, 3)))
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 0.7
    return bp(_nz(N), 180, 900) * rum * e * 0.6


def sfx_chime():
    N = int(2.6 * SR)
    out = np.zeros(N)
    for k, (dt, amp) in enumerate(((0, 1.0), (0.17, 0.55), (0.46, 0.35), (0.9, 0.18))):
        base = 1880 * (1 + 0.012 * k)
        n2 = N - int(dt * SR)
        t = np.arange(n2) / SR
        s = sum(a * np.sin(2 * np.pi * base * r_ * t) * np.exp(-t / dd)
                for r_, a, dd in ((1, 1, 1.5), (2.76, 0.45, 0.7), (5.4, 0.2, 0.35), (8.93, 0.1, 0.2)))
        out[int(dt * SR):] += s * amp * np.clip(t / 0.002, 0, 1)
    return out * 0.18


def sfx_slurp(vol):
    d = 0.65
    N = int(d * SR)
    t = np.arange(N) / SR
    nz = _nz(N)
    y = np.zeros(N)
    for i, (a, b) in enumerate(((600, 1100), (900, 1700), (1300, 2600))):
        y += bp(nz, a, b) * np.clip(1 - abs(t / d - (0.25 + 0.3 * i)) * 3.2, 0, 1)
    am = 0.55 + 0.45 * np.sin(2 * np.pi * 21 * t) ** 2
    return y * am * np.sin(np.pi * t / d) * vol * 0.9


def sfx_bowl(soft=False):
    N = int(0.5 * SR)
    t = np.arange(N) / SR
    thud = np.sin(2 * np.pi * 150 * t) * np.exp(-t / 0.05)
    ring = (np.sin(2 * np.pi * 1320 * t) + 0.6 * np.sin(2 * np.pi * 3150 * t)) * np.exp(-t / 0.16) * 0.25
    return (thud * 0.8 + ring * (0.4 if soft else 1) + sfx_click(1500, 5000, 0.006, 0.5) * 0.4) * 0.5


def sfx_ladle():
    N = int(0.35 * SR)
    t = np.arange(N) / SR
    f = _rng.uniform(0.95, 1.05)
    return sum(a * np.sin(2 * np.pi * fr * f * t) * np.exp(-t / dd)
               for fr, a, dd in ((2900, 1, 0.12), (4650, 0.6, 0.08), (7100, 0.3, 0.05))) * 0.07


def sfx_shimmer():
    N = int(3.5 * SR)
    out = np.zeros(N)
    for i, m in enumerate((81, 83, 86, 88, 90, 93, 95)):
        s = koto(m, 0.35 - 0.03 * i, 2.5)
        o = int(i * 0.07 * SR)
        out[o:o + len(s)] += s[:N - o]
    t = np.arange(N) / SR
    swell = bp(_nz(N), 2500, 9000) * np.clip(t / 0.6, 0, 1) * np.exp(-t / 0.8) * 0.15
    return reverb(out + swell, 0.8) * 0.8


def sfx_card():
    N = int(1.6 * SR)
    out = np.zeros(N)
    t = np.arange(N) / SR
    out += bp(_nz(N), 2000, 7000) * np.exp(-t / 0.06) * 0.08
    for dt, m in ((0.03, 81), (0.15, 86)):
        s = koto(m, 0.28, 1.4)
        i = int(dt * SR)
        out[i:i + len(s)] += s[:N - i]
    return out


def sfx_step(kind):
    if kind == 'step_geta':
        f = _rng.choice([1150, 1450])
        N = int(0.12 * SR)
        t = np.arange(N) / SR
        return (sfx_click(f * 0.8, f * 1.3, 0.025) * 0.6 + np.sin(2 * np.pi * f * t) * np.exp(-t / 0.02) * 0.25) * 0.55
    N = int(0.1 * SR)
    return lp(_nz(N), 380) * np.exp(-np.arange(N) / SR / 0.035) * 0.35


def sfx_whoosh():
    N = int(1.2 * SR)
    t = np.arange(N) / SR
    nz = _nz(N)
    out = np.zeros(N)
    for i in range(6):
        lo = 300 * 2 ** (i * 0.6)
        seg = bp(nz, lo, lo * 1.8) * np.exp(-((t - 0.15 - i * 0.08) / 0.12) ** 2)
        out += seg
    return out * 0.35 + sfx_shimmer()[:N] * 0.3


def sfx_brush():
    N = int(1.1 * SR)
    t = np.arange(N) / SR
    am = np.clip(np.sin(2 * np.pi * 2.2 * t), 0, 1) ** 2
    return bp(_nz(N), 1800, 6000) * am * 0.12


def sfx_board():
    out = np.zeros(int(2.0 * SR))
    add(out, sfx_click(400, 1600, 0.02, 0.2), 0.0, 0.6)
    add(out, koto(86, 0.35, 1.8), 0.05)
    add(out, koto(93, 0.25, 1.8), 0.18)
    return out


def sfx_poof():
    N = int(0.6 * SR)
    t = np.arange(N) / SR
    nz = lp(_nz(N), 2500) * np.exp(-t / 0.12)
    f = 600 * np.exp(-t / 0.15) + 120
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.2)
    return (nz * 0.5 + tone * 0.3) * 0.7


def sfx_splash():
    N = int(0.8 * SR)
    t = np.arange(N) / SR
    out = bp(_nz(N), 800, 5000) * np.exp(-t / 0.15) * 0.5
    for i in range(6):
        add(out, sfx_drop(_rng.uniform(600, 1400)), 0.05 + i * 0.07, 0.4)
    return out


def sfx_drop(f=900):
    N = int(0.08 * SR)
    t = np.arange(N) / SR
    return np.sin(2 * np.pi * np.cumsum(f * (1 + 4 * t)) / SR) * np.exp(-t / 0.02)


def sfx_pour():
    out = np.zeros(int(1.0 * SR))
    for i in range(14):
        add(out, sfx_drop(_rng.uniform(300, 700)), i * 0.06, 0.3)
    return out + bp(_nz(len(out)), 400, 2400) * 0.05


def sfx_thunder():
    N = int(4.0 * SR)
    t = np.arange(N) / SR
    crack = bp(_nz(N), 300, 4000) * np.exp(-t / 0.08) * 0.7
    rumble = lp(_nz(N), 160, 4) * (np.exp(-t / 1.4) * np.clip(t / 0.15, 0, 1)) * 4.0
    return crack + rumble


def sfx_boing():
    N = int(0.5 * SR)
    t = np.arange(N) / SR
    f = 260 + 380 * np.sin(np.pi * np.clip(t / 0.25, 0, 1))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.18) * 0.35


def sfx_hop():
    return sfx_click(200, 900, 0.03, 0.15) * 0.6


def sfx_paddle():
    N = int(0.4 * SR)
    t = np.arange(N) / SR
    return bp(_nz(N), 500, 2500) * np.sin(np.pi * t / 0.4) ** 2 * 0.12


def sfx_sparkle():
    out = np.zeros(int(1.6 * SR))
    for i, m in enumerate((88, 91, 95, 98)):
        add(out, bell(m, 0.25, 1.2), i * 0.06)
    return out


def sfx_pop():
    N = int(0.12 * SR)
    t = np.arange(N) / SR
    return np.sin(2 * np.pi * np.cumsum(500 + 900 * t) / SR) * np.exp(-t / 0.03) * 0.4


def sfx_zap():
    N = int(0.5 * SR)
    t = np.arange(N) / SR
    nz = hp(_nz(N), 3000) * (np.abs(np.sin(2 * np.pi * 37 * t)) > 0.6) * np.exp(-t / 0.2)
    return nz * 0.35


def sfx_drums():
    out = np.zeros(int(2.4 * SR))
    for i in range(8):
        add(out, kick(0.8 + 0.2 * (i % 2)), i * 0.22)
    return out * 0.8


def sfx_crunch():
    out = np.zeros(int(0.5 * SR))
    for i in range(4):
        add(out, sfx_click(1500, 6000, 0.01, 0.06), i * 0.09, 0.5)
    return out


def sfx_cracker():
    N = int(0.4 * SR)
    t = np.arange(N) / SR
    out = bp(_nz(N), 1000, 8000) * np.exp(-t / 0.04) * 0.8
    add(out, sfx_sparkle()[:N], 0.0, 0.5)
    return out


def sfx_wind():
    N = int(3.0 * SR)
    t = np.arange(N) / SR
    return bp(_nz(N), 200, 1200) * np.sin(np.pi * t / 3.0) ** 2 * 0.6


def sfx_kettle():
    N = int(1.4 * SR)
    t = np.arange(N) / SR
    whistle = np.sin(2 * np.pi * 2100 * t + 3 * np.sin(2 * np.pi * 6 * t)) * np.clip(t / 0.3, 0, 1) * np.exp(-t / 0.8)
    return whistle * 0.12 + bp(_nz(N), 3000, 7000) * np.exp(-t / 0.6) * 0.05


def sfx_paw():
    return sfx_click(2500, 7000, 0.006, 0.05) * 0.25


def sfx_bark():
    N = int(0.25 * SR)
    t = np.arange(N) / SR
    f = 520 * (1 - 0.3 * t / 0.25)
    s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t / 0.08)
    return lp(s, 2200) * 0.25


def blip(voice, seed):
    """One soft keystroke of the text blips: pitch depends on who is talking."""
    N = int(0.035 * SR)
    t = np.arange(N) / SR
    f = 520 * voice * (1 + 0.04 * ((seed * 7919) % 5 - 2))
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
    return s * np.exp(-t / 0.012) * 0.10


SFX_FN = dict(
    door_open=lambda: sfx_roll(), door_close=lambda: sfx_roll(), chime=sfx_chime, shimmer=sfx_shimmer,
    ladle=sfx_ladle, bowl=lambda: sfx_bowl(), bowl_soft=lambda: sfx_bowl(True), card=sfx_card, whoosh=sfx_whoosh,
    brush=sfx_brush, board=sfx_board, poof=sfx_poof, splash=sfx_splash, pour=sfx_pour, thunder=sfx_thunder,
    boing=sfx_boing, hop=sfx_hop, paddle=sfx_paddle, sparkle=sfx_sparkle, pop=sfx_pop, zap=sfx_zap,
    drums=sfx_drums, crunch=sfx_crunch, cracker=sfx_cracker, wind=sfx_wind, kettle=sfx_kettle, paw=sfx_paw,
    bark=sfx_bark,
)
SFX_GAIN = dict(door_open=0.5, door_close=0.5, chime=0.75, shimmer=0.55, bowl=0.4, bowl_soft=0.35, whoosh=0.45,
                board=0.7, thunder=0.9, slurp=1.0)


def effects(tl, t0, t1):
    """All effects (and text blips) of a timeline between source times t0 and t1."""
    n = int((t1 - t0) * SR) + SR
    out = np.zeros(n)
    for (name, t, kw) in tl.sfx:
        if not (t0 - 4 <= t < t1):
            continue
        tt = t - t0
        if name == 'rattle':
            for k in range(7):
                add(out, sfx_click(800, 2800, 0.012), tt + k * 0.06 + _rng.uniform(0, 0.02), _rng.uniform(0.15, 0.35))
        elif name in ('step', 'step_geta'):
            add(out, sfx_step(name), tt)
        elif name == 'slurp':
            add(out, sfx_slurp(0.55), tt)
        elif name == 'slurp_soft':
            add(out, sfx_slurp(0.25), tt)
        elif name in SFX_FN:
            add(out, SFX_FN[name](), tt, SFX_GAIN.get(name, 1.0))
    for ln in tl.lines:
        if ln['t1'] < t0 or ln['t0'] > t1:
            continue
        v = tl.cast.get(ln['who'], {}).get('voice', 1.0)
        for i, ch in enumerate(ln['text']):
            if i % 2 or ch in ' .,!?…-—\'"':
                continue
            tt = ln['t0'] + i / ln['cps'] - t0
            if 0 <= tt < t1 - t0:
                add(out, blip(v, i), tt)
    return out[:int((t1 - t0) * SR)]


def ambience(tl, t0, t1, seed=3):
    """Rain (or snow wind, or storm) and the pot, louder while the door is open."""
    r = rng(seed + int(t0))
    n = int((t1 - t0) * SR)
    t = t0 + np.arange(n) / SR
    rain = lp(hp(r.standard_normal(n), 400), 5200) * 0.05
    drops = np.zeros(n)
    pos = r.integers(0, max(1, n), int((t1 - t0) * 35))
    drops[pos] = r.uniform(0.2, 1, len(pos))
    rain += bp(drops, 1800, 6000) * 0.12
    wind = bp(r.standard_normal(n), 150, 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t)) * 0.05
    # weather mix over time
    wr = np.zeros(n)
    ww = np.zeros(n)
    for i, (tw, w) in enumerate(tl.weather):
        te = tl.weather[i + 1][0] if i + 1 < len(tl.weather) else 1e9
        a, b = int((max(tw, t0) - t0) * SR), int((min(te, t1) - t0) * SR)
        if b <= 0 or a >= n:
            continue
        a, b = max(0, a), min(n, b)
        if w in ('rain',):
            wr[a:b] = 1.0
        elif w == 'storm':
            wr[a:b] = 1.8
            ww[a:b] = 0.6
        elif w == 'snow':
            wr[a:b] = 0.0
            ww[a:b] = 1.0
    k = np.zeros(n)
    for dv in tl.doors:
        a, b = int((dv['t0'] - t0) * SR), int((dv['t1'] + 0.55 - t0) * SR)
        if b > 0 and a < n:
            k[max(0, a):min(n, b)] = 1.0
    k = lfilter([0.0004], [1, -0.9996], k)
    rain = 2.2 * rain * wr * (0.45 + 1.4 * k) + wind * ww * (0.6 + 1.6 * k) * 1.4
    bub = np.zeros(n)
    tt = 0.0
    while tt < (t1 - t0) - 0.1:
        tt += r.uniform(0.15, 0.7)
        N = int(0.05 * SR)
        u = np.arange(N) / SR
        f = r.uniform(170, 260)
        s = np.sin(2 * np.pi * np.cumsum(f * (1 + 6 * u)) / SR) * np.sin(np.pi * u / 0.05)
        add(bub, s * r.uniform(0.01, 0.03), tt)
    return rain + lp(bub, 1200)


def write_wav(path, stereo):
    st = np.clip(stereo, -1, 1)
    pcm = (st * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def mix_plan(tl, plan, music_names, music_start=0.0, music_at=0.0, seed=1, music_gain=0.9):
    """plan: list of (src_t0, src_t1) pieces in output order.  Music plays from output time
    `music_at` to the end, `music_start` seconds into the playlist."""
    total = sum(b - a for a, b in plan)
    n = int(total * SR)
    fxa = np.zeros(n)
    amb = np.zeros(n)
    o = 0.0
    for (a, b) in plan:
        e = effects(tl, a, b)
        am = ambience(tl, a, b, seed)
        f = int(0.03 * SR)
        for arr in (e, am):
            if len(arr) > 2 * f:
                arr[:f] *= np.linspace(0, 1, f)
                arr[-f:] *= np.linspace(1, 0, f)
        add(fxa, e, o)
        add(amb, am, o)
        o += b - a
    mus = np.zeros(n)
    if music_names:
        m = playlist(music_names, max(1.0, total - music_at), seed=seed, start=music_start)
        add(mus, m, music_at)
        f = int(3.0 * SR)
        mus[-f:] *= np.linspace(1, 0, f)
    d = int(0.011 * SR)
    ambR = np.concatenate([np.zeros(d), amb[:-d]])
    L = music_gain * mus + amb + fxa
    R = music_gain * mus + ambR + fxa
    st = np.stack([L, R], 1)
    st /= max(1e-9, np.abs(st).max()) / 0.8
    return st
