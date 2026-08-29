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
    GROQ_MODEL = "llama-3.3-70b-versatile"

    def __init__(self):
        self.auth = GitHubAppAuth()
        self.groq_key = os.getenv("GROQ_API_KEY", "")
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

        # Try GitHub Models first
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
                logger.warning("GitHub Models backend failed, falling back to Groq: %s", e)

        # Groq fallback with rate-limit retry
        if self.groq_key:
            import random

            for attempt in range(6):
                try:
                    r = requests.post(
                        self.GROQ_ENDPOINT,
                        headers={
                            "Authorization": f"Bearer {self.groq_key}",
                            "Content-Type": "application/json",
                        },
                        json={"model": self.GROQ_MODEL, "messages": messages, "max_tokens": 1024},
                        timeout=20,
                    )
                    if r.status_code == 429 and attempt < 5:
                        wait = min(60, 2**attempt) + random.uniform(0, 1)
                        logger.warning("Groq rate-limited; retrying in %.1fs", wait)
                        time.sleep(wait)
                        continue
                    r.raise_for_status()
                    return self._record_reasoning(
                        "groq", message, r.json()["choices"][0]["message"]["content"]
                    )
                except requests.RequestException as e:
                    if attempt == 5:
                        logger.warning("Groq backend failed, falling back to Fireworks: %s", e)
                        break
                    wait = min(60, 2**attempt) + random.uniform(0, 1)
                    logger.warning("Groq request failed; retrying in %.1fs: %s", wait, e)
                    time.sleep(wait)
            # fall through to Fireworks

        # Fireworks fallback
        fw_key = os.getenv("FIREWORKS_API_KEY", "")
        if fw_key:
            try:
                r = requests.post(
                    self.FIREWORKS_ENDPOINT,
                    headers={
                        "Authorization": f"Bearer {fw_key}",
                        "Content-Type": "application/json",
                    },
                    json={"model": self.FIREWORKS_MODEL, "messages": messages, "max_tokens": 1024},
                    timeout=20,
                )
                r.raise_for_status()
                return self._record_reasoning(
                    "fireworks", message, r.json()["choices"][0]["message"]["content"]
                )
            except Exception as e:
                logger.error("Fireworks backend failed: %s", e)
        logger.error("All backends failed for this request.")
        return "[BARROT] All backends failed."

    @property
    def backend(self) -> str:
        if self.auth.ready:
            return "GitHub Models"
        if self.groq_key:
            return "Groq Llama 3.1 70B"
        return "None"
