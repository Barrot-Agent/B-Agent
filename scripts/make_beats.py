#!/usr/bin/env python3
"""make_beats.py — Barrot producer-mode beat engine.

Builds 5 starter beats (MIDI + WAV + step-pattern text) from the production
DNA cheat sheets in producers/. Technique study, not song copying: every
pattern below is an original grid derived from each producer's *methods*.

Usage:
    python3 scripts/make_beats.py            # build all 5 tracks into tracks/
    python3 scripts/make_beats.py --check    # reload + verify every track
"""
from __future__ import annotations

import argparse
import math
import struct
import sys
import wave
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "tracks"
SR = 44100

# ----------------------------------------------------------------- music data
MINOR = [0, 2, 3, 5, 7, 8, 10]          # natural minor
MAJOR = [0, 2, 4, 5, 7, 9, 11]
PENT_MIN = [0, 3, 5, 7, 10, 12, 15]     # minor pentatonic degrees (root..oct+)
PENT_MAJ = [0, 2, 4, 7, 9, 12, 14]

CHORDS = {
    "m7":  [0, 3, 7, 10],
    "maj7": [0, 4, 7, 11],
    "m9":  [0, 3, 7, 10, 14],
    "maj9": [0, 4, 7, 11, 14],
    "maj": [0, 4, 7],
    "min": [0, 3, 7],
    "6":   [0, 4, 7, 9],
    "7":   [0, 4, 7, 10],
}

# GM drum map
K, SN, CL = 36, 38, 39          # kick, snare, clap
CH, OH, PH = 42, 46, 44         # closed/open/pedal hat
SH, TB, CB = 70, 54, 56         # maracas(shaker), tambourine, cowbell
CG1, CG2 = 64, 62               # low conga (log-drum-ish), mute hi conga
WB_H, WB_L = 76, 77             # hi/lo wood block
TR_M, TR_O = 80, 81             # mute/open triangle (Timbo "pops")
KL, RD = 75, 51                 # claves, ride

# note name -> midi
NOTES = {"C": 0, "C#": 1, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5,
         "F#": 6, "Gb": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}


def midi_of(name: str, octave: int) -> int:
    return 12 * (octave + 1) + NOTES[name]


def deg(root_midi: int, scale, idx: int) -> int:
    """Scale degree index (can exceed octave, wraps)."""
    n = len(scale)
    octs, i = divmod(idx, n)
    return root_midi + scale[i] + 12 * octs


# ------------------------------------------------------------------ patterns
# 16-step grids. Values are velocity (1-127) or None.
def v(steps, vel=100, accents=None):
    out = {}
    for s in steps:
        out[s] = vel
    if accents:
        for s, a in accents.items():
            out[s] = a
    return out


DARKCHILD = dict(
    slug="track_01_darkchild_rnb", title="Darkchild R&B", bpm=95,
    key=("F", "minor"), swing=0.08,
    prog=[("F", "m7"), ("Db", "maj7"), ("Eb", "maj7"), ("C", "m7")],
    sections=[("intro", 4), ("verse", 8), ("hook", 8), ("outro", 4)],
    drums={
        "verse": {K: v([0, 6, 10], 118, {0: 127}), SN: v([4, 12], 112),
                  CL: v([4, 12], 78), CH: v([0, 2, 4, 6, 8, 10, 12, 14], 62,
                                            {2: 84, 6: 84, 10: 84, 14: 96}),
                  OH: v([14], 70), PH: v([15], 52)},
        "hook": {K: v([0, 6, 8, 10], 120, {0: 127}), SN: v([4, 12], 118),
                 CL: v([4, 12], 92), CH: v(range(16), 64, {2: 90, 6: 90, 10: 90, 14: 100}),
                 OH: v([7, 15], 78), RD: v([8], 60)},
        "intro": {CH: v([0, 4, 8, 12], 52), CL: v([12], 70)},
        "outro": {K: v([0, 10], 100), SN: v([12], 90), CH: v([0, 4, 8, 12], 56)},
    },
    bass={   # gliding: root holds, 5th pickup slides into next root
        "verse": [(0, 0, 5), (6, 0, 2), (10, 4, 3), (14, -3, 2)],
        "hook":  [(0, 0, 3), (3, 7, 1), (6, 0, 2), (8, 0, 2), (10, 4, 3), (14, 7, 2)],
    },
    pads="pad",      # warm pad bed, swells
    strings=True,    # dramatic string swells on hook
    chops={          # staccato vocal-chop surrogate (square lead, chord tones)
        "verse": [(0, 0, 1), (4, 0, 1), (7, 2, 1), (10, 1, 1), (14, 0, 1)],
        "hook":  [(0, 0, 1), (2, 0, 1), (4, 2, 1), (7, 3, 1), (10, 2, 1), (12, 0, 1), (14, 1, 1)],
    },
    melody=None,
)

