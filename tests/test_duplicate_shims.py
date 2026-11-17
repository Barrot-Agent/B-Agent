"""Phase 2 dedupe proof.

Two kinds of check:

1. SHIM EQUIVALENCE — every public name of the canonical module must exist on
   the shim and be the *same object*. A shim that drifts is a bug.
2. DRIFT GUARD — the two copies that must stay byte-identical (because one is
   shipped standalone and cannot be shimmed) are compared by sha256, so any
   future edit to only one of them fails here.

No network, no subprocess, no writes.
"""
from __future__ import annotations

import ast
import hashlib
import importlib
import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _load_path(name: str, relative: str):
    """Import a module from an explicit file path (scripts/, utils/ are not packages)."""
    path = REPO / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SHIMS = [
    # (shim module name, shim path, canonical module name)
    ("scripts.mem_palace", "scripts/mem_palace.py", "barrot_agent.mem_palace"),
    ("tools.mem_palace", "tools/mem_palace.py", "barrot_agent.mem_palace"),
    ("scripts.granite_model_config", "scripts/granite_model_config.py",
     "barrot_agent.tools.granite_model_config"),
    ("utils.score_to_signal", "utils/score_to_signal.py",
     "barrot_agent.analysis.score_to_signal"),
    ("scripts.deploy_huggingface", "scripts/deploy_huggingface.py",
     "barrot_agent.orchestration.deploy_huggingface"),
    ("barrot_agent.tools.trial_tracker", "barrot_agent/tools/trial_tracker.py",
     "barrot_agent.monetization.trial_tracker"),
]


def _public(module) -> set[str]:
    return {name for name in vars(module) if not name.startswith("_")}


@pytest.mark.parametrize("shim_name,shim_path,canonical_name", SHIMS)
def test_shim_reexports_every_public_name(shim_name, shim_path, canonical_name):
    canonical = importlib.import_module(canonical_name)
    shim = _load_path(shim_name, shim_path)

    missing = _public(canonical) - _public(shim)
    assert not missing, f"{shim_path} does not re-export: {sorted(missing)}"


@pytest.mark.parametrize("shim_name,shim_path,canonical_name", SHIMS)
def test_shim_exports_are_the_same_objects(shim_name, shim_path, canonical_name):
    canonical = importlib.import_module(canonical_name)
    shim = _load_path(shim_name, shim_path)

    for name in _public(canonical):
        canonical_obj = getattr(canonical, name)
        if not callable(canonical_obj):
            continue
        assert getattr(shim, name) is canonical_obj, (
            f"{shim_path}.{name} is not the canonical object — shim has drifted"
        )


@pytest.mark.parametrize("shim_name,shim_path,canonical_name", SHIMS)
def test_shim_is_import_only(shim_name, shim_path, canonical_name):
    """A shim may only import, set sys.path, and delegate under __main__.

    Enforced structurally: no function or class definitions anywhere in the
    file, and only the statement kinds a shim needs at top level.
    """
    tree = ast.parse((REPO / shim_path).read_text())
    allowed = (ast.Import, ast.ImportFrom, ast.Assign, ast.AnnAssign, ast.If)
    for index, node in enumerate(tree.body):
        is_docstring = (
            index == 0
            and isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )
        assert is_docstring or isinstance(node, allowed), (
            f"{shim_path}: unexpected top-level {type(node).__name__} — "
            "this is logic, move it to the canonical module"
        )
    definitions = [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    ]
    assert not definitions, f"{shim_path}: shim defines {len(definitions)} symbol(s)"


# ---------------------------------------------------------------- drift guard

def _sha256(relative: str) -> str:
    return hashlib.sha256((REPO / relative).read_bytes()).hexdigest()


def test_hrm_ternary_copies_are_byte_identical():
    """hf_space/ ships standalone (app.py: 'ships alongside app.py on the Space'),
    so it cannot be shimmed. Hash equality keeps the two copies honest."""
    assert _sha256("core/hrm_ternary.py") == _sha256("hf_space/hrm_ternary.py")


def test_grant_generator_copies_are_byte_identical():
    """5-line print-only script. Shimming would print on import, so the copies
    stay and are hash-locked instead."""
    assert _sha256("barrot_agent/monetization/grant_generator.py") == \
        _sha256("barrot_agent/tools/grant_generator.py")
