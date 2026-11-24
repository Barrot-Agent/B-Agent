"""Deterministic original composition from abstract musical constraints.

This module creates new harmony, bass, melody, and percussion patterns. It does
not copy source pitches or reconstruct a reference composition.
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass

from .musical_dna import (
    Evaluation,
    MusicalEvent,
    MusicalManifest,
    MusicalSection,
    RecursiveCreativeMemory,
)

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
    preserve_instrument_palette: bool = True

    def __post_init__(self) -> None:
        if not 1 <= self.bars <= 256:
            raise ValueError("bars must be between 1 and 256")
        if not 0.0 <= self.melody_density <= 1.0:
            raise ValueError("melody_density must be between 0 and 1")
        if not -0.49 <= self.swing <= 0.49:
            raise ValueError("swing must be between -0.49 and 0.49")


@dataclass(frozen=True)
class SongForm:
    """Validated contiguous section plan for a full-length composition."""

    name: str
    sections: tuple[MusicalSection, ...]

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.sections:
            raise ValueError("song form name and sections are required")
        expected_start = 1
        names: set[str] = set()
        for section in self.sections:
            if section.start_bar != expected_start:
                raise ValueError("song form sections must be contiguous and ordered")
            if section.name in names:
                raise ValueError("song form section names must be unique")
            names.add(section.name)
            expected_start += section.bars

    @property
    def total_bars(self) -> int:
        return sum(section.bars for section in self.sections)


DEFAULT_PRODUCTION_INSTRUMENTS = (
    "kick", "snare", "hihat", "cymbal", "bass", "keys", "lead", "pad", "strings"
)

DEFAULT_FULL_SONG_FORM = SongForm(
    name="extended_pop_80",
    sections=(
        MusicalSection("intro", 1, 4, 0.25),
        MusicalSection("verse1", 5, 12, 0.45),
        MusicalSection("pre_chorus1", 17, 4, 0.62),
        MusicalSection("chorus1", 21, 8, 0.84),
        MusicalSection("verse2", 29, 12, 0.52),
        MusicalSection("pre_chorus2", 41, 4, 0.70),
        MusicalSection("chorus2", 45, 8, 0.90),
        MusicalSection("bridge", 53, 8, 0.42),
        MusicalSection("final_chorus", 61, 16, 1.0),
        MusicalSection("outro", 77, 4, 0.22),
    ),
)


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
    default_instruments = ("kick", "snare", "hihat", "bass", "keys", "lead")
    instruments = template.instruments if settings.preserve_instrument_palette else default_instruments
    drum_names = [
        name for name in instruments
        if name.lower() in {"kick", "snare", "hihat", "hat", "cymbal", "percussion"}
    ]
    pitched_names = [
        name for name in instruments
        if name.lower() not in {"kick", "snare", "hihat", "hat", "cymbal", "percussion"}
    ]
    if not pitched_names:
        raise ValueError("composition requires at least one pitched instrument")
    kick_name = "kick" if "kick" in instruments else (drum_names[0] if drum_names else None)
    snare_name = "snare" if "snare" in instruments else (drum_names[-1] if drum_names else None)
    hat_name = "hihat" if "hihat" in instruments else ("hat" if "hat" in instruments else None)
    bass_name = "bass" if "bass" in instruments else pitched_names[0]
    keys_name = "keys" if "keys" in instruments else pitched_names[0]
    lead_name = "lead" if "lead" in instruments else pitched_names[-1]
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
            events.append(MusicalEvent(keys_name, "harmony", float(start), float(beats_per_bar), 72, pitch))
        events.append(MusicalEvent(bass_name, "low_end", float(start), 1.5, 96, chord_root))
        events.append(MusicalEvent(bass_name, "low_end", float(start + 2), 1.0, 84, chord_root))

        for beat in range(beats_per_bar):
            # Four-on-the-floor or halftime variations are selected by seed.
            if kick_name and (beat % 2 == 0 or rng.random() < 0.18):
                events.append(MusicalEvent(kick_name, "pulse", float(start + beat), 0.12, 105))
            if snare_name and beat % 2 == 1:
                events.append(MusicalEvent(snare_name, "backbeat", float(start + beat), 0.12, 94))
            if hat_name:
                for subdivision in (0.0, 0.5):
                    if rng.random() < 0.9:
                        offset = subdivision + (settings.swing if subdivision == 0.5 else 0.0)
                        events.append(MusicalEvent(hat_name, "timekeeping", start + beat + offset, 0.08, rng.randint(55, 88)))

        # Melody is generated independently from scale tones and a fresh seed.
        for step in range(beats_per_bar * 2):
            if rng.random() > settings.melody_density:
                continue
            beat = start + (step * 0.5) + (settings.swing if step % 2 else 0.0)
            pitch = scale_pitch(rng.randrange(0, len(intervals) * 2), 5)
            duration = rng.choice((0.25, 0.5, 0.75))
            events.append(MusicalEvent(lead_name, "melody", float(beat), duration, rng.randint(70, 108), pitch))

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



def compose_full_song(
    template: MusicalManifest,
    *,
    seed: int = 0,
    form: SongForm = DEFAULT_FULL_SONG_FORM,
    melody_density: float = 0.58,
    swing: float = 0.0,
    instruments: tuple[str, ...] = DEFAULT_PRODUCTION_INSTRUMENTS,
) -> MusicalManifest:
    """Compose an original, section-aware full song with a reproducible hook motif.

    The default 80-bar form includes an intro, two verses, two pre-choruses,
    three choruses, a bridge, a final chorus, and an outro. Section-specific
    harmony, dynamics, percussion, fills, and motif treatments prevent the
    production path from being only a repeated four-bar loop. It remains an
    original composition draft; technical tests do not establish artistic
    quality or commercial sound-library rights.
    """
    if not isinstance(form, SongForm):
        raise TypeError("form must be a SongForm")
    if template.beats_per_bar != 4:
        raise ValueError("the current full-song production form supports 4/4 only")
    if not 0.0 <= melody_density <= 1.0:
        raise ValueError("melody_density must be between 0 and 1")
    if not -0.49 <= swing <= 0.49:
        raise ValueError("swing must be between -0.49 and 0.49")
    if not instruments or len(set(instruments)) != len(instruments):
        raise ValueError("production instruments must be non-empty and unique")
    supported = set(DEFAULT_PRODUCTION_INSTRUMENTS)
    unknown = set(instruments) - supported
    if unknown:
        raise ValueError(f"unsupported production instruments: {sorted(unknown)}")

    root, intervals, minor = _scale_info(template.scale)
    rng = random.Random(seed)
    instrument_names = tuple(instruments)
    drum_names = {
        name for name in instrument_names
        if name in {"kick", "snare", "hihat", "cymbal"}
    }
    pitched_names = [name for name in instrument_names if name not in drum_names]
    if not {"bass", "keys", "lead"} <= set(pitched_names):
        raise ValueError("full-song production requires bass, keys, and lead instruments")

    kick_name = "kick" if "kick" in drum_names else None
    snare_name = "snare" if "snare" in drum_names else None
    hat_name = "hihat" if "hihat" in drum_names else None
    cymbal_name = "cymbal" if "cymbal" in drum_names else None
    bass_name = "bass"
    keys_name = "keys"
    lead_name = "lead"
    pad_name = "pad" if "pad" in pitched_names else None
    strings_name = "strings" if "strings" in pitched_names else None

    def scale_pitch(degree: int, octave: int) -> int:
        octave_shift, index = divmod(degree, len(intervals))
        return 12 * (octave + octave_shift) + root + intervals[index]

    def velocity(base: int, energy: float, multiplier: float = 1.0) -> int:
        return max(1, min(127, round(base * (0.72 + 0.48 * energy) * multiplier)))

    def section_kind(name: str) -> str:
        lowered = name.lower()
        if lowered.startswith("pre"):
            return "pre"
        if "chorus" in lowered:
            return "chorus"
        if "bridge" in lowered:
            return "bridge"
        if "intro" in lowered:
            return "intro"
        if "outro" in lowered:
            return "outro"
        return "verse"

    minor_progressions = {
        "intro": (0, 5, 2, 6),
        "verse": (0, 5, 2, 6),
        "pre": (5, 6, 0, 6),
        "chorus": (0, 3, 6, 4),
        "bridge": (3, 0, 5, 6),
        "outro": (0, 5, 2, 6),
    }
    major_progressions = {
        "intro": (0, 4, 5, 3),
        "verse": (0, 4, 5, 3),
        "pre": (2, 3, 4, 4),
        "chorus": (0, 4, 5, 3),
        "bridge": (5, 3, 0, 4),
        "outro": (0, 4, 5, 3),
    }
    progressions = minor_progressions if minor else major_progressions

    # One four-bar motif is reused with controlled section/register changes.
    # This creates recognizable phrases while leaving room for arrangement variation.
    motif: list[list[tuple[float, int, float]]] = []
    previous_degree = 2
    for _bar in range(4):
        bar_notes: list[tuple[float, int, float]] = []
        for slot in range(4):
            if slot not in (0, 2) and rng.random() > 0.62:
                continue
            if slot == 0 and not motif:
                degree = 0
                previous_degree = degree
            else:
                previous_degree = max(
                    -1, min(len(intervals) + 1, previous_degree + rng.choice((-2, -1, 1, 2)))
                )
                degree = previous_degree
            bar_notes.append((float(slot), degree, rng.choice((0.5, 0.75, 1.0))))
        motif.append(bar_notes)

    events: list[MusicalEvent] = []
    beats_per_bar = template.beats_per_bar
    for section_index, section in enumerate(form.sections):
        kind = section_kind(section.name)
        progression = progressions[kind]
        next_section = (
            form.sections[section_index + 1]
            if section_index + 1 < len(form.sections)
            else None
        )
        next_kind = section_kind(next_section.name) if next_section else None

        for local_bar in range(section.bars):
            global_bar = section.start_bar - 1 + local_bar
            start = float(global_bar * beats_per_bar)
            phrase_index = local_bar // 4
            degree = progression[local_bar % 4]
            chord_degrees = (degree, degree + 2, degree + 4)
            chord = tuple(scale_pitch(value, 4) for value in chord_degrees)

            # Harmony changes by section; keys, pad, and strings have separate roles.
            key_velocity = velocity(76, section.energy)
            for pitch in chord:
                events.append(
                    MusicalEvent(keys_name, "harmony", start, 2.0, key_velocity, pitch)
                )
                if kind in {"chorus"}:
                    events.append(
                        MusicalEvent(
                            keys_name, "harmony", start + 2.0, 1.5,
                            velocity(66, section.energy), pitch
                        )
                    )
            if pad_name:
                events.append(
                    MusicalEvent(
                        pad_name, "sustain", start, float(beats_per_bar),
                        velocity(42, section.energy), scale_pitch(degree, 3)
                    )
                )
                events.append(
                    MusicalEvent(
                        pad_name, "sustain", start, float(beats_per_bar),
                        velocity(34, section.energy), scale_pitch(degree + 4, 3)
                    )
                )
            if strings_name and kind in {"pre", "chorus", "bridge"}:
                strings_pitch = scale_pitch(degree + (2 if kind != "bridge" else 4), 5)
                events.append(
                    MusicalEvent(
                        strings_name, "swell", start, float(beats_per_bar),
                        velocity(54, section.energy), strings_pitch
                    )
                )

            # Bass changes its pickup behavior between verse, build, and hook.
            events.append(
                MusicalEvent(
                    bass_name, "low_end", start, 1.5,
                    velocity(100, section.energy), scale_pitch(degree, 2)
                )
            )
            events.append(
                MusicalEvent(
                    bass_name, "low_end", start + 2.0, 1.0,
                    velocity(86, section.energy), scale_pitch(degree + 4, 2)
                )
            )
            if kind in {"pre", "chorus"} and local_bar % 2 == 1:
                next_degree = progression[(local_bar + 1) % 4]
                events.append(
                    MusicalEvent(
                        bass_name, "low_end", start + 3.5, 0.35,
                        velocity(76, section.energy), scale_pitch(next_degree, 2)
                    )
                )

            # Section-aware drum patterns create contrast and controlled builds.
            if kick_name:
                if kind == "intro":
                    kick_steps = (0.0,) if local_bar % 2 == 0 else ()
                elif kind == "verse":
                    kick_steps = (0.0, 2.0, 3.5) if rng.random() < 0.18 else (0.0, 2.0)
                elif kind == "pre":
                    kick_steps = (0.0, 1.5, 2.0, 3.5) if local_bar >= section.bars - 2 else (0.0, 2.0)
                elif kind == "chorus":
                    kick_steps = (0.0, 1.5, 2.5, 3.5) if local_bar % 2 == 0 else (0.0, 2.0, 3.5)
                elif kind == "bridge":
                    kick_steps = (0.0,) if local_bar % 2 == 0 else (2.0,)
                else:
                    kick_steps = (0.0,) if local_bar < section.bars // 2 else ()
                for beat in kick_steps:
                    events.append(
                        MusicalEvent(
                            kick_name, "pulse", start + beat, 0.12,
                            velocity(112, section.energy), None
                        )
                    )

            if snare_name:
                if kind in {"verse", "pre", "chorus"}:
                    snare_steps = (1.0, 3.0)
                elif kind == "bridge":
                    snare_steps = (2.0,)
                elif kind == "intro" and local_bar == section.bars - 1:
                    snare_steps = (3.0,)
                elif kind == "outro" and local_bar == 0:
                    snare_steps = (3.0,)
                else:
                    snare_steps = ()
                for beat in snare_steps:
                    events.append(
                        MusicalEvent(
                            snare_name, "backbeat", start + beat, 0.12,
                            velocity(100, section.energy), None
                        )
                    )

            if hat_name:
                if kind in {"verse", "pre", "chorus"}:
                    hat_steps = (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5)
                elif kind == "bridge":
                    hat_steps = (0.0, 1.0, 2.0, 3.0)
                elif kind == "intro":
                    hat_steps = (0.0, 2.0)
                else:
                    hat_steps = (0.0, 2.0) if local_bar < section.bars // 2 else (0.0,)
                for beat in hat_steps:
                    if beat not in (0.0, 2.0) and rng.random() > (0.45 + section.energy * 0.5):
                        continue
                    events.append(
                        MusicalEvent(
                            hat_name, "timekeeping", start + beat, 0.08,
                            velocity(66, section.energy, 0.92 if beat % 1 else 1.0), None
                        )
                    )

            if cymbal_name and kind in {"chorus", "bridge"} and local_bar == 0:
                events.append(
                    MusicalEvent(
                        cymbal_name, "section_accent", start, 0.2,
                        velocity(96, section.energy), None
                    )
                )

            # Repeated melodic motif, lifted for choruses and thinned for intros/outros.
            density_factor = {
                "intro": 0.35, "verse": 0.68, "pre": 0.82,
                "chorus": 1.0, "bridge": 0.52, "outro": 0.30,
            }[kind]
            octave = 6 if kind == "chorus" else 5
            section_shift = 2 if kind == "chorus" else (-1 if kind == "bridge" else (1 if kind == "pre" else 0))
            for note_index, (offset, motif_degree, duration) in enumerate(motif[local_bar % 4]):
                if note_index and rng.random() > melody_density * density_factor:
                    continue
                phrase_shift = 1 if phrase_index % 2 and note_index % 2 == 0 else 0
                degree_for_note = motif_degree + section_shift + phrase_shift
                pitch = scale_pitch(degree_for_note, octave)
                events.append(
                    MusicalEvent(
                        lead_name, "melody", start + offset + (swing if offset % 1 else 0.0),
                        duration, velocity(82 + (note_index % 2) * 6, section.energy), pitch
                    )
                )
                if kind == "chorus" and strings_name and note_index in (0, 2):
                    events.append(
                        MusicalEvent(
                            strings_name, "counter_melody", start + offset, duration,
                            velocity(50, section.energy), scale_pitch(degree_for_note, octave + 1)
                        )
                    )

            # Fill into the next chorus rather than repeating a static loop boundary.
            if snare_name and next_kind == "chorus" and local_bar == section.bars - 1:
                for beat in (3.0, 3.5):
                    events.append(
                        MusicalEvent(
                            snare_name, "transition_fill", start + beat, 0.1,
                            velocity(92, section.energy), None
                        )
                    )
                if hat_name:
                    events.append(
                        MusicalEvent(
                            hat_name, "transition_fill", start + 3.75, 0.06,
                            velocity(88, section.energy), None
                        )
                    )

    events.sort(key=lambda event: (
        event.beat, event.instrument,
        event.pitch if event.pitch is not None else -1,
        event.role,
    ))
    return MusicalManifest(
        bpm=template.bpm,
        beats_per_bar=beats_per_bar,
        scale=template.scale,
        instruments=instrument_names,
        events=tuple(events),
        sections=form.sections,
        provenance=f"original_full_song_{form.name}_seed_{seed}",
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
    required_roles = {"harmony", "melody", "low_end"}
    if any(
        name.lower() in {"kick", "snare", "hihat", "hat", "cymbal", "percussion"}
        for name in manifest.instruments
    ):
        required_roles.update({"pulse", "backbeat"})
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
