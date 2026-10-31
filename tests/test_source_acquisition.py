from barrot_agent.sources.source_acquisition import (
    AcquisitionNeed,
    AcquisitionTarget,
    SourceAcquisitionPlanner,
)


def make_need():
    return AcquisitionNeed(
        need_id="need-001",
        category="technical",
        description="Missing technical documentation",
        priority="HIGH",
        rationale="Required to close a documented capability gap",
        related_gap_ids=["gap-001"],
        required_evidence=["official documentation"],
    )


def make_target():
    return AcquisitionTarget(
        target_id="target-001",
        need_id="need-001",
        source_type="documentation",
        name="Example Technical Specification",
        purpose="Close the technical documentation gap",
        discovery_uri="https://example.invalid/discovery",
        publisher="Example Publisher",
        provenance_requirements=[
            "publisher identity",
            "retrieval timestamp",
            "content hash",
        ],
        verification_requirements=[
            "source accessibility",
            "content integrity",
        ],
    )


def test_need_persists_and_reloads(tmp_path):
    path = tmp_path / "planner.json"

    planner = SourceAcquisitionPlanner(path)
    planner.add_need(make_need())

    reloaded = SourceAcquisitionPlanner(path)

    need = reloaded.get_need("need-001")

    assert need is not None
    assert need.category == "technical"
    assert need.priority == "HIGH"


def test_target_requires_existing_need(tmp_path):
    planner = SourceAcquisitionPlanner(
        tmp_path / "planner.json"
    )

    target = make_target()

    try:
        planner.add_target(target)
        assert False, "Expected unknown need to fail"
    except KeyError:
        pass


def test_target_persists_and_reloads(tmp_path):
    path = tmp_path / "planner.json"

    planner = SourceAcquisitionPlanner(path)
    planner.add_need(make_need())
    planner.add_target(make_target())

    reloaded = SourceAcquisitionPlanner(path)

    target = reloaded.get_target("target-001")

    assert target is not None
    assert target.mmi_required is True
    assert target.independent_corroboration_required is True


def test_duplicate_target_is_idempotent(tmp_path):
    planner = SourceAcquisitionPlanner(
        tmp_path / "planner.json"
    )

    planner.add_need(make_need())

    first = planner.add_target(make_target())
    second = planner.add_target(make_target())

    assert first.content_hash() == second.content_hash()
    assert planner.summary()["target_count"] == 1


def test_conflicting_target_is_rejected(tmp_path):
    planner = SourceAcquisitionPlanner(
        tmp_path / "planner.json"
    )

    planner.add_need(make_need())
    planner.add_target(make_target())

    changed = AcquisitionTarget(
        target_id="target-001",
        need_id="need-001",
        source_type="dataset",
        name="Different Source",
        purpose="Different purpose",
    )

    try:
        planner.add_target(changed)
        assert False, "Expected conflicting target to fail"
    except ValueError:
        pass


def test_target_status_update(tmp_path):
    planner = SourceAcquisitionPlanner(
        tmp_path / "planner.json"
    )

    planner.add_need(make_need())
    planner.add_target(make_target())

    updated = planner.update_target_status(
        "target-001",
        "VERIFIED",
    )

    assert updated.status == "VERIFIED"
    assert planner.summary()["status_counts"] == {
        "VERIFIED": 1
    }


def test_gaps_and_summary(tmp_path):
    planner = SourceAcquisitionPlanner(
        tmp_path / "planner.json"
    )

    planner.add_need(make_need())
    planner.add_target(make_target())

    gaps = planner.gaps()

    assert len(gaps) == 1
    assert gaps[0]["need_id"] == "need-001"
    assert gaps[0]["target_count"] == 1

    summary = planner.summary()

    assert summary["need_count"] == 1
    assert summary["target_count"] == 1
    assert summary["status_counts"] == {
        "PROPOSED": 1
    }
