# XRP BATCH 1 — 2026-11-18 SEAN FEED

**PAPER ONLY. NO WALLET. NO KEYS. NO LIVE ORDER PATH. Real XRP at risk: 0.**

Snapshot: `market/2026-11-18-sean-feed.json`, provenance `SEAN_SUPPLIED`,
captured `2026-11-18T00:00:00Z`.
Ledger: `XRP_BATCH1.csv` (10 rows, 25 columns).
Runner: `scripts/xrp_batch1.py` · `--check` verifies the ledger.
Tests: `tests/test_xrp_batch.py`.

The snapshot was supplied by Sean and was **not** checked against any exchange.
It is recorded testimony, not verified market data. No network call was made.

## 1. Baseline (TRADE #0)

| Item | Value |
|---|---|
| Paper XRP | 102.27 XRP |
| Paper USD | $100.00 |
| BTC equivalent | 0.001584 BTC |
| XRP price used | $0.9778 |
| Regime | DOWN, BTC dominance 59%, XRP dominance 2.885% (derived) |

XRP dominance is derived, not supplied: `total = 1.27T / 0.59 = 2.1525T`,
`XRP = 62.1B / 2.1525T = 2.885%`. If either input is missing the gate fails
closed instead of receiving a guess.

## 2. Signals, derived from the numbers

Every signal is computed. None is asserted. Formula:
`ratio_change = (1 + XRP%) / (1 + asset%) − 1`, and the 7d round trip returns
`1 / (1 + ratio_change) − 1`.

| Asset | XRP per asset | Ratio 7d | Round trip 7d | Trend | Ratio signal | Volume |
|---|---|---|---|---|---|---|
| BTC | 0.00001549 | **+9.41%** | **−8.60%** | DOWN | AGAINST | UNKNOWN |
| ETH | 0.00055328 | **+9.41%** | **−8.60%** | DOWN | AGAINST | UNKNOWN |
| SOL | 0.01327631 | +5.68% | −5.38% | MIXED | AGAINST | UNKNOWN |
| USDT | 0.97887676 | n/a | n/a | DOWN | UNKNOWN | UNKNOWN |
| XLM | 7.05992780 | −1.06% | **+1.08%** | MIXED | FAVOURS | UNKNOWN |

**Sean's read is confirmed by the arithmetic.** XRP fell 7% on 7d while BTC and
ETH fell 15%. Rotating XRP into BTC or ETH a week ago and rotating back would
have returned **91.4 XRP for every 100**, an 8.6% loss before the 0.4% cost.
XRP→BTC is not "probably bad"; on this data it is measurably bad.

The exception is XLM: it fell 6% against XRP's 7%, so it is the only major that
gained on XRP (+1.08% gross, +0.68% net). It still fails the gate, on volume.

**Correction to Sean's figures:** XRP/USDT was given as 0.9778, which assumes
USDT = $1.00. The supplied price is $0.9989, so the ratio is 0.97888. The gap is
0.11%, a quarter of the round-trip cost. The batch uses the computed value.

## 3. Batch 1 — 10 candidates

| # | Asset | Thesis | Decision | Size | Reason |
|---|---|---|---|---|---|
| B1-01 | USDT | XRP's +1.70% bounce fades; defensive | **ACCEPTED** | 18.9389 XRP | risk 1.000% |
| B1-02 | USDT | same thesis, 12% backstop | **ACCEPTED** | 6.7203 XRP | risk 0.815% |
| B1-03 | USDT | same, 0.5% expected move | REJECTED | — | 0.500% below 1.5× cost (0.600%) |
| B1-04 | USDT | same, news not supplied | REJECTED | — | scan incomplete |
| B1-05 | BTC | Sean's read | REJECTED | — | trend DOWN, ratio AGAINST, volume unknown |
| B1-06 | ETH | tracks BTC | REJECTED | — | trend DOWN, ratio AGAINST, volume unknown |
| B1-07 | SOL | weakest major | REJECTED | — | trend MIXED, ratio AGAINST, volume unknown |
| B1-08 | XLM | only asset that gained on XRP | REJECTED | — | trend MIXED, volume unknown |
| B1-09 | BTC | contrarian bounce | REJECTED | — | trend DOWN; no rule permits counter-trend |
| B1-10 | XRP | hold the base asset | NO_TRADE | — | holding is a position |

