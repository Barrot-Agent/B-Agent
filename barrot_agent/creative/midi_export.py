"""Optional Standard MIDI File export for generated musical manifests."""
from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from .musical_dna import MusicalManifest


def export_midi(
    manifest: MusicalManifest,
    destination: str | Path,
    *,
    program_map: Mapping[str, int] | None = None,
) -> Path:
    """Render a manifest to MIDI with optional per-instrument GM program overrides."""
    if program_map is not None and not isinstance(program_map, Mapping):
        raise TypeError("program_map must map instrument names to General MIDI program numbers")
    supplied_programs = dict(program_map or {})
    unknown_programs = set(supplied_programs) - set(manifest.instruments)
    if unknown_programs:
        raise ValueError(f"program_map contains unknown instruments: {sorted(unknown_programs)}")
    for instrument_name, program in supplied_programs.items():
        if isinstance(program, bool) or not isinstance(program, int) or not 0 <= program <= 127:
            raise ValueError(
                f"program_map value for {instrument_name!r} must be an integer from 0 to 127"
            )
    path = Path(destination)
    if path.exists():
        raise FileExistsError(path)
    try:
        import pretty_midi
        import mido
    except ImportError as exc:
        raise RuntimeError(
            "MIDI export requires the optional music dependencies: pip install -e '.[music]'"
        ) from exc

    midi = pretty_midi.PrettyMIDI(initial_tempo=manifest.bpm)
    instruments = {}
    programs = {"bass": 33, "keys": 4, "lead": 80, "pad": 89, "strings": 48}
    drum_pitches = {"kick": 36, "snare": 38, "hihat": 42, "hat": 42, "cymbal": 49, "percussion": 39}
    for name in manifest.instruments:
        is_drum = name.lower() in drum_pitches
        instrument = pretty_midi.Instrument(
            program=supplied_programs.get(name, programs.get(name.lower(), 0)),
            is_drum=is_drum,
            name=name,
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
    path.parent.mkdir(parents=True, exist_ok=True)
    midi.write(str(path))

    if manifest.sections:
        midi_file = mido.MidiFile(str(path))
        marker_track = mido.MidiTrack()
        marker_track.append(
            mido.MetaMessage("track_name", name="Barrot Sections", time=0)
        )
        previous_tick = 0
        for section in manifest.sections:
            marker_tick = round(
                (section.start_bar - 1)
                * manifest.beats_per_bar
                * midi_file.ticks_per_beat
            )
            if marker_tick < previous_tick:
                raise ValueError("section markers must be in nondecreasing bar order")
            marker_track.append(
                mido.MetaMessage(
                    "marker",
                    text=section.name,
                    time=marker_tick - previous_tick,
                )
            )
            previous_tick = marker_tick
        marker_track.append(mido.MetaMessage("end_of_track", time=0))
        midi_file.tracks.append(marker_track)
        midi_file.save(str(path))

    return path
