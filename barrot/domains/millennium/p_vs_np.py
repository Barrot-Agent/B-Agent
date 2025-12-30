# barrot/domains/millennium/p_vs_np.py
from typing import List
from .base_problem import MillenniumProblem

class PvsNP(MillenniumProblem):
    def __init__(self):
        super().__init__(
            name="P versus NP",
            description="Can every problem whose solution can be verified quickly also be solved quickly?",
            keywords=["computational complexity", "algorithms", "NP-complete", "complexity theory"],
        )
    
    def get_formal_statement(self) -> str:
        return (
            "Does P = NP? That is, if the solution to a problem can be verified in polynomial time, "
            "can the problem also be solved in polynomial time? "
            "Equivalently, is every problem in NP also in P?"
        )
    
    def get_approaches(self) -> List[str]:
        return [
            "Circuit complexity lower bounds",
            "Natural proofs barrier",
            "Algebraic approaches",
            "Proof complexity",
            "Geometric complexity theory",
            "Oracle separations",
        ]
