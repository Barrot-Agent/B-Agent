# Reference Pipeline — Self-Test Record

`scripts/bench_reference.py` renders an 8-bar clip at 110 BPM where EVERY
event is known in advance (answer key), then runs `analyze_reference.py` and
grades recovery. This file records the measured results and the thresholds
derived from them. Run: `python3 scripts/bench_reference.py --analyze`
(exit 0 = all green).

## Answer key (truth)
- 110 BPM, swing 0.33 (odd 16ths late), snares pushed +15ms off-grid
- backbeat: kick steps 0/8/10, snare 4/12 (bars 2–7), 16th hats (swing on odds)
- bass A2/F2/G2/C3 (45/41/43/48) — exact pitches known
- lead: 11 notes (A4–E5) — exact pitches known
- chords: Am×4 → Fmaj7×2 → Gmaj×2 per bar
- sections: intro(2) / main(4) / outro(2)
- stems rendered separately: drums / bass / lead / chords

## Results (2026-11-15)
| Check | Stems mode | Mix mode |
|---|---|---|
| bpm | 110.0 exact (meta) | 109.96 detected (−0.04) |
| kick recall | 18/18 @40ms | 18/18 @60ms |
| snare +15ms push | +15.1ms median | +6.2ms median |
| swing est | 0.392 vs 0.33 | 0.254 vs 0.33 |
| bass pitches | 4/4 exact | 3/4 exact (C3 missed) |
| lead pitches | 11/11 | 6/11 |
| chord ladder | 8/8 | 6/8 (Gmaj bars read Emin7 in some runs) |
| sections | 3 found | 2–3 found (labels approximate) |
| **total** | **9/9 PASS** | **9/9 PASS** |

## Measured thresholds (do not "tune" by feel — re-measure via bench)
- low-band kick: 35ms-window centroid < 140 Hz (bench kicks 86–127; bass
  onsets 139+; bass-note onsets are skipped, not mislabeled)
- mid-band snare: 150 < centroid < 500 Hz AND decay < 0.95 (kick-bleed ~500+,
  hat-bleed decay > 1.0); suppressed within 25ms of a low-band kick
- high band: hat (decay ≤ 0.55) / ride (decay > 0.55)
- low-band onset detection in a full mix: log-compressed spectral flux
  (log1p(1e3·|STFT|)), delta=0.1 — 18/18 kick recall where plain flux missed
  6 (kicks quiet under pad+bass bed)
- beat grid: beat_track frames run ~+13ms late; each beat is gradient-refined
  to the low-band energy rise (−5ms residual measured) — without this a real
  +15ms push reads as +0
- bass pyin: fmin < 100 needs frame_length 4096 (2048 cannot resolve ~87Hz);
  mix-mode range 75–150 Hz + 170Hz lowpass (pads leak in otherwise)

## Known limits (honest)
- Swing estimate under-reads in mix mode (0.254 vs 0.33) — median diluted by
  non-hat odd-step events. Direction is always right; magnitude is range.
- Mix-mode lead transcription catches ~half the notes (drums pollute pyin);
  stems mode is exact. Chord templates can confuse relative minors (Gmaj vs
  Emin7 share 5 of 7 chroma bins).
- Section labels in mix mode are energy/density-ranked, not semantic.
- No neural polyphonic transcriber installs on this box (basic-pitch build
  backend broken) — DSP methods only. If exactness matters: send stems.
- Micro-timing resolution floor ≈ ±6ms in mix mode, ±2ms with stems.
