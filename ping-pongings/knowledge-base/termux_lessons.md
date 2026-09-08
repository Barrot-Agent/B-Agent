# Termux Execution Lessons


## 2026-09-08 05:08 UTC
- Always verify that the validation test covers the same conditions that later repairs address; the repeated pattern of 'initial implementation → validation test → Barrot repair' suggests missing pre‑checks in the validation step.
- Add an explicit existence or state check before any repair command (e.g., Barrot repair, derived repair) to avoid redundant repairs when the code is already correct.
- Make repair commands idempotent and safe to run multiple times; the history shows several consecutive repair cycles, indicating that current repairs may not guarantee a clean state after the first run.
- Introduce a pre‑execution guard that skips the 'initial implementation' step if a previous successful implementation is detected, reducing unnecessary re‑implementation cycles.
- Separate derived code paths from base implementations with their own validation suite; the appearance of 'derived repair' after multiple base cycles points to a gap in testing derived logic early enough.
- Log and assert the presence of required files or directories before executing repository‑wide tasks; missing checks can lead to silent failures that only surface during later repair steps.
- Avoid running generic 'Barrot repair' after every validation test; instead, conditionally trigger specific repairs only when targeted checks (e.g., syntax, type, or runtime) actually fail.
