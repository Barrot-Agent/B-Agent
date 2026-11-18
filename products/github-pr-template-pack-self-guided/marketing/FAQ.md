# FAQ

**Is this a list of live bounties?**

No. It is a decision and packaging kit. It does not scrape, list, claim, or track
bounties. You bring the issue; the kit helps you decide whether to start and what
to send.

**GitHub gives PR templates away for free. Why pay?**

Correct, and the pack says so. The free template is a form. The paid part is the
decision layer: nine hard gates, effective rate after fees, a scored ledger, a
120-minute phase gate that can report `CLAIM BROKEN`, and an evidence-pack
validator. If you only want a PR template, use a free one. The $9 tier is priced
for the intake and rules, not for a file GitHub already supports.

**Does it work with Algora, IssueHunt, or Opire?**

The ledger accepts any issue URL and an optional platform label. It does not call
a platform API. Two platform facts changed during research: Algora's site now
sells talent placement and `algora.io/bounties` returned 404; IssueHunt's home
page now sells security bug bounties. Opire still describes an issue-bounty
model. Do not trust a platform name in old copy; check the platform yourself.

**Do you promise that a bounty will pay?**

No. A stated bounty is not escrow, and the intake makes you record whether you
actually saw escrow. `escrow_verified` is a human observation, not a software
check.

**Is "in 2 hours" realistic?**

It is a 120-minute timebox you control, not a prediction of review time. In 112
merged PRs sampled across three public repositories, the pooled median
open-to-merge time was 1.11 hours and 52.7% merged within two hours. That is
review latency, not contributor effort. If an issue is estimated over three
hours, the default gate says NO-GO.

**What if the timer runs over?**

The tool reports `CLAIM BROKEN` and keeps the row. That is deliberate. A timer
that always says success is a decoration; this one can fail.

**Do I need Python?**

Only for the $19 and $39 tiers. The $9 tier is Markdown and CSV. The Python kit
is standard library only, Python 3.10+.

**Do I need an API key, a GitHub token, or an internet connection?**

No. The kit makes no network call. The optional research script uses the GitHub
CLI, but it is not part of the buyer package.

**Does it open or submit pull requests?**

No. It builds a PR body and an evidence pack; you open the PR.

**What does the validator block?**

Missing sections, missing issue link, missing test command, missing result,
missing rollback, fewer than two checked items, placeholders such as TODO or
<insert, and claims such as "guaranteed", "zero risk", "production-ready", or
"bulletproof". The evidence pack also rejects a non-zero exit code presented as
proof. It does not fetch the URL, so it checks link shape, not that the issue
exists.

**Can it reject something valid?**

Yes. The check is conservative. A benign use of a banned phrase will be blocked;
reword the text. Do not weaken the check to get one PR through.

**Is the code open source?**

No. It is source-available under the product licence: read it, run it, modify it
for your own use, but do not publish or resell it. See
`LICENSE_AND_TERMS.md`.

**What if the tests fail on my machine?**

Run `./run_selftest.sh` and send the traceback with your OS and Python version
(Team tier includes 30 days of support). The build was tested on Python 3.13.5
on Linux; Windows and macOS were not tested.

**Do I get updates?**

One year of updates for the tier purchased. Each update adds a changelog line
and a version bump.

**Can I share it with my team?**

Up to 10 seats with the Team Kit, inside one organization. Field and Operator
are one person each.

**Refunds?**

14 days, no questions, through the store. A refund ends the licence.

**Is this financial, legal, or career advice?**

No. It is a workflow and a set of templates. It contains no trading signals, no
income figures, and no legal advice. The licence is a draft and must be reviewed
before publication.

**Why is the status "staged, not published"?**

Because the governance rule is fail-closed: build, test, and stage on a branch,
then stop for human authorization. No store listing exists, no price is live, and
no money has moved. The README says so at the top.
