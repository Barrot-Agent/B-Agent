"""
Reactive observers for Barrot's Cognitive Event Bus.

Observers evaluate completed work automatically while remaining non-invasive:
they document integrity signals but never modify an inference response.
"""

from __future__ import annotations

import logging
from typing import Any

from barrot_agent.evolution.corroboration import CrossCorroborationEngine
from barrot_agent.evolution.event_bus import CognitiveEvent, CognitiveEventBus

logger = logging.getLogger(__name__)


class ReactiveCorroborationObserver:
    """Automatically evaluate selected cognitive events for corroboration."""

    def __init__(self) -> None:
        self.corroboration = CrossCorroborationEngine()

    def observe(self, event: CognitiveEvent) -> dict[str, Any]:
        """Evaluate event evidence without changing the originating result."""
        claim = event.payload.get("claim")

        # Inference events intentionally contain hashes rather than full
        # responses, so they are documented without duplicating response data.
        if not claim:
            return {
                "status": "no_claim_to_corroborate",
                "event_type": event.event_type,
            }

        return self.corroboration.corroborate(
            {"claim": claim},
            sources=[event.source],
        )

    def register(self, bus: CognitiveEventBus) -> None:
        """Attach this observer to evidence-producing events."""
        bus.subscribe("research_acquired", self.observe)
        bus.subscribe("claim_submitted", self.observe)
