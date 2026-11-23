"""Real FluidSynth integration test; the CI SoundFont is test-only GPL-2."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("scipy")
pytest.importorskip("pretty_midi")
from scipy.io import wavfile
from scipy.signal import resample_poly

from barrot_agent.creative.audio_render import render_audio
from barrot_agent.creative.composer import CompositionSettings, compose_original
from barrot_agent.creative.musical_dna import MusicalEvent, MusicalManifest


def _template() -> MusicalManifest:
    return MusicalManifest(
        bpm=110,
        beats_per_bar=4,
        scale="D minor",
        instruments=("kick", "snare", "bass", "keys"),
        events=(MusicalEvent("kick", "pulse", 0.0, 0.25),),
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def test_real_fluidsynth_render_is_stereo_reproducible_and_headroom_safe(tmp_path):
    soundfont_value = os.environ.get("BARROT_TEST_SF2")
    if not soundfont_value:
        pytest.skip("BARROT_TEST_SF2 is not configured outside the dedicated CI job")

    soundfont = Path(soundfont_value)
    license_name = os.environ.get("BARROT_TEST_SF2_LICENSE", "")
    source_name = os.environ.get("BARROT_TEST_SF2_SOURCE", "")
    assert soundfont.is_file()
    assert license_name.startswith("GPL-2")
    assert "timgm6mb-soundfont" in source_name.lower()

    manifest = compose_original(
        _template(), CompositionSettings(bars=16, seed=20261123)
    )
    first_path = tmp_path / "barrot-render-a.wav"
    second_path = tmp_path / "barrot-render-b.wav"
    first = render_audio(manifest, first_path, soundfont_path=soundfont)
    second = render_audio(manifest, second_path, soundfont_path=soundfont)

    sample_rate, samples = wavfile.read(first_path)
    repeat_rate, repeat_samples = wavfile.read(second_path)
    assert sample_rate == repeat_rate == 44100
    assert samples.dtype == np.float32
    assert samples.ndim == 2 and samples.shape[1] == 2
    assert repeat_samples.shape == samples.shape
    assert _sha256(first_path) == _sha256(second_path)
    assert np.isfinite(samples).all()

    sample_peak = float(np.max(np.abs(samples)))
    oversampled = resample_poly(samples, 4, 1, axis=0)
    true_peak = float(np.max(np.abs(oversampled)))
    rms = float(np.sqrt(np.mean(np.square(samples, dtype=np.float64))))
    ceiling = 10 ** (-6.0 / 20.0)

    assert first.channels == second.channels == 2
    assert first.duration_seconds > 30.0
    assert first.peak_level <= ceiling + 1e-4
    assert first.true_peak_level <= ceiling + 1e-4
    assert abs(first.peak_level - sample_peak) <= 1e-4
    assert abs(first.true_peak_level - true_peak) <= 2e-3
    assert abs(first.rms_level - rms) <= 1e-5
    assert sample_peak > 0.001 and rms > 0.001
    assert int(np.count_nonzero(np.abs(samples) >= 1.0)) == 0

    sf2_hash = _sha256(soundfont)
    qc = {
        "status": "VERIFIED",
        "renderer": "FluidSynth via pyfluidsynth",
        "pyfluidsynth_version": importlib.metadata.version("pyfluidsynth"),
        "soundfont_source": source_name,
        "soundfont_license": license_name,
        "soundfont_sha256": sf2_hash,
        "render_sha256": _sha256(first_path),
        "sample_rate_hz": sample_rate,
        "channels": int(samples.shape[1]),
        "duration_seconds": first.duration_seconds,
        "peak_dbfs": 20.0 * math.log10(max(sample_peak, 1e-12)),
        "true_peak_dbtp": 20.0 * math.log10(max(true_peak, 1e-12)),
        "rms_dbfs": 20.0 * math.log10(max(rms, 1e-12)),
        "clip_sample_count": 0,
        "bars": 16,
        "bpm": manifest.bpm,
        "key": manifest.scale,
        "time_signature": "4/4",
        "seed": 20261123,
        "distribution": "QC JSON only; GPL-2 SoundFont and rendered WAV are not uploaded",
    }
    qc_output = os.environ.get("BARROT_AUDIO_QC_OUTPUT")
    if qc_output:
        Path(qc_output).write_text(json.dumps(qc, indent=2, sort_keys=True) + "\n")
    print(json.dumps(qc, indent=2, sort_keys=True))


def test_real_fluidsynth_bundle_exports_reproducible_aligned_stems_and_midi(tmp_path):
    from barrot_agent.creative.audio_bundle import render_production_bundle
    import pretty_midi

    soundfont_value = os.environ.get("BARROT_TEST_SF2")
    if not soundfont_value:
        pytest.skip("BARROT_TEST_SF2 is not configured outside the dedicated CI job")

    soundfont = Path(soundfont_value)
    license_name = os.environ.get("BARROT_TEST_SF2_LICENSE", "")
    source_name = os.environ.get("BARROT_TEST_SF2_SOURCE", "")
    assert soundfont.is_file()
    assert license_name.startswith("GPL-2")
    assert "timgm6mb-soundfont" in source_name.lower()

    manifest = compose_original(
        _template(), CompositionSettings(bars=16, seed=20261123)
    )
    first = render_production_bundle(
        manifest,
        tmp_path / "bundle-a",
        soundfont_path=soundfont,
        soundfont_source=source_name,
        soundfont_license=license_name,
    )
    second = render_production_bundle(
        manifest,
        tmp_path / "bundle-b",
        soundfont_path=soundfont,
        soundfont_source=source_name,
        soundfont_license=license_name,
    )

    sample_rate, mix_samples = wavfile.read(first.mix_path)
    repeat_rate, repeat_mix = wavfile.read(second.mix_path)
    assert sample_rate == repeat_rate == 44100
    assert mix_samples.dtype == np.float32
    assert mix_samples.ndim == 2 and mix_samples.shape[1] == 2
    assert repeat_mix.shape == mix_samples.shape
    assert _sha256(first.mix_path) == _sha256(second.mix_path)
    assert _sha256(first.midi_path) == _sha256(second.midi_path)
    assert [ _sha256(path) for path in first.stems ] == [
        _sha256(path) for path in second.stems
    ]

    ceiling = 10 ** (-6.0 / 20.0)
    mix_peak = float(np.max(np.abs(mix_samples)))
    mix_true_peak = float(np.max(resample_poly(mix_samples, 4, 1, axis=0)))
    assert first.channels == 2
    assert first.duration_seconds > 30.0
    assert first.peak_level <= ceiling + 1e-4
    assert first.true_peak_level <= ceiling + 1e-4
    assert abs(first.peak_level - mix_peak) <= 1e-4
    assert abs(first.true_peak_level - mix_true_peak) <= 2e-3
    assert int(np.count_nonzero(np.abs(mix_samples) >= 1.0)) == 0

    midi = pretty_midi.PrettyMIDI(str(first.midi_path))
    assert [instrument.name for instrument in midi.instruments] == list(manifest.instruments)
    assert len(first.stems) == len(manifest.instruments)
    for stem_path in first.stems:
        stem_rate, stem_samples = wavfile.read(stem_path)
        assert stem_rate == sample_rate
        assert stem_samples.dtype == np.float32
        assert stem_samples.shape == mix_samples.shape
        assert np.isfinite(stem_samples).all()
        assert float(np.max(np.abs(stem_samples))) <= ceiling + 1e-4
        assert float(np.max(resample_poly(stem_samples, 4, 1, axis=0))) <= ceiling + 2e-3
        assert int(np.count_nonzero(np.abs(stem_samples) >= 1.0)) == 0

    metadata = json.loads(first.metadata_path.read_text(encoding="utf-8"))
    assert metadata["artifact_type"] == "barrot.audio.production_bundle"
    assert metadata["bpm"] == manifest.bpm
    assert metadata["key"] == manifest.scale
    assert metadata["time_signature"] == "4/4"
    assert metadata["stem_alignment"]["aligned"] is True
    assert metadata["stem_alignment"]["sample_count"] == mix_samples.shape[0]
    assert metadata["native_daw_project_available"] is False
    assert metadata["rights"]["status"] == "CALLER_SUPPLIED_UNVERIFIED"
    assert metadata["rights"]["soundfont_sha256"] == _sha256(soundfont)
    assert metadata["mix"]["sha256"] == _sha256(first.mix_path)
    assert metadata["midi"]["sha256"] == _sha256(first.midi_path)
    assert all(stem["clip_sample_count"] == 0 for stem in metadata["stems"])

    qc = {
        "status": "VERIFIED_TECHNICAL_BUNDLE",
        "render_engine": "FluidSynth via pyfluidsynth",
        "mix_sha256": _sha256(first.mix_path),
        "midi_sha256": _sha256(first.midi_path),
        "stem_sha256s": [_sha256(path) for path in first.stems],
        "metadata_sha256": _sha256(first.metadata_path),
        "soundfont_sha256": _sha256(soundfont),
        "soundfont_source": source_name,
        "soundfont_license": license_name,
        "sample_rate_hz": sample_rate,
        "channels": 2,
        "duration_seconds": first.duration_seconds,
        "stem_count": len(first.stems),
        "sample_count": int(mix_samples.shape[0]),
        "peak_dbfs": 20.0 * math.log10(max(mix_peak, 1e-12)),
        "true_peak_dbtp": 20.0 * math.log10(max(mix_true_peak, 1e-12)),
        "clip_sample_count": 0,
        "stem_alignment": "all WAV stems share the mix sample rate, frame count, and timeline origin",
        "daw_interchange": "Standard MIDI File + aligned WAV stems + JSON metadata; not a native DAW project",
        "rights_metadata_status": metadata["rights"]["status"],
        "distribution": "QC JSON only; GPL-2 SoundFont, WAV mix, stems, and MIDI are not uploaded",
    }
    qc_output = os.environ.get("BARROT_AUDIO_BUNDLE_QC_OUTPUT")
    if qc_output:
        Path(qc_output).write_text(json.dumps(qc, indent=2, sort_keys=True) + "\n")
    print(json.dumps(qc, indent=2, sort_keys=True))
