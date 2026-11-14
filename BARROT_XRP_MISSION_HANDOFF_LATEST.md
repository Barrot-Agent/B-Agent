# Barrot XRP Intelligence — Canonical Mission Handoff (Run109)

Updated: 2026-11-14 00:18 UTC

**Mission priority 1:** XRP intelligence and measured prediction-engine mastery. **Protected foundation:** Barrot V3 execution, orchestration, safety, verification and external-action controls.

## 1. Repository state

- Repository: Barrot-Agent/B-Agent.
- Main SHA: fb272b40966834754ec686f9ed3ab94123f09306 (unchanged).
- Integration branch: integration/xrp-v3-unified-main-20261112.
- Code-bearing integration head verified in Run109: ff707656f1023713718dad137c54835372e6f272. This handoff/research update is a documentation-only descendant; see PR #1662 for the live branch head.
- At the code-bearing head: 2,319 commits ahead of main, zero behind; main tree 1,381 entries; integration tree 2,396 entries; 88 workflow files.
- Consolidated PR #1662: draft/open; 1,154 changed files, 334,661 additions, 5,354 deletions; 50 workflow files and seven public web files.
- Open PR inventory: 375 (361 drafts, 14 non-drafts). PR #1662 has zero formal reviews, zero approvals and zero review threads.
- Merged PRs in this run: none. Main remains unchanged. No new branch or PR was created.

## 2. Integrated architecture and execution status

**DESIGNED:** 50 public XRP source definitions; 45 hourly and three weekly CFTC schedules, with two non-commercial XRPL node endpoints excluded from scheduled collection; read-only main-only ingestion; SHA-256 raw receipts and local receipt chains; cross-run receipt-index continuity; SQLite point-in-time feature store; event timeline; source-independence registry; scenario/counter-hypothesis generation; four deterministic baselines; chronological walk-forward with purge/embargo; temporal calibration; PSI drift diagnostics; paired bootstrap; fail-closed forecast ledger.

**EXECUTED in Run109:**
- Added a source-cluster moving-block safeguard: minimum observations per source cluster must be at least the full bootstrap block length. Default block length and per-cluster minimum are both five origins.
- Upgraded forecast-readiness policy, report schema and Ed25519 attestation domain to v6. V1–V5 readiness reports are not accepted by the v6 ledger.
- Updated the packaged and root mission manifests to the same v6 policy and added regression coverage for block-length and manifest consistency.
- Reconciled the one full-suite failure on intermediate head 2bf89bee: the packaged mission manifest was v6 while the root copy remained v5. Both copies were synchronized on ff707656.
- Added this Run109 research record and refreshed the forecast-ledger contract.

**VERIFIED on code-bearing head ff707656:**
- Full repository suite: 3,625 passed, eight subtests, zero failures; 62.34% inclusive coverage; 93.28 seconds.
- Core tests: 739 passed.
- Wheel build and installed mission verification: passed.
- Dependency audit: five manifest groups passed, zero known vulnerabilities reported.
- Fail-closed gate: passed with merge disabled.
- Evidence: full CI 43532798292; dependency audit 43532805721; push fail-closed gate 43532798208; PR fail-closed gate 43532805701.
- PR-event core CI is explicitly skipped by the integration-branch workflow condition; the push-event full-suite run is the actual exact-head test.
- Main's last recorded full suite on unchanged main passed 747 tests and eight subtests (run 43343513172).

## 3. Prediction-engine readiness

Implemented on integration: 48 scheduled public endpoints; read-only main-only collector; SHA-256 receipts/local chain; point-in-time SQLite store; event and source-independence records; naive, momentum, mean-reversion and volatility baselines; leakage-safe chronological walk-forward with purge/embargo; calibration and PSI; paired temporal/source-clustered moving-block bootstrap; v6 fail-closed ledger with independent Ed25519 evaluator attestation.

