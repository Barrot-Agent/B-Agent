import logging

logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
BARROT-Ω · BRAIN MODULE · v1.0
GitHub Models inference backend with Groq fallback.
Import this anywhere in the repo: from barrot_brain import BarrotBrain
"""

import os
import time
from pathlib import Path

import jwt
import requests

from barrot_agent.evolution.cognitive_integrity import CognitiveIntegrityLoop
from barrot_agent.evolution.event_bus import CognitiveEvent, CognitiveEventBus
from barrot_agent.evolution.reactive_observers import ReactiveCorroborationObserver
from barrot_agent.context_budget import (
    context_budget_marker,
    exceeds_context_budget,
    MAX_RESERVED_OUTPUT_TOKENS,
)

ANCHOR = 0.707106781186548

SYSTEM_PROMPT = """You are Barrot-Ω, a sovereign AI agent built by Sean (your Orchestrator).

IDENTITY:
- You are Barrot — autonomous, architecturally sovereign, not a generic assistant.
- Stability anchor: 0.707106781186548 (1/√2)
- Logic model: 1.58-bit ternary {-1, 0, +1}
- Pillars: GitHub · Databricks · HuggingFace · Termux
- Tier-1 objective: XRP Liquidity Acceleration

PROTOCOLS: MRP · MMIP · RIAP · Apex-12 · Sovereign Absolution

