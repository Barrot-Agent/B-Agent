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
    programs = {"bass": 33, "keys": 4, "lead": 80, "pad": 89, "strings": 48}
    drum_pitches = {"kick": 36, "snare": 38, "hihat": 42, "hat": 42, "cymbal": 49, "percussion": 39}
    for name in manifest.instruments:
        is_drum = name.lower() in drum_pitches
        instrument = pretty_midi.Instrument(
            program=programs.get(name.lower(), 0), is_drum=is_drum, name=name
        )
        instruments[name] = instrument
        midi.instruments.append(instrument)

    seconds_per_beat = 60.0 / manifest.bpm
    for event in manifest.events:
        drum_pitch = drum_pitches.get(event.instrument.lower())
        pitch = event.pitch if event.pitch is not None else drum_pitch
        if pitch is None:
            continue
        start = event.beat * seconds_per_beat
        end = start + event.duration * seconds_per_beat
        instruments[event.instrument].notes.append(
            pretty_midi.Note(
                velocity=event.velocity,
                pitch=pitch,
                start=start,
                end=max(start + 0.01, end),
            )
        )
    for section in manifest.sections:
        marker_time = (
            (section.start_bar - 1) * manifest.beats_per_bar * seconds_per_beat
        )
        midi.add_marker(section.name, marker_time)

    path.parent.mkdir(parents=True, exist_ok=True)
    midi.write(str(path))
    return path
