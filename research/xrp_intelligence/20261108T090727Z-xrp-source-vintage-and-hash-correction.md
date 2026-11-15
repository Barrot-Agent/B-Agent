# XRP source-vintage and hash correction overlay

**Reference time:** 2026-11-08 09:07:27 UTC  
**Original market/ETF/institutional artifact:** `20261108T090727Z-xrp-market-etf-derivatives-institutional-reconciliation.json`  
**Research PR:** #1643

## Corrections

1. **Alpha Finance receipt hash:** the stored SHA-256 hex string was transcribed incorrectly. The unchanged excerpt recomputes to `7a72694b88f6f2b2e6fa25eea787169c5b5526a9be6118527981d14818bcc5bf`. The original artifact is preserved; this overlay records the correction.
2. **FundingRates.app:** opening the URL rendered a page dated November 3, not November 8. The previously indexed November 8 search snippet is quarantined as unverified. No November 8 FundingRates observation is verified.
3. **Kodexius:** the later rendered page snapshot at 08:29 UTC reports $785.20M OI, +0.0091% weighted funding and $707.47M 24h volume across seven contracts. The earlier $775.07M snapshot at 01:19 UTC remains historical.
4. **XRP Insights:** the undated live dashboard displays $1.40723B AUM, 1.19518B XRP locked and -0.81M XRP Week 45 flow. These undated values remain separate from its dated November 6 row (-663,043 XRP, approximately $1.43B net assets).
5. **CryptoKeyhole:** November 6 remains partial at 3/4 funds, with -$887K shown for XRPC; the November 9 issuer-file date is future relative to the November 8 page update and quarantined.
6. **TradRadar:** its November 8 08:20 UTC page explicitly says the figures are delayed by 15 minutes.

No source correction creates a synchronized market cutoff. OI, funding and ETF values remain research-only; no forecast is issued.
