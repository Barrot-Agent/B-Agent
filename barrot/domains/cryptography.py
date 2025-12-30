# barrot/domains/cryptography.py
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class CryptographyDomain:
    """Domain for cryptographic problems and research"""
    name: str = "Cryptography"
    focus_areas: List[str] = field(default_factory=lambda: [
        "Post-quantum cryptography",
        "Zero-knowledge proofs",
        "Homomorphic encryption",
        "Lattice-based cryptography",
        "Elliptic curve cryptography",
    ])
    
    def get_active_problems(self) -> List[str]:
        return [
            "Efficient post-quantum key exchange",
            "Practical fully homomorphic encryption",
            "Scalable zero-knowledge proofs",
            "Lattice problem hardness assumptions",
        ]
