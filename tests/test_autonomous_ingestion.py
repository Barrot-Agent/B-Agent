#!/usr/bin/env python3
"""
Test Suite for Autonomous Ingestion System
Tests all components of the ingestion engine and related systems.
"""

import sys
import unittest
from pathlib import Path

# Add parent directory to path
base_path = Path(__file__).parent.parent
sys.path.insert(0, str(base_path))
sys.path.insert(0, str(base_path / "Barrot-Agent"))
sys.path.insert(0, str(base_path / "barrot_sim"))
sys.path.insert(0, str(base_path / "glyphs"))

from autonomous_ingestion_engine import AutonomousIngestionEngine
from alignment_scorer import AlignmentScorer
from ingestors.youtube_ingestor import YouTubeIngestor
from ingestors.arxiv_ingestor import ArxivIngestor
from ingestors.github_ingestor import GitHubIngestor
from ingestors.web_ingestor import WebIngestor
from pingpong_processor import BundlePingPongProcessor
from auto_emergence_detector import AutoGlyphEmergenceDetector


class TestIngestionEngine(unittest.TestCase):
    """Test the main autonomous ingestion engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = AutonomousIngestionEngine()
    
    def test_engine_initialization(self):
        """Test that engine initializes properly."""
        self.assertIsNotNone(self.engine)
        self.assertIsInstance(self.engine.config, dict)
        self.assertIsInstance(self.engine.puzzle_pieces, list)
        self.assertIsInstance(self.engine.active_modules, list)
    
    def test_get_status(self):
        """Test status retrieval."""
        status = self.engine.get_status()
        self.assertIsInstance(status, dict)
        self.assertIn('engine_version', status)
        self.assertIn('enabled', status)


class TestIngestors(unittest.TestCase):
    """Test all source ingestors."""
    
    def test_youtube_ingestor(self):
        """Test YouTube ingestor."""
        ingestor = YouTubeIngestor()
        self.assertIsNotNone(ingestor)
        results = ingestor.search(["AGI"])
        self.assertIsInstance(results, list)
    
    def test_arxiv_ingestor(self):
        """Test arXiv ingestor."""
        ingestor = ArxivIngestor()
        self.assertIsNotNone(ingestor)
        results = ingestor.search(["neural networks"])
        self.assertIsInstance(results, list)
    
    def test_github_ingestor(self):
        """Test GitHub ingestor."""
        ingestor = GitHubIngestor()
        self.assertIsNotNone(ingestor)
        results = ingestor.search(["ai-agents"])
        self.assertIsInstance(results, list)
    
    def test_web_ingestor(self):
        """Test web ingestor."""
        ingestor = WebIngestor()
        self.assertIsNotNone(ingestor)
        results = ingestor.search(["AGI research"])
        self.assertIsInstance(results, list)


class TestAlignmentScorer(unittest.TestCase):
    """Test content alignment scoring."""
    
    def test_scorer_initialization(self):
        """Test scorer initialization."""
        puzzle_pieces = [{"id": 1, "name": "Test", "integration_level": "high"}]
        modules = [{"name": "test_module"}]
        scorer = AlignmentScorer(puzzle_pieces, modules)
        self.assertIsNotNone(scorer)
    
    def test_score_content(self):
        """Test content scoring."""
        puzzle_pieces = [{"id": 1, "name": "Test", "integration_level": "high"}]
        modules = [{"name": "test_module"}]
        scorer = AlignmentScorer(puzzle_pieces, modules)
        
        content = {"id": "test", "source": "arxiv", "title": "Test"}
        result = scorer.score_content(content)
        self.assertIn('overall_score', result)
        self.assertGreaterEqual(result['overall_score'], 0.0)
        self.assertLessEqual(result['overall_score'], 1.0)


class TestPingPongProcessor(unittest.TestCase):
    """Test PingPong bundle processor."""
    
    def test_processor_initialization(self):
        """Test processor initialization."""
        processor = BundlePingPongProcessor("v20")
        self.assertIsNotNone(processor)
        self.assertEqual(processor.bundle_version, "v20")
    
    def test_calculate_convergence(self):
        """Test convergence calculation."""
        processor = BundlePingPongProcessor("v20")
        convergence = processor._calculate_convergence({"a": 1}, {"a": 1, "b": 2})
        self.assertIsInstance(convergence, float)
        self.assertGreaterEqual(convergence, 0.0)
        self.assertLessEqual(convergence, 1.0)


class TestGlyphDetector(unittest.TestCase):
    """Test glyph emergence detector."""
    
    def test_detector_initialization(self):
        """Test detector initialization."""
        detector = AutoGlyphEmergenceDetector()
        self.assertIsNotNone(detector)
        self.assertIsInstance(detector.existing_glyphs, list)
    
    def test_glyph_name_generation(self):
        """Test glyph name generation."""
        detector = AutoGlyphEmergenceDetector()
        name = detector._generate_glyph_name("test concept")
        self.assertEqual(name, "TEST_CONCEPT_GLYPH")


def run_tests():
    """Run all tests."""
    print("=" * 70)
    print("Autonomous Ingestion System Test Suite")
    print("=" * 70)
    print()
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestIngestionEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestIngestors))
    suite.addTests(loader.loadTestsFromTestCase(TestAlignmentScorer))
    suite.addTests(loader.loadTestsFromTestCase(TestPingPongProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestGlyphDetector))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
