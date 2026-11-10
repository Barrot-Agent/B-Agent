from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ARTIFACTS = (
    "hover_bike_spec.json",
    "component_geometry.json",
    "assembly_guide.md",
    "bill_of_materials.md",
)


def test_generator_writes_artifacts_to_the_project_directory(tmp_path: Path) -> None:
    """The workflow runs the generator from the repository root."""
    source = (
        REPOSITORY_ROOT
        / "hover_bike_revolution"
        / "src"
        / "hover_bike_generator.py"
    )
    project_dir = tmp_path / "hover_bike_revolution"
    script_dir = project_dir / "src"
    script_dir.mkdir(parents=True)
    copied_script = script_dir / source.name
    copied_script.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    subprocess.run(
        [sys.executable, str(copied_script)],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    for artifact in EXPECTED_ARTIFACTS:
        assert (project_dir / artifact).is_file(), artifact

    assert not (project_dir / "hover_bike_revolution").exists()


def test_workflow_upload_paths_match_generator_outputs() -> None:
    workflow = (
        REPOSITORY_ROOT
        / ".github"
        / "workflows"
        / "hover_bike_updates.yml"
    ).read_text(encoding="utf-8")

    for artifact in EXPECTED_ARTIFACTS:
        assert f"hover_bike_revolution/{artifact}" in workflow
