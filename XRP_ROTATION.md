# XRP ROTATION — PAPER ONLY

**PAPER ONLY. NO REAL MONEY. NO REAL XRP UNTIL THE GATE PASSES.**

Base capital is XRP, not USD. A rotation sells XRP for another asset and buys
XRP back. Success has two separate measures and both are recorded:

1. **Did the XRP stack grow?** `xrp_out > xrp_in`.
2. **Did the USD value grow?** `usd_out > usd_in`.

They can disagree. A defensive rotation into USDT during a 5% XRP drop grows the
XRP stack while the USD value falls slightly after costs. A rotation into an asset
that pumps in USD but dumps against XRP does the reverse. Collapsing both into one
"profit" number would hide exactly the case that matters, so the ledger keeps
both.

Engine: `barrot_agent/trading/xrp_rotation.py`. CLI: `scripts/xrp_loop.py`.
Ledger: `XRP_ROTATIONS.csv`. Lessons: `XRP_LESSONS.jsonl`.
Tests: `tests/test_xrp_rotation.py` — 32 tests.

```bash
python scripts/xrp_loop.py demo          # 20 simulated rotations, 2 lessons
python scripts/xrp_loop.py lesson        # propose one change from the ledger
python scripts/xrp_loop.py confidence    # readiness checklist, exit 1 if not ready
python scripts/xrp_loop.py scan snap.json  # evaluate plans from a dated snapshot
```

## 1. Rotation universe

| Target | Use it when | Fails when |
|---|---|---|
| BTC | XRP/BTC ratio falling, trend and volume align | chop; ratio mean-reverts |
| ETH | same, ETH usually higher beta than BTC | ETH lags and costs eat the move |
| SOL | same, highest beta of the three | the move is smaller than the cost |
| USDT | defensive: high-impact news, XRP downtrend, ratio against | XRP rallies while parked |
| XLM | XRP-correlated alt; only with its own confirmation | correlation breaks exactly when you need it |

XLM is the one the first lesson disabled. Correlation is not a thesis: two assets
that usually move together can separate on the day you rotate.

## 2. Cost is a gate, not a footnote

| Item | Value | Basis |
|---|---|---|
| Fee per side | 0.10% | ASSUMPTION: taker fee, mid-tier venue |
| Slippage per side | 0.10% | ASSUMPTION: liquid majors, small size |
| Round trip | **0.40%** | two legs |

A rotation must clear 0.40% just to break even, and the gate demands the expected
move be at least **1.5x** the round-trip cost (0.60%). A 0.3% "edge" is a loss
wearing a signal. Both numbers are assumptions, both are printed in every row, and
both must be replaced with measured fills before real capital is discussed.

## 3. Decision gate

A rotation is approved only if all of these hold. Any one failure rejects, and
reasons are returned together so the whole picture is visible.

| Rule | Reject condition |
|---|---|
| Asset | not in BTC/ETH/SOL/USDT/XLM, or disabled by a prior lesson |
| Stop | missing, zero, negative, or >= 100% |
| Risk | worst case (stop + round-trip cost) > 1.0% of the stack |
| Expected move | net edge <= 0, or below 1.5x cost |
| Trend | not UP for an offensive rotation |
| Ratio | not FAVOURS for an offensive rotation |
| Volume | not CONFIRMS for an offensive rotation |
| News | HIGH_IMPACT blocks offensive; UNKNOWN blocks everything except a recorded defensive trigger |
| Dominance | missing or outside 0..100 blocks the scan |
| Time | held more than 10 bars forces the exit |
| Count | more than 3 rotations in a day |

Sizing is the output, never the input: `risk_xrp = stack x 1%`;
`allocation = risk_xrp / ((stop + cost)/100)`. The cost is inside the risk
denominator, so advertised risk equals worst-case risk instead of understating it.

## 4. The loop