TIMBALAND = dict(
    slug="track_02_timbaland_futuristic", title="Timbaland Futuristic", bpm=90,
    key=("C", "minor"), swing=0.20,
    prog=[("C", "m7"), ("C", "m7"), ("Ab", "maj7"), ("Bb", "maj7")],
    sections=[("intro", 4), ("verse", 8), ("hook", 8), ("outro", 4)],
    drums={
        "verse": {K: v([0, 3, 6, 10, 14], 116, {0: 127}), SN: v([8], 118),
                  CL: v([5, 13], 82), CH: v(range(16), 58, {3: 88, 7: 88, 11: 88, 15: 92}),
                  WB_H: v([2], 96), TR_M: v([9], 92), CG2: v([12], 78)},
        "hook": {K: v([0, 3, 6, 10, 13, 14], 120, {0: 127}), SN: v([8], 122),
                 CL: v([2, 5, 13], 88), CH: v(range(16), 62, {3: 92, 7: 92, 11: 92, 15: 96}),
                 WB_H: v([2, 11], 100), WB_L: v([6], 88), TR_M: v([9], 96),
                 TR_O: v([15], 82), CG1: v([4], 80)},
        "intro": {CH: v([0, 3, 8, 11], 50), TR_M: v([9], 70), WB_H: v([2], 80)},
        "outro": {K: v([0, 10], 96), SN: v([8], 100), TR_M: v([9], 80), CH: v([0, 6], 50)},
    },
    bass={   # gallop: dotted-8th engine, root-octave hops
        "verse": [(0, 0, 2), (3, 0, 1), (6, 7, 1), (8, 0, 2), (11, 0, 1), (14, -5, 2)],
        "hook":  [(0, 0, 1), (3, 0, 1), (6, 12, 1), (8, 0, 1), (11, 7, 1), (13, 5, 1), (14, 7, 2)],
    },
    pads=None,
    strings=False,
    lead={   # detuned keyboard gallop = the hook itself
        "hook": [(0, 0, 1), (3, 0, 1), (6, 2, 1), (8, 0, 1), (11, 3, 1), (14, 2, 1)],
    },
    blip={   # weird "baby-cry"/glitch surrogate (high sine zap)
        "verse": [(7, 4, 1), (15, 5, 1)],
        "hook": [(4, 5, 1), (9, 6, 1), (15, 5, 1)],
    },
)

