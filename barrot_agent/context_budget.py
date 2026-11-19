"""Conservative preflight budget for model requests.

This is a deterministic character-based estimate, not a provider tokenizer.
It deliberately leaves headroom for output tokens and provider-side message
framing so oversized work is blocked before an external request is sent.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

CHARS_PER_ESTIMATED_TOKEN = 2
MESSAGE_OVERHEAD_TOKENS = 16
MAX_ESTIMATED_INPUT_TOKENS = 4800
MAX_RESERVED_OUTPUT_TOKENS = 2048
MAX_ESTIMATED_TOTAL_TOKENS = 7000


def estimate_messages_tokens(messages: Iterable[Mapping[str, Any]]) -> int:
    """Return a conservative estimate for system, history and user messages."""
    estimate = 0
    for message in messages:
        content = message.get("content", "")
        text = content if isinstance(content, str) else "" if content is None else str(content)
        estimate += (len(text) + CHARS_PER_ESTIMATED_TOKEN - 1) // CHARS_PER_ESTIMATED_TOKEN
        estimate += MESSAGE_OVERHEAD_TOKENS
    return estimate


def exceeds_context_budget(
    messages: Iterable[Mapping[str, Any]],
    *,
    reserved_output_tokens: int = MAX_RESERVED_OUTPUT_TOKENS,
) -> tuple[bool, int]:
    """Return whether the conservative input plus reserved output exceeds budget."""
    estimated_input = estimate_messages_tokens(messages)
    exceeded = (
        estimated_input > MAX_ESTIMATED_INPUT_TOKENS
        or estimated_input + reserved_output_tokens > MAX_ESTIMATED_TOTAL_TOKENS
    )
    return exceeded, estimated_input


def context_budget_marker(estimated_input_tokens: int) -> str:
    """Stable marker consumed by the repair planner as a blocked result."""
    return (
        "[BARROT_CONTEXT_BUDGET_EXCEEDED] "
        f"estimated_input_tokens={estimated_input_tokens}; "
        f"max_input_tokens={MAX_ESTIMATED_INPUT_TOKENS}; "
        f"reserved_output_tokens={MAX_RESERVED_OUTPUT_TOKENS}; "
        f"max_total_tokens={MAX_ESTIMATED_TOTAL_TOKENS}; "
        "conservative character estimate, not provider tokenization; "
        "no provider request was sent and no repository mutation was attempted."
    )
