"""Export an aligned WAV mix/stem bundle and a MIDI DAW-interchange file.

The output is editable through its Standard MIDI File and aligned WAV stems.
It is not a native DAW project. SoundFont source and licensing remain caller-
supplied metadata and are never asserted as independently verified.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import re
from pathlib import Path

from .audio_render import (
    AUDIO_QUALITY_BENCHMARK_VERSION,
    _headroom_gain,
    _measure_audio_levels,
    _measure_loudness,
    _measure_stereo_integrity,
    _limit_stereo_side_for_mono_compatibility,
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


def _remove_dc_offset(audio):
    """Center each stereo channel and retain the reversible pre-gain offsets."""
    import numpy as np

    samples = np.asarray(audio, dtype=np.float64)
    if samples.ndim != 2 or samples.shape[1] != 2 or samples.shape[0] == 0:
        raise ValueError("DC correction requires non-empty stereo audio")
    if not np.isfinite(samples).all():
        raise ValueError("DC correction cannot process non-finite audio")
    offsets = np.mean(samples, axis=0, dtype=np.float64)
    corrected = np.asarray(samples - offsets, dtype=np.float32)
    after = np.mean(corrected.astype(np.float64), axis=0, dtype=np.float64)
    return corrected, {
        "method": "per-channel arithmetic mean subtraction",
        "channel_offsets_before": [float(value) for value in offsets],
        "channel_offsets_after": [float(value) for value in after],
        "dc_offset_before_dbfs": _dbfs(float(np.max(np.abs(offsets)))),
        "dc_offset_after_dbfs": _dbfs(float(np.max(np.abs(after)))),
        "reversible": True,
        "offset_units": "pre-gain sample values; add offsets multiplied by common_gain_linear to reconstruct pre-correction output",
    }


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
    soundfont_map: Mapping[str, str | Path] | None = None,
    soundfont_map_metadata: Mapping[str, Mapping[str, str]] | None = None,
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
    instrument_names = set(manifest.instruments)
    if soundfont_map is not None and not isinstance(soundfont_map, Mapping):
        raise TypeError("soundfont_map must map instrument names to SoundFont paths")
    if soundfont_map_metadata is not None and not isinstance(soundfont_map_metadata, Mapping):
        raise TypeError("soundfont_map_metadata must map instrument names to source/license metadata")
    supplied_map = dict(soundfont_map or {})
    supplied_metadata = dict(soundfont_map_metadata or {})
    unknown_map = set(supplied_map) - instrument_names
    unknown_metadata = set(supplied_metadata) - instrument_names
    if unknown_map:
        raise ValueError(f"SoundFont map contains unknown instruments: {sorted(unknown_map)}")
    if unknown_metadata:
        raise ValueError(f"SoundFont metadata contains unknown instruments: {sorted(unknown_metadata)}")
    soundfont_by_instrument = {
        name: Path(supplied_map.get(name, soundfont))
        for name in manifest.instruments
    }
    for asset_path in set(soundfont_by_instrument.values()):
        if not asset_path.is_file():
            raise FileNotFoundError(asset_path)
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
    soundfont_assets_by_instrument = {}
    for instrument_name, asset_path in soundfont_by_instrument.items():
        details = supplied_metadata.get(instrument_name, {})
        if not isinstance(details, Mapping) or set(details) - {"source", "license"}:
            raise ValueError(
                f"SoundFont metadata for {instrument_name!r} must contain only source/license."
            )
        source = details.get("source", soundfont_source if asset_path == soundfont else None)
        license_name = details.get("license", soundfont_license if asset_path == soundfont else None)
        if source is not None and (not isinstance(source, str) or not source.strip()):
            raise ValueError(f"SoundFont source for {instrument_name!r} must be non-empty text.")
        if license_name is not None and (not isinstance(license_name, str) or not license_name.strip()):
            raise ValueError(f"SoundFont license for {instrument_name!r} must be non-empty text.")
        asset_status = (
            "CALLER_SUPPLIED_UNVERIFIED"
            if source and license_name
            else "MISSING_SOURCE_OR_LICENSE_METADATA"
        )
        soundfont_assets_by_instrument[instrument_name] = {
            "instrument": instrument_name,
            "asset_name": asset_path.name,
            "sha256": _sha256_file(asset_path),
            "source": source,
            "license": license_name,
            "status": asset_status,
        }
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
        soundfont_path=soundfont_by_instrument,
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
                soundfont_path=soundfont_by_instrument,
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
                "soundfont_asset": soundfont_assets_by_instrument[instrument.name],
            }
        )

    raw_audio_arrays = [mix, *stem_arrays]
    audio_arrays = []
    dc_offset_corrections = []
    for audio in raw_audio_arrays:
        corrected, correction = _remove_dc_offset(audio)
        audio_arrays.append(corrected)
        dc_offset_corrections.append(correction)

    # Keep individual stems usable in mono. Preserve the mid signal exactly;
    # reduce only excessive side energy, and report cases that cannot be repaired.
    # Apply the same stem deltas to the full mix so its pre-existing reconstruction
    # residual is preserved rather than creating a new mix/stem mismatch.
    pre_compatibility_stems = [audio.copy() for audio in audio_arrays[1:]]
    stereo_compatibility_corrections = []
    for index, descriptor in enumerate(stem_descriptors, start=1):
        corrected, correction = _limit_stereo_side_for_mono_compatibility(
            audio_arrays[index],
            mono_fold_down_warning_db=-3.0,
        )
        audio_arrays[index] = corrected
        stereo_compatibility_corrections.append(correction)

    if any(item["applied"] for item in stereo_compatibility_corrections):
        adjusted_mix = np.asarray(audio_arrays[0], dtype=np.float64)
        for original, corrected in zip(pre_compatibility_stems, audio_arrays[1:]):
            adjusted_mix += (
                np.asarray(corrected, dtype=np.float64)
                - np.asarray(original, dtype=np.float64)
            )
        audio_arrays[0] = np.asarray(adjusted_mix, dtype=np.float32)

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
    rendered_stereo_integrity = [
        _measure_stereo_integrity(audio) for audio in rendered_arrays
    ]
    rendered_loudness = [
        _measure_loudness(audio, sample_rate) for audio in rendered_arrays
    ]

    rendered_mix = rendered_arrays[0]

    # Measure how closely independently rendered stems reconstruct the mix.
    # Separate FluidSynth passes can differ in shared effects, so this is a
    # diagnostic measurement, not a guarantee or a musical-quality score.
    stem_sum = np.zeros(rendered_mix.shape, dtype=np.float64)
    for stem_audio in rendered_arrays[1:]:
        stem_sum += stem_audio
    # Accumulate the mix in float64 too: np.vdot(float32, float32) otherwise
    # accumulates in float32 and can produce an impossible correlation > 1.
    mix_values = np.asarray(rendered_mix, dtype=np.float64)
    sample_count = stem_sum.size
    stem_sum_total = float(np.sum(stem_sum, dtype=np.float64))
    mix_total = float(np.sum(mix_values, dtype=np.float64))
    stem_sum_energy = float(np.vdot(stem_sum, stem_sum))
    mix_energy = float(np.vdot(mix_values, mix_values))
    cross_energy = float(np.vdot(stem_sum, mix_values))
    covariance = cross_energy - (stem_sum_total * mix_total / sample_count)
    stem_variance = max(0.0, stem_sum_energy - (stem_sum_total * stem_sum_total / sample_count))
    mix_variance = max(0.0, mix_energy - (mix_total * mix_total / sample_count))
    correlation_denominator = math.sqrt(stem_variance * mix_variance)
    stem_sum_correlation = (
        float(np.clip(covariance / correlation_denominator, -1.0, 1.0))
        if correlation_denominator > 0.0
        else None
    )
    stem_sum -= mix_values
    stem_sum_rms_error = math.sqrt(float(np.vdot(stem_sum, stem_sum)) / sample_count)
    mix_rms_for_reconstruction = math.sqrt(mix_energy / sample_count)
    stem_sum_reconstruction = {
        "measured": True,
        "guaranteed": False,
        "method": "float64 sum of independently rendered, sample-aligned WAV stems compared with the stereo mix",
        "rms_error": stem_sum_rms_error,
        "relative_rms_error": (
            stem_sum_rms_error / mix_rms_for_reconstruction
            if mix_rms_for_reconstruction > 0.0
            else 0.0
        ),
        "max_abs_error": float(np.max(np.abs(stem_sum))),
        "correlation": stem_sum_correlation,
    }

    _write_float32_wav(mix_path, rendered_mix, sample_rate, wavfile)
    stem_paths = []
    stem_metadata = []
    for descriptor, audio, levels, stereo_integrity, loudness_report, dc_correction, stereo_correction in zip(
        stem_descriptors,
        rendered_arrays[1:],
        rendered_levels[1:],
        rendered_stereo_integrity[1:],
        rendered_loudness[1:],
        dc_offset_corrections[1:],
        stereo_compatibility_corrections,
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
                "loudness": loudness_report,
                "clip_sample_count": int(np.count_nonzero(np.abs(audio) >= 1.0)),
                "stereo_integrity": stereo_integrity,
                "dc_offset_correction": dc_correction,
                "stereo_compatibility_correction": stereo_correction,
                "soundfont_sha256": descriptor["soundfont_asset"]["sha256"],
                "soundfont_source": descriptor["soundfont_asset"]["source"],
                "soundfont_license": descriptor["soundfont_asset"]["license"],
                "soundfont_rights_status": descriptor["soundfont_asset"]["status"],
            }
        )

    sample_peak, true_peak, rms = rendered_levels[0]
    midi_sha256 = _sha256_file(midi_path)
    mix_sha256 = _sha256_file(mix_path)
    soundfont_sha256 = _sha256_file(soundfont)
    rights_status = (
        "CALLER_SUPPLIED_UNVERIFIED"
        if all(
            item["status"] == "CALLER_SUPPLIED_UNVERIFIED"
            for item in soundfont_assets_by_instrument.values()
        )
        else "MISSING_SOURCE_OR_LICENSE_METADATA"
    )
    quality_warnings = {
        "mix": rendered_stereo_integrity[0]["warnings"],
        "stems": {
            item["instrument"]: item["stereo_integrity"]["warnings"]
            for item in stem_metadata
        },
    }
    quality_status = (
        "PASS"
        if not quality_warnings["mix"]
        and all(not warnings for warnings in quality_warnings["stems"].values())
        else "WARN"
    )
    metadata = {
        "schema_version": "1.0.0",
        "audio_quality_benchmark_version": AUDIO_QUALITY_BENCHMARK_VERSION,
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
        "quality_status": quality_status,
        "common_gain_linear": common_gain,
        "headroom_ceiling_dbfs": headroom_dbfs,
        "mix": {
            "path": "mix.wav",
            "sha256": mix_sha256,
            "peak_dbfs": _dbfs(sample_peak),
            "true_peak_dbtp": _dbfs(true_peak),
            "rms_dbfs": _dbfs(rms),
            "loudness": rendered_loudness[0],
            "clip_sample_count": int(np.count_nonzero(np.abs(rendered_mix) >= 1.0)),
            "stereo_integrity": rendered_stereo_integrity[0],
            "dc_offset_correction": dc_offset_corrections[0],
            "stereo_compatibility_correction": {
                "applied": any(item["applied"] for item in stereo_compatibility_corrections),
                "method": "apply each corrected stem delta to the full mix while preserving the pre-existing mix/stem residual",
                "instruments": [
                    descriptor["instrument"]
                    for descriptor, item in zip(stem_descriptors, stereo_compatibility_corrections)
                    if item["applied"]
                ],
            },
        },
        "dc_offset_correction": {
            "applied": True,
            "method": "per-channel arithmetic mean subtraction",
            "stage": "after rendering and before common headroom gain",
            "reversible": True,
            "offsets_are_pre_gain_sample_values": True,
            "mix": dc_offset_corrections[0],
            "stems": {
                descriptor["instrument"]: correction
                for descriptor, correction in zip(stem_descriptors, dc_offset_corrections[1:])
            },
        },
        "midi": {
            "path": "composition.mid",
            "sha256": midi_sha256,
            "track_names": [instrument.name for instrument in midi.instruments],
            "format": "Standard MIDI File",
        },
        "stems": stem_metadata,
        "stereo_compatibility_corrections": {
            descriptor["instrument"]: correction
            for descriptor, correction in zip(stem_descriptors, stereo_compatibility_corrections)
        },
        "stem_alignment": {
            "aligned": True,
            "sample_rate_hz": sample_rate,
            "channels": 2,
            "sample_count": int(rendered_mix.shape[0]),
            "timeline_origin_seconds": 0.0,
        },
        "stem_render_mode": (
            "One instrument per FluidSynth pass using the same instrument-to-SoundFont "
            "map as the mix, with a common gain and sample timeline."
        ),
        "stem_sum_reconstruction_guaranteed": False,
        "stem_sum_reconstruction": stem_sum_reconstruction,
        "stereo_integrity_thresholds": {
            "dc_offset_warning_dbfs": -60.0,
            "mono_fold_down_warning_db": -3.0,
        },
        "quality_warnings": quality_warnings,
        "rights": {
            "soundfont_source": soundfont_source,
            "soundfont_license": soundfont_license,
            "soundfont_sha256": soundfont_sha256,
            "soundfont_assets": list(soundfont_assets_by_instrument.values()),
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
