# SKILL: <skill-name>

**Name:** <skill-name>
**Version:** 0.0.0
**Status:** placeholder

## Description

<one sentence: what reality this skill proves or what action it performs.>

## Activation

- <trigger condition>

## Exclusion

- <when not to use this skill>

## Required inputs

- `<input>` — <type, format>

## Execution procedure

1. <single command or single step>
2. <single command or single step>
3. <terminal condition: stop on failure>
4. <success condition: what must be captured>

## Decision rules

- <fail condition> -> <verdict>. Stop.
- <success condition> -> <verdict>. Record evidence.

## Expected outputs

```
KEY: <value>
VERDICT: <enum>
```

## Failure/recovery

- <failure mode> -> <verdict>, <whether to retry>

## Tool dependencies

- `<binary>` — <why>

## Security

Read-only. Never write/delete/execute unverified file.

## Test references

- `tests/test_01.md` — <case>
