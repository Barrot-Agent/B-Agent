# MMI mastery wishlist — market, day trading, paradigm-sync integrity

Top 50. Every "Why" cites something measured in this repo on 2026-11-17, not a
textbook. Constraint that does not move: **paper only, no live keys.** Nothing
below requires capital to prove itself.

Baseline facts this list is built on:

| Fact | Evidence |
|---|---|
| Directional signal accuracy is **45.5%** (772 / 1697) | `web/signal_accuracy.json` |
| `latest_signal.json` publishes `confidence: 0.0` with `score: 44` | that file; `scripts/signal_summary.py:135` rejects `0 < confidence` |
| That signal is **18.6 days old** and nothing rejects it | `generated_at_unix: 1793280213` |
| Paper state holds a position with `position_product: null` and `avg_entry_price: 80436.84` | `web/paper_trading_state.json` |
| Trading surface: market orders only, dry-run default, `BARROT_MAX_TRADE_USD=25`, zero fee/slippage/drawdown code | `barrot_agent/trading/{coinbase_trader,risk_manager}.py` |
| Two disagreeing signal ledgers: 45 lines vs 1697 records | `data/signal_ledger.jsonl` vs `web/signal_history.jsonl` |

Format per item: **Why** (the defect) — **Data needed** — **Transmutation**
(what gets rewritten) — **Proof of mastery** (the test that must fail today and
pass after).

---

## A. Market data & signal integrity

**1. Zero-confidence publish gate**
Why: a signal with `confidence: 0.0` is live, and the repo's own summary
validator requires `0 < confidence`. A consumer that trusts confidence is being
told "no information" while the file says `score: 44`.
Data: `score`, `confidence`, per-channel status.
Transmutation: `scripts/emit_signal.py:35` + `emit_signal_btc.py:35` — when
`confidence <= 0` or every channel is degraded, write `status: "degraded"` and
refuse to overwrite the last valid signal.
Proof: test freezes the emit path with a 429 on every channel → prior
`latest_signal.json` bytes unchanged, exit code non-zero, one log line.

**2. Signal freshness clock**
Why: 18.6-day-old signal is served as current.
Data: `generated_at_unix` + wall clock.
Transmutation: `scripts/signal_summary.py` gains `age_seconds` / `stale: bool`;
every reader refuses `stale` by default.
Proof: test with a 19-day fixture asserts `stale is True` and consumer raises.

**3. Hit-rate floor before any capital**
Why: measured 45.5% directional accuracy is negative EV before fees. Any sizing
logic downstream is currently multiplying noise.
Data: `checked_count`, `accuracy_pct` per signal family.
Transmutation: `scripts/coinbase_paper_trader.py` — refuse to trade when
`accuracy_pct < 52` or `checked_count < 200`, log the refusal.
Proof: with the current `signal_accuracy.json` the trader makes zero trades and
says why; flip the fixture to 55% and it trades.

**4. Cost model in the paper ledger**
Why: no fee, no spread, no slippage anywhere in `trading/`. A round trip is
currently free, which makes every strategy look viable.
Data: taker fee bps, quoted spread, size vs top-of-book.
Transmutation: `coinbase_paper_trader.py:127` (`execute_paper_trade`) — deduct
`fee_bps` and half-spread on entry and exit.
Proof: `buy` then immediately `sell` the same size must lose exactly
`2*fee + spread` within 1e-9. This one test invalidates most paper profits.

**5. Order-book snapshot, not trade prints**
Why: `fetch_recent_trades(limit=20)` is tape, not depth. Sizing against tape
cannot see the wall that will eat the order.
Data: L1/L2 snapshot with exchange timestamp.
Transmutation: paper trader takes a `BookSnapshot` and rejects any decision whose
snapshot age exceeds the strategy horizon.
Proof: a stale-book fixture (> 2s) produces a rejection, a fresh one trades.