MISSY = dict(
    slug="track_03_missy_minimal", title="Missy Minimal", bpm=100,
    key=("D", "minor"), swing=0.10,
    prog=[("D", "m7"), ("D", "m7"), ("Bb", "maj7"), ("C", "7")],
    sections=[("intro", 4), ("verse", 8), ("hook", 8), ("outro", 4)],
    drums={
        "verse": {K: v([0, 10], 118, {0: 127}), SN: v([4, 12], 100),
                  CH: v([2, 6, 14], 60), TR_M: v([11], 66)},
        "hook": {K: v([0, 8, 10], 122, {0: 127}), SN: v([4, 12], 108),
                 CL: v([12], 74), CH: v([2, 5, 6, 9, 14], 66, {6: 88}),
                 TR_O: v([14], 74), WB_L: v([7], 84)},
        "intro": {CH: v([2], 46), TR_M: v([11], 60)},
        "outro": {K: v([0], 100), TR_M: v([11], 70), CH: v([6], 50)},
    },
    bass={   # static sub drones (whole-bar roots)
        "verse": [(0, 0, 14)],
        "hook":  [(0, 0, 6), (8, 0, 7)],
    },
    pads=None,
    strings=False,
    pluck={  # kalimba "reverse tabla" surrogate — weird and sparse
        "verse": [(0, 0, 2), (10, 2, 2)],
        "hook":  [(0, 3, 2), (4, 2, 1), (8, 1, 2), (13, 2, 2)],
    },
    blip={   # futuristic zap in the hole
        "verse": [(13, 6, 1)],
        "hook": [(6, 5, 1), (13, 7, 1)],
    },
)

BLACK_COFFEE = dict(
    slug="track_04_blackcoffee_afrohouse", title="Black Coffee Afro House", bpm=122,
    key=("A", "minor"), swing=0.0,
    prog=[("A", "m9"), ("A", "m9"), ("F", "maj9"), ("G", "6")],
    sections=[("intro", 8), ("groove", 8), ("main", 8), ("outro", 4)],
    drums={
        "groove": {K: v([0, 4, 8, 12], 112, {0: 124}), OH: v([2, 6, 10, 14], 74),
                   SH: v(range(16), 48, {0: 66, 4: 66, 8: 66, 12: 66}),
                   CG1: v([3, 6, 9, 13], 82, {9: 96}), CL: v([8], 88)},
        "main": {K: v([0, 4, 8, 12], 118, {0: 127}), OH: v([2, 6, 10, 14], 78),
                 SH: v(range(16), 56, {2: 72, 6: 72, 10: 72, 14: 72}),
                 CG1: v([3, 6, 9, 12, 13], 88, {9: 104}), CG2: v([5, 11], 76),
                 CL: v([8], 94), CB: v([14], 70)},
        "intro": {SH: v(range(16), 44, {2: 62, 10: 62}), CG1: v([3, 9], 66)},
        "outro": {SH: v(range(16), 44), K: v([0, 8], 90), CG1: v([3, 9], 70)},
    },
    bass={   # warm off-beat roller between the kicks
        "groove": [(2, 0, 2), (6, 0, 2), (10, 0, 2), (14, 7, 2)],
        "main": [(2, 0, 1), (4, 7, 1), (6, 0, 2), (10, 0, 1), (12, 5, 1), (14, 7, 2)],
    },
    pads="soul",     # jazzy maj9/m9 soulful pads
    strings=False,
    log={    # low kalimba = log-drum answers
        "groove": [(0, 0, 2), (8, 0, 2)],
        "main": [(0, 0, 2), (5, 2, 1), (8, 0, 2), (11, 1, 1)],
    },
    melody={  # marimba rolling melody
        "main": [(0, 2, 1), (2, 3, 1), (4, 2, 1), (6, 1, 1), (8, 2, 1), (10, 3, 1),
                 (12, 4, 1), (14, 3, 1)],
    },
)

