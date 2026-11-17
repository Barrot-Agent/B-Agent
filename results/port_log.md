# Port log — `origin/work` → `main`

Date: 2026-11-17. Range examined: `git log main..origin/work` = **841 commits**.
Merge base: **none** (unrelated histories). Decision: **0 commits ported, 0 files ported.**

This file records why, per the instruction "port ONLY what is real; skip duplicates
and stale work, and log why".

---

## 1. Commit classification (841 total)

| category | count | verdict |
|---|---:|---|
| `🏓 Barrot-SHRM Ping-Pong cycle executed at …` | 393 | automated noise: one timestamped record per run, superseded by `barrot_agent/agi/emit_pingpong.py` on main |
| `Create/Update/Add/Remove …` | 157 | workflow/manifest churn: `bundles.yml`, `manifest.yml`, `build_manifest.yaml`, `BBR.yml` rewritten repeatedly; main already has its own CI set |
| "other" (PR features / Copilot plans) | 126 | see §3 — 30/33 Python files already exist under `barrot_agent/` |
| `Barrot pulse snapshot at …` | 89 | automated telemetry snapshots, no code |
| merge commits | 76 | content covered by the rows above |

No commit in the range survives all three filters (real, non-duplicate, safe).

---

## 2. File-level reality check

```
paths only on origin/work : 155
  of those, content found nowhere in main : 138
  of those, moved copies of main content  :  17
shared paths with different bytes         :  17  (all one-way: work holds stubs)
shared paths byte-identical               :  73
```

### The 17 shared-but-different files

Every one is an older/stub version of something main already has in a larger form:

| file | main | origin/work |
|---|---:|---:|
| `scripts/transmute.py` | 15,144 B (real engine) | 1,131 B (stub) |
| `results/transmute_log.json` | 33,378 B (21 records) | 70 B (`{"note": "…Phoenix remembers…"}`) |
| `.opencode/agent/barrot.md` | 5,140 B | 1,107 B |
| `README.md` | 29,527 B | 18,276 B |
| `requirements.txt` | 297 B | 161 B |
| `build_manifest.yaml` | 13,073 B | 13,438 B (older layout) |
| `dependency-ingestion-config.yaml` | 12,206 B | 11,745 B |
| `.github/workflows/Barrot.Cognitive.PingPong.Engine.yml` | 505 B | 4,159 B |
| `PINGPONG_USAGE.md` | 9,423 B | 1,275 B |
| `Dockerfile`, `.dockerignore`, `.gitignore`, `.github/FUNDING.yml`, `app.json`, `PINGPONG_USAGE.md`, `ping-pongings/knowledge-base/config.json`, two `merge_conflict_*.json` | — | older/parallel |

Porting any of these would **regress** main.

### The 138 files that exist nowhere in main — why none were ported

```
33 .py    -> 30 already have a same-stem module under barrot_agent/
             (agi_orchestrator, agi_reasoning, transformative_insights,
              mmi_data_analyzer, monetization_engine, quantum_entanglement,
              email_analyzer, character_capability_analyzer, advanced_algorithms,
              barrot_integration, emit_pingpong, …)
           -> 3 have no counterpart, and none are wanted:
              coin-app/coin_app_automation.py  (abandoned token presale app,
              coin-app/example_usage.py         pairs with contracts/ChameleonToken.sol)
              pingpong_emitter.py             (explicitly superseded: see main's
              barrot_agent/agi/emit_pingpong.py docstring, "the original file was…")
61 .md    -> docs describing the pre-refactor layout (root-level scripts,
             DEFAULT_BRANCH_*, MIGRATION_CHECKLIST, MOBILE_SETUP, Heroku/Railway/
             Render/Vercel configs). Main restructured away from this on purpose.
11 .yml   -> BBR.yml, bundles workflows, ping-pong workflows, arc-agi-parallel-test.
             Main has its own workflow set; these are unmaintained duplicates.
 9 .json  -> package.json / package-hardhat.json / pingpong_request.json / configs
             for the abandoned coin-app.
 6 .yaml  -> deploy configs (fly, render, convery) for platforms main no longer uses.
 6 (no ext) -> Procfile, runtime.txt, contracts/*, spells/*
 3 .html  -> site/index.html, chameleon-presale.html, search-engine/index.html
             (a presale landing page — not part of the agent)
 2 .toml  -> railway.toml, fly.toml
 2 .sh    -> delete-main-branch.sh  (destructive, must not enter main)
             migrate-default-branch.sh
 1 .txt   -> runtime.txt
```

### Governance block

Five of the 138 carry vocabulary that `scripts/pillars_check.py` flags:

```
glyphs/hermetic_quantum_fusion_glyph.yml   quantum chronodynamics
glyphs/organoid_reasoning_glyph.yml        bio-computing
glyphs/temporal_plasticity_glyph.yml       quantum chronodynamics
memory-bundles/shrm-v2-config.json         SHRM v2
simulation-stack/shrm-v2-config.yml        SHRM v2, bio-computing
```

Porting them would re-introduce into main exactly what Phase 4.4 removed from
the prompt surface.

---

## 3. Cherry-pick feasibility

`main` and `origin/work` have **no merge base**. Every cherry-pick computes a diff
against a parent that does not share main's tree. The 1388-file diff means the
first pick alone conflicts across the full refactor (root `agi_orchestrator.py`
vs `barrot_agent/agi/agi_orchestrator.py`, root `README.md` vs rewritten
`README.md`, etc.). A literal "one commit at a time" port would produce hundreds
of manual conflict resolutions to re-add superseded files.

Not attempted. Not because it is hard, but because the target content is wrong.

---

## 4. What was actually done

- `origin/work` left untouched. No force-push, no delete, no reset.
- Local branch `work` left at `0732187` as a placeholder; it tracks nothing.
- Stash `stash@{0}` (`main-wip-before-work-merge-20261117`) popped back onto
  `main`; working tree restored to 62 changed paths.
- Outside-git backup kept at `~/barrot/backup-20261117/`
  (`main-wip-untracked.tar.gz` 31 entries, `main-wip-tracked.patch` 2854 lines).

## 5. Recommendation

Leave `origin/work` as an archive. If any of the 138 ever matters, the cheapest
safe path is file-level:

```
git show origin/work:<path> > <path>    # one file, reviewed, then tested
```

Never a merge, never a force-push.
