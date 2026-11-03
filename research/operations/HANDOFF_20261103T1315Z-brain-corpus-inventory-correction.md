# Brain Corpus Inventory Correction — 2026-11-03 13:15 UTC

Current main inventory at `32d3a1ad997384db71f0f37def77deb1c19c7fad`:
- 16 entries total.
- Two generated public dumps: `dump.json`, `dump.md`.
- Fourteen other entries remain: 13 `polymath_*.json` files plus `topics.txt`.

The earlier handoff's count of 13 remaining entries was incorrect. The correct count is 14. No remaining file contents were inspected.

The expanded PR #1585 removes only the two generated dumps, disables the exporter and adds a regression test that requires all 14 unclassified entries to remain byte-for-byte untouched at the path level. It does not erase historical Git objects, forks, caches or external copies.

## Main-branch preservation incident
One handoff file was briefly created on main because a branch argument was omitted in a GitHub file-create call. It was immediately deleted in a separate commit:
- Accidental add: `817a955f39ecc39ef59ad73c91371b6ce6b8d0d6`.
- Removal: `6f0a4c34d21c6aa20c344b4b4107d2f59f7b29a1`.
- A GitHub compare from pre-incident main `32d3a1ad997384db71f0f37def77deb1c19c7fad` to current main `6f0a4c34d21c6aa20c344b4b4107d2f59f7b29a1` returned zero changed paths.
- Main file tree is restored. Commit history retains the add/revert pair. No force-push or history rewrite occurred.

PR #1585 remains draft and unmerged. Exact-head CI and fail-closed verification must pass after this correction.
