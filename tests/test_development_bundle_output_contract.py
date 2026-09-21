from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_generated_bundle_provenance_contract():
    generated = sorted(
        (
            ROOT
            / ".barrot"
            / "autonomous_bundle"
            / "generated"
        ).glob(
            "development_bundle_*.json"
        )
    )

    if not generated:
        raise AssertionError(
            "No generated development bundle exists"
        )

    bundle = generated[-1]

    data = json.loads(
        bundle.read_text(
            encoding="utf-8"
        )
    )

    provenance = data.get(
        "provenance"
    )

    assert isinstance(
        provenance,
        dict,
    )

    assert provenance.get(
        "builder_sha256"
    )

    assert provenance.get(
        "mission_sha256"
    )

    assert provenance.get(
        "spec_sha256"
    )

    assert provenance.get(
        "spec_record_sha256"
    )

    evidence = bundle.with_name(
        bundle.stem
        + ".evidence.json"
    )

    assert evidence.exists()

    evidence_data = json.loads(
        evidence.read_text(
            encoding="utf-8"
        )
    )

    assert evidence_data.get(
        "source_spec_sha256"
    )

    assert evidence_data.get(
        "source_spec_record_sha256"
    )