Policy v6 requires candidate-versus-each-of-four-baselines comparisons for Brier score and log loss in both OOS and independent shadow cohorts; at least 10,000 bootstrap replicates; at least 100 paired origins per cohort; familywise confidence of at least 95% across eight comparisons (99.375% per interval); at least five receipt-backed source clusters; and minimum observations per cluster >= block length. Every required interval must have an upper bound below zero.

Important limitation: five clusters is only an admission floor. Small-cluster coverage, cluster-count sensitivity, block-length sensitivity and residual serial-dependence diagnostics still need simulation and empirical validation. Source clusters identify target-outcome publisher lineage; they do not prove independence among training-feature sources.

**No trained XRP-specific candidate model exists.** The walk-forward system evaluates deterministic baselines. Synchronized historical spot/L2/derivatives/flows/collateral data, independent WORM storage and trusted timestamp anchoring, mature independent shadow outcomes and demonstrated candidate superiority remain absent. The scheduled workflow has not executed on main.

Forecast status: NOT_ISSUED. Accuracy: NOT_EVALUATED. No directional forecast or paper trade occurred.

## 4. Run109 XRP market observations

Market cutoff: CoinGlass page updated 2026-11-13 23:49 UTC; other observations retain their own timestamps. None of these web observations has a byte-exact raw receipt in Barrot, so none is model-eligible.

- CoinGlass XRP aggregate: approximately $1.010; 24h -2.90%, 7d -14.25%, 30d -24.03%, 90d +0.88%, YTD -45.10%; 24h spot volume about $739.6M and futures volume about $3.04B (roughly 4.1x spot). OI headline $2.24B, but the same page reports -1.73% in its header and +1.20% in generated narrative. Do not use the OI change direction until reconciled.
- CoinGlass reports 24h liquidations about $15.61M: $13.96M long and $1.65M short (89% long); aggregate funding +0.0022% per eight hours; fear/greed 21; 30-day volatility about 49%; price about 19.9% below its 200-day average.
- Swiftedge tracked on-chain perpetuals: around 21:55 UTC price $1.0133, funding -0.0076% per eight hours, OI 91.03M XRP (about $92.2M), down 1%. Its 22:06 UTC resting walls included bids near $0.991/$0.987/$1.0045 and asks near $1.017/$1.019/$1.027. This is perpetual liquidity, not spot L2; resting orders can be cancelled.
- Funding sign differs between CoinGlass global aggregation and Swiftedge's tracked on-chain perpetuals. Different venue universes; never average.
- No synchronized, fresh, raw multi-venue spot L2 snapshot was admitted.
- ETF disagreement: XRP Insights data page shows four settled sessions Nov 9–12 at -9.481905M XRP and Nov 13 provisional; its live homepage shows week 46 near -10.41M XRP and Nov 12 daily -268,644 XRP. CoinGlass reports $0 for Nov 12, Alpha Finance reports zero for its five-fund cohort, and CryptoKeyhole lacked complete issuer files. XRP Insights homepage/data-page holdings differ by about 0.929M XRP. Different vintages and fund universes; do not average.
- Latest retrieved CFTC Legacy Futures-Only report remains Nov 3: 7,216 contracts, 50,000 XRP multiplier, 360.8M XRP contract-equivalent OI, non-commercial net long 1,465. Longs and shorts both fell; the net-long increase is more consistent with short covering than fresh long accumulation.

## 5. Run109 Evernorth actual-capital reconciliation

New primary evidence: Evernorth Form 10-Q filed Nov 13, for the quarter ended Sep 30, with subsequent events through Nov 13. It explicitly says the historical financial statements are pre-combination and do not reflect the Oct 9 closing. The initial closing 8-K was filed Oct 9; an 8-K/A with Pathfinder financials and pro forma information remains due within 90 days.

