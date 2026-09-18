from pathlib import PurePosixPath


EXCLUDED_PREFIXES = (
    ".git/",
    ".barrot-backup/",
    "node_modules/",
    "__pycache__/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".venv/",
    "venv/",
    "dist/",
    "build/",
    "data/",
)


SUBSYSTEMS = {
    "barrot_agent": ("barrot_agent/",),
    "apex_lattice": ("apex_lattice/",),
    "barrot_runtime": (".barrot/",),
    "agent_skills": (".agents/",),
    "a2a": ("a2a/",),
    "github_workflows": (".github/workflows/",),
    "deployment": (
        "Dockerfile",
        "docker-compose.yml",
        "hf_space/",
        "self_hosted_brain/",
    ),
    "tests": (
        "tests/",
        "test_",
    ),
    "root": (),
}


def is_excluded(path: str) -> bool:
    return path.startswith(EXCLUDED_PREFIXES)


def classify_path(path: str) -> str:
    if is_excluded(path):
        return "excluded"

    for subsystem, prefixes in SUBSYSTEMS.items():
        for prefix in prefixes:
            if prefix.endswith("/"):
                if path.startswith(prefix):
                    return subsystem
            elif prefix == "test_":
                if PurePosixPath(path).name.startswith(prefix):
                    return subsystem
            elif path == prefix:
                return subsystem

    return "root"


def build_subsystem_map(tree):
    result = {}

    for path, _ in tree:
        subsystem = classify_path(path)

        if subsystem == "excluded":
            continue

        result.setdefault(subsystem, []).append(path)

    for paths in result.values():
        paths.sort()

    return dict(sorted(result.items()))
