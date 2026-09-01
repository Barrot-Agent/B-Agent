from barrot_agent.trust import TrustEngine


def test_success_requires_state_verification():
    engine = TrustEngine()

    result = engine.execute(
        task="test",
        expected_state={"namespace": "barrot-agent-group"},
        observed_state={"namespace": "barrot-agent-group"},
        validators=[
            lambda x: x["namespace"] == "barrot-agent-group",
        ],
        risk="low",
    )

    assert result["authoritative"] is True
    assert result["verification"]["passed"] is True
    assert result["certificate"]["certificate_type"] == "BVC-1"


def test_http_success_does_not_equal_operation_success():
    engine = TrustEngine()

    result = engine.execute(
        task="transfer_project",
        expected_state={"namespace": "barrot-agent-group"},
        observed_state={"namespace": "Barrot-Agent"},
        validators=[
            lambda x: x["namespace"] == "barrot-agent-group",
        ],
        risk="medium",
        transport_success=True,
    )

    assert result["authoritative"] is False
    assert result["verification"]["passed"] is False
    assert any(
        s["code"] == "STATE_MISMATCH"
        for s in result["syndromes"]
    )


def test_certificate_is_hashed():
    engine = TrustEngine()

    result = engine.execute(
        task="certificate",
        expected_state="A",
        observed_state="A",
        validators=[lambda x: x == "A"],
        risk="low",
    )

    certificate = result["certificate"]

    assert certificate["certificate_hash"]
    assert len(certificate["certificate_hash"]) == 64


def test_failed_state_never_becomes_authoritative():
    from barrot_agent.trust import TrustEngine

    engine = TrustEngine()

    result = engine.execute(
        task="failed-operation",
        expected_state={"status": "complete"},
        observed_state={"status": "failed"},
        validators=[lambda value: value["status"] == "complete"],
        risk="high",
        transport_success=True,
    )

    assert result["authoritative"] is False
    assert result["verification"]["passed"] is False
    assert result["confidence"]["lower_bound"] == 0.0
