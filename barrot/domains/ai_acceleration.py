# barrot/domains/ai_acceleration.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class AIAccelerationDomain:
    """Domain for AI-accelerated mathematical research"""
    name: str = "AI Acceleration"
    focus_areas: List[str] = field(default_factory=lambda: [
        "Automated theorem proving",
        "Neural network guided proof search",
        "Symbolic regression",
        "Conjecture generation",
        "Pattern recognition in mathematical structures",
    ])
    
    def get_active_problems(self) -> List[str]:
        return [
            "Developing AI systems for proof discovery",
            "Automated conjecture generation",
            "Machine learning for mathematical insight",
            "Formal verification with AI assistance",
        ]
