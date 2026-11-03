import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _load_kaggle_script(monkeypatch, relative_path="scripts/kaggle_competitions_automation.py"):
    # The safety tests exercise the pre-authentication guard only; keep the
    # optional Kaggle/pandas/sklearn runtime dependencies stubbed and offline.
    import sys
    import types

    def stub(name, **attributes):
        module = types.ModuleType(name)
        module.__dict__.update(attributes)
        module.__path__ = []
        monkeypatch.setitem(sys.modules, name, module)
        return module

    stub("pandas")
    stub("kaggle")
    stub("kaggle.api")
    stub("kaggle.api.kaggle_api_extended", KaggleApiExtended=type("KaggleApiExtended", (), {}))
    stub("sklearn")
    stub("sklearn.dummy", DummyClassifier=type("DummyClassifier", (), {}), DummyRegressor=type("DummyRegressor", (), {}))
    stub("sklearn.preprocessing", LabelEncoder=type("LabelEncoder", (), {}))

    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location("kaggle_submission_guard_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_databricks_token_rotation_accepts_no_token_and_has_no_secret_write():
    workflow = (ROOT / ".github" / "workflows" / "rotate-databricks-token.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch" in workflow
    assert "permissions: {}" in workflow
    assert "inputs:" not in workflow
    assert "new_token" not in workflow
    assert "secrets." not in workflow
    assert "gh secret set" not in workflow
    assert "gh workflow run" not in workflow
    assert "ROTATION_NOT_PERFORMED" in workflow


def test_force_deploy_space_is_inert_and_cannot_force_push():
    workflow = (ROOT / ".github" / "workflows" / "force-deploy-space.yml").read_text(encoding="utf-8")
    assert "permissions: {}" in workflow
    assert "if: false" in workflow
    assert "workflow_dispatch" in workflow
    assert "HF_TOKEN" not in workflow
    assert "git push -f" not in workflow
    assert "huggingface.co/spaces" not in workflow
    assert "actions/checkout" not in workflow


def test_kaggle_workflow_is_manual_and_explicitly_gated():
    workflow = (ROOT / ".github" / "workflows" / "kaggle-competitions.yml").read_text(encoding="utf-8")
    assert "schedule:" not in workflow
    assert "workflow_dispatch:" in workflow
    assert "allow_submission:" in workflow
    assert "competition_allowlist:" in workflow
    assert "KAGGLE_COMPETITION_ALLOWLIST:" in workflow
    assert "type: boolean" in workflow
    assert "default: false" in workflow
    assert "inputs.allow_submission == true" in workflow
    assert "KAGGLE_ALLOW_SUBMISSIONS:" in workflow
    assert "persist-credentials: false" in workflow
    assert "python scripts/kaggle_competitions_automation.py" in workflow
    assert "python kaggle_competitions_automation.py" not in workflow


def test_kaggle_script_blocks_api_authentication_before_any_api_call(monkeypatch):
    module = _load_kaggle_script(monkeypatch)
    monkeypatch.delenv("KAGGLE_ALLOW_SUBMISSIONS", raising=False)
    monkeypatch.setattr(module, "_build_api", lambda: pytest.fail("Kaggle API must not initialize without explicit opt-in"))
    with pytest.raises(SystemExit, match="KAGGLE_ALLOW_SUBMISSIONS=true"):
        module.main()


def test_kaggle_submit_guard_runs_before_external_submission(monkeypatch, tmp_path):
    module = _load_kaggle_script(monkeypatch)
    monkeypatch.delenv("KAGGLE_ALLOW_SUBMISSIONS", raising=False)

    class FakeApi:
        called = False

        def competition_submit(self, **kwargs):
            self.called = True

    api = FakeApi()
    with pytest.raises(RuntimeError, match="KAGGLE_ALLOW_SUBMISSIONS=true"):
        module._submit(api, "synthetic-competition", tmp_path / "submission.csv")
    assert api.called is False



def test_kaggle_script_requires_nonempty_allowlist_before_api_authentication(monkeypatch):
    module = _load_kaggle_script(monkeypatch)
    monkeypatch.setenv("KAGGLE_ALLOW_SUBMISSIONS", "true")
    monkeypatch.delenv("KAGGLE_COMPETITION_ALLOWLIST", raising=False)
    monkeypatch.setattr(module, "_build_api", lambda: pytest.fail("Kaggle API must not initialize without an exact allowlist"))
    with pytest.raises(SystemExit, match="non-empty exact"):
        module.main()


def test_kaggle_submit_requires_exact_approved_competition(monkeypatch, tmp_path):
    module = _load_kaggle_script(monkeypatch)
    monkeypatch.setenv("KAGGLE_ALLOW_SUBMISSIONS", "true")
    monkeypatch.setenv("KAGGLE_COMPETITION_ALLOWLIST", "approved-competition")

    class FakeApi:
        calls = []

        def competition_submit(self, **kwargs):
            self.calls.append(kwargs)

    api = FakeApi()
    with pytest.raises(RuntimeError, match="exact competition allowlist"):
        module._submit(api, "not-approved", tmp_path / "submission.csv")
    assert api.calls == []

    module._submit(api, "approved-competition", tmp_path / "submission.csv")
    assert len(api.calls) == 1
    assert api.calls[0]["competition"] == "approved-competition"


def test_active_competitions_are_filtered_before_processing(monkeypatch):
    module = _load_kaggle_script(monkeypatch)

    class Competition:
        def __init__(self, ref, kernels_only=False):
            self.ref = ref
            self.isKernelsSubmissionsOnly = kernels_only

    class FakeApi:
        def competitions_list(self, sort_by):
            return [
                Competition("not-approved"),
                Competition("approved-competition"),
                Competition("approved-kernels-only", kernels_only=True),
            ]

    selected = module._list_active_competitions(
        FakeApi(),
        {"approved-competition", "approved-kernels-only"},
    )
    assert [item.ref for item in selected] == ["approved-competition"]


def test_invalid_competition_allowlist_slug_fails_closed(monkeypatch):
    module = _load_kaggle_script(monkeypatch)
    monkeypatch.setenv("KAGGLE_COMPETITION_ALLOWLIST", "approved-competition,*")
    with pytest.raises(SystemExit, match="invalid slug"):
        module._approved_competitions()



def test_allowlist_cannot_exceed_configured_submission_cap(monkeypatch):
    module = _load_kaggle_script(monkeypatch)
    monkeypatch.setenv(
        "KAGGLE_COMPETITION_ALLOWLIST",
        "competition-one,competition-two,competition-three,competition-four,competition-five,competition-six",
    )
    with pytest.raises(SystemExit, match="exceeds KAGGLE_MAX_COMPETITIONS"):
        module._approved_competitions()


def test_duplicate_kaggle_entrypoint_is_guarded_and_identical(monkeypatch):
    primary = _load_kaggle_script(monkeypatch)
    duplicate = _load_kaggle_script(
        monkeypatch,
        "barrot_agent/tools/kaggle_competitions_automation.py",
    )
    primary_text = (ROOT / "scripts" / "kaggle_competitions_automation.py").read_text(encoding="utf-8")
    duplicate_text = (ROOT / "barrot_agent" / "tools" / "kaggle_competitions_automation.py").read_text(encoding="utf-8")
    assert primary_text == duplicate_text

    monkeypatch.delenv("KAGGLE_ALLOW_SUBMISSIONS", raising=False)
    monkeypatch.delenv("KAGGLE_COMPETITION_ALLOWLIST", raising=False)
    monkeypatch.setattr(
        duplicate,
        "_build_api",
        lambda: pytest.fail("duplicate entrypoint must fail before Kaggle API authentication"),
    )
    with pytest.raises(SystemExit, match="non-empty exact"):
        duplicate.main()
