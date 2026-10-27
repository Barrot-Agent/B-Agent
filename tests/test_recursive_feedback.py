"""
Tests for Kimi 3 integration and recursive feedback loop.
"""

import json
from unittest.mock import MagicMock, Mock, patch

import pytest

from barrot_agent.config import FeedbackLoopConfig, KimiConfig
from barrot_agent.kimi_integration import KimiClient
from barrot_agent.recursive_feedback import RecursiveFeedbackLoop


class TestKimiClient:
    """Test Kimi 3 API client."""

    def test_is_available_without_config(self):
        """Test that Kimi is not available without configuration."""
        config = KimiConfig(enabled=False)
        client = KimiClient(config)
        assert not client.is_available

    def test_is_available_with_config(self):
        """Test that Kimi is available with proper configuration."""
        config = KimiConfig(enabled=True, api_key="test_key")
        client = KimiClient(config)
        assert client.is_available

    @patch("barrot_agent.kimi_integration.requests.Session.post")
    def test_generate_success(self, mock_post):
        """Test successful text generation."""
        config = KimiConfig(enabled=True, api_key="test_key")
        client = KimiClient(config)

        mock_response = Mock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "Test response"}}]}
        mock_post.return_value = mock_response

        result = client.generate("Test prompt")
        assert result == "Test response"
        assert mock_post.called

    def test_generate_without_config(self):
        """Test that generate raises error without configuration."""
        config = KimiConfig(enabled=False)
        client = KimiClient(config)

        with pytest.raises(RuntimeError, match="Kimi integration not available"):
            client.generate("Test prompt")

    @patch("barrot_agent.kimi_integration.requests.Session.post")
    def test_analyze_feedback(self, mock_post):
        """Test feedback analysis."""
        config = KimiConfig(enabled=True, api_key="test_key")
        client = KimiClient(config)

        feedback_json = {
            "paradigm_shifts": ["Shift 1"],
            "emergent_patterns": ["Pattern 1"],
            "meta_optimizations": ["Opt 1"],
            "infrastructure_gaps": ["Gap 1"],
            "convergence_strategies": ["Strategy 1"],
        }

        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": json.dumps(feedback_json)}}]
        }
        mock_post.return_value = mock_response

        result = client.analyze_feedback(
            current_state={"iteration": 1},
            previous_outputs=[],
            improvement_goals=["Goal 1"],
        )

        assert "paradigm_shifts" in result
        assert result["paradigm_shifts"] == ["Shift 1"]


class TestRecursiveFeedbackLoop:
    """Test recursive feedback loop orchestrator."""

    def test_initialization(self):
        """Test feedback loop initialization."""
        loop = RecursiveFeedbackLoop()
        assert loop.config is not None
        assert loop.kimi is not None
        assert loop.output_dir.exists()

    def test_observe_system_state(self):
        """Test system state observation."""
        loop = RecursiveFeedbackLoop()
        state = loop._observe_system_state(iteration=1)

        assert "iteration" in state
        assert state["iteration"] == 1
        assert "timestamp" in state
        assert "infrastructure" in state

    def test_absorb_feedback(self):
        """Test feedback absorption."""
        loop = RecursiveFeedbackLoop()

        kimi_feedback = {
            "paradigm_shifts": ["Shift 1", "Shift 2"],
            "emergent_patterns": ["Pattern 1"],
            "meta_optimizations": ["Opt 1"],
            "infrastructure_gaps": ["Gap 1"],
            "convergence_strategies": ["Strategy 1"],
        }

        insights = loop._absorb_feedback(kimi_feedback)

        assert len(insights) == 6  # 2 shifts + 1 pattern + 1 opt + 1 gap + 1 strategy
        assert any("PARADIGM:" in i for i in insights)
        assert any("PATTERN:" in i for i in insights)
        assert any("META:" in i for i in insights)
        assert any("GAP:" in i for i in insights)
        assert any("STRATEGY:" in i for i in insights)

    def test_verify_improvement(self):
        """Test improvement verification."""
        loop = RecursiveFeedbackLoop()

        system_state = {"infrastructure": {"coverage_gain": 0.5}}
        applied_improvements = ["Improvement 1", "Improvement 2"]

        score, convergence = loop._verify_improvement(
            iteration=1, system_state=system_state, applied_improvements=applied_improvements
        )

        assert 0.0 <= score <= 1.0
        assert 0.0 <= convergence <= 1.0

    @patch.object(RecursiveFeedbackLoop, "_observe_system_state")
    @patch.object(RecursiveFeedbackLoop, "_analyze_with_kimi")
    @patch.object(RecursiveFeedbackLoop, "_absorb_feedback")
    @patch.object(RecursiveFeedbackLoop, "_apply_improvements")
    @patch.object(RecursiveFeedbackLoop, "_verify_improvement")
    def test_run_converges(
        self,
        mock_verify,
        mock_apply,
        mock_absorb,
        mock_analyze,
        mock_observe,
    ):
        """Test that loop can converge."""
        config = FeedbackLoopConfig(
            max_iterations=10,
            convergence_threshold=0.90,
        )
        loop = RecursiveFeedbackLoop(loop_config=config)

        # Mock all methods to return quickly
        mock_observe.return_value = {"iteration": 1}
        mock_analyze.return_value = {"paradigm_shifts": ["Test"]}
        mock_absorb.return_value = ["PARADIGM: Test"]
        mock_apply.return_value = (["Applied"], {})
        mock_verify.return_value = (0.8, 0.95)  # Convergence above threshold

        report = loop.run(max_iterations=5)

        assert report.converged
        assert report.total_iterations <= 5
        assert report.final_convergence >= 0.90

    @patch.object(RecursiveFeedbackLoop, "_observe_system_state")
    @patch.object(RecursiveFeedbackLoop, "_analyze_with_kimi")
    @patch.object(RecursiveFeedbackLoop, "_absorb_feedback")
    @patch.object(RecursiveFeedbackLoop, "_apply_improvements")
    @patch.object(RecursiveFeedbackLoop, "_verify_improvement")
    def test_run_reaches_max_iterations(
        self,
        mock_verify,
        mock_apply,
        mock_absorb,
        mock_analyze,
        mock_observe,
    ):
        """Test that loop respects max iterations."""
        config = FeedbackLoopConfig(
            max_iterations=10,
            convergence_threshold=0.99,  # Very high threshold
        )
        loop = RecursiveFeedbackLoop(loop_config=config)

        # Mock all methods to return quickly
        mock_observe.return_value = {"iteration": 1}
        mock_analyze.return_value = {"paradigm_shifts": ["Test"]}
        mock_absorb.return_value = ["PARADIGM: Test"]
        mock_apply.return_value = (["Applied"], {})
        mock_verify.return_value = (0.5, 0.5)  # Never converges

        report = loop.run(max_iterations=5)

        assert not report.converged
        assert report.total_iterations == 5


class TestFeedbackLoopConfig:
    """Test feedback loop configuration."""

    def test_default_values(self):
        """Test default configuration values."""
        config = FeedbackLoopConfig()

        assert config.max_iterations == 100
        assert config.convergence_threshold == 0.95
        assert config.improvement_window == 5
        assert config.enable_auto_refinement is True
        assert config.refinement_interval == 10


class TestKimiConfig:
    """Test Kimi configuration."""

    def test_default_values(self):
        """Test default configuration values."""
        config = KimiConfig()

        assert config.api_key is None
        assert config.model_name == "moonshot-v1-128k"
        assert config.enabled is False
        assert config.temperature == 0.7
