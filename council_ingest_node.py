#!/usr/bin/env python3
# ==============================================================================
# BARROT-Ω INGESTION & REASONING NODE
# Architect: Sean | Node: Brooklyn Core
# Objective: Autonomous Parsing and Orchestrator JSON Injection
# ==============================================================================

import os
import re
import logging
import sys
import json
from datetime import datetime, timezone


class CouncilIngestionEngine:
    def __init__(self):
        self.report_path = "COUNCIL_REVIEW.md"
        self.state_path = "council_weights.json"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - [BARROT-Ω REASONING] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger = logging.getLogger(__name__)

    def parse_physical_artifact(self):
        self.logger.info(f"Scanning substrate for {self.report_path}...")
        if not os.path.exists(self.report_path):
            self.logger.error("Artifact missing. Halting ingestion.")
            sys.exit(1)

        with open(self.report_path, "r") as file:
            content = file.read()

        try:
            asset = re.search(r"\*\*Target Asset:\*\* (\w+)", content).group(1)
            sentiment_match = re.search(r"Sentiment Score: ([\d\.]+)", content)
            sentiment = float(sentiment_match.group(1)) if sentiment_match else 0.0
            variance_match = re.search(r"\*\*Shear Variance:\*\* ([\d\.]+)", content)
            variance = float(variance_match.group(1)) if variance_match else 0.0

            return {"asset": asset, "sentiment": sentiment, "variance": variance}
        except Exception as e:
            self.logger.error(f"Failed to parse matrix parameters: {e}")
            sys.exit(1)

    def calculate_and_inject(self, metrics):
        self.logger.info("Metrics extracted. Calculating strategic directive...")

        if metrics["asset"] == "XRP" and metrics["sentiment"] >= 0.85:
            action = "MAX_ACCUMULATION_TRIGGERED"
            weight = 1.15  # Represents +15%
        elif metrics["variance"] > 0.5:
            action = "HIGH_SHEAR_DETECTED_HOLD"
            weight = 1.00
        else:
            action = "MAINTAIN_CURRENT_TRAJECTORY"
            weight = 1.00

        # Build the JSON payload for the AGI Orchestrator
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "target_asset": metrics["asset"],
            "council_action": action,
            "orchestrator_weight_multiplier": weight,
            "active_stability_anchor": 0.707,
        }

        with open(self.state_path, "w") as f:
            json.dump(payload, f, indent=4)

        self.logger.info(f"=== STRATEGIC INJECTION COMPLETE ===")
        self.logger.info(f"Action: {action}")
        self.logger.info(f"Payload successfully written to {self.state_path} for AGI Orchestrator.")


if __name__ == "__main__":
    engine = CouncilIngestionEngine()
    data = engine.parse_physical_artifact()
    engine.calculate_and_inject(data)
