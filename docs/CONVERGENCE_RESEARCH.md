# Convergence research

`scripts/convergence_research.py` runs a bounded, read-only review of
allow-listed GitHub repositories and mathematical sources from
`config/convergence_sources.json`.

Each run writes:

- `ping-pongings/knowledge-base/convergence_reports.jsonl` — ranked candidates,
  internal integration targets, corroboration results, mathematical statuses,
  failures, and next actions.
- `ping-pongings/knowledge-base/convergence_audit.jsonl` — hashes and counts
  for freshness and provenance monitoring.

The weekly `.github/workflows/convergence-research.yml` workflow only creates
review reports. It does not install dependencies, modify source code, alter
canonical datasets, deploy services, or adopt recommendations. Any such
change requires a separate human-reviewed change. Scheduled execution is
bounded by the registry allow-list and repository limit; it is recurring, not
an unbounded process.

Run locally with:

```bash
python3 scripts/convergence_research.py
```
