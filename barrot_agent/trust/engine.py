from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Iterable, List, Optional


class SyndromeSeverity(str, Enum):
    BENIGN = "benign"
    RECOVERABLE = "recoverable"
    SIGNIFICANT = "significant"
    FATAL = "fatal"
    UNKNOWN = "unknown"


@dataclass
class Syndrome:
    code: str
    severity: SyndromeSeverity
    message: str
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity.value,
            "message": self.message,
            "evidence": self.evidence,
        }


class StateVerifier:
    """
    Verifies observed state against intended state.

    A successful transport/API response is NOT treated as proof
    that the requested state was actually achieved.
    """

    def verify(
        self,
        expected: Any,
        observed: Any,
        *,
        comparator: Optional[Callable[[Any, Any], bool]] = None,
    ) -> Dict[str, Any]:
        if comparator is None:
            passed = expected == observed
        else:
            passed = bool(comparator(expected, observed))

        return {
            "passed": passed,
            "expected": expected,
            "observed": observed,
            "reason": "STATE_MATCH" if passed else "STATE_MISMATCH",
        }


class SyndromeEngine:
    """
    Converts failed or suspicious verification signals into structured
    syndromes that can drive repair/retry decisions.
    """

    def detect(
        self,
        *,
        verification: Dict[str, Any],
        transport_success: bool = True,
        anomalies: Optional[Iterable[Dict[str, Any]]] = None,
    ) -> List[Syndrome]:
        syndromes: List[Syndrome] = []

        if transport_success and not verification.get("passed", False):
            syndromes.append(
                Syndrome(
                    code="STATE_MISMATCH",
                    severity=SyndromeSeverity.SIGNIFICANT,
                    message="Transport succeeded but observed state does not match expected state.",
                    evidence=verification,
                )
            )

        if not transport_success:
            syndromes.append(
                Syndrome(
                    code="TRANSPORT_FAILURE",
                    severity=SyndromeSeverity.RECOVERABLE,
                    message="Underlying operation did not complete successfully.",
                )
            )

        for anomaly in anomalies or []:
            syndromes.append(
                Syndrome(
                    code=anomaly.get("code", "UNKNOWN_ANOMALY"),
                    severity=SyndromeSeverity(
                        anomaly.get("severity", SyndromeSeverity.UNKNOWN.value)
                    ),
                    message=anomaly.get("message", "Unspecified anomaly."),
                    evidence=anomaly,
                )
            )

        return syndromes


class AdaptiveValidator:
    """
    Allocates verification effort according to risk.

    low      -> 1 validator
    medium   -> 2 validators
    high     -> 3 validators
    critical -> 5 validators
    """

    LEVELS = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 5,
    }

    def required_validators(self, risk: str = "medium") -> int:
        return self.LEVELS.get(str(risk).lower(), self.LEVELS["medium"])

    def validate(
        self,
        value: Any,
        validators: Iterable[Callable[[Any], bool]],
        *,
        risk: str = "medium",
    ) -> Dict[str, Any]:
        validators = list(validators)
        required = self.required_validators(risk)

        results = []
        for validator in validators[:required]:
            try:
                results.append(bool(validator(value)))
            except Exception:
                results.append(False)

        passed = bool(results) and all(results)

        return {
            "risk": risk,
            "required_validators": required,
            "validators_used": len(results),
            "results": results,
            "passed": passed,
        }


class ConfidenceEngine:
    """
    Produces a conservative confidence score.

    This is an engineering confidence metric, not a statistical claim
    unless supplied with statistically justified inputs.
    """

    def calculate(
        self,
        *,
        execution_success: bool,
        state_verified: bool,
        validator_results: Iterable[bool],
        unresolved_syndromes: int = 0,
        evidence_score: float = 1.0,
    ) -> Dict[str, float]:
        validators = list(validator_results)
        validator_score = (
            sum(1 for x in validators if x) / len(validators)
            if validators
            else 0.0
        )

        execution_score = 1.0 if execution_success else 0.0
        state_score = 1.0 if state_verified else 0.0

        evidence_score = max(0.0, min(1.0, float(evidence_score)))

        base = (
            execution_score
            * state_score
            * validator_score
            * evidence_score
        )

        penalty = min(0.50, unresolved_syndromes * 0.10)
        confidence = max(0.0, min(1.0, base - penalty))

        return {
            "execution": execution_score,
            "state": state_score,
            "validators": validator_score,
            "evidence": evidence_score,
            "lower_bound": confidence,
        }


