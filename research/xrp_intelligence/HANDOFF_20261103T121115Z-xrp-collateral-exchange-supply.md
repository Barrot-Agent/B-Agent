# XRP Intelligence Handoff — 2026-11-03 12:11:15 UTC

## Priority
XRP intelligence and prediction-engine mastery. Barrot V3 remains the execution, security and verification foundation.

## New finding: collateral eligibility is route-specific
- Coinbase Global Exchange explicitly lists XRP as eligible collateral for perpetual futures. Organization-level average-daily-quantity caps and haircuts apply; collateral can be liquidated.
- Deribit’s September 28, 2026 cross-collateral table lists XRP as a cross-collateral currency, with a 15% X:SM haircut. This supersedes older Deribit documentation that described XRP as offset-only.
- Coinbase Prime Global Derivatives through CFM publishes USDC, BTC and ETH as eligible collateral. XRP is not in that route’s published list.
- Coinbase International Exchange institutional accounts migrated to Deribit on October 1 through Coinbase Bermuda Limited, with Cross Standard Margin as the default. The FAQ does not expressly enumerate XRP for every migrated account. Deribit-wide XRP support is therefore not proof of account-specific Coinbase eligibility.
- CFTC Letter 26-17 lists XRP as a digital-commodity example and establishes a conditional no-action structure for the described CFM/CBBM/Deribit transfer of customer digital assets as margin. It does not prove XRP was actually accepted or posted. The CFM/Prime route’s current published collateral list remains USDC/BTC/ETH.

## New XRP supply snapshot
XRP Insights’ November 3 page reports 22.34B XRP across 701 publicly attributed wallets at 24 exchanges, read via rippled account_info at approximately 08:00 UTC and attributed using XRPSCAN labels. This is a floor; most balances are customer deposits in omnibus wallets, not proprietary inventory or immediately available sell-side float.

Provider-reported concentrations:
- Upbit: 6.43B XRP (28.8% of tracked exchange balances).
- Coinbase: 5.83B (26.1%).
- Binance: 2.70B (12.1%).
- South Korea: 8.58B; United States: 8.48B; Japan: 1.38B, based on exchange headquarters.

The same source reports 151.5M cbXRP, 19.4M wXRP and 418.4M XRP in DeFi/AMM/bridge/wrapped categories. It warns that some exchange-wallet totals include reserves backing wrapped assets, so category totals may overlap.

Additional provider observations:
- RLUSD: $2.55B across XRPL and Ethereum, with $859M on XRPL and $1.69B on Ethereum; other deployments may be excluded.
- XRPL RWA: $4.33B total, but only $276M transferable/distributed; $4.06B is represented/platform-locked registry notional.
- Seven ETF/index products: 1.20B XRP, with issuer holding dates varying from Sep 28 to Nov 2.

## Causal hypotheses
1. XRP collateral support may increase holding utility, but collateral utilization and incremental spot buying are unknown.
2. Cross-collateral haircuts and margin calls may create procyclical liquidation risk, but no XRP-specific collateral utilization/liquidation series is available.
3. Coinbase-labeled XRP balances likely include customer custody/omnibus balances; they are not a Coinbase proprietary bullish position.
4. XRPL stablecoin/RWA growth can raise network activity without proportionate XRP demand; fees, reserves and market-making channels need measurement.
5. Exchange wallet concentration is a liquidity/custody indicator, not a direct tradable-float measure.
6. Coinbase’s derivatives consolidation may improve capital efficiency, but eligibility differs by product, legal entity and customer route.

## Prediction status
NOT_ISSUED. No calibrated directional forecast or paper position was created. The new data establish product eligibility and provider-reported supply structure, not predictive price skill.

## Architecture decisions
Store collateral eligibility by platform, legal entity, product, jurisdiction, account type, asset and effective date. Store haircuts separately by margin model. Store actual utilization as unknown until reliable balances are disclosed. Store exchange balances by wallet label, ledger index, timestamp and attribution version. Reconcile wrapped-token backing before summing supply categories. Separate transferable RWA float from represented registry notional.

## Sources
- CFTC Letter 26-17: https://www.cftc.gov/csl/26-17/download
- Coinbase Global Exchange collateral: https://help.coinbase.com/en/global-exchange/margin-requirements/how-does-cross-collateral-work
- Deribit cross collateral: https://support.deribit.com/hc/en-us/articles/25944777203869-Cross-collateral-specifications
- Coinbase Prime derivatives: https://help.coinbase.com/en/prime/derivatives-on-prime
- Coinbase International Exchange migration: https://help.coinbase.com/en/international-exchange/deribit/institutional-faqs
- XRP Insights Radar: https://xrp-insights.com/xrp-radar

## Next actions
1. Circle Q3 results, Nov 4, 2026 13:00 UTC.
2. Verify XRPL fixCleanup3_4_0 activation via validated EnableAmendment and following ledger.
3. Confirm account-specific XRP collateral eligibility for migrated Coinbase International Exchange clients.
4. Reconcile cbXRP backing and Coinbase-labeled exchange-wallet balances.
5. Reconcile contract-level XRP derivatives OI and liquidations.
6. Continue fixed-horizon walk-forward evaluation, leakage prevention, calibration and independent attestation.
