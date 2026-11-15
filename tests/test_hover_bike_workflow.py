from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = REPOSITORY_ROOT / ".github" / "workflows" / "hover_bike_updates.yml"
GENERATOR_PATH = REPOSITORY_ROOT / "hover_bike_revolution" / "src" / "hover_bike_generator.py"
ASSEMBLY_GUIDE_PATH = (
    REPOSITORY_ROOT / "hover_bike_revolution" / "src" / "assembly_guide_generator.py"
)


def _step_block(workflow: str, heading: str) -> str:
    start = workflow.index(f"      - name: {heading}")
    next_step = workflow.find("\n      - name:", start + 1)
    return workflow[start:] if next_step < 0 else workflow[start:next_step]


def test_hover_bike_generator_runs_from_repository_root_and_matches_artifact_paths():
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    generator_step = _step_block(
        workflow, "Generate hover bike design artefacts from repository root"
    )
    generator_source = GENERATOR_PATH.read_text(encoding="utf-8")

    assert "working-directory:" not in generator_step
    assert "python hover_bike_revolution/src/hover_bike_generator.py" in generator_step
    assert 'output_dir: Path | str = Path("hover_bike_revolution")' in generator_source
    assert 'path = self.output_dir / "hover_bike_spec.json"' in generator_source
    assert 'path = self.output_dir / "component_geometry.json"' in generator_source
    assert 'path = self.output_dir / "assembly_guide.md"' in generator_source
    assert 'path = self.output_dir / "bill_of_materials.md"' in generator_source
    for artifact in (
        "hover_bike_revolution/hover_bike_spec.json",
        "hover_bike_revolution/component_geometry.json",
        "hover_bike_revolution/assembly_guide.md",
        "hover_bike_revolution/bill_of_materials.md",
    ):
        assert artifact in workflow


def test_hover_bike_documentation_generator_runs_from_repository_root():
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    documentation_step = _step_block(
        workflow, "Generate documentation from repository root"
    )
    generator_source = ASSEMBLY_GUIDE_PATH.read_text(encoding="utf-8")

    assert "working-directory:" not in documentation_step
    assert "python hover_bike_revolution/src/assembly_guide_generator.py" in documentation_step
    assert 'output_dir: Path | str = Path("hover_bike_revolution/docs")' in generator_source