@dataclass
class VerificationCertificate:
    operation_id: str
    task: str
    input_hash: str
    execution_hash: str
    checks_completed: int
    checks_passed: int
    checks_failed: int
    syndromes: List[Dict[str, Any]]
    confidence: Dict[str, float]
    state_verified: bool
    provenance: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    certificate_hash: Optional[str] = None

    def finalize(self) -> "VerificationCertificate":
        payload = {
            "operation_id": self.operation_id,
            "task": self.task,
            "input_hash": self.input_hash,
            "execution_hash": self.execution_hash,
            "checks_completed": self.checks_completed,
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "syndromes": self.syndromes,
            "confidence": self.confidence,
            "state_verified": self.state_verified,
            "provenance": self.provenance,
            "timestamp": self.timestamp,
        }

        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode()

        self.certificate_hash = hashlib.sha256(encoded).hexdigest()
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "certificate_type": "BVC-1",
            "operation_id": self.operation_id,
            "task": self.task,
            "input_hash": self.input_hash,
            "execution_hash": self.execution_hash,
            "checks": {
                "completed": self.checks_completed,
                "passed": self.checks_passed,
                "failed": self.checks_failed,
            },
            "syndromes": self.syndromes,
            "confidence": self.confidence,
            "state_verified": self.state_verified,
            "provenance": self.provenance,
            "timestamp": self.timestamp,
            "certificate_hash": self.certificate_hash,
        }


class TrustEngine:
    """
    Unified Barrot trust pipeline:

        OBSERVE
        -> VERIFY
        -> DETECT
        -> VALIDATE
        -> SCORE
        -> CERTIFY

    The operation is not considered authoritative merely because
    an API returned HTTP success.
    """

    def __init__(self):
        self.state_verifier = StateVerifier()
        self.syndrome_engine = SyndromeEngine()
        self.adaptive_validator = AdaptiveValidator()
        self.confidence_engine = ConfidenceEngine()

    @staticmethod
    def _hash(value: Any) -> str:
        encoded = json.dumps(
            value,
            sort_keys=True,
            default=str,
            separators=(",", ":"),
        ).encode()
        return hashlib.sha256(encoded).hexdigest()

    def execute(
        self,
        *,
        task: str,
        expected_state: Any,
        observed_state: Any,
        validators: Optional[Iterable[Callable[[Any], bool]]] = None,
        risk: str = "medium",
        transport_success: bool = True,
        provenance: Optional[List[str]] = None,
        anomalies: Optional[Iterable[Dict[str, Any]]] = None,
        evidence_score: float = 1.0,
    ) -> Dict[str, Any]:

        operation_id = str(uuid.uuid4())

        verification = self.state_verifier.verify(
            expected_state,
            observed_state,
        )

        syndromes = self.syndrome_engine.detect(
            verification=verification,
            transport_success=transport_success,
            anomalies=anomalies,
        )

        validation = self.adaptive_validator.validate(
            observed_state,
            validators or [],
            risk=risk,
        )

        all_validator_results = validation["results"]

        confidence = self.confidence_engine.calculate(
            execution_success=transport_success,
            state_verified=verification["passed"],
            validator_results=all_validator_results,
            unresolved_syndromes=sum(
                1
                for s in syndromes
                if s.severity
                in {
                    SyndromeSeverity.SIGNIFICANT,
                    SyndromeSeverity.FATAL,
                }
            ),
            evidence_score=evidence_score,
        )

        checks_completed = (
            1
            + validation["validators_used"]
            + len(syndromes)
        )

        checks_passed = (
            int(verification["passed"])
            + sum(1 for x in all_validator_results if x)
        )

        checks_failed = checks_completed - checks_passed

        certificate = VerificationCertificate(
            operation_id=operation_id,
            task=task,
            input_hash=self._hash(expected_state),
            execution_hash=self._hash(observed_state),
            checks_completed=checks_completed,
            checks_passed=checks_passed,
            checks_failed=checks_failed,
            syndromes=[s.to_dict() for s in syndromes],
            confidence=confidence,
            state_verified=verification["passed"],
            provenance=provenance or [],
        ).finalize()

        authoritative = (
            transport_success
            and verification["passed"]
            and validation["passed"]
            and not any(
                s.severity
                in {
                    SyndromeSeverity.SIGNIFICANT,
                    SyndromeSeverity.FATAL,
                }
                for s in syndromes
            )
        )

        return {
            "operation_id": operation_id,
            "task": task,
            "authoritative": authoritative,
            "verification": verification,
            "validation": validation,
            "syndromes": [s.to_dict() for s in syndromes],
            "confidence": confidence,
            "certificate": certificate.to_dict(),
        }
