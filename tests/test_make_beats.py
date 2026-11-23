from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "barrot_make_beats",
    ROOT / "scripts" / "make_beats.py",
)
assert SPEC is not None and SPEC.loader is not None
make_beats = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(make_beats)


def _minimal_config(slug: str = "test_track") -> dict:
    return {
        "slug": slug,
        "title": slug,
        "bpm": 120,
        "key": ("C", "minor"),
        "swing": 0.0,
        "prog": [("C", "m7")],
        "sections": [("verse", 1)],
        "drums": {"verse": {make_beats.SN: {0: 100}}},
        "bass": {},
    }


def test_render_wav_is_byte_reproducible_for_same_seed(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(make_beats, "kit_drum", lambda *args, **kwargs: None)
    monkeypatch.setattr(make_beats, "sample_mel", lambda *args, **kwargs: None)
    cfg = _minimal_config()

    first = tmp_path / "first.wav"
    second = tmp_path / "second.wav"
    first_duration = make_beats.render_wav(cfg, first, seed=42)
    second_duration = make_beats.render_wav(cfg, second, seed=42)

    assert first_duration == second_duration
    assert first.read_bytes() == second.read_bytes()


def test_render_wav_refuses_to_overwrite_existing_audio(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(make_beats, "kit_drum", lambda *args, **kwargs: None)
    monkeypatch.setattr(make_beats, "sample_mel", lambda *args, **kwargs: None)
    cfg = _minimal_config()
    target = tmp_path / "preserved.wav"
    target.write_bytes(b"user-owned audio")
    original = target.read_bytes()

    with pytest.raises(FileExistsError):
        make_beats.render_wav(cfg, target, seed=99)

    assert target.read_bytes() == original


def test_build_all_refuses_existing_artifacts_before_starting(tmp_path: Path, monkeypatch) -> None:
    cfg = _minimal_config()
    monkeypatch.setattr(make_beats, "TRACKS", [cfg])
    output_dir = tmp_path / "build"
    output_dir.mkdir()
    preserved = output_dir / f"{cfg['slug']}.wav"
    preserved.write_bytes(b"preserve this take")

    def fail_if_called(_cfg):
        raise AssertionError("preflight must stop before rendering or MIDI generation")

    monkeypatch.setattr(make_beats, "build_midi", fail_if_called)
    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        make_beats.build_all(output_dir=output_dir, seed=5)

    assert preserved.read_bytes() == b"preserve this take"


def test_midi_publish_refuses_concurrent_target_without_overwrite(tmp_path: Path) -> None:
    target = tmp_path / "race.mid"

    class RacingMidi:
        def write(self, path: str) -> None:
            Path(path).write_bytes(b"generated MIDI")
            # Simulate another process creating a user-owned target after preflight.
            target.write_bytes(b"concurrent user MIDI")

    with pytest.raises(FileExistsError, match="Refusing to overwrite existing MIDI"):
        make_beats._write_midi_exclusive(RacingMidi(), target)

    assert target.read_bytes() == b"concurrent user MIDI"
    assert list(tmp_path.glob(f".{target.name}.*.tmp")) == []


def test_build_all_uses_distinct_deterministic_seeds_and_versioned_outputs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    tracks = [_minimal_config("first"), _minimal_config("second")]
    monkeypatch.setattr(make_beats, "TRACKS", tracks)

    class FakeMidi:
        def write(self, path: str) -> None:
            Path(path).write_bytes(b"MIDI")

    seeds: list[int] = []

    def fake_render(_cfg, path: Path, *, seed: int) -> float:
        seeds.append(seed)
        with Path(path).open("xb") as handle:
            handle.write(f"WAV-{seed}".encode())
        return 2.0

    def fake_pattern(_cfg, path: Path, _bars: int) -> None:
        with Path(path).open("x", encoding="utf-8") as handle:
            handle.write("pattern")

    monkeypatch.setattr(make_beats, "build_midi", lambda _cfg: (FakeMidi(), 1))
    monkeypatch.setattr(make_beats, "render_wav", fake_render)
    monkeypatch.setattr(make_beats, "write_pattern_txt", fake_pattern)

    output_dir = tmp_path / "builds" / "seed-17"
    report = make_beats.build_all(output_dir=output_dir, seed=17)

    assert seeds == [17, 18]
    assert len(report) == 2
    assert (output_dir / "first.mid").read_bytes() == b"MIDI"
    assert (output_dir / "first.wav").read_bytes() == b"WAV-17"
    assert (output_dir / "second.wav").read_bytes() == b"WAV-18"
    assert (output_dir / "second_pattern.txt").read_text(encoding="utf-8") == "pattern"

    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        make_beats.build_all(output_dir=output_dir, seed=17)



def test_linear_headroom_gain_is_non_boosting_and_validates() -> None:
    assert make_beats._linear_headroom_gain(0.0, -6.0) == 1.0
    assert make_beats._linear_headroom_gain(0.25, -6.0) == 1.0
    assert make_beats._linear_headroom_gain(1.5, -6.0) == pytest.approx(
        (10 ** (-6.0 / 20.0)) / 1.5
    )
    with pytest.raises(ValueError):
        make_beats._linear_headroom_gain(float("nan"), -6.0)
    with pytest.raises(ValueError):
        make_beats._linear_headroom_gain(1.0, 1.0)


def test_render_wav_uses_linear_gain_and_leaves_six_db_sample_headroom(
    tmp_path: Path,
    monkeypatch,
) -> None:
    import wave

    monkeypatch.setattr(make_beats, "kit_drum", lambda *args, **kwargs: None)
    monkeypatch.setattr(make_beats, "sample_mel", lambda *args, **kwargs: None)

    def test_signal(_gm, _velocity, duration, *, rng=None):
        signal = make_beats.np.zeros(
            int(make_beats.SR * duration),
            dtype=make_beats.np.float32,
        )
        signal[0] = 1.0
        signal[1] = 0.5
        return signal

    monkeypatch.setattr(make_beats, "synth_drum", test_signal)
    target = tmp_path / "linear-premaster.wav"
    make_beats.render_wav(
        _minimal_config(),
        target,
        seed=7,
        headroom_dbfs=-6.0,
    )

    with wave.open(str(target), "rb") as rendered:
        assert rendered.getnchannels() == 2
        assert rendered.getsampwidth() == 2
        samples = make_beats.np.frombuffer(
            rendered.readframes(rendered.getnframes()),
            dtype="<i2",
        ).reshape(-1, 2)

    normalized = samples.astype(make_beats.np.float64) / 32767.0
    ceiling = 10 ** (-6.0 / 20.0)
    assert make_beats.np.max(make_beats.np.abs(normalized)) <= ceiling + 1 / 32767
    left = normalized[:2, 0]
    assert left[1] != 0
    assert abs(left[0] / left[1]) == pytest.approx(2.0, rel=1e-3)
