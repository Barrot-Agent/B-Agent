# XRP Research Index — Run 70

This index groups the Run 70 append-only evidence packages committed to the existing XRP research workstream. It is not a forecast and does not admit the cited institutional/incident facts as directional price features.

## Evidence packages

| Package | Evidence focus | Regression tests |
|---|---|---|
| [Binance hack / XRP-flow reconciliation](20261108T211453Z-binance-hack-xrp-flow-derivatives-cross-ledger-reconciliation.json) | 233.46M XRP theft, exchange-flow timing, wallet attribution, frozen/intercepted assets, laundering status, derivative-provider vintage | [test](../../tests/test_xrp_binance_hack_flow_derivatives_reconciliation_20261108.py) |
| [Stablecoin freeze vs native-XRP control](20261108T213528Z-xrp-stablecoin-freeze-native-asset-control-reconciliation.json) | 40.5M RLUSD on-chain freeze vs reported $200M Ripple stop claim; Circle/Tether/other issuer controls; native XRP cannot be protocol-frozen | [test](../../tests/test_xrp_stablecoin_freeze_native_asset_control_reconciliation_20261108.py) |
| [SBI Ripple Asia ownership and XRP utility](20261108T213528Z-sbi-ripple-asia-ownership-xrp-utility-reconciliation.json) | SBI Group aggregate 60% voting rights, historical ODL XRP bridge use, XRPL-only PoC distinction, RLUSD and Visa reward distribution | [test](../../tests/test_sbi_ripple_asia_ownership_xrp_utility_reconciliation_20261108.py) |
| [Coinbase / Circle / SBI / Ripple / Binance relationship reconciliation](20261108T214524Z-coinbase-circle-sbi-ripple-binance-relationship-reconciliation.json) | Coinbase-Circle USDC economics, Circle SBI Japan K.K. 50/50 JV, Binance $100M equity investment and five-year USDC incentive agreement, Coinbase XRP/RLUSD disclosures | [test](../../tests/test_coinbase_circle_sbi_ripple_binance_relationship_reconciliation_20261108.py) |

## Critical interpretation rules

- **SBI Ripple Asia** and **Circle SBI Japan K.K.** are separate joint ventures. The former is an SBI/Ripple entity with SBI Group aggregate voting rights reported at 60%; the latter is a 50/50 Circle/SBI Holdings entity that Circle controls and consolidates, with no significant operating results reported in Circle's Q3 2026 filing.
- **SBI VC Trade's RLUSD handling** is a stablecoin distribution channel. It does not establish XRP as the settlement asset for every RLUSD transfer.
- **Coinbase's XRP holding / commercial-engagement flags** are dated to March 31, 2026, are unquantified, and do not prove customer collateral balances. cbXRP is a separate wrapped asset.
- **Coinbase RLUSD availability** on Prime, Exchange and retail is distinct from Global Exchange collateral, which Coinbase described as a later phase at launch.
- **Circle's USDC onchain volume** is not net payment demand. Q3 minted and redeemed gross amounts are separate from the $610M net issuance.
- **Circle/Binance's $100M equity investment** and USDC incentive agreement are not XRP purchases or a Ripple partnership.
- **Native XRP cannot be frozen at the XRPL protocol level**; custodial exchanges can still restrict balances/withdrawals in their own systems.
- **The $200M Ripple stop claim** attributed to Binance co-CEO Yi He is not reconciled to TRM's 40.5M RLUSD attacker-wallet freeze. Preserve the disagreement.

## Provenance and admission

- SEC filings and official issuer releases are primary for the parties' own balances, contracts and stated product availability.
- Related-party filings are not independent third-party confirmation of XRP demand.
- All artifact receipt hashes are scoped to the exact surfaced excerpt strings, not raw HTTP wire bytes.
- Institutional, stablecoin and incident facts remain event-timeline/context data only.
- Forecast status: **NOT_ISSUED**.
