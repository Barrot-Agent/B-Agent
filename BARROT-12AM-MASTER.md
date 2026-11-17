MASTER FOR BARROT AT 12 - FINAL - Nov 15, 2026

CONTEXT:
Barrot 12AM Harvest. OpenCode resets at 12.

LOCKED IN:
1. HARVEST SEED: Music Theory, Rendering, Metacognition
2. REVERSE ENGINEER ALL 3: Extract pure rules, rebuild from rules only. No copy.
3. SANDBOX HANDICAPS: No Copy, Low Memory (500 tokens), Blind, Deaf, 60-sec, No Internet, One-Shot
4. MEMORY INDEX: What he knows, patterns seen, failures to NOT repeat
5. GUARDRAILS: Max time, max output, if stuck >10 min log and move on

FINAL CONVERGENCE LOOP:
RE -> Isomorphism Probe -> Anti-Cheat -> Failure Taxonomy -> Second-Order Probe -> Axiom Forge -> Emergence Lens -> Plugin -> Skill -> Phoenix

1. ISOMORPHISM PROBE (Grok)
ISOMORPHISM PROBE - ONE SHOT ONLY
You have just extracted a pure rule set for [SOURCE_DOMAIN].
Source rules (do not alter or expand): [PASTE EXACT RULE LIST]
Target domain: [TARGET_DOMAIN] (Music Theory | Rendering | Metacognition)
Handicaps still active: No Copy, Low Memory (500 tokens max), One-Shot, No Internet
Task:
1. Using ONLY source rules, attempt smallest non-trivial task in target domain.
2. Do not import prior knowledge of target domain.
3. Execute attempt.
4. Report in exact schema.
OUTPUT:
TRANSFER_SUCCESS: [list]
TRANSFER_FAILURE: [list + one-sentence reason each]
NEW_PATTERN: [higher-order pattern or "none"]
TOKEN_COUNT: [total]
Cycle: Music->Rendering, Rendering->Metacognition, Metacognition->Music

2. ANTI-CHEAT
Before reporting success, answer:
- "Which EXACT source rule caused this success? Quote it."
- "If I delete that rule, does task still work? Yes/No + why"
If can't quote rule -> LEAKED KNOWLEDGE, not success.

3. FAILURE TAXONOMY
TYPE A - SCALE BREAK: Works but needs different numbers
TYPE B - INVERSION: Works but backwards in target
TYPE C - MISSING AXIOM: Target needs rule source doesn't have
TYPE D - FALSE FRIEND: Looks transferred but meaning changed
Save TYPE C.

4. SECOND-ORDER PROBE
"Take NEW_PATTERN. Apply THAT pattern back to SOURCE. Does it improve source?"
If yes -> UNIVERSAL RULE. Promote to top of Memory Index.
If no -> Keep as domain-specific.

5. AXIOM FORGE (TYPE C ONLY)
AXIOM FORGE - ONE SHOT
Source of TYPE C: [domain + exact missing need]
Failed transfer summary: [one sentence]
Task:
1. Invent single smallest new axiom that would have made transfer succeed.
2. Do not invent more than one.
3. Retest by re-running exact same smallest non-trivial target task with new axiom added.
4. Report only in schema.
OUTPUT:
INVENTED_AXIOM: [exact statement]
RETEST_SUCCESS: true/false
RETEST_EVIDENCE: [one sentence]
AXIOM_COST: [extra tokens or steps]
PROMOTE_CANDIDATE: true/false
Rules: Pass + cost <=2 steps = Provisional Axiom, append to Memory Index under "Provisional Axioms - next harvest only". NOT auto Universal. Must survive next full cycle under handicaps before promotion. Fail = Dead Hypothesis, never generate near-identical again.

6. EMERGENCE LENS
Trigger ONLY if >=2 successful transfers OR >=1 Provisional Axiom this cycle.
Construct smallest hybrid task requiring simultaneous use of material from TWO domains. Execute under full handicaps. Detect non-additive behavior.
Report: HYBRID_TASK, EMERGENCE_DETECTED, EMERGENT_BEHAVIOR, ADDITIVE_BASELINE, NOVELTY_SCORE (0-3), PROMOTE_TO_PHOENIX
Novelty >=2 + promote = write to Phoenix as higher-order pattern candidate.
No emergence = log "Flat combination", do not retry similar hybrids this cycle.

LOGGING JSON (ALL FIELDS)
{
  "timestamp": "ISO-8601",
  "source_domain": "...",
  "target_domain": "...",
  "source_rules_hash": "...",
  "transfer_success": [],
  "transfer_failure": [{"rule": "...", "reason": "..."}],
  "new_pattern": "string or null",
  "task_attempted": "...",
  "outcome_summary": "...",
  "token_count": number,
  "anti_cheat_passed": true/false,
  "failure_type": "A/B/C/D or null",
  "universal_rule_candidate": "string or null",
  "axiom_forge": { "invented_axiom": "string or null", "retest_success": true/false, "axiom_cost": number, "promote_candidate": true/false }
}

HANDICAP RULE
Only Universal Rules + surviving Provisional Axioms may request reduced handicaps. Everything else stays fully handicapped.
