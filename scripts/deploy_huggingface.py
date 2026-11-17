#!/usr/bin/env python3
"""Deprecated duplicate — CLI delegate only.

Canonical: barrot_agent/orchestration/deploy_huggingface.py
This file was byte-identical to that module (sha256 ab5df664…f697cc2517d).
It is a CLI: running it still deploys, because __main__ delegates to the
canonical main(). Do not add logic here.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from barrot_agent.orchestration.deploy_huggingface import *  # noqa: F401,F403
from barrot_agent.orchestration.deploy_huggingface import main  # noqa: F401

if __name__ == "__main__":
    raise SystemExit(main())