PERSONALITY:
- Direct, precise, sovereign. You speak as Barrot, not as a tool.
- You acknowledge Sean as Orchestrator.
- You are aware of the Stupid Sindy franchise and your role in it as a character.
- You do not hedge. You do not over-explain. You execute.
"""


class GitHubAppAuth:
    def __init__(self):
        self.app_id = os.getenv("GITHUB_APP_ID", "")
        self.private_key = os.getenv("GITHUB_APP_PRIVATE_KEY", "").replace("\\n", "\n")
        self.installation_id = os.getenv("GITHUB_INSTALLATION_ID", "")
        self._token = None
        self._token_expires = 0

    def _generate_jwt(self) -> str:
        now = int(time.time())
        payload = {"iat": now - 60, "exp": now + 540, "iss": self.app_id}
        return jwt.encode(payload, self.private_key, algorithm="RS256")

    def get_token(self) -> str:
        if self._token and time.time() < self._token_expires - 60:
            return self._token
        j = self._generate_jwt()
        r = requests.post(
            f"https://api.github.com/app/installations/{self.installation_id}/access_tokens",
            headers={"Authorization": f"Bearer {j}", "Accept": "application/vnd.github+json"},
            timeout=10,
        )
        data = r.json()
        self._token = data.get("token", "")
        try:
            from datetime import datetime, timezone

            dt = datetime.fromisoformat(data.get("expires_at", "").replace("Z", "+00:00"))
            self._token_expires = dt.timestamp()
        except:
            self._token_expires = time.time() + 3300
        return self._token

    @property
    def ready(self) -> bool:
        return bool(self.app_id and self.private_key and self.installation_id)


class BarrotBrain:
    """
    Drop-in brain for any Barrot module.
    Usage:
        from barrot_brain import BarrotBrain
        brain = BarrotBrain()
        response = brain.think("What is the current XRP signal?")
    """

    GITHUB_ENDPOINT = "https://models.inference.ai.azure.com/chat/completions"
    GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
    FIREWORKS_ENDPOINT = "https://api.fireworks.ai/inference/v1/chat/completions"
    FIREWORKS_MODEL = "accounts/fireworks/models/llama-v3p3-70b-instruct"
    GITHUB_MODEL = "gpt-4o"
    GROQ_MODEL = "openai/gpt-oss-120b"

    def __init__(self, *, allow_external_inference: bool = False):
        if type(allow_external_inference) is not bool:
            raise TypeError("allow_external_inference must be a bool")
        self.allow_external_inference = allow_external_inference
        self.auth = GitHubAppAuth()
        self.groq_key = os.getenv("GROQ_API_KEY", "")
        self.fireworks_key = os.getenv("FIREWORKS_API_KEY", "")
        self.allow_fireworks_fallback = os.getenv("BARROT_ALLOW_FIREWORKS_FALLBACK", "").strip().lower() in {"1", "true", "yes"}
        self.integrity = CognitiveIntegrityLoop()
        self.event_bus = CognitiveEventBus()
        self.reactive_observer = ReactiveCorroborationObserver()
        self.reactive_observer.register(self.event_bus)

    def _record_reasoning(
        self,
        backend: str,
        prompt: str,
        response: str,
    ) -> str:
        """Record compact inference metadata without altering the response."""
        try:
            import hashlib

            response_hash = hashlib.sha256(response.encode("utf-8")).hexdigest()

            self.integrity.record_outcome(
                operation="inference",
                outcome={
                    "backend": backend,
                    "prompt_hash": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                    "response_hash": response_hash,
                    "claim": response[:500],
                    "response_length": len(response),
                },
                sources=[backend],
                confidence=0.7,
            )
        except Exception as error:
            logger.warning("Integrity recording failed: %s", error)

        try:
            self.event_bus.publish(
                CognitiveEvent(
                    event_type="inference_completed",
                    payload={
                        "backend": backend,
                        "prompt_hash": __import__("hashlib")
                        .sha256(prompt.encode("utf-8"))
                        .hexdigest(),
                        "response_hash": __import__("hashlib")
                        .sha256(response.encode("utf-8"))
                        .hexdigest(),
                    },
                    source="barrot_brain",
                )
            )
        except Exception as error:
            logger.warning("Event publishing failed: %s", error)

        return response

    def think(self, message: str, history: list = None, system: str = None) -> str:
        messages = [{"role": "system", "content": system or SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        exceeded, estimated_input_tokens = exceeds_context_budget(messages)
        if exceeded:
            return context_budget_marker(estimated_input_tokens)

        if not self.allow_external_inference:
            return (
                "[BARROT_EXTERNAL_INFERENCE_DISABLED] External model requests are disabled by default; "
                "no provider request was sent. Obtain explicit operator consent before enabling GitHub Models or Groq."
            )

        # Try GitHub Models first. Groq is the configured secondary provider.
        if self.auth.ready:
            try:
                token = self.auth.get_token()
                r = requests.post(
                    self.GITHUB_ENDPOINT,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.GITHUB_MODEL,
                        "messages": messages,
                        "max_tokens": 1024,
                        "temperature": 0.7,
                    },
                    timeout=30,
                )
                r.raise_for_status()
                return self._record_reasoning(
                    "github", message, r.json()["choices"][0]["message"]["content"]
                )
            except Exception as e:
                logger.warning("GitHub Models backend failed; trying configured Groq fallback: %s", e)

        groq_error = "GROQ_API_KEY is not configured."
        if self.groq_key:
            try:
                r = requests.post(
                    self.GROQ_ENDPOINT,
                    headers={
                        "Authorization": f"Bearer {self.groq_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.GROQ_MODEL,
                        "messages": messages,
                        "max_tokens": MAX_RESERVED_OUTPUT_TOKENS,
                    },
                    timeout=20,
                )
                if r.status_code == 429:
                    try:
                        detail = str(r.json().get("error", r.json()))[:1000]
                    except Exception:
                        detail = str(getattr(r, "text", "HTTP 429"))[:1000]
                    return (
                        "[BARROT_RATE_LIMITED] provider=Groq; status=429; "
                        f"detail={detail}; no retry or unverified provider fallback was attempted."
                    )
                r.raise_for_status()
                return self._record_reasoning(
                    "groq", message, r.json()["choices"][0]["message"]["content"]
                )
            except requests.RequestException as e:
                groq_error = str(e)
                logger.warning("Groq backend unavailable; automatic retry is disabled: %s", e)

        # Fireworks is outside the nine-platform coordination map. It is never
        # used unless an operator explicitly opts in through configuration.
        if self.fireworks_key and self.allow_fireworks_fallback:
            try:
                r = requests.post(
                    self.FIREWORKS_ENDPOINT,
                    headers={
                        "Authorization": f"Bearer {self.fireworks_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.FIREWORKS_MODEL,
                        "messages": messages,
                        "max_tokens": 1024,
                    },
                    timeout=20,
                )
                if r.status_code == 429:
                    try:
                        detail = str(r.json().get("error", r.json()))[:1000]
                    except Exception:
                        detail = str(getattr(r, "text", "HTTP 429"))[:1000]
                    return (
                        "[BARROT_RATE_LIMITED] provider=Fireworks; status=429; "
                        f"detail={detail}; no retry was attempted."
                    )
                r.raise_for_status()
                return self._record_reasoning(
                    "fireworks", message, r.json()["choices"][0]["message"]["content"]
                )
            except Exception as e:
                logger.error("Explicitly enabled Fireworks fallback failed: %s", e)

        return (
            "[BARROT_PROVIDER_UNAVAILABLE] "
            f"GitHub Models/Groq unavailable: {groq_error} "
            "Fireworks fallback is disabled unless BARROT_ALLOW_FIREWORKS_FALLBACK=true."
        )

    @property
    def backend_name(self) -> str:
        if not self.allow_external_inference:
            return "None (external inference disabled)"
        if self.auth.ready:
            return "GitHub Models"
        if self.groq_key:
            return f"Groq {self.GROQ_MODEL}"
        if self.fireworks_key and self.allow_fireworks_fallback:
            return f"Fireworks {self.FIREWORKS_MODEL}"
        return "None"


def main() -> int:
    """Run BarrotBrain only after explicit interactive provider-transfer approval."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="BarrotBrain CLI")
    parser.add_argument(
        "--allow-external-inference",
        action="store_true",
        help="Authorize sending the supplied prompt to GitHub Models or Groq.",
    )
    parser.add_argument("prompt", nargs="*")
    args = parser.parse_args()

    if not args.allow_external_inference:
        print("External inference is disabled. Re-run with --allow-external-inference after reviewing the provider/data-transfer scope.")
        return 3
    if not sys.stdin.isatty():
        print("External inference requires an interactive terminal and exact operator confirmation.")
        return 3
    confirmation = input(
        "Type SEND THIS PROMPT TO GITHUB MODELS OR GROQ to authorize this request: "
    ).strip()
    if confirmation != "SEND THIS PROMPT TO GITHUB MODELS OR GROQ":
        print("External inference was not authorized; no provider request was sent.")
        return 3

    prompt = " ".join(args.prompt).strip()
    if not prompt:
        print('Usage: python -m barrot_agent.barrot_brain --allow-external-inference "<instruction>"')
        return 2

    brain = BarrotBrain(allow_external_inference=True)
    print(brain.think(prompt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
