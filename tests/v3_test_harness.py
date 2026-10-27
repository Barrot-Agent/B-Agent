from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from barrot_agent.orchestration.repository_repair import RepairCycleEvidence, RepositoryRepairController


class FakeBrain:
    def __init__(self, *responses: object):
        self._responses = list(responses)
        self.calls = 0

    def think(self, message: str, history=None, system=None) -> str:
        del message, history, system
        index = self.calls if self.calls < len(self._responses) else len(self._responses) - 1
        response = self._responses[index]
        self.calls += 1
        if isinstance(response, Exception):
            raise response
        return str(response)


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)


def init_repo(tmp_path: Path, *, origin: bool = False, gitlab: bool = False) -> tuple[Path, str]:
    workspace = tmp_path / "repo"
    workspace.mkdir(parents=True)
    (workspace / "barrot_agent").mkdir()
    (workspace / "scripts").mkdir()
    (workspace / "barrot_agent" / "__init__.py").write_text("", encoding="utf-8")
    (workspace / "scripts" / "__init__.py").write_text("", encoding="utf-8")
    (workspace / ".gitignore").write_text("__pycache__/\n*.pyc\n", encoding="utf-8")
    target = workspace / "barrot_agent" / "target.py"
    target.write_text('FLAG = "BROKEN"\n', encoding="utf-8")

    assert git(workspace, "init", "-b", "main").returncode == 0
    assert git(workspace, "config", "user.email", "test@example.com").returncode == 0
    assert git(workspace, "config", "user.name", "Test User").returncode == 0
    assert git(workspace, "add", ".").returncode == 0
    assert git(workspace, "commit", "-m", "initial").returncode == 0
    assert git(workspace, "checkout", "-b", "repair/test").returncode == 0

    if origin:
        remote = tmp_path / "origin.git"
        assert git(tmp_path, "init", "--bare", str(remote)).returncode == 0
        assert git(workspace, "remote", "add", "origin", str(remote)).returncode == 0
    if gitlab:
        remote = tmp_path / "gitlab.git"
        assert git(tmp_path, "init", "--bare", str(remote)).returncode == 0
        assert git(workspace, "remote", "add", "gitlab", str(remote)).returncode == 0

    return workspace, "barrot_agent/target.py"


def defect_command(path: str, token: str = "BROKEN", *, timeout: int = 5) -> dict[str, object]:
    code = (
        "from pathlib import Path; import sys; "
        f"text = Path({path!r}).read_text(); "
        f"sys.exit(1 if {token!r} in text else 0)"
    )
    return {"program": sys.executable, "args": ["-c", code], "timeout": timeout}


def success_command(*, timeout: int = 5) -> dict[str, object]:
    return {"program": sys.executable, "args": ["-c", "import sys; sys.exit(0)"], "timeout": timeout}


def failure_command(*, timeout: int = 5) -> dict[str, object]:
    return {"program": sys.executable, "args": ["-c", "import sys; sys.exit(1)"], "timeout": timeout}


def timeout_command(*, timeout: int = 1) -> dict[str, object]:
    return {"program": sys.executable, "args": ["-c", "import time; time.sleep(2)"], "timeout": timeout}


def repair_payload(
    path: str,
    *,
    old: str = 'FLAG = "BROKEN"',
    new: str = 'FLAG = "FIXED"',
    reproduction_commands: list[dict[str, object]] | None = None,
    validation_commands: list[dict[str, object]] | None = None,
    resolution_commands: list[dict[str, object]] | None = None,
    expected_files: list[str] | None = None,
    mode: str = "repair",
) -> str:
    payload = {
        "mode": mode,
        "report": "",
        "issue": {
            "summary": "target file remains broken",
            "evidence": [f"{path} contains the BROKEN marker"],
            "files": [path],
            "reproduction_commands": reproduction_commands or [defect_command(path)],
            "validation_commands": validation_commands or [defect_command(path)],
            "resolution_commands": resolution_commands or [defect_command(path)],
        },
        "repair_plan": {
            "summary": "Replace the BROKEN marker with FIXED",
            "reason": "The reproduced defect is the BROKEN marker in the target file.",
        },
        "changeset": {
            "operations": [
                {
                    "type": "replace",
                    "path": path,
                    "old": old,
                    "new": new,
                    "reason": "Swap the broken marker for the fixed marker.",
                }
            ],
            "expected_files": expected_files or [path],
            "commit_message": "Fix broken target marker",
        },
    }
    return json.dumps(payload)


def make_controller(workspace: Path, brain: FakeBrain) -> RepositoryRepairController:
    return RepositoryRepairController(brain=brain, workspace=workspace, planner_attempts=3)


