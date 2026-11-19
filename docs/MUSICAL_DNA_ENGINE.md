# Barrot Musical DNA Transmutation Engine

## Purpose
Turn abstract musical structure into a repeatable analysis → transmutation → original composition → evaluation → recursive learning workflow.

## Implemented pipeline
1. **Manifest** — tempo, meter, scale, instrument roles, beat-relative events, durations, velocities, and section energy.
2. **Audio analysis** — optional `librosa` adapter extracts tempo, onset timing, RMS dynamics, and an estimated scale profile. It does not separate instruments from a mixed recording. Install with `pip install -e ".[music]"`.
3. **Transmutation** — controlled changes to phase, duration, swing, and dynamics while locked constraints remain fixed.
4. **Original composition** — seeded, repeatable composition of new diatonic harmony, melody, bass, and percussion patterns. This creates new material; it does not reproduce source pitches, lyrics, hooks, or distinctive arrangements.
5. **MIDI export** — optional `pretty_midi` adapter exports generated pitched notes and mapped percussion events. Existing files are never overwritten.
6. **Evaluation** — verify inventory preservation and measure whether a transformation is meaningfully different.
7. **Recursive memory** — append every attempt, including failures. Promote a reusable lesson only after the evaluator passes and the user gives explicit positive feedback.
8. **Next iteration** — use the best verified settings as a starting point, then evaluate the next result against the same criteria.

## Python entry points
- `barrot_agent.creative.analyze_audio(path)`
- `barrot_agent.creative.compose_original(manifest, CompositionSettings(...))`
- `barrot_agent.creative.RecursiveCompositionEngine(memory).create(manifest)`
- `run.learned_lessons` exposes approved lessons from earlier attempts
- `engine.record_feedback(run, feedback=..., lesson=...)` appends user feedback
- `barrot_agent.creative.export_midi(manifest, destination)`
- `barrot_agent.creative.transmute(manifest, Transmutation(...))`
- `barrot_agent.creative.evaluate_transmutation(source, candidate)`
- `barrot_agent.creative.RecursiveCreativeMemory(path)`

## Learning discipline
- Attempts are append-only and fingerprinted.
- Failures remain available as negative evidence.
- No lesson is promoted from model confidence alone.
- User feedback is separate from automated evaluation.
- A better score is not proof of artistic quality; human judgment remains decisive.
- This implementation stores external memory and preferences. It does not fine-tune model weights or claim autonomous changes to the underlying model.
- Do not store source audio, lyrics, melodies, or hooks in the learning journal. Store abstract features and fingerprints only.
- Audio analysis currently treats a mixed recording as a generic source track. True stem separation and instrument identification require a separately validated model/backend.
- The generated MIDI is a structured composition sketch, not a finished mastered production.

## Recursive iteration behavior
- Each generation is written to the append-only journal before user feedback arrives.
- Failed structural evaluations remain recorded and cannot be promoted.
- A passing result becomes reusable only after explicit positive user feedback and a concrete lesson.
- The next run uses the best-scoring approved composition settings and advances the random seed to explore a new variation.
- Approved lesson text is exposed to Barrot so later creative reasoning can account for prior feedback.

## Next integration stages
- Stem separation and instrument-role detection with an optional, explicitly configured backend.
- Richer harmonic and melodic evaluation, including voice-leading and phrase-level development.
- DAW/FluidSynth rendering and listening-based evaluation.
- A/B comparison against prior versions and regression detection across a user's approved creative preferences.
- A full recursive production run that persists manifests, generated MIDI, evaluation reports, and user feedback as versioned artifacts.
