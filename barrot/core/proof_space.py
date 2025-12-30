# barrot/core/proof_space.py
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class ProofFragment:
    id: str
    problem: str
    statement: str
    sketch: str
    status: str       # "hypothesis", "attempted", "refuted", "promising"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProofSpace:
    fragments: Dict[str, ProofFragment] = field(default_factory=dict)

    def add_fragment(self, fragment: ProofFragment) -> None:
        self.fragments[fragment.id] = fragment

    def get_fragments_for_problem(self, problem: str) -> List[ProofFragment]:
        return [f for f in self.fragments.values() if f.problem == problem]

    def mark_status(self, fragment_id: str, status: str) -> None:
        self.fragments[fragment_id].status = status
