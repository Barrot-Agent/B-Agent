"""Recovery KPI must be measured, not asserted."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.restore_drill import drill


def test_restore_is_lossless():
    result = drill(files=40)
    assert result["files"] == 40
    assert result["files_lost_or_changed"] == 0
    assert result["data_loss_free"] is True
    assert result["restore_seconds"] >= 0
