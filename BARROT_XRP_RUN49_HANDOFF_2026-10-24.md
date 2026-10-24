# Barrot XRP Intelligence + V3 Handoff — Run 49

**Observed cutoff:** 2026-10-24 approximately 05:02 UTC.  
**Mission priority:** XRP intelligence and prediction-engine mastery.  
**Execution foundation:** Barrot V3.  
**Forecast status:** NOT_ISSUED.

## Fresh XRP spot and derivatives observations

### Kraken XRP/USD
Public ticker observed at approximately 05:02 UTC; endpoint does not provide an explicit quote-event timestamp.
- Last: $1.28953
- Bid / ask: $1.28951 / $1.28952
- 24h VWAP: $1.30297418
- 24h volume: 11,316,195.652 XRP
- 24h open: $1.29344
- 24h high / low: $1.32950 / $1.28051
- Last vs open: approximately -0.302%
- Last vs VWAP: approximately -1.032%
- Quoted spread: $0.00001 (~0.078 bps)

Source: https://api.kraken.com/0/public/Ticker?pair=XRPUSD

### Binance USD-M XRPUSDT
The public premium-index API explicitly timestamps the record at 2026-10-24 04:52:10 UTC:
- Mark: $1.29230
- Index: $1.29289712
- Funding: +0.004047% for the current interval
- Next funding: 08:00 UTC
- Mark approximately 0.046% below index

Source: https://fapi.binance.com/fapi/v1/premiumIndex?symbol=XRPUSDT

Positive funding means longs pay shorts under Binance's convention. One venue and one interval do not establish crowded positioning or direction. No synchronized multi-venue OI/liquidation panel was captured. Forecast remains NOT_ISSUED.

## ETF flows: primary tracker refreshed
Alpha Finance's five-fund series, through the October 23, 2026 session:
- October 23: $0 net flow reported.
- October 15–23: about +$1.7M across the displayed seven-session window.
- 30-session flow: +$103.6M.
- Cumulative net inflow since launch: about $1.73B.
- The tracker lists Bitwise as the largest cumulative flow contributor at about $680.3M.

This is a five-fund flow-only series and does not publish fund-level holdings/AUM in the tracker. Keep it separate from XRP Insights' six spot funds plus BITW dataset, which has known GXRP flow gaps and provisional settlement rows.

Source: https://alphafinance.io/etf/xrp/

## New primary-source Evernorth capital/custody findings

Evernorth's SEC prospectus filed October 23, 2026 adds useful qualifications to the existing 473M XRP treasury analysis.

1. **Facility borrowing:** The filing says the October 7 second amendment increased the Company Facility borrowing limit to $10.0M and that $9.7M had been borrowed as of October 7. This implies only about $0.3M of unused capacity under that specific facility at that date; it is not a measure of total corporate liquidity. Some payments Ripple made for the Company/Evernorth were reclassified as borrowings.
2. **Historical cash caveat:** The filing reports unrestricted cash of $0.8M and a $3.7M net working-capital deficit as of June 30, 2026. These are pre-closing historical balances, not current post-closing cash figures.
3. **Custody:** The filing says 100% of XRP was in offline/cold storage as of the prospectus date, held initially through BitGo Bank & Trust. It describes shared aggregate cold-storage insurance of approximately $250M across eligible BitGo clients, equal to about 36.9% of Evernorth's XRP value as of October 9; this is not dedicated insurance for Evernorth.
4. **Yield strategy timing:** The prospectus says yield strategies and DeFi participation commenced following closing, but also says all XRP was in cold storage as of the prospectus date and that material ecosystem deployment was not anticipated before Q4 2026. This creates a timing/definition ambiguity: strategy commencement does not quantify XRP actually deployed. Seek subsequent disclosures or on-chain evidence before inferring deployed size.
5. **Potential strategy:** Disclosed plans include institutional XRP lending, covered calls, basis trades, decentralized lending, AMM liquidity and RLUSD/XRP pools. These are strategies/intent; the prospectus does not disclose a verified current quantity lent, pledged, hedged, sold or deployed.

Primary source: https://www.sec.gov/Archives/edgar/data/2092592/000162828026067081/xrpn-20261023.htm

Additional SEC correction: an October 12 Form 8-K says delayed-funding Class A shares at the October 9 closing were 1,078,613, not 663,510, correcting a clerical error in the earlier filing.
Source: https://www.sec.gov/Archives/edgar/data/2092592/000119312526419605/d118629d8k.htm

### Updated hypotheses
- The 473M XRP stock is not 473M of new open-market buying. Separate cash-funded acquisition from in-kind contributions/subscriptions.
- Cold storage is evidence of custody status, not proof that tokens will remain permanently unavailable; deployment, custody movements, hedging and lending need evidence.
- Facility borrowing may constrain near-term use of that facility, but cannot be used alone to infer total cash or future XRP buying capacity.
- Announced yield strategies may create future liquidity/collateral/hedging links with Ripple, BitGo, exchanges and DeFi venues, but actual deployment size remains unknown.

