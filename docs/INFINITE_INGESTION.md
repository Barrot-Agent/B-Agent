# Infinite Ingestion + Transmutation

Status: built, tested once on `long_context_memory`, **continuous mode not enabled**.
Approval is required before running the loop repeatedly.

The pipeline turns any reachable text source into extractive Barrot memory, finds
cross-source connections, and uses that memory to patch one capability at a time.
It is bounded at every step: no unbounded loops, no unbounded disk, no invented facts.

---

## Modules

| Module | File | Job |
|---|---|---|
| Ingestor | `barrot_agent/infinite_ingest/ingestor.py` | fetch, hype-gate, dedupe, store raw, prune, enforce per-run cap |
| Transmuter | `barrot_agent/infinite_ingest/transmuter.py` | paper / transcript / proof / code / problem -> memory records |
| Cross-analyzer | `barrot_agent/infinite_ingest/cross_analyzer.py` | shared rare terms across different sources -> `data/connections.json` |
| Refiner | `barrot_agent/infinite_ingest/refiner.py` | test -> gap -> ingest -> transmute -> patch -> re-test -> log |
| Hype filter | `barrot_agent/hype_filter.py` | five checks; 2+ failures => `HYPE`; HYPE cannot refine |
| Support | `models.py`, `storage.py`, `sources.py`, `cli.py` | types, disk layout, adapters, command line |

---

## Quick start

```bash
cd /root/barrot/Barrot-Agent

# state
python3 -m barrot_agent.infinite_ingest.cli status

# discover URLs through the local SearXNG (127.0.0.1:8888)
python3 -m barrot_agent.infinite_ingest.cli discover \
    --query "memory tokens long context" --limit 5 --capability long_context_memory

# queue a capability's declared sources
python3 -m barrot_agent.infinite_ingest.cli seed --capability long_context_memory

# one capped ingestion pass (does not run forever)
python3 -m barrot_agent.infinite_ingest.cli ingest --queue --capability long_context_memory

# one refinement for one capability
python3 -m barrot_agent.infinite_ingest.cli refine --capability long_context_memory

# rebuild the connection graph
python3 -m barrot_agent.infinite_ingest.cli connect
```

YouTube transcripts need the venv that has `youtube-transcript-api`:

```bash
/root/.local/share/ytvenv/bin/python -m barrot_agent.infinite_ingest.cli ingest \
    --url "https://www.youtube.com/watch?v=VIDEOID" --kind video
```

A local transcript can be replayed without the network. The canonical URL is still
recorded on every derived fact:

```bash
python3 -m barrot_agent.infinite_ingest.cli ingest \
    --url "https://www.youtube.com/watch?v=VIDEOID" --kind video --path /tmp/transcript.txt
```

---

## Hard limits

| Limit | Value | Behaviour |
|---|---|---|
| ingests per run | 10 (`--max`) | remaining items stay queued |
| refinements per capability | 1 per `Refiner` instance | second call raises `RuntimeError` |
| rate limit | HTTP 429 / 503 | run stops, unprocessed queue items are re-queued |
| `data/raw` | 500 MB | oldest files pruned after every write |
| single document | 1,000,000 chars | rejected, not truncated |
| media transcript | non-empty | empty media raises `ValueError` in the hype gate |
| connections | 500 edges, 400 nodes | strongest edges kept, 5 edges per node |
| memory bound | 128 records per capability | oldest binding dropped first |

`--max` defaults to 10 in the CLI. One refine command is one run; a new process
resets the in-process guard, which is why continuous mode needs an external
scheduler with its own budget.

---

## Dedupe and provenance

- `data/ingest_ledger.json` maps `url -> {sha256, fetched_at, kind, tag}`.
  A URL in the ledger is never fetched again.
- Content is also deduped by sha256, so the same text under two URLs is stored once.
- Every `MemoryRecord` requires `source_url`, `retrieved_at`, `document_sha256`
  and a non-empty verbatim `statement`. `MemoryRecord.build` raises without them.
- The transmuter never paraphrases. Statements are source sentences clipped at
  400 characters; clipped records carry the `truncated` tag.
- HYPE records are written to `data/raw/` for audit and then excluded from
  transmutation and refinement.

---

## Hype filter

Five deterministic checks (`barrot_agent/hype_filter.py`):

1. `benchmark_caveat` - the benchmark's own limitation must survive the framing.
2. `harness_disclosure` - scores must name the harness or evaluation setup.
3. `cost_and_budget` - accuracy claims must report cost, tokens, latency or compute.
4. `funding_vs_intent` - funding may be stated; motive may not be asserted from it.
5. `beneficiary` - emotional framing must name a beneficiary or stake.

Two or more failed applicable checks => `tag == "HYPE"`, `refinement_blocked == True`.
Checks that do not apply return `passed=None` and are not counted.

Calibration on the two sources that motivated the filter:

| Source | Applicable | Failed | Verdict |
|---|---|---|---|
| Better Stack, Memorilla (`lNpDxKfBlf8`) | 3 | 0 | `OK` |
| Julia McCoy, "We've Entered AGI" (`us_pnC6ETNA`) | 5 | `benchmark_caveat`, `funding_vs_intent` | `HYPE` |

Video 2 quotes ARC Prize's "this isn't proof of AGI" and then says "AGI is here";
it names grant funding and then asserts "it was built to make you afraid". Both are
recorded as failures with the matching spans as evidence.

```bash
python3 -m barrot_agent.hype_filter --file /tmp/yt_us_pnC6ETNA.txt --kind video
python3 -m barrot_agent.hype_filter --file /tmp/yt_lNpDxKfBlf8.txt --kind video --json
```

---

