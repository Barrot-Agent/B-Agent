# Delivery requirements

Nothing in this file has been executed against a live store. It is the manifest
and the runbook for the day a human authorizes publication.

## 1. Package names

```
github-pr-template-pack-self-guided-v1.0.0-field.zip
github-pr-template-pack-self-guided-v1.0.0-operator.zip
github-pr-template-pack-self-guided-v1.0.0-team.zip
```

Version comes from `deliverables/paid_issue_kit/__init__.py` (`__version__`).
A version mismatch between the zip name and the package is a release blocker.

## 2. Tier manifests

Left column is the path inside the buyer package. Right column is the source
path in this repository. The product root is not the package root.

### Field Kit — $9

Flat package inside `github-pr-template-pack-self-guided/`:

```
README.md              <- deliverables/README_FIELD.md
LICENSE_AND_TERMS.md   <- LICENSE_AND_TERMS.md
CHANGELOG.md           <- deliverables/CHANGELOG.md
templates/issue_intake.md    <- deliverables/templates/issue_intake.md
templates/decision_rules.md  <- deliverables/templates/decision_rules.md
templates/pr_body.md         <- deliverables/templates/pr_body.md
templates/evidence_pack.md   <- deliverables/templates/evidence_pack.md
templates/bounty_ledger.csv  <- deliverables/templates/bounty_ledger.csv
templates/timebox_card.md    <- deliverables/templates/timebox_card.md
```

No Python, no tests, no examples. The buyer gets the forms and the rules. The
internal product README is not shipped; it links to internal files.

### Operator Kit — $19

Flat package inside `github-pr-template-pack-self-guided/`:

```
README.md              <- deliverables/README.md
LICENSE_AND_TERMS.md   <- LICENSE_AND_TERMS.md
CHANGELOG.md           <- deliverables/CHANGELOG.md
run_selftest.sh        <- deliverables/run_selftest.sh
templates/*            <- deliverables/templates/  (6 files)
paid_issue_kit/*.py    <- deliverables/paid_issue_kit/  (6 files)
tests/*.py             <- deliverables/tests/  (4 files)
examples/*             <- deliverables/examples/  (inputs, generated outputs, README)
```

The source tree under `deliverables/` keeps its folders. At packaging time each
source is copied to the package path on the left; folder entries keep their
folder. The README lands at the package root so its relative paths resolve. The
Field Kit uses `README_FIELD.md`; Operator and Team use `README.md`. Do not ship
the internal product README.

### Team Kit — $39

Same files as Operator, plus:

- a `TEAM_LICENSE.txt` generated at packaging time, naming the buying
  organization and the 10-seat limit;
- an invoice from the store;
- the same support terms as section 6.

Do not ship a generic team license that does not name the organization.

## 3. Exclusions

Never in a buyer package:

- `research/` (internal evidence, including rejected platforms)
- `evaluation/` (test logs, improvement log, capability ledger)
- `marketing/` (internal copy variants)
- `PRODUCT_SPECIFICATION.md`, `PRODUCTION_WORKFLOW.md`, `QUALITY_CHECKLIST.md`,
  `PRICING.md`, `CAPABILITY_LEDGER.md`
- `.git/`, `__pycache__/`, `.pytest_cache/`, any `*.pyc`
- any file containing a token, a personal email address, or a local path

One exception: the buyer-facing support address in `LICENSE_AND_TERMS.md` §13 is
allowed inside a buyer package once it is a real address. While it carries the
`PLACEHOLDER` marker, no package may be built or shipped.

`SALES_COPY.md` is internal. The store page is built from it; the file is not
shipped.

## 4. Build steps

```bash
cd products/github-pr-template-pack-self-guided
python3 evaluation/verify_release.py
cd deliverables && ./run_selftest.sh
python3 -m paid_issue_kit score --input examples/candidates.json \
  --out /tmp/ledger.csv --now 2026-11-18T12:00:00+00:00
python3 -m paid_issue_kit pr --plan examples/pr_plan.json --out-dir /tmp/pr
```

