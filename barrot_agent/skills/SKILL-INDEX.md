# SKILL-INDEX

Single source of truth for B-ACES Transmuted v1.1 skills.
Law: NO FILE = NO SKILL. NO TEST = NO CLAIM. NO HASH = NO TRUTH.

| skill name | version | status | test result | hash |
|---|---|---|---|---|
| debian-verify | 1.0.0 | draft | test_01 FAIL (premise false: path EXISTS, skill behaved correctly) | a002e66e9a47bd09c9ad7803cc0e221936e69d777b7a436b0d8834dafd5a7186 |
| _template | 0.0.0 | placeholder | n/a (no test, not a skill) | see files/ |

Hash = SHA-256 of `skills/<name>/SKILL.md`.

## Rules

- A skill enters this table only after its directory, `SKILL.md`, `metadata.json`,
  `CHANGELOG.md`, and `tests/test_01.md` all exist on disk.
- Status `draft` = files exist, test executed, result recorded verbatim.
- Status `verified` = at least one test PASS.
- No entry may claim `verified` without a listed test result.
