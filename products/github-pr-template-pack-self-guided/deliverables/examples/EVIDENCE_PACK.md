# Evidence pack - issue-42

Generated: 2026-11-18T06:38:21.727147Z
Issue: https://github.com/example/project/issues/42
Commit: uncommitted (example)
Environment: Python 3.13.5, Linux, no third-party test dependencies

## Command

```
python3 -m unittest discover -s tests
```

Exit code: 0

## Output

```
Ran 76 tests in 0.095s

OK
```

## Claims

### The ledger rejects an issue with no stated amount.

- Evidence: tests/test_ledger.py::test_missing_amount_is_no_go
- Limit: Only the parseable-amount path is covered; amounts inside images are not read.

### The timebox refuses an out-of-order checkpoint.

- Evidence: tests/test_timebox.py::test_out_of_order_checkpoint_rejected
- Limit: Ordering is enforced; wall-clock honesty depends on the operator.
