# Barrot mission handoff — latest

Captured: 2026-11-27T16:35:53Z; primary-source research retrieved earlier in this run.  
Repository: https://github.com/Barrot-Agent/B-Agent  
Current main: `2151843140fd770b62ef93d06a78c559f9e73bbd`  
Current handoff branch before this corrective refresh: `0454127e1e9a6503e4b250915212c9571df84755`.

The prior large handoff and operational map are preserved unchanged in:
- [Previous handoff archive](docs/handoffs/archive/BARROT_MISSION_HANDOFF_2026-11-27_RUN13.md)
- [Previous nine-platform map archive](research/operations/archive/nine_platform_operational_map_2026-11-27_run13.json)

## Operating contract

XRP intelligence/prediction-engine mastery, professional audio production, and long-horizon continuity/capability development are three co-equal highest-priority missions. Each remains priority 1 and active. None may be deferred behind another. Barrot V3 remains the shared execution, orchestration, safety, provenance, authorization, persistence, and verification foundation.

Revenue/customer acquisition is an immediate cross-mission objective, not a fourth technical mission. Sellbird is restricted to Barrot technology and Barrot-related services only. Music, vocal/songwriting services, TrekFlex, and unrelated ventures remain excluded from Sellbird.

## Repository and integration state

- Main SHA: `2151843140fd770b62ef93d06a78c559f9e73bbd`; complete recursive tree: 3,164 entries, not truncated.
- Main exact full-suite CI: run [45735004570](https://github.com/Barrot-Agent/B-Agent/actions/runs/45735004570), 4,695 passed, 0 failed, 1 skipped, 11 warnings, 21 subtests; 74.21% coverage.
- Main dependency audit [45735004518](https://github.com/Barrot-Agent/B-Agent/actions/runs/45735004518) and money audit [45735004503](https://github.com/Barrot-Agent/B-Agent/actions/runs/45735004503) passed.
- Main has 12 open PRs. Merged history includes #1692, #1699, #1701 and #1712.
- Main branch is protected; four required checks are enforced for non-admins. The detailed branch-protection endpoint returns HTTP 403 / RESOURCE_NOT_ACCESSIBLE_BY_INTEGRATION, so the required approving-review count is unknown. Merge to main triggers GitHub Pages deployment. No new deployment authorization was given.
- **Runtime alignment gap:** the main `scripts/ask_barrot.py` prompt still calls XRP the singular highest-priority mission. The three-mission manifest and durable round-robin scheduler are present on main, but the corrected three-co-equal runtime prompt is on PR #1702 only. Do not claim the runtime prompt fix is on main.

### Open PR classification

| PR | Workstream | Current state |
|---|---|---|
| [#1702](https://github.com/Barrot-Agent/B-Agent/pull/1702) | Canonical handoff, nine-platform map, runtime prompt | Active; current head `0454127`; 4,704 passed, 1 failed, 1 skipped because the archived handoff was omitted from `docs/INDEX.md`; corrective index entry is in this commit; legacy merge gate still blocks on stale base; no independent review |
| [#1703](https://github.com/Barrot-Agent/B-Agent/pull/1703) | Long-horizon project-state ledger | Active; 4,715 passed, 1 skipped; local continuity tested, cross-host sync unimplemented; no review |
| [#1704](https://github.com/Barrot-Agent/B-Agent/pull/1704) | Audio SoundFont routing and full-song bundle | Active; 4,703 passed, 1 skipped; FluidSynth integration passed; no review |
| [#1705](https://github.com/Barrot-Agent/B-Agent/pull/1705) | XRP/RLUSD research and source capture | Active; 4,727 passed, 1 skipped; dependency/money/conflict checks passed; legacy gate falsely blocks on stale base; no review |
| [#1714](https://github.com/Barrot-Agent/B-Agent/pull/1714) | V3 governance and corrected ancestry gate | Active clean successor; 4,697 passed, 1 skipped; exact-head gate passed; no independent review; Pages deployment authorization still absent |
| [#1713](https://github.com/Barrot-Agent/B-Agent/pull/1713) | Superseded governance source plus Telegram draft | Keep as draft/source history; shared governance work is superseded by #1714; unique Telegram additions were intentionally excluded from #1714 |
| [#1706](https://github.com/Barrot-Agent/B-Agent/pull/1706) | actions/cache restore update | Blocked by stale base and overlapping XRP workflow/action-pin changes in #1705/#1709 |
| [#1707](https://github.com/Barrot-Agent/B-Agent/pull/1707) | actions/setup-node update | Unique, unreviewed, stale base; exact workflow validation required |
| [#1708](https://github.com/Barrot-Agent/B-Agent/pull/1708) | actions/cache save update | Duplicate subset of #1706; do not merge separately |
| [#1709](https://github.com/Barrot-Agent/B-Agent/pull/1709) | Databricks setup action update | Unique dependency update but overlaps #1706 action-pin tests; stale base |
| [#1710](https://github.com/Barrot-Agent/B-Agent/pull/1710) | Legacy PyYAML requirement | Unique/unreviewed; runtime use of the legacy requirements file is unconfirmed |
| [#1711](https://github.com/Barrot-Agent/B-Agent/pull/1711) | NumPy upper-bound update | Blocked: allowing NumPy 2.x conflicts with the current Streamlit 1.35 constraint |

No PR was merged or closed in this run. Do not bulk-close unique/unreviewed work. Prefer consolidating the cache/action-pin overlap rather than creating another dependency PR.

### Current #1702 exact-head result

- Head tested: `b42ed89b3ad6f23f9a79ebf1b026f3d5bf3b394a`.
- Full suite [46031711753](https://github.com/Barrot-Agent/B-Agent/actions/runs/46031711753): 4,705 passed, 0 failed, 1 skipped, 11 warnings, 21 subtests; 74.21% coverage.
- Dependency, money, and conflict-integrity checks passed.
- Merge gate [46031712028](https://github.com/Barrot-Agent/B-Agent/actions/runs/46031712028) failed closed because the legacy gate compares the PR's stored base SHA with current main. GitHub ancestry comparison is 199 commits ahead / 0 behind; this is a stale-base gate defect, not evidence that the branch is behind.
- #1714 contains the corrected ancestry gate and passed its own exact-head gate, but still has no independent review. Do not merge either PR without required review and authorization for the automatic Pages side effect.
- First refresh head `0454127e1e9a6503e4b250915212c9571df84755` ran full suite [46034113268](https://github.com/Barrot-Agent/B-Agent/actions/runs/46034113268): 4,704 passed, 1 failed, 1 skipped, 11 warnings, 21 subtests; 74.21% coverage. The sole failure was `tests/test_cross_domain_audit.py::test_all_links_resolve_or_are_documented`: the new archived handoff was not listed in `docs/INDEX.md`. Dependency audit [46034113100](https://github.com/Barrot-Agent/B-Agent/actions/runs/46034113100), money audit [46034113114](https://github.com/Barrot-Agent/B-Agent/actions/runs/46034113114), and conflict integrity [46034113076](https://github.com/Barrot-Agent/B-Agent/actions/runs/46034113076) passed. This corrective commit adds the missing index entry; its exact-head full suite is pending.

## Mission 1 — XRP intelligence and prediction-engine mastery

Main scheduled ingestion run [#220](https://github.com/Barrot-Agent/B-Agent/actions/runs/46031858066) succeeded on main SHA `2151843140fd770b62ef93d06a78c559f9e73bbd`.

- Adapter `xrp-public-market-v3.34`; parser `xrp-public-market-v3.32`.
- Data cutoff: `2026-11-27T16:14:43.923938Z`.
- Feature store: 167 snapshots; 41,343 history rows; 2,230 input records; 367 eligible and 367 excluded records; SQLite integrity `ok`. The store is restored from workflow checkpoints/cache; rebuild from immutable raw artifacts is not implemented.
- Receipt chain: sequence 167, 37 receipts, 21 retained raw payloads, 16 digest-only receipts; cross-run continuity verified. No external timestamp/WORM anchor.
- Event timeline: 150 events; 0 verified receipt links; 150 missing raw receipt hashes; 11 URL-only matches; 0 URL-plus-capture-time matches. Receipt linkage remains incomplete and the event timeline is not model-eligible.
- Walk-forward: 632 rows, 1-hour horizon only, status `PARTIAL_OR_BLOCKED`. Drift: 0 of 206 features evaluated; `INSUFFICIENT_DATA`.
- Source failures: 18. SEC EDGAR is blocked by missing contact configuration (3 failures, no raw receipts). Morpho cbXRP remains excluded because its Base indexer tip (63,027,272) trails observed market/history blocks (63,028,531); block timestamp is unverified.
- Same-venue OKX top-of-book quote basis: mid `$0.9482060335`, spread `1.15347 bps`. This is one publisher group and top-of-book only—not full-depth liquidity or independent corroboration.
- Forecast status: **NOT_ISSUED**. No paper trade or real-money action.

The next XRP implementation target is event-to-receipt linkage and durable raw-source retention/anchoring, followed by synchronized multi-horizon evaluation, SEC configuration, and Morpho block alignment. Do not issue a directional forecast while receipt linkage, historical point-in-time coverage, walk-forward completeness, and drift remain blocked.

## Primary-source relationship update — branch-only research artifact

A new evidence record was added to the existing XRP integration branch #1705: `research/xrp_intelligence/20261127T161715Z-sbi-circle-coinbase-ripple-primary-source-network-update.json` (14 relationship records, 24 primary-source/counterparty/SEC references). It is **research-only**, has no byte-exact raw receipts, and is not model-eligible. Its CI was pending at this handoff capture.

Key findings:
- **SBIC identity:** SBIC East is Tokyo Small and Medium Business Investment & Consultation Co., Ltd. (corporate number 9011001030621); Central is Nagoya Small and Medium Business Investment & Consultation Co., Ltd.; West is Osaka Small and Medium Business Investment & Consultation Co., Ltd. They are distinct regional statutory investment companies, not SBI Holdings subsidiaries. SBIC East's official June 12–13, 2025 investee-company training included ChatGPT and Copilot; that is training, not an OpenAI partnership.
- **Circle–Coinbase economics:** Circle's Q3 2026 Form 10-Q reports $331.3M of Coinbase distribution costs in Q3 and $986.6M for the first nine months. Those amounts are approximately 81.0% and 80.5% of Circle's respective distribution-and-transaction-cost totals (derived ratios, not separately reported). Coinbase's Q3 2026 10-Q says its Circle arrangement was renewed on the same terms and average USDC held in Coinbase products reached $22B. This is a large USDC distribution relationship, not XRP demand.
- **SBI–Circle–Arc:** SBI disclosed subsidiary participation in Circle's ARC token presale; Circle named SBI Group a founding Arc validator. Arc is Circle's separate EVM-compatible network, not XRPL. SBI's allocation and actual validator economics are undisclosed.
- **Ripple–BNY:** BNY supports XRP and RLUSD custody and is identified as RLUSD's primary reserve custodian. Direct mint/redeem and tokenized trade-finance use cases were future plans subject to client/regulatory approvals; no XRP custody balance or utilization was disclosed.
- **Coinbase–Ripple–RLUSD:** RLUSD launched across Coinbase Prime, Exchange and app with XRPL, Base and Ethereum deposits/withdrawals. Coinbase Global Exchange collateral functionality was described as future, not live at launch.
- **Other rails:** Circle–DBS announced direct institutional USDC mint/redeem with 24/7 USD-USDC settlement; Circle–Paribu signed an exploratory Arc MOU; SBI–SMBC announced an exploratory stablecoin/tokenization alliance; SBI's JPYSC launch was initially account-limited. None establishes XRP settlement volume.
- **Exact phrases:** ASK Coin's best-supported candidate remains Permission's ASK token, but context identity is unconfirmed and no XRP/SBI link is established. "Actual capital" remains unresolved and must not be conflated with SBI's "Actual XRP" category. "SBIC, ChatGPT SBIC" resolves to SBIC East educational training, not partnership.
- **Kamilah/Camilla Stevenson:** person identity and channel attribution remain separate questions; the public channel attribution is strong but not legally verified, the video inventory is incomplete, and namesake channels remain unmerged.

Counter-hypothesis retained: corporate investment, stablecoin distribution, custody support, exchange listing, and future tokenized-finance plans do not establish XRP demand, XRP collateral usage, net XRPL flows, or realized transaction throughput. The research artifact preserves counterparty corroboration and limitations; raw publisher bytes were not captured by the web retrieval path.

## Mission 2 — professional audio production

PR #1704's exact-head FluidSynth workflow [run 45867292176](https://github.com/Barrot-Agent/B-Agent/actions/runs/45867292176) produced a real full-song production artifact:
- [Audio production bundle artifact](https://github.com/Barrot-Agent/B-Agent/actions/runs/45867292176/artifacts/15139779842), 242,108,638 bytes; artifact retention expires 2026-12-26.
- [Full-song QC artifact](https://github.com/Barrot-Agent/B-Agent/actions/runs/45867292176/artifacts/15139719863).
- [Per-track SoundFont routing QC artifact](https://github.com/Barrot-Agent/B-Agent/actions/runs/45867292176/artifacts/15139799666).

The full-song bundle contains a 32-bit-float stereo WAV, nine aligned WAV stems, Standard MIDI File, JSON metadata/section markers, QC, and an MIT license notice. It does **not** contain a native DAW project. It is a PR workflow artifact, not yet a main-branch release.

Verified technical QC: 175.545 seconds; 80 bars; 110 BPM; D minor; 4/4; 44.1 kHz stereo; 9 sample-aligned stems; zero clipped samples; peak -6.024 dBFS; true peak -6.000 dBTP; integrated loudness -22.441 LUFS; LRA 7.870 LU; stereo correlation 0.718; mono fold-down loss -0.661 dB; stem-sum reconstruction correlation 0.999979. The lead stem's mono fold-down loss was corrected from -4.563 dB to -2.978 dB.

The full-song render uses FluidR3_GM with an MIT license notice. The separate routing test uses two FreePats assets whose source pages state CC0-1.0; that is source-page provenance, not an independent legal audit. Rights metadata remains caller-supplied/unverified. The SoundFont binary is not bundled.

Human listening was **NOT PERFORMED**; user acceptance is **NOT VERIFIED**. Technical QC is not a musical-quality verdict. The earlier low user rating remains a quality baseline. Next: listen in a DAW, capture explicit accept/reject notes, verify rights independently, and produce a native DAW project or supported interchange package. Do not market music or vocal services.

## Mission 3 — long-horizon continuity and capability development

PR #1703 adds a versioned local project-state ledger, explicit signed export/import, conflict/staleness preservation, and dependency-aware task selection. Exact full-suite validation passed (4,715 passed, 1 skipped). The main three-mission scheduler's durable round-robin selection has been tested across fresh processes.

Not verified: authenticated cross-host synchronization, automatic key exchange, cross-provider state transport, or unattended recovery across separate machines. Local persistence/export-import is not proof of cross-host continuity. Keep key material outside ordinary state records.

## Nine-platform coordination

Only the ChatGPT GitHub connector has a verified live Barrot data flow. It can inspect the current repository and write existing integration branches. No external model data transfer occurred.

Claude, Grok, Gemini, Copilot, Codex, Hugging Face, Kaggle, and Databricks remain **NOT TESTED** for Barrot authentication, permissions, and data flow. The user's account existence or a provider's public documentation is not a live connection. Sellbird's Codex CLI support does not establish a Barrot↔Codex connection. Retain minority objections and red-team review as designed requirements; no nine-platform evidence exchange has been executed.

## Commercial objective — Sellbird, Barrot only

Upstream source audit of [ethanplusai/sellbird](https://github.com/ethanplusai/sellbird) was executed at main SHA `8c743f1c475f61f7b2c04e50501cf6938a126ed`, release v0.5.0 (published 2026-11-25). It is a local AI sales-prospecting/outreach platform, formerly Harvey—not a persistent-execution/approval framework. It requires Python 3.11+ and declares **AGPL-3.0-only**. Its latest main test workflow (run 45576760134) passed.

Sellbird supports Claude and Codex CLI as model providers; Codex can use a ChatGPT subscription. The documented ChatGPT desktop pane is explicitly not tested upstream. This is not a native ChatGPT API integration.

Source-audited controls include a default human approval queue, a deterministic pre-send gate, a pause-all kill switch, daily caps, send windows, bounce-rate pause, verified-address-only behavior, immediate opt-out suppression, and an agent-route allowlist that cannot approve, send, or resume. Autopilot exists as an opt-in configuration, so it must remain disabled. A supervised browser pane uses the user's dashboard session and can click what the user can; never leave it unattended.

Readiness blockers: Sellbird is not installed or integrated with Barrot; authentication and mailbox are not configured; the template has no postal address, do-not-contact list, or warmup start date; SPF/DKIM/DMARC and a dedicated sending domain are unverified; no campaign or prospecting run has been approved. Keep outbound paused. The README describes free OpenStreetMap/TinyFish discovery and DataForSEO Business Listings at $0.372 per 1,000; estimate any paid provider before use. Keep LinkedIn browser automation disabled because the repository warns it violates LinkedIn's Terms of Service. AGPL obligations require legal review before copying code into Barrot or operating a modified network service.

Barrot-only scope: prospect only for verified Barrot technology, pilot users, research collaborators, technology partners, and potential paying organizations. Do not prospect for music, vocal/songwriting services, TrekFlex, or unrelated ventures.

Fastest credible offer hypothesis: a supervised, fixed-scope public-data provenance/quality assessment for research or analytics teams. This is not yet validated as a sellable production service. Verified prospects: 0; contacts: 0; outbound sent: 0; replies: 0; meetings: 0; proposals: 0; revenue collected: $0; paid lookup spend: $0.

## DESIGNED / EXECUTED / VERIFIED

- **DESIGNED:** three co-equal priority-1 missions; V3 shared foundation; XRP forecast admission gate; audio benchmark/deliverable standard; versioned continuity model; nine-platform trust map; Barrot-only Sellbird acquisition and approval controls.
- **EXECUTED:** fetched main metadata and full tree; inspected all 12 open PRs, ancestry, shared diffs, CI/security/gate runs, workflow logs and artifact manifests; inspected main XRP run #220; downloaded and inspected the audio QC artifacts; audited Sellbird v0.5.0 source, license, configuration, dependencies, provider and sending controls.
- **VERIFIED:** main SHA/tree; main full-suite and security checks; XRP run #220 receipt-chain continuity and SQLite integrity; audio artifact existence and technical QC; PR exact-head suite counts listed above; Sellbird upstream test run. Forecast readiness, audio listening acceptance, cross-host continuity, nine-platform coordination, Sellbird installation/authentication, prospecting, outreach, meetings, and revenue remain unverified or blocked.

## Next concrete actions

1. Obtain an independent review of #1714 and the specific authorization required for its automatic Pages deployment side effect. If authorized and all required gates remain green, merge through branch protection, then refetch main, verify the merge commit/files, and rerun main CI.
2. Re-run exact-head full suite and gate for the new #1702 handoff commit. Keep #1702 unmerged until independent review, corrected gate, required approvals, and deployment authorization are satisfied.
3. Consolidate the #1706/#1708/#1709 dependency overlap; do not create more fragmented PRs or close unique work.
4. Fix XRP event-to-receipt linkage and raw-source retention/anchoring; then expand multi-horizon walk-forward evaluation and resolve SEC/Morpho blockers.
5. Inspect/listen to the full-song bundle, record user acceptance, independently verify asset rights, and add native DAW project/interchange support.
6. Demonstrate authenticated cross-host continuity and key handling without weakening V3 safety.
7. Keep Sellbird uninstalled and outbound paused until AGPL review, a verified Barrot demo/offer, mailbox/domain/compliance readiness, and explicit campaign/audience/message/sending approval.

No merge, deployment, secret change, Space restart, Kaggle submission, paper trade, funds transfer, paid lookup, or outbound message was performed.
