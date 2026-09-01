"""Validate generated MuJoCo physics programs."""

from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET


def validate_mujoco_xml(
    source: str | Path,
) -> bool:
    """
    Validate XML structure and, when installed,
    compile it through MuJoCo.
    """

    path = Path(
        source
    ).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(
            path
        )

    root = ET.fromstring(
        path.read_text(
            encoding="utf-8",
        )
    )

    if root.tag != "mujoco":
        raise ValueError(
            "Root element must be <mujoco>."
        )

    try:
        import mujoco
    except ImportError:
        return True

    mujoco.MjModel.from_xml_path(
        str(path)
    )

    return True