SOCA = dict(
    slug="track_05_afro_carib_soca", title="Afro-Carib Soca", bpm=110,
    key=("A", "major"), swing=0.10,
    prog=[("A", "maj"), ("D", "maj"), ("F#", "min"), ("E", "maj")],
    sections=[("intro", 4), ("verse", 8), ("hook", 8), ("outro", 4)],
    drums={
        "verse": {K: v([0, 3, 8, 11], 116, {0: 127}), SN: v([4, 12], 106),
                  SH: v(range(16), 52, {2: 70, 10: 70}), TB: v([4, 12], 72),
                  CG1: v([6, 14], 78)},
        "hook": {K: v([0, 3, 7, 8, 11, 14], 120, {0: 127}), SN: v([4, 12], 112),
                 CL: v([12], 86), SH: v(range(16), 58, {2: 74, 6: 74, 10: 74, 14: 74}),
                 TB: v([4, 12], 80), CB: v([7], 84), CG1: v([5, 9, 13], 86, {9: 100})},
        "intro": {K: v([0, 8], 100), SH: v(range(16), 48, {2: 66}), TB: v([4, 12], 66),
                  CG1: v([6], 72)},
        "outro": {K: v([0, 3, 8, 11], 104), SN: v([12], 96), SH: v(range(16), 50)},
    },
    bass={   # bouncy tresillo root-octave hops
        "verse": [(0, 0, 2), (3, 0, 2), (6, 7, 2), (8, 0, 2), (11, 0, 1), (13, 7, 1), (14, 12, 2)],
        "hook":  [(0, 0, 1), (3, 12, 1), (6, 7, 2), (8, 0, 1), (11, 0, 1), (14, 7, 2)],
    },
    pads=None,
    strings=False,
    brass={  # brass stabs on the drop
        "hook": [(0, 0, 2), (8, 0, 2)],
    },
    melody={  # steelpan surrogate (marimba) — call (bar A) / response (bar B)
        "hook": [(0, 0, 1), (2, 2, 1), (3, 3, 1), (6, 2, 1), (8, 4, 1), (10, 3, 1),
                 (11, 2, 1), (14, 0, 1)],
        "verse": [(0, 0, 1), (3, 2, 1), (6, 3, 1), (11, 2, 1)],
    },
)

TRACKS = [DARKCHILD, TIMBALAND, MISSY, BLACK_COFFEE, SOCA]

MAJ_PROGS = {s["slug"]: s["key"][1] == "major" for s in TRACKS}


# ------------------------------------------------------------- MIDI building
def build_midi(cfg):
    import pretty_midi

    pm = pretty_midi.PrettyMIDI(initial_tempo=cfg["bpm"])
    spb = 60.0 / cfg["bpm"]          # seconds per beat
    s16 = spb / 4.0                  # 16th
    swing = cfg["swing"]

    def t_of(bar, step):
        t = (bar * 16 + step) * s16
        if step % 2 == 1:
            t += swing * s16         # swing the off-16ths late
        return t

    is_major = cfg["key"][1] == "major"
    scale = MAJOR if is_major else MINOR
    root = midi_of(cfg["key"][0], 0)

    drums = pretty_midi.Instrument(program=0, is_drum=True, name="drums")
    bass = pretty_midi.Instrument(program=38, name="bass")
    pad_i = pretty_midi.Instrument(program=89 if cfg.get("pads") == "soul" else 48,
                                   name="pad/strings")
    plk = pretty_midi.Instrument(program=12, name="steelpan/marimba pluck")
    kal = pretty_midi.Instrument(program=108, name="log/kalimba")
    lead = pretty_midi.Instrument(program=80, name="lead/chops")
    zap = pretty_midi.Instrument(program=82, name="blip/zap")
    brass = pretty_midi.Instrument(program=62, name="brass stab")

    def add(inst, pitch, start, dur, vel):
        inst.notes.append(pretty_midi.Note(velocity=int(max(1, min(127, vel))),
                                           pitch=int(pitch), start=start, end=start + dur))

    def chord_notes(root_name, ctype, octv=3):
        r = midi_of(root_name, octv)
        return [r + iv for iv in CHORDS[ctype]]

    bar = 0
    total_bars = sum(n for _, n in cfg["sections"])
    for label, n in cfg["sections"]:
        for b in range(n):
            chord = cfg["prog"][(b) % len(cfg["prog"])]
            croot = midi_of(chord[0], 2)
            dr = cfg["drums"].get(label, cfg["drums"].get("verse", {}))
            for gm, velmap in dr.items():
                for step, vel in velmap.items():
                    add(drums, gm, t_of(bar, step), 0.12 if gm not in (K,) else 0.3, vel)
            bp = cfg["bass"].get(label)
            if bp:
                for step, d, ln in bp:
                    add(bass, croot + (d if d <= 7 else d), t_of(bar, step),
                        s16 * ln * 0.92, 104 if step == 0 else 92)
            if label in ("intro", "outro") or cfg.get("pads") or cfg.get("strings"):
                if label == "intro" or label == "outro" or cfg.get("pads") or cfg.get("strings"):
                    notes = chord_notes(chord[0], chord[1], 3)
                    dur = s16 * 16 * 0.98
                    start = t_of(bar, 0)
                    for nn in notes:
                        add(pad_i, nn, start, dur, 62 if label in ("intro", "outro") else 72)
                    if label == "hook" and (cfg.get("strings") or cfg.get("pads")):
                        for nn in notes:
                            add(pad_i, nn + 12, start, dur, 56)
            for key_name, inst, oct_shift in (("chops", lead, 1), ("lead", lead, 2),
                                              ("melody", plk, 2), ("plk", plk, 2),
                                              ("log", kal, 1), ("blip", zap, 3),
                                              ("brass", brass, 2)):
                m = (cfg.get(key_name) or {}).get(label)
                if not m:
                    continue
                pent = PENT_MAJ if is_major else PENT_MIN
                for step, d, ln in m:
                    pitch = deg(midi_of(chord[0], 3 + oct_shift - 1), pent, d)
                    add(inst, pitch, t_of(bar, step), s16 * ln * 0.95, 96 if step in (0, 8) else 84)
            bar += 1

    pm.instruments.extend([drums, bass, pad_i, plk, kal, lead, zap, brass])
    return pm, total_bars


