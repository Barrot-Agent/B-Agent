"""Optional stereo SoundFont rendering of Barrot compositions to WAV.

Requires the optional music dependencies and a local FluidSynth shared library.
The SoundFont is supplied by the caller; no soundfont is bundled or downloaded.
The renderer preserves separate MIDI channels and applies non-boosting sample-
and true-peak headroom. Its metrics are technical QC, not an artistic-quality score.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import math
from pathlib import Path
import tempfile


from .midi_export import export_midi
from .musical_dna import MusicalManifest


AUDIO_QUALITY_BENCHMARK_VERSION = "1.1.0"


@dataclass(frozen=True)
class AudioRenderResult:
    """Facts about a rendered WAV artifact; not an artistic-quality score."""

    path: Path
    sample_rate: int
    duration_seconds: float
    peak_level: float
    true_peak_level: float
    rms_level: float
    channels: int
    dc_offset_dbfs: float = -240.0
    stereo_correlation: float | None = None
    mono_fold_down_loss_db: float | None = None
    stereo_warnings: tuple[str, ...] = ()
    integrated_lufs: float | None = None
    loudness_range_lu: float | None = None
    crest_factor_db: float | None = None
    quality_benchmark_version: str = AUDIO_QUALITY_BENCHMARK_VERSION


def _headroom_gain(peak_level: float, ceiling_dbfs: float) -> float:
    """Return a non-boosting scalar gain that keeps peaks below a ceiling."""
    if not math.isfinite(peak_level) or peak_level < 0:
        raise ValueError("peak_level must be finite and non-negative")
    if not math.isfinite(ceiling_dbfs) or not -24.0 <= ceiling_dbfs <= 0.0:
        raise ValueError("headroom_dbfs must be between -24 and 0 dBFS")
    if peak_level == 0.0:
        return 1.0
    ceiling = 10.0 ** (ceiling_dbfs / 20.0)
    return min(1.0, ceiling / peak_level)


def _render_midi_stereo(
    midi,
    *,
    soundfont_path: str | Path | Mapping[str, str | Path],
    sample_rate: int,
    render_duration_seconds: float | None = None,
):
    """Render MIDI through one FluidSynth instance with optional per-track SF2s.

    A mapping selects a SoundFont by MIDI instrument name. Every distinct SF2 is
    loaded once into the same synth, so tracks retain a shared render timeline and
    shared FluidSynth effects. Pitched instruments receive independent channels;
    channel 10 (index 9) is reserved for General MIDI percussion.
    """
    try:
        import fluidsynth
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(
            "Stereo WAV rendering requires pyfluidsynth and the FluidSynth system library."
        ) from exc

    instruments = list(getattr(midi, "instruments", ()))
    if not any(getattr(instrument, "notes", ()) for instrument in instruments):
        return np.zeros((0, 2), dtype=np.float32)

    active_indices = {
        index
        for index, instrument in enumerate(instruments)
        if (
            getattr(instrument, "notes", ())
            or getattr(instrument, "pitch_bends", ())
            or getattr(instrument, "control_changes", ())
        )
    }
    if isinstance(soundfont_path, Mapping):
        soundfont_by_instrument: dict[int, Path] = {}
        for index in sorted(active_indices):
            name = getattr(instruments[index], "name", None)
            if not isinstance(name, str) or not name or name not in soundfont_path:
                raise ValueError(
                    f"No SoundFont mapping was supplied for MIDI instrument {name!r}."
                )
            soundfont_by_instrument[index] = Path(soundfont_path[name])
    else:
        default_soundfont = Path(soundfont_path)
        soundfont_by_instrument = {
            index: default_soundfont for index in active_indices
        }

    synth = fluidsynth.Synth(samplerate=sample_rate)
    try:
        soundfont_ids: dict[Path, int] = {}
        for soundfont in dict.fromkeys(soundfont_by_instrument.values()):
            soundfont_id = synth.sfload(str(soundfont))
            if soundfont_id < 0:
                raise RuntimeError(
                    f"FluidSynth could not load SoundFont {soundfont.name!r}."
                )
            soundfont_ids[soundfont] = soundfont_id

        channel_by_instrument: dict[int, int] = {}
        next_channel = 0
        drum_program: int | None = None

        for index, instrument in enumerate(instruments):
            if index not in active_indices:
                continue

            if instrument.is_drum:
                channel = 9
                if drum_program is None:
                    drum_program = int(instrument.program)
                elif drum_program != int(instrument.program):
                    raise ValueError(
                        "A single render supports one General MIDI drum-kit program."
                    )
                bank = 128
            else:
                if next_channel == 9:
                    next_channel += 1
                if next_channel > 15:
                    raise ValueError(
                        "FluidSynth render supports at most 15 simultaneous pitched instruments."
                    )
                channel = next_channel
                next_channel += 1
                bank = 0

            selected = synth.program_select(
                channel,
                soundfont_ids[soundfont_by_instrument[index]],
                bank,
                int(instrument.program),
            )
            if selected == -1:
                raise RuntimeError(
                    f"FluidSynth could not select bank {bank}, program {instrument.program}."
                )
            channel_by_instrument[index] = channel

        events = []
        for index, instrument in enumerate(instruments):
            channel = channel_by_instrument.get(index)
            if channel is None:
                continue
            for note in instrument.notes:
                start = max(0, int(round(float(note.start) * sample_rate)))
                end = max(start + 1, int(round(float(note.end) * sample_rate)))
                events.append(
                    (start, 2, index, channel, "note_on", int(note.pitch), int(note.velocity))
                )
                events.append(
                    (end, 0, index, channel, "note_off", int(note.pitch), 0)
                )
            for bend in getattr(instrument, "pitch_bends", ()):
                sample = max(0, int(round(float(bend.time) * sample_rate)))
                events.append(
                    (sample, 1, index, channel, "pitch_bend", int(bend.pitch), 0)
                )
            for control in getattr(instrument, "control_changes", ()):
                sample = max(0, int(round(float(control.time) * sample_rate)))
                events.append(
                    (
                        sample, 1, index, channel, "control_change",
                        int(control.number), int(control.value),
                    )
                )

        if not events:
            return np.zeros((0, 2), dtype=np.float32)

        events.sort(key=lambda event: (event[0], event[1], event[2], event[5]))
        end_time = float(midi.get_end_time())
        if render_duration_seconds is not None:
            if not math.isfinite(render_duration_seconds) or render_duration_seconds < 0:
                raise ValueError("render_duration_seconds must be finite and non-negative.")
            end_time = max(end_time, float(render_duration_seconds))
        if not math.isfinite(end_time) or end_time <= 0:
            raise ValueError("MIDI has no finite positive render duration.")
        total_samples = max(1, int(math.ceil(end_time * sample_rate)) + sample_rate)
        audio = np.zeros((total_samples, 2), dtype=np.float32)
        cursor = 0

        for sample, _, _, channel, event_type, value_a, value_b in events:
            sample = min(max(int(sample), cursor), total_samples)
            count = sample - cursor
            if count:
                block = np.asarray(synth.get_samples(count), dtype=np.float32)
                if block.size != count * 2:
                    raise RuntimeError(
                        f"FluidSynth returned {block.size} values for {count} stereo frames."
                    )
                audio[cursor:sample] += block.reshape(count, 2)
                cursor = sample

            if event_type == "note_on":
                synth.noteon(channel, value_a, value_b)
            elif event_type == "note_off":
                synth.noteoff(channel, value_a)
            elif event_type == "pitch_bend":
                synth.pitch_bend(channel, value_a)
            elif event_type == "control_change":
                synth.cc(channel, value_a, value_b)

        remaining = total_samples - cursor
        if remaining:
            block = np.asarray(synth.get_samples(remaining), dtype=np.float32)
            if block.size != remaining * 2:
                raise RuntimeError(
                    f"FluidSynth returned {block.size} values for {remaining} stereo frames."
                )
            audio[cursor:] += block.reshape(remaining, 2)

        return audio
    finally:
        synth.delete()


def _measure_audio_levels(audio, resample_poly, *, oversample: int = 4):
    """Measure sample peak, 4x oversampled true peak, and RMS in bounded chunks."""
    import numpy as np

    if audio.ndim != 2 or audio.shape[1] != 2:
        raise ValueError("audio must be a stereo frames-by-channels array")
    if audio.shape[0] == 0:
        raise ValueError("audio contains no samples")

    sample_peak = 0.0
    true_peak = 0.0
    square_sum = 0.0
    value_count = 0
    chunk_frames = 262144
    filter_overlap = 64

    for start in range(0, audio.shape[0], chunk_frames):
        end = min(audio.shape[0], start + chunk_frames)
        chunk = audio[start:end]
        sample_peak = max(sample_peak, float(np.max(np.abs(chunk))))
        square_sum += float(np.sum(np.square(chunk, dtype=np.float64)))
        value_count += int(chunk.size)

        left = max(0, start - filter_overlap)
        right = min(audio.shape[0], end + filter_overlap)
        segment = audio[left:right]
        oversampled = resample_poly(segment, oversample, 1, axis=0)
        local_start = (start - left) * oversample
        local_end = (end - left) * oversample
        core = oversampled[local_start:local_end]
        if core.size == 0:
            raise RuntimeError("True-peak resampler returned an empty analysis window.")
        true_peak = max(true_peak, float(np.max(np.abs(core))))

    rms = math.sqrt(square_sum / value_count) if value_count else 0.0
    return sample_peak, true_peak, rms


def _measure_loudness(audio, sample_rate: int) -> dict[str, object]:
    """Measure BS.1770 integrated loudness and EBU R128 LRA without processing audio."""
    import numpy as np
    import pyloudnorm as pyln
    from importlib.metadata import PackageNotFoundError, version

    samples = np.asarray(audio, dtype=np.float64)
    if samples.ndim == 1:
        samples = samples.reshape(-1, 1)
    if samples.ndim != 2 or samples.shape[0] == 0:
        raise ValueError("loudness measurement requires non-empty frames-by-channels audio")
    if sample_rate <= 0:
        raise ValueError("sample_rate must be positive")
    if not np.isfinite(samples).all():
        raise ValueError("loudness measurement cannot process non-finite audio")

    peak = float(np.max(np.abs(samples)))
    rms = math.sqrt(float(np.mean(np.square(samples), dtype=np.float64)))
    crest_factor_db = (
        20.0 * math.log10(max(peak, 1e-12) / max(rms, 1e-12))
        if rms > 0.0
        else None
    )
    try:
        library_version = version("pyloudnorm")
    except PackageNotFoundError:
        library_version = "unknown"

    report: dict[str, object] = {
        "standard": "ITU-R BS.1770-4",
        "loudness_range_standard": "EBU R128 LRA",
        "implementation": "pyloudnorm",
        "implementation_version": library_version,
        "sample_rate_hz": int(sample_rate),
        "duration_seconds": float(samples.shape[0] / sample_rate),
        "integrated_lufs": None,
        "loudness_range_lu": None,
        "loudness_range_status": "UNMEASURED",
        "crest_factor_db": crest_factor_db,
        "normalization_applied": False,
        "measurement_only": True,
    }
    if peak <= 1e-12 or rms <= 1e-12:
        report.update(
            status="SILENT",
            loudness_range_status="SILENT",
        )
        return report

    meter = pyln.Meter(sample_rate)
    try:
        integrated = float(meter.integrated_loudness(samples))
    except ValueError:
        integrated = float("nan")
    try:
        loudness_range = float(meter.loudness_range(samples))
    except (ValueError, ZeroDivisionError):
        loudness_range = float("nan")

    if math.isfinite(integrated):
        report["integrated_lufs"] = integrated
    if math.isfinite(loudness_range) and loudness_range >= 0.0:
        report["loudness_range_lu"] = loudness_range
        report["loudness_range_status"] = "MEASURED"
    else:
        report["loudness_range_status"] = "INSUFFICIENT_DURATION_OR_GATED"
    report["status"] = (
        "MEASURED" if report["integrated_lufs"] is not None else "INSUFFICIENT_DURATION"
    )
    return report


def _measure_stereo_integrity(
    audio,
    *,
    dc_offset_warning_dbfs: float = -60.0,
    mono_fold_down_warning_db: float = -3.0,
    chunk_frames: int = 262144,
) -> dict[str, object]:
    """Measure DC offset, inter-channel correlation, and mono fold-down loss.

    The calculation uses bounded float64 accumulators so long stereo renders do
    not require another full-size audio copy. Thresholds are warning indicators,
    not artistic-quality scores or automatic audio processing.
    """
    import numpy as np

    if audio.ndim != 2 or audio.shape[1] != 2:
        raise ValueError("audio must be a stereo frames-by-channels array")
    if audio.shape[0] == 0:
        raise ValueError("audio contains no samples")
    if chunk_frames <= 0:
        raise ValueError("chunk_frames must be positive")
    if not math.isfinite(dc_offset_warning_dbfs):
        raise ValueError("dc_offset_warning_dbfs must be finite")
    if not math.isfinite(mono_fold_down_warning_db):
        raise ValueError("mono_fold_down_warning_db must be finite")

    frame_count = int(audio.shape[0])
    channel_sum = np.zeros(2, dtype=np.float64)
    channel_square_sum = np.zeros(2, dtype=np.float64)
    cross_sum = 0.0

    for start in range(0, frame_count, chunk_frames):
        chunk = np.asarray(audio[start : start + chunk_frames], dtype=np.float64)
        if not np.isfinite(chunk).all():
            raise ValueError("audio contains non-finite samples")
        channel_sum += np.sum(chunk, axis=0, dtype=np.float64)
        channel_square_sum += np.sum(np.square(chunk), axis=0, dtype=np.float64)
        cross_sum += float(np.sum(chunk[:, 0] * chunk[:, 1], dtype=np.float64))

    means = channel_sum / frame_count
    variances = np.maximum(
        0.0,
        channel_square_sum - np.square(channel_sum) / frame_count,
    )
    covariance = cross_sum - (
        channel_sum[0] * channel_sum[1] / frame_count
    )
    denominator = math.sqrt(float(variances[0] * variances[1]))
    correlation = (
        float(np.clip(covariance / denominator, -1.0, 1.0))
        if denominator > 0.0
        else None
    )

    stereo_rms = math.sqrt(
        float(np.sum(channel_square_sum, dtype=np.float64))
        / (2.0 * frame_count)
    )
    mono_square_sum = (
        channel_square_sum[0]
        + channel_square_sum[1]
        + 2.0 * cross_sum
    ) / 4.0
    mono_rms = math.sqrt(max(0.0, mono_square_sum / frame_count))
    mono_loss_db = (
        20.0 * math.log10(max(mono_rms, 1e-12) / stereo_rms)
        if stereo_rms > 0.0
        else None
    )

    dc_offset = float(np.max(np.abs(means)))
    dc_offset_dbfs = 20.0 * math.log10(max(dc_offset, 1e-12))
    channel_dc_offset_dbfs = [
        20.0 * math.log10(max(abs(float(value)), 1e-12))
        for value in means
    ]
    warnings: list[str] = []
    if dc_offset_dbfs > dc_offset_warning_dbfs:
        warnings.append("dc_offset_above_threshold")
    if mono_loss_db is not None and mono_loss_db < mono_fold_down_warning_db:
        warnings.append("mono_fold_down_loss_below_threshold")
    if correlation is not None and correlation < 0.0:
        warnings.append("negative_stereo_correlation")

    return {
        "dc_offset_dbfs": dc_offset_dbfs,
        "channel_dc_offset_dbfs": channel_dc_offset_dbfs,
        "stereo_correlation": correlation,
        "stereo_rms_dbfs": 20.0 * math.log10(max(stereo_rms, 1e-12)),
        "mono_rms_dbfs": 20.0 * math.log10(max(mono_rms, 1e-12)),
        "mono_fold_down_loss_db": mono_loss_db,
        "dc_offset_warning": dc_offset_dbfs > dc_offset_warning_dbfs,
        "mono_compatibility_warning": (
            (mono_loss_db is not None and mono_loss_db < mono_fold_down_warning_db)
            or (correlation is not None and correlation < 0.0)
        ),
        "thresholds": {
            "dc_offset_warning_dbfs": dc_offset_warning_dbfs,
            "mono_fold_down_warning_db": mono_fold_down_warning_db,
        },
        "warnings": warnings,
        "status": "WARN" if warnings else "PASS",
    }


def _limit_stereo_side_for_mono_compatibility(
    audio,
    *,
    mono_fold_down_warning_db: float = -3.0,
    safety_margin: float = 0.05,
):
    """Reduce excessive side energy on one stem without changing its mono signal.

    The operation is deliberately conservative: it only narrows a stem when
    the measured mono fold-down or inter-channel correlation fails the supplied
    threshold. A near-null mid signal cannot be repaired without deleting the
    audible content, so that case is returned unchanged and explicitly flagged.
    """
    import numpy as np

    samples = np.asarray(audio, dtype=np.float32)
    if samples.ndim != 2 or samples.shape[1] != 2 or samples.shape[0] == 0:
        raise ValueError("mono-compatibility correction requires non-empty stereo audio")
    if not np.isfinite(samples).all():
        raise ValueError("mono-compatibility correction cannot process non-finite audio")
    if (
        not math.isfinite(mono_fold_down_warning_db)
        or not -12.0 <= mono_fold_down_warning_db < 0.0
    ):
        raise ValueError("mono_fold_down_warning_db must be between -12 and 0 dB")
    if not math.isfinite(safety_margin) or not 0.0 <= safety_margin < 0.1:
        raise ValueError("safety_margin must be between 0 and 0.1")

    before = _measure_stereo_integrity(
        samples,
        mono_fold_down_warning_db=mono_fold_down_warning_db,
    )
    report = {
        "applied": False,
        "side_gain": 1.0,
        "target_mono_fold_down_loss_db": mono_fold_down_warning_db,
        "before": before,
        "after": before,
        "status": "NOT_REQUIRED",
        "reason": None,
    }
    if not before["mono_compatibility_warning"]:
        return samples.copy(), report

    values = samples.astype(np.float64, copy=False)
    mid = (values[:, 0] + values[:, 1]) * 0.5
    side = (values[:, 0] - values[:, 1]) * 0.5
    mid_power = float(np.mean(np.square(mid), dtype=np.float64))
    side_power = float(np.mean(np.square(side), dtype=np.float64))
    if (
        not math.isfinite(mid_power)
        or not math.isfinite(side_power)
        or mid_power <= max(1e-20, side_power * 1e-12)
        or side_power <= 0.0
    ):
        report.update(
            status="UNRESOLVED",
            reason="mid_signal_too_weak_to_preserve_mono_content",
        )
        return samples.copy(), report

    mono_ratio = 10.0 ** (mono_fold_down_warning_db / 20.0)
    allowed_side_power = mid_power * (1.0 / (mono_ratio * mono_ratio) - 1.0)
    side_gain = min(
        1.0,
        math.sqrt(max(0.0, allowed_side_power) / side_power) * (1.0 - safety_margin),
    )
    if side_gain >= 1.0:
        return samples.copy(), report

    corrected = np.column_stack((mid + side * side_gain, mid - side * side_gain))
    corrected = np.asarray(corrected, dtype=np.float32)
    after = _measure_stereo_integrity(
        corrected,
        mono_fold_down_warning_db=mono_fold_down_warning_db,
    )
    report.update(
        applied=True,
        side_gain=side_gain,
        after=after,
        status="APPLIED" if not after["mono_compatibility_warning"] else "UNRESOLVED",
        reason=(
            "reduced_side_energy_to_preserve_mono_content"
            if not after["mono_compatibility_warning"]
            else "post_correction_mono_compatibility_still_below_threshold"
        ),
    )
    return corrected, report


def render_audio(
    manifest: MusicalManifest,
    destination: str | Path,
    *,
    soundfont_path: str | Path,
    sample_rate: int = 44100,
    headroom_dbfs: float = -6.0,
    program_map: Mapping[str, int] | None = None,
) -> AudioRenderResult:
    """Render a manifest to a new stereo WAV using a caller-provided SF2 SoundFont.

    Existing destinations are never overwritten. The requested ceiling is applied
    to both sample peak and 4x oversampled true peak using one non-boosting scalar
    gain. No hard clipping, limiting, or dynamic-range compression is applied.
    The default leaves at least 6 dB of sample-peak and true-peak headroom.
    """
    target = Path(destination)
    soundfont = Path(soundfont_path)
    if target.exists():
        raise FileExistsError(target)
    if not soundfont.is_file():
        raise FileNotFoundError(soundfont)
    if not 8000 <= sample_rate <= 192000:
        raise ValueError("sample_rate must be between 8000 and 192000")
    _headroom_gain(0.0, headroom_dbfs)

    try:
        import numpy as np
        import pretty_midi
        from scipy.io import wavfile
        from scipy.signal import resample_poly
    except ImportError as exc:
        raise RuntimeError(
            "WAV rendering requires the optional music dependencies: "
            "pip install -e '.[music]'"
        ) from exc

    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="barrot-render-") as temporary:
        midi_path = Path(temporary) / "composition.mid"
        export_midi(manifest, midi_path, program_map=program_map)
        try:
            midi = pretty_midi.PrettyMIDI(str(midi_path))
            audio = _render_midi_stereo(
                midi, soundfont_path=soundfont, sample_rate=sample_rate
            )
        except Exception as exc:
            raise RuntimeError(
                "FluidSynth stereo rendering failed. Install the FluidSynth system "
                "library, pyfluidsynth, and provide a compatible SF2 SoundFont."
            ) from exc

    audio = np.asarray(audio, dtype=np.float32)
    if audio.size == 0 or not np.isfinite(audio).all():
        raise ValueError("renderer returned empty or non-finite audio")
    sample_peak, source_true_peak, source_rms = _measure_audio_levels(
        audio, resample_poly, oversample=4
    )
    if sample_peak <= 0.0 and source_true_peak <= 0.0:
        raise ValueError("renderer returned silent audio")

    gain = _headroom_gain(max(sample_peak, source_true_peak), headroom_dbfs)
    if gain < 1.0:
        audio = audio * gain
    peak = sample_peak * gain
    true_peak = source_true_peak * gain
    rms = source_rms * gain
    duration = float(audio.shape[0] / sample_rate)
    stereo_integrity = _measure_stereo_integrity(audio)
    loudness_report = _measure_loudness(audio, sample_rate)

    created = False
    try:
        with target.open("xb") as output:
            created = True
            wavfile.write(output, sample_rate, audio)
    except Exception:
        if created:
            target.unlink(missing_ok=True)
        raise

    return AudioRenderResult(
        path=target,
        sample_rate=sample_rate,
        duration_seconds=duration,
        peak_level=peak,
        true_peak_level=true_peak,
        rms_level=rms,
        channels=2,
        dc_offset_dbfs=float(stereo_integrity["dc_offset_dbfs"]),
        stereo_correlation=stereo_integrity["stereo_correlation"],
        mono_fold_down_loss_db=stereo_integrity["mono_fold_down_loss_db"],
        stereo_warnings=tuple(stereo_integrity["warnings"]),
        integrated_lufs=loudness_report["integrated_lufs"],
        loudness_range_lu=loudness_report["loudness_range_lu"],
        crest_factor_db=loudness_report["crest_factor_db"],
    )