**6. Paper state invariants**
Why: `position_product: null` with a non-zero `position_size` and
`avg_entry_price` is a corrupt book that no code caught.
Data: the state file itself.
Transmutation: `load_state()` validates: `position_size > 0 ⇔ position_product
set ⇔ avg_entry_price set`; repair or raise, never silently continue.
Proof: the current `web/paper_trading_state.json` becomes a fixture; loading it
raises a named error.

**7. Paper→live parity harness**
Why: `coinbase_trader.py` and `coinbase_paper_trader.py` share no decision code,
so "it worked in paper" proves nothing about the live path.
Data: a decision record `{product, side, size, reason}`.
Transmutation: extract one `decide()` used by both; live path takes the same
record and only swaps the executor.
Proof: golden decisions produce byte-identical intent from both paths; a diff is
a test failure.

**8. Structured provenance**
Why: `source` is a prose apology — `"sentiment unavailable (github_failed:…;
groq_failed:429 …)"`. Unparseable, unalertable, unmeterable.
Data: per-channel `{name, status, latency_ms, error}`.
Transmutation: `emit_signal.py` writes a `channels: [...]` array; `source`
becomes derived text only.
Proof: schema test rejects an emit missing any declared channel; a 429 fixture
records `status: failed, error: 429` as data.

**9. Duplicate-signal suppression**
Why: emission is unconditional per cycle, so an unchanged signal keeps hitting
downstream consumers as if it were new.
Data: hash of `(score, confidence, sorted headline ids)`.
Transmutation: emit path compares hash to last record; unchanged → `no_new_information`,
no file write.
Proof: two identical cycles produce one new ledger record.

**10. One signal ledger**
Why: `data/signal_ledger.jsonl` (45) and `web/signal_history.jsonl` (1697) both
claim to be the history. Two truths means no truth.
Data: both files.
Transmutation: pick one append-only file, hash-chain it, migrate the other,
leave a tombstone note.
Proof: `verify_ledger` passes on the merged file; a row count reconciliation
report equals the union with zero duplicates.

**11. Vendor disagreement, not averaging**
Why: `_get_xrp_price()` trusts one endpoint. The repo already has a test saying
disagreeing providers must not be averaged — the signal path ignores that rule.
Data: 2+ price sources with timestamps.
Transmutation: quote requires agreement within X bps, else `disputed` and no
signal.
Proof: a 40 bps fixture yields `disputed`; 5 bps yields a quote.

**12. Clock agreement**
Why: every artifact carries both ISO and unix time; nothing checks they match,
and a 2026-10-29 record is being consumed today.
Data: `timestamp`, `generated_at_unix`.
Transmutation: one `parse_ts()` used repo-wide; skew > 1s is a hard error.
Proof: a fixture where ISO and unix disagree by 3s is rejected.

**13. Published score formula**
Why: `score: 44` next to `news_score: 88` with no stated mapping. A number
nobody can recompute cannot be audited or ablated.
Data: raw inputs per component.
Transmutation: extract `compute_score(inputs) -> (score, breakdown)`, store the
breakdown with the signal.
Proof: recomputing from the stored breakdown reproduces `score` exactly for all
1697 historical records.

---

## B. Day-trading execution & risk

**14. Risk-based sizing**
Why: `amount_usd = min(amount, cash * 0.2, cash)` is a fixed fraction with no
reference to where the stop is. Risk per trade is unknown.
Data: equity, entry, stop distance.
Transmutation: `size = (equity * risk_pct) / abs(entry - stop)`, capped by the
existing `$25` ceiling as a second lock.
Proof: two trades with different stop distances risk the same dollars within 1%.

**15. Stop attached at entry**
Why: no stop-loss or take-profit exists in the trading package at all
(`grep drawdown|kelly` → 0 files).
Data: entry price, ATR or fixed bps.
Transmutation: order intent carries `stop` and `target`; paper executor honours
them on every tick, gap fills at gap price.
Proof: a gap-through fixture fills below the stop and the loss exceeds the
nominal stop — proving the simulation is not optimistic.

