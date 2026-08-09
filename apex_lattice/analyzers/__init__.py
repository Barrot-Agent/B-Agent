"""Analyzers sub-package for Apex Lattice.

Each analyzer module exposes an Analyzer class (subclassing BaseAnalyzer)
with an analyze() method returning a dict containing at least a
'findings' list. Analyzers are loaded dynamically by module path via
apex_lattice.sandbox.SandboxPipeline / select_analyzers. Concrete classes are
also available through lazy, descriptive aliases for callers that want a
stable package-level API. The aliases are listed in ``__all__`` and resolved
on demand through PEP 562 module attribute lookup.
"""

from __future__ import annotations

import importlib

from apex_lattice.analyzers.base import BaseAnalyzer

_ANALYZER_EXPORTS = {
    "ArchitectureAnalyzer": "architecture_analyzer",
    "CapabilityAnalyzer": "capability_analyzer",
    "CodeAnalyzer": "code_analyzer",
    "DependencyAnalyzer": "dependency_analyzer",
    "PerformanceAnalyzer": "performance_analyzer",
    "ReverseEngineeringAnalyzer": "reverse_engineering_analyzer",
    "ScopeCreepAnalyzer": "scope_creep_analyzer",
    "SecurityAnalyzer": "security_analyzer",
    "TestQualityAnalyzer": "test_quality_analyzer",
}

__all__ = ["BaseAnalyzer", *_ANALYZER_EXPORTS]


def __getattr__(name: str) -> type[BaseAnalyzer]:
    """Load a concrete analyzer only when its public alias is requested."""
    module_name = _ANALYZER_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = importlib.import_module(f"{__name__}.{module_name}")
    analyzer = getattr(module, "Analyzer")
    if not issubclass(analyzer, BaseAnalyzer):
        raise TypeError(f"{module_name}.Analyzer must subclass BaseAnalyzer")
    globals()[name] = analyzer
    return analyzer
