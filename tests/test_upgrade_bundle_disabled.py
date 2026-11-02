from pathlib import Path
from barrot_agent.tools import upgrade_bundle

def test_legacy_upgrade_bundle_is_disabled_without_writes(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    result = upgrade_bundle.main()
    output = capsys.readouterr().out
    assert result == 2
    assert "DISABLED" in output
    assert "No files were written" in output
    assert not (tmp_path / "barrot").exists()