- At Sep 30, Evernorth's pre-close XRP balance was 346,284,972 XRP, historical cost $846.575M and carrying value $341.887M after $271.037M nine-month impairment. The 10-Q says 346,484,972 XRP was transferred to Pathfinder at closing; the 200,000 XRP difference is the delayed in-kind funding delivered at closing.
- Ripple contributed 126,791,458 XRP to Pathfinder. Combined with the 346,484,972 XRP transfer, the closing stack is 473,276,430 XRP. This is a closing figure, not a verified current balance.
- Gross closing cash proceeds were $272.6M: $224.6M private-placement cash plus $48M SPAC trust release, before transaction expenses. The $214.05M advance cash was used to purchase 84,365,876 XRP; it is a use of cash, not another raise.
- Total in-kind XRP contributions were 388,910,554 XRP. They are non-cash contributions.
- A $30M PIK convertible note produced approximately $29M net cash after a $1M advisor fee; this is debt, not equity.
- Between Oct 12 and Nov 9, holders exercised 3,073,366 warrants for cash. Evernorth received $35.3M gross and issued 3,073,366 Class A shares. This is additional actual cash, separate from the $272.6M closing proceeds.
- Evernorth assumed 11,739,645 warrants at $11.50. After the 3,073,366 exercises, 8,666,279 remain. Their theoretical gross proceeds at full exercise are about $99.66M; this is conditional capacity, not cash received.
- The $524.260M refundable investor-advance liability represents the fair value of subscriber XRP or cash advances. It was settled through equity issuance at closing; no cash was repaid. Do not count it again as new closing cash.
- The ELOC allows up to 5,218,935 shares at 97% of VWAP, at the company's discretion; Cantor is not obligated to purchase. The latest explicit disclosure states zero ELOC proceeds as of Nov 9. This is share capacity, not a fixed-dollar raise.
- The 73.688M registered resale shares include already-issued shares, Class C conversion shares, Pathfinder unit redemptions and warrants. Secondary resales do not generate issuer proceeds, except cash from warrant exercise.
- As of Nov 9, shares outstanding were 27,012,248 Class A and 31,392,746 Class C, total 58,404,994. Using closing XRP divided by that later share count gives approximately 8.10 XRP per Class A+Class C share. This is a derived cross-date ratio, not a company-reported current or fully diluted KPI.
- The 10-Q reports Q3 net income $155.265M while operating loss was $7.558M; the Q3 gain was driven by a $162.834M fair-value change in refundable advances. Nine-month net loss was $32.870M. The 10-Q is pre-combination; do not treat the Q3 net income as recurring operating profit.
- XRP Insights' Nov 13 wallet-attribution page reports about 103.13M XRP across 13 attributed wallets and about 370.35M gross outbound transfers from that set, with destinations not attributed. Its own breakdown says most current XRP sits in wallets holding Ripple's Pathfinder contribution, while only 127 XRP is in Evernorth's own wallets and five XRP in BitGo purchase-tranche wallets. This is wallet attribution, not proof of direct beneficial ownership or a sale. XRPSCAN/API transaction detail was inaccessible during this run; no destination inference was made.
- The XRP Insights page's statement that no share count/closing filing had been reported is stale against the Nov 13 10-Q and 424B3 supplements. The post-close Pathfinder financials/pro forma 8-K/A remain pending.

## 6. RLUSD, custody, payments and corporate relationships

