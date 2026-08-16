# Session Federation Runbook

`SessionManager` can inventory and merge local agent transcripts without
modifying their source files.

## Scope and validation

`inventory_repository_sessions(repository_dir)` considers only `.json`,
`.jsonl`, `.md`, and `.txt` files. It excludes `.git`, `.directive_platform`,
`.venv`, `node_modules`, and `__pycache__`, rejects files over 5 MiB, and
reports malformed, unrelated, and content-duplicate files in `excluded`.
Included records contain the relative transcript path, source session ID,
format, timestamps, status, directive, participants, and message count.

## Merge and review

`merge_repository_sessions()` imports included transcripts with source
provenance, creates a new chronological de-duplicated session, and generates
a versioned unified report. Original transcript and session files are never
deleted. A reviewable audit is written to
`.directive_platform/reports/session-audit.json`; it records exclusions,
the merged session, and report location. With a custom `sessions_dir`, the
same file is written under that directory's parent `reports/` directory. The
audit is marked
`approval_required: true` and `approved: false` until a human reviews it.

Review the audit and unified report before any cleanup or merge-queue action.
Use the merge queue's documented dry-run mode and add its label only to PRs
that have passed required checks and approvals.
