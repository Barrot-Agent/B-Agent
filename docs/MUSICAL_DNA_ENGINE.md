# Barrot Musical DNA Transmutation Engine

## Purpose
Turn abstract musical structure into a repeatable analysis → transmutation → original composition → evaluation → recursive learning workflow.

## Pipeline
1. **Manifest** — tempo, meter, scale, instrument roles, beat-relative events, durations, velocities, and section energy.
2. **Transmutation** — controlled changes to phase, duration, swing, and dynamics while locked constraints remain fixed.
3. **Original composition** — use the transformed manifest as a design constraint, then create independent harmony, melody, bass, drums, and arrangement. The manifest is not a license to reproduce a source composition.
4. **Evaluation** — verify inventory preservation and measure whether the transformation is meaningfully different.
5. **Recursive memory** — append every attempt, including failures. Promote a reusable lesson only after the evaluator passes and the user gives explicit positive feedback.
6. **Next iteration** — use the best verified settings as a starting point, then evaluate the next result against the same criteria.

## Learning discipline
- Attempts are append-only and fingerprinted.
- Failures remain available as negative evidence.
- No lesson is promoted from model confidence alone.
- User feedback is separate from automated evaluation.
- A better score is not proof of artistic quality; human judgment remains decisive.
- This implementation stores external memory and preferences. It does not fine-tune model weights or claim autonomous changes to the underlying model.
- Do not store source audio, lyrics, melodies, or hooks in the learning journal. Store abstract features and fingerprints only.

## Current implementation boundary
The initial module provides typed manifests, deterministic rhythmic transmutation, structural evaluation, and evidence-gated recursive memory. DAW rendering, audio feature extraction, MIDI export, and learned harmony/melody generation are subsequent integration stages.
