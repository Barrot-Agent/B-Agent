"""Tests for original composition and optional audio/MIDI adapters."""
import tempfile
import unittest
from types import ModuleType
from pathlib import Path
from unittest.mock import patch

from barrot_agent.creative.audio_adapter import analyze_audio
from barrot_agent.creative.composer import CompositionSettings, compose_original
from barrot_agent.creative.midi_export import export_midi
from barrot_agent.creative.musical_dna import MusicalEvent, MusicalManifest


def template():
    return MusicalManifest(
        bpm=110,
        beats_per_bar=4,
        scale="D minor",
        instruments=("kick", "snare", "bass", "keys"),
        events=(MusicalEvent("kick", "pulse", 0, 0.25),),
    )


class OriginalCompositionTests(unittest.TestCase):
    def test_composition_is_deterministic_for_seed(self):
        a = compose_original(template(), CompositionSettings(bars=8, seed=42))
        b = compose_original(template(), CompositionSettings(bars=8, seed=42))
        self.assertEqual(a, b)

    def test_composition_creates_harmony_melody_bass_and_drums(self):
        result = compose_original(template(), CompositionSettings(bars=8, seed=7))
        roles = {event.role for event in result.events}
        self.assertTrue({"harmony", "melody", "low_end", "pulse", "backbeat"} <= roles)
        self.assertEqual(result.provenance, "original_composition_seed_7")
        self.assertEqual(result.instruments, template().instruments)

    def test_composition_respects_scale_pitch_classes(self):
        result = compose_original(template(), CompositionSettings(bars=4, seed=11))
        allowed = {2, 4, 5, 7, 9, 10, 0}  # D natural minor pitch classes
        for event in result.events:
            if event.pitch is not None:
                self.assertIn(event.pitch % 12, allowed)

    def test_palette_can_be_expanded_when_requested(self):
        result = compose_original(
            template(),
            CompositionSettings(bars=4, seed=12, preserve_instrument_palette=False),
        )
        self.assertIn("lead", result.instruments)
        self.assertIn("hihat", result.instruments)

    def test_unsupported_scale_is_rejected(self):
        bad = MusicalManifest(110, 4, "mystery", ("kick",), ())
        with self.assertRaises(ValueError):
            compose_original(bad)


