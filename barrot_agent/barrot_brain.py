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
                return r.json()["choices"][0]["message"]["content"]
            except Exception as e:
                pass  # fall through to Groq

        # Groq fallback
        if self.groq_key:
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
                return r.json()["choices"][0]["message"]["content"]
            except Exception as e:
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
                return r.json()["choices"][0]["message"]["content"]
            except:
                pass
        return f"[BARROT] All backends failed: {e}"

        return "[BARROT] No inference backend. Set GITHUB_APP credentials or GROQ_API_KEY."

    @property
    def backend(self) -> str:
        if self.auth.ready:
            return "GitHub Models"
        if self.groq_key:
            return "Groq Llama 3.1 70B"
        return "None"
