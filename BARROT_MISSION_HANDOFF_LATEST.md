# Run 65.1 — second exact-head test diagnosis, audio artifact reinspection and Sellbird source audit — 2026-11-27T02:50:13Z

## #1702 integration test — EXECUTED

The first Run 65 correction removed #1714 from `current_prs` while retaining it under `repair_prs`. That resolved the first inventory mismatch. The next exact-head full suite on `582590b9889a39545b18622557b091bd9b09a98d` still failed one assertion: `dependency_prs[1711].classification` was the generic `blocked`, while the contract requires the machine-readable value `blocked_dependency_compatibility`.

Run [45929935187](https://github.com/Barrot-Agent/B-Agent/actions/runs/45929935187): **4,700 passed, 1 failed, 1 skipped, 11 warnings, 21 subtests; 74.21% coverage**. The only failing test was `test_current_pr_inventory_includes_integration_and_dependency_workstreams`. This Run 65.1 map update changes the classification and records the reason separately. No product code or test was weakened.

Dependency Audit [45929935199](https://github.com/Barrot-Agent/B-Agent/actions/runs/45929935199), Money audit [45929935179](https://github.com/Barrot-Agent/B-Agent/actions/runs/45929935179), and Conflict Integrity [45929935154](https://github.com/Barrot-Agent/B-Agent/actions/runs/45929935154) passed. Gated Merge [45929935192](https://github.com/Barrot-Agent/B-Agent/actions/runs/45929935192) failed for two independently recorded reasons: the required full suite failed, and the legacy gate compares the PR's stored base SHA to current main by equality. GitHub's ancestry comparison remains 156 ahead / 0 behind. #1714 contains the ancestry-based repair; do not duplicate it or bypass the gate.

## #1705 XRP research update — EXECUTED; exact-head CI pending

The existing #1705 branch was extended in place, not forked. Its new head is `08176c52d7b47298fac597e701c832145ef16f29`. The research note now includes a source-grounded reconciliation from Evernorth's September 30, 2026 Form 10-Q:

- Pre-close cash was **$91,397**, restricted cash **$49,995**, digital assets **$341,887,231**, and refundable investor advances **$524,259,563**. The advance liability is not a current cash balance.
- The filing says those advances were settled through equity at the October 9 close and no cash was repaid to investors.
- It separately reports **$29m net cash** from a **$30m principal** convertible note issued October 13, and a discretionary ELOC for up to 5,218,935 shares. The ELOC is capacity, not cash received.
- It reports 346,284,972 XRP in the contribution table and 346,484,972 XRP transferred to Pathfinder after closing. The 200,000 XRP difference matches a separately disclosed delayed-funding quantity arithmetically, but is retained as a reconciliation hypothesis, not a proven sole explanation.
- SBI-affiliated investors are subject to a 39.9% Class A threshold. Ripple received 1,678,382 Class A shares and 16,461,545 Pathfinder units, subject to the disclosed 9.9% ownership threshold.
- Coinbase is named as the principal market for XRP fair-value measurement. That is an accounting price-reference role, not evidence of Coinbase custody or execution venue.

Primary source: [Evernorth Form 10-Q, period ended 2026-09-30](https://www.sec.gov/Archives/edgar/data/2092592/000162828026073871/xrpn-20260930.htm). The updated exact-head CI [45930214468](https://github.com/Barrot-Agent/B-Agent/actions/runs/45930214468) was still running at capture time; dependency, money and conflict checks had passed, and the gate remained in progress. Do not claim the new note has passed full-suite CI until that run completes.

## Professional audio — independent artifact reinspection — VERIFIED technically, not listened to

Downloaded and inspected the #1704 full-song artifact again: [artifact 15139779842](https://github.com/Barrot-Agent/B-Agent/actions/runs/45867292176/artifacts/15139779842), ZIP SHA-256 `f8d8cf4dcc9c26ec83030f2a5a5b4271dd8b224eb1d4de9215e8271cc448cdac`.

- Mix and MIDI file SHA-256 values independently match `quality-control.json`.
- Mix plus nine aligned stereo 44.1 kHz IEEE-float32 WAV stems, each 7,741,555 frames / 175.545 seconds; zero clipped samples.
- Mix: -22.44 LUFS integrated, -6.02 dBFS sample peak, -6.00 dBTP true peak, 7.87 LU loudness range.
- Stem reconstruction correlation 0.999979; relative RMS error 0.006478; maximum absolute error 0.028158.
- MIDI: type 1, 11 tracks (nine instrument tracks plus metadata/marker tracks), 1,751 note-on events, 110.00011 BPM, 4/4, ten section markers.
- The lead's stereo correlation is 0.0074 with 2.978 dB mono-fold-down loss; the existing QC classifies it near threshold. It requires listening/translation review.
- FluidR3_GM is described as MIT-licensed, but the caller-supplied binary's rights remain unverified. There is no native DAW project. No human listening or user acceptance occurred.

## Sellbird v0.5.0 source audit — EXECUTED; not installed or authenticated

Repository `ethanplusai/sellbird`, main SHA `8c743f1c475f61f7b2c04e50501cf6938a126ed6`, 345 tree entries, version 0.5.0, release v0.5.0 published 2026-11-25, AGPL-3.0-only, Python >=3.11. Its actual purpose is AI prospect discovery and outreach, not a persistent-execution/approval framework.

- The CI tests Python 3.11/3.12 on Linux, macOS and Windows; Codex CLI 0.159.3 tests run only on Linux/macOS with localhost mocks and no credentials. The visible workflow tree has no Dependabot configuration or dependency-audit workflow, no lockfile was found, and security-alert counts remain inaccessible. This is source review, not an independent security audit.
- The Docker image runs as non-root, but the build installs the Claude CLI through an unpinned upstream installer. Compose supports native Linux only, uses host networking and keeps the dashboard loopback-bound; remote access is documented through an SSH tunnel. Android/Termux is not documented or tested.
- Model providers are Claude CLI and Codex CLI. ChatGPT desktop dashboard-pane support is upstream-documented but explicitly not tested in the host matrix; direct ChatGPT model-provider support is not available. Gemini/Grok/Copilot/Hugging Face/Kaggle/Databricks are not Sellbird model providers.
- The separate agent token is allowlisted: it can read records, estimate costs, draft/propose, move stages, record meetings and pause sending. It cannot approve/send/resume, run discovery, confirm paid signals, change keys/settings, purchase or delete. A signed-in browser pane is a user session and can click user-level approval controls, so it must be supervised.
- The template has email enabled, approval required, a 50/day cap, no warmup start date, no configured send window, blank postal address, empty suppression list, Precleared disabled and LinkedIn disabled. Set email disabled until a specific campaign is approved; do not treat approval-default as a substitute for domain, compliance or warmup readiness.
- Free discovery defaults include OpenStreetMap and limited TinyFish. Paid options are explicitly priced before execution: DataForSEO Business Listings $0.372/1,000, SERP $0.006/search, Maps $0.002/search; Serper has 2,500 free searches. Reoon 600 and ZeroBounce 100 validations/month are documented free tiers. No paid lookup occurred.
- Barrot is Apache-2.0; Sellbird is AGPL-3.0-only. Keep Sellbird a separate process behind its documented MCP/API boundary and do not copy its source into Barrot. AGPL Section 13 imposes source-offer duties for users interacting remotely with a modified network service; obtain legal review before distributing a combined work or hosting a modified Sellbird service.
- Sellbird remains not installed, not authenticated, no supported host verified, no prospects, no messages, no meetings and $0 revenue. All outreach remains paused and Barrot-only.

## Next actions

1. Verify exact-head full-suite CI for the Run 65.1 handoff/map commit; do not merge #1702 on the basis of the previous failing head.
2. Wait for #1705 head `08176c5` exact-head full-suite result; do not claim the SEC addendum passed before that result.
3. Obtain independent review and verify required approvals for #1714; its ancestry gate fix must pass exact-head checks. Do not merge while Pages deployment authorization is absent.
4. Continue the main XRP event-receipt linkage, multi-publisher depth/flow and raw-artifact rebuild gaps; no forecast until independent walk-forward evidence supports it.
5. Complete audio listening, lead mono-translation review, source-rights confirmation and native DAW project export.
6. Keep Sellbird sending disabled until a supported host, separate mailbox/domain, SPF/DKIM/DMARC, warmup, postal address, suppression list, legal review and explicit campaign approval are verified.

No merge, deployment, secret change, paid lookup, prospecting run, outbound message, paper trade, funds transfer or real-money action occurred.


---

