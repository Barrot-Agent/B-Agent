## What changed

[One paragraph. What does the diff do, in plain language?]

- [Specific change one]
- [Specific change two]

## Why

Issue: [full issue URL]

[Why the issue happens and why this change fixes it. No adjectives that cannot
be checked.]

## Proof

Command: `[exact command you ran]`
Result: [exact result line, including test count and pass/fail]

## Risk and rollback

Risk: [what can break, who is affected, how you would notice]
Rollback: [the exact revert or flag that restores the previous behaviour]

## Checklist

- [ ] I reproduced the issue before changing code
- [ ] The change is limited to the issue scope
- [ ] The command above was run after the last edit
- [ ] I read the full diff
- [ ] I did not add a dependency without saying so
- [ ] I did not include generated files or secrets

<!--
Rules:
- Replace every placeholder. A leftover `TODO`, `TBD`, `FIXME`, or `<insert` is
  a reason to reject the PR. The validator checks those markers; it is not a
  general square-bracket linter.
- Do not write "guaranteed", "100%", "zero risk", "production-ready".
- If the test command did not pass, do not send the PR. Fix it or report the
  failing state honestly in the issue.
-->