def run_cycle(workspace: Path, brain: FakeBrain) -> RepairCycleEvidence:
    controller = make_controller(workspace, brain)
    return controller.run(
        task_title="Repair target",
        task_body="Fix the reproduced defect in barrot_agent/target.py",
        issue_number="123",
        repo="Barrot-Agent/B-Agent",
        branch="repair/test",
        audit_context={"inventory": "barrot_agent/target.py"},
    )


def write_science_bundle(
    path: Path,
    *,
    independent: bool,
    adversarial_status: str,
    formal_command: list[str] | None = None,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    bundle = {
        "problem": {
            "problem_id": "generic_problem",
            "title": "Generic research problem",
            "domain": "math",
            "primary_question": "Is the claim established?",
            "primary_claims": ["claim.main"],
            "related_problems": [],
            "acceptance_requirements": {
                "formal_verification_required": True,
                "independent_verification_required": True,
                "resolved_adversarial_reviews_required": True,
            },
        },
        "sources": [
            {
                "source_id": "paper",
                "title": "Primary paper",
                "author_or_organization": "Author",
                "source_type": "paper",
                "url": "https://example.invalid/paper",
            },
            {
                "source_id": "formal_repo",
                "title": "Formal repo",
                "author_or_organization": "Author",
                "source_type": "formal_repo",
                "url": "https://example.invalid/repo",
                "source_commit": "abc123",
            },
            {
                "source_id": "independent_check",
                "title": "Independent verification",
                "author_or_organization": "Independent team",
                "source_type": "independent_report",
                "url": "https://example.invalid/check",
            },
        ],
        "claims": [
            {
                "claim_id": "claim.main",
                "statement": "Main theorem statement.",
                "domain": "math",
                "claim_type": "theorem",
                "source": "paper",
                "source_location": "section 1",
                "assumptions": ["A1", "A2"],
                "provenance": ["paper"],
            }
        ],
        "evidence": [
            {
                "evidence_id": "paper-support",
                "claim_id": "claim.main",
                "kind": "theorem",
                "summary": "Primary paper states theorem.",
                "source_id": "paper",
                "source_location": "section 1",
                "status": "SUPPORTED",
                "independence": "same_source_confirmation",
                "provenance": ["paper"],
                "details": {"ancestry": "lineage-paper"},
            },
            {
                "evidence_id": "independent-support",
                "claim_id": "claim.main",
                "kind": "independent_verification",
                "summary": "Independent team checked theorem.",
                "source_id": "independent_check",
                "source_location": "section 2",
                "status": "INDEPENDENTLY_VERIFIED",
                "independence": "independent_mathematical_derivation" if independent else "same_source_confirmation",
                "provenance": ["independent_check"],
                "details": {"ancestry": "independent-lineage" if independent else "lineage-paper"},
            },
        ],
        "tracks": [
            {
                "track_id": "proof",
                "role": "proof_construction",
                "strategy": "constructive proof",
                "hypothesis": "claim should hold",
                "assumptions": ["A1"],
                "dependencies": [],
                "focus_claims": ["claim.main"],
                "intermediate_results": [{"claim_id": "claim.main", "summary": "constructed argument", "status": "SUPPORTED"}],
                "evidence": ["paper-support"],
                "provenance": ["paper"],
                "confidence": 0.7,
            },
            {
                "track_id": "formal",
                "role": "formalization",
                "strategy": "formal proof",
                "hypothesis": "formalization should compile",
                "dependencies": ["claim.main"],
                "focus_claims": ["claim.formal"],
                "intermediate_results": [{"claim_id": "claim.main", "summary": "formal theorem registered", "status": "FORMALIZED"}],
                "provenance": ["formal_repo"],
                "confidence": 0.8,
            },
        ],
        "adversarial_reviews": [
            {
                "review_id": "adv-1",
                "claim_id": "claim.main",
                "objections": ["Check missing assumption"],
                "responses": ["Addressed"] if adversarial_status == "SUPPORTED" else [],
                "status": adversarial_status,
                "provenance": ["adversarial"],
            }
        ],
        "formal_verification": [
            {
                "verification_id": "formal-1",
                "system": "lean",
                "claim_ids": ["claim.main"],
                "theorem_names": ["main_theorem"],
                "source_files": ["Main.lean"],
                "repository": "https://example.invalid/repo",
                "repository_path": None,
                "source_commit": "abc123",
                "toolchain_version": "lean4",
                "command": formal_command or ["lake", "build"],
                "dependencies": ["Mathlib"],
            }
        ],
        "question_map": [],
    }
    path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    return path
