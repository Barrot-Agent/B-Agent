"""Export an aligned WAV mix/stem bundle and a MIDI DAW-interchange file.

The output is editable through its Standard MIDI File and aligned WAV stems.
It is not a native DAW project. SoundFont source and licensing remain caller-
supplied metadata and are never asserted as independently verified.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import re
from pathlib import Path

from .audio_render import (
    _headroom_gain,
    _measure_audio_levels,
    _render_midi_stereo,
)
from .midi_export import export_midi
from .musical_dna import MusicalManifest


@dataclass(frozen=True)
class AudioProductionBundleResult:
    """Paths and technical measurements for one production bundle."""

    directory: Path
    mix_path: Path
    midi_path: Path
    stems: tuple[Path, ...]
    metadata_path: Path
    sample_rate: int
    duration_seconds: float
    peak_level: float
    true_peak_level: float
    rms_level: float
    channels: int


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _dbfs(value: float) -> float:
    return 20.0 * math.log10(max(float(value), 1e-12))


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "instrument"


def _write_float32_wav(path: Path, audio, sample_rate: int, wavfile) -> None:
    import numpy as np

    samples = np.asarray(audio, dtype=np.float32)
    if samples.ndim != 2 or samples.shape[1] != 2:
        raise ValueError("production bundle audio must be stereo")
    if not np.isfinite(samples).all():
        raise ValueError("production bundle audio contains non-finite samples")
    with path.open("xb") as output:
        wavfile.write(output, sample_rate, samples)


def render_production_bundle(
    manifest: MusicalManifest,
    destination_dir: str | Path,
    *,
    soundfont_path: str | Path,
    sample_rate: int = 44100,
    headroom_dbfs: float = -6.0,
    soundfont_source: str | None = None,
    soundfont_license: str | None = None,
) -> AudioProductionBundleResult:
    """Render a mix, sample-aligned instrument stems, MIDI, and QC metadata.

    Every WAV uses one common non-boosting gain and the same sample timeline.
    The MIDI file contains named instrument tracks. Separate synth passes can
    differ from the stereo mix in shared reverb/chorus behavior, so exact stem
    summation is not guaranteed. Existing output directories are never replaced.
    A failed run leaves its newly created partial directory for inspection.
    """
    target = Path(destination_dir)
    soundfont = Path(soundfont_path)
    if target.exists():
        raise FileExistsError(target)
    if not soundfont.is_file():
        raise FileNotFoundError(soundfont)
    if not 8000 <= sample_rate <= 192000:
        raise ValueError("sample_rate must be between 8000 and 192000")
    if len(set(manifest.instruments)) != len(manifest.instruments):
        raise ValueError("instrument names must be unique for stem export")
    _headroom_gain(0.0, headroom_dbfs)

    try:
        import numpy as np
        import pretty_midi
        from scipy.io import wavfile
        from scipy.signal import resample_poly
    except ImportError as exc:
        raise RuntimeError(
            "Production bundle export requires the optional music dependencies: "
            "pip install -e '.[music]'"
        ) from exc

    target.parent.mkdir(parents=True, exist_ok=True)
    target.mkdir(parents=True, exist_ok=False)

    midi_path = target / "composition.mid"
    mix_path = target / "mix.wav"
    stems_dir = target / "stems"
    stems_dir.mkdir(exist_ok=False)

    export_midi(manifest, midi_path)
    midi = pretty_midi.PrettyMIDI(str(midi_path))
    midi_end_seconds = float(midi.get_end_time())
    section_end_beats = max(
        (
            (section.start_bar - 1 + section.bars) * manifest.beats_per_bar
            for section in manifest.sections
        ),
        default=0,
    )
    section_end_seconds = section_end_beats * 60.0 / manifest.bpm
    musical_duration_seconds = max(midi_end_seconds, section_end_seconds)
    if not math.isfinite(musical_duration_seconds) or musical_duration_seconds <= 0:
        raise ValueError("composition has no finite positive musical duration")

    mix = _render_midi_stereo(
        midi,
        soundfont_path=soundfont,
        sample_rate=sample_rate,
        render_duration_seconds=musical_duration_seconds,
    )
    mix = np.asarray(mix, dtype=np.float32)
    if mix.ndim != 2 or mix.shape[1] != 2 or mix.shape[0] == 0:
        raise ValueError("renderer returned an empty or invalid stereo mix")

    stem_arrays = []
    stem_descriptors = []
    for index, instrument in enumerate(midi.instruments, start=1):
        filename = f"{index:02d}-{_safe_slug(instrument.name or f'instrument-{index}')}.wav"
        stem_path = stems_dir / filename
        if instrument.notes:
            stem_midi = pretty_midi.PrettyMIDI(
                initial_tempo=manifest.bpm,
                resolution=midi.resolution,
            )
            stem_midi.instruments.append(instrument)
            stem_audio = _render_midi_stereo(
                stem_midi,
                soundfont_path=soundfont,
                sample_rate=sample_rate,
                render_duration_seconds=musical_duration_seconds,
            )
            stem_audio = np.asarray(stem_audio, dtype=np.float32)
        else:
            stem_audio = np.zeros_like(mix)
        if stem_audio.shape != mix.shape:
            raise RuntimeError(
                f"Stem {instrument.name!r} is not sample-aligned with the stereo mix."
            )
        stem_arrays.append(stem_audio)
        stem_descriptors.append(
            {
                "instrument": instrument.name,
                "filename": filename,
                "path": f"stems/{filename}",
                "destination": stem_path,
            }
        )

    audio_arrays = [mix, *stem_arrays]
    source_levels = [
        _measure_audio_levels(audio, resample_poly, oversample=4)
        for audio in audio_arrays
    ]
    maximum_peak = max(
        max(sample_peak, true_peak)
        for sample_peak, true_peak, _ in source_levels
    )
    common_gain = _headroom_gain(maximum_peak, headroom_dbfs)
    rendered_arrays = [
        np.asarray(audio * common_gain, dtype=np.float32)
        for audio in audio_arrays
    ]
    rendered_levels = [
        _measure_audio_levels(audio, resample_poly, oversample=4)
        for audio in rendered_arrays
    ]

    rendered_mix = rendered_arrays[0]
    _write_float32_wav(mix_path, rendered_mix, sample_rate, wavfile)
    stem_paths = []
    stem_metadata = []
    for descriptor, audio, levels in zip(
        stem_descriptors, rendered_arrays[1:], rendered_levels[1:]
    ):
        stem_path = descriptor["destination"]
        _write_float32_wav(stem_path, audio, sample_rate, wavfile)
        stem_paths.append(stem_path)
        sample_peak, true_peak, rms = levels
        stem_metadata.append(
            {
                "instrument": descriptor["instrument"],
                "path": descriptor["path"],
                "sha256": _sha256_file(stem_path),
                "sample_count": int(audio.shape[0]),
                "peak_dbfs": _dbfs(sample_peak),
                "true_peak_dbtp": _dbfs(true_peak),
                "rms_dbfs": _dbfs(rms),
                "clip_sample_count": int(np.count_nonzero(np.abs(audio) >= 1.0)),
            }
        )

    sample_peak, true_peak, rms = rendered_levels[0]
    midi_sha256 = _sha256_file(midi_path)
    mix_sha256 = _sha256_file(mix_path)
    soundfont_sha256 = _sha256_file(soundfont)
    rights_status = (
        "CALLER_SUPPLIED_UNVERIFIED"
        if soundfont_source and soundfont_license
        else "MISSING_SOURCE_OR_LICENSE_METADATA"
    )
    metadata = {
        "schema_version": "1.0.0",
        "artifact_type": "barrot.audio.production_bundle",
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "manifest_fingerprint": manifest.fingerprint,
        "render_engine": "FluidSynth via pyfluidsynth",
        "sample_rate_hz": sample_rate,
        "channels": 2,
        "musical_duration_seconds": musical_duration_seconds,
        "rendered_duration_seconds": float(rendered_mix.shape[0] / sample_rate),
        "sample_count": int(rendered_mix.shape[0]),
        "bpm": manifest.bpm,
        "key": manifest.scale,
        "beats_per_bar": manifest.beats_per_bar,
        "time_signature": f"{manifest.beats_per_bar}/4",
        "time_signature_basis": (
            "Current MusicalManifest stores quarter-note beats per bar; "
            "the denominator is fixed at 4."
        ),
        "sections": [
            {
                "name": section.name,
                "start_bar": section.start_bar,
                "bars": section.bars,
                "energy": section.energy,
            }
            for section in manifest.sections
        ],
        "instruments": list(manifest.instruments),
        "common_gain_linear": common_gain,
        "headroom_ceiling_dbfs": headroom_dbfs,
        "mix": {
            "path": "mix.wav",
            "sha256": mix_sha256,
            "peak_dbfs": _dbfs(sample_peak),
            "true_peak_dbtp": _dbfs(true_peak),
            "rms_dbfs": _dbfs(rms),
            "clip_sample_count": int(np.count_nonzero(np.abs(rendered_mix) >= 1.0)),
        },
        "midi": {
            "path": "composition.mid",
            "sha256": midi_sha256,
            "track_names": [instrument.name for instrument in midi.instruments],
            "format": "Standard MIDI File",
        },
        "stems": stem_metadata,
        "stem_alignment": {
            "aligned": True,
            "sample_rate_hz": sample_rate,
            "channels": 2,
            "sample_count": int(rendered_mix.shape[0]),
            "timeline_origin_seconds": 0.0,
        },
        "stem_render_mode": (
            "One instrument per FluidSynth pass with a common gain and sample timeline."
        ),
        "stem_sum_reconstruction_guaranteed": False,
        "rights": {
            "soundfont_source": soundfont_source,
            "soundfont_license": soundfont_license,
            "soundfont_sha256": soundfont_sha256,
            "status": rights_status,
        },
        "native_daw_project_available": False,
        "daw_interchange": (
            "Standard MIDI File with named instrument tracks, aligned WAV stems, "
            "and JSON section/tempo/key metadata; import into a DAW. "
            "This is not a native DAW project."
        ),
    }
    metadata_path = target / "metadata.json"
    with metadata_path.open("x", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2, sort_keys=True)
        handle.write("\n")

    return AudioProductionBundleResult(
        directory=target,
        mix_path=mix_path,
        midi_path=midi_path,
        stems=tuple(stem_paths),
        metadata_path=metadata_path,
        sample_rate=sample_rate,
        duration_seconds=float(rendered_mix.shape[0] / sample_rate),
        peak_level=sample_peak,
        true_peak_level=true_peak,
        rms_level=rms,
        channels=2,
    )