**A — SCAN.** XRP plus BTC, ETH, SOL, USDT, XLM: ratio, dominance, volume, news,
funding. Today there is no feed. A scan input must declare
`SEAN_SUPPLIED` or `RECORDED_FEED`; anything else is refused.

**B — DECIDE.** Run the gate. Approval is mechanical, not discretionary.

**C — EXECUTE IN PAPER.** Log entry ratio, exit ratio, XRP in, XRP out, USD in,
USD out, R, cost, bars held, reason, mistake tag.

**D — REVIEW.** Every 10 closed rotations, `auto_lesson` computes per-asset trade
count, win rate, XRP delta and average R, the best and worst rotation, and the
most common mistake. It then proposes **exactly one** change.

The change is applied only when the worst bucket has **at least 4 trades** and a
negative XRP delta. Otherwise it returns `INSUFFICIENT_EVIDENCE` and changes
nothing. This is deliberate: a loop that always finds an improvement is measuring
itself, not the market.

**Never stuck in a dead pair.** Three mechanisms: a 5% stop, a 10-bar time stop
that forces the return to XRP, and the lesson that disables a repeat loser. The
run proves the third: after the lesson, an XLM rotation is rejected with
`asset XLM disabled by the learning loop`.

## 5. Confidence gate — when real $100 XRP is even discussable

The engine answers this, not mood. `confidence` returns READY only when all six
pass:

| # | Criterion | Why it is here |
|---|---|---|
| 1 | Provenance is recorded market data | simulated scenarios can never justify real capital |
| 2 | >= 100 closed rotations | 20 trades is noise |
| 3 | XRP stack grew after costs | the base thesis |
| 4 | XRP drawdown <= 10% | survivable, not just profitable |
| 5 | Recent expectancy > 0 over the last 30 | a stale edge is not an edge |
| 6 | Zero rule violations | an undisciplined record is not evidence |

Current output:

```
provenance: SIMULATED_SCENARIO
[FAIL] provenance is recorded market data: SIMULATED_SCENARIO
[FAIL] closed rotations >= 100: 20
[PASS] XRP stack grew after costs: 183.3525 XRP
[PASS] XRP drawdown <= 10.0%: 0.982%
[PASS] recent expectancy > 0: 0.0917R over last 20
[PASS] zero rule violations: 0
READY FOR REAL XRP: NO
```

**I am not confident, and I will not say I am.** The four passes are arithmetic
on a path I wrote myself. The gate refuses because of that, not because the
numbers look bad.

## 6. Run record (2026-11-18, simulated)

- 20 rotations, 2 batches of 10, starting stack 10,000 XRP (fake)
- Batch 1 lesson: XLM 4 trades, 0% win, **-201.19 XRP** -> XLM disabled
- Batch 2 lesson: worst bucket 3 trades -> `INSUFFICIENT_EVIDENCE`, no change
- Post-lesson XLM attempt: **REJECTED** (disabled), which is the proof the loop
  changed behaviour rather than describing it
- Rehearsal stack after 20: 10,183.35 XRP. **This is a designed scenario, not
  performance.** Changing the fixture changes the number.

## 7. Prompt tail

Your message stopped at "D) REVIEW: After every 10 trades, run AUTO-LESSON: What
worked? What rotation". I implemented what worked, what failed, per-asset
statistics, the mistake tally, and the single-change rule. If the missing tail
asked for something else — a confidence score per rotation, funding-rate rules,
or a specific lesson format — say the word and it goes in. I did not invent it.

## 8. Status

| Item | Value |
|---|---|
| Mode | PAPER ONLY |
| Real XRP at risk | 0 |
| Wallet / keys | none exist in this system |
| Network imports in the engine | none (AST test) |
| Live key in environment | aborts with rc=2 |
| Closed rotations | 20, all simulated |
| Confidence | **NO** — 2 of 6 criteria fail |
| Next | dated market data from Sean or an approved read-only feed |
