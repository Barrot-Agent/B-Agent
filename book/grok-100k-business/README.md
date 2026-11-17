# How to Build a $100K/Month Business With Zero Employees Using Grok Bot

Manuscript project. Source TOC supplied by the Orchestrator on 2026-11-17.
297 pages stated; supplied units sum to 216; the 81-page difference is carried
explicitly in `toc.yaml` under `proposed` and is labeled everywhere it appears.

## Build

```bash
python book/grok-100k-business/build_book.py          # measure + assemble
python book/grok-100k-business/build_book.py --strict # fail on any non-final unit
```

Output:

- `dist/book.md` — assembled reading order, with a comment per unit showing status and pages
- `dist/build_report.json` — measured words, pages, ratios, missing files, problems

The build exits non-zero when a file is missing, a `draft` unit is empty, or a
`draft` unit lands outside 60–150% of its page target. Page estimates use a house
standard of **320 words per page**; code blocks and HTML comments are excluded from
the word count so a code-heavy chapter is not flattered.

## Status

| Range | Status |
|---|---|
| Front matter (7 units) | drafted |
| Part One, Chapters 1–6 | drafted |
| Part Two, Chapters 7–12 (Phase A) | drafted |
| Part Three–Five, Chapters 13–29 | outline (beats written, prose pending) |
| Part Six, Chapters 30–34 | proposed — not in the supplied TOC |
| Appendices A–F | proposed — not in the supplied TOC |

Measured at the last build: **75.9 drafted pages of 89 targeted (85%)**, 85.9 pages
of content present in the repo including outlines. Phase A (Chapters 7–12) measures
40.5 of 44 target pages (92%).

## Evidence policy

Every claim in the manuscript is one of three kinds and is labeled as such:

1. **Documented** — appears on the vendor's own docs. Checked 2026-11-17 against
   `docs.x.ai` (overview, Grok Bot, Grok Build, pricing). Prices change; the
   arithmetic method does not.
2. **Measured** — produced by running code in this repository. Test counts,
   verifier findings, cost arithmetic from a real run.
3. **Assumed** — an input the reader must replace: price, conversion, hours saved.
   Assumptions appear with a sensitivity table.

No benchmark scores are claimed. No product capability appears that is not in the
verified set. Where the supplied TOC names something that is not a documented
product ("Grok Swarm"), the chapter treats it as a pattern built from documented
primitives and says so.

## Layout

```
toc.yaml                 contract: ids, titles, page targets, status
build_book.py            measure + assemble
manuscript/00-front-matter/
manuscript/part-1..part-6/
appendix/
dist/                    generated (gitignored)
```

## Recovery note

On 2026-11-17 a cleanup command (`git ls-files --others | xargs rm`) deleted the
untracked manuscript and tooling. Everything was reconstructed from
`dist/book.md`, which is generated but also a complete copy of the text. Two
lessons are encoded in the project now: `dist/` is treated as a backup as well as
an artifact, and no bulk delete of untracked files is ever run in this repo.