# --------------------------------------------------------------- WAV synth
def _env(n, attack=0.004, decay=0.3):
    t = np.arange(n) / SR
    e = np.exp(-t / max(decay, 1e-4) * 6)
    a = int(attack * SR)
    if a > 0:
        e[:a] *= np.linspace(0, 1, a)
    return e


def synth_drum(gm, vel, dur):
    n = int(SR * dur)
    t = np.arange(n) / SR
    amp = vel / 127.0
    if gm == K:      # warm punchy kick: pitch sweep + click
        f = np.linspace(150, 44, n)
        body = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.002, 0.16)
        click = np.random.randn(min(n, int(0.004 * SR))) * 0.4 * _env(min(n, int(0.004 * SR)), 0.001, 0.004)
        out = body * 1.0
        out[:len(click)] += click
    elif gm in (SN,):  # snare: tone + noise
        noise = np.random.randn(n)
        nl = np.convolve(noise, np.ones(6) / 6, "same")     # crude lowpass
        tone = np.sin(2 * np.pi * 190 * t) * _env(n, 0.001, 0.06)
        out = (noise - nl) * 1.1 * _env(n, 0.001, 0.07) + tone * 0.8
    elif gm == CL:   # clap: 3 bursts
        out = np.zeros(n)
        for i, off in enumerate((0.0, 0.011, 0.024)):
            s = int(off * SR)
            m = n - s
            burst = np.random.randn(m) * _env(m, 0.001, 0.05 if i == 2 else 0.015)
            out[s:] += burst
    elif gm in (CH, PH):   # closed/pedal hat
        noise = np.random.randn(n)
        hp = noise - np.convolve(noise, np.ones(24) / 24, "same")
        out = hp * _env(n, 0.001, 0.02)
    elif gm == OH:
        noise = np.random.randn(n)
        hp = noise - np.convolve(noise, np.ones(24) / 24, "same")
        out = hp * _env(n, 0.001, 0.11)
    elif gm == SH:   # shaker: soft noisy swish
        noise = np.random.randn(n)
        bp = noise - np.convolve(noise, np.ones(16) / 16, "same")
        out = bp * _env(n, 0.008, 0.028) * 0.7
    elif gm in (CG1, CG2):   # conga/log: pitched thonk
        f0 = 170 if gm == CG1 else 300
        f = np.linspace(f0 * 1.25, f0 * 0.85, n)
        out = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.002, 0.05)
    elif gm in (WB_H, WB_L):  # woodblock
        f0 = 1180 if gm == WB_H else 860
        out = (np.sign(np.sin(2 * np.pi * f0 * t)) * 0.4 + np.sin(2 * np.pi * f0 * t) * 0.6) \
            * _env(n, 0.001, 0.018)
    elif gm in (TR_M, TR_O):  # triangle pops (Timbo "pops")
        f0 = 2400 if gm == TR_M else 1900
        out = np.sin(2 * np.pi * f0 * t) * _env(n, 0.001, 0.03 if gm == TR_M else 0.14)
    elif gm == TB:   # tambourine
        noise = np.random.randn(n)
        hp = noise - np.convolve(noise, np.ones(10) / 10, "same")
        out = hp * _env(n, 0.002, 0.045)
    elif gm == CB:   # cowbell
        out = (np.sign(np.sin(2 * np.pi * 540 * t)) + np.sign(np.sin(2 * np.pi * 800 * t))) * 0.35 \
            * _env(n, 0.001, 0.05)
    elif gm == KL:   # claves
        out = np.sin(2 * np.pi * 2450 * t) * _env(n, 0.001, 0.014)
    elif gm == RD:   # ride
        noise = np.random.randn(n)
        hp = noise - np.convolve(noise, np.ones(12) / 12, "same")
        out = hp * _env(n, 0.002, 0.16) * 0.5
    else:            # fallback tick
        out = np.sin(2 * np.pi * 1000 * t) * _env(n, 0.001, 0.02)
    return (out * amp * 0.9).astype(np.float32)