**16. Daily loss kill switch**
Why: `RiskManager` checks one thing: `amount <= 25`. No daily PnL, no cooldown.
Data: realized PnL per UTC day.
Transmutation: `RiskManager.approve_buy()` adds a daily-loss floor; on breach all
buys reject until UTC midnight and the event is logged.
Proof: three losing trades that cross the floor → fourth buy rejected with a
named reason.

**17. Drawdown governor**
Why: zero drawdown awareness.
Data: equity curve.
Transmutation: track peak equity; −5% halves size, −10% halts.
Proof: a synthetic curve hitting −10% produces `halted: true` and zero further
orders.

**18. Concentration caps**
Why: no per-product or open-position limit; 126 trades with no cap evidence.
Data: open positions by product.
Transmutation: max % equity per product and max concurrent positions.
Proof: a third position in the same product is rejected.

**19. Post-loss cooldown**
Why: nothing prevents immediate re-entry after a loss.
Data: last exit timestamp, exit reason.
Transmutation: cooldown of N minutes or M bars per product after a losing exit.
Proof: immediate re-entry is rejected; after cooldown it passes.

**20. Slippage telemetry**
Why: no intended-vs-filled comparison exists, so execution quality is unknown.
Data: intended price, filled price, size, timestamp.
Transmutation: every paper fill records both; rolling p50/p95 per product.
Proof: a report with non-zero p95 exists after the test suite runs the executor.

**21. Latency budget**
Why: decision latency is unmeasured; a signal that takes 3s to act on is a
different strategy than the one backtested.
Data: snapshot ts → order ts.
Transmutation: executor records latency; refuse when snapshot age + latency >
strategy horizon.
Proof: an injected 5s delay causes rejection.

**22. Idempotent order ids**
Why: `client_order_id = str(uuid.uuid4())` per call — a retry after a timeout
places a second order.
Data: signal hash, product, size.
Transmutation: derive the id deterministically; same intent → same id → exchange
rejects the duplicate.
Proof: calling `buy()` twice with one intent yields one accepted order.

**23. Book-aware size cap**
Why: size is independent of liquidity; a $25 order is fine on BTC, not on a thin
alt pair.
Data: top-of-book size.
Transmutation: cap at X% of L1 size, else split or reject.
Proof: a thin-book fixture rejects the same size that a deep book accepts.

**24. Volatility-normalised risk**
Why: fixed-fraction sizing means risk per trade swings with regime.
Data: ATR(14) or realized vol.
Transmutation: size ∝ 1/vol so dollar risk is constant.
Proof: high-vol and low-vol fixtures risk the same dollars.

**25. Regime declaration**
Why: no strategy states which market it is allowed to trade in.
Data: trend/range classifier (ADX, Hurst, or variance ratio).
Transmutation: strategy declares `allowed_regimes`; executor enforces.
Proof: a ranging fixture blocks a trend-only strategy.

**26. Costed backtest**
Why: there is no backtest harness; the only evidence is 126 paper trades.
Data: `web/signal_history.jsonl` + price series.
Transmutation: replay the 1697 historical signals through the executor with fees
and slippage.
Proof: the 45.5% signal family shows negative EV; if it does not, the cost model
is wrong and item 4 is not finished.

**27. Trade journal with reason codes**
Why: `trade_count: 126` and nothing else. No record of why.
Data: signal id, regime, size rule, entry/exit reason.
Transmutation: append-only journal, one JSON line per trade, hash-chained.
Proof: every trade in a replay maps to a signal id and an exit reason enum.

---

## C. Paradigm synchronisation integrity

**28. Unit and type registry**
Why: `RiskManager` uses `Decimal`, the trader passes strings, the paper trader
uses float, and `avg_entry_price` is a bare float. Mixed precision in money code.
Data: one `Money` type (Decimal + currency).
Transmutation: replace float/str money in `trading/` and `coinbase_paper_trader.py`.
Proof: a test that parses every money field in `web/*.json` through `Money`
without loss; mypy on the package.

