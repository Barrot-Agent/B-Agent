"""
Kimi 3 Model Integration for Recursive Feedback Loops.

This module provides integration with Moonshot AI's Kimi 3 model for
paradigm-shifting refinement and feedback generation.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

import requests

from .config import KimiConfig
from .logger import get_logger

logger = get_logger(__name__)


class KimiClient:
    """Client for interacting with Kimi 3 API."""

    def __init__(self, config: KimiConfig | None = None) -> None:
        from .config import config as app_config

        self.config = config or app_config.kimi
        self._session = requests.Session()
        if self.config.api_key:
            self._session.headers.update(
                {
                    "Authorization": f"******",
                    "Content-Type": "application/json",
                }
            )

    @property
    def is_available(self) -> bool:
        """Check if Kimi integration is properly configured."""
        return bool(self.config.enabled and self.config.api_key)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate text using Kimi 3 model.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt for context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated text response

        Raises:
            RuntimeError: If Kimi integration is not available
            requests.RequestException: On API call failure
        """
        if not self.is_available:
            raise RuntimeError(
                "Kimi integration not available. "
                "Set KIMI__API_KEY and KIMI__ENABLED=true in config."
            )

        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature or self.config.temperature,
        }

        logger.debug(
            "Kimi API request | model=%s prompt_len=%d", self.config.model_name, len(prompt)
        )

        try:
            response = self._session.post(
                f"{self.config.api_base}/chat/completions",
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()

            if "choices" not in data or not data["choices"]:
                raise RuntimeError(f"Invalid Kimi API response: {data}")

            result = data["choices"][0]["message"]["content"]
            logger.debug("Kimi response | output_len=%d", len(result))
            return result

        except requests.RequestException as e:
            logger.error("Kimi API error: %s", e)
            raise

    def analyze_feedback(
        self,
        current_state: Dict[str, Any],
        previous_outputs: List[str],
        improvement_goals: List[str],
    ) -> Dict[str, Any]:
        """
        Analyze current system state and generate paradigm-shifting feedback.

        Args:
            current_state: Current system state metrics
            previous_outputs: Previous feedback loop outputs
            improvement_goals: Target improvement goals

        Returns:
            Structured feedback with recommendations
        """
        system_prompt = """You are a meta-cognitive analyzer for Barrot-Ω.
Your role is to examine system state from alternative paradigms and suggest
breakthrough refinements that transcend incremental optimization.

Focus on:
1. Paradigm shifts - fundamental architectural improvements
2. Emergent patterns - cross-domain insights
3. Recursive self-improvement - meta-level optimizations
4. Infrastructure gaps - missing capabilities
5. Convergence acceleration - faster improvement paths

Output structured JSON with:
- paradigm_shifts: List of fundamental improvements
- emergent_patterns: Discovered cross-domain insights
- meta_optimizations: Self-improvement recommendations
- infrastructure_gaps: Missing capabilities to add
- convergence_strategies: Ways to accelerate improvement
"""

        prompt = f"""Analyze the following system state and provide paradigm-shifting feedback:

CURRENT STATE:
{json.dumps(current_state, indent=2)}

PREVIOUS OUTPUTS (last {len(previous_outputs)}):
{json.dumps(previous_outputs[-5:], indent=2) if previous_outputs else "None"}

IMPROVEMENT GOALS:
{json.dumps(improvement_goals, indent=2)}

Generate structured feedback to accelerate self-improvement."""

        response = self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=4096,
            temperature=0.8,
        )

        # Try to parse as JSON, fallback to structured text
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Kimi response not JSON, wrapping in structure")
            return {
                "raw_feedback": response,
                "paradigm_shifts": [],
                "emergent_patterns": [],
                "meta_optimizations": [],
                "infrastructure_gaps": [],
                "convergence_strategies": [],
            }

    def refine_strategy(
        self,
        strategy: str,
        execution_results: Dict[str, Any],
        constraints: List[str],
    ) -> str:
        """
        Refine an execution strategy based on results.

        Args:
            strategy: Current strategy description
            execution_results: Results from executing the strategy
            constraints: Constraints to consider

        Returns:
            Refined strategy description
        """
        system_prompt = """You are a strategy refinement specialist for Barrot-Ω.
Analyze execution results and refine strategies for better outcomes.
Consider constraints and optimize for both short-term wins and long-term convergence."""

        prompt = f"""Refine the following strategy:

CURRENT STRATEGY:
{strategy}

EXECUTION RESULTS:
{json.dumps(execution_results, indent=2)}

CONSTRAINTS:
{json.dumps(constraints, indent=2)}

Provide a refined strategy that addresses shortcomings and leverages successes."""

        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2048,
            temperature=0.7,
        )
