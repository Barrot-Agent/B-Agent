"""Analyzers sub-package for Apex Lattice.

Each analyzer module exposes an Analyzer class (subclassing BaseAnalyzer)
with an analyze() method returning a dict containing at least a
'findings' list. Analyzers are loaded dynamically by module path via
apex_lattice.sandbox.SandboxPipeline / select_analyzers.
"""

from apex_lattice.analyzers.base import BaseAnalyzer

__all__ = ["BaseAnalyzer"]
