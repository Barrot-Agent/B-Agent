# Barrot XRP Intelligence Handoff — 2026-11-03T08:11:21Z

## Mission
XRP intelligence and measured prediction-engine mastery remain the highest-priority mission. Barrot V3 remains the execution, security and verification foundation.

## Repository
- Main base verified before branch creation: `ba121a1051c84ceb311e5c65e38a18659dcd7f0e`.
- Research branch: `research/xrp-exchange-liquidity-binance-phase2-20261103T0812Z`.
- Security PR #1570 was rebased onto current main and exact-head CI passed 362 tests + 8 subtests; its fail-closed gate passed. PR #1570 remains draft/open/unmerged.
- This research proposal is separate from security containment and is append-only.

## New findings
1. CoinGecko's 2026 CEX study uses 60 daily snapshots from July 6–September 3 at 16:00 UTC+8, across eight exchanges, and reports XRP depth of ~$18M bids/$14M asks across ±2%. Binance leads at the touch; Coinbase overtakes near 0.1% and retains the strongest median curve across the sampled range. This is historical resting liquidity, not live depth or executed flow.
2. The same report documents dynamic behavior: a July 31 escrow-day bid-depth increase with overall depth near its median, and unusually large Coinbase sell-side orders on August 23. These observations argue against treating a static Coinbase advantage as permanent or equating visible bids with new capital.
3. CoinGecko reports average XRP daily volume ~$1.8B during its study, peak ~$11.3B late August and ~$2.2B early September; XRPL RWA market capitalization ~$494M in July; and a $110.5M weekly XRP spot ETF inflow high for the week ending August 28. RWA capitalization and ETF holdings are separate from native XRP spot demand.
4. Binance's official verified profile lists native XRP on the XRP network as restored in Phase 1 on November 1. Binance reports $4.649B withdrawals and $1.01B deposits between 14:00 and 23:30 UTC+8, net outflows ~$3.64B (2.1% of its $171B AUM reference). These are exchange-wide, self-reported amounts, not XRP-specific flows.
5. Binance Recovery Update #6 (November 3) schedules phased withdrawals from 12:00 UTC+8 and its asset/network matrix includes BSC:XRP and XRP-network:RLUSD. This is a schedule, not proof both pairs were live. BSC XRP contract/issuer is unknown; do not equate it with native XRPL XRP. The profile's later restored-assets list explicitly showed Ethereum RLUSD, but did not yet confirm XRPL RLUSD live.
6. Reuters confirms additional withdrawals were scheduled for multiple networks from 04:00 GMT, but does not map each asset to each network. Do not use the Reuters network list to infer asset/network pairs.
7. Circle Q3 results are scheduled for November 4 at 08:00 ET / 13:00 UTC. No Q3 result is anticipated.

## Prediction architecture decision
Separate market-quality models (standardized slippage, depth persistence, next-interval realized volatility) from directional XRP return forecasts. Use point-in-time orderbook snapshots, venue-specific coverage, cancellation/replenishment data, executed notional and fixed-horizon walk-forward evaluation. Depth alone is not a price signal.

## Current forecast
NOT_ISSUED. No paper position or real-money action.

## Open unknowns
- Live orderbook after Binance's withdrawal reopening.
- Actual XRP-specific withdrawal/deposit amounts at Binance.
- Exact BSC XRP contract/issuer.
- Whether XRP-network RLUSD withdrawal support completed.
- Current native XRPL RLUSD transfer flows.
- Whether Coinbase's historical orderbook depth translated into actual institutional executions.

## Next actions
- Verify exact-head CI and fail-closed gate for this research PR.
- Obtain live venue orderbook snapshots with synchronized timestamps and depth bands.
- Verify Binance phase-2 asset/network status from official live withdrawal-status endpoints and map BSC XRP contract before treating it as XRP exposure.
- Reconcile Circle Q3 results with Coinbase USDC distribution economics after publication.
- Continue SBIC, ASK Coin and Wholesome Mils inventory; no new identity claim made in this artifact.

## Preservation
No main modification, merge, force-push, workflow dispatch, secret access, deployment, paper trade or real-money transaction. Explicit approval remains required for consequential external changes.
