"""Evidence-gated recursive self-improvement primitives."""
from .evidence import EvaluationSnapshot, ImprovementAssessment, assess_improvement
__all__ = ["EvaluationSnapshot", "ImprovementAssessment", "assess_improvement"]
