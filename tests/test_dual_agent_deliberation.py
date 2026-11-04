from pathlib import Path
import subprocess

from barrot_agent.collaboration.dual_agent_deliberation import (
    DualAgentDeliberation,
)


def _init_git_repo(root: Path) -> str:
    root.mkdir(parents=True, exist_ok=True)
    def run(*args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    run("init", "-b", "main")
    run("config", "user.email", "barrot-tests@example.com")
    run("config", "user.name", "Barrot Test Fixture")
    (root / "README.md").write_text("deliberation fixture\\n", encoding="utf-8")
    run("add", "README.md")
    run("commit", "-m", "initialize deliberation fixture")
    return run("rev-parse", "HEAD")


def test_dual_agent_requires_both_independent_reports(tmp_path):
    repo_root = tmp_path / "repo"
    commit = _init_git_repo(repo_root)
    d = DualAgentDeliberation(storage_root=tmp_path / "records")

    case = d.create_case(
        case_id="case_tmp_comment_path",
        issue="Hard-coded /tmp comment body path fails on Termux",
        repo_root=repo_root,
        ref="main",
        commit=commit,
    )

    d.add_report(
        case.case_id,
        agent="BARRETT",
        proposed_action="use_safe_temporary_directory",
        interpretation="hard-coded temporary path is non-portable",
        evidence_refs=["test_barrot_agent_script.py"],
    )

    assert d.get_case(case.case_id).status == "AWAITING_EXTERNAL_AGENT_INPUT"


def test_agreement_does_not_equal_verification(tmp_path):
    repo_root = tmp_path / "repo"
    commit = _init_git_repo(repo_root)
    d = DualAgentDeliberation(storage_root=tmp_path / "records")

    case = d.create_case(
        case_id="case_agreement",
        issue="Temporary file portability",
        repo_root=repo_root,
        ref="main",
        commit=commit,
    )

    for agent in ("BARRETT", "CHATGPT"):
        d.add_report(
            case.case_id,
            agent=agent,
            proposed_action="use_safe_temporary_directory",
            interpretation="hard-coded temporary path is non-portable",
            evidence_refs=["test_barrot_agent_script.py"],
        )

    result = d.get_case(case.case_id)

    assert result.status == "AGREED_AWAITING_VALIDATION"
    assert d.can_execute(case.case_id) is True

    d.record_validation(
        case.case_id,
        success=True,
        evidence_refs=["298 tests passed"],
    )

    result = d.get_case(case.case_id)

    assert result.status == "VALIDATED"


def test_disagreement_blocks_execution(tmp_path):
    repo_root = tmp_path / "repo"
    commit = _init_git_repo(repo_root)
    d = DualAgentDeliberation(storage_root=tmp_path / "records")

    case = d.create_case(
        case_id="case_disputed",
        issue="Temporary file portability",
        repo_root=repo_root,
        ref="main",
        commit=commit,
    )

    d.add_report(
        case.case_id,
        agent="BARRETT",
        proposed_action="use_safe_temporary_directory",
        interpretation="hard-coded temporary path is non-portable",
        evidence_refs=["test_barrot_agent_script.py"],
    )

    d.add_report(
        case.case_id,
        agent="CHATGPT",
        proposed_action="leave_existing_path",
        interpretation="path is acceptable",
        evidence_refs=["none"],
    )

    result = d.get_case(case.case_id)

    assert result.status == "DISPUTED"
    assert d.can_execute(case.case_id) is False
