import re


IMPORT_PATTERNS = (
    re.compile(
        r"^\s*import\s+([A-Za-z0-9_\.]+)",
        re.MULTILINE,
    ),
    re.compile(
        r"^\s*from\s+([A-Za-z0-9_\.]+)\s+import",
        re.MULTILINE,
    ),
)


def find_python_imports(content: str):
    imports = set()

    for pattern in IMPORT_PATTERNS:
        for match in pattern.finditer(content):
            imports.add(match.group(1))

    return sorted(imports)


def analyze_dependencies(repo, paths):
    result = {}

    for path in paths:
        if not path.endswith(".py"):
            continue

        try:
            content = repo.read_file(path)
        except Exception:
            continue

        result[path] = find_python_imports(content)

    return result
