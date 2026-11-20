# Capability ledger — Phase 1

Status of the ten named components. **All ten are PROPOSED. None is PROVEN.**
No component may be described as Active in the product, the marketing, or this
repository until the proof bar below is met.

## Proof bar

A component becomes **PROVEN** only when all four exist:

1. A pinned commit (HEAD SHA) or exact version in this repository.
2. A committed test or run log showing the component doing the job claimed.
3. A named owner among the eight roles.
4. A documented failure mode and what happens when the component is down.

A component with a logo, a config stub, or a passing import does not meet the
bar. A config file is not a run log. An import is not a test.

## Ledger

| # | Component | Role in the pipeline | Status | Proof present | What would prove it | Runtime dependency of this product |
|---|---|---|---|---|---|---|
| 1 | PydanticAI | Typed agent outputs and tool schemas | PROPOSED | none | Pinned version + schema validation test log + rejected-output test | none — the kit uses dataclasses |
| 2 | LiteLLM | Model routing and cost control | PROPOSED | none | Call log with provider, model, tokens, cost; fallback test | none |
| 3 | Phoenix | Tracing and evaluation of runs | PROPOSED | none | Exported trace for one product run + eval report | none |
| 4 | Promptfoo | Prompt regression tests | PROPOSED | none | Config + a pass/fail run with a fixed prompt set | none |
| 5 | Guardrails AI | Output validation | PROPOSED | none | Validator test log with a rejected unsafe output | partial substitute: `pack.py` validators, not Guardrails |
| 6 | Mem0 / Qdrant | Long-term memory and retrieval | PROPOSED | none | Write/read test log + collection dump + deletion test | none |
| 7 | OpenPipe | Fine-tuning and dataset export | PROPOSED | none | Dataset export + before/after eval delta on a held-out set | none |
| 8 | Argilla | Human annotation and review | PROPOSED | none | Project export + a reviewed batch with agreement numbers | none |
| 9 | KitOps | Model and artifact packaging | PROPOSED | none | `kit build` log + digest + pull verification | none |
| 10 | Composio | External tool actions | PROPOSED | none | Authenticated action log + a revoked-credential failure test | none |

## What this means for the product

The product runs on the Python standard library and Markdown. It does not call
any of the ten components. If every one of them disappeared tomorrow, the 76
tests would still pass and a buyer could still score issues, run the timebox,
and package a PR. That is deliberate: the pack must not depend on unproven
infrastructure.

## What is not claimed

- No component is "in use" in production.
- No component has been benchmarked for this product.
- No cost, latency, or accuracy number is attached to any component, because
  none was measured.
- The presence of a name in `PRODUCTS_MATRIX.md` or a planning document is not
  evidence of capability.

## Next proof steps (in order)

1. PydanticAI: schemas for `Candidate` and the PR plan, with a rejection test.
2. Promptfoo: a fixed prompt set for the sales copy, with a forbidden-claim
   check as a failing test.
3. Guardrails AI: only if the `pack.py` validators prove insufficient; do not
   add it for the logo.
4. Phoenix and LiteLLM: only if a hosted agent is actually built; they add no
   value to an offline file product.
5. The rest stay PROPOSED until a pipeline needs them.

Each step must land as a commit with a test log. Until then, this file is the
honest status.
