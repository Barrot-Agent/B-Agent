#!/usr/bin/env python3
"""analyze_reference.py — Barrot reference-track analysis pipeline.

Breaks a reference track down the way a producer studies it:
  1. exact timing    -> tempo, beat/16th grid, per-hit micro-offsets (push/pull),
                        swing estimate
  2. notes           -> bass + lead transcription (pyin), chord ladder per bar
  3. instruments     -> onset events classified into roles via band energy,
                        attack/decay shape, spectral centroid
  4. arrangement     -> per-bar feature vector -> novelty segmentation ->
                        section map + per-role entry/exit bars

Outputs per input REF (next to the file unless --outdir):
  REF.profile.json          machine-readable profile (feeds form_style.py)
  REF.breakdown.md          human-readable version of the four asks
  REF_transcription.mid     transcription as loadable MIDI

Two modes:
  mix  (default)      analyze the full mix; roles are heuristic, lead voice =
                      top voice only, chords = chroma templates.
  stems (via .meta)   if NAME.meta.json declares stems, each stem is analyzed
                      with its role pinned and results merged -- exact notes.

Known limits (measured, see references/SELFTEST.md):
  - polyphonic note transcription in a full mix is approximate (no neural
    transcriber installs on this box); stems give exact notes
  - drum role labels in a mix are heuristic band/shape rules, not a trained
    classifier
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

REPO = Path(__file__).resolve().parents[1]
HOP = 256          # pyin hop (~5.8ms @44.1k)
HOP_O = 512        # onset/chroma hop (~11.6ms)
MIN_NOTE_S = 0.06  # 60ms minimum note length
GMS = {            # transcription role -> GM program (MIDI export)
    "bass": 38, "lead": 80, "chords": 0, "kick": 36, "snare": 38,
    "hat": 42, "perc": 70, "ride": 51,
}
STEM_ROLE_FM = {   # stem role -> (fmin, fmax) for pyin; None = drums/chroma
    "bass": (35, 300), "lead": (200, 2200), "melody": (200, 2200),
    "chords": None, "pads": None, "kick": None, "snare": None,
    "hat": None, "perc": None, "drums": None, "fx": None,
}


# ------------------------------------------------------------------ audio io
def load_audio(path):
    d, sr = sf.read(str(path))
    if d.ndim > 1:
        d = d.mean(axis=1)
    return d.astype(np.float64), sr


def band_split(y, sr):
    out = {}
    spec = [("low", 30, 180), ("mid", 180, 800), ("high", 800, min(11000, sr // 2 - 100))]
    for name, lo, hi in spec:
        sos = []
        if lo > 0:
            sos.append(butter(4, lo, "hp", fs=sr, output="sos"))
        if hi < sr / 2 - 100:
            sos.append(butter(4, hi, "lp", fs=sr, output="sos"))
        z = y
        for s in sos:
            z = sosfilt(s, z)
        out[name] = z
    return out


def rms(x, sr, win=0.030, hop=0.005):
    n = max(1, int(win * sr))
    h = max(1, int(hop * sr))
    if len(x) < n:
        return np.array([float(np.sqrt(np.mean(x ** 2)))]) if len(x) else np.zeros(1)
    w = np.lib.stride_tricks.sliding_window_view(x, n)[::h]
    return np.sqrt(np.mean(w ** 2, axis=1))


def bands_low(y, sr):
    """30-180 Hz band for beat refinement / kick work."""
    return sosfilt(butter(4, 180, "hp", fs=sr, output="sos"),
                   sosfilt(butter(4, 30, "lp", fs=sr, output="sos"), y))


def smooth_env(x, sr, ms=1.0):
    k = max(1, int(sr * ms / 1000))
    return np.convolve(np.abs(x), np.ones(k) / k, mode="same")


def refine_beat(src, sr, t):
    """Refine one beat time to the physical energy rise of the low band.

    beat_track quantizes to frames and its flux peaks run late (bench:
    +13ms — that bias ate a real +15ms push, reading it as +0). The peak of
    the smoothed envelope's derivative marks the actual rise; -5ms is the
    bench-measured residual of this estimator. Beats with no low-band rise
    (pad-only intro beats) are left in place.
    """
    i0 = max(0, int((t - 0.04) * sr))
    i1 = min(len(src), int((t + 0.025) * sr))
    if i1 - i0 < 64:
        return t
    e = smooth_env(src[i0:i1], sr)
    g = np.diff(e, prepend=e[0])
    if float(g.max()) <= 2.0 * float(np.median(np.abs(g))) + 1e-12:
        return t                      # no clear rise here — do not shift
    t_new = (i0 + int(np.argmax(g))) / sr - 0.005
    return t if abs(t_new - t) > 0.03 else t_new


# ------------------------------------------------------------------ grid
def estimate_tempo(y, sr, meta):
    import librosa

    oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP_O)
    detected = None
    beats = None
    if not meta.get("bpm"):
        tempo, frames = librosa.beat.beat_track(onset_envelope=oenv, sr=sr,
                                                hop_length=HOP_O)
        tempo = float(np.atleast_1d(tempo)[0])
        # resolve half/double confusion into the 60-190 window
        cand = [tempo, tempo * 2, tempo / 2]
        good = [c for c in cand if 60 <= c <= 190]
        detected = min(good, key=lambda c: abs(c - 110)) if good else tempo
        beats = librosa.frames_to_time(frames, sr=sr, hop_length=HOP_O)
    bpm = float(meta.get("bpm") or detected)
    t0 = float(meta.get("first_downbeat", 0.0))
    if meta.get("bpm"):                     # trust user grid
        spb = 60.0 / bpm
        n = int((len(y) / sr - t0) / spb) + 1
        beats = t0 + np.arange(max(n, 1)) * spb
    elif len(beats):
        # refine beats to the physical energy rise (low band): beat_track's
        # frame-quantized times run ~+13ms late on the bench, which eats real
        # micro-timing (a +15ms push read as +0)
        low = bands_low(y, sr)
        beats = np.asarray([refine_beat(low, sr, float(b)) for b in beats])
        # beat_track only returns beats where the pulse is audible (e.g. it
        # skips a pad-only intro). Extend the grid over the full file at the
        # median beat gap so bars/onsets before the first detected beat exist.
        gap = float(np.median(np.diff(beats))) if len(beats) > 1 else 60.0 / bpm
        n_back = int(np.ceil(beats[0] / gap))
        n_fwd = int(np.ceil((len(y) / sr - beats[-1]) / gap)) + 1
        beats = np.concatenate([beats[0] + np.arange(-n_back, 0) * gap, beats,
                                beats[-1] + np.arange(1, n_fwd) * gap])
        beats = beats[(beats >= 0) & (beats <= len(y) / sr)]
    return detected, bpm, np.asarray(beats), oenv


def build_grid(beats, subdiv=4):
    """16th-note grid times by linear interpolation between beat times."""
    if len(beats) < 2:
        return np.array([])
    steps = [beats[0]]
    for i in range(len(beats) - 1):
        d = (beats[i + 1] - beats[i]) / subdiv
        for k in range(1, subdiv + 1):
            steps.append(beats[i] + k * d)
    return np.asarray(steps)


# ------------------------------------------------------------------ onsets
def band_onsets(y_band, sr, delta=0.02, log_compress=False):
    import librosa

    if len(y_band) < sr // 4 or np.abs(y_band).max() < 1e-6:
        return [], np.zeros(1)
    if log_compress:
        # log-compressed spectral flux: makes a quiet kick detectable on top
        # of a loud sustained bed (pad + bass) in a full mix.
        # delta=0.1 MEASURED on the bench: 18/18 kick recall, 35 onsets
        # (delta 0.2 drops to 14/18; 0.05 over-triggers at 72).
        S = np.log1p(1e3 * np.abs(librosa.stft(y_band, n_fft=1024,
                                               hop_length=HOP_O)))
        oenv = librosa.onset.onset_strength(S=S, sr=sr, hop_length=HOP_O)
        idx = librosa.onset.onset_detect(onset_envelope=oenv, sr=sr,
                                         hop_length=HOP_O, units="frames",
                                         backtrack=False, delta=0.1)
        times = librosa.frames_to_time(idx, sr=sr, hop_length=HOP_O)
        strengths = oenv[idx] if len(idx) else np.array([])
        return list(times), strengths
    oenv = librosa.onset.onset_strength(y=y_band, sr=sr, hop_length=HOP_O)
    idx = librosa.onset.onset_detect(onset_envelope=oenv, sr=sr, hop_length=HOP_O,
                                     units="frames", backtrack=False, delta=delta)
    times = librosa.frames_to_time(idx, sr=sr, hop_length=HOP_O)
    strengths = oenv[idx] if len(idx) else np.array([])
    return list(times), strengths


def event_features(y, sr, t, bands, source=None, win_s=0.10):
    """attack/decay/centroid snapshot after onset t.

    decay/centroid come from *source* (the signal where the onset was
    detected: full mix in stems mode, the band signal in mix mode); band
    shares always come from the full-mix bands dict. win_s = analysis
    window length (35ms for low-band kick centroid, 100ms for snare decay).
    """
    src = y if source is None else source
    i0 = int(t * sr)
    seg = src[i0:i0 + int(win_s * sr)]
    if len(seg) < 64:
        return None
    e = np.abs(seg)
    a = e[: len(e) // 3].mean() + 1e-9
    b = e[len(e) // 3:].mean() + 1e-9
    decay = float(b / a)
    w = np.hanning(len(seg))
    sp = np.abs(np.fft.rfft(seg * w))
    fr = np.fft.rfftfreq(len(seg), 1 / sr)
    centroid = float((fr * sp).sum() / max(sp.sum(), 1e-9))
    be = {k: float(rms(v[i0:i0 + int(0.05 * sr)], sr, 0.05, 0.05)[0]) for k, v in bands.items()}
    tot = sum(be.values()) + 1e-12
    return {"decay": decay, "centroid": centroid,
            "band_share": {k: v / tot for k, v in be.items()}}


def classify_event(f):
    """Band/shape rules -> role label. Thresholds MEASURED on the TR-808 kit
    via bench_reference (kick low .74/decay .08; snare low .54/decay .24)."""
    if f is None:
        return "unknown"
    share = f["band_share"]
    if share["low"] > 0.65:
        return "kick"
    if 0.40 < share["low"] <= 0.65 and f["decay"] > 0.15:
        return "snare"          # low body + noise tail = snare family
    if share["high"] > 0.5:
        return "ride" if f["decay"] > 0.55 else "hat"
    if share["mid"] > 0.45:
        return "snare" if f["centroid"] > 900 else "perc"
    return "perc"


# ------------------------------------------------------------------ notes
def midi_of_hz(f):
    return 69 + 12 * math.log2(max(f, 1e-6) / 440.0)


def pyin_notes(y, sr, fmin, fmax, vel_ref=100, voicing=0.55):
    import librosa

    if len(y) < sr // 2 or np.abs(y).max() < 1e-6:
        return []
    frame_length = 4096 if fmin < 100 else 2048   # 2048 can't resolve ~87Hz
    f0, _, vprob = librosa.pyin(y, fmin=fmin, fmax=fmax, sr=sr,
                                frame_length=frame_length, hop_length=HOP,
                                fill_na=np.nan)
    voiced = vprob > voicing
    times = librosa.times_like(f0, sr=sr, hop_length=HOP)
    notes = []
    i = 0
    n = len(f0)
    while i < n:
        if not voiced[i]:
            i += 1
            continue
        j = i
        while j < n and voiced[j]:
            j += 1
        seg = f0[i:j]
        seg = seg[~np.isnan(seg)]
        if len(seg):
            notes.append((float(times[i]), float(times[min(j, n - 1)]), float(np.median(seg))))
        i = j
    # split long notes at pitch jumps, drop tiny, quantize pitch
    out = []
    for st, en, f in notes:
        p = int(round(midi_of_hz(f)))
        dur = en - st
        if dur < MIN_NOTE_S:
            continue
        out.append({"pitch": p, "start": round(st, 4), "end": round(en, 4),
                    "dur": round(dur, 4), "vel": vel_ref})
    return merge_same_pitch(out)


def merge_same_pitch(notes):
    """join consecutive notes of the same pitch separated by < 30ms."""
    if not notes:
        return notes
    out = [dict(notes[0])]
    for nn in notes[1:]:
        if nn["pitch"] == out[-1]["pitch"] and nn["start"] - out[-1]["end"] < 0.03:
            out[-1]["end"] = nn["end"]
            out[-1]["dur"] = round(out[-1]["end"] - out[-1]["start"], 4)
        else:
            out.append(dict(nn))
    return out


def chord_templates():
    T = {}
    shapes = {"maj": (0, 4, 7), "min": (0, 3, 7), "maj7": (0, 4, 7, 11),
              "min7": (0, 3, 7, 10), "7": (0, 4, 7, 10), "sus4": (0, 5, 7),
              "dim": (0, 3, 6)}
    names = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
    for root in range(12):
        for suf, iv in shapes.items():
            v = np.zeros(12)
            for i in iv:
                v[(root + i) % 12] = 1 + (0.4 if i else 0)
            T[f"{names[root]}{suf}"] = v / np.linalg.norm(v)
    return T


def detect_chords(y, sr, bars, hp_hz=None):
    import librosa

    if hp_hz:
        sos = butter(4, hp_hz, "hp", fs=sr, output="sos")
        y = sosfilt(sos, y)
    T = chord_templates()
    labels = []
    for bi in range(len(bars) - 1):
        t0, t1 = bars[bi], bars[bi + 1]
        i0, i1 = int(t0 * sr), int(t1 * sr)
        seg = y[i0:i1]
        if len(seg) < sr // 4 or np.abs(seg).max() < 1e-5:
            labels.append({"bar": bi, "label": "-", "conf": 0.0})
            continue
        c = librosa.feature.chroma_cqt(y=seg, sr=sr, hop_length=HOP_O)
        v = c.mean(axis=1)
        v = v / (np.linalg.norm(v) + 1e-9)
        scores = {k: float(v @ tv) for k, tv in T.items()}
        best = max(scores, key=scores.get)
        srt = sorted(scores.values(), reverse=True)
        labels.append({"bar": bi, "label": best,
                       "conf": round(srt[0] - srt[1], 3)})
    return labels


# ------------------------------------------------------------------ structure
def bar_features(y, sr, bars, onsets, notes, chords):
    feats = []
    for bi in range(len(bars) - 1):
        t0, t1 = bars[bi], bars[bi + 1]
        ev = [o for o in onsets if t0 <= o["t"] < t1]
        nb = [n for n in notes["bass"] if t0 <= n["start"] < t1]
        seg = y[int(t0 * sr):int(t1 * sr)]
        e = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
        ch = chords[bi]["label"] if bi < len(chords) else "-"
        prev = chords[bi - 1]["label"] if 0 < bi <= len(chords) else "-"
        feats.append({"bar": bi, "energy": round(e, 4),
                      "onsets": len(ev),
                      "kicks": sum(1 for o in ev if o["role"] == "kick"),
                      "bass_notes": len(nb),
                      "chord": ch, "chord_change": ch != prev})
    return feats


def segment_sections(feats, min_bars=2):
    """novelty = distance between consecutive smoothed bar features."""
    import numpy as np

    if len(feats) < 3:
        return [{"start_bar": 0, "end_bar": len(feats), "label": "A", "bars": len(feats)}]
    vec = np.array([[f["energy"] * 8, f["onsets"] / 20, f["kicks"] / 8,
                     f["bass_notes"] / 8, 1.0 if f["chord_change"] else 0.0]
                    for f in feats])
    nov = np.zeros(len(vec))
    for i in range(1, len(vec)):
        nov[i] = np.linalg.norm(vec[i] - vec[i - 1])
    mx = float(nov.max()) or 1.0
    bounds = [0]
    for i in range(2, len(vec) - min_bars + 1):
        if (nov[i] > 0.55 * mx and nov[i] >= nov[i - 1]
                and (i == len(vec) - 1 or nov[i] >= nov[i + 1])
                and i - bounds[-1] >= min_bars):
            bounds.append(i)
    bounds.append(len(vec))
    secs = []
    for a, b in zip(bounds[:-1], bounds[1:]):
        e = float(np.mean([feats[i]["energy"] for i in range(a, b)]))
        d = float(np.mean([feats[i]["onsets"] for i in range(a, b)]))
        secs.append({"start_bar": a, "end_bar": b, "bars": b - a,
                     "energy": round(e, 4), "density": round(d, 1)})
    order = sorted(secs, key=lambda s: (s["energy"] + s["density"] / 40))
    labels = ["intro", "build", "main/hook", "outro"]
    for rank, s in enumerate(order):
        s["label"] = labels[min(rank, len(labels) - 1)]
    return sorted(secs, key=lambda s: s["start_bar"])


# ------------------------------------------------------------------ pipeline
def analyze_stem(path, role, meta, sr_ref=None):
    """Analyze one stem with its role pinned. Returns a partial profile dict."""
    y, sr = load_audio(path)
    out = {"role": role, "file": Path(path).name, "sr": sr, "seconds": len(y) / sr}
    fm = STEM_ROLE_FM.get(role)
    if fm:                                        # pitched stem
        frame_length = 4096 if fm[0] < 60 else 2048
        import librosa

        if len(y) < sr // 2 or np.abs(y).max() < 1e-6:
            out["notes"] = []
        else:
            f0, _, vprob = librosa.pyin(y, fmin=fm[0], fmax=fm[1], sr=sr,
                                        frame_length=frame_length, hop_length=HOP,
                                        fill_na=np.nan)
            voiced = vprob > 0.55
            times = librosa.times_like(f0, sr=sr, hop_length=HOP)
            raw = []
            i, n = 0, len(f0)
            while i < n:
                if not voiced[i]:
                    i += 1
                    continue
                j = i
                while j < n and voiced[j]:
                    j += 1
                seg = f0[i:j]
                seg = seg[~np.isnan(seg)]
                if len(seg):
                    raw.append((float(times[i]), float(times[min(j, n - 1)]),
                                float(np.median(seg))))
                i = j
            notes = []
            for st, en, f in raw:
                p = int(round(midi_of_hz(f)))
                if en - st < MIN_NOTE_S:
                    continue
                notes.append({"pitch": p, "start": round(st, 4),
                              "end": round(en, 4),
                              "dur": round(en - st, 4), "vel": 100})
            out["notes"] = merge_same_pitch(notes)
        out["onsets"] = []
    elif role in ("chords", "pads"):
        out["notes"] = []
        out["onsets"] = []
        out["chords_only"] = True
    else:                                         # drum-ish stem: classify hits
        bands = band_split(y, sr)
        events = []
        for bname in ("low", "mid", "high"):
            times, strengths = band_onsets(bands[bname], sr)
            for t, s in zip(times, strengths):
                f = event_features(y, sr, t, bands)
                r = classify_event(f) if role == "drums" else role
                vel = int(min(127, 40 + 87 * float(s)
                              / max(strengths.max(), 1e-9)))
                events.append({"t": round(float(t), 4), "role": r, "vel": vel})
        events.sort(key=lambda e: e["t"])
        dedup = []
        for e in events:
            if dedup and abs(e["t"] - dedup[-1]["t"]) < 0.025:
                if e["role"] == "kick":
                    dedup[-1] = e
                continue
            dedup.append(e)
        out["onsets"] = dedup
        out["notes"] = []
    return out


def analyze_mix(path, meta):
    y, sr = load_audio(path)
    detected, bpm, beats, oenv = estimate_tempo(y, sr, meta)
    grid = build_grid(beats)
    s16 = float(np.median(np.diff(beats))) / 4 if len(beats) > 1 else 0.0
    bars = beats[::4] if len(beats) >= 5 else np.array([0.0])

    bands = band_split(y, sr)
    # mix-mode classification: per-band local features, thresholds MEASURED
    # on the bench mix (see references/SELFTEST.md):
    #   low  band: kick centroid < 130 Hz; higher = bass-note onset (skip)
    #   mid  band: snare if 150 < centroid < 500 and decay < 0.95
    #              (kick-bleed sits ~500+, hat-bleed decays > 1.0)
    #   high band: hat (fast) / ride (slow decay)
    # Simultaneous hits (kick+hat) survive as separate events: different roles.
    raw_events = []
    for bname in ("low", "mid", "high"):
        # log-flux ONLY on the low band (measured: rescues quiet kicks under
        # the pad/bass bed); mid/high keep plain flux
        times, strengths = band_onsets(bands[bname], sr,
                                       log_compress=(bname == "low"))
        for t, s in zip(times, strengths):
            raw_events.append({"t": float(t), "band": bname, "s": float(s)})
    raw_events.sort(key=lambda e: e["t"])
    picked = []
    for e in raw_events:                       # dedupe within band overlaps
        if picked and abs(e["t"] - picked[-1]["t"]) < 0.025 \
                and e["band"] == picked[-1]["band"]:
            if e["s"] > picked[-1]["s"]:
                picked[-1] = e
            continue
        picked.append(e)
    events = []
    for e in picked:
        src = bands[e["band"]]
        if e["band"] == "low":
            # 35ms window: kick click before bass/pad sustain pollutes it
            # (measured: all bench kicks 86-127; threshold 140)
            f = event_features(y, sr, e["t"], bands, source=src, win_s=0.035)
            role = "kick" if f and f["centroid"] < 140 else None
            c, d = (f["centroid"], f["decay"]) if f else (None, None)
        else:
            f = event_features(y, sr, e["t"], bands, source=src)
            if f is None:
                continue
            c, d = f["centroid"], f["decay"]
            if e["band"] == "mid":
                role = "snare" if (150 < c < 500 and d < 0.95) else "perc"
            else:
                role = "ride" if d > 0.55 else "hat"
        if role is None:
            continue
        events.append({"t": round(e["t"], 4), "role": role,
                       "vel": int(min(127, 30 + 6 * e["s"])),
                       "centroid": round(c, 0) if c else None,
                       "dominant_band": e["band"]})
    # a mid-band "snare" stacked within 25ms of a low-band kick is the kick's
    # mid component (bench-measured), not a real snare — suppress it
    kt = sorted(e["t"] for e in events if e["role"] == "kick")
    events = [e for e in events
              if not (e["role"] == "snare" and e["dominant_band"] == "mid"
                      and any(abs(e["t"] - k) < 0.025 for k in kt))]
    events.sort(key=lambda e: e["t"])

    # micro-timing vs 16th grid
    if len(grid):
        for e in events:
            gi = max(0, min(len(grid) - 1, int(np.searchsorted(grid, e["t"]))))
            cands = [gi] + ([gi - 1] if gi else [])
            g = min(cands, key=lambda c: abs(grid[c] - e["t"]))
            e["step"] = int(g)
            e["offset_ms"] = round(float(e["t"] - grid[g]) * 1000, 1)
    else:
        for e in events:
            e["step"], e["offset_ms"] = None, None

    odd = [e["offset_ms"] for e in events
           if e.get("step") is not None and e["step"] % 2 == 1
           and abs(e["offset_ms"]) < 0.6 * s16 * 1000]
    swing = round(float(np.median(odd)) / (s16 * 1000), 3) if odd and s16 else None

    # notes — mix-mode bass extraction tight-lowpassed (pad roots at 220Hz+
    # otherwise leak in); lead voicing relaxed because drums pollute pyin
    low_y = bands["low"]
    sos = butter(4, 170, "lp", fs=sr, output="sos")
    bass_y = sosfilt(sos, low_y)
    sos = butter(4, 600, "hp", fs=sr, output="sos")
    lead_y = sosfilt(sos, y)
    notes = {"bass": pyin_notes(bass_y, sr, 75, 150, vel_ref=100, voicing=0.5),
             "lead": pyin_notes(lead_y, sr, 500, 2200, vel_ref=100, voicing=0.5)}

    # chroma on bass-filtered audio: bass fundamentals otherwise dominate the
    # chroma and drag every bar toward the bass note
    sos = butter(4, 130, "hp", fs=sr, output="sos")
    chords = detect_chords(sosfilt(sos, y), sr, bars, hp_hz=None)
    feats = bar_features(y, sr, bars, events, notes, chords)
    secs = meta.get("sections") or segment_sections(feats)
    if meta.get("sections"):
        secs = [{"start_bar": s["bar"], "end_bar": s["bar"] + s.get("bars", 4),
                 "label": s["label"], "bars": s.get("bars", 4)}
                for s in meta["sections"]]

    per_role = {}
    for e in events:
        per_role.setdefault(e["role"], []).append(e["offset_ms"])
    mt = {r: round(float(np.median(v)), 1) for r, v in per_role.items() if v}

    entry_exit = {}
    for r in sorted(per_role):
        bars_active = sorted({e["step"] // 16 for e in events
                              if e["role"] == r and e.get("step") is not None})
        if bars_active:
            entry_exit[r] = {"first_bar": bars_active[0], "last_bar": bars_active[-1],
                             "bars_active": len(bars_active)}

    profile = {
        "file": Path(path).name, "mode": "mix", "sr": sr,
        "seconds": round(len(y) / sr, 2),
        "bpm_detected": round(detected, 2) if detected else None,
        "bpm_used": round(bpm, 2),
        "beats": len(beats), "bars_estimated": len(bars) - 1,
        "swing_estimate": swing,
        "events": events, "microtiming_per_role_ms": mt,
        "notes": notes, "chords": chords, "bar_features": feats,
        "sections": secs, "roles": entry_exit,
        "meta_provided": {k: meta[k] for k in ("bpm", "key", "first_downbeat") if k in meta},
        "limits": ["mix mode: lead = top voice only; chords = chroma templates;"
                   " drum roles are heuristic band/shape rules"],
    }
    return profile


def analyze(path, meta, outdir):
    path = Path(path)
    outdir = Path(outdir)
    stems = meta.get("stems")
    if stems:
        parts = [analyze_stem(stems[r] if Path(stems[r]).is_absolute()
                              else path.parent / stems[r], r, meta) for r in stems]
        y, sr = load_audio(path)
        detected, bpm, beats, _ = estimate_tempo(y, sr, meta)
        bars = beats[::4] if len(beats) >= 5 else np.array([0.0])
        notes = {"bass": [], "lead": []}
        events = []
        for p in parts:
            events += p["onsets"]
            if p["role"] == "bass":
                notes["bass"] = p["notes"]
            elif p["role"] in ("lead", "melody"):
                notes.setdefault("lead", []).extend(p["notes"])
        notes["lead"].sort(key=lambda n: n["start"])
        ch_src = next((p for p in parts if p.get("chords_only")), None)
        ch_y = load_audio(path.parent / stems["chords"])[0] if ch_src else y
        chords = detect_chords(ch_y, sr, bars)
        if len(grid := build_grid(beats)):
            for e in events:
                gi = int(np.clip(np.searchsorted(grid, e["t"]), 0, len(grid) - 1))
                cands = [gi] + ([gi - 1] if gi else [])
                g = min(cands, key=lambda c: abs(grid[c] - e["t"]))
                e["step"], e["offset_ms"] = int(g), round(float(e["t"] - grid[g]) * 1000, 1)
        s16 = float(np.median(np.diff(beats))) / 4 if len(beats) > 1 else 0
        odd = [e["offset_ms"] for e in events if e.get("step") is not None
               and e["step"] % 2 == 1 and abs(e["offset_ms"]) < 0.6 * s16 * 1000]
        swing = round(float(np.median(odd)) / (s16 * 1000), 3) if odd and s16 else None
        feats = bar_features(y, sr, bars, events, notes, chords)
        secs = segment_sections(feats)
        per_role = {}
        for e in events:
            per_role.setdefault(e["role"], []).append(e["offset_ms"])
        mt = {r: round(float(np.median(v)), 1) for r, v in per_role.items() if v}
        profile = {
            "file": path.name, "mode": "stems", "sr": sr,
            "seconds": round(len(y) / sr, 2),
            "bpm_detected": round(detected, 2) if detected else None,
            "bpm_used": round(bpm, 2), "bars_estimated": len(bars) - 1,
            "swing_estimate": swing, "events": events,
            "microtiming_per_role_ms": mt, "notes": notes, "chords": chords,
            "bar_features": feats, "sections": secs,
            "stems": [{"role": p["role"], "file": p["file"],
                       "notes": len(p["notes"]), "onsets": len(p["onsets"])}
                      for p in parts],
            "meta_provided": {k: meta[k] for k in ("bpm", "key", "first_downbeat") if k in meta},
        }
    else:
        profile = analyze_mix(path, meta)
    profile["chords_mode"] = "chroma-templates"

    pj = outdir / f"{path.stem}.profile.json"
    pj.write_text(json.dumps(profile, indent=1))
    write_breakdown(profile, outdir / f"{path.stem}.breakdown.md")
    export_midi(profile, outdir / f"{path.stem}_transcription.mid")
    return profile, pj


# ------------------------------------------------------------------ exports
def write_breakdown(p, path):
    L = [f"# Breakdown — {p['file']}", "",
         f"Mode: {p['mode']} · BPM used: {p['bpm_used']}"
         + (f" (detected {p['bpm_detected']})" if p.get('bpm_detected') else "")
         + f" · {p['seconds']}s · swing est: {p.get('swing_estimate')}", ""]
    L += ["## 1. Exact timing", ""]
    mt = p.get("microtiming_per_role_ms") or {}
    if mt:
        L += ["| role | median offset vs 16th grid (ms) |", "|---|---|"]
        L += [f"| {r} | {v:+.1f} |" for r, v in sorted(mt.items(), key=lambda kv: -abs(kv[1]))]
        L += [""]
    if p.get("swing_estimate") is not None:
        L += [f"Swing: off-16ths sit ~{p['swing_estimate'] * 100:.0f}% of a 16th late.", ""]
    L += ["## 2. Notes", ""]
    for k in ("bass", "lead"):
        ns = p["notes"].get(k) or []
        L.append(f"### {k} — {len(ns)} notes")
        for n in ns[:64]:
            L.append(f"  {n['start']:7.3f}s  pitch {n['pitch']:3d}  {n['dur']:.2f}s")
        if len(ns) > 64:
            L.append(f"  … {len(ns) - 64} more")
        L.append("")
    L += ["### chord ladder", ""]
    L += [" ".join(f"{c['label']}({c['bar']})" for c in p["chords"]), ""]
    L += ["## 3. Instruments (roles)", ""]
    for r, ee in sorted((p.get("roles") or {}).items()):
        L.append(f"  {r}: bars {ee['first_bar']}–{ee['last_bar']}"
                 f" (active {ee['bars_active']})")
    L += [""]
    L += ["## 4. Arrangement", ""]
    for s in p["sections"]:
        L.append(f"  bars {s['start_bar']}–{s['end_bar'] - 1}: {s['label']}"
                 f" (energy {s['energy']}, density {s['density']}/bar)")
    L += [""]
    L += ["## Limits", ""]
    L += [f"  - {x}" for x in
          p.get("limits", ["stems recommended for exact notes"])]
    Path(path).write_text("\n".join(L), encoding="utf-8")


def export_midi(p, path):
    import pretty_midi

    pm = pretty_midi.PrettyMIDI(initial_tempo=p["bpm_used"])
    inst = {}
    drums = pretty_midi.Instrument(program=0, is_drum=True, name="transcription")
    role_gm = {"kick": 36, "snare": 38, "hat": 42, "perc": 70, "ride": 51,
               "drum": 38}
    for e in p.get("events", []):
        if e.get("t") is None:
            continue
        gmp = role_gm.get(e["role"])
        if gmp is not None:
            drums.notes.append(pretty_midi.Note(
                velocity=int(max(1, min(127, e["vel"]))), pitch=gmp,
                start=e["t"], end=e["t"] + 0.15))
    pm.instruments.append(drums)
    for name, prog in (("bass", 38), ("lead", 80)):
        for n in p.get("notes", {}).get(name, []):
            key = name
            if key not in inst:
                inst[key] = pretty_midi.Instrument(program=prog, name=name)
                pm.instruments.append(inst[key])
            inst[key].notes.append(pretty_midi.Note(
                velocity=n.get("vel", 100), pitch=n["pitch"],
                start=n["start"], end=n["end"]))
    for c in p.get("chords", []):
        if c["label"] in ("-", ""):
            continue
        import re

        m = re.match(r"^([A-G][#b]?)(.+)$", c["label"])
        if not m:
            continue
        base = {"C": 0, "C#": 1, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5,
                "F#": 6, "Gb": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}[m.group(1)]
        iv = {"maj": [0, 4, 7], "min": [0, 3, 7], "7": [0, 4, 7, 10],
              "maj7": [0, 4, 7, 11], "min7": [0, 3, 7, 10], "sus4": [0, 5, 7],
              "dim": [0, 3, 6]}.get(m.group(2), [0, 4, 7])
        if "chords" not in inst:
            inst["chords"] = pretty_midi.Instrument(program=0, name="chords")
            pm.instruments.append(inst["chords"])
        spb = 60.0 / p["bpm_used"]
        st = c["bar"] * 4 * spb
        for i in iv:
            inst["chords"].notes.append(pretty_midi.Note(
                velocity=70, pitch=48 + base + i, start=st, end=st + 4 * spb * 0.98))
    pm.write(str(path))


# ------------------------------------------------------------------ cli
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--meta", help="sidecar JSON: bpm/key/first_downbeat/sections/stems")
    ap.add_argument("--outdir", default=None)
    args = ap.parse_args()

    path = Path(args.audio)
    meta = {}
    if args.meta:
        meta = json.loads(Path(args.meta).read_text())
    else:
        side = path.parent / (path.name + ".meta.json")
        if side.is_file():
            meta = json.loads(side.read_text())
    outdir = Path(args.outdir) if args.outdir else path.parent
    profile, pj = analyze(path, meta, outdir)
    print(f"analyzed {path.name}: bpm={profile['bpm_used']} "
          f"(detected {profile['bpm_detected']}), bars={profile['bars_estimated']}, "
          f"events={len(profile['events'])}, bass_notes={len(profile['notes']['bass'])}, "
          f"lead_notes={len(profile['notes']['lead'])}, sections={len(profile['sections'])}")
    print(f"  -> {pj}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
