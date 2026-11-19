"""Optional SoundFont-backed rendering of Barrot compositions to WAV.

Requires the optional music dependencies and a local FluidSynth shared library.
The SoundFont is supplied by the caller; no soundfont is bundled or downloaded.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tempfile

import numpy as np

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


def render_audio(
    manifest: MusicalManifest,
    destination: str | Path,
    *,
    soundfont_path: str | Path,
    sample_rate: int = 44100,
) -> AudioRenderResult:
    """Render a manifest to a new WAV file using a caller-provided SF2 SoundFont.

    Existing destinations are never overwritten. The returned measurements are
    technical diagnostics only; they do not assess musicality or replace listening.
    """
    target = Path(destination)
    soundfont = Path(soundfont_path)
    if target.exists():
        raise FileExistsError(target)
    if not soundfont.is_file():
        raise FileNotFoundError(soundfont)
    if not 8000 <= sample_rate <= 192000:
        raise ValueError("sample_rate must be between 8000 and 192000")

    try:
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
    audio = np.clip(audio, -1.0, 1.0)
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
