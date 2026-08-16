"""
Millennium reasoning orchestration for Barrot-Agent.

Implements an end-to-end scaffold for:
- Capability targets and scoring
- Trusted knowledge asset ingestion with provenance
- Retrieval and grounding
- Formal verification artifact tracking
- Hypothesis experimentation state
- Cross-corroboration claim assessment
- Applied-domain finding mapping
- Governance gates and reproducibility bundles
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Callable, Dict, Iterable, List, Optional, Set

from barrot_agent.logger import get_logger

logger = get_logger(__name__)

ALLOWED_CLAIM_STATUSES = ("conjecture", "partial_result", "verified_theorem")


@dataclass
class CapabilityTargets:
    """Target metrics for Millennium-level reasoning."""

    formal_proof_success_rate: float
    conjecture_generation_quality: float
    citation_reliability: float
    cross_domain_transfer_score: float
    assist_discovery_target: float
    machine_checkable_target: float

    def evaluate(self, observed: Dict[str, float]) -> Dict[str, Any]:
        """Evaluate observed metrics against configured targets."""
        targets = {
            "formal_proof_success_rate": self.formal_proof_success_rate,
            "conjecture_generation_quality": self.conjecture_generation_quality,
            "citation_reliability": self.citation_reliability,
            "cross_domain_transfer_score": self.cross_domain_transfer_score,
            "assist_discovery_target": self.assist_discovery_target,
            "machine_checkable_target": self.machine_checkable_target,
        }
        per_metric: Dict[str, Dict[str, float | bool]] = {}
        passed = 0

        for metric, target in targets.items():
            actual = float(observed.get(metric, 0.0))
            ok = actual >= target
            if ok:
                passed += 1
            per_metric[metric] = {"target": target, "actual": actual, "met": ok}

        return {
            "metrics": per_metric,
            "score": passed / max(len(targets), 1),
            "all_targets_met": passed == len(targets),
        }


@dataclass
class KnowledgeAsset:
    """Trusted knowledge item with provenance metadata."""

    asset_id: str
    title: str
    source_url: str
    source_class: str
    peer_reviewed: bool
    published_on: str
    confidence: float
    tags: List[str] = field(default_factory=list)
    citation: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FormalArtifact:
    """Machine-checkable proof or verification artifact."""

    artifact_id: str
    problem_name: str
    artifact_type: str
    uri: str
    machine_checkable: bool
    verifier: str
    checksum_sha256: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HypothesisExperiment:
    """Track one hypothesis through falsification and checks."""

    hypothesis_id: str
    statement: str
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    falsification_passed: bool = False
    formal_checks_passed: bool = False
    numeric_checks_passed: bool = False
    status: str = "candidate"
    notes: List[str] = field(default_factory=list)


@dataclass
class ClaimAssessment:
    """Cross-corroborated claim status."""

    claim: str
    status: str
    confidence: float
    evidence_ids: List[str] = field(default_factory=list)
    missing_source_classes: List[str] = field(default_factory=list)
    contradictions: List[str] = field(default_factory=list)
    rationale: str = ""


@dataclass
class FindingImpactReport:
    """Maps abstract findings to applied domains and datasets."""

    finding: str
    changed_capability: str
    applicable_domains: List[str]
    applicable_datasets: List[str]
    confidence: float
    limitations: List[str] = field(default_factory=list)


@dataclass
class GovernanceDecision:
    """Publication-governance decision."""

    approved: bool
    reason: str
    claim_status: str
    reproducibility_bundle: Dict[str, Any]


class MillenniumReasoningEngine:
    """Reasoning stack that operationalizes the Millennium implementation plan."""

    required_source_classes: Set[str] = {"paper", "formal_proof", "computational_replication"}

    def __init__(self, targets: Optional[CapabilityTargets] = None) -> None:
        self.targets = targets
        self.knowledge_assets: Dict[str, KnowledgeAsset] = {}
        self.formal_artifacts: Dict[str, FormalArtifact] = {}
        self.hypotheses: Dict[str, HypothesisExperiment] = {}
        self._connectors: Dict[str, Callable[[str], Iterable[Dict[str, Any]]]] = {}
        self._domain_index: Dict[str, Set[str]] = {}
        self._domain_datasets: Dict[str, Set[str]] = {}

    # ------------------------------------------------------------------
    # Track 1: capabilities
    # ------------------------------------------------------------------
    def set_capability_targets(self, targets: CapabilityTargets) -> None:
        self.targets = targets

    def evaluate_capability_progress(self, observed: Dict[str, float]) -> Dict[str, Any]:
        if self.targets is None:
            raise ValueError("Capability targets are not configured")
        return self.targets.evaluate(observed)

    # ------------------------------------------------------------------
    # Track 2: trusted knowledge base
    # ------------------------------------------------------------------
    def register_knowledge_asset(self, asset: KnowledgeAsset) -> None:
        self.knowledge_assets[asset.asset_id] = asset

    def ingest_knowledge_catalog(self, catalog: Dict[str, Any]) -> int:
        records = catalog.get("trusted_sources", [])
        count = 0
        for row in records:
            asset = KnowledgeAsset(
                asset_id=row["asset_id"],
                title=row["title"],
                source_url=row["source_url"],
                source_class=row.get("source_class", "paper"),
                peer_reviewed=bool(row.get("peer_reviewed", False)),
                published_on=row.get("published_on", ""),
                confidence=float(row.get("confidence", 0.0)),
                tags=list(row.get("tags", [])),
                citation=row.get("citation", ""),
                metadata=dict(row.get("metadata", {})),
            )
            self.register_knowledge_asset(asset)
            count += 1
        return count

    # ------------------------------------------------------------------
    # Track 3: retrieval + grounding
    # ------------------------------------------------------------------
    def register_connector(
        self, name: str, connector: Callable[[str], Iterable[Dict[str, Any]]]
    ) -> None:
        self._connectors[name] = connector

    def retrieve_grounded(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        min_confidence: float = 0.0,
        limit: int = 10,
    ) -> List[KnowledgeAsset]:
        """Retrieve assets using local KB + connector outputs with trust prioritization."""
        tag_set = {t.lower() for t in (tags or [])}
        all_assets = list(self.knowledge_assets.values())

        for name, connector in self._connectors.items():
            try:
                for payload in connector(query):
                    asset = self._coerce_asset(payload, source_hint=name)
                    all_assets.append(asset)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Connector '%s' failed: %s", name, exc)

        # Deduplicate by asset_id (prefer higher confidence)
        deduped: Dict[str, KnowledgeAsset] = {}
        for asset in all_assets:
            existing = deduped.get(asset.asset_id)
            if existing is None or asset.confidence > existing.confidence:
                deduped[asset.asset_id] = asset

        filtered = []
        for asset in deduped.values():
            if asset.confidence < min_confidence:
                continue
            if tag_set and not tag_set.intersection({t.lower() for t in asset.tags}):
                continue
            filtered.append(asset)

        filtered.sort(key=self._relevance_sort_key, reverse=True)
        return filtered[: max(limit, 1)]

    # ------------------------------------------------------------------
    # Track 4: formal reasoning components
    # ------------------------------------------------------------------
    def register_formal_artifact(self, artifact: FormalArtifact) -> None:
        self.formal_artifacts[artifact.artifact_id] = artifact

    # ------------------------------------------------------------------
    # Track 5: hypothesis + experiments
    # ------------------------------------------------------------------
    def record_hypothesis(
        self,
        hypothesis_id: str,
        statement: str,
        falsification_passed: bool,
        formal_checks_passed: bool,
        numeric_checks_passed: bool,
        notes: Optional[List[str]] = None,
    ) -> HypothesisExperiment:
        status = (
            "promoted"
            if falsification_passed and formal_checks_passed and numeric_checks_passed
            else "rejected"
        )
        experiment = HypothesisExperiment(
            hypothesis_id=hypothesis_id,
            statement=statement,
            falsification_passed=falsification_passed,
            formal_checks_passed=formal_checks_passed,
            numeric_checks_passed=numeric_checks_passed,
            status=status,
            notes=notes or [],
        )
        self.hypotheses[hypothesis_id] = experiment
        return experiment

    # ------------------------------------------------------------------
    # Track 6: cross-corroboration
    # ------------------------------------------------------------------
    def assess_claim(
        self,
        claim: str,
        evidence_ids: List[str],
        contradictions: Optional[List[str]] = None,
        replication_passed: bool = False,
        formal_artifact_id: Optional[str] = None,
    ) -> ClaimAssessment:
        contradictions = contradictions or []

        source_classes = set()
        confidence_values: List[float] = []

        for evidence_id in evidence_ids:
            asset = self.knowledge_assets.get(evidence_id)
            if asset is None:
                continue
            source_classes.add(asset.source_class)
            confidence_values.append(asset.confidence)

        if replication_passed:
            source_classes.add("computational_replication")

        artifact = None
        if formal_artifact_id:
            artifact = self.formal_artifacts.get(formal_artifact_id)
            if artifact and artifact.machine_checkable:
                source_classes.add("formal_proof")

        missing = sorted(self.required_source_classes - source_classes)
        base_confidence = (sum(confidence_values) / len(confidence_values)) if confidence_values else 0.0
        confidence = base_confidence
        if replication_passed:
            confidence = min(1.0, confidence + 0.1)
        if artifact and artifact.machine_checkable:
            confidence = min(1.0, confidence + 0.15)
        if contradictions:
            confidence = max(0.0, confidence - 0.3)

        if contradictions:
            status = "conjecture"
            rationale = "Contradictory evidence detected."
        elif missing:
            status = "partial_result"
            rationale = "Insufficient independent source classes for theorem-level verification."
        elif artifact and artifact.machine_checkable:
            status = "verified_theorem"
            rationale = "Corroborated by paper, machine-checkable proof, and computational replication."
        else:
            status = "partial_result"
            rationale = "Cross-corroborated but missing machine-checkable formal artifact."

        return ClaimAssessment(
            claim=claim,
            status=status,
            confidence=round(confidence, 3),
            evidence_ids=evidence_ids,
            missing_source_classes=missing,
            contradictions=contradictions,
            rationale=rationale,
        )

    # ------------------------------------------------------------------
    # Track 7: impact mapping
    # ------------------------------------------------------------------
    def register_domain_mapping(self, domain: str, tags: List[str], datasets: List[str]) -> None:
        self._domain_index.setdefault(domain, set()).update(t.lower() for t in tags)
        self._domain_datasets.setdefault(domain, set()).update(datasets)

    def map_finding_to_domains(
        self, finding: str, changed_capability: str, tags: List[str], confidence: float
    ) -> FindingImpactReport:
        tag_set = {tag.lower() for tag in tags}
        matched_domains = [
            domain for domain, domain_tags in self._domain_index.items() if tag_set.intersection(domain_tags)
        ]
        datasets: List[str] = []
        for domain in matched_domains:
            datasets.extend(sorted(self._domain_datasets.get(domain, set())))

        limitations: List[str] = []
        if not matched_domains:
            limitations.append("No mapped applied domain matched supplied finding tags.")
        if confidence < 0.5:
            limitations.append("Low-confidence finding; requires additional corroboration.")

        return FindingImpactReport(
            finding=finding,
            changed_capability=changed_capability,
            applicable_domains=sorted(matched_domains),
            applicable_datasets=sorted(set(datasets)),
            confidence=round(confidence, 3),
            limitations=limitations,
        )

    # ------------------------------------------------------------------
    # Track 8: governance + publication controls
    # ------------------------------------------------------------------
    def decide_publication(
        self, assessment: ClaimAssessment, reproducibility_artifacts: Optional[List[str]] = None
    ) -> GovernanceDecision:
        artifacts = reproducibility_artifacts or []
        bundle = self._build_reproducibility_bundle(assessment, artifacts)

        if assessment.status not in ALLOWED_CLAIM_STATUSES:
            return GovernanceDecision(
                approved=False,
                reason=f"Unsupported claim status: {assessment.status}",
                claim_status=assessment.status,
                reproducibility_bundle=bundle,
            )

        if assessment.status == "verified_theorem":
            if assessment.missing_source_classes:
                return GovernanceDecision(
                    approved=False,
                    reason="Verified theorem blocked: missing required corroboration classes.",
                    claim_status=assessment.status,
                    reproducibility_bundle=bundle,
                )
            if not artifacts:
                return GovernanceDecision(
                    approved=False,
                    reason="Verified theorem blocked: reproducibility bundle is empty.",
                    claim_status=assessment.status,
                    reproducibility_bundle=bundle,
                )

        if assessment.contradictions:
            return GovernanceDecision(
                approved=False,
                reason="Claim blocked due to unresolved contradictions.",
                claim_status=assessment.status,
                reproducibility_bundle=bundle,
            )

        return GovernanceDecision(
            approved=True,
            reason="Claim cleared for publication under governance policy.",
            claim_status=assessment.status,
            reproducibility_bundle=bundle,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _coerce_asset(self, payload: Dict[str, Any], source_hint: str) -> KnowledgeAsset:
        if not payload.get("asset_id"):
            fallback_key = f"{source_hint}:{payload.get('title', payload.get('source_url', 'unknown'))}"
            payload = {**payload, "asset_id": hashlib.sha256(fallback_key.encode("utf-8")).hexdigest()[:16]}

        return KnowledgeAsset(
            asset_id=str(payload["asset_id"]),
            title=str(payload.get("title", "Untitled source")),
            source_url=str(payload.get("source_url", "")),
            source_class=str(payload.get("source_class", "paper")),
            peer_reviewed=bool(payload.get("peer_reviewed", False)),
            published_on=str(payload.get("published_on", "")),
            confidence=float(payload.get("confidence", 0.0)),
            tags=[str(t) for t in payload.get("tags", [])],
            citation=str(payload.get("citation", "")),
            metadata=dict(payload.get("metadata", {})),
        )

    @staticmethod
    def _relevance_sort_key(asset: KnowledgeAsset) -> tuple[float, float, float]:
        peer = 1.0 if asset.peer_reviewed else 0.0
        source_bonus = 0.15 if asset.source_class in {"paper", "formal_proof"} else 0.0
        return (peer, asset.confidence, source_bonus)

    @staticmethod
    def _build_reproducibility_bundle(
        assessment: ClaimAssessment, reproducibility_artifacts: List[str]
    ) -> Dict[str, Any]:
        payload = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "claim": assessment.claim,
            "claim_status": assessment.status,
            "evidence_ids": assessment.evidence_ids,
            "missing_source_classes": assessment.missing_source_classes,
            "contradictions": assessment.contradictions,
            "confidence": assessment.confidence,
            "artifacts": reproducibility_artifacts,
        }
        serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        payload["bundle_sha256"] = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        return payload
