# XRP ETF primary-issuer holdings and point-in-time reconciliation

**Reference:** 2026-11-08 09:07:27 UTC  
**Research PR:** #1643  
**Prior correction clarified:** the Canary file labelled 9 Nov was published 7 Nov and mapped to 6 Nov by the aggregator. It is not future availability relative to the run.

## Primary issuer observations

- **Grayscale GXRP, Nov 6:** 64,838,291.2993 XRP; 3,350,100 shares; $75.953M AUM. BNY administrator; Coinbase Custody and Anchorage custodians.
- **21Shares TOXR, Nov 6:** $126.272M AUM, $11.46 NAV, 2,962.14 shares daily volume. Issuer says it holds XRP and names Anchorage, BitGo and Coinbase Custody; the rendered underlying-assets table did not expose XRP units.
- **Franklin XRPZ, Nov 4:** 310,430,333.34 XRP; 28.6M shares; Coinbase Custody. The rendered issuer page did not show Nov 6 holdings.
- **Bitwise XRP, Nov 5:** 415,365,129.04 XRP; 37.21M shares; BNY trust custodian and Coinbase Custody digital-asset custodian.
- **Canary XRPC, Nov 6 NAV table:** $286.859M net assets, $12.48 NAV, 22.99M shares; the same share count appears on Nov 5. A separate issuer holdings section labelled Nov 9 shows 242.963M XRP and 22.92M shares.
- **REX-Osprey XRPR, Nov 5:** $40.954M assets, 4.075M shares and four holdings; its 80% policy allows direct or subsidiary exposure. Do not count it as a pure spot XRP holding without full underlying exposure.

## Corrected CryptoKeyhole file-date interpretation

CryptoKeyhole says its Canary file labelled 9 Nov was published/read on 7 Nov 2026 at 05:07–05:12 UTC and maps to 6 Nov because the file is dated one trading day after the previous trading day's orders. The file-date label is future relative to the run date, but the information was available before the 8 Nov cutoff. Preserve issuer file date, effective trading date and availability time separately.

The Nov 6 CryptoKeyhole result remains **partial at 3/4 funds**: Bitwise 0 XRP, XRPC -752,048 XRP, TOXR 0 XRP; Franklin XRPZ missing. Its Nov 5 complete four-fund flow is -3,339 XRP and holdings are 1,076,805,885 XRP.

## Unresolved discrepancy

Canary's Nov 6 daily NAV table shows 22.99M shares, unchanged from Nov 5. Its separate Nov 9 holdings section shows 22.92M shares and 242.963M XRP. CryptoKeyhole maps the Nov 9 file to Nov 6 and reports -752,048 XRP. The file was available before the run, but the 70,000-share discrepancy and holdings-flow calculation remain unresolved.

Grayscale's issuer page shows 64.838M XRP as of Nov 6, while CryptoKeyhole uses a June 30 SEC figure because its own automated read is blocked. REX is excluded from the daily flow series because its daily file does not show total indirect exposure.

**Model admission: excluded. Forecast: NOT_ISSUED.** No paper trade or real-money action occurred.
