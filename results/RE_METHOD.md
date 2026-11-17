# How Barrot reverse-engineers — the method, not the mystique

Generated 2026-11-17. Scope: the method I actually run, reconstructed from this
repo. Where a step is not enforced in code, it says so. Companion documents:
`results/meta_re_loop.md` (the ten-stage loop, and why five of its six checks are
self-grading) and `scripts/witness_loop.py` (the only anti-cheat that executes).

## 1. The order I actually run

1. **Pin the claim to a location.** Not "the docs say" — the URL, the file:line,
   the command. A claim with no location is a guess wearing a suit.
2. **Split it into atoms.** One sentence of prose usually holds 2-4 checkable
   facts: a flag, a default, a number, an attribution. Split before fetching.
3. **Pick the cheapest authority per atom.** Executable > schema > official doc
   > README > my own earlier note. My earlier note is last on purpose.
4. **Fetch, quote, diff.** Keep the quoted line next to the claim. Three outcomes:
   supported, refuted, or unsupported-but-not-contradicted. The third is the
   common one and gets written down as such.
5. **Find the smallest fix** for real defects only. A refuted fact is a defect; a
   stylistic preference is not. Where the shell and the prose disagree, the shell
   wins.
6. **Prove before and after.** Run the check that can fail — a test, a build, a
   compile of the code inside the markdown. Record the numbers.
7. **Revert the side effects.** Test runs mutate tracked files in this repo
   (36 files per full `pytest` invocation, measured twice). Anything not mine goes
   back before the commit.
8. **Write the receipt.** What was asked, what I sent, what came back, what I kept,
   what I rejected and why. `results/flight_recorder/`.

## 2. First, then last

**First:** does the pointer resolve? Path exists, schema accepts, command is on
PATH. The cheapest failure in this repo is a dangling reference —
`mcp_config.json` names `barrot_agent/mcp_registry.json`, which does not exist.
Check the pointer, not the prose about the pointer.

**Last:** cross-references and prose coherence — "see Chapter N" when Chapter N is
about something else, a summary that contradicts the paragraph above it. Sweep
these after the facts: fixing prose first hides facts.

## 3. Done vs guessing

Done means every atom has either a fetched source I can quote or an executed
check that could have failed. Guessing is detectable from the inside: I can state
the claim but not the line that proves it.

The formal version is `scripts/witness_loop.py` (10 tests): record the claim, run
the task **with** the rule and **without** it, store the outcome.

| with rule | without rule | state |
|---|---|---|
| success | failure | SUPPORTED |
| any | same | REFUTED |
| failure | success | CONTRADICTED |

If I cannot run the ablation, the honest label is `unverified`, not "done". Five
of the ten loop stages fail this test: they ask the model to grade itself.

## 4. Three mistakes I keep making

1. **Trusting my own earlier summary instead of the artifact.** In a prior session
   I wrote that a token ceiling exists in Grok Build; no docs page has one. The
   error was mine, inherited, and it survived one review pass.
2. **Checking the object, not the path to it.** `artifact.exists()` was checked in
   the wrong directory, so the receipt marked good runs failed. The `mcp_registry`
   pointer above is the same defect in config form.
3. **Letting the harness edit the repo.** Full-suite runs rewrite 36 tracked files
   with timestamps. Twice now the fix has been a scoped revert before committing.

Fourth, smaller, and worth writing down: I chased a phantom build bug because two
chapters reported identical word counts (2378). It was a coincidence, confirmed by
diffing character counts — but I only trusted it after checking.

## 5. The checklist — any target, no Sean required

```
[ ] 1  claim pinned to URL / file:line / command
[ ] 2  atoms split (flag, default, number, attribution)
[ ] 3  cheapest authority chosen per atom
[ ] 4  evidence quoted, not paraphrased
[ ] 5  outcome labelled supported / refuted / unsupported
[ ] 6  defect list ranked by blast radius
[ ] 7  smallest fix, no drive-by edits
[ ] 8  proof run before AND after, numbers recorded
[ ] 9  side effects reverted to a clean tree
[ ] 10 receipt written: asked / sent / returned / kept / rejected
[ ] 11 anything not executed is labelled unverified
```

Rule that survives the whole checklist: **a claim is not true because a model
says so. It is true when deleting the evidence changes a result you can run
again.** Everything above is scaffolding around that one sentence.
