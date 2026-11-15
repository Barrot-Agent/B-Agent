"""Query-conditioned gist memory: fixed-budget, extractive compression.

Text-level analogue of the memory-token idea from Stanford's Memorilla
(https://arxiv.org/abs/2610.21375).  Memorilla learns 16 latent vectors that a
frozen LLM reads instead of a whole document collection.  This module cannot
produce latent vectors without a GPU, so it implements the part that survives
on a 0.5B model in Termux: a *fixed-size, query-conditioned summary* built only
from verbatim source spans.

Design rules (derived from the published failure modes):

* Extractive only.  Every word of a gist token exists in the source text, so
  the compressor cannot invent facts the way a generative summary can.
* Query-conditioned.  The same collection yields different gists for different
  questions (two-pass: relevance first, then refinement from the first pass).
* Budgeted.  ``num_memories * words_per_token`` words at most, regardless of
  collection size.
* Traceable.  Each token keeps its source span, so a RAG fallback can recover
  exact names, numbers and dates that a gist is known to lose.

No third-party dependencies: pure stdlib, deterministic, CPU-only.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Sequence

DEFAULT_NUM_MEMORIES = 16
DEFAULT_WORDS_PER_TOKEN = 6
MIN_UNIT_WORDS = 3
MAX_UNIT_WORDS = 40

_UNIT_SPLIT = re.compile(
    r"(?<=[.!?])\s+|\n+|(?<=[,;:])\s+|\s+(?:and|but|because|which|while|who)\s+",
    re.IGNORECASE,
)
_WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'\-]*")
_NUMBER = re.compile(r"\d")
_ABBREVIATIONS = ("Dr.", "Mr.", "Mrs.", "Ms.", "St.", "Jr.", "Sr.", "Prof.", "etc.", "e.g.", "i.e.")

_STOPWORDS = frozenset(
    """
    a about above after again against all am an and any are as at be because been before
    being below between both but by can could did do does doing down during each few for
    from further had has have having he her here hers herself him himself his how i if in
    into is it its itself just me more most my myself no nor not now of off on once only
    or other our ours ourselves out over own same she should so some such than that the
    their theirs them themselves then there these they this those through to too under
    until up very was we were what when where which while who whom why will with would
    you your yours yourself yourselves
    """.split()
)


def _stem(word: str) -> str:
    """Light, deterministic suffix stripping used only for matching."""
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 5 and word.endswith("ing"):
        return word[:-3]
    if len(word) > 4 and word.endswith("ed"):
        return word[:-2]
    if len(word) > 4 and word.endswith("es"):
        return word[:-2]
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _terms(text: str) -> list[str]:
    """Content terms of ``text`` in order: stemmed, lowercased, stopwords removed."""
    out = []
    for raw in _WORD.findall(text):
        low = raw.lower()
        if low in _STOPWORDS or len(low) == 1:
            continue
        out.append(_stem(low))
    return out


def _split_units(text: str) -> list[str]:
    """Split a document into clause-level units, keeping only useful lengths.

    Markdown headings are dropped (labels, not facts) and hard-wrapped lines are
    rejoined so a line break inside a sentence does not truncate a memory token.
    """
    text = re.sub(r"(?m)^#{1,6}.*$", "", text)
    text = re.sub(r"(?m)^\s*[-*+]\s+", "", text)
    text = re.sub(r"\n(?!\n)", " ", text)
    guarded = text
    for i, abbreviation in enumerate(_ABBREVIATIONS):
        guarded = guarded.replace(abbreviation, f"\u0000{i}\u0000")
    out = []
    for chunk in _UNIT_SPLIT.split(guarded):
        clean = " ".join(chunk.split()).strip(" ,;:-")
        for i, abbreviation in enumerate(_ABBREVIATIONS):
            clean = clean.replace(f"\u0000{i}\u0000", abbreviation)
        words = _WORD.findall(clean)
        if MIN_UNIT_WORDS <= len(words) <= MAX_UNIT_WORDS:
            out.append(clean)
    return out


def _token_count(text: str) -> int:
    """Approximate token count (word pieces) used for budget accounting."""
    return len(_WORD.findall(text))


@dataclass(frozen=True)
class GistToken:
    """One compressed memory slot.

    Attributes:
        text: Verbatim phrase taken from ``source_sentence``.
        score: Final selection score (higher is more relevant to the query).
        source_index: Document index the phrase came from.
        source_sentence: The full source unit the phrase was cut from.
        facts: Numbers or capitalised names carried by the phrase.
    """

    text: str
    score: float
    source_index: int
    source_sentence: str
    facts: tuple[str, ...] = ()


@dataclass
class GistResult:
    """Output of :meth:`GistMemory.compress`.

    Attributes:
        query: The question the gist was conditioned on.
        tokens: Selected memory slots, best first.
        documents: Number of source documents.
        units: Number of candidate clauses scored.
        source_words: Word count of the whole collection.
    """

    query: str
    tokens: list[GistToken] = field(default_factory=list)
    documents: int = 0
    units: int = 0
    source_words: int = 0

    @property
    def words(self) -> int:
        """Words in the rendered gist."""
        return sum(_token_count(t.text) for t in self.tokens)

    @property
    def compression_ratio(self) -> float:
        """Source words divided by gist words (``1.0`` for an empty gist)."""
        gist = self.words
        return round(self.source_words / gist, 2) if gist else 1.0

    @property
    def carries_exact_facts(self) -> bool:
        """Whether any selected token keeps a number or capitalised name."""
        return any(t.facts for t in self.tokens)

    def expand(self, token: GistToken | int) -> str:
        """Return the verbatim source unit behind a token (RAG-style fallback)."""
        item = token if isinstance(token, GistToken) else self.tokens[token]
        return item.source_sentence

    def render(self) -> str:
        """Render the gist as newline-separated phrases."""
        return "\n".join(f"- {t.text}" for t in self.tokens)

    def to_prompt(self) -> str:
        """Render a prompt block for a small model, with an anti-invention rule."""
        if not self.tokens:
            return ""
        return (
            "Compressed memory (verbatim source phrases, fixed budget):\n"
            f"{self.render()}\n"
            "Use only these phrases. If the answer needs a precise name, number or "
            "date that is missing, say so instead of guessing."
        )

    def as_dict(self) -> dict:
        """Serialise for offline storage (JSON-safe)."""
        return {
            "query": self.query,
            "tokens": [
                {
                    "text": t.text,
                    "score": round(t.score, 4),
                    "source_index": t.source_index,
                    "source_sentence": t.source_sentence,
                    "facts": list(t.facts),
                }
                for t in self.tokens
            ],
            "stats": {
                "documents": self.documents,
                "units": self.units,
                "source_words": self.source_words,
                "gist_words": self.words,
                "compression_ratio": self.compression_ratio,
            },
        }


class GistMemory:
    """Budgeted, query-conditioned extractive compressor.

    Args:
        num_memories: Maximum number of gist slots (Memorilla's ``16``).
        words_per_token: Maximum words per slot.
        precision_bonus: Score added per number or proper name in a candidate.
    """

    def __init__(
        self,
        num_memories: int = DEFAULT_NUM_MEMORIES,
        words_per_token: int = DEFAULT_WORDS_PER_TOKEN,
        precision_bonus: float = 0.35,
    ) -> None:
        if num_memories < 1:
            raise ValueError("num_memories must be >= 1")
        if words_per_token < 1:
            raise ValueError("words_per_token must be >= 1")
        self.num_memories = num_memories
        self.words_per_token = words_per_token
        self.precision_bonus = precision_bonus

    # -- scoring ---------------------------------------------------------

    def _idf(self, units: Sequence[Sequence[str]]) -> dict[str, float]:
        df: dict[str, int] = {}
        for terms in units:
            for term in sorted(set(terms)):
                df[term] = df.get(term, 0) + 1
        total = len(units)
        return {term: math.log((total + 1) / (count + 1)) + 1.0 for term, count in df.items()}

    def _scores(
        self,
        units: Sequence[Sequence[str]],
        idf: dict[str, float],
        query_terms: set[str],
        extra_terms: set[str],
    ) -> list[float]:
        scores = []
        for terms in units:
            unique = set(terms)
            hits = sum(idf.get(t, 1.0) for t in sorted(query_terms & unique))
            boost = sum(idf.get(t, 1.0) for t in sorted((extra_terms - query_terms) & unique))
            density = (hits + 0.5 * boost) / math.sqrt(max(len(terms), 1))
            scores.append(density)
        return scores

    def _precision(self, unit: str) -> tuple[float, tuple[str, ...]]:
        facts = []
        bonus = 0.0
        for position, word in enumerate(_WORD.findall(unit)):
            if _NUMBER.search(word):
                facts.append(word)
                bonus += self.precision_bonus
            elif position > 0 and word[:1].isupper() and word.lower() not in _STOPWORDS:
                facts.append(word)
                bonus += self.precision_bonus * 0.6
        return bonus, tuple(dict.fromkeys(facts))

    def _select(
        self,
        units: Sequence[str],
        terms: Sequence[Sequence[str]],
        scores: Sequence[float],
        budget: int,
        eligible: Sequence[bool],
    ) -> list[int]:
        """Greedy maximal-marginal-relevance selection with a redundancy penalty."""
        chosen: list[int] = []
        chosen_terms: list[set[str]] = []
        remaining = [i for i, ok in enumerate(eligible) if ok]
        while remaining and len(chosen) < budget:
            best, best_value = -1, -math.inf
            for idx in remaining:
                overlap = 0.0
                for picked in chosen_terms:
                    union = set(terms[idx]) | picked
                    if union:
                        overlap = max(overlap, len(set(terms[idx]) & picked) / len(union))
                value = scores[idx] - 1.5 * overlap
                if value > best_value:
                    best, best_value = idx, value
            if best < 0 or best_value <= 0:
                break
            chosen.append(best)
            chosen_terms.append(set(terms[best]))
            remaining.remove(best)
        return chosen

    def _phrase(self, unit: str, query_terms: set[str], idf: dict[str, float]) -> str:
        """Take the most query-relevant verbatim window out of a clause."""
        words = [(m.group(0), m.start(), m.end()) for m in _WORD.finditer(unit)]
        if len(words) <= self.words_per_token * 3:
            return unit
        best_span, best_value = None, -math.inf
        for start in range(len(words) - self.words_per_token + 1):
            window = words[start : start + self.words_per_token]
            stems = [_stem(w.lower()) for w, _, _ in window]
            value = sum(idf.get(s, 1.0) for s in stems) / math.sqrt(len(window))
            if any(s in query_terms for s in stems):
                value += 0.5
            if value > best_value:
                best_value, best_span = value, (window[0][1], window[-1][2])
        if best_span is None:
            return unit
        return " ".join(unit[best_span[0] : best_span[1]].split()).strip(" ,;:-")

    # -- public API -------------------------------------------------------

    def compress(self, documents: Sequence[str], query: str) -> GistResult:
        """Compress ``documents`` into at most ``num_memories`` gist tokens.

        Args:
            documents: Raw text documents (chats, notes, book chapters).
            query: Question the memory should be conditioned on.

        Returns:
            A :class:`GistResult`; ``tokens`` is empty when there is nothing to keep.
        """
        result = GistResult(query=query, documents=len(documents))
        if not documents:
            return result

        units: list[str] = []
        owners: list[int] = []
        for doc_index, doc in enumerate(documents):
            for unit in _split_units(doc or ""):
                units.append(unit)
                owners.append(doc_index)
        result.units = len(units)
        result.source_words = sum(_token_count(u) for u in units)
        if not units:
            return result

        # Deduplicate identical clauses so one repeated line cannot own the budget.
        seen: set[str] = set()
        unique: list[str] = []
        unique_owners: list[int] = []
        for unit, owner in zip(units, owners):
            key = " ".join(_WORD.findall(unit.lower()))
            if key in seen:
                continue
            seen.add(key)
            unique.append(unit)
            unique_owners.append(owner)
        units, owners = unique, unique_owners

        terms = [_terms(unit) for unit in units]
        idf = self._idf(terms)
        query_terms = set(_terms(query))
        precision = [self._precision(u)[0] for u in units]
        eligible = [
            bool(query_terms & set(unit_terms)) if query_terms else True
            for unit_terms in terms
        ]

        # Pass 1: query relevance only.
        pass1_scores = [
            score + bonus
            for score, bonus in zip(self._scores(terms, idf, query_terms, set()), precision)
        ]
        pass1 = self._select(units, terms, pass1_scores, self.num_memories, eligible)

        # Pass 2: re-rank with terms the first pass found useful (refinement).
        expansion: set[str] = set()
        for idx in pass1:
            expansion.update(terms[idx])
        expansion -= query_terms
        expansion = {t for t in expansion if idf.get(t, 0.0) > 1.0}
        pass2_scores = [
            score + bonus
            for score, bonus in zip(self._scores(terms, idf, query_terms, expansion), precision)
        ]
        chosen = self._select(units, terms, pass2_scores, self.num_memories, eligible)

        # Build verbatim phrases, best first, until the fixed word budget is spent.
        picked = sorted(chosen, key=lambda i: (-pass2_scores[i], i))
        total_words = 0
        used: set[int] = set()

        def add(idx: int, score: float) -> bool:
            nonlocal total_words
            if idx in used or len(result.tokens) >= self.num_memories:
                return False
            text = self._phrase(units[idx], query_terms, idf)
            if not text:
                return False
            count = _token_count(text)
            if total_words + count > self.num_memories * self.words_per_token:
                return False
            total_words += count
            used.add(idx)
            result.tokens.append(
                GistToken(
                    text=text,
                    score=score,
                    source_index=owners[idx],
                    source_sentence=units[idx],
                    facts=self._precision(text)[1],
                )
            )
            return True

        for idx in picked:
            add(idx, pass2_scores[idx])
        # Context pass: keep the clause before/after a hit so names and numbers
        # are not orphaned (e.g. "the villain from ..." without the name).
        for idx in picked:
            for neighbour in (idx - 1, idx + 1):
                if 0 <= neighbour < len(units) and owners[neighbour] == owners[idx]:
                    add(neighbour, pass2_scores[idx] * 0.5)
        return result


def compress_documents(
    documents: Sequence[str],
    query: str,
    num_memories: int = DEFAULT_NUM_MEMORIES,
    words_per_token: int = DEFAULT_WORDS_PER_TOKEN,
) -> GistResult:
    """Convenience wrapper around :class:`GistMemory`."""
    return GistMemory(num_memories=num_memories, words_per_token=words_per_token).compress(
        documents, query
    )
