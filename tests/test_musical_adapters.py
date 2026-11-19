"""Tests for original composition and optional audio/MIDI adapters."""
import tempfile
import unittest
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

    def test_composition_respects_scale_pitch_classes(self):
        result = compose_original(template(), CompositionSettings(bars=4, seed=11))
        allowed = {2, 4, 5, 7, 9, 10, 0}  # D natural minor pitch classes
        for event in result.events:
            if event.pitch is not None:
                self.assertIn(event.pitch % 12, allowed)

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
            second = engine.create(template(), CompositionSettings(bars=8, seed=999))
            self.assertEqual(second.settings.seed, 73)
            self.assertEqual(len(memory.read_all()), 4)

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
