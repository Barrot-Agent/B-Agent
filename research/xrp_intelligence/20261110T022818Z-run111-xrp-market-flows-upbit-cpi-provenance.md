# Run 111 — XRP market, exchange-flow and provenance research

**Capture window:** 2026-11-10 02:28–02:30 UTC  
**Verified code/test head:** \`d28612a2ac04e93338b0a8774a75fdc8181c3bbd\`  
**Forecast:** NOT_ISSUED

## Spot cross-check

| Source | Last | Bid / ask | 24h XRP volume | Provider time |
|---|---:|---:|---:|---|
| Kraken XRP/USD | $1.09175 | 1.09174 / 1.09175 | 29.752M | Not supplied |
| OKX XRP-USDT | 1.0938 USDT | 1.0938 / 1.0939 | 71.886M | 02:23:18.267 UTC |
| Kraken USDT/USD | $0.99870 | 0.99869 / 0.99870 | 281.397M | Not supplied |

Using Kraken's asynchronous USDT/USD last to normalize OKX gives approximately $1.092378, 0.0575% above Kraken's displayed last. This is not an executable arbitrage calculation. The OKX timestamp was approximately 300 seconds old at run start, and exact web retrieval time was unavailable. No synchronized L2 depth was captured.

The SHA-256 values in the JSON artifact cover the exact JSON text surfaced by the web renderer, not original HTTP wire bytes. These observations are model-ineligible.

## Exchange balances are not tradable float

XRP Insights reports 22.35B XRP across 701 attributed wallets at 24 exchanges, based on a daily snapshot at 2026-11-09 08:01 UTC. The snapshot was approximately 18.455 hours old at capture.

- Same-wallet change: −25.8M XRP over 7 days; −138.1M over 30 days.
- November 9 daily same-wallet change: +9.7M XRP.
- Naive total change: +373.9M XRP, including two newly tracked wallets holding 512M XRP.
- Approximately 48.4% cold-labeled, 12% hot-labeled and 40% unclassified.
- Approximately 483M XRP in wrapped/insurance/other reserves; another 323M XRP in labeled wallets at about 36 exchanges outside the tracked set.

The provider reads XRPL account_info daily, uses XRPSCAN wallet labels, retains last-good balances on failed reads, adds wallets above a 100,000 XRP threshold and does not publish per-wallet historical series. This is labeled-wallet coverage, not proof of reserves, customer liabilities or total tradable float. The endpoint remains raw-only/model-ineligible.

## Conflicting Binance flows

CryptoQuant/Darkfost reported a 691M XRP gross inflow on Nov 8 and a 418.5M XRP gross outflow on Nov 4. These are the same provider and analyst, on different dates. Do not net them. Deposits do not prove sales; withdrawals do not prove accumulation. Reserve replenishment after the Oct 29 Binance incident is one unconfirmed hypothesis.

## Korea and ETF activity

CryptoTicker reports 138.7B KRW of Upbit XRP turnover, approximately $102M and 17% of the venue's 24-hour turnover. It also reports declining daily XRP turnover from 178.2B KRW on Nov 5 to 76.8B on Nov 8. Volume is turnover, not net new capital. Its kimchi-premium conversion uses the Nov 6 ECB USD/KRW rate, so it is not a contemporaneous FX comparison.

Bitcoin.com News, citing SoSoValue, reports a $529,500 XRPC outflow on Nov 2 and zero net flows Nov 3–6. Cumulative net inflows were reported at $1.81B and net assets at $1.34B. The underlying tracker was not directly accessible in this run; this remains secondary-source reporting, not issuer-level reconciliation.

## Macro event

The BLS scheduled October 2026 CPI for Nov 10 at 08:30 ET / 13:30 UTC. It had not been released at capture.

## Competing hypotheses

1. **Distribution pressure:** large gross Binance deposits, no reported ETF net inflows in the cited tracker window, and weak Korean premium/turnover could indicate limited marginal demand.
2. **Reserve/internal rebalancing:** the Nov 4 Binance outflow, same-wallet exchange balance declines and possible reserve replenishment show that gross exchange transfers are not equivalent to executed sales.
3. **Deleveraging exhaustion:** long liquidations and falling turnover could precede stabilization, but no synchronized L2 depth or validated spot CVD confirms absorption.

No directional forecast was issued. All web observations remain outside the model feature store.
