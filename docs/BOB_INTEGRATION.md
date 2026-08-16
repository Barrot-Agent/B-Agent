# IBM Bob and Barrot's improvement loop

IBM Bob should be used as a development and review agent around Barrot, not as
an unrestricted self-modification mechanism. Barrot can record observable task
outcomes with `barrot_agent.learning.ExperienceLedger`; Bob can then inspect
those records, propose a focused change, and run the existing tests and
benchmarks.

## Controlled cycle

1. Barrot performs a task and records success, an optional normalized score,
   feedback, and provenance metadata.
2. A benchmark produces a baseline and candidate result using the same tasks.
3. Bob analyzes failures and prepares a small, reviewable patch.
4. CI runs tests, security checks, and the benchmark again.
5. A human or protected CI policy reviews the evidence and decides whether to
   promote the candidate.

The ledger is append-only and evidence-only: it does not execute code, change
repository files, or promote candidates. Scores must be finite values from
`0.0` to `1.0`; missing scores cannot qualify a candidate for promotion.

Example:

```python
from barrot_agent.learning import Experience, ExperienceLedger

ledger = ExperienceLedger("ping-pongings/knowledge-base/experiences.jsonl")
experience = ledger.record(Experience("memory retrieval", True, score=0.9))
print(ledger.summarize([experience]))
```

This provides the missing measurement layer for Barrot's self-learning
roadmap while preserving rollback, provenance, and human approval.
