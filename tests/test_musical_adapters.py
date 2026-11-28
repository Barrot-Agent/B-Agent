"""Tests for original composition and optional audio/MIDI adapters."""
import pytest
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
        np = pytest.importorskip("numpy")

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
            expanded = np.repeat(samples, up, axis=axis)
            expanded[4, 0] = 1.2
            expanded[4, 1] = -1.2
            return expanded

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
        np = pytest.importorskip("numpy")
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


    def test_stereo_renderer_routes_each_named_track_to_its_soundfont(self):
        import sys
        import numpy as np
        from types import SimpleNamespace

        from barrot_agent.creative.audio_render import _render_midi_stereo

        class FakeSynth:
            def __init__(self, *, samplerate):
                self.calls = []
                self.deleted = False

            def sfload(self, path):
                soundfont_id = 7 + sum(call[0] == "sfload" for call in self.calls)
                self.calls.append(("sfload", path, soundfont_id))
                return soundfont_id

            def program_select(self, channel, soundfont_id, bank, program):
                self.calls.append(("program_select", channel, soundfont_id, bank, program))
                return 0

            def get_samples(self, count):
                self.calls.append(("get_samples", count))
                return np.zeros(count * 2, dtype=np.float32)

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
        note = lambda: SimpleNamespace(start=0.0, end=0.5, pitch=60, velocity=90)
        keys = SimpleNamespace(
            name="keys", is_drum=False, program=10, notes=[note()],
            pitch_bends=[], control_changes=[],
        )
        bass = SimpleNamespace(
            name="bass", is_drum=False, program=33, notes=[note()],
            pitch_bends=[], control_changes=[],
        )
        midi = SimpleNamespace(instruments=[keys, bass], get_end_time=lambda: 1.0)

        with patch.dict(sys.modules, {"fluidsynth": fluidsynth}):
            audio = _render_midi_stereo(
                midi,
                soundfont_path={"keys": "keys.sf2", "bass": "bass.sf2"},
                sample_rate=8000,
            )

        self.assertEqual(audio.shape, (16000, 2))
        self.assertEqual(
            [call[1] for call in fake_synth.calls if call[0] == "sfload"],
            ["keys.sf2", "bass.sf2"],
        )
        self.assertIn(("program_select", 0, 7, 0, 10), fake_synth.calls)
        self.assertIn(("program_select", 1, 8, 0, 33), fake_synth.calls)
        self.assertTrue(fake_synth.deleted)


