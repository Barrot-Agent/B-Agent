#!/usr/bin/env bash
# ============================================================================
# push_with_token.sh — the GH_TOKEN plug for Barrot-Agent pushes.
#
# House rules honored (BARROT_SYNC.md):
#   - No password auth, no SSH key requirement: fine-grained PAT over HTTPS
#     with username "x-access-token" only.
#   - Direct pushes to main are disabled. Push only the current non-main branch;
#     use a reviewed pull request and the fail-closed merge gate for main.
#   - The token is read from GH_TOKEN, never written to disk, echoed, or
#     stored in .git/config or remote URLs. Validation sends it to curl through
#     config stdin and to the Python fallback through stdin, not process argv.
#     The single-quoted git credential-helper string contains the literal
#     ${GH_TOKEN}; only the helper shell expands it from its environment, so
#     the parent shell does not interpolate the token into git's argv.
#
# One-time token setup (do this in your browser, NOT in chat):
#   1. Open https://github.com/settings/personal-access-tokens/new
#   2. Token name: barrot-push
#   3. Repository access: "Only select repositories" -> Barrot-Agent/B-Agent
#   4. Repository permissions: Contents -> "Read and write"
#      (Metadata is granted read-only automatically.)
#   5. Generate, copy the github_pat_... value, then run IN YOUR TERMINAL:
#
#        GH_TOKEN=github_pat_xxxxxxxxxxxx bash scripts/push_with_token.sh
#
# Usage:
#   GH_TOKEN=... bash scripts/push_with_token.sh                         # current non-main branch
#   GH_TOKEN=... bash scripts/push_with_token.sh --verify-only           # no push
#   BRANCH=integration/my-task GH_TOKEN=... bash scripts/push_with_token.sh
#   BRANCH=main is rejected; use a pull request for main.
# ============================================================================
set -euo pipefail

REPO_SLUG="${REPO_SLUG:-Barrot-Agent/B-Agent}"

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

CURRENT_BRANCH="$(git branch --show-current)"
BRANCH="${BRANCH:-${CURRENT_BRANCH}}"

if [[ -z "${BRANCH}" ]]; then
  echo "ERROR: no current branch is available (detached HEAD); set BRANCH to a non-main branch." >&2
  exit 5
fi
if [[ "${BRANCH}" == "main" ]]; then
  echo "ERROR: direct pushes to main are disabled. Use a pull request and the verified merge gate." >&2
  exit 6
fi
if ! git check-ref-format --branch "${BRANCH}" >/dev/null 2>&1; then
  echo "ERROR: BRANCH is not a valid Git branch name." >&2
  exit 7
fi

if [[ -z "${GH_TOKEN:-}" ]]; then
  echo "ERROR: GH_TOKEN is not set." >&2
  echo "Create a fine-grained PAT:" >&2
  echo "  https://github.com/settings/personal-access-tokens/new" >&2
  echo "  Repo: ${REPO_SLUG} | Permission: Contents -> Read and write" >&2
  echo "Then run:" >&2
  echo "  GH_TOKEN=github_pat_... bash scripts/push_with_token.sh" >&2
  exit 2
fi

# Defuse accidental whitespace/newlines from copy-paste.
GH_TOKEN="${GH_TOKEN//[[:space:]]/}"
# Keep the token as a shell variable during validation; do not export it to curl/Python.
export -n GH_TOKEN

# ---------------------------------------------------------------------------
# 1. Validate the token against the GitHub API (never prints the token).
# ---------------------------------------------------------------------------
check_token() {
  if command -v curl >/dev/null 2>&1; then
    {
      printf 'url = "https://api.github.com/repos/%s"\n' "${REPO_SLUG}"
      printf 'header = "Authorization: Bearer %s"\n' "${GH_TOKEN}"
      printf 'header = "X-GitHub-Api-Version: 2022-11-28"\n'
    } | curl --config - -s -o /dev/null -w '%{http_code}'
  else
    printf '%s\n%s\n' "${GH_TOKEN}" "${REPO_SLUG}" | python3 -c '
import sys, urllib.request, urllib.error
token, slug = sys.stdin.read().splitlines()
req = urllib.request.Request(
    f"https://api.github.com/repos/{slug}",
    headers={"Authorization": f"Bearer {token}",
             "X-GitHub-Api-Version": "2022-11-28",
             "User-Agent": "barrot-push-script"},
)
try:
    urllib.request.urlopen(req, timeout=15)
    print("200")
except urllib.error.HTTPError as e:
    print(e.code)
except Exception:
    print("000")
'
  fi
}

status="$(check_token)"
case "${status}" in
  200) echo "token OK for ${REPO_SLUG}" ;;
  401) echo "REJECTED: token invalid or expired (HTTP 401). Generate a new PAT." >&2; exit 3 ;;
  403|404) echo "REJECTED: token lacks access to ${REPO_SLUG} (HTTP ${status})." >&2
           echo "Grant: Repository access -> B-Agent, Permissions -> Contents: Read and write." >&2; exit 4 ;;
  *) echo "REJECTED: unexpected HTTP ${status} from api.github.com (offline?)." >&2; exit 5 ;;
esac

# ---------------------------------------------------------------------------
# 2. Show exactly what would be pushed.
# ---------------------------------------------------------------------------
echo
echo "Commits on ${BRANCH} not yet on origin:"
if git rev-parse --verify --quiet "origin/${BRANCH}" >/dev/null; then
  git log --oneline "origin/${BRANCH}..${BRANCH}" || true
  count="$(git rev-list --count "origin/${BRANCH}..${BRANCH}")"
  echo "=> ${count} commit(s) would be pushed."
else
  echo "(no origin/${BRANCH} ref locally; pushing will create/update it)"
fi

if [[ "${1:-}" == "--verify-only" || "${1:-}" == "--dry-run" ]]; then
  echo "verify-only: stopping before push."
  exit 0
fi

# ---------------------------------------------------------------------------
# 3. Push over HTTPS using a credential helper so the token never appears
#    in argv, remote URLs, or any file.
# ---------------------------------------------------------------------------
export GH_TOKEN
git -c credential.helper='!f() { echo "username=x-access-token"; echo "password=${GH_TOKEN}"; }; f' \
  push "https://github.com/${REPO_SLUG}.git" "${BRANCH}"

echo
echo "PUSH COMPLETE: ${REPO_SLUG}@${BRANCH}"
