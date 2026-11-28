from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

import pytest

from barrot_agent.creative.musical_dna import (
    MusicalEvent,
    MusicalManifest,
    MusicalSection,
)


def _manifest(instruments: tuple[str, ...] = ("keys", "pad")) -> MusicalManifest:
    events = tuple(
        MusicalEvent(name, "harmony", 0.0, 1.0, 90, 60)
        for name in instruments
    )
    return MusicalManifest(
        bpm=120.0,
        beats_per_bar=4,
        scale="C minor",
        instruments=instruments,
        events=events,
        sections=(
            MusicalSection("intro", 1, 1, 0.25),
            MusicalSection("verse", 2, 1, 0.5),
        ),
        provenance="audio_production_quality_gate_test",
    )


def _fake_bundle_modules() -> dict[str, ModuleType]:
    np = pytest.importorskip("numpy")
    pretty_midi = ModuleType("pretty_midi")

    class FakeInstrument:
        def __init__(self, name: str, notes: list[object]) -> None:
            self.name = name
            self.notes = notes
            self.program = {"keys": 4, "pad": 89}.get(name, 0)

    class FakeMidi:
        def __init__(
            self,
            path: str | None = None,
            *,
            initial_tempo: float | None = None,
            resolution: int = 220,
        ) -> None:
            self.resolution = resolution
            self.instruments = (
                [
                    FakeInstrument("keys", [object()]),
                    FakeInstrument("pad", []),
                ]
                if isinstance(path, str)
                else []
            )

        def get_end_time(self) -> float:
            return 1.0

    pretty_midi.PrettyMIDI = FakeMidi

    scipy = ModuleType("scipy")
    scipy.__path__ = []
    scipy_io = ModuleType("scipy.io")
    scipy_io.__path__ = []
    scipy_signal = ModuleType("scipy.signal")
    wavfile = ModuleType("scipy.io.wavfile")

    def write(handle, sample_rate: int, samples) -> None:
        array = np.asarray(samples, dtype=np.float32)
        handle.write(b"RIFF")
        handle.write(int(sample_rate).to_bytes(4, "little"))
        handle.write(array.tobytes())

    wavfile.write = write
    scipy_io.wavfile = wavfile
    scipy_signal.resample_poly = lambda samples, up, down, axis=0: samples
    scipy.io = scipy_io
    scipy.signal = scipy_signal

    return {
        "pretty_midi": pretty_midi,
        "scipy": scipy,
        "scipy.io": scipy_io,
        "scipy.io.wavfile": wavfile,
        "scipy.signal": scipy_signal,
    }


def _fake_loudness_report(audio, sample_rate: int) -> dict[str, object]:
    return {
        "standard": "ITU-R BS.1770-4",
        "loudness_range_standard": "EBU R128 LRA",
        "implementation": "pyloudnorm",
        "implementation_version": "0.2.0",
        "sample_rate_hz": int(sample_rate),
        "duration_seconds": float(len(audio) / sample_rate),
        "integrated_lufs": -20.0,
        "loudness_range_lu": 4.0,
        "loudness_range_status": "MEASURED",
        "crest_factor_db": 3.0,
        "normalization_applied": False,
        "measurement_only": True,
        "status": "MEASURED",
    }


def _fake_librosa(
    signal: np.ndarray,
    *,
    onsets: tuple[int, ...] = (0, 1, 2),
    tempo: float | np.ndarray = 120.0,
) -> ModuleType:
    np = pytest.importorskip("numpy")
    librosa = ModuleType("librosa")
    librosa.load = lambda *args, **kwargs: (signal, 8000)
    librosa.beat = SimpleNamespace(
        beat_track=lambda **kwargs: (tempo, np.asarray([0], dtype=int))
    )
    librosa.onset = SimpleNamespace(
        onset_detect=lambda **kwargs: np.asarray(onsets, dtype=int)
    )
    librosa.frames_to_time = lambda frames, sr: (
        np.asarray(frames, dtype=float) * (512.0 / float(sr))
    )
    librosa.feature = SimpleNamespace(
        rms=lambda y: np.asarray([[0.1, 0.2, 0.3]], dtype=float),
        chroma_stft=lambda y, sr: np.ones((12, 3), dtype=float),
    )
    return librosa


