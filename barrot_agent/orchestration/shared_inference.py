#!/usr/bin/env python3
"""Shared OpenAI-compatible inference client for Barrot cloud and local providers."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any


class InferenceError(RuntimeError):
    """Provider selection or inference request failed."""


def _env(name: str) -> str:
    return os.getenv(name, "").strip()


def get_provider() -> dict[str, str]:
    """Resolve an explicitly selected provider or preserve the legacy cloud order.

    BARROT_INFERENCE_PROVIDER=local_llama selects the on-device llama.cpp server.
    With no explicit selection, legacy Groq-then-Fireworks behavior is preserved.
    """
    selected = _env("BARROT_INFERENCE_PROVIDER").lower() or "auto"
    if selected in {"local_llama", "llama", "local"}:
        return {
            "name": "local_llama",
            "api_key": "",
            "base_url": _env("LOCAL_LLAMA_BASE_URL") or "http://127.0.0.1:8081/v1",
            "default_model": _env("LOCAL_LLAMA_MODEL") or "local",
        }
    if selected not in {"auto", "groq", "fireworks"}:
        raise InferenceError(
            "Unsupported BARROT_INFERENCE_PROVIDER. Choose auto, groq, fireworks, or local_llama."
        )

    if selected in {"auto", "groq"}:
        groq_key = _env("GROQ_API_KEY")
        if groq_key:
            return {
                "name": "groq",
                "api_key": groq_key,
                "base_url": "https://api.groq.com/openai/v1",
                "default_model": _env("GROQ_MODEL") or "openai/gpt-oss-120b",
            }
        if selected == "groq":
            raise InferenceError("GROQ_API_KEY is not configured.")

    if selected in {"auto", "fireworks"}:
        fireworks_key = _env("FIREWORKS_API_KEY")
        if fireworks_key:
            return {
                "name": "fireworks",
                "api_key": fireworks_key,
                "base_url": _env("FIREWORKS_BASE_URL")
                or "https://api.fireworks.ai/inference/v1",
                "default_model": _env("FIREWORKS_MODEL"),
            }
        if selected == "fireworks":
            raise InferenceError("FIREWORKS_API_KEY is not configured.")

    raise InferenceError(
        "No inference provider configured. Set GROQ_API_KEY or FIREWORKS_API_KEY, "
        "or select BARROT_INFERENCE_PROVIDER=local_llama."
    )


def chat(
    messages: list[dict[str, Any]],
    *,
    model: str | None = None,
    max_tokens: int = 1200,
    temperature: float = 0.3,
    timeout: int = 90,
) -> str:
    """Send an OpenAI-compatible chat completion request and return text."""
    provider = get_provider()
    payload: dict[str, Any] = {
        "model": model or provider["default_model"] or "local",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Barrot/1.0",
    }
    if provider["api_key"]:
        headers["Authorization"] = f"Bearer {provider['api_key']}"

    url = provider["base_url"].rstrip("/") + "/chat/completions"
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers
    )

    for attempt in range(2):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:400]
            if exc.code == 429 and attempt == 0:
                retry_after = exc.headers.get("Retry-After", "")
                try:
                    delay = min(30.0, max(0.0, float(retry_after)))
                except (TypeError, ValueError):
                    delay = 1.0
                time.sleep(delay)
                continue
            raise InferenceError(
                f"{provider['name']} HTTP {exc.code}: {detail}"
            ) from exc
        except Exception as exc:
            raise InferenceError(
                f"{provider['name']} request failed: {type(exc).__name__}: {exc}"
            ) from exc
    else:
        raise InferenceError(f"{provider['name']} rate limit retry exhausted")

    try:
        message = data["choices"][0]["message"]
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str) or not content.strip():
            raise InferenceError(
                f"{provider['name']} returned no text completion; "
                "this text-only client does not execute tool calls."
            )
        return content.strip()
    except InferenceError:
        raise
    except (KeyError, IndexError, TypeError) as exc:
        raise InferenceError(
            f"Unexpected response from {provider['name']}: {str(data)[:400]}"
        ) from exc


def ask(
    prompt: str,
    *,
    system: str | None = None,
    **kwargs: Any,
) -> str:
    """Convenience wrapper for single-prompt requests."""
    messages: list[dict[str, Any]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return chat(messages, **kwargs)
