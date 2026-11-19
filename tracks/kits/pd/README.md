# One-Shot Kit — `tracks/kits/pd/`

Acquired 2026-11-14 to close the v1 "toy-timbre" gap (see
`producers/reference_acquisition.md`). Two origins, both clean:

## 1. Public-domain drum machine one-shots (15)
Source: `github.com/smpldsnds/drum-machines` — repository README declares
"A collection of public domain samples of different drum machines"
(checked before download; DrumCurate/Boochi44 candidates had NO license and
were rejected). Decoded TR-808 / 808-mini ogg one-shots to 44.1kHz mono
16-bit WAV, peak-normalized to 0.89, silence-trimmed.

kick_808, kick_808_soft, kick_808mini, snare_808, snare_808_ghost,
clap_808, hihat_closed_808, hihat_open_808, conga_low_808, conga_mid_808,
conga_hi_808, rimshot_808, maraca_808, tom_mid_808, cowbell_808

Notes: `bd0000/bd0025/…/bd1000` naming = the 808's velocity ladder; we took
the full-velocity + mid-velocity variants. Congas/rimshot/maraca directly
cover the v2 patch list for tracks 04/05 (percussion layer + dembow rims).

## 2. Synthesized signature sounds (9) — original, no third-party rights
Generated from physics in-house (numpy; modal synthesis, Karplus-Strong,
state-variable filters). No sampled commercial material involved.

| File | Method | Target role |
|---|---|---|
| logdrum_C/G | pitch-glided sine body (f0→0.6·f0, 18ms) + 2nd/2.83rd partials + click | Black Coffee track 04 answers |
| steelpan_C5/G4 | inharmonic bowl-mode partials (2.0/2.83/3.71/4.62/5.83 ratios) + strike noise | soca call-and-response track 05 |
| tumbi_D5/A4 | Karplus-Strong bright pluck (0.996 loop damp) | Missy track 03 hook |
| squelch_F1 | portamento saw (65→87Hz glide) → resonant 2-stage LP sweep | Darkchild glide bass track 01 |
| harp_F4/C5 | warm Karplus-Strong (0.9985 damp), long ring | Darkchild rhythmic-harp signature |

## Verification (2026-11-14)
- 24/24 one-shots load via soundfile, peak 0.89 ±0.01, durations 0.25–1.1s.
- Spectral spot-checks: fundamentals/partial structure present where
  expected (glides/bright plucks legitimately shift the dominant bin).

## Not acquired (deliberate)
- Copyrighted producer drum kits (search results were store listings).
- Producer reference loops/stems: need YOUR supply for the learning loop —
  analysis is fine to run, but taste anchors and A/B verdicts come from you.
