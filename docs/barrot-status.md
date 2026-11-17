# Barrot status

Updated: 2026-11-17
Scope: MCP tools 3 and 4, plus the reverse-engineering method.

## MCP server (5-tool spec) - NOT BUILT

No handler, no file, no tests exist for any of the five tools. Nothing is stubbed.

### Tool 3 - flight_recorder_replay - NOT BUILT

- Required input: mission_id, skill_version.
- Required output: original vs replay (accuracy, time, cost, errors), improved,
  regression, verdict.
- Blocker: results/flight_recorder/ holds one mission with 3 records
  (2026-11-17-ch08.jsonl). There is no second run of the same task and skill
  version, so there is nothing to compare. Any pair would have to be invented.
- The comparison logic is small. The data does not exist yet. Status is
  NOT_IMPLEMENTED for the honest reason, not for lack of code.

### Tool 4 - reverse_engineer - NOT BUILT

- Spec arrived truncated: the message ends inside this tool's return object at
  "steps_used": ["1.",
- Fields after steps_used are unknown. Tool 5 never arrived at all.
- Building it now would mean inventing a contract other callers depend on.

### Tool 1 - check_capability - buildable, not built

- Real source exists: barrot_capability_audit.json has current_capabilities (122),
  evidence, and gaps. Git commit lookup can supply the evidence path.

### Tool 2 - run_foundry_cycle - blocked

- No Foundry exists: grep for "foundry" across all .py files returns 0 hits, and
  there is no Foundry directory. Sean has not authorised building it.
- A tool that can only return ERROR: NOT_IMPLEMENTED is a stub by his definition.

### Config defect found on the way

- mcp_config.json line 94 sets registry_path to barrot_agent/mcp_registry.json.
  The file does not exist. barrot_agent/mcp_registry.py does.

## Reverse-engineering method - BUILT

- File: results/RE_METHOD.md
- Contents: the actual step order (pin claim, split atoms, cheapest authority,
  quote and diff, smallest fix, before/after proof, revert side effects, receipt),
  what is checked first vs last, how done is distinguished from guessing, three
  recurring mistakes, and an 11-box checklist that needs no human in the loop.
- Enforcement reference: scripts/witness_loop.py, states SUPPORTED / REFUTED /
  CONTRADICTED, 10 tests in tests/test_witness_loop.py.
- Flight Recorder: results/flight_recorder/2026-11-17-re-method.jsonl

## Evidence used

- scripts/witness_loop.py:33-35 and 95-96
- mcp_config.json:94 (dangling registry path)
- barrot_capability_audit.json (122 capabilities, evidence, gaps)
- 36 tracked files rewritten by one full pytest run, measured twice

## Next action required from Sean

1. Send the rest of the spec: tools 4 and 5 in full.
2. Decide Foundry: build it, or accept NOT_IMPLEMENTED from tool 2.
3. Decide replay with no pair: return ERROR, or trigger a fresh run to create one.
