# CHANGELOG — debian-verify

## v1.0.0 — 2026-11-16

- Created. First living skill of B-ACES Transmuted v1.1.
- Procedure: `ls -lh` then `sha256sum`; MISSING is terminal, EXISTS requires hash.
- Security: read-only, never write/delete/execute unverified file.
- Test: `tests/test_01.md` (1 real case).