- Standard Chartered's Oct 12 announcement says institutional RLUSD custody on XRPL is live through its DIFC branch, regulated by DFSA. The planned LMAX collateral-mirroring arrangement is future work subject to final documents, testing, laws, regulation and approvals. The asset is RLUSD, not XRP.
- OCC's bank application record shows Ripple National Trust Bank effective Oct 26. Ripple says the bank's approved activities include segregated RLUSD reserve management, collateral-trustee services and fiduciary custody. RLUSD remains issued by NYDFS-regulated Standard Custody & Trust Company; BNY remains the primary reserve custodian. Do not conflate issuer, trustee and custody roles.
- Ripple/Robinhood's Oct 27 partnership: RLUSD live on Robinhood Chain and Bitstamp; expected later in the Robinhood app; RLUSD on XRPL for institutional settlement; Ripple Treasury integration for corporate cash management; Ripple Prime financing and market access for Bitstamp. This is RLUSD infrastructure, not evidence of XRP purchases.
- Ripple/Coinbase's Oct 28 announcement: RLUSD live across Coinbase Prime, Exchange and Retail on XRPL, Base and Ethereum. Coinbase Global Exchange collateral support was still forthcoming, not live.
- Ripple's Oct 28 company-reported claims include over $16T transactions enabled across its products in 2025 and a projected $900M annualized product-revenue run rate exiting 2026. These are company-wide product claims, not XRP on-ledger throughput or XRP demand.
- Bitquery's Sep 19–Oct 18 XRPL RLUSD analysis reports 7.821M payments, with 7.789M (99.6%) from a 110-wallet dust cluster to three collectors, averaging about 0.00099 RLUSD. The report attributes funding to Binance-labelled wallets but says this may be one Binance customer; it does not establish Binance operated the bots.
- Bitquery reports $7.33B gross value across payments >=1 RLUSD, but top ten senders account for 82%; issuer mint/redemption loops are about 20%; one $424M transfer returned $424M, adding $848M gross without net economic transfer. The report has internal count and redemption discrepancies (14,600 vs 14,608 derived payments; $734M vs $744M redemption figures). It is one provider's analysis and has not been independently reproduced. Do not treat raw payment count or gross value as merchant adoption or net settlement.
- CoinDesk's Oct 14 x402 report cited 14.3M cumulative transactions across 169 merchants but only 6,991 XRP and 12,752 RLUSD in its tracked payment totals. Transaction counts alone are not economic throughput.
- SBI Ripple Asia remains a 60/40 SBI Group/Ripple software-services JV and does not directly handle XRP. SBI Remit/SBI VC Trade/Tranglo is the separate operational XRP remittance route. SBI also has a 50/50 Circle JV; SBI Holdings and SBI Shinsei each invested $25M in Circle's IPO.

## 7. Identity research

- SBIC East/Tokyo, SBIC Central/Nagoya and SBIC West/Osaka are regional Japanese SME investment companies, distinct from SBI Holdings. SBIC East's ChatGPT/Copilot training was for investee companies; its public ChatGPT seminar was educational activity, not evidence of an OpenAI commercial partnership.
- ASK Coin: no canonical XRPL issuer or deployment verified. Permission Coin (ASK) is a candidate ticker on Base/Polygon from secondary token listings; it is not evidence of an XRP Ledger asset.
- Actual capital: not a standardized XRP metric. Use the SEC distinctions above: gross cash, warrant exercise cash, debt, in-kind XRP, refundable advances settled in equity, conditional ELOC capacity and secondary resales.
- Dr. Kamilah/Camilla Stevenson: person identity is not enough to attribute similarly named YouTube channels. No first-party channel ownership link was verified; verified own-channel video inventory remains zero.

## 8. Nine-platform coordination

| Platform | Run109 status |
|---|---|
| ChatGPT | GitHub connector access verified; permissions include admin, maintain, push, pull and triage, exceeding least privilege |
| Claude | Authentication and data flow unverified |
| Grok | Authentication and data flow unverified |
| Gemini | Authentication and data flow unverified |
| Copilot | Review artifacts exist; no formal approval on #1662 |
| Codex | Authentication and data flow unverified |
| Hugging Face | Prior BUILD_ERROR; no current deployment |
| Kaggle | Untested; no submission |
| Databricks | Prior HTTP 403; no write verified |

LunaRoute is separate from the nine platforms. Remote MCP is enabled on main and disabled in integration; endpoint authentication is unverified. No external-model dispatch, nine-platform evidence exchange or external-model data transfer occurred.

## 9. Security, merge decision and backlog

- Main branch metadata reports protected=true; integration is unprotected. Direct branch-protection detail returns HTTP 403. Fallback ruleset 10863829 is disabled.
- Main OpenCode still allows remote LunaRoute MCP and write-capable edit/bash/webfetch; integration disables remote MCP and requires approval for mutations.
- Main Barrot Sync masks missing-dependency/sync errors and ignores push failure; integration quarantines it. Its key-prefix diagnostic prints only the fixed 30-character label, not the secret.
- Main A2A deployment is push-triggered and uploads secrets; integration requires manual action-specific confirmation and exact-main-SHA verification.
- Main paper-trader workflow can write results to main without the integration's explicit confirmation/artifact-only restriction; no paper trade was run.
- GitHub Pages has deployed automatically after main pushes. Seven public web files change in #1662; publication authorization remains unresolved.
- The full 1,154-file semantic review remains incomplete, especially 50 workflows and seven public web files.

