import json
from pathlib import Path


def test_platform_evidence_packet_schema_covers_nine_platforms_and_verification_gates():
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "xrp_intelligence"
        / "platform_evidence_packet.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    expected_platforms = {
        "ChatGPT", "Claude", "Grok", "Gemini", "Copilot", "Codex",
        "Hugging Face", "Kaggle", "Databricks",
    }
    assert set(schema["properties"]["platform"]["enum"]) == expected_platforms
    assert {
        "packet_id", "created_at_utc", "data_cutoff_utc", "platform", "status",
        "auth_state", "permission_scope", "task", "source_records", "claims",
        "causal_hypotheses", "disagreement", "red_team_review", "handoff", "security",
    }.issubset(set(schema["required"]))
    assert {"DESIGNED", "EXECUTED", "VERIFIED", "BLOCKED"}.issubset(
        set(schema["properties"]["status"]["enum"])
    )
    assert "minority_objections" in schema["properties"]["disagreement"]["required"]
    assert "red_team_review" in schema["required"]
    assert {
        "data_cutoff_utc", "horizon", "target", "assumptions", "probability",
        "alternatives", "confidence", "model_version", "outcome_due_at_utc", "outcome_status",
    }.issubset(set(schema["properties"]["forecast"]["required"]))
    security = schema["properties"]["security"]["properties"]
    assert security["public_or_authorized_sources_only"]["const"] is True
    assert security["private_data_used"]["const"] is False
    assert security["secrets_in_packet"]["const"] is False
    assert security["unauthorized_access"]["const"] is False
    assert security["market_manipulation"]["const"] is False
    assert security["real_money_action"]["const"] is False
