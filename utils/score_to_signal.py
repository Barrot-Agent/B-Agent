"""Deprecated duplicate — import shim only.

Canonical: barrot_agent/analysis/score_to_signal.py
This file was byte-identical to that module (sha256 c152c941…61466a6ea41).

Kept because scripts/emit_signal_with_hrm.py imports the bare name
``score_to_signal`` after putting utils/ on sys.path. It also puts the repo
root on sys.path, so this shim resolves. Do not add logic here.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from barrot_agent.analysis.score_to_signal import *  # noqa: F401,F403
from barrot_agent.analysis.score_to_signal import score_to_unit  # noqa: F401
