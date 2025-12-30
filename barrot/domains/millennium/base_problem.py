# barrot/domains/millennium/base_problem.py
from dataclasses import dataclass, field
from typing import List, Dict, Any
from abc import ABC, abstractmethod

@dataclass
class MillenniumProblem(ABC):
    """Base class for all Millennium Prize Problems"""
    name: str
    prize_amount: int = 1_000_000  # USD
    status: str = "open"  # "open" or "solved"
    year_posed: int = 0  # Year the problem was first posed (0 = unspecified)
    description: str = ""
    keywords: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @abstractmethod
    def get_formal_statement(self) -> str:
        """Return the formal mathematical statement of the problem"""
        pass
    
    @abstractmethod
    def get_approaches(self) -> List[str]:
        """Return known approaches to the problem"""
        pass
    
    def is_solved(self) -> bool:
        return self.status == "solved"
