#!/usr/bin/env python3
"""Retired legacy Termux upgrade bundle.

This script wrote files directly into ~/barrot and embedded unvalidated
XRP BUY/SELL heuristics. It is intentionally disabled. Use the controlled
Barrot V3 bundle workflow after its explicit authorization and verification
gates; do not execute this legacy installer.
"""
import json

STATUS = {
    "status": "QUARANTINED",
    "files_written": False,
    "external_actions_performed": False,
    "reason_code": "LEGACY_TERMUX_INSTALLER_RETIRED",
    "message": "No files were written. Use the controlled Barrot V3 bundle workflow.",
}


def main():
    print(json.dumps(STATUS, sort_keys=True))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
