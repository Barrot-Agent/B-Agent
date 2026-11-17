#!/usr/bin/env python3
"""Restore drill: destroy a tree, restore it, prove nothing was lost.

Measures the Phoenix recovery KPI with a real tar round trip: seconds to restore
and the number of files whose sha256 changed. Clause: this drills files, not a
running service.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tarfile
import tempfile
import time
from pathlib import Path


def tree_hashes(root: Path) -> dict[str, str]:
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def drill(files: int = 200) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        live = base / "live"
        live.mkdir()
        for i in range(files):
            (live / f"f{i:03d}.txt").write_text(f"payload {i}\n" * 20)
        before = tree_hashes(live)
        archive = base / "backup.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(live, arcname="live")
        shutil.rmtree(live)
        started = time.perf_counter()
        with tarfile.open(archive) as tar:
            tar.extractall(base, filter="data")
        seconds = round(time.perf_counter() - started, 3)
        after = tree_hashes(live)
        lost = sum(1 for name, digest in before.items() if after.get(name) != digest)
        return {
            "files": files,
            "restore_seconds": seconds,
            "files_lost_or_changed": lost,
            "data_loss_free": lost == 0 and after == before,
        }


if __name__ == "__main__":
    result = drill()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["data_loss_free"] else 1)
