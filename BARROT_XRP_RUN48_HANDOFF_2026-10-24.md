# Barrot XRP Intelligence + V3 Handoff — Run 48

**Observation window:** 2026-10-24 approximately 04:32 UTC; connector timestamps may be a little ahead of the automation clock.  
**Mission priority:** XRP intelligence and prediction-engine mastery.  
**Execution foundation:** Barrot V3.  
**Forecast status:** NOT_ISSUED.

## Current XRP spot snapshot

Kraken public XRP/USD ticker endpoint, observed through web at this run:
- Last trade: $1.28890
- Bid / ask: $1.28890 / $1.28891
- 24h VWAP: $1.30300543
- 24h volume: 11,324,642.816 XRP
- 24h high / low: $1.32950 / $1.28051
- 24h open: $1.29344
- Last vs open: approximately -0.351%
- Last vs VWAP: approximately -1.083%
- Quoted spread: $0.00001, approximately 0.078 bps

The API does not supply an explicit quote-event timestamp. This is one venue, not a consolidated quote; no directional forecast is issued.

Source: https://api.kraken.com/0/public/Ticker?pair=XRPUSD

## ETF flow update: data universe matters

Alpha Finance's five-fund series is updated through the October 23, 2026 session:
- October 23: $0 net flow reported across the five listed funds.
- October 15–23: approximately +$1.7M net flow over the displayed seven-session window.
- 30-session net flow: approximately +$103.6M.
- Cumulative net inflow since November 2025: approximately $1.73B.
- Alpha says the series does not publish fund-level AUM/holdings for this tracker; it is a flow-only series.

XRP Insights uses a different universe (six spot funds plus BITW) and reports +3,335,007 XRP for October 19–22, with known GXRP flow gaps and provisional settlement caveats. Do not average the trackers. Alpha's Oct 23 zero is a reported session value; XRP Insights had not yet settled its Oct 23 row at its displayed cutoff.

Sources:
- https://alphafinance.io/etf/xrp/
- https://xrp-insights.com/data

## Major primary-source finding: Evernorth holdings decomposition

Evernorth's SEC Form 8-K filed October 9, 2026 confirms the business combination closed on October 9. The filing reports approximately 80.3% of SPAC shares with redemption rights were redeemed, for about $195.39M in cash redemptions. The filing also details the XRP consideration at closing.

- Advance subscribers: approximately $214.05M cash plus 600,000 XRP.
- Delayed subscribers: $10.5M cash plus 200,000 XRP.
- Arrington XRP Capital Fund: 211,319,096.061435 XRP.
- Larsen Lam Children's Remainder Trust, an investor affiliated with Ripple: 50,000,000 XRP.
- Ripple contribution: 126,791,458 XRP.
- Total XRP contributed/subscribed in-kind at closing, by arithmetic sum: approximately 388,910,554 XRP.
- Separate earlier cash-funded purchase reported in Evernorth's SEC prospectus: 84,365,876 XRP purchased using proceeds from the $214.05M advance funding.
- These components sum to approximately 473,276,430 XRP, consistent with the prospectus's statement that Evernorth held approximately 473 million XRP as of October 9.

Critical interpretation: the 473M holding figure is a stock, not 473M of new open-market demand at closing. Only the separately documented 84.366M XRP was bought with cash in the described earlier purchase; approximately 388.911M XRP entered through in-kind subscriptions/contributions. Transfers into treasury custody may reduce tradable float if held, but actual liquidity impact depends on wallet/custody controls, lending, collateral pledges, hedging and any later sales. Those deployment details must be evidenced, not assumed.

The same 8-K identifies SBI Holdings subsidiaries/partnerships as collectively holding 8,885,293 Class A shares (39.9% of that class) and 2,905,659 Class C shares (9.0% of that class). Class C shares are non-voting. This is a documented SBI Holdings relationship with Evernorth, distinct from SBIC East Japan. It does not establish an SBIC–XRP relationship.

Primary sources:
- SEC Form 8-K (closing and contributions): https://www.sec.gov/Archives/edgar/data/2092592/000119312526419146/d24481d8k.htm
- SEC prospectus dated October 19, 2026 (473M holdings and acquisition strategy): https://www.sec.gov/Archives/edgar/data/2092592/000119312526425367/d184594d424b3.htm

## Revised causal hypotheses

1. **Treasury stock vs flow:** Evernorth's large XRP treasury is not equivalent to a similarly sized market purchase. Measure cash-funded purchases separately from in-kind contributions and subscriptions; monitor disclosed holdings and actual public execution data.
2. **Float restriction:** In-kind XRP moved to a long-term treasury could reduce immediately available float if it is held unencumbered and not lent/hedged/sold. Disconfirming evidence would include active lending, collateral rehypothecation, hedging, sales or market-making supply.
3. **Capital-structure sensitivity:** The 80.3% redemption rate is a material financing caveat, but does not by itself determine post-close available cash because private placements, XRP contributions and $30M convertible notes also exist. Reconcile pro forma cash, restrictions, debt and obligations from the prospectus before modeling acquisition capacity.
4. **ETF demand is mixed at the margin:** Alpha's Oct 23 reported zero flow and only about $1.7M net across Oct 15–23 coexist with about $1.73B cumulative inflow. Cumulative inflow is not a near-term flow impulse; source universes and settlement cutoffs must remain separate.
5. **Macro/derivatives dominance remains plausible:** The spot quote is below the 24h open and VWAP, but without synchronized multi-venue spot depth, funding/OI/liquidations, BTC beta and macro series, price causation is unresolved.