**Merge decision: NO MERGE.** PR #1662 remains draft with zero approvals. Branch-protection visibility, least-privilege access, Pages publication authorization and complete semantic review remain blockers, despite exact code-head tests passing.

Backlog: #1662 blocked integration; #1661/#1660/#1643/#1642 are zero-ahead path-overlap supersession candidates; #1640's one extra commit is fully represented by the stricter integration external-action gates; preserve all until successor is merged and verified. #1653/#1655/#1659/#1615/#1614/#1320/#1318/#1317/#1269 remain unique/unreviewed or individually blocked. #1644–#1650 and #1254/#1255 remain dependency candidates blocked pending current-main validation. No source PR was closed.

## 10. Next concrete actions

1. Complete the documentation-only descendant's exact-head full-suite, dependency and fail-closed checks.
2. Finish semantic reconciliation of all 1,154 changed paths, prioritizing 50 workflows and seven public web files.
3. Resolve GitHub least privilege, branch-protection visibility, remote MCP containment and Pages publication authorization.
4. Add an XRPL payment-quality adapter that separates dust/bot counts, gross vs net transfers, issuer mint/redemption loops, round trips, exchange/custody sweeps and wallet concentration; reproduce Bitquery findings from raw ledger receipts before admitting features.
5. Reconcile Evernorth's 10-Q, 424B3 supplements, 8-K/A and custody wallet destinations; do not infer that the 370M XRP gross outbound wallet flow was sold.
6. Establish independently anchored raw-source receipts and durable archives, then collect synchronized historical spot, L2, derivatives, exchange-flow and collateral data.
7. Validate bootstrap coverage under small cluster counts, cluster-count sensitivity and block-length sensitivity before allowing any candidate model through policy v6.
8. Train an XRP-specific candidate only when the dataset supports it; require calibrated out-of-sample superiority and independent shadow outcomes before forecast issuance.

No merge, deployment, secret rotation, Space restart, external-model transfer, Databricks write, Kaggle submission, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or source PR closure occurred.

## Run110 — 2026-11-14T01:06:08Z

### Mission and repository state

XRP intelligence and prediction-engine mastery remain mission priority 1. Barrot V3 remains the protected execution, orchestration, safety and verification foundation.

- Main SHA: `fb272b40966834754ec686f9ed3ab94123f09306`.
- Code-bearing integration head verified in this run: `2945c5617519ed297dbd311af2bb8dbee47dc6bb`.
- Branch: `integration/xrp-v3-unified-main-20261112`; 2,322 commits ahead of main, zero behind.
- Main tree: 1,381 entries / 87 workflows. Integration tree: 2,397 entries / 88 workflows.
- PR #1662: draft, open, 1,156 changed files, 334,325 additions, 5,354 deletions; 50 workflow files and seven public web files.
- Open PR inventory: 375 total; 361 drafts and 14 non-drafts.
- PR #1662 has zero formal reviews, approvals and review threads. No merge occurred.

This Run110 handoff and its JSON/map records are documentation-only descendants of the verified code head above. They do not alter runtime code. Their own exact-head CI is pending after this commit; do not transfer the parent head's test result to a later descendant.

### Exact-head verification — EXECUTED and VERIFIED on 2945c561

A failing full-suite run on predecessor `e915307` exposed a contract-documentation mismatch: a regression test required the literal “block-bootstrap adjustment” phrase, which was missing from `research/xrp_intelligence/forecast-ledger-contract.md`. The phrase was added with a policy explanation in commit `2945c561`. No runtime code changed.

Exact-head evidence on `2945c561`:

