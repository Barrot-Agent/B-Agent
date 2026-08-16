from scripts.convergence_research import normalize_math_status, rank_repository, validate_math_status


def test_math_status_is_normalized_without_collapsing_solved_into_open():
    assert normalize_math_status("**SOLVED** (2003)") == "solved"
    assert normalize_math_status("Official Status: Open") == "open"
    assert normalize_math_status("unverified claim") == "speculative"


def test_solved_problem_is_marked_historical():
    findings = validate_math_status(
        {"problems": [{"name": "Poincare", "official_status": "**SOLVED** (2003)"}]}
    )
    assert findings[0]["status"] == "solved"
    assert findings[0]["warning"]


def test_repository_rank_includes_internal_targets_and_approval_gate():
    result = rank_repository(
        {
            "full_name": "example/project",
            "domain": "memory",
            "keywords": ["memory", "retrieval"],
            "integration_targets": ["data/registry.py"],
        },
        {
            "html_url": "https://github.com/example/project",
            "description": "memory retrieval",
            "stars": 50000,
            "forks": 100,
            "archived": False,
            "updated_at": "2026-08-01T00:00:00Z",
        },
        "data/registry.py ping-pongings/knowledge-base",
    )
    assert result["impact_score"] > 0
    assert result["approval_required"] is True
    assert result["integration_targets"] == ["data/registry.py"]