## GitHub/V3 state: corrected from prior handoff

Live inspection of main confirms that these workflows are already disabled/read-only on main:
- .github/workflows/barrot-pr-automerge.yml
- .github/workflows/barrot-gated-merge.yml

The earlier Run 46 statement that these main workflows were still active is stale. Their disabling commit is https://github.com/Barrot-Agent/B-Agent/commit/429ebafdff70d74327c4b3f8943e3d80197d021b.

The remaining verified scheduled writer under review is main's .github/workflows/check-signal-accuracy.yml. It still runs daily with contents:write, mutates web/signal_history.jsonl and web/signal_accuracy.json, and pushes to main. PR #1126 changes it to manual-only, read-only and artifact-based, with a regression test. Main is unchanged by this run.

### PR #1126 exact-head verification
- PR: https://github.com/Barrot-Agent/B-Agent/pull/1126
- Branch: barrot/accuracy-artifact-only-20261024
- Exact observed head: 4408da4147bb3829d75d83e0b75681ec9a67b08d
- GitHub Actions CI run 40061912975 completed successfully on that head.
- Run 40061912969 for the gated-merge workflow completed successfully, but it is an audit-only/disabled notice, not evidence that an automatic merge gate is operational.
- PR remains open and draft. The branch was 6 commits ahead and 2 behind main at the last comparison; main continued advancing during this run. Do not rebase or merge blindly.

PR #1124 remains open/draft and has become redundant for the two merge-workflow files already changed on main; it was 6 commits ahead and 11 behind at the last comparison. Do not rewrite or close it automatically.

### Signal evaluation defect remains
Main's latest_signal.json at 04:30:11 UTC reports score 44, confidence 0.0, news_score 88 and explicit provider failures (missing GitHub model credentials; Groq HTTP 429). Treat this as provider-unavailable sentiment blended with news, not a validated prediction.

Main's check_signal_accuracy.py scores all overdue entries against one current price at each run. Each entry therefore has a variable actual horizon, depending on when it was first checked. Bullish/bearish scores only require direction, neutral scores count as correct when the move is under 2%; the summary lacks a fixed-horizon target, no-change baseline, Brier/log loss and calibration. The reported 44.4% is not a valid estimate of predictive skill.

### Other known scheduled writers (not changed)
- knowledge-signal-cycle.yml: hourly, contents:write; commits knowledge base and blended signal.
- signal-summary.yml: workflow_run plus hourly fallback; commits summary/audio outputs.
- cross-analysis.yml: workflow_run plus hourly fallback, contents:write; commits entity/sentiment outputs.
- scheduler-tick.yml: every 15 minutes, contents:write and actions:write; commits scheduler queue.
- coinbase-paper-trader.yml: every 30 minutes; configured for BTC-USD, not XRP.
- check-signal-accuracy.yml: daily writer addressed by PR #1126.

This list is a partial verified inventory, not a claim that all workflow side effects have been audited. Disabled backups are not active workflows. Do not bulk-disable unrelated writers without a trigger/permission/secrets/output/dependency review.

## Platform coordination

Only ChatGPT through the authorized GitHub connector is live-tested. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks remain designed-only adapters, not verified live collaborators.

## Forecast ledger

No forecast issued. The current dataset does not provide synchronized market features, a validated point-in-time history, fixed-horizon outcomes or calibrated model performance. Any future forecast must record cutoff, horizon, target, assumptions, probability/confidence, alternatives and subsequent outcome.

## Next actions

1. Verify GitHub CI on the exact head after any new branch commit; the existing 4408da head is the last tested head, not a guarantee about future commits.
2. Compare PR #1126 with the latest main and preserve its draft state; no blind rebase/merge.
3. Continue a least-privilege inventory of scheduled writers, including secrets, external side effects and output paths.
4. Build fixed-horizon, point-in-time prediction evaluation with no-change and simple baselines, Brier/log loss, calibration, walk-forward splits and leakage tests.
5. Reconcile Evernorth's pro forma cash/debt and post-close XRP holdings; distinguish spot purchases, in-kind contributions, collateral/lending and any actual execution.
6. Keep the five-fund Alpha ETF series separate from the six-spot-plus-BITW XRP Insights series.
7. Continue SBIC, ASK Coin, “actual capital” and Camilla Stephenson identity research without unsupported attribution.

Safety record: no main-branch write, merge, force-push, rebase, reset, clean, stash, overwrite or discard was performed in this run.
