# Barrot Beat DNA Vol. 1 — Starter Beats

Five starter beats built by Barrot from production-technique study (see
`../producers/*.md` cheat sheets). **Technique study, not song copying** — all
patterns are original grids derived from each producer's methods.

Each track ships as:
- `.mid` — GM-format MIDI (drums on channel 10 + 7 melodic instruments). Drop it
  in any DAW, swap the sounds, keep the DNA.
- `.wav` — rendered stereo preview (44.1 kHz, synthesized in-house).
- `_pattern.txt` — 16-step grid chart of the main grooves.

Rebuild anytime: `python3 scripts/make_beats.py` · verify: `--check`.

Cover: `cover.png` (art via LunaRoute image gen, type set with PIL).

| # | Track | BPM | Key | Vibe | DNA source |
|---|-------|-----|-----|------|------------|
| 01 | `track_01_darkchild_rnb` | 95 | F minor | Punchy late-90s R&B: jerky backbeat, gliding squelch bass, staccato vocal-chop stabs, dramatic string swells on the hook | Rodney Jerkins / Darkchild |
| 02 | `track_02_timbaland_futuristic` | 90 | C minor | Off-grid half-time swing, woodblock/triangle "weird percussion as drums", galloping hook bass, glitch-zap pockets | Timbaland |
| 03 | `track_03_missy_minimal` | 100 | D minor | Futuristic minimal: big silences, static sub drone, kalimba-pluck weirdness, zap in the hole, ad-lib pocket reserved | Missy Elliott |
| 04 | `track_04_blackcoffee_afrohouse` | 122 | A minor | Deep Afro House: warm 4-on-floor, velocity-varied shaker 16ths, log-drum answers, soulful m9 pads, DJ-shaped long build | Black Coffee |
| 05 | `track_05_afro_carib_soca` | 110 | A major | Soca/afrobeats bounce: tresillo kick + dembow rims, steelpan-style call-and-response plucks, brass stabs on the drop, tambourine 2&4 | Catalyst + Afro/Carib (soca/dancehall) |

## Arrangement (all tracks)
`intro → verse → hook → outro` (Black Coffee uses DJ-shaped
`intro → groove → main → outro`), 24–28 bars each:

- **track_01**: 4 / 8 / 8 / 4 — strings + chops carry the hook
- **track_02**: 4 / 8 / 8 / 4 — percussion conversation, gallop bass enters on hook
- **track_03**: 4 / 8 / 8 / 4 — sparse verse, weirdness rotates per section
- **track_04**: 8 / 8 / 8 / 4 — elements accumulate and rarely leave
- **track_05**: 4 / 8 / 8 / 4 — dropout pre-hook, call-and-response plucks

## Verification (run 2026-11-14)
- All 5 MIDIs reload via `pretty_midi`: 268–1045 notes each, tempo events exact
  (95.0 / 90.0 / 100.0 / 122.0 / 110.0 BPM).
- All 5 WAVs: stereo 16-bit 44.1 kHz, RMS 0.11–0.18, durations match MIDI ends.
- `librosa` beat-tracking on 3 spot-checks: 95.7 / 123.0 / 112.3 detected vs
  95 / 122 / 110 spec — grooves lock to the intended pulse.
