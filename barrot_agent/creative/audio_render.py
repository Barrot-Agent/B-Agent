"""Optional SoundFont-backed rendering of Barrot compositions to WAV.

Requires the optional music dependencies and a local FluidSynth shared library.
The SoundFont is supplied by the caller; no soundfont is bundled or downloaded.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import tempfile


from .midi_export import export_midi
from .musical_dna import MusicalManifest


@dataclass(frozen=True)
class AudioRenderResult:
    """Facts about a rendered WAV artifact; not an artistic-quality score."""

    path: Path
    sample_rate: int
    duration_seconds: float
    peak_level: float
    rms_level: float
    channels: int


def _headroom_gain(peak_level: float, ceiling_dbfs: float) -> float:
    """Return a non-boosting scalar gain that keeps sample peaks below a ceiling."""
    if not math.isfinite(peak_level) or peak_level < 0:
        raise ValueError("peak_level must be finite and non-negative")
    if not math.isfinite(ceiling_dbfs) or not -24.0 <= ceiling_dbfs <= 0.0:
        raise ValueError("headroom_dbfs must be between -24 and 0 dBFS")
    if peak_level == 0.0:
        return 1.0
    ceiling = 10.0 ** (ceiling_dbfs / 20.0)
    return min(1.0, ceiling / peak_level)


def render_audio(
    manifest: MusicalManifest,
    destination: str | Path,
    *,
    soundfont_path: str | Path,
    sample_rate: int = 44100,
    headroom_dbfs: float = -6.0,
) -> AudioRenderResult:
    """Render a manifest to a new WAV file using a caller-provided SF2 SoundFont.

    Existing destinations are never overwritten. If the sample peak exceeds the
    requested ceiling, the whole render receives one transparent scalar gain
    reduction; no hard clipping or dynamic-range compression is applied. The
    default leaves 6 dB of sample-peak headroom. True-peak oversampling and
    artistic-quality review remain separate QC steps.
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
    except ImportError as exc:
        raise RuntimeError(
            "WAV rendering requires the optional music dependencies: "
            "pip install -e '.[music]'"
        ) from exc

    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="barrot-render-") as temporary:
        midi_path = Path(temporary) / "composition.mid"
        export_midi(manifest, midi_path)
        try:
            midi = pretty_midi.PrettyMIDI(str(midi_path))
            samples = midi.fluidsynth(fs=sample_rate, sf2_path=str(soundfont))
        except Exception as exc:
            raise RuntimeError(
                "FluidSynth rendering failed. Install the FluidSynth system library, "
                "pyfluidsynth, and provide a compatible SF2 SoundFont."
            ) from exc

    audio = np.asarray(samples, dtype=np.float32)
    if audio.size == 0 or not np.isfinite(audio).all():
        raise ValueError("renderer returned empty or non-finite audio")
    source_peak = float(np.max(np.abs(audio)))
    gain = _headroom_gain(source_peak, headroom_dbfs)
    if gain < 1.0:
        audio = audio * gain
    peak = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(np.square(audio), dtype=np.float64)))
    channels = 1 if audio.ndim == 1 else int(audio.shape[1])
    duration = float(audio.shape[0] / sample_rate)

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
        rms_level=rms,
        channels=channels,
    )
