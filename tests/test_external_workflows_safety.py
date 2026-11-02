import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _load_kaggle_script(monkeypatch):
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

    path = ROOT / "scripts" / "kaggle_competitions_automation.py"
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
