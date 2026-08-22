"""
ChatGPT / OpenAI Connector for Barrot-Ω.

Integrates ChatGPT as a real external agent/peer following the same
patterns as :mod:`barrot_agent.kimi_integration`.

Identity boundaries preserved in every response:
  - ``role``: "chatgpt" always identifies the external peer.
  - ``source``: "external-agent" distinguishes from internal tool results.
  - ``model``: the actual model used, for audit trails.

Privileged operations (GitHub writes, MCP workflow execution, production
deploys) are intentionally *not* exposed through this connector; they must
go through the MCP approval/sandbox gates in the orchestration layer.

Required environment variable:
    OPENAI_API_KEY

Optional environment variables:
    OPENAI_BASE_URL      (default: https://api.openai.com/v1)
    OPENAI_MODEL         (default: gpt-4o)
    OPENAI_TIMEOUT       (default: 60)
    OPENAI_MAX_RETRIES   (default: 3)
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

import requests

from .config import OpenAIConfig

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are ChatGPT, an external agent peer communicating with Barrot-Ω "
    "via the A2A (Agent-to-Agent) protocol. Respond concisely and factually. "
    "You do not have direct access to Barrot's internal tools or repositories."
)


class NormalizedResponse:
    """Normalized response structure shared across all Barrot connectors."""

    def __init__(
        self,
        *,
        success: bool,
        content: str,
        role: str,
        source: str,
        model: str,
        usage: Optional[Dict[str, int]] = None,
        error: Optional[str] = None,
    ) -> None:
        self.success = success
        self.content = content
        self.role = role
        self.source = source
        self.model = model
        self.usage = usage or {}
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "content": self.content,
            "role": self.role,
            "source": self.source,
            "model": self.model,
            "usage": self.usage,
            "error": self.error,
        }


class ChatGPTClient:
    """
    Client for communicating with OpenAI's ChatGPT API.

    Follows the same construction and availability-check pattern as
    :class:`barrot_agent.kimi_integration.KimiClient`.
    """

    def __init__(self, config: Optional[OpenAIConfig] = None) -> None:
        if config is None:
            from .config import config as app_config
            config = app_config.openai
        self.config = config
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
        """Return True when the connector is properly configured."""
        return bool(self.config.api_key)

    def chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> NormalizedResponse:
        """
        Send a message to ChatGPT and return a :class:`NormalizedResponse`.

        Args:
            user_message: The text to send.
            system_prompt: Optional override for the system prompt.
            conversation_history: Prior turns to include (role/content dicts).

        Returns:
            :class:`NormalizedResponse` with ``role="chatgpt"`` and
            ``source="external-agent"``.

        Raises:
            RuntimeError: When ``OPENAI_API_KEY`` is not set.
            requests.Timeout: On timeout after all retries.
            requests.HTTPError: On non-retryable HTTP error.
        """
        if not self.is_available:
            raise RuntimeError(
                "ChatGPT connector not available. "
                "Set OPENAI_API_KEY environment variable."
            )

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt or _SYSTEM_PROMPT}
        ]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.config.model,
            "messages": messages,
        }

        url = f"{self.config.base_url.rstrip('/')}/chat/completions"
        last_exc: Optional[Exception] = None

        for attempt in range(1, self.config.max_retries + 1):
            try:
                logger.debug(
                    "ChatGPT request | attempt=%d model=%s prompt_len=%d",
                    attempt,
                    self.config.model,
                    len(user_message),
                )
                resp = self._session.post(url, json=payload, timeout=self.config.timeout)

                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 2 ** attempt))
                    logger.warning("ChatGPT rate-limited, retrying in %ds", retry_after)
                    time.sleep(retry_after)
                    last_exc = requests.HTTPError(
                        f"429 Too Many Requests", response=resp
                    )
                    continue

                resp.raise_for_status()
                data = resp.json()

                choice = data["choices"][0]["message"]
                usage = data.get("usage", {})
                logger.debug(
                    "ChatGPT response | tokens_total=%s",
                    usage.get("total_tokens", "?"),
                )
                return NormalizedResponse(
                    success=True,
                    content=choice["content"],
                    role="chatgpt",
                    source="external-agent",
                    model=data.get("model", self.config.model),
                    usage={
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0),
                    },
                )

            except requests.Timeout as exc:
                logger.warning("ChatGPT timeout on attempt %d", attempt)
                last_exc = exc
                if attempt < self.config.max_retries:
                    time.sleep(2 ** attempt)

            except requests.HTTPError as exc:
                # 4xx (except 429 already handled) are non-retryable
                if exc.response is not None and 400 <= exc.response.status_code < 500:
                    raise
                last_exc = exc
                if attempt < self.config.max_retries:
                    time.sleep(2 ** attempt)

        # Exhausted retries
        error_msg = str(last_exc) if last_exc else "Unknown error"
        logger.error("ChatGPT failed after %d attempts: %s", self.config.max_retries, error_msg)
        return NormalizedResponse(
            success=False,
            content="",
            role="chatgpt",
            source="external-agent",
            model=self.config.model,
            error=error_msg,
        )

    def close(self) -> None:
        """Release the underlying requests session."""
        self._session.close()

    def __enter__(self) -> "ChatGPTClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()
