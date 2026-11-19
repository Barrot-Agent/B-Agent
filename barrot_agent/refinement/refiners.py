"""Refiner adapters for the ping-pong refinement engine.

Two families:
- OpenCodeRefiner: live model via the OpenAI-compatible OpenCode inference API
  (model passed by name; never logs or echoes the API key).
- HeuristicRefiner: fully deterministic offline refiner — dedupes lists,
  trims vague placeholders, normalizes whitespace. Guarantees a fixed point
  (returns CONVERGED when its pass changes nothing), which makes the whole
  engine testable and keyless-environment safe.

Every refiner returns a RefinementOutput with a machine-readable verdict so
the engine can decide fixed-point convergence, not the model's mood.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from . import scoring

OPENCODE_BASE = "https://opencode.ai/inference/openai/v1"
DEFAULT_MODELS = (
    "deepseek-v4.1-flash-free",
)

REFINE_SYSTEM = (
    "You are a data-refinement worker in a ping-pong refinement loop. "
    "Improve the GIVEN DATA: fix inconsistencies, remove redundancy, fill "
    "gaps with explicit values, drop unsupported claims, keep structure. "
    "Technique over style. Never invent facts. Reply with STRICT JSON only: "
    '{"data": <refined data>, "verdict": "REFINED"|"CONVERGED", "notes": "<=200 chars"} '
    'Use verdict CONVERGED only when no further meaningful refinement is possible.'
)

CRITIQUE_SYSTEM = (
    "You are the critique side of a ping-pong refinement loop. Examine the "
    "GIVEN DATA and the previous refinement. State what is still wrong, "
    "missing, unsupported, or redundant. Reply with STRICT JSON only: "
    '{"critique": "<=400 chars", "verdict": "REFINE"|"CONVERGED"} '
    'Use verdict CONVERGED only if nothing meaningful remains to fix.'
)


@dataclass
class RefinementOutput:
    actor: str
    role: str                 # "refine" | "critique"
    verdict: str              # "REFINED" | "CONVERGED" | "FAILED"
    data: Any = None          # refined data (refine role)
    critique: str = ""        # critique text (critique role)
    notes: str = ""
    meta: dict = field(default_factory=dict)


class Refiner(ABC):
    name: str = "refiner"

    @abstractmethod
    def refine(self, data: Any, critique: str | None) -> RefinementOutput:
        """One refinement pass over data, optionally guided by the other
        side's critique."""

    @abstractmethod
    def critique(self, data: Any) -> RefinementOutput:
        """One critique pass over data (no rewrite)."""


