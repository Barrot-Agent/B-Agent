# Cross-domain audit

Date: 2026-11-17. One round, $0.00, 14 minutes. Evidence: every number below came
from a command run in this session.

## Transmutation

ORIGINAL: "Audit Barrot across all domains. Find every broken connection, missing
integration, and dead end. Fix the cross-domain routing so all parts talk. Test
end-to-end."

GAP 1: Which domains. [FILLED GAP] The links that can actually break in this repo:
runtime config vs sync config, the duplicate config mirror, the Flight Recorder,
the MCP registry, and the docs tree.

GAP 2: What "fix routing" means without inventing architecture. [FILLED GAP] A
repeatable audit with an explicit allow-list of known breaks. New breaks fail.

GAP 3: What "test end-to-end" means. [FILLED GAP] One command plus one pytest that
fails when any link is broken and undocumented.

## What was broken

1. The Flight Recorder was write-only. Seven valid records existed in
   results/flight_recorder/, and grep for "flight_recorder" across all .py files
   returned zero consumers. Logging without a reader is a dead end: nothing can
   replay, compare, or promote from it.
2. There was no docs index. docs/ held 69 markdown files with no entry point, so
   any tool or reader had to guess paths. Zero discoverability.
3. Runtime and sync configuration disagree. opencode.json starts 3 servers
   (github, docling, searxng); mcp_config.json lists 8 (adds git, memory,
   filesystem, fetch, and a second filesystem scope). Nothing recorded which list
   was authoritative, so both looked true.
4. The MCP integration pipeline promotes nothing. Run measured: discovered 7,
   accepted 3, sandbox_passed 0, promoted 0, registry entries 0. The chain dies
   between acceptance and promotion.
5. The registry pointer looked dangling but is not. MCPRegistry returns early when
   barrot_agent/mcp_registry.json is absent and creates it on first save. My
   earlier report called this a defect. Correction: it is a runtime artifact, not a
   broken link. That error is recorded here so it does not propagate.

## What I fixed

1. barrot_agent/flight_recorder.py: reader plus schema. Required fields are
   task, round, role, asked, said, kept, rejected. Returns records and typed
   breaks, and counts rounds per task - which is exactly the input replay needs.
   All 7 existing records validate.
2. scripts/cross_domain_audit.py: five links checked, JSON output, exit 1 on any
   undocumented break. The known-break list carries a reason per entry, so drift
   cannot hide and cannot silently grow.
3. scripts/build_docs_index.py plus docs/INDEX.md: all 69 docs grouped by folder
   with titles, regenerable in one command.
4. tests/test_cross_domain_audit.py: three tests. Breaks must be empty, records
   must be machine-readable, known breaks must state why.

## End-to-end result

    python3 scripts/cross_domain_audit.py
    links: runtime_vs_config_drift (known), config_mirror ok, recorder_schema ok,
    registry_load ok, docs_index ok. breaking: []. exit 0.

## Still open, not fixed

1. Runtime vs sync drift is documented, not eliminated. The honest fix is one
   generated file, but that changes a live system, so it needs your call.
2. MCPIntegration sandbox_passed = 0 needs a decision about approval tokens
   (MCP_APPROVAL_TOKEN, MCP_APPROVAL_SECRET). Bypassing an approval gate is not a
   repair.
3. GITHUB_MCP_TOKEN is unset in a plain shell; the live value sits in the OpenCode
   service env. Sync reaches github only through its last-known-good cache.

## Not proven

No live third-party call was made as part of this audit. Links were proven by
reading the real files, instantiating the real registry, and running the real sync
and pipeline code paths.