class AdapterTests(unittest.TestCase):
    def test_audio_adapter_rejects_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            analyze_audio("/definitely/not/a/real/audio/file.wav")

    def test_midi_export_requires_optional_dependency(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "test.mid"
            with patch.dict("sys.modules", {"pretty_midi": None}):
                with self.assertRaises(RuntimeError):
                    export_midi(compose_original(template()), target)
            self.assertFalse(target.exists())

    def test_midi_export_never_overwrites(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "existing.mid"
            target.write_bytes(b"existing")
            with self.assertRaises(FileExistsError):
                export_midi(template(), target)
            self.assertEqual(target.read_bytes(), b"existing")


if __name__ == "__main__":
    unittest.main()

class RecursiveCompositionEngineTests(unittest.TestCase):
    def test_every_run_is_recorded_and_approved_settings_seed_next_run(self):
        from barrot_agent.creative.composer import RecursiveCompositionEngine
        from barrot_agent.creative.musical_dna import RecursiveCreativeMemory

        with tempfile.TemporaryDirectory() as directory:
            memory = RecursiveCreativeMemory(Path(directory) / "journal.jsonl")
            engine = RecursiveCompositionEngine(memory)
            first = engine.create(template(), CompositionSettings(bars=8, seed=73))
            self.assertTrue(first.evaluation.passed)
            self.assertEqual(len(memory.read_all()), 1)
            engine.record_feedback(
                first, feedback="approved",
                lesson="Keep this seed and phrase density for the next draft",
            )
            second = engine.create(template())
            self.assertEqual(second.settings.seed, 74)
            self.assertEqual(second.settings.bars, 8)
            self.assertEqual(len(memory.read_all()), 3)
            self.assertTrue(second.learned_lessons)

    def test_negative_feedback_is_retained_but_not_promoted(self):
        from barrot_agent.creative.composer import RecursiveCompositionEngine
        from barrot_agent.creative.musical_dna import RecursiveCreativeMemory

        with tempfile.TemporaryDirectory() as directory:
            memory = RecursiveCreativeMemory(Path(directory) / "journal.jsonl")
            engine = RecursiveCompositionEngine(memory)
            run = engine.create(template(), CompositionSettings(bars=8, seed=19))
            engine.record_feedback(run, feedback="worse", lesson="Do not repeat this")
            self.assertIsNone(memory.recommend_composition_settings())
            self.assertEqual(len(memory.read_all()), 2)

class AudioRenderTests(unittest.TestCase):
    def test_audio_render_rejects_missing_soundfont(self):
        from barrot_agent.creative.audio_render import render_audio

        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "render.wav"
            with self.assertRaises(FileNotFoundError):
                render_audio(template(), target, soundfont_path=Path(directory) / "missing.sf2")
            self.assertFalse(target.exists())

    def test_audio_render_requires_optional_dependencies(self):
        from barrot_agent.creative.audio_render import render_audio

        with tempfile.TemporaryDirectory() as directory:
            soundfont = Path(directory) / "test.sf2"
            soundfont.write_bytes(b"placeholder")
            target = Path(directory) / "render.wav"
            with patch.dict("sys.modules", {"pretty_midi": None}):
                with self.assertRaises(RuntimeError):
                    render_audio(template(), target, soundfont_path=soundfont)
            self.assertFalse(target.exists())

    def test_audio_render_never_overwrites(self):
        from barrot_agent.creative.audio_render import render_audio

        with tempfile.TemporaryDirectory() as directory:
            soundfont = Path(directory) / "test.sf2"
            soundfont.write_bytes(b"placeholder")
            target = Path(directory) / "existing.wav"
            target.write_bytes(b"existing")
            with self.assertRaises(FileExistsError):
                render_audio(template(), target, soundfont_path=soundfont)
            self.assertEqual(target.read_bytes(), b"existing")

    def test_audio_render_validates_sample_rate(self):
        from barrot_agent.creative.audio_render import render_audio

        with tempfile.TemporaryDirectory() as directory:
            soundfont = Path(directory) / "test.sf2"
            soundfont.write_bytes(b"placeholder")
            with self.assertRaises(ValueError):
                render_audio(
                    template(),
                    Path(directory) / "render.wav",
                    soundfont_path=soundfont,
                    sample_rate=100,
                )
    def test_headroom_gain_reduces_only_when_sample_peak_exceeds_ceiling(self):
        from barrot_agent.creative.audio_render import _headroom_gain

        self.assertEqual(_headroom_gain(0.2, -6.0), 1.0)
        self.assertEqual(_headroom_gain(0.0, -6.0), 1.0)
        self.assertAlmostEqual(_headroom_gain(1.5, -6.0), (10 ** (-6.0 / 20.0)) / 1.5)
        with self.assertRaises(ValueError):
            _headroom_gain(float("nan"), -6.0)
        with self.assertRaises(ValueError):
            _headroom_gain(1.0, 1.0)

    def test_audio_render_writes_new_stereo_wav_with_sample_and_true_peak_headroom(self):
        import sys
        import numpy as np

        from barrot_agent.creative.audio_render import render_audio

        class FakeMidi:
            def __init__(self, path):
                self.path = path

        pretty_midi = ModuleType("pretty_midi")
        pretty_midi.PrettyMIDI = FakeMidi
        scipy = ModuleType("scipy")
        scipy.__path__ = []
        scipy_io = ModuleType("scipy.io")
        scipy_io.__path__ = []
        scipy_signal = ModuleType("scipy.signal")
        wavfile = ModuleType("scipy.io.wavfile")
        written = {}

        def resample_poly(samples, up, down, axis=0):
            return np.repeat(samples, up, axis=axis)

        def write(handle, sample_rate, samples):
            written["samples"] = np.asarray(samples).copy()
            handle.write(b"RIFF-test-wav")

        scipy_signal.resample_poly = resample_poly
        wavfile.write = write
        scipy_io.wavfile = wavfile
        scipy.io = scipy_io
        scipy.signal = scipy_signal

        rendered = np.asarray(
            [[0.0, 0.0], [0.8, -0.8], [0.8, -0.8]], dtype=np.float32
        )
        modules = {
            "pretty_midi": pretty_midi,
            "scipy": scipy,
            "scipy.io": scipy_io,
            "scipy.io.wavfile": wavfile,
            "scipy.signal": scipy_signal,
        }

        with tempfile.TemporaryDirectory() as directory:
            soundfont = Path(directory) / "test.sf2"
            soundfont.write_bytes(b"placeholder")
            target = Path(directory) / "render.wav"
            with patch.dict(sys.modules, modules), patch(
                "barrot_agent.creative.audio_render.export_midi",
                side_effect=lambda manifest, path: path.write_bytes(b"midi"),
            ), patch(
                "barrot_agent.creative.audio_render._render_midi_stereo",
                return_value=rendered,
            ):
                result = render_audio(template(), target, soundfont_path=soundfont)

            ceiling = 10 ** (-6.0 / 20.0)
            self.assertEqual(target.read_bytes(), b"RIFF-test-wav")
            self.assertEqual(result.sample_rate, 44100)
            self.assertAlmostEqual(result.duration_seconds, 3 / 44100)
            self.assertEqual(result.channels, 2)
            self.assertLess(result.peak_level, ceiling)
            self.assertAlmostEqual(result.true_peak_level, ceiling, places=6)
            self.assertLessEqual(
                float(np.max(np.abs(written["samples"]))), ceiling + 1e-6
            )
            self.assertGreater(result.rms_level, 0.0)

    def test_stereo_renderer_schedules_pitched_and_drum_channels(self):
        import sys
        import numpy as np
        from types import SimpleNamespace

        from barrot_agent.creative.audio_render import _render_midi_stereo

        class FakeSynth:
            def __init__(self, *, samplerate):
                self.samplerate = samplerate
                self.calls = []
                self.deleted = False

            def sfload(self, path):
                self.calls.append(("sfload", path))
                return 7

            def program_select(self, channel, soundfont_id, bank, program):
                self.calls.append(("program_select", channel, soundfont_id, bank, program))
                return 0

            def get_samples(self, count):
                self.calls.append(("get_samples", count))
                return np.tile(np.asarray([0.1, -0.1], dtype=np.float32), count)

            def noteon(self, channel, pitch, velocity):
                self.calls.append(("noteon", channel, pitch, velocity))

            def noteoff(self, channel, pitch):
                self.calls.append(("noteoff", channel, pitch))

            def pitch_bend(self, channel, value):
                self.calls.append(("pitch_bend", channel, value))

            def cc(self, channel, number, value):
                self.calls.append(("cc", channel, number, value))

            def delete(self):
                self.deleted = True

        fake_synth = FakeSynth(samplerate=8000)
        fluidsynth = ModuleType("fluidsynth")
        fluidsynth.Synth = lambda **kwargs: fake_synth

        note = lambda start, end, pitch, velocity: SimpleNamespace(
            start=start, end=end, pitch=pitch, velocity=velocity
        )
        pitched = SimpleNamespace(
            is_drum=False, program=10, notes=[note(0.0, 0.5, 60, 90)],
            pitch_bends=[], control_changes=[],
        )
        drums = SimpleNamespace(
            is_drum=True, program=0, notes=[note(0.25, 0.5, 36, 100)],
            pitch_bends=[], control_changes=[],
        )
        midi = SimpleNamespace(
            instruments=[pitched, drums],
            get_end_time=lambda: 1.0,
        )

        with patch.dict(sys.modules, {"fluidsynth": fluidsynth}):
            audio = _render_midi_stereo(
                midi, soundfont_path="test.sf2", sample_rate=8000
            )

        self.assertEqual(audio.shape, (16000, 2))
        self.assertIn(("program_select", 0, 7, 0, 10), fake_synth.calls)
        self.assertIn(("program_select", 9, 7, 128, 0), fake_synth.calls)
        self.assertIn(("noteon", 0, 60, 90), fake_synth.calls)
        self.assertIn(("noteon", 9, 36, 100), fake_synth.calls)
        self.assertIn(("noteoff", 0, 60), fake_synth.calls)
        self.assertIn(("noteoff", 9, 36), fake_synth.calls)
        self.assertTrue(fake_synth.deleted)