## GitHub/V3 current-state inspection

Repository: https://github.com/Barrot-Agent/B-Agent

- Latest observed main commit: `543b0cdc4f103fdab2e04a32e918aa34e7044a55` (cross-analysis refresh, 2026-10-24 04:53:43 UTC).
- PR #1126 remains open/draft: https://github.com/Barrot-Agent/B-Agent/pull/1126
- Candidate branch: `barrot/accuracy-artifact-only-20261024`
- Candidate head last verified: `c076d1d04c5d02bb19640c4c98e257210449440d`
- Compare at this cutoff: 8 commits ahead / 6 behind main, merge base `f9e72f25166da3931898f07c380c0a1202618a15`; do not rebase/merge blindly.
- Exact candidate head has GitHub Actions CI run 40063058905 with success, and the separate gated-merge run 40063058904 completed as a disabled/audit-only notice. These are associated with the exact head observed; any later commit needs its own CI verification.
- Main was not modified. No merge, force-push, rebase, reset, clean, stash, overwrite or discard was performed.

### Confirmed active scheduled writers / external side effects on main
1. `.github/workflows/knowledge-signal-cycle.yml`: hourly, contents:write; ingests/distills and commits knowledge, latest signal and signal history.
2. `.github/workflows/signal-summary.yml`: workflow_run after knowledge cycle plus hourly fallback; commits summary JSON and generated audio. Explicit permissions are omitted, so effective token permissions need settings-aware verification.
3. `.github/workflows/cross-analysis.yml`: workflow_run after knowledge cycle plus hourly fallback; contents:write; commits entity co-occurrence and sentiment outputs.
4. `.github/workflows/scheduler-tick.yml`: every 15 minutes, contents:write and actions:write; commits queue state and dispatches due workflow_dispatch runs from queue entries.
5. `.github/workflows/coinbase-paper-trader.yml`: every 30 minutes; commits simulated BTC-USD paper-trading state/log, not XRP and not real-money trading. It requires Groq and exits if no key, so the paper cycle can fail on provider errors.
6. `.github/workflows/check-signal-accuracy.yml`: daily, contents:write; commits history/summary and pushes main. PR #1126 changes this one workflow to manual-only, read-only and artifact-based.

The `.github/workflows/barrot-agent.yml` workflow has contents/pull-request/issues write permissions. Its issue-label job condition restricts the `barrot-task` label trigger to the repository owner or Barrot-Agent, while manual dispatch can run for authorized workflow-dispatch users. Keep that guard intact and test it.

The scheduler uses an argv list (no shell) and restricts names to existing workflow files, but `scheduler-tick` has actions:write and can dispatch workflows named in its queue. Audit queue-writer permissions and allowable dispatch targets before broadening it. The inventory above is a verified subset, not a complete inventory of every workflow or external side effect. Files under `.barrot-backup/workflows/` and with `.disabled` suffix are not counted as active workflows.

### Prediction quality
Main `web/latest_signal.json` reports score 44, confidence 0.0, news score 88 and explicit provider failures (missing GitHub model credentials and Groq HTTP 429). `scripts/emit_signal.py` returns (0, 0.0) when both model providers fail, then averages that sentinel with the news score. This is invalid sentiment blending, not a calibrated prediction.

Main `scripts/check_signal_accuracy.py` compares every matured-but-unchecked entry to the price fetched at the time of the current run, so different entries get different horizons. Bullish/bearish predictions are scored by direction only; neutral is called correct if the move is under 2%. It does not use a fixed-horizon outcome, no-change baseline, Brier/log loss or calibration. The reported 44.4% cannot be treated as predictive skill.

## Identity/relationship continuity
- SBI Holdings' Evernorth equity relationship is distinct from SBIC East Japan/West Japan. No SBIC–XRP relationship established.
- Circle/USDC on XRPL is documented; whether it complements or substitutes for XRP bridge demand remains a hypothesis.
- Coinbase and Circle share meaningful USDC distribution economics, but no coordinated XRP price strategy is established.
- ASK Coin, “actual capital” and Camilla Stephenson YouTube channel identity remain unresolved; do not invent attribution.
- Only ChatGPT through the authorized GitHub connector is live-tested. Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle and Databricks remain designed-only integrations.

## Next actions
1. Continue the scheduled-writer inventory, including workflow permissions, event trust boundaries, queue inputs, secrets and outputs.
2. Fix provider-failure sentinel handling and build fixed-horizon point-in-time evaluation with baseline/calibration metrics on a reviewed branch.
3. Keep PR #1126 draft; do not merge or rebase while six commits behind main without a reviewed reconciliation.
4. Track Evernorth post-closing cash, facility balances, treasury movements and actual yield-strategy deployment; distinguish declared strategy from executed activity.
5. Continue synchronized XRP spot/depth/derivatives, ETF issuer reconciliation, XRPL stablecoin flows and macro data collection.

**Safety status:** research and read-only inspection executed; main unchanged; no XRP forecast issued.
