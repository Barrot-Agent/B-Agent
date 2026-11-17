#!/usr/bin/env python3
"""Deprecated duplicate — import shim only.

Canonical: barrot_agent/mem_palace.py
This file was byte-identical to that module (sha256 d342878c…b0e96d6).
Do not add logic here. Edit the canonical module and this shim follows.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from barrot_agent.mem_palace import *  # noqa: F401,F403
from barrot_agent.mem_palace import (  # noqa: F401
    HALLS,
    PALACE_ROOT,
    initialize_palace,
    store_memory,
)

if __name__ == "__main__":
    initialize_palace()
