"""Optional Standard MIDI File export for generated musical manifests."""
from __future__ import annotations

from pathlib import Path

from .musical_dna import MusicalManifest


def export_midi(manifest: MusicalManifest, destination: str | Path) -> Path:
    """Render a manifest to a new MIDI file; never overwrite an existing file."""
    path = Path(destination)
    if path.exists():
        raise FileExistsError(path)
    try:
        import pretty_midi
    except ImportError as exc:
        raise RuntimeError(
            "MIDI export requires the optional dependency: pip install -e '.[music]'"
        ) from exc

    midi = pretty_midi.PrettyMIDI(initial_tempo=manifest.bpm)
    instruments = {}
    for name in manifest.instruments:
        is_drum = name.lower() in {"kick", "snare", "hihat", "hat", "cymbal", "percussion"}
        instrument = pretty_midi.Instrument(
            program=0 if is_drum else 0, is_drum=is_drum, name=name
        )
        instruments[name] = instrument
        midi.instruments.append(instrument)

    seconds_per_beat = 60.0 / manifest.bpm
    for event in manifest.events:
        if event.pitch is None:
            continue
        start = event.beat * seconds_per_beat
        end = start + event.duration * seconds_per_beat
        instruments[event.instrument].notes.append(
            pretty_midi.Note(
                velocity=event.velocity,
                pitch=event.pitch,
                start=start,
                end=max(start + 0.01, end),
            )
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    midi.write(str(path))
    return path
