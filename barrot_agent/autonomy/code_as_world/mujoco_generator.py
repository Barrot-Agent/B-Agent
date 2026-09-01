"""Generate executable MuJoCo programs from Code-as-World worlds."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import math
import xml.etree.ElementTree as ET


@dataclass
class GeneratedPhysicsProgram:
    """A generated MuJoCo physics program."""

    source_world: str
    output_path: str
    object_count: int
    xml: str

    def to_dict(self) -> dict[str, object]:
        return {
            "source_world": self.source_world,
            "output_path": self.output_path,
            "object_count": self.object_count,
            "xml": self.xml,
        }


def _finite(value: object, default: float) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default

    return result if math.isfinite(result) else default


def _positive(value: object, default: float) -> float:
    result = _finite(value, default)
    return result if result > 0 else default


def _vector(
    raw: object,
    default: tuple[float, float, float],
) -> tuple[float, float, float]:
    if not isinstance(raw, dict):
        return default

    return (
        _finite(raw.get("x"), default[0]),
        _finite(raw.get("y"), default[1]),
        _finite(raw.get("z"), default[2]),
    )


def _text_vector(
    values: tuple[float, float, float],
) -> str:
    return " ".join(f"{value:.6g}" for value in values)


def _safe_name(value: object, fallback: str) -> str:
    text = str(value).strip()

    if not text:
        return fallback

    cleaned = []

    for character in text:
        if (
            character.isalnum()
            or character in "_-"
        ):
            cleaned.append(character)
        else:
            cleaned.append("_")

    result = "".join(cleaned).strip("_")

    return result or fallback


def _geom_size(
    size: tuple[float, float, float],
) -> tuple[float, float, float]:
    return (
        max(abs(size[0]) / 2.0, 0.001),
        max(abs(size[1]) / 2.0, 0.001),
        max(abs(size[2]) / 2.0, 0.001),
    )


def build_mujoco_xml(
    world: dict[str, object],
) -> tuple[str, int]:
    """Build a valid MuJoCo XML model from a structured world."""

    root = ET.Element(
        "mujoco",
        model="code_as_world",
    )

    ET.SubElement(
        root,
        "compiler",
        angle="radian",
        coordinate="local",
    )

    ET.SubElement(
        root,
        "option",
        timestep="0.01",
        gravity="0 0 -9.81",
    )

    asset = ET.SubElement(
        root,
        "asset",
    )

    ET.SubElement(
        asset,
        "texture",
        name="ground_texture",
        type="2d",
        builtin="checker",
        width="256",
        height="256",
    )

    ET.SubElement(
        asset,
        "material",
        name="ground_material",
        texture="ground_texture",
        texrepeat="5 5",
        reflectance="0.1",
    )

    worldbody = ET.SubElement(
        root,
        "worldbody",
    )

    ET.SubElement(
        worldbody,
        "geom",
        name="ground",
        type="plane",
        size="10 10 0.1",
        material="ground_material",
        pos="0 0 0",
    )

    states = world.get("states", [])

    if not isinstance(states, list):
        states = []

    object_count = 0
    used_names: set[str] = set()

    for state_index, state in enumerate(states):
        if not isinstance(state, dict):
            continue

        objects = state.get("objects", [])

        if not isinstance(objects, list):
            continue

        for object_index, obj in enumerate(objects):
            if not isinstance(obj, dict):
                continue

            object_count += 1

            fallback_name = (
                f"object_{state_index}_{object_index}"
            )

            name = _safe_name(
                obj.get("id"),
                fallback_name,
            )

            base_name = name
            suffix = 1

            while name in used_names:
                name = f"{base_name}_{suffix}"
                suffix += 1

            used_names.add(name)

            position = _vector(
                obj.get("position"),
                (0.0, 0.0, 0.5),
            )

            size = _vector(
                obj.get("size"),
                (1.0, 1.0, 1.0),
            )

            geom_size = _geom_size(
                size
            )

            mass = obj.get("mass")

            body = ET.SubElement(
                worldbody,
                "body",
                name=name,
                pos=_text_vector(position),
            )

            if mass is None:
                ET.SubElement(
                    body,
                    "geom",
                    name=f"{name}_geom",
                    type="box",
                    size=_text_vector(
                        geom_size
                    ),
                    density="1000",
                )
            else:
                ET.SubElement(
                    body,
                    "freejoint",
                    name=f"{name}_joint",
                )

                ET.SubElement(
                    body,
                    "geom",
                    name=f"{name}_geom",
                    type="box",
                    size=_text_vector(
                        geom_size
                    ),
                    mass=f"{_positive(mass, 1.0):.6g}",
                )

    actuator = ET.SubElement(
        root,
        "actuator",
    )

    actuator.set(
        "ctrllimited",
        "false",
    )

    xml = ET.tostring(
        root,
        encoding="unicode",
    )

    return xml, object_count


def generate_physics_program(
    world_path: str | Path,
    output_path: str | Path,
) -> GeneratedPhysicsProgram:
    """Generate and persist an executable MuJoCo XML program."""

    source = Path(
        world_path
    ).expanduser().resolve()

    if not source.exists():
        raise FileNotFoundError(
            source
        )

    raw = json.loads(
        source.read_text(
            encoding="utf-8",
        )
    )

    if not isinstance(raw, dict):
        raise ValueError(
            "World manifest must contain a JSON object."
        )

    xml, object_count = build_mujoco_xml(
        raw
    )

    output = Path(
        output_path
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        xml + "\n",
        encoding="utf-8",
    )

    return GeneratedPhysicsProgram(
        source_world=str(source),
        output_path=str(
            output.resolve()
        ),
        object_count=object_count,
        xml=xml,
    )
