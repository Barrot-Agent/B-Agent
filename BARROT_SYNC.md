# BARROT SYNC - Single Source of Truth
# This file is the shared brain-state between Termux Barrot (LunaRoute) and GPT Barrot.
# BOTH must read this before answering. BOTH must update this after any change.

## Identity
- Brain: LunaRoute ONLY - https://gw.lunaroute.com/v1 - lunaroute/glm-5.3-flash
- Canonical Barrot: Termux ~/barrot/Barrot-Agent via b_agent.py
- Relay Barrot: GPT Project (ChatGPT) - NEVER claims to be LunaRoute brain
- Repo: github.com/Barrot-Agent/B-Agent, branch main

## Hard Rules
- Do NOT re-add Orbit. Commit 71cdd8b. ORBIT_REMOVED.md exists.
- Do NOT touch Orbitron font in hf_space/app.py
- Do NOT use password auth. GH_TOKEN via x-access-token only.
- Do NOT re-commit .config/gh/hosts.yml. OAuth revocation is repository-reported; provider-side revocation remains unverified.

## Last State
- GitHub main: 84f28ee Add BARROT_SYNC.md - shared state for Termux + GPT.
- GitHub Orbit-removal commit: 64dc43b Ditch Orbit. The Termux-side reference 71cdd8b remains recorded above; its equivalence to the GitHub commit is not verified.
- Last sync: 2026-11-11T07:58:26.504Z; main 84f28ee7755607236231545a14f3d093c1baaa85; #1661 parent head 26d9cb967996cc48a0c0930d4d5acfb8c379f34a; 1,996 ahead/0 behind; 986 changed files (44 workflows, 942 other paths); 374 open PRs (360 drafts/14 non-drafts); exact-head full suite failed 3,405 passed/2 failed/8 subtests/59.98% coverage (run 42980807226, job 130390518665); failures are two current-map assertion wording mismatches; dependency audit passed (run 42980807234, six manifests, zero known vulnerabilities reported); fail-closed gate passed (run 42980807254); main CI passed (42944864014); main Cross Analysis passed (42982558265). Credential path absent on main/#1661 but present in 17 other inspected PR tips; no contents read; OAuth revocation remains provider-unverified. Branch-protection details HTTP 403; visible fallback ruleset disabled. Pages publication remains unauthorized. Forecast NOT_ISSUED.
- Next task: complete semantic review of 938 non-workflow paths; resolve the inclusive coverage-floor tradeoff (53% vs the prior 70% configured floor); verify provider-side OAuth revocation and remediate the 17 branch-tip copies additively; obtain authoritative branch-protection/approval requirements and Pages-publication authorization; restore safe V3 parity; keep #1661 draft until every gate passes. Preserve #1660 and all unique PRs until successor merge and main verification.

## Conversation Log
- 2026-11-10: User + ChatGPT established LunaRoute as sole brain, Orbit ditched.

- 2026-11-11T05:07Z — GPT relay updated the integration-branch handoff after exact-head CI, current-main/PR reconciliation and fresh public XRP market capture; no main write, merge, deployment or external-model transfer.


- 2026-11-11T06:02:40Z — Run 13 updated the integration-branch handoff/map after exact-head full-suite, six-manifest dependency audit and fail-closed verification; refreshed spot/L2/flows/derivatives/options/ETF/CFTC observations; reconciled SBI/SMBC/Startale JPYSC capital network and Circle/Coinbase Q3 metrics; no main write, merge, deployment, secret action, external-model transfer or forecast issuance.


- 2026-11-11T07:00:00Z — Run 14 recorded the latest exact-head CI failure (12 stale snapshot assertions), refreshed repository/PR/security state, rechecked all 17 affected branch-tip trees without reading credential contents, and captured current Kraken plus conflicting Nov 10 ETF provider updates; no main write, merge, deployment, secret action, external-model transfer or forecast issuance.


- 2026-11-11T07:11:00Z — Run14 follow-up: the first correction reduced full-suite failures from 12 to 3. The remaining failures are assertion wording mismatches for CI classification, Kraken UTC-day open semantics and ETF reconciliation. Latest Kraken and issuer-file ETF snapshots were refreshed; SBI/Evernorth, Circle/Arc, RLUSD/JPYSC, SBIC and Kamilah identity evidence was reconciled. No main write, merge, deployment, secret action, external-model transfer or forecast issuance.


- 2026-11-11T07:26:19Z — Run 15 inspected current main, full trees, 374 open PRs, #1661 head and exact-head CI. Diagnosed five stale current-map assertions on parent ab3763fd5b181672f989d7b9fcee7641ef572a9f; corrected snapshot consistency checks and missing market/capital caveats on the existing integration branch. Dependency audit and fail-closed gate passed; full suite on parent failed five tests. No main write, merge, deployment, secret action, external-model transfer or forecast issuance.


- 2026-11-11T07:36:51Z — Run 15B rechecked current main, integration tree, PR inventory and exact-head CI. Run 42980105698 failed two snapshot-contract tests (NameError in test setup and missing Kamilah unverified-attribution phrase); dependency audit and fail-closed gate passed. Corrected both on the same integration branch; exact-head verification pending. No main write, merge, deployment, secret action, external-model transfer or forecast issuance.


- 2026-11-11T07:58:26.504Z — Run16 inspected current main, full trees, 374 open PRs, #1661 and exact-head CI; rechecked 17 affected branch-tip trees without reading credential contents; refreshed Kraken/OKX spot, Fuelmaps L2, funding/ETF observations, Elliptic/FBI Binance theft-linked XRP flows and Reuters Hormuz oil context; corrected current-map assertion wording metadata and updated the canonical handoff on the existing integration branch. No main write, merge, deployment, secret action, external-model transfer or forecast issuance.
