# barrot/domains/geometry_number_theory.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class GeometryNumberTheoryDomain:
    """Domain for geometry and number theory"""
    name: str = "Geometry & Number Theory"
    focus_areas: List[str] = field(default_factory=lambda: [
        "Arithmetic geometry",
        "Algebraic topology",
        "Diophantine equations",
        "Modular forms",
        "Elliptic curves",
    ])
    
    def get_active_problems(self) -> List[str]:
        return [
            "Birch and Swinnerton-Dyer conjecture",
            "Hodge conjecture",
            "Riemann hypothesis",
            "Langlands program",
        ]
