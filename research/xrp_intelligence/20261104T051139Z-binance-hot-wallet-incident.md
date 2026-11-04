# XRP research addendum — Binance hot-wallet incident and 233.46M XRP outflow

**Captured:** 2026-11-04T05:11:39Z
**Incident:** October 29, 2026
**Prediction status:** NOT_ISSUED

## Incident facts

Binance's November 3 report estimates approximately **$6.34B** of affected digital assets and approximately **$2.85B** frozen or intercepted, subject to reconciliation. It says 98% of affected token assets were replenished as of October 31 and that company resources cover user balances. Gross affected assets, frozen assets, customer-balance replenishment and recovery of stolen tokens are different measures.

Binance says five hot wallets sent **233,461,943.1 XRP** to one account between 20:05 and 20:09 UTC on October 29. XRPLWin reconstructs five valid signed XRPL payments and values the XRP at approximately **$296M** at transfer time. The evidence points to compromised exchange signing authorization, not an XRPL protocol exploit.

The FBI formally attributed the broader theft to North Korea's TraderTraitor activity. North Korea publicly denied the attribution on November 3. Both claims are preserved; no judicial finding is asserted.

## Subsequent XRP movement

The October 30 XRPLWin snapshot said the initial receiving account had no outbound transactions at that time. That was superseded. Tibane Labs' November 3 ledger reconstruction reports that on November 2 the original 233.46M XRP was redistributed through nine main payments to six new wallets, plus a separate 1,000 XRP test destination. At its November 3 07:27 UTC cutoff, none of the seven recipient addresses had outbound transactions. This is not a live November 4 status check.

Whale Alert indexes a 40M XRP transaction at 03:56:21 UTC on November 2. That is one transaction within the redistribution, not the entire 233.46M XRP.

## Market-intelligence implications

1. Do not classify the 233.46M XRP transfer as organic exchange selling, whale distribution or self-custody accumulation. It is a known security incident.
2. Binance says it replenished customer backing using company resources. That is not proof the original stolen XRP was recovered.
3. Ripple reportedly froze about 40.5M RLUSD on Ethereum. Native XRP has no issuer freeze or clawback control.
4. Reuters reported Circle had frozen more than $1.1B USDC by November 2, versus XRPLWin's earlier October 30 $823M snapshot. These are different dated snapshots; do not average.
5. Reuters reported $4.72B net Binance customer outflows since reopening, about 3% of platform assets; Binance also reported $2.7B in inflows since Sunday and stabilizing withdrawals. Most withdrawals were in USDT. These are exchange-wide, not XRP-specific.
6. Binance's account describes compromised devices, fake recruitment/interviews, internal AI tooling and unauthorized signing-service access. The AI tool is not established as the initial vulnerability. The engineering lesson is least privilege, isolated credentials, signing boundaries, time-bound approval and immutable audit logs.

## Required model-data treatment

Create a security-incident flag keyed to the five originating hot wallets, the original receiving account, six main recipient wallets and the separate test destination. Preserve raw transaction hashes and ledger indices. Exclude the 233.46M XRP movement from organic exchange-flow and whale-flow features unless represented as a separate incident variable. Track later movement, exchange deposits, DEX activity and bridge use independently.

## Sources

- [Binance official initial incident report](https://www.binance.com/en-AE/square/post/11-03-2026-binance-initial-report-fbi-attributes-6-34-billion-attack-to-north-korea-which-used-fake-job-interviews-and-an-ai-tool-to-reach-hot-wallets-users-fully-covered-384321660235967)
- [FBI TraderTraitor attribution](https://www.fbi.gov/investigate/cyber/alerts/2026/north-korea-responsible-for-6-billion-binance-attack)
- [Reuters: Binance replenishment](https://www.reuters.com/legal/government/binance-says-90-stolen-assets-replenished-2026-10-31/)
- [Reuters: customer outflows after reopening](https://www.reuters.com/business/finance/binance-sees-outflows-stabilising-exchange-returns-online-after-63-billion-heist-2026-11-02/)
- [XRPLWin: initial XRP drain reconstruction](https://xrplwin.com/insights/the-63-billion-binance-hack-233-million-xrp-drained-on-the-xrp-ledger)
- [Tibane Labs: public XRPL transaction reconstruction](https://www.tibane.net/research/binance-hack)
- [Whale Alert: 40M XRP transaction](https://whale-alert.io/transaction/ripple/3AAA8BEE45ADFD6833A2CAED9E28D00F82C20278F730BA722B79DB453B0E617D)
- [AP: North Korea denial](https://apnews.com/article/01c9b80d938dd67c747e268c410f265d)