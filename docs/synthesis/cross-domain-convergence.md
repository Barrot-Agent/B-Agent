# Cross-domain synthesis and convergence

Date: 2026-11-17. One page. Sources: docs/fields/track-01-cymatics.md,
results/RE_METHOD.md, results/flight_recorder/, the fields track contract in
MEMORY.md.

## Transmutation of the request

ORIGINAL: "Let's do cross domain synthesis and convergence and then go server."

GAP 1: Which domains. [FILLED GAP] The four artifacts that already exist and that
the server depends on: cymatics, the RE method, the Flight Recorder, the fields
contract. Not a new reading list.

GAP 2: What convergence means. [FILLED GAP] Not "the domains are similar". A
convergence claim is only worth making if the same rule can be removed from all
four and each one measurably degrades. Agreement is cheap; ablation is not.

GAP 3: What the output is. [FILLED GAP] One page with three shared patterns, one
named method, and the gaps that would make GO SERVER dishonest.

TRANSMUTED: "Ablate four existing artifacts for shared rules, name the method they
converge on, and list what still blocks the server. One page, plain ASCII."

## 1. Convergence: three rules that appear in all four

Rule A. The artifact outranks the narrator.
- Cymatics: the pattern is measured on a grid; the prose about the pattern is
  worth nothing next to the 0.16% error.
- RE method: quote the source, do not paraphrase it. My own earlier note ranks
  last as authority.
- Flight Recorder: a receipt is written by the harness, not by the agent. Agent
  self-report is testimony, harness output is measurement.
- Fields contract: L1 requires units and conditions; without them a claim drops
  to L3 no matter how confident it sounds.
Ablation test: remove it and every domain accepts a fluent description as proof -
the exact failure meta-RE found in five of ten loop stages.

Rule B. Conditions travel with the claim.
- Cymatics: same frequency on a different plate gives a different pattern. The
  boundary conditions are part of the result, which is why "frequency -> pattern"
  is false and "frequency + object -> mode" is true.
- RE method: pointer first, then atoms, each with its own authority and label.
- Flight Recorder: compare the same task and the same skill version, or the
  comparison means nothing.
- Fields contract: L1 vs L2 separation exists because an applied result carries
  its build and environment with it.
Ablation test: remove it and you compare different objects, tasks, or builds.
Those comparisons always pass and always mean nothing.

Rule C. Do not collapse ambiguity into a verdict.
- Cymatics: degenerate pairs give two patterns at one frequency. My per-axis
  prediction failed there and the failure was kept, because it is the mechanism.
- RE method: supported, refuted and unsupported are three states. Merging
  unsupported into refuted is how a guess becomes a fact.
- Flight Recorder: verdicts are promote, keep old, investigate. "Investigate" is
  a legitimate output, not a failure to decide.
- Fields contract: L3 is preserved and quarantined, not deleted and not promoted.
Ablation test: remove it and every ambiguous case gets rounded to the nearest
confident answer.

## 2. Synthesis: the method that emerges

Name: THE THREE-GATE METHOD.

G1 PIN. Before anything: does the pointer resolve, and what are the atoms? A claim
with no location is not a claim.
G2 COMPARE. Only compare under identical conditions, with an executed or recorded
artifact on both sides. Different object, task, or version means no comparison.
G3 PRESERVE. Output three states, not two: supported, refuted, unverified. Or
promote, keep old, investigate. Ambiguity is data.

The sentence under all three: a claim is a mode. It exists only relative to the
boundary conditions that produced it, and two modes at the same frequency are not
the same mode.

Each server tool maps to one gate: reverse_engineer and transmute_query to G1,
replay and compare to G2, the three-state verdicts to G3.

## 3. Three gaps that would make GO SERVER dishonest

1. No comparable pair exists. Each recorder file holds one mission; cost and
   minutes appear as free-form numbers, accuracy and error counts appear nowhere.
   With n=1, "improved" and "regression" cannot be computed, so any output would be
   invented. Required: one schema, two runs of the same task and skill version.
2. No scoring rule for transmute_query. The tool can return ORIGINAL/GAP/
   TRANSMUTED text, but nothing defines a better transmutation. Without a gate it
   is a text generator with a confident name. Required: a pass/fail criterion, for
   example the transmuted query must name a constraint the original did not.
3. No capability-to-test binding for reverse_engineer. It must return steps_used,
   but nothing checks the steps against executed evidence. Required: each step
   cites a file, command, or commit, or the step is marked unverified.

Not a gap, already solved: check_capability has real data in
barrot_capability_audit.json, and the registry file it points at still does not
exist, so the pointer check from G1 applies before the server starts.