The release verifier takes no arguments and resolves its own paths.

Then create the zip with an explicit include list (never `zip -r` the whole
directory), and write `SHA256SUMS.txt` inside the archive:

```bash
zip -X -@ "$ZIP" <<'EOF'
README.md
LICENSE_AND_TERMS.md
CHANGELOG.md
run_selftest.sh
templates/issue_intake.md
...
EOF
sha256sum ./* 2>/dev/null > SHA256SUMS.txt
```

The literal list is the point. A glob would ship internal files on the next
directory change.

## 5. Store settings

- Product type: digital download, one file per tier.
- Instant delivery: on.
- Tax: store is merchant of record; no tax configuration by the seller.
- Refund: 14 days, no questions, handled through the store.
- Email capture: off unless a human explicitly turns it on.
- The listing description must match `SALES_COPY.md`; any change to a number
  needs a matching line in `research/EVIDENCE_LOG.md`.
- Price: $9 / $19 / $39, set only after human sign-off. Changing a price is a
  separate approval.

## 6. Support

**Team Kit only.** 30 days from purchase.

- Channel: a support email. `LICENSE_AND_TERMS.md` §13 currently holds a
  placeholder; the real address is still pending and is a release blocker.
- Response: two business days.
- In scope: installation, running the tests, a failing test traceback, unclear
  documentation, a reproducible bug in the kit.
- Out of scope: debugging the buyer's repository, doing the issue for them,
  bounty disputes with a maintainer, legal or financial advice.
- Refund request: direct to the store, no questions. Do not make a refund
  conditional on support use.

Operator and Field buyers get documentation only. That is stated on the page.

## 7. Updates

- One year of updates for the files in the tier purchased.
- Delivery: the store's file update, or a fresh download link. No account system.
- Every update increments the version and adds a `CHANGELOG.md` line.
- A buyer keeps the version they bought; an update is not a new licence.

## 8. Failed or duplicate delivery

- File will not open: resend the link, then refund if it still fails.
- Duplicate purchase: refund the duplicate in full.
- Wrong tier purchased: refund and let the buyer rebuy, or upgrade at the price
  difference if the store supports it. Do not send both tiers for the lower
  price.

## 9. Formats and accessibility

- UTF-8 Markdown, LF line endings, CSV for the ledger.
- No DRM, no account, no proprietary viewer.
- Files open in a text editor and on a phone.
- The PDF (if one is ever generated) must be generated from the Markdown, not
  hand-edited. No PDF is in Phase 1.

## 10. Release blockers

All must be cleared by a human before publication:

- [ ] Support email created and tested (placeholder in `LICENSE_AND_TERMS.md` §13, marked not for publication)
- [x] Seller legal name and address set in `LICENSE_AND_TERMS.md` (Sean Drew, 1545 Minford Place, Bronx, NY 10460, USA — 2026-11-18)
- [x] Governing law and venue set in `LICENSE_AND_TERMS.md` (New York, USA; Bronx County venue to be confirmed by a lawyer — 2026-11-18)
- [ ] Licence reviewed by a lawyer
- [ ] Test purchase on the live store, including refund path
- [ ] Zip contents verified against section 2, not against a glob (no zip built)
- [x] `verify_release.py` exits 0 (staging gate, 9/9)
- [ ] `verify_release.py --publication` exits 0 (publication gate — currently blocked by design)
- [x] Independent verification report signed (PASS WITH CAVEATS; `evaluation/INDEPENDENT_VERIFICATION.md`)
- [ ] Explicit written authorization from Sean to publish. The 2026-11-18 message authorizes staging only, not publication.

## 11. Privacy

The kit does not collect data. The store holds buyer data and payment details.
The seller must not copy buyer emails into the repository. Support emails are
kept only as long as needed to resolve the request.
