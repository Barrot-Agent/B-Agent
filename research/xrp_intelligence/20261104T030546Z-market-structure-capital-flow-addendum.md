# XRP market structure and capital-flow addendum — 2026-11-04 03:05 UTC

## Capture and repository state

- Captured: 2026-11-04T03:05:46Z
- Data cutoff: 2026-11-04T03:05:00Z
- Main inspected: `d89cc363812a9a9d04d076d6ef5a09f7cf736285`
- Research PR base: `162f43d29970db9abebfec1b7872601a9d659037`
- PR #1622 head before this addendum: `b09aae906139824ae2bc71b351348115e2ba6d46`
- Main advanced by one generated Cross Analysis refresh. The only changed main path is `ping-pongings/knowledge-base/sentiment_shift.json`; it does not overlap the research PR's changed paths.

## Derivatives snapshot

TradRadar's 2026-11-04 02:25 UTC snapshot reports XRP perpetual mark price $1.2532, aggregate open interest $1.95B across seven exchanges, 24-hour OI change +0.10%, funding +0.0100% per eight hours, 77.3% long accounts, and at least $5.37M liquidations (long $2.63M; short $2.74M). Its venue list is Binance, Bybit, Gate, Bitget, MEXC, Hyperliquid and OKX.

Kodexius at 2026-11-03 22:04 UTC reports $870.32M across seven contract instruments, +0.0100% funding and $1.19B 24-hour volume. Its listed instruments differ from TradRadar's exchange universe. The snapshots are 4h21m apart. **Do not average these values or infer manipulation from the gap.** Reconstruct exchange-native contract IDs, quote units, multipliers, venue inclusion and timestamps first.

The long-account skew is a positioning warning, not a directional signal. Account counts are not notional exposure, and liquidations were approximately balanced in TradRadar's snapshot.

## ETF flow discrepancy

XRP Insights reports Nov 2 holdings change of -32,825 XRP (approximately -$42K) and 1,196,567,361 XRP held across six spot ETFs plus BITW's XRP sleeve. Its Nov 3 row is provisional; excluded/capture-gap fund flows contribute zero.

ByKaranteli reports -$530K on Nov 2, +$1.81B cumulative net inflow and $1.42B net assets. Its recent row is also provisional. Fund scope and flow methods differ.

This is an **unreconciled data-quality discrepancy**, not evidence of hidden buying or selling. Rebuild from each issuer's daily holdings and creation/redemption records at a common market close.

## Circle economics

Circle's Oct 16 issuer-authored article states that USDC settled more than $36T on-chain in H1 2026, Circle minted and redeemed more than $315B, and $819M went to distribution partners and transaction costs. It reports approximately 77% of global stablecoin transaction volume by June and says Circle reinvested about $473M in licenses, banking relationships, settlement liquidity, compliance and integrations, retaining seven cents of net profit per dollar of revenue.

These are Circle's own figures. Gross on-chain settlement and gross mint/redemption are not net new capital, and neither is XRP transaction volume. SEC reconciliation remains required.

## Ripple National Trust Bank

Ripple's Oct 26 release says the OCC granted final approval to Ripple National Trust Bank, with reserve-management, collateral-trustee and fiduciary custody roles for RLUSD. The release says Standard Custody & Trust Company remains RLUSD's issuer.

Classification: **issuer-sourced regulatory claim**. A separate OCC final decision document was not located in this run. Final approval is not proof that the bank has opened or commenced operations. Do not upgrade this claim to regulator-verified until the OCC record is located.

## SBIC identity

Tokyo SBIC's official site identifies Tokyo Small and Medium Business Investment & Consultation Co., Ltd. and describes a long-term stable-shareholder/equity-support role for Japanese SMEs. Its official Feb 26, 2025 page records a ChatGPT/generative-AI seminar. This establishes the Tokyo entity and event only; it does not establish SBI Holdings affiliation, an OpenAI partnership or an XRP relationship.

## Source quarantine

A dynamic Swiftedge page returned internally inconsistent timestamps, including a session high later than this run's capture cutoff and a separate update timestamp that did not align with the displayed current session. It was quarantined and not used as a model input.

## Competing hypotheses

1. Provider OI differences are explained primarily by contract/venue coverage and capture time.
2. High long-account share plus positive funding increases liquidation sensitivity but does not imply direction.
3. ETF flow differences are caused by provisional settlement, fund scope, excluded rows or capture methodology.
4. Circle's gross USDC activity demonstrates network scale but is not evidence of XRP demand.
5. Ripple's trust-bank structure could de-risk RLUSD institutionally, but any XRP benefit is indirect and unproven.

## Prediction status

**NOT_ISSUED.** No directional XRP forecast is supported by this snapshot. Historical feature storage and walk-forward evaluation remain incomplete.

## Next actions

- Reconstruct exchange-native derivatives data with normalized instrument definitions.
- Reconcile ETF holdings from issuer sources at a common close.
- Review Circle Q3 2026 results after the scheduled Nov 4 08:00 ET release.
- Locate the direct OCC decision and verify Ripple National Trust Bank commencement.
- Preserve all provider disagreement and minority hypotheses.
