# Meta-R.E. — reverse-engineering Barrot's own convergence loop

Generated 2026-11-17. Every claim below is tied to a file:line or a command
result. Nothing here is a plan that has not been measured.

Source of the loop: `BARROT-12AM-MASTER.md` — 95 lines, stages named at line 25,
specified at lines 16-88.

---

## 1. What the loop actually is

Ten stages, one of which (RE) is the seed extraction and nine of which are
post-processing on a claim:

```
RE -> Isomorphism Probe -> Anti-Cheat -> Failure Taxonomy -> Second-Order Probe
   -> Axiom Forge -> Emergence Lens -> Plugin -> Skill -> Phoenix
```

Reality check, `grep` over all `.py`:

| Token the loop depends on | Files in `.py` |
|---|---|
| `TRANSFER_SUCCESS` | 0 |
| `anti_cheat_passed` | 0 |
| `AXIOM_FORGE` | 0 |
| `NOVELTY_SCORE` | 0 |
| `failure_type` | 0 |
| `universal_rule_candidate` | 0 |

The ten-stage loop is **prose only**. `scripts/strike_loop.sh` is a 6-line
liquidity polling loop; `scripts/termux_learning_loop.py` is a Groq lesson
extractor. Neither implements it. Stages 8-10 (Plugin, Skill, Phoenix) are
named on line 25 and never specified — the file ends at line 95.

---

## 2. Stage-by-stage: what each stage takes in, gives back, and breaks on

| # | Stage | Input | Output | Failure mode | Automatable? |
|---|---|---|---|---|---|
| 0 | RE | source artefact | "pure rule set" (prose) | rules are unnumbered, unversioned, unhashed — cannot be ablated later | only with a hash per rule |
| 1 | Isomorphism Probe | rule list + target domain | success/failure lists + new pattern | "execute attempt" happens inside one chat turn; nothing runs, so nothing can fail | yes, if the task is a runnable spec |
| 2 | **Anti-Cheat** | a claimed success | quoted rule + yes/no counterfactual | **asks the model to interrogate itself.** A model that hallucinated a rule quotes its own hallucination; "if I delete it, does it still work" is answered from priors | **yes — replace introspection with an executed ablation** |
| 3 | Failure Taxonomy | one failure | TYPE A/B/C/D | label assigned by the same model that just failed, no fixture, no test per type | yes — each type needs a detector |
| 4 | Second-Order Probe | new pattern | universal vs domain-specific | "does it improve source" has no before/after measurement | yes — needs a source baseline score |
| 5 | Axiom Forge | TYPE C gap | one invented axiom + retest | "single smallest axiom" is unverifiable; retest can reuse the same run, so the axiom is unfalsifiable | yes — retest must be a fresh run of the same task id |
| 6 | Emergence Lens | 2 domains | novelty 0-3 | `NOVELTY_SCORE` has no rubric; additive baseline is asserted, not measured | yes — measure A, B, A+B on one metric; emergence = A+B beats A ⊕ B |
| 7 | Plugin | — | — | **not specified anywhere** | no spec, no automation |
| 8 | Skill | — | — | **not specified anywhere** | no spec, no automation |
| 9 | Phoenix | — | — | **not specified anywhere** | no spec, no automation |

Two structural defects, not ten separate ones:

**D1 — the loop grades itself.** Stages 2, 3, 4, 5, 6 all ask the generator to
be the judge. The only thing separating a real transfer from a confident
hallucination is the model's own answer to "are you sure". That is not a
control, it is a courtesy.

**D2 — nothing is durable.** The JSON blob at lines 76-91 is printed into a
transcript. A transcript can be edited, truncated, or regenerated; there is no
chain, so a rewritten history is indistinguishable from the real one.

---

## 3. Three transmutations of the loop

Rule 1 of the repo: never settle for v1. Three implementations were built and
measured with `scripts/transmute.py`, target `scripts/witness_loop.py`, tests
`tests/test_witness_loop.py` (10 tests), 3 repeats.

```
candidate: baseline (V2 witness+chain)   tests=100%  lines=182  score=996389.0
candidate: V1 ablation-only              tests= 10%  lines= 71  score= 93881.0   (1/10)
candidate: V3 durable ledger             tests=100%  lines=195  score=994393.0   -> APPLIED
winner   : witness_v3_durable_ledger.py
```

