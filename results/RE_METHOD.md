# How Barrot reverse-engineers

Updated 2026-11-17. One page. Companion: results/meta_re_loop.md (the ten-stage
loop and why five of its six checks grade themselves), scripts/witness_loop.py
(the only anti-cheat that executes).

## 1. Steps, in order

1. Pin the claim to a location: URL, file:line, or command. A claim with no
   location is a guess wearing a suit.
2. Split it into atoms. One sentence usually holds 2-4 checkable facts: a flag, a
   default, a number, an attribution.
3. Pick the cheapest authority per atom: executable > schema > official doc >
   README > my own earlier note. My note is last on purpose.
4. Fetch, quote, diff. Label each atom supported / refuted / unsupported. The
   third is common and gets written down as such.
5. Fix only real defects, smallest change, no drive-by edits.
6. Prove before and after with a check that can fail: test, build, or compile the
   code inside the markdown.
7. Revert side effects, then write the receipt: asked, sent, returned, kept,
   rejected.

## 2. Check first vs last

First: does the pointer resolve? Path exists, schema accepts, command is on PATH.
Cheapest failure in this repo is a dangling reference: mcp_config.json line 94
names barrot_agent/mcp_registry.json, which does not exist. Check the pointer, not
the prose about the pointer.

Last: cross-references and coherence, such as "see Chapter N" when Chapter N is
about something else. Sweep these after the facts, because fixing prose first
hides facts.

## 3. Done vs guessing

Done means every atom has a quoted source or an executed check that could have
failed. Guessing is detectable from inside: I can state the claim but not the line
that proves it.

The formal version is scripts/witness_loop.py (10 tests): run the task with the
rule and without it, store the outcome.

| with rule | without rule | state |
|---|---|---|
| success | failure | SUPPORTED |
| any | same | REFUTED |
| failure | success | CONTRADICTED |

If I cannot run the ablation, the honest label is unverified, not done.

## 4. Three mistakes I keep making

1. Trusting my own earlier summary instead of the artifact. I once wrote that a
   token ceiling exists in Grok Build; no docs page has one. It survived a review
   pass because I checked the prose, not the source.
2. Checking the object instead of the path to it. An artifact existence check ran
   in the wrong directory and marked good runs failed. The dangling registry path
   above is the same defect in config form.
3. Letting the harness edit the repo. One full pytest run rewrites 36 tracked
   files with timestamps; twice now the fix has been a scoped revert before commit.

## 5. Checklist for any new target

```
[ ] 1  claim pinned to URL / file:line / command
[ ] 2  atoms split (flag, default, number, attribution)
[ ] 3  cheapest authority chosen per atom
[ ] 4  evidence quoted, not paraphrased
[ ] 5  outcome labelled supported / refuted / unsupported
[ ] 6  defects ranked by blast radius
[ ] 7  smallest fix applied
[ ] 8  proof run before AND after, numbers recorded
[ ] 9  side effects reverted, tree clean
[ ] 10 receipt written: asked / sent / returned / kept / rejected
[ ] 11 anything not executed is labelled unverified
```

The rule under the checklist: a claim is not true because a model says so. It is
true when deleting the evidence changes a result you can run again.