## Transmutation routes

| Source kind | Record kind | What survives |
|---|---|---|
| `paper`, `article`, `web` | `fact` | sentences with numbers, methods, results |
| `video`, `podcast`, `ted`, `audiobook` | `capability_note` | mechanism, numbers, failure evidence |
| `proof` (or detected theorem vocabulary) | `reasoning_pattern` | theorem / assume / therefore / contradiction steps |
| `code` | `reusable_function` | verbatim `def` / `class` signature lines |
| `problem_solution`, `test_case` | `test_case` | problem, solution, error, expected/actual sentences |

Defaults: 48 records per source, 40-600 characters per candidate unit. Selection
is numeric-weighted IDF; order is restored to source order.

---

## Cross-analyzer

- Nodes: memory records (id, label, kind, capability, source).
- Edge: two records from **different** source URLs sharing at least two rare terms;
  a term is rare when it appears in at most 40% of records.
- Edge weight: number of shared terms; six terms are stored per edge.
- `data/connections.json` also contains `suggestions`, each with
  `"status": "hypothesis"`. A combined capability is never written as a fact.

---

## Capability definition

`data/capabilities/long_context_memory.json`:

```json
{
  "name": "long_context_memory",
  "memory_ids": ["..."],
  "questions": [
    {"id": "tokens", "question": "...", "expect": ["16 memory tokens"], "forbid": []}
  ],
  "sources": [
    {"url": "https://...", "kind": "video", "title": "...", "path": "/tmp/transcript.txt"}
  ],
  "history": []
}
```

The test builds a query-conditioned gist from the bound `memory_ids` and checks
whether each `expect` substring survives. `forbid` terms subtract from the score.
A regression (`after < before`) restores the previous `memory_ids` automatically.

Harness limitation, stated in every result: this measures **extractive recall of
real source facts**, not LLM answer accuracy. A 0.5B model still needs
`GistResult.to_prompt()` (the anti-invention rule), and exact names/numbers need
`GistResult.expand()` to recover the full source sentence.

---

## First measured run - 2026-11-15

Capability: `long_context_memory`. Sources: the Better Stack transcript
(`lNpDxKfBlf8`, local replay of the 2026-11-15 fetch) and the Memorilla README
(`raw.githubusercontent.com/snap-stanford/memorilla/main/README.md`).

| Question | Expected | Before | After |
|---|---|---|---|
| memory tokens | `16 memory tokens` | missing | found |
| latency at 512 docs | `0.74 seconds` | missing | found |
| FactKG accuracy | `84.33%` | missing | found |
| decoder model | `Qwen3-8B` | missing | found |
| Hound plot questions | `just one` | missing | found |

```
before: recall=0.00 (0/5 facts) records=0 prompt_chars=0
after:  recall=1.00 (5/5 facts) records=17 prompt_chars=5075
96 records added, 17 bound, reverted=False, rate-limited=False
```

Both source records passed the hype filter (`OK`). Raw files: 36 KB. The first pass
scored 0.80 and exposed two extraction defects, both fixed before the clean run:

1. Six-word gist windows orphaned numbers from units (`0.74` without `seconds`).
   Fixed by widening the default slot to 10 words and extending a span over a
   trailing measurement unit; the total budget stays fixed at 160 words.
2. The 24-record extraction cap dropped the transcript sentence "Memorilla got
   just one" (rank 39 of 107). Fixed by raising the cap to 48.

Neither fix changes the test: the questions and expected facts are fixed, and the
before score is measured with empty memory.

**What this result does not mean.** It does not mean the Memorilla system works on
detail questions; the same video measured 1/8 on *The Hound of the Baskervilles*.
It does not mean Barrot's 0.5B model answers correctly; the harness scores memory
availability. It is an upper bound on what the gist can expose.

---

## Source adapters

| Kind | Adapter |
|---|---|
| `video` | `youtube-transcript-api` (English tracks) |
| `paper` | arXiv API, PubMed E-utilities, OpenAlex API |
| `article` | Wikipedia action API (`explaintext`) |
| `discussion` | Hacker News Algolia API |
| `code` | GitHub README API (token-aware) or raw blob URL |
| `web` | generic HTML-to-text |
| local | any file, `--path`, canonical URL still recorded |

Discovery: `discover` calls the local SearXNG JSON API and queues results. Nothing
is fetched during discovery.

The six requested extra MCP servers were **not** added: this phone has ~3.6 GB of
RAM and MCP processes churn under that pressure. The adapters above are plain
HTTP/JSON and cost no resident memory. `docling` remains available as an MCP for
PDF/OCR conversion; the pipeline itself does not parse PDFs yet.

Known gaps:

- No PDF parser in the pipeline (use `docling` first, then feed the text).
- No automatic retry for a failed fetch; the item is logged and must be re-seeded.
- Lexical matching only, so synonyms do not connect.
- Audiobooks only when a text transcript or page exists.
- No scheduler. Continuous mode requires explicit approval.

---

## Tests

```bash
python3 -m pytest tests/test_hype_filter.py tests/test_infinite_ingest.py \
    tests/test_gist_memory.py -q --no-cov
python3 -m flake8 barrot_agent/hype_filter.py barrot_agent/gist_memory.py \
    barrot_agent/infinite_ingest tests/test_hype_filter.py \
    tests/test_infinite_ingest.py tests/test_gist_memory.py
```

78 tests, no network, temporary data roots. The tests cover URL and hash dedupe,
the per-run cap, rate-limit stop and re-queue, raw pruning, HYPE blocking, verbatim
statements, provenance refusal, code/proof extraction, graph edges, regression
rollback, the one-refinement guard and the SearXNG parser.