def test_bundle_exports_mix_aligned_stems_midi_and_rights_metadata(
    tmp_path: Path,
) -> None:
    np = pytest.importorskip("numpy")
    from barrot_agent.creative.audio_bundle import render_production_bundle

    soundfont = tmp_path / "caller-supplied.sf2"
    soundfont.write_bytes(b"test-soundfont")
    target = tmp_path / "deliverables" / "bundle"
    sample_rate = 8000
    frames = sample_rate * 4
    mix = np.tile(
        np.asarray([[0.95, -0.95], [-0.65, 0.65]], dtype=np.float32),
        (frames // 2, 1),
    )
    keys = np.tile(
        np.asarray([[0.75, -0.75], [-0.25, 0.25]], dtype=np.float32),
        (frames // 2, 1),
    )
    render_calls: list[dict] = []

    def render(midi, **kwargs):
        render_calls.append(kwargs)
        if len(render_calls) == 1:
            return mix.copy()
        assert midi.instruments[0].name == "keys"
        return keys.copy()

    def measure(audio, _resample_poly, *, oversample):
        assert oversample == 4
        values = np.asarray(audio, dtype=np.float64)
        peak = float(np.max(np.abs(values)))
        rms = float(np.sqrt(np.mean(np.square(values))))
        return peak, peak * 1.05, rms

    def export(manifest, path: Path, *, program_map=None) -> None:
        Path(path).write_bytes(b"named-midi-tracks")

    with (
        patch.dict(sys.modules, _fake_bundle_modules()),
        patch("barrot_agent.creative.audio_bundle.export_midi", side_effect=export),
        patch("barrot_agent.creative.audio_bundle._render_midi_stereo", side_effect=render),
        patch("barrot_agent.creative.audio_bundle._measure_audio_levels", side_effect=measure),
        patch("barrot_agent.creative.audio_bundle._measure_loudness", side_effect=_fake_loudness_report),
    ):
        result = render_production_bundle(
            _manifest(),
            target,
            soundfont_path=soundfont,
            sample_rate=sample_rate,
            headroom_dbfs=-6.0,
            soundfont_source="caller supplied test fixture",
            soundfont_license="caller supplied; not independently verified",
        )

    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    ceiling = 10 ** (-6.0 / 20.0)

    assert result.mix_path.is_file()
    assert result.midi_path.read_bytes() == b"named-midi-tracks"
    assert len(result.stems) == 2
    assert all(path.is_file() for path in result.stems)
    assert all(path.read_bytes().startswith(b"RIFF") for path in (result.mix_path, *result.stems))
    assert result.sample_rate == sample_rate
    assert result.channels == 2
    assert result.duration_seconds == pytest.approx(4.0)
    assert result.true_peak_level <= ceiling + 1e-6
    assert result.peak_level <= ceiling + 1e-6
    assert metadata["stem_alignment"]["aligned"] is True
    assert metadata["stem_alignment"]["sample_count"] == frames
    assert metadata["dc_offset_correction"]["applied"] is True
    assert metadata["dc_offset_correction"]["reversible"] is True
    assert metadata["mix"]["stereo_integrity"]["dc_offset_dbfs"] < -60.0
    assert metadata["audio_quality_benchmark_version"] == "1.1.0"
    assert metadata["mix"]["loudness"]["integrated_lufs"] == -20.0
    assert metadata["mix"]["loudness"]["normalization_applied"] is False
    assert all(stem["loudness"]["integrated_lufs"] == -20.0 for stem in metadata["stems"])
    assert all(stem["stereo_integrity"]["dc_offset_dbfs"] < -60.0 for stem in metadata["stems"])
    assert [stem["instrument"] for stem in metadata["stems"]] == ["keys", "pad"]
    assert all(stem["sample_count"] == frames for stem in metadata["stems"])
    assert metadata["common_gain_linear"] < 1.0
    assert metadata["rights"]["status"] == "CALLER_SUPPLIED_UNVERIFIED"
    assert metadata["rights"]["soundfont_sha256"] == hashlib.sha256(soundfont.read_bytes()).hexdigest()
    assert metadata["native_daw_project_available"] is False
    assert metadata["stem_sum_reconstruction_guaranteed"] is False
    reconstruction = metadata["stem_sum_reconstruction"]
    assert reconstruction["measured"] is True
    assert reconstruction["guaranteed"] is False
    assert reconstruction["relative_rms_error"] >= 0.0
    assert reconstruction["max_abs_error"] >= 0.0
    assert reconstruction["correlation"] is None or -1.0 <= reconstruction["correlation"] <= 1.0
    assert metadata["midi"]["track_names"] == ["keys", "pad"]
    assert len(render_calls) == 2
    assert all(call["render_duration_seconds"] == pytest.approx(4.0) for call in render_calls)


def test_bundle_requires_explicit_rights_metadata_to_claim_any_status(tmp_path: Path) -> None:
    np = pytest.importorskip("numpy")
    from barrot_agent.creative.audio_bundle import render_production_bundle

    soundfont = tmp_path / "fixture.sf2"
    soundfont.write_bytes(b"fixture")
    target = tmp_path / "bundle"

    def render(midi, **kwargs):
        return np.zeros((4, 2), dtype=np.float32)

    with (
        patch.dict(sys.modules, _fake_bundle_modules()),
        patch("barrot_agent.creative.audio_bundle.export_midi", side_effect=lambda m, p, *, program_map=None: Path(p).write_bytes(b"midi")),
        patch("barrot_agent.creative.audio_bundle._render_midi_stereo", side_effect=render),
        patch("barrot_agent.creative.audio_bundle._measure_audio_levels", return_value=(0.0, 0.0, 0.0)),
        patch("barrot_agent.creative.audio_bundle._measure_loudness", side_effect=_fake_loudness_report),
    ):
        result = render_production_bundle(_manifest(), target, soundfont_path=soundfont)

    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    assert metadata["rights"]["status"] == "MISSING_SOURCE_OR_LICENSE_METADATA"
    assert metadata["rights"]["soundfont_source"] is None
    assert metadata["rights"]["soundfont_license"] is None


def test_bundle_refuses_existing_directory_without_modifying_user_file(tmp_path: Path) -> None:
    from barrot_agent.creative.audio_bundle import render_production_bundle

    target = tmp_path / "existing"
    target.mkdir()
    preserved = target / "user.wav"
    preserved.write_bytes(b"user-owned audio")

    with pytest.raises(FileExistsError):
        render_production_bundle(
            _manifest(),
            target,
            soundfont_path=tmp_path / "missing.sf2",
        )

    assert preserved.read_bytes() == b"user-owned audio"


def test_bundle_rejects_missing_soundfont_and_invalid_configuration_before_output(
    tmp_path: Path,
) -> None:
    from barrot_agent.creative.audio_bundle import render_production_bundle

    soundfont = tmp_path / "fixture.sf2"
    soundfont.write_bytes(b"fixture")

    with pytest.raises(FileNotFoundError):
        render_production_bundle(
            _manifest(), tmp_path / "missing", soundfont_path=tmp_path / "absent.sf2"
        )
    with pytest.raises(ValueError, match="sample_rate"):
        render_production_bundle(
            _manifest(), tmp_path / "bad-rate", soundfont_path=soundfont, sample_rate=100
        )
    with pytest.raises(ValueError, match="unique"):
        render_production_bundle(
            _manifest(("keys", "keys")),
            tmp_path / "duplicate",
            soundfont_path=soundfont,
        )
    with pytest.raises(ValueError):
        render_production_bundle(
            _manifest(),
            tmp_path / "bad-headroom",
            soundfont_path=soundfont,
            headroom_dbfs=1.0,
        )
    with pytest.raises(ValueError, match="unknown instruments"):
        render_production_bundle(
            _manifest(),
            tmp_path / "bad-program-name",
            soundfont_path=soundfont,
            program_map={"not-a-track": 0},
        )
    with pytest.raises(ValueError, match="0 to 127"):
        render_production_bundle(
            _manifest(),
            tmp_path / "bad-program-number",
            soundfont_path=soundfont,
            program_map={"keys": 128},
        )
    assert not (tmp_path / "missing").exists()
    assert not (tmp_path / "bad-rate").exists()
    assert not (tmp_path / "duplicate").exists()
    assert not (tmp_path / "bad-headroom").exists()
    assert not (tmp_path / "bad-program-name").exists()
    assert not (tmp_path / "bad-program-number").exists()


def test_bundle_reports_missing_optional_music_dependencies(tmp_path: Path) -> None:
    from barrot_agent.creative.audio_bundle import render_production_bundle

    soundfont = tmp_path / "fixture.sf2"
    soundfont.write_bytes(b"fixture")
    with patch.dict(sys.modules, {"pretty_midi": None}):
        with pytest.raises(RuntimeError, match="optional music dependencies"):
            render_production_bundle(
                _manifest(), tmp_path / "bundle", soundfont_path=soundfont
            )
    assert not (tmp_path / "bundle").exists()


def test_bundle_rejects_invalid_mix_and_sample_misaligned_stem(tmp_path: Path) -> None:
    np = pytest.importorskip("numpy")
    from barrot_agent.creative.audio_bundle import render_production_bundle

    soundfont = tmp_path / "fixture.sf2"
    soundfont.write_bytes(b"fixture")

    with (
        patch.dict(sys.modules, _fake_bundle_modules()),
        patch("barrot_agent.creative.audio_bundle.export_midi", side_effect=lambda m, p: Path(p).write_bytes(b"midi")),
        patch("barrot_agent.creative.audio_bundle._render_midi_stereo", return_value=np.zeros((4, 1), dtype=np.float32)),
    ):
        with pytest.raises(ValueError, match="invalid stereo mix"):
            render_production_bundle(
                _manifest(), tmp_path / "invalid-mix", soundfont_path=soundfont
            )

    calls = 0

    def misaligned(midi, **kwargs):
        nonlocal calls
        calls += 1
        return np.zeros((4 if calls == 1 else 3, 2), dtype=np.float32)

    with (
        patch.dict(sys.modules, _fake_bundle_modules()),
        patch("barrot_agent.creative.audio_bundle.export_midi", side_effect=lambda m, p: Path(p).write_bytes(b"midi")),
        patch("barrot_agent.creative.audio_bundle._render_midi_stereo", side_effect=misaligned),
    ):
        with pytest.raises(RuntimeError, match="not sample-aligned"):
            render_production_bundle(
                _manifest(), tmp_path / "misaligned", soundfont_path=soundfont
            )


def test_bundle_keeps_new_partial_directory_for_failure_inspection(tmp_path: Path) -> None:
    from barrot_agent.creative.audio_bundle import render_production_bundle

    soundfont = tmp_path / "fixture.sf2"
    soundfont.write_bytes(b"fixture")
    target = tmp_path / "partial"

    with (
        patch.dict(sys.modules, _fake_bundle_modules()),
        patch("barrot_agent.creative.audio_bundle.export_midi", side_effect=lambda m, p: Path(p).write_bytes(b"midi")),
        patch("barrot_agent.creative.audio_bundle._render_midi_stereo", side_effect=RuntimeError("render failed")),
    ):
        with pytest.raises(RuntimeError, match="render failed"):
            render_production_bundle(
                _manifest(), target, soundfont_path=soundfont
            )

    assert (target / "stems").is_dir()
    assert (target / "composition.mid").read_bytes() == b"midi"


def test_float32_wav_writer_rejects_mono_and_non_finite_audio(tmp_path: Path) -> None:
    np = pytest.importorskip("numpy")
    from barrot_agent.creative.audio_bundle import _write_float32_wav

    writer = SimpleNamespace(write=lambda *args: None)
    with pytest.raises(ValueError, match="stereo"):
        _write_float32_wav(tmp_path / "mono.wav", np.zeros((4, 1)), 8000, writer)
    with pytest.raises(ValueError, match="non-finite"):
        _write_float32_wav(
            tmp_path / "nan.wav",
            np.asarray([[np.nan, 0.0]], dtype=np.float32),
            8000,
            writer,
        )
    assert not (tmp_path / "mono.wav").exists()
    assert not (tmp_path / "nan.wav").exists()


def test_audio_adapter_extracts_timing_dynamics_scale_and_section_map(tmp_path: Path) -> None:
    np = pytest.importorskip("numpy")
    from barrot_agent.creative.audio_adapter import analyze_audio

    source = tmp_path / "source.wav"
    source.write_bytes(b"source")
    signal = np.ones(8000, dtype=np.float32)
    with patch.dict(sys.modules, {"librosa": _fake_librosa(signal)}):
        manifest = analyze_audio(source, instrument_label="reference_audio")

    assert manifest.provenance == "audio_abstract_features_only"
    assert manifest.instruments == ("reference_audio",)
    assert len(manifest.events) == 3
    assert all(event.role == "transient" for event in manifest.events)
    assert [event.beat for event in manifest.events] == sorted(
        event.beat for event in manifest.events
    )
    assert all(1 <= event.velocity <= 127 for event in manifest.events)
    assert manifest.sections[0].start_bar == 1
    assert manifest.sections[0].bars == 1
    assert manifest.scale.endswith(("major", "minor"))


def test_audio_adapter_uses_sustain_fallback_and_default_tempo(tmp_path: Path) -> None:
    np = pytest.importorskip("numpy")
    from barrot_agent.creative.audio_adapter import analyze_audio

    source = tmp_path / "sustain.wav"
    source.write_bytes(b"source")
    signal = np.ones(8000, dtype=np.float32)
    with patch.dict(
        sys.modules,
        {"librosa": _fake_librosa(signal, onsets=(), tempo=np.asarray([np.nan]))},
    ):
        manifest = analyze_audio(source)

    assert manifest.bpm == 120.0
    assert len(manifest.events) == 1
    assert manifest.events[0].role == "sustain"
    assert manifest.events[0].velocity == 64


def test_audio_adapter_rejects_empty_audio_and_missing_files(tmp_path: Path) -> None:
    np = pytest.importorskip("numpy")
    from barrot_agent.creative.audio_adapter import analyze_audio

    with pytest.raises(FileNotFoundError):
        analyze_audio(tmp_path / "absent.wav")

    source = tmp_path / "empty.wav"
    source.write_bytes(b"empty")
    with patch.dict(sys.modules, {"librosa": _fake_librosa(np.asarray([], dtype=np.float32))}):
        with pytest.raises(ValueError, match="no samples"):
            analyze_audio(source)


def test_audio_adapter_reports_missing_optional_dependency(tmp_path: Path) -> None:
    from barrot_agent.creative.audio_adapter import analyze_audio

    source = tmp_path / "source.wav"
    source.write_bytes(b"source")
    with patch.dict(sys.modules, {"librosa": None}):
        with pytest.raises(RuntimeError, match="optional dependencies"):
            analyze_audio(source)



def test_stereo_integrity_flags_dc_offset_and_mono_cancellation() -> None:
    np = pytest.importorskip("numpy")
    from barrot_agent.creative.audio_render import _measure_stereo_integrity

    sample_count = 8192
    phase = np.arange(sample_count, dtype=np.float64) * (2.0 * np.pi / 256.0)
    tone = np.sin(phase)
    anti_phase = np.column_stack((tone + 0.01, -tone + 0.01)).astype(np.float32)

    measured = _measure_stereo_integrity(anti_phase)

    assert measured["dc_offset_dbfs"] > -60.0
    assert measured["dc_offset_warning"] is True
    assert measured["stereo_correlation"] < -0.999
    assert measured["mono_fold_down_loss_db"] < -3.0
    assert measured["mono_compatibility_warning"] is True
    assert "negative_stereo_correlation" in measured["warnings"]
    assert "mono_fold_down_loss_below_threshold" in measured["warnings"]


def test_stereo_integrity_passes_centered_mono_compatible_audio() -> None:
    np = pytest.importorskip("numpy")
    from barrot_agent.creative.audio_render import _measure_stereo_integrity

    sample_count = 8192
    phase = np.arange(sample_count, dtype=np.float64) * (2.0 * np.pi / 256.0)
    tone = np.sin(phase)
    compatible = np.column_stack((tone, 0.8 * tone)).astype(np.float32)

    measured = _measure_stereo_integrity(compatible)

    assert measured["dc_offset_dbfs"] < -60.0
    assert measured["stereo_correlation"] > 0.999
    assert measured["mono_fold_down_loss_db"] > -1.0
    assert measured["dc_offset_warning"] is False
    assert measured["mono_compatibility_warning"] is False
    assert measured["warnings"] == []



def test_stereo_side_reduction_preserves_mono_signal_and_repairs_phase_warning() -> None:
    np = pytest.importorskip("numpy")
    from barrot_agent.creative.audio_render import (
        _limit_stereo_side_for_mono_compatibility,
        _measure_stereo_integrity,
    )

    phase = np.arange(8192, dtype=np.float64) * (2.0 * np.pi / 256.0)
    tone = np.sin(phase)
    anti_phase = np.column_stack((tone, -0.5 * tone)).astype(np.float32)
    original_mono = (anti_phase[:, 0] + anti_phase[:, 1]) * 0.5

    corrected, report = _limit_stereo_side_for_mono_compatibility(anti_phase)
    measured = _measure_stereo_integrity(corrected)
    corrected_mono = (corrected[:, 0] + corrected[:, 1]) * 0.5

    assert report["applied"] is True
    assert report["status"] == "APPLIED"
    assert report["side_gain"] < 1.0
    assert np.allclose(corrected_mono, original_mono, atol=1e-7)
    assert measured["mono_compatibility_warning"] is False
    assert measured["mono_fold_down_loss_db"] >= -3.0
    assert measured["mono_fold_down_loss_db"] >= -3.5
    assert report["after"]["mono_fold_down_loss_db"] >= -3.5
    assert measured["stereo_correlation"] >= 0.0


def test_stereo_side_reduction_does_not_silence_a_true_mono_null() -> None:
    np = pytest.importorskip("numpy")
    from barrot_agent.creative.audio_render import (
        _limit_stereo_side_for_mono_compatibility,
        _measure_stereo_integrity,
    )

    phase = np.arange(8192, dtype=np.float64) * (2.0 * np.pi / 256.0)
    tone = np.sin(phase)
    anti_phase = np.column_stack((tone, -tone)).astype(np.float32)

    corrected, report = _limit_stereo_side_for_mono_compatibility(anti_phase)

    assert report["applied"] is False
    assert report["status"] == "UNRESOLVED"
    assert report["reason"] == "mid_signal_too_weak_to_preserve_mono_content"
    assert np.array_equal(corrected, anti_phase)
    assert _measure_stereo_integrity(corrected)["mono_compatibility_warning"] is True


def test_audio_render_integration_runs_for_integration_branch_pushes() -> None:
    workflow = Path(".github/workflows/audio-render-integration.yml").read_text(
        encoding="utf-8"
    )
    assert "push:" in workflow
    assert 'branches: ["integration/**"]' in workflow
    assert '"barrot_agent/creative/**"' in workflow
    assert '"tests/test_audio_render_integration.py"' in workflow

def test_loudness_metrics_measure_bs1770_integrated_lufs_lra_and_crest_factor() -> None:
    np = pytest.importorskip("numpy")
    from barrot_agent.creative.audio_render import _measure_loudness

    sample_rate = 48000
    sample_count = sample_rate * 20
    time = np.arange(sample_count, dtype=np.float64) / sample_rate
    signal = np.empty(sample_count, dtype=np.float64)
    signal[: sample_rate * 10] = 0.10 * np.sin(
        2.0 * np.pi * 440.0 * time[: sample_rate * 10]
    )
    signal[sample_rate * 10 :] = 0.05 * np.sin(
        2.0 * np.pi * 440.0 * time[sample_rate * 10 :]
    )
    stereo = np.column_stack((signal, signal * 0.9)).astype(np.float32)

    report = _measure_loudness(stereo, sample_rate)

    assert report["standard"] == "ITU-R BS.1770-4"
    assert report["loudness_range_standard"] == "EBU R128 LRA"
    assert report["implementation"] == "pyloudnorm"
    assert report["implementation_version"] == "0.2.0"
    assert report["status"] == "MEASURED"
    assert report["integrated_lufs"] is not None
    assert report["loudness_range_lu"] is not None
    assert report["loudness_range_lu"] >= 0.0
    assert report["crest_factor_db"] > 0.0
    assert report["normalization_applied"] is False
    assert report["measurement_only"] is True


def test_loudness_metrics_mark_silence_without_inventing_a_loudness_value() -> None:
    np = pytest.importorskip("numpy")
    from barrot_agent.creative.audio_render import _measure_loudness

    report = _measure_loudness(np.zeros((48000 * 5, 2), dtype=np.float32), 48000)

    assert report["status"] == "SILENT"
    assert report["integrated_lufs"] is None
    assert report["loudness_range_lu"] is None
    assert report["normalization_applied"] is False