### V1 — ABLATION ONLY (`/tmp/opencode/variants/witness_v1_ablation_only.py`)
The smallest thing that answers the anti-cheat question: run the task with the
rule, run it again without it, return a state. 71 lines.
**Lost: 1/10 tests.** No ledger means no record, so 9 of the 10 required
behaviours (refusal, chaining, tamper detection, fail-closed lookup) do not
exist. Deleted by the scorer, correctly.

### V2 — WITNESS + HASH CHAIN (the baseline at transmute time)
`CLAIM -> WITNESS -> LOG`. The anti-cheat becomes an executed ablation:
`run(True)` vs `run(False)` on the same task string, and the outcome difference
is the evidence. Three states, all evidence states rather than verdicts:

| with rule | without rule | state |
|---|---|---|
| success | failure | `SUPPORTED` |
| any | same | `REFUTED` |
| failure | success | `CONTRADICTED` (the rule actively hurts) |

Refusals are structural: recording a claim with no witness, or with a witness
whose `rule_id`/`task_sha256` does not match, raises `EvidenceRequired`. The
ledger is append-only and hash-chained from `GENESIS = "0"*64`, so editing one
record breaks every later `prev_sha256`.

### V3 — DURABLE LEDGER (winner, now at `scripts/witness_loop.py`)
Same API and same refusals as V2, three changes:

1. `verify_ledger` is single-pass streaming — parse each line once, hash once,
   O(1) memory (V2 built a list then re-serialised every record twice).
2. Appends use `os.open(O_APPEND) + os.write + os.fsync` — two processes cannot
   interleave a half line, a crash cannot leave a half-written record.
3. `_tail_record` seeks the last 64 KiB instead of re-reading the whole ledger,
   which makes append O(1) instead of O(n).
4. `iter_ledger` lets `assert_supported` stop at the first match.

**Honest note on the score:** the transmute run measured baseline jitter of
21 726 ms, so the tie band swallowed V3's 1 996-point deficit and the variant
won on rule 1. The pytest wall time cannot resolve a ~2 s effect under 21 s of
noise. So speed was settled by a dedicated benchmark instead — the same ledger,
1 000 records, same process:

| metric | V2 | V3 | change |
|---|---|---|---|
| append ×1000 | 7 350.7 ms | 5 103.4 ms | **−31%** (O(n²) → O(n)) |
| verify 1000 records | 59.7 ms | 48.5 ms | −19% |
| assert_supported (last id) | 24.59 ms | 13.63 ms | −45% |
| ledger bytes | 550 670 | 550 670 | identical format |
| tampered record detected | yes | yes | unchanged |

Tests: 10/10 before and after. Behaviour unchanged; format unchanged, so V2
ledgers stay valid.

---

## 4. What is now enforced, and what is still only prose

Enforced in code (`scripts/witness_loop.py`, 10 tests):

- a claim cannot be recorded without an executed witness
- a witness is bound to one `rule_id` and one task hash
- REFUTED and CONTRADICTED are recorded, not discarded — a rule that does
  nothing is kept as evidence that it does nothing
- the chain is verifiable and tamper-evident
- `assert_supported` fails closed

Still prose, in order of damage:

| Gap | Why it hurts | Fill |
|---|---|---|
| `run()` is supplied by the caller | the loop cannot tell a real ablation from a stubbed one | require `run` to be a repo test path, execute through pytest, store returncode |
| Stage 0 rules are not hashed | cannot prove the rule set was unchanged between with/without runs | hash the rule file, require it in `Claim` |
| Failure taxonomy has no fixtures | TYPE A/B/C/D remain labels | one failing example per type in `tests/` |
| Emergence has no metric | `NOVELTY_SCORE` is opinion | A/B/A+B on one numeric metric |
| Stages 7-10 undefined | Plugin/Skill/Phoenix cannot be built | write the spec or drop the names |
| Transmute wall-time noise | 21 s jitter hid a real 2 s effect | benchmark separately when jitter > effect |

The last row is itself a lesson from this session: `scripts/transmute.py`
scores on pytest wall time, which is fine for a 4× regression and blind to a
31% append win. Recorded in `results/gap_fill_log.json`.

---

## 5. The rule that comes out of this

> A rule is not known to transfer because the model says so. It is known to
> transfer when deleting it changes an executed outcome, and that outcome is
> written to a chain that cannot be quietly rewritten.

That is the whole meta-R.E. result. The ten stages are a useful checklist; the
only part that is real evidence is stage 2, and it only became evidence once it
stopped asking and started running.
