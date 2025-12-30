# barrot/domains/pde_physics.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class PDEPhysicsDomain:
    """Domain for partial differential equations in physics"""
    name: str = "PDE & Physics"
    focus_areas: List[str] = field(default_factory=lambda: [
        "Navier-Stokes equations",
        "Einstein field equations",
        "Schrödinger equation",
        "Wave equations",
        "Heat equation",
    ])
    
    def get_active_problems(self) -> List[str]:
        return [
            "Navier-Stokes smoothness and existence",
            "General relativity singularities",
            "Quantum field theory foundations",
            "Turbulence modeling",
        ]
