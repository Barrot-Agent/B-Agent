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
- Last sync: 2026-11-11T05:07Z; main `84f28ee7755607236231545a14f3d093c1baaa85`; successor #1661 head `f7ce5b44b67c063dd37de5683df647244a592692`; exact-head full suite 3,407 passed, 8 subtests, 59.98% coverage; core 714 passed; six-manifest dependency audit and fail-closed gate passed. Main still lacks the XRP mission manifest and scheduled collector; both are on the draft successor. GitHub API repository inspection works; local Git transport currently fails DNS. LunaRoute remains the sole canonical brain; GPT is relay only; no LunaRoute endpoint auth was tested. OAuth revocation is recorded as REVOKED but not provider-verified; 17 other open PR tips still contain the `.config/gh/hosts.yml` path (tree metadata only). Forecast remains `NOT_ISSUED`.
- Next task: finish semantic review of 938 non-workflow paths and 44 workflow changes; verify owner-reported OAuth revocation and remediate the 17 branch-tip copies additively; obtain authoritative branch-protection/approval requirements and Pages-publication authorization; restore safe V3 parity; keep #1661 draft until all gates pass. Preserve #1660 and all unique PRs until successor merge and main verification.

## Conversation Log
- 2026-11-10: User + ChatGPT established LunaRoute as sole brain, Orbit ditched.

- 2026-11-11T05:07Z — GPT relay updated the integration-branch handoff after exact-head CI, current-main/PR reconciliation and fresh public XRP market capture; no main write, merge, deployment or external-model transfer.
