# XRP market, Binance incident and XRPL amendment update

**Capture / data cutoff:** 2026-11-04T07:33:49Z  
**Main base:** `18da9c9981c744c2cf91bb936ecfddce96d3236d`  
**Prediction status:** NOT_ISSUED

## Binance XRP incident

Five Binance hot wallets transferred **233,461,943.1 XRP** to `rK21t6nGLy4MNDqhvy3pGwcLFy25qgfzMx` on October 29 between 20:05 and 20:09:20 UTC. Binance attributes the event to unauthorized access to its internal signing service; it is not described as an XRPL consensus exploit.

On November 2, public ledger reconstructions report redistribution to six new accounts plus a separate 1,000 XRP test destination:

| Destination | Reported balance |
|---|---:|
| `ryB7NESZcttqzRioiD5L6Kf5tFL87ktmx` | 40,001,000 XRP |
| `rKxwzjpZj5r9eXnCJQvLVUnebpGEHTDH1F` | 40,001,000 XRP |
| `rhfA8QzpcDPYX3safySLrvT5afnNjHc9XB` | 40,001,000 XRP |
| `rsNoNkb1zqMBR1rjbrasUzExqjCDXseisW` | 40,001,000 XRP |
| `rhXtRtpfZRAKVayWd5Z5kRJ2YXYkcuxNRD` | 40,001,000 XRP |
| `raoMrxbMFo5xpVfE9VPoEuVpv1CTtebm5t` | 33,455,920 XRP |
| Separate test destination `rJheAAxFoWNoTrfrt8N5GyAJLa559jWh4b` | 1,000 XRP |

A public tracker indexed a 04:12 UTC November 4 observation claiming no outbound transactions from the six recipient wallets. PANews' dynamic tracker separately displayed approximately 233 million XRP remaining at capture. This run did not query raw XRPL RPC for all six wallets, so the latest no-outbound statement remains a bounded secondary-source claim, not a direct verification.

**Arithmetic discrepancy preserved:** the reported recipient sum is 233,461,920 XRP. Initial transfer less the reported 23.69905 XRP residual implies 233,461,919.40095 XRP, leaving **0.59905 XRP** unresolved. The rounded figures are not forced to reconcile.

No sale, exchange deposit or beneficial owner is established. The incident transfer and redistribution are excluded from organic exchange-flow and whale-accumulation features.

## Attack-chain correction

Reuters' November 3 report describes a multi-stage compromise: a tampered Homebrew installation in June, a fake recruiter and malicious repository in September, an internal AI tool used on October 20 as a springboard to a container-deployment token, and malicious container execution on October 29. The AI tool is not established as the initial entry point.

## XRPL amendment clock

The newer XRPL.to November 4 ledger view reports **34/36** validators supporting `fixCleanup3_4_0`, with 29 required. XRPLWin's earlier snapshot reports 33/35. These are separate dated observations and are not averaged.

The earliest conditional activation is **November 4, 14:46:22 UTC**. At this cutoff it is not verified active. A direct `EnabledAmendments` ledger check is still required.

The amendment repairs issued-token permission handling, including a burn-only authorization bug, and other cleanup. It does not itself launch native XRPL lending. The newer tracker reports LendingProtocol at 19 votes and SingleAssetVault at 21, below 29 required.

## Market snapshot

- Yahoo Finance's November 3 daily row: XRP close **$1.2802**, volume approximately **$1.857B**.
- CoinGecko's November 4 page: displayed price approximately **$1.28**, 24-hour range $1.24–$1.29, 7-day range $1.20–$1.34, reported perpetual OI $4.137B, funding 0.0099% per 8 hours, and perps/spot volume ratio 14.3x.
- The first ten visible CoinGecko venue rows sum to approximately $2.334B OI, while the page reports 130 market rows. The page-level aggregate is not yet reconciled to the partial table.
- Altcoinlog displayed $1.2529 at 01:26 UTC, a stale and unsynchronized observation.

These data are not suitable for a directional forecast. No values are averaged across providers.

## Competing hypotheses

1. The Binance event materially contaminates ordinary XRP exchange-flow features.
2. The November 2 redistribution is currently evidence of wallet layering, not a verified sale.
3. `fixCleanup3_4_0` is a safety/maintenance amendment, not an immediate XRP-demand catalyst or lending launch.
4. High reported perpetual OI may amplify volatility but does not establish direction.
5. Stablecoin issuer freeze capability differs from native XRP custody/recovery; this is not itself a price signal.

## Next checks

1. Re-query all six recipient wallets and the separate test destination through two independent XRPL indexers at a common ledger index.
2. Verify `fixCleanup3_4_0` in `EnabledAmendments` after 14:46:22 UTC.
3. Review Circle's Q3 results after the 13:00 UTC webcast.
4. Reconstruct synchronized exchange-native spot, depth, OI, funding and liquidation features.
5. Continue historical feature-store population and chronological walk-forward evaluation against fixed baselines.

## Source register

The machine-readable JSON companion contains the complete source register, retrieval timestamps, source-independence groups, relationship graph, hypothesis support, disconfirming evidence, limitations and next actions.
