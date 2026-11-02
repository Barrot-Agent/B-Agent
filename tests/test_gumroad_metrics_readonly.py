import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "scripts" / "gumroad_metrics.py"
    spec = importlib.util.spec_from_file_location("gumroad_metrics_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gumroad_metrics_workflow_is_read_only_and_artifact_based():
    workflow = (ROOT / ".github" / "workflows" / "gumroad-metrics.yml").read_text(encoding="utf-8")
    assert "contents: read" in workflow
    assert "contents: write" not in workflow
    assert "persist-credentials: false" in workflow
    assert "actions/upload-artifact@" in workflow
    assert "retention-days: 30" in workflow
    assert "git commit" not in workflow
    assert "git push" not in workflow
    assert "GUMROAD_ACCESS_TOKEN" in workflow


def test_gumroad_metrics_writes_only_allowlisted_aggregate_and_never_logs_raw_product(tmp_path, monkeypatch, capsys):
    module = load_module()
    module.TOKEN = "synthetic-test-token"
    module.OUT_PATH = str(tmp_path / "gumroad_metrics.json")
    module.fetch_products = lambda: {
        "success": True,
        "products": [
            {
                "name": "XRP Signal Service",
                "short_url": "https://gumroad.com/l/opvxi",
                "sales_count": 12,
                "price": 1999,
                "currency": "usd",
                "published": True,
                "buyer_email": "synthetic-private@example.invalid",
                "private_note": "synthetic private field",
            }
        ],
    }

    assert module.main() == 0
    output = capsys.readouterr().out
    payload = json.loads((tmp_path / "gumroad_metrics.json").read_text(encoding="utf-8"))

    assert payload["sales_count"] == 12
    assert payload["price_cents"] == 1999
    assert payload["currency"] == "usd"
    assert "buyer_email" not in payload
    assert "private_note" not in payload
    assert "synthetic-private@example.invalid" not in output
    assert "synthetic private field" not in output
    assert "RAW real product response" not in output


def test_gumroad_metrics_refuses_to_substitute_first_product(tmp_path, capsys):
    module = load_module()
    module.TOKEN = "synthetic-test-token"
    module.OUT_PATH = str(tmp_path / "gumroad_metrics.json")
    module.fetch_products = lambda: {
        "success": True,
        "products": [
            {
                "name": "Different product",
                "short_url": "https://gumroad.com/l/not-opvxi",
                "sales_count": 99,
                "price": 100,
                "currency": "usd",
            }
        ],
    }

    assert module.main() == 2
    assert not (tmp_path / "gumroad_metrics.json").exists()
    assert "refusing to substitute another product" in capsys.readouterr().err
