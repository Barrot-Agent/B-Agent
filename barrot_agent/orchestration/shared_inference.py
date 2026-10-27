#!/usr/bin/env python3
"""
Shared inference client for Barrot.

Centralizes provider credentials and OpenAI-compatible chat requests.
Existing scripts can migrate here incrementally.
"""

from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from typing import Any


class InferenceError(RuntimeError):
    pass


def _env(name: str) -> str:
    return os.getenv(name, "").strip()


def get_provider() -> dict[str, str]:
    """Return the first configured inference provider."""

    groq_key = _env("GROQ_API_KEY")
    if groq_key:
        return {
            "name": "groq",
            "api_key": groq_key,
            "base_url": "https://api.groq.com/openai/v1",
            "default_model": _env("GROQ_MODEL") or "openai/gpt-oss-120b",
        }

    fireworks_key = _env("FIREWORKS_API_KEY")
    if fireworks_key:
        return {
            "name": "fireworks",
            "api_key": fireworks_key,
            "base_url": _env("FIREWORKS_BASE_URL")
            or "https://api.fireworks.ai/inference/v1",
            "default_model": _env("FIREWORKS_MODEL"),
        }

    raise InferenceError(
        "No inference provider configured. "
        "Set GROQ_API_KEY or FIREWORKS_API_KEY."
    )


def chat(
    messages: list[dict[str, str]],
    *,
    model: str | None = None,
    max_tokens: int = 1200,
    temperature: float = 0.3,
    timeout: int = 90,
) -> str:
    """Send an OpenAI-compatible chat completion request."""

    provider = get_provider()

    payload: dict[str, Any] = {
        "model": model or provider["default_model"],
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    url = provider["base_url"].rstrip("/") + "/chat/completions"

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {provider['api_key']}",
            "Content-Type": "application/json",
            "User-Agent": "Barrot/1.0",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise InferenceError(
            f"{provider['name']} HTTP {exc.code}: {detail}"
        ) from exc
    except Exception as exc:
        raise InferenceError(
            f"{provider['name']} request failed: {exc}"
        ) from exc

    try:
        message = data["choices"][0]["message"]
        content = message.get("content") if isinstance(message, dict) else None

        if not isinstance(content, str) or not content.strip():
            raise InferenceError(
                f"{provider['name']} returned an empty completion"
            )

        return content.strip()

    except InferenceError:
        raise
    except (KeyError, IndexError, TypeError) as exc:
        raise InferenceError(
            f"Unexpected response from {provider['name']}: "
            f"{str(data)[:500]}"
        ) from exc


def ask(
    prompt: str,
    *,
    system: str | None = None,
    **kwargs: Any,
) -> str:
    """Convenience wrapper for single-prompt requests."""

    messages: list[dict[str, str]] = []

    if system:
        messages.append({"role": "system", "content": system})

    messages.append({"role": "user", "content": prompt})

    return chat(messages, **kwargs)
