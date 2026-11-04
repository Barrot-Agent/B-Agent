from __future__ import annotations
import json, subprocess
from pathlib import Path
import pytest
from barrot_agent.experimentation import (
    ContinuousDiscoveryScheduler, DockerSandboxRunner, ExperimentKnowledgeRepository,
    ExperimentOrchestrator, ExperimentSpec, SandboxDiscoveryEngine, VariationGenerator,
)

def spec(**overrides):
    data = {"objective": "test objective", "hypothesis": "test hypothesis",
            "command": ("python", "-c", "print('run')"),
            "verification_command": ("python", "-c", "print('verified')"),
            "source_commit": "a" * 40}
    data.update(overrides)
    return ExperimentSpec(**data)

def test_spec_rejects_empty_commands_and_bad_limits():
    with pytest.raises(ValueError): spec(command=())
    with pytest.raises(ValueError): spec(timeout_seconds=0)
    with pytest.raises(ValueError): spec(max_variants=1000)

def test_variations_are_deterministic_and_bounded():
    dims = {"model": ["base", "alt"], "window": ["30d", "90d"],
            "features": ["price", "price+liquidity"]}
    first = VariationGenerator.generate(dims, 8)
    assert first == VariationGenerator.generate(dims, 8)
    assert len(first) <= 8
    assert first[0]["model"] == "base"
    assert len({json.dumps(x, sort_keys=True) for x in first}) == len(first)

def test_variations_empty_dimensions():
    assert VariationGenerator.generate({}) == [{}]

def test_ledger_append_verify_and_tamper_detection(tmp_path):
    ledger = ExperimentKnowledgeRepository(tmp_path)
    ledger.append({"status": "DESIGNED", "experiment_id": "x"})
    ledger.append({"status": "VERIFIED", "experiment_id": "x"})
    assert ledger.verify()["records"] == 2
    lines = ledger.path.read_text().splitlines()
    record = json.loads(lines[0]); record["payload"]["status"] = "REJECTED"
    lines[0] = json.dumps(record); ledger.path.write_text("\n".join(lines) + "\n")
    assert ledger.verify()["valid"] is False
    with pytest.raises(RuntimeError): ledger.append({"status": "DESIGNED"})

def test_discovery_detects_shell_true_and_todo(tmp_path):
    package = tmp_path / "barrot_agent"; package.mkdir()
    (package / "unsafe.py").write_text("import subprocess\nsubprocess.run('x', shell=True) # TODO\n")
    results = SandboxDiscoveryEngine(tmp_path).discover()
    assert results[0]["source_path"] == "barrot_agent/unsafe.py"
    assert "shell_true_execution" in results[0]["signals"]
    assert "unfinished_marker" in results[0]["signals"]

def test_discovery_ignores_venv_and_symlinks(tmp_path):
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "skip.py").write_text("TODO")
    secret = tmp_path / "secret.py"; secret.write_text("password = 'x'")
    (tmp_path / "linked.py").symlink_to(secret)
    assert all(".venv" not in x["source_path"] for x in SandboxDiscoveryEngine(tmp_path).discover())
    assert all(x["source_path"] != "linked.py" for x in SandboxDiscoveryEngine(tmp_path).discover())

def test_docker_runner_fails_closed_if_image_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda args, **kw:
        subprocess.CompletedProcess(args, 1, "", "missing image"))
    result = DockerSandboxRunner(tmp_path).run(spec())
    assert result.status == "REQUIRES_IMAGE"
    assert "automatic pulls are disabled" in result.reason

def test_docker_runner_enforces_network_and_privilege_limits(tmp_path, monkeypatch):
    calls = []
    def fake(args, **kw):
        calls.append(args)
        if args[1:3] == ["image", "inspect"]:
            return subprocess.CompletedProcess(args, 0, "[]", "")
        return subprocess.CompletedProcess(args, 0, "ok", "")
    monkeypatch.setattr(subprocess, "run", fake)
    (tmp_path / "source.py").write_text("x = 1")
    result = DockerSandboxRunner(tmp_path).run(spec())
    assert result.passed and result.status == "VERIFIED"
    run = calls[1]
    assert run[run.index("--network") + 1] == "none"
    assert "--read-only" in run and "--cap-drop" in run and "--security-opt" in run
    assert len([x for x in calls if x[1:3] == ["run", "--rm"]]) == 2

def test_orchestrator_records_lifecycle_and_requires_approval(tmp_path):
    from barrot_agent.experimentation import SandboxResult
    class Runner:
        def run(self, experiment, variant=None):
            return SandboxResult(True, "VERIFIED", stdout="ok", sandbox_id="s1")
    engine = ExperimentOrchestrator(tmp_path, runner=Runner())
    item = spec(); outcome = engine.execute(item, {"model": "base"})
    assert outcome["status"] == "VERIFIED"
    assert engine.knowledge.verify()["records"] == 2
    assert engine.integration_assessment(item.experiment_id)["ready"] is False
    assert engine.integration_assessment(item.experiment_id, True)["automatic_merge"] is False

def test_scheduler_persists_discovery_tick(tmp_path):
    package = tmp_path / "barrot_agent"; package.mkdir()
    (package / "example.py").write_text("def f():\n return 1 # TODO\n")
    engine = ExperimentOrchestrator(tmp_path, runner=object())
    result = ContinuousDiscoveryScheduler(engine, 5).run_once()
    assert result["status"] == "EXECUTED" and result["candidate_count"] >= 1
    assert result["ledger"]["valid"]
