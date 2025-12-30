# barrot/domains/millennium/yang_mills.py
from typing import List
from .base_problem import MillenniumProblem

class YangMills(MillenniumProblem):
    def __init__(self):
        super().__init__(
            name="Yang-Mills and Mass Gap",
            description="Prove Yang-Mills theory exists and has a mass gap",
            keywords=["quantum field theory", "gauge theory", "mass gap", "quantum chromodynamics"],
        )
    
    def get_formal_statement(self) -> str:
        return (
            "Prove that for any compact simple gauge group G, "
            "a non-trivial quantum Yang-Mills theory exists on ℝ⁴ and has a mass gap Δ > 0. "
            "This means the quantum excitations have a minimum energy above the vacuum."
        )
    
    def get_approaches(self) -> List[str]:
        return [
            "Lattice gauge theory",
            "Constructive quantum field theory",
            "Functional integration methods",
            "Renormalization group techniques",
            "Computer simulations",
        ]
