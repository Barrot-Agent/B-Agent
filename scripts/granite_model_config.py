#!/usr/bin/env python3
"""Deprecated duplicate — import shim only.

Canonical: barrot_agent/tools/granite_model_config.py
This file was byte-identical to that module (sha256 c2fb77f9…343beaaa2).
The canonical copy is the one imported by
barrot_agent/analysis/vision_pipeline.py and
barrot_agent/orchestration/inference_provider.py.
Do not add logic here.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from barrot_agent.tools.granite_model_config import *  # noqa: F401,F403
