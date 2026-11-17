# SKILL: debian-verify

**Name:** debian-verify
**Version:** 1.0.0
**Status:** draft

## Description

Prove whether a path exists, and if it does, return its size and SHA-256.
Reality check primitive. Used before any read, write, or claim about a file.

## Activation

- Any task that needs to know whether a file exists.
- Before any claim about a path ("it exists", "it is there", "it is ready").
- Before reading a `SKILL.md`, test file, or log referenced by another skill.

## Exclusion

- Do not use for directories (use `ls -ld` and report as DIRECTORY).
- Do not use to prove file *contents* or correctness. Existence is not validity.
- Do not use as a substitute for running a test.

## Required inputs

- `path` — absolute path to a single file.

## Execution procedure

1. ls -lh <path>
2. sha256sum <path>
3. If ls fails -> MISSING, DO NOT PROCEED
4. If ls succeeds -> EXISTS + hash + size

## Decision rules

- `ls` non-zero exit, or no output -> verdict MISSING. Stop. Do not read the path.
- `ls` zero exit -> verdict EXISTS. Record size from `ls -lh` and hash from `sha256sum`.
- `ls` succeeds but `sha256sum` fails -> verdict EXISTS_UNHASHED. Treat as unverified; do not claim truth.
- Never infer existence from a referenced path in a document.

## Expected outputs

Plain text, one verdict per path:

```
PATH: <path>
VERDICT: MISSING | EXISTS | EXISTS_UNHASHED
SIZE: <human size> | n/a
SHA256: <64 hex> | n/a
```

## Failure/recovery

- Permission denied -> verdict MISSING (unverified), report the error string verbatim.
- Path is a directory -> verdict DIRECTORY, no hash.
- Hash mismatch against a known-good hash -> verdict TAMPERED, stop, escalate.
- No retry on MISSING. A missing file is a finding, not a transient error.

## Tool dependencies

- `ls` (GNU coreutils)
- `sha256sum` (GNU coreutils)

No network. No Python. No shell builtins beyond these two binaries.

## Security

Read-only. Never write/delete/execute unverified file.

## Test references

- `tests/test_01.md` — ls on `/root/barrot/Barrot-Agent/barrot_agent/phoenix.py`, expect MISSING.