# ------------------------------------------------------------------ live API
class OpenCodeRefiner(Refiner):
    """OpenAI-compatible chat refiner backed by OpenCode inference."""

    def __init__(self, model: str, api_key: str | None = None,
                 base_url: str = OPENCODE_BASE, timeout: int = 120,
                 max_tokens: int = 3000, temperature: float = 0.1):
        self.name = f"opencode:{model}"
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.api_key = api_key if api_key is not None else os.environ.get("OPENCODE_API_KEY", "public")
        self.calls = 0
        self.errors = 0

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def _budget(self, payload_chars: int) -> int:
        """Output token budget: room for the model's reasoning phase (which
        alone can burn several thousand tokens) plus the full strict-JSON
        echo of the data (JSON ≈ 1 token per ~2.5-3 chars)."""
        return max(self.max_tokens, min(16000, payload_chars // 2 + 6000))

    def _chat_parts(self, system: str, user: str,
                    max_tokens: int | None = None) -> tuple[str, str, str]:
        """Returns (content, reasoning_content, finish_reason) — reasoning
        models may put the strict-JSON payload in either text field.
        Transient transport errors (timeouts, connection resets, HTTP
        429/5xx) are retried with exponential backoff, up to 3 attempts
        total; permanent HTTP errors (4xx other than 429) surface
        immediately."""
        body = json.dumps({
            "model": self.model,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "max_tokens": max_tokens or self._budget(len(user)),
            "temperature": self.temperature,
        }).encode()
        last_exc: Exception | None = None
        for attempt in range(3):
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions", data=body,
                headers={"Authorization": f"Bearer {self.api_key}",
                         "Content-Type": "application/json",
                         "User-Agent": "barrot-refinement/1.0"})
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    payload = json.load(resp)
            except urllib.error.HTTPError as exc:
                if exc.code != 429 and not 500 <= exc.code < 600:
                    raise                     # permanent — not worth retrying
                last_exc = exc
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_exc = exc
            else:
                self.calls += 1
                choice = payload["choices"][0]
                msg = choice["message"]
                return (msg.get("content") or "",
                        str(msg.get("reasoning_content") or ""),
                        str(choice.get("finish_reason") or ""))
            if attempt < 2:
                time.sleep(0.5 * (2 ** attempt))    # 0.5s, then 1.0s
        assert last_exc is not None
        raise last_exc

    # -- strict-JSON extraction (handles fences / preamble) ---------------
    @staticmethod
    def _extract_json(text: str) -> dict | None:
        text = text.strip()
        if not text:
            return None
        fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
        if fence:
            text = fence.group(1).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        brace = re.search(r"\{.*\}", text, re.DOTALL)
        if brace:
            try:
                return json.loads(brace.group(0))
            except json.JSONDecodeError:
                return None
        return None

    def _complete(self, system: str, user: str) -> tuple[dict | None, str]:
        """One chat completion + strict-JSON parse. If the response was
        truncated (finish_reason=length, the classic failure on larger
        documents), retries once with a doubled output budget."""
        content, reasoning, finish = self._chat_parts(system, user)
        parsed = self._extract_json(content) or self._extract_json(reasoning)
        if parsed is None and finish == "length":
            bigger = min(self._budget(len(user)) * 2, 32000)
            content, reasoning, finish = self._chat_parts(
                system, user, max_tokens=bigger)
            parsed = self._extract_json(content) or self._extract_json(reasoning)
        return parsed, finish

    def complete_json(self, system: str, user: str) -> tuple[dict | None, str]:
        """Public strict-JSON completion for protocol consumers other than
        the refine/critique roles (e.g. the independent semantic judge).
        Same retry + truncation-retry behavior."""
        return self._complete(system, user)

    def refine(self, data: Any, critique: str | None) -> RefinementOutput:
        user = ("PREVIOUS CRITIQUE (address every point):\n"
                f"{critique or '(none — first pass)'}\n\nDATA:\n"
                + json.dumps(data, ensure_ascii=False)[:24000])
        try:
            parsed, finish = self._complete(REFINE_SYSTEM, user)
        except (urllib.error.URLError, OSError, ValueError, KeyError) as exc:
            self.errors += 1
            return RefinementOutput(self.name, "refine", "FAILED",
                                    notes=f"{type(exc).__name__}: {exc}"[:200])
        if not parsed or "data" not in parsed:
            self.errors += 1
            return RefinementOutput(self.name, "refine", "FAILED",
                                    notes="unparseable model output",
                                    meta={"finish_reason": finish})
        verdict = str(parsed.get("verdict", "REFINED")).upper()
        return RefinementOutput(
            self.name, "refine",
            "CONVERGED" if verdict == "CONVERGED" else "REFINED",
            data=parsed["data"], notes=str(parsed.get("notes", ""))[:200])

    def critique(self, data: Any) -> RefinementOutput:
        user = "DATA:\n" + json.dumps(data, ensure_ascii=False)[:24000]
        try:
            parsed, finish = self._complete(CRITIQUE_SYSTEM, user)
        except (urllib.error.URLError, OSError, ValueError, KeyError) as exc:
            self.errors += 1
            return RefinementOutput(self.name, "critique", "FAILED",
                                    critique="",
                                    notes=f"{type(exc).__name__}: {exc}"[:200])
        if not parsed or "critique" not in parsed:
            self.errors += 1
            return RefinementOutput(self.name, "critique", "FAILED",
                                    critique="",
                                    notes="unparseable model output",
                                    meta={"finish_reason": finish})
        verdict = str(parsed.get("verdict", "REFINE")).upper()
        return RefinementOutput(
            self.name, "critique",
            "CONVERGED" if verdict == "CONVERGED" else "REFINED",
            critique=str(parsed["critique"])[:400])


# -------------------------------------------------------------- deterministic
class HeuristicRefiner(Refiner):
    """Deterministic offline refiner. Improves what can be improved
    mechanically and reports CONVERGED exactly when nothing changed —
    a true fixed point, no randomness, no network."""

    def __init__(self, name: str = "heuristic"):
        self.name = name

    @staticmethod
    def _clean_str(s: str) -> str:
        return re.sub(r"\s+", " ", s).strip()

    def _refine_node(self, node: Any) -> tuple[Any, bool]:
        changed = False
        if isinstance(node, dict):
            out = {}
            for k, v in node.items():
                nv, c = self._refine_node(v)
                out[k] = nv
                changed |= c
            return out, changed
        if isinstance(node, list):
            out = []
            seen = set()
            for item in node:
                ni, c = self._refine_node(item)
                changed |= c
                if isinstance(ni, str) and not ni.strip():
                    changed = True      # drop empty-string items
                    continue
                key = json.dumps(ni, sort_keys=True, ensure_ascii=False) \
                    if isinstance(ni, (dict, list)) else repr(ni)
                if key in seen:
                    changed = True      # dropped duplicate
                    continue
                seen.add(key)
                out.append(ni)
            return out, changed
        if isinstance(node, str):
            cleaned = self._clean_str(node)
            if cleaned != node:
                return cleaned, True
            return node, False
        return node, False

    def refine(self, data: Any, critique: str | None) -> RefinementOutput:
        refined, changed = self._refine_node(data)
        if not changed and scoring.score(refined) >= scoring.score(data) - 1e-9:
            return RefinementOutput(self.name, "refine", "CONVERGED",
                                    data=data, notes="no mechanical improvement left")
        return RefinementOutput(self.name, "refine", "REFINED",
                                data=refined, notes="dedupe/normalize pass")

    def critique(self, data: Any) -> RefinementOutput:
        _, changed = self._refine_node(data)
        issues = []
        bd = scoring.breakdown(data)
        if bd["completeness"] < 1.0:
            issues.append(f"{1.0 - bd['completeness']:.0%} empty leaves")
        if bd["redundancy"] < 1.0:
            issues.append("duplicate list items")
        if bd["consistency"] < 1.0:
            issues.append("conflicting duplicate keys")
        text = "; ".join(issues) or "no mechanical defects detected"
        # CONVERGED == no further MECHANICAL refinement possible. Residual
        # semantic gaps (empty leaves needing facts) are noted for the live
        # models but cannot be fixed deterministically, so they don't block
        # this refiner's fixed point.
        return RefinementOutput(self.name, "critique",
                                "REFINE" if changed else "CONVERGED",
                                critique=text)


def make_model_refiners(models: tuple[str, ...] = DEFAULT_MODELS,
                        api_key: str | None = None) -> list[OpenCodeRefiner]:
    """Build live refiners for the given OpenCode model names."""
    key = api_key or os.environ.get("OPENCODE_API_KEY", "public")
    return [OpenCodeRefiner(m, api_key=key) for m in models if key]
