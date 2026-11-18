# Changelog

## 1.0.0 — 2026-11-18

First staged release. The $9 Field Kit contains the templates only; the Python
items below ship with the Operator and Team kits.

- Added the 120-minute phase gate with six ordered phases and a
  `CLAIM HOLDS` / `CLAIM BROKEN` verdict.
- Added the candidate ledger with hard gates for amount, acceptance criteria,
  repo activity, archive state, stars, spam markers, effort, and effective rate.
- Added the PR body builder with five required sections.
- Added the evidence-pack validator: each claim needs evidence and a stated
  limit; a non-zero exit code cannot be presented as proof; the issue URL must
  be http(s).
- Added rejection of bracketed placeholder text such as `[one paragraph]`.
- Added the CLI: `score`, `pr`, `timebox`, `phases`.
- Added six templates: intake, decision rules, PR body, evidence pack, ledger
  header, and the printable timebox card.
- Added 76 tests, a one-command self-test, and generated examples.
- No third-party dependencies. No network call in the kit.

Known limits at release:

- Effort estimates are the operator's; the tool cannot verify them.
- Escrow is never verified by software; the flag is only what a human saw.
- Windows and macOS were not tested. Python 3.10+ is required; the build ran on
  3.13.5 on Linux.
- The validator is conservative and can reject a benign use of a banned phrase.
  Reword the PR body; do not weaken the check.
