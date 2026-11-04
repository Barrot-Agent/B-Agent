#!/usr/bin/env python3
"""Disabled public brain-corpus exporter.

The historical script queried the full non-error workspace.barrot.brain table
and wrote timestamp/topic/insight/session records into the public repository.
It is intentionally inert until data classification, authorization, redaction,
and a non-public storage destination are approved.
"""


def main() -> int:
    print("DISABLED: public brain-corpus export is not authorized.")
    print("No Databricks credentials were read, no query was run, no files were written, and no repository push occurred.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
