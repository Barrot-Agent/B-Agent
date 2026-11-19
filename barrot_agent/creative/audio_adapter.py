"""Optional audio-to-abstract-feature adapter.

Requires the optional `music` dependencies. Audio is analyzed in memory; this
adapter persists no recording, lyrics, melody transcription, or source file.
It deliberately reports a generic audio-source transient track rather than
claiming to separate instruments from a mixed recording.
"""
from __future__ import annotations

from pathlib import Path

from .musical_dna import MusicalEvent, MusicalManifest, MusicalSection


def analyze_audio(
    audio_path: str | Path,
    *,
    instrument_label: str = "audio_source",
) -> MusicalManifest:
    """Extract tempo, onset timing, dynamics, and an estimated scale profile."""
    path = Path(audio_path)
    if not path.is_file():
        raise FileNotFoundError(path)
    try:
        import librosa
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(
            "Audio analysis requires the optional dependencies: "
            "pip install -e '.[music]'"
        ) from exc

    signal, sample_rate = librosa.load(str(path), sr=None, mono=True)
    if signal.size == 0:
        raise ValueError("audio file contains no samples")

    tempo, beat_frames = librosa.beat.beat_track(y=signal, sr=sample_rate)
    bpm = float(np.asarray(tempo).reshape(-1)[0])
    if not np.isfinite(bpm) or bpm <= 0:
        bpm = 120.0

    onset_frames = librosa.onset.onset_detect(
        y=signal, sr=sample_rate, backtrack=False, units="frames"
    )
    onset_times = librosa.frames_to_time(onset_frames, sr=sample_rate)
    rms = librosa.feature.rms(y=signal)[0]
    rms_times = librosa.frames_to_time(np.arange(len(rms)), sr=sample_rate)
    chroma = librosa.feature.chroma_stft(y=signal, sr=sample_rate).mean(axis=1)

    major_template = np.asarray([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor_template = np.asarray([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    candidates = []
    for root in range(12):
        candidates.append((float(np.dot(chroma, np.roll(major_template, root))), root, "major"))
        candidates.append((float(np.dot(chroma, np.roll(minor_template, root))), root, "minor"))
    _, root, mode = max(candidates)
    scale = f"{('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')[root]} {mode}"

    beat_seconds = 60.0 / bpm
    events = []
    for index, seconds in enumerate(onset_times):
        beat = float(seconds) / beat_seconds
        next_seconds = float(onset_times[index + 1]) if index + 1 < len(onset_times) else float(seconds) + 0.2
        duration = max(0.0625, min(2.0, (next_seconds - float(seconds)) / beat_seconds))
        energy_index = int(np.argmin(np.abs(rms_times - seconds))) if len(rms_times) else 0
        energy = float(rms[energy_index]) if len(rms) else 0.5
        velocity = max(1, min(127, round(40 + energy * 300)))
        events.append(MusicalEvent(
            instrument=instrument_label,
            role="transient",
            beat=round(beat, 6),
            duration=round(duration, 6),
            velocity=velocity,
        ))

    if not events:
        # Preserve a valid manifest for sustained/no-onset material.
        events.append(MusicalEvent(instrument_label, "sustain", 0.0, 1.0, 64))

    duration_seconds = len(signal) / sample_rate
    total_beats = max(1.0, duration_seconds / beat_seconds)
    bars = max(1, int(total_beats // 4))
    sections = tuple(
        MusicalSection(f"section_{i + 1}", i * 8 + 1, min(8, max(1, bars - i * 8)), 0.5)
        for i in range((bars + 7) // 8)
    )
    return MusicalManifest(
        bpm=round(bpm, 3),
        beats_per_bar=4,
        scale=scale,
        instruments=(instrument_label,),
        events=tuple(events),
        sections=sections,
        provenance="audio_abstract_features_only",
    )