def synth_mel(pitch, vel, dur, kind):
    n = int(SR * dur)
    t = np.arange(n) / SR
    amp = vel / 127.0
    f = 440.0 * 2 ** ((pitch - 69) / 12)
    if kind == "bass":
        f = f / 2.0
        # glide into target from a fourth below for the "squeltch" feel
        fenv = np.linspace(f * 0.92, f, min(n, int(0.05 * SR)))
        ph = 2 * np.pi * np.cumsum(np.concatenate([fenv, np.full(n - len(fenv), f)])) / SR
        out = (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph))
        out *= _env(n, 0.004, dur * 0.55)
        out = np.tanh(out * 1.6) * 0.9
    elif kind == "pad":
        att = min(n, int(0.25 * SR))
        e = np.ones(n)
        e[:att] = np.linspace(0, 1, att)
        rel = int(0.2 * SR)
        e[-rel:] *= np.linspace(1, 0, rel)
        det = [1.0, 1.004, 0.997]
        out = sum(np.sin(2 * np.pi * f * d * t + i) for i, d in enumerate(det)) / 3
        out *= e
        out = np.tanh(out * 1.2) * 0.7
    elif kind == "pluck":
        h = [1.0, 0.6, 0.35, 0.22, 0.12]
        out = sum(a * np.sin(2 * np.pi * f * (i + 1) * t) for i, a in enumerate(h))
        out *= _env(n, 0.002, min(0.14, dur))
    elif kind == "log":
        fenv = np.linspace(f * 1.3, f * 0.9, n)
        out = np.sin(2 * np.pi * np.cumsum(fenv) / SR) * _env(n, 0.002, 0.09)
    elif kind == "brass":
        out = sum(np.sin(2 * np.pi * f * (i + 1) * t) / (i + 1) for i in range(6))
        out *= _env(n, 0.01, dur * 0.5)
        out = np.tanh(out * 1.4)
    elif kind == "zap":
        fenv = np.linspace(f * 0.5, f * 2.5, n)
        out = np.sin(2 * np.pi * np.cumsum(fenv) / SR) * _env(n, 0.001, 0.05)
        out = np.tanh(out * 2)
    else:  # lead/chop stabs
        h = [1.0, 0.5, 0.3, 0.15]
        out = sum(a * np.sin(2 * np.pi * f * (i + 1) * t) for i, a in enumerate(h))
        vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t)
        out = sum(a * np.sin(2 * np.pi * f * vib * (i + 1) * t) for i, a in enumerate(h))
        out *= _env(n, 0.003, dur * 0.6)
        out = np.tanh(out * 1.3)
    return (out * amp * 0.8).astype(np.float32)


