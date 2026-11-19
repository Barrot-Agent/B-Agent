"""Musical DNA analysis, safe transmutation, evaluation, and recursive learning.

This module stores abstract musical features, not source recordings or lyrics.
It is deliberately deterministic and model/provider agnostic.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MusicalEvent:
    """One abstract musical event on a beat-relative timeline."""

    instrument: str
    role: str
    beat: float
    duration: float
    velocity: int = 96
    pitch: int | None = None

    def __post_init__(self) -> None:
        if not self.instrument.strip() or not self.role.strip():
            raise ValueError("instrument and role are required")
        if not math.isfinite(self.beat) or self.beat < 0:
            raise ValueError("beat must be finite and non-negative")
        if not math.isfinite(self.duration) or self.duration <= 0:
            raise ValueError("duration must be finite and positive")
        if not 1 <= self.velocity <= 127:
            raise ValueError("velocity must be between 1 and 127")
        if self.pitch is not None and not 0 <= self.pitch <= 127:
            raise ValueError("pitch must be a MIDI note number")


@dataclass(frozen=True)
class MusicalSection:
    name: str
    start_bar: int
    bars: int
    energy: float = 0.5

    def __post_init__(self) -> None:
        if not self.name.strip() or self.start_bar < 1 or self.bars < 1:
            raise ValueError("section name, start_bar, and bars must be valid")
        if not 0.0 <= self.energy <= 1.0:
            raise ValueError("section energy must be between 0 and 1")


@dataclass(frozen=True)
class MusicalManifest:
    """Abstract, non-reconstructive description of a musical arrangement."""

    bpm: float
    beats_per_bar: int
    scale: str
    instruments: tuple[str, ...]
    events: tuple[MusicalEvent, ...]
    sections: tuple[MusicalSection, ...] = ()
    provenance: str = "user_supplied_abstract_features"

    def __post_init__(self) -> None:
        if not math.isfinite(self.bpm) or not 20 <= self.bpm <= 300:
            raise ValueError("bpm must be between 20 and 300")
        if not 1 <= self.beats_per_bar <= 16:
            raise ValueError("beats_per_bar must be between 1 and 16")
        if not self.scale.strip():
            raise ValueError("scale is required")
        if not self.instruments:
            raise ValueError("at least one instrument is required")
        known = set(self.instruments)
        if any(event.instrument not in known for event in self.events):
            raise ValueError("every event instrument must appear in instruments")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Transmutation:
    phase_shift_beats: float = 0.0
    duration_scale: float = 1.0
    swing: float = 0.0
    velocity_scale: float = 1.0

    def __post_init__(self) -> None:
        if not math.isfinite(self.phase_shift_beats):
            raise ValueError("phase shift must be finite")
        if not 0.25 <= self.duration_scale <= 4.0:
            raise ValueError("duration_scale must be between 0.25 and 4")
        if not -0.49 <= self.swing <= 0.49:
            raise ValueError("swing must be between -0.49 and 0.49")
        if not 0.25 <= self.velocity_scale <= 1.5:
            raise ValueError("velocity_scale must be between 0.25 and 1.5")


@dataclass(frozen=True)
class Evaluation:
    passed: bool
    score: float
    novelty: float
    constraint_adherence: float
    reasons: tuple[str, ...] = ()


def transmute(manifest: MusicalManifest, settings: Transmutation) -> MusicalManifest:
    """Transform event timing and expression while preserving musical inventory.

    Event count, instrument palette, roles, meter, tempo, and scale remain fixed.
    Beat positions wrap inside the original timeline; no source melody is generated.
    """
    if not manifest.events:
        return manifest
    end_beat = max(event.beat for event in manifest.events) + manifest.beats_per_bar
    transformed: list[MusicalEvent] = []
    for event in manifest.events:
        beat = event.beat + settings.phase_shift_beats
        # Apply swing to alternating half-beat subdivisions.
        whole = math.floor(beat)
        fraction = beat - whole
        if math.isclose(fraction, 0.5, abs_tol=1e-8):
            beat += settings.swing
        beat = beat % end_beat
        duration = max(0.0625, event.duration * settings.duration_scale)
        velocity = max(1, min(127, round(event.velocity * settings.velocity_scale)))
        transformed.append(MusicalEvent(
            instrument=event.instrument,
            role=event.role,
            beat=round(beat, 6),
            duration=round(duration, 6),
            velocity=velocity,
            pitch=event.pitch,
        ))
    transformed.sort(key=lambda item: (item.beat, item.instrument, item.role))
    return MusicalManifest(
        bpm=manifest.bpm,
        beats_per_bar=manifest.beats_per_bar,
        scale=manifest.scale,
        instruments=manifest.instruments,
        events=tuple(transformed),
        sections=manifest.sections,
        provenance="abstract_transmutation",
    )


def evaluate_transmutation(
    source: MusicalManifest,
    candidate: MusicalManifest,
    *,
    minimum_novelty: float = 0.05,
) -> Evaluation:
    """Evaluate structural integrity, constraint adherence, and meaningful change."""
    reasons: list[str] = []
    inventory_ok = (
        len(source.events) == len(candidate.events)
        and source.instruments == candidate.instruments
        and source.bpm == candidate.bpm
        and source.beats_per_bar == candidate.beats_per_bar
        and source.scale == candidate.scale
        and sorted(event.role for event in source.events)
        == sorted(event.role for event in candidate.events)
    )
    if not inventory_ok:
        reasons.append("Musical inventory or locked constraints changed")
    if not candidate.events:
        reasons.append("Candidate contains no events")
        return Evaluation(False, 0.0, 0.0, 0.0, tuple(reasons))

    if len(source.events) != len(candidate.events):
        novelty = 1.0
    else:
        differences = 0
        for original, changed in zip(
            sorted(source.events, key=lambda e: (e.beat, e.instrument, e.role)),
            sorted(candidate.events, key=lambda e: (e.beat, e.instrument, e.role)),
        ):
            if (
                not math.isclose(original.beat, changed.beat, abs_tol=1e-6)
                or not math.isclose(original.duration, changed.duration, abs_tol=1e-6)
                or original.velocity != changed.velocity
            ):
                differences += 1
        novelty = differences / max(1, len(source.events))

    adherence = 1.0 if inventory_ok else 0.0
    score = round((adherence * 0.7) + (novelty * 0.3), 4)
    if novelty < minimum_novelty:
        reasons.append("Transformation did not reach the minimum novelty threshold")
    passed = inventory_ok and novelty >= minimum_novelty
    return Evaluation(passed, score, round(novelty, 4), adherence, tuple(reasons))


class RecursiveCreativeMemory:
    """Append-only attempt journal with evidence-gated reusable lessons.

    Every attempt is retained, including failures. A lesson is promoted only
    when the evaluator passes and the user feedback is explicitly positive.
    This is durable external memory, not a claim that model weights changed.
    """

    def __init__(self, path: str | Path = "data/evolution/musical_attempts.jsonl"):
        self.path = Path(path)

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        records: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(item, dict):
                    records.append(item)
        return records

    def record_attempt(
        self,
        *,
        source_fingerprint: str,
        output_fingerprint: str,
        settings: Transmutation,
        evaluation: Evaluation,
        user_feedback: str,
        lesson: str = "",
    ) -> dict[str, Any]:
        feedback = user_feedback.strip().lower()
        positive = feedback in {"positive", "approved", "good", "better", "keep", "yes"}
        promoted = bool(evaluation.passed and positive and lesson.strip())
        record = {
            "attempt_id": hashlib.sha256(
                f"{source_fingerprint}:{output_fingerprint}:{len(self.read_all())}".encode()
            ).hexdigest(),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "source_fingerprint": source_fingerprint,
            "output_fingerprint": output_fingerprint,
            "settings": asdict(settings),
            "evaluation": asdict(evaluation),
            "user_feedback": user_feedback,
            "lesson": lesson.strip() if promoted else "",
            "lesson_promoted": promoted,
            "status": "verified_lesson" if promoted else "retained_unpromoted_attempt",
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
        return record

    def verified_lessons(self) -> list[dict[str, Any]]:
        return [record for record in self.read_all() if record.get("lesson_promoted")]

    def recommend_settings(self) -> Transmutation:
        """Return the settings from the best-rated verified lesson, if any."""
        lessons = self.verified_lessons()
        if not lessons:
            return Transmutation()
        best = max(lessons, key=lambda item: item["evaluation"]["score"])
        return Transmutation(**best["settings"])
