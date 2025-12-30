# barrot/core/contradiction_vectors.py
from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class ContradictionVector:
    id: str
    description: str
    source_region: str          # where in proof-space it appears
    severity: float             # how strongly it blocks progress
    features: Dict[str, Any]    # symbolic fingerprint

    def merge(self, other: "ContradictionVector") -> "ContradictionVector":
        # naive example: later refine into real feature merging
        return ContradictionVector(
            id=f"{self.id}+{other.id}",
            description=f"{self.description} / {other.description}",
            source_region=f"{self.source_region},{other.source_region}",
            severity=max(self.severity, other.severity),
            features={**self.features, **other.features},
        )