PAN = {CH: 0.25, OH: 0.25, SH: -0.3, TB: 0.2, TR_M: -0.2, TR_O: -0.2,
       CG1: 0.15, CG2: -0.15, WB_H: 0.2, WB_L: -0.2, KL: -0.25, RD: 0.3}


def render_wav(cfg, path):
    spb = 60.0 / cfg["bpm"]
    s16 = spb / 4.0
    is_major = cfg["key"][1] == "major"
    scale = MAJOR if is_major else MINOR
    total_bars = sum(n for _, n in cfg["sections"])
    length = int((total_bars * 16 * s16 + 1.5) * SR)
    L = np.zeros(length, np.float32)
    R = np.zeros(length, np.float32)
    swing = cfg["swing"]

    def place(buf, sig, start, pan=0.0):
        s = int(start * SR)
        e = min(length, s + len(sig))
        if e <= s:
            return
        seg = sig[: e - s]
        # equal-power pan
        lg = math.cos((pan + 1) * math.pi / 4)
        rg = math.sin((pan + 1) * math.pi / 4)
        buf[0][s:e] += seg * lg
        buf[1][s:e] += seg * rg

    def t_of(bar, step):
        t = (bar * 16 + step) * s16
        if step % 2 == 1:
            t += swing * s16
        return t

    bar = 0
    for label, n_bars in cfg["sections"]:
        for b in range(n_bars):
            chord = cfg["prog"][b % len(cfg["prog"])]
            croot = midi_of(chord[0], 2)
            dr = cfg["drums"].get(label, cfg["drums"].get("verse", {}))
            for gm, velmap in dr.items():
                for step, vel in velmap.items():
                    dur = 0.35 if gm == K else (0.5 if gm == RD else 0.28)
                    sig = synth_drum(gm, vel, dur)
                    place((L, R), sig, t_of(bar, step), PAN.get(gm, 0.0))
            bp = cfg["bass"].get(label)
            if bp:
                for step, d, ln in bp:
                    pitch = croot + d
                    sig = synth_mel(pitch, 108 if step == 0 else 92, s16 * ln, "bass")
                    place((L, R), sig, t_of(bar, step), -0.05)
            if label in ("intro", "outro") or cfg.get("pads") or cfg.get("strings"):
                notes = [croot + 12 + iv for iv in CHORDS[chord[1]]]
                start = t_of(bar, 0)
                dur = s16 * 16 * 0.95
                lvl = 54 if label in ("intro", "outro") else 66
                for nn in notes:
                    place((L, R), synth_mel(nn, lvl, dur, "pad"), start, 0.1)
                if label == "hook" and (cfg.get("strings") or cfg.get("pads")):
                    for nn in notes:
                        place((L, R), synth_mel(nn + 12, 46, dur, "pad"), start, -0.15)
            for key_name, kind, oct_shift in (("chops", "lead", 1), ("lead", "lead", 2),
                                              ("melody", "pluck", 2), ("plk", "pluck", 2),
                                              ("log", "log", 1), ("blip", "zap", 3),
                                              ("brass", "brass", 2)):
                m = (cfg.get(key_name) or {}).get(label)
                if not m:
                    continue
                pent = PENT_MAJ if is_major else PENT_MIN
                for step, d, ln in m:
                    pitch = deg(midi_of(chord[0], 3 + oct_shift - 1), pent, d)
                    place((L, R), synth_mel(pitch, 96 if step in (0, 8) else 84,
                                            s16 * ln * 0.95, kind),
                          t_of(bar, step), 0.2 if key_name in ("melody", "plk") else 0.0)
            bar += 1

    mix = np.stack([L, R], axis=1)
    mix = np.tanh(mix * 1.15) * 0.92       # gentle glue/limiter
    data = (mix * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    return length / SR


# ------------------------------------------------------------ pattern sheets
def write_pattern_txt(cfg, path, total_bars):
    spb = 60.0 / cfg["bpm"]
    lines = [f"{cfg['title']} — {cfg['bpm']} BPM — {cfg['key'][0]} {cfg['key'][1]}",
             f"Source DNA: see producers/ cheat sheet. {total_bars} bars "
             f"({total_bars * 16 * spb / 60:.1f}s). Swing {int(cfg['swing'] * 100)}%.",
             "Section map: " + " | ".join(f"{l} x{n}" for l, n in cfg["sections"]), ""]
    for label, n in cfg["sections"]:
        lines.append(f"== {label.upper()} ({n} bars) ==")
        dr = cfg["drums"].get(label, cfg["drums"].get("verse", {}))
        for gm, velmap in sorted(dr.items()):
            grid = "".join("x" if s in velmap else "-" for s in range(16))
            lines.append(f"  {gm:>3}: |{grid}|")
        bp = cfg["bass"].get(label)
        if bp:
            grid = ["-"] * 16
            for step, d, ln in bp:
                grid[step] = "R" if d == 0 else ("O" if d == 12 else "5" if d == 7 else "d")
            lines.append(f"  bas: |{''.join(grid)}|")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


# ------------------------------------------------------------------- runner
def build_all():
    OUT.mkdir(exist_ok=True)
    report = []
    for cfg in TRACKS:
        pm, bars = build_midi(cfg)
        mid = OUT / f"{cfg['slug']}.mid"
        pm.write(str(mid))
        wav = OUT / f"{cfg['slug']}.wav"
        dur = render_wav(cfg, wav)
        write_pattern_txt(cfg, OUT / f"{cfg['slug']}_pattern.txt", bars)
        report.append((cfg["slug"], cfg["bpm"], f"{cfg['key'][0]} {cfg['key'][1]}",
                       bars, f"{dur:.1f}s", f"{wav.stat().st_size / 1e6:.1f}MB"))
    return report


def check_all():
    import pretty_midi
    ok = True
    for cfg in TRACKS:
        mid = OUT / f"{cfg['slug']}.mid"
        wav = OUT / f"{cfg['slug']}.wav"
        try:
            pm = pretty_midi.PrettyMIDI(str(mid))
            notes = sum(len(i.notes) for i in pm.instruments)
            drums = next(i for i in pm.instruments if i.is_drum)
            est = pm.get_end_time()
            _, tempi = pm.get_tempo_changes()
            tempo = tempi[0] if len(tempi) else 0
            with wave.open(str(wav)) as w:
                wdur = w.getnframes() / w.getframerate()
                assert w.getnchannels() == 2 and w.getsampwidth() == 2
                frames = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2")
            rms = float(np.sqrt(np.mean((frames.astype(np.float32) / 32767) ** 2)))
            okk = (notes > 100 and 30 < est < 120 and abs(wdur - est) < 4.0
                   and abs(tempo - cfg["bpm"]) < 0.5 and rms > 0.02)
            ok &= okk
            print(f"[{'OK ' if okk else 'BAD'}] {cfg['slug']}: {notes} notes "
                  f"({len(drums.notes)} drum), MIDI {est:.1f}s @ {tempo:.1f} BPM, "
                  f"WAV {wdur:.1f}s RMS={rms:.3f}, instruments={len(pm.instruments)}")
        except Exception as e:
            ok = False
            print(f"[BAD] {cfg['slug']}: {type(e).__name__}: {e}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if args.check:
        ok = check_all()
        sys.exit(0 if ok else 1)
    for row in build_all():
        print(f"built {row[0]}: {row[1]} BPM, {row[2]}, {row[3]} bars, {row[4]}, WAV {row[5]}")
    print("\n-- verification pass --")
    sys.exit(0 if check_all() else 1)


if __name__ == "__main__":
    main()
