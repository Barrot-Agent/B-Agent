# Barrot XRP Mission — Canonical Current Handoff

**Updated:** 2026-11-10 UTC  
**Run:** 113  
**Authority:** This file is the single current handoff. The older, very large `BARROT_XRP_MISSION_HANDOFF.md` and `BARROT_XRP_MISSION_HANDOFF_CURRENT.md` files remain historical archives; do not append routine run updates to them. Preserve their history.

## Mission and foundation

- **Priority 1:** `xrp_intelligence_prediction_engine`.
- **Preserved foundation:** Barrot V3 execution, orchestration, safety, verification and evidence gates.
- **Forecast policy:** no directional forecast until synchronized point-in-time data and leakage-safe out-of-sample evaluation meet the readiness contract. No guaranteed returns, paper trading or real-money actions.

## Repository state — VERIFIED

| Item | State |
|---|---|
| Main SHA | `d4d43be3427375cf79d190e768976de062e20287` |
| Integration branch | `integration/core-capabilities-mmi-structural-paper-20261104` |
| Integration head at this verification | `e46e4264ef31cb4eee8c9fa6787569fb9204e978` |
| Active integration PR | [#1640](https://github.com/Barrot-Agent/B-Agent/pull/1640) |
| PR ancestry | 895 commits ahead, 0 behind |
| PR changed paths | 230 |
| PR API diff | 112,167 additions / 3,554 deletions |
| Main tree | 1,404 entries; 1,299 files; 86 workflows |
| Integration tree | 1,527 entries; 1,414 files; 87 workflows |
| Open PR inventory | 372 total: 356 drafts, 16 non-drafts |

The integration branch contains the priority-one mission manifest and registry, the 40-source XRP registry, the read-only scheduled public-ingestion workflow, point-in-time feature store, forecast ledger and Barrot V3 safeguards. Main does **not** yet contain `data/missions/primary_mission.json` or `.github/workflows/xrp-public-ingestion.yml`.

## Verification — exact head e46e4264

<badge>VERIFIED</badge>

- Full repository suite: **1,347 passed, 0 failed, 8 subtests passed**.
- Inclusive coverage: **59.48%**, above the 53% floor.
- Core suite: **677 passed, 8 subtests passed**.
- Dependency audit: all six manifests passed; zero known vulnerabilities reported.
- Fail-closed merge gate passed; automatic merging remains disabled.

Evidence:
- [Full CI run 42749023084](https://github.com/Barrot-Agent/B-Agent/actions/runs/42749023084) — both core and full-suite jobs succeeded.
- [Dependency audit 42749022857](https://github.com/Barrot-Agent/B-Agent/actions/runs/42749022857).
- [Fail-closed gate 42749022854](https://github.com/Barrot-Agent/B-Agent/actions/runs/42749022854) — job explicitly says merging is disabled pending gate verification.

Main's latest CI, [run 42526890841](https://github.com/Barrot-Agent/B-Agent/actions/runs/42526890841), passed 718 tests and 8 subtests. Main's CI has a full-suite job but no inclusive coverage measurement; the integration CI adds coverage across the full `barrot_agent` package set.

The exact-head verification above applies to `e46e4264`. Any subsequent commit requires fresh exact-head checks.

## Integration architecture — DESIGNED / EXECUTED / VERIFIED

### Public ingestion and provenance

- 40 unique endpoint records: 36 hourly public sources, 2 weekly CFTC TFF sources, and 2 non-commercial XRPL node sources excluded from scheduled market ingestion.
- The scheduled workflow is read-only, uses public GET requests, runs only on main, and stores run artifacts/cache rather than writing repository files.
- `RawReceiptArchive` captures response bytes, source/receipt metadata, HTTP provenance headers, SHA-256 payload identities and a per-run receipt chain. Redirects are disabled and hosts are allowlisted.
- Some sources are digest-only because of source terms; this is explicit in the source registry.
- Current retention is bounded: raw artifacts up to 90 days, per-run feature-store checkpoint 7 days, daily archive up to 90 days, plus a cache. This is **not** independent WORM retention or an external trusted timestamp anchor.
- SQLite triggers deter ordinary application mutation but do not make the store adversarially tamper-proof.
- The workflow is not active on main until PR #1640 is safely integrated.

### Feature store and evaluation

- Point-in-time SQLite feature store and source-registration/cutoff checks.
- Four deterministic baselines: naive, momentum, mean-reversion and volatility.
- Chronological walk-forward evaluation with horizon purge/embargo; two venue-specific price series and five horizons (1h, 4h, 24h, 7d, 30d).
- The evaluator requires at least 100 training samples, 100 out-of-sample samples, two independent source groups, at least ten horizon multiples, and weighted calibration error no greater than 0.05.
- Forecast issuance additionally requires a trusted Ed25519 evaluator signature and a valid issuance-time feature snapshot.
- Temporal temperature scaling is applied to deterministic baseline probabilities from prior resolved outcomes; it is not evidence of a trained predictive model or independent shadow success.
- Overlapping hourly origins for multi-hour/multi-day horizons can reduce effective sample size. Block-bootstrap/HAC or equivalent effective-sample correction is still needed before those results support issuance.
- No sufficient shadow-outcome set or demonstrated out-of-sample lift is established.

**Forecast state: NOT_ISSUED.** No directional forecast or paper trade occurred.

## XRP market and flow snapshot — 2026-11-10

### Spot — direct public venue APIs

- Kraken XRP/USD: last **$1.09187**; bid **$1.09147**; ask **$1.09158**; top spread about **1.01 bps**; 24h volume **27.42M XRP**; 24h VWAP **$1.09507**; 24h high/low **$1.11573 / $1.07502**; UTC-day open **$1.09748**.
- OKX XRP-USDT: last **1.0936 USDT**; bid **1.0937**; ask **1.0938**; 24h volume **69.30M XRP**; provider event timestamp **2026-11-10T03:27:27.968Z**.
- Kraken USDT/USD midpoint: **0.998655**. Normalized OKX last is approximately **$1.092129**, about **0.0237%** above Kraken's last. The quotes are asynchronous; this is not an executable arbitrage calculation.
- Kraken last is about 0.29% below its 24h VWAP and 0.51% below its UTC-day open.
- **No synchronized live L2 depth snapshot was captured in this run.** Direct depth API retrieval was unavailable through the web retrieval path. Do not substitute a combined spot/perpetual heatmap for pure spot depth or executable slippage.

### Derivatives — disagreement preserved

| Provider / cutoff | Open interest | 24h liquidations / positioning |
|---|---:|---|
| Liqwall, 02:22 UTC | $1.22B, -1.8% | $8.2M total; $7.5M longs, $706K shorts; +0.0055% funding per 8h; 74.5% of Binance XRP accounts long |
| TradRadar, 02:00 UTC | $1.66B, -3.9% | At least $9.08M; $8.22M longs, $864.67K shorts; OI-weighted funding +0.0030% per 8h; 79.8% long accounts |
| Alpha Finance, 02:54 UTC | $2.46B | $8.1M longs, $777.7K shorts; modeled long cluster $3.5M at $1.0739 and short cluster $6.0M at $1.1193 |

Open-interest aggregates differ by approximately **2.02x**. Venue coverage and aggregation windows overlap but are not identical; do not average them. Alpha's liquidation bands are modeled from open interest and leverage tiers, not actual resting orders or guaranteed liquidation triggers. The shared observation is long-heavy deleveraging, not a directional forecast.

### Exchange balances and transfers — inherited Run112 evidence

- XRP Insights tracked 701 labeled wallets across 24 exchanges, about 22.35B XRP (32.5% of its circulating-supply reference).
- Same-wallet-set changes: **-25.8M XRP over 7 days**, **-138.1M over 30 days**, and **+9.7M on Nov 9**.
- Two newly tracked wallets added 512M XRP; the naive total-wallet change was +373.9M. This demonstrates why wallet-set changes must be separated from actual balance movements.
- Labeled omnibus/custody wallets, cold storage, wrapped-token reserves and insurance balances are not tradable float.
- CryptoQuant/Darkfost reported a **691M XRP Binance inflow on Nov 8**, valued above $900M at the event price. A deposit is not proof of a sale. Reserve replenishment after the reported Oct 29 theft is a hypothesis, not confirmed attribution. A separate Nov 4 outflow reported by the same source must not be netted without wallet-level reconciliation.

### ETF holdings — new temporal update

CryptoKeyhole's issuer-file tracker was updated **2026-11-10 03:22 UTC**:

- **Nov 9 partial: 2 of 4 daily-tracked funds reported**, not a complete market total.
- Bitwise XRP ETF: **-8,594,551 XRP**.
- 21Shares TOXR: **-194,660 XRP**.
- Partial total: **-8,789,212 XRP**, approximately **-$9.658M** using the tracker’s close. Franklin Templeton XRPZ and Canary XRPC were still pending. This partial is not included in the cumulative total.
- The earlier Run112 capture at 02:52 UTC showed 1 of 4; that was a valid earlier snapshot. The later 03:22 UTC page added the 21Shares file. Preserve both cutoffs; do not overwrite the earlier receipt.
- Latest complete day, Nov 6: **-752,048 XRP / -$887K**, all 4 funds reported. Last five complete trading days: **-765,403 XRP**. Cumulative Oct 23–Nov 6: **+2,622,459 XRP**, with 2 inflow days and 8 outflow days across the tracker’s 11-day series.
- Bitwise's own page reports 406,770,577.61 XRP and 36.44M shares for its latest displayed holdings, versus 415,365,129.04 XRP and 37.21M shares on the prior displayed holdings page. The roughly 8.595M XRP and 770K-share reduction corroborates the tracker’s Bitwise row.
- These are holdings changes, not a direct cash-subscription series or proof that every XRP was sold into spot. CryptoKeyhole excludes daily Grayscale data it cannot lawfully read and excludes REX-Osprey direct-only holdings because they do not represent the fund's full look-through holdings.

### Macro and regulatory event timeline

- U.S. October CPI and Real Earnings are scheduled for **2026-11-10 at 08:30 ET / 13:30 UTC**. At this snapshot they are future events, not released results.
- CFTC announced on Oct 27 a plan to move COT publication to twice weekly by end-2026: Monday data on Wednesday and Wednesday data on Friday at 3:30 p.m. ET. The release does not give an effective date or clearly specify whether the new schedule applies to TFF financial-futures/XRP rows. Keep the XRP CFTC adapter weekly until scope and effective date are confirmed.
- EBA direct supervision of significant USDC e-money-token requirements is scheduled to begin Nov 12. This is a USDC regulatory event, not an XRP demand event.

## Institutional and corporate relationship map

- Coinbase–Circle: USDC distribution/revenue-sharing economics. Circle's Q3 filing reports $331.3M of Q3 distribution costs to Coinbase; Coinbase's Q3 filing reports a $306.9M stablecoin-revenue line. These are different accounting measures and must not be netted as profit or treated as XRP flows.
- SBI–Circle: 50/50 Circle Japan JV, distinct from SBI Holdings/SBI Shinsei Bank's separate $50M strategic investment in Circle.
- SBI–Ripple: SBI's Ripple equity relationship, SBI Ripple Asia, and SBI Remit corridors that explicitly use XRP as a bridge asset are separate from SBI VC Trade's RLUSD distribution and JPYSC lending.
- SBI–Evernorth: SEC filing reports SBI-controlled holders with 21.4% of common stock and 39.9% of voting power. This does not prove that SBI contributed 39.9% of Evernorth's XRP treasury. Aggregate cash and in-kind XRP subscriptions are not disclosed as SBI-only contributions.
- Ripple–BNY: BNY custody support for XRP and RLUSD expands institutional custody access; it does not prove BNY proprietary XRP purchases or collateral utilization.
- PNC–Coinbase–Circle: USDC receipt-and-conversion pilot is an alternative institutional dollar rail, not an XRP corridor.
- RLUSD/USDC market capitalization, custody balances, stablecoin payments, corporate revenue and XRP bridge conversion are separate variables. No stablecoin balance is counted as XRP demand without direct evidence.

## Identity research

- Japan's SBIC East/Central/West are Tokyo, Nagoya and Osaka regional Small and Medium Business Investment & Consultation companies under Japan's 1963 Act No. 101. They are distinct from SBI Holdings.
- Tokyo SBIC's official June 2025 course includes ChatGPT and Copilot instruction for investee companies. This is training activity, not an OpenAI partnership.
- ASK Coin: Permission Coin ASK remains a candidate; no XRP integration is verified. The inactive Ask Coin exchange listing is a separate entity.
- “Actual capital” is not a standardized XRP metric. Keep cash purchases, in-kind XRP contributions, debt proceeds, drawn facilities and contingent equity capacity separate.
- Camilla/Kamilah Stevenson: guest-appearance identity evidence is stronger than channel-ownership evidence. Do not inventory similarly named personal channels without direct identity verification.

## Nine-platform coordination map

Current verified state; no persistent cross-platform data exchange was demonstrated this run.

| Platform | Authentication / data-flow evidence |
|---|---|
| ChatGPT | Current-session GitHub connector read/write verified |
| Claude | Unverified |
| Grok | Unverified |
| Gemini | Unverified |
| Copilot | One-off COMMENTED review activity; no approval |
| Codex | Unverified |
| Hugging Face | Prior BUILD_ERROR; no deployment |
| Kaggle | Untested; no submission |
| Databricks | Prior HTTP 403; no workspace write |

Map: [nine-platform capability/authentication/data-flow map](https://github.com/Barrot-Agent/B-Agent/blob/integration/core-capabilities-mmi-structural-paper-20261104/research/xrp_intelligence/nine_platform_capability_authentication_dataflow_map_current.json).

## PR backlog and overlap classification

- **#1640 — blocked integration:** sole active V3/XRP integration PR. 895 ahead / 0 behind, 230 changed paths, GitHub reports mergeable/clean.
- **#1643 — unique/unreviewed research:** 670 paths; 663 unique relative to #1640, 7 overlapping. Its base is older than current main. Preserve the unique evidence archive.
- **#1653 — unique/unreviewed repository graph:** 7 paths; 6 unique and 1 CI overlap. Eight review threads remain unresolved. Preserve unique MCP/codebase-memory work.
- **#1642 — superseded candidate:** all 7 changed paths overlap #1640.
- **#1317, #1318, #1320 — superseded candidates:** all changed paths overlap #1640; retain until successor content is verified on main.
- **#1644–#1650 — dependency/action overlap candidates:** changed paths overlap #1640; reconcile exact versions and workflow behavior before closing.
- **#1254/#1255 — older dependency candidates:** retain until exact-version reconciliation.
- **#1269 — unique/unreviewed:** 8 unique mesh/topology paths plus one CI overlap; preserve.
- **#1655/#1659 — unique draft material:** preserve unique portions; no bulk closure.

No PRs were closed. The remaining draft inventory contains many older XRP, prediction, safety and workflow proposals; classify exact overlaps before any closure.

## Merge decision — BLOCKED

PR #1640 has 62 review submissions, all **COMMENTED**, zero **APPROVED**, and no requested reviewers. Its 22 review threads are all resolved but outdated. The review history is not an independent approval of the current head.

- Main reports `protected=true`, but the detailed branch-protection endpoint returns HTTP 403 (“Resource not accessible by integration”). Effective required approvals/check contexts remain unverified.
- The only visible fallback ruleset is disabled.
- The repository is public and has GitHub Pages enabled. Main push `d4d43be` triggered successful [Pages build/deployment run 42526890275](https://github.com/Barrot-Agent/B-Agent/actions/runs/42526890275). PR #1640 changes public `web/` assets, so merging it would trigger another public Pages deployment. Specific authorization for that publication is absent.
- The new scheduled XRP ingestion workflow is read-only, but it is not on main yet.

**Do not merge** until an independent approving review is obtained, effective branch-protection requirements are verified, exact-head checks remain green, and the Pages publication side effect is specifically authorized. Never bypass branch protection.

## Raw spot-response receipts — exact surfaced JSON text

These hashes cover the exact JSON response text surfaced by public API retrieval, not original HTTP wire bytes. Response headers and exact retrieval timestamps were not exposed by the web retrieval path. These records are research receipts only and are **not model-admitted**.

```json
{
  "capture_scope": "exact JSON response text surfaced by public API retrieval",
  "raw_http_wire_bytes_preserved": false,
  "response_headers_preserved": false,
  "retrieval_timestamp_exactly_exposed": false,
  "provider_event_time_utc": {
    "kraken_xrpusd": null,
    "okx_xrpusdt": "2026-11-10T03:27:27.968Z",
    "kraken_usdtusd": null
  },
  "sha256": {
    "kraken_xrpusd": "da420383dfb0a8f0d6dce4c892e498aec97b835d9b1f0a567e1022fa86dd1790",
    "okx_xrpusdt": "cbeb00856f8f4894782f061f4b345b2dcfb69c9aad0d2b1147fa9f22039bad6a",
    "kraken_usdtusd": "c8abaa69e223c06d1c1fee1ef48f0a75ff0b1dabf6028429afd2beecaf0907e5"
  },
  "raw_response_text": {
    "kraken_xrpusd": "{\"error\":[],\"result\":{\"XXRPZUSD\":{\"a\":[\"1.09158000\",\"1244\",\"1244.000\"],\"b\":[\"1.09147000\",\"831\",\"831.000\"],\"c\":[\"1.09187000\",\"1.05089589\"],\"v\":[\"2746644.33606185\",\"27418112.44154435\"],\"p\":[\"1.09647138\",\"1.09506948\"],\"t\":[3370,36296],\"l\":[\"1.08912000\",\"1.07502000\"],\"h\":[\"1.10404000\",\"1.11573000\"],\"o\":\"1.09748000\"}}}",
    "okx_xrpusdt": "{\"code\":\"0\",\"data\":[{\"instType\":\"SPOT\",\"instId\":\"XRP-USDT\",\"last\":\"1.0936\",\"lastSz\":\"582.76968\",\"askPx\":\"1.0938\",\"askSz\":\"7370.790268\",\"bidPx\":\"1.0937\",\"bidSz\":\"260.296779\",\"open24h\":\"1.1099\",\"high24h\":\"1.1167\",\"low24h\":\"1.0764\",\"volCcy24h\":\"75950210.014235668\",\"vol24h\":\"69302465.895863\",\"ts\":\"1794281247968\",\"sodUtc0\":\"1.0988\",\"sodUtc8\":\"1.1144\"}],\"msg\":\"\"}",
    "kraken_usdtusd": "{\"error\":[],\"result\":{\"USDTZUSD\":{\"a\":[\"0.99866000\",\"238387\",\"238387.000\"],\"b\":[\"0.99865000\",\"870693\",\"870693.000\"],\"c\":[\"0.99865000\",\"9.10419579\"],\"v\":[\"42895856.85833851\",\"299175045.79945031\"],\"p\":[\"0.99872008\",\"0.99879313\"],\"t\":[7562,53340],\"l\":[\"0.99865000\",\"0.99850000\"],\"h\":[\"0.99877000\",\"0.99918000\"],\"o\":\"0.99872000\"}}}"
  }
}
```

## Next concrete actions

1. Keep #1640 as the single active V3/XRP integration path; no new duplicate PRs.
2. Obtain independent approval and authoritative visibility into main branch protection.
3. Resolve explicit authorization for the automatic GitHub Pages publication before merging.
4. Keep the ETF Nov 9 snapshot partial until all four daily-tracked funds publish; preserve the 02:52 1/4 and 03:22 2/4 cutoffs separately.
5. Reconcile XRP exchange-balance wallet-set changes and Binance gross transfers without netting unrelated methods.
6. Keep CFTC TFF weekly until the semiweekly effective date and applicability to financial futures are confirmed.
7. Add independent WORM/timestamp anchoring only through an authorized destination; current GitHub artifact retention is bounded.
8. Build synchronized historical spot/L2/derivatives/exchange-flow/collateral features, then evaluate baselines and calibrated walk-forward lift before any forecast.
9. After any authorized merge, fetch main again, verify the merge commit/files, run main CI, inspect automatic workflow side effects, and close only exact duplicate/superseded PRs whose content is verified on main.

No merge, deployment, secret rotation, Space restart, Kaggle submission, Databricks write, external-model transfer, paper trade, funds transfer, real-money action, force-push or destructive worktree operation occurred.
