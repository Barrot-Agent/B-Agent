from pathlib import Path


TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".md",
    ".sh",
}


def should_read(path: str) -> bool:
    name = Path(path).name
    suffix = Path(path).suffix.lower()

    return suffix in TEXT_EXTENSIONS or name in {
        "Dockerfile",
        "requirements.txt",
        "pyproject.toml",
        "package.json",
        "README.md",
    }


def build_subsystem_context(
    repo,
    subsystem_name,
    paths,
    max_file_chars=6000,
    max_total_chars=30000,
):
    blocks = []
    total = 0

    for path in paths:
        if total >= max_total_chars:
            break

        if not should_read(path):
            continue

        try:
            content = repo.read_file(path)
        except Exception as exc:
            blocks.append(
                f"\n===== FILE: {path} =====\n"
                f"[READ FAILED: {type(exc).__name__}: {exc}]\n"
            )
            continue

        if len(content) > max_file_chars:
            content = (
                content[:max_file_chars]
                + "\n\n[TRUNCATED]\n"
            )

        block = (
            f"\n===== FILE: {path} =====\n"
            f"{content}\n"
        )

        remaining = max_total_chars - total

        if len(block) > remaining:
            block = block[:remaining]

        blocks.append(block)
        total += len(block)

    listing = "\n".join(paths)

    return (
        f"SUBSYSTEM: {subsystem_name}\n"
        f"FILES: {len(paths)}\n\n"
        f"===== FILE LIST =====\n"
        f"{listing}\n\n"
        f"===== INSPECTED CONTENT =====\n"
        f"{''.join(blocks)}"
    )
