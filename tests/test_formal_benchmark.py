from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from barrot_agent.research import (
    ANTHROPIC_FLT_IMPORT_CONFIG,
    ExternalLeanProjectImporter,
    FormalVerificationStatus,
    LeanVerificationGateway,
)

SCRIPT_PATH = Path("/home/runner/work/B-Agent/B-Agent/scripts/run_formal_verification_benchmark.py")


def load_script_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def create_external_project(root: Path) -> Path:
    (root / "Theorems").mkdir(parents=True)
    (root / "Definitions").mkdir(parents=True)
    (root / "P2M" / "Sol").mkdir(parents=True)
    (root / "verification" / "comparator").mkdir(parents=True)
    (root / "verification" / "nanoda").mkdir(parents=True)
    (root / "lean-toolchain").write_text("leanprover/lean4:v4.33.1\n", encoding="utf-8")
    (root / "lake-manifest.json").write_text(
        json.dumps(
            {
                "version": "1.2.0",
                "packages": [
                    {
                        "name": "mathlib",
                        "url": "https://github.com/leanprover-community/mathlib4.git",
                        "rev": "db584cd6d46c92f209a44c0f1c829460d327499d",
                        "inputRev": "db584cd6d46c92f209a44c0f1c829460d327499d",
                        "scope": "",
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / "formalization.yaml").write_text('project:\n  name: "Fermat"\n  license: "Apache-2.0"\n', encoding="utf-8")
    (root / "PROOF-PATH.md").write_text(
        "**1. Reduction to a prime p ≥ 5.** `Step.one` derives the prime case.\n\n"
        "**2. Frey package.** `Step.two` depends on `proof-step-3`.\n\n"
        "**3. Irreducibility.** `Step.three` closes the contradiction.\n",
        encoding="utf-8",
    )
    (root / "FinalCheck.lean").write_text(
        "import Theorems.Thm_fermat_last_theorem\n"
        "/-- info: 'fermat_last_theorem' depends on axioms: [propext, Classical.choice, Quot.sound] -/\n"
        "#guard_msgs in\n#print axioms fermat_last_theorem\n\n"
        "theorem flt_mathlib : FermatLastTheorem := by\n"
        "  intro n hn a b c ha hb hc\n"
        "  exact fermat_last_theorem n hn a b c (Nat.pos_of_ne_zero ha) (Nat.pos_of_ne_zero hb) (Nat.pos_of_ne_zero hc)\n",
        encoding="utf-8",
    )
    (root / "Theorems" / "Thm_fermat_last_theorem.lean").write_text(
        "import Mathlib.NumberTheory.FLT.Basic\n\n"
        "theorem fermat_last_theorem (n : ℕ) (hn : 3 ≤ n) (a b c : ℕ) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) :\n"
        "    a ^ n + b ^ n ≠ c ^ n := by\n"
        "  exact by\n"
        "    simp\n",
        encoding="utf-8",
    )
    (root / "lakefile.lean").write_text(
        """import Lake\nopen Lake DSL\n\npackage flt_e2e where\n  leanOptions := #[\n    ⟨`autoImplicit, false⟩,\n    ⟨`maxHeartbeats, (4000000 : Nat)⟩\n  ]\n\nrequire mathlib from git \"https://github.com/leanprover-community/mathlib4.git\" @ \"db584cd6d46c92f209a44c0f1c829460d327499d\"\n""",
        encoding="utf-8",
    )
    (root / "verification" / "comparator" / "config.json").write_text(
        json.dumps(
            {
                "theorem_names": ["FLT_for_comparator", "FLT_mathlib_for_comparator"],
                "permitted_axioms": ["propext", "Quot.sound", "Classical.choice"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / "verification" / "nanoda" / "nanoda-config.json").write_text(
        json.dumps(
            {
                "pp_declars": ["fermat_last_theorem", "FermatLastTheorem"],
                "permitted_axioms": ["propext", "Classical.choice", "Quot.sound"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / "verification" / "comparator" / "run.sh").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    (root / "verification" / "nanoda" / "run.sh").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    return root


def test_external_importer_builds_flt_bundle(tmp_path: Path) -> None:
    project_root = create_external_project(tmp_path / "external")
    importer = ExternalLeanProjectImporter()

    bundle = importer.build_bundle(project_root, ANTHROPIC_FLT_IMPORT_CONFIG)
    formal = bundle["formal_verification"][0]

    assert formal["status"] == FormalVerificationStatus.IMPORTED.value
    assert formal["provenance"][0] == "EXTERNAL_AI_FORMALIZATION"
    assert formal["root_theorem"] == "fermat_last_theorem"
    assert formal["theorem_statement"].startswith("theorem fermat_last_theorem")
    assert formal["mathlib_version"] == "db584cd6d46c92f209a44c0f1c829460d327499d"
    assert formal["axiom_result"]["declared_axioms"] == ["propext", "Classical.choice", "Quot.sound"]
    assert formal["comparator_result"]["statement_alignment"]["equivalent"] is True
    assert bundle["claims"][0]["claim_id"] == "claim.fermat_last_theorem"
    assert bundle["claims"][0]["dependencies"]


def test_gateway_records_staged_formal_verification(tmp_path: Path) -> None:
    project_root = create_external_project(tmp_path / "external")
    formal = ExternalLeanProjectImporter().build_bundle(project_root, ANTHROPIC_FLT_IMPORT_CONFIG)["formal_verification"][0]
    formal["repository_path"] = str(project_root)
    gateway = LeanVerificationGateway()

    def runner(command: list[str], repository_path: str | None) -> dict[str, object]:
        joined = " ".join(command)
        if joined == "lake build":
            return {"returncode": 0, "stdout": "Build completed successfully", "stderr": ""}
        if joined == "lake env lean FinalCheck.lean":
            return {
                "returncode": 0,
                "stdout": "'fermat_last_theorem' depends on axioms: [propext, Classical.choice, Quot.sound]",
                "stderr": "",
            }
        if joined == "bash verification/comparator/run.sh":
            return {"returncode": 0, "stdout": "Your solution is okay!", "stderr": ""}
        if joined == "bash verification/nanoda/run.sh":
            return {"returncode": 0, "stdout": "Checked 1052234 declarations with no errors", "stderr": ""}
        raise AssertionError(f"unexpected command: {command} @ {repository_path}")

    record = gateway.verify(formal, runner=runner)

    assert record.compiled is True
    assert record.independently_verified is True
    assert record.status == FormalVerificationStatus.INDEPENDENTLY_CHECKED.value
    assert record.status_history == [
        FormalVerificationStatus.IMPORTED.value,
        FormalVerificationStatus.BUILD_ATTEMPTED.value,
        FormalVerificationStatus.COMPILED.value,
        FormalVerificationStatus.KERNEL_VERIFIED.value,
        FormalVerificationStatus.COMPARATOR_VERIFIED.value,
        FormalVerificationStatus.INDEPENDENTLY_CHECKED.value,
    ]
    assert record.axiom_result["declared_axioms"] == ["propext", "Classical.choice", "Quot.sound"]
    assert record.comparator_result["verdict"] == "verified"
    assert record.independent_checker_result["success"] is True


def test_gateway_unavailable_lake_stays_at_build_attempted(tmp_path: Path, monkeypatch) -> None:
    project_root = create_external_project(tmp_path / "external")
    formal = ExternalLeanProjectImporter().build_bundle(project_root, ANTHROPIC_FLT_IMPORT_CONFIG)["formal_verification"][0]
    formal["repository_path"] = str(project_root)
    monkeypatch.setenv("PATH", "")

    record = LeanVerificationGateway().verify(formal)

    assert record.compiled is False
    assert record.independently_verified is False
    assert record.returncode == 127
    assert record.status == FormalVerificationStatus.BUILD_ATTEMPTED.value
    assert record.status_history == [
        FormalVerificationStatus.IMPORTED.value,
        FormalVerificationStatus.BUILD_ATTEMPTED.value,
    ]
    assert "No such file or directory" in record.build_result["stderr"]


def test_formal_benchmark_script_materializes_import_only_report(tmp_path: Path, monkeypatch) -> None:
    project_root = create_external_project(tmp_path / "external")
    bundle_out = tmp_path / "bundle.json"
    report_out = tmp_path / "report.json"
    module = load_script_module("run_formal_benchmark_test")
    monkeypatch.setattr(sys, "argv", [
        str(SCRIPT_PATH),
        "--workspace",
        str(tmp_path),
        "--project-root",
        str(project_root),
        "--bundle-out",
        str(bundle_out),
        "--report-out",
        str(report_out),
    ])

    module.main()

    report = json.loads(report_out.read_text(encoding="utf-8"))
    assert bundle_out.exists()
    assert report["formal_verifications"][0]["status"] == FormalVerificationStatus.IMPORTED.value
    assert report["status"] == "no_solution_claim"
