# Reference Acquisition Log — Producer DNA v2 (2026-11-14)

Initiated with `web_search` (5 queries → 25 hits) + `webfetch`
(5 deep sources). Cross-referenced against the v1 cheat sheets in this
directory. This file records WHAT WAS ACQUIRED and the DELTAS vs our v1
tracks — the patch list for v2. No copyrighted audio was downloaded;
technique specs only.

## MCP connection status
- `opencode.list_mcp_resources`: 0 servers/0 templates (no file/memory MCP
  resources exposed) — local repo data + webfetch covered the rest.
- Local toolchain referenced: `.opencode/skill/music/SKILL.md` (fluidsynth +
  FluidR3_GM soundfont + ffmpeg + mpv = real playback/render upgrade path),
  `scripts/audio_ingest.py` + `.github/workflows/audio-ingest.yml`,
  `brain_corpus/polymath_music...json` (13 concept index, thin).

## Sources acquired (technical, per producer)
| Producer | Source | Key extraction |
|---|---|---|
| Darkchild | Roland interview (articles.roland.com) | JV-2080 **harp played rhythmically** (arpeggiated chords in rhythm form, NOT glistening pads) = THE signature across "The Boy Is Mine"/"Telephone"/"If You Had My Love"; R-8/Dr. Rhythm snare DNA; D-50 Nylon Atmosphere pad era; "melody is king" workflow |
| Timbaland | massivefm.com breakdown | **Per-layer timing**: layers push/pull against each other (kick rigid, percussion late) — NOT uniform swing; percussion-as-hook; silence discipline (mute kick a bar, strange accent every 4 bars); disciplined low end, midrange identity; repetition w/ micro-variation |
| Missy | revolt.tv "Get Ur Freak On" deep dive | **Tumbi hook + tabla** (bhangra DNA, Zero-G samples) as the main hook; chant-driven structure from DC **go-go** (simple enough to shout back); beat written for dancers/visuals first; hooks born from "stray keyboard sound" accidents |
| Black Coffee | theproducerschool.com tutorial | **Kick + tom-loop dual foundation** (tom low-cut ~80 Hz, sidechain-ducked); **sub-bass = sustained root only** (weight, not rhythm); **one-hit shaker at bar-end** anticipation; shaker noise-tail automation in builds; late piano (OTT+reverb) for the spiritual layer; 16-bar arrangement blocks w/ gradual filter opening; ambient bed (vinyl noise + root-pitched drone); E-minor root typical |
| Soca/dembow | grokipedia.com/page/Dembow_beat | Tresillo = **3+3+2 cross-rhythm**; snare accents on "and of 2" + beat 4 ("boom-ch-boom-chick") over 4-on-floor kick; **3-2 clave alignment** across 2 bars; 85–105 BPM reggaeton, 110–130 Dominican; TR-808 kick + 909 snare + congas/shakers layering |

## Cross-reference deltas — what v1 missed (v2 patch list)
1. **track_01 (Darkchild)**: v1 used string swells on the hook. MISSING: the
   rhythmic harp arpeggio signature — add arpeggiated harp figure
   (JV-2080-style plucked harp, rhythm form) as an identity element.
2. **track_02 (Timbaland)**: v1 applied uniform 20% swing. MISSING: per-layer
   timing offsets (rigid kick vs late percussion) + one strange accent every
   4 bars + optional kick-dropout bar in the hook.
3. **track_03 (Missy)**: v1 has kalimba plucks + sub drone. MISSING: chant
   test (is the hook shoutable back?) and a tumbi-style pluck hook; go-go
   call-and-response answer phrase.
4. **track_04 (Black Coffee)**: v1 has 4-on-floor + velocity shakers.
   MISSING: tom-loop layer under the kick (80 Hz low-cut, ducked), static
   root-only sub-bass, bar-end single shaker hits, noise-tail shaker builds,
   ambient texture bed.
5. **track_05 (soca)**: v1 has tresillo kick + dembow rims. MISSING: conga
   layer + explicit 3-2 clave alignment check across 2 bars + "and of 2"
   snare accent confirmation.

## Still requires human-supplied audio (cannot acquire via MCP)
- Reference loops/stems per producer (2–8 bar WAV) for librosa feature
  extraction (groove curves, velocity profiles, spectral palette).
- One-shot kits (kick/snare/hat + signature: log drum, steelpan, tumbi,
  squelch bass) — synthesized GM timbres are the v1 ceiling.
- User A/B verdicts + rating anchors (the 10 and the 3) for judge
  calibration in the learning loop (`tracks/feedback/ledger.jsonl`).

## Rebuild order when user supplies feedback
track_01 (harp) → track_04 (foundation split) → track_02 (layer offsets) →
track_05 (clave check) → track_03 (chant test). Each is a patch, not a
rewrite — per the refinement baseline.
