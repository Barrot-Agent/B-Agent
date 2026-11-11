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
- Do NOT re-commit .config/gh/hosts.yml - OAuth REVOKED

## Last State
- GitHub main: 84f28ee Add BARROT_SYNC.md - shared state for Termux + GPT.
- GitHub Orbit-removal commit: 64dc43b Ditch Orbit. The Termux-side reference 71cdd8b remains recorded above; its equivalence to the GitHub commit is not verified.
- Last sync: 2026-11-11T06:02:40Z; main `84f28ee7755607236231545a14f3d093c1baaa85`; #1661 integration head `3b11e39f253ac8d07d02eb5da0c770155614f814`; exact-head full suite 3,407 passed, 8 subtests, 59.98% inclusive `barrot_agent` coverage; wheel/primary mission verification passed; six-manifest pip-audit passed with no known vulnerabilities; fail-closed gate passed and automatic merge remains disabled. Main full suite passed 718 tests/8 subtests on exact main SHA. PR #1661 remains draft, 1,991 ahead/0 behind, 982 changed files (44 workflows, 938 other paths), no formal reviews or threads. Main still lacks the primary XRP mission manifest and scheduled collector. GitHub API tree/file/PR inspection works; local Git transport still fails DNS. Main BARROT_SYNC and legacy handoff remain stale. The .config/gh/hosts.yml path remains in 17/17 other open PR tips; OAuth revocation is recorded but not provider-verified. Forecast remains NOT_ISSUED.
- Next task: complete semantic review of 938 non-workflow paths; resolve the inclusive coverage-floor tradeoff (53% vs the prior 70% configured floor); verify provider-side OAuth revocation and remediate the 17 branch-tip copies additively; obtain authoritative branch-protection/approval requirements and Pages-publication authorization; restore safe V3 parity; keep #1661 draft until every gate passes. Preserve #1660 and all unique PRs until successor merge and main verification.

## Conversation Log
- 2026-11-10: User + ChatGPT established LunaRoute as sole brain, Orbit ditched.

- 2026-11-11T05:07Z — GPT relay updated the integration-branch handoff after exact-head CI, current-main/PR reconciliation and fresh public XRP market capture; no main write, merge, deployment or external-model transfer.


- 2026-11-11T06:02:40Z — Run 13 updated the integration-branch handoff/map after exact-head full-suite, six-manifest dependency audit and fail-closed verification; refreshed spot/L2/flows/derivatives/options/ETF/CFTC observations; reconciled SBI/SMBC/Startale JPYSC capital network and Circle/Coinbase Q3 metrics; no main write, merge, deployment, secret action, external-model transfer or forecast issuance.
