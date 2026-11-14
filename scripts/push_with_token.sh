#!/usr/bin/env bash
# ============================================================================
# push_with_token.sh — the GH_TOKEN plug for Barrot-Agent pushes.
#
# House rules honored (BARROT_SYNC.md):
#   - No password auth, no SSH key requirement: fine-grained PAT over HTTPS
#     with username "x-access-token" only.
#   - The token is read from the GH_TOKEN env var, NEVER written to disk,
#     never echoed, never stored in .git/config or remote URLs. The git
#     credential helper below is passed via `git -c`, which does place it in
#     the short-lived git process argv (visible to same-user local processes
#     only); if that matters in your threat model, run this on a single-user
#     box. Alternatives (askpass scripts, credential store) all require
#     writing the token to disk, which this script refuses to do.
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
#   GH_TOKEN=... bash scripts/push_with_token.sh                # verify + push
#   GH_TOKEN=... bash scripts/push_with_token.sh --verify-only  # no push
#   BRANCH=main GH_TOKEN=... bash scripts/push_with_token.sh    # explicit branch
# ============================================================================
set -euo pipefail

REPO_SLUG="${REPO_SLUG:-Barrot-Agent/B-Agent}"
BRANCH="${BRANCH:-main}"

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

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

# ---------------------------------------------------------------------------
# 1. Validate the token against the GitHub API (never prints the token).
# ---------------------------------------------------------------------------
check_token() {
  if command -v curl >/dev/null 2>&1; then
    curl -s -o /dev/null -w '%{http_code}' \
      -H "Authorization: Bearer ${GH_TOKEN}" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      "https://api.github.com/repos/${REPO_SLUG}"
  else
    python3 - "$GH_TOKEN" "$REPO_SLUG" <<'PY'
import sys, urllib.request, urllib.error
token, slug = sys.argv[1], sys.argv[2]
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
PY
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
git -c credential.helper='!f() { echo "username=x-access-token"; echo "password=${GH_TOKEN}"; }; f' \
  push "https://github.com/${REPO_SLUG}.git" "${BRANCH}"

echo
echo "PUSH COMPLETE: ${REPO_SLUG}@${BRANCH}"
