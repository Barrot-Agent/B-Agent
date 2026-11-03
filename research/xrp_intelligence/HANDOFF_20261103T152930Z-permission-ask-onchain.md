# Permission ASK on-chain sample — 2026-11-03 15:29 UTC

## Question
Permission's official tokenomics page claims that a portion of parent subscription revenue is used to buy ASK on the open market. This pass looked for transaction-level evidence of that claimed capital path.

## Observed sample
- BaseScan indexed a May 12, 2026 transaction with 916,922.574548 ASK transferred to the zero address; the same transaction page shows a small internal ETH transfer to LayerZero EndpointV2.
- A separate BaseScan-indexed transaction shows 551,026.043904 ASK transferred to the zero address, again with an internal fee transfer to LayerZero EndpointV2.
- Another BaseScan event shows an `OFTSent` event for 551,003.115694 ASK from the same sender address, destination endpoint ID 30109. It is a different transaction hash; the similar amount is not treated as proof that the burn and send are the same event.
- PolygonScan shows an unlimited ASK allowance to the official Base ASK contract on April 25, 2025. An allowance does not prove a purchase.
- One BaseScan transaction contains both ASK and USDC transfer events, but the indexed snippet did not expose the full context or USDC amount.

## Interpretation
The zero-address burns, LayerZero endpoint fees and OFTSent event are consistent with omnichain OFT bridge mechanics. They are not evidence of a subscription-funded market buyback. The allowance and multi-token transaction are also insufficient to classify a buyback. No revenue wallet, buyback wallet, DEX purchase route or subscription-to-ASK reconciliation was identified.

Direct BaseScan page opens returned 403 in this pass; transaction details came from indexed search results. The sample is not exhaustive.

## Status
- Permission's buyback mechanism: **issuer claim, not independently verified**
- Actual ASK market purchases funded by subscriptions: **not established**
- "Actual capital" phrase: **unresolved**
- XRP/Ripple relationship: **none established**
- Forecast: **NOT ISSUED**

## Next
Obtain full traces, identify any publicly disclosed revenue/buyback wallets, and distinguish market purchases from bridge burns, liquidity operations, approvals and reward distributions. Do not claim actual capital deployment until a traceable cash-to-token path is established.