class FullSongProductionTests(unittest.TestCase):
    def test_full_song_form_is_deterministic_section_aware_and_long(self):
        from barrot_agent.creative.composer import (
            DEFAULT_FULL_SONG_FORM,
            DEFAULT_PRODUCTION_INSTRUMENTS,
            compose_full_song,
        )

        first = compose_full_song(template(), seed=20261123)
        second = compose_full_song(template(), seed=20261123)
        self.assertEqual(first, second)
        self.assertEqual(first.sections, DEFAULT_FULL_SONG_FORM.sections)
        self.assertEqual(first.instruments, DEFAULT_PRODUCTION_INSTRUMENTS)
        self.assertEqual(sum(section.bars for section in first.sections), 80)
        self.assertEqual(first.sections[0].name, "intro")
        self.assertEqual(first.sections[-1].name, "outro")
        self.assertGreater(len(first.events), 1000)
        roles = {event.role for event in first.events}
        self.assertTrue(
            {"harmony", "melody", "low_end", "pulse", "backbeat", "transition_fill"}
            <= roles
        )
        total_beats = DEFAULT_FULL_SONG_FORM.total_bars * first.beats_per_bar
        self.assertLessEqual(
            max(event.beat + event.duration for event in first.events),
            total_beats + 1e-6,
        )
        self.assertEqual(first.provenance, "original_full_song_extended_pop_80_seed_20261123")

        def average_velocity(section_name):
            section = next(item for item in first.sections if item.name == section_name)
            start = (section.start_bar - 1) * first.beats_per_bar
            end = start + section.bars * first.beats_per_bar
            values = [
                event.velocity for event in first.events if start <= event.beat < end
            ]
            return sum(values) / len(values)

        self.assertGreater(average_velocity("final_chorus"), average_velocity("intro"))

    def test_full_song_uses_distinct_bridge_harmony_and_shared_chorus_hook(self):
        from barrot_agent.creative.composer import compose_full_song

        manifest = compose_full_song(template(), seed=17)

        def first_chord(section_name):
            section = next(item for item in manifest.sections if item.name == section_name)
            start = (section.start_bar - 1) * manifest.beats_per_bar
            return tuple(sorted(
                event.pitch for event in manifest.events
                if event.instrument == "keys"
                and event.role == "harmony"
                and event.beat == start
                and event.pitch is not None
            ))

        self.assertNotEqual(first_chord("verse1"), first_chord("bridge"))
        self.assertEqual(first_chord("chorus1"), first_chord("chorus2"))
        self.assertEqual(first_chord("chorus2"), first_chord("final_chorus"))

    def test_midi_export_includes_named_section_markers(self):
        import sys
        from types import ModuleType
        from barrot_agent.creative.composer import compose_full_song
        from barrot_agent.creative.midi_export import export_midi

        instances = []
        midi_files = []

        class FakeMidi:
            def __init__(self, initial_tempo):
                self.initial_tempo = initial_tempo
                self.instruments = []
                instances.append(self)

            def write(self, path):
                Path(path).write_bytes(b"midi")

        class FakeMetaMessage:
            def __init__(self, message_type, **kwargs):
                self.type = message_type
                self.time = kwargs.get("time", 0)
                self.text = kwargs.get("text")
                self.name = kwargs.get("name")

        class FakeMidiTrack(list):
            pass

        class FakeMidiFile:
            def __init__(self, filename):
                self.ticks_per_beat = 220
                self.tracks = [FakeMidiTrack()]
                midi_files.append(self)

            def save(self, filename):
                Path(filename).write_bytes(b"midi-with-section-markers")

        class FakeInstrument:
            def __init__(self, program, is_drum, name):
                self.program = program
                self.is_drum = is_drum
                self.name = name
                self.notes = []

        class FakeNote:
            def __init__(self, velocity, pitch, start, end):
                self.velocity = velocity
                self.pitch = pitch
                self.start = start
                self.end = end

        fake = ModuleType("pretty_midi")
        fake.PrettyMIDI = FakeMidi
        fake.Instrument = FakeInstrument
        fake.Note = FakeNote
        fake_mido = ModuleType("mido")
        fake_mido.MidiFile = FakeMidiFile
        fake_mido.MidiTrack = FakeMidiTrack
        fake_mido.MetaMessage = FakeMetaMessage
        manifest = compose_full_song(template(), seed=9)

        with tempfile.TemporaryDirectory() as directory, patch.dict(
            sys.modules, {"pretty_midi": fake, "mido": fake_mido}
        ):
            target = Path(directory) / "full-song.mid"
            export_midi(manifest, target, program_map={"keys": 0})
            self.assertTrue(target.is_file())
            program_by_name = {
                instrument.name: instrument.program
                for instrument in instances[0].instruments
            }
            self.assertEqual(program_by_name["keys"], 0)
            self.assertEqual(program_by_name["bass"], 33)

        marker_track = next(
            track for track in midi_files[0].tracks
            if any(message.type == "marker" for message in track)
        )
        marker_messages = []
        absolute_tick = 0
        for message in marker_track:
            absolute_tick += message.time
            if message.type == "marker":
                marker_messages.append((message.text, absolute_tick))
        self.assertEqual(
            [name for name, _ in marker_messages],
            [section.name for section in manifest.sections],
        )
        self.assertEqual(
            [tick for _, tick in marker_messages],
            [
                round(
                    (section.start_bar - 1)
                    * manifest.beats_per_bar
                    * midi_files[0].ticks_per_beat
                )
                for section in manifest.sections
            ],
        )
