#!/usr/bin/env python3
"""bench_reference.py — ground-truth test bench for analyze_reference.py.

Renders an 8-bar clip at 110 BPM from tracks/kits/pd one-shots + make_beats
synths, with EVERY event known in advance (bpm, swing, a deliberate +15ms
snare push, exact bass/lead pitches, chord ladder, 3 sections, stems), then
runs the analyzer and grades recovery against that answer key.

Usage: python3 scripts/bench_reference.py [--outdir /tmp/opencode/ref_bench]
Exit 0 = all checks pass. This is the honest way to claim the pipeline works.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_beats import SR, kit_drum, synth_mel  # noqa: E402

BPM = 110.0
SPB = 60.0 / BPM
S16 = SPB / 4
SWING = 0.33          # odd 16ths pushed late by 0.33 * s16
SNARE_PUSH = 0.015    # deliberate +15ms push on snares
BARS = 8


def t_of(bar, step):
    t = (bar * 16 + step) * S16
    return t + (SWING * S16 if step % 2 else 0.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="/tmp/opencode/ref_bench")
    ap.add_argument("--analyze", action="store_true",
                    help="run the analyzer on the bench and grade it")
    args = ap.parse_args()
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------- render bench
    length = int((BARS * 16 * S16 + 1.0) * SR)
    stems = {r: (np.zeros(length), np.zeros(length)) for r in
             ("drums", "bass", "lead", "chords")}

    def place(role, sig, t, pan=0.0):
        s = int(t * SR)
        e = min(length, s + len(sig))
        if e <= s:
            return
        lg = np.cos((pan + 1) * np.pi / 4)
        rg = np.sin((pan + 1) * np.pi / 4)
        stems[role][0][s:e] += sig * lg
        stems[role][1][s:e] += sig * rg

    truth = {"bpm": BPM, "swing": SWING, "snare_push_ms": SNARE_PUSH * 1000,
             "sections": [{"start_bar": 0, "end_bar": 2, "label": "intro"},
                          {"start_bar": 2, "end_bar": 6, "label": "main"},
                          {"start_bar": 6, "end_bar": 8, "label": "outro"}],
             "bass_notes": [], "lead_notes": [], "chord_per_bar": []}

    # chords: Am bars 0-3, Fmaj7 bars 4-5, Gmaj bars 6-7
    CH = {"Am": [57, 60, 64], "Fmaj7": [53, 57, 60, 64], "Gmaj": [55, 59, 62]}
    ladder = ["Am"] * 4 + ["Fmaj7"] * 2 + ["Gmaj"] * 2
    for bar, ch in enumerate(ladder):
        truth["chord_per_bar"].append({"bar": bar, "label": ch})
        lvl = 80 if bar in (0, 1, 6, 7) else 58   # pads sustain all bars
        for p in CH[ch]:
            place("chords", synth_mel(p, lvl, 4 * SPB * 0.95, "pad"), bar * 4 * SPB, 0.1)

    for bar in range(BARS):
        sec = "intro" if bar < 2 else ("main" if bar < 6 else "outro")
        if sec in ("main", "outro"):
            for st in (0, 8):
                place("drums", kit_drum(36, 120), t_of(bar, st))
            for st in (10,):
                place("drums", kit_drum(36, 96), t_of(bar, st))
        if sec == "main":
            for st in (4, 12):
                place("drums", kit_drum(38, 110), t_of(bar, st) + SNARE_PUSH)
            for st in range(16):           # 16th hats, odd 16ths swung (v1 convention)
                place("drums", kit_drum(42, 34 + 12 * (st % 4 == 2)), t_of(bar, st), 0.2)
        elif sec == "intro":
            for st in (0, 4, 8, 12):
                place("drums", kit_drum(42, 45), t_of(bar, st), 0.2)

    bass_seq = {2: [(0, 45, 4)], 3: [(0, 41, 4)], 4: [(0, 45, 2), (8, 48, 2)],
                5: [(0, 43, 4)], 6: [(0, 45, 4)], 7: [(0, 45, 4)]}
    for bar, seq in bass_seq.items():
        for st, p, beats_n in seq:
            # kind="bass" renders an octave below the given pitch -> feed p+12
            # so the audible fundamental equals the labeled truth pitch
            place("bass", synth_mel(p + 12, 108, beats_n * SPB, "bass"),
                  bar * 4 * SPB + st * S16)
            truth["bass_notes"].append({"bar": bar, "pitch": p})

    lead_seq = {2: [(0, 69, 1), (4, 72, 1), (8, 76, 2)],
                3: [(0, 76, 1), (4, 74, 1), (8, 72, 2)],
                4: [(0, 72, 1), (4, 69, 1), (8, 67, 2)],
                5: [(0, 67, 2), (8, 69, 2)]}
    for bar, seq in lead_seq.items():
        for st, p, beats_n in seq:
            place("lead", synth_mel(p, 96, beats_n * SPB * 0.9, "lead"),
                  bar * 4 * SPB + st * S16, 0.2)
            truth["lead_notes"].append({"bar": bar, "pitch": p})

    for role, (L, R) in stems.items():
        mix = np.stack([L, R], axis=1)
        mix = np.tanh(mix * 1.1) * 0.9
        with wave.open(str(out / f"bench.stem_{role}.wav"), "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((mix * 32767).astype("<i2").tobytes())
    full = sum(np.stack(x, axis=1) for x in stems.values())
    full = np.tanh(full * 1.1) * 0.9
    with wave.open(str(out / "bench.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((full * 32767).astype("<i2").tobytes())
    meta = {"stems": {"drums": "bench.stem_drums.wav", "bass": "bench.stem_bass.wav",
                      "lead": "bench.stem_lead.wav", "chords": "bench.stem_chords.wav"},
            "bpm": BPM, "first_downbeat": 0.0, "key": "A minor"}
    (out / "bench.wav.meta.json").write_text(json.dumps(meta, indent=1))
    (out / "bench_truth.json").write_text(json.dumps(truth, indent=1))
    print(f"bench rendered -> {out}/bench.wav (+4 stems, meta, truth)")
    if not args.analyze:
        return 0

    # --------------------------------------------- analyze + grade BOTH modes
    AR = Path(__file__).parent / "analyze_reference.py"

    def run_analyzer(audio, meta):
        cmd = [sys.executable, str(AR), str(audio), "--outdir", str(out)]
        if meta:
            cmd += ["--meta", str(meta)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print("ANALYZER FAILED:", (r.stderr or r.stdout)[-900:])
            return None
        print((r.stdout or "").strip().splitlines()[0])
        return json.loads((out / (Path(audio).stem + ".profile.json")).read_text())

    def norm_chord(lbl):
        for suf, std in (("min7", "m7"), ("min", "m"), ("maj7", "maj7"), ("maj", "")):
            if lbl.endswith(suf):
                return lbl[:-len(suf)] + std
        return lbl

    def grade(prof, mode, strict):
        """strict=True: stems mode thresholds. strict=False: mix mode."""
        checks = []

        def chk(name, ok, detail):
            checks.append((name, ok, detail))
            print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")

        ev = prof["events"]
        if strict:
            chk("bpm", abs(prof["bpm_used"] - BPM) < 0.5,
                f"used {prof['bpm_used']} vs {BPM}")
        else:
            d = prof.get("bpm_detected")
            chk("bpm detected", d is not None and abs(d - BPM) < 2.0,
                f"detected {d} vs {BPM} (used {prof['bpm_used']})")
        kicks = [e for e in ev if e["role"] == "kick"]
        kick_truth = [t_of(b, st) for b in range(2, 8) for st in (0, 8, 10)]
        win = 0.04 if strict else 0.06
        need = len(kick_truth) if strict else 18
        hit = sum(1 for kt in kick_truth if any(abs(e["t"] - kt) < win for e in kicks))
        chk("kick recall", hit >= need,
            f"{hit}/{len(kick_truth)} within {win * 1000:.0f}ms "
            f"({len(kicks)} kick-labeled events)")
        sn = [e for e in ev if e["role"] == "snare"]
        if sn:
            med = float(np.median([e["offset_ms"] for e in sn]))
            lo, hi = (8, 22) if strict else (5, 28)
            chk("snare push recovered", lo <= med <= hi,
                f"median {med:+.1f}ms vs truth +{SNARE_PUSH * 1000:.0f}ms "
                f"({len(sn)} snare events)")
        else:
            chk("snare push recovered", False, "no snare-labeled events")
        sw = prof.get("swing_estimate")
        swin = (0.21, 0.45) if strict else (0.15, 0.55)
        chk("swing estimate", sw is not None and swin[0] <= sw <= swin[1],
            f"{sw} vs truth {SWING}")
        tb = {n["pitch"] for n in truth["bass_notes"]}
        gb = {n["pitch"] for n in prof["notes"]["bass"]}
        need_b = 4 if strict else 3
        chk("bass pitches", len(tb & gb) >= need_b,
            f"{len(tb & gb)}/{len(tb)} exact (truth {sorted(tb)}, "
            f"got {sorted(gb)}, {len(prof['notes']['bass'])} notes)")
        tl = [n["pitch"] for n in truth["lead_notes"]]
        gl = [n["pitch"] for n in prof["notes"]["lead"]]
        matched = sum(1 for p in tl if p in gl and gl.remove(p) is None)
        need_l = int(0.8 * len(tl)) if strict else 6
        chk("lead pitches", matched >= need_l, f"{matched}/{len(tl)} matched")
        okc = sum(1 for a, b in zip(prof["chords"], truth["chord_per_bar"])
                  if norm_chord(a["label"]) == norm_chord(b["label"]))
        need_c = 6 if strict else 5
        chk("chord ladder", okc >= need_c,
            f"{okc}/8 correct: " + " ".join(c["label"] for c in prof["chords"]))
        need_s = 3 if strict else 2
        chk("sections", len(prof["sections"]) >= need_s,
            f"{len(prof['sections'])}: "
            + "; ".join(f"{s['start_bar']}-{s['end_bar'] - 1}:{s['label']}"
                        for s in prof["sections"]))
        chk(f"mode={prof['mode']}", prof["mode"] == ("stems" if strict else "mix"),
            f"mode={prof['mode']}")
        ok = all(c[1] for c in checks)
        print(f"  -> {mode.upper()} MODE: "
              f"{sum(c[1] for c in checks)}/{len(checks)} checks "
              f"{'PASS' if ok else 'FAIL'}\n")
        return ok

    ok_all = True
    print("=== STEMS MODE (meta with 4 stems, bpm given) ===")
    p1 = run_analyzer(out / "bench.wav", out / "bench.wav.meta.json")
    ok_all &= bool(p1) and grade(p1, "stems", strict=True)
    print("=== MIX MODE (bare WAV copy, no sidecar, no meta) ===")
    import shutil

    shutil.copy(out / "bench.wav", out / "bench_mix.wav")
    p2 = run_analyzer(out / "bench_mix.wav", None)
    ok_all &= bool(p2) and grade(p2, "mix", strict=False)
    print(f"BENCH OVERALL: {'PASS' if ok_all else 'FAIL'}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
