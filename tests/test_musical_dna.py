"""Tests for the Musical DNA Transmutation and recursive learning engine."""
import json
import tempfile
import unittest
from pathlib import Path

from barrot_agent.creative.musical_dna import (
    Evaluation,
    MusicalEvent,
    MusicalManifest,
    MusicalSection,
    RecursiveCreativeMemory,
    Transmutation,
    evaluate_transmutation,
    transmute,
)


def sample_manifest():
    return MusicalManifest(
        bpm=104,
        beats_per_bar=4,
        scale="D minor",
        instruments=("kick", "snare", "bass", "keys"),
        events=(
            MusicalEvent("kick", "pulse", 0.0, 0.5, 110),
            MusicalEvent("snare", "backbeat", 1.0, 0.25, 100),
            MusicalEvent("bass", "low_end", 1.5, 1.0, 90, 38),
            MusicalEvent("keys", "harmony", 2.0, 1.5, 75, 62),
        ),
        sections=(MusicalSection("verse", 1, 8, 0.45),),
    )


class MusicalManifestTests(unittest.TestCase):
    def test_fingerprint_is_stable(self):
        self.assertEqual(sample_manifest().fingerprint, sample_manifest().fingerprint)

    def test_invalid_event_is_rejected(self):
        with self.assertRaises(ValueError):
            MusicalEvent("kick", "pulse", -1, 0.5)

    def test_manifest_rejects_unknown_instrument(self):
        with self.assertRaises(ValueError):
            MusicalManifest(100, 4, "C major", ("kick",),
                            (MusicalEvent("snare", "backbeat", 0, 0.5),))


class TransmutationTests(unittest.TestCase):
    def test_transmutation_preserves_locked_inventory(self):
        source = sample_manifest()
        result = transmute(source, Transmutation(
            phase_shift_beats=0.25, duration_scale=0.8, swing=0.1
        ))
        self.assertEqual(len(source.events), len(result.events))
        self.assertEqual(source.instruments, result.instruments)
        self.assertEqual(source.bpm, result.bpm)
        self.assertEqual(source.scale, result.scale)
        self.assertEqual(source.beats_per_bar, result.beats_per_bar)
        self.assertEqual(
            sorted(event.role for event in source.events),
            sorted(event.role for event in result.events),
        )

    def test_transmutation_is_deterministic(self):
        source = sample_manifest()
        settings = Transmutation(phase_shift_beats=0.25, duration_scale=0.9)
        self.assertEqual(transmute(source, settings), transmute(source, settings))

    def test_evaluator_rejects_no_change(self):
        source = sample_manifest()
        result = evaluate_transmutation(source, transmute(source, Transmutation()))
        self.assertFalse(result.passed)

    def test_evaluator_accepts_valid_change(self):
        source = sample_manifest()
        result = transmute(source, Transmutation(phase_shift_beats=0.25))
        evaluation = evaluate_transmutation(source, result)
        self.assertTrue(evaluation.passed)
        self.assertEqual(evaluation.constraint_adherence, 1.0)

    def test_evaluator_rejects_changed_inventory(self):
        source = sample_manifest()
        result = transmute(source, Transmutation(phase_shift_beats=0.25))
        invalid = MusicalManifest(
            bpm=result.bpm, beats_per_bar=result.beats_per_bar,
            scale=result.scale, instruments=("kick",),
            events=(MusicalEvent("kick", "pulse", 0, 0.5),),
        )
        self.assertFalse(evaluate_transmutation(source, invalid).passed)


class RecursiveMemoryTests(unittest.TestCase):
    def test_every_attempt_is_retained_but_only_verified_positive_is_promoted(self):
        with tempfile.TemporaryDirectory() as directory:
            memory = RecursiveCreativeMemory(Path(directory) / "attempts.jsonl")
            passed = Evaluation(True, 0.9, 0.7, 1.0)
            failed = Evaluation(False, 0.2, 0.0, 0.0, ("failed",))
            settings = Transmutation(phase_shift_beats=0.25)
            memory.record_attempt(
                source_fingerprint="source-1", output_fingerprint="output-1",
                settings=settings, evaluation=failed, user_feedback="positive",
                lesson="This must not be promoted",
            )
            memory.record_attempt(
                source_fingerprint="source-1", output_fingerprint="output-2",
                settings=settings, evaluation=passed, user_feedback="approved",
                lesson="The syncopated shift improved the groove",
            )
            self.assertEqual(len(memory.read_all()), 2)
            self.assertEqual(len(memory.verified_lessons()), 1)
            self.assertEqual(
                memory.verified_lessons()[0]["lesson"],
                "The syncopated shift improved the groove",
            )

    def test_recommendation_uses_best_verified_lesson(self):
        with tempfile.TemporaryDirectory() as directory:
            memory = RecursiveCreativeMemory(Path(directory) / "attempts.jsonl")
            memory.record_attempt(
                source_fingerprint="s", output_fingerprint="o",
                settings=Transmutation(phase_shift_beats=0.5),
                evaluation=Evaluation(True, 0.95, 0.8, 1.0),
                user_feedback="approved", lesson="Strongest result",
            )
            self.assertEqual(memory.recommend_settings().phase_shift_beats, 0.5)

    def test_negative_feedback_does_not_promote(self):
        with tempfile.TemporaryDirectory() as directory:
            memory = RecursiveCreativeMemory(Path(directory) / "attempts.jsonl")
            memory.record_attempt(
                source_fingerprint="s", output_fingerprint="o",
                settings=Transmutation(),
                evaluation=Evaluation(True, 0.95, 0.8, 1.0),
                user_feedback="worse", lesson="Do not learn this",
            )
            self.assertEqual(memory.verified_lessons(), [])


if __name__ == "__main__":
    unittest.main()
