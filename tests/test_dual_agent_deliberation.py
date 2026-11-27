from pathlib import Path
import json
import subprocess

from barrot_agent.collaboration.dual_agent_deliberation import (
    AgentReport,
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


def _report(agent: str, proposed_action: str, interpretation: str, evidence_refs: list[str]) -> AgentReport:
    return AgentReport(
        agent=agent,
        status="COMPLETE",
        proposed_action=proposed_action,
        interpretation=interpretation,
        evidence_refs=evidence_refs,
    )


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
        _report("BARRETT", "use_safe_temporary_directory", "hard-coded temporary path is non-portable", ["test_barrot_agent_script.py"]),
    )

    assert d.load(case.case_id).status == "AWAITING_EXTERNAL_AGENT_INPUT"


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
            _report(agent, "use_safe_temporary_directory", "hard-coded temporary path is non-portable", ["test_barrot_agent_script.py"]),
        )

    result = d.load(case.case_id)

    assert result.status == "AGREED_AWAITING_VALIDATION"
    assert d.can_execute(case.case_id) is True

    d.record_validation(case.case_id, ["298 tests passed"], True)

    result = d.load(case.case_id)

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
        _report("BARRETT", "use_safe_temporary_directory", "hard-coded temporary path is non-portable", ["test_barrot_agent_script.py"]),
    )

    d.add_report(
        case.case_id,
        _report("CHATGPT", "leave_existing_path", "path is acceptable", ["none"]),
    )

    result = d.load(case.case_id)

    assert result.status == "DISPUTED"
    assert d.can_execute(case.case_id) is False



def test_changing_either_report_invalidates_prior_validation(tmp_path):
    repo_root = tmp_path / "repo"
    commit = _init_git_repo(repo_root)
    d = DualAgentDeliberation(storage_root=tmp_path / "records")

    for changed_agent in ("BARRETT", "CHATGPT"):
        case_id = f"case_changed_{changed_agent.lower()}"
        case = d.create_case(
            case_id=case_id,
            repo_root=repo_root,
            ref="main",
            commit=commit,
        )
        for agent in ("BARRETT", "CHATGPT"):
            d.add_report(
                case.case_id,
                _report(
                    agent,
                    "retain_existing_behavior",
                    "the existing behavior is correct",
                    [f"{agent.lower()}-evidence"],
                ),
            )

        d.record_validation(case.case_id, ["previous validation passed"], True)
        assert d.load(case.case_id).status == "VALIDATED"

        d.add_report(
            case.case_id,
            _report(
                changed_agent,
                "change_behavior",
                "the existing behavior needs correction",
                [f"{changed_agent.lower()}-updated-evidence"],
            ),
        )

        result = d.load(case.case_id)
        assert result.status == "DISPUTED"
        assert result.validation_evidence == []
        assert result.final_decision == ""
        assert result.proposed_resolution == ""
        assert result.disputed_claims == ["proposed_action", "interpretation"]
        assert d.can_execute(case.case_id) is False


def test_import_preserves_independent_as_report_claim_not_proof(tmp_path):
    repo_root = tmp_path / "repo"
    commit = _init_git_repo(repo_root)
    d = DualAgentDeliberation(storage_root=tmp_path / "records")
    case = d.create_case(
        case_id="case_independence_claim",
        repo_root=repo_root,
        ref="main",
        commit=commit,
    )
    d.add_report(
        case.case_id,
        _report(
            "BARRETT",
            "same_action",
            "same_interpretation",
            ["barrett-evidence"],
        ),
    )

    packet = {
        "agent": "CHATGPT",
        "case_id": case.case_id,
        "chatgpt_report": {
            "status": "COMPLETE",
            "proposed_action": "same_action",
            "interpretation": "same_interpretation",
            "independent": False,
        },
    }
    packet_path = tmp_path / "chatgpt_packet.json"
    packet_path.write_text(json.dumps(packet), encoding="utf-8")

    result = d.import_chatgpt_packet(case.case_id, packet_path)
    assert result.chatgpt["independent"] is False
    # Agreement is still only agreement; this flag is not independent proof.
    assert result.status == "AGREED_AWAITING_VALIDATION"
    assert result.validation_evidence == []