**29. Schema contracts for artifacts**
Why: `web/` and `data/` hold 10+ JSON artifacts with no schema and no validation.
Data: current shapes.
Transmutation: `schemas/` + validate-on-write, validate-on-read.
Proof: a corrupted fixture fails loudly at load, not silently at 3am.

**30. Cross-artifact consistency check**
Why: the paper state contradicts itself and no tool noticed.
Data: all artifacts.
Transmutation: `scripts/verify_artifacts.py` run in CI: position ⇔ product ⇔
entry price; confidence > 0 for publishable signals; ledger counts reconcile.
Proof: it fails on today's repo state, passes after items 1, 6 and 10 land.

**31. Single writer for "current signal"**
Why: `emit_signal.py`, `emit_signal_btc.py` and `emit_signal_with_hrm.py` all
write signal files, plus `patch_add_btc_tool.py` rewrites derived output from
them. Last writer wins by luck, with no lock and no `writer` field.
Data: writer identity.
Transmutation: one `publish_signal()` with a lock file and a `writer` field.
Proof: concurrent writes produce a serialised result and a provenance trail.

**32. Reasoning→action fidelity**
Why: the model returns free text; parsing is permissive. A justification that
does not match the executed side is currently possible.
Data: decision enum + reason.
Transmutation: decision must be one of `BUY/SELL/HOLD` plus a cited signal id;
free text is rejected.
Proof: a mismatched fixture is rejected before any order call.

**33. Prompt-version drift tracking**
Why: `barrot_agent/barrot_brain.py:121` already hashes prompts for integrity, but
that hash never reaches the signal artifacts — so the 45.5% accuracy is an
average over an unknown number of prompt versions.
Data: prompt hash, carried forward from the brain to the emitter.
Transmutation: store `prompt_sha256` in every signal record; report accuracy per hash.
Proof: the accuracy report splits by hash and shows which version is worse.

**34. Memory contamination guard**
Why: `MEMORY.md` and `BARROT_SYNC.md` are append-only prose; retrieval cannot
tell a pre-change fact from a post-change one.
Data: timestamps + supersession markers.
Transmutation: entries carry dates and `supersedes:` pointers; retrieval filters
by date.
Proof: a query for "current max trade" returns the latest value, not all of them.

**35. Clock skew detection**
Why: same as item 12 but repo-wide: every subsystem has its own notion of now.
Data: UTC + exchange time per artifact.
Transmutation: one clock module; skew > 1s is an error.
Proof: an injected skewed fixture is rejected by every reader.

**36. Rollback drill**
Why: "revert with git" is a rule, never a measurement.
Data: commit sha, revert time.
Transmutation: scripted drill — apply a known-bad change, revert, run tests,
record elapsed.
Proof: a dated drill record with a measured time under the agreed budget.

**37. Global halt file**
Why: no single switch stops every entrypoint.
Data: `HALT` marker + reason.
Transmutation: every trading entrypoint checks it first, including the paper trader.
Proof: creating `HALT` makes all entrypoints exit non-zero with the reason.

**38. Secrets never logged**
Why: `GITHUB_MCP_TOKEN`, `HF_TOKEN`, `GROQ_API_KEY` are read from env; one debug
print leaks them.
Data: env var names.
Transmutation: a scanner test over logs and artifacts for each secret pattern.
Proof: a planted fake key in a log fixture fails the scan.

**39. Deterministic decisions**
Why: a strategy that changes answer between identical runs cannot be measured.
Data: model version, temperature, seed.
Transmutation: decisions at temperature 0 with the model version recorded.
Proof: the same input replay produces identical decisions N times.

---

## D. Loop & system integrity feeding the market engine

**40. Executed ablation is the only promotion path**
Why: the old anti-cheat asked the model if it cheated. Now `witness_loop.py`
runs `run(True)` vs `run(False)` and records it.
Data: claim + witness.
Transmutation: no strategy rule may size capital without a `SUPPORTED` ledger
record; `assert_supported` is called in the sizing path.
Proof: an unsupported rule raises `EvidenceRequired` before an order is built.

