"""Deterministic original composition from abstract musical constraints.

This module creates new harmony, bass, melody, and percussion patterns. It does
not copy source pitches or reconstruct a reference composition.
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass

from .musical_dna import Evaluation, MusicalEvent, MusicalManifest, MusicalSection, RecursiveCreativeMemory

_NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
_NOTE_TO_PC = {name: index for index, name in enumerate(_NOTE_NAMES)}
_NOTE_TO_PC.update({"Db": 1, "Eb": 3, "Gb": 6, "Ab": 8, "Bb": 10})
_MAJOR = (0, 2, 4, 5, 7, 9, 11)
_NATURAL_MINOR = (0, 2, 3, 5, 7, 8, 10)


@dataclass(frozen=True)
class CompositionSettings:
    bars: int = 16
    seed: int = 0
    melody_density: float = 0.55
    swing: float = 0.0

    def __post_init__(self) -> None:
        if not 1 <= self.bars <= 256:
            raise ValueError("bars must be between 1 and 256")
        if not 0.0 <= self.melody_density <= 1.0:
            raise ValueError("melody_density must be between 0 and 1")
        if not -0.49 <= self.swing <= 0.49:
            raise ValueError("swing must be between -0.49 and 0.49")


def _scale_info(scale: str) -> tuple[int, tuple[int, ...], bool]:
    match = re.match(r"^\s*([A-G](?:#|b)?)\s*(.*)$", scale, flags=re.IGNORECASE)
    if not match:
        raise ValueError("scale must begin with a note name, e.g. 'D minor' or 'F# major'")
    root_name = match.group(1).capitalize()
    if root_name not in _NOTE_TO_PC:
        raise ValueError(f"unsupported root note: {root_name}")
    mode = match.group(2).strip().lower()
    minor = "minor" in mode or mode in {"m", "aeolian"}
    return _NOTE_TO_PC[root_name], _NATURAL_MINOR if minor else _MAJOR, minor


def compose_original(
    template: MusicalManifest,
    settings: CompositionSettings = CompositionSettings(),
) -> MusicalManifest:
    """Create a fresh arrangement in the requested scale and instrument palette."""
    root, intervals, minor = _scale_info(template.scale)
    rng = random.Random(settings.seed)
    instruments = ("kick", "snare", "hihat", "bass", "keys", "lead")
    events: list[MusicalEvent] = []
    beats_per_bar = template.beats_per_bar

    # Four-bar harmonic cycle: a new, seed-selected diatonic progression.
    minor_progressions = ((0, 5, 2, 6), (0, 3, 6, 4), (0, 6, 3, 5))
    major_progressions = ((0, 4, 5, 3), (0, 3, 1, 4), (5, 3, 0, 4))
    progression = rng.choice(minor_progressions if minor else major_progressions)

    def scale_pitch(degree: int, octave: int) -> int:
        octave_shift, index = divmod(degree, len(intervals))
        return 12 * (octave + octave_shift) + root + intervals[index]

    for bar in range(settings.bars):
        start = bar * beats_per_bar
        degree = progression[bar % len(progression)]
        chord_degrees = (degree, degree + 2, degree + 4)
        chord = tuple(scale_pitch(d, 4) for d in chord_degrees)
        chord_root = scale_pitch(degree, 2)

        # Independent harmonic voicing and bass foundation.
        for pitch in chord:
            events.append(MusicalEvent("keys", "harmony", float(start), float(beats_per_bar), 72, pitch))
        events.append(MusicalEvent("bass", "low_end", float(start), 1.5, 96, chord_root))
        events.append(MusicalEvent("bass", "low_end", float(start + 2), 1.0, 84, chord_root))

        for beat in range(beats_per_bar):
            # Four-on-the-floor or halftime variations are selected by seed.
            if beat % 2 == 0 or rng.random() < 0.18:
                events.append(MusicalEvent("kick", "pulse", float(start + beat), 0.12, 105))
            if beat % 2 == 1:
                events.append(MusicalEvent("snare", "backbeat", float(start + beat), 0.12, 94))
            for subdivision in (0.0, 0.5):
                if rng.random() < 0.9:
                    offset = subdivision + (settings.swing if subdivision == 0.5 else 0.0)
                    events.append(MusicalEvent("hihat", "timekeeping", start + beat + offset, 0.08, rng.randint(55, 88)))

        # Melody is generated independently from scale tones and a fresh seed.
        for step in range(beats_per_bar * 2):
            if rng.random() > settings.melody_density:
                continue
            beat = start + (step * 0.5) + (settings.swing if step % 2 else 0.0)
            pitch = scale_pitch(rng.randrange(0, len(intervals) * 2), 5)
            duration = rng.choice((0.25, 0.5, 0.75))
            events.append(MusicalEvent("lead", "melody", float(beat), duration, rng.randint(70, 108), pitch))

    if settings.bars < 8:
        sections = (MusicalSection("main", 1, settings.bars, 0.65),)
    else:
        sections = (
            MusicalSection("intro", 1, 4, 0.35),
            MusicalSection("main", 5, settings.bars - 4, 0.75),
        )
    return MusicalManifest(
        bpm=template.bpm,
        beats_per_bar=beats_per_bar,
        scale=template.scale,
        instruments=instruments,
        events=tuple(sorted(events, key=lambda e: (e.beat, e.instrument, e.pitch or -1))),
        sections=sections,
        provenance=f"original_composition_seed_{settings.seed}",
    )

@dataclass(frozen=True)
class CompositionRun:
    manifest: MusicalManifest
    evaluation: Evaluation
    settings: CompositionSettings
    attempt_id: str
    learned_lessons: tuple[str, ...] = ()


def evaluate_composition(manifest: MusicalManifest) -> Evaluation:
    """Score required arrangement roles and diatonic pitch consistency."""
    required_roles = {"harmony", "melody", "low_end", "pulse", "backbeat"}
    present_roles = {event.role for event in manifest.events}
    role_coverage = len(required_roles & present_roles) / len(required_roles)
    root, intervals, _ = _scale_info(manifest.scale)
    allowed = {(root + interval) % 12 for interval in intervals}
    pitched = [event.pitch for event in manifest.events if event.pitch is not None]
    scale_adherence = (
        sum(1 for pitch in pitched if pitch % 12 in allowed) / len(pitched)
        if pitched else 0.0
    )
    reasons = []
    if role_coverage < 1.0:
        reasons.append("Required musical roles are missing")
    if scale_adherence < 0.98:
        reasons.append("Pitched events do not consistently follow the selected scale")
    score = round((0.7 * role_coverage) + (0.3 * scale_adherence), 4)
    passed = role_coverage == 1.0 and scale_adherence >= 0.98
    novelty = min(1.0, len(set(pitched)) / 12.0) if pitched else 0.0
    return Evaluation(passed, score, round(novelty, 4), round(scale_adherence, 4), tuple(reasons))


class RecursiveCompositionEngine:
    """Generate, evaluate, journal, and improve original compositions across runs."""

    def __init__(self, memory: RecursiveCreativeMemory):
        self.memory = memory

    def create(
        self,
        template: MusicalManifest,
        settings: CompositionSettings | None = None,
    ) -> CompositionRun:
        from dataclasses import asdict
        if not isinstance(self.memory, RecursiveCreativeMemory):
            raise TypeError("memory must be a RecursiveCreativeMemory")
        recommended = self.memory.recommend_composition_settings()
        if recommended and settings is None:
            recommended["seed"] = int(recommended["seed"]) + 1
            chosen = CompositionSettings(**recommended)
        else:
            chosen = settings or CompositionSettings()
        output = compose_original(template, chosen)
        evaluation = evaluate_composition(output)
        attempt = self.memory.record_composition_attempt(
            source_fingerprint=template.fingerprint,
            output_fingerprint=output.fingerprint,
            settings=asdict(chosen),
            evaluation=evaluation,
        )
        lessons = tuple(
            item["lesson"] for item in self.memory.verified_composition_lessons()
            if item.get("lesson")
        )
        return CompositionRun(output, evaluation, chosen, attempt["attempt_id"], lessons)

    def record_feedback(self, run: CompositionRun, *, feedback: str, lesson: str = ""):
        return self.memory.record_composition_feedback(
            run.attempt_id, feedback=feedback, lesson=lesson
        )
