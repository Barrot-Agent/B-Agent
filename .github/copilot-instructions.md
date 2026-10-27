# Copilot Coding Agent Instructions

## Repository context
- The repo hosts two independent systems: the **search engine** (`/search-engine`) and the **agent dashboard** (`/site`). Keep changes scoped to the relevant area.
- Avoid touching private agent configs under `.github/agents/`.

## Development guidelines
- Favor Python standard library; do not add new dependencies unless absolutely required.
- Keep workflow files in `.github/workflows/` stable; understand their impact before edits.
- Make the smallest possible change that solves the problem.

## Testing and verification
- There is no default automated test suite. When modifying Python code, run targeted checks such as `python -m compileall <changed directories>` instead of broad commands.
- Manually verify affected features and document any steps taken.

## Pull requests and reviews
- Provide concise summaries with no follow-up work required.
- Confirm CI status and recent workflow results when relevant to the change.