**41. Decisions cite evidence ids**
Why: a trade reason of "bullish" is unfalsifiable.
Data: signal id, response id, ledger record sha.
Transmutation: every order intent carries the ids that produced it.
Proof: an order without ids cannot be constructed (type-level refusal).

**42. Benchmarks when jitter exceeds effect**
Why: this session's transmute measured 21.7s of pytest jitter, which hid a real
31% append win. Wall time is the wrong instrument at that noise level.
Data: repeat spread vs effect size.
Transmutation: `scripts/transmute.py` gains a `--bench` hook; when jitter >
effect, the verdict comes from a microbenchmark, not the suite.
Proof: the witness-loop comparison is reproducible from the bench script alone.

**43. Retire or gate the 45.5% channel**
Why: a channel below chance is not a weak signal, it is a cost. The repo's own
research test forbids averaging disagreeing providers; the signal path still does.
Data: accuracy per channel.
Transmutation: channels below chance are disabled by config, with the record kept.
Proof: disabling the channel changes the emitted score and the accuracy report
shows why.

**44. Paper-only is enforced, not promised**
Why: dry-run is an env default (`BARROT_TRADING_DRY_RUN=true`), not a lock.
Data: env + key presence.
Transmutation: a test asserts live mode requires both an explicit flag and a
key, and that missing either cannot enable it.
Proof: the test passes with no keys present (this environment).

**45. `$25` is a ceiling, not a risk system**
Why: the only limit is a constant. Equity-relative risk does not exist.
Data: account equity.
Transmutation: `max_trade_usd` becomes `min(constant_ceiling, equity * pct)`.
Proof: a $1,000 equity fixture caps at the pct; a $100,000 fixture caps at the
constant.

**46. Untested-script budget**
Why: 94 of 121 scripts have no test reference (`results/re_wishlist.md`), and the
trading scripts are among them.
Data: script inventory.
Transmutation: import-smoke test per script, then behaviour tests for trading paths.
Proof: the untested count drops and CI prints it.

**47. No bare `except:` on an order path**
Why: 8 tracked files swallow every exception; a swallowed order error is a
silently missing trade.
Data: the 8 files.
Transmutation: at minimum, none may wrap an exchange call; replace with typed
catches that log and re-raise.
Proof: an AST test that forbids bare `except:` in `trading/` and its callers.

**48. Kill `sys.path.insert`**
Why: 31 tracked files insert paths, which is how the wrong copy of a module gets
imported — exactly the duplicate risk Phase 2 shimmed around.
Data: package metadata.
Transmutation: `pip install -e .`, delete the inserts and the shims they support.
Proof: full suite green with zero `sys.path.insert` in tracked files.

**49. Ledger verification in CI**
Why: a hash chain nobody verifies is decoration.
Data: `results/witness_ledger.jsonl`, trade journal.
Transmutation: CI step runs `verify_ledger` on both; failure blocks merge.
Proof: a tampered fixture fails CI locally in one command.

**50. Post-mortem protocol for dead rules**
Why: `REFUTED` and `CONTRADICTED` must never be quietly deleted, or the same bad
idea returns next cycle.
Data: ledger states.
Transmutation: every refuted rule gets a dated note with the failing witness;
deletion requires a written supersession record.
Proof: a rule that reappears after being refuted is flagged by id collision.

---

## Order of attack (highest damage first)

1. **4 → 26** (cost model, then costed backtest). Until costs are real, every
   other number in this list is fiction.
2. **1 → 2 → 3** (stop publishing zero-confidence, stale signals; stop trading
   below chance). Three small gates that make the system honest at the edges.
3. **6 → 30 → 10** (state invariants, artifact consistency, one ledger). This is
   the "paradigm sync" core: one truth per fact.
4. **14 → 15 → 16 → 17** (sizing, stops, daily loss, drawdown). Risk before
   alpha.
5. **40 → 41 → 49** (evidence-gated promotion). Makes every later claim auditable.

Nothing here needs a live key. Items 1-6, 9-13, 26-30, 40-43, 46-50 are all
provable with files already in this repo.
