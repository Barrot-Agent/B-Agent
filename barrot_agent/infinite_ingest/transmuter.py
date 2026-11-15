"""Convert raw sources into Barrot-format memory records.

One format in, Barrot format out:

===============  ==========================  ==================
source kind      output record kind          what is extracted
===============  ==========================  ==================
paper            fact                        quantitative and method sentences
video / podcast  capability_note             mechanism, numbers, failure evidence
proof            reasoning_pattern           theorem / proof-step sentences
code             reusable_function           verbatim function and class signatures
problem/solution test_case                   problem and solution sentences
article / web    fact                        quantitative or named-entity sentences
===============  ==========================  ==================

The transmuter is extractive.  ``statement`` is a verbatim source sentence
(clipped at 400 characters, tagged ``truncated`` when clipped); nothing is
paraphrased and no fact is generated.  HYPE records produce zero output.
"""

from __future__ import annotations

import re

from .models import MemoryRecord, RawRecord, normalise

MEDIA_KINDS = frozenset({"video", "youtube", "podcast", "ted", "tedtalk", "ted_talk", "audiobook"})
# A 12-minute transcript yields ~100 units; 48 keeps failure narratives that a
# 24-record cap drops (e.g. "Memorilla got just one" on the Hound test).
MAX_RECORDS = 48
MIN_UNIT_CHARS = 40
MAX_UNIT_CHARS = 600

_NUMBER = re.compile(
    r"\d|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|hundred|thousand|million|billion)\b",
    re.IGNORECASE,
)
_MEDIA_WORDS = re.compile(
    r"\b(memory|token|model|score|benchmark|latency|seconds?|cost|train\w*|test\w*|"
    r"fail\w*|wrong|hallucinat\w*|question\w*|plot|document\w*|chat\w*|context|"
    r"accuracy|percent|answer\w*)\b",
    re.IGNORECASE,
)
_PAPER_WORDS = re.compile(
    r"\b(we (?:propose|introduce|present|show|find)|method|architecture|dataset|"
    r"results?|accuracy|benchmark|model|encoder|decoder|training)\b",
    re.IGNORECASE,
)
_PROOF_WORDS = re.compile(
    r"\b(theorem|lemma|corollary|proof|assume|suppose|therefore|hence|contradiction|"
    r"induction|q\.?e\.?d\.?|definition)\b",
    re.IGNORECASE,
)
_PROBLEM_WORDS = re.compile(
    r"\b(problem|solution|fix|bug|error|expected|actual|fails?|broken)\b", re.IGNORECASE
)
_CODE_LINE = re.compile(r"^\s*(?:async\s+def|def|class)\s+([A-Za-z_]\w*)")

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n{2,}")


def _sentences(text: str) -> list[str]:
    """Split prose into sentence-like units of useful length."""
    cleaned = re.sub(r"(?m)^#{1,6}\s*", "", text or "")
    units: list[str] = []
    for chunk in _SENTENCE_SPLIT.split(cleaned):
        unit = normalise(chunk.lstrip("-*+ "))
        if MIN_UNIT_CHARS <= len(unit) <= MAX_UNIT_CHARS:
            units.append(unit)
    return units


def _score(unit: str, words: re.Pattern[str]) -> float:
    score = 3.0 if _NUMBER.search(unit) else 0.0
    score += len({match.group(0).lower() for match in words.finditer(unit)})
    return score


def _top_scored(units: list[str], pattern: re.Pattern[str], limit: int) -> list[str]:
    """Keep the highest-scoring units, restored to source order."""
    scored = [(index, _score(unit, pattern), unit) for index, unit in enumerate(units)]
    keep = [(index, score, unit) for index, score, unit in scored if score > 0]
    keep.sort(key=lambda item: (-item[1], item[0]))
    chosen = sorted(keep[:limit], key=lambda item: item[0])
    return [unit for _, _, unit in chosen]


class Transmuter:
    """Route raw records to extractive fact builders."""

    def __init__(self, max_records: int = MAX_RECORDS):
        self.max_records = max(1, max_records)

    def transmute(self, record: RawRecord, capability: str = "") -> list[MemoryRecord]:
        """Return memory records derived from ``record`` (empty for HYPE)."""
        if record.is_hype or not record.text.strip():
            return []
        kind = record.kind.lower()
        if kind in MEDIA_KINDS or kind == "transcript":
            units = _top_scored(_sentences(record.text), _MEDIA_WORDS, self.max_records)
            out = [(unit, "capability_note", (record.kind, "media")) for unit in units]
        elif kind == "code":
            out = self._code(record)
        elif kind == "proof" or self._looks_like_proof(record.text):
            units = _top_scored(_sentences(record.text), _PROOF_WORDS, self.max_records)
            out = [(unit, "reasoning_pattern", ("proof",)) for unit in units]
        elif kind in {"problem", "problem_solution", "test_case"}:
            units = _top_scored(_sentences(record.text), _PROBLEM_WORDS, self.max_records)
            out = [(unit, "test_case", ("problem_solution",)) for unit in units]
        elif kind == "paper":
            units = _top_scored(_sentences(record.text), _PAPER_WORDS, self.max_records)
            out = [(unit, "fact", ("paper",)) for unit in units]
        else:
            units = _top_scored(_sentences(record.text), _PAPER_WORDS, self.max_records)
            out = [(unit, "fact", ("article",)) for unit in units]

        records: list[MemoryRecord] = []
        seen: set[str] = set()
        for statement, record_kind, tags in out:
            key = normalise(statement).lower()
            if key in seen:
                continue
            seen.add(key)
            try:
                records.append(
                    MemoryRecord.build(
                        statement=statement,
                        kind=record_kind,
                        capability=capability,
                        source_url=record.url,
                        retrieved_at=record.fetched_at,
                        document_sha256=record.sha256,
                        tags=tuple(tags),
                        derived_from=record.url,
                    )
                )
            except ValueError:
                continue
        return records

    # -- specialised builders --------------------------------------------

    def _code(self, record: RawRecord) -> list[tuple[str, str, tuple[str, ...]]]:
        language = record.title.rsplit(".", 1)[-1].lower() if "." in record.title else ""
        out = []
        for line in record.text.splitlines():
            if _CODE_LINE.match(line):
                out.append((normalise(line), "reusable_function", ("code", language)))
            if len(out) >= self.max_records:
                break
        return [
            (statement, kind, tuple(tag for tag in tags if tag))
            for statement, kind, tags in out
        ]

    def _looks_like_proof(self, text: str) -> bool:
        if not re.search(r"\b(proof|theorem|lemma)\b", text, re.IGNORECASE):
            return False
        return len(_PROOF_WORDS.findall(text)) >= 4