**Read this honestly: Batch 1 is one decision, not ten trades.** B1-01 and B1-02
are the same defensive thesis at two sizes. The other eight are one accept-less
thesis and nine non-entries. Padding the count with near-duplicates would make
the batch look busier than it is.

## 4. Accounting

| Item | Value |
|---|---|
| XRP allocated | **25.6591 XRP** (25.1% of stack) |
| XRP at risk (stop + cost) | **1.8560 XRP** (1.815% of stack) |
| XRP idle | 76.6109 XRP |
| Exits pending | 2 |
| Realised XRP delta | **0.0000** |
| Realised USD delta | **$0.00** |
| Realised R | **UNDEFINED** |
| Win rate | **UNDEFINED** |
| Drawdown | **UNDEFINED** |

`UNDEFINED` is not `0`. A trade that has not exited has no R-multiple. Filling
those cells would be inventing the result, and `scripts/xrp_batch1.py --check`
fails the ledger if any realised field is ever populated while `exit_status` is
`PENDING`.

## 5. Confidence score — honest

```
[PASS] provenance is recorded market data: SEAN_SUPPLIED
[FAIL] closed rotations >= 100: 0
[FAIL] XRP stack grew after costs: 0.0000 XRP
[FAIL] XRP drawdown <= 10%: no closed rotations
[FAIL] recent expectancy > 0: 0.0000R over last 0
[FAIL] zero rule violations: 0
READY FOR REAL XRP: NO
```

**1 of 6.** Confidence score: **0 / 100**, unchanged, and it will stay at 0 until
there are closed rotations on recorded provenance.

Sean supplied data. That removed the "no data" excuse for *entries*. It did not
create exits. One snapshot cannot produce a win rate, and no amount of analysis
changes that.

## 6. Defects the run exposed, and the fixes

1. **`available_xrp` did not exist.** Ten candidates each sized against the full
   102.27 XRP stack. A tight stop would have over-committed capital several times
   over. Fixed: `evaluate(..., available_xrp=)` caps allocation at uncommitted
   capital and rejects a zero-size approval. The runner spends capacity as
   entries are approved.
2. **Unknown news still approved the defensive leg.** The `UNKNOWN` check lived
   inside the offensive branch, so an incomplete scan could still park capital.
   Fixed: `UNKNOWN` now blocks every rotation, including USDT.
3. **Holding XRP was reported as a rejection.** It is a decision, not a failed
   rotation. Fixed: `decision=NO_TRADE`, counted separately.
4. **A simulated lesson could disable XLM on real data.** The demo disabled XLM
   at −201.19 XRP. That lesson describes the fixture I wrote, not the market, and
   applying it would have silently removed the only asset with a favourable 7d
   ratio. Fixed: `load_config(path, provenance)` applies only lessons recorded
   against the same provenance. `XRP_LESSONS.jsonl` holds no `SEAN_SUPPLIED`
   lessons, so 0 were applied.

## 7. What unlocks the next step

| Missing | Blocks | Cost to fix |
|---|---|---|
| 24h volume for BTC/ETH/SOL/XLM | the volume signal, so every offensive rotation | one line per asset in a snapshot |
| News state | every rotation when unknown | one field |
| A second snapshot | exits, realised R, win rate, drawdown | send "NEXT SNAPSHOT" |
| Portfolio risk cap | total exposure across tranches | **Sean's decision — not invented** |

The portfolio cap is the one rule I did not add on my own authority. Per-trade
risk is capped at 1%, but nothing caps the sum: three tranches at 1% each is 3%.
This batch came to 1.815% because sizing uses *available* capital, which shrinks
after each entry. That is conservative by accident, not by design. Sean should
set the number.

## 8. Status

| Item | Value |
|---|---|
| Mode | PAPER TRAINING |
| Provenance | SEAN_SUPPLIED |
| Real XRP at risk | **$0** |
| Wallet / keys | none |
| Accepted entries | 2 (one thesis, two sizes) |
| Closed rotations | 0 |
| Confidence | **0 / 100 — NOT READY** |
| Next | second snapshot, plus volume and news fields |
