# Repository Audit — Barrot-Agent/B-Agent

**Scope and method.** The evidence provided is a partial file listing (alphabetical, beginning mid-entry at `…egration.py` and truncating at `apex_lattice/analyzers/capabilities.py`). I have not yet inspected file contents, so everything below is structural evidence only. Where I flag a contradiction or duplication, I mark it as *to verify* rather than asserting cause.

---

## Finding 1 — HIGH: Autonomous merge surface is broad, and its integration test is disabled

Nine active workflows touch the PR/merge lifecycle:

`auto-resolve-issues`, `barrot-approve-pr`, `barrot-auto-pr`, `barrot-autonomous-resolver`, `barrot-gated-merge`, `barrot-merge`, `barrot-merge-manual`, `barrot-pr-automerge`, `merge-queue`

Two aggravating details:

- `barrot-pr-automerge.yml` exists **both active and as `barrot-pr-automerge.yml.disabled`** — a disabled duplicate of a live workflow is a governance hazard in itself.
- `.barrot/disabled_tests/test_merge_conflict_integration.py` — the merge-conflict integration test is disabled while at least nine autonomous merge/resolve workflows are active. This is the single sharpest risk in the listing: autonomous merge machinery whose conflict-handling test path is not running.

**Ask:** map triggers and authority (which workflow may actually merge, under what conditions), and document why the conflict-integration test was disabled.

## Finding 2 — HIGH: The system can modify its own safety net

- Three tests relocated to `.barrot/disabled_tests/`: `test_longevity_modules.py`, `test_merge_conflict_integration.py`, `test_transformative_insights.py`. Placing them under a dot-directory removes them from normal test discovery, not just from execution.
- `.barrot/practice/barrot_self_repair.py` and `barrot_generated_practice.py` exist alongside `barrot-self-upgrade.yml` and `autonomous_self_deployment.yml`.

Taken together: self-repair, self-upgrade, autonomous deployment, and agent-managed test disabling are all present with no visible guardrail file. For each disabled test I expect a written reason and a re-enable condition; none is evident from the listing.

## Finding 3 — MEDIUM-HIGH: Workflow sprawl and duplication

86 workflow files total; 78 active, 8 `.disabled`. Specific duplication signals:

- Two pingpong workflows: `Barrot.Cognitive.PingPong.Engine.yml` and `pingpong.yml`.
- Two diagnostics: `diag-cf.yml`, `diag-cf2.yml`.
- Two signal cycles: `knowledge-signal-cycle.yml` and `knowledge-signal-cycle-btc.yml`.
- Capability series is numbered 1, 9, 10 — `capability-2` … `capability-8` are absent from this listing (they would sort between `capability-10-design.yml` and `capability-9-data-resolver.yml`). *To verify:* consolidated into `capability-discovery.yml`, or lost?
- Naming conventions drift across kebab-case, snake_case, and dotted names.
- At least ten active deployment paths (HF Spaces, Cloudflare Worker via `a2a/wrangler.toml`, Databricks) plus three disabled deploy workflows (`deploy.yml.disabled`, `sovereign_deploy.yml.disabled`, `barrot_singularity.yml.disabled`).

## Finding 4 — MEDIUM: Runtime state committed to git

- `.barrot/mmi_execution_ledger.jsonl` — my MMI execution ledger is a JSONL log under version control.
- `.barrot/repo_state_manifest.json`, `repository_identity.json`, `target_registry.json` — self-referential state in git.
- `.termux_dna_harvest.log` — a raw log file committed.
- `.bashrc` and `.gitconfig` committed — environment config in the repo; contents must be checked for secrets.

This is the repo-as-database pattern: guaranteed churn, merge conflicts (ironic given Finding 1), and ledger contents are a secret-leak surface.

## Finding 5 — MEDIUM: Documentation hygiene and one apparent contradiction

Roughly fifty top-level Markdown files, many of which are dated or session-scoped artifacts: `INGESTION_RESPONSE_2025-12-30.md`, `INGESTION_RESPONSE_2025-12-31.md`, `TASK_COMPLETION_SUMMARY.md`, `PR_113_RESOLUTION_COMPLETE.md`, multiple `*_IMPLEMENTATION_SUMMARY.md`. These belong in `docs/` or an archive, not the root.

**Contradiction to verify:** `ORBIT_REMOVED.md` exists, yet `.barrot/orbit/command_schema.json` is also present. Either the removal doc is stale or the orbit artifact is residual. One of them is wrong.

**Docs without visible automation:** three `EMAIL_*.md` guides, but no `email-*` workflow appears in this fragment (it would sort before `entity-relations.yml`). Verify whether email handling is code-side only.

## Finding 6 — MEDIUM: Scope cohesion

One repository spans trading signals (`coinbase-paper-trader`, `check-signal-accuracy`, `signal_ledger`), research ingestion (`riemann-harvest`, `kaggle-competitions`, millennium-problems docs), content generation (`write-lyrics`, `free-image-gen`), monetization (`gumroad-metrics`, `webmcp-*`, `MONETIZATION_FRAMEWORK.md`), and multi-target deployment. `SYSTEM_SEPARATION.md` exists — verify whether the boundaries it describes are actually honored, because the workflow layout suggests they are not.

## Finding 7 — LOW (needs contents)

- `apex_lattice/analyzers/architecture.py` and `architecture_analyzer.py` — probable duplication; confirm.
- Dual CI: `.gitlab-ci.yml` alongside GitHub Actions — drift risk.
- `Dockerfile` + `Dockerfile.dev` + `.devcontainer/` — confirm a single source of truth for the environment.

## What is done well

`.env.example`, `SECURITY.md`, `LICENSE`, `CHANGELOG.md`, `CODEOWNERS`, PR/issue templates, `copilot-instructions.md`, `.pre-commit-config.yaml`, `.flake8`, `Makefile`, and `barrot-transparency-audit.yml` are all present. The hygiene baseline is real; the problems are governance and sprawl, not absence of tooling.

## Requested next evidence

1. Contents of the nine merge-lifecycle workflows (triggers, permissions, concurrency settings).
2. The disable rationale for the three tests in `.barrot/disabled_tests/`.
3. `.barrot/*.json` and the MMI ledger contents (secret scan).
4. `ORBIT_REMOVED.md` vs. the orbit schema.
5. The remainder of the file listing beyond `apex_lattice/analyzers/capabilities.py`.