- [Full CI 43538066244](https://github.com/Barrot-Agent/B-Agent/actions/runs/43538066244): 3,626 passed, eight subtests passed, zero failures; 62.34% inclusive coverage; 88.95 seconds. Wheel build and installed Barrot V3 / primary-mission verification passed.
- Core test job: 739 passed, eight subtests, 13.95 seconds; legacy core coverage 76%.
- [Dependency audit 43538066242](https://github.com/Barrot-Agent/B-Agent/actions/runs/43538066242): five groups audited (runtime, dev, Hugging Face Space, legacy and PEP 621 pyproject dependencies); no known vulnerabilities reported.
- [Fail-closed push gate 43538066174](https://github.com/Barrot-Agent/B-Agent/actions/runs/43538066174) and [PR gate 43538072699](https://github.com/Barrot-Agent/B-Agent/actions/runs/43538072699): passed with automatic merge disabled.
- PR-event CI 43538072864 was skipped by the explicit integration-branch condition. The push-event full-suite run is the actual exact-head full-suite evidence.

Non-blocking build warnings remain: deprecated TOML table-form license metadata and setuptools package-discovery warnings for `barrot_agent.data.missions` / `data.research`. The wheel's primary mission resource was nevertheless verified after installation.

### Prediction-engine gate — critical design limitation

Implemented on integration: four deterministic baselines, chronological walk-forward with purge/embargo, paired temporal moving-block bootstrap, outcome-source-clustered bootstrap, 95% familywise Bonferroni control across eight baseline/metric comparisons (99.375% individual intervals), minimum 100 paired origins, 10,000 resamples, five source clusters and minimum five origins per cluster, calibration/drift checks, receipt-backed provenance and independent Ed25519 readiness attestation.

New inspection of `walk_forward.py` shows that an outcome-source cluster ID is assigned only when the target outcome resolves to exactly one canonical independence group. Multi-publisher target aggregates are explicitly marked unclustered. The source-cluster interval measures outcome-publisher lineage; it does not establish independence among training-feature sources.

This creates a structural feasibility problem: a per-venue target fed by one exchange publisher can produce only one outcome cluster, while a composite multi-venue target is currently marked unclustered. The five-cluster admission gate may therefore be impossible to satisfy under the current target schema without redefining the estimand or adding genuinely independent outcome observations. Do not weaken the five-cluster fail-closed rule or count API wrappers sharing one upstream venue as independent sources. Resolve target definition, cluster unit, weighting, and dependence assumptions; then add small-cluster coverage and block-length sensitivity simulations before candidate admission.

There is still no trained XRP-specific candidate model. Walk-forward results currently evaluate deterministic baselines. No directional forecast was issued; accuracy remains NOT_EVALUATED. No paper trade or real-money action occurred.

### Fresh XRP market and ETF observations

Research cutoff: 2026-11-14T01:06:08Z.

- OKX XRP-USDT ticker event timestamp: 2026-11-14 00:56:03.669 UTC; last $1.0100, bid $1.0097, ask $1.0098, 24h open $1.0364, high $1.0438, low $0.9974, volume 47.067M XRP. At the automation start (01:00:55 UTC) the quote was 291 seconds old; by this research cutoff it was about 604 seconds old and outside the 300-second admission limit. Best-level sizes (4,152.49 bid / 316.3 ask) are one price level, not full depth. No raw byte receipt/hash was captured; not model-eligible.
- Kraken XRP/USD separately returned last $1.01123, bid $1.01050 and ask $1.01054 without a provider event timestamp. Do not synchronize or average it with OKX.
- XRPN secondary-market history reports a Nov 13 close of $7.85, down 12.49%, on 388,810 shares. This is equity-market context, not evidence of XRP demand or a causal signal.
- XRP Insights' data page says four settled sessions Nov 9–12 net -9,481,905 XRP; Nov 12 alone -268,644 XRP; holdings 1,185,698,783 XRP. Nov 13 is provisional. The same provider's homepage agrees on Nov 12 and the weekly total. The dataset computes flows from day-over-day issuer-reported holdings, with GXRP flows withheld during a capture gap; BITW rebalancing and fees can appear as flow. CryptoKeyhole's Nov 12 observation is partial (three of four funds, -3,322 XRP); Alpha Finance's five-fund cohort reports zero. Different coverage and settlement vintages are not averaged.

### Evernorth: material primary-filing correction and actual-capital reconciliation

Primary source review found that the XRP Insights Evernorth page still says no closing 8-K was on EDGAR at its Nov 13 23:41 UTC check and says no filing reports the closing share count. That statement is contradicted by Evernorth's Oct 9 closing Form 8-K, its Oct 13 corrective Form 8-K, and its Nov 13 Form 10-Q. The tracker page itself lists the 10-Q as filed after its last review. Treat its wallet attribution as a third-party partial ledger analysis, not the authority for corporate closing status or capital structure.

- The Oct 9 business combination closed. The Oct 13 8-K corrected a clerical error: delayed-funding Class A shares were 1,078,613, not 663,510. Corrected closing shares were 23,638,882 Class A and 31,392,746 Class C.
- The Nov 13 10-Q states Pubco's principal asset is a 71.5% ownership interest in Pathfinder. The 473,276,430 XRP headline is gross Pathfinder treasury, not 100% directly attributable to public Pubco equity. Pathfinder received 346,484,972 XRP transferred by Evernorth and 126,791,458 XRP contributed by Ripple. Applying 71.5% to gross Pathfinder XRP gives approximately 338,392,647 XRP attributable to Pubco, a derived estimate rather than a company-reported post-close balance. The 10-Q defines XRP per share as XRP attributable to Pubco divided by outstanding Class A plus Class C shares.
- As of Nov 9 the 10-Q reports 27,012,248 Class A and 31,392,746 Class C shares. Using the derived 338.393M XRP and those 58.405M A+C shares gives approximately 5.79 XRP per A+C share; this is a calculation, not a company-reported KPI. Exact attributable holdings and later share changes require further reconciliation.
- SBI Holdings' Oct 13 8-K disclosure lists 9,431,914 Class A and 2,359,038 Class C shares at closing; Class C represented 7.5% of that class. The Class A amount was about 39.9% of closing Class A shares. If those holdings remained unchanged through Nov 9, the implied percentages would be about 34.9% of Class A, 7.5% of Class C and 20.2% of combined A+C shares. No updated beneficial-ownership filing was verified, so these are conditional calculations, not current confirmed percentages.
- The 10-Q reports 3,073,366 warrant exercises from Oct 12 through Nov 9 for approximately $35.3M gross cash; 8,666,279 warrants remained at $11.50. The 10-Q's Nov 9 Class A count exceeds corrected closing shares plus those disclosed exercises by 300,000 shares. No reviewed filing reconciles that residual; do not attribute it to an ELOC draw, employee plan or other issuance without evidence.
- Gross closing cash proceeds were $272.6M before expenses (private-placement cash plus SPAC trust release). Of this, $214.05M was used to purchase 84.365876M XRP at approximately $2.5366; do not count it again as cash still available. In-kind XRP contributions were 388.910554M. The $524.26M refundable investor advances were settled in equity at closing, not repaid as cash and not a second new cash raise.
- A $30M 4% PIK convertible note was issued Oct 13; reported net cash after a $1M advisor fee was about $29M. A discretionary ELOC for up to 5,218,935 shares at 97% of VWAP is financing capacity, not cash received; no ELOC proceeds were disclosed in the reviewed 10-Q. Registered secondary-resale shares generate no issuer proceeds.
- The 10-Q's financial statements are for the period ended Sep 30, before the Oct 9 combination: unrestricted cash $91,397, restricted cash $49,995, no revenue, Q3 net income $155.265M primarily from a $162.834M fair-value gain on refundable investor advances, and nine-month net loss $32.870M with $271.037M digital-asset impairment. The Q3 gain is not operating profitability and the Sep 30 cash balance is not post-close liquidity.
- The 10-Q says Coinbase is Evernorth's principal market for XRP fair-value/impairment accounting and says the initial post-combination custodian is BitGo Trust. Principal-market designation does not prove Coinbase is the custodian or the exclusive execution venue.

The tracker reports 103,129,905 XRP in 13 attributed XRPL wallets at ledger 108,313,323 (Nov 13 23:41 UTC), and 370,346,663 XRP moved outside that attributed set, with destinations not attributed (latest Oct 22). The tracker explicitly does not assume those transfers were sold. Its wallet set includes Ripple-contribution-related wallets; it is not a complete Pathfinder custody inventory. The SEC gross treasury and the tracker’s partial wallet attribution must remain separate.

### Workflow/security and PR reconciliation

All 50 changed workflow-file patches were screened for triggers, permissions, secrets, deployments, pushes and confirmation gates. The XRP public ingestion workflow is scheduled/read-only and main-only. External write/deploy paths remain manual and require action-specific confirmation and main-SHA pinning; the Hugging Face sync and self-hosted brain sync paths are disabled/quarantined in integration. No external action was executed.

Main-side observations:
- Main metadata says protected=true, enforcement for non-admins, but required status-check contexts are empty. Detailed protection endpoint returned HTTP 403; fallback ruleset 10863829 is disabled. Integration is unprotected.
- GitHub connector permission set includes admin, maintain, push, pull and triage; this exceeds least privilege.
- Main Pillars Consistency run 43430139937 failed because required GitHub App identifiers were missing, Databricks returned HTTP 403 and Hugging Face reported BUILD_ERROR.
- Main Barrot Sync run 43343513347 reported success but logs show `ModuleNotFoundError: httpx`, sync skipped and a no-op `Everything up-to-date` push. Treat the green status as a workflow defect, not verified synchronization.
- GitHub Pages has deployed automatically after main pushes. Seven public web files change in #1662; publication authorization remains unresolved.

PR #1662 remains draft with zero formal reviews, approvals or review threads. Current path/ancestry reconciliation:
- #1661, #1660, #1643 and #1642 have full path overlap with #1662 and no source-only commits; integration is respectively 190, 328, 1,390 and 2,295 commits ahead of those heads. They are exact supersession candidates, but remain open until #1662 is merged and verified on main.
- #1640 has one source-only commit; its action-specific Databricks/Kaggle approval workflow and tests are semantically present in integration with stricter gates. Preserve until successor merge/verification.
- #1653 and #1655 retain 18 and 17 unique commits respectively. Preserve. #1659, #1615, #1614, #1320, #1318, #1317 and #1269 remain unique/unreviewed or individually blocked. #1644–#1650 and #1254/#1255 remain dependency candidates blocked pending current-main validation.
- No source PR was closed.

**Merge decision: NO MERGE.** Draft status, no approvals, incomplete semantic review of 1,156 files, branch-protection visibility, overprivileged connector permissions, automatic Pages publication and unresolved source-cluster target design remain blockers.

### Next concrete actions

1. Resolve the source-cluster estimand/target-schema feasibility without weakening independence requirements; add coverage simulations and require the resulting evidence in forecast readiness.
2. Reconcile Evernorth's 71.5% Pathfinder ownership, 473.276M gross treasury, 338.393M derived attributable amount, 300K share-count residual, ELOC status and custody wallets against the next combined-company disclosure.
3. Continue synchronized historical XRP spot/L2/derivatives/flows/collateral ingestion with byte-exact raw receipts and independent durable anchoring.
4. Complete semantic review of the 1,156-file integration, prioritizing 50 workflows and seven public web files.
5. Resolve least-privilege GitHub access, branch-protection visibility, main-side remote MCP containment and Pages publication authorization.
6. Train an XRP-specific candidate only after sufficient point-in-time history exists; require calibrated out-of-sample superiority against all four baselines and independent shadow outcomes before any directional forecast.

No merge, deployment, secret rotation, Space restart, external-model transfer, Databricks write, Kaggle submission, paper trade, funds transfer, real-money action, force-push, history rewrite, destructive worktree operation or source-PR closure occurred.
