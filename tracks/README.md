# Barrot Beat DNA Vol. 1 — Starter Beats

Five starter beats built by Barrot from production-technique study (see
`../producers/*.md` cheat sheets). **Technique study, not song copying** — all
patterns are original grids derived from each producer's methods.

**v2 (2026-11-14):** rebuilt against the MCP-acquired patch list
(`../producers/reference_acquisition.md`) with real one-shots from
`kits/pd/`. User baseline: **all five v1 tracks rated 3/10** — v2 patches
timbre (real 808 kit + signature samples) and groove (per-layer timing, clave,
chant structure). Feedback ledger: `feedback/ledger.jsonl`.

Each track ships as:
- `.mid` — GM-format MIDI (drums on channel 10 + melodic instruments; v2 adds
  harp/tom-loop/clave/answer layers and bakes Timbaland per-layer offsets in).
  Drop it in any DAW, swap the sounds, keep the DNA.
- `.wav` — rendered stereo preview (44.1 kHz; v2 renders the kit one-shots
  directly, synth fallback only where no sample exists).
- `_pattern.txt` — 16-step grid chart + v2 patch notes per track.

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
- All 5 MIDIs reload via `pretty_midi`: 348–1053 notes each, tempo events exact
  (95.0 / 90.0 / 100.0 / 122.0 / 110.0 BPM).
- All 5 WAVs: stereo 16-bit 44.1 kHz, RMS 0.12–0.27, durations match MIDI ends.
- **v2 artifact checks**: Timbaland snare measured +27.3ms vs grid (spec 28ms,
  kick on-grid); hook kick-dropout bars 15/19 confirmed; SOCA clave measured at
  exactly steps 0/6/12/20+24 of the 2-bar cycle; and-of-2 snare accent present.
- **v2 kit evidence**: rendered kick/conga correlate against the kit samples
  ~4x / ~2.6x higher than the v1 synth baselines at identical positions (real
  samples audible in the mix). Steelpan/tumbi/harp are pitch-shifted so raw
  correlation is meaningless — evidence is structural (MIDI instruments) +
  spectral (track_05 centroid 10348→6862 Hz on the marimba→steelpan swap).
- v1→v2 spectral centroids all shifted (8095→6293, 7646→6189, 7406→5840,
  5617→5535, 10348→6862 Hz): every track audibly changed, none skipped.
- **v1 bug fixed**: Missy's `pluck` hook layer was absent from the v1 render/
  MIDI mapping lists — it never sounded. v1 track_03 shipped without its main
  hook layer (part of why it earned a 3). v2 renders it (tumbi) + adds the
  call-and-response answer (6 instruments now vs 4).